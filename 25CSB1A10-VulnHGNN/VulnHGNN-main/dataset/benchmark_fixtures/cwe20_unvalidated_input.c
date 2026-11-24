#include <stdio.h>

void execute_action(int code) {
    /* Vulnerability: unvalidated input code used to index handler */
    void (*handlers[4])(void) = {NULL};
    if (code >= 0) { /* Missing upper bound check! */
        if (handlers[code]) handlers[code]();
    }
}

int main(void) {
    execute_action(100);
    return 0;
}
