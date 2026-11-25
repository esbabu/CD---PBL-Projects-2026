// inventory_server: request handlers of a small C++ service. Vulnerable lines are marked "expect".
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

class Store {
public:
    void addFromStdin() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());                     // expect: SEC052
        std::puts(label);
    }

    void addFromStdinSafe() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

    void exportReport() {
        std::string target;
        std::getline(std::cin, target);
        std::string cmd = "tar czf /tmp/report.tgz " + target;
        std::system(cmd.c_str());                                      // expect: SEC002
    }

    int findItem(sqlite3 *db) {
        std::string name;
        std::cin >> name;
        std::string sql = "SELECT id FROM items WHERE name = '" + name + "'";
        return sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);   // expect: SEC005
    }

    int findItemSafe(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

    void openLog() {
        std::string file;
        std::cin >> file;
        std::ifstream in("/var/log/inventory/" + file);              // expect: SEC013
    }

    int priceAt(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        return prices[i];                                              // expect: SEC054
    }

    int priceAtSafe(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        if (i < 0 || i >= (int)prices.size()) return -1;
        return prices[i];
    }

    void removeItem(Item *item) {
        delete item;
        std::cout << item->name << std::endl;                          // expect: SEC056
    }

    void removeItemSafe(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

    void status(const char *msg) {
        std::printf(msg);                                              // expect: SEC026
    }

    void statusSafe(const char *msg) {
        std::printf("%s", msg);
    }
};

}  // namespace inventory

int main() {
    inventory::Store s;
    s.addFromStdin();
    return 0;
}
