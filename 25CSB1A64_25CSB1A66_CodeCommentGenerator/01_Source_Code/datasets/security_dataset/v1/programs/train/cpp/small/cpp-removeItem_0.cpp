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

class SampleCppRemoveitem0 {
public:
    void removeItem(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

};

}  // namespace inventory
