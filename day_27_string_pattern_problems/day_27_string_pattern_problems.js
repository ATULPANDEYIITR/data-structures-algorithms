/*
STRING PATTERN PROBLEMS
=======================

A standalone JavaScript study file covering:

- Character frequency
- Palindromes
- Anagrams
- Substrings
- Subsequences
- Sliding windows
- String transformations
- Dynamic programming
- Edit distance
- Longest common subsequence
- Pattern matching with KMP
- Trie
- Rolling hash
- Validation
- Testing
- Performance considerations

Run with:
    node string_pattern_problems.js
*/

"use strict";

// ============================================================================
// 1. FUNDAMENTALS
// ============================================================================

function demonstrateStringFundamentals() {
    const text = "Algorithm";

    console.log("\n=== STRING FUNDAMENTALS ===");
    console.log("Original:", text);
    console.log("Length:", text.length);
    console.log("First:", text[0]);
    console.log("Last:", text[text.length - 1]);
    console.log("Slice:", text.slice(0, 4));
    console.log("Reverse:", [...text].reverse().join(""));
    console.log("Uppercase:", text.toUpperCase());
    console.log("Lowercase:", text.toLowerCase());
    console.log("Contains 'go':", text.toLowerCase().includes("go"));

    // JavaScript strings are immutable. replace() returns a new string.
    console.log("Changed:", text.replace("g", "X"));
}

function normalizeText(text, {
    ignoreCase = true,
    alphanumericOnly = false
} = {}) {
    if (typeof text !== "string") {
        throw new TypeError("text must be a string");
    }

    let result = ignoreCase ? text.toLocaleLowerCase() : text;

    if (alphanumericOnly) {
        result = result.replace(/[^\p{L}\p{N}]/gu, "");
    }

    return result;
}

// ============================================================================
// 2. CHARACTER FREQUENCY
// ============================================================================

function characterFrequency(text) {
    const frequencies = new Map();

    for (const character of text) {
        frequencies.set(character, (frequencies.get(character) ?? 0) + 1);
    }

    return frequencies;
}

function mapToObject(map) {
    return Object.fromEntries(map.entries());
}

function firstNonRepeatingCharacter(text) {
    const frequencies = characterFrequency(text);

    for (const character of text) {
        if (frequencies.get(character) === 1) {
            return character;
        }
    }

    return null;
}

function firstRepeatingCharacter(text) {
    const seen = new Set();

    for (const character of text) {
        if (seen.has(character)) {
            return character;
        }

        seen.add(character);
    }

    return null;
}

function mostFrequentCharacter(text) {
    if (text.length === 0) {
        return null;
    }

    const frequencies = characterFrequency(text);
    let bestCharacter = null;
    let bestFrequency = 0;

    for (const [character, frequency] of frequencies) {
        if (frequency > bestFrequency) {
            bestCharacter = character;
            bestFrequency = frequency;
        }
    }

    return { character: bestCharacter, frequency: bestFrequency };
}

// ============================================================================
// 3. PALINDROMES
// ============================================================================

function isPalindrome(text) {
    const characters = [...text];

    for (let left = 0, right = characters.length - 1; left < right; left++, right--) {
        if (characters[left] !== characters[right]) {
            return false;
        }
    }

    return true;
}

function isValidPalindrome(text) {
    const normalized = normalizeText(text, {
        ignoreCase: true,
        alphanumericOnly: true
    });

    return isPalindrome(normalized);
}

function longestPalindromicSubstring(text) {
    if (text.length === 0) {
        return "";
    }

    const characters = [...text];
    let bestStart = 0;
    let bestLength = 1;

    function expand(left, right) {
        while (
            left >= 0 &&
            right < characters.length &&
            characters[left] === characters[right]
        ) {
            left--;
            right++;
        }

        return {
            start: left + 1,
            length: right - left - 1
        };
    }

    for (let center = 0; center < characters.length; center++) {
        for (const [left, right] of [
            [center, center],
            [center, center + 1]
        ]) {
            const result = expand(left, right);

            if (result.length > bestLength) {
                bestStart = result.start;
                bestLength = result.length;
            }
        }
    }

    return characters.slice(bestStart, bestStart + bestLength).join("");
}

// ============================================================================
// 4. ANAGRAMS
// ============================================================================

function areAnagramsSorting(first, second) {
    const normalize = value => [...value.toLocaleLowerCase()].sort().join("");
    return normalize(first) === normalize(second);
}

function areAnagramsFrequency(first, second) {
    const firstCharacters = [...first.toLocaleLowerCase()];
    const secondCharacters = [...second.toLocaleLowerCase()];

    if (firstCharacters.length !== secondCharacters.length) {
        return false;
    }

    const firstFrequency = characterFrequency(first);
    const secondFrequency = characterFrequency(second);

    if (firstFrequency.size !== secondFrequency.size) {
        return false;
    }

    for (const [character, count] of firstFrequency) {
        if (secondFrequency.get(character) !== count) {
            return false;
        }
    }

    return true;
}

function groupAnagrams(words) {
    const groups = new Map();

    for (const word of words) {
        const key = [...word.toLocaleLowerCase()].sort().join("");

        if (!groups.has(key)) {
            groups.set(key, []);
        }

        groups.get(key).push(word);
    }

    return [...groups.values()];
}

// ============================================================================
// 5. SUBSTRING SEARCH
// ============================================================================

function naiveSearch(text, pattern) {
    if (pattern.length === 0) {
        return 0;
    }

    if (pattern.length > text.length) {
        return -1;
    }

    for (let start = 0; start <= text.length - pattern.length; start++) {
        let matched = true;

        for (let offset = 0; offset < pattern.length; offset++) {
            if (text[start + offset] !== pattern[offset]) {
                matched = false;
                break;
            }
        }

        if (matched) {
            return start;
        }
    }

    return -1;
}

function findAllOccurrences(text, pattern) {
    if (pattern.length === 0) {
        return Array.from({ length: text.length + 1 }, (_, index) => index);
    }

    const positions = [];

    for (let start = 0; start <= text.length - pattern.length; start++) {
        if (text.startsWith(pattern, start)) {
            positions.push(start);
        }
    }

    return positions;
}

function buildLPS(pattern) {
    const lps = new Array(pattern.length).fill(0);
    let prefixLength = 0;
    let index = 1;

    while (index < pattern.length) {
        if (pattern[index] === pattern[prefixLength]) {
            prefixLength++;
            lps[index] = prefixLength;
            index++;
        } else if (prefixLength > 0) {
            prefixLength = lps[prefixLength - 1];
        } else {
            lps[index] = 0;
            index++;
        }
    }

    return lps;
}

function kmpSearch(text, pattern) {
    if (pattern.length === 0) {
        return 0;
    }

    const lps = buildLPS(pattern);
    let textIndex = 0;
    let patternIndex = 0;

    while (textIndex < text.length) {
        if (text[textIndex] === pattern[patternIndex]) {
            textIndex++;
            patternIndex++;

            if (patternIndex === pattern.length) {
                return textIndex - patternIndex;
            }
        } else if (patternIndex > 0) {
            patternIndex = lps[patternIndex - 1];
        } else {
            textIndex++;
        }
    }

    return -1;
}

// ============================================================================
// 6. SUBSEQUENCES
// ============================================================================

function isSubsequence(candidate, text) {
    let candidateIndex = 0;

    for (const character of text) {
        if (
            candidateIndex < candidate.length &&
            character === candidate[candidateIndex]
        ) {
            candidateIndex++;
        }
    }

    return candidateIndex === candidate.length;
}

function countSubsequenceOccurrences(source, target) {
    const dp = new Array(target.length + 1).fill(0);
    dp[0] = 1;

    for (const sourceCharacter of source) {
        for (let targetIndex = target.length; targetIndex >= 1; targetIndex--) {
            if (sourceCharacter === target[targetIndex - 1]) {
                dp[targetIndex] += dp[targetIndex - 1];
            }
        }
    }

    return dp[target.length];
}

function lcsLength(first, second) {
    // Two-row DP reduces memory from O(n*m) to O(min(n,m)).
    if (first.length < second.length) {
        [first, second] = [second, first];
    }

    let previous = new Array(second.length + 1).fill(0);

    for (const firstCharacter of first) {
        const current = new Array(second.length + 1).fill(0);

        for (let j = 1; j <= second.length; j++) {
            if (firstCharacter === second[j - 1]) {
                current[j] = previous[j - 1] + 1;
            } else {
                current[j] = Math.max(previous[j], current[j - 1]);
            }
        }

        previous = current;
    }

    return previous[second.length];
}

function longestCommonSubsequence(first, second) {
    const rows = first.length + 1;
    const columns = second.length + 1;
    const dp = Array.from(
        { length: rows },
        () => new Array(columns).fill("")
    );

    for (let i = 1; i < rows; i++) {
        for (let j = 1; j < columns; j++) {
            if (first[i - 1] === second[j - 1]) {
                dp[i][j] = dp[i - 1][j - 1] + first[i - 1];
            } else {
                dp[i][j] =
                    dp[i - 1][j].length >= dp[i][j - 1].length
                        ? dp[i - 1][j]
                        : dp[i][j - 1];
            }
        }
    }

    return dp[rows - 1][columns - 1];
}

// ============================================================================
// 7. SLIDING WINDOWS
// ============================================================================

function longestSubstringWithoutRepeating(text) {
    const lastSeen = new Map();
    let left = 0;
    let bestStart = 0;
    let bestLength = 0;

    for (let right = 0; right < text.length; right++) {
        const character = text[right];

        if (lastSeen.has(character) && lastSeen.get(character) >= left) {
            left = lastSeen.get(character) + 1;
        }

        lastSeen.set(character, right);

        const currentLength = right - left + 1;

        if (currentLength > bestLength) {
            bestStart = left;
            bestLength = currentLength;
        }
    }

    return text.slice(bestStart, bestStart + bestLength);
}

function minimumWindowSubstring(text, target) {
    if (target.length === 0) {
        return "";
    }

    const required = characterFrequency(target);
    let remaining = [...target].length;
    let left = 0;
    let bestStart = 0;
    let bestLength = Infinity;

    for (let right = 0; right < text.length; right++) {
        const character = text[right];

        if (required.has(character)) {
            if (required.get(character) > 0) {
                remaining--;
            }

            required.set(character, required.get(character) - 1);
        }

        while (remaining === 0) {
            const currentLength = right - left + 1;

            if (currentLength < bestLength) {
                bestStart = left;
                bestLength = currentLength;
            }

            const leftCharacter = text[left];

            if (required.has(leftCharacter)) {
                required.set(
                    leftCharacter,
                    required.get(leftCharacter) + 1
                );

                if (required.get(leftCharacter) > 0) {
                    remaining++;
                }
            }

            left++;
        }
    }

    return bestLength === Infinity
        ? ""
        : text.slice(bestStart, bestStart + bestLength);
}

function longestRepeatingReplacement(text, replacementBudget) {
    if (!Number.isInteger(replacementBudget) || replacementBudget < 0) {
        throw new RangeError("replacementBudget must be a non-negative integer");
    }

    const frequencies = new Map();
    let left = 0;
    let maxFrequency = 0;
    let best = 0;

    for (let right = 0; right < text.length; right++) {
        const character = text[right];

        frequencies.set(
            character,
            (frequencies.get(character) ?? 0) + 1
        );

        maxFrequency = Math.max(maxFrequency, frequencies.get(character));

        while (right - left + 1 - maxFrequency > replacementBudget) {
            const leftCharacter = text[left];
            frequencies.set(
                leftCharacter,
                frequencies.get(leftCharacter) - 1
            );
            left++;
        }

        best = Math.max(best, right - left + 1);
    }

    return best;
}

// ============================================================================
// 8. TRANSFORMATIONS
// ============================================================================

function reverseWords(text) {
    return text.trim().split(/\s+/).filter(Boolean).reverse().join(" ");
}

function reverseEachWord(text) {
    return text.trim()
        .split(/\s+/)
        .filter(Boolean)
        .map(word => [...word].reverse().join(""))
        .join(" ");
}

function rotateString(text, shift) {
    if (text.length === 0) {
        return "";
    }

    shift = ((shift % text.length) + text.length) % text.length;

    return text.slice(shift) + text.slice(0, shift);
}

function areRotations(first, second) {
    return first.length === second.length && (first + first).includes(second);
}

function compressString(text) {
    if (text.length === 0) {
        return "";
    }

    let output = "";
    let count = 1;

    for (let index = 1; index <= text.length; index++) {
        if (index < text.length && text[index] === text[index - 1]) {
            count++;
        } else {
            output += text[index - 1] + String(count);
            count = 1;
        }
    }

    return output;
}

function decompressString(encoded) {
    let output = "";
    let index = 0;

    while (index < encoded.length) {
        const character = encoded[index++];

        if (index >= encoded.length || !/[0-9]/.test(encoded[index])) {
            throw new Error("Invalid run-length encoding");
        }

        let digits = "";

        while (index < encoded.length && /[0-9]/.test(encoded[index])) {
            digits += encoded[index++];
        }

        const count = Number(digits);

        if (!Number.isSafeInteger(count) || count < 0) {
            throw new Error("Invalid run length");
        }

        output += character.repeat(count);
    }

    return output;
}

// ============================================================================
// 9. EDIT DISTANCE
// ============================================================================

function levenshteinDistance(first, second) {
    if (first.length < second.length) {
        [first, second] = [second, first];
    }

    let previous = Array.from(
        { length: second.length + 1 },
        (_, index) => index
    );

    for (let i = 1; i <= first.length; i++) {
        const current = [i];

        for (let j = 1; j <= second.length; j++) {
            const insertion = current[j - 1] + 1;
            const deletion = previous[j] + 1;
            const substitution =
                previous[j - 1] + (first[i - 1] === second[j - 1] ? 0 : 1);

            current.push(Math.min(insertion, deletion, substitution));
        }

        previous = current;
    }

    return previous[second.length];
}

// ============================================================================
// 10. STRING STRUCTURES
// ============================================================================

class TrieNode {
    constructor() {
        this.children = new Map();
        this.isWord = false;
    }
}

class Trie {
    constructor() {
        this.root = new TrieNode();
    }

    insert(word) {
        let node = this.root;

        for (const character of word) {
            if (!node.children.has(character)) {
                node.children.set(character, new TrieNode());
            }

            node = node.children.get(character);
        }

        node.isWord = true;
    }

    contains(word) {
        let node = this.root;

        for (const character of word) {
            if (!node.children.has(character)) {
                return false;
            }

            node = node.children.get(character);
        }

        return node.isWord;
    }

    startsWith(prefix) {
        let node = this.root;

        for (const character of prefix) {
            if (!node.children.has(character)) {
                return false;
            }

            node = node.children.get(character);
        }

        return true;
    }

    wordsWithPrefix(prefix) {
        let node = this.root;

        for (const character of prefix) {
            if (!node.children.has(character)) {
                return [];
            }

            node = node.children.get(character);
        }

        const results = [];

        function collect(currentNode, currentWord) {
            if (currentNode.isWord) {
                results.push(currentWord);
            }

            const children = [...currentNode.children.entries()]
                .sort(([first], [second]) => first.localeCompare(second));

            for (const [character, child] of children) {
                collect(child, currentWord + character);
            }
        }

        collect(node, prefix);
        return results;
    }
}

// ============================================================================
// 11. VALIDATION AND COMPARISON
// ============================================================================

function areIsomorphic(first, second) {
    if (first.length !== second.length) {
        return false;
    }

    const firstToSecond = new Map();
    const secondToFirst = new Map();

    for (let index = 0; index < first.length; index++) {
        const a = first[index];
        const b = second[index];

        if (firstToSecond.has(a) && firstToSecond.get(a) !== b) {
            return false;
        }

        if (secondToFirst.has(b) && secondToFirst.get(b) !== a) {
            return false;
        }

        firstToSecond.set(a, b);
        secondToFirst.set(b, a);
    }

    return true;
}

function canFormPalindrome(text) {
    let oddCount = 0;

    for (const count of characterFrequency(text).values()) {
        if (count % 2 !== 0) {
            oddCount++;
        }
    }

    return oddCount <= 1;
}

function oneEditApart(first, second) {
    const firstCharacters = [...first];
    const secondCharacters = [...second];

    if (Math.abs(firstCharacters.length - secondCharacters.length) > 1) {
        return false;
    }

    if (firstCharacters.length === secondCharacters.length) {
        let differences = 0;

        for (let index = 0; index < firstCharacters.length; index++) {
            if (firstCharacters[index] !== secondCharacters[index]) {
                differences++;
            }
        }

        return differences <= 1;
    }

    let shorter = firstCharacters;
    let longer = secondCharacters;

    if (shorter.length > longer.length) {
        [shorter, longer] = [longer, shorter];
    }

    let left = 0;
    let right = 0;
    let differences = 0;

    while (left < shorter.length && right < longer.length) {
        if (shorter[left] === longer[right]) {
            left++;
            right++;
        } else {
            differences++;
            right++;

            if (differences > 1) {
                return false;
            }
        }
    }

    return true;
}

// ============================================================================
// 12. ASYNCHRONOUS APPLICATION-LEVEL DEMONSTRATION
// ============================================================================

function delayedTextAnalysis(text, delayMilliseconds = 20) {
    /*
     * Promise-based APIs model asynchronous application work.
     * The string algorithms themselves remain synchronous, but the
     * surrounding application can schedule analysis asynchronously.
     */
    return new Promise(resolve => {
        setTimeout(() => {
            resolve({
                text,
                length: [...text].length,
                frequency: mapToObject(characterFrequency(text)),
                palindrome: isValidPalindrome(text)
            });
        }, delayMilliseconds);
    });
}

async function demonstrateAsyncAnalysis() {
    const result = await delayedTextAnalysis("level");
    console.log("\n=== ASYNCHRONOUS ANALYSIS ===");
    console.log(result);
}

// ============================================================================
// 13. TESTS
// ============================================================================

function assert(condition, message) {
    if (!condition) {
        throw new Error(`Assertion failed: ${message}`);
    }
}

function runTests() {
    assert(isPalindrome("racecar"), "racecar is a palindrome");
    assert(!isPalindrome("hello"), "hello is not a palindrome");
    assert(
        isValidPalindrome("A man, a plan, a canal: Panama"),
        "normalized palindrome"
    );

    assert(
        areAnagramsFrequency("listen", "silent"),
        "listen/silent anagram"
    );

    assert(
        !areAnagramsFrequency("abc", "abd"),
        "different strings are not anagrams"
    );

    assert(
        firstNonRepeatingCharacter("swiss") === "w",
        "first non-repeating character"
    );

    assert(
        firstRepeatingCharacter("abca") === "a",
        "first repeating character"
    );

    assert(
        naiveSearch("hello world", "world") === 6,
        "naive search"
    );

    assert(
        kmpSearch("ababcabcabababd", "ababd") === 10,
        "KMP search"
    );

    assert(
        JSON.stringify(findAllOccurrences("aaaa", "aa")) ===
        JSON.stringify([0, 1, 2]),
        "overlapping occurrences"
    );

    assert(isSubsequence("ace", "abcde"), "subsequence");
    assert(!isSubsequence("aec", "abcde"), "invalid subsequence");

    assert(
        countSubsequenceOccurrences("babgbag", "bag") === 5,
        "subsequence count"
    );

    assert(
        longestCommonSubsequence("abcde", "ace") === "ace",
        "LCS"
    );

    assert(
        lcsLength("abcde", "ace") === 3,
        "LCS length"
    );

    assert(
        longestSubstringWithoutRepeating("abcabcbb") === "abc",
        "longest unique substring"
    );

    assert(
        minimumWindowSubstring("ADOBECODEBANC", "ABC") === "BANC",
        "minimum window"
    );

    assert(
        longestRepeatingReplacement("AABABBA", 1) === 4,
        "replacement window"
    );

    assert(
        reverseWords("  one   two three ") === "three two one",
        "reverse words"
    );

    assert(
        rotateString("abcdef", 2) === "cdefab",
        "rotation"
    );

    assert(
        areRotations("waterbottle", "erbottlewat"),
        "rotation comparison"
    );

    assert(
        decompressString(compressString("aaabccccdd")) === "aaabccccdd",
        "compression round trip"
    );

    assert(
        levenshteinDistance("kitten", "sitting") === 3,
        "edit distance"
    );

    assert(oneEditApart("pale", "ple"), "one edit");
    assert(!oneEditApart("pale", "bake"), "more than one edit");

    assert(areIsomorphic("egg", "add"), "isomorphic strings");
    assert(!areIsomorphic("foo", "bar"), "non-isomorphic strings");

    assert(canFormPalindrome("carrace"), "rearrangeable palindrome");
    assert(!canFormPalindrome("daily"), "not rearrangeable");

    const trie = new Trie();

    for (const word of ["apple", "app", "apply", "banana"]) {
        trie.insert(word);
    }

    assert(trie.contains("apple"), "trie contains apple");
    assert(trie.contains("app"), "trie contains app");
    assert(!trie.contains("apples"), "trie rejects apples");
    assert(trie.startsWith("ap"), "trie prefix");

    console.log("\nAll JavaScript tests passed.");
}

// ============================================================================
// 14. PERFORMANCE COMPARISON
// ============================================================================

function demonstratePerformance() {
    const text = "a".repeat(50000) + "b";
    const pattern = "aaab";

    console.log("\n=== PERFORMANCE CHARACTERISTICS ===");
    console.log("Input text length:", text.length);
    console.log("Naive search is O(n*m) in the worst case.");
    console.log("KMP search is O(n+m).");

    console.time("KMP");
    const result = kmpSearch(text, pattern);
    console.timeEnd("KMP");

    console.log("KMP result:", result);
    console.log(
        "For production applications, built-in String methods are usually"
        + " preferable unless a specific algorithmic requirement exists."
    );
}

// ============================================================================
// 15. MAIN
// ============================================================================

async function main() {
    demonstrateStringFundamentals();

    console.log("\n=== CHARACTER FREQUENCY ===");
    console.log(mapToObject(characterFrequency("banana")));
    console.log("First non-repeating:", firstNonRepeatingCharacter("swiss"));
    console.log("First repeating:", firstRepeatingCharacter("abca"));
    console.log("Most frequent:", mostFrequentCharacter("banana"));

    console.log("\n=== PALINDROMES ===");
    console.log(isValidPalindrome("A man, a plan, a canal: Panama"));
    console.log(
        "Longest:",
        longestPalindromicSubstring("forgeeksskeegfor")
    );

    console.log("\n=== ANAGRAMS ===");
    console.log(areAnagramsSorting("listen", "silent"));
    console.log(
        groupAnagrams(["eat", "tea", "tan", "ate", "nat", "bat"])
    );

    console.log("\n=== SUBSTRINGS ===");
    console.log("Naive:", naiveSearch("hello world", "world"));
    console.log("KMP:", kmpSearch("ababcabcabababd", "ababd"));
    console.log("LPS:", buildLPS("ababaca"));

    console.log("\n=== SUBSEQUENCES ===");
    console.log(isSubsequence("ace", "abcde"));
    console.log(countSubsequenceOccurrences("babgbag", "bag"));
    console.log(longestCommonSubsequence("AGGTAB", "GXTXAYB"));

    console.log("\n=== SLIDING WINDOW ===");
    console.log(longestSubstringWithoutRepeating("pwwkew"));
    console.log(minimumWindowSubstring("ADOBECODEBANC", "ABC"));
    console.log(longestRepeatingReplacement("AABABBA", 1));

    console.log("\n=== TRANSFORMATIONS ===");
    console.log(reverseWords("JavaScript string pattern problems"));
    console.log(reverseEachWord("JavaScript strings"));
    console.log(rotateString("abcdefgh", 3));

    const compressed = compressString("aaabccccccdd");
    console.log("Compressed:", compressed);
    console.log("Decompressed:", decompressString(compressed));

    console.log("\n=== TRIE ===");
    const trie = new Trie();

    for (const word of ["car", "card", "care", "cat", "catalog"]) {
        trie.insert(word);
    }

    console.log("Prefix ca:", trie.wordsWithPrefix("ca"));

    await demonstrateAsyncAnalysis();
    demonstratePerformance();
    runTests();

    console.log("\nJavaScript string-pattern study completed.");
}

main().catch(error => {
    console.error("Program failed:", error);
    process.exitCode = 1;
});
