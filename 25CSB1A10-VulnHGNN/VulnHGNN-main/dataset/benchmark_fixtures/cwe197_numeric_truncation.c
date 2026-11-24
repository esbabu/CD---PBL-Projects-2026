#include <stdio.h>
#include <stdlib.h>

void allocate_buffer(long long big_size) {
    /* Vulnerability: truncation from 64-bit to 16-bit short */
    short truncated = (short)big_size;
    char *buf = (char *)malloc(truncated);
    if (buf) free(buf);
}

int main(void) {
    allocate_buffer(65536 + 10);
    return 0;
}
