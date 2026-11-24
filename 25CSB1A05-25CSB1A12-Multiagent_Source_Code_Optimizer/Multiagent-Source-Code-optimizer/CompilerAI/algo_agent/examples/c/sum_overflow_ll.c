/* Candidate using long long accumulator: avoids UB and matches on all UB-free inputs. */
int sum_overflow(const int *arr, int n) {
    long long total = 0;
    for (int i = 0; i < n; i++) {
        total += (long long)arr[i];
    }
    return (int)total;
}
