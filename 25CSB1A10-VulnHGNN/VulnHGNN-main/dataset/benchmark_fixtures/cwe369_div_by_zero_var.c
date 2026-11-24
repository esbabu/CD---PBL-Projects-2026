#include <stdio.h>

int calculate_average(int sum, int count) {
    /* Vulnerability: count can be zero without validation */
    return sum / count;
}

int main(void) {
    int avg = calculate_average(100, 0);
    printf("Avg: %d\n", avg);
    return 0;
}
