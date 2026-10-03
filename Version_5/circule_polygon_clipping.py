import pygame

# ============================================================
# SCREEN
# ============================================================

WIDTH = 1000
HEIGHT = 700

pixels = [[(255, 255, 255, 255) for x in range(WIDTH)] for y in range(HEIGHT)]

PI = 3.14159265358979323846


# ============================================================
# COLORS
# ============================================================

WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)
RED = (255, 0, 0, 255)
BLUE = (0, 100, 255, 255)
GREEN = (0, 180, 0, 255)
YELLOW = (255, 220, 0, 255)
CYAN = (0, 180, 180, 255)
PINK = (255, 0, 180, 255)


# ============================================================
# POINT
# ============================================================

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


# ============================================================
# CUSTOM BASIC FUNCTIONS
# No Python abs(), min(), max(), round(), ceil(), floor(),
# sorted(), sort(), sum(), etc.
# ============================================================

def myAbs(x):
    if x < 0:
        return -x
    return x


def myMin(a, b):
    if a < b:
        return a
    return b


def myMax(a, b):
    if a > b:
        return a
    return b


def myFloor(x):
    i = int(x)
    if x < 0 and x != i:
        return i - 1
    return i


def myCeil(x):
    i = int(x)
    if x > 0 and x != i:
        return i + 1
    return i


def myRound(x):
    if x >= 0:
        return int(x + 0.5)
    return int(x - 0.5)


def mySin(x):
    # Reduce angle to [-PI, PI]
    while x > PI:
        x = x - 2.0 * PI

    while x < -PI:
        x = x + 2.0 * PI

    term = x
    result = x
    n = 1

    while n <= 12:
        term = -term * x * x / ((2 * n) * (2 * n + 1))
        result = result + term
        n = n + 1

    return result


def myCos(x):
    # Reduce angle to [-PI, PI]
    while x > PI:
        x = x - 2.0 * PI

    while x < -PI:
        x = x + 2.0 * PI

    term = 1.0
    result = 1.0
    n = 1

    while n <= 12:
        term = -term * x * x / ((2 * n - 1) * (2 * n))
        result = result + term
        n = n + 1

    return result


def manualSort(values):
    # Selection sort
    n = len(values)

    i = 0
    while i < n - 1:
        smallest = i

        j = i + 1
        while j < n:
            if values[j] < values[smallest]:
                smallest = j
            j = j + 1

        if smallest != i:
            temp = values[i]
            values[i] = values[smallest]
            values[smallest] = temp

        i = i + 1


# ============================================================
# PIXEL FUNCTIONS
# ============================================================

def safePutPixel(x, y, color):
    if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
        return

    pixels[y][x] = color


def clearScreen(color):
    y = 0

    while y < HEIGHT:
        x = 0

        while x < WIDTH:
            pixels[y][x] = color
            x = x + 1

        y = y + 1


def present(screen):
    # This is only the display operation.
    # The actual drawing algorithms below are implemented manually.
    surface = pygame.Surface((WIDTH, HEIGHT))

    y = 0
    while y < HEIGHT:
        x = 0

        while x < WIDTH:
            surface.set_at((x, y), pixels[y][x])
            x = x + 1

        y = y + 1

    screen.blit(surface, (0, 0))
    pygame.display.flip()


# ============================================================
# BRESENHAM LINE DRAWING
# ============================================================

def bresenhamLine(x1, y1, x2, y2, color):

    dx = myAbs(x2 - x1)
    dy = myAbs(y2 - y1)

    if x1 < x2:
        sx = 1
    else:
        sx = -1

    if y1 < y2:
        sy = 1
    else:
        sy = -1

    err = dx - dy

    while True:

        safePutPixel(x1, y1, color)

        if x1 == x2 and y1 == y2:
            break

        e2 = 2 * err

        if e2 > -dy:
            err = err - dy
            x1 = x1 + sx

        if e2 < dx:
            err = err + dx
            y1 = y1 + sy


# ============================================================
# BRESENHAM CIRCLE
# ============================================================

def plotCirclePoints(xc, yc, x, y, color):

    safePutPixel(xc + x, yc + y, color)
    safePutPixel(xc - x, yc + y, color)
    safePutPixel(xc + x, yc - y, color)
    safePutPixel(xc - x, yc - y, color)

    safePutPixel(xc + y, yc + x, color)
    safePutPixel(xc - y, yc + x, color)
    safePutPixel(xc + y, yc - x, color)
    safePutPixel(xc - y, yc - x, color)


def bresenhamCircle(xc, yc, radius, color):

    x = 0
    y = radius

    d = 3 - 2 * radius

    while x <= y:

        plotCirclePoints(xc, yc, x, y, color)

        if d < 0:
            d = d + 4 * x + 6
        else:
            d = d + 4 * (x - y) + 10
            y = y - 1

        x = x + 1


# ============================================================
# SCAN-LINE POLYGON FILLING
# ============================================================

class IPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def scanlineFill(polygon, color):

    if len(polygon) < 3:
        return

    minY = polygon[0].y
    maxY = polygon[0].y

    i = 0
    while i < len(polygon):
        p = polygon[i]

        minY = myMin(minY, p.y)
        maxY = myMax(maxY, p.y)

        i = i + 1

    y = minY

    while y <= maxY:

        intersections = []

        i = 0

        while i < len(polygon):

            p1 = polygon[i]
            p2 = polygon[(i + 1) % len(polygon)]

            # Ignore horizontal edges
            if p1.y != p2.y:

                ymin = myMin(p1.y, p2.y)
                ymax = myMax(p1.y, p2.y)

                # Half-open interval
                if not (y < ymin or y >= ymax):

                    x = (
                        p1.x
                        + (y - p1.y)
                        * (p2.x - p1.x)
                        / (p2.y - p1.y)
                    )

                    intersections.append(x)

            i = i + 1

        manualSort(intersections)

        i = 0

        while i + 1 < len(intersections):

            x1 = myCeil(intersections[i])
            x2 = myFloor(intersections[i + 1])

            x = x1

            while x <= x2:
                safePutPixel(x, y, color)
                x = x + 1

            i = i + 2

        y = y + 1


def fillPolygon(polygon, color):

    temp = []

    i = 0

    while i < len(polygon):

        p = polygon[i]

        temp.append(
            IPoint(
                myRound(p.x),
                myRound(p.y)
            )
        )

        i = i + 1

    scanlineFill(temp, color)


# ============================================================
# DRAW POLYGON USING BRESENHAM
# ============================================================

def drawPolygon(polygon, color):

    if len(polygon) < 2:
        return

    i = 0

    while i < len(polygon):

        p1 = polygon[i]
        p2 = polygon[(i + 1) % len(polygon)]

        bresenhamLine(
            myRound(p1.x),
            myRound(p1.y),
            myRound(p2.x),
            myRound(p2.y),
            color
        )

        i = i + 1


# ============================================================
# CIRCLE
# ============================================================

class Circle:
    def __init__(self, cx, cy, radius):
        self.cx = cx
        self.cy = cy
        self.radius = radius


# ============================================================
# CREATE CIRCULAR CLIPPING POLYGON
# ============================================================

def createCircularClipPolygon(circle):

    SIDES = 100

    circlePolygon = []

    i = 0

    while i < SIDES:

        angle = 2.0 * PI * i / SIDES

        x = (
            circle.cx
            + circle.radius * myCos(angle)
        )

        y = (
            circle.cy
            + circle.radius * mySin(angle)
        )

        circlePolygon.append(Point(x, y))

        i = i + 1

    return circlePolygon


# ============================================================
# CROSS PRODUCT
# ============================================================

def cross(a, b, p):

    return (
        (b.x - a.x) * (p.y - a.y)
        -
        (b.y - a.y) * (p.x - a.x)
    )


# ============================================================
# FIND ORIENTATION OF CLIPPING POLYGON
# ============================================================

def polygonArea(polygon):

    area = 0.0

    i = 0

    while i < len(polygon):

        p1 = polygon[i]
        p2 = polygon[(i + 1) % len(polygon)]

        area = (
            area
            + p1.x * p2.y
            - p2.x * p1.y
        )

        i = i + 1

    return area / 2.0


# ============================================================
# CHECK WHETHER POINT IS INSIDE CLIPPING EDGE
# ============================================================

def insideClipEdge(p, a, b, clipCCW):

    value = cross(a, b, p)

    if clipCCW:
        return value >= 0
    else:
        return value <= 0


# ============================================================
# LINE-LINE INTERSECTION
# ============================================================

def lineIntersection(p1, p2, a, b):

    dx1 = p2.x - p1.x
    dy1 = p2.y - p1.y

    dx2 = b.x - a.x
    dy2 = b.y - a.y

    denominator = (
        dx1 * dy2
        -
        dy1 * dx2
    )

    if myAbs(denominator) < 1e-9:
        return Point(p2.x, p2.y)

    t = (
        (a.x - p1.x) * dy2
        -
        (a.y - p1.y) * dx2
    ) / denominator

    resultX = p1.x + t * dx1
    resultY = p1.y + t * dy1

    return Point(resultX, resultY)


# ============================================================
# CLIP POLYGON AGAINST ONE EDGE
# ============================================================

def clipAgainstEdge(subject, clipA, clipB, clipCCW):

    output = []

    if len(subject) == 0:
        return output

    i = 0

    while i < len(subject):

        current = subject[i]

        previous = subject[
            (i + len(subject) - 1)
            % len(subject)
        ]

        currentInside = insideClipEdge(
            current,
            clipA,
            clipB,
            clipCCW
        )

        previousInside = insideClipEdge(
            previous,
            clipA,
            clipB,
            clipCCW
        )

        # CASE 1
        # Previous INSIDE, Current INSIDE

        if previousInside and currentInside:

            output.append(current)

        # CASE 2
        # Previous OUTSIDE, Current INSIDE

        elif not previousInside and currentInside:

            intersection = lineIntersection(
                previous,
                current,
                clipA,
                clipB
            )

            output.append(intersection)
            output.append(current)

        # CASE 3
        # Previous INSIDE, Current OUTSIDE

        elif previousInside and not currentInside:

            intersection = lineIntersection(
                previous,
                current,
                clipA,
                clipB
            )

            output.append(intersection)

        # CASE 4
        # Both OUTSIDE
        # Add nothing

        i = i + 1

    return output


# ============================================================
# SUTHERLAND-HODGMAN
# ============================================================

def circularPolygonClipping(polygon, circle):

    clippingPolygon = createCircularClipPolygon(circle)

    output = []

    i = 0
    while i < len(polygon):
        output.append(polygon[i])
        i = i + 1

    if len(output) < 3:
        return []

    area = polygonArea(clippingPolygon)

    if area > 0:
        clipCCW = True
    else:
        clipCCW = False

    i = 0

    while i < len(clippingPolygon):

        clipA = clippingPolygon[i]

        clipB = clippingPolygon[
            (i + 1) % len(clippingPolygon)
        ]

        output = clipAgainstEdge(
            output,
            clipA,
            clipB,
            clipCCW
        )

        if len(output) == 0:
            break

        i = i + 1

    return output


# ============================================================
# INPUT
# ============================================================

def readInteger(message):
    while True:
        try:
            value = int(input(message))
            return value
        except:
            print("Enter a valid integer.")


def readFloat(message):
    while True:
        try:
            value = float(input(message))
            return value
        except:
            print("Enter a valid number.")


# ============================================================
# MAIN
# ============================================================

def main():

    # ========================================================
    # INPUT POLYGON
    # ========================================================

    n = readInteger("Enter number of polygon vertices: ")

    if n < 3:
        print("A polygon requires at least 3 vertices.")
        return

    polygon = []

    print("\nEnter polygon coordinates:")

    i = 0

    while i < n:

        print("Point " + str(i + 1) + " (x y): ", end="")

        values = input().split()

        while len(values) != 2:
            print("Enter exactly two coordinates: ", end="")
            values = input().split()

        x = float(values[0])
        y = float(values[1])

        polygon.append(Point(x, y))

        i = i + 1

    # ========================================================
    # COLOR
    # ========================================================

    print("\nSelect polygon color:")
    print("1. Red")
    print("2. Green")
    print("3. Blue")
    print("4. Yellow")
    print("5. Cyan")
    print("6. Pink")

    choice = readInteger("Enter choice: ")

    polygonColor = BLUE

    if choice == 1:
        polygonColor = RED
    elif choice == 2:
        polygonColor = GREEN
    elif choice == 3:
        polygonColor = BLUE
    elif choice == 4:
        polygonColor = YELLOW
    elif choice == 5:
        polygonColor = CYAN
    elif choice == 6:
        polygonColor = PINK

    # ========================================================
    # CIRCULAR CLIPPING WINDOW
    # ========================================================

    print("\nEnter circular clipping window:")

    cx = readFloat("Center X: ")
    cy = readFloat("Center Y: ")
    radius = readFloat("Radius: ")

    circle = Circle(cx, cy, radius)

    # ========================================================
    # SDL/PYGAME INITIALIZATION
    # ========================================================

    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Circular Polygon Clipping")

    # ========================================================
    # STATE
    # ========================================================

    running = True
    clipped = False
    clippedPolygon = []

    clock = pygame.time.Clock()

    # ========================================================
    # MAIN LOOP
    # ========================================================

    while running:

        events = pygame.event.get()

        eventIndex = 0

        while eventIndex < len(events):

            event = events[eventIndex]

            if event.type == pygame.QUIT:
                running = False

            # =================================================
            # PRESS C -> CLIP
            # =================================================

            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_c
            ):

                clippedPolygon = circularPolygonClipping(
                    polygon,
                    circle
                )

                clipped = True

                print("\n=================================")
                print("Circular polygon clipping done.")
                print(
                    "Original vertices : "
                    + str(len(polygon))
                )
                print(
                    "Clipped vertices  : "
                    + str(len(clippedPolygon))
                )
                print("=================================")

            # =================================================
            # PRESS R -> RESET
            # =================================================

            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_r
            ):

                clipped = False
                clippedPolygon = []

                print("\nOriginal polygon restored.")

            eventIndex = eventIndex + 1

        # ====================================================
        # DRAW
        # ====================================================

        clearScreen(WHITE)

        if not clipped:

            # ORIGINAL POLYGON

            fillPolygon(
                polygon,
                polygonColor
            )

            drawPolygon(
                polygon,
                BLACK
            )

        else:

            # CLIPPED POLYGON

            if len(clippedPolygon) >= 3:

                fillPolygon(
                    clippedPolygon,
                    polygonColor
                )

                drawPolygon(
                    clippedPolygon,
                    BLACK
                )

        # ====================================================
        # DRAW CIRCULAR CLIPPING WINDOW
        # ====================================================

        bresenhamCircle(
            myRound(circle.cx),
            myRound(circle.cy),
            myRound(circle.radius),
            RED
        )

        present(screen)

        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
