import pygame
import math
import random
import sys

pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Fun Race & Parkour - Graphics Algorithms")
clock = pygame.time.Clock()

# Colors
BLACK = (10, 10, 10)
WHITE = (235, 235, 235)
RED = (230, 45, 45)
BLUE = (55, 130, 255)
GREEN = (50, 210, 100)
YELLOW = (255, 220, 0)
CYAN = (50, 205, 255)
ORANGE = (255, 140, 30)
ROAD_COLOR = (68, 68, 68)
ROAD_EDGE_COLOR = (210, 210, 210)
GRASS_COLOR = (25, 80, 35)

PLAYER_SPEED = 210.0
AI_SPEED = 205.0
MAX_REVERSE = 70.0

ROAD_WIDTH = 180
ROAD_HALF_WIDTH = ROAD_WIDTH // 2
LANE_WIDTH = ROAD_WIDTH / 3
START_POSITION = 0.0
COIN_RADIUS = 12
COIN_COLLECT_DISTANCE = 28

pygame.display.set_caption("Fun Race & Parkour")
clock = pygame.time.Clock()

current_level = 2
menu_active = True

# ==============================================================
# COMPUTER GRAPHICS ALGORITHMS
# ==============================================================

def bresenham_line(x1, y1, x2, y2, color, surface=screen):
    """Bresenham's line drawing algorithm."""
    x1, y1, x2, y2 = map(int, (x1, y1, x2, y2))

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    while True:
        if 0 <= x1 < surface.get_width() and 0 <= y1 < surface.get_height():
            surface.set_at((x1, y1), color)

        if x1 == x2 and y1 == y2:
            break

        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy


def bresenham_circle(cx, cy, radius, color, surface=screen):
    """Bresenham's midpoint/bresenham circle drawing algorithm."""
    cx, cy, radius = int(cx), int(cy), int(radius)
    x = 0
    y = radius
    d = 3 - 2 * radius

    def plot8(px, py):
        points = [
            (cx + px, cy + py), (cx - px, cy + py),
            (cx + px, cy - py), (cx - px, cy - py),
            (cx + py, cy + px), (cx - py, cy + px),
            (cx + py, cy - px), (cx - py, cy - px)
        ]
        for qx, qy in points:
            if 0 <= qx < surface.get_width() and 0 <= qy < surface.get_height():
                surface.set_at((qx, qy), color)

    while x <= y:
        plot8(x, y)
        if d < 0:
            d += 4 * x + 6
        else:
            d += 4 * (x - y) + 10
            y -= 1
        x += 1


def draw_filled_circle(cx, cy, radius, fill_color, border_color=BLACK):
    """Fill a Bresenham circle using flood fill."""
    bresenham_circle(cx, cy, radius, border_color)
    flood_fill(cx, cy, fill_color, border_color)


def flood_fill(x, y, fill_color, boundary_color):
    """Iterative 4-connected flood-fill algorithm."""
    x, y = int(x), int(y)

    if not (0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT):
        return

    target = screen.get_at((x, y))[:3]
    if target == fill_color or target == boundary_color:
        return

    stack = [(x, y)]
    visited = set()

    while stack:
        px, py = stack.pop()

        if (px, py) in visited:
            continue
        visited.add((px, py))

        if not (0 <= px < SCREEN_WIDTH and 0 <= py < SCREEN_HEIGHT):
            continue

        current = screen.get_at((px, py))[:3]
        if current != target:
            continue

        screen.set_at((px, py), fill_color)

        stack.append((px + 1, py))
        stack.append((px - 1, py))
        stack.append((px, py + 1))
        stack.append((px, py - 1))


def translate_point(x, y, tx, ty):
    """2-D translation: x'=x+tx, y'=y+ty."""
    return x + tx, y + ty


def rotate_point(x, y, cx, cy, angle_degrees):
    """2-D rotation about (cx, cy) using the rotation matrix."""
    a = math.radians(angle_degrees)
    cos_a = math.cos(a)
    sin_a = math.sin(a)

    x -= cx
    y -= cy

    rx = x * cos_a - y * sin_a
    ry = x * sin_a + y * cos_a

    return rx + cx, ry + cy


def rotate_vector(x, y, angle_degrees):
    return rotate_point(x, y, 0, 0, angle_degrees)


def draw_polyline_bresenham(points, color):
    for i in range(len(points) - 1):
        bresenham_line(
            points[i][0], points[i][1],
            points[i + 1][0], points[i + 1][1],
            color
        )


def draw_filled_rect(x, y, width, height, fill_color, border_color=BLACK):
    """Rectangle boundary with Bresenham lines, interior with flood fill."""
    x1, y1 = int(x), int(y)
    x2, y2 = int(x + width), int(y + height)

    bresenham_line(x1, y1, x2, y1, border_color)
    bresenham_line(x2, y1, x2, y2, border_color)
    bresenham_line(x2, y2, x1, y2, border_color)
    bresenham_line(x1, y2, x1, y1, border_color)

    flood_fill((x1 + x2) // 2, (y1 + y2) // 2, fill_color, border_color)


# ==============================================================
# ===== SQUARE CLIPPING =====
# Sutherland-Hodgman polygon clipping, ported from
# circule_polygon_clipping.py (clipAgainstEdge / insideClipEdge /
# lineIntersection / circularPolygonClipping in that file).
#
# The only thing that changes is the CLIPPING WINDOW: instead of the
# many-sided polygon that approximated a circle, the window here is a
# plain 4-vertex square. The edge-clipping math itself (cross product
# inside/outside test, line-line intersection, one Sutherland-Hodgman
# pass per edge) is exactly the same algorithm, just written against
# (x, y) tuples instead of a Point class, to match how points are
# represented everywhere else in this game (road_points, worldToScreen,
# etc. all use plain tuples).
#
# Everything here is convex-polygon-agnostic: sutherlandHodgmanClip()
# takes ANY convex clipping polygon, not just a square. To swap the
# square for a different shape later, write a new create*ClipPolygon()
# function that returns a list of (x, y) vertices in order (see
# createSquareClipPolygon below) and pass its result in where
# getSquareClipWindow() is used now -- nothing else needs to change.
# ==============================================================

def clip_cross(a, b, p):
    """Cross product of (b - a) and (p - a). Same formula as cross()
    in circule_polygon_clipping.py."""
    return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])


def clip_polygon_signed_area(polygon):
    """Signed area of a polygon; sign tells us if its vertices run
    clockwise or counter-clockwise (same as polygonArea() in the
    original clipping file)."""
    area = 0.0
    n = len(polygon)

    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]
        area += x1 * y2 - x2 * y1

    return area / 2.0


def clip_inside_edge(p, a, b, clip_is_ccw):
    """True if point p is on the 'inside' half-plane of clip edge a->b.
    Same test as insideClipEdge() in the original clipping file."""
    value = clip_cross(a, b, p)

    if clip_is_ccw:
        return value >= 0

    return value <= 0


def clip_line_intersection(p1, p2, a, b):
    """Intersection of segment p1->p2 with the infinite line through
    a->b. Same formula as lineIntersection() in the original clipping
    file."""
    dx1 = p2[0] - p1[0]
    dy1 = p2[1] - p1[1]

    dx2 = b[0] - a[0]
    dy2 = b[1] - a[1]

    denominator = dx1 * dy2 - dy1 * dx2

    if abs(denominator) < 1e-9:
        return p2

    t = (
        (a[0] - p1[0]) * dy2
        - (a[1] - p1[1]) * dx2
    ) / denominator

    return (p1[0] + t * dx1, p1[1] + t * dy1)


def clip_against_edge(subject, a, b, clip_is_ccw):
    """One Sutherland-Hodgman pass: clip polygon 'subject' against a
    single clip edge a->b. Same four cases as clipAgainstEdge() in the
    original clipping file (both inside / entering / leaving / both
    outside)."""
    output = []
    n = len(subject)

    if n == 0:
        return output

    for i in range(n):
        current = subject[i]
        previous = subject[i - 1]

        current_inside = clip_inside_edge(current, a, b, clip_is_ccw)
        previous_inside = clip_inside_edge(previous, a, b, clip_is_ccw)

        if previous_inside and current_inside:
            # CASE 1: previous inside, current inside
            output.append(current)

        elif (not previous_inside) and current_inside:
            # CASE 2: previous outside, current inside
            output.append(clip_line_intersection(previous, current, a, b))
            output.append(current)

        elif previous_inside and not current_inside:
            # CASE 3: previous inside, current outside
            output.append(clip_line_intersection(previous, current, a, b))

        # CASE 4: both outside -> add nothing

    return output


def sutherlandHodgmanClip(subject_polygon, clip_polygon):
    """
    General Sutherland-Hodgman clip: clips subject_polygon against any
    CONVEX clip_polygon (the square clipping window, or any future
    convex shape). This is the direct equivalent of
    circularPolygonClipping() in circule_polygon_clipping.py, just
    generalised to take the clip polygon directly instead of always
    building it from a Circle.
    """
    output = list(subject_polygon)

    if len(output) < 3:
        return []

    clip_is_ccw = clip_polygon_signed_area(clip_polygon) > 0

    m = len(clip_polygon)

    for i in range(m):
        a = clip_polygon[i]
        b = clip_polygon[(i + 1) % m]

        output = clip_against_edge(output, a, b, clip_is_ccw)

        if len(output) == 0:
            break

    return output


def createSquareClipPolygon(center_x, center_y, half_size):
    """
    Builds the square clipping window as 4 vertices, in order, centered
    at (center_x, center_y) in SCREEN space. This replaces the circular
    clipping window (createCircularClipPolygon in the original file)
    with a simple 4-sided one.
    """
    return [
        (center_x - half_size, center_y - half_size),
        (center_x + half_size, center_y - half_size),
        (center_x + half_size, center_y + half_size),
        (center_x - half_size, center_y + half_size),
    ]


# Half-size (pixels) of the square clipping window shown on screen.
SQUARE_CLIP_HALF_SIZE = 130


def getSquareClipWindow():
    """
    The square clipping window used this frame, centered on the
    screen. Obstacle polygons are clipped against whatever this
    returns -- swap it for a different create*ClipPolygon() call to
    use a different convex clipping shape without touching the game
    loop or the clipping math above.
    """
    return createSquareClipPolygon(
        SCREEN_WIDTH // 2,
        SCREEN_HEIGHT // 2,
        SQUARE_CLIP_HALF_SIZE,
    )


def fillClippedPolygon(polygon, color):
    """
    Manual scan-line polygon fill for the CLIPPED polygon, using the
    same algorithm as scanlineFill()/fillPolygon() in
    circule_polygon_clipping.py (find edge intersections per scan-line,
    sort them, fill between pairs). Drawn directly onto the game's
    'screen' surface, same as bresenham_line()/flood_fill() elsewhere
    in this file.
    """
    if len(polygon) < 3:
        return

    min_y = int(min(p[1] for p in polygon))
    max_y = int(max(p[1] for p in polygon))

    n = len(polygon)

    for y in range(min_y, max_y + 1):

        intersections = []

        for i in range(n):
            x1, y1 = polygon[i]
            x2, y2 = polygon[(i + 1) % n]

            if y1 != y2:
                ymin = min(y1, y2)
                ymax = max(y1, y2)

                # Half-open interval, same as scanlineFill()
                if ymin <= y < ymax:
                    x = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                    intersections.append(x)

        intersections.sort()

        for i in range(0, len(intersections) - 1, 2):
            x_start = int(math.ceil(intersections[i]))
            x_end = int(math.floor(intersections[i + 1]))

            for x in range(x_start, x_end + 1):
                if 0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT:
                    screen.set_at((x, y), color)


def drawClippedPolygon(polygon, color):
    """Outline of the clipped polygon, drawn with this file's own
    bresenham_line() (same approach as drawPolygon() in the original
    clipping file)."""
    n = len(polygon)

    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]
        bresenham_line(x1, y1, x2, y2, color)


# ==============================================================
# ROAD
# Curved turning points are generated by rotating the travel
# direction. This explicitly uses the rotation transformation.
# ==============================================================

road_points = []
road_distances = []
road_tangents = []
road_total_length = 0.0


def createRoad():
    global road_points, road_distances, road_tangents, road_total_length

    road_points = [(0.0, 350.0)]
    heading = 0.0
    x, y = road_points[0]

    commands = [
        ("straight", 650),
        ("turn", 90, 180),
        ("straight", 650),
        ("turn", -90, 180),
        ("straight", 800),
        ("turn", -90, 180),
        ("straight", 650),
        ("turn", 90, 180),
        ("straight", 850),
        ("turn", 90, 180),
        ("straight", 650),
        ("turn", -90, 180),
        ("straight", 800),
        ("turn", -90, 180),
        ("straight", 750),
    ]

    step = 10.0

    for command in commands:
        if command[0] == "straight":
            distance = command[1]
            count = max(1, int(distance / step))

            for _ in range(count):
                dx, dy = rotate_vector(step, 0, heading)
                x, y = translate_point(x, y, dx, dy)
                road_points.append((x, y))

        else:
            _, turn_angle, radius = command
            arc_length = radius * math.radians(abs(turn_angle))
            count = max(2, int(arc_length / step))
            angle_step = turn_angle / count

            # Rotate the tangent at each turning point.
            for _ in range(count):
                dx, dy = rotate_vector(step, 0, heading)
                x, y = translate_point(x, y, dx, dy)
                road_points.append((x, y))
                heading += angle_step

    road_distances = [0.0]
    road_tangents = []

    total = 0.0
    for i in range(len(road_points)):
        if i == 0:
            dx = road_points[1][0] - road_points[0][0]
            dy = road_points[1][1] - road_points[0][1]
        elif i == len(road_points) - 1:
            dx = road_points[-1][0] - road_points[-2][0]
            dy = road_points[-1][1] - road_points[-2][1]
        else:
            dx = road_points[i + 1][0] - road_points[i - 1][0]
            dy = road_points[i + 1][1] - road_points[i - 1][1]

        length = math.hypot(dx, dy)
        tangent = (1.0, 0.0) if length == 0 else (dx / length, dy / length)
        road_tangents.append(tangent)

        if i > 0:
            segment_length = math.hypot(
                road_points[i][0] - road_points[i - 1][0],
                road_points[i][1] - road_points[i - 1][1]
            )
            total += segment_length
            road_distances.append(total)

    road_total_length = total


def getRoadPosition(position):
    position = max(0.0, min(position, road_total_length))

    for i in range(1, len(road_distances)):
        if position <= road_distances[i]:
            previous = road_distances[i - 1]
            segment_length = road_distances[i] - previous
            ratio = 0.0 if segment_length == 0 else (position - previous) / segment_length

            x1, y1 = road_points[i - 1]
            x2, y2 = road_points[i]

            x = x1 + (x2 - x1) * ratio
            y = y1 + (y2 - y1) * ratio
            tx, ty = road_tangents[i]
            return x, y, tx, ty

    x, y = road_points[-1]
    tx, ty = road_tangents[-1]
    return x, y, tx, ty


def getNormal(tx, ty):
    return -ty, tx


def getWorldPosition(position, offset=0.0):
    x, y, tx, ty = getRoadPosition(position)
    nx, ny = getNormal(tx, ty)
    return translate_point(x, y, nx * offset, ny * offset)


# ==============================================================
# CAMERA / TRANSLATION
# ==============================================================

cameraX = 0.0
cameraY = 0.0


def worldToScreen(x, y):
    # Camera movement is a translation transformation.
    return int(x - cameraX), int(y - cameraY)


# ==============================================================
# DRAW ROAD WITH BRESENHAM + FLOOD FILL
# ==============================================================

def drawLaneLines(start, end):
    position = start

    while position < end:
        dash_end = min(position + 35, end)

        for lane_offset in [-LANE_WIDTH / 2, LANE_WIDTH / 2]:
            points = []
            p = position

            while p <= dash_end:
                x, y = getWorldPosition(p, lane_offset)
                points.append(worldToScreen(x, y))
                p += 8

            draw_polyline_bresenham(points, WHITE)

        position += 70


road_surface = None
road_surface_origin_x = 0
road_surface_origin_y = 0


def buildRoadSurface():
    """
    Build the complete road ONCE.

    Bresenham and flood fill are intentionally kept, but they are not
    executed every frame. This removes the biggest source of lag.
    """
    global road_surface, road_surface_origin_x, road_surface_origin_y

    min_x = int(min(p[0] for p in road_points)) - ROAD_WIDTH - 20
    max_x = int(max(p[0] for p in road_points)) + ROAD_WIDTH + 20
    min_y = int(min(p[1] for p in road_points)) - ROAD_WIDTH - 20
    max_y = int(max(p[1] for p in road_points)) + ROAD_WIDTH + 20

    width = max_x - min_x + 1
    height = max_y - min_y + 1

    road_surface_origin_x = min_x
    road_surface_origin_y = min_y

    road_surface = pygame.Surface((width, height))
    road_surface.fill(GRASS_COLOR)

    def local_point(x, y):
        return int(x - min_x), int(y - min_y)

    # Create one continuous closed road boundary.
    left_points = []
    right_points = []

    for i, (x, y) in enumerate(road_points):
        tx, ty = road_tangents[i]
        nx, ny = getNormal(tx, ty)

        left_points.append(
            local_point(
                x + nx * ROAD_HALF_WIDTH,
                y + ny * ROAD_HALF_WIDTH
            )
        )
        right_points.append(
            local_point(
                x - nx * ROAD_HALF_WIDTH,
                y - ny * ROAD_HALF_WIDTH
            )
        )

    # Bresenham road boundary.
    for i in range(len(left_points) - 1):
        bresenham_line(
            *left_points[i],
            *left_points[i + 1],
            ROAD_EDGE_COLOR,
            road_surface
        )
        bresenham_line(
            *right_points[i],
            *right_points[i + 1],
            ROAD_EDGE_COLOR,
            road_surface
        )

    # Close the road at the start and finish.
    bresenham_line(
        *left_points[0], *right_points[0],
        ROAD_EDGE_COLOR, road_surface
    )
    bresenham_line(
        *left_points[-1], *right_points[-1],
        ROAD_EDGE_COLOR, road_surface
    )

    # Flood fill ONCE.
    sx, sy = local_point(*road_points[len(road_points) // 2])
    flood_fill_on_surface(
        road_surface, sx, sy,
        ROAD_COLOR, ROAD_EDGE_COLOR
    )

    # Lane lines are also drawn once.
    position = 0.0
    while position < road_total_length:
        dash_end = min(position + 35, road_total_length)

        for lane_offset in [-LANE_WIDTH / 2, LANE_WIDTH / 2]:
            points = []
            p = position

            while p <= dash_end:
                x, y = getWorldPosition(p, lane_offset)
                points.append(local_point(x, y))
                p += 8

            for i in range(len(points) - 1):
                bresenham_line(
                    *points[i], *points[i + 1],
                    WHITE, road_surface
                )

        position += 70


def flood_fill_on_surface(surface, x, y, fill_color, boundary_color):
    """Flood fill for any pygame surface."""
    x, y = int(x), int(y)

    if not (0 <= x < surface.get_width() and 0 <= y < surface.get_height()):
        return

    target = surface.get_at((x, y))[:3]

    if target == fill_color or target == boundary_color:
        return

    stack = [(x, y)]

    while stack:
        px, py = stack.pop()

        if not (0 <= px < surface.get_width() and
                0 <= py < surface.get_height()):
            continue

        if surface.get_at((px, py))[:3] != target:
            continue

        surface.set_at((px, py), fill_color)

        stack.append((px + 1, py))
        stack.append((px - 1, py))
        stack.append((px, py + 1))
        stack.append((px, py - 1))


def drawRoad():
    screen.fill(GRASS_COLOR)

    # Translation transformation:
    # move the pre-rendered world road according to the camera.
    screen.blit(
        road_surface,
        (
            int(road_surface_origin_x - cameraX),
            int(road_surface_origin_y - cameraY)
        )
    )


def drawRaceMarker(position, label, color):
    x, y, tx, ty = getRoadPosition(position)
    nx, ny = getNormal(tx, ty)

    left = translate_point(x, y, nx * ROAD_HALF_WIDTH, ny * ROAD_HALF_WIDTH)
    right = translate_point(x, y, -nx * ROAD_HALF_WIDTH, -ny * ROAD_HALF_WIDTH)

    bresenham_line(
        *worldToScreen(*left),
        *worldToScreen(*right),
        color
    )

    sx, sy = worldToScreen(x, y)
    text = largeFont.render(label, True, color)
    shadow = largeFont.render(label, True, BLACK)

    rect = text.get_rect(center=(sx, sy - ROAD_HALF_WIDTH - 28))
    shadow_rect = shadow.get_rect(center=(sx + 2, sy - ROAD_HALF_WIDTH - 26))

    screen.blit(shadow, shadow_rect)
    screen.blit(text, rect)


# ==============================================================
# COINS - BRESENHAM CIRCLE + FLOOD FILL
# ==============================================================

class Coin:
    def __init__(self, position, lane):
        self.position = position
        self.lane = lane
        self.collected = False

    def world_position(self):
        return getWorldPosition(self.position, self.lane * LANE_WIDTH)


coins = []
coin_count = 0


def createCoins():
    global coins
    coins = []

    coin_positions = [
        350, 500, 650, 800, 950,
        1100, 1250, 1400, 1550, 1700,
        1850, 2000, 2150, 2300, 2450,
        2600, 2750, 2900, 3050, 3200,
        3350, 3500, 3650, 3800, 3950,
        4100, 4250, 4400, 4550, 4700
    ]

    for position in coin_positions:
        if position < road_total_length - 100:
            coins.append(Coin(position, 0))


coin_surface = None


def buildCoinSurface():
    global coin_surface

    size = (COIN_RADIUS + 5) * 2
    coin_surface = pygame.Surface((size, size), pygame.SRCALPHA)
    coin_surface.fill((0, 0, 0, 0))

    cx = size // 2
    cy = size // 2

    # Bresenham circle + flood fill only once.
    bresenham_circle(cx + 2, cy + 2, COIN_RADIUS + 2, BLACK, coin_surface)
    flood_fill_on_surface(
        coin_surface, cx + 2, cy + 2,
        BLACK, BLACK
    )

    bresenham_circle(cx, cy, COIN_RADIUS, ORANGE, coin_surface)
    flood_fill_on_surface(
        coin_surface, cx, cy,
        YELLOW, ORANGE
    )

    bresenham_circle(cx, cy, COIN_RADIUS - 4, ORANGE, coin_surface)

    bresenham_circle(cx - 4, cy - 4, 3, WHITE, coin_surface)
    flood_fill_on_surface(
        coin_surface, cx - 4, cy - 4,
        WHITE, WHITE
    )


def drawCoin(coin):
    if coin.collected:
        return

    x, y = coin.world_position()
    sx, sy = worldToScreen(x, y)

    rect = coin_surface.get_rect(center=(sx, sy))
    screen.blit(coin_surface, rect)


def collectCoins(racer):
    global coin_count

    if not racer.is_player:
        return

    player_x, player_y = getWorldPosition(
        racer.position,
        racer.lane * LANE_WIDTH
    )

    for coin in coins:
        if coin.collected:
            continue

        coin_x, coin_y = coin.world_position()

        distance = math.hypot(
            player_x - coin_x,
            player_y - coin_y
        )

        if distance < COIN_COLLECT_DISTANCE:
            coin.collected = True
            coin_count += 1


# ==============================================================
# OBSTACLES
# ==============================================================

class Obstacle:
    def __init__(self, position, speed, start_side=1):
        self.position = position
        self.offset = -ROAD_HALF_WIDTH + 25 if start_side == 1 else ROAD_HALF_WIDTH - 25
        self.speed = speed
        self.direction = 1 if start_side == 1 else -1

    def update(self, dt):
        self.offset += self.speed * self.direction * dt
        limit = ROAD_HALF_WIDTH - 25

        if self.offset >= limit:
            self.offset = limit
            self.direction = -1
        elif self.offset <= -limit:
            self.offset = -limit
            self.direction = 1

    def world_position(self):
        return getWorldPosition(self.position, self.offset)


obstacles = []


def createObstacles():
    global obstacles
    obstacles = []

    positions = [
        650, 1250, 1900, 2550, 3200,
        3850, 4500, 5150, 5800, 6450
    ]

    for i, position in enumerate(positions):
        obstacles.append(
            Obstacle(
                position,
                55 + random.randint(0, 30),
                1 if i % 2 == 0 else -1,
            )
        )


def makeObstacleSurface(angle):
    """Create an obstacle using Bresenham/flood fill, then rotate it."""
    base = pygame.Surface((90, 64), pygame.SRCALPHA)

    # Boundary with Bresenham.
    pts = [(10, 10), (80, 10), (80, 54), (10, 54)]
    for i in range(4):
        bresenham_line(
            *pts[i], *pts[(i + 1) % 4],
            BLACK, base
        )

    flood_fill_on_surface(base, 45, 32, ORANGE, BLACK)

    inner = [(19, 19), (71, 19), (71, 45), (19, 45)]
    for i in range(4):
        bresenham_line(
            *inner[i], *inner[(i + 1) % 4],
            RED, base
        )

    flood_fill_on_surface(base, 45, 32, RED, RED)

    bresenham_line(27, 32, 63, 32, WHITE, base)

    return pygame.transform.rotate(base, -angle)


def drawObstacle(obstacle):
    x, y = obstacle.world_position()
    sx, sy = worldToScreen(x, y)

    if not hasattr(obstacle, "surface"):
        _, _, tx, ty = getRoadPosition(obstacle.position)
        angle = math.degrees(math.atan2(ty, tx))
        obstacle.surface = makeObstacleSurface(angle)

    rect = obstacle.surface.get_rect(center=(sx, sy))
    screen.blit(obstacle.surface, rect)


# ===== SQUARE CLIPPING =====
# The clipping boundary is a mathematical/rendering boundary only.
# It is NOT drawn on the screen and it is NOT a gameplay object.
#
# Rendering order for the obstacle:
#     local polygon -> rotation -> translation -> camera transformation
#     -> screen coordinates -> Sutherland-Hodgman clipping -> rendering
#
# The obstacle keeps the same visual construction as the original:
# outer orange rectangle, inner red rectangle, and white centre marking.
# Each polygon is clipped independently so the visible appearance is
# preserved while only the part inside the mathematical square is drawn.

SQUARE_CLIP_CENTER_X = SCREEN_WIDTH // 2
SQUARE_CLIP_CENTER_Y = SCREEN_HEIGHT // 2
SQUARE_CLIP_HALF_SIZE = 260


def getSquareClipWindow():
    """Return the four mathematical vertices of the invisible square."""
    cx = SQUARE_CLIP_CENTER_X
    cy = SQUARE_CLIP_CENTER_Y
    h = SQUARE_CLIP_HALF_SIZE

    return [
        (cx - h, cy - h),   # Top-left
        (cx + h, cy - h),   # Top-right
        (cx + h, cy + h),   # Bottom-right
        (cx - h, cy + h),   # Bottom-left
    ]


def transformObstaclePolygon(local_polygon, world_x, world_y, angle):
    """
    Apply the existing game transformations in this order:

        Object coordinates
        -> Rotation
        -> Translation
        -> Camera transformation
        -> Screen coordinates
    """
    screen_polygon = []

    for lx, ly in local_polygon:
        # Rotation transformation.
        rx, ry = rotate_point(lx, ly, 0, 0, angle)

        # Translation to the obstacle's world position.
        wx, wy = translate_point(rx, ry, world_x, world_y)

        # Camera translation / world-to-screen transformation.
        sx, sy = worldToScreen(wx, wy)

        screen_polygon.append((sx, sy))

    return screen_polygon


def drawObstacle(obstacle):
    """
    Draw the obstacle using actual Sutherland-Hodgman polygon clipping.

    No Pygame clipping API, masks, sprite masking, centre-point test, or
    object deletion is used. The polygon vertices are mathematically
    clipped against all four edges of the invisible square.
    """
    world_x, world_y = obstacle.world_position()

    # Same road-based rotation used by the original obstacle sprite.
    _, _, tx, ty = getRoadPosition(obstacle.position)
    angle = math.degrees(math.atan2(ty, tx))

    # Original obstacle surface is 90 x 64.
    # Its outer boundary is (10,10)-(80,54), centred at (45,32).
    # Therefore these coordinates are relative to the obstacle centre.
    outer_polygon = [
        (-35, -22),
        (35, -22),
        (35, 22),
        (-35, 22),
    ]

    # Original inner red rectangle: (19,19)-(71,45).
    inner_polygon = [
        (-26, -13),
        (26, -13),
        (26, 13),
        (-26, 13),
    ]

    # Original white centre line (27,32)-(63,32), represented as a
    # thin polygon so it can also be processed by Sutherland-Hodgman.
    centre_line_polygon = [
        (-18, -0.5),
        (18, -0.5),
        (18, 0.5),
        (-18, 0.5),
    ]

    # --------------------------------------------------------------
    # MATHEMATICAL CLIPPING WINDOW
    # --------------------------------------------------------------
    # This square is never drawn. It exists only for the clipping math.
    clip_window = getSquareClipWindow()

    # --------------------------------------------------------------
    # TRANSFORMATION STAGE
    # --------------------------------------------------------------
    # Object -> Rotation -> Translation -> Camera -> Screen
    outer_screen = transformObstaclePolygon(
        outer_polygon, world_x, world_y, angle
    )
    inner_screen = transformObstaclePolygon(
        inner_polygon, world_x, world_y, angle
    )
    centre_line_screen = transformObstaclePolygon(
        centre_line_polygon, world_x, world_y, angle
    )

    # --------------------------------------------------------------
    # SUTHERLAND-HODGMAN CLIPPING
    # --------------------------------------------------------------
    # The polygon is processed against the four square edges:
    # Left -> Top -> Right -> Bottom (through the ordered clip polygon).
    #
    # For every edge, the algorithm:
    #   1. tests whether vertices are inside/outside,
    #   2. calculates an intersection when an edge crosses the boundary,
    #   3. generates a new polygon for the next clipping edge.
    clipped_outer = sutherlandHodgmanClip(
        outer_screen,
        clip_window
    )

    clipped_inner = sutherlandHodgmanClip(
        inner_screen,
        clip_window
    )

    clipped_centre_line = sutherlandHodgmanClip(
        centre_line_screen,
        clip_window
    )

    # --------------------------------------------------------------
    # RENDER ONLY THE CLIPPED RESULT
    # --------------------------------------------------------------
    # Completely inside  -> complete polygon is returned.
    # Completely outside -> empty polygon is returned.
    # Intersecting       -> intersection vertices form the visible part.
    if len(clipped_outer) >= 3:
        fillClippedPolygon(clipped_outer, ORANGE)
        drawClippedPolygon(clipped_outer, BLACK)

    if len(clipped_inner) >= 3:
        fillClippedPolygon(clipped_inner, RED)
        drawClippedPolygon(clipped_inner, RED)

    if len(clipped_centre_line) >= 3:
        fillClippedPolygon(clipped_centre_line, WHITE)


def obstacleCollision(racer):
    racer_x, racer_y = getWorldPosition(
        racer.position,
        racer.lane * LANE_WIDTH
    )

    for obstacle in obstacles:

        if abs(racer.position - obstacle.position) > 60:
            continue

        obstacle_x, obstacle_y = obstacle.world_position()

        distance = math.hypot(
            racer_x - obstacle_x,
            racer_y - obstacle_y
        )

        if distance < 30 + 22:
            return True

    return False


# ==============================================================
# RACERS
# ==============================================================

class Racer:
    def __init__(self, name, color, lane, is_player=False, ai_speed =AI_SPEED, reaction=1.0, risk=0.5):
        self.name = name
        self.color = color
        self.is_player = is_player
        self.lane = lane
        
        self.ai_speed = ai_speed
        self.reaction = reaction
        self.risk = risk

        self.position = START_POSITION
        self.checkpoint = START_POSITION
        self.speed = 0.0

        self.finished = False
        self.finish_time = None
        self.collision_count = 0
        self.stun_timer = 0.0

    def reset(self):
        self.position = START_POSITION
        self.checkpoint = START_POSITION
        self.speed = 0.0
        self.finished = False
        self.finish_time = None
        self.collision_count = 0
        self.stun_timer = 0.0


racers = [
    Racer("YOU", RED, 0, True),
    Racer("BLUE", BLUE, -1, ai_speed=215, reaction=0.55, risk=0.25),
    Racer("GREEN", GREEN, 1, ai_speed=215, reaction=0.75, risk=0.25),
]

userPosition = START_POSITION

raceTime = 0.0
raceStarted = False
winner = None
coin_count = 0


def updateCheckpoint(racer):
    distance = 900.0
    cp = int(racer.position // distance) * distance

    if cp > racer.checkpoint:
        racer.checkpoint = cp


def handleCollision(racer):
    if racer.finished:
        return

    if obstacleCollision(racer): # remove position
        racer.position = max(START_POSITION, racer.checkpoint - 15)
        racer.speed = 0.0
        racer.stun_timer = 0.65
        racer.collision_count += 1


def nearestObstacleAhead(position):
    nearest = None
    nearest_distance = float("inf")

    for obstacle in obstacles:
        distance = obstacle.position - position

        if 0 < distance < nearest_distance:
            nearest = obstacle
            nearest_distance = distance

    return nearest, nearest_distance


def updateAI(racer, dt):

    if racer.finished:
        return

    # Individual collision recovery
    if racer.stun_timer > 0:
        racer.stun_timer -= dt
        return

    obstacle, distance = nearestObstacleAhead(racer.position)

    target_speed = racer.ai_speed

    if obstacle is not None:

        relative_offset = abs(obstacle.offset)

        # -------------------------------------------------
        # CAUTIOUS AI
        # -------------------------------------------------
        if racer.risk < 0.5:

            if distance < 350 and relative_offset < 55:
                target_speed = 120

            if distance < 200 and relative_offset < 60:
                target_speed = 65

            if distance < 100 and relative_offset < 65:
                target_speed = 35

        # -------------------------------------------------
        # AGGRESSIVE AI
        # -------------------------------------------------
        else:

            if distance < 250 and relative_offset < 45:
                target_speed = 170

            if distance < 130 and relative_offset < 50:
                target_speed = 110

            if distance < 70 and relative_offset < 55:
                target_speed = 50

    # Individual reaction speed
    if racer.speed < target_speed:
        racer.speed += 400 * racer.reaction * dt

        if racer.speed > target_speed:
            racer.speed = target_speed

    elif racer.speed > target_speed:
        racer.speed -= 500 * racer.reaction * dt

        if racer.speed < target_speed:
            racer.speed = target_speed

    # Move this AI independently
    racer.position += racer.speed * dt

    racer.position = min(
        racer.position,
        finishPosition
    )

    updateCheckpoint(racer)

    handleCollision(racer)

# ==============================================================
# HUD
# ==============================================================

font = pygame.font.Font(None, 27)
largeFont = pygame.font.Font(None, 40)
titleFont = pygame.font.Font(None, 50)

finishPosition = 0.0

racer_surfaces = {}


def getRacerSurface(color, outer_radius, inner_radius):
    key = (color, outer_radius, inner_radius)

    if key in racer_surfaces:
        return racer_surfaces[key]

    size = outer_radius * 2 + 4
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = cy = size // 2

    bresenham_circle(cx, cy, outer_radius, BLACK, surface)
    flood_fill_on_surface(surface, cx, cy, BLACK, BLACK)

    bresenham_circle(cx, cy, inner_radius, color, surface)
    flood_fill_on_surface(surface, cx, cy, color, WHITE)

    bresenham_circle(cx, cy, inner_radius, WHITE, surface)

    racer_surfaces[key] = surface
    return surface


def getRaceTime():
    return raceTime


def drawHUD():
    panel = pygame.Surface((SCREEN_WIDTH, 105), pygame.SRCALPHA)
    panel.fill((10, 10, 10, 225))
    screen.blit(panel, (0, 0))

    title = titleFont.render("Fun Race & Parkour", True, WHITE)
    screen.blit(title, (10, 12))

    time_text = font.render(
        f"TIME: {raceTime:05.1f}s",
        True,
        YELLOW,
    )
    screen.blit(time_text, (370, 20))

    controls = font.render(
        "RIGHT: ACCELERATE    LEFT: BRAKE / REVERSE    ESC: QUIT",
        True,
        WHITE,
    )
    screen.blit(controls, (10, 52))

    coin_text = font.render(
        f"COINS: {coin_count}",
        True,
        YELLOW
    )
    screen.blit(coin_text, (700, 20))

    y = 88
    for racer in racers:
        progress = min(
            100,
            int((racer.position / finishPosition) * 100)
        )

        text = font.render(
            f"{racer.name}: {progress:3d}%",
            True,
            racer.color,
        )
        screen.blit(text, (10 + racers.index(racer) * 105, y))


def drawFinishResults():
    if winner is None:
        return

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))

    title = titleFont.render(
        f"{winner.name} WINS!",
        True,
        winner.color,
    )
    title_rect = title.get_rect(
        center=(SCREEN_WIDTH // 2, 180)
    )
    screen.blit(title, title_rect)

    sorted_racers = sorted(
        racers,
        key=lambda r: r.finish_time if r.finish_time is not None else 999999
    )

    y = 250
    for index, racer in enumerate(sorted_racers, start=1):
        result = (
            f"{index}. {racer.name}   "
            f"{racer.finish_time:.2f}s   "
            f"Hits: {racer.collision_count}"
        )

        text = font.render(result, True, racer.color)
        rect = text.get_rect(
            center=(SCREEN_WIDTH // 2, y)
        )
        screen.blit(text, rect)
        y += 42

    restart = font.render(
        "Press R to race again    |    ESC to quit",
        True,
        WHITE
    )
    rect = restart.get_rect(
        center=(SCREEN_WIDTH // 2, y + 25)
    )
    screen.blit(restart, rect)


def drawFrame():
    bresenham_line(4, 4, SCREEN_WIDTH - 4, 4, WHITE)
    bresenham_line(
        SCREEN_WIDTH - 4, 4,
        SCREEN_WIDTH - 4, SCREEN_HEIGHT - 4,
        WHITE
    )
    bresenham_line(
        SCREEN_WIDTH - 4, SCREEN_HEIGHT - 4,
        4, SCREEN_HEIGHT - 4,
        WHITE
    )
    bresenham_line(
        4, SCREEN_HEIGHT - 4,
        4, 4,
        WHITE
    )

# ==============================================================
# MAIN GAME
# ==============================================================

def drawMenu():

    screen.fill(GRASS_COLOR)

    # Background road
    pygame.draw.rect(
        screen,
        ROAD_COLOR,
        (150, 0, 700, SCREEN_HEIGHT)
    )

    # Road borders
    pygame.draw.line(
        screen,
        ROAD_EDGE_COLOR,
        (150, 0),
        (150, SCREEN_HEIGHT),
        6
    )

    pygame.draw.line(
        screen,
        ROAD_EDGE_COLOR,
        (850, 0),
        (850, SCREEN_HEIGHT),
        6
    )

    # Title
    title = titleFont.render(
        "FUN RACE & PARKOUR",
        True,
        WHITE
    )

    title_rect = title.get_rect(
        center=(SCREEN_WIDTH // 2, 70)
    )

    screen.blit(title, title_rect)

    # Subtitle
    subtitle = largeFont.render(
        "SELECT LEVEL",
        True,
        YELLOW
    )

    subtitle_rect = subtitle.get_rect(
        center=(SCREEN_WIDTH // 2, 125)
    )

    screen.blit(subtitle, subtitle_rect)

    # Level information
    levels = [
        ("LEVEL 1", "STRAIGHT ROAD", GREEN),
        ("LEVEL 2", "CURRENT GAME", BLUE),
        ("LEVEL 3", "COMING SOON", RED)
    ]

    y = 210

    for level_name, description, color in levels:

        box = pygame.Rect(
            250,
            y,
            500,
            90
        )

        # Box background
        pygame.draw.rect(
            screen,
            BLACK,
            box
        )

        # Box border
        pygame.draw.rect(
            screen,
            color,
            box,
            3
        )

        # Level name
        level_text = largeFont.render(
            level_name,
            True,
            color
        )

        screen.blit(
            level_text,
            (box.x + 25, box.y + 15)
        )

        # Description
        desc_text = font.render(
            description,
            True,
            WHITE
        )

        screen.blit(
            desc_text,
            (box.x + 25, box.y + 55)
        )

        # Key number
        key_text = largeFont.render(
            level_name[-1],
            True,
            YELLOW
        )

        key_rect = key_text.get_rect(
            center=(box.right - 35, box.centery)
        )

        screen.blit(
            key_text,
            key_rect
        )

        y += 110

    # Instructions
    instruction = font.render(
        "Press 1, 2 or 3 to select a level",
        True,
        WHITE
    )

    instruction_rect = instruction.get_rect(
        center=(SCREEN_WIDTH // 2, 570)
    )

    screen.blit(
        instruction,
        instruction_rect
    )

    quit_text = font.render(
        "ESC - Quit",
        True,
        WHITE
    )

    quit_rect = quit_text.get_rect(
        center=(SCREEN_WIDTH // 2, 610)
    )

    screen.blit(
        quit_text,
        quit_rect
    )


def resetRace():
    global raceTime, raceStarted, winner
    global cameraX, cameraY, userPosition, coin_count

    for racer in racers:
        racer.reset()

    createObstacles()
    createCoins()

    raceTime = 0.0
    raceStarted = False
    winner = None
    coin_count = 0

    userPosition = START_POSITION

    start_x, start_y, _, _ = getRoadPosition(START_POSITION)

    cameraX = start_x - 250
    cameraY = start_y - 350


def main():
    global raceTime, raceStarted, winner, coin_count
    global cameraX, cameraY, userPosition
    global finishPosition
    global current_level, menu_active

    random.seed()

    # Start with Level 2 as the current game
    current_level = 2
    menu_active = True

    createRoad()
    buildRoadSurface()
    buildCoinSurface()

    finishPosition = road_total_length - 80
    resetRace()

    running = True

    while running:

        dt = clock.tick(60) / 1000.0
        dt = min(dt, 0.05)

        # ==========================================================
        # EVENTS
        # ==========================================================

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:

                # ESC works everywhere
                if event.key == pygame.K_ESCAPE:
                    running = False

                # ==================================================
                # MENU
                # ==================================================

                if menu_active:

                    # ------------------------------
                    # LEVEL 1
                    # ------------------------------
                    if event.key == pygame.K_1:

                        current_level = 1

                        print("Level 1 selected")

                        # We will add Level 1 later.
                        # For now stay on menu.

                    # ------------------------------
                    # LEVEL 2
                    # ------------------------------
                    elif event.key == pygame.K_2:

                        current_level = 2

                        # Re-create the current curved road
                        createRoad()

                        finishPosition = road_total_length - 80

                        resetRace()

                        menu_active = False

                    # ------------------------------
                    # LEVEL 3
                    # ------------------------------
                    elif event.key == pygame.K_3:

                        current_level = 3

                        print("Level 3 selected")

                        # We will add Level 3 later.
                        # For now stay on menu.

                # ==================================================
                # GAME
                # ==================================================

                else:

                    # Restart after race finishes
                    if event.key == pygame.K_r and winner is not None:
                        resetRace()

                    # Return to menu
                    if event.key == pygame.K_m:

                        menu_active = True
                        winner = None
                        raceStarted = False

        # ==========================================================
        # MENU SCREEN
        # ==========================================================

        if menu_active:

            drawMenu()

            pygame.display.flip()

            continue

        # ==========================================================
        # GAME UPDATE
        # ==========================================================

        keys = pygame.key.get_pressed()

        if winner is None:

            # Start race when player presses a movement key
            if keys[pygame.K_RIGHT] or keys[pygame.K_LEFT]:
                raceStarted = True

            if raceStarted:
                raceTime += dt

            # ------------------------------------------------------
            # PLAYER
            # ------------------------------------------------------

            player = racers[0]

            if player.stun_timer > 0:

                player.stun_timer -= dt

            else:

                if keys[pygame.K_RIGHT]:

                    player.speed = PLAYER_SPEED

                elif keys[pygame.K_LEFT]:

                    player.speed = -MAX_REVERSE

                else:

                    player.speed = 0.0

                # Translation transformation
                player.position += player.speed * dt

                player.position = max(
                    START_POSITION,
                    min(player.position, finishPosition)
                )

                updateCheckpoint(player)

                handleCollision(player)

                collectCoins(player)

            userPosition = player.position

            # ------------------------------------------------------
            # AI RACERS
            # ------------------------------------------------------

            updateAI(racers[1], dt)
            updateAI(racers[2], dt)

            # ------------------------------------------------------
            # FINISH CHECK
            # ------------------------------------------------------

            for racer in racers:

                if (
                    not racer.finished
                    and racer.position >= finishPosition
                ):

                    racer.finished = True
                    racer.finish_time = raceTime

                    if winner is None:
                        winner = racer

            # ------------------------------------------------------
            # CAMERA TRANSLATION
            # ------------------------------------------------------

            player_x, player_y = getWorldPosition(
                player.position
            )

            target_camera_x = player_x - 250
            target_camera_y = player_y - 350

            cameraX += (
                target_camera_x - cameraX
            ) * 7.0 * dt

            cameraY += (
                target_camera_y - cameraY
            ) * 7.0 * dt

        # ==========================================================
        # DRAW GAME
        # ==========================================================

        drawRoad()

        # START
        drawRaceMarker(
            START_POSITION,
            "START",
            GREEN
        )

        # FINISH
        drawRaceMarker(
            finishPosition,
            "FINISH",
            YELLOW
        )

        # ----------------------------------------------------------
        # OBSTACLES
        # ----------------------------------------------------------

        for obstacle in obstacles:

            if winner is None:
                obstacle.update(dt)

            # drawObstacle() performs the actual Sutherland-Hodgman
            # clipping before any obstacle pixels are rendered.
            if abs(
                obstacle.position - userPosition
            ) < 1500:
                drawObstacle(obstacle)

        # ----------------------------------------------------------
        # COINS
        # ----------------------------------------------------------

        for coin in coins:

            drawCoin(coin)

        # ----------------------------------------------------------
        # AI RACERS
        # ----------------------------------------------------------

        for racer in racers[1:]:

            offset = racer.lane * LANE_WIDTH

            x, y = getWorldPosition(
                racer.position,
                offset
            )

            sx, sy = worldToScreen(x, y)

            # Bresenham circle + flood fill
            racer_surface = getRacerSurface(
                racer.color,
                15,
                10
            )

            rect = racer_surface.get_rect(
                center=(sx, sy)
            )

            screen.blit(
                racer_surface,
                rect
            )

        # ----------------------------------------------------------
        # PLAYER
        # ----------------------------------------------------------

        player = racers[0]

        x, y = getWorldPosition(
            player.position
        )

        sx, sy = worldToScreen(
            x,
            y
        )

        # Bresenham circle + flood fill
        player_surface = getRacerSurface(
            player.color,
            16,
            11
        )

        rect = player_surface.get_rect(
            center=(sx, sy)
        )

        screen.blit(
            player_surface,
            rect
        )

        # ----------------------------------------------------------
        # HUD
        # ----------------------------------------------------------

        drawHUD()

        drawFinishResults()

        drawFrame()

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
