// sarang wasamwar 124b1b090

#include<iostream>
#include<graphics.h>
#include<cmath>

using namespace std ;

void drawcircle(int xc, int yc, int x, int y) {
	putpixel(xc +x, yc +y, RED) ;
	putpixel(xc -x, yc +y, RED) ;
	putpixel(xc +x, yc -y, RED) ;
	putpixel(xc -x, yc -y, RED) ;
	putpixel(xc +y, yc +x, RED) ;
	putpixel(xc -y, yc +x, RED) ;
	putpixel(xc +y, yc -x, RED) ;
	putpixel(xc -y, yc -x, RED) ;
}

void dda(int xc, int yc, int r) {
	double x = 0;
	double y = r;
	int val = 0;
	while (pow(2, val) < r) {
		val++;
	}
	double eps = 1.0 / pow(2, val);
	while (x <= y) {
		drawcircle(xc, yc, (int)(x + 0.5), (int)(y + 0.5));
		x = x + (eps * y);
		y = y - (eps * x);
	}	
}

int main() {
	int gd = DETECT ; int gm ;
	initgraph(&gd,&gm, (char*)"");
	
	int xc = 300 , yc = 300 ;
	dda(xc, yc, 10) ;
	
	delay(30);
	closegraph() ;
	return 0 ;
}

/*

// True DDA Circle Algorithm utilizing 8-way symmetry
void dda(int xc, int yc, int r) {
    // 1. Initialize starting coordinates
    double x = 0;
    double y = r;
    
    // 2. Find epsilon (eps = 2^-n) where 2^n is just greater than r
    int val = 0;
    while (pow(2, val) < r) {
        val++;
    }
    double eps = 1.0 / pow(2, val);
    
    // 3. Loop only until x equals y (first 45 degrees / octant)
    while (x <= y) {
        // Plot all 8 symmetric points simultaneously
        drawcircle(xc, yc, (int)(x + 0.5), (int)(y + 0.5)); // +0.5 helps with clean rounding
        
        // DDA differential step calculations
        x = x + (eps * y);
        y = y - (eps * x);
    }
}

*/
