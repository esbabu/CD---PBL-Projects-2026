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

class TrainCppProgram02 {
public:
        int clampValue1(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

        bool isLeapYear2(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth2(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear2(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

        std::string joinWords3(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

        double averageOf4(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

        int clampValue5(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    int findItemSafeN6(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

    int priceAtN7(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        return prices[i];
    }

        double averageOf8(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

    void addFromStdinSafeN9() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

    void removeItemN10(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
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

    void exportReportN13() {
        std::string target;
        std::getline(std::cin, target);
        std::string cmd = "tar czf /tmp/report.tgz " + target;
        std::system(cmd.c_str());
    }

        bool isLeapYear14(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth14(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear14(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

        double averageOf15(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

        std::string joinWords16(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

    void addFromStdinSafeN17() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

    void exportReportN18() {
        std::string target;
        std::getline(std::cin, target);
        std::string cmd = "tar czf /tmp/report.tgz " + target;
        std::system(cmd.c_str());
    }

    void removeItemSafeN19(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

    void removeItemSafeN20(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

    void removeItemSafeN21(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

    void removeItemSafeN22(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

        double averageOf23(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

    void removeItemSafeN24(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

        int clampValue25(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    void removeItemN26(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
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

    void removeItemN28(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

    void removeItemSafeN29(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

        double averageOf30(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

    void removeItemN31(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

        int clampValue32(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
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

    void removeItemN34(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

    int priceAtN35(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        return prices[i];
    }

        double averageOf36(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

    void removeItemN37(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

    void exportReportN38() {
        std::string target;
        std::getline(std::cin, target);
        std::string cmd = "tar czf /tmp/report.tgz " + target;
        std::system(cmd.c_str());
    }

    void addFromStdinSafeN39() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

        double averageOf40(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
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

    void addFromStdinN42() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
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

    void addFromStdinSafeN44() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

        double averageOf45(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

        int clampValue46(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    void addFromStdinSafeN47() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

        int clampValue48(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

        double averageOf49(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

        int clampValue50(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    int findItemN51(sqlite3 *db) {
        std::string name;
        std::cin >> name;
        std::string sql = "SELECT id FROM items WHERE name = '" + name + "'";
        return sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);
    }

    void addFromStdinN52() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
    }

    void addFromStdinN53() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
    }

    void addFromStdinSafeN54() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

        int clampValue55(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

        std::string joinWords56(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

    void addFromStdinSafeN57() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

    void exportReportN58() {
        std::string target;
        std::getline(std::cin, target);
        std::string cmd = "tar czf /tmp/report.tgz " + target;
        std::system(cmd.c_str());
    }

    void addFromStdinSafeN59() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

        int clampValue60(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    int priceAtN61(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        return prices[i];
    }

    void exportReportN62() {
        std::string target;
        std::getline(std::cin, target);
        std::string cmd = "tar czf /tmp/report.tgz " + target;
        std::system(cmd.c_str());
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

    int priceAtSafeN64(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        if (i < 0 || i >= (int)prices.size()) return -1;
        return prices[i];
    }

    void exportReportN65() {
        std::string target;
        std::getline(std::cin, target);
        std::string cmd = "tar czf /tmp/report.tgz " + target;
        std::system(cmd.c_str());
    }

        std::string joinWords66(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

    void addFromStdinN67() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
    }

        double averageOf68(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

    int priceAtSafeN69(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        if (i < 0 || i >= (int)prices.size()) return -1;
        return prices[i];
    }

    int priceAtN70(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        return prices[i];
    }

    void removeItemSafeN71(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
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

    int findItemSafeN73(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

        bool isLeapYear74(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth74(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear74(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

        int clampValue75(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

        double averageOf76(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

        double averageOf77(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

    int priceAtN78(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        return prices[i];
    }

        int clampValue79(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    void addFromStdinSafeN80() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

        int clampValue81(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    void addFromStdinN82() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
    }

    int findItemSafeN83(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

        std::string joinWords84(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

    int findItemN85(sqlite3 *db) {
        std::string name;
        std::cin >> name;
        std::string sql = "SELECT id FROM items WHERE name = '" + name + "'";
        return sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);
    }

        bool isLeapYear86(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth86(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear86(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

        int clampValue87(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    int priceAtSafeN88(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        if (i < 0 || i >= (int)prices.size()) return -1;
        return prices[i];
    }

        int clampValue89(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
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

    void addFromStdinN91() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
    }

        bool isLeapYear92(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth92(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear92(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

        double averageOf93(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

    void addFromStdinSafeN94() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

        int clampValue95(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

        std::string joinWords96(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

        int clampValue97(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
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

        std::string joinWords99(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

        bool isLeapYear100(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth100(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear100(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    void removeItemSafeN101(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
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

        int clampValue103(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

        std::string joinWords104(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

        int clampValue105(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    int priceAtSafeN106(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        if (i < 0 || i >= (int)prices.size()) return -1;
        return prices[i];
    }

    void removeItemSafeN107(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

        std::string joinWords108(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

        std::string joinWords109(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

    int findItemSafeN110(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

    void addFromStdinSafeN111() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

    void addFromStdinN112() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
    }

    void removeItemSafeN113(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
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

    void removeItemN116(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

    int findItemN117(sqlite3 *db) {
        std::string name;
        std::cin >> name;
        std::string sql = "SELECT id FROM items WHERE name = '" + name + "'";
        return sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);
    }

    int priceAtN118(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        return prices[i];
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

    int priceAtSafeN121(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        if (i < 0 || i >= (int)prices.size()) return -1;
        return prices[i];
    }

    void addFromStdinN122() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
    }

    void addFromStdinSafeN123() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

    int findItemN124(sqlite3 *db) {
        std::string name;
        std::cin >> name;
        std::string sql = "SELECT id FROM items WHERE name = '" + name + "'";
        return sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);
    }

    void removeItemN125(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
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

        bool isLeapYear127(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth127(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear127(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
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

    void addFromStdinSafeN129() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

    void addFromStdinSafeN130() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

    void addFromStdinSafeN131() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

        double averageOf132(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

        bool isLeapYear133(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth133(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear133(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

        bool isLeapYear134(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth134(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear134(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
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

    void addFromStdinSafeN136() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

        int clampValue137(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    void addFromStdinN138() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
    }

        std::string joinWords139(const std::vector<std::string> &words, const std::string &sep) {
            std::string out;
            for (size_t i = 0; i < words.size(); ++i) {
                if (i > 0) {
                    out += sep;
                }
                out += words[i];
            }
            return out;
        }

        bool isLeapYear140(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth140(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear140(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    void removeItemN141(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

    void exportReportN142() {
        std::string target;
        std::getline(std::cin, target);
        std::string cmd = "tar czf /tmp/report.tgz " + target;
        std::system(cmd.c_str());
    }

        int clampValue143(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
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

    void removeItemSafeN146(Item *item) {
        std::string name = item->name;
        delete item;
        std::cout << name << std::endl;
    }

    int findItemSafeN147(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

    int priceAtSafeN148(const std::vector<int> &prices) {
        int i;
        std::cin >> i;
        if (i < 0 || i >= (int)prices.size()) return -1;
        return prices[i];
    }

    void addFromStdinN149() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
    }

        int clampValue150(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

        int clampValue151(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
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

    int findItemSafeN153(sqlite3 *db) {
        sqlite3_stmt *stmt;
        sqlite3_prepare_v2(db, "SELECT id FROM items WHERE name = ?", -1, &stmt, nullptr);
        return sqlite3_step(stmt);
    }

        int clampValue154(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    void removeItemN155(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

        bool isLeapYear156(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth156(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear156(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    void addFromStdinSafeN157() {
        std::string name;
        std::cin >> name;
        char label[32];
        std::snprintf(label, sizeof label, "item:%s", name.c_str());
        std::puts(label);
    }

        double averageOf158(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

    void exportReportN159() {
        std::string target;
        std::getline(std::cin, target);
        std::string cmd = "tar czf /tmp/report.tgz " + target;
        std::system(cmd.c_str());
    }

        double averageOf160(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

        bool isLeapYear161(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth161(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear161(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

        bool isLeapYear162(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth162(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear162(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

        int clampValue163(int value, int low, int high) {
            if (value < low) {
                return low;
            }
            return value > high ? high : value;
        }

    void addFromStdinN164() {
        std::string name;
        std::cin >> name;
        char label[32];
        sprintf(label, "item:%s", name.c_str());
        std::puts(label);
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

        double averageOf166(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

    void removeItemN167(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

        bool isLeapYear168(int year) {
            return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
        }

        int daysInMonth168(int year, int month) {
            switch (month) {
            case 2:
                return isLeapYear168(year) ? 29 : 28;
            case 4: case 6: case 9: case 11:
                return 30;
            default:
                return 31;
            }
        }

    void removeItemN169(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

    void removeItemN170(Item *item) {
        delete item;
        std::cout << item->name << std::endl;
    }

        double averageOf171(const std::vector<int> &values) {
            if (values.empty()) {
                return 0.0;
            }
            long total = 0;
            for (int v : values) {
                total += v;
            }
            return static_cast<double>(total) / values.size();
        }

    int findItemN172(sqlite3 *db) {
        std::string name;
        std::cin >> name;
        std::string sql = "SELECT id FROM items WHERE name = '" + name + "'";
        return sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);
    }

};

}  // namespace inventory
