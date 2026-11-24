#include <stdio.h>

int safe_get(const int *arr, int len, int index) {
    /* Safe: boundary check */
    if (index < 0 || index >= len) return -1;
    return arr[index];
}

int main(void) {
    int nums[5] = {1, 2, 3, 4, 5};
    int val = safe_get(nums, 5, 2);
    printf("Val: %d\n", val);
    return 0;
}
