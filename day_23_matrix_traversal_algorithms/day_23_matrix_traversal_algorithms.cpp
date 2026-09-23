/*
    Matrix Traversal Algorithms
    ============================

    A C++17 case study implementing a matrix inspection engine for a
    warehouse robot-grid system.

    The modeled system represents a rectangular warehouse floor as a matrix.
    Each cell contains an integer representing a sensor reading, inventory
    quantity, or grid identifier.

    The program progressively implements:

        1. Row-wise traversal
        2. Column-wise traversal
        3. Main diagonal traversal
        4. Secondary diagonal traversal
        5. Boundary traversal
        6. Spiral traversal
        7. Row zigzag traversal
        8. Column zigzag traversal
        9. Coordinate-based traversal
       10. Matrix transposition
       11. Statistical analysis
       12. Validation
       13. Automated correctness tests
       14. Edge-case handling

    Compile:
        g++ -std=c++17 -O2 matrix_traversal.cpp -o matrix_traversal

    Run:
        ./matrix_traversal
*/

#include <algorithm>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using Matrix = std::vector<std::vector<int>>;
using Coordinate = std::pair<std::size_t, std::size_t>;


// -----------------------------------------------------------------------------
// Matrix validation
// -----------------------------------------------------------------------------

class MatrixValidator {
public:
    static std::pair<std::size_t, std::size_t>
    dimensions(const Matrix& matrix) {
        if (matrix.empty()) {
            return {0, 0};
        }

        const std::size_t columns = matrix.front().size();

        for (std::size_t row = 0; row < matrix.size(); ++row) {
            if (matrix[row].size() != columns) {
                throw std::invalid_argument(
                    "Matrix must be rectangular: every row must contain "
                    "the same number of columns."
                );
            }
        }

        return {matrix.size(), columns};
    }

    static void requireNonEmpty(const Matrix& matrix) {
        const auto [rows, columns] = dimensions(matrix);

        if (rows == 0 || columns == 0) {
            throw std::invalid_argument(
                "This operation requires a non-empty matrix."
            );
        }
    }
};


// -----------------------------------------------------------------------------
// Matrix display
// -----------------------------------------------------------------------------

void printMatrix(const Matrix& matrix) {
    const auto [rows, columns] = MatrixValidator::dimensions(matrix);

    if (rows == 0 || columns == 0) {
        std::cout << "[empty matrix]\n";
        return;
    }

    std::size_t width = 1;

    for (const auto& row : matrix) {
        for (int value : row) {
            width = std::max(
                width,
                std::to_string(value).size()
            );
        }
    }

    for (const auto& row : matrix) {
        for (std::size_t column = 0; column < columns; ++column) {
            std::cout
                << std::setw(static_cast<int>(width))
                << row[column];

            if (column + 1 < columns) {
                std::cout << ' ';
            }
        }
        std::cout << '\n';
    }
}


void printValues(
    const std::string& label,
    const std::vector<int>& values
) {
    std::cout << std::left << std::setw(24) << label << ": ";

    for (std::size_t index = 0; index < values.size(); ++index) {
        std::cout << values[index];

        if (index + 1 < values.size()) {
            std::cout << " -> ";
        }
    }

    std::cout << '\n';
}


void printCoordinates(
    const std::vector<Coordinate>& coordinates
) {
    for (const auto& [row, column] : coordinates) {
        std::cout << "(" << row << ", " << column << ") ";
    }

    std::cout << '\n';
}


// -----------------------------------------------------------------------------
// Matrix traversal engine
// -----------------------------------------------------------------------------

class MatrixTraversalEngine {
public:
    static std::vector<int>
    rowWise(const Matrix& matrix) {
        const auto [rows, columns] =
            MatrixValidator::dimensions(matrix);

        std::vector<int> result;
        result.reserve(rows * columns);

        for (std::size_t row = 0; row < rows; ++row) {
            for (std::size_t column = 0; column < columns; ++column) {
                result.push_back(matrix[row][column]);
            }
        }

        return result;
    }


    static std::vector<int>
    columnWise(const Matrix& matrix) {
        const auto [rows, columns] =
            MatrixValidator::dimensions(matrix);

        std::vector<int> result;
        result.reserve(rows * columns);

        for (std::size_t column = 0; column < columns; ++column) {
            for (std::size_t row = 0; row < rows; ++row) {
                result.push_back(matrix[row][column]);
            }
        }

        return result;
    }


    static std::vector<int>
    mainDiagonal(const Matrix& matrix) {
        const auto [rows, columns] =
            MatrixValidator::dimensions(matrix);

        const std::size_t length =
            std::min(rows, columns);

        std::vector<int> result;
        result.reserve(length);

        for (std::size_t index = 0; index < length; ++index) {
            result.push_back(matrix[index][index]);
        }

        return result;
    }


    static std::vector<int>
    secondaryDiagonal(const Matrix& matrix) {
        const auto [rows, columns] =
            MatrixValidator::dimensions(matrix);

        const std::size_t length =
            std::min(rows, columns);

        std::vector<int> result;
        result.reserve(length);

        /*
            For a square N x N matrix, the secondary diagonal contains:

                matrix[0][N - 1]
                matrix[1][N - 2]
                ...
                matrix[N - 1][0]

            For a rectangular matrix, this implementation uses the largest
            square prefix so that coordinates remain valid.
        */
        for (std::size_t index = 0; index < length; ++index) {
            result.push_back(
                matrix[index][length - 1 - index]
            );
        }

        return result;
    }


    static std::vector<int>
    boundary(const Matrix& matrix) {
        const auto [rows, columns] =
            MatrixValidator::dimensions(matrix);

        if (rows == 0 || columns == 0) {
            return {};
        }

        std::vector<int> result;
        result.reserve(2 * rows + 2 * columns);

        // Top edge: left to right.
        for (std::size_t column = 0;
             column < columns;
             ++column) {
            result.push_back(matrix[0][column]);
        }

        // Right edge: top to bottom.
        for (std::size_t row = 1;
             row < rows;
             ++row) {
            result.push_back(matrix[row][columns - 1]);
        }

        // Bottom edge: right to left.
        // Do not repeat the top edge for a single-row matrix.
        if (rows > 1) {
            for (std::size_t column = columns - 1;
                 column-- > 0;) {
                result.push_back(matrix[rows - 1][column]);
            }
        }

        // Left edge: bottom to top.
        // Do not repeat corners.
        if (columns > 1 && rows > 2) {
            for (std::size_t row = rows - 1;
                 row-- > 1;) {
                result.push_back(matrix[row][0]);
            }
        }

        return result;
    }


    static std::vector<int>
    spiral(const Matrix& matrix) {
        const auto [rows, columns] =
            MatrixValidator::dimensions(matrix);

        if (rows == 0 || columns == 0) {
            return {};
        }

        std::vector<int> result;
        result.reserve(rows * columns);

        /*
            Four boundaries define the unvisited rectangle.

                top
                bottom
                left
                right

            Each side is consumed and then moved inward.
        */
        std::size_t top = 0;
        std::size_t bottom = rows - 1;
        std::size_t left = 0;
        std::size_t right = columns - 1;

        while (top <= bottom && left <= right) {
            // Top side.
            for (std::size_t column = left;
                 column <= right;
                 ++column) {
                result.push_back(matrix[top][column]);
            }

            ++top;

            // Right side.
            for (std::size_t row = top;
                 row <= bottom;
                 ++row) {
                result.push_back(matrix[row][right]);
            }

            if (right == 0) {
                /*
                    Prevent unsigned underflow.
                    The loop can safely terminate after setting right below.
                */
                if (left == 0) {
                    right = 0;
                } else {
                    --right;
                }
            } else {
                --right;
            }

            // Bottom side.
            if (top <= bottom) {
                for (std::size_t column = right + 1;
                     column-- > left;) {
                    result.push_back(matrix[bottom][column]);
                }

                if (bottom == 0) {
                    break;
                }

                --bottom;
            }

            // Left side.
            if (left <= right) {
                for (std::size_t row = bottom + 1;
                     row-- > top;) {
                    result.push_back(matrix[row][left]);
                }

                ++left;
            }
        }

        /*
            The unsigned-boundary implementation above is intentionally
            conservative about underflow. For production code, signed
            indices can make boundary arithmetic easier to read. The public
            wrapper below uses a second, signed implementation to make the
            actual case study straightforward.
        */
        return spiralSigned(matrix);
    }


    static std::vector<int>
    spiralSigned(const Matrix& matrix) {
        const auto [rows, columns] =
            MatrixValidator::dimensions(matrix);

        if (rows == 0 || columns == 0) {
            return {};
        }

        std::vector<int> result;
        result.reserve(rows * columns);

        long long top = 0;
        long long bottom =
            static_cast<long long>(rows) - 1;
        long long left = 0;
        long long right =
            static_cast<long long>(columns) - 1;

        while (top <= bottom && left <= right) {
            for (long long column = left;
                 column <= right;
                 ++column) {
                result.push_back(
                    matrix[
                        static_cast<std::size_t>(top)
                    ][
                        static_cast<std::size_t>(column)
                    ]
                );
            }

            ++top;

            for (long long row = top;
                 row <= bottom;
                 ++row) {
                result.push_back(
                    matrix[
                        static_cast<std::size_t>(row)
                    ][
                        static_cast<std::size_t>(right)
                    ]
                );
            }

            --right;

            if (top <= bottom) {
                for (long long column = right;
                     column >= left;
                     --column) {
                    result.push_back(
                        matrix[
                            static_cast<std::size_t>(bottom)
                        ][
                            static_cast<std::size_t>(column)
                        ]
                    );
                }

                --bottom;
            }

            if (left <= right) {
                for (long long row = bottom;
                     row >= top;
                     --row) {
                    result.push_back(
                        matrix[
                            static_cast<std::size_t>(row)
                        ][
                            static_cast<std::size_t>(left)
                        ]
                    );
                }

                ++left;
            }
        }

        return result;
    }


    static std::vector<int>
    rowZigzag(const Matrix& matrix) {
        const auto [rows, columns] =
            MatrixValidator::dimensions(matrix);

        std::vector<int> result;
        result.reserve(rows * columns);

        for (std::size_t row = 0; row < rows; ++row) {
            if (row % 2 == 0) {
                for (std::size_t column = 0;
                     column < columns;
                     ++column) {
                    result.push_back(matrix[row][column]);
                }
            } else {
                for (std::size_t column = columns;
                     column-- > 0;) {
                    result.push_back(matrix[row][column]);
                }
            }
        }

        return result;
    }


    static std::vector<int>
    columnZigzag(const Matrix& matrix) {
        const auto [rows, columns] =
            MatrixValidator::dimensions(matrix);

        std::vector<int> result;
        result.reserve(rows * columns);

        for (std::size_t column = 0;
             column < columns;
             ++column) {
            if (column % 2 == 0) {
                for (std::size_t row = 0;
                     row < rows;
                     ++row) {
                    result.push_back(matrix[row][column]);
                }
            } else {
                for (std::size_t row = rows;
                     row-- > 0;) {
                    result.push_back(matrix[row][column]);
                }
            }
        }

        return result;
    }


    static std::vector<Coordinate>
    spiralCoordinates(const Matrix& matrix) {
        const auto [rows, columns] =
            MatrixValidator::dimensions(matrix);

        if (rows == 0 || columns == 0) {
            return {};
        }

        std::vector<Coordinate> result;
        result.reserve(rows * columns);

        long long top = 0;
        long long bottom =
            static_cast<long long>(rows) - 1;
        long long left = 0;
        long long right =
            static_cast<long long>(columns) - 1;

        while (top <= bottom && left <= right) {
            for (long long column = left;
                 column <= right;
                 ++column) {
                result.emplace_back(
                    static_cast<std::size_t>(top),
                    static_cast<std::size_t>(column)
                );
            }

            ++top;

            for (long long row = top;
                 row <= bottom;
                 ++row) {
                result.emplace_back(
                    static_cast<std::size_t>(row),
                    static_cast<std::size_t>(right)
                );
            }

            --right;

            if (top <= bottom) {
                for (long long column = right;
                     column >= left;
                     --column) {
                    result.emplace_back(
                        static_cast<std::size_t>(bottom),
                        static_cast<std::size_t>(column)
                    );
                }

                --bottom;
            }

            if (left <= right) {
                for (long long row = bottom;
                     row >= top;
                     --row) {
                    result.emplace_back(
                        static_cast<std::size_t>(row),
                        static_cast<std::size_t>(left)
                    );
                }

                ++left;
            }
        }

        return result;
    }
};


// -----------------------------------------------------------------------------
// Transpose
// -----------------------------------------------------------------------------

Matrix transpose(const Matrix& matrix) {
    const auto [rows, columns] =
        MatrixValidator::dimensions(matrix);

    if (rows == 0 || columns == 0) {
        return {};
    }

    Matrix result(
        columns,
        std::vector<int>(rows)
    );

    for (std::size_t row = 0; row < rows; ++row) {
        for (std::size_t column = 0;
             column < columns;
             ++column) {
            result[column][row] = matrix[row][column];
        }
    }

    return result;
}


// -----------------------------------------------------------------------------
// Practical warehouse-grid analysis
// -----------------------------------------------------------------------------

struct GridStatistics {
    std::size_t cellCount{};
    int minimum{};
    int maximum{};
    long long sum{};
    long long boundarySum{};
    int spiralFirst{};
    int spiralLast{};
};


GridStatistics analyzeGrid(const Matrix& matrix) {
    const auto values =
        MatrixTraversalEngine::rowWise(matrix);

    const auto boundary =
        MatrixTraversalEngine::boundary(matrix);

    const auto spiral =
        MatrixTraversalEngine::spiralSigned(matrix);

    if (values.empty()) {
        return {};
    }

    const auto [minimum, maximum] =
        std::minmax_element(values.begin(), values.end());

    const long long total =
        std::accumulate(
            values.begin(),
            values.end(),
            0LL
        );

    const long long boundaryTotal =
        std::accumulate(
            boundary.begin(),
            boundary.end(),
            0LL
        );

    return {
        values.size(),
        *minimum,
        *maximum,
        total,
        boundaryTotal,
        spiral.front(),
        spiral.back()
    };
}


// -----------------------------------------------------------------------------
// Correctness helpers
// -----------------------------------------------------------------------------

void require(
    bool condition,
    const std::string& message
) {
    if (!condition) {
        throw std::runtime_error(
            "Test failed: " + message
        );
    }
}


void verifyFullTraversal(
    const Matrix& matrix,
    const std::vector<int>& values,
    const std::string& name
) {
    const auto [rows, columns] =
        MatrixValidator::dimensions(matrix);

    require(
        values.size() == rows * columns,
        name + " visited the wrong number of cells."
    );

    auto expected = matrix.empty()
        ? std::vector<int>{}
        : MatrixTraversalEngine::rowWise(matrix);

    auto actual = values;

    std::sort(expected.begin(), expected.end());
    std::sort(actual.begin(), actual.end());

    require(
        expected == actual,
        name + " did not visit exactly the matrix cells."
    );
}


// -----------------------------------------------------------------------------
// Automated tests
// -----------------------------------------------------------------------------

void runTests() {
    const std::vector<Matrix> testMatrices = {
        {},
        {{1}},
        {{1, 2, 3, 4}},
        {{1}, {2}, {3}, {4}},
        {
            {1, 2},
            {3, 4}
        },
        {
            {1, 2, 3},
            {4, 5, 6},
            {7, 8, 9}
        },
        {
            {1, 2, 3, 4},
            {5, 6, 7, 8},
            {9, 10, 11, 12}
        },
        {
            {1, 2, 3},
            {4, 5, 6},
            {7, 8, 9},
            {10, 11, 12}
        }
    };

    for (const auto& matrix : testMatrices) {
        verifyFullTraversal(
            matrix,
            MatrixTraversalEngine::rowWise(matrix),
            "row-wise traversal"
        );

        verifyFullTraversal(
            matrix,
            MatrixTraversalEngine::columnWise(matrix),
            "column-wise traversal"
        );

        verifyFullTraversal(
            matrix,
            MatrixTraversalEngine::spiralSigned(matrix),
            "spiral traversal"
        );

        verifyFullTraversal(
            matrix,
            MatrixTraversalEngine::rowZigzag(matrix),
            "row zigzag traversal"
        );

        verifyFullTraversal(
            matrix,
            MatrixTraversalEngine::columnZigzag(matrix),
            "column zigzag traversal"
        );
    }

    const Matrix square = {
        {1, 2, 3},
        {4, 5, 6},
        {7, 8, 9}
    };

    require(
        MatrixTraversalEngine::mainDiagonal(square)
        == std::vector<int>{1, 5, 9},
        "main diagonal"
    );

    require(
        MatrixTraversalEngine::secondaryDiagonal(square)
        == std::vector<int>{3, 5, 7},
        "secondary diagonal"
    );

    require(
        MatrixTraversalEngine::boundary(square)
        == std::vector<int>{1, 2, 3, 6, 9, 8, 7, 4},
        "boundary traversal"
    );

    require(
        MatrixTraversalEngine::spiralSigned(square)
        == std::vector<int>{
            1, 2, 3, 6, 9, 8, 7, 4, 5
        },
        "spiral traversal"
    );

    std::cout << "\nAll C++ correctness tests passed.\n";
}


// -----------------------------------------------------------------------------
// Edge-case demonstrations
// -----------------------------------------------------------------------------

void demonstrateEdgeCases() {
    const std::vector<std::pair<std::string, Matrix>> examples = {
        {"single element", {{42}}},
        {"single row", {{1, 2, 3, 4, 5}}},
        {"single column", {{1}, {2}, {3}, {4}, {5}}},
        {
            "rectangular",
            {
                {1, 2, 3, 4},
                {5, 6, 7, 8}
            }
        }
    };

    std::cout << "\n=== Edge Cases ===\n";

    for (const auto& [name, matrix] : examples) {
        std::cout << "\n" << name << "\n";
        printMatrix(matrix);

        printValues(
            "row-wise",
            MatrixTraversalEngine::rowWise(matrix)
        );

        printValues(
            "column-wise",
            MatrixTraversalEngine::columnWise(matrix)
        );

        printValues(
            "boundary",
            MatrixTraversalEngine::boundary(matrix)
        );

        printValues(
            "spiral",
            MatrixTraversalEngine::spiralSigned(matrix)
        );

        printValues(
            "row zigzag",
            MatrixTraversalEngine::rowZigzag(matrix)
        );
    }
}


// -----------------------------------------------------------------------------
// Invalid input demonstration
// -----------------------------------------------------------------------------

void demonstrateValidationErrors() {
    std::cout << "\n=== Validation Errors ===\n";

    const Matrix invalidMatrix = {
        {1, 2},
        {3}
    };

    try {
        MatrixValidator::dimensions(invalidMatrix);
    } catch (const std::exception& error) {
        std::cout
            << "Rejected invalid matrix: "
            << error.what()
            << '\n';
    }
}


// -----------------------------------------------------------------------------
// Main case study
// -----------------------------------------------------------------------------

int main() {
    try {
        /*
            Scenario:

            A warehouse contains a rectangular sensor grid. Every integer
            represents a measurement captured from one physical location.

            Different downstream operations require different traversal
            orders. For example:

              - row-wise order can mirror row-oriented storage;
              - column-wise order can inspect vertical zones;
              - boundary traversal can inspect perimeter sensors;
              - spiral traversal can progressively inspect outer-to-inner
                regions;
              - zigzag traversal can model alternating scan directions.
        */
        const Matrix warehouseGrid = {
            {1,  2,  3,  4,  5},
            {6,  7,  8,  9, 10},
            {11, 12, 13, 14, 15},
            {16, 17, 18, 19, 20}
        };

        std::cout
            << "=== Matrix Traversal Case Study ===\n\n";

        std::cout << "Warehouse sensor grid:\n";
        printMatrix(warehouseGrid);

        std::cout << "\n=== Traversal Results ===\n";

        printValues(
            "row-wise",
            MatrixTraversalEngine::rowWise(warehouseGrid)
        );

        printValues(
            "column-wise",
            MatrixTraversalEngine::columnWise(warehouseGrid)
        );

        printValues(
            "boundary",
            MatrixTraversalEngine::boundary(warehouseGrid)
        );

        printValues(
            "spiral",
            MatrixTraversalEngine::spiralSigned(warehouseGrid)
        );

        printValues(
            "row zigzag",
            MatrixTraversalEngine::rowZigzag(warehouseGrid)
        );

        printValues(
            "column zigzag",
            MatrixTraversalEngine::columnZigzag(warehouseGrid)
        );

        const Matrix squareGrid = {
            {1,  2,  3,  4},
            {5,  6,  7,  8},
            {9, 10, 11, 12},
            {13, 14, 15, 16}
        };

        std::cout << "\n=== Diagonal Analysis ===\n";
        printMatrix(squareGrid);

        printValues(
            "main diagonal",
            MatrixTraversalEngine::mainDiagonal(squareGrid)
        );

        printValues(
            "secondary diagonal",
            MatrixTraversalEngine::secondaryDiagonal(squareGrid)
        );

        std::cout
            << "\n=== Spiral Coordinates ===\n";

        const auto coordinates =
            MatrixTraversalEngine::spiralCoordinates(
                warehouseGrid
            );

        printCoordinates(coordinates);

        std::cout
            << "\n=== Transposed Grid ===\n";

        printMatrix(transpose(warehouseGrid));

        std::cout
            << "\n=== Grid Statistics ===\n";

        const GridStatistics statistics =
            analyzeGrid(warehouseGrid);

        std::cout
            << "Cell count       : "
            << statistics.cellCount << '\n';

        std::cout
            << "Minimum          : "
            << statistics.minimum << '\n';

        std::cout
            << "Maximum          : "
            << statistics.maximum << '\n';

        std::cout
            << "Total             : "
            << statistics.sum << '\n';

        std::cout
            << "Boundary total    : "
            << statistics.boundarySum << '\n';

        std::cout
            << "First spiral cell : "
            << statistics.spiralFirst << '\n';

        std::cout
            << "Last spiral cell  : "
            << statistics.spiralLast << '\n';

        runTests();
        demonstrateEdgeCases();
        demonstrateValidationErrors();

        return 0;
    } catch (const std::exception& error) {
        std::cerr
            << "Fatal error: "
            << error.what()
            << '\n';

        return 1;
    }
}
