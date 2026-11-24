#include <stdio.h>
#include <stdlib.h>

void write_array(int count) {
    /* Flaw 1: Integer overflow on multiplication */
    int alloc_size = count * sizeof(int);
    int *arr = (int *)malloc(alloc_size);
    if (!arr) return;

    /* Flaw 2: Out of bounds write */
    for (int i = 0; i < count + 5; i++) {
        arr[i] = i;
    }
    free(arr);
}

int main(void) {
    write_array(100);
    return 0;
}
