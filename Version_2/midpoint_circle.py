import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Midpoint Circle Drawing Algorithm")

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

def midpoint(xc, yc, r):
    p = 1 - r
    x = 0
    y = r
    while x <= y:
        draw_circle_points(xc, yc, x, y)
        xk2 = 2 * x + 2
        yk2 = 2 * y - 2
        x += 1
        if p < 0:
            p = p + xk2 + 1
        else:
            y -= 1
            p = p + xk2 + 1 - yk2

def main():
    xc = int(input("Enter center x-coordinate (xc): "))
    yc = int(input("Enter center y-coordinate (yc): "))
    r = int(input("Enter radius: "))
    if r <= 0:
        print("Radius must be greater than zero.")
        pygame.quit()
        sys.exit()

    screen.fill(BLACK)
    midpoint(xc, yc, r)
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