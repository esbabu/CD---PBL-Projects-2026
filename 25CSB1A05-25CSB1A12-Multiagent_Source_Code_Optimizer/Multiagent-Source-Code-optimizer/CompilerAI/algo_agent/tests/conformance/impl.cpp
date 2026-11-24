#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

int add(int a, int b) {
    return a + b;
}

std::vector<int> reverse_list(std::vector<int> xs) {
    std::reverse(xs.begin(), xs.end());
    return xs;
}

int raise_on_negative(int x) {
    if (x < 0) throw std::invalid_argument("negative");
    return x;
}

int mutates_argument(std::vector<int>& xs) {
    xs.push_back(99);
    return static_cast<int>(xs.size());
}

std::string prints_text(const std::string& s) {
    std::cout << s << std::endl;
    return s;
}

int infinite_loop(int x) {
    volatile int y = x;
    while (true) { y++; }
    return y;
}

int crashes_hard(int x) {
    (void)x;
    std::abort();
    return 0;
}

double returns_special_values(int x) {
    (void)x;
    return std::nan("");
}
