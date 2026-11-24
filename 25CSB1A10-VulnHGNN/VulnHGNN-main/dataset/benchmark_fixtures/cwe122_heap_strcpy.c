#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void store_message(const char *msg) {
    char *dest = (char *)malloc(16);
    if (!dest) return;
    /* Vulnerability: strcpy into fixed 16-byte heap buffer */
    strcpy(dest, msg);
    printf("Msg: %s\n", dest);
    free(dest);
}

int main(void) {
    store_message("Heap buffer overflow payload exceeding 16 bytes");
    return 0;
}
