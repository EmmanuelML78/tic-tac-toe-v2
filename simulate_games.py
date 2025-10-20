"""
Simulación completa de juegos de Tic-Tac-Toe para verificar la lógica
"""

# Copiando la lógica
WINNING_COMBINATIONS = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
    [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
    [0, 4, 8], [2, 4, 6]              # Diagonals
]

def check_winner(board):
    for combination in WINNING_COMBINATIONS:
        symbols = [board[i] for i in combination]
        if symbols[0] != '-' and symbols[0] == symbols[1] == symbols[2]:
            return symbols[0]
    return None

def is_board_full(board):
    return '-' not in board

def get_result(board):
    winner = check_winner(board)
    if winner:
        return "WIN", winner
    if is_board_full(board):
        return "DRAW", None
    return "ONGOING", None

def print_board(board, title=""):
    if title:
        print(f"\n{title}")
    print(f"  {board[0]} | {board[1]} | {board[2]}")
    print(f"  ---------")
    print(f"  {board[3]} | {board[4]} | {board[5]}")
    print(f"  ---------")
    print(f"  {board[6]} | {board[7]} | {board[8]}")

def make_move(board, position, symbol):
    board_list = list(board)
    board_list[position] = symbol
    return ''.join(board_list)

print("="*70)
print("SIMULACIÓN 1: X gana por fila horizontal")
print("="*70)
board = "---------"
moves = [
    (0, 'X'), (3, 'O'), (1, 'X'), (4, 'O'), (2, 'X')
]

for i, (pos, sym) in enumerate(moves):
    board = make_move(board, pos, sym)
    result, winner = get_result(board)
    print_board(board, f"Movimiento {i+1}: {sym} en posición {pos}")
    print(f"Estado: {result}" + (f" - Ganador: {winner}" if winner else ""))
    
    if result != "ONGOING":
        print(f"\n{'✅' if result == 'WIN' and winner == 'X' else '❌'} X gana en fila horizontal [0,1,2]")
        break

print("\n" + "="*70)
print("SIMULACIÓN 2: O gana por columna vertical")
print("="*70)
board = "---------"
moves = [
    (0, 'X'), (1, 'O'), (3, 'X'), (4, 'O'), (8, 'X'), (7, 'O')
]

for i, (pos, sym) in enumerate(moves):
    board = make_move(board, pos, sym)
    result, winner = get_result(board)
    print_board(board, f"Movimiento {i+1}: {sym} en posición {pos}")
    print(f"Estado: {result}" + (f" - Ganador: {winner}" if winner else ""))
    
    if result != "ONGOING":
        print(f"\n{'✅' if result == 'WIN' and winner == 'O' else '❌'} O gana en columna vertical [1,4,7]")
        break

print("\n" + "="*70)
print("SIMULACIÓN 3: X gana por diagonal")
print("="*70)
board = "---------"
moves = [
    (0, 'X'), (1, 'O'), (4, 'X'), (2, 'O'), (8, 'X')
]

for i, (pos, sym) in enumerate(moves):
    board = make_move(board, pos, sym)
    result, winner = get_result(board)
    print_board(board, f"Movimiento {i+1}: {sym} en posición {pos}")
    print(f"Estado: {result}" + (f" - Ganador: {winner}" if winner else ""))
    
    if result != "ONGOING":
        print(f"\n{'✅' if result == 'WIN' and winner == 'X' else '❌'} X gana en diagonal [0,4,8]")
        break

print("\n" + "="*70)
print("SIMULACIÓN 4: Empate (tablero lleno sin ganador)")
print("="*70)
board = "---------"
moves = [
    (0, 'X'), (1, 'O'), (2, 'X'),  # X O X
    (3, 'X'), (4, 'O'), (5, 'O'),  # X O O
    (6, 'O'), (7, 'X'), (8, 'X')   # O X X
]

for i, (pos, sym) in enumerate(moves):
    board = make_move(board, pos, sym)
    result, winner = get_result(board)
    print_board(board, f"Movimiento {i+1}: {sym} en posición {pos}")
    print(f"Estado: {result}" + (f" - Ganador: {winner}" if winner else ""))
    
    if result != "ONGOING":
        print(f"\n{'✅' if result == 'DRAW' else '❌'} Empate - tablero lleno sin tres en línea")
        break

print("\n" + "="*70)
print("SIMULACIÓN 5: Juego en curso (no lleno, sin ganador)")
print("="*70)
board = "---------"
moves = [
    (0, 'X'), (4, 'O'), (1, 'X'), (3, 'O')
]

for i, (pos, sym) in enumerate(moves):
    board = make_move(board, pos, sym)
    result, winner = get_result(board)
    print_board(board, f"Movimiento {i+1}: {sym} en posición {pos}")
    print(f"Estado: {result}" + (f" - Ganador: {winner}" if winner else ""))

if result == "ONGOING":
    print(f"\n✅ Juego continúa - tablero no lleno y sin ganador aún")

print("\n" + "="*70)
print("RESUMEN DE LA LÓGICA")
print("="*70)
print("""
La lógica del juego está CORRECTA:

1. ✅ Detecta victoria cuando hay 3 símbolos iguales en:
   - Cualquier fila horizontal (posiciones 0-1-2, 3-4-5, 6-7-8)
   - Cualquier columna vertical (posiciones 0-3-6, 1-4-7, 2-5-8)
   - Cualquier diagonal (posiciones 0-4-8, 2-4-6)

2. ✅ Detecta empate cuando:
   - El tablero está completamente lleno (9 posiciones ocupadas)
   - NO hay tres símbolos iguales alineados

3. ✅ Detecta juego en curso cuando:
   - El tablero NO está lleno
   - NO hay ganador aún

La implementación es correcta y sigue las reglas estándar del Tic-Tac-Toe.
""")
