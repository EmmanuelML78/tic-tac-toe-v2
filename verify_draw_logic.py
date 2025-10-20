"""
Verificación simple de la lógica de empate
"""

# Copiando la lógica directamente para probar
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

def check_winner(board):
    """Check if there's a winner"""
    for combination in WINNING_COMBINATIONS:
        symbols = [board[i] for i in combination]
        if symbols[0] != '-' and symbols[0] == symbols[1] == symbols[2]:
            return symbols[0]
    return None

def is_board_full(board):
    """Check if board is full"""
    return '-' not in board

def get_result(board):
    """Get game result"""
    winner = check_winner(board)
    if winner:
        return "WIN", winner
    if is_board_full(board):
        return "DRAW", None
    return "ONGOING", None

# Casos REALES de empate
real_draws = [
    'XXOOOXXXO',  # Ya probado - es empate real
    'XOXOXOOXO',  # Diferente
    'OXOXXXOOX',  # Diferente
    'OXXOXOXOO',  # Diferente
    'XOXOOXXXO',  # Diferente
]

print('='*60)
print('VERIFICANDO EMPATES REALES')
print('='*60)

for board in real_draws:
    result, winner = get_result(board)
    print(f'\nBoard: {board}')
    print(f'  {board[0]} | {board[1]} | {board[2]}')
    print(f'  ---------')
    print(f'  {board[3]} | {board[4]} | {board[5]}')
    print(f'  ---------')
    print(f'  {board[6]} | {board[7]} | {board[8]}')
    print(f'Winner: {winner}, Result: {result}')
    
    # Verificar todas las líneas
    print(f'Verificando líneas ganadoras:')
    for i, combo in enumerate(WINNING_COMBINATIONS):
        symbols = [board[pos] for pos in combo]
        if symbols[0] != '-' and symbols[0] == symbols[1] == symbols[2]:
            print(f'  ⚠️ Línea {i+1} {combo}: {symbols} - ¡GANADORA!')
    
    if result == 'DRAW':
        print('✅ Empate confirmado')
    elif result == 'WIN':
        print(f'⚠️ No es empate, {winner} ganó')
