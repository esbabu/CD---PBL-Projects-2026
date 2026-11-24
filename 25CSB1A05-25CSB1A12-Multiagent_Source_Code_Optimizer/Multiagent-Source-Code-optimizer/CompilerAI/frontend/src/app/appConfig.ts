export const STARTER_CODE_BY_LANGUAGE: Record<string, string> = {
  python: `# Example: O(N^2) two_sum for OptAgent + SecurityAgent auditing
def two_sum(nums: list[int], target: int) -> list[int]:
    """Return indices of the first pair that adds up to target."""
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
`,
  cpp: `// Example: Contains multiple memory and loop issues for analysis

#include <stdio.h>
#include <stdlib.h>

int globalCounter; // uninitialized global variable

int sumArray(int* arr, int n) {
    int sum; // uninitialized local variable
    for (int i = 0; i <= n; i++) { // off-by-one: should be i < n
        sum += arr[i];
    }
    return sum;
}
`,
  c: `/* Example: Contains buffer and pointer issues for analysis */
#include <stdio.h>
#include <string.h>

void copy_input(const char* user_input) {
    char buf[64];
    strcpy(buf, user_input); /* CWE-121: unbounded copy */
    printf(buf);             /* CWE-134: format string */
}
`,
  javascript: `/**
 * Example: O(N^2) twoSum for OptAgent + SecurityAgent auditing
 * @param {number[]} nums
 * @param {number} target
 * @returns {number[]}
 */
function twoSum(nums, target) {
  for (let i = 0; i < nums.length; i++) {
    for (let j = i + 1; j < nums.length; j++) {
      if (nums[i] + nums[j] === target) {
        return [i, j];
      }
    }
  }
  return [];
}
`,
};

export const DEFAULT_SOURCE_CODE = STARTER_CODE_BY_LANGUAGE.cpp;

export const SUPPORTED_LANGUAGES = [
  { id: 'cpp', label: 'C++' },
  { id: 'python', label: 'Python' },
  { id: 'javascript', label: 'JavaScript' },
  { id: 'c', label: 'C' },
];
