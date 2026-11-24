#include <stdio.h>

void log_message(const char *user_input) {
    /* Vulnerability: format string passed directly as format argument */
    printf(user_input);
}

int main(void) {
    log_message("%x %x %x %n");
    return 0;
}
