#include <stdio.h>
#include <string.h>

void copy_user_name(const char *input) {
    char name_buf[16];
    /* Vulnerability: strcpy without length check can overflow stack buffer */
    strcpy(name_buf, input);
    printf("Name: %s\n", name_buf);
}

int main(void) {
    copy_user_name("ThisIsAVeryLongStringExceedingSixteenBytes");
    return 0;
}
