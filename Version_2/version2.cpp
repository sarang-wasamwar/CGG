#include<iostream>
#include<graphics.h>
#include<conio.h>
#include<math.h>
#include<cstdio>

using namespace std;


//================ Bresenham Line Algorithm =================//

void bresenhamLine(int x1,int y1,int x2,int y2,int color)
{
    int dx = abs(x2-x1);
    int dy = abs(y2-y1);

    int sx = (x1 < x2) ? 1 : -1;
    int sy = (y1 < y2) ? 1 : -1;

    int err = dx - dy;


    while(true)
    {
        putpixel(x1,y1,color);


        if(x1==x2 && y1==y2)
            break;


        int e2 = 2 * err;


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



//================ Bresenham Circle Algorithm =================//

void bresenhamCircle(int xc,int yc,int r,int color)
{
    int x=0;
    int y=r;

    int d=3-2*r;


    while(y>=x)
    {

        putpixel(xc+x,yc+y,color);
        putpixel(xc-x,yc+y,color);

        putpixel(xc+x,yc-y,color);
        putpixel(xc-x,yc-y,color);


        putpixel(xc+y,yc+x,color);
        putpixel(xc-y,yc+x,color);

        putpixel(xc+y,yc-x,color);
        putpixel(xc-y,yc-x,color);



        if(d<0)
        {
            d=d+4*x+6;
        }

        else
        {
            d=d+4*(x-y)+10;
            y--;
        }

        x++;
    }
}



//================ Draw Race Track =================//

void drawTrack()
{

    // White Road Border

    bresenhamLine(80,160,700,160,WHITE);

    bresenhamLine(80,300,700,300,WHITE);


    // Side Borders

    bresenhamLine(80,160,80,300,WHITE);

    bresenhamLine(700,160,700,300,WHITE);



    // Three Grey Running Paths

    bresenhamLine(80,205,700,205,LIGHTGRAY);

    bresenhamLine(80,235,700,235,LIGHTGRAY);

    bresenhamLine(80,265,700,265,LIGHTGRAY);



    // Finish Line

    bresenhamLine(700,160,700,300,YELLOW);

}



//================ Draw Runner =================//

void drawRunner(int x,int y,int color)
{
    setcolor(color);

    setfillstyle(SOLID_FILL,color);

    fillellipse(x,y,7,7);
}



//================ Draw Coin =================//

void drawCoin(int x,int y)
{
    bresenhamCircle(x,y,8,YELLOW);
}



//================ Collision =================//

bool collision(int x1,int y1,int x2,int y2)
{
    int dist = sqrt(
        (x2-x1)*(x2-x1) +
        (y2-y1)*(y2-y1)
    );


    if(dist < 15)
        return true;


    return false;
}



//================ Main =================//

int main()
{

    int gd=DETECT;
    int gm;


    initgraph(&gd,&gm,(char*)"");



    // Player Position

    int playerX=100;
    int playerY=205;



    // AI Positions

    int blueX=100;
    int blueY=235;


    int greenX=100;
    int greenY=265;



    // Coins

    int coinX[6]={220,330,430,520,600,650};

    bool coinTaken[6]=
    {
        false,false,false,
        false,false,false
    };


    int score=0;


    bool gameOver=false;



    while(!gameOver)
    {

        cleardevice();



        drawTrack();



        // Draw Coins

        for(int i=0;i<6;i++)
        {
            if(!coinTaken[i])
            {
                drawCoin(coinX[i],playerY);
            }
        }



        // Draw Players

        drawRunner(playerX,playerY,RED);

        drawRunner(blueX,blueY,BLUE);

        drawRunner(greenX,greenY,GREEN);



        // AI Movement

        blueX += 3;

        greenX += 5;



        // Player Controls

        if(kbhit())
        {

            int key=getch();


            if(key==0 || key==224)
            {

                key=getch();


                switch(key)
                {

                    case 77:     // Right Arrow

                        playerX+=10;
                        break;


                    case 75:     // Left Arrow

                        playerX-=10;
                        break;

                }
            }



            if(key==27)
                break;

        }



        // Keep player on track

        if(playerX < 80)
            playerX=80;


        if(playerX > 700)
            playerX=700;



        // Coin Collection

        for(int i=0;i<6;i++)
        {

            if(!coinTaken[i])
            {

                if(collision(playerX,playerY,
                             coinX[i],playerY))
                {

                    coinTaken[i]=true;

                    score++;

                }

            }

        }




        // Winner Detection

        if(playerX>=700)
        {

            cleardevice();


            outtextxy(250,220,
            (char*)"RED PLAYER WINS!");


            char text[30];

            sprintf(text,"Coins Collected: %d",score);


            outtextxy(250,260,text);


            delay(3000);


            gameOver=true;

        }



        else if(blueX>=700)
        {

            cleardevice();


            outtextxy(250,220,
            (char*)"BLUE PLAYER WINS!");


            delay(3000);


            gameOver=true;

        }



        else if(greenX>=700)
        {

            cleardevice();


            outtextxy(250,220,
            (char*)"GREEN PLAYER WINS!");


            delay(3000);


            gameOver=true;

        }



        delay(30);

    }



    closegraph();


    return 0;
}