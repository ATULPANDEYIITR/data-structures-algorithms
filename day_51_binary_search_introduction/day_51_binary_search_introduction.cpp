#include <algorithm>
#include <cassert>
#include <exception>
#include <iomanip>
#include <iostream>
#include <optional>
#include <stdexcept>
#include <string>
#include <vector>

class BinarySearchError : public std::invalid_argument {
public:
    explicit BinarySearchError(const std::string& message)
        : std::invalid_argument(message) {}
};

class SortedIndex {
private:
    std::vector<int> values_;

    static void validateSorted(const std::vector<int>& values) {
        if (!std::is_sorted(values.begin(), values.end())) {
            throw BinarySearchError(
                "Binary search requires non-decreasing sorted data."
            );
        }
    }

    std::optional<std::size_t> recursiveImpl(
        int target,
        std::size_t left,
        std::size_t right
    ) const {
        if (left > right) {
            return std::nullopt;
        }

        // Subtraction before division avoids a potentially unsafe left + right
        // midpoint calculation for large index ranges.
        const std::size_t middle = left + (right - left) / 2;

        if (values_[middle] == target) {
            return middle;
        }

        if (values_[middle] < target) {
            return recursiveImpl(target, middle + 1, right);
        }

        if (middle == 0) {
            return std::nullopt;
        }

        return recursiveImpl(target, left, middle - 1);
    }

public:
    explicit SortedIndex(std::vector<int> values)
        : values_(std::move(values)) {
        validateSorted(values_);
    }

    std::optional<std::size_t> iterative(int target) const {
        std::size_t left = 0;
        std::size_t right = values_.empty() ? 0 : values_.size() - 1;

        if (values_.empty()) {
            return std::nullopt;
        }

        while (left <= right) {
            const std::size_t middle = left + (right - left) / 2;

            if (values_[middle] == target) {
                return middle;
            }

            if (values_[middle] < target) {
                left = middle + 1;
            } else {
                if (middle == 0) {
                    return std::nullopt;
                }
                right = middle - 1;
            }
        }

        return std::nullopt;
    }

    std::optional<std::size_t> recursive(int target) const {
        if (values_.empty()) {
            return std::nullopt;
        }

        return recursiveImpl(target, 0, values_.size() - 1);
    }

    std::size_t lowerBound(int target) const {
        std::size_t left = 0;
        std::size_t right = values_.size();

        while (left < right) {
            const std::size_t middle = left + (right - left) / 2;

            if (values_[middle] < target) {
                left = middle + 1;
            } else {
                right = middle;
            }
        }

        return left;
    }

    std::size_t upperBound(int target) const {
        std::size_t left = 0;
        std::size_t right = values_.size();

        while (left < right) {
            const std::size_t middle = left + (right - left) / 2;

            if (values_[middle] <= target) {
                left = middle + 1;
            } else {
                right = middle;
            }
        }

        return left;
    }

    const std::vector<int>& values() const {
        return values_;
    }
};

void printResult(
    const SortedIndex& index,
    int target
) {
    const auto iterative = index.iterative(target);
    const auto recursive = index.recursive(target);
    const std::size_t first = index.lowerBound(target);
    const std::size_t after = index.upperBound(target);

    std::cout << "target=" << std::setw(3) << target
              << " iterative=";

    if (iterative.has_value()) {
        std::cout << *iterative;
    } else {
        std::cout << "not-found";
    }

    std::cout << " recursive=";

    if (recursive.has_value()) {
        std::cout << *recursive;
    } else {
        std::cout << "not-found";
    }

    if (first < index.values().size() &&
        index.values()[first] == target) {
        std::cout << " range=[" << first << ", " << after - 1 << "]";
    } else {
        std::cout << " insertion-position=" << first;
    }

    std::cout << '\n';
}

int main() {
    try {
        SortedIndex index({
            -20, -10, -1, 0, 4, 4, 4, 9, 15, 21, 42
        });

        std::cout << "Repository artifact lookup index\n";
        std::cout << "Sorted keys: ";

        for (const int value : index.values()) {
            std::cout << value << ' ';
        }
        std::cout << "\n\n";

        for (const int target : {-20, 4, 5, 42, 100}) {
            printResult(index, target);
        }

        SortedIndex empty({});
        assert(!empty.iterative(10).has_value());

        try {
            SortedIndex invalid({1, 8, 3, 9});
        } catch (const BinarySearchError& error) {
            std::cout << "\nValidation failure handled: "
                      << error.what() << '\n';
        }

        std::cout << "\nComplexity: O(log n) search time, O(1) auxiliary "
                     "space for iterative search and O(log n) call-stack "
                     "space for recursive search.\n";
    } catch (const std::exception& error) {
        std::cerr << "Fatal error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
