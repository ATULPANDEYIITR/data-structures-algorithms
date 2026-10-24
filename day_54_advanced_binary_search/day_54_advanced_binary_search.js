"use strict";

/*
 * Advanced Binary Search
 *
 * This file models several search structures:
 * 1. ordinary sorted arrays
 * 2. rotated sorted arrays
 * 3. rotated arrays containing duplicates
 * 4. bitonic arrays
 * 5. row-major globally sorted matrices
 * 6. matrices sorted independently by rows and columns
 *
 * No external packages are required.
 */

class SearchError extends Error {}

function result(algorithm, index, value, comparisons) {
    return { algorithm, index, value, comparisons };
}

function binarySearch(values, target) {
    let left = 0;
    let right = values.length - 1;
    let comparisons = 0;

    while (left <= right) {
        const mid = left + Math.floor((right - left) / 2);
        const value = values[mid];
        comparisons++;

        if (value === target) {
            return result("binarySearch", mid, value, comparisons);
        }

        if (value < target) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }

    return result("binarySearch", null, null, comparisons);
}

function rotatedBinarySearch(values, target) {
    let left = 0;
    let right = values.length - 1;
    let comparisons = 0;

    while (left <= right) {
        const mid = left + Math.floor((right - left) / 2);
        const middle = values[mid];
        comparisons++;

        if (middle === target) {
            return result(
                "rotatedBinarySearch",
                mid,
                middle,
                comparisons
            );
        }

        // The left section is sorted.
        if (values[left] <= middle) {
            if (values[left] <= target && target < middle) {
                right = mid - 1;
            } else {
                left = mid + 1;
            }
        } else {
            // The right section is sorted.
            if (middle < target && target <= values[right]) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
    }

    return result("rotatedBinarySearch", null, null, comparisons);
}

function rotatedBinarySearchWithDuplicates(values, target) {
    let left = 0;
    let right = values.length - 1;
    let comparisons = 0;

    while (left <= right) {
        const mid = left + Math.floor((right - left) / 2);
        const middle = values[mid];
        comparisons++;

        if (middle === target) {
            return result(
                "rotatedBinarySearchWithDuplicates",
                mid,
                middle,
                comparisons
            );
        }

        /*
         * When all three boundary values are equal, the sorted-half
         * test provides no information. Shrinking both boundaries
         * avoids an incorrect branch at the cost of O(n) worst case.
         */
        if (
            values[left] === middle &&
            middle === values[right]
        ) {
            left++;
            right--;
            continue;
        }

        if (values[left] <= middle) {
            if (values[left] <= target && target < middle) {
                right = mid - 1;
            } else {
                left = mid + 1;
            }
        } else {
            if (middle < target && target <= values[right]) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
    }

    return result(
        "rotatedBinarySearchWithDuplicates",
        null,
        null,
        comparisons
    );
}

function validateBitonic(values) {
    if (values.length === 0) {
        throw new SearchError("A bitonic array cannot be empty.");
    }
}

function findBitonicPeak(values) {
    validateBitonic(values);

    let left = 0;
    let right = values.length - 1;
    let comparisons = 0;

    while (left < right) {
        const mid = left + Math.floor((right - left) / 2);
        comparisons++;

        if (values[mid] < values[mid + 1]) {
            left = mid + 1;
        } else {
            right = mid;
        }
    }

    return result(
        "findBitonicPeak",
        left,
        values[left],
        comparisons
    );
}

function searchBitonic(values, target) {
    validateBitonic(values);

    const peak = findBitonicPeak(values);
    let comparisons = peak.comparisons;

    // Increasing side.
    let left = 0;
    let right = peak.index;

    while (left <= right) {
        const mid = left + Math.floor((right - left) / 2);
        comparisons++;

        if (values[mid] === target) {
            return result(
                "searchBitonic",
                mid,
                values[mid],
                comparisons
            );
        }

        if (values[mid] < target) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }

    // Decreasing side.
    left = peak.index + 1;
    right = values.length - 1;

    while (left <= right) {
        const mid = left + Math.floor((right - left) / 2);
        comparisons++;

        if (values[mid] === target) {
            return result(
                "searchBitonic",
                mid,
                values[mid],
                comparisons
            );
        }

        // Reverse binary-search direction.
        if (values[mid] > target) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }

    return result("searchBitonic", null, null, comparisons);
}

function validateRectangular(matrix) {
    if (matrix.length === 0) {
        return 0;
    }

    const columns = matrix[0].length;

    for (const row of matrix) {
        if (row.length !== columns) {
            throw new SearchError("Matrix must be rectangular.");
        }
    }

    return columns;
}

function searchGloballySortedMatrix(matrix, target) {
    const columns = validateRectangular(matrix);

    if (matrix.length === 0 || columns === 0) {
        return result(
            "searchGloballySortedMatrix",
            null,
            null,
            0
        );
    }

    let left = 0;
    let right = matrix.length * columns - 1;
    let comparisons = 0;

    while (left <= right) {
        const mid = left + Math.floor((right - left) / 2);
        const row = Math.floor(mid / columns);
        const column = mid % columns;
        const value = matrix[row][column];
        comparisons++;

        if (value === target) {
            return result(
                "searchGloballySortedMatrix",
                mid,
                value,
                comparisons
            );
        }

        if (value < target) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }

    return result(
        "searchGloballySortedMatrix",
        null,
        null,
        comparisons
    );
}

function searchRowColumnMatrix(matrix, target) {
    const columns = validateRectangular(matrix);

    if (matrix.length === 0 || columns === 0) {
        return result(
            "searchRowColumnMatrix",
            null,
            null,
            0
        );
    }

    let row = 0;
    let column = columns - 1;
    let comparisons = 0;

    while (row < matrix.length && column >= 0) {
        const value = matrix[row][column];
        comparisons++;

        if (value === target) {
            return result(
                "searchRowColumnMatrix",
                row * columns + column,
                value,
                comparisons
            );
        }

        if (value > target) {
            column--;
        } else {
            row++;
        }
    }

    return result(
        "searchRowColumnMatrix",
        null,
        null,
        comparisons
    );
}

function lowerBound(values, target) {
    let left = 0;
    let right = values.length;

    while (left < right) {
        const mid = left + Math.floor((right - left) / 2);

        if (values[mid] < target) {
            left = mid + 1;
        } else {
            right = mid;
        }
    }

    return left;
}

function upperBound(values, target) {
    let left = 0;
    let right = values.length;

    while (left < right) {
        const mid = left + Math.floor((right - left) / 2);

        if (values[mid] <= target) {
            left = mid + 1;
        } else {
            right = mid;
        }
    }

    return left;
}

function findRange(values, target) {
    const first = lowerBound(values, target);
    const end = upperBound(values, target);

    return first === end
        ? [-1, -1]
        : [first, end - 1];
}

function runExamples() {
    const sorted = [2, 5, 8, 12, 17, 21, 29];
    console.assert(binarySearch(sorted, 17).index === 4);

    const rotated = [13, 18, 25, 2, 8, 10];
    console.assert(rotatedBinarySearch(rotated, 8).index === 4);

    const duplicateRotated = [2, 5, 6, 0, 0, 1, 2];
    const duplicateResult =
        rotatedBinarySearchWithDuplicates(duplicateRotated, 0);
    console.assert(
        duplicateResult.index === 3 ||
        duplicateResult.index === 4
    );

    const bitonic = [2, 5, 9, 14, 19, 16, 11, 4];
    console.assert(findBitonicPeak(bitonic).index === 4);
    console.assert(searchBitonic(bitonic, 11).index === 6);

    const matrix = [
        [1, 3, 5, 7],
        [10, 12, 14, 16],
        [20, 22, 24, 26]
    ];
    console.assert(
        searchGloballySortedMatrix(matrix, 22).index === 9
    );

    const rowColumnMatrix = [
        [1, 4, 7, 11],
        [2, 5, 8, 13],
        [3, 6, 9, 15],
        [10, 12, 14, 18]
    ];
    console.assert(
        searchRowColumnMatrix(rowColumnMatrix, 9).index === 10
    );

    console.assert(
        JSON.stringify(findRange([1, 2, 2, 2, 4, 7], 2)) ===
        JSON.stringify([1, 3])
    );

    console.log("Advanced binary-search examples passed.");
    console.log(rotatedBinarySearch(rotated, 8));
    console.log(findBitonicPeak(bitonic));
    console.log(searchGloballySortedMatrix(matrix, 22));
    console.log(findRange([1, 2, 2, 2, 4, 7], 2));
}

runExamples();
