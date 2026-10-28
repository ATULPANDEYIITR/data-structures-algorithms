# Quick Sort: Partitioning, Pivot Selection, and Worst-Case Behavior

## Scope

This project studies Quick Sort as an in-place comparison-sorting algorithm through five independent implementations.

The central distinction is between:

- **Partitioning**: rearranging a subarray around a pivot according to a partition invariant.
- **Pivot selection**: deciding which value should guide the partition.
- **Randomized Quick Sort**: selecting pivots using randomness to reduce dependence on predictable input order.
- **Worst-case behavior**: understanding how repeatedly unbalanced partitions can produce quadratic running time.

The implementations deliberately use different engineering approaches rather than translating one program line by line.

## Core Model

For a subarray containing `n` elements, Quick Sort performs three conceptual operations:

1. Select a pivot.
2. Partition the subarray.
3. Recursively or iteratively sort the resulting partitions.

A balanced partition has approximate sizes:

`n/2 + n/2`

A highly unbalanced partition may have:

`0 + (n - 1)`

The recurrence for balanced partitions is approximately:

`T(n) = 2T(n/2) + O(n)`

which gives `O(n log n)` time.

A repeated one-sided partition gives:

`T(n) = T(n - 1) + O(n)`

which gives `O(n²)` time.

The algorithm is therefore strongly affected by partition quality.

## Partitioning Strategies

### Lomuto Partition

The Lomuto implementation maintains a growing region containing values less than or equal to the pivot.

A typical invariant is:

`low ... store-1` contains values `<= pivot`

The pivot is moved to the end before scanning. Elements satisfying the partition condition are exchanged toward the beginning, and the pivot is finally placed at its resulting position.

Advantages:

- Simple invariant.
- Easy to implement and inspect.
- Straightforward pivot-position return value.

Trade-offs:

- It can perform many swaps.
- Duplicate-heavy inputs can produce inefficient partitions.
- Its behavior can be sensitive to pivot selection.

### Hoare Partition

The Hoare implementation uses two scanning positions.

The left scan moves until it encounters a value that should be on the right side. The right scan moves until it encounters a value that should be on the left side. Those elements are exchanged.

The returned index represents a partition boundary, not necessarily the final position of the pivot.

Advantages:

- Usually performs fewer swaps than a basic Lomuto implementation.
- Works naturally with two-sided partitioning.
- Handles duplicate values efficiently when the partition invariant is implemented correctly.

Trade-offs:

- The boundary semantics are different from Lomuto.
- Recursive ranges must use the returned boundary carefully.
- Incorrect loop conditions can cause nontermination or invalid indexing.

## Pivot Selection

The source implementations support several policies.

| Strategy | Selection rule | Main characteristic |
|---|---|---|
| First | First element | Vulnerable to ordered inputs |
| Last | Last element | Vulnerable to ordered inputs |
| Middle | Middle position | Often useful for simple structured inputs |
| Median of three | Median of first, middle, last | Reduces some common bad partitions |
| Random | Random element | Reduces predictable adversarial patterns |

### First and Last Element

Using the first element as the pivot on already sorted data produces highly unbalanced partitions:

`0 + (n - 1)`

The same problem occurs with a last-element pivot on sorted or reverse-sorted inputs.

This is a direct example of why Quick Sort does not have an unconditional `O(n log n)` worst-case bound.

### Middle Element

Choosing the middle position is inexpensive and often improves behavior on ordered data, but it does not guarantee balanced partitions for arbitrary input distributions.

### Median of Three

Median-of-three compares the first, middle, and last values and selects their median.

For example:

`[2, 100, 5]`

has median value `5`.

This policy avoids some obvious extremes without requiring randomness. It is still a heuristic rather than a worst-case guarantee.

### Randomized Pivot

Randomized Quick Sort chooses a pivot independently of predictable input order.

The random policy does not eliminate the theoretical `O(n²)` worst case. It makes consistently bad partitions much less predictable and gives expected `O(n log n)` behavior under the standard randomized analysis.

The Python, JavaScript, C++17, and Java 17 implementations use explicit seeds where reproducibility matters.

## Python Implementation

The Python program provides a reusable `QuickSorter` class with:

- `PivotStrategy` and `PartitionStrategy` enumerations.
- `SortStats` for measuring comparisons, swaps, partitions, and recursion depth.
- Lomuto and Hoare partition implementations.
- First, last, middle, median-of-three, and random pivot policies.
- Input copying so the caller's iterable is not modified.
- Assertions validating sorted output.
- Benchmark cases for random, sorted, reverse-sorted, and duplicate-heavy data.
- Deterministic random behavior through a seeded generator.

The implementation also processes the smaller partition recursively and continues iteratively through the larger partition. This reduces recursion-stack risk while preserving the Quick Sort partitioning model.

The Python program uses only the standard library.

## JavaScript Implementation

The JavaScript program treats Quick Sort as a Node.js application rather than a direct Python translation.

Its notable design choices are:

- JavaScript `Map`/`Set` are not necessary for the numerical core, so the implementation does not introduce artificial data structures.
- Objects and enumerated policy values represent configuration.
- A deterministic linear congruential generator supplies reproducible randomized pivots.
- An explicit range stack avoids dependence on the JavaScript call stack.
- `Promise`-based batch processing demonstrates how independent sorting workloads can be scheduled without adding an external dependency.
- `Number.isSafeInteger` prevents silent loss of integer precision for values outside JavaScript's safe integer range.
- `performance.now()` measures execution time.

The explicit stack is particularly important in JavaScript because a naïve recursive implementation can hit the runtime call-stack limit on sufficiently unbalanced input.

## C++17 Implementation

The C++17 program treats Quick Sort as a technical case study in explicit memory and policy control.

It uses:

- `enum class` for pivot and partition policies.
- STL `vector` for contiguous numerical storage.
- `std::mt19937` for deterministic pseudo-random pivot selection.
- `std::uniform_int_distribution` for unbiased pivot-index selection within a range.
- An explicit `vector`-based work stack.
- `std::is_sorted` to validate the final ordering.
- Exception handling around the application entry point.
- `std::uint64_t` for operation counters.

The implementation avoids relying on recursive calls for the main sorting workflow. This makes the memory behavior easier to control for adversarial inputs.

The Hoare implementation uses signed indices internally because the scan begins logically outside the array bounds. The actual array access occurs only after the scan has advanced to a valid position.

## Java 17 Implementation

The Java implementation models Quick Sort through explicit domain-oriented types.

Its main structures are:

- `enum` values for pivot and partition policies.
- `record SortStats` for immutable result reporting.
- `record Range` for subarray boundaries.
- `SortStatsBuilder` for controlled mutation while collecting metrics.
- `QuickSortService` for sorting behavior and policy execution.
- `SortRequest` for associating a workload with a sorting service.

Java's `ArrayDeque` is used as an explicit work stack.

The implementation uses a `switch` expression for pivot-policy selection and a seeded `Random` instance for randomized pivots.

The service validates null input, preserves explicit range boundaries, tracks stack depth, and verifies output against `Arrays.sort` in the executable test scenarios.

## PostgreSQL Model

The PostgreSQL implementation treats sorting as an experimental workflow rather than attempting to reproduce the in-memory sorting algorithm with SQL.

The relational model contains:

`sorting_jobs`
→ describes the selected pivot and partition policies and workflow state.

`input_values`
→ stores ordered input positions and values.

`algorithm_runs`
→ stores measured comparisons, swaps, partitions, stack depth, elapsed time, and correctness.

`sorted_values`
→ provides a relational representation for validating sorted output when results are recorded.

The workflow states are:

`created → running → completed`

or:

`created → running → failed`

Constraints prevent negative operation metrics and invalid failure records.

## Database-Level Integrity

The database uses:

- Primary keys for entity identity.
- Foreign keys for job-to-input and job-to-run relationships.
- `ON DELETE CASCADE` where dependent experimental records should disappear with their job.
- Unique job names for experiment identification.
- Check constraints for non-negative positions and metrics.
- Enumerated types for controlled strategy and workflow values.
- A trigger that prevents a run from being marked correct before its associated job is completed.
- Functions for starting and completing jobs.
- A transactional example covering job state, run insertion, correctness, and completion.

This makes the database more than a collection of unrelated sorting records. It represents an auditable experiment lifecycle.

## SQL Analysis

The SQL script includes queries for:

- Input-size and value-distribution statistics.
- Failed or unverified runs.
- Aggregated comparisons and swaps by policy.
- Normalized comparisons per input item.
- Ordered-output validation using `LAG`.
- Workflow-state reporting.
- Query-plan inspection through `EXPLAIN`.
- Identification of runs exhibiting quadratic-style normalized work.

The index on `(job_id, value)` supports queries that retrieve values for a particular sorting job while ordering or filtering by value.

The index on `(job_id, recorded_at DESC)` supports recent-run reporting for a job.

Indexes are deliberately limited to relationships that support actual analytical queries.

## Complexity

| Case | Time | Explanation |
|---|---:|---|
| Best/typical balanced behavior | `O(n log n)` | Partitions remain reasonably balanced |
| Expected randomized behavior | `O(n log n)` | Random pivoting avoids predictable partition patterns |
| Worst case | `O(n²)` | Repeated `0 + (n - 1)` partitions |
| Partition operation | `O(n)` | Each element in the active range may be inspected |
| Auxiliary stack | `O(log n)` typical | Balanced partitions |
| Auxiliary stack | `O(n)` naïve worst case | Repeatedly unbalanced partitions |

The implementations reduce practical stack growth through explicit work stacks or smaller-partition-first processing, but this does not change the mathematical worst-case comparison complexity.

## Duplicate Values

Duplicate values are an important edge case.

A partition implementation that repeatedly sends equal values to one side can produce poor balance even when the input contains very little numerical variation.

The Hoare implementation used here scans toward values on the opposite side of the pivot and can exchange equal values across the partition boundary. This gives it useful behavior on duplicate-heavy inputs.

For applications with extremely large numbers of duplicate values, a three-way partitioning scheme can be preferable because it explicitly separates:

`less than pivot | equal to pivot | greater than pivot`

The current implementations intentionally focus on Lomuto and Hoare because their partition invariants make the fundamental partitioning differences clear.

## Stability

Quick Sort is generally **not stable**.

If two records have equal sort keys, their relative order is not guaranteed to remain unchanged.

For primitive integer arrays this is usually irrelevant. For records such as:

`(priority, timestamp, identifier)`

stability may become a business requirement.

The implementations in this project do not promise stability.

## In-Place Behavior

The numerical implementations modify the working array directly.

They do not construct a second array containing the complete sorted result.

This gives Quick Sort a useful memory advantage over algorithms that require linear auxiliary storage, though partitioning still requires some control structure for pending ranges.

The Python implementation begins by copying the input iterable into a list. That copy is intentional because Python callers may supply arbitrary iterables and the sorter needs indexed mutable storage.

## Worst-Case Scenario

Consider:

`[1, 2, 3, 4, 5, 6, 7]`

With a first-element pivot, the first partition can produce:

`[] + [2, 3, 4, 5, 6, 7]`

The next partition produces:

`[] + [3, 4, 5, 6, 7]`

This continues until the array contains one element.

The work becomes approximately:

`n + (n - 1) + (n - 2) + ... + 1`

which is:

`O(n²)`

This is the central failure mode that pivot selection attempts to reduce.

## Security and Robustness Considerations

Quick Sort can be affected by deliberately constructed input.

If an application uses a deterministic weak pivot policy and accepts attacker-controlled ordering, an attacker may be able to construct input that causes excessive comparison work.

Relevant controls include:

- Randomized pivot selection.
- Median-of-three heuristics.
- Explicit stack management.
- Input-size limits for untrusted workloads.
- Execution time limits at the application layer.
- Operation counters for monitoring.
- Avoiding predictable deterministic pivots for hostile input.
- Validation of numerical ranges in languages with fixed numeric representations.

Randomization reduces predictability but does not mathematically remove the quadratic worst case.

## Engineering Trade-Offs

| Decision | Benefit | Cost |
|---|---|---|
| Hoare partition | Efficient two-sided partitioning | Boundary semantics are more complex |
| Lomuto partition | Simple invariant | Can perform more swaps |
| Median-of-three | Cheap pivot heuristic | No worst-case guarantee |
| Random pivot | Reduces predictable adversarial patterns | Requires random-state management |
| Explicit stack | Avoids recursive call-stack limits | Requires range-stack bookkeeping |
| Operation counters | Makes behavior measurable | Adds small constant overhead |
| Database experiment model | Reproducible analytical workflow | Does not execute the in-memory sort itself |

## Conceptual Workflow

    Input
      |
      v
    Validate
      |
      v
    Select pivot policy
      |
      v
    Select pivot
      |
      v
    Partition
      |
      +-------------------+
      |                   |
      v                   v
    Left range         Right range
      |                   |
      +---------+---------+
                |
                v
          Repeat until
          ranges have
          size <= 1
                |
                v
              Sorted

Pivot selection influences partition balance.

Partition balance influences the number of recursive or pending ranges.

Partition balance therefore strongly influences practical Quick Sort performance.

## File Responsibilities

| File | Primary responsibility |
|---|---|
| Python | Configurable Quick Sort simulator with measurements and benchmarks |
| JavaScript | Event-driven Node.js implementation with explicit stack and safe-integer validation |
| C++17 | Policy-driven in-memory sorting engine with STL and explicit memory control |
| Java 17 | Enterprise-style sorting service with immutable result records and explicit policies |
| PostgreSQL | Relational experiment model, workflow state, integrity enforcement, and analytical reporting |

## Practical Interpretation

Quick Sort should not be understood simply as a recursive sorting function.

Its behavior emerges from the interaction of:

- The partition invariant.
- Pivot selection.
- Input distribution.
- Duplicate frequency.
- Range-management strategy.
- Stack behavior.
- Randomization policy.
- Validation and operational constraints.

A good implementation therefore needs both a correct partition algorithm and a deliberate strategy for controlling pathological input.

The most important distinction is that `O(n log n)` describes balanced or expected behavior, while `O(n²)` remains the theoretical worst case. Pivot selection heuristics and randomized selection improve practical behavior but do not change that fundamental distinction.
