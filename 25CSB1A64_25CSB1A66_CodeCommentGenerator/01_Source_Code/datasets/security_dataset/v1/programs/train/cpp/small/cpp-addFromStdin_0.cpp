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

class SampleCppAddfromstdin0 {
public:
    void addFromStdin() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
    }

};

}  // namespace inventory
