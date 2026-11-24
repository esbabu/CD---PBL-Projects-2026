import { describe, it } from 'node:test';
import assert from 'node:assert';
import { getTransformationLine } from '../utils/transformationLineResolver';

describe('transformationLineResolver', () => {
  const sampleCode = `// Four Sum Program
#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

vector<vector<int>> fourSum(vector<int>& nums, int target) {
    int n = nums.size();
    vector<vector<int>> ans;
    sort(nums.begin(), nums.end());

    for (int i = 0; i < n; i++) {
        if (i > 0 && nums[i] == nums[i - 1]) continue;
        for (int j = i + 1; j < n; j++) {
            if (j > i + 1 && nums[j] == nums[j - 1]) continue;
            int k = j + 1;
            int l = n - 1;
            while (k < l) {
                long long sum = nums[i] + nums[j];
                sum += nums[k];
                sum += nums[l];
                if (sum == target) {
                    ans.push_back({nums[i], nums[j], nums[k], nums[l]});
                    k++;
                    l--;
                    while (k < l && nums[k] == nums[k - 1]) k++;
                    while (k < l && nums[l] == nums[l + 1]) l--;
                } else if (sum < target) {
                    k++;
                } else {
                    l--;
                }
            }
        }
    }
    return ans;
}
`;

  it('detects explicit line prefix "Line 14:"', () => {
    const line = getTransformationLine('Line 14: Replaced O(N^2) loop with two pointer', sampleCode);
    assert.strictEqual(line, 14);
  });

  it('detects explicit line inside text "at line 22"', () => {
    const line = getTransformationLine('Pruned redundant loop branches at line 22', sampleCode);
    assert.strictEqual(line, 22);
  });

  it('detects bracketed line format "[Line 8]"', () => {
    const line = getTransformationLine('[Line 8] Pre-sorted nums array for two-pointer technique', sampleCode);
    assert.strictEqual(line, 8);
  });

  it('detects line via diff comparison when line number is omitted', () => {
    const modifiedCode = sampleCode.replace('int n = nums.size();', 'const int n = static_cast<int>(nums.size());');
    const line = getTransformationLine('Cached vector size into const variable', sampleCode, modifiedCode, 0);
    assert.strictEqual(line, 9);
  });

  it('detects loop line when transformation mentions loop', () => {
    const line = getTransformationLine('Replaced nested loops with two-pointer technique', sampleCode);
    assert.strictEqual(line, 13);
  });

  it('falls back safely to first executable line on unmatched text instead of line 1 header', () => {
    const line = getTransformationLine('Arbitrary description with no code tokens', sampleCode);
    // Line 8 is "vector<vector<int>> fourSum..."
    assert.strictEqual(line, 8);
  });
});
