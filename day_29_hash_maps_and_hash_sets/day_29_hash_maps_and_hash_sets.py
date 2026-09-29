"""
Hash Maps and Hash Sets
=======================

A comprehensive executable study file covering:
- Hashing fundamentals
- Hash maps / dictionaries
- Hash sets
- Lookup, insertion, deletion
- Frequency counting
- Duplicate detection
- Set operations
- Collision handling
- Load factor and resizing
- Complexity and trade-offs
- Python-specific behavior
- Custom hash-table implementations
- Advanced patterns
- Edge cases, validation, testing, and practical applications

The script uses only the Python standard library.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from time import perf_counter
from typing import Any, Iterable, Iterator, Optional


# ============================================================================
# 1. FUNDAMENTAL TERMINOLOGY
# ============================================================================
#
# A hash table stores key/value or key-only information by transforming a key
# into an array index using a hash function.
#
# Typical average-case complexity:
#
#   Lookup:    O(1)
#   Insert:    O(1)
#   Delete:    O(1)
#
# Worst-case complexity can become O(n), usually because many keys collide.
#
# A hash map stores associations:
#
#   key -> value
#
# A hash set stores unique keys:
#
#   key
#
# Python's dict is a hash map.
# Python's set is a hash set.
#
# A critical distinction:
#
#   List membership:       O(n) average
#   Set/dict membership:   O(1) average
#
# Hash-based structures trade memory usage for fast average-case operations.


def section(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


# ============================================================================
# 2. BASIC HASH MAP OPERATIONS
# ============================================================================

def demonstrate_dictionary_basics() -> None:
    section("2. Python Dictionary: Basic Hash Map Operations")

    student = {
        "name": "Atul",
        "age": 30,
        "department": "Computer Science",
    }

    # Average-case O(1) lookup.
    print("Name:", student["name"])

    # Safer lookup when a key may not exist.
    print("City:", student.get("city", "Unknown"))

    # Insert a new key/value pair.
    student["city"] = "Lucknow"

    # Update an existing value.
    student["age"] = 31

    print("Updated map:", student)

    # Membership tests keys, not values.
    print("'name' in student:", "name" in student)
    print("'Atul' in student:", "Atul" in student)

    # Delete a key.
    removed_city = student.pop("city")
    print("Removed city:", removed_city)

    # Avoid KeyError with pop's default value.
    removed_missing = student.pop("country", None)
    print("Missing removal result:", removed_missing)

    print("Final map:", student)


# ============================================================================
# 3. ITERATING THROUGH A HASH MAP
# ============================================================================

def demonstrate_dictionary_iteration() -> None:
    section("3. Dictionary Iteration")

    prices = {
        "apple": 120,
        "banana": 60,
        "orange": 90,
    }

    print("Keys:")
    for product in prices:
        print(" ", product)

    print("Values:")
    for price in prices.values():
        print(" ", price)

    print("Key/value pairs:")
    for product, price in prices.items():
        print(f"  {product}: {price}")

    # Dictionary comprehensions create maps concisely.
    discounted_prices = {
        product: round(price * 0.90, 2)
        for product, price in prices.items()
    }
    print("Discounted:", discounted_prices)


# ============================================================================
# 4. HASHABLE AND UNHASHABLE OBJECTS
# ============================================================================

def demonstrate_hashability() -> None:
    section("4. Hashability")

    # Immutable values such as integers, strings, and tuples containing
    # hashable values can normally be dictionary keys or set members.
    valid_keys: dict[Any, str] = {
        42: "integer",
        "python": "string",
        (10, 20): "tuple",
    }

    print("Valid keys:", valid_keys)

    # Lists and dictionaries are mutable and therefore unhashable.
    for invalid_key in ([1, 2, 3], {"a": 1}):
        try:
            hash(invalid_key)
        except TypeError as exc:
            print(f"{type(invalid_key).__name__} is unhashable:", exc)

    # A tuple is hashable only when all of its elements are hashable.
    mixed_tuple = (1, "two", (3, 4))
    print("Hashable tuple:", hash(mixed_tuple))

    try:
        hash((1, [2, 3]))
    except TypeError as exc:
        print("Tuple containing list is unhashable:", exc)


# ============================================================================
# 5. FREQUENCY COUNTING
# ============================================================================

def frequency_count_manual(items: Iterable[Any]) -> dict[Any, int]:
    counts: dict[Any, int] = {}

    for item in items:
        counts[item] = counts.get(item, 0) + 1

    return counts


def frequency_count_defaultdict(items: Iterable[Any]) -> dict[Any, int]:
    counts: defaultdict[Any, int] = defaultdict(int)

    for item in items:
        counts[item] += 1

    return dict(counts)


def frequency_count_counter(items: Iterable[Any]) -> Counter:
    return Counter(items)


def demonstrate_frequency_counting() -> None:
    section("5. Frequency Counting")

    words = [
        "python",
        "hash",
        "map",
        "python",
        "set",
        "hash",
        "python",
    ]

    print("Manual:", frequency_count_manual(words))
    print("defaultdict:", frequency_count_defaultdict(words))
    print("Counter:", frequency_count_counter(words))

    counts = Counter(words)

    print("Most common:", counts.most_common(3))
    print("Python count:", counts["python"])

    # Counter also supports arithmetic-style operations.
    first = Counter("aabbc")
    second = Counter("abccd")

    print("Counter addition:", first + second)
    print("Counter intersection:", first & second)
    print("Counter union:", first | second)


# ============================================================================
# 6. DUPLICATE DETECTION
# ============================================================================

def contains_duplicate(items: Iterable[Any]) -> bool:
    seen: set[Any] = set()

    for item in items:
        if item in seen:
            return True
        seen.add(item)

    return False


def duplicate_values(items: Iterable[Any]) -> set[Any]:
    seen: set[Any] = set()
    duplicates: set[Any] = set()

    for item in items:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)

    return duplicates


def demonstrate_duplicate_detection() -> None:
    section("6. Duplicate Detection")

    unique_values = [10, 20, 30, 40]
    repeated_values = [10, 20, 30, 20, 40, 10]

    print(
        "Unique input contains duplicate:",
        contains_duplicate(unique_values),
    )
    print(
        "Repeated input contains duplicate:",
        contains_duplicate(repeated_values),
    )
    print("Duplicate values:", duplicate_values(repeated_values))

    # Using len(set(...)) is concise when all elements are hashable.
    print(
        "Set-size duplicate test:",
        len(repeated_values) != len(set(repeated_values)),
    )


# ============================================================================
# 7. HASH SET FUNDAMENTALS
# ============================================================================

def demonstrate_set_operations() -> None:
    section("7. Hash Set Operations")

    engineers = {"Python", "C++", "SQL", "Git"}
    analysts = {"Python", "SQL", "Excel", "Power BI"}

    print("Engineers:", engineers)
    print("Analysts:", analysts)

    # Union: elements in either set.
    print("Union:", engineers | analysts)

    # Intersection: elements in both.
    print("Intersection:", engineers & analysts)

    # Difference: elements in the left set but not the right.
    print("Engineers only:", engineers - analysts)
    print("Analysts only:", analysts - engineers)

    # Symmetric difference: elements belonging to exactly one set.
    print("Symmetric difference:", engineers ^ analysts)

    print("Engineers subset of union:", engineers <= (engineers | analysts))
    print("Intersection subset of engineers:", (engineers & analysts) <= engineers)

    # Set methods provide the same operations without operators.
    print("Union method:", engineers.union(analysts))
    print("Intersection method:", engineers.intersection(analysts))

    # Mutation.
    skills = {"Python", "SQL"}
    skills.add("C++")
    skills.discard("Java")  # discard does not raise if absent.

    try:
        skills.remove("Java")
    except KeyError:
        print("remove() raises KeyError for a missing element.")

    print("Mutated set:", skills)


# ============================================================================
# 8. ORDERING BEHAVIOR
# ============================================================================

def demonstrate_ordering() -> None:
    section("8. Ordering and Hash-Based Collections")

    data = {"b", "a", "c", "d"}

    # Sets do not promise list-like positional ordering.
    print("Set:", data)

    # dict preserves insertion order in modern Python.
    ordered_map = {}
    ordered_map["first"] = 1
    ordered_map["second"] = 2
    ordered_map["third"] = 3

    print("Dictionary insertion order:", list(ordered_map))

    # Relying on a set's displayed order is incorrect.
    # If deterministic output is required, sort explicitly.
    print("Sorted set:", sorted(data))


# ============================================================================
# 9. GROUPING DATA WITH A HASH MAP
# ============================================================================

def group_transactions_by_customer(
    transactions: list[tuple[str, float]],
) -> dict[str, list[float]]:
    groups: defaultdict[str, list[float]] = defaultdict(list)

    for customer, amount in transactions:
        groups[customer].append(amount)

    return dict(groups)


def demonstrate_grouping() -> None:
    section("9. Grouping Records with a Hash Map")

    transactions = [
        ("C001", 1200.0),
        ("C002", 800.0),
        ("C001", 450.0),
        ("C003", 2100.0),
        ("C002", 300.0),
    ]

    groups = group_transactions_by_customer(transactions)

    for customer, amounts in groups.items():
        print(customer, "->", amounts, "total =", sum(amounts))


# ============================================================================
# 10. TWO-SUM PATTERN
# ============================================================================

def two_sum(numbers: list[int], target: int) -> Optional[tuple[int, int]]:
    """
    Return indices of two numbers whose sum equals target.

    Time: O(n) average.
    Space: O(n).

    A brute-force nested-loop solution takes O(n^2).
    The hash map lets us ask whether the required complement was seen before.
    """
    seen: dict[int, int] = {}

    for index, number in enumerate(numbers):
        complement = target - number

        if complement in seen:
            return seen[complement], index

        seen[number] = index

    return None


def demonstrate_two_sum() -> None:
    section("10. Two-Sum Hash Map Pattern")

    numbers = [2, 7, 11, 15]
    target = 9

    result = two_sum(numbers, target)

    print("Numbers:", numbers)
    print("Target:", target)
    print("Indices:", result)

    if result is not None:
        first, second = result
        print("Values:", numbers[first], numbers[second])


# ============================================================================
# 11. FIRST NON-REPEATING CHARACTER
# ============================================================================

def first_non_repeating_character(text: str) -> Optional[str]:
    counts = Counter(text)

    for character in text:
        if counts[character] == 1:
            return character

    return None


def demonstrate_first_non_repeating() -> None:
    section("11. First Non-Repeating Character")

    samples = ["swiss", "aabbcc", "python"]

    for sample in samples:
        print(sample, "->", first_non_repeating_character(sample))


# ============================================================================
# 12. ANAGRAM DETECTION
# ============================================================================

def are_anagrams(first: str, second: str) -> bool:
    return Counter(first) == Counter(second)


def demonstrate_anagrams() -> None:
    section("12. Anagram Detection")

    pairs = [
        ("listen", "silent"),
        ("triangle", "integral"),
        ("hello", "world"),
    ]

    for first, second in pairs:
        print(first, second, "->", are_anagrams(first, second))


# ============================================================================
# 13. SET-BASED DATA CLEANING
# ============================================================================

def normalize_emails(emails: Iterable[str]) -> set[str]:
    """
    Normalize email strings and remove duplicates.

    This is useful for data-cleaning pipelines, but real systems may require
    domain-specific rules before deciding whether two addresses are equivalent.
    """
    return {
        email.strip().lower()
        for email in emails
        if email.strip()
    }


def demonstrate_data_cleaning() -> None:
    section("13. Set-Based Data Cleaning")

    raw_emails = [
        " ATUL@example.com ",
        "atul@example.com",
        "ADMIN@example.com",
        "",
        "admin@example.com",
    ]

    print("Normalized unique emails:", normalize_emails(raw_emails))


# ============================================================================
# 14. CUSTOM HASH TABLE WITH SEPARATE CHAINING
# ============================================================================

@dataclass
class KeyValueEntry:
    key: Any
    value: Any


class ChainedHashMap:
    """
    Educational hash-map implementation using separate chaining.

    Separate chaining stores a bucket containing zero or more key/value pairs.
    If two keys map to the same bucket, both can coexist in that bucket.

    This implementation deliberately exposes internal mechanics that Python's
    built-in dict hides.
    """

    def __init__(self, capacity: int = 8) -> None:
        if capacity < 1:
            raise ValueError("Capacity must be positive.")

        self._buckets: list[list[KeyValueEntry]] = [
            [] for _ in range(capacity)
        ]
        self._size = 0

    @property
    def size(self) -> int:
        return self._size

    @property
    def capacity(self) -> int:
        return len(self._buckets)

    @property
    def load_factor(self) -> float:
        return self._size / self.capacity

    def _index(self, key: Any) -> int:
        return hash(key) % self.capacity

    def _find_entry(self, key: Any) -> Optional[KeyValueEntry]:
        bucket = self._buckets[self._index(key)]

        for entry in bucket:
            if entry.key == key:
                return entry

        return None

    def _resize(self, new_capacity: int) -> None:
        old_entries = [
            entry
            for bucket in self._buckets
            for entry in bucket
        ]

        self._buckets = [[] for _ in range(new_capacity)]

        for entry in old_entries:
            self._buckets[self._index(entry.key)].append(entry)

    def _ensure_capacity(self) -> None:
        # A lower load factor generally reduces collision chains.
        if self.load_factor > 0.75:
            self._resize(self.capacity * 2)

    def set(self, key: Any, value: Any) -> None:
        entry = self._find_entry(key)

        if entry is not None:
            entry.value = value
            return

        bucket = self._buckets[self._index(key)]
        bucket.append(KeyValueEntry(key, value))
        self._size += 1

        self._ensure_capacity()

    def get(self, key: Any, default: Any = None) -> Any:
        entry = self._find_entry(key)
        return default if entry is None else entry.value

    def contains(self, key: Any) -> bool:
        return self._find_entry(key) is not None

    def delete(self, key: Any) -> Any:
        bucket = self._buckets[self._index(key)]

        for position, entry in enumerate(bucket):
            if entry.key == key:
                removed = bucket.pop(position)
                self._size -= 1
                return removed.value

        raise KeyError(key)

    def items(self) -> Iterator[tuple[Any, Any]]:
        for bucket in self._buckets:
            for entry in bucket:
                yield entry.key, entry.value

    def debug_buckets(self) -> list[list[tuple[Any, Any]]]:
        return [
            [(entry.key, entry.value) for entry in bucket]
            for bucket in self._buckets
        ]


def demonstrate_custom_hash_map() -> None:
    section("14. Custom Hash Map with Separate Chaining")

    table = ChainedHashMap(capacity=4)

    for number in range(12):
        table.set(f"key-{number}", number * 10)

    print("Size:", table.size)
    print("Capacity:", table.capacity)
    print("Load factor:", round(table.load_factor, 3))
    print("Lookup key-7:", table.get("key-7"))

    table.set("key-7", 999)
    print("Updated key-7:", table.get("key-7"))

    print("Contains key-100:", table.contains("key-100"))

    removed = table.delete("key-3")
    print("Deleted key-3:", removed)
    print("Contains key-3:", table.contains("key-3"))

    print("Buckets:")
    for index, bucket in enumerate(table.debug_buckets()):
        print(f"  Bucket {index}: {bucket}")


# ============================================================================
# 15. COLLISION CONCEPT
# ============================================================================

class CollisionKey:
    """
    Deliberately forces all objects to have the same hash value.

    Equality remains based on the stored identifier, so different keys collide
    but can still coexist in a correctly implemented hash table.
    """

    def __init__(self, identifier: str) -> None:
        self.identifier = identifier

    def __hash__(self) -> int:
        return 42

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, CollisionKey)
            and self.identifier == other.identifier
        )

    def __repr__(self) -> str:
        return f"CollisionKey({self.identifier!r})"


def demonstrate_collisions() -> None:
    section("15. Hash Collisions")

    table = ChainedHashMap(capacity=4)

    keys = [CollisionKey("A"), CollisionKey("B"), CollisionKey("C")]

    for position, key in enumerate(keys):
        table.set(key, position)

    print("All keys have the same hash:", [hash(key) for key in keys])
    print("Stored entries:", list(table.items()))

    # Correct collision handling still permits distinct keys.
    print("Lookup B:", table.get(CollisionKey("B")))


# ============================================================================
# 16. CUSTOM HASHABLE OBJECTS
# ============================================================================

@dataclass(frozen=True)
class Employee:
    employee_id: int
    name: str
    department: str


def demonstrate_custom_objects() -> None:
    section("16. Custom Hashable Objects")

    employee = Employee(101, "Atul", "Engineering")

    employee_set = {employee}
    employee_map = {employee: {"salary_band": "L4"}}

    print("Employee in set:", employee in employee_set)
    print("Employee metadata:", employee_map[employee])

    # frozen=True makes this dataclass immutable and safely hashable based on
    # its fields, assuming all fields themselves are hashable.


# ============================================================================
# 17. SET ALGEBRA FOR REAL DATA
# ============================================================================

def demonstrate_set_algebra() -> None:
    section("17. Set Algebra for Data Comparison")

    old_permissions = {
        "read",
        "write",
        "export",
        "audit",
    }

    new_permissions = {
        "read",
        "export",
        "delete",
        "audit",
    }

    added = new_permissions - old_permissions
    removed = old_permissions - new_permissions
    unchanged = old_permissions & new_permissions

    print("Added permissions:", added)
    print("Removed permissions:", removed)
    print("Unchanged permissions:", unchanged)


# ============================================================================
# 18. CACHE USING A HASH MAP
# ============================================================================

class SimpleCache:
    """
    Small fixed-capacity cache.

    This is intentionally simple. It demonstrates the hash-map role in
    constant-average-time retrieval. It is not a replacement for a production
    cache with expiration, eviction policy, concurrency controls, and metrics.
    """

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("Cache capacity must be positive.")

        self.capacity = capacity
        self._data: dict[str, Any] = {}

    def get(self, key: str) -> Optional[Any]:
        return self._data.get(key)

    def put(self, key: str, value: Any) -> None:
        if key in self._data:
            self._data[key] = value
            return

        if len(self._data) >= self.capacity:
            # Deterministic simple eviction for demonstration.
            oldest_key = next(iter(self._data))
            del self._data[oldest_key]

        self._data[key] = value

    def __len__(self) -> int:
        return len(self._data)


def demonstrate_cache() -> None:
    section("18. Hash Map as a Simple Cache")

    cache = SimpleCache(capacity=2)

    cache.put("user:101", {"name": "Atul"})
    cache.put("user:102", {"name": "Priya"})

    print("Cached user:", cache.get("user:101"))

    cache.put("user:103", {"name": "Rahul"})

    print("Evicted user:", cache.get("user:101"))
    print("Current cache size:", len(cache))


# ============================================================================
# 19. GRAPH REPRESENTATION WITH A HASH MAP
# ============================================================================

def build_graph(edges: Iterable[tuple[str, str]]) -> dict[str, set[str]]:
    graph: defaultdict[str, set[str]] = defaultdict(set)

    for source, destination in edges:
        graph[source].add(destination)
        graph[destination]  # Ensure destination appears even with no outgoing edge.

    return dict(graph)


def demonstrate_graph() -> None:
    section("19. Graph Representation")

    edges = [
        ("A", "B"),
        ("A", "C"),
        ("B", "D"),
        ("C", "D"),
    ]

    graph = build_graph(edges)

    for node, neighbors in graph.items():
        print(node, "->", neighbors)


# ============================================================================
# 20. TWO-SUM MULTIPLE RESULTS
# ============================================================================

def all_two_sum_pairs(numbers: list[int], target: int) -> list[tuple[int, int]]:
    """
    Find all unique index pairs whose values sum to target.

    The set prevents duplicate index pairs from being emitted.
    """
    seen: dict[int, list[int]] = defaultdict(list)
    results: list[tuple[int, int]] = []

    for index, number in enumerate(numbers):
        complement = target - number

        for previous_index in seen.get(complement, []):
            results.append((previous_index, index))

        seen[number].append(index)

    return results


def demonstrate_all_two_sum_pairs() -> None:
    section("20. Multiple Two-Sum Results")

    numbers = [2, 7, 2, 7, 4]
    print("Numbers:", numbers)
    print("Target 9:", all_two_sum_pairs(numbers, 9))


# ============================================================================
# 21. EDGE CASES
# ============================================================================

def demonstrate_edge_cases() -> None:
    section("21. Edge Cases")

    empty_map: dict[str, int] = {}
    empty_set: set[str] = set()

    print("Empty map:", empty_map)
    print("Empty set:", empty_set)

    print("Missing get:", empty_map.get("missing"))

    try:
        _ = empty_map["missing"]
    except KeyError as exc:
        print("Direct missing lookup raises:", exc)

    # None is hashable and can be a key.
    special_map = {None: "null-like key", 0: "zero", False: "false"}

    # Important subtlety:
    # 0 == False and hash(0) == hash(False), so they refer to the same key.
    print("Special map:", special_map)
    print("Number of entries:", len(special_map))


# ============================================================================
# 22. SECURITY AND HASHING CONSIDERATIONS
# ============================================================================

def demonstrate_hash_security_concepts() -> None:
    section("22. Hashing and Security Considerations")

    # Python's hash for strings is intentionally randomized between interpreter
    # processes in normal configurations. Therefore, never persist Python's
    # built-in hash(string) as a stable identifier.
    value = "security-example"

    print("Current-process string hash:", hash(value))
    print("Stable equality:", value == "security-example")

    # Hash tables should not be confused with cryptographic hashes.
    #
    # A dictionary hash is designed for efficient table placement.
    # Cryptographic hashes are designed for security properties such as
    # preimage resistance and collision resistance.
    #
    # Passwords should never be stored as ordinary dictionary hashes.


# ============================================================================
# 23. PERFORMANCE COMPARISON
# ============================================================================

def membership_timing(size: int = 100_000) -> None:
    section("23. Membership Performance Demonstration")

    values = list(range(size))
    value_set = set(values)

    target = size - 1

    start = perf_counter()
    target in values
    list_elapsed = perf_counter() - start

    start = perf_counter()
    target in value_set
    set_elapsed = perf_counter() - start

    print(f"List membership time: {list_elapsed:.8f} seconds")
    print(f"Set membership time:  {set_elapsed:.8f} seconds")

    # Exact timing depends on hardware, interpreter, workload, and cache state.
    # The important algorithmic distinction is O(n) versus average-case O(1).


# ============================================================================
# 24. VALIDATION WITH HASH SETS
# ============================================================================

def validate_unique_ids(ids: Iterable[str]) -> tuple[bool, set[str]]:
    seen: set[str] = set()
    duplicates: set[str] = set()

    for identifier in ids:
        if not identifier:
            raise ValueError("Identifiers must not be empty.")

        if identifier in seen:
            duplicates.add(identifier)

        seen.add(identifier)

    return not duplicates, duplicates


def demonstrate_validation() -> None:
    section("24. Validation with Sets")

    identifiers = ["A100", "A101", "A102", "A101", "A103"]

    is_valid, duplicates = validate_unique_ids(identifiers)

    print("Unique:", is_valid)
    print("Duplicates:", duplicates)

    try:
        validate_unique_ids(["A100", ""])
    except ValueError as exc:
        print("Validation error:", exc)


# ============================================================================
# 25. MINI INVENTORY SYSTEM
# ============================================================================

class Inventory:
    """Simple inventory using a dictionary keyed by product identifier."""

    def __init__(self) -> None:
        self._stock: dict[str, int] = {}

    def add_product(self, product_id: str, quantity: int) -> None:
        if not product_id:
            raise ValueError("Product ID cannot be empty.")
        if quantity < 0:
            raise ValueError("Quantity cannot be negative.")

        self._stock[product_id] = self._stock.get(product_id, 0) + quantity

    def remove_product(self, product_id: str, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Removal quantity must be positive.")

        current = self._stock.get(product_id)

        if current is None:
            raise KeyError(f"Unknown product: {product_id}")

        if quantity > current:
            raise ValueError("Insufficient stock.")

        remaining = current - quantity

        if remaining == 0:
            del self._stock[product_id]
        else:
            self._stock[product_id] = remaining

    def quantity(self, product_id: str) -> int:
        return self._stock.get(product_id, 0)

    def contains(self, product_id: str) -> bool:
        return product_id in self._stock

    def snapshot(self) -> dict[str, int]:
        return dict(self._stock)


def demonstrate_inventory() -> None:
    section("25. Hash Map Inventory Case")

    inventory = Inventory()

    inventory.add_product("LAPTOP", 10)
    inventory.add_product("MOUSE", 25)
    inventory.add_product("LAPTOP", 5)

    print("Inventory:", inventory.snapshot())
    print("Laptop quantity:", inventory.quantity("LAPTOP"))

    inventory.remove_product("MOUSE", 5)
    print("After removal:", inventory.snapshot())

    try:
        inventory.remove_product("MOUSE", 100)
    except ValueError as exc:
        print("Inventory error:", exc)


# ============================================================================
# 26. TESTS
# ============================================================================

def run_tests() -> None:
    section("26. Self-Tests")

    assert frequency_count_manual("banana") == {
        "b": 1,
        "a": 3,
        "n": 2,
    }

    assert contains_duplicate([1, 2, 3, 1])
    assert not contains_duplicate([1, 2, 3])

    assert duplicate_values([1, 1, 2, 3, 3]) == {1, 3}

    assert are_anagrams("listen", "silent")
    assert not are_anagrams("listen", "python")

    assert two_sum([2, 7, 11, 15], 9) == (0, 1)
    assert two_sum([1, 2, 3], 100) is None

    custom = ChainedHashMap(capacity=2)
    custom.set("a", 1)
    custom.set("b", 2)
    custom.set("a", 10)

    assert custom.get("a") == 10
    assert custom.get("missing") is None
    assert custom.contains("b")
    assert custom.delete("b") == 2
    assert not custom.contains("b")

    inventory = Inventory()
    inventory.add_product("A", 5)
    inventory.remove_product("A", 5)
    assert not inventory.contains("A")

    print("All tests passed.")


# ============================================================================
# 27. COMPLEXITY REFERENCE
# ============================================================================

def print_complexity_reference() -> None:
    section("27. Complexity Reference")

    rows = [
        ("dict lookup", "Average O(1)", "Worst O(n)"),
        ("dict insertion", "Average O(1)", "Worst O(n)"),
        ("dict deletion", "Average O(1)", "Worst O(n)"),
        ("set lookup", "Average O(1)", "Worst O(n)"),
        ("set insertion", "Average O(1)", "Worst O(n)"),
        ("set deletion", "Average O(1)", "Worst O(n)"),
        ("list membership", "O(n)", "O(n)"),
        ("set union", "O(n + m)", "Depends on implementation details"),
        ("set intersection", "O(min(n, m)) typical", "Depends on implementation"),
    ]

    for operation, average, worst in rows:
        print(f"{operation:24} | {average:28} | {worst}")


# ============================================================================
# 28. PRACTICAL DESIGN GUIDELINES
# ============================================================================

def print_design_guidelines() -> None:
    section("28. Practical Design Guidelines")

    guidelines = [
        "Use dict when you need key -> value associations.",
        "Use set when you only need unique membership.",
        "Use Counter for frequency counting.",
        "Use defaultdict when missing keys have natural default values.",
        "Use immutable, meaningfully comparable keys.",
        "Do not assume set ordering.",
        "Do not persist Python's built-in hash values as stable identifiers.",
        "Remember that average O(1) is not guaranteed worst-case O(1).",
        "Monitor memory usage when replacing lists with large hash tables.",
        "Validate external input before using it as application keys.",
        "Use cryptographic hash functions when cryptographic properties are required.",
        "Do not store passwords using ordinary hash-table hashing.",
    ]

    for number, guideline in enumerate(guidelines, start=1):
        print(f"{number:2}. {guideline}")


# ============================================================================
# 29. MAIN
# ============================================================================

def main() -> None:
    print("HASH MAPS AND HASH SETS")
    print("Executable study guide: fundamentals through advanced concepts.")

    demonstrate_dictionary_basics()
    demonstrate_dictionary_iteration()
    demonstrate_hashability()
    demonstrate_frequency_counting()
    demonstrate_duplicate_detection()
    demonstrate_set_operations()
    demonstrate_ordering()
    demonstrate_grouping()
    demonstrate_two_sum()
    demonstrate_first_non_repeating()
    demonstrate_anagrams()
    demonstrate_data_cleaning()
    demonstrate_custom_hash_map()
    demonstrate_collisions()
    demonstrate_custom_objects()
    demonstrate_set_algebra()
    demonstrate_cache()
    demonstrate_graph()
    demonstrate_all_two_sum_pairs()
    demonstrate_edge_cases()
    demonstrate_hash_security_concepts()
    membership_timing()
    demonstrate_validation()
    demonstrate_inventory()
    run_tests()
    print_complexity_reference()
    print_design_guidelines()


if __name__ == "__main__":
    main()
