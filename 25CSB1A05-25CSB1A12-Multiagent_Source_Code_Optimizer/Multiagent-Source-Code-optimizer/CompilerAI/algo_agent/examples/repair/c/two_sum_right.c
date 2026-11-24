#include <stddef.h>

int two_sum_count(const int* arr, int n, int target) {
    int count = 0;
    for (int i = 0; i < n; i++) {
        int need = target - arr[i];
        for (int j = i + 1; j < n; j++) {
            if (arr[j] == need) {
                count++;
            }
        }
    }
    return count;
}
