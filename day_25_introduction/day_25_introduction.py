"""
Strings Introduction: representation, characters, ASCII, Unicode, traversal,
comparison, manipulation, validation, encoding, normalization, performance,
security, and practical applications.

This file is designed as a standalone executable study program.
It progresses from basic string concepts to advanced Unicode and text-processing
techniques available in Python's standard library.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
import sys
import time
import unicodedata
from collections import Counter


# ============================================================================
# 1. FUNDAMENTALS
# ============================================================================

def section(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def subsection(title: str) -> None:
    print("\n" + "-" * 78)
    print(title)
    print("-" * 78)


def demonstrate_string_creation() -> None:
    subsection("1.1 Creating strings")

    single_quoted = 'Hello'
    double_quoted = "World"
    apostrophe_example = "Python's string"
    multiline = """This is
a multiline
string."""

    print(single_quoted)
    print(double_quoted)
    print(apostrophe_example)
    print(multiline)

    # A string containing quotes can use a different outer quote style.
    quoted_text = 'She said, "Hello."'
    print(quoted_text)

    # Escape sequences represent special characters.
    escaped = "Line 1\nLine 2\tIndented"
    print(escaped)

    # Raw strings prevent most backslash escape processing.
    raw_path = r"C:\Users\student\Documents"
    print(raw_path)


def demonstrate_string_properties() -> None:
    subsection("1.2 Strings as immutable sequences")

    text = "Python"

    print("Value:", text)
    print("Type:", type(text).__name__)
    print("Length:", len(text))
    print("First character:", text[0])
    print("Last character:", text[-1])

    # Python strings are immutable. This would raise TypeError:
    # text[0] = "J"

    # A new string must be created instead.
    changed = "J" + text[1:]
    print("New string:", changed)

    print("Object size:", sys.getsizeof(text), "bytes")


# ============================================================================
# 2. CHARACTERS, ORDINAL VALUES, AND ASCII
# ============================================================================

def demonstrate_characters_and_ordinals() -> None:
    subsection("2.1 Characters and Unicode code points")

    characters = ["A", "a", "0", " ", "€", "中", "😀"]

    for character in characters:
        print(
            repr(character),
            "code point:",
            ord(character),
            "hex:",
            hex(ord(character)),
        )

    # chr() performs the inverse operation of ord() for valid code points.
    for number in [65, 97, 48, 8364, 20013, 128512]:
        print(number, "->", chr(number))


def demonstrate_ascii() -> None:
    subsection("2.2 ASCII")

    print("ASCII represents 128 code points numbered 0 through 127.")

    for character in "AZaz09":
        print(character, "=", ord(character))

    # ASCII-specific validation.
    samples = ["Hello", "Hello123", "café", "भारत"]

    for value in samples:
        print(repr(value), "is ASCII:", value.isascii())

    # Encoding to ASCII fails for characters that are not representable.
    try:
        print("café".encode("ascii"))
    except UnicodeEncodeError as error:
        print("Expected ASCII encoding error:", error)


# ============================================================================
# 3. UNICODE
# ============================================================================

def demonstrate_unicode() -> None:
    subsection("3.1 Unicode concepts")

    examples = [
        "A",
        "é",
        "€",
        "भारत",
        "東京",
        "مرحبا",
        "😀",
        "🧑‍💻",
    ]

    for value in examples:
        print(
            f"{value!r}: characters={len(value)}, "
            f"code points={[f'U+{ord(c):04X}' for c in value]}"
        )

    # A Python str is Unicode text. It is not the same thing as a byte array.
    text = "café"
    encoded = text.encode("utf-8")

    print("Text:", text)
    print("UTF-8 bytes:", encoded)
    print("Decoded text:", encoded.decode("utf-8"))


def demonstrate_utf8() -> None:
    subsection("3.2 UTF-8 encoding")

    examples = ["A", "é", "€", "中", "😀"]

    for value in examples:
        encoded = value.encode("utf-8")
        print(
            repr(value),
            "code point(s):",
            [f"U+{ord(c):04X}" for c in value],
            "UTF-8:",
            encoded,
            "byte length:",
            len(encoded),
        )

    # Decoding with the wrong character encoding can produce an error or
    # corrupted text depending on the bytes and chosen decoder.
    utf8_data = "café".encode("utf-8")

    try:
        print(utf8_data.decode("ascii"))
    except UnicodeDecodeError as error:
        print("Expected decoding error:", error)

    print("Correct decoding:", utf8_data.decode("utf-8"))


# ============================================================================
# 4. INDEXING AND TRAVERSAL
# ============================================================================

def demonstrate_indexing_and_slicing() -> None:
    subsection("4.1 Indexing and slicing")

    text = "Programming"

    print("text[0]:", text[0])
    print("text[-1]:", text[-1])
    print("text[0:4]:", text[0:4])
    print("text[4:]:", text[4:])
    print("text[:4]:", text[:4])
    print("text[::2]:", text[::2])
    print("text[::-1]:", text[::-1])

    # Out-of-range slicing is safe and simply returns available content.
    print("text[100:]:", repr(text[100:]))

    try:
        print(text[100])
    except IndexError as error:
        print("Expected indexing error:", error)


def demonstrate_traversal() -> None:
    subsection("4.2 Traversing strings")

    text = "Python"

    print("Direct traversal:")
    for character in text:
        print(character)

    print("\nIndexed traversal:")
    for index, character in enumerate(text):
        print(index, character)

    print("\nReverse traversal:")
    for character in reversed(text):
        print(character)


# ============================================================================
# 5. COMPARISON
# ============================================================================

def demonstrate_comparison() -> None:
    subsection("5.1 String comparison")

    values = ["apple", "banana", "apple", "Apple"]

    print("apple == apple:", values[0] == values[2])
    print("apple != banana:", values[0] != values[1])
    print("apple < banana:", values[0] < values[1])
    print("Apple < apple:", values[3] < values[0])

    # Python's ordinary string ordering compares Unicode code points.
    print("ord('A'):", ord("A"))
    print("ord('a'):", ord("a"))

    # Case-insensitive comparison should normally use casefold() rather than
    # relying only on lower(), especially for international text.
    pairs = [("Python", "python"), ("Straße", "STRASSE"), ("CAFÉ", "café")]

    for left, right in pairs:
        print(
            repr(left),
            repr(right),
            "casefold equal:",
            left.casefold() == right.casefold(),
        )


# ============================================================================
# 6. SEARCHING
# ============================================================================

def demonstrate_searching() -> None:
    subsection("6.1 Searching strings")

    text = "Python is powerful and Python is readable."

    print("'Python' in text:", "Python" in text)
    print("find:", text.find("Python"))
    print("rfind:", text.rfind("Python"))
    print("count:", text.count("Python"))
    print("startswith:", text.startswith("Python"))
    print("endswith:", text.endswith("readable."))

    missing = text.find("Java")
    print("Missing substring index:", missing)

    # index() differs from find(): it raises ValueError when absent.
    try:
        text.index("Java")
    except ValueError as error:
        print("Expected index() error:", error)


# ============================================================================
# 7. MANIPULATION
# ============================================================================

def demonstrate_manipulation() -> None:
    subsection("7.1 Common string manipulation")

    text = "  Python Programming  "

    print("strip:", repr(text.strip()))
    print("lstrip:", repr(text.lstrip()))
    print("rstrip:", repr(text.rstrip()))
    print("upper:", text.upper())
    print("lower:", text.lower())
    print("title:", text.title())
    print("swapcase:", text.swapcase())

    print("replace:", text.replace("Python", "Advanced Python"))

    words = "Python,Java,C++".split(",")
    print("split:", words)
    print("join:", " | ".join(words))

    # Partition is useful when exactly one separator matters.
    header, separator, body = "Content-Type: text/plain".partition(":")
    print("partition:", header, separator, body)


def demonstrate_formatting() -> None:
    subsection("7.2 Formatting strings")

    name = "Atul"
    score = 97.4567

    print("Concatenation:", "Name: " + name)
    print("format():", "Name: {}, Score: {:.2f}".format(name, score))
    print(f"f-string: Name: {name}, Score: {score:.2f}")

    # f-strings can contain expressions, but complex business logic should
    # remain in named variables or functions for readability.
    average = (90 + 95 + 98) / 3
    print(f"Average: {average:.2f}")


# ============================================================================
# 8. VALIDATION
# ============================================================================

def demonstrate_validation() -> None:
    subsection("8.1 Character and string validation")

    samples = [
        "12345",
        "abc",
        "abc123",
        " ",
        "Python",
        "é",
        "भारत",
    ]

    for value in samples:
        print(
            repr(value),
            "alpha=", value.isalpha(),
            "digit=", value.isdigit(),
            "alnum=", value.isalnum(),
            "space=", value.isspace(),
            "lower=", value.islower(),
            "upper=", value.isupper(),
            "ascii=", value.isascii(),
        )


def validate_username(username: str) -> tuple[bool, str]:
    """Validate a conservative ASCII username policy."""

    if not username:
        return False, "Username cannot be empty."

    if not 3 <= len(username) <= 20:
        return False, "Username must contain 3 to 20 characters."

    if not username.isascii():
        return False, "Username must contain only ASCII characters."

    if not (username[0].isalpha() or username[0] == "_"):
        return False, "Username must start with a letter or underscore."

    if not all(character.isalnum() or character == "_" for character in username):
        return False, "Username may contain letters, digits, and underscores."

    return True, "Valid username."


def demonstrate_validation_function() -> None:
    subsection("8.2 Reusable validation")

    for username in ["atul_01", "", "ab", "1atul", "atul-pandey", "भारत"]:
        valid, message = validate_username(username)
        print(f"{username!r}: {valid} - {message}")


# ============================================================================
# 9. REGULAR EXPRESSIONS
# ============================================================================

def demonstrate_regular_expressions() -> None:
    subsection("9.1 Pattern-based string processing")

    text = "Contact: alice@example.com or bob@example.org"

    email_pattern = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
    emails = email_pattern.findall(text)

    print("Emails:", emails)

    redacted = email_pattern.sub("[EMAIL]", text)
    print("Redacted:", redacted)

    # Anchors describe positions rather than characters.
    identifier_pattern = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

    for candidate in ["name_1", "1name", "name-value", ""]:
        print(candidate, bool(identifier_pattern.fullmatch(candidate)))


# ============================================================================
# 10. IMMUTABILITY AND BUILDING STRINGS
# ============================================================================

def demonstrate_immutability_and_building() -> None:
    subsection("10.1 Efficient string construction")

    pieces = ["Python", "is", "fast", "to", "prototype"]

    # Repeated concatenation creates new string objects. For many pieces,
    # join() clearly communicates the intended operation.
    joined = " ".join(pieces)
    print(joined)

    # Building a list and joining once is a common pattern.
    output_parts = []
    for number in range(1, 6):
        output_parts.append(f"Item {number}")

    print("\n".join(output_parts))


# ============================================================================
# 11. CHARACTER FREQUENCY AND ALGORITHMIC EXAMPLES
# ============================================================================

def character_frequency(text: str) -> Counter[str]:
    """Return frequency of every Unicode code point in text."""
    return Counter(text)


def first_non_repeating_character(text: str) -> str | None:
    """Return the first character whose frequency is exactly one."""
    counts = Counter(text)

    for character in text:
        if counts[character] == 1:
            return character

    return None


def is_palindrome(text: str, *, ignore_case: bool = True) -> bool:
    """Check whether text reads identically in both directions."""
    normalized = text.casefold() if ignore_case else text
    return normalized == normalized[::-1]


def reverse_words(sentence: str) -> str:
    """Reverse word order while treating repeated whitespace naturally."""
    words = sentence.split()
    return " ".join(reversed(words))


def demonstrate_algorithms() -> None:
    subsection("11.1 String algorithms")

    text = "banana"
    print("Frequency:", dict(character_frequency(text)))

    for sample in ["swiss", "aabbcc", "Python", ""]:
        print(
            repr(sample),
            "first non-repeating:",
            first_non_repeating_character(sample),
        )

    for sample in ["level", "RaceCar", "Python", "Never odd or even"]:
        print(
            repr(sample),
            "simple palindrome:",
            is_palindrome(sample),
        )

    print(reverse_words("Python makes text processing practical"))


# ============================================================================
# 12. NORMALIZATION
# ============================================================================

def demonstrate_unicode_normalization() -> None:
    subsection("12.1 Unicode normalization")

    # These two strings can look identical while containing different
    # sequences of code points.
    composed = "é"
    decomposed = "e\u0301"

    print("Composed:", repr(composed), [f"U+{ord(c):04X}" for c in composed])
    print(
        "Decomposed:",
        repr(decomposed),
        [f"U+{ord(c):04X}" for c in decomposed],
    )

    print("Direct equality:", composed == decomposed)

    normalized_composed = unicodedata.normalize("NFC", composed)
    normalized_decomposed = unicodedata.normalize("NFC", decomposed)

    print(
        "NFC equality:",
        normalized_composed == normalized_decomposed,
    )

    print("NFD composed:", repr(unicodedata.normalize("NFD", composed)))
    print("Unicode name:", unicodedata.name("é"))


# ============================================================================
# 13. CODE POINTS VS GRAPHEME-LIKE USER-PERCEIVED CHARACTERS
# ============================================================================

def demonstrate_unicode_subtleties() -> None:
    subsection("13.1 Code points are not always user-perceived characters")

    examples = [
        "é",
        "e\u0301",
        "👍",
        "👍🏽",
        "🇮🇳",
        "👨‍👩‍👧‍👦",
    ]

    for value in examples:
        print(
            repr(value),
            "Python len=",
            len(value),
            "code points=",
            [f"U+{ord(c):04X}" for c in value],
        )

    print(
        "\nImportant: Python's len(str) counts Unicode code points, "
        "not necessarily what a user perceives as one visual character."
    )


# ============================================================================
# 14. SECURITY CONSIDERATIONS
# ============================================================================

def demonstrate_security_considerations() -> None:
    subsection("14.1 Security-related string concerns")

    # Homoglyph/confusable characters can resemble ordinary identifiers.
    latin_a = "a"
    cyrillic_a = "а"  # Cyrillic small letter a.

    print("Latin a:", repr(latin_a), ord(latin_a))
    print("Cyrillic a:", repr(cyrillic_a), ord(cyrillic_a))
    print("Visually similar but equal:", latin_a == cyrillic_a)

    # Control characters can alter terminal/log presentation.
    malicious_log_value = "alice\nADMIN=true"
    print("repr-safe logging:", repr(malicious_log_value))

    # Never build SQL commands by string concatenation from untrusted input.
    # Parameterized queries should be used with database APIs.
    user_input = "' OR 1=1 --"
    unsafe_example = "SELECT * FROM users WHERE name = '" + user_input + "'"
    print("Illustrative unsafe SQL:", unsafe_example)
    print("Use parameterized database queries in real applications.")

    # URL/HTML/JSON contexts each require their own correct escaping strategy.
    # There is no universal "escape string" operation that is safe everywhere.


# ============================================================================
# 15. PARSING A SIMPLE LOG
# ============================================================================

@dataclass
class LogRecord:
    timestamp: str
    level: str
    message: str


LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\S+)\s+"
    r"(?P<level>[A-Z]+)\s+"
    r"(?P<message>.*)$"
)


def parse_log_line(line: str) -> LogRecord | None:
    match = LOG_PATTERN.fullmatch(line.strip())

    if not match:
        return None

    return LogRecord(
        timestamp=match.group("timestamp"),
        level=match.group("level"),
        message=match.group("message"),
    )


def demonstrate_log_parser() -> None:
    subsection("15.1 Practical text parser")

    lines = [
        "2026-09-25T10:00:00 INFO Server started",
        "2026-09-25T10:01:05 WARNING Cache is nearly full",
        "invalid log line",
        "2026-09-25T10:02:10 ERROR Database connection failed",
    ]

    for line in lines:
        record = parse_log_line(line)

        if record is None:
            print("Could not parse:", repr(line))
        else:
            print(record)


# ============================================================================
# 16. TEXT TOKENIZATION
# ============================================================================

def tokenize_text(text: str) -> list[str]:
    """
    Simple educational tokenizer.

    This intentionally does not attempt to solve all natural-language
    tokenization problems. Punctuation, contractions, scripts, emoji, and
    language-specific segmentation can require specialized algorithms.
    """
    return re.findall(r"\b[\w']+\b", text, flags=re.UNICODE)


def demonstrate_tokenization() -> None:
    subsection("16.1 Tokenization")

    text = "Python's strings are useful: fast, flexible, and readable."
    tokens = tokenize_text(text)

    print("Tokens:", tokens)
    print("Token count:", len(tokens))


# ============================================================================
# 17. SORTING AND CASE-INSENSITIVE ORDERING
# ============================================================================

def demonstrate_sorting() -> None:
    subsection("17.1 Sorting strings")

    names = ["alice", "Bob", "charlie", "ALAN"]

    print("Code-point ordering:", sorted(names))
    print("Case-insensitive ordering:", sorted(names, key=str.casefold))

    # Sorting strings by length uses a key function rather than modifying
    # the original values.
    print("Length ordering:", sorted(names, key=len))


# ============================================================================
# 18. PERFORMANCE
# ============================================================================

def demonstrate_performance() -> None:
    subsection("18.1 Basic performance considerations")

    pieces = [str(number) for number in range(5000)]

    start = time.perf_counter()
    result = "".join(pieces)
    join_duration = time.perf_counter() - start

    start = time.perf_counter()
    result_loop = ""
    for piece in pieces:
        result_loop += piece
    concat_duration = time.perf_counter() - start

    print("join result length:", len(result))
    print("loop concatenation length:", len(result_loop))
    print(f"join time: {join_duration:.6f}s")
    print(f"repeated concatenation time: {concat_duration:.6f}s")
    print(
        "Timing varies by machine and runtime. "
        "For many fragments, join() is the conventional approach."
    )


# ============================================================================
# 19. BYTES VS STR
# ============================================================================

def demonstrate_text_and_bytes() -> None:
    subsection("19.1 str versus bytes")

    text = "Hello, 世界"
    data = text.encode("utf-8")

    print("str:", text)
    print("bytes:", data)
    print("str length:", len(text))
    print("byte length:", len(data))

    # bytes is a sequence of integers in the range 0..255.
    print("First UTF-8 byte:", data[0])
    print("Decoded:", data.decode("utf-8"))

    # Invalid byte sequences should be handled deliberately.
    invalid = b"\xff\xfe"

    try:
        invalid.decode("utf-8")
    except UnicodeDecodeError as error:
        print("Expected invalid UTF-8 error:", error)

    # Explicit replacement can preserve processing while marking invalid
    # sequences. It is not equivalent to recovering the original text.
    print("Replacement decoding:", invalid.decode("utf-8", errors="replace"))


# ============================================================================
# 20. ADVANCED STRING FEATURES
# ============================================================================

def demonstrate_advanced_features() -> None:
    subsection("20.1 Advanced standard-library operations")

    text = "one,two,three"

    print("partition:", text.partition(","))
    print("rpartition:", text.rpartition(","))
    print("split:", text.split(","))
    print("rsplit:", text.rsplit(",", 1))

    # translate() can perform many character substitutions efficiently.
    translation_table = str.maketrans({
        "a": "@",
        "e": "3",
        "i": "1",
        "o": "0",
    })

    print("translate:", "education".translate(translation_table))

    # Removing characters can be expressed with a translation table.
    punctuation_table = str.maketrans("", "", ".,!?")
    print("Removed punctuation:", "Hello, world!".translate(punctuation_table))


# ============================================================================
# 21. PRACTICAL PASSWORD-INPUT DEMONSTRATION
# ============================================================================

def password_policy(password: str) -> list[str]:
    """
    Return policy findings.

    This is a policy demonstration, not a complete password-security system.
    Real authentication systems should use a dedicated password hashing
    algorithm and should not store plaintext passwords.
    """
    findings: list[str] = []

    if len(password) < 12:
        findings.append("Use at least 12 characters.")

    if password.casefold() == password:
        findings.append("Contains no uppercase distinction.")

    if password.lower() == password:
        findings.append("Contains no uppercase letters.")

    if not any(character.isdigit() for character in password):
        findings.append("Contains no digits.")

    if not any(not character.isalnum() for character in password):
        findings.append("Contains no non-alphanumeric characters.")

    return findings


def demonstrate_password_policy() -> None:
    subsection("21.1 String-based password policy checks")

    samples = [
        "password",
        "Password123",
        "A-stronger-example-2026!",
    ]

    for password in samples:
        findings = password_policy(password)
        print(repr(password), "=>", findings or ["Policy checks passed."])


# ============================================================================
# 22. EDGE CASES
# ============================================================================

def demonstrate_edge_cases() -> None:
    subsection("22.1 Important edge cases")

    cases = [
        "",
        " ",
        "\n",
        "é",
        "e\u0301",
        "😀",
        "👍🏽",
        "   Python   ",
        "Python\nJava\nC++",
    ]

    for value in cases:
        print(
            "value=",
            repr(value),
            "length=",
            len(value),
            "stripped=",
            repr(value.strip()),
        )

    # split() without an argument treats runs of whitespace as separators.
    print("Whitespace split:", "  one\t two\nthree ".split())

    # split(" ") treats a literal space differently.
    print("Literal-space split:", "  one  two ".split(" "))


# ============================================================================
# 23. MINI TEXT ANALYZER
# ============================================================================

@dataclass
class TextStatistics:
    characters: int
    code_points: int
    words: int
    lines: int
    digits: int
    whitespace: int
    alphabetic: int


def analyze_text(text: str) -> TextStatistics:
    return TextStatistics(
        characters=len(text),
        code_points=len(text),
        words=len(text.split()),
        lines=text.count("\n") + 1 if text else 0,
        digits=sum(character.isdigit() for character in text),
        whitespace=sum(character.isspace() for character in text),
        alphabetic=sum(character.isalpha() for character in text),
    )


def demonstrate_text_analyzer() -> None:
    subsection("23.1 Complete text-analysis example")

    document = """Python strings represent Unicode text.
They can contain ASCII, accented characters, symbols, and emoji.
Text processing requires attention to encoding and normalization."""

    statistics = analyze_text(document)
    print(statistics)

    frequencies = character_frequency(document.casefold())
    print("Most common characters:", frequencies.most_common(10))


# ============================================================================
# 24. TESTS
# ============================================================================

def run_tests() -> None:
    subsection("24. Automated tests")

    assert "Python"[0] == "P"
    assert "Python"[-1] == "n"
    assert "Python"[::-1] == "nohtyP"

    assert "abc" < "abd"
    assert "Python".casefold() == "python"
    assert "Straße".casefold() == "strasse"

    assert "é".encode("utf-8").decode("utf-8") == "é"
    assert unicodedata.normalize("NFC", "e\u0301") == "é"

    assert first_non_repeating_character("swiss") == "w"
    assert first_non_repeating_character("aabb") is None

    assert is_palindrome("Level")
    assert not is_palindrome("Python")

    assert reverse_words("one two three") == "three two one"

    valid, _ = validate_username("user_123")
    assert valid

    invalid, _ = validate_username("1user")
    assert not invalid

    parsed = parse_log_line("2026-09-25T10:00:00 INFO Started")
    assert parsed is not None
    assert parsed.level == "INFO"

    assert tokenize_text("one two three") == ["one", "two", "three"]

    print("All tests passed.")


# ============================================================================
# 25. STUDY CHECKLIST
# ============================================================================

def print_study_checklist() -> None:
    subsection("25. Study checklist")

    topics = [
        "String creation and literals",
        "String immutability",
        "Indexing and slicing",
        "Traversal and enumerate()",
        "ASCII",
        "Unicode code points",
        "ord() and chr()",
        "UTF-8 encoding and decoding",
        "String comparison",
        "casefold()",
        "Searching",
        "Splitting and joining",
        "Formatting",
        "Validation",
        "Regular expressions",
        "Frequency counting",
        "Palindrome algorithms",
        "String normalization",
        "Code points versus perceived characters",
        "str versus bytes",
        "Security concerns",
        "Text parsing",
        "Tokenization",
        "Sorting",
        "Performance",
        "Testing",
    ]

    for number, topic in enumerate(topics, start=1):
        print(f"{number:02d}. {topic}")


# ============================================================================
# MAIN
# ============================================================================

def main() -> None:
    section("STRINGS INTRODUCTION: COMPLETE PYTHON STUDY PROGRAM")

    demonstrate_string_creation()
    demonstrate_string_properties()

    demonstrate_characters_and_ordinals()
    demonstrate_ascii()
    demonstrate_unicode()
    demonstrate_utf8()

    demonstrate_indexing_and_slicing()
    demonstrate_traversal()

    demonstrate_comparison()
    demonstrate_searching()
    demonstrate_manipulation()
    demonstrate_formatting()

    demonstrate_validation()
    demonstrate_validation_function()
    demonstrate_regular_expressions()

    demonstrate_immutability_and_building()
    demonstrate_algorithms()

    demonstrate_unicode_normalization()
    demonstrate_unicode_subtleties()

    demonstrate_security_considerations()

    demonstrate_log_parser()
    demonstrate_tokenization()
    demonstrate_sorting()
    demonstrate_performance()

    demonstrate_text_and_bytes()
    demonstrate_advanced_features()

    demonstrate_password_policy()
    demonstrate_edge_cases()
    demonstrate_text_analyzer()

    run_tests()
    print_study_checklist()

    section("END OF STRING STUDY PROGRAM")
    print("The examples above are executable demonstrations of string concepts.")


if __name__ == "__main__":
    main()
