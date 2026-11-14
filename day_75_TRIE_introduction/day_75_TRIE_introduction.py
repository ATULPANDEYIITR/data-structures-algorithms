"""
TRIE INTRODUCTION: PREFIX TREES, NODE TRANSITIONS, AND PREFIX MATCHING

Features:
- Trie node and character-transition modeling
- Insertion and exact-word searching
- Prefix searching and autocomplete
- Word frequency tracking
- Deletion with node pruning
- Longest prefix matching
- Dictionary statistics
- JSON persistence
- Input validation and error handling
- Unit-style assertions and performance analysis

Python 3.10+
Standard library only.
"""

from __future__ import annotations

import json
import unicodedata
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


class TrieError(Exception):
    """Base exception for trie operations."""


class InvalidWordError(TrieError):
    """Raised when an invalid word is supplied."""


@dataclass
class TrieNode:
    children: dict[str, "TrieNode"] = field(default_factory=dict)
    is_end_of_word: bool = False
    frequency: int = 0


class Trie:
    """
    Character-based prefix tree.

    Each edge represents one Unicode code point.
    Words share nodes when they share prefixes.
    """

    def __init__(self, case_sensitive: bool = False):
        self.root = TrieNode()
        self.case_sensitive = case_sensitive
        self.word_count = 0
        self.total_insertions = 0

    def _normalize(self, word: str) -> str:
        if not isinstance(word, str):
            raise InvalidWordError("Word must be a string.")

        word = unicodedata.normalize("NFC", word.strip())

        if not word:
            raise InvalidWordError("Word cannot be empty.")

        if len(word) > 256:
            raise InvalidWordError("Word exceeds 256 characters.")

        if any(unicodedata.category(c).startswith("C") for c in word):
            raise InvalidWordError("Control characters are not allowed.")

        return word if self.case_sensitive else word.casefold()

    def insert(self, word: str) -> bool:
        """
        Insert a word.

        Returns True when a new word is created.
        Returns False when an existing word frequency is increased.
        """
        word = self._normalize(word)
        node = self.root

        for character in word:
            if character not in node.children:
                node.children[character] = TrieNode()
            node = node.children[character]

        is_new = not node.is_end_of_word

        if is_new:
            self.word_count += 1

        node.is_end_of_word = True
        node.frequency += 1
        self.total_insertions += 1

        return is_new

    def search(self, word: str) -> bool:
        """Check whether a complete word exists."""
        word = self._normalize(word)
        node = self.root

        for character in word:
            node = node.children.get(character)

            if node is None:
                return False

        return node.is_end_of_word

    def starts_with(self, prefix: str) -> bool:
        """Check whether any stored word starts with a prefix."""
        prefix = self._normalize(prefix)
        node = self.root

        for character in prefix:
            node = node.children.get(character)

            if node is None:
                return False

        return True

    def _find_node(self, text: str) -> Optional[TrieNode]:
        node = self.root

        for character in text:
            node = node.children.get(character)

            if node is None:
                return None

        return node

    def autocomplete(self, prefix: str, limit: int = 10) -> list[str]:
        """
        Return alphabetically ordered words matching a prefix.

        The limit prevents unnecessarily large result collections.
        """
        prefix = self._normalize(prefix)

        if not isinstance(limit, int) or isinstance(limit, bool):
            raise ValueError("Limit must be an integer.")

        if not 1 <= limit <= 1000:
            raise ValueError("Limit must be between 1 and 1000.")

        start = self._find_node(prefix)

        if start is None:
            return []

        results = []
        stack = [(start, prefix)]

        while stack and len(results) < limit:
            node, current_word = stack.pop()

            if node.is_end_of_word:
                results.append(current_word)

                if len(results) == limit:
                    break

            # Reverse insertion ensures ascending traversal with a LIFO stack.
            for character in sorted(node.children, reverse=True):
                stack.append(
                    (node.children[character], current_word + character)
                )

        return results

    def delete(self, word: str) -> bool:
        """
        Delete a complete word.

        Remove unnecessary nodes while preserving shared prefixes.
        """
        word = self._normalize(word)

        def remove(node: TrieNode, depth: int) -> bool:
            if depth == len(word):
                if not node.is_end_of_word:
                    return False

                node.is_end_of_word = False
                node.frequency = 0
                return not node.children

            character = word[depth]
            child = node.children.get(character)

            if child is None:
                return False

            should_prune = remove(child, depth + 1)

            if should_prune:
                del node.children[character]

            return (
                not node.is_end_of_word
                and not node.children
            )

        if not self.search(word):
            return False

        remove(self.root, 0)
        self.word_count -= 1
        return True

    def frequency(self, word: str) -> int:
        """Return the number of times a word was inserted."""
        word = self._normalize(word)
        node = self._find_node(word)

        if node is None or not node.is_end_of_word:
            return 0

        return node.frequency

    def longest_prefix(self, text: str) -> str:
        """
        Find the longest stored word that is a prefix of the input.
        """
        text = self._normalize(text)
        node = self.root
        longest = ""
        current = ""

        for character in text:
            node = node.children.get(character)

            if node is None:
                break

            current += character

            if node.is_end_of_word:
                longest = current

        return longest

    def statistics(self) -> dict:
        """Calculate trie size and structural statistics."""
        nodes = 0
        edges = 0
        terminal_nodes = 0
        maximum_depth = 0

        queue = deque([(self.root, 0)])

        while queue:
            node, depth = queue.popleft()
            nodes += 1
            maximum_depth = max(maximum_depth, depth)

            if node.is_end_of_word:
                terminal_nodes += 1

            for child in node.children.values():
                edges += 1
                queue.append((child, depth + 1))

        return {
            "words": self.word_count,
            "total_insertions": self.total_insertions,
            "nodes": nodes,
            "edges": edges,
            "terminal_nodes": terminal_nodes,
            "maximum_depth": maximum_depth,
        }

    def save(self, filename: str) -> None:
        """Persist the logical dictionary rather than internal node pointers."""
        words = self.autocomplete("", limit=1000)

        if self.word_count > 1000:
            words = self._all_words()

        data = {
            "version": 1,
            "case_sensitive": self.case_sensitive,
            "words": [
                {
                    "word": word,
                    "frequency": self.frequency(word)
                }
                for word in words
            ],
        }

        destination = Path(filename)
        temporary = destination.with_suffix(destination.suffix + ".tmp")

        try:
            temporary.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            temporary.replace(destination)
        except OSError as exc:
            temporary.unlink(missing_ok=True)
            raise TrieError(f"Unable to save trie: {exc}") from exc

    def _all_words(self) -> list[str]:
        results = []
        stack = [(self.root, "")]

        while stack:
            node, word = stack.pop()

            if node.is_end_of_word:
                results.append(word)

            for character in sorted(node.children, reverse=True):
                stack.append((node.children[character], word + character))

        return results

    @classmethod
    def load(cls, filename: str) -> "Trie":
        """Restore a trie with validated data."""
        try:
            data = json.loads(Path(filename).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise TrieError(f"Unable to load trie: {exc}") from exc

        if not isinstance(data, dict) or data.get("version") != 1:
            raise TrieError("Unsupported or invalid file format.")

        case_sensitive = data.get("case_sensitive")

        if not isinstance(case_sensitive, bool):
            raise TrieError("Invalid case sensitivity setting.")

        records = data.get("words")

        if not isinstance(records, list) or len(records) > 100000:
            raise TrieError("Invalid dictionary records.")

        trie = cls(case_sensitive=case_sensitive)

        for record in records:
            if not isinstance(record, dict):
                raise TrieError("Invalid word record.")

            word = record.get("word")
            frequency = record.get("frequency")

            if (
                not isinstance(frequency, int)
                or isinstance(frequency, bool)
                or not 1 <= frequency <= 1000000
            ):
                raise TrieError("Invalid word frequency.")

            for _ in range(frequency):
                trie.insert(word)

        return trie


def demonstrate_trie() -> None:
    print("=" * 65)
    print("TRIE: PREFIX TREE IMPLEMENTATION")
    print("=" * 65)

    trie = Trie()

    dictionary = [
        "apple",
        "application",
        "apply",
        "app",
        "apt",
        "bat",
        "batch",
        "bath",
        "banana",
        "band",
        "band",
        "cat",
        "car",
        "carbon",
        "care",
    ]

    print("\n1. INSERTION")

    for word in dictionary:
        created = trie.insert(word)
        print(f"{word:15} {'NEW' if created else 'EXISTING'}")

    print("\n2. EXACT SEARCH")

    for word in ["apple", "app", "application", "ap", "dog"]:
        print(f"{word:15} {trie.search(word)}")

    print("\n3. PREFIX SEARCH")

    for prefix in ["app", "ba", "car", "xyz"]:
        print(f"{prefix:15} {trie.starts_with(prefix)}")

    print("\n4. AUTOCOMPLETE")

    for prefix in ["app", "ba", "car"]:
        print(f"{prefix:15} {trie.autocomplete(prefix, 10)}")

    print("\n5. FREQUENCY")

    print("band frequency:", trie.frequency("band"))
    print("apple frequency:", trie.frequency("apple"))

    print("\n6. LONGEST PREFIX")

    for text in ["application_server", "batman", "carbon_copy"]:
        print(f"{text:25} {trie.longest_prefix(text)}")

    print("\n7. DELETION")

    print("Delete application:", trie.delete("application"))
    print("Search application:", trie.search("application"))
    print("Search apple:", trie.search("apple"))
    print("Remaining app suggestions:", trie.autocomplete("app"))

    print("\n8. UNICODE SUPPORT")

    trie.insert("café")
    trie.insert("naïve")
    trie.insert("東京")

    print("café:", trie.search("cafe\u0301"))
    print("東京:", trie.search("東京"))

    print("\n9. STATISTICS")

    for key, value in trie.statistics().items():
        print(f"{key:20}: {value}")

    print("\n10. JSON PERSISTENCE")

    filename = "trie_dictionary.json"

    try:
        trie.save(filename)
        restored = Trie.load(filename)

        print("Saved dictionary successfully.")
        print("Restored word count:", restored.word_count)
        print("Restored apple search:", restored.search("apple"))

        Path(filename).unlink(missing_ok=True)

    except TrieError as exc:
        print("Persistence error:", exc)

    print("\n11. EDGE CASES")

    try:
        trie.insert("")
    except InvalidWordError as exc:
        print("Empty input rejected:", exc)

    print("Delete missing word:", trie.delete("missing"))
    print("Search missing word:", trie.search("missing"))

    print("\n12. ASSERTION TESTS")

    test = Trie()
    assert test.insert("car")
    assert test.insert("cart")
    assert test.insert("cat")
    assert not test.insert("car")
    assert test.search("car")
    assert not test.search("ca")
    assert test.starts_with("ca")
    assert test.autocomplete("car") == ["car", "cart"]
    assert test.frequency("car") == 2
    assert test.delete("car")
    assert not test.search("car")
    assert test.search("cart")
    assert test.delete("cart")
    assert not test.starts_with("car")
    assert test.search("cat")

    print("All assertions passed.")

    print("\n" + "=" * 65)
    print("TRIE DEMONSTRATION COMPLETED")
    print("=" * 65)


if __name__ == "__main__":
    demonstrate_trie()
