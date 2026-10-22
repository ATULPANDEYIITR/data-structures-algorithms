#include <algorithm>
#include <cassert>
#include <iostream>
#include <optional>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>

class SortedRepositoryIndex {
private:
    std::vector<int> versions;

    void validateSorted() const {
        if (!std::is_sorted(versions.begin(), versions.end())) {
            throw std::invalid_argument("Repository version index is not sorted.");
        }
    }

public:
    explicit SortedRepositoryIndex(std::vector<int> values)
        : versions(std::move(values)) {
        validateSorted();
    }

    // First position containing a value >= target.
    std::size_t lowerBound(int target) const {
        std::size_t left = 0;
        std::size_t right = versions.size();

        while (left < right) {
            const std::size_t mid = left + (right - left) / 2;

            if (versions[mid] < target) {
                left = mid + 1;
            } else {
                right = mid;
            }
        }

        return left;
    }

    // First position containing a value > target.
    std::size_t upperBound(int target) const {
        std::size_t left = 0;
        std::size_t right = versions.size();

        while (left < right) {
            const std::size_t mid = left + (right - left) / 2;

            if (versions[mid] <= target) {
                left = mid + 1;
            } else {
                right = mid;
            }
        }

        return left;
    }

    std::optional<std::size_t> exactSearch(int target) const {
        const std::size_t index = lowerBound(target);

        if (index < versions.size() && versions[index] == target) {
            return index;
        }

        return std::nullopt;
    }

    std::optional<std::size_t> firstOccurrence(int target) const {
        return exactSearch(target);
    }

    std::optional<std::size_t> lastOccurrence(int target) const {
        const std::size_t upper = upperBound(target);

        if (upper == 0 || versions[upper - 1] != target) {
            return std::nullopt;
        }

        return upper - 1;
    }

    std::size_t insertionPosition(int target) const {
        return lowerBound(target);
    }

    std::size_t duplicateCount(int target) const {
        return upperBound(target) - lowerBound(target);
    }

    std::pair<std::optional<std::size_t>, std::optional<std::size_t>>
    occurrenceRange(int target) const {
        const auto first = firstOccurrence(target);
        const auto last = lastOccurrence(target);
        return {first, last};
    }

    void printAnalysis(int target) const {
        const auto exact = exactSearch(target);
        const auto first = firstOccurrence(target);
        const auto last = lastOccurrence(target);
        const auto [rangeFirst, rangeLast] = occurrenceRange(target);

        std::cout << "Target " << target << '\n';
        std::cout << "  exact search:       "
                  << (exact ? std::to_string(*exact) : "absent") << '\n';
        std::cout << "  first occurrence:   "
                  << (first ? std::to_string(*first) : "absent") << '\n';
        std::cout << "  last occurrence:    "
                  << (last ? std::to_string(*last) : "absent") << '\n';
        std::cout << "  lower bound:        " << lowerBound(target) << '\n';
        std::cout << "  upper bound:        " << upperBound(target) << '\n';
        std::cout << "  insertion position: "
                  << insertionPosition(target) << '\n';
        std::cout << "  duplicate count:    "
                  << duplicateCount(target) << '\n';

        if (rangeFirst && rangeLast) {
            std::cout << "  duplicate range:    ["
                      << *rangeFirst << ", " << *rangeLast << "]\n";
        } else {
            std::cout << "  duplicate range:    absent\n";
        }

        std::cout << '\n';
    }
};

static void runTests() {
    {
        SortedRepositoryIndex index({});

        assert(index.lowerBound(5) == 0);
        assert(index.upperBound(5) == 0);
        assert(index.duplicateCount(5) == 0);
        assert(!index.exactSearch(5));
    }

    {
        SortedRepositoryIndex index({1, 1, 1, 2, 4, 4, 7});

        assert(index.firstOccurrence(1) == std::optional<std::size_t>(0));
        assert(index.lastOccurrence(1) == std::optional<std::size_t>(2));

        assert(index.firstOccurrence(4) == std::optional<std::size_t>(4));
        assert(index.lastOccurrence(4) == std::optional<std::size_t>(5));

        assert(index.lowerBound(3) == 4);
        assert(index.upperBound(4) == 6);
        assert(index.insertionPosition(6) == 6);
        assert(index.duplicateCount(4) == 2);
        assert(index.duplicateCount(3) == 0);
    }

    {
        SortedRepositoryIndex index({-10, -5, 0, 0, 0, 9});

        assert(index.lowerBound(-11) == 0);
        assert(index.lowerBound(0) == 2);
        assert(index.upperBound(0) == 5);
        assert(index.lastOccurrence(0) == std::optional<std::size_t>(4));
        assert(index.insertionPosition(10) == 6);
    }

    bool rejected = false;

    try {
        SortedRepositoryIndex invalid({3, 2, 4});
    } catch (const std::invalid_argument&) {
        rejected = true;
    }

    assert(rejected);
    std::cout << "All C++17 verification tests passed.\n";
}

int main() {
    try {
        SortedRepositoryIndex repositoryVersions{
            101, 102, 102, 102, 105, 107, 107, 110, 115, 115
        };

        std::cout << "Repository version index analysis\n\n";

        for (const int target : {100, 102, 104, 107, 115, 120}) {
            repositoryVersions.printAnalysis(target);
        }

        runTests();
    } catch (const std::exception& error) {
        std::cerr << "Failure: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
