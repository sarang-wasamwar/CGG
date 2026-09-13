#include<iostream>
#include<graphics.h>

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

void midpoint(int xc, int yc, int r) {
	int p = 5/4 - r ;
	int x = 0 ; int y = r ;
	
	int xk2, yk2 ;
	while ( x <= y) {
		xk2 = 2*x + 2 ;
		yk2 = 2*y - 2 ;
		x++ ;
		if ( p < 0 ) {
			p = p + xk2 + 1 ;
		} else {
			y-- ;
			p = p + xk2 + 1 - yk2 ;
		}
		drawcircle(xc, yc, x, y) ;
	}
	
}

int main() {
	int gd = DETECT ; int gm ;
	initgraph(&gd,&gm, (char*)"") ;
	
	int xc = 300 ; int yc = 300 ;
	midpoint(xc, yc, 100) ;
	delay(30) ;
	closegraph() ;

}
