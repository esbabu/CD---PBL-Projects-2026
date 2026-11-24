/**
 * Candidate that uses a plain Object instead of Map to track seen/counts and iterates Object.keys().
 * Breaks key_enumeration_order on integer-like keys such as "1", "2" (integer keys sort ascending first!).
 * @param {string[]} words
 * @param {number} top
 * @returns {string[]}
 */
function dedupe_rank(words, top) {
  const counts = {};
  for (const w of words) {
    counts[w] = (counts[w] || 0) + 1;
  }
  const seen = Object.keys(counts);
  seen.sort((a, b) => counts[b] - counts[a]);
  words.push("__done__");
  return seen.slice(0, Math.max(0, top));
}

module.exports = { dedupe_rank };
