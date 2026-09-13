#include <iostream>
#include <cmath>
#include <iomanip>
#include <graphics.h>

using namespace std;

#define PI 3.1416

void displayPoints(double points[][3], int n) {
    cout << "\nTransformed points: \n";
    cout << "X\t\tY\n";

    for (int i = 0; i < n; i++) {
        cout << fixed << setprecision(2)
             << points[i][0] << "\t\t"
             << points[i][1] << endl;
    }
}

void multiply(double points[][3], int n, double T[3][3]) {
    double result[n][3];

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < 3; j++) {
            result[i][j] = 0;
            for (int k = 0; k < 3; k++) {
                result[i][j] += points[i][k] * T[k][j];
            }
        }
    }

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < 3; j++) {
            points[i][j] = result[i][j];
        }
    }
}

void translate(double points[][3], int n) {
    double tx, ty;
    cout << "Enter translation factors(tx and ty): ";
    cin >> tx >> ty;

    double T[3][3] = {
        {1,  0,  0},
        {0,  1,  0},
        {tx, ty, 1}
    };

    multiply(points, n, T);
    displayPoints(points, n);
}

void scale(double points[][3], int n) {
    double sx, sy;
    cout << "Enter scaling factors(sx and sy): ";
    cin >> sx >> sy;

    double S[3][3] = {
        {sx, 0,  0},
        {0,  sy, 0},
        {0,  0,  1}
    };

    multiply(points, n, S);
    displayPoints(points, n);
}

void rotate(double points[][3], int n) {
    double theta;
    int choice;

    cout << "Enter rotation angle(degrees): ";
    cin >> theta;

    cout << "1.Counterclockwise\n";
    cout << "2.Clockwise\n";
    cout << "Enter choice: ";
    cin >> choice;

    double rad = theta * PI / 180.0;
    if (choice == 2) rad = -rad;

    double R[3][3] = {
        {cos(rad),  -sin(rad), 0},
        {sin(rad),  cos(rad),  0},
        {0,          0,         1}
    };

    multiply(points, n, R);
    displayPoints(points, n);
}

void DDA(int x1, int y1, int x2, int y2, int color) {
    float dx = x2 - x1;
    float dy = y2 - y1;

    int steps = max(abs(dx), abs(dy));

    float Xinc = dx / (steps ? steps : 1); 
    float Yinc = dy / (steps ? steps : 1);

    float x = x1;
    float y = y1;

    for (int i = 0; i <= steps; i++) {
        putpixel(round(x), round(y), color);
        x += Xinc;
        y += Yinc;
    }
}

void composite(double points[][3], int n) {
    string sequence;

    cout << "\nEnter composite transformation sequence: ";
    cout << "\nT = Translation";
    cout << "\nR = Rotation";
    cout << "\nS = Scaling";
    cout << "\nEnter Sequence: ";
    cin >> sequence;

    for (size_t i = 0; i < sequence.length(); i++) {
        char ch = toupper(sequence[i]);
        if (ch == 'T') {
            double tx, ty;
            cout << "Enter translation factors(tx and ty): ";
            cin >> tx >> ty;

            double T[3][3] = {
                {1,  0,  0},
                {0,  1,  0},
                {tx, ty, 1}
            };
            multiply(points, n, T);
        } 
        else if (ch == 'R') {
            double theta;
            int choice;

            cout << "Enter rotation angle(degrees): ";
            cin >> theta;

            cout << "1.Counterclockwise\n";
            cout << "2.Clockwise\n";
            cout << "Enter choice: ";
            cin >> choice;

            double rad = theta * PI / 180.0;
            if (choice == 2) rad = -rad;

            double R[3][3] = {
                {cos(rad),  -sin(rad), 0},
                {sin(rad),  cos(rad),  0},
                {0,          0,         1}
            };
            multiply(points, n, R);
        } 
        else if (ch == 'S') {
            double sx, sy;
            cout << "Enter scaling factors(sx and sy): ";
            cin >> sx >> sy;

            double S[3][3] = {
                {sx, 0,  0},
                {0,  sy, 0},
                {0,  0,  1}
            };
            multiply(points, n, S);
        } 
        else {
            cout << "\nInvalid Transformation '" << sequence[i] << "'";
            return;
        }
    }

    cout << "\nFinal Result after composite transformations: ";
    displayPoints(points, n);
}

int main() {
    int gd = DETECT, gm;
    initgraph(&gd, &gm, (char*)"");

    int n;
    cout << "Enter no. of points: ";
    cin >> n;

    double points[n][3];
    cout << "Enter points (X and Y):\n";
    for (int i = 0; i < n; i++) {
        cin >> points[i][0] >> points[i][1];
        points[i][2] = 1;
    }

    int ch;
    do {
        cout << "\n1. Translation\n";
        cout << "2. Scaling\n";
        cout << "3. Rotation\n";
        cout << "4. Composite Transformation\n";
        cout << "5. Exit\n";
        cout << "Enter Choice: ";
        cin >> ch;

        double temp[n][3];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < 3; j++) {
                temp[i][j] = points[i][j];
            }
        }

        switch (ch) {
            case 1:
                translate(temp, n);
                break;
            case 2:
                scale(temp, n);
                break;
            case 3:
                rotate(temp, n);
                break;
            case 4:
                composite(temp, n);
                break;
            case 5:
                cout << "\nExiting\n";
                break;
            default:
                cout << "\nInvalid choice\n";
        }
    } while (ch != 5);

    //getch();
    delay(50);
    closegraph();
    return 0;
}

