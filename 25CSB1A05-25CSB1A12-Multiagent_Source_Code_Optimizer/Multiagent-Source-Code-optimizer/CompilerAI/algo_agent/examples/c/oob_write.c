/* Correct buffer writer writing within bounds [0, n). */
int oob_write(int *arr, int n) {
    int s = 0;
    for (int i = 0; i < n; i++) {
        arr[i] = arr[i] + 1;
        s += arr[i];
    }
    return s;
}
