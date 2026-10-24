#include <algorithm>
#include <cassert>
#include <exception>
#include <iostream>
#include <optional>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

struct SearchResult {
    string algorithm;
    optional<size_t> index;
    optional<int> value;
    size_t comparisons;
};

class SearchError : public invalid_argument {
public:
    explicit SearchError(const string& message)
        : invalid_argument(message) {}
};

SearchResult binarySearch(const vector<int>& values, int target) {
    size_t left = 0;
    size_t right = values.empty() ? 0 : values.size() - 1;
    size_t comparisons = 0;

    if (values.empty()) {
        return {"binarySearch", nullopt, nullopt, 0};
    }

    while (left <= right) {
        size_t mid = left + (right - left) / 2;
        ++comparisons;

        if (values[mid] == target) {
            return {
                "binarySearch",
                mid,
                values[mid],
                comparisons
            };
        }

        if (values[mid] < target) {
            left = mid + 1;
        } else {
            if (mid == 0) {
                break;
            }
            right = mid - 1;
        }
    }

    return {"binarySearch", nullopt, nullopt, comparisons};
}

SearchResult rotatedSearch(
    const vector<int>& values,
    int target
) {
    if (values.empty()) {
        return {"rotatedSearch", nullopt, nullopt, 0};
    }

    size_t left = 0;
    size_t right = values.size() - 1;
    size_t comparisons = 0;

    while (left <= right) {
        size_t mid = left + (right - left) / 2;
        ++comparisons;

        if (values[mid] == target) {
            return {
                "rotatedSearch",
                mid,
                values[mid],
                comparisons
            };
        }

        if (values[left] <= values[mid]) {
            if (values[left] <= target &&
                target < values[mid]) {
                if (mid == 0) {
                    break;
                }
                right = mid - 1;
            } else {
                left = mid + 1;
            }
        } else {
            if (values[mid] < target &&
                target <= values[right]) {
                left = mid + 1;
            } else {
                if (mid == 0) {
                    break;
                }
                right = mid - 1;
            }
        }
    }

    return {"rotatedSearch", nullopt, nullopt, comparisons};
}

SearchResult rotatedSearchWithDuplicates(
    const vector<int>& values,
    int target
) {
    if (values.empty()) {
        return {
            "rotatedSearchWithDuplicates",
            nullopt,
            nullopt,
            0
        };
    }

    size_t left = 0;
    size_t right = values.size() - 1;
    size_t comparisons = 0;

    while (left <= right) {
        size_t mid = left + (right - left) / 2;
        ++comparisons;

        if (values[mid] == target) {
            return {
                "rotatedSearchWithDuplicates",
                mid,
                values[mid],
                comparisons
            };
        }

        if (values[left] == values[mid] &&
            values[mid] == values[right]) {
            ++left;

            if (right == 0) {
                break;
            }

            --right;
            continue;
        }

        if (values[left] <= values[mid]) {
            if (values[left] <= target &&
                target < values[mid]) {
                if (mid == 0) {
                    break;
                }
                right = mid - 1;
            } else {
                left = mid + 1;
            }
        } else {
            if (values[mid] < target &&
                target <= values[right]) {
                left = mid + 1;
            } else {
                if (mid == 0) {
                    break;
                }
                right = mid - 1;
            }
        }
    }

    return {
        "rotatedSearchWithDuplicates",
        nullopt,
        nullopt,
        comparisons
    };
}

SearchResult findBitonicPeak(const vector<int>& values) {
    if (values.empty()) {
        throw SearchError("Bitonic array cannot be empty.");
    }

    size_t left = 0;
    size_t right = values.size() - 1;
    size_t comparisons = 0;

    while (left < right) {
        size_t mid = left + (right - left) / 2;
        ++comparisons;

        if (values[mid] < values[mid + 1]) {
            left = mid + 1;
        } else {
            right = mid;
        }
    }

    return {
        "findBitonicPeak",
        left,
        values[left],
        comparisons
    };
}

SearchResult searchBitonic(
    const vector<int>& values,
    int target
) {
    if (values.empty()) {
        return {"searchBitonic", nullopt, nullopt, 0};
    }

    SearchResult peak = findBitonicPeak(values);
    size_t comparisons = peak.comparisons;

    size_t left = 0;
    size_t right = *peak.index;

    while (left <= right) {
        size_t mid = left + (right - left) / 2;
        ++comparisons;

        if (values[mid] == target) {
            return {
                "searchBitonic",
                mid,
                values[mid],
                comparisons
            };
        }

        if (values[mid] < target) {
            left = mid + 1;
        } else {
            if (mid == 0) {
                break;
            }
            right = mid - 1;
        }
    }

    left = *peak.index + 1;
    right = values.size() - 1;

    while (left <= right) {
        size_t mid = left + (right - left) / 2;
        ++comparisons;

        if (values[mid] == target) {
            return {
                "searchBitonic",
                mid,
                values[mid],
                comparisons
            };
        }

        // The second half is descending.
        if (values[mid] > target) {
            left = mid + 1;
        } else {
            if (mid == 0) {
                break;
            }
            right = mid - 1;
        }
    }

    return {
        "searchBitonic",
        nullopt,
        nullopt,
        comparisons
    };
}

void validateMatrix(const vector<vector<int>>& matrix) {
    if (matrix.empty()) {
        return;
    }

    const size_t columns = matrix.front().size();

    for (const auto& row : matrix) {
        if (row.size() != columns) {
            throw SearchError("Matrix must be rectangular.");
        }
    }
}

SearchResult searchGlobalMatrix(
    const vector<vector<int>>& matrix,
    int target
) {
    validateMatrix(matrix);

    if (matrix.empty() || matrix.front().empty()) {
        return {"searchGlobalMatrix", nullopt, nullopt, 0};
    }

    const size_t rows = matrix.size();
    const size_t columns = matrix.front().size();

    size_t left = 0;
    size_t right = rows * columns - 1;
    size_t comparisons = 0;

    while (left <= right) {
        size_t mid = left + (right - left) / 2;
        size_t row = mid / columns;
        size_t column = mid % columns;

        ++comparisons;
        int value = matrix[row][column];

        if (value == target) {
            return {
                "searchGlobalMatrix",
                mid,
                value,
                comparisons
            };
        }

        if (value < target) {
            left = mid + 1;
        } else {
            if (mid == 0) {
                break;
            }
            right = mid - 1;
        }
    }

    return {
        "searchGlobalMatrix",
        nullopt,
        nullopt,
        comparisons
    };
}

SearchResult searchRowColumnMatrix(
    const vector<vector<int>>& matrix,
    int target
) {
    validateMatrix(matrix);

    if (matrix.empty() || matrix.front().empty()) {
        return {
            "searchRowColumnMatrix",
            nullopt,
            nullopt,
            0
        };
    }

    const size_t rows = matrix.size();
    const size_t columns = matrix.front().size();

    size_t row = 0;
    size_t column = columns - 1;
    size_t comparisons = 0;

    while (row < rows) {
        int value = matrix[row][column];
        ++comparisons;

        if (value == target) {
            return {
                "searchRowColumnMatrix",
                row * columns + column,
                value,
                comparisons
            };
        }

        if (value > target) {
            if (column == 0) {
                break;
            }
            --column;
        } else {
            ++row;
        }
    }

    return {
        "searchRowColumnMatrix",
        nullopt,
        nullopt,
        comparisons
    };
}

size_t lowerBound(const vector<int>& values, int target) {
    size_t left = 0;
    size_t right = values.size();

    while (left < right) {
        size_t mid = left + (right - left) / 2;

        if (values[mid] < target) {
            left = mid + 1;
        } else {
            right = mid;
        }
    }

    return left;
}

size_t upperBound(const vector<int>& values, int target) {
    size_t left = 0;
    size_t right = values.size();

    while (left < right) {
        size_t mid = left + (right - left) / 2;

        if (values[mid] <= target) {
            left = mid + 1;
        } else {
            right = mid;
        }
    }

    return left;
}

pair<int, int> findRange(
    const vector<int>& values,
    int target
) {
    size_t first = lowerBound(values, target);
    size_t end = upperBound(values, target);

    if (first == end) {
        return {-1, -1};
    }

    return {
        static_cast<int>(first),
        static_cast<int>(end - 1)
    };
}

void printResult(const SearchResult& result) {
    cout << result.algorithm << ": ";

    if (result.index.has_value()) {
        cout << "index=" << *result.index
             << ", value=" << *result.value;
    } else {
        cout << "not found";
    }

    cout << ", comparisons=" << result.comparisons << '\n';
}

int main() {
    try {
        const vector<int> sorted{
            2, 5, 8, 12, 17, 21, 29
        };

        const vector<int> rotated{
            13, 18, 25, 2, 8, 10
        };

        const vector<int> duplicateRotated{
            2, 5, 6, 0, 0, 1, 2
        };

        const vector<int> bitonic{
            2, 5, 9, 14, 19, 16, 11, 4
        };

        const vector<vector<int>> globalMatrix{
            {1, 3, 5, 7},
            {10, 12, 14, 16},
            {20, 22, 24, 26}
        };

        const vector<vector<int>> rowColumnMatrix{
            {1, 4, 7, 11},
            {2, 5, 8, 13},
            {3, 6, 9, 15},
            {10, 12, 14, 18}
        };

        auto basic = binarySearch(sorted, 17);
        assert(basic.index == optional<size_t>{4});

        auto rotatedResult = rotatedSearch(rotated, 8);
        assert(rotatedResult.index == optional<size_t>{4});

        auto duplicateResult =
            rotatedSearchWithDuplicates(duplicateRotated, 0);
        assert(
            duplicateResult.index == optional<size_t>{3} ||
            duplicateResult.index == optional<size_t>{4}
        );

        auto peak = findBitonicPeak(bitonic);
        assert(peak.index == optional<size_t>{4});

        auto bitonicResult = searchBitonic(bitonic, 11);
        assert(bitonicResult.index == optional<size_t>{6});

        auto matrixResult = searchGlobalMatrix(
            globalMatrix,
            22
        );
        assert(matrixResult.index == optional<size_t>{9});

        auto staircaseResult = searchRowColumnMatrix(
            rowColumnMatrix,
            9
        );
        assert(staircaseResult.index == optional<size_t>{10});

        auto range = findRange(
            vector<int>{1, 2, 2, 2, 4, 7},
            2
        );
        assert(range == make_pair(1, 3));

        printResult(basic);
        printResult(rotatedResult);
        printResult(duplicateResult);
        printResult(peak);
        printResult(bitonicResult);
        printResult(matrixResult);
        printResult(staircaseResult);

        cout << "Range of 2: ["
             << range.first << ", "
             << range.second << "]\n";

        cout << "All C++17 checks passed.\n";
    } catch (const exception& error) {
        cerr << "Search failure: "
             << error.what() << '\n';
        return 1;
    }

    return 0;
}
