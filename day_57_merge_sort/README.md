# Merge Sort

## Scope

This project studies merge sort as a divide-and-conquer sorting algorithm and implements the algorithm from several engineering perspectives.

The central relationship is:

Input sequence
→ divide into smaller ranges
→ recursively or iteratively sort each range
→ merge ordered ranges
→ produce one ordered sequence

The implementations focus on four core properties:

| Property | Merge Sort Behavior |
|---|---|
| Design | Divide and conquer |
| Worst-case time | O(n log n) |
| Auxiliary space | O(n) for the array implementations |
| Stability | Yes when equal elements select the left run first |

The five source files use the same algorithmic foundation but deliberately emphasize different engineering techniques.

## Core Algorithm

Merge sort divides a sequence until each sub-sequence contains at most one element. A sequence of zero or one element is already sorted.

For a non-trivial range, the algorithm performs:

1. Calculate the midpoint.
2. Sort the left half.
3. Sort the right half.
4. Merge the two sorted halves.
5. Copy the merged result back into the working sequence.

The merge operation is the central mechanism. Two independently sorted ranges can be combined in linear time by maintaining one cursor for each range and repeatedly selecting the smaller next value.

For a range containing n elements, the recurrence is:

T(n) = 2T(n/2) + O(n)

This produces O(n log n) time.

The recursion depth is O(log n). The auxiliary merge buffer requires O(n) storage.

## Divide-and-Conquer Structure

The algorithm does not compare every element with every other element. Instead, it creates progressively smaller independent sorting problems.

A sequence containing eight elements can be represented conceptually as:

[8 elements]
├── [4 elements]
│   ├── [2 elements]
│   │   ├── [1]
│   │   └── [1]
│   └── [2 elements]
│       ├── [1]
│       └── [1]
└── [4 elements]
    ├── [2 elements]
    │   ├── [1]
    │   └── [1]
    └── [2 elements]
        ├── [1]
        └── [1]

The merge phase then reconstructs the sequence in the opposite direction:

individual values
→ sorted pairs
→ sorted groups
→ complete sorted sequence

## Stability

A sorting algorithm is stable when elements having equal sort keys retain their original relative order.

Consider:

| Original Position | Record | Key |
|---:|---|---:|
| 0 | Asha | 85 |
| 1 | Ravi | 70 |
| 2 | Maya | 85 |
| 3 | Karan | 70 |
| 4 | Neha | 85 |

Sorting by score must produce:

| Sorted Position | Record | Key |
|---:|---|---:|
| 0 | Ravi | 70 |
| 1 | Karan | 70 |
| 2 | Asha | 85 |
| 3 | Maya | 85 |
| 4 | Neha | 85 |

The equal-key records preserve their original order.

The implementations achieve this by selecting the element from the left sorted range when two keys are equal. This decision is small but essential to stability.

Stability is useful when records have multiple ordering criteria. A stable secondary sort can preserve an earlier ordering established by another sort.

## Python Implementation

The Python source provides a reusable `MergeSort` class with:

- Generic sequence handling.
- A key function for object-based sorting.
- Ascending and descending modes.
- A dataclass containing sorting metrics.
- Input validation.
- Explicit failure handling.
- Stability tests.
- Randomized self-tests.
- Large-input validation.
- Comparison and merge counters.
- Performance timing.

The implementation uses recursive top-down merge sort.

A single auxiliary list is allocated for a sorting operation and reused by every merge. This avoids allocating a new list for each recursive merge and keeps the additional memory requirement at O(n).

The implementation also contains an optimization that checks whether the largest value in the left half is already less than or equal to the smallest value in the right half. If the two halves are already ordered relative to one another, the merge is skipped.

## JavaScript Implementation

The JavaScript implementation uses bottom-up merge sort instead of recursive top-down sorting.

The algorithm begins with sorted runs of width one, then combines:

1 → 2 → 4 → 8 → 16 → ...

This removes recursive call depth from the implementation while retaining O(n log n) time.

The implementation also introduces an event-driven service layer.

The event flow is:

sort:start
→ sorting operation
→ sort:complete

If validation or processing fails:

sort:start
→ sorting operation
→ sort:error

A `SortEventBus` uses a `Map` of event names and `Set` collections of listeners. This prevents duplicate listener registrations and provides a simple event-driven integration boundary.

The JavaScript implementation also supports asynchronous service calls through promises. The actual sort is synchronous because it is CPU-bound, but the service boundary allows the sorting operation to participate cleanly in a larger asynchronous application.

Object sorting is demonstrated with records containing identifiers, names, and scores.

## C++17 Implementation

The C++ implementation treats merge sort as a reusable generic engine.

Templates allow the same engine to operate on:

- Integers.
- User-defined domain objects.
- Custom comparison policies.

The `MergeSortEngine` accepts a comparator rather than hard-coding ascending integer comparison.

The domain example uses deployment changes with:

| Field | Purpose |
|---|---|
| id | Unique change identifier |
| component | System component |
| priority | Ordering key |

This demonstrates that merge sort can operate on domain objects when a meaningful ordering relation is supplied.

The implementation uses move operations when transferring elements between the working vector and auxiliary buffer. This avoids unnecessary copying for types where moving is cheaper than copying.

The program measures:

- Number of comparisons.
- Number of merge operations.
- Elapsed execution time.

It also validates the final ordering with the standard library's sortedness predicate.

## Java 17 Implementation

The Java implementation models sorting as an enterprise-style service.

The domain contains deployment changes with:

- A change identifier.
- A service name.
- A risk score.
- An explicit status.

Validation occurs in the record constructor, preventing invalid domain objects from entering the workflow.

A separate `GovernancePolicy` decides whether a deployment change is eligible for automatic processing. The merge-sort service then orders eligible changes by risk.

This separates two concerns:

GovernancePolicy
→ decides which records are eligible

MergeSortService
→ orders eligible records

The sorting service accepts a `Comparator` and a merge observer. The observer provides an integration point for instrumentation without coupling the sorting algorithm to a logging implementation.

Java records provide immutable domain representations, while collections and comparators express the sorting policy explicitly.

## PostgreSQL Implementation

The PostgreSQL source represents merge-sort experimentation as a relational workflow.

The principal relationships are:

datasets
→ dataset_items
→ sort_runs
→ sorted_items

Additional merge information is stored in:

sort_runs
→ merge_operations

The schema distinguishes input data from execution results. This makes it possible to compare an original sequence with the resulting sorted sequence and verify properties such as ordering and stability.

### Main Tables

| Table | Purpose |
|---|---|
| `datasets` | Identifies logical input datasets |
| `dataset_items` | Stores values and original positions |
| `sort_runs` | Records sorting executions and metrics |
| `sorted_items` | Stores the resulting ordered sequence |
| `merge_operations` | Records representative merge ranges |

Foreign keys maintain relationships between datasets, runs, and items.

Check constraints restrict invalid states such as negative positions, invalid sort directions, and unsupported run statuses.

## Database Validation

The schema uses triggers for rules that depend on multiple columns or related records.

A sort run can be:

- `RUNNING`
- `COMPLETED`
- `FAILED`

A running operation cannot have a completion timestamp. A completed or failed operation must have one.

The `sorted_items` trigger verifies that a sorted item belongs to the dataset associated with the sort run and that the recorded value matches the original item.

This keeps important integrity rules inside the database rather than relying exclusively on application code.

## SQL Stability Verification

The PostgreSQL script records both:

- `original_position`
- `sorted_position`

That makes stability testable.

For equal values, the query compares original positions in sorted order. A stability violation occurs if a later original position appears before an earlier original position among equal keys.

This is stronger than merely checking that the final values are numerically sorted.

A sequence can be numerically sorted while still violating stability.

## Edge Cases

The implementations explicitly handle:

| Case | Expected Behavior |
|---|---|
| Empty sequence | Return immediately |
| One element | Already sorted |
| Duplicate values | Preserve stable ordering |
| Negative values | Sort normally |
| Already sorted input | Avoid unnecessary merges where supported |
| Reverse-sorted input | Sort correctly |
| Object records | Use a supplied key or comparator |
| Invalid input | Raise or report a validation error |

Empty and singleton inputs are important because they form the base cases of divide-and-conquer recursion.

Duplicate values are important because they expose stability behavior.

Already sorted input is useful for testing optimizations that avoid unnecessary merge work.

## Complexity

For n elements, merge sort divides the input into approximately equal halves at each level.

There are approximately log2(n) levels.

At each level, all n elements participate in merging.

Therefore:

| Measurement | Complexity |
|---|---:|
| Best-case time | O(n log n) in the general implementation |
| Average-case time | O(n log n) |
| Worst-case time | O(n log n) |
| Auxiliary array space | O(n) |
| Recursive stack | O(log n) |
| Stable ordering | Yes |

The JavaScript bottom-up version avoids recursive stack growth. The Python, C++, and Java implementations use recursive top-down decomposition.

## Performance Considerations

The dominant operation is the merge phase.

For each merge, elements are examined through two sorted cursors. Once one half is exhausted, the remaining elements of the other half can be copied directly.

The implementations reuse an auxiliary buffer instead of allocating a separate buffer for every recursive call.

This reduces allocation overhead and makes memory behavior more predictable.

The Python implementation measures comparisons and merges directly. The C++ implementation measures execution time with a monotonic clock. The Java implementation exposes comparison, merge, and nanosecond timing metrics. The JavaScript implementation reports comparison and merge counts through its result object and completion event.

## Failure Handling

The source files validate important boundaries instead of silently accepting invalid configuration.

Examples include:

- Null or non-array inputs.
- Invalid key functions.
- Invalid domain identifiers.
- Invalid risk scores.
- Invalid database states.
- Incorrect sort-run completion timestamps.
- Sorted records that do not belong to the associated dataset.

Failure handling is deliberately separated from the core merge operation so that the algorithm remains focused on ordering while callers receive explicit validation failures.

## Security and Reliability Considerations

Merge sort itself is not an authentication or authorization mechanism. Security concerns arise around how sorting is embedded in applications.

The implementations therefore avoid evaluating arbitrary expressions as sorting policies.

The Python implementation accepts callable key functions supplied directly by the application. The Java implementation uses typed comparators. The C++ implementation uses compile-time or explicitly supplied comparator functions. The JavaScript implementation receives functions directly rather than executing strings as code.

The PostgreSQL model uses constraints, foreign keys, and triggers to prevent inconsistent workflow records.

For untrusted large inputs, application-level resource limits are still necessary. Merge sort has predictable O(n log n) comparison behavior, but O(n) auxiliary memory can become significant for very large datasets.

## Practical Distinctions

Merge sort should not be confused with related concepts.

**Divide and conquer** describes the strategy of decomposing a problem into smaller subproblems and combining their solutions.

**Recursion** is one implementation technique for expressing the divide-and-conquer structure. Merge sort can also be implemented iteratively, as demonstrated by the JavaScript version.

**Merging** is the operation that combines two already-sorted ranges into one sorted range.

**Stability** describes the preservation of relative order among equal-key records.

**Complexity analysis** describes how execution time and memory requirements grow as the input size increases.

These concepts interact, but they are not interchangeable.

## File Responsibilities

| File | Engineering Perspective |
|---|---|
| Python | Recursive generic merge-sort library with validation, metrics, stability, and tests |
| JavaScript | Iterative merge sort with asynchronous service boundaries and event-driven reporting |
| C++17 | Generic merge-sort engine using templates, move semantics, comparators, and domain objects |
| Java 17 | Enterprise-oriented sorting service with records, policies, comparators, validation, and observers |
| PostgreSQL | Relational model for datasets, sorting runs, merge operations, results, and integrity validation |

## Design Decisions

A shared auxiliary buffer is preferred over repeatedly allocating temporary arrays during each merge.

Equality is resolved in favor of the left sorted range. This provides stable behavior.

Comparators and key functions are injected rather than hard-coded where the language makes that practical. This allows the same algorithm to sort different domain representations.

The implementations do not modify caller-owned input unnecessarily. Python explicitly copies the input sequence, JavaScript creates a working copy, and Java returns immutable result views where appropriate.

The PostgreSQL model records original positions because stability cannot be verified from values alone when duplicate keys exist.

## Limitations

Merge sort requires additional memory for array-based merging. In-place merge algorithms can reduce auxiliary memory, but they are substantially more complicated and may introduce unfavorable constants or implementation trade-offs.

The implementations focus on in-memory sorting. They do not implement external merge sort for datasets larger than available memory.

The PostgreSQL model represents and validates sorting results rather than replacing a database query planner's native ordering mechanisms.

For database-scale workloads, SQL `ORDER BY` should normally be preferred to manually reproducing an application-level merge-sort workflow. The schema here exists to model the algorithmic concepts and make execution properties observable.

## Learning Outcomes

The completed artifacts provide practical coverage of:

- Divide-and-conquer decomposition.
- Recursive sorting.
- Iterative bottom-up sorting.
- Merge operations.
- Stable ordering.
- Comparator and key-based sorting.
- Auxiliary-buffer management.
- Base cases and recursive termination.
- Input validation.
- Domain-specific ordering.
- Performance measurement.
- Complexity analysis.
- Database integrity enforcement.
- Edge-case testing.
- Failure-state modeling.

The five implementations present the same fundamental algorithm through different engineering abstractions while preserving the defining properties of merge sort.
