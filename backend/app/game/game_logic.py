"""
Tic-Tac-Toe game logic
"""
from typing import Optional, List, Tuple
from enum import Enum


class GameResult(Enum):
    """Game result enum"""
    WIN = "win"
    DRAW = "draw"
    ONGOING = "ongoing"


class TicTacToeLogic:
    """
    Tic-Tac-Toe game logic implementation
    Board positions: 0-8
    Board representation:
    0 | 1 | 2
    ---------
    3 | 4 | 5
    ---------
    6 | 7 | 8
    """

    # Winning combinations
    WINNING_COMBINATIONS = [
        # Rows
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],
        # Columns
        [0, 3, 6],
        [1, 4, 7],
        [2, 5, 8],
        # Diagonals
        [0, 4, 8],
        [2, 4, 6]
    ]

    @staticmethod
    def create_empty_board() -> str:
        """Create an empty board"""
        return "---------"

    @staticmethod
    def is_valid_move(board: str, position: int) -> bool:
        """
        Check if a move is valid

        Args:
            board: Current board state
            position: Position to check (0-8)

        Returns:
            True if move is valid, False otherwise
        """
        if position < 0 or position > 8:
            return False

        return board[position] == '-'

    @staticmethod
    def make_move(board: str, position: int, symbol: str) -> str:
        """
        Make a move on the board

        Args:
            board: Current board state
            position: Position to place symbol (0-8)
            symbol: Symbol to place ('X' or 'O')

        Returns:
            New board state
        """
        if not TicTacToeLogic.is_valid_move(board, position):
            raise ValueError(f"Invalid move at position {position}")

        board_list = list(board)
        board_list[position] = symbol
        return ''.join(board_list)

    @staticmethod
    def check_winner(board: str) -> Optional[str]:
        """
        Check if there's a winner

        Args:
            board: Current board state

        Returns:
            Winning symbol ('X' or 'O') or None
        """
        for combination in TicTacToeLogic.WINNING_COMBINATIONS:
            symbols = [board[i] for i in combination]

            # Check if all three positions have the same symbol and it's not empty
            if symbols[0] != '-' and symbols[0] == symbols[1] == symbols[2]:
                return symbols[0]

        return None

    @staticmethod
    def is_board_full(board: str) -> bool:
        """
        Check if the board is full

        Args:
            board: Current board state

        Returns:
            True if board is full, False otherwise
        """
        return '-' not in board

    @staticmethod
    def get_game_result(board: str) -> GameResult:
        """
        Get the current game result

        Args:
            board: Current board state

        Returns:
            GameResult enum value
        """
        winner = TicTacToeLogic.check_winner(board)

        if winner:
            return GameResult.WIN

        if TicTacToeLogic.is_board_full(board):
            return GameResult.DRAW

        return GameResult.ONGOING

    @staticmethod
    def get_available_moves(board: str) -> List[int]:
        """
        Get list of available moves

        Args:
            board: Current board state

        Returns:
            List of available positions
        """
        return [i for i, cell in enumerate(board) if cell == '-']

    @staticmethod
    def get_winning_line(board: str) -> Optional[List[int]]:
        """
        Get the winning line positions

        Args:
            board: Current board state

        Returns:
            List of winning positions or None
        """
        for combination in TicTacToeLogic.WINNING_COMBINATIONS:
            symbols = [board[i] for i in combination]

            if symbols[0] != '-' and symbols[0] == symbols[1] == symbols[2]:
                return combination

        return None

    @staticmethod
    def get_opponent_symbol(symbol: str) -> str:
        """
        Get opponent's symbol

        Args:
            symbol: Current player symbol

        Returns:
            Opponent symbol
        """
        return 'O' if symbol == 'X' else 'X'

    @staticmethod
    def board_to_matrix(board: str) -> List[List[str]]:
        """
        Convert board string to 3x3 matrix

        Args:
            board: Board string

        Returns:
            3x3 matrix representation
        """
        return [
            [board[0], board[1], board[2]],
            [board[3], board[4], board[5]],
            [board[6], board[7], board[8]]
        ]

    @staticmethod
    def matrix_to_board(matrix: List[List[str]]) -> str:
        """
        Convert 3x3 matrix to board string

        Args:
            matrix: 3x3 matrix

        Returns:
            Board string
        """
        return ''.join([''.join(row) for row in matrix])
