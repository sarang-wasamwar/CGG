import pygame
import sys

# Initialization
pygame.init()

WIDTH = 800
HEIGHT = 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Race Track - Bresenham Algorithms")

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
LIGHTGRAY = (200, 200, 200)
YELLOW = (255, 255, 0)
clock = pygame.time.Clock()

# Matrix Translation
def multiply(points, T):
    """
    Multiply a row-vector point [x, y, 1] by a 3x3 matrix.
    This follows the same matrix convention as the original C++ code.
    """
    result = [0.0, 0.0, 0.0]
    for j in range(3):
        for k in range(3):
            result[j] += points[k] * T[k][j]
    for j in range(3):
        points[j] = result[j]

def apply_matrix_translation(point, tx, ty):
    T = [
        [1,  0,  0],
        [0,  1,  0],
        [tx, ty, 1]
    ]
    multiply(point, T)

# Bresenham Line Algorithm
def bresenham_line(x1, y1, x2, y2, color):
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy
    while True:
        if 0 <= x1 < WIDTH and 0 <= y1 < HEIGHT:
            screen.set_at((x1, y1), color)
        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy

# Bresenham Circle Algorithm
def bresenham_circle(xc, yc, r, color):
    x = 0
    y = r
    d = 3 - 2 * r
    while y >= x:
        points = [
            (xc + x, yc + y),
            (xc - x, yc + y),
            (xc + x, yc - y),
            (xc - x, yc - y),
            (xc + y, yc + x),
            (xc - y, yc + x),
            (xc + y, yc - x),
            (xc - y, yc - x)
        ]
        for px, py in points:
            if 0 <= px < WIDTH and 0 <= py < HEIGHT:
                screen.set_at((int(px), int(py)), color)
        if d < 0:
            d = d + 4 * x + 6
        else:
            d = d + 4 * (x - y) + 10
            y -= 1
        x += 1

# Track and Objects
def draw_track():
    # Outer road border
    bresenham_line(80, 160, 700, 160, WHITE)
    bresenham_line(80, 300, 700, 300, WHITE)
    bresenham_line(80, 160, 80, 300, WHITE)
    bresenham_line(700, 160, 700, 300, WHITE)

    # Lane separators
    bresenham_line(80, 195, 700, 195, LIGHTGRAY)
    bresenham_line(80, 230, 700, 230, LIGHTGRAY)
    bresenham_line(80, 265, 700, 265, LIGHTGRAY)

    # Finish line
    bresenham_line(700, 160, 700, 300, YELLOW)

def draw_runner(x, y, color):
    # Draw concentric circles, as in the original C++ program
    for r in range(7, -1, -1):
        bresenham_circle(x, y, r, color)

def draw_coin(x, y):
    bresenham_circle(x, y, 8, YELLOW)

# Main Program
def main():
    # Each point is [x, y, 1], matching the C++ homogeneous coordinates
    player_point = [100.0, 195.0, 1.0]
    blue_player = [100.0, 230.0, 1.0]
    green_player = [100.0, 265.0, 1.0]

    red_speed = 3.0
    blue_speed = 2.0
    green_speed = 1.5

    finish_line = 700
    coin_x = [220, 320, 420, 520, 620]

    running = True

    while running:
        # Allow the window to close normally
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        screen.fill(BLACK)
        draw_track()

        # Draw five coins in each of the three lanes
        for x in coin_x:
            draw_coin(x, 195)
            draw_coin(x, 230)
            draw_coin(x, 265)

        red_x = int(player_point[0])
        blue_x = int(blue_player[0])
        green_x = int(green_player[0])

        draw_runner(red_x, 195, RED)
        draw_runner(blue_x, 230, BLUE)
        draw_runner(green_x, 265, GREEN)

        pygame.display.flip()
        pygame.time.delay(10)

        # Move each runner until it reaches the finish line
        if red_x < finish_line:
            apply_matrix_translation(player_point, red_speed, 0.0)
        if blue_x < finish_line:
            apply_matrix_translation(blue_player, blue_speed, 0.0)
        if green_x < finish_line:
            apply_matrix_translation(green_player, green_speed, 0.0)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
