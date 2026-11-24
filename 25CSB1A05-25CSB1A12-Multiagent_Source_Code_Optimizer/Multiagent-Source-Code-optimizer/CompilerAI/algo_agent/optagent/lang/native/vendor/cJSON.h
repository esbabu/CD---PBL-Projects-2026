/* Lightweight vendored cJSON-compatible header for OptAgent C drivers.
 * Inside sandbox-native Docker, system <cjson/cJSON.h> is also available.
 */
#ifndef OPTAGENT_CJSON_H
#define OPTAGENT_CJSON_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    cJSON_Invalid = 0,
    cJSON_False   = 1 << 0,
    cJSON_True    = 1 << 1,
    cJSON_NULL    = 1 << 2,
    cJSON_Number  = 1 << 3,
    cJSON_String  = 1 << 4,
    cJSON_Array   = 1 << 5,
    cJSON_Object  = 1 << 6
} cJSON_Type;

typedef struct cJSON {
    struct cJSON *next;
    struct cJSON *prev;
    struct cJSON *child;
    int type;
    char *valuestring;
    long long valueint;
    double valuedouble;
    char *string;
} cJSON;

cJSON *cJSON_Parse(const char *value);
void   cJSON_Delete(cJSON *item);
int    cJSON_GetArraySize(const cJSON *array);
cJSON *cJSON_GetArrayItem(const cJSON *array, int index);
cJSON *cJSON_GetObjectItemCaseSensitive(const cJSON *object, const char *string);
int    cJSON_IsBool(const cJSON *item);
int    cJSON_IsTrue(const cJSON *item);
int    cJSON_IsNull(const cJSON *item);
int    cJSON_IsNumber(const cJSON *item);
int    cJSON_IsString(const cJSON *item);
int    cJSON_IsArray(const cJSON *item);
int    cJSON_IsObject(const cJSON *item);

#ifdef __cplusplus
}
#endif

#endif /* OPTAGENT_CJSON_H */
