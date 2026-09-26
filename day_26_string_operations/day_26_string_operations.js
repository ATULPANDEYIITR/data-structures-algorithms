/*
 * STRING OPERATIONS: JAVASCRIPT PRACTICAL STUDY FILE
 *
 * Demonstrates:
 * - Creation and indexing
 * - Concatenation
 * - Substrings and slices
 * - Reversal
 * - Replacement
 * - Deletion and insertion
 * - Frequency counting
 * - Searching
 * - Unicode
 * - Regular expressions
 * - Validation
 * - Immutability
 * - Functional processing
 * - Performance-aware construction
 * - A practical text-analysis case study
 *
 * Run with:
 *   node string_operations.js
 */

// ---------------------------------------------------------------------------
// 1. FUNDAMENTALS
// ---------------------------------------------------------------------------

function fundamentals() {
    console.log("\n" + "=".repeat(70));
    console.log("1. STRING FUNDAMENTALS");
    console.log("=".repeat(70));

    const text = "JavaScript";

    console.log("String:", text);
    console.log("Type:", typeof text);
    console.log("Length:", text.length);
    console.log("First character:", text[0]);
    console.log("Last character:", text[text.length - 1]);

    for (let index = 0; index < text.length; index++) {
        console.log(`index=${index}: ${text[index]}`);
    }

    // Strings are immutable. Operations create new strings.
    const changed = "J" + text.slice(1);
    console.log("Reconstructed string:", changed);
}


// ---------------------------------------------------------------------------
// 2. CONCATENATION
// ---------------------------------------------------------------------------

function concatenationExamples() {
    console.log("\n" + "=".repeat(70));
    console.log("2. CONCATENATION");
    console.log("=".repeat(70));

    const firstName = "Atul";
    const lastName = "Pandey";

    console.log("Using +:", firstName + " " + lastName);

    const age = 30;
    console.log(`Using template literal: ${firstName} ${lastName} is ${age}.`);

    const words = ["JavaScript", "String", "Operations"];
    console.log("Using join():", words.join(" "));

    console.log("Repetition:", "ab".repeat(3));
}


// ---------------------------------------------------------------------------
// 3. SUBSTRING EXTRACTION
// ---------------------------------------------------------------------------

function substringExamples() {
    console.log("\n" + "=".repeat(70));
    console.log("3. SUBSTRING EXTRACTION");
    console.log("=".repeat(70));

    const text = "String Operations";

    console.log("Original:", text);
    console.log("First six:", text.slice(0, 6));
    console.log("From index 7:", text.slice(7));
    console.log("Last five:", text.slice(-5));
    console.log("Middle:", text.substring(7, 17));

    // slice() supports negative indexes; substring() treats negative values
    // differently, so slice() is usually easier for index-based extraction.
    console.log("Reverse:", [...text].reverse().join(""));
}


// ---------------------------------------------------------------------------
// 4. REVERSING
// ---------------------------------------------------------------------------

function reverseString(text) {
    // Spread into an array first. This handles many Unicode code points better
    // than text.split("") because some Unicode characters occupy multiple
    // UTF-16 code units.
    return [...text].reverse().join("");
}

function reverseExamples() {
    console.log("\n" + "=".repeat(70));
    console.log("4. REVERSING");
    console.log("=".repeat(70));

    const text = "algorithm";

    console.log("Original:", text);
    console.log("Reversed:", reverseString(text));

    const candidate = "level";
    console.log("Palindrome:", candidate === reverseString(candidate));
}


// ---------------------------------------------------------------------------
// 5. CHARACTER REPLACEMENT
// ---------------------------------------------------------------------------

function replacementExamples() {
    console.log("\n" + "=".repeat(70));
    console.log("5. CHARACTER REPLACEMENT");
    console.log("=".repeat(70));

    const text = "banana";

    console.log("Original:", text);
    console.log("First 'a':", text.replace("a", "o"));
    console.log("All 'a':", text.replaceAll("a", "o"));

    const sentence = "JavaScript is powerful. JavaScript runs in browsers.";
    console.log(sentence.replaceAll("JavaScript", "JS"));
}


// ---------------------------------------------------------------------------
// 6. CHARACTER DELETION
// ---------------------------------------------------------------------------

function deleteAt(text, index) {
    if (!Number.isInteger(index) || index < 0 || index >= text.length) {
        throw new RangeError("Deletion index is outside the valid range.");
    }

    return text.slice(0, index) + text.slice(index + 1);
}

function deleteRange(text, start, end) {
    if (
        !Number.isInteger(start) ||
        !Number.isInteger(end) ||
        start < 0 ||
        end < start ||
        end > text.length
    ) {
        throw new RangeError("Invalid deletion range.");
    }

    return text.slice(0, start) + text.slice(end);
}

function deletionExamples() {
    console.log("\n" + "=".repeat(70));
    console.log("6. CHARACTER DELETION");
    console.log("=".repeat(70));

    console.log("Delete index 2:", deleteAt("banana", 2));
    console.log("Delete range:", deleteRange("JavaScript", 4, 10));
    console.log("Delete all spaces:", "a b c".replaceAll(" ", ""));

    try {
        deleteAt("abc", 99);
    } catch (error) {
        console.log("Expected error:", error.message);
    }
}


// ---------------------------------------------------------------------------
// 7. CHARACTER INSERTION
// ---------------------------------------------------------------------------

function insertAt(text, index, value) {
    if (!Number.isInteger(index) || index < 0 || index > text.length) {
        throw new RangeError("Insertion index is outside the valid range.");
    }

    return text.slice(0, index) + value + text.slice(index);
}

function insertionExamples() {
    console.log("\n" + "=".repeat(70));
    console.log("7. CHARACTER INSERTION");
    console.log("=".repeat(70));

    console.log("Correction:", insertAt("Javasript", 4, "c"));
    console.log("Beginning:", insertAt("World", 0, "Hello "));
    console.log("End:", insertAt("Hello", 5, "!"));
}


// ---------------------------------------------------------------------------
// 8. FREQUENCY COUNTING
// ---------------------------------------------------------------------------

function characterFrequency(text) {
    const frequency = new Map();

    for (const character of text) {
        frequency.set(character, (frequency.get(character) || 0) + 1);
    }

    return frequency;
}

function wordFrequency(text) {
    const words = text.toLocaleLowerCase().match(/\b[\p{L}\p{N}'-]+\b/gu) || [];
    const frequency = new Map();

    for (const word of words) {
        frequency.set(word, (frequency.get(word) || 0) + 1);
    }

    return frequency;
}

function mapToObject(map) {
    return Object.fromEntries(map.entries());
}

function frequencyExamples() {
    console.log("\n" + "=".repeat(70));
    console.log("8. FREQUENCY COUNTING");
    console.log("=".repeat(70));

    console.log(
        "Character frequency:",
        mapToObject(characterFrequency("banana"))
    );

    const sentence = "JavaScript is useful and JavaScript is flexible";
    console.log("Word frequency:", mapToObject(wordFrequency(sentence)));
}


// ---------------------------------------------------------------------------
// 9. SEARCHING
// ---------------------------------------------------------------------------

function searchingExamples() {
    console.log("\n" + "=".repeat(70));
    console.log("9. SEARCHING");
    console.log("=".repeat(70));

    const text = "String operations are useful.";

    console.log("Includes:", text.includes("operations"));
    console.log("Index:", text.indexOf("operations"));
    console.log("Missing index:", text.indexOf("database"));
    console.log("Starts with:", text.startsWith("String"));
    console.log("Ends with:", text.endsWith("."));
}


// ---------------------------------------------------------------------------
// 10. NORMALIZATION
// ---------------------------------------------------------------------------

function normalizationExamples() {
    console.log("\n" + "=".repeat(70));
    console.log("10. NORMALIZATION");
    console.log("=".repeat(70));

    const text = "   JavaScript STRING Operations   ";

    console.log("Original:", JSON.stringify(text));
    console.log("Trimmed:", JSON.stringify(text.trim()));
    console.log("Lowercase:", text.toLowerCase());
    console.log("Uppercase:", text.toUpperCase());

    const userInput = "  YES  ";
    const normalized = userInput.trim().toLowerCase();

    console.log("Normalized input:", normalized);
    console.log("Accepted:", ["yes", "y"].includes(normalized));
}


// ---------------------------------------------------------------------------
// 11. REGULAR EXPRESSIONS
// ---------------------------------------------------------------------------

function regexExamples() {
    console.log("\n" + "=".repeat(70));
    console.log("11. REGULAR EXPRESSIONS");
    console.log("=".repeat(70));

    const text = "Contact alice@example.com and bob@example.org.";

    const emails = text.match(
        /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g
    ) || [];

    console.log("Emails:", emails);

    const messy = "JavaScript\tstrings   are\npowerful";
    const clean = messy.replace(/\s+/g, " ").trim();

    console.log("Normalized whitespace:", clean);
}


// ---------------------------------------------------------------------------
// 12. UNICODE
// ---------------------------------------------------------------------------

function unicodeExamples() {
    console.log("\n" + "=".repeat(70));
    console.log("12. UNICODE AND UTF-16");
    console.log("=".repeat(70));

    const examples = ["A", "é", "中", "🙂"];

    for (const character of examples) {
        console.log(
            character,
            "UTF-16 length:",
            character.length,
            "code points:",
            [...character].length
        );
    }

    const multilingual = "नमस्ते 世界";
    console.log("Multilingual text:", multilingual);
    console.log("UTF-16 code-unit length:", multilingual.length);
    console.log("Code-point count:", [...multilingual].length);
}


// ---------------------------------------------------------------------------
// 13. VALIDATION
// ---------------------------------------------------------------------------

function validateIdentifier(identifier) {
    if (identifier.length === 0) {
        return { valid: false, message: "Identifier cannot be empty." };
    }

    if (!/^[A-Za-z_$]/.test(identifier)) {
        return {
            valid: false,
            message: "Identifier must begin with a letter, _ or $."
        };
    }

    if (!/^[A-Za-z0-9_$]+$/.test(identifier)) {
        return {
            valid: false,
            message: "Identifier contains an invalid character."
        };
    }

    return { valid: true, message: "Valid identifier." };
}

function validationExamples() {
    console.log("\n" + "=".repeat(70));
    console.log("13. VALIDATION");
    console.log("=".repeat(70));

    const candidates = [
        "total_count",
        "$price",
        "2ndValue",
        "user-name",
        "",
        "user123"
    ];

    for (const candidate of candidates) {
        console.log(candidate, validateIdentifier(candidate));
    }
}


// ---------------------------------------------------------------------------
// 14. TEXT ANALYZER CLASS
// ---------------------------------------------------------------------------

class TextAnalyzer {
    constructor(text) {
        if (typeof text !== "string") {
            throw new TypeError("TextAnalyzer requires a string.");
        }

        this.text = text;
    }

    characterFrequency(ignoreWhitespace = false) {
        const source = ignoreWhitespace
            ? [...this.text].filter(character => !/\s/u.test(character)).join("")
            : this.text;

        return characterFrequency(source);
    }

    words() {
        return this.text.match(/\b[\p{L}\p{N}'-]+\b/gu) || [];
    }

    wordFrequency() {
        return wordFrequency(this.text);
    }

    reverse() {
        return reverseString(this.text);
    }

    palindrome() {
        const normalized = [...this.text]
            .filter(character => /[\p{L}\p{N}]/u.test(character))
            .join("")
            .toLocaleLowerCase();

        return normalized === reverseString(normalized);
    }

    replace(oldValue, newValue) {
        return this.text.replaceAll(oldValue, newValue);
    }

    insert(index, value) {
        return insertAt(this.text, index, value);
    }

    deleteRange(start, end) {
        return deleteRange(this.text, start, end);
    }
}

function analyzerDemo() {
    console.log("\n" + "=".repeat(70));
    console.log("14. TEXT ANALYZER");
    console.log("=".repeat(70));

    const analyzer = new TextAnalyzer(
        "JavaScript strings are immutable. JavaScript strings are sequences."
    );

    console.log(
        "Character frequency:",
        mapToObject(analyzer.characterFrequency(true))
    );
    console.log("Word frequency:", mapToObject(analyzer.wordFrequency()));
    console.log("Reversed:", analyzer.reverse());
    console.log("Palindrome:", analyzer.palindrome());
    console.log("Replacement:", analyzer.replace("JavaScript", "JS"));
    console.log("Insertion:", analyzer.insert(0, "[TEXT] "));
    console.log("Deletion:", analyzer.deleteRange(0, 11));
}


// ---------------------------------------------------------------------------
// 15. ALGORITHMIC OPERATIONS
// ---------------------------------------------------------------------------

function firstNonRepeatingCharacter(text) {
    const frequencies = characterFrequency(text);

    for (const character of text) {
        if (frequencies.get(character) === 1) {
            return character;
        }
    }

    return null;
}

function isPalindrome(text) {
    const normalized = [...text]
        .filter(character => /[\p{L}\p{N}]/u.test(character))
        .join("")
        .toLocaleLowerCase();

    return normalized === reverseString(normalized);
}

function algorithmExamples() {
    console.log("\n" + "=".repeat(70));
    console.log("15. ALGORITHMS");
    console.log("=".repeat(70));

    for (const value of [
        "level",
        "A man, a plan, a canal: Panama",
        "JavaScript"
    ]) {
        console.log(value, "palindrome:", isPalindrome(value));
    }

    for (const value of ["swiss", "aabbcc", ""]) {
        console.log(
            value,
            "first non-repeating:",
            firstNonRepeatingCharacter(value)
        );
    }
}


// ---------------------------------------------------------------------------
// 16. PRACTICAL LOG PROCESSING CASE STUDY
// ---------------------------------------------------------------------------

function processLogRecords(records) {
    const levelFrequency = new Map();
    const userFrequency = new Map();
    const messages = [];
    const invalidRecords = [];

    for (const record of records) {
        const parts = record.split("|");

        if (parts.length !== 3) {
            invalidRecords.push(record);
            continue;
        }

        const [rawLevel, rawUser, rawMessage] = parts;
        const level = rawLevel.trim().toUpperCase();
        const user = rawUser.trim();
        const message = rawMessage.trim().replace(/\s+/g, " ");

        if (!level || !user || !message) {
            invalidRecords.push(record);
            continue;
        }

        levelFrequency.set(
            level,
            (levelFrequency.get(level) || 0) + 1
        );

        userFrequency.set(
            user,
            (userFrequency.get(user) || 0) + 1
        );

        messages.push(message);
    }

    return {
        levels: mapToObject(levelFrequency),
        users: mapToObject(userFrequency),
        messages,
        invalid: invalidRecords
    };
}

function caseStudyDemo() {
    console.log("\n" + "=".repeat(70));
    console.log("16. LOG PROCESSING CASE STUDY");
    console.log("=".repeat(70));

    const records = [
        "INFO|alice|Login successful",
        "ERROR|bob|Invalid password",
        "INFO|alice|Viewed dashboard",
        "WARNING|charlie|Password expires soon",
        "ERROR|bob|Account temporarily locked",
        "INVALID RECORD"
    ];

    console.log(processLogRecords(records));
}


// ---------------------------------------------------------------------------
// 17. PERFORMANCE-AWARE CONSTRUCTION
// ---------------------------------------------------------------------------

function performanceExample() {
    console.log("\n" + "=".repeat(70));
    console.log("17. PERFORMANCE-AWARE STRING CONSTRUCTION");
    console.log("=".repeat(70));

    // Collect pieces and join once instead of repeatedly constructing a
    // growing string inside a large loop.
    const pieces = [];

    for (let index = 0; index < 10000; index++) {
        pieces.push(`record-${index}`);
    }

    const result = pieces.join("\n");

    console.log("Records:", pieces.length);
    console.log("Generated characters:", result.length);
}


// ---------------------------------------------------------------------------
// 18. ERROR HANDLING AND EDGE CASES
// ---------------------------------------------------------------------------

function edgeCaseExamples() {
    console.log("\n" + "=".repeat(70));
    console.log("18. EDGE CASES");
    console.log("=".repeat(70));

    const cases = ["", " ", "A", "AAAA", "12345", "😀😀"];

    for (const value of cases) {
        console.log({
            value,
            length: value.length,
            codePoints: [...value].length,
            reversed: reverseString(value),
            aCount: [...value].filter(c => c === "a").length
        });
    }

    // indexOf returns -1 rather than throwing when a value is absent.
    console.log("Missing search:", "abc".indexOf("z"));

    // slice safely handles indexes beyond the string's length.
    console.log("Out-of-range slice:", "abc".slice(100));

    try {
        insertAt("abc", 10, "X");
    } catch (error) {
        console.log("Insertion failure:", error.message);
    }
}


// ---------------------------------------------------------------------------
// 19. TESTS
// ---------------------------------------------------------------------------

function runTests() {
    console.log("\n" + "=".repeat(70));
    console.log("19. SELF-TESTS");
    console.log("=".repeat(70));

    console.assert("Hello" + " " + "World" === "Hello World");
    console.assert("abcdef".slice(1, 4) === "bcd");
    console.assert(reverseString("abcdef") === "fedcba");
    console.assert("banana".replaceAll("a", "o") === "bonono");
    console.assert(deleteAt("banana", 2) === "baana");
    console.assert(insertAt("Pythn", 4, "o") === "Python");
    console.assert(characterFrequency("banana").get("a") === 3);
    console.assert(isPalindrome("Race car!"));
    console.assert(firstNonRepeatingCharacter("swiss") === "w");
    console.assert(validateIdentifier("user_123").valid);
    console.assert(!validateIdentifier("123user").valid);

    console.log("All tests passed.");
}


// ---------------------------------------------------------------------------
// 20. MAIN
// ---------------------------------------------------------------------------

function main() {
    fundamentals();
    concatenationExamples();
    substringExamples();
    reverseExamples();
    replacementExamples();
    deletionExamples();
    insertionExamples();
    frequencyExamples();
    searchingExamples();
    normalizationExamples();
    regexExamples();
    unicodeExamples();
    validationExamples();
    analyzerDemo();
    algorithmExamples();
    caseStudyDemo();
    performanceExample();
    edgeCaseExamples();
    runTests();

    console.log("\n" + "=".repeat(70));
    console.log("JAVASCRIPT STRING OPERATIONS STUDY PROGRAM COMPLETE");
    console.log("=".repeat(70));
}

main();
