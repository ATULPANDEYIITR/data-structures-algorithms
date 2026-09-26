"""
STRING OPERATIONS: BEGINNER TO ADVANCED
=======================================

This standalone study script demonstrates:
- String creation and indexing
- Concatenation
- Length and traversal
- Substring extraction
- Reversing
- Character replacement
- Character deletion
- Character insertion
- Frequency counting
- Searching and comparison
- Splitting and joining
- Whitespace handling
- Validation
- Unicode considerations
- Case normalization
- Immutability
- Regular expressions
- Efficient string construction
- Advanced text-processing patterns
- Edge cases and testing
- A practical text-analysis case study

Python strings are immutable Unicode sequences. Operations that appear to
"modify" a string actually create a new string.
"""

from collections import Counter
import re
import time
from typing import Dict, List, Tuple


# ---------------------------------------------------------------------------
# 1. FUNDAMENTALS
# ---------------------------------------------------------------------------

def fundamentals() -> None:
    print("\n" + "=" * 70)
    print("1. STRING FUNDAMENTALS")
    print("=" * 70)

    text = "Python"

    print("String:", text)
    print("Type:", type(text).__name__)
    print("Length:", len(text))
    print("First character:", text[0])
    print("Last character:", text[-1])

    print("Characters:")
    for index, character in enumerate(text):
        print(f"  index={index}: {character}")

    # Strings are immutable.
    # text[0] = "J" would raise TypeError.
    modified = "J" + text[1:]
    print("Replacement through reconstruction:", modified)


# ---------------------------------------------------------------------------
# 2. CONCATENATION
# ---------------------------------------------------------------------------

def concatenation_examples() -> None:
    print("\n" + "=" * 70)
    print("2. CONCATENATION")
    print("=" * 70)

    first_name = "Atul"
    last_name = "Pandey"

    full_name = first_name + " " + last_name
    print("Using +:", full_name)

    # f-strings are generally clearer for formatted strings.
    age = 30
    description = f"{full_name} is {age} years old."
    print("Using f-string:", description)

    # join() is useful when combining many strings.
    words = ["Python", "String", "Operations"]
    sentence = " ".join(words)
    print("Using join():", sentence)

    # Repetition uses the * operator.
    print("Repetition:", "ab" * 3)

    # Common edge case: joining an empty collection.
    print("Joining empty list:", repr("".join([])))


# ---------------------------------------------------------------------------
# 3. SUBSTRING EXTRACTION
# ---------------------------------------------------------------------------

def substring_examples() -> None:
    print("\n" + "=" * 70)
    print("3. SUBSTRING EXTRACTION")
    print("=" * 70)

    text = "String Operations"

    print("Original:", text)
    print("First six characters:", text[:6])
    print("From index 7:", text[7:])
    print("Indices 0 to 5:", text[0:6])
    print("Every second character:", text[::2])
    print("Reverse using slicing:", text[::-1])
    print("Last five characters:", text[-5:])

    # Slicing outside the valid range is safe.
    print("Out-of-range slice:", text[100:200])

    # A slice with step zero is invalid.
    try:
        print(text[::0])
    except ValueError as error:
        print("Expected slicing error:", error)


# ---------------------------------------------------------------------------
# 4. REVERSING
# ---------------------------------------------------------------------------

def reverse_examples() -> None:
    print("\n" + "=" * 70)
    print("4. REVERSING")
    print("=" * 70)

    text = "algorithm"

    print("Original:", text)
    print("Slice reversal:", text[::-1])
    print("Using reversed():", "".join(reversed(text)))

    # Reversal is useful for palindrome detection.
    candidate = "level"
    normalized = candidate.casefold()
    print(
        f"Is '{candidate}' a palindrome?",
        normalized == normalized[::-1]
    )


# ---------------------------------------------------------------------------
# 5. CHARACTER REPLACEMENT
# ---------------------------------------------------------------------------

def replacement_examples() -> None:
    print("\n" + "=" * 70)
    print("5. CHARACTER REPLACEMENT")
    print("=" * 70)

    text = "banana"

    # replace() returns a new string.
    print("Original:", text)
    print("Replace a with o:", text.replace("a", "o"))
    print("Replace first two a characters:", text.replace("a", "o", 2))

    # replace() can also replace longer substrings.
    sentence = "I like Java. Java is widely used."
    print(sentence.replace("Java", "Python"))

    # Strings remain unchanged.
    print("Original remains:", sentence)


# ---------------------------------------------------------------------------
# 6. CHARACTER DELETION
# ---------------------------------------------------------------------------

def deletion_examples() -> None:
    print("\n" + "=" * 70)
    print("6. CHARACTER DELETION")
    print("=" * 70)

    text = "banana"

    # There is no direct delete-character operation because strings are
    # immutable. Reconstructing the string is the normal approach.
    without_a = text.replace("a", "")
    print("Delete all 'a':", without_a)

    # Delete one position.
    index_to_delete = 2
    result = text[:index_to_delete] + text[index_to_delete + 1:]
    print("Delete index 2:", result)

    # Delete every digit.
    mixed = "abc123xyz456"
    letters_only = "".join(character for character in mixed if not character.isdigit())
    print("Letters only:", letters_only)

    # Delete whitespace.
    spaced = " a b c "
    print("Whitespace removed:", spaced.replace(" ", ""))


# ---------------------------------------------------------------------------
# 7. CHARACTER INSERTION
# ---------------------------------------------------------------------------

def insertion_examples() -> None:
    print("\n" + "=" * 70)
    print("7. CHARACTER INSERTION")
    print("=" * 70)

    text = "Pythn"
    position = 4

    # Insert by joining the prefix and suffix around the insertion point.
    corrected = text[:position] + "o" + text[position:]
    print("Inserted character:", corrected)

    # Insert a substring.
    base = "HelloWorld"
    inserted = base[:5] + " " + base[5:]
    print("Inserted substring:", inserted)

    # Edge cases: inserting at the beginning and end.
    print("Beginning:", "X" + base)
    print("End:", base + "X")


# ---------------------------------------------------------------------------
# 8. FREQUENCY COUNTING
# ---------------------------------------------------------------------------

def frequency_examples() -> None:
    print("\n" + "=" * 70)
    print("8. FREQUENCY COUNTING")
    print("=" * 70)

    text = "banana"

    print("Count of 'a':", text.count("a"))
    print("Count of 'na':", text.count("na"))

    frequency = Counter(text)
    print("Character frequencies:", dict(frequency))

    # Manual counting demonstrates the underlying algorithm.
    manual: Dict[str, int] = {}
    for character in text:
        manual[character] = manual.get(character, 0) + 1

    print("Manual frequency table:", manual)

    # Word frequency is a different problem from character frequency.
    sentence = "python is useful and python is readable"
    word_frequency = Counter(sentence.split())
    print("Word frequencies:", dict(word_frequency))


# ---------------------------------------------------------------------------
# 9. SEARCHING
# ---------------------------------------------------------------------------

def searching_examples() -> None:
    print("\n" + "=" * 70)
    print("9. SEARCHING")
    print("=" * 70)

    text = "String operations are useful."

    print("'operations' in text:", "operations" in text)
    print("Position of 'operations':", text.find("operations"))
    print("Position of missing word:", text.find("database"))

    try:
        print("Index:", text.index("database"))
    except ValueError as error:
        print("index() failure:", error)

    print("Starts with 'String':", text.startswith("String"))
    print("Ends with '.':", text.endswith("."))


# ---------------------------------------------------------------------------
# 10. CASE AND WHITESPACE NORMALIZATION
# ---------------------------------------------------------------------------

def normalization_examples() -> None:
    print("\n" + "=" * 70)
    print("10. NORMALIZATION")
    print("=" * 70)

    text = "   Python STRING Operations   "

    print("Original:", repr(text))
    print("strip():", repr(text.strip()))
    print("lower():", text.lower())
    print("upper():", text.upper())
    print("title():", text.title())

    # casefold() is intended for caseless matching and is more aggressive
    # than lower() for certain Unicode characters.
    print("casefold():", text.casefold())

    user_input = "  YES  "
    normalized = user_input.strip().casefold()
    print("Normalized input:", normalized)
    print("Accepted:", normalized in {"yes", "y"})


# ---------------------------------------------------------------------------
# 11. SPLITTING AND JOINING
# ---------------------------------------------------------------------------

def split_join_examples() -> None:
    print("\n" + "=" * 70)
    print("11. SPLITTING AND JOINING")
    print("=" * 70)

    csv_line = "Python,JavaScript,C++"
    languages = csv_line.split(",")
    print("Split:", languages)

    reconstructed = " | ".join(languages)
    print("Joined:", reconstructed)

    sentence = "Python   handles   strings"
    print("Default split:", sentence.split())

    # splitlines() handles different line-ending conventions.
    multiline = "one\ntwo\r\nthree"
    print("Lines:", multiline.splitlines())


# ---------------------------------------------------------------------------
# 12. TRANSLATION TABLES
# ---------------------------------------------------------------------------

def translation_examples() -> None:
    print("\n" + "=" * 70)
    print("12. CHARACTER TRANSLATION")
    print("=" * 70)

    text = "hello world"

    # str.maketrans() creates a translation table.
    table = str.maketrans({"a": "@", "e": "3", "o": "0"})
    transformed = text.translate(table)

    print("Original:", text)
    print("Translated:", transformed)

    # Characters can also be deleted through translate().
    delete_vowels = str.maketrans("", "", "aeiou")
    print("Delete vowels:", text.translate(delete_vowels))


# ---------------------------------------------------------------------------
# 13. UNICODE AND CHARACTER CATEGORIES
# ---------------------------------------------------------------------------

def unicode_examples() -> None:
    print("\n" + "=" * 70)
    print("13. UNICODE")
    print("=" * 70)

    examples = ["A", "é", "中", "🙂"]

    for character in examples:
        print(
            repr(character),
            "length=",
            len(character),
            "code point=",
            hex(ord(character))
        )

    # Python strings represent Unicode text. This is important when processing
    # multilingual input.
    multilingual = "नमस्ते 世界"
    print("Multilingual string:", multilingual)
    print("Character count:", len(multilingual))


# ---------------------------------------------------------------------------
# 14. REGULAR EXPRESSIONS
# ---------------------------------------------------------------------------

def regex_examples() -> None:
    print("\n" + "=" * 70)
    print("14. REGULAR EXPRESSIONS")
    print("=" * 70)

    text = "Contact: alice@example.com or bob@example.org"

    emails = re.findall(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        text
    )

    print("Emails:", emails)

    # Replace runs of whitespace with a single space.
    messy = "Python\tstrings   are\npowerful"
    clean = re.sub(r"\s+", " ", messy).strip()
    print("Normalized whitespace:", clean)


# ---------------------------------------------------------------------------
# 15. VALIDATION
# ---------------------------------------------------------------------------

def validate_identifier(identifier: str) -> Tuple[bool, str]:
    """
    Validate a simple programming-style identifier.

    Rules:
    - Must not be empty.
    - First character must be alphabetic or underscore.
    - Remaining characters must be alphanumeric or underscore.
    """
    if not identifier:
        return False, "Identifier cannot be empty."

    if not (identifier[0].isalpha() or identifier[0] == "_"):
        return False, "Identifier must start with a letter or underscore."

    if not all(character.isalnum() or character == "_" for character in identifier):
        return False, "Identifier contains an invalid character."

    return True, "Valid identifier."


def validation_examples() -> None:
    print("\n" + "=" * 70)
    print("15. VALIDATION")
    print("=" * 70)

    candidates = [
        "total_count",
        "_private",
        "2ndValue",
        "user-name",
        "",
        "café",
    ]

    for candidate in candidates:
        valid, message = validate_identifier(candidate)
        print(f"{candidate!r}: {valid} - {message}")


# ---------------------------------------------------------------------------
# 16. IMMUTABILITY
# ---------------------------------------------------------------------------

def immutability_examples() -> None:
    print("\n" + "=" * 70)
    print("16. STRING IMMUTABILITY")
    print("=" * 70)

    original = "cat"

    # This does not modify original.
    changed = original.replace("c", "b")

    print("Original:", original)
    print("New string:", changed)

    try:
        original[0] = "b"
    except TypeError as error:
        print("Expected error:", error)


# ---------------------------------------------------------------------------
# 17. EFFICIENT STRING CONSTRUCTION
# ---------------------------------------------------------------------------

def performance_examples() -> None:
    print("\n" + "=" * 70)
    print("17. STRING CONSTRUCTION AND PERFORMANCE")
    print("=" * 70)

    values = [str(number) for number in range(10)]

    # join() expresses the intent clearly and avoids repeatedly creating
    # intermediate strings in a loop.
    efficient = ",".join(values)
    print("Efficient construction:", efficient)

    # For large text processing, collecting pieces and joining once is often
    # preferable to repeated concatenation.
    pieces = []
    for number in range(1000):
        pieces.append(f"record-{number}")

    result = "\n".join(pieces)
    print("Generated characters:", len(result))


# ---------------------------------------------------------------------------
# 18. PRACTICAL TEXT ANALYZER
# ---------------------------------------------------------------------------

class TextAnalyzer:
    """Reusable text-analysis component."""

    def __init__(self, text: str) -> None:
        self.text = text

    def character_frequency(self, ignore_spaces: bool = False) -> Dict[str, int]:
        data = self.text
        if ignore_spaces:
            data = "".join(character for character in data if not character.isspace())
        return dict(Counter(data))

    def word_frequency(self) -> Dict[str, int]:
        words = re.findall(r"\b[\w']+\b", self.text.casefold())
        return dict(Counter(words))

    def reverse(self) -> str:
        return self.text[::-1]

    def palindrome(self) -> bool:
        normalized = "".join(
            character.casefold()
            for character in self.text
            if character.isalnum()
        )
        return normalized == normalized[::-1]

    def replace_word(self, old: str, new: str) -> str:
        return self.text.replace(old, new)

    def insert(self, position: int, value: str) -> str:
        if not 0 <= position <= len(self.text):
            raise IndexError("Insertion position is outside the valid range.")
        return self.text[:position] + value + self.text[position:]

    def delete_range(self, start: int, end: int) -> str:
        if start < 0 or end < start or end > len(self.text):
            raise ValueError("Invalid deletion range.")
        return self.text[:start] + self.text[end:]


def analyzer_demo() -> None:
    print("\n" + "=" * 70)
    print("18. TEXT ANALYZER")
    print("=" * 70)

    text = "Python strings are immutable. Python strings are sequences."
    analyzer = TextAnalyzer(text)

    print("Character frequency:", analyzer.character_frequency(True))
    print("Word frequency:", analyzer.word_frequency())
    print("Reversed:", analyzer.reverse())
    print("Palindrome:", analyzer.palindrome())
    print("Replacement:", analyzer.replace_word("Python", "Programming"))
    print("Insertion:", analyzer.insert(0, "[TEXT] "))

    try:
        print("Deletion:", analyzer.delete_range(0, 7))
    except ValueError as error:
        print("Deletion error:", error)


# ---------------------------------------------------------------------------
# 19. PALINDROME AND FREQUENCY ALGORITHMS
# ---------------------------------------------------------------------------

def normalized_text(text: str) -> str:
    """Keep alphanumeric characters and normalize case."""
    return "".join(character.casefold() for character in text if character.isalnum())


def is_palindrome(text: str) -> bool:
    normalized = normalized_text(text)
    return normalized == normalized[::-1]


def first_non_repeating_character(text: str) -> str | None:
    frequency = Counter(text)

    for character in text:
        if frequency[character] == 1:
            return character

    return None


def algorithm_examples() -> None:
    print("\n" + "=" * 70)
    print("19. STRING ALGORITHMS")
    print("=" * 70)

    examples = [
        "level",
        "A man, a plan, a canal: Panama",
        "Python",
    ]

    for example in examples:
        print(
            repr(example),
            "palindrome=",
            is_palindrome(example)
        )

    for example in ["swiss", "aabbcc", ""]:
        print(
            repr(example),
            "first non-repeating=",
            first_non_repeating_character(example)
        )


# ---------------------------------------------------------------------------
# 20. EDGE CASES
# ---------------------------------------------------------------------------

def edge_case_examples() -> None:
    print("\n" + "=" * 70)
    print("20. EDGE CASES")
    print("=" * 70)

    cases = [
        "",
        " ",
        "A",
        "AAAA",
        "12345",
        "😀😀😀",
        "a\nb\nc",
    ]

    for value in cases:
        print(
            repr(value),
            "length=",
            len(value),
            "reversed=",
            repr(value[::-1]),
            "a_count=",
            value.count("a")
        )

    # Searching for an empty string has defined behavior.
    print("Empty substring in 'abc':", "" in "abc")
    print("Find empty substring:", "abc".find(""))


# ---------------------------------------------------------------------------
# 21. TESTING
# ---------------------------------------------------------------------------

def run_tests() -> None:
    print("\n" + "=" * 70)
    print("21. SELF-TESTS")
    print("=" * 70)

    assert "Hello" + " " + "World" == "Hello World"
    assert "abcdef"[1:4] == "bcd"
    assert "abcdef"[::-1] == "fedcba"
    assert "banana".replace("a", "o") == "bonono"
    assert "banana".replace("a", "") == "bnn"
    assert "Pythn"[:4] + "o" + "Pythn"[4:] == "Python"
    assert Counter("banana")["a"] == 3
    assert is_palindrome("Race car!")
    assert first_non_repeating_character("swiss") == "w"

    valid, _ = validate_identifier("user_123")
    assert valid

    invalid, _ = validate_identifier("123user")
    assert not invalid

    print("All tests passed.")


# ---------------------------------------------------------------------------
# 22. PRACTICAL CASE STUDY: LOG RECORD PROCESSING
# ---------------------------------------------------------------------------

def process_log_records(records: List[str]) -> Dict[str, object]:
    """
    Process simple log records.

    Expected format:
        LEVEL|user|message

    Example:
        INFO|alice|Login successful

    The function demonstrates:
    - splitting
    - trimming
    - validation
    - replacement
    - frequency counting
    - aggregation
    """
    level_frequency: Counter[str] = Counter()
    user_frequency: Counter[str] = Counter()
    messages: List[str] = []
    invalid_records: List[str] = []

    for record in records:
        parts = record.split("|", 2)

        if len(parts) != 3:
            invalid_records.append(record)
            continue

        level, user, message = (part.strip() for part in parts)

        if not level or not user or not message:
            invalid_records.append(record)
            continue

        level = level.upper()
        message = re.sub(r"\s+", " ", message)

        level_frequency[level] += 1
        user_frequency[user] += 1
        messages.append(message)

    return {
        "levels": dict(level_frequency),
        "users": dict(user_frequency),
        "messages": messages,
        "invalid": invalid_records,
    }


def case_study_demo() -> None:
    print("\n" + "=" * 70)
    print("22. LOG PROCESSING CASE STUDY")
    print("=" * 70)

    records = [
        "INFO|alice|Login successful",
        "ERROR|bob|Invalid password",
        "INFO|alice|Viewed dashboard",
        "WARNING|charlie|Password expires soon",
        "ERROR|bob|Account temporarily locked",
        "INVALID RECORD",
    ]

    result = process_log_records(records)

    print("Level frequency:", result["levels"])
    print("User frequency:", result["users"])
    print("Messages:", result["messages"])
    print("Invalid records:", result["invalid"])


# ---------------------------------------------------------------------------
# 23. COMMON MISTAKES
# ---------------------------------------------------------------------------

def common_mistakes() -> None:
    print("\n" + "=" * 70)
    print("23. COMMON MISTAKES")
    print("=" * 70)

    # Mistake 1: confusing find() with index().
    missing = "python".find("z")
    print("find() returns:", missing)

    # Mistake 2: forgetting that methods return new strings.
    text = "hello"
    text.upper()
    print("Calling upper() without assignment:", text)

    text = text.upper()
    print("After assignment:", text)

    # Mistake 3: using split("").
    try:
        "abc".split("")
    except ValueError as error:
        print("Empty separator error:", error)

    # Mistake 4: assuming character count always equals byte count.
    unicode_text = "café"
    print(
        "Unicode characters:",
        len(unicode_text),
        "UTF-8 bytes:",
        len(unicode_text.encode("utf-8"))
    )


# ---------------------------------------------------------------------------
# 24. MAIN PROGRAM
# ---------------------------------------------------------------------------

def main() -> None:
    fundamentals()
    concatenation_examples()
    substring_examples()
    reverse_examples()
    replacement_examples()
    deletion_examples()
    insertion_examples()
    frequency_examples()
    searching_examples()
    normalization_examples()
    split_join_examples()
    translation_examples()
    unicode_examples()
    regex_examples()
    validation_examples()
    immutability_examples()
    performance_examples()
    analyzer_demo()
    algorithm_examples()
    edge_case_examples()
    run_tests()
    case_study_demo()
    common_mistakes()

    print("\n" + "=" * 70)
    print("STRING OPERATIONS STUDY PROGRAM COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
