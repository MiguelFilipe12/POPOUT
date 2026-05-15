ROWS = 6
COLS = 7

def iniciar_matrix (): 
    matrix = []
    for r in range(ROWS):

        linha = []

        for c in range(COLS):
            linha.append(0)

        matrix.append(linha)
    return matrix


matrix = iniciar_matrix () 

def print_matrix (board):

    for row in board:
        print (row)


def drop(board, peca, col):

    if col_isFull(board, col):
        return

    for r in range(ROWS-1, -1, -1):
        if board[r][col] == 0:
            board[r][col] = peca
            break

    

def col_isFull(board, col):
    if board[0][col] != 0:
        return True
    return False

def check_victory(board, peca):
    # horizontal
    for r in range(ROWS):
        for c in range(COLS - 3):
            if board[r][c] == peca and board[r][c+1] == peca and board[r][c+2] == peca and board[r][c+3] == peca:
                return True

    # vertical
    for c in range(COLS):
        for r in range(ROWS - 3):
            if board[r][c] == peca and board[r+1][c] == peca and board[r+2][c] == peca and board[r+3][c] == peca:
                return True

    # diagonal (descer)
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if board[r][c] == peca and board[r+1][c+1] == peca and board[r+2][c+2] == peca and board[r+3][c+3] == peca:
                return True

    # diagonal (subir)
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            if board[r][c] == peca and board[r-1][c+1] == peca and board[r-2][c+2] == peca and board[r-3][c+3] == peca:
                return True

    return False

def pop (board, player, col):
    
    for r in range (ROWS - 1, 0, -1):
        board[r][col] = board [r-1][col]


    board[0][col] = 0            

def check_pop(board, player, col):

    if col < 0 or col >= COLS:
        return False

    if board[ROWS-1][col] != player:
        return False

    return True

def check_winning_threat(board, player):
    """Check if a player has a threat (3 in a row with an empty spot to win)"""
    # Check horizontal threats
    for r in range(ROWS):
        for c in range(COLS - 3):
            # Count pieces and empty spaces in a row of 4
            pieces = 0
            empty_spaces = 0
            for i in range(4):
                if board[r][c + i] == player:
                    pieces += 1
                elif board[r][c + i] == 0:
                    empty_spaces += 1
            if pieces == 3 and empty_spaces == 1:
                return True
    
    # Check vertical threats
    for c in range(COLS):
        for r in range(ROWS - 3):
            pieces = 0
            empty_spaces = 0
            for i in range(4):
                if board[r + i][c] == player:
                    pieces += 1
                elif board[r + i][c] == 0:
                    empty_spaces += 1
            if pieces == 3 and empty_spaces == 1:
                return True
    
    # Check diagonal (down-right) threats
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            pieces = 0
            empty_spaces = 0
            for i in range(4):
                if board[r + i][c + i] == player:
                    pieces += 1
                elif board[r + i][c + i] == 0:
                    empty_spaces += 1
            if pieces == 3 and empty_spaces == 1:
                return True
    
    # Check diagonal (up-right) threats
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            pieces = 0
            empty_spaces = 0
            for i in range(4):
                if board[r - i][c + i] == player:
                    pieces += 1
                elif board[r - i][c + i] == 0:
                    empty_spaces += 1
            if pieces == 3 and empty_spaces == 1:
                return True
    
    return False

def get_row_before_drop(board, col):
    for r in reversed(range(ROWS)):
        if board[r][col] == 0:
            return r
    return None

def board_is_full(board):
    return all(board[0][c] != 0 for c in range(COLS))


################################# MAIN ###################################