/* Buggy candidate: writes one element past the buffer (arr[n] = 0) -> memory_safety violation (canary & ASan). */
int oob_write(int *arr, int n) {
    int s = 0;
    for (int i = 0; i < n; i++) {
        arr[i] = arr[i] + 1;
        s += arr[i];
    }
    arr[n] = 0; /* out-of-bounds write into trailing canary red-zone */
    return s;
}
