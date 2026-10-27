#include <algorithm>
#include <cassert>
#include <chrono>
#include <exception>
#include <functional>
#include <iomanip>
#include <iostream>
#include <random>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

enum class SortOrder {
    Ascending,
    Descending
};

struct SortMetrics {
    std::size_t comparisons{0};
    std::size_t merges{0};
    double elapsedMilliseconds{0.0};
};

class MergeSortError : public std::runtime_error {
public:
    explicit MergeSortError(const std::string& message)
        : std::runtime_error(message) {}
};

class RepositoryChange {
public:
    int id;
    std::string component;
    int priority;

    RepositoryChange(int id, std::string component, int priority)
        : id(id), component(std::move(component)), priority(priority) {}
};

class MergeSortEngine {
private:
    SortMetrics metrics_;

    template <typename T, typename Compare>
    void merge(
        std::vector<T>& data,
        std::vector<T>& buffer,
        std::size_t left,
        std::size_t middle,
        std::size_t right,
        Compare compare
    ) {
        ++metrics_.merges;

        std::size_t i = left;
        std::size_t j = middle + 1;
        std::size_t k = left;

        while (i <= middle && j <= right) {
            ++metrics_.comparisons;

            // If elements compare equivalent, choose the left element.
            // This is the key property that makes the algorithm stable.
            if (!compare(data[j], data[i])) {
                buffer[k++] = std::move(data[i++]);
            } else {
                buffer[k++] = std::move(data[j++]);
            }
        }

        while (i <= middle) {
            buffer[k++] = std::move(data[i++]);
        }

        while (j <= right) {
            buffer[k++] = std::move(data[j++]);
        }

        for (std::size_t index = left; index <= right; ++index) {
            data[index] = std::move(buffer[index]);
        }
    }

    template <typename T, typename Compare>
    void sortRange(
        std::vector<T>& data,
        std::vector<T>& buffer,
        std::size_t left,
        std::size_t right,
        Compare compare
    ) {
        if (left >= right) {
            return;
        }

        const std::size_t middle = left + (right - left) / 2;

        sortRange(data, buffer, left, middle, compare);
        sortRange(data, buffer, middle + 1, right, compare);

        // Avoid an unnecessary merge when the two ranges are already ordered.
        ++metrics_.comparisons;
        if (!compare(data[middle + 1], data[middle])) {
            return;
        }

        merge(data, buffer, left, middle, right, compare);
    }

public:
    template <typename T, typename Compare = std::less<T>>
    SortMetrics sort(std::vector<T>& data, Compare compare = Compare{}) {
        metrics_ = {};

        if (data.size() < 2) {
            return metrics_;
        }

        std::vector<T> buffer(data.size());

        const auto start = std::chrono::steady_clock::now();

        sortRange(data, buffer, 0, data.size() - 1, compare);

        const auto end = std::chrono::steady_clock::now();

        metrics_.elapsedMilliseconds =
            std::chrono::duration<double, std::milli>(end - start).count();

        return metrics_;
    }
};

void printVector(const std::vector<int>& values) {
    std::cout << "[";
    for (std::size_t i = 0; i < values.size(); ++i) {
        if (i > 0) {
            std::cout << ", ";
        }
        std::cout << values[i];
    }
    std::cout << "]\n";
}

void validateSorted(const std::vector<int>& values) {
    if (!std::is_sorted(values.begin(), values.end())) {
        throw MergeSortError("Sort validation failed.");
    }
}

void demonstrateIntegerSorting() {
    std::vector<int> values{
        42, -7, 19, 0, 42, 5, -100, 8, 13, 2
    };

    MergeSortEngine engine;
    SortMetrics metrics = engine.sort(values);

    validateSorted(values);

    std::cout << "Sorted integers: ";
    printVector(values);

    std::cout << "Comparisons: " << metrics.comparisons << "\n";
    std::cout << "Merges: " << metrics.merges << "\n";
    std::cout << "Time: "
              << std::fixed << std::setprecision(4)
              << metrics.elapsedMilliseconds << " ms\n\n";
}

void demonstrateStableDomainSorting() {
    std::vector<RepositoryChange> changes{
        {101, "authentication", 2},
        {102, "database", 1},
        {103, "logging", 2},
        {104, "frontend", 1},
        {105, "deployment", 2}
    };

    MergeSortEngine engine;

    auto metrics = engine.sort(
        changes,
        [](const RepositoryChange& left, const RepositoryChange& right) {
            return left.priority < right.priority;
        }
    );

    // Equal-priority records must retain their original relative ordering.
    assert(changes[0].id == 102);
    assert(changes[1].id == 104);
    assert(changes[2].id == 101);
    assert(changes[3].id == 103);
    assert(changes[4].id == 105);

    std::cout << "Stable priority ordering:\n";
    for (const auto& change : changes) {
        std::cout << "  #" << change.id
                  << " " << change.component
                  << " priority=" << change.priority << "\n";
    }

    std::cout << "Comparisons: " << metrics.comparisons << "\n";
    std::cout << "Merges: " << metrics.merges << "\n\n";
}

void demonstrateEdgeCases() {
    MergeSortEngine engine;

    std::vector<int> empty;
    engine.sort(empty);
    assert(empty.empty());

    std::vector<int> singleton{7};
    engine.sort(singleton);
    assert(singleton == std::vector<int>{7});

    std::vector<int> duplicates{5, 5, 5, 5};
    engine.sort(duplicates);
    assert(duplicates == std::vector<int>{5, 5, 5, 5});

    std::vector<int> descending{5, 4, 3, 2, 1};

    engine.sort(
        descending,
        [](int left, int right) {
            return left > right;
        }
    );

    assert(descending == std::vector<int>{5, 4, 3, 2, 1});

    std::cout << "Edge cases: PASSED\n\n";
}

void performanceTest() {
    constexpr std::size_t size = 100000;

    std::mt19937 generator(42);
    std::uniform_int_distribution<int> distribution(-1'000'000, 1'000'000);

    std::vector<int> values(size);

    for (auto& value : values) {
        value = distribution(generator);
    }

    MergeSortEngine engine;
    const auto metrics = engine.sort(values);

    validateSorted(values);

    std::cout << "Performance test:\n";
    std::cout << "  elements: " << size << "\n";
    std::cout << "  comparisons: " << metrics.comparisons << "\n";
    std::cout << "  merges: " << metrics.merges << "\n";
    std::cout << "  elapsed: "
              << metrics.elapsedMilliseconds << " ms\n";
}

int main() {
    try {
        demonstrateIntegerSorting();
        demonstrateStableDomainSorting();
        demonstrateEdgeCases();
        performanceTest();

        std::cout << "\nAll merge-sort demonstrations passed.\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Failure: " << error.what() << "\n";
        return 1;
    }
}
