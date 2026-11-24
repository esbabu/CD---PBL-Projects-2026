#include <stdio.h>
#include <string.h>

void safe_like_copy(int len, const char *src) {
    char dest[64];
    /* Vulnerability: negative len converted to huge unsigned size_t in strncpy */
    strncpy(dest, src, len);
    dest[63] = '\0';
    printf("Dest: %s\n", dest);
}

int main(void) {
    safe_like_copy(-5, "Hello");
    return 0;
}
