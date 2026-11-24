#include <stdio.h>
#include <stdlib.h>

void safe_alloc(size_t len) {
    if (len == 0 || len > 1024) return;
    char *buf = (char *)malloc(len);
    /* Safe: checked against NULL */
    if (!buf) return;
    buf[0] = 'A';
    free(buf);
}

int main(void) {
    safe_alloc(64);
    return 0;
}
