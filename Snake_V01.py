import pygame
import random
import sys

# ---------------- PARAMETRELER ----------------
BLOCK_SIZE = 20
GRID_WIDTH = 10
GRID_HEIGHT = 20

COLOR_MODE = 1
DRAW_GRID_LINES = True

FPS = 60
DROP_SPEED = 500
SPEED_PER_LEVEL = 70
MIN_FALL_SPEED = 20
FAST_DROP_FACTOR = 8
LEVEL_UP_DURATION_MS = 1500
LINE_CLEAR_EFFECT_MS = 200

# ---------------- EFECT AYARLARI ----------------
FAST_DROP_EFFECT = 1      # 1 = aktif, 0 = kapalı
LINE_CLEAR_EFFECT = 1     # 1 = normal satır silme efekti
COMBO_EFFECT = 1          # 1 = 4+ satır silme efekti

# ---------------- RENKLER ----------------
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
FRAME_COLOR = (180, 180, 180)

# Pastel renkler
COLORS = [
    (135, 206, 250),  # Light Sky Blue
    (100, 149, 237),  # Cornflower Blue
    (255, 182, 193),  # Light Pink
    (255, 239, 128),  # Pastel Yellow
    (144, 238, 144),  # Light Green
    (216, 191, 216),  # Thistle
    (255, 160, 122),  # Light Salmon
]

# ---------------- PARÇALAR ----------------
SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[0, 1, 0], [1, 1, 1]],
    [[1, 1, 0], [0, 1, 1]]
]

# ---------------- SINIFLAR ----------------
class Piece:
    def __init__(self, x, y, shape, color):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = color
        self.rotation = 0

    def image(self):
        return self.shape[self.rotation % len(self.shape)]

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.shape)

# ---------------- FONKSİYONLAR ----------------
def create_grid(locked):
    grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if (x, y) in locked:
                grid[y][x] = locked[(x, y)]
    return grid

def valid_space(piece, grid):
    accepted_positions = [[(x, y) for x in range(GRID_WIDTH) if grid[y][x] == BLACK] for y in range(GRID_HEIGHT)]
    accepted_positions = [x for sub in accepted_positions for x in sub]
    formatted = convert_shape_format(piece)
    return all((pos in accepted_positions or pos[1] < 0) for pos in formatted)

def convert_shape_format(piece):
    positions = []
    shape = piece.image()
    for i, line in enumerate(shape):
        for j, cell in enumerate(line):
            if cell:
                positions.append((piece.x + j, piece.y + i))
    return positions

def check_lost(locked):
    return any(y < 1 for (x, y) in locked)

def get_shape():
    idx = random.randrange(len(SHAPES))
    rotations = []
    shape = SHAPES[idx]
    for _ in range(4):
        rotations.append(shape)
        shape = list(zip(*shape[::-1]))
        shape = [list(row) for row in shape]
    return Piece(GRID_WIDTH // 2 - 2, 0, rotations, COLORS[idx])

def clear_rows(grid, locked):
    cleared_rows = [y for y in range(GRID_HEIGHT) if BLACK not in grid[y]]
    if not cleared_rows:
        return 0, locked, []
    new_locked = {}
    for (x, y), color in locked.items():
        if y in cleared_rows:
            continue
        shift = sum(1 for cy in cleared_rows if cy > y)
        new_locked[(x, y + shift)] = color
    return len(cleared_rows), new_locked, cleared_rows

def draw_grid(surface, grid):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            color = grid[y][x]
            if color != BLACK:
                pygame.draw.rect(surface, color if COLOR_MODE else WHITE,
                                 (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                if DRAW_GRID_LINES:
                    pygame.draw.rect(surface, GRAY,
                                     (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

def draw_next_shape(shape, surface, offset_x, offset_y):
    fmt = shape.image()
    for i, row in enumerate(fmt):
        for j, cell in enumerate(row):
            if cell:
                pygame.draw.rect(surface, shape.color if COLOR_MODE else WHITE,
                                 (offset_x + j * BLOCK_SIZE, offset_y + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                if DRAW_GRID_LINES:
                    pygame.draw.rect(surface, GRAY,
                                     (offset_x + j * BLOCK_SIZE, offset_y + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

def draw_text_center(surface, text_surf, y):
    surface.blit(text_surf, (surface.get_width() // 2 - text_surf.get_width() // 2, y))

def compute_fall_speed(level):
    return max(MIN_FALL_SPEED, DROP_SPEED - (level - 1) * SPEED_PER_LEVEL)

def draw_line_clear_effect(win, cleared_rows):
    if LINE_CLEAR_EFFECT == 0 and COMBO_EFFECT == 0:
        return
    for y in cleared_rows:
        overlay = pygame.Surface((GRID_WIDTH * BLOCK_SIZE, BLOCK_SIZE))
        overlay.set_alpha(180)
        if COMBO_EFFECT == 1 and len(cleared_rows) >= 4:
            overlay.fill((255, 215, 0))  # Altın sarısı combo efekti
        else:
            overlay.fill(WHITE)
        win.blit(overlay, (0, y * BLOCK_SIZE))
    pygame.display.update()
    pygame.time.delay(LINE_CLEAR_EFFECT_MS)

    # COMBO mesajı göster
    if COMBO_EFFECT == 1 and len(cleared_rows) >= 4:
        draw_combo_message(win)

def draw_combo_message(win):
    font = pygame.font.SysFont("Arial", 48, bold=True)
    text_surf = font.render("COMBO! Aferin...", True, (255, 215, 0))
    draw_text_center(win, text_surf, win.get_height() // 2)
    pygame.display.update()
    pygame.time.delay(1000)  # 1 saniye bekle

def draw_fast_drop_effect(win, piece):
    if FAST_DROP_EFFECT == 0:
        return
    effect_surf = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
    effect_surf.set_alpha(100)
    effect_surf.fill(WHITE)
    positions = convert_shape_format(piece)
    for x, y in positions:
        if y >= 0:
            win.blit(effect_surf, (x * BLOCK_SIZE, y * BLOCK_SIZE))
    pygame.display.update()
    pygame.time.delay(10)

# ---------------- OYUN ----------------
def run_game(win, clock, screen_width, screen_height, start_level=1, start_speed=None):
    fall_time = 0
    locked_positions = {}
    grid = create_grid(locked_positions)
    change_piece = False
    current_piece = get_shape()
    next_piece = get_shape()
    score = 0
    total_lines = 0
    level = start_level
    fall_speed = start_speed if start_speed else compute_fall_speed(level)
    show_level_up = False
    level_up_start = 0

    while True:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick(FPS)

        if fall_time >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit', score, level, fall_speed
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                if event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                if event.key == pygame.K_DOWN:
                    fall_speed = max(MIN_FALL_SPEED, compute_fall_speed(level) // FAST_DROP_FACTOR)
                if event.key == pygame.K_UP:
                    current_piece.rotate()
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = (current_piece.rotation - 1) % len(current_piece.shape)
                if event.key == pygame.K_SPACE:
                    while True:
                        current_piece.y += 1
                        if not valid_space(current_piece, grid):
                            current_piece.y -= 1
                            change_piece = True
                            break
                        draw_fast_drop_effect(win, current_piece)
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    fall_speed = compute_fall_speed(level)

        shape_pos = convert_shape_format(current_piece)
        for x, y in shape_pos:
            if y >= 0 and 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                locked_positions[pos] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            cleared, locked_positions, cleared_rows = clear_rows(grid, locked_positions)
            if cleared > 0:
                draw_line_clear_effect(win, cleared_rows)
                score += cleared * 100 * level
                total_lines += cleared
                new_level = total_lines // 10 + 1
                if new_level > level:
                    level = new_level
                    fall_speed = compute_fall_speed(level)
                    show_level_up = True
                    level_up_start = pygame.time.get_ticks()

        win.fill(BLACK)
        draw_grid(win, grid)

        pygame.draw.rect(win, FRAME_COLOR,
                         (0, 0, GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE), 2)
        pygame.draw.line(win, FRAME_COLOR,
                         (GRID_WIDTH * BLOCK_SIZE, 0),
                         (GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE), 2)

        font = pygame.font.SysFont("Arial", 20)
        base_x = GRID_WIDTH * BLOCK_SIZE + 20
        win.blit(font.render(f"Skor: {score}", True, WHITE), (base_x, 20))
        win.blit(font.render(f"Seviye: {level}", True, WHITE), (base_x, 60))
        win.blit(font.render(f"Hız: {fall_speed} ms", True, WHITE), (base_x, 100))
        win.blit(font.render("Sonraki:", True, WHITE), (base_x, 140))
        draw_next_shape(next_piece, win, base_x, 180)

        if show_level_up:
            now = pygame.time.get_ticks()
            if now - level_up_start <= LEVEL_UP_DURATION_MS:
                big_font = pygame.font.SysFont("Arial", 48, bold=True)
                up_surf = big_font.render("LEVEL UP!", True, WHITE)
                draw_text_center(win, up_surf, screen_height // 4)
            else:
                show_level_up = False

        pygame.display.update()

        if check_lost(locked_positions):
            return game_over_screen(win, score, level, fall_speed, screen_width, screen_height, clock)

# ---------------- GAME OVER ----------------
def game_over_screen(win, score, level, speed, screen_w, screen_h, clock):
    font_big = pygame.font.SysFont("Arial", 64)
    font_small = pygame.font.SysFont("Arial", 28)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit', 0, 1, None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return 'restart', 0, 1, None
                if event.key == pygame.K_c:
                    return 'continue', 0, level, speed
                if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    return 'quit', 0, 1, None

        overlay = pygame.Surface((screen_w, screen_h))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        win.blit(overlay, (0, 0))

        text = font_big.render("OYUN BİTTİ", True, WHITE)
        score_text = font_small.render(f"Skor: {score}", True, WHITE)
        level_text = font_small.render(f"Seviye: {level}", True, WHITE)
        speed_text = font_small.render(f"Hız: {speed} ms", True, WHITE)
        prompt1 = font_small.render("R - Yeniden Başlat", True, WHITE)
        prompt2 = font_small.render("C - Devam Et", True, WHITE)
        prompt3 = font_small.render("Q veya ESC - Çıkış", True, WHITE)

        draw_text_center(win, text, screen_h // 2 - 120)
        draw_text_center(win, score_text, screen_h // 2 - 40)
        draw_text_center(win, level_text, screen_h // 2)
        draw_text_center(win, speed_text, screen_h // 2 + 40)
        draw_text_center(win, prompt1, screen_h // 2 + 90)
        draw_text_center(win, prompt2, screen_h // 2 + 130)
        draw_text_center(win, prompt3, screen_h // 2 + 170)

        pygame.display.update()
        clock.tick(10)

# ---------------- ANA ----------------
def main():
    pygame.init()
    side_panel_width = 120
    screen_width = GRID_WIDTH * BLOCK_SIZE + side_panel_width
    screen_height = GRID_HEIGHT * BLOCK_SIZE
    win = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Tetris (Geliştirilmiş)")

    clock = pygame.time.Clock()
    start_level = 1
    start_speed = None
    while True:
        result, score, level, speed = run_game(win, clock, screen_width, screen_height, start_level, start_speed)
        if result == 'quit':
            break
        elif result == 'restart':
            start_level = 1
            start_speed = None
        elif result == 'continue':
            start_level = level
            start_speed = speed
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
