import pygame
import sys

pygame.init()

x1 = int(input("Enter x1: "))
y1 = int(input("Enter y1: "))
x2 = int(input("Enter x2: "))
y2 = int(input("Enter y2: "))

dx = x2 - x1
dy = y2 - y1
p = 2 * dy - dx
x = x1
y = y1

width = 800
height = 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Bresenham's Line Drawing Algorithm")

screen.fill((255, 255, 255))

while x < x2:
    x += 1

    if p < 0:
        p = p + 2 * dy
    else:
        y += 1
        p = p + 2 * dy - 2 * dx

    pygame.draw.rect(screen, (255, 0, 0), (x, y, 1, 1))

pygame.display.update()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
sys.exit()