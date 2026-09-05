# Asymptotic Notations

## 1. Introduction

Asymptotic notation is a mathematical framework for describing how the resource requirements of an algorithm grow as the input size becomes large.

The principal notations are:

- **Big-O, O(g(n))**: asymptotic upper bound
- **Big-Omega, Ω(g(n))**: asymptotic lower bound
- **Big-Theta, Θ(g(n))**: asymptotically tight bound
- **Little-o, o(g(n))**: strict asymptotic upper relationship
- **Little-omega, ω(g(n))**: strict asymptotic lower relationship

The accompanying Python script demonstrates these concepts through executable implementations and progressively more advanced examples involving loops, searching, sorting, recursion, recurrence relations, space complexity, amortized analysis, empirical measurement, formal bounds, edge cases, and practical considerations.

---

## 2. Input Size

The first step in asymptotic analysis is identifying the quantity that represents input size.

The symbol `n` is commonly used, but its exact meaning depends on the problem.

Examples include:

- `n` as the number of elements in an array
- `n` as the number of characters in a string
- `n` as the number of vertices in a graph
- `m` as the number of edges in a graph
- `n` as the dimension of a square matrix
- `n` as the number of database records being processed

Correctly defining input size is essential because complexity is expressed relative to that quantity.

For graph algorithms, two parameters may be required:

n = number of vertices
m = number of edges

An algorithm that scans all vertices and edges might therefore have complexity `O(n + m)`.

---

## 3. Purpose of Asymptotic Analysis

Actual execution time depends on many implementation-specific factors:

- Processor speed
- Programming language
- Compiler or interpreter
- Memory hierarchy
- Operating system
- Input representation
- Hardware architecture
- Background processes

Asymptotic analysis removes most of these implementation-dependent details and focuses on how resource requirements grow as the input size increases.

The main goals are:

1. Compare algorithms independently of hardware.
2. Predict how an algorithm behaves for large inputs.
3. Identify inefficient algorithms.
4. Estimate scalability.
5. Understand the relationship between input size and resource usage.
6. Choose appropriate algorithms and data structures.

For example, suppose two algorithms solve the same problem:

- Algorithm A takes `10n` operations.
- Algorithm B takes `n²` operations.

For small values of `n`, both may appear practical. As `n` becomes large, `n²` grows much faster than `10n`.

Therefore, asymptotic analysis helps identify which algorithm will scale better.

---

## 4. Input Size

Asymptotic analysis requires a definition of input size.

For an array containing `n` elements, the input size is usually:

`n`

For a string containing `n` characters:

`n`

For a graph:

- `n` may represent the number of vertices.
- `m` may represent the number of edges.

For a matrix with `n` rows and `m` columns, the input size may depend on both dimensions.

For an integer, the situation is slightly different. If the integer is very large, the number of bits required to represent it can matter.

For example, an integer `x` requires approximately:

`log₂(x) + 1`

bits for its binary representation.

This distinction becomes important in advanced algorithm analysis.

---

## 5. Measuring Growth

Suppose an algorithm performs:

`T(n) = 3n² + 5n + 10`

operations.

For large `n`, the `n²` term dominates the lower-order terms.

Therefore:

`T(n) = O(n²)`

The constants and lower-order terms are ignored when describing asymptotic growth.

Consider:

`T(n) = 1000n + 500`

This is still:

`O(n)`

Even though the constant `1000` may have a practical effect for some input sizes.

Asymptotic notation describes growth rather than exact execution time.

---

## 6. Why Constants Are Ignored

Consider two algorithms:

`T₁(n) = 5n`

`T₂(n) = 100n`

Both are linear:

`T₁(n) = O(n)`

`T₂(n) = O(n)`

The second algorithm may be significantly slower in practice, but both grow proportionally to `n`.

Asymptotic analysis focuses on the growth rate.

The constant factor becomes less important when comparing the fundamental scalability of algorithms.

---

## 7. Why Lower-Order Terms Are Ignored

Consider:

`T(n) = n³ + 100n² + 5000n + 20`

As `n` becomes very large, the cubic term dominates the others.

Therefore:

`T(n) = O(n³)`

For example, if `n = 10`:

- `n³ = 1,000`
- `100n² = 10,000`
- `5000n = 50,000`

For this relatively small input, lower-order terms can still matter.

For sufficiently large `n`, the cubic term eventually dominates.

This is why asymptotic notation is primarily concerned with long-run growth.

---

## 8. Common Growth Rates

The most common complexity classes include:

| Complexity | Name | Typical Example |
|---|---|---|
| `O(1)` | Constant | Array access |
| `O(log n)` | Logarithmic | Binary search |
| `O(n)` | Linear | Linear search |
| `O(n log n)` | Linearithmic | Merge sort |
| `O(n²)` | Quadratic | Simple nested loops |
| `O(n³)` | Cubic | Some matrix algorithms |
| `O(2ⁿ)` | Exponential | Some recursive subset algorithms |
| `O(n!)` | Factorial | Brute-force permutation search |

The growth rate generally becomes less desirable as `n` increases.

---

## 9. Constant Time: `O(1)`

An operation has constant complexity when its running time does not depend on the size of the input.

For example, accessing an element by index in an array is typically:

`O(1)`

Example:

    value = numbers[5]

The operation directly accesses a known memory location.

Even if the array contains one million elements, accessing a particular index takes approximately the same number of elementary operations.

Constant time does not necessarily mean one physical machine instruction.

It means the number of operations is bounded independently of `n`.

---

## 10. Logarithmic Time: `O(log n)`

An algorithm is logarithmic when each major operation reduces the remaining problem by a constant factor.

Binary search is the classic example.

Suppose a sorted array contains:

`1,000,000`

elements.

Binary search repeatedly divides the search space approximately in half.

After one comparison:

`500,000`

elements remain.

Then:

`250,000`

Then:

`125,000`

The number of steps grows approximately as:

`log₂(n)`

Therefore:

`T(n) = O(log n)`

Logarithmic algorithms scale very well for large inputs.

---

## 11. Linear Time: `O(n)`

An algorithm is linear when its work grows proportionally with the input size.

Example:

    total = 0

    for value in numbers:
        total += value

If there are `n` elements, the loop executes approximately `n` times.

Therefore:

`T(n) = O(n)`

Linear algorithms are often practical for large datasets.

---

## 12. Linearithmic Time: `O(n log n)`

`O(n log n)` commonly appears in efficient sorting algorithms.

Merge sort is a standard example.

The algorithm divides the input repeatedly, producing approximately:

`log n`

levels.

At each level, approximately `n` elements are processed.

Therefore:

`n × log n`

gives:

`O(n log n)`

This is significantly better than quadratic growth for large datasets.

---

## 13. Quadratic Time: `O(n²)`

Quadratic complexity usually occurs when an algorithm performs approximately `n` work for each of `n` elements.

Example:

    for i in range(n):
        for j in range(n):
            print(i, j)

The outer loop executes `n` times.

For every outer-loop iteration, the inner loop executes `n` times.

Therefore:

`n × n = n²`

So:

`T(n) = O(n²)`

Quadratic algorithms can become expensive as input size increases.

---

## 14. Cubic Time: `O(n³)`

Three nested loops often produce cubic complexity.

Example:

    for i in range(n):
        for j in range(n):
            for k in range(n):
                process(i, j, k)

The total number of iterations is:

`n × n × n = n³`

Therefore:

`T(n) = O(n³)`

Cubic algorithms become impractical relatively quickly as `n` increases.

---

## 15. Exponential Time: `O(2ⁿ)`

Exponential algorithms have growth proportional to an exponential function.

A common example is generating all subsets of a set.

A set containing `n` elements has:

`2ⁿ`

possible subsets.

Therefore, an algorithm that explicitly examines every subset may require:

`O(2ⁿ)`

time.

Exponential algorithms are usually practical only for relatively small inputs unless additional optimization techniques are used.

---

## 16. Factorial Time: `O(n!)`

Factorial growth occurs when an algorithm considers every possible ordering of `n` objects.

The number of permutations is:

`n!`

For example:

`5! = 120`

`10! = 3,628,800`

`15! = 1,307,674,368,000`

Factorial growth is extremely rapid.

Brute-force solutions to some permutation-based problems therefore become infeasible very quickly.

---

## 17. Big-O Notation

Big-O notation describes an asymptotic upper bound.

It is commonly used to describe the worst-case growth of an algorithm.

If:

`T(n) = 3n² + 5n + 10`

then:

`T(n) = O(n²)`

This means that for sufficiently large `n`, the running time does not grow faster than a constant multiple of `n²`.

Big-O does not necessarily mean that `n²` is the exact complexity.

For example:

`O(n)`

is also technically:

`O(n²)`

because a linear function is eventually bounded above by a quadratic function.

This is why Big-O alone does not necessarily represent a tight bound.

---

## 18. Formal Definition of Big-O

A function `f(n)` is:

`O(g(n))`

if there exist positive constants `c` and `n₀` such that:

`0 ≤ f(n) ≤ c · g(n)`

for every:

`n ≥ n₀`

Here:

- `f(n)` is the actual function being analyzed.
- `g(n)` is the comparison function.
- `c` is a positive constant.
- `n₀` is a threshold after which the inequality holds.

The constants `c` and `n₀` do not depend on `n`.

---

## 19. Big-O Example

Consider:

`f(n) = 3n + 5`

We want to show:

`f(n) = O(n)`

Choose:

`c = 4`

For sufficiently large `n`:

`3n + 5 ≤ 4n`

This is true when:

`5 ≤ n`

Therefore, for:

`n ≥ 5`

we have:

`3n + 5 ≤ 4n`

Hence:

`3n + 5 = O(n)`

---

## 20. Big-Omega Notation

Big-Omega, written as:

`Ω(g(n))`

describes an asymptotic lower bound.

If:

`f(n) = Ω(g(n))`

then `f(n)` grows at least as quickly as a constant multiple of `g(n)` for sufficiently large `n`.

For example:

`3n² + 5n + 10 = Ω(n²)`

The quadratic term guarantees that the function grows at least proportionally to `n²` asymptotically.

---

## 21. Formal Definition of Big-Omega

A function `f(n)` is:

`Ω(g(n))`

if there exist positive constants `c` and `n₀` such that:

`0 ≤ c · g(n) ≤ f(n)`

for every:

`n ≥ n₀`

The important relationship is that `f(n)` eventually stays above a constant multiple of `g(n)`.

---

## 22. Big-Theta Notation

Big-Theta notation:

`Θ(g(n))`

represents a tight asymptotic bound.

If:

`f(n) = Θ(g(n))`

then `f(n)` is bounded both above and below by constant multiples of `g(n)`.

For example:

`3n² + 5n + 10 = Θ(n²)`

because the function is both:

`O(n²)`

and:

`Ω(n²)`

Therefore:

`Θ(n²)`

is the tightest standard asymptotic characterization.

---

## 23. Formal Definition of Big-Theta

A function:

`f(n)`

is:

`Θ(g(n))`

if there exist positive constants `c₁`, `c₂`, and `n₀` such that:

`0 ≤ c₁g(n) ≤ f(n) ≤ c₂g(n)`

for every:

`n ≥ n₀`

The lower bound and upper bound together establish a tight asymptotic bound.

---

## 24. Relationship Between O, Ω, and Θ

The three primary asymptotic notations can be understood as:

| Notation | Meaning |
|---|---|
| `O(g(n))` | Upper bound |
| `Ω(g(n))` | Lower bound |
| `Θ(g(n))` | Tight bound |

For:

`f(n) = 5n² + 2n + 7`

we can state:

`f(n) = O(n²)`

`f(n) = Ω(n²)`

and therefore:

`f(n) = Θ(n²)`

---

## 25. Big-O Is Not Always Worst Case

A common misconception is:

"Big-O always means worst-case complexity."

This is not mathematically correct.

Big-O is an upper-bound notation.

Worst-case complexity is a separate concept.

For example, an algorithm can have:

- Best case: `Θ(1)`
- Average case: `Θ(n)`
- Worst case: `Θ(n²)`

The worst-case complexity can be described as:

`O(n²)`

But Big-O itself is not synonymous with worst case.

---

## 26. Best-Case Complexity

Best-case complexity describes the minimum amount of work an algorithm performs for an input of size `n`.

Consider linear search.

If the desired element is the first element:

`O(1)`

So the best-case complexity is:

`Ω(1)`

and more precisely:

`Θ(1)`

for that best-case scenario.

---

## 27. Worst-Case Complexity

Worst-case complexity describes the maximum amount of work required for an input of size `n`.

For linear search, the target might:

- Appear at the final position.
- Not appear at all.

In either situation, approximately all `n` elements may need to be examined.

Therefore:

`Θ(n)`

is the worst-case complexity.

---

## 28. Average-Case Complexity

Average-case analysis estimates expected resource usage across inputs according to an assumed probability distribution.

Average-case analysis can be more difficult because it requires assumptions about the input distribution.

For example, if an element is equally likely to occur at any position in an array, a successful linear search examines approximately:

`(n + 1) / 2`

elements on average.

Ignoring constants:

`Θ(n)`

---

## 29. Amortized Analysis

Amortized analysis evaluates the average cost of a sequence of operations rather than treating each operation independently.

For example, dynamically growing an array may occasionally require copying all elements to a larger memory region.

Most insertions are inexpensive.

A resize operation can be expensive.

Even so, when the cost is distributed across a long sequence of insertions, the amortized cost per insertion can be:

`O(1)`

This does not mean every insertion takes constant time.

It means the average cost over a suitable sequence is constant.

---

## 30. Aggregate Method

The aggregate method calculates the total cost of a sequence of operations and divides it by the number of operations.

Suppose `n` dynamic-array insertions have total cost:

`O(n)`

Then the amortized cost per insertion is:

`O(n) / n = O(1)`

This provides an amortized constant-time bound.

---

## 31. Accounting Method

The accounting method assigns an amortized cost to each operation.

Some operations are charged more than their immediate cost.

The extra amount acts as stored credit that can pay for future expensive operations.

For example, an insertion into a dynamic array might be charged slightly more than its immediate insertion cost.

The accumulated credit can later help pay for resizing.

---

## 32. Potential Method

The potential method defines a potential function representing stored future work.

The amortized cost of an operation can be expressed using:

`amortized cost = actual cost + change in potential`

This approach is useful for analyzing sophisticated data structures and sequences of operations.

---

## 33. Space Complexity

Asymptotic analysis can measure memory usage as well as running time.

Space complexity describes how the additional memory requirement grows with input size.

For example:

    result = []

    for value in numbers:
        result.append(value * 2)

If the output contains `n` elements, the output itself requires:

`O(n)`

space.

If the algorithm also needs an additional temporary structure of size `n`, auxiliary space may also be:

`O(n)`

---

## 34. Auxiliary Space

Auxiliary space refers to additional memory used by an algorithm, excluding the memory required for the input and sometimes excluding the output depending on the convention.

For example:

    total = 0

    for value in numbers:
        total += value

The algorithm uses a constant number of extra variables.

Therefore, its auxiliary space is:

`O(1)`

The distinction between total space and auxiliary space should always be stated clearly.

---

## 35. Time Complexity of Multiple Statements

Consider:

    for i in range(n):
        process(i)

    for j in range(n):
        process(j)

The first loop requires:

`O(n)`

The second loop requires:

`O(n)`

Because the loops execute sequentially:

`O(n) + O(n) = O(n)`

The constant factor is removed.

Therefore, the complete algorithm has:

`O(n)`

time complexity.

---

## 36. Nested Loops

Consider:

    for i in range(n):
        for j in range(n):
            process(i, j)

The loops are nested.

Therefore, the number of operations is:

`n × n`

which gives:

`O(n²)`

A common mistake is to add the complexities of nested loops.

For nested loops, the costs are generally multiplied when each inner loop executes for every outer-loop iteration.

---

## 37. Dependent Nested Loops

Consider:

    for i in range(n):
        for j in range(i):
            process(i, j)

The total number of operations is:

`0 + 1 + 2 + ... + (n - 1)`

Using the arithmetic-series formula:

`n(n - 1) / 2`

Therefore:

`Θ(n²)`

Even though the inner loop does not execute exactly `n` times for every `i`, the overall growth remains quadratic.

---

## 38. Triangular Loop Example

Consider:

    for i in range(n):
        for j in range(i, n):
            process(i, j)

The number of iterations is:

`n + (n - 1) + (n - 2) + ... + 1`

This equals:

`n(n + 1) / 2`

Therefore:

`Θ(n²)`

The exact number of operations differs from a full `n × n` loop, but the asymptotic growth is still quadratic.

---

## 39. Logarithmic Loop

Consider:

    i = 1

    while i < n:
        process(i)
        i = i * 2

The values of `i` are approximately:

`1, 2, 4, 8, 16, ...`

After `k` iterations:

`i = 2^k`

The loop stops when:

`2^k ≥ n`

Taking logarithms:

`k ≥ log₂(n)`

Therefore:

`O(log n)`

---

## 40. Dividing Loop

Consider:

    i = n

    while i > 1:
        process(i)
        i = i // 2

The input size is repeatedly divided by two.

Therefore:

`O(log n)`

The base of the logarithm does not matter in asymptotic notation because logarithms with different constant bases differ only by a constant factor.

---

## 41. Combining Different Complexities

Consider:

    for i in range(n):
        process(i)

    i = 1
    while i < n:
        process(i)
        i *= 2

The first section is:

`O(n)`

The second section is:

`O(log n)`

Therefore:

`O(n + log n)`

Since `n` grows faster than `log n`:

`O(n + log n) = O(n)`

---

## 42. Complexity of Conditionals

Consider:

    if condition:
        for i in range(n):
            process(i)
    else:
        process_single_item()

The worst-case branch requires:

`O(n)`

The other branch requires:

`O(1)`

Therefore, the worst-case complexity is:

`O(n)`

When analyzing conditional statements, consider the relevant execution path and the type of analysis being performed.

---

## 43. Recursion and Complexity

Recursive algorithms require special care.

Consider:

    def countdown(n):
        if n == 0:
            return
        countdown(n - 1)

The function calls itself `n` times.

Therefore:

`T(n) = T(n - 1) + O(1)`

which gives:

`T(n) = O(n)`

The recursion depth is also:

`O(n)`

so the auxiliary stack space is `O(n)`.

---

## 44. Recurrence Relations

Recursive algorithms are frequently analyzed using recurrence relations.

For example:

`T(n) = 2T(n/2) + O(n)`

This recurrence represents an algorithm that:

1. Creates two subproblems.
2. Reduces each subproblem to approximately half the original size.
3. Performs `O(n)` additional work.

This recurrence is solved as:

`T(n) = O(n log n)`

and more precisely:

`T(n) = Θ(n log n)`

---

## 45. Master Theorem

The Master Theorem provides a systematic way to solve many divide-and-conquer recurrences of the form:

`T(n) = aT(n/b) + f(n)`

where:

- `a ≥ 1`
- `b > 1`
- `f(n)` represents the additional work.

The critical comparison is between:

`f(n)`

and:

`n^(log_b(a))`

The theorem has several standard cases.

---

## 46. Master Theorem Case 1

If:

`f(n) = O(n^(log_b(a) - ε))`

for some positive constant `ε`, then:

`T(n) = Θ(n^(log_b(a)))`

Example:

`T(n) = 2T(n/2) + O(1)`

Here:

`a = 2`

`b = 2`

Therefore:

`n^(log₂2) = n`

The additional work is smaller than `n`.

Thus:

`T(n) = Θ(n)`

---

## 47. Master Theorem Case 2

If:

`f(n) = Θ(n^(log_b(a)) log^k n)`

for `k ≥ 0`, then:

`T(n) = Θ(n^(log_b(a)) log^(k+1) n)`

For example:

`T(n) = 2T(n/2) + Θ(n)`

has:

`a = 2`

`b = 2`

and:

`n^(log₂2) = n`

Therefore:

`T(n) = Θ(n log n)`

This is the recurrence associated with merge sort.

---

## 48. Master Theorem Case 3

If:

`f(n) = Ω(n^(log_b(a) + ε))`

for some positive constant `ε`, and an appropriate regularity condition is satisfied, then:

`T(n) = Θ(f(n))`

The additional work dominates the recursive subproblems.

This case should be applied carefully because the regularity condition matters.

---

## 49. Comparing Algorithms

Suppose three algorithms solve the same problem:

| Algorithm | Complexity |
|---|---|
| A | `O(n²)` |
| B | `O(n log n)` |
| C | `O(n)` |

For sufficiently large inputs:

`O(n)` grows more slowly than:

`O(n log n)`

which grows more slowly than:

`O(n²)`

Therefore, algorithm C generally provides the best asymptotic scalability.

---

## 50. Complexity Growth Example

Consider an input size of `n = 1,000`.

Approximate operation counts:

| Complexity | Approximate Operations |
|---|---:|
| `log₂ n` | about 10 |
| `n` | 1,000 |
| `n log₂ n` | about 10,000 |
| `n²` | 1,000,000 |
| `n³` | 1,000,000,000 |
| `2ⁿ` | astronomically large |

This illustrates why selecting an appropriate complexity class becomes critical as input size grows.

---

## 51. Polynomial vs Exponential Complexity

Polynomial complexities include:

`O(n)`

`O(n²)`

`O(n³)`

`O(n^k)`

for a fixed constant `k`.

Exponential complexities include:

`O(2ⁿ)`

`O(3ⁿ)`

and similar forms.

Polynomial-time algorithms generally scale much better than exponential-time algorithms.

This distinction is fundamental in theoretical computer science.

---

## 52. Logarithmic Base

Consider:

`log₂ n`

and:

`log₁₀ n`

Using the change-of-base formula:

`log₂ n = log₁₀ n / log₁₀ 2`

Since:

`1 / log₁₀ 2`

is a constant:

`log₂ n = Θ(log₁₀ n)`

Therefore, asymptotic notation usually writes:

`O(log n)`

without specifying the base.

---

## 53. Dominant-Term Rule

For a polynomial:

`f(n) = a_k n^k + a_(k-1)n^(k-1) + ... + a_1n + a_0`

the highest-degree term dominates asymptotically.

Therefore:

`f(n) = Θ(n^k)`

provided:

`a_k ≠ 0`

Example:

`7n⁴ + 3n³ + 100n² + 20`

becomes:

`Θ(n⁴)`

---

## 54. Common Simplification Rules

When simplifying asymptotic expressions:

### Rule 1: Drop Constants

`O(5n) = O(n)`

### Rule 2: Keep the Dominant Term

`O(n² + n) = O(n²)`

### Rule 3: Sequential Work Is Added

`O(n) + O(n²) = O(n²)`

### Rule 4: Nested Independent Work Is Multiplied

`O(n) × O(n) = O(n²)`

### Rule 5: Logarithmic Base Is Usually Ignored

`O(log₂ n) = O(log n)`

These rules make algorithm analysis much easier.

---

## 55. Common Mistake: Counting Every Operation Exactly

Asymptotic analysis does not normally require exact instruction counting.

For example:

`3n + 7`

is simplified to:

`Θ(n)`

The purpose is to understand growth rather than calculate an exact runtime.

Exact operation counting can still be useful in performance engineering, benchmarking, and low-level optimization.

---

## 56. Common Mistake: Confusing O and Θ

Suppose:

`f(n) = n`

It is true that:

`f(n) = O(n²)`

but:

`Θ(n)`

is the tighter characterization.

Therefore, saying an algorithm is `O(n²)` does not necessarily mean that its exact asymptotic growth is quadratic.

When a tight bound is known, `Θ` provides more information.

---

## 57. Common Mistake: Assuming Nested Loops Always Mean `O(n²)`

Nested loops do not automatically imply quadratic complexity.

Example:

    i = 1

    while i < n:
        j = 1
        while j < n:
            process(i, j)
            j *= 2
        i *= 2

The outer loop runs:

`O(log n)`

times.

The inner loop also runs:

`O(log n)`

times.

Therefore:

`O(log² n)`

The loop structure must be analyzed rather than judged only by the number of nesting levels.

---

## 58. Common Mistake: Ignoring Input Representation

An algorithm may be described as operating on an integer in `O(1)` time when the model assumes fixed-size machine integers.

For arbitrarily large integers, arithmetic operations themselves may depend on the number of bits.

For example, adding two `b`-bit integers is not necessarily constant time in a bit-complexity model.

Therefore, the computational model matters.

---

## 59. RAM Model

A common theoretical model is the Random Access Machine, or RAM model.

Under a simplified RAM model:

- Basic arithmetic operations are treated as constant time.
- Array access is treated as constant time.
- Comparisons are treated as constant time.
- Assignment is treated as constant time.

This model makes algorithm analysis manageable.

Real hardware does not always behave exactly according to this model.

---

## 60. Bit Complexity

Bit complexity measures computation based on the number of bits used to represent values.

This is particularly important for:

- Cryptography
- Number theory
- Large integer arithmetic
- Computational algebra
- Exact numerical computation

An operation that is considered `O(1)` under a fixed-word RAM model may have nonconstant cost under a bit-complexity model.

---

## 61. Data Structures and Complexity

The choice of data structure can significantly affect algorithmic complexity.

For example:

| Operation | Array | Hash Table | Balanced Search Tree |
|---|---|---|---|
| Access by index | `O(1)` | Not typical | `O(log n)` by key |
| Search | `O(n)` | Average `O(1)` | `O(log n)` |
| Insert | Depends on position | Average `O(1)` | `O(log n)` |
| Delete | Depends on position | Average `O(1)` | `O(log n)` |

These bounds depend on implementation and assumptions.

Hash-table operations, for example, typically have expected or average `O(1)` performance but can have worse-case `O(n)` behavior under unfavorable conditions.

---

## 62. Hash Tables and Expected Complexity

Hash tables are often described as providing:

`O(1)`

average or expected lookup.

This does not mean every lookup is guaranteed to take constant time.

Hash collisions can cause multiple keys to occupy the same bucket or otherwise require additional work.

Therefore, the complexity should be stated accurately:

`Expected O(1)`

rather than universally claiming:

`Worst-case O(1)`

for a conventional hash-table implementation.

---

## 63. Graph Algorithms

Graph algorithms often use two input-size parameters:

`n = number of vertices`

`m = number of edges`

A graph traversal such as BFS or DFS typically runs in:

`O(n + m)`

when the graph is represented using adjacency lists.

The algorithm processes:

- Each reachable vertex.
- Each relevant edge.

Therefore, the complexity depends on both vertices and edges.

---

## 64. Adjacency Matrix vs Adjacency List

Graph representation affects complexity.

An adjacency matrix uses:

`O(n²)`

space.

Checking whether an edge exists is typically:

`O(1)`

An adjacency list uses:

`O(n + m)`

space.

Traversing the neighbors of a vertex is proportional to its degree.

Therefore, choosing the representation depends on graph density and required operations.

---

## 65. Sorting Complexity

Common comparison-based sorting algorithms include:

| Algorithm | Best | Average | Worst |
|---|---|---|---|
| Bubble Sort | `O(n)`* | `O(n²)` | `O(n²)` |
| Selection Sort | `O(n²)` | `O(n²)` | `O(n²)` |
| Insertion Sort | `O(n)` | `O(n²)` | `O(n²)` |
| Merge Sort | `O(n log n)` | `O(n log n)` | `O(n log n)` |
| Heap Sort | `O(n log n)` | `O(n log n)` | `O(n log n)` |
| Quicksort | `O(n log n)` | `O(n log n)` | `O(n²)` |

*The `O(n)` best case for bubble sort assumes an implementation that detects when no swaps occur.

---

## 66. Searching Complexity

Linear search examines elements sequentially.

Worst-case:

`O(n)`

Binary search repeatedly halves a sorted search space.

Worst-case:

`O(log n)`

The important requirement for binary search is that the search structure must support the necessary ordering and random-access behavior efficiently.

Applying binary search to an unsuitable data structure may change the practical complexity.

---

## 67. Space-Time Trade-Off

Sometimes additional memory can reduce running time.

For example, storing previously computed results in a cache can avoid repeated computation.

Without caching:

`O(n²)`

With an appropriate lookup structure:

The computation may be reduced substantially, potentially toward:

`O(n)`

while requiring additional:

`O(n)`

memory.

This is known as a space-time trade-off.

---

## 68. Memoization

Memoization stores results of previously solved subproblems.

Consider a recursive function with overlapping subproblems.

Without memoization, the same subproblems may be solved repeatedly.

With memoization, each distinct subproblem can be solved once and its result reused.

This can transform some recursive algorithms from exponential time to polynomial time.

For example, naive recursive Fibonacci computation has exponential growth, while memoized Fibonacci can run in:

`O(n)`

time with:

`O(n)`

additional space.

---

## 69. Dynamic Programming

Dynamic programming combines:

1. Optimal substructure.
2. Overlapping subproblems.

It stores intermediate results so that they are not recomputed unnecessarily.

Dynamic programming may be implemented using:

- Top-down recursion with memoization.
- Bottom-up iteration.

The complexity depends on the number of states and the work required to process each state.

---

## 70. Divide and Conquer

Divide-and-conquer algorithms typically follow three stages:

1. Divide the problem.
2. Solve smaller subproblems.
3. Combine their results.

Examples include:

- Merge sort
- Quicksort
- Binary search
- Strassen-style matrix multiplication

Their complexity is commonly expressed using recurrence relations.

---

## 71. Greedy Algorithms

Greedy algorithms make locally optimal choices with the goal of producing a globally optimal solution.

Examples include:

- Kruskal's algorithm
- Prim's algorithm
- Dijkstra's algorithm under appropriate edge-weight conditions
- Activity-selection algorithms

Their complexity depends on the data structures used.

For example, a priority queue can significantly affect the complexity of graph algorithms.

---

## 72. Randomized Algorithms

Randomized algorithms use random choices during execution.

Their complexity may be expressed using:

- Expected running time.
- High-probability bounds.
- Worst-case bounds.

Randomization can improve expected performance or simplify algorithm design.

Quicksort is a common example where random pivot selection can reduce the likelihood of consistently poor partitions.

---

## 73. Probabilistic Analysis

Probabilistic analysis evaluates algorithm behavior under assumptions about inputs or random choices.

It is especially useful for:

- Randomized algorithms.
- Hashing.
- Average-case analysis.
- Random sampling.
- Randomized data structures.

The probability model must be clearly specified because average-case results depend on assumptions.

---

## 74. Practical Runtime vs Asymptotic Complexity

Two algorithms with the same asymptotic complexity can have very different practical runtimes.

For example:

`A(n) = 2n`

and:

`B(n) = 1000n`

are both:

`Θ(n)`

Yet A may be substantially faster for practical input sizes.

Other factors include:

- Constant factors.
- Memory access patterns.
- Cache locality.
- Branch prediction.
- Parallelism.
- Compiler optimization.
- Hardware architecture.
- Input characteristics.

Asymptotic analysis should therefore be combined with empirical benchmarking when making production performance decisions.

---

## 75. Cache Effects

Modern processors do not access all memory at the same speed.

Data stored closer to the processor can often be accessed faster than data stored farther away.

Two algorithms with the same asymptotic complexity can behave differently because of memory locality.

For example, sequentially scanning an array often benefits from good cache locality.

A theoretically efficient algorithm with poor memory access patterns may perform worse in practice than a simpler algorithm.

---

## 76. Parallel Algorithms

Traditional Big-O analysis often assumes a sequential machine.

Parallel algorithms may use multiple processors or computing units simultaneously.

Their analysis can involve:

- Work.
- Span.
- Parallel time.
- Processor count.
- Communication cost.

An algorithm may perform more total work but still complete faster when sufficient parallelism is available.

Therefore, standard sequential complexity is not always enough for modern parallel systems.

---

## 77. Time Complexity Is Not the Only Concern

Algorithm selection may also depend on:

- Space usage.
- Energy consumption.
- Network traffic.
- I/O operations.
- Latency.
- Throughput.
- Maintainability.
- Reliability.
- Security.
- Implementation complexity.

An algorithm with the theoretically smallest asymptotic runtime is not automatically the best choice in every application.

---

## 78. Complexity and Scalability

Scalability describes how well a system continues to perform as workload increases.

An algorithm with:

`O(n)`

usually scales better than one with:

`O(n²)`

for sufficiently large `n`.

For example, doubling the input approximately:

- Doubles an `O(n)` workload.
- Quadruples an `O(n²)` workload.
- Increases an `O(n³)` workload by approximately eight times.

This provides an intuitive way to understand asymptotic growth.

---

## 79. Doubling-Input Rule

If an algorithm has complexity:

`O(n)`

doubling `n` approximately doubles the dominant work.

If it has:

`O(n²)`

doubling `n` approximately multiplies the dominant work by:

`2² = 4`

If it has:

`O(n³)`

doubling `n` approximately multiplies the dominant work by:

`2³ = 8`

For exponential complexity:

`O(2ⁿ)`

doubling the input does not simply multiply the work by a fixed small polynomial factor.

The growth becomes extremely rapid.

---

## 80. How to Analyze an Algorithm

A systematic process can be used:

1. Identify the input-size parameter.
2. Identify the basic operation.
3. Count how many times it executes.
4. Analyze loops.
5. Analyze nested loops.
6. Analyze conditional branches.
7. Analyze recursion.
8. Form a mathematical expression.
9. Remove constants and lower-order terms.
10. Express the result using asymptotic notation.
11. Analyze auxiliary space separately.
12. Consider best, average, and worst cases when relevant.

---

## 81. Worked Example

Consider:

    def find_max(values):
        maximum = values[0]

        for value in values:
            if value > maximum:
                maximum = value

        return maximum

Let:

`n = len(values)`

The loop examines each element once.

Therefore:

`T(n) = Θ(n)`

The function uses a fixed number of additional variables:

`maximum`

and:

`value`

Therefore, auxiliary space is:

`Θ(1)`

The input itself requires:

`Θ(n)`

space.

---

## 82. Worked Example with Nested Loops

Consider:

    def count_pairs(values):
        count = 0

        for i in range(len(values)):
            for j in range(i + 1, len(values)):
                count += 1

        return count

The number of iterations is approximately:

`n(n - 1) / 2`

Therefore:

`T(n) = Θ(n²)`

The algorithm uses a constant amount of auxiliary memory.

Therefore:

`Space = Θ(1)`

excluding the input array.

---

## 83. Worked Example with Logarithmic Growth

Consider:

    def reduce_value(n):
        steps = 0

        while n > 1:
            n //= 2
            steps += 1

        return steps

Each iteration approximately halves `n`.

Therefore:

`T(n) = Θ(log n)`

The algorithm stores only a constant number of variables.

Therefore:

`Space = Θ(1)`

---

## 84. Final Conceptual Distinction

The most important ideas to remember are:

- `O(g(n))` describes an asymptotic upper bound.
- `Ω(g(n))` describes an asymptotic lower bound.
- `Θ(g(n))` describes a tight asymptotic bound.
- Best, average, and worst case are different ways of analyzing inputs or execution scenarios.
- Time complexity describes how computational work grows.
- Space complexity describes how memory requirements grow.
- Constants and lower-order terms are ignored in asymptotic growth.
- The dominant term determines the asymptotic class.
- Nested loops do not automatically imply `O(n²)`.
- Recursive algorithms often require recurrence relations.
- Data structures can dramatically change complexity.
- Practical performance also depends on hardware, memory access, constants, implementation, and workload.
- Asymptotic analysis is primarily about scalability as input size becomes large.
