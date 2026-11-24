#include <stdio.h>
#include <stddef.h>

size_t get_remaining_buffer(size_t used, size_t offset) {
    /* Vulnerability: offset > used wraps size_t to near SIZE_MAX */
    size_t rem = used - offset;
    return rem;
}

int main(void) {
    size_t rem = get_remaining_buffer(10, 25);
    printf("Remaining: %zu\n", rem);
    return 0;
}
