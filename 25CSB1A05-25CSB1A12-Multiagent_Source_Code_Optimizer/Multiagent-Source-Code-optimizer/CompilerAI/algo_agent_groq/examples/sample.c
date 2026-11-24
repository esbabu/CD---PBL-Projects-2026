#include <stdio.h>

int contains(const int values[], int size, int target) {
    for (int i = 0; i < size; ++i) {
        if (values[i] == target) {
            return 1;
        }
    }
    return 0;
}

int main(void) {
    const int values[] = {4, 8, 15, 16, 23, 42};
    const int size = (int)(sizeof(values) / sizeof(values[0]));
    printf("%s\n", contains(values, size, 15) ? "true" : "false");
    return 0;
}
