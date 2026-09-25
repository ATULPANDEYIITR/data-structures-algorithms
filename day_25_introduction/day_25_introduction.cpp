/*
 * Strings Introduction - C++17 Case Study
 *
 * Case study:
 * A multilingual command-line log ingestion and analysis system.
 *
 * The program demonstrates:
 * - std::string
 * - characters and bytes
 * - ASCII
 * - UTF-8 byte representation
 * - traversal
 * - comparison
 * - searching
 * - manipulation
 * - validation
 * - regular expressions
 * - maps and vectors for text analysis
 * - parsing structured text
 * - normalization considerations
 * - error handling
 * - edge cases
 * - complexity analysis
 * - security considerations
 *
 * Compile:
 * g++ -std=c++17 -O2 -Wall -Wextra -pedantic strings_case_study.cpp -o strings_case_study
 */

#include <algorithm>
#include <cctype>
#include <iomanip>
#include <iostream>
#include <map>
#include <regex>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <unordered_map>
#include <utility>
#include <vector>

using namespace std;


// ============================================================================
// DISPLAY UTILITIES
// ============================================================================

void section(const string& title) {
    cout << "\n" << string(78, '=') << "\n";
    cout << title << "\n";
    cout << string(78, '=') << "\n";
}

void subsection(const string& title) {
    cout << "\n" << string(78, '-') << "\n";
    cout << title << "\n";
    cout << string(78, '-') << "\n";
}


// ============================================================================
// BASIC STRING OPERATIONS
// ============================================================================

void demonstrateBasicStrings() {
    subsection("1. Basic std::string operations");

    string singleQuotedConcept = "C++ uses double-quoted string literals.";
    string text = "Programming";

    cout << singleQuotedConcept << '\n';
    cout << "Text: " << text << '\n';
    cout << "Length in bytes: " << text.size() << '\n';
    cout << "First byte/character for ASCII text: " << text[0] << '\n';
    cout << "Last byte/character for ASCII text: "
         << text[text.size() - 1] << '\n';

    // std::string is mutable, unlike Python and JavaScript strings.
    text[0] = 'p';

    cout << "Modified mutable string: " << text << '\n';

    // at() performs bounds checking and throws std::out_of_range.
    try {
        cout << text.at(100) << '\n';
    } catch (const out_of_range& error) {
        cout << "Expected bounds error: " << error.what() << '\n';
    }
}


// ============================================================================
// ASCII
// ============================================================================

bool isAscii(string_view text) {
    for (unsigned char byte : text) {
        if (byte > 127) {
            return false;
        }
    }

    return true;
}

void demonstrateAscii() {
    subsection("2. ASCII");

    const vector<string> samples = {
        "Hello",
        "Hello123",
        "cafe",
        "café"
    };

    for (const string& value : samples) {
        cout << quoted(value)
             << " ASCII: "
             << boolalpha
             << isAscii(value)
             << '\n';
    }

    cout << "ASCII 'A' numeric value: "
         << static_cast<int>('A')
         << '\n';

    cout << "ASCII 'a' numeric value: "
         << static_cast<int>('a')
         << '\n';
}


// ============================================================================
// UTF-8 BYTE REPRESENTATION
// ============================================================================

string bytesToHex(string_view value) {
    ostringstream output;

    for (unsigned char byte : value) {
        output << hex
               << uppercase
               << setw(2)
               << setfill('0')
               << static_cast<int>(byte)
               << ' ';
    }

    return output.str();
}

void demonstrateUtf8() {
    subsection("3. UTF-8 byte representation");

    /*
     * std::string does not inherently mean Unicode text.
     * It is a sequence of bytes. UTF-8 is an encoding convention that
     * represents Unicode code points using one to four bytes.
     */

    const vector<string> samples = {
        "A",
        "é",
        "€",
        "中",
        "😀"
    };

    for (const string& value : samples) {
        cout << "Text: " << value << '\n';
        cout << "Byte length: " << value.size() << '\n';
        cout << "UTF-8 bytes: " << bytesToHex(value) << "\n\n";
    }
}


// ============================================================================
// UTF-8 DECODING
// ============================================================================

struct DecodedCodePoint {
    uint32_t value;
    size_t byteCount;
};

DecodedCodePoint decodeUtf8CodePoint(string_view text, size_t index) {
    if (index >= text.size()) {
        throw invalid_argument("UTF-8 index is outside the input.");
    }

    const unsigned char first =
        static_cast<unsigned char>(text[index]);

    if (first <= 0x7F) {
        return {first, 1};
    }

    if ((first & 0xE0) == 0xC0) {
        if (index + 1 >= text.size()) {
            throw invalid_argument("Truncated two-byte UTF-8 sequence.");
        }

        const unsigned char second =
            static_cast<unsigned char>(text[index + 1]);

        if ((second & 0xC0) != 0x80) {
            throw invalid_argument("Invalid UTF-8 continuation byte.");
        }

        const uint32_t codePoint =
            ((first & 0x1F) << 6) |
            (second & 0x3F);

        if (codePoint < 0x80) {
            throw invalid_argument("Overlong UTF-8 encoding.");
        }

        return {codePoint, 2};
    }

    if ((first & 0xF0) == 0xE0) {
        if (index + 2 >= text.size()) {
            throw invalid_argument("Truncated three-byte UTF-8 sequence.");
        }

        const unsigned char second =
            static_cast<unsigned char>(text[index + 1]);

        const unsigned char third =
            static_cast<unsigned char>(text[index + 2]);

        if ((second & 0xC0) != 0x80 ||
            (third & 0xC0) != 0x80) {
            throw invalid_argument("Invalid UTF-8 continuation byte.");
        }

        const uint32_t codePoint =
            ((first & 0x0F) << 12) |
            ((second & 0x3F) << 6) |
            (third & 0x3F);

        if (codePoint < 0x800) {
            throw invalid_argument("Overlong UTF-8 encoding.");
        }

        if (codePoint >= 0xD800 && codePoint <= 0xDFFF) {
            throw invalid_argument("UTF-8 cannot encode UTF-16 surrogates.");
        }

        return {codePoint, 3};
    }

    if ((first & 0xF8) == 0xF0) {
        if (index + 3 >= text.size()) {
            throw invalid_argument("Truncated four-byte UTF-8 sequence.");
        }

        const unsigned char second =
            static_cast<unsigned char>(text[index + 1]);

        const unsigned char third =
            static_cast<unsigned char>(text[index + 2]);

        const unsigned char fourth =
            static_cast<unsigned char>(text[index + 3]);

        if ((second & 0xC0) != 0x80 ||
            (third & 0xC0) != 0x80 ||
            (fourth & 0xC0) != 0x80) {
            throw invalid_argument("Invalid UTF-8 continuation byte.");
        }

        const uint32_t codePoint =
            ((first & 0x07) << 18) |
            ((second & 0x3F) << 12) |
            ((third & 0x3F) << 6) |
            (fourth & 0x3F);

        if (codePoint < 0x10000 || codePoint > 0x10FFFF) {
            throw invalid_argument("Invalid four-byte UTF-8 code point.");
        }

        return {codePoint, 4};
    }

    throw invalid_argument("Invalid UTF-8 leading byte.");
}

vector<uint32_t> decodeUtf8(string_view text) {
    vector<uint32_t> result;

    size_t index = 0;

    while (index < text.size()) {
        const DecodedCodePoint decoded =
            decodeUtf8CodePoint(text, index);

        result.push_back(decoded.value);
        index += decoded.byteCount;
    }

    return result;
}

void demonstrateUtf8Decoding() {
    subsection("3.1 UTF-8 decoding into Unicode code points");

    const string text = "Aé€中😀";

    try {
        const vector<uint32_t> codePoints = decodeUtf8(text);

        cout << "Text: " << text << '\n';
        cout << "Code-point count: " << codePoints.size() << '\n';

        cout << "Code points: ";

        for (uint32_t codePoint : codePoints) {
            cout << "U+"
                 << hex
                 << uppercase
                 << codePoint
                 << ' ';
        }

        cout << dec << '\n';
    } catch (const exception& error) {
        cout << "UTF-8 decoding failed: "
             << error.what()
             << '\n';
    }

    // Invalid UTF-8 demonstrates explicit failure handling.
    const string invalid = "\xFF\xFE";

    try {
        decodeUtf8(invalid);
    } catch (const exception& error) {
        cout << "Expected invalid UTF-8 error: "
             << error.what()
             << '\n';
    }
}


// ============================================================================
// TRAVERSAL
// ============================================================================

void demonstrateTraversal() {
    subsection("4. String traversal");

    const string text = "Python";

    cout << "Range-based traversal: ";

    for (char character : text) {
        cout << character << ' ';
    }

    cout << '\n';

    cout << "Indexed traversal: ";

    for (size_t index = 0; index < text.size(); ++index) {
        cout << '[' << index << ':' << text[index] << "] ";
    }

    cout << '\n';

    cout << "Reverse traversal: ";

    for (auto iterator = text.rbegin();
         iterator != text.rend();
         ++iterator) {
        cout << *iterator << ' ';
    }

    cout << '\n';
}


// ============================================================================
// COMPARISON
// ============================================================================

void demonstrateComparison() {
    subsection("5. String comparison");

    const string apple = "apple";
    const string banana = "banana";

    cout << boolalpha;
    cout << "apple == apple: "
         << (apple == "apple")
         << '\n';

    cout << "apple != banana: "
         << (apple != banana)
         << '\n';

    cout << "apple < banana: "
         << (apple < banana)
         << '\n';

    cout << "'A' < 'a': "
         << (string("A") < string("a"))
         << '\n';

    cout << dec;

    /*
     * std::string comparisons are lexicographic.
     * They do not automatically mean locale-aware human-language sorting.
     */
}


// ============================================================================
// SEARCHING
// ============================================================================

void demonstrateSearching() {
    subsection("6. Searching");

    const string text =
        "C++ is powerful and C++ is widely used.";

    cout << "find: "
         << text.find("C++")
         << '\n';

    cout << "rfind: "
         << text.rfind("C++")
         << '\n';

    cout << "find missing: "
         << text.find("Python")
         << " (npos means not found)\n";

    cout << "contains C++: "
         << (text.find("C++") != string::npos)
         << '\n';

    cout << "starts with C++: "
         << (text.rfind("C++", 0) == 0)
         << '\n';

    cout << "counting C++ manually:\n";

    size_t count = 0;
    size_t position = 0;

    while ((position = text.find("C++", position)) != string::npos) {
        ++count;
        position += 3;
    }

    cout << "Occurrences: " << count << '\n';
}


// ============================================================================
// MANIPULATION
// ============================================================================

void demonstrateManipulation() {
    subsection("7. Manipulation");

    string text = "  C++ Programming  ";

    cout << "Original: [" << text << "]\n";

    // std::string does not provide Python-style strip() directly.
    // We can use find_first_not_of/find_last_not_of.
    const size_t first = text.find_first_not_of(' ');
    const size_t last = text.find_last_not_of(' ');

    if (first != string::npos) {
        string trimmed = text.substr(first, last - first + 1);
        cout << "Trimmed: [" << trimmed << "]\n";
    }

    cout << "Substring: "
         << text.substr(2, 3)
         << '\n';

    text.replace(2, 3, "Advanced");
    cout << "After replace: " << text << '\n';

    text.append(" Language");
    cout << "After append: " << text << '\n';
}


// ============================================================================
// SPLITTING
// ============================================================================

vector<string> split(const string& text, char delimiter) {
    vector<string> parts;
    string current;

    for (char character : text) {
        if (character == delimiter) {
            parts.push_back(current);
            current.clear();
        } else {
            current.push_back(character);
        }
    }

    parts.push_back(current);

    return parts;
}

string join(const vector<string>& parts, string_view separator) {
    string result;

    for (size_t index = 0; index < parts.size(); ++index) {
        if (index > 0) {
            result += separator;
        }

        result += parts[index];
    }

    return result;
}

void demonstrateSplitJoin() {
    subsection("8. Split and join");

    const string csv = "Python,JavaScript,C++";

    const vector<string> languages = split(csv, ',');

    for (const string& language : languages) {
        cout << language << '\n';
    }

    cout << "Joined: "
         << join(languages, " | ")
         << '\n';
}


// ============================================================================
// VALIDATION
// ============================================================================

bool isValidUsername(const string& username, string& reason) {
    if (username.empty()) {
        reason = "Username cannot be empty.";
        return false;
    }

    if (username.size() < 3 || username.size() > 20) {
        reason = "Username must contain 3 to 20 ASCII characters.";
        return false;
    }

    if (!isAscii(username)) {
        reason = "Username must contain only ASCII characters.";
        return false;
    }

    const unsigned char first =
        static_cast<unsigned char>(username.front());

    if (!std::isalpha(first) && first != '_') {
        reason = "Username must start with a letter or underscore.";
        return false;
    }

    for (unsigned char character : username) {
        if (!std::isalnum(character) && character != '_') {
            reason = "Only letters, digits, and underscores are allowed.";
            return false;
        }
    }

    reason = "Valid username.";
    return true;
}

void demonstrateValidation() {
    subsection("9. Validation");

    const vector<string> candidates = {
        "atul_01",
        "",
        "ab",
        "1atul",
        "atul-pandey",
        "भारत"
    };

    for (const string& candidate : candidates) {
        string reason;
        const bool valid =
            isValidUsername(candidate, reason);

        cout << quoted(candidate)
             << " -> "
             << boolalpha
             << valid
             << " : "
             << reason
             << '\n';
    }
}


// ============================================================================
// REGULAR EXPRESSIONS
// ============================================================================

void demonstrateRegularExpressions() {
    subsection("10. Regular expressions");

    const string text =
        "Contact alice@example.com or bob@example.org.";

    const regex emailPattern(
        R"(\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b)"
    );

    auto begin = sregex_iterator(
        text.begin(),
        text.end(),
        emailPattern
    );

    auto end = sregex_iterator();

    for (auto iterator = begin; iterator != end; ++iterator) {
        cout << "Email: "
             << iterator->str()
             << '\n';
    }

    const regex identifierPattern(
        R"(^[A-Za-z_][A-Za-z0-9_]*$)"
    );

    for (const string& candidate :
         vector<string>{"name_1", "1name", "name-value", ""}) {

        cout << quoted(candidate)
             << " identifier: "
             << regex_match(candidate, identifierPattern)
             << '\n';
    }
}


// ============================================================================
// CHARACTER FREQUENCY
// ============================================================================

unordered_map<char, size_t> characterFrequency(string_view text) {
    unordered_map<char, size_t> counts;

    for (char character : text) {
        ++counts[character];
    }

    return counts;
}

optional<char> firstNonRepeatingCharacter(string_view text) {
    const auto counts = characterFrequency(text);

    for (char character : text) {
        auto iterator = counts.find(character);

        if (iterator != counts.end() &&
            iterator->second == 1) {
            return character;
        }
    }

    return nullopt;
}

void demonstrateFrequency() {
    subsection("11. Character frequency and first non-repeating character");

    const string text = "banana";
    const auto counts = characterFrequency(text);

    for (const auto& [character, count] : counts) {
        cout << character << ": " << count << '\n';
    }

    for (const string& sample :
         vector<string>{"swiss", "aabb", "Python"}) {

        const auto result =
            firstNonRepeatingCharacter(sample);

        cout << sample << " -> ";

        if (result.has_value()) {
            cout << *result;
        } else {
            cout << "none";
        }

        cout << '\n';
    }
}


// ============================================================================
// PALINDROME
// ============================================================================

bool isPalindrome(string_view text) {
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

void demonstratePalindrome() {
    subsection("12. Palindrome algorithm");

    for (const string& sample :
         vector<string>{"level", "radar", "Python", ""}) {

        cout << quoted(sample)
             << " palindrome: "
             << boolalpha
             << isPalindrome(sample)
             << '\n';
    }
}


// ============================================================================
// REVERSE WORDS
// ============================================================================

vector<string> splitWhitespace(const string& text) {
    vector<string> words;
    istringstream input(text);

    string word;

    while (input >> word) {
        words.push_back(word);
    }

    return words;
}

string reverseWords(const string& sentence) {
    vector<string> words = splitWhitespace(sentence);

    reverse(words.begin(), words.end());

    return join(words, " ");
}

void demonstrateReverseWords() {
    subsection("13. Reverse word order");

    const string sentence =
        "C++ provides powerful standard library components";

    cout << reverseWords(sentence) << '\n';
}


// ============================================================================
// LOG RECORD
// ============================================================================

struct LogRecord {
    string timestamp;
    string level;
    string message;
};

optional<LogRecord> parseLogLine(const string& line) {
    static const regex pattern(
        R"(^(\S+)\s+([A-Z]+)\s+(.*)$)"
    );

    smatch match;

    if (!regex_match(line, match, pattern)) {
        return nullopt;
    }

    return LogRecord{
        match[1].str(),
        match[2].str(),
        match[3].str()
    };
}

void demonstrateLogParser() {
    subsection("14. Structured log parser");

    const vector<string> lines = {
        "2026-09-25T10:00:00 INFO Server started",
        "2026-09-25T10:01:05 WARNING Cache is nearly full",
        "invalid log line",
        "2026-09-25T10:02:10 ERROR Database connection failed"
    };

    for (const string& line : lines) {
        const auto record = parseLogLine(line);

        if (!record.has_value()) {
            cout << "Could not parse: " << quoted(line) << '\n';
            continue;
        }

        cout << "Timestamp: " << record->timestamp << '\n';
        cout << "Level: " << record->level << '\n';
        cout << "Message: " << record->message << "\n\n";
    }
}


// ============================================================================
// LOG INGESTION SYSTEM
// ============================================================================

class LogAnalyzer {
private:
    vector<LogRecord> records;
    map<string, size_t> levelCounts;

public:
    void addLine(const string& line) {
        const auto record = parseLogLine(line);

        if (!record.has_value()) {
            throw invalid_argument(
                "Invalid log record: " + line
            );
        }

        levelCounts[record->level]++;
        records.push_back(*record);
    }

    size_t recordCount() const {
        return records.size();
    }

    size_t countLevel(const string& level) const {
        const auto iterator = levelCounts.find(level);

        if (iterator == levelCounts.end()) {
            return 0;
        }

        return iterator->second;
    }

    vector<LogRecord> recordsWithLevel(
        const string& level
    ) const {
        vector<LogRecord> result;

        for (const LogRecord& record : records) {
            if (record.level == level) {
                result.push_back(record);
            }
        }

        return result;
    }

    void printReport() const {
        cout << "\nLog Analyzer Report\n";
        cout << "-------------------\n";
        cout << "Records: " << records.size() << '\n';

        for (const auto& [level, count] : levelCounts) {
            cout << level << ": " << count << '\n';
        }
    }
};

void demonstrateLogAnalyzer() {
    subsection("15. Industry-style log analysis component");

    LogAnalyzer analyzer;

    const vector<string> input = {
        "2026-09-25T10:00:00 INFO Server started",
        "2026-09-25T10:01:05 WARNING Cache is nearly full",
        "2026-09-25T10:02:10 ERROR Database connection failed",
        "2026-09-25T10:03:00 INFO Request processed",
        "2026-09-25T10:04:20 ERROR Timeout contacting service"
    };

    for (const string& line : input) {
        try {
            analyzer.addLine(line);
        } catch (const exception& error) {
            cout << "Rejected record: "
                 << error.what()
                 << '\n';
        }
    }

    analyzer.printReport();

    cout << "ERROR records: "
         << analyzer.countLevel("ERROR")
         << '\n';

    const auto errors =
        analyzer.recordsWithLevel("ERROR");

    for (const LogRecord& record : errors) {
        cout << record.timestamp
             << " | "
             << record.message
             << '\n';
    }
}


// ============================================================================
// SECURITY
// ============================================================================

void demonstrateSecurity() {
    subsection("16. String security considerations");

    const string trusted = "a";
    const string visuallySimilar = "а";

    cout << "ASCII 'a' bytes: "
         << bytesToHex(trusted)
         << '\n';

    cout << "Cyrillic 'а' UTF-8 bytes: "
         << bytesToHex(visuallySimilar)
         << '\n';

    cout << "Byte sequences equal: "
         << boolalpha
         << (trusted == visuallySimilar)
         << '\n';

    /*
     * Logging untrusted text without escaping can create misleading logs.
     */
    const string maliciousLogValue =
        "alice\nADMIN=true";

    cout << "Untrusted log value size: "
         << maliciousLogValue.size()
         << '\n';

    /*
     * SQL injection example:
     * Never concatenate untrusted input into SQL.
     *
     * The following is intentionally only a string demonstration and does
     * not execute a database command.
     */
    const string userInput = "' OR 1=1 --";

    const string unsafeSql =
        "SELECT * FROM users WHERE name = '" +
        userInput +
        "'";

    cout << "Illustrative unsafe SQL: "
         << unsafeSql
         << '\n';

    cout << "Real database code should use parameter binding.\n";
}


// ============================================================================
// COMPLEXITY
// ============================================================================

void demonstrateComplexity() {
    subsection("17. Algorithmic complexity");

    cout << "Indexing std::string by position: O(1)\n";
    cout << "Linear traversal: O(n)\n";
    cout << "find() is generally linear in simple substring searches, "
            "with implementation-dependent optimizations.\n";
    cout << "Character-frequency map construction: O(n) expected with "
            "unordered_map.\n";
    cout << "Sorting n strings: typically O(n log n) comparisons, "
            "plus comparison costs.\n";
    cout << "LogAnalyzer level counting: O(n) total ingestion, assuming "
            "efficient map operations.\n";
}


// ============================================================================
// EDGE CASES
// ============================================================================

void demonstrateEdgeCases() {
    subsection("18. Edge cases");

    const vector<string> cases = {
        "",
        " ",
        "\n",
        "ASCII",
        "café",
        "😀",
        "👍🏽",
        "   C++   ",
        "line1\nline2"
    };

    for (const string& value : cases) {
        cout << "Byte length: "
             << value.size()
             << " | ASCII: "
             << isAscii(value)
             << " | value: "
             << quoted(value)
             << '\n';
    }

    /*
     * An empty string has no front() or back() element.
     * Calling those functions on an empty string is invalid.
     */
}


// ============================================================================
// TESTS
// ============================================================================

void runTests() {
    subsection("19. Automated tests");

    if (string("C++")[0] != 'C') {
        throw runtime_error("Basic indexing test failed.");
    }

    if (string("Python").substr(0, 6) != "Python") {
        throw runtime_error("Substring test failed.");
    }

    if (string("apple").find("app") != 0) {
        throw runtime_error("Search test failed.");
    }

    if (string("level") != string("level")) {
        throw runtime_error("Equality test failed.");
    }

    if (!isPalindrome("level")) {
        throw runtime_error("Palindrome test failed.");
    }

    if (isPalindrome("Python")) {
        throw runtime_error("Non-palindrome test failed.");
    }

    if (reverseWords("one two three") != "three two one") {
        throw runtime_error("Reverse-word test failed.");
    }

    string reason;

    if (!isValidUsername("user_123", reason)) {
        throw runtime_error("Valid username test failed.");
    }

    if (isValidUsername("1user", reason)) {
        throw runtime_error("Invalid username test failed.");
    }

    const auto parsed =
        parseLogLine(
            "2026-09-25T10:00:00 INFO Started"
        );

    if (!parsed.has_value() ||
        parsed->level != "INFO") {
        throw runtime_error("Log parsing test failed.");
    }

    if (isAscii("café")) {
        throw runtime_error("ASCII test failed.");
    }

    const auto decoded = decodeUtf8("A€");

    if (decoded.size() != 2 ||
        decoded[0] != 'A' ||
        decoded[1] != 0x20AC) {
        throw runtime_error("UTF-8 decoding test failed.");
    }

    cout << "All tests passed.\n";
}


// ============================================================================
// MAIN
// ============================================================================

int main() {
    try {
        section("STRINGS INTRODUCTION - C++17 TECHNICAL CASE STUDY");

        demonstrateBasicStrings();
        demonstrateAscii();
        demonstrateUtf8();
        demonstrateUtf8Decoding();

        demonstrateTraversal();
        demonstrateComparison();
        demonstrateSearching();
        demonstrateManipulation();
        demonstrateSplitJoin();

        demonstrateValidation();
        demonstrateRegularExpressions();

        demonstrateFrequency();
        demonstratePalindrome();
        demonstrateReverseWords();

        demonstrateLogParser();
        demonstrateLogAnalyzer();

        demonstrateSecurity();
        demonstrateComplexity();
        demonstrateEdgeCases();

        runTests();

        section("END OF C++ STRING CASE STUDY");

        return 0;
    } catch (const exception& error) {
        cerr << "Fatal error: "
             << error.what()
             << '\n';

        return 1;
    }
}
