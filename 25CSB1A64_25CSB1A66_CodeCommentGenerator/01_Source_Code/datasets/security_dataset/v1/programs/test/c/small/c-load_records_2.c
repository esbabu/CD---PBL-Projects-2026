#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <openssl/md5.h>
#include <openssl/ssl.h>

#define NAME_MAX_LEN 32

struct record { int id; char name[NAME_MAX_LEN]; };

struct record *load_recordsV2(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

