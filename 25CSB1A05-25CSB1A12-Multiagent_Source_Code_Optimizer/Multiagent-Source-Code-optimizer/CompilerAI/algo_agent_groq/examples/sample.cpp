#include <iostream>
#include <vector>

bool contains(const std::vector<int>& values, int target) {
    for (int value : values) {
        if (value == target) {
            return true;
        }
    }
    return false;
}

int main() {
    const std::vector<int> values{4, 8, 15, 16, 23, 42};
    std::cout << std::boolalpha << contains(values, 15) << '\n';
    return 0;
}
