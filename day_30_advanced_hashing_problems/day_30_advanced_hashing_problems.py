"""
Advanced Hashing Problems
=========================

A self-contained progression from fundamental hash-map/set usage to advanced
hashing patterns:

- Prefix-sum hashing
- Longest subarray problems
- Frequency-based problems
- Grouping and canonicalization
- Pair-sum problems
- Subarray counting
- Zero-sum and target-sum techniques
- Collision-aware implementation decisions
- Complexity and edge-case analysis

Run:
    python advanced_hashing.py
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Iterable


# ---------------------------------------------------------------------------
# Fundamental hashing helpers
# ---------------------------------------------------------------------------

def frequency_map(values: Iterable[int]) -> dict[int, int]:
    """Count occurrences using a dictionary."""
    counts: dict[int, int] = {}

    for value in values:
        counts[value] = counts.get(value, 0) + 1

    return counts


def unique_values(values: Iterable[int]) -> set[int]:
    """Return the distinct values using a hash set."""
    return set(values)


def contains_duplicate(values: Iterable[int]) -> bool:
    """Detect duplicates in O(n) expected time."""
    seen: set[int] = set()

    for value in values:
        if value in seen:
            return True
        seen.add(value)

    return False


# ---------------------------------------------------------------------------
# Pair-sum hashing
# ---------------------------------------------------------------------------

def two_sum_indices(values: list[int], target: int) -> tuple[int, int] | None:
    """
    Find two different positions whose values sum to target.

    The dictionary stores a previously observed value and its index.
    Checking the complement before inserting the current value prevents
    an element from being paired with itself.
    """
    seen: dict[int, int] = {}

    for index, value in enumerate(values):
        complement = target - value

        if complement in seen:
            return seen[complement], index

        seen[value] = index

    return None


def all_unique_pair_values(values: list[int], target: int) -> list[tuple[int, int]]:
    """
    Return every distinct value pair that sums to target.

    A normalized pair is stored in a set so repeated occurrences do not
    create duplicate value-pairs.
    """
    seen: set[int] = set()
    pairs: set[tuple[int, int]] = set()

    for value in values:
        complement = target - value

        if complement in seen:
            pairs.add(tuple(sorted((value, complement))))

        seen.add(value)

    return sorted(pairs)


def count_pairs_with_sum(values: list[int], target: int) -> int:
    """
    Count index-pairs (i, j), i < j, whose values sum to target.

    Unlike two_sum_indices, duplicate values contribute multiple pairs.
    """
    frequencies: dict[int, int] = {}
    answer = 0

    for value in values:
        complement = target - value
        answer += frequencies.get(complement, 0)
        frequencies[value] = frequencies.get(value, 0) + 1

    return answer


def count_pairs_with_sum_counter(values: list[int], target: int) -> int:
    """Equivalent pair counting using Counter for comparison."""
    counts = Counter(values)
    answer = 0

    for value, count in counts.items():
        complement = target - value

        if complement not in counts:
            continue

        if value < complement:
            answer += count * counts[complement]
        elif value == complement:
            answer += count * (count - 1) // 2

    return answer


# ---------------------------------------------------------------------------
# Prefix-sum hashing
# ---------------------------------------------------------------------------

def prefix_sums(values: list[int]) -> list[int]:
    """
    Produce prefix sums including the empty-prefix value.

    For values [a, b, c], the result is [0, a, a+b, a+b+c].
    """
    result = [0]
    running = 0

    for value in values:
        running += value
        result.append(running)

    return result


def has_subarray_sum(values: list[int], target: int) -> bool:
    """
    Determine whether a contiguous subarray has the requested sum.

    If prefix[j] - prefix[i] == target, then the interval (i, j]
    has target sum. The set stores prefix sums already encountered.
    """
    seen_prefixes = {0}
    running = 0

    for value in values:
        running += value

        if running - target in seen_prefixes:
            return True

        seen_prefixes.add(running)

    return False


def count_subarrays_with_sum(values: list[int], target: int) -> int:
    """
    Count all contiguous subarrays whose sum equals target.

    The frequency map is necessary because the same prefix sum can occur
    multiple times, and every earlier occurrence forms a valid interval.
    """
    prefix_frequency: dict[int, int] = {0: 1}
    running = 0
    answer = 0

    for value in values:
        running += value
        answer += prefix_frequency.get(running - target, 0)
        prefix_frequency[running] = prefix_frequency.get(running, 0) + 1

    return answer


def longest_subarray_with_sum(values: list[int], target: int) -> tuple[int, int, int] | None:
    """
    Find the longest contiguous subarray with a target sum.

    The earliest index for each prefix sum is retained. An earlier
    occurrence always produces a longer candidate when the same
    prefix difference is later encountered.

    Returns:
        (length, left_index, right_index), or None.
    """
    first_index: dict[int, int] = {0: -1}
    running = 0
    best: tuple[int, int, int] | None = None

    for index, value in enumerate(values):
        running += value

        required = running - target

        if required in first_index:
            left_boundary = first_index[required]
            length = index - left_boundary

            if best is None or length > best[0]:
                best = (length, left_boundary + 1, index)

        if running not in first_index:
            first_index[running] = index

    return best


def longest_zero_sum_subarray(values: list[int]) -> tuple[int, int, int] | None:
    """Specialized form of longest_subarray_with_sum for target zero."""
    return longest_subarray_with_sum(values, 0)


# ---------------------------------------------------------------------------
# Prefix transformation: equal binary counts
# ---------------------------------------------------------------------------

def longest_equal_zero_one_subarray(binary_values: list[int]) -> tuple[int, int, int] | None:
    """
    Find the longest binary subarray containing equal numbers of 0 and 1.

    Treat 0 as -1 and 1 as +1. Equal counts produce a transformed sum of
    zero, reducing the problem to repeated prefix sums.
    """
    first_index = {0: -1}
    balance = 0
    best: tuple[int, int, int] | None = None

    for index, value in enumerate(binary_values):
        if value == 0:
            balance -= 1
        elif value == 1:
            balance += 1
        else:
            raise ValueError("Binary input may contain only 0 and 1.")

        if balance in first_index:
            length = index - first_index[balance]

            if best is None or length > best[0]:
                best = (length, first_index[balance] + 1, index)
        else:
            first_index[balance] = index

    return best


# ---------------------------------------------------------------------------
# Divisibility and modular prefix hashing
# ---------------------------------------------------------------------------

def has_subarray_sum_divisible_by(values: list[int], divisor: int) -> bool:
    """
    Determine whether a subarray of length at least two has sum divisible
    by divisor.

    Equal prefix remainders indicate a sum divisible by divisor.
    """
    if divisor == 0:
        raise ValueError("Divisor cannot be zero.")

    first_index: dict[int, int] = {0: -1}
    running = 0

    for index, value in enumerate(values):
        running += value
        remainder = running % divisor

        if remainder in first_index:
            if index - first_index[remainder] >= 2:
                return True
        else:
            first_index[remainder] = index

    return False


def count_subarrays_divisible_by(values: list[int], divisor: int) -> int:
    """Count contiguous subarrays whose sum is divisible by divisor."""
    if divisor == 0:
        raise ValueError("Divisor cannot be zero.")

    remainder_frequency: dict[int, int] = {0: 1}
    running = 0
    answer = 0

    for value in values:
        running += value
        remainder = running % divisor

        answer += remainder_frequency.get(remainder, 0)
        remainder_frequency[remainder] = remainder_frequency.get(remainder, 0) + 1

    return answer


# ---------------------------------------------------------------------------
# Frequency-based problems
# ---------------------------------------------------------------------------

def top_k_frequent(values: list[int], k: int) -> list[int]:
    """
    Return up to k values with the highest frequency.

    Counter.most_common uses a frequency map and performs the ordering
    required for the final result.
    """
    if k < 0:
        raise ValueError("k must be non-negative")

    return [value for value, _ in Counter(values).most_common(k)]


def first_unique_value(values: list[int]) -> int | None:
    """
    Return the first value occurring exactly once.

    Counting is separated from the final scan so original ordering is
    preserved while frequency lookup remains O(1) expected time.
    """
    counts = Counter(values)

    for value in values:
        if counts[value] == 1:
            return value

    return None


def majority_element(values: list[int]) -> int | None:
    """
    Find a value appearing more than n/2 times.

    The hash-map implementation is intentionally explicit because it
    demonstrates frequency accumulation rather than relying on sorting.
    """
    if not values:
        return None

    counts = Counter(values)
    threshold = len(values) // 2

    for value, count in counts.items():
        if count > threshold:
            return value

    return None


def group_values_by_frequency(values: list[int]) -> dict[int, list[int]]:
    """Group distinct values according to their occurrence frequency."""
    counts = Counter(values)
    groups: dict[int, list[int]] = defaultdict(list)

    for value, count in counts.items():
        groups[count].append(value)

    for group in groups.values():
        group.sort()

    return dict(sorted(groups.items()))


# ---------------------------------------------------------------------------
# Grouping and canonicalization
# ---------------------------------------------------------------------------

def group_anagrams(words: list[str]) -> list[list[str]]:
    """
    Group words that contain the same character frequencies.

    A 26-element frequency tuple is used as a hashable canonical key.
    This avoids sorting every word and is especially useful when word
    lengths are large but the alphabet is fixed.
    """
    groups: dict[tuple[int, ...], list[str]] = defaultdict(list)

    for word in words:
        frequency = [0] * 26

        for character in word.lower():
            if "a" <= character <= "z":
                frequency[ord(character) - ord("a")] += 1
            else:
                raise ValueError(
                    "group_anagrams accepts alphabetic ASCII letters only."
                )

        groups[tuple(frequency)].append(word)

    return list(groups.values())


def group_shifted_strings(words: list[str]) -> list[list[str]]:
    """
    Group lowercase strings having the same cyclic shift pattern.

    The first character is normalized to zero. For example, abc and bcd
    receive the same difference signature.
    """
    groups: dict[tuple[int, ...], list[str]] = defaultdict(list)

    for word in words:
        if not word:
            key = ()
        else:
            if any(not ("a" <= c <= "z") for c in word):
                raise ValueError("Expected lowercase ASCII words.")

            key = tuple(
                (ord(word[i]) - ord(word[i - 1])) % 26
                for i in range(1, len(word))
            )

        groups[key].append(word)

    return list(groups.values())


def canonical_pair(value_a: str, value_b: str) -> tuple[str, str]:
    """Normalize an unordered pair so it has one deterministic representation."""
    return tuple(sorted((value_a, value_b)))


# ---------------------------------------------------------------------------
# Advanced subarray transformations
# ---------------------------------------------------------------------------

def longest_subarray_equal_to_k_distinct_categories(
    values: list[str],
    category_a: str,
    category_b: str,
) -> tuple[int, int, int] | None:
    """
    Find the longest interval containing equal counts of two categories.

    category_a contributes +1 and category_b contributes -1. Other values
    are rejected because silently ignoring unrelated categories can hide
    malformed input in a production data pipeline.
    """
    first_index = {0: -1}
    balance = 0
    best = None

    for index, value in enumerate(values):
        if value == category_a:
            balance += 1
        elif value == category_b:
            balance -= 1
        else:
            raise ValueError("Unexpected category in input.")

        if balance in first_index:
            length = index - first_index[balance]

            if best is None or length > best[0]:
                best = (length, first_index[balance] + 1, index)
        else:
            first_index[balance] = index

    return best


def count_subarrays_with_equal_zero_one(values: list[int]) -> int:
    """Count all binary subarrays containing equal numbers of zeroes and ones."""
    frequency = {0: 1}
    balance = 0
    answer = 0

    for value in values:
        if value == 0:
            balance -= 1
        elif value == 1:
            balance += 1
        else:
            raise ValueError("Input must contain only 0 and 1.")

        answer += frequency.get(balance, 0)
        frequency[balance] = frequency.get(balance, 0) + 1

    return answer


# ---------------------------------------------------------------------------
# A reusable hash-based analytics engine
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SubarrayResult:
    length: int
    start: int
    end: int
    total: int


class PrefixHashAnalyzer:
    """
    Reusable analyzer for integer sequences.

    The object keeps immutable input and exposes several related queries.
    Prefix calculations are computed once, making repeated target queries
    cheap when the workload justifies retaining the prefix array.
    """

    def __init__(self, values: Iterable[int]):
        self.values = tuple(values)
        self.prefix = tuple(prefix_sums(list(self.values)))

    def longest_for_sum(self, target: int) -> SubarrayResult | None:
        first_index: dict[int, int] = {0: -1}
        best: SubarrayResult | None = None

        for index, value in enumerate(self.values):
            running = self.prefix[index + 1]
            required = running - target

            if required in first_index:
                boundary = first_index[required]
                length = index - boundary

                candidate = SubarrayResult(
                    length=length,
                    start=boundary + 1,
                    end=index,
                    total=target,
                )

                if best is None or candidate.length > best.length:
                    best = candidate

            if running not in first_index:
                first_index[running] = index

        return best

    def count_for_sum(self, target: int) -> int:
        frequency: dict[int, int] = {0: 1}
        answer = 0

        for running in self.prefix[1:]:
            answer += frequency.get(running - target, 0)
            frequency[running] = frequency.get(running, 0) + 1

        return answer


# ---------------------------------------------------------------------------
# Validation and demonstration
# ---------------------------------------------------------------------------

def demonstrate_edge_cases() -> None:
    """Exercise cases that commonly expose hashing mistakes."""
    cases = [
        ([], 0),
        ([5], 5),
        ([0, 0, 0], 0),
        ([1, -1, 1, -1], 0),
        ([3, -2, 2, -3, 3], 0),
    ]

    print("\nEdge cases")

    for values, target in cases:
        print(
            f"values={values!r}, target={target}: "
            f"longest={longest_subarray_with_sum(values, target)}, "
            f"count={count_subarrays_with_sum(values, target)}"
        )


def run_demo() -> None:
    print("Advanced Hashing Problems")
    print("=" * 30)

    numbers = [4, 7, 1, 9, 7, 4, 7]

    print("\nFrequency and uniqueness")
    print("frequency:", frequency_map(numbers))
    print("unique:", sorted(unique_values(numbers)))
    print("duplicate:", contains_duplicate(numbers))
    print("first unique:", first_unique_value(numbers))
    print("top two:", top_k_frequent(numbers, 2))
    print("frequency groups:", group_values_by_frequency(numbers))

    print("\nPair-sum hashing")
    pair_values = [2, 7, 11, 15, 7, 3]
    print("two sum:", two_sum_indices(pair_values, 9))
    print("unique value pairs:", all_unique_pair_values(pair_values, 10))
    print("number of index pairs:", count_pairs_with_sum(pair_values, 14))

    print("\nPrefix-sum hashing")
    values = [3, 4, -7, 2, 2, -2, 5, -5]
    print("prefix sums:", prefix_sums(values))
    print("has sum 0:", has_subarray_sum(values, 0))
    print("count with sum 0:", count_subarrays_with_sum(values, 0))
    print("longest with sum 0:", longest_subarray_with_sum(values, 0))
    print("longest with sum 5:", longest_subarray_with_sum(values, 5))

    print("\nBinary transformation")
    binary = [0, 0, 1, 0, 0, 0, 1, 1]
    print("longest equal zero/one:", longest_equal_zero_one_subarray(binary))
    print("count equal zero/one:", count_subarrays_with_equal_zero_one(binary))

    print("\nModular prefix hashing")
    divisible_values = [23, 2, 4, 6, 7]
    print(
        "has length>=2 subarray divisible by 6:",
        has_subarray_sum_divisible_by(divisible_values, 6),
    )
    print(
        "count divisible by 6:",
        count_subarrays_divisible_by(divisible_values, 6),
    )

    print("\nGrouping")
    words = ["eat", "tea", "tan", "ate", "nat", "bat"]
    print("anagrams:", group_anagrams(words))

    shifted = ["abc", "bcd", "acef", "xyz", "az", "ba", "a", "z"]
    print("shifted groups:", group_shifted_strings(shifted))

    print("\nReusable analyzer")
    analyzer = PrefixHashAnalyzer([1, -1, 5, -2, 3, 0, 2])
    print("longest target 3:", analyzer.longest_for_sum(3))
    print("count target 3:", analyzer.count_for_sum(3))

    print("\nCategory balance")
    events = ["success", "failure", "success", "success", "failure", "failure"]
    print(
        "longest balanced interval:",
        longest_subarray_equal_to_k_distinct_categories(
            events, "success", "failure"
        ),
    )

    demonstrate_edge_cases()


if __name__ == "__main__":
    run_demo()
