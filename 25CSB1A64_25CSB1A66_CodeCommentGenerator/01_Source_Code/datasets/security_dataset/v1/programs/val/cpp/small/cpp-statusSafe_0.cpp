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

class SampleCppStatussafe0 {
public:
    void statusSafe(const char *msg) {
        std::printf("%s", msg);
    }

};

}  // namespace inventory
