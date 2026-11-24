/* Reads uninitialized local/heap memory when n == 0 -> affected cases marked unstable. */
#include <stdlib.h>

int uninit(const int *arr, int n) {
    int *tmp = (int *)malloc(sizeof(int));
    if (!tmp) return 0;
    if (n > 0) {
        *tmp = arr[0];
    }
    int res = *tmp; /* uninitialized read when n <= 0; MALLOC_PERTURB_ exposes it */
    free(tmp);
    return res;
}
