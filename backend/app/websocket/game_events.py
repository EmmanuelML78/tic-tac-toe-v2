"""
Socket.IO game events
This file contains all game-related Socket.IO event handlers
"""
import socketio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict
import logging

from app.models import User, Game, Invitation
from app.game import game_manager
from app.database import AsyncSessionLocal
from app.utils import log_event, validate_move

logger = logging.getLogger(__name__)


def register_game_events(sio: socketio.AsyncServer, active_connections: Dict[int, str]):
    """
    Register all game-related Socket.IO events

    Args:
        sio: Socket.IO server instance
        active_connections: Dictionary of active user connections
    """

    @sio.event
    async def join_game(sid, data):
        """
        Join a game room (used when reconnecting to game page)

        Args:
            sid: Socket ID
            data: {"game_id": int}
        """
        try:
            # Get user
            user_id = None
            for uid, socket_id in active_connections.items():
                if socket_id == sid:
                    user_id = int(uid)
                    break

            if not user_id:
                await sio.emit('error', {'message': 'Not authenticated'}, room=sid)
                return

            game_id = data.get('game_id')
            if not game_id:
                await sio.emit('error', {'message': 'Game ID required'}, room=sid)
                return

            # Try to get game from active games first
            game_state = await game_manager.get_game_state(game_id)
            
            # If not in active games, try to load from database
            if not game_state:
                async with AsyncSessionLocal() as db:
                    result = await db.execute(select(Game).where(Game.id == game_id))
                    game = result.scalar_one_or_none()
                    
                    if not game:
                        await sio.emit('error', {'message': 'Game not found'}, room=sid)
                        return
                    
                    # Verify user is part of this game
                    if game.player1_id != user_id and game.player2_id != user_id:
                        await sio.emit('error', {'message': 'Not a player in this game'}, room=sid)
                        return
                    
                    # Check if game is finished
                    if game.status == 'finished':
                        await sio.emit('error', {'message': 'Game already finished'}, room=sid)
                        return
                    
                    # Re-add game to active games if it's still active
                    if game.status == 'active':
                        logger.info(f"Re-loading game {game_id} into active games")
                        # Recreate game state in memory
                        game_state = {
                            'game_id': game_id,
                            'board': game.board_state,
                            'current_turn': game.current_turn,
                            'player1_id': game.player1_id,
                            'player2_id': game.player2_id,
                            'is_bot_game': game.is_bot_game,
                            'move_count': len([c for c in game.board_state if c != '-'])
                        }
                        
                        # Add back to active games
                        from app.game.bot_ai import BotAI
                        game_manager.active_games[game_id] = {
                            'game': game,
                            'player1_id': game.player1_id,
                            'player2_id': game.player2_id,
                            'is_bot_game': game.is_bot_game,
                            'bot_difficulty': game.bot_difficulty,
                            'board': game.board_state,
                            'current_turn': game.current_turn,
                            'move_count': game_state['move_count'],
                            'bot_ai': BotAI(game.bot_difficulty, 'O') if game.is_bot_game else None
                        }
                        
                        # Track users
                        game_manager.user_to_game[game.player1_id] = game_id
                        if game.player2_id:
                            game_manager.user_to_game[game.player2_id] = game_id
            else:
                # Game is in active games, verify user is part of it
                if game_state['player1_id'] != user_id and game_state['player2_id'] != user_id:
                    await sio.emit('error', {'message': 'Not a player in this game'}, room=sid)
                    return

            # Join game room
            game_room = f"game_{game_id}"
            await sio.enter_room(sid, game_room)

            logger.info(f"User {user_id} joined game room {game_room}")

            # Acknowledge successful join
            await sio.emit('game_joined', {'game_id': game_id}, room=sid)

        except Exception as e:
            logger.error(f"Error in join_game: {str(e)}")
            await sio.emit('error', {'message': 'Failed to join game'}, room=sid)

    @sio.event
    async def invite_player(sid, data):
        """
        Send game invitation to another player

        Args:
            sid: Socket ID
            data: {"target_user_id": int}
        """
        try:
            # Get sender user
            sender_id = None
            for user_id, socket_id in active_connections.items():
                if socket_id == sid:
                    sender_id = int(user_id)  # Convert to int immediately
                    break

            if not sender_id:
                await sio.emit('error', {'message': 'Not authenticated'}, room=sid)
                return

            target_user_id = data.get('target_user_id')
            if not target_user_id:
                await sio.emit('error', {'message': 'Target user ID required'}, room=sid)
                return

            async with AsyncSessionLocal() as db:
                # Check if both users exist and are online
                sender_result = await db.execute(select(User).where(User.id == sender_id))
                sender = sender_result.scalar_one_or_none()

                target_result = await db.execute(select(User).where(User.id == target_user_id))
                target = target_result.scalar_one_or_none()

                if not sender or not target:
                    await sio.emit('error', {'message': 'User not found'}, room=sid)
                    return

                if not target.is_online:
                    await sio.emit('error', {'message': 'User is offline'}, room=sid)
                    return

                # Check if target is already in a game
                if await game_manager.is_user_in_game(target_user_id):
                    await sio.emit('error', {'message': 'User is already in a game'}, room=sid)
                    return

                # Create invitation
                invitation = Invitation(
                    from_user_id=sender_id,
                    to_user_id=target_user_id,
                    status='pending'
                )
                db.add(invitation)
                await db.commit()
                await db.refresh(invitation)

                # Send invitation to target user
                # Note: active_connections uses string keys (from JWT)
                target_sid = active_connections.get(str(target_user_id))
                logger.info(f"Target user {target_user_id} has sid: {target_sid}, active_connections keys: {list(active_connections.keys())}")
                if target_sid:
                    logger.info(f"Emitting invitation_received to {target_sid}")
                    await sio.emit('invitation_received', {
                        'invitation_id': invitation.id,
                        'from_user_id': sender_id,
                        'from_username': sender.username
                    }, room=target_sid)
                else:
                    logger.warning(f"Target user {target_user_id} not found in active_connections!")

                # Confirm to sender
                await sio.emit('invitation_sent', {
                    'invitation_id': invitation.id,
                    'to_username': target.username
                }, room=sid)

                await log_event("INFO", "INVITATION_SENT",
                               f"{sender.username} invited {target.username}", db, sender_id)

                logger.info(f"Invitation sent from {sender.username} to {target.username}")

        except Exception as e:
            logger.error(f"Error in invite_player: {str(e)}")
            await sio.emit('error', {'message': 'Failed to send invitation'}, room=sid)

    @sio.event
    async def accept_invitation(sid, data):
        """
        Accept a game invitation

        Args:
            sid: Socket ID
            data: {"invitation_id": int}
        """
        try:
            logger.info(f"🎯 accept_invitation called - sid: {sid}, data: {data}")

            # Get user
            user_id = None
            for uid, socket_id in active_connections.items():
                if socket_id == sid:
                    user_id = int(uid)  # Convert to int immediately
                    break

            logger.info(f"🔍 User lookup - user_id: {user_id}, active_connections: {list(active_connections.keys())}")

            if not user_id:
                logger.error(f"❌ User not found in active_connections for sid: {sid}")
                await sio.emit('error', {'message': 'Not authenticated'}, room=sid)
                return

            invitation_id = data.get('invitation_id')
            logger.info(f"📨 Invitation ID from data: {invitation_id} (type: {type(invitation_id)})")
            
            if not invitation_id:
                logger.error(f"❌ No invitation_id in data")
                await sio.emit('error', {'message': 'Invitation ID required'}, room=sid)
                return

            async with AsyncSessionLocal() as db:
                # Get invitation
                result = await db.execute(
                    select(Invitation).where(Invitation.id == invitation_id)
                )
                invitation = result.scalar_one_or_none()

                logger.info(f"📋 Invitation found: {invitation}")
                if invitation:
                    logger.info(f"📋 Invitation details - ID: {invitation.id}, from: {invitation.from_user_id}, to: {invitation.to_user_id}, status: {invitation.status}")
                    logger.info(f"🔍 Checking: invitation.to_user_id ({invitation.to_user_id}) == user_id ({user_id}): {invitation.to_user_id == user_id}")

                if not invitation or invitation.to_user_id != user_id:
                    logger.error(f"❌ Invitation not found or not for this user - invitation: {invitation}, user_id: {user_id}")
                    await sio.emit('error', {'message': 'Invitation not found'}, room=sid)
                    return

                if invitation.status != 'pending':
                    await sio.emit('error', {'message': 'Invitation already responded'}, room=sid)
                    return

                # Create game
                game = await game_manager.create_game(
                    player1_id=invitation.from_user_id,
                    player2_id=invitation.to_user_id,
                    is_bot_game=False,
                    bot_difficulty=None,
                    db=db
                )

                # Update invitation
                invitation.status = 'accepted'
                invitation.game_id = game.id
                await db.commit()

                # Get usernames
                player1_result = await db.execute(select(User).where(User.id == invitation.from_user_id))
                player1 = player1_result.scalar_one()

                player2_result = await db.execute(select(User).where(User.id == invitation.to_user_id))
                player2 = player2_result.scalar_one()

                # Notify both players
                game_data = {
                    'game_id': game.id,
                    'player1': {'id': player1.id, 'username': player1.username, 'symbol': 'X'},
                    'player2': {'id': player2.id, 'username': player2.username, 'symbol': 'O'},
                    'board': game.board_state,
                    'current_turn': game.current_turn
                }

                player1_sid = active_connections.get(str(invitation.from_user_id))
                player2_sid = active_connections.get(str(invitation.to_user_id))

                # Join both players to game room for better synchronization
                game_room = f"game_{game.id}"
                if player1_sid:
                    await sio.enter_room(player1_sid, game_room)
                    await sio.emit('game_started', game_data, room=player1_sid)

                if player2_sid:
                    await sio.enter_room(player2_sid, game_room)
                    await sio.emit('game_started', game_data, room=player2_sid)

                await log_event("INFO", "GAME_START",
                               f"Game started: {player1.username} vs {player2.username}",
                               db, game_id=game.id)

                logger.info(f"Game {game.id} started: {player1.username} vs {player2.username}")

        except Exception as e:
            logger.error(f"Error in accept_invitation: {str(e)}")
            await sio.emit('error', {'message': 'Failed to accept invitation'}, room=sid)

    @sio.event
    async def reject_invitation(sid, data):
        """
        Reject a game invitation

        Args:
            sid: Socket ID
            data: {"invitation_id": int}
        """
        try:
            user_id = None
            for uid, socket_id in active_connections.items():
                if socket_id == sid:
                    user_id = int(uid)  # Convert to int immediately
                    break

            if not user_id:
                await sio.emit('error', {'message': 'Not authenticated'}, room=sid)
                return

            invitation_id = data.get('invitation_id')

            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(Invitation).where(Invitation.id == invitation_id)
                )
                invitation = result.scalar_one_or_none()

                if not invitation or invitation.to_user_id != user_id:
                    await sio.emit('error', {'message': 'Invitation not found'}, room=sid)
                    return

                invitation.status = 'rejected'
                await db.commit()

                # Notify sender
                sender_sid = active_connections.get(str(invitation.from_user_id))
                if sender_sid:
                    await sio.emit('invitation_rejected', {
                        'invitation_id': invitation.id
                    }, room=sender_sid)

                logger.info(f"Invitation {invitation.id} rejected")

        except Exception as e:
            logger.error(f"Error in reject_invitation: {str(e)}")
            await sio.emit('error', {'message': 'Failed to reject invitation'}, room=sid)

    @sio.event
    async def make_move(sid, data):
        """
        Make a move in the game

        Args:
            sid: Socket ID
            data: {"game_id": int, "position": int}
        """
        try:
            # Get user
            user_id = None
            for uid, socket_id in active_connections.items():
                if socket_id == sid:
                    user_id = int(uid)  # Convert to int immediately
                    break

            if not user_id:
                await sio.emit('error', {'message': 'Not authenticated'}, room=sid)
                return

            game_id = data.get('game_id')
            position = data.get('position')

            # Validate position
            valid, error = validate_move(position)
            if not valid:
                await sio.emit('error', {'message': error}, room=sid)
                return

            async with AsyncSessionLocal() as db:
                # Get game info BEFORE making the move (important!)
                game_state = await game_manager.get_game_state(game_id)
                if not game_state:
                    await sio.emit('error', {'message': 'Game not found'}, room=sid)
                    return

                # Make the move
                result = await game_manager.make_move(game_id, user_id, position, db)

                # Broadcast move to both players
                move_data = {
                    'game_id': game_id,
                    'position': position,
                    'player_id': user_id,
                    'board': result['board'],
                    'current_turn': result['current_turn'],
                    'game_over': result['game_over']
                }

                if result['game_over']:
                    move_data['result'] = result['result']
                    move_data['winner_id'] = result['winner_id']
                    move_data['winning_line'] = result['winning_line']

                # Broadcast move to all players in game room
                game_room = f"game_{game_id}"
                logger.info(f"Broadcasting move_made to room {game_room}: game_over={result['game_over']}, result={result.get('result')}")
                await sio.emit('move_made', move_data, room=game_room)

                # If it's a bot game and game is not over, make bot move
                if game_state['is_bot_game'] and not result['game_over']:
                    # Small delay for better UX
                    import asyncio
                    await asyncio.sleep(0.5)

                    bot_result = await game_manager.make_bot_move(game_id, db)

                    bot_move_data = {
                        'game_id': game_id,
                        'position': bot_result.get('position'),
                        'player_id': game_state['player2_id'],
                        'board': bot_result['board'],
                        'current_turn': bot_result['current_turn'],
                        'game_over': bot_result['game_over']
                    }

                    if bot_result['game_over']:
                        bot_move_data['result'] = bot_result['result']
                        bot_move_data['winner_id'] = bot_result['winner_id']
                        bot_move_data['winning_line'] = bot_result['winning_line']

                    # Broadcast bot move to game room
                    await sio.emit('move_made', bot_move_data, room=game_room)

                if result['game_over']:
                    await log_event("INFO", "GAME_END",
                                   f"Game {game_id} ended: {result['result']}",
                                   db, game_id=game_id)

        except ValueError as e:
            await sio.emit('error', {'message': str(e)}, room=sid)
        except Exception as e:
            logger.error(f"Error in make_move: {str(e)}")
            await sio.emit('error', {'message': 'Failed to make move'}, room=sid)

    @sio.event
    async def forfeit_game(sid, data):
        """
        Forfeit the current game

        Args:
            sid: Socket ID
            data: {"game_id": int}
        """
        try:
            user_id = None
            for uid, socket_id in active_connections.items():
                if socket_id == sid:
                    user_id = int(uid)  # Convert to int immediately
                    break

            if not user_id:
                await sio.emit('error', {'message': 'Not authenticated'}, room=sid)
                return

            game_id = data.get('game_id')

            async with AsyncSessionLocal() as db:
                result = await game_manager.forfeit_game(game_id, user_id, db)

                game_state = await game_manager.get_game_state(game_id)
                if game_state:
                    forfeit_data = {
                        'game_id': game_id,
                        'forfeited_by': user_id,
                        'winner_id': result['winner_id'],
                        'result': 'abandoned'
                    }

                    # Broadcast forfeit to game room
                    game_room = f"game_{game_id}"
                    await sio.emit('game_forfeited', forfeit_data, room=game_room)

                await log_event("INFO", "GAME_FORFEIT",
                               f"Game {game_id} forfeited by user {user_id}",
                               db, user_id, game_id)

                logger.info(f"Game {game_id} forfeited by user {user_id}")

        except Exception as e:
            logger.error(f"Error in forfeit_game: {str(e)}")
            await sio.emit('error', {'message': 'Failed to forfeit game'}, room=sid)

    @sio.event
    async def play_vs_bot(sid, data):
        """
        Start a game against bot

        Args:
            sid: Socket ID
            data: {"difficulty": "easy" | "medium" | "hard"}
        """
        try:
            user_id = None
            for uid, socket_id in active_connections.items():
                if socket_id == sid:
                    user_id = int(uid)  # Convert to int immediately
                    break

            if not user_id:
                await sio.emit('error', {'message': 'Not authenticated'}, room=sid)
                return

            difficulty = data.get('difficulty', 'medium')
            if difficulty not in ['easy', 'medium', 'hard']:
                difficulty = 'medium'

            async with AsyncSessionLocal() as db:
                # Check if user already in game
                if await game_manager.is_user_in_game(user_id):
                    await sio.emit('error', {'message': 'Already in a game'}, room=sid)
                    return

                # Create bot game
                game = await game_manager.create_game(
                    player1_id=user_id,
                    player2_id=None,
                    is_bot_game=True,
                    bot_difficulty=difficulty,
                    db=db
                )

                # Get user
                user_result = await db.execute(select(User).where(User.id == user_id))
                user = user_result.scalar_one()

                # Notify player
                game_data = {
                    'game_id': game.id,
                    'player1': {'id': user.id, 'username': user.username, 'symbol': 'X'},
                    'player2': {'id': None, 'username': f'Bot ({difficulty})', 'symbol': 'O'},
                    'board': game.board_state,
                    'current_turn': game.current_turn,
                    'is_bot_game': True,
                    'bot_difficulty': difficulty
                }

                # Join player to game room
                game_room = f"game_{game.id}"
                await sio.enter_room(sid, game_room)

                logger.info(f"Emitting game_started to {sid} for bot game {game.id}")
                await sio.emit('game_started', game_data, room=sid)

                await log_event("INFO", "GAME_START",
                               f"Bot game started: {user.username} vs Bot ({difficulty})",
                               db, user_id, game.id)

                logger.info(f"Bot game {game.id} started: {user.username} vs Bot ({difficulty})")

        except Exception as e:
            logger.error(f"Error in play_vs_bot: {str(e)}")
            await sio.emit('error', {'message': 'Failed to start bot game'}, room=sid)

    return sio
