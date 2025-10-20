"""
Game module - handles game logic and management
"""
from .game_logic import TicTacToeLogic, GameResult
from .game_manager import GameManager, game_manager
from .bot_ai import BotAI

__all__ = [
    "TicTacToeLogic",
    "GameResult",
    "GameManager",
    "game_manager",
    "BotAI"
]
