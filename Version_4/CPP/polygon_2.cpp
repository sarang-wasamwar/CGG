#include <graphics.h>

void floodFill(int x, int y, int fillColor, int boundaryColor)
{
    int currentColor = getpixel(x, y);

    if (currentColor != boundaryColor && currentColor != fillColor)
    {
        putpixel(x, y, fillColor);

        floodFill(x + 1, y, fillColor, boundaryColor);
        floodFill(x - 1, y, fillColor, boundaryColor);
        floodFill(x, y + 1, fillColor, boundaryColor);
        floodFill(x, y - 1, fillColor, boundaryColor);
    }
}

int main()
{
    initwindow(800, 600, "Flood Fill");

    setcolor(WHITE);

    int polygon[] = {
        200, 150,
        500, 150,
        500, 350,
        200, 350,
        200, 150
    };

    drawpoly(5, polygon);

    floodFill(350, 250, RED, WHITE);

    getch();
    closegraph();

    return 0;
}