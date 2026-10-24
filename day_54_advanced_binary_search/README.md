# Advanced Binary Search

This project develops binary-search techniques for data structures whose ordering is more complicated than a single ascending array.

The implementations cover:

- ordinary sorted arrays
- rotated sorted arrays
- rotated sorted arrays containing duplicates
- bitonic arrays
- globally sorted matrices
- matrices sorted independently by rows and columns
- lower-bound and upper-bound range queries

The central engineering principle is that binary search is not simply a loop that compares a target with a middle element. It is a method for preserving an ordering invariant while eliminating a provably impossible portion of the search space.

## Problem Domain

A conventional binary search assumes a monotonic ordering:

`a[0] <= a[1] <= ... <= a[n-1]`

A rotated array breaks the global ordering while retaining two locally sorted regions. A bitonic array changes direction exactly once. A matrix may encode a two-dimensional ordering that can either be flattened logically or searched using a staircase strategy.

The correct algorithm depends on the structural invariant known about the input.

| Structure | Main invariant | Typical search complexity |
|---|---|---:|
| Sorted array | Entire sequence is ordered | `O(log n)` |
| Rotated unique array | At least one half is sorted | `O(log n)` |
| Rotated array with duplicates | A sorted half may be ambiguous | `O(log n)` average, `O(n)` worst case |
| Bitonic array | Sequence changes direction once | `O(log n)` |
| Globally sorted matrix | Matrix can be viewed as one sorted sequence | `O(log(mn))` |
| Row-column sorted matrix | Rows and columns are monotonic | `O(m + n)` |

The algorithms are deliberately separated because applying an invariant from one structure to another can eliminate the target incorrectly.

## Search-Space Invariants

The important question in each iteration is not merely which value is smaller. It is which region can still contain the target.

For a normal sorted array:

`left ... mid ... right`

If `target > values[mid]`, every index at or below `mid` can be rejected.

For a rotated array, the midpoint does not necessarily divide the data into two globally ordered pieces. Instead, one of the two halves is guaranteed to be sorted when all values are distinct.

For a bitonic sequence, the comparison between `values[mid]` and `values[mid + 1]` identifies which side contains the peak.

For a globally sorted matrix, a two-dimensional coordinate can be mapped to a virtual one-dimensional position without physically copying the matrix.

## Python Implementation

The Python implementation provides independent functions for each structural case.

`binary_search` implements the conventional half-interval reduction. The implementation uses `left + (right - left) // 2` so midpoint calculation does not depend on directly adding two potentially large indexes.

`rotated_binary_search` determines whether the left or right half is sorted. Once the sorted half is known, the target range determines whether that half can be discarded.

`rotated_binary_search_with_duplicates` handles the ambiguity caused by equal boundary values. When `values[left]`, `values[mid]`, and `values[right]` are equal, the algorithm cannot infer a useful sorted half. It therefore contracts the boundaries. This preserves correctness but means the worst case can become linear.

`find_peak_bitonic` finds the maximum by checking the local slope between adjacent elements. An increasing slope means the peak lies to the right; a decreasing slope means the peak is at or to the left of the midpoint.

`search_bitonic` first finds the peak and then performs one ascending binary search and one descending binary search.

`search_matrix` treats a row-major globally sorted matrix as a virtual one-dimensional array. `divmod` converts a virtual index into a matrix row and column.

`search_row_column_matrix` implements the staircase method. It starts at the top-right cell. A value larger than the target eliminates the current column; a value smaller than the target eliminates the current row.

`lower_bound` and `upper_bound` provide insertion-boundary primitives. Together they locate the complete range of equal values without scanning the range linearly.

The script also uses:

- `dataclass` for structured results
- exceptions for invalid structures
- assertions for executable verification
- comparison counters for algorithmic observation
- rectangular-matrix validation
- explicit empty-input handling

## JavaScript Implementation

The JavaScript implementation uses objects for structured results and classes for validation errors and reusable search policies.

The search algorithms are intentionally not a line-by-line translation of the Python file. JavaScript's runtime model is used to keep the implementation compact while still making the search state explicit.

The implementation includes:

- `SearchError` for invalid input
- result objects containing algorithm name, index, value, and comparison count
- `Map`- and `Set`-compatible application structure through normal JavaScript objects and arrays
- explicit matrix validation
- duplicate-aware rotated searching
- range discovery using lower and upper bounds
- executable assertions through `console.assert`

The result objects make search outcomes distinguishable from exceptions. A missing target is a normal search result, while malformed input is treated as a validation failure.

## C++17 Implementation

The C++17 implementation treats the search functions as a small algorithmic engine.

`SearchResult` uses `std::optional` to distinguish a missing index from a valid index such as zero. This is safer than using a sentinel index because zero is a legitimate result.

`SearchError` provides an explicit validation exception.

The matrix algorithms operate directly on `std::vector<std::vector<int>>`. No matrix flattening is performed for the globally sorted case. The virtual index is translated into:

`row = mid / columns`

`column = mid % columns`

The C++ implementation also takes care with unsigned indexes. When decrementing a `size_t`, the code checks for zero first. This prevents unsigned underflow from turning an intended termination condition into a very large index.

The program reports comparison counts and uses `assert` statements to validate expected positions and ranges.

## Java 17 Implementation

The Java implementation uses explicit domain abstractions to represent search policies.

`SearchResult` is a Java record, giving the result object immutable value semantics.

`SearchPolicy` is an interface implemented by:

- `StandardBinarySearch`
- `RotatedSearch`
- `RotatedSearchWithDuplicates`

This separates the selection of a search strategy from the caller that executes it.

`BitonicSearch` encapsulates peak detection and the two directional searches. `MatrixSearch` owns rectangular-matrix validation and provides separate policies for globally sorted and row-column sorted matrices.

`OptionalInt` represents optional indexes and values without using nullable boxed integers.

The Java implementation also demonstrates a practical enterprise-style distinction between:

- invalid input
- a valid search with a matching target
- a valid search where the target is absent

These states should not be conflated because a missing target is expected application behavior, while malformed data represents a contract violation.

## PostgreSQL Implementation

The PostgreSQL implementation models advanced-search input as relational data rather than implementing procedural binary-search loops inside SQL.

The `search_cases` table records the known structural property of each search problem.

The `search_structure` enum distinguishes:

- `SORTED_ARRAY`
- `ROTATED_ARRAY`
- `ROTATED_DUPLICATES`
- `BITONIC_ARRAY`
- `GLOBAL_MATRIX`
- `ROW_COLUMN_MATRIX`

The `search_values` table stores sequence positions and, when applicable, matrix coordinates.

The relationship is:

`search_cases`
`    -> search_values`
`         -> ordered positions`
`         -> optional matrix coordinates`

The schema uses:

- primary keys
- foreign keys
- check constraints
- indexes
- an enum representing search structures
- a validation trigger
- SQL and PL/pgSQL functions
- a materialized reporting view
- transactional validation

The `ordered_values` view uses `lag` to expose the previous value within a sequence. This is useful when checking monotonic assumptions.

`validate_sorted_case` verifies whether a sequence is non-decreasing.

`find_value_range` returns the first and last stored positions for a target. This corresponds conceptually to lower-bound and upper-bound range discovery.

`global_matrix_match` retrieves a target from matrix coordinates without copying the matrix into a different representation.

The materialized `case_statistics` view provides reusable reporting information such as element count, minimum, maximum, and target frequency.

The transaction section demonstrates that invalid matrix coordinates are rejected by the trigger while the surrounding transaction can safely recover through a savepoint.

## Matrix Search Distinctions

Two matrix problems are represented because their ordering guarantees are different.

### Globally Sorted Matrix

A matrix such as:

`1  3  5  7`
`10 12 14 16`
`20 22 24 26`

can be viewed as a sorted sequence:

`1, 3, 5, 7, 10, 12, 14, 16, 20, 22, 24, 26`

The implementation does not physically flatten it. Instead, a virtual index is converted into a row and column.

This produces `O(log(mn))` search complexity.

### Row-Column Sorted Matrix

A matrix such as:

`1   4   7  11`
`2   5   8  13`
`3   6   9  15`
`10 12  14  18`

is not necessarily globally sorted under row-major traversal.

It is sorted independently across rows and columns.

Starting from the top-right cell gives a useful elimination rule:

- value greater than target: eliminate the current column
- value smaller than target: eliminate the current row
- equal value: target found

This requires at most `m + n` movements.

## Rotated Arrays

A rotated sorted array preserves enough structure for binary search when the values are unique.

For example:

`2  8  10  13  18  25`

can become:

`13 18 25 2 8 10`

The midpoint may lie in either sorted region.

The key decision is:

`values[left] <= values[mid]`

If true, the left half is sorted. The target can then be tested against that half's boundaries.

Duplicates change the problem. Consider:

`2 5 6 0 0 1 2`

When the left boundary, midpoint, and right boundary contain the same value, neither half can safely be classified using those boundaries alone.

The duplicate-aware implementation therefore removes equal boundaries. This maintains correctness but sacrifices the strict logarithmic worst-case guarantee.

## Bitonic Search

A strictly bitonic sequence has one direction change:

`2 5 9 14 19 16 11 4`

The peak is `19`.

The peak search compares adjacent values around the midpoint.

If:

`values[mid] < values[mid + 1]`

the sequence is still rising at that location, so the peak must occur farther right.

Otherwise the peak is at or to the left.

After finding the peak, the array consists of two independently searchable monotonic regions:

`ascending region -> peak <- descending region`

The first region uses ordinary binary-search direction. The second reverses the comparison direction because values decrease as indexes increase.

## Range Search

Finding one occurrence of a value and finding its complete range are different tasks.

For:

`1 2 2 2 4 7`

the target `2` occupies indexes `1` through `3`.

`lower_bound(2)` finds the first position whose value is at least `2`.

`upper_bound(2)` finds the first position whose value is greater than `2`.

Therefore:

`first = lower_bound(target)`

`last = upper_bound(target) - 1`

This avoids scanning all matching elements and keeps the search logarithmic.

## Failure Conditions

The implementations distinguish several failure classes.

| Condition | Handling |
|---|---|
| Empty ordinary array | Target is reported absent |
| Empty bitonic array | Validation error where a peak is required |
| Missing target | Normal not-found result |
| Ragged matrix | Validation error |
| Duplicate ambiguity in rotated array | Boundary contraction |
| Invalid matrix coordinates | PostgreSQL constraint/trigger failure |
| Malformed structural assumption | Caller must validate the declared structure |

The most important limitation is that binary search cannot manufacture ordering that the input does not possess. The caller must provide a correct structural assumption.

## Performance Considerations

Binary search reduces the search interval approximately by half per iteration.

For a sorted array containing `n` elements:

`T(n) = O(log n)`

For a globally ordered matrix containing `m × n` elements:

`T(m,n) = O(log(mn))`

For a row-column sorted matrix:

`T(m,n) = O(m+n)`

For a bitonic array:

`O(log n)` peak discovery plus up to two `O(log n)` directional searches remains `O(log n)`.

For a rotated array containing duplicates, the worst case can degrade to:

`O(n)`

because repeated equal boundaries can prevent the algorithm from identifying which half is ordered.

Space usage is constant for the array and matrix search algorithms because they operate directly on the supplied data and do not create flattened copies.

## Security and Reliability Considerations

Binary-search code often appears simple, but boundary errors can create incorrect results or unsafe memory access in lower-level languages.

The implementations therefore use:

- explicit boundary checks
- overflow-safe midpoint formulas
- rectangular-matrix validation
- explicit handling of empty collections
- checked decrement operations for unsigned C++ indexes
- immutable Java result records
- exceptions for invalid structural assumptions
- PostgreSQL constraints and triggers for persisted structural data

For untrusted application input, validation should occur before an algorithm is selected. A caller should not declare arbitrary data to be bitonic or globally sorted merely to obtain a faster algorithm.

## Practical Workflow

A robust advanced-search workflow is:

`Input`
`  ↓`
`Validate structural assumptions`
`  ↓`
`Identify the monotonic invariant`
`  ↓`
`Select the matching search strategy`
`  ↓`
`Maintain left/right or row/column boundaries`
`  ↓`
`Discard only provably impossible regions`
`  ↓`
`Return found/not-found result`
`  ↓`
`Verify boundary and edge cases`

The same reasoning applies across all five source implementations even though the programming models differ.

## Engineering Trade-offs

| Decision | Benefit | Cost |
|---|---|---|
| Virtual matrix indexing | Avoids copying matrix data | Requires coordinate conversion |
| Duplicate-aware rotated search | Correctness with repeated values | Linear worst case |
| Separate bitonic searches | Simple directional invariants | Peak must be identified first |
| `Optional`/`OptionalInt` results | Distinguishes absence from valid index zero | Slightly more explicit calling code |
| PostgreSQL constraints | Invalid persisted data is rejected centrally | Schema becomes more restrictive |
| Comparison counters | Makes algorithm behavior observable | Adds small instrumentation overhead |

The implementations therefore emphasize the invariant behind each algorithm rather than treating binary search as a single reusable loop.
