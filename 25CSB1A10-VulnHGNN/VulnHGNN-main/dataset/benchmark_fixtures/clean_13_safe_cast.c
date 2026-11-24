#include <stdio.h>
#include <limits.h>

short safe_cast_to_short(int val) {
    /* Safe: explicit range check before casting */
    if (val > SHRT_MAX || val < SHRT_MIN) return 0;
    return (short)val;
}

int main(void) {
    short s = safe_cast_to_short(500);
    printf("Short: %d\n", s);
    return 0;
}
