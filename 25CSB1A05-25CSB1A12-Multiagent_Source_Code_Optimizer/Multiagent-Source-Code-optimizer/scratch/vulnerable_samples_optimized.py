"""
vulnerable_samples.py
Intentionally vulnerable and inefficient Python used as a TEST INPUT for a
static analysis / optimization tool. Never use any of this in real software.
Labels: [CWE-xxx] = vulnerability, [OPT-xx] = optimization chance.
"""
 
import os
import re
import sys
import time
import json
import yaml
import pickle
import random
import sqlite3
import hashlib
import tempfile
import subprocess
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
 
API_KEY = "sk_live_51H8xExampleKey000"          # [CWE-798] hard-coded secret
ADMIN_PASSWORD = "admin123"                      # [CWE-798] hard-coded password
DEBUG = True                                     # [CWE-489] debug flag left on
DB_PATH = "/tmp/app.db"                          # [CWE-377] fixed path in shared dir
 
 
# ---------------------------------------------------------------
# SECTION 1: injection
# ---------------------------------------------------------------
 
def get_user(username):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    query = "SELECT * FROM users WHERE name = '" + username + "'"   # [CWE-89] SQL injection
    cur.execute(query)
    return cur.fetchall()
 
 
def login(username, password):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(f"SELECT id FROM users WHERE name='{username}' AND pw='{password}'")  # [CWE-89]
    row = cur.fetchone()
    return row is not None
 
 
def ping_host(host):
    os.system("ping -c 1 " + host)                                   # [CWE-78] command injection
 
 
def run_shell(cmd):
    return subprocess.check_output(cmd, shell=True)                  # [CWE-78] shell=True
 
 
def calculate(expression):
    return eval(expression)                                          # [CWE-95] eval on user input
 
 
# ---------------------------------------------------------------
# SECTION 2: deserialization and parsing
# ---------------------------------------------------------------
 
def load_session(blob):
    return pickle.loads(blob)                                        # [CWE-502] untrusted pickle
 
 
def load_config(text):
    return yaml.load(text)                                           # [CWE-502] yaml.load without SafeLoader
 
 
# ---------------------------------------------------------------
# SECTION 3: files and paths
# ---------------------------------------------------------------
 
def read_upload(filename):
    path = "/var/uploads/" + filename                                # [CWE-22] path traversal
    with open(path) as f:
        return f.read()
 
 
def make_temp():
    name = tempfile.mktemp()                                         # [CWE-377] race, predictable
    with open(name, "w") as f:
        f.write("secret data")
    return name
 
 
def check_then_write(path):
    if os.access(path, os.W_OK):                                     # [CWE-367] TOCTOU
        with open(path, "w") as f:
            f.write("data")
 
 
# ---------------------------------------------------------------
# SECTION 4: crypto, randomness, secrets
# ---------------------------------------------------------------
 
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()                # [CWE-327] MD5, unsalted
 
 
def make_session_id():
    return str(random.randint(100000, 999999))                       # [CWE-338] weak PRNG for session id
 
 
def check_token(supplied, real):
    return supplied == real                                          # [CWE-208] non-constant-time compare
 
 
def check_admin(password):
    if password == ADMIN_PASSWORD:                                   # [CWE-798]
        return True
    return False
 
 
# ---------------------------------------------------------------
# SECTION 5: network
# ---------------------------------------------------------------
 
def fetch_url(url):
    return urllib.request.urlopen(url).read()                        # [CWE-918] SSRF, [CWE-295] no timeout
 
 
# ---------------------------------------------------------------
# SECTION 6: logic and misc
# ---------------------------------------------------------------
 
def safe_divide(a, b):
    try:
        return a / b
    except:                                                          # [CWE-396] bare except hides errors
        pass
 
 
def append_item(item, bucket=[]):                                    # [CWE-1188] mutable default arg
    bucket.append(item)
    return bucket
 
 
def regex_check(text):
    return re.match(r"^(a+)+$", text)                                # [CWE-1333] catastrophic backtracking
 
 
# ---------------------------------------------------------------
# SECTION 7: OPTIMIZATION OPPORTUNITIES
# ---------------------------------------------------------------
 
def fib_slow(n):                                                     # [OPT-01] iterative O(n) memoized
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
 
 
def concat_in_loop(n):
    return "".join(f"item{i}," for i in range(n))                    # [OPT-02] list comprehension with join
 
 
def has_duplicates(items):
    return len(items) != len(set(items))                             # [OPT-03] O(n) set comparison
 
 
def membership_in_list(queries, allowed):
    allowed_set = set(allowed)                                       # [OPT-04] O(1) set lookup
    return [q for q in queries if q in allowed_set]
 
 
def bubble_sort(arr):
    return sorted(arr)                                               # [OPT-05] use Timsort O(n log n)
 
 
def loop_invariant(data, a, b):
    factor = (a ** 2 + b ** 2) ** 0.5                               # [OPT-08] hoist invariant outside loop
    return [x * factor for x in data]
 
 
def count_words(words):
    from collections import Counter
    return dict(Counter(words))                                      # [OPT-09] use collections.Counter
 
 
def read_big_file(path):
    total = 0
    with open(path) as f:
        for line in f:                                               # [OPT-10] stream file line by line
            total += len(line)
    return total
 
 
def is_prime_slow(n):
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    limit = int(n ** 0.5) + 1
    for i in range(5, limit, 6):                                      # [OPT-12] stop at sqrt(n)
        if n % i == 0 or n % (i + 2) == 0:
            return False
    return True
 
 
def matrix_multiply(A, B):
    try:
        import numpy as np
        return (np.array(A) @ np.array(B)).tolist()                  # [OPT-14] vectorized matrix multiply
    except ImportError:
        n = len(A)
        return [[sum(A[i][k] * B[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
 
 
# ---------------------------------------------------------------
# SECTION 8: extra cases
# ---------------------------------------------------------------
 
def make_reset_token():
    random.seed(int(time.time()))                                    # [CWE-338] predictable seed
    return "".join(random.choice("abcdef0123456789") for _ in range(8))
 
 
def fetch_insecure(url):
    import ssl
    ctx = ssl.create_default_context()
    ctx.check_hostname = False                                       # [CWE-295] TLS checks disabled
    ctx.verify_mode = ssl.CERT_NONE
    return urllib.request.urlopen(url, context=ctx).read()
 
 
def bind_all():
    import socket
    s = socket.socket()
    s.bind(("0.0.0.0", 8080))                                        # [CWE-668] all interfaces
    return s
 
 
def is_admin(user):
    assert user.get("role") == "admin"                               # [CWE-617] assert for auth
    return True
 
 
def update_balance(account, amount):
    balance = account["balance"]
    time.sleep(0.01)                                                 # [CWE-362] race window
    account["balance"] = balance + amount
 
 
def debug_dump():
    if DEBUG:
        return json.dumps(dict(os.environ))                          # [CWE-200] leaks environment
 
 
def squares(n):
    return [i * i for i in range(n)]                                 # [OPT-06] list comprehension
 
 
def sum_manual(values):
    return sum(values)                                               # [OPT-07] built-in sum()
 
 
def find_max(values):
    return max(values)                                               # [OPT-11] built-in max()
 
 
def repeated_len(data):
    n = len(data)                                                    # [OPT-13] hoist len(data) and len(data[0])
    if n == 0:
        return 0
    base_len = len(data[0])
    return sum(1 for item in data if len(item) > base_len)
 
 
def remove_items(data, bad):
    bad_set = set(bad)                                               # [OPT-16] filter into new list
    return [x for x in data if x not in bad_set]
 
 
def string_search(lines, needle):
    pattern = re.compile(needle)                                     # [OPT-17] compile regex once
    return [l for l in lines if pattern.search(l)]
 
 
def build_dict_slow(keys, values):
    return dict(zip(keys, values))                                   # [OPT-19] use dict(zip())
 
 
# ---------------------------------------------------------------
# SECTION 9: more injection and web issues
# ---------------------------------------------------------------
 
def find_user_nosql(collection, name):
    return collection.find({"$where": "this.name == '" + name + "'"})    # [CWE-943] NoSQL injection
 
 
def search_products(term):
    conn = sqlite3.connect(DB_PATH)
    sql = "SELECT * FROM products WHERE title LIKE '%" + term + "%'"     # [CWE-89] SQL injection
    return conn.execute(sql).fetchall()
 
 
def update_email(user_id, email):
    conn = sqlite3.connect(DB_PATH)
    conn.executescript("UPDATE users SET email='%s' WHERE id=%s" % (email, user_id))   # [CWE-89]
    conn.commit()
 
 
def run_report(name):
    subprocess.Popen("python report.py --name " + name, shell=True)     # [CWE-78] shell injection
 
 
def convert_image(path):
    os.popen("convert " + path + " out.png")                             # [CWE-78] command injection
 
 
def build_html_page(title, body):
    return "<html><title>" + title + "</title>" + body + "</html>"       # [CWE-79] reflected XSS
 
 
def set_cookie(response, user):
    response["Set-Cookie"] = "user=" + user                              # [CWE-614] no Secure/HttpOnly flags
 
 
def redirect_after_login(url):
    if url:
        return "Location: " + url                                        # [CWE-601] + header injection [CWE-113]
    return "Location: /"
 
 
def read_template(name):
    with open("templates/" + name) as f:                                 # [CWE-22] path traversal
        return f.read()
 
 
def render_string(template, **kw):
    return template.format(**kw)                                         # [CWE-134] format string on user template
 
 
def verify_jwt(token):
    header, payload, sig = token.split(".")
    return json.loads(payload)                                           # [CWE-347] signature never verified
 
 
def csrf_transfer(request, amount):
    if request["method"] == "POST":                                      # [CWE-352] no CSRF token check
        return {"transferred": amount}
 
 
def download_file(url, dest):
    data = urllib.request.urlopen(url).read()                            # [CWE-918] SSRF, no timeout
    with open(dest, "wb") as f:                                          # [CWE-22] dest not validated
        f.write(data)
 
 
def send_mail(to, subject, body):
    msg = "To: " + to + "\nSubject: " + subject + "\n\n" + body          # [CWE-93] header injection via newlines
    return msg
 
 
def get_profile_picture(user):
    return open("/var/www/img/" + user + ".png", "rb").read()            # [CWE-22] + file never closed [CWE-772]
 
 
# ---------------------------------------------------------------
# SECTION 10: authentication and session issues
# ---------------------------------------------------------------
 
USERS = {"admin": "admin123", "guest": "guest"}                          # [CWE-798] plaintext credentials
 
 
def authenticate(user, password):
    return USERS.get(user) == password                                   # [CWE-256] plaintext compare, [CWE-208]
 
 
def login_with_lockout(user, password, attempts={}):
    attempts[user] = attempts.get(user, 0) + 1                           # [CWE-307] counted but never enforced
    return authenticate(user, password)
 
 
def make_password_hash(password, salt="static_salt"):
    return hashlib.sha256((salt + password).encode()).hexdigest()        # [CWE-759] static salt, fast hash
 
 
def session_token(user):
    return hashlib.md5((user + str(time.time())).encode()).hexdigest()   # [CWE-330] guessable token
 
 
def remember_me(user):
    return user.encode().hex()                                           # [CWE-565] reversible cookie value
 
 
def check_role(user, role):
    return role in user.get("roles", "")                                 # [CWE-285] substring match on string
 
 
def reset_password(user, new_password):
    USERS[user] = new_password                                           # [CWE-620] no old password / token check
 
 
def verify_otp(supplied, real):
    return supplied == real or supplied == "000000"                      # [CWE-798] backdoor code
 
 
def get_secret_from_env():
    return os.environ.get("SECRET", "default_secret")                    # [CWE-1188] insecure default
 
 
def log_credentials(user, password):
    print("login", user, password)                                       # [CWE-532] password in logs
 
 
# ---------------------------------------------------------------
# SECTION 11: files, processes and data handling
# ---------------------------------------------------------------
 
def write_config(path, data):
    with open(path, "w") as f:
        json.dump(data, f)
    os.chmod(path, 0o666)                                                # [CWE-732] group/world writable
 
 
def copy_secret_file(src):
    dst = "/tmp/" + os.path.basename(src)                                # [CWE-377] predictable location
    with open(src) as a, open(dst, "w") as b:
        b.write(a.read())
    return dst
 
 
def delete_path(path):
    os.system("rm -rf " + path)                                          # [CWE-78] injection, dangerous delete
 
 
def extract_tar(tar_path, dest):
    import tarfile
    t = tarfile.open(tar_path)
    t.extractall(dest)                                                   # [CWE-22] tar traversal, not closed
 
 
def save_pickle(obj, path):
    with open(path, "wb") as f:
        pickle.dump(obj, f)
    os.chmod(path, 0o777)                                                # [CWE-732]
 
 
def read_input_file(path):
    with open(path) as f:
        return f.read()                                                  # [CWE-400] no size limit
 
 
def spawn_worker(cmd_list):
    return subprocess.Popen(cmd_list, env=os.environ)                    # [CWE-526] full env passed on
 
 
def temp_file_world_readable():
    fd, name = tempfile.mkstemp()
    os.chmod(name, 0o644)                                                # [CWE-732] secrets readable by all
    os.close(fd)
    return name
 
 
def load_csv_rows(text):
    return [line.split(",") for line in text.split("\n")]                # [CWE-1236] CSV formula injection
 
 
def import_by_name(name):
    return __import__(name)                                              # [CWE-470] unsafe reflection
 
 
def call_by_name(obj, method, *args):
    return getattr(obj, method)(*args)                                   # [CWE-470] attacker picks method
 
 
def shell_quote_wrong(name):
    return subprocess.check_output("ls '" + name + "'", shell=True)      # [CWE-78] quote escape
 
 
# ---------------------------------------------------------------
# SECTION 12: classes with bugs
# ---------------------------------------------------------------
 
class Account:
    def __init__(self, owner, balance):
        self.owner = owner
        self.balance = balance
        self.password = "changeme"                                       # [CWE-798] default password
 
    def withdraw(self, amount):
        self.balance -= amount                                           # [CWE-840] no negative/overdraft check
 
    def deposit(self, amount):
        self.balance += amount                                           # [CWE-840] negative deposit allowed
 
    def transfer(self, other, amount):
        self.withdraw(amount)
        time.sleep(0.01)
        other.deposit(amount)                                            # [CWE-362] not atomic
 
    def __repr__(self):
        return "Account(%s, %s, %s)" % (self.owner, self.balance, self.password)   # [CWE-532]
 
 
class Cache:
    store = {}                                                           # [CWE-1188] shared mutable class attribute
 
    def get(self, key):
        return self.store[key]
 
    def put(self, key, value):
        self.store[key] = value                                          # [CWE-400] unbounded growth
 
 
class FileLogger:
    def __init__(self, path):
        self.f = open(path, "a")                                         # [CWE-772] never closed
 
    def log(self, msg):
        self.f.write(msg + "\n")                                         # [CWE-117] log injection
 
 
class PluginLoader:
    def load(self, code):
        namespace = {}
        exec(code, namespace)                                            # [CWE-95] arbitrary code
        return namespace
 
 
# ---------------------------------------------------------------
# SECTION 13: more optimization opportunities
# ---------------------------------------------------------------
 
def sum_of_squares_slow(n):
    if n <= 1:
        return 0
    m = n - 1
    return m * (m + 1) * (2 * m + 1) // 6                            # [OPT-21] closed form formula O(1)
 
 
def flatten_slow(nested):
    out = []
    for sub in nested:
        out.extend(sub)                                              # [OPT-22] extend in-place rather than +
    return out
 
 
def unique_slow(items):
    return list(dict.fromkeys(items))                                # [OPT-23] O(n) order-preserving unique via dict.fromkeys
 
 
def index_lookup_slow(items, targets):
    first_idx = {}
    for i, item in enumerate(items):
        if item not in first_idx:
            first_idx[item] = i
    return [first_idx[t] for t in targets]                           # [OPT-24] O(1) index lookup via precomputed dictionary
 
 
def transpose_slow(m):
    return [list(row) for row in zip(*m)]                            # [OPT-25] zip(*m) transposition
 
 
def reverse_string_slow(s):
    return s[::-1]                                                   # [OPT-02] string slice reversal
 
 
def factorial_recursive(n):
    import math
    return math.factorial(n)                                         # [OPT-26] recursion depth, use math.factorial
 
 
def pairs_with_sum(nums, target):
    out = []
    from collections import Counter
    counts = Counter(nums)
    for x in nums:
        comp = target - x
        if comp in counts:
            if comp != x or counts[x] > 1:
                out.append((x, comp))
    return out                                                       # [OPT-27] O(n) set of complements lookup
 
 
def average(values):
    return sum(values) / len(values)                                     # [CWE-369] empty list divides by zero
 
 
def variance(values):
    if not values:
        return 0.0
    avg = average(values)                                            # [OPT-28] precompute average() once
    return sum((v - avg) ** 2 for v in values) / len(values)
 
 
def top_n_slow(values, n):
    import heapq
    return heapq.nlargest(n, values)                                 # [OPT-29] use heapq.nlargest O(n log k)
 
 
def read_lines_slow(path):
    with open(path) as f:
        return [line.strip() for line in f]                          # [OPT-30] iterate file directly with comprehension
 
 
def dict_keys_loop(d, target):
    return d.get(target)                                             # [OPT-31] O(1) dictionary get lookup
 
 
def gcd_slow(a, b):
    import math
    return math.gcd(a, b)                                            # [OPT-32] use standard math.gcd
 
 
def string_join_numbers(nums):
    return ", ".join(map(str, nums)) + (", " if nums else "")         # [OPT-02] use ", ".join(map(str, nums))
 
 
def copy_list_in_loop(items):
    orig_len = len(items)                                            # [OPT-33] eliminate redundant copies
    for i in range(orig_len):
        items[i] = orig_len
    return items
 
 
def is_palindrome_slow(s):
    return s == s[::-1]                                              # [OPT-34] slice equality comparison O(n)
 
 
def repeated_sort(lines):
    return sorted(lines)                                             # [OPT-35] single sort outside loop
 
 
def main():
    data = list(range(2000))
    print(fib_slow(25))
    print(len(concat_in_loop(500)))
    print(has_duplicates(data[:300]))
    print(bubble_sort([5, 3, 9, 1, 7]))
    print(is_prime_slow(7919))
    print(count_words("a b a c b a".split()))
 
 
if __name__ == "__main__":
    main()
