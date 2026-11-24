#include <stdio.h>

typedef struct {
    int val;
} Node;

int safe_read_node(const Node *node) {
    /* Safe: NULL check on pointer parameter */
    if (!node) return 0;
    return node->val;
}

int main(void) {
    Node n = {42};
    printf("Val: %d\n", safe_read_node(&n));
    return 0;
}
