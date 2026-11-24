#include <stdio.h>
#include <string.h>

void build_path(const char *dir, const char *file) {
    char path[32];
    /* Vulnerability: unchecked strcat overflows stack buffer */
    strcpy(path, dir);
    strcat(path, "/");
    strcat(path, file);
    printf("Path: %s\n", path);
}

int main(void) {
    build_path("/very/long/nested/directory/path/here", "filename.txt");
    return 0;
}
