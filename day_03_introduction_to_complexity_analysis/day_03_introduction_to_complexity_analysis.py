"""
===============================================================
INTRODUCTION TO COMPLEXITY ANALYSIS
===============================================================

Topic:
    Learn why algorithm efficiency matters and understand:
    - Time Complexity
    - Space Complexity
    - Best Case
    - Average Case
    - Worst Case
    - Big-O, Big-Theta, Big-Omega
    - Common complexity classes
    - Input-size analysis
    - Loops and nested loops
    - Recursion
    - Recurrence relations
    - Searching and sorting examples
    - Auxiliary space
    - Time-space trade-offs
    - Amortized analysis
    - Practical benchmarking
    - Complexity of Python data structures
    - Advanced complexity reasoning

Goal:
    Build an intuition for analyzing algorithms instead of merely
    memorizing Big-O notation.

IMPORTANT:
    Complexity analysis describes how resource requirements GROW
    as input size grows. It is not simply a measurement of how
    many seconds a program takes on one particular machine.

===============================================================
1. WHAT IS AN ALGORITHM?
===============================================================

An algorithm is a finite, well-defined sequence of steps used to
solve a problem.

Example:

Problem:
    Find whether a number exists in a list.

Simple algorithm:
    1. Start from the first element.
    2. Compare it with the target.
    3. If equal, return True.
    4. Otherwise continue.
    5. If the list ends, return False.

An algorithm can be correct but inefficient.

Example:

    [1, 2, 3, 4, 5, ..., 1_000_000]

Searching one element at a time may require many comparisons.

This leads to an important question:

    "How efficiently does this algorithm use computational
     resources as the input becomes larger?"

That is the purpose of complexity analysis.


===============================================================
2. WHY DOES ALGORITHM EFFICIENCY MATTER?
===============================================================

Suppose Algorithm A takes approximately:

    n operations

and Algorithm B takes:

    n^2 operations

For n = 10:

    A -> approximately 10 operations
    B -> approximately 100 operations

For n = 1,000:

    A -> approximately 1,000 operations
    B -> approximately 1,000,000 operations

For n = 1,000,000:

    A -> approximately 1,000,000 operations
    B -> approximately 1,000,000,000,000 operations

The difference becomes enormous as n grows.

This is why algorithmic efficiency matters.

A program that works perfectly for 100 records may become unusable
for 100 million records.

Complexity analysis helps us predict scalability.


===============================================================
3. WHAT IS INPUT SIZE?
===============================================================

Complexity is usually expressed in terms of input size.

We normally call the input size:

    n

Examples:

    List of 10 elements:
        n = 10

    List of 1,000 elements:
        n = 1,000

    String containing 500 characters:
        n = 500

    Matrix with n rows and n columns:
        input contains approximately n^2 elements

For multiple inputs, we may use different variables.

Example:

    Matrix A has n rows and m columns.

An operation that examines every element takes:

    O(nm)

not necessarily:

    O(n^2)

The correct definition of n depends on the problem.


===============================================================
4. WHAT IS COMPLEXITY ANALYSIS?
===============================================================

Complexity analysis studies the resources required by an algorithm
as the size of its input increases.

The two most common resources are:

    1. Time
    2. Space

Therefore:

    Time Complexity
        How the number of computational steps grows.

    Space Complexity
        How the amount of memory usage grows.

Example:

    for x in numbers:
        print(x)

If numbers contains n elements, the loop executes n times.

Time complexity:

    O(n)

If no significant additional data structure grows with n,
auxiliary space can be:

    O(1)


===============================================================
5. TIME COMPLEXITY
===============================================================

Time complexity describes how the amount of computation grows
with input size.

We normally do NOT measure time as:

    0.0023 seconds
    0.0047 seconds
    2.31 milliseconds

because those measurements depend on:

    - CPU
    - RAM
    - programming language
    - compiler/interpreter
    - operating system
    - background processes
    - implementation details

Instead, we study the growth rate.

For example:

    T(n) = 3n + 10

is linear.

We represent its asymptotic growth as:

    O(n)


===============================================================
6. BASIC OPERATION COUNTING
===============================================================

Consider:

    x = 10

This is approximately constant work.

Complexity:

    O(1)

Consider:

    for i in range(n):
        print(i)

The loop runs n times.

Complexity:

    O(n)

Consider:

    for i in range(n):
        for j in range(n):
            print(i, j)

The outer loop runs n times.

For every outer iteration, the inner loop runs n times.

Total:

    n * n = n^2

Complexity:

    O(n^2)


===============================================================
7. CONSTANT COMPLEXITY: O(1)
===============================================================

O(1) means constant-time growth.

Example:

    def get_first(items):
        return items[0]

Whether the list contains:

    10 elements
    1,000 elements
    1,000,000 elements

the operation accesses one element.

Therefore:

    O(1)

Another example:

    def get_last(items):
        return items[-1]

For Python lists, this is also:

    O(1)


===============================================================
8. LINEAR COMPLEXITY: O(n)
===============================================================

Linear complexity means work grows approximately in direct
proportion to input size.

Example:

    def find_maximum(numbers):
        maximum = numbers[0]

        for number in numbers:
            if number > maximum:
                maximum = number

        return maximum

For n elements:

    approximately n comparisons

Therefore:

    O(n)


===============================================================
9. QUADRATIC COMPLEXITY: O(n^2)
===============================================================

Quadratic complexity occurs when work grows approximately as
the square of the input size.

Example:

    def print_all_pairs(items):
        for first in items:
            for second in items:
                print(first, second)

For n elements:

    n * n = n^2

Therefore:

    O(n^2)


===============================================================
10. CUBIC COMPLEXITY: O(n^3)
===============================================================

Three nested loops often produce cubic complexity.

Example:

    def triple_loop(n):
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    pass

Number of iterations:

    n * n * n

Therefore:

    O(n^3)

Polynomial algorithms become increasingly expensive as n grows.


===============================================================
11. LOGARITHMIC COMPLEXITY: O(log n)
===============================================================

A logarithmic algorithm reduces the remaining problem by a
constant factor at each step.

The classic example is binary search.

Suppose a sorted list contains:

    1,000,000 elements

Instead of checking every element, binary search repeatedly
cuts the search space approximately in half.

Conceptually:

    1,000,000
      500,000
      250,000
      125,000
      ...
      1

The number of steps grows approximately as:

    log2(n)

Therefore:

    O(log n)


===============================================================
12. BINARY SEARCH
===============================================================
"""

def binary_search(sorted_items, target):
    """
    Binary search requires sorted input.

    Time:
        Best case    -> O(1)
        Average case -> O(log n)
        Worst case   -> O(log n)

    Auxiliary space:
        O(1) for this iterative implementation.
    """

    left = 0
    right = len(sorted_items) - 1

    while left <= right:
        middle = (left + right) // 2

        if sorted_items[middle] == target:
            return middle

        if sorted_items[middle] < target:
            left = middle + 1
        else:
            right = middle - 1

    return -1


"""
===============================================================
13. LINEAR SEARCH VS BINARY SEARCH
===============================================================

Linear search:

    O(n)

Binary search:

    O(log n)

But binary search has a requirement:

    The data must be sorted.

This illustrates an important principle:

    A faster algorithm may require additional assumptions,
    preprocessing, memory, or complexity in implementation.

Algorithm selection depends on the complete problem context.


===============================================================
14. EXPONENTIAL COMPLEXITY: O(2^n)
===============================================================

Exponential complexity grows extremely rapidly.

Example:

    2^n

Values:

    n = 10       -> 1,024
    n = 20       -> 1,048,576
    n = 30       -> 1,073,741,824
    n = 40       -> 1,099,511,627,776

A naive recursive Fibonacci implementation is a common
educational example.

It repeatedly solves overlapping subproblems.

"""


def fibonacci_naive(n):
    """
    Educational example.

    Time:
        Approximately exponential.
        More precisely, Θ(phi^n) for the standard recurrence,
        where phi is the golden ratio.

    Auxiliary recursion stack:
        O(n)
    """

    if n <= 1:
        return n

    return fibonacci_naive(n - 1) + fibonacci_naive(n - 2)


"""
===============================================================
15. FACTORIAL COMPLEXITY: O(n!)
===============================================================

Factorial growth is even faster than exponential growth.

Examples:

    5!  = 120
    10! = 3,628,800
    15! = 1,307,674,368,000
    20! = 2,432,902,008,176,640,000

Problems involving trying every possible permutation can have
factorial complexity.

Example:

    Traveling Salesperson Problem (brute force)

If n cities are considered, brute-force permutation search can
require approximately:

    O(n!)

This becomes infeasible very quickly.


===============================================================
16. COMMON COMPLEXITY CLASSES
===============================================================

From generally more scalable to less scalable:

    O(1)
    O(log n)
    O(n)
    O(n log n)
    O(n^2)
    O(n^3)
    O(2^n)
    O(n!)

This is a rough growth hierarchy.

Important:

    Real performance also depends on constants, hardware,
    implementation, input distribution, and practical constraints.

Still, asymptotic growth is extremely useful for understanding
scalability.


===============================================================
17. O(n log n)
===============================================================

O(n log n) is extremely common in efficient sorting algorithms.

Examples include:

    Merge sort
    Heap sort
    Average-case quicksort

The pattern often comes from:

    log n levels

with approximately:

    n work

at each level.

Therefore:

    n * log n

Example:

    Merge sort

The list is repeatedly divided:

    n
    n/2 + n/2
    n/4 + n/4 + ...
    ...

The recursion has approximately log n levels.

Each level processes approximately n elements.

Therefore:

    O(n log n)


===============================================================
18. BEST CASE
===============================================================

Best-case complexity describes the most favorable input condition
for an algorithm.

Example:

    Linear search:

        [10, 20, 30, 40, 50]

Search for:

    10

The first element is the target.

Only one comparison is required.

Best-case time:

    O(1)


===============================================================
19. WORST CASE
===============================================================

Worst-case complexity describes the most unfavorable input
condition.

For linear search:

    [10, 20, 30, 40, 50]

Search for:

    50

or a value that does not exist.

The algorithm may inspect every element.

Worst-case time:

    O(n)


===============================================================
20. AVERAGE CASE
===============================================================

Average-case complexity describes expected performance across
a defined distribution of inputs.

For linear search, if the target is equally likely to appear
at any position, the expected number of comparisons is roughly:

    (n + 1) / 2

Asymptotically:

    Θ(n)

Important:

    Average-case analysis requires assumptions about the input
    distribution.

Without a probability model, "average case" can be ambiguous.


===============================================================
21. BEST, AVERAGE AND WORST CASE SUMMARY
===============================================================

For linear search:

    Best:
        O(1)

    Average:
        O(n)

    Worst:
        O(n)

For binary search:

    Best:
        O(1)

    Average:
        O(log n)

    Worst:
        O(log n)

Understanding all three gives a much better picture than
memorizing only one Big-O value.


===============================================================
22. BIG-O NOTATION
===============================================================

Big-O describes an asymptotic upper bound.

Informally:

    "The algorithm does not grow faster than this order,
     ignoring constant factors and lower-order terms."

Example:

    T(n) = 3n + 100

We simplify:

    O(n)

Why?

Because for sufficiently large n, the linear term dominates
the constant.


===============================================================
23. BIG-OMEGA: Ω
===============================================================

Big-Omega describes an asymptotic lower bound.

Example:

    T(n) = 3n + 100

can also be described as:

    Ω(n)

because its growth is at least linear asymptotically.


===============================================================
24. BIG-THETA: Θ
===============================================================

Big-Theta describes a tight asymptotic bound.

If:

    T(n) = 3n + 100

then:

    Θ(n)

is the strongest standard asymptotic characterization.

In many educational discussions:

    O(n)

is used when people simply mean the overall asymptotic
complexity.

Strictly speaking:

    O(n)
and
    Θ(n)

are not identical mathematical concepts.


===============================================================
25. CONSTANT FACTORS
===============================================================

Suppose:

    T(n) = 5n

and another algorithm:

    T(n) = 100n

Both are:

    O(n)

Asymptotic notation ignores constant multipliers.

But in real systems, constants matter.

For example:

    5n

may be substantially faster than:

    100n

for practical input sizes.

Therefore:

    Big-O is excellent for scalability analysis,
    but it is not a complete performance prediction.


===============================================================
26. DROP LOWER-ORDER TERMS
===============================================================

Suppose:

    T(n) = n^2 + 10n + 500

The dominant term is:

    n^2

Therefore:

    O(n^2)

For very large n, the quadratic term dominates the linear
and constant terms.


===============================================================
27. SUMMING SEQUENTIAL OPERATIONS
===============================================================

Consider:

    for i in range(n):
        pass

    for j in range(n):
        pass

First loop:

    O(n)

Second loop:

    O(n)

Total:

    O(n) + O(n)
    = O(2n)
    = O(n)

Sequential loops generally add their complexities.


===============================================================
28. MULTIPLYING NESTED COMPLEXITIES
===============================================================

Consider:

    for i in range(n):
        for j in range(n):
            pass

Outer:

    O(n)

Inner:

    O(n)

Nested work:

    O(n) * O(n)
    = O(n^2)


===============================================================
29. DIFFERENT INPUT SIZES
===============================================================

Suppose:

    for x in list_a:
        for y in list_b:
            pass

Let:

    len(list_a) = n
    len(list_b) = m

Then:

    O(nm)

Do NOT automatically write:

    O(n^2)

unless:

    n and m represent the same scale.


===============================================================
30. LOOP THAT DOUBLES EACH TIME
===============================================================

Consider:

    i = 1

    while i < n:
        i *= 2

Values:

    1
    2
    4
    8
    16
    ...

How many iterations?

Approximately:

    log2(n)

Therefore:

    O(log n)


===============================================================
31. LOOP THAT HALVES EACH TIME
===============================================================

Consider:

    i = n

    while i > 1:
        i //= 2

Again, approximately:

    log2(n)

iterations.

Therefore:

    O(log n)


===============================================================
32. TWO POINTER TECHNIQUE
===============================================================

Some algorithms use two pointers and still run in O(n).

Example:

    left = 0
    right = len(items) - 1

    while left < right:
        ...
        left += 1
        right -= 1

Even though there are two variables moving, the total number
of pointer movements is proportional to n.

Therefore:

    O(n)

Having multiple variables does not automatically mean O(n^2).


===============================================================
33. AMORTIZED ANALYSIS
===============================================================

Amortized analysis studies the average cost of operations across
a sequence of operations.

A single operation may be expensive while the overall sequence
remains efficient.

Python list append is a classic conceptual example.

Most appends are approximately:

    O(1)

Occasionally, the underlying dynamic array must resize and copy
elements.

That particular operation can cost:

    O(n)

But across many appends, the amortized cost is:

    O(1)

Amortized complexity is different from average-case analysis.

Average-case analysis typically uses a probability distribution.

Amortized analysis considers the total cost of a sequence of
operations without requiring randomness.


===============================================================
34. SPACE COMPLEXITY
===============================================================

Space complexity describes how memory requirements grow with
input size.

Example:

    def copy_list(items):
        result = []

        for item in items:
            result.append(item)

        return result

If there are n items, result contains n items.

Auxiliary space:

    O(n)


===============================================================
35. AUXILIARY SPACE
===============================================================

Auxiliary space usually refers to additional memory used by
the algorithm, excluding the input itself.

Example:

    def find_maximum(numbers):
        maximum = numbers[0]

        for number in numbers:
            if number > maximum:
                maximum = number

        return maximum

Additional variables:

    maximum
    number

These do not grow with n.

Auxiliary space:

    O(1)


===============================================================
36. TOTAL SPACE VS AUXILIARY SPACE
===============================================================

Suppose input is:

    numbers = [1, 2, 3, ..., n]

The input itself requires:

    O(n)

If the algorithm creates another list of size n:

    O(n)

additional memory.

Depending on terminology:

    Total space:
        O(n)

or, if counting both input and copied output explicitly:

    O(n) + O(n)
    = O(n)

The distinction matters conceptually even though the asymptotic
class may remain the same.


===============================================================
37. RECURSION AND SPACE COMPLEXITY
===============================================================

Every recursive function consumes call-stack space.

Example:

    def countdown(n):
        if n == 0:
            return

        countdown(n - 1)

There are approximately n recursive calls.

Stack space:

    O(n)


===============================================================
38. RECURSION TREE
===============================================================

Consider:

    fibonacci_naive(n)

It branches into:

    fib(n-1)
    fib(n-2)

Each of those branches creates more branches.

The recursion tree grows rapidly.

This explains why naive Fibonacci is exponentially expensive.

Recursion is not automatically inefficient.

For example, merge sort uses recursion but has:

    Time: O(n log n)
    Auxiliary space: commonly O(n)

The structure of the recurrence matters.


===============================================================
39. RECURRENCE RELATIONS
===============================================================

A recurrence expresses the running time of a recursive algorithm.

For merge sort:

    T(n) = 2T(n/2) + O(n)

Interpretation:

    2 recursive subproblems
    each of size n/2
    plus O(n) merging work

The resulting complexity is:

    O(n log n)


===============================================================
40. MASTER THEOREM INTUITION
===============================================================

For recurrences of the form:

    T(n) = aT(n/b) + f(n)

we can compare:

    f(n)

against:

    n^(log_b(a))

This produces several major cases.

Case 1:
    f(n) is polynomially smaller.

Case 2:
    f(n) matches the critical term.

Case 3:
    f(n) is polynomially larger under the required conditions.

For example:

    T(n) = 2T(n/2) + n

Here:

    a = 2
    b = 2

Therefore:

    n^(log_2 2) = n

The extra work is also:

    n

So:

    T(n) = Θ(n log n)

This is one reason divide-and-conquer algorithms often produce
n log n complexity.


===============================================================
41. MERGE SORT
===============================================================
"""

def merge(left, right):
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


def merge_sort(items):
    """
    Merge sort.

    Time:
        Best    -> Θ(n log n)
        Average -> Θ(n log n)
        Worst   -> Θ(n log n)

    Auxiliary space:
        O(n) for this implementation.
    """

    if len(items) <= 1:
        return items

    middle = len(items) // 2

    left = merge_sort(items[:middle])
    right = merge_sort(items[middle:])

    return merge(left, right)


"""
===============================================================
42. QUICKSORT
===============================================================

Quicksort chooses a pivot and partitions the input.

Typical complexity:

    Best:
        O(n log n)

    Average:
        O(n log n)

    Worst:
        O(n^2)

Worst case can occur when partitioning is consistently very
unbalanced.

With good pivot strategies and randomized behavior, practical
performance is often excellent.

This illustrates why best, average, and worst cases all matter.


===============================================================
43. BUBBLE SORT
===============================================================
"""

def bubble_sort(items):
    """
    Educational bubble sort.

    Worst-case:
        O(n^2)

    Average-case:
        O(n^2)

    Best-case:
        O(n) when optimized and input is already sorted.

    Auxiliary space:
        O(1)
    """

    items = items.copy()

    n = len(items)

    for i in range(n):
        swapped = False

        for j in range(0, n - i - 1):
            if items[j] > items[j + 1]:
                items[j], items[j + 1] = items[j + 1], items[j]
                swapped = True

        if not swapped:
            break

    return items


"""
===============================================================
44. INSERTION SORT
===============================================================

Insertion sort:

    Best:
        O(n)

    Average:
        O(n^2)

    Worst:
        O(n^2)

Space:
    O(1) auxiliary space in an in-place implementation.

Insertion sort can be excellent for small or nearly sorted
datasets despite having O(n^2) worst-case complexity.


===============================================================
45. PYTHON'S SORT
===============================================================

Python's list.sort() and sorted() use Timsort.

Timsort combines ideas from insertion sort and merge sort and is
designed to exploit existing order in real-world data.

Typical discussion:

    Worst-case time:
        O(n log n)

    Best-case behavior:
        Can approach O(n) on highly structured inputs.

The lesson is important:

    The algorithm used in a production library may exploit
    practical properties of real data that a simple theoretical
    algorithm does not.


===============================================================
46. HASH TABLES AND DICTIONARIES
===============================================================

Python dictionaries use hash-table-based structures.

Typical dictionary lookup:

    Average:
        O(1)

Worst-case theoretical behavior can differ depending on
collisions and implementation details.

Example:

    data = {
        "name": "Atul",
        "age": 30
    }

Lookup:

    data["name"]

is expected to be approximately:

    O(1)

This is one reason hash tables are fundamental in software
engineering.


===============================================================
47. PYTHON LIST COMPLEXITIES
===============================================================

Typical Python list operations:

    Access by index:
        O(1)

    Assignment by index:
        O(1)

    Append:
        O(1) amortized

    Pop from end:
        O(1)

    Insert at beginning:
        O(n)

    Insert in middle:
        O(n)

    Delete from beginning:
        O(n)

    Search:
        O(n)

    Membership test:
        O(n)

Why is inserting at the beginning O(n)?

Because existing elements generally need to be shifted.


===============================================================
48. PYTHON SET COMPLEXITIES
===============================================================

Typical set operations:

    Membership:
        O(1) average

    Add:
        O(1) average

    Remove:
        O(1) average

Sets are useful when the main requirement is fast membership
testing rather than maintaining positional order.


===============================================================
49. PYTHON DICTIONARY COMPLEXITIES
===============================================================

Typical dictionary operations:

    Lookup:
        O(1) average

    Insert:
        O(1) average

    Delete:
        O(1) average

    Membership:
        O(1) average

This is why dictionaries are often preferred over lists when
the problem requires frequent key-based lookups.


===============================================================
50. STRING COMPLEXITY
===============================================================

Strings are sequences.

Searching for a substring may require work dependent on the
lengths of the strings and the algorithm used.

A naive substring search can have relatively high worst-case
complexity.

Modern libraries may use optimized implementations.

Therefore:

    Never assume a string operation is O(1) simply because it
    appears as one line of Python code.

One line of code can hide substantial computation.


===============================================================
51. ONE LINE DOES NOT MEAN O(1)
===============================================================

This is a critical lesson.

Consider:

    x in my_list

It is one line.

But if my_list is a list, membership testing generally requires
linear scanning.

Therefore:

    O(n)

By contrast:

    x in my_set

is typically:

    O(1) average

The number of lines of source code does NOT determine complexity.


===============================================================
52. HIDDEN COMPLEXITY
===============================================================

Consider:

    sorted(numbers)

This looks simple.

But sorting n elements is not O(1).

It requires approximately:

    O(n log n)

time in typical general-purpose comparison sorting.

Similarly:

    list.copy()

takes time proportional to the number of copied elements:

    O(n)


===============================================================
53. COMBINING COMPLEXITIES
===============================================================

Suppose an algorithm does:

    Step A -> O(n)
    Step B -> O(n log n)
    Step C -> O(n^2)

Total:

    O(n) + O(n log n) + O(n^2)

Dominant term:

    O(n^2)

Therefore:

    Overall complexity = O(n^2)


===============================================================
54. IF-ELSE STATEMENTS
===============================================================

Consider:

    if condition:
        for i in range(n):
            pass
    else:
        for i in range(n):
            for j in range(n):
                pass

One branch:

    O(n)

Other branch:

    O(n^2)

Worst-case complexity:

    O(n^2)

But the complexity of a specific execution depends on which
branch actually runs.


===============================================================
55. EARLY TERMINATION
===============================================================

Consider linear search:

    for item in items:
        if item == target:
            return True

Best case:

    target is first
    -> O(1)

Worst case:

    target is absent or last
    -> O(n)

Early termination is a major reason best-case behavior can differ
dramatically from worst-case behavior.


===============================================================
56. INPUT DISTRIBUTION MATTERS
===============================================================

Average-case analysis requires assumptions.

Suppose a search algorithm behaves differently depending on
where the target appears.

If targets are:

    equally likely to appear anywhere

the expected behavior differs from a situation where:

    targets are usually near the beginning.

Therefore:

    "Average case" is meaningful only when the probability model
    is defined or reasonably understood.


===============================================================
57. RANDOMIZED ALGORITHMS
===============================================================

Some algorithms use randomness.

Quicksort is a classic example.

Random pivot selection reduces the likelihood of repeatedly
choosing extremely poor pivots for adversarial input patterns.

The analysis may therefore involve:

    Expected running time

rather than only deterministic best/worst behavior.

Important concepts include:

    Expected complexity
    High-probability bounds
    Randomized algorithms
    Adversarial inputs


===============================================================
58. DETERMINISTIC VS RANDOMIZED COMPLEXITY
===============================================================

Deterministic algorithm:

    Same input
    ->
    Same sequence of computational decisions

Randomized algorithm:

    Same input
    ->
    Random choices may change the execution path

Randomized algorithms can produce excellent expected performance
while still having possible bad executions.


===============================================================
59. AMORTIZED VS AVERAGE VS WORST CASE
===============================================================

Worst case:

    Maximum cost over valid inputs of size n.

Best case:

    Minimum cost over valid inputs of size n.

Average case:

    Expected cost under a probability distribution.

Amortized:

    Average cost per operation over a sequence, without necessarily
    assuming random inputs.

These concepts should not be treated as interchangeable.


===============================================================
60. TIME-SPACE TRADE-OFF
===============================================================

Sometimes we can use more memory to reduce execution time.

Example:

    Searching repeatedly for the same values.

Approach 1:
    Search a list every time.

Each search:

    O(n)

Approach 2:
    Build a set.

Construction:

    O(n)

Then membership:

    O(1) average

If there are many queries, preprocessing can significantly
reduce total time.

This is a classic time-space trade-off.


===============================================================
61. PRECOMPUTATION
===============================================================

Precomputation means doing work once so future operations become
cheaper.

Example:

    Build a frequency dictionary:

        frequency[value] += 1

Then frequency lookup is approximately:

    O(1) average

instead of repeatedly scanning the original data.

The general pattern is:

    Pay upfront
    ->
    Answer future queries faster


===============================================================
62. PREFIX SUM
===============================================================

Suppose we repeatedly need range sums.

Naive approach:

    sum(items[left:right])

Each query can cost:

    O(n)

If we construct prefix sums:

    prefix[i] = sum of first i elements

Preprocessing:

    O(n)

Each range sum:

    O(1)

This transforms repeated expensive operations into cheap queries.


===============================================================
63. DATABASE EXAMPLE
===============================================================

Suppose a database contains millions of records.

Query:

    Find customer by customer_id.

Without a suitable index:

    Potentially O(n)

With an appropriate index:

    Often approximately O(log n) for tree-based indexes.

Some database systems use hash-based indexes or other structures
with different characteristics.

The key principle:

    Data structures and indexes determine computational cost.


===============================================================
64. ALGORITHM COMPLEXITY VS REAL PERFORMANCE
===============================================================

Two algorithms can have the same asymptotic complexity but very
different practical performance.

Example:

    Algorithm A:
        10n operations

    Algorithm B:
        1000n operations

Both:

    O(n)

But A may be much faster.

Similarly:

    Cache behavior
    Memory locality
    Branch prediction
    Parallelism
    I/O
    Network latency
    Serialization
    Interpreter overhead

can significantly influence actual performance.


===============================================================
65. CPU-BOUND VS I/O-BOUND
===============================================================

Complexity analysis often focuses on computational work.

Real applications also perform:

    Disk I/O
    Network requests
    Database queries
    File operations

A program may be algorithmically efficient but slow because it
performs thousands of network requests.

Therefore, performance engineering must consider the entire system.


===============================================================
66. BIG-O IS NOT A STOPWATCH
===============================================================

Never interpret:

    O(n)

as:

    "This always takes n milliseconds."

It means roughly:

    The growth in work is proportional to n.

Similarly:

    O(n^2)

does not mean:

    "It always takes n^2 seconds."

It describes scaling behavior.


===============================================================
67. ASYMPTOTIC ANALYSIS
===============================================================

Asymptotic analysis focuses on behavior as:

    n -> infinity

This allows us to compare scalability.

Example:

    T1(n) = 1000n

    T2(n) = n^2

For small n:

    T1 may be slower or faster depending on constants.

For sufficiently large n:

    n^2 eventually grows faster than 1000n.

This is why asymptotic analysis is useful for large-scale
algorithm selection.


===============================================================
68. LOWER BOUNDS
===============================================================

Sometimes we can prove that no algorithm in a certain model can
solve a problem faster than a certain asymptotic bound.

For comparison-based sorting, a fundamental lower bound is:

    Ω(n log n)

for the general comparison model.

This explains why comparison sorting algorithms such as merge sort
cannot generally beat n log n asymptotically in that model.


===============================================================
69. NOT EVERY PROBLEM HAS THE SAME BEST POSSIBLE COMPLEXITY
===============================================================

Different problems have different algorithmic limits.

Examples:

    Array indexing:
        O(1)

    Comparison sorting:
        Ω(n log n) lower bound

    Linear search in an unsorted array:
        Ω(n) worst-case lower bound for deterministic comparison
        search in the general setting.

The goal is not merely:

    "Find an O(n) algorithm."

The deeper goal is:

    "Find an algorithm close to the best achievable complexity
     under the problem's assumptions."


===============================================================
70. DATA STRUCTURE CHOICE AFFECTS COMPLEXITY
===============================================================

Suppose we need membership testing.

Using a list:

    x in list
    -> O(n)

Using a set:

    x in set
    -> O(1) average

Using a balanced search tree:

    search
    -> O(log n)

Same high-level problem.

Different data structures.

Different complexity.

Therefore:

    Algorithm design and data-structure design are deeply connected.


===============================================================
71. GRAPH ALGORITHM COMPLEXITY
===============================================================

For graphs, complexity is often expressed using:

    V = number of vertices
    E = number of edges

A graph algorithm may therefore be:

    O(V + E)

instead of:

    O(n)

Breadth-first search (BFS) and depth-first search (DFS), using
appropriate adjacency-list representations, can run in:

    O(V + E)

because each vertex and edge is processed a bounded number of
times.


===============================================================
72. MATRIX COMPLEXITY
===============================================================

For two n x n matrices:

    Matrix multiplication using the basic algorithm:

        O(n^3)

because there are approximately:

    n^2

output cells

and each cell requires:

    O(n)

work.

Total:

    n^2 * n
    = n^3


===============================================================
73. MULTI-DIMENSIONAL INPUT
===============================================================

Suppose an image has:

    height = h
    width = w

An algorithm visiting every pixel has:

    O(hw)

complexity.

If:

    h = w = n

then:

    O(n^2)

This is why defining input dimensions correctly is essential.


===============================================================
74. PARAMETERIZED COMPLEXITY
===============================================================

Some problems depend on several parameters.

Example:

    O(V + E)

for graph traversal.

Another algorithm may depend on:

    n = number of items
    k = number of clusters

Then complexity might be:

    O(nk)

Good complexity analysis preserves meaningful parameters instead
of forcing everything into a single n.


===============================================================
75. ITERATIVE VS RECURSIVE IMPLEMENTATION
===============================================================

Two implementations may have the same time complexity but
different space complexity.

Example:

Iterative traversal:

    Time: O(n)
    Auxiliary space: potentially O(1)

Recursive traversal:

    Time: O(n)
    Call-stack space: O(n) in a linear recursion chain

Therefore, complexity analysis should examine both dimensions.


===============================================================
76. TAIL RECURSION
===============================================================

A tail-recursive function performs its recursive call as the
final operation.

Some programming languages optimize tail calls.

Python does not generally perform tail-call optimization.

Therefore, converting a Python algorithm from a loop to recursion
can increase stack usage and may hit recursion limits.


===============================================================
77. ITERATOR AND GENERATOR MEMORY
===============================================================

Generators can reduce memory usage.

List:

    values = [x * x for x in range(1_000_000)]

creates a large collection.

Generator:

    values = (x * x for x in range(1_000_000))

produces values lazily.

This can reduce memory from approximately:

    O(n)

for materialized output

to approximately:

    O(1)

additional storage, depending on the surrounding computation.

But lazy execution may introduce different time and access
trade-offs.


===============================================================
78. SPACE COMPLEXITY OF COPYING
===============================================================

Consider:

    new_items = old_items.copy()

If old_items contains n elements:

    Time:
        O(n)

    Additional space:
        O(n)

Copying is not free.

This is particularly important when manipulating large datasets.


===============================================================
79. SHALLOW VS DEEP COPY
===============================================================

A shallow copy duplicates the outer container.

A deep copy may recursively duplicate nested objects.

Therefore, complexity can depend on:

    Number of nested objects
    Structure of the object graph
    Total amount of data copied

Never assume all copying operations are O(1).


===============================================================
80. ALGORITHM ANALYSIS WORKFLOW
===============================================================

A practical analysis process:

    Step 1:
        Define the input size.

    Step 2:
        Identify the dominant operation.

    Step 3:
        Count how many times it can execute.

    Step 4:
        Analyze loops.

    Step 5:
        Analyze nested loops.

    Step 6:
        Analyze branches.

    Step 7:
        Analyze recursion.

    Step 8:
        Analyze hidden library/data-structure operations.

    Step 9:
        Determine best/average/worst behavior when relevant.

    Step 10:
        Analyze auxiliary space.

    Step 11:
        Simplify using asymptotic notation.

    Step 12:
        Validate practical assumptions with benchmarking.


===============================================================
81. EXAMPLE: ANALYZE THIS FUNCTION
===============================================================
"""

def example_one(numbers):
    total = 0

    for number in numbers:
        total += number

    return total


"""
Analysis:

Let:

    n = len(numbers)

Loop executes n times.

Each iteration performs constant work.

Therefore:

    Time = O(n)

Additional variables:

    total
    number

Do not grow with n.

Therefore:

    Auxiliary space = O(1)


===============================================================
82. EXAMPLE: TWO NESTED LOOPS
===============================================================
"""

def example_two(numbers):
    count = 0

    for x in numbers:
        for y in numbers:
            if x == y:
                count += 1

    return count


"""
Analysis:

Outer loop:

    n

Inner loop:

    n

Total:

    n * n

Time:

    O(n^2)

Auxiliary space:

    O(1)


===============================================================
83. EXAMPLE: LOGARITHMIC LOOP
===============================================================
"""

def example_three(n):
    value = 1

    while value < n:
        value *= 2

    return value


"""
Analysis:

Values:

    1
    2
    4
    8
    ...

After k iterations:

    value = 2^k

We stop when:

    2^k >= n

Therefore:

    k >= log2(n)

Time:

    O(log n)

Space:

    O(1)


===============================================================
84. EXAMPLE: LINEAR + QUADRATIC
===============================================================
"""

def example_four(numbers):
    total = sum(numbers)

    for x in numbers:
        for y in numbers:
            if x < y:
                total += 1

    return total


"""
Analysis:

sum(numbers):

    O(n)

Nested loops:

    O(n^2)

Total:

    O(n) + O(n^2)

Dominant term:

    O(n^2)


===============================================================
85. EXAMPLE: MULTIPLE INPUTS
===============================================================
"""

def compare_lists(list_a, list_b):
    matches = 0

    for a in list_a:
        for b in list_b:
            if a == b:
                matches += 1

    return matches


"""
Let:

    n = len(list_a)
    m = len(list_b)

Outer loop:

    O(n)

Inner loop:

    O(m)

Total:

    O(nm)


===============================================================
86. BENCHMARKING WITH PYTHON
===============================================================

Theoretical complexity and practical benchmarking are different.

Complexity asks:

    "How does work scale as n grows?"

Benchmarking asks:

    "How long did this implementation take in this environment?"

Python's timeit module can be used for controlled microbenchmarks.
"""

import timeit


def linear_work(n):
    total = 0

    for i in range(n):
        total += i

    return total


def quadratic_work(n):
    total = 0

    for i in range(n):
        for j in range(n):
            total += i + j

    return total


def benchmark():
    """
    Benchmarking demonstrates practical runtime.

    It does NOT replace complexity analysis.
    """

    linear_time = timeit.timeit(
        lambda: linear_work(10_000),
        number=10
    )

    quadratic_time = timeit.timeit(
        lambda: quadratic_work(500),
        number=10
    )

    print("Linear benchmark:", linear_time)
    print("Quadratic benchmark:", quadratic_time)


"""
Do not compare benchmark numbers from different input sizes
without accounting for the difference in n.

Benchmarking should be controlled and repeatable.


===============================================================
87. WHY BENCHMARKING CAN MISLEAD
===============================================================

Runtime can be affected by:

    CPU frequency
    Thermal throttling
    Background applications
    Operating system scheduling
    Memory hierarchy
    Python version
    Interpreter behavior
    Garbage collection
    Input characteristics
    Cache state

Therefore:

    "Algorithm A ran in 0.5 seconds once"

does not prove:

    "Algorithm A is asymptotically better."


===============================================================
88. COMPLEXITY CHEAT SHEET
===============================================================

Typical examples:

    O(1)
        Array index access
        Dictionary lookup average case
        Set membership average case

    O(log n)
        Binary search
        Repeated halving

    O(n)
        Linear search
        Array traversal
        Finding maximum

    O(n log n)
        Efficient comparison sorting

    O(n^2)
        Pairwise comparison
        Simple nested loops

    O(n^3)
        Basic cubic matrix multiplication

    O(2^n)
        Many brute-force subset problems
        Naive recursive branching examples

    O(n!)
        Brute-force permutation enumeration


===============================================================
89. COMMON ANALYSIS MISTAKES
===============================================================

Mistake 1:

    "There are two loops, so it must be O(n^2)."

Not always.

If loops are sequential:

    O(n) + O(n)
    = O(n)

Mistake 2:

    "One line means O(1)."

False.

Example:

    sorted(items)

is not O(1).

Mistake 3:

    "Two variables mean O(n^2)."

False.

Two pointers can still be:

    O(n)

Mistake 4:

    "Big-O gives exact runtime."

False.

It describes asymptotic growth.

Mistake 5:

    "Average case and amortized case are the same."

False.

They use different analytical ideas.

Mistake 6:

    "Worst-case complexity tells me everything about practical
     performance."

Not necessarily.

Real workloads and constants matter.


===============================================================
90. COMPLEXITY AND SCALABILITY
===============================================================

Scalability means how well a system continues to perform as
workload grows.

Consider:

    O(n)

versus:

    O(n^2)

If input grows by a factor of 10:

    O(n)
        grows approximately 10x

    O(n^2)
        grows approximately 100x

If input grows by a factor of 100:

    O(n)
        grows approximately 100x

    O(n^2)
        grows approximately 10,000x

This is why complexity is fundamentally about scalability.


===============================================================
91. COMPLEXITY IN MACHINE LEARNING
===============================================================

Complexity analysis is also important in machine learning.

Examples:

    Training dataset size
    Number of features
    Number of parameters
    Batch size
    Number of layers
    Sequence length

Transformer models, for example, have attention mechanisms whose
naive self-attention computation is commonly described as:

    O(n^2)

with respect to sequence length n.

This becomes important for long-context processing.

Optimization techniques attempt to reduce computational or memory
costs through approaches such as:

    Sparse attention
    Sliding-window attention
    Linear attention variants
    FlashAttention-style memory optimization
    Chunking
    Quantization
    Caching


===============================================================
92. COMPLEXITY IN DISTRIBUTED SYSTEMS
===============================================================

In distributed systems, computational complexity is only one
part of the problem.

We may also care about:

    Network messages
    Bandwidth
    Latency
    Number of machines
    Storage
    Replication
    Coordination
    Fault tolerance

An algorithm can have low CPU complexity but high network cost.

Therefore, distributed algorithms often analyze communication
complexity as well.


===============================================================
93. I/O COMPLEXITY
===============================================================

For data-intensive applications, the number of disk or network
operations can dominate CPU operations.

Example:

    Reading 1 million small files

may be much slower than processing 1 million values already in RAM.

Therefore, practical analysis can include:

    CPU complexity
    Memory complexity
    I/O complexity
    Communication complexity


===============================================================
94. CACHE AND MEMORY LOCALITY
===============================================================

Two algorithms with identical Big-O complexity can behave
differently because of memory access patterns.

Sequential memory access often benefits from:

    Cache locality

Random access can cause:

    Cache misses

Therefore:

    O(n)

does not imply identical real-world performance for every
implementation.

Asymptotic complexity abstracts away hardware-level effects.


===============================================================
95. PARALLEL COMPUTING
===============================================================

In parallel computing, total work is not the only consideration.

We may analyze:

    Work
    Span
    Parallelism

An algorithm may have:

    O(n)

total work

but may or may not be efficiently parallelizable.

Another algorithm may have more total work but much lower critical
path length.

This leads to more advanced performance models beyond simple
single-threaded Big-O analysis.


===============================================================
96. COMPLEXITY AND OPTIMIZATION
===============================================================

Optimization should begin with understanding the actual bottleneck.

Suppose:

    O(n^2)

algorithm takes too long.

Possible improvements:

    Use hashing
    Use sorting
    Use binary search
    Use a better data structure
    Precompute information
    Use dynamic programming
    Use divide and conquer
    Reduce unnecessary work

Example:

Naive duplicate detection:

    Compare every pair
    -> O(n^2)

Hash-based approach:

    Track seen values
    -> O(n) average

This is a major algorithmic improvement.


===============================================================
97. DYNAMIC PROGRAMMING AND COMPLEXITY
===============================================================

Dynamic programming often reduces exponential recursion by
storing previously computed results.

Naive Fibonacci:

    Exponential time

Memoized Fibonacci:

    O(n) time
    O(n) space

Bottom-up Fibonacci:

    O(n) time
    O(1) space if only the last two values are stored

This demonstrates:

    Time-space trade-off

and:

    Avoiding repeated computation.


===============================================================
98. MEMOIZATION
===============================================================
"""

from functools import lru_cache


@lru_cache(maxsize=None)
def fibonacci_memoized(n):
    """
    Memoized Fibonacci.

    Each Fibonacci state is calculated once.

    Time:
        O(n)

    Space:
        O(n) for cached states and recursion depth.
    """

    if n <= 1:
        return n

    return (
        fibonacci_memoized(n - 1)
        + fibonacci_memoized(n - 2)
    )


"""
The important idea is not Fibonacci itself.

The important idea is:

    Repeated subproblem
        ->
    store result
        ->
    reuse result

This can transform exponential algorithms into polynomial or
linear-time algorithms for many problems.


===============================================================
99. SPACE-TIME TRADE-OFF EXAMPLE
===============================================================
"""

def duplicate_detection_naive(items):
    """
    Compare every pair.

    Time:
        O(n^2)

    Auxiliary space:
        O(1)
    """

    n = len(items)

    for i in range(n):
        for j in range(i + 1, n):
            if items[i] == items[j]:
                return True

    return False


def duplicate_detection_hash(items):
    """
    Use a set.

    Expected time:
        O(n)

    Auxiliary space:
        O(n)
    """

    seen = set()

    for item in items:
        if item in seen:
            return True

        seen.add(item)

    return False


"""
Comparison:

Naive:
    Time  -> O(n^2)
    Space -> O(1)

Hash-based:
    Time  -> O(n) average
    Space -> O(n)

We traded memory for speed.


===============================================================
100. ADVANCED VIEW: COMPLEXITY IS MODEL-DEPENDENT
===============================================================

Complexity depends on the computational model.

Examples:

    RAM model
    Comparison model
    External-memory model
    Distributed model
    Parallel model

An operation considered O(1) in one model may not be considered
constant in another.

For example, arithmetic on arbitrarily large integers is not
necessarily constant-time because the number of bits matters.


===============================================================
101. INTEGER SIZE COMPLEXITY
===============================================================

In basic algorithm courses, arithmetic operations are often
treated as O(1).

This is a useful simplification for fixed-width integers.

But with arbitrary-precision integers:

    10

and:

    10^1,000,000

do not require the same amount of storage.

Operations can depend on the number of bits.

This leads to more advanced concepts such as:

    Bit complexity
    Word-RAM model
    Bit operations
    Arithmetic complexity


===============================================================
102. OUTPUT-SENSITIVE COMPLEXITY
===============================================================

Some problems require work proportional to the size of the output.

Suppose an algorithm must produce k results.

An algorithm cannot physically output k items in less than:

    Ω(k)

time simply because writing the output itself takes time.

Such algorithms may be analyzed as:

    O(input size + output size)

This is known as output-sensitive thinking.


===============================================================
103. SPACE LOWER BOUNDS
===============================================================

Just as problems have time lower bounds, some tasks have memory
requirements.

For example, if an algorithm must explicitly store n distinct
output elements, the output itself requires:

    Ω(n)

space.

The distinction between:

    output space

and:

    auxiliary workspace

is important in advanced analysis.


===============================================================
104. COMPLEXITY OF APIs AND LIBRARIES
===============================================================

When writing production code, understand the complexity of the
operations used by your libraries.

Questions to ask:

    Is membership O(1) or O(n)?

    Is this operation copying data?

    Is sorting happening internally?

    Does this API make a network request?

    Does this database query use an index?

    Does this operation allocate another large object?

Good developers analyze not only their own loops but also the
operations hidden behind abstractions.


===============================================================
105. PRACTICAL CODE REVIEW CHECKLIST
===============================================================

When reviewing an algorithm, ask:

    1. What is the input size?

    2. What is the dominant operation?

    3. How many times does it execute?

    4. Are loops sequential or nested?

    5. Does a loop grow or shrink exponentially?

    6. Is there recursion?

    7. What is the recurrence?

    8. What data structures are being used?

    9. Are there hidden O(n) operations?

    10. Are there repeated scans?

    11. Can hashing eliminate repeated searches?

    12. Can sorting enable binary search?

    13. Can preprocessing reduce query cost?

    14. What is the auxiliary space?

    15. What happens in the worst case?

    16. What assumptions define the average case?

    17. Is the implementation amortized?

    18. Are I/O or network operations dominant?

    19. Are constants practically important?

    20. Does benchmarking confirm the theoretical expectation?


===============================================================
106. FINAL COMPLEXITY ANALYSIS EXAMPLE
===============================================================
"""

def comprehensive_example(items):
    """
    A deliberately mixed example for analysis.
    """

    if not items:
        return None

    sorted_items = sorted(items)

    target = sorted_items[len(sorted_items) // 2]

    left = 0
    right = len(sorted_items) - 1

    while left <= right:
        middle = (left + right) // 2

        if sorted_items[middle] == target:
            return middle

        if sorted_items[middle] < target:
            left = middle + 1
        else:
            right = middle - 1

    return -1


"""
Analysis:

Step 1:
    sorted(items)

Time:
    O(n log n)

Space:
    Depends on implementation and temporary storage,
    but sorting may require additional memory.

Step 2:
    Binary search.

Time:
    O(log n)

Total:

    O(n log n) + O(log n)

Dominant term:

    O(n log n)

Therefore:

    Overall time complexity = O(n log n)


===============================================================
107. A VERY IMPORTANT RULE
===============================================================

When analyzing an algorithm:

    DO NOT count lines of code.

Count:

    How the work scales with input size.


===============================================================
108. ANOTHER IMPORTANT RULE
===============================================================

Big-O should not be used mechanically.

Always ask:

    What is n?

Example:

    O(n)

could mean:

    number of users
    number of records
    number of vertices
    number of edges
    number of characters
    number of pixels
    sequence length

The meaning of n must be defined.


===============================================================
109. COMPLEXITY TABLE
===============================================================

Complexity        Typical interpretation
---------------------------------------------------------------
O(1)              Constant
O(log n)           Logarithmic
O(n)               Linear
O(n log n)         Linearithmic
O(n^2)             Quadratic
O(n^3)             Cubic
O(2^n)             Exponential
O(n!)              Factorial

As n becomes very large, lower-growth algorithms generally scale
better.


===============================================================
110. FINAL TAKEAWAY
===============================================================

Complexity analysis is the mathematical language used to reason
about algorithm scalability.

The most important ideas are:

    1. Algorithms consume resources.

    2. The two major resources are time and space.

    3. Input size is usually represented by n.

    4. Time complexity describes how computational work grows.

    5. Space complexity describes how memory requirements grow.

    6. Best case represents favorable input behavior.

    7. Average case represents expected behavior under assumptions
       about input distribution.

    8. Worst case represents the maximum cost for valid inputs.

    9. Big-O expresses an asymptotic upper bound.

    10. Big-Omega expresses an asymptotic lower bound.

    11. Big-Theta expresses a tight asymptotic bound.

    12. Constant factors and lower-order terms are usually ignored
        in asymptotic notation.

    13. Sequential complexities are generally added.

    14. Nested complexities are generally multiplied.

    15. Repeated halving often produces O(log n).

    16. Efficient comparison sorting commonly achieves
        O(n log n).

    17. Hash tables provide O(1) average lookup in typical cases.

    18. Data-structure choice can dramatically change complexity.

    19. Precomputation can trade memory or setup time for faster
        queries.

    20. Memoization can eliminate repeated computation.

    21. Amortized analysis is different from average-case analysis.

    22. Benchmarking measures actual runtime; Big-O describes
        asymptotic growth.

    23. Real-world performance also depends on I/O, memory,
        caching, hardware, networking, and implementation details.

    24. Advanced systems may require analysis of communication,
        parallelism, bit complexity, or external-memory behavior.

The central mindset is:

    "Do not ask only whether the algorithm works."

Ask:

    "How does its cost grow when the problem becomes larger?"

That question is at the heart of algorithmic thinking.


===============================================================
END OF COMPLETE PYTHON LEARNING SCRIPT
===============================================================
"""

if __name__ == "__main__":
    print("Complexity Analysis learning script loaded successfully.")

    print("\nBinary Search:")
    data = [1, 3, 5, 7, 9, 11, 13]
    print(binary_search(data, 9))

    print("\nMerge Sort:")
    unsorted = [9, 4, 7, 1, 3, 8]
    print(merge_sort(unsorted))

    print("\nBubble Sort:")
    print(bubble_sort(unsorted))

    print("\nNaive Fibonacci:")
    print(fibonacci_naive(10))

    print("\nMemoized Fibonacci:")
    print(fibonacci_memoized(30))

    print("\nDuplicate Detection:")
    sample = [1, 2, 3, 4, 3]
    print("Naive:", duplicate_detection_naive(sample))
    print("Hash-based:", duplicate_detection_hash(sample))

    print("\nComplexity examples:")
    print("example_one:", example_one([1, 2, 3, 4]))
    print("example_three:", example_three(100))
