#include <stdio.h>
#include <stdlib.h>

int parse_config(int flag) {
    char *buffer = (char *)malloc(1024);
    if (!buffer) return -1;
    if (flag < 0) {
        /* Vulnerability: early return leaks allocated buffer */
        return -2;
    }
    free(buffer);
    return 0;
}

int main(void) {
    parse_config(-1);
    return 0;
}
