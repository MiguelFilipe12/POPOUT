import random
import math
import bitboard as bl
from numba import njit

class Node:

    
    __slots__ = ('p1', 'p2', 'jogador_atual', 'move', 'parent',
                 'children', 'visits', 'wins', 'untried_moves')

    def __init__(self, p1, p2, jogador_atual, move=None, parent=None):
        self.p1 = p1
        self.p2 = p2
        self.jogador_atual = jogador_atual
        self.move = move
        self.parent = parent
        self.children = []
        self.visits = 0
        self.wins = 0
        # Movimentos possíveis a partir DESTE estado
        self.untried_moves = bl.get_legal_moves(self.p1, self.p2, jogador_atual)

    def expand(self):


        move = self.untried_moves.pop()
        
        
        if move >= 0:
            novo_p1, novo_p2 = bl.drop(self.p1, self.p2, self.jogador_atual, move)
        else:
            novo_p1, novo_p2 = bl.pop(self.p1, self.p2, - (move + 1))
            
        child = Node(novo_p1, novo_p2, 3 - self.jogador_atual, move, self)
        self.children.append(child)
        return child

    def select_child(self):
        log_pv = math.log(self.visits)
        best_score = -1.0
        best = None
        for c in self.children:
            score = (c.wins / c.visits) + 1.41 * math.sqrt(log_pv / c.visits)
            if score > best_score:
                best_score = score
                best = c
        return best
    def is_terminal(self):
        if bl.check_victory(self.p1) or bl.check_victory(self.p2):
            return True
        return len(bl.get_legal_moves(self.p1, self.p2, self.jogador_atual)) == 0

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
@njit
def simulate(p1, p2, jogador_atual):
    curr = jogador_atual
    for _ in range(42):
        p = p1 if curr == 1 else p2
        moves = [0] * 14
        nm = 0
        for c in range(7):
            if not ((p1 | p2) >> c & 1):
                moves[nm] = c
                nm += 1
            if (p >> (35 + c)) & 1:
                moves[nm] = -(c + 1)
                nm += 1
        if nm == 0: break
        
        move = moves[int(random.random() * nm)]
        
        if move >= 0:
            for r in range(5, -1, -1):
                idx = r * 7 + move
                if not ((p1 | p2) >> idx & 1):
                    if curr == 1: p1 |= 1 << idx
                    else: p2 |= 1 << idx
                    break
        else:
            col = -(move + 1)
            for r in range(5, 0, -1):
                ia = r * 7 + col
                ib = (r-1) * 7 + col
                if (p1 >> ib) & 1: p1 |= 1 << ia
                else: p1 &= ~(1 << ia)
                if (p2 >> ib) & 1: p2 |= 1 << ia
                else: p2 &= ~(1 << ia)
            p1 &= ~(1 << col)
            p2 &= ~(1 << col)
        
        # check_victory inline
        # horizontal
        m = p1 & (p1 >> 1); 
        if m & (m >> 2): return 1
        m = p2 & (p2 >> 1)
        if m & (m >> 2): return 2
        # vertical
        m = p1 & (p1 >> 7)
        if m & (m >> 14): return 1
        m = p2 & (p2 >> 7)
        if m & (m >> 14): return 2
        # diagonal ↘
        m = p1 & (p1 >> 8)
        if m & (m >> 16): return 1
        m = p2 & (p2 >> 8)
        if m & (m >> 16): return 2
        # diagonal ↗
        m = p1 & (p1 >> 6)
        if m & (m >> 12): return 1
        m = p2 & (p2 >> 6)
        if m & (m >> 12): return 2

        curr = 3 - curr
    return 0

def algoritmo_mcts(board, jogador_atual, tempo, root=None):

    import time
    p1, p2 = bl.board_to_bitboard(board)

    legal = bl.get_legal_moves(p1, p2, jogador_atual)
    if root is None or root.p1 != p1 or root.p2 != p2:
        root = Node(p1, p2, jogador_atual)

    fim = time.time() + tempo
    iteracoes = 0
    while time.time() < fim:
        node = root

        # Seleção
        terminal = node.is_terminal()
        while node.children and not node.untried_moves and not terminal:
            node = node.select_child()
            terminal = node.is_terminal()

        # Expansão — reutiliza o terminal já calculado
        if node.untried_moves and not terminal:
            node = node.expand()

        # Simulação
        result = simulate(node.p1, node.p2, node.jogador_atual)

        # Backpropagation
        node.backpropagate(result)
        iteracoes += 1

    print(f"MCTS_Bitboard Iterações: {iteracoes}")
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
    # converter tuplo para inteiro
    if move[0] == "drop":
        move_int = move[1]
    else:
        move_int = -(move[1] + 1)
    
    for child in root.children:
        if child.move == move_int:
            child.parent = None
            return child
    return None
