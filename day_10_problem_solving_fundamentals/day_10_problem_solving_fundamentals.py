"""
Problem-Solving Fundamentals
============================

A comprehensive, executable study file covering problem-solving from absolute
beginner level through advanced practical techniques.

The examples are intentionally implemented in Python so that the concepts can
be studied by reading the code, running it, changing inputs, and observing
behavior.

Main areas covered:
1. Understanding and restating problems
2. Inputs, outputs, assumptions, constraints, and requirements
3. Problem decomposition
4. Examples, tables, and manual simulation
5. Pattern recognition
6. Brute-force problem solving
7. Optimization and algorithmic thinking
8. Correctness and invariants
9. Edge cases and boundary conditions
10. Input validation
11. Complexity analysis
12. Common algorithmic patterns
13. Searching and sorting
14. Hashing and frequency counting
15. Two pointers
16. Sliding windows
17. Prefix sums
18. Binary search
19. Recursion and backtracking
20. Greedy reasoning
21. Dynamic programming
22. Graph problem-solving fundamentals
23. Testing and debugging
24. Property-based thinking without external packages
25. Trade-offs and production considerations
26. A complete end-to-end problem-solving workflow

Only the Python standard library is used.
"""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations
from math import inf, isclose, sqrt
from time import perf_counter
from typing import Callable, Iterable, Optional


# =============================================================================
# 1. BASIC PROBLEM-SOLVING VOCABULARY
# =============================================================================

def section(title: str) -> None:
    """Print a readable section heading."""
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def subsection(title: str) -> None:
    """Print a smaller heading."""
    print("\n" + "-" * 78)
    print(title)
    print("-" * 78)


@dataclass
class ProblemSpecification:
    """
    A simple representation of a problem specification.

    A good problem statement should make clear:
    - what information is provided,
    - what must be produced,
    - what restrictions apply,
    - what assumptions are valid.
    """

    problem: str
    inputs: str
    outputs: str
    constraints: str
    assumptions: str

    def display(self) -> None:
        print(f"Problem:     {self.problem}")
        print(f"Inputs:      {self.inputs}")
        print(f"Outputs:     {self.outputs}")
        print(f"Constraints: {self.constraints}")
        print(f"Assumptions: {self.assumptions}")


def demonstrate_problem_specification() -> None:
    section("1. Understanding a Problem")

    specification = ProblemSpecification(
        problem="Find the largest number in a list.",
        inputs="A finite list of numbers.",
        outputs="The largest number.",
        constraints="The list must contain at least one element.",
        assumptions="The elements are comparable.",
    )

    specification.display()

    print("\nThe important questions are:")
    questions = [
        "What exactly is the input?",
        "What exactly must be returned?",
        "What constraints are stated?",
        "What constraints are implied?",
        "What assumptions are safe?",
        "What happens for the smallest valid input?",
        "What happens for invalid input?",
    ]

    for number, question in enumerate(questions, start=1):
        print(f"{number}. {question}")


# =============================================================================
# 2. RESTATING A PROBLEM
# =============================================================================

def restate_find_maximum(numbers: list[int]) -> int:
    """
    Restate the problem operationally:

    Given a non-empty sequence of comparable values, inspect every value and
    return the greatest value encountered.
    """
    if not numbers:
        raise ValueError("The input list must not be empty.")

    largest = numbers[0]

    for value in numbers[1:]:
        if value > largest:
            largest = value

    return largest


def demonstrate_restatement() -> None:
    section("2. Restating a Problem as an Algorithm")

    examples = [
        [4, 7, 1, 9, 3],
        [-10, -5, -20, -1],
        [8],
    ]

    for numbers in examples:
        print(f"Input:  {numbers}")
        print(f"Output: {restate_find_maximum(numbers)}")


# =============================================================================
# 3. INPUTS, OUTPUTS, AND CONSTRAINTS
# =============================================================================

def validate_integer_list(values: Iterable[int]) -> list[int]:
    """
    Validate and normalize an integer collection.

    Validation is part of problem solving because an algorithm can be logically
    correct for valid input but still fail badly when its input assumptions are
    violated.
    """
    normalized = list(values)

    if not all(isinstance(value, int) and not isinstance(value, bool)
               for value in normalized):
        raise TypeError("All values must be integers.")

    return normalized


def demonstrate_constraints() -> None:
    section("3. Constraints Change the Solution")

    print("Example: searching for a target in a list.")

    print("\nIf the list is unsorted:")
    print("- Linear search is generally appropriate.")
    print("- Worst-case time: O(n).")

    print("\nIf the list is sorted:")
    print("- Binary search becomes possible.")
    print("- Worst-case time: O(log n).")

    print("\nIf many repeated searches are required:")
    print("- A hash set may provide average O(1) membership checks.")
    print("- This uses additional memory.")

    print("\nThe same task can therefore require different algorithms depending")
    print("on constraints and how the result will be used.")


# =============================================================================
# 4. MANUAL EXAMPLES AND TRACE TABLES
# =============================================================================

def trace_maximum(numbers: list[int]) -> None:
    """Show the state of a simple algorithm after each iteration."""
    if not numbers:
        raise ValueError("At least one value is required.")

    current_max = numbers[0]

    print("\nIndex | Value | Current maximum")
    print("-" * 34)

    for index, value in enumerate(numbers):
        if value > current_max:
            current_max = value

        print(f"{index:5} | {value:5} | {current_max:16}")


def demonstrate_examples() -> None:
    section("4. Examples and Manual Simulation")

    numbers = [5, 2, 8, 1, 7]
    print(f"Tracing: {numbers}")
    trace_maximum(numbers)

    print("\nManual tracing exposes:")
    print("- the changing state,")
    print("- the current decision,")
    print("- the invariant being maintained,")
    print("- and possible boundary failures.")


# =============================================================================
# 5. PROBLEM DECOMPOSITION
# =============================================================================

def calculate_student_result(scores: list[float]) -> dict[str, float | str]:
    """
    Decompose a larger task into smaller operations:

    1. Validate input.
    2. Calculate total.
    3. Calculate average.
    4. Determine classification.
    5. Return structured output.
    """
    if not scores:
        raise ValueError("At least one score is required.")

    if any(score < 0 or score > 100 for score in scores):
        raise ValueError("Each score must be between 0 and 100.")

    total = sum(scores)
    average = total / len(scores)

    if average >= 90:
        classification = "Excellent"
    elif average >= 75:
        classification = "Good"
    elif average >= 50:
        classification = "Pass"
    else:
        classification = "Fail"

    return {
        "total": total,
        "average": average,
        "classification": classification,
    }


def demonstrate_decomposition() -> None:
    section("5. Decomposing a Problem")

    scores = [78, 84, 91, 69, 88]
    result = calculate_student_result(scores)

    print(f"Scores: {scores}")
    print(f"Result: {result}")


# =============================================================================
# 6. BRUTE FORCE
# =============================================================================

def has_duplicate_brute_force(values: list[int]) -> bool:
    """
    Brute-force duplicate detection.

    Every pair is compared.

    Time: O(n^2)
    Extra space: O(1), excluding the input itself.

    This is useful as a baseline implementation because it is simple and can
    be used to verify a faster implementation.
    """
    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            if values[i] == values[j]:
                return True

    return False


def has_duplicate_set(values: list[int]) -> bool:
    """
    Optimized duplicate detection using a hash set.

    Average time: O(n)
    Extra space: O(n)
    """
    seen: set[int] = set()

    for value in values:
        if value in seen:
            return True
        seen.add(value)

    return False


def demonstrate_brute_force_and_optimization() -> None:
    section("6. Brute Force Before Optimization")

    test_cases = [
        [1, 2, 3, 4],
        [1, 2, 3, 2],
        [7],
        [],
    ]

    for values in test_cases:
        brute = has_duplicate_brute_force(values)
        optimized = has_duplicate_set(values)

        print(f"Input: {values}")
        print(f"Brute force: {brute}")
        print(f"Optimized:   {optimized}")

        assert brute == optimized


# =============================================================================
# 7. CORRECTNESS AND INVARIANTS
# =============================================================================

def sum_positive_numbers(values: list[int]) -> int:
    """
    Calculate a sum while maintaining this invariant:

    After processing the first k elements, total equals the sum of exactly
    those k elements.

    This gives a useful correctness argument for the loop.
    """
    total = 0

    for value in values:
        if value > 0:
            total += value

    return total


def demonstrate_invariant() -> None:
    section("7. Correctness and Loop Invariants")

    values = [-2, 5, 3, -1, 7]
    result = sum_positive_numbers(values)

    print(f"Input: {values}")
    print(f"Sum of positive values: {result}")

    print("\nInvariant idea:")
    print("At every point in the loop, the accumulator represents the correct")
    print("result for the portion of the input already processed.")


# =============================================================================
# 8. LINEAR SEARCH
# =============================================================================

def linear_search(values: list[int], target: int) -> int:
    """
    Return the first index containing target, or -1.

    Time: O(n)
    Space: O(1)
    """
    for index, value in enumerate(values):
        if value == target:
            return index

    return -1


def demonstrate_linear_search() -> None:
    section("8. Linear Search")

    values = [11, 4, 19, 7, 3, 19]

    for target in [19, 8]:
        print(f"Searching for {target}: index {linear_search(values, target)}")


# =============================================================================
# 9. BINARY SEARCH
# =============================================================================

def binary_search(values: list[int], target: int) -> int:
    """
    Iterative binary search.

    IMPORTANT:
    The input must be sorted in ascending order.

    Time: O(log n)
    Space: O(1)
    """
    left = 0
    right = len(values) - 1

    while left <= right:
        middle = left + (right - left) // 2

        if values[middle] == target:
            return middle

        if values[middle] < target:
            left = middle + 1
        else:
            right = middle - 1

    return -1


def demonstrate_binary_search() -> None:
    section("9. Binary Search")

    values = [2, 5, 8, 11, 15, 21, 30]
    print(f"Sorted input: {values}")

    for target in [2, 15, 30, 10]:
        print(f"Target {target}: index {binary_search(values, target)}")

    print("\nKey rule: binary search is only valid when the search space")
    print("satisfies the ordering assumption used by the algorithm.")


# =============================================================================
# 10. SORTING AS A TOOL
# =============================================================================

def bubble_sort(values: list[int]) -> list[int]:
    """
    Simple comparison sort.

    Time:
        Best case with early termination: O(n)
        Average/worst case: O(n^2)

    Space: O(1) auxiliary space.

    This implementation is educational rather than production-preferred.
    """
    result = values.copy()

    for end in range(len(result) - 1, 0, -1):
        swapped = False

        for index in range(end):
            if result[index] > result[index + 1]:
                result[index], result[index + 1] = (
                    result[index + 1],
                    result[index],
                )
                swapped = True

        if not swapped:
            break

    return result


def demonstrate_sorting() -> None:
    section("10. Sorting as a Problem-Solving Tool")

    values = [5, 1, 8, 2, 4]
    print(f"Original: {values}")
    print(f"Bubble sorted: {bubble_sort(values)}")
    print(f"Python sorted: {sorted(values)}")

    print("\nSorting can simplify problems involving:")
    print("- ordering")
    print("- duplicate grouping")
    print("- interval processing")
    print("- two-pointer techniques")
    print("- ranking")
    print("- greedy selection")


# =============================================================================
# 11. HASHING AND FREQUENCY COUNTING
# =============================================================================

def character_frequency(text: str) -> dict[str, int]:
    """Count the frequency of every character."""
    frequency: dict[str, int] = defaultdict(int)

    for character in text:
        frequency[character] += 1

    return dict(frequency)


def character_frequency_counter(text: str) -> Counter[str]:
    """The standard-library Counter expresses frequency counting directly."""
    return Counter(text)


def first_unique_character(text: str) -> Optional[str]:
    """
    Find the first character appearing exactly once.

    Time: O(n) average.
    Space: O(k), where k is the number of distinct characters.
    """
    counts = Counter(text)

    for character in text:
        if counts[character] == 1:
            return character

    return None


def demonstrate_hashing() -> None:
    section("11. Hashing and Frequency Counting")

    text = "programming"
    print(f"Text: {text}")
    print(f"Frequency: {character_frequency(text)}")
    print(f"Counter:  {character_frequency_counter(text)}")
    print(f"First unique character: {first_unique_character(text)}")


# =============================================================================
# 12. TWO SUM: BRUTE FORCE VS HASH MAP
# =============================================================================

def two_sum_brute_force(values: list[int], target: int) -> Optional[tuple[int, int]]:
    """
    Return indices of two values adding to target.

    Brute force:
    Time O(n^2)
    Space O(1)
    """
    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            if values[i] + values[j] == target:
                return i, j

    return None


def two_sum_hash_map(values: list[int], target: int) -> Optional[tuple[int, int]]:
    """
    Optimized two-sum solution.

    Average time O(n)
    Space O(n)
    """
    positions: dict[int, int] = {}

    for index, value in enumerate(values):
        needed = target - value

        if needed in positions:
            return positions[needed], index

        positions[value] = index

    return None


def demonstrate_two_sum() -> None:
    section("12. Optimization Through a Better Data Structure")

    values = [3, 8, 12, 4, 7]
    target = 11

    brute_result = two_sum_brute_force(values, target)
    optimized_result = two_sum_hash_map(values, target)

    print(f"Values: {values}")
    print(f"Target: {target}")
    print(f"Brute-force result: {brute_result}")
    print(f"Hash-map result:    {optimized_result}")

    assert brute_result == optimized_result


# =============================================================================
# 13. TWO POINTERS
# =============================================================================

def pair_sum_sorted(values: list[int], target: int) -> Optional[tuple[int, int]]:
    """
    Find two values adding to target in a sorted list.

    Time: O(n)
    Space: O(1)

    The left pointer moves right when the sum is too small.
    The right pointer moves left when the sum is too large.
    """
    left = 0
    right = len(values) - 1

    while left < right:
        current_sum = values[left] + values[right]

        if current_sum == target:
            return values[left], values[right]

        if current_sum < target:
            left += 1
        else:
            right -= 1

    return None


def demonstrate_two_pointers() -> None:
    section("13. Two-Pointer Technique")

    values = [1, 2, 4, 6, 8, 10, 14]
    target = 12

    print(f"Sorted values: {values}")
    print(f"Target: {target}")
    print(f"Pair: {pair_sum_sorted(values, target)}")


# =============================================================================
# 14. SLIDING WINDOW
# =============================================================================

def maximum_sum_fixed_window(values: list[int], window_size: int) -> int:
    """
    Maximum sum of any contiguous window of exactly window_size elements.

    Time: O(n)
    Space: O(1)

    A brute-force solution would repeatedly calculate each window sum,
    potentially taking O(n * window_size).
    """
    if window_size <= 0:
        raise ValueError("Window size must be positive.")

    if window_size > len(values):
        raise ValueError("Window size cannot exceed input length.")

    current_sum = sum(values[:window_size])
    best_sum = current_sum

    for right in range(window_size, len(values)):
        current_sum += values[right]
        current_sum -= values[right - window_size]
        best_sum = max(best_sum, current_sum)

    return best_sum


def longest_substring_without_repeating(text: str) -> int:
    """
    Length of the longest substring containing no repeated characters.

    Sliding-window solution.

    Time: O(n) average.
    Space: O(k).
    """
    left = 0
    last_seen: dict[str, int] = {}
    best_length = 0

    for right, character in enumerate(text):
        if character in last_seen and last_seen[character] >= left:
            left = last_seen[character] + 1

        last_seen[character] = right
        best_length = max(best_length, right - left + 1)

    return best_length


def demonstrate_sliding_window() -> None:
    section("14. Sliding-Window Technique")

    values = [2, 1, 5, 1, 3, 2]
    print(f"Values: {values}")
    print(f"Maximum sum for window 3: {maximum_sum_fixed_window(values, 3)}")

    text_examples = ["abcabcbb", "bbbbb", "pwwkew", ""]
    for text in text_examples:
        print(
            f"Text={text!r}, longest non-repeating substring length="
            f"{longest_substring_without_repeating(text)}"
        )


# =============================================================================
# 15. PREFIX SUMS
# =============================================================================

def build_prefix_sums(values: list[int]) -> list[int]:
    """
    Build prefix sums.

    prefix[i] stores the sum of the first i elements.

    For values [2, 4, 6]:
    prefix becomes [0, 2, 6, 12].
    """
    prefix = [0]

    for value in values:
        prefix.append(prefix[-1] + value)

    return prefix


def range_sum(prefix: list[int], left: int, right: int) -> int:
    """
    Inclusive range sum using a prefix-sum array.

    Example:
    values [2, 4, 6, 8]
    range [1, 3] = 4 + 6 + 8 = 18.
    """
    if left < 0 or right < left or right + 1 >= len(prefix):
        raise IndexError("Invalid inclusive range.")

    return prefix[right + 1] - prefix[left]


def demonstrate_prefix_sums() -> None:
    section("15. Prefix Sums")

    values = [2, 4, 6, 8, 10]
    prefix = build_prefix_sums(values)

    print(f"Values: {values}")
    print(f"Prefix sums: {prefix}")
    print(f"Sum from index 1 to 3: {range_sum(prefix, 1, 3)}")


# =============================================================================
# 16. RECURSION
# =============================================================================

def factorial_recursive(number: int) -> int:
    """
    Recursive factorial.

    Mathematical definition:
        0! = 1
        n! = n * (n - 1)! for n > 0

    Recursion must have:
    - a base case,
    - a progress rule that approaches the base case.
    """
    if not isinstance(number, int) or isinstance(number, bool):
        raise TypeError("number must be an integer.")

    if number < 0:
        raise ValueError("Factorial is undefined for negative integers.")

    if number == 0:
        return 1

    return number * factorial_recursive(number - 1)


def factorial_iterative(number: int) -> int:
    """Iterative version of factorial."""
    if not isinstance(number, int) or isinstance(number, bool):
        raise TypeError("number must be an integer.")

    if number < 0:
        raise ValueError("Factorial is undefined for negative integers.")

    result = 1

    for value in range(2, number + 1):
        result *= value

    return result


def demonstrate_recursion() -> None:
    section("16. Recursion")

    for number in range(6):
        recursive = factorial_recursive(number)
        iterative = factorial_iterative(number)
        print(f"{number}! = {recursive}")

        assert recursive == iterative

    print("\nRecursion is not automatically better than iteration.")
    print("It can make naturally recursive problems easier to express,")
    print("but it may introduce call-stack overhead.")


# =============================================================================
# 17. BACKTRACKING
# =============================================================================

def generate_subsets(values: list[int]) -> list[list[int]]:
    """
    Generate every subset using backtracking.

    For n elements there are 2^n subsets.

    This exponential growth is fundamental to many exhaustive search problems.
    """
    result: list[list[int]] = []
    current: list[int] = []

    def backtrack(index: int) -> None:
        if index == len(values):
            result.append(current.copy())
            return

        # Choice 1: exclude the current value.
        backtrack(index + 1)

        # Choice 2: include the current value.
        current.append(values[index])
        backtrack(index + 1)
        current.pop()

    backtrack(0)
    return result


def demonstrate_backtracking() -> None:
    section("17. Backtracking")

    values = [1, 2, 3]
    subsets = generate_subsets(values)

    print(f"Input: {values}")
    print(f"Number of subsets: {len(subsets)}")
    print(f"Subsets: {subsets}")


# =============================================================================
# 18. GREEDY ALGORITHMS
# =============================================================================

def minimum_coins_greedy(coins: list[int], amount: int) -> Optional[list[int]]:
    """
    Greedy coin selection.

    This repeatedly chooses the largest coin that does not exceed the
    remaining amount.

    IMPORTANT:
    Greedy is not universally optimal.

    For coins [1, 3, 4] and amount 6:
    greedy gives [4, 1, 1] -> 3 coins,
    while optimal gives [3, 3] -> 2 coins.
    """
    if amount < 0:
        raise ValueError("Amount cannot be negative.")

    if any(coin <= 0 for coin in coins):
        raise ValueError("Coins must be positive.")

    remaining = amount
    result: list[int] = []

    for coin in sorted(coins, reverse=True):
        while remaining >= coin:
            result.append(coin)
            remaining -= coin

    if remaining != 0:
        return None

    return result


def demonstrate_greedy_limitation() -> None:
    section("18. Greedy Thinking and Its Limitations")

    coins = [1, 3, 4]
    amount = 6

    greedy_result = minimum_coins_greedy(coins, amount)

    print(f"Coins: {coins}")
    print(f"Amount: {amount}")
    print(f"Greedy result: {greedy_result}")

    print("\nThis is a useful warning:")
    print("A locally best decision does not necessarily produce a globally")
    print("best solution.")


# =============================================================================
# 19. DYNAMIC PROGRAMMING
# =============================================================================

def minimum_coins_dynamic_programming(
    coins: list[int],
    amount: int,
) -> Optional[list[int]]:
    """
    Solve the minimum-coin problem optimally using bottom-up dynamic programming.

    dp[value] stores the minimum number of coins needed to make 'value'.
    choice[value] stores the coin used for the optimal solution.

    Time: O(amount * number_of_coins)
    Space: O(amount)
    """
    if amount < 0:
        raise ValueError("Amount cannot be negative.")

    if any(coin <= 0 for coin in coins):
        raise ValueError("Coins must be positive.")

    dp = [inf] * (amount + 1)
    choice: list[Optional[int]] = [None] * (amount + 1)
    dp[0] = 0

    for value in range(1, amount + 1):
        for coin in coins:
            if coin <= value and dp[value - coin] != inf:
                candidate = dp[value - coin] + 1

                if candidate < dp[value]:
                    dp[value] = candidate
                    choice[value] = coin

    if dp[amount] == inf:
        return None

    result: list[int] = []
    current = amount

    while current > 0:
        coin = choice[current]

        if coin is None:
            raise RuntimeError("Invalid dynamic-programming reconstruction.")

        result.append(coin)
        current -= coin

    return result


def demonstrate_dynamic_programming() -> None:
    section("19. Dynamic Programming")

    coins = [1, 3, 4]
    amount = 6

    greedy = minimum_coins_greedy(coins, amount)
    optimal = minimum_coins_dynamic_programming(coins, amount)

    print(f"Coins: {coins}")
    print(f"Amount: {amount}")
    print(f"Greedy:  {greedy}")
    print(f"Optimal: {optimal}")

    assert optimal is not None
    assert len(optimal) == 2


# =============================================================================
# 20. MEMOIZATION
# =============================================================================

def fibonacci_plain(number: int) -> int:
    """Naive recursive Fibonacci, useful for understanding repeated work."""
    if number < 0:
        raise ValueError("number must be non-negative.")

    if number <= 1:
        return number

    return fibonacci_plain(number - 1) + fibonacci_plain(number - 2)


@lru_cache(maxsize=None)
def fibonacci_memoized(number: int) -> int:
    """
    Fibonacci with memoization.

    Each state is solved once instead of repeatedly.

    Time: O(n)
    Space: O(n)
    """
    if number < 0:
        raise ValueError("number must be non-negative.")

    if number <= 1:
        return number

    return fibonacci_memoized(number - 1) + fibonacci_memoized(number - 2)


def demonstrate_memoization() -> None:
    section("20. Memoization")

    for number in range(11):
        plain = fibonacci_plain(number)
        memoized = fibonacci_memoized(number)
        print(f"F({number}) = {memoized}")
        assert plain == memoized


# =============================================================================
# 21. COMBINING CONSTRAINTS WITH ALGORITHMS
# =============================================================================

def contains_nearby_duplicate(values: list[int], distance: int) -> bool:
    """
    Determine whether equal values occur within 'distance' positions.

    Uses a dictionary storing the most recent position.

    Average time: O(n)
    Space: O(n)
    """
    if distance < 0:
        raise ValueError("Distance cannot be negative.")

    last_position: dict[int, int] = {}

    for index, value in enumerate(values):
        if value in last_position:
            if index - last_position[value] <= distance:
                return True

        last_position[value] = index

    return False


def demonstrate_constraint_driven_design() -> None:
    section("21. Constraints Drive Algorithm Selection")

    values = [1, 2, 3, 1]
    print(f"Values: {values}")
    print(f"Nearby duplicate within distance 3: "
          f"{contains_nearby_duplicate(values, 3)}")
    print(f"Nearby duplicate within distance 2: "
          f"{contains_nearby_duplicate(values, 2)}")


# =============================================================================
# 22. INTERVAL PROBLEMS
# =============================================================================

@dataclass(frozen=True)
class Interval:
    start: int
    end: int


def merge_intervals(intervals: list[Interval]) -> list[Interval]:
    """
    Merge overlapping intervals.

    Strategy:
    1. Sort by starting point.
    2. Maintain the interval currently being built.
    3. Merge when the next interval overlaps.
    4. Otherwise start a new interval.

    Time: O(n log n) due to sorting.
    Space: O(n) for the output.
    """
    if not intervals:
        return []

    sorted_intervals = sorted(intervals, key=lambda interval: interval.start)
    merged: list[Interval] = [sorted_intervals[0]]

    for current in sorted_intervals[1:]:
        previous = merged[-1]

        if current.start <= previous.end:
            merged[-1] = Interval(
                start=previous.start,
                end=max(previous.end, current.end),
            )
        else:
            merged.append(current)

    return merged


def demonstrate_intervals() -> None:
    section("22. Sorting Plus Greedy Interval Processing")

    intervals = [
        Interval(1, 3),
        Interval(2, 6),
        Interval(8, 10),
        Interval(9, 12),
    ]

    print(f"Original intervals: {intervals}")
    print(f"Merged intervals:   {merge_intervals(intervals)}")


# =============================================================================
# 23. STACK-BASED PROBLEM SOLVING
# =============================================================================

def is_balanced_parentheses(text: str) -> bool:
    """
    Validate (), [], and {} using a stack.

    A closing bracket must match the most recent unmatched opening bracket.
    """
    opening_to_closing = {
        "(": ")",
        "[": "]",
        "{": "}",
    }

    closing_to_opening = {
        ")": "(",
        "]": "[",
        "}": "{",
    }

    stack: list[str] = []

    for character in text:
        if character in opening_to_closing:
            stack.append(character)

        elif character in closing_to_opening:
            if not stack:
                return False

            if stack.pop() != closing_to_opening[character]:
                return False

    return not stack


def demonstrate_stack_problem() -> None:
    section("23. Stack-Based Problem Solving")

    examples = [
        "()",
        "([]{})",
        "([)]",
        "(((",
        "",
    ]

    for text in examples:
        print(f"{text!r}: {is_balanced_parentheses(text)}")


# =============================================================================
# 24. QUEUES AND BREADTH-FIRST SEARCH
# =============================================================================

def breadth_first_search(
    graph: dict[str, list[str]],
    start: str,
) -> list[str]:
    """
    Breadth-first traversal.

    A queue ensures nodes are processed level by level.

    Time: O(V + E)
    Space: O(V)
    """
    if start not in graph:
        raise KeyError(f"Unknown start node: {start}")

    visited = {start}
    queue: deque[str] = deque([start])
    order: list[str] = []

    while queue:
        node = queue.popleft()
        order.append(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return order


def demonstrate_bfs() -> None:
    section("24. Graph Traversal and Breadth-First Search")

    graph = {
        "A": ["B", "C"],
        "B": ["D", "E"],
        "C": ["F"],
        "D": [],
        "E": ["F"],
        "F": [],
    }

    print(f"BFS from A: {breadth_first_search(graph, 'A')}")


# =============================================================================
# 25. DEPTH-FIRST SEARCH
# =============================================================================

def depth_first_search(
    graph: dict[str, list[str]],
    start: str,
) -> list[str]:
    """
    Iterative depth-first traversal using an explicit stack.

    Time: O(V + E)
    Space: O(V)
    """
    if start not in graph:
        raise KeyError(f"Unknown start node: {start}")

    visited = set()
    stack = [start]
    order: list[str] = []

    while stack:
        node = stack.pop()

        if node in visited:
            continue

        visited.add(node)
        order.append(node)

        for neighbor in reversed(graph.get(node, [])):
            if neighbor not in visited:
                stack.append(neighbor)

    return order


def demonstrate_dfs() -> None:
    section("25. Depth-First Search")

    graph = {
        "A": ["B", "C"],
        "B": ["D", "E"],
        "C": ["F"],
        "D": [],
        "E": ["F"],
        "F": [],
    }

    print(f"DFS from A: {depth_first_search(graph, 'A')}")


# =============================================================================
# 26. SHORTEST PATH IN AN UNWEIGHTED GRAPH
# =============================================================================

def shortest_path_unweighted(
    graph: dict[str, list[str]],
    start: str,
    target: str,
) -> Optional[list[str]]:
    """
    Find a shortest path in an unweighted graph using BFS.

    BFS explores vertices in increasing distance from the source.
    """
    if start not in graph or target not in graph:
        raise KeyError("Both start and target must exist in the graph.")

    queue: deque[str] = deque([start])
    previous: dict[str, Optional[str]] = {start: None}

    while queue:
        node = queue.popleft()

        if node == target:
            break

        for neighbor in graph.get(node, []):
            if neighbor not in previous:
                previous[neighbor] = node
                queue.append(neighbor)

    if target not in previous:
        return None

    path: list[str] = []
    current: Optional[str] = target

    while current is not None:
        path.append(current)
        current = previous[current]

    path.reverse()
    return path


def demonstrate_shortest_path() -> None:
    section("26. Shortest Path Reasoning")

    graph = {
        "A": ["B", "C"],
        "B": ["D"],
        "C": ["D", "E"],
        "D": ["F"],
        "E": ["F"],
        "F": [],
    }

    print(f"Shortest path A -> F: {shortest_path_unweighted(graph, 'A', 'F')}")


# =============================================================================
# 27. VALIDATING EDGE CASES
# =============================================================================

def safe_average(values: list[float]) -> Optional[float]:
    """Return None for an empty input instead of dividing by zero."""
    if not values:
        return None

    return sum(values) / len(values)


def demonstrate_edge_cases() -> None:
    section("27. Edge Cases")

    cases = {
        "empty list": [],
        "single value": [42],
        "duplicates": [5, 5, 5],
        "negative values": [-5, -2, -9],
        "already sorted": [1, 2, 3, 4],
        "reverse sorted": [4, 3, 2, 1],
        "zero": [0],
    }

    for description, values in cases.items():
        print(f"{description:20}: {values}")

    print("\nEmpty average:")
    print(safe_average([]))

    print("\nTypical edge-case questions:")
    questions = [
        "Can the input be empty?",
        "Can there be exactly one element?",
        "Can values be negative?",
        "Can values be zero?",
        "Can duplicate values occur?",
        "Can the answer be impossible?",
        "Can the input be extremely large?",
        "Can values exceed normal integer ranges?",
        "What should invalid input do?",
    ]

    for question in questions:
        print(f"- {question}")


# =============================================================================
# 28. EXCEPTIONS AND INVALID INPUT
# =============================================================================

def divide_numbers(numerator: float, denominator: float) -> float:
    """
    Validate a division operation explicitly.

    Raising a meaningful exception is better than silently returning an
    incorrect result.
    """
    if denominator == 0:
        raise ZeroDivisionError("The denominator cannot be zero.")

    return numerator / denominator


def demonstrate_error_handling() -> None:
    section("28. Error Handling")

    valid_cases = [(10, 2), (9, 3), (-4, 2)]

    for numerator, denominator in valid_cases:
        print(f"{numerator} / {denominator} = "
              f"{divide_numbers(numerator, denominator)}")

    try:
        divide_numbers(10, 0)
    except ZeroDivisionError as error:
        print(f"Caught expected error: {error}")


# =============================================================================
# 29. ASSERTIONS AND TESTING
# =============================================================================

def test_restate_find_maximum() -> None:
    assert restate_find_maximum([1, 5, 3]) == 5
    assert restate_find_maximum([-5, -2, -8]) == -2
    assert restate_find_maximum([7]) == 7

    try:
        restate_find_maximum([])
    except ValueError:
        pass
    else:
        raise AssertionError("Empty input should raise ValueError.")


def test_binary_search() -> None:
    values = [1, 3, 5, 7, 9, 11]

    assert binary_search(values, 1) == 0
    assert binary_search(values, 11) == 5
    assert binary_search(values, 7) == 3
    assert binary_search(values, 8) == -1


def test_two_sum() -> None:
    cases = [
        ([2, 7, 11, 15], 9, (0, 1)),
        ([3, 2, 4], 6, (1, 2)),
        ([1, 2, 3], 10, None),
    ]

    for values, target, expected in cases:
        assert two_sum_hash_map(values, target) == expected


def test_interval_merging() -> None:
    intervals = [
        Interval(1, 4),
        Interval(2, 5),
        Interval(7, 9),
    ]

    expected = [
        Interval(1, 5),
        Interval(7, 9),
    ]

    assert merge_intervals(intervals) == expected


def run_unit_tests() -> None:
    section("29. Testing")

    tests: list[Callable[[], None]] = [
        test_restate_find_maximum,
        test_binary_search,
        test_two_sum,
        test_interval_merging,
    ]

    passed = 0

    for test in tests:
        test()
        print(f"PASS: {test.__name__}")
        passed += 1

    print(f"\n{passed}/{len(tests)} tests passed.")


# =============================================================================
# 30. DIFFERENTIAL TESTING
# =============================================================================

def differential_test_duplicate_detection() -> None:
    """
    Compare an optimized implementation against a simpler reference
    implementation over many generated cases.

    This is useful when the optimized implementation is harder to reason about.
    """
    section("30. Differential Testing")

    generated_cases: list[list[int]] = [
        [],
        [1],
        [1, 1],
        [1, 2, 3],
        [3, 2, 1, 3],
        [-1, -2, -3],
        [0, 0, 0],
        [5, -5, 5, -5],
    ]

    for values in generated_cases:
        expected = has_duplicate_brute_force(values)
        actual = has_duplicate_set(values)

        assert expected == actual
        print(f"PASS: {values} -> {actual}")


# =============================================================================
# 31. PROPERTY-BASED THINKING
# =============================================================================

def demonstrate_properties() -> None:
    section("31. Property-Based Thinking")

    print("Instead of testing only selected outputs, identify properties.")

    values = [4, 9, 1, 7, 2]

    original_max = restate_find_maximum(values)
    shuffled_values = list(reversed(values))
    reversed_max = restate_find_maximum(shuffled_values)

    print(f"Original values: {values}")
    print(f"Maximum: {original_max}")
    print(f"Reversed values: {shuffled_values}")
    print(f"Maximum after reversal: {reversed_max}")

    # Property: changing order does not change the maximum.
    assert original_max == reversed_max

    # Property: adding a smaller value does not lower the maximum.
    assert restate_find_maximum(values + [-100]) == original_max

    # Property: adding a larger value must make the maximum at least that value.
    assert restate_find_maximum(values + [100]) == 100

    print("Several useful invariants and properties passed.")


# =============================================================================
# 32. COMMON MISTAKE: OFF-BY-ONE ERRORS
# =============================================================================

def sum_range_inclusive(start: int, end: int) -> int:
    """
    Sum all integers from start through end, inclusive.

    range(start, end + 1) is necessary because Python's range excludes its
    upper bound.
    """
    if start > end:
        raise ValueError("start must not exceed end.")

    return sum(range(start, end + 1))


def demonstrate_off_by_one() -> None:
    section("32. Off-by-One Errors")

    print("Python range(1, 5) produces:", list(range(1, 5)))
    print("An inclusive 1..5 sequence is:", list(range(1, 6)))
    print("Inclusive sum 1..5:", sum_range_inclusive(1, 5))


# =============================================================================
# 33. COMMON MISTAKE: MUTATING INPUT UNEXPECTEDLY
# =============================================================================

def sorted_copy(values: list[int]) -> list[int]:
    """Return a sorted copy without changing the caller's list."""
    return sorted(values)


def demonstrate_mutation() -> None:
    section("33. Managing Mutation")

    values = [3, 1, 2]
    result = sorted_copy(values)

    print(f"Original list: {values}")
    print(f"Sorted copy:   {result}")

    assert values == [3, 1, 2]


# =============================================================================
# 34. COMMON MISTAKE: FLOATING-POINT COMPARISON
# =============================================================================

def demonstrate_floating_point() -> None:
    section("34. Floating-Point Edge Cases")

    result = 0.1 + 0.2

    print("0.1 + 0.2 =", result)
    print("Exact equality with 0.3:", result == 0.3)
    print("Approximate comparison:", isclose(result, 0.3))

    print("\nFloating-point values are represented approximately in binary.")
    print("Use suitable tolerances when exact decimal equality is not required.")


# =============================================================================
# 35. PERFORMANCE MEASUREMENT
# =============================================================================

def measure_runtime(
    function: Callable[..., object],
    *args: object,
) -> float:
    """Measure elapsed wall-clock time for a single function call."""
    start = perf_counter()
    function(*args)
    end = perf_counter()
    return end - start


def demonstrate_performance_measurement() -> None:
    section("35. Measuring Performance")

    values = list(range(1000))

    linear_time = measure_runtime(linear_search, values, 999)
    binary_time = measure_runtime(binary_search, values, 999)

    print(f"Linear search time: {linear_time:.8f} seconds")
    print(f"Binary search time: {binary_time:.8f} seconds")

    print("\nTiming results depend on hardware, Python version, input size,")
    print("system load, and implementation details.")
    print("Asymptotic complexity is therefore more useful for general reasoning.")


# =============================================================================
# 36. COMPLEXITY CALCULATOR CONCEPT
# =============================================================================

def complexity_examples() -> None:
    section("36. Complexity Analysis")

    examples = [
        ("Accessing a list element by index", "O(1)"),
        ("Scanning a list once", "O(n)"),
        ("Nested loops over the same n items", "O(n²)"),
        ("Binary search", "O(log n)"),
        ("Sorting using a comparison sort", "typically O(n log n)"),
        ("Generating every subset", "O(2ⁿ)"),
        ("Generating every permutation", "O(n!)"),
    ]

    for operation, complexity in examples:
        print(f"{operation:45} {complexity}")

    print("\nComplexity asks how resource usage grows as input size grows.")


# =============================================================================
# 37. SPACE COMPLEXITY
# =============================================================================

def demonstrate_space_complexity() -> None:
    section("37. Space Complexity")

    values = [1, 2, 3, 4, 5]

    print("An in-place operation may use O(1) auxiliary space.")
    print("Creating another list of n elements generally uses O(n) space.")

    copied = values.copy()

    print(f"Original: {values}")
    print(f"Copy:     {copied}")


# =============================================================================
# 38. TRADE-OFF: TIME VS SPACE
# =============================================================================

def membership_with_list(values: list[int], target: int) -> bool:
    return target in values


def membership_with_set(values: list[int], target: int) -> bool:
    return target in set(values)


def demonstrate_time_space_tradeoff() -> None:
    section("38. Time-Space Trade-offs")

    values = list(range(20))
    target = 19

    print("List membership:", membership_with_list(values, target))
    print("Set membership: ", membership_with_set(values, target))

    print("\nA set can make repeated membership operations faster on average,")
    print("but constructing and storing the set requires additional memory.")


# =============================================================================
# 39. PREFIX/SUFFIX REASONING
# =============================================================================

def product_except_self(values: list[int]) -> list[int]:
    """
    Return a[i] = product of all elements except values[i].

    This avoids division and handles zero values correctly.

    Time: O(n)
    Extra space: O(1) beyond the output array.
    """
    result = [1] * len(values)

    prefix_product = 1

    for index, value in enumerate(values):
        result[index] = prefix_product
        prefix_product *= value

    suffix_product = 1

    for index in range(len(values) - 1, -1, -1):
        result[index] *= suffix_product
        suffix_product *= values[index]

    return result


def demonstrate_prefix_suffix() -> None:
    section("39. Prefix and Suffix Reasoning")

    values = [1, 2, 3, 4]
    print(f"Values: {values}")
    print(f"Product except self: {product_except_self(values)}")

    values_with_zero = [1, 2, 0, 4]
    print(f"With zero: {values_with_zero}")
    print(f"Result:    {product_except_self(values_with_zero)}")


# =============================================================================
# 40. BINARY SEARCH ON AN ANSWER
# =============================================================================

def can_allocate_with_capacity(
    workloads: list[int],
    number_of_workers: int,
    capacity: int,
) -> bool:
    """
    Determine whether workloads can be divided among at most number_of_workers
    sequential groups where each group has total <= capacity.
    """
    if not workloads:
        return True

    workers_used = 1
    current_load = 0

    for workload in workloads:
        if workload > capacity:
            return False

        if current_load + workload <= capacity:
            current_load += workload
        else:
            workers_used += 1
            current_load = workload

            if workers_used > number_of_workers:
                return False

    return True


def minimum_capacity(workloads: list[int], number_of_workers: int) -> int:
    """
    Find the minimum capacity required to distribute sequential workloads.

    This demonstrates binary search over a numerical answer rather than
    directly searching an array.
    """
    if not workloads:
        return 0

    if number_of_workers <= 0:
        raise ValueError("number_of_workers must be positive.")

    lower = max(workloads)
    upper = sum(workloads)

    while lower < upper:
        middle = (lower + upper) // 2

        if can_allocate_with_capacity(
            workloads,
            number_of_workers,
            middle,
        ):
            upper = middle
        else:
            lower = middle + 1

    return lower


def demonstrate_binary_search_on_answer() -> None:
    section("40. Binary Search on the Answer")

    workloads = [7, 2, 5, 10, 8]
    workers = 2

    result = minimum_capacity(workloads, workers)

    print(f"Workloads: {workloads}")
    print(f"Workers:   {workers}")
    print(f"Minimum capacity: {result}")


# =============================================================================
# 41. DYNAMIC PROGRAMMING WITH A CLASSIC SUBSEQUENCE PROBLEM
# =============================================================================

def longest_common_subsequence(text_a: str, text_b: str) -> str:
    """
    Return one longest common subsequence.

    Unlike a substring, a subsequence does not need to occupy consecutive
    positions.

    Time: O(mn)
    Space: O(mn)
    """
    rows = len(text_a) + 1
    columns = len(text_b) + 1

    dp = [[""] * columns for _ in range(rows)]

    for i in range(1, rows):
        for j in range(1, columns):
            if text_a[i - 1] == text_b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + text_a[i - 1]
            else:
                left = dp[i][j - 1]
                up = dp[i - 1][j]
                dp[i][j] = left if len(left) >= len(up) else up

    return dp[-1][-1]


def demonstrate_lcs() -> None:
    section("41. Dynamic Programming: Longest Common Subsequence")

    a = "ABCBDAB"
    b = "BDCABA"

    result = longest_common_subsequence(a, b)

    print(f"First sequence:  {a}")
    print(f"Second sequence: {b}")
    print(f"One LCS:         {result}")
    print(f"LCS length:      {len(result)}")


# =============================================================================
# 42. RECURSIVE SEARCH WITH PRUNING
# =============================================================================

def combinations_with_target_sum(
    values: list[int],
    target: int,
) -> list[list[int]]:
    """
    Find combinations whose elements sum to target.

    Values are assumed non-negative for the pruning rule used here.

    The algorithm demonstrates:
    - recursive decomposition,
    - choice exploration,
    - pruning,
    - duplicate avoidance after sorting.
    """
    if any(value < 0 for value in values):
        raise ValueError("This implementation expects non-negative values.")

    values = sorted(values)
    result: list[list[int]] = []
    current: list[int] = []

    def backtrack(start: int, remaining: int) -> None:
        if remaining == 0:
            result.append(current.copy())
            return

        previous_value: Optional[int] = None

        for index in range(start, len(values)):
            value = values[index]

            if value == previous_value:
                continue

            if value > remaining:
                break

            current.append(value)
            backtrack(index + 1, remaining - value)
            current.pop()

            previous_value = value

    backtrack(0, target)
    return result


def demonstrate_pruning() -> None:
    section("42. Backtracking with Pruning")

    values = [2, 3, 6, 7]
    target = 9

    print(f"Values: {values}")
    print(f"Target: {target}")
    print(f"Combinations: {combinations_with_target_sum(values, target)}")


# =============================================================================
# 43. ALGORITHM SELECTION DECISION TREE
# =============================================================================

def algorithm_selection_guide() -> None:
    section("43. Algorithm Selection")

    guide = [
        ("Need to scan every element once?", "Consider a linear scan."),
        ("Need repeated exact membership checks?", "Consider a set or dictionary."),
        ("Input is sorted and search is repeated?", "Consider binary search."),
        ("Need contiguous-range optimization?", "Consider a sliding window."),
        ("Need range sums repeatedly?", "Consider prefix sums."),
        ("Need pair relationships in sorted data?", "Consider two pointers."),
        ("Need hierarchical graph traversal?", "Consider BFS or DFS."),
        ("Need shortest path in an unweighted graph?", "Consider BFS."),
        ("Need all possible choices?", "Consider backtracking."),
        ("Repeated subproblems occur?", "Consider memoization or DP."),
        ("Local choices have a provable global property?", "Consider greedy."),
        ("Need to group overlapping ranges?", "Sort intervals and merge."),
    ]

    for question, recommendation in guide:
        print(f"{question}\n  -> {recommendation}")


# =============================================================================
# 44. PROBLEM-SOLVING WORKFLOW
# =============================================================================

def problem_solving_workflow() -> None:
    section("44. A Complete Problem-Solving Workflow")

    steps = [
        "Read the problem carefully.",
        "Restate the problem in your own precise words.",
        "Identify inputs and outputs.",
        "Identify explicit and implicit constraints.",
        "Clarify assumptions.",
        "Create small examples.",
        "Include a normal case.",
        "Include the smallest valid case.",
        "Include the largest conceptual boundary.",
        "Include invalid cases if relevant.",
        "Try a simple brute-force solution.",
        "Verify the brute-force solution manually.",
        "Analyze time and space complexity.",
        "Look for repeated work.",
        "Look for useful data structures.",
        "Look for ordering, frequency, prefix, window, or pointer patterns.",
        "Consider whether sorting simplifies the problem.",
        "Consider whether a greedy strategy is provably valid.",
        "Consider dynamic programming when subproblems overlap.",
        "Implement the optimized solution.",
        "Compare it against the simpler solution.",
        "Test edge cases.",
        "Test invalid inputs.",
        "Measure performance when performance matters.",
        "Review readability, maintainability, and correctness.",
    ]

    for step_number, step in enumerate(steps, start=1):
        print(f"{step_number:2}. {step}")


# =============================================================================
# 45. COMPLETE EXAMPLE: FINDING THE BEST PAIR
# =============================================================================

def best_pair_brute_force(values: list[int]) -> Optional[tuple[int, int, int]]:
    """
    Find the pair with the largest sum.

    Returns:
        (first_index, second_index, sum)

    Brute force checks every pair.

    Time: O(n²)
    """
    if len(values) < 2:
        return None

    best: Optional[tuple[int, int, int]] = None

    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            current_sum = values[i] + values[j]

            if best is None or current_sum > best[2]:
                best = (i, j, current_sum)

    return best


def best_pair_sorted(values: list[int]) -> Optional[tuple[int, int, int]]:
    """
    Find the largest pair sum by observing that the two largest values form
    the optimal pair.

    Sorting is unnecessary for this exact task, but is demonstrated here to
    illustrate how a structural observation can lead to a simpler solution.

    Time: O(n log n)
    Space: O(n) for the sorted copy.
    """
    if len(values) < 2:
        return None

    ordered = sorted(enumerate(values), key=lambda item: item[1])
    first_index, first_value = ordered[-1]
    second_index, second_value = ordered[-2]

    return first_index, second_index, first_value + second_value


def best_pair_linear(values: list[int]) -> Optional[tuple[int, int, int]]:
    """
    Optimal one-pass solution.

    Time: O(n)
    Space: O(1)
    """
    if len(values) < 2:
        return None

    largest = (-inf, -1)
    second_largest = (-inf, -1)

    for index, value in enumerate(values):
        if value > largest[0]:
            second_largest = largest
            largest = (value, index)
        elif value > second_largest[0]:
            second_largest = (value, index)

    return (
        largest[1],
        second_largest[1],
        int(largest[0] + second_largest[0]),
    )


def demonstrate_complete_optimization() -> None:
    section("45. Complete Optimization Example")

    values = [12, -3, 25, 7, 19, 4]

    brute = best_pair_brute_force(values)
    sorted_solution = best_pair_sorted(values)
    linear = best_pair_linear(values)

    print(f"Values: {values}")
    print(f"Brute force: {brute}")
    print(f"Sorted:      {sorted_solution}")
    print(f"Linear:      {linear}")

    assert brute is not None
    assert sorted_solution is not None
    assert linear is not None

    assert brute[2] == sorted_solution[2] == linear[2]


# =============================================================================
# 46. MULTIPLE VALID SOLUTIONS AND CHOICE OF OUTPUT
# =============================================================================

def all_indices_of_maximum(values: list[int]) -> list[int]:
    """Return every index containing the maximum value."""
    if not values:
        return []

    maximum = max(values)
    return [index for index, value in enumerate(values) if value == maximum]


def demonstrate_output_contract() -> None:
    section("46. Output Contracts Matter")

    values = [4, 9, 2, 9, 7]

    print(f"Values: {values}")
    print(f"Maximum value: {max(values)}")
    print(f"All maximum indices: {all_indices_of_maximum(values)}")

    print("\nA problem asking for one maximum index is different from one asking")
    print("for every index containing the maximum. Read the output requirement")
    print("precisely before selecting an implementation.")


# =============================================================================
# 47. REAL-WORLD VALIDATION PIPELINE
# =============================================================================

@dataclass
class Transaction:
    transaction_id: str
    amount: float
    category: str


def validate_transactions(
    transactions: list[Transaction],
) -> list[Transaction]:
    """
    Validate transaction records.

    Production-oriented validation should reject malformed records before
    business calculations are performed.
    """
    seen_ids: set[str] = set()
    valid: list[Transaction] = []

    for transaction in transactions:
        if not transaction.transaction_id:
            raise ValueError("Transaction ID cannot be empty.")

        if transaction.transaction_id in seen_ids:
            raise ValueError(
                f"Duplicate transaction ID: {transaction.transaction_id}"
            )

        if transaction.amount < 0:
            raise ValueError("Transaction amount cannot be negative.")

        if not transaction.category:
            raise ValueError("Transaction category cannot be empty.")

        seen_ids.add(transaction.transaction_id)
        valid.append(transaction)

    return valid


def total_by_category(
    transactions: list[Transaction],
) -> dict[str, float]:
    """Aggregate validated transaction amounts by category."""
    validated = validate_transactions(transactions)

    totals: dict[str, float] = defaultdict(float)

    for transaction in validated:
        totals[transaction.category] += transaction.amount

    return dict(totals)


def demonstrate_real_world_pipeline() -> None:
    section("47. Real-World Validation and Aggregation")

    transactions = [
        Transaction("T001", 1200.0, "Technology"),
        Transaction("T002", 800.0, "Operations"),
        Transaction("T003", 450.0, "Technology"),
        Transaction("T004", 300.0, "Marketing"),
    ]

    print("Transactions:")
    for transaction in transactions:
        print(transaction)

    print(f"\nTotals by category: {total_by_category(transactions)}")


# =============================================================================
# 48. SECURITY-RELEVANT PROBLEM-SOLVING
# =============================================================================

def safe_parse_integer(text: str) -> Optional[int]:
    """
    Parse an integer without evaluating arbitrary Python expressions.

    For untrusted input, never use eval() merely to convert a value.
    """
    try:
        return int(text.strip())
    except ValueError:
        return None


def demonstrate_secure_input_handling() -> None:
    section("48. Security Considerations")

    inputs = ["42", "  -17 ", "3.14", "not-a-number"]

    for text in inputs:
        print(f"{text!r} -> {safe_parse_integer(text)}")

    print("\nSecurity-oriented problem solving includes:")
    print("- validating untrusted input,")
    print("- limiting resource consumption,")
    print("- avoiding unsafe evaluation,")
    print("- controlling file and network access,")
    print("- protecting sensitive information,")
    print("- and failing safely.")


# =============================================================================
# 49. RESOURCE LIMITS
# =============================================================================

def bounded_factorial(number: int, maximum_input: int = 1000) -> int:
    """
    Demonstrate explicit resource limits.

    A production system may need limits even when an algorithm is mathematically
    valid, because large inputs can consume excessive CPU or memory.
    """
    if number < 0:
        raise ValueError("number must be non-negative.")

    if number > maximum_input:
        raise ValueError(
            f"number exceeds the configured limit of {maximum_input}."
        )

    return factorial_iterative(number)


def demonstrate_resource_limits() -> None:
    section("49. Resource and Production Constraints")

    print(f"10! = {bounded_factorial(10)}")

    try:
        bounded_factorial(1001)
    except ValueError as error:
        print(f"Rejected oversized input: {error}")


# =============================================================================
# 50. DEBUGGING BY REDUCING THE INPUT
# =============================================================================

def debugging_example(values: list[int]) -> int:
    """
    Intentionally simple function used to demonstrate a debugging strategy:
    reduce the problem to the smallest input that reproduces the behavior.
    """
    result = 0

    for value in values:
        result += value

    return result


def demonstrate_debugging() -> None:
    section("50. Debugging Strategy")

    values = [10, -3, 7]
    print(f"Input: {values}")
    print(f"Result: {debugging_example(values)}")

    print("\nA practical debugging sequence:")
    print("1. Reproduce the problem reliably.")
    print("2. Reduce the input size.")
    print("3. Identify the first incorrect state.")
    print("4. Check assumptions at that point.")
    print("5. Fix the cause rather than only the visible symptom.")
    print("6. Add a regression test.")


# =============================================================================
# 51. REGRESSION TESTING
# =============================================================================

def demonstrate_regression_testing() -> None:
    section("51. Regression Testing")

    known_problematic_cases = [
        ([], None),
        ([1], 1),
        ([-5, -10], -5),
        ([3, 3, 3], 3),
        ([1, 100, 2], 100),
    ]

    for values, expected in known_problematic_cases:
        if expected is None:
            try:
                restate_find_maximum(values)
            except ValueError:
                print(f"PASS: empty input rejected")
            else:
                raise AssertionError("Expected empty input to fail.")
        else:
            actual = restate_find_maximum(values)
            assert actual == expected
            print(f"PASS: {values} -> {actual}")


# =============================================================================
# 52. TESTING THE BRUTE-FORCE BASELINE AGAINST THE OPTIMIZED VERSION
# =============================================================================

def compare_duplicate_algorithms() -> None:
    section("52. Baseline Versus Optimized Implementation")

    test_cases = [
        [1, 2, 3, 4, 5],
        [1, 2, 3, 4, 1],
        [9, 9],
        [],
        [-1, -2, -1],
        [0, 1, 2, 0],
    ]

    for values in test_cases:
        baseline = has_duplicate_brute_force(values)
        optimized = has_duplicate_set(values)

        if baseline != optimized:
            raise AssertionError(
                f"Implementations disagree for {values}: "
                f"{baseline} != {optimized}"
            )

        print(f"Verified: {values} -> {optimized}")


# =============================================================================
# 53. SIMPLE DECISION-MAKING MODEL
# =============================================================================

@dataclass
class CandidateSolution:
    name: str
    time_complexity: str
    space_complexity: str
    simplicity: str
    assumptions: str


def compare_candidate_solutions() -> None:
    section("53. Comparing Candidate Solutions")

    candidates = [
        CandidateSolution(
            name="Brute force duplicate detection",
            time_complexity="O(n²)",
            space_complexity="O(1)",
            simplicity="Very high",
            assumptions="None beyond equality.",
        ),
        CandidateSolution(
            name="Hash-set duplicate detection",
            time_complexity="O(n) average",
            space_complexity="O(n)",
            simplicity="High",
            assumptions="Hashing is available and acceptable.",
        ),
    ]

    print(
        f"{'Solution':35} {'Time':15} {'Space':15} "
        f"{'Simplicity':15}"
    )
    print("-" * 82)

    for candidate in candidates:
        print(
            f"{candidate.name:35} "
            f"{candidate.time_complexity:15} "
            f"{candidate.space_complexity:15} "
            f"{candidate.simplicity:15}"
        )

    print("\nAlgorithm selection is not simply 'fastest is always best.'")
    print("Correctness, assumptions, memory, maintainability, and operational")
    print("requirements also matter.")


# =============================================================================
# 54. COMPLETE MINI PROBLEM: FREQUENT ELEMENT
# =============================================================================

def most_frequent_value(values: list[int]) -> Optional[int]:
    """
    Return the most frequent value.

    If multiple values tie, return the one appearing first in the input.

    Time: O(n) average.
    Space: O(n).
    """
    if not values:
        return None

    counts = Counter(values)
    best_value = values[0]
    best_count = counts[best_value]

    for value in values[1:]:
        if counts[value] > best_count:
            best_value = value
            best_count = counts[value]

    return best_value


def demonstrate_frequency_problem() -> None:
    section("54. Complete Frequency-Counting Problem")

    examples = [
        [1, 2, 2, 3, 3, 3],
        [5, 5, 4, 4],
        [],
    ]

    for values in examples:
        print(f"{values} -> {most_frequent_value(values)}")


# =============================================================================
# 55. EDGE CASE MATRIX
# =============================================================================

def edge_case_matrix() -> None:
    section("55. Building an Edge-Case Matrix")

    matrix = [
        ("Empty", "[]", "Does the function reject or return a defined value?"),
        ("Singleton", "[x]", "Does indexing assume a second element?"),
        ("Minimum", "smallest valid value", "Does a boundary comparison work?"),
        ("Maximum", "largest valid value", "Can limits be exceeded?"),
        ("Duplicate", "[x, x]", "Does uniqueness logic behave correctly?"),
        ("All equal", "[x, x, x]", "Does selection logic handle ties?"),
        ("Negative", "[-x]", "Are sign assumptions valid?"),
        ("Zero", "[0]", "Does zero create division or multiplication issues?"),
        ("Already ordered", "sorted input", "Does the algorithm preserve correctness?"),
        ("Reverse ordered", "descending input", "Does ordering matter?"),
        ("Impossible", "no valid solution", "Is failure represented clearly?"),
    ]

    print(f"{'Case':20} {'Example':25} Question")
    print("-" * 78)

    for case, example, question in matrix:
        print(f"{case:20} {example:25} {question}")


# =============================================================================
# 56. VALIDATING ALGORITHM ASSUMPTIONS
# =============================================================================

def require_sorted(values: list[int]) -> None:
    """Explicitly validate the precondition required by binary search."""
    if values != sorted(values):
        raise ValueError("Binary search requires sorted input.")


def safe_binary_search(values: list[int], target: int) -> int:
    """Binary search with an explicit sorted-input precondition."""
    require_sorted(values)
    return binary_search(values, target)


def demonstrate_preconditions() -> None:
    section("56. Preconditions and Assumptions")

    values = [1, 3, 5, 7, 9]
    print(safe_binary_search(values, 7))

    try:
        safe_binary_search([5, 1, 3], 3)
    except ValueError as error:
        print(f"Rejected invalid precondition: {error}")


# =============================================================================
# 57. POSTCONDITIONS
# =============================================================================

def demonstrate_postconditions() -> None:
    section("57. Postconditions")

    values = [7, 2, 9, 4]
    result = sorted_copy(values)

    assert len(result) == len(values)
    assert result == sorted(values)

    print(f"Input:  {values}")
    print(f"Output: {result}")
    print("Postconditions verified.")


# =============================================================================
# 58. REASONING ABOUT IMPOSSIBILITY
# =============================================================================

def can_make_exact_sum(coins: list[int], amount: int) -> bool:
    """Return whether an exact amount can be formed."""
    return minimum_coins_dynamic_programming(coins, amount) is not None


def demonstrate_impossible_cases() -> None:
    section("58. Impossible Cases")

    examples = [
        ([2, 4], 7),
        ([3, 5], 8),
        ([5, 10], 3),
    ]

    for coins, amount in examples:
        print(
            f"Coins={coins}, amount={amount}, "
            f"possible={can_make_exact_sum(coins, amount)}"
        )


# =============================================================================
# 59. MATHEMATICAL REASONING
# =============================================================================

def arithmetic_progression_sum(first: int, difference: int, count: int) -> int:
    """
    Calculate an arithmetic progression sum using a mathematical formula.

    S = n / 2 * (2a + (n - 1)d)

    This replaces an O(n) loop with O(1) arithmetic.
    """
    if count < 0:
        raise ValueError("count cannot be negative.")

    if count == 0:
        return 0

    return count * (2 * first + (count - 1) * difference) // 2


def demonstrate_mathematical_optimization() -> None:
    section("59. Mathematical Optimization")

    first = 3
    difference = 4
    count = 100

    loop_result = sum(
        first + index * difference
        for index in range(count)
    )

    formula_result = arithmetic_progression_sum(
        first,
        difference,
        count,
    )

    print(f"Loop result:    {loop_result}")
    print(f"Formula result: {formula_result}")

    assert loop_result == formula_result


# =============================================================================
# 60. A COMPLETE PROBLEM-SOLVING TEMPLATE AS CODE
# =============================================================================

def solve_problem_template(values: list[int], target: int) -> Optional[tuple[int, int]]:
    """
    Generic study template for a pair-sum problem.

    Step 1: Validate.
    Step 2: State assumptions.
    Step 3: Choose a direct strategy.
    Step 4: Maintain useful state.
    Step 5: Return according to the output contract.
    """
    if not isinstance(values, list):
        raise TypeError("values must be a list.")

    if not all(isinstance(value, int) for value in values):
        raise TypeError("values must contain integers.")

    # State:
    # positions[value] = index where the value was previously seen.
    positions: dict[int, int] = {}

    for index, value in enumerate(values):
        needed = target - value

        if needed in positions:
            return positions[needed], index

        positions[value] = index

    return None


def demonstrate_problem_template() -> None:
    section("60. Complete Problem-Solving Template")

    examples = [
        ([2, 7, 11, 15], 9),
        ([3, 2, 4], 6),
        ([1, 2, 3], 10),
    ]

    for values, target in examples:
        print(
            f"values={values}, target={target} -> "
            f"{solve_problem_template(values, target)}"
        )


# =============================================================================
# 61. MAIN DEMONSTRATION
# =============================================================================

def run_all_demonstrations() -> None:
    """Run the complete educational program."""
    demonstrate_problem_specification()
    demonstrate_restatement()
    demonstrate_constraints()
    demonstrate_examples()
    demonstrate_decomposition()
    demonstrate_brute_force_and_optimization()
    demonstrate_invariant()
    demonstrate_linear_search()
    demonstrate_binary_search()
    demonstrate_sorting()
    demonstrate_hashing()
    demonstrate_two_sum()
    demonstrate_two_pointers()
    demonstrate_sliding_window()
    demonstrate_prefix_sums()
    demonstrate_recursion()
    demonstrate_backtracking()
    demonstrate_greedy_limitation()
    demonstrate_dynamic_programming()
    demonstrate_memoization()
    demonstrate_constraint_driven_design()
    demonstrate_intervals()
    demonstrate_stack_problem()
    demonstrate_bfs()
    demonstrate_dfs()
    demonstrate_shortest_path()
    demonstrate_edge_cases()
    demonstrate_error_handling()
    run_unit_tests()
    differential_test_duplicate_detection()
    demonstrate_properties()
    demonstrate_off_by_one()
    demonstrate_mutation()
    demonstrate_floating_point()
    demonstrate_performance_measurement()
    complexity_examples()
    demonstrate_space_complexity()
    demonstrate_time_space_tradeoff()
    demonstrate_prefix_suffix()
    demonstrate_binary_search_on_answer()
    demonstrate_lcs()
    demonstrate_pruning()
    algorithm_selection_guide()
    problem_solving_workflow()
    demonstrate_complete_optimization()
    demonstrate_output_contract()
    demonstrate_real_world_pipeline()
    demonstrate_secure_input_handling()
    demonstrate_resource_limits()
    demonstrate_debugging()
    demonstrate_regression_testing()
    compare_duplicate_algorithms()
    compare_candidate_solutions()
    demonstrate_frequency_problem()
    edge_case_matrix()
    demonstrate_preconditions()
    demonstrate_postconditions()
    demonstrate_impossible_cases()
    demonstrate_mathematical_optimization()
    demonstrate_problem_template()


# =============================================================================
# 62. PROGRAM ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    run_all_demonstrations()
