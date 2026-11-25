#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define URL_MAX 128
#define HASH_LEN 32

typedef struct {
    int version;
    char channel[16];
    char source_url[URL_MAX];
    uint8_t image_hash[HASH_LEN];
} FirmwarePackage;

int current_version = 10;

#ifndef __STDC_LIB_EXT1__
static int strncpy_s(char *dest, size_t destsz, const char *src, size_t count) {
    if (!dest || !src || destsz == 0) {
        return -1;
    }
    size_t i = 0;
    while (i < count && i + 1 < destsz && src[i] != '\0') {
        dest[i] = src[i];
        i++;
    }
    dest[i] = '\0';
    return 0;
}
#endif

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

static void sanitizePackage(FirmwarePackage *pkg) {
    char channel_copy[16];
    char log_buf[64];
    uint8_t hash_copy[HASH_LEN];

    // Safe and bounded memory operations
    strncpy_s(channel_copy, sizeof(channel_copy), pkg->channel, sizeof(channel_copy) - 1);
    snprintf(log_buf, sizeof(log_buf), "v=%d", pkg->version);
    memcpy(hash_copy, pkg->image_hash, sizeof(hash_copy));
}

int updateFirmware(FirmwarePackage *pkg) {
    sanitizePackage(pkg);

    if (!verifySignature(pkg)) {
        return -1;
    }

    if (!sourceTrusted(pkg)) {
        return -2;
    }

    if (pkg->version <= current_version) {
        return -3;
    }

    if (!verifyImageHash(pkg)) {
        return -4;
    }

    install(pkg);
    return 0;
}

int main(void) {
    FirmwarePackage pkg = {
        .version = 11,
        .channel = "prod",
        .source_url = "https://github.com/trusted/firmware.bin",
        .image_hash = {0}
    };
    return updateFirmware(&pkg);
}
