#include<iostream>
#include<graphics.h>

// g++ fileName.cpp -o r -lSDL_bgi -lSDL2

using namespace std ;

// Something extra that we should know with the logic & algorithm: {
// Global offsets for the centered origin
int OriginX = 0;
int OriginY = 0;

// INDEPENDENT FUNCTION: Call this once right after initgraph()
void setOriginToCenter() {
    OriginX = getmaxx() / 2;
    OriginY = getmaxy() / 2;
}

// Custom independent wrapper to plot relative to the center origin
void putpixelCenter(int x, int y, int color) {
    // Standard Cartesian mapping: Add to X, Subtract from Y
    putpixel(OriginX + x, OriginY - y, color);
}

// Draws the point symmetrically in all 4 quadrants of your centered origin
void drawFullCirclePoints(int x, int y, int color) {
    putpixelCenter(x, y, color);
    putpixelCenter(-x, y, color);
    putpixelCenter(-x, -y, color);
    putpixelCenter(x, -y, color);
}

// }
// Logic Wasn't wrong we were just missing some extra things like : setOriginToCenter, putPixelCenter, DrawFullCirclePoints


int main() {
	int x ; int y ; x = 0 ; y = 100 ;
	int g_delta = 2*(1-y) ; int s_delta ;
	int limit = 0 ;
	int gd = DETECT, gm ;
	
	initgraph(&gd, &gm, (char*)"");
	setOriginToCenter() ;
	
	drawFullCirclePoints(x,y,MAGENTA) ;
	while ( y > limit ) {
		if ( y <= limit ) {
			cout << "Y is less than Limit" << endl ;
			return 0 ;
		}
		if ( g_delta < 0 ) {
			s_delta = 2*g_delta + 2*y - 1 ;
			if ( s_delta <= 0 ) {
				x++ ;
				g_delta += 2*x + 1 ;
			} else {
				x++ ; y-- ;
				g_delta += 2*x - 2*y + 2 ;
			}
		} else if ( g_delta > 0 ) {
			s_delta = 2*g_delta - 2*x - 1 ;
			if ( s_delta <= 0 ) {
				x++ ; y-- ;
				g_delta += 2*x - 2*y + 2 ;
			} else {
				y-- ;
				g_delta += 1 - 2*y ;
			}
		} else {
			x++ ; y-- ;
			g_delta += 2*x -2*y + 2 ;
		}
		drawFullCirclePoints(x,y,MAGENTA) ;
	}
	//getch() ;
	// Replace getch(); with this:
	//cout << "Press Enter in the terminal to exit..." << endl;
	//cin.get(); 
	delay(60); 
	closegraph() ;
	return 0 ;

}
