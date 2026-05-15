ROWS = 6
COLS = 7

MASK_HORIZONTAL = 0
for r in range(ROWS):
    MASK_HORIZONTAL |= 0b0111111 << (r * COLS)


def board_to_bitboard(board):
    p1 = 0
    p2 = 0
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] == 1:
                p1 |= 1 << (r * COLS + c)
            elif board[r][c] == 2:
                p2 |= 1 << (r * COLS + c)
    return p1, p2

def bitboard_to_board(p1, p2):
    board = [[0] * COLS for _ in range(ROWS)]
    for r in range(ROWS):
        for c in range(COLS):
            if p1 & (1 << (r * COLS + c)):
                board[r][c] = 1
            elif p2 & (1 << (r * COLS + c)):
                board[r][c] = 2
    return board

def col_is_full (p1, p2, col):
    return (p1 & (1 << col)) != 0 or (p2 & (1 << col)) != 0

def check_pop (p, jogador, col):
    return (p & (1 << (35 + col))) != 0

def drop (p1, p2, jogador, col):
    for r in range(ROWS - 1, -1, -1):
        if (p1 & (1 << (r * COLS + col))) == 0 and (p2 & (1 << (r * COLS + col))) == 0:
            if jogador == 1:
                p1 |= 1 << (r * COLS + col)
            else:
                p2 |= 1 << (r * COLS + col)
            break
    return p1, p2

def pop(p1, p2, col):
    for r in range(ROWS-1, 0, -1):
        idx_atual = r * COLS + col
        idx_acima = (r-1) * COLS + col
        
        if (p1 & (1 << idx_acima)):
            p1 |= 1 << idx_atual
        else:            
            p1 &= ~(1 << idx_atual)

        if (p2 & (1 << idx_acima)):
            p2 |= 1 << idx_atual

        else:
            p2 &= ~(1 << idx_atual)
    
    # apagar o topo (linha 0) em ambos
    p1 &= ~(1 << col)
    p2 &= ~(1 << col)
    
    return p1, p2

def check_victory(p):
    # horizontal
    m = (p & MASK_HORIZONTAL) & ((p & MASK_HORIZONTAL) >> 1)
    if m & (m >> 2): return True
    
    # vertical
    m = p & (p >> 7)
    if m & (m >> 14): return True
    
    # diagonal ↘
    m = p & (p >> 8)
    if m & (m >> 16): return True
    
    # diagonal ↗
    m = p & (p >> 6)
    if m & (m >> 12): return True
    
    return False

def get_legal_moves(p1, p2, jogador):
    p = p1 if jogador == 1 else p2
    moves = []
    for col in range(COLS):
        if not col_is_full(p1, p2, col):
            moves.append(col)
        if check_pop(p, jogador, col):
            moves.append(- (col + 1))
    return moves


