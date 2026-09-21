"""
Kadane's Algorithm: Maximum and Minimum Subarray Study

This standalone script teaches:
- Subarrays and contiguous ranges
- Brute-force maximum subarray
- Prefix sums
- Kadane's algorithm
- Recovering the actual maximum subarray
- Minimum subarray
- Circular maximum subarray
- Circular minimum subarray
- Fixed-length variants
- Maximum subarray with at-most-k length
- Maximum subarray with at-least-k length
- Maximum product subarray
- Maximum sum with one deletion
- Maximum sum with one allowed replacement
- Counting maximum-sum subarrays
- Streaming-style Kadane processing
- Overflow considerations
- Complexity comparisons
- Testing and edge cases

The examples use only the Python standard library.
"""

from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Iterable, Optional


NEG_INF = float("-inf")
POS_INF = float("inf")


def print_section(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def validate_non_empty(numbers: list[int]) -> None:
    if not numbers:
        raise ValueError("The array must contain at least one element.")


def validate_k(numbers: list[int], k: int) -> None:
    validate_non_empty(numbers)
    if not 1 <= k <= len(numbers):
        raise ValueError("k must satisfy 1 <= k <= len(numbers).")


# ---------------------------------------------------------------------------
# 1. Fundamental concept: subarrays
# ---------------------------------------------------------------------------

def all_subarrays(numbers: list[int]) -> list[list[int]]:
    """
    Return every non-empty contiguous subarray.

    For [1, 2, 3], the subarrays are:
    [1], [1, 2], [1, 2, 3], [2], [2, 3], [3]

    The number of non-empty subarrays is n * (n + 1) // 2.
    """
    result: list[list[int]] = []

    for start in range(len(numbers)):
        for end in range(start + 1, len(numbers) + 1):
            result.append(numbers[start:end])

    return result


def demonstrate_subarrays() -> None:
    numbers = [4, -2, 3]

    print("Array:", numbers)
    print("Non-empty contiguous subarrays:")

    for subarray in all_subarrays(numbers):
        print(subarray)


# ---------------------------------------------------------------------------
# 2. Brute-force maximum subarray
# ---------------------------------------------------------------------------

def maximum_subarray_bruteforce(numbers: list[int]) -> tuple[int, int, int]:
    """
    Brute-force O(n^3) implementation.

    Returns:
        (maximum_sum, start_index, end_index)

    The end index is inclusive.

    This version explicitly creates every subarray and sums its values.
    It is excellent for learning but unsuitable for large inputs.
    """
    validate_non_empty(numbers)

    best_sum = numbers[0]
    best_start = 0
    best_end = 0

    for start in range(len(numbers)):
        for end in range(start, len(numbers)):
            current_sum = sum(numbers[start:end + 1])

            if current_sum > best_sum:
                best_sum = current_sum
                best_start = start
                best_end = end

    return best_sum, best_start, best_end


# ---------------------------------------------------------------------------
# 3. Brute force improved with incremental sums
# ---------------------------------------------------------------------------

def maximum_subarray_quadratic(numbers: list[int]) -> tuple[int, int, int]:
    """
    O(n^2) maximum-subarray implementation.

    Instead of repeatedly calculating sum(numbers[start:end + 1]),
    extend the current subarray one element at a time.
    """
    validate_non_empty(numbers)

    best_sum = numbers[0]
    best_start = 0
    best_end = 0

    for start in range(len(numbers)):
        current_sum = 0

        for end in range(start, len(numbers)):
            current_sum += numbers[end]

            if current_sum > best_sum:
                best_sum = current_sum
                best_start = start
                best_end = end

    return best_sum, best_start, best_end


# ---------------------------------------------------------------------------
# 4. Prefix sums
# ---------------------------------------------------------------------------

def build_prefix_sums(numbers: list[int]) -> list[int]:
    """
    prefix[i] stores the sum of the first i elements.

    Therefore:
        sum(numbers[left:right]) = prefix[right] - prefix[left]

    A prefix array has n + 1 elements.
    """
    prefix = [0]

    for value in numbers:
        prefix.append(prefix[-1] + value)

    return prefix


def maximum_subarray_prefix(numbers: list[int]) -> tuple[int, int, int]:
    """
    O(n^2) maximum-subarray implementation using prefix sums.

    Each subarray sum becomes O(1), but all O(n^2) ranges still need
    to be examined.
    """
    validate_non_empty(numbers)

    prefix = build_prefix_sums(numbers)

    best_sum = numbers[0]
    best_start = 0
    best_end = 0

    for start in range(len(numbers)):
        for end_exclusive in range(start + 1, len(numbers) + 1):
            current_sum = prefix[end_exclusive] - prefix[start]

            if current_sum > best_sum:
                best_sum = current_sum
                best_start = start
                best_end = end_exclusive - 1

    return best_sum, best_start, best_end


# ---------------------------------------------------------------------------
# 5. Kadane's algorithm
# ---------------------------------------------------------------------------

def kadane(numbers: list[int]) -> int:
    """
    Classic Kadane's algorithm.

    Core idea:
        best_ending_here =
            max(current_value,
                best_ending_here + current_value)

    At every position we decide whether the previous subarray should
    continue or whether a new subarray should start at the current value.

    Time:  O(n)
    Space: O(1)

    Important edge case:
    An all-negative array must return its largest element, not zero.
    """
    validate_non_empty(numbers)

    best_ending_here = numbers[0]
    best_so_far = numbers[0]

    for value in numbers[1:]:
        best_ending_here = max(value, best_ending_here + value)
        best_so_far = max(best_so_far, best_ending_here)

    return best_so_far


def kadane_with_indices(numbers: list[int]) -> tuple[int, int, int]:
    """
    Kadane's algorithm while remembering the actual subarray.

    Returns:
        (maximum_sum, start_index, end_index)
    """
    validate_non_empty(numbers)

    best_ending_here = numbers[0]
    best_so_far = numbers[0]

    current_start = 0
    best_start = 0
    best_end = 0

    for index in range(1, len(numbers)):
        value = numbers[index]

        # Starting over is better when the previous accumulated sum
        # would make the current value worse.
        if value > best_ending_here + value:
            best_ending_here = value
            current_start = index
        else:
            best_ending_here += value

        if best_ending_here > best_so_far:
            best_so_far = best_ending_here
            best_start = current_start
            best_end = index

    return best_so_far, best_start, best_end


@dataclass(frozen=True)
class SubarrayResult:
    sum: int
    start: int
    end: int
    values: tuple[int, ...]

    @property
    def length(self) -> int:
        return self.end - self.start + 1


def maximum_subarray_result(numbers: list[int]) -> SubarrayResult:
    validate_non_empty(numbers)

    best_sum, start, end = kadane_with_indices(numbers)

    return SubarrayResult(
        sum=best_sum,
        start=start,
        end=end,
        values=tuple(numbers[start:end + 1]),
    )


# ---------------------------------------------------------------------------
# 6. Minimum subarray
# ---------------------------------------------------------------------------

def minimum_subarray(numbers: list[int]) -> int:
    """
    Minimum-subarray analogue of Kadane's algorithm.

    Replace max with min:

        minimum_ending_here =
            min(value, minimum_ending_here + value)

    This finds the smallest possible sum over a non-empty contiguous range.
    """
    validate_non_empty(numbers)

    minimum_ending_here = numbers[0]
    minimum_so_far = numbers[0]

    for value in numbers[1:]:
        minimum_ending_here = min(value, minimum_ending_here + value)
        minimum_so_far = min(minimum_so_far, minimum_ending_here)

    return minimum_so_far


def minimum_subarray_with_indices(numbers: list[int]) -> tuple[int, int, int]:
    validate_non_empty(numbers)

    best_ending_here = numbers[0]
    best_so_far = numbers[0]

    current_start = 0
    best_start = 0
    best_end = 0

    for index in range(1, len(numbers)):
        value = numbers[index]

        if value < best_ending_here + value:
            best_ending_here = value
            current_start = index
        else:
            best_ending_here += value

        if best_ending_here < best_so_far:
            best_so_far = best_ending_here
            best_start = current_start
            best_end = index

    return best_so_far, best_start, best_end


# ---------------------------------------------------------------------------
# 7. Circular maximum subarray
# ---------------------------------------------------------------------------

def maximum_circular_subarray(numbers: list[int]) -> int:
    """
    Maximum subarray when the array is considered circular.

    There are two possibilities:

    1. The best range does not wrap around:
       ordinary Kadane.

    2. The best range wraps around the boundary:
       total_sum - minimum_subarray_sum

    Example:
        [5, -3, 5]
        ordinary maximum = 7
        total = 7
        minimum subarray = -3
        circular maximum = 7 - (-3) = 10
        wrapped range is [5] + [5].

    Special case:
    If all values are negative, total - minimum would become zero,
    which would incorrectly represent an empty subarray. In that case
    return the ordinary Kadane result.
    """
    validate_non_empty(numbers)

    ordinary_max = kadane(numbers)

    if ordinary_max < 0:
        return ordinary_max

    total_sum = sum(numbers)
    minimum_sum = minimum_subarray(numbers)

    return max(ordinary_max, total_sum - minimum_sum)


def maximum_circular_subarray_with_indices(
    numbers: list[int],
) -> tuple[int, tuple[int, ...]]:
    """
    Return the maximum circular sum and one corresponding sequence of
    original indices.

    The wrapped sequence is represented in circular order.
    """
    validate_non_empty(numbers)

    ordinary_sum, start, end = kadane_with_indices(numbers)

    if ordinary_sum < 0:
        return ordinary_sum, tuple(range(start, end + 1))

    minimum_sum, min_start, min_end = minimum_subarray_with_indices(numbers)
    total_sum = sum(numbers)
    wrapped_sum = total_sum - minimum_sum

    if wrapped_sum <= ordinary_sum:
        return ordinary_sum, tuple(range(start, end + 1))

    n = len(numbers)

    # The wrapped subarray consists of:
    # min_end + 1 ... n - 1, followed by 0 ... min_start - 1.
    indices = tuple(range(min_end + 1, n)) + tuple(range(0, min_start))

    return wrapped_sum, indices


# ---------------------------------------------------------------------------
# 8. Circular minimum subarray
# ---------------------------------------------------------------------------

def minimum_circular_subarray(numbers: list[int]) -> int:
    """
    Minimum-sum circular subarray.

    The circular minimum can be:

    - the ordinary minimum subarray, or
    - total_sum - maximum_subarray_sum

    The all-positive case requires special handling because the second
    formula could represent an empty subarray.
    """
    validate_non_empty(numbers)

    ordinary_min = minimum_subarray(numbers)

    if ordinary_min > 0:
        return ordinary_min

    total_sum = sum(numbers)
    maximum_sum = kadane(numbers)

    return min(ordinary_min, total_sum - maximum_sum)


# ---------------------------------------------------------------------------
# 9. Fixed-length maximum subarray
# ---------------------------------------------------------------------------

def maximum_fixed_length_subarray(
    numbers: list[int], k: int
) -> tuple[int, int, int]:
    """
    Maximum sum among all subarrays having exactly k elements.

    Sliding window gives O(n) time.
    """
    validate_k(numbers, k)

    current_sum = sum(numbers[:k])
    best_sum = current_sum
    best_start = 0

    for right in range(k, len(numbers)):
        current_sum += numbers[right]
        current_sum -= numbers[right - k]

        current_start = right - k + 1

        if current_sum > best_sum:
            best_sum = current_sum
            best_start = current_start

    return best_sum, best_start, best_start + k - 1


# ---------------------------------------------------------------------------
# 10. Maximum subarray with at most k elements
# ---------------------------------------------------------------------------

def maximum_subarray_at_most_k(numbers: list[int], k: int) -> int:
    """
    Maximum sum among non-empty subarrays of length <= k.

    Prefix sums convert the problem into:

        prefix[r] - minimum(prefix[l])

    where r - l <= k.

    A monotonic deque maintains the smallest eligible prefix sum.

    Time: O(n)
    Space: O(k)
    """
    validate_k(numbers, k)

    prefix = build_prefix_sums(numbers)

    from collections import deque

    # Stores prefix indices with increasing prefix values.
    candidates: deque[int] = deque([0])

    best_sum = numbers[0]

    for right in range(1, len(prefix)):
        # Remove prefix indices that are too old.
        while candidates and candidates[0] < right - k:
            candidates.popleft()

        current_sum = prefix[right] - prefix[candidates[0]]
        best_sum = max(best_sum, current_sum)

        # Current prefix can become a future left boundary.
        while candidates and prefix[candidates[-1]] >= prefix[right]:
            candidates.pop()

        candidates.append(right)

    return best_sum


# ---------------------------------------------------------------------------
# 11. Maximum subarray with at least k elements
# ---------------------------------------------------------------------------

def maximum_subarray_at_least_k(numbers: list[int], k: int) -> int:
    """
    Maximum sum among non-empty subarrays of length at least k.

    First compute every length-k window. A longer candidate can be formed
    by extending a length-k ending position with a best positive prefix
    contribution.

    A particularly clear formulation uses prefix sums:

        prefix[r] - minimum(prefix[l])

    subject to r - l >= k.

    We maintain the smallest prefix sum among all eligible l.
    """
    validate_k(numbers, k)

    prefix = build_prefix_sums(numbers)

    minimum_prefix = prefix[0]
    best_sum = NEG_INF

    for right in range(k, len(prefix)):
        # prefix[right - k] becomes eligible as a left endpoint.
        minimum_prefix = min(minimum_prefix, prefix[right - k])
        best_sum = max(best_sum, prefix[right] - minimum_prefix)

    return int(best_sum)


# ---------------------------------------------------------------------------
# 12. Maximum product subarray
# ---------------------------------------------------------------------------

def maximum_product_subarray(numbers: list[int]) -> int:
    """
    Maximum product contiguous subarray.

    Unlike sums, multiplication changes sign when multiplied by a negative
    number. Therefore we must keep both:

        maximum product ending here
        minimum product ending here

    The minimum may become the maximum after multiplication by a negative.

    Time: O(n)
    Space: O(1)
    """
    validate_non_empty(numbers)

    maximum_ending = numbers[0]
    minimum_ending = numbers[0]
    best = numbers[0]

    for value in numbers[1:]:
        candidates = (
            value,
            maximum_ending * value,
            minimum_ending * value,
        )

        maximum_ending = max(candidates)
        minimum_ending = min(candidates)
        best = max(best, maximum_ending)

    return best


# ---------------------------------------------------------------------------
# 13. Maximum sum with one deletion
# ---------------------------------------------------------------------------

def maximum_subarray_one_deletion(numbers: list[int]) -> int:
    """
    Maximum subarray sum when at most one element may be deleted.

    State 1:
        no deletion has been used.

    State 2:
        one deletion has been used.

    For every value x:

        new_no_delete = max(x, no_delete + x)

        new_one_delete = max(
            x,
            one_delete + x,
            no_delete
        )

    The "no_delete" term means that x itself is deleted.

    Time: O(n)
    Space: O(1)
    """
    validate_non_empty(numbers)

    no_delete = numbers[0]
    one_delete = NEG_INF
    best = numbers[0]

    for value in numbers[1:]:
        previous_no_delete = no_delete
        previous_one_delete = one_delete

        no_delete = max(value, previous_no_delete + value)

        one_delete = max(
            value,
            previous_one_delete + value,
            previous_no_delete,
        )

        best = max(best, no_delete, one_delete)

    return int(best)


# ---------------------------------------------------------------------------
# 14. Maximum sum after replacing one element
# ---------------------------------------------------------------------------

def maximum_subarray_one_replacement(
    numbers: list[int], replacement_value: int
) -> int:
    """
    Maximum contiguous sum when at most one element may be replaced by a
    specified value.

    State 1: no replacement used.
    State 2: replacement already used.

    This is a useful example of extending Kadane's state model.
    """
    validate_non_empty(numbers)

    no_replacement = numbers[0]
    replacement_used = replacement_value
    best = max(no_replacement, replacement_used)

    for value in numbers[1:]:
        previous_no_replacement = no_replacement
        previous_replacement = replacement_used

        no_replacement = max(
            value,
            previous_no_replacement + value,
        )

        replacement_used = max(
            value,
            previous_replacement + value,
            previous_no_replacement + replacement_value,
            replacement_value,
        )

        best = max(best, no_replacement, replacement_used)

    return best


# ---------------------------------------------------------------------------
# 15. Count subarrays having the maximum possible sum
# ---------------------------------------------------------------------------

def count_subarrays_with_sum(numbers: list[int], target: int) -> int:
    """
    Count contiguous subarrays whose sum equals target.

    Prefix-sum identity:

        current_prefix - previous_prefix = target

    Therefore:

        previous_prefix = current_prefix - target

    A dictionary stores how many times each prefix sum has appeared.
    """
    prefix_frequency = {0: 1}
    current_prefix = 0
    count = 0

    for value in numbers:
        current_prefix += value
        count += prefix_frequency.get(current_prefix - target, 0)
        prefix_frequency[current_prefix] = (
            prefix_frequency.get(current_prefix, 0) + 1
        )

    return count


# ---------------------------------------------------------------------------
# 16. Streaming Kadane
# ---------------------------------------------------------------------------

class StreamingKadane:
    """
    Maintain a maximum subarray result as values arrive one at a time.

    This demonstrates that Kadane's algorithm does not require the complete
    array to be stored when only the maximum sum is required.

    The object keeps O(1) state.
    """

    def __init__(self) -> None:
        self.seen_value = False
        self.best_ending_here = 0
        self.best_so_far = NEG_INF

    def add(self, value: int) -> int:
        if not self.seen_value:
            self.best_ending_here = value
            self.best_so_far = value
            self.seen_value = True
        else:
            self.best_ending_here = max(
                value,
                self.best_ending_here + value,
            )
            self.best_so_far = max(
                self.best_so_far,
                self.best_ending_here,
            )

        return int(self.best_so_far)

    def result(self) -> int:
        if not self.seen_value:
            raise ValueError("No values have been added.")

        return int(self.best_so_far)


# ---------------------------------------------------------------------------
# 17. Divide-and-conquer maximum subarray
# ---------------------------------------------------------------------------

def maximum_crossing_sum(
    numbers: list[int], left: int, middle: int, right: int
) -> int:
    """
    Best subarray that crosses middle.

    The left half must end at middle.
    The right half must start at middle + 1.
    """
    left_sum = NEG_INF
    running = 0

    for index in range(middle, left - 1, -1):
        running += numbers[index]
        left_sum = max(left_sum, running)

    right_sum = NEG_INF
    running = 0

    for index in range(middle + 1, right + 1):
        running += numbers[index]
        right_sum = max(right_sum, running)

    return int(left_sum + right_sum)


def maximum_subarray_divide_and_conquer(
    numbers: list[int], left: int = 0, right: Optional[int] = None
) -> int:
    """
    Divide-and-conquer maximum subarray.

    Time: O(n log n)
    Space: O(log n) recursion depth.

    Kadane is normally preferable for the ordinary one-dimensional problem,
    but divide-and-conquer is important because it illustrates how a
    problem can be split into left, right, and crossing cases.
    """
    validate_non_empty(numbers)

    if right is None:
        right = len(numbers) - 1

    if left == right:
        return numbers[left]

    middle = (left + right) // 2

    left_best = maximum_subarray_divide_and_conquer(
        numbers, left, middle
    )
    right_best = maximum_subarray_divide_and_conquer(
        numbers, middle + 1, right
    )
    crossing_best = maximum_crossing_sum(
        numbers, left, middle, right
    )

    return max(left_best, right_best, crossing_best)


# ---------------------------------------------------------------------------
# 18. Demonstrations
# ---------------------------------------------------------------------------

def demonstrate_basic_kadane() -> None:
    examples = [
        [-2, 1, -3, 4, -1, 2, 1, -5, 4],
        [1],
        [-5, -2, -9, -1],
        [5, 4, 3],
        [-1, 0, -2],
        [0, 0, 0],
    ]

    for numbers in examples:
        result = maximum_subarray_result(numbers)

        print(
            f"{numbers}\n"
            f"  maximum sum = {result.sum}\n"
            f"  range = [{result.start}, {result.end}]\n"
            f"  subarray = {list(result.values)}"
        )


def demonstrate_circular() -> None:
    examples = [
        [5, -3, 5],
        [3, -2, 2, -3],
        [-3, -2, -1],
        [3, 4, 5],
        [-5, 4, -1, 7, 8],
    ]

    for numbers in examples:
        maximum = maximum_circular_subarray(numbers)
        minimum = minimum_circular_subarray(numbers)
        print(
            f"{numbers}\n"
            f"  circular maximum = {maximum}\n"
            f"  circular minimum = {minimum}"
        )


def demonstrate_variations() -> None:
    numbers = [2, -1, 2, 3, -9, 4, 6, -2]

    print("Input:", numbers)
    print("Exactly 3:", maximum_fixed_length_subarray(numbers, 3))
    print("At most 4:", maximum_subarray_at_most_k(numbers, 4))
    print("At least 3:", maximum_subarray_at_least_k(numbers, 3))
    print("Maximum product:", maximum_product_subarray(numbers))
    print("One deletion:", maximum_subarray_one_deletion(numbers))
    print(
        "One replacement with 10:",
        maximum_subarray_one_replacement(numbers, 10),
    )


def demonstrate_streaming() -> None:
    numbers = [-2, 1, -3, 4, -1, 2, 1, -5, 4]

    tracker = StreamingKadane()

    for value in numbers:
        print(
            f"Added {value:>3}: "
            f"current best = {tracker.add(value)}"
        )


# ---------------------------------------------------------------------------
# 19. Randomized cross-checking
# ---------------------------------------------------------------------------

def verify_algorithms() -> None:
    """
    Compare multiple implementations on many small random arrays.

    This is useful because the brute-force method is simple enough to act
    as a reference implementation.
    """
    random = Random(42)

    for _ in range(1000):
        length = random.randint(1, 10)
        numbers = [
            random.randint(-10, 10)
            for _ in range(length)
        ]

        brute = maximum_subarray_bruteforce(numbers)[0]
        quadratic = maximum_subarray_quadratic(numbers)[0]
        prefix = maximum_subarray_prefix(numbers)[0]
        linear = kadane(numbers)
        divide = maximum_subarray_divide_and_conquer(numbers)

        results = {
            "brute": brute,
            "quadratic": quadratic,
            "prefix": prefix,
            "kadane": linear,
            "divide": divide,
        }

        if len(set(results.values())) != 1:
            raise AssertionError(
                f"Mismatch for {numbers}: {results}"
            )

    print("Randomized maximum-subarray verification: PASSED")


# ---------------------------------------------------------------------------
# 20. Edge-case demonstrations
# ---------------------------------------------------------------------------

def demonstrate_edge_cases() -> None:
    cases = {
        "single positive": [7],
        "single negative": [-7],
        "all negative": [-8, -3, -6, -2, -5],
        "all positive": [1, 2, 3, 4],
        "zeros": [0, 0, 0],
        "alternating": [10, -20, 30, -5, 4],
        "large cancellation": [10**9, -10**9, 10**9],
    }

    for name, numbers in cases.items():
        print(
            f"{name:>20}: {numbers} -> "
            f"max={kadane(numbers)}, min={minimum_subarray(numbers)}"
        )


# ---------------------------------------------------------------------------
# 21. Common incorrect implementation
# ---------------------------------------------------------------------------

def incorrect_all_negative_version(numbers: list[int]) -> int:
    """
    This function intentionally demonstrates a common bug.

    Starting best at zero silently permits the empty subarray.
    The conventional maximum-subarray problem requires a non-empty
    subarray, so this implementation is intentionally NOT used as the
    correct solution.
    """
    best = 0
    current = 0

    for value in numbers:
        current = max(0, current + value)
        best = max(best, current)

    return best


def demonstrate_common_mistake() -> None:
    numbers = [-5, -2, -9]

    print("All-negative array:", numbers)
    print("Incorrect empty-subarray-permitting result:",
          incorrect_all_negative_version(numbers))
    print("Correct non-empty result:", kadane(numbers))


# ---------------------------------------------------------------------------
# 22. Complexity reference
# ---------------------------------------------------------------------------

def print_complexity_reference() -> None:
    rows = [
        ("Brute force with repeated sum", "O(n^3)", "O(1)"),
        ("Incremental brute force", "O(n^2)", "O(1)"),
        ("Prefix-sum enumeration", "O(n^2)", "O(n)"),
        ("Kadane", "O(n)", "O(1)"),
        ("Divide and conquer", "O(n log n)", "O(log n)"),
        ("Fixed-length sliding window", "O(n)", "O(1)"),
        ("At-most-k with deque", "O(n)", "O(k)"),
        ("Maximum product", "O(n)", "O(1)"),
        ("One deletion", "O(n)", "O(1)"),
    ]

    print(f"{'Technique':35} {'Time':12} {'Space':12}")
    print("-" * 59)

    for technique, time, space in rows:
        print(f"{technique:35} {time:12} {space:12}")


# ---------------------------------------------------------------------------
# 23. Assertions for core correctness
# ---------------------------------------------------------------------------

def run_assertions() -> None:
    assert kadane([-2, 1, -3, 4, -1, 2, 1, -5, 4]) == 6
    assert kadane([-3, -2, -5]) == -2
    assert kadane([5]) == 5
    assert kadane([0, 0, 0]) == 0

    assert minimum_subarray([3, -4, 2, -1]) == -4
    assert maximum_circular_subarray([5, -3, 5]) == 10
    assert maximum_circular_subarray([-3, -2, -1]) == -1

    assert maximum_fixed_length_subarray(
        [1, 2, 3, -2, 5], 3
    )[0] == 6

    assert maximum_product_subarray(
        [2, 3, -2, 4]
    ) == 6

    assert maximum_subarray_one_deletion(
        [1, -2, 0, 3]
    ) == 4

    assert count_subarrays_with_sum(
        [1, 1, 1], 2
    ) == 2

    print("Core assertions: PASSED")


# ---------------------------------------------------------------------------
# Main study program
# ---------------------------------------------------------------------------

def main() -> None:
    print_section("1. Subarrays")
    demonstrate_subarrays()

    print_section("2. Basic maximum-subarray implementations")
    numbers = [-2, 1, -3, 4, -1, 2, 1, -5, 4]

    print("Input:", numbers)
    print("Brute force:", maximum_subarray_bruteforce(numbers))
    print("Quadratic:", maximum_subarray_quadratic(numbers))
    print("Prefix sums:", maximum_subarray_prefix(numbers))
    print("Kadane:", kadane_with_indices(numbers))
    print("Divide and conquer:", maximum_subarray_divide_and_conquer(numbers))

    print_section("3. Kadane's algorithm")
    demonstrate_basic_kadane()

    print_section("4. Minimum subarray")
    print("Input:", numbers)
    print(
        "Minimum:",
        minimum_subarray_with_indices(numbers),
    )

    print_section("5. Circular subarrays")
    demonstrate_circular()

    print_section("6. Kadane variations")
    demonstrate_variations()

    print_section("7. Streaming Kadane")
    demonstrate_streaming()

    print_section("8. Edge cases")
    demonstrate_edge_cases()

    print_section("9. Common implementation mistake")
    demonstrate_common_mistake()

    print_section("10. Complexity")
    print_complexity_reference()

    print_section("11. Randomized verification")
    verify_algorithms()

    print_section("12. Assertions")
    run_assertions()

    print_section("13. Prefix-sum target counting")
    target_numbers = [1, 2, 3, -2, 2, 1]
    target = 3
    print(
        f"Array={target_numbers}, target={target}, "
        f"count={count_subarrays_with_sum(target_numbers, target)}"
    )

    print("\nStudy program completed successfully.")


if __name__ == "__main__":
    main()
