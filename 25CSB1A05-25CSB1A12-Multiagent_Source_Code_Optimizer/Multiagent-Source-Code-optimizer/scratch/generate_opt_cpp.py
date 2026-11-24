"""
Generate the full optimized C++ code for vulnerable_samples.cpp and test it.
"""

# Read original
with open(r"scratch\vulnerable_samples.cpp", "r", encoding="utf-8") as f:
    orig = f.read()

# Replace Section 8 and Section 13 with optimized versions while keeping #include <unordered_set> and <deque>
headers = """#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <map>
#include <unordered_map>
#include <unordered_set>
#include <deque>
#include <cstring>
#include <cstdio>
#include <cstdlib>
#include <ctime>
#include <cmath>
#include <algorithm>
#include <unistd.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <alloca.h>"""

optimized = orig.replace("""#include <iostream>
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
#include <alloca.h>""", headers)

# Replace fib_slow
old_fib = """int fib_slow(int n) {                   // [OPT-01] exponential recursion, use iteration/memo
    if (n <= 1) return n;
    return fib_slow(n - 1) + fib_slow(n - 2);
}"""
new_fib = """int fib_slow(int n) {                   // [OPT-01] O(N) iterative implementation
    if (n <= 1) return n;
    int a = 0, b = 1;
    for (int i = 2; i <= n; i++) {
        int c = a + b;
        a = b;
        b = c;
    }
    return b;
}"""
optimized = optimized.replace(old_fib, new_fib)

# Replace strlen_in_loop
old_strlen = """void strlen_in_loop(const char *s) {
    for (size_t i = 0; i < strlen(s); i++) {   // [OPT-02] strlen recomputed every pass, O(n^2)
        putchar(toupper(s[i]));
    }
}"""
new_strlen = """void strlen_in_loop(const char *s) {
    size_t len = strlen(s);                    // [OPT-02] Hoisted strlen outside loop, O(N)
    for (size_t i = 0; i < len; i++) {
        putchar(toupper(s[i]));
    }
}"""
optimized = optimized.replace(old_strlen, new_strlen)

# Replace sum_by_value
old_sum_val = """int sum_by_value(vector<int> v) {       // [OPT-03] vector copied, pass by const reference
    int total = 0;
    for (size_t i = 0; i < v.size(); i++) total += v[i];
    return total;
}"""
new_sum_val = """int sum_by_value(const vector<int> &v) { // [OPT-03] const reference avoids copy
    int total = 0;
    for (size_t i = 0; i < v.size(); i++) total += v[i];
    return total;
}"""
optimized = optimized.replace(old_sum_val, new_sum_val)

# Replace build_vector
old_build_vec = """vector<int> build_vector(int n) {
    vector<int> v;
    for (int i = 0; i < n; i++) {
        v.push_back(i * i);             // [OPT-04] no reserve(), repeated reallocation
    }
    return v;
}"""
new_build_vec = """vector<int> build_vector(int n) {
    vector<int> v;
    v.reserve(n);                       // [OPT-04] Pre-allocated storage prevents reallocation
    for (int i = 0; i < n; i++) {
        v.push_back(i * i);
    }
    return v;
}"""
optimized = optimized.replace(old_build_vec, new_build_vec)

# Replace concat_in_loop
old_concat = """string concat_in_loop(int n) {
    string s = "";
    for (int i = 0; i < n; i++) {
        s = s + "item" + to_string(i) + ",";   // [OPT-05] temporary strings each pass
    }
    return s;
}"""
new_concat = """string concat_in_loop(int n) {
    string s = "";
    s.reserve(n * 16);                  // [OPT-05] Pre-reserved buffer and in-place append
    for (int i = 0; i < n; i++) {
        s += "item";
        s += to_string(i);
        s += ",";
    }
    return s;
}"""
optimized = optimized.replace(old_concat, new_concat)

# Replace has_duplicates
old_dup = """bool has_duplicates(const vector<int> &v) {
    for (size_t i = 0; i < v.size(); i++)      // [OPT-06] O(n^2), sort or use unordered_set
        for (size_t j = i + 1; j < v.size(); j++)
            if (v[i] == v[j]) return true;
    return false;
}"""
new_dup = """bool has_duplicates(const vector<int> &v) {
    unordered_set<int> seen;            // [OPT-06] O(N) hash set lookup
    seen.reserve(v.size());
    for (int x : v) {
        if (!seen.insert(x).second) return true;
    }
    return false;
}"""
optimized = optimized.replace(old_dup, new_dup)

# Replace bubble_sort
old_sort = """void bubble_sort(vector<int> &v) {      // [OPT-07] O(n^2) sort, use std::sort
    for (size_t i = 0; i < v.size(); i++)
        for (size_t j = 0; j + 1 < v.size() - i; j++)
            if (v[j] > v[j + 1]) swap(v[j], v[j + 1]);
}"""
new_sort = """void bubble_sort(vector<int> &v) {      // [OPT-07] O(N log N) std::sort
    sort(v.begin(), v.end());
}"""
optimized = optimized.replace(old_sort, new_sort)

# Replace matrix_multiply
old_matrix = """void matrix_multiply(int n, double **A, double **B, double **C) {
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++) {
            C[i][j] = 0;
            for (int k = 0; k < n; k++)
                C[i][j] += A[i][k] * B[k][j];  // [OPT-08] poor cache locality on B, reorder loops
        }
}"""
new_matrix = """void matrix_multiply(int n, double **A, double **B, double **C) {
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            C[i][j] = 0.0;
    for (int i = 0; i < n; i++)                 // [OPT-08] Reordered loops (i-k-j) for contiguous memory cache hits
        for (int k = 0; k < n; k++) {
            double r = A[i][k];
            for (int j = 0; j < n; j++)
                C[i][j] += r * B[k][j];
        }
}"""
optimized = optimized.replace(old_matrix, new_matrix)

# Replace loop_invariant
old_inv = """void loop_invariant(vector<double> &v, double a, double b) {
    for (size_t i = 0; i < v.size(); i++) {
        v[i] = v[i] * sqrt(a * a + b * b);     // [OPT-09] loop-invariant sqrt inside loop
    }
}"""
new_inv = """void loop_invariant(vector<double> &v, double a, double b) {
    double factor = sqrt(a * a + b * b);       // [OPT-09] Hoisted invariant computation outside loop
    for (size_t i = 0; i < v.size(); i++) {
        v[i] = v[i] * factor;
    }
}"""
optimized = optimized.replace(old_inv, new_inv)

# Replace print_many
old_print = """void print_many(int n) {
    for (int i = 0; i < n; i++) {
        cout << "Line " << i << endl;   // [OPT-11] endl flushes every line, use '\\n'
    }
}"""
new_print = """void print_many(int n) {
    for (int i = 0; i < n; i++) {
        cout << "Line " << i << '\\n';   // [OPT-11] Fast '\\n' avoids excessive buffer flush
    }
}"""
optimized = optimized.replace(old_print, new_print)

# Replace is_prime_slow
old_prime = """bool is_prime_slow(int n) {
    if (n < 2) return false;
    for (int i = 2; i < n; i++) {       // [OPT-13] should stop at sqrt(n)
        if (n % i == 0) return false;
    }
    return true;
}"""
new_prime = """bool is_prime_slow(int n) {
    if (n < 2) return false;
    int limit = (int)sqrt(n);           // [OPT-13] O(sqrt(N)) trial division limit
    for (int i = 2; i <= limit; i++) {
        if (n % i == 0) return false;
    }
    return true;
}"""
optimized = optimized.replace(old_prime, new_prime)

# Replace power_of_two_div
old_p2 = """int power_of_two_div(int x) {
    return x / 8 + x * 16 + x % 4;      // [OPT-10] strength reduction (shifts / masks)
}"""
new_p2 = """int power_of_two_div(int x) {
    return (x >> 3) + (x << 4) + (x & 3); // [OPT-10] Bitwise shifts and masks replace division/multiplication
}"""
optimized = optimized.replace(old_p2, new_p2)

# Replace redundant_computation
old_red = """int redundant_computation(int a, int b) {
    int r1 = (a * b) + (a * b);         // [OPT-15] common subexpression computed twice
    int r2 = (a * b) * 2;
    return r1 + r2;
}"""
new_red = """int redundant_computation(int a, int b) {
    int prod = a * b;                   // [OPT-15] Common subexpression eliminated
    return prod * 4;
}"""
optimized = optimized.replace(old_red, new_red)

# Replace dead_code
old_dead = """int dead_code(int x) {
    int unused = x * 100;               // [OPT-16] dead store
    int y = 10;
    if (false) {                        // [OPT-16] unreachable branch
        y = 20;
    }
    return x + y;
}"""
new_dead = """int dead_code(int x) {
    int y = 10;                         // [OPT-16] Removed dead store and unreachable branch
    return x + y;
}"""
optimized = optimized.replace(old_dead, new_dead)

# Replace count_chars
old_cnt = """int count_chars(const string &s, char c) {
    int count = 0;
    for (size_t i = 0; i < s.length(); i++) {
        string ch = s.substr(i, 1);     // [OPT-12] allocation per character
        if (ch[0] == c) count++;
    }
    return count;
}"""
new_cnt = """int count_chars(const string &s, char c) {
    int count = 0;
    for (size_t i = 0; i < s.length(); i++) {
        if (s[i] == c) count++;          // [OPT-12] Direct indexed comparison without substr allocation
    }
    return count;
}"""
optimized = optimized.replace(old_cnt, new_cnt)

# Replace sum_with_pow
old_pow = """long sum_with_pow(const vector<int> &v) {
    long total = 0;
    for (size_t i = 0; i < v.size(); i++) {
        total += (long)pow(v[i], 2);    // [OPT-19] pow() for squaring, use v*v
    }
    return total;
}"""
new_pow = """long sum_with_pow(const vector<int> &v) {
    long total = 0;
    for (size_t i = 0; i < v.size(); i++) {
        total += (long)v[i] * v[i];      // [OPT-19] Direct multiplication avoids floating point pow()
    }
    return total;
}"""
optimized = optimized.replace(old_pow, new_pow)

# Replace word_count
old_wc = """map<string, int> word_count(const vector<string> &words) {
    map<string, int> counts;            // [OPT-20] ordered map when order is unused
    for (size_t i = 0; i < words.size(); i++) {
        if (counts.find(words[i]) == counts.end()) counts[words[i]] = 0;
        counts[words[i]] = counts[words[i]] + 1;    // [OPT-20] three lookups for one update
    }
    return counts;
}"""
new_wc = """unordered_map<string, int> word_count(const vector<string> &words) {
    unordered_map<string, int> counts;  // [OPT-20] O(1) unordered_map with single operator[] increment
    for (size_t i = 0; i < words.size(); i++) {
        counts[words[i]]++;
    }
    return counts;
}"""
optimized = optimized.replace(old_wc, new_wc)

# Replace sum_2d
old_s2d = """int sum_2d(const vector<vector<int>> &m) {
    int total = 0;
    for (size_t j = 0; j < m[0].size(); j++)
        for (size_t i = 0; i < m.size(); i++)
            total += m[i][j];           // [OPT-21] column-major walk on row-major data
    return total;
}"""
new_s2d = """int sum_2d(const vector<vector<int>> &m) {
    int total = 0;
    for (size_t i = 0; i < m.size(); i++)      // [OPT-21] Row-major walk matches memory layout
        for (size_t j = 0; j < m[0].size(); j++)
            total += m[i][j];
    return total;
}"""
optimized = optimized.replace(old_s2d, new_s2d)

# Replace filter_even
old_fe = """vector<int> filter_even(vector<int> v) {        // [OPT-03] pass by value
    vector<int> out;
    for (size_t i = 0; i < v.size(); i++) {
        if (v[i] % 2 == 0) out.push_back(v[i]); // [OPT-04] no reserve
    }
    return out;
}"""
new_fe = """vector<int> filter_even(const vector<int> &v) { // [OPT-03] const& and [OPT-04] reserve
    vector<int> out;
    out.reserve(v.size());
    for (size_t i = 0; i < v.size(); i++) {
        if (v[i] % 2 == 0) out.push_back(v[i]);
    }
    return out;
}"""
optimized = optimized.replace(old_fe, new_fe)

# Replace reverse_slow
old_rev = """string reverse_slow(const string &s) {
    string r = "";
    for (int i = s.size() - 1; i >= 0; i--) {
        r = r + s[i];                   // [OPT-05] builds a new string every step
    }
    return r;
}"""
new_rev = """string reverse_slow(string s) {
    reverse(s.begin(), s.end());        // [OPT-05] In-place std::reverse avoids quadratic allocations
    return s;
}"""
optimized = optimized.replace(old_rev, new_rev)

# Replace variance
old_var = """double variance(const vector<double> &v) {
    double s = 0;
    for (size_t i = 0; i < v.size(); i++) {
        s += (v[i] - average(v)) * (v[i] - average(v));   // [OPT-24] average() recomputed twice per pass
    }
    return s / v.size();
}"""
new_var = """double variance(const vector<double> &v) {
    if (v.empty()) return 0.0;
    double avg = average(v);            // [OPT-24] Hoisted average() computation outside loop
    double s = 0;
    for (size_t i = 0; i < v.size(); i++) {
        double diff = v[i] - avg;
        s += diff * diff;
    }
    return s / v.size();
}"""
optimized = optimized.replace(old_var, new_var)

# Replace swap_by_copy
old_swap = """void swap_by_copy(vector<string> &v) {
    for (size_t i = 0; i + 1 < v.size(); i += 2) {
        string tmp = v[i];              // [OPT-25] use std::swap / move
        v[i] = v[i + 1];
        v[i + 1] = tmp;
    }
}"""
new_swap = """void swap_by_copy(vector<string> &v) {
    for (size_t i = 0; i + 1 < v.size(); i += 2) {
        swap(v[i], v[i + 1]);           // [OPT-25] std::swap avoids deep string copies
    }
}"""
optimized = optimized.replace(old_swap, new_swap)

# Replace gcd_slow
old_gcd = """int gcd_slow(int a, int b) {
    int g = 1;
    for (int i = 1; i <= a && i <= b; i++) {         // [OPT-27] use Euclid's algorithm
        if (a % i == 0 && b % i == 0) g = i;
    }
    return g;
}"""
new_gcd = """int gcd_slow(int a, int b) {
    while (b != 0) {                    // [OPT-27] O(log min(a,b)) Euclidean algorithm
        int t = b;
        b = a % b;
        a = t;
    }
    return a;
}"""
optimized = optimized.replace(old_gcd, new_gcd)

# Replace factorial_recursive
old_fac = """long factorial_recursive(int n) {
    if (n == 0) return 1;
    return n * factorial_recursive(n - 1);           // [OPT-28] recursion, also overflows [CWE-190]
}"""
new_fac = """long factorial_recursive(int n) {
    long res = 1;                       // [OPT-28] Iterative loop avoids stack frames
    for (int i = 2; i <= n; i++) res *= i;
    return res;
}"""
optimized = optimized.replace(old_fac, new_fac)

with open(r"scratch\vulnerable_samples_optimized.cpp", "w", encoding="utf-8") as f:
    f.write(optimized)

print("Generated scratch/vulnerable_samples_optimized.cpp successfully! Length:", len(optimized))
