// vulnerable_samples.cpp
// Intentionally vulnerable and inefficient code used as a TEST INPUT for a
// static analysis / optimization tool. Never use any of this in real software.
// Ground-truth labels: [CWE-xxx] = vulnerability, [OPT-xx] = optimization chance.
// Build (warnings expected):  g++ -std=c++17 -O0 -w vulnerable_samples.cpp -o vs
 
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <map>
#include <cstring>
#include <cstdio>
#include <cstdlib>
#include <ctime>
#include <cmath>
#include <algorithm>
#include <unistd.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <alloca.h>
 
using namespace std;
 
#define BUF_SIZE 16
#define MAX_USERS 8
#define SECRET_KEY "admin123"          // [CWE-798] hard-coded credential
#define DB_PASSWORD "P@ssw0rd!"         // [CWE-798] hard-coded credential
 
// ---------------------------------------------------------------
// SECTION 1: buffer overflows
// ---------------------------------------------------------------
 
void copy_name(const char *input) {
    char name[BUF_SIZE];
    strcpy(name, input);                // [CWE-121] stack overflow, no bounds check
    printf("Name: %s\n", name);
}
 
void join_strings(const char *a, const char *b) {
    char out[BUF_SIZE];
    strcpy(out, a);                     // [CWE-121]
    strcat(out, b);                     // [CWE-121] strcat unbounded
    puts(out);
}
 
void read_line_unsafe() {
    char line[BUF_SIZE];
    printf("Enter text: ");
    scanf("%s", line);                  // [CWE-120] unbounded scanf
    printf("You typed %s\n", line);
}
 
void format_into_buffer(int id, const char *user) {
    char msg[32];
    sprintf(msg, "User %d is %s", id, user);   // [CWE-120] sprintf overflow
    puts(msg);
}
 
void off_by_one() {
    int arr[10];
    for (int i = 0; i <= 10; i++) {     // [CWE-193] off-by-one write
        arr[i] = i * 2;
    }
    printf("%d\n", arr[9]);
}
 
void heap_overflow(const char *src) {
    char *buf = (char *)malloc(8);
    memcpy(buf, src, strlen(src) + 1);  // [CWE-122] heap overflow
    printf("%s\n", buf);
    free(buf);
}
 
// ---------------------------------------------------------------
// SECTION 2: format string problems
// ---------------------------------------------------------------
 
void log_message(const char *user_msg) {
    printf(user_msg);                   // [CWE-134] user data as format string
    printf("\n");
}
 
void log_to_file(const char *fname, const char *msg) {
    FILE *f = fopen(fname, "a");
    fprintf(f, msg);                    // [CWE-134] and f is never checked for NULL [CWE-476]
    fclose(f);
}
 
// ---------------------------------------------------------------
// SECTION 3: integer problems
// ---------------------------------------------------------------
 
int add_sizes(int a, int b) {
    return a + b;                       // [CWE-190] signed overflow, undefined behavior
}
 
void alloc_array(int count) {
    int *p = (int *)malloc(count * sizeof(int));   // [CWE-190] multiplication may wrap
    for (int i = 0; i < count; i++) p[i] = i;
    free(p);
}
 
unsigned int sub_unsigned(unsigned int a, unsigned int b) {
    return a - b;                       // [CWE-191] unsigned wraparound
}
 
// ---------------------------------------------------------------
// SECTION 4: memory management bugs
// ---------------------------------------------------------------
 
void use_after_free() {
    char *p = (char *)malloc(32);
    strcpy(p, "hello");
    free(p);
    printf("%s\n", p);                  // [CWE-416] use after free
}
 
void double_free(int flag) {
    char *p = (char *)malloc(16);
    if (flag) free(p);
    free(p);                            // [CWE-415] double free when flag != 0
}
 
void memory_leak(int n) {
    for (int i = 0; i < n; i++) {
        char *tmp = new char[256];      // [CWE-401] leaked on every iteration
        sprintf(tmp, "item %d", i);
    }
}
 
void leak_on_error(const char *path) {
    char *buf = (char *)malloc(1024);
    FILE *f = fopen(path, "r");
    if (!f) return;                     // [CWE-401] buf leaked on this path
    fread(buf, 1, 1024, f);
    fclose(f);
    free(buf);
}
 
char *return_stack_address() {
    char local[32];
    strcpy(local, "temporary");
    return local;                       // [CWE-562] returns address of local
}
 
// ---------------------------------------------------------------
// SECTION 5: injection, file and OS issues
// ---------------------------------------------------------------
 
void run_ping(const char *host) {
    char cmd[128];
    sprintf(cmd, "ping -c 1 %s", host); // [CWE-78] command injection + [CWE-120]
    system(cmd);
}
 
void list_dir(const char *dir) {
    string cmd = string("ls -l ") + dir;
    system(cmd.c_str());                // [CWE-78] OS command injection
}
 
void read_user_file(const char *name) {
    char path[128];
    sprintf(path, "/var/data/%s", name); // [CWE-22] path traversal ("../../etc/passwd")
    FILE *f = fopen(path, "r");
    if (f) {
        char c;
        while ((c = fgetc(f)) != EOF) putchar(c);
        fclose(f);
    }
}
 
void check_then_open(const char *path) {
    if (access(path, W_OK) == 0) {      // [CWE-367] TOCTOU race
        FILE *f = fopen(path, "w");
        if (f) { fputs("data", f); fclose(f); }
    }
}
 
// ---------------------------------------------------------------
// SECTION 6: crypto, randomness, authentication
// ---------------------------------------------------------------
 
int generate_token() {
    srand(time(NULL));                  // [CWE-338] predictable seed
    return rand();                      // [CWE-338] weak PRNG for a security token
}
 
bool check_password(const char *input) {
    return strcmp(input, DB_PASSWORD) == 0;   // [CWE-208] timing side channel
}
 
bool check_token(const char *a, const char *b, int n) {
    for (int i = 0; i < n; i++) {
        if (a[i] != b[i]) return false; // [CWE-208] early exit leaks position of mismatch
    }
    return true;
}
 
bool login(const char *user, const char *pass) {
    if (strcmp(user, "admin") == 0) {   // [CWE-798] hard-coded admin account
        return strcmp(pass, SECRET_KEY) == 0;
    }
    return false;
}
 
// ---------------------------------------------------------------
// SECTION 7: concurrency / misc
// ---------------------------------------------------------------
 
int global_counter = 0;
 
void increment_counter() {
    global_counter++;                   // [CWE-362] unsynchronized shared variable
}
 
void switch_fallthrough(int level) {
    switch (level) {
        case 1: puts("low");            // [CWE-484] missing break
        case 2: puts("medium");
        case 3: puts("high"); break;
        default: puts("unknown");
    }
}
 
// ---------------------------------------------------------------
// SECTION 8: OPTIMIZATION OPPORTUNITIES
// ---------------------------------------------------------------
 
int fib_slow(int n) {                   // [OPT-01] exponential recursion, use iteration/memo
    if (n <= 1) return n;
    return fib_slow(n - 1) + fib_slow(n - 2);
}
 
void strlen_in_loop(const char *s) {
    for (size_t i = 0; i < strlen(s); i++) {   // [OPT-02] strlen recomputed every pass, O(n^2)
        putchar(toupper(s[i]));
    }
}
 
int sum_by_value(vector<int> v) {       // [OPT-03] vector copied, pass by const reference
    int total = 0;
    for (size_t i = 0; i < v.size(); i++) total += v[i];
    return total;
}
 
vector<int> build_vector(int n) {
    vector<int> v;
    for (int i = 0; i < n; i++) {
        v.push_back(i * i);             // [OPT-04] no reserve(), repeated reallocation
    }
    return v;
}
 
string concat_in_loop(int n) {
    string s = "";
    for (int i = 0; i < n; i++) {
        s = s + "item" + to_string(i) + ",";   // [OPT-05] temporary strings each pass
    }
    return s;
}
 
bool has_duplicates(const vector<int> &v) {
    for (size_t i = 0; i < v.size(); i++)      // [OPT-06] O(n^2), sort or use unordered_set
        for (size_t j = i + 1; j < v.size(); j++)
            if (v[i] == v[j]) return true;
    return false;
}
 
void bubble_sort(vector<int> &v) {      // [OPT-07] O(n^2) sort, use std::sort
    for (size_t i = 0; i < v.size(); i++)
        for (size_t j = 0; j + 1 < v.size() - i; j++)
            if (v[j] > v[j + 1]) swap(v[j], v[j + 1]);
}
 
void matrix_multiply(int n, double **A, double **B, double **C) {
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++) {
            C[i][j] = 0;
            for (int k = 0; k < n; k++)
                C[i][j] += A[i][k] * B[k][j];  // [OPT-08] poor cache locality on B, reorder loops
        }
}
 
void loop_invariant(vector<double> &v, double a, double b) {
    for (size_t i = 0; i < v.size(); i++) {
        v[i] = v[i] * sqrt(a * a + b * b);     // [OPT-09] loop-invariant sqrt inside loop
    }
}
 
void print_many(int n) {
    for (int i = 0; i < n; i++) {
        cout << "Line " << i << endl;   // [OPT-11] endl flushes every line, use '\n'
    }
}
 
bool is_prime_slow(int n) {
    if (n < 2) return false;
    for (int i = 2; i < n; i++) {       // [OPT-13] should stop at sqrt(n)
        if (n % i == 0) return false;
    }
    return true;
}
 
// ---------------------------------------------------------------
// SECTION 9: extra cases
// ---------------------------------------------------------------
 
void world_writable_file(const char *path) {
    int fd = creat(path, 0777);         // [CWE-732] overly permissive mode
    if (fd >= 0) close(fd);
}
 
void insecure_temp() {
    char *name = tmpnam(NULL);          // [CWE-377] predictable temp name
    FILE *f = fopen(name, "w");
    if (f) { fputs("secret", f); fclose(f); }
}
 
void print_secret() {
    printf("DB password is %s\n", DB_PASSWORD);     // [CWE-532] secret in output
}
 
void assign_in_condition(int x) {
    if (x = 5) {                        // [CWE-481] assignment instead of comparison
        puts("five");
    }
}
 
int power_of_two_div(int x) {
    return x / 8 + x * 16 + x % 4;      // [OPT-10] strength reduction (shifts / masks)
}
 
int redundant_computation(int a, int b) {
    int r1 = (a * b) + (a * b);         // [OPT-15] common subexpression computed twice
    int r2 = (a * b) * 2;
    return r1 + r2;
}
 
int dead_code(int x) {
    int unused = x * 100;               // [OPT-16] dead store
    int y = 10;
    if (false) {                        // [OPT-16] unreachable branch
        y = 20;
    }
    return x + y;
}
 
int count_chars(const string &s, char c) {
    int count = 0;
    for (size_t i = 0; i < s.length(); i++) {
        string ch = s.substr(i, 1);     // [OPT-12] allocation per character
        if (ch[0] == c) count++;
    }
    return count;
}
 
int lookup_slow(const vector<pair<string, int>> &table, const string &key) {
    for (size_t i = 0; i < table.size(); i++) {     // [OPT-14] linear scan, use unordered_map
        if (table[i].first == key) return table[i].second;
    }
    return -1;
}
 
long sum_with_pow(const vector<int> &v) {
    long total = 0;
    for (size_t i = 0; i < v.size(); i++) {
        total += (long)pow(v[i], 2);    // [OPT-19] pow() for squaring, use v*v
    }
    return total;
}
 
map<string, int> word_count(const vector<string> &words) {
    map<string, int> counts;            // [OPT-20] ordered map when order is unused
    for (size_t i = 0; i < words.size(); i++) {
        if (counts.find(words[i]) == counts.end()) counts[words[i]] = 0;
        counts[words[i]] = counts[words[i]] + 1;    // [OPT-20] three lookups for one update
    }
    return counts;
}
 
// ---------------------------------------------------------------
// SECTION 10: more memory and string bugs
// ---------------------------------------------------------------
 
char *get_static_buffer(const char *s) {
    static char buf[16];
    strcpy(buf, s);                     // [CWE-120] overflow, and shared static buffer [CWE-362]
    return buf;
}
 
void tokenize(char *line) {
    char *tok = strtok(line, ",");      // [CWE-676] non-reentrant, modifies the input
    while (tok) {
        printf("%s\n", tok);
        tok = strtok(NULL, ",");
    }
}
 
int parse_number(const char *s) {
    return atoi(s);                     // [CWE-20] no error checking on input
}
 
void read_two_numbers() {
    int a, b;
    scanf("%d %d", &a, &b);             // [CWE-252] return value ignored
    printf("%d\n", a + b);              // [CWE-457] may be uninitialized
}
 
void realloc_leak(char *p, size_t n) {
    p = (char *)realloc(p, n);          // [CWE-401] original block lost if realloc fails
    p[0] = 0;                           // [CWE-476] result not checked
}
 
void alloca_use(int n) {
    char *p = (char *)alloca(n);        // [CWE-770] stack allocation of attacker-chosen size
    memset(p, 0, n);
}
 
void vla_use(int n) {
    int arr[n];                         // [CWE-770] VLA size not validated
    for (int i = 0; i < n; i++) arr[i] = i;
}
 
void strncat_off_by_one(const char *src) {
    char dst[16] = "hello ";
    strncat(dst, src, sizeof(dst));     // [CWE-193] should be sizeof(dst) - strlen(dst) - 1
    puts(dst);
}
 
void memcpy_overlap(char *buf) {
    memcpy(buf + 2, buf, 10);           // [CWE-119] overlapping regions, use memmove
}
 
void wild_pointer() {
    int *p;
    *p = 42;                            // [CWE-824] uninitialized pointer dereference
}
 
void dangling_after_delete() {
    int *p = new int(5);
    delete p;
    *p = 6;                             // [CWE-416] write after delete
    delete p;                           // [CWE-415] double delete
}
 
void scalar_delete_on_array() {
    char *p = new char[64];
    delete p;                           // [CWE-762] should be delete[]
}
 
void global_overflow(int i) {
    static char table[8];
    table[i] = 'x';                     // [CWE-787] unchecked index into static array
}
 
void fread_unchecked(const char *path) {
    char buf[64];
    FILE *f = fopen(path, "rb");
    fread(buf, 1, 128, f);              // [CWE-120] reads 128 into 64, [CWE-476] f unchecked
    fclose(f);
}
 
void sensitive_not_cleared() {
    char password[32];
    strcpy(password, "hunter2");
    memset(password, 0, sizeof(password));   // [CWE-14] compiler may remove this dead store
}
 
void printf_percent_n(const char *s) {
    printf(s);                          // [CWE-134] attacker can supply %n to write memory
}
 
void gets_style(char *dst) {
    int c, i = 0;
    while ((c = getchar()) != '\n' && c != EOF) {
        dst[i++] = c;                   // [CWE-120] no length limit at all
    }
    dst[i] = 0;
}
 
void string_copy_loop(char *dst, const char *src) {
    int i = 0;
    while (src[i] != '\0') {
        dst[i] = src[i];                // [CWE-120] hand-written unbounded copy
        i++;
    }
}
 
int *return_freed_pointer() {
    int *p = (int *)malloc(sizeof(int));
    *p = 7;
    free(p);
    return p;                           // [CWE-416] returns dangling pointer
}
 
void struct_overflow(const char *name) {
    struct Rec { char name[8]; int admin; } r;
    r.admin = 0;
    strcpy(r.name, name);               // [CWE-787] can overwrite the admin flag
    if (r.admin) puts("admin access");
}
 
// ---------------------------------------------------------------
// SECTION 11: classes with bugs
// ---------------------------------------------------------------
 
class Account {
public:
    char owner[16];
    double balance;
    Account(const char *o, double b) {
        strcpy(owner, o);               // [CWE-120] constructor overflow
        balance = b;
    }
    void withdraw(double amt) {
        balance -= amt;                 // [CWE-840] no check for negative or insufficient funds
    }
    void deposit(double amt) {
        balance += amt;                 // [CWE-840] negative deposit becomes a withdrawal
    }
};
 
class Base {
public:
    virtual void run() { puts("base"); }
    ~Base() {}                          // [CWE-1079] non-virtual destructor
};
 
class Derived : public Base {
    char *data;
public:
    Derived() { data = new char[100]; }
    ~Derived() { delete[] data; }
    void run() override { puts("derived"); }
};
 
void delete_through_base() {
    Base *b = new Derived();
    delete b;                           // [CWE-401] derived destructor skipped, leak
}
 
class Buffer {
    char *ptr;
    size_t size;
public:
    Buffer(size_t n) : size(n) { ptr = new char[n]; }
    ~Buffer() { delete[] ptr; }         // [CWE-415] no copy ctor, shallow copy double-frees
    char &at(size_t i) { return ptr[i]; }   // [CWE-125] no bounds check
};
 
void buffer_copy_bug() {
    Buffer a(16);
    Buffer b = a;                       // [CWE-415] both destructors free the same block
    b.at(100) = 'x';                    // [CWE-787]
}
 
class Session {
public:
    string token;
    Session() { token = to_string(rand()); }   // [CWE-338] weak token
    bool valid(const string &t) { return t == token; }   // [CWE-208] non-constant-time
};
 
// ---------------------------------------------------------------
// SECTION 12: file and network style issues
// ---------------------------------------------------------------
 
void fd_leak(const char *path) {
    int fd = open(path, O_RDONLY);
    if (fd < 0) return;
    char buf[32];
    if (read(fd, buf, 32) < 0) return;  // [CWE-772] fd leaked on this path
    close(fd);
}
 
void log_user_input(const char *input) {
    FILE *f = fopen("/tmp/app.log", "a");
    if (f) {
        fprintf(f, "Login attempt by: %s\n", input);   // [CWE-117] log injection via newlines
        fclose(f);
    }
}
 
void parse_header(const char *hdr) {
    char key[16], val[16];
    sscanf(hdr, "%s: %s", key, val);    // [CWE-120] unbounded sscanf
    printf("%s=%s\n", key, val);
}
 
void trust_length_field(const unsigned char *pkt) {
    unsigned short len = pkt[0] | (pkt[1] << 8);
    char out[64];
    memcpy(out, pkt + 2, len);          // [CWE-130] length taken from packet, never validated
    out[len] = 0;
}
 
// ---------------------------------------------------------------
// SECTION 13: more optimization opportunities
// ---------------------------------------------------------------
 
int sum_2d(const vector<vector<int>> &m) {
    int total = 0;
    for (size_t j = 0; j < m[0].size(); j++)
        for (size_t i = 0; i < m.size(); i++)
            total += m[i][j];           // [OPT-21] column-major walk on row-major data
    return total;
}
 
vector<int> filter_even(vector<int> v) {        // [OPT-03] pass by value
    vector<int> out;
    for (size_t i = 0; i < v.size(); i++) {
        if (v[i] % 2 == 0) out.push_back(v[i]); // [OPT-04] no reserve
    }
    return out;
}
 
void insert_front(vector<int> &v, int n) {
    for (int i = 0; i < n; i++) {
        v.insert(v.begin(), i);         // [OPT-22] O(n) insert at front each time, use deque
    }
}
 
string reverse_slow(const string &s) {
    string r = "";
    for (int i = s.size() - 1; i >= 0; i--) {
        r = r + s[i];                   // [OPT-05] builds a new string every step
    }
    return r;
}
 
int count_primes(int n) {
    int c = 0;
    for (int i = 2; i <= n; i++) {      // [OPT-23] trial division, use a sieve
        bool prime = true;
        for (int j = 2; j < i; j++) {
            if (i % j == 0) { prime = false; break; }
        }
        if (prime) c++;
    }
    return c;
}
 
double average(const vector<double> &v) {
    double sum = 0;
    for (size_t i = 0; i < v.size(); i++) sum += v[i];
    return sum / v.size();              // [CWE-369] also divides by zero on empty input
}
 
double variance(const vector<double> &v) {
    double s = 0;
    for (size_t i = 0; i < v.size(); i++) {
        s += (v[i] - average(v)) * (v[i] - average(v));   // [OPT-24] average() recomputed twice per pass
    }
    return s / v.size();
}
 
void swap_by_copy(vector<string> &v) {
    for (size_t i = 0; i + 1 < v.size(); i += 2) {
        string tmp = v[i];              // [OPT-25] use std::swap / move
        v[i] = v[i + 1];
        v[i + 1] = tmp;
    }
}
 
bool contains(const vector<int> &v, int x) {
    return find(v.begin(), v.end(), x) != v.end();   // [OPT-26] O(n) lookup in hot path
}
 
int gcd_slow(int a, int b) {
    int g = 1;
    for (int i = 1; i <= a && i <= b; i++) {         // [OPT-27] use Euclid's algorithm
        if (a % i == 0 && b % i == 0) g = i;
    }
    return g;
}
 
long factorial_recursive(int n) {
    if (n == 0) return 1;
    return n * factorial_recursive(n - 1);           // [OPT-28] recursion, also overflows [CWE-190]
}
 
// ---------------------------------------------------------------
// main: calls a few of the functions so the file links and runs
// ---------------------------------------------------------------
 
int main(int argc, char *argv[]) {
    if (argc > 1) {
        copy_name(argv[1]);
        log_message(argv[1]);
        run_ping(argv[1]);
    }
    vector<int> data = build_vector(1000);
    bubble_sort(data);
    cout << sum_by_value(data) << endl;
    cout << fib_slow(30) << endl;
    cout << concat_in_loop(100).size() << endl;
    increment_counter();
    return 0;
}

