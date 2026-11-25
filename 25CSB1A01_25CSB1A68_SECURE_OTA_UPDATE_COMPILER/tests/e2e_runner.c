#include "update_handler.h"
#include "version.h"
#include "crypto.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <package.ota> [initial_version_packed] [hex_master_key]\n", argv[0]);
        return 1;
    }

    const char *ota_path = argv[1];
    uint32_t initial_ver = MAKE_SEMVER(1, 1, 0); // Default current version: v1.1.0

    if (argc >= 3) {
        initial_ver = (uint32_t)strtoul(argv[2], NULL, 0);
    }

    if (argc >= 4) {
        const char *hex_mk = argv[3];
        if (strlen(hex_mk) == 64) {
            uint8_t custom_mk[32];
            for (int i = 0; i < 32; ++i) {
                unsigned int byte_val = 0;
                if (sscanf(hex_mk + i * 2, "%02x", &byte_val) == 1 ||
                    sscanf(hex_mk + i * 2, "%02X", &byte_val) == 1) {
                    custom_mk[i] = (uint8_t)byte_val;
                }
            }
            set_device_master_key(custom_mk);
        }
    }

    // Initialize device persistent version storage
    init_nvram_version_storage(initial_ver);

    DeviceState dev = {
        .current_version = (int)initial_ver,
        .boot_slot = 0,
        .pending_slot = 1,
        .active_channel = "stable"
    };

    // Read .ota package file
    FILE *f = fopen(ota_path, "rb");
    if (!f) {
        fprintf(stderr, "Error: unable to open file '%s'\n", ota_path);
        return 2;
    }

    fseek(f, 0, SEEK_END);
    long file_size = ftell(f);
    fseek(f, 0, SEEK_SET);

    if (file_size < (long)sizeof(OtaPackageHeader)) {
        fprintf(stderr, "Error: file size %ld too small for OTA header\n", file_size);
        fclose(f);
        return 2;
    }

    uint8_t *buffer = (uint8_t *)malloc((size_t)file_size);
    if (!buffer) {
        fprintf(stderr, "Error: failed to allocate %ld bytes\n", file_size);
        fclose(f);
        return 3;
    }

    size_t read_bytes = fread(buffer, 1, (size_t)file_size, f);
    fclose(f);

    if (read_bytes != (size_t)file_size) {
        fprintf(stderr, "Error: partial file read\n");
        free(buffer);
        return 2;
    }

    FirmwarePackage pkg;
    if (!load_ota_package(buffer, (size_t)file_size, &pkg)) {
        fprintf(stderr, "Error: load_ota_package failed (invalid magic or corrupt header)\n");
        free(buffer);
        return 4;
    }

    // Execute firmware update pipeline
    UpdateStatus status = updateFirmware(&dev, &pkg);

    if (status == OTA_UPDATE_SUCCESS) {
        printf("SUCCESS: Firmware update applied successfully!\n");
        printf("New Active Version: 0x%08X (current_version=%d)\n",
               get_current_firmware_version(), current_version);
        printf("Decrypted Payload Length: %zu bytes\n", pkg.decrypted_len);
        printf("Decrypted Payload Content: ");
        for (size_t i = 0; i < pkg.decrypted_len; ++i) {
            putchar(pkg.decrypted_payload[i]);
        }
        putchar('\n');
        free(buffer);
        return 0;
    } else if (status == ERR_SIGNATURE_INVALID) {
        fprintf(stderr, "HALT: Cryptographic signature verification failed (ERR_SIGNATURE_INVALID)\n");
        free(buffer);
        return 10;
    } else if (status == ERR_SOURCE_UNTRUSTED) {
        fprintf(stderr, "HALT: Source repository untrusted (ERR_SOURCE_UNTRUSTED)\n");
        free(buffer);
        return 11;
    } else if (status == ERR_IMAGE_HASH_INVALID) {
        fprintf(stderr, "HALT: Image hash verification failed (ERR_IMAGE_HASH_INVALID)\n");
        free(buffer);
        return 12;
    } else if (status == ERR_VERSION_ROLLBACK_BLOCKED) {
        fprintf(stderr, "HALT: Monotonic rollback guard blocked update (ERR_VERSION_ROLLBACK_BLOCKED)\n");
        free(buffer);
        return 13;
    } else if (status == ERR_DECRYPTION_FAILED) {
        fprintf(stderr, "HALT: AES-256-GCM decryption / tag authentication failed (ERR_DECRYPTION_FAILED)\n");
        free(buffer);
        return 14;
    } else {
        fprintf(stderr, "HALT: Update failed with error code %d\n", status);
        free(buffer);
        return 15;
    }
}
