#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <openssl/md5.h>
#include <openssl/ssl.h>

#define NAME_MAX_LEN 32

struct record { int id; char name[NAME_MAX_LEN]; };

size_t count_char1(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

int is_leap_year2(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month2(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year2(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

int is_leap_year3(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month3(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year3(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

size_t count_char4(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

int lookupN5(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    return table[i];
}

void log_request_safeN6(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf("%s", msg);
}

double average_of7(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

void copy_name_safeN8(const char *src) {
    char buf[16];
    snprintf(buf, sizeof buf, "%s", src);
    puts(buf);
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

void release_twiceN10(char *p, int fail) {
    free(p);
    if (fail) {
        free(p);
    }
}

void read_packet_safeN11(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    if (len < 0 || len > (int)sizeof body) return;
    memcpy(body, header, len);
}

void greetN12(void) {
    char name[64];
    gets(name);
    printf("hello %s\n", name);
}

void reverse_ints13(int *values, size_t n) {
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

int clamp_value14(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

void write_configN15(const char *path) {
    if (access(path, W_OK) == 0) {
        FILE *f = fopen(path, "w");
        fputs("enabled=1\n", f);
        fclose(f);
    }
}

size_t count_char16(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

void greetN17(void) {
    char name[64];
    gets(name);
    printf("hello %s\n", name);
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

void log_request_safeN19(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf("%s", msg);
}

size_t count_char20(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

char *make_buffer_safeN21(size_t n) {
    char *p = malloc(n);
    if (p == NULL) return NULL;
    p[0] = '\0';
    return p;
}

void copy_nameN22(int argc, char **argv) {
    char buf[16];
    strcpy(buf, argv[1]);
    puts(buf);
}

void run_hookN23(void) {
    char *hook = getenv("NETCONF_HOOK");
    system(hook);
}

void copy_nameN24(int argc, char **argv) {
    char buf[16];
    strcpy(buf, argv[1]);
    puts(buf);
}

void run_hookN25(void) {
    char *hook = getenv("NETCONF_HOOK");
    system(hook);
}

int is_leap_year26(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month26(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year26(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

size_t count_char27(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

int is_leap_year28(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month28(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year28(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

size_t count_char29(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
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

void copy_name_safeN31(const char *src) {
    char buf[16];
    snprintf(buf, sizeof buf, "%s", src);
    puts(buf);
}

int is_leap_year32(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month32(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year32(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

void write_configN33(const char *path) {
    if (access(path, W_OK) == 0) {
        FILE *f = fopen(path, "w");
        fputs("enabled=1\n", f);
        fclose(f);
    }
}

void read_packetN34(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    memcpy(body, header, len);
}

size_t count_char35(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

void log_request_safeN36(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf("%s", msg);
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

void greet_safeN38(void) {
    char name[64];
    if (fgets(name, sizeof name, stdin) == NULL) return;
    printf("hello %s\n", name);
}

int clamp_value39(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

void release_twiceN40(char *p, int fail) {
    free(p);
    if (fail) {
        free(p);
    }
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

void copy_nameN43(int argc, char **argv) {
    char buf[16];
    strcpy(buf, argv[1]);
    puts(buf);
}

void reverse_ints44(int *values, size_t n) {
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

int is_leap_year45(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month45(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year45(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

void read_packetN46(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    memcpy(body, header, len);
}

void reverse_ints47(int *values, size_t n) {
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

void log_requestN48(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf(msg);
}

void write_configN49(const char *path) {
    if (access(path, W_OK) == 0) {
        FILE *f = fopen(path, "w");
        fputs("enabled=1\n", f);
        fclose(f);
    }
}

int lookup_safeN50(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    if (i < 0 || i >= 10) return -1;
    return table[i];
}

void reverse_ints51(int *values, size_t n) {
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

int clamp_value52(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

void run_hookN53(void) {
    char *hook = getenv("NETCONF_HOOK");
    system(hook);
}

void read_packetN54(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    memcpy(body, header, len);
}

int clamp_value55(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

int lookup_safeN56(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    if (i < 0 || i >= 10) return -1;
    return table[i];
}

int is_leap_year57(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month57(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year57(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

int is_leap_year58(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month58(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year58(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

char *make_bufferN59(size_t n) {
    char *p = malloc(n);
    p[0] = '\0';
    return p;
}

void read_packet_safeN60(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    if (len < 0 || len > (int)sizeof body) return;
    memcpy(body, header, len);
}

void write_configN61(const char *path) {
    if (access(path, W_OK) == 0) {
        FILE *f = fopen(path, "w");
        fputs("enabled=1\n", f);
        fclose(f);
    }
}

int clamp_value62(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

void log_requestN63(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf(msg);
}

void reverse_ints64(int *values, size_t n) {
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

int lookup_safeN65(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    if (i < 0 || i >= 10) return -1;
    return table[i];
}

char *make_buffer_safeN66(size_t n) {
    char *p = malloc(n);
    if (p == NULL) return NULL;
    p[0] = '\0';
    return p;
}

char *make_buffer_safeN67(size_t n) {
    char *p = malloc(n);
    if (p == NULL) return NULL;
    p[0] = '\0';
    return p;
}

int session_tokenN68(void) {
    return rand();
}

int lookup_safeN69(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    if (i < 0 || i >= 10) return -1;
    return table[i];
}

int clamp_value70(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

size_t count_char71(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

void read_packet_safeN72(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    if (len < 0 || len > (int)sizeof body) return;
    memcpy(body, header, len);
}

int clamp_value73(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

void reverse_ints74(int *values, size_t n) {
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

void read_packet_safeN75(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    if (len < 0 || len > (int)sizeof body) return;
    memcpy(body, header, len);
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

void reverse_ints77(int *values, size_t n) {
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

void copy_nameN78(int argc, char **argv) {
    char buf[16];
    strcpy(buf, argv[1]);
    puts(buf);
}

void reverse_ints79(int *values, size_t n) {
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

void reverse_ints80(int *values, size_t n) {
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

void read_packet_safeN83(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    if (len < 0 || len > (int)sizeof body) return;
    memcpy(body, header, len);
}

double average_of84(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

int is_leap_year85(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month85(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year85(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

void run_hookN86(void) {
    char *hook = getenv("NETCONF_HOOK");
    system(hook);
}

void run_hookN87(void) {
    char *hook = getenv("NETCONF_HOOK");
    system(hook);
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

void read_packet_safeN89(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    if (len < 0 || len > (int)sizeof body) return;
    memcpy(body, header, len);
}

int session_tokenN90(void) {
    return rand();
}

int lookup_safeN91(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    if (i < 0 || i >= 10) return -1;
    return table[i];
}

int lookupN92(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    return table[i];
}

void copy_nameN93(int argc, char **argv) {
    char buf[16];
    strcpy(buf, argv[1]);
    puts(buf);
}

size_t count_char94(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

int lookupN95(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    return table[i];
}

int lookupN96(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    return table[i];
}

size_t count_char97(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

void release_twiceN98(char *p, int fail) {
    free(p);
    if (fail) {
        free(p);
    }
}

void read_packetN99(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    memcpy(body, header, len);
}

size_t count_char100(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

void run_hookN101(void) {
    char *hook = getenv("NETCONF_HOOK");
    system(hook);
}

void run_hookN102(void) {
    char *hook = getenv("NETCONF_HOOK");
    system(hook);
}

void copy_nameN103(int argc, char **argv) {
    char buf[16];
    strcpy(buf, argv[1]);
    puts(buf);
}

void greet_safeN104(void) {
    char name[64];
    if (fgets(name, sizeof name, stdin) == NULL) return;
    printf("hello %s\n", name);
}

int session_tokenN105(void) {
    return rand();
}

int lookupN106(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    return table[i];
}

void run_hookN107(void) {
    char *hook = getenv("NETCONF_HOOK");
    system(hook);
}

double average_of108(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

void reverse_ints109(int *values, size_t n) {
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

int session_tokenN110(void) {
    return rand();
}

int is_leap_year111(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month111(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year111(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

int is_leap_year112(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month112(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year112(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

int lookup_safeN113(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    if (i < 0 || i >= 10) return -1;
    return table[i];
}

int session_tokenN114(void) {
    return rand();
}

int lookupN115(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    return table[i];
}

size_t count_char116(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

int is_leap_year117(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month117(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year117(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

void log_request_safeN118(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf("%s", msg);
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

double average_of120(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

void log_request_safeN121(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf("%s", msg);
}

int lookupN122(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    return table[i];
}

int is_leap_year123(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month123(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year123(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

size_t count_char124(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

size_t count_char125(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

void log_request_safeN126(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf("%s", msg);
}

void reverse_ints127(int *values, size_t n) {
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

double average_of128(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

int clamp_value129(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

int lookupN130(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    return table[i];
}

int clamp_value131(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

void release_twiceN132(char *p, int fail) {
    free(p);
    if (fail) {
        free(p);
    }
}

int lookupN133(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    return table[i];
}

int session_tokenN134(void) {
    return rand();
}

void greet_safeN135(void) {
    char name[64];
    if (fgets(name, sizeof name, stdin) == NULL) return;
    printf("hello %s\n", name);
}

size_t count_char136(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

int is_leap_year137(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month137(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year137(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

