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

def get_cpp_snippet(line_num):
    if not line_num or line_num < 1 or line_num > len(cpp_lines):
        return ""
    idx = line_num - 1
    
    # Check if single line definition (macros or global vars)
    if idx < 32 and ('#define' in cpp_lines[idx] or '=' in cpp_lines[idx]):
        return cpp_lines[idx].strip()
    
    # Scan backward for function start or struct/class
    start = idx
    while start > 0:
        l = cpp_lines[start].strip()
        if l.startswith(('void ', 'int ', 'char ', 'long ', 'bool ', 'double ', 'float ', 'auto ', 'Account', 'Buffer', 'Base', 'struct ', 'class ', 'std::')):
            break
        if start < idx - 8:
            break
        start -= 1
        
    # Scan forward for closing brace
    end = idx
    brace_count = 0
    started = False
    for i in range(start, min(len(cpp_lines), idx + 15)):
        line_str = cpp_lines[i]
        brace_count += line_str.count('{') - line_str.count('}')
        if '{' in line_str:
            started = True
        if started and brace_count <= 0 and i >= idx:
            end = i
            break
        end = i

    snippet_lines = cpp_lines[start:end+1]
    # Remove empty lines at edges
    while snippet_lines and not snippet_lines[0].strip():
        snippet_lines.pop(0)
    while snippet_lines and not snippet_lines[-1].strip():
        snippet_lines.pop()
    return '\n'.join(snippet_lines)

def get_py_snippet(line_num):
    if not line_num or line_num < 1 or line_num > len(py_lines):
        return ""
    idx = line_num - 1
    
    # Check if global constant
    if idx < 30 and '=' in py_lines[idx]:
        return py_lines[idx].strip()
        
    # Scan backward for def or class
    start = idx
    while start > 0:
        l = py_lines[start].strip()
        if l.startswith(('def ', 'class ')):
            break
        if start < idx - 10:
            break
        start -= 1
        
    # Scan forward until next def/class or empty line before top-level
    end = idx
    for i in range(idx, min(len(py_lines), idx + 12)):
        if i > idx and (py_lines[i].startswith(('def ', 'class ')) or (py_lines[i] == '' and i+1 < len(py_lines) and not py_lines[i+1].startswith((' ', '\t', '#', '')))):
            break
        end = i

    snippet_lines = py_lines[start:end+1]
    while snippet_lines and not snippet_lines[0].strip():
        snippet_lines.pop(0)
    while snippet_lines and not snippet_lines[-1].strip():
        snippet_lines.pop()
    return '\n'.join(snippet_lines)

starter_snippets = {
    195: """int sumArray(int* arr, int n) {
    int sum;
    for (int i = 0; i <= n; i++) {
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

# Test extraction for all 198 items
snippets = {}
for item in metadata:
    tc_num = item['tc_num']
    suite = item['suite']
    line_num = extract_line_number(item['line'])
    
    if tc_num in starter_snippets:
        snip = starter_snippets[tc_num]
    elif suite == 'cpp':
        snip = get_cpp_snippet(line_num)
    else:
        snip = get_py_snippet(line_num)
        
    snippets[tc_num] = snip

print('Extracted snippets count:', len(snippets))
empty_count = sum(1 for s in snippets.values() if not s.strip())
print('Empty snippets count:', empty_count)

for test_id in [1, 3, 20, 67, 88, 92, 161, 195]:
    print(f'\n--- Snippet for TC {test_id} ---')
    print(snippets[test_id])
