# Heap Problems: Algorithms and Stream Processing

## 1. Technical Scope

This project implements fundamental and advanced heap problems across Python, JavaScript, C++17, Java 17, and PostgreSQL.

The main problems are:

- Finding the kth largest element.
- Finding the kth smallest element.
- Finding the top-k largest elements.
- Finding the most frequent elements.
- Merging multiple sorted arrays.
- Maintaining a running median.
- Maintaining the kth largest value in a continuous stream.

The implementations use binary heaps, priority queues, streaming algorithms, and database ranking operations.

The central design objective is to select an appropriate data structure for each problem rather than sorting an entire dataset unnecessarily.

## 2. Binary Heap Fundamentals

A binary heap is a complete binary tree that satisfies a heap-ordering property.

A complete binary tree fills each level from left to right, except possibly the final level.

Two principal heap configurations are used.

| Property | Min-Heap | Max-Heap |
|---|---|---|
| Root | Smallest element | Largest element |
| Parent-child rule | Parent is no greater than children | Parent is no smaller than children |
| Primary operation | Retrieve minimum | Retrieve maximum |
| Typical application | Kth largest | Kth smallest |

A binary heap is commonly stored in an array rather than using explicit tree nodes.

For an element at index `i`:

- Parent: `(i - 1) // 2`
- Left child: `2 * i + 1`
- Right child: `2 * i + 2`

These relationships eliminate the need for pointer-based tree structures.

### Heap operations

| Operation | Time complexity |
|---|---:|
| Peek at root | O(1) |
| Insert | O(log n) |
| Remove root | O(log n) |
| Replace root | O(log n) |
| Build heap | O(n) |
| Search arbitrary element | O(n) |

Heap construction uses bottom-up heapification. It is O(n), rather than O(n log n), because most nodes are close to the leaves and require little adjustment.

## 3. Kth Largest Element

The kth largest problem asks for the element occupying position k when values are arranged in descending order.

For example:

| Input | Rank | Result |
|---|---:|---:|
| `[3, 2, 1, 5, 6, 4]` | 1 | 6 |
| `[3, 2, 1, 5, 6, 4]` | 2 | 5 |
| `[3, 2, 1, 5, 6, 4]` | 3 | 4 |

### Min-heap approach

Maintain a min-heap containing no more than k elements.

1. Insert the first k elements.
2. Compare each remaining element with the heap root.
3. Ignore values smaller than or equal to the root.
4. Replace the root when a larger value arrives.
5. Return the root after processing all elements.

The root represents the smallest element among the retained k largest values.

This makes it the kth largest element in the complete input.

**Complexity**

- Time: O(n log k)
- Auxiliary space: O(k)

This approach is particularly useful when k is substantially smaller than n.

The Python, JavaScript, C++17, and Java 17 implementations use this strategy.

## 4. Kth Smallest Element

The kth smallest problem is the reverse of kth largest.

A max-heap maintains the k smallest values.

The root represents the largest value among those retained elements.

When a smaller input value arrives, it replaces the root.

After processing the input, the root is the kth smallest value.

**Complexity**

- Time: O(n log k)
- Auxiliary space: O(k)

This technique avoids sorting all elements when only one rank is required.

## 5. Top-K Elements

Top-k problems return multiple elements rather than a single ranked value.

For example:

Input: `[12, 3, 5, 7, 19, 4, 8, 15]`

Requested k: `4`

Result: `[19, 15, 12, 8]`

A min-heap of size k is maintained throughout processing.

The root is the weakest member of the current top-k collection. A new value replaces it only when the new value is larger.

The final heap contains the required elements, which can be sorted to produce descending output.

**Complexity**

- Selection: O(n log k)
- Final ordering: O(k log k)
- Space: O(k)

### Top-K frequent elements

Top-k frequent elements require two stages:

1. Count occurrences using a hash map.
2. Select the highest-frequency entries using a heap.

The implementations establish deterministic tie-breaking rules.

- Python: frequency descending, followed by the representation of the value.
- JavaScript: frequency descending, followed by insertion order.
- C++17: frequency descending, followed by value ascending.
- Java 17: frequency descending, followed by value ascending.

These rules make output reproducible within each implementation.

## 6. K-Way Merge

K-way merging combines multiple individually sorted sequences into one sorted sequence.

Example:

| Source | Sorted values |
|---|---|
| A | 1, 4, 7 |
| B | 2, 5, 8 |
| C | 3, 6, 9 |

Merged result:

`[1, 2, 3, 4, 5, 6, 7, 8, 9]`

### Algorithm

A min-heap stores one candidate from each nonempty input sequence.

Each heap entry contains:

- Current value.
- Source sequence identifier.
- Position within that source.

Processing follows these steps:

1. Insert the first element of every nonempty source.
2. Remove the smallest candidate.
3. Append its value to the output.
4. Insert the next element from the same source.
5. Continue until the heap becomes empty.

Only one active candidate per source is retained.

**Complexity**

For k sorted sequences containing N total elements:

- Time: O(N log k)
- Auxiliary heap space: O(k)
- Output space: O(N)

The Python implementation also provides an iterator-based merge that avoids materializing all source sequences.

### Practical applications

- Merging sorted log files.
- Combining database query results.
- External sorting.
- Processing distributed data partitions.
- Merging chronological event streams.
- Combining multiple ranking outputs.

The algorithm assumes that each source is already sorted. The implementations validate this requirement where applicable.

## 7. Running Median

A running median calculates the median after every new observation.

Sorting the entire collection after every insertion is inefficient for large streams.

A two-heap structure provides a more efficient approach.

### Two-heap architecture

| Heap | Structure | Contents |
|---|---|---|
| Lower heap | Max-heap | Smaller half |
| Upper heap | Min-heap | Larger half |

The following conditions must remain true:

1. Every lower-heap value is no greater than every upper-heap value.
2. The lower heap has either the same number of elements as the upper heap or exactly one more.
3. The median can therefore be calculated from the heap roots.

For an odd number of elements, the lower heap root is the median.

For an even number of elements, the median is the average of both roots.

Example:

| Inserted value | Running median |
|---:|---:|
| 5 | 5 |
| 15 | 10 |
| 1 | 5 |
| 3 | 4 |

**Complexity**

- Insertion: O(log n)
- Median retrieval: O(1)
- Space: O(n)

This design is appropriate for monitoring systems, financial observations, telemetry, and continuously arriving measurements.

## 8. Kth Largest in a Data Stream

A continuous stream may contain an unknown number of observations.

Keeping every value is unnecessary when only the kth largest value is required.

A min-heap of size k retains the largest k values seen so far.

For every incoming value:

1. Insert it when fewer than k elements exist.
2. Otherwise compare it with the heap root.
3. Replace the root when the new value is larger.
4. Return the root once k observations have been processed.

Before k observations exist, the result is undefined.

**Complexity**

- Each insertion: O(log k)
- Result retrieval: O(1)
- Memory: O(k)

The `KthLargestStream` classes in all four application languages implement this behavior.

## 9. Python Implementation

The Python file provides a reusable algorithm library and an executable demonstration.

### Main components

| Component | Responsibility |
|---|---|
| `BinaryHeap` | Generic min-heap or max-heap |
| `kth_largest` | Kth largest selection |
| `kth_smallest` | Kth smallest selection |
| `top_k_largest` | Top-k selection |
| `top_k_frequent` | Frequency ranking |
| `merge_sorted_arrays` | K-way merging |
| `merge_sorted_iterators` | Lazy merging |
| `RunningMedian` | Dynamic median |
| `KthLargestStream` | Streaming rank tracking |
| `StreamProcessor` | Combined stream analytics |
| `HeapTests` | Automated verification |

The implementation uses `heapq` for standard heap operations and a custom `BinaryHeap` to demonstrate heap mechanics.

The `dataclass`-based `HeapEvent` provides immutable event records.

Exceptions distinguish empty-heap conditions from invalid input.

The tests include:

- Min-heap ordering.
- Max-heap ordering.
- Kth element selection.
- Duplicate values.
- Empty inputs.
- Invalid ranks.
- Sorted-array validation.
- Running median.
- Stream updates.
- Randomized comparison against sorting-based reference results.

### Execution

Run the file using Python 3:

`python heap_problems.py`

The script executes the demonstrations and unit tests.

## 10. JavaScript Implementation

The JavaScript file provides an event-driven processing model.

### Main components

| Component | Responsibility |
|---|---|
| `BinaryHeap` | Comparator-based priority queue |
| `kthLargest` | Kth largest selection |
| `kthSmallest` | Kth smallest selection |
| `topK` | Top-k selection |
| `topKFrequent` | Frequency ranking |
| `mergeSortedArrays` | K-way merging |
| `RunningMedian` | Two-heap median |
| `KthLargestStream` | Streaming rank |
| `HeapEventProcessor` | Event-driven analytics |
| `simulatedStream` | Asynchronous input generator |

The heap accepts a comparator, allowing the same implementation to support different priority rules.

`Map` is used for frequency aggregation.

`EventEmitter` broadcasts processed observations to registered listeners.

`async` and `for await...of` support asynchronous stream processing.

Processing is sequential so that each event observes the state produced by earlier events.

The implementation uses safe-integer validation to avoid silently accepting integers outside JavaScript's exact integer range.

### Execution

Run:

`node heap_problems.js`

The program prints stream events, algorithm results, and test outcomes.

## 11. C++17 Implementation

The C++17 file emphasizes generic data structures, efficient STL containers, and explicit domain modeling.

### Main components

| Component | Responsibility |
|---|---|
| `BinaryHeap` | Generic binary heap |
| `kthLargest` | Kth largest |
| `kthSmallest` | Kth smallest |
| `topKLargest` | Top-k selection |
| `topKFrequent` | Frequency ranking |
| `mergeSortedArrays` | K-way merging |
| `RunningMedian` | Dynamic median |
| `KthLargestStream` | Continuous rank tracking |
| `GovernanceEngine` | Additional policy evaluation example |

The generic heap accepts a comparator and supports heap construction from an existing vector.

The STL `priority_queue` is used for specialized algorithms where a custom heap implementation is unnecessary.

The merge operation uses a priority queue containing source indices and element positions.

The running median implementation converts integer values to floating-point values before adding the two middle elements, avoiding signed integer overflow in the median calculation.

### Execution

Compile:

`g++ -std=c++17 -O2 -Wall -Wextra -pedantic heap_problems.cpp -o heap_problems`

Run:

`./heap_problems`

On Windows:

`heap_problems.exe`

The program includes assertions for algorithmic and validation behavior.

## 12. Java 17 Implementation

The Java implementation adopts a reusable enterprise-oriented structure.

### Main components

| Component | Responsibility |
|---|---|
| `BinaryHeap<T>` | Generic comparator-based heap |
| `kthLargest` | Kth largest |
| `kthSmallest` | Kth smallest |
| `topKLargest` | Top-k selection |
| `topKFrequent` | Frequency ranking |
| `mergeSortedArrays` | K-way merge |
| `RunningMedian` | Dynamic median |
| `KthLargestStream` | Stream ranking |
| `StreamAnalyticsService` | Stream processing service |
| `StreamEvent` | Immutable processing result |

Java records provide immutable structures for frequency entries, merge candidates, and stream events.

The generic heap separates ordering behavior from heap mechanics through `Comparator`.

`PriorityQueue` is used for efficient specialized operations.

`AtomicLong` provides sequence generation for accepted stream events.

The stream service synchronizes its state-changing methods to preserve consistent sequential updates when accessed by multiple threads.

The implementation avoids third-party dependencies.

### Execution

Compile:

`javac HeapProblems.java`

Run:

`java -ea HeapProblems`

Assertions are enabled through the `-ea` option.

## 13. PostgreSQL Implementation

The SQL file models heap-related analytics as a relational processing workflow.

PostgreSQL does not expose a general-purpose persistent binary heap through ordinary SQL. Its ordering, aggregation, and window-function capabilities provide equivalent result calculations.

The database implementation therefore distinguishes between:

- In-memory incremental heap processing.
- Relational ranking and aggregation.
- Persistent stream-event storage.
- Database-managed processing jobs.

### Database structure

| Table | Purpose |
|---|---|
| `datasets` | Input dataset registration |
| `dataset_values` | Dataset observations |
| `processing_jobs` | Algorithm processing requests |
| `stream_events` | Source stream observations |
| `stream_results` | Persisted stream analytics |

### Functions and procedures

| Database object | Functionality |
|---|---|
| `kth_largest` | Descending rank selection |
| `kth_smallest` | Ascending rank selection |
| `top_k_largest` | Ranked top-k retrieval |
| `top_k_frequent` | Frequency aggregation |
| `merge_sorted_streams` | Sorted stream merging |
| `running_median_view` | Running median calculation |
| `stream_kth_largest_view` | Stream ranking |
| `process_heap_job` | Processing-job execution |
| `validate_stream_event` | Stream input validation |

### Data integrity

The database uses:

- Primary keys for unique records.
- Foreign keys for dataset relationships.
- Unique constraints for source sequence numbers.
- Check constraints for valid job states and parameters.
- Indexes for ranking and stream retrieval.
- Triggers for input validation.

The processing procedure locks its selected job row before changing its state.

This prevents concurrent workers from independently claiming the same pending job through that procedure.

### SQL ranking versus an incremental heap

The distinction is important.

A database query using `ORDER BY` may need to examine and sort many records. An in-memory heap of size k can maintain a top-k result using O(k) memory and O(log k) update operations.

The database implementation prioritizes persistent storage, relational integrity, reporting, and transactional processing.

For high-volume streaming applications, incremental heap processing is generally more appropriate than recalculating rankings over the complete historical dataset after every event.

## 14. Complexity Comparison

Let:

- n represent the number of input elements.
- k represent the requested rank or number of retained elements.
- m represent the number of sorted input sequences.
- N represent the total number of elements across those sequences.

| Problem | Algorithm | Time | Auxiliary space |
|---|---|---:|---:|
| Heap construction | Bottom-up heapify | O(n) | O(1) additional for in-place heapification |
| Kth largest | Size-k min-heap | O(n log k) | O(k) |
| Kth smallest | Size-k max-heap | O(n log k) | O(k) |
| Top-k largest | Size-k min-heap | O(n log k + k log k) | O(k) |
| Top-k frequent | Frequency map and heap | O(n + u log k) | O(u + k) |
| K-way merge | Min-heap | O(N log m) | O(m) |
| Running median insertion | Two heaps | O(log n) | O(n) |
| Running median retrieval | Heap roots | O(1) | O(1) |
| Stream kth largest | Size-k min-heap | O(log k) per update | O(k) |

Here, u represents the number of distinct input values.

For a full sort, the usual time complexity is O(n log n). Heap-based selection is preferable when only a small number of ranked elements are required.

## 15. Edge Cases and Correctness

The implementations account for important boundary conditions.

| Condition | Expected behavior |
|---|---|
| Empty heap | Raise an empty-heap exception |
| k = 0 for top-k | Return an empty collection |
| k less than 1 for kth selection | Reject the request |
| k greater than input size | Reject the request |
| Duplicate values | Preserve duplicate occurrences |
| Negative values | Process normally |
| Single-element input | Return the only element for k = 1 |
| Empty sorted sequences | Ignore them during merging |
| Unsorted input sequence | Reject the merge |
| Fewer than k stream observations | Return an undefined rank |
| Even number of observations | Average the two middle values for median |
| Odd number of observations | Return the middle value |

A kth-largest calculation generally considers duplicate occurrences as separate positions.

For example, the second largest value in `[5, 5, 4]` is `5`, not `4`.

## 16. Engineering and Security Considerations

### Memory management

A size-k heap prevents unnecessary storage of all observations when only a limited ranking is required.

For a large number of sorted sources, the k-way merge maintains only one active candidate per source.

For an unbounded stream, the running median requires storage proportional to the number of processed observations. Exact median calculation cannot generally retain only a fixed number of observations.

### Input validation

Applications should validate:

- The requested rank.
- Input collection size.
- Integer boundaries.
- Source sequence ordering.
- Stream identity.
- Duplicate event identifiers.
- Missing observations.
- Batch size.

JavaScript uses safe-integer checks because its standard numeric type cannot represent every arbitrary-precision integer exactly.

### Concurrency

Concurrent stream processing introduces ordering challenges.

A production implementation should define:

- Event ordering.
- Duplicate-event handling.
- Atomic state updates.
- Recovery after processing failures.
- State persistence.
- Checkpoint boundaries.

The Java service synchronizes its update operations. The JavaScript implementation processes asynchronous events sequentially.

### Database security

The PostgreSQL implementation should operate under a restricted database role.

Production deployments should use:

- Least-privilege database permissions.
- Parameterized application queries.
- Transaction boundaries.
- Statement timeouts.
- Input-size restrictions.
- Controlled data retention.
- Monitoring of temporary disk usage.

Database indexes improve selected access patterns but introduce storage overhead and additional write costs.

## 17. Practical Applications

| Application | Heap technique | Purpose |
|---|---|---|
| Financial monitoring | Running median | Track changing market observations |
| Log analytics | Top-k frequent | Identify repeated error codes |
| Search systems | Top-k largest | Retrieve highest-scoring results |
| Distributed processing | K-way merge | Combine sorted partitions |
| Network monitoring | Stream kth largest | Track high-value measurements |
| Performance monitoring | Min-heap | Maintain largest latency observations |
| Data engineering | Priority queue | Schedule and process ordered events |
| Real-time analytics | Two heaps | Calculate continuously updated medians |

## 18. Implementation Limitations

The five implementations intentionally use different execution models.

- Python uses the standard `heapq` library alongside a custom binary heap.
- JavaScript uses a comparator-based heap and event-driven stream processing.
- C++17 uses generic heap structures and STL priority queues.
- Java 17 uses comparator-based priority queues, records, and a synchronized service.
- PostgreSQL uses relational ranking, aggregation, window functions, and persistent job processing.

The database implementation is not an incremental replacement for an in-memory heap.

The running median implementations retain all observations in their two heaps. They do not implement approximate quantile sketches or sliding-window expiration.

The stream examples process one logical stream at a time. Multi-producer production systems require explicit ordering and recovery policies.

These distinctions determine which implementation model is appropriate for a given workload.
