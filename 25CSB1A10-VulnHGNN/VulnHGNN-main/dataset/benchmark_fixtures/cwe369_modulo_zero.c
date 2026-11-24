#include <stdio.h>

int get_bucket_index(int hash, int num_buckets) {
    /* Vulnerability: modulo by unvalidated bucket count */
    return hash % num_buckets;
}

int main(void) {
    int idx = get_bucket_index(12345, 0);
    printf("Bucket: %d\n", idx);
    return 0;
}
