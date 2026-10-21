# Binary Search Introduction

## Scope

This project studies binary search as an ordered-data algorithm rather than as a collection of language-specific syntax examples.

Binary search repeatedly compares a target with the middle element of a sorted search domain. If the middle value is smaller than the target, the lower half can be discarded. If it is larger, the upper half can be discarded. The remaining interval therefore shrinks geometrically.

The central invariant used by the implementations is a closed search interval:

`[left, right]`

For an iterative search, the interval is repeatedly reduced until either the target is found or `left > right`. The recursive version represents the same reasoning through function calls.

## Sorted-data requirement

Binary search is valid only when the ordering relation used by the search is consistent with the data.

For ascending integer data:

    [-20, -10, -1, 0, 4, 4, 4, 9, 15, 21, 42]

the comparison with the middle element provides useful information about which half can be eliminated.

For unsorted data:

    [1, 8, 3, 9]

a comparison with `8` cannot establish that every element to its left is smaller or every element to its right is larger. Discarding either half would therefore be unsafe.

The implementations validate this precondition rather than silently sorting the input. Silent sorting can hide a defect in a larger application and also changes the relationship between the original data and its returned indexes.

## Search boundaries

The iterative implementations use a closed interval:

    left = 0
    right = length - 1

    while left <= right:
        middle = left + (right - left) / 2

The expression `left + (right - left) / 2` avoids the unnecessary risk of calculating `left + right` directly when indexes can approach the maximum integer range.

After a failed comparison:

    target > values[middle]  -> left = middle + 1
    target < values[middle]  -> right = middle - 1

The middle element must be excluded from the next interval because it has already been compared with the target.

Empty arrays are handled by an initially invalid interval. Single-element arrays naturally reduce to one comparison.

## Iterative and recursive search

The iterative algorithm stores the current boundaries in local variables.

The recursive algorithm stores the same boundaries in the call stack:

    search(left, right)
        |
        +-- compare middle
              |
              +-- search(left, middle - 1)
              |
              +-- search(middle + 1, right)

Both perform `O(log n)` comparisons in the usual case.

The iterative form requires `O(1)` auxiliary space. The recursive form requires `O(log n)` call-stack space in the worst case.

For production systems, the iterative form is generally preferable when recursion provides no domain-specific benefit because it avoids unnecessary stack growth.

## Duplicate values and boundary searches

A standard binary search does not inherently specify which duplicate occurrence must be returned.

For:

    [10, 20, 30, 40, 40, 40, 70]

a normal search for `40` can return any matching position.

The implementations also demonstrate boundary-oriented searches:

- `lower_bound` returns the first position whose value is greater than or equal to the target.
- `upper_bound` returns the first position whose value is greater than the target.
- The interval `[lower_bound(target), upper_bound(target) - 1]` describes the complete matching range when the target exists.

This distinction is important because finding a matching value and finding the first matching value are different requirements.

## Python implementation

The Python program models binary search as reusable functions.

`validate_sorted` enforces the principal algorithmic precondition. `binary_search_iterative` uses an explicit closed interval, while `binary_search_recursive` carries the interval through recursive calls.

The `lower_bound` and `upper_bound` functions demonstrate how the same boundary mechanics support insertion positions and duplicate-range detection.

`BinarySearchError` separates invalid input from a normal unsuccessful search. A missing target is not an error, so the search functions return `None`.

The demonstration includes empty data, a single-element domain, duplicates, negative values, successful searches, unsuccessful searches, and unsorted input.

## JavaScript implementation

The JavaScript version uses a `SearchSession` object to model repeated searches against an immutable snapshot of sorted data.

`Object.freeze([...values])` prevents later mutation of the session's search domain. Each query records its target, result, success state, and timestamp. This provides an event-oriented perspective that is useful for an application performing multiple searches rather than a single console calculation.

The program also provides iterative and recursive searches and explicit lower and upper bounds.

Validation rejects non-arrays, non-finite numbers, and unsorted values. The asynchronous `runDemo` function provides an executable Node.js entry point while keeping the search algorithm itself synchronous because it is CPU-local and does not require I/O.

## C++ implementation

The C++ program uses a `SortedIndex` class to represent an immutable search domain.

The constructor validates the ordering invariant once. Subsequent searches can therefore rely on the established invariant rather than repeatedly checking the complete vector.

`std::optional<std::size_t>` represents the distinction between a valid index and no match without using a sentinel index that could be confused with a real result.

The recursive implementation has an explicit guard for `middle == 0` before calculating `middle - 1`. This prevents unsigned-index underflow.

The class also implements lower and upper bounds, making duplicate handling explicit. The main program treats malformed input as an exception and reports the validation failure without terminating the normal demonstration.

## Java implementation

The Java program models a repository-style artifact index through domain-oriented classes.

`SearchRequest` represents a validated search request. `SearchResult` records the target, optional result index, insertion point, success state, and search method.

The `BinarySearchService` contains the algorithmic behavior, while `RepositoryArtifactIndex` owns the validated immutable search data. `List.copyOf` prevents callers from modifying the stored search domain after construction.

Java 17 records provide compact immutable domain representations. The `SearchMethod` enum makes the algorithm selection explicit rather than passing arbitrary strings through the service.

The design also separates a failed search from a failed request. A missing target is represented by `OptionalInt.empty()`, while unsorted input causes an `IllegalArgumentException`.

## PostgreSQL implementation

The SQL script models ordered repository artifacts.

The `repository_artifacts` table contains an artifact key that serves as the ordered search value. The sample deliberately contains duplicate platform key `50` under distinct artifact names, demonstrating why search semantics must define how duplicates are handled.

The composite B-tree index on `(repository_name, artifact_key)` supports repository-scoped ordered retrieval and range operations.

The PostgreSQL functions `binary_search_recursive` and `binary_search_first` operate on ordered integer arrays. PostgreSQL arrays are one-based, so the functions use explicit array bounds rather than assuming zero-based indexing.

The script also demonstrates:

- CTE-based construction of an ordered search domain.
- First-match searching with duplicate values.
- Insertion-position-style retrieval.
- Aggregation of minimum, maximum, and distinct keys.
- Database constraints rejecting invalid artifact names.
- Transaction and savepoint behavior.
- `EXPLAIN` for inspecting an ordered query.
- A reporting view over the search domain.

Database-level constraints are important because application-level validation alone cannot protect data from every client or transaction.

## Relationship between algorithm and data structure

Binary search does not require a particular programming language or storage engine. It requires an ordered search domain and a way to access the middle element efficiently.

For an array or random-access list:

    sorted data
         |
    +----+----+
    |         |
    lower     upper
    half      half
    |         |
    discard one half
         |
       repeat

With random access, locating the middle element is `O(1)`, allowing the number of comparisons to fall to `O(log n)`.

If accessing the middle element itself requires linear traversal, the theoretical reduction in comparisons does not automatically produce the same practical performance. This is why binary search is especially natural for arrays and random-access structures.

## Failure modes

### Unsorted input

The algorithm's ordering assumptions are invalid. The implementations reject this condition instead of producing an unreliable result.

### Empty input

There is no candidate element. The search returns no match without performing a comparison.

### Missing target

A missing target is a normal search outcome, not an exceptional condition.

### Duplicate target

A normal binary search may return an arbitrary matching occurrence. Applications requiring the first, last, or complete range need explicit boundary semantics.

### Incorrect boundary updates

Using `left = middle` or `right = middle` in a closed-interval implementation can leave the same middle index in the search range indefinitely. Moving past the examined element is necessary for termination.

### Integer boundary errors

Calculating a midpoint as `(left + right) / 2` can overflow in environments with bounded integer indexes. The safer expression is `left + (right - left) / 2`.

### Recursive depth

Recursive binary search consumes stack frames. Its depth is logarithmic for a correctly shrinking interval, but iterative search avoids this additional resource requirement.

## Complexity

| Operation | Time | Extra space |
|---|---|---|
| Iterative binary search | `O(log n)` | `O(1)` |
| Recursive binary search | `O(log n)` | `O(log n)` stack |
| Lower bound | `O(log n)` | `O(1)` |
| Upper bound | `O(log n)` | `O(1)` |
| Sorting before search | `O(n log n)` | Depends on sorting method |

Binary search is most useful when the data is already sorted or when repeated searches justify the cost of maintaining sorted data.

## Practical design considerations

A search service should define whether its input may change during the operation. Concurrent mutation of a search domain can invalidate the sortedness invariant and produce incorrect results.

For persistent systems, indexes should be designed around actual query patterns. An ordered database index can often answer range and equality conditions directly, so manually reconstructing an application-level binary search may be unnecessary.

For in-memory structures, validation can be performed once when an immutable index is created rather than on every search. This reduces repeated work while preserving the invariant for subsequent operations.

The essential distinction remains:

    Sorted data
        ↓
    Known search boundaries
        ↓
    Middle-element comparison
        ↓
    Discard impossible half
        ↓
    Repeat until found or interval is empty

The algorithm is simple because the correctness of each discarded half follows from the sorted-data invariant.
