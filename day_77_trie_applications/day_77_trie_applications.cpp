#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <exception>
#include <iomanip>
#include <iostream>
#include <limits>
#include <memory>
#include <optional>
#include <queue>
#include <random>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

using namespace std;

// ============================================================
// 1. DOMAIN TYPES
// ============================================================

enum class QueryMode {
    Maximum,
    Minimum
};

struct XorResult {
    uint64_t xorValue;
    uint64_t matchedValue;
};

struct PairResult {
    uint64_t maximumXor;
    uint64_t first;
    uint64_t second;
};

// ============================================================
// 2. COMPRESSED RADIX TRIE
// ============================================================

class RadixTrie {
private:
    struct Node {
        string edge;
        bool terminal = false;
        vector<unique_ptr<Node>> children;

        explicit Node(string label = "")
            : edge(move(label)) {}
    };

    Node root;
    size_t wordCount = 0;

    static size_t commonPrefix(
        const string& a,
        const string& b
    ) {
        size_t i = 0;

        while (
            i < a.size() &&
            i < b.size() &&
            a[i] == b[i]
        ) {
            ++i;
        }

        return i;
    }

    static Node* findChild(Node& node, char first) {
        for (auto& child : node.children) {
            if (child->edge[0] == first) {
                return child.get();
            }
        }

        return nullptr;
    }

    static void collect(
        const Node& node,
        const string& prefix,
        vector<string>& results,
        size_t limit
    ) {
        if (results.size() >= limit) return;

        if (node.terminal) {
            results.push_back(prefix);
        }

        for (const auto& child : node.children) {
            if (results.size() >= limit) break;

            collect(
                *child,
                prefix + child->edge,
                results,
                limit
            );
        }
    }

    bool eraseRecursive(Node& node, const string& remaining) {
        Node* child = findChild(node, remaining[0]);

        if (!child) return false;

        size_t common = commonPrefix(remaining, child->edge);

        if (common != child->edge.size()) return false;

        string suffix = remaining.substr(common);

        if (!suffix.empty()) {
            if (!eraseRecursive(*child, suffix)) return false;
        } else {
            if (!child->terminal) return false;
            child->terminal = false;
        }

        auto& children = node.children;

        for (auto it = children.begin(); it != children.end(); ++it) {
            if (it->get() == child) {
                if (!child->terminal && child->children.empty()) {
                    children.erase(it);
                } else if (
                    !child->terminal &&
                    child->children.size() == 1
                ) {
                    unique_ptr<Node> next =
                        move(child->children.front());

                    child->edge += next->edge;
                    child->terminal = next->terminal;
                    child->children = move(next->children);
                }

                break;
            }
        }

        return true;
    }

public:
    bool insert(const string& word) {
        if (word.empty()) {
            throw invalid_argument("Empty words are not supported.");
        }

        Node* node = &root;
        string remaining = word;

        while (!remaining.empty()) {
            Node* child = findChild(*node, remaining[0]);

            if (!child) {
                auto fresh = make_unique<Node>(remaining);
                fresh->terminal = true;
                node->children.push_back(move(fresh));
                ++wordCount;
                return true;
            }

            size_t common = commonPrefix(
                remaining,
                child->edge
            );

            if (common == child->edge.size()) {
                remaining.erase(0, common);
                node = child;

                if (remaining.empty()) {
                    if (node->terminal) return false;

                    node->terminal = true;
                    ++wordCount;
                    return true;
                }

                continue;
            }

            auto intermediate = make_unique<Node>(
                child->edge.substr(0, common)
            );

            child->edge.erase(0, common);

            unique_ptr<Node> oldChild;

            for (auto& item : node->children) {
                if (item.get() == child) {
                    oldChild = move(item);
                    break;
                }
            }

            intermediate->children.push_back(move(oldChild));

            string suffix = remaining.substr(common);

            if (suffix.empty()) {
                intermediate->terminal = true;
            } else {
                auto fresh = make_unique<Node>(suffix);
                fresh->terminal = true;
                intermediate->children.push_back(move(fresh));
            }

            for (auto& item : node->children) {
                if (!item) {
                    item = move(intermediate);
                    break;
                }
            }

            ++wordCount;
            return true;
        }

        return false;
    }

    bool search(const string& word) const {
        if (word.empty()) return false;

        const Node* node = &root;
        string remaining = word;

        while (!remaining.empty()) {
            const Node* child = nullptr;

            for (const auto& candidate : node->children) {
                if (candidate->edge[0] == remaining[0]) {
                    child = candidate.get();
                    break;
                }
            }

            if (!child) return false;

            if (remaining.compare(
                    0,
                    child->edge.size(),
                    child->edge
                ) != 0) {
                return false;
            }

            remaining.erase(0, child->edge.size());
            node = child;
        }

        return node->terminal;
    }

    bool startsWith(const string& prefix) const {
        if (prefix.empty()) return false;

        const Node* node = &root;
        string remaining = prefix;

        while (!remaining.empty()) {
            const Node* child = nullptr;

            for (const auto& candidate : node->children) {
                if (candidate->edge[0] == remaining[0]) {
                    child = candidate.get();
                    break;
                }
            }

            if (!child) return false;

            size_t common = commonPrefix(
                remaining,
                child->edge
            );

            if (common == remaining.size()) return true;
            if (common != child->edge.size()) return false;

            remaining.erase(0, common);
            node = child;
        }

        return true;
    }

    bool erase(const string& word) {
        if (!search(word)) return false;

        if (eraseRecursive(root, word)) {
            --wordCount;
            return true;
        }

        return false;
    }

    vector<string> autocomplete(
        const string& prefix,
        size_t limit = 10
    ) const {
        vector<string> results;

        if (prefix.empty() || limit == 0) {
            return results;
        }

        const Node* node = &root;
        string remaining = prefix;
        string accumulated;

        while (!remaining.empty()) {
            const Node* child = nullptr;

            for (const auto& candidate : node->children) {
                if (candidate->edge[0] == remaining[0]) {
                    child = candidate.get();
                    break;
                }
            }

            if (!child) return results;

            size_t common = commonPrefix(
                remaining,
                child->edge
            );

            if (
                common < remaining.size() &&
                common < child->edge.size()
            ) {
                return results;
            }

            accumulated += child->edge;
            remaining.erase(0, common);
            node = child;
        }

        collect(*node, accumulated, results, limit);
        sort(results.begin(), results.end());

        return results;
    }

    size_t size() const {
        return wordCount;
    }
};


// ============================================================
// 3. BINARY TRIE GOVERNANCE ENGINE
// ============================================================

class BinaryTrie {
private:
    struct Node {
        array<unique_ptr<Node>, 2> children;
        uint64_t count = 0;
    };

    Node root;
    unsigned width;
    uint64_t size_ = 0;

    void validate(uint64_t value) const {
        if (width < 64 && value >= (uint64_t(1) << width)) {
            throw out_of_range("Value exceeds configured bit width.");
        }
    }

public:
    explicit BinaryTrie(unsigned bitWidth = 32)
        : width(bitWidth) {
        if (width == 0 || width > 64) {
            throw invalid_argument("Width must be between 1 and 64.");
        }
    }

    void insert(uint64_t value) {
        validate(value);

        Node* node = &root;
        ++node->count;

        for (int bit = static_cast<int>(width) - 1;
             bit >= 0; --bit) {

            unsigned direction = (value >> bit) & 1ULL;

            if (!node->children[direction]) {
                node->children[direction] = make_unique<Node>();
            }

            node = node->children[direction].get();
            ++node->count;
        }

        ++size_;
    }

    bool contains(uint64_t value) const {
        validate(value);

        const Node* node = &root;

        for (int bit = static_cast<int>(width) - 1;
             bit >= 0; --bit) {

            unsigned direction = (value >> bit) & 1ULL;

            if (!node->children[direction]) return false;

            node = node->children[direction].get();

            if (node->count == 0) return false;
        }

        return true;
    }

    bool erase(uint64_t value) {
        validate(value);

        if (!contains(value)) return false;

        Node* node = &root;
        --node->count;

        for (int bit = static_cast<int>(width) - 1;
             bit >= 0; --bit) {

            unsigned direction = (value >> bit) & 1ULL;
            Node* child = node->children[direction].get();

            --child->count;

            if (child->count == 0) {
                node->children[direction].reset();
                break;
            }

            node = child;
        }

        --size_;
        return true;
    }

    XorResult query(
        uint64_t value,
        QueryMode mode = QueryMode::Maximum
    ) const {
        validate(value);

        if (size_ == 0) {
            throw logic_error("Cannot query an empty trie.");
        }

        const Node* node = &root;
        uint64_t matched = 0;
        uint64_t xorValue = 0;

        for (int bit = static_cast<int>(width) - 1;
             bit >= 0; --bit) {

            unsigned current = (value >> bit) & 1ULL;

            unsigned preferred =
                mode == QueryMode::Maximum
                ? 1U - current
                : current;

            unsigned alternate = 1U - preferred;
            unsigned selected;

            if (
                node->children[preferred] &&
                node->children[preferred]->count > 0
            ) {
                selected = preferred;
            } else {
                selected = alternate;
            }

            if (selected != current) {
                xorValue |= uint64_t(1) << bit;
            }

            matched |= uint64_t(selected) << bit;
            node = node->children[selected].get();
        }

        return {xorValue, matched};
    }

    optional<PairResult> maximumXorPair(
        const vector<uint64_t>& values
    ) {
        if (values.size() < 2) return nullopt;

        root = Node();
        size_ = 0;

        uint64_t best = 0;
        uint64_t first = 0;
        uint64_t second = 0;

        bool initialized = false;

        for (uint64_t value : values) {
            validate(value);

            if (size_ > 0) {
                XorResult result = query(value);

                if (!initialized || result.xorValue > best) {
                    initialized = true;
                    best = result.xorValue;
                    first = value;
                    second = result.matchedValue;
                }
            }

            insert(value);
        }

        return PairResult{best, first, second};
    }

    uint64_t size() const {
        return size_;
    }
};


// ============================================================
// 4. REPOSITORY-STYLE POLICY EVALUATION
// ============================================================

struct GovernanceReport {
    bool eligible;
    vector<string> blockers;
};

class MergeEligibilityEngine {
private:
    BinaryTrie numericIndex;

public:
    GovernanceReport evaluate(
        const vector<uint64_t>& values,
        size_t requiredReviews,
        size_t approvals,
        bool checksPassed,
        bool protectedBranch,
        bool conversationsResolved,
        bool branchSynchronized,
        bool draft,
        bool mergeConflict,
        bool linearHistory
    ) {
        GovernanceReport report{true, {}};

        if (draft) {
            report.blockers.push_back("Pull Request is a draft.");
        }

        if (mergeConflict) {
            report.blockers.push_back("Merge conflicts exist.");
        }

        if (!checksPassed) {
            report.blockers.push_back("Required checks have not passed.");
        }

        if (approvals < requiredReviews) {
            report.blockers.push_back("Required approvals are missing.");
        }

        if (!conversationsResolved) {
            report.blockers.push_back("Review conversations are unresolved.");
        }

        if (!branchSynchronized) {
            report.blockers.push_back("Source branch requires synchronization.");
        }

        if (!linearHistory) {
            report.blockers.push_back("Linear history requirement failed.");
        }

        if (protectedBranch && approvals == 0 && requiredReviews > 0) {
            report.blockers.push_back("Protected branch approval requirement failed.");
        }

        report.eligible = report.blockers.empty();

        if (!values.empty()) {
            auto result = numericIndex.maximumXorPair(values);

            if (result) {
                cout << "Governance index maximum XOR: "
                     << result->maximumXor << '\n';
            }
        }

        return report;
    }
};


// ============================================================
// 5. EXECUTABLE TEST SCENARIO
// ============================================================

int main() {
    try {
        cout << "ADVANCED TRIE ENGINEERING\n";

        cout << "\nCOMPRESSED RADIX TRIE\n";

        RadixTrie words;

        vector<string> dictionary = {
            "application",
            "apply",
            "apple",
            "app",
            "binary",
            "bitwise",
            "bit",
            "database"
        };

        for (const auto& word : dictionary) {
            words.insert(word);
        }

        cout << "Stored words: " << words.size() << '\n';
        cout << "Search application: "
             << boolalpha << words.search("application") << '\n';

        cout << "Prefix appl: "
             << words.startsWith("appl") << '\n';

        for (const auto& word : words.autocomplete("app", 10)) {
            cout << word << '\n';
        }

        words.erase("apple");

        cout << "After deletion: "
             << words.search("apple") << '\n';

        cout << "\nBINARY XOR TRIE\n";

        BinaryTrie binary(8);

        vector<uint64_t> values = {
            3, 10, 5, 25, 2, 8
        };

        auto pairResult = binary.maximumXorPair(values);

        if (pairResult) {
            cout << "Maximum XOR: "
                 << pairResult->maximumXor << '\n';

            cout << "Pair: "
                 << pairResult->first << ", "
                 << pairResult->second << '\n';
        }

        binary.insert(12);
        binary.insert(12);

        cout << "Contains 12: " << binary.contains(12) << '\n';

        binary.erase(12);
        cout << "Contains after one deletion: "
             << binary.contains(12) << '\n';

        binary.erase(12);
        cout << "Contains after second deletion: "
             << binary.contains(12) << '\n';

        cout << "\nMINIMUM XOR QUERY\n";

        binary.insert(10);
        binary.insert(12);

        auto minimum = binary.query(
            10,
            QueryMode::Minimum
        );

        cout << "Minimum XOR: "
             << minimum.xorValue << '\n';

        cout << "\nMERGE ELIGIBILITY ENGINE\n";

        MergeEligibilityEngine engine;

        GovernanceReport report = engine.evaluate(
            values,
            2,
            2,
            true,
            true,
            true,
            true,
            false,
            false,
            true
        );

        cout << "Merge eligible: "
             << report.eligible << '\n';

        if (!report.eligible) {
            for (const auto& blocker : report.blockers) {
                cout << "- " << blocker << '\n';
            }
        }

        cout << "\nBLOCKED MERGE SCENARIO\n";

        GovernanceReport blocked = engine.evaluate(
            values,
            2,
            1,
            false,
            true,
            false,
            false,
            false,
            true,
            false
        );

        cout << "Merge eligible: "
             << blocked.eligible << '\n';

        for (const auto& blocker : blocked.blockers) {
            cout << "- " << blocker << '\n';
        }

        cout << "\nEDGE CASES\n";

        try {
            RadixTrie invalid;
            invalid.insert("");
        } catch (const invalid_argument& error) {
            cout << "Validation: " << error.what() << '\n';
        }

        try {
            BinaryTrie empty(8);
            empty.query(1);
        } catch (const logic_error& error) {
            cout << "Empty query: " << error.what() << '\n';
        }

        try {
            binary.insert(256);
        } catch (const out_of_range& error) {
            cout << "Range check: " << error.what() << '\n';
        }

        cout << "\nRANDOMIZED VALIDATION\n";

        mt19937_64 generator(42);
        uniform_int_distribution<uint64_t> distribution(0, 65535);

        vector<uint64_t> randomValues;

        for (int i = 0; i < 1000; ++i) {
            randomValues.push_back(distribution(generator));
        }

        BinaryTrie randomTrie(16);

        auto randomResult =
            randomTrie.maximumXorPair(randomValues);

        uint64_t bruteForce = 0;

        for (size_t i = 0; i < randomValues.size(); ++i) {
            for (size_t j = i + 1; j < randomValues.size(); ++j) {
                bruteForce = max(
                    bruteForce,
                    randomValues[i] ^ randomValues[j]
                );
            }
        }

        assert(randomResult.has_value());
        assert(randomResult->maximumXor == bruteForce);

        cout << "Optimized result: "
             << randomResult->maximumXor << '\n';

        cout << "Brute-force result: "
             << bruteForce << '\n';

        cout << "Validation passed.\n";

    } catch (const exception& error) {
        cerr << "Fatal error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
