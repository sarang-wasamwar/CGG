#include <graphics.h>
#include <windows.h>
#include <iostream>
#include <cmath>
#include <cstdlib>
#include <ctime>
#include <cstdio>
using namespace std;
const int SCREEN_WIDTH = 800;
const int SCREEN_HEIGHT = 600;
const double PLAYER_SPEED = 180.0;
const double BACKWARD_SPEED = 180.0;
const double CAMERA_SMOOTH = 8.0;
const int LANE_OFFSET = 55;
const int ROAD_HALF_WIDTH = 90;
double userPosition = 80.0;
double computer1Position = 80.0;
double computer2Position = 80.0;
double cameraX = 0.0;
double cameraY = 0.0;
int score = 0;
void multiply(double point[1][3], double T[3][3]) {
    double result[1][3] = {0};
    for (int i = 0; i < 1; i++) {
        for (int j = 0; j < 3; j++) {
            for (int k = 0; k < 3; k++) {
                result[i][j] += point[i][k] * T[k][j];
            }
        }
    }
    for (int i = 0; i < 1; i++) {
        for (int j = 0; j < 3; j++) {
            point[i][j] = result[i][j];
        }
    }
}
void applyTranslation( double point[1][3], double tx, double ty) {
    double T[3][3] = {
        {1, 0, 0},
        {0, 1, 0},
        {tx, ty, 1}
    };
    multiply(point, T);
}
void bresenhamLine( int x1, int y1, int x2, int y2, int color) {
    int dx = abs(x2 - x1);
    int dy = abs(y2 - y1);
    int sx = (x1 < x2) ? 1 : -1;
    int sy = (y1 < y2) ? 1 : -1;
    int err = dx - dy;
    while (true) {
        if ( x1 >= 0 && x1 < SCREEN_WIDTH && y1 >= 0 && y1 < SCREEN_HEIGHT ) {
            putpixel(x1, y1, color);
        }
        if (x1 == x2 && y1 == y2)
            break;
        int e2 = 2 * err;
        if (e2 > -dy) {
            err -= dy;
            x1 += sx;
        }
        if (e2 < dx) {
            err += dx;
            y1 += sy;
        }
    }
}
void bresenhamCircle( int xc, int yc, int r, int color ) {
    int x = 0;
    int y = r;
    int d = 3 - 2 * r;
    while (y >= x)
    {
        putpixel(xc + x, yc + y, color);
        putpixel(xc - x, yc + y, color);
        putpixel(xc + x, yc - y, color);
        putpixel(xc - x, yc - y, color);
        putpixel(xc + y, yc + x, color);
        putpixel(xc - y, yc + x, color);
        putpixel(xc + y, yc - x, color);
        putpixel(xc - y, yc - x, color);
        if (d < 0) {
            d += 4 * x + 6;
        }
        else {
            d += 4 * (x - y) + 10;
            y--;
        }
        x++;
    }
}
void filledCircle( int x, int y, int radius, int color) {
    setfillstyle( SOLID_FILL, color );
    fillellipse( x, y, radius, radius );
}
struct Segment {
    double x1;
    double y1;
    double x2;
    double y2;
    double length;
    int direction;
};
const int SEGMENT_COUNT = 8;
Segment road[SEGMENT_COUNT];
void createRoad() {
    road[0] = { 0, 300, 800, 300, 800, 0 };
    road[1] = { 800, 300, 800, 650, 350, 1 };
    road[2] = { 800, 650, 1600, 650, 800, 0 };
    road[3] = { 1600, 650, 1600, 250, 400, 1 };
    road[4] = { 1600, 250, 2500, 250, 900, 0 };
    road[5] = { 2500, 250, 2500, 650, 400, 1 };
    road[6] = { 2500, 650, 3400, 650, 900, 0 };
    road[7] = { 3400, 650, 3400, 250,400, 1 };
}
double totalRoadLength() {
    double total = 0;
    for (int i = 0; i < SEGMENT_COUNT; i++) {
        total += road[i].length;
    }
    return total;
}
void getRoadPosition( double position, double &x, double &y, int &direction) {
    double remaining = position;
    for (int i = 0; i < SEGMENT_COUNT; i++) {
        if (remaining <= road[i].length) {
            double ratio = remaining / road[i].length;
            x = road[i].x1 + (road[i].x2 - road[i].x1) * ratio;
            y = road[i].y1 + (road[i].y2 - road[i].y1) * ratio;
            direction = road[i].direction;
            return;
        }
        remaining -= road[i].length;
    }
    x = road[SEGMENT_COUNT - 1].x2;
    y = road[SEGMENT_COUNT - 1].y2;
    direction = road[SEGMENT_COUNT - 1].direction;
}
void getPlayerWorldPosition( double position, int lane, double &x, double &y) {
    int direction;
    getRoadPosition( position, x, y, direction );
    double offset = 0;
    if (lane == 0)
        offset = -LANE_OFFSET;
    if (lane == 1)
        offset = 0;
    if (lane == 2)
        offset = LANE_OFFSET;
    if (direction == 0) {
        y += offset;
    } else {
        x += offset;
    }
}
void worldToScreen( double worldX, double worldY, int &screenX, int &screenY) {
    double point[1][3] = { { worldX, worldY, 1 } };
    applyTranslation( point, -cameraX, -cameraY );
    screenX = (int)point[0][0];
    screenY = (int)point[0][1];
}
void drawRoadLine(
    double position1,
    int offset1,
    double position2,
    int offset2,
    int color)
{
    double x1, y1;
    double x2, y2;
    int direction1;
    int direction2;
    getRoadPosition(
        position1,
        x1,
        y1,
        direction1
    );
    getRoadPosition(
        position2,
        x2,
        y2,
        direction2
    );
    if (direction1 == 0)
        y1 += offset1;
    else
        x1 += offset1;
    if (direction2 == 0)
        y2 += offset2;
    else
        x2 += offset2;
    int sx1, sy1;
    int sx2, sy2;
    worldToScreen(
        x1,
        y1,
        sx1,
        sy1
    );
    worldToScreen(
        x2,
        y2,
        sx2,
        sy2
    );
    bresenhamLine(
        sx1,
        sy1,
        sx2,
        sy2,
        color
    );
}
void drawRoad()
{
    double start =
        max(
            0.0,
            userPosition - 750
        );
    double end =
        min(
            totalRoadLength(),
            userPosition + 1200
        );
    for (
        double p = start;
        p < end;
        p += 5
    )
    {
        double next =
            min(
                p + 5,
                end
            );
        drawRoadLine(
            p,
            -ROAD_HALF_WIDTH,
            next,
            -ROAD_HALF_WIDTH,
            LIGHTGRAY
        );
        drawRoadLine(
            p,
            0,
            next,
            0,
            DARKGRAY
        );
        drawRoadLine(
            p,
            ROAD_HALF_WIDTH,
            next,
            ROAD_HALF_WIDTH,
            LIGHTGRAY
        );
    }
}
void drawStartLine()
{
    double x;
    double y;
    int direction;
    getRoadPosition(
        80,
        x,
        y,
        direction
    );
    int sx;
    int sy;
    worldToScreen(
        x,
        y,
        sx,
        sy
    );
    if (direction == 0)
    {
        bresenhamLine(
            sx,
            sy - ROAD_HALF_WIDTH,
            sx,
            sy + ROAD_HALF_WIDTH,
            GREEN
        );
    }
    else
    {
        bresenhamLine(
            sx - ROAD_HALF_WIDTH,
            sy,
            sx + ROAD_HALF_WIDTH,
            sy,
            GREEN
        );
    }
    setcolor(GREEN);
    settextstyle(
        DEFAULT_FONT,
        HORIZ_DIR,
        2
    );
    outtextxy(
        sx - 35,
        sy - 120,
        (char*)"START"
    );
}
void drawPlayer(
    double position,
    int lane,
    int color)
{
    double x;
    double y;
    getPlayerWorldPosition(
        position,
        lane,
        x,
        y
    );
    int sx;
    int sy;
    worldToScreen(
        x,
        y,
        sx,
        sy
    );
    filledCircle(
        sx,
        sy,
        8,
        color
    );
}
const int COIN_COUNT = 15;
double coins[COIN_COUNT];
void createCoins()
{
    for (int i = 0;
         i < COIN_COUNT;
         i++)
    {
        coins[i] =
            350 +
            i * 230;
    }
}
void drawCoins()
{
    for (int i = 0;
         i < COIN_COUNT;
         i++)
    {
        double x;
        double y;
        getPlayerWorldPosition(
            coins[i],
            1,
            x,
            y
        );
        int sx;
        int sy;
        worldToScreen(
            x,
            y,
            sx,
            sy
        );
        bresenhamCircle(
            sx,
            sy,
            8,
            YELLOW
        );
    }
}
void collectCoins()
{
    for (int i = 0;
         i < COIN_COUNT;
         i++)
    {
        if (
            fabs(
                coins[i]
                - userPosition
            ) < 15
        )
        {
            score += 10;
            coins[i] =
                userPosition
                + 1500;
        }
    }
}
struct Obstacle
{
    double position;
    double offset;
    double speed;
    bool movingDown;
};
const int OBSTACLE_COUNT = 6;
Obstacle obstacles[
    OBSTACLE_COUNT
];
void createObstacles()
{
    for (int i = 0;
         i < OBSTACLE_COUNT;
         i++)
    {
        obstacles[i].position =
            600 +
            i * 500;
        obstacles[i].offset =
            -100;
        obstacles[i].speed =
            70 +
            rand() % 40;
        obstacles[i].movingDown =
            true;
    }
}
void updateObstacle(
    Obstacle &ob,
    double dt)
{
    if (ob.movingDown)
    {
        ob.offset +=
            ob.speed * dt;
        if (ob.offset >= 100)
        {
            ob.offset = 100;
            ob.movingDown = false;
        }
    }
    else
    {
        ob.offset -=
            ob.speed * dt;
        if (ob.offset <= -100)
        {
            ob.offset = -100;
            ob.movingDown = true;
        }
    }
}
void drawObstacle(
    Obstacle &ob)
{
    double x;
    double y;
    int direction;
    getRoadPosition(
        ob.position,
        x,
        y,
        direction
    );
    if (direction == 0)
    {
        y += ob.offset;
    }
    else
    {
        x += ob.offset;
    }
    int sx;
    int sy;
    worldToScreen(
        x,
        y,
        sx,
        sy
    );
    setcolor(RED);
    if (direction == 0)
    {
        bresenhamLine(
            sx,
            sy - 22,
            sx,
            sy + 22,
            RED
        );
        bresenhamLine(
            sx - 4,
            sy - 22,
            sx - 4,
            sy + 22,
            RED
        );
    }
    else
    {
        bresenhamLine(
            sx - 22,
            sy,
            sx + 22,
            sy,
            RED
        );
        bresenhamLine(
            sx - 22,
            sy - 4,
            sx + 22,
            sy - 4,
            RED
        );
    }
}
void drawHUD()
{
    setcolor(WHITE);
    settextstyle(
        DEFAULT_FONT,
        HORIZ_DIR,
        1
    );
    char text[50];
    sprintf(
        text,
        "COINS: %d",
        score
    );
    outtextxy(
        20,
        25,
        text
    );
    outtextxy(
        500,
        25,
        (char*)"RIGHT = FORWARD"
    );
    outtextxy(
        500,
        45,
        (char*)"LEFT = BACKWARD"
    );
}
int main() {
    srand( (unsigned int) time(NULL) );
    int gd = DETECT;
    int gm;
    initgraph( &gd, &gm, (char*)"");
    createRoad();
    createCoins();
    createObstacles();
    userPosition = 80.0;
    computer1Position = 80.0;
    computer2Position = 80.0;
    double startX;
    double startY;
    int startDirection;
    getRoadPosition( userPosition, startX, startY, startDirection );
    cameraX = startX - 200;
    cameraY = startY - 300;
    bool running = true;
    DWORD previousTime = GetTickCount();
    while (running) {
        DWORD currentTime = GetTickCount();
        double dt = (currentTime - previousTime) / 1000.0;
        previousTime = currentTime;
        if (dt > 0.05)
            dt = 0.05;
        if ( GetAsyncKeyState( VK_ESCAPE ) & 0x8000 ) {
            running = false;
            break;
        }
        if ( GetAsyncKeyState( VK_RIGHT ) & 0x8000 ) {
            userPosition += PLAYER_SPEED * dt;
        } else if ( GetAsyncKeyState( VK_LEFT ) & 0x8000 ) { // LEFT = BACKWARD
            userPosition -= BACKWARD_SPEED * dt;
        }
        if (userPosition < 80){
            userPosition = 80;
        }
        double endPosition = totalRoadLength() - 50;
        if ( userPosition > endPosition ) {
            userPosition = endPosition;
        }
        computer1Position += PLAYER_SPEED * dt;
        computer2Position += PLAYER_SPEED * dt;
        if ( computer1Position > endPosition ) {
            computer1Position = endPosition;
        }
        if ( computer2Position > endPosition ) {
            computer2Position = endPosition;
        }
        double userWorldX;
        double userWorldY;
        getPlayerWorldPosition( userPosition, 1, userWorldX, userWorldY );
        double targetCameraX = userWorldX - 200;
        double targetCameraY = userWorldY - 300;
        cameraX += ( targetCameraX - cameraX ) * CAMERA_SMOOTH * dt;
        cameraY += ( targetCameraY - cameraY ) * CAMERA_SMOOTH * dt;
        for (int i = 0; i < OBSTACLE_COUNT; i++) {
            updateObstacle ( obstacles[i], dt );
        }
        collectCoins();
        cleardevice();
        drawRoad();
        if (userPosition < 500) {
            drawStartLine();
        }
        drawCoins();
        for (int i = 0; i < OBSTACLE_COUNT; i++) {
            drawObstacle( obstacles[i] );
        }
        drawPlayer( computer1Position, 0, BLUE );
        drawPlayer( userPosition, 1, RED );
        drawPlayer( computer2Position, 2, GREEN );
        drawHUD();
        delay(5);
    }
    closegraph();
    return 0;
}
