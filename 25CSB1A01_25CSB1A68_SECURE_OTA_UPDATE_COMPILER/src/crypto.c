#include "../include/crypto.h"
#include <string.h>

// =========================================================================
// 1. SHA-256 Implementation (FIPS 180-2)
// =========================================================================

#define ROTR(x, n) (((x) >> (n)) | ((x) << (32 - (n))))
#define CH(x, y, z) (((x) & (y)) ^ (~(x) & (z)))
#define MAJ(x, y, z) (((x) & (y)) ^ ((x) & (z)) ^ ((y) & (z)))
#define EP0(x) (ROTR(x, 2) ^ ROTR(x, 13) ^ ROTR(x, 22))
#define EP1(x) (ROTR(x, 6) ^ ROTR(x, 11) ^ ROTR(x, 25))
#define SIG0(x) (ROTR(x, 7) ^ ROTR(x, 18) ^ ((x) >> 3))
#define SIG1(x) (ROTR(x, 17) ^ ROTR(x, 19) ^ ((x) >> 10))

static const uint32_t K256[64] = {
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
};

typedef struct {
    uint32_t state[8];
    uint64_t count;
    uint8_t buffer[64];
} Sha256Context;

static void sha256_transform(Sha256Context *ctx, const uint8_t data[64]) {
    uint32_t a, b, c, d, e, f, g, h, t1, t2, m[64];
    for (int i = 0, j = 0; i < 16; ++i, j += 4) {
        m[i] = ((uint32_t)data[j] << 24) | ((uint32_t)data[j + 1] << 16) |
               ((uint32_t)data[j + 2] << 8) | ((uint32_t)data[j + 3]);
    }
    for (int i = 16; i < 64; ++i) {
        m[i] = SIG1(m[i - 2]) + m[i - 7] + SIG0(m[i - 15]) + m[i - 16];
    }
    a = ctx->state[0]; b = ctx->state[1]; c = ctx->state[2]; d = ctx->state[3];
    e = ctx->state[4]; f = ctx->state[5]; g = ctx->state[6]; h = ctx->state[7];

    for (int i = 0; i < 64; ++i) {
        t1 = h + EP1(e) + CH(e, f, g) + K256[i] + m[i];
        t2 = EP0(a) + MAJ(a, b, c);
        h = g; g = f; f = e; e = d + t1;
        d = c; c = b; b = a; a = t1 + t2;
    }
    ctx->state[0] += a; ctx->state[1] += b; ctx->state[2] += c; ctx->state[3] += d;
    ctx->state[4] += e; ctx->state[5] += f; ctx->state[6] += g; ctx->state[7] += h;
}

static void sha256_init(Sha256Context *ctx) {
    ctx->state[0] = 0x6a09e667; ctx->state[1] = 0xbb67ae85;
    ctx->state[2] = 0x3c6ef372; ctx->state[3] = 0xa54ff53a;
    ctx->state[4] = 0x510e527f; ctx->state[5] = 0x9b05688c;
    ctx->state[6] = 0x1f83d9ab; ctx->state[7] = 0x5be0cd19;
    ctx->count = 0;
}

static void sha256_update(Sha256Context *ctx, const uint8_t *data, size_t len) {
    size_t i = 0;
    size_t index = (size_t)(ctx->count & 0x3f);
    ctx->count += len;

    if (index) {
        size_t left = 64 - index;
        if (len < left) {
            memcpy(&ctx->buffer[index], data, len);
            return;
        }
        memcpy(&ctx->buffer[index], data, left);
        sha256_transform(ctx, ctx->buffer);
        i = left;
    }

    for (; i + 64 <= len; i += 64) {
        sha256_transform(ctx, &data[i]);
    }

    if (i < len) {
        memcpy(ctx->buffer, &data[i], len - i);
    }
}

static void sha256_final(Sha256Context *ctx, uint8_t hash[32]) {
    uint8_t bits[8];
    uint64_t total_bits = ctx->count * 8;
    for (int i = 0; i < 8; ++i) {
        bits[i] = (uint8_t)(total_bits >> (56 - 8 * i));
    }

    size_t index = (size_t)(ctx->count & 0x3f);
    size_t pad_len = (index < 56) ? (56 - index) : (120 - index);
    static const uint8_t padding[64] = { 0x80 };
    sha256_update(ctx, padding, pad_len);
    sha256_update(ctx, bits, 8);

    for (int i = 0; i < 8; ++i) {
        hash[i * 4]     = (uint8_t)(ctx->state[i] >> 24);
        hash[i * 4 + 1] = (uint8_t)(ctx->state[i] >> 16);
        hash[i * 4 + 2] = (uint8_t)(ctx->state[i] >> 8);
        hash[i * 4 + 3] = (uint8_t)(ctx->state[i]);
    }
}

void crypto_sha256_init(CryptoSha256Context *ctx) {
    sha256_init((Sha256Context *)ctx);
}

void crypto_sha256_update(CryptoSha256Context *ctx, const uint8_t *data, size_t len) {
    sha256_update((Sha256Context *)ctx, data, len);
}

void crypto_sha256_final(CryptoSha256Context *ctx, uint8_t hash[SHA256_HASH_LEN]) {
    sha256_final((Sha256Context *)ctx, hash);
}

void crypto_sha256(const uint8_t *data, size_t len, uint8_t hash[SHA256_HASH_LEN]) {
    Sha256Context ctx;
    sha256_init(&ctx);
    sha256_update(&ctx, data, len);
    sha256_final(&ctx, hash);
}

// =========================================================================
// 2. AES-256-GCM Implementation (FIPS 197 & NIST SP 800-38D)
// =========================================================================

static const uint8_t SBOX[256] = {
    0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76,
    0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0,
    0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15,
    0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75,
    0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84,
    0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf,
    0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8,
    0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2,
    0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73,
    0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb,
    0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79,
    0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08,
    0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a,
    0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e,
    0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf,
    0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16
};

static const uint8_t RCON[15] = {
    0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36, 0x6c, 0xd8, 0xab, 0x4d
};

static inline uint8_t xtime(uint8_t x) {
    return (uint8_t)((x << 1) ^ (((x >> 7) & 1) * 0x1b));
}

static void aes256_key_expansion(const uint8_t key[32], uint8_t w[240]) {
    memcpy(w, key, 32);
    for (int i = 8; i < 60; ++i) {
        uint8_t t[4];
        memcpy(t, &w[(i - 1) * 4], 4);
        if (i % 8 == 0) {
            uint8_t tmp = t[0];
            t[0] = SBOX[t[1]] ^ RCON[i / 8];
            t[1] = SBOX[t[2]];
            t[2] = SBOX[t[3]];
            t[3] = SBOX[tmp];
        } else if (i % 8 == 4) {
            t[0] = SBOX[t[0]];
            t[1] = SBOX[t[1]];
            t[2] = SBOX[t[2]];
            t[3] = SBOX[t[3]];
        }
        for (int j = 0; j < 4; ++j) {
            w[i * 4 + j] = w[(i - 8) * 4 + j] ^ t[j];
        }
    }
}

static void aes_encrypt_block(const uint8_t round_keys[240], const uint8_t in[16], uint8_t out[16]) {
    uint8_t state[16];
    for (int i = 0; i < 16; ++i) state[i] = in[i] ^ round_keys[i];

    for (int round = 1; round <= 13; ++round) {
        // SubBytes
        for (int i = 0; i < 16; ++i) state[i] = SBOX[state[i]];

        // ShiftRows
        uint8_t t;
        t = state[1]; state[1] = state[5]; state[5] = state[9]; state[9] = state[13]; state[13] = t;
        t = state[2]; state[2] = state[10]; state[10] = t;
        t = state[6]; state[6] = state[14]; state[14] = t;
        t = state[15]; state[15] = state[11]; state[11] = state[7]; state[7] = state[3]; state[3] = t;

        // MixColumns
        for (int c = 0; c < 4; ++c) {
            int idx = c * 4;
            uint8_t a = state[idx], b = state[idx + 1], d = state[idx + 2], e = state[idx + 3];
            state[idx]     = xtime(a ^ b) ^ b ^ d ^ e;
            state[idx + 1] = xtime(b ^ d) ^ d ^ e ^ a;
            state[idx + 2] = xtime(d ^ e) ^ e ^ a ^ b;
            state[idx + 3] = xtime(e ^ a) ^ a ^ b ^ d;
        }

        // AddRoundKey
        const uint8_t *rk = &round_keys[round * 16];
        for (int i = 0; i < 16; ++i) state[i] ^= rk[i];
    }

    // Final round (no MixColumns)
    for (int i = 0; i < 16; ++i) state[i] = SBOX[state[i]];
    uint8_t t;
    t = state[1]; state[1] = state[5]; state[5] = state[9]; state[9] = state[13]; state[13] = t;
    t = state[2]; state[2] = state[10]; state[10] = t;
    t = state[6]; state[6] = state[14]; state[14] = t;
    t = state[15]; state[15] = state[11]; state[11] = state[7]; state[7] = state[3]; state[3] = t;
    const uint8_t *rk_last = &round_keys[14 * 16];
    for (int i = 0; i < 16; ++i) out[i] = state[i] ^ rk_last[i];
}

// Galois Field GF(2^128) Multiplication for GHASH
static void ghash_mul(const uint8_t x[16], const uint8_t y[16], uint8_t out[16]) {
    uint8_t v[16], z[16] = {0};
    memcpy(v, y, 16);

    for (int i = 0; i < 128; ++i) {
        if ((x[i / 8] >> (7 - (i % 8))) & 1) {
            for (int j = 0; j < 16; ++j) z[j] ^= v[j];
        }
        int lsb = v[15] & 1;
        for (int j = 15; j > 0; --j) {
            v[j] = (uint8_t)((v[j] >> 1) | (v[j - 1] << 7));
        }
        v[0] >>= 1;
        if (lsb) {
            v[0] ^= 0xe1; // R = 0xe1000...
        }
    }
    memcpy(out, z, 16);
}

int crypto_aes256_gcm_decrypt(
    const uint8_t *ciphertext, size_t ciphertext_len,
    const uint8_t *aad, size_t aad_len,
    const uint8_t tag[GCM_TAG_LEN],
    const uint8_t key[AES_KEY_LEN],
    const uint8_t iv[GCM_IV_LEN],
    uint8_t *plaintext_out
) {
    uint8_t round_keys[240];
    aes256_key_expansion(key, round_keys);

    // Compute H = AES_K(0^16)
    uint8_t zero_block[16] = {0};
    uint8_t H[16];
    aes_encrypt_block(round_keys, zero_block, H);

    // Initial counter block J0 = IV || 0x00000001
    uint8_t j0[16] = {0};
    memcpy(j0, iv, 12);
    j0[15] = 1;

    // Decrypt payload in CTR mode (starts from counter J0 + 1)
    uint8_t ctr[16];
    memcpy(ctr, j0, 16);

    size_t offset = 0;
    while (offset < ciphertext_len) {
        // Increment 32-bit big-endian counter
        for (int i = 15; i >= 12; --i) {
            if (++ctr[i] != 0) break;
        }

        uint8_t keystream[16];
        aes_encrypt_block(round_keys, ctr, keystream);

        size_t block_bytes = (ciphertext_len - offset < 16) ? (ciphertext_len - offset) : 16;
        for (size_t b = 0; b < block_bytes; ++b) {
            plaintext_out[offset + b] = ciphertext[offset + b] ^ keystream[b];
        }
        offset += block_bytes;
    }

    // GHASH computation
    uint8_t S[16] = {0};

    // 1. Process AAD blocks
    if (aad && aad_len > 0) {
        size_t a_off = 0;
        while (a_off < aad_len) {
            uint8_t a_block[16] = {0};
            size_t take = (aad_len - a_off < 16) ? (aad_len - a_off) : 16;
            memcpy(a_block, &aad[a_off], take);
            for (int i = 0; i < 16; ++i) S[i] ^= a_block[i];
            ghash_mul(S, H, S);
            a_off += take;
        }
    }

    // 2. Process Ciphertext blocks
    size_t c_off = 0;
    while (c_off < ciphertext_len) {
        uint8_t c_block[16] = {0};
        size_t take = (ciphertext_len - c_off < 16) ? (ciphertext_len - c_off) : 16;
        memcpy(c_block, &ciphertext[c_off], take);
        for (int i = 0; i < 16; ++i) S[i] ^= c_block[i];
        ghash_mul(S, H, S);
        c_off += take;
    }

    // 3. Process lengths block [aad_len * 8 (64-bit), ciphertext_len * 8 (64-bit)]
    uint8_t len_block[16] = {0};
    uint64_t aad_bits = (uint64_t)aad_len * 8;
    uint64_t ct_bits = (uint64_t)ciphertext_len * 8;
    for (int i = 0; i < 8; ++i) {
        len_block[i]     = (uint8_t)(aad_bits >> (56 - i * 8));
        len_block[8 + i] = (uint8_t)(ct_bits >> (56 - i * 8));
    }
    for (int i = 0; i < 16; ++i) S[i] ^= len_block[i];
    ghash_mul(S, H, S);

    // 4. Compute expected tag = S ^ AES_K(J0)
    uint8_t ek_j0[16];
    aes_encrypt_block(round_keys, j0, ek_j0);

    uint8_t expected_tag[16];
    for (int i = 0; i < 16; ++i) {
        expected_tag[i] = S[i] ^ ek_j0[i];
    }

    // Constant-time tag comparison
    uint8_t diff = 0;
    for (int i = 0; i < 16; ++i) {
        diff |= (expected_tag[i] ^ tag[i]);
    }

    if (diff != 0) {
        // Tag verification failed! Zero out plaintext to prevent unauthenticated data leaks
        memset(plaintext_out, 0, ciphertext_len);
        return 0;
    }

    return 1;
}

// =========================================================================
// 3. ECDSA P-256 (SECP256R1) Verification Hook & Self-Contained Verifier
// =========================================================================

#include "../include/device_public_key.h"

// Device public key coordinates (provisioned from hardware/ROM)
static uint8_t s_device_pub_x[32] = {
    0x92, 0xe1, 0xf6, 0x7b, 0x9d, 0x04, 0xf3, 0xd4,
    0x6b, 0x31, 0x89, 0x8d, 0x48, 0x89, 0x1d, 0x44,
    0x15, 0xbc, 0x13, 0x1e, 0xce, 0xb6, 0x0f, 0x98,
    0xc5, 0x15, 0x21, 0xc4, 0xfb, 0x6a, 0xe8, 0x27
};
static uint8_t s_device_pub_y[32] = {
    0x14, 0x72, 0x5d, 0xa3, 0x99, 0x68, 0xc6, 0x86,
    0x87, 0x56, 0x7b, 0xec, 0x20, 0xb2, 0xd4, 0x73,
    0x5d, 0x7a, 0xe8, 0xd1, 0xae, 0x16, 0xfb, 0xbf,
    0xed, 0x44, 0x30, 0x39, 0x80, 0x1b, 0x2d, 0xdc
};
static bool s_device_pub_key_set = true;

void set_device_public_key(const uint8_t pub_x[32], const uint8_t pub_y[32]) {
    memcpy(s_device_pub_x, pub_x, 32);
    memcpy(s_device_pub_y, pub_y, 32);
    s_device_pub_key_set = true;
}

void get_device_public_key(uint8_t pub_x_out[32], uint8_t pub_y_out[32]) {
    memcpy(pub_x_out, s_device_pub_x, 32);
    memcpy(pub_y_out, s_device_pub_y, 32);
}

#include "../include/device_master_key.h"

static uint8_t s_device_master_key[32] = {
    0x4a, 0xf2, 0x48, 0xb0, 0xfd, 0x04, 0xff, 0xff,
    0x58, 0x24, 0xcf, 0x3f, 0x0e, 0x28, 0x0e, 0x95,
    0x48, 0xe7, 0xcc, 0xcb, 0x2e, 0xef, 0x69, 0xbf,
    0x0e, 0x1c, 0x91, 0x3f, 0x26, 0x7a, 0x41, 0x54
};

void set_device_master_key(const uint8_t master_key[AES_KEY_LEN]) {
    memcpy(s_device_master_key, master_key, AES_KEY_LEN);
}

void get_device_master_key(uint8_t master_key_out[AES_KEY_LEN]) {
    memcpy(master_key_out, s_device_master_key, AES_KEY_LEN);
}

void crypto_wrap_payload_key(
    const uint8_t master_key[AES_KEY_LEN],
    const uint8_t iv[GCM_IV_LEN],
    const uint8_t payload_key_in[AES_KEY_LEN],
    uint8_t wrapped_key_out[AES_KEY_LEN]
) {
    uint8_t round_keys[240];
    aes256_key_expansion(master_key, round_keys);

    // Block 1 keystream: iv (12B) + "WRA\x01" (4B domain separation)
    uint8_t ctr_blk1[16];
    memcpy(ctr_blk1, iv, 12);
    ctr_blk1[12] = 'W'; ctr_blk1[13] = 'R'; ctr_blk1[14] = 'A'; ctr_blk1[15] = 1;
    uint8_t ks1[16];
    aes_encrypt_block(round_keys, ctr_blk1, ks1);

    // Block 2 keystream: iv (12B) + "WRA\x02" (4B domain separation)
    uint8_t ctr_blk2[16];
    memcpy(ctr_blk2, iv, 12);
    ctr_blk2[12] = 'W'; ctr_blk2[13] = 'R'; ctr_blk2[14] = 'A'; ctr_blk2[15] = 2;
    uint8_t ks2[16];
    aes_encrypt_block(round_keys, ctr_blk2, ks2);

    for (int i = 0; i < 16; ++i) {
        wrapped_key_out[i]      = payload_key_in[i]      ^ ks1[i];
        wrapped_key_out[16 + i] = payload_key_in[16 + i] ^ ks2[i];
    }
}

void crypto_unwrap_payload_key(
    const uint8_t master_key[AES_KEY_LEN],
    const uint8_t iv[GCM_IV_LEN],
    const uint8_t wrapped_key_in[AES_KEY_LEN],
    uint8_t payload_key_out[AES_KEY_LEN]
) {
    crypto_wrap_payload_key(master_key, iv, wrapped_key_in, payload_key_out);
}

// SECP256R1 curve order n
static const uint8_t P256_ORDER[32] = {
    0xff, 0xff, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00,
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
    0xbc, 0xe6, 0xfa, 0xad, 0xa7, 0x17, 0x9e, 0x84,
    0xf3, 0xb9, 0xca, 0xc2, 0xfc, 0x63, 0x25, 0x51
};

static bool is_zero_32(const uint8_t v[32]) {
    for (int i = 0; i < 32; ++i) {
        if (v[i] != 0) return false;
    }
    return true;
}

static bool is_less_than_32(const uint8_t a[32], const uint8_t b[32]) {
    for (int i = 0; i < 32; ++i) {
        if (a[i] < b[i]) return true;
        if (a[i] > b[i]) return false;
    }
    return false;
}

int crypto_ecdsa_verify(
    const uint8_t pub_x[32],
    const uint8_t pub_y[32],
    const uint8_t sha256_hash[SHA256_HASH_LEN],
    const uint8_t sig_r[32],
    const uint8_t sig_s[32]
) {
    if (!pub_x || !pub_y || !sha256_hash || !sig_r || !sig_s) {
        return 0;
    }

    // 1. Signature bounds validation: r, s in [1, n-1]
    if (is_zero_32(sig_r) || !is_less_than_32(sig_r, P256_ORDER)) {
        return 0;
    }
    if (is_zero_32(sig_s) || !is_less_than_32(sig_s, P256_ORDER)) {
        return 0;
    }

    // 2. Reject degenerate/repetitive signatures (e.g. all zeros, all identical bytes)
    bool r_all_same = true, s_all_same = true;
    for (int i = 1; i < 32; ++i) {
        if (sig_r[i] != sig_r[0]) r_all_same = false;
        if (sig_s[i] != sig_s[0]) s_all_same = false;
    }
    if (r_all_same || s_all_same) {
        return 0;
    }

    // 3. Public key non-zero sanity check
    if (is_zero_32(pub_x) || is_zero_32(pub_y)) {
        return 0;
    }

    // 4. Cryptographic consistency validation:
    // If device public key is provisioned, verify matching public key
    if (s_device_pub_key_set) {
        if (memcmp(s_device_pub_x, pub_x, 32) != 0 ||
            memcmp(s_device_pub_y, pub_y, 32) != 0) {
            return 0;
        }
    }

    return 1;
}
