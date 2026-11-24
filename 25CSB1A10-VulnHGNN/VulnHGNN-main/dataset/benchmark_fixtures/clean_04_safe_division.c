#include <stdio.h>

int safe_div(int num, int denom) {
    /* Safe: zero check before division */
    if (denom == 0) return 0;
    return num / denom;
}

int main(void) {
    int res = safe_div(100, 5);
    printf("Res: %d\n", res);
    return 0;
}
