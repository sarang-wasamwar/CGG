#include<iostream>
#include<graphics.h>
#include<math.h>
#include<cstdio>

using namespace std;

void multiply(double points[1][3], int n, double T[3][3]) {
    double result[1][3] = {{0,0,0}};

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < 3; j++) {
            result[i][j] = 0;
            for (int k = 0; k < 3 ; k++) {
                result[i][j] += points[i][k]*T[k][j];
            }
        }
    }

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < 3; j++ ) {
            points[i][j] = result[i][j] ;
        }
    }
}

void applyMatrixTranslation(double points[1][3], double tx, double ty) {
    double T[3][3] = {
        {1,  0,  0 },
        {0,  1,  0} ,
        {tx, ty, 1}
    } ;
    multiply(points, 1, T) ; 
}

void bresenhamLine(int x1,int y1,int x2,int y2,int color) {
    int dx = abs(x2-x1);
    int dy = abs(y2-y1);

    int sx = (x1 < x2) ? 1 : -1;
    int sy = (y1 < y2) ? 1 : -1;

    int err = dx - dy;

    while(true) {
        putpixel(x1,y1,color);
        if(x1==x2 && y1==y2)
            break;
        int e2 = 2 * err;
        if(e2 > -dy) {
            err -= dy;
            x1 += sx;
        }
        if(e2 < dx) {
            err += dx;
            y1 += sy;
        }
    }
}

void bresenhamCircle(int xc,int yc,int r,int color) {
    int x=0;
    int y=r;

    int d=3-2*r;

    while(y>=x) {
        putpixel(xc+x,yc+y,color);
        putpixel(xc-x,yc+y,color);
        putpixel(xc+x,yc-y,color);
        putpixel(xc-x,yc-y,color);
        putpixel(xc+y,yc+x,color);
        putpixel(xc-y,yc+x,color);
        putpixel(xc+y,yc-x,color);
        putpixel(xc-y,yc-x,color);

        if(d<0) {
            d=d+4*x+6;
        } else {
            d=d+4*(x-y)+10;
            y--;
        }
        x++;
    }
}

void drawTrack() {
    bresenhamLine(80,160,700,160,WHITE); // road border
    bresenhamLine(80,300,700,300,WHITE);
    bresenhamLine(80,160,80,300,WHITE); // side border
    bresenhamLine(700,160,700,300,WHITE);
    bresenhamLine(80,195,700,195,LIGHTGRAY); // Grey running path
    bresenhamLine(80,230,700,230,LIGHTGRAY);
    bresenhamLine(80,265,700,265,LIGHTGRAY);
    bresenhamLine(700,160,700,300,YELLOW); // Finish Line
}

void drawRunner(int x,int y,int color) {
   for(int r = 7; r >= 0; r--)  
      bresenhamCircle(x,y,r,color);
}

void drawCoin(int x,int y) {
    bresenhamCircle(x,y,8,YELLOW);
}

int main() {
    int gd=DETECT;
    int gm;
    initgraph(&gd,&gm,(char*)"");
    
    double playerPoint[1][3] = {{100.0, 195.0, 1.0}};
    double bluePlayer[1][3] = {{100.0, 230.0, 1.0}};
    double greenPlayer[1][3] = {{100.0, 265.0, 1.0}};
    double r_speed = 8.0;
    double b_speed = 5.0;
    double g_speed = 4.9; 
    int finishLine = 700;    
    int coinX[5] = {220,320,420,520,620};
    while (true) {
	cleardevice();
	drawTrack();    
	for(int i = 0; i < 5; i++) {
	    drawCoin(coinX[i], 195);
	    drawCoin(coinX[i], 230);
	    drawCoin(coinX[i], 265);
	}
	int redX  = (int)playerPoint[0][0];
        int blueX = (int)bluePlayer[0][0];
        int greenX = (int)greenPlayer[0][0];
	drawRunner(redX, 195, RED);
	drawRunner(blueX, 230, BLUE);
	drawRunner(greenX, 265, GREEN);
	delay(10);
	if ( redX < finishLine )
		applyMatrixTranslation(playerPoint, r_speed, 0.0);
	if (blueX < finishLine)
		applyMatrixTranslation(bluePlayer, b_speed, 0.0);
	if (greenX < finishLine)
		applyMatrixTranslation(greenPlayer, g_speed, 0.0);
    }

    closegraph();

    return 0;
}
