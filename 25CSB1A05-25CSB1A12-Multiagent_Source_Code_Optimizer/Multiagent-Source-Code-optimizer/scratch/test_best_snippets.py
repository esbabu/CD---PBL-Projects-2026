import json
import re

with open('scratch/vulnerable_samples.cpp', 'r', encoding='utf-8') as f:
    cpp_lines = [l.rstrip('\r\n') for l in f.readlines()]

with open('scratch/vulnerable_samples.py', 'r', encoding='utf-8') as f:
    py_lines = [l.rstrip('\r\n') for l in f.readlines()]

with open('scratch/all_198_metadata.json', 'r', encoding='utf-8') as f:
    metadata = json.load(f)

def extract_line_number(line_str):
    m = re.search(r'\d+', str(line_str))
    return int(m.group()) if m else None

def get_exact_cpp_function(name):
    pattern = rf'\b{name}\s*\('
    for i, line in enumerate(cpp_lines):
        if re.search(pattern, line) and not line.strip().startswith('//') and not line.strip().startswith('cout'):
            start = i
            # Find declaration start if previous line had return type
            if start > 0 and cpp_lines[start-1].strip() in ('void', 'int', 'bool', 'char*', 'string'):
                start -= 1
            brace_count = 0
            started = False
            for j in range(start, min(len(cpp_lines), start + 25)):
                brace_count += cpp_lines[j].count('{') - cpp_lines[j].count('}')
                if '{' in cpp_lines[j]:
                    started = True
                if started and brace_count <= 0:
                    return '\n'.join(cpp_lines[start:j+1])
    return None

def get_exact_py_function(name):
    pattern = rf'def\s+{name}\s*\('
    for i, line in enumerate(py_lines):
        if re.search(pattern, line):
            start = i
            end = i
            for j in range(start + 1, min(len(py_lines), start + 25)):
                l = py_lines[j]
                if l.startswith(('def ', 'class ', '# -')):
                    break
                if l == '' and j + 1 < len(py_lines) and py_lines[j+1].startswith(('def ', '# -')):
                    break
                end = j
            snippet = '\n'.join(py_lines[start:end+1]).strip()
            return snippet
    return None

def get_cpp_snippet_by_line(line_num):
    if not line_num or line_num < 1 or line_num > len(cpp_lines):
        return ""
    idx = line_num - 1
    if idx < 32 and ('#define' in cpp_lines[idx] or '=' in cpp_lines[idx]):
        return cpp_lines[idx].strip()
    start = max(0, idx - 2)
    end = min(len(cpp_lines) - 1, idx + 3)
    return '\n'.join(cpp_lines[start:end+1])

def get_py_snippet_by_line(line_num):
    if not line_num or line_num < 1 or line_num > len(py_lines):
        return ""
    idx = line_num - 1
    if idx < 32 and '=' in py_lines[idx]:
        return py_lines[idx].strip()
    start = max(0, idx - 2)
    end = min(len(py_lines) - 1, idx + 3)
    return '\n'.join(py_lines[start:end+1])

starter_snippets = {
    195: """int sumArray(int* arr, int n) {
    int sum = 0;
    for (int i = 0; i < n; i++) {
        sum += arr[i];
    }
    return sum;
}""",
    196: """def two_sum(nums: list[int], target: int) -> list[int]:
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []""",
    197: """void copy_input(const char* user_input) {
    char buf[64];
    strcpy(buf, user_input); /* CWE-121: unbounded copy */
    printf(buf);             /* CWE-134: format string */
}""",
    198: """function twoSum(nums, target) {
    for (let i = 0; i < nums.length; i++) {
        for (let j = i + 1; j < nums.length; j++) {
            if (nums[i] + nums[j] === target) {
                return [i, j];
            }
        }
    }
    return [];
}"""
}

# Find snippet for item
def extract_best_snippet(item):
    tc_num = item['tc_num']
    if tc_num in starter_snippets:
        return starter_snippets[tc_num]
        
    suite = item['suite']
    title = item['title']
    desc = item['description']
    line_num = extract_line_number(item['line'])
    
    # Check for function name in backticks `fn`
    backticks = re.findall(r'`([a-zA-Z0-9_]+)`', title + ' ' + desc)
    # Check for 'in fn'
    in_fn = re.findall(r'in\s+([a-zA-Z0-9_]+)', title + ' ' + desc)
    # Check for 'fn('
    call_fn = re.findall(r'\b([a-zA-Z0-9_]+)\s*\(', title + ' ' + desc)
    
    candidates = backticks + in_fn + call_fn
    
    if suite == 'cpp':
        for cand in candidates:
            res = get_exact_cpp_function(cand)
            if res:
                return res
        return get_cpp_snippet_by_line(line_num)
    else:
        for cand in candidates:
            res = get_exact_py_function(cand)
            if res:
                return res
        return get_py_snippet_by_line(line_num)

snippets = {}
for item in metadata:
    s = extract_best_snippet(item)
    snippets[item['tc_num']] = s

print('Total snippets extracted:', len(snippets))
print('Any empty?', any(not s.strip() for s in snippets.values()))

# Print 5 random samples
for idx in [5, 25, 70, 110, 175]:
    print(f"\n================ TC {idx} ================")
    print(metadata[idx-1]['title'])
    print("CODE:")
    print(snippets[idx])
