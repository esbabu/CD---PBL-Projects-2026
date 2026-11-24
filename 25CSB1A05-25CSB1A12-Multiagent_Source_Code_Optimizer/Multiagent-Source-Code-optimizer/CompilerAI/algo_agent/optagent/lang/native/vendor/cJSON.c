/* Lightweight self-contained cJSON parser implementation for OptAgent C drivers. */
#include "cJSON.h"
#include <ctype.h>
#include <stdlib.h>
#include <string.h>

static cJSON *new_item(void) {
    return (cJSON *)calloc(1, sizeof(cJSON));
}

static const char *skip_ws(const char *p) {
    while (p && *p && (unsigned char)*p <= 32) p++;
    return p;
}

static const char *parse_value(cJSON *item, const char *p);

static const char *parse_string_raw(char **out, const char *p) {
    if (*p != '"') return NULL;
    p++;
    size_t cap = 64, len = 0;
    char *buf = (char *)malloc(cap);
    if (!buf) return NULL;
    while (*p && *p != '"') {
        char ch = *p++;
        if (ch == '\\' && *p) {
            char esc = *p++;
            switch (esc) {
                case '"':  ch = '"'; break;
                case '\\': ch = '\\'; break;
                case '/':  ch = '/'; break;
                case 'b':  ch = '\b'; break;
                case 'f':  ch = '\f'; break;
                case 'n':  ch = '\n'; break;
                case 'r':  ch = '\r'; break;
                case 't':  ch = '\t'; break;
                case 'u': {
                    unsigned int code = 0;
                    for (int i = 0; i < 4 && *p; i++) {
                        code <<= 4;
                        if (*p >= '0' && *p <= '9') code |= (unsigned int)(*p - '0');
                        else if (*p >= 'a' && *p <= 'f') code |= (unsigned int)(*p - 'a' + 10);
                        else if (*p >= 'A' && *p <= 'F') code |= (unsigned int)(*p - 'A' + 10);
                        p++;
                    }
                    ch = (char)(code & 0xFF);
                    break;
                }
                default: ch = esc; break;
            }
        }
        if (len + 2 >= cap) {
            cap *= 2;
            char *nb = (char *)realloc(buf, cap);
            if (!nb) { free(buf); return NULL; }
            buf = nb;
        }
        buf[len++] = ch;
    }
    if (*p != '"') { free(buf); return NULL; }
    buf[len] = '\0';
    *out = buf;
    return p + 1;
}

static const char *parse_number(cJSON *item, const char *p) {
    char *end_d = NULL;
    char *end_i = NULL;
    double d = strtod(p, &end_d);
    long long iv = strtoll(p, &end_i, 10);
    if (end_d == p) return NULL;
    item->type = cJSON_Number;
    item->valuedouble = d;
    item->valueint = (end_i == end_d) ? iv : (long long)d;
    return end_d;
}

static const char *parse_array(cJSON *item, const char *p) {
    if (*p != '[') return NULL;
    item->type = cJSON_Array;
    p = skip_ws(p + 1);
    if (*p == ']') return p + 1;
    cJSON *head = NULL, *tail = NULL;
    while (*p) {
        cJSON *ch = new_item();
        if (!ch) return NULL;
        p = parse_value(ch, skip_ws(p));
        if (!p) { cJSON_Delete(ch); return NULL; }
        if (!head) head = tail = ch;
        else { tail->next = ch; ch->prev = tail; tail = ch; }
        p = skip_ws(p);
        if (*p == ',') { p++; continue; }
        if (*p == ']') { item->child = head; return p + 1; }
        return NULL;
    }
    return NULL;
}

static const char *parse_object(cJSON *item, const char *p) {
    if (*p != '{') return NULL;
    item->type = cJSON_Object;
    p = skip_ws(p + 1);
    if (*p == '}') return p + 1;
    cJSON *head = NULL, *tail = NULL;
    while (*p) {
        char *key = NULL;
        p = parse_string_raw(&key, skip_ws(p));
        if (!p) return NULL;
        p = skip_ws(p);
        if (*p != ':') { free(key); return NULL; }
        cJSON *ch = new_item();
        if (!ch) { free(key); return NULL; }
        ch->string = key;
        p = parse_value(ch, skip_ws(p + 1));
        if (!p) { cJSON_Delete(ch); return NULL; }
        if (!head) head = tail = ch;
        else { tail->next = ch; ch->prev = tail; tail = ch; }
        p = skip_ws(p);
        if (*p == ',') { p++; continue; }
        if (*p == '}') { item->child = head; return p + 1; }
        return NULL;
    }
    return NULL;
}

static const char *parse_value(cJSON *item, const char *p) {
    p = skip_ws(p);
    if (!p || !*p) return NULL;
    if (strncmp(p, "null", 4) == 0)  { item->type = cJSON_NULL;  return p + 4; }
    if (strncmp(p, "false", 5) == 0) { item->type = cJSON_False; return p + 5; }
    if (strncmp(p, "true", 4) == 0)  { item->type = cJSON_True;  item->valueint = 1; return p + 4; }
    if (*p == '"') { item->type = cJSON_String; return parse_string_raw(&item->valuestring, p); }
    if (*p == '[') return parse_array(item, p);
    if (*p == '{') return parse_object(item, p);
    if (*p == '-' || (*p >= '0' && *p <= '9')) return parse_number(item, p);
    return NULL;
}

cJSON *cJSON_Parse(const char *value) {
    if (!value) return NULL;
    cJSON *root = new_item();
    if (!root) return NULL;
    if (!parse_value(root, value)) { cJSON_Delete(root); return NULL; }
    return root;
}

void cJSON_Delete(cJSON *item) {
    while (item) {
        cJSON *next = item->next;
        if (item->child) cJSON_Delete(item->child);
        if (item->valuestring) free(item->valuestring);
        if (item->string) free(item->string);
        free(item);
        item = next;
    }
}

int cJSON_GetArraySize(const cJSON *array) {
    int n = 0;
    if (!array) return 0;
    for (const cJSON *c = array->child; c; c = c->next) n++;
    return n;
}

cJSON *cJSON_GetArrayItem(const cJSON *array, int index) {
    if (!array || index < 0) return NULL;
    cJSON *c = array->child;
    while (c && index-- > 0) c = c->next;
    return c;
}

cJSON *cJSON_GetObjectItemCaseSensitive(const cJSON *object, const char *string) {
    if (!object || !string) return NULL;
    for (cJSON *c = object->child; c; c = c->next) {
        if (c->string && strcmp(c->string, string) == 0) return c;
    }
    return NULL;
}

int cJSON_IsBool(const cJSON *item)   { return item && (item->type == cJSON_True || item->type == cJSON_False); }
int cJSON_IsTrue(const cJSON *item)   { return item && item->type == cJSON_True; }
int cJSON_IsNull(const cJSON *item)   { return item && item->type == cJSON_NULL; }
int cJSON_IsNumber(const cJSON *item) { return item && item->type == cJSON_Number; }
int cJSON_IsString(const cJSON *item) { return item && item->type == cJSON_String; }
int cJSON_IsArray(const cJSON *item)  { return item && item->type == cJSON_Array; }
int cJSON_IsObject(const cJSON *item) { return item && item->type == cJSON_Object; }
