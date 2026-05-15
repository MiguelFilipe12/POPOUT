import random
import time
import game_logic as gl
import math


def board_to_tuple(board):
    return tuple(cell for row in board for cell in row)

def drop_tuple(board, peca, col):
    lst = list(board)  # cópia temporária para modificar
    for r in range(gl.ROWS - 1, -1, -1):
        if lst[r * gl.COLS + col] == 0:
            lst[r * gl.COLS + col] = peca
            break
    return tuple(lst)

def pop_tuple(board, col):
    lst = list(board)
    for r in range(gl.ROWS - 1, 0, -1):
        lst[r * gl.COLS + col] = lst[(r - 1) * gl.COLS + col]
    lst[col] = 0
    return tuple(lst)

def check_victory_tuple(board, peca):
    # horizontal
    for r in range(gl.ROWS):
        for c in range(gl.COLS - 3):
            if board[r * gl.COLS + c] == peca and board[r * gl.COLS + c + 1] == peca and board[r * gl.COLS + c + 2] == peca and board[r * gl.COLS + c + 3] == peca:
                return True

    # vertical
    for c in range(gl.COLS):
        for r in range(gl.ROWS - 3):
            if board[r * gl.COLS + c] == peca and board[(r + 1) * gl.COLS + c] == peca and board[(r + 2) * gl.COLS + c] == peca and board[(r + 3) * gl.COLS + c] == peca:
                return True

    # diagonal (descer)
    for r in range(gl.ROWS - 3):
        for c in range(gl.COLS - 3):
            if board[r * gl.COLS + c] == peca and board[(r + 1) * gl.COLS + c + 1] == peca and board[(r + 2) * gl.COLS + c + 2] == peca and board[(r + 3) * gl.COLS + c + 3] == peca:
                return True

    # diagonal (subir)
    for r in range(3, gl.ROWS):
        for c in range(gl.COLS - 3):
            if board[r * gl.COLS + c] == peca and board[(r - 1) * gl.COLS + c + 1] == peca and board[(r - 2) * gl.COLS + c + 2] == peca and board[(r - 3) * gl.COLS + c + 3] == peca:
                return True

    return False


class Node:
    def __init__(self, board, jogador_atual, move=None, parent=None):
        self.board = board
        self.jogador_atual = jogador_atual
        self.move = move
        self.parent = parent
        self.children = []
        self.visits = 0
        self.wins = 0
        # Movimentos possíveis a partir DESTE estado
        self.untried_moves = get_legal_moves(self.board, jogador_atual)

    def expand(self):


        move = self.untried_moves.pop()
        
        
        if move >= 0:
            new_board = drop_tuple(self.board, self.jogador_atual, move)
        else:
            new_board = pop_tuple(self.board, - (move + 1))
            
        child = Node(new_board, 3 - self.jogador_atual, move, self)
        self.children.append(child)
        return child

    def select_child(self):
        # UCT
        log_parent = math.log(self.visits)
        return max(self.children, key=lambda c: (c.wins / c.visits) + 1.41 * math.sqrt(log_parent / c.visits))

    def is_terminal(self):
        if check_victory_tuple(self.board, 1) or check_victory_tuple(self.board, 2):
            return True
        return not any(self.board[c] == 0 for c in range(gl.COLS))

    def backpropagate(self, result):
        node = self
        while node is not None:
            node.visits += 1
            # O resultado é o vencedor (1 ou 2). Se o vencedor for quem jogou para chegar a este nó, conta vitória.
            if result == 3 - node.jogador_atual: 
                node.wins += 1
            elif result == 0:
                node.wins += 0.5
            node = node.parent

def get_legal_moves(board, jogador):
    moves = []
    for c in range(gl.COLS):
        if board[c] == 0:   # índice c = linha 0, coluna c - > topo livre = coluna não cheia
            moves.append(c)  # drop (POSITIVO)
        if board[(gl.ROWS - 1) * gl.COLS + c] == jogador:  # fundo pertence ao jogador, pode fazer pop
            moves.append(- (c + 1))  # usar número negativo para distinguir pop de drop
    return moves

def simulate(board, jogador_atual):
    temp_board = board
    curr = jogador_atual
    
    for _ in range(42):
        moves = get_legal_moves(temp_board, curr)
        if not moves: break
        move = random.choice(moves)
        
        if move >= 0:
            temp_board = drop_tuple(temp_board, curr, move)
        else:
            temp_board = pop_tuple(temp_board, -(move + 1))
            
        if check_victory_tuple(temp_board, curr):
            return curr
        curr = 3 - curr
    return 0
def algoritmo_mcts(board, jogador_atual, tempo, root=None):
    
    if isinstance(board, list):
        board = board_to_tuple(board)
    legal = get_legal_moves(board, jogador_atual)
    if root is None or root.board != board:
        root = Node(board, jogador_atual)
    
    fim = time.time() + tempo
    iteracoes = 0
    while time.time() < fim:
        node = root
        # Seleção
        while node.children and not node.untried_moves and not node.is_terminal():
            node = node.select_child()
        # Expansão
        if node.untried_moves and not node.is_terminal():
            node = node.expand()
        # Simulação
        result = simulate(node.board, node.jogador_atual)
        # Backpropagation
        node.backpropagate(result)
        iteracoes += 1
    
    print(f"Iterações: {iteracoes}")
    if not root.children:
        move = random.choice(legal)
        if move >= 0:
            return ("drop", move), None
        else:
            return ("pop", - (move + 1)), None
        
    best_child = max(root.children, key=lambda c: c.visits)
    move = best_child.move
    if move >= 0:
        return ("drop", move), best_child
    else:
        return ("pop", -(move + 1)), best_child


def atualizar_root(root, move):
    if root is None: return None
    for child in root.children:
        if child.move == move:
            child.parent = None
            return child
    return None
