#!/usr/bin/env python3
"""
Trie Applications
=================
Implements:
- Trie insertion, search, deletion, and prefix searching
- Autocomplete with frequency-based ranking
- Longest prefix matching
- Wildcard dictionary searching
- Word Break using trie-guided dynamic programming
- Word Search II using trie-guided DFS
- Input validation and executable tests

Python 3.10+
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Iterable, Optional
import json
import logging
import re
import unittest


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

LOGGER = logging.getLogger("trie_applications")

ALPHABET_PATTERN = re.compile(r"^[a-z]+$")


def normalize_word(word: str) -> str:
    if not isinstance(word, str):
        raise TypeError("Word must be a string.")

    word = word.strip().lower()

    if not word:
        raise ValueError("Word cannot be empty.")

    if not ALPHABET_PATTERN.fullmatch(word):
        raise ValueError("Only alphabetic English characters are supported.")

    return word


@dataclass
class TrieNode:
    children: dict[str, "TrieNode"] = field(default_factory=dict)
    is_end: bool = False
    frequency: int = 0


class Trie:
    """Prefix tree supporting dictionary and autocomplete operations."""

    def __init__(self) -> None:
        self.root = TrieNode()
        self.word_count = 0

    def insert(self, word: str, frequency: int = 1) -> bool:
        word = normalize_word(word)

        if not isinstance(frequency, int) or isinstance(frequency, bool):
            raise TypeError("Frequency must be an integer.")

        if frequency <= 0:
            raise ValueError("Frequency must be positive.")

        node = self.root

        for character in word:
            node = node.children.setdefault(character, TrieNode())

        is_new = not node.is_end
        node.is_end = True
        node.frequency += frequency

        if is_new:
            self.word_count += 1

        return is_new

    def _find_node(self, prefix: str) -> Optional[TrieNode]:
        node = self.root

        for character in prefix:
            node = node.children.get(character)

            if node is None:
                return None

        return node

    def search(self, word: str) -> bool:
        word = normalize_word(word)
        node = self._find_node(word)
        return node is not None and node.is_end

    def starts_with(self, prefix: str) -> bool:
        prefix = normalize_word(prefix)
        return self._find_node(prefix) is not None

    def frequency(self, word: str) -> int:
        word = normalize_word(word)
        node = self._find_node(word)

        return node.frequency if node and node.is_end else 0

    def delete(self, word: str) -> bool:
        word = normalize_word(word)

        def remove(node: TrieNode, index: int) -> tuple[bool, bool]:
            if index == len(word):
                if not node.is_end:
                    return False, False

                node.is_end = False
                node.frequency = 0
                return True, not node.children

            character = word[index]
            child = node.children.get(character)

            if child is None:
                return False, False

            deleted, prune_child = remove(child, index + 1)

            if prune_child:
                del node.children[character]

            should_prune = (
                not node.is_end and not node.children
            )

            return deleted, should_prune

        deleted, _ = remove(self.root, 0)

        if deleted:
            self.word_count -= 1

        return deleted

    def autocomplete(
        self,
        prefix: str,
        limit: int = 10
    ) -> list[tuple[str, int]]:
        prefix = normalize_word(prefix)

        if not isinstance(limit, int) or isinstance(limit, bool):
            raise TypeError("Limit must be an integer.")

        if limit < 0:
            raise ValueError("Limit cannot be negative.")

        if limit == 0:
            return []

        start = self._find_node(prefix)

        if start is None:
            return []

        results: list[tuple[str, int]] = []
        stack = [(start, prefix)]

        while stack:
            node, current = stack.pop()

            if node.is_end:
                results.append((current, node.frequency))

            for character in sorted(node.children, reverse=True):
                stack.append((
                    node.children[character],
                    current + character
                ))

        results.sort(key=lambda item: (-item[1], item[0]))

        return results[:limit]

    def longest_prefix(self, text: str) -> str:
        text = normalize_word(text)

        node = self.root
        longest = ""

        for index, character in enumerate(text):
            node = node.children.get(character)

            if node is None:
                break

            if node.is_end:
                longest = text[:index + 1]

        return longest

    def wildcard_search(self, pattern: str) -> list[str]:
        """
        Supports:
        . = exactly one arbitrary alphabetic character
        * = zero or more arbitrary alphabetic characters
        """
        if not isinstance(pattern, str):
            raise TypeError("Pattern must be a string.")

        pattern = pattern.strip().lower()

        if not pattern:
            raise ValueError("Pattern cannot be empty.")

        if not re.fullmatch(r"[a-z.*]+", pattern):
            raise ValueError("Invalid wildcard pattern.")

        results: set[str] = set()
        visited: set[tuple[int, int]] = set()

        def dfs(
            node: TrieNode,
            index: int,
            current: str
        ) -> None:
            state = (id(node), index)

            if state in visited:
                return

            visited.add(state)

            if index == len(pattern):
                if node.is_end:
                    results.add(current)
                return

            token = pattern[index]

            if token == ".":
                for character, child in node.children.items():
                    dfs(child, index + 1, current + character)

            elif token == "*":
                dfs(node, index + 1, current)

                for character, child in node.children.items():
                    dfs(child, index, current + character)

            else:
                child = node.children.get(token)

                if child:
                    dfs(child, index + 1, current + token)

        dfs(self.root, 0, "")

        return sorted(results)

    def all_words(self) -> list[str]:
        return [
            word
            for word, _ in self.autocomplete_from_root()
        ]

    def autocomplete_from_root(self) -> list[tuple[str, int]]:
        results: list[tuple[str, int]] = []
        stack = [(self.root, "")]

        while stack:
            node, current = stack.pop()

            if node.is_end:
                results.append((current, node.frequency))

            for character, child in node.children.items():
                stack.append((child, current + character))

        return sorted(results)

    def __len__(self) -> int:
        return self.word_count


class WordDictionary:
    """Dictionary supporting exact and wildcard queries."""

    def __init__(self, words: Iterable[str] = ()) -> None:
        self.trie = Trie()

        for word in words:
            self.add_word(word)

    def add_word(self, word: str) -> None:
        self.trie.insert(word)

    def search(self, pattern: str) -> bool:
        return bool(self.trie.wildcard_search(pattern))


def word_break(text: str, trie: Trie) -> bool:
    """Determine whether a string can be segmented into dictionary words."""

    if not isinstance(text, str):
        raise TypeError("Text must be a string.")

    text = text.strip().lower()

    if not text:
        return True

    if not ALPHABET_PATTERN.fullmatch(text):
        raise ValueError("Text must contain alphabetic characters only.")

    n = len(text)
    reachable = [False] * (n + 1)
    reachable[0] = True

    for start in range(n):
        if not reachable[start]:
            continue

        node = trie.root

        for end in range(start, n):
            node = node.children.get(text[end])

            if node is None:
                break

            if node.is_end:
                reachable[end + 1] = True

    return reachable[n]


def word_break_sentences(
    text: str,
    trie: Trie,
    max_results: int = 100
) -> list[str]:
    """Return valid dictionary segmentations with bounded output."""

    if not isinstance(text, str):
        raise TypeError("Text must be a string.")

    if not isinstance(max_results, int) or isinstance(max_results, bool):
        raise TypeError("Maximum results must be an integer.")

    if max_results < 0:
        raise ValueError("Maximum results cannot be negative.")

    text = text.strip().lower()

    if not text:
        return []

    if not ALPHABET_PATTERN.fullmatch(text):
        raise ValueError("Invalid input text.")

    if max_results == 0:
        return []

    memo: dict[int, list[tuple[str, ...]]] = {}

    def solve(index: int) -> list[tuple[str, ...]]:
        if index == len(text):
            return [()]

        if index in memo:
            return memo[index]

        results: list[tuple[str, ...]] = []
        node = trie.root

        for end in range(index, len(text)):
            node = node.children.get(text[end])

            if node is None:
                break

            if node.is_end:
                word = text[index:end + 1]

                for suffix in solve(end + 1):
                    results.append((word,) + suffix)

                    if len(results) >= max_results:
                        memo[index] = results
                        return results

        memo[index] = results
        return results

    return [
        " ".join(words)
        for words in solve(0)
    ][:max_results]


def word_search_ii(
    board: list[list[str]],
    words: Iterable[str]
) -> list[str]:
    """
    Find all dictionary words present in a character grid.

    Movement is horizontal or vertical.
    A cell cannot be reused within one word.
    """
    if not isinstance(board, list):
        raise TypeError("Board must be a list.")

    if not board:
        return []

    if not isinstance(words, Iterable):
        raise TypeError("Words must be iterable.")

    if not isinstance(words, (list, tuple, set)):
        words = list(words)

    rows = len(board)

    if any(not isinstance(row, list) for row in board):
        raise TypeError("Each board row must be a list.")

    columns = len(board[0])

    if columns == 0 or any(len(row) != columns for row in board):
        raise ValueError("Board must be rectangular and nonempty.")

    normalized_board: list[list[str]] = []

    for row in board:
        normalized_row = []

        for cell in row:
            if not isinstance(cell, str):
                raise TypeError("Board cells must be strings.")

            cell = cell.lower()

            if len(cell) != 1 or not ALPHABET_PATTERN.fullmatch(cell):
                raise ValueError("Each board cell must contain one letter.")

            normalized_row.append(cell)

        normalized_board.append(normalized_row)

    trie = Trie()

    for word in words:
        trie.insert(word)

    found: set[str] = set()
    directions = ((1, 0), (-1, 0), (0, 1), (0, -1))

    def dfs(
        row: int,
        column: int,
        node: TrieNode,
        current: str
    ) -> None:
        character = normalized_board[row][column]
        child = node.children.get(character)

        if child is None:
            return

        current += character

        if child.is_end:
            found.add(current)

            # Remove the terminal marker to avoid repeated discoveries.
            child.is_end = False
            trie.word_count -= 1

        normalized_board[row][column] = "#"

        for dr, dc in directions:
            nr = row + dr
            nc = column + dc

            if (
                0 <= nr < rows
                and 0 <= nc < columns
                and normalized_board[nr][nc] != "#"
            ):
                dfs(nr, nc, child, current)

        normalized_board[row][column] = character

    for row in range(rows):
        for column in range(columns):
            dfs(row, column, trie.root, "")

    return sorted(found)


def load_dictionary(path: str) -> Trie:
    """Load newline-separated words from a UTF-8 dictionary file."""

    trie = Trie()

    try:
        with open(path, "r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                word = line.strip()

                if not word:
                    continue

                try:
                    trie.insert(word)
                except (ValueError, TypeError) as error:
                    LOGGER.warning(
                        "Skipping line %d: %s",
                        line_number,
                        error
                    )

    except OSError as error:
        raise RuntimeError(
            f"Unable to read dictionary file: {error}"
        ) from error

    return trie


def save_dictionary(trie: Trie, path: str) -> None:
    """Persist dictionary words and frequencies as JSON."""

    data = {
        word: frequency
        for word, frequency in trie.autocomplete_from_root()
    }

    try:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, sort_keys=True)
    except OSError as error:
        raise RuntimeError(
            f"Unable to save dictionary: {error}"
        ) from error


def load_saved_dictionary(path: str) -> Trie:
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("Dictionary file must contain a JSON object.")

    trie = Trie()

    for word, frequency in data.items():
        trie.insert(word, frequency)

    return trie


class TrieTests(unittest.TestCase):

    def setUp(self) -> None:
        self.trie = Trie()

        for word in [
            "apple",
            "app",
            "application",
            "apply",
            "banana",
            "band",
            "bandana",
            "bat",
            "ball"
        ]:
            self.trie.insert(word)

        self.trie.insert("apple", 5)

    def test_exact_search(self) -> None:
        self.assertTrue(self.trie.search("apple"))
        self.assertFalse(self.trie.search("appl"))

    def test_prefix_search(self) -> None:
        self.assertTrue(self.trie.starts_with("app"))
        self.assertFalse(self.trie.starts_with("xyz"))

    def test_autocomplete(self) -> None:
        results = self.trie.autocomplete("app", 3)

        self.assertEqual(results[0][0], "apple")
        self.assertEqual(len(results), 3)

    def test_delete(self) -> None:
        self.assertTrue(self.trie.delete("app"))
        self.assertFalse(self.trie.search("app"))
        self.assertTrue(self.trie.search("apple"))

    def test_wildcard(self) -> None:
        self.assertIn("apple", self.trie.wildcard_search("app.."))

    def test_longest_prefix(self) -> None:
        self.assertEqual(
            self.trie.longest_prefix("application"),
            "app"
        )

    def test_word_break(self) -> None:
        self.assertTrue(word_break("applebanana", self.trie))
        self.assertFalse(word_break("applexyz", self.trie))

    def test_word_break_sentences(self) -> None:
        dictionary = Trie()

        for word in ["cat", "cats", "and", "sand", "dog"]:
            dictionary.insert(word)

        results = word_break_sentences("catsanddog", dictionary)

        self.assertEqual(
            results,
            ["cat sand dog", "cats and dog"]
        )

    def test_validation(self) -> None:
        with self.assertRaises(ValueError):
            self.trie.insert("hello123")

    def test_frequency(self) -> None:
        self.assertEqual(self.trie.frequency("apple"), 6)

    def test_empty_prefix_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.trie.autocomplete("")

    def test_word_search(self) -> None:
        board = [
            ["o", "a", "a", "n"],
            ["e", "t", "a", "e"],
            ["i", "h", "k", "r"],
            ["i", "f", "l", "v"]
        ]

        words = ["oath", "pea", "eat", "rain"]

        self.assertEqual(
            word_search_ii(board, words),
            ["eat", "oath"]
        )


def demonstrate() -> None:
    print("\nTRIE APPLICATIONS")
    print("=" * 55)

    trie = Trie()

    words = [
        "apple",
        "app",
        "application",
        "apply",
        "apt",
        "banana",
        "band",
        "bandana",
        "bat",
        "ball",
        "cat",
        "cats",
        "and",
        "sand",
        "dog"
    ]

    for word in words:
        trie.insert(word)

    trie.insert("apple", 10)
    trie.insert("application", 4)

    print("\nDictionary size:", len(trie))
    print("Exact search:", trie.search("apple"))
    print("Prefix exists:", trie.starts_with("app"))

    print("\nAutocomplete:")
    for word, frequency in trie.autocomplete("app", 5):
        print(f"{word:20} frequency={frequency}")

    print("\nLongest dictionary prefix:")
    print(trie.longest_prefix("application"))

    print("\nWildcard search:")
    print(trie.wildcard_search("app.."))

    print("\nWord Break:")
    print(word_break("catsanddog", trie))

    print("\nWord Break Sentences:")
    print(word_break_sentences("catsanddog", trie))

    board = [
        ["o", "a", "a", "n"],
        ["e", "t", "a", "e"],
        ["i", "h", "k", "r"],
        ["i", "f", "l", "v"]
    ]

    print("\nWord Search II:")
    print(word_search_ii(
        board,
        ["oath", "pea", "eat", "rain"]
    ))

    print("\nDelete operation:")
    print("Deleted:", trie.delete("application"))
    print("Still exists:", trie.search("application"))

    print("\nAll operations completed.")


if __name__ == "__main__":
    demonstrate()

    print("\nRUNNING UNIT TESTS")
    unittest.main(argv=["trie_applications.py"], exit=False)
