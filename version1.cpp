#include<iostream>
#include<graphics.h>
#include<conio.h>

using namespace std;

//------------ Bresenham Line Drawing Algorithm ------------//
void bresenhamLine(int x1,int y1,int x2,int y2,int color)
{
    int dx = abs(x2-x1); int dy = abs(y2-y1);
    int sx = (x1<x2)?1:-1; int sy = (y1<y2)?1:-1;
    int err = dx-dy;
    while(true)
    {
        putpixel(x1,y1,color);
        if(x1==x2 && y1==y2)
            break;
        int e2 = 2*err;
        if(e2 > -dy)
        {
            err -= dy;
            x1 += sx;
        }
        if(e2 < dx)
        {
            err += dx;
            y1 += sy;
        }
    }
}

//------------ Draw Race Track ------------//
void drawTrack()
{
    // Outer White Border
    bresenhamLine(80,120,700,120,WHITE);
    bresenhamLine(80,380,700,380,WHITE);
    // Left curved border
    bresenhamLine(80,120,40,180,WHITE);
    bresenhamLine(40,180,40,320,WHITE);
    bresenhamLine(40,320,80,380,WHITE);
    // Right curved border
    bresenhamLine(700,120,740,180,WHITE);
    bresenhamLine(740,180,740,320,WHITE);
    bresenhamLine(740,320,700,380,WHITE);
    // Three Grey Running Lines
    bresenhamLine(80,190,700,190,LIGHTGRAY);
    bresenhamLine(80,250,700,250,LIGHTGRAY);
    bresenhamLine(80,310,700,310,LIGHTGRAY);
    // Finish Line
    bresenhamLine(700,120,700,380,YELLOW);
}

//------------ Draw Player Dot ------------//
void drawRunner(int x,int y,int color)
{
    setcolor(color);
    setfillstyle(SOLID_FILL,color);
    fillellipse(x,y,8,8);
}

//------------ Main Function ------------//
int main()
{
    int gd = DETECT; int gm;
    initgraph(&gd,&gm,(char*)"");
    // Starting positions
    int playerX = 100;
    int blueX = 100;
    int greenX = 100;
    // Fixed running lines
    int redY = 190;
    int blueY = 250;
    int greenY = 310;
    bool gameOver = false;
    while(!gameOver)
    {
        cleardevice();
        drawTrack();
        // Draw runners on their paths
        drawRunner(playerX,redY,RED);
        drawRunner(blueX,blueY,BLUE);
        drawRunner(greenX,greenY,GREEN);
        // AI speed
        blueX += 3;
        greenX += 5;
        // Player Controls
        if(kbhit())
        {
            int key = getch();
            if(key==0 || key==224)
            {
                key = getch();
                switch(key)
                {
                    case 77:        // Right Arrow Forward
                        playerX += 10;
                        break;
                    case 75:        // Left Arrow Backward
                        playerX -= 10;
                        break;
                }
            }
            if(key==27)
                break;
        }
        // Keep player on track
        if(playerX < 80)
            playerX = 80;
        if(playerX > 700)
            playerX = 700;
        // Winner checking
        if(playerX >= 700)
        {
            cleardevice();
            settextstyle(DEFAULT_FONT,0,2);
            outtextxy(250,250,"RED PLAYER WINS!");
            delay(3000);
            gameOver = true;
        }
        else if(blueX >= 700)
        {
            cleardevice();
            settextstyle(DEFAULT_FONT,0,2);
            outtextxy(250,250,"BLUE PLAYER WINS!");
            delay(3000);
            gameOver = true;
        }
        else if(greenX >= 700)
        {
            cleardevice();
            settextstyle(DEFAULT_FONT,0,2);
            outtextxy(250,250,"GREEN PLAYER WINS!");
            delay(3000);
            gameOver = true;
        }
        delay(30);
    }
    closegraph();
    return 0;
}