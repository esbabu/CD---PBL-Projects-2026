#include <stdio.h>
#include <stdlib.h>

void safe_array_ops(void) {
    int *arr = (int *)malloc(10 * sizeof(int));
    if (!arr) return;
    for (int i = 0; i < 10; i++) {
        arr[i] = i;
    }
    free(arr);
}

int main(void) {
    safe_array_ops();
    return 0;
}
