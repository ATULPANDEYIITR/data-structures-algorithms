# Advanced Heap Problems: Algorithms, Scheduling and Greedy Optimization

## Technical Scope

This project implements advanced heap-based algorithms across five programming and database environments.

The central data structure is the binary heap. Its ability to maintain an efficiently accessible minimum or maximum element makes it suitable for streaming statistics, priority scheduling, sorted data processing, and greedy optimization.

The implementations cover six problem categories:

| Problem | Primary technique | Main application |
|---|---|---|
| Median from Data Stream | Two heaps | Real-time statistical monitoring |
| Priority Task Scheduling | Min heap | CPU and background job scheduling |
| Merge K Sorted Lists | Min heap | Distributed data processing |
| Maximum Capital | Sorting and max heap | Investment selection |
| Minimum Refueling Stops | Max heap | Resource optimization |
| Deadline Profit Scheduling | Min heap | Time-constrained task selection |

Each implementation is independently executable and includes validation and failure handling.

## 1. Binary Heap Fundamentals

A binary heap is a complete binary tree that satisfies a heap-ordering property.

A complete binary tree fills each level from left to right before creating nodes at the next level.

Two common heap types are:

| Property | Min heap | Max heap |
|---|---|---|
| Root element | Smallest | Largest |
| Parent relationship | Parent ≤ children | Parent ≥ children |
| Primary operation | Extract minimum | Extract maximum |
| Typical application | Earliest event | Highest priority |

A heap is commonly represented using an array rather than explicitly allocated tree nodes.

For a zero-based array:

- Parent of index `i`: `(i - 1) / 2`
- Left child: `2i + 1`
- Right child: `2i + 2`

The array representation avoids pointer overhead and provides efficient memory locality.

### Core operation complexity

| Operation | Complexity |
|---|---:|
| Access root | O(1) |
| Insert | O(log n) |
| Extract root | O(log n) |
| Heap construction | O(n) |
| Search arbitrary value | O(n) |
| Heap storage | O(n) |

A heap is not a completely sorted collection. Only the relationship between parents and children is guaranteed.

This distinction is important when selecting a data structure for a particular operation.

## 2. Median from Data Stream

### Problem definition

A data stream supplies numerical observations sequentially. The median must be available after each insertion without sorting the entire collection repeatedly.

For an odd number of observations, the median is the middle value.

For an even number, it is the arithmetic mean of the two middle values.

Example:

`12, 4, 5, 3, 8, 7`

The sorted sequence is:

`3, 4, 5, 7, 8, 12`

The median is:

`(5 + 7) / 2 = 6`

### Two-heap architecture

The collection is divided into two partitions.

| Heap | Contents | Implementation |
|---|---|---|
| Lower heap | Smaller half | Max heap |
| Upper heap | Larger half | Min heap |

The root of the lower heap is the largest element in the smaller partition.

The root of the upper heap is the smallest element in the larger partition.

Two invariants must remain valid:

1. Every lower-partition element is less than or equal to every upper-partition element.
2. The lower heap contains either the same number of elements as the upper heap or exactly one additional element.

The median can therefore be obtained directly from the heap roots.

For an odd number of observations:

`median = maximum(lower)`

For an even number:

`median = (maximum(lower) + minimum(upper)) / 2`

### Insertion workflow

1. Insert the new value into the lower heap.
2. Transfer its largest element if the partition ordering is violated.
3. Rebalance the heap sizes.
4. Read the median from the root elements.

### Complexity

| Operation | Complexity |
|---|---:|
| Insert observation | O(log n) |
| Retrieve median | O(1) |
| Storage | O(n) |

### Edge cases

The implementations account for:

- An empty stream.
- Negative values.
- Repeated observations.
- Increasing sequences.
- Decreasing sequences.
- Even and odd stream sizes.
- Large integer values and overflow concerns.

The Python and JavaScript versions also demonstrate the validation of incoming numerical data.

### Practical applications

- Server response-time monitoring.
- Network latency analysis.
- Financial transaction monitoring.
- Sensor data analysis.
- Real-time operational dashboards.

For distributed streams, each partition requires an aggregation strategy. The median of partition medians is not generally the median of the complete dataset.

## 3. Priority Task Scheduling

### Problem definition

A scheduler receives tasks with different priority levels. It must select the highest-priority waiting task whenever execution capacity becomes available.

The implementations use a min heap where a smaller priority number represents a more urgent task.

For equal priorities, submission order determines execution order.

### Scheduling data model

Each task contains:

| Field | Meaning |
|---|---|
| Task ID | Unique identifier |
| Priority | Scheduling priority |
| Sequence | Submission order |
| Duration | Expected execution time |
| State | Current execution state |

The task lifecycle is:

`WAITING → RUNNING → COMPLETED`

Failure handling introduces an alternative transition:

`RUNNING → FAILED`

The Python and Java implementations explicitly represent task states. The JavaScript implementation adds event-driven notifications.

### Scheduling mechanics

The scheduler inserts each task into a priority queue.

When execution capacity becomes available:

1. Extract the highest-priority task.
2. Mark it as running.
3. Execute its operation.
4. Record completion or failure.
5. Select the next task.

### Event-driven JavaScript implementation

The JavaScript scheduler extends Node.js `EventEmitter`.

It produces events for:

- `submitted`
- `started`
- `completed`
- `failed`

Task execution uses asynchronous functions and `await`.

This allows a scheduler to coordinate operations that involve asynchronous I/O without requiring third-party packages.

A failed task does not automatically terminate the entire scheduling loop.

### Enterprise considerations

A production scheduler needs more than priority ordering.

Important operational concerns include:

- Duplicate task prevention.
- Task ownership.
- Retry limits.
- Execution timeouts.
- Cancellation.
- Persistence.
- Worker health.
- Concurrent task claiming.
- Starvation prevention.
- Dead-letter processing.

The in-memory implementations demonstrate ordering and execution behavior. The PostgreSQL implementation demonstrates persistent job state and concurrent claiming.

The example schedulers are non-preemptive. Once execution begins, a higher-priority arrival does not interrupt the running task.

## 4. Merge K Sorted Lists

### Problem definition

Given K individually sorted sequences, produce one globally sorted sequence.

Example:

| Input | Values |
|---|---|
| List A | 1, 4, 7 |
| List B | 2, 5, 8 |
| List C | 3, 6, 9 |

Expected result:

`1, 2, 3, 4, 5, 6, 7, 8, 9`

### Why a heap is appropriate

A naive implementation repeatedly scans all K lists to locate the smallest available element.

That approach can require O(NK) work.

A min heap maintains only the current smallest candidate from each nonempty list.

The process is:

1. Insert the first element of each nonempty list.
2. Extract the smallest element.
3. Append it to the result.
4. Insert the next element from the same source list.
5. Continue until the heap becomes empty.

Each heap entry stores:

- Value.
- Source list index.
- Position within that list.

### Complexity

Let:

- K represent the number of input lists.
- N represent the total number of elements.

The complexity is:

| Operation | Complexity |
|---|---:|
| Initial heap construction | O(K log K) |
| Processing all elements | O(N log K) |
| Output storage | O(N) |
| Auxiliary heap storage | O(K) |

The total time complexity is O(N log K).

### Practical applications

- Merging database result streams.
- External sorting.
- Log aggregation.
- Distributed event processing.
- Merging time-series data.
- Combining sorted transaction files.

### Important distinction

The algorithm assumes every input sequence is already sorted.

It does not sort individual input lists before merging. Validation is performed before processing.

For large datasets, storing all input sequences and the complete output in memory may be impractical. A production implementation can use iterators, files, or streaming interfaces.

## 5. Greedy Optimization: Maximum Capital

### Problem definition

An investor has initial capital and a collection of projects.

Each project specifies:

- Required starting capital.
- Expected profit.

A project becomes eligible when available capital reaches its requirement.

Completing a project increases available capital by its profit.

The objective is to maximize final capital while selecting no more than K projects.

### Greedy strategy

The implementation combines sorting and a max heap.

The algorithm works in two stages.

**Stage A: Sort projects**

Sort projects by required capital in ascending order.

**Stage B: Select the most profitable affordable project**

1. Identify all projects affordable with current capital.
2. Insert them into a max heap.
3. Extract the project with maximum profit.
4. Add its profit to capital.
5. Repeat until the selection limit is reached or no profitable eligible project remains.

### Example

Initial capital: `1`

| Project | Required capital | Profit |
|---|---:|---:|
| Infrastructure | 0 | 2 |
| Analytics | 1 | 5 |
| Security | 2 | 8 |
| Cloud | 5 | 10 |

Selection:

| Stage | Capital before | Selected project | Capital after |
|---|---:|---|---:|
| 1 | 1 | Analytics | 6 |
| 2 | 6 | Cloud | 16 |
| 3 | 16 | Security | 24 |

Final capital: `24`.

The same algorithm is implemented in the four programming languages.

### Complexity

Sorting requires O(N log N).

Each project can enter the affordable heap once and be removed at most once.

The total complexity is O(N log N).

### Practical applications

- Investment portfolio selection.
- Capital allocation.
- Infrastructure expansion.
- Project prioritization.
- Budget-constrained resource allocation.

### Assumptions and limitations

The implementation assumes:

- Projects are independent.
- Each project can be selected only once.
- Profit is realized immediately.
- Projects cannot require additional capital after selection.
- Expected profit is non-negative.

Real investment decisions may require risk, time, dependency, and uncertainty models. Maximizing expected profit alone does not constitute a complete investment strategy.

## 6. Greedy Optimization: Minimum Refueling Stops

### Problem definition

A vehicle must travel to a destination.

It starts with a limited quantity of fuel and can refuel at stations along the route.

Each station has:

- Position.
- Available fuel.

The objective is to reach the destination with the fewest possible refueling stops.

### Greedy strategy

The algorithm uses a max heap containing the fuel quantities of stations already passed but not yet selected.

At each station:

1. Determine whether the station is reachable.
2. If it is not reachable, select the previously available station offering the largest fuel quantity.
3. Increase reachable distance by that quantity.
4. Repeat until the current station becomes reachable.
5. Add the current station to the available-station heap.

After processing all stations, continue selecting the largest previously available fuel quantities until the destination becomes reachable.

If the heap becomes empty before the destination is reachable, the journey is impossible.

### Complexity

For N fuel stations:

- Sorting: O(N log N).
- Heap insertion: O(log N).
- Heap extraction: O(log N).
- Total: O(N log N).

Auxiliary heap storage: O(N).

### Practical applications

- Vehicle route planning.
- Fuel-resource allocation.
- Battery charging optimization.
- Resource replenishment.
- Logistics planning.

### Important assumptions

The standard greedy solution assumes:

- Stations can be used only once.
- All available fuel at a selected station is taken.
- Fuel consumption per unit distance is constant.
- There is no maximum tank capacity.
- Station positions are known.
- Fuel quantities are non-negative.

A vehicle with limited tank capacity requires a different optimization model.

The implementation reports `-1` when the destination is unreachable.

## 7. Deadline-Based Profit Scheduling

### Problem definition

A collection of jobs is available.

Each job has:

- A deadline.
- A profit.
- A duration of exactly one scheduling unit.

Only one job can occupy a scheduling unit.

The objective is to maximize total profit while completing selected jobs before their deadlines.

### Greedy strategy

The algorithm sorts jobs by increasing deadline.

A min heap maintains the currently selected jobs.

For each job:

1. Add the job to the heap.
2. Add its profit to the total.
3. If the number of selected jobs exceeds the current deadline, remove the lowest-profit job.
4. Continue until every job has been evaluated.

This maintains a maximum-profit feasible subset under the unit-duration scheduling assumptions.

### Example

| Job | Deadline | Profit |
|---|---:|---:|
| A | 2 | 100 |
| B | 1 | 19 |
| C | 2 | 27 |
| D | 1 | 25 |
| E | 3 | 15 |

Selected jobs:

- A
- C
- E

Maximum profit: `142`.

### Complexity

| Operation | Complexity |
|---|---:|
| Sorting | O(N log N) |
| Heap insertion | O(log N) |
| Heap extraction | O(log N) |
| Total | O(N log N) |

### Limitations

This algorithm assumes all jobs have identical execution duration.

For variable-duration jobs, the problem requires a different scheduling formulation.

Deadlines, release times, precedence relationships, and machine constraints can substantially change the optimal solution.

## 8. Implementation Architecture

The five source files approach the same algorithmic domain from different engineering perspectives.

| Deliverable | Engineering perspective | Main mechanisms |
|---|---|---|
| Python | Algorithm simulation | `heapq`, dataclasses, exceptions, unittest |
| JavaScript | Event-driven processing | Custom heap, Maps, Sets, Promises, EventEmitter |
| C++17 | Efficient algorithm implementation | STL priority queues, structs, comparators, overflow checks |
| Java 17 | Enterprise domain modeling | Records, interfaces, immutable results, services, exceptions |
| PostgreSQL | Persistent workflow management | Relational tables, constraints, functions, triggers, transactions |

### Python

The Python implementation uses the standard-library `heapq` module.

Because Python's `heapq` provides a min heap, the median implementation stores negated integers to represent the lower max heap.

Dataclasses provide explicit domain structures for tasks, projects, stations, and deadline jobs.

The automated tests cover representative valid inputs and important failure conditions.

### JavaScript

The JavaScript implementation provides its own generic binary heap.

This makes comparator behavior explicit and allows different algorithms to use the same data structure.

The priority scheduler uses `EventEmitter` and asynchronous task execution.

The use of `Map` preserves task execution results, while `Set` prevents duplicate task identifiers.

### C++17

The C++ implementation uses STL priority queues.

Custom comparator structures define priority behavior without requiring an external library.

The implementation also addresses:

- Integer conversion.
- Overflow checks.
- Input validation.
- Deterministic tie-breaking.
- Empty heap operations.
- Exception handling.

### Java 17

The Java implementation uses records for immutable domain data.

Interfaces separate task execution behavior from scheduling logic.

Service classes separate median maintenance, job scheduling, capital allocation, and other operations.

Immutable result records prevent accidental modification of returned decision data.

The scheduling service records completed and failed execution states.

### PostgreSQL

The SQL implementation models persistent workflows.

The database stores jobs, observations, sorted streams, projects, stations, and deadline tasks.

The relational implementation provides integrity constraints and reporting mechanisms that are not available in a purely in-memory heap.

## 9. PostgreSQL Data Architecture

The principal relationships are:

`Median Streams → Median Observations`

`Sorted Streams → Sorted Stream Values`

`Jobs → Job Execution History`

`Investment Projects → Capital Allocation Decisions`

`Capital Allocation Runs → Capital Allocation Decisions`

`Journeys → Fuel Stations`

`Journeys → Refueling Results`

`Deadline Tasks → Deadline Optimization Results`

### Job scheduling and concurrency

The `jobs` table stores persistent task information.

The `claim_next_job()` function uses:

- Priority ordering.
- Submission timestamps.
- `FOR UPDATE SKIP LOCKED`.
- An atomic update.

`SKIP LOCKED` allows concurrent workers to claim different waiting jobs without waiting for rows already locked by another worker.

The operation must run inside a transaction so the claim and state transition are committed atomically.

### State integrity

The `validate_job_transition()` trigger prevents invalid transitions from terminal states.

The audit trigger records state changes in `job_execution_history`.

These mechanisms separate operational state from historical evidence.

### Streaming median

PostgreSQL calculates the median using `percentile_cont(0.5)`.

This is a statistical ordered-set aggregate.

Unlike the two-heap streaming implementation, the SQL calculation operates over the stored observation set when queried.

It is appropriate for database reporting but does not provide the same incremental update complexity as a continuously maintained two-heap structure.

### K-way merging

The `merge_sorted_streams()` function globally orders values from multiple stored sequences.

Its output is equivalent to a sorted union of the stream contents, while preserving source identifiers.

The underlying table maintains an index on stream identifier and sequence position.

### Capital allocation

The `allocate_capital()` procedure records:

- Initial capital.
- Final capital.
- Project limit.
- Project selection order.
- Capital before each selection.
- Capital after each selection.

Each decision references a project and an allocation run.

This creates a persistent decision history rather than returning only the final amount.

### Refueling optimization

The refueling procedure demonstrates an array-backed max heap in PL/pgSQL.

It maintains the largest available fuel quantity at the root.

The implementation records reachability and the minimum number of stops.

The relational result table allows journey outcomes to be queried independently of the procedure execution.

### Deadline optimization

The deadline procedure uses a temporary relational structure to maintain selected tasks.

It repeatedly removes the lowest-profit task when the selected-task count exceeds the current deadline.

The result is persisted in `deadline_optimization_results`.

## 10. Algorithm Selection and Trade-offs

Different heap strategies solve different optimization problems.

| Algorithm | Heap structure | Selection criterion |
|---|---|---|
| Streaming median | Two heaps | Partition balance |
| Priority scheduling | Min heap | Lowest priority value |
| K-way merge | Min heap | Smallest available value |
| Maximum capital | Max heap | Highest affordable profit |
| Minimum refueling | Max heap | Largest previously available fuel |
| Deadline scheduling | Min heap | Lowest selected profit |

A min heap is not inherently less or more efficient than a max heap.

The choice depends on which element must be retrieved first.

A two-heap design is useful when the problem requires access to both sides of a partition.

A single heap is sufficient when the decision repeatedly selects one extremum.

Sorting is useful when eligibility changes monotonically, allowing elements to be introduced into a heap only when they become eligible.

## 11. Performance Considerations

Heap-based algorithms are effective when repeated minimum or maximum selection is required.

Important performance decisions include:

- Avoid repeatedly sorting the complete collection.
- Store only the necessary heap entries.
- Use deterministic tie-breaking.
- Validate sorted input once before merging.
- Avoid unnecessary object creation in high-volume processing.
- Use indexed relational access for database workflows.
- Keep transactional operations short.
- Avoid unbounded in-memory task queues.
- Consider memory limits when retaining complete data streams.

### Complexity comparison

Let N represent the number of observations, projects, jobs, or stations, and K represent the number of sorted lists.

| Problem | Time complexity | Auxiliary space |
|---|---|---|
| Median insertion | O(log N) | O(N) |
| Priority scheduling | O(N log N) | O(N) |
| Merge K lists | O(N log K) | O(K), excluding output |
| Maximum capital | O(N log N) | O(N) |
| Minimum refueling | O(N log N) | O(N) |
| Deadline scheduling | O(N log N) | O(N) |

For median calculation, retrieving the current median takes O(1).

For merge operations, output storage requires O(N), even though the auxiliary heap itself requires only O(K).

## 12. Security and Reliability

Heap algorithms operate on data, but production systems must also protect the workflows surrounding them.

### Input validation

Validate:

- Numeric ranges.
- Duplicate identifiers.
- Sorted input requirements.
- Non-negative fuel and profit.
- Valid deadlines.
- Task durations.
- Capital limits.

### Concurrency

A shared in-memory priority queue requires synchronization when accessed by multiple threads.

The Java median service synchronizes its operations.

The PostgreSQL job-claiming function demonstrates row-level concurrency control.

### Resource management

Unbounded queues can consume excessive memory.

Production scheduling systems should define:

- Queue capacity.
- Maximum task duration.
- Retry policies.
- Worker concurrency.
- Retention periods.
- Failure recovery.

### Financial and numerical safety

Capital, profit, and fuel calculations must not silently overflow.

The C++ and Java implementations use checked arithmetic for important accumulation operations.

The database uses explicit numeric precision for monetary values.

For production financial systems, rounding rules, currency precision, and audit requirements must be defined independently.

### Database security

A production deployment should use:

- Dedicated database roles.
- Least-privilege permissions.
- Restricted procedure execution.
- Transaction boundaries.
- Auditable state transitions.
- Controlled access to financial and operational records.

The SQL script demonstrates integrity mechanisms, not a complete authentication or authorization system.

## 13. Edge Cases and Failure Conditions

| Scenario | Expected behavior |
|---|---|
| Empty median stream | Reject median retrieval |
| Negative observations | Accept valid numerical values |
| Duplicate job ID | Reject submission |
| Equal task priorities | Preserve submission order |
| Failed asynchronous task | Record failure and continue |
| Unsorted input list | Reject merge operation |
| Empty input lists | Return empty merged output |
| No affordable project | Preserve existing capital |
| Zero-profit projects | Do not select them |
| Unreachable fuel station | Return `-1` |
| Insufficient total fuel | Return `-1` |
| Duplicate station position | Reject invalid input |
| No profitable deadline job | Return zero profit |
| Invalid job state transition | Reject database update |
| Concurrent database workers | Prevent duplicate row claiming |

## 14. Execution

### Python

Requirements: Python 3.10 or later.

Save the first source file as `heap_problems.py`.

Run:

`python heap_problems.py`

The demonstration executes the algorithms and runs the embedded unit tests.

### JavaScript

Requirements: Node.js 18 or later.

Save the second source file as `heap_problems.js`.

Run:

`node heap_problems.js`

The scheduler demonstrates asynchronous execution and event notifications.

### C++17

Save the third source file as `heap_problems.cpp`.

Compile:

`g++ -std=c++17 -O2 -Wall -Wextra -pedantic heap_problems.cpp -o heap_problems`

Run:

`./heap_problems`

On Windows PowerShell:

`.\heap_problems.exe`

### Java 17

Save the fourth source file as `AdvancedHeapProblems.java`.

Compile:

`javac --release 17 AdvancedHeapProblems.java`

Run:

`java AdvancedHeapProblems`

Enable assertions during execution when required:

`java -ea AdvancedHeapProblems`

### PostgreSQL

Requirements: PostgreSQL 15 or later.

Save the fifth source file as `advanced_heap_problems.sql`.

Execute:

`psql -U postgres -d your_database -f advanced_heap_problems.sql`

The SQL script creates the `heap_lab` schema and its database objects.

The script is transactional. Run it against a dedicated development database because it creates database objects and sample records.

The SQL script also demonstrates the use of PostgreSQL procedures, triggers, window functions, ordered-set aggregates, and transactional queue claiming.

## 15. Learning Outcomes

The implementations provide practical experience with:

- Binary heap construction and maintenance.
- Min-heap and max-heap behavior.
- Two-heap partitioning.
- Priority-based execution.
- Stable tie-breaking.
- K-way merging.
- Greedy resource allocation.
- Greedy scheduling.
- Asynchronous task execution.
- Immutable domain modeling.
- Relational workflow persistence.
- Transactional concurrency control.
- Data validation and failure handling.

The central engineering principle is to select a heap strategy according to the exact operation required by the problem.

A heap is most useful when a continuously changing collection must repeatedly expose its smallest or largest eligible element without fully sorting the collection after every update.
