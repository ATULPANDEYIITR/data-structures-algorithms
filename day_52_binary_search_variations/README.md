# Binary Search Variations

This project studies binary search as a family of boundary-finding algorithms rather than as a single exact-match operation.

The central distinction is between searching for a value and searching for a **position where a value belongs**. Once that distinction is made explicit, first occurrence, last occurrence, lower bound, upper bound, insertion position, duplicate counting, and duplicate ranges become closely related operations.

The five source files model the same conceptual problem from different technical perspectives:

| Implementation | Primary perspective | Main mechanism |
|---|---|---|
| Python | Algorithm simulation and verification | Functions, lists, assertions, exceptions, `bisect` cross-checks |
| JavaScript | Event-oriented data processing | Functions, objects, runtime validation, tabular output |
| C++17 | Search engine case study | Encapsulation, `std::optional`, vectors, explicit invariants |
| Java 17 | Enterprise release indexing | Immutable domain state, collections, `OptionalInt`, validation services |
| PostgreSQL | Relational search workflow | Arrays, PL/pgSQL functions, transactions, constraints, views, indexes |

## Search Model

For a sorted sequence, a binary search repeatedly eliminates approximately half of the remaining search space.

The implementations use a half-open interval for boundary searches:

`[left, right)`

Here, `left` is included and `right` is excluded.

The lower-bound operation searches for the first position satisfying:

`value >= target`

The upper-bound operation searches for the first position satisfying:

`value > target`

These two predicates differ by exactly one equality condition. That small distinction is enough to support most duplicate-related binary-search problems.

### Boundary relationships

For a target that occurs in the sequence:

`first occurrence = lower bound`

`last occurrence = upper bound - 1`

`number of occurrences = upper bound - lower bound`

`insertion position = lower bound`

For a target that does not occur, the lower bound is still meaningful. It identifies the position at which the target can be inserted while preserving sorted order.

## First Occurrence

The first occurrence problem must continue searching after finding a matching value.

A conventional exact binary search can terminate immediately after finding the target. That is not sufficient when duplicates exist.

The lower-bound implementation instead treats equality as a reason to continue toward the left:

`value < target` moves right.

`value >= target` moves left by reducing the upper boundary.

When the search terminates, the lower boundary is the first valid position.

For example:

| Index | 0 | 1 | 2 | 3 | 4 | 5 |
|---|---:|---:|---:|---:|---:|---:|
| Value | 2 | 2 | 2 | 5 | 7 | 7 |

For target `2`, the first occurrence is index `0`, not an arbitrary matching index.

## Last Occurrence

The last occurrence is the symmetric boundary problem.

The search must continue toward the right after encountering an equal value.

The upper-bound operation searches for the first value strictly greater than the target. Therefore:

`last occurrence = upper bound - 1`

For target `7` in the example above, the upper bound points immediately after the final `7`.

This avoids scanning the duplicate region linearly.

## Lower Bound

Lower bound is the most reusable primitive in the implementations.

It returns the first index `i` satisfying:

`values[i] >= target`

This means it has three possible practical interpretations:

- The first occurrence of an existing target.
- The insertion position of a target.
- The boundary immediately before values greater than or equal to the target.

For:

`[1, 2, 2, 4, 5]`

the lower bound of `3` is index `3`, because `4` is the first value greater than or equal to `3`.

The target does not need to exist.

## Upper Bound

Upper bound returns the first index `i` satisfying:

`values[i] > target`

For the same sequence, the upper bound of `2` is index `3`.

This makes upper bound particularly useful for duplicate counting:

`count = upper_bound(target) - lower_bound(target)`

The interval `[lower_bound, upper_bound)` contains exactly the elements equal to the target.

## Insertion Position

Insertion position is not a separate search algorithm in these implementations.

It is derived from lower bound:

`insertion position = lower bound`

This is important because insertion must work for both present and absent values.

For:

`[10, 20, 30, 40]`

the insertion positions are:

| Target | Position |
|---:|---:|
| 5 | 0 |
| 10 | 0 |
| 25 | 2 |
| 40 | 3 |
| 50 | 4 |

The position is always within `[0, n]`.

## Duplicate Ranges

The duplicate range is represented by two boundaries:

`[first occurrence, last occurrence]`

Internally, the more useful representation is the half-open interval:

`[lower_bound, upper_bound)`

This representation makes counting simple and avoids special-case scanning.

For:

`[1, 2, 2, 2, 4, 4, 7]`

and target `2`:

- lower bound = `1`
- upper bound = `4`
- first occurrence = `1`
- last occurrence = `3`
- occurrence count = `3`

The algorithms therefore remain logarithmic even when the duplicate region is large.

## Python Implementation

The Python implementation uses small, composable functions.

`lower_bound()` and `upper_bound()` contain the core boundary logic. The other operations derive their results from those two primitives instead of implementing independent search loops.

`validate_sorted()` rejects input that violates the fundamental binary-search precondition.

The demonstration includes targets that are:

- smaller than every value,
- exactly present once,
- present multiple times,
- located between existing values,
- larger than every value.

The test suite cross-checks the custom implementation against Python's `bisect_left()` and `bisect_right()`.

This provides an independent standard-library reference for the boundary calculations.

The implementation also tests empty collections and invalid unsorted input.

### Python design

The important relationship is:

`lower_bound -> first occurrence / insertion position`

and:

`lower_bound + upper_bound -> last occurrence / duplicate count / duplicate range`

The code avoids linear duplicate scanning, so finding a range does not become `O(n)` merely because many equal values exist.

## JavaScript Implementation

The JavaScript implementation uses the same mathematical boundary definitions but presents them as a runtime-oriented data-processing model.

`evaluateTarget()` creates an object containing the complete search analysis for a target. The resulting objects are printed with `console.table()`, which makes comparison of boundary results convenient during debugging.

JavaScript-specific behavior includes:

- strict mode,
- object-based result construction,
- array processing,
- runtime exceptions,
- `console.table()` reporting,
- explicit validation before searching.

The implementation remains dependency-free and can run directly under Node.js.

The validation layer is important because JavaScript arrays do not inherently guarantee sorted order. A binary-search implementation that silently accepts unsorted input can return plausible but incorrect positions.

## C++17 Implementation

The C++ implementation models a sorted collection as a domain object named `SortedRepositoryIndex`.

The class owns a copied vector rather than exposing mutable internal storage. This prevents external code from changing the sequence after construction and invalidating the sorted invariant.

`std::optional<std::size_t>` is used for operations where an index may not exist.

This distinguishes:

- a valid index of `0`,
- an absent target.

That distinction is safer than using a special negative integer with an unsigned index type.

The class also provides duplicate counting and range reporting without exposing implementation details.

The scenario uses release identifiers, making insertion and duplicate lookup representative of operations that can occur in an indexed repository or deployment system.

### C++ boundary safety

The implementation calculates the midpoint as:

`left + (right - left) / 2`

rather than:

`(left + right) / 2`

The first form avoids overflow from adding two large indices before division.

The search itself remains `O(log n)`.

## Java 17 Implementation

The Java implementation models an enterprise release index using an immutable internal array.

The constructor copies the supplied array before storing it. This prevents callers from mutating the original array and breaking the sorted invariant after validation.

`OptionalInt` represents an index that may not exist.

The domain model separates:

- exact search,
- first occurrence,
- last occurrence,
- lower bound,
- upper bound,
- insertion position,
- occurrence count,
- duplicate range.

The program uses Java collections for target processing while keeping the core search implementation primitive and predictable.

The design demonstrates a useful enterprise principle: domain invariants should be established when an object is created rather than repeatedly assumed by every method.

An invalid release index is rejected immediately.

## PostgreSQL Implementation

The PostgreSQL script models sorted values as relational records rather than treating the database as only a place to store an array.

The main entities are:

| Table | Purpose |
|---|---|
| `search_collections` | Defines independent sorted datasets |
| `search_values` | Stores each value and its logical position |
| `search_queries` | Records search targets |
| `search_results` | Stores evaluated boundary results |

The `(collection_id, position)` primary key guarantees that a position is unique within a collection.

The `(collection_id, value, position)` index supports retrieval of values by collection and value while preserving positional information.

## PostgreSQL Boundary Functions

`lower_bound()` and `upper_bound()` implement the same boundary predicates as the application-language implementations.

PostgreSQL arrays are one-based, while the conceptual search positions in the project are zero-based. The functions therefore convert the final array position into a zero-based logical position.

`binary_search_report()` combines both boundaries to produce:

- lower bound,
- upper bound,
- first occurrence,
- last occurrence,
- occurrence count,
- insertion position.

The function rejects a null input array rather than silently treating missing data as an empty collection.

## PostgreSQL Workflow

The SQL workflow records queries separately from their results.

A query identifies:

`collection + target`

The evaluation function loads the sorted values, calculates the boundaries, and stores the result transactionally.

The reporting view combines collection, target, and result information into a query-oriented representation.

The script also performs integrity checks such as:

`occurrence_count = upper_bound - lower_bound`

and:

`last_occurrence = upper_bound - 1`

when a target exists.

These checks make the relationship between the derived values explicit.

## Algorithmic Complexity

For a sorted sequence containing `n` elements:

| Operation | Time | Extra space |
|---|---:|---:|
| Exact binary search | `O(log n)` | `O(1)` |
| First occurrence | `O(log n)` | `O(1)` |
| Last occurrence | `O(log n)` | `O(1)` |
| Lower bound | `O(log n)` | `O(1)` |
| Upper bound | `O(log n)` | `O(1)` |
| Insertion position | `O(log n)` | `O(1)` |
| Duplicate count | `O(log n)` | `O(1)` |
| Duplicate range | `O(log n)` | `O(1)` |

The important performance property is that duplicate size does not change the asymptotic search cost.

A target occurring one million times can still have its first and last positions determined with two logarithmic searches.

## Correctness Invariants

Binary-search boundary implementations are particularly sensitive to off-by-one errors.

The implementations rely on several invariants.

For lower bound:

`all positions before the returned position contain values < target`

and:

`the returned position, when inside the sequence, contains a value >= target`

For upper bound:

`all positions before the returned position contain values <= target`

and:

`the returned position, when inside the sequence, contains a value > target`

For an existing target:

`first occurrence <= last occurrence`

and:

`upper bound = last occurrence + 1`

For duplicate counting:

`count = upper bound - lower bound`

These relationships make useful test assertions because they validate the boundary model rather than only a collection of manually selected outputs.

## Edge Cases

Empty input has both bounds at position `0`.

A target smaller than every element has lower and upper bounds at the beginning.

A target larger than every element has both bounds at `n`.

A singleton sequence has only one possible matching index.

A sequence containing only duplicates tests whether equality moves the search toward the correct boundary.

A target between two distinct values tests insertion behavior without requiring the target to exist.

Unsorted input violates the fundamental precondition and is explicitly rejected by the application implementations.

## Common Failure Modes

### Returning immediately on equality

This solves exact search but does not solve first or last occurrence.

For first occurrence, equality must continue searching left.

For last occurrence, equality must continue searching right.

### Using the wrong equality condition

Lower bound uses:

`value < target`

Upper bound uses:

`value <= target`

Swapping those conditions changes the boundary and breaks duplicate counting.

### Returning `upper_bound - 1` without checking existence

If the target is absent, `upper_bound - 1` may refer to an unrelated element.

The implementation first verifies that the boundary actually identifies the target when calculating last occurrence.

### Mixing closed and half-open intervals

A search using `[left, right]` has different termination and update rules from `[left, right)`.

The implementations deliberately use one consistent interval model for each boundary function.

### Searching unsorted data

Binary search does not sort data. It relies on sorted order.

Running the algorithm on unsorted input can produce an apparently valid index that has no semantic meaning.

## Practical Interpretation

Binary search variations are best understood as **boundary queries**.

Exact search asks:

`Does the target exist?`

Lower bound asks:

`Where does the first value not smaller than the target begin?`

Upper bound asks:

`Where does the first value larger than the target begin?`

First occurrence and last occurrence are derived from those boundaries.

Insertion position is also a lower-bound query.

Duplicate counting is the width between the two boundaries.

This unified model reduces the number of independent algorithms that need to be implemented and tested while making the duplicate behavior explicit.

## Relationship Between the Implementations

The implementations intentionally do not represent the problem in identical ways.

Python emphasizes algorithm composition and independent verification.

JavaScript emphasizes structured result generation and runtime data processing.

C++ emphasizes ownership, invariants, optional results, and a reusable search object.

Java emphasizes immutable domain modeling and explicit enterprise validation.

PostgreSQL demonstrates how the same boundary concepts can be represented as persistent relational workflow data and database functions.

The mathematical contract remains consistent across all five implementations, while the engineering concerns differ according to the execution environment.
