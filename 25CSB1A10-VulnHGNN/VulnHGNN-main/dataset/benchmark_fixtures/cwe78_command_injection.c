#include <stdio.h>
#include <stdlib.h>

void ping_host(const char *hostname) {
    char cmd[256];
    /* Vulnerability: unvalidated string formatted into system command */
    snprintf(cmd, sizeof(cmd), "ping -c 1 %s", hostname);
    system(cmd);
}

int main(void) {
    ping_host("localhost; rm -rf /");
    return 0;
}
