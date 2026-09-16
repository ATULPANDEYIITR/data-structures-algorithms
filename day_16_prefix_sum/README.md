# Prefix Sum

Prefix sum is a preprocessing technique for converting repeated cumulative calculations into constant-time range queries. The central idea is simple: calculate cumulative values once, then obtain a range result by subtracting two previously calculated prefix values.

The technique is especially useful when a dataset is relatively static and many queries ask for the sum of different contiguous ranges.

This repository contains three complementary implementations:

- Python provides a broad educational implementation covering one-dimensional and multidimensional prefix sums, subarray problems, difference arrays, Fenwick trees, segment trees, testing, and performance considerations.
- JavaScript demonstrates the same family of ideas in an application-oriented language, including `Map`, typed numeric considerations, immutable query structures, and dynamic data structures.
- C++ presents an industry-style telemetry analytics case study in which sensor measurements are queried repeatedly and occasionally updated.

## Topic introduction

Given an array:

`[4, 2, 7, 1, 5, 3]`

a prefix sum array can be represented as:

`[0, 4, 6, 13, 14, 19, 22]`

The first element is zero. Each following element contains the sum of all original elements before that position.

For example:

`prefix[5] = 4 + 2 + 7 + 1 + 5 = 19`

The sum from index `1` through index `4` is:

`prefix[5] - prefix[1] = 19 - 4 = 15`

This transforms a range-sum operation from repeatedly scanning elements to a constant-time arithmetic operation after preprocessing.

## Fundamental terminology

### Array

An array stores values at indexed positions. Prefix sums are normally introduced using arrays because contiguous ranges have a natural left and right boundary.

### Prefix

A prefix is a portion of a sequence beginning at its first element.

For an array `A`, a prefix ending at position `i` contains the elements from the beginning through `i`.

### Prefix sum

A prefix sum stores cumulative sums.

Using an extra leading zero is a common implementation convention:

`P[0] = 0`

`P[i + 1] = P[i] + A[i]`

This makes the range formula uniform.

### Range query

A range query asks for an operation over a contiguous interval.

For example:

`sum(A[2..5])`

asks for the sum of elements at indices 2 through 5.

### Static data

Static data does not change after preprocessing. Prefix sums are particularly effective for static data.

### Dynamic data

Dynamic data can change after preprocessing. A basic prefix array does not efficiently support arbitrary point changes because changing one element potentially invalidates every later prefix value.

Fenwick trees and segment trees address this limitation.

## Core one-dimensional formula

For an array `A` and prefix array `P`:

`P[i] = A[0] + A[1] + ... + A[i - 1]`

An inclusive range `[L, R]` is:

`A[L] + A[L + 1] + ... + A[R]`

The prefix representation is:

`P[R + 1] - P[L]`

The `R + 1` index occurs because `P` contains one extra leading element.

This indexing convention eliminates special cases for ranges beginning at zero.

## Why preprocessing helps

Suppose an array contains `n` elements and there are `q` range-sum queries.

A direct implementation may scan every element in every query. If a typical range contains `k` elements, the query work is approximately `O(k)`. In the worst case, it is `O(n)` per query.

With prefix sums:

- preprocessing takes `O(n)`
- each range query takes `O(1)`
- storage requires `O(n)`

For many queries, this can substantially reduce repeated work.

The Python implementation explicitly compares direct range scanning with prefix-based queries.

## Python implementation

The Python implementation starts with `build_prefix_sum()`.

The function creates an array of length `n + 1`, initializes the first element to zero, and accumulates values into subsequent positions.

`prefix_range_sum()` implements:

`prefix[right + 1] - prefix[left]`

The implementation validates ranges before performing the calculation. This is important because an incorrect index can silently produce an incorrect analytical result in less defensive code.

### Negative values

Prefix sums do not require non-negative input.

For:

`[5, -3, 8, -10, 6]`

the cumulative sums naturally include negative intermediate values.

The only fundamental requirement for ordinary prefix-sum subtraction is that the aggregation operation behaves appropriately under subtraction.

## Prefix sums as counting structures

A prefix sum does not have to represent the sum of the original values.

A condition can first be transformed into binary values:

- condition true → `1`
- condition false → `0`

For example, given:

`[3, 12, 7, 18, 5, 20]`

an even-number indicator becomes:

`[0, 1, 0, 1, 0, 1]`

A prefix sum over this indicator array can answer how many even values occur in any range.

This technique generalizes to many classification queries.

## Multiple prefix arrays

The Python `StatisticsPrefix` class stores:

- cumulative count
- cumulative sum
- cumulative square sum

The additional arrays permit range calculations such as:

- count
- sum
- mean
- population variance

For variance, the implementation uses:

`E[X²] - E[X]²`

The method is useful when repeated statistical queries are required over immutable observations.

Floating-point numerical error should be considered for large or highly variable datasets. Production numerical systems may require more specialized statistical algorithms depending on precision requirements.

## Weighted prefix sums

Prefix sums can accumulate derived quantities.

If each value has a corresponding weight, the contribution can be:

`value × weight`

A prefix array of these contributions can answer weighted range totals in constant time.

This pattern appears in areas such as:

- weighted revenue
- resource consumption
- workload accounting
- inventory valuation
- weighted sensor measurements

The important concept is that the prefix structure stores the quantity actually needed by the query rather than necessarily storing the original values.

## Prefix XOR

The Python and JavaScript implementations also demonstrate prefix XOR.

XOR has an important property:

`x XOR x = 0`

and:

`x XOR 0 = x`

Consequently, a range XOR can be recovered using two prefix XOR values:

`prefix[right + 1] XOR prefix[left]`

This illustrates a broader principle: prefix techniques can work with operations that have a suitable inverse or cancellation property, not only ordinary addition.

## Two-dimensional prefix sums

A one-dimensional prefix sum handles intervals.

A two-dimensional prefix sum handles rectangles in a matrix.

For matrix `A`, the prefix table represents the sum of the rectangle between the origin and a particular position.

The recurrence is:

`P[r][c] = A[r-1][c-1] + P[r-1][c] + P[r][c-1] - P[r-1][c-1]`

The final subtraction is required because the upper-left region was included twice.

### Rectangle query

For an inclusive rectangle from `(top, left)` to `(bottom, right)`:

`P[bottom + 1][right + 1]`
`- P[top][right + 1]`
`- P[bottom + 1][left]`
`+ P[top][left]`

This is a two-dimensional inclusion-exclusion calculation.

After preprocessing:

- construction: `O(rows × columns)`
- rectangle query: `O(1)`
- memory: `O(rows × columns)`

Applications include:

- image processing
- heat maps
- geographical grids
- spatial statistics
- occupancy maps
- game boards
- matrix analytics

## Three-dimensional prefix sums

The Python implementation extends the same idea to a three-dimensional volume.

The principle is unchanged, but inclusion-exclusion contains more terms.

A three-dimensional prefix structure can answer rectangular-volume queries in constant time after preprocessing.

The trade-off is memory. A volume containing `D × R × C` cells requires storage proportional to that volume.

## Subarray sums

Prefix sums become especially useful when the problem is not simply to answer explicit ranges but to identify ranges satisfying a condition.

Suppose:

`P[j] - P[i] = target`

Then:

`P[i] = P[j] - target`

The Python and JavaScript implementations use a frequency map to count previous prefix sums matching the required value.

This produces an `O(n)` expected-time algorithm for counting subarrays whose sum equals a target, assuming normal hash-table behavior.

It works with negative numbers, which is an important distinction from sliding-window approaches that rely on non-negative values.

## Longest subarray with a target sum

To find the longest subarray whose sum equals a target, the implementation stores the earliest position at which each prefix sum occurred.

For a current prefix sum `P`:

`needed = P - target`

If `needed` occurred at an earlier position, the interval between those two prefix positions has the target sum.

Keeping the earliest occurrence maximizes the possible length.

This produces an expected `O(n)` solution using a hash map.

## Divisibility using prefix remainders

A related technique counts subarrays whose sums are divisible by a number `k`.

If two prefix sums have the same remainder modulo `k`, their difference is divisible by `k`.

Therefore, a frequency table of prefix remainders can count qualifying subarrays.

This is an example of transforming a range property into a relationship between two prefix states.

## Difference arrays

A difference array reverses the direction of the prefix relationship.

Suppose many operations add a value to every element in an interval:

`[L, R] += X`

Updating every element individually is potentially expensive.

Instead, record:

`difference[L] += X`

`difference[R + 1] -= X`

After all operations have been recorded, take a prefix sum of the difference array.

The resulting prefix values are the final array.

This provides:

- range update: `O(1)`
- final reconstruction: `O(n)`

Difference arrays are particularly useful when many range updates are performed before the resulting array is needed.

## Coordinate compression

The Python implementation includes interval aggregation with coordinate compression.

This technique is useful when coordinates are numerically large but only a relatively small number of boundaries matter.

The process is:

1. Collect relevant interval endpoints.
2. Sort and deduplicate them.
3. Map each endpoint to a compact index.
4. Store range changes using a difference array.
5. Prefix-accumulate the changes.
6. Interpret each adjacent coordinate pair as a segment.

This combination is common in interval and sweep-line algorithms.

## Immutable range-query structure

`PrefixRangeQuery` in Python and JavaScript encapsulates an immutable dataset and its prefix array.

This separates preprocessing from query execution.

For workloads such as reporting, analytics, and historical measurements, this design can be appropriate when data is loaded once and queried repeatedly.

The primary assumption is that the underlying values do not change.

## Dynamic updates

A standard prefix array is not designed for frequent point updates.

If:

`A[k]`

changes, every prefix position after `k` is affected.

Rebuilding the complete prefix array takes `O(n)`.

For workloads containing both updates and queries, this can be inefficient.

The Python, JavaScript, and C++ implementations therefore introduce a Fenwick tree.

## Fenwick tree

A Fenwick tree, also called a Binary Indexed Tree, supports:

- point update: `O(log n)`
- prefix sum: `O(log n)`
- range sum: `O(log n)`

It stores partial cumulative information rather than every complete prefix value.

The internal index manipulation uses the least significant set bit to move between related tree nodes.

A Fenwick tree generally uses less implementation complexity and memory than a fully general segment tree when only point updates and additive range queries are required.

## Segment tree

The Python and JavaScript implementations also include segment trees.

A segment tree recursively represents intervals and stores an aggregate for each node.

For range sums, it supports:

- construction: `O(n)`
- point update: `O(log n)`
- range query: `O(log n)`

Segment trees use more memory and implementation complexity than simple prefix sums, but they are more general.

They can support many associative operations, including variants of:

- sum
- minimum
- maximum
- greatest common divisor

With lazy propagation, segment trees can also support more advanced range-update workloads.

## Prefix sums versus Fenwick trees versus segment trees

| Requirement | Prefix sum | Fenwick tree | Segment tree |
|---|---:|---:|---:|
| Static range sum | O(1) query | O(log n) | O(log n) |
| Preprocessing | O(n) | O(n log n) in this implementation | O(n) |
| Point update | O(n) rebuild | O(log n) | O(log n) |
| Range sum | O(1) | O(log n) | O(log n) |
| Implementation complexity | Low | Moderate | Higher |
| General aggregate operations | Limited | Limited to suitable operations | Broad |
| Memory | O(n) | O(n) | O(n) |

The appropriate structure depends on the workload.

For static data with many range-sum queries, a prefix sum is straightforward and efficient.

For frequent point updates with additive queries, a Fenwick tree is often appropriate.

For more general interval operations and complex aggregate requirements, a segment tree may be suitable.

## C++ telemetry case study

The C++ implementation models a sensor analytics service.

The domain object contains:

- a sensor identifier
- a sequence of integer measurements

The service provides analytical operations over measurement intervals.

### Direct baseline

`DirectRangeCalculator` represents the simplest implementation.

For every query it scans the requested interval.

This implementation is useful as a correctness baseline and as a comparison point for optimized approaches.

### Immutable prefix layer

`PrefixSumArray` preprocesses the complete measurement sequence.

The analytics service can then answer static interval sums in constant time.

This is appropriate for historical snapshots where the data is not expected to change.

### Statistical layer

`PrefixStatistics` stores cumulative:

- count
- sum
- squared values

The service can therefore calculate interval mean and variance without rescanning the measurement interval.

### Dynamic layer

The case study also models an operational correction.

When one measurement changes, the immutable prefix array is not modified. The dynamic Fenwick tree receives the difference between the old and new values.

For example, if a measurement changes from `18` to `25`, the tree receives:

`+7`

This updates all relevant Fenwick aggregates in `O(log n)` time.

This separation is an important architectural decision: immutable analytical snapshots and mutable operational state have different optimization requirements.

## Two-dimensional C++ analysis

`MatrixPrefixSum` models regional measurements.

The matrix can represent spatial or organizational regions, and rectangle queries can calculate aggregate measurements over rectangular areas.

The implementation validates that the matrix is rectangular before construction.

The rectangle formula uses inclusion-exclusion to prevent overlapping regions from being counted twice.

## Difference-array C++ component

`RangeUpdateAccumulator` models repeated interval-wide changes such as maintenance load, planned capacity, or scheduled adjustments.

Each range update modifies only two boundary positions.

The complete result is materialized once with a prefix pass.

This design is efficient when many updates occur before the resulting array is consumed.

## JavaScript-specific considerations

JavaScript provides several useful mechanisms for prefix-based algorithms.

`Map` is used for prefix-frequency algorithms because prefix values can be negative or otherwise unsuitable for array indexing.

For example, the subarray-target algorithm stores:

`prefix sum → frequency`

The `Map` approach avoids assuming a small numeric domain.

### Number precision

JavaScript's ordinary `Number` uses IEEE-754 double-precision floating-point representation.

Integer calculations are exact only through:

`Number.MAX_SAFE_INTEGER`

For prefix sums involving values that can exceed that exact integer range, `BigInt` can be used.

The JavaScript implementation demonstrates a separate `BigInt` prefix array.

`Number` and `BigInt` should not be mixed directly in arithmetic expressions. A production application should establish its numeric representation based on domain constraints before implementing cumulative calculations.

## Indexing considerations

Many prefix-sum errors are indexing errors rather than mathematical errors.

A robust convention is:

`prefix.length = values.length + 1`

and:

`prefix[0] = 0`

Then:

`rangeSum(left, right) = prefix[right + 1] - prefix[left]`

This convention handles:

- ranges starting at zero
- one-element ranges
- full-array ranges
- ranges ending at the final element

The implementations consistently use inclusive query boundaries and an exclusive-style prefix representation.

## Edge cases

Important cases include:

### Empty input

An empty one-dimensional input produces a prefix structure containing the leading zero.

A query against an empty dataset should be rejected because there is no valid inclusive range.

### One-element range

For `[L, L]`:

`prefix[L + 1] - prefix[L]`

returns exactly the element at `L`.

### Full-array query

For an array of length `n`:

`prefix[n] - prefix[0]`

returns the complete sum.

### Negative values

Negative values are valid for ordinary prefix sums and for the hash-map subarray algorithms.

### Negative targets

Target-sum algorithms should not assume that the target is positive.

### Negative array elements

Algorithms based on prefix differences continue to work with negative elements. Some alternative techniques, such as certain sliding-window methods, require stronger assumptions and should not be substituted without checking those assumptions.

### Large numeric values

Potential integer overflow must be considered in languages with fixed-width integer types.

C++ code uses `std::int64_t`, but even 64-bit arithmetic has limits.

### Large matrices

A two-dimensional prefix array requires additional memory proportional to the entire matrix.

For very large matrices, memory consumption can become the primary constraint.

## Common mistakes

### Off-by-one errors

Using `prefix[right] - prefix[left]` with an inclusive right endpoint is a common mistake when the prefix array contains a leading zero.

The correct formula for the convention used here is:

`prefix[right + 1] - prefix[left]`

### Forgetting the leading zero

A prefix array without the leading zero can still work, but it creates special cases for ranges starting at index zero.

### Incorrect two-dimensional inclusion-exclusion

The upper-left overlap must be added back after subtracting the upper and left regions.

The correct rectangle pattern is:

`total - above - left + overlap`

### Using prefix sums for mutable data without considering update cost

A prefix array is not automatically the correct data structure merely because queries involve sums.

If values change frequently, update cost must be considered.

### Assuming prefix sums solve every range problem

Prefix sums are highly effective for suitable aggregate operations, but they do not automatically solve:

- arbitrary range minimum queries
- arbitrary range median queries
- non-invertible aggregate operations

Other data structures may be required.

### Ignoring overflow

The mathematical prefix sum can be valid while the selected machine integer type overflows.

The implementation type must be chosen from realistic maximum cumulative values.

## Performance considerations

For `n` values and `q` queries:

Naive repeated range scanning can approach:

`O(nq)`

in the worst case.

Static prefix sums provide:

`O(n + q)`

time after preprocessing, because construction is `O(n)` and every query is `O(1)`.

For two-dimensional data containing `R × C` cells:

- preprocessing: `O(RC)`
- rectangle query: `O(1)`
- storage: `O(RC)`

For Fenwick trees:

- update: `O(log n)`
- prefix query: `O(log n)`
- range query: `O(log n)`

For segment trees:

- construction: `O(n)`
- point update: `O(log n)`
- range query: `O(log n)`

The correct choice depends on the ratio between reads, updates, memory capacity, and the aggregate operation.

## Memory considerations

A prefix array requires an additional `n + 1` values.

A two-dimensional prefix table requires approximately `(R + 1) × (C + 1)` values.

For very large datasets, alternatives may include:

- storing only the required dimensional summaries
- processing data in blocks
- using compressed representations
- using database-side aggregation
- using streaming algorithms when exact arbitrary range queries are not required

Such alternatives change the supported query model and should be selected according to requirements.

## Security and reliability considerations

Prefix-sum calculations are normally algorithmic rather than security-sensitive, but production systems still require defensive handling.

Input validation should cover:

- negative indices
- reversed ranges
- indices outside the dataset
- malformed matrix dimensions
- unsupported numeric values
- integer overflow
- unexpected update operations

If range parameters originate from external requests, they should be validated before accessing memory or collections.

For JavaScript services, extremely large integer values should not silently pass through ordinary `Number` calculations when exact integer arithmetic is required.

For C++, invalid indices must not be allowed to produce undefined behavior.

## Testing strategy

The Python and C++ implementations compare optimized range calculations with brute-force calculations.

This is a strong testing pattern for prefix algorithms because the brute-force implementation is simple enough to serve as a reference.

Randomized testing can generate:

- random arrays
- random negative and positive values
- random query boundaries
- random matrices
- random rectangles

Each optimized result can then be compared against direct computation.

This approach helps detect subtle indexing errors.

## Practical applications

Prefix sums and closely related cumulative techniques appear in:

- financial time-series analysis
- transaction aggregation
- inventory systems
- telemetry systems
- sensor analytics
- image processing
- spatial data processing
- geographic grids
- workload analysis
- scheduling
- competitive programming
- database query optimization
- histogram analysis
- event counting
- cumulative statistics

The core pattern is not limited to arithmetic addition. The important idea is preprocessing repeated structure so that later queries avoid recomputing the same information.

## Important distinctions

### Prefix sum versus cumulative total

A cumulative total describes the running accumulation itself.

A prefix-sum data structure organizes those cumulative values specifically so that two prefix states can be combined to answer a range query efficiently.

### Prefix sum versus suffix sum

A prefix sum accumulates from the beginning.

A suffix sum accumulates from the end.

Both can answer useful queries, but they naturally favor different query orientations.

### Prefix sum versus difference array

A prefix sum converts original values into cumulative values.

A difference array represents changes at boundaries and uses a later prefix operation to reconstruct the resulting values.

The two concepts are closely related and often appear together.

### Prefix sum versus Fenwick tree

A prefix array is simplest for static data.

A Fenwick tree stores hierarchical partial sums so that point updates can be performed efficiently.

### Prefix sum versus segment tree

A segment tree provides a more general hierarchical range structure.

It usually has greater implementation complexity than a basic prefix array and can support dynamic range operations that ordinary prefix sums cannot.

## Best practices

Use a leading zero in one-dimensional prefix arrays when possible.

Define whether query boundaries are inclusive or exclusive before writing the implementation.

Keep index conventions consistent across functions.

Validate externally supplied ranges.

Use an integer type large enough for expected cumulative values.

Benchmark complete workloads rather than assuming an asymptotic improvement will dominate every small input.

Use brute-force implementations as correctness references during development.

Separate immutable snapshots from mutable data when an application has both historical analytics and live corrections.

For multidimensional structures, verify matrix dimensions before preprocessing.

For hash-map prefix algorithms, account for the memory used by distinct prefix states.

## Conceptual pattern

Many prefix-sum problems can be reduced to the following sequence:

1. Identify the quantity that is repeatedly recomputed.
2. Express that quantity as a cumulative state.
3. Precompute the cumulative state.
4. Determine how two cumulative states produce the desired range result.
5. Choose an appropriate data structure if updates are required.
6. Validate boundary conditions and numeric limits.

The most important formula for the basic one-dimensional case remains:

`range(L, R) = prefix[R + 1] - prefix[L]`

The Python, JavaScript, and C++ implementations demonstrate how that simple relationship scales into multidimensional queries, frequency analysis, subarray algorithms, range updates, and dynamic data structures.
