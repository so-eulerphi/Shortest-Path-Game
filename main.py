import pygame
import sys
import random
import os

pygame.init()

TILE_SIZE = 60
ROWS, COLS = 10, 10
WIDTH = COLS * TILE_SIZE
HEIGHT = ROWS * TILE_SIZE + 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Info Projekt 2026 - Sophie")
font = pygame.font.SysFont(None, 28)

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS # tmp Speicherort nach PyInstaller Einpacken
    except AttributeError:
        base_path = os.path.abspath(".") # falls kein PyInstaller-Einpacken

    return os.path.join(base_path, relative_path)

# Bilder
def load_tile(filename):
    img = pygame.image.load(get_resource_path(filename)).convert_alpha()
    return pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))


tile_images = {
    0: load_tile('empty.png'),
    1: load_tile('obstacle.png'),
    2: load_tile('path.png'),
    3: load_tile('ship.png'),
    4: load_tile('warehouse.png')
}

# GVariablen
grid = []
is_drawing = False
path_cells = []
currency = 0
level = 1
message = "Bringe das Schiff auf kürzestem Wege zum Warenhaus!"
optimal_steps = 0

# methode
def get_shortest_path_length(start_r, start_c, target_r, target_c):  # breitensuche mit start und end koordinaten,
    queue = [(start_r, start_c, 0)] # Inhalt: (Zeile (r), Spalte (c), Kosten)
    visited = set()
    visited.add((start_r, start_c))

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while queue:
        current_r, current_c, dist = queue.pop(0)

        # sobald wir angekommen sind, return kosten
        if (current_r, current_c) == (target_r, target_c):
            return dist

        for dr, dc in directions:
            next_r, next_c = current_r + dr, current_c + dc

            if 0 <= next_r < ROWS and 0 <= next_c < COLS:
                #
                if grid[next_r][next_c] in [0, 4] and (next_r, next_c) not in visited:
                    visited.add((next_r, next_c))
                    queue.append((next_r, next_c, dist + 1))

    # None, falls unmöglich
    return None


def generate_random_level():
    global grid, path_cells, optimal_steps
    path_cells.clear()

    while True:
        grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]

        w_row, w_col = random.randint(0, ROWS - 1), random.randint(0, COLS - 1)
        grid[w_row][w_col] = 3

        while True:
            s_row, s_col = random.randint(0, ROWS - 1), random.randint(0, COLS - 1)
            distance = abs(s_row - w_row) + abs(s_col - w_col)
            if distance >= 4:
                grid[s_row][s_col] = 4
                break

        num_obstacles = min(15 + (level * 2), 40)
        obstacles_placed = 0

        while obstacles_placed < num_obstacles:
            o_row, o_col = random.randint(0, ROWS - 1), random.randint(0, COLS - 1)
            if grid[o_row][o_col] == 0:
                grid[o_row][o_col] = 1
                obstacles_placed += 1

        # kürzester weg nach breitensuche
        shortest_length = get_shortest_path_length(w_row, w_col, s_row, s_col)

        # falls es einen pfad gibt: kürzeste länge speichern, loop abbrechen
        if shortest_length is not None:
            optimal_steps = shortest_length
            break

# frontend
def draw_grid():
    for row in range(ROWS):
        for col in range(COLS):
            val = grid[row][col]
            image_to_draw = tile_images[val]
            screen.blit(image_to_draw, (col * TILE_SIZE, row * TILE_SIZE))

            rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, BLACK, rect, 1)


def clear_path():
    global path_cells
    for r, c in path_cells:
        if grid[r][c] == 2:
            grid[r][c] = 0
    path_cells.clear()


def is_adjacent(r1, c1, r2, c2):
    return abs(r1 - r2) + abs(c1 - c2) == 1


# Spiel-Loop
generate_random_level()
clock = pygame.time.Clock()

while True:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            col, row = x // TILE_SIZE, y // TILE_SIZE

            if row < ROWS and col < COLS:
                if grid[row][col] == 3:
                    clear_path()
                    is_drawing = True
                    path_cells.append((row, col))
                    message = f"Level {level}: Target = {optimal_steps} steps."

        elif event.type == pygame.MOUSEMOTION and is_drawing:
            x, y = pygame.mouse.get_pos()
            col, row = x // TILE_SIZE, y // TILE_SIZE

            if row < ROWS and col < COLS:
                last_r, last_c = path_cells[-1]

                if (row, col) != (last_r, last_c) and is_adjacent(row, col, last_r, last_c):
                    if grid[row][col] == 0:
                        grid[row][col] = 2
                        path_cells.append((row, col))
                    elif grid[row][col] == 4:
                        is_drawing = False
                        path_cells.append((row, col))
                        # Bedingung: kürzester weg, minus 1 exklusive start am warenhaus
                        player_steps = len(path_cells) - 1

                        if player_steps == optimal_steps:
                            # kürzeste route
                            earned = 50 + (level * 10)
                            currency += earned
                            level += 1
                            message = f"Perfekt! Punkte: {earned}. Lvl {level}..."
                            generate_random_level()
                        else:
                            # zu lange route
                            message = f"Suboptimal! Deine Schritte: {player_steps}. Ziel: {optimal_steps}."
                            clear_path()

        elif event.type == pygame.MOUSEBUTTONUP:
            if is_drawing:
                is_drawing = False
                message = "Route inkomplett."
                clear_path()

    draw_grid()

    pygame.draw.rect(screen, BLACK, (0, ROWS * TILE_SIZE, WIDTH, 60))
    ui_text = font.render(message, True, WHITE)
    currency_text = font.render(f"Credits: {currency} | Lvl: {level}", True, GREEN)

    screen.blit(ui_text, (10, ROWS * TILE_SIZE + 10))
    screen.blit(currency_text, (10, ROWS * TILE_SIZE + 35))

    pygame.display.flip()
    clock.tick(60)
