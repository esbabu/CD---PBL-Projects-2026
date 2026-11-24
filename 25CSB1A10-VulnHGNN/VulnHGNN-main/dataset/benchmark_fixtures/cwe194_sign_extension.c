#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void copy_data(short length, const char *src) {
    /* Vulnerability: signed short sign-extended when converted to size_t */
    char *buf = (char *)malloc((size_t)length);
    if (!buf) return;
    memcpy(buf, src, (size_t)length);
    free(buf);
}

int main(void) {
    copy_data(-1, "Data");
    return 0;
}
