/**
 * O(n log n) equivalent two_sum using value -> sorted index list + binary search.
 * Preserves lexicographically smallest (i, j).
 * @param {number[]} nums
 * @param {number} target
 * @returns {number[]}
 */
function two_sum(nums, target) {
  const pos = new Map();
  for (let idx = 0; idx < nums.length; idx++) {
    const v = nums[idx];
    let lst = pos.get(v);
    if (!lst) {
      lst = [];
      pos.set(v, lst);
    }
    lst.push(idx);
  }
  for (let i = 0; i < nums.length; i++) {
    const lst = pos.get(target - nums[i]);
    if (lst) {
      let lo = 0;
      let hi = lst.length;
      while (lo < hi) {
        const mid = (lo + hi) >> 1;
        if (lst[mid] <= i) lo = mid + 1;
        else hi = mid;
      }
      if (lo < lst.length) {
        return [i, lst[lo]];
      }
    }
  }
  return [];
}

module.exports = { two_sum };
