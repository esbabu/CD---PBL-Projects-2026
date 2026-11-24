/**
 * @param {number[]} nums
 * @param {number} target
 * @returns {number[]}
 */
function twoSum(nums, target) {
    const pos = new Map();
    for (let idx = 0; idx < nums.length; idx++) {
        const v = nums[idx];
        if (!pos.has(v)) pos.set(v, []);
        pos.get(v).push(idx);
    }
    for (let i = 0; i < nums.length; i++) {
        const lst = pos.get(target - nums[i]);
        if (lst) {
            for (const j of lst) {
                if (j > i) return [i, j];
            }
        }
    }
    return [];
}
