// =============================================================================
// vulnerable_100.cpp -- INTENTIONALLY VULNERABLE CODE FOR EDUCATION ONLY
// 100 labeled security flaws for code-review / static-analysis practice.
// DO NOT deploy, link into real software, or run on a shared machine.
// Try: g++ -Wall -Wextra -fsanitize=address,undefined -g vulnerable_100.cpp
// Tools to practice with: cppcheck, clang-tidy, clang --analyze, CodeQL, ASan
// =============================================================================
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <string>
#include <vector>
#include <thread>
#include <mutex>
#include <csignal>
#include <ctime>
#include <alloca.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <syslog.h>

// ---- stubs so the file is self-contained ------------------------------------
static void db_exec(const std::string&) {}
static std::string md5_hex(const std::string& s) { return s; }
static void send_all(int, const char*, size_t) {}
static void http_response(const std::string&) {}

// =============================================================================
// SECTION A: MEMORY SAFETY (1-25)
// =============================================================================

// 1. CWE-121 Stack buffer overflow via strcpy
void v001(const char* in) { char buf[16]; strcpy(buf, in); }

// 2. CWE-121 strcat overflow
void v002(const char* in) { char buf[16] = "user:"; strcat(buf, in); }

// 3. CWE-121 sprintf overflow
void v003(const char* name) { char buf[32]; sprintf(buf, "Hello, %s! Welcome back.", name); }

// 4. CWE-120 scanf %s with no width
void v004() { char buf[8]; scanf("%s", buf); }

// 5. CWE-193 Off-by-one
void v005(const char* in) { char buf[8]; for (int i = 0; i <= 8; i++) buf[i] = in[i]; }

// 6. CWE-122 Heap overflow, attacker-controlled length
void v006(const char* src, size_t n) { char* p = (char*)malloc(16); memcpy(p, src, n); free(p); }

// 7. CWE-416 Use after free
void v007() { int* p = (int*)malloc(4); free(p); *p = 42; }

// 8. CWE-415 Double free
void v008() { char* p = (char*)malloc(8); free(p); free(p); }

// 9. CWE-401 Memory leak
void v009() { for (int i = 0; i < 1000; i++) { new char[1024]; } }

// 10. CWE-476 Null pointer dereference
int v010(const char* s) { const char* p = strchr(s, ':'); return *p; }

// 11. CWE-457 Uninitialized variable
int v011() { int secret; return secret; }

// 12. CWE-562 Return pointer to stack variable
char* v012() { char local[32] = "temp"; return local; }

// 13. CWE-190 Integer overflow in allocation size
void* v013(uint32_t count) { return malloc(count * sizeof(uint64_t)); }

// 14. CWE-195 Signed/unsigned confusion
void v014(int len) { char buf[64]; if (len < 64) memcpy(buf, "AAAA", (size_t)len); }

// 15. CWE-129 Negative array index
int v015(int idx) { int a[10] = {0}; return a[idx]; }

// 16. CWE-125 Out-of-bounds read
int v016(const int* arr, int n) { int s = 0; for (int i = 0; i <= n; i++) s += arr[i]; return s; }

// 17. CWE-134 Format string
void v017(const char* in) { printf(in); }

// 18. CWE-762 Mismatched new[] / delete
void v018() { int* p = new int[10]; delete p; }

// 19. CWE-416 Dangling reference
const std::string& v019() { std::string s = "temp"; return s; }

// 20. CWE-416 Iterator invalidation
void v020(std::vector<int>& v) { for (auto it = v.begin(); it != v.end(); ++it) if (*it == 0) v.push_back(1); }

// 21. CWE-125 vector::operator[] out of range
int v021(std::vector<int>& v, size_t i) { return v[i]; }

// 22. CWE-170 strncpy without null termination
void v022(const char* in) { char buf[8]; strncpy(buf, in, sizeof(buf)); printf("%s", buf); }

// 23. CWE-770 alloca with attacker size
void v023(size_t n) { char* p = (char*)alloca(n); memset(p, 0, n); }

// 24. CWE-1285 VLA sized by input
void v024(int n) { char buf[n]; memset(buf, 0, n); }

// 25. CWE-197 Integer truncation
void v025(size_t big) { unsigned char n = big; char* p = (char*)malloc(n); memset(p, 0, big); }

// =============================================================================
// SECTION B: INJECTION & OUTPUT HANDLING (26-40)
// =============================================================================

// 26. CWE-78 OS command injection via system()
void v026(const std::string& host) { system(("ping -c1 " + host).c_str()); }

// 27. CWE-78 popen injection
void v027(const std::string& f) { FILE* p = popen(("cat " + f).c_str(), "r"); if (p) pclose(p); }

// 28. CWE-89 SQL injection
void v028(const std::string& u, const std::string& p) {
    db_exec("SELECT * FROM users WHERE name='" + u + "' AND pw='" + p + "'");
}

// 29. CWE-22 Path traversal
void v029(const std::string& name) { FILE* f = fopen(("/var/www/files/" + name).c_str(), "r"); if (f) fclose(f); }

// 30. CWE-78 execl through shell
void v030(const char* arg) { char cmd[128]; snprintf(cmd, sizeof cmd, "ls %s", arg); execl("/bin/sh", "sh", "-c", cmd, (char*)0); }

// 31. CWE-90 LDAP filter injection
std::string v031(const std::string& u) { return "(&(uid=" + u + ")(objectClass=person))"; }

// 32. CWE-79 Reflected XSS
void v032(const std::string& q) { http_response("<html><body>You searched: " + q + "</body></html>"); }

// 33. CWE-117 Log injection
void v033(const std::string& user) { fprintf(stderr, "Login attempt for user: %s\n", user.c_str()); }

// 34. CWE-113 CRLF / header injection
void v034(const std::string& lang) { http_response("HTTP/1.1 200 OK\r\nContent-Language: " + lang + "\r\n\r\n"); }

// 35. CWE-134 Format string in syslog
void v035(const char* msg) { syslog(LOG_ERR, msg); }

// 36. CWE-78 Environment variable fed into shell
void v036() { const char* d = getenv("BACKUP_DIR"); system((std::string("tar czf /tmp/b.tgz ") + d).c_str()); }

// 37. CWE-611 XXE-style: trusting external entity references in raw XML
bool v037(const std::string& xml) { return xml.find("<!ENTITY") != std::string::npos ? true : false; /* then parses anyway */ }

// 38. CWE-1333 Catastrophic backtracking style matcher
bool v038(const char* s, const char* p) {
    if (!*p) return !*s;
    if (p[1] == '*') return v038(s, p + 2) || (*s && (*s == *p) && v038(s + 1, p));
    return *s && *s == *p && v038(s + 1, p + 1);
}

// 39. CWE-502 Unsafe deserialization of a struct holding a function pointer
struct Msg { int type; void (*handler)(const char*); char data[32]; };
void v039(const char* raw) { Msg m; memcpy(&m, raw, sizeof m); m.handler(m.data); }

// 40. CWE-1336 Template / format string built from user input
std::string v040(const std::string& userTpl, const std::string& name) {
    char out[256]; snprintf(out, sizeof out, userTpl.c_str(), name.c_str()); return out;
}

// =============================================================================
// SECTION C: CRYPTO & AUTHENTICATION (41-60)
// =============================================================================

// 41. CWE-798 Hardcoded password
bool v041(const std::string& p) { return p == "admin123"; }

// 42. CWE-798 Hardcoded API key
const char* v042() { return "sk_live_51H8xExampleHardcodedKey"; }

// 43. CWE-328 Weak hash (MD5) for passwords
std::string v043(const std::string& pw) { return md5_hex(pw); }

// 44. CWE-338 rand() for security tokens
int v044() { return rand(); }

// 45. CWE-337 Predictable seed
int v045() { srand(time(nullptr)); return rand(); }

// 46. CWE-327 Home-grown XOR "encryption"
std::string v046(std::string d) { for (auto& c : d) c ^= 0x5A; return d; }

// 47. CWE-208 Timing side channel in comparison
bool v047(const char* a, const char* b) { return strcmp(a, b) == 0; }

// 48. CWE-256 Plaintext password storage
void v048(const std::string& u, const std::string& p) { FILE* f = fopen("users.txt", "a"); fprintf(f, "%s:%s\n", u.c_str(), p.c_str()); fclose(f); }

// 49. CWE-759 Hash without salt
std::string v049(const std::string& pw) { return md5_hex(pw); }

// 50. CWE-329 Static / hardcoded IV
static const unsigned char IV[16] = {0};
const unsigned char* v050() { return IV; }

// 51. CWE-377 Predictable temp filename
void v051() { FILE* f = fopen("/tmp/app_session.tmp", "w"); if (f) fclose(f); }

// 52. CWE-326 Inadequate key length
int v052() { return 40; /* RSA key bits */ }

// 53. CWE-295 Certificate validation disabled
struct TlsCfg { bool verify_peer; bool verify_host; };
TlsCfg v053() { return {false, false}; }

// 54. CWE-1392 Default credentials
struct Cred { const char* u; const char* p; };
Cred v054() { return {"admin", "admin"}; }

// 55. CWE-532 Password written to log
void v055(const char* u, const char* p) { fprintf(stderr, "login user=%s pass=%s\n", u, p); }

// 56. CWE-306 Missing authentication on admin function
void v056(const std::string& cmd) { system(cmd.c_str()); }

// 57. CWE-330 Sequential session IDs
int v057() { static int id = 1000; return ++id; }

// 58. CWE-697 Comparing C-string pointers instead of contents
bool v058(const char* a, const char* b) { return a == b; }

// 59. CWE-321 Hardcoded cryptographic key
static const char AES_KEY[] = "0123456789abcdef";
const char* v059() { return AES_KEY; }

// 60. CWE-261 Encoding (not encryption) used to protect secrets
std::string v060(const std::string& s) {
    static const char* t = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    std::string o; for (size_t i = 0; i < s.size(); i++) o += t[s[i] & 63]; return o;
}

// =============================================================================
// SECTION D: FILES, PROCESSES & CONCURRENCY (61-75)
// =============================================================================

// 61. CWE-367 TOCTOU: check then use
void v061(const char* path) { if (access(path, W_OK) == 0) { int fd = open(path, O_WRONLY); if (fd >= 0) close(fd); } }

// 62. CWE-732 World-writable file permissions
void v062() { int fd = open("config.ini", O_CREAT | O_WRONLY, 0777); if (fd >= 0) close(fd); }

// 63. CWE-59 Symlink-following write in /tmp
void v063() { int fd = open("/tmp/report.txt", O_WRONLY | O_CREAT, 0666); if (fd >= 0) close(fd); }

// 64. CWE-276 Permissive umask
void v064() { umask(0); }

// 65. CWE-73 External control of file name
void v065(const char* p) { FILE* f = fopen(p, "w"); if (f) fclose(f); }

// 66. CWE-252 Unchecked return values
void v066(const char* p) { char b[16]; int fd = open(p, O_RDONLY); read(fd, b, sizeof b); write(1, b, sizeof b); }

// 67. CWE-775 File descriptor leak
void v067(const char* p) { for (int i = 0; i < 100000; i++) open(p, O_RDONLY); }

// 68. CWE-362 Data race on shared counter
static int g_counter = 0;
void v068() { std::thread a([]{ for (int i = 0; i < 100000; i++) g_counter++; });
              std::thread b([]{ for (int i = 0; i < 100000; i++) g_counter++; }); a.join(); b.join(); }

// 69. CWE-479 Non-async-signal-safe handler
void v069_handler(int) { printf("caught\n"); free(malloc(10)); }
void v069() { signal(SIGINT, v069_handler); }

// 70. CWE-250 Privileges never dropped
void v070() { setuid(0); system("/usr/bin/helper"); }

// 71. CWE-243 chroot without chdir
void v071() { chroot("/jail"); }

// 72. CWE-400 Unbounded file read into memory
std::string v072(const char* p) { FILE* f = fopen(p, "rb"); std::string s; char c; while (f && fread(&c, 1, 1, f)) s += c; return s; }

// 73. CWE-23 Zip-slip: extracting entry names unchecked
void v073(const std::string& entry) { FILE* f = fopen(("./out/" + entry).c_str(), "wb"); if (f) fclose(f); }

// 74. CWE-377 tmpnam() race
void v074() { char n[L_tmpnam]; tmpnam(n); FILE* f = fopen(n, "w"); if (f) fclose(f); }

// 75. CWE-532 Sensitive log file world-readable
void v075() { int fd = open("audit.log", O_CREAT | O_APPEND | O_WRONLY, 0644); if (fd >= 0) close(fd); }

// =============================================================================
// SECTION E: NETWORK (76-90)
// =============================================================================

// 76. CWE-1327 Binding to all interfaces
void v076(int s) { sockaddr_in a{}; a.sin_family = AF_INET; a.sin_addr.s_addr = INADDR_ANY; a.sin_port = htons(8080); bind(s, (sockaddr*)&a, sizeof a); }

// 77. CWE-400 No socket timeout (slowloris)
void v077(int s) { char b[256]; while (recv(s, b, sizeof b, 0) > 0) {} }

// 78. CWE-120 recv length larger than buffer
void v078(int s) { char b[64]; recv(s, b, 4096, 0); }

// 79. CWE-130 Trusting a client-supplied length field
void v079(int s) { uint32_t len; recv(s, &len, 4, 0); char* b = (char*)malloc(64); recv(s, b, len, 0); free(b); }

// 80. CWE-319 Cleartext transmission of credentials
void v080(int s, const std::string& pw) { send_all(s, pw.c_str(), pw.size()); }

// 81. CWE-918 SSRF: fetching attacker-chosen URL
void v081(const std::string& url) { system(("curl " + url).c_str()); }

// 82. CWE-770 Allocation driven by client with no cap
void v082(uint32_t n) { std::vector<char> v(n); }

// 83. CWE-307 No limit on authentication attempts
bool v083(const std::string& p) { return p == "letmein"; /* callable in a loop forever */ }

// 84. CWE-362 Non-thread-safe resolver
void v084(const char* h) { hostent* he = gethostbyname(h); (void)he; }

// 85. CWE-362 strtok shared static state
void v085(char* s) { for (char* t = strtok(s, ","); t; t = strtok(nullptr, ",")) puts(t); }

// 86. CWE-252 inet_addr error value unchecked
void v086(const char* ip) { sockaddr_in a{}; a.sin_addr.s_addr = inet_addr(ip); (void)a; }

// 87. CWE-601 Open redirect
void v087(const std::string& next) { http_response("HTTP/1.1 302 Found\r\nLocation: " + next + "\r\n\r\n"); }

// 88. CWE-209 Verbose error leaks internals
void v088(const char* q) { http_response(std::string("DB error in query: ") + q + " at /srv/app/db.cpp:88"); }

// 89. CWE-942 Wildcard CORS with credentials
void v089() { http_response("Access-Control-Allow-Origin: *\r\nAccess-Control-Allow-Credentials: true\r\n"); }

// 90. CWE-912 Hidden backdoor
bool v090(const std::string& u) { return u == "debug_master" || u == "admin"; }

// =============================================================================
// SECTION F: LOGIC, UB & MISC (91-100)
// =============================================================================

// 91. CWE-833 Lock-order deadlock
std::mutex A, B;
void v091a() { std::lock_guard<std::mutex> l1(A); std::lock_guard<std::mutex> l2(B); }
void v091b() { std::lock_guard<std::mutex> l1(B); std::lock_guard<std::mutex> l2(A); }

// 92. CWE-674 Uncontrolled recursion
int v092(int n) { return v092(n + 1) + 1; }

// 93. CWE-369 Division by zero
int v093(int a, int b) { return a / b; }

// 94. CWE-1335 Shift by attacker-controlled count (UB)
uint32_t v094(int n) { return 1u << n; }

// 95. CWE-190 Signed integer overflow (UB)
int v095(int a, int b) { return a + b; }

// 96. CWE-20 atoi with no validation
int v096(const char* s) { int n = atoi(s); int a[16]; return a[n]; }

// 97. CWE-1108 Mutable global holding security state
bool g_is_admin = false;
void v097() { g_is_admin = true; }

// 98. CWE-14 memset on secret optimized away
void v098() { char key[32] = "supersecret"; memset(key, 0, sizeof key); }

// 99. CWE-562 Returning pointer to static buffer (not reentrant, overwritten)
char* v099(const char* s) { static char buf[64]; snprintf(buf, sizeof buf, "<%s>", s); return buf; }

// 100. CWE-657 Security decision made on client-controlled flag
bool v100(const std::string& cookie) { return cookie.find("role=admin") != std::string::npos; }

int main() {
    // Intentionally calls nothing. Read, analyse, scan.
    return 0;
}
