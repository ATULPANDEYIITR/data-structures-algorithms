# Deque Engineering: Double-Ended Queues and Sliding Window Extrema

## Technical scope

A double-ended queue, commonly called a deque, supports insertion and removal at both ends. It is useful when an algorithm must maintain a changing set of candidates without repeatedly shifting an array or rescanning every element.

Sliding-window maximum and minimum problems are particularly important applications. Given a sequence of measurements and a window size \(k\), the objective is to calculate the largest and smallest values in every contiguous group of \(k\) elements.

The implementations distinguish three related ideas:

- **Deque:** A data structure that provides efficient operations at the front and back.
- **Monotonic deque:** A deque whose candidate values remain ordered, allowing an extremum to be read from one end.
- **Sliding window:** A fixed-size interval that advances through a sequence, expiring old elements and accepting new ones.

The Python, JavaScript, C++, Java, and PostgreSQL implementations examine these ideas through different implementation styles, including a circular buffer, event-driven monitoring, a telemetry case study, a stateful enterprise service, and relational analytics.

## Deque operations and representation

A conventional deque supports insertion at either end, removal at either end, inspection of the front and back, and queries about its size or emptiness.

| Operation | Typical complexity | Purpose |
|---|---|---|
| Insert at front | \(O(1)\) amortized for a dynamic deque | Add a new leading element |
| Insert at back | \(O(1)\) amortized for a dynamic deque | Append an element |
| Remove from front | \(O(1)\) | Expire the oldest candidate |
| Remove from back | \(O(1)\) | Discard a dominated candidate |
| Inspect either end | \(O(1)\) | Retrieve the current extremum |
| Access an arbitrary middle element | Usually \(O(n)\) | Not the deque's primary use |

Exact complexity depends on the implementation. Python's `collections.deque` supports efficient operations at both ends. The JavaScript implementation uses a circular array and occasionally doubles its capacity. Its end operations are amortized \(O(1)\). The C++ and Java versions use their standard-library deque implementations.

### Circular-buffer mechanics

A circular buffer stores elements in an array and treats the last position as adjacent to the first. Its head position identifies the logical front, while its size determines the logical back.

For capacity \(C\), a logical offset \(i\) maps to physical index

\[
(\text{head}+i)\bmod C
\]

When the head moves backward, the buffer wraps to the last array position if necessary. This avoids shifting all stored elements after each front removal.

The Python `CircularDeque` uses a fixed capacity and raises an exception when full. The JavaScript `Deque` instead grows its array when required. These policies solve different problems: fixed capacity provides predictable storage, while dynamic growth supports workloads whose size is not known in advance.

A bounded deque that silently discards old entries is useful for retaining recent history, but it should not be used where overflow must be reported or every measurement must be preserved.

## Sliding-window maximum

Consider the measurements

`[1, 3, -1, -3, 5, 3, 6, 7]`

with a window size of three. The maximum values are

`[3, 3, 5, 5, 6, 7]`

A direct implementation examines all \(k\) values in every window. There are \(n-k+1\) windows, so the total time is

\[
O((n-k+1)k)=O(nk)
\]

The deque algorithm avoids repeating that work.

### Maintaining maximum candidates

The maximum algorithm stores indices rather than only measurement values.

- Indices that have moved outside the current window are removed from the front.
- Trailing indices whose values are less than or equal to the incoming value are removed from the back.
- The incoming index is appended to the back.
- Once the window is complete, the value at the front is its maximum.

The deque's candidate values are therefore monotonically decreasing from front to back.

Suppose the current candidates contain values `8, 6, 4`, and a new value of `9` arrives. The new value is greater than all three candidates. Any future window containing the new value will have a maximum of at least `9`, so the old candidates cannot provide the maximum while `9` remains in the window. They can all be removed.

This dominance rule is the central optimization. The algorithm does not preserve every value, only the values that could still become a future maximum.

### Why indices matter

Two equal values may occur at different positions. An older value expires before a newer value, even when both have the same magnitude. An index makes expiration precise:

\[
i_{\text{candidate}}\leq i_{\text{current}}-k
\]

The condition identifies candidates that no longer belong to the current window. Storing indices also avoids confusing repeated values with distinct occurrences.

## Sliding-window minimum

The minimum algorithm applies the same structure with the comparison reversed.

Its deque maintains monotonically increasing candidate values. When a new value arrives, trailing candidates greater than or equal to it are removed. The minimum is always at the front.

For the sequence

`[1, 3, -1, -3, 5, 3, 6, 7]`

and a window size of three, the minimum values are

`[-1, -3, -3, -3, 3, 3]`

The maximum and minimum algorithms share the expiration mechanism but preserve different candidate invariants. They are related implementations, not interchangeable ones.

## Linear-time analysis

Each index is inserted into a candidate deque once. It can be removed from the front once or discarded from the back once. Although a loop may remove several candidates during one iteration, no candidate can be removed repeatedly.

Across all \(n\) input elements, the total number of deque insertions and removals is bounded by a constant multiple of \(n\).

Consequently:

- **Time:** \(O(n)\) for a complete traversal.
- **Auxiliary space:** \(O(k)\) for a window of size \(k\).
- **Streaming suitability:** The algorithm can process values as they arrive without retaining the full input sequence.

The Python implementation also provides a combined minimum-and-maximum function. It maintains two independent candidate deques in a single traversal. The JavaScript implementation provides an event-driven monitor and an asynchronous input example. The C++ implementation models a telemetry service, while the Java implementation separates window policy from measurement processing.

## Python implementation

The Python script uses `collections.deque` for its optimized algorithms and includes a separate circular-buffer implementation to expose the underlying storage mechanics.

`sliding_window_maximum` and `sliding_window_minimum` validate their input before processing it. Both functions return one result for each complete window. `sliding_window_extrema` maintains two deques and returns minimum-maximum pairs.

The monotonic-deque trace shows how candidate indices evolve during a maximum query. This is more informative than inspecting the final output alone because it reveals why some values disappear before their windows expire.

The brute-force functions serve as correctness references. They deliberately use repeated window scans, making them suitable for small test inputs rather than production-scale processing.

The deterministic test suite compares the optimized functions with their reference implementations across singleton inputs, duplicates, negative values, increasing and decreasing sequences, and different window sizes. Invalid inputs are tested separately to verify that errors are raised rather than silently producing misleading results.

The benchmark uses a larger input for the optimized algorithm and a smaller input for the brute-force reference. Their elapsed times illustrate the difference in growth patterns, but they are not a controlled hardware benchmark.

## JavaScript implementation

The JavaScript file implements a circular-array deque with a dynamically expanding buffer. Its `_physicalIndex` method translates logical positions into array indices, while `_grow` copies logical elements into a larger buffer when the current capacity is exhausted.

The sliding-window functions use indices and a monotonic candidate order, matching the mathematical algorithm without relying on an external deque package.

The `SlidingWindowMonitor` demonstrates an event-driven design. Incoming measurements are processed immediately, and a callback receives each completed window. This is useful when a monitoring application needs to publish rolling statistics as data arrives.

`StreamingWindowExtrema` stores candidate records containing both an index and a value. It does not need the complete measurement history to calculate future extrema.

The asynchronous generator and `consumeMeasurements` function demonstrate integration with an asynchronous source. This pattern can be adapted to a stream reader, but the example itself uses deterministic in-memory readings. A real network consumer would also need reconnection policies, cancellation, backpressure, and source-specific error handling.

The implementation rejects non-finite numeric values. In particular, `NaN` breaks the expected comparison relationships required by monotonic queues. Input validation protects the algorithm's ordering invariant.

## C++ telemetry case study

The C++ program models a monitoring service that calculates rolling latency extrema.

`Measurement` associates each value with a sequence number. `WindowExtrema` represents the result interval and its minimum and maximum. `SlidingExtremaEngine` owns two candidate deques, one for each extremum, while `TelemetryService` processes a batch of readings and reports completed windows.

The engine rejects non-finite measurements and invalid window sizes. Its sequence numbers distinguish repeated measurements and make expiration independent of value equality.

The implementation uses `std::deque`, which provides efficient insertion and removal at both ends. It does not need to manage a raw circular buffer, allowing the case study to concentrate on the monitoring logic.

The brute-force functions independently calculate the minimum and maximum of each window. Correctness checks compare them against the optimized results for multiple small test sequences.

The service is illustrative rather than a complete production telemetry platform. A deployed system would also need timestamp ordering rules, missing-measurement handling, durable storage, concurrency coordination, and explicit behavior for delayed or duplicated events.

## Java enterprise implementation

The Java program separates policy, state, processing, and output.

`WindowPolicy` validates the configured window size. `Measurement` is an immutable record that rejects non-finite values. `WindowResult` represents a completed interval without exposing mutable internal candidate queues.

`WindowExtremaService` owns the two monotonic deques and tracks whether the service is accepting measurements or has been closed. Its synchronized methods protect the service's state when callers share an instance across threads.

The service validates a measurement before changing the deque state. This ordering prevents invalid input from partially modifying the candidate queues. After closure, attempts to accept new readings fail explicitly.

`MonitoringBatch` adapts a list of readings into completed window results. The test methods compare these results with brute-force references and verify that invalid measurements and closed-service transitions are rejected.

Synchronization alone does not establish an ordering policy for independently arriving measurements. A production service that receives concurrent events must define sequence assignment, event ordering, and whether delayed readings can revise previous results.

## PostgreSQL relational analytics

The SQL script models streams, measurements, window policies, and calculated results in a relational schema.

### Data model

| Table | Responsibility |
|---|---|
| `monitored_streams` | Identifies a telemetry stream and its measurement unit |
| `measurements` | Stores each measurement with a stream, timestamp, sequence, and value |
| `window_policies` | Defines the window size and whether a policy is active |
| `window_results` | Stores calculated extrema for a specific policy and interval |

Foreign keys ensure that measurements and policies refer to existing streams. Unique constraints prevent duplicate sequence numbers within a stream and duplicate result intervals within a policy. Check constraints reject nonpositive window sizes, invalid interval boundaries, and non-finite measurements.

The indexes support stream-and-time filtering and retrieval of recent window results. Their usefulness depends on the actual query workload and data distribution, so query plans should be inspected before making additional indexing decisions.

### Window functions and configurable windows

PostgreSQL window functions can calculate minimums and maximums over ordered partitions. The script uses a frame of two preceding rows and the current row to illustrate a three-sample window.

That frame is intentionally static. PostgreSQL does not permit an ordinary column reference to determine the numeric offset in a `ROWS` frame clause. The script therefore includes a correlated query using `LATERAL` to calculate windows whose sizes come from policy records.

The correlated query is straightforward and supports different window sizes, but it can repeatedly scan measurements for each endpoint. On large datasets, this may be expensive. An optimized implementation should evaluate available window sizes, query plans, indexing, and whether results should be incrementally maintained.

The `window_results` table provides a materialized record of computed extrema. The insert operation uses a uniqueness constraint and `ON CONFLICT` handling so that recalculation does not create duplicate intervals.

The final integrity query independently recomputes the extrema of each stored interval. It returns rows when a result does not match the underlying measurements or the expected number of samples. This provides a database-level audit of stored calculations.

## Edge cases and operational limits

### Window size of one

Each complete window contains one measurement, so its minimum and maximum are identical. This case verifies that the algorithm handles the smallest legal window without special-purpose logic.

### Window size equal to the input length

Exactly one result is produced. The entire sequence is the only complete window.

### Repeated values

When equal trailing values are removed, the newer index remains a valid candidate for longer. This reduces unnecessary candidate storage while preserving the correct result.

### Strictly increasing or decreasing input

Increasing values repeatedly eliminate trailing candidates from a maximum deque. Decreasing values do the opposite. These inputs are useful for testing because they exercise extreme patterns of candidate removal.

### Invalid measurements

The numeric implementations reject invalid window sizes and inappropriate value types. The floating-point implementations also reject `NaN` and infinity, whose behavior can violate the ordering assumptions of the candidate comparisons.

### Streaming and memory usage

A streaming algorithm needs only its candidate state for each active window. It does not need to retain the full input history. Its memory use is therefore proportional to the window size rather than the total number of observations.

The candidate deques may contain fewer than \(k\) entries because dominated elements are removed early. The worst-case auxiliary-space bound remains \(O(k)\).

### SQL versus in-memory processing

SQL window functions are useful for retrospective analytics, audit queries, and relational reporting. A monotonic deque is more appropriate when values arrive continuously and each new measurement must be processed with low incremental overhead.

The two approaches serve different execution models. SQL provides declarative query processing and relational integrity, while the in-memory deque maintains a compact state that can be updated as measurements arrive.
