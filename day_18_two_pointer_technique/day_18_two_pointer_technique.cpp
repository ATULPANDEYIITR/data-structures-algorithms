/*
 * Two Pointer Technique: Industry-Style Order Analytics Case Study
 *
 * C++17
 *
 * Scenario
 * --------
 * A market surveillance service receives a sorted stream of transaction
 * prices and needs to answer several analytical questions:
 *
 * - Find two prices that satisfy a target relationship.
 * - Remove duplicate price levels.
 * - Partition prices around a threshold.
 * - Detect suspicious three-price combinations.
 * - Merge independently sorted market feeds.
 * - Calculate maximum spread opportunity.
 * - Maintain a sliding window over recent observations.
 * - Detect cycles in a linked structure used by a legacy feed component.
 *
 * The implementation deliberately develops the system progressively.
 *
 * Compile:
 *   g++ -std=c++17 -O2 -Wall -Wextra -pedantic two_pointer_case_study.cpp -o two_pointer_case_study
 *
 * Run:
 *   ./two_pointer_case_study
 */

#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstddef>
#include <exception>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

using std::size_t;

// ============================================================================
// Utility Functions
// ============================================================================

template <typename T>
void printVector(const std::vector<T>& values) {
    std::cout << "[";
    for (size_t index = 0; index < values.size(); ++index) {
        if (index > 0) {
            std::cout << ", ";
        }
        std::cout << values[index];
    }
    std::cout << "]";
}

// ============================================================================
// Domain Model
// ============================================================================

struct Trade {
    long long tradeId;
    double price;
    int quantity;
    std::string symbol;

    double notional() const {
        return price * static_cast<double>(quantity);
    }
};

struct PriceLevel {
    double price;
    int quantity;
};

// ============================================================================
// Basic Two-Pointer Algorithms
// ============================================================================

void reverseInPlace(std::vector<int>& values) {
    size_t left = 0;
    size_t right = values.empty() ? 0 : values.size() - 1;

    if (values.empty()) {
        return;
    }

    while (left < right) {
        std::swap(values[left], values[right]);
        ++left;
        --right;
    }
}

bool twoSumSorted(
    const std::vector<int>& values,
    int target,
    size_t& firstIndex,
    size_t& secondIndex
) {
    if (values.size() < 2) {
        return false;
    }

    size_t left = 0;
    size_t right = values.size() - 1;

    while (left < right) {
        const long long sum =
            static_cast<long long>(values[left]) +
            static_cast<long long>(values[right]);

        if (sum == target) {
            firstIndex = left;
            secondIndex = right;
            return true;
        }

        if (sum < target) {
            ++left;
        } else {
            --right;
        }
    }

    return false;
}

std::vector<int> removeDuplicatesSorted(std::vector<int>& values) {
    if (values.empty()) {
        return {};
    }

    size_t slow = 1;

    for (size_t fast = 1; fast < values.size(); ++fast) {
        if (values[fast] != values[slow - 1]) {
            values[slow] = values[fast];
            ++slow;
        }
    }

    values.resize(slow);
    return values;
}

// ============================================================================
// Partitioning
// ============================================================================

size_t partitionByPivot(std::vector<int>& values, int pivot) {
    if (values.empty()) {
        return 0;
    }

    size_t left = 0;
    size_t right = values.size() - 1;

    while (left <= right) {
        while (left <= right && values[left] < pivot) {
            ++left;
        }

        while (left <= right && values[right] >= pivot) {
            if (right == 0) {
                break;
            }
            --right;
        }

        if (left <= right) {
            std::swap(values[left], values[right]);
            ++left;

            if (right == 0) {
                break;
            }

            --right;
        }
    }

    return left;
}

void dutchNationalFlag(std::vector<int>& values) {
    if (values.empty()) {
        return;
    }

    size_t low = 0;
    size_t middle = 0;
    size_t high = values.size() - 1;

    while (middle <= high) {
        if (values[middle] == 0) {
            std::swap(values[low], values[middle]);
            ++low;
            ++middle;
        } else if (values[middle] == 1) {
            ++middle;
        } else if (values[middle] == 2) {
            std::swap(values[middle], values[high]);

            if (high == 0) {
                break;
            }

            --high;
        } else {
            throw std::invalid_argument(
                "Dutch National Flag requires values 0, 1, or 2."
            );
        }
    }
}

// ============================================================================
// Three-Sum Analytics
// ============================================================================

std::vector<std::array<int, 3>> threeSum(
    std::vector<int> values,
    int target
) {
    std::sort(values.begin(), values.end());

    std::vector<std::array<int, 3>> results;

    for (size_t first = 0; first + 2 < values.size(); ++first) {
        if (first > 0 && values[first] == values[first - 1]) {
            continue;
        }

        size_t left = first + 1;
        size_t right = values.size() - 1;

        while (left < right) {
            const long long sum =
                static_cast<long long>(values[first]) +
                values[left] +
                values[right];

            if (sum == target) {
                results.push_back({
                    values[first],
                    values[left],
                    values[right]
                });

                const int leftValue = values[left];
                const int rightValue = values[right];

                while (left < right && values[left] == leftValue) {
                    ++left;
                }

                while (left < right && values[right] == rightValue) {
                    --right;
                }
            } else if (sum < target) {
                ++left;
            } else {
                --right;
            }
        }
    }

    return results;
}

// ============================================================================
// Merge Sorted Market Feeds
// ============================================================================

std::vector<Trade> mergeSortedTrades(
    const std::vector<Trade>& first,
    const std::vector<Trade>& second
) {
    std::vector<Trade> merged;
    merged.reserve(first.size() + second.size());

    size_t left = 0;
    size_t right = 0;

    auto comparator = [](const Trade& a, const Trade& b) {
        if (a.price != b.price) {
            return a.price < b.price;
        }
        return a.tradeId < b.tradeId;
    };

    while (left < first.size() && right < second.size()) {
        if (comparator(first[left], second[right]) ||
            (!comparator(second[right], first[left]) &&
             first[left].tradeId <= second[right].tradeId)) {
            merged.push_back(first[left]);
            ++left;
        } else {
            merged.push_back(second[right]);
            ++right;
        }
    }

    while (left < first.size()) {
        merged.push_back(first[left]);
        ++left;
    }

    while (right < second.size()) {
        merged.push_back(second[right]);
        ++right;
    }

    return merged;
}

// ============================================================================
// Market Spread Analysis
// ============================================================================

class SpreadAnalyzer {
public:
    /*
     * Given buy and sell observations already sorted by price, identify the
     * largest positive spread between a sell-side maximum and an earlier
     * compatible buy-side minimum.
     *
     * This is deliberately modeled as a two-pointer scan rather than a
     * brute-force comparison of every pair.
     */
    static std::optional<std::pair<double, double>> bestSpread(
        const std::vector<double>& buyPrices,
        const std::vector<double>& sellPrices
    ) {
        if (buyPrices.empty() || sellPrices.empty()) {
            return std::nullopt;
        }

        size_t buy = 0;
        size_t sell = 0;

        double bestBuy = 0.0;
        double bestSell = 0.0;
        double bestSpread = -std::numeric_limits<double>::infinity();

        while (buy < buyPrices.size() && sell < sellPrices.size()) {
            if (buyPrices[buy] <= sellPrices[sell]) {
                const double spread = sellPrices[sell] - buyPrices[buy];

                if (spread > bestSpread) {
                    bestSpread = spread;
                    bestBuy = buyPrices[buy];
                    bestSell = sellPrices[sell];
                }

                ++sell;
            } else {
                ++buy;
            }
        }

        if (!std::isfinite(bestSpread)) {
            return std::nullopt;
        }

        return std::make_pair(bestBuy, bestSell);
    }
};

// ============================================================================
// Sliding Window Risk Check
// ============================================================================

class RollingRiskMonitor {
private:
    std::size_t windowSize_;
    std::vector<double> observations_;

public:
    explicit RollingRiskMonitor(std::size_t windowSize)
        : windowSize_(windowSize) {
        if (windowSize_ == 0) {
            throw std::invalid_argument(
                "Window size must be greater than zero."
            );
        }
    }

    void add(double observation) {
        observations_.push_back(observation);

        if (observations_.size() > windowSize_) {
            observations_.erase(observations_.begin());
        }
    }

    std::optional<double> average() const {
        if (observations_.empty()) {
            return std::nullopt;
        }

        double sum = 0.0;

        for (double value : observations_) {
            sum += value;
        }

        return sum / static_cast<double>(observations_.size());
    }

    std::optional<double> maximumAbsoluteChange() const {
        if (observations_.size() < 2) {
            return std::nullopt;
        }

        double maximum = 0.0;

        for (size_t left = 0; left + 1 < observations_.size(); ++left) {
            maximum = std::max(
                maximum,
                std::abs(observations_[left + 1] - observations_[left])
            );
        }

        return maximum;
    }
};

// ============================================================================
// Linked-List Feed Cycle Detection
// ============================================================================

class FeedNode {
public:
    int sequence;
    FeedNode* next;

    explicit FeedNode(int sequenceNumber)
        : sequence(sequenceNumber), next(nullptr) {}
};

bool hasCycle(FeedNode* head) {
    FeedNode* slow = head;
    FeedNode* fast = head;

    while (fast != nullptr && fast->next != nullptr) {
        slow = slow->next;
        fast = fast->next->next;

        if (slow == fast) {
            return true;
        }
    }

    return false;
}

FeedNode* findCycleStart(FeedNode* head) {
    FeedNode* slow = head;
    FeedNode* fast = head;

    while (fast != nullptr && fast->next != nullptr) {
        slow = slow->next;
        fast = fast->next->next;

        if (slow == fast) {
            FeedNode* pointer = head;

            while (pointer != slow) {
                pointer = pointer->next;
                slow = slow->next;
            }

            return pointer;
        }
    }

    return nullptr;
}

// ============================================================================
// Transaction Surveillance System
// ============================================================================

class TransactionSurveillance {
private:
    std::vector<Trade> trades_;

public:
    void addTrade(const Trade& trade) {
        if (trade.tradeId <= 0) {
            throw std::invalid_argument("Trade ID must be positive.");
        }

        if (!std::isfinite(trade.price) || trade.price < 0.0) {
            throw std::invalid_argument("Trade price must be finite and non-negative.");
        }

        if (trade.quantity <= 0) {
            throw std::invalid_argument("Trade quantity must be positive.");
        }

        if (trade.symbol.empty()) {
            throw std::invalid_argument("Trade symbol cannot be empty.");
        }

        trades_.push_back(trade);
    }

    std::vector<double> sortedPrices() const {
        std::vector<double> prices;
        prices.reserve(trades_.size());

        for (const Trade& trade : trades_) {
            prices.push_back(trade.price);
        }

        std::sort(prices.begin(), prices.end());
        return prices;
    }

    std::vector<double> uniquePriceLevels() const {
        std::vector<double> prices = sortedPrices();

        if (prices.empty()) {
            return {};
        }

        size_t slow = 1;

        for (size_t fast = 1; fast < prices.size(); ++fast) {
            if (prices[fast] != prices[slow - 1]) {
                prices[slow] = prices[fast];
                ++slow;
            }
        }

        prices.resize(slow);
        return prices;
    }

    std::vector<Trade> suspiciousTriples(double target) const {
        std::vector<int> roundedPrices;
        roundedPrices.reserve(trades_.size());

        /*
         * A real system would use a carefully defined monetary representation
         * such as integer minor units or a decimal library. This case study
         * rounds to integer units solely to connect domain data to the
         * educational three-sum algorithm.
         */
        for (const Trade& trade : trades_) {
            roundedPrices.push_back(
                static_cast<int>(std::llround(trade.price))
            );
        }

        const int integerTarget = static_cast<int>(std::llround(target));
        const auto triples = threeSum(roundedPrices, integerTarget);

        std::vector<Trade> result;

        for (const auto& triple : triples) {
            for (const Trade& trade : trades_) {
                const int rounded =
                    static_cast<int>(std::llround(trade.price));

                if (rounded == triple[0] ||
                    rounded == triple[1] ||
                    rounded == triple[2]) {
                    result.push_back(trade);
                }
            }
        }

        return result;
    }

    const std::vector<Trade>& trades() const {
        return trades_;
    }
};

// ============================================================================
// Tests
// ============================================================================

void runTests() {
    {
        std::vector<int> values{1, 2, 3, 4, 5};
        reverseInPlace(values);
        assert((values == std::vector<int>{5, 4, 3, 2, 1}));
    }

    {
        const std::vector<int> values{1, 2, 4, 7, 9};

        size_t first = 0;
        size_t second = 0;

        assert(twoSumSorted(values, 11, first, second));
        assert(first == 1);
        assert(second == 4);
    }

    {
        std::vector<int> values{1, 1, 2, 2, 3, 3};
        removeDuplicatesSorted(values);

        assert((values == std::vector<int>{1, 2, 3}));
    }

    {
        std::vector<int> values{2, 0, 2, 1, 1, 0};
        dutchNationalFlag(values);

        assert((values == std::vector<int>{0, 0, 1, 1, 2, 2}));
    }

    {
        const auto triples =
            threeSum({-1, 0, 1, 2, -1, -4}, 0);

        assert(triples.size() == 2);
    }

    {
        const std::vector<double> buys{10.0, 11.0, 12.0};
        const std::vector<double> sells{12.0, 13.0, 14.0};

        const auto result =
            SpreadAnalyzer::bestSpread(buys, sells);

        assert(result.has_value());
        assert(result->first == 10.0);
        assert(result->second == 14.0);
    }

    {
        RollingRiskMonitor monitor(3);

        monitor.add(100.0);
        monitor.add(105.0);
        monitor.add(103.0);
        monitor.add(108.0);

        assert(monitor.average().has_value());
        assert(std::abs(*monitor.average() - 105.3333333333) < 0.001);
        assert(monitor.maximumAbsoluteChange().has_value());
        assert(*monitor.maximumAbsoluteChange() == 5.0);
    }

    {
        FeedNode first(1);
        FeedNode second(2);
        FeedNode third(3);
        FeedNode fourth(4);

        first.next = &second;
        second.next = &third;
        third.next = &fourth;
        fourth.next = &second;

        assert(hasCycle(&first));
        assert(findCycleStart(&first) == &second);
    }

    {
        TransactionSurveillance surveillance;

        surveillance.addTrade({1, 100.0, 10, "ABC"});
        surveillance.addTrade({2, 100.0, 5, "ABC"});
        surveillance.addTrade({3, 101.0, 20, "ABC"});

        assert(surveillance.uniquePriceLevels().size() == 2);
    }

    {
        bool rejected = false;

        try {
            TransactionSurveillance surveillance;
            surveillance.addTrade({0, 100.0, 10, "ABC"});
        } catch (const std::invalid_argument&) {
            rejected = true;
        }

        assert(rejected);
    }
}

// ============================================================================
// Demonstration
// ============================================================================

void demonstrateCaseStudy() {
    std::cout << "=== Transaction Surveillance Case Study ===\n\n";

    TransactionSurveillance surveillance;

    surveillance.addTrade({1001, 100.0, 120, "NEXA"});
    surveillance.addTrade({1002, 100.0, 80, "NEXA"});
    surveillance.addTrade({1003, 101.0, 150, "NEXA"});
    surveillance.addTrade({1004, 103.0, 90, "NEXA"});
    surveillance.addTrade({1005, 104.0, 110, "NEXA"});
    surveillance.addTrade({1006, 105.0, 75, "NEXA"});
    surveillance.addTrade({1007, 105.0, 40, "NEXA"});

    const auto prices = surveillance.sortedPrices();

    std::cout << "Sorted transaction prices: ";
    printVector(prices);
    std::cout << "\n";

    const auto uniquePrices = surveillance.uniquePriceLevels();

    std::cout << "Unique price levels: ";
    printVector(uniquePrices);
    std::cout << "\n\n";

    size_t first = 0;
    size_t second = 0;

    const int integerTarget = 205;

    if (twoSumSorted(
            std::vector<int>{100, 100, 101, 103, 104, 105, 105},
            integerTarget,
            first,
            second
        )) {
        std::cout
            << "Pair target " << integerTarget
            << " found at indices "
            << first << " and " << second << ".\n";
    } else {
        std::cout
            << "No pair satisfies target "
            << integerTarget << ".\n";
    }

    std::vector<int> priceBuckets{105, 100, 103, 101, 105, 104, 100};

    const size_t boundary =
        partitionByPivot(priceBuckets, 103);

    std::cout << "Partitioned around 103: ";
    printVector(priceBuckets);
    std::cout << "\nBoundary index: " << boundary << "\n\n";

    const auto suspicious =
        surveillance.suspiciousTriples(308.0);

    std::cout
        << "Transactions participating in rounded-price "
           "three-sum matches for target 308: "
        << suspicious.size()
        << "\n";

    const std::vector<double> buyPrices{
        98.0, 99.0, 100.0, 101.0, 102.0
    };

    const std::vector<double> sellPrices{
        100.0, 101.0, 103.0, 105.0, 107.0
    };

    const auto spread =
        SpreadAnalyzer::bestSpread(buyPrices, sellPrices);

    if (spread.has_value()) {
        std::cout
            << "Best compatible spread: buy "
            << spread->first
            << ", sell "
            << spread->second
            << ", difference "
            << spread->second - spread->first
            << "\n";
    }

    RollingRiskMonitor riskMonitor(4);

    for (double price : {100.0, 101.5, 99.0, 102.0, 103.5}) {
        riskMonitor.add(price);
    }

    if (riskMonitor.average().has_value()) {
        std::cout
            << "Rolling average: "
            << std::fixed
            << std::setprecision(2)
            << *riskMonitor.average()
            << "\n";
    }

    if (riskMonitor.maximumAbsoluteChange().has_value()) {
        std::cout
            << "Maximum adjacent change in window: "
            << *riskMonitor.maximumAbsoluteChange()
            << "\n";
    }

    std::vector<Trade> feedA{
        {1, 100.0, 10, "NEXA"},
        {3, 102.0, 20, "NEXA"},
        {5, 104.0, 15, "NEXA"}
    };

    std::vector<Trade> feedB{
        {2, 101.0, 8, "NEXA"},
        {4, 103.0, 12, "NEXA"},
        {6, 105.0, 25, "NEXA"}
    };

    const auto merged =
        mergeSortedTrades(feedA, feedB);

    std::cout << "Merged feed prices: ";

    for (const Trade& trade : merged) {
        std::cout << trade.price << " ";
    }

    std::cout << "\n";

    std::cout << "\nCase-study processing completed.\n";
}

// ============================================================================
// Main
// ============================================================================

int main() {
    try {
        runTests();
        std::cout << "All C++ assertions passed.\n\n";

        demonstrateCaseStudy();
    } catch (const std::exception& error) {
        std::cerr
            << "Fatal error: "
            << error.what()
            << "\n";

        return 1;
    }

    return 0;
}
