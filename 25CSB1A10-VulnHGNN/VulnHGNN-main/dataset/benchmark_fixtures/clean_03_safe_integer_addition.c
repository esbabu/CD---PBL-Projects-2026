#include <stdio.h>
#include <limits.h>

int safe_add(int a, int b) {
    /* Safe: checked before adding */
    if (b > 0 && a > INT_MAX - b) return -1;
    if (b < 0 && a < INT_MIN - b) return -1;
    return a + b;
}

int main(void) {
    int sum = safe_add(10, 20);
    printf("Sum: %d\n", sum);
    return 0;
}
