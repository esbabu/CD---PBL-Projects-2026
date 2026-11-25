#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define URL_MAX 128
#define HASH_LEN 32

#define MAKE_SEMVER(maj, min, pat) \
    (((uint32_t)(maj) << 16) | ((uint32_t)(min) << 8) | (uint32_t)(pat))

#define ERR_VERSION_ROLLBACK_BLOCKED -4

typedef struct {
    uint32_t version;         // Monotonic packed SemVer
    char version_str[16];     // String representation
    char channel[16];
    char source_url[URL_MAX];
    uint8_t image_hash[HASH_LEN];
    uint8_t signature[64];
    uint32_t image_size;
} FirmwarePackage;

typedef struct {
    int active_version;
} DeviceState;

// Persistent non-volatile flash storage simulation
static uint32_t s_nvram_version = MAKE_SEMVER(1, 1, 0); // v1.1.0 installed
int current_version = (int)MAKE_SEMVER(1, 1, 0);

uint32_t get_current_firmware_version(void) {
    return s_nvram_version;
}

int set_current_firmware_version(uint32_t new_version) {
    s_nvram_version = new_version;
    current_version = (int)new_version;
    return 0;
}

int verifySignature(FirmwarePackage *pkg) {
    (void)pkg;
    return 1;
}

int sourceTrusted(FirmwarePackage *pkg) {
    return strncmp(pkg->source_url, "https://github.com/", strlen("https://github.com/")) == 0;
}

int verifyImageHash(FirmwarePackage *pkg) {
    (void)pkg;
    return 1;
}

void install(FirmwarePackage *pkg) {
    (void)pkg;
}

int updateFirmware(DeviceState *dev, FirmwarePackage *pkg) {
    if (!verifySignature(pkg)) {
        return -1;
    }

    if (!sourceTrusted(pkg)) {
        return -2;
    }

    if (!verifyImageHash(pkg)) {
        return -3;
    }

    // Monotonic Rollback Guard: incoming (v1.2.0) must be strictly greater than current (v1.1.0)
    int incoming_version = (int)pkg->version;
    if (incoming_version <= current_version) {
        // Reject installation to prevent rollback attack
        return ERR_VERSION_ROLLBACK_BLOCKED;
    }

    install(pkg);
    set_current_firmware_version((uint32_t)incoming_version);
    if (dev) {
        dev->active_version = incoming_version;
    }
    return 0;
}

int main(void) {
    DeviceState dev = { .active_version = (int)MAKE_SEMVER(1, 1, 0) };

    // Upgrade test payload: incoming_version (v1.2.0) > current_version (v1.1.0)
    FirmwarePackage pkg = {
        .version = MAKE_SEMVER(1, 2, 0),
        .version_str = "1.2.0",
        .channel = "stable",
        .source_url = "https://github.com/firmware/v1.2.0.bin",
        .image_size = 512
    };

    return updateFirmware(&dev, &pkg);
}
