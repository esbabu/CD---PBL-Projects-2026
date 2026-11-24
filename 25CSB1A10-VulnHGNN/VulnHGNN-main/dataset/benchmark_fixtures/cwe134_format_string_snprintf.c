#include <stdio.h>

void format_status(char *out, size_t out_len, const char *status) {
    /* Vulnerability: status used as format string instead of specifier */
    snprintf(out, out_len, status);
}

int main(void) {
    char buf[128];
    format_status(buf, sizeof(buf), "%p%p%p");
    return 0;
}
