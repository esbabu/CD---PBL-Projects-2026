#include <stdio.h>
#include <string.h>
#include <stdlib.h>

void vulnerable_function(char *user_input) {
    char buffer[64];
    
    // 1. Unsafe input reading (CWE-242)
    gets(buffer);

    // 2. Buffer overflow via unbounded copy (CWE-120)
    strcpy(buffer, user_input);

    // 3. Format string vulnerability (CWE-134)
    printf(user_input);

    // 4. Integer overflow leading to heap overflow (CWE-190)
    int count = 1000000;
    int *array = (int *)malloc(count * sizeof(int));
    
    // 5. Unchecked malloc (CWE-476)
    array[0] = 42;

    free(array);

    // 6. Use-after-free (CWE-416)
    printf("Array value: %d\n", array[0]);
}

int main(int argc, char **argv) {
    if (argc > 1) {
        vulnerable_function(argv[1]);
    }
    return 0;
}
