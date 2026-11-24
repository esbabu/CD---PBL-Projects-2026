/**
 * @param {number[]} nums
 * @returns {Promise<number>}
 */
async function asyncSum(nums) {
    let total = 0;
    for (const x of nums) {
        total += x;
    }
    return total;
}
