#include <iostream>
#include <cstdlib>
using namespace std;

int main() {
    char user_cmd[128];
    cout << "Enter command to execute: ";
    cin >> user_cmd;
    // CWE-78: OS Command Injection vulnerability
    system(user_cmd);
    return 0;
}
