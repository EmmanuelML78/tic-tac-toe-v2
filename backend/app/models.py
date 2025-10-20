"""
Database models for the application
"""
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    is_admin = Column(Boolean, default=False)
    is_online = Column(Boolean, default=False)
    socket_id = Column(String(100))

    # Relationships
    stats = relationship("UserStats", back_populates="user", uselist=False)
    games_as_player1 = relationship("Game", foreign_keys="Game.player1_id", back_populates="player1")
    games_as_player2 = relationship("Game", foreign_keys="Game.player2_id", back_populates="player2")
    moves = relationship("Move", back_populates="player")
    sent_invitations = relationship("Invitation", foreign_keys="Invitation.from_user_id", back_populates="from_user")
    received_invitations = relationship("Invitation", foreign_keys="Invitation.to_user_id", back_populates="to_user")
    chat_messages = relationship("ChatMessage", back_populates="user")
    sessions = relationship("Session", back_populates="user")
    logs = relationship("ServerLog", back_populates="user")


class Game(Base):
    """Game model"""
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    player1_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    player2_id = Column(Integer, ForeignKey("users.id"))
    is_bot_game = Column(Boolean, default=False)
    bot_difficulty = Column(String(20))  # 'easy', 'medium', 'hard'
    winner_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String(20), nullable=False, default="waiting", index=True)  # 'waiting', 'active', 'finished', 'abandoned'
    board_state = Column(String(9), default="---------")
    current_turn = Column(Integer, ForeignKey("users.id"))
    player1_symbol = Column(String(1), default="X")
    player2_symbol = Column(String(1), default="O")
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
    abandon_by = Column(Integer, ForeignKey("users.id"))
    result = Column(String(20))  # 'win', 'draw', 'abandoned'

    # Relationships
    player1 = relationship("User", foreign_keys=[player1_id], back_populates="games_as_player1")
    player2 = relationship("User", foreign_keys=[player2_id], back_populates="games_as_player2")
    moves = relationship("Move", back_populates="game", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="game", cascade="all, delete-orphan")


class Move(Base):
    """Move model - stores each move for replay functionality"""
    __tablename__ = "moves"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False, index=True)
    player_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    position = Column(Integer, nullable=False)  # 0-8
    symbol = Column(String(1), nullable=False)  # 'X' or 'O'
    board_state_after = Column(String(9), nullable=False)
    move_number = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    game = relationship("Game", back_populates="moves")
    player = relationship("User", back_populates="moves")


class UserStats(Base):
    """User statistics model"""
    __tablename__ = "user_stats"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    total_games = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    draws = Column(Integer, default=0)
    games_abandoned = Column(Integer, default=0)
    games_vs_bot = Column(Integer, default=0)
    win_streak = Column(Integer, default=0)
    best_win_streak = Column(Integer, default=0)
    ranking_points = Column(Integer, default=1000)  # ELO system

    # Relationships
    user = relationship("User", back_populates="stats")


class Invitation(Base):
    """Game invitation model"""
    __tablename__ = "invitations"

    id = Column(Integer, primary_key=True, index=True)
    from_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    to_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    status = Column(String(20), default="pending", index=True)  # 'pending', 'accepted', 'rejected', 'expired'
    created_at = Column(DateTime, default=datetime.utcnow)
    responded_at = Column(DateTime)

    # Relationships
    from_user = relationship("User", foreign_keys=[from_user_id], back_populates="sent_invitations")
    to_user = relationship("User", foreign_keys=[to_user_id], back_populates="received_invitations")


class ChatMessage(Base):
    """Chat message model"""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    game = relationship("Game", back_populates="chat_messages")
    user = relationship("User", back_populates="chat_messages")


class ServerLog(Base):
    """Server log model"""
    __tablename__ = "server_logs"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(10), nullable=False)  # 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    event_type = Column(String(50), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    game_id = Column(Integer, ForeignKey("games.id"))
    message = Column(Text, nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="logs")


class Session(Base):
    """Session model for reconnection"""
    __tablename__ = "sessions"

    id = Column(String(100), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token = Column(String(255), nullable=False, index=True)
    socket_id = Column(String(100))
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="sessions")


class ServerMetric(Base):
    """Server metrics for dashboard"""
    __tablename__ = "server_metrics"

    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(50), nullable=False)
    metric_value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


# Create indexes for better performance
Index('idx_games_status', Game.status)
Index('idx_games_player1', Game.player1_id)
Index('idx_games_player2', Game.player2_id)
Index('idx_moves_game', Move.game_id)
Index('idx_invitations_status', Invitation.status)
Index('idx_invitations_to_user', Invitation.to_user_id)
Index('idx_sessions_user', Session.user_id)
Index('idx_sessions_token', Session.token)
Index('idx_logs_timestamp', ServerLog.timestamp)
Index('idx_logs_event_type', ServerLog.event_type)
