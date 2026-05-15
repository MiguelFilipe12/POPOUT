import os
os.environ['MPLBACKEND'] = 'Agg'

import pygame
import csv
import time
from game_logic import *
from ID3 import Node as ID3Node

# ── Importar os 3 módulos MCTS ──────────────────────────────────────────────────
import MCTS as mcts_easy
import MCTS_fast as mcts_medium
import MCTS_bitboard as mcts_hard

def get_mcts(modo):
    if modo == "easy":   return mcts_easy
    if modo == "medium": return mcts_medium
    if modo == "hard":   return mcts_hard
    return None  # "dt" → sem módulo MCTS

# ── Iterações / Tempo por dificuldade ──────────────────────────────────────────
ITERACOES_EASY = 6000

TEMPO = {
    "medium": 5.0,
    "hard":   5.0,
}

dataset = []
def reset_game():
    return iniciar_matrix(), 1, None

pygame.init()

cell_size   = 110
top_area    = 90
bottom_area = 90

width  = COLS * cell_size
height = ROWS * cell_size + top_area + bottom_area

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("connect 4")

black      = (0, 0, 0)
background = (12, 16, 40)
board_color = (35, 85, 140)
hole_color  = (230, 235, 240)
player1     = (255, 130, 60)
player2     = (130, 190, 120)


# ── Desenhar tabuleiro ──────────────────────────────────────────────────────────
def draw_board(board):
    pygame.draw.rect(screen, board_color,
                     (0, top_area, COLS * cell_size, ROWS * cell_size),
                     border_radius=25)
    for r in range(ROWS):
        for c in range(COLS):
            x = c * cell_size
            y = r * cell_size + top_area
            center = (x + cell_size // 2, y + cell_size // 2)
            if board[r][c] == 0:
                pygame.draw.circle(screen, hole_color, center, cell_size // 2 - 10)
            elif board[r][c] == 1:
                pygame.draw.circle(screen, player1, center, cell_size // 2 - 10)
            elif board[r][c] == 2:
                pygame.draw.circle(screen, player2, center, cell_size // 2 - 10)


# ── Decision Tree ───────────────────────────────────────────────────────────────
def dt_play(board, tree, player):
    example = {f"cell_{r}_{c}": str(board[r][c]) for r in range(6) for c in range(7)}
    label = tree.predict(example)
    if label is None:
        import random
        moves = mcts_easy.get_legal_moves(board, player)
        return random.choice(moves) if moves else ("drop", 3)
    action, col = label.split("_")
    return (action, int(col))

def load_dt():
    try:
        examples = []
        with open("dataset.csv", "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                example = {f"cell_{r}_{c}": row[f"cell_{r}_{c}"]
                           for r in range(6) for c in range(7)}
                example["label"] = row["label"]
                examples.append(example)
        attributes = [f"cell_{r}_{c}" for r in range(6) for c in range(7)]
        tree = ID3Node(max_depth=None)
        tree.build_tree(examples, attributes, 0)
        #tree.plot_tree("decision_tree.png")
        #tree.plot_interactive("arvore_interativa.html")
        return tree
    except Exception as e:
        print(f"[DT] Erro ao carregar dataset: {e}")
        return None


# ── Utilitários ─────────────────────────────────────────────────────────────────
def board_to_tuple(board):
    return tuple(tuple(row) for row in board)

def draw_draw_button(reason=""):
    font     = pygame.font.Font(None, 28)
    btn_text = f"Declare Draw ({reason})" if reason else "Declare Draw"
    text_surf = font.render(btn_text, True, (255, 255, 255))
    btn_w    = text_surf.get_width() + 20
    btn_h    = 34
    btn_x    = width - btn_w - 10
    btn_y    = (top_area - btn_h) // 2
    btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
    pygame.draw.rect(screen, (180, 60, 60), btn_rect, border_radius=8)
    screen.blit(text_surf, (btn_x + 10, btn_y + 7))
    return btn_rect


# ── Executar jogada de IA ───────────────────────────────────────────────────────
def ai_play(modo, board, jogador, root, dt_tree):
    """
    Executa a jogada da IA conforme o modo escolhido.
    Devolve (movimento, novo_root).
    """
    if modo == "dt":
        movimento = dt_play(board, dt_tree, jogador)
        legal = mcts_easy.get_legal_moves(board, jogador)
        if movimento not in legal:
            import random
            movimento = random.choice(legal) if legal else ("drop", 3)
        return movimento, None

    mcts = get_mcts(modo)

    if modo == "easy":
        movimento, novo_root = mcts.algoritmo_mcts(board, jogador, ITERACOES_EASY, root)
    else:
        movimento, novo_root = mcts.algoritmo_mcts(board, jogador, TEMPO[modo], root)

    return movimento, novo_root


# ── Menus ───────────────────────────────────────────────────────────────────────
def _draw_gradient():
    for i in range(height):
        c = (
            background[0] + int(i * (10 - background[0]) / height),
            background[1] + int(i * (20 - background[1]) / height),
            background[2] + int(i * (30 - background[2]) / height),
        )
        pygame.draw.line(screen, c, (0, i), (width, i))

def show_menu():
    font_title   = pygame.font.Font(None, 72)
    font_options = pygame.font.Font(None, 48)
    font_hover   = pygame.font.Font(None, 52)
    opcoes       = ["HUMAN vs HUMAN", "HUMAN vs AI", "AI vs AI"]
    clock        = pygame.time.Clock()
    resultado    = None

    while resultado is None:
        clock.tick(60)
        screen.fill(background)
        _draw_gradient()

        # Círculos decorativos
        for i in range(15):
            cx = (pygame.time.get_ticks() * 0.03 + i * 80) % (width + 100) - 50
            cy = (pygame.time.get_ticks() * 0.02 + i * 70) % (height + 100) - 50
            surf = pygame.Surface((100, 100), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*player1, 30 + i * 5), (50, 50), 40)
            screen.blit(surf, (cx, cy))

        # Título
        for offset, cor in [((4, 4), (50, 50, 50)), ((0, 0), (255, 255, 255))]:
            t = font_title.render("CONNECT 4", True, cor)
            screen.blit(t, t.get_rect(center=(width // 2 + offset[0], height // 4 - 10 + offset[1])))

        pygame.draw.line(screen, (255,255,255), (width//2-150, height//4+40), (width//2+150, height//4+40), 3)

        mx, my = pygame.mouse.get_pos()
        for i, opcao in enumerate(opcoes):
            y_pos = height // 2 + i * 80 - 40
            tw, th = font_options.size(opcao)
            rect  = pygame.Rect(width//2 - tw//2 - 20, y_pos - 20, tw + 40, th + 40)
            texto = (font_hover if rect.collidepoint(mx, my) else font_options).render(
                opcao, True, (255, 130, 60) if rect.collidepoint(mx, my) else (200, 200, 200))
            screen.blit(texto, texto.get_rect(center=(width // 2, y_pos)))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                for i, opcao in enumerate(opcoes):
                    y_pos = height // 2 + i * 80 - 40
                    tw, th = font_options.size(opcao)
                    rect  = pygame.Rect(width//2 - tw//2 - 20, y_pos - 20, tw + 40, th + 40)
                    if rect.collidepoint(x, y):
                        resultado = i + 1

    return resultado


def show_ai_selection_menu(titulo, player_num=None):
    """
    Menu de seleção de IA.
    Devolve: "easy", "medium", "hard" ou "dt"
    """
    font_title    = pygame.font.Font(None, 56)
    font_subtitle = pygame.font.Font(None, 36)
    font_options  = pygame.font.Font(None, 44)
    font_hover    = pygame.font.Font(None, 48)

    cor_jogador = player1 if player_num == 1 else player2 if player_num == 2 else (255, 255, 255)

    opcoes  = ["MCTS Fácil", "MCTS Médio", "MCTS Difícil", "Decision Tree"]
    valores = ["easy",       "medium",     "hard",          "dt"]
    clock   = pygame.time.Clock()
    choice  = None

    while choice is None:
        clock.tick(60)
        screen.fill(background)
        _draw_gradient()

        # Título
        t = font_title.render(titulo, True, (255, 255, 255))
        screen.blit(t, t.get_rect(center=(width // 2, height // 4 - 20)))

        if player_num is not None:
            sub = font_subtitle.render(f"Choose AI for Player {player_num}:", True, cor_jogador)
            screen.blit(sub, sub.get_rect(center=(width // 2, height // 4 + 35)))

        pygame.draw.line(screen, (255,255,255),
                         (width//2 - 220, height//4 + 60),
                         (width//2 + 220, height//4 + 60), 2)

        mx, my = pygame.mouse.get_pos()
        for i, opcao in enumerate(opcoes):
            y_pos = height // 2 + i * 80 - 80
            tw, th = font_options.size(opcao)
            rect  = pygame.Rect(width//2 - tw//2 - 20, y_pos - 20, tw + 40, th + 40)
            hover = rect.collidepoint(mx, my)
            texto = (font_hover if hover else font_options).render(
                opcao, True, cor_jogador if hover else (200, 200, 200))
            screen.blit(texto, texto.get_rect(center=(width // 2, y_pos)))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                for i, opcao in enumerate(opcoes):
                    y_pos = height // 2 + i * 80 - 80
                    tw, th = font_options.size(opcao)
                    rect  = pygame.Rect(width//2 - tw//2 - 20, y_pos - 20, tw + 40, th + 40)
                    if rect.collidepoint(x, y):
                        choice = valores[i]

    return choice


def show_end_popup(winner):
    overlay = pygame.Surface((width, height))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    popup_w, popup_h = 350, 150
    popup = pygame.Surface((popup_w, popup_h))
    popup.fill((40, 40, 60))
    pygame.draw.rect(popup, (100, 100, 120), popup.get_rect(), 3, border_radius=15)

    font = pygame.font.Font(None, 36)
    if winner == 1:
        txt, cor = "PLAYER 1 WINS!", player1
    elif winner == 2:
        txt, cor = "PLAYER 2 WINS!", player2
    else:
        txt, cor = "IT'S A TIE!", (255, 255, 255)

    t = font.render(txt, True, cor)
    popup.blit(t, t.get_rect(center=(popup_w // 2, popup_h // 2)))
    screen.blit(popup, ((width - popup_w) // 2, (height - popup_h) // 2))
    pygame.display.update()
    pygame.time.wait(2000)


# ── SETUP ───────────────────────────────────────────────────────────────────────
modo_jogo = show_menu()

ai_p1    = None
ai_p2    = None
ai_human = None   # modo Human vs AI
dt_tree  = None

if modo_jogo == 2:
    ai_human = show_ai_selection_menu("HUMAN vs AI")
    if ai_human == "dt":
        dt_tree = load_dt()

elif modo_jogo == 3:
    ai_p1 = show_ai_selection_menu("AI vs AI", player_num=1)
    ai_p2 = show_ai_selection_menu("AI vs AI", player_num=2)
    if ai_p1 == "dt" or ai_p2 == "dt":
        dt_tree = load_dt()

matrix         = iniciar_matrix()
running        = True
current_player = 1
mcts_root      = None   # Human vs AI
mcts_root_p1   = None   # AI vs AI jogador 1
mcts_root_p2   = None   # AI vs AI jogador 2
state_history  = {}

reuse_ok   = 0
reuse_fail = 0
turn       = 0
jogos      = 0
MAX        = 2


# ── LOOP PRINCIPAL ──────────────────────────────────────────────────────────────
while running:

    current_state            = board_to_tuple(matrix)
    repetition_draw_available = state_history.get(current_state, 0) >= 3
    full_board_draw_available = (board_is_full(matrix)
                                 and not check_victory(matrix, 1)
                                 and not check_victory(matrix, 2))

    # Empate automático AI vs AI
    if modo_jogo == 3 and (repetition_draw_available or full_board_draw_available):
        show_end_popup(0)
        matrix, current_player, _ = reset_game()
        mcts_root_p1 = None
        mcts_root_p2 = None
        state_history = {}
        turn = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and not (modo_jogo == 2 and current_player == 2) and not (modo_jogo == 3):
            x, y   = event.pos
            col    = x // cell_size
            jogada_feita = False

            if repetition_draw_available or full_board_draw_available:
                reason   = "R3" if repetition_draw_available else "R2"
                btn_rect = draw_draw_button(reason)
                if btn_rect.collidepoint(x, y):
                    show_end_popup(0)
                    running = False
                    break

            if y < top_area:
                if not col_isFull(matrix, col):
                    drop(matrix, current_player, col)
                    jogada_feita = True
            elif y > height - bottom_area:
                if check_pop(matrix, current_player, col):
                    pop(matrix, current_player, col)
                    jogada_feita = True

            if jogada_feita:
                state_history[board_to_tuple(matrix)] = state_history.get(board_to_tuple(matrix), 0) + 1

                mov_tuple = ("drop", col) if y < top_area else ("pop", col)

                # Atualizar root do MCTS (só se for modo MCTS)
                if ai_human and ai_human != "dt":
                    novo_root = get_mcts(ai_human).atualizar_root(mcts_root, mov_tuple)
                    mcts_root = novo_root if novo_root else None

                screen.fill(black)
                draw_board(matrix)
                pygame.display.update()

                venceu_atual    = check_victory(matrix, current_player)
                venceu_oponente = check_victory(matrix, 3 - current_player)

                if venceu_atual or venceu_oponente:
                    show_end_popup(current_player if venceu_atual else 3 - current_player)
                    running = False
                else:
                    current_player = 3 - current_player

    # ── AI moves ────────────────────────────────────────────────────────────────
    if running:

        # ── Modo 2: Human vs AI ──
        if modo_jogo == 2 and current_player == 2:

            if full_board_draw_available or repetition_draw_available:
                show_end_popup(0)
                running = False
            else:
                movimento, mcts_root = ai_play(ai_human, matrix, current_player, mcts_root, dt_tree)

                if movimento[0] == "drop":
                    drop(matrix, current_player, movimento[1])
                else:
                    pop(matrix, current_player, movimento[1])

                state_history[board_to_tuple(matrix)] = state_history.get(board_to_tuple(matrix), 0) + 1

                # Atualizar root após jogada da IA
                if ai_human and ai_human != "dt" and mcts_root is not None:
                    novo_root = get_mcts(ai_human).atualizar_root(mcts_root, movimento)
                    if novo_root:
                        reuse_ok += 1
                    else:
                        reuse_fail += 1
                    mcts_root = novo_root

                screen.fill(black)
                draw_board(matrix)
                pygame.display.update()

                venceu_atual    = check_victory(matrix, current_player)
                venceu_oponente = check_victory(matrix, 3 - current_player)

                if venceu_atual or venceu_oponente:
                    show_end_popup(current_player if venceu_atual else 3 - current_player)
                    running = False
                else:
                    current_player = 3 - current_player

        # ── Modo 3: AI vs AI ──
        elif modo_jogo == 3:

            screen.fill(black)
            draw_board(matrix)
            pygame.display.update()

            ai_atual = ai_p1 if current_player == 1 else ai_p2
            root_atual = mcts_root_p1 if current_player == 1 else mcts_root_p2

            movimento, novo_root = ai_play(ai_atual, matrix, current_player, root_atual, dt_tree)

            # Guardar root atualizado
            if current_player == 1:
                mcts_root_p1 = novo_root
            else:
                mcts_root_p2 = novo_root

            # Informar o root do outro jogador da jogada feita
            if current_player == 1 and mcts_root_p2 is not None and ai_p2 != "dt":
                mcts_root_p2 = get_mcts(ai_p2).atualizar_root(mcts_root_p2, movimento)
            elif current_player == 2 and mcts_root_p1 is not None and ai_p1 != "dt":
                mcts_root_p1 = get_mcts(ai_p1).atualizar_root(mcts_root_p1, movimento)

            if turn > 3 and ai_p1 != "dt" and ai_p2 != "dt":
                dataset.append(([row[:] for row in matrix], movimento))

            if movimento[0] == "drop":
                drop(matrix, current_player, movimento[1])
            else:
                pop(matrix, current_player, movimento[1])
            turn += 1

            state_history[board_to_tuple(matrix)] = state_history.get(board_to_tuple(matrix), 0) + 1

            screen.fill(black)
            draw_board(matrix)
            pygame.display.update()

            venceu_atual    = check_victory(matrix, current_player)
            venceu_oponente = check_victory(matrix, 3 - current_player)

            if venceu_atual or venceu_oponente:
                show_end_popup(current_player if venceu_atual else 3 - current_player)
                matrix, current_player, _ = reset_game()
                mcts_root_p1 = None
                mcts_root_p2 = None
                state_history = {}
                turn = 0
            else:
                current_player = 3 - current_player

        if jogos > MAX:
            running = False

    # ── Render ──────────────────────────────────────────────────────────────────
    if running:
        screen.fill(black)
        draw_board(matrix)

        if modo_jogo != 3:
            mx, my = pygame.mouse.get_pos()
            col    = mx // cell_size
            hl     = pygame.Surface((cell_size, ROWS * cell_size), pygame.SRCALPHA)
            hl.fill((255, 255, 255, 40))
            screen.blit(hl, (col * cell_size, top_area))

            if my < top_area and not (modo_jogo == 2 and current_player == 2):
                color = player1 if current_player == 1 else player2
                pygame.draw.circle(screen, color, (mx, top_area // 2), cell_size // 2 - 10)

            if repetition_draw_available or full_board_draw_available:
                reason = "R3" if repetition_draw_available else "R2"
                draw_draw_button(reason)

        pygame.display.update()


pygame.quit()

print("\n--- STATS ---")
print("Reuse OK:", reuse_ok)
print("Reuse FAIL:", reuse_fail)

file_exists = os.path.exists("dataset.csv")
with open("dataset.csv", "a", newline="") as f:
    fieldnames = [f"cell_{r}_{c}" for r in range(6) for c in range(7)] + ["label"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    if not file_exists:
        writer.writeheader()
    for estado, mov in dataset:
        row = {f"cell_{r}_{c}": str(estado[r][c]) for r in range(6) for c in range(7)}
        row["label"] = f"{mov[0]}_{mov[1]}"
        writer.writerow(row)