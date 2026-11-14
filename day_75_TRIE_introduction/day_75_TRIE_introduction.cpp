/*
 * TRIE INTRODUCTION: C++17 PREFIX DICTIONARY ENGINE
 *
 * Scenario:
 * An enterprise command catalogue stores commands, validates
 * exact commands, searches prefixes, and generates suggestions.
 *
 * Features:
 * - Domain-oriented node structures
 * - STL unordered_map transitions
 * - Insertion and exact searching
 * - Prefix matching
 * - Autocomplete
 * - Frequency counting
 * - Safe deletion
 * - Longest stored prefix
 * - Dictionary statistics
 * - Input validation
 * - Automated assertions
 *
 * Compile:
 * g++ -std=c++17 -O2 -Wall -Wextra -pedantic trie.cpp -o trie
 */

#include <algorithm>
#include <cassert>
#include <cctype>
#include <iostream>
#include <memory>
#include <queue>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

using namespace std;

class TrieException : public runtime_error {
public:
    explicit TrieException(const string& message)
        : runtime_error(message) {}
};

class Trie {
private:
    struct Node {
        unordered_map<char, unique_ptr<Node>> children;
        bool terminal = false;
        size_t frequency = 0;
    };

    Node root;
    size_t distinctWords = 0;
    size_t totalInsertions = 0;

    static string normalize(const string& input) {
        if (input.empty()) {
            throw TrieException("Word cannot be empty.");
        }

        if (input.size() > 256) {
            throw TrieException("Word exceeds 256 bytes.");
        }

        string result;

        for (unsigned char character : input) {
            if (character < 32 || character > 126) {
                throw TrieException(
                    "Only printable ASCII characters are supported."
                );
            }

            result.push_back(
                static_cast<char>(tolower(character))
            );
        }

        return result;
    }

    const Node* findNode(const string& word) const {
        const Node* current = &root;

        for (char character : word) {
            auto it = current->children.find(character);

            if (it == current->children.end()) {
                return nullptr;
            }

            current = it->second.get();
        }

        return current;
    }

    static void collect(
        const Node& node,
        string& current,
        vector<string>& results,
        size_t limit
    ) {
        if (results.size() >= limit) {
            return;
        }

        if (node.terminal) {
            results.push_back(current);
        }

        vector<char> characters;

        characters.reserve(node.children.size());

        for (const auto& entry : node.children) {
            characters.push_back(entry.first);
        }

        sort(characters.begin(), characters.end());

        for (char character : characters) {
            if (results.size() >= limit) {
                break;
            }

            current.push_back(character);

            collect(
                *node.children.at(character),
                current,
                results,
                limit
            );

            current.pop_back();
        }
    }

    static bool prune(Node& node, const string& word, size_t depth) {
        if (depth == word.size()) {
            if (!node.terminal) {
                return false;
            }

            node.terminal = false;
            node.frequency = 0;

            return node.children.empty();
        }

        char character = word[depth];

        auto it = node.children.find(character);

        if (it == node.children.end()) {
            return false;
        }

        bool removable = prune(
            *it->second,
            word,
            depth + 1
        );

        if (removable) {
            node.children.erase(it);
        }

        return !node.terminal && node.children.empty();
    }

public:
    bool insert(const string& input) {
        string word = normalize(input);
        Node* current = &root;

        for (char character : word) {
            auto& child = current->children[character];

            if (!child) {
                child = make_unique<Node>();
            }

            current = child.get();
        }

        bool created = !current->terminal;

        current->terminal = true;
        current->frequency++;

        totalInsertions++;

        if (created) {
            distinctWords++;
        }

        return created;
    }

    bool search(const string& input) const {
        string word = normalize(input);
        const Node* node = findNode(word);

        return node != nullptr && node->terminal;
    }

    bool startsWith(const string& input) const {
        string prefix = normalize(input);

        return findNode(prefix) != nullptr;
    }

    size_t frequency(const string& input) const {
        string word = normalize(input);
        const Node* node = findNode(word);

        if (!node || !node->terminal) {
            return 0;
        }

        return node->frequency;
    }

    vector<string> autocomplete(
        const string& input,
        size_t limit = 10
    ) const {
        string prefix = normalize(input);

        if (limit == 0 || limit > 1000) {
            throw TrieException("Invalid suggestion limit.");
        }

        const Node* start = findNode(prefix);

        vector<string> results;

        if (!start) {
            return results;
        }

        string current = prefix;

        collect(*start, current, results, limit);

        return results;
    }

    bool erase(const string& input) {
        string word = normalize(input);

        if (!search(word)) {
            return false;
        }

        prune(root, word, 0);
        distinctWords--;

        return true;
    }

    string longestPrefix(const string& input) const {
        string text = normalize(input);

        const Node* current = &root;

        string candidate;
        string longest;

        for (char character : text) {
            auto it = current->children.find(character);

            if (it == current->children.end()) {
                break;
            }

            current = it->second.get();
            candidate.push_back(character);

            if (current->terminal) {
                longest = candidate;
            }
        }

        return longest;
    }

    struct Statistics {
        size_t words = 0;
        size_t insertions = 0;
        size_t nodes = 0;
        size_t edges = 0;
        size_t maximumDepth = 0;
    };

    Statistics statistics() const {
        Statistics stats;

        stats.words = distinctWords;
        stats.insertions = totalInsertions;

        queue<pair<const Node*, size_t>> pending;

        pending.push({&root, 0});

        while (!pending.empty()) {
            auto [node, depth] = pending.front();
            pending.pop();

            stats.nodes++;

            stats.maximumDepth = max(
                stats.maximumDepth,
                depth
            );

            for (const auto& [character, child] : node->children) {
                (void)character;

                stats.edges++;

                pending.push({
                    child.get(),
                    depth + 1
                });
            }
        }

        return stats;
    }

    void printSuggestions(
        const string& prefix,
        size_t limit = 10
    ) const {
        vector<string> results = autocomplete(prefix, limit);

        cout << prefix << ": ";

        if (results.empty()) {
            cout << "No matching words";
        } else {
            for (const string& word : results) {
                cout << word << " ";
            }
        }

        cout << '\n';
    }
};

void runTests() {
    Trie trie;

    assert(trie.insert("car"));
    assert(trie.insert("cart"));
    assert(trie.insert("cat"));
    assert(!trie.insert("car"));

    assert(trie.search("car"));
    assert(!trie.search("ca"));

    assert(trie.startsWith("ca"));
    assert(!trie.startsWith("xyz"));

    assert(trie.frequency("car") == 2);

    vector<string> expected = {"car", "cart"};

    assert(trie.autocomplete("car") == expected);

    assert(trie.erase("car"));
    assert(!trie.search("car"));
    assert(trie.search("cart"));

    assert(trie.erase("cart"));
    assert(!trie.startsWith("car"));

    assert(trie.search("cat"));

    assert(!trie.erase("missing"));

    TrieException caught("not caught");

    try {
        trie.insert("");
    } catch (const TrieException&) {
        caught = TrieException("validation successful");
    }

    assert(string(caught.what()) == "validation successful");

    cout << "All C++ assertions passed.\n";
}

int main() {
    try {
        cout << "========================================\n";
        cout << "TRIE: ENTERPRISE COMMAND DICTIONARY\n";
        cout << "========================================\n";

        Trie commands;

        vector<string> catalogue = {
            "deploy",
            "deployment",
            "deployments",
            "delete",
            "describe",
            "design",
            "device",
            "directory",
            "database",
            "debug",
            "docker",
            "document",
            "download",
            "download"
        };

        cout << "\n1. INSERTION\n";

        for (const string& command : catalogue) {
            bool created = commands.insert(command);

            cout << command << " -> "
                 << (created ? "NEW" : "EXISTING")
                 << '\n';
        }

        cout << "\n2. EXACT SEARCH\n";

        for (const string& command : {
            "deploy", "deployment", "depl", "unknown"
        }) {
            cout << command << ": "
                 << (commands.search(command) ? "FOUND" : "NOT FOUND")
                 << '\n';
        }

        cout << "\n3. PREFIX MATCHING\n";

        for (const string& prefix : {
            "dep", "do", "dat", "xyz"
        }) {
            cout << prefix << ": "
                 << (commands.startsWith(prefix) ? "MATCH" : "NO MATCH")
                 << '\n';
        }

        cout << "\n4. AUTOCOMPLETE\n";

        commands.printSuggestions("dep");
        commands.printSuggestions("do", 3);
        commands.printSuggestions("dat");

        cout << "\n5. FREQUENCY\n";

        cout << "download: "
             << commands.frequency("download")
             << '\n';

        cout << "\n6. LONGEST PREFIX\n";

        cout << "deployment_service: "
             << commands.longestPrefix("deployment_service")
             << '\n';

        cout << "\n7. DELETION\n";

        cout << "Delete deploy: "
             << commands.erase("deploy")
             << '\n';

        cout << "deploy exists: "
             << commands.search("deploy")
             << '\n';

        cout << "deployment exists: "
             << commands.search("deployment")
             << '\n';

        cout << "\n8. STRUCTURAL STATISTICS\n";

        auto stats = commands.statistics();

        cout << "Distinct words: " << stats.words << '\n';
        cout << "Insertions: " << stats.insertions << '\n';
        cout << "Nodes: " << stats.nodes << '\n';
        cout << "Edges: " << stats.edges << '\n';
        cout << "Maximum depth: " << stats.maximumDepth << '\n';

        cout << "\n9. AUTOMATED TESTS\n";

        runTests();

        cout << "\n10. ENGINEERING CHARACTERISTICS\n";

        cout << "Insertion: O(L) expected\n";
        cout << "Search: O(L) expected\n";
        cout << "Prefix lookup: O(P) expected\n";
        cout << "Autocomplete: O(P + V + K log K)\n";
        cout << "Deletion: O(L)\n";
        cout << "Storage: O(N) trie nodes\n";

        cout << "\nExecution completed successfully.\n";

    } catch (const exception& error) {
        cerr << "Application error: "
             << error.what()
             << '\n';

        return 1;
    }

    return 0;
}
