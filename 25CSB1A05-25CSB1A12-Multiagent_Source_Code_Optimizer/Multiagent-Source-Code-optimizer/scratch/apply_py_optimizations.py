"""
Script to generate vulnerable_samples_optimized.py from scratch/vulnerable_samples.py
"""
import re

def build_optimized():
    with open('scratch/vulnerable_samples.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # We replace each target function body or function definition
    replacements = [
        # 1. fib_slow
        (
'''def fib_slow(n):                                                     # [OPT-01] exponential recursion
    if n <= 1:
        return n
    return fib_slow(n - 1) + fib_slow(n - 2)''',
'''def fib_slow(n):                                                     # [OPT-01] iterative O(n) memoized
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a'''
        ),

        # 2. concat_in_loop
        (
'''def concat_in_loop(n):
    s = ""
    for i in range(n):
        s = s + "item" + str(i) + ","                                # [OPT-02] use list + join
    return s''',
'''def concat_in_loop(n):
    return "".join(f"item{i}," for i in range(n))                    # [OPT-02] list comprehension with join'''
        ),

        # 3. has_duplicates
        (
'''def has_duplicates(items):
    for i in range(len(items)):                                      # [OPT-03] O(n^2), use set
        for j in range(i + 1, len(items)):
            if items[i] == items[j]:
                return True
    return False''',
'''def has_duplicates(items):
    return len(items) != len(set(items))                             # [OPT-03] O(n) set comparison'''
        ),

        # 4. membership_in_list
        (
'''def membership_in_list(queries, allowed):
    out = []
    for q in queries:
        if q in allowed:                                             # [OPT-04] list lookup O(n), use set
            out.append(q)
    return out''',
'''def membership_in_list(queries, allowed):
    allowed_set = set(allowed)                                       # [OPT-04] O(1) set lookup
    return [q for q in queries if q in allowed_set]'''
        ),

        # 5. bubble_sort
        (
'''def bubble_sort(arr):
    n = len(arr)
    for i in range(n):                                               # [OPT-05] use sorted()/list.sort()
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr''',
'''def bubble_sort(arr):
    return sorted(arr)                                               # [OPT-05] use Timsort O(n log n)'''
        ),

        # 6. loop_invariant
        (
'''def loop_invariant(data, a, b):
    out = []
    for x in data:
        out.append(x * (a ** 2 + b ** 2) ** 0.5)                     # [OPT-08] invariant inside loop
    return out''',
'''def loop_invariant(data, a, b):
    factor = (a ** 2 + b ** 2) ** 0.5                               # [OPT-08] hoist invariant outside loop
    return [x * factor for x in data]'''
        ),

        # 7. count_words
        (
'''def count_words(words):
    counts = {}
    for w in words:
        if w in counts:                                              # [OPT-09] use Counter/defaultdict
            counts[w] = counts[w] + 1
        else:
            counts[w] = 1
    return counts''',
'''def count_words(words):
    from collections import Counter
    return dict(Counter(words))                                      # [OPT-09] use collections.Counter'''
        ),

        # 8. read_big_file
        (
'''def read_big_file(path):
    with open(path) as f:
        lines = f.readlines()                                        # [OPT-10] loads whole file in memory
    total = 0
    for line in lines:
        total += len(line)
    return total''',
'''def read_big_file(path):
    total = 0
    with open(path) as f:
        for line in f:                                               # [OPT-10] stream file line by line
            total += len(line)
    return total'''
        ),

        # 9. is_prime_slow
        (
'''def is_prime_slow(n):
    if n < 2:
        return False
    for i in range(2, n):                                            # [OPT-12] stop at sqrt(n)
        if n % i == 0:
            return False
    return True''',
'''def is_prime_slow(n):
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
    return True'''
        ),

        # 10. matrix_multiply
        (
'''def matrix_multiply(A, B):
    n = len(A)
    C = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            for k in range(n):
                C[i][j] += A[i][k] * B[k][j]                         # [OPT-14] use numpy
    return C''',
'''def matrix_multiply(A, B):
    try:
        import numpy as np
        return (np.array(A) @ np.array(B)).tolist()                  # [OPT-14] vectorized matrix multiply
    except ImportError:
        n = len(A)
        return [[sum(A[i][k] * B[k][j] for k in range(n)) for j in range(n)] for i in range(n)]'''
        ),

        # 11. squares
        (
'''def squares(n):
    result = []
    for i in range(n):
        result.append(i * i)                                         # [OPT-06] list comprehension
    return result''',
'''def squares(n):
    return [i * i for i in range(n)]                                 # [OPT-06] list comprehension'''
        ),

        # 12. sum_manual
        (
'''def sum_manual(values):
    total = 0
    for i in range(len(values)):                                     # [OPT-07] use sum()
        total = total + values[i]
    return total''',
'''def sum_manual(values):
    return sum(values)                                               # [OPT-07] built-in sum()'''
        ),

        # 13. find_max
        (
'''def find_max(values):
    best = values[0]
    for i in range(1, len(values)):                                  # [OPT-11] use max()
        if values[i] > best:
            best = values[i]
    return best''',
'''def find_max(values):
    return max(values)                                               # [OPT-11] built-in max()'''
        ),

        # 14. repeated_len
        (
'''def repeated_len(data):
    count = 0
    i = 0
    while i < len(data):                                             # [OPT-13] len() each pass
        if len(data[i]) > len(data[0]):
            count += 1
        i += 1
    return count''',
'''def repeated_len(data):
    n = len(data)                                                    # [OPT-13] hoist len(data) and len(data[0])
    if n == 0:
        return 0
    base_len = len(data[0])
    return sum(1 for item in data if len(item) > base_len)'''
        ),

        # 15. remove_items
        (
'''def remove_items(data, bad):
    for x in data:
        if x in bad:
            data.remove(x)                                           # [OPT-16] remove while iterating
    return data''',
'''def remove_items(data, bad):
    bad_set = set(bad)                                               # [OPT-16] filter into new list
    return [x for x in data if x not in bad_set]'''
        ),

        # 16. string_search
        (
'''def string_search(lines, needle):
    return [l for l in lines if re.search(needle, l)]                # [OPT-17] compile regex once''',
'''def string_search(lines, needle):
    pattern = re.compile(needle)                                     # [OPT-17] compile regex once
    return [l for l in lines if pattern.search(l)]'''
        ),

        # 17. build_dict_slow
        (
'''def build_dict_slow(keys, values):
    d = {}
    for i in range(len(keys)):                                       # [OPT-19] use dict(zip())
        d[keys[i]] = values[i]
    return d''',
'''def build_dict_slow(keys, values):
    return dict(zip(keys, values))                                   # [OPT-19] use dict(zip())'''
        ),

        # 18. sum_of_squares_slow
        (
'''def sum_of_squares_slow(n):
    total = 0
    for i in range(n):
        total += i ** 2                                                  # [OPT-21] closed form exists
    return total''',
'''def sum_of_squares_slow(n):
    if n <= 1:
        return 0
    m = n - 1
    return m * (m + 1) * (2 * m + 1) // 6                            # [OPT-21] closed form formula O(1)'''
        ),

        # 19. flatten_slow
        (
'''def flatten_slow(nested):
    out = []
    for sub in nested:
        out = out + sub                                                  # [OPT-22] builds a new list each time
    return out''',
'''def flatten_slow(nested):
    out = []
    for sub in nested:
        out.extend(sub)                                              # [OPT-22] extend in-place rather than +
    return out'''
        ),

        # 20. unique_slow
        (
'''def unique_slow(items):
    result = []
    for x in items:
        if x not in result:                                              # [OPT-23] O(n^2), use dict.fromkeys
            result.append(x)
    return result''',
'''def unique_slow(items):
    return list(dict.fromkeys(items))                                # [OPT-23] O(n) order-preserving unique via dict.fromkeys'''
        ),

        # 21. index_lookup_slow
        (
'''def index_lookup_slow(items, targets):
    return [items.index(t) for t in targets]                             # [OPT-24] O(n) index per target''',
'''def index_lookup_slow(items, targets):
    first_idx = {}
    for i, item in enumerate(items):
        if item not in first_idx:
            first_idx[item] = i
    return [first_idx[t] for t in targets]                           # [OPT-24] O(1) index lookup via precomputed dictionary'''
        ),

        # 22. transpose_slow
        (
'''def transpose_slow(m):
    out = []
    for j in range(len(m[0])):
        row = []
        for i in range(len(m)):
            row.append(m[i][j])                                          # [OPT-25] use zip(*m)
        out.append(row)
    return out''',
'''def transpose_slow(m):
    return [list(row) for row in zip(*m)]                            # [OPT-25] zip(*m) transposition'''
        ),

        # 23. reverse_string_slow
        (
'''def reverse_string_slow(s):
    r = ""
    for ch in s:
        r = ch + r                                                       # [OPT-02] quadratic string building
    return r''',
'''def reverse_string_slow(s):
    return s[::-1]                                                   # [OPT-02] string slice reversal'''
        ),

        # 24. factorial_recursive
        (
'''def factorial_recursive(n):
    if n == 0:
        return 1
    return n * factorial_recursive(n - 1)                                # [OPT-26] recursion depth, use math.factorial''',
'''def factorial_recursive(n):
    import math
    return math.factorial(n)                                         # [OPT-26] recursion depth, use math.factorial'''
        ),

        # 25. pairs_with_sum
        (
'''def pairs_with_sum(nums, target):
    out = []
    for i in range(len(nums)):
        for j in range(len(nums)):                                       # [OPT-27] O(n^2), use a set of complements
            if i != j and nums[i] + nums[j] == target:
                out.append((nums[i], nums[j]))
    return out''',
'''def pairs_with_sum(nums, target):
    out = []
    from collections import Counter
    counts = Counter(nums)
    for x in nums:
        comp = target - x
        if comp in counts:
            if comp != x or counts[x] > 1:
                out.append((x, comp))
    return out                                                       # [OPT-27] O(n) set of complements lookup'''
        ),

        # 26. variance
        (
'''def variance(values):
    return sum((v - average(values)) ** 2 for v in values) / len(values)   # [OPT-28] average() per element''',
'''def variance(values):
    if not values:
        return 0.0
    avg = average(values)                                            # [OPT-28] precompute average() once
    return sum((v - avg) ** 2 for v in values) / len(values)'''
        ),

        # 27. top_n_slow
        (
'''def top_n_slow(values, n):
    return sorted(values, reverse=True)[:n]                              # [OPT-29] use heapq.nlargest''',
'''def top_n_slow(values, n):
    import heapq
    return heapq.nlargest(n, values)                                 # [OPT-29] use heapq.nlargest O(n log k)'''
        ),

        # 28. read_lines_slow
        (
'''def read_lines_slow(path):
    out = []
    f = open(path)
    line = f.readline()
    while line:
        out.append(line.strip())                                         # [OPT-30] iterate file directly
        line = f.readline()
    return out''',
'''def read_lines_slow(path):
    with open(path) as f:
        return [line.strip() for line in f]                          # [OPT-30] iterate file directly with comprehension'''
        ),

        # 29. dict_keys_loop
        (
'''def dict_keys_loop(d, target):
    for k in d.keys():                                                   # [OPT-31] "in d" is O(1)
        if k == target:
            return d[k]
    return None''',
'''def dict_keys_loop(d, target):
    return d.get(target)                                             # [OPT-31] O(1) dictionary get lookup'''
        ),

        # 30. gcd_slow
        (
'''def gcd_slow(a, b):
    g = 1
    for i in range(1, min(a, b) + 1):                                    # [OPT-32] use math.gcd
        if a % i == 0 and b % i == 0:
            g = i
    return g''',
'''def gcd_slow(a, b):
    import math
    return math.gcd(a, b)                                            # [OPT-32] use standard math.gcd'''
        ),

        # 31. string_join_numbers
        (
'''def string_join_numbers(nums):
    s = ""
    for n in nums:
        s += str(n) + ", "                                               # [OPT-02] use ", ".join(map(str, nums))
    return s''',
'''def string_join_numbers(nums):
    return ", ".join(map(str, nums)) + (", " if nums else "")         # [OPT-02] use ", ".join(map(str, nums))'''
        ),

        # 32. copy_list_in_loop
        (
'''def copy_list_in_loop(items):
    for i in range(len(items)):
        snapshot = items[:]                                              # [OPT-33] full copy every iteration
        items[i] = len(snapshot)
    return items''',
'''def copy_list_in_loop(items):
    orig_len = len(items)                                            # [OPT-33] eliminate redundant copies
    for i in range(orig_len):
        items[i] = orig_len
    return items'''
        ),

        # 33. is_palindrome_slow
        (
'''def is_palindrome_slow(s):
    for i in range(len(s)):
        if s[i] != s[len(s) - 1 - i]:                                    # [OPT-34] checks each pair twice
            return False
    return True''',
'''def is_palindrome_slow(s):
    return s == s[::-1]                                              # [OPT-34] slice equality comparison O(n)'''
        ),

        # 34. repeated_sort
        (
'''def repeated_sort(lines):
    for _ in range(len(lines)):
        lines = sorted(lines)                                            # [OPT-35] sort inside loop
    return lines''',
'''def repeated_sort(lines):
    return sorted(lines)                                             # [OPT-35] single sort outside loop'''
        )
    ]

    opt = content
    applied = 0
    for target, repl in replacements:
        target_norm = target.replace('\r\n', '\n').strip()
        opt_norm = opt.replace('\r\n', '\n')
        if target_norm in opt_norm:
            opt = opt_norm.replace(target_norm, repl.replace('\r\n', '\n').strip())
            applied += 1
        else:
            print(f"FAILED to match target: {target_norm[:40]}...")

    print(f"Applied {applied}/{len(replacements)} optimization transformations.")
    with open('scratch/vulnerable_samples_optimized.py', 'w', encoding='utf-8') as f:
        f.write(opt)
    print("Saved scratch/vulnerable_samples_optimized.py successfully!")

if __name__ == '__main__':
    build_optimized()
