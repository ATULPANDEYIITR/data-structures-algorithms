#include <algorithm>
#include <chrono>
#include <cstddef>
#include <iomanip>
#include <iostream>
#include <random>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

enum class Algorithm {
    Bubble,
    Selection,
    Insertion
};

struct SortStats {
    std::size_t comparisons = 0;
    std::size_t swaps = 0;
    std::size_t writes = 0;
    double milliseconds = 0.0;
};

struct SortResult {
    std::vector<int> values;
    SortStats stats;
};

class SortException : public std::runtime_error {
public:
    explicit SortException(const std::string& message)
        : std::runtime_error(message) {}
};

class SortingEngine {
public:
    static SortResult bubbleSort(const std::vector<int>& input) {
        auto data = input;
        SortStats stats;

        const auto start = std::chrono::steady_clock::now();

        // Early termination changes the best case from O(n²) to O(n).
        for (std::size_t end = data.size(); end > 1; --end) {
            bool changed = false;

            for (std::size_t i = 1; i < end; ++i) {
                ++stats.comparisons;

                if (data[i - 1] > data[i]) {
                    std::swap(data[i - 1], data[i]);
                    ++stats.swaps;
                    stats.writes += 2;
                    changed = true;
                }
            }

            if (!changed) {
                break;
            }
        }

        stats.milliseconds = elapsedMilliseconds(start);
        return {std::move(data), stats};
    }

    static SortResult selectionSort(const std::vector<int>& input) {
        auto data = input;
        SortStats stats;

        const auto start = std::chrono::steady_clock::now();

        for (std::size_t i = 0; i + 1 < data.size(); ++i) {
            std::size_t minimum = i;

            for (std::size_t j = i + 1; j < data.size(); ++j) {
                ++stats.comparisons;

                if (data[j] < data[minimum]) {
                    minimum = j;
                }
            }

            if (minimum != i) {
                std::swap(data[i], data[minimum]);
                ++stats.swaps;
                stats.writes += 2;
            }
        }

        stats.milliseconds = elapsedMilliseconds(start);
        return {std::move(data), stats};
    }

    static SortResult insertionSort(const std::vector<int>& input) {
        auto data = input;
        SortStats stats;

        const auto start = std::chrono::steady_clock::now();

        for (std::size_t i = 1; i < data.size(); ++i) {
            const int key = data[i];
            ++stats.writes;

            std::size_t j = i;

            while (j > 0) {
                ++stats.comparisons;

                if (data[j - 1] <= key) {
                    break;
                }

                data[j] = data[j - 1];
                ++stats.writes;
                --j;
            }

            data[j] = key;
            ++stats.writes;
        }

        stats.milliseconds = elapsedMilliseconds(start);
        return {std::move(data), stats};
    }

private:
    static double elapsedMilliseconds(
        const std::chrono::steady_clock::time_point& start
    ) {
        const auto finish = std::chrono::steady_clock::now();

        return std::chrono::duration<double, std::milli>(
            finish - start
        ).count();
    }
};

std::string algorithmName(Algorithm algorithm) {
    switch (algorithm) {
        case Algorithm::Bubble:
            return "Bubble Sort";
        case Algorithm::Selection:
            return "Selection Sort";
        case Algorithm::Insertion:
            return "Insertion Sort";
    }

    throw SortException("Unknown sorting algorithm.");
}

SortResult execute(
    Algorithm algorithm,
    const std::vector<int>& values
) {
    switch (algorithm) {
        case Algorithm::Bubble:
            return SortingEngine::bubbleSort(values);
        case Algorithm::Selection:
            return SortingEngine::selectionSort(values);
        case Algorithm::Insertion:
            return SortingEngine::insertionSort(values);
    }

    throw SortException("Unsupported algorithm.");
}

bool isSorted(const std::vector<int>& values) {
    return std::is_sorted(values.begin(), values.end());
}

bool isPermutation(
    const std::vector<int>& original,
    const std::vector<int>& result
) {
    if (original.size() != result.size()) {
        return false;
    }

    auto left = original;
    auto right = result;

    std::sort(left.begin(), left.end());
    std::sort(right.begin(), right.end());

    return left == right;
}

std::vector<int> randomData(std::size_t size, unsigned seed) {
    std::mt19937 generator(seed);
    std::uniform_int_distribution<int> distribution(
        0,
        static_cast<int>(size * 4)
    );

    std::vector<int> values;
    values.reserve(size);

    for (std::size_t i = 0; i < size; ++i) {
        values.push_back(distribution(generator));
    }

    return values;
}

std::unordered_map<std::string, std::vector<int>> makeDatasets(
    std::size_t size
) {
    std::vector<int> sorted(size);
    for (std::size_t i = 0; i < size; ++i) {
        sorted[i] = static_cast<int>(i);
    }

    auto reverse = sorted;
    std::reverse(reverse.begin(), reverse.end());

    auto duplicates = randomData(size, 99);
    for (auto& value : duplicates) {
        value %= 10;
    }

    auto nearlySorted = sorted;
    const std::size_t step = std::max<std::size_t>(1, size / 20);

    for (std::size_t i = 0; i + 1 < size; i += step) {
        std::swap(nearlySorted[i], nearlySorted[i + 1]);
    }

    return {
        {"random", randomData(size, 42)},
        {"sorted", std::move(sorted)},
        {"reverse", std::move(reverse)},
        {"duplicates", std::move(duplicates)},
        {"nearly sorted", std::move(nearlySorted)}
    };
}

void runCorrectnessTests() {
    const std::vector<std::vector<int>> cases = {
        {},
        {1},
        {2, 1},
        {1, 2, 3, 4},
        {4, 3, 2, 1},
        {3, 1, 3, 2, 1, 2},
        {-4, 7, 0, -1, 5}
    };

    const std::vector<Algorithm> algorithms = {
        Algorithm::Bubble,
        Algorithm::Selection,
        Algorithm::Insertion
    };

    for (const auto algorithm : algorithms) {
        for (const auto& input : cases) {
            const auto result = execute(algorithm, input);

            if (!isSorted(result.values)) {
                throw SortException(
                    algorithmName(algorithm) + " produced unsorted output."
                );
            }

            if (!isPermutation(input, result.values)) {
                throw SortException(
                    algorithmName(algorithm) + " changed the input values."
                );
            }
        }
    }

    std::cout << "Correctness suite: PASS\n";
}

void printResult(
    const std::string& dataset,
    Algorithm algorithm,
    const SortResult& result
) {
    std::cout << std::left
              << std::setw(16) << dataset
              << std::setw(17) << algorithmName(algorithm)
              << std::right
              << std::setw(13) << result.stats.comparisons
              << std::setw(10) << result.stats.swaps
              << std::setw(10) << result.stats.writes
              << std::setw(12)
              << std::fixed
              << std::setprecision(3)
              << result.stats.milliseconds
              << '\n';
}

int main() {
    try {
        runCorrectnessTests();

        constexpr std::size_t dataSize = 300;
        const auto datasets = makeDatasets(dataSize);

        const std::vector<Algorithm> algorithms = {
            Algorithm::Bubble,
            Algorithm::Selection,
            Algorithm::Insertion
        };

        std::cout << "\n"
                  << std::left
                  << std::setw(16) << "Dataset"
                  << std::setw(17) << "Algorithm"
                  << std::right
                  << std::setw(13) << "Comparisons"
                  << std::setw(10) << "Swaps"
                  << std::setw(10) << "Writes"
                  << std::setw(12) << "Time ms"
                  << '\n';

        std::cout << std::string(78, '-') << '\n';

        for (const auto& [dataset, values] : datasets) {
            for (const auto algorithm : algorithms) {
                const auto result = execute(algorithm, values);
                printResult(dataset, algorithm, result);
            }
        }

        const std::vector<int> example = {5, 2, 4, 1, 3};

        std::cout << "\nExample input: ";
        for (const int value : example) {
            std::cout << value << ' ';
        }
        std::cout << '\n';

        for (const auto algorithm : algorithms) {
            const auto result = execute(algorithm, example);

            std::cout << algorithmName(algorithm) << ": ";
            for (const int value : result.values) {
                std::cout << value << ' ';
            }
            std::cout << '\n';
        }

        std::cout << "\nComplexity characteristics:\n"
                  << "Bubble Sort: best O(n), average/worst O(n^2), O(1) space.\n"
                  << "Selection Sort: O(n^2) in all input orders, O(1) space.\n"
                  << "Insertion Sort: best O(n), average/worst O(n^2), O(1) space.\n"
                  << "Bubble and Insertion Sort preserve equal-element order here.\n"
                  << "Selection Sort does not guarantee stability.\n";

        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Execution failure: " << error.what() << '\n';
        return 1;
    }
}
