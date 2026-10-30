#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <stdexcept>
#include <string>
#include <variant>
#include <vector>

using Clock = std::chrono::steady_clock;

enum class Algorithm {
    Counting,
    Radix,
    Bucket,
    Comparison
};

std::string algorithmName(Algorithm algorithm) {
    switch (algorithm) {
        case Algorithm::Counting:
            return "counting";
        case Algorithm::Radix:
            return "radix";
        case Algorithm::Bucket:
            return "bucket";
        case Algorithm::Comparison:
            return "comparison";
    }

    throw std::invalid_argument("Unknown sorting algorithm.");
}

struct SortMetrics {
    std::size_t inputSize;
    double elapsedMicroseconds;
    Algorithm algorithm;
};

template <typename T>
struct SortReport {
    std::vector<T> values;
    SortMetrics metrics;
};

class SortingError : public std::runtime_error {
public:
    explicit SortingError(const std::string& message)
        : std::runtime_error(message) {}
};

class RepositoryTelemetrySorter {
private:
    static constexpr std::size_t MAX_INPUT_SIZE = 2'000'000;
    static constexpr std::size_t MAX_COUNTING_RANGE = 1'000'000;
    static constexpr std::size_t MAX_BUCKET_COUNT = 10'000;

    static void validateSize(std::size_t size) {
        if (size > MAX_INPUT_SIZE) {
            throw SortingError("Input exceeds the configured size limit.");
        }
    }

    static std::vector<std::int64_t> countingSort(
        const std::vector<std::int64_t>& input
    ) {
        validateSize(input.size());

        if (input.empty()) {
            return {};
        }

        const auto [minimumIt, maximumIt] =
            std::minmax_element(input.begin(), input.end());

        const std::int64_t minimum = *minimumIt;
        const std::int64_t maximum = *maximumIt;

        // __int128 prevents signed overflow for extreme int64_t endpoints.
        const __int128 spanWide =
            static_cast<__int128>(maximum) -
            static_cast<__int128>(minimum) + 1;

        if (spanWide > static_cast<__int128>(MAX_COUNTING_RANGE)) {
            throw SortingError(
                "Counting sort range exceeds the configured memory limit."
            );
        }

        const std::size_t span = static_cast<std::size_t>(spanWide);
        std::vector<std::size_t> frequency(span, 0);

        for (const std::int64_t value : input) {
            const __int128 offset =
                static_cast<__int128>(value) -
                static_cast<__int128>(minimum);

            ++frequency[static_cast<std::size_t>(offset)];
        }

        std::vector<std::int64_t> output;
        output.reserve(input.size());

        for (std::size_t offset = 0; offset < span; ++offset) {
            for (std::size_t count = 0; count < frequency[offset]; ++count) {
                output.push_back(
                    static_cast<std::int64_t>(
                        static_cast<__int128>(minimum) + offset
                    )
                );
            }
        }

        return output;
    }

    static std::vector<std::int64_t> radixSort(
        const std::vector<std::int64_t>& input
    ) {
        validateSize(input.size());

        if (input.size() < 2) {
            return input;
        }

        /*
         * Flipping the sign bit maps signed int64_t order to unsigned
         * lexicographic key order. Eight byte passes cover all 64 bits,
         * including INT64_MIN and INT64_MAX.
         */
        constexpr std::uint64_t SIGN_MASK =
            std::uint64_t{1} << 63;

        std::vector<std::int64_t> output = input;
        std::vector<std::int64_t> temporary(input.size());

        for (unsigned pass = 0; pass < 8; ++pass) {
            std::array<std::size_t, 256> frequency{};
            const unsigned shift = pass * 8;

            for (const std::int64_t value : output) {
                const std::uint64_t key =
                    static_cast<std::uint64_t>(value) ^ SIGN_MASK;

                const std::size_t digit =
                    static_cast<std::size_t>((key >> shift) & 0xFFU);

                ++frequency[digit];
            }

            std::size_t total = 0;

            for (std::size_t digit = 0; digit < frequency.size(); ++digit) {
                total += frequency[digit];
                frequency[digit] = total;
            }

            // Reverse traversal preserves stability for each byte pass.
            for (std::size_t index = output.size(); index > 0; --index) {
                const std::int64_t value = output[index - 1];
                const std::uint64_t key =
                    static_cast<std::uint64_t>(value) ^ SIGN_MASK;

                const std::size_t digit =
                    static_cast<std::size_t>((key >> shift) & 0xFFU);

                const std::size_t destination = --frequency[digit];
                temporary[destination] = value;
            }

            output.swap(temporary);
        }

        return output;
    }

    static void insertionSort(std::vector<double>& bucket) {
        for (std::size_t index = 1; index < bucket.size(); ++index) {
            const double current = bucket[index];
            std::size_t position = index;

            while (
                position > 0 &&
                bucket[position - 1] > current
            ) {
                bucket[position] = bucket[position - 1];
                --position;
            }

            bucket[position] = current;
        }
    }

    static std::vector<double> bucketSort(
        const std::vector<double>& input
    ) {
        validateSize(input.size());

        for (const double value : input) {
            if (!std::isfinite(value)) {
                throw SortingError(
                    "Bucket sorting does not accept NaN or infinity."
                );
            }
        }

        if (input.size() < 2) {
            return input;
        }

        const auto [minimumIt, maximumIt] =
            std::minmax_element(input.begin(), input.end());

        const double minimum = *minimumIt;
        const double maximum = *maximumIt;

        if (minimum == maximum) {
            return input;
        }

        const std::size_t bucketCount = std::min(
            MAX_BUCKET_COUNT,
            std::max<std::size_t>(
                1,
                static_cast<std::size_t>(
                    std::ceil(std::sqrt(input.size()))
                )
            )
        );

        /*
         * long double gives additional range for subtraction between
         * finite double endpoints such as -DBL_MAX and DBL_MAX.
         */
        const long double low = static_cast<long double>(minimum);
        const long double high = static_cast<long double>(maximum);
        const long double span = high - low;

        std::vector<std::vector<double>> buckets(bucketCount);

        for (const double value : input) {
            const long double normalized =
                (static_cast<long double>(value) - low) / span;

            std::size_t index = static_cast<std::size_t>(
                normalized * static_cast<long double>(bucketCount)
            );

            if (index >= bucketCount) {
                index = bucketCount - 1;
            }

            buckets[index].push_back(value);
        }

        std::vector<double> output;
        output.reserve(input.size());

        for (auto& bucket : buckets) {
            insertionSort(bucket);
            output.insert(
                output.end(),
                bucket.begin(),
                bucket.end()
            );
        }

        return output;
    }

    static Algorithm chooseIntegerAlgorithm(
        const std::vector<std::int64_t>& input
    ) {
        if (input.empty()) {
            return Algorithm::Counting;
        }

        const auto [minimumIt, maximumIt] =
            std::minmax_element(input.begin(), input.end());

        const __int128 span =
            static_cast<__int128>(*maximumIt) -
            static_cast<__int128>(*minimumIt) + 1;

        const std::size_t relativeLimit = std::max<std::size_t>(
            256,
            input.size() * 16
        );

        if (
            span <= static_cast<__int128>(MAX_COUNTING_RANGE) &&
            span <= static_cast<__int128>(relativeLimit)
        ) {
            return Algorithm::Counting;
        }

        return Algorithm::Radix;
    }

    template <typename T>
    static void verifyResult(
        const std::vector<T>& original,
        const std::vector<T>& sorted
    ) {
        if (original.size() != sorted.size()) {
            throw SortingError("Sorting changed the input size.");
        }

        if (!std::is_sorted(sorted.begin(), sorted.end())) {
            throw SortingError("Result is not in non-decreasing order.");
        }

        /*
         * Verification uses a separate reference copy. This is suitable
         * for this technical demonstration, not a production hot path.
         */
        std::vector<T> reference = original;
        std::sort(reference.begin(), reference.end());

        if (reference != sorted) {
            throw SortingError("Sorting changed the input values.");
        }
    }

public:
    SortReport<std::int64_t> sortIntegers(
        const std::vector<std::int64_t>& input,
        Algorithm requested = Algorithm::Counting
    ) const {
        validateSize(input.size());

        Algorithm selected = requested;

        if (requested == Algorithm::Comparison) {
            std::vector<std::int64_t> output = input;

            const auto start = Clock::now();
            std::sort(output.begin(), output.end());
            const auto finish = Clock::now();

            verifyResult(input, output);

            const double elapsed =
                std::chrono::duration<double, std::micro>(
                    finish - start
                ).count();

            return {
                std::move(output),
                {input.size(), elapsed, Algorithm::Comparison}
            };
        }

        if (requested == Algorithm::Bucket) {
            throw SortingError(
                "Bucket sort is configured for decimal telemetry."
            );
        }

        if (requested == Algorithm::Counting && !input.empty()) {
            // Explicit counting requests still pass the allocation guard.
            selected = Algorithm::Counting;
        } else if (requested == Algorithm::Radix) {
            selected = Algorithm::Radix;
        } else if (requested == Algorithm::Counting && input.empty()) {
            selected = Algorithm::Counting;
        }

        const auto start = Clock::now();

        std::vector<std::int64_t> output =
            selected == Algorithm::Counting
                ? countingSort(input)
                : radixSort(input);

        const auto finish = Clock::now();

        verifyResult(input, output);

        const double elapsed =
            std::chrono::duration<double, std::micro>(
                finish - start
            ).count();

        return {
            std::move(output),
            {input.size(), elapsed, selected}
        };
    }

    SortReport<double> sortMeasurements(
        const std::vector<double>& input,
        Algorithm requested = Algorithm::Bucket
    ) const {
        validateSize(input.size());

        if (
            requested != Algorithm::Bucket &&
            requested != Algorithm::Comparison
        ) {
            throw SortingError(
                "Decimal measurements support bucket or comparison sorting."
            );
        }

        const auto start = Clock::now();

        std::vector<double> output;

        if (requested == Algorithm::Bucket) {
            output = bucketSort(input);
        } else {
            output = input;
            std::sort(output.begin(), output.end());
        }

        const auto finish = Clock::now();

        verifyResult(input, output);

        const double elapsed =
            std::chrono::duration<double, std::micro>(
                finish - start
            ).count();

        return {
            std::move(output),
            {input.size(), elapsed, requested}
        };
    }

    Algorithm recommend(
        const std::vector<std::int64_t>& input
    ) const {
        validateSize(input.size());
        return chooseIntegerAlgorithm(input);
    }
};

void printReport(const SortReport<std::int64_t>& report) {
    std::cout
        << std::left
        << std::setw(12) << algorithmName(report.metrics.algorithm)
        << " size=" << report.metrics.inputSize
        << " elapsed=" << std::fixed << std::setprecision(3)
        << report.metrics.elapsedMicroseconds << " us\n";

    std::cout << "  values: ";

    for (const auto value : report.values) {
        std::cout << value << ' ';
    }

    std::cout << '\n';
}

void printReport(const SortReport<double>& report) {
    std::cout
        << std::left
        << std::setw(12) << algorithmName(report.metrics.algorithm)
        << " size=" << report.metrics.inputSize
        << " elapsed=" << std::fixed << std::setprecision(3)
        << report.metrics.elapsedMicroseconds << " us\n";

    std::cout << "  values: ";

    for (const auto value : report.values) {
        std::cout << value << ' ';
    }

    std::cout << '\n';
}

int main() {
    try {
        RepositoryTelemetrySorter sorter;

        std::cout << "REPOSITORY TELEMETRY SORTING ENGINE\n\n";

        /*
         * Workload A: bounded sensor status codes.
         * A narrow integer range makes counting sort appropriate.
         */
        const std::vector<std::int64_t> statusCodes = {
            4, -2, 7, 4, 0, -2, 3, 1, 7, 5, 4
        };

        std::cout << "A. BOUNDED INTEGER SENSOR CODES\n";
        std::cout
            << "Recommended: "
            << algorithmName(sorter.recommend(statusCodes))
            << '\n';

        printReport(
            sorter.sortIntegers(statusCodes, Algorithm::Counting)
        );

        /*
         * Workload B: wide signed event identifiers.
         * The value range is too large for a safe counting-array allocation.
         */
        const std::vector<std::int64_t> eventIdentifiers = {
            std::numeric_limits<std::int64_t>::max(),
            0,
            std::numeric_limits<std::int64_t>::min(),
            42,
            -1,
            9'000'000'000LL
        };

        std::cout << "\nB. WIDE SIGNED EVENT IDENTIFIERS\n";
        std::cout
            << "Recommended: "
            << algorithmName(sorter.recommend(eventIdentifiers))
            << '\n';

        printReport(
            sorter.sortIntegers(eventIdentifiers, Algorithm::Radix)
        );

        /*
         * Workload C: floating-point latency measurements.
         * Bucket sorting benefits when values are reasonably distributed.
         */
        const std::vector<double> latencies = {
            0.42, 0.32, 0.23, 0.52, 0.25, 0.47, 0.51
        };

        std::cout << "\nC. LATENCY MEASUREMENTS\n";
        printReport(
            sorter.sortMeasurements(latencies, Algorithm::Bucket)
        );

        std::cout << "\nD. COMPARISON BASELINE\n";
        printReport(
            sorter.sortIntegers(statusCodes, Algorithm::Comparison)
        );
        printReport(
            sorter.sortMeasurements(latencies, Algorithm::Comparison)
        );

        std::cout << "\nE. EDGE CASES\n";

        const std::vector<std::int64_t> equalValues = {
            8, 8, 8, 8, 8
        };

        printReport(
            sorter.sortIntegers(equalValues, Algorithm::Radix)
        );

        const std::vector<double> extremeMeasurements = {
            -std::numeric_limits<double>::max(),
            0.0,
            std::numeric_limits<double>::max()
        };

        printReport(
            sorter.sortMeasurements(
                extremeMeasurements,
                Algorithm::Bucket
            )
        );

        std::cout << "\nF. VALIDATION FAILURE\n";

        try {
            sorter.sortIntegers(
                {0, 10'000'000},
                Algorithm::Counting
            );
        } catch (const SortingError& error) {
            std::cout << "Safely rejected: " << error.what() << '\n';
        }

        try {
            sorter.sortMeasurements(
                {1.0, std::numeric_limits<double>::quiet_NaN()},
                Algorithm::Bucket
            );
        } catch (const SortingError& error) {
            std::cout << "Safely rejected: " << error.what() << '\n';
        }

        std::cout << "\nALL SORTING CHECKS PASSED\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Fatal sorting error: " << error.what() << '\n';
        return 1;
    }
}
