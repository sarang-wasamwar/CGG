#include <graphics.h>
#include <conio.h>
#include <math.h>
#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <vector>
#include <string>
#include <algorithm>

using namespace std;

const int SCREEN_WIDTH = 1000;
const int SCREEN_HEIGHT = 700;

const double PLAYER_SPEED = 210.0;
const double AI_SPEED = 205.0;
const double MAX_REVERSE = 70.0;

const double ROAD_WIDTH = 180.0;
const double ROAD_HALF_WIDTH = 90.0;
const double LANE_WIDTH = 60.0;

const double START_POSITION = 0.0;
const int COIN_RADIUS = 12;
const double COIN_COLLECT_DISTANCE = 28.0;

struct Point {
    double x, y;
    Point() : x(0), y(0) {}
    Point(double X, double Y) : x(X), y(Y) {}
};

struct Obstacle {
    double position;
    double offset;
    double speed;
    int direction;

    Obstacle(double p, double s, int side) {
        position = p;
        speed = s;
        offset = (side == 1) ? -ROAD_HALF_WIDTH + 25 : ROAD_HALF_WIDTH - 25;
        direction = (side == 1) ? 1 : -1;
    }

    void update(double dt) {
        offset += speed * direction * dt;
        double limit = ROAD_HALF_WIDTH - 25;
        if (offset >= limit) {
            offset = limit;
            direction = -1;
        }
        if (offset <= -limit) {
            offset = -limit;
            direction = 1;
        }
    }
};

struct Coin {
    double position;
    int lane;
    bool collected;

    Coin(double p, int l) {
        position = p;
        lane = l;
        collected = false;
    }
};

struct Racer {
    string name;
    int color;
    int lane;
    bool isPlayer;
    double aiSpeed;
    double reaction;
    double risk;

    double position;
    double checkpoint;
    double speed;
    bool finished;
    double finishTime;
    bool hasFinishTime;
    int collisionCount;
    double stunTimer;

    Racer(string n, int c, int l, bool player, double ais, double react, double r)
        : name(n), color(c), lane(l), isPlayer(player),
          aiSpeed(ais), reaction(react), risk(r) {
        reset();
    }

    void reset() {
        position = START_POSITION;
        checkpoint = START_POSITION;
        speed = 0;
        finished = false;
        finishTime = 0;
        hasFinishTime = false;
        collisionCount = 0;
        stunTimer = 0;
    }
};

vector<Point> roadPoints;
vector<double> roadDistances;
vector<Point> roadTangents;
vector<Obstacle> obstacles;
vector<Coin> coins;
vector<Racer> racers;

double roadTotalLength = 0;
double finishPosition = 0;
double cameraX = 0;
double cameraY = 0;
double raceTime = 0;
double userPosition = 0;

bool raceStarted = false;
bool menuActive = true;
int coinCount = 0;
int currentLevel = 2;
int winnerIndex = -1;

int BLACK_C = BLACK;
int WHITE_C = WHITE;
int RED_C = RED;
int BLUE_C = BLUE;
int GREEN_C = GREEN;
int YELLOW_C = YELLOW;
int CYAN_C = CYAN;
int ORANGE_C = LIGHTRED;

void setBGIColor(int c) {
    setcolor(c);
}

void bresenhamLine(int x1, int y1, int x2, int y2, int color) {
    int dx = abs(x2 - x1);
    int dy = abs(y2 - y1);
    int sx = x1 < x2 ? 1 : -1;
    int sy = y1 < y2 ? 1 : -1;
    int err = dx - dy;

    while (true) {
        if (x1 >= 0 && x1 < SCREEN_WIDTH && y1 >= 0 && y1 < SCREEN_HEIGHT)
            putpixel(x1, y1, color);

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

void bresenhamCircle(int cx, int cy, int radius, int color) {
    int x = 0;
    int y = radius;
    int d = 3 - 2 * radius;

    while (x <= y) {
        putpixel(cx + x, cy + y, color);
        putpixel(cx - x, cy + y, color);
        putpixel(cx + x, cy - y, color);
        putpixel(cx - x, cy - y, color);
        putpixel(cx + y, cy + x, color);
        putpixel(cx - y, cy + x, color);
        putpixel(cx + y, cy - x, color);
        putpixel(cx - y, cy - x, color);

        if (d < 0)
            d += 4 * x + 6;
        else {
            d += 4 * (x - y) + 10;
            y--;
        }
        x++;
    }
}

void floodFillCircle(int cx, int cy, int radius, int fillColor, int borderColor) {
    setcolor(borderColor);
    bresenhamCircle(cx, cy, radius, borderColor);
    setfillstyle(SOLID_FILL, fillColor);
    floodfill(cx, cy, borderColor);
}

Point translatePoint(double x, double y, double tx, double ty) {
    return Point(x + tx, y + ty);
}

Point rotateVector(double x, double y, double degrees) {
    double a = degrees * 3.141592653589793 / 180.0;
    return Point(x * cos(a) - y * sin(a), x * sin(a) + y * cos(a));
}

void createRoad() {
    roadPoints.clear();
    roadDistances.clear();
    roadTangents.clear();

    roadPoints.push_back(Point(0, 350));
    double heading = 0;
    double x = 0;
    double y = 350;

    double step = 10;

    int types[] = {
        0,1,0,1,0,1,0,1,0,1,0,1,0,1,0
    };

    double values[] = {
        650,90,650,-90,800,-90,650,90,850,90,650,-90,800,-90,750
    };

    int v = 0;

    while (v < 15) {
        if (types[v] == 0) {
            double distance = values[v];
            int count = (int)(distance / step);
            int i;
            for (i = 0; i < count; i++) {
                Point d = rotateVector(step, 0, heading);
                x += d.x;
                y += d.y;
                roadPoints.push_back(Point(x, y));
            }
        } else {
            double turnAngle = values[v];
            double radius = 180;
            double arcLength = radius * 3.141592653589793 * fabs(turnAngle) / 180.0;
            int count = (int)(arcLength / step);
            if (count < 2) count = 2;

            double angleStep = turnAngle / count;
            int i;
            for (i = 0; i < count; i++) {
                Point d = rotateVector(step, 0, heading);
                x += d.x;
                y += d.y;
                roadPoints.push_back(Point(x, y));
                heading += angleStep;
            }
        }
        v++;
    }

    roadDistances.push_back(0);
    double total = 0;

    int i;
    for (i = 0; i < (int)roadPoints.size(); i++) {
        double dx, dy;

        if (i == 0) {
            dx = roadPoints[1].x - roadPoints[0].x;
            dy = roadPoints[1].y - roadPoints[0].y;
        } else if (i == (int)roadPoints.size() - 1) {
            dx = roadPoints[i].x - roadPoints[i-1].x;
            dy = roadPoints[i].y - roadPoints[i-1].y;
        } else {
            dx = roadPoints[i+1].x - roadPoints[i-1].x;
            dy = roadPoints[i+1].y - roadPoints[i-1].y;
        }

        double len = sqrt(dx * dx + dy * dy);
        if (len == 0)
            roadTangents.push_back(Point(1,0));
        else
            roadTangents.push_back(Point(dx / len, dy / len));

        if (i > 0) {
            double sx = roadPoints[i].x - roadPoints[i-1].x;
            double sy = roadPoints[i].y - roadPoints[i-1].y;
            total += sqrt(sx * sx + sy * sy);
            roadDistances.push_back(total);
        }
    }

    roadTotalLength = total;
}

void getRoadPosition(double position, double &x, double &y, double &tx, double &ty) {
    if (position < 0) position = 0;
    if (position > roadTotalLength) position = roadTotalLength;

    int i;
    for (i = 1; i < (int)roadDistances.size(); i++) {
        if (position <= roadDistances[i]) {
            double previous = roadDistances[i-1];
            double segment = roadDistances[i] - previous;
            double ratio = segment == 0 ? 0 : (position - previous) / segment;

            x = roadPoints[i-1].x +
                (roadPoints[i].x - roadPoints[i-1].x) * ratio;

            y = roadPoints[i-1].y +
                (roadPoints[i].y - roadPoints[i-1].y) * ratio;

            tx = roadTangents[i].x;
            ty = roadTangents[i].y;
            return;
        }
    }

    x = roadPoints.back().x;
    y = roadPoints.back().y;
    tx = roadTangents.back().x;
    ty = roadTangents.back().y;
}

void getWorldPosition(double position, double offset, double &x, double &y) {
    double px, py, tx, ty;
    getRoadPosition(position, px, py, tx, ty);

    double nx = -ty;
    double ny = tx;

    x = px + nx * offset;
    y = py + ny * offset;
}

void worldToScreen(double x, double y, int &sx, int &sy) {
    sx = (int)(x - cameraX);
    sy = (int)(y - cameraY);
}

void drawRoad() {
    setfillstyle(SOLID_FILL, GREEN);
    bar(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT);

    int start = 0;
    int end = (int)roadPoints.size() - 1;

    double centerX = cameraX + SCREEN_WIDTH / 2.0;
    double centerY = cameraY + SCREEN_HEIGHT / 2.0;

    double nearest = 0;
    double best = 1e30;

    int i;
    for (i = 0; i < (int)roadPoints.size(); i += 5) {
        double dx = roadPoints[i].x - centerX;
        double dy = roadPoints[i].y - centerY;
        double d = dx * dx + dy * dy;
        if (d < best) {
            best = d;
            nearest = roadDistances[i];
        }
    }

    while (start < end && roadDistances[start] < nearest - 900) start++;
    while (end > start && roadDistances[end] > nearest + 1400) end--;

    setfillstyle(SOLID_FILL, DARKGRAY);

    for (i = start; i < end; i++) {
        double x1 = roadPoints[i].x;
        double y1 = roadPoints[i].y;
        double x2 = roadPoints[i+1].x;
        double y2 = roadPoints[i+1].y;

        double tx1 = roadTangents[i].x;
        double ty1 = roadTangents[i].y;
        double tx2 = roadTangents[i+1].x;
        double ty2 = roadTangents[i+1].y;

        double lx1 = x1 - ty1 * ROAD_HALF_WIDTH;
        double ly1 = y1 + tx1 * ROAD_HALF_WIDTH;
        double rx1 = x1 + ty1 * ROAD_HALF_WIDTH;
        double ry1 = y1 - tx1 * ROAD_HALF_WIDTH;

        double lx2 = x2 - ty2 * ROAD_HALF_WIDTH;
        double ly2 = y2 + tx2 * ROAD_HALF_WIDTH;
        double rx2 = x2 + ty2 * ROAD_HALF_WIDTH;
        double ry2 = y2 - tx2 * ROAD_HALF_WIDTH;

        int poly[8];
        worldToScreen(lx1, ly1, poly[0], poly[1]);
        worldToScreen(rx1, ry1, poly[2], poly[3]);
        worldToScreen(rx2, ry2, poly[4], poly[5]);
        worldToScreen(lx2, ly2, poly[6], poly[7]);

        fillpoly(4, poly);
    }

    for (i = start; i < end; i += 2) {
        int x1, y1, x2, y2;

        double tx = roadTangents[i].x;
        double ty = roadTangents[i].y;

        double lx = roadPoints[i].x - ty * ROAD_HALF_WIDTH;
        double ly = roadPoints[i].y + tx * ROAD_HALF_WIDTH;

        double rx = roadPoints[i].x + ty * ROAD_HALF_WIDTH;
        double ry = roadPoints[i].y - tx * ROAD_HALF_WIDTH;

        worldToScreen(lx, ly, x1, y1);
        worldToScreen(rx, ry, x2, y2);

        bresenhamLine(x1, y1, x2, y2, LIGHTGRAY);
    }

    setcolor(WHITE);

    double position = roadDistances[start];
    while (position < roadDistances[end]) {
        double dashEnd = position + 35;
        if (dashEnd > roadDistances[end]) dashEnd = roadDistances[end];

        int lane;
        for (lane = -1; lane <= 1; lane += 2) {
            double p = position;
            while (p <= dashEnd) {
                double x, y;
                getWorldPosition(p, lane * LANE_WIDTH / 2.0, x, y);
                int sx, sy;
                worldToScreen(x, y, sx, sy);

                if (sx >= 0 && sx < SCREEN_WIDTH && sy >= 0 && sy < SCREEN_HEIGHT)
                    putpixel(sx, sy, WHITE);

                p += 4;
            }
        }

        position += 70;
    }
}

void drawFrame() {
    bresenhamLine(4,4,SCREEN_WIDTH-4,4,WHITE);
    bresenhamLine(SCREEN_WIDTH-4,4,SCREEN_WIDTH-4,SCREEN_HEIGHT-4,WHITE);
    bresenhamLine(SCREEN_WIDTH-4,SCREEN_HEIGHT-4,4,SCREEN_HEIGHT-4,WHITE);
    bresenhamLine(4,SCREEN_HEIGHT-4,4,4,WHITE);
}

void drawTextCenter(const char *text, int x, int y, int color, int size) {
    setcolor(color);
    settextstyle(DEFAULT_FONT, HORIZ_DIR, size);
    int w = textwidth((char*)text);
    outtextxy(x - w / 2, y, (char*)text);
}

void drawMenu() {
    setfillstyle(SOLID_FILL, GREEN);
    bar(0,0,SCREEN_WIDTH,SCREEN_HEIGHT);

    setfillstyle(SOLID_FILL, DARKGRAY);
    bar(150,0,850,SCREEN_HEIGHT);

    setcolor(LIGHTGRAY);
    setlinestyle(SOLID_LINE,0,3);
    line(150,0,150,SCREEN_HEIGHT);
    line(850,0,850,SCREEN_HEIGHT);
    setlinestyle(SOLID_LINE,0,1);

    drawTextCenter("FUN RACE & PARKOUR",500,55,WHITE,4);
    drawTextCenter("SELECT LEVEL",500,120,YELLOW,3);

    const char *names[3] = {"LEVEL 1","LEVEL 2","LEVEL 3"};
    const char *desc[3] = {"STRAIGHT ROAD","CURVED ROAD","PARKOUR ROAD"};
    int colors[3] = {GREEN,BLUE,RED};

    int y = 200;
    int i;

    for (i = 0; i < 3; i++) {
        setfillstyle(SOLID_FILL, BLACK);
        bar(250,y,750,y+85);

        setcolor(colors[i]);
        rectangle(250,y,750,y+85);
        rectangle(252,y+2,748,y+83);

        settextstyle(DEFAULT_FONT,HORIZ_DIR,3);
        outtextxy(275,y+15,(char*)names[i]);

        setcolor(WHITE);
        settextstyle(DEFAULT_FONT,HORIZ_DIR,2);
        outtextxy(275,y+52,(char*)desc[i]);

        setcolor(YELLOW);
        char key[2];
        key[0] = '1' + i;
        key[1] = '\0';
        outtextxy(705,y+28,key);

        y += 110;
    }

    drawTextCenter("Press 1, 2 or 3 to select a level",500,570,WHITE,2);
    drawTextCenter("ESC - Quit",500,610,WHITE,2);
}

void createCoins() {
    coins.clear();

    int positions[] = {
        350,500,650,800,950,
        1100,1250,1400,1550,1700,
        1850,2000,2150,2300,2450,
        2600,2750,2900,3050,3200,
        3350,3500,3650,3800,3950,
        4100,4250,4400,4550,4700
    };

    int i;
    for (i = 0; i < 30; i++) {
        if (positions[i] < roadTotalLength - 100)
            coins.push_back(Coin(positions[i],0));
    }
}

void drawCoin(const Coin &coin) {
    if (coin.collected) return;

    double x,y;
    getWorldPosition(coin.position,coin.lane * LANE_WIDTH,x,y);

    int sx,sy;
    worldToScreen(x,y,sx,sy);

    if (sx < -20 || sx > SCREEN_WIDTH+20 || sy < -20 || sy > SCREEN_HEIGHT+20)
        return;

    floodFillCircle(sx,sy,COIN_RADIUS,YELLOW,LIGHTRED);
    bresenhamCircle(sx,sy,COIN_RADIUS-4,LIGHTRED);
    bresenhamCircle(sx-4,sy-4,3,WHITE);
}

void createObstacles() {
    obstacles.clear();

    int positions[] = {
        650,1250,1900,2550,3200,
        3850,4500,5150,5800,6450
    };

    int i;
    for (i = 0; i < 10; i++) {
        int speed = 55 + rand() % 31;
        obstacles.push_back(Obstacle(positions[i],speed,i % 2 == 0 ? 1 : -1));
    }
}

void drawObstacle(const Obstacle &ob) {
    double x,y;
    getWorldPosition(ob.position,ob.offset,x,y);

    int sx,sy;
    worldToScreen(x,y,sx,sy);

    if (sx < -60 || sx > SCREEN_WIDTH+60 || sy < -60 || sy > SCREEN_HEIGHT+60)
        return;

    setfillstyle(SOLID_FILL, LIGHTRED);
    bar(sx-40,sy-25,sx+40,sy+25);

    setcolor(BLACK);
    rectangle(sx-40,sy-25,sx+40,sy+25);

    setfillstyle(SOLID_FILL, RED);
    bar(sx-28,sy-14,sx+28,sy+14);

    setcolor(WHITE);
    line(sx-20,sy,sx+20,sy);
}

void drawRacer(double position, int lane, int color, bool player) {
    double x,y;
    getWorldPosition(position,player ? 0 : lane * LANE_WIDTH,x,y);

    int sx,sy;
    worldToScreen(x,y,sx,sy);

    if (sx < -30 || sx > SCREEN_WIDTH+30 || sy < -30 || sy > SCREEN_HEIGHT+30)
        return;

    floodFillCircle(sx,sy,player ? 16 : 15,color,BLACK);

    if (player)
        bresenhamCircle(sx,sy,11,WHITE);
    else
        bresenhamCircle(sx,sy,10,WHITE);
}

bool obstacleCollision(const Racer &racer) {
    double rx,ry;
    getWorldPosition(racer.position,racer.lane * LANE_WIDTH,rx,ry);

    int i;
    for (i = 0; i < (int)obstacles.size(); i++) {
        if (fabs(racer.position - obstacles[i].position) > 60)
            continue;

        double ox,oy;
        getWorldPosition(obstacles[i].position,obstacles[i].offset,ox,oy);

        double dx = rx - ox;
        double dy = ry - oy;

        if (sqrt(dx*dx + dy*dy) < 52)
            return true;
    }

    return false;
}

void updateCheckpoint(Racer &racer) {
    double distance = 900;
    double cp = floor(racer.position / distance) * distance;

    if (cp > racer.checkpoint)
        racer.checkpoint = cp;
}

void handleCollision(Racer &racer) {
    if (racer.finished) return;

    if (obstacleCollision(racer)) {
        racer.position = racer.checkpoint - 15;
        if (racer.position < START_POSITION)
            racer.position = START_POSITION;

        racer.speed = 0;
        racer.stunTimer = 0.65;
        racer.collisionCount++;
    }
}

int nearestObstacleAhead(double position, int &index) {
    double nearest = 1e30;
    index = -1;

    int i;
    for (i = 0; i < (int)obstacles.size(); i++) {
        double d = obstacles[i].position - position;
        if (d > 0 && d < nearest) {
            nearest = d;
            index = i;
        }
    }

    return index;
}

void updateAI(Racer &racer, double dt) {
    if (racer.finished) return;

    if (racer.stunTimer > 0) {
        racer.stunTimer -= dt;
        return;
    }

    int obstacleIndex;
    nearestObstacleAhead(racer.position,obstacleIndex);

    double targetSpeed = racer.aiSpeed;

    if (obstacleIndex >= 0) {
        double distance = obstacles[obstacleIndex].position - racer.position;
        double relativeOffset = fabs(obstacles[obstacleIndex].offset);

        if (racer.risk < 0.5) {
            if (distance < 350 && relativeOffset < 55) targetSpeed = 120;
            if (distance < 200 && relativeOffset < 60) targetSpeed = 65;
            if (distance < 100 && relativeOffset < 65) targetSpeed = 35;
        } else {
            if (distance < 250 && relativeOffset < 45) targetSpeed = 170;
            if (distance < 130 && relativeOffset < 50) targetSpeed = 110;
            if (distance < 70 && relativeOffset < 55) targetSpeed = 50;
        }
    }

    if (racer.speed < targetSpeed) {
        racer.speed += 400 * racer.reaction * dt;
        if (racer.speed > targetSpeed)
            racer.speed = targetSpeed;
    } else if (racer.speed > targetSpeed) {
        racer.speed -= 500 * racer.reaction * dt;
        if (racer.speed < targetSpeed)
            racer.speed = targetSpeed;
    }

    racer.position += racer.speed * dt;

    if (racer.position > finishPosition)
        racer.position = finishPosition;

    updateCheckpoint(racer);
    handleCollision(racer);
}

void collectCoins(Racer &racer) {
    if (!racer.isPlayer) return;

    double px,py;
    getWorldPosition(racer.position,racer.lane * LANE_WIDTH,px,py);

    int i;
    for (i = 0; i < (int)coins.size(); i++) {
        if (coins[i].collected) continue;

        double cx,cy;
        getWorldPosition(coins[i].position,coins[i].lane * LANE_WIDTH,cx,cy);

        double dx = px-cx;
        double dy = py-cy;

        if (sqrt(dx*dx + dy*dy) < COIN_COLLECT_DISTANCE) {
            coins[i].collected = true;
            coinCount++;
        }
    }
}

void drawRaceMarker(double position,const char *label,int color) {
    double x,y,tx,ty;
    getRoadPosition(position,x,y,tx,ty);

    double nx = -ty;
    double ny = tx;

    int x1,y1,x2,y2;
    worldToScreen(x + nx*ROAD_HALF_WIDTH,y + ny*ROAD_HALF_WIDTH,x1,y1);
    worldToScreen(x - nx*ROAD_HALF_WIDTH,y - ny*ROAD_HALF_WIDTH,x2,y2);

    bresenhamLine(x1,y1,x2,y2,color);

    int sx,sy;
    worldToScreen(x,y,sx,sy);

    setcolor(color);
    settextstyle(DEFAULT_FONT,HORIZ_DIR,2);
    outtextxy(sx-35,sy-(int)ROAD_HALF_WIDTH-25,(char*)label);
}

void drawHUD() {
    setfillstyle(SOLID_FILL,BLACK);
    bar(0,0,SCREEN_WIDTH,105);

    setcolor(WHITE);
    settextstyle(DEFAULT_FONT,HORIZ_DIR,3);
    outtextxy(10,12,(char*)"Fun Race & Parkour");

    char buffer[100];

    sprintf(buffer,"TIME: %05.1fs",raceTime);
    setcolor(YELLOW);
    settextstyle(DEFAULT_FONT,HORIZ_DIR,2);
    outtextxy(370,20,buffer);

    sprintf(buffer,"COINS: %d",coinCount);
    outtextxy(700,20,buffer);

    setcolor(WHITE);
    outtextxy(10,52,(char*)"RIGHT: ACCELERATE   LEFT: BRAKE / REVERSE   ESC: QUIT");

    int i;
    for (i = 0; i < (int)racers.size(); i++) {
        int progress = 0;
        if (finishPosition > 0)
            progress = (int)(racers[i].position / finishPosition * 100);

        if (progress > 100) progress = 100;

        sprintf(buffer,"%s: %3d%%",racers[i].name.c_str(),progress);
        setcolor(racers[i].color);
        outtextxy(10+i*150,88,buffer);
    }
}

void drawFinishResults() {
    if (winnerIndex < 0) return;

    setfillstyle(SOLID_FILL,BLACK);
    bar(150,130,850,620);

    setcolor(racers[winnerIndex].color);
    settextstyle(DEFAULT_FONT,HORIZ_DIR,4);

    char title[100];
    sprintf(title,"%s WINS!",racers[winnerIndex].name.c_str());

    int w = textwidth(title);
    outtextxy(500-w/2,160,title);

    vector<int> order;
    int i;
    for (i = 0; i < (int)racers.size(); i++)
        order.push_back(i);

    for (i = 0; i < (int)order.size(); i++) {
        int j;
        for (j = i+1; j < (int)order.size(); j++) {
            double ti = racers[order[i]].hasFinishTime ? racers[order[i]].finishTime : 999999;
            double tj = racers[order[j]].hasFinishTime ? racers[order[j]].finishTime : 999999;

            if (tj < ti) {
                int temp = order[i];
                order[i] = order[j];
                order[j] = temp;
            }
        }
    }

    settextstyle(DEFAULT_FONT,HORIZ_DIR,2);

    for (i = 0; i < (int)order.size(); i++) {
        int r = order[i];
        char result[150];

        if (racers[r].hasFinishTime)
            sprintf(result,"%d. %s   %.2fs   Hits: %d",
                    i+1,racers[r].name.c_str(),
                    racers[r].finishTime,racers[r].collisionCount);
        else
            sprintf(result,"%d. %s   --   Hits: %d",
                    i+1,racers[r].name.c_str(),
                    racers[r].collisionCount);

        setcolor(racers[r].color);
        outtextxy(280,250+i*50,result);
    }

    setcolor(WHITE);
    outtextxy(330,430,(char*)"Press R to race again");
    outtextxy(330,470,(char*)"Press M to return to menu");
    outtextxy(330,510,(char*)"Press ESC to quit");
}

void resetRace() {
    int i;
    for (i = 0; i < (int)racers.size(); i++)
        racers[i].reset();

    createObstacles();
    createCoins();

    raceTime = 0;
    raceStarted = false;
    winnerIndex = -1;
    coinCount = 0;
    userPosition = START_POSITION;

    double sx,sy,tx,ty;
    getRoadPosition(START_POSITION,sx,sy,tx,ty);

    cameraX = sx - 250;
    cameraY = sy - 350;
}

void setupRacers() {
    racers.clear();

    racers.push_back(Racer("YOU",RED,0,true,AI_SPEED,1.0,0.5));
    racers.push_back(Racer("BLUE",BLUE,-1,false,215,0.55,0.25));
    racers.push_back(Racer("GREEN",GREEN,1,false,215,0.75,0.25));
}

void startLevel(int level) {
    currentLevel = level;

    createRoad();

    finishPosition = roadTotalLength - 80;

    resetRace();

    menuActive = false;
}

int main() {
    srand((unsigned int)time(NULL));

    int gd = DETECT;
    int gm = 0;

    initgraph(&gd,&gm,(char*)"");

    setbkcolor(GREEN);
    cleardevice();

    setupRacers();
    createRoad();
    finishPosition = roadTotalLength - 80;
    resetRace();

    menuActive = true;

    bool running = true;
    long lastTime = clock();

    while (running) {
        long now = clock();
        double dt = (double)(now-lastTime) / CLOCKS_PER_SEC;
        lastTime = now;

        if (dt > 0.05) dt = 0.05;
        if (dt < 0) dt = 0;

        if (kbhit()) {
            int key = getch();

            if (key == 27) {
                running = false;
                continue;
            }

            if (menuActive) {
                if (key == '1') {
                    startLevel(1);
                } else if (key == '2') {
                    startLevel(2);
                } else if (key == '3') {
                    startLevel(3);
                }
            } else {
                if ((key == 'r' || key == 'R') && winnerIndex >= 0) {
                    resetRace();
                } else if (key == 'm' || key == 'M') {
                    menuActive = true;
                    winnerIndex = -1;
                    raceStarted = false;
                }
            }
        }

        if (menuActive) {
            drawMenu();
            delay(16);
            continue;
        }

        bool rightPressed = false;
        bool leftPressed = false;

        while (kbhit()) {
            int key = getch();

            if (key == 27) {
                running = false;
                break;
            }

            if (key == 77) rightPressed = true;
            if (key == 75) leftPressed = true;
        }

        if (!running) break;

        if (winnerIndex < 0) {
            if (rightPressed || leftPressed)
                raceStarted = true;

            if (raceStarted)
                raceTime += dt;

            Racer &player = racers[0];

            if (player.stunTimer > 0) {
                player.stunTimer -= dt;
            } else {
                if (rightPressed)
                    player.speed = PLAYER_SPEED;
                else if (leftPressed)
                    player.speed = -MAX_REVERSE;
                else
                    player.speed = 0;

                player.position += player.speed * dt;

                if (player.position < START_POSITION)
                    player.position = START_POSITION;

                if (player.position > finishPosition)
                    player.position = finishPosition;

                updateCheckpoint(player);
                handleCollision(player);
                collectCoins(player);
            }

            userPosition = player.position;

            updateAI(racers[1],dt);
            updateAI(racers[2],dt);

            int i;
            for (i = 0; i < (int)racers.size(); i++) {
                if (!racers[i].finished && racers[i].position >= finishPosition) {
                    racers[i].finished = true;
                    racers[i].finishTime = raceTime;
                    racers[i].hasFinishTime = true;

                    if (winnerIndex < 0)
                        winnerIndex = i;
                }
            }

            double px,py,ptx,pty;
            getRoadPosition(player.position,px,py,ptx,pty);

            double targetCameraX = px - 250;
            double targetCameraY = py - 350;

            cameraX += (targetCameraX-cameraX) * 7.0 * dt;
            cameraY += (targetCameraY-cameraY) * 7.0 * dt;
        }

        cleardevice();

        drawRoad();

        drawRaceMarker(START_POSITION,"START",GREEN);
        drawRaceMarker(finishPosition,"FINISH",YELLOW);

        int i;

        for (i = 0; i < (int)obstacles.size(); i++) {
            if (winnerIndex < 0)
                obstacles[i].update(dt);

            if (fabs(obstacles[i].position-userPosition) < 1500)
                drawObstacle(obstacles[i]);
        }

        for (i = 0; i < (int)coins.size(); i++)
            drawCoin(coins[i]);

        for (i = 1; i < (int)racers.size(); i++)
            drawRacer(racers[i].position,racers[i].lane,racers[i].color,false);

        drawRacer(racers[0].position,racers[0].lane,racers[0].color,true);

        drawHUD();

        if (winnerIndex >= 0)
            drawFinishResults();

        drawFrame();

        delay(16);
    }

    closegraph();
    return 0;
}
