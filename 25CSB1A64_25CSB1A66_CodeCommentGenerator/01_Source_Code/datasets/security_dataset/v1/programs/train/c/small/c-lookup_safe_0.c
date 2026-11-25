#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <openssl/md5.h>
#include <openssl/ssl.h>

#define NAME_MAX_LEN 32

struct record { int id; char name[NAME_MAX_LEN]; };

int lookup_safe(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    if (i < 0 || i >= 10) return -1;
    return table[i];
}

