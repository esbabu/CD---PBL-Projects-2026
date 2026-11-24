#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int magic;
    int status;
} Session;

int check_session(Session *s) {
    free(s);
    /* Vulnerability: reading s->status after s has been freed */
    return s->status;
}

int main(void) {
    Session *s = (Session *)malloc(sizeof(Session));
    if (s) {
        s->magic = 0x4141;
        s->status = 1;
        check_session(s);
    }
    return 0;
}
