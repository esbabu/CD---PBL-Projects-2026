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

int clamp_value2(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

void reverse_ints3(int *values, size_t n) {
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

double average_of4(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

size_t count_char5(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

void releaseN6(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
}

void releaseN7(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
}

void releaseN8(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
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

int is_leap_year10(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month10(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year10(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

void reverse_ints11(int *values, size_t n) {
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

void releaseN12(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
}

void releaseN13(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
}

int is_leap_year14(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month14(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year14(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

void releaseN15(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
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

size_t count_char18(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

void release_safeN19(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

struct record *load_recordsN20(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

int clamp_value21(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

void release_safeN22(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

int is_leap_year23(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month23(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year23(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

struct record *load_recordsN24(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

void reverse_ints25(int *values, size_t n) {
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

void release_safeN26(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

struct record *load_recordsN27(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
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

double average_of30(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
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

double average_of32(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

void release_safeN33(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
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

void release_safeN35(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

void releaseN36(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
}

void release_safeN37(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

void reverse_ints38(int *values, size_t n) {
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

int clamp_value39(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
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

void release_safeN41(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

struct record *load_recordsN42(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

void release_safeN43(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

struct record *load_recordsN44(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

void releaseN45(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
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

void releaseN47(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
}

size_t count_char48(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
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

struct record *load_recordsN51(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
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

void reverse_ints53(int *values, size_t n) {
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

void releaseN54(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
}

void releaseN55(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
}

struct record *load_recordsN56(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

struct record *load_recordsN57(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

void release_safeN58(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

size_t count_char59(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

void release_safeN60(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

void reverse_ints61(int *values, size_t n) {
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

void reverse_ints62(int *values, size_t n) {
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

void release_safeN63(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
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

void release_safeN65(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

void releaseN66(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
}

void reverse_ints67(int *values, size_t n) {
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

void release_safeN68(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

void reverse_ints69(int *values, size_t n) {
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

void releaseN70(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
}

void releaseN71(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
}

struct record *load_recordsN72(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

void release_safeN73(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

void releaseN74(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
}

int clamp_value75(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

struct record *load_recordsN76(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

int clamp_value77(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

void release_safeN78(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

double average_of79(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

struct record *load_recordsN80(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

void reverse_ints81(int *values, size_t n) {
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

int clamp_value82(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

void release_safeN83(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

void release_safeN84(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

void release_safeN85(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

void releaseN86(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
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

double average_of88(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
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

struct record *load_recordsN90(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

void releaseN91(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
}

void release_safeN92(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

void reverse_ints93(int *values, size_t n) {
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

void releaseN94(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
}

size_t count_char95(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

void release_safeN96(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
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

void releaseN100(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
}

struct record *load_recordsN101(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

int is_leap_year102(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month102(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year102(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

int is_leap_year103(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month103(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year103(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

struct record *load_recordsN104(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
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

void release_safeN106(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

int is_leap_year107(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month107(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year107(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

void releaseN108(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
}

int is_leap_year109(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month109(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year109(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
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

void release_safeN112(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

int clamp_value113(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

void reverse_ints114(int *values, size_t n) {
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

struct record *load_recordsN115(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

struct record *load_recordsN116(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
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

double average_of118(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

struct record *load_recordsN119(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

size_t count_char120(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

void releaseN121(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
}

void release_safeN122(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

double average_of123(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

void releaseN124(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
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

void releaseN126(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
}

void releaseN127(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
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

void releaseN130(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
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

struct record *load_recordsN132(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

struct record *load_recordsN133(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

void release_safeN134(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

void releaseN135(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
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

struct record *load_recordsN137(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

struct record *load_recordsN138(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

struct record *load_recordsN139(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

void release_safeN140(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

struct record *load_recordsN141(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

int is_leap_year142(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month142(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year142(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

void reverse_ints143(int *values, size_t n) {
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

struct record *load_recordsN144(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

void releaseN145(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
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

void reverse_ints147(int *values, size_t n) {
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

int is_leap_year149(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month149(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year149(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

size_t count_char150(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

void reverse_ints151(int *values, size_t n) {
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

