# Non-Comparison Sorting

## Technical Scope

Non-comparison sorting algorithms organize values without relying exclusively on comparisons between individual elements. They use information about the values themselves, such as integer digits, frequency counts, or distribution across a numeric interval.

This repository implements three non-comparison sorting algorithms:

- **Counting sort** records how frequently each value occurs.
- **Radix sort** orders values through successive digit or byte passes.
- **Bucket sort** distributes values into intervals and sorts each interval independently.

A comparison-based sorting implementation is also included as a reference. It provides a correctness baseline and helps evaluate when a non-comparison algorithm is likely to offer a practical advantage.

The three algorithms are related through their ability to exploit properties of the input. Their assumptions, memory requirements, and performance characteristics are different.

## 1. Counting Sort

Counting sort is designed for discrete integer values drawn from a bounded range.

Let:

- `n` represent the number of input elements.
- `min` represent the smallest input value.
- `max` represent the largest input value.
- `k = max - min + 1` represent the number of possible values in the interval.

The algorithm allocates a frequency array of length `k`. Each input value increments the frequency at its offset from the minimum.

The output is reconstructed by visiting frequency entries in ascending order and emitting each value according to its recorded count.

### Negative integer support

A frequency array cannot use negative positions. The implementations therefore calculate an offset:

`offset = value - minimum`

For an input containing `[-4, -1, 0, 3]`, the offsets are `[0, 3, 4, 7]`. The array positions remain non-negative while the original values are preserved.

### Complexity

| Property | Complexity |
|---|---|
| Time | `O(n + k)` |
| Auxiliary space | `O(n + k)` |
| Stable reconstruction | Yes, when the implementation uses cumulative positions and reverse traversal |
| Input requirement | Discrete integers |
| Main constraint | A reasonably small value range |

The Python and C++ implementations reconstruct output from frequencies. Their value-only output does not need to retain record identity.

The Java and PostgreSQL implementations use the same frequency principle. PostgreSQL stores frequencies in a bounded `BIGINT[]` array.

### When counting sort is suitable

Counting sort is useful for:

- Small integer status-code ranges.
- Bounded categorical identifiers represented as integers.
- Examination scores within a known scale.
- Small-range event classifications.
- Large datasets with relatively few distinct possible values.

Its performance advantage comes from avoiding a comparison operation for every ordering decision.

### When counting sort is unsuitable

A small number of values can still produce a very large range. For example, an input containing `-1` and `10^12` would require an impractically large frequency array.

Memory use depends on `k`, not just on `n`. The implementations therefore enforce configurable maximum ranges before allocating frequency storage.

Counting sort should not be selected solely because the dataset contains integers. The range must also be considered.

## 2. Radix Sort

Radix sort processes values one digit or group of digits at a time.

The implementations use the Least Significant Digit (LSD) approach. Each pass performs a stable distribution according to the current digit. Stability ensures that the ordering established by earlier passes is retained.

For decimal integer representation, the first pass processes the least significant decimal digit, the next pass processes the following digit, and so on.

The final result is ordered after all relevant digit positions have been processed.

### Stable digit passes

A stable pass preserves the relative order of elements having the same current digit.

A common implementation uses:

1. A frequency array for the current digit.
2. Prefix totals to determine output positions.
3. Reverse traversal of the input.
4. An output array for the reordered values.

Reverse traversal is important when the prefix array represents final positions. It preserves the order of values sharing a digit.

### Signed integer handling

Negative values require additional care because ordinary non-negative digit processing does not directly establish signed numeric order.

The Python implementation subtracts the minimum input value from every integer. The resulting keys are non-negative and retain the original numeric ordering.

The C++ and Java implementations use a signed-order transformation:

`unsigned_key = value XOR sign_bit`

Flipping the sign bit maps signed integer ordering to unsigned key ordering. Their fixed-width implementations then process eight byte positions for 64-bit integers.

The PostgreSQL implementation uses numeric offsets and base-10 digit extraction. This avoids overflow when calculating the difference between the minimum and maximum `BIGINT` values.

### Complexity

| Property | Complexity |
|---|---|
| Time | `O(d(n + b))` |
| Auxiliary space | `O(n + b)` |
| `d` | Number of digit or byte passes |
| `b` | Digit base or radix |
| Stability | Yes, when each digit pass is stable |

For base 256, each pass processes one byte. A fixed-width 64-bit implementation requires eight passes.

For arbitrary-precision integers, the number of passes depends on the number of bytes required by the largest shifted key.

### When radix sort is suitable

Radix sort is suitable for:

- Large integer identifiers.
- Wide signed integer ranges.
- Fixed-width numeric keys.
- Large datasets where digit processing is cheaper than repeated comparisons.
- Workloads with predictable integer representations.

It is especially useful when counting sort would allocate an excessive frequency array.

### When radix sort is unsuitable

Radix sort requires a representation that can be divided into ordered digit groups. Arbitrary strings, complex objects, and floating-point values need additional encoding rules.

Its performance depends on the number of passes, the base, memory movement, and cache behavior. A large radix reduces pass count but increases per-pass frequency-array size.

The implementation must also preserve signed ordering. Simply extracting digits from a negative integer without a signed-order transformation can produce an incorrect result.

## 3. Bucket Sort

Bucket sort distributes values into a set of intervals. Each interval is represented by a separate bucket.

The general process is:

1. Find the minimum and maximum input values.
2. Select a bucket count.
3. Map each value to a bucket.
4. Sort each bucket independently.
5. Concatenate buckets in interval order.

For a value `x`, the normalized position is:

`normalized = (x - minimum) / (maximum - minimum)`

The bucket index is calculated as:

`index = floor(normalized * bucket_count)`

The maximum value must be assigned to the final bucket because its normalized position is exactly `1`.

The implementations clamp bucket positions to prevent an out-of-range index.

### Distribution and local sorting

Bucket sort is most effective when values are distributed reasonably evenly across the selected interval.

The Python and C++ implementations sort individual buckets using insertion sort. Insertion sort has low overhead for small collections and performs well when each bucket contains relatively few elements.

The Java implementation uses a comparison sort within each bucket. The PostgreSQL version stores variable-length bucket contents in JSONB arrays and orders each bucket before concatenation.

### Complexity

| Property | Complexity |
|---|---|
| Expected time | `O(n + k)` under suitable distribution assumptions |
| Worst-case time | `O(n²)` with insertion sorting when most values occupy one bucket |
| Auxiliary space | `O(n + k)` |
| `k` | Number of buckets |
| Input requirement | Values that can be mapped consistently to ordered intervals |

### When bucket sort is suitable

Bucket sort is useful for:

- Uniformly or reasonably distributed decimal measurements.
- Normalized scores.
- Bounded measurements such as latency or sensor readings.
- Numeric values with a meaningful interval.
- Workloads where buckets are expected to remain relatively small.

### When bucket sort is unsuitable

A heavily skewed distribution may put most values into one bucket. In that situation, the local sorting method dominates execution time.

Bucket sort also requires careful numerical handling. Subtracting extreme floating-point values can overflow even when both endpoints are finite. The JavaScript, Java, and C++ implementations normalize values before calculating bucket positions. The Python implementation uses `Decimal` arithmetic for bucket placement.

NaN and infinite values are rejected because they do not have the ordinary finite interval behavior assumed by the bucket mapping.

## 4. Relationship Between the Algorithms

The algorithms exploit different properties of the input.

| Property | Counting Sort | Radix Sort | Bucket Sort |
|---|---|---|---|
| Primary input | Integers | Integer keys | Finite numeric values |
| Main mechanism | Frequency counts | Stable digit distribution | Interval distribution |
| Depends on value range | Strongly | Through digit count | Through interval mapping |
| Depends on distribution | No | No | Yes |
| Handles negative values | With an offset | With an ordering transformation | Through interval normalization |
| Stable implementation possible | Yes | Yes | Yes, depending on local sorting |
| Main memory concern | Frequency-array size | Temporary arrays per pass | Bucket storage |
| Main failure mode | Excessive integer range | Incorrect digit or sign handling | Skewed bucket distribution |

The algorithms are not interchangeable.

Counting sort is most effective when the integer range is small. Radix sort is useful for integer data with a large range but a manageable digit representation. Bucket sort is useful when values can be distributed effectively across a numeric interval.

## 5. Algorithm Selection

The implementations include automatic selection policies based on data type, input size, and value range.

The default decision process is:

    Start
      |
      v
    Validate input values
      |
      +---- Decimal or mixed numeric values
      |          |
      |          v
      |      Bucket sort
      |
      +---- Integer values
                 |
                 v
           Calculate value range
                 |
                 +---- Small bounded range
                 |          |
                 |          v
                 |      Counting sort
                 |
                 +---- Wide integer range
                            |
                            v
                         Radix sort

This policy is a practical heuristic, not a universal performance guarantee.

The automatic selectors use a maximum counting range and compare the range with the input size. They do not assume that every integer dataset should use counting sort.

The bucket-sort selection assumes that numeric values are suitable for interval distribution. A production deployment should evaluate actual distribution patterns before making this choice permanently.

### Comparison sorting as a baseline

Comparison sorting is retained for verification and performance measurement.

A comparison sort does not require a bounded numeric interval or a digit representation. Its general-purpose behavior makes it an important fallback for data that does not satisfy non-comparison sorting assumptions.

For comparison-based sorting algorithms with `O(n log n)` behavior, non-comparison methods can offer an advantage when their input assumptions hold:

- Counting sort can achieve `O(n + k)`.
- Radix sort can achieve `O(d(n + b))`.
- Bucket sort can achieve expected `O(n + k)` under suitable distribution.

An asymptotically better expression does not automatically imply faster execution. Allocation, cache locality, memory bandwidth, input size, and implementation overhead all influence actual performance.

## 6. Python Implementation

The Python script provides a sorting laboratory using standard-library components.

| Component | Purpose |
|---|---|
| `Algorithm` enum | Defines supported sorting methods |
| `SortingError` | Represents invalid inputs and unsupported configurations |
| `SortReport` dataclass | Stores algorithm, output, input size, and elapsed time |
| `validate_integers` | Rejects non-integer input and booleans |
| `validate_numbers` | Rejects unsupported and non-finite numeric values |
| `counting_sort` | Implements signed integer frequency counting |
| `radix_sort` | Processes arbitrary-precision integer keys in byte-sized passes |
| `bucket_sort` | Uses decimal interval mapping and insertion sorting |
| `select_algorithm` | Chooses a strategy from type and range information |
| `benchmark` | Compares outputs against a reference result |

The Python radix implementation uses arbitrary-precision integer arithmetic. It does not assume that every input fits in a fixed-width machine integer.

The bucket implementation uses `Decimal` when calculating interval positions. Original values remain unchanged in the output.

The benchmark uses `perf_counter_ns()` for high-resolution duration measurement. It checks both ordering and value frequencies.

## 7. JavaScript Implementation

The JavaScript file provides an event-driven sorting pipeline for Node.js.

Its main architectural components are:

| Component | Responsibility |
|---|---|
| `SortingPipeline` | Manages sorting jobs |
| `Map` | Stores jobs by unique identifier |
| `EventEmitter` | Publishes state changes and completion events |
| `Promise` | Represents asynchronous job execution |
| `AbortSignal` | Supports cancellation before sorting starts |
| `performance.now()` | Measures execution duration |
| `SetImmediate` scheduling | Yields before processing a queued job |

The pipeline maintains explicit states:

`queued -> running -> completed`

A job may instead move to `failed` or `cancelled`.

Job identifiers are registered before execution is scheduled. This prevents two submissions with the same identifier from being accepted.

The integer radix implementation uses `BigInt` internally to calculate signed offsets and digit positions accurately. The public dataset remains an array of safe JavaScript integers.

The bucket implementation validates finite numbers and scales extreme values before calculating interval positions. This avoids overflow caused by direct subtraction of opposite floating-point extremes.

Cancellation is checked before the synchronous sorting operation starts. Once a sorting operation is executing, the current implementation does not interrupt it midway.

## 8. C++17 Implementation

The C++ program represents a telemetry-processing workload.

Sensor status codes are handled as signed 64-bit integers. Network latency measurements are handled as finite floating-point values.

The `RepositoryTelemetrySorter` class separates integer and decimal processing. Integer requests can use counting sort, radix sort, or comparison sorting. Decimal requests can use bucket sorting or comparison sorting.

Important implementation decisions include:

- `std::vector` provides contiguous storage for values and temporary arrays.
- `std::array` provides fixed-size radix frequency storage.
- `__int128` safely calculates integer ranges beyond the signed 64-bit difference limit on compilers supporting this extension.
- `std::uint64_t` and sign-bit transformation preserve signed ordering during radix sorting.
- `std::chrono::steady_clock` measures elapsed time.
- `std::isfinite` rejects NaN and infinite measurements.
- `std::sort` supplies reference output for correctness verification.

The radix implementation always processes eight byte positions, covering the complete signed 64-bit domain.

The counting implementation checks the range before allocating its frequency vector. A large interval is rejected rather than silently consuming excessive memory.

The bucket implementation uses `long double` for interval arithmetic and insertion sorting within individual buckets.

## 9. Java 17 Implementation

The Java implementation models sorting as an enterprise service rather than a collection of independent algorithm demonstrations.

### Domain model

`SortRequest` captures a job identifier, requested algorithm, and one numeric dataset. It validates input and creates immutable copies of accepted collections.

`SortResult` records the selected algorithm, ordered output, and execution duration.

`JobSnapshot` provides a read-only representation of a job's state.

`Algorithm` and `JobState` enums constrain supported values and lifecycle states.

### Policy evaluation

`SortingPolicy` is separate from algorithm execution.

For automatic requests, the policy:

- Selects bucket sort for decimal workloads.
- Examines integer range before selecting counting sort.
- Selects radix sort when the integer range exceeds counting-sort limits.

`BigInteger` is used for range calculation because subtracting `Long.MIN_VALUE` from `Long.MAX_VALUE` cannot be represented by a signed `long`.

### Job execution and state transitions

`RepositorySortingService` uses a bounded `ThreadPoolExecutor`.

The executor has:

- Two worker threads.
- A queue capacity of sixteen jobs.
- A rejection policy when the service is at capacity.

`ConcurrentHashMap` stores job records. `AtomicReference` protects state transitions against concurrent updates.

`CompletableFuture` returns each job's result to the submitting caller.

The service validates its output against an independently sorted reference array before marking a job as completed. Failure changes the job state to `FAILED` and completes its future exceptionally.

The bounded queue is a deliberate resource-management decision. An unbounded work queue can allow large sorting requests to accumulate until memory pressure becomes a system-level failure.

## 10. PostgreSQL Implementation

The PostgreSQL script models the sorting process as a relational workflow.

### Relational model

    algorithm_catalog
          |
          |
    sorting_job
          |
          +--------------------+
          |                    |
          v                    v
    sorting_input       sorting_execution

`algorithm_catalog` describes available algorithms and their supported data categories.

`sorting_job` records the requested strategy, workload type, lifecycle state, and any failure reason.

`sorting_input` stores each numeric value with its original ordinal position. The unique constraint on `(job_id, ordinal)` prevents duplicate positions within one workload.

`sorting_execution` stores the selected algorithm, sorted output array, item count, execution duration, and execution timestamp.

### Database constraints and indexes

The relational model enforces:

- Valid numeric workload types.
- Supported algorithm names.
- Valid job states.
- Positive input ordinals.
- Unique input positions within a job.
- Foreign-key integrity between jobs and their input and execution records.
- Valid execution counts and non-negative durations.
- A failure reason for jobs recorded in the failed state.

The input index on `(job_id, ordinal)` supports ordered retrieval of a workload.

The execution index on `(job_id, executed_at DESC)` supports recent-execution lookup for a job.

### PL/pgSQL sorting functions

The database implements the three algorithms independently.

`counting_sort` uses a bounded `BIGINT[]` frequency array and supports negative values through offset calculation.

`radix_sort_bigint` uses stable decimal digit passes. Its numeric offset calculation protects the algorithm against overflow across the signed `BIGINT` domain.

`bucket_sort_numeric` distributes finite `NUMERIC` values across JSONB array buckets. Each bucket is ordered independently before the final result is assembled.

The JSONB representation allows buckets to contain different numbers of values. A conventional multidimensional SQL array requires rectangular dimensions and would not provide the same variable-length bucket structure.

### Transactional execution

`execute_sorting_job` performs the database workflow:

1. Locks the selected job row.
2. Rejects jobs that are not queued.
3. Moves the job into the running state.
4. Retrieves input values in their original ordinal order.
5. Evaluates the requested or automatic algorithm.
6. Executes the selected sorting function.
7. Records the output and duration.
8. Marks the job as completed.

The execution insert activates a validation trigger. The trigger compares the sorted input multiset with the stored output multiset and checks cardinality.

The procedure and its database writes execute within the caller's transaction. An exception causes the transaction's changes to be rolled back, preventing a partially completed execution from being committed.

The `sorting_job_report` view joins job information with input counts and the most recent execution.

The included queries cover output retrieval, sortedness checks, frequency reporting, runtime aggregation, failed jobs, and cardinality validation.

## 11. Stability and Correctness

A sorting algorithm is stable when equal-key elements retain their original relative order.

Stability matters when records have multiple attributes. For example, a dataset may first be ordered by department and then stably ordered by employee score. Equal scores can retain their previous department ordering.

Counting sort and radix sort can be implemented stably. Bucket sort can also preserve stability when distribution and local sorting preserve the order of equal values.

The value-only examples focus on ordering and multiplicity. They do not model application records with unique identities or secondary attributes. A record-oriented production implementation should store the original record alongside its sorting key.

Correctness validation in the source files checks:

- Non-decreasing output order.
- Preservation of input cardinality.
- Preservation of duplicates.
- Preservation of negative values.
- Empty and single-element input behavior.
- Rejection of unsupported types and non-finite values.
- Safe handling of large integer ranges.

The PostgreSQL execution trigger validates the input and output multisets independently of the algorithm implementation.

## 12. Performance and Memory Considerations

Selecting a non-comparison algorithm requires evaluating the complete workload rather than only its element count.

| Workload characteristic | Suitable approach | Primary consideration |
|---|---|---|
| Many integers in a narrow range | Counting sort | Frequency-array memory |
| Signed integers across a wide range | Radix sort | Number of digit passes |
| Finite values with balanced distribution | Bucket sort | Bucket occupancy |
| Skewed or unknown distribution | Comparison sort | Predictable general-purpose behavior |
| Extremely large input | Workload-specific policy | Memory bandwidth and allocation |
| Small input | Often comparison sort | Non-comparison setup overhead |

### Memory allocation

Counting sort allocates storage based on the complete integer range. A range limit is necessary to prevent an unexpectedly large allocation.

Radix sort allocates temporary storage proportional to the input size. This is more predictable for fixed-width integer types.

Bucket sort allocates multiple bucket containers. Excessive bucket counts increase allocation overhead, while insufficient bucket counts can create large individual buckets.

### Cache behavior

Frequency arrays and bucket collections may create memory-access patterns different from sequential comparison sorting.

Radix passes generally read input values sequentially and write into temporary arrays. This can be effective for large workloads, though repeated passes move data multiple times.

Counting sort can be highly efficient when the frequency array fits comfortably in memory. A large frequency array can reduce that advantage.

### Benchmark interpretation

Elapsed times depend on:

- Input size.
- Integer range.
- Number of digit passes.
- Numeric distribution.
- Memory allocation.
- Runtime optimization.
- Cache behavior.
- Operating-system scheduling.

The sample programs use local timing mechanisms. Their measurements are useful for exploring workloads but are not a replacement for controlled production benchmarking.

## 13. Validation and Operational Limits

The implementations deliberately reject or limit inputs that violate their algorithm assumptions.

| Condition | Handling |
|---|---|
| Empty input | Return an empty sorted result |
| One value | Return the original value |
| Duplicate values | Preserve all occurrences |
| Negative integers | Use offset keys or signed-order transformations |
| Counting range too large | Reject before allocation |
| NaN or infinity | Reject numeric bucket input |
| Unsupported numeric type | Raise a validation error |
| Duplicate job identifier | Reject the new submission |
| Full Java execution queue | Reject work rather than allow unbounded growth |
| Invalid job state | Reject the database transition |
| Incorrect output multiset | Reject execution result |

The input-size limits are protective defaults for the examples. A production system should configure them according to available memory and operational capacity.

The implementations favor clear allocation boundaries and independently verifiable output over attempts to accept every possible numeric representation.

## 14. Practical Decision Criteria

A non-comparison algorithm is appropriate when its assumptions are supported by the actual data.

Counting sort is the strongest choice when the integer range is tightly bounded and the frequency array remains small.

Radix sort is appropriate when integer values have a manageable digit representation but a range too wide for counting sort.

Bucket sort is appropriate when values can be distributed across intervals without excessive concentration in a small number of buckets.

Comparison sorting remains useful when the data representation is complex, distribution is unpredictable, or the overhead of a specialized algorithm exceeds its expected benefit.

The central engineering decision is not whether non-comparison sorting is theoretically faster. It is whether the structure of a particular dataset permits the algorithm to reduce total processing cost without introducing excessive memory use, fragile assumptions, or correctness risks.
