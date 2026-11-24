#include <stdio.h>

char get_char_at(const char *str, int offset) {
    /* Vulnerability: negative offset reads before string buffer */
    return str[offset];
}

int main(void) {
    const char *s = "SecureCode";
    char c = get_char_at(s, -5);
    printf("Char: %c\n", c);
    return 0;
}
