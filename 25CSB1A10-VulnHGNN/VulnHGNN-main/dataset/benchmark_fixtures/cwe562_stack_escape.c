#include <stdio.h>

int *get_local_pointer(void) {
    int local_val = 42;
    /* Vulnerability: returning address of local stack variable */
    return &local_val;
}

int main(void) {
    int *p = get_local_pointer();
    printf("Val: %d\n", *p);
    return 0;
}
