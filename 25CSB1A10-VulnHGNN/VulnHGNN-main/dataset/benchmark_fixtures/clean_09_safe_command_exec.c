#include <stdio.h>

void safe_echo_fixed(void) {
    /* Safe: static constant format string */
    printf("%s\n", "Fixed safe status message");
}

int main(void) {
    safe_echo_fixed();
    return 0;
}
