#include <stdio.h>

void safe_log(const char *msg) {
    /* Safe: %s format specifier prevents format string exploit */
    printf("%s\n", msg);
}

int main(void) {
    safe_log("%x %n %s");
    return 0;
}
