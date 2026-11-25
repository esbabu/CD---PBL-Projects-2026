#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <openssl/md5.h>
#include <openssl/ssl.h>

#define NAME_MAX_LEN 32

struct record { int id; char name[NAME_MAX_LEN]; };

int is_leap_year1(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month1(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year1(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

double average_of2(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

void log_requestN3(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf(msg);
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

void log_request_safeN5(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf("%s", msg);
}

void log_requestN6(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf(msg);
}

void copy_name_safeN7(const char *src) {
    char buf[16];
    snprintf(buf, sizeof buf, "%s", src);
    puts(buf);
}

int is_leap_year8(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month8(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year8(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

int lookupN9(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    return table[i];
}

int lookup_safeN10(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    if (i < 0 || i >= 10) return -1;
    return table[i];
}

size_t count_char11(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
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

void write_configN13(const char *path) {
    if (access(path, W_OK) == 0) {
        FILE *f = fopen(path, "w");
        fputs("enabled=1\n", f);
        fclose(f);
    }
}

int lookupN14(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    return table[i];
}

size_t count_char15(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
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

int is_leap_year17(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month17(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year17(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
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

char *make_bufferN19(size_t n) {
    char *p = malloc(n);
    p[0] = '\0';
    return p;
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

int is_leap_year21(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month21(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year21(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

int is_leap_year22(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month22(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year22(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

void log_requestN23(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf(msg);
}

int session_tokenN24(void) {
    return rand();
}

double average_of25(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
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

int clamp_value27(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

int clamp_value28(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

void reverse_ints29(int *values, size_t n) {
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

int clamp_value30(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

size_t count_char31(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

void read_packetN32(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    memcpy(body, header, len);
}

char *make_bufferN33(size_t n) {
    char *p = malloc(n);
    p[0] = '\0';
    return p;
}

void reverse_ints34(int *values, size_t n) {
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

void run_hookN37(void) {
    char *hook = getenv("NETCONF_HOOK");
    system(hook);
}

void copy_nameN38(int argc, char **argv) {
    char buf[16];
    strcpy(buf, argv[1]);
    puts(buf);
}

int is_leap_year39(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month39(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year39(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

double average_of40(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
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

void copy_nameN42(int argc, char **argv) {
    char buf[16];
    strcpy(buf, argv[1]);
    puts(buf);
}

char *make_buffer_safeN43(size_t n) {
    char *p = malloc(n);
    if (p == NULL) return NULL;
    p[0] = '\0';
    return p;
}

void read_packetN44(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    memcpy(body, header, len);
}

void copy_name_safeN45(const char *src) {
    char buf[16];
    snprintf(buf, sizeof buf, "%s", src);
    puts(buf);
}

void log_requestN46(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf(msg);
}

int clamp_value47(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

void copy_name_safeN48(const char *src) {
    char buf[16];
    snprintf(buf, sizeof buf, "%s", src);
    puts(buf);
}

void reverse_ints49(int *values, size_t n) {
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

int clamp_value50(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
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

char *make_buffer_safeN52(size_t n) {
    char *p = malloc(n);
    if (p == NULL) return NULL;
    p[0] = '\0';
    return p;
}

int clamp_value53(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
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

void reverse_ints55(int *values, size_t n) {
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

double average_of56(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

int clamp_value57(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

size_t count_char58(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

int is_leap_year59(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month59(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year59(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

void release_twiceN60(char *p, int fail) {
    free(p);
    if (fail) {
        free(p);
    }
}

void greet_safeN61(void) {
    char name[64];
    if (fgets(name, sizeof name, stdin) == NULL) return;
    printf("hello %s\n", name);
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

void greetN63(void) {
    char name[64];
    gets(name);
    printf("hello %s\n", name);
}

void run_hookN64(void) {
    char *hook = getenv("NETCONF_HOOK");
    system(hook);
}

int is_leap_year65(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month65(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year65(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

void copy_name_safeN66(const char *src) {
    char buf[16];
    snprintf(buf, sizeof buf, "%s", src);
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

void log_request_safeN68(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf("%s", msg);
}

void release_twiceN69(char *p, int fail) {
    free(p);
    if (fail) {
        free(p);
    }
}

void copy_nameN70(int argc, char **argv) {
    char buf[16];
    strcpy(buf, argv[1]);
    puts(buf);
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

double average_of72(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

void run_hookN73(void) {
    char *hook = getenv("NETCONF_HOOK");
    system(hook);
}

void log_request_safeN74(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf("%s", msg);
}

char *make_buffer_safeN75(size_t n) {
    char *p = malloc(n);
    if (p == NULL) return NULL;
    p[0] = '\0';
    return p;
}

int lookupN76(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    return table[i];
}

size_t count_char77(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

void reverse_ints78(int *values, size_t n) {
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

int session_tokenN79(void) {
    return rand();
}

void copy_name_safeN80(const char *src) {
    char buf[16];
    snprintf(buf, sizeof buf, "%s", src);
    puts(buf);
}

size_t count_char81(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

void greetN82(void) {
    char name[64];
    gets(name);
    printf("hello %s\n", name);
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

char *make_bufferN85(size_t n) {
    char *p = malloc(n);
    p[0] = '\0';
    return p;
}

void read_packetN86(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    memcpy(body, header, len);
}

int lookupN87(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    return table[i];
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

int lookupN89(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    return table[i];
}

size_t count_char90(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
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

double average_of92(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

double average_of93(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
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

void greet_safeN95(void) {
    char name[64];
    if (fgets(name, sizeof name, stdin) == NULL) return;
    printf("hello %s\n", name);
}

size_t count_char96(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
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

double average_of98(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

void reverse_ints99(int *values, size_t n) {
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

int lookup_safeN100(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    if (i < 0 || i >= 10) return -1;
    return table[i];
}

void copy_nameN101(int argc, char **argv) {
    char buf[16];
    strcpy(buf, argv[1]);
    puts(buf);
}

void run_hookN102(void) {
    char *hook = getenv("NETCONF_HOOK");
    system(hook);
}

void run_hookN103(void) {
    char *hook = getenv("NETCONF_HOOK");
    system(hook);
}

int session_tokenN104(void) {
    return rand();
}

char *make_buffer_safeN105(size_t n) {
    char *p = malloc(n);
    if (p == NULL) return NULL;
    p[0] = '\0';
    return p;
}

void read_packetN106(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    memcpy(body, header, len);
}

void greetN107(void) {
    char name[64];
    gets(name);
    printf("hello %s\n", name);
}

void read_packetN108(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    memcpy(body, header, len);
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

double average_of110(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

void read_packetN111(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    memcpy(body, header, len);
}

void run_hookN112(void) {
    char *hook = getenv("NETCONF_HOOK");
    system(hook);
}

int session_tokenN113(void) {
    return rand();
}

size_t count_char114(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

void copy_name_safeN115(const char *src) {
    char buf[16];
    snprintf(buf, sizeof buf, "%s", src);
    puts(buf);
}

void log_requestN116(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf(msg);
}

double average_of117(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

char *make_bufferN118(size_t n) {
    char *p = malloc(n);
    p[0] = '\0';
    return p;
}

void log_request_safeN119(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf("%s", msg);
}

void reverse_ints120(int *values, size_t n) {
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

void read_packet_safeN121(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    if (len < 0 || len > (int)sizeof body) return;
    memcpy(body, header, len);
}

size_t count_char122(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

int clamp_value123(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

void log_requestN124(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf(msg);
}

char *make_buffer_safeN125(size_t n) {
    char *p = malloc(n);
    if (p == NULL) return NULL;
    p[0] = '\0';
    return p;
}

void log_request_safeN126(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf("%s", msg);
}

void greet_safeN127(void) {
    char name[64];
    if (fgets(name, sizeof name, stdin) == NULL) return;
    printf("hello %s\n", name);
}

void release_twiceN128(char *p, int fail) {
    free(p);
    if (fail) {
        free(p);
    }
}

void run_hookN129(void) {
    char *hook = getenv("NETCONF_HOOK");
    system(hook);
}

void copy_name_safeN130(const char *src) {
    char buf[16];
    snprintf(buf, sizeof buf, "%s", src);
    puts(buf);
}

int lookupN131(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    return table[i];
}

double average_of132(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

int clamp_value133(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

void reverse_ints134(int *values, size_t n) {
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

double average_of135(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

void release_twiceN136(char *p, int fail) {
    free(p);
    if (fail) {
        free(p);
    }
}

void log_requestN137(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf(msg);
}

void reverse_ints138(int *values, size_t n) {
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

int clamp_value139(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

void copy_name_safeN140(const char *src) {
    char buf[16];
    snprintf(buf, sizeof buf, "%s", src);
    puts(buf);
}

void write_configN141(const char *path) {
    if (access(path, W_OK) == 0) {
        FILE *f = fopen(path, "w");
        fputs("enabled=1\n", f);
        fclose(f);
    }
}

void reverse_ints142(int *values, size_t n) {
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

void log_requestN143(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf(msg);
}

double average_of144(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

void reverse_ints145(int *values, size_t n) {
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

void reverse_ints146(int *values, size_t n) {
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

void log_request_safeN147(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf("%s", msg);
}

void reverse_ints148(int *values, size_t n) {
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

int session_tokenN149(void) {
    return rand();
}

void reverse_ints150(int *values, size_t n) {
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

void log_request_safeN151(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf("%s", msg);
}

void reverse_ints152(int *values, size_t n) {
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

int is_leap_year153(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month153(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year153(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

double average_of154(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

int is_leap_year155(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month155(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year155(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

double average_of156(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

int lookup_safeN157(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    if (i < 0 || i >= 10) return -1;
    return table[i];
}

void greet_safeN158(void) {
    char name[64];
    if (fgets(name, sizeof name, stdin) == NULL) return;
    printf("hello %s\n", name);
}

int lookup_safeN159(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    if (i < 0 || i >= 10) return -1;
    return table[i];
}

void read_packet_safeN160(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    if (len < 0 || len > (int)sizeof body) return;
    memcpy(body, header, len);
}

void reverse_ints161(int *values, size_t n) {
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

