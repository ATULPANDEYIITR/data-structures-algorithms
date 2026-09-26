/*
STRING PATTERN PROBLEMS: C++ CASE STUDY
=======================================

Industry-style case study:
A document similarity and text-processing engine.

The program models a service that receives documents and provides:

1. Input validation and normalization
2. Character statistics
3. Duplicate and unique-character analysis
4. Palindrome detection
5. Anagram detection
6. Exact substring search
7. KMP pattern matching
8. Sliding-window analysis
9. Longest common subsequence
10. Edit distance
11. Document similarity
12. Word-frequency indexing
13. Prefix search using a Trie
14. Run-length compression
15. Validation and error handling
16. Complexity-aware design

Compile:
    g++ -std=c++17 -O2 -Wall -Wextra -pedantic string_pattern_case_study.cpp -o string_patterns

Run:
    ./string_patterns
*/

#include <algorithm>
#include <cctype>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

using namespace std;

// ============================================================================
// 1. UTILITY FUNCTIONS
// ============================================================================

string toLowerAscii(string text) {
    for (char& character : text) {
        character = static_cast<char>(
            tolower(static_cast<unsigned char>(character))
        );
    }

    return text;
}

string normalizeAlphanumeric(string text) {
    string result;

    for (char character : text) {
        unsigned char value = static_cast<unsigned char>(character);

        if (isalnum(value)) {
            result += static_cast<char>(tolower(value));
        }
    }

    return result;
}

vector<string> splitWords(const string& text) {
    vector<string> words;
    string word;
    stringstream stream(text);

    while (stream >> word) {
        words.push_back(toLowerAscii(word));
    }

    return words;
}

// ============================================================================
// 2. CHARACTER FREQUENCY INDEX
// ============================================================================

class CharacterFrequencyIndex {
private:
    unordered_map<char, size_t> frequencies;

public:
    explicit CharacterFrequencyIndex(const string& text) {
        for (char character : text) {
            ++frequencies[character];
        }
    }

    size_t frequency(char character) const {
        auto iterator = frequencies.find(character);

        if (iterator == frequencies.end()) {
            return 0;
        }

        return iterator->second;
    }

    char firstNonRepeating(const string& text) const {
        for (char character : text) {
            if (frequency(character) == 1) {
                return character;
            }
        }

        return '\0';
    }

    char firstRepeating(const string& text) const {
        unordered_set<char> seen;

        for (char character : text) {
            if (seen.contains(character)) {
                return character;
            }

            seen.insert(character);
        }

        return '\0';
    }

    void print() const {
        vector<pair<char, size_t>> entries(
            frequencies.begin(),
            frequencies.end()
        );

        sort(
            entries.begin(),
            entries.end(),
            [](const auto& first, const auto& second) {
                return first.first < second.first;
            }
        );

        for (const auto& [character, count] : entries) {
            if (character == ' ') {
                cout << "[space] = " << count << '\n';
            } else {
                cout << character << " = " << count << '\n';
            }
        }
    }
};

// ============================================================================
// 3. PALINDROME ANALYSIS
// ============================================================================

bool isPalindromeTwoPointer(const string& text) {
    if (text.empty()) {
        return true;
    }

    size_t left = 0;
    size_t right = text.size() - 1;

    while (left < right) {
        if (text[left] != text[right]) {
            return false;
        }

        ++left;
        --right;
    }

    return true;
}

bool isNormalizedPalindrome(const string& text) {
    return isPalindromeTwoPointer(normalizeAlphanumeric(text));
}

string longestPalindromicSubstring(const string& text) {
    if (text.empty()) {
        return "";
    }

    size_t bestStart = 0;
    size_t bestLength = 1;

    auto expand = [&](long long left, long long right) {
        while (
            left >= 0 &&
            right < static_cast<long long>(text.size()) &&
            text[static_cast<size_t>(left)] ==
                text[static_cast<size_t>(right)]
        ) {
            --left;
            ++right;
        }

        size_t start = static_cast<size_t>(left + 1);
        size_t length = static_cast<size_t>(right - left - 1);

        if (length > bestLength) {
            bestStart = start;
            bestLength = length;
        }
    };

    for (size_t center = 0; center < text.size(); ++center) {
        expand(
            static_cast<long long>(center),
            static_cast<long long>(center)
        );

        expand(
            static_cast<long long>(center),
            static_cast<long long>(center + 1)
        );
    }

    return text.substr(bestStart, bestLength);
}

// ============================================================================
// 4. ANAGRAM ANALYSIS
// ============================================================================

bool areAnagrams(const string& first, const string& second) {
    if (first.size() != second.size()) {
        return false;
    }

    unordered_map<char, int> frequencies;

    for (char character : first) {
        ++frequencies[character];
    }

    for (char character : second) {
        auto iterator = frequencies.find(character);

        if (iterator == frequencies.end()) {
            return false;
        }

        --iterator->second;

        if (iterator->second < 0) {
            return false;
        }
    }

    return true;
}

bool areAnagramsIgnoringCase(const string& first, const string& second) {
    return areAnagrams(toLowerAscii(first), toLowerAscii(second));
}

// ============================================================================
// 5. NAIVE AND KMP PATTERN SEARCH
// ============================================================================

int naiveSearch(const string& text, const string& pattern) {
    if (pattern.empty()) {
        return 0;
    }

    if (pattern.size() > text.size()) {
        return -1;
    }

    for (size_t start = 0;
         start + pattern.size() <= text.size();
         ++start) {

        bool matched = true;

        for (size_t offset = 0; offset < pattern.size(); ++offset) {
            if (text[start + offset] != pattern[offset]) {
                matched = false;
                break;
            }
        }

        if (matched) {
            return static_cast<int>(start);
        }
    }

    return -1;
}

vector<int> buildLPS(const string& pattern) {
    vector<int> lps(pattern.size(), 0);

    int prefixLength = 0;
    size_t index = 1;

    while (index < pattern.size()) {
        if (pattern[index] == pattern[static_cast<size_t>(prefixLength)]) {
            ++prefixLength;
            lps[index] = prefixLength;
            ++index;
        } else if (prefixLength > 0) {
            prefixLength =
                lps[static_cast<size_t>(prefixLength - 1)];
        } else {
            lps[index] = 0;
            ++index;
        }
    }

    return lps;
}

int kmpSearch(const string& text, const string& pattern) {
    if (pattern.empty()) {
        return 0;
    }

    const vector<int> lps = buildLPS(pattern);

    size_t textIndex = 0;
    size_t patternIndex = 0;

    while (textIndex < text.size()) {
        if (text[textIndex] == pattern[patternIndex]) {
            ++textIndex;
            ++patternIndex;

            if (patternIndex == pattern.size()) {
                return static_cast<int>(
                    textIndex - patternIndex
                );
            }
        } else if (patternIndex > 0) {
            patternIndex =
                static_cast<size_t>(
                    lps[patternIndex - 1]
                );
        } else {
            ++textIndex;
        }
    }

    return -1;
}

// ============================================================================
// 6. SLIDING WINDOW
// ============================================================================

string longestSubstringWithoutRepeating(const string& text) {
    unordered_map<char, size_t> lastSeen;

    size_t left = 0;
    size_t bestStart = 0;
    size_t bestLength = 0;

    for (size_t right = 0; right < text.size(); ++right) {
        char character = text[right];

        auto iterator = lastSeen.find(character);

        if (iterator != lastSeen.end() && iterator->second >= left) {
            left = iterator->second + 1;
        }

        lastSeen[character] = right;

        size_t currentLength = right - left + 1;

        if (currentLength > bestLength) {
            bestStart = left;
            bestLength = currentLength;
        }
    }

    return text.substr(bestStart, bestLength);
}

string minimumWindowSubstring(
    const string& text,
    const string& target
) {
    if (target.empty()) {
        return "";
    }

    unordered_map<char, int> required;

    for (char character : target) {
        ++required[character];
    }

    size_t left = 0;
    size_t bestStart = 0;
    size_t bestLength = numeric_limits<size_t>::max();
    size_t remaining = target.size();

    for (size_t right = 0; right < text.size(); ++right) {
        char character = text[right];

        auto iterator = required.find(character);

        if (iterator != required.end()) {
            if (iterator->second > 0) {
                --remaining;
            }

            --iterator->second;
        }

        while (remaining == 0) {
            size_t currentLength = right - left + 1;

            if (currentLength < bestLength) {
                bestLength = currentLength;
                bestStart = left;
            }

            char leftCharacter = text[left];
            auto leftIterator = required.find(leftCharacter);

            if (leftIterator != required.end()) {
                ++leftIterator->second;

                if (leftIterator->second > 0) {
                    ++remaining;
                }
            }

            ++left;
        }
    }

    if (bestLength == numeric_limits<size_t>::max()) {
        return "";
    }

    return text.substr(bestStart, bestLength);
}

// ============================================================================
// 7. SUBSEQUENCE ANALYSIS
// ============================================================================

bool isSubsequence(
    const string& candidate,
    const string& source
) {
    size_t candidateIndex = 0;

    for (char character : source) {
        if (
            candidateIndex < candidate.size() &&
            character == candidate[candidateIndex]
        ) {
            ++candidateIndex;
        }
    }

    return candidateIndex == candidate.size();
}

size_t countSubsequenceOccurrences(
    const string& source,
    const string& target
) {
    vector<unsigned long long> dp(target.size() + 1, 0);
    dp[0] = 1;

    for (char sourceCharacter : source) {
        for (size_t targetIndex = target.size();
             targetIndex > 0;
             --targetIndex) {

            if (
                sourceCharacter ==
                target[targetIndex - 1]
            ) {
                dp[targetIndex] += dp[targetIndex - 1];
            }
        }
    }

    return static_cast<size_t>(dp[target.size()]);
}

// ============================================================================
// 8. LONGEST COMMON SUBSEQUENCE
// ============================================================================

string longestCommonSubsequence(
    const string& first,
    const string& second
) {
    const size_t rows = first.size() + 1;
    const size_t columns = second.size() + 1;

    vector<vector<string>> dp(
        rows,
        vector<string>(columns)
    );

    for (size_t i = 1; i < rows; ++i) {
        for (size_t j = 1; j < columns; ++j) {
            if (first[i - 1] == second[j - 1]) {
                dp[i][j] =
                    dp[i - 1][j - 1] +
                    first[i - 1];
            } else {
                const string& upper = dp[i - 1][j];
                const string& left = dp[i][j - 1];

                dp[i][j] =
                    upper.size() >= left.size()
                        ? upper
                        : left;
            }
        }
    }

    return dp[rows - 1][columns - 1];
}

size_t lcsLengthOptimized(
    const string& first,
    const string& second
) {
    const string* larger = &first;
    const string* smaller = &second;

    if (first.size() < second.size()) {
        larger = &second;
        smaller = &first;
    }

    vector<size_t> previous(smaller->size() + 1, 0);

    for (char character : *larger) {
        vector<size_t> current(smaller->size() + 1, 0);

        for (size_t j = 1; j <= smaller->size(); ++j) {
            if (character == (*smaller)[j - 1]) {
                current[j] = previous[j - 1] + 1;
            } else {
                current[j] =
                    max(previous[j], current[j - 1]);
            }
        }

        previous = move(current);
    }

    return previous.back();
}

// ============================================================================
// 9. EDIT DISTANCE
// ============================================================================

size_t levenshteinDistance(
    const string& first,
    const string& second
) {
    const string* larger = &first;
    const string* smaller = &second;

    if (first.size() < second.size()) {
        larger = &second;
        smaller = &first;
    }

    vector<size_t> previous(smaller->size() + 1);

    iota(previous.begin(), previous.end(), 0);

    for (size_t i = 1; i <= larger->size(); ++i) {
        vector<size_t> current(smaller->size() + 1);
        current[0] = i;

        for (size_t j = 1; j <= smaller->size(); ++j) {
            size_t insertion = current[j - 1] + 1;
            size_t deletion = previous[j] + 1;
            size_t substitution =
                previous[j - 1] +
                ((*larger)[i - 1] != (*smaller)[j - 1]);

            current[j] =
                min({insertion, deletion, substitution});
        }

        previous = move(current);
    }

    return previous.back();
}

// ============================================================================
// 10. WORD FREQUENCY INDEX
// ============================================================================

class WordIndex {
private:
    unordered_map<string, size_t> frequencies;

public:
    explicit WordIndex(const string& document) {
        for (const string& word : splitWords(document)) {
            ++frequencies[word];
        }
    }

    size_t frequency(const string& word) const {
        auto iterator = frequencies.find(toLowerAscii(word));

        if (iterator == frequencies.end()) {
            return 0;
        }

        return iterator->second;
    }

    vector<pair<string, size_t>> mostFrequent(
        size_t limit
    ) const {
        vector<pair<string, size_t>> entries(
            frequencies.begin(),
            frequencies.end()
        );

        sort(
            entries.begin(),
            entries.end(),
            [](const auto& first, const auto& second) {
                if (first.second != second.second) {
                    return first.second > second.second;
                }

                return first.first < second.first;
            }
        );

        if (entries.size() > limit) {
            entries.resize(limit);
        }

        return entries;
    }
};

// ============================================================================
// 11. TRIE FOR PREFIX SEARCH
// ============================================================================

class Trie {
private:
    struct Node {
        map<char, unique_ptr<Node>> children;
        bool isWord = false;
    };

    unique_ptr<Node> root = make_unique<Node>();

    void collect(
        const Node* node,
        const string& prefix,
        vector<string>& results
    ) const {
        if (node->isWord) {
            results.push_back(prefix);
        }

        for (const auto& [character, child] : node->children) {
            collect(
                child.get(),
                prefix + character,
                results
            );
        }
    }

public:
    void insert(const string& word) {
        Node* current = root.get();

        for (char character : word) {
            if (!current->children.contains(character)) {
                current->children[character] =
                    make_unique<Node>();
            }

            current = current->children[character].get();
        }

        current->isWord = true;
    }

    bool contains(const string& word) const {
        const Node* current = root.get();

        for (char character : word) {
            auto iterator = current->children.find(character);

            if (iterator == current->children.end()) {
                return false;
            }

            current = iterator->second.get();
        }

        return current->isWord;
    }

    vector<string> wordsWithPrefix(
        const string& prefix
    ) const {
        const Node* current = root.get();

        for (char character : prefix) {
            auto iterator = current->children.find(character);

            if (iterator == current->children.end()) {
                return {};
            }

            current = iterator->second.get();
        }

        vector<string> results;
        collect(current, prefix, results);
        return results;
    }
};

// ============================================================================
// 12. DOCUMENT SIMILARITY ENGINE
// ============================================================================

struct DocumentAnalysis {
    string name;
    size_t characterCount = 0;
    size_t wordCount = 0;
    size_t uniqueWordCount = 0;
    string longestPalindrome;
    string longestUniqueSubstring;
};

class DocumentSimilarityEngine {
public:
    static DocumentAnalysis analyze(
        const string& name,
        const string& document
    ) {
        vector<string> words = splitWords(document);

        unordered_set<string> uniqueWords(
            words.begin(),
            words.end()
        );

        return {
            name,
            document.size(),
            words.size(),
            uniqueWords.size(),
            longestPalindromicSubstring(
                normalizeAlphanumeric(document)
            ),
            longestSubstringWithoutRepeating(document)
        };
    }

    static double lcsSimilarity(
        const string& first,
        const string& second
    ) {
        const size_t firstLength = first.size();
        const size_t secondLength = second.size();

        if (firstLength == 0 && secondLength == 0) {
            return 1.0;
        }

        const size_t lcs =
            lcsLengthOptimized(first, second);

        return static_cast<double>(lcs) /
            static_cast<double>(
                max(firstLength, secondLength)
            );
    }

    static double editSimilarity(
        const string& first,
        const string& second
    ) {
        const size_t maximumLength =
            max(first.size(), second.size());

        if (maximumLength == 0) {
            return 1.0;
        }

        const size_t distance =
            levenshteinDistance(first, second);

        if (distance >= maximumLength) {
            return 0.0;
        }

        return 1.0 -
            static_cast<double>(distance) /
            static_cast<double>(maximumLength);
    }
};

// ============================================================================
// 13. RUN-LENGTH ENCODING
// ============================================================================

string compressRunLength(const string& text) {
    if (text.empty()) {
        return "";
    }

    string encoded;
    size_t count = 1;

    for (size_t index = 1; index <= text.size(); ++index) {
        if (
            index < text.size() &&
            text[index] == text[index - 1]
        ) {
            ++count;
        } else {
            encoded += text[index - 1];
            encoded += to_string(count);
            count = 1;
        }
    }

    return encoded;
}

string decompressRunLength(const string& encoded) {
    string result;
    size_t index = 0;

    while (index < encoded.size()) {
        char character = encoded[index++];

        if (
            index >= encoded.size() ||
            !isdigit(
                static_cast<unsigned char>(encoded[index])
            )
        ) {
            throw invalid_argument(
                "Invalid run-length encoding"
            );
        }

        size_t count = 0;

        while (
            index < encoded.size() &&
            isdigit(
                static_cast<unsigned char>(encoded[index])
            )
        ) {
            const int digit =
                encoded[index] - '0';

            if (
                count >
                (numeric_limits<size_t>::max() -
                 static_cast<size_t>(digit)) / 10
            ) {
                throw overflow_error(
                    "Run length is too large"
                );
            }

            count = count * 10 +
                static_cast<size_t>(digit);

            ++index;
        }

        if (
            count >
            numeric_limits<size_t>::max() -
            result.size()
        ) {
            throw overflow_error(
                "Decoded output would be too large"
            );
        }

        result.append(count, character);
    }

    return result;
}

// ============================================================================
// 14. VALIDATION
// ============================================================================

bool isValidInteger(const string& text) {
    if (text.empty()) {
        return false;
    }

    size_t start = 0;

    if (text[0] == '+' || text[0] == '-') {
        start = 1;
    }

    if (start == text.size()) {
        return false;
    }

    for (size_t index = start; index < text.size(); ++index) {
        if (
            !isdigit(
                static_cast<unsigned char>(text[index])
            )
        ) {
            return false;
        }
    }

    return true;
}

// ============================================================================
// 15. OUTPUT HELPERS
// ============================================================================

void printHeader(const string& title) {
    cout << "\n========================================\n";
    cout << title << '\n';
    cout << "========================================\n";
}

void printDocumentAnalysis(
    const DocumentAnalysis& analysis
) {
    cout << "Document: " << analysis.name << '\n';
    cout << "Characters: " << analysis.characterCount << '\n';
    cout << "Words: " << analysis.wordCount << '\n';
    cout << "Unique words: " << analysis.uniqueWordCount << '\n';
    cout << "Longest palindrome: "
         << analysis.longestPalindrome << '\n';
    cout << "Longest unique substring: "
         << analysis.longestUniqueSubstring << '\n';
}

// ============================================================================
// 16. TESTS
// ============================================================================

void runTests() {
    if (!isPalindromeTwoPointer("racecar")) {
        throw runtime_error("Palindrome test failed");
    }

    if (isPalindromeTwoPointer("hello")) {
        throw runtime_error("Non-palindrome test failed");
    }

    if (
        !isNormalizedPalindrome(
            "A man, a plan, a canal: Panama"
        )
    ) {
        throw runtime_error(
            "Normalized palindrome test failed"
        );
    }

    if (
        !areAnagramsIgnoringCase(
            "Listen",
            "Silent"
        )
    ) {
        throw runtime_error("Anagram test failed");
    }

    if (
        naiveSearch("hello world", "world") != 6
    ) {
        throw runtime_error("Naive search test failed");
    }

    if (
        kmpSearch(
            "ababcabcabababd",
            "ababd"
        ) != 10
    ) {
        throw runtime_error("KMP test failed");
    }

    if (
        !isSubsequence("ace", "abcde")
    ) {
        throw runtime_error("Subsequence test failed");
    }

    if (
        isSubsequence("aec", "abcde")
    ) {
        throw runtime_error(
            "Invalid subsequence test failed"
        );
    }

    if (
        countSubsequenceOccurrences(
            "babgbag",
            "bag"
        ) != 5
    ) {
        throw runtime_error(
            "Subsequence counting test failed"
        );
    }

    if (
        longestCommonSubsequence(
            "abcde",
            "ace"
        ) != "ace"
    ) {
        throw runtime_error("LCS test failed");
    }

    if (
        levenshteinDistance(
            "kitten",
            "sitting"
        ) != 3
    ) {
        throw runtime_error(
            "Edit distance test failed"
        );
    }

    if (
        longestSubstringWithoutRepeating(
            "abcabcbb"
        ) != "abc"
    ) {
        throw runtime_error(
            "Sliding window test failed"
        );
    }

    if (
        minimumWindowSubstring(
            "ADOBECODEBANC",
            "ABC"
        ) != "BANC"
    ) {
        throw runtime_error(
            "Minimum window test failed"
        );
    }

    string original = "aaabccccdd";
    string compressed = compressRunLength(original);
    string restored = decompressRunLength(compressed);

    if (original != restored) {
        throw runtime_error(
            "Compression round-trip test failed"
        );
    }

    Trie trie;

    for (const string& word :
         vector<string>{"apple", "app", "apply"}) {
        trie.insert(word);
    }

    if (!trie.contains("apple")) {
        throw runtime_error(
            "Trie contains test failed"
        );
    }

    if (trie.contains("apples")) {
        throw runtime_error(
            "Trie negative test failed"
        );
    }

    cout << "All C++ tests passed.\n";
}

// ============================================================================
// 17. MAIN CASE STUDY
// ============================================================================

int main() {
    try {
        printHeader("STRING PATTERN CASE STUDY");

        const string documentA =
            "Algorithms transform data into useful information. "
            "String algorithms transform text into searchable information.";

        const string documentB =
            "Efficient algorithms process text and data. "
            "String processing supports search, validation, and analysis.";

        // --------------------------------------------------------------------
        // Character analysis
        // --------------------------------------------------------------------
        printHeader("1. CHARACTER FREQUENCY");

        CharacterFrequencyIndex frequencyIndex(documentA);

        frequencyIndex.print();

        char firstUnique =
            frequencyIndex.firstNonRepeating(documentA);

        char firstRepeated =
            frequencyIndex.firstRepeating(documentA);

        cout << "First non-repeating: "
             << (firstUnique == '\0' ? "none" :
                 string(1, firstUnique))
             << '\n';

        cout << "First repeating: "
             << (firstRepeated == '\0' ? "none" :
                 string(1, firstRepeated))
             << '\n';

        // --------------------------------------------------------------------
        // Palindrome
        // --------------------------------------------------------------------
        printHeader("2. PALINDROME ANALYSIS");

        const string palindromeCandidate =
            "A man, a plan, a canal: Panama";

        cout << palindromeCandidate << '\n';
        cout << "Normalized palindrome: "
             << boolalpha
             << isNormalizedPalindrome(
                    palindromeCandidate
                )
             << '\n';

        cout << "Longest palindromic substring: "
             << longestPalindromicSubstring(
                    "forgeeksskeegfor"
                )
             << '\n';

        // --------------------------------------------------------------------
        // Anagram
        // --------------------------------------------------------------------
        printHeader("3. ANAGRAM ANALYSIS");

        cout << "listen / silent: "
             << areAnagramsIgnoringCase(
                    "listen",
                    "silent"
                )
             << '\n';

        cout << "triangle / integral: "
             << areAnagramsIgnoringCase(
                    "triangle",
                    "integral"
                )
             << '\n';

        // --------------------------------------------------------------------
        // Exact pattern search
        // --------------------------------------------------------------------
        printHeader("4. PATTERN SEARCH");

        const string searchText =
            "ababcabcabababd";

        const string searchPattern =
            "ababd";

        cout << "Naive result: "
             << naiveSearch(
                    searchText,
                    searchPattern
                )
             << '\n';

        cout << "KMP result: "
             << kmpSearch(
                    searchText,
                    searchPattern
                )
             << '\n';

        cout << "KMP LPS table: ";

        for (int value :
             buildLPS("ababaca")) {
            cout << value << ' ';
        }

        cout << '\n';

        // --------------------------------------------------------------------
        // Sliding window
        // --------------------------------------------------------------------
        printHeader("5. SLIDING WINDOW");

        cout << "Longest unique substring: "
             << longestSubstringWithoutRepeating(
                    "pwwkew"
                )
             << '\n';

        cout << "Minimum window containing ABC: "
             << minimumWindowSubstring(
                    "ADOBECODEBANC",
                    "ABC"
                )
             << '\n';

        // --------------------------------------------------------------------
        // Subsequences
        // --------------------------------------------------------------------
        printHeader("6. SUBSEQUENCES");

        cout << "'ace' is subsequence of 'abcde': "
             << isSubsequence(
                    "ace",
                    "abcde"
                )
             << '\n';

        cout << "Number of 'bag' subsequences: "
             << countSubsequenceOccurrences(
                    "babgbag",
                    "bag"
                )
             << '\n';

        // --------------------------------------------------------------------
        // Dynamic programming
        // --------------------------------------------------------------------
        printHeader("7. DYNAMIC PROGRAMMING");

        const string first =
            "AGGTAB";

        const string second =
            "GXTXAYB";

        cout << "LCS: "
             << longestCommonSubsequence(
                    first,
                    second
                )
             << '\n';

        cout << "LCS length: "
             << lcsLengthOptimized(
                    first,
                    second
                )
             << '\n';

        cout << "Edit distance kitten/sitting: "
             << levenshteinDistance(
                    "kitten",
                    "sitting"
                )
             << '\n';

        // --------------------------------------------------------------------
        // Word index
        // --------------------------------------------------------------------
        printHeader("8. WORD FREQUENCY INDEX");

        WordIndex wordIndex(documentA);

        cout << "Frequency of 'string': "
             << wordIndex.frequency("string")
             << '\n';

        cout << "Most frequent words:\n";

        for (const auto& [word, count] :
             wordIndex.mostFrequent(5)) {
            cout << "  " << word << " -> "
                 << count << '\n';
        }

        // --------------------------------------------------------------------
        // Trie
        // --------------------------------------------------------------------
        printHeader("9. PREFIX SEARCH");

        Trie dictionary;

        for (const string& word :
             vector<string>{
                 "car",
                 "card",
                 "care",
                 "career",
                 "cat",
                 "catalog",
                 "carbon"
             }) {
            dictionary.insert(word);
        }

        cout << "Words beginning with 'car':\n";

        for (const string& word :
             dictionary.wordsWithPrefix("car")) {
            cout << "  " << word << '\n';
        }

        // --------------------------------------------------------------------
        // Compression
        // --------------------------------------------------------------------
        printHeader("10. STRING TRANSFORMATION");

        const string repeatedText =
            "aaabbbbbccccccdd";

        const string encoded =
            compressRunLength(repeatedText);

        const string decoded =
            decompressRunLength(encoded);

        cout << "Original: "
             << repeatedText << '\n';

        cout << "Encoded: "
             << encoded << '\n';

        cout << "Decoded: "
             << decoded << '\n';

        // --------------------------------------------------------------------
        // Document analysis
        // --------------------------------------------------------------------
        printHeader("11. DOCUMENT ANALYSIS");

        DocumentAnalysis analysisA =
            DocumentSimilarityEngine::analyze(
                "Document A",
                documentA
            );

        DocumentAnalysis analysisB =
            DocumentSimilarityEngine::analyze(
                "Document B",
                documentB
            );

        printDocumentAnalysis(analysisA);
        cout << '\n';
        printDocumentAnalysis(analysisB);

        // --------------------------------------------------------------------
        // Similarity
        // --------------------------------------------------------------------
        printHeader("12. DOCUMENT SIMILARITY");

        double lcsSimilarity =
            DocumentSimilarityEngine::lcsSimilarity(
                documentA,
                documentB
            );

        double editSimilarity =
            DocumentSimilarityEngine::editSimilarity(
                documentA,
                documentB
            );

        cout << fixed << setprecision(4);

        cout << "LCS-based similarity: "
             << lcsSimilarity << '\n';

        cout << "Edit-distance similarity: "
             << editSimilarity << '\n';

        /*
         * These scores are descriptive metrics, not proof of semantic
         * similarity. Character-level methods can miss synonyms,
         * paraphrases, word order changes, and language-specific meaning.
         */

        // --------------------------------------------------------------------
        // Validation
        // --------------------------------------------------------------------
        printHeader("13. VALIDATION");

        for (const string& candidate :
             vector<string>{"123", "-42", "+8", "", "+"}) {
            cout << quoted(candidate)
                 << " -> "
                 << isValidInteger(candidate)
                 << '\n';
        }

        // --------------------------------------------------------------------
        // Edge cases
        // --------------------------------------------------------------------
        printHeader("14. EDGE CASES");

        cout << "Empty palindrome: "
             << isPalindromeTwoPointer("")
             << '\n';

        cout << "Empty pattern search: "
             << naiveSearch("abc", "")
             << '\n';

        cout << "Empty subsequence: "
             << isSubsequence("", "abc")
             << '\n';

        cout << "Missing minimum window: "
             << quoted(
                    minimumWindowSubstring(
                        "abc",
                        "xyz"
                    )
                )
             << '\n';

        cout << "Empty LCS: "
             << quoted(
                    longestCommonSubsequence(
                        "",
                        "abc"
                    )
                )
             << '\n';

        // --------------------------------------------------------------------
        // Automated verification
        // --------------------------------------------------------------------
        printHeader("15. TESTING");

        runTests();

        // --------------------------------------------------------------------
        // Complexity notes
        // --------------------------------------------------------------------
        printHeader("16. COMPLEXITY NOTES");

        cout << "Character frequency: O(n) average time, O(k) space\n";
        cout << "Palindrome two-pointer: O(n) time, O(1) extra space\n";
        cout << "Anagram frequency: O(n) average time, O(k) space\n";
        cout << "Naive search: O(n*m) worst case\n";
        cout << "KMP search: O(n+m)\n";
        cout << "Sliding-window unique substring: O(n) average time\n";
        cout << "LCS: O(n*m) time\n";
        cout << "Optimized LCS length: O(n*m) time, O(min(n,m)) space\n";
        cout << "Levenshtein distance: O(n*m) time, O(min(n,m)) space\n";
        cout << "Trie lookup: O(L), where L is the word length\n";

        /*
         * Production considerations:
         *
         * 1. std::string indexes bytes, not Unicode grapheme clusters.
         *    International text processing requires explicit Unicode
         *    handling when character-level correctness matters.
         *
         * 2. unordered_map and unordered_set provide average O(1) lookup,
         *    but worst-case behavior can degrade. Ordered map structures
         *    provide O(log n) guarantees and deterministic ordering.
         *
         * 3. Dynamic-programming matrices can become expensive for large
         *    documents. Memory-optimized versions should be preferred when
         *    only a length is required.
         *
         * 4. Character-level similarity is not semantic similarity.
         *
         * 5. Untrusted input must be bounded to prevent excessive memory,
         *    CPU consumption, or decompression amplification.
         *
         * 6. Run-length encoding is an educational transformation and is
         *    not suitable as a secure compression format.
         */

        cout << "\nCase study completed successfully.\n";
        return 0;
    }
    catch (const exception& error) {
        cerr << "Fatal error: "
             << error.what()
             << '\n';

        return 1;
    }
}
