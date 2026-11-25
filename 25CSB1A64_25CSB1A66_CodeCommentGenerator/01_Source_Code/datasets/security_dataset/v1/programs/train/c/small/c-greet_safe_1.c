#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <openssl/md5.h>
#include <openssl/ssl.h>

#define NAME_MAX_LEN 32

struct record { int id; char name[NAME_MAX_LEN]; };

void greet_safeV1(void) {
    char name[64];
    if (fgets(name, sizeof name, stdin) == NULL) return;
    printf("hello %s\n", name);
}

