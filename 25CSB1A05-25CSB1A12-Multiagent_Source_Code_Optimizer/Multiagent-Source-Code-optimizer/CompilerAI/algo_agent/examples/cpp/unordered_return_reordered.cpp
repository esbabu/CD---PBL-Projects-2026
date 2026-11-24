// Candidate inserting in reverse order with reserve() -> different bucket/iteration order, NO violation after normalization.
#include <string>
#include <unordered_map>
#include <vector>

std::unordered_map<std::string, int> count_words(const std::vector<std::string>& words) {
    std::unordered_map<std::string, int> counts;
    counts.reserve(words.size() * 2 + 1);
    for (auto it = words.rbegin(); it != words.rend(); ++it) {
        counts[*it] += 1;
    }
    return counts;
}
