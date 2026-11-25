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

class TrainCppProgram04 {
public:
    int findItemN1(sqlite3 *db) {
        std::string name;
        std::cin >> name;
        std::string sql = "SELECT id FROM items WHERE name = '" + name + "'";
        return sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);
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

    void addFromStdinN3() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
    }

        int clampValue4(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

        bool isLeapYear5(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth5(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear5(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    int findItemN6(sqlite3 *db) {
        std::string name;
        std::cin >> name;
        std::string sql = "SELECT id FROM items WHERE name = '" + name + "'";
        return sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);
    }

    void addFromStdinN7() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
    }

    void addFromStdinN8() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
    }

    int findItemN9(sqlite3 *db) {
        std::string name;
        std::cin >> name;
        std::string sql = "SELECT id FROM items WHERE name = '" + name + "'";
        return sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);
    }

    void addFromStdinN10() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
    }

        int clampValue11(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
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

        double averageOf13(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

    void addFromStdinSafeN14() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

    int findItemSafeN15(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

        bool isLeapYear16(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth16(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear16(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    void addFromStdinSafeN17() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

        int clampValue18(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    void removeItemN19(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

        double averageOf20(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

        std::string joinWords21(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

    int priceAtSafeN22(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        if (i < 0 || i >= (int)prices.size()) return -1;
        return prices[i];
    }

        int clampValue23(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

        bool isLeapYear24(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth24(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear24(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

        int clampValue25(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    void removeItemSafeN26(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

        int clampValue27(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    int priceAtN28(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        return prices[i];
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

    void addFromStdinN30() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
    }

        std::string joinWords31(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

    int findItemSafeN32(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

        int clampValue33(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

        int clampValue34(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

        int clampValue35(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    int findItemN36(sqlite3 *db) {
        std::string name;
        std::cin >> name;
        std::string sql = "SELECT id FROM items WHERE name = '" + name + "'";
        return sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);
    }

        std::string joinWords37(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

    void removeItemN38(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

    void addFromStdinSafeN39() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

    int priceAtN40(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        return prices[i];
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

    void removeItemN42(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

        double averageOf43(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

        std::string joinWords44(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

        int clampValue45(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    void removeItemN46(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

    int findItemN47(sqlite3 *db) {
        std::string name;
        std::cin >> name;
        std::string sql = "SELECT id FROM items WHERE name = '" + name + "'";
        return sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);
    }

    int findItemN48(sqlite3 *db) {
        std::string name;
        std::cin >> name;
        std::string sql = "SELECT id FROM items WHERE name = '" + name + "'";
        return sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);
    }

    void addFromStdinSafeN49() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

        double averageOf50(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

    int priceAtSafeN51(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        if (i < 0 || i >= (int)prices.size()) return -1;
        return prices[i];
    }

    void removeItemSafeN52(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

        bool isLeapYear53(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth53(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear53(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    int findItemN54(sqlite3 *db) {
        std::string name;
        std::cin >> name;
        std::string sql = "SELECT id FROM items WHERE name = '" + name + "'";
        return sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);
    }

        bool isLeapYear55(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth55(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear55(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    int priceAtN56(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        return prices[i];
    }

    void exportReportN57() {
        std::string target;
        std::getline(std::cin, target);
        std::string cmd = "tar czf /tmp/report.tgz " + target;
        std::system(cmd.c_str());
    }

    void exportReportN58() {
        std::string target;
        std::getline(std::cin, target);
        std::string cmd = "tar czf /tmp/report.tgz " + target;
        std::system(cmd.c_str());
    }

        int clampValue59(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    void addFromStdinSafeN60() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

        double averageOf61(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
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

    void addFromStdinN63() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
    }

    int findItemSafeN64(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

    void exportReportN65() {
        std::string target;
        std::getline(std::cin, target);
        std::string cmd = "tar czf /tmp/report.tgz " + target;
        std::system(cmd.c_str());
    }

    int findItemSafeN66(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

    int priceAtSafeN67(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        if (i < 0 || i >= (int)prices.size()) return -1;
        return prices[i];
    }

    int priceAtN68(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        return prices[i];
    }

    void removeItemN69(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

        double averageOf70(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

        double averageOf71(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

        bool isLeapYear72(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth72(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear72(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

        double averageOf73(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

    void exportReportN74() {
        std::string target;
        std::getline(std::cin, target);
        std::string cmd = "tar czf /tmp/report.tgz " + target;
        std::system(cmd.c_str());
    }

    int findItemN75(sqlite3 *db) {
        std::string name;
        std::cin >> name;
        std::string sql = "SELECT id FROM items WHERE name = '" + name + "'";
        return sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);
    }

        std::string joinWords76(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

        int clampValue77(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    void exportReportN78() {
        std::string target;
        std::getline(std::cin, target);
        std::string cmd = "tar czf /tmp/report.tgz " + target;
        std::system(cmd.c_str());
    }

    int priceAtN79(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        return prices[i];
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

        bool isLeapYear82(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth82(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear82(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

        std::string joinWords83(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

        int clampValue84(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    void removeItemSafeN85(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

        double averageOf86(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

    void exportReportN87() {
        std::string target;
        std::getline(std::cin, target);
        std::string cmd = "tar czf /tmp/report.tgz " + target;
        std::system(cmd.c_str());
    }

    void addFromStdinN88() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
    }

        int clampValue89(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

        double averageOf90(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

        int clampValue91(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    int priceAtN92(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        return prices[i];
    }

    void exportReportN93() {
        std::string target;
        std::getline(std::cin, target);
        std::string cmd = "tar czf /tmp/report.tgz " + target;
        std::system(cmd.c_str());
    }

    void removeItemSafeN94(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

        int clampValue95(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    void removeItemN96(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

    void removeItemN97(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

        std::string joinWords98(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

    int priceAtSafeN99(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        if (i < 0 || i >= (int)prices.size()) return -1;
        return prices[i];
    }

        int clampValue100(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    int findItemN101(sqlite3 *db) {
        std::string name;
        std::cin >> name;
        std::string sql = "SELECT id FROM items WHERE name = '" + name + "'";
        return sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);
    }

    void addFromStdinN102() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
    }

        std::string joinWords103(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

    void exportReportN104() {
        std::string target;
        std::getline(std::cin, target);
        std::string cmd = "tar czf /tmp/report.tgz " + target;
        std::system(cmd.c_str());
    }

    int findItemSafeN105(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

    int priceAtSafeN106(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        if (i < 0 || i >= (int)prices.size()) return -1;
        return prices[i];
    }

        int clampValue107(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

        double averageOf108(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

    void addFromStdinN109() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
    }

        double averageOf110(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

    void addFromStdinSafeN111() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
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

        double averageOf114(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

    void removeItemSafeN115(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

    int priceAtSafeN116(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        if (i < 0 || i >= (int)prices.size()) return -1;
        return prices[i];
    }

    void exportReportN117() {
        std::string target;
        std::getline(std::cin, target);
        std::string cmd = "tar czf /tmp/report.tgz " + target;
        std::system(cmd.c_str());
    }

        int clampValue118(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

        bool isLeapYear119(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth119(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear119(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    void removeItemSafeN120(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

        std::string joinWords121(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

    void addFromStdinN122() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
    }

    int priceAtSafeN123(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        if (i < 0 || i >= (int)prices.size()) return -1;
        return prices[i];
    }

    void addFromStdinSafeN124() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

    void removeItemSafeN125(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

    int findItemSafeN126(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

    void removeItemSafeN127(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

    void addFromStdinSafeN128() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

    int findItemN129(sqlite3 *db) {
        std::string name;
        std::cin >> name;
        std::string sql = "SELECT id FROM items WHERE name = '" + name + "'";
        return sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);
    }

        double averageOf130(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
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

    void exportReportN132() {
        std::string target;
        std::getline(std::cin, target);
        std::string cmd = "tar czf /tmp/report.tgz " + target;
        std::system(cmd.c_str());
    }

    int findItemN133(sqlite3 *db) {
        std::string name;
        std::cin >> name;
        std::string sql = "SELECT id FROM items WHERE name = '" + name + "'";
        return sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);
    }

    void removeItemN134(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

        double averageOf135(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

        int clampValue136(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    int findItemSafeN137(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

        bool isLeapYear138(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth138(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear138(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    void removeItemN139(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

    int findItemSafeN140(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

    void addFromStdinSafeN141() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

    void removeItemSafeN142(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

    void exportReportN143() {
        std::string target;
        std::getline(std::cin, target);
        std::string cmd = "tar czf /tmp/report.tgz " + target;
        std::system(cmd.c_str());
    }

    void exportReportN144() {
        std::string target;
        std::getline(std::cin, target);
        std::string cmd = "tar czf /tmp/report.tgz " + target;
        std::system(cmd.c_str());
    }

        double averageOf145(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

        double averageOf146(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

        double averageOf147(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

        bool isLeapYear148(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth148(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear148(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    void removeItemN149(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

    void removeItemN150(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

    void removeItemN151(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

        std::string joinWords152(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

        int clampValue153(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

        int clampValue154(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

        double averageOf155(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

    int findItemN156(sqlite3 *db) {
        std::string name;
        std::cin >> name;
        std::string sql = "SELECT id FROM items WHERE name = '" + name + "'";
        return sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);
    }

    int findItemSafeN157(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

    void removeItemSafeN158(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

    void addFromStdinN159() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
    }

        int clampValue160(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    void removeItemN161(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

    int priceAtN162(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        return prices[i];
    }

    int findItemN163(sqlite3 *db) {
        std::string name;
        std::cin >> name;
        std::string sql = "SELECT id FROM items WHERE name = '" + name + "'";
        return sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);
    }

        int clampValue164(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

        bool isLeapYear165(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth165(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear165(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    int priceAtSafeN166(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        if (i < 0 || i >= (int)prices.size()) return -1;
        return prices[i];
    }

    void addFromStdinN167() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
    }

        int clampValue168(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

        int clampValue169(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    void addFromStdinN170() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
    }

    void addFromStdinN171() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
    }

};

}  // namespace inventory
