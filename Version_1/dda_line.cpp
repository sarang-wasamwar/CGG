// Sarang Wasamwar - 124B1B090
#include<iostream>
#include<graphics.h>
#include<cmath>
using namespace std ;

int main() {
	float x1 = 50, x2 = 250;
    	float y1 = 60, y2 = 260;
    	float dx = x2 - x1 ;
    	float dy = y2 - y1 ;
	int length = (abs(dx) >= abs(dy)) ? abs(dx) : abs(dy) ;
	float x_inc = (x2-x1)/length;
	float y_inc = (y2-y1)/length;
	
	int gd = DETECT, gm ;
	initgraph(&gd, &gm, (char*)"");
	
	int i = 0 ;
	
	while (i<length) {
		putpixel(x1, y1, YELLOW) ;
		x1 = x1 + x_inc ;
		y1 = y1 + y_inc ;
		if (x1 == x2 && y1 == y2 ) break ;
		i++ ;
		//getch() ;
	}
	bgi_getch() ;
	closegraph() ;
	return 0 ;
}

