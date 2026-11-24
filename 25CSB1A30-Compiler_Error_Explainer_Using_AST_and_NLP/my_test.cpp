#include <iostream>
#include <vector>

using namespace std;

void processData() {
    // 1. Security vulnerability: Integer overflow (CWE-190)
    int maxVal = 2147483647;
    maxVal = maxVal + 1;

    // 2. Syntax error: Missing semicolon
    int totalCount = 100;
    cout << "Total count: " << totalCount << endl;

    // 3. Name resolution error: Undeclared variable
    int unknown_variable = 50;
    unknown_variable = 50;
    cout << "Value: " << unknown_variable << endl;


// 4. Suboptimal Big-O: O(n^2) nested loop bubble sort
}
void bubbleSort(vector<int>& arr) {
    for (size_t i = 0; i < arr.size(); ++i) {
        for (size_t j = 0; j < arr.size() - 1; ++j) {
            if (arr[j] > arr[j + 1]) {
                swap(arr[j], arr[j + 1]);
            }
        
    }
}

}
int main() {
    cout << "=== Compiler Error Explainer Live Test ===" << endl;
    processData();
    return 0;
}