/* OptAgent Native Harness Common Runtime (C11 & C++17 compatible)
 *
 * Provides:
 *  - Fork-per-case isolation (resets global state & survives crashes/timeouts)
 *  - RLIMIT_AS / RLIMIT_CPU / RLIMIT_STACK + setitimer deadline enforcement
 *  - Stdout capture via pipe
 *  - Canary red-zone buffer allocation & OOB write detection (even without ASan)
 *  - High-resolution monotonic timing (clock_gettime) & peak RSS (getrusage)
 *  - Benchmark DoNotOptimize barrier (defeats dead-code elimination)
 *  - SanCov 8-bit inline counter collection
 */
#ifndef OPTAGENT_HARNESS_COMMON_H
#define OPTAGENT_HARNESS_COMMON_H

#ifndef _POSIX_C_SOURCE
#define _POSIX_C_SOURCE 200809L
#endif

#include <errno.h>
#include <math.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#if !defined(_WIN32)
#include <fcntl.h>
#include <sys/resource.h>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#endif

#define OPTAGENT_CANARY_SIZE 64
#define OPTAGENT_CANARY_BYTE 0xCD

/* Compiler barrier to prevent dead-code elimination during benchmarking */
#if defined(__GNUC__) || defined(__clang__)
#define OPTAGENT_DO_NOT_OPTIMIZE(val) __asm__ volatile("" : : "g"(val) : "memory")
#else
#define OPTAGENT_DO_NOT_OPTIMIZE(val) ((void)(val))
#endif

/* ---------- Canary red-zone buffer ---------- */
typedef struct {
    void *raw;
    void *user_ptr;
    size_t user_bytes;
} OptCanaryBuf;

static inline OptCanaryBuf optagent_canary_alloc(size_t user_bytes) {
    OptCanaryBuf b;
    size_t total = user_bytes + 2 * OPTAGENT_CANARY_SIZE;
    if (total < 2 * OPTAGENT_CANARY_SIZE + 1) total = 2 * OPTAGENT_CANARY_SIZE + 1;
    unsigned char *raw = (unsigned char *)malloc(total);
    b.raw = raw;
    b.user_bytes = user_bytes;
    if (!raw) {
        b.user_ptr = NULL;
        return b;
    }
    memset(raw, OPTAGENT_CANARY_BYTE, OPTAGENT_CANARY_SIZE);
    memset(raw + OPTAGENT_CANARY_SIZE, 0, user_bytes);
    memset(raw + OPTAGENT_CANARY_SIZE + user_bytes, OPTAGENT_CANARY_BYTE, OPTAGENT_CANARY_SIZE);
    b.user_ptr = raw + OPTAGENT_CANARY_SIZE;
    return b;
}

/* Returns 0 if clean, 1 if leading canary corrupted, 2 if trailing canary corrupted */
static inline int optagent_canary_check(const OptCanaryBuf *b) {
    if (!b || !b->raw) return 0;
    const unsigned char *raw = (const unsigned char *)b->raw;
    for (size_t i = 0; i < OPTAGENT_CANARY_SIZE; i++) {
        if (raw[i] != OPTAGENT_CANARY_BYTE) return 1;
    }
    const unsigned char *tail = raw + OPTAGENT_CANARY_SIZE + b->user_bytes;
    for (size_t i = 0; i < OPTAGENT_CANARY_SIZE; i++) {
        if (tail[i] != OPTAGENT_CANARY_BYTE) return 2;
    }
    return 0;
}

static inline void optagent_canary_free(OptCanaryBuf *b) {
    if (b && b->raw) {
        free(b->raw);
        b->raw = NULL;
        b->user_ptr = NULL;
    }
}

/* ---------- High-resolution timer ---------- */
static inline double optagent_now_s(void) {
#if defined(CLOCK_MONOTONIC) && !defined(_WIN32)
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec * 1e-9;
#else
    return (double)clock() / (double)CLOCKS_PER_SEC;
#endif
}

/* ---------- Signal name lookup ---------- */
static inline const char *optagent_signal_name(int sig) {
    switch (sig) {
        case SIGSEGV: return "SIGSEGV";
        case SIGABRT: return "SIGABRT";
        case SIGFPE:  return "SIGFPE";
        case SIGILL:  return "SIGILL";
#ifdef SIGBUS
        case SIGBUS:  return "SIGBUS";
#endif
#ifdef SIGALRM
        case SIGALRM: return "SIGALRM";
#endif
#ifdef SIGKILL
        case SIGKILL: return "SIGKILL";
#endif
#ifdef SIGXCPU
        case SIGXCPU: return "SIGXCPU";
#endif
        default:      return "SIGUNKNOWN";
    }
}

/* ---------- SanCov 8-bit inline counters (weak hooks) ---------- */
static uint8_t *g_optagent_sancov_start = NULL;
static uint8_t *g_optagent_sancov_stop = NULL;

#ifdef __cplusplus
extern "C" {
#endif
void __sanitizer_cov_8bit_counters_init(uint8_t *start, uint8_t *stop) {
    g_optagent_sancov_start = start;
    g_optagent_sancov_stop = stop;
}
#ifdef __cplusplus
}
#endif

static inline void optagent_sancov_reset(void) {
    if (g_optagent_sancov_start && g_optagent_sancov_stop && g_optagent_sancov_stop > g_optagent_sancov_start) {
        memset(g_optagent_sancov_start, 0, (size_t)(g_optagent_sancov_stop - g_optagent_sancov_start));
    }
}

/* ---------- JSON string escaping helper ---------- */
static inline void optagent_fprint_json_str(FILE *fp, const char *s) {
    fputc('"', fp);
    if (s) {
        for (const unsigned char *p = (const unsigned char *)s; *p; p++) {
            unsigned char c = *p;
            if (c == '"') fputs("\\\"", fp);
            else if (c == '\\') fputs("\\\\", fp);
            else if (c == '\b') fputs("\\b", fp);
            else if (c == '\f') fputs("\\f", fp);
            else if (c == '\n') fputs("\\n", fp);
            else if (c == '\r') fputs("\\r", fp);
            else if (c == '\t') fputs("\\t", fp);
            else if (c < 0x20) fprintf(fp, "\\u%04x", c);
            else fputc((int)c, fp);
        }
    }
    fputc('"', fp);
}

static inline void optagent_fprint_double(FILE *fp, double v) {
    if (isnan(v)) fputs("{\"__float\":\"nan\"}", fp);
    else if (isinf(v)) fputs(v > 0 ? "{\"__float\":\"inf\"}" : "{\"__float\":\"-inf\"}", fp);
    else if (v == 0.0 && signbit(v)) fputs("{\"__float\":\"-0\"}", fp);
    else fprintf(fp, "%.17g", v);
}

static inline void optagent_fprint_float(FILE *fp, float v) {
    if (isnan(v)) fputs("{\"__float\":\"nan\"}", fp);
    else if (isinf(v)) fputs(v > 0 ? "{\"__float\":\"inf\"}" : "{\"__float\":\"-inf\"}", fp);
    else if (v == 0.0f && signbit(v)) fputs("{\"__float\":\"-0\"}", fp);
    else fprintf(fp, "%.9g", v);
}

#if !defined(_WIN32)
/* Child resource limits & timeout setup */
static inline void optagent_child_setup_limits(double timeout_s, size_t mem_mb) {
    struct rlimit rl;
    if (mem_mb > 0) {
        rl.rlim_cur = rl.rlim_max = (rlim_t)mem_mb * 1024ULL * 1024ULL;
        setrlimit(RLIMIT_AS, &rl);
    }
    rlim_t cpu_lim = (rlim_t)(timeout_s + 2.0);
    if (cpu_lim < 2) cpu_lim = 2;
    rl.rlim_cur = rl.rlim_max = cpu_lim;
    setrlimit(RLIMIT_CPU, &rl);

    rl.rlim_cur = rl.rlim_max = 16ULL * 1024ULL * 1024ULL; /* 16 MB stack */
    setrlimit(RLIMIT_STACK, &rl);

    struct itimerval it;
    memset(&it, 0, sizeof(it));
    long sec = (long)timeout_s;
    long usec = (long)((timeout_s - (double)sec) * 1e6);
    if (sec == 0 && usec < 50000) usec = 50000;
    it.it_value.tv_sec = sec;
    it.it_value.tv_usec = usec;
    setitimer(ITIMER_REAL, &it, NULL);
}

static inline long optagent_peak_rss_kb(void) {
    struct rusage ru;
    if (getrusage(RUSAGE_SELF, &ru) == 0) return ru.ru_maxrss;
    return 0;
}
#endif

#endif /* OPTAGENT_HARNESS_COMMON_H */
