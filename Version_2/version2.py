import pygame
import sys
import math

pygame.init()

# Window Setup
WIDTH, HEIGHT = 800, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Race Track - Bresenham Algorithms")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
LIGHTGRAY = (200, 200, 200)

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)

# Bresenham Line Algorithm
def bresenham_line(x1, y1, x2, y2, color):
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
                screen.set_at((px, py), color)

        if d < 0:
            d += 4 * x + 6
        else:
            d += 4 * (x - y) + 10
            y -= 1
        x += 1


# Draw Race Track
def draw_track():
    bresenham_line(80, 160, 700, 160, WHITE)
    bresenham_line(80, 300, 700, 300, WHITE)

    bresenham_line(80, 160, 80, 300, WHITE)
    bresenham_line(700, 160, 700, 300, WHITE)

    bresenham_line(80, 205, 700, 205, LIGHTGRAY)
    bresenham_line(80, 235, 700, 235, LIGHTGRAY)
    bresenham_line(80, 265, 700, 265, LIGHTGRAY)

    bresenham_line(700, 160, 700, 300, YELLOW)

# Draw Runner
def draw_runner(x, y, color):
    pygame.draw.ellipse(
        screen, color,
        (x - 7, y - 7, 14, 14)
    )

# Draw Coin
def draw_coin(x, y):
    bresenham_circle(x, y, 8, YELLOW)

# Collision Detection
def collision(x1, y1, x2, y2):
    dist = math.sqrt(
        (x2 - x1) ** 2 + (y2 - y1) ** 2
    )
    return dist < 15

# Main Program
def main():
    # Fixed player positions (no movement)
    playerX, playerY = 100, 205
    blueX, blueY = 100, 235
    greenX, greenY = 100, 265
    # Coins
    coinX = [220, 330, 430, 520, 600, 650]
    coinTaken = [False] * 6
    score = 0
    running = True

    while running:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
    
        # Draw track
        draw_track()
        # Draw coins
        for i in range(6):
            if not coinTaken[i]:
                draw_coin(coinX[i], playerY)
        # Draw stationary players
        draw_runner(playerX, playerY, RED)
        draw_runner(blueX, blueY, BLUE)
        draw_runner(greenX, greenY, GREEN)

        # Coin collection check
        for i in range(6):
            if not coinTaken[i]:
                if collision(
                    playerX, playerY,
                    coinX[i], playerY
                ):
                    coinTaken[i] = True
                    score += 1

        # Display score
        score_text = font.render(
            f"Coins: {score}", True, YELLOW
        )
        screen.blit(score_text, (20, 20))
        pygame.display.flip()
        clock.tick(30)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()