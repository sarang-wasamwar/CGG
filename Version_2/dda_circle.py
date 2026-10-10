import pygame
import sys
import math

pygame.init()

WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DDA Circle Drawing Algorithm")

BLACK = (0, 0, 0)
RED = (255, 0, 0)

def draw_circle_points(xc, yc, x, y):
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
            screen.set_at((px, py), RED)

def dda(xc, yc, r):
    x = 0.0
    y = float(r)
    val = 0
    while 2 ** val < r:
        val += 1
    eps = 1.0 / (2 ** val)
    while x <= y:
        draw_circle_points(
            xc, yc,
            int(x + 0.5),
            int(y + 0.5)
        )
        x_new = x + eps * y
        y_new = y - eps * x_new
        x = x_new
        y = y_new

def main():
    screen.fill(BLACK)
    xc = int(input("Enter center x-coordinate (xc): "))
    yc = int(input("Enter center y-coordinate (yc): "))
    r = int(input("Enter radius: "))
    if r <= 0:
        print("Radius must be greater than zero.")
        pygame.quit()
        sys.exit()

    dda(xc, yc, r)
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