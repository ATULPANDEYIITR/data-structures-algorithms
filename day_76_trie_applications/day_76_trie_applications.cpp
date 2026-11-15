#include <algorithm>
#include <array>
#include <cctype>
#include <functional>
#include <iostream>
#include <memory>
#include <queue>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

using namespace std;

/*
 * Trie Applications - C++17
 *
 * Implements:
 * - Prefix tree and dictionary operations
 * - Frequency-ranked autocomplete
 * - Exact word lookup
 * - Prefix lookup
 * - Deletion and memory pruning
 * - Wildcard search
 * - Word Break
 * - Word Search II
 */

class Trie {
public:
    struct Node {
        array<unique_ptr<Node>, 26> children{};
        bool terminal = false;
        int frequency = 0;
    };

    struct Suggestion {
        string word;
        int frequency;
    };

private:
    Node root;
    size_t wordCount = 0;

    static string normalize(const string& input) {
        if (input.empty()) {
            throw invalid_argument("Word cannot be empty.");
        }

        string result;
        result.reserve(input.size());

        for (unsigned char character : input) {
            if (!isalpha(character) || character > 127) {
                throw invalid_argument(
                    "Only ASCII alphabetic characters are supported."
                );
            }

            result.push_back(
                static_cast<char>(tolower(character))
            );
        }

        return result;
    }

    static int indexOf(char character) {
        return character - 'a';
    }

    Node* findNode(const string& prefix) {
        Node* node = &root;

        for (char character : prefix) {
            node = node->children[indexOf(character)].get();

            if (!node) {
                return nullptr;
            }
        }

        return node;
    }

    const Node* findNode(const string& prefix) const {
        const Node* node = &root;

        for (char character : prefix) {
            node = node->children[indexOf(character)].get();

            if (!node) {
                return nullptr;
            }
        }

        return node;
    }

    static bool hasChildren(const Node& node) {
        for (const auto& child : node.children) {
            if (child) {
                return true;
            }
        }

        return false;
    }

    bool deleteRecursive(Node& node, const string& word, size_t depth) {
        if (depth == word.size()) {
            if (!node.terminal) {
                return false;
            }

            node.terminal = false;
            node.frequency = 0;
            return true;
        }

        const int index = indexOf(word[depth]);

        auto& child = node.children[index];

        if (!child) {
            return false;
        }

        bool deleted = deleteRecursive(*child, word, depth + 1);

        if (deleted && !child->terminal && !hasChildren(*child)) {
            child.reset();
        }

        return deleted;
    }

    static void collect(
        const Node& node,
        const string& prefix,
        vector<Suggestion>& results
    ) {
        if (node.terminal) {
            results.push_back({
                prefix,
                node.frequency
            });
        }

        for (int i = 0; i < 26; ++i) {
            if (node.children[i]) {
                collect(
                    *node.children[i],
                    prefix + static_cast<char>('a' + i),
                    results
                );
            }
        }
    }

public:
    Trie() = default;

    Trie(const Trie&) = delete;
    Trie& operator=(const Trie&) = delete;

    void insert(const string& input, int frequency = 1) {
        string word = normalize(input);

        if (frequency <= 0) {
            throw invalid_argument("Frequency must be positive.");
        }

        Node* node = &root;

        for (char character : word) {
            int index = indexOf(character);

            if (!node->children[index]) {
                node->children[index] = make_unique<Node>();
            }

            node = node->children[index].get();
        }

        if (node->frequency > 1000000000 - frequency) {
            throw overflow_error("Frequency limit exceeded.");
        }

        if (!node->terminal) {
            node->terminal = true;
            ++wordCount;
        }

        node->frequency += frequency;
    }

    bool search(const string& input) const {
        string word = normalize(input);
        const Node* node = findNode(word);

        return node && node->terminal;
    }

    bool startsWith(const string& input) const {
        string prefix = normalize(input);
        return findNode(prefix) != nullptr;
    }

    bool erase(const string& input) {
        string word = normalize(input);

        bool deleted = deleteRecursive(root, word, 0);

        if (deleted) {
            --wordCount;
        }

        return deleted;
    }

    int frequency(const string& input) const {
        string word = normalize(input);
        const Node* node = findNode(word);

        return node && node->terminal ? node->frequency : 0;
    }

    vector<Suggestion> autocomplete(
        const string& input,
        size_t limit = 10
    ) const {
        string prefix = normalize(input);

        if (limit == 0) {
            return {};
        }

        const Node* node = findNode(prefix);

        if (!node) {
            return {};
        }

        vector<Suggestion> results;

        collect(*node, prefix, results);

        sort(
            results.begin(),
            results.end(),
            [](const Suggestion& a, const Suggestion& b) {
                if (a.frequency != b.frequency) {
                    return a.frequency > b.frequency;
                }

                return a.word < b.word;
            }
        );

        if (results.size() > limit) {
            results.resize(limit);
        }

        return results;
    }

    string longestPrefix(const string& input) const {
        string text = normalize(input);

        const Node* node = &root;
        string result;

        for (size_t i = 0; i < text.size(); ++i) {
            node = node->children[indexOf(text[i])].get();

            if (!node) {
                break;
            }

            if (node->terminal) {
                result = text.substr(0, i + 1);
            }
        }

        return result;
    }

    vector<string> wildcardSearch(const string& patternInput) const {
        if (patternInput.empty()) {
            throw invalid_argument("Pattern cannot be empty.");
        }

        string pattern;

        for (unsigned char character : patternInput) {
            if (
                !isalpha(character) &&
                character != '.' &&
                character != '*'
            ) {
                throw invalid_argument("Invalid wildcard pattern.");
            }

            pattern.push_back(
                static_cast<char>(tolower(character))
            );
        }

        unordered_set<string> uniqueResults;

        function<void(const Node&, size_t, const string&)> dfs =
            [&](const Node& node, size_t position, const string& current) {
                if (position == pattern.size()) {
                    if (node.terminal) {
                        uniqueResults.insert(current);
                    }

                    return;
                }

                char token = pattern[position];

                if (token == '.') {
                    for (int i = 0; i < 26; ++i) {
                        if (node.children[i]) {
                            dfs(
                                *node.children[i],
                                position + 1,
                                current + static_cast<char>('a' + i)
                            );
                        }
                    }
                } else if (token == '*') {
                    dfs(node, position + 1, current);

                    for (int i = 0; i < 26; ++i) {
                        if (node.children[i]) {
                            dfs(
                                *node.children[i],
                                position,
                                current + static_cast<char>('a' + i)
                            );
                        }
                    }
                } else {
                    const Node* child =
                        node.children[indexOf(token)].get();

                    if (child) {
                        dfs(*child, position + 1, current + token);
                    }
                }
            };

        dfs(root, 0, "");

        vector<string> results(
            uniqueResults.begin(),
            uniqueResults.end()
        );

        sort(results.begin(), results.end());

        return results;
    }

    size_t size() const {
        return wordCount;
    }

    vector<Suggestion> allWords() const {
        vector<Suggestion> results;
        collect(root, "", results);

        sort(
            results.begin(),
            results.end(),
            [](const Suggestion& a, const Suggestion& b) {
                return a.word < b.word;
            }
        );

        return results;
    }
};

bool wordBreak(const string& input, const Trie& trie) {
    if (input.empty()) {
        return true;
    }

    string text;

    for (unsigned char character : input) {
        if (!isalpha(character) || character > 127) {
            throw invalid_argument("Invalid word-break input.");
        }

        text.push_back(
            static_cast<char>(tolower(character))
        );
    }

    vector<bool> dp(text.size() + 1, false);
    dp[0] = true;

    for (size_t start = 0; start < text.size(); ++start) {
        if (!dp[start]) {
            continue;
        }

        const Trie::Node* node = &trie.root;

        for (size_t end = start; end < text.size(); ++end) {
            int index = text[end] - 'a';

            node = node->children[index].get();

            if (!node) {
                break;
            }

            if (node->terminal) {
                dp[end + 1] = true;
            }
        }
    }

    return dp[text.size()];
}

vector<string> wordBreakSentences(
    const string& input,
    const Trie& trie,
    size_t maximumResults = 100
) {
    if (input.empty() || maximumResults == 0) {
        return {};
    }

    string text;

    for (unsigned char character : input) {
        if (!isalpha(character) || character > 127) {
            throw invalid_argument("Invalid input.");
        }

        text.push_back(
            static_cast<char>(tolower(character))
        );
    }

    vector<vector<string>> memo(text.size() + 1);
    vector<bool> computed(text.size() + 1, false);

    function<const vector<string>&(size_t)> solve =
        [&](size_t start) -> const vector<string>& {
            if (computed[start]) {
                return memo[start];
            }

            computed[start] = true;

            if (start == text.size()) {
                memo[start].push_back("");
                return memo[start];
            }

            const Trie::Node* node = &trie.root;

            for (size_t end = start; end < text.size(); ++end) {
                node = node->children[text[end] - 'a'].get();

                if (!node) {
                    break;
                }

                if (node->terminal) {
                    string word = text.substr(
                        start,
                        end - start + 1
                    );

                    for (const string& suffix : solve(end + 1)) {
                        if (memo[start].size() >= maximumResults) {
                            break;
                        }

                        memo[start].push_back(
                            suffix.empty()
                                ? word
                                : word + " " + suffix
                        );
                    }
                }

                if (memo[start].size() >= maximumResults) {
                    break;
                }
            }

            return memo[start];
        };

    return solve(0);
}

class WordSearch {
private:
    vector<vector<char>> board;
    int rows;
    int columns;
    unordered_set<string> found;

    const vector<pair<int, int>> directions = {
        {1, 0},
        {-1, 0},
        {0, 1},
        {0, -1}
    };

    void dfs(
        int row,
        int column,
        Trie::Node& node,
        const string& current
    ) {
        char character = board[row][column];
        int index = character - 'a';

        if (!node.children[index]) {
            return;
        }

        Trie::Node& child = *node.children[index];

        string word = current + character;

        if (child.terminal) {
            found.insert(word);
            child.terminal = false;
            child.frequency = 0;
        }

        board[row][column] = '#';

        for (const auto& [dr, dc] : directions) {
            int nr = row + dr;
            int nc = column + dc;

            if (
                nr >= 0 &&
                nr < rows &&
                nc >= 0 &&
                nc < columns &&
                board[nr][nc] != '#'
            ) {
                dfs(nr, nc, child, word);
            }
        }

        board[row][column] = character;
    }

public:
    vector<string> findWords(
        const vector<vector<char>>& inputBoard,
        const vector<string>& words
    ) {
        if (inputBoard.empty()) {
            return {};
        }

        rows = static_cast<int>(inputBoard.size());
        columns = static_cast<int>(inputBoard[0].size());

        if (columns == 0) {
            throw invalid_argument("Board cannot have empty rows.");
        }

        board = inputBoard;
        found.clear();

        for (const auto& row : board) {
            if (static_cast<int>(row.size()) != columns) {
                throw invalid_argument("Board must be rectangular.");
            }

            for (char character : row) {
                if (
                    !isalpha(static_cast<unsigned char>(character)) ||
                    character > 127
                ) {
                    throw invalid_argument(
                        "Board cells must contain alphabetic characters."
                    );
                }
            }
        }

        for (auto& row : board) {
            for (char& character : row) {
                character = static_cast<char>(
                    tolower(static_cast<unsigned char>(character))
                );
            }
        }

        Trie trie;

        for (const string& word : words) {
            trie.insert(word);
        }

        for (int row = 0; row < rows; ++row) {
            for (int column = 0; column < columns; ++column) {
                dfs(row, column, trie.root, "");
            }
        }

        vector<string> results(found.begin(), found.end());

        sort(results.begin(), results.end());

        return results;
    }
};

void printSuggestions(const vector<Trie::Suggestion>& suggestions) {
    for (const auto& suggestion : suggestions) {
        cout << "  " << suggestion.word
             << " (frequency: " << suggestion.frequency << ")\n";
    }
}

void runTests() {
    Trie trie;

    for (const string& word : {
        "apple", "app", "application", "apply",
        "banana", "band", "bandana", "bat"
    }) {
        trie.insert(word);
    }

    trie.insert("apple", 5);

    if (!trie.search("apple")) {
        throw runtime_error("Exact search test failed.");
    }

    if (trie.search("appl")) {
        throw runtime_error("Prefix incorrectly matched as a word.");
    }

    if (!trie.startsWith("app")) {
        throw runtime_error("Prefix search test failed.");
    }

    if (trie.autocomplete("app", 1).front().word != "apple") {
        throw runtime_error("Autocomplete ranking test failed.");
    }

    if (!trie.erase("app") || trie.search("app")) {
        throw runtime_error("Deletion test failed.");
    }

    if (!trie.search("apple")) {
        throw runtime_error("Deletion damaged another word.");
    }

    if (trie.wildcardSearch("app..").size() != 1) {
        throw runtime_error("Wildcard search test failed.");
    }

    Trie dictionary;

    for (const string& word : {
        "cat", "cats", "and", "sand", "dog"
    }) {
        dictionary.insert(word);
    }

    if (!wordBreak("catsanddog", dictionary)) {
        throw runtime_error("Word Break test failed.");
    }

    if (wordBreak("catsandxyz", dictionary)) {
        throw runtime_error("Invalid Word Break result.");
    }

    const auto sentences = wordBreakSentences(
        "catsanddog",
        dictionary
    );

    if (sentences.size() != 2) {
        throw runtime_error("Sentence generation test failed.");
    }

    WordSearch search;

    auto results = search.findWords(
        {
            {'o', 'a', 'a', 'n'},
            {'e', 't', 'a', 'e'},
            {'i', 'h', 'k', 'r'},
            {'i', 'f', 'l', 'v'}
        },
        {"oath", "pea", "eat", "rain"}
    );

    if (results != vector<string>{"eat", "oath"}) {
        throw runtime_error("Word Search test failed.");
    }

    bool rejected = false;

    try {
        trie.insert("word123");
    } catch (const invalid_argument&) {
        rejected = true;
    }

    if (!rejected) {
        throw runtime_error("Input validation test failed.");
    }

    cout << "\nAll C++17 tests passed.\n";
}

int main() {
    try {
        cout << "TRIE APPLICATIONS - C++17\n";
        cout << "==============================\n";

        Trie trie;

        for (const string& word : {
            "apple", "app", "application", "apply",
            "apt", "banana", "band", "bandana",
            "bat", "ball"
        }) {
            trie.insert(word);
        }

        trie.insert("apple", 10);
        trie.insert("application", 4);

        cout << "\nDictionary size: " << trie.size() << '\n';

        cout << "\nAutocomplete for 'app':\n";
        printSuggestions(trie.autocomplete("app", 5));

        cout << "\nExact search: "
             << boolalpha << trie.search("apple") << '\n';

        cout << "Prefix search: "
             << trie.startsWith("app") << '\n';

        cout << "\nWildcard search for 'app..':\n";

        for (const string& word : trie.wildcardSearch("app..")) {
            cout << "  " << word << '\n';
        }

        cout << "\nLongest prefix: "
             << trie.longestPrefix("application") << '\n';

        Trie dictionary;

        for (const string& word : {
            "cat", "cats", "and", "sand", "dog"
        }) {
            dictionary.insert(word);
        }

        cout << "\nWord Break: "
             << wordBreak("catsanddog", dictionary) << '\n';

        cout << "\nWord Break sentences:\n";

        for (const string& sentence :
             wordBreakSentences("catsanddog", dictionary)) {
            cout << "  " << sentence << '\n';
        }

        WordSearch search;

        cout << "\nWord Search II:\n";

        const auto matches = search.findWords(
            {
                {'o', 'a', 'a', 'n'},
                {'e', 't', 'a', 'e'},
                {'i', 'h', 'k', 'r'},
                {'i', 'f', 'l', 'v'}
            },
            {"oath", "pea", "eat", "rain"}
        );

        for (const string& word : matches) {
            cout << "  " << word << '\n';
        }

        cout << "\nRunning tests...\n";
        runTests();

    } catch (const exception& error) {
        cerr << "Error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
