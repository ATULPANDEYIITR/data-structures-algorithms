"""
BIG-O NOTATION
==============

This script is a detailed learning resource on algorithmic complexity and
Big-O notation. It covers complexity analysis from basic principles to more
advanced reasoning, including:

    1. Why algorithmic complexity matters
    2. Time complexity and space complexity
    3. The meaning of Big-O notation
    4. Best-case, average-case, and worst-case analysis
    5. Constant complexity      O(1)
    6. Logarithmic complexity   O(log n)
    7. Linear complexity        O(n)
    8. Linearithmic complexity  O(n log n)
    9. Quadratic complexity     O(n²)
   10. Cubic complexity         O(n³)
   11. Exponential complexity   O(2^n)
   12. Factorial complexity     O(n!)
   13. Rules for simplifying complexity expressions
   14. Loop analysis
   15. Nested loops
   16. Consecutive operations
   17. Recursive algorithms
   18. Recurrence relations
   19. Comparing growth rates
   20. Practical examples and Python demonstrations

Big-O notation does not measure execution time in seconds. Instead, it
describes how the amount of computational work grows as the input size grows.

The examples in this script are designed for understanding complexity rather
than benchmarking precise hardware performance.
"""

import math
import time
from functools import lru_cache


# =============================================================================
# 1. THE FUNDAMENTAL IDEA OF ALGORITHM ANALYSIS
# =============================================================================

print("=" * 80)
print("BIG-O NOTATION AND ALGORITHMIC COMPLEXITY")
print("=" * 80)

"""
Suppose two algorithms solve exactly the same problem.

Algorithm A:
    Requires approximately 10 operations for every input.

Algorithm B:
    Requires approximately n² operations.

For a very small input, Algorithm B may appear acceptable. As n becomes large,
the difference becomes substantial.

For example:

    n = 10
        O(n²) -> approximately 100 units of work

    n = 1,000
        O(n²) -> approximately 1,000,000 units of work

    n = 1,000,000
        O(n²) -> approximately 1,000,000,000,000 units of work

The purpose of complexity analysis is to understand this growth.

Big-O notation focuses primarily on scalability rather than the exact running
time of one particular execution.
"""


# =============================================================================
# 2. INPUT SIZE
# =============================================================================

"""
Complexity is usually expressed as a function of input size.

The symbol:

    n

normally represents the size of the input.

Examples:

    Searching a list:
        n = number of elements

    Sorting an array:
        n = number of values

    Processing a string:
        n = number of characters

    Traversing a graph:
        n may represent vertices
        m may represent edges

Some algorithms depend on multiple input dimensions.

For example:

    O(n * m)

could describe an operation involving two independent collections.
"""


# =============================================================================
# 3. TIME COMPLEXITY
# =============================================================================

"""
Time complexity describes how the number of computational operations grows
relative to input size.

It does NOT necessarily mean:

    "This algorithm takes exactly n seconds."

Instead, it means:

    "The amount of work performed grows proportionally to n."

For example:

    for item in data:
        process(item)

If data contains n elements and process(item) requires constant work, the loop
performs work n times.

Therefore:

    Time Complexity = O(n)
"""


def demonstrate_linear_work(data):
    """Perform one constant-time operation for each element."""
    result = 0

    for value in data:
        result += value

    return result


# =============================================================================
# 4. SPACE COMPLEXITY
# =============================================================================

"""
Space complexity describes how additional memory requirements grow with input.

Example:

    def copy_list(data):
        result = []

        for item in data:
            result.append(item)

        return result

The new list grows with the size of the original input.

Therefore:

    Additional Space = O(n)

Now consider:

    total = 0

    for item in data:
        total += item

Only a fixed number of variables are used regardless of input size.

Therefore:

    Additional Space = O(1)

A common mistake is to confuse input storage with auxiliary space.

When analyzing an algorithm, auxiliary space usually refers to memory allocated
beyond the input itself.
"""


def constant_space_sum(data):
    total = 0

    for value in data:
        total += value

    return total


def linear_space_copy(data):
    copied = []

    for value in data:
        copied.append(value)

    return copied


# =============================================================================
# 5. WHAT BIG-O NOTATION REPRESENTS
# =============================================================================

"""
Big-O notation describes an asymptotic upper bound on growth.

Informally:

    O(f(n))

means that, for sufficiently large input sizes, the amount of work grows no
faster than a constant multiple of f(n).

For example:

    3n + 7

has complexity:

    O(n)

Why?

As n becomes very large, the linear term dominates the constant term.

For example:

    n = 10
        3n + 7 = 37

    n = 1,000
        3n + 7 = 3,007

    n = 1,000,000
        3n + 7 = 3,000,007

The additional 7 becomes insignificant relative to the growth of n.

Similarly:

    5n² + 2n + 100

becomes:

    O(n²)

because n² eventually dominates n and constant terms.
"""


# =============================================================================
# 6. CONSTANT FACTORS
# =============================================================================

"""
Big-O notation generally ignores constant multipliers.

Examples:

    O(2n)    -> O(n)
    O(10n)   -> O(n)
    O(0.5n)  -> O(n)

Similarly:

    O(1000)  -> O(1)

This does not mean constants never matter in practical software.

An O(n) algorithm with a very large constant factor may be slower than another
O(n) algorithm with a smaller constant factor for realistic input sizes.

Big-O is primarily a mathematical model of growth, not a complete replacement
for empirical performance measurement.
"""


# =============================================================================
# 7. DOMINANT TERMS
# =============================================================================

"""
When multiple terms appear, the fastest-growing term dominates for large n.

Examples:

    n² + n + 1        -> O(n²)
    n³ + n² + n       -> O(n³)
    n log n + n       -> O(n log n)
    2^n + n^100       -> O(2^n)

The dominant term determines asymptotic growth.
"""


# =============================================================================
# 8. CONSTANT TIME: O(1)
# =============================================================================

print("\n" + "=" * 80)
print("O(1): CONSTANT COMPLEXITY")
print("=" * 80)

"""
Constant complexity means that the amount of work does not grow with input size.

Examples:

    Accessing an array element by index
    Reading the first element
    Assigning a variable
    Arithmetic operations on fixed-size values

Example:
"""


def get_first_element(data):
    return data[0]


def swap_values(a, b):
    return b, a


"""
Even if the input contains:

    10 elements
    10,000 elements
    10,000,000 elements

the operation:

    data[0]

still accesses one indexed position.

Therefore:

    O(1)

Important distinction:

O(1) does not mean that the operation requires exactly one CPU instruction.

It means that its work is bounded independently of input size.
"""


# =============================================================================
# 9. LOGARITHMIC TIME: O(log n)
# =============================================================================

print("\n" + "=" * 80)
print("O(log n): LOGARITHMIC COMPLEXITY")
print("=" * 80)

"""
Logarithmic algorithms reduce the remaining problem by a constant factor during
each major step.

The most common example is binary search.

Suppose a sorted list contains 1,024 elements.

Binary search repeatedly divides the remaining search space approximately in
half:

    1024
    512
    256
    128
    64
    32
    16
    8
    4
    2
    1

Approximately:

    log₂(1024) = 10

major reductions are required.

The base of the logarithm is normally irrelevant in Big-O notation because:

    log_a(n) = log_b(n) / log_b(a)

The difference between logarithmic bases is a constant multiplier.
"""


def binary_search(data, target):
    """
    Search a sorted sequence using binary search.

    Time Complexity:
        O(log n)

    Space Complexity:
        O(1)
    """
    left = 0
    right = len(data) - 1

    while left <= right:
        middle = (left + right) // 2
        value = data[middle]

        if value == target:
            return middle

        if value < target:
            left = middle + 1
        else:
            right = middle - 1

    return -1


"""
Loop-based understanding of logarithmic growth:

    i = n

    while i > 1:
        i = i // 2

The value repeatedly decreases by half.

If k iterations occur:

    n / 2^k = 1

Therefore:

    n = 2^k

Taking logarithms:

    k = log₂(n)

Therefore:

    O(log n)
"""


def halve_until_one(n):
    steps = 0

    while n > 1:
        n //= 2
        steps += 1

    return steps


# =============================================================================
# 10. LINEAR TIME: O(n)
# =============================================================================

print("\n" + "=" * 80)
print("O(n): LINEAR COMPLEXITY")
print("=" * 80)

"""
Linear complexity occurs when the amount of work grows proportionally with the
number of input elements.

Example:

    for item in data:
        process(item)

If there are n elements, the loop performs n iterations.

Therefore:

    O(n)
"""


def linear_search(data, target):
    """
    Search elements sequentially.

    Worst-case time complexity:
        O(n)

    Best-case time complexity:
        O(1)

    Average-case time complexity:
        O(n)
    """
    for index, value in enumerate(data):
        if value == target:
            return index

    return -1


"""
The following operations are also consecutive linear operations:

    for item in data:
        operation_a(item)

    for item in data:
        operation_b(item)

The total work is:

    n + n = 2n

Big-O simplifies this to:

    O(n)
"""


# =============================================================================
# 11. LINEARITHMIC TIME: O(n log n)
# =============================================================================

print("\n" + "=" * 80)
print("O(n log n): LINEARITHMIC COMPLEXITY")
print("=" * 80)

"""
The term "linearithmic" describes complexity proportional to:

    n log n

This frequently occurs when:

    1. n elements are processed, and
    2. each processing stage involves logarithmic work

or when an algorithm recursively divides a problem while performing linear work
at each level.

Efficient comparison sorting algorithms such as merge sort have:

    O(n log n)

time complexity.
"""


def merge(left, right):
    """
    Merge two sorted lists.

    If the combined size is n, merging requires O(n) work.
    """
    result = []

    i = 0
    j = 0

    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])

    return result


def merge_sort(data):
    """
    Merge Sort

    Recurrence:

        T(n) = 2T(n/2) + O(n)

    This resolves to:

        O(n log n)

    Space Complexity:
        Typically O(n) additional memory.
    """
    if len(data) <= 1:
        return data

    middle = len(data) // 2

    left = merge_sort(data[:middle])
    right = merge_sort(data[middle:])

    return merge(left, right)


"""
Why O(n log n)?

Imagine a problem of size n.

Merge sort repeatedly divides the data:

Level 0:
    1 problem of size n

Level 1:
    2 problems of size n/2

Level 2:
    4 problems of size n/4

Eventually:

    approximately log n levels

At every level, the total merging work is proportional to n.

Therefore:

    n work per level × log n levels

    O(n log n)
"""


# =============================================================================
# 12. QUADRATIC TIME: O(n²)
# =============================================================================

print("\n" + "=" * 80)
print("O(n²): QUADRATIC COMPLEXITY")
print("=" * 80)

"""
Quadratic complexity frequently occurs when every element is compared or paired
with every other element.

Example:

    for i in range(n):
        for j in range(n):
            operation()

The outer loop executes n times.

For every outer iteration, the inner loop executes n times.

Total:

    n × n = n²

Therefore:

    O(n²)
"""


def compare_all_pairs(data):
    """
    Compare every element with every element.

    Time Complexity:
        O(n²)
    """
    count = 0

    for i in range(len(data)):
        for j in range(len(data)):
            count += 1

    return count


"""
Another common pattern:

    for i in range(n):
        for j in range(i + 1, n):
            operation()

The number of operations is approximately:

    n(n - 1) / 2

which expands to:

    (n² - n) / 2

Ignoring constants and lower-order terms:

    O(n²)

The fact that the inner loop does not always execute n times does not
necessarily change the asymptotic complexity.
"""


def unique_pair_count(n):
    count = 0

    for i in range(n):
        for j in range(i + 1, n):
            count += 1

    return count


# =============================================================================
# 13. CUBIC TIME: O(n³)
# =============================================================================

print("\n" + "=" * 80)
print("O(n³): CUBIC COMPLEXITY")
print("=" * 80)

"""
Cubic complexity often occurs with three nested loops.

Example:

    for i in range(n):
        for j in range(n):
            for k in range(n):
                operation()

The total number of operations is:

    n × n × n = n³

Therefore:

    O(n³)

Cubic algorithms become expensive rapidly as input grows.
"""


def cubic_example(n):
    count = 0

    for _ in range(n):
        for _ in range(n):
            for _ in range(n):
                count += 1

    return count


"""
For comparison:

    n = 10
        n³ = 1,000

    n = 100
        n³ = 1,000,000

    n = 1,000
        n³ = 1,000,000,000

This rapid increase explains why algorithms with high-degree polynomial
complexity become impractical for sufficiently large inputs.
"""


# =============================================================================
# 14. EXPONENTIAL TIME: O(2^n)
# =============================================================================

print("\n" + "=" * 80)
print("O(2^n): EXPONENTIAL COMPLEXITY")
print("=" * 80)

"""
Exponential complexity occurs when the number of possible computational paths
grows exponentially with input size.

A common recursive pattern is:

    T(n) = 2T(n - 1) + O(1)

Each function call creates approximately two more recursive calls.

Example: generating all subsets.

For a set containing n elements, each element has two possibilities:

    Include it
    Exclude it

Therefore, the total number of possible subsets is:

    2^n
"""


def generate_subsets(data):
    """
    Generate every subset of a collection.

    Number of subsets:
        2^n

    Time Complexity:
        At least exponential due to the number of generated results.
    """
    result = []

    def backtrack(index, current):
        if index == len(data):
            result.append(current.copy())
            return

        # Exclude the current element.
        backtrack(index + 1, current)

        # Include the current element.
        current.append(data[index])
        backtrack(index + 1, current)
        current.pop()

    backtrack(0, [])

    return result


"""
The growth of 2^n is extremely fast.

Examples:

    n = 10
        2^n = 1,024

    n = 20
        2^n = 1,048,576

    n = 30
        2^n = 1,073,741,824

    n = 50
        2^n = 1,125,899,906,842,624

Increasing input by one doubles the number of possibilities.
"""


# =============================================================================
# 15. FACTORIAL COMPLEXITY: O(n!)
# =============================================================================

print("\n" + "=" * 80)
print("O(n!): FACTORIAL COMPLEXITY")
print("=" * 80)

"""
Although exponential complexity is the primary advanced category discussed in
many introductory complexity comparisons, factorial complexity is important
because it grows even faster.

The number of permutations of n distinct elements is:

    n!

Examples:

    1! = 1
    2! = 2
    3! = 6
    4! = 24
    5! = 120
    10! = 3,628,800
    20! ≈ 2.43 × 10^18

Algorithms that examine every possible ordering often have factorial growth.
"""


def factorial(n):
    if n <= 1:
        return 1

    return n * factorial(n - 1)


# =============================================================================
# 16. ORDER OF GROWTH COMPARISON
# =============================================================================

print("\n" + "=" * 80)
print("COMPARING GROWTH RATES")
print("=" * 80)

"""
A common ordering from slower growth to faster growth is:

    O(1)
        <
    O(log n)
        <
    O(n)
        <
    O(n log n)
        <
    O(n²)
        <
    O(n³)
        <
    O(2^n)
        <
    O(n!)

This ordering describes asymptotic behavior.

For sufficiently large n:

    O(log n) grows slower than O(n)

    O(n) grows slower than O(n log n)

    O(n log n) grows slower than O(n²)

    O(n²) grows slower than O(n³)

    Polynomial functions grow slower than exponential functions.

The differences become more significant as n increases.
"""


def display_growth_values(max_n=20):
    print(f"\n{'n':>3} {'log2(n)':>12} {'n':>8} {'n log2(n)':>15} {'n²':>12} {'n³':>15} {'2^n':>15}")
    print("-" * 85)

    for n in range(1, max_n + 1):
        log_n = math.log2(n)
        n_log_n = n * log_n
        n_squared = n ** 2
        n_cubed = n ** 3
        exponential = 2 ** n

        print(
            f"{n:>3} "
            f"{log_n:>12.2f} "
            f"{n:>8} "
            f"{n_log_n:>15.2f} "
            f"{n_squared:>12} "
            f"{n_cubed:>15} "
            f"{exponential:>15}"
        )


display_growth_values()


# =============================================================================
# 17. BEST CASE, WORST CASE, AND AVERAGE CASE
# =============================================================================

print("\n" + "=" * 80)
print("BEST-CASE, AVERAGE-CASE, AND WORST-CASE ANALYSIS")
print("=" * 80)

"""
An algorithm may have different complexity depending on the input.

Consider linear search.

Best case:

    The target is the first element.

    Work required:
        1 comparison

    Complexity:
        O(1)

Worst case:

    The target is the final element or is absent.

    Work required:
        n comparisons

    Complexity:
        O(n)

Average case:

    The target is expected to be found somewhere within the sequence.

    Expected comparisons grow proportionally with n.

    Complexity:
        O(n)

When someone states the complexity of an algorithm without qualification,
worst-case complexity is often intended, but this depends on the context.
"""


# =============================================================================
# 18. CONSECUTIVE STATEMENTS
# =============================================================================

print("\n" + "=" * 80)
print("ADDING CONSECUTIVE COMPLEXITIES")
print("=" * 80)

"""
Suppose an algorithm performs:

    O(n)

followed by:

    O(n²)

The total is:

    O(n + n²)

The dominant term is n².

Therefore:

    O(n²)

Example:
"""


def consecutive_operations(data):
    # O(n)
    total = 0
    for value in data:
        total += value

    # O(n²)
    comparisons = 0
    for _ in data:
        for _ in data:
            comparisons += 1

    return total, comparisons


"""
The total complexity is:

    O(n + n²)

which simplifies to:

    O(n²)
"""


# =============================================================================
# 19. CONDITIONAL STATEMENTS
# =============================================================================

print("\n" + "=" * 80)
print("COMPLEXITY OF CONDITIONAL STATEMENTS")
print("=" * 80)

"""
Consider:

    if condition:
        O(n)
    else:
        O(n²)

For worst-case complexity, the branch requiring the greatest amount of work is
considered.

Therefore:

    O(n²)

The complexities of mutually exclusive branches are not normally multiplied.
Only one branch executes during one execution.
"""


def conditional_example(data, use_expensive_operation):
    if use_expensive_operation:
        # O(n²)
        count = 0
        for _ in data:
            for _ in data:
                count += 1
        return count

    # O(n)
    return sum(data)


# =============================================================================
# 20. SIMPLE LOOP ANALYSIS
# =============================================================================

print("\n" + "=" * 80)
print("ANALYZING LOOPS")
print("=" * 80)

"""
A loop should be analyzed according to how many times it executes.

Example:

    for i in range(n):
        operation()

Iterations:

    n

Complexity:

    O(n)
"""


def simple_loop(n):
    count = 0

    for _ in range(n):
        count += 1

    return count


"""
Now consider:

    for i in range(0, n, 2):
        operation()

The loop executes approximately n/2 times.

Complexity:

    O(n/2)

Ignoring constant factors:

    O(n)
"""


def step_two_loop(n):
    count = 0

    for _ in range(0, n, 2):
        count += 1

    return count


# =============================================================================
# 21. MULTIPLICATIVE LOOP PROGRESSION
# =============================================================================

"""
Consider:

    i = 1

    while i < n:
        i *= 2

The values are:

    1
    2
    4
    8
    16
    ...

After k iterations:

    2^k

The loop terminates when:

    2^k >= n

Therefore:

    k >= log₂(n)

Complexity:

    O(log n)
"""


def doubling_loop(n):
    count = 0
    value = 1

    while value < n:
        value *= 2
        count += 1

    return count


# =============================================================================
# 22. NESTED LOOPS WITH DIFFERENT RANGES
# =============================================================================

"""
Nested loops are not automatically O(n²).

The actual number of iterations must be examined.

Example:

    for i in range(n):
        for j in range(10):
            operation()

The outer loop executes n times.

The inner loop executes 10 times.

Total:

    10n

Therefore:

    O(n)

The inner loop is constant with respect to n.
"""


def linear_with_constant_inner_loop(n):
    count = 0

    for _ in range(n):
        for _ in range(10):
            count += 1

    return count


"""
Now consider:

    for i in range(n):
        j = 1

        while j < n:
            j *= 2

The outer loop is O(n).

The inner loop is O(log n).

Total:

    O(n log n)
"""


def linear_logarithmic_loop(n):
    count = 0

    for _ in range(n):
        value = 1

        while value < n:
            value *= 2
            count += 1

    return count


# =============================================================================
# 23. DEPENDENT NESTED LOOPS
# =============================================================================

print("\n" + "=" * 80)
print("DEPENDENT NESTED LOOPS")
print("=" * 80)

"""
Consider:

    for i in range(n):
        for j in range(i):
            operation()

The inner loop does not always execute n times.

The total work is:

    0 + 1 + 2 + 3 + ... + (n - 1)

This is an arithmetic series:

    n(n - 1) / 2

Asymptotically:

    O(n²)
"""


def triangular_loop(n):
    count = 0

    for i in range(n):
        for _ in range(i):
            count += 1

    return count


# =============================================================================
# 24. MULTIPLE INDEPENDENT INPUT VARIABLES
# =============================================================================

print("\n" + "=" * 80)
print("COMPLEXITY WITH MULTIPLE INPUT SIZES")
print("=" * 80)

"""
Suppose two arrays have different sizes:

    first has n elements
    second has m elements

Algorithm:

    for item in first:
        operation()

    for item in second:
        operation()

Complexity:

    O(n + m)

It should not automatically be written as O(n).

The two input sizes may vary independently.
"""


def process_two_lists(first, second):
    total = 0

    for value in first:
        total += value

    for value in second:
        total += value

    return total


"""
If every element of one collection is combined with every element of another:

    for x in first:
        for y in second:
            operation()

The complexity is:

    O(nm)
"""


def pair_two_lists(first, second):
    count = 0

    for _ in first:
        for _ in second:
            count += 1

    return count


# =============================================================================
# 25. RECURSION AND COMPLEXITY
# =============================================================================

print("\n" + "=" * 80)
print("RECURSIVE COMPLEXITY")
print("=" * 80)

"""
Recursive algorithms require analysis of:

    1. The work performed in each function call
    2. The number of recursive calls
    3. How quickly the input size changes

Example:
"""


def recursive_countdown(n):
    """
    T(n) = T(n - 1) + O(1)

    Complexity:
        O(n)
    """
    if n <= 0:
        return

    recursive_countdown(n - 1)


"""
There are approximately n recursive calls.

Each performs constant work.

Therefore:

    O(n)
"""


# =============================================================================
# 26. LOGARITHMIC RECURSION
# =============================================================================

def recursive_halving(n):
    """
    T(n) = T(n / 2) + O(1)

    Complexity:
        O(log n)
    """
    if n <= 1:
        return 1

    return 1 + recursive_halving(n // 2)


"""
Each call reduces the problem approximately by half.

The number of levels is logarithmic.
"""


# =============================================================================
# 27. EXPONENTIAL RECURSION
# =============================================================================

def naive_fibonacci(n):
    """
    Naive recursive Fibonacci.

    T(n) = T(n - 1) + T(n - 2) + O(1)

    The complexity is exponential.
    """
    if n <= 1:
        return n

    return naive_fibonacci(n - 1) + naive_fibonacci(n - 2)


"""
The repeated recursive calls produce an exponentially growing recursion tree.

The major inefficiency is repeated computation.

For example, calculating:

    Fibonacci(5)

causes smaller Fibonacci values to be recalculated multiple times.
"""


# =============================================================================
# 28. MEMOIZATION AND COMPLEXITY IMPROVEMENT
# =============================================================================

print("\n" + "=" * 80)
print("MEMOIZATION")
print("=" * 80)

"""
Memoization stores results that have already been calculated.

This can transform some exponential recursive algorithms into polynomial or
linear-time algorithms.

For Fibonacci:
"""


@lru_cache(maxsize=None)
def memoized_fibonacci(n):
    """
    Each Fibonacci value is calculated once.

    Time Complexity:
        O(n)

    Cache Space:
        O(n)
    """
    if n <= 1:
        return n

    return memoized_fibonacci(n - 1) + memoized_fibonacci(n - 2)


"""
The mathematical problem has not changed.

The computational strategy has changed by eliminating repeated work.

This illustrates an important principle:

Complexity often depends strongly on algorithm design rather than merely the
problem being solved.
"""


# =============================================================================
# 29. RECURSION DEPTH AND SPACE COMPLEXITY
# =============================================================================

"""
Recursive time complexity and recursive space complexity are separate.

Example:

    def countdown(n):
        if n == 0:
            return
        countdown(n - 1)

Time:

    O(n)

because approximately n calls execute.

Space:

    O(n)

because approximately n stack frames may exist simultaneously.

For binary recursive division with recursion depth log n:

    Space may be O(log n)

depending on how the recursive calls and data structures are implemented.
"""


# =============================================================================
# 30. COMMON COMPLEXITY EXPRESSIONS
# =============================================================================

print("\n" + "=" * 80)
print("SIMPLIFYING COMPLEXITY EXPRESSIONS")
print("=" * 80)

"""
Examples:

    O(7)
        -> O(1)

    O(3n)
        -> O(n)

    O(n + 10)
        -> O(n)

    O(n² + n)
        -> O(n²)

    O(n³ + n² + n)
        -> O(n³)

    O(n log n + n²)
        -> O(n²)

    O(2n + 5n)
        -> O(n)

    O(n² / 2)
        -> O(n²)

The process generally involves:

    1. Removing constant factors
    2. Removing lower-order terms
    3. Retaining the dominant growth term
"""


# =============================================================================
# 31. IMPORTANT PECULIARITY: NESTED LOOPS ARE NOT ALWAYS QUADRATIC
# =============================================================================

print("\n" + "=" * 80)
print("WHY NESTED LOOPS MUST BE ANALYZED CAREFULLY")
print("=" * 80)

"""
Consider:

    for i in range(n):
        for j in range(10):
            operation()

This is:

    O(10n) -> O(n)

Now:

    for i in range(n):
        for j in range(i):
            operation()

This is:

    O(n²)

Now:

    for i in range(n):
        j = 1

        while j < n:
            j *= 2

This is:

    O(n log n)

The presence of nested loops alone is insufficient to determine complexity.
The number of iterations of every loop must be analyzed.
"""


# =============================================================================
# 32. IMPORTANT PECULIARITY: SEQUENTIAL LOOPS ADD, NOT MULTIPLY
# =============================================================================

"""
Example:

    for i in range(n):
        operation()

    for j in range(n):
        operation()

This is:

    O(n) + O(n)

    = O(2n)

    = O(n)

Multiplication generally occurs when operations are nested in such a way that
one operation repeats for every execution of another.
"""


# =============================================================================
# 33. IMPORTANT PECULIARITY: EARLY TERMINATION
# =============================================================================

print("\n" + "=" * 80)
print("EARLY TERMINATION")
print("=" * 80)

"""
Algorithms can terminate before processing all input.

Example:

    for item in data:
        if item == target:
            return True

Best case:

    Target appears first.
    O(1)

Worst case:

    Target appears last or does not exist.
    O(n)

When analyzing worst-case Big-O, the longest possible execution path is usually
considered.
"""


def contains(data, target):
    for value in data:
        if value == target:
            return True

    return False


# =============================================================================
# 34. IMPORTANT PECULIARITY: AMORTIZED COMPLEXITY
# =============================================================================

print("\n" + "=" * 80)
print("AMORTIZED COMPLEXITY")
print("=" * 80)

"""
Some operations are occasionally expensive but inexpensive on average across a
large sequence of operations.

A dynamic array is a common conceptual example.

Appending an element is usually:

    O(1)

Occasionally, the underlying storage may need to grow.

When resizing occurs:

    Existing elements may need to be copied.

One individual append can therefore require:

    O(n)

work.

Across many append operations, the average cost per append can still be:

    Amortized O(1)

Amortized analysis studies the average cost across a sequence of operations
without relying on probability distributions.
"""


# =============================================================================
# 35. BIG-O VERSUS EXACT PERFORMANCE
# =============================================================================

"""
Big-O does not provide an exact runtime.

Two O(n) algorithms may perform differently because of:

    Hardware
    Compiler or interpreter implementation
    Memory locality
    Constant factors
    Cache behavior
    Input distribution
    Operating system scheduling
    Library implementations

For example:

    Algorithm A:
        1,000n operations

    Algorithm B:
        n² operations

For sufficiently small n, Algorithm B may be faster.

For sufficiently large n, the quadratic growth eventually dominates.

Therefore, asymptotic complexity is most useful for understanding scalability,
while benchmarking is useful for understanding practical performance in a
specific environment.
"""


# =============================================================================
# 36. PYTHON-SPECIFIC COMPLEXITY CONSIDERATIONS
# =============================================================================

print("\n" + "=" * 80)
print("COMMON PYTHON COMPLEXITY PATTERNS")
print("=" * 80)

"""
Python complexity analysis also requires understanding data structures.

Typical conceptual complexities include:

List indexing:

    data[index]

    approximately O(1)

List append:

    data.append(value)

    amortized O(1)

List membership:

    value in data

    O(n)

Set membership:

    value in my_set

    average-case O(1)

Dictionary lookup:

    mapping[key]

    average-case O(1)

Sorting:

    sorted(data)

    O(n log n) comparisons in the general case.

The exact behavior of language features depends on implementation details and
data characteristics, but choosing the appropriate data structure can change
the complexity of an application substantially.
"""


# =============================================================================
# 37. EXAMPLE: LIST MEMBERSHIP VERSUS SET MEMBERSHIP
# =============================================================================

def list_membership(data, target):
    """
    Linear membership search.

    Typical complexity:
        O(n)
    """
    return target in data


def set_membership(data, target):
    """
    Hash-based membership lookup.

    Typical average-case complexity:
        O(1)
    """
    lookup = set(data)
    return target in lookup


"""
There is an important analytical detail here.

Creating the set itself requires processing the input.

Therefore:

    lookup = set(data)

is generally O(n).

After construction, individual average-case membership checks are typically O(1).

If only one membership check is required, constructing a set may not always be
beneficial. If many membership checks are required, preprocessing can be useful.
"""


# =============================================================================
# 38. EXAMPLE: DUPLICATE DETECTION
# =============================================================================

print("\n" + "=" * 80)
print("ALGORITHM DESIGN AND COMPLEXITY")
print("=" * 80)

"""
Problem:

Determine whether a list contains duplicate values.

Approach 1:

Compare every pair.

Complexity:

    O(n²)

Approach 2:

Store previously seen values in a hash set.

Complexity:

    O(n) average case
"""


def has_duplicates_quadratic(data):
    """
    Pairwise comparison.

    Time Complexity:
        O(n²)

    Extra Space:
        O(1)
    """
    for i in range(len(data)):
        for j in range(i + 1, len(data)):
            if data[i] == data[j]:
                return True

    return False


def has_duplicates_hash(data):
    """
    Hash-based approach.

    Average Time Complexity:
        O(n)

    Extra Space:
        O(n)
    """
    seen = set()

    for value in data:
        if value in seen:
            return True

        seen.add(value)

    return False


"""
This example demonstrates a frequent algorithmic trade-off:

    Less time may require more memory.

The first algorithm:

    O(n²) time
    O(1) extra space

The second algorithm:

    O(n) average time
    O(n) extra space
"""


# =============================================================================
# 39. SORTING AND COMPLEXITY TRADE-OFFS
# =============================================================================

"""
Another approach to duplicate detection is sorting.

Steps:

    1. Sort the data
    2. Compare adjacent elements

Sorting:

    O(n log n)

Scanning:

    O(n)

Total:

    O(n log n + n)

Dominant term:

    O(n log n)
"""


def has_duplicates_sorted(data):
    sorted_data = sorted(data)

    for i in range(1, len(sorted_data)):
        if sorted_data[i] == sorted_data[i - 1]:
            return True

    return False


# =============================================================================
# 40. COMPLEXITY OF COMBINED ALGORITHMIC STAGES
# =============================================================================

print("\n" + "=" * 80)
print("COMBINING ALGORITHMIC STAGES")
print("=" * 80)

"""
Suppose an algorithm:

    1. Reads n elements
    2. Sorts them
    3. Performs a linear scan

Complexities:

    Reading:   O(n)
    Sorting:   O(n log n)
    Scanning:  O(n)

Total:

    O(n + n log n + n)

Dominant term:

    O(n log n)

A more expensive stage can dominate the total complexity.
"""


# =============================================================================
# 41. SPACE-TIME TRADE-OFFS
# =============================================================================

"""
Algorithms frequently involve trade-offs between computational time and memory.

Examples:

Using a set:

    More memory
    Faster membership testing

Memoization:

    More memory
    Avoids repeated computation

Precomputed lookup tables:

    Preprocessing and storage costs
    Faster later queries

The most efficient algorithm depends on the constraints of the actual problem.
An algorithm with excellent time complexity may still be unsuitable if its
memory requirements exceed available resources.
"""


# =============================================================================
# 42. INPUT REPRESENTATION MATTERS
# =============================================================================

print("\n" + "=" * 80)
print("INPUT REPRESENTATION MATTERS")
print("=" * 80)

"""
Complexity depends on the operations available for a data representation.

Searching for a value in:

    Unsorted list:
        O(n)

Sorted array with binary search:
        O(log n)

Hash set:
        Average O(1)

The computational problem may be conceptually identical:

    "Does this value exist?"

Yet the complexity changes because the underlying representation and algorithm
change.
"""


# =============================================================================
# 43. LOGARITHMS IN COMPUTATIONAL COMPLEXITY
# =============================================================================

"""
Logarithmic complexity often appears in:

    Binary search
    Balanced search trees
    Divide-and-conquer algorithms
    Repeated halving
    Hierarchical structures

Examples of logarithmic patterns:

    n -> n / 2

    n -> n / 3

    n -> n / 10

All represent:

    O(log n)

The logarithm base changes only by a constant factor.
"""


# =============================================================================
# 44. WHY n log n IS IMPORTANT
# =============================================================================

"""
The complexity O(n log n) is particularly important because it often represents
an efficient balance between processing every input element and organizing or
dividing the problem.

Comparison sorting has a theoretical lower bound of:

    Ω(n log n)

for general comparison-based sorting under standard assumptions.

This means that no comparison-based sorting algorithm can guarantee arbitrary
sorting in o(n log n) comparisons in the general case.

Algorithms such as merge sort and heap sort achieve O(n log n) worst-case time.
"""


# =============================================================================
# 45. BIG-O, BIG-OMEGA, AND BIG-THETA
# =============================================================================

print("\n" + "=" * 80)
print("ASYMPTOTIC NOTATION")
print("=" * 80)

"""
Big-O is part of a larger family of asymptotic notation.

Big-O:

    O(f(n))

Represents an asymptotic upper bound.

Big-Omega:

    Ω(f(n))

Represents an asymptotic lower bound.

Big-Theta:

    Θ(f(n))

Represents a tight asymptotic bound when both upper and lower bounds have the
same growth order.

For example, if an algorithm performs exactly:

    3n + 2

operations up to constant-level variations, its asymptotic growth is:

    O(n)
    Ω(n)
    Θ(n)

In informal programming discussions, "Big-O" is often used broadly when
describing complexity classes, even when Θ notation would be mathematically
more precise.
"""


# =============================================================================
# 46. FORMAL INTUITION OF BIG-O
# =============================================================================

"""
A function f(n) is O(g(n)) if there exist positive constants:

    c
    n₀

such that:

    0 <= f(n) <= c * g(n)

for every:

    n >= n₀

Example:

    f(n) = 3n + 7

We want to show:

    3n + 7 = O(n)

For sufficiently large n:

    3n + 7 <= 10n

when n is sufficiently large.

Therefore, a constant multiple of n bounds the function.

The exact constants are generally not the primary concern in ordinary algorithm
analysis. The important point is the long-term growth relationship.
"""


# =============================================================================
# 47. PRACTICAL GROWTH COMPARISON
# =============================================================================

def growth_comparison():
    print("\nGrowth comparison for selected input sizes:\n")

    values = [1, 2, 4, 8, 16, 20]

    for n in values:
        print(f"n = {n}")
        print(f"  O(1):       1")
        print(f"  O(log n):   {math.log2(n):.2f}")
        print(f"  O(n):       {n}")
        print(f"  O(n log n): {n * math.log2(n):.2f}")
        print(f"  O(n²):      {n ** 2}")
        print(f"  O(n³):      {n ** 3}")
        print(f"  O(2^n):     {2 ** n}")
        print()


growth_comparison()


# =============================================================================
# 48. EMPIRICAL TIMING DEMONSTRATION
# =============================================================================

print("\n" + "=" * 80)
print("EMPIRICAL TIMING AND THEORETICAL COMPLEXITY")
print("=" * 80)

"""
The following timing examples demonstrate an important distinction.

Theoretical complexity:

    Describes growth.

Empirical timing:

    Measures actual execution in one environment.

Timing results can vary between computers and executions. Therefore, measured
seconds should not be interpreted as mathematical proof of complexity.
"""


def measure_execution(function, *args):
    start = time.perf_counter()
    result = function(*args)
    end = time.perf_counter()

    return result, end - start


def linear_operation(n):
    total = 0

    for i in range(n):
        total += i

    return total


def quadratic_operation(n):
    total = 0

    for _ in range(n):
        for _ in range(n):
            total += 1

    return total


for size in [100, 500, 1000]:
    _, linear_time = measure_execution(linear_operation, size)

    print(
        f"Linear operation, n={size:<5}: "
        f"{linear_time:.8f} seconds"
    )


"""
Quadratic timing is demonstrated using smaller values because work grows much
faster.
"""

for size in [50, 100, 200]:
    _, quadratic_time = measure_execution(quadratic_operation, size)

    print(
        f"Quadratic operation, n={size:<5}: "
        f"{quadratic_time:.8f} seconds"
    )


# =============================================================================
# 49. COMMON ERRORS IN BIG-O ANALYSIS
# =============================================================================

print("\n" + "=" * 80)
print("COMMON ERRORS IN COMPLEXITY ANALYSIS")
print("=" * 80)

"""
Error 1: Counting source-code lines.

Complexity depends on execution frequency, not the number of written lines.

A single loop statement can execute millions of times.

--------------------------------------------------------------------

Error 2: Assuming every nested loop is O(n²).

The ranges and dependencies of the loops must be analyzed.

--------------------------------------------------------------------

Error 3: Multiplying consecutive loops.

Consecutive operations generally add:

    O(n) + O(n)

rather than multiply.

--------------------------------------------------------------------

Error 4: Treating O(1) as instantaneous.

Constant complexity means independent of input size. It does not imply zero
runtime.

--------------------------------------------------------------------

Error 5: Ignoring preprocessing.

If building a data structure costs O(n), that cost matters unless the analysis
explicitly concerns only subsequent operations.

--------------------------------------------------------------------

Error 6: Ignoring output size.

An algorithm that generates 2^n outputs cannot generally run in polynomial time
because writing the output itself requires exponential work.

--------------------------------------------------------------------

Error 7: Assuming faster asymptotic complexity is always faster for small input.

Constant factors and implementation details can dominate for small n.
"""


# =============================================================================
# 50. ANALYZING A REALISTIC EXAMPLE
# =============================================================================

print("\n" + "=" * 80)
print("COMPLETE ALGORITHM ANALYSIS EXAMPLE")
print("=" * 80)


def analyze_data(data):
    """
    Step 1:
        Copy the data
        O(n)

    Step 2:
        Sort the copy
        O(n log n)

    Step 3:
        Scan the sorted data
        O(n)

    Total:
        O(n + n log n + n)

    Simplified:
        O(n log n)
    """
    copied = list(data)

    copied.sort()

    duplicates = []

    for i in range(1, len(copied)):
        if copied[i] == copied[i - 1]:
            duplicates.append(copied[i])

    return duplicates


# =============================================================================
# 51. ADVANCED VIEW: ASYMPTOTIC ANALYSIS IGNORES FINITE DETAILS
# =============================================================================

"""
Big-O is concerned with behavior as:

    n -> infinity

Therefore, differences that remain bounded or differ only by constant factors
are intentionally abstracted.

For example:

    1000n
    n

belong to the same asymptotic complexity class:

    O(n)

But:

    n
    n²

do not belong to the same class because their ratio changes without bound as n
increases.

This abstraction makes Big-O useful for comparing algorithms independently of a
specific machine or exact implementation.
"""


# =============================================================================
# 52. POLYNOMIAL VERSUS EXPONENTIAL GROWTH
# =============================================================================

print("\n" + "=" * 80)
print("POLYNOMIAL AND EXPONENTIAL GROWTH")
print("=" * 80)

"""
Polynomial complexity includes:

    O(n)
    O(n²)
    O(n³)
    O(n^k)

where k is a fixed constant.

Exponential complexity includes:

    O(2^n)
    O(3^n)
    O(c^n)

where c is a constant greater than 1.

For sufficiently large n, exponential functions grow faster than any fixed
polynomial.

This distinction is central in computational feasibility.

An O(n³) algorithm may be expensive but still practical for moderate input
sizes.

An O(2^n) algorithm can become impractical even for relatively small increases
in input size.
"""


# =============================================================================
# 53. FINAL EXECUTABLE EXAMPLES
# =============================================================================

print("\n" + "=" * 80)
print("EXECUTABLE EXAMPLES")
print("=" * 80)

sample = [5, 2, 8, 1, 9, 3, 7, 4, 6]

print("\nSample data:")
print(sample)

print("\nConstant-time access:")
print(get_first_element(sample))

print("\nLinear search for 7:")
print(linear_search(sample, 7))

print("\nBinary search requires sorted input:")
sorted_sample = sorted(sample)
print(sorted_sample)
print(binary_search(sorted_sample, 7))

print("\nMerge sort:")
print(merge_sort(sample))

print("\nPair count for n = 5:")
print(unique_pair_count(5))

print("\nTriangular loop operations for n = 5:")
print(triangular_loop(5))

print("\nSteps required to repeatedly halve 1024:")
print(halve_until_one(1024))

print("\nSteps required to repeatedly double until reaching 1024:")
print(doubling_loop(1024))

print("\nSubset count for [1, 2, 3]:")
subsets = generate_subsets([1, 2, 3])
print(len(subsets))

print("\nNaive Fibonacci example:")
print(naive_fibonacci(10))

print("\nMemoized Fibonacci example:")
print(memoized_fibonacci(10))

print("\nDuplicate detection:")
duplicate_data = [1, 2, 3, 4, 2]

print("Quadratic approach:", has_duplicates_quadratic(duplicate_data))
print("Hash-based approach:", has_duplicates_hash(duplicate_data))
print("Sorting approach:", has_duplicates_sorted(duplicate_data))

print("\n" + "=" * 80)
print("END OF BIG-O NOTATION SCRIPT")
print("=" * 80)
