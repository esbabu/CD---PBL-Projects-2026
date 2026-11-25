#ifndef CRYPTO_H
#define CRYPTO_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#define AES_KEY_LEN     32  // AES-256 key size in bytes
#define GCM_IV_LEN      12  // 96-bit standard GCM IV
#define GCM_TAG_LEN     16  // 128-bit GCM authentication tag
#define SHA256_HASH_LEN 32  // SHA-256 digest length
#define ECDSA_SIG_LEN   64  // 32-byte r + 32-byte s

// Incremental SHA-256 Context
typedef struct {
    uint32_t state[8];
    uint64_t count;
    uint8_t buffer[64];
} CryptoSha256Context;

void crypto_sha256_init(CryptoSha256Context *ctx);
void crypto_sha256_update(CryptoSha256Context *ctx, const uint8_t *data, size_t len);
void crypto_sha256_final(CryptoSha256Context *ctx, uint8_t hash[SHA256_HASH_LEN]);

// Single-shot SHA-256 computation
void crypto_sha256(const uint8_t *data, size_t len, uint8_t hash[SHA256_HASH_LEN]);

// AES-256-GCM Decryption and Authentication
// Returns 1 on authentic decryption, 0 on tag mismatch or error.
int crypto_aes256_gcm_decrypt(
    const uint8_t *ciphertext, size_t ciphertext_len,
    const uint8_t *aad, size_t aad_len,
    const uint8_t tag[GCM_TAG_LEN],
    const uint8_t key[AES_KEY_LEN],
    const uint8_t iv[GCM_IV_LEN],
    uint8_t *plaintext_out
);

// ECDSA P-256 (SECP256R1) Signature Verification
// Verifies raw signature (32-byte r, 32-byte s) over sha256_hash with (pub_x, pub_y).
// Returns 1 if valid, 0 if invalid or tampered.
int crypto_ecdsa_verify(
    const uint8_t pub_x[32],
    const uint8_t pub_y[32],
    const uint8_t sha256_hash[SHA256_HASH_LEN],
    const uint8_t sig_r[32],
    const uint8_t sig_s[32]
);

// Configure or retrieve device public key coordinates
void set_device_public_key(const uint8_t pub_x[32], const uint8_t pub_y[32]);
void get_device_public_key(uint8_t pub_x_out[32], uint8_t pub_y_out[32]);

// Configure or retrieve pre-shared device master key (PSK / eFuse)
void set_device_master_key(const uint8_t master_key[AES_KEY_LEN]);
void get_device_master_key(uint8_t master_key_out[AES_KEY_LEN]);

// Key Wrapping: Wrap and unwrap ephemeral 256-bit payload keys using Pre-Shared Master Key (PSK)
void crypto_wrap_payload_key(
    const uint8_t master_key[AES_KEY_LEN],
    const uint8_t iv[GCM_IV_LEN],
    const uint8_t payload_key_in[AES_KEY_LEN],
    uint8_t wrapped_key_out[AES_KEY_LEN]
);

void crypto_unwrap_payload_key(
    const uint8_t master_key[AES_KEY_LEN],
    const uint8_t iv[GCM_IV_LEN],
    const uint8_t wrapped_key_in[AES_KEY_LEN],
    uint8_t payload_key_out[AES_KEY_LEN]
);

#ifdef __cplusplus
}
#endif

#endif // CRYPTO_H
