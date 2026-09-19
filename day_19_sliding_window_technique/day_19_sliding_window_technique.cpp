#include <algorithm>
#include <cctype>
#include <deque>
#include <exception>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

using namespace std;

/*
 * Sliding Window Technique: C++17 Case Study
 *
 * Scenario:
 * A service-monitoring and analytics system receives a sequence of
 * measurements. The system must calculate rolling statistics, detect
 * stable periods, search text logs, and identify constrained intervals.
 *
 * The implementation begins with a simple fixed window and evolves into
 * reusable classes and monotonic-deque algorithms.
 *
 * Compile:
 *     g++ -std=c++17 -O2 sliding_window.cpp -o sliding_window
 */

// ---------------------------------------------------------------------------
// Utility functions
// ---------------------------------------------------------------------------

void requireValidWindow(const vector<int>& values, size_t k) {
    if (k == 0 || k > values.size()) {
        throw invalid_argument("window size must satisfy 1 <= k <= n");
    }
}

template <typename T>
void printVector(const vector<T>& values) {
    cout << "[";
    for (size_t i = 0; i < values.size(); ++i) {
        if (i > 0) {
            cout << ", ";
        }
        cout << values[i];
    }
    cout << "]";
}

// ---------------------------------------------------------------------------
// Phase 1: Basic fixed-size window
// ---------------------------------------------------------------------------

long long maximumSumFixedWindow(
    const vector<int>& values,
    size_t k
) {
    requireValidWindow(values, k);

    long long windowSum = 0;

    for (size_t i = 0; i < k; ++i) {
        windowSum += values[i];
    }

    long long best = windowSum;

    for (size_t right = k; right < values.size(); ++right) {
        windowSum += values[right];
        windowSum -= values[right - k];
        best = max(best, windowSum);
    }

    return best;
}

long long minimumSumFixedWindow(
    const vector<int>& values,
    size_t k
) {
    requireValidWindow(values, k);

    long long windowSum = 0;

    for (size_t i = 0; i < k; ++i) {
        windowSum += values[i];
    }

    long long best = windowSum;

    for (size_t right = k; right < values.size(); ++right) {
        windowSum += values[right];
        windowSum -= values[right - k];
        best = min(best, windowSum);
    }

    return best;
}

// ---------------------------------------------------------------------------
// Phase 2: Monotonic deque for window maximum
// ---------------------------------------------------------------------------

vector<int> maximumInEachWindow(
    const vector<int>& values,
    size_t k
) {
    requireValidWindow(values, k);

    deque<size_t> candidates;
    vector<int> result;
    result.reserve(values.size() - k + 1);

    for (size_t right = 0; right < values.size(); ++right) {
        // Remove indices outside the active window.
        while (!candidates.empty() &&
               candidates.front() + k <= right) {
            candidates.pop_front();
        }

        // Maintain decreasing values.
        while (!candidates.empty() &&
               values[candidates.back()] <= values[right]) {
            candidates.pop_back();
        }

        candidates.push_back(right);

        if (right + 1 >= k) {
            result.push_back(values[candidates.front()]);
        }
    }

    return result;
}

vector<int> minimumInEachWindow(
    const vector<int>& values,
    size_t k
) {
    requireValidWindow(values, k);

    deque<size_t> candidates;
    vector<int> result;
    result.reserve(values.size() - k + 1);

    for (size_t right = 0; right < values.size(); ++right) {
        while (!candidates.empty() &&
               candidates.front() + k <= right) {
            candidates.pop_front();
        }

        // Maintain increasing values.
        while (!candidates.empty() &&
               values[candidates.back()] >= values[right]) {
            candidates.pop_back();
        }

        candidates.push_back(right);

        if (right + 1 >= k) {
            result.push_back(values[candidates.front()]);
        }
    }

    return result;
}

// ---------------------------------------------------------------------------
// Phase 3: Minimum-length variable window
// ---------------------------------------------------------------------------

size_t minimumLengthAtLeastTarget(
    const vector<int>& values,
    long long target
) {
    if (target <= 0) {
        return 0;
    }

    // This algorithm requires non-negative values.
    size_t left = 0;
    long long sum = 0;
    size_t best = numeric_limits<size_t>::max();

    for (size_t right = 0; right < values.size(); ++right) {
        sum += values[right];

        while (sum >= target) {
            best = min(best, right - left + 1);
            sum -= values[left];
            ++left;
        }
    }

    return best == numeric_limits<size_t>::max() ? 0 : best;
}

// ---------------------------------------------------------------------------
// Phase 4: Frequency-based string windows
// ---------------------------------------------------------------------------

struct StringWindowResult {
    size_t length;
    string substring;
};

StringWindowResult longestUniqueSubstring(
    const string& text
) {
    /*
     * ASCII/byte-oriented implementation.
     *
     * For arbitrary Unicode text, production software should first decide
     * whether a "character" means byte, Unicode code point, or grapheme
     * cluster. std::string alone does not perform Unicode segmentation.
     */
    array<size_t, 256> lastSeen;
    lastSeen.fill(numeric_limits<size_t>::max());

    size_t left = 0;
    size_t bestStart = 0;
    size_t bestLength = 0;

    for (size_t right = 0; right < text.size(); ++right) {
        unsigned char character =
            static_cast<unsigned char>(text[right]);

        if (lastSeen[character] != numeric_limits<size_t>::max() &&
            lastSeen[character] >= left) {
            left = lastSeen[character] + 1;
        }

        lastSeen[character] = right;

        size_t length = right - left + 1;

        if (length > bestLength) {
            bestLength = length;
            bestStart = left;
        }
    }

    return {
        bestLength,
        text.substr(bestStart, bestLength)
    };
}

StringWindowResult longestSubstringAtMostKDistinct(
    const string& text,
    size_t k
) {
    if (k == 0 || text.empty()) {
        return {0, ""};
    }

    unordered_map<unsigned char, size_t> frequency;

    size_t left = 0;
    size_t bestStart = 0;
    size_t bestLength = 0;

    for (size_t right = 0; right < text.size(); ++right) {
        unsigned char current =
            static_cast<unsigned char>(text[right]);

        ++frequency[current];

        while (frequency.size() > k) {
            unsigned char outgoing =
                static_cast<unsigned char>(text[left]);

            auto iterator = frequency.find(outgoing);

            if (iterator != frequency.end()) {
                if (--iterator->second == 0) {
                    frequency.erase(iterator);
                }
            }

            ++left;
        }

        size_t length = right - left + 1;

        if (length > bestLength) {
            bestLength = length;
            bestStart = left;
        }
    }

    return {
        bestLength,
        text.substr(bestStart, bestLength)
    };
}

// ---------------------------------------------------------------------------
// Phase 5: Minimum window containing required characters
// ---------------------------------------------------------------------------

string minimumWindowSubstring(
    const string& text,
    const string& required
) {
    if (text.empty() || required.empty()) {
        return "";
    }

    array<int, 256> requiredCount{};
    array<int, 256> windowCount{};

    size_t requiredKinds = 0;

    for (unsigned char character : required) {
        if (requiredCount[character] == 0) {
            ++requiredKinds;
        }
        ++requiredCount[character];
    }

    size_t satisfiedKinds = 0;
    size_t left = 0;
    size_t bestStart = 0;
    size_t bestLength = numeric_limits<size_t>::max();

    for (size_t right = 0; right < text.size(); ++right) {
        unsigned char current =
            static_cast<unsigned char>(text[right]);

        ++windowCount[current];

        if (requiredCount[current] > 0 &&
            windowCount[current] == requiredCount[current]) {
            ++satisfiedKinds;
        }

        while (satisfiedKinds == requiredKinds) {
            size_t length = right - left + 1;

            if (length < bestLength) {
                bestLength = length;
                bestStart = left;
            }

            unsigned char outgoing =
                static_cast<unsigned char>(text[left]);

            --windowCount[outgoing];

            if (requiredCount[outgoing] > 0 &&
                windowCount[outgoing] < requiredCount[outgoing]) {
                --satisfiedKinds;
            }

            ++left;
        }
    }

    if (bestLength == numeric_limits<size_t>::max()) {
        return "";
    }

    return text.substr(bestStart, bestLength);
}

// ---------------------------------------------------------------------------
// Phase 6: Bounded-difference window
// ---------------------------------------------------------------------------

struct NumericWindowResult {
    size_t length;
    vector<int> values;
};

NumericWindowResult longestBoundedDifference(
    const vector<int>& values,
    int limit
) {
    if (limit < 0 || values.empty()) {
        return {0, {}};
    }

    deque<size_t> maximums;
    deque<size_t> minimums;

    size_t left = 0;
    size_t bestStart = 0;
    size_t bestLength = 0;

    for (size_t right = 0; right < values.size(); ++right) {
        while (!maximums.empty() &&
               values[maximums.back()] <= values[right]) {
            maximums.pop_back();
        }
        maximums.push_back(right);

        while (!minimums.empty() &&
               values[minimums.back()] >= values[right]) {
            minimums.pop_back();
        }
        minimums.push_back(right);

        while (
            !maximums.empty() &&
            !minimums.empty() &&
            values[maximums.front()] -
                values[minimums.front()] > limit
        ) {
            if (maximums.front() == left) {
                maximums.pop_front();
            }

            if (minimums.front() == left) {
                minimums.pop_front();
            }

            ++left;
        }

        size_t length = right - left + 1;

        if (length > bestLength) {
            bestLength = length;
            bestStart = left;
        }
    }

    vector<int> bestValues(
        values.begin() + static_cast<ptrdiff_t>(bestStart),
        values.begin() +
            static_cast<ptrdiff_t>(bestStart + bestLength)
    );

    return {bestLength, bestValues};
}

// ---------------------------------------------------------------------------
// Phase 7: Exactly K distinct subarrays
// ---------------------------------------------------------------------------

long long countSubarraysAtMostKDistinct(
    const vector<int>& values,
    int k
) {
    if (k < 0) {
        return 0;
    }

    unordered_map<int, int> frequency;

    size_t left = 0;
    long long result = 0;

    for (size_t right = 0; right < values.size(); ++right) {
        ++frequency[values[right]];

        while (static_cast<int>(frequency.size()) > k) {
            auto iterator = frequency.find(values[left]);

            if (iterator != frequency.end()) {
                if (--iterator->second == 0) {
                    frequency.erase(iterator);
                }
            }

            ++left;
        }

        // For this right endpoint, every start from left through right
        // is valid. Count = right - left + 1.
        result += static_cast<long long>(right - left + 1);
    }

    return result;
}

long long countSubarraysExactlyKDistinct(
    const vector<int>& values,
    int k
) {
    return countSubarraysAtMostKDistinct(values, k) -
           countSubarraysAtMostKDistinct(values, k - 1);
}

// ---------------------------------------------------------------------------
// Phase 8: Industry-style rolling monitoring component
// ---------------------------------------------------------------------------

class RollingLatencyMonitor {
private:
    size_t capacity_;
    double threshold_;
    deque<double> window_;
    double sum_ = 0.0;

public:
    RollingLatencyMonitor(
        size_t capacity,
        double threshold
    )
        : capacity_(capacity),
          threshold_(threshold) {
        if (capacity_ == 0) {
            throw invalid_argument("capacity must be positive");
        }

        if (!isfinite(threshold_)) {
            throw invalid_argument("threshold must be finite");
        }
    }

    struct Snapshot {
        size_t sampleCount;
        double average;
        double minimum;
        double maximum;
        bool thresholdExceeded;
    };

    void addMeasurement(double latencyMilliseconds) {
        if (!isfinite(latencyMilliseconds) ||
            latencyMilliseconds < 0.0) {
            throw invalid_argument(
                "latency must be a finite non-negative value"
            );
        }

        window_.push_back(latencyMilliseconds);
        sum_ += latencyMilliseconds;

        if (window_.size() > capacity_) {
            sum_ -= window_.front();
            window_.pop_front();
        }
    }

    Snapshot snapshot() const {
        if (window_.empty()) {
            return {0, 0.0, 0.0, 0.0, false};
        }

        auto [minimumIterator, maximumIterator] =
            minmax_element(window_.begin(), window_.end());

        double average = sum_ /
            static_cast<double>(window_.size());

        return {
            window_.size(),
            average,
            *minimumIterator,
            *maximumIterator,
            average > threshold_
        };
    }

    const deque<double>& currentWindow() const {
        return window_;
    }
};

// ---------------------------------------------------------------------------
// Testing
// ---------------------------------------------------------------------------

void runAssertions() {
    vector<int> numbers = {2, 1, 5, 1, 3, 2};

    if (maximumSumFixedWindow(numbers, 3) != 9) {
        throw runtime_error("maximumSumFixedWindow failed");
    }

    if (minimumSumFixedWindow(numbers, 3) != 6) {
        throw runtime_error("minimumSumFixedWindow failed");
    }

    vector<int> expectedMaximums = {3, 3, 5, 5, 6, 7};
    vector<int> testInput = {1, 3, -1, -3, 5, 3, 6, 7};

    if (maximumInEachWindow(testInput, 3) != expectedMaximums) {
        throw runtime_error("maximumInEachWindow failed");
    }

    vector<int> expectedMinimums = {-1, -3, -3, -3, 3, 3};

    if (minimumInEachWindow(testInput, 3) != expectedMinimums) {
        throw runtime_error("minimumInEachWindow failed");
    }

    if (minimumLengthAtLeastTarget(
            {2, 3, 1, 2, 4, 3}, 7) != 2) {
        throw runtime_error("minimumLengthAtLeastTarget failed");
    }

    auto unique = longestUniqueSubstring("abcabcbb");

    if (unique.length != 3 || unique.substring != "abc") {
        throw runtime_error("longestUniqueSubstring failed");
    }

    auto distinct =
        longestSubstringAtMostKDistinct("eceba", 2);

    if (distinct.length != 3) {
        throw runtime_error("longestSubstringAtMostKDistinct failed");
    }

    if (minimumWindowSubstring(
            "ADOBECODEBANC", "ABC") != "BANC") {
        throw runtime_error("minimumWindowSubstring failed");
    }

    if (countSubarraysExactlyKDistinct(
            {1, 2, 1, 2, 3}, 2) != 7) {
        throw runtime_error("countSubarraysExactlyKDistinct failed");
    }

    auto bounded =
        longestBoundedDifference({8, 2, 4, 7}, 4);

    if (bounded.length != 2 ||
        bounded.values != vector<int>({2, 4})) {
        throw runtime_error("longestBoundedDifference failed");
    }
}

// ---------------------------------------------------------------------------
// Main case study
// ---------------------------------------------------------------------------

int main() {
    try {
        cout << "=== SLIDING WINDOW C++ CASE STUDY ===\n\n";

        // A monitoring service receives measurements over time.
        // We want to detect the highest total load across any three
        // consecutive observations.
        vector<int> load = {12, 8, 15, 6, 10, 14, 9};

        cout << "Load measurements: ";
        printVector(load);
        cout << "\n";

        cout << "Maximum three-point load: "
             << maximumSumFixedWindow(load, 3)
             << "\n";

        cout << "Minimum three-point load: "
             << minimumSumFixedWindow(load, 3)
             << "\n\n";

        // The monotonic deque solves "maximum for every window" in O(n),
        // even though the maximum may change many times.
        vector<int> telemetry = {
            1, 3, -1, -3, 5, 3, 6, 7
        };

        cout << "Window maximums: ";
        printVector(maximumInEachWindow(telemetry, 3));
        cout << "\n";

        cout << "Window minimums: ";
        printVector(minimumInEachWindow(telemetry, 3));
        cout << "\n\n";

        // Variable-size window:
        // determine the shortest interval whose total load reaches 7.
        vector<int> positiveLoads = {
            2, 3, 1, 2, 4, 3
        };

        cout << "Minimum interval length with load >= 7: "
             << minimumLengthAtLeastTarget(positiveLoads, 7)
             << "\n\n";

        // Text logs can be processed with a frequency-based window.
        string logData = "abcabcbb";

        auto unique =
            longestUniqueSubstring(logData);

        cout << "Longest unique log fragment: "
             << unique.substring
             << " (length " << unique.length << ")\n";

        cout << "Minimum log fragment containing ABC: "
             << minimumWindowSubstring(
                    "ADOBECODEBANC", "ABC")
             << "\n\n";

        // Exactly-K-distinct is derived from two "at most K" calculations.
        vector<int> categories = {
            1, 2, 1, 2, 3
        };

        cout << "Subarrays with exactly two categories: "
             << countSubarraysExactlyKDistinct(
                    categories, 2)
             << "\n\n";

        // A stable telemetry interval may require max-min <= limit.
        auto stable =
            longestBoundedDifference({8, 2, 4, 7}, 4);

        cout << "Longest stable interval: ";
        printVector(stable.values);
        cout << " (length " << stable.length << ")\n\n";

        // Production-style rolling latency monitor.
        RollingLatencyMonitor monitor(4, 100.0);

        vector<double> latencies = {
            80.0, 120.0, 110.0, 90.0, 130.0, 70.0
        };

        cout << "=== ROLLING LATENCY MONITOR ===\n";

        for (double latency : latencies) {
            monitor.addMeasurement(latency);

            auto snapshot = monitor.snapshot();

            cout << fixed << setprecision(2)
                 << "Added " << latency
                 << " ms | samples=" << snapshot.sampleCount
                 << " | average=" << snapshot.average
                 << " ms | min=" << snapshot.minimum
                 << " ms | max=" << snapshot.maximum
                 << " ms | threshold="
                 << (snapshot.thresholdExceeded ? "EXCEEDED" : "OK")
                 << "\n";
        }

        // Demonstrate a controlled failure condition.
        try {
            maximumSumFixedWindow(load, 0);
        } catch (const invalid_argument& error) {
            cout << "\nExpected validation error: "
                 << error.what() << "\n";
        }

        runAssertions();

        cout << "\nAll C++ assertions passed.\n";

        cout << "\nComplexity characteristics:\n";
        cout << "Fixed-size rolling sum: O(n) time, O(1) auxiliary space.\n";
        cout << "Monotonic deque extrema: O(n) time, O(k) auxiliary space.\n";
        cout << "Frequency-map windows: O(n) average time, O(u) space.\n";
        cout << "Bounded max/min window: O(n) time, O(k) space.\n";

        return 0;
    } catch (const exception& error) {
        cerr << "Fatal error: " << error.what() << '\n';
        return 1;
    }
}
