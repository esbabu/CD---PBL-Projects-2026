#ifndef UPDATE_HANDLER_H
#define UPDATE_HANDLER_H

#include "version.h"
#include "crypto.h"
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#define URL_MAX 128
#define HASH_LEN 32
#define OTA_MAGIC 0x3141544F
#define MAX_PAYLOAD_SIZE 65536

typedef enum {
    OTA_UPDATE_SUCCESS = 0,
    ERR_SIGNATURE_INVALID = -1,
    ERR_SOURCE_UNTRUSTED = -2,
    ERR_IMAGE_HASH_INVALID = -3,
    ERR_VERSION_ROLLBACK_BLOCKED = -4,
    ERR_INSTALL_FAILED = -5,
    ERR_DECRYPTION_FAILED = -6,
    ERR_INVALID_PACKAGE = -7
} UpdateStatus;

#pragma pack(push, 1)
typedef struct {
    uint32_t magic;              // 0x3141544F ('OTA1')
    uint32_t version;            // Packed SemVer monotonic integer
    char version_str[16];        // Semantic version string (e.g. "1.2.0")
    char channel[16];            // Target release channel
    char source_url[URL_MAX];    // Trusted URL
    uint8_t iv[12];              // 96-bit AES-GCM IV
    union {
        uint8_t aes_key[32];     // Legacy alias
        uint8_t wrapped_key[32]; // AES-256 payload key wrapped with Master Key (PSK)
    };
    uint32_t payload_len;        // Ciphertext size in bytes
    uint8_t image_hash[32];      // SHA-256 over metadata + ciphertext + tag
    uint8_t signature[64];       // ECDSA P-256 raw signature (32B r + 32B s)
    uint8_t tag[16];             // 128-bit AES-GCM tag
} OtaPackageHeader;
#pragma pack(pop)

_Static_assert(sizeof(OtaPackageHeader) == 328, "OtaPackageHeader size must be exactly 328 bytes");

// Firmware update package header containing version metadata (legacy structure)
typedef struct {
    uint32_t version;         // Monotonic integer / packed SemVer
    char version_str[16];     // String representation (e.g. "1.2.0")
    char channel[16];
    char source_url[URL_MAX];
    uint8_t image_hash[HASH_LEN];
    uint8_t signature[64];
    uint32_t image_size;
} FirmwareHeader;

// Firmware update container package
typedef struct {
    FirmwareHeader header;
    int version;              // Monotonic version alias
    char channel[16];
    char source_url[URL_MAX];
    uint8_t image_hash[HASH_LEN];
    uint8_t signature[64];
    uint8_t image[512];
    uint32_t image_size;

    // Encrypt-Then-Sign OTA bundle support
    OtaPackageHeader ota_header;
    const uint8_t *raw_ota_data;
    size_t raw_ota_len;
    const uint8_t *ciphertext;
    size_t ciphertext_len;
    uint8_t decrypted_payload[MAX_PAYLOAD_SIZE];
    size_t decrypted_len;
    bool is_ota_bundle;
} FirmwarePackage;

// Device runtime state
typedef struct {
    int current_version;
    int boot_slot;
    int pending_slot;
    char active_channel[16];
} DeviceState;

// Cryptographic and integrity verification hooks
int verify_cryptographic_signature(FirmwarePackage *pkg);
int verifySignature(FirmwarePackage *pkg);
int sourceTrusted(FirmwarePackage *pkg);
int verify_image_hash(FirmwarePackage *pkg);
int verifyImageHash(FirmwarePackage *pkg);
int decrypt_payload_aes_gcm(FirmwarePackage *pkg, uint8_t *out_buf, size_t out_max, size_t *out_len);
void install(FirmwarePackage *pkg);

// Helper to load raw .ota binary bundle into FirmwarePackage
int load_ota_package(const uint8_t *data, size_t len, FirmwarePackage *pkg);

// Header parsing helper
uint32_t parse_incoming_version(const FirmwarePackage *pkg);

// Core firmware update logic with rollback guard & dominance verification
UpdateStatus updateFirmware(DeviceState *dev, FirmwarePackage *pkg);

#ifdef __cplusplus
}
#endif

#endif // UPDATE_HANDLER_H
