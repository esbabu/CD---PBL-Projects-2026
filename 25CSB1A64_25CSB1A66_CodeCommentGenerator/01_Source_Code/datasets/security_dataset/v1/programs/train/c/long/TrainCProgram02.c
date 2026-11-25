#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <openssl/md5.h>
#include <openssl/ssl.h>

#define NAME_MAX_LEN 32

struct record { int id; char name[NAME_MAX_LEN]; };

int clamp_value1(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

void log_request_safeN2(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf("%s", msg);
}

double average_of3(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

int clamp_value4(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

int lookupN5(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    return table[i];
}

void read_packet_safeN6(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    if (len < 0 || len > (int)sizeof body) return;
    memcpy(body, header, len);
}

size_t count_char7(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

double average_of8(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

int is_leap_year9(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month9(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year9(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

int lookupN10(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    return table[i];
}

void greet_safeN11(void) {
    char name[64];
    if (fgets(name, sizeof name, stdin) == NULL) return;
    printf("hello %s\n", name);
}

int is_leap_year12(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month12(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year12(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

size_t count_char13(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

int clamp_value14(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

void read_packet_safeN15(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    if (len < 0 || len > (int)sizeof body) return;
    memcpy(body, header, len);
}

char *make_buffer_safeN16(size_t n) {
    char *p = malloc(n);
    if (p == NULL) return NULL;
    p[0] = '\0';
    return p;
}

int lookup_safeN17(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    if (i < 0 || i >= 10) return -1;
    return table[i];
}

void run_hookN18(void) {
    char *hook = getenv("NETCONF_HOOK");
    system(hook);
}

int is_leap_year19(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month19(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year19(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

double average_of20(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

void reverse_ints21(int *values, size_t n) {
    if (n < 2) {
        return;
    }
    size_t i = 0;
    size_t j = n - 1;
    while (i < j) {
        int tmp = values[i];
        values[i] = values[j];
        values[j] = tmp;
        i++;
        j--;
    }
}

int lookupN22(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    return table[i];
}

void greetN23(void) {
    char name[64];
    gets(name);
    printf("hello %s\n", name);
}

void greet_safeN24(void) {
    char name[64];
    if (fgets(name, sizeof name, stdin) == NULL) return;
    printf("hello %s\n", name);
}

size_t count_char25(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

void log_requestN26(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf(msg);
}

int session_tokenN27(void) {
    return rand();
}

void write_configN28(const char *path) {
    if (access(path, W_OK) == 0) {
        FILE *f = fopen(path, "w");
        fputs("enabled=1\n", f);
        fclose(f);
    }
}

int clamp_value29(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

void log_request_safeN30(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf("%s", msg);
}

int clamp_value31(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

int clamp_value32(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

char *make_bufferN33(size_t n) {
    char *p = malloc(n);
    p[0] = '\0';
    return p;
}

double average_of34(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

void reverse_ints35(int *values, size_t n) {
    if (n < 2) {
        return;
    }
    size_t i = 0;
    size_t j = n - 1;
    while (i < j) {
        int tmp = values[i];
        values[i] = values[j];
        values[j] = tmp;
        i++;
        j--;
    }
}

void read_packetN36(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    memcpy(body, header, len);
}

void greetN37(void) {
    char name[64];
    gets(name);
    printf("hello %s\n", name);
}

void read_packetN38(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    memcpy(body, header, len);
}

double average_of39(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

int lookupN40(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    return table[i];
}

size_t count_char41(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

void log_requestN42(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf(msg);
}

void read_packetN43(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    memcpy(body, header, len);
}

int clamp_value44(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

size_t count_char45(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

char *make_bufferN46(size_t n) {
    char *p = malloc(n);
    p[0] = '\0';
    return p;
}

double average_of47(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

void run_hookN48(void) {
    char *hook = getenv("NETCONF_HOOK");
    system(hook);
}

void greet_safeN49(void) {
    char name[64];
    if (fgets(name, sizeof name, stdin) == NULL) return;
    printf("hello %s\n", name);
}

int is_leap_year50(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month50(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year50(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

int is_leap_year51(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month51(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year51(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

void release_twiceN52(char *p, int fail) {
    free(p);
    if (fail) {
        free(p);
    }
}

void read_packetN53(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    memcpy(body, header, len);
}

size_t count_char54(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

void greet_safeN55(void) {
    char name[64];
    if (fgets(name, sizeof name, stdin) == NULL) return;
    printf("hello %s\n", name);
}

int lookupN56(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    return table[i];
}

void greet_safeN57(void) {
    char name[64];
    if (fgets(name, sizeof name, stdin) == NULL) return;
    printf("hello %s\n", name);
}

void greet_safeN58(void) {
    char name[64];
    if (fgets(name, sizeof name, stdin) == NULL) return;
    printf("hello %s\n", name);
}

double average_of59(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

void read_packet_safeN60(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    if (len < 0 || len > (int)sizeof body) return;
    memcpy(body, header, len);
}

char *make_bufferN61(size_t n) {
    char *p = malloc(n);
    p[0] = '\0';
    return p;
}

size_t count_char62(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

void reverse_ints63(int *values, size_t n) {
    if (n < 2) {
        return;
    }
    size_t i = 0;
    size_t j = n - 1;
    while (i < j) {
        int tmp = values[i];
        values[i] = values[j];
        values[j] = tmp;
        i++;
        j--;
    }
}

size_t count_char64(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

size_t count_char65(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

size_t count_char66(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

int lookupN67(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    return table[i];
}

double average_of68(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

void greetN69(void) {
    char name[64];
    gets(name);
    printf("hello %s\n", name);
}

void greet_safeN70(void) {
    char name[64];
    if (fgets(name, sizeof name, stdin) == NULL) return;
    printf("hello %s\n", name);
}

void reverse_ints71(int *values, size_t n) {
    if (n < 2) {
        return;
    }
    size_t i = 0;
    size_t j = n - 1;
    while (i < j) {
        int tmp = values[i];
        values[i] = values[j];
        values[j] = tmp;
        i++;
        j--;
    }
}

int lookup_safeN72(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    if (i < 0 || i >= 10) return -1;
    return table[i];
}

void write_configN73(const char *path) {
    if (access(path, W_OK) == 0) {
        FILE *f = fopen(path, "w");
        fputs("enabled=1\n", f);
        fclose(f);
    }
}

int session_tokenN74(void) {
    return rand();
}

double average_of75(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

char *make_bufferN76(size_t n) {
    char *p = malloc(n);
    p[0] = '\0';
    return p;
}

void read_packetN77(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    memcpy(body, header, len);
}

int clamp_value78(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

int is_leap_year79(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month79(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year79(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

size_t count_char80(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

int clamp_value81(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

void log_requestN82(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf(msg);
}

void reverse_ints83(int *values, size_t n) {
    if (n < 2) {
        return;
    }
    size_t i = 0;
    size_t j = n - 1;
    while (i < j) {
        int tmp = values[i];
        values[i] = values[j];
        values[j] = tmp;
        i++;
        j--;
    }
}

void greetN84(void) {
    char name[64];
    gets(name);
    printf("hello %s\n", name);
}

double average_of85(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

int is_leap_year86(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month86(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year86(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

double average_of87(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

size_t count_char88(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

int is_leap_year89(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month89(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year89(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

void release_twiceN90(char *p, int fail) {
    free(p);
    if (fail) {
        free(p);
    }
}

void greetN91(void) {
    char name[64];
    gets(name);
    printf("hello %s\n", name);
}

void read_packetN92(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    memcpy(body, header, len);
}

size_t count_char93(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

void write_configN94(const char *path) {
    if (access(path, W_OK) == 0) {
        FILE *f = fopen(path, "w");
        fputs("enabled=1\n", f);
        fclose(f);
    }
}

int is_leap_year95(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month95(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year95(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

void read_packetN96(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    memcpy(body, header, len);
}

char *make_bufferN97(size_t n) {
    char *p = malloc(n);
    p[0] = '\0';
    return p;
}

int clamp_value98(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

void copy_nameN99(int argc, char **argv) {
    char buf[16];
    strcpy(buf, argv[1]);
    puts(buf);
}

int is_leap_year100(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month100(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year100(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

void reverse_ints101(int *values, size_t n) {
    if (n < 2) {
        return;
    }
    size_t i = 0;
    size_t j = n - 1;
    while (i < j) {
        int tmp = values[i];
        values[i] = values[j];
        values[j] = tmp;
        i++;
        j--;
    }
}

void reverse_ints102(int *values, size_t n) {
    if (n < 2) {
        return;
    }
    size_t i = 0;
    size_t j = n - 1;
    while (i < j) {
        int tmp = values[i];
        values[i] = values[j];
        values[j] = tmp;
        i++;
        j--;
    }
}

void reverse_ints103(int *values, size_t n) {
    if (n < 2) {
        return;
    }
    size_t i = 0;
    size_t j = n - 1;
    while (i < j) {
        int tmp = values[i];
        values[i] = values[j];
        values[j] = tmp;
        i++;
        j--;
    }
}

int is_leap_year104(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month104(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year104(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

void reverse_ints105(int *values, size_t n) {
    if (n < 2) {
        return;
    }
    size_t i = 0;
    size_t j = n - 1;
    while (i < j) {
        int tmp = values[i];
        values[i] = values[j];
        values[j] = tmp;
        i++;
        j--;
    }
}

int lookup_safeN106(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    if (i < 0 || i >= 10) return -1;
    return table[i];
}

void reverse_ints107(int *values, size_t n) {
    if (n < 2) {
        return;
    }
    size_t i = 0;
    size_t j = n - 1;
    while (i < j) {
        int tmp = values[i];
        values[i] = values[j];
        values[j] = tmp;
        i++;
        j--;
    }
}

size_t count_char108(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

void copy_nameN109(int argc, char **argv) {
    char buf[16];
    strcpy(buf, argv[1]);
    puts(buf);
}

void log_request_safeN110(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf("%s", msg);
}

void reverse_ints111(int *values, size_t n) {
    if (n < 2) {
        return;
    }
    size_t i = 0;
    size_t j = n - 1;
    while (i < j) {
        int tmp = values[i];
        values[i] = values[j];
        values[j] = tmp;
        i++;
        j--;
    }
}

int clamp_value112(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

double average_of113(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

void release_twiceN114(char *p, int fail) {
    free(p);
    if (fail) {
        free(p);
    }
}

int lookup_safeN115(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    if (i < 0 || i >= 10) return -1;
    return table[i];
}

int clamp_value116(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

void read_packetN117(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    memcpy(body, header, len);
}

int clamp_value118(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

int is_leap_year119(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month119(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year119(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

void read_packet_safeN120(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    if (len < 0 || len > (int)sizeof body) return;
    memcpy(body, header, len);
}

int session_tokenN121(void) {
    return rand();
}

char *make_buffer_safeN122(size_t n) {
    char *p = malloc(n);
    if (p == NULL) return NULL;
    p[0] = '\0';
    return p;
}

char *make_bufferN123(size_t n) {
    char *p = malloc(n);
    p[0] = '\0';
    return p;
}

int clamp_value124(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

double average_of125(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

int is_leap_year126(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month126(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year126(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

void log_request_safeN127(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf("%s", msg);
}

void log_request_safeN128(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf("%s", msg);
}

void read_packet_safeN129(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    if (len < 0 || len > (int)sizeof body) return;
    memcpy(body, header, len);
}

void reverse_ints130(int *values, size_t n) {
    if (n < 2) {
        return;
    }
    size_t i = 0;
    size_t j = n - 1;
    while (i < j) {
        int tmp = values[i];
        values[i] = values[j];
        values[j] = tmp;
        i++;
        j--;
    }
}

int is_leap_year131(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month131(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year131(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

int is_leap_year132(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month132(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year132(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

void copy_name_safeN133(const char *src) {
    char buf[16];
    snprintf(buf, sizeof buf, "%s", src);
    puts(buf);
}

void copy_name_safeN134(const char *src) {
    char buf[16];
    snprintf(buf, sizeof buf, "%s", src);
    puts(buf);
}

int lookupN135(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    return table[i];
}

int clamp_value136(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

void greetN137(void) {
    char name[64];
    gets(name);
    printf("hello %s\n", name);
}

double average_of138(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

int is_leap_year139(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month139(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year139(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

int lookup_safeN140(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    if (i < 0 || i >= 10) return -1;
    return table[i];
}

void reverse_ints141(int *values, size_t n) {
    if (n < 2) {
        return;
    }
    size_t i = 0;
    size_t j = n - 1;
    while (i < j) {
        int tmp = values[i];
        values[i] = values[j];
        values[j] = tmp;
        i++;
        j--;
    }
}

int session_tokenN142(void) {
    return rand();
}

int session_tokenN143(void) {
    return rand();
}

void read_packet_safeN144(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    if (len < 0 || len > (int)sizeof body) return;
    memcpy(body, header, len);
}

int clamp_value145(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

void release_twiceN146(char *p, int fail) {
    free(p);
    if (fail) {
        free(p);
    }
}

int clamp_value147(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

int is_leap_year148(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month148(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year148(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

void copy_nameN149(int argc, char **argv) {
    char buf[16];
    strcpy(buf, argv[1]);
    puts(buf);
}

double average_of150(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

void write_configN151(const char *path) {
    if (access(path, W_OK) == 0) {
        FILE *f = fopen(path, "w");
        fputs("enabled=1\n", f);
        fclose(f);
    }
}

int clamp_value152(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

size_t count_char153(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

int lookup_safeN154(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    if (i < 0 || i >= 10) return -1;
    return table[i];
}

void reverse_ints155(int *values, size_t n) {
    if (n < 2) {
        return;
    }
    size_t i = 0;
    size_t j = n - 1;
    while (i < j) {
        int tmp = values[i];
        values[i] = values[j];
        values[j] = tmp;
        i++;
        j--;
    }
}

size_t count_char156(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

void write_configN157(const char *path) {
    if (access(path, W_OK) == 0) {
        FILE *f = fopen(path, "w");
        fputs("enabled=1\n", f);
        fclose(f);
    }
}

void greetN158(void) {
    char name[64];
    gets(name);
    printf("hello %s\n", name);
}

double average_of159(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

int is_leap_year160(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month160(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year160(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

int clamp_value161(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

void read_packetN162(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    memcpy(body, header, len);
}

int clamp_value163(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

char *make_bufferN164(size_t n) {
    char *p = malloc(n);
    p[0] = '\0';
    return p;
}

int is_leap_year165(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month165(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year165(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

int clamp_value166(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

double average_of167(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

void read_packetN168(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    memcpy(body, header, len);
}

void copy_name_safeN169(const char *src) {
    char buf[16];
    snprintf(buf, sizeof buf, "%s", src);
    puts(buf);
}

double average_of170(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

int clamp_value171(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

void reverse_ints172(int *values, size_t n) {
    if (n < 2) {
        return;
    }
    size_t i = 0;
    size_t j = n - 1;
    while (i < j) {
        int tmp = values[i];
        values[i] = values[j];
        values[j] = tmp;
        i++;
        j--;
    }
}

double average_of173(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

int is_leap_year174(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month174(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year174(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

void log_request_safeN175(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf("%s", msg);
}

int clamp_value176(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

void reverse_ints177(int *values, size_t n) {
    if (n < 2) {
        return;
    }
    size_t i = 0;
    size_t j = n - 1;
    while (i < j) {
        int tmp = values[i];
        values[i] = values[j];
        values[j] = tmp;
        i++;
        j--;
    }
}

int session_tokenN178(void) {
    return rand();
}

void read_packet_safeN179(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    if (len < 0 || len > (int)sizeof body) return;
    memcpy(body, header, len);
}

void run_hookN180(void) {
    char *hook = getenv("NETCONF_HOOK");
    system(hook);
}

size_t count_char181(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

char *make_bufferN182(size_t n) {
    char *p = malloc(n);
    p[0] = '\0';
    return p;
}

double average_of183(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

void reverse_ints184(int *values, size_t n) {
    if (n < 2) {
        return;
    }
    size_t i = 0;
    size_t j = n - 1;
    while (i < j) {
        int tmp = values[i];
        values[i] = values[j];
        values[j] = tmp;
        i++;
        j--;
    }
}

void greet_safeN185(void) {
    char name[64];
    if (fgets(name, sizeof name, stdin) == NULL) return;
    printf("hello %s\n", name);
}

int is_leap_year186(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month186(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year186(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

size_t count_char187(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

int clamp_value188(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

int is_leap_year189(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month189(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year189(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

