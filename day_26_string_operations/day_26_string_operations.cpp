/*
 * STRING OPERATIONS: C++17 INDUSTRY-STYLE CASE STUDY
 *
 * Scenario:
 * A lightweight command-line text processing service receives log records,
 * normalizes their text, validates fields, performs string transformations,
 * counts character and word frequencies, searches records, and produces
 * analytical output.
 *
 * The implementation demonstrates:
 * - std::string
 * - concatenation
 * - substr()
 * - insertion and deletion
 * - replacement
 * - reversal
 * - frequency counting
 * - searching
 * - validation
 * - classes and encapsulation
 * - vectors, maps, unordered_map, sets
 * - exceptions
 * - algorithmic complexity
 * - Unicode limitations in ordinary std::string
 * - production-oriented validation
 *
 * Compile:
 *   g++ -std=c++17 -O2 string_operations.cpp -o string_operations
 */

#include <algorithm>
#include <cctype>
#include <exception>
#include <iomanip>
#include <iostream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

using namespace std;


// ---------------------------------------------------------------------------
// Utility functions
// ---------------------------------------------------------------------------

string trim(const string& text) {
    const auto first = text.find_first_not_of(" \t\r\n");
    if (first == string::npos) {
        return "";
    }

    const auto last = text.find_last_not_of(" \t\r\n");
    return text.substr(first, last - first + 1);
}

string toUpperAscii(string text) {
    for (char& character : text) {
        character = static_cast<char>(
            toupper(static_cast<unsigned char>(character))
        );
    }

    return text;
}

string normalizeWhitespace(const string& text) {
    string result;
    bool previousWasWhitespace = false;

    for (char character : text) {
        const bool whitespace =
            isspace(static_cast<unsigned char>(character)) != 0;

        if (whitespace) {
            if (!previousWasWhitespace) {
                result += ' ';
            }
        } else {
            result += character;
        }

        previousWasWhitespace = whitespace;
    }

    return trim(result);
}

string reverseString(const string& text) {
    string result = text;
    reverse(result.begin(), result.end());
    return result;
}


// ---------------------------------------------------------------------------
// Basic string operations
// ---------------------------------------------------------------------------

string concatenate(const string& first, const string& second) {
    return first + second;
}

string extractSubstring(
    const string& text,
    size_t start,
    size_t length
) {
    if (start > text.size()) {
        throw out_of_range("Substring start is outside the string.");
    }

    return text.substr(start, length);
}

string replaceAll(
    string text,
    const string& oldValue,
    const string& newValue
) {
    if (oldValue.empty()) {
        throw invalid_argument("Replacement value cannot be empty.");
    }

    size_t position = 0;

    while ((position = text.find(oldValue, position)) != string::npos) {
        text.replace(position, oldValue.size(), newValue);
        position += newValue.size();
    }

    return text;
}

string deleteAt(const string& text, size_t index) {
    if (index >= text.size()) {
        throw out_of_range("Deletion index is outside the string.");
    }

    string result = text;
    result.erase(index, 1);
    return result;
}

string insertAt(
    const string& text,
    size_t index,
    const string& value
) {
    if (index > text.size()) {
        throw out_of_range("Insertion index is outside the string.");
    }

    string result = text;
    result.insert(index, value);
    return result;
}

unordered_map<char, size_t> characterFrequency(const string& text) {
    unordered_map<char, size_t> frequency;

    for (char character : text) {
        ++frequency[character];
    }

    return frequency;
}

bool isPalindrome(string text) {
    text.erase(
        remove_if(
            text.begin(),
            text.end(),
            [](unsigned char character) {
                return !isalnum(character);
            }
        ),
        text.end()
    );

    transform(
        text.begin(),
        text.end(),
        text.begin(),
        [](unsigned char character) {
            return static_cast<char>(tolower(character));
        }
    );

    return text == string(text.rbegin(), text.rend());
}


// ---------------------------------------------------------------------------
// LogRecord
// ---------------------------------------------------------------------------

class LogRecord {
private:
    string level_;
    string user_;
    string message_;

public:
    LogRecord(
        string level,
        string user,
        string message
    )
        : level_(move(level)),
          user_(move(user)),
          message_(move(message)) {

        level_ = toUpperAscii(trim(level_));
        user_ = trim(user_);
        message_ = normalizeWhitespace(message_);

        if (level_.empty()) {
            throw invalid_argument("Log level cannot be empty.");
        }

        if (user_.empty()) {
            throw invalid_argument("User cannot be empty.");
        }

        if (message_.empty()) {
            throw invalid_argument("Message cannot be empty.");
        }
    }

    const string& level() const {
        return level_;
    }

    const string& user() const {
        return user_;
    }

    const string& message() const {
        return message_;
    }

    string serialize() const {
        return level_ + "|" + user_ + "|" + message_;
    }
};


// ---------------------------------------------------------------------------
// Parsing
// ---------------------------------------------------------------------------

vector<string> splitByDelimiter(
    const string& text,
    char delimiter
) {
    vector<string> parts;
    string current;

    for (char character : text) {
        if (character == delimiter) {
            parts.push_back(current);
            current.clear();
        } else {
            current += character;
        }
    }

    parts.push_back(current);
    return parts;
}

bool parseLogRecord(
    const string& raw,
    LogRecord& output,
    string& error
) {
    const vector<string> parts = splitByDelimiter(raw, '|');

    if (parts.size() != 3) {
        error = "Expected exactly three fields separated by '|'.";
        return false;
    }

    try {
        output = LogRecord(parts[0], parts[1], parts[2]);
        return true;
    } catch (const exception& exception) {
        error = exception.what();
        return false;
    }
}


// ---------------------------------------------------------------------------
// Text analytics
// ---------------------------------------------------------------------------

class TextAnalytics {
public:
    static map<char, size_t> sortedCharacterFrequency(
        const string& text
    ) {
        map<char, size_t> frequency;

        for (char character : text) {
            ++frequency[character];
        }

        return frequency;
    }

    static map<string, size_t> wordFrequency(
        const string& text
    ) {
        map<string, size_t> frequency;
        string word;

        auto flushWord = [&]() {
            if (!word.empty()) {
                string normalized = toUpperAscii(word);
                ++frequency[normalized];
                word.clear();
            }
        };

        for (char character : text) {
            if (isalnum(static_cast<unsigned char>(character))) {
                word += character;
            } else {
                flushWord();
            }
        }

        flushWord();
        return frequency;
    }

    static string firstNonRepeatingCharacter(
        const string& text
    ) {
        const auto frequency = characterFrequency(text);

        for (char character : text) {
            auto iterator = frequency.find(character);

            if (iterator != frequency.end() &&
                iterator->second == 1) {
                return string(1, character);
            }
        }

        return "";
    }
};


// ---------------------------------------------------------------------------
// Production-style processor
// ---------------------------------------------------------------------------

class LogProcessor {
private:
    vector<LogRecord> validRecords_;
    vector<string> invalidRecords_;

public:
    void ingest(const vector<string>& rawRecords) {
        for (const string& raw : rawRecords) {
            LogRecord record("", "", "");
            string error;

            if (parseLogRecord(raw, record, error)) {
                validRecords_.push_back(record);
            } else {
                invalidRecords_.push_back(
                    raw + " [reason: " + error + "]"
                );
            }
        }
    }

    const vector<LogRecord>& records() const {
        return validRecords_;
    }

    const vector<string>& invalidRecords() const {
        return invalidRecords_;
    }

    map<string, size_t> levelFrequency() const {
        map<string, size_t> result;

        for (const auto& record : validRecords_) {
            ++result[record.level()];
        }

        return result;
    }

    map<string, size_t> userFrequency() const {
        map<string, size_t> result;

        for (const auto& record : validRecords_) {
            ++result[record.user()];
        }

        return result;
    }

    vector<LogRecord> findContaining(
        const string& searchTerm
    ) const {
        vector<LogRecord> result;

        for (const auto& record : validRecords_) {
            if (
                record.message().find(searchTerm) != string::npos ||
                record.user().find(searchTerm) != string::npos
            ) {
                result.push_back(record);
            }
        }

        return result;
    }

    string combinedMessages() const {
        string result;

        for (size_t index = 0; index < validRecords_.size(); ++index) {
            if (index > 0) {
                result += '\n';
            }

            result += validRecords_[index].message();
        }

        return result;
    }
};


// ---------------------------------------------------------------------------
// Output helpers
// ---------------------------------------------------------------------------

void printMap(const map<string, size_t>& values) {
    for (const auto& [key, value] : values) {
        cout << "  " << key << ": " << value << '\n';
    }
}

void printCharacterMap(
    const map<char, size_t>& values
) {
    for (const auto& [key, value] : values) {
        if (key == ' ') {
            cout << "  [space]: " << value << '\n';
        } else {
            cout << "  [" << key << "]: " << value << '\n';
        }
    }
}

void printRecords(
    const vector<LogRecord>& records
) {
    for (const auto& record : records) {
        cout << "  " << record.serialize() << '\n';
    }
}


// ---------------------------------------------------------------------------
// Demonstrations
// ---------------------------------------------------------------------------

void basicOperationsDemo() {
    cout << "\n" << string(70, '=') << '\n';
    cout << "1. BASIC STRING OPERATIONS\n";
    cout << string(70, '=') << '\n';

    const string first = "String";
    const string second = "Operations";

    cout << "Concatenation: "
         << concatenate(first, " " + second)
         << '\n';

    const string text = "Programming";

    cout << "Substring: "
         << extractSubstring(text, 0, 7)
         << '\n';

    cout << "Reverse: "
         << reverseString(text)
         << '\n';

    cout << "Replacement: "
         << replaceAll(text, "Programming", "C++")
         << '\n';

    cout << "Deletion: "
         << deleteAt(text, 3)
         << '\n';

    cout << "Insertion: "
         << insertAt(text, 11, "!")
         << '\n';

    cout << "Frequency of characters:\n";

    const auto frequency = characterFrequency("banana");

    map<char, size_t> sortedFrequency(
        frequency.begin(),
        frequency.end()
    );

    printCharacterMap(sortedFrequency);
}


void edgeCasesDemo() {
    cout << "\n" << string(70, '=') << '\n';
    cout << "2. EDGE CASES AND ERROR HANDLING\n";
    cout << string(70, '=') << '\n';

    try {
        cout << "Invalid substring: "
             << extractSubstring("abc", 20, 2)
             << '\n';
    } catch (const exception& exception) {
        cout << "Handled substring error: "
             << exception.what()
             << '\n';
    }

    try {
        cout << "Invalid deletion: "
             << deleteAt("abc", 20)
             << '\n';
    } catch (const exception& exception) {
        cout << "Handled deletion error: "
             << exception.what()
             << '\n';
    }

    try {
        cout << "Invalid replacement: "
             << replaceAll("abc", "", "x")
             << '\n';
    } catch (const exception& exception) {
        cout << "Handled replacement error: "
             << exception.what()
             << '\n';
    }

    cout << "Empty string length: "
         << string("").size()
         << '\n';

    cout << "Empty search result: "
         << ("abc".find("") == 0)
         << '\n';
}


void caseStudyDemo() {
    cout << "\n" << string(70, '=') << '\n';
    cout << "3. LOG PROCESSING CASE STUDY\n";
    cout << string(70, '=') << '\n';

    const vector<string> rawRecords = {
        "INFO|alice|Login successful",
        "ERROR|bob|Invalid password",
        "INFO|alice|Viewed dashboard",
        "WARNING|charlie|Password expires soon",
        "ERROR|bob|Account temporarily locked",
        "INVALID RECORD",
        "ERROR||Missing user",
        "INFO|david|   Excessive   whitespace   "
    };

    LogProcessor processor;
    processor.ingest(rawRecords);

    cout << "\nValid records:\n";
    printRecords(processor.records());

    cout << "\nInvalid records:\n";
    for (const auto& record : processor.invalidRecords()) {
        cout << "  " << record << '\n';
    }

    cout << "\nLevel frequency:\n";
    printMap(processor.levelFrequency());

    cout << "\nUser frequency:\n";
    printMap(processor.userFrequency());

    cout << "\nRecords containing 'password':\n";
    printRecords(processor.findContaining("password"));

    const string combined = processor.combinedMessages();

    cout << "\nCombined message palindrome: "
         << boolalpha
         << isPalindrome(combined)
         << '\n';

    cout << "\nWord frequency:\n";
    printMap(TextAnalytics::wordFrequency(combined));

    cout << "\nFirst non-repeating character: ";

    const string firstUnique =
        TextAnalytics::firstNonRepeatingCharacter(combined);

    if (firstUnique.empty()) {
        cout << "none\n";
    } else {
        cout << firstUnique << '\n';
    }
}


// ---------------------------------------------------------------------------
// Complexity notes encoded as runtime demonstrations
// ---------------------------------------------------------------------------

void algorithmDemo() {
    cout << "\n" << string(70, '=') << '\n';
    cout << "4. ALGORITHMIC CONSIDERATIONS\n";
    cout << string(70, '=') << '\n';

    const string text = "banana";

    /*
     * Character frequency:
     *   Time: O(n)
     *   Auxiliary space: O(k), where k is the number of distinct characters.
     *
     * Substring extraction:
     *   In modern C++, std::string::substr creates a new string, so copying
     *   the selected characters costs O(m), where m is substring length.
     *
     * Searching with find():
     *   The exact complexity depends on the standard-library implementation.
     *   It should not automatically be treated as constant time.
     */

    cout << "Text: " << text << '\n';

    const auto frequency = TextAnalytics::sortedCharacterFrequency(text);

    cout << "Frequency:\n";
    printCharacterMap(frequency);

    cout << "Palindrome 'level': "
         << boolalpha
         << isPalindrome("level")
         << '\n';
}


// ---------------------------------------------------------------------------
// Unicode considerations
// ---------------------------------------------------------------------------

void unicodeDemo() {
    cout << "\n" << string(70, '=') << '\n';
    cout << "5. CHARACTER ENCODING CONSIDERATION\n";
    cout << string(70, '=') << '\n';

    /*
     * std::string is a sequence of bytes, not automatically a sequence of
     * Unicode characters.
     *
     * ASCII examples work naturally because one ASCII character is one byte.
     * UTF-8 text may use multiple bytes for one user-perceived character.
     *
     * This program therefore treats std::string as byte-oriented text.
     * Production multilingual systems should explicitly choose and enforce
     * an encoding strategy rather than assuming byte count equals character
     * count.
     */

    const string ascii = "cafe";

    cout << "ASCII text: " << ascii << '\n';
    cout << "Byte count: " << ascii.size() << '\n';

    const string utf8 = "cafe with UTF-8: café";

    cout << "UTF-8 text: " << utf8 << '\n';
    cout << "std::string byte count: " << utf8.size() << '\n';
}


// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

void runTests() {
    cout << "\n" << string(70, '=') << '\n';
    cout << "6. SELF-TESTS\n";
    cout << string(70, '=') << '\n';

    if (concatenate("Hello", " World") != "Hello World") {
        throw runtime_error("Concatenation test failed.");
    }

    if (extractSubstring("abcdef", 1, 3) != "bcd") {
        throw runtime_error("Substring test failed.");
    }

    if (reverseString("abcdef") != "fedcba") {
        throw runtime_error("Reverse test failed.");
    }

    if (replaceAll("banana", "a", "o") != "bonono") {
        throw runtime_error("Replacement test failed.");
    }

    if (deleteAt("banana", 2) != "baana") {
        throw runtime_error("Deletion test failed.");
    }

    if (insertAt("Pythn", 4, "o") != "Python") {
        throw runtime_error("Insertion test failed.");
    }

    if (characterFrequency("banana").at('a') != 3) {
        throw runtime_error("Frequency test failed.");
    }

    if (!isPalindrome("A man, a plan, a canal: Panama")) {
        throw runtime_error("Palindrome test failed.");
    }

    cout << "All tests passed.\n";
}


// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

int main() {
    try {
        basicOperationsDemo();
        edgeCasesDemo();
        caseStudyDemo();
        algorithmDemo();
        unicodeDemo();
        runTests();

        cout << "\n" << string(70, '=') << '\n';
        cout << "C++ STRING OPERATIONS CASE STUDY COMPLETE\n";
        cout << string(70, '=') << '\n';

        return 0;
    } catch (const exception& exception) {
        cerr << "Fatal error: " << exception.what() << '\n';
        return 1;
    }
}
