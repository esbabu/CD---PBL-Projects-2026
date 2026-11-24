#include <stdio.h>

int main(void) {
    int n = 0, sum = 0, x = 0;
    if (scanf("%d", &n) == 1) {
        for (int i = 0; i < n; i++) {
            if (scanf("%d", &x) == 1) sum += x;
        }
    }
    printf("%d\n", sum);
    return 0;
}
