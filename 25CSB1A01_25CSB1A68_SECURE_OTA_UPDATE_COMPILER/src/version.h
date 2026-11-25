#ifndef VERSION_H
#define VERSION_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

// Semantic version representation: major.minor.patch
typedef struct {
    uint16_t major;
    uint16_t minor;
    uint16_t patch;
} SemVer;

// Monotonic 32-bit packed integer:
// Bits 31..16 = Major (up to 65535)
// Bits 15..8  = Minor (up to 255)
// Bits 7..0   = Patch (up to 255)
#define MAKE_SEMVER(maj, min, pat) \
    (((uint32_t)(maj) << 16) | ((uint32_t)(min) << 8) | (uint32_t)(pat))

static inline uint32_t semver_to_u32(SemVer sv) {
    return ((uint32_t)sv.major << 16) | ((uint32_t)sv.minor << 8) | (uint32_t)sv.patch;
}

static inline SemVer u32_to_semver(uint32_t val) {
    SemVer sv;
    sv.major = (uint16_t)((val >> 16) & 0xFFFF);
    sv.minor = (uint16_t)((val >> 8) & 0xFF);
    sv.patch = (uint16_t)(val & 0xFF);
    return sv;
}

int compare_semver(SemVer a, SemVer b);
int parse_semver(const char *str, SemVer *out);

// Simulated persistent NVRAM / EEPROM version store
uint32_t get_current_firmware_version(void);
int set_current_firmware_version(uint32_t new_version);
void init_nvram_version_storage(uint32_t initial_version);

// Global current_version variable for runtime and LLVM pass integration
extern int current_version;

#ifdef __cplusplus
}
#endif

#endif // VERSION_H
