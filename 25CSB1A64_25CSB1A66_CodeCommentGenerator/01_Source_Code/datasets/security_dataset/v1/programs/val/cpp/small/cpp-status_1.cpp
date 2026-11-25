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

class SampleCppStatus1 {
public:
    void statusV1(const char *msg) {
        std::printf(msg);
    }

};

}  // namespace inventory
