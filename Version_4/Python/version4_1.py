import pygame
import math
import random
import sys

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT)
)

pygame.display.set_caption("Road Racing Game")

clock = pygame.time.Clock()

BLACK = (10, 10, 10)
WHITE = (255, 255, 255)
RED = (230, 40, 40)
GREEN = (40, 220, 80)
BLUE = (50, 120, 255)
YELLOW = (255, 220, 0)
ROAD_COLOR = (70, 70, 70)
ROAD_EDGE_COLOR = (210, 210, 210)
ROAD_LINE_COLOR = (220, 220, 220)
GRASS_COLOR = (25, 80, 35)
CYAN = (60, 200, 255)
ORANGE = (255, 140, 30)

PLAYER_SPEED = 180.0
COMPUTER_SPEED = 170.0
BACKWARD_SPEED = 130.0

LANE_OFFSET = 55
ROAD_HALF_WIDTH = 90

START_POSITION = 80.0

userPosition = START_POSITION
computer1Position = START_POSITION
computer2Position = START_POSITION

userCheckpoint = START_POSITION
computer1Checkpoint = START_POSITION
computer2Checkpoint = START_POSITION

userLane = 1
computer1Lane = 0
computer2Lane = 2

score = 0

cameraX = 0
cameraY = 0

font = pygame.font.Font(None, 24)
largeFont = pygame.font.Font(None, 38)
titleFont = pygame.font.Font(None, 48)


class Segment:

    def __init__(
        self,
        x1,
        y1,
        x2,
        y2,
        length,
        direction
    ):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.length = length
        self.direction = direction


road = [None] * 8


def createRoad():

    road[0] = Segment(
        0, 300,
        800, 300,
        800,
        0
    )

    road[1] = Segment(
        800, 300,
        800, 650,
        350,
        1
    )

    road[2] = Segment(
        800, 650,
        1600, 650,
        800,
        0
    )

    road[3] = Segment(
        1600, 650,
        1600, 250,
        400,
        1
    )

    road[4] = Segment(
        1600, 250,
        2500, 250,
        900,
        0
    )

    road[5] = Segment(
        2500, 250,
        2500, 650,
        400,
        1
    )

    road[6] = Segment(
        2500, 650,
        3400, 650,
        900,
        0
    )

    road[7] = Segment(
        3400, 650,
        3400, 250,
        400,
        1
    )


def totalRoadLength():

    return sum(
        segment.length
        for segment in road
    )


def getRoadPosition(position):

    position = max(0, position)

    remaining = position

    for segment in road:

        if remaining <= segment.length:

            ratio = remaining / segment.length

            x = (
                segment.x1 +
                (segment.x2 - segment.x1) *
                ratio
            )

            y = (
                segment.y1 +
                (segment.y2 - segment.y1) *
                ratio
            )

            return x, y, segment.direction

        remaining -= segment.length

    segment = road[-1]

    return (
        segment.x2,
        segment.y2,
        segment.direction
    )


def getPlayerWorldPosition(
    position,
    lane
):

    x, y, direction = getRoadPosition(
        position
    )

    if lane == 0:
        offset = -LANE_OFFSET

    elif lane == 2:
        offset = LANE_OFFSET

    else:
        offset = 0

    if direction == 0:
        y += offset
    else:
        x += offset

    return x, y


def cameraWorldToScreen(x, y):

    return (
        int(x - cameraX),
        int(y - cameraY)
    )


def drawWorldLine(
    position1,
    offset1,
    position2,
    offset2,
    color,
    width=1
):

    x1, y1, direction1 = getRoadPosition(
        position1
    )

    x2, y2, direction2 = getRoadPosition(
        position2
    )

    if direction1 == 0:
        y1 += offset1
    else:
        x1 += offset1

    if direction2 == 0:
        y2 += offset2
    else:
        x2 += offset2

    sx1, sy1 = cameraWorldToScreen(
        x1,
        y1
    )

    sx2, sy2 = cameraWorldToScreen(
        x2,
        y2
    )

    pygame.draw.line(
        screen,
        color,
        (sx1, sy1),
        (sx2, sy2),
        width
    )


def drawRoad():

    screen.fill(GRASS_COLOR)

    start = max(
        0,
        int(userPosition - 900)
    )

    end = min(
        int(totalRoadLength()),
        int(userPosition + 1400)
    )

    p = start

    while p < end:

        nextPosition = min(
            p + 20,
            end
        )

        x1, y1, d1 = getRoadPosition(p)
        x2, y2, d2 = getRoadPosition(nextPosition)

        if d1 == 0:

            corners = [
                (x1, y1 - ROAD_HALF_WIDTH),
                (x2, y2 - ROAD_HALF_WIDTH),
                (x2, y2 + ROAD_HALF_WIDTH),
                (x1, y1 + ROAD_HALF_WIDTH)
            ]

        else:

            corners = [
                (x1 - ROAD_HALF_WIDTH, y1),
                (x2 - ROAD_HALF_WIDTH, y2),
                (x2 + ROAD_HALF_WIDTH, y2),
                (x1 + ROAD_HALF_WIDTH, y1)
            ]

        points = [
            cameraWorldToScreen(x, y)
            for x, y in corners
        ]

        pygame.draw.polygon(
            screen,
            ROAD_COLOR,
            points
        )

        drawWorldLine(
            p,
            -ROAD_HALF_WIDTH,
            nextPosition,
            -ROAD_HALF_WIDTH,
            ROAD_EDGE_COLOR,
            5
        )

        drawWorldLine(
            p,
            ROAD_HALF_WIDTH,
            nextPosition,
            ROAD_HALF_WIDTH,
            ROAD_EDGE_COLOR,
            5
        )

        p = nextPosition

    drawCenterRoadLines(
        start,
        end
    )


def drawCenterRoadLines(
    start,
    end
):

    p = start

    while p < end:

        dashEnd = min(
            p + 35,
            end
        )

        drawWorldLine(
            p,
            0,
            dashEnd,
            0,
            ROAD_LINE_COLOR,
            3
        )

        p += 65


def drawRaceLine(
    position,
    label,
    color
):

    x, y, direction = getRoadPosition(
        position
    )

    sx, sy = cameraWorldToScreen(
        x,
        y
    )

    tile = 15

    if direction == 0:

        for i in range(12):

            c = WHITE if i % 2 == 0 else BLACK

            pygame.draw.rect(
                screen,
                c,
                (
                    sx - 7,
                    sy - ROAD_HALF_WIDTH +
                    i * tile,
                    14,
                    tile
                )
            )

        pygame.draw.rect(
            screen,
            color,
            (
                sx - 8,
                sy - ROAD_HALF_WIDTH - 8,
                16,
                ROAD_HALF_WIDTH * 2 + 16
            ),
            3
        )

    else:

        for i in range(12):

            c = WHITE if i % 2 == 0 else BLACK

            pygame.draw.rect(
                screen,
                c,
                (
                    sx - ROAD_HALF_WIDTH +
                    i * tile,
                    sy - 7,
                    tile,
                    14
                )
            )

        pygame.draw.rect(
            screen,
            color,
            (
                sx - ROAD_HALF_WIDTH - 8,
                sy - 8,
                ROAD_HALF_WIDTH * 2 + 16,
                16
            ),
            3
        )

    text = largeFont.render(
        label,
        True,
        color
    )

    shadow = largeFont.render(
        label,
        True,
        BLACK
    )

    textRect = text.get_rect(
        center=(
            sx,
            sy - ROAD_HALF_WIDTH - 40
        )
    )

    shadowRect = shadow.get_rect(
        center=(
            sx + 2,
            sy - ROAD_HALF_WIDTH - 38
        )
    )

    screen.blit(
        shadow,
        shadowRect
    )

    screen.blit(
        text,
        textRect
    )


CHECKPOINT_DISTANCE = 900
checkpoints = []


def createCheckpoints():

    global checkpoints

    checkpoints = [START_POSITION]

    position = CHECKPOINT_DISTANCE

    while position < totalRoadLength() - 100:

        checkpoints.append(position)

        position += CHECKPOINT_DISTANCE


def updateCheckpoint(
    position,
    checkpoint
):

    for cp in checkpoints:

        if position >= cp and cp > checkpoint:

            checkpoint = cp

    return checkpoint


def drawCheckpoints():

    for cp in checkpoints:

        if abs(cp - userPosition) > 1200:
            continue

        x, y, direction = getRoadPosition(cp)

        sx, sy = cameraWorldToScreen(
            x,
            y
        )

        pygame.draw.circle(
            screen,
            CYAN,
            (sx, sy),
            7
        )

        if direction == 0:

            pygame.draw.line(
                screen,
                CYAN,
                (
                    sx,
                    sy - ROAD_HALF_WIDTH
                ),
                (
                    sx,
                    sy + ROAD_HALF_WIDTH
                ),
                2
            )

        else:

            pygame.draw.line(
                screen,
                CYAN,
                (
                    sx - ROAD_HALF_WIDTH,
                    sy
                ),
                (
                    sx + ROAD_HALF_WIDTH,
                    sy
                ),
                2
            )


def drawPlayer(
    position,
    lane,
    color
):

    x, y = getPlayerWorldPosition(
        position,
        lane
    )

    sx, sy = cameraWorldToScreen(
        x,
        y
    )

    pygame.draw.circle(
        screen,
        BLACK,
        (sx, sy),
        12
    )

    pygame.draw.circle(
        screen,
        color,
        (sx, sy),
        8
    )

    pygame.draw.circle(
        screen,
        WHITE,
        (sx, sy),
        8,
        1
    )


COIN_COUNT = 15
coins = []


def createCoins():

    global coins

    coins = []

    for i in range(COIN_COUNT):

        coins.append(
            350 + i * 230
        )


def drawCoins():

    for position in coins:

        if abs(position - userPosition) > 1000:
            continue

        x, y = getPlayerWorldPosition(
            position,
            1
        )

        sx, sy = cameraWorldToScreen(
            x,
            y
        )

        pygame.draw.circle(
            screen,
            YELLOW,
            (sx, sy),
            9
        )

        pygame.draw.circle(
            screen,
            WHITE,
            (sx, sy),
            9,
            2
        )


def collectCoins():

    global score

    for i in range(len(coins)):

        if abs(coins[i] - userPosition) < 18:

            score += 10

            coins[i] = userPosition + 2000


class Obstacle:

    def __init__(self):

        self.position = 0
        self.offset = -65
        self.speed = 60
        self.movingDown = True
        self.width = 56
        self.height = 26


OBSTACLE_COUNT = 6

obstacles = [
    Obstacle()
    for _ in range(OBSTACLE_COUNT)
]


def createObstacles():

    for i, obstacle in enumerate(obstacles):

        obstacle.position = 650 + i * 500

        obstacle.offset = -65

        obstacle.speed = (
            45 +
            random.randint(0, 25)
        )

        obstacle.movingDown = True


def updateObstacle(
    obstacle,
    dt
):

    if obstacle.movingDown:

        obstacle.offset += (
            obstacle.speed * dt
        )

        if obstacle.offset >= 65:

            obstacle.offset = 65
            obstacle.movingDown = False

    else:

        obstacle.offset -= (
            obstacle.speed * dt
        )

        if obstacle.offset <= -65:

            obstacle.offset = -65
            obstacle.movingDown = True


def getObstaclePosition(obstacle):

    x, y, direction = getRoadPosition(
        obstacle.position
    )

    if direction == 0:

        y += obstacle.offset

    else:

        x += obstacle.offset

    return x, y


def drawObstacle(obstacle):

    x, y = getObstaclePosition(
        obstacle
    )

    sx, sy = cameraWorldToScreen(
        x,
        y
    )

    _, _, direction = getRoadPosition(
        obstacle.position
    )

    if direction == 0:

        rect = pygame.Rect(
            sx - obstacle.width // 2,
            sy - obstacle.height // 2,
            obstacle.width,
            obstacle.height
        )

    else:

        rect = pygame.Rect(
            sx - obstacle.height // 2,
            sy - obstacle.width // 2,
            obstacle.height,
            obstacle.width
        )

    shadowRect = rect.inflate(
        8,
        8
    )

    pygame.draw.rect(
        screen,
        BLACK,
        shadowRect,
        border_radius=5
    )

    pygame.draw.rect(
        screen,
        ORANGE,
        rect,
        border_radius=3
    )

    pygame.draw.rect(
        screen,
        RED,
        rect,
        3,
        border_radius=3
    )

    if direction == 0:

        pygame.draw.line(
            screen,
            WHITE,
            (
                rect.left + 7,
                rect.centery
            ),
            (
                rect.right - 7,
                rect.centery
            ),
            4
        )

    else:

        pygame.draw.line(
            screen,
            WHITE,
            (
                rect.centerx,
                rect.top + 7
            ),
            (
                rect.centerx,
                rect.bottom - 7
            ),
            4
        )


def getPlayerLanePosition(
    position,
    lane
):

    return getPlayerWorldPosition(
        position,
        lane
    )


def collisionWithNormalObstacle(
    position,
    lane
):

    playerX, playerY = getPlayerLanePosition(
        position,
        lane
    )

    for obstacle in obstacles:

        if abs(
            position -
            obstacle.position
        ) > 55:

            continue

        obstacleX, obstacleY = getObstaclePosition(
            obstacle
        )

        if math.hypot(
            playerX - obstacleX,
            playerY - obstacleY
        ) < 40:

            return True

    return False


def playerObstacleCollision(
    position,
    lane
):

    if collisionWithNormalObstacle(
        position,
        lane
    ):

        return True

    return False


def laneSafe(
    position,
    lane
):

    return not playerObstacleCollision(
        position,
        lane
    )


def findSafeLane(
    position,
    currentLane
):

    lanes = [
        currentLane,
        0,
        1,
        2
    ]

    for lane in lanes:

        if 0 <= lane <= 2:

            if laneSafe(
                position + 30,
                lane
            ):

                return lane

    return currentLane


def updateComputer(
    position,
    lane,
    checkpoint,
    dt
):

    lookAhead = 100

    for obstacle in obstacles:

        distanceAhead = (
            obstacle.position -
            position
        )

        if 0 < distanceAhead < lookAhead:

            if not laneSafe(
                obstacle.position,
                lane
            ):

                lane = findSafeLane(
                    position,
                    lane
                )

    position += COMPUTER_SPEED * dt

    position = min(
        position,
        totalRoadLength() - 50
    )

    checkpoint = updateCheckpoint(
        position,
        checkpoint
    )

    if playerObstacleCollision(
        position,
        lane
    ):

        position = checkpoint

        lane = findSafeLane(
            position,
            lane
        )

    return position, lane, checkpoint


def handlePlayerCollision():

    global userPosition
    global userLane

    if playerObstacleCollision(
        userPosition,
        userLane
    ):

        userPosition = userCheckpoint

        userLane = findSafeLane(
            userPosition,
            userLane
        )

        return True

    return False


def drawHUD():

    pygame.draw.rect(
        screen,
        (20, 20, 20),
        (
            10,
            10,
            SCREEN_WIDTH - 20,
            75
        ),
        2
    )

    coinText = font.render(
        f"COINS: {score}",
        True,
        YELLOW
    )

    checkpointText = font.render(
        f"CHECKPOINT: {int(userCheckpoint)}",
        True,
        CYAN
    )

    controls = font.render(
        "A/D: CHANGE LANE    RIGHT: FORWARD    LEFT: BACKWARD",
        True,
        WHITE
    )

    screen.blit(
        coinText,
        (25, 20)
    )

    screen.blit(
        checkpointText,
        (25, 45)
    )

    screen.blit(
        controls,
        (300, 25)
    )


def drawFrame():

    pygame.draw.rect(
        screen,
        WHITE,
        (
            4,
            4,
            SCREEN_WIDTH - 8,
            SCREEN_HEIGHT - 8
        ),
        4
    )

    pygame.draw.rect(
        screen,
        (80, 80, 80),
        (
            10,
            10,
            SCREEN_WIDTH - 20,
            SCREEN_HEIGHT - 20
        ),
        2
    )


def drawFinishBanner():

    if userPosition >= totalRoadLength() - 150:

        text = largeFont.render(
            "FINISH LINE",
            True,
            YELLOW
        )

        rect = text.get_rect(
            center=(
                SCREEN_WIDTH // 2,
                120
            )
        )

        pygame.draw.rect(
            screen,
            BLACK,
            rect.inflate(30, 20)
        )

        pygame.draw.rect(
            screen,
            YELLOW,
            rect.inflate(30, 20),
            3
        )

        screen.blit(
            text,
            rect
        )


def main():

    global userPosition
    global computer1Position
    global computer2Position

    global userCheckpoint
    global computer1Checkpoint
    global computer2Checkpoint

    global userLane
    global computer1Lane
    global computer2Lane

    global cameraX
    global cameraY

    global score

    random.seed()

    createRoad()
    createCoins()
    createObstacles()
    createCheckpoints()

    userPosition = START_POSITION
    computer1Position = START_POSITION
    computer2Position = START_POSITION

    userCheckpoint = START_POSITION
    computer1Checkpoint = START_POSITION
    computer2Checkpoint = START_POSITION

    userLane = 1
    computer1Lane = 0
    computer2Lane = 2

    score = 0

    startX, startY, _ = getRoadPosition(
        START_POSITION
    )

    cameraX = startX - 200
    cameraY = startY - 300

    finishPosition = (
        totalRoadLength() - 50
    )

    running = True

    while running:

        dt = clock.tick(60) / 1000.0

        dt = min(
            dt,
            0.05
        )

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                running = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

                    running = False

                if event.key == pygame.K_a:

                    userLane -= 1

                    userLane = max(
                        0,
                        userLane
                    )

                if event.key == pygame.K_d:

                    userLane += 1

                    userLane = min(
                        2,
                        userLane
                    )

        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:

            userPosition += (
                PLAYER_SPEED * dt
            )

        elif keys[pygame.K_LEFT]:

            userPosition -= (
                BACKWARD_SPEED * dt
            )

        userPosition = max(
            START_POSITION,
            userPosition
        )

        userPosition = min(
            userPosition,
            finishPosition
        )

        computer1Position, computer1Lane, computer1Checkpoint = (
            updateComputer(
                computer1Position,
                computer1Lane,
                computer1Checkpoint,
                dt
            )
        )

        computer2Position, computer2Lane, computer2Checkpoint = (
            updateComputer(
                computer2Position,
                computer2Lane,
                computer2Checkpoint,
                dt
            )
        )

        userCheckpoint = updateCheckpoint(
            userPosition,
            userCheckpoint
        )

        userHit = handlePlayerCollision()

        if userHit:

            userCheckpoint = updateCheckpoint(
                userPosition,
                userCheckpoint
            )

        for obstacle in obstacles:

            updateObstacle(
                obstacle,
                dt
            )

        collectCoins()

        userWorldX, userWorldY = getPlayerWorldPosition(
            userPosition,
            userLane
        )

        targetCameraX = (
            userWorldX - 200
        )

        targetCameraY = (
            userWorldY - 300
        )

        cameraX += (
            targetCameraX - cameraX
        ) * 8.0 * dt

        cameraY += (
            targetCameraY - cameraY
        ) * 8.0 * dt

        drawRoad()

        drawCheckpoints()

        drawRaceLine(
            START_POSITION,
            "START",
            GREEN
        )

        drawRaceLine(
            finishPosition,
            "FINISH",
            YELLOW
        )

        drawCoins()

        for obstacle in obstacles:

            drawObstacle(
                obstacle
            )

        drawPlayer(
            computer1Position,
            computer1Lane,
            BLUE
        )

        drawPlayer(
            userPosition,
            userLane,
            RED
        )

        drawPlayer(
            computer2Position,
            computer2Lane,
            GREEN
        )

        drawHUD()

        drawFinishBanner()

        drawFrame()

        pygame.display.flip()

    pygame.quit()

    sys.exit()


if __name__ == "__main__":
    main()