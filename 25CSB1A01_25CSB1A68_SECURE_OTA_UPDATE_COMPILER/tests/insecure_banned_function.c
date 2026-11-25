#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define URL_MAX 128

typedef struct {
    int version;
    char channel[16];
    char source_url[URL_MAX];
} FirmwarePackage;

int current_version = 10;

int verifySignature(FirmwarePackage *pkg) {
    (void)pkg;
    return 1;
}

int sourceTrusted(FirmwarePackage *pkg) {
    return strncmp(pkg->source_url, "https://github.com/", strlen("https://github.com/")) == 0;
}

int decryptPayloadAesGcm(FirmwarePackage *pkg) {
    (void)pkg;
    return 1;
}

void install(FirmwarePackage *pkg) {
    (void)pkg;
}

int updateFirmware(FirmwarePackage *pkg) {
    char url_buf[64];

    if (!verifySignature(pkg)) {
        return -1;
    }

    if (!sourceTrusted(pkg)) {
        return -2;
    }

    if (pkg->version <= current_version) {
        return -3;
    }

    if (!decryptPayloadAesGcm(pkg)) {
        return -4;
    }

    strcpy(url_buf, pkg->source_url);

    install(pkg);
    return 0;
}

int main(void) {
    FirmwarePackage pkg = {
        .version = 11,
        .source_url = "https://github.com/trusted/firmware.bin"
    };
    return updateFirmware(&pkg);
}
