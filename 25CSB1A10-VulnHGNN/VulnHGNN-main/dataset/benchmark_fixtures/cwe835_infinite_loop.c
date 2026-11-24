#include <stdio.h>

void process_tokens(unsigned int count) {
    /* Vulnerability: unsigned loop condition >= 0 is always true */
    for (unsigned int i = count; i >= 0; i--) {
        printf("%u\n", i);
        if (i == 0) break; /* If break missing or bugged, infinite loop */
    }
}

int main(void) {
    process_tokens(5);
    return 0;
}
