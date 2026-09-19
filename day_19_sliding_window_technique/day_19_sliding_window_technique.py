"""
Sliding Window Technique
========================

A standalone study program covering fixed-size and variable-size sliding
windows for arrays, strings, subarrays, substrings, optimization problems,
frequency counting, monotonic deques, and practical edge cases.

The program is intentionally executable: run it directly with Python 3.
"""

from collections import Counter, defaultdict, deque
from math import inf
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# 1. Fundamentals
# ---------------------------------------------------------------------------

def explain_basics() -> None:
    print("\n=== SLIDING WINDOW: FUNDAMENTALS ===")
    print("""
A sliding window maintains a contiguous portion of an array or string.

Instead of repeatedly constructing every possible subarray or substring,
we move the window boundaries and update only the information affected by
the elements entering and leaving the window.

A window is commonly represented by:
    left  = start index
    right = end index

For a fixed-size window of length k:
    right moves forward one position at a time.
    left follows right so that the window remains length k.

For a variable-size window:
    right expands the window.
    left contracts the window when a constraint is violated.

Typical complexity changes from O(n*k) or O(n^2) to O(n), provided that each
element enters and leaves the window a bounded number of times.

Sliding windows require CONTIGUOUS data. They are not generally suitable
for arbitrary subsequences where gaps are allowed.
""")


# ---------------------------------------------------------------------------
# 2. Naive versus sliding-window fixed-size maximum sum
# ---------------------------------------------------------------------------

def maximum_sum_naive(numbers: List[int], k: int) -> int:
    """Reference implementation with O(n*k) time."""
    if k <= 0 or k > len(numbers):
        raise ValueError("k must satisfy 1 <= k <= len(numbers)")

    best = -inf
    for start in range(len(numbers) - k + 1):
        current_sum = 0
        for index in range(start, start + k):
            current_sum += numbers[index]
        best = max(best, current_sum)

    return int(best)


def maximum_sum_fixed_window(numbers: List[int], k: int) -> int:
    """
    O(n) fixed-size sliding window.

    Instead of recomputing:
        a[i] + a[i+1] + ... + a[i+k-1]

    after moving one position, subtract the element leaving the window and
    add the element entering it.
    """
    if k <= 0 or k > len(numbers):
        raise ValueError("k must satisfy 1 <= k <= len(numbers)")

    window_sum = sum(numbers[:k])
    best = window_sum

    for right in range(k, len(numbers)):
        left = right - k
        window_sum += numbers[right]
        window_sum -= numbers[left]
        best = max(best, window_sum)

    return best


def minimum_sum_fixed_window(numbers: List[int], k: int) -> int:
    """Find the minimum sum among all contiguous windows of length k."""
    if k <= 0 or k > len(numbers):
        raise ValueError("k must satisfy 1 <= k <= len(numbers)")

    window_sum = sum(numbers[:k])
    best = window_sum

    for right in range(k, len(numbers)):
        window_sum += numbers[right] - numbers[right - k]
        best = min(best, window_sum)

    return best


def average_of_each_window(numbers: List[float], k: int) -> List[float]:
    """Return the average of every fixed-size window."""
    if k <= 0 or k > len(numbers):
        raise ValueError("k must satisfy 1 <= k <= len(numbers)")

    window_sum = sum(numbers[:k])
    averages = [window_sum / k]

    for right in range(k, len(numbers)):
        window_sum += numbers[right] - numbers[right - k]
        averages.append(window_sum / k)

    return averages


# ---------------------------------------------------------------------------
# 3. Fixed-size window extrema using a monotonic deque
# ---------------------------------------------------------------------------

def maximum_in_each_window(numbers: List[int], k: int) -> List[int]:
    """
    Return maximum values for every window of size k.

    The deque stores indices, and values decrease from front to back.
    Therefore the front is always the maximum valid element.

    Each index enters and leaves the deque at most once: O(n) time.
    """
    if k <= 0 or k > len(numbers):
        raise ValueError("k must satisfy 1 <= k <= len(numbers)")

    candidates = deque()
    result = []

    for right, value in enumerate(numbers):
        # Remove indices that have moved outside the current window.
        while candidates and candidates[0] <= right - k:
            candidates.popleft()

        # Any smaller value behind this value can never become the maximum
        # while the current value remains in the window.
        while candidates and numbers[candidates[-1]] <= value:
            candidates.pop()

        candidates.append(right)

        if right >= k - 1:
            result.append(numbers[candidates[0]])

    return result


def minimum_in_each_window(numbers: List[int], k: int) -> List[int]:
    """Monotonic increasing deque for minimum values in each fixed window."""
    if k <= 0 or k > len(numbers):
        raise ValueError("k must satisfy 1 <= k <= len(numbers)")

    candidates = deque()
    result = []

    for right, value in enumerate(numbers):
        while candidates and candidates[0] <= right - k:
            candidates.popleft()

        while candidates and numbers[candidates[-1]] >= value:
            candidates.pop()

        candidates.append(right)

        if right >= k - 1:
            result.append(numbers[candidates[0]])

    return result


# ---------------------------------------------------------------------------
# 4. Variable-size windows: minimum length with target sum
# ---------------------------------------------------------------------------

def minimum_length_subarray_at_least_target(
    numbers: List[int], target: int
) -> int:
    """
    Minimum length contiguous subarray whose sum is >= target.

    IMPORTANT:
    This standard shrinking-window solution requires non-negative numbers.
    With negative numbers, expanding right does not necessarily increase
    the sum, so the monotonic property needed by the technique disappears.
    """
    if target <= 0:
        return 0

    left = 0
    window_sum = 0
    best_length = inf

    for right, value in enumerate(numbers):
        window_sum += value

        while window_sum >= target:
            best_length = min(best_length, right - left + 1)
            window_sum -= numbers[left]
            left += 1

    return 0 if best_length == inf else int(best_length)


def longest_subarray_sum_at_most_k(
    numbers: List[int], k: int
) -> int:
    """
    Longest window whose sum is <= k.

    This implementation assumes all numbers are non-negative.
    """
    left = 0
    window_sum = 0
    best_length = 0

    for right, value in enumerate(numbers):
        window_sum += value

        while window_sum > k and left <= right:
            window_sum -= numbers[left]
            left += 1

        best_length = max(best_length, right - left + 1)

    return best_length


# ---------------------------------------------------------------------------
# 5. Longest substring without repeating characters
# ---------------------------------------------------------------------------

def longest_unique_substring(text: str) -> Tuple[int, str]:
    """
    Find the longest substring containing no repeated character.

    The dictionary records the most recent index of each character.
    If a repeated character is inside the active window, move left directly
    past its previous occurrence.
    """
    left = 0
    best_start = 0
    best_length = 0
    last_seen: Dict[str, int] = {}

    for right, character in enumerate(text):
        if character in last_seen and last_seen[character] >= left:
            left = last_seen[character] + 1

        last_seen[character] = right

        current_length = right - left + 1
        if current_length > best_length:
            best_length = current_length
            best_start = left

    return best_length, text[best_start:best_start + best_length]


# ---------------------------------------------------------------------------
# 6. Longest substring with at most K distinct characters
# ---------------------------------------------------------------------------

def longest_substring_at_most_k_distinct(
    text: str, k: int
) -> Tuple[int, str]:
    """Variable-size frequency-map window."""
    if k <= 0 or not text:
        return 0, ""

    left = 0
    frequencies = defaultdict(int)
    best_start = 0
    best_length = 0

    for right, character in enumerate(text):
        frequencies[character] += 1

        while len(frequencies) > k:
            outgoing = text[left]
            frequencies[outgoing] -= 1
            if frequencies[outgoing] == 0:
                del frequencies[outgoing]
            left += 1

        current_length = right - left + 1
        if current_length > best_length:
            best_length = current_length
            best_start = left

    return best_length, text[best_start:best_start + best_length]


# ---------------------------------------------------------------------------
# 7. Longest substring after replacing at most K characters
# ---------------------------------------------------------------------------

def longest_repeating_character_replacement(
    text: str, k: int
) -> Tuple[int, str]:
    """
    Find the longest substring that can become all one character after
    replacing at most k characters.

    Window validity:
        window_length - highest_frequency <= k

    We do not need to reduce the maximum frequency immediately when the
    left boundary moves. Keeping a historical maximum still produces the
    correct maximum length because the window length only matters as a
    candidate threshold. This is a common subtle optimization.
    """
    if k < 0:
        raise ValueError("k cannot be negative")

    left = 0
    frequencies = Counter()
    highest_frequency = 0
    best_start = 0
    best_length = 0

    for right, character in enumerate(text):
        frequencies[character] += 1
        highest_frequency = max(highest_frequency, frequencies[character])

        while (right - left + 1) - highest_frequency > k:
            frequencies[text[left]] -= 1
            left += 1

        current_length = right - left + 1
        if current_length > best_length:
            best_length = current_length
            best_start = left

    return best_length, text[best_start:best_start + best_length]


# ---------------------------------------------------------------------------
# 8. Minimum window substring
# ---------------------------------------------------------------------------

def minimum_window_substring(text: str, required: str) -> str:
    """
    Find the shortest substring of text containing every character in
    required with at least the required multiplicity.

    Example:
        text = "ADOBECODEBANC"
        required = "ABC"
        answer = "BANC"

    The algorithm is O(n + m) where n=len(text), m=len(required).
    """
    if not text or not required or len(required) > len(text):
        return ""

    required_counts = Counter(required)
    window_counts = Counter()

    required_unique = len(required_counts)
    satisfied_unique = 0
    left = 0

    best_start = 0
    best_length = inf

    for right, character in enumerate(text):
        window_counts[character] += 1

        if (
            character in required_counts
            and window_counts[character] == required_counts[character]
        ):
            satisfied_unique += 1

        while satisfied_unique == required_unique:
            current_length = right - left + 1

            if current_length < best_length:
                best_length = current_length
                best_start = left

            outgoing = text[left]
            window_counts[outgoing] -= 1

            if (
                outgoing in required_counts
                and window_counts[outgoing] < required_counts[outgoing]
            ):
                satisfied_unique -= 1

            left += 1

    return "" if best_length == inf else text[
        best_start:best_start + best_length
    ]


# ---------------------------------------------------------------------------
# 9. Permutation/anagram detection
# ---------------------------------------------------------------------------

def contains_permutation(text: str, pattern: str) -> bool:
    """
    Determine whether text contains a substring that is a permutation
    (anagram) of pattern.

    Every valid window has exactly len(pattern) characters.
    """
    if not pattern:
        return True
    if len(pattern) > len(text):
        return False

    target = Counter(pattern)
    window = Counter()
    left = 0

    for right, character in enumerate(text):
        window[character] += 1

        if right - left + 1 > len(pattern):
            outgoing = text[left]
            window[outgoing] -= 1
            if window[outgoing] == 0:
                del window[outgoing]
            left += 1

        if right - left + 1 == len(pattern) and window == target:
            return True

    return False


def find_all_anagrams(text: str, pattern: str) -> List[int]:
    """Return starting positions of every anagram of pattern."""
    if not pattern or len(pattern) > len(text):
        return []

    target = Counter(pattern)
    window = Counter()
    result = []
    left = 0

    for right, character in enumerate(text):
        window[character] += 1

        if right - left + 1 > len(pattern):
            outgoing = text[left]
            window[outgoing] -= 1
            if window[outgoing] == 0:
                del window[outgoing]
            left += 1

        if right - left + 1 == len(pattern) and window == target:
            result.append(left)

    return result


# ---------------------------------------------------------------------------
# 10. Binary-array longest window after deleting one element
# ---------------------------------------------------------------------------

def longest_ones_after_one_deletion(binary_numbers: List[int]) -> int:
    """
    Longest run of 1s obtainable after deleting exactly one element.

    At most one zero is permitted inside the current window.
    Because one element must be deleted, the answer is window_size - 1.
    """
    left = 0
    zero_count = 0
    best = 0

    for right, value in enumerate(binary_numbers):
        if value not in (0, 1):
            raise ValueError("Input must contain only 0 and 1")

        if value == 0:
            zero_count += 1

        while zero_count > 1:
            if binary_numbers[left] == 0:
                zero_count -= 1
            left += 1

        best = max(best, right - left)

    return best


# ---------------------------------------------------------------------------
# 11. Count subarrays with exactly K distinct values
# ---------------------------------------------------------------------------

def count_subarrays_at_most_k_distinct(
    numbers: List[int], k: int
) -> int:
    """
    Count subarrays containing at most k distinct values.

    For every right boundary, after shrinking, every starting index from
    left through right produces a valid subarray. There are therefore:
        right - left + 1
    valid windows ending at right.
    """
    if k < 0:
        return 0

    left = 0
    frequencies = defaultdict(int)
    result = 0

    for right, value in enumerate(numbers):
        frequencies[value] += 1

        while len(frequencies) > k:
            outgoing = numbers[left]
            frequencies[outgoing] -= 1
            if frequencies[outgoing] == 0:
                del frequencies[outgoing]
            left += 1

        result += right - left + 1

    return result


def count_subarrays_exactly_k_distinct(
    numbers: List[int], k: int
) -> int:
    """
    Exactly K distinct = atMost(K) - atMost(K-1).

    This is an important sliding-window transformation.
    """
    return (
        count_subarrays_at_most_k_distinct(numbers, k)
        - count_subarrays_at_most_k_distinct(numbers, k - 1)
    )


# ---------------------------------------------------------------------------
# 12. Maximum consecutive ones with at most K zero-to-one changes
# ---------------------------------------------------------------------------

def longest_ones_with_k_flips(binary_numbers: List[int], k: int) -> int:
    """Longest binary window containing at most k zeros."""
    if k < 0:
        raise ValueError("k cannot be negative")

    left = 0
    zero_count = 0
    best = 0

    for right, value in enumerate(binary_numbers):
        if value not in (0, 1):
            raise ValueError("Input must contain only 0 and 1")

        if value == 0:
            zero_count += 1

        while zero_count > k:
            if binary_numbers[left] == 0:
                zero_count -= 1
            left += 1

        best = max(best, right - left + 1)

    return best


# ---------------------------------------------------------------------------
# 13. Window with bounded difference
# ---------------------------------------------------------------------------

def longest_subarray_bounded_difference(
    numbers: List[int], limit: int
) -> Tuple[int, List[int]]:
    """
    Longest subarray where max(window) - min(window) <= limit.

    Two monotonic deques maintain the maximum and minimum independently.
    """
    if limit < 0:
        return 0, []

    max_candidates = deque()
    min_candidates = deque()
    left = 0
    best_start = 0
    best_length = 0

    for right, value in enumerate(numbers):
        while max_candidates and numbers[max_candidates[-1]] <= value:
            max_candidates.pop()
        max_candidates.append(right)

        while min_candidates and numbers[min_candidates[-1]] >= value:
            min_candidates.pop()
        min_candidates.append(right)

        while (
            numbers[max_candidates[0]]
            - numbers[min_candidates[0]]
            > limit
        ):
            if max_candidates[0] == left:
                max_candidates.popleft()
            if min_candidates[0] == left:
                min_candidates.popleft()
            left += 1

        current_length = right - left + 1
        if current_length > best_length:
            best_length = current_length
            best_start = left

    return best_length, numbers[
        best_start:best_start + best_length
    ]


# ---------------------------------------------------------------------------
# 14. Weighted/fixed-window example
# ---------------------------------------------------------------------------

def maximum_weighted_window(
    values: List[int], weights: List[int], k: int
) -> int:
    """
    Maximum sum of values[i] * weights[i] over every fixed window.

    This demonstrates that the sliding-window idea applies to a derived
    quantity, not only directly to raw values.
    """
    if len(values) != len(weights):
        raise ValueError("values and weights must have equal lengths")
    if k <= 0 or k > len(values):
        raise ValueError("invalid window size")

    current = sum(
        values[i] * weights[i] for i in range(k)
    )
    best = current

    for right in range(k, len(values)):
        current += values[right] * weights[right]
        outgoing = right - k
        current -= values[outgoing] * weights[outgoing]
        best = max(best, current)

    return best


# ---------------------------------------------------------------------------
# 15. A reusable fixed-window abstraction
# ---------------------------------------------------------------------------

class FixedWindowSum:
    """
    Small reusable object for maintaining a rolling sum.

    The class makes the state of the window explicit:
        values
        k
        left/right boundaries
        current sum
    """

    def __init__(self, values: List[int], k: int) -> None:
        if k <= 0 or k > len(values):
            raise ValueError("invalid window size")
        self.values = values
        self.k = k
        self.left = 0
        self.right = k - 1
        self.current_sum = sum(values[:k])

    def current(self) -> Tuple[int, int, int]:
        return self.left, self.right, self.current_sum

    def slide(self) -> bool:
        """Move one position. Return False when no movement is possible."""
        if self.right + 1 >= len(self.values):
            return False

        self.current_sum -= self.values[self.left]
        self.left += 1
        self.right += 1
        self.current_sum += self.values[self.right]
        return True


# ---------------------------------------------------------------------------
# 16. Testing and validation
# ---------------------------------------------------------------------------

def run_assertions() -> None:
    numbers = [2, 1, 5, 1, 3, 2]
    assert maximum_sum_naive(numbers, 3) == 9
    assert maximum_sum_fixed_window(numbers, 3) == 9
    assert minimum_sum_fixed_window(numbers, 3) == 6

    assert average_of_each_window([1, 2, 3, 4], 2) == [1.5, 2.5, 3.5]

    assert maximum_in_each_window(
        [1, 3, -1, -3, 5, 3, 6, 7], 3
    ) == [3, 3, 5, 5, 6, 7]

    assert minimum_in_each_window(
        [1, 3, -1, -3, 5, 3, 6, 7], 3
    ) == [-1, -3, -3, -3, 3, 3]

    assert minimum_length_subarray_at_least_target(
        [2, 3, 1, 2, 4, 3], 7
    ) == 2

    assert longest_substring_at_most_k_distinct(
        "eceba", 2
    )[0] == 3

    assert longest_unique_substring("abcabcbb")[0] == 3

    assert minimum_window_substring(
        "ADOBECODEBANC", "ABC"
    ) == "BANC"

    assert contains_permutation("oidbcaf", "abc") is True
    assert find_all_anagrams("cbaebabacd", "abc") == [0, 6]

    assert longest_ones_with_k_flips(
        [1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0], 2
    ) == 6

    assert longest_ones_after_one_deletion(
        [1, 1, 0, 1]
    ) == 3

    assert count_subarrays_exactly_k_distinct(
        [1, 2, 1, 2, 3], 2
    ) == 7

    length, window = longest_subarray_bounded_difference(
        [8, 2, 4, 7], 4
    )
    assert length == 2
    assert window == [2, 4]

    assert maximum_weighted_window(
        [1, 2, 3, 4], [4, 3, 2, 1], 2
    ) == 10


# ---------------------------------------------------------------------------
# 17. Demonstration
# ---------------------------------------------------------------------------

def demonstrate() -> None:
    print("\n=== FIXED-SIZE WINDOWS ===")

    numbers = [2, 1, 5, 1, 3, 2]
    k = 3

    print("Input:", numbers)
    print("Window size:", k)
    print("Naive maximum:", maximum_sum_naive(numbers, k))
    print("Sliding-window maximum:", maximum_sum_fixed_window(numbers, k))
    print("Sliding-window minimum:", minimum_sum_fixed_window(numbers, k))

    print(
        "Window averages:",
        average_of_each_window([1, 2, 3, 4, 5], 3),
    )

    print(
        "Window maximums:",
        maximum_in_each_window(
            [1, 3, -1, -3, 5, 3, 6, 7], 3
        ),
    )

    print(
        "Window minimums:",
        minimum_in_each_window(
            [1, 3, -1, -3, 5, 3, 6, 7], 3
        ),
    )

    print("\n=== VARIABLE-SIZE NUMERIC WINDOWS ===")

    numbers = [2, 3, 1, 2, 4, 3]
    print("Minimum length with sum >= 7:",
          minimum_length_subarray_at_least_target(numbers, 7))

    print("Longest length with sum <= 7:",
          longest_subarray_sum_at_most_k([1, 2, 1, 0, 3], 7))

    print("\n=== STRING WINDOWS ===")

    text = "abcabcbb"
    length, substring = longest_unique_substring(text)
    print("Longest unique substring:", substring, "length:", length)

    length, substring = longest_substring_at_most_k_distinct(
        "eceba", 2
    )
    print("At most 2 distinct:", substring, "length:", length)

    length, substring = longest_repeating_character_replacement(
        "AABABBA", 1
    )
    print("One replacement:", substring, "length:", length)

    print(
        "Minimum window:",
        minimum_window_substring("ADOBECODEBANC", "ABC"),
    )

    print(
        "Permutation exists:",
        contains_permutation("oidbcaf", "abc"),
    )

    print(
        "Anagram positions:",
        find_all_anagrams("cbaebabacd", "abc"),
    )

    print("\n=== CONSTRAINT WINDOWS ===")

    binary = [1, 1, 0, 0, 1, 1, 1, 0, 1]
    print("Longest ones with two flips:",
          longest_ones_with_k_flips(binary, 2))

    print("Longest ones after one deletion:",
          longest_ones_after_one_deletion(binary))

    values = [8, 2, 4, 7]
    length, window = longest_subarray_bounded_difference(values, 4)
    print("Bounded-difference window:", window, "length:", length)

    print("\n=== EXACTLY K DISTINCT ===")
    values = [1, 2, 1, 2, 3]
    print(
        "Subarrays with exactly two distinct values:",
        count_subarrays_exactly_k_distinct(values, 2),
    )

    print("\n=== REUSABLE WINDOW OBJECT ===")
    window = FixedWindowSum([4, 2, 7, 1, 5], 3)

    while True:
        print("Window state:", window.current())
        if not window.slide():
            break


# ---------------------------------------------------------------------------
# 18. Complexity reference
# ---------------------------------------------------------------------------

def print_complexity_reference() -> None:
    print("\n=== COMPLEXITY REFERENCE ===")
    rows = [
        ("Fixed-size sum", "O(n)", "O(1)"),
        ("Fixed-size average", "O(n)", "O(1)"),
        ("Window max/min with deque", "O(n)", "O(k)"),
        ("Longest unique substring", "O(n)", "O(u)"),
        ("At most K distinct", "O(n)", "O(k)"),
        ("Minimum window substring", "O(n+m)", "O(u)"),
        ("Anagram search", "O(n+m)", "O(u)"),
        ("Exactly K distinct", "O(n)", "O(u)"),
        ("Bounded difference", "O(n)", "O(k)"),
    ]

    print(f"{'Problem':35} {'Time':10} {'Space':10}")
    print("-" * 58)
    for problem, time, space in rows:
        print(f"{problem:35} {time:10} {space:10}")


# ---------------------------------------------------------------------------
# 19. Important limitations
# ---------------------------------------------------------------------------

def demonstrate_edge_cases() -> None:
    print("\n=== EDGE CASES AND LIMITATIONS ===")

    cases = [
        ("Empty unique substring", longest_unique_substring("")),
        ("Empty minimum window", minimum_window_substring("", "A")),
        ("Pattern longer than text", contains_permutation("ab", "abcd")),
        ("K=0 distinct", count_subarrays_exactly_k_distinct([1, 2], 0)),
        ("All equal characters", longest_unique_substring("aaaa")),
        ("Window equal to input", maximum_sum_fixed_window([5, -2, 3], 3)),
    ]

    for name, value in cases:
        print(f"{name}: {value}")

    print("""
Important limitations:

1. Fixed-size windows need a valid k.
2. Many variable-size sum problems rely on non-negative values.
3. A frequency map consumes memory proportional to the number of tracked
   distinct values.
4. Monotonic deques store indices and require careful expiration logic.
5. Sliding windows operate on contiguous ranges.
6. For Unicode text, "character" can mean different things depending on
   the language/runtime and normalization model.
7. Integer overflow can matter in fixed-width languages such as C++.
8. A window predicate should usually have a monotonic property: after
   expansion violates the constraint, contraction should be capable of
   restoring validity without needing to reconsider discarded positions.
""")


def main() -> None:
    explain_basics()
    demonstrate()
    demonstrate_edge_cases()
    print_complexity_reference()
    run_assertions()
    print("\nAll built-in assertions passed successfully.")


if __name__ == "__main__":
    main()
