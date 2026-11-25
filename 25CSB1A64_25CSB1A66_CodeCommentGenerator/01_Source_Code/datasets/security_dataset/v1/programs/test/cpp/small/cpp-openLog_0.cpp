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

class SampleCppOpenlog0 {
public:
    void openLog() {
        std::string file;
        std::cin >> file;
        std::ifstream in("/var/log/inventory/" + file);
    }

};

}  // namespace inventory
