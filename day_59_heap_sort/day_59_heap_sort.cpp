#include <algorithm>
#include <chrono>
#include <cstddef>
#include <exception>
#include <iomanip>
#include <iostream>
#include <limits>
#include <random>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

enum class HeapType {
    Max,
    Min
};

struct SortMetrics {
    std::size_t comparisons{};
    std::size_t swaps{};
    long long elapsedNanoseconds{};
};

class HeapSortEngine {
public:
    explicit HeapSortEngine(HeapType type = HeapType::Max)
        : type_(type) {}

    SortMetrics sort(std::vector<long long>& values) {
        comparisons_ = 0;
        swaps_ = 0;

        const auto start = std::chrono::steady_clock::now();

        if (values.size() < 2) {
            return metrics(start);
        }

        // Bottom-up construction uses O(n) heap-building time.
        for (std::size_t i = values.size() / 2; i-- > 0;) {
            siftDown(values, i, values.size());
        }

        // The root is repeatedly exchanged with the final active element.
        for (std::size_t end = values.size(); end-- > 1;) {
            exchange(values, 0, end);
            siftDown(values, 0, end);
        }

        if (type_ == HeapType::Min) {
            std::reverse(values.begin(), values.end());
        }

        return metrics(start);
    }

private:
    HeapType type_;
    std::size_t comparisons_{};
    std::size_t swaps_{};

    bool preferred(long long left, long long right) {
        ++comparisons_;
        return type_ == HeapType::Max ? left > right : left < right;
    }

    void exchange(std::vector<long long>& values,
                  std::size_t first,
                  std::size_t second) {
        std::swap(values[first], values[second]);
        ++swaps_;
    }

    void siftDown(std::vector<long long>& values,
                  std::size_t root,
                  std::size_t size) {
        while (true) {
            const std::size_t left = root * 2 + 1;
            const std::size_t right = left + 1;
            std::size_t selected = root;

            if (left < size && preferred(values[left], values[selected])) {
                selected = left;
            }

            if (right < size && preferred(values[right], values[selected])) {
                selected = right;
            }

            if (selected == root) {
                return;
            }

            exchange(values, root, selected);
            root = selected;
        }
    }

    SortMetrics metrics(
        const std::chrono::steady_clock::time_point& start) const {
        const auto elapsed =
            std::chrono::duration_cast<std::chrono::nanoseconds>(
                std::chrono::steady_clock::now() - start);

        return {comparisons_, swaps_, elapsed.count()};
    }
};

class MergeSorter {
public:
    static std::vector<long long> sort(const std::vector<long long>& values) {
        if (values.size() <= 1) {
            return values;
        }

        std::vector<long long> buffer(values.size());
        std::vector<long long> result = values;
        mergeSort(result, buffer, 0, result.size());
        return result;
    }

private:
    static void mergeSort(std::vector<long long>& values,
                          std::vector<long long>& buffer,
                          std::size_t begin,
                          std::size_t end) {
        if (end - begin <= 1) {
            return;
        }

        const std::size_t middle = begin + (end - begin) / 2;
        mergeSort(values, buffer, begin, middle);
        mergeSort(values, buffer, middle, end);

        std::size_t left = begin;
        std::size_t right = middle;
        std::size_t output = begin;

        while (left < middle && right < end) {
            if (values[left] <= values[right]) {
                buffer[output++] = values[left++];
            } else {
                buffer[output++] = values[right++];
            }
        }

        while (left < middle) {
            buffer[output++] = values[left++];
        }

        while (right < end) {
            buffer[output++] = values[right++];
        }

        for (std::size_t i = begin; i < end; ++i) {
            values[i] = buffer[i];
        }
    }
};

class QuickSorter {
public:
    static void sort(std::vector<long long>& values) {
        if (!values.empty()) {
            quickSort(values, 0, values.size() - 1);
        }
    }

private:
    static void quickSort(std::vector<long long>& values,
                          std::size_t low,
                          std::size_t high) {
        std::size_t i = low;
        std::size_t j = high;
        const long long pivot = values[low + (high - low) / 2];

        while (i <= j) {
            while (values[i] < pivot) {
                ++i;
            }

            while (values[j] > pivot) {
                if (j == 0) {
                    break;
                }
                --j;
            }

            if (i <= j) {
                std::swap(values[i], values[j]);
                ++i;

                if (j == 0) {
                    break;
                }
                --j;
            }
        }

        if (low < j) {
            quickSort(values, low, j);
        }

        if (i < high) {
            quickSort(values, i, high);
        }
    }
};

static void require(bool condition, const std::string& message) {
    if (!condition) {
        throw std::runtime_error(message);
    }
}

static void runTests() {
    const std::vector<std::vector<long long>> cases{
        {},
        {1},
        {2, 1},
        {5, 5, 5, 5},
        {-7, 4, 0, -2, 9, 4},
        {std::numeric_limits<long long>::min(),
         0,
         std::numeric_limits<long long>::max(),
         -1}
    };

    for (const auto& input : cases) {
        auto expected = input;
        std::sort(expected.begin(), expected.end());

        auto heapResult = input;
        HeapSortEngine().sort(heapResult);
        require(heapResult == expected, "Heap-sort test failed.");

        auto minHeapResult = input;
        HeapSortEngine(HeapType::Min).sort(minHeapResult);
        require(minHeapResult == expected, "Min-heap test failed.");

        require(MergeSorter::sort(input) == expected,
                "Merge-sort comparison failed.");

        auto quickResult = input;
        QuickSorter::sort(quickResult);
        require(quickResult == expected,
                "Quick-sort comparison failed.");
    }

    std::mt19937_64 generator(20261029);
    std::uniform_int_distribution<long long> distribution(-100000, 100000);

    for (int trial = 0; trial < 100; ++trial) {
        std::vector<long long> input;
        const std::size_t size = generator() % 300;

        for (std::size_t i = 0; i < size; ++i) {
            input.push_back(distribution(generator));
        }

        auto expected = input;
        std::sort(expected.begin(), expected.end());

        HeapSortEngine().sort(input);
        require(input == expected, "Randomized test failed.");
    }

    std::cout << "All C++17 heap-sort tests passed.\n";
}

static void printVector(const std::vector<long long>& values) {
    std::cout << "[";
    for (std::size_t i = 0; i < values.size(); ++i) {
        if (i != 0) {
            std::cout << ", ";
        }
        std::cout << values[i];
    }
    std::cout << "]";
}

int main() {
    try {
        runTests();

        std::vector<long long> data{
            12, 7, 3, 19, 4, 7, -2, 15, 0, 9
        };

        HeapSortEngine engine;
        const SortMetrics metrics = engine.sort(data);

        std::cout << "\nHeap Sort result: ";
        printVector(data);
        std::cout << "\nComparisons: " << metrics.comparisons
                  << "\nSwaps: " << metrics.swaps
                  << "\nElapsed: " << metrics.elapsedNanoseconds
                  << " ns\n";

        std::vector<long long> mergeData{
            12, 7, 3, 19, 4, 7, -2, 15, 0, 9
        };

        const auto mergeResult = MergeSorter::sort(mergeData);

        std::cout << "\nMerge Sort result: ";
        printVector(mergeResult);
        std::cout << "\n";

        std::vector<long long> quickData{
            12, 7, 3, 19, 4, 7, -2, 15, 0, 9
        };

        QuickSorter::sort(quickData);

        std::cout << "Quick Sort result: ";
        printVector(quickData);
        std::cout << "\n";

        /*
         * Heap sort is useful when deterministic O(n log n) worst-case time
         * and O(1) auxiliary storage are more important than stability.
         * It is not stable: equal values can change relative order.
         */
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Failure: " << error.what() << '\n';
        return 1;
    }
}
