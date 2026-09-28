"""
Hashing Introduction: Hash Functions, Hash Tables, Collisions, Chaining,
Open Addressing, and Load Factors

This standalone study script progresses from the basic idea of hashing to
practical hash-table implementations and advanced design considerations.

No external packages are required.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterator, Optional
import hashlib
import math
import random
import string
import time


# ============================================================================
# 1. FUNDAMENTAL CONCEPTS
# ============================================================================

def simple_remainder_hash(key: int, table_size: int) -> int:
    """Map an integer key into a valid table index."""
    if table_size <= 0:
        raise ValueError("table_size must be positive")
    return key % table_size


def polynomial_string_hash(text: str, table_size: int) -> int:
    """
    Polynomial rolling-style hash for demonstration.

    h(i+1) = (h(i) * base + character_code) mod table_size

    The modulus keeps the result inside the table.
    """
    if table_size <= 0:
        raise ValueError("table_size must be positive")

    value = 0
    base = 31

    for character in text:
        value = (value * base + ord(character)) % table_size

    return value


def demonstrate_basic_hashing() -> None:
    print("\n=== BASIC HASHING ===")

    table_size = 10
    numbers = [12, 25, 37, 41, 58]

    for number in numbers:
        print(
            f"key={number:>2} -> index={simple_remainder_hash(number, table_size)}"
        )

    words = ["cat", "dog", "hash", "table", "python"]

    for word in words:
        print(
            f"text={word!r:<8} -> index="
            f"{polynomial_string_hash(word, table_size)}"
        )


# ============================================================================
# 2. HASH FUNCTIONS: DESIRABLE PROPERTIES
# ============================================================================

def hash_function_properties() -> None:
    print("\n=== DESIRABLE HASH-FUNCTION PROPERTIES ===")

    properties = [
        "Deterministic: the same key produces the same hash under the same rules.",
        "Efficient: hashing should normally be inexpensive.",
        "Good distribution: keys should spread across buckets.",
        "Fixed output range: table indexing requires a bounded result.",
        "Avalanche behavior: small input changes should ideally alter the result.",
        "Low predictable clustering: related keys should not systematically collide.",
    ]

    for property_description in properties:
        print("-", property_description)

    print(
        "\nImportant distinction: a general-purpose hash-table hash is not "
        "automatically a cryptographic hash."
    )


def demonstrate_python_hash() -> None:
    print("\n=== PYTHON'S BUILT-IN HASH ===")

    values = [42, "hello", (1, 2, 3)]

    for value in values:
        print(f"{value!r:15} -> {hash(value)}")

    print(
        "\nPython's hash values should not be treated as stable persistent IDs. "
        "Some hash behavior is intentionally randomized between interpreter runs."
    )


# ============================================================================
# 3. CRYPTOGRAPHIC HASHING
# ============================================================================

def cryptographic_hash_demo() -> None:
    print("\n=== CRYPTOGRAPHIC HASHING ===")

    messages = [
        "hello",
        "Hello",
        "hello!",
        "The quick brown fox jumps over the lazy dog",
    ]

    for message in messages:
        digest = hashlib.sha256(message.encode("utf-8")).hexdigest()
        print(f"{message!r}\n  SHA-256: {digest}")

    print(
        "\nSHA-256 demonstrates a cryptographic digest. It is useful for "
        "integrity and fingerprinting, but a hash table normally needs a "
        "fast indexing hash rather than a cryptographic digest."
    )


# ============================================================================
# 4. COLLISIONS
# ============================================================================

def collision_demo() -> None:
    print("\n=== COLLISIONS ===")

    table_size = 5
    keys = [10, 15, 20, 7, 12]

    buckets: dict[int, list[int]] = {}

    for key in keys:
        index = key % table_size
        buckets.setdefault(index, []).append(key)

    for index in range(table_size):
        print(f"bucket {index}: {buckets.get(index, [])}")

    print(
        "\nA collision occurs when different keys map to the same table index."
    )


# ============================================================================
# 5. CHAINING HASH TABLE
# ============================================================================

@dataclass
class Entry:
    key: Any
    value: Any


class ChainedHashTable:
    """
    Hash table using separate chaining.

    Each bucket contains a list of entries. Colliding keys therefore occupy
    the same bucket instead of requiring another table position.
    """

    def __init__(self, capacity: int = 8) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")

        self._buckets: list[list[Entry]] = [[] for _ in range(capacity)]
        self._size = 0

    @property
    def capacity(self) -> int:
        return len(self._buckets)

    @property
    def size(self) -> int:
        return self._size

    @property
    def load_factor(self) -> float:
        return self._size / self.capacity

    def _index(self, key: Any) -> int:
        return hash(key) % self.capacity

    def put(self, key: Any, value: Any) -> None:
        index = self._index(key)
        bucket = self._buckets[index]

        for entry in bucket:
            if entry.key == key:
                entry.value = value
                return

        bucket.append(Entry(key, value))
        self._size += 1

    def get(self, key: Any, default: Any = None) -> Any:
        index = self._index(key)

        for entry in self._buckets[index]:
            if entry.key == key:
                return entry.value

        return default

    def contains(self, key: Any) -> bool:
        index = self._index(key)
        return any(entry.key == key for entry in self._buckets[index])

    def remove(self, key: Any) -> Any:
        index = self._index(key)
        bucket = self._buckets[index]

        for position, entry in enumerate(bucket):
            if entry.key == key:
                removed = bucket.pop(position)
                self._size -= 1
                return removed.value

        raise KeyError(key)

    def bucket_lengths(self) -> list[int]:
        return [len(bucket) for bucket in self._buckets]

    def __iter__(self) -> Iterator[tuple[Any, Any]]:
        for bucket in self._buckets:
            for entry in bucket:
                yield entry.key, entry.value

    def _resize(self, new_capacity: int) -> None:
        old_entries = list(self)

        self._buckets = [[] for _ in range(new_capacity)]
        self._size = 0

        for key, value in old_entries:
            self.put(key, value)

    def ensure_capacity(self) -> None:
        if self.load_factor > 0.75:
            self._resize(self.capacity * 2)

    def put_auto_resize(self, key: Any, value: Any) -> None:
        self.put(key, value)
        self.ensure_capacity()


def chaining_demo() -> None:
    print("\n=== SEPARATE CHAINING ===")

    table = ChainedHashTable(capacity=4)

    # These integer keys deliberately collide when capacity is 4.
    for key in [0, 4, 8, 12]:
        table.put(key, f"value-{key}")

    print("Bucket lengths:", table.bucket_lengths())
    print("Lookup key 8:", table.get(8))
    print("Contains key 12:", table.contains(12))

    removed = table.remove(8)
    print("Removed:", removed)
    print("Bucket lengths after removal:", table.bucket_lengths())

    print("\nAll entries:")
    for key, value in table:
        print(f"  {key} -> {value}")


# ============================================================================
# 6. OPEN ADDRESSING
# ============================================================================

class OpenAddressingHashTable:
    """
    Hash table using linear probing.

    Every entry lives directly inside the main array.

    State values:
        None       = never occupied
        TOMBSTONE  = previously occupied but deleted
        Entry      = active item
    """

    TOMBSTONE = object()

    def __init__(self, capacity: int = 8) -> None:
        if capacity < 3:
            raise ValueError("capacity must be at least 3")

        self._table: list[Any] = [None] * capacity
        self._size = 0

    @property
    def capacity(self) -> int:
        return len(self._table)

    @property
    def size(self) -> int:
        return self._size

    @property
    def load_factor(self) -> float:
        return self._size / self.capacity

    def _start_index(self, key: Any) -> int:
        return hash(key) % self.capacity

    def _find_slot(self, key: Any, for_insert: bool) -> Optional[int]:
        start = self._start_index(key)
        first_tombstone: Optional[int] = None

        for offset in range(self.capacity):
            index = (start + offset) % self.capacity
            item = self._table[index]

            if item is None:
                if for_insert:
                    return (
                        first_tombstone
                        if first_tombstone is not None
                        else index
                    )
                return None

            if item is self.TOMBSTONE:
                if first_tombstone is None:
                    first_tombstone = index
                continue

            if item.key == key:
                return index

        if for_insert:
            return first_tombstone

        return None

    def _resize(self, new_capacity: int) -> None:
        old_items = [
            item
            for item in self._table
            if item is not None and item is not self.TOMBSTONE
        ]

        self._table = [None] * new_capacity
        self._size = 0

        for item in old_items:
            self._insert_without_resize(item.key, item.value)

    def _insert_without_resize(self, key: Any, value: Any) -> None:
        index = self._find_slot(key, True)

        if index is None:
            raise RuntimeError("Hash table has no available slot")

        item = self._table[index]

        if item is None or item is self.TOMBSTONE:
            self._size += 1

        self._table[index] = Entry(key, value)

    def put(self, key: Any, value: Any) -> None:
        if (self._size + 1) / self.capacity > 0.70:
            self._resize(self.capacity * 2)

        self._insert_without_resize(key, value)

    def get(self, key: Any, default: Any = None) -> Any:
        index = self._find_slot(key, False)

        if index is None:
            return default

        return self._table[index].value

    def contains(self, key: Any) -> bool:
        return self._find_slot(key, False) is not None

    def remove(self, key: Any) -> Any:
        index = self._find_slot(key, False)

        if index is None:
            raise KeyError(key)

        value = self._table[index].value
        self._table[index] = self.TOMBSTONE
        self._size -= 1

        return value

    def occupied_slots(self) -> list[Any]:
        return self._table[:]


def open_addressing_demo() -> None:
    print("\n=== OPEN ADDRESSING WITH LINEAR PROBING ===")

    table = OpenAddressingHashTable(capacity=7)

    # Keys 0, 7, and 14 have the same initial index for capacity 7.
    for key in [0, 7, 14, 21]:
        table.put(key, f"value-{key}")

    print("Occupied slots:")
    for index, item in enumerate(table.occupied_slots()):
        if item is None:
            description = "EMPTY"
        elif item is table.TOMBSTONE:
            description = "TOMBSTONE"
        else:
            description = f"{item.key} -> {item.value}"

        print(f"  {index}: {description}")

    print("Lookup 14:", table.get(14))

    table.remove(7)

    print("\nAfter deleting key 7:")
    for index, item in enumerate(table.occupied_slots()):
        if item is None:
            description = "EMPTY"
        elif item is table.TOMBSTONE:
            description = "TOMBSTONE"
        else:
            description = f"{item.key} -> {item.value}"

        print(f"  {index}: {description}")

    print("Lookup 14 after deletion:", table.get(14))


# ============================================================================
# 7. PROBING STRATEGIES
# ============================================================================

def linear_probe(start: int, attempt: int, capacity: int) -> int:
    return (start + attempt) % capacity


def quadratic_probe(start: int, attempt: int, capacity: int) -> int:
    return (start + attempt * attempt) % capacity


def double_hash_probe(
    key: int,
    attempt: int,
    capacity: int,
    prime: int,
) -> int:
    first = key % capacity
    step = prime - (key % prime)
    return (first + attempt * step) % capacity


def probing_demo() -> None:
    print("\n=== PROBING STRATEGIES ===")

    capacity = 11
    key = 34
    start = key % capacity

    print("Linear probing:")
    print([linear_probe(start, i, capacity) for i in range(6)])

    print("Quadratic probing:")
    print([quadratic_probe(start, i, capacity) for i in range(6)])

    print("Double hashing:")
    print(
        [
            double_hash_probe(key, i, capacity, 7)
            for i in range(6)
        ]
    )

    print(
        "\nLinear probing is simple and cache-friendly but can create "
        "primary clustering. Quadratic probing reduces primary clustering "
        "but has stricter table-size and probe-sequence considerations. "
        "Double hashing uses a second hash to generate a step size."
    )


# ============================================================================
# 8. LOAD FACTOR
# ============================================================================

def load_factor_demo() -> None:
    print("\n=== LOAD FACTOR ===")

    for entries, capacity in [
        (0, 10),
        (3, 10),
        (5, 10),
        (7, 10),
        (9, 10),
    ]:
        load = entries / capacity
        print(
            f"entries={entries}, capacity={capacity}, "
            f"load_factor={load:.2f}"
        )

    print(
        "\nLoad factor α = number of stored elements / table capacity.\n"
        "Higher load factors usually mean more collisions or longer probe "
        "sequences. Exact performance depends on the collision strategy and "
        "the quality of the hash function."
    )


# ============================================================================
# 9. FREQUENCY COUNTING
# ============================================================================

def character_frequency(text: str) -> dict[str, int]:
    frequencies: dict[str, int] = {}

    for character in text:
        frequencies[character] = frequencies.get(character, 0) + 1

    return frequencies


def word_frequency(text: str) -> dict[str, int]:
    frequencies: dict[str, int] = {}

    for word in text.lower().split():
        cleaned = word.strip(string.punctuation)
        if cleaned:
            frequencies[cleaned] = frequencies.get(cleaned, 0) + 1

    return frequencies


def frequency_demo() -> None:
    print("\n=== HASHING APPLICATION: FREQUENCY COUNTING ===")

    text = "hash tables make fast lookup possible and hash tables count data"

    print("Character frequencies:", character_frequency("banana"))
    print("Word frequencies:", word_frequency(text))


# ============================================================================
# 10. DEDUPLICATION
# ============================================================================

def deduplicate_preserving_order(values: list[Any]) -> list[Any]:
    seen: set[Any] = set()
    result: list[Any] = []

    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)

    return result


def deduplication_demo() -> None:
    print("\n=== HASHING APPLICATION: DEDUPLICATION ===")

    values = [4, 2, 4, 1, 2, 8, 1, 9]
    print("Input:", values)
    print("Unique:", deduplicate_preserving_order(values))


# ============================================================================
# 11. TWO-SUM USING HASHING
# ============================================================================

def two_sum(values: list[int], target: int) -> Optional[tuple[int, int]]:
    """
    Return indexes of two values whose sum equals target.

    Average-case complexity: O(n)
    Extra space: O(n)
    """
    positions: dict[int, int] = {}

    for index, value in enumerate(values):
        needed = target - value

        if needed in positions:
            return positions[needed], index

        positions[value] = index

    return None


def two_sum_demo() -> None:
    print("\n=== HASHING APPLICATION: TWO-SUM ===")

    values = [4, 9, 1, 7, 5, 3]
    target = 12

    result = two_sum(values, target)

    print("Values:", values)
    print("Target:", target)
    print("Indexes:", result)

    if result:
        i, j = result
        print(f"Verification: {values[i]} + {values[j]} = {target}")


# ============================================================================
# 12. CUSTOM OBJECT HASHING
# ============================================================================

@dataclass(frozen=True)
class UserKey:
    username: str
    tenant_id: int


def custom_object_demo() -> None:
    print("\n=== CUSTOM HASHABLE OBJECT ===")

    users: dict[UserKey, str] = {}

    users[UserKey("alice", 1)] = "Administrator"
    users[UserKey("alice", 2)] = "Analyst"

    lookup_key = UserKey("alice", 1)

    print("Lookup:", users[lookup_key])
    print("Distinct keys:", len(users))

    print(
        "\nImmutable/frozen objects are suitable dictionary keys because "
        "their equality and hash-relevant state cannot accidentally change "
        "after insertion."
    )


# ============================================================================
# 13. HASH/EQUALITY CONTRACT
# ============================================================================

class CorrectKey:
    def __init__(self, identifier: int) -> None:
        self.identifier = identifier

    def __hash__(self) -> int:
        return hash(self.identifier)

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, CorrectKey)
            and self.identifier == other.identifier
        )


def equality_hash_contract_demo() -> None:
    print("\n=== EQUALITY AND HASH CONTRACT ===")

    first = CorrectKey(10)
    second = CorrectKey(10)

    print("first == second:", first == second)
    print("hash(first) == hash(second):", hash(first) == hash(second))

    print(
        "\nRule: if a == b is true, hash(a) must equal hash(b). "
        "The reverse is not required because collisions are possible."
    )


# ============================================================================
# 14. EDGE CASES
# ============================================================================

def edge_case_demo() -> None:
    print("\n=== EDGE CASES ===")

    table = ChainedHashTable(3)

    cases = [
        ("empty string", ""),
        ("zero", 0),
        ("negative integer", -10),
        ("tuple", ("a", 1)),
        ("large integer", 10**100),
    ]

    for description, key in cases:
        table.put(key, description)

    for _, key in cases:
        print(f"{key!r} -> {table.get(key)}")

    print(
        "\nA good implementation must also consider empty tables, repeated "
        "keys, deletion, extreme load factors, duplicate values, unusual "
        "keys, and invalid capacities."
    )


# ============================================================================
# 15. RESIZING AND AMORTIZED PERFORMANCE
# ============================================================================

def resizing_demo() -> None:
    print("\n=== RESIZING ===")

    table = ChainedHashTable(2)

    for number in range(20):
        table.put_auto_resize(number, number * number)

        print(
            f"insert={number:2}, size={table.size:2}, "
            f"capacity={table.capacity:2}, "
            f"load={table.load_factor:.2f}"
        )

    print(
        "\nResizing costs O(n) for the resize operation because entries must "
        "be rehashed. Geometric growth makes the average insertion cost "
        "amortized O(1)."
    )


# ============================================================================
# 16. DISTRIBUTION EXPERIMENT
# ============================================================================

def distribution_experiment() -> None:
    print("\n=== HASH DISTRIBUTION EXPERIMENT ===")

    capacity = 17
    bucket_counts = [0] * capacity

    random_generator = random.Random(42)

    for _ in range(500):
        key = random_generator.randrange(0, 1_000_000)
        bucket_counts[key % capacity] += 1

    print("Bucket counts:")
    print(bucket_counts)

    average = sum(bucket_counts) / capacity
    maximum = max(bucket_counts)
    minimum = min(bucket_counts)

    print(f"Average bucket population: {average:.2f}")
    print(f"Minimum: {minimum}")
    print(f"Maximum: {maximum}")


# ============================================================================
# 17. PERFORMANCE COMPARISON
# ============================================================================

def benchmark_lookup_structures() -> None:
    print("\n=== SIMPLE LOOKUP PERFORMANCE EXPERIMENT ===")

    number_of_items = 50_000
    values = list(range(number_of_items))
    random_generator = random.Random(7)

    dictionary = {value: value * 2 for value in values}
    target_values = [
        random_generator.randrange(number_of_items)
        for _ in range(20_000)
    ]

    start = time.perf_counter()

    checksum = 0
    for target in target_values:
        checksum += dictionary[target]

    elapsed = time.perf_counter() - start

    print(f"Dictionary lookup checksum: {checksum}")
    print(f"Elapsed time: {elapsed:.6f} seconds")

    print(
        "\nThis is an illustrative local benchmark, not a universal ranking. "
        "Actual results depend on hardware, runtime, key types, data "
        "distribution, and implementation details."
    )


# ============================================================================
# 18. COMPLEXITY TABLE
# ============================================================================

def print_complexity_table() -> None:
    print("\n=== TYPICAL COMPLEXITIES ===")

    rows = [
        ("Hash-table lookup", "Average O(1)", "Worst O(n)"),
        ("Hash-table insertion", "Average O(1)", "Worst O(n)"),
        ("Hash-table deletion", "Average O(1)", "Worst O(n)"),
        ("Resize", "O(n)", "O(n)"),
        ("Linear search", "O(n)", "O(n)"),
        ("Sorting for lookup", "O(log n) lookup", "O(log n) lookup"),
    ]

    print(f"{'Operation':30} {'Typical':20} {'Worst':20}")
    print("-" * 72)

    for operation, typical, worst in rows:
        print(f"{operation:30} {typical:20} {worst:20}")

    print(
        "\nHash tables are usually described as average-case O(1), not "
        "guaranteed O(1). Poor hashing, adversarial input, or extreme "
        "collisions can degrade performance."
    )


# ============================================================================
# 19. SECURITY CONSIDERATIONS
# ============================================================================

def security_demo() -> None:
    print("\n=== SECURITY CONSIDERATIONS ===")

    password = "correct horse battery staple"

    digest = hashlib.sha256(password.encode()).hexdigest()

    print("Example SHA-256 digest:", digest)

    print(
        "\nSecurity principles:\n"
        "1. Do not store plaintext passwords.\n"
        "2. SHA-256 alone is not a password-storage scheme because password "
        "hashing should use a deliberately slow, salted password KDF.\n"
        "3. Hash-table implementations exposed to attackers should consider "
        "collision attacks and denial-of-service risks.\n"
        "4. Secret-sensitive applications should use appropriate cryptographic "
        "libraries rather than inventing cryptographic primitives."
    )


# ============================================================================
# 20. DESIGN COMPARISON
# ============================================================================

def compare_collision_strategies() -> None:
    print("\n=== CHAINING VS OPEN ADDRESSING ===")

    comparisons = [
        ("Storage", "Separate buckets", "Entries stored in main array"),
        ("Deletion", "Usually straightforward", "Requires tombstones or reorganization"),
        ("Memory", "Bucket/list overhead", "Compact array representation"),
        ("Cache locality", "Often lower", "Often higher"),
        ("High load factor", "Can tolerate it better", "Performance usually degrades sharply"),
        ("Implementation", "Conceptually simpler", "More sensitive to probe logic"),
    ]

    print(
        f"{'Aspect':20} {'Chaining':35} {'Open Addressing':35}"
    )
    print("-" * 94)

    for aspect, chaining, open_addressing in comparisons:
        print(f"{aspect:20} {chaining:35} {open_addressing:35}")


# ============================================================================
# 21. MINI IN-MEMORY CACHE
# ============================================================================

class SimpleCache:
    """
    A small hash-based cache.

    This demonstrates a realistic use of dictionary/hash-table semantics.
    This class intentionally does not implement expiration or LRU eviction;
    those are separate cache-management policies.
    """

    def __init__(self, max_items: int) -> None:
        if max_items <= 0:
            raise ValueError("max_items must be positive")

        self.max_items = max_items
        self._data: dict[str, Any] = {}

    def get(self, key: str) -> Optional[Any]:
        return self._data.get(key)

    def set(self, key: str, value: Any) -> None:
        if key not in self._data and len(self._data) >= self.max_items:
            oldest_key = next(iter(self._data))
            del self._data[oldest_key]

        self._data[key] = value

    def contains(self, key: str) -> bool:
        return key in self._data


def cache_demo() -> None:
    print("\n=== HASH-BASED CACHE ===")

    cache = SimpleCache(max_items=3)

    cache.set("user:1", {"name": "Alice"})
    cache.set("user:2", {"name": "Bob"})
    cache.set("user:3", {"name": "Carol"})

    print("user:2:", cache.get("user:2"))

    cache.set("user:4", {"name": "David"})

    print("user:1 still cached:", cache.contains("user:1"))
    print("user:4 cached:", cache.contains("user:4"))


# ============================================================================
# 22. TESTS
# ============================================================================

def run_tests() -> None:
    print("\n=== SELF-TESTS ===")

    table = ChainedHashTable(4)

    table.put("a", 1)
    assert table.get("a") == 1

    table.put("a", 2)
    assert table.get("a") == 2

    table.put("b", 3)
    assert table.contains("b")

    assert table.remove("a") == 2
    assert not table.contains("a")

    open_table = OpenAddressingHashTable(5)

    for key in [1, 6, 11]:
        open_table.put(key, key * 10)

    assert open_table.get(11) == 110

    open_table.remove(6)
    assert open_table.get(11) == 110

    assert two_sum([2, 7, 11, 15], 9) == (0, 1)
    assert two_sum([1, 2, 3], 100) is None

    assert deduplicate_preserving_order(
        [1, 2, 1, 3, 2]
    ) == [1, 2, 3]

    assert character_frequency("banana") == {
        "b": 1,
        "a": 3,
        "n": 2,
    }

    print("All tests passed.")


# ============================================================================
# 23. MAIN STUDY RUNNER
# ============================================================================

def main() -> None:
    print("=" * 78)
    print("HASHING INTRODUCTION: COMPLETE PYTHON STUDY")
    print("=" * 78)

    demonstrate_basic_hashing()
    hash_function_properties()
    demonstrate_python_hash()
    cryptographic_hash_demo()
    collision_demo()
    chaining_demo()
    open_addressing_demo()
    probing_demo()
    load_factor_demo()
    frequency_demo()
    deduplication_demo()
    two_sum_demo()
    custom_object_demo()
    equality_hash_contract_demo()
    edge_case_demo()
    resizing_demo()
    distribution_experiment()
    benchmark_lookup_structures()
    print_complexity_table()
    security_demo()
    compare_collision_strategies()
    cache_demo()
    run_tests()

    print("\n=== STUDY COMPLETE ===")
    print(
        "Core ideas covered: hash functions, indexing, collisions, chaining, "
        "open addressing, probing, load factor, resizing, hashing applications, "
        "custom keys, complexity, performance, and security."
    )


if __name__ == "__main__":
    main()
