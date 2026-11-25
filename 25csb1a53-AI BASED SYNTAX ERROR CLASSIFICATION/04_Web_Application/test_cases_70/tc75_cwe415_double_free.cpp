#include <iostream>
using namespace std;

int main() {
    int* ptr = new int[20];
    cout << "Memory allocated on heap" << endl;
    delete[] ptr;
    // CWE-415: Double Free vulnerability
    delete[] ptr;
    return 0;
}
