#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <openssl/md5.h>
#include <openssl/ssl.h>

#define NAME_MAX_LEN 32

struct record { int id; char name[NAME_MAX_LEN]; };

double average_of1(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

void log_requestN2(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf(msg);
}

int clamp_value3(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
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

int is_leap_year5(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month5(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year5(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

double average_of6(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

char *make_bufferN7(size_t n) {
    char *p = malloc(n);
    p[0] = '\0';
    return p;
}

void greetN8(void) {
    char name[64];
    gets(name);
    printf("hello %s\n", name);
}

void log_requestN9(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf(msg);
}

void release_twiceN10(char *p, int fail) {
    free(p);
    if (fail) {
        free(p);
    }
}

int clamp_value11(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

size_t count_char12(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

void run_hookN13(void) {
    char *hook = getenv("NETCONF_HOOK");
    system(hook);
}

void copy_nameN14(int argc, char **argv) {
    char buf[16];
    strcpy(buf, argv[1]);
    puts(buf);
}

void write_configN15(const char *path) {
    if (access(path, W_OK) == 0) {
        FILE *f = fopen(path, "w");
        fputs("enabled=1\n", f);
        fclose(f);
    }
}

void copy_name_safeN16(const char *src) {
    char buf[16];
    snprintf(buf, sizeof buf, "%s", src);
    puts(buf);
}

void reverse_ints17(int *values, size_t n) {
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

double average_of18(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

int clamp_value19(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

void copy_nameN20(int argc, char **argv) {
    char buf[16];
    strcpy(buf, argv[1]);
    puts(buf);
}

double average_of21(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

void log_requestN22(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf(msg);
}

int session_tokenN23(void) {
    return rand();
}

void log_requestN24(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf(msg);
}

void read_packet_safeN25(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    if (len < 0 || len > (int)sizeof body) return;
    memcpy(body, header, len);
}

void reverse_ints26(int *values, size_t n) {
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

int lookupN27(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    return table[i];
}

void write_configN28(const char *path) {
    if (access(path, W_OK) == 0) {
        FILE *f = fopen(path, "w");
        fputs("enabled=1\n", f);
        fclose(f);
    }
}

int is_leap_year29(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month29(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year29(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

void reverse_ints30(int *values, size_t n) {
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

int session_tokenN31(void) {
    return rand();
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

void reverse_ints33(int *values, size_t n) {
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

char *make_bufferN34(size_t n) {
    char *p = malloc(n);
    p[0] = '\0';
    return p;
}

void read_packet_safeN35(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    if (len < 0 || len > (int)sizeof body) return;
    memcpy(body, header, len);
}

size_t count_char36(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

int clamp_value37(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

void log_requestN38(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf(msg);
}

void reverse_ints39(int *values, size_t n) {
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

int is_leap_year40(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month40(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year40(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

void reverse_ints41(int *values, size_t n) {
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

void copy_name_safeN42(const char *src) {
    char buf[16];
    snprintf(buf, sizeof buf, "%s", src);
    puts(buf);
}

void reverse_ints43(int *values, size_t n) {
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

int clamp_value44(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

double average_of45(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

void reverse_ints46(int *values, size_t n) {
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

int is_leap_year48(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month48(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year48(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

double average_of49(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

int session_tokenN50(void) {
    return rand();
}

void log_request_safeN51(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf("%s", msg);
}

size_t count_char52(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

void copy_name_safeN53(const char *src) {
    char buf[16];
    snprintf(buf, sizeof buf, "%s", src);
    puts(buf);
}

void log_requestN54(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf(msg);
}

void copy_name_safeN55(const char *src) {
    char buf[16];
    snprintf(buf, sizeof buf, "%s", src);
    puts(buf);
}

int lookupN56(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    return table[i];
}

void log_request_safeN57(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf("%s", msg);
}

double average_of58(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

int lookupN59(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    return table[i];
}

char *make_bufferN60(size_t n) {
    char *p = malloc(n);
    p[0] = '\0';
    return p;
}

void greet_safeN61(void) {
    char name[64];
    if (fgets(name, sizeof name, stdin) == NULL) return;
    printf("hello %s\n", name);
}

int session_tokenN62(void) {
    return rand();
}

double average_of63(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

void greetN64(void) {
    char name[64];
    gets(name);
    printf("hello %s\n", name);
}

double average_of65(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

void copy_nameN66(int argc, char **argv) {
    char buf[16];
    strcpy(buf, argv[1]);
    puts(buf);
}

int is_leap_year67(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month67(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year67(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

void greet_safeN68(void) {
    char name[64];
    if (fgets(name, sizeof name, stdin) == NULL) return;
    printf("hello %s\n", name);
}

int clamp_value69(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

size_t count_char70(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

int clamp_value71(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

int clamp_value72(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

int is_leap_year73(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month73(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year73(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

int is_leap_year74(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month74(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year74(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
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

double average_of76(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

int is_leap_year77(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month77(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year77(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

void release_twiceN78(char *p, int fail) {
    free(p);
    if (fail) {
        free(p);
    }
}

void read_packetN79(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    memcpy(body, header, len);
}

int session_tokenN80(void) {
    return rand();
}

int is_leap_year81(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month81(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year81(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

void log_request_safeN82(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf("%s", msg);
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

void reverse_ints84(int *values, size_t n) {
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

size_t count_char85(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

void copy_name_safeN86(const char *src) {
    char buf[16];
    snprintf(buf, sizeof buf, "%s", src);
    puts(buf);
}

size_t count_char87(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

int is_leap_year88(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month88(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year88(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

char *make_bufferN89(size_t n) {
    char *p = malloc(n);
    p[0] = '\0';
    return p;
}

void greetN90(void) {
    char name[64];
    gets(name);
    printf("hello %s\n", name);
}

size_t count_char91(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

void reverse_ints92(int *values, size_t n) {
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

int clamp_value93(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

void reverse_ints94(int *values, size_t n) {
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

char *make_bufferN95(size_t n) {
    char *p = malloc(n);
    p[0] = '\0';
    return p;
}

void greetN96(void) {
    char name[64];
    gets(name);
    printf("hello %s\n", name);
}

int clamp_value97(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

char *make_bufferN98(size_t n) {
    char *p = malloc(n);
    p[0] = '\0';
    return p;
}

void release_twiceN99(char *p, int fail) {
    free(p);
    if (fail) {
        free(p);
    }
}

char *make_buffer_safeN100(size_t n) {
    char *p = malloc(n);
    if (p == NULL) return NULL;
    p[0] = '\0';
    return p;
}

double average_of101(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

void copy_nameN102(int argc, char **argv) {
    char buf[16];
    strcpy(buf, argv[1]);
    puts(buf);
}

void log_request_safeN103(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf("%s", msg);
}

int lookup_safeN104(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    if (i < 0 || i >= 10) return -1;
    return table[i];
}

void greet_safeN105(void) {
    char name[64];
    if (fgets(name, sizeof name, stdin) == NULL) return;
    printf("hello %s\n", name);
}

size_t count_char106(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

int clamp_value107(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

int is_leap_year108(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month108(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year108(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

int clamp_value109(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

void read_packetN110(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    memcpy(body, header, len);
}

char *make_bufferN111(size_t n) {
    char *p = malloc(n);
    p[0] = '\0';
    return p;
}

void greet_safeN112(void) {
    char name[64];
    if (fgets(name, sizeof name, stdin) == NULL) return;
    printf("hello %s\n", name);
}

void release_twiceN113(char *p, int fail) {
    free(p);
    if (fail) {
        free(p);
    }
}

void greetN114(void) {
    char name[64];
    gets(name);
    printf("hello %s\n", name);
}

void read_packet_safeN115(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    if (len < 0 || len > (int)sizeof body) return;
    memcpy(body, header, len);
}

void write_configN116(const char *path) {
    if (access(path, W_OK) == 0) {
        FILE *f = fopen(path, "w");
        fputs("enabled=1\n", f);
        fclose(f);
    }
}

size_t count_char117(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

char *make_bufferN118(size_t n) {
    char *p = malloc(n);
    p[0] = '\0';
    return p;
}

int clamp_value119(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

int clamp_value120(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

int lookupN121(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    return table[i];
}

int lookupN122(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    return table[i];
}

void read_packetN123(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    memcpy(body, header, len);
}

void read_packet_safeN124(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    if (len < 0 || len > (int)sizeof body) return;
    memcpy(body, header, len);
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

double average_of126(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

int is_leap_year127(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month127(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year127(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

void copy_name_safeN128(const char *src) {
    char buf[16];
    snprintf(buf, sizeof buf, "%s", src);
    puts(buf);
}

int is_leap_year129(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month129(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year129(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

