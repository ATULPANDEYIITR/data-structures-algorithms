/*
    Advanced Hashing Problems
    ==========================

    Technical case study:
    A repository-independent transaction monitoring engine uses hashing
    techniques to detect suspicious contiguous activity windows.

    The case study demonstrates:
      - Prefix-sum hashing for exact target totals
      - Longest qualifying windows
      - Frequency-based anomaly detection
      - Pair-sum matching between transaction amounts
      - Canonical grouping of related event signatures
      - Hash-based state retention
      - Validation and failure handling
      - Complexity and integer-range considerations

    Compile:
        g++ -std=c++17 -O2 -Wall -Wextra -pedantic advanced_hashing.cpp -o advanced_hashing

    Run:
        ./advanced_hashing
*/

#include <algorithm>
#include <cstdint>
#include <exception>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

using Amount = std::int64_t;

struct Transaction {
    std::string account;
    Amount amount;
    std::string category;
};

struct Window {
    std::size_t start;
    std::size_t end;
    std::size_t length;
    Amount total;
};

struct PairMatch {
    std::size_t first;
    std::size_t second;
    Amount total;
};

class TransactionHashEngine {
private:
    std::vector<Transaction> transactions_;

public:
    explicit TransactionHashEngine(std::vector<Transaction> transactions)
        : transactions_(std::move(transactions)) {
        if (transactions_.empty()) {
            throw std::invalid_argument("At least one transaction is required.");
        }
    }

    /*
        Exact target windows use the identity:

            prefix[j] - prefix[i] = target

        Therefore a current prefix P needs an earlier prefix P - target.
        The earliest index is retained because it maximizes the resulting
        window length.
    */
    std::optional<Window> longestTargetWindow(Amount target) const {
        std::unordered_map<Amount, std::size_t> firstPrefix;
        firstPrefix.reserve(transactions_.size() * 2 + 1);

        // Prefix index zero represents the empty prefix before transaction 0.
        firstPrefix.emplace(0, 0);

        Amount running = 0;
        std::optional<Window> best;

        for (std::size_t i = 0; i < transactions_.size(); ++i) {
            running += transactions_[i].amount;

            const Amount required = running - target;
            const auto it = firstPrefix.find(required);

            if (it != firstPrefix.end()) {
                const std::size_t prefixStart = it->second;
                const std::size_t start = prefixStart;
                const std::size_t end = i;
                const std::size_t length = end - start + 1;

                Window candidate{start, end, length, target};

                if (!best.has_value() || candidate.length > best->length) {
                    best = candidate;
                }
            }

            // Never replace the earliest prefix index. Keeping a later index
            // would make all future windows unnecessarily shorter.
            firstPrefix.emplace(running, i + 1);
        }

        return best;
    }

    /*
        Count target windows rather than merely detecting one.

        Unlike longestTargetWindow, this map stores the number of times each
        prefix sum has occurred. Every previous occurrence of P-target forms
        a distinct interval ending at the current transaction.
    */
    std::uint64_t countTargetWindows(Amount target) const {
        std::unordered_map<Amount, std::uint64_t> prefixFrequency;
        prefixFrequency.reserve(transactions_.size() * 2 + 1);
        prefixFrequency[0] = 1;

        Amount running = 0;
        std::uint64_t result = 0;

        for (const auto& transaction : transactions_) {
            running += transaction.amount;

            const auto it = prefixFrequency.find(running - target);

            if (it != prefixFrequency.end()) {
                result += it->second;
            }

            ++prefixFrequency[running];
        }

        return result;
    }

    /*
        Frequency-based anomaly analysis.

        A category-frequency map separates "how often an event occurs" from
        the ordering of transactions. This is useful when repeated categories
        need to be detected independently of contiguous-window logic.
    */
    std::unordered_map<std::string, std::size_t> categoryFrequency() const {
        std::unordered_map<std::string, std::size_t> frequencies;
        frequencies.reserve(transactions_.size() * 2 + 1);

        for (const auto& transaction : transactions_) {
            ++frequencies[transaction.category];
        }

        return frequencies;
    }

    std::vector<std::string> frequentCategories(std::size_t minimum) const {
        const auto frequencies = categoryFrequency();
        std::vector<std::string> result;

        for (const auto& [category, count] : frequencies) {
            if (count >= minimum) {
                result.push_back(category);
            }
        }

        std::sort(result.begin(), result.end());

        return result;
    }

    /*
        Pair-sum detection operates on transaction positions.

        If a transaction has amount X, only previously observed amount
        target-X is required. A frequency map could count all pairs, while
        this index map returns an actual matching pair.
    */
    std::optional<PairMatch> findPairWithTotal(Amount target) const {
        std::unordered_map<Amount, std::size_t> previous;
        previous.reserve(transactions_.size() * 2 + 1);

        for (std::size_t i = 0; i < transactions_.size(); ++i) {
            const Amount current = transactions_[i].amount;
            const Amount required = target - current;

            const auto it = previous.find(required);

            if (it != previous.end()) {
                return PairMatch{it->second, i, target};
            }

            previous.emplace(current, i);
        }

        return std::nullopt;
    }

    /*
        Count all pair indices whose amounts add to target.

        Duplicates matter here. If three transactions have amount 100 and
        the target is 200, they contribute C(3,2)=3 pairs.
    */
    std::uint64_t countPairsWithTotal(Amount target) const {
        std::unordered_map<Amount, std::uint64_t> frequency;
        frequency.reserve(transactions_.size() * 2 + 1);

        std::uint64_t result = 0;

        for (const auto& transaction : transactions_) {
            const Amount required = target - transaction.amount;

            const auto it = frequency.find(required);

            if (it != frequency.end()) {
                result += it->second;
            }

            ++frequency[transaction.amount];
        }

        return result;
    }

    /*
        Group accounts by a canonical activity signature.

        The signature is based on the sorted sequence of transaction
        categories. Two accounts with the same multiset of categories receive
        the same key. Sorting the categories makes the representation
        independent of their original order.
    */
    std::map<std::string, std::vector<std::string>> groupAccountsBySignature()
        const {
        std::map<std::string, std::vector<std::string>> groups;

        std::unordered_map<std::string, std::vector<std::string>> accountEvents;

        for (const auto& transaction : transactions_) {
            accountEvents[transaction.account].push_back(transaction.category);
        }

        for (auto& [account, categories] : accountEvents) {
            std::sort(categories.begin(), categories.end());

            std::string signature;

            for (const auto& category : categories) {
                signature += category;
                signature += '|';
            }

            groups[signature].push_back(account);
        }

        return groups;
    }

    const std::vector<Transaction>& transactions() const {
        return transactions_;
    }
};

static void printWindow(
    const std::optional<Window>& window,
    const std::vector<Transaction>& transactions) {

    if (!window.has_value()) {
        std::cout << "No matching contiguous window.\n";
        return;
    }

    std::cout
        << "Window [" << window->start
        << ", " << window->end
        << "] length=" << window->length
        << " total=" << window->total << '\n';

    for (std::size_t i = window->start; i <= window->end; ++i) {
        std::cout
            << "  " << i
            << ": " << transactions[i].account
            << " amount=" << transactions[i].amount
            << " category=" << transactions[i].category
            << '\n';
    }
}

static void demonstratePrefixHashing(
    const TransactionHashEngine& engine) {

    std::cout << "\nPrefix-sum hashing\n";
    std::cout << "------------------\n";

    const Amount target = 100;

    std::cout
        << "Longest contiguous window with total "
        << target << ":\n";

    printWindow(
        engine.longestTargetWindow(target),
        engine.transactions()
    );

    std::cout
        << "Number of contiguous windows with total "
        << target << ": "
        << engine.countTargetWindows(target)
        << '\n';
}

static void demonstrateFrequencyAnalysis(
    const TransactionHashEngine& engine) {

    std::cout << "\nFrequency-based analysis\n";
    std::cout << "------------------------\n";

    const auto frequencies = engine.categoryFrequency();

    std::vector<std::pair<std::string, std::size_t>> ordered(
        frequencies.begin(),
        frequencies.end()
    );

    std::sort(
        ordered.begin(),
        ordered.end(),
        [](const auto& left, const auto& right) {
            if (left.second != right.second) {
                return left.second > right.second;
            }

            return left.first < right.first;
        }
    );

    for (const auto& [category, count] : ordered) {
        std::cout
            << std::left
            << std::setw(12)
            << category
            << " count=" << count
            << '\n';
    }

    std::cout << "Categories occurring at least twice:\n";

    for (const auto& category : engine.frequentCategories(2)) {
        std::cout << "  " << category << '\n';
    }
}

static void demonstratePairHashing(
    const TransactionHashEngine& engine) {

    std::cout << "\nPair-sum hashing\n";
    std::cout << "----------------\n";

    const Amount target = 100;

    const auto pair = engine.findPairWithTotal(target);

    if (pair.has_value()) {
        std::cout
            << "Matching pair: indexes "
            << pair->first
            << " and "
            << pair->second
            << " with total "
            << pair->total
            << '\n';
    } else {
        std::cout << "No pair reaches the requested total.\n";
    }

    std::cout
        << "All index-pairs reaching "
        << target
        << ": "
        << engine.countPairsWithTotal(target)
        << '\n';
}

static void demonstrateGrouping(
    const TransactionHashEngine& engine) {

    std::cout << "\nCanonical grouping\n";
    std::cout << "------------------\n";

    const auto groups = engine.groupAccountsBySignature();

    for (const auto& [signature, accounts] : groups) {
        std::cout << "signature=" << signature << "\n";

        for (const auto& account : accounts) {
            std::cout << "  account=" << account << '\n';
        }
    }
}

static void demonstrateFailureConditions() {
    std::cout << "\nValidation and failure handling\n";
    std::cout << "-------------------------------\n";

    try {
        TransactionHashEngine invalid({});
    } catch (const std::exception& error) {
        std::cout
            << "Rejected empty transaction stream: "
            << error.what()
            << '\n';
    }

    try {
        std::vector<Transaction> valid{
            {"A", 10, "login"}
        };

        TransactionHashEngine engine(std::move(valid));
        engine.longestTargetWindow(
            std::numeric_limits<Amount>::max()
        );

        std::cout
            << "Large target processed without narrowing it to int.\n";
    } catch (const std::exception& error) {
        std::cout
            << "Unexpected validation failure: "
            << error.what()
            << '\n';
    }
}

int main() {
    try {
        /*
            The sequence deliberately contains negative amounts. This makes
            prefix hashing necessary: a sliding-window technique that assumes
            non-negative values cannot safely solve the same exact-sum problem.
        */
        const std::vector<Transaction> transactions{
            {"ACCT-01", 40, "deposit"},
            {"ACCT-02", -20, "refund"},
            {"ACCT-01", 60, "purchase"},
            {"ACCT-03", 20, "login"},
            {"ACCT-02", 80, "purchase"},
            {"ACCT-01", -40, "refund"},
            {"ACCT-03", 20, "purchase"},
            {"ACCT-02", 40, "deposit"},
            {"ACCT-01", 60, "purchase"},
            {"ACCT-03", -20, "refund"}
        };

        const TransactionHashEngine engine(transactions);

        std::cout << "Advanced Hashing Case Study\n";
        std::cout << "===========================\n";

        demonstratePrefixHashing(engine);
        demonstrateFrequencyAnalysis(engine);
        demonstratePairHashing(engine);
        demonstrateGrouping(engine);
        demonstrateFailureConditions();

        /*
            Complexity:
              - Prefix target detection/counting: expected O(n)
              - Frequency analysis: expected O(n)
              - Pair-sum detection/counting: expected O(n)
              - Canonical grouping here: O(n log n) in total for sorting
                each account's category list.
              - Auxiliary hash-map storage: O(n)

            unordered_map and unordered_set provide expected constant-time
            lookup, not a mathematical worst-case guarantee. Hash collisions
            can degrade operations toward linear behavior for adversarial input.
        */

        std::cout << "\nCase study completed.\n";
    } catch (const std::exception& error) {
        std::cerr
            << "Fatal error: "
            << error.what()
            << '\n';

        return 1;
    }

    return 0;
}
