#include <stdio.h>

void init_buffer(void) {
    int buffer[8];
    /* Vulnerability: loop runs 0..8 which writes buffer[8] (out of bounds) */
    for (int i = 0; i <= 8; i++) {
        buffer[i] = 0;
    }
}

int main(void) {
    init_buffer();
    return 0;
}
