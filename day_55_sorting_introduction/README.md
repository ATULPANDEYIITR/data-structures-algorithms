# Sorting Fundamentals

## Purpose

This project examines sorting as a data-ordering operation through three executable algorithms and a relational representation of sorting behavior. It distinguishes four important properties:

- **Stability:** whether records with equal sorting keys retain their original relative order.
- **In-place operation:** whether an algorithm rearranges its input using only a small amount of auxiliary storage.
- **Comparison sorting:** whether ordering decisions are made by comparing keys.
- **Time and space complexity:** how operation counts and memory requirements scale with input size.

The implementations use integer values and records with repeated keys so that correctness, stability, and resource trade-offs can be examined separately.

## Core Concepts

### Stable and unstable sorting

Consider records entered in this order:

| Name | Score | Original position |
|---|---:|---:|
| Asha | 90 | 1 |
| Ravi | 75 | 2 |
| Meera | 90 | 3 |
| Kabir | 75 | 4 |
| Isha | 90 | 5 |

Sorting by score produces ascending scores. A stable algorithm preserves the original relative order of records with equal scores.

A stable result is:

| Name | Score | Original position |
|---|---:|---:|
| Ravi | 75 | 2 |
| Kabir | 75 | 4 |
| Asha | 90 | 1 |
| Meera | 90 | 3 |
| Isha | 90 | 5 |

An unstable algorithm may place equal-score records in a different order while still producing correctly sorted scores.

Stability matters when records have multiple attributes. For example, sorting employee records by department and then performing a stable sort by salary preserves the earlier department ordering among employees with equal salaries. An explicit composite key can also express the intended final ordering directly.

### In-place sorting

An in-place algorithm rearranges elements in the supplied collection while requiring only a small amount of auxiliary storage, typically excluding the input itself.

Insertion sort and the three-way quicksort implementations modify their working arrays or vectors directly. Merge sort creates temporary storage for merging.

The term *in-place* does not mean that an implementation uses no memory. Recursive algorithms need stack space, and implementations may allocate small temporary objects or copies. The exact memory cost depends on the implementation, not just the algorithm's name.

The Java strategies intentionally copy their input before sorting. Their sorting operations use in-place techniques on the copy, but the public strategy interface preserves the caller's original list. This is a service-level design decision rather than a claim that the complete Java operation is memory-free.

### Comparison sorting

Comparison sorting determines order through comparisons between keys. Insertion sort, merge sort, and quicksort belong to this category.

For general comparison sorting, the worst-case number of comparisons required to sort arbitrary distinct elements has a lower bound of order \(n \log n\). Merge sort achieves this time bound in its standard implementation.

Counting sort is different. It uses the range of integer keys instead of relying exclusively on comparisons. Its running time can be expressed as \(O(n+k)\), where \(n\) is the number of records and \(k\) is the key range. It can be useful when the key range is small, but its memory cost may be impractical for very large ranges.

### Complexity notation

| Algorithm | Best case | Average case | Worst case | Auxiliary space | Stable by design |
|---|---|---|---|---|---|
| Insertion sort | \(O(n)\) | \(O(n^2)\) | \(O(n^2)\) | \(O(1)\) | Yes |
| Merge sort | \(O(n \log n)\) | \(O(n \log n)\) | \(O(n \log n)\) | \(O(n)\) | Yes |
| Quicksort | \(O(n \log n)\) | \(O(n \log n)\) | \(O(n^2)\) | \(O(\log n)\) average stack | No |
| Heap sort | \(O(n \log n)\) | \(O(n \log n)\) | \(O(n \log n)\) | \(O(1)\) | No |
| Counting sort | \(O(n+k)\) | \(O(n+k)\) | \(O(n+k)\) | \(O(n+k)\) | Yes, with a stable implementation |

These are conventional asymptotic bounds, not measured timings. Constant factors, memory allocation, cache behavior, input distribution, and implementation details affect real performance.

## Algorithm Mechanics

### Insertion sort

Insertion sort builds a sorted prefix. For each next element, it shifts larger elements one position to the right and inserts the element into the available position.

Important properties:

- It is stable when it shifts only strictly greater keys.
- It is in-place.
- It performs well on short or nearly sorted inputs.
- It requires quadratic time for reverse-ordered input in the general case.

The Python, JavaScript, C++17, and Java implementations count comparisons and writes to make the mechanics observable.

### Merge sort

Merge sort recursively divides an input into smaller parts, sorts the parts, and merges them into an ordered result.

During merging, the implementations select the left item when the two current keys are equal. This choice preserves the relative order of equal-key records.

Important properties:

- Worst-case running time is \(O(n \log n)\).
- Auxiliary storage is linear in the input size for the provided implementations.
- Stability is explicit in the merge operation.
- The extra memory cost can matter when sorting large datasets.

The implementations use merge sort as the predictable-time alternative to quicksort.

### Three-way quicksort

Three-way quicksort partitions a range into three regions:

- Keys smaller than the pivot.
- Keys equivalent to the pivot.
- Keys greater than the pivot.

The algorithm then processes the smaller outer partition recursively and continues iteratively with the larger partition. This reduces recursive stack growth, although it does not remove the quadratic worst-case time bound.

Three-way partitioning handles duplicate-heavy inputs efficiently. The algorithm is not stable because partition swaps can change the relative order of records with equal keys.

The selected middle element is a simple pivot policy, not a worst-case guarantee. A production implementation facing adversarial inputs may need a stronger pivot strategy, introspective sorting, or a trusted standard-library sort.

## Python Implementation

The Python script defines an immutable `SortResult` data class containing the algorithm name, sorted values, stability metadata, in-place metadata, comparison count, and write count.

Its three sorting functions have different contracts:

- `insertion_sort` modifies the provided list and returns its metrics.
- `merge_sort` accepts an iterable, creates a working list, and returns a separate sorted result.
- `quick_sort` modifies the provided list using three-way partitioning.

The `Student` data class provides records with duplicate scores. The `is_stable` helper checks whether equal-key records retain their original positions, using object identity to track records independently of their values.

The `main` function tests empty input, single-element input, duplicate values, negative values, and record sorting. Assertions compare results with Python's built-in sorting implementation and check stability where required.

The script uses only the Python standard library. Its deterministic random test data makes the verification repeatable.

## JavaScript Implementation

The JavaScript file provides equivalent algorithmic behavior through arrays, functions, and structured result objects.

`validateArray` checks the input collection and verifies that every derived sorting key is a finite number. This avoids undefined ordering behavior caused by `NaN`, missing numeric keys, or nonnumeric values.

The merge sort returns a new result array. Insertion sort and quicksort mutate their supplied arrays. Each function reports comparisons and writes.

The `sortBatch` function uses `Promise.all` to coordinate independent sorting jobs. The example operations are CPU-bound and do not become parallel merely because promises are used. For actual parallel CPU work in Node.js, worker threads or another suitable execution strategy would be required.

Assertions verify output ordering and stable behavior. Error handling at the entry point reports failed checks and sets a nonzero process exit code.

## C++17 Implementation

The C++ program uses templates so the sorting algorithms can operate on different record types and comparison functions.

`SortMetrics` records operation counts. `Record` models a named entity with a score and registration order. A comparator defines score ordering independently of the record's other fields.

The insertion sort shifts records through a vector, while merge sort uses a reusable buffer. Quicksort uses three-way partitioning and a generic recursive lambda to avoid requiring a separate class for each sorting strategy.

The merge implementation chooses the left record when the right record is not strictly less. This preserves stability for a valid strict weak ordering comparator.

Assertions check that all integer outputs agree and that the stable record result retains registration order for equal scores. The implementation uses standard-library vectors, algorithms, comparators, and assertions, without third-party dependencies.

## Java 17 Implementation

The Java implementation separates the algorithm interface from concrete sorting strategies.

The `SortingStrategy` interface defines a common contract. Records represent immutable metrics, employee data, and sorting results. The result constructor creates an immutable snapshot of the sorted values.

`InsertionSort`, `MergeSort`, and `QuickSort` each maintain operation counters for a single invocation. Merge sort uses temporary lists, while quicksort performs three-way partitioning on its working list.

The employee example demonstrates stable ordering by department rank. The comparator uses only the department rank, so employees with equal ranks remain in their input order when processed by a stable strategy.

The strategy objects contain per-invocation mutable counters and should not be shared concurrently between calls without synchronization or redesign. For concurrent enterprise services, invocation state can instead be held in local variables or a dedicated execution context.

## PostgreSQL Implementation

The SQL script creates a dedicated `sorting_lab` schema and models algorithm properties, input records, and recorded runs.

### Relational model

The principal relationships are:

    sorting_algorithms
          |
          | one algorithm per recorded run
          v
       sort_runs

       sort_items
          |
          +-- batch_name
          +-- sort_key
          +-- original_position
          +-- payload

`sorting_algorithms` stores algorithm classifications and complexity descriptions. `sort_runs` records input counts, verification outcomes, and optional elapsed times. `sort_items` stores sortable records, their keys, their original positions, and structured JSON payloads.

Primary keys, foreign keys, unique constraints, and check constraints protect record identity and basic data validity. The batch/key/position index supports deterministic ordering and batch-scoped key queries. The run-history index supports retrieving recent runs for a batch.

### Deterministic ordering and stability

SQL tables do not have an inherent row order. A query must specify `ORDER BY` to request an order.

The `sorted_batch` function orders by `sort_key` and then `original_position`. The second ordering key makes ties deterministic and preserves original order for records sharing the same key.

This is a query-level ordering policy. It does not mean PostgreSQL's physical sort implementation is guaranteed to be stable. An explicit unique tie-breaker establishes the required result order regardless of the internal sorting method.

The reporting view uses `row_number`, `rank`, and `dense_rank` to distinguish deterministic row positions from ranks that group equal values.

### Validation and reporting

`validate_batch_sorted` checks the requested ordering through a window function and rejects an empty batch name. The reporting queries compare algorithm properties, aggregate recorded runs, and retrieve records within a key range.

The script inserts example algorithm metadata, student records, integer values, and verified run records. Elapsed times remain nullable because no actual benchmark has been performed.

The transaction groups schema changes and sample data into one unit of work. The `DROP VIEW` and `DROP TABLE` statements make the script repeatable for the dedicated learning schema, but they also remove existing objects with those names. Run it only where replacing those objects is acceptable.

## Edge Cases and Correctness

The implementations cover several common sorting hazards:

- **Empty collections:** no element access occurs, and the result remains empty.
- **Single-element collections:** no rearrangement is needed.
- **Duplicate keys:** merge sort and insertion sort preserve relative order.
- **Negative values:** integer comparison works without special handling.
- **Duplicate-heavy inputs:** three-way partitioning groups equivalent keys.
- **Invalid JavaScript keys:** non-finite or nonnumeric keys are rejected.
- **Input preservation:** merge sort and the Java strategies retain the caller's input.
- **Ordering verification:** tests check nondecreasing keys rather than relying only on printed output.

A correct sorted sequence must satisfy two separate properties: its keys are in nondecreasing order, and it contains the same records as the original input. Stability adds a third property concerning the relative order of equivalent keys.

## Engineering Trade-offs

| Requirement | Suitable approach | Main trade-off |
|---|---|---|
| Small or nearly sorted collection | Insertion sort | Quadratic worst-case time |
| Predictable \(O(n \log n)\) behavior with stable ordering | Merge sort | Additional memory |
| Fast general-purpose partitioning | Quicksort | Quadratic worst case and no stability guarantee |
| Stable ordering of equal records | Stable algorithm or explicit tie-breaker | May require extra storage or additional key handling |
| Deterministic SQL output | Explicit `ORDER BY` with a unique tie-breaker | Requires choosing the intended tie policy |
| Adversarial production inputs | Introspective or otherwise bounded sorting strategy | More implementation complexity |

## Running the Files

The implementations require Python 3, Node.js, a C++17 compiler, Java 17, and PostgreSQL with permission to create objects in the target schema.

- Python: save the script as a `.py` file and run it with Python 3.
- JavaScript: save the file as a `.js` file and run it with Node.js.
- C++17: compile the source with a C++17-enabled compiler and execute the resulting program.
- Java 17: save the source as `SortingEnterpriseDemo.java`, compile it with `javac`, and run `SortingEnterpriseDemo`.
- PostgreSQL: execute the SQL file against a database where the executing role can create schemas, tables, functions, and views.

Each program performs correctness checks and prints representative results. The SQL file demonstrates ordering and reporting but does not benchmark PostgreSQL's internal sort implementation.

## Limitations

The operation counters measure selected algorithm-level comparisons and writes. They do not capture every machine instruction, allocation, cache miss, garbage-collection event, or database operation.

The reported complexity classifications describe conventional implementations and expected input assumptions. Actual execution time should be measured with representative datasets before selecting an algorithm for a performance-sensitive workload.

Stability metadata describes the algorithmic strategy. Stability is not inferred merely from a sorted result, since a particular run of an unstable algorithm may happen to preserve the order of equal-key records.
