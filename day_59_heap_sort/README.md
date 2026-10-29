# Heap Sort: Heap-Based Sorting and Algorithm Comparison

## Scope

This project implements heap sort from multiple engineering perspectives and compares it with merge sort and quicksort.

The central algorithm is heap sort. Its key property is a worst-case time complexity of `O(n log n)` while requiring `O(1)` auxiliary storage when implemented in place. The implementation uses an array representation of a binary heap rather than allocating explicit tree nodes.

The three comparison algorithms have different engineering characteristics:

| Algorithm | Best | Average | Worst | Auxiliary Space | Stable |
|---|---:|---:|---:|---:|---|
| Heap Sort | `O(n log n)` | `O(n log n)` | `O(n log n)` | `O(1)` | No |
| Merge Sort | `O(n log n)` | `O(n log n)` | `O(n log n)` | `O(n)` | Yes |
| Quick Sort | `O(n log n)` | `O(n log n)` | `O(n²)` | `O(log n)` average recursion | No |

The practical choice depends on the required guarantees, memory constraints, stability requirements, and expected data distribution.

## Core Heap Model

A binary heap is represented directly in an array.

For an element at zero-based index `i`:

- Parent: `(i - 1) // 2`
- Left child: `2i + 1`
- Right child: `2i + 2`

A max-heap maintains the invariant that every parent is greater than or equal to its children.

A min-heap maintains the opposite ordering.

For ascending heap sort, the max-heap form is particularly convenient:

`unsorted array → max-heap → move maximum to end → repair heap → repeat`

The sorted suffix grows from right to left while the active heap becomes smaller.

## Heap Construction

The implementations use bottom-up heap construction.

Only internal nodes can have children, so heapification begins at the last internal node and proceeds toward the root.

For `n` elements, the heap construction phase is `O(n)`, not `O(n log n)`. The subsequent extraction phase performs up to `n - 1` heap repairs, each costing `O(log n)`.

Therefore:

`O(n) + O(n log n) = O(n log n)`

The heap remains inside the original array, which gives heap sort its constant auxiliary-space property.

## Heap Sort Mechanics

The Python implementation provides a reusable `HeapSorter` class with:

- max-heap sorting
- min-heap sorting
- input validation
- comparison counting
- swap counting
- execution timing
- randomized tests
- edge-case tests
- comparison with merge sort and quicksort
- a separate priority-queue demonstration using `heapq`

The implementation validates integer input and rejects excessively large configured inputs before processing.

The JavaScript implementation uses an immutable-input boundary. The sorter copies the caller's array and performs the heap operations on the copy. This prevents an unexpected mutation of application state.

It also uses JavaScript's `EventEmitter` to process sorting jobs through an event-driven queue. This separates the sorting algorithm from application-level job processing.

The C++17 implementation uses `std::vector<long long>` and a dedicated `HeapSortEngine`. Instrumentation is kept inside the engine, making the operation counters independent of the calling code.

The Java 17 implementation introduces an enterprise-oriented service boundary. `SortPolicy`, `SortResult`, `SortingStrategy`, and `RepositorySortService` make validation, policy selection, algorithm execution, and returned metrics explicit.

## Python Implementation

The Python program models heap sort as a class-based algorithm.

Important mechanisms include:

- `dataclass` for immutable sort metrics
- `Enum` for max-heap and min-heap modes
- explicit sift-down operations
- in-place swapping
- randomized correctness testing
- reference merge sort
- reference quicksort
- priority-queue behavior using the standard library
- assertions for correctness
- validation of element types and input size

The comparison functions count every heap comparison. The swap function counts every exchange. These counters make the algorithm's internal behavior observable without changing its asymptotic complexity.

The script tests empty input, singleton input, duplicates, negative numbers, large integer boundaries, already ordered patterns, and randomized arrays.

## JavaScript Implementation

The JavaScript program is designed for Node.js.

`HeapSorter` validates safe JavaScript integers because JavaScript's `Number` type cannot represent every integer exactly beyond `Number.MAX_SAFE_INTEGER`.

The sorter returns a structured result containing:

- sorted values
- comparison count
- swap count
- elapsed time

The `SortJobQueue` class provides an event-driven application layer. Jobs generate `queued`, `completed`, and `failed` events. The queue uses asynchronous processing without introducing an external package.

This creates a useful distinction between:

`sorting algorithm → job service → application events`

The sorting mechanism does not depend on the event system, so either component can be tested independently.

## C++17 Implementation

The C++ implementation treats heap sort as a reusable algorithm engine.

The `HeapType` enumeration controls whether the engine constructs a max-heap or min-heap.

`SortMetrics` records operation counts and elapsed time.

The program uses:

- `std::vector`
- `std::algorithm`
- `std::chrono`
- `std::random`
- `std::numeric_limits`
- exception handling

The C++ version deliberately uses `long long` values so the test cases can exercise signed integer boundaries without the floating-point precision concerns associated with JavaScript numbers.

A separate merge-sort implementation uses a reusable buffer. This exposes the additional memory required by merge sort.

The quicksort implementation uses a middle element as its partition pivot and performs in-place partitioning.

## Java 17 Implementation

The Java implementation represents sorting as an enterprise service.

`SortPolicy` defines execution constraints:

- heap type
- desired ordering
- maximum permitted input size

`SortResult` is an immutable record containing the result and operational metrics.

`SortingStrategy` defines an algorithm boundary. `HeapSortStrategy` provides the concrete heap implementation.

`RepositorySortService` validates domain-specific numeric metrics before invoking the sorting strategy.

This separation demonstrates an important production design principle: algorithm selection and domain validation should not be entangled unnecessarily.

Java streams are used for validation and metric reporting, while mutable `ArrayList` storage is used internally during the in-place heap operations.

The service rejects null values, negative repository metrics, and inputs exceeding the configured size limit.

## PostgreSQL Relational Model

The PostgreSQL implementation treats sorting as an observable processing workflow.

The `sorting_runs` table records:

- algorithm
- heap type
- input size
- execution state
- comparison count
- swap count
- timestamps

The `sort_values` table stores individual input values with their positions.

The `heap_snapshots` and `heap_snapshot_values` tables provide a relational representation of selected heap states.

The relationships are:

`sorting_runs`
`    ├── sort_values`
`    └── heap_snapshots`
`             └── heap_snapshot_values`

Foreign keys provide referential integrity and cascading deletion prevents orphaned measurements.

## Database Validation

The database uses constraints for structural validation.

Examples include:

- non-negative input sizes
- non-negative operation counters
- valid algorithm names
- valid heap types
- valid run states
- unique positions within a run
- valid snapshot stages

A trigger prevents a run from being marked `completed` without a completion timestamp.

The `complete_sorting_run` function centralizes the transition to the completed state and validates operation counts.

This demonstrates why application validation and database validation serve different purposes. Application code can provide user-facing validation, while database constraints protect the persisted state against invalid writes from any client.

## SQL Analysis Queries

The script contains queries for several operational questions.

### Stored Input

The first retrieval query reconstructs the values associated with a particular sorting run in their stored position order.

### Algorithm Aggregation

The aggregation query compares the number of runs, average input size, average comparisons, and average swaps by algorithm.

### Duplicate Analysis

Heap sort does not require distinct values. The duplicate-value query identifies repeated values so that equal-element behavior can be inspected.

### Workload Classification

A CTE calculates total recorded operations and classifies workloads into small, moderate, and large groups.

### Sorted-Order Validation

A window function uses `LAG` to compare each value with its predecessor. The result determines whether the stored sequence is monotonically ascending.

### Workflow Reporting

The database distinguishes completed, failed, and running executions rather than representing all records as successful sorting operations.

## Edge Cases

The implementations explicitly cover:

| Edge Case | Expected Behavior |
|---|---|
| Empty array | Return immediately |
| One element | No heap operations required |
| Two elements | One possible extraction |
| Duplicate values | Preserve values, but not necessarily relative order |
| Negative values | Sort normally |
| Already sorted data | Still performs heap construction |
| Reverse-sorted data | Still guarantees `O(n log n)` |
| Extreme integer values | Handled according to the language's integer representation |
| Invalid element | Reject before sorting |
| Excessive input | Reject according to configured limits |

Heap sort is not stable. If two records have equal sort keys, their original relative order is not guaranteed to remain unchanged.

This matters when sorting records rather than primitive values.

## Heap Sort Versus Merge Sort

Merge sort and heap sort both provide deterministic `O(n log n)` worst-case time.

Their principal difference is memory behavior.

Merge sort normally requires an auxiliary buffer proportional to the input size. Its merge operation has predictable sequential memory access and it can be implemented as a stable sort.

Heap sort can operate directly inside the input array. Its `O(1)` auxiliary-space requirement is useful when memory is constrained.

The trade-off is that heap operations perform non-sequential jumps through the array, which can produce less favorable cache behavior than merge operations.

## Heap Sort Versus Quick Sort

Quicksort often performs very well in practice because partitioning has favorable locality and does not require a full auxiliary array.

Its classic implementation can degrade to `O(n²)` in the worst case.

Modern quicksort implementations can reduce this risk through randomized pivots, median-based strategies, three-way partitioning, or introspective sorting.

Heap sort provides a simpler worst-case guarantee:

`worst-case time = O(n log n)`

This makes it useful when deterministic upper bounds are more important than typical-case performance.

## Complexity Comparison

| Operation | Heap Sort | Merge Sort | Quick Sort |
|---|---:|---:|---:|
| Build structure | `O(n)` | `O(1)` setup | `O(1)` setup |
| Sorting | `O(n log n)` | `O(n log n)` | `O(n log n)` average |
| Worst case | `O(n log n)` | `O(n log n)` | `O(n²)` classic |
| Auxiliary storage | `O(1)` | `O(n)` | `O(log n)` average recursion |
| Stable | No | Yes | No |
| In-place | Yes | Usually no | Yes, in common implementations |

The comparison should not be reduced to asymptotic complexity alone. Memory access patterns, object movement, recursion depth, stability, input distribution, and implementation quality affect real workloads.

## Correctness Invariants

During max-heap construction:

`parent >= children`

During extraction:

`sorted suffix contains the largest extracted values`

At every point, the active heap occupies indices `[0, heap_size)`.

The sorted suffix occupies indices `[heap_size, n)`.

The key invariant is:

`all elements in the active heap <= every element already placed in the sorted suffix`

After the final extraction, the active heap contains one element and the complete array is sorted.

## Performance Considerations

Heap construction should use bottom-up heapification rather than inserting every element into a heap individually.

Repeated insertion would require `O(n log n)` construction, while bottom-up construction requires `O(n)`.

The extraction phase dominates the complete algorithm at `O(n log n)`.

Instrumentation adds constant work to each comparison and swap, so benchmark results from the instrumented versions should not be treated as production-performance measurements.

The source programs include timing only to make relative behavior observable.

## Security and Robustness

The sorting algorithms do not require network access, filesystem access, shell execution, or external services.

Input limits are included to reduce accidental resource exhaustion in application-facing examples.

JavaScript validates safe integers because silently accepting values beyond exact integer precision can produce incorrect ordering.

The Java and C++ versions reject invalid domain data before performing the main operation.

The PostgreSQL model uses constraints, foreign keys, and trigger-based state validation to prevent invalid persisted workflow states.

Database transactions demonstrate how an invalid state transition can be rejected without partially committing the operation.

## Practical Selection

Heap sort is a strong choice when:

- worst-case `O(n log n)` time is required
- auxiliary memory should remain constant
- stability is not required
- deterministic behavior is desirable

Merge sort is preferable when:

- stability is required
- predictable sequential processing is useful
- additional memory is acceptable

Quicksort is attractive when:

- average-case performance is the primary concern
- in-place processing is desired
- a robust partition strategy is available
- worst-case behavior is controlled by the implementation

The appropriate algorithm is therefore determined by workload constraints rather than by a single universal ranking.

## File Responsibilities

| File | Technical Role |
|---|---|
| Python | Class-based heap sorter, metrics, validation, tests, and algorithm comparison |
| JavaScript | Safe-integer validation, immutable input boundary, event-driven sort jobs, and comparisons |
| C++17 | Low-level heap engine with STL containers, integer-boundary tests, metrics, and reference algorithms |
| Java 17 | Enterprise service model using records, strategy interfaces, policies, validation, and immutable results |
| PostgreSQL | Relational execution model, constraints, triggers, functions, transactions, snapshots, and analytical queries |
| README.md | Technical explanation of heap mechanics, algorithm trade-offs, implementations, complexity, and database workflow |

## Execution Model

The five implementations share the same conceptual progression:

`Input`
`  ↓`
`Validation`
`  ↓`
`Heap Construction`
`  ↓`
`Repeated Root Extraction`
`  ↓`
`Heap Repair`
`  ↓`
`Sorted Output`
`  ↓`
`Metrics / Validation`

The surrounding engineering differs by language.

Python emphasizes direct algorithm experimentation and testing.

JavaScript emphasizes event-driven application integration.

C++17 emphasizes explicit memory and container behavior.

Java 17 emphasizes domain modeling, policy objects, and service boundaries.

PostgreSQL emphasizes durable state, integrity constraints, workflow state, and analytical reporting.
