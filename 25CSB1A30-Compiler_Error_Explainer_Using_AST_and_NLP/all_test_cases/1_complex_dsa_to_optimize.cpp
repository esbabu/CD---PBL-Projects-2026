#include <iostream>
#include <vector>
#include <string>
#include <unordered_set>

using namespace std;

// Subset sum solved with DP to avoid exponential recursion
bool subsetSumDP(const vector<int>& nums, int target) {
    vector<bool> dp(target + 1, false); // O(T) space
    dp[0] = true;
    for (int num : nums) {
        for (int t = target; t >= num; --t) {
            if (dp[t - num]) dp[t] = true; // Why: propagate reachable sums
        }
    }
    return dp[target]; // O(n·T) time
}

// Detect duplicates in linear time using unordered_set
void findDuplicateKeywords(const vector<string>& keywords) {
    cout << "Scanning for duplicate keywords...\n";
    unordered_set<string> seen;
    for (const auto& kw : keywords) {
        if (!seen.insert(kw).second) { // insert returns pair<iterator,bool>
            cout << "Duplicate keyword found: " << kw << '\n'; // Why: output duplicate
        }
    }
}

int main() {
    cout << "=== COMPLEX DSA OPTIMIZATION DEMO ===\n";
    vector<string> wordList = {
        "compiler", "optimizer", "ast", "nlp", "compiler",
        "security", "tokens", "parser", "ast", "execution"
    };
    findDuplicateKeywords(wordList);

    vector<int> numbers = {3, 34, 4, 12, 5, 2};
    int target = 9;
    cout << "Searching subset sum target " << target << "...\n";
    if (subsetSumDP(numbers, target)) {
        cout << "Found subset with target sum " << target << "\n";
    } else {
        cout << "No subset sum found.\n";
    }
    cout << "Completed successfully!\n";
    return 0;
}
