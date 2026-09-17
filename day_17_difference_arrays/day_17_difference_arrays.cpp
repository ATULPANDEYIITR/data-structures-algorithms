/*
 * Difference Arrays: Industry-Style C++ Case Study
 *
 * Scenario:
 * ---------
 * A distributed infrastructure team needs to calculate server capacity
 * across a large sequence of deployment slots. Hundreds of planned capacity
 * changes affect contiguous ranges of slots.
 *
 * A naive solution modifies every slot for every change:
 *
 *     O(n * q) in the worst case
 *
 * A difference-array solution records only the two boundaries of each
 * inclusive range update:
 *
 *     difference[left]     += change
 *     difference[right+1] -= change
 *
 * and performs one prefix reconstruction:
 *
 *     O(q + n)
 *
 * This program develops the solution progressively and also demonstrates:
 * - validation
 * - classes and data structures
 * - 64-bit arithmetic
 * - batch range updates
 * - capacity constraints
 * - static range queries
 * - 2D capacity maps
 * - interval coverage
 * - coordinate compression
 * - randomized verification
 * - complexity and engineering trade-offs
 *
 * Compile:
 *     g++ -std=c++17 -O2 -Wall -Wextra -pedantic difference_arrays.cpp -o difference_arrays
 */

#include <algorithm>
#include <cassert>
#include <chrono>
#include <cstdint>
#include <exception>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <random>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

using namespace std;

using int64 = long long;


// ---------------------------------------------------------------------------
// 1. BASIC DIFFERENCE ARRAY
// ---------------------------------------------------------------------------

vector<int64> buildDifferenceArray(const vector<int64>& values) {
    if (values.empty()) {
        return {};
    }

    vector<int64> difference(values.size());
    difference[0] = values[0];

    for (size_t i = 1; i < values.size(); ++i) {
        difference[i] = values[i] - values[i - 1];
    }

    return difference;
}


vector<int64> reconstructFromDifference(
    const vector<int64>& difference
) {
    vector<int64> values(difference.size());

    int64 running = 0;

    for (size_t i = 0; i < difference.size(); ++i) {
        running += difference[i];
        values[i] = running;
    }

    return values;
}


// ---------------------------------------------------------------------------
// 2. RANGE UPDATE ENGINE
// ---------------------------------------------------------------------------

class RangeUpdateArray {
private:
    vector<int64> difference_;

public:
    explicit RangeUpdateArray(size_t size)
        : difference_(size + 1, 0) {}

    size_t size() const {
        return difference_.size() - 1;
    }

    void add(size_t left, size_t right, int64 amount) {
        if (left > right || right >= size()) {
            throw out_of_range("Invalid inclusive update range.");
        }

        difference_[left] += amount;
        difference_[right + 1] -= amount;
    }

    vector<int64> materialize() const {
        vector<int64> result(size());

        int64 running = 0;

        for (size_t i = 0; i < size(); ++i) {
            running += difference_[i];
            result[i] = running;
        }

        return result;
    }

    int64 pointValue(size_t index) const {
        if (index >= size()) {
            throw out_of_range("Point index is outside the array.");
        }

        int64 running = 0;

        for (size_t i = 0; i <= index; ++i) {
            running += difference_[i];
        }

        return running;
    }
};


// ---------------------------------------------------------------------------
// 3. INFRASTRUCTURE CAPACITY MODEL
// ---------------------------------------------------------------------------

struct CapacityChange {
    size_t startSlot;
    size_t endSlot;
    int64 delta;
};


class CapacityPlanner {
private:
    vector<int64> difference_;
    int64 baseCapacity_;

public:
    CapacityPlanner(size_t slotCount, int64 baseCapacity)
        : difference_(slotCount + 1, 0),
          baseCapacity_(baseCapacity) {
        if (baseCapacity < 0) {
            throw invalid_argument("Base capacity cannot be negative.");
        }
    }

    size_t slotCount() const {
        return difference_.size() - 1;
    }

    void schedule(const CapacityChange& change) {
        if (
            change.startSlot > change.endSlot ||
            change.endSlot >= slotCount()
        ) {
            throw out_of_range("Capacity change has an invalid slot range.");
        }

        /*
         * Only two boundary operations are necessary.
         *
         * The prefix sum will propagate delta through the entire range.
         */
        difference_[change.startSlot] += change.delta;
        difference_[change.endSlot + 1] -= change.delta;
    }

    vector<int64> capacityProfile() const {
        vector<int64> profile(slotCount());

        int64 runningChange = 0;

        for (size_t slot = 0; slot < slotCount(); ++slot) {
            runningChange += difference_[slot];
            profile[slot] = baseCapacity_ + runningChange;
        }

        return profile;
    }

    int64 minimumCapacity() const {
        const vector<int64> profile = capacityProfile();

        if (profile.empty()) {
            return 0;
        }

        return *min_element(profile.begin(), profile.end());
    }

    bool violatesMinimum(int64 requiredCapacity) const {
        return minimumCapacity() < requiredCapacity;
    }
};


// ---------------------------------------------------------------------------
// 4. STATIC RANGE-SUM INDEX
// ---------------------------------------------------------------------------

class StaticRangeSum {
private:
    vector<int64> prefix_;

public:
    explicit StaticRangeSum(const vector<int64>& values)
        : prefix_(values.size() + 1, 0) {
        for (size_t i = 0; i < values.size(); ++i) {
            prefix_[i + 1] = prefix_[i] + values[i];
        }
    }

    int64 query(size_t left, size_t right) const {
        if (
            left > right ||
            right + 1 >= prefix_.size()
        ) {
            throw out_of_range("Invalid range-sum query.");
        }

        return prefix_[right + 1] - prefix_[left];
    }
};


// ---------------------------------------------------------------------------
// 5. INTERVAL COVERAGE
// ---------------------------------------------------------------------------

vector<int> intervalCoverage(
    size_t maximumCoordinate,
    const vector<pair<size_t, size_t>>& intervals
) {
    vector<int> difference(maximumCoordinate + 2, 0);

    for (const auto& [left, right] : intervals) {
        if (
            left > right ||
            right > maximumCoordinate
        ) {
            throw out_of_range("Invalid interval.");
        }

        ++difference[left];
        --difference[right + 1];
    }

    vector<int> coverage(maximumCoordinate + 1);
    int active = 0;

    for (size_t coordinate = 0;
         coordinate <= maximumCoordinate;
         ++coordinate) {
        active += difference[coordinate];
        coverage[coordinate] = active;
    }

    return coverage;
}


// ---------------------------------------------------------------------------
// 6. TWO-DIMENSIONAL DIFFERENCE ARRAY
// ---------------------------------------------------------------------------

class GridDifferenceArray {
private:
    size_t rows_;
    size_t columns_;
    vector<vector<int64>> difference_;

public:
    GridDifferenceArray(size_t rows, size_t columns)
        : rows_(rows),
          columns_(columns),
          difference_(
              rows + 1,
              vector<int64>(columns + 1, 0)
          ) {}

    void addRectangle(
        size_t top,
        size_t left,
        size_t bottom,
        size_t right,
        int64 amount
    ) {
        if (
            top > bottom ||
            left > right ||
            bottom >= rows_ ||
            right >= columns_
        ) {
            throw out_of_range("Invalid rectangle.");
        }

        /*
         * Four corners implement two-dimensional inclusion-exclusion.
         */
        difference_[top][left] += amount;
        difference_[bottom + 1][left] -= amount;
        difference_[top][right + 1] -= amount;
        difference_[bottom + 1][right + 1] += amount;
    }

    vector<vector<int64>> materialize() const {
        vector<vector<int64>> result(
            rows_,
            vector<int64>(columns_, 0)
        );

        for (size_t row = 0; row < rows_; ++row) {
            for (size_t column = 0;
                 column < columns_;
                 ++column) {

                const int64 above =
                    row > 0 ? result[row - 1][column] : 0;

                const int64 left =
                    column > 0 ? result[row][column - 1] : 0;

                const int64 diagonal =
                    row > 0 && column > 0
                        ? result[row - 1][column - 1]
                        : 0;

                result[row][column] =
                    difference_[row][column] +
                    above +
                    left -
                    diagonal;
            }
        }

        return result;
    }
};


// ---------------------------------------------------------------------------
// 7. COORDINATE COMPRESSION
// ---------------------------------------------------------------------------

struct CompressedSegment {
    int64 start;
    int64 end;
    int64 value;
};


vector<CompressedSegment> compressedIntervals(
    const vector<tuple<int64, int64, int64>>& intervals
) {
    /*
     * Intervals are half-open:
     *
     *     [start, end)
     *
     * This convention is convenient for continuous coordinates because the
     * endpoint itself does not belong to the interval.
     */
    if (intervals.empty()) {
        return {};
    }

    vector<int64> coordinates;

    for (const auto& [start, end, value] : intervals) {
        if (start >= end) {
            throw invalid_argument(
                "Compressed intervals require start < end."
            );
        }

        coordinates.push_back(start);
        coordinates.push_back(end);
    }

    sort(coordinates.begin(), coordinates.end());
    coordinates.erase(
        unique(coordinates.begin(), coordinates.end()),
        coordinates.end()
    );

    map<int64, size_t> indexOf;

    for (size_t i = 0; i < coordinates.size(); ++i) {
        indexOf[coordinates[i]] = i;
    }

    vector<int64> difference(coordinates.size() + 1, 0);

    for (const auto& [start, end, value] : intervals) {
        difference[indexOf[start]] += value;
        difference[indexOf[end]] -= value;
    }

    vector<CompressedSegment> result;

    int64 running = 0;

    for (size_t i = 0; i + 1 < coordinates.size(); ++i) {
        running += difference[i];

        if (running != 0) {
            result.push_back({
                coordinates[i],
                coordinates[i + 1],
                running
            });
        }
    }

    return result;
}


// ---------------------------------------------------------------------------
// 8. NAIVE REFERENCE IMPLEMENTATION
// ---------------------------------------------------------------------------

vector<int64> naiveRangeUpdates(
    size_t n,
    const vector<CapacityChange>& changes
) {
    vector<int64> result(n, 0);

    for (const CapacityChange& change : changes) {
        if (
            change.startSlot > change.endSlot ||
            change.endSlot >= n
        ) {
            throw out_of_range("Invalid naive update.");
        }

        for (
            size_t slot = change.startSlot;
            slot <= change.endSlot;
            ++slot
        ) {
            result[slot] += change.delta;
        }
    }

    return result;
}


// ---------------------------------------------------------------------------
// 9. RANDOMIZED DIFFERENTIAL TESTING
// ---------------------------------------------------------------------------

void randomizedCorrectnessTest() {
    mt19937 generator(42);

    uniform_int_distribution<int> sizeDistribution(0, 40);
    uniform_int_distribution<int> updateDistribution(0, 50);
    uniform_int_distribution<int> amountDistribution(-50, 50);

    constexpr int testCases = 500;

    for (int test = 0; test < testCases; ++test) {
        const size_t n =
            static_cast<size_t>(sizeDistribution(generator));

        const int updateCount = updateDistribution(generator);

        vector<CapacityChange> changes;

        if (n > 0) {
            uniform_int_distribution<size_t> indexDistribution(
                0,
                n - 1
            );

            for (int i = 0; i < updateCount; ++i) {
                size_t left = indexDistribution(generator);
                size_t right = indexDistribution(generator);

                if (left > right) {
                    swap(left, right);
                }

                changes.push_back({
                    left,
                    right,
                    amountDistribution(generator)
                });
            }
        }

        CapacityPlanner optimized(n, 0);

        for (const auto& change : changes) {
            optimized.schedule(change);
        }

        const vector<int64> efficient =
            optimized.capacityProfile();

        const vector<int64> reference =
            naiveRangeUpdates(n, changes);

        if (efficient != reference) {
            throw runtime_error(
                "Randomized differential test failed."
            );
        }
    }

    cout << "Randomized correctness tests passed: "
         << testCases << '\n';
}


// ---------------------------------------------------------------------------
// 10. EDGE-CASE TESTS
// ---------------------------------------------------------------------------

void edgeCaseTests() {
    {
        CapacityPlanner planner(0, 100);
        assert(planner.capacityProfile().empty());
    }

    {
        CapacityPlanner planner(1, 10);
        planner.schedule({0, 0, 7});

        const auto result = planner.capacityProfile();

        assert(result == vector<int64>{17});
    }

    {
        CapacityPlanner planner(5, 100);
        planner.schedule({0, 4, 25});

        const auto result = planner.capacityProfile();

        assert(
            result ==
            vector<int64>{125, 125, 125, 125, 125}
        );
    }

    {
        CapacityPlanner planner(5, 100);
        planner.schedule({2, 2, -30});

        const auto result = planner.capacityProfile();

        assert(
            result ==
            vector<int64>{100, 100, 70, 100, 100}
        );
    }

    bool rejected = false;

    try {
        CapacityPlanner planner(5, 100);
        planner.schedule({3, 2, 10});
    }
    catch (const out_of_range&) {
        rejected = true;
    }

    assert(rejected);
}


// ---------------------------------------------------------------------------
// 11. 2D DEMONSTRATION
// ---------------------------------------------------------------------------

void printMatrix(const vector<vector<int64>>& matrix) {
    for (const auto& row : matrix) {
        for (int64 value : row) {
            cout << setw(5) << value;
        }
        cout << '\n';
    }
}


void twoDimensionalDemo() {
    GridDifferenceArray grid(4, 5);

    grid.addRectangle(0, 0, 1, 3, 5);
    grid.addRectangle(1, 2, 3, 4, 8);
    grid.addRectangle(2, 1, 2, 2, -3);

    const auto result = grid.materialize();

    cout << "\nTwo-dimensional difference array:\n";
    printMatrix(result);
}


// ---------------------------------------------------------------------------
// 12. COORDINATE-COMPRESSION DEMONSTRATION
// ---------------------------------------------------------------------------

void coordinateCompressionDemo() {
    /*
     * Coordinates reach one billion, but only a few boundaries matter.
     * Direct allocation of a billion-element array would be wasteful.
     */
    const vector<tuple<int64, int64, int64>> intervals = {
        {10, 1'000'000'000LL, 5},
        {500, 700, 3},
        {600, 900, -2}
    };

    const auto segments = compressedIntervals(intervals);

    cout << "\nCompressed segments:\n";

    for (const auto& segment : segments) {
        cout
            << '[' << segment.start
            << ", " << segment.end
            << ") -> " << segment.value
            << '\n';
    }
}


// ---------------------------------------------------------------------------
// 13. PERFORMANCE DEMONSTRATION
// ---------------------------------------------------------------------------

void performanceDemo() {
    constexpr size_t n = 500'000;
    constexpr size_t q = 100'000;

    mt19937 generator(123);

    uniform_int_distribution<size_t> indexDistribution(
        0,
        n - 1
    );

    uniform_int_distribution<int64> amountDistribution(
        -100,
        100
    );

    vector<CapacityChange> changes;
    changes.reserve(q);

    for (size_t i = 0; i < q; ++i) {
        size_t left = indexDistribution(generator);
        size_t right = indexDistribution(generator);

        if (left > right) {
            swap(left, right);
        }

        changes.push_back({
            left,
            right,
            amountDistribution(generator)
        });
    }

    const auto start =
        chrono::steady_clock::now();

    CapacityPlanner planner(n, 1000);

    for (const auto& change : changes) {
        planner.schedule(change);
    }

    const auto profile =
        planner.capacityProfile();

    const auto finish =
        chrono::steady_clock::now();

    const auto elapsed =
        chrono::duration_cast<chrono::microseconds>(
            finish - start
        ).count();

    cout << "\nPerformance demonstration:\n";
    cout << "Array size: " << n << '\n';
    cout << "Updates:    " << q << '\n';
    cout << "Time:       "
         << elapsed / 1000.0
         << " ms\n";

    /*
     * Keep the generated profile observable and prevent accidental removal
     * of all computation by an optimizing compiler.
     */
    if (profile.size() != n) {
        throw runtime_error("Unexpected profile size.");
    }
}


// ---------------------------------------------------------------------------
// 14. COMPLETE CASE STUDY
// ---------------------------------------------------------------------------

void infrastructureCaseStudy() {
    cout << "\nInfrastructure capacity case study\n";

    constexpr size_t slots = 12;
    constexpr int64 baseCapacity = 1'000;

    CapacityPlanner planner(slots, baseCapacity);

    /*
     * Business events:
     *
     * 1. Additional application traffic requires +250 units during slots
     *    2 through 7.
     *
     * 2. A scheduled marketing event requires +500 units during slots
     *    5 through 9.
     *
     * 3. A hardware maintenance window removes 300 units from slots
     *    6 through 6.
     */
    planner.schedule({2, 7, 250});
    planner.schedule({5, 9, 500});
    planner.schedule({6, 6, -300});

    const vector<int64> profile =
        planner.capacityProfile();

    cout << "Capacity by deployment slot:\n";

    for (size_t slot = 0; slot < profile.size(); ++slot) {
        cout
            << "Slot " << setw(2) << slot
            << ": " << profile[slot]
            << '\n';
    }

    const int64 minimum =
        planner.minimumCapacity();

    cout << "Minimum capacity: " << minimum << '\n';

    constexpr int64 safetyThreshold = 800;

    cout
        << "Safety threshold "
        << safetyThreshold
        << ": "
        << (planner.violatesMinimum(safetyThreshold)
            ? "violated"
            : "satisfied")
        << '\n';

    /*
     * Static range sums become possible after materialization. For example,
     * the sum of planned capacity across slots 4 through 8 can be obtained
     * in O(1) using a prefix-sum structure.
     */
    StaticRangeSum sumIndex(profile);

    cout
        << "Capacity sum [4, 8]: "
        << sumIndex.query(4, 8)
        << '\n';
}


// ---------------------------------------------------------------------------
// 15. EDUCATIONAL EXPLANATION PRINTED BY THE PROGRAM
// ---------------------------------------------------------------------------

void printTechnicalNotes() {
    cout << R"(
Technical notes
---------------

For an inclusive range [L, R] with addition X:

    D[L]     += X
    D[R + 1] -= X

The prefix sum of D reconstructs the actual values.

Complexity:

    q range updates       O(q)
    final reconstruction  O(n)
    total                 O(n + q)

A naive implementation can require O(nq).

A difference array is most appropriate when updates are known or processed
in a batch and the final state is needed.

It is not automatically the correct replacement for a Fenwick tree or
segment tree when updates and queries are dynamically interleaved.

For two-dimensional rectangles:

    D[top][left]           += X
    D[bottom+1][left]      -= X
    D[top][right+1]        -= X
    D[bottom+1][right+1]   += X

For very large sparse coordinates, coordinate compression avoids allocating
one element per coordinate.

Use fixed-width 64-bit integers for potentially large cumulative totals.
Even when each individual update fits into 32 bits, thousands of updates
may exceed a 32-bit result.
)";
}


// ---------------------------------------------------------------------------
// 16. MAIN
// ---------------------------------------------------------------------------

int main() {
    try {
        cout << string(72, '=') << '\n';
        cout << "DIFFERENCE ARRAYS: C++ CASE STUDY\n";
        cout << string(72, '=') << "\n\n";

        const vector<int64> values = {
            10, 13, 13, 20, 17
        };

        const auto difference =
            buildDifferenceArray(values);

        const auto reconstructed =
            reconstructFromDifference(difference);

        cout << "Original:      ";

        for (int64 value : values) {
            cout << value << ' ';
        }

        cout << "\nDifference:    ";

        for (int64 value : difference) {
            cout << value << ' ';
        }

        cout << "\nReconstructed: ";

        for (int64 value : reconstructed) {
            cout << value << ' ';
        }

        cout << '\n';

        assert(values == reconstructed);

        infrastructureCaseStudy();

        cout << "\nInterval coverage:\n";

        const auto coverage = intervalCoverage(
            7,
            {
                {1, 4},
                {2, 6},
                {4, 5}
            }
        );

        for (size_t coordinate = 0;
             coordinate < coverage.size();
             ++coordinate) {
            cout
                << coordinate
                << ": "
                << coverage[coordinate]
                << '\n';
        }

        twoDimensionalDemo();
        coordinateCompressionDemo();
        edgeCaseTests();
        randomizedCorrectnessTest();
        performanceDemo();
        printTechnicalNotes();

        cout << "\nAll C++ demonstrations completed successfully.\n";
    }
    catch (const exception& error) {
        cerr
            << "Program failed: "
            << error.what()
            << '\n';

        return 1;
    }

    return 0;
}
