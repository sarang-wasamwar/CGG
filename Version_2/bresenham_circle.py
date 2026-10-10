import pygame
import sys

pygame.init()

WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Midpoint Circle Drawing Algorithm")

BLACK = (0, 0, 0)
MAGENTA = (255, 0, 255)

OriginX = 0
OriginY = 0

def set_origin_to_center():
    global OriginX, OriginY
    OriginX = WIDTH // 2
    OriginY = HEIGHT // 2

def putpixel_center(x, y, color):
    screen_x = OriginX + x
    screen_y = OriginY - y

    if 0 <= screen_x < WIDTH and 0 <= screen_y < HEIGHT:
        screen.set_at((screen_x, screen_y), color)

def draw_full_circle_points(x, y, color):
    putpixel_center(x, y, color)
    putpixel_center(-x, y, color)
    putpixel_center(-x, -y, color)
    putpixel_center(x, -y, color)

def main():
    screen.fill(BLACK)

    set_origin_to_center()

    xc = int(input("Enter center x-coordinate (xc): "))
    yc = int(input("Enter center y-coordinate (yc): "))
    radius = int(input("Enter radius: "))

    if radius <= 0:
        print("Radius must be greater than zero.")
        pygame.quit()
        sys.exit()

    x = 0
    y = radius

    g_delta = 2 * (1 - y)
    s_delta = 0
    limit = 0

    draw_full_circle_points(x, y, MAGENTA)

    while y > limit:

        if g_delta < 0:
            s_delta = 2 * g_delta + 2 * y - 1

            if s_delta <= 0:
                x += 1
                g_delta += 2 * x + 1
            else:
                x += 1
                y -= 1
                g_delta += 2 * x - 2 * y + 2

        elif g_delta > 0:
            s_delta = 2 * g_delta - 2 * x - 1

            if s_delta <= 0:
                x += 1
                y -= 1
                g_delta += 2 * x - 2 * y + 2
            else:
                y -= 1
                g_delta += 1 - 2 * y

        else:
            x += 1
            y -= 1
            g_delta += 2 * x - 2 * y + 2

        draw_full_circle_points(x, y, MAGENTA)

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