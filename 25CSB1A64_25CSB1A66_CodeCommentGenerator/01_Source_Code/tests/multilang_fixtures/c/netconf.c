/* netconf: a small configuration daemon. Vulnerable functions are marked "expect";
 * each has a safe twin below it. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <openssl/md5.h>
#include <openssl/ssl.h>

#define NAME_MAX_LEN 32

struct record { int id; char name[NAME_MAX_LEN]; };

void greet(void) {
    char name[64];
    gets(name);                                                     /* expect: SEC051 */
    printf("hello %s\n", name);
}

void greet_safe(void) {
    char name[64];
    if (fgets(name, sizeof name, stdin) == NULL) return;
    printf("hello %s\n", name);
}

void copy_name(int argc, char **argv) {
    char buf[16];
    strcpy(buf, argv[1]);                                           /* expect: SEC052 */
    puts(buf);
}

void copy_name_safe(const char *src) {
    char buf[16];
    snprintf(buf, sizeof buf, "%s", src);
    puts(buf);
}

void log_request(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf(msg);                                                    /* expect: SEC026 */
}

void log_request_safe(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf("%s", msg);
}

void read_packet(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    memcpy(body, header, len);                                      /* expect: SEC053 */
}

void read_packet_safe(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    if (len < 0 || len > (int)sizeof body) return;
    memcpy(body, header, len);
}

int lookup(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    return table[i];                                                /* expect: SEC054 */
}

int lookup_safe(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    if (i < 0 || i >= 10) return -1;
    return table[i];
}

struct record *load_records(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));       /* expect: SEC055 */
    return r;
}

void release(struct record *r) {
    free(r);
    printf("released %d\n", r->id);                                 /* expect: SEC056 */
}

void release_twice(char *p, int fail) {
    free(p);
    if (fail) {
        free(p);                                                    /* expect: SEC057 */
    }
}

void release_safe(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

char *make_buffer(size_t n) {
    char *p = malloc(n);
    p[0] = '\0';                                                    /* expect: SEC058 */
    return p;
}

char *make_buffer_safe(size_t n) {
    char *p = malloc(n);
    if (p == NULL) return NULL;
    p[0] = '\0';
    return p;
}

void run_hook(void) {
    char *hook = getenv("NETCONF_HOOK");
    system(hook);                                                   /* expect: SEC002 */
}

void write_config(const char *path) {
    if (access(path, W_OK) == 0) {
        FILE *f = fopen(path, "w");                                 /* expect: SEC059 */
        fputs("enabled=1\n", f);
        fclose(f);
    }
}

void checksum(const unsigned char *data, size_t n, unsigned char *out) {
    MD5(data, n, out);                                              /* expect: SEC004 */
}

void tls_client(SSL_CTX *ctx) {
    SSL_CTX_set_verify(ctx, SSL_VERIFY_NONE, NULL);                 /* expect: SEC031 */
}

int session_token(void) {
    return rand();                                                  /* expect: SEC011 */
}

int main(int argc, char **argv) {
    copy_name(argc, argv);
    return 0;
}
