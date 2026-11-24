#include <stdio.h>
#include <limits.h>

int compute_total(int base, int bonus) {
    /* Vulnerability: signed integer overflow without range check */
    int total = base + bonus;
    return total;
}

int main(void) {
    int result = compute_total(INT_MAX, 100);
    printf("Total: %d\n", result);
    return 0;
}
