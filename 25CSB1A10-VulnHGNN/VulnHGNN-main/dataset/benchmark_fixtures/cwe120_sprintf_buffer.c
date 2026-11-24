#include <stdio.h>

void format_greeting(const char *first, const char *last) {
    char buffer[32];
    /* Vulnerability: sprintf cannot check destination bounds */
    sprintf(buffer, "Hello, %s %s!", first, last);
    printf("%s\n", buffer);
}

int main(void) {
    format_greeting("VeryLongFirstNameExceedingLimit", "VeryLongLastNameExceedingLimit");
    return 0;
}
