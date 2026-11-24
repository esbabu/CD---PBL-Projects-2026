#include <algorithm>
#include <string>
#include <unordered_map>
#include <vector>

std::vector<std::string> dedupe_rank(std::vector<std::string>& words, int top) {
    std::vector<std::string> seen;
    for (const auto& w : words) {
        if (std::find(seen.begin(), seen.end(), w) == seen.end()) {
            seen.push_back(w);
        }
    }
    std::unordered_map<std::string, int> counts;
    for (const auto& w : words) counts[w] += 1;
    std::stable_sort(seen.begin(), seen.end(), [&](const std::string& a, const std::string& b) {
        return counts[a] > counts[b];
    });
    words.push_back("__done__");
    std::vector<std::string> res;
    int limit = top < 0 ? 0 : top;
    for (int i = 0; i < limit && i < static_cast<int>(seen.size()); i++) {
        res.push_back(seen.at(static_cast<size_t>(i)));
    }
    return res;
}
