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

class TrainCppProgram01 {
public:
        double averageOf1(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

    int findItemSafeN2(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

        double averageOf3(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

        int clampValue4(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

        std::string joinWords5(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

        bool isLeapYear6(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth6(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear6(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

        int clampValue7(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

        bool isLeapYear8(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth8(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear8(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

        int clampValue9(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

        int clampValue10(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

        double averageOf11(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

    int priceAtN12(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        return prices[i];
    }

    int findItemSafeN13(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

        int clampValue14(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

        int clampValue15(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    int findItemSafeN16(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

    void removeItemSafeN17(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

    void removeItemSafeN18(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

        bool isLeapYear19(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth19(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear19(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    int findItemSafeN20(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

    int findItemN21(sqlite3 *db) {
        std::string name;
        std::cin >> name;
        std::string sql = "SELECT id FROM items WHERE name = '" + name + "'";
        return sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);
    }

    void addFromStdinSafeN22() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

        int clampValue23(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    int priceAtSafeN24(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        if (i < 0 || i >= (int)prices.size()) return -1;
        return prices[i];
    }

        bool isLeapYear25(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth25(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear25(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    void addFromStdinSafeN26() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

    void addFromStdinSafeN27() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

    void addFromStdinSafeN28() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

        double averageOf29(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

    int priceAtSafeN30(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        if (i < 0 || i >= (int)prices.size()) return -1;
        return prices[i];
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

    void exportReportN32() {
        std::string target;
        std::getline(std::cin, target);
        std::string cmd = "tar czf /tmp/report.tgz " + target;
        std::system(cmd.c_str());
    }

        int clampValue33(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    void exportReportN34() {
        std::string target;
        std::getline(std::cin, target);
        std::string cmd = "tar czf /tmp/report.tgz " + target;
        std::system(cmd.c_str());
    }

        std::string joinWords35(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

        std::string joinWords36(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

    void exportReportN37() {
        std::string target;
        std::getline(std::cin, target);
        std::string cmd = "tar czf /tmp/report.tgz " + target;
        std::system(cmd.c_str());
    }

        bool isLeapYear38(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth38(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear38(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

        int clampValue39(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

        bool isLeapYear40(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth40(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear40(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

        double averageOf41(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

        std::string joinWords42(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

        std::string joinWords43(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

    int findItemSafeN44(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

    void addFromStdinN45() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
    }

    int findItemN46(sqlite3 *db) {
        std::string name;
        std::cin >> name;
        std::string sql = "SELECT id FROM items WHERE name = '" + name + "'";
        return sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);
    }

    void addFromStdinSafeN47() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

        bool isLeapYear48(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth48(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear48(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

        std::string joinWords49(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

    int findItemSafeN50(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

    int priceAtN51(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        return prices[i];
    }

        int clampValue52(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    void removeItemSafeN53(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

    void exportReportN54() {
        std::string target;
        std::getline(std::cin, target);
        std::string cmd = "tar czf /tmp/report.tgz " + target;
        std::system(cmd.c_str());
    }

    void exportReportN55() {
        std::string target;
        std::getline(std::cin, target);
        std::string cmd = "tar czf /tmp/report.tgz " + target;
        std::system(cmd.c_str());
    }

    void removeItemSafeN56(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

    int priceAtSafeN57(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        if (i < 0 || i >= (int)prices.size()) return -1;
        return prices[i];
    }

    int priceAtSafeN58(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        if (i < 0 || i >= (int)prices.size()) return -1;
        return prices[i];
    }

    int priceAtSafeN59(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        if (i < 0 || i >= (int)prices.size()) return -1;
        return prices[i];
    }

    int priceAtSafeN60(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        if (i < 0 || i >= (int)prices.size()) return -1;
        return prices[i];
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

        std::string joinWords62(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

    int priceAtSafeN63(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        if (i < 0 || i >= (int)prices.size()) return -1;
        return prices[i];
    }

        bool isLeapYear64(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth64(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear64(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

        int clampValue65(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    void removeItemN66(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

    int priceAtN67(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        return prices[i];
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

        bool isLeapYear69(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth69(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear69(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    void addFromStdinN70() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
    }

    void removeItemN71(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

        double averageOf72(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

        bool isLeapYear73(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth73(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear73(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    void addFromStdinSafeN74() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

        bool isLeapYear75(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth75(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear75(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

        int clampValue76(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

        bool isLeapYear77(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth77(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear77(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    int priceAtN78(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        return prices[i];
    }

    int priceAtSafeN79(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        if (i < 0 || i >= (int)prices.size()) return -1;
        return prices[i];
    }

        double averageOf80(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

        double averageOf81(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

    void removeItemSafeN82(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

        bool isLeapYear83(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth83(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear83(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

        int clampValue84(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    void addFromStdinN85() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
    }

    int findItemN86(sqlite3 *db) {
        std::string name;
        std::cin >> name;
        std::string sql = "SELECT id FROM items WHERE name = '" + name + "'";
        return sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);
    }

    void addFromStdinSafeN87() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

        std::string joinWords88(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

    int findItemSafeN89(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

        bool isLeapYear90(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth90(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear90(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    int findItemN91(sqlite3 *db) {
        std::string name;
        std::cin >> name;
        std::string sql = "SELECT id FROM items WHERE name = '" + name + "'";
        return sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);
    }

    int findItemN92(sqlite3 *db) {
        std::string name;
        std::cin >> name;
        std::string sql = "SELECT id FROM items WHERE name = '" + name + "'";
        return sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);
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

        int clampValue94(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

        std::string joinWords95(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

        int clampValue96(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

        int clampValue97(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    int findItemSafeN98(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

        double averageOf99(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

        std::string joinWords100(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
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

        std::string joinWords102(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

    void removeItemSafeN103(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

    void removeItemSafeN104(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

        std::string joinWords105(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

    void removeItemN106(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

    void removeItemSafeN107(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

    int findItemSafeN108(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

    void exportReportN109() {
        std::string target;
        std::getline(std::cin, target);
        std::string cmd = "tar czf /tmp/report.tgz " + target;
        std::system(cmd.c_str());
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

        int clampValue111(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

        bool isLeapYear112(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth112(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear112(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    int findItemSafeN113(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

        bool isLeapYear114(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth114(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear114(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

        std::string joinWords115(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

        std::string joinWords116(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

        double averageOf117(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

    void addFromStdinSafeN118() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

    int priceAtN119(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        return prices[i];
    }

        bool isLeapYear120(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth120(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear120(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    void exportReportN121() {
        std::string target;
        std::getline(std::cin, target);
        std::string cmd = "tar czf /tmp/report.tgz " + target;
        std::system(cmd.c_str());
    }

        std::string joinWords122(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

        bool isLeapYear123(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth123(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear123(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

};

}  // namespace inventory
