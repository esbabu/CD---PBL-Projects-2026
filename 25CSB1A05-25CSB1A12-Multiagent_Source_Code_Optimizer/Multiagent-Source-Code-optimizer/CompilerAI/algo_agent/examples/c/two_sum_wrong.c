/* WRONG two_sum: iterates outer j from 1..n-1 and inner i from j-1..0, breaking lexicographical (i, j) order. */
int two_sum(const int *nums, int n, int target, int *out) {
    for (int j = 1; j < n; j++) {
        for (int i = j - 1; i >= 0; i--) {
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
