/**
 * Return indices of the first pair (lexicographically by (i, j)) adding up to target.
 * @param {number[]} nums
 * @param {number} target
 * @returns {number[]}
 */
function two_sum(nums, target) {
  for (let i = 0; i < nums.length; i++) {
    for (let j = i + 1; j < nums.length; j++) {
      if (nums[i] + nums[j] === target) {
        return [i, j];
      }
    }
  }
  return [];
}

module.exports = { two_sum };
