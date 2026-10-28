#include <algorithm>
#include <cstdint>
#include <exception>
#include <iostream>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

enum class PivotStrategy {
    First,
    Last,
    Middle,
    MedianOfThree,
    Random
};

enum class PartitionStrategy {
    Lomuto,
    Hoare
};

struct SortStats {
    std::uint64_t comparisons = 0;
    std::uint64_t swaps = 0;
    std::uint64_t partitions = 0;
    std::size_t max_stack_depth = 0;
};

class QuickSortEngine {
public:
    QuickSortEngine(
        PivotStrategy pivot,
        PartitionStrategy partition,
        std::uint32_t seed = 42
    )
        : pivot_strategy_(pivot),
          partition_strategy_(partition),
          generator_(seed) {}

    SortStats sort(std::vector<int>& values) {
        SortStats stats;

        if (values.size() < 2) {
            return stats;
        }

        struct Range {
            std::size_t low;
            std::size_t high;
        };

        // Explicit ranges avoid uncontrolled call-stack growth on adversarial
        // input. The smaller range is processed first.
        std::vector<Range> stack;
        stack.push_back({0, values.size() - 1});

        while (!stack.empty()) {
            stats.max_stack_depth =
                std::max(stats.max_stack_depth, stack.size());

            Range current = stack.back();
            stack.pop_back();

            if (current.low >= current.high) {
                continue;
            }

            ++stats.partitions;

            if (partition_strategy_ == PartitionStrategy::Lomuto) {
                const std::size_t pivot_index =
                    choosePivot(values, current.low, current.high, stats);

                const std::size_t split =
                    lomuto(values, current.low, current.high,
                           pivot_index, stats);

                Range left{
                    current.low,
                    split == 0 ? 0 : split - 1
                };
                Range right{split + 1, current.high};

                const std::size_t left_size =
                    split > current.low ? split - current.low : 0;
                const std::size_t right_size =
                    current.high > split ? current.high - split : 0;

                if (left_size < right_size) {
                    pushIfValid(stack, right);
                    pushIfValid(stack, left);
                } else {
                    pushIfValid(stack, left);
                    pushIfValid(stack, right);
                }
            } else {
                const std::size_t pivot_index =
                    choosePivot(values, current.low, current.high, stats);

                const int pivot = values[pivot_index];

                const std::size_t split =
                    hoare(values, current.low, current.high,
                          pivot, stats);

                Range left{current.low, split};
                Range right{split + 1, current.high};

                const std::size_t left_size =
                    split >= current.low ? split - current.low + 1 : 0;
                const std::size_t right_size =
                    current.high > split ? current.high - split : 0;

                if (left_size < right_size) {
                    pushIfValid(stack, right);
                    pushIfValid(stack, left);
                } else {
                    pushIfValid(stack, left);
                    pushIfValid(stack, right);
                }
            }
        }

        return stats;
    }

private:
    PivotStrategy pivot_strategy_;
    PartitionStrategy partition_strategy_;
    std::mt19937 generator_;

    static void pushIfValid(
        std::vector<struct Range>&,
        const struct Range&
    ) {}

    // Range is declared separately here because it is only needed for the
    // implementation stack.
    struct Range {
        std::size_t low;
        std::size_t high;
    };

    std::size_t choosePivot(
        const std::vector<int>& values,
        std::size_t low,
        std::size_t high,
        SortStats& stats
    ) {
        switch (pivot_strategy_) {
        case PivotStrategy::First:
            return low;

        case PivotStrategy::Last:
            return high;

        case PivotStrategy::Middle:
            return low + (high - low) / 2;

        case PivotStrategy::Random: {
            std::uniform_int_distribution<std::size_t> distribution(
                low, high
            );
            return distribution(generator_);
        }

        case PivotStrategy::MedianOfThree: {
            const std::size_t middle = low + (high - low) / 2;
            const int a = values[low];
            const int b = values[middle];
            const int c = values[high];

            stats.comparisons += 3;

            if ((a <= b && b <= c) || (c <= b && b <= a)) {
                return middle;
            }

            if ((b <= a && a <= c) || (c <= a && a <= b)) {
                return low;
            }

            return high;
        }
        }

        throw std::logic_error("Invalid pivot strategy");
    }

    static void swapValues(
        std::vector<int>& values,
        std::size_t i,
        std::size_t j,
        SortStats& stats
    ) {
        if (i != j) {
            std::swap(values[i], values[j]);
            ++stats.swaps;
        }
    }

    static std::size_t lomuto(
        std::vector<int>& values,
        std::size_t low,
        std::size_t high,
        std::size_t pivot_index,
        SortStats& stats
    ) {
        swapValues(values, pivot_index, high, stats);
        const int pivot = values[high];

        std::size_t store = low;

        for (std::size_t i = low; i < high; ++i) {
            ++stats.comparisons;

            if (values[i] <= pivot) {
                swapValues(values, i, store, stats);
                ++store;
            }
        }

        swapValues(values, store, high, stats);
        return store;
    }

    static std::size_t hoare(
        std::vector<int>& values,
        std::size_t low,
        std::size_t high,
        int pivot,
        SortStats& stats
    ) {
        std::int64_t i = static_cast<std::int64_t>(low) - 1;
        std::int64_t j = static_cast<std::int64_t>(high) + 1;

        while (true) {
            do {
                ++i;
                ++stats.comparisons;
            } while (values[static_cast<std::size_t>(i)] < pivot);

            do {
                --j;
                ++stats.comparisons;
            } while (values[static_cast<std::size_t>(j)] > pivot);

            if (i >= j) {
                return static_cast<std::size_t>(j);
            }

            swapValues(
                values,
                static_cast<std::size_t>(i),
                static_cast<std::size_t>(j),
                stats
            );
        }
    }
};

template <typename Sorter>
void runSort(
    const std::string& name,
    std::vector<int> values,
    Sorter& sorter
) {
    const SortStats stats = sorter.sort(values);

    if (!std::is_sorted(values.begin(), values.end())) {
        throw std::runtime_error(name + ": sorting invariant failed");
    }

    std::cout << name
              << " | size=" << values.size()
              << " | comparisons=" << stats.comparisons
              << " | swaps=" << stats.swaps
              << " | partitions=" << stats.partitions
              << " | max_stack_depth=" << stats.max_stack_depth
              << '\n';
}

int main() {
    try {
        QuickSortEngine engine(
            PivotStrategy::MedianOfThree,
            PartitionStrategy::Hoare,
            42
        );

        std::vector<std::vector<int>> examples{
            {},
            {5},
            {3, 1, 4, 1, 5, 9, 2, 6},
            {7, 7, 7, 7},
            {5, 4, 3, 2, 1},
            {-4, 9, 0, -7, 3, 3, 1}
        };

        for (std::size_t i = 0; i < examples.size(); ++i) {
            runSort("example-" + std::to_string(i + 1), examples[i], engine);
        }

        std::mt19937 generator(10);
        std::uniform_int_distribution<int> distribution(-100000, 100000);

        std::vector<int> random_values(10000);
        for (int& value : random_values) {
            value = distribution(generator);
        }

        runSort("random", random_values, engine);

        std::vector<int> sorted(10000);
        std::iota(sorted.begin(), sorted.end(), 0);
        runSort("sorted", sorted, engine);

        std::vector<int> reverse = sorted;
        std::reverse(reverse.begin(), reverse.end());
        runSort("reverse-sorted", reverse, engine);

        std::vector<int> duplicates(10000, 7);
        runSort("duplicates", duplicates, engine);

        std::cout << "\nPivot comparison on sorted input\n";

        const std::vector<std::pair<PivotStrategy, std::string>> strategies{
            {PivotStrategy::First, "first"},
            {PivotStrategy::Middle, "middle"},
            {PivotStrategy::MedianOfThree, "median-of-three"},
            {PivotStrategy::Random, "random"}
        };

        for (const auto& [strategy, name] : strategies) {
            QuickSortEngine test_engine(
                strategy,
                PartitionStrategy::Hoare,
                42
            );

            std::vector<int> input(10000);
            std::iota(input.begin(), input.end(), 0);

            runSort(name, std::move(input), test_engine);
        }

        // Lomuto is intentionally demonstrated separately because its
        // partition invariant differs from Hoare's two-pointer invariant.
        QuickSortEngine lomuto_engine(
            PivotStrategy::MedianOfThree,
            PartitionStrategy::Lomuto,
            42
        );

        std::vector<int> lomuto_case{10, 4, 8, 3, 7, 1, 9, 2, 6, 5};
        runSort("lomuto-case", lomuto_case, lomuto_engine);

    } catch (const std::exception& error) {
        std::cerr << "Quick Sort failure: "
                  << error.what() << '\n';
        return 1;
    }

    return 0;
}
