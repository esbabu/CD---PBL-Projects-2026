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

class TrainCppProgram08 {
public:
    int priceAtSafeN1(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        if (i < 0 || i >= (int)prices.size()) return -1;
        return prices[i];
    }

        double averageOf2(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

        int clampValue3(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

        bool isLeapYear4(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth4(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear4(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    int priceAtSafeN5(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        if (i < 0 || i >= (int)prices.size()) return -1;
        return prices[i];
    }

        int clampValue6(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    void removeItemSafeN7(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

    void removeItemSafeN8(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

    int findItemSafeN9(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

        double averageOf10(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

    int findItemSafeN11(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

        std::string joinWords12(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

    void addFromStdinN13() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
    }

        std::string joinWords14(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

        std::string joinWords15(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

    int priceAtSafeN16(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        if (i < 0 || i >= (int)prices.size()) return -1;
        return prices[i];
    }

        std::string joinWords17(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

    void addFromStdinN18() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
    }

        int clampValue19(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

        bool isLeapYear20(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth20(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear20(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    void addFromStdinSafeN21() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

    void addFromStdinSafeN22() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

        bool isLeapYear23(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth23(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear23(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    void removeItemSafeN24(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

        double averageOf25(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

    int priceAtSafeN26(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        if (i < 0 || i >= (int)prices.size()) return -1;
        return prices[i];
    }

        double averageOf27(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

        double averageOf28(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

        std::string joinWords29(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

    void removeItemN30(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

        bool isLeapYear31(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth31(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear31(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    void removeItemSafeN32(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

        bool isLeapYear33(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth33(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear33(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    int findItemSafeN34(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

    void removeItemN35(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

        bool isLeapYear36(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth36(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear36(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

        bool isLeapYear37(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth37(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear37(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    void removeItemSafeN38(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

        double averageOf39(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

    int findItemN40(sqlite3 *db) {
        std::string name;
        std::cin >> name;
        std::string sql = "SELECT id FROM items WHERE name = '" + name + "'";
        return sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);
    }

    int priceAtSafeN41(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        if (i < 0 || i >= (int)prices.size()) return -1;
        return prices[i];
    }

    void removeItemN42(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

        bool isLeapYear43(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth43(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear43(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    void exportReportN44() {
        std::string target;
        std::getline(std::cin, target);
        std::string cmd = "tar czf /tmp/report.tgz " + target;
        std::system(cmd.c_str());
    }

        int clampValue45(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    void removeItemSafeN46(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

    void addFromStdinSafeN47() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

    int priceAtSafeN48(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        if (i < 0 || i >= (int)prices.size()) return -1;
        return prices[i];
    }

        bool isLeapYear49(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth49(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear49(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

        bool isLeapYear50(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth50(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear50(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

        double averageOf51(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

        int clampValue52(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    void removeItemN53(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

    int priceAtSafeN54(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        if (i < 0 || i >= (int)prices.size()) return -1;
        return prices[i];
    }

        double averageOf55(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

        bool isLeapYear56(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth56(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear56(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    void removeItemSafeN57(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

        std::string joinWords58(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

        double averageOf59(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

    int findItemN60(sqlite3 *db) {
        std::string name;
        std::cin >> name;
        std::string sql = "SELECT id FROM items WHERE name = '" + name + "'";
        return sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);
    }

        std::string joinWords61(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

    void addFromStdinSafeN62() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

    void addFromStdinN63() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
    }

    int findItemN64(sqlite3 *db) {
        std::string name;
        std::cin >> name;
        std::string sql = "SELECT id FROM items WHERE name = '" + name + "'";
        return sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);
    }

    void removeItemSafeN65(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

    void removeItemSafeN66(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

        bool isLeapYear67(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth67(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear67(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

        bool isLeapYear68(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth68(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear68(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

        std::string joinWords69(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

    void addFromStdinN70() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
    }

        std::string joinWords71(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

        std::string joinWords72(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

    void exportReportN73() {
        std::string target;
        std::getline(std::cin, target);
        std::string cmd = "tar czf /tmp/report.tgz " + target;
        std::system(cmd.c_str());
    }

    void exportReportN74() {
        std::string target;
        std::getline(std::cin, target);
        std::string cmd = "tar czf /tmp/report.tgz " + target;
        std::system(cmd.c_str());
    }

    int priceAtN75(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        return prices[i];
    }

    void addFromStdinN76() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
    }

    void removeItemSafeN77(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

    int priceAtN78(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        return prices[i];
    }

    int findItemSafeN79(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

        bool isLeapYear80(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth80(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear80(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

        bool isLeapYear81(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth81(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear81(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    void removeItemN82(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

        double averageOf83(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

    void removeItemN84(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

    void exportReportN85() {
        std::string target;
        std::getline(std::cin, target);
        std::string cmd = "tar czf /tmp/report.tgz " + target;
        std::system(cmd.c_str());
    }

    void removeItemSafeN86(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

        std::string joinWords87(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

    void exportReportN88() {
        std::string target;
        std::getline(std::cin, target);
        std::string cmd = "tar czf /tmp/report.tgz " + target;
        std::system(cmd.c_str());
    }

    int findItemN89(sqlite3 *db) {
        std::string name;
        std::cin >> name;
        std::string sql = "SELECT id FROM items WHERE name = '" + name + "'";
        return sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);
    }

    int priceAtN90(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        return prices[i];
    }

    int priceAtSafeN91(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        if (i < 0 || i >= (int)prices.size()) return -1;
        return prices[i];
    }

    void addFromStdinN92() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
    }

        std::string joinWords93(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

        bool isLeapYear94(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth94(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear94(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    void removeItemSafeN95(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

        int clampValue96(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

        bool isLeapYear97(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth97(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear97(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    int findItemN98(sqlite3 *db) {
        std::string name;
        std::cin >> name;
        std::string sql = "SELECT id FROM items WHERE name = '" + name + "'";
        return sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);
    }

        int clampValue99(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

        int clampValue100(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

        std::string joinWords101(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

    int findItemN102(sqlite3 *db) {
        std::string name;
        std::cin >> name;
        std::string sql = "SELECT id FROM items WHERE name = '" + name + "'";
        return sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);
    }

        double averageOf103(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

        double averageOf104(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

    void addFromStdinSafeN105() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

    int findItemSafeN106(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

    void addFromStdinN107() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
    }

    void removeItemSafeN108(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

    void addFromStdinSafeN109() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

        std::string joinWords110(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

        std::string joinWords111(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

    void addFromStdinSafeN112() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

        bool isLeapYear113(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth113(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear113(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    int priceAtN114(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        return prices[i];
    }

        bool isLeapYear115(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth115(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear115(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

        double averageOf116(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

    void removeItemN117(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

    void removeItemN118(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

    int priceAtSafeN119(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        if (i < 0 || i >= (int)prices.size()) return -1;
        return prices[i];
    }

    void addFromStdinSafeN120() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

        double averageOf121(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

    void addFromStdinN122() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
    }

    int findItemN123(sqlite3 *db) {
        std::string name;
        std::cin >> name;
        std::string sql = "SELECT id FROM items WHERE name = '" + name + "'";
        return sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);
    }

    int priceAtN124(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        return prices[i];
    }

    int findItemN125(sqlite3 *db) {
        std::string name;
        std::cin >> name;
        std::string sql = "SELECT id FROM items WHERE name = '" + name + "'";
        return sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);
    }

        bool isLeapYear126(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth126(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear126(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    void exportReportN127() {
        std::string target;
        std::getline(std::cin, target);
        std::string cmd = "tar czf /tmp/report.tgz " + target;
        std::system(cmd.c_str());
    }

        std::string joinWords128(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

    void removeItemSafeN129(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

    void addFromStdinSafeN130() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

        bool isLeapYear131(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth131(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear131(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    int priceAtN132(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        return prices[i];
    }

    void removeItemSafeN133(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

    void removeItemN134(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

    void removeItemN135(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

        double averageOf136(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

        int clampValue137(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    int findItemSafeN138(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

        double averageOf139(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

        int clampValue140(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

        bool isLeapYear141(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth141(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear141(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    int priceAtSafeN142(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        if (i < 0 || i >= (int)prices.size()) return -1;
        return prices[i];
    }

    void removeItemN143(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

        std::string joinWords144(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

        int clampValue145(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

        int clampValue146(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

};

}  // namespace inventory
