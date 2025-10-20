"""
Bot AI implementation using Minimax algorithm
"""
import random
from typing import Optional, Tuple
from .game_logic import TicTacToeLogic


class BotAI:
    """
    AI Bot for playing Tic-Tac-Toe
    Implements Minimax algorithm with different difficulty levels
    """

    def __init__(self, difficulty: str = 'medium', symbol: str = 'O'):
        """
        Initialize Bot AI

        Args:
            difficulty: Difficulty level ('easy', 'medium', 'hard')
            symbol: Bot's symbol ('X' or 'O')
        """
        self.difficulty = difficulty.lower()
        self.symbol = symbol
        self.opponent_symbol = TicTacToeLogic.get_opponent_symbol(symbol)

    def get_best_move(self, board: str) -> int:
        """
        Get the best move for the bot based on difficulty

        Args:
            board: Current board state

        Returns:
            Position to play (0-8)
        """
        if self.difficulty == 'easy':
            return self._get_easy_move(board)
        elif self.difficulty == 'medium':
            return self._get_medium_move(board)
        else:  # hard
            return self._get_hard_move(board)

    def _get_easy_move(self, board: str) -> int:
        """
        Easy difficulty: Random valid move

        Args:
            board: Current board state

        Returns:
            Random valid position
        """
        available_moves = TicTacToeLogic.get_available_moves(board)
        return random.choice(available_moves)

    def _get_medium_move(self, board: str) -> int:
        """
        Medium difficulty: Minimax with limited depth (3)
        50% chance to make a random move for unpredictability

        Args:
            board: Current board state

        Returns:
            Best position found
        """
        # 50% chance to make a random move
        if random.random() < 0.5:
            return self._get_easy_move(board)

        # Otherwise use minimax with depth 3
        _, move = self._minimax(board, depth=0, max_depth=3, is_maximizing=True)
        return move if move is not None else self._get_easy_move(board)

    def _get_hard_move(self, board: str) -> int:
        """
        Hard difficulty: Full Minimax with alpha-beta pruning
        Unbeatable AI

        Args:
            board: Current board state

        Returns:
            Optimal position
        """
        _, move = self._minimax_alpha_beta(
            board,
            depth=0,
            alpha=float('-inf'),
            beta=float('inf'),
            is_maximizing=True
        )
        return move if move is not None else self._get_easy_move(board)

    def _minimax(
        self,
        board: str,
        depth: int,
        max_depth: int,
        is_maximizing: bool
    ) -> Tuple[int, Optional[int]]:
        """
        Minimax algorithm with depth limit

        Args:
            board: Current board state
            depth: Current depth in the game tree
            max_depth: Maximum depth to search
            is_maximizing: True if maximizing player, False if minimizing

        Returns:
            Tuple of (score, best_move)
        """
        # Check terminal states
        winner = TicTacToeLogic.check_winner(board)
        if winner == self.symbol:
            return (10 - depth, None)
        elif winner == self.opponent_symbol:
            return (-10 + depth, None)
        elif TicTacToeLogic.is_board_full(board):
            return (0, None)

        # Depth limit reached
        if depth >= max_depth:
            return (0, None)

        available_moves = TicTacToeLogic.get_available_moves(board)

        if is_maximizing:
            max_score = float('-inf')
            best_move = None

            for move in available_moves:
                new_board = TicTacToeLogic.make_move(board, move, self.symbol)
                score, _ = self._minimax(new_board, depth + 1, max_depth, False)

                if score > max_score:
                    max_score = score
                    best_move = move

            return (max_score, best_move)
        else:
            min_score = float('inf')
            best_move = None

            for move in available_moves:
                new_board = TicTacToeLogic.make_move(board, move, self.opponent_symbol)
                score, _ = self._minimax(new_board, depth + 1, max_depth, True)

                if score < min_score:
                    min_score = score
                    best_move = move

            return (min_score, best_move)

    def _minimax_alpha_beta(
        self,
        board: str,
        depth: int,
        alpha: float,
        beta: float,
        is_maximizing: bool
    ) -> Tuple[int, Optional[int]]:
        """
        Minimax algorithm with alpha-beta pruning
        More efficient for full game tree search

        Args:
            board: Current board state
            depth: Current depth in the game tree
            alpha: Alpha value for pruning
            beta: Beta value for pruning
            is_maximizing: True if maximizing player, False if minimizing

        Returns:
            Tuple of (score, best_move)
        """
        # Check terminal states
        winner = TicTacToeLogic.check_winner(board)
        if winner == self.symbol:
            return (10 - depth, None)
        elif winner == self.opponent_symbol:
            return (-10 + depth, None)
        elif TicTacToeLogic.is_board_full(board):
            return (0, None)

        available_moves = TicTacToeLogic.get_available_moves(board)

        if is_maximizing:
            max_score = float('-inf')
            best_move = None

            for move in available_moves:
                new_board = TicTacToeLogic.make_move(board, move, self.symbol)
                score, _ = self._minimax_alpha_beta(
                    new_board, depth + 1, alpha, beta, False
                )

                if score > max_score:
                    max_score = score
                    best_move = move

                alpha = max(alpha, score)
                if beta <= alpha:
                    break  # Beta cutoff

            return (max_score, best_move)
        else:
            min_score = float('inf')
            best_move = None

            for move in available_moves:
                new_board = TicTacToeLogic.make_move(board, move, self.opponent_symbol)
                score, _ = self._minimax_alpha_beta(
                    new_board, depth + 1, alpha, beta, True
                )

                if score < min_score:
                    min_score = score
                    best_move = move

                beta = min(beta, score)
                if beta <= alpha:
                    break  # Alpha cutoff

            return (min_score, best_move)

    def evaluate_position(self, board: str) -> int:
        """
        Evaluate the current board position

        Args:
            board: Current board state

        Returns:
            Evaluation score (positive is good for bot, negative is bad)
        """
        winner = TicTacToeLogic.check_winner(board)

        if winner == self.symbol:
            return 100
        elif winner == self.opponent_symbol:
            return -100
        else:
            return 0
