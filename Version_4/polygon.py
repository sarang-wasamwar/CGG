import pygame

pygame.init()
WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flood Fill Algorithm - Live Animation")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Input
n = int(input("Enter number of vertices: "))
polygon = []
for i in range(n):
    x, y = map(int, input(f"Enter vertex {i + 1} (x y): ").split())
    polygon.append((x, y))

seed_x, seed_y = map(int, input("Enter seed point (x y): ").split())
print("\n1. Red")
print("2. Blue")
print("3. Green")
print("4. Yellow")
choice = int(input("Enter fill color: "))
colors = {
    1: RED,
    2: BLUE,
    3: GREEN,
    4: YELLOW
}
fill_color = colors.get(choice, RED)
boundary_color = WHITE

# DRAW POLYGON
screen.fill(BLACK)
pygame.draw.polygon(screen, boundary_color, polygon, 1)
pygame.display.flip()

# FLOOD FILL
def flood_fill(x, y, fill_color, boundary_color):
    if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
        print("Seed point is outside the screen!")
        return
    fill_pixel = screen.map_rgb(fill_color)
    boundary_pixel = screen.map_rgb(boundary_color)
    pixels = pygame.PixelArray(screen)
    if pixels[x, y] == boundary_pixel:
        del pixels
        print("Seed point lies on the boundary!")
        return
    if pixels[x, y] == fill_pixel:
        del pixels
        return
    stack = [(x, y)]
    count = 0
    batch_size = 500
    running = True
    while stack and running:
        # Process a small batch of pixels
        for _ in range(batch_size):
            if not stack:
                break
            px, py = stack.pop()
            if not (0 <= px < WIDTH and 0 <= py < HEIGHT):
                continue
            current = pixels[px, py]
            if current == boundary_pixel or current == fill_pixel:
                continue
            pixels[px, py] = fill_pixel
            count += 1
            # Four-connected neighbours
            stack.append((px + 1, py))
            stack.append((px - 1, py))
            stack.append((px, py + 1))
            stack.append((px, py - 1))
        # Release pixel access so the display can update
        del pixels
        pygame.display.flip()
        # Keep the window responsive
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        if running:
            pygame.time.delay(10)
            pixels = pygame.PixelArray(screen)
    if running:
        del pixels
    else:
        # Release the surface lock when exiting
        del pixels
    print("Pixels filled:", count)

flood_fill(seed_x, seed_y, fill_color, boundary_color)

# KEEP WINDOW OPEN
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
pygame.quit()
