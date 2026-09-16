/*
    Prefix Sum: Industry-Style Telemetry Analytics Case Study

    Scenario
    --------
    A monitoring service receives a sequence of integer measurements from
    infrastructure sensors. Analysts repeatedly request statistics over
    time intervals, while an administrative component occasionally changes
    individual measurements.

    The implementation begins with direct scanning, evolves to immutable
    prefix sums for high-volume read workloads, then uses a Fenwick tree
    when point updates and range queries must coexist.

    Standard: C++17
*/

#include <algorithm>
#include <cassert>
#include <chrono>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <optional>
#include <random>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>


// ---------------------------------------------------------------------------
// Domain model
// ---------------------------------------------------------------------------

struct SensorReading {
    std::string sensor_id;
    std::vector<std::int64_t> measurements;
};


// ---------------------------------------------------------------------------
// Validation utilities
// ---------------------------------------------------------------------------

void validate_range(
    std::size_t size,
    std::size_t left,
    std::size_t right
) {
    if (size == 0 || left > right || right >= size) {
        throw std::out_of_range("Invalid inclusive range");
    }
}


// ---------------------------------------------------------------------------
// Direct implementation
// ---------------------------------------------------------------------------

class DirectRangeCalculator {
public:
    explicit DirectRangeCalculator(
        const std::vector<std::int64_t>& values
    )
        : values_(values) {}

    std::int64_t range_sum(
        std::size_t left,
        std::size_t right
    ) const {
        validate_range(values_.size(), left, right);

        std::int64_t result = 0;

        for (std::size_t index = left; index <= right; ++index) {
            result += values_[index];
        }

        return result;
    }

private:
    const std::vector<std::int64_t>& values_;
};


// ---------------------------------------------------------------------------
// Immutable prefix-sum implementation
// ---------------------------------------------------------------------------

class PrefixSumArray {
public:
    explicit PrefixSumArray(
        const std::vector<std::int64_t>& values
    ) {
        prefix_.resize(values.size() + 1, 0);

        for (std::size_t index = 0; index < values.size(); ++index) {
            prefix_[index + 1] =
                prefix_[index] + values[index];
        }
    }

    std::int64_t range_sum(
        std::size_t left,
        std::size_t right
    ) const {
        const std::size_t value_count = prefix_.size() - 1;

        validate_range(value_count, left, right);

        return prefix_[right + 1] - prefix_[left];
    }

    std::int64_t total_sum() const {
        return prefix_.back();
    }

    std::size_t size() const {
        return prefix_.size() - 1;
    }

private:
    std::vector<std::int64_t> prefix_;
};


// ---------------------------------------------------------------------------
// Extended prefix statistics
// ---------------------------------------------------------------------------

class PrefixStatistics {
public:
    explicit PrefixStatistics(
        const std::vector<std::int64_t>& values
    ) {
        count_.resize(values.size() + 1, 0);
        sum_.resize(values.size() + 1, 0);
        squares_.resize(values.size() + 1, 0);

        for (std::size_t index = 0; index < values.size(); ++index) {
            const auto value = values[index];

            count_[index + 1] = count_[index] + 1;
            sum_[index + 1] = sum_[index] + value;

            // This assumes the application has chosen an integer range
            // where squaring is safe. Production systems should define
            // explicit overflow policy based on domain limits.
            squares_[index + 1] =
                squares_[index] + value * value;
        }
    }

    std::int64_t sum(
        std::size_t left,
        std::size_t right
    ) const {
        validate_range(count_.size() - 1, left, right);
        return sum_[right + 1] - sum_[left];
    }

    std::size_t count(
        std::size_t left,
        std::size_t right
    ) const {
        validate_range(count_.size() - 1, left, right);
        return static_cast<std::size_t>(
            count_[right + 1] - count_[left]
        );
    }

    double mean(
        std::size_t left,
        std::size_t right
    ) const {
        return static_cast<double>(sum(left, right)) /
               static_cast<double>(count(left, right));
    }

    double variance(
        std::size_t left,
        std::size_t right
    ) const {
        const auto n = static_cast<double>(count(left, right));
        const auto total = static_cast<double>(sum(left, right));
        const auto square_total = static_cast<double>(
            squares_[right + 1] - squares_[left]
        );

        const double average = total / n;

        // Population variance:
        // E[X^2] - E[X]^2
        return square_total / n - average * average;
    }

private:
    std::vector<std::int64_t> count_;
    std::vector<std::int64_t> sum_;
    std::vector<std::int64_t> squares_;
};


// ---------------------------------------------------------------------------
// Two-dimensional prefix sums
// ---------------------------------------------------------------------------

class MatrixPrefixSum {
public:
    explicit MatrixPrefixSum(
        const std::vector<std::vector<std::int64_t>>& matrix
    ) {
        if (matrix.empty()) {
            prefix_ = {{0}};
            return;
        }

        const std::size_t columns = matrix.front().size();

        for (const auto& row : matrix) {
            if (row.size() != columns) {
                throw std::invalid_argument(
                    "Matrix must be rectangular"
                );
            }
        }

        prefix_.assign(
            matrix.size() + 1,
            std::vector<std::int64_t>(columns + 1, 0)
        );

        for (std::size_t row = 0; row < matrix.size(); ++row) {
            for (std::size_t column = 0; column < columns; ++column) {
                prefix_[row + 1][column + 1] =
                    matrix[row][column]
                    + prefix_[row][column + 1]
                    + prefix_[row + 1][column]
                    - prefix_[row][column];
            }
        }
    }

    std::int64_t rectangle_sum(
        std::size_t top,
        std::size_t left,
        std::size_t bottom,
        std::size_t right
    ) const {
        if (
            top > bottom ||
            left > right ||
            bottom + 1 >= prefix_.size() ||
            right + 1 >= prefix_.front().size()
        ) {
            throw std::out_of_range("Invalid rectangle");
        }

        // Inclusion-exclusion:
        //
        // complete rectangle
        // - region above
        // - region left
        // + upper-left overlap
        return
            prefix_[bottom + 1][right + 1]
            - prefix_[top][right + 1]
            - prefix_[bottom + 1][left]
            + prefix_[top][left];
    }

private:
    std::vector<std::vector<std::int64_t>> prefix_;
};


// ---------------------------------------------------------------------------
// Difference array
// ---------------------------------------------------------------------------

class RangeUpdateAccumulator {
public:
    explicit RangeUpdateAccumulator(std::size_t size)
        : difference_(size + 1, 0) {}

    void add(
        std::size_t left,
        std::size_t right,
        std::int64_t amount
    ) {
        const std::size_t size = difference_.size() - 1;
        validate_range(size, left, right);

        difference_[left] += amount;
        difference_[right + 1] -= amount;
    }

    std::vector<std::int64_t> materialize() const {
        std::vector<std::int64_t> values(
            difference_.size() - 1
        );

        std::int64_t running = 0;

        for (std::size_t index = 0; index < values.size(); ++index) {
            running += difference_[index];
            values[index] = running;
        }

        return values;
    }

private:
    std::vector<std::int64_t> difference_;
};


// ---------------------------------------------------------------------------
// Fenwick tree for dynamic measurements
// ---------------------------------------------------------------------------

class FenwickTree {
public:
    explicit FenwickTree(
        const std::vector<std::int64_t>& values
    )
        : tree_(values.size() + 1, 0) {
        for (std::size_t index = 0; index < values.size(); ++index) {
            add(index + 1, values[index]);
        }
    }

    void add(
        std::size_t one_based_index,
        std::int64_t delta
    ) {
        if (
            one_based_index == 0 ||
            one_based_index >= tree_.size()
        ) {
            throw std::out_of_range(
                "Fenwick index out of range"
            );
        }

        std::size_t index = one_based_index;

        while (index < tree_.size()) {
            tree_[index] += delta;
            index += index & (~index + 1);
        }
    }

    std::int64_t prefix_sum(std::size_t count) const {
        if (count >= tree_.size()) {
            throw std::out_of_range(
                "Fenwick prefix length out of range"
            );
        }

        std::int64_t result = 0;
        std::size_t index = count;

        while (index > 0) {
            result += tree_[index];
            index &= index - 1;
        }

        return result;
    }

    std::int64_t range_sum(
        std::size_t left,
        std::size_t right
    ) const {
        const std::size_t size = tree_.size() - 1;
        validate_range(size, left, right);

        return prefix_sum(right + 1) - prefix_sum(left);
    }

private:
    std::vector<std::int64_t> tree_;
};


// ---------------------------------------------------------------------------
// Analytics service
// ---------------------------------------------------------------------------

class TelemetryAnalyticsService {
public:
    explicit TelemetryAnalyticsService(
        SensorReading reading
    )
        : reading_(std::move(reading)),
          prefix_(reading_.measurements),
          statistics_(reading_.measurements),
          dynamic_tree_(reading_.measurements) {}

    const std::string& sensor_id() const {
        return reading_.sensor_id;
    }

    std::int64_t interval_sum(
        std::size_t start,
        std::size_t end
    ) const {
        return prefix_.range_sum(start, end);
    }

    double interval_mean(
        std::size_t start,
        std::size_t end
    ) const {
        return statistics_.mean(start, end);
    }

    double interval_variance(
        std::size_t start,
        std::size_t end
    ) const {
        return statistics_.variance(start, end);
    }

    std::int64_t dynamic_interval_sum(
        std::size_t start,
        std::size_t end
    ) const {
        return dynamic_tree_.range_sum(start, end);
    }

    void update_measurement(
        std::size_t index,
        std::int64_t new_value
    ) {
        if (index >= reading_.measurements.size()) {
            throw std::out_of_range(
                "Measurement index out of range"
            );
        }

        const std::int64_t old_value =
            reading_.measurements[index];

        const std::int64_t delta = new_value - old_value;

        reading_.measurements[index] = new_value;

        // The immutable prefix and statistics structures represent the
        // original snapshot. The Fenwick tree is the dynamic structure.
        dynamic_tree_.add(index + 1, delta);
    }

private:
    SensorReading reading_;
    PrefixSumArray prefix_;
    PrefixStatistics statistics_;
    FenwickTree dynamic_tree_;
};


// ---------------------------------------------------------------------------
// Subarray analytics
// ---------------------------------------------------------------------------

std::size_t count_subarrays_with_sum(
    const std::vector<std::int64_t>& values,
    std::int64_t target
) {
    /*
        If:
            prefix[j] - prefix[i] = target

        then:
            prefix[i] = prefix[j] - target

        An unordered_map is commonly used for the frequency table.
    */

    // Included here through a local standard-library associative structure.
    std::unordered_map<std::int64_t, std::size_t> frequency;

    frequency[0] = 1;

    std::int64_t current = 0;
    std::size_t answer = 0;

    for (const auto value : values) {
        current += value;

        const auto found = frequency.find(current - target);

        if (found != frequency.end()) {
            answer += found->second;
        }

        ++frequency[current];
    }

    return answer;
}


// ---------------------------------------------------------------------------
// Brute-force validation for tests
// ---------------------------------------------------------------------------

std::int64_t brute_force_sum(
    const std::vector<std::int64_t>& values,
    std::size_t left,
    std::size_t right
) {
    validate_range(values.size(), left, right);

    return std::accumulate(
        values.begin() + static_cast<std::ptrdiff_t>(left),
        values.begin() + static_cast<std::ptrdiff_t>(right + 1),
        std::int64_t{0}
    );
}


// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

void run_tests() {
    const std::vector<std::int64_t> values{
        4, 2, 7, 1, 5, 3
    };

    PrefixSumArray prefix(values);

    for (std::size_t left = 0; left < values.size(); ++left) {
        for (
            std::size_t right = left;
            right < values.size();
            ++right
        ) {
            assert(
                prefix.range_sum(left, right)
                == brute_force_sum(values, left, right)
            );
        }
    }

    MatrixPrefixSum matrix({
        {1, 2, 3},
        {4, 5, 6},
        {7, 8, 9}
    });

    assert(matrix.rectangle_sum(1, 1, 2, 2) == 28);

    RangeUpdateAccumulator updates(6);

    updates.add(1, 3, 5);
    updates.add(2, 5, 2);
    updates.add(0, 1, 4);

    const auto result = updates.materialize();

    assert(
        result == std::vector<std::int64_t>{
            4, 9, 7, 7, 2, 2
        }
    );

    FenwickTree tree(values);

    assert(tree.range_sum(1, 4) == 18);

    tree.add(3, 5);

    assert(tree.range_sum(1, 4) == 23);

    assert(
        count_subarrays_with_sum(
            {1, 2, 1, 2, 1},
            3
        ) == 4
    );
}


// ---------------------------------------------------------------------------
// Demonstration
// ---------------------------------------------------------------------------

void print_vector(
    const std::vector<std::int64_t>& values
) {
    std::cout << "[";

    for (std::size_t index = 0; index < values.size(); ++index) {
        if (index != 0) {
            std::cout << ", ";
        }

        std::cout << values[index];
    }

    std::cout << "]";
}


int main() {
    try {
        run_tests();

        std::cout << "PREFIX SUM TELEMETRY CASE STUDY\n";
        std::cout << "================================\n\n";

        SensorReading reading{
            "SENSOR-ALPHA",
            {12, 15, 11, 20, 18, 14, 17, 21, 13, 16}
        };

        TelemetryAnalyticsService service(std::move(reading));

        std::cout << "Sensor: "
                  << service.sensor_id()
                  << "\n";

        std::cout << "Static interval sum [2, 7]: "
                  << service.interval_sum(2, 7)
                  << "\n";

        std::cout << "Static interval mean [2, 7]: "
                  << std::fixed
                  << std::setprecision(2)
                  << service.interval_mean(2, 7)
                  << "\n";

        std::cout << "Static interval variance [2, 7]: "
                  << service.interval_variance(2, 7)
                  << "\n";

        std::cout << "Dynamic interval sum [2, 7]: "
                  << service.dynamic_interval_sum(2, 7)
                  << "\n";

        /*
            An operational correction arrives for measurement index 4.

            Prefix sums are excellent for immutable data but do not make
            arbitrary point updates O(1). The Fenwick tree handles the
            corrected value without rebuilding the complete prefix array.
        */
        service.update_measurement(4, 25);

        std::cout << "After correcting index 4 to 25:\n";

        std::cout << "Dynamic interval sum [2, 7]: "
                  << service.dynamic_interval_sum(2, 7)
                  << "\n\n";

        MatrixPrefixSum regional_matrix({
            {10, 12, 15, 11},
            {14, 13, 18, 20},
            {16, 19, 17, 21},
            {12, 14, 22, 25}
        });

        std::cout << "Regional rectangle [1..3][1..2]: "
                  << regional_matrix.rectangle_sum(
                         1, 1, 3, 2
                     )
                  << "\n";

        RangeUpdateAccumulator maintenance_schedule(8);

        maintenance_schedule.add(1, 4, 3);
        maintenance_schedule.add(3, 6, 5);
        maintenance_schedule.add(0, 2, 2);

        std::cout << "Aggregated maintenance load: ";

        const auto schedule =
            maintenance_schedule.materialize();

        print_vector(schedule);

        std::cout << "\n";

        std::cout << "Subarrays summing to 20: "
                  << count_subarrays_with_sum(
                         {5, 15, 10, -5, 20, -10, 30},
                         20
                     )
                  << "\n";

        std::cout << "\nAll C++ correctness tests passed.\n";

        /*
            Complexity:
              Prefix construction: O(n)
              Static range query: O(1)
              Fenwick point update: O(log n)
              Fenwick range query: O(log n)
              2D prefix construction: O(rows * columns)
              2D rectangle query: O(1)
              Difference-array update: O(1)
              Difference-array materialization: O(n)

            Production considerations:
              - Establish whether signed overflow is possible.
              - Use suitable integer widths for the measurement domain.
              - Validate externally supplied indices.
              - Treat immutable snapshots and live data as separate concepts.
              - Avoid rebuilding large prefix arrays for every small update.
              - Benchmark using workload characteristics rather than isolated
                microbenchmarks.
        */

        return 0;
    }
    catch (const std::exception& error) {
        std::cerr << "Application error: "
                  << error.what()
                  << "\n";
        return 1;
    }
}
