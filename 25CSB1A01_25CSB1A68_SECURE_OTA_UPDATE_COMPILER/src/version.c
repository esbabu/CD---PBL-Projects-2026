#include "version.h"
#include <stddef.h>

#define NVRAM_MAGIC 0x46575652 // 'FWVR' (Firmware Version Record)

typedef struct {
    uint32_t magic;
    uint32_t monotonic_version;
    uint32_t write_count;
    uint32_t checksum;
} NvramRecord;

// Simulated persistent non-volatile flash / EEPROM storage
static NvramRecord s_nvram_flash = {
    .magic = NVRAM_MAGIC,
    .monotonic_version = 0,
    .write_count = 0,
    .checksum = 0
};

// Global for runtime tracking and LLVM pass integration
int current_version = 0;

int compare_semver(SemVer a, SemVer b) {
    uint32_t u_a = semver_to_u32(a);
    uint32_t u_b = semver_to_u32(b);
    if (u_a > u_b) return 1;
    if (u_a < u_b) return -1;
    return 0;
}

int parse_semver(const char *s, SemVer *out) {
    if (!s || !out) {
        return -1;
    }
    if (*s == 'v' || *s == 'V') {
        s++;
    }

    uint32_t maj = 0;
    if (*s < '0' || *s > '9') return -1;
    while (*s >= '0' && *s <= '9') {
        maj = maj * 10 + (*s++ - '0');
        if (maj > 0xFFFF) return -1;
    }

    if (*s++ != '.') return -1;

    uint32_t min = 0;
    if (*s < '0' || *s > '9') return -1;
    while (*s >= '0' && *s <= '9') {
        min = min * 10 + (*s++ - '0');
        if (min > 0xFF) return -1;
    }

    if (*s++ != '.') return -1;

    uint32_t pat = 0;
    if (*s < '0' || *s > '9') return -1;
    while (*s >= '0' && *s <= '9') {
        pat = pat * 10 + (*s++ - '0');
        if (pat > 0xFF) return -1;
    }

    out->major = (uint16_t)maj;
    out->minor = (uint16_t)min;
    out->patch = (uint16_t)pat;
    return 0;
}

void init_nvram_version_storage(uint32_t initial_version) {
    s_nvram_flash.magic = NVRAM_MAGIC;
    s_nvram_flash.monotonic_version = initial_version;
    s_nvram_flash.write_count = 1;
    s_nvram_flash.checksum = initial_version ^ NVRAM_MAGIC;
    current_version = (int)initial_version;
}

uint32_t get_current_firmware_version(void) {
    if (s_nvram_flash.magic == NVRAM_MAGIC &&
        s_nvram_flash.checksum == (s_nvram_flash.monotonic_version ^ NVRAM_MAGIC)) {
        return s_nvram_flash.monotonic_version;
    }
    return (uint32_t)current_version;
}

int set_current_firmware_version(uint32_t new_version) {
    s_nvram_flash.magic = NVRAM_MAGIC;
    s_nvram_flash.monotonic_version = new_version;
    s_nvram_flash.write_count++;
    s_nvram_flash.checksum = new_version ^ NVRAM_MAGIC;
    current_version = (int)new_version;
    return 0;
}
