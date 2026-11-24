// Returns std::unordered_map: iteration order is implementation-defined, normalized by CppAdapter.
#include <string>
#include <unordered_map>
#include <vector>

std::unordered_map<std::string, int> count_words(const std::vector<std::string>& words) {
    std::unordered_map<std::string, int> counts;
    for (const auto& w : words) {
        counts[w] += 1;
    }
    return counts;
}
