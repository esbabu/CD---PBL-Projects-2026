#include <stdio.h>
#include <stdlib.h>

void safe_single_free(void) {
    char *res = (char *)malloc(32);
    if (!res) return;
    free(res);
    res = NULL; /* Safe: pointer cleared to prevent UAF / double free */
}

int main(void) {
    safe_single_free();
    return 0;
}
