from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from collections import defaultdict
import json
import logging
import random

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger("advanced_trie")


# ============================================================
# 1. COMPRESSED TRIE (RADIX TREE)
# ============================================================

@dataclass
class RadixNode:
    children: dict[str, "RadixNode"] = field(default_factory=dict)
    is_terminal: bool = False
    value: Optional[str] = None


class CompressedTrie:
    """
    Compressed trie:
    - Stores common prefixes as shared edge labels.
    - Splits edges when inserting partially matching words.
    - Merges edges after deletion.
    - Supports exact search and prefix search.
    """

    def __init__(self):
        self.root = RadixNode()
        self.size = 0

    @staticmethod
    def common_prefix_length(a: str, b: str) -> int:
        limit = min(len(a), len(b))
        i = 0

        while i < limit and a[i] == b[i]:
            i += 1

        return i

    def insert(self, word: str, value: Optional[str] = None) -> bool:
        if not isinstance(word, str) or not word:
            raise ValueError("Word must be a non-empty string.")

        node = self.root
        remaining = word

        while remaining:
            first = remaining[0]

            if first not in node.children:
                node.children[first] = RadixNode(
                    is_terminal=True,
                    value=value if value is not None else word
                )
                # The edge label is stored separately.
                node.children[first]._edge = remaining
                self.size += 1
                return True

            child = node.children[first]
            edge = child._edge
            common = self.common_prefix_length(remaining, edge)

            if common == len(edge):
                remaining = remaining[common:]
                node = child

                if not remaining:
                    if child.is_terminal:
                        child.value = value if value is not None else word
                        return False

                    child.is_terminal = True
                    child.value = value if value is not None else word
                    self.size += 1
                    return True

                continue

            # Split an existing compressed edge.
            intermediate = RadixNode()
            old_suffix = edge[common:]
            child._edge = old_suffix
            intermediate.children[old_suffix[0]] = child

            node.children[first] = intermediate
            intermediate._edge = edge[:common]

            new_suffix = remaining[common:]

            if not new_suffix:
                intermediate.is_terminal = True
                intermediate.value = value if value is not None else word
            else:
                new_child = RadixNode(
                    is_terminal=True,
                    value=value if value is not None else word
                )
                new_child._edge = new_suffix
                intermediate.children[new_suffix[0]] = new_child

            self.size += 1
            return True

        return False

    def search(self, word: str) -> bool:
        if not isinstance(word, str) or not word:
            return False

        node = self.root
        remaining = word

        while remaining:
            child = node.children.get(remaining[0])

            if child is None:
                return False

            edge = child._edge

            if not remaining.startswith(edge):
                return False

            remaining = remaining[len(edge):]
            node = child

        return node.is_terminal

    def starts_with(self, prefix: str) -> bool:
        if not isinstance(prefix, str) or not prefix:
            return False

        node = self.root
        remaining = prefix

        while remaining:
            child = node.children.get(remaining[0])

            if child is None:
                return False

            edge = child._edge
            common = self.common_prefix_length(remaining, edge)

            if common == len(remaining):
                return True

            if common != len(edge):
                return False

            remaining = remaining[common:]
            node = child

        return True

    def delete(self, word: str) -> bool:
        if not self.search(word):
            return False

        def remove(node: RadixNode, remaining: str) -> None:
            child = node.children[remaining[0]]
            edge = child._edge
            suffix = remaining[len(edge):]

            if suffix:
                remove(child, suffix)
            else:
                child.is_terminal = False
                child.value = None

            if not child.is_terminal and not child.children:
                del node.children[edge[0]]
            elif not child.is_terminal and len(child.children) == 1:
                next_child = next(iter(child.children.values()))
                child._edge += next_child._edge
                child.children = next_child.children
                child.is_terminal = next_child.is_terminal
                child.value = next_child.value

        remove(self.root, word)
        self.size -= 1
        return True

    def autocomplete(self, prefix: str, limit: int = 10) -> list[str]:
        if limit < 0:
            raise ValueError("Limit cannot be negative.")

        if limit == 0:
            return []

        results = []

        def collect(node: RadixNode, current: str) -> None:
            if len(results) >= limit:
                return

            if node.is_terminal:
                results.append(current)

            for key in sorted(node.children):
                child = node.children[key]
                collect(child, current + child._edge)

                if len(results) >= limit:
                    break

        node = self.root
        remaining = prefix
        accumulated = ""

        while remaining:
            child = node.children.get(remaining[0])

            if child is None:
                return []

            edge = child._edge
            common = self.common_prefix_length(remaining, edge)

            if common < len(remaining) and common < len(edge):
                return []

            accumulated += edge
            remaining = remaining[common:]
            node = child

        collect(node, accumulated)
        return results


# ============================================================
# 2. BINARY TRIE
# ============================================================

@dataclass
class BitNode:
    children: list[Optional["BitNode"]] = field(
        default_factory=lambda: [None, None]
    )
    count: int = 0


class BinaryTrie:
    """
    Fixed-width binary trie.

    Supports:
    - Insert
    - Delete
    - Maximum XOR query
    - Minimum XOR query
    - Maximum XOR pair

    Duplicate values are supported through subtree counts.
    """

    def __init__(self, width: int = 32):
        if not 1 <= width <= 64:
            raise ValueError("Width must be between 1 and 64.")

        self.width = width
        self.limit = (1 << width) - 1
        self.root = BitNode()
        self.size = 0

    def _validate(self, number: int) -> None:
        if not isinstance(number, int) or isinstance(number, bool):
            raise TypeError("Expected an integer.")

        if not 0 <= number <= self.limit:
            raise ValueError(
                f"Number must be between 0 and {self.limit}."
            )

    def insert(self, number: int) -> None:
        self._validate(number)

        node = self.root
        node.count += 1

        for bit_position in range(self.width - 1, -1, -1):
            bit = (number >> bit_position) & 1

            if node.children[bit] is None:
                node.children[bit] = BitNode()

            node = node.children[bit]
            node.count += 1

        self.size += 1

    def contains(self, number: int) -> bool:
        self._validate(number)

        node = self.root

        for position in range(self.width - 1, -1, -1):
            bit = (number >> position) & 1
            node = node.children[bit]

            if node is None or node.count == 0:
                return False

        return True

    def delete(self, number: int) -> bool:
        self._validate(number)

        if not self.contains(number):
            return False

        node = self.root
        node.count -= 1

        for position in range(self.width - 1, -1, -1):
            bit = (number >> position) & 1
            child = node.children[bit]
            child.count -= 1

            if child.count == 0:
                node.children[bit] = None
                break

            node = child

        self.size -= 1
        return True

    def query_xor(self, number: int, maximize: bool = True):
        self._validate(number)

        if self.size == 0:
            raise ValueError("Cannot query an empty binary trie.")

        node = self.root
        xor_value = 0
        matched = 0

        for position in range(self.width - 1, -1, -1):
            bit = (number >> position) & 1

            preferred = 1 - bit if maximize else bit
            alternative = bit if maximize else 1 - bit

            if (
                node.children[preferred] is not None
                and node.children[preferred].count > 0
            ):
                chosen = preferred
            else:
                chosen = alternative

            if chosen != bit:
                xor_value |= 1 << position

            node = node.children[chosen]
            matched |= chosen << position

        return xor_value, matched

    def maximum_xor_pair(self, numbers: list[int]):
        if len(numbers) < 2:
            raise ValueError("At least two numbers are required.")

        for number in numbers:
            self._validate(number)

        self.root = BitNode()
        self.size = 0

        best = -1
        best_pair = None

        for number in numbers:
            if self.size:
                xor_value, matched = self.query_xor(number)

                if xor_value > best:
                    best = xor_value
                    best_pair = (number, matched)

            self.insert(number)

        return {
            "maximum_xor": best,
            "pair": best_pair
        }


# ============================================================
# 3. PREFIX DICTIONARY APPLICATION
# ============================================================

class PrefixDictionary:
    def __init__(self):
        self.trie = CompressedTrie()
        self.metadata = {}

    def add(self, word: str, category: str) -> None:
        if not category.strip():
            raise ValueError("Category cannot be empty.")

        self.trie.insert(word, category)
        self.metadata[word] = category

    def find(self, word: str):
        if not self.trie.search(word):
            return None

        return self.metadata.get(word)

    def suggest(self, prefix: str, limit: int = 10):
        return [
            {
                "word": word,
                "category": self.metadata.get(word)
            }
            for word in self.trie.autocomplete(prefix, limit)
        ]


# ============================================================
# 4. TESTING AND EXECUTION
# ============================================================

def test_compressed_trie():
    trie = CompressedTrie()

    words = [
        "application",
        "apply",
        "apple",
        "app",
        "banana",
        "band",
        "bandwidth",
        "binary",
    ]

    for word in words:
        assert trie.insert(word)

    assert trie.size == len(words)
    assert trie.search("application")
    assert trie.search("app")
    assert not trie.search("appl")

    assert trie.starts_with("appl")
    assert trie.starts_with("band")

    assert "apple" in trie.autocomplete("app")
    assert trie.delete("apple")
    assert not trie.search("apple")
    assert trie.search("application")

    assert not trie.delete("missing")

    return {
        "size": trie.size,
        "suggestions": trie.autocomplete("app")
    }


def test_binary_trie():
    trie = BinaryTrie(width=8)

    values = [3, 10, 5, 25, 2, 8]

    result = trie.maximum_xor_pair(values)

    assert result["maximum_xor"] == 28

    trie.insert(12)
    trie.insert(12)

    assert trie.contains(12)
    assert trie.delete(12)
    assert trie.contains(12)
    assert trie.delete(12)
    assert not trie.contains(12)

    return result


def test_edge_cases():
    trie = CompressedTrie()

    try:
        trie.insert("")
        raise AssertionError("Empty words must be rejected.")
    except ValueError:
        pass

    binary = BinaryTrie(width=4)

    try:
        binary.insert(16)
        raise AssertionError("Out-of-range values must be rejected.")
    except ValueError:
        pass

    try:
        binary.query_xor(1)
        raise AssertionError("Empty trie queries must fail.")
    except ValueError:
        pass

    return True


def benchmark():
    random.seed(42)

    numbers = [random.randint(0, 65535) for _ in range(10000)]

    trie = BinaryTrie(width=16)
    result = trie.maximum_xor_pair(numbers)

    return result


def main():
    print("\nCOMPRESSED TRIE")
    print(json.dumps(test_compressed_trie(), indent=2))

    print("\nBINARY TRIE")
    print(json.dumps(test_binary_trie(), indent=2))

    print("\nEDGE CASE VALIDATION")
    print("Passed:", test_edge_cases())

    print("\nPREFIX DICTIONARY")
    dictionary = PrefixDictionary()

    dictionary.add("postgresql", "database")
    dictionary.add("postman", "api")
    dictionary.add("python", "programming")
    dictionary.add("protocol", "networking")

    print(json.dumps(dictionary.suggest("post"), indent=2))

    print("\nRANDOMIZED MAXIMUM XOR")
    print(json.dumps(benchmark(), indent=2))

    print("\nALL TESTS COMPLETED")


if __name__ == "__main__":
    main()
