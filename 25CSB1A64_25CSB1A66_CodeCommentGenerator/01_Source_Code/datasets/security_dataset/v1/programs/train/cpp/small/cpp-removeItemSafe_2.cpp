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

class SampleCppRemoveitemsafe2 {
public:
    void removeItemSafeV2(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

};

}  // namespace inventory
