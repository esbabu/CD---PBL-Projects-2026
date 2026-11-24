/* O(n log n) equivalent two_sum using sorted (value, index) array + binary search. */
#include <stdlib.h>

typedef struct { int val; int idx; } _Pair;

static int _cmp_pair(const void *a, const void *b) {
    const _Pair *pa = (const _Pair *)a;
    const _Pair *pb = (const _Pair *)b;
    if (pa->val != pb->val) return (pa->val > pb->val) - (pa->val < pb->val);
    return (pa->idx > pb->idx) - (pa->idx < pb->idx);
}

int two_sum(const int *nums, int n, int target, int *out) {
    if (n < 2) {
        out[0] = -1;
        out[1] = -1;
        return 0;
    }
    _Pair *pairs = (_Pair *)malloc((size_t)n * sizeof(_Pair));
    if (!pairs) return 0;
    for (int i = 0; i < n; i++) {
        pairs[i].val = nums[i];
        pairs[i].idx = i;
    }
    qsort(pairs, (size_t)n, sizeof(_Pair), _cmp_pair);
    for (int i = 0; i < n; i++) {
        long long need = (long long)target - (long long)nums[i];
        int lo = 0, hi = n;
        while (lo < hi) {
            int mid = lo + (hi - lo) / 2;
            if ((long long)pairs[mid].val < need ||
                ((long long)pairs[mid].val == need && pairs[mid].idx <= i)) {
                lo = mid + 1;
            } else {
                hi = mid;
            }
        }
        if (lo < n && (long long)pairs[lo].val == need && pairs[lo].idx > i) {
            out[0] = i;
            out[1] = pairs[lo].idx;
            free(pairs);
            return 1;
        }
    }
    free(pairs);
    out[0] = -1;
    out[1] = -1;
    return 0;
}
