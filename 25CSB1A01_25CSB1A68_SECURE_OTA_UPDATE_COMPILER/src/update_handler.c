#include "update_handler.h"
#include "crypto.h"
#include <string.h>

int verify_cryptographic_signature(FirmwarePackage *pkg) {
    if (!pkg) {
        return 0;
    }

    if (pkg->is_ota_bundle) {
        uint8_t pub_x[32];
        uint8_t pub_y[32];
        get_device_public_key(pub_x, pub_y);

        const uint8_t *sig_r = pkg->ota_header.signature;
        const uint8_t *sig_s = pkg->ota_header.signature + 32;

        return crypto_ecdsa_verify(
            pub_x,
            pub_y,
            pkg->ota_header.image_hash,
            sig_r,
            sig_s
        );
    }

    return 1;
}

int verifySignature(FirmwarePackage *pkg) {
    return verify_cryptographic_signature(pkg);
}

int sourceTrusted(FirmwarePackage *pkg) {
    if (!pkg) {
        return 0;
    }
    return strncmp(pkg->source_url, "https://github.com/", strlen("https://github.com/")) == 0;
}

int verify_image_hash(FirmwarePackage *pkg) {
    if (!pkg) {
        return 0;
    }

    if (pkg->is_ota_bundle) {
        CryptoSha256Context ctx;
        crypto_sha256_init(&ctx);

        // 1. Hash metadata block (first 216 bytes of OtaPackageHeader)
        crypto_sha256_update(&ctx, (const uint8_t *)&pkg->ota_header, 216);

        // 2. Hash encrypted ciphertext payload
        if (pkg->ciphertext && pkg->ciphertext_len > 0) {
            crypto_sha256_update(&ctx, pkg->ciphertext, pkg->ciphertext_len);
        }

        // 3. Hash AES-GCM authentication tag (16 bytes)
        crypto_sha256_update(&ctx, pkg->ota_header.tag, 16);

        uint8_t computed_hash[32];
        crypto_sha256_final(&ctx, computed_hash);

        // Strict comparison with expected image_hash in header
        if (memcmp(computed_hash, pkg->ota_header.image_hash, 32) != 0) {
            return 0;
        }
    }

    return 1;
}

int verifyImageHash(FirmwarePackage *pkg) {
    return verify_image_hash(pkg);
}

int decrypt_payload_aes_gcm(FirmwarePackage *pkg, uint8_t *out_buf, size_t out_max, size_t *out_len) {
    if (!pkg || !pkg->is_ota_bundle || !out_buf) {
        if (out_len) *out_len = 0;
        return 0;
    }

    if (pkg->ciphertext_len > out_max) {
        if (out_len) *out_len = 0;
        return 0;
    }

    // 1. Retrieve provisioned Pre-Shared Master Key (PSK / eFuse)
    uint8_t master_key[AES_KEY_LEN];
    get_device_master_key(master_key);

    // 2. Unwrap ephemeral 256-bit AES payload key
    uint8_t payload_key[AES_KEY_LEN];
    crypto_unwrap_payload_key(master_key, pkg->ota_header.iv, pkg->ota_header.wrapped_key, payload_key);

    // 3. Decrypt and authenticate payload with ephemeral AES-256-GCM key
    int success = crypto_aes256_gcm_decrypt(
        pkg->ciphertext,
        pkg->ciphertext_len,
        NULL,
        0,
        pkg->ota_header.tag,
        payload_key,
        pkg->ota_header.iv,
        out_buf
    );

    // 4. Securely wipe ephemeral payload key and master key copy from memory
    memset(payload_key, 0, sizeof(payload_key));
    memset(master_key, 0, sizeof(master_key));

    if (success) {
        if (out_len) *out_len = pkg->ciphertext_len;
        return 1;
    } else {
        if (out_len) *out_len = 0;
        return 0;
    }
}

void install(FirmwarePackage *pkg) {
    (void)pkg;
}

int load_ota_package(const uint8_t *data, size_t len, FirmwarePackage *pkg) {
    if (!data || !pkg || len < sizeof(OtaPackageHeader)) {
        return 0;
    }

    memset(pkg, 0, sizeof(*pkg));
    memcpy(&pkg->ota_header, data, sizeof(OtaPackageHeader));

    if (pkg->ota_header.magic != OTA_MAGIC) {
        return 0;
    }

    if (len < sizeof(OtaPackageHeader) + pkg->ota_header.payload_len) {
        return 0;
    }

    pkg->ciphertext = data + sizeof(OtaPackageHeader);
    pkg->ciphertext_len = pkg->ota_header.payload_len;
    pkg->raw_ota_data = data;
    pkg->raw_ota_len = len;
    pkg->is_ota_bundle = true;

    // Populate common and legacy package fields
    pkg->version = (int)pkg->ota_header.version;
    pkg->header.version = pkg->ota_header.version;
    memcpy(pkg->header.version_str, pkg->ota_header.version_str, sizeof(pkg->header.version_str));
    memcpy(pkg->header.channel, pkg->ota_header.channel, sizeof(pkg->header.channel));
    memcpy(pkg->channel, pkg->ota_header.channel, sizeof(pkg->channel));
    memcpy(pkg->header.source_url, pkg->ota_header.source_url, sizeof(pkg->header.source_url));
    memcpy(pkg->source_url, pkg->ota_header.source_url, sizeof(pkg->source_url));
    memcpy(pkg->header.image_hash, pkg->ota_header.image_hash, sizeof(pkg->header.image_hash));
    memcpy(pkg->image_hash, pkg->ota_header.image_hash, sizeof(pkg->image_hash));
    memcpy(pkg->header.signature, pkg->ota_header.signature, sizeof(pkg->header.signature));
    memcpy(pkg->signature, pkg->ota_header.signature, sizeof(pkg->signature));
    pkg->header.image_size = pkg->ota_header.payload_len;
    pkg->image_size = pkg->ota_header.payload_len;

    return 1;
}

uint32_t parse_incoming_version(const FirmwarePackage *pkg) {
    if (!pkg) {
        return 0;
    }
    if (pkg->is_ota_bundle && pkg->ota_header.version != 0) {
        return pkg->ota_header.version;
    }
    if (pkg->header.version_str[0] != '\0') {
        SemVer sv;
        if (parse_semver(pkg->header.version_str, &sv) == 0) {
            return semver_to_u32(sv);
        }
    }
    if (pkg->header.version != 0) {
        return pkg->header.version;
    }
    return (uint32_t)pkg->version;
}

UpdateStatus updateFirmware(DeviceState *dev, FirmwarePackage *pkg) {
    if (!pkg) {
        return ERR_INVALID_PACKAGE;
    }

    // 1. Asymmetric ECDSA Signature Check
    if (!verify_cryptographic_signature(pkg)) {
        return ERR_SIGNATURE_INVALID;
    }

    // 2. Trusted source validation
    if (!sourceTrusted(pkg)) {
        return ERR_SOURCE_UNTRUSTED;
    }

    // 3. Image hash integrity verification (strictly dominates install)
    if (!verify_image_hash(pkg)) {
        return ERR_IMAGE_HASH_INVALID;
    }

    // 4. AES-256-GCM Payload Decryption
    if (pkg->is_ota_bundle) {
        if (!decrypt_payload_aes_gcm(pkg, pkg->decrypted_payload, sizeof(pkg->decrypted_payload), &pkg->decrypted_len)) {
            return ERR_DECRYPTION_FAILED;
        }
    }

    // 5. Monotonic Version & Rollback Guard
    uint32_t incoming_version = parse_incoming_version(pkg);
    if (pkg->version == 0 && incoming_version != 0) {
        pkg->version = (int)incoming_version;
    }

    if (incoming_version <= current_version) {
        // Reject installation to prevent rollback attack
        return ERR_VERSION_ROLLBACK_BLOCKED;
    }

    // 6. Secure installation
    install(pkg);

    // 7. Update persistent storage
    set_current_firmware_version(incoming_version);
    if (dev) {
        dev->current_version = (int)incoming_version;
        dev->pending_slot = dev->boot_slot ^ 1;
    }

    return OTA_UPDATE_SUCCESS;
}
