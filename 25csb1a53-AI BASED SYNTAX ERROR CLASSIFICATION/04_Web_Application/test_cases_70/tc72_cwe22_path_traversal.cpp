#include <iostream>
#include <fstream>
using namespace std;

int main() {
    char filename[64];
    cout << "Enter file to open: ";
    cin >> filename;
    // CWE-22: Path Traversal vulnerability
    ifstream file(filename);
    if (file.is_open()) {
        cout << "File opened successfully" << endl;
        file.close();
    }
    return 0;
}
