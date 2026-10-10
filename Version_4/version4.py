import math
import random
import pygame

# Python Pygame conversion of the supplied graphics.h racing game.
# Colors, dimensions, speeds, road layout, coin positions and obstacle positions
# follow the original C++ program.

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

PLAYER_SPEED = 210.0
AI_SPEED = 205.0
MAX_REVERSE = 70.0
ROAD_WIDTH = 180.0
ROAD_HALF_WIDTH = 90.0
LANE_WIDTH = 60.0
START_POSITION = 0.0
COIN_RADIUS = 12
COIN_COLLECT_DISTANCE = 28.0

# Approximate BGI palette colors, kept consistent with the C++ color names.
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 170, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
LIGHTRED = (255, 85, 85)
DARKGRAY = (85, 85, 85)
LIGHTGRAY = (170, 170, 170)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Fun Race & Parkour")
clock = pygame.time.Clock()

FONT_SMALL = pygame.font.SysFont("consolas", 18)
FONT_MEDIUM = pygame.font.SysFont("consolas", 24)
FONT_LARGE = pygame.font.SysFont("consolas", 32, bold=True)
FONT_TITLE = pygame.font.SysFont("consolas", 40, bold=True)


def draw_text(text, x, y, color=WHITE, font=FONT_MEDIUM, center=False, surface=None):
    if surface is None:
        surface = screen
    image = font.render(str(text), True, color)
    rect = image.get_rect()
    if center:
        rect.center = (int(x), int(y))
    else:
        rect.topleft = (int(x), int(y))
    surface.blit(image, rect)


def bresenham_line(x1, y1, x2, y2, color):
    """Bresenham line algorithm, matching the original helper."""
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy
    while True:
        if 0 <= x1 < SCREEN_WIDTH and 0 <= y1 < SCREEN_HEIGHT:
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


def bresenham_circle(cx, cy, radius, color):
    """Bresenham midpoint circle algorithm."""
    x = 0
    y = int(radius)
    d = 3 - 2 * radius
    while x <= y:
        points = [
            (cx + x, cy + y), (cx - x, cy + y),
            (cx + x, cy - y), (cx - x, cy - y),
            (cx + y, cy + x), (cx - y, cy + x),
            (cx + y, cy - x), (cx - y, cy - x),
        ]
        for px, py in points:
            if 0 <= px < SCREEN_WIDTH and 0 <= py < SCREEN_HEIGHT:
                screen.set_at((int(px), int(py)), color)
        if d < 0:
            d += 4 * x + 6
        else:
            d += 4 * (x - y) + 10
            y -= 1
        x += 1


def flood_fill_circle(cx, cy, radius, fill_color, border_color):
    # Draw the same filled-circle appearance as BGI floodfill, without doing a
    # costly per-pixel flood fill every frame.
    pygame.draw.circle(screen, fill_color, (int(cx), int(cy)), int(radius))
    bresenham_circle(int(cx), int(cy), int(radius), border_color)


class Point:
    def __init__(self, x=0.0, y=0.0):
        self.x = float(x)
        self.y = float(y)


class Obstacle:
    def __init__(self, position, speed, side):
        self.position = float(position)
        self.speed = float(speed)
        self.offset = -ROAD_HALF_WIDTH + 25 if side == 1 else ROAD_HALF_WIDTH - 25
        self.direction = 1 if side == 1 else -1

    def update(self, dt):
        self.offset += self.speed * self.direction * dt
        limit = ROAD_HALF_WIDTH - 25
        if self.offset >= limit:
            self.offset = limit
            self.direction = -1
        if self.offset <= -limit:
            self.offset = -limit
            self.direction = 1


class Coin:
    def __init__(self, position, lane):
        self.position = float(position)
        self.lane = int(lane)
        self.collected = False


class Racer:
    def __init__(self, name, color, lane, is_player, ai_speed, reaction, risk):
        self.name = name
        self.color = color
        self.lane = lane
        self.is_player = is_player
        self.aiSpeed = float(ai_speed)
        self.reaction = float(reaction)
        self.risk = float(risk)
        self.reset()

    def reset(self):
        self.position = START_POSITION
        self.checkpoint = START_POSITION
        self.speed = 0.0
        self.finished = False
        self.finishTime = 0.0
        self.hasFinishTime = False
        self.collisionCount = 0
        self.stunTimer = 0.0


road_points = []
road_distances = []
road_tangents = []
obstacles = []
coins = []
racers = []
road_total_length = 0.0
finish_position = 0.0
camera_x = 0.0
camera_y = 0.0
race_time = 0.0
user_position = 0.0
race_started = False
menu_active = True
coin_count = 0
current_level = 2
winner_index = -1


def rotate_vector(x, y, degrees):
    a = math.radians(degrees)
    return Point(x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a))


def create_road():
    global road_points, road_distances, road_tangents, road_total_length
    road_points = [Point(0, 350)]
    road_distances = []
    road_tangents = []
    heading = 0.0
    x = 0.0
    y = 350.0
    step = 10.0
    types = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
    values = [650, 90, 650, -90, 800, -90, 650, 90, 850, 90, 650, -90, 800, -90, 750]

    for v in range(15):
        if types[v] == 0:
            count = int(values[v] / step)
            for _ in range(count):
                d = rotate_vector(step, 0, heading)
                x += d.x
                y += d.y
                road_points.append(Point(x, y))
        else:
            turn_angle = values[v]
            radius = 180.0
            arc_length = radius * math.pi * abs(turn_angle) / 180.0
            count = max(2, int(arc_length / step))
            angle_step = turn_angle / count
            for _ in range(count):
                d = rotate_vector(step, 0, heading)
                x += d.x
                y += d.y
                road_points.append(Point(x, y))
                heading += angle_step

    road_distances.append(0.0)
    total = 0.0
    for i in range(len(road_points)):
        if i == 0:
            dx = road_points[1].x - road_points[0].x
            dy = road_points[1].y - road_points[0].y
        elif i == len(road_points) - 1:
            dx = road_points[i].x - road_points[i - 1].x
            dy = road_points[i].y - road_points[i - 1].y
        else:
            dx = road_points[i + 1].x - road_points[i - 1].x
            dy = road_points[i + 1].y - road_points[i - 1].y
        length = math.sqrt(dx * dx + dy * dy)
        road_tangents.append(Point(1, 0) if length == 0 else Point(dx / length, dy / length))
        if i > 0:
            sx = road_points[i].x - road_points[i - 1].x
            sy = road_points[i].y - road_points[i - 1].y
            total += math.sqrt(sx * sx + sy * sy)
            road_distances.append(total)
    road_total_length = total


def get_road_position(position):
    position = max(0.0, min(float(position), road_total_length))
    for i in range(1, len(road_distances)):
        if position <= road_distances[i]:
            previous = road_distances[i - 1]
            segment = road_distances[i] - previous
            ratio = 0 if segment == 0 else (position - previous) / segment
            x = road_points[i - 1].x + (road_points[i].x - road_points[i - 1].x) * ratio
            y = road_points[i - 1].y + (road_points[i].y - road_points[i - 1].y) * ratio
            t = road_tangents[i]
            return x, y, t.x, t.y
    p = road_points[-1]
    t = road_tangents[-1]
    return p.x, p.y, t.x, t.y


def get_world_position(position, offset):
    px, py, tx, ty = get_road_position(position)
    nx = -ty
    ny = tx
    return px + nx * offset, py + ny * offset


def world_to_screen(x, y):
    return int(x - camera_x), int(y - camera_y)


def draw_road():
    screen.fill(GREEN)
    start = 0
    end = len(road_points) - 1
    center_x = camera_x + SCREEN_WIDTH / 2.0
    center_y = camera_y + SCREEN_HEIGHT / 2.0
    nearest = 0.0
    best = 1e30
    for i in range(0, len(road_points), 5):
        dx = road_points[i].x - center_x
        dy = road_points[i].y - center_y
        d = dx * dx + dy * dy
        if d < best:
            best = d
            nearest = road_distances[i]
    while start < end and road_distances[start] < nearest - 900:
        start += 1
    while end > start and road_distances[end] > nearest + 1400:
        end -= 1

    for i in range(start, end):
        p1, p2 = road_points[i], road_points[i + 1]
        t1, t2 = road_tangents[i], road_tangents[i + 1]
        lx1, ly1 = p1.x - t1.y * ROAD_HALF_WIDTH, p1.y + t1.x * ROAD_HALF_WIDTH
        rx1, ry1 = p1.x + t1.y * ROAD_HALF_WIDTH, p1.y - t1.x * ROAD_HALF_WIDTH
        lx2, ly2 = p2.x - t2.y * ROAD_HALF_WIDTH, p2.y + t2.x * ROAD_HALF_WIDTH
        rx2, ry2 = p2.x + t2.y * ROAD_HALF_WIDTH, p2.y - t2.x * ROAD_HALF_WIDTH
        polygon = [world_to_screen(lx1, ly1), world_to_screen(rx1, ry1),
                   world_to_screen(rx2, ry2), world_to_screen(lx2, ly2)]
        pygame.draw.polygon(screen, DARKGRAY, polygon)

    for i in range(start, end, 2):
        p = road_points[i]
        t = road_tangents[i]
        lx, ly = p.x - t.y * ROAD_HALF_WIDTH, p.y + t.x * ROAD_HALF_WIDTH
        rx, ry = p.x + t.y * ROAD_HALF_WIDTH, p.y - t.x * ROAD_HALF_WIDTH
        pygame.draw.line(screen, LIGHTGRAY, world_to_screen(lx, ly), world_to_screen(rx, ry), 1)

    position = road_distances[start]
    while position < road_distances[end]:
        dash_end = min(position + 35, road_distances[end])
        for lane in (-1, 1):
            p = position
            while p <= dash_end:
                wx, wy = get_world_position(p, lane * LANE_WIDTH / 2.0)
                sx, sy = world_to_screen(wx, wy)
                if 0 <= sx < SCREEN_WIDTH and 0 <= sy < SCREEN_HEIGHT:
                    screen.set_at((sx, sy), WHITE)
                p += 4
        position += 70


def draw_frame():
    pygame.draw.rect(screen, WHITE, (4, 4, SCREEN_WIDTH - 8, SCREEN_HEIGHT - 8), 1)


def draw_menu():
    screen.fill(GREEN)
    pygame.draw.rect(screen, DARKGRAY, (150, 0, 700, SCREEN_HEIGHT))
    pygame.draw.line(screen, LIGHTGRAY, (150, 0), (150, SCREEN_HEIGHT), 3)
    pygame.draw.line(screen, LIGHTGRAY, (850, 0), (850, SCREEN_HEIGHT), 3)
    draw_text("FUN RACE & PARKOUR", 500, 65, WHITE, FONT_TITLE, center=True)
    draw_text("SELECT LEVEL", 500, 125, YELLOW, FONT_LARGE, center=True)
    names = ["LEVEL 1", "LEVEL 2", "LEVEL 3"]
    desc = ["STRAIGHT ROAD", "CURVED ROAD", "PARKOUR ROAD"]
    colors = [GREEN, BLUE, RED]
    y = 200
    for i in range(3):
        pygame.draw.rect(screen, BLACK, (250, y, 500, 85))
        pygame.draw.rect(screen, colors[i], (250, y, 500, 85), 2)
        pygame.draw.rect(screen, colors[i], (252, y + 2, 496, 81), 1)
        draw_text(names[i], 275, y + 12, colors[i], FONT_LARGE)
        draw_text(desc[i], 275, y + 51, WHITE, FONT_MEDIUM)
        draw_text(str(i + 1), 705, y + 25, YELLOW, FONT_LARGE)
        y += 110
    draw_text("Press 1, 2 or 3 to select a level", 500, 575, WHITE, FONT_MEDIUM, center=True)
    draw_text("ESC - Quit", 500, 615, WHITE, FONT_MEDIUM, center=True)


def create_coins():
    global coins
    coins = []
    positions = [350, 500, 650, 800, 950, 1100, 1250, 1400, 1550, 1700,
                 1850, 2000, 2150, 2300, 2450, 2600, 2750, 2900, 3050, 3200,
                 3350, 3500, 3650, 3800, 3950, 4100, 4250, 4400, 4550, 4700]
    for position in positions:
        if position < road_total_length - 100:
            coins.append(Coin(position, 0))


def draw_coin(coin):
    if coin.collected:
        return
    x, y = get_world_position(coin.position, coin.lane * LANE_WIDTH)
    sx, sy = world_to_screen(x, y)
    if sx < -20 or sx > SCREEN_WIDTH + 20 or sy < -20 or sy > SCREEN_HEIGHT + 20:
        return
    flood_fill_circle(sx, sy, COIN_RADIUS, YELLOW, LIGHTRED)
    bresenham_circle(sx, sy, COIN_RADIUS - 4, LIGHTRED)
    bresenham_circle(sx - 4, sy - 4, 3, WHITE)


def create_obstacles():
    global obstacles
    obstacles = []
    positions = [650, 1250, 1900, 2550, 3200, 3850, 4500, 5150, 5800, 6450]
    for i, position in enumerate(positions):
        speed = 55 + random.randrange(31)
        obstacles.append(Obstacle(position, speed, 1 if i % 2 == 0 else -1))


def draw_obstacle(ob):
    x, y = get_world_position(ob.position, ob.offset)
    sx, sy = world_to_screen(x, y)
    if sx < -60 or sx > SCREEN_WIDTH + 60 or sy < -60 or sy > SCREEN_HEIGHT + 60:
        return
    pygame.draw.rect(screen, LIGHTRED, (sx - 40, sy - 25, 80, 50))
    pygame.draw.rect(screen, BLACK, (sx - 40, sy - 25, 80, 50), 1)
    pygame.draw.rect(screen, RED, (sx - 28, sy - 14, 56, 28))
    pygame.draw.line(screen, WHITE, (sx - 20, sy), (sx + 20, sy), 1)


def draw_racer(position, lane, color, player):
    x, y = get_world_position(position, 0 if player else lane * LANE_WIDTH)
    sx, sy = world_to_screen(x, y)
    if sx < -30 or sx > SCREEN_WIDTH + 30 or sy < -30 or sy > SCREEN_HEIGHT + 30:
        return
    radius = 16 if player else 15
    flood_fill_circle(sx, sy, radius, color, BLACK)
    bresenham_circle(sx, sy, 11 if player else 10, WHITE)


def obstacle_collision(racer):
    rx, ry = get_world_position(racer.position, racer.lane * LANE_WIDTH)
    for obstacle in obstacles:
        if abs(racer.position - obstacle.position) > 60:
            continue
        ox, oy = get_world_position(obstacle.position, obstacle.offset)
        if math.hypot(rx - ox, ry - oy) < 52:
            return True
    return False


def update_checkpoint(racer):
    cp = math.floor(racer.position / 900.0) * 900.0
    if cp > racer.checkpoint:
        racer.checkpoint = cp


def handle_collision(racer):
    if racer.finished:
        return
    if obstacle_collision(racer):
        racer.position = max(START_POSITION, racer.checkpoint - 15)
        racer.speed = 0
        racer.stunTimer = 0.65
        racer.collisionCount += 1


def nearest_obstacle_ahead(position):
    nearest = 1e30
    index = -1
    for i, obstacle in enumerate(obstacles):
        d = obstacle.position - position
        if 0 < d < nearest:
            nearest = d
            index = i
    return index


def update_ai(racer, dt):
    if racer.finished:
        return
    if racer.stunTimer > 0:
        racer.stunTimer -= dt
        return
    obstacle_index = nearest_obstacle_ahead(racer.position)
    target_speed = racer.aiSpeed
    if obstacle_index >= 0:
        obstacle = obstacles[obstacle_index]
        distance = obstacle.position - racer.position
        relative_offset = abs(obstacle.offset)
        if racer.risk < 0.5:
            if distance < 350 and relative_offset < 55: target_speed = 120
            if distance < 200 and relative_offset < 60: target_speed = 65
            if distance < 100 and relative_offset < 65: target_speed = 35
        else:
            if distance < 250 and relative_offset < 45: target_speed = 170
            if distance < 130 and relative_offset < 50: target_speed = 110
            if distance < 70 and relative_offset < 55: target_speed = 50
    if racer.speed < target_speed:
        racer.speed = min(target_speed, racer.speed + 400 * racer.reaction * dt)
    elif racer.speed > target_speed:
        racer.speed = max(target_speed, racer.speed - 500 * racer.reaction * dt)
    racer.position = min(finish_position, racer.position + racer.speed * dt)
    update_checkpoint(racer)
    handle_collision(racer)


def collect_coins(racer):
    global coin_count
    if not racer.is_player:
        return
    px, py = get_world_position(racer.position, racer.lane * LANE_WIDTH)
    for coin in coins:
        if coin.collected:
            continue
        cx, cy = get_world_position(coin.position, coin.lane * LANE_WIDTH)
        if math.hypot(px - cx, py - cy) < COIN_COLLECT_DISTANCE:
            coin.collected = True
            coin_count += 1


def draw_race_marker(position, label, color):
    x, y, tx, ty = get_road_position(position)
    nx, ny = -ty, tx
    p1 = world_to_screen(x + nx * ROAD_HALF_WIDTH, y + ny * ROAD_HALF_WIDTH)
    p2 = world_to_screen(x - nx * ROAD_HALF_WIDTH, y - ny * ROAD_HALF_WIDTH)
    pygame.draw.line(screen, color, p1, p2, 1)
    sx, sy = world_to_screen(x, y)
    draw_text(label, sx - 35, sy - int(ROAD_HALF_WIDTH) - 25, color, FONT_MEDIUM)


def draw_hud():
    pygame.draw.rect(screen, BLACK, (0, 0, SCREEN_WIDTH, 105))
    draw_text("Fun Race & Parkour", 10, 12, WHITE, FONT_LARGE)
    draw_text(f"TIME: {race_time:05.1f}s", 370, 20, YELLOW, FONT_MEDIUM)
    draw_text(f"COINS: {coin_count}", 700, 20, YELLOW, FONT_MEDIUM)
    draw_text("RIGHT: ACCELERATE   LEFT: BRAKE / REVERSE   ESC: QUIT", 10, 52, WHITE, FONT_SMALL)
    for i, racer in enumerate(racers):
        progress = int(racer.position / finish_position * 100) if finish_position > 0 else 0
        progress = min(progress, 100)
        draw_text(f"{racer.name}: {progress:3d}%", 10 + i * 150, 82, racer.color, FONT_SMALL)


def draw_finish_results():
    if winner_index < 0:
        return
    pygame.draw.rect(screen, BLACK, (150, 130, 700, 490))
    winner = racers[winner_index]
    draw_text(f"{winner.name} WINS!", 500, 180, winner.color, FONT_TITLE, center=True)
    order = sorted(range(len(racers)), key=lambda i: racers[i].finishTime if racers[i].hasFinishTime else 999999)
    for i, r_index in enumerate(order):
        racer = racers[r_index]
        if racer.hasFinishTime:
            result = f"{i + 1}. {racer.name}   {racer.finishTime:.2f}s   Hits: {racer.collisionCount}"
        else:
            result = f"{i + 1}. {racer.name}   --   Hits: {racer.collisionCount}"
        draw_text(result, 280, 250 + i * 50, racer.color, FONT_MEDIUM)
    draw_text("Press R to race again", 330, 430, WHITE, FONT_MEDIUM)
    draw_text("Press M to return to menu", 330, 470, WHITE, FONT_MEDIUM)
    draw_text("Press ESC to quit", 330, 510, WHITE, FONT_MEDIUM)


def reset_race():
    global race_time, race_started, winner_index, coin_count, user_position, camera_x, camera_y
    for racer in racers:
        racer.reset()
    create_obstacles()
    create_coins()
    race_time = 0.0
    race_started = False
    winner_index = -1
    coin_count = 0
    user_position = START_POSITION
    sx, sy, _, _ = get_road_position(START_POSITION)
    camera_x = sx - 250
    camera_y = sy - 350


def setup_racers():
    global racers
    racers = [
        Racer("YOU", RED, 0, True, AI_SPEED, 1.0, 0.5),
        Racer("BLUE", BLUE, -1, False, 215, 0.55, 0.25),
        Racer("GREEN", GREEN, 1, False, 215, 0.75, 0.25),
    ]


def start_level(level):
    global current_level, finish_position, menu_active
    current_level = level
    # The supplied C++ startLevel() calls createRoad() identically for all levels.
    create_road()
    finish_position = road_total_length - 80
    reset_race()
    menu_active = False


def main():
    global finish_position, menu_active, race_started, race_time, user_position
    global camera_x, camera_y, winner_index
    setup_racers()
    create_road()
    finish_position = road_total_length - 80
    reset_race()
    menu_active = True
    running = True

    while running:
        dt = min(clock.tick(FPS) / 1000.0, 0.05)
        right_pressed = False
        left_pressed = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif menu_active:
                    if event.key == pygame.K_1:
                        start_level(1)
                    elif event.key == pygame.K_2:
                        start_level(2)
                    elif event.key == pygame.K_3:
                        start_level(3)
                else:
                    if event.key in (pygame.K_r,) and winner_index >= 0:
                        reset_race()
                    elif event.key == pygame.K_m:
                        menu_active = True
                        winner_index = -1
                        race_started = False

        if not running:
            break

        if menu_active:
            draw_menu()
            pygame.display.flip()
            continue

        keys = pygame.key.get_pressed()
        right_pressed = keys[pygame.K_RIGHT]
        left_pressed = keys[pygame.K_LEFT]

        if winner_index < 0:
            if right_pressed or left_pressed:
                race_started = True
            if race_started:
                race_time += dt

            player = racers[0]
            if player.stunTimer > 0:
                player.stunTimer -= dt
            else:
                if right_pressed:
                    player.speed = PLAYER_SPEED
                elif left_pressed:
                    player.speed = -MAX_REVERSE
                else:
                    player.speed = 0
                player.position += player.speed * dt
                player.position = max(START_POSITION, min(player.position, finish_position))
                update_checkpoint(player)
                handle_collision(player)
                collect_coins(player)

            user_position = player.position
            update_ai(racers[1], dt)
            update_ai(racers[2], dt)

            for i, racer in enumerate(racers):
                if not racer.finished and racer.position >= finish_position:
                    racer.finished = True
                    racer.finishTime = race_time
                    racer.hasFinishTime = True
                    if winner_index < 0:
                        winner_index = i

            px, py, _, _ = get_road_position(player.position)
            target_camera_x = px - 250
            target_camera_y = py - 350
            camera_x += (target_camera_x - camera_x) * 7.0 * dt
            camera_y += (target_camera_y - camera_y) * 7.0 * dt

        draw_road()
        draw_race_marker(START_POSITION, "START", GREEN)
        draw_race_marker(finish_position, "FINISH", YELLOW)

        for obstacle in obstacles:
            if winner_index < 0:
                obstacle.update(dt)
            if abs(obstacle.position - user_position) < 1500:
                draw_obstacle(obstacle)
        for coin in coins:
            draw_coin(coin)
        for racer in racers[1:]:
            draw_racer(racer.position, racer.lane, racer.color, False)
        draw_racer(racers[0].position, racers[0].lane, racers[0].color, True)
        draw_hud()
        if winner_index >= 0:
            draw_finish_results()
        draw_frame()
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
