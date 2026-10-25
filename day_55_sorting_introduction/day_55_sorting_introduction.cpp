#include <algorithm>
#include <cassert>
#include <cstddef>
#include <iostream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

struct SortMetrics {
    std::string algorithm;
    std::size_t comparisons = 0;
    std::size_t writes = 0;
};

struct Record {
    std::string name;
    int score;
    int registration_order;
};

bool score_less(const Record& a, const Record& b) {
    return a.score < b.score;
}

template <typename T, typename Compare>
SortMetrics insertion_sort(std::vector<T>& values, Compare less) {
    SortMetrics metrics{"Insertion sort"};

    for (std::size_t i = 1; i < values.size(); ++i) {
        T current = values[i];
        std::size_t j = i;

        // Shift only strictly greater elements; equal keys retain their order.
        while (j > 0) {
            ++metrics.comparisons;
            if (!less(current, values[j - 1])) {
                break;
            }
            values[j] = values[j - 1];
            ++metrics.writes;
            --j;
        }

        values[j] = std::move(current);
        ++metrics.writes;
    }

    return metrics;
}

template <typename T, typename Compare>
SortMetrics merge_sort(std::vector<T>& values, Compare less) {
    SortMetrics metrics{"Merge sort"};
    std::vector<T> buffer(values.size());

    auto sort = [&](auto&& self, std::size_t low, std::size_t high) -> void {
        if (high - low < 2) {
            return;
        }

        const std::size_t middle = low + (high - low) / 2;
        self(self, low, middle);
        self(self, middle, high);

        std::size_t i = low;
        std::size_t j = middle;
        std::size_t out = low;

        while (i < middle && j < high) {
            ++metrics.comparisons;

            // Taking the left item when neither is less preserves stability.
            if (!less(values[j], values[i])) {
                buffer[out++] = values[i++];
            } else {
                buffer[out++] = values[j++];
            }
            ++metrics.writes;
        }

        while (i < middle) {
            buffer[out++] = values[i++];
            ++metrics.writes;
        }
        while (j < high) {
            buffer[out++] = values[j++];
            ++metrics.writes;
        }

        for (std::size_t k = low; k < high; ++k) {
            values[k] = std::move(buffer[k]);
            ++metrics.writes;
        }
    };

    sort(sort, 0, values.size());
    return metrics;
}

template <typename T, typename Compare>
SortMetrics quick_sort(std::vector<T>& values, Compare less) {
    SortMetrics metrics{"Three-way quicksort"};

    auto equivalent = [&](const T& a, const T& b) {
        return !less(a, b) && !less(b, a);
    };

    auto sort = [&](auto&& self, std::ptrdiff_t low,
                    std::ptrdiff_t high) -> void {
        while (low < high) {
            const T pivot = values[static_cast<std::size_t>(
                low + (high - low) / 2)];

            std::ptrdiff_t lt = low;
            std::ptrdiff_t current = low;
            std::ptrdiff_t gt = high;

            while (current <= gt) {
                const T& item = values[static_cast<std::size_t>(current)];
                ++metrics.comparisons;

                if (less(item, pivot)) {
                    std::swap(values[static_cast<std::size_t>(lt)],
                              values[static_cast<std::size_t>(current)]);
                    metrics.writes += 2;
                    ++lt;
                    ++current;
                } else {
                    ++metrics.comparisons;
                    if (less(pivot, item)) {
                        std::swap(values[static_cast<std::size_t>(current)],
                                  values[static_cast<std::size_t>(gt)]);
                        metrics.writes += 2;
                        --gt;
                    } else {
                        assert(equivalent(item, pivot));
                        ++current;
                    }
                }
            }

            // Bound recursion depth by recursing into the smaller partition.
            if (lt - low < high - gt) {
                self(self, low, lt - 1);
                low = gt + 1;
            } else {
                self(self, gt + 1, high);
                high = lt - 1;
            }
        }
    };

    sort(sort, 0, static_cast<std::ptrdiff_t>(values.size()) - 1);
    return metrics;
}

template <typename T, typename Compare>
bool is_sorted_by(const std::vector<T>& values, Compare less) {
    for (std::size_t i = 1; i < values.size(); ++i) {
        if (less(values[i], values[i - 1])) {
            return false;
        }
    }
    return true;
}

template <typename T>
void print_values(const std::vector<T>& values) {
    for (const auto& value : values) {
        std::cout << value << ' ';
    }
    std::cout << '\n';
}

std::ostream& operator<<(std::ostream& out, const Record& record) {
    return out << record.name << "(score=" << record.score
               << ",order=" << record.registration_order << ')';
}

template <typename T>
void print_metrics(const SortMetrics& metrics) {
    std::cout << metrics.algorithm
              << ": comparisons=" << metrics.comparisons
              << ", writes=" << metrics.writes << '\n';
}

int main() {
    const std::vector<std::vector<int>> samples{
        {},
        {1},
        {5, 2, 4, 1, 3},
        {4, 4, 4, 4},
        {9, -2, 0, 7, -2}
    };

    for (const auto& sample : samples) {
        auto insertion = sample;
        auto merged = sample;
        auto quick = sample;

        const auto insertion_metrics =
            insertion_sort(insertion, std::less<int>{});
        const auto merge_metrics = merge_sort(merged, std::less<int>{});
        const auto quick_metrics = quick_sort(quick, std::less<int>{});

        assert(std::is_sorted(insertion.begin(), insertion.end()));
        assert(std::is_sorted(merged.begin(), merged.end()));
        assert(std::is_sorted(quick.begin(), quick.end()));
        assert(insertion == merged && merged == quick);

        std::cout << "Input: ";
        print_values(sample);
        std::cout << "Sorted: ";
        print_values(merged);
        print_metrics<int>(insertion_metrics);
        print_metrics<int>(merge_metrics);
        print_metrics<int>(quick_metrics);
        std::cout << '\n';
    }

    // A record-oriented workload makes stability observable.
    const std::vector<Record> records{
        {"Asha", 90, 1},
        {"Ravi", 75, 2},
        {"Meera", 90, 3},
        {"Kabir", 75, 4},
        {"Isha", 90, 5}
    };

    auto stable_records = records;
    auto quick_records = records;

    insertion_sort(stable_records, score_less);
    quick_sort(quick_records, score_less);

    assert(is_sorted_by(stable_records, score_less));
    assert(is_sorted_by(quick_records, score_less));

    // Stable insertion sort retains registration order for equal scores.
    assert(stable_records[0].name == "Ravi");
    assert(stable_records[1].name == "Kabir");
    assert(stable_records[2].name == "Asha");
    assert(stable_records[3].name == "Meera");
    assert(stable_records[4].name == "Isha");

    std::cout << "Stable score ordering:\n";
    for (const auto& record : stable_records) {
        std::cout << record << '\n';
    }

    std::cout << "\nQuicksort score ordering:\n";
    for (const auto& record : quick_records) {
        std::cout << record << '\n';
    }

    std::vector<int> descending(1000);
    for (std::size_t i = 0; i < descending.size(); ++i) {
        descending[i] = static_cast<int>(descending.size() - i);
    }

    merge_sort(descending, std::less<int>{});
    assert(std::is_sorted(descending.begin(), descending.end()));

    std::cout << "\nAll sorting assertions passed.\n";
    return 0;
}
