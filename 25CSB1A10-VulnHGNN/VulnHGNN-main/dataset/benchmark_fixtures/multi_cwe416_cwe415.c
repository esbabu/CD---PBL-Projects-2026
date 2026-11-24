#include <stdio.h>
#include <stdlib.h>

void cleanup_bad(char *ptr) {
    free(ptr);
    /* Flaw 1: Use after free */
    printf("Tag: %c\n", ptr[0]);
    /* Flaw 2: Double free */
    free(ptr);
}

int main(void) {
    char *buf = (char *)malloc(16);
    if (buf) {
        buf[0] = 'A';
        cleanup_bad(buf);
    }
    return 0;
}
