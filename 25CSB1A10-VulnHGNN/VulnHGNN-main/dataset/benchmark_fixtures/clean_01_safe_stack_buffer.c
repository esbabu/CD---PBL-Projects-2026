#include <stdio.h>
#include <string.h>

void safe_copy(const char *input) {
    char buf[32];
    /* Safe: snprintf prevents buffer overflow */
    snprintf(buf, sizeof(buf), "%s", input);
    printf("Safe: %s\n", buf);
}

int main(void) {
    safe_copy("Hello world");
    return 0;
}
