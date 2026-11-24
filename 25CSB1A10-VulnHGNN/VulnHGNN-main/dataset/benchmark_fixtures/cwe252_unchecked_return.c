#include <stdio.h>
#include <stdlib.h>

void read_file_data(const char *path) {
    FILE *f = fopen(path, "r");
    char buf[64];
    /* Vulnerability: fread return value unchecked; buf may be uninitialized */
    fread(buf, 1, sizeof(buf), f);
    if (f) fclose(f);
}

int main(void) {
    read_file_data("nonexistent.txt");
    return 0;
}
