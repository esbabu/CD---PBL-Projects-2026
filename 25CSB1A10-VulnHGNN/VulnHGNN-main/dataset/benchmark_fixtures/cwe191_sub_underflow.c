#include <stdio.h>
#include <limits.h>

int decrement_account(int balance, int debit) {
    /* Vulnerability: subtraction can underflow below INT_MIN */
    int new_balance = balance - debit;
    return new_balance;
}

int main(void) {
    int res = decrement_account(INT_MIN, 1);
    printf("Balance: %d\n", res);
    return 0;
}
