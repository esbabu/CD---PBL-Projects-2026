#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <openssl/md5.h>
#include <openssl/ssl.h>

#define NAME_MAX_LEN 32

struct record { int id; char name[NAME_MAX_LEN]; };

void reverse_ints1(int *values, size_t n) {
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

void read_packetN2(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    memcpy(body, header, len);
}

void greet_safeN3(void) {
    char name[64];
    if (fgets(name, sizeof name, stdin) == NULL) return;
    printf("hello %s\n", name);
}

void copy_nameN4(int argc, char **argv) {
    char buf[16];
    strcpy(buf, argv[1]);
    puts(buf);
}

double average_of5(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

int session_tokenN6(void) {
    return rand();
}

int session_tokenN7(void) {
    return rand();
}

int lookupN8(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    return table[i];
}

char *make_bufferN9(size_t n) {
    char *p = malloc(n);
    p[0] = '\0';
    return p;
}

int lookupN10(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    return table[i];
}

void log_requestN11(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf(msg);
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

int is_leap_year13(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month13(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year13(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

void write_configN14(const char *path) {
    if (access(path, W_OK) == 0) {
        FILE *f = fopen(path, "w");
        fputs("enabled=1\n", f);
        fclose(f);
    }
}

void copy_name_safeN15(const char *src) {
    char buf[16];
    snprintf(buf, sizeof buf, "%s", src);
    puts(buf);
}

int clamp_value16(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

void read_packetN17(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    memcpy(body, header, len);
}

int session_tokenN18(void) {
    return rand();
}

void copy_name_safeN19(const char *src) {
    char buf[16];
    snprintf(buf, sizeof buf, "%s", src);
    puts(buf);
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

void read_packetN21(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    memcpy(body, header, len);
}

void read_packet_safeN22(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    if (len < 0 || len > (int)sizeof body) return;
    memcpy(body, header, len);
}

int session_tokenN23(void) {
    return rand();
}

int clamp_value24(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
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

void write_configN26(const char *path) {
    if (access(path, W_OK) == 0) {
        FILE *f = fopen(path, "w");
        fputs("enabled=1\n", f);
        fclose(f);
    }
}

void copy_nameN27(int argc, char **argv) {
    char buf[16];
    strcpy(buf, argv[1]);
    puts(buf);
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

void copy_nameN29(int argc, char **argv) {
    char buf[16];
    strcpy(buf, argv[1]);
    puts(buf);
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

int is_leap_year31(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month31(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year31(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

size_t count_char32(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

int lookupN33(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    return table[i];
}

int lookupN34(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    return table[i];
}

int lookup_safeN35(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    if (i < 0 || i >= 10) return -1;
    return table[i];
}

void greet_safeN36(void) {
    char name[64];
    if (fgets(name, sizeof name, stdin) == NULL) return;
    printf("hello %s\n", name);
}

void read_packetN37(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    memcpy(body, header, len);
}

int lookupN38(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    return table[i];
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

int is_leap_year41(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month41(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year41(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

int is_leap_year42(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month42(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year42(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

void log_requestN43(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf(msg);
}

void log_requestN44(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf(msg);
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

int clamp_value46(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
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

void greetN49(void) {
    char name[64];
    gets(name);
    printf("hello %s\n", name);
}

size_t count_char50(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

int session_tokenN51(void) {
    return rand();
}

void log_requestN52(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf(msg);
}

size_t count_char53(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

void greet_safeN54(void) {
    char name[64];
    if (fgets(name, sizeof name, stdin) == NULL) return;
    printf("hello %s\n", name);
}

int lookupN55(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    return table[i];
}

void reverse_ints56(int *values, size_t n) {
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

void greet_safeN59(void) {
    char name[64];
    if (fgets(name, sizeof name, stdin) == NULL) return;
    printf("hello %s\n", name);
}

void copy_name_safeN60(const char *src) {
    char buf[16];
    snprintf(buf, sizeof buf, "%s", src);
    puts(buf);
}

int lookupN61(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    return table[i];
}

void read_packet_safeN62(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    if (len < 0 || len > (int)sizeof body) return;
    memcpy(body, header, len);
}

size_t count_char63(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

void greetN64(void) {
    char name[64];
    gets(name);
    printf("hello %s\n", name);
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

void greet_safeN66(void) {
    char name[64];
    if (fgets(name, sizeof name, stdin) == NULL) return;
    printf("hello %s\n", name);
}

void greet_safeN67(void) {
    char name[64];
    if (fgets(name, sizeof name, stdin) == NULL) return;
    printf("hello %s\n", name);
}

void run_hookN68(void) {
    char *hook = getenv("NETCONF_HOOK");
    system(hook);
}

size_t count_char69(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

void reverse_ints70(int *values, size_t n) {
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

int clamp_value71(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

size_t count_char72(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

void reverse_ints73(int *values, size_t n) {
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

void copy_nameN74(int argc, char **argv) {
    char buf[16];
    strcpy(buf, argv[1]);
    puts(buf);
}

void greetN75(void) {
    char name[64];
    gets(name);
    printf("hello %s\n", name);
}

void reverse_ints76(int *values, size_t n) {
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

size_t count_char78(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
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

void log_requestN80(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf(msg);
}

int lookup_safeN81(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    if (i < 0 || i >= 10) return -1;
    return table[i];
}

size_t count_char82(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

double average_of83(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
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

int session_tokenN85(void) {
    return rand();
}

int clamp_value86(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

void greetN87(void) {
    char name[64];
    gets(name);
    printf("hello %s\n", name);
}

void log_request_safeN88(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf("%s", msg);
}

void read_packet_safeN89(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    if (len < 0 || len > (int)sizeof body) return;
    memcpy(body, header, len);
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

void log_request_safeN92(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf("%s", msg);
}

int is_leap_year93(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month93(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year93(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

void read_packet_safeN94(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    if (len < 0 || len > (int)sizeof body) return;
    memcpy(body, header, len);
}

int clamp_value95(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
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

void reverse_ints97(int *values, size_t n) {
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

int clamp_value98(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

void greet_safeN99(void) {
    char name[64];
    if (fgets(name, sizeof name, stdin) == NULL) return;
    printf("hello %s\n", name);
}

void log_request_safeN100(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf("%s", msg);
}

void copy_name_safeN101(const char *src) {
    char buf[16];
    snprintf(buf, sizeof buf, "%s", src);
    puts(buf);
}

size_t count_char102(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

void copy_nameN103(int argc, char **argv) {
    char buf[16];
    strcpy(buf, argv[1]);
    puts(buf);
}

void read_packetN104(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    memcpy(body, header, len);
}

size_t count_char105(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

void log_requestN106(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf(msg);
}

void greet_safeN107(void) {
    char name[64];
    if (fgets(name, sizeof name, stdin) == NULL) return;
    printf("hello %s\n", name);
}

void copy_name_safeN108(const char *src) {
    char buf[16];
    snprintf(buf, sizeof buf, "%s", src);
    puts(buf);
}

void greet_safeN109(void) {
    char name[64];
    if (fgets(name, sizeof name, stdin) == NULL) return;
    printf("hello %s\n", name);
}

void reverse_ints110(int *values, size_t n) {
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

void greet_safeN111(void) {
    char name[64];
    if (fgets(name, sizeof name, stdin) == NULL) return;
    printf("hello %s\n", name);
}

void log_request_safeN112(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf("%s", msg);
}

void greet_safeN113(void) {
    char name[64];
    if (fgets(name, sizeof name, stdin) == NULL) return;
    printf("hello %s\n", name);
}

void log_requestN114(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf(msg);
}

void release_twiceN115(char *p, int fail) {
    free(p);
    if (fail) {
        free(p);
    }
}

void greet_safeN116(void) {
    char name[64];
    if (fgets(name, sizeof name, stdin) == NULL) return;
    printf("hello %s\n", name);
}

void reverse_ints117(int *values, size_t n) {
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

int session_tokenN118(void) {
    return rand();
}

int lookup_safeN119(int sock) {
    int table[10] = {0};
    char idx_text[4];
    recv(sock, idx_text, sizeof idx_text, 0);
    int i = atoi(idx_text);
    if (i < 0 || i >= 10) return -1;
    return table[i];
}

int is_leap_year120(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month120(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year120(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

void copy_nameN121(int argc, char **argv) {
    char buf[16];
    strcpy(buf, argv[1]);
    puts(buf);
}

void read_packetN122(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    memcpy(body, header, len);
}

int session_tokenN123(void) {
    return rand();
}

void log_request_safeN124(int sock) {
    char msg[256];
    recv(sock, msg, sizeof msg - 1, 0);
    printf("%s", msg);
}

void reverse_ints125(int *values, size_t n) {
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

void greetN126(void) {
    char name[64];
    gets(name);
    printf("hello %s\n", name);
}

int clamp_value127(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

int is_leap_year128(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month128(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year128(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

double average_of129(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
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

void reverse_ints131(int *values, size_t n) {
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

int is_leap_year133(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month133(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year133(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

int is_leap_year134(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month134(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year134(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

void reverse_ints135(int *values, size_t n) {
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

void greetN136(void) {
    char name[64];
    gets(name);
    printf("hello %s\n", name);
}

void read_packetN137(int sock) {
    char header[8];
    char body[128];
    recv(sock, header, sizeof header, 0);
    int len = atoi(header);
    memcpy(body, header, len);
}

char *make_bufferN138(size_t n) {
    char *p = malloc(n);
    p[0] = '\0';
    return p;
}

int session_tokenN139(void) {
    return rand();
}

void release_twiceN140(char *p, int fail) {
    free(p);
    if (fail) {
        free(p);
    }
}

