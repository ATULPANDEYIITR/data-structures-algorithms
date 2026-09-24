/*
 * Advanced Matrix Problems
 *
 * C++17 industry-style case study:
 * A grid analytics and image-processing engine that combines
 * matrix transformations, spatial queries, binary-grid analysis,
 * shortest-path search, connected components, prefix sums,
 * range updates, sparse matrices, and performance-aware design.
 *
 * Compile:
 *     g++ -std=c++17 -O2 -Wall -Wextra -pedantic matrix_engine.cpp -o matrix_engine
 */

#include <algorithm>
#include <cassert>
#include <cstddef>
#include <deque>
#include <exception>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <optional>
#include <queue>
#include <stdexcept>
#include <string>
#include <tuple>
#include <unordered_set>
#include <utility>
#include <vector>

using Matrix = std::vector<std::vector<long long>>;

struct Position {
    int row;
    int column;

    bool operator==(const Position& other) const {
        return row == other.row && column == other.column;
    }
};

struct PositionHash {
    std::size_t operator()(const Position& position) const {
        return std::hash<int>{}(position.row) ^
               (std::hash<int>{}(position.column) << 1);
    }
};

class MatrixEngine {
public:
    static void validate(const Matrix& matrix) {
        if (matrix.empty()) {
            throw std::invalid_argument("Matrix cannot be empty.");
        }

        if (matrix.front().empty()) {
            throw std::invalid_argument("Matrix rows cannot be empty.");
        }

        const std::size_t columns = matrix.front().size();

        for (const auto& row : matrix) {
            if (row.size() != columns) {
                throw std::invalid_argument(
                    "Matrix must be rectangular."
                );
            }
        }
    }

    static void validateSquare(const Matrix& matrix) {
        validate(matrix);

        if (matrix.size() != matrix.front().size()) {
            throw std::invalid_argument(
                "Operation requires a square matrix."
            );
        }
    }

    static void print(
        const Matrix& matrix,
        const std::string& title
    ) {
        std::cout << "\n" << title << "\n";

        for (const auto& row : matrix) {
            for (long long value : row) {
                std::cout
                    << std::setw(6)
                    << value;
            }

            std::cout << '\n';
        }
    }

    // ------------------------------------------------------------------------
    // Matrix transformation
    // ------------------------------------------------------------------------

    static Matrix transpose(const Matrix& matrix) {
        validate(matrix);

        const std::size_t rows = matrix.size();
        const std::size_t columns = matrix.front().size();

        Matrix result(
            columns,
            std::vector<long long>(rows)
        );

        for (std::size_t row = 0; row < rows; ++row) {
            for (std::size_t column = 0; column < columns; ++column) {
                result[column][row] = matrix[row][column];
            }
        }

        return result;
    }

    static void transposeInPlace(Matrix& matrix) {
        validateSquare(matrix);

        const std::size_t n = matrix.size();

        for (std::size_t row = 0; row < n; ++row) {
            for (std::size_t column = row + 1; column < n; ++column) {
                std::swap(
                    matrix[row][column],
                    matrix[column][row]
                );
            }
        }
    }

    static void rotateClockwiseInPlace(Matrix& matrix) {
        validateSquare(matrix);

        // Transpose + reverse each row gives a clockwise rotation.
        transposeInPlace(matrix);

        for (auto& row : matrix) {
            std::reverse(row.begin(), row.end());
        }
    }

    // ------------------------------------------------------------------------
    // Search in sorted matrices
    // ------------------------------------------------------------------------

    static std::optional<Position> searchRowColumnSorted(
        const Matrix& matrix,
        long long target
    ) {
        validate(matrix);

        int row = 0;
        int column = static_cast<int>(matrix.front().size()) - 1;

        while (
            row < static_cast<int>(matrix.size()) &&
            column >= 0
        ) {
            const long long value = matrix[row][column];

            if (value == target) {
                return Position{row, column};
            }

            if (value > target) {
                --column;
            } else {
                ++row;
            }
        }

        return std::nullopt;
    }

    // ------------------------------------------------------------------------
    // Prefix sums
    // ------------------------------------------------------------------------

    static Matrix buildPrefixSum(const Matrix& matrix) {
        validate(matrix);

        const std::size_t rows = matrix.size();
        const std::size_t columns = matrix.front().size();

        Matrix prefix(
            rows + 1,
            std::vector<long long>(columns + 1, 0)
        );

        for (std::size_t row = 0; row < rows; ++row) {
            long long running = 0;

            for (std::size_t column = 0; column < columns; ++column) {
                running += matrix[row][column];

                prefix[row + 1][column + 1] =
                    prefix[row][column + 1] +
                    running;
            }
        }

        return prefix;
    }

    static long long rectangleSum(
        const Matrix& prefix,
        int top,
        int left,
        int bottom,
        int right
    ) {
        if (top < 0 ||
            left < 0 ||
            bottom < top ||
            right < left) {
            throw std::invalid_argument(
                "Invalid rectangle coordinates."
            );
        }

        if (
            bottom + 1 >= static_cast<int>(prefix.size()) ||
            right + 1 >= static_cast<int>(prefix.front().size())
        ) {
            throw std::out_of_range(
                "Rectangle exceeds matrix dimensions."
            );
        }

        return
            prefix[bottom + 1][right + 1] -
            prefix[top][right + 1] -
            prefix[bottom + 1][left] +
            prefix[top][left];
    }

    // ------------------------------------------------------------------------
    // Difference matrix for many rectangle updates
    // ------------------------------------------------------------------------

    static Matrix createDifferenceMatrix(
        int rows,
        int columns
    ) {
        if (rows <= 0 || columns <= 0) {
            throw std::invalid_argument(
                "Dimensions must be positive."
            );
        }

        return Matrix(
            rows + 1,
            std::vector<long long>(columns + 1, 0)
        );
    }

    static void addRectangleDifference(
        Matrix& difference,
        int top,
        int left,
        int bottom,
        int right,
        long long value
    ) {
        const int rows =
            static_cast<int>(difference.size()) - 1;
        const int columns =
            static_cast<int>(difference.front().size()) - 1;

        if (
            top < 0 ||
            left < 0 ||
            bottom < top ||
            right < left ||
            bottom >= rows ||
            right >= columns
        ) {
            throw std::invalid_argument(
                "Invalid rectangle update."
            );
        }

        difference[top][left] += value;
        difference[bottom + 1][left] -= value;
        difference[top][right + 1] -= value;
        difference[bottom + 1][right + 1] += value;
    }

    static Matrix materializeDifference(
        const Matrix& difference
    ) {
        if (difference.size() < 2 ||
            difference.front().size() < 2) {
            throw std::invalid_argument(
                "Difference matrix is too small."
            );
        }

        const std::size_t rows = difference.size() - 1;
        const std::size_t columns = difference.front().size() - 1;

        Matrix result(
            rows,
            std::vector<long long>(columns, 0)
        );

        for (std::size_t row = 0; row < rows; ++row) {
            for (std::size_t column = 0; column < columns; ++column) {
                long long value = difference[row][column];

                if (row > 0) {
                    value += result[row - 1][column];
                }

                if (column > 0) {
                    value += result[row][column - 1];
                }

                if (row > 0 && column > 0) {
                    value -= result[row - 1][column - 1];
                }

                result[row][column] = value;
            }
        }

        return result;
    }

    // ------------------------------------------------------------------------
    // Matrix multiplication
    // ------------------------------------------------------------------------

    static Matrix multiply(
        const Matrix& first,
        const Matrix& second
    ) {
        validate(first);
        validate(second);

        if (first.front().size() != second.size()) {
            throw std::invalid_argument(
                "Matrix dimensions are incompatible."
            );
        }

        const std::size_t rows = first.size();
        const std::size_t shared = first.front().size();
        const std::size_t columns = second.front().size();

        Matrix result(
            rows,
            std::vector<long long>(columns, 0)
        );

        /*
         * The loop ordering i-k-j reuses first[i][k] and often improves
         * cache behavior compared with the naive i-j-k ordering.
         */
        for (std::size_t row = 0; row < rows; ++row) {
            for (std::size_t k = 0; k < shared; ++k) {
                const long long value = first[row][k];

                for (std::size_t column = 0; column < columns; ++column) {
                    result[row][column] +=
                        value * second[k][column];
                }
            }
        }

        return result;
    }

    static Matrix identity(std::size_t size) {
        if (size == 0) {
            throw std::invalid_argument(
                "Identity matrix size must be positive."
            );
        }

        Matrix result(
            size,
            std::vector<long long>(size, 0)
        );

        for (std::size_t index = 0; index < size; ++index) {
            result[index][index] = 1;
        }

        return result;
    }

    static Matrix power(
        const Matrix& matrix,
        unsigned long long exponent
    ) {
        validateSquare(matrix);

        Matrix result = identity(matrix.size());
        Matrix base = matrix;

        while (exponent > 0) {
            if (exponent & 1ULL) {
                result = multiply(result, base);
            }

            base = multiply(base, base);
            exponent >>= 1ULL;
        }

        return result;
    }

    // ------------------------------------------------------------------------
    // Grid graph analysis
    // ------------------------------------------------------------------------

    static int countIslands(const Matrix& grid) {
        validateBinaryGrid(grid);

        const int rows = static_cast<int>(grid.size());
        const int columns = static_cast<int>(grid.front().size());

        Matrix visited(
            rows,
            std::vector<long long>(columns, 0)
        );

        int islands = 0;

        const std::vector<std::pair<int, int>> directions{
            {-1, 0},
            {1, 0},
            {0, -1},
            {0, 1}
        };

        for (int row = 0; row < rows; ++row) {
            for (int column = 0; column < columns; ++column) {
                if (
                    grid[row][column] == 0 ||
                    visited[row][column]
                ) {
                    continue;
                }

                ++islands;

                std::queue<Position> queue;
                queue.push({row, column});
                visited[row][column] = 1;

                while (!queue.empty()) {
                    const Position current = queue.front();
                    queue.pop();

                    for (const auto& [dr, dc] : directions) {
                        const int nextRow = current.row + dr;
                        const int nextColumn = current.column + dc;

                        if (
                            nextRow < 0 ||
                            nextRow >= rows ||
                            nextColumn < 0 ||
                            nextColumn >= columns
                        ) {
                            continue;
                        }

                        if (
                            visited[nextRow][nextColumn] ||
                            grid[nextRow][nextColumn] == 0
                        ) {
                            continue;
                        }

                        visited[nextRow][nextColumn] = 1;
                        queue.push({nextRow, nextColumn});
                    }
                }
            }
        }

        return islands;
    }

    static int shortestPath(
        const Matrix& grid,
        Position start,
        Position goal
    ) {
        validateBinaryGrid(grid);

        const int rows = static_cast<int>(grid.size());
        const int columns = static_cast<int>(grid.front().size());

        auto inBounds = [rows, columns](Position position) {
            return
                position.row >= 0 &&
                position.row < rows &&
                position.column >= 0 &&
                position.column < columns;
        };

        if (!inBounds(start) || !inBounds(goal)) {
            throw std::out_of_range(
                "Start or goal is outside the grid."
            );
        }

        // Zero means traversable; one means blocked.
        if (
            grid[start.row][start.column] != 0 ||
            grid[goal.row][goal.column] != 0
        ) {
            return -1;
        }

        Matrix distance(
            rows,
            std::vector<long long>(columns, -1)
        );

        std::queue<Position> queue;
        queue.push(start);
        distance[start.row][start.column] = 0;

        const std::vector<std::pair<int, int>> directions{
            {-1, 0},
            {1, 0},
            {0, -1},
            {0, 1}
        };

        while (!queue.empty()) {
            const Position current = queue.front();
            queue.pop();

            if (current == goal) {
                return static_cast<int>(
                    distance[current.row][current.column]
                );
            }

            for (const auto& [dr, dc] : directions) {
                Position next{
                    current.row + dr,
                    current.column + dc
                };

                if (!inBounds(next)) {
                    continue;
                }

                if (grid[next.row][next.column] != 0) {
                    continue;
                }

                if (distance[next.row][next.column] != -1) {
                    continue;
                }

                distance[next.row][next.column] =
                    distance[current.row][current.column] + 1;

                queue.push(next);
            }
        }

        return -1;
    }

private:
    static void validateBinaryGrid(const Matrix& grid) {
        validate(grid);

        for (const auto& row : grid) {
            for (long long value : row) {
                if (value != 0 && value != 1) {
                    throw std::invalid_argument(
                        "Grid must contain only zero and one."
                    );
                }
            }
        }
    }
};

// -----------------------------------------------------------------------------
// Sparse matrix representation
// -----------------------------------------------------------------------------

class SparseMatrix {
public:
    SparseMatrix(
        std::size_t rows,
        std::size_t columns
    )
        : rows_(rows),
          columns_(columns) {
        if (rows == 0 || columns == 0) {
            throw std::invalid_argument(
                "Sparse dimensions must be positive."
            );
        }
    }

    void set(
        std::size_t row,
        std::size_t column,
        long long value
    ) {
        validatePosition(row, column);

        const auto key = std::make_pair(row, column);

        if (value == 0) {
            values_.erase(key);
        } else {
            values_[key] = value;
        }
    }

    long long get(
        std::size_t row,
        std::size_t column
    ) const {
        validatePosition(row, column);

        const auto iterator =
            values_.find({row, column});

        if (iterator == values_.end()) {
            return 0;
        }

        return iterator->second;
    }

    Matrix toDense() const {
        Matrix result(
            rows_,
            std::vector<long long>(columns_, 0)
        );

        for (const auto& [position, value] : values_) {
            result[position.first][position.second] = value;
        }

        return result;
    }

    std::size_t nonZeroCount() const {
        return values_.size();
    }

    double density() const {
        return static_cast<double>(nonZeroCount()) /
               static_cast<double>(rows_ * columns_);
    }

private:
    std::size_t rows_;
    std::size_t columns_;

    std::map<
        std::pair<std::size_t, std::size_t>,
        long long
    > values_;

    void validatePosition(
        std::size_t row,
        std::size_t column
    ) const {
        if (row >= rows_ || column >= columns_) {
            throw std::out_of_range(
                "Sparse matrix position is invalid."
            );
        }
    }
};

// -----------------------------------------------------------------------------
// Industry-style case study
// -----------------------------------------------------------------------------

class GridAnalyticsSystem {
public:
    explicit GridAnalyticsSystem(Matrix data)
        : data_(std::move(data)) {
        MatrixEngine::validate(data_);
    }

    void rotateSensorMap() {
        MatrixEngine::validateSquare(data_);
        MatrixEngine::rotateClockwiseInPlace(data_);
    }

    long long queryRegion(
        int top,
        int left,
        int bottom,
        int right
    ) const {
        const Matrix prefix =
            MatrixEngine::buildPrefixSum(data_);

        return MatrixEngine::rectangleSum(
            prefix,
            top,
            left,
            bottom,
            right
        );
    }

    std::optional<Position> findReading(
        long long value
    ) const {
        return MatrixEngine::searchRowColumnSorted(
            data_,
            value
        );
    }

    const Matrix& data() const {
        return data_;
    }

private:
    Matrix data_;
};

// -----------------------------------------------------------------------------
// Tests
// -----------------------------------------------------------------------------

void runTests() {
    Matrix matrix{
        {1, 2, 3},
        {4, 5, 6},
        {7, 8, 9}
    };

    Matrix expectedTranspose{
        {1, 4, 7},
        {2, 5, 8},
        {3, 6, 9}
    };

    assert(
        MatrixEngine::transpose(matrix) ==
        expectedTranspose
    );

    Matrix rotated = matrix;

    MatrixEngine::rotateClockwiseInPlace(rotated);

    Matrix expectedRotation{
        {7, 4, 1},
        {8, 5, 2},
        {9, 6, 3}
    };

    assert(rotated == expectedRotation);

    Matrix sorted{
        {1, 4, 7, 11},
        {2, 5, 8, 12},
        {3, 6, 9, 16},
        {10, 13, 14, 17}
    };

    const auto found =
        MatrixEngine::searchRowColumnSorted(
            sorted,
            9
        );

    assert(found.has_value());
    assert(found->row == 2);
    assert(found->column == 2);

    Matrix prefix = MatrixEngine::buildPrefixSum({
        {1, 2, 3},
        {4, 5, 6},
        {7, 8, 9}
    });

    assert(
        MatrixEngine::rectangleSum(
            prefix,
            1,
            1,
            2,
            2
        ) == 28
    );

    Matrix multiplication =
        MatrixEngine::multiply(
            {
                {1, 2},
                {3, 4}
            },
            {
                {5, 6},
                {7, 8}
            }
        );

    assert(
        multiplication ==
        Matrix{
            {19, 22},
            {43, 50}
        }
    );

    Matrix fibonacciPower =
        MatrixEngine::power(
            {
                {1, 1},
                {1, 0}
            },
            5
        );

    assert(
        fibonacciPower ==
        Matrix{
            {8, 5},
            {5, 3}
        }
    );

    Matrix difference =
        MatrixEngine::createDifferenceMatrix(4, 5);

    MatrixEngine::addRectangleDifference(
        difference,
        1,
        1,
        2,
        3,
        10
    );

    Matrix materialized =
        MatrixEngine::materializeDifference(difference);

    assert(materialized[1][1] == 10);
    assert(materialized[2][3] == 10);
    assert(materialized[0][0] == 0);

    assert(
        MatrixEngine::countIslands({
            {1, 1, 0, 0},
            {0, 1, 0, 1},
            {0, 0, 1, 1}
        }) == 2
    );

    assert(
        MatrixEngine::shortestPath(
            {
                {0, 1, 0, 0},
                {0, 1, 0, 1},
                {0, 0, 0, 1},
                {1, 1, 0, 0}
            },
            {0, 0},
            {3, 3}
        ) == 6
    );

    SparseMatrix sparse(4, 4);

    sparse.set(0, 3, 7);
    sparse.set(2, 1, 3);

    assert(sparse.get(0, 3) == 7);
    assert(sparse.get(1, 1) == 0);
    assert(sparse.nonZeroCount() == 2);

    std::cout << "All C++ tests passed.\n";
}

// -----------------------------------------------------------------------------
// Main demonstration
// -----------------------------------------------------------------------------

int main() {
    try {
        std::cout
            << std::string(80, '=')
            << "\nADVANCED MATRIX PROBLEMS\n"
            << std::string(80, '=')
            << '\n';

        Matrix sensorMap{
            {10, 20, 30, 40},
            {50, 60, 70, 80},
            {90, 100, 110, 120},
            {130, 140, 150, 160}
        };

        MatrixEngine::print(
            sensorMap,
            "Original 4 x 4 sensor map"
        );

        MatrixEngine::print(
            MatrixEngine::transpose(sensorMap),
            "Transposed sensor map"
        );

        MatrixEngine::rotateClockwiseInPlace(sensorMap);

        MatrixEngine::print(
            sensorMap,
            "Sensor map rotated 90 degrees clockwise"
        );

        Matrix sortedReadings{
            {1, 4, 7, 10},
            {2, 5, 8, 12},
            {3, 6, 9, 16},
            {11, 13, 14, 20}
        };

        const auto reading =
            MatrixEngine::searchRowColumnSorted(
                sortedReadings,
                14
            );

        if (reading.has_value()) {
            std::cout
                << "\nReading 14 found at ("
                << reading->row
                << ", "
                << reading->column
                << ")\n";
        } else {
            std::cout << "\nReading not found.\n";
        }

        Matrix analyticsData{
            {1, 2, 3, 4},
            {5, 6, 7, 8},
            {9, 10, 11, 12},
            {13, 14, 15, 16}
        };

        Matrix prefix =
            MatrixEngine::buildPrefixSum(analyticsData);

        MatrixEngine::print(
            prefix,
            "Prefix-sum matrix"
        );

        std::cout
            << "\nRegion sum [1..2][1..3]: "
            << MatrixEngine::rectangleSum(
                prefix,
                1,
                1,
                2,
                3
            )
            << '\n';

        Matrix difference =
            MatrixEngine::createDifferenceMatrix(5, 6);

        MatrixEngine::addRectangleDifference(
            difference,
            1,
            1,
            3,
            4,
            10
        );

        MatrixEngine::addRectangleDifference(
            difference,
            0,
            2,
            2,
            5,
            5
        );

        MatrixEngine::print(
            MatrixEngine::materializeDifference(difference),
            "Materialized rectangle updates"
        );

        Matrix product =
            MatrixEngine::multiply(
                {
                    {1, 2},
                    {3, 4}
                },
                {
                    {5, 6},
                    {7, 8}
                }
            );

        MatrixEngine::print(
            product,
            "Matrix multiplication"
        );

        Matrix power =
            MatrixEngine::power(
                {
                    {1, 1},
                    {1, 0}
                },
                10
            );

        MatrixEngine::print(
            power,
            "Matrix exponentiation"
        );

        Matrix cityGrid{
            {1, 1, 0, 0, 0},
            {1, 0, 0, 1, 1},
            {0, 0, 1, 1, 0},
            {0, 1, 0, 0, 0}
        };

        MatrixEngine::print(
            cityGrid,
            "Binary city connectivity grid"
        );

        std::cout
            << "\nConnected regions: "
            << MatrixEngine::countIslands(cityGrid)
            << '\n';

        Matrix pathGrid{
            {0, 1, 0, 0, 0},
            {0, 1, 0, 1, 0},
            {0, 0, 0, 1, 0},
            {1, 1, 0, 0, 0}
        };

        std::cout
            << "Shortest open-cell path: "
            << MatrixEngine::shortestPath(
                pathGrid,
                {0, 0},
                {3, 4}
            )
            << '\n';

        SparseMatrix sparse(1000, 1000);

        /*
         * A 1000 x 1000 dense matrix contains one million cells.
         * If only a few values are non-zero, storing every cell wastes
         * memory. The sparse representation stores only meaningful entries.
         */
        sparse.set(10, 20, 500);
        sparse.set(700, 800, 900);
        sparse.set(999, 999, 42);

        std::cout
            << "\nSparse non-zero values: "
            << sparse.nonZeroCount()
            << '\n';

        std::cout
            << "Sparse density: "
            << std::fixed
            << std::setprecision(6)
            << sparse.density()
            << '\n';

        GridAnalyticsSystem system({
            {1, 4, 7},
            {2, 5, 8},
            {3, 6, 9}
        });

        std::cout
            << "\nIndustry-style region query: "
            << system.queryRegion(0, 0, 1, 1)
            << '\n';

        runTests();

        std::cout
            << "\nCase study completed successfully.\n";

    } catch (const std::exception& exception) {
        std::cerr
            << "Fatal error: "
            << exception.what()
            << '\n';

        return 1;
    }

    return 0;
}
