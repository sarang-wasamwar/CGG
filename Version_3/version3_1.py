import pygame
import math
import random
import time

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racing Game - Computer Graphics")

clock = pygame.time.Clock()

PLAYER_SPEED = 180.0
BACKWARD_SPEED = 180.0
CAMERA_SMOOTH = 8.0
LANE_OFFSET = 55
ROAD_HALF_WIDTH = 90

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
LIGHTGRAY = (180, 180, 180)
DARKGRAY = (80, 80, 80)

font = pygame.font.SysFont("Arial", 18)
user_position = 80.0
computer1_position = 80.0
computer2_position = 80.0
camera_x = 0.0
camera_y = 0.0
score = 0

# MATRIX TRANSFORMATION
def multiply(point, matrix):
    result = [0.0, 0.0, 0.0]
    for j in range(3):
        for k in range(3):
            result[j] += point[k] * matrix[k][j]
    point[:] = result

def apply_translation(point, tx, ty):
    matrix = [
        [1, 0, 0],
        [0, 1, 0],
        [tx, ty, 1]
    ]
    multiply(point, matrix)

# PIXEL DRAWING
def put_pixel(x, y, color):
    if 0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT:
        screen.set_at((x, y), color)

# BRESENHAM LINE ALGORITHM
def bresenham_line(x1, y1, x2, y2, color):
    x1, y1 = int(x1), int(y1)
    x2, y2 = int(x2), int(y2)
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy
    while True:
        put_pixel(x1, y1, color)
        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy

# BRESENHAM CIRCLE ALGORITHM
def bresenham_circle(xc, yc, radius, color):
    x = 0
    y = radius
    d = 3 - 2 * radius
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
            put_pixel(int(px), int(py), color)
        if d < 0:
            d += 4 * x + 6
        else:
            d += 4 * (x - y) + 10
            y -= 1
        x += 1

def filled_circle(x, y, radius, color):
    pygame.draw.circle(screen, color, (int(x), int(y)), radius)

# ROAD SEGMENTS
class Segment:
    def __init__(self, x1, y1, x2, y2, length, direction):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.length = length
        self.direction = direction

SEGMENT_COUNT = 8
road = [
    Segment(0, 300, 800, 300, 800, 0),
    Segment(800, 300, 800, 650, 350, 1),
    Segment(800, 650, 1600, 650, 800, 0),
    Segment(1600, 650, 1600, 250, 400, 1),
    Segment(1600, 250, 2500, 250, 900, 0),
    Segment(2500, 250, 2500, 650, 400, 1),
    Segment(2500, 650, 3400, 650, 900, 0),
    Segment(3400, 650, 3400, 250, 400, 1)
]

def total_road_length():
    return sum(segment.length for segment in road)

# ROAD POSITION
def get_road_position(position):
    remaining = position
    for segment in road:
        if remaining <= segment.length:
            ratio = remaining / segment.length
            x = segment.x1 + (segment.x2 - segment.x1) * ratio
            y = segment.y1 + (segment.y2 - segment.y1) * ratio
            return x, y, segment.direction
        remaining -= segment.length
    last = road[-1]
    return last.x2, last.y2, last.direction

def get_player_world_position(position, lane):
    x, y, direction = get_road_position(position)
    if lane == 0:
        offset = -LANE_OFFSET
    elif lane == 1:
        offset = 0
    else:
        offset = LANE_OFFSET
    if direction == 0:
        y += offset
    else:
        x += offset
    return x, y

# WORLD TO SCREEN TRANSFORMATION
def world_to_screen(world_x, world_y):
    point = [world_x, world_y, 1]
    apply_translation(point, -camera_x, -camera_y)
    return int(point[0]), int(point[1])

# ROAD DRAWING
def draw_road_line(position1, offset1, position2, offset2, color):
    x1, y1, direction1 = get_road_position(position1)
    x2, y2, direction2 = get_road_position(position2)
    if direction1 == 0:
        y1 += offset1
    else:
        x1 += offset1
    if direction2 == 0:
        y2 += offset2
    else:
        x2 += offset2
    sx1, sy1 = world_to_screen(x1, y1)
    sx2, sy2 = world_to_screen(x2, y2)
    bresenham_line(sx1, sy1, sx2, sy2, color)

def draw_road():
    start = max(0.0, user_position - 750)
    end = min(total_road_length(), user_position + 1200)
    p = start
    while p < end:
        next_p = min(p + 5, end)
        draw_road_line(
            p, -ROAD_HALF_WIDTH,
            next_p, -ROAD_HALF_WIDTH,
            LIGHTGRAY
        )
        draw_road_line(p, 0, next_p, 0, DARKGRAY)
        draw_road_line(
            p, ROAD_HALF_WIDTH,
            next_p, ROAD_HALF_WIDTH,
            LIGHTGRAY
        )
        p += 5

# START LINE
def draw_start_line():
    x, y, direction = get_road_position(80)
    sx, sy = world_to_screen(x, y)
    if direction == 0:
        bresenham_line(
            sx, sy - ROAD_HALF_WIDTH,
            sx, sy + ROAD_HALF_WIDTH,
            GREEN
        )
    else:
        bresenham_line(
            sx - ROAD_HALF_WIDTH, sy,
            sx + ROAD_HALF_WIDTH, sy,
            GREEN
        )
    text = font.render("START", True, GREEN)
    screen.blit(text, (sx - 35, sy - 120))

# PLAYER DRAWING
def draw_player(position, lane, color):
    x, y = get_player_world_position(position, lane)
    sx, sy = world_to_screen(x, y)
    filled_circle(sx, sy, 8, color)

# COINS
COIN_COUNT = 15
coins = []

def create_coins():
    global coins
    coins = [350 + i * 230 for i in range(COIN_COUNT)]

def draw_coins():
    for coin_position in coins:
        x, y = get_player_world_position(coin_position, 1)
        sx, sy = world_to_screen(x, y)
        bresenham_circle(sx, sy, 8, YELLOW)

def collect_coins():
    global score
    for i in range(COIN_COUNT):
        if abs(coins[i] - user_position) < 15:
            score += 10
            coins[i] = user_position + 1500

# MOVING OBSTACLES
class Obstacle:
    def __init__(self, position):
        self.position = position
        self.offset = -100
        self.speed = random.randint(70, 109)
        self.moving_down = True

OBSTACLE_COUNT = 6
obstacles = []

def create_obstacles():
    global obstacles
    obstacles = [
        Obstacle(600 + i * 500)
        for i in range(OBSTACLE_COUNT)
    ]

def update_obstacle(obstacle, dt):
    if obstacle.moving_down:
        obstacle.offset += obstacle.speed * dt
        if obstacle.offset >= 100:
            obstacle.offset = 100
            obstacle.moving_down = False
    else:
        obstacle.offset -= obstacle.speed * dt
        if obstacle.offset <= -100:
            obstacle.offset = -100
            obstacle.moving_down = True

def draw_obstacle(obstacle):
    x, y, direction = get_road_position(obstacle.position)
    if direction == 0:
        y += obstacle.offset
    else:
        x += obstacle.offset

    sx, sy = world_to_screen(x, y)
    if direction == 0:
        bresenham_line(sx, sy - 22, sx, sy + 22, RED)
        bresenham_line(sx - 4, sy - 22, sx - 4, sy + 22, RED)
    else:
        bresenham_line(sx - 22, sy, sx + 22, sy, RED)
        bresenham_line(sx - 22, sy - 4, sx + 22, sy - 4, RED)

# HUD
def draw_hud():
    coin_text = font.render(f"COINS: {score}", True, WHITE)
    screen.blit(coin_text, (20, 25))
    forward_text = font.render("RIGHT = FORWARD", True, WHITE)
    screen.blit(forward_text, (500, 25))
    backward_text = font.render("LEFT = BACKWARD", True, WHITE)
    screen.blit(backward_text, (500, 45))

# Main Game Loop
def main():
    global user_position
    global computer1_position
    global computer2_position
    global camera_x
    global camera_y
    create_coins()
    create_obstacles()
    user_position = 80.0
    computer1_position = 80.0
    computer2_position = 80.0
    start_x, start_y, _ = get_road_position(user_position)
    camera_x = start_x - 200
    camera_y = start_y - 300
    running = True
    while running:
        dt = clock.tick(200) / 1000.0
        dt = min(dt, 0.05)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            user_position += PLAYER_SPEED * dt
        elif keys[pygame.K_LEFT]:
            user_position -= BACKWARD_SPEED * dt

        user_position = max(80.0, user_position)
        end_position = total_road_length() - 50
        user_position = min(user_position, end_position)
        computer1_position = min(
            computer1_position + PLAYER_SPEED * dt,
            end_position
        )
        computer2_position = min(
            computer2_position + PLAYER_SPEED * dt,
            end_position
        )

        # Smooth camera movement
        user_x, user_y = get_player_world_position(
            user_position, 1
        )
        target_camera_x = user_x - 200
        target_camera_y = user_y - 300
        camera_x += (
            target_camera_x - camera_x
        ) * CAMERA_SMOOTH * dt
        camera_y += (
            target_camera_y - camera_y
        ) * CAMERA_SMOOTH * dt

        # Update obstacles
        for obstacle in obstacles:
            update_obstacle(obstacle, dt)
        collect_coins()
        # Render the game
        screen.fill(BLACK)
        draw_road()
        if user_position < 500:
            draw_start_line()
        draw_coins()
        for obstacle in obstacles:
            draw_obstacle(obstacle)
        draw_player(computer1_position, 0, BLUE)
        draw_player(user_position, 1, RED)
        draw_player(computer2_position, 2, GREEN)

        draw_hud()
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()