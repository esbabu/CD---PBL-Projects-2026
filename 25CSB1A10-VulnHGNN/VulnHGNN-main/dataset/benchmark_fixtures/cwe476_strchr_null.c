#include <stdio.h>
#include <string.h>

void parse_domain(const char *email) {
    const char *at = strchr(email, '@');
    /* Vulnerability: at can be NULL if no @ found */
    char first_letter = *(at + 1);
    printf("Domain first: %c\n", first_letter);
}

int main(void) {
    parse_domain("invalid-email");
    return 0;
}
