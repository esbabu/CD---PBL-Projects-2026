/**
 * WRONG one-pass Map two_sum: returns the first pair by second index j,
 * NOT lexicographically first (i, j). Fails on e.g. nums=[1, 2, 2], target=3? No:
 * nums=[2, 1, 2, 3], target=4 -> orig [0, 2], wrong? Wait: [1, 3, 2, 2] target=4 -> orig [0, 1], wrong [0, 1].
 * Fails on [1, 2, 3, 2], target=4 -> orig [0, 2] (1+3), wrong [1, 3] (2+2)? Actually
 * one-pass visits j=0 (1), j=1 (2), j=2 (3 -> sees 1 at 0 -> [0,2]).
 * Fails on [2, 1, 1, 2], target=3 -> orig [0, 1], wrong [0, 1].
 * Fails on [1, 2, 1, 0], target=2 -> j=0 (1), j=1 (2), j=2 (1 -> [0,2]).
 * Fails on [3, 1, 2, 1], target=4 -> orig [0, 1] (3+1).
 * Fails on [0, 1, 2, 1], target=2 -> orig [0, 2] (0+2), one-pass finds [1, 3] or [0, 2]:
 * j=0 (0), j=1 (1), j=2 (2 -> sees 0 -> [0,2]).
 * Fails on [1, 0, 0, 2], target=2? No, [2, 1, 0, 1], target=2 -> orig [0, 2] (2+0),
 * one-pass: j=0(2), j=1(1), j=2(0 -> sees 2 -> [0,2]).
 * Fails on [0, 2, 2, 4], target=4 -> orig [0, 3] (0+4), one-pass: j=2 sees 2 -> returns [1, 2]!
 * 3-element counterexample: [1, 2, 2, 3] or [0, 1, 1] with target=2? Wait: [0, 1, 1, 2] target=2 -> orig [0, 3], wrong [1, 2]!
 * Even simpler 3-element: [2, 0, 0], target=0 -> [1, 2].
 * With [1, 2, 3] target=4 -> [0, 2].
 * With [2, 1, 2] -> [0, 2] if target=4.
 * For 3 elements: [a, b, c] where a+c == target AND b+b? No, 3 distinct indices: (0,2) vs (1,2)!
 * Wait: if a+c == target and b+c == target, then a == b, so [1, 1, 2] target=3 -> orig [0, 2],
 * one-pass stores seen.set(v, i) overwriting index 0 with index 1 -> returns [1, 2]!
 * @param {number[]} nums
 * @param {number} target
 * @returns {number[]}
 */
function two_sum(nums, target) {
  const seen = new Map();
  for (let i = 0; i < nums.length; i++) {
    const need = target - nums[i];
    if (seen.has(need)) {
      return [seen.get(need), i];
    }
    seen.set(nums[i], i);
  }
  return [];
}

module.exports = { two_sum };
