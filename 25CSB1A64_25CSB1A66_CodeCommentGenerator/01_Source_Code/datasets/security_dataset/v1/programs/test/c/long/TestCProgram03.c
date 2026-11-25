#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <openssl/md5.h>
#include <openssl/ssl.h>

#define NAME_MAX_LEN 32

struct record { int id; char name[NAME_MAX_LEN]; };

void release_safeN1(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

void releaseN2(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
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

struct record *load_recordsN5(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

struct record *load_recordsN6(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

void reverse_ints7(int *values, size_t n) {
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

size_t count_char8(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

void release_safeN9(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

void release_safeN10(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

void release_safeN11(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

void reverse_ints12(int *values, size_t n) {
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

void releaseN14(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
}

int clamp_value15(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

void release_safeN16(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

void release_safeN17(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

struct record *load_recordsN18(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
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

void releaseN20(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
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

void release_safeN22(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

struct record *load_recordsN23(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
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

int clamp_value25(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
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

struct record *load_recordsN27(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

void reverse_ints28(int *values, size_t n) {
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

void release_safeN29(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
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

struct record *load_recordsN33(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
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

struct record *load_recordsN35(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

void releaseN36(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
}

struct record *load_recordsN37(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

struct record *load_recordsN38(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
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

void release_safeN40(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
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

size_t count_char42(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
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

struct record *load_recordsN44(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
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

void release_safeN46(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
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

void release_safeN48(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
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

void release_safeN51(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

void release_safeN52(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
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

int clamp_value54(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

void release_safeN55(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

void releaseN56(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
}

double average_of57(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

void releaseN58(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
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

void releaseN61(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
}

void releaseN62(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
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

double average_of66(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

int clamp_value67(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
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

void releaseN70(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
}

void releaseN71(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
}

void release_safeN72(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
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

void release_safeN75(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

void release_safeN76(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

void release_safeN77(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

int is_leap_year78(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month78(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year78(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
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

struct record *load_recordsN82(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

void release_safeN83(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

size_t count_char84(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

void reverse_ints85(int *values, size_t n) {
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

void release_safeN86(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

void releaseN87(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
}

int clamp_value88(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

size_t count_char89(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

void releaseN90(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
}

double average_of91(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

void releaseN92(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
}

void release_safeN93(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
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

void releaseN95(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
}

void releaseN96(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
}

struct record *load_recordsN97(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
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

void release_safeN99(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
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

int is_leap_year101(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month101(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year101(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

struct record *load_recordsN102(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

void releaseN103(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
}

int clamp_value104(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

struct record *load_recordsN105(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

int is_leap_year106(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month106(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year106(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

size_t count_char107(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
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

struct record *load_recordsN109(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

void releaseN110(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
}

size_t count_char111(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
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

struct record *load_recordsN113(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

double average_of114(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

void release_safeN115(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
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

void release_safeN117(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

int is_leap_year118(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month118(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year118(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

void release_safeN119(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
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

int clamp_value121(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
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

struct record *load_recordsN123(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

double average_of124(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
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

int clamp_value126(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

void release_safeN127(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

int clamp_value128(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

void release_safeN129(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

struct record *load_recordsN130(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

size_t count_char131(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

void release_safeN132(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
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

int is_leap_year135(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month135(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year135(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

struct record *load_recordsN136(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

void reverse_ints137(int *values, size_t n) {
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

struct record *load_recordsN138(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

double average_of139(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

int is_leap_year140(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month140(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year140(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

int clamp_value141(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

struct record *load_recordsN142(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

struct record *load_recordsN143(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

struct record *load_recordsN144(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

size_t count_char145(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

struct record *load_recordsN146(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

void release_safeN147(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

struct record *load_recordsN148(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

double average_of149(const int *values, size_t n) {
    if (n == 0) {
        return 0.0;
    }
    long total = 0;
    for (size_t i = 0; i < n; i++) {
        total += values[i];
    }
    return (double)total / (double)n;
}

void release_safeN150(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

int is_leap_year151(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month151(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year151(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
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

void reverse_ints153(int *values, size_t n) {
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

void releaseN154(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
}

int clamp_value155(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

int clamp_value156(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

void releaseN157(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
}

void releaseN158(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
}

int clamp_value159(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

int clamp_value160(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
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

struct record *load_recordsN162(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
}

void releaseN163(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
}

void release_safeN164(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
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

void release_safeN166(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
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

size_t count_char168(const char *text, char c) {
    size_t n = 0;
    while (*text != '\0') {
        if (*text == c) {
            n++;
        }
        text++;
    }
    return n;
}

void reverse_ints169(int *values, size_t n) {
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

struct record *load_recordsN170(int sock) {
    char count_text[8];
    recv(sock, count_text, sizeof count_text, 0);
    size_t count = strtoul(count_text, NULL, 10);
    struct record *r = malloc(count * sizeof(struct record));
    return r;
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

void release_safeN172(struct record *r) {
    int id = r->id;
    free(r);
    r = NULL;
    printf("released %d\n", id);
}

int clamp_value173(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

void releaseN174(struct record *r) {
    free(r);
    printf("released %d\n", r->id);
}

int is_leap_year175(int year) {
    return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
}

int days_in_month175(int year, int month) {
    switch (month) {
    case 2:
        return is_leap_year175(year) ? 29 : 28;
    case 4: case 6: case 9: case 11:
        return 30;
    default:
        return 31;
    }
}

