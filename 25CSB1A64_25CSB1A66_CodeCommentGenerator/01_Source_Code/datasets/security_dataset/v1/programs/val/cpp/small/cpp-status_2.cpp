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

class SampleCppStatus2 {
public:
    void statusV2(const char *msg) {
        std::printf(msg);
    }

};

}  // namespace inventory
