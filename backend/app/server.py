"""
Main server application with FastAPI and Socket.IO
"""
import socketio
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
from typing import Optional
import logging

from app.config import settings
from app.database import init_db, get_db, AsyncSessionLocal
from app.models import User, Game, UserStats, Invitation, Session as DBSession
from app.auth import (
    hash_password,
    authenticate_user,
    create_access_token,
    get_current_user
)
from app.auth.session import SessionManager
from app.game import game_manager
from app.utils import setup_logging, log_event, validate_username, validate_password
from pydantic import BaseModel

# Setup logging
setup_logging(settings.LOG_FILE, settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Tic-Tac-Toe Multiplayer API",
    description="Network Multiplayer Tic-Tac-Toe Game - Capstone Project",
    version="1.0.0"
)

# Add CORS middleware - Must be added BEFORE routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',  # Allow all origins for development
    logger=settings.DEBUG,
    engineio_logger=settings.DEBUG
)

# Wrap with ASGI app
socket_app = socketio.ASGIApp(sio, app)

# Store active connections: user_id -> sid
active_connections = {}


# Pydantic models for API
class RegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str


# ===== FastAPI REST API Routes =====

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_db()
    logger.info("Server started successfully")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Tic-Tac-Toe Multiplayer API",
        "version": "1.0.0",
        "status": "online"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/register", response_model=LoginResponse)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user

    Args:
        request: Registration request
        db: Database session

    Returns:
        Access token and user info
    """
    # Validate input
    valid, error = validate_username(request.username)
    if not valid:
        raise HTTPException(status_code=400, detail=error)

    valid, error = validate_password(request.password)
    if not valid:
        raise HTTPException(status_code=400, detail=error)

    # Check if username already exists
    result = await db.execute(select(User).where(User.username == request.username))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already taken"
        )

    # Create new user
    hashed_password = hash_password(request.password)
    new_user = User(
        username=request.username,
        password_hash=hashed_password,
        email=request.email
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Create user stats
    user_stats = UserStats(user_id=new_user.id)
    db.add(user_stats)
    await db.commit()

    # Log event
    await log_event("INFO", "USER_REGISTER", f"New user registered: {request.username}", db, new_user.id)

    # Create access token
    access_token = create_access_token({"sub": str(new_user.id), "username": new_user.username})

    logger.info(f"User registered: {request.username} (ID: {new_user.id})")

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=new_user.id,
        username=new_user.username
    )


@app.post("/api/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Login user

    Args:
        request: Login request
        db: Database session

    Returns:
        Access token and user info
    """
    # Authenticate user
    user = await authenticate_user(request.username, request.password, db)

    if not user:
        await log_event("WARNING", "LOGIN_FAILED", f"Failed login attempt: {request.username}", db)
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )

    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()

    # Create access token
    access_token = create_access_token({"sub": str(user.id), "username": user.username})

    # Log event
    await log_event("INFO", "USER_LOGIN", f"User logged in: {request.username}", db, user.id)

    logger.info(f"User logged in: {request.username} (ID: {user.id})")

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        username=user.username
    )


@app.get("/api/users/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "is_online": current_user.is_online,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None
    }


@app.get("/api/stats/leaderboard")
async def get_leaderboard(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get top players leaderboard"""
    result = await db.execute(
        select(User, UserStats)
        .join(UserStats, User.id == UserStats.user_id)
        .order_by(UserStats.ranking_points.desc())
        .limit(limit)
    )

    leaderboard = []
    for user, stats in result:
        leaderboard.append({
            "rank": len(leaderboard) + 1,
            "username": user.username,
            "wins": stats.wins,
            "losses": stats.losses,
            "draws": stats.draws,
            "win_rate": round(stats.wins / stats.total_games * 100, 1) if stats.total_games > 0 else 0,
            "ranking_points": stats.ranking_points,
            "best_streak": stats.best_win_streak
        })

    return leaderboard


@app.get("/api/games/history")
async def get_game_history(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get game history for current user"""
    result = await db.execute(
        select(Game)
        .where(
            (Game.player1_id == current_user.id) | (Game.player2_id == current_user.id)
        )
        .where(Game.status == 'finished')
        .order_by(Game.finished_at.desc())
        .limit(limit)
    )

    games = result.scalars().all()
    history = []

    for game in games:
        # Get opponent info
        opponent_id = game.player2_id if game.player1_id == current_user.id else game.player1_id
        if opponent_id:
            opponent_result = await db.execute(select(User).where(User.id == opponent_id))
            opponent = opponent_result.scalar_one_or_none()
            opponent_name = opponent.username if opponent else "Bot"
        else:
            opponent_name = "Bot"

        # Determine result for current user
        if game.winner_id == current_user.id:
            user_result = "win"
        elif game.winner_id is None:
            user_result = "draw"
        else:
            user_result = "loss"

        history.append({
            "game_id": game.id,
            "opponent": opponent_name,
            "result": user_result,
            "is_bot_game": game.is_bot_game,
            "finished_at": game.finished_at.isoformat() if game.finished_at else None
        })

    return history


@app.get("/api/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get statistics for current user"""
    result = await db.execute(
        select(UserStats).where(UserStats.user_id == current_user.id)
    )
    stats = result.scalar_one_or_none()

    if not stats:
        return {
            "total_games": 0,
            "wins": 0,
            "losses": 0,
            "draws": 0,
            "win_rate": 0,
            "ranking_points": 1000
        }

    return {
        "total_games": stats.total_games,
        "wins": stats.wins,
        "losses": stats.losses,
        "draws": stats.draws,
        "win_rate": round(stats.wins / stats.total_games * 100, 1) if stats.total_games > 0 else 0,
        "ranking_points": stats.ranking_points,
        "current_streak": stats.win_streak,
        "best_streak": stats.best_win_streak
    }


# ===== Socket.IO Events =====

@sio.event
async def connect(sid, environ, auth=None):
    """Handle client connection"""
    logger.info(f"Client connected: {sid}")
    return True


@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {sid}")

    # Find user by sid and mark as offline
    user_id = None
    for uid, s in active_connections.items():
        if s == sid:
            user_id = int(uid)  # Convert back to int for database query
            break

    if user_id:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()

            if user:
                user.is_online = False
                user.socket_id = None
                await db.commit()

                # Broadcast updated online users
                await broadcast_online_users()

                await log_event("INFO", "USER_DISCONNECT", f"User disconnected: {user.username}", db, user_id)

        del active_connections[str(user_id)]


@sio.event
async def authenticate(sid, data):
    """
    Authenticate user via Socket.IO

    Args:
        sid: Socket ID
        data: {"token": "jwt_token"}
    """
    try:
        token = data.get('token')
        if not token:
            await sio.emit('error', {'message': 'Token required'}, room=sid)
            return

        # Verify token
        from app.auth import verify_token
        payload = verify_token(token)

        if not payload:
            await sio.emit('error', {'message': 'Invalid token'}, room=sid)
            return

        user_id = int(payload.get('sub'))

        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()

            if not user:
                await sio.emit('error', {'message': 'User not found'}, room=sid)
                return

            # Mark user as online
            user.is_online = True
            user.socket_id = sid
            await db.commit()

            # Store connection (use string keys for consistency)
            active_connections[str(user_id)] = sid

            # Send success
            await sio.emit('authenticated', {
                'user_id': user.id,
                'username': user.username
            }, room=sid)

            # Broadcast updated online users
            await broadcast_online_users()

            await log_event("INFO", "USER_CONNECT", f"User connected: {user.username}", db, user_id)

            logger.info(f"User authenticated: {user.username} (SID: {sid})")

    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        await sio.emit('error', {'message': 'Authentication failed'}, room=sid)


async def broadcast_online_users():
    """Broadcast list of online users to all connected clients"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(User.is_online == True)
        )
        online_users = result.scalars().all()

        users_data = [
            {
                'id': user.id,
                'username': user.username,
                'in_game': await game_manager.is_user_in_game(user.id)
            }
            for user in online_users
        ]

        await sio.emit('online_users', {'users': users_data})


# Register game events
from app.websocket.game_events import register_game_events
register_game_events(sio, active_connections)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        socket_app,
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower()
    )
