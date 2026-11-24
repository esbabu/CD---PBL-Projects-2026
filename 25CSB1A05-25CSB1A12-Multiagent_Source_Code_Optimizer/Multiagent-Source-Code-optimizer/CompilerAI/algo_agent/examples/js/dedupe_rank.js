/**
 * Deduplicate words preserving first-seen order, rank by descending frequency (stable),
 * mutate caller's array by pushing "__done__", and return top k words.
 * @param {string[]} words
 * @param {number} top
 * @returns {string[]}
 */
function dedupe_rank(words, top) {
  const seen = [];
  for (let i = 0; i < words.length; i++) {
    const w = words[i];
    if (!seen.includes(w)) {
      seen.push(w);
    }
  }
  const counts = new Map();
  for (let i = 0; i < words.length; i++) {
    const w = words[i];
    counts.set(w, (counts.get(w) || 0) + 1);
  }
  seen.sort((a, b) => counts.get(b) - counts.get(a));
  words.push("__done__"); // quirk: mutates caller's array
  return seen.slice(0, Math.max(0, top));
}

module.exports = { dedupe_rank };
