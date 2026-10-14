#include <algorithm>
#include <cassert>
#include <cstddef>
#include <deque>
#include <iomanip>
#include <iostream>
#include <limits>
#include <random>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

/*
 * Repository telemetry case study: a high-throughput monitoring service
 * computes rolling minimum and maximum values for incoming measurements.
 *
 * The same monotonic-deque technique used for sliding-window extrema is
 * useful when each measurement represents latency, memory usage, queue
 * depth, or a sensor reading.
 *
 * Compile:
 *   g++ -std=c++17 -O2 -Wall -Wextra -pedantic deque_case_study.cpp -o deque_case_study
 */

struct Measurement {
    std::size_t sequence;
    double value;
};

struct WindowExtrema {
    std::size_t first_sequence;
    std::size_t last_sequence;
    double minimum;
    double maximum;
};

class SlidingExtremaEngine {
public:
    explicit SlidingExtremaEngine(std::size_t window_size)
        : window_size_(window_size) {
        if (window_size_ == 0) {
            throw std::invalid_argument("Window size must be positive.");
        }
    }

    WindowExtrema push(double value) {
        if (!std::isfinite(value)) {
            throw std::invalid_argument(
                "Measurements must be finite numbers."
            );
        }

        const std::size_t current = next_sequence_++;

        // Expired candidates leave from the front. Sequence numbers make
        // expiration independent of duplicate measurement values.
        while (!minimum_candidates_.empty() &&
               minimum_candidates_.front().sequence + window_size_ <= current) {
            minimum_candidates_.pop_front();
        }

        while (!maximum_candidates_.empty() &&
               maximum_candidates_.front().sequence + window_size_ <= current) {
            maximum_candidates_.pop_front();
        }

        // Remove dominated candidates. A newer smaller value dominates
        // older larger values for minimum queries.
        while (!minimum_candidates_.empty() &&
               minimum_candidates_.back().value >= value) {
            minimum_candidates_.pop_back();
        }

        // A newer larger value dominates older smaller values for maximum
        // queries. Equal values are removed because the newer one expires
        // later and provides the same extremum.
        while (!maximum_candidates_.empty() &&
               maximum_candidates_.back().value <= value) {
            maximum_candidates_.pop_back();
        }

        const Measurement measurement{current, value};
        minimum_candidates_.push_back(measurement);
        maximum_candidates_.push_back(measurement);

        if (next_sequence_ < window_size_) {
            throw std::logic_error("The window is not complete yet.");
        }

        return WindowExtrema{
            current - window_size_ + 1,
            current,
            minimum_candidates_.front().value,
            maximum_candidates_.front().value
        };
    }

    std::size_t window_size() const noexcept {
        return window_size_;
    }

private:
    std::size_t window_size_;
    std::size_t next_sequence_ = 0;
    std::deque<Measurement> minimum_candidates_;
    std::deque<Measurement> maximum_candidates_;
};

class TelemetryService {
public:
    explicit TelemetryService(std::size_t window_size)
        : engine_(window_size) {}

    void process(const std::vector<double>& readings) {
        for (double reading : readings) {
            // The service waits until a complete window exists rather than
            // reporting extrema over a partially filled interval.
            if (processed_ >= engine_.window_size() - 1) {
                const WindowExtrema result = engine_.push(reading);
                display(result);
            } else {
                engine_.push(reading);
            }
            ++processed_;
        }
    }

private:
    SlidingExtremaEngine engine_;
    std::size_t processed_ = 0;

    static void display(const WindowExtrema& result) {
        std::cout << "Window [" << result.first_sequence << ", "
                  << result.last_sequence << "]"
                  << " min=" << result.minimum
                  << " max=" << result.maximum << '\n';
    }
};

std::vector<double> brute_force_minimum(
    const std::vector<double>& values,
    std::size_t window_size
) {
    if (window_size == 0 || window_size > values.size()) {
        throw std::invalid_argument("Invalid window size.");
    }

    std::vector<double> result;

    for (std::size_t start = 0;
         start + window_size <= values.size();
         ++start) {
        result.push_back(*std::min_element(
            values.begin() + static_cast<std::ptrdiff_t>(start),
            values.begin() + static_cast<std::ptrdiff_t>(
                start + window_size
            )
        ));
    }

    return result;
}

std::vector<double> brute_force_maximum(
    const std::vector<double>& values,
    std::size_t window_size
) {
    if (window_size == 0 || window_size > values.size()) {
        throw std::invalid_argument("Invalid window size.");
    }

    std::vector<double> result;

    for (std::size_t start = 0;
         start + window_size <= values.size();
         ++start) {
        result.push_back(*std::max_element(
            values.begin() + static_cast<std::ptrdiff_t>(start),
            values.begin() + static_cast<std::ptrdiff_t>(
                start + window_size
            )
        ));
    }

    return result;
}

std::pair<std::vector<double>, std::vector<double>> optimized_extrema(
    const std::vector<double>& values,
    std::size_t window_size
) {
    if (window_size == 0 || window_size > values.size()) {
        throw std::invalid_argument("Invalid window size.");
    }

    for (double value : values) {
        if (!std::isfinite(value)) {
            throw std::invalid_argument("Values must be finite.");
        }
    }

    std::deque<std::size_t> minima;
    std::deque<std::size_t> maxima;
    std::vector<double> minimum_result;
    std::vector<double> maximum_result;

    for (std::size_t index = 0; index < values.size(); ++index) {
        while (!minima.empty() && minima.front() + window_size <= index) {
            minima.pop_front();
        }

        while (!maxima.empty() && maxima.front() + window_size <= index) {
            maxima.pop_front();
        }

        while (!minima.empty() && values[minima.back()] >= values[index]) {
            minima.pop_back();
        }

        while (!maxima.empty() && values[maxima.back()] <= values[index]) {
            maxima.pop_back();
        }

        minima.push_back(index);
        maxima.push_back(index);

        if (index + 1 >= window_size) {
            minimum_result.push_back(values[minima.front()]);
            maximum_result.push_back(values[maxima.front()]);
        }
    }

    return {minimum_result, maximum_result};
}

void run_correctness_checks() {
    const std::vector<std::vector<double>> test_cases{
        {1.0},
        {4.0, 4.0, 4.0, 4.0},
        {-8.0, -3.0, -9.0, -1.0},
        {1.0, 9.0, 2.0, 8.0, 3.0, 7.0},
        {0.0, -1.0, 0.0, -1.0, 0.0}
    };

    std::size_t comparisons = 0;

    for (const auto& values : test_cases) {
        for (std::size_t k = 1; k <= values.size(); ++k) {
            const auto actual = optimized_extrema(values, k);
            assert(actual.first == brute_force_minimum(values, k));
            assert(actual.second == brute_force_maximum(values, k));
            ++comparisons;
        }
    }

    bool rejected = false;
    try {
        SlidingExtremaEngine invalid(0);
    } catch (const std::invalid_argument&) {
        rejected = true;
    }
    assert(rejected);

    rejected = false;
    try {
        SlidingExtremaEngine engine(1);
        engine.push(std::numeric_limits<double>::quiet_NaN());
    } catch (const std::invalid_argument&) {
        rejected = true;
    }
    assert(rejected);

    std::cout << "Correctness comparisons passed: "
              << comparisons << '\n';
}

int main() {
    try {
        std::cout << std::fixed << std::setprecision(2);

        std::cout << "=== Telemetry window analysis ===\n";

        const std::vector<double> latency_ms{
            18.2, 19.1, 17.4, 20.6, 21.3, 16.8, 18.9, 23.1
        };

        TelemetryService service(3);
        service.process(latency_ms);

        std::cout << "\n=== Offline verification ===\n";

        const std::vector<double> readings{
            1.0, 3.0, -1.0, -3.0, 5.0, 3.0, 6.0, 7.0
        };

        const auto extrema = optimized_extrema(readings, 3);

        std::cout << "Minimums: ";
        for (double value : extrema.first) {
            std::cout << value << ' ';
        }

        std::cout << "\nMaximums: ";
        for (double value : extrema.second) {
            std::cout << value << ' ';
        }
        std::cout << '\n';

        run_correctness_checks();

        std::cout
            << "\nComplexity: O(n) total processing time, O(k) auxiliary "
               "space for window size k.\n"
            << "Each index enters and leaves each candidate deque at most "
               "once.\n";
    } catch (const std::exception& error) {
        std::cerr << "Processing failed: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
