# Bubble, Selection and Insertion Sort

## Scope

This project implements and analyzes three elementary comparison-based sorting algorithms:

- Bubble Sort
- Selection Sort
- Insertion Sort

The implementations use the same core problem while presenting different engineering perspectives. Python focuses on executable experimentation and instrumentation. JavaScript models sorting work as event-driven jobs. C++17 implements a compact sorting engine with explicit statistics and value preservation. Java 17 models sorting as an enterprise service with domain types, interfaces, immutable results, validation, and service boundaries. PostgreSQL models sorting experiments as relational data with constraints, triggers, views, reporting queries, and transactional state.

The algorithms are intentionally elementary. Their value is not raw performance on large datasets. They expose important relationships between input order, comparisons, writes, swaps, stability, memory usage, and algorithm selection.

## Conceptual Model

The three algorithms use different mechanisms to establish the same final ordering.

    Input sequence
          |
          +---------------- Bubble Sort
          |                    |
          |                    +-- compare adjacent elements
          |                    +-- exchange inverted pairs
          |                    +-- largest remaining value moves right
          |
          +---------------- Selection Sort
          |                    |
          |                    +-- search remaining suffix
          |                    +-- identify minimum
          |                    +-- place minimum at current position
          |
          +---------------- Insertion Sort
                               |
                               +-- maintain sorted prefix
                               +-- select next value
                               +-- shift larger values
                               +-- insert selected value
          |
          v
    Sorted sequence

The implementations preserve the caller's original sequence by sorting a copy. This is useful for experiments because the same dataset can be submitted to all three algorithms without accidental mutation from an earlier run.

## Bubble Sort

Bubble Sort examines adjacent elements and exchanges them when they appear in the wrong order.

For an ascending sort, an inversion such as `7, 3` becomes `3, 7`. After one complete pass, the largest value that remains unsorted reaches the end of the active region.

The implementations use an early-termination condition. If an entire pass performs no exchange, the input is already sorted and further passes are unnecessary.

### Properties

| Property | Bubble Sort |
|---|---|
| Best case | O(n) with early termination |
| Average case | O(n²) |
| Worst case | O(n²) |
| Auxiliary algorithmic space | O(1) |
| Stable in these implementations | Yes |
| Adaptive to sorted input | Yes |
| Main operation | Adjacent comparison and exchange |

Bubble Sort can be useful for teaching inversion movement and for very small datasets. Its quadratic behavior makes it unsuitable as a general-purpose choice for large unsorted collections.

## Selection Sort

Selection Sort divides the sequence into a sorted prefix and an unsorted suffix.

At each position, the algorithm scans the remaining suffix, identifies the minimum value, and exchanges it with the value at the current position.

The number of comparisons is largely independent of input ordering. A sorted input still requires scanning the remaining suffix to establish that its first element is already the minimum.

### Properties

| Property | Selection Sort |
|---|---|
| Best case | O(n²) |
| Average case | O(n²) |
| Worst case | O(n²) |
| Auxiliary algorithmic space | O(1) |
| Stable in the implemented form | No general guarantee |
| Adaptive to sorted input | No |
| Main operation | Minimum search followed by exchange |

A useful practical characteristic is the relatively small number of exchanges. When writes or swaps are more expensive than comparisons, this trade-off can matter even though the asymptotic running time remains quadratic.

## Insertion Sort

Insertion Sort maintains a sorted prefix. It takes the next element and moves larger prefix elements one position to the right until the correct insertion position is found.

For example, starting with `5, 2, 4, 1, 3`, the first insertion changes the sorted prefix from `5` to `2, 5`. The next value, `4`, is inserted between them, producing `2, 4, 5`.

### Properties

| Property | Insertion Sort |
|---|---|
| Best case | O(n) |
| Average case | O(n²) |
| Worst case | O(n²) |
| Auxiliary algorithmic space | O(1) |
| Stable in these implementations | Yes |
| Adaptive to nearly sorted input | Yes |
| Main operation | Shift and insertion |

Insertion Sort is often the strongest of these three choices for small or nearly sorted collections. The number of shifts is related to the number of inversions in the input.

## Relationship Between Input Order and Cost

Input arrangement is important.

    Already sorted
    1 2 3 4 5 6
          |
          +-- Bubble: early exit
          +-- Insertion: minimal movement
          +-- Selection: still scans suffixes

    Reverse sorted
    6 5 4 3 2 1
          |
          +-- Bubble: many exchanges
          +-- Insertion: many shifts
          +-- Selection: many comparisons, relatively fewer exchanges

    Nearly sorted
    1 2 4 3 5 6
          |
          +-- Bubble: limited exchanges before early exit
          +-- Insertion: very small number of shifts
          +-- Selection: still performs quadratic comparisons

This is why asymptotic complexity alone does not describe every practical difference. Input structure determines the amount of work performed by adaptive algorithms.

## Stability

A stable sorting algorithm preserves the relative order of records that compare as equal.

For example, consider records represented as:

`(priority=2, id=A)` and `(priority=2, id=B)`

If A occurs before B before sorting, a stable sort keeps A before B after sorting by priority.

Bubble Sort and Insertion Sort are implemented with comparisons that avoid exchanging equal values, so their basic forms are stable.

Selection Sort can move an element across another equal element during a minimum exchange. The basic implementation therefore does not guarantee stability.

Stability matters when sorting records by multiple criteria in separate stages.

## Python Implementation

The Python program provides a reusable sorting interface through `SortResult` and `SortStats`.

Important mechanisms include:

- `dataclass` objects for structured statistics and results.
- `Enum` values for explicit algorithm selection.
- Input validation through `SortError`.
- Dictionary-based algorithm dispatch.
- Correctness tests for empty, singleton, sorted, reverse-sorted, duplicate-heavy, and negative-value inputs.
- Operation counters for comparisons, swaps, and writes.
- Timing using the standard-library performance counter.
- Deterministic dataset construction.
- Input-preservation checks.

The statistics deliberately distinguish comparisons, swaps, and writes. A swap generally produces two element writes, while Insertion Sort performs repeated shifts and therefore has a different write profile.

## JavaScript Implementation

The JavaScript program uses Node.js standard-library functionality without npm dependencies.

It differs from the Python implementation by introducing an event-driven sorting job queue.

The `SortJobQueue` stores jobs containing:

- Dataset name
- Algorithm
- Input values

The queue processes jobs asynchronously and yields with `setImmediate()` between jobs. This models how a Node.js service can schedule independent units of computational work while retaining event-loop responsiveness between jobs.

JavaScript-specific mechanisms include:

- `Map` for algorithm dispatch.
- Multiset validation through `Map` counters.
- Classes for validation and job processing.
- Promises and `async`/`await`.
- Node.js `performance.now()` for timing.
- Deterministic pseudo-random dataset creation.
- Explicit process exit status for fatal failures.

The implementation accepts only finite numeric values. This prevents ambiguous comparisons involving strings, `NaN`, or unsupported values.

## C++17 Implementation

The C++ program treats sorting as a small reusable engine.

`SortingEngine` contains separate implementations while `SortResult` combines sorted values with operation statistics. `SortException` provides explicit failure reporting.

The implementation uses:

- `std::vector`
- `std::algorithm`
- `std::swap`
- `std::is_sorted`
- `std::mt19937`
- `std::unordered_map`
- `std::chrono`
- Exception handling
- Strongly typed `enum class`

The input is copied before sorting. A separate permutation check sorts independent copies of the original and result to verify that no value was lost or introduced.

This verification is important because checking only sortedness is insufficient. An incorrect algorithm could produce a sorted sequence with missing or duplicated values and still pass a simple `is_sorted` test.

## Java 17 Implementation

The Java implementation uses explicit domain modeling.

The main domain types are:

| Type | Responsibility |
|---|---|
| `Algorithm` | Identifies the supported sorting algorithms |
| `SortStats` | Immutable performance measurements |
| `SortResult` | Immutable sorted output and statistics |
| `Sorter` | Sorting service interface |
| `SortingService` | Validates input and dispatches algorithms |
| `SortingException` | Represents domain validation failures |
| `GovernanceStyleReport` | Separates result presentation from sorting |

Java records provide immutable result objects. `EnumMap` provides efficient algorithm dispatch using the enum keys.

The service copies incoming lists before modifying them. Null elements are rejected explicitly.

The implementation demonstrates an enterprise-oriented separation between:

    Input
      |
      v
    Validation
      |
      v
    SortingService
      |
      +--> Bubble Sort
      +--> Selection Sort
      +--> Insertion Sort
      |
      v
    Immutable SortResult
      |
      v
    Reporting

This separation prevents reporting concerns from becoming embedded in algorithm logic.

## PostgreSQL Model

The PostgreSQL implementation treats sorting experiments as persistent operational data rather than merely as in-memory calculations.

The central relationship is:

    sorting_dataset
          |
          v
    sorting_run
          |
          v
    sorting_observation

A dataset contains the original numeric sequence. A sorting run records the selected algorithm, execution state, operation counts, output, timing, and failure information.

### Database Entities

| Table | Purpose |
|---|---|
| `sorting_dataset` | Stores named input sequences and dataset categories |
| `sorting_run` | Stores algorithm executions and their state |
| `sorting_observation` | Stores measured operation values |

The `sort_algorithm`, `dataset_kind`, and `run_status` enum types constrain important domain values at the database level.

## Database Validation

The schema uses several layers of validation.

`sorting_dataset` requires:

- A non-empty dataset name.
- A JSON array.
- Numeric array elements.

`sorting_run` requires:

- Non-negative operation counts.
- Output for completed runs.
- Timing for completed runs.
- Failure reasons for failed runs.

A trigger validates state transitions and rejects invalid transitions such as changing a completed run back into another state.

A second trigger verifies that completed output is sorted and has the same number of elements as the input.

This is important because application code should not be the only place where core data invariants are protected.

## PostgreSQL Workflow

The database represents execution state explicitly:

    pending
       |
       v
    running
       |
       +----------> failed
       |
       v
    completed

A completed run cannot be converted back into another state. A failed run cannot directly transition to `running` through the demonstrated update path.

The transaction example demonstrates how multiple state changes can be grouped and rolled back as one unit.

## Reporting Queries

The SQL script provides several reporting perspectives:

- Completed sorted outputs.
- Average comparisons by algorithm.
- Average swaps.
- Average writes.
- Average execution time.
- Best comparison count per dataset.
- Sortedness validation.
- Run-state counts.

The window-function query ranks algorithms within each dataset according to comparison count.

This separates the data model from the algorithm implementation. PostgreSQL is not being used to implement the three sorting algorithms themselves; it is being used to persist, validate, analyze, and report on sorting experiments.

## Complexity Comparison

| Algorithm | Best | Average | Worst | Extra Space | Stable | Adaptive |
|---|---|---|---|---|---|---|
| Bubble Sort | O(n) | O(n²) | O(n²) | O(1) | Yes | Yes |
| Selection Sort | O(n²) | O(n²) | O(n²) | O(1) | No general guarantee | No |
| Insertion Sort | O(n) | O(n²) | O(n²) | O(1) | Yes | Yes |

The O(n) best case for Bubble Sort depends on the implemented early-exit optimization. Without that optimization, the algorithm would still perform quadratic comparisons on already sorted input.

## Practical Limitations

These algorithms become poor choices as the dataset grows because quadratic work increases rapidly.

For example, if an algorithm performs approximately n² comparisons, increasing the input size from 1,000 to 10,000 can increase the dominant comparison work by roughly a factor of 100.

Their main practical limitations are:

- Poor scalability for large unsorted datasets.
- High comparison counts in quadratic cases.
- Significant data movement for Bubble and Insertion Sort on difficult input.
- Lack of the advanced partitioning, merging, or heap-based structures used by more scalable algorithms.
- Dependence on input order for practical performance.

Their educational and practical value remains clear for:

- Small collections.
- Nearly sorted collections.
- Demonstrating stability.
- Demonstrating adaptive behavior.
- Understanding inversions.
- Learning operation-level cost.
- Testing sorting invariants.
- Comparing algorithmic trade-offs.

## Edge Cases

The implementations explicitly cover:

- Empty input.
- Single-element input.
- Already sorted input.
- Reverse-sorted input.
- Duplicate values.
- Negative values.
- Nearly sorted input.
- Invalid values.
- Null values in Java.
- Non-numeric values in JavaScript.
- Preservation of the input sequence.
- Preservation of the input multiset.
- Invalid database execution states.
- Failed sorting runs.
- Completed-run output validation.

## Security and Reliability Considerations

Sorting itself has limited security exposure, but production implementations still need defensive boundaries.

The programs avoid executing input as code and do not construct shell commands from dataset values.

Input validation prevents unsupported values from entering comparison logic.

The PostgreSQL schema uses constraints and triggers to prevent invalid persisted states. Foreign keys ensure that runs cannot reference nonexistent datasets.

The database uses `ON DELETE CASCADE` for dependent experimental records. This is appropriate for an experiment model where a run has no independent meaning after its dataset is deleted.

For production workloads, untrusted input should also be bounded by maximum collection size. A quadratic algorithm can become a resource-exhaustion risk when an attacker controls the number of elements.

## Performance Measurement

The timing values in these programs are observational rather than formal benchmarks.

Small sorting workloads are sensitive to:

- CPU scheduling.
- Runtime startup cost.
- Garbage collection.
- Compiler optimization.
- Operating-system load.
- Runtime implementation.
- Dataset construction.
- Measurement resolution.

Operation counts are often more useful than a single elapsed-time measurement for understanding algorithm behavior. The programs therefore record comparisons and data movement as well as elapsed time.

## Design Distinctions

The project deliberately keeps four concerns separate:

    Sorting algorithm
          |
          v
    How elements are reordered

    Instrumentation
          |
          v
    How computational work is measured

    Validation
          |
          v
    How correctness and input constraints are enforced

    Persistence and reporting
          |
          v
    How experiments are stored and analyzed

Bubble Sort, Selection Sort, and Insertion Sort are not interchangeable mechanisms even though they produce the same sorted result.

Bubble Sort repeatedly resolves adjacent inversions.

Selection Sort repeatedly identifies a minimum from the remaining suffix.

Insertion Sort grows a sorted prefix by inserting the next element.

These distinctions explain their different behavior on sorted, reverse-sorted, duplicate-heavy, and nearly sorted data.

## Files

| File | Technical focus |
|---|---|
| Python | Instrumented implementations, validation, datasets, correctness tests |
| JavaScript | Event-driven sorting jobs, asynchronous processing, Maps, validation |
| C++17 | Explicit sorting engine, STL algorithms, deterministic benchmarking, exception handling |
| Java 17 | Enterprise-style service layer, records, interfaces, immutable results, domain validation |
| PostgreSQL | Persistent experiment model, constraints, triggers, views, reporting, transactions |
| README.md | Technical model, algorithm analysis, implementation relationships, limitations |

## Execution Characteristics

The source programs use only standard functionality for their respective environments.

Python requires a Python 3 runtime.

JavaScript requires a Node.js runtime.

C++ requires a compiler supporting C++17.

Java requires Java 17 or later.

PostgreSQL requires a PostgreSQL server supporting JSONB, enum types, PL/pgSQL functions, triggers, views, common table expressions, and window functions.

The implementations intentionally avoid third-party dependencies so that algorithm behavior remains visible and reproducible.
