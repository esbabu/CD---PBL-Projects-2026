#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>
#include <sqlite3.h>

namespace inventory {

class Item {
public:
    int id;
    std::string name;
};

class SampleCppPriceat0 {
public:
    int priceAt(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        return prices[i];
    }

};

}  // namespace inventory
