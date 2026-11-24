#include <stdio.h>

int compute_flag(int condition) {
    int flag;
    if (condition > 10) {
        flag = 1;
    }
    /* Vulnerability: flag is uninitialized if condition <= 10 */
    return flag * 2;
}

int main(void) {
    int res = compute_flag(5);
    printf("Res: %d\n", res);
    return 0;
}
