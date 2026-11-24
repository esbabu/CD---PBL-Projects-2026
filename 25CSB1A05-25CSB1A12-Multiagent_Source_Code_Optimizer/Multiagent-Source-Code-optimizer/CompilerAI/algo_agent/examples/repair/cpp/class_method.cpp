#include <vector>

class Solution {
public:
    int countMatches(const std::vector<int>& nums, int target) {
        int c = 0;
        for (size_t i = 0; i < nums.size(); ++i) {
            if (nums[i] == target) c++;
        }
        return c;
    }
};
