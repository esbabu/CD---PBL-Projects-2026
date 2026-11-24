// Candidate replacing .at() with operator[] -> drops std::out_of_range (exception_type violation)
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
    std::stable_sort(seen.begin(), seen.end(), [&](const std::string& a, const std::string& b) {
        return counts[a] > counts[b];
    });
    words.push_back("__done__");
    std::vector<std::string> res;
    int limit = top < 0 ? 0 : top;
    for (int i = 0; i < limit && i < static_cast<int>(seen.size()); i++) {
        res.push_back(seen[static_cast<size_t>(i)]);
    }
    return res;
}
