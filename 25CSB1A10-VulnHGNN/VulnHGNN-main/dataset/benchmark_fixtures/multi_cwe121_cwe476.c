#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void process_request(const char *name) {
    char stack_buf[16];
    /* Flaw 1: Stack overflow via strcpy */
    strcpy(stack_buf, name);

    char *heap_buf = (char *)malloc(64);
    /* Flaw 2: NULL pointer dereference (heap_buf unchecked) */
    heap_buf[0] = stack_buf[0];
    free(heap_buf);
}

int main(void) {
    process_request("SuperLongNameThatOverflowsTheStackBuffer");
    return 0;
}
