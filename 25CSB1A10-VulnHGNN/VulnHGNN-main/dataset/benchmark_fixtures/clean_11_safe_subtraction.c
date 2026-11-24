#include <stdio.h>
#include <limits.h>

int safe_sub(int a, int b) {
    /* Safe: underflow check */
    if (b > 0 && a < INT_MIN + b) return -1;
    if (b < 0 && a > INT_MAX + b) return -1;
    return a - b;
}

int main(void) {
    int diff = safe_sub(100, 40);
    printf("Diff: %d\n", diff);
    return 0;
}
