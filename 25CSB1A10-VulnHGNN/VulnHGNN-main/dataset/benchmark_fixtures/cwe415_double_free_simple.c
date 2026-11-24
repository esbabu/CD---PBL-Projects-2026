#include <stdio.h>
#include <stdlib.h>

void cleanup_resource(char *res) {
    free(res);
    /* Vulnerability: double free on the same pointer */
    free(res);
}

int main(void) {
    char *p = (char *)malloc(64);
    if (p) cleanup_resource(p);
    return 0;
}
