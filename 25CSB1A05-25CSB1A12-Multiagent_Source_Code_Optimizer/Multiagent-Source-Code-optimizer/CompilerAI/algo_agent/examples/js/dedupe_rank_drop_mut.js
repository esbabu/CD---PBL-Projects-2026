/**
 * Candidate that drops the `words.push("__done__")` mutation -> caught by arg_mutation.
 * @param {string[]} words
 * @param {number} top
 * @returns {string[]}
 */
function dedupe_rank(words, top) {
  const seen = [];
  const seenSet = new Set();
  const counts = new Map();
  for (const w of words) {
    if (!seenSet.has(w)) {
      seenSet.add(w);
      seen.push(w);
    }
    counts.set(w, (counts.get(w) || 0) + 1);
  }
  seen.sort((a, b) => counts.get(b) - counts.get(a));
  return seen.slice(0, Math.max(0, top));
}

module.exports = { dedupe_rank };
