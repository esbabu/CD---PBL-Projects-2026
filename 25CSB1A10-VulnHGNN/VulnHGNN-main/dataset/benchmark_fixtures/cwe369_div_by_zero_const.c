#include <stdio.h>

int compute_ratio(int num) {
    /* Vulnerability: constant division by zero */
    int ratio = num / 0;
    return ratio;
}

int main(void) {
    int r = compute_ratio(42);
    printf("Ratio: %d\n", r);
    return 0;
}
