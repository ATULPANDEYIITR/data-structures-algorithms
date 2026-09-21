#include <algorithm>
#include <cassert>
#include <cstdint>
#include <deque>
#include <exception>
#include <iomanip>
#include <iostream>
#include <limits>
#include <random>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

/*
 * Kadane's Algorithm Industry-Style Case Study
 *
 * Scenario:
 * A monitoring platform receives a chronological sequence of signed
 * measurements. Positive values represent beneficial impact and negative
 * values represent losses, penalties, outages, or resource consumption.
 *
 * The platform needs to answer questions such as:
 *
 * 1. What contiguous period produced the largest cumulative benefit?
 * 2. What period produced the largest cumulative loss?
 * 3. What if the timeline is circular?
 * 4. What if the period must contain exactly k observations?
 * 5. What if the period may contain at most k observations?
 * 6. What if one bad observation can be removed?
 * 7. How can the calculation operate on streaming data?
 *
 * The implementation demonstrates Kadane's algorithm and several
 * closely related techniques.
 *
 * Compile:
 *   g++ -std=c++17 -O2 -Wall -Wextra -pedantic kadane.cpp -o kadane
 */

using std::int64_t;
using std::size_t;
using std::string;
using std::vector;

constexpr int64_t NEGATIVE_INFINITY =
    std::numeric_limits<int64_t>::lowest() / 4;

struct SubarrayResult {
    int64_t sum{};
    size_t start{};
    size_t end{};

    size_t length() const {
        return end - start + 1;
    }
};

class MeasurementAnalyzer {
public:
    explicit MeasurementAnalyzer(vector<int64_t> values)
        : values_(std::move(values)) {
        if (values_.empty()) {
            throw std::invalid_argument(
                "Measurement sequence cannot be empty."
            );
        }
    }

    const vector<int64_t>& values() const {
        return values_;
    }

    // ---------------------------------------------------------------------
    // Ordinary Kadane with index recovery
    // ---------------------------------------------------------------------

    SubarrayResult maximumSubarray() const {
        int64_t bestEndingHere = values_[0];
        int64_t bestSoFar = values_[0];

        size_t currentStart = 0;
        size_t bestStart = 0;
        size_t bestEnd = 0;

        for (size_t i = 1; i < values_.size(); ++i) {
            const int64_t value = values_[i];

            if (value > bestEndingHere + value) {
                bestEndingHere = value;
                currentStart = i;
            } else {
                bestEndingHere += value;
            }

            if (bestEndingHere > bestSoFar) {
                bestSoFar = bestEndingHere;
                bestStart = currentStart;
                bestEnd = i;
            }
        }

        return {bestSoFar, bestStart, bestEnd};
    }

    // ---------------------------------------------------------------------
    // Minimum subarray
    // ---------------------------------------------------------------------

    SubarrayResult minimumSubarray() const {
        int64_t bestEndingHere = values_[0];
        int64_t bestSoFar = values_[0];

        size_t currentStart = 0;
        size_t bestStart = 0;
        size_t bestEnd = 0;

        for (size_t i = 1; i < values_.size(); ++i) {
            const int64_t value = values_[i];

            if (value < bestEndingHere + value) {
                bestEndingHere = value;
                currentStart = i;
            } else {
                bestEndingHere += value;
            }

            if (bestEndingHere < bestSoFar) {
                bestSoFar = bestEndingHere;
                bestStart = currentStart;
                bestEnd = i;
            }
        }

        return {bestSoFar, bestStart, bestEnd};
    }

    // ---------------------------------------------------------------------
    // Circular maximum
    // ---------------------------------------------------------------------

    int64_t maximumCircularSubarray() const {
        const SubarrayResult ordinary = maximumSubarray();

        // If all values are negative, total - minimum represents an empty
        // complement. The problem requires a non-empty subarray.
        if (ordinary.sum < 0) {
            return ordinary.sum;
        }

        const int64_t total = totalSum();
        const int64_t minimum = minimumSubarray().sum;

        return std::max(
            ordinary.sum,
            total - minimum
        );
    }

    // ---------------------------------------------------------------------
    // Circular minimum
    // ---------------------------------------------------------------------

    int64_t minimumCircularSubarray() const {
        const SubarrayResult ordinary = minimumSubarray();

        // For all-positive data, the complement of the maximum would be
        // empty, so return the ordinary minimum.
        if (ordinary.sum > 0) {
            return ordinary.sum;
        }

        const int64_t total = totalSum();
        const int64_t maximum = maximumSubarray().sum;

        return std::min(
            ordinary.sum,
            total - maximum
        );
    }

    // ---------------------------------------------------------------------
    // Fixed-length sliding window
    // ---------------------------------------------------------------------

    SubarrayResult maximumFixedLength(size_t k) const {
        validateK(k);

        int64_t windowSum = 0;

        for (size_t i = 0; i < k; ++i) {
            windowSum += values_[i];
        }

        int64_t bestSum = windowSum;
        size_t bestStart = 0;

        for (size_t right = k; right < values_.size(); ++right) {
            windowSum += values_[right];
            windowSum -= values_[right - k];

            const size_t start = right - k + 1;

            if (windowSum > bestSum) {
                bestSum = windowSum;
                bestStart = start;
            }
        }

        return {
            bestSum,
            bestStart,
            bestStart + k - 1
        };
    }

    // ---------------------------------------------------------------------
    // Maximum subarray with at most k elements
    // ---------------------------------------------------------------------

    int64_t maximumAtMostK(size_t k) const {
        validateK(k);

        /*
         * Let prefix[i] be the sum of values before index i.
         *
         * A subarray [left, right) has:
         *
         *     sum = prefix[right] - prefix[left]
         *
         * For length <= k:
         *
         *     right - left <= k
         *
         * We need the smallest eligible prefix[left].
         *
         * A monotonic deque stores candidate prefix indices.
         */
        vector<int64_t> prefix(values_.size() + 1, 0);

        for (size_t i = 0; i < values_.size(); ++i) {
            prefix[i + 1] = prefix[i] + values_[i];
        }

        std::deque<size_t> candidates;
        candidates.push_back(0);

        int64_t best = NEGATIVE_INFINITY;

        for (size_t right = 1; right < prefix.size(); ++right) {
            while (
                !candidates.empty() &&
                candidates.front() + k < right
            ) {
                candidates.pop_front();
            }

            best = std::max(
                best,
                prefix[right] - prefix[candidates.front()]
            );

            while (
                !candidates.empty() &&
                prefix[candidates.back()] >= prefix[right]
            ) {
                candidates.pop_back();
            }

            candidates.push_back(right);
        }

        return best;
    }

    // ---------------------------------------------------------------------
    // Maximum subarray with at least k elements
    // ---------------------------------------------------------------------

    int64_t maximumAtLeastK(size_t k) const {
        validateK(k);

        vector<int64_t> prefix(values_.size() + 1, 0);

        for (size_t i = 0; i < values_.size(); ++i) {
            prefix[i + 1] = prefix[i] + values_[i];
        }

        int64_t minimumEligiblePrefix = prefix[0];
        int64_t best = NEGATIVE_INFINITY;

        for (size_t right = k; right < prefix.size(); ++right) {
            minimumEligiblePrefix = std::min(
                minimumEligiblePrefix,
                prefix[right - k]
            );

            best = std::max(
                best,
                prefix[right] - minimumEligiblePrefix
            );
        }

        return best;
    }

    // ---------------------------------------------------------------------
    // Maximum sum with one deletion
    // ---------------------------------------------------------------------

    int64_t maximumWithOneDeletion() const {
        int64_t noDeletion = values_[0];
        int64_t oneDeletion = NEGATIVE_INFINITY;
        int64_t best = values_[0];

        for (size_t i = 1; i < values_.size(); ++i) {
            const int64_t value = values_[i];

            const int64_t previousNoDeletion = noDeletion;
            const int64_t previousOneDeletion = oneDeletion;

            noDeletion = std::max(
                value,
                previousNoDeletion + value
            );

            /*
             * There are three meaningful possibilities:
             *
             * 1. value becomes a new subarray after a deletion.
             * 2. A previous one-deletion state continues.
             * 3. Delete the current value, leaving previousNoDeletion.
             */
            oneDeletion = std::max({
                value,
                previousOneDeletion + value,
                previousNoDeletion
            });

            best = std::max({
                best,
                noDeletion,
                oneDeletion
            });
        }

        return best;
    }

    // ---------------------------------------------------------------------
    // Count subarrays whose sum equals a target
    // ---------------------------------------------------------------------

    int64_t countSubarraysWithSum(int64_t target) const {
        /*
         * prefix[r] - prefix[l] = target
         *
         * Therefore:
         *
         * prefix[l] = prefix[r] - target
         *
         * An unordered_map would be the conventional implementation.
         * For this self-contained standard-library case study, we use
         * std::map so that the implementation has deterministic ordering.
         */
        std::map<int64_t, int64_t> frequency;
        frequency[0] = 1;

        int64_t prefix = 0;
        int64_t count = 0;

        for (const int64_t value : values_) {
            prefix += value;

            auto found = frequency.find(prefix - target);

            if (found != frequency.end()) {
                count += found->second;
            }

            ++frequency[prefix];
        }

        return count;
    }

    int64_t totalSum() const {
        int64_t result = 0;

        for (const int64_t value : values_) {
            result += value;
        }

        return result;
    }

private:
    void validateK(size_t k) const {
        if (k == 0 || k > values_.size()) {
            throw std::invalid_argument(
                "k must satisfy 1 <= k <= number of measurements."
            );
        }
    }

    vector<int64_t> values_;
};

// ---------------------------------------------------------------------------
// Streaming implementation
// ---------------------------------------------------------------------------

class StreamingKadane {
public:
    void add(int64_t value) {
        if (!hasValue_) {
            bestEndingHere_ = value;
            bestSoFar_ = value;
            hasValue_ = true;
            return;
        }

        bestEndingHere_ = std::max(
            value,
            bestEndingHere_ + value
        );

        bestSoFar_ = std::max(
            bestSoFar_,
            bestEndingHere_
        );
    }

    int64_t result() const {
        if (!hasValue_) {
            throw std::logic_error(
                "Cannot request a result before receiving data."
            );
        }

        return bestSoFar_;
    }

private:
    bool hasValue_{false};
    int64_t bestEndingHere_{0};
    int64_t bestSoFar_{NEGATIVE_INFINITY};
};

// ---------------------------------------------------------------------------
// Reference implementation for testing
// ---------------------------------------------------------------------------

int64_t bruteForceMaximum(
    const vector<int64_t>& values
) {
    if (values.empty()) {
        throw std::invalid_argument(
            "Reference input cannot be empty."
        );
    }

    int64_t best = values[0];

    for (size_t start = 0; start < values.size(); ++start) {
        int64_t running = 0;

        for (size_t end = start; end < values.size(); ++end) {
            running += values[end];
            best = std::max(best, running);
        }
    }

    return best;
}

// ---------------------------------------------------------------------------
// Output helpers
// ---------------------------------------------------------------------------

void printVector(
    const vector<int64_t>& values
) {
    std::cout << "[";

    for (size_t i = 0; i < values.size(); ++i) {
        if (i > 0) {
            std::cout << ", ";
        }

        std::cout << values[i];
    }

    std::cout << "]";
}

void printResult(
    const string& name,
    const SubarrayResult& result,
    const vector<int64_t>& values
) {
    std::cout << name
              << ": sum=" << result.sum
              << ", range=[" << result.start
              << ", " << result.end
              << "], values=[";

    for (size_t i = result.start; i <= result.end; ++i) {
        if (i > result.start) {
            std::cout << ", ";
        }

        std::cout << values[i];
    }

    std::cout << "]\n";
}

// ---------------------------------------------------------------------------
// Demonstrations
// ---------------------------------------------------------------------------

void demonstrateBasicAnalysis() {
    const vector<int64_t> measurements{
        -2, 1, -3, 4, -1, 2, 1, -5, 4
    };

    MeasurementAnalyzer analyzer(measurements);

    std::cout << "\n=== Basic measurement analysis ===\n";
    std::cout << "Measurements: ";
    printVector(measurements);
    std::cout << "\n";

    printResult(
        "Maximum contiguous period",
        analyzer.maximumSubarray(),
        measurements
    );

    printResult(
        "Minimum contiguous period",
        analyzer.minimumSubarray(),
        measurements
    );

    std::cout
        << "Circular maximum: "
        << analyzer.maximumCircularSubarray()
        << "\n";

    std::cout
        << "Circular minimum: "
        << analyzer.minimumCircularSubarray()
        << "\n";
}

void demonstrateOperationalConstraints() {
    const vector<int64_t> measurements{
        4, -7, 5, 2, -1, 6, -8, 3, 4
    };

    MeasurementAnalyzer analyzer(measurements);

    std::cout << "\n=== Operational constraints ===\n";
    std::cout << "Measurements: ";
    printVector(measurements);
    std::cout << "\n";

    printResult(
        "Exactly 4 observations",
        analyzer.maximumFixedLength(4),
        measurements
    );

    std::cout
        << "At most 4 observations: "
        << analyzer.maximumAtMostK(4)
        << "\n";

    std::cout
        << "At least 4 observations: "
        << analyzer.maximumAtLeastK(4)
        << "\n";

    std::cout
        << "Maximum after deleting one observation: "
        << analyzer.maximumWithOneDeletion()
        << "\n";
}

void demonstrateTargetCounting() {
    const vector<int64_t> values{
        1, 2, 1, 2, 1
    };

    MeasurementAnalyzer analyzer(values);

    std::cout << "\n=== Prefix-sum target counting ===\n";
    std::cout << "Measurements: ";
    printVector(values);
    std::cout << "\n";

    std::cout
        << "Subarrays with sum 3: "
        << analyzer.countSubarraysWithSum(3)
        << "\n";
}

void demonstrateStreaming() {
    const vector<int64_t> values{
        -2, 1, -3, 4, -1, 2, 1, -5, 4
    };

    StreamingKadane tracker;

    std::cout << "\n=== Streaming Kadane ===\n";

    for (const int64_t value : values) {
        tracker.add(value);

        std::cout
            << "Received " << std::setw(3) << value
            << " -> best so far = "
            << tracker.result()
            << "\n";
    }
}

// ---------------------------------------------------------------------------
// Deterministic correctness tests
// ---------------------------------------------------------------------------

void runDeterministicTests() {
    {
        MeasurementAnalyzer analyzer({
            -2, 1, -3, 4, -1, 2, 1, -5, 4
        });

        assert(analyzer.maximumSubarray().sum == 6);
    }

    {
        MeasurementAnalyzer analyzer({
            -8, -3, -6, -2, -5
        });

        // The result must remain non-empty.
        assert(analyzer.maximumSubarray().sum == -2);
    }

    {
        MeasurementAnalyzer analyzer({
            5, -3, 5
        });

        assert(analyzer.maximumCircularSubarray() == 10);
    }

    {
        MeasurementAnalyzer analyzer({
            -3, -2, -1
        });

        assert(analyzer.maximumCircularSubarray() == -1);
    }

    {
        MeasurementAnalyzer analyzer({
            3, -4, 2, -1
        });

        assert(analyzer.minimumSubarray().sum == -4);
    }

    {
        MeasurementAnalyzer analyzer({
            1, -2, 0, 3
        });

        assert(analyzer.maximumWithOneDeletion() == 4);
    }

    {
        MeasurementAnalyzer analyzer({
            1, 1, 1
        });

        assert(analyzer.countSubarraysWithSum(2) == 2);
    }

    {
        MeasurementAnalyzer analyzer({
            1, 2, 3, -2, 5
        });

        assert(analyzer.maximumFixedLength(3).sum == 6);
    }

    std::cout
        << "\nDeterministic tests: PASSED\n";
}

// ---------------------------------------------------------------------------
// Randomized testing
// ---------------------------------------------------------------------------

void runRandomizedTests() {
    std::mt19937 generator(42);
    std::uniform_int_distribution<int> lengthDistribution(1, 10);
    std::uniform_int_distribution<int> valueDistribution(-10, 10);

    for (int test = 0; test < 2000; ++test) {
        const int length = lengthDistribution(generator);

        vector<int64_t> values;
        values.reserve(static_cast<size_t>(length));

        for (int i = 0; i < length; ++i) {
            values.push_back(valueDistribution(generator));
        }

        MeasurementAnalyzer analyzer(values);

        const int64_t expected =
            bruteForceMaximum(values);

        const int64_t actual =
            analyzer.maximumSubarray().sum;

        if (expected != actual) {
            std::cerr
                << "Randomized test failure.\n"
                << "Values: ";

            printVector(values);

            std::cerr
                << "\nExpected: " << expected
                << "\nActual: " << actual
                << "\n";

            throw std::runtime_error(
                "Kadane verification failed."
            );
        }
    }

    std::cout
        << "Randomized Kadane tests: PASSED\n";
}

// ---------------------------------------------------------------------------
// Error handling demonstration
// ---------------------------------------------------------------------------

void demonstrateValidation() {
    std::cout << "\n=== Validation ===\n";

    try {
        MeasurementAnalyzer analyzer({});
        (void)analyzer;
    } catch (const std::invalid_argument& error) {
        std::cout
            << "Rejected empty input: "
            << error.what()
            << "\n";
    }

    try {
        MeasurementAnalyzer analyzer({1, 2, 3});
        (void)analyzer.maximumFixedLength(0);
    } catch (const std::invalid_argument& error) {
        std::cout
            << "Rejected invalid k: "
            << error.what()
            << "\n";
    }

    try {
        StreamingKadane tracker;
        (void)tracker.result();
    } catch (const std::logic_error& error) {
        std::cout
            << "Rejected empty stream result: "
            << error.what()
            << "\n";
    }
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

int main() {
    try {
        demonstrateBasicAnalysis();
        demonstrateOperationalConstraints();
        demonstrateTargetCounting();
        demonstrateStreaming();

        runDeterministicTests();
        runRandomizedTests();

        demonstrateValidation();

        std::cout
            << "\nCase study completed successfully.\n";

        return 0;
    } catch (const std::exception& error) {
        std::cerr
            << "Fatal error: "
            << error.what()
            << "\n";

        return 1;
    }
}
