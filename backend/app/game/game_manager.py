"""
Game Manager - Event-bus pattern for managing multiple games
"""
from typing import Dict, Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import asyncio
import logging

from app.models import Game, User, Move, UserStats, Invitation
from .game_logic import TicTacToeLogic, GameResult
from .bot_ai import BotAI

logger = logging.getLogger(__name__)


class GameManager:
    """
    Manages all active games using event-bus pattern
    Handles game creation, moves, and state synchronization
    """

    def __init__(self):
        """Initialize Game Manager"""
        self.active_games: Dict[int, Dict] = {}  # game_id -> game_data
        self.user_to_game: Dict[int, int] = {}  # user_id -> game_id
        self._lock = asyncio.Lock()

    async def create_game(
        self,
        player1_id: int,
        player2_id: Optional[int],
        is_bot_game: bool,
        bot_difficulty: Optional[str],
        db: AsyncSession
    ) -> Game:
        """
        Create a new game

        Args:
            player1_id: First player ID
            player2_id: Second player ID (None for bot)
            is_bot_game: True if playing against bot
            bot_difficulty: Bot difficulty if applicable
            db: Database session

        Returns:
            Created game object
        """
        async with self._lock:
            # Create game in database
            game = Game(
                player1_id=player1_id,
                player2_id=player2_id,
                is_bot_game=is_bot_game,
                bot_difficulty=bot_difficulty,
                status='active',
                board_state=TicTacToeLogic.create_empty_board(),
                current_turn=player1_id,
                started_at=datetime.utcnow()
            )

            db.add(game)
            await db.commit()
            await db.refresh(game)

            # Add to active games
            self.active_games[game.id] = {
                'game': game,
                'player1_id': player1_id,
                'player2_id': player2_id if player2_id else 0,  # Use 0 for bot
                'is_bot_game': is_bot_game,
                'bot_difficulty': bot_difficulty,
                'board': game.board_state,
                'current_turn': player1_id,
                'move_count': 0,
                'bot_ai': BotAI(bot_difficulty, 'O') if is_bot_game else None
            }

            # Track which users are in which games
            self.user_to_game[player1_id] = game.id
            if player2_id:
                self.user_to_game[player2_id] = game.id

            logger.info(f"Game {game.id} created: player1={player1_id}, player2={player2_id}, bot={is_bot_game}")

            return game

    async def make_move(
        self,
        game_id: int,
        player_id: int,
        position: int,
        db: AsyncSession
    ) -> Dict:
        """
        Process a player move

        Args:
            game_id: Game ID
            player_id: Player making the move
            position: Position to play (0-8)
            db: Database session

        Returns:
            Dictionary with move result
        """
        async with self._lock:
            if game_id not in self.active_games:
                raise ValueError("Game not found")

            game_data = self.active_games[game_id]

            # Validate it's player's turn
            logger.info(f"make_move validation: game_id={game_id}, player_id={player_id}, current_turn={game_data['current_turn']}")
            if game_data['current_turn'] != player_id:
                logger.error(f"Turn validation failed: current_turn={game_data['current_turn']}, player_id={player_id}")
                raise ValueError("Not your turn")

            # Validate move
            board = game_data['board']
            if not TicTacToeLogic.is_valid_move(board, position):
                raise ValueError("Invalid move")

            # Determine player symbol
            symbol = 'X' if player_id == game_data['player1_id'] else 'O'

            # Make the move
            new_board = TicTacToeLogic.make_move(board, position, symbol)
            game_data['board'] = new_board
            game_data['move_count'] += 1

            # Save move to database
            move = Move(
                game_id=game_id,
                player_id=player_id,
                position=position,
                symbol=symbol,
                board_state_after=new_board,
                move_number=game_data['move_count']
            )
            db.add(move)

            # Check game result
            result = TicTacToeLogic.get_game_result(new_board)
            winner_id = None
            game_over = False

            if result == GameResult.WIN:
                winner_id = player_id
                game_over = True
                await self._end_game(game_id, winner_id, 'win', db)
            elif result == GameResult.DRAW:
                game_over = True
                await self._end_game(game_id, None, 'draw', db)
            else:
                # Switch turn
                game_data['current_turn'] = (
                    game_data['player2_id']
                    if player_id == game_data['player1_id']
                    else game_data['player1_id']
                )

            # Update game in database
            await db.execute(
                update(Game)
                .where(Game.id == game_id)
                .values(
                    board_state=new_board,
                    current_turn=game_data['current_turn']
                )
            )

            await db.commit()

            logger.info(f"Move made in game {game_id}: player={player_id}, pos={position}")

            return {
                'success': True,
                'board': new_board,
                'current_turn': game_data['current_turn'],
                'game_over': game_over,
                'result': result.value if game_over else None,
                'winner_id': winner_id,
                'winning_line': TicTacToeLogic.get_winning_line(new_board) if game_over and result == GameResult.WIN else None
            }

    async def make_bot_move(self, game_id: int, db: AsyncSession) -> Dict:
        """
        Make a bot move

        Args:
            game_id: Game ID
            db: Database session

        Returns:
            Dictionary with bot move result
        """
        # Get game data without lock first
        if game_id not in self.active_games:
            raise ValueError("Game not found")

        game_data = self.active_games[game_id]
        
        logger.info(f"Bot game data: player1_id={game_data['player1_id']}, player2_id={game_data['player2_id']}, current_turn={game_data['current_turn']}")

        if not game_data['is_bot_game']:
            raise ValueError("Not a bot game")

        if not game_data['bot_ai']:
            raise ValueError("Bot AI not initialized")

        # Get bot's best move
        board = game_data['board']
        position = game_data['bot_ai'].get_best_move(board)
        logger.info(f"Bot selected position: {position}")

        # Bot is always player 2 (we use ID 0 for bot)
        bot_player_id = game_data['player2_id']
        logger.info(f"Bot player ID: {bot_player_id}, attempting move at position {position}")
        
        # Call make_move which has its own lock
        result = await self.make_move(game_id, bot_player_id, position, db)
        logger.info(f"Bot move result: {result}")
        
        # Add the position to the result
        result['position'] = position

        logger.info(f"Bot move in game {game_id}: pos={position}")

        return result

    async def forfeit_game(
        self,
        game_id: int,
        player_id: int,
        db: AsyncSession
    ) -> Dict:
        """
        Player forfeits the game

        Args:
            game_id: Game ID
            player_id: Player who is forfeiting
            db: Database session

        Returns:
            Dictionary with forfeit result
        """
        async with self._lock:
            if game_id not in self.active_games:
                raise ValueError("Game not found")

            game_data = self.active_games[game_id]

            # Determine winner (opponent)
            if player_id == game_data['player1_id']:
                winner_id = game_data['player2_id']
            else:
                winner_id = game_data['player1_id']

            await self._end_game(game_id, winner_id, 'abandoned', db, abandon_by=player_id)

            logger.info(f"Game {game_id} forfeited by player {player_id}")

            return {
                'success': True,
                'winner_id': winner_id,
                'result': 'abandoned'
            }

    async def _end_game(
        self,
        game_id: int,
        winner_id: Optional[int],
        result: str,
        db: AsyncSession,
        abandon_by: Optional[int] = None
    ) -> None:
        """
        End a game and update statistics

        Args:
            game_id: Game ID
            winner_id: Winner ID (None for draw)
            result: Game result ('win', 'draw', 'abandoned')
            db: Database session
            abandon_by: Player who abandoned (if applicable)
        """
        if game_id not in self.active_games:
            return

        game_data = self.active_games[game_id]

        # Update game in database
        await db.execute(
            update(Game)
            .where(Game.id == game_id)
            .values(
                status='finished',
                winner_id=winner_id,
                result=result,
                finished_at=datetime.utcnow(),
                abandon_by=abandon_by
            )
        )

        # Update player statistics
        player1_id = game_data['player1_id']
        player2_id = game_data['player2_id']

        if player2_id:  # Not a bot game or bot has ID
            await self._update_player_stats(player1_id, player2_id, winner_id, result, db)

        await db.commit()

        # Remove from active games
        del self.active_games[game_id]
        if player1_id in self.user_to_game:
            del self.user_to_game[player1_id]
        if player2_id and player2_id in self.user_to_game:
            del self.user_to_game[player2_id]

        logger.info(f"Game {game_id} ended: winner={winner_id}, result={result}")

    async def _update_player_stats(
        self,
        player1_id: int,
        player2_id: int,
        winner_id: Optional[int],
        result: str,
        db: AsyncSession
    ) -> None:
        """
        Update statistics for both players

        Args:
            player1_id: Player 1 ID
            player2_id: Player 2 ID
            winner_id: Winner ID (None for draw)
            result: Game result
            db: Database session
        """
        # Get or create stats for both players
        for player_id in [player1_id, player2_id]:
            result_obj = await db.execute(
                select(UserStats).where(UserStats.user_id == player_id)
            )
            stats = result_obj.scalar_one_or_none()

            if not stats:
                stats = UserStats(user_id=player_id)
                db.add(stats)
                await db.flush()

            # Update stats
            stats.total_games += 1

            if result == 'draw':
                stats.draws += 1
                stats.win_streak = 0
            elif result == 'abandoned':
                if player_id == winner_id:
                    stats.wins += 1
                    stats.win_streak += 1
                    stats.best_win_streak = max(stats.best_win_streak, stats.win_streak)
                else:
                    stats.games_abandoned += 1
                    stats.win_streak = 0
            else:  # win
                if player_id == winner_id:
                    stats.wins += 1
                    stats.win_streak += 1
                    stats.best_win_streak = max(stats.best_win_streak, stats.win_streak)
                    stats.ranking_points += 25
                else:
                    stats.losses += 1
                    stats.win_streak = 0
                    stats.ranking_points = max(0, stats.ranking_points - 15)

    async def get_game_state(self, game_id: int) -> Optional[Dict]:
        """
        Get current game state

        Args:
            game_id: Game ID

        Returns:
            Game state dictionary or None
        """
        if game_id not in self.active_games:
            return None

        game_data = self.active_games[game_id]
        return {
            'game_id': game_id,
            'board': game_data['board'],
            'current_turn': game_data['current_turn'],
            'player1_id': game_data['player1_id'],
            'player2_id': game_data['player2_id'],
            'is_bot_game': game_data['is_bot_game'],
            'move_count': game_data['move_count']
        }

    async def get_user_active_game(self, user_id: int) -> Optional[int]:
        """
        Get active game ID for a user

        Args:
            user_id: User ID

        Returns:
            Game ID or None
        """
        return self.user_to_game.get(user_id)

    async def is_user_in_game(self, user_id: int) -> bool:
        """
        Check if user is currently in a game

        Args:
            user_id: User ID

        Returns:
            True if user is in an active game
        """
        return user_id in self.user_to_game

    def get_active_game_count(self) -> int:
        """Get number of active games"""
        return len(self.active_games)

    def get_all_active_games(self) -> List[Dict]:
        """Get all active games data"""
        return [
            {
                'game_id': game_id,
                'player1_id': data['player1_id'],
                'player2_id': data['player2_id'],
                'is_bot_game': data['is_bot_game'],
                'move_count': data['move_count']
            }
            for game_id, data in self.active_games.items()
        ]


# Global game manager instance
game_manager = GameManager()
