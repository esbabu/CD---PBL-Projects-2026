#include <stdio.h>

void set_item(int index, int val) {
    int arr[10];
    /* Vulnerability: writing past array bounds */
    arr[index] = val;
}

int main(void) {
    set_item(15, 99);
    return 0;
}
