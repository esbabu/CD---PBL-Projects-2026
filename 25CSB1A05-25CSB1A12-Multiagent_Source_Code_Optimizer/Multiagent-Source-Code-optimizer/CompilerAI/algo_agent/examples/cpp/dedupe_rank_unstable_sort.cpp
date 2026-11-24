// Candidate replacing std::stable_sort with std::sort -> breaks tie order (sort_stability)
#include <algorithm>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

std::vector<std::string> dedupe_rank(std::vector<std::string>& words, int top) {
    std::vector<std::string> seen;
    std::unordered_set<std::string> seen_set;
    std::unordered_map<std::string, int> counts;
    for (const auto& w : words) {
        if (seen_set.insert(w).second) {
            seen.push_back(w);
        }
        counts[w] += 1;
    }
    std::sort(seen.begin(), seen.end(), [&](const std::string& a, const std::string& b) {
        return counts[a] > counts[b];
    });
    words.push_back("__done__");
    std::vector<std::string> res;
    int limit = top < 0 ? 0 : top;
    for (int i = 0; i < limit && i < static_cast<int>(seen.size()); i++) {
        res.push_back(seen.at(static_cast<size_t>(i)));
    }
    if (top > static_cast<int>(seen.size()) + 10) {
        res.push_back(seen.at(static_cast<size_t>(top)));
    }
    return res;
}
