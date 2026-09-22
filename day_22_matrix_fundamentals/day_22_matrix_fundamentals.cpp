#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

/*
    Matrix Fundamentals: C++ Technical Case Study
    ===============================================

    Scenario:
    A small image-processing and geometric-transformation engine uses
    matrices to represent grayscale images, coordinates, transformations,
    and linear systems.

    The program progressively develops:
    1. A reusable Matrix class
    2. Matrix validation and indexing
    3. Arithmetic operations
    4. Matrix multiplication
    5. Transpose and special matrices
    6. Determinant
    7. Gaussian elimination and RREF
    8. Rank
    9. Matrix inverse
    10. Linear-system solving
    11. 2D transformations
    12. Sparse matrix representation
    13. Image-style filtering
    14. Performance and failure considerations

    Compile with:
        g++ -std=c++17 -O2 matrix_fundamentals.cpp -o matrix_fundamentals
*/

class Matrix {
private:
    std::size_t rows_;
    std::size_t columns_;
    std::vector<double> data_;

    std::size_t index(std::size_t row, std::size_t column) const {
        if (row >= rows_ || column >= columns_) {
            throw std::out_of_range("Matrix index is outside bounds.");
        }

        return row * columns_ + column;
    }

public:
    Matrix(std::size_t rows, std::size_t columns, double initialValue = 0.0)
        : rows_(rows),
          columns_(columns),
          data_(rows * columns, initialValue) {
        if (rows == 0 || columns == 0) {
            throw std::invalid_argument(
                "Matrix dimensions must be positive."
            );
        }
    }

    Matrix(std::initializer_list<std::initializer_list<double>> values) {
        if (values.size() == 0) {
            throw std::invalid_argument("Matrix cannot be empty.");
        }

        rows_ = values.size();
        columns_ = values.begin()->size();

        if (columns_ == 0) {
            throw std::invalid_argument("Matrix rows cannot be empty.");
        }

        data_.reserve(rows_ * columns_);

        for (const auto& row : values) {
            if (row.size() != columns_) {
                throw std::invalid_argument(
                    "Matrix must be rectangular."
                );
            }

            data_.insert(data_.end(), row.begin(), row.end());
        }
    }

    std::size_t rows() const {
        return rows_;
    }

    std::size_t columns() const {
        return columns_;
    }

    double& operator()(std::size_t row, std::size_t column) {
        return data_[index(row, column)];
    }

    double operator()(std::size_t row, std::size_t column) const {
        return data_[index(row, column)];
    }

    static Matrix identity(std::size_t size) {
        Matrix result(size, size);

        for (std::size_t i = 0; i < size; ++i) {
            result(i, i) = 1.0;
        }

        return result;
    }

    bool isSquare() const {
        return rows_ == columns_;
    }

    bool isApproximatelyEqual(
        const Matrix& other,
        double tolerance = 1e-9
    ) const {
        if (
            rows_ != other.rows_ ||
            columns_ != other.columns_
        ) {
            return false;
        }

        for (std::size_t i = 0; i < data_.size(); ++i) {
            if (
                std::abs(data_[i] - other.data_[i]) >
                tolerance
            ) {
                return false;
            }
        }

        return true;
    }

    Matrix transpose() const {
        Matrix result(columns_, rows_);

        for (std::size_t row = 0; row < rows_; ++row) {
            for (std::size_t column = 0; column < columns_; ++column) {
                result(column, row) = (*this)(row, column);
            }
        }

        return result;
    }

    bool isSymmetric(double tolerance = 1e-9) const {
        if (!isSquare()) {
            return false;
        }

        return isApproximatelyEqual(transpose(), tolerance);
    }

    double trace() const {
        if (!isSquare()) {
            throw std::invalid_argument(
                "Trace requires a square matrix."
            );
        }

        double result = 0.0;

        for (std::size_t i = 0; i < rows_; ++i) {
            result += (*this)(i, i);
        }

        return result;
    }

    Matrix minorMatrix(
        std::size_t excludedRow,
        std::size_t excludedColumn
    ) const {
        if (!isSquare()) {
            throw std::invalid_argument(
                "Minors require a square matrix."
            );
        }

        if (rows_ <= 1) {
            throw std::invalid_argument(
                "A 1x1 matrix does not have a conventional submatrix."
            );
        }

        Matrix result(rows_ - 1, columns_ - 1);

        std::size_t targetRow = 0;

        for (std::size_t row = 0; row < rows_; ++row) {
            if (row == excludedRow) {
                continue;
            }

            std::size_t targetColumn = 0;

            for (std::size_t column = 0; column < columns_; ++column) {
                if (column == excludedColumn) {
                    continue;
                }

                result(targetRow, targetColumn) =
                    (*this)(row, column);

                ++targetColumn;
            }

            ++targetRow;
        }

        return result;
    }

    double determinantRecursive() const {
        if (!isSquare()) {
            throw std::invalid_argument(
                "Determinant requires a square matrix."
            );
        }

        if (rows_ == 1) {
            return (*this)(0, 0);
        }

        if (rows_ == 2) {
            return
                (*this)(0, 0) * (*this)(1, 1) -
                (*this)(0, 1) * (*this)(1, 0);
        }

        double determinant = 0.0;

        for (std::size_t column = 0; column < columns_; ++column) {
            const double sign =
                column % 2 == 0 ? 1.0 : -1.0;

            determinant +=
                sign *
                (*this)(0, column) *
                minorMatrix(0, column).determinantRecursive();
        }

        return determinant;
    }

    Matrix rref(double tolerance = 1e-10) const {
        Matrix result = *this;

        std::size_t pivotRow = 0;

        for (
            std::size_t pivotColumn = 0;
            pivotColumn < columns_ && pivotRow < rows_;
            ++pivotColumn
        ) {
            std::size_t bestRow = pivotRow;

            for (
                std::size_t row = pivotRow + 1;
                row < rows_;
                ++row
            ) {
                if (
                    std::abs(result(row, pivotColumn)) >
                    std::abs(result(bestRow, pivotColumn))
                ) {
                    bestRow = row;
                }
            }

            if (
                std::abs(result(bestRow, pivotColumn)) <=
                tolerance
            ) {
                continue;
            }

            for (std::size_t column = 0; column < columns_; ++column) {
                std::swap(
                    result(pivotRow, column),
                    result(bestRow, column)
                );
            }

            const double pivot =
                result(pivotRow, pivotColumn);

            for (
                std::size_t column = 0;
                column < columns_;
                ++column
            ) {
                result(pivotRow, column) /= pivot;
            }

            for (std::size_t row = 0; row < rows_; ++row) {
                if (row == pivotRow) {
                    continue;
                }

                const double factor =
                    result(row, pivotColumn);

                for (
                    std::size_t column = 0;
                    column < columns_;
                    ++column
                ) {
                    result(row, column) -=
                        factor * result(pivotRow, column);
                }
            }

            ++pivotRow;
        }

        for (std::size_t row = 0; row < rows_; ++row) {
            for (std::size_t column = 0; column < columns_; ++column) {
                if (std::abs(result(row, column)) <= tolerance) {
                    result(row, column) = 0.0;
                }
            }
        }

        return result;
    }

    std::size_t rank(double tolerance = 1e-10) const {
        Matrix reduced = rref(tolerance);

        std::size_t rankValue = 0;

        for (std::size_t row = 0; row < reduced.rows_; ++row) {
            bool nonZero = false;

            for (
                std::size_t column = 0;
                column < reduced.columns_;
                ++column
            ) {
                if (
                    std::abs(reduced(row, column)) >
                    tolerance
                ) {
                    nonZero = true;
                    break;
                }
            }

            if (nonZero) {
                ++rankValue;
            }
        }

        return rankValue;
    }

    Matrix inverse(double tolerance = 1e-10) const {
        if (!isSquare()) {
            throw std::invalid_argument(
                "Inverse requires a square matrix."
            );
        }

        const std::size_t size = rows_;

        Matrix augmented(size, size * 2);

        for (std::size_t row = 0; row < size; ++row) {
            for (std::size_t column = 0; column < size; ++column) {
                augmented(row, column) =
                    (*this)(row, column);

                augmented(row, column + size) =
                    row == column ? 1.0 : 0.0;
            }
        }

        for (
            std::size_t pivotColumn = 0;
            pivotColumn < size;
            ++pivotColumn
        ) {
            std::size_t pivotRow = pivotColumn;

            for (
                std::size_t row = pivotColumn + 1;
                row < size;
                ++row
            ) {
                if (
                    std::abs(
                        augmented(row, pivotColumn)
                    ) >
                    std::abs(
                        augmented(pivotRow, pivotColumn)
                    )
                ) {
                    pivotRow = row;
                }
            }

            if (
                std::abs(
                    augmented(pivotRow, pivotColumn)
                ) <= tolerance
            ) {
                throw std::runtime_error(
                    "Matrix is singular or numerically singular."
                );
            }

            for (
                std::size_t column = 0;
                column < augmented.columns_;
                ++column
            ) {
                std::swap(
                    augmented(pivotColumn, column),
                    augmented(pivotRow, column)
                );
            }

            const double pivot =
                augmented(pivotColumn, pivotColumn);

            for (
                std::size_t column = 0;
                column < augmented.columns_;
                ++column
            ) {
                augmented(pivotColumn, column) /= pivot;
            }

            for (std::size_t row = 0; row < size; ++row) {
                if (row == pivotColumn) {
                    continue;
                }

                const double factor =
                    augmented(row, pivotColumn);

                for (
                    std::size_t column = 0;
                    column < augmented.columns_;
                    ++column
                ) {
                    augmented(row, column) -=
                        factor *
                        augmented(pivotColumn, column);
                }
            }
        }

        Matrix result(size, size);

        for (std::size_t row = 0; row < size; ++row) {
            for (std::size_t column = 0; column < size; ++column) {
                result(row, column) =
                    augmented(row, column + size);
            }
        }

        return result;
    }

    Matrix operator+(const Matrix& other) const {
        if (
            rows_ != other.rows_ ||
            columns_ != other.columns_
        ) {
            throw std::invalid_argument(
                "Matrix addition requires equal dimensions."
            );
        }

        Matrix result(rows_, columns_);

        for (std::size_t row = 0; row < rows_; ++row) {
            for (std::size_t column = 0; column < columns_; ++column) {
                result(row, column) =
                    (*this)(row, column) +
                    other(row, column);
            }
        }

        return result;
    }

    Matrix operator-(const Matrix& other) const {
        if (
            rows_ != other.rows_ ||
            columns_ != other.columns_
        ) {
            throw std::invalid_argument(
                "Matrix subtraction requires equal dimensions."
            );
        }

        Matrix result(rows_, columns_);

        for (std::size_t row = 0; row < rows_; ++row) {
            for (std::size_t column = 0; column < columns_; ++column) {
                result(row, column) =
                    (*this)(row, column) -
                    other(row, column);
            }
        }

        return result;
    }

    Matrix operator*(const Matrix& other) const {
        if (columns_ != other.rows_) {
            throw std::invalid_argument(
                "Matrix multiplication requires A.columns == B.rows."
            );
        }

        Matrix result(rows_, other.columns_);

        for (std::size_t i = 0; i < rows_; ++i) {
            for (std::size_t j = 0; j < other.columns_; ++j) {
                double sum = 0.0;

                for (std::size_t k = 0; k < columns_; ++k) {
                    sum +=
                        (*this)(i, k) *
                        other(k, j);
                }

                result(i, j) = sum;
            }
        }

        return result;
    }

    Matrix operator*(double scalar) const {
        Matrix result(rows_, columns_);

        for (std::size_t row = 0; row < rows_; ++row) {
            for (std::size_t column = 0; column < columns_; ++column) {
                result(row, column) =
                    (*this)(row, column) * scalar;
            }
        }

        return result;
    }

    std::vector<double> multiplyVector(
        const std::vector<double>& vector
    ) const {
        if (vector.size() != columns_) {
            throw std::invalid_argument(
                "Vector size must equal matrix column count."
            );
        }

        std::vector<double> result(rows_, 0.0);

        for (std::size_t row = 0; row < rows_; ++row) {
            for (std::size_t column = 0; column < columns_; ++column) {
                result[row] +=
                    (*this)(row, column) *
                    vector[column];
            }
        }

        return result;
    }

    void print(const std::string& title = "") const {
        if (!title.empty()) {
            std::cout << "\n" << title << "\n";
        }

        std::cout << std::fixed << std::setprecision(4);

        for (std::size_t row = 0; row < rows_; ++row) {
            for (std::size_t column = 0; column < columns_; ++column) {
                std::cout
                    << std::setw(10)
                    << (*this)(row, column);
            }

            std::cout << '\n';
        }
    }
};


// -----------------------------------------------------------------------------
// Sparse matrix for large matrices containing mostly zeros
// -----------------------------------------------------------------------------

class SparseMatrix {
private:
    std::size_t rows_;
    std::size_t columns_;

    std::map<std::pair<std::size_t, std::size_t>, double> values_;

public:
    SparseMatrix(std::size_t rows, std::size_t columns)
        : rows_(rows), columns_(columns) {}

    void set(
        std::size_t row,
        std::size_t column,
        double value
    ) {
        if (row >= rows_ || column >= columns_) {
            throw std::out_of_range(
                "Sparse matrix coordinate is outside bounds."
            );
        }

        const auto key = std::make_pair(row, column);

        if (value == 0.0) {
            values_.erase(key);
        } else {
            values_[key] = value;
        }
    }

    double get(
        std::size_t row,
        std::size_t column
    ) const {
        if (row >= rows_ || column >= columns_) {
            throw std::out_of_range(
                "Sparse matrix coordinate is outside bounds."
            );
        }

        const auto iterator =
            values_.find({row, column});

        if (iterator == values_.end()) {
            return 0.0;
        }

        return iterator->second;
    }

    std::size_t nonZeroCount() const {
        return values_.size();
    }

    Matrix toDense() const {
        Matrix result(rows_, columns_);

        for (const auto& [coordinate, value] : values_) {
            result(coordinate.first, coordinate.second) = value;
        }

        return result;
    }

    void printStorage() const {
        std::cout << "\nSparse entries:\n";

        for (const auto& [coordinate, value] : values_) {
            std::cout
                << "("
                << coordinate.first
                << ", "
                << coordinate.second
                << ") = "
                << value
                << '\n';
        }
    }
};


// -----------------------------------------------------------------------------
// Matrix powers
// -----------------------------------------------------------------------------

Matrix matrixPower(Matrix base, unsigned int exponent) {
    if (!base.isSquare()) {
        throw std::invalid_argument(
            "Matrix powers require a square matrix."
        );
    }

    Matrix result = Matrix::identity(base.rows());

    while (exponent > 0) {
        if (exponent % 2 == 1) {
            result = result * base;
        }

        base = base * base;
        exponent /= 2;
    }

    return result;
}


// -----------------------------------------------------------------------------
// 2D geometric transformation
// -----------------------------------------------------------------------------

Matrix rotationMatrix(double degrees) {
    const double pi = std::acos(-1.0);
    const double radians = degrees * pi / 180.0;

    return Matrix{
        {std::cos(radians), -std::sin(radians)},
        {std::sin(radians), std::cos(radians)}
    };
}


// -----------------------------------------------------------------------------
// Image processing
// -----------------------------------------------------------------------------

Matrix thresholdImage(
    const Matrix& image,
    double threshold
) {
    Matrix result(image.rows(), image.columns());

    for (std::size_t row = 0; row < image.rows(); ++row) {
        for (
            std::size_t column = 0;
            column < image.columns();
            ++column
        ) {
            result(row, column) =
                image(row, column) >= threshold ? 1.0 : 0.0;
        }
    }

    return result;
}

Matrix blur3x3(const Matrix& image) {
    if (image.rows() < 3 || image.columns() < 3) {
        throw std::invalid_argument(
            "A 3x3 filter requires at least a 3x3 image."
        );
    }

    Matrix result = image;

    for (std::size_t row = 1; row + 1 < image.rows(); ++row) {
        for (
            std::size_t column = 1;
            column + 1 < image.columns();
            ++column
        ) {
            double sum = 0.0;

            for (
                std::size_t filterRow = row - 1;
                filterRow <= row + 1;
                ++filterRow
            ) {
                for (
                    std::size_t filterColumn = column - 1;
                    filterColumn <= column + 1;
                    ++filterColumn
                ) {
                    sum += image(filterRow, filterColumn);
                }
            }

            result(row, column) = sum / 9.0;
        }
    }

    return result;
}


// -----------------------------------------------------------------------------
// Linear-system case study
// -----------------------------------------------------------------------------

std::vector<double> solveTwoVariableSystem(
    const Matrix& coefficients,
    const std::vector<double>& constants
) {
    if (
        coefficients.rows() != 2 ||
        coefficients.columns() != 2 ||
        constants.size() != 2
    ) {
        throw std::invalid_argument(
            "This solver requires a 2x2 system."
        );
    }

    Matrix augmented{
        {
            coefficients(0, 0),
            coefficients(0, 1),
            constants[0]
        },
        {
            coefficients(1, 0),
            coefficients(1, 1),
            constants[1]
        }
    };

    Matrix reduced = augmented.rref();

    if (
        std::abs(reduced(0, 0)) < 1e-10 ||
        std::abs(reduced(1, 1)) < 1e-10
    ) {
        throw std::runtime_error(
            "System does not have a unique solution."
        );
    }

    return {
        reduced(0, 2),
        reduced(1, 2)
    };
}


// -----------------------------------------------------------------------------
// Main technical case study
// -----------------------------------------------------------------------------

int main() {
    try {
        std::cout
            << "============================================================\n"
            << "MATRIX FUNDAMENTALS: C++ TECHNICAL CASE STUDY\n"
            << "============================================================\n";

        // ---------------------------------------------------------------------
        // Stage 1: Representing a small grayscale image.
        // A grayscale image can be modeled as a matrix where each element
        // represents a pixel intensity.
        // ---------------------------------------------------------------------

        Matrix image{
            {10, 10, 10, 10, 10},
            {10, 50, 50, 50, 10},
            {10, 50, 100, 50, 10},
            {10, 50, 50, 50, 10},
            {10, 10, 10, 10, 10}
        };

        image.print("Original grayscale matrix");

        // ---------------------------------------------------------------------
        // Stage 2: Thresholding.
        // This is an element-wise matrix operation.
        // ---------------------------------------------------------------------

        Matrix binaryImage =
            thresholdImage(image, 50);

        binaryImage.print("Thresholded image");

        // ---------------------------------------------------------------------
        // Stage 3: Neighborhood processing.
        // A 3x3 averaging kernel computes each interior pixel from nine
        // neighboring matrix elements.
        // ---------------------------------------------------------------------

        Matrix blurred =
            blur3x3(image);

        blurred.print("Blurred image");

        // ---------------------------------------------------------------------
        // Stage 4: Matrix arithmetic.
        // ---------------------------------------------------------------------

        Matrix brightnessAdjustment{
            {5, 5, 5, 5, 5},
            {5, 5, 5, 5, 5},
            {5, 5, 5, 5, 5},
            {5, 5, 5, 5, 5},
            {5, 5, 5, 5, 5}
        };

        Matrix brighter =
            image + brightnessAdjustment;

        brighter.print("Brightness-adjusted image");

        // ---------------------------------------------------------------------
        // Stage 5: Geometric transformation.
        // A point represented as a column vector can be transformed by
        // multiplying it with a rotation matrix.
        // ---------------------------------------------------------------------

        Matrix rotation =
            rotationMatrix(90);

        std::vector<double> point{1.0, 0.0};

        std::vector<double> rotatedPoint =
            rotation.multiplyVector(point);

        rotation.print("90-degree rotation matrix");

        std::cout
            << "\nOriginal point: ("
            << point[0]
            << ", "
            << point[1]
            << ")\n";

        std::cout
            << "Rotated point: ("
            << rotatedPoint[0]
            << ", "
            << rotatedPoint[1]
            << ")\n";

        // ---------------------------------------------------------------------
        // Stage 6: Matrix multiplication.
        // This demonstrates composition of transformations.
        // ---------------------------------------------------------------------

        Matrix scale{
            {2, 0},
            {0, 2}
        };

        Matrix combinedTransformation =
            rotation * scale;

        combinedTransformation.print(
            "Combined rotation and scaling transformation"
        );

        // ---------------------------------------------------------------------
        // Stage 7: Determinant and invertibility.
        // A non-zero determinant indicates that a square matrix is invertible.
        // ---------------------------------------------------------------------

        Matrix calibration{
            {4, 7},
            {2, 6}
        };

        std::cout
            << "\nCalibration determinant: "
            << calibration.determinantRecursive()
            << '\n';

        Matrix calibrationInverse =
            calibration.inverse();

        calibrationInverse.print(
            "Calibration inverse"
        );

        Matrix identityCheck =
            calibration * calibrationInverse;

        identityCheck.print(
            "Calibration * inverse"
        );

        std::cout
            << "Inverse validation: "
            << (
                identityCheck.isApproximatelyEqual(
                    Matrix::identity(2)
                )
                    ? "PASS"
                    : "FAIL"
            )
            << '\n';

        // ---------------------------------------------------------------------
        // Stage 8: Rank and RREF.
        // ---------------------------------------------------------------------

        Matrix dependentSystem{
            {1, 2, 3},
            {2, 4, 6},
            {1, 1, 1}
        };

        Matrix reduced =
            dependentSystem.rref();

        reduced.print("RREF");

        std::cout
            << "Rank: "
            << dependentSystem.rank()
            << '\n';

        // ---------------------------------------------------------------------
        // Stage 9: Linear equations.
        //
        // 2x + y = 7
        // x - y = 1
        //
        // The coefficient matrix is:
        // [2  1]
        // [1 -1]
        //
        // The augmented matrix includes the constants as an extra column.
        // ---------------------------------------------------------------------

        Matrix coefficients{
            {2, 1},
            {1, -1}
        };

        std::vector<double> constants{
            7,
            1
        };

        std::vector<double> solution =
            solveTwoVariableSystem(
                coefficients,
                constants
            );

        std::cout
            << "\nLinear-system solution:\n"
            << "x = "
            << solution[0]
            << "\n"
            << "y = "
            << solution[1]
            << '\n';

        // ---------------------------------------------------------------------
        // Stage 10: Matrix powers.
        // The Fibonacci transformation matrix demonstrates how repeated
        // state transitions can be represented through matrix powers.
        // ---------------------------------------------------------------------

        Matrix fibonacci{
            {1, 1},
            {1, 0}
        };

        Matrix fibonacciPower =
            matrixPower(fibonacci, 10);

        fibonacciPower.print(
            "Fibonacci transformation matrix^10"
        );

        // ---------------------------------------------------------------------
        // Stage 11: Sparse representation.
        // Sparse matrices are useful when the majority of entries are zero.
        // ---------------------------------------------------------------------

        SparseMatrix sparseImage(1000, 1000);

        sparseImage.set(10, 20, 255);
        sparseImage.set(500, 700, 128);
        sparseImage.set(999, 999, 64);

        std::cout
            << "\nSparse matrix non-zero entries: "
            << sparseImage.nonZeroCount()
            << '\n';

        sparseImage.printStorage();

        // ---------------------------------------------------------------------
        // Stage 12: Demonstrate an important edge case.
        // ---------------------------------------------------------------------

        Matrix singular{
            {1, 2},
            {2, 4}
        };

        std::cout
            << "\nSingular matrix determinant: "
            << singular.determinantRecursive()
            << '\n';

        try {
            Matrix impossibleInverse =
                singular.inverse();

            impossibleInverse.print(
                "This should not be reached"
            );
        } catch (const std::exception& error) {
            std::cout
                << "Expected inverse failure: "
                << error.what()
                << '\n';
        }

        // ---------------------------------------------------------------------
        // Performance notes.
        // ---------------------------------------------------------------------

        std::cout
            << "\nPerformance considerations:\n"
            << "- Dense element-wise operations are O(m*n).\n"
            << "- Naive multiplication is O(m*n*p).\n"
            << "- Gaussian elimination is approximately O(n^3).\n"
            << "- Dense storage requires O(m*n) memory.\n"
            << "- Sparse storage depends on the number of non-zero entries.\n"
            << "- Contiguous row-major storage improves cache locality.\n"
            << "- Partial pivoting improves numerical robustness.\n";

        std::cout
            << "\nCase study completed successfully.\n";
    }
    catch (const std::exception& error) {
        std::cerr
            << "Fatal error: "
            << error.what()
            << '\n';

        return 1;
    }

    return 0;
}
