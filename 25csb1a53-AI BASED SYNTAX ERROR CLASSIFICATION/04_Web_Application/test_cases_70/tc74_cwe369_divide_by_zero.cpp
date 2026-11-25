#include <iostream>
using namespace std;

int main() {
    int total_score = 500;
    // CWE-369: Divide By Zero
    int result = total_score / 0;
    cout << "Calculated result: " << result << endl;
    return 0;
}
