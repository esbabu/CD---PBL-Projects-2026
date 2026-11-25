#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <openssl/md5.h>
#include <openssl/ssl.h>

#define NAME_MAX_LEN 32

struct record { int id; char name[NAME_MAX_LEN]; };

void copy_name_safeV2(const char *src) {
    char buf[16];
    snprintf(buf, sizeof buf, "%s", src);
    puts(buf);
}

