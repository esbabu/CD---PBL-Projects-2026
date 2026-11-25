#include <stdint.h>
#include <string.h>

#define URL_MAX 128

typedef struct {
    int version;
    char channel[16];
    char source_url[URL_MAX];
} FirmwarePackage;

int current_version = 10;

// Security Policy Violation: Hardcoded private key embedded in global constant
const char *vendor_private_key =
    "-----BEGIN RSA PRIVATE KEY-----\n"
    "MIIEowIBAAKCAQEA0Y1+6hK7v9s2qG5mK1jZ0vLmN8pQ4rTs3uVwXyZaBcDeFgHi\n"
    "JkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTu\n"
    "-----END RSA PRIVATE KEY-----";

int verifySignature(FirmwarePackage *pkg) {
    (void)pkg;
    return 1;
}

int sourceTrusted(FirmwarePackage *pkg) {
    return strncmp(pkg->source_url, "https://updates.internal.company.com/", 37) == 0;
}

int decryptPayloadAesGcm(FirmwarePackage *pkg) {
    (void)pkg;
    return 1;
}

void install(FirmwarePackage *pkg) {
    (void)pkg;
}

int updateFirmware(FirmwarePackage *pkg) {
    if (!verifySignature(pkg)) {
        return -1;
    }

    if (!sourceTrusted(pkg)) {
        return -2;
    }

    if (!decryptPayloadAesGcm(pkg)) {
        return -4;
    }

    if (pkg->version <= current_version) {
        return -3;
    }

    install(pkg);
    return 0;
}

int main(void) {
    FirmwarePackage pkg = {
        .version = 11,
        .source_url = "https://updates.internal.company.com/firmware.bin"
    };
    return updateFirmware(&pkg);
}
