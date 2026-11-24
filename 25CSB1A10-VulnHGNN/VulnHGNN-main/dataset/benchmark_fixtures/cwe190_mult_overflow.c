#include <stdio.h>
#include <stdlib.h>

void *allocate_matrix(int rows, int cols) {
    /* Vulnerability: rows * cols can overflow leading to small allocation */
    int size = rows * cols * sizeof(int);
    return malloc(size);
}

int main(void) {
    void *p = allocate_matrix(100000, 100000);
    free(p);
    return 0;
}
