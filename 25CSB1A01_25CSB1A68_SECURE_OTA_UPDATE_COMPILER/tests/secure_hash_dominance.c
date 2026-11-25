#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define URL_MAX 128
#define HASH_LEN 32

typedef struct {
    int version;
    char source_url[URL_MAX];
    uint8_t image_hash[HASH_LEN];
    uint32_t image_size;
} FirmwarePackage;

typedef struct {
    int active_version;
} DeviceState;

int current_version = 5;

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

    if (pkg->version <= current_version) {
        return -3;
    }

    // Secure: verifyImageHash strictly dominates install on the success branch
    if (!verifyImageHash(pkg)) {
        return -4;
    }

    install(pkg);
    dev->active_version = pkg->version;
    return 0;
}

int main(void) {
    DeviceState dev = { .active_version = 5 };
    FirmwarePackage pkg = {
        .version = 6,
        .source_url = "https://github.com/firmware/v6.bin",
        .image_size = 512
    };
    return updateFirmware(&dev, &pkg);
}
