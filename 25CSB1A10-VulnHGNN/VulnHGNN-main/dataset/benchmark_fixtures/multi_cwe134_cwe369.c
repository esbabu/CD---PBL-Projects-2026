#include <stdio.h>

void display_stats(const char *user_format, int total, int divisor) {
    /* Flaw 1: Format string */
    printf(user_format);
    /* Flaw 2: Divide by zero */
    int stat = total / divisor;
    printf("Stat: %d\n", stat);
}

int main(void) {
    display_stats("%s%s", 100, 0);
    return 0;
}
