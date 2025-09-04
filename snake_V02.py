import pygame
import sys
import random

# ---------------- PARAMETRELER ----------------
CELL_SIZE = 20
GRID_WIDTH = 20
GRID_HEIGHT = 20
SIDE_PANEL_WIDTH = 180

SCREEN_WIDTH = CELL_SIZE * GRID_WIDTH + SIDE_PANEL_WIDTH
SCREEN_HEIGHT = CELL_SIZE * GRID_HEIGHT

BG_COLOR = (20, 20, 20)
GRID_COLOR = (50, 50, 50)
FRAME_COLOR = (180, 180, 180)
PANEL_BG_COLOR = (40, 40, 40)

BASE_FPS = 8
LEVEL_UP_YEM = 5

# ---------------- FONKSİYONLAR ----------------
def draw_grid(surface):
    for x in range(0, CELL_SIZE * GRID_WIDTH, CELL_SIZE):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, CELL_SIZE * GRID_HEIGHT))
    for y in range(0, CELL_SIZE * GRID_HEIGHT, CELL_SIZE):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (CELL_SIZE * GRID_WIDTH, y))

def draw_frame(surface):
    pygame.draw.rect(surface, FRAME_COLOR, (0, 0, CELL_SIZE*GRID_WIDTH, CELL_SIZE*GRID_HEIGHT), 3)

def gradient_color(start_color, end_color, t):
    """t: 0.0 -> start, 1.0 -> end"""
    return tuple(int(start + (end - start) * t) for start, end in zip(start_color, end_color))

def draw_snake(surface, snake, level):
    head_color = (102, 255, 178)
    tail_color = (0, 153, 102)
    # Seviye arttıkça renk biraz değişiyor
    head_color = gradient_color(head_color, (255, 255, 102), min((level-1)*0.1,1))
    tail_color = gradient_color(tail_color, (102, 255, 255), min((level-1)*0.1,1))

    for i, segment in enumerate(snake):
        t = i / len(snake)
        color = gradient_color(head_color, tail_color, t)
        pygame.draw.rect(surface, color, (segment[0]*CELL_SIZE, segment[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(surface, (0,0,0), (segment[0]*CELL_SIZE+2, segment[1]*CELL_SIZE+2, CELL_SIZE-4, CELL_SIZE-4), 1)

def draw_food(surface, food, effects):
    pygame.draw.rect(surface, (255, 102, 102), (food[0]*CELL_SIZE, food[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))
    # Yem efektleri
    for effect in effects[:]:
        alpha = int(255 * (effect["timer"] / effect["max_timer"]))
        s = pygame.Surface((CELL_SIZE*4, CELL_SIZE*4), pygame.SRCALPHA)
        pygame.draw.circle(s, (255,180,180, alpha), (CELL_SIZE*2, CELL_SIZE*2), effect["radius"], 3)
        surface.blit(s, (effect["pos"][0]-CELL_SIZE*2, effect["pos"][1]-CELL_SIZE*2))
        effect["radius"] += 1  # büyüt
        effect["timer"] -= 1
        if effect["timer"] <= 0:
            effects.remove(effect)

def random_food_position(snake):
    while True:
        pos = (random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1))
        if pos not in snake:
            return pos

def draw_text_center(surface, text_surf, y, x_offset=0):
    surface.blit(text_surf, (surface.get_width() // 2 - text_surf.get_width() // 2 + x_offset, y))

# ---------------- OYUN ----------------
def run_game(win, clock):
    snake = [(GRID_WIDTH//2, GRID_HEIGHT//2 + i) for i in range(3)]
    direction = (0, -1)
    food = random_food_position(snake)
    score = 0
    level = 1
    fps = BASE_FPS
    yem_sayaci = 0
    running = True

    font = pygame.font.SysFont("Arial", 24)
    food_effects = []  # Yem animasyon listesi

    while running:
        win.fill(BG_COLOR)
        # Oyun alanı
        draw_grid(win)
        draw_frame(win)
        draw_snake(win, snake, level)
        draw_food(win, food, food_effects)

        # Yan panel
        pygame.draw.rect(win, PANEL_BG_COLOR, (CELL_SIZE*GRID_WIDTH,0,SIDE_PANEL_WIDTH,SCREEN_HEIGHT))
        win.blit(font.render(f"Skor: {score}", True, (255,255,255)), (CELL_SIZE*GRID_WIDTH + 20, 50))
        win.blit(font.render(f"Seviye: {level}", True, (255,255,255)), (CELL_SIZE*GRID_WIDTH + 20, 100))
        win.blit(font.render(f"Hız: {fps}", True, (255,255,255)), (CELL_SIZE*GRID_WIDTH + 20, 150))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != (0,1):
                    direction = (0, -1)
                elif event.key == pygame.K_DOWN and direction != (0,-1):
                    direction = (0, 1)
                elif event.key == pygame.K_LEFT and direction != (1,0):
                    direction = (-1, 0)
                elif event.key == pygame.K_RIGHT and direction != (-1,0):
                    direction = (1, 0)

        # Yılan hareketi
        new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
        if new_head in snake or not (0 <= new_head[0] < GRID_WIDTH) or not (0 <= new_head[1] < GRID_HEIGHT):
            break
        snake.insert(0, new_head)

        # Yem kontrolü
        if new_head == food:
            score += 1
            yem_sayaci += 1
            food = random_food_position(snake)
            # Yeni efekt ekle
            food_effects.append({
                "pos": (new_head[0]*CELL_SIZE + CELL_SIZE//2, new_head[1]*CELL_SIZE + CELL_SIZE//2),
                "radius": CELL_SIZE//2,
                "timer": 15,
                "max_timer": 15
            })
            if yem_sayaci % LEVEL_UP_YEM == 0:
                level += 1
                fps += 2
        else:
            snake.pop()

        pygame.display.update()
        clock.tick(fps)

    return score

# ---------------- GAME OVER ----------------
def game_over_screen(win, clock, score):
    font_big = pygame.font.SysFont("Arial", 48)
    font_small = pygame.font.SysFont("Arial", 28)
    while True:
        win.fill(BG_COLOR)
        text = font_big.render("OYUN BİTTİ", True, (255,0,0))
        score_text = font_small.render(f"Skor: {score}", True, (255,255,255))
        prompt1 = font_small.render("R - Yeniden Başlat", True, (255,255,255))
        prompt2 = font_small.render("Q - Çıkış", True, (255,255,255))
        draw_text_center(win, text, SCREEN_HEIGHT//3)
        draw_text_center(win, score_text, SCREEN_HEIGHT//2)
        draw_text_center(win, prompt1, SCREEN_HEIGHT//2 + 50)
        draw_text_center(win, prompt2, SCREEN_HEIGHT//2 + 90)
        pygame.display.update()
        clock.tick(10)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return 'restart'
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

# ---------------- ANA ----------------
def main():
    pygame.init()
    win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Snake (Estetik & Animasyonlu)")
    clock = pygame.time.Clock()

    while True:
        score = run_game(win, clock)
        action = game_over_screen(win, clock, score)
        if action == 'restart':
            continue

if __name__ == "__main__":
    main()
