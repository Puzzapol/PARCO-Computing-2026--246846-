#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <iomanip>
#include <omp.h>
#include <algorithm>
#include <string>
using namespace std;

struct tripla { int r, c; double v; };

int main() {
    const char* M = getenv("MATRIX");
    if (!M) return 1;

    string path = string("matrix/") + M;
    FILE* f = fopen(path.c_str(), "r");
    if (!f) return 1;

    char line[256];
    do { if (!fgets(line, sizeof(line), f)) return 1; } while (line[0] == '%');

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

    srand(123);

    for (int i = 0; i < nc; i++)
        x[i] = ((double) rand() / RAND_MAX) * 2000.0 - 1000.0;

    #pragma omp parallel for schedule(runtime)
    for (int i = 0; i < nr; i++) {
        double sum = 0.0;
        for (int k = pref[i]; k < pref[i + 1]; k++)
            sum += A[k].v * x[A[k].c];
        y[i] = sum;
    }

    long long FLOPS = 2LL * nz;
    long long BYTES = nz * 20LL + nr * 8LL;
    double AI = (double) FLOPS / (double) BYTES;

    for (int run = 0; run < 12; run++) {

        double t1 = omp_get_wtime();

        #pragma omp parallel for schedule(runtime)
        for (int i = 0; i < nr; i++) {
            double sum = 0.0;
            for (int k = pref[i]; k < pref[i + 1]; k++)
                sum += A[k].v * x[A[k].c];
            y[i] = sum;
        }

        double t2 = omp_get_wtime();
        double sec = t2 - t1;
        double ms = sec * 1000.0;

        double gflops = (double) FLOPS / sec / 1e9;
        double bw_gbs = (double) BYTES / sec / 1e9;

        cout << fixed << setprecision(7)
             << ms << "," << gflops << "," << bw_gbs << "," << AI << endl;
    }

    free(A);
    free(pref);
    free(x);
    free(y);
    return 0;
}

