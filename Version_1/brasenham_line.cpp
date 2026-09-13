// Sarang Wasamwar - 124B1B090
#include<iostream>
#include<graphics.h>
#include<cmath>
using namespace std ;

int main() {
	int x1 = 50, x2 = 250;
    	int y1 = 60, y2 = 260;
    	int dx = x2 - x1 ;
    	int dy = y2 - y1 ;
    	int p = 2*dy - dx ;
	
	int gd = DETECT, gm ;
	initgraph(&gd, &gm, (char*)"");
	
	/*int x_end ;
	if (x1 > x2 ) x_end = x2 ;
	else x_end = x1 ;
	*/
	
	int x = x1 ; int y = y1 ;
	
	while (x < x2) {
		x++ ;
		if (p < 0) {
			p = p + 2*dy ;
		} else {
			y++ ;
			p = p + 2*dy - 2*dx ;
		}
		putpixel(x, y, RED) ;
	}
	bgi_getch() ;
	closegraph() ;
	return 0 ;
}

