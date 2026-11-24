#include <stdio.h>
#include <stdlib.h>

void write_header(size_t len) {
    char *buf = (char *)malloc(len);
    /* Vulnerability: dereferencing buf without checking for NULL */
    buf[0] = 'H';
    buf[1] = 'I';
    free(buf);
}

int main(void) {
    write_header(100);
    return 0;
}
