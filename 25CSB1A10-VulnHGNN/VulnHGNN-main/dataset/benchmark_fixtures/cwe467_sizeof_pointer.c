#include <stdio.h>
#include <string.h>

void clear_buffer(int *buffer) {
    /* Vulnerability: sizeof(buffer) returns pointer size (4 or 8), not buffer capacity */
    memset(buffer, 0, sizeof(buffer));
}

int main(void) {
    int arr[100];
    clear_buffer(arr);
    return 0;
}
