import random
import game_logic as gl
import math

class Node:
    def __init__(self, board, jogador_atual, move=None, parent=None):
        self.board = [row[:] for row in board]
        self.jogador_atual = jogador_atual
        self.move = move
        self.parent = parent
        self.children = []
        self.visits = 0
        self.wins = 0
        # Movimentos possíveis a partir DESTE estado
        self.untried_moves = get_legal_moves(self.board, jogador_atual)

    def expand(self):
        if not self.untried_moves:
            return None
        move = self.untried_moves.pop()
        new_board = [row[:] for row in self.board]
        
        if move[0] == "drop":
            gl.drop(new_board, self.jogador_atual, move[1])
        else:
            gl.pop(new_board, self.jogador_atual, move[1])
            
        child = Node(new_board, 3 - self.jogador_atual, move, self)
        self.children.append(child)
        return child

    def select_child(self):
        # UCT
        log_parent = math.log(self.visits)
        return max(self.children, key=lambda c: (c.wins / c.visits) + 1.41 * math.sqrt(log_parent / c.visits))

    def is_terminal(self):
        if gl.check_victory(self.board, 1) or gl.check_victory(self.board, 2):
            return True
        return not any(not gl.col_isFull(self.board, c) for c in range(gl.COLS))

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
        if not gl.col_isFull(board, c):
            moves.append(("drop", c))
        if gl.check_pop(board, jogador, c):
            moves.append(("pop", c))
    return moves

def simulate(board, jogador_atual):
    temp_board = [row[:] for row in board]
    curr = jogador_atual
    
   # jogadas max
    for _ in range(42):
        moves = get_legal_moves(temp_board, curr)
        if not moves: break
        
        pop_moves = [m for m in moves if m[0] == "pop"]
        drop_moves = [m for m in moves if m[0] == "drop"]


        # Heurística rápida: ganhar ou bloquear
        best_move = None
        for m in moves:
            info = apply_move(temp_board, curr, m)
            if gl.check_victory(temp_board, curr):
                undo_move(temp_board, info)
                best_move = m
                break
            undo_move(temp_board, info)
            
            # Bloquear oponente
            info_op = apply_move(temp_board, 3 - curr, m)
            if gl.check_victory(temp_board, 3 - curr):
                undo_move(temp_board, info_op)
                best_move = m # Prioridade bloqueio se não houver vitória
            else:
                undo_move(temp_board, info_op)

        if best_move:
            move = best_move
        elif pop_moves and random.random() < 0.4:
            move = random.choice(pop_moves)
        else: 
            move = random.choice(drop_moves if drop_moves else moves)

        
        if move[0] == "drop": gl.drop(temp_board, curr, move[1])
        else: gl.pop(temp_board, curr, move[1])
            
        if gl.check_victory(temp_board, curr):
            return curr
        curr = 3 - curr
    return 0

def algoritmo_mcts(board, jogador_atual, iteracoes, root=None):

    legal = get_legal_moves(board, jogador_atual)
    
    # verificar vitória imediata
    for m in legal:
        info = apply_move(board, jogador_atual, m)
        if gl.check_victory(board, jogador_atual):
            undo_move(board, info)
            return m, None
        undo_move(board, info)
    
    # verificar bloqueio imediato
    safe_blocking_move = None
    for m in legal:
        # vê se o oponente ganharia se jogasse aqui
        info_op = apply_move(board, 3 - jogador_atual, m)
        if gl.check_victory(board, 3 - jogador_atual):
            undo_move(board, info_op)
            
            # temos de bloquear. Mas este bloqueio é seguro?
            if not leads_to_opponent_win(board, m, jogador_atual):
                return m, None # Bloqueio seguro!
            else:
                safe_blocking_move = m # Bloqueio desesperado (suicídio de qualquer forma)
        else:
            undo_move(board, info_op)


    if root is None or root.board != board:
        root = Node(board, jogador_atual)
    
    for _ in range(iteracoes):
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
    
    if not root.children:
        return random.choice(legal), None
        
    best_child = max(root.children, key=lambda c: c.visits)
    return best_child.move, best_child

def apply_move(board, jogador, move):
    if move[0] == "drop":
        row = gl.get_row_before_drop(board, move[1])
        gl.drop(board, jogador, move[1])
        return ("drop", move[1], row)
    else:
        removed = board[gl.ROWS-1][move[1]]
        gl.pop(board, jogador, move[1])
        return ("pop", move[1], removed)

def undo_move(board, move_info):
    if move_info[0] == "drop":
        if move_info[2] is not None:
            board[move_info[2]][move_info[1]] = 0
    else:
        col, removed = move_info[1], move_info[2]
        for r in range(gl.ROWS - 1):
            board[r][col] = board[r+1][col]
        board[gl.ROWS-1][col] = removed

def atualizar_root(root, move):
    if root is None: return None
    for child in root.children:
        if child.move == move:
            child.parent = None
            return child
    return None


def leads_to_opponent_win(board, move, jogador_ia):
    """Verifica se uma jogada da IA resulta numa vitória imediata do oponente"""
    oponente = 3 - jogador_ia
    # Fazemos a jogada
    info = apply_move(board, jogador_ia, move)
    # Verificamos se o oponente ficou com 4-em-linha (comum no POP)
    if gl.check_victory(board, oponente):
        undo_move(board, info)
        return True
    
    # Verificamos se o oponente agora consegue ganhar em qualquer coluna
    can_win = False
    for m_op in get_legal_moves(board, oponente):
        info_op = apply_move(board, oponente, m_op)
        if gl.check_victory(board, oponente):
            can_win = True
        undo_move(board, info_op)
        if can_win: break
        
    undo_move(board, info)
    return can_win