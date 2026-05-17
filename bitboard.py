# bitboard.py
ROWS = 6
COLS = 7

# Máscaras para evitar que 4 em linha "dobrem" a esquina do tabuleiro
# Criadas bit a bit para não haver erro de interpretação
NOT_COL0 = 0
for r in range(6):
    for c in range(1, 7): NOT_COL0 |= (1 << (r * 7 + c))

NOT_COL6 = 0
for r in range(6):
    for c in range(0, 6): NOT_COL6 |= (1 << (r * 7 + c))

def board_to_bitboard(board):
    p1, p2 = 0, 0
    for r in range(6):
        for c in range(7):
            if board[r][c] == 1: p1 |= (1 << (r * 7 + c))
            elif board[r][c] == 2: p2 |= (1 << (r * 7 + c))
    return p1, p2

def col_is_full(p1, p2, col):
    return ((p1 | p2) & (1 << col)) != 0

def check_pop(p, jogador, col):
    # Fundo é a linha 5 (bits 35 a 41)
    return (p & (1 << (35 + col))) != 0

def drop(p1, p2, jogador, col):
    # Procura da linha 5 para a 0
    for r in range(5, -1, -1):
        idx = r * 7 + col
        if not ((p1 | p2) & (1 << idx)):
            if jogador == 1: p1 |= (1 << idx)
            else: p2 |= (1 << idx)
            break
    return p1, p2

def pop(p1, p2, col):
    # Peças de cima caem
    for r in range(5, 0, -1):
        idx_atual, idx_acima = r * 7 + col, (r - 1) * 7 + col
        if p1 & (1 << idx_acima): p1 |= (1 << idx_atual)
        else: p1 &= ~(1 << idx_atual)
        if p2 & (1 << idx_acima): p2 |= (1 << idx_atual)
        else: p2 &= ~(1 << idx_atual)
    # Topo fica vazio
    p1 &= ~(1 << col)
    p2 &= ~(1 << col)
    return p1, p2

def check_victory(p):
    # Vertical (shift 7)
    v = p & (p >> 7)
    if v & (v >> 14): return True
    # Horizontal (shift 1 + máscara)
    h = p & (p >> 1) & NOT_COL0
    if h & (h >> 2) & (NOT_COL0 >> 2): return True
    # Diagonal \ (shift 8 + máscara)
    d1 = p & (p >> 8) & NOT_COL0
    if d1 & (d1 >> 16) & (NOT_COL0 >> 16): return True
    # Diagonal / (shift 6 + máscara)
    d2 = p & (p >> 6) & NOT_COL6
    if d2 & (d2 >> 12) & (NOT_COL6 >> 12): return True
    return False

def get_legal_moves(p1, p2, jogador):
    p_jogador = p1 if jogador == 1 else p2
    moves = []
    for c in range(7):
        if not col_is_full(p1, p2, c): moves.append(c) # Drop
        if check_pop(p_jogador, jogador, c): moves.append(-(c + 1)) # Pop
    return moves