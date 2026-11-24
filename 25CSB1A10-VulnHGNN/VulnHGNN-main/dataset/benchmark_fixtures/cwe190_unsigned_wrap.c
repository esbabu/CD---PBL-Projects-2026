#include <stdio.h>

unsigned int compute_next_seq(unsigned int current) {
    /* Vulnerability: unsigned integer wrap-around */
    unsigned int next = current + 10;
    return next;
}

int main(void) {
    unsigned int val = compute_next_seq(4294967290U);
    printf("Seq: %u\n", val);
    return 0;
}
