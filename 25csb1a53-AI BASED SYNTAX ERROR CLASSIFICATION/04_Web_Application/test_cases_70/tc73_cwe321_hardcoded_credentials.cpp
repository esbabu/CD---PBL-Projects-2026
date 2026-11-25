#include <iostream>
#include <cstring>
using namespace std;

int main() {
    // CWE-321: Use of Hardcoded Credentials
    const char* password = "AdminSuperSecretKey999!";
    char input_pass[32];
    cout << "Enter admin password: ";
    cin >> input_pass;
    if (strcmp(input_pass, password) == 0) {
        cout << "Access Granted to Secret Vault" << endl;
    }
    return 0;
}
