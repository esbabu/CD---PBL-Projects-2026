#include <vector>

template <typename T>
T sum_vec(const std::vector<T>& vals) {
    T acc = T();
    for (const auto& v : vals) {
        acc += v;
    }
    return acc;
}
