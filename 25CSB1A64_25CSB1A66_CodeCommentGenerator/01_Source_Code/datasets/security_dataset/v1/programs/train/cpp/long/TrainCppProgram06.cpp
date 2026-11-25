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

class TrainCppProgram06 {
public:
    int priceAtN1(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        return prices[i];
    }

    int findItemN2(sqlite3 *db) {
        std::string name;
        std::cin >> name;
        std::string sql = "SELECT id FROM items WHERE name = '" + name + "'";
        return sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);
    }

    void removeItemN3(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

    int findItemSafeN4(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
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

    void addFromStdinN7() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
    }

        int clampValue8(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    int priceAtN9(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        return prices[i];
    }

    void removeItemN10(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

    void addFromStdinN11() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
    }

    int findItemSafeN12(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

        int clampValue13(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

        double averageOf14(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

    int findItemN15(sqlite3 *db) {
        std::string name;
        std::cin >> name;
        std::string sql = "SELECT id FROM items WHERE name = '" + name + "'";
        return sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);
    }

    int priceAtSafeN16(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        if (i < 0 || i >= (int)prices.size()) return -1;
        return prices[i];
    }

    int findItemSafeN17(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

    int findItemSafeN18(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

        double averageOf19(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

    int priceAtN20(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        return prices[i];
    }

        bool isLeapYear21(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth21(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear21(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    int priceAtN22(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        return prices[i];
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

    int findItemSafeN26(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

        std::string joinWords27(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

        bool isLeapYear28(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth28(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear28(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

        int clampValue29(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
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

        bool isLeapYear32(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth32(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear32(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

        int clampValue33(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    void addFromStdinSafeN34() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

    int findItemN35(sqlite3 *db) {
        std::string name;
        std::cin >> name;
        std::string sql = "SELECT id FROM items WHERE name = '" + name + "'";
        return sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);
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

        double averageOf38(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

        int clampValue39(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    void removeItemSafeN40(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

        bool isLeapYear41(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth41(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear41(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
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

    int priceAtN43(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        return prices[i];
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

    int findItemSafeN45(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

        std::string joinWords46(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

    void exportReportN47() {
        std::string target;
        std::getline(std::cin, target);
        std::string cmd = "tar czf /tmp/report.tgz " + target;
        std::system(cmd.c_str());
    }

        double averageOf48(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
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

        bool isLeapYear51(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth51(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear51(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

        double averageOf52(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

        double averageOf53(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

    void addFromStdinN54() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
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

    void exportReportN56() {
        std::string target;
        std::getline(std::cin, target);
        std::string cmd = "tar czf /tmp/report.tgz " + target;
        std::system(cmd.c_str());
    }

    void addFromStdinSafeN57() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

    void addFromStdinSafeN58() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

        std::string joinWords59(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

        bool isLeapYear60(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth60(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear60(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    void removeItemN61(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

        bool isLeapYear62(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth62(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear62(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

        bool isLeapYear63(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth63(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear63(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    void addFromStdinN64() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
    }

    void addFromStdinN65() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
    }

        bool isLeapYear66(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth66(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear66(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    void removeItemN67(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

    void exportReportN68() {
        std::string target;
        std::getline(std::cin, target);
        std::string cmd = "tar czf /tmp/report.tgz " + target;
        std::system(cmd.c_str());
    }

    int priceAtN69(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        return prices[i];
    }

    int findItemN70(sqlite3 *db) {
        std::string name;
        std::cin >> name;
        std::string sql = "SELECT id FROM items WHERE name = '" + name + "'";
        return sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);
    }

    int priceAtN71(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        return prices[i];
    }

    int priceAtSafeN72(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        if (i < 0 || i >= (int)prices.size()) return -1;
        return prices[i];
    }

    void addFromStdinSafeN73() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

        std::string joinWords74(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

        std::string joinWords75(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
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

    int findItemSafeN77(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

        double averageOf78(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

    int findItemSafeN79(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

        std::string joinWords80(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

        int clampValue81(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

        std::string joinWords82(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

    int priceAtN83(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        return prices[i];
    }

    void exportReportN84() {
        std::string target;
        std::getline(std::cin, target);
        std::string cmd = "tar czf /tmp/report.tgz " + target;
        std::system(cmd.c_str());
    }

    void addFromStdinSafeN85() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

    void exportReportN86() {
        std::string target;
        std::getline(std::cin, target);
        std::string cmd = "tar czf /tmp/report.tgz " + target;
        std::system(cmd.c_str());
    }

        int clampValue87(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

        double averageOf88(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

        double averageOf89(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
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

        double averageOf91(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

    int priceAtSafeN92(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        if (i < 0 || i >= (int)prices.size()) return -1;
        return prices[i];
    }

        bool isLeapYear93(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth93(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear93(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    int findItemSafeN94(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

    int findItemN95(sqlite3 *db) {
        std::string name;
        std::cin >> name;
        std::string sql = "SELECT id FROM items WHERE name = '" + name + "'";
        return sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);
    }

        double averageOf96(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

    void removeItemSafeN97(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

        int clampValue98(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
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

    void removeItemN100(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
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

        double averageOf102(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
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

    void removeItemN104(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

    void removeItemSafeN105(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

        bool isLeapYear106(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth106(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear106(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

        bool isLeapYear107(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth107(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear107(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    int priceAtN108(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        return prices[i];
    }

        bool isLeapYear109(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth109(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear109(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
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

    void removeItemN111(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

    void addFromStdinSafeN112() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

        std::string joinWords113(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

        std::string joinWords114(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
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

    void removeItemSafeN116(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

        std::string joinWords117(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

        int clampValue118(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    int findItemSafeN119(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

    int priceAtN120(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        return prices[i];
    }

    void removeItemN121(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

        int clampValue122(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    void removeItemSafeN123(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

    void addFromStdinN124() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
    }

        double averageOf125(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

        double averageOf126(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

        double averageOf127(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

        int clampValue128(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    int priceAtSafeN129(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        if (i < 0 || i >= (int)prices.size()) return -1;
        return prices[i];
    }

        std::string joinWords130(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

    void exportReportN131() {
        std::string target;
        std::getline(std::cin, target);
        std::string cmd = "tar czf /tmp/report.tgz " + target;
        std::system(cmd.c_str());
    }

        std::string joinWords132(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

};

}  // namespace inventory
