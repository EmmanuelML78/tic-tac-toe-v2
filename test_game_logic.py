"""
Test script to verify game logic - wins and draws
"""
import sys
sys.path.insert(0, 'backend')

from backend.app.game.game_logic import TicTacToeLogic, GameResult

def test_win_scenarios():
    """Test all winning scenarios"""
    print("="*60)
    print("TESTING WIN SCENARIOS")
    print("="*60)
    
    # Test horizontal wins
    test_cases = [
        # Horizontal wins for X
        ("XXX------", "X wins - Row 1"),
        ("---XXX---", "X wins - Row 2"),
        ("------XXX", "X wins - Row 3"),
        
        # Horizontal wins for O
        ("OOO------", "O wins - Row 1"),
        ("---OOO---", "O wins - Row 2"),
        ("------OOO", "O wins - Row 3"),
        
        # Vertical wins for X
        ("X--X--X--", "X wins - Column 1"),
        ("-X--X--X-", "X wins - Column 2"),
        ("--X--X--X", "X wins - Column 3"),
        
        # Vertical wins for O
        ("O--O--O--", "O wins - Column 1"),
        ("-O--O--O-", "O wins - Column 2"),
        ("--O--O--O", "O wins - Column 3"),
        
        # Diagonal wins for X
        ("X---X---X", "X wins - Diagonal (top-left to bottom-right)"),
        ("--X-X-X--", "X wins - Diagonal (top-right to bottom-left)"),
        
        # Diagonal wins for O
        ("O---O---O", "O wins - Diagonal (top-left to bottom-right)"),
        ("--O-O-O--", "O wins - Diagonal (top-right to bottom-left)"),
    ]
    
    for board, description in test_cases:
        winner = TicTacToeLogic.check_winner(board)
        result = TicTacToeLogic.get_game_result(board)
        winning_line = TicTacToeLogic.get_winning_line(board)
        
        print(f"\n{description}")
        print(f"Board: {board}")
        print_board(board)
        print(f"Winner detected: {winner}")
        print(f"Result: {result.value}")
        print(f"Winning line: {winning_line}")
        
        expected_winner = 'X' if 'X' in description else 'O'
        if winner != expected_winner:
            print(f"❌ ERROR: Expected {expected_winner}, got {winner}")
        else:
            print(f"✅ PASS")

def test_draw_scenarios():
    """Test draw scenarios"""
    print("\n" + "="*60)
    print("TESTING DRAW SCENARIOS")
    print("="*60)
    
    # Draw scenarios - board is full but no winner
    test_cases = [
        ("XXOOOXXXO", "Draw - Full board no winner 1"),
        ("XOXOXOXOX", "Draw - Full board no winner 2"),
        ("OXXOXOOXO", "Draw - Full board no winner 3"),
        ("XXOOXOOXX", "Draw - Full board no winner 4"),
    ]
    
    for board, description in test_cases:
        winner = TicTacToeLogic.check_winner(board)
        result = TicTacToeLogic.get_game_result(board)
        is_full = TicTacToeLogic.is_board_full(board)
        
        print(f"\n{description}")
        print(f"Board: {board}")
        print_board(board)
        print(f"Board full: {is_full}")
        print(f"Winner detected: {winner}")
        print(f"Result: {result.value}")
        
        if result != GameResult.DRAW:
            print(f"❌ ERROR: Expected DRAW, got {result.value}")
        else:
            print(f"✅ PASS")

def test_ongoing_scenarios():
    """Test ongoing game scenarios"""
    print("\n" + "="*60)
    print("TESTING ONGOING GAME SCENARIOS")
    print("="*60)
    
    test_cases = [
        ("---------", "Empty board"),
        ("X--------", "One move"),
        ("XO-------", "Two moves"),
        ("XOX------", "Three moves"),
        ("XOXOX----", "Five moves - no winner yet"),
        ("XX-OO----", "Mixed moves - no winner yet"),
    ]
    
    for board, description in test_cases:
        winner = TicTacToeLogic.check_winner(board)
        result = TicTacToeLogic.get_game_result(board)
        is_full = TicTacToeLogic.is_board_full(board)
        
        print(f"\n{description}")
        print(f"Board: {board}")
        print_board(board)
        print(f"Board full: {is_full}")
        print(f"Winner detected: {winner}")
        print(f"Result: {result.value}")
        
        if result != GameResult.ONGOING:
            print(f"❌ ERROR: Expected ONGOING, got {result.value}")
        else:
            print(f"✅ PASS")

def test_edge_cases():
    """Test edge cases"""
    print("\n" + "="*60)
    print("TESTING EDGE CASES")
    print("="*60)
    
    # Test case where almost full but still ongoing
    board = "XXOO-XOXO"
    winner = TicTacToeLogic.check_winner(board)
    result = TicTacToeLogic.get_game_result(board)
    
    print(f"\nAlmost full board")
    print(f"Board: {board}")
    print_board(board)
    print(f"Winner detected: {winner}")
    print(f"Result: {result.value}")
    
    if result == GameResult.ONGOING and winner is None:
        print("✅ PASS - Game ongoing correctly")
    else:
        print(f"❌ ERROR: Should be ONGOING with no winner")
    
    # Test immediate win detection (3 in a row from start)
    board = "XXX------"
    winner = TicTacToeLogic.check_winner(board)
    result = TicTacToeLogic.get_game_result(board)
    
    print(f"\nImmediate win")
    print(f"Board: {board}")
    print_board(board)
    print(f"Winner detected: {winner}")
    print(f"Result: {result.value}")
    
    if result == GameResult.WIN and winner == 'X':
        print("✅ PASS - Win detected correctly")
    else:
        print(f"❌ ERROR: Should be WIN with X as winner")

def print_board(board: str):
    """Print board in a nice format"""
    print(f"  {board[0]} | {board[1]} | {board[2]}")
    print(f"  ---------")
    print(f"  {board[3]} | {board[4]} | {board[5]}")
    print(f"  ---------")
    print(f"  {board[6]} | {board[7]} | {board[8]}")

def main():
    print("\n🎮 TIC-TAC-TOE GAME LOGIC VERIFICATION\n")
    
    test_win_scenarios()
    test_draw_scenarios()
    test_ongoing_scenarios()
    test_edge_cases()
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()
