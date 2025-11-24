#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <iomanip>
#include <algorithm>
#include <string>
#include <chrono>
using namespace std;

struct tripla {
    int r, c;
    double v;
};

int main() {
    const char* MATRIX = getenv("MATRIX");
    if (!MATRIX) return 1;

    string path = string("matrix/") + MATRIX;
    FILE* f = fopen(path.c_str(), "r");
    if (!f) return 1;

    char line[256];
    do {
        if (!fgets(line, sizeof(line), f)) return 1;
    } while (line[0] == '%');

    int nr, nc, nz;
    sscanf(line, "%d %d %d", &nr, &nc, &nz);

    tripla* A = (tripla*) malloc(nz * sizeof(tripla));
    int a, b;
    for (int i = 0; i < nz; i++) {
        fgets(line, sizeof(line), f);
        sscanf(line, "%d %d %lf", &a, &b, &A[i].v);
        A[i].r = a - 1;
        A[i].c = b - 1;
    }
    fclose(f);

    sort(A, A + nz, [](const tripla& x, const tripla& y) {
        if (x.r == y.r) return x.c < y.c;
        return x.r < y.r;
    });

    int* pref = (int*) malloc((nr + 1) * sizeof(int));
    pref[0] = 0;
    int j = 0;
    for (int i = 0; i < nr; i++) {
        while (j < nz && A[j].r == i) j++;
        pref[i + 1] = j;
    }

    double* x = (double*) malloc(nc * sizeof(double));
    double* y = (double*) malloc(nr * sizeof(double));

    srand(time(NULL));
    for (int i = 0; i < nc; i++)
        x[i] = ((double)rand() / RAND_MAX) * 2000.0 - 1000.0;

    for (int warm = 0; warm < nr; warm++) {
        double sum = 0.0;
        for (int k = pref[warm]; k < pref[warm + 1]; k++)
            sum += A[k].v * x[A[k].c];
        y[warm] = sum;
    }

    long bytes_A = nz * (sizeof(int)*2 + sizeof(double));
    long bytes_x = nc * sizeof(double);
    long bytes_y = nr * sizeof(double);
    long total_bytes = bytes_A + bytes_x + bytes_y;
    long flops = 2L * nz;

    for (int run = 0; run < 12; run++) {

        auto t1 = chrono::high_resolution_clock::now();

        for (int i = 0; i < nr; i++) {
            double sum = 0.0;
            for (int k = pref[i]; k < pref[i + 1]; k++)
                sum += A[k].v * x[A[k].c];
            y[i] = sum;
        }

        auto t2 = chrono::high_resolution_clock::now();
        double ms = chrono::duration_cast<chrono::nanoseconds>(t2 - t1).count() / 1e6;

        double gflops = (double)flops / (ms * 1e6);
        double bw_gbs = (double)total_bytes / (ms * 1e6);
        double ai = (double)flops / total_bytes;

        cout << fixed << setprecision(7)
             << ms << ","
             << gflops << ","
             << bw_gbs << ","
             << ai
             << endl;
    }

    free(A);
    free(pref);
    free(x);
    free(y);
    return 0;
}

