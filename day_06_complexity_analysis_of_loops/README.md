# Complexity Analysis of Loops

## 1. Topic Introduction

Complexity analysis of loops is the process of determining how the computational work performed by an algorithm grows as its input size increases.

Loops are among the most important structures used to determine algorithmic complexity because their iteration counts often directly determine the number of operations performed. A single loop may be linear, logarithmic, or constant depending on how its control variable changes. Nested loops may produce quadratic, cubic, or more complicated complexity. Consecutive loops generally add their costs rather than multiply them. Dependent loops require summation-based reasoning because the number of inner iterations changes according to an outer-loop variable.

This script develops a systematic method for analyzing these patterns, beginning with simple loops and progressing to dependent loops, logarithmic loops, harmonic sums, monotonic pointers, amortized behavior, multiple input dimensions, and combinations of different complexity classes.

---

## 2. Fundamental Terminology

### Input Size

The input size, conventionally represented by `n`, measures the amount of data processed by an algorithm.

Examples:

- An array containing `n` elements has input size `n`.
- A matrix with `r` rows and `c` columns has two dimensions, `r` and `c`.
- A graph with `V` vertices and `E` edges has two important dimensions, `V` and `E`.

Input dimensions should not automatically be collapsed into one variable. An algorithm processing `n` rows and `m` columns may have complexity `O(nm)`, not necessarily `O(n²)`.

### Basic Operation

A basic operation is an operation treated as constant-time under the chosen computational model.

Examples include:

- An integer addition under ordinary fixed-width assumptions.
- A comparison.
- An assignment.
- Access to an array element under random-access assumptions.

The precise cost model can affect exact operation counts, but it generally does not change the asymptotic classification when each operation is treated as constant time.

### Time Complexity

Time complexity describes how the amount of computation grows with input size.

It is primarily concerned with growth rather than a specific number of seconds. Actual execution time depends on hardware, programming language, implementation details, memory behavior, compiler or interpreter overhead, and system load.

### Space Complexity

Space complexity describes how memory requirements grow with input size.

When discussing auxiliary space, the memory already occupied by the input is normally distinguished from additional memory allocated by the algorithm.

---

## 3. Asymptotic Notation

### Big-O

Big-O describes an asymptotic upper bound.

If an algorithm performs work proportional to `n²` or less for sufficiently large inputs, it can be described as `O(n²)`.

Big-O is commonly used to communicate worst-case growth, although formally it is an upper-bound notation and does not inherently mean worst case.

### Big-Omega

Big-Omega describes an asymptotic lower bound.

An algorithm that must perform at least a linear amount of work can have a lower bound of `Ω(n)`.

### Big-Theta

Big-Theta describes a tight asymptotic bound.

If an algorithm performs both `O(n)` and `Ω(n)` work, its tight complexity is `Θ(n)`.

For loop analysis, `Theta` is often the most precise notation when the number of iterations is known asymptotically.

---

## 4. Constant-Time Loops

A loop that executes a fixed number of times has constant complexity.

For example, a loop that always executes five times performs a constant amount of work regardless of `n`.

Its complexity is:

`Θ(1)`

The value of `n` may be passed into the function, but if it does not determine the number of loop iterations, it does not affect the asymptotic complexity.

---

## 5. Single Linear Loops

A loop that processes each of `n` elements once generally has linear complexity.

A typical pattern is:

`for i in range(n)`

The body executes `n` times.

Therefore:

`T(n) = c n`

and:

`T(n) = Θ(n)`

A fixed increment does not change the class. For example, iterating through approximately `n/3` values is still:

`Θ(n)`

because division by a fixed constant only changes the constant factor.

---

## 6. Exact Operation Counts

Asymptotic analysis intentionally ignores constant factors and lower-order terms.

Suppose a loop executes exactly `n` times and performs one addition each time. The exact number of additions is `n`.

Another implementation might execute `2n + 5` operations.

The exact expressions differ, but both are:

`Θ(n)`

Exact counting is useful when comparing small inputs, understanding an implementation, or deriving a mathematical expression. Asymptotic notation is more useful for understanding long-term growth.

---

## 7. Nested Independent Loops

Consider two nested loops:

- The outer loop executes `n` times.
- For every outer iteration, the inner loop executes `n` times.

The total number of inner-body executions is:

`n × n = n²`

Therefore:

`Θ(n²)`

With three independent loops:

`n × n × n = n³`

giving:

`Θ(n³)`

The script demonstrates both quadratic and cubic patterns.

---

## 8. Nested Loops with Different Dimensions

If the outer loop executes `n` times and the inner loop executes `m` times, the complexity is:

`Θ(nm)`

This distinction matters when `n` and `m` represent different input dimensions.

For example, processing every cell of an `n × m` matrix requires:

`Θ(nm)`

If the matrix is specifically `n × n`, this becomes:

`Θ(n²)`.

---

## 9. Consecutive Loops

Consecutive loops are added rather than multiplied.

Consider:

- First loop: `n` iterations.
- Second loop: `n` iterations.

The total work is:

`n + n = 2n`

Since constant factors are ignored asymptotically:

`Θ(2n) = Θ(n)`

This is one of the most common mistakes in loop analysis.

Nested loops generally multiply independent iteration counts. Consecutive loops generally add their costs.

---

## 10. Dominant-Term Rule

Suppose an algorithm performs:

`n² + n`

operations.

The quadratic term eventually dominates the linear term.

Therefore:

`Θ(n² + n) = Θ(n²)`

Similarly:

- `3n + 10` → `Θ(n)`
- `7n² + 3n + 100` → `Θ(n²)`
- `n³ + n² + n` → `Θ(n³)`
- `n log n + n` → `Θ(n log n)`

The same principle applies when multiple loops occur consecutively.

---

## 11. Logarithmic Loops

A loop is commonly logarithmic when its state changes by a constant multiplicative factor.

Examples include:

- `x *= 2`
- `x *= 3`
- `x //= 2`
- `x //= 10`

For a doubling loop:

`1, 2, 4, 8, 16, ...`

After `k` iterations:

`x = 2^k`

The loop stops when approximately:

`2^k >= n`

Taking logarithms:

`k >= log₂(n)`

Therefore the number of iterations is:

`Θ(log n)`

---

## 12. Logarithm Bases

For fixed positive bases greater than one:

`log₂(n)`

`log₃(n)`

and

`log₁₀(n)`

differ only by constant factors.

The change-of-base relationship is:

`log_a(n) = log_b(n) / log_b(a)`

Because `1 / log_b(a)` is constant when the bases are fixed:

`Θ(log₂ n) = Θ(log₃ n) = Θ(log₁₀ n)`

The base matters when calculating exact iteration counts, but not when determining the asymptotic class.

---

## 13. Linearithmic Loops

A common pattern is:

- Outer loop: `n` iterations.
- Inner loop: `log n` iterations.

The total work is:

`n × log n`

Therefore:

`Θ(n log n)`

The script demonstrates this with an outer linear loop and an inner doubling loop.

This complexity class is important because it appears frequently in efficient sorting algorithms and divide-and-conquer algorithms.

---

## 14. Dependent Loops

A dependent loop has an iteration count controlled by an outer-loop variable.

Consider:

`for i in range(n):`

with an inner loop that executes `i` times.

The total number of executions is:

`0 + 1 + 2 + ... + (n - 1)`

Using the arithmetic-series formula:

`n(n - 1) / 2`

Therefore:

`Θ(n²)`

The fact that the inner loop does not always execute `n` times does not make the total linear. The summation still grows quadratically.

---

## 15. Triangular Loop Patterns

Two common triangular patterns are:

`sum(i)` for `i` from `0` to `n - 1`

and:

`n + (n - 1) + ... + 1`

Both produce a quadratic number of operations.

For example:

`1 + 2 + ... + n = n(n + 1)/2`

Therefore:

`Θ(n²)`

This pattern appears frequently when algorithms examine pairs of elements.

---

## 16. Upper-Triangle Pair Processing

A loop such as:

`for i in range(n):`

followed by:

`for j in range(i, n):`

executes:

`n + (n - 1) + ... + 1`

times.

The exact count is:

`n(n + 1)/2`

The asymptotic result is:

`Θ(n²)`

This is common when comparing each element with elements that appear after it while avoiding duplicate pair comparisons.

---

## 17. Fixed-Step Loops

Changing the increment from one to a fixed constant does not change the asymptotic class.

For example:

`i += 3`

results in approximately:

`n / 3`

iterations.

Since `1/3` is a constant:

`Θ(n/3) = Θ(n)`

Likewise:

- `n/2` → `Θ(n)`
- `n/10` → `Θ(n)`
- `3n` → `Θ(n)`

Constants affect practical runtime but not asymptotic growth.

---

## 18. Constant Decrement vs Multiplicative Reduction

Two visually similar loops can have very different complexities.

A loop that repeatedly performs:

`n -= 1`

takes:

`Θ(n)`

iterations.

A loop that repeatedly performs:

`n //= 2`

takes:

`Θ(log n)`

iterations.

The difference comes from how quickly the remaining problem shrinks.

A constant subtraction removes a fixed amount.

A multiplicative reduction removes a constant fraction of the remaining value.

---

## 19. Geometric Progression

A geometric loop might generate:

`1, 2, 4, 8, 16, ...`

or:

`n, n/2, n/4, n/8, ...`

The number of terms required to reach the stopping condition grows logarithmically.

This is why binary search, halving-based algorithms, and many divide-and-conquer structures have logarithmic depth.

---

## 20. Dependent Logarithmic Loops

A loop may execute approximately `log(i)` times for each value of `i`.

The total can be represented as:

`log(1) + log(2) + ... + log(n)`

Using logarithm properties:

`log(1 × 2 × ... × n) = log(n!)`

By Stirling-type asymptotic reasoning:

`log(n!) = Θ(n log n)`

Therefore:

`sum(log i) = Θ(n log n)`

This is different from simply assuming that every nested logarithmic loop produces `n log n` without examining its bound.

---

## 21. Harmonic Nested Loops

A particularly important pattern is:

- Outer loop: `i = 1 ... n`
- Inner loop: approximately `n/i` iterations

The total is:

`n/1 + n/2 + n/3 + ... + n/n`

Factor out `n`:

`n(1 + 1/2 + 1/3 + ... + 1/n)`

The harmonic series grows as:

`Θ(log n)`

Therefore:

`Θ(n log n)`

The script implements this pattern explicitly.

---

## 22. Square-Root Complexity

Some loops stop when a variable reaches `sqrt(n)`.

For example, checking possible divisors only up to the square root of a number produces:

`Θ(sqrt(n))`

This is useful because factors occur in pairs.

If `d` divides `n`, then:

`n/d`

is also a divisor.

Once `d` exceeds `sqrt(n)`, its paired factor would already have been encountered below `sqrt(n)`.

The script demonstrates divisor counting and primality testing using this optimization.

---

## 23. Prime Testing

A straightforward primality test may try every integer from `2` through `n - 1`.

Its worst-case complexity is:

`O(n)`

A more efficient approach tests divisors only through:

`sqrt(n)`

giving:

`O(sqrt(n))`

The optimization illustrates an important principle of loop analysis:

The loop bound is often more important than the number of statements in the loop body.

---

## 24. Three Nested Loops

Three independent loops nested together produce:

`n × n × n = n³`

Therefore:

`Θ(n³)`

Such loops occur in problems involving:

- Triplets.
- Three-dimensional arrays.
- Brute-force enumeration of three variables.
- Certain matrix and graph algorithms.

Cubic complexity becomes expensive quickly as `n` grows.

---

## 25. Mixed Loop Structures

A program can contain several different loop structures.

For example:

`n + n log n + n²`

is dominated by:

`n²`

Therefore:

`Θ(n²)`

Another example:

`n³ + n² + n log n`

is:

`Θ(n³)`

The correct procedure is to analyze each component and then simplify the resulting expression.

---

## 26. Multiple Input Parameters

Suppose an algorithm contains:

- A nested loop involving `a` and `b`.
- A separate loop involving `c`.

The resulting complexity may be:

`Θ(ab + c)`

It is incorrect to automatically replace everything with `n²`.

Multiple variables should be retained when they represent independent input dimensions.

This is especially important in:

- Matrix algorithms.
- Graph algorithms.
- Database operations.
- Image processing.
- Multi-dimensional numerical computations.

---

## 27. Conditional Inner Loops

A loop may execute its inner loop only for some outer iterations.

For example, an inner loop might run only when `i` is even.

Approximately half the outer iterations may execute the inner loop:

`(n/2) × n`

which is:

`n²/2`

Since `1/2` is a constant:

`Θ(n²)`

A condition that changes only a constant fraction of iterations does not change the asymptotic class.

---

## 28. Data-Dependent Termination

Some loops terminate according to the values being processed.

For example, a loop might keep adding elements until a threshold is reached.

The actual number of iterations can vary substantially between inputs.

For complexity analysis, distinguish:

- Best case.
- Average case.
- Worst case.

If the loop can process all `n` elements, the worst-case complexity is:

`O(n)`

The fact that many real inputs may terminate earlier does not eliminate the worst-case bound.

---

## 29. Break

A `break` statement can substantially improve practical execution time.

A linear search may stop after its first element:

Best case:

`O(1)`

If the target occurs at the end or is absent:

Worst case:

`O(n)`

Therefore, `break` does not automatically make a loop constant-time.

The correct question is:

> How many iterations can occur on the most expensive valid execution path?

---

## 30. Break in Nested Loops

A `break` statement exits the loop containing it.

It does not necessarily terminate all surrounding loops.

When a nested search returns immediately, the entire function may stop. In that case, early termination can affect practical and best-case behavior.

Even so, if the target can be absent, every relevant element may still need to be inspected.

For an `r × c` matrix:

`O(rc)`

is the worst-case bound.

---

## 31. Continue

A `continue` statement skips part of the current iteration.

It does not eliminate the iteration itself.

If a loop examines every element of an array and uses `continue` for certain values, the array is still traversed:

`Θ(n)`

This distinction is important when analyzing filtering, validation, and conditional processing loops.

---

## 32. Loop Body Cost

Counting only loop iterations can be misleading.

Suppose an outer loop executes `n` times and each iteration performs another `n` operations.

The total is:

`n × n = n²`

Therefore:

`Θ(n²)`

The cost of the body must be included in the analysis.

The same principle applies to function calls inside loops. If a called function costs `O(n)`, invoking it `n` times can result in `O(n²)` total work.

---

## 33. Nested Syntax Does Not Always Mean Quadratic Complexity

A major subtlety is that nested syntax does not automatically imply multiplication.

Consider a structure where an inner pointer `j` is not reset for each outer iteration.

If `j` only increases and can move from `0` to `n` once across the entire algorithm, its total movement is only:

`O(n)`

Even though the `while` loop is syntactically nested inside a `for` loop.

The correct analysis must consider total pointer movement rather than blindly multiplying maximum loop bounds.

This idea is fundamental to:

- Two-pointer algorithms.
- Sliding-window algorithms.
- Merge procedures.
- Monotonic queue techniques.
- Certain sweep-line algorithms.

---

## 34. Two-Pointer Algorithms

Two pointers do not automatically imply quadratic complexity.

If:

- `left` only increases.
- `right` only decreases.

then each pointer can move at most `n` times.

Total pointer movement is therefore:

`O(n)`

A classic example is searching for a pair with a specified sum in a sorted array.

The algorithm has:

`O(n)`

time and:

`O(1)`

auxiliary space.

The requirement that the input be sorted is an important algorithmic assumption.

---

## 35. Binary Search

Binary search repeatedly eliminates approximately half of the remaining search space.

If the initial search space has size `n`, after `k` iterations it is approximately:

`n / 2^k`

The process stops when:

`n / 2^k <= 1`

which implies:

`2^k >= n`

and therefore:

`k = O(log n)`

Binary search has:

- Best case: `O(1)`
- Worst case: `O(log n)`
- Auxiliary space for iterative implementation: `O(1)`

Binary search generally requires sorted data and an appropriate access model.

---

## 36. Best, Average, and Worst Cases

### Best Case

The minimum amount of work required for an input of a given size.

For linear search, finding the target at the first position is:

`O(1)`

### Worst Case

The maximum amount of work required for an input of a given size.

For linear search, an absent target requires checking every element:

`O(n)`

### Average Case

Expected work under a specified probability distribution.

Average-case analysis is meaningful only when assumptions about input probabilities are defined.

For uniformly distributed successful searches, the expected position in a list of `n` elements is approximately:

`(n + 1) / 2`

which is still:

`Θ(n)`

---

## 37. Loop Invariants

A loop invariant is a statement that remains true at a specified point during every iteration.

Loop invariants are primarily used for correctness proofs, but they are closely related to rigorous loop analysis.

For a running sum:

Before processing the next element, the accumulator represents the sum of all elements processed so far.

A rigorous loop analysis should consider both:

1. Whether the loop terminates and performs the intended work.
2. How much work it performs.

An algorithm can have an accurately analyzed complexity and still be incorrect.

---

## 38. Amortized Complexity

Not every operation in a sequence has to have the same complexity.

A dynamic array may occasionally need to allocate a larger storage region and copy many existing elements.

One resize can cost:

`O(n)`

Yet if capacity grows geometrically, such as doubling, the total number of copied elements across many appends is linear in the number of appended elements.

Consequently, the amortized cost of an append is:

`O(1)`

This is an important distinction between:

- Worst-case cost of one operation.
- Average cost over a sequence of operations.
- Amortized cost guaranteed over a sequence.

---

## 39. Space Complexity of Loops

A loop that uses only a fixed number of variables can use:

`O(1)`

auxiliary space.

For example, summing an array can take linear time but constant auxiliary space.

By contrast, creating a new output list containing `n` elements requires:

`O(n)`

additional space.

The time complexity and space complexity of a loop must therefore be analyzed separately.

---

## 40. Complexity Growth Ranking

A common ordering from slower growth to faster growth is:

1. `O(1)`
2. `O(log n)`
3. `O(sqrt(n))`
4. `O(n)`
5. `O(n log n)`
6. `O(n²)`
7. `O(n³)`
8. `O(2ⁿ)`
9. `O(n!)`

This ordering describes asymptotic growth, not necessarily exact runtime for small inputs.

A highly optimized quadratic implementation may outperform a poorly implemented linear algorithm for sufficiently small inputs.

For large inputs, asymptotic growth becomes increasingly important.

---

## 41. Growth Rate and Practical Performance

Complexity analysis does not directly provide execution time.

Two algorithms may both be:

`O(n)`

while having different constant factors.

For example:

- Algorithm A may perform two simple operations per element.
- Algorithm B may perform twenty expensive operations per element.

Both are asymptotically linear.

Actual runtime also depends on:

- Hardware.
- CPU architecture.
- Memory hierarchy.
- Cache behavior.
- Interpreter or compiler.
- Data representation.
- Function-call overhead.
- Allocation behavior.
- Input characteristics.

The script includes a small empirical timing demonstration to illustrate this distinction.

---

## 42. Algorithmic Improvement

Complexity analysis is especially useful when evaluating alternative implementations.

For duplicate detection, a pairwise comparison approach can require:

`O(n²)`

comparisons.

A hash-set-based approach can provide expected:

`O(n)`

time while using:

`O(n)`

additional space.

This is an example of a time-space trade-off.

The improved algorithm consumes more memory but substantially reduces expected computational work.

---

## 43. Insertion Sort as a Loop Example

Insertion sort demonstrates how dependent loops create different cases.

For already sorted input, the inner `while` loop performs little work.

Best case:

`Θ(n)`

For reverse-sorted input, each new element may need to move across the entire sorted prefix.

Worst case:

`Θ(n²)`

Insertion sort therefore demonstrates why loop complexity can depend on input arrangement rather than only on input size.

Its standard in-place form uses:

`Θ(1)`

auxiliary space.

---

## 44. Matrix Algorithms

A matrix with `r` rows and `c` columns contains:

`r × c`

cells.

Scanning every cell therefore requires:

`Θ(rc)`

time.

If the matrix is square with dimension `n × n`, this becomes:

`Θ(n²)`

Matrix multiplication provides a more complex example.

For matrices with dimensions corresponding to:

- `rows_a`
- `cols_a`
- `cols_b`

the standard triple-loop multiplication structure performs:

`Θ(rows_a × cols_a × cols_b)`

arithmetic operations.

---

## 45. Common Loop Patterns

| Loop pattern | Typical complexity |
|---|---:|
| Fixed number of iterations | `O(1)` |
| One loop through `n` items | `O(n)` |
| Two consecutive linear loops | `O(n)` |
| Two independent nested loops | `O(n²)` |
| Three independent nested loops | `O(n³)` |
| Halving or doubling | `O(log n)` |
| `n` iterations with `log n` inner work | `O(n log n)` |
| Inner bound `i` | `O(n²)` |
| Inner bound `n/i` | `O(n log n)` |
| Inner bound `sqrt(n)` | `O(n sqrt(n))` |
| Monotonic shared pointer | Often `O(n)` |

These are patterns rather than universal rules. The actual bounds and state changes must always be examined.

---

## 46. Common Mistakes

### Mistake 1: Assuming Every Nested Loop Is `O(n²)`

Nested syntax alone is insufficient.

If the inner pointer moves monotonically across the complete execution rather than resetting, total work can be linear.

### Mistake 2: Multiplying Consecutive Loops

Two consecutive loops each performing `n` iterations produce:

`n + n = 2n`

not:

`n²`

### Mistake 3: Treating Constants as Complexity Changes

These all belong to the same asymptotic class:

- `n`
- `n/2`
- `3n`
- `1000n`

All are:

`O(n)`

### Mistake 4: Confusing Doubling with Incrementing

These have different growth:

`x += 1` → `O(n)`

`x *= 2` → `O(log n)`

### Mistake 5: Assuming `break` Means `O(1)`

`break` may create an `O(1)` best case while retaining an `O(n)` worst case.

### Mistake 6: Ignoring Body Complexity

If the loop body performs `O(n)` work and the loop itself executes `n` times, total work can become:

`O(n²)`

### Mistake 7: Ignoring Input Dimensions

An algorithm processing `n` rows and `m` columns should normally be expressed as:

`O(nm)`

rather than assuming:

`O(n²)`

### Mistake 8: Ignoring Termination

A `while` loop must make measurable progress toward its termination condition.

Incorrect state updates can result in infinite loops, making ordinary finite-input complexity analysis inapplicable.

---

## 47. Edge Cases

Important cases include:

- `n = 0`
- `n = 1`
- Empty lists
- Single-element lists
- Missing search targets
- Target at the first position
- Target at the last position
- Reverse-sorted input
- Already sorted input
- Invalid step sizes
- Multiplicative factors less than or equal to one
- Negative inputs where the algorithm assumes positive values

The script explicitly demonstrates several of these cases and validates invalid parameters.

---

## 48. Security and Resource-Consumption Considerations

Complexity analysis has direct production and security implications when loop bounds are controlled by external input.

An attacker who can force an algorithm to process a very large `n` may cause excessive CPU or memory consumption.

For example, an uncontrolled quadratic operation has potential resource-exhaustion implications because increasing the input size by a factor of ten can increase the dominant computational work by approximately a factor of one hundred.

Production code should therefore:

- Validate input sizes.
- Impose reasonable limits.
- Avoid uncontrolled nested loops.
- Guarantee termination of `while` loops.
- Avoid repeatedly scanning large collections when indexing or hashing is appropriate.
- Consider worst-case computational cost for externally supplied inputs.

Algorithmic complexity should be treated as part of resource-management design, not merely as an academic classification.

---

## 49. Performance Considerations

When performance matters, both asymptotic analysis and empirical measurement are useful.

Asymptotic analysis answers:

> How does computational work grow as the input becomes large?

Profiling and benchmarking answer:

> How long does this implementation take under a particular environment and workload?

Neither completely replaces the other.

A production performance investigation should consider:

- Input scale.
- Typical input distribution.
- Worst-case input.
- Allocation behavior.
- Cache locality.
- Data structures.
- Function-call overhead.
- I/O operations.
- Concurrency.
- System resource constraints.

A theoretically faster algorithm can also have larger constants or more complicated memory behavior.

---

## 50. Design Trade-Offs

### Time vs Space

Hash-based approaches often use additional memory to reduce expected lookup time.

A duplicate-detection algorithm can move from:

`O(n²)` time and `O(1)` additional space

toward:

`O(n)` expected time and `O(n)` additional space.

### Worst Case vs Average Case

An algorithm can have strong average performance but a weak worst-case guarantee.

The appropriate choice depends on application requirements.

### Exact Counts vs Asymptotic Growth

Exact operation counts are useful for small inputs and low-level optimization.

Asymptotic complexity is more useful for understanding scalability.

### Algorithm vs Implementation

Two implementations can have identical asymptotic complexity and substantially different practical performance.

### Input Assumptions

Sorted data, bounded integer ranges, and random-access structures can enable loop patterns with significantly better complexity.

Such assumptions must be explicitly documented.

---

## 51. Systematic Method for Analyzing Any Loop

A reliable loop-analysis procedure is:

### Step 1: Identify Input Size

Determine what `n` represents.

For multi-dimensional problems, identify all independent dimensions.

### Step 2: Analyze Each Loop Separately

Determine the number of iterations of every loop.

Ask whether the bound is:

- Constant.
- Linear.
- Logarithmic.
- Polynomial.
- Data-dependent.
- Dependent on another loop.

### Step 3: Determine Loop Relationships

For nested loops, ask whether their costs multiply.

For consecutive loops, add their costs.

For dependent loops, construct a summation.

### Step 4: Analyze State Changes

Look for:

- `+ constant`
- `- constant`
- `* constant`
- `/ constant`
- Monotonic pointers
- Changing bounds
- Early exits

These often determine whether the loop is linear, logarithmic, or something more complicated.

### Step 5: Analyze the Body

The loop body may contain another algorithm or expensive operation.

Do not assume the body is `O(1)` without justification.

### Step 6: Account for Early Termination

Calculate best and worst cases where relevant.

### Step 7: Combine Terms

Add sequential costs and multiply independent nested costs where appropriate.

### Step 8: Simplify

Remove constant factors and lower-order terms to obtain the asymptotic class.

### Step 9: Analyze Space Separately

Determine whether the loop creates additional data structures or only uses fixed-size variables.

### Step 10: Verify Correctness and Termination

A complexity derivation is meaningful only for a correctly functioning finite algorithm.

---

## 52. Integrated Example

The script contains an integrated example consisting of:

1. A linear loop.
2. A linear outer loop with a logarithmic inner loop.
3. A triangular dependent loop.

Their complexities are:

`O(n)`

`O(n log n)`

`O(n²)`

The combined complexity is:

`O(n + n log n + n²)`

The dominant term is:

`n²`

Therefore the complete algorithm is:

`O(n²)`

This illustrates the importance of analyzing each loop independently before combining the results.

---

## 53. Testing and Validation

The script contains executable assertions covering:

- Linear sums.
- Nested-loop counts.
- Triangular sums.
- Logarithmic loops.
- Divisor counting.
- Prime testing.
- Binary search.
- Sorting.
- Duplicate detection.

Complexity analysis should be accompanied by correctness testing.

A program that produces incorrect results can still have a perfectly valid mathematical operation count, but that complexity analysis does not establish that the intended problem has been solved.

---

## 54. Practical Loop-Analysis Checklist

When analyzing a new algorithm, ask:

1. What is the input size?
2. Are there multiple independent input dimensions?
3. How many times does each loop execute?
4. Are loops consecutive or nested?
5. Are nested bounds independent?
6. Does an inner bound depend on an outer variable?
7. Does a variable grow or shrink geometrically?
8. Is an inner pointer reset or globally monotonic?
9. What is the cost of the loop body?
10. Can execution terminate early?
11. What are the best and worst cases?
12. What summation represents the total work?
13. Which term dominates?
14. What is the auxiliary space?
15. Can input size cause resource-exhaustion problems?
16. Does the loop always terminate?
17. Are the assumptions about sorting, indexing, or data structures valid?
18. Does empirical performance support the theoretical analysis for the intended workload?
