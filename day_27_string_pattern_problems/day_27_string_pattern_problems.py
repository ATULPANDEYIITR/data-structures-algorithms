"""
STRING PATTERN PROBLEMS
=======================

A comprehensive standalone study file covering:

- Strings and character access
- Character frequency
- Palindromes
- Anagrams
- Substrings and subsequences
- String transformation
- Two-pointer techniques
- Sliding windows
- Hash-map based techniques
- Sorting and counting techniques
- Dynamic programming
- Edit distance
- Longest common subsequence
- Longest palindromic subsequence
- Pattern matching
- Run-length encoding
- String rotation
- Edge cases and validation
- Complexity analysis
- Testing and debugging

The examples are executable and use only the Python standard library.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable, Iterator


# ============================================================================
# 1. FUNDAMENTALS
# ============================================================================

def demonstrate_string_fundamentals() -> None:
    """Introduce Python strings and their most important basic operations."""
    text = "Algorithm"

    print("\n=== STRING FUNDAMENTALS ===")
    print("Original:", text)
    print("Length:", len(text))
    print("First character:", text[0])
    print("Last character:", text[-1])
    print("First four:", text[:4])
    print("From index 4:", text[4:])
    print("Reversed:", text[::-1])
    print("Uppercase:", text.upper())
    print("Lowercase:", text.lower())
    print("Contains 'go':", "go" in text.lower())

    # Strings are immutable. A new string must be created for a change.
    changed = text[:3] + "X" + text[4:]
    print("Changed:", changed)


def normalize_text(text: str, *, ignore_case: bool = True,
                   alphanumeric_only: bool = False) -> str:
    """
    Normalize text for problems where punctuation, spaces, or case
    should not affect the comparison.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    result = text.casefold() if ignore_case else text

    if alphanumeric_only:
        result = "".join(character for character in result if character.isalnum())

    return result


# ============================================================================
# 2. CHARACTER FREQUENCY
# ============================================================================

def character_frequency(text: str) -> dict[str, int]:
    """Count every character using a dictionary."""
    frequencies: dict[str, int] = {}

    for character in text:
        frequencies[character] = frequencies.get(character, 0) + 1

    return frequencies


def character_frequency_counter(text: str) -> Counter[str]:
    """The standard-library Counter implementation of frequency counting."""
    return Counter(text)


def first_non_repeating_character(text: str) -> str | None:
    """
    Return the first character whose frequency is exactly one.
    A second pass preserves the original order.
    """
    frequencies = Counter(text)

    for character in text:
        if frequencies[character] == 1:
            return character

    return None


def first_repeating_character(text: str) -> str | None:
    """Return the first character encountered for the second time."""
    seen: set[str] = set()

    for character in text:
        if character in seen:
            return character
        seen.add(character)

    return None


def most_frequent_character(text: str) -> tuple[str, int] | None:
    """Return one most frequent character and its frequency."""
    if not text:
        return None

    frequencies = Counter(text)
    character, frequency = frequencies.most_common(1)[0]
    return character, frequency


# ============================================================================
# 3. PALINDROMES
# ============================================================================

def is_palindrome_simple(text: str) -> bool:
    """Compare a string with its reverse."""
    return text == text[::-1]


def is_palindrome_two_pointer(text: str) -> bool:
    """
    Two-pointer palindrome test.

    Time: O(n)
    Extra space: O(1), ignoring Python string indexing.
    """
    left = 0
    right = len(text) - 1

    while left < right:
        if text[left] != text[right]:
            return False
        left += 1
        right -= 1

    return True


def is_valid_palindrome(text: str) -> bool:
    """
    Case-insensitive palindrome test that ignores non-alphanumeric
    characters.
    """
    normalized = normalize_text(
        text,
        ignore_case=True,
        alphanumeric_only=True,
    )
    return is_palindrome_two_pointer(normalized)


def longest_palindromic_substring(text: str) -> str:
    """
    Expand around every possible center.

    Each character can be the center of an odd-length palindrome.
    Each gap can be the center of an even-length palindrome.

    Time: O(n^2)
    Extra space: O(1), excluding the returned substring.
    """
    if not text:
        return ""

    best_start = 0
    best_length = 1

    def expand(left: int, right: int) -> tuple[int, int]:
        while left >= 0 and right < len(text) and text[left] == text[right]:
            left -= 1
            right += 1

        start = left + 1
        length = right - left - 1
        return start, length

    for center in range(len(text)):
        start, length = expand(center, center)
        if length > best_length:
            best_start, best_length = start, length

        start, length = expand(center, center + 1)
        if length > best_length:
            best_start, best_length = start, length

    return text[best_start:best_start + best_length]


# ============================================================================
# 4. ANAGRAMS
# ============================================================================

def are_anagrams_sorting(first: str, second: str) -> bool:
    """
    Anagram test using sorting.

    Time: O(n log n)
    Space: O(n) in typical implementations because sorting creates data.
    """
    return sorted(first.casefold()) == sorted(second.casefold())


def are_anagrams_frequency(first: str, second: str) -> bool:
    """
    Anagram test using frequency counting.

    Time: O(n)
    Space: O(k), where k is the number of distinct characters.
    """
    if len(first) != len(second):
        return False

    return Counter(first.casefold()) == Counter(second.casefold())


def are_anagrams_ignoring_spaces(first: str, second: str) -> bool:
    """Anagram comparison after removing whitespace and ignoring case."""
    first_normalized = "".join(first.casefold().split())
    second_normalized = "".join(second.casefold().split())

    return Counter(first_normalized) == Counter(second_normalized)


def group_anagrams(words: Iterable[str]) -> list[list[str]]:
    """
    Group words whose character multisets are identical.

    The sorted tuple is used as a canonical signature.
    """
    groups: dict[tuple[str, ...], list[str]] = defaultdict(list)

    for word in words:
        signature = tuple(sorted(word.casefold()))
        groups[signature].append(word)

    return list(groups.values())


def group_anagrams_by_frequency(words: Iterable[str]) -> list[list[str]]:
    """
    Frequency-based grouping.

    This avoids sorting every word and is useful when the alphabet is bounded.
    """
    groups: dict[tuple[tuple[str, int], ...], list[str]] = defaultdict(list)

    for word in words:
        signature = tuple(sorted(Counter(word.casefold()).items()))
        groups[signature].append(word)

    return list(groups.values())


# ============================================================================
# 5. SUBSTRING PROBLEMS
# ============================================================================

def contains_substring(text: str, pattern: str) -> bool:
    """
    Basic substring search using Python's optimized implementation.

    Empty strings are considered substrings of every string.
    """
    return pattern in text


def find_all_occurrences(text: str, pattern: str) -> list[int]:
    """
    Return every starting position of pattern.

    Overlapping matches are included.
    Example: find_all_occurrences("aaaa", "aa") -> [0, 1, 2]
    """
    if pattern == "":
        return list(range(len(text) + 1))

    positions: list[int] = []
    start = 0

    while True:
        index = text.find(pattern, start)
        if index == -1:
            break

        positions.append(index)
        start = index + 1

    return positions


def naive_pattern_search(text: str, pattern: str) -> int:
    """
    Naive exact pattern matching.

    Worst-case time: O(n*m)
    Extra space: O(1)
    """
    if pattern == "":
        return 0

    if len(pattern) > len(text):
        return -1

    for start in range(len(text) - len(pattern) + 1):
        matched = True

        for offset in range(len(pattern)):
            if text[start + offset] != pattern[offset]:
                matched = False
                break

        if matched:
            return start

    return -1


def build_lps(pattern: str) -> list[int]:
    """
    Build the Longest Proper Prefix which is also Suffix array for KMP.

    lps[i] tells us how far the pattern can fall back after a mismatch.
    """
    lps = [0] * len(pattern)
    prefix_length = 0
    index = 1

    while index < len(pattern):
        if pattern[index] == pattern[prefix_length]:
            prefix_length += 1
            lps[index] = prefix_length
            index += 1
        elif prefix_length:
            prefix_length = lps[prefix_length - 1]
        else:
            lps[index] = 0
            index += 1

    return lps


def kmp_search(text: str, pattern: str) -> int:
    """
    Knuth-Morris-Pratt pattern search.

    Preprocessing: O(m)
    Search: O(n)
    Total: O(n + m)
    """
    if pattern == "":
        return 0

    lps = build_lps(pattern)
    text_index = 0
    pattern_index = 0

    while text_index < len(text):
        if text[text_index] == pattern[pattern_index]:
            text_index += 1
            pattern_index += 1

            if pattern_index == len(pattern):
                return text_index - pattern_index
        elif pattern_index:
            pattern_index = lps[pattern_index - 1]
        else:
            text_index += 1

    return -1


# ============================================================================
# 6. SUBSEQUENCES
# ============================================================================

def is_subsequence(candidate: str, text: str) -> bool:
    """
    Determine whether candidate is a subsequence of text.

    Characters must occur in order but need not be adjacent.
    """
    candidate_index = 0

    for character in text:
        if candidate_index < len(candidate) and character == candidate[candidate_index]:
            candidate_index += 1

    return candidate_index == len(candidate)


def count_subsequence_occurrences(source: str, target: str) -> int:
    """
    Count how many distinct index selections form target as a subsequence.

    Dynamic programming:
    dp[j] = number of ways to form target[:j] using processed source chars.
    """
    if not target:
        return 1

    dp = [0] * (len(target) + 1)
    dp[0] = 1

    for source_character in source:
        for target_index in range(len(target), 0, -1):
            if source_character == target[target_index - 1]:
                dp[target_index] += dp[target_index - 1]

    return dp[-1]


def longest_common_subsequence(first: str, second: str) -> str:
    """
    Return one longest common subsequence.

    Time: O(n*m)
    Space: O(n*m)
    """
    rows = len(first) + 1
    columns = len(second) + 1

    dp = [[""] * columns for _ in range(rows)]

    for i in range(1, rows):
        for j in range(1, columns):
            if first[i - 1] == second[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + first[i - 1]
            else:
                upper = dp[i - 1][j]
                left = dp[i][j - 1]
                dp[i][j] = upper if len(upper) >= len(left) else left

    return dp[-1][-1]


def lcs_length_optimized(first: str, second: str) -> int:
    """
    Compute LCS length using only two rows.

    Time: O(n*m)
    Space: O(min(n, m))
    """
    if len(first) < len(second):
        first, second = second, first

    previous = [0] * (len(second) + 1)

    for first_character in first:
        current = [0] * (len(second) + 1)

        for j, second_character in enumerate(second, start=1):
            if first_character == second_character:
                current[j] = previous[j - 1] + 1
            else:
                current[j] = max(previous[j], current[j - 1])

        previous = current

    return previous[-1]


# ============================================================================
# 7. SLIDING WINDOW PROBLEMS
# ============================================================================

def longest_substring_without_repeating(text: str) -> str:
    """
    Sliding-window solution.

    Time: O(n)
    Space: O(k), where k is the number of distinct characters in the window.
    """
    left = 0
    best_start = 0
    best_length = 0
    last_seen: dict[str, int] = {}

    for right, character in enumerate(text):
        if character in last_seen and last_seen[character] >= left:
            left = last_seen[character] + 1

        last_seen[character] = right

        current_length = right - left + 1

        if current_length > best_length:
            best_start = left
            best_length = current_length

    return text[best_start:best_start + best_length]


def minimum_window_substring(text: str, target: str) -> str:
    """
    Find the smallest substring containing all target characters,
    including repeated characters.

    Time: O(n)
    Space: O(k)
    """
    if not target:
        return ""

    required = Counter(target)
    remaining = len(target)
    left = 0
    best_start = 0
    best_length = float("inf")

    for right, character in enumerate(text):
        if character in required:
            if required[character] > 0:
                remaining -= 1
            required[character] -= 1

        while remaining == 0:
            current_length = right - left + 1

            if current_length < best_length:
                best_start = left
                best_length = current_length

            left_character = text[left]

            if left_character in required:
                required[left_character] += 1

                if required[left_character] > 0:
                    remaining += 1

            left += 1

    if best_length == float("inf"):
        return ""

    return text[best_start:best_start + int(best_length)]


def longest_repeating_replacement(text: str, replacement_budget: int) -> int:
    """
    Longest substring that can be converted into one repeated character
    using at most replacement_budget replacements.

    Window validity:
        window_size - maximum_frequency <= replacement_budget
    """
    if replacement_budget < 0:
        raise ValueError("replacement_budget cannot be negative")

    frequencies = Counter()
    left = 0
    best = 0
    max_frequency = 0

    for right, character in enumerate(text):
        frequencies[character] += 1
        max_frequency = max(max_frequency, frequencies[character])

        while (right - left + 1) - max_frequency > replacement_budget:
            frequencies[text[left]] -= 1
            left += 1

        best = max(best, right - left + 1)

    return best


# ============================================================================
# 8. STRING TRANSFORMATION
# ============================================================================

def reverse_words(text: str) -> str:
    """
    Reverse word order while treating arbitrary whitespace as separators.
    """
    return " ".join(text.split()[::-1])


def reverse_each_word(text: str) -> str:
    """Reverse characters inside each whitespace-separated word."""
    return " ".join(word[::-1] for word in text.split())


def rotate_string(text: str, shift: int) -> str:
    """
    Left rotation by shift positions.

    Python modulo handles shifts larger than the string length.
    """
    if not text:
        return ""

    shift %= len(text)
    return text[shift:] + text[:shift]


def are_rotations(first: str, second: str) -> bool:
    """
    Two strings are rotations if second occurs in first + first,
    provided their lengths are equal.
    """
    return len(first) == len(second) and second in first + first


def compress_string(text: str) -> str:
    """
    Run-length encoding.

    Example:
        aaabbc -> a3b2c1

    This is educational compression, not a general-purpose compressor.
    """
    if not text:
        return ""

    pieces: list[str] = []
    count = 1

    for index in range(1, len(text) + 1):
        if index < len(text) and text[index] == text[index - 1]:
            count += 1
        else:
            pieces.append(f"{text[index - 1]}{count}")
            count = 1

    return "".join(pieces)


def decompress_string(encoded: str) -> str:
    """
    Decode the output of compress_string.

    The format is character followed by one or more decimal digits.
    """
    if not encoded:
        return ""

    output: list[str] = []
    index = 0

    while index < len(encoded):
        character = encoded[index]
        index += 1

        if index >= len(encoded) or not encoded[index].isdigit():
            raise ValueError("Invalid run-length encoding")

        digits_start = index

        while index < len(encoded) and encoded[index].isdigit():
            index += 1

        count = int(encoded[digits_start:index])

        if count < 0:
            raise ValueError("Run length cannot be negative")

        output.append(character * count)

    return "".join(output)


# ============================================================================
# 9. EDIT DISTANCE
# ============================================================================

def levenshtein_distance(first: str, second: str) -> int:
    """
    Compute minimum insertions, deletions, and substitutions.

    Time: O(n*m)
    Space: O(min(n, m))
    """
    if len(first) < len(second):
        first, second = second, first

    previous = list(range(len(second) + 1))

    for i, first_character in enumerate(first, start=1):
        current = [i]

        for j, second_character in enumerate(second, start=1):
            insertion = current[j - 1] + 1
            deletion = previous[j] + 1
            substitution = previous[j - 1] + (first_character != second_character)

            current.append(min(insertion, deletion, substitution))

        previous = current

    return previous[-1]


def edit_operations(first: str, second: str) -> list[str]:
    """
    Construct one minimum edit sequence.

    The matrix is retained because reconstructing the actual operations
    requires the decisions made during dynamic programming.
    """
    rows = len(first) + 1
    columns = len(second) + 1

    dp = [[0] * columns for _ in range(rows)]

    for i in range(rows):
        dp[i][0] = i

    for j in range(columns):
        dp[0][j] = j

    for i in range(1, rows):
        for j in range(1, columns):
            if first[i - 1] == second[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j],       # deletion
                    dp[i][j - 1],       # insertion
                    dp[i - 1][j - 1],   # substitution
                )

    operations: list[str] = []
    i = len(first)
    j = len(second)

    while i > 0 or j > 0:
        if i > 0 and j > 0 and first[i - 1] == second[j - 1]:
            operations.append(f"Keep '{first[i - 1]}'")
            i -= 1
            j -= 1
        elif i > 0 and j > 0 and dp[i][j] == dp[i - 1][j - 1] + 1:
            operations.append(
                f"Replace '{first[i - 1]}' with '{second[j - 1]}'"
            )
            i -= 1
            j -= 1
        elif i > 0 and dp[i][j] == dp[i - 1][j] + 1:
            operations.append(f"Delete '{first[i - 1]}'")
            i -= 1
        else:
            operations.append(f"Insert '{second[j - 1]}'")
            j -= 1

    operations.reverse()
    return operations


# ============================================================================
# 10. LONGEST PALINDROMIC SUBSEQUENCE
# ============================================================================

def longest_palindromic_subsequence(text: str) -> str:
    """
    Find one longest palindromic subsequence.

    Unlike longest_palindromic_substring, characters need not be adjacent.

    Time: O(n^2)
    Space: O(n^2)
    """
    n = len(text)

    if n == 0:
        return ""

    dp = [[""] * n for _ in range(n)]

    for i in range(n):
        dp[i][i] = text[i]

    for length in range(2, n + 1):
        for left in range(n - length + 1):
            right = left + length - 1

            if text[left] == text[right]:
                if length == 2:
                    dp[left][right] = text[left] + text[right]
                else:
                    dp[left][right] = (
                        text[left] + dp[left + 1][right - 1] + text[right]
                    )
            else:
                first_option = dp[left + 1][right]
                second_option = dp[left][right - 1]

                dp[left][right] = (
                    first_option
                    if len(first_option) >= len(second_option)
                    else second_option
                )

    return dp[0][n - 1]


# ============================================================================
# 11. WORD BREAK
# ============================================================================

def word_break(text: str, dictionary: set[str]) -> bool:
    """
    Determine whether text can be segmented into dictionary words.

    dp[i] means text[:i] can be segmented.
    """
    dp = [False] * (len(text) + 1)
    dp[0] = True

    for end in range(1, len(text) + 1):
        for start in range(end):
            if dp[start] and text[start:end] in dictionary:
                dp[end] = True
                break

    return dp[-1]


def all_word_breaks(text: str, dictionary: set[str]) -> list[str]:
    """Return all dictionary-based segmentations for manageable inputs."""
    @lru_cache(maxsize=None)
    def solve(start: int) -> tuple[str, ...]:
        if start == len(text):
            return ("",)

        results: list[str] = []

        for end in range(start + 1, len(text) + 1):
            word = text[start:end]

            if word not in dictionary:
                continue

            for suffix in solve(end):
                results.append(word if not suffix else word + " " + suffix)

        return tuple(results)

    return list(solve(0))


# ============================================================================
# 12. PREFIX AND SUFFIX PROBLEMS
# ============================================================================

def longest_common_prefix(words: list[str]) -> str:
    """Find the longest prefix shared by all strings."""
    if not words:
        return ""

    prefix = words[0]

    for word in words[1:]:
        common_length = 0

        for first_character, second_character in zip(prefix, word):
            if first_character != second_character:
                break
            common_length += 1

        prefix = prefix[:common_length]

        if not prefix:
            break

    return prefix


def longest_common_suffix(words: list[str]) -> str:
    """Find the longest suffix shared by all strings."""
    if not words:
        return ""

    reversed_words = [word[::-1] for word in words]
    return longest_common_prefix(reversed_words)[::-1]


# ============================================================================
# 13. DISTINCT CHARACTER AND TRANSFORMATION PROBLEMS
# ============================================================================

def remove_duplicate_characters(text: str) -> str:
    """Keep the first occurrence of each character."""
    seen: set[str] = set()
    output: list[str] = []

    for character in text:
        if character not in seen:
            seen.add(character)
            output.append(character)

    return "".join(output)


def are_isomorphic(first: str, second: str) -> bool:
    """
    Two strings are isomorphic if characters in one can be mapped
    one-to-one to characters in the other.
    """
    if len(first) != len(second):
        return False

    first_to_second: dict[str, str] = {}
    second_to_first: dict[str, str] = {}

    for first_character, second_character in zip(first, second):
        if first_character in first_to_second:
            if first_to_second[first_character] != second_character:
                return False
        else:
            first_to_second[first_character] = second_character

        if second_character in second_to_first:
            if second_to_first[second_character] != first_character:
                return False
        else:
            second_to_first[second_character] = first_character

    return True


def can_form_palindrome(text: str) -> bool:
    """
    A string can be rearranged into a palindrome iff at most one character
    has odd frequency.
    """
    odd_count = sum(count % 2 for count in Counter(text).values())
    return odd_count <= 1


def one_edit_apart(first: str, second: str) -> bool:
    """
    Determine whether strings differ by at most one insertion, deletion,
    or substitution.
    """
    if abs(len(first) - len(second)) > 1:
        return False

    if len(first) == len(second):
        differences = sum(a != b for a, b in zip(first, second))
        return differences <= 1

    if len(first) > len(second):
        first, second = second, first

    left = right = 0
    differences = 0

    while left < len(first) and right < len(second):
        if first[left] == second[right]:
            left += 1
            right += 1
        else:
            differences += 1
            right += 1

            if differences > 1:
                return False

    return True


# ============================================================================
# 14. PARSING AND VALIDATION
# ============================================================================

def is_valid_integer_string(text: str) -> bool:
    """
    Validate a signed decimal integer without using int().

    Examples:
        "123" -> True
        "-42" -> True
        "+8" -> True
        "" -> False
        "+" -> False
    """
    if not text:
        return False

    start = 1 if text[0] in "+-" else 0

    if start == len(text):
        return False

    return all(character.isdigit() for character in text[start:])


def parse_integer_string(text: str) -> int:
    """Convert a validated signed decimal string manually."""
    if not is_valid_integer_string(text):
        raise ValueError(f"Invalid integer string: {text!r}")

    sign = -1 if text[0] == "-" else 1
    start = 1 if text[0] in "+-" else 0
    value = 0

    for character in text[start:]:
        value = value * 10 + (ord(character) - ord("0"))

    return sign * value


# ============================================================================
# 15. ADVANCED: TRIE
# ============================================================================

@dataclass
class TrieNode:
    children: dict[str, "TrieNode"]
    is_word: bool = False

    def __init__(self) -> None:
        self.children = {}
        self.is_word = False


class Trie:
    """
    Prefix tree.

    Average operations depend on word length rather than total dictionary
    size. A trie is useful for autocomplete, prefix search, and dictionaries.
    """

    def __init__(self) -> None:
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root

        for character in word:
            node = node.children.setdefault(character, TrieNode())

        node.is_word = True

    def contains(self, word: str) -> bool:
        node = self.root

        for character in word:
            if character not in node.children:
                return False
            node = node.children[character]

        return node.is_word

    def starts_with(self, prefix: str) -> bool:
        node = self.root

        for character in prefix:
            if character not in node.children:
                return False
            node = node.children[character]

        return True

    def words_with_prefix(self, prefix: str) -> list[str]:
        node = self.root

        for character in prefix:
            if character not in node.children:
                return []

            node = node.children[character]

        results: list[str] = []

        def collect(current: TrieNode, current_word: str) -> None:
            if current.is_word:
                results.append(current_word)

            for character in sorted(current.children):
                collect(
                    current.children[character],
                    current_word + character,
                )

        collect(node, prefix)
        return results


# ============================================================================
# 16. ADVANCED: ROLLING HASH
# ============================================================================

class RollingHash:
    """
    Polynomial rolling hash for educational substring hashing.

    Hash collisions are possible. Hash equality is therefore a candidate
    match, not mathematical proof of string equality unless the strings
    themselves are compared afterward.
    """

    def __init__(self, text: str, base: int = 911382323,
                 modulus: int = 1_000_000_007) -> None:
        if modulus <= base:
            raise ValueError("modulus should be larger than base")

        self.text = text
        self.base = base
        self.modulus = modulus
        self.prefix = [0]
        self.power = [1]

        for character in text:
            self.prefix.append(
                (self.prefix[-1] * base + ord(character)) % modulus
            )
            self.power.append(
                (self.power[-1] * base) % modulus
            )

    def substring_hash(self, left: int, right: int) -> int:
        """Return hash of text[left:right]."""
        if not (0 <= left <= right <= len(self.text)):
            raise IndexError("Invalid substring range")

        return (
            self.prefix[right]
            - self.prefix[left] * self.power[right - left]
        ) % self.modulus

    def equal_substrings(
        self,
        first_left: int,
        first_right: int,
        second_left: int,
        second_right: int,
    ) -> bool:
        """Use hashes as a fast filter, followed by exact comparison."""
        first_length = first_right - first_left
        second_length = second_right - second_left

        if first_length != second_length:
            return False

        if self.substring_hash(first_left, first_right) != self.substring_hash(
            second_left,
            second_right,
        ):
            return False

        return self.text[first_left:first_right] == self.text[
            second_left:second_right
        ]


# ============================================================================
# 17. TESTING
# ============================================================================

def run_assertions() -> None:
    """Small deterministic test suite covering normal and edge cases."""
    assert is_palindrome_simple("level")
    assert is_palindrome_two_pointer("racecar")
    assert not is_palindrome_two_pointer("python")
    assert is_valid_palindrome("A man, a plan, a canal: Panama")
    assert is_valid_palindrome("")
    assert are_anagrams_sorting("listen", "silent")
    assert are_anagrams_frequency("Triangle", "Integral")
    assert not are_anagrams_frequency("abc", "abd")
    assert first_non_repeating_character("swiss") == "w"
    assert first_non_repeating_character("aabb") is None
    assert first_repeating_character("abca") == "a"

    assert naive_pattern_search("hello world", "world") == 6
    assert naive_pattern_search("hello", "xyz") == -1
    assert kmp_search("ababcabcabababd", "ababd") == 10
    assert kmp_search("abc", "") == 0

    assert is_subsequence("ace", "abcde")
    assert not is_subsequence("aec", "abcde")
    assert count_subsequence_occurrences("babgbag", "bag") == 5

    assert longest_common_subsequence("abcde", "ace") == "ace"
    assert lcs_length_optimized("abcde", "ace") == 3

    assert longest_substring_without_repeating("abcabcbb") == "abc"
    assert longest_substring_without_repeating("") == ""
    assert minimum_window_substring("ADOBECODEBANC", "ABC") == "BANC"

    assert reverse_words("  one   two three ") == "three two one"
    assert reverse_each_word("hello world") == "olleh dlrow"
    assert rotate_string("abcdef", 2) == "cdefab"
    assert rotate_string("abcdef", -1) == "fabcde"
    assert are_rotations("waterbottle", "erbottlewat")

    assert compress_string("aaabbc") == "a3b2c1"
    assert decompress_string("a3b2c1") == "aaabbc"

    assert levenshtein_distance("kitten", "sitting") == 3
    assert one_edit_apart("pale", "ple")
    assert not one_edit_apart("pale", "bake")

    assert longest_palindromic_subsequence("bbbab") == "bbbb"
    assert word_break("leetcode", {"leet", "code"})
    assert not word_break("catsandog", {"cats", "dog", "sand", "and", "cat"})

    assert longest_common_prefix(["flower", "flow", "flight"]) == "fl"
    assert longest_common_suffix(["running", "jogging", "walking"]) == "ing"

    assert remove_duplicate_characters("programming") == "progamin"
    assert are_isomorphic("egg", "add")
    assert not are_isomorphic("foo", "bar")
    assert can_form_palindrome("carrace")
    assert not can_form_palindrome("daily")

    assert is_valid_integer_string("-123")
    assert not is_valid_integer_string("+")
    assert parse_integer_string("-42") == -42

    trie = Trie()
    for word in ["apple", "app", "apply", "banana"]:
        trie.insert(word)

    assert trie.contains("apple")
    assert trie.contains("app")
    assert not trie.contains("apples")
    assert trie.starts_with("ap")
    assert trie.words_with_prefix("app") == ["app", "apple", "apply"]

    rolling_hash = RollingHash("abracadabra")
    assert rolling_hash.equal_substrings(0, 3, 7, 10)

    print("All assertions passed.")


# ============================================================================
# 18. DEMONSTRATION
# ============================================================================

def demonstrate_problem_solving() -> None:
    print("\n=== CHARACTER FREQUENCY ===")
    sample = "banana"
    print(sample, "->", character_frequency(sample))
    print("Counter:", character_frequency_counter(sample))
    print("First non-repeating:", first_non_repeating_character(sample))
    print("First repeating:", first_repeating_character(sample))
    print("Most frequent:", most_frequent_character(sample))

    print("\n=== PALINDROMES ===")
    for value in ["racecar", "hello", "A man, a plan, a canal: Panama"]:
        print(
            repr(value),
            "simple:",
            is_palindrome_simple(value),
            "normalized:",
            is_valid_palindrome(value),
        )
    print("Longest palindromic substring:", longest_palindromic_substring(
        "forgeeksskeegfor"
    ))

    print("\n=== ANAGRAMS ===")
    print("listen / silent:", are_anagrams_frequency("listen", "silent"))
    print(
        "Conversation / Voices rant on:",
        are_anagrams_ignoring_spaces(
            "conversation",
            "voices rant on",
        ),
    )
    print(
        "Grouped:",
        group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"]),
    )

    print("\n=== SUBSTRING SEARCH ===")
    text = "ababcabcabababd"
    pattern = "ababd"
    print("Naive:", naive_pattern_search(text, pattern))
    print("KMP:", kmp_search(text, pattern))
    print("All occurrences:", find_all_occurrences("aaaa", "aa"))
    print("LPS array:", build_lps("ababaca"))

    print("\n=== SUBSEQUENCES ===")
    print("'ace' in 'abcde':", is_subsequence("ace", "abcde"))
    print(
        "Number of 'bag' subsequences:",
        count_subsequence_occurrences("babgbag", "bag"),
    )
    print("LCS:", longest_common_subsequence("AGGTAB", "GXTXAYB"))

    print("\n=== SLIDING WINDOWS ===")
    print(
        "Longest unique substring:",
        longest_substring_without_repeating("pwwkew"),
    )
    print(
        "Minimum window:",
        minimum_window_substring("ADOBECODEBANC", "ABC"),
    )
    print(
        "Replacement window length:",
        longest_repeating_replacement("AABABBA", 1),
    )

    print("\n=== TRANSFORMATIONS ===")
    print("Reverse words:", reverse_words("Python makes string problems clear"))
    print("Reverse each word:", reverse_each_word("Python string"))
    print("Rotate:", rotate_string("abcdefgh", 3))
    encoded = compress_string("aaabccccccdd")
    print("Compressed:", encoded)
    print("Decompressed:", decompress_string(encoded))

    print("\n=== EDIT DISTANCE ===")
    first = "kitten"
    second = "sitting"
    print("Distance:", levenshtein_distance(first, second))
    print("Operations:")
    for operation in edit_operations(first, second):
        print(" ", operation)

    print("\n=== ADVANCED STRUCTURES ===")
    trie = Trie()

    for word in ["car", "card", "care", "cat", "catalog"]:
        trie.insert(word)

    print("Trie prefix 'ca':", trie.words_with_prefix("ca"))

    rolling_hash = RollingHash("thequickbrownfox")
    print(
        "Hash equality:",
        rolling_hash.equal_substrings(0, 3, 0, 3),
    )


# ============================================================================
# 19. INTERACTIVE PRACTICE
# ============================================================================

def interactive_practice() -> None:
    """
    Optional command-line practice menu.

    The default main program runs demonstrations and tests. This function
    can be called manually if interactive practice is desired.
    """
    while True:
        print(
            "\nString Pattern Practice\n"
            "1. Palindrome\n"
            "2. Anagram\n"
            "3. Character frequency\n"
            "4. Subsequence\n"
            "5. Longest unique substring\n"
            "6. Edit distance\n"
            "7. Exit"
        )

        choice = input("Choose: ").strip()

        try:
            if choice == "1":
                text = input("Text: ")
                print(is_valid_palindrome(text))

            elif choice == "2":
                first = input("First string: ")
                second = input("Second string: ")
                print(are_anagrams_frequency(first, second))

            elif choice == "3":
                text = input("Text: ")
                print(dict(character_frequency_counter(text)))

            elif choice == "4":
                candidate = input("Candidate subsequence: ")
                text = input("Source text: ")
                print(is_subsequence(candidate, text))

            elif choice == "5":
                text = input("Text: ")
                print(longest_substring_without_repeating(text))

            elif choice == "6":
                first = input("First string: ")
                second = input("Second string: ")
                print(levenshtein_distance(first, second))

            elif choice == "7":
                break

            else:
                print("Invalid choice.")

        except (ValueError, TypeError) as error:
            print("Input error:", error)


# ============================================================================
# 20. MAIN
# ============================================================================

def main() -> None:
    demonstrate_string_fundamentals()
    demonstrate_problem_solving()
    run_assertions()

    print("\n=== EDGE CASES ===")
    print("Empty palindrome:", is_palindrome_two_pointer(""))
    print("Empty substring:", contains_substring("abc", ""))
    print("Empty subsequence:", is_subsequence("", "abc"))
    print("Empty LCS:", longest_common_subsequence("", "abc"))
    print("Empty edit distance:", levenshtein_distance("", "abc"))
    print("Large rotation:", rotate_string("abc", 100))
    print("Negative rotation:", rotate_string("abc", -1))
    print("No minimum window:", minimum_window_substring("abc", "xyz"))

    print("\nStudy file execution completed.")


if __name__ == "__main__":
    main()
