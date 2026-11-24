#include <stdio.h>

void safe_index_access(int index) {
    int table[10] = {0};
    /* Safe: strictly validated bounds */
    if (index >= 0 && index < 10) {
        table[index] = 1;
        printf("Set index %d\n", index);
    }
}

int main(void) {
    safe_index_access(5);
    return 0;
}
