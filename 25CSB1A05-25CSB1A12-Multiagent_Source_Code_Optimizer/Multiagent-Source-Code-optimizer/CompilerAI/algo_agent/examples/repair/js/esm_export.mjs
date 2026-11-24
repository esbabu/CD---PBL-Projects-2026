/**
 * @param {number[]} items
 * @returns {number[]}
 */
export function uniqueValues(items) {
    const seen = [];
    for (const x of items) {
        if (!seen.includes(x)) {
            seen.push(x);
        }
    }
    return seen;
}
