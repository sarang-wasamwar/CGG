"""
Example Inputs:
Enter number of points: 3
Point 1: 100 100
Point 2: 200 100
Point 3: 150 200

Enter choice: 1
Enter translation factors (tx and ty): 50 30
"""

import pygame
import sys
import math

pygame.init()

# Window Setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Transformations")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (120, 120, 120)

PI = 3.1416

# Display Points
def display_points(points):
    print("\nTransformed Points:")
    print("X\t\tY")
    for x, y in points:
        print(f"{x:.2f}\t\t{y:.2f}")

# Matrix Multiplication
def multiply(points, T):
    result = []
    for x, y in points:
        new_x = x * T[0][0] + y * T[1][0] + T[2][0]
        new_y = x * T[0][1] + y * T[1][1] + T[2][1]
        result.append((new_x, new_y))
    return result

# Translation
def translate(points):
    tx, ty = map(
                    float,
                    input("Enter translation factors (tx ty): ").split()
                )
    T = [
        [1, 0, 0],
        [0, 1, 0],
        [tx, ty, 1]
    ]
    result = multiply(points, T)
    display_points(result)
    return result

# Scaling
def scale(points):
    sx, sy = map(
        float,
        input("Enter scaling factors (sx and sy): ").split()
    )
    S = [
        [sx, 0, 0],
        [0, sy, 0],
        [0, 0, 1]
    ]
    result = multiply(points, S)
    display_points(result)
    return result

# Rotation
def rotate(points):
    theta = float(input("Enter rotation angle (degrees): "))
    print("1. Counterclockwise")
    print("2. Clockwise")
    choice = int(input("Enter choice: "))

    if choice not in (1, 2):
        print("Invalid rotation choice.")
        return points
    rad = theta * PI / 180.0

    if choice == 1:
        R = [
            [math.cos(rad), math.sin(rad), 0],
            [-math.sin(rad), math.cos(rad), 0],
            [0, 0, 1]
        ]
    else:
        R = [
            [math.cos(rad), -math.sin(rad), 0],
            [math.sin(rad), math.cos(rad), 0],
            [0, 0, 1]
        ]
    result = multiply(points, R)
    display_points(result)
    return result

# Composite Transformation
def composite(points):
    sequence = input(
        "\nEnter transformation sequence (T, R, S), e.g. TRS: "
    ).upper()
    result = points[:]

    for ch in sequence:
        if ch == 'T':
            tx, ty = map(
                float,
                input("Enter translation factors (tx ty): ").split()
            )
            T = [
                [1, 0, 0],
                [0, 1, 0],
                [tx, ty, 1]
            ]
            result = multiply(result, T)
        elif ch == 'R':
            theta = float(input("Enter rotation angle (degrees): "))
            print("1. Counterclockwise")
            print("2. Clockwise")
            choice = int(input("Enter choice: "))
            if choice not in (1, 2):
                print("Invalid rotation choice.")
                return points
            rad = theta * PI / 180.0
            if choice == 1:
                R = [
                    [math.cos(rad), math.sin(rad), 0],
                    [-math.sin(rad), math.cos(rad), 0],
                    [0, 0, 1]
                ]
            else:
                R = [
                    [math.cos(rad), -math.sin(rad), 0],
                    [math.sin(rad), math.cos(rad), 0],
                    [0, 0, 1]
                ]
            result = multiply(result, R)
        elif ch == 'S':
            sx, sy = map(
                float,
                input("Enter scaling factors (sx sy): ").split()
            )
            S = [
                [sx, 0, 0],
                [0, sy, 0],
                [0, 0, 1]
            ]
            result = multiply(result, S)
        else:
            print(f"Invalid transformation: {ch}")
            return points
    print("\nFinal result after composite transformations:")
    display_points(result)
    return result

# DDA Line Algorithm
def dda_line(x1, y1, x2, y2, color):
    dx = x2 - x1
    dy = y2 - y1
    steps = int(max(abs(dx), abs(dy)))
    if steps == 0:
        if 0 <= x1 < WIDTH and 0 <= y1 < HEIGHT:
            screen.set_at((x1, y1), color)
        return
    x_inc = dx / steps
    y_inc = dy / steps
    x = float(x1)
    y = float(y1)
    for _ in range(steps + 1):
        px = round(x)
        py = round(y)
        if 0 <= px < WIDTH and 0 <= py < HEIGHT:
            screen.set_at((px, py), color)
        x += x_inc
        y += y_inc

# Draw Shape
def draw_shape(points, color):
    if not points:
        return
    screen_points = [
        (WIDTH // 2 + round(x), HEIGHT // 2 - round(y))
        for x, y in points
    ]
    if len(screen_points) == 1:
        x, y = screen_points[0]
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            pygame.draw.circle(screen, color, (x, y), 3)
        return
    for i in range(len(screen_points)):
        x1, y1 = screen_points[i]
        x2, y2 = screen_points[(i + 1) % len(screen_points)]
        dda_line(x1, y1, x2, y2, color)

# Draw Coordinate Axes
def draw_axes():
    # X-axis and Y-axis
    dda_line(0, HEIGHT // 2, WIDTH - 1, HEIGHT // 2, GRAY)
    dda_line(WIDTH // 2, 0, WIDTH // 2, HEIGHT - 1, GRAY)

# Main Program
def main():
    n = int(input("Enter number of points: "))
    if n <= 0:
        print("Number of points must be greater than zero.")
        pygame.quit()
        sys.exit()
    
    points = []

    print("Enter points (X and Y), separated by a space:")
    for i in range(n):
        x, y = map(
            float,
            input(f"Point {i + 1}: ").split()
        )
        points.append((x, y))
    transformed_points = points[:]

    while True:
        print("\n===== 2D Transformations =====")
        print("1. Translation")
        print("2. Scaling")
        print("3. Rotation")
        print("4. Composite Transformation")
        print("5. Reset to Original")
        print("6. Exit")
        ch = int(input("Enter choice: "))

        if ch == 1:
            transformed_points = translate(points[:])
        elif ch == 2:
            transformed_points = scale(points[:])
        elif ch == 3:
            transformed_points = rotate(points[:])
        elif ch == 4:
            transformed_points = composite(points[:])
        elif ch == 5:
            transformed_points = points[:]
            print("Shape reset to original points.")
        elif ch == 6:
            break
        else:
            print("Invalid choice.")
            continue

        screen.fill(BLACK)
        draw_axes()
        draw_shape(points, WHITE)
        draw_shape(transformed_points, RED)
        pygame.display.flip()
        print("\nWhite: Original shape")
        print("Red: Transformed shape")
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        waiting = False
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
