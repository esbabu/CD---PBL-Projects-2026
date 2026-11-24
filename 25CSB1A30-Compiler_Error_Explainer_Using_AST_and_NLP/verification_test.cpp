#include <iostream>
#include <vector>
#include <climits>
#include <cstring>
#include <cstdio>

using namespace std;

// =================================================================
// 1. SECURITY VULNERABILITIES (FOR TESTING SECURITY & AUTO-HEAL)
// =================================================================

// CWE-369: Division by Zero
int testDivisionByZero(int val) {
    int divisor = 0;
    int result = val / divisor; // [Security: CWE-369] Division by zero
    return result;
}

// CWE-190: Integer Overflow
int testIntegerOverflow(int x) {
    int maxLimit = 2147483647; // INT_MAX
    int overflowed = maxLimit + x; // [Security: CWE-190] Integer overflow
    return overflowed;
}

// CWE-120 & CWE-676: Unsafe Buffer Operations
void testBufferSecurity(const char* input) {
    char smallBuffer[16];
    strcpy(smallBuffer, input); // [Security: CWE-120/676] Unsafe string copy
}

// CWE-134: Format String Vulnerability
void testFormatString(const char* userInput) {
    printf(userInput); // [Security: CWE-134] Uncontrolled format string
}

// =================================================================
// 2. ALGORITHMIC BOTTLENECK (FOR TESTING OPTIMIZE CODE: O(n²) ➔ O(n log n))
// =================================================================

vector<int> quadraticBubbleSort(vector<int> arr) {
    int n = arr.size();
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }
    return arr;
}

// =================================================================
// 3. COMPILER ERRORS (FOR TESTING EXPLAINER & AUTO-HEAL)
// =================================================================

void testCompilerErrors() {
    // Error 1: Missing semicolon
    int score = 100
    
    // Error 2: Wrong stream operator
    << "Checking stream operator\n";

    cout << "Test completed: " << score << endl;
}

int main() {
    cout << "=== Compiler Error Explainer & Optimizer Verification Suite ===" << endl;
    
    testBufferSecurity("Test");
    testFormatString("Testing system security\n");
    testDivisionByZero(50);
    testIntegerOverflow(10);

    vector<int> sample = {5, 2, 9, 1, 5, 6};
    vector<int> sorted = quadraticBubbleSort(sample);
    cout << "Sorted count: " << sorted.size() << endl;

    testCompilerErrors();
    return 0;
}
