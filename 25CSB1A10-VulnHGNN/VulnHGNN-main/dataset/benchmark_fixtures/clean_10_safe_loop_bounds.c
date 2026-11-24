#include <stdio.h>

void safe_bounded_loop(void) {
    int buffer[8];
    /* Safe: strictly less than 8 */
    for (int i = 0; i < 8; i++) {
        buffer[i] = i * i;
    }
}

int main(void) {
    safe_bounded_loop();
    return 0;
}
