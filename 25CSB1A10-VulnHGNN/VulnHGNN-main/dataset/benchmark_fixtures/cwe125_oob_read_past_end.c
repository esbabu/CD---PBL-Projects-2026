#include <stdio.h>

int read_element(const int *table, int idx) {
    /* Vulnerability: idx not validated against table capacity */
    return table[idx];
}

int main(void) {
    int lookup[4] = {10, 20, 30, 40};
    int val = read_element(lookup, 10);
    printf("Val: %d\n", val);
    return 0;
}
