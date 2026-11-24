#include <stdio.h>
#include <stdlib.h>

void populate_heap(int count) {
    int *data = (int *)malloc(5 * sizeof(int));
    if (!data) return;
    /* Vulnerability: writing beyond allocated 5 elements */
    for (int i = 0; i < count; i++) {
        data[i] = i * 2;
    }
    free(data);
}

int main(void) {
    populate_heap(10);
    return 0;
}
