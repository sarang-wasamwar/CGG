import pygame
import sys

pygame.init()

x1 = float(input("Enter x1: "))
y1 = float(input("Enter y1: "))
x2 = float(input("Enter x2: "))
y2 = float(input("Enter y2: "))

dx = x2 - x1
dy = y2 - y1

length = max(abs(dx), abs(dy))

if length != 0:
    x_inc = dx / length
    y_inc = dy / length
else:
    x_inc = 0
    y_inc = 0

width = 800
height = 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("DDA Line Drawing Algorithm")

screen.fill((255, 255, 255))

i = 0
while i < length:
    pygame.draw.rect(
        screen,
        (255, 255, 0),
        (round(x1), round(y1), 1, 1)
    )
    x1 = x1 + x_inc
    y1 = y1 + y_inc
    if round(x1) == round(x2) and round(y1) == round(y2):
        break
    i += 1

pygame.display.update()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
sys.exit()