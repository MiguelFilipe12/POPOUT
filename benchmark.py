import csv
import random
from game_logic import *
import MCTS as mcts_easy
import MCTS_fast as mcts_medium
import MCTS_bitboard as mcts_hard
from ID3 import Node as ID3Node

ITERACOES_EASY = 6000
TEMPO = {"medium": 5.0, "hard": 5.0}

def load_dt():
    try:
        examples = []
        with open("dataset.csv", "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                example = {f"cell_{r}_{c}": row[f"cell_{r}_{c}"] for r in range(6) for c in range(7)}
                example["label"] = row["label"]
                examples.append(example)
        attributes = [f"cell_{r}_{c}" for r in range(6) for c in range(7)]
        tree = ID3Node(max_depth=None)
        tree.build_tree(examples, attributes, 0)
        return tree
    except Exception as e:
        print(f"[DT] Erro: {e}")
        return None

def dt_play(board, tree, player):
    example = {f"cell_{r}_{c}": str(board[r][c]) for r in range(6) for c in range(7)}
    label = tree.predict(example)
    if label is None:
        moves = mcts_easy.get_legal_moves(board, player)
        return random.choice(moves) if moves else ("drop", 3)
    action, col = label.split("_")
    return (action, int(col))

def get_mcts(modo):
    if modo == "easy":   return mcts_easy
    if modo == "medium": return mcts_medium
    if modo == "hard":   return mcts_hard
    return None

def ai_play(modo, board, jogador, root, dt_tree):
    if modo == "dt":
        movimento = dt_play(board, dt_tree, jogador)
        legal = mcts_easy.get_legal_moves(board, jogador)
        if movimento not in legal:
            movimento = random.choice(legal) if legal else ("drop", 3)
        return movimento, None
    mcts = get_mcts(modo)
    if modo == "easy":
        return mcts.algoritmo_mcts(board, jogador, ITERACOES_EASY, root)
    else:
        return mcts.algoritmo_mcts(board, jogador, TEMPO[modo], root)

def jogar_jogo(agente1, agente2, dt_tree):
    board = iniciar_matrix()
    current_player = 1
    root1 = None
    root2 = None
    state_history = {}

    for _ in range(84):
        estado = tuple(tuple(row) for row in board)
        state_history[estado] = state_history.get(estado, 0) + 1
        if state_history[estado] >= 3:
            return 0
        if board_is_full(board) and not check_victory(board, 1) and not check_victory(board, 2):
            return 0

        root_atual = root1 if current_player == 1 else root2
        agente_atual = agente1 if current_player == 1 else agente2

        movimento, novo_root = ai_play(agente_atual, board, current_player, root_atual, dt_tree)

        if current_player == 1:
            root1 = novo_root
            if agente2 != "dt" and root2 is not None:
                root2 = get_mcts(agente2).atualizar_root(root2, movimento)
        else:
            root2 = novo_root
            if agente1 != "dt" and root1 is not None:
                root1 = get_mcts(agente1).atualizar_root(root1, movimento)

        if movimento[0] == "drop":
            drop(board, current_player, movimento[1])
        else:
            pop(board, current_player, movimento[1])

        if check_victory(board, current_player):
            return current_player
        if check_victory(board, 3 - current_player):
            return 3 - current_player

        current_player = 3 - current_player

    return 0

def benchmark(agente1, agente2, n_jogos, nome1, nome2, dt_tree):
    v1, v2, empates = 0, 0, 0
    for i in range(n_jogos):
        if i % 2 == 0:
            r = jogar_jogo(agente1, agente2, dt_tree)
            if r == 1: v1 += 1
            elif r == 2: v2 += 1
            else: empates += 1
        else:
            r = jogar_jogo(agente2, agente1, dt_tree)
            if r == 2: v1 += 1
            elif r == 1: v2 += 1
            else: empates += 1
        print(f"  Jogo {i+1}/{n_jogos} | {nome1}: {v1} | {nome2}: {v2} | Empates: {empates}")
    return v1, v2, empates

# ── Main ────────────────────────────────────────────────────────────────────────
N_JOGOS = 50

print("A carregar Decision Tree...")
dt_tree = load_dt()

pares = [
    ("easy",   "medium", "Facil", "Médio"),
    ("medium",   "easy", "Médio", "Fácil"),
    ("easy",   "hard", "Fácil", "Difícil"),
    ("hard", "easy", "Difícil", "Fácil"),
    ("easy", "dt", "Fácil", "Árvore"),
    ("dt", "easy", "Árvore", "Fácil"),
    ("medium", "hard", "Médio", "Difícil"),
    ("hard", "medium", "Difícil", "Médio"),
    ("medium", "dt", "Médio", "Árvore"),
    ("dt", "medium", "Árvore," "Médio"),
    ("hard", "dt", "Difícil", "Árvore"),
    ("dt", "hard", "Árvore", "Difícil")
]

resultados = []
for a1, a2, n1, n2 in pares:
    print(f"\n{n1} vs {n2}")
    v1, v2, e = benchmark(a1, a2, N_JOGOS, n1, n2, dt_tree)
    resultados.append((n1, n2, v1, v2, e))
    print(f"  -> {n1}: {v1} | {n2}: {v2} | Empates: {e}")

print("\n===== RESULTADOS FINAIS =====")
for n1, n2, v1, v2, e in resultados:
    print(f"{n1} vs {n2}: {v1} / {v2} / {e} (empates)")

import os

file_exists = os.path.exists("benchmark_resultados.csv")
with open("benchmark_resultados.csv", "a", newline="") as f:
    fieldnames = ["agente1", "agente2", "vitorias1", "vitorias2", "empates", "n_jogos"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    if not file_exists:
        writer.writeheader()
    for n1, n2, v1, v2, e in resultados:
        writer.writerow({
            "agente1": n1,
            "agente2": n2,
            "vitorias1": v1,
            "vitorias2": v2,
            "empates": e,
            "n_jogos": N_JOGOS
        })

print("Resultados guardados em benchmark_resultados.csv")