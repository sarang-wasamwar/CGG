#include <graphics.h>

int main()
{
    initwindow(800, 600, "Polygon");

    int points[] = {
        200, 150,
        400, 100,
        550, 250,
        450, 400,
        250, 350,
        200, 150
    };

    drawpoly(6, points);

    getch();
    closegraph();

    return 0;
}
