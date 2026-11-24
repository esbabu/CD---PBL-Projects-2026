/* O(n^2) two_sum returning 1 and writing lexicographically first (i, j) to out[0..1], else 0. */
int two_sum(const int *nums, int n, int target, int *out) {
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            if ((long long)nums[i] + (long long)nums[j] == (long long)target) {
                out[0] = i;
                out[1] = j;
                return 1;
            }
        }
    }
    out[0] = -1;
    out[1] = -1;
    return 0;
}
