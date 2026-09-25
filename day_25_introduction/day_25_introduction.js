/*
 * Strings Introduction
 *
 * Topics demonstrated:
 * - String literals and representation
 * - Characters and UTF-16 code units
 * - Unicode code points
 * - ASCII
 * - UTF-8 through TextEncoder/TextDecoder
 * - Indexing and traversal
 * - Comparison
 * - Searching
 * - Manipulation
 * - Template literals
 * - Validation
 * - Regular expressions
 * - Arrays and string construction
 * - Unicode normalization
 * - Unicode-aware iteration
 * - Edge cases
 * - Security considerations
 * - Practical text parsing
 * - Performance considerations
 * - Testing
 *
 * Run with a modern Node.js runtime:
 * node strings_introduction.js
 */

"use strict";

const section = (title) => {
    console.log("\n" + "=".repeat(78));
    console.log(title);
    console.log("=".repeat(78));
};

const subsection = (title) => {
    console.log("\n" + "-".repeat(78));
    console.log(title);
    console.log("-".repeat(78));
};


// ============================================================================
// 1. STRING CREATION
// ============================================================================

function demonstrateStringCreation() {
    subsection("1.1 String literals");

    const singleQuoted = 'Hello';
    const doubleQuoted = "World";
    const apostropheExample = "JavaScript's string";
    const templateLiteral = `A template literal can contain expressions.`;

    console.log(singleQuoted);
    console.log(doubleQuoted);
    console.log(apostropheExample);
    console.log(templateLiteral);

    // Escape sequences represent special characters.
    console.log("Line 1\nLine 2\tIndented");

    // JavaScript does not have a separate character primitive type.
    // A single character is still a string.
    const character = "A";
    console.log("Character:", character, "Type:", typeof character);
}


// ============================================================================
// 2. IMMUTABILITY
// ============================================================================

function demonstrateImmutability() {
    subsection("1.2 Strings are immutable");

    const text = "JavaScript";

    console.log("Original:", text);
    console.log("First character:", text[0]);
    console.log("Last character:", text[text.length - 1]);

    // Direct character assignment does not mutate a JavaScript string.
    // text[0] = "X"; // Does not produce a new modified string.

    const changed = "X" + text.slice(1);
    console.log("New string:", changed);
}


// ============================================================================
// 3. ASCII AND CODE POINTS
// ============================================================================

function demonstrateCodePoints() {
    subsection("2. ASCII and Unicode code points");

    const examples = ["A", "a", "0", "€", "中", "😀"];

    for (const value of examples) {
        console.log(
            JSON.stringify(value),
            "code point:",
            value.codePointAt(0),
            "hex:",
            "U+" + value.codePointAt(0).toString(16).toUpperCase()
        );
    }

    console.log("String.fromCodePoint(65):", String.fromCodePoint(65));
    console.log("String.fromCodePoint(128512):", String.fromCodePoint(128512));
}


// ============================================================================
// 4. UTF-16 CODE UNITS VS CODE POINTS
// ============================================================================

function demonstrateUtf16Behavior() {
    subsection("2.1 UTF-16 code units and Unicode code points");

    const examples = ["A", "é", "€", "😀", "👍🏽"];

    for (const value of examples) {
        console.log(
            JSON.stringify(value),
            "length/code units:",
            value.length,
            "code points:",
            [...value].length,
            "code point values:",
            Array.from(value, (character) => character.codePointAt(0))
        );
    }

    /*
     * JavaScript string indexing operates on UTF-16 code units.
     * Therefore emoji such as 😀 occupy two code units.
     */
    const emoji = "😀";
    console.log("emoji[0]:", emoji[0]);
    console.log("emoji code point:", emoji.codePointAt(0));
    console.log("Array.from(emoji):", Array.from(emoji));
}


// ============================================================================
// 5. ASCII
// ============================================================================

function isAscii(text) {
    for (const character of text) {
        if (character.codePointAt(0) > 127) {
            return false;
        }
    }

    return true;
}

function demonstrateAscii() {
    subsection("2.2 ASCII validation");

    for (const value of ["Hello", "Hello123", "café", "भारत"]) {
        console.log(JSON.stringify(value), "is ASCII:", isAscii(value));
    }
}


// ============================================================================
// 6. UTF-8
// ============================================================================

function demonstrateUtf8() {
    subsection("2.3 UTF-8 encoding and decoding");

    const textEncoder = new TextEncoder();
    const textDecoder = new TextDecoder("utf-8");

    const examples = ["A", "é", "€", "中", "😀"];

    for (const value of examples) {
        const bytes = textEncoder.encode(value);

        console.log(
            JSON.stringify(value),
            "UTF-8 bytes:",
            Array.from(bytes),
            "byte length:",
            bytes.length
        );

        console.log("Decoded:", textDecoder.decode(bytes));
    }

    // TextDecoder normally replaces malformed sequences unless configured
    // with fatal: true.
    const malformed = new Uint8Array([0xff, 0xfe]);

    console.log("Replacement decoding:", textDecoder.decode(malformed));

    const strictDecoder = new TextDecoder("utf-8", { fatal: true });

    try {
        strictDecoder.decode(malformed);
    } catch (error) {
        console.log("Expected strict decoding error:", error.message);
    }
}


// ============================================================================
// 7. INDEXING, SLICING, AND TRAVERSAL
// ============================================================================

function demonstrateTraversal() {
    subsection("3. Indexing and traversal");

    const text = "Programming";

    console.log("First:", text[0]);
    console.log("Last:", text[text.length - 1]);
    console.log("slice(0, 4):", text.slice(0, 4));
    console.log("slice(4):", text.slice(4));
    console.log("substring(0, 4):", text.substring(0, 4));

    console.log("for...of traversal:");
    for (const character of text) {
        process.stdout.write(character + " ");
    }
    console.log();

    console.log("Indexed traversal:");
    for (let index = 0; index < text.length; index++) {
        console.log(index, text[index]);
    }
}


// ============================================================================
// 8. COMPARISON
// ============================================================================

function demonstrateComparison() {
    subsection("4. String comparison");

    console.log("apple === apple:", "apple" === "apple");
    console.log("apple !== banana:", "apple" !== "banana");
    console.log("apple < banana:", "apple" < "banana");
    console.log("A < a:", "A" < "a");

    // JavaScript's relational comparison is based on lexicographic
    // ordering of UTF-16 code units.
    console.log("'A'.charCodeAt(0):", "A".charCodeAt(0));
    console.log("'a'.charCodeAt(0):", "a".charCodeAt(0));

    const left = "Python";
    const right = "python";

    console.log("Exact equality:", left === right);
    console.log(
        "Case-insensitive comparison:",
        left.toLocaleLowerCase() === right.toLocaleLowerCase()
    );
}


// ============================================================================
// 9. SEARCHING
// ============================================================================

function demonstrateSearching() {
    subsection("5. Searching");

    const text = "JavaScript is powerful and JavaScript is widely used.";

    console.log("includes:", text.includes("JavaScript"));
    console.log("startsWith:", text.startsWith("JavaScript"));
    console.log("endsWith:", text.endsWith("used."));
    console.log("indexOf:", text.indexOf("JavaScript"));
    console.log("lastIndexOf:", text.lastIndexOf("JavaScript"));

    console.log("Missing substring:", text.indexOf("Python"));

    console.log("Count using match:",
        (text.match(/JavaScript/g) || []).length
    );
}


// ============================================================================
// 10. MANIPULATION
// ============================================================================

function demonstrateManipulation() {
    subsection("6. Manipulation");

    const text = "  JavaScript Programming  ";

    console.log("trim:", JSON.stringify(text.trim()));
    console.log("trimStart:", JSON.stringify(text.trimStart()));
    console.log("trimEnd:", JSON.stringify(text.trimEnd()));
    console.log("upper:", text.toUpperCase());
    console.log("lower:", text.toLowerCase());
    console.log(
        "replace:",
        text.replace("JavaScript", "Advanced JavaScript")
    );
    console.log(
        "replaceAll:",
        "one one one".replaceAll("one", "1")
    );

    const words = "JavaScript,Python,C++".split(",");
    console.log("split:", words);
    console.log("join:", words.join(" | "));

    console.log(
        "repeat:",
        "JS ".repeat(3)
    );
}


// ============================================================================
// 11. TEMPLATE LITERALS
// ============================================================================

function demonstrateTemplateLiterals() {
    subsection("6.1 Template literals");

    const name = "Atul";
    const score = 97.4567;
    const average = (90 + 95 + 98) / 3;

    console.log(`Name: ${name}`);
    console.log(`Score: ${score.toFixed(2)}`);
    console.log(`Average: ${average.toFixed(2)}`);

    const multiline = `
Line 1
Line 2
Line 3
`;

    console.log(multiline);
}


// ============================================================================
// 12. VALIDATION
// ============================================================================

function validateUsername(username) {
    if (username.length === 0) {
        return { valid: false, message: "Username cannot be empty." };
    }

    if (username.length < 3 || username.length > 20) {
        return {
            valid: false,
            message: "Username must contain 3 to 20 characters."
        };
    }

    if (!isAscii(username)) {
        return {
            valid: false,
            message: "Username must contain only ASCII characters."
        };
    }

    if (!/^[A-Za-z_]/.test(username)) {
        return {
            valid: false,
            message: "Username must start with a letter or underscore."
        };
    }

    if (!/^[A-Za-z_][A-Za-z0-9_]*$/.test(username)) {
        return {
            valid: false,
            message: "Only letters, digits, and underscores are allowed."
        };
    }

    return { valid: true, message: "Valid username." };
}

function demonstrateValidation() {
    subsection("7. Validation");

    const candidates = [
        "atul_01",
        "",
        "ab",
        "1atul",
        "atul-pandey",
        "भारत"
    ];

    for (const candidate of candidates) {
        console.log(JSON.stringify(candidate), validateUsername(candidate));
    }
}


// ============================================================================
// 13. REGULAR EXPRESSIONS
// ============================================================================

function demonstrateRegularExpressions() {
    subsection("8. Regular expressions");

    const text = "Contact alice@example.com or bob@example.org.";

    const emailPattern =
        /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g;

    const emails = text.match(emailPattern) || [];
    console.log("Emails:", emails);

    const redacted = text.replace(emailPattern, "[EMAIL]");
    console.log("Redacted:", redacted);

    const identifierPattern = /^[A-Za-z_][A-Za-z0-9_]*$/;

    for (const value of ["name_1", "1name", "name-value", ""]) {
        console.log(
            JSON.stringify(value),
            identifierPattern.test(value)
        );
    }
}


// ============================================================================
// 14. ARRAY-BASED CHARACTER FREQUENCY
// ============================================================================

function characterFrequency(text) {
    const counts = new Map();

    for (const character of text) {
        counts.set(character, (counts.get(character) || 0) + 1);
    }

    return counts;
}

function demonstrateFrequency() {
    subsection("9. Character frequency");

    const text = "banana";
    const counts = characterFrequency(text);

    console.log("Frequency map:", Object.fromEntries(counts));
}


// ============================================================================
// 15. STRING ALGORITHMS
// ============================================================================

function firstNonRepeatingCharacter(text) {
    const counts = characterFrequency(text);

    for (const character of text) {
        if (counts.get(character) === 1) {
            return character;
        }
    }

    return null;
}

function isPalindrome(text, ignoreCase = true) {
    const normalized = ignoreCase ? text.toLocaleLowerCase() : text;
    return normalized === [...normalized].reverse().join("");
}

function reverseWords(sentence) {
    return sentence.trim().split(/\s+/).reverse().join(" ");
}

function demonstrateAlgorithms() {
    subsection("10. String algorithms");

    for (const value of ["swiss", "aabbcc", "Python", ""]) {
        console.log(
            JSON.stringify(value),
            "first non-repeating:",
            firstNonRepeatingCharacter(value)
        );
    }

    for (const value of ["level", "RaceCar", "Python"]) {
        console.log(
            JSON.stringify(value),
            "palindrome:",
            isPalindrome(value)
        );
    }

    console.log(
        reverseWords("JavaScript makes text processing practical")
    );
}


// ============================================================================
// 16. UNICODE NORMALIZATION
// ============================================================================

function demonstrateNormalization() {
    subsection("11. Unicode normalization");

    const composed = "é";
    const decomposed = "e\u0301";

    console.log(
        "Composed code points:",
        [...composed].map(
            character => "U+" + character.codePointAt(0).toString(16)
        )
    );

    console.log(
        "Decomposed code points:",
        [...decomposed].map(
            character => "U+" + character.codePointAt(0).toString(16)
        )
    );

    console.log("Direct equality:", composed === decomposed);

    console.log(
        "NFC equality:",
        composed.normalize("NFC") === decomposed.normalize("NFC")
    );

    console.log(
        "NFD decomposed:",
        [...composed.normalize("NFD")]
    );
}


// ============================================================================
// 17. USER-PERCEIVED CHARACTERS
// ============================================================================

function demonstrateUnicodeIteration() {
    subsection("11.1 Code points versus perceived characters");

    const examples = [
        "é",
        "e\u0301",
        "😀",
        "👍🏽",
        "🇮🇳",
        "👨‍👩‍👧‍👦"
    ];

    for (const value of examples) {
        console.log(
            JSON.stringify(value),
            "UTF-16 length:",
            value.length,
            "code-point count:",
            [...value].length
        );
    }

    /*
     * [...text] correctly avoids splitting surrogate pairs, but even this
     * does not necessarily correspond to one visual grapheme per element.
     * Complex grapheme segmentation requires Unicode-aware grapheme rules.
     */
}


// ============================================================================
// 18. SORTING
// ============================================================================

function demonstrateSorting() {
    subsection("12. Sorting");

    const names = ["alice", "Bob", "charlie", "ALAN"];

    console.log("Default sort:", [...names].sort());

    console.log(
        "Locale-aware sort:",
        [...names].sort((a, b) => a.localeCompare(b))
    );

    console.log(
        "Case-insensitive locale sort:",
        [...names].sort((a, b) =>
            a.localeCompare(b, undefined, { sensitivity: "base" })
        )
    );

    console.log(
        "Length sort:",
        [...names].sort((a, b) => a.length - b.length)
    );
}


// ============================================================================
// 19. PRACTICAL LOG PARSER
// ============================================================================

function parseLogLine(line) {
    const pattern =
        /^(?<timestamp>\S+)\s+(?<level>[A-Z]+)\s+(?<message>.*)$/;

    const match = line.trim().match(pattern);

    if (!match) {
        return null;
    }

    return {
        timestamp: match.groups.timestamp,
        level: match.groups.level,
        message: match.groups.message
    };
}

function demonstrateLogParser() {
    subsection("13. Practical log parsing");

    const lines = [
        "2026-09-25T10:00:00 INFO Server started",
        "2026-09-25T10:01:05 WARNING Cache is nearly full",
        "invalid log line",
        "2026-09-25T10:02:10 ERROR Database connection failed"
    ];

    for (const line of lines) {
        console.log(JSON.stringify(line), "=>", parseLogLine(line));
    }
}


// ============================================================================
// 20. TOKENIZATION
// ============================================================================

function tokenizeText(text) {
    return text.match(/\b[\p{L}\p{N}_']+\b/gu) || [];
}

function demonstrateTokenization() {
    subsection("14. Tokenization");

    const text =
        "JavaScript's strings are useful: fast, flexible, and readable.";

    const tokens = tokenizeText(text);

    console.log("Tokens:", tokens);
    console.log("Token count:", tokens.length);
}


// ============================================================================
// 21. SECURITY CONSIDERATIONS
// ============================================================================

function demonstrateSecurity() {
    subsection("15. Security-related string concerns");

    const latinA = "a";
    const cyrillicA = "а";

    console.log("Latin a code point:", latinA.codePointAt(0));
    console.log("Cyrillic a code point:", cyrillicA.codePointAt(0));
    console.log("Equal:", latinA === cyrillicA);

    // Control characters can make logs difficult to interpret.
    const maliciousLogValue = "alice\nADMIN=true";
    console.log("Safe diagnostic representation:", JSON.stringify(maliciousLogValue));

    /*
     * Never construct SQL, shell commands, HTML, or other executable
     * contexts by blindly concatenating untrusted strings.
     *
     * Each destination requires its own context-aware escaping or parameter
     * binding mechanism.
     */

    const userInput = "' OR 1=1 --";
    const unsafeSql =
        "SELECT * FROM users WHERE name = '" + userInput + "'";

    console.log("Illustrative unsafe SQL:", unsafeSql);
}


// ============================================================================
// 22. PASSWORD POLICY
// ============================================================================

function passwordPolicy(password) {
    const findings = [];

    if ([...password].length < 12) {
        findings.push("Use at least 12 characters.");
    }

    if (!/[A-Z]/.test(password)) {
        findings.push("Contains no uppercase letters.");
    }

    if (!/[a-z]/.test(password)) {
        findings.push("Contains no lowercase letters.");
    }

    if (!/\d/.test(password)) {
        findings.push("Contains no digits.");
    }

    if (!/[^\p{L}\p{N}]/u.test(password)) {
        findings.push("Contains no non-alphanumeric characters.");
    }

    return findings;
}

function demonstratePasswordPolicy() {
    subsection("16. Password policy checks");

    const passwords = [
        "password",
        "Password123",
        "A-stronger-example-2026!"
    ];

    for (const password of passwords) {
        const findings = passwordPolicy(password);
        console.log(
            JSON.stringify(password),
            findings.length === 0
                ? ["Policy checks passed."]
                : findings
        );
    }

    console.log(
        "A password policy is not a password-storage design. "
        + "Real systems require secure password hashing."
    );
}


// ============================================================================
// 23. PERFORMANCE
// ============================================================================

function demonstratePerformance() {
    subsection("17. Performance considerations");

    const pieces = Array.from(
        { length: 5000 },
        (_, index) => String(index)
    );

    let start = process.hrtime.bigint();
    const joined = pieces.join("");
    const joinDuration = Number(process.hrtime.bigint() - start);

    start = process.hrtime.bigint();

    let concatenated = "";
    for (const piece of pieces) {
        concatenated += piece;
    }

    const concatenationDuration =
        Number(process.hrtime.bigint() - start);

    console.log("join length:", joined.length);
    console.log("concatenation length:", concatenated.length);
    console.log(
        "join nanoseconds:",
        joinDuration
    );
    console.log(
        "repeated concatenation nanoseconds:",
        concatenationDuration
    );

    console.log(
        "For large collections of fragments, Array.join() clearly "
        + "expresses the intended bulk construction operation."
    );
}


// ============================================================================
// 24. EDGE CASES
// ============================================================================

function demonstrateEdgeCases() {
    subsection("18. Edge cases");

    const cases = [
        "",
        " ",
        "\n",
        "é",
        "e\u0301",
        "😀",
        "👍🏽",
        "   JavaScript   ",
        "JavaScript\nPython\nC++"
    ];

    for (const value of cases) {
        console.log(
            "value:",
            JSON.stringify(value),
            "UTF-16 length:",
            value.length,
            "trimmed:",
            JSON.stringify(value.trim())
        );
    }

    console.log(
        "Whitespace split:",
        "  one\t two\nthree ".trim().split(/\s+/)
    );
}


// ============================================================================
// 25. TEXT STATISTICS
// ============================================================================

function analyzeText(text) {
    let digits = 0;
    let whitespace = 0;
    let alphabetic = 0;

    for (const character of text) {
        if (/\p{N}/u.test(character)) {
            digits++;
        }

        if (/\s/u.test(character)) {
            whitespace++;
        }

        if (/\p{L}/u.test(character)) {
            alphabetic++;
        }
    }

    return {
        utf16CodeUnits: text.length,
        codePoints: [...text].length,
        words: text.trim() ? text.trim().split(/\s+/).length : 0,
        lines: text.length === 0 ? 0 : text.split("\n").length,
        digits,
        whitespace,
        alphabetic
    };
}

function demonstrateTextAnalyzer() {
    subsection("19. Complete text analyzer");

    const document = [
        "JavaScript strings represent Unicode text.",
        "They support ASCII, accented characters, symbols, and emoji.",
        "Text processing requires careful encoding decisions."
    ].join("\n");

    console.log(analyzeText(document));
}


// ============================================================================
// 26. TESTS
// ============================================================================

function runTests() {
    subsection("20. Automated tests");

    console.assert("JavaScript"[0] === "J");
    console.assert("JavaScript".slice(-1) === "t");
    console.assert("JavaScript".split("").reverse().join("") ===
        "tpircSavaJ");

    console.assert("apple" < "banana");
    console.assert("Python".toLowerCase() === "python");

    console.assert(
        new TextDecoder().decode(
            new TextEncoder().encode("café")
        ) === "café"
    );

    console.assert(
        "é".normalize("NFC") === "e\u0301".normalize("NFC")
    );

    console.assert(
        firstNonRepeatingCharacter("swiss") === "w"
    );

    console.assert(
        firstNonRepeatingCharacter("aabb") === null
    );

    console.assert(isPalindrome("Level"));
    console.assert(!isPalindrome("Python"));

    console.assert(
        reverseWords("one two three") === "three two one"
    );

    console.assert(validateUsername("user_123").valid);
    console.assert(!validateUsername("1user").valid);

    const parsed = parseLogLine(
        "2026-09-25T10:00:00 INFO Started"
    );

    console.assert(parsed !== null);
    console.assert(parsed.level === "INFO");

    console.assert(
        JSON.stringify(tokenizeText("one two three")) ===
        JSON.stringify(["one", "two", "three"])
    );

    console.log("All tests passed.");
}


// ============================================================================
// MAIN
// ============================================================================

function main() {
    section("STRINGS INTRODUCTION: COMPLETE JAVASCRIPT STUDY PROGRAM");

    demonstrateStringCreation();
    demonstrateImmutability();

    demonstrateCodePoints();
    demonstrateUtf16Behavior();
    demonstrateAscii();
    demonstrateUtf8();

    demonstrateTraversal();
    demonstrateComparison();
    demonstrateSearching();
    demonstrateManipulation();
    demonstrateTemplateLiterals();

    demonstrateValidation();
    demonstrateRegularExpressions();
    demonstrateFrequency();
    demonstrateAlgorithms();

    demonstrateNormalization();
    demonstrateUnicodeIteration();

    demonstrateSorting();
    demonstrateLogParser();
    demonstrateTokenization();

    demonstrateSecurity();
    demonstratePasswordPolicy();

    demonstratePerformance();
    demonstrateEdgeCases();
    demonstrateTextAnalyzer();

    runTests();

    section("END OF STRING STUDY PROGRAM");
}

main();
