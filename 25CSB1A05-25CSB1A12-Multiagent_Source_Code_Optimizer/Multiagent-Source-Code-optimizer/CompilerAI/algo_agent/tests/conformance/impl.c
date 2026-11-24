#include <math.h>
#include <stdio.h>
#include <stdlib.h>

int add(int a, int b) {
    return a + b;
}

int mutates_argument(int* arr, int n) {
    if (n > 0) arr[0] = 99;
    return n;
}

int prints_text(const char* s) {
    printf("%s\n", s);
    return 0;
}

int infinite_loop(int x) {
    volatile int y = x;
    while (1) { y++; }
    return y;
}

int crashes_hard(int x) {
    (void)x;
    abort();
    return 0;
}

double returns_special_values(int x) {
    (void)x;
    return NAN;
}
