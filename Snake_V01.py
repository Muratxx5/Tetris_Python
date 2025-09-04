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

# Estetik renkler
SNAKE_HEAD_COLOR = (102, 255, 178)   # Açık yeşil
SNAKE_BODY_COLOR = (0, 153, 102)     # Koyu yeşil
FOOD_COLOR = (255, 102, 102)         # Canlı kırmızı
BG_COLOR = (20, 20, 20)              # Koyu gri
GRID_COLOR = (50, 50, 50)            # Yumuşak grid
FRAME_COLOR = (180, 180, 180)        # Çerçeve
PANEL_BG_COLOR = (40, 40, 40)        # Yan panel

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

def draw_snake(surface, snake):
    for i, segment in enumerate(snake):
        color = SNAKE_HEAD_COLOR if i == 0 else SNAKE_BODY_COLOR
        pygame.draw.rect(surface, color, (segment[0]*CELL_SIZE, segment[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))
        # Hafif iç gölge
        pygame.draw.rect(surface, (0,0,0,50), (segment[0]*CELL_SIZE+2, segment[1]*CELL_SIZE+2, CELL_SIZE-4, CELL_SIZE-4), 1)

def draw_food(surface, food):
    pygame.draw.rect(surface, FOOD_COLOR, (food[0]*CELL_SIZE, food[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))
    # Parlama efekti
    pygame.draw.circle(surface, (255,180,180), (food[0]*CELL_SIZE+CELL_SIZE//2, food[1]*CELL_SIZE+CELL_SIZE//2), CELL_SIZE//2, 2)

def random_food_position(snake):
    while True:
        pos = (random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1))
        if pos not in snake:
            return pos

def draw_text_center(surface, text_surf, y, x_offset=0):
    surface.blit(text_surf, (surface.get_width() // 2 - text_surf.get_width() // 2 + x_offset, y))

# ---------------- OYUN ----------------
def run_game(win, clock):
    # Başlangıç yılanı 3 blok
    snake = [(GRID_WIDTH//2, GRID_HEIGHT//2 + i) for i in range(3)]
    direction = (0, -1)
    food = random_food_position(snake)
    score = 0
    level = 1
    fps = BASE_FPS
    yem_sayaci = 0
    running = True

    font = pygame.font.SysFont("Arial", 24)

    while running:
        win.fill(BG_COLOR)
        # Oyun alanı
        draw_grid(win)
        draw_frame(win)
        draw_snake(win, snake)
        draw_food(win, food)

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

        # Çarpma kontrolü
        if new_head in snake or not (0 <= new_head[0] < GRID_WIDTH) or not (0 <= new_head[1] < GRID_HEIGHT):
            break

        snake.insert(0, new_head)

        # Yem kontrolü
        if new_head == food:
            score += 1
            yem_sayaci += 1
            food = random_food_position(snake)
            # Seviye artışı
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
    pygame.display.set_caption("Snake (Estetik)")
    clock = pygame.time.Clock()

    while True:
        score = run_game(win, clock)
        action = game_over_screen(win, clock, score)
        if action == 'restart':
            continue

if __name__ == "__main__":
    main()
