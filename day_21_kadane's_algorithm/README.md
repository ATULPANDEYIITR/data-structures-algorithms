# Kadane's Algorithm

## Topic overview

Kadane's algorithm is a linear-time technique for finding the maximum sum of a non-empty contiguous subarray.

Given an array such as `[−2, 1, −3, 4, −1, 2, 1, −5, 4]`, the objective is to select a contiguous range whose elements have the largest possible sum.

For this example, the maximum sum is `6`, produced by `[4, −1, 2, 1]`.

The problem looks simple, but it provides an important introduction to dynamic programming, state compression, prefix sums, sliding windows, monotonic queues, circular arrays, and several useful variations.

This project contains three implementations:

- Python provides a broad educational implementation with several maximum-subarray variants.
- JavaScript demonstrates the same algorithmic ideas while incorporating JavaScript-specific array, `Map`, class, runtime, and numeric behavior.
- C++ develops an industry-style measurement-analysis system using classes, `std::vector`, `std::deque`, `std::map`, validation, exceptions, streaming state, and randomized testing.

The implementations treat a subarray as a non-empty contiguous sequence unless a variation explicitly defines another constraint.

## Fundamental terminology

### Array

An array is an ordered collection of values.

For example:

`[4, -2, 7, 1]`

The elements have positions called indices:

| Index | Value |
|---:|---:|
| 0 | 4 |
| 1 | -2 |
| 2 | 7 |
| 3 | 1 |

Most examples in this project use zero-based indexing.

### Subarray

A subarray is a contiguous portion of an array.

For `[1, 2, 3]`, valid non-empty subarrays include:

- `[1]`
- `[2]`
- `[3]`
- `[1, 2]`
- `[2, 3]`
- `[1, 2, 3]`

`[1, 3]` is not a subarray because the elements are not contiguous.

### Subsequence

A subsequence does not require contiguity.

For `[1, 2, 3]`, `[1, 3]` is a subsequence but not a subarray.

This distinction is fundamental. Kadane's algorithm solves the contiguous maximum-sum problem, not the general maximum-subsequence problem.

### Prefix sum

A prefix sum stores cumulative totals.

For:

`[3, -1, 5, 2]`

the prefix representation can be:

`[0, 3, 2, 7, 9]`

The extra initial zero means that the sum of `[left, right)` can be calculated as:

`prefix[right] - prefix[left]`

Prefix sums are especially useful for constrained subarray problems.

### Maximum subarray

The maximum subarray is the non-empty contiguous subarray with the greatest sum.

### Minimum subarray

The minimum subarray is the non-empty contiguous subarray with the smallest sum.

The minimum problem is almost identical to the maximum problem. The important change is replacing the maximization operations with minimization operations.

## Why the problem is not trivial

A straightforward solution can enumerate every possible start and end position.

An array of length `n` contains:

`n(n + 1) / 2`

non-empty contiguous subarrays.

That number grows quadratically.

If every candidate is also summed from its beginning, the resulting implementation can take `O(n^3)` time.

The Python implementation contains such a brute-force reference implementation because it is useful for understanding the problem and for testing the optimized algorithm.

A better quadratic implementation maintains the current sum while extending a candidate range. This reduces the time complexity to `O(n^2)`.

Prefix sums also allow each individual range sum to be calculated in `O(1)`, but all possible ranges still have to be examined, so the total remains `O(n^2)`.

Kadane's algorithm reduces the problem to `O(n)`.

## The central idea of Kadane's algorithm

For every array position, consider the best subarray that must end at that position.

Suppose the current value is `x`.

There are only two fundamental choices:

1. Start a new subarray at `x`.
2. Extend the best subarray ending immediately before `x`.

Therefore:

`best_ending_here = max(x, best_ending_here + x)`

The global answer is the largest value ever produced by `best_ending_here`.

This is the essential recurrence behind Kadane's algorithm.

## Dynamic programming interpretation

Kadane's algorithm can be understood as dynamic programming with aggressive state compression.

A traditional dynamic-programming solution might store:

`dp[i] = maximum sum of a subarray ending at index i`

The recurrence is:

`dp[i] = max(numbers[i], dp[i - 1] + numbers[i])`

Only the previous state is required to calculate the next state.

Therefore, the entire `dp` array does not have to be stored.

The implementation can keep only:

- the best sum ending at the current position
- the best sum seen anywhere

This reduces auxiliary space from `O(n)` to `O(1)`.

## Why all-negative arrays require special care

Consider:

`[-8, -3, -6, -2, -5]`

The correct answer is `-2`.

The maximum-subarray problem normally requires a non-empty subarray.

A common incorrect implementation initializes the answer to zero and repeatedly performs something equivalent to:

`current = max(0, current + value)`

That implementation solves a slightly different problem in which an empty subarray is allowed.

For an all-negative array it returns `0`, even though `0` does not occur as the sum of a non-empty subarray.

The Python, JavaScript, and C++ implementations therefore initialize the state from the first element.

## Recovering the actual subarray

Finding only the maximum sum is often insufficient.

Applications may need:

- the beginning of the period
- the end of the period
- the values inside the period
- the length of the period

The index-aware implementation keeps a temporary starting position.

When starting a new subarray becomes preferable, the current start index is moved to the current position.

When a new global maximum is discovered, the current range is saved.

The Python implementation represents this result with the `SubarrayResult` data class.

The JavaScript implementation returns an object containing `sum`, `start`, `end`, and `values`.

The C++ implementation uses the `SubarrayResult` structure.

## Example

For:

`[-2, 1, -3, 4, -1, 2, 1, -5, 4]`

Kadane's algorithm identifies:

- start index: `3`
- end index: `6`
- sum: `6`
- values: `[4, -1, 2, 1]`

The important point is that the algorithm does not need to enumerate every subarray.

## Minimum subarray

The minimum version uses the same state structure.

Instead of:

`max(value, previous + value)`

use:

`min(value, previous + value)`

The global state is also minimized rather than maximized.

This gives a linear-time solution:

- Time: `O(n)`
- Auxiliary space: `O(1)`

The minimum-subarray calculation becomes especially important when solving circular maximum-subarray problems.

## Circular arrays

A circular array treats the last element as adjacent to the first element.

For example:

`[5, -3, 5]`

The circular maximum subarray can contain the first and last elements:

`[5] + [5]`

Its sum is `10`.

### Two possibilities

A circular maximum is either:

1. an ordinary non-wrapping subarray, or
2. a wrapping subarray containing the end and beginning of the array.

For the wrapping case:

`wrapping maximum = total sum - minimum subarray sum`

The reason is that removing the minimum contiguous section leaves the complementary section, which wraps around the boundary.

Therefore:

`circular maximum = max(ordinary maximum, total - minimum)`

### All-negative exception

For:

`[-3, -2, -1]`

the total is `-6` and the minimum subarray is `-6`.

The expression:

`total - minimum = 0`

does not represent a valid non-empty subarray.

Therefore, if the ordinary maximum is negative, the circular maximum implementation returns the ordinary maximum directly.

This is one of the most important edge cases in circular Kadane implementations.

## Circular minimum subarray

The same complement principle works in the opposite direction.

A wrapping minimum can be represented as:

`total sum - maximum subarray sum`

Therefore:

`circular minimum = min(ordinary minimum, total - maximum)`

The all-positive case must be handled separately because the complement could represent an empty range.

## Fixed-length maximum subarray

Sometimes the subarray length is exactly `k`.

This is not the ordinary Kadane problem because the range length is constrained.

A sliding window is appropriate.

For a window of length `k`:

`window_sum = sum(first k values)`

When the window moves one position:

`new_sum = old_sum - outgoing + incoming`

Each element enters and leaves the window once.

Therefore:

- Time: `O(n)`
- Auxiliary space: `O(1)`

The three implementations include this technique.

## Maximum subarray with at most k elements

A length restriction of at most `k` requires a different structure.

Using prefix sums:

`sum(left, right) = prefix[right] - prefix[left]`

For every right boundary, the best answer requires the smallest eligible prefix value.

The eligible left boundary must satisfy:

`right - left <= k`

A monotonic deque maintains candidate prefix indices in increasing prefix-sum order.

This produces:

- Time: `O(n)`
- Auxiliary space: `O(k)`

The deque removes:

- indices that have become too old
- indices whose prefix sums are no better than the new candidate

This is a standard example of combining prefix sums with a monotonic data structure.

## Maximum subarray with at least k elements

For a minimum length of `k`, a left boundary becomes eligible once it is at least `k` positions before the current right boundary.

The algorithm maintains the smallest eligible prefix sum.

For each right endpoint:

`best = max(best, prefix[right] - minimum_eligible_prefix)`

This gives `O(n)` time.

## Maximum product subarray

The product problem resembles maximum sum but has an important difference: multiplication by a negative value reverses ordering.

For example, a very negative product can become the largest product after multiplication by another negative number.

Therefore two states are required:

- maximum product ending here
- minimum product ending here

For each value, consider:

- the value itself
- previous maximum multiplied by the value
- previous minimum multiplied by the value

Then update both states.

The resulting algorithm is:

- Time: `O(n)`
- Space: `O(1)`

This is an important example of how changing the mathematical operation can require a richer dynamic-programming state.

## Maximum subarray with one deletion

Suppose one element may be removed.

Two states are sufficient:

`no_deletion`

and:

`one_deletion`

The first state is ordinary Kadane.

The second state represents a subarray where one value has already been removed.

For a new value, the deleted-state candidate can come from:

- an earlier deleted state extended by the new value
- the previous non-deleted state with the current value removed
- a new subarray state

The Python, JavaScript, and C++ implementations maintain these states without storing a complete dynamic-programming table.

This is another example of state compression.

## Maximum subarray after one replacement

The Python implementation also demonstrates a replacement-based state transition.

There are two states:

- no replacement has been used
- replacement has already been used

The replacement transition allows one element to be substituted with a specified value.

This is structurally similar to the one-deletion problem but represents a different operation.

The important lesson is that many Kadane variations can be constructed by defining a small number of states and carefully describing how each new element changes those states.

## Prefix sums and target-sum counting

Kadane finds the maximum sum, but prefix sums solve many other contiguous-range questions.

For a target sum `T`:

`prefix[right] - prefix[left] = T`

Rearranging:

`prefix[left] = prefix[right] - T`

Therefore, while scanning the array, the algorithm can count how many previous prefix sums equal the required value.

A frequency map stores the number of occurrences of each prefix sum.

This gives:

- Average time: `O(n)` with a hash map
- Space: `O(n)`

The C++ case study uses `std::map` for deterministic ordered storage, which gives `O(log n)` map operations. A hash table such as `std::unordered_map` would normally provide expected `O(1)` lookup and insertion.

The Python version uses a dictionary, while JavaScript uses `Map`.

## Streaming Kadane

The ordinary maximum-subarray sum does not require the entire input to remain in memory.

Only the current state is required:

- best subarray ending at the current position
- best subarray seen so far

The `StreamingKadane` classes demonstrate this pattern.

Values can arrive one at a time.

After each value, the current best result can be queried.

This is useful for:

- telemetry streams
- financial time series
- system monitoring
- event streams
- sensor measurements
- rolling analytical pipelines

The limitation is important: if the complete original subarray must later be reconstructed, additional index or storage information is required.

## Python implementation

The Python implementation is organized as a standalone study program.

It contains:

- brute-force enumeration
- incremental quadratic enumeration
- prefix-sum enumeration
- ordinary Kadane
- index recovery
- `SubarrayResult`
- minimum subarray
- circular maximum
- circular minimum
- fixed-length maximum
- at-most-k maximum
- at-least-k maximum
- maximum product
- one deletion
- one replacement
- target-sum counting
- streaming Kadane
- divide-and-conquer maximum subarray
- randomized cross-checking
- assertions
- edge-case demonstrations
- complexity comparison

The brute-force implementations are intentionally retained because a simple reference algorithm is valuable when validating an optimized algorithm.

The randomized test routine generates many small arrays and checks that multiple maximum-subarray implementations produce identical sums.

## JavaScript implementation

The JavaScript implementation emphasizes practical execution in Node.js.

It demonstrates:

- ordinary arrays
- object-based result structures
- `Map` for prefix-frequency counting
- class-based streaming state
- logical deque indexing
- validation
- deterministic assertions
- randomized verification
- `BigInt`

JavaScript's `Array` does not provide a specialized standard deque with the same interface as C++'s `std::deque`.

The at-most-k implementation therefore uses an array with a logical `head` index instead of repeatedly calling `shift()`.

Repeated `shift()` operations can cause unnecessary work because elements have to be moved or reindexed. A logical head pointer avoids that pattern.

## JavaScript numeric precision

JavaScript's ordinary `Number` type uses IEEE 754 double-precision floating-point representation.

Integer arithmetic is exact only within the safe integer range.

The important constant is:

`Number.MAX_SAFE_INTEGER`

If subarray sums can exceed the safe integer range, ordinary `Number` arithmetic can lose integer precision.

The JavaScript implementation therefore includes a `BigInt` version of Kadane's algorithm.

`BigInt` values must be written with the `n` suffix, such as `9007199254740992n`.

`Number` and `BigInt` values should not be mixed directly in arithmetic expressions.

## C++ case study

The C++ implementation models a chronological measurement-analysis system.

A sequence of signed measurements represents values such as:

- operational impact
- financial gains and losses
- resource consumption
- performance changes
- telemetry deviations
- cumulative business effects

The `MeasurementAnalyzer` class stores the input and exposes analytical operations.

The class demonstrates how a mathematical algorithm can be integrated into a larger software component instead of being presented as an isolated function.

## C++ architecture

The main components are:

### `MeasurementAnalyzer`

Responsible for calculations over a stored sequence.

It implements:

- maximum subarray
- minimum subarray
- circular maximum
- circular minimum
- exact-length maximum
- at-most-k maximum
- at-least-k maximum
- one-deletion maximum
- target-sum counting
- total sum

### `SubarrayResult`

Stores:

- sum
- start index
- end index

It also calculates the selected range length.

### `StreamingKadane`

Maintains Kadane's state as measurements arrive.

This separates the streaming use case from the stored-array analyzer.

### Reference implementation

`bruteForceMaximum` is deliberately simple.

It acts as a correctness oracle for randomized tests.

## C++ data structures

The case study uses several standard-library structures.

### `std::vector`

Used for the measurement sequence and prefix sums.

It provides contiguous storage and efficient indexed access.

### `std::deque`

Used by the at-most-k algorithm.

The deque efficiently removes candidates from both ends.

### `std::map`

Used for prefix-sum frequency counting.

The ordered map provides logarithmic lookup and insertion.

A production implementation focused purely on average lookup performance could use `std::unordered_map`, subject to its hashing behavior and operational requirements.

## C++ integer considerations

The C++ implementation uses `int64_t` for measurement values and sums.

This provides a substantially larger integer range than a typical 32-bit integer.

Even `int64_t` is not mathematically unlimited.

If the application permits values whose cumulative sum can exceed the available integer range, an appropriate larger numeric representation or checked arithmetic strategy is required.

For production systems, numeric constraints should be established from the expected domain rather than assuming that a particular integer type is always sufficient.

## Divide-and-conquer alternative

The Python implementation includes a divide-and-conquer solution.

The array is divided into:

- a left section
- a right section
- a crossing section

The answer is the maximum of those three cases.

Its time complexity is:

`O(n log n)`

Kadane's algorithm is linear and therefore asymptotically faster for the ordinary maximum-subarray problem.

The divide-and-conquer approach remains educationally useful because it demonstrates a general recursive problem-solving pattern and becomes relevant when maximum-subarray logic is integrated into more complicated divide-and-conquer structures.

## Complexity comparison

| Algorithm | Time | Auxiliary space | Main purpose |
|---|---:|---:|---|
| Repeated-sum brute force | `O(n^3)` | `O(1)` | Simple reference |
| Incremental quadratic | `O(n^2)` | `O(1)` | Improved brute force |
| Prefix-sum enumeration | `O(n^2)` | `O(n)` | Fast individual range sums |
| Kadane | `O(n)` | `O(1)` | Ordinary maximum subarray |
| Minimum Kadane | `O(n)` | `O(1)` | Minimum subarray |
| Divide and conquer | `O(n log n)` | `O(log n)` | Recursive alternative |
| Circular Kadane | `O(n)` | `O(1)` | Circular maximum |
| Fixed-length sliding window | `O(n)` | `O(1)` | Exactly k elements |
| At-most-k with deque | `O(n)` | `O(k)` | Length upper bound |
| At-least-k with prefix sums | `O(n)` | `O(n)` | Length lower bound |
| Maximum product | `O(n)` | `O(1)` | Product objective |
| One deletion | `O(n)` | `O(1)` | One removable element |
| Target-sum counting | `O(n)` expected with hashing | `O(n)` | Count target-sum ranges |

The fastest ordinary maximum-subarray solution is linear in the number of input elements.

## Edge cases

A robust implementation must explicitly consider:

### One element

For `[7]`, the answer is `7`.

For `[-7]`, the answer is `-7`.

### All negative values

The result is the largest individual element.

An implementation that initializes the answer to zero is solving a different problem.

### All positive values

The entire array is the maximum subarray.

### Zeros

Zeros do not automatically invalidate a range.

Tie-handling can affect which range is returned when several ranges have the same sum.

### Mixed positive and negative values

These are the typical inputs for which the restart-or-extend decision becomes important.

### Circular all-negative input

The complement formula must not be allowed to produce an empty subarray.

### Invalid k

For constrained problems, `k` must satisfy the required range.

The provided implementations reject invalid values rather than silently producing an incorrect result.

### Numeric overflow

Python integers automatically expand to accommodate large integers.

C++ fixed-width integers can overflow if the mathematical result exceeds their range.

JavaScript `Number` can lose integer precision outside its safe integer range.

These language differences are implementation concerns rather than differences in the underlying algorithm.

## Common mistakes

### Mistake: confusing subarrays and subsequences

A subarray must be contiguous.

### Mistake: allowing the empty subarray unintentionally

Initializing the answer to zero can produce an incorrect result for all-negative input.

### Mistake: using circular logic without the all-negative check

`total - minimum` can represent an empty complement.

### Mistake: forgetting index recovery requirements

If an application needs the actual range, the implementation must maintain start and end information.

### Mistake: using a fixed-size window for an unrestricted problem

Sliding windows work directly when the length constraint provides the required structure.

Ordinary maximum subarray does not have a fixed window size.

### Mistake: assuming maximum-product logic is identical to maximum-sum logic

Products can change sign.

Both maximum and minimum ending products are therefore needed.

### Mistake: using a large quadratic algorithm on production-sized data

An `O(n^2)` solution can be perfectly useful for teaching and testing but unsuitable for millions of elements.

### Mistake: using `shift()` repeatedly for a large JavaScript deque

A logical head index is preferable when implementing a queue-like structure with an array.

## Tie behavior

Several subarrays can have the same maximum sum.

For example:

`[1, -1, 1]`

contains multiple ranges with sum `1`.

The numerical result is unambiguous, but the exact range returned depends on the comparison rules.

Using `>` preserves the first discovered strict improvement.

Using `>=` can prefer a later equal-valued candidate.

This distinction should be specified when the actual selected range has business meaning.

## Security considerations

Kadane's algorithm itself is not a security-sensitive primitive, but implementations can still be exposed to operational risks.

Input should be validated before processing.

Applications receiving untrusted arrays should consider:

- maximum input length
- maximum numeric magnitude
- memory limits
- integer overflow
- malformed serialization
- resource exhaustion through unnecessarily expensive variants

The linear Kadane algorithm is generally much more resistant to computational growth than a quadratic or cubic enumeration approach.

For services that accept arbitrary input, complexity is therefore also an operational security consideration.

## Production implementation considerations

### Input size

For very large arrays, prefer the linear algorithm when the problem is the ordinary maximum-subarray problem.

### Memory

If only the maximum sum is needed, Kadane requires constant auxiliary space.

If the complete selected range is required, index state can still be maintained in constant auxiliary space.

If many historical results must be preserved, storage requirements become application-specific.

### Streaming

When data arrives continuously, streaming Kadane avoids retaining the entire input solely for the purpose of computing the maximum sum.

### Numeric range

Choose numeric types according to domain constraints.

Do not assume that a value type is safe simply because individual measurements fit inside it. The cumulative sum may be much larger.

### Testing

A simple brute-force implementation is useful as a test oracle for small inputs.

The provided Python, JavaScript, and C++ implementations use randomized validation patterns to compare optimized results against a simpler reference calculation.

## Why Kadane's algorithm is important

Kadane's algorithm is valuable beyond the specific maximum-subarray problem because it demonstrates a reusable algorithmic principle:

> Keep only the state that is necessary to make the next decision.

The algorithm begins with a problem containing quadratically many candidate ranges and reduces it to a single pass.

Its state is compact because the future does not need the complete history. It only needs the best result that ends at the current position.

That idea appears repeatedly in dynamic programming and state-compression techniques.

## Relationship between the implementations

The three implementations are intentionally different in emphasis.

### Python

The Python file is primarily a comprehensive algorithm laboratory.

It demonstrates multiple formulations, variations, testing techniques, result objects, and educational comparisons.

### JavaScript

The JavaScript file focuses on executable application-level behavior.

It demonstrates arrays, `Map`, classes, logical deques, streaming state, assertions, randomized tests, and `BigInt`.

### C++

The C++ program treats the problem as a reusable technical component.

It models chronological measurements using a class-based design and integrates algorithms with validation, standard-library data structures, exceptions, streaming processing, deterministic tests, and randomized verification.

The underlying mathematical principles remain the same, while the implementation concerns differ according to each language.

## Core formulas

### Ordinary maximum

`bestEndingHere = max(value, bestEndingHere + value)`

`best = max(best, bestEndingHere)`

### Ordinary minimum

`minimumEndingHere = min(value, minimumEndingHere + value)`

`minimum = min(minimum, minimumEndingHere)`

### Circular maximum

`max(ordinaryMaximum, total - minimumSubarray)`

with an all-negative special case.

### Circular minimum

`min(ordinaryMinimum, total - maximumSubarray)`

with an all-positive special case.

### Fixed-length window

`newWindow = oldWindow - outgoing + incoming`

### Prefix range sum

`sum(left, right) = prefix[right] - prefix[left]`

### Maximum product

Track both:

- maximum product ending here
- minimum product ending here

### One deletion

Track:

- best state without deletion
- best state with one deletion

These formulas provide a compact representation of the principal techniques implemented in the project.
