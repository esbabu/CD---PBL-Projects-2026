#include <stdio.h>
#include <stdlib.h>

void process_and_clean(char *ptr, int err_code) {
    free(ptr);
    if (err_code != 0) {
        /* Vulnerability: second free in error branch */
        free(ptr);
    }
}

int main(void) {
    char *p = (char *)malloc(32);
    if (p) process_and_clean(p, 1);
    return 0;
}
