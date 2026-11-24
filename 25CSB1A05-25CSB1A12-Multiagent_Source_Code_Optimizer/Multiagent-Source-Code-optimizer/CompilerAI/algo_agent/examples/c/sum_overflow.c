/* Signed int accumulation: triggers signed overflow (UB) on large inputs. */
int sum_overflow(const int *arr, int n) {
    int total = 0;
    for (int i = 0; i < n; i++) {
        total += arr[i];
    }
    return total;
}
