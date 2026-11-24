#include <stdio.h>
#include <string.h>

void safe_strncpy_usage(const char *src) {
    char dest[16];
    /* Safe: strncpy with explicit null termination */
    strncpy(dest, src, sizeof(dest) - 1);
    dest[sizeof(dest) - 1] = '\0';
    printf("Dest: %s\n", dest);
}

int main(void) {
    safe_strncpy_usage("SampleString");
    return 0;
}
