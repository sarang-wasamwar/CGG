import pygame
import sys

pygame.init()

WIDTH = 800
HEIGHT = 500

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Race Track - Bresenham Line Algorithm")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
LIGHTGRAY = (200, 200, 200)

def bresenham_line(x1, y1, x2, y2, color):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1

    err = dx - dy

    while True:
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


def draw_track():

    # Outer white borders
    bresenham_line(80, 120, 700, 120, WHITE)
    bresenham_line(80, 380, 700, 380, WHITE)

    # Left border
    bresenham_line(80, 120, 40, 180, WHITE)
    bresenham_line(40, 180, 40, 320, WHITE)
    bresenham_line(40, 320, 80, 380, WHITE)

    # Right border
    bresenham_line(700, 120, 740, 180, WHITE)
    bresenham_line(740, 180, 740, 320, WHITE)
    bresenham_line(740, 320, 700, 380, WHITE)

    # Three grey running lane lines
    bresenham_line(80, 190, 700, 190, LIGHTGRAY)
    bresenham_line(80, 250, 700, 250, LIGHTGRAY)
    bresenham_line(80, 310, 700, 310, LIGHTGRAY)

    bresenham_line(700, 120, 700, 380, YELLOW)


def draw_runner(x, y, color):
    pygame.draw.circle(screen, color, (x, y), 8)


def main():
    screen.fill(BLACK)

    draw_track()

    draw_runner(100, 190, RED)
    draw_runner(100, 250, BLUE)
    draw_runner(100, 310, GREEN)

    pygame.display.flip()

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
