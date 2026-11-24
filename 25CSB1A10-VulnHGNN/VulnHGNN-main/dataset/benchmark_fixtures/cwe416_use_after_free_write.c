#include <stdio.h>
#include <stdlib.h>

void process_data(char *ptr) {
    free(ptr);
    /* Vulnerability: writing to memory after it was deallocated */
    ptr[0] = 'X';
}

int main(void) {
    char *buf = (char *)malloc(32);
    if (buf) {
        process_data(buf);
    }
    return 0;
}
