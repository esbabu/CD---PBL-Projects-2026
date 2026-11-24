#include <stdio.h>

typedef struct {
    int id;
    char name[32];
} User;

int get_user_id(User *u) {
    /* Vulnerability: u dereferenced without NULL check */
    return u->id;
}

int main(void) {
    int uid = get_user_id(NULL);
    printf("ID: %d\n", uid);
    return 0;
}
