import pygame

pygame.init()

WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flood Fill Algorithm")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

def flood_fill(x, y, fill_color, boundary_color):
    if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
        return

    pixels = pygame.PixelArray(screen)

    fill_pixel = screen.map_rgb(fill_color)
    boundary_pixel = screen.map_rgb(boundary_color)

    if pixels[x, y] == boundary_pixel or pixels[x, y] == fill_pixel:
        del pixels
        return

    stack = [(x, y)]
    batch_size = 500

    while stack:
        for _ in range(batch_size):
            if not stack:
                break
            px, py = stack.pop()
            if not (0 <= px < WIDTH and 0 <= py < HEIGHT):
                continue
            current_color = pixels[px, py]
            if current_color == boundary_pixel or current_color == fill_pixel:
                continue
            pixels[px, py] = fill_pixel
            # Four-connected neighbours
            stack.append((px + 1, py))
            stack.append((px - 1, py))
            stack.append((px, py + 1))
            stack.append((px, py - 1))
        # Update display to show live filling
        del pixels
        pygame.display.flip()
        pygame.event.pump()
        pygame.time.delay(10)
        pixels = pygame.PixelArray(screen)

    del pixels

screen.fill(BLACK)

polygon = [
    (200, 150),
    (500, 150),
    (500, 350),
    (200, 350)
]

pygame.draw.polygon(screen, WHITE, polygon, 1)
pygame.display.flip()

flood_fill(350, 250, RED, WHITE)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
pygame.quit()