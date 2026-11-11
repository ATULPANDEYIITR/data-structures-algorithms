# Heap Operations and Priority Queue Management

## 1. Technical Scope

This project implements binary heap operations and priority queue management across Python, JavaScript, C++17, Java 17, and PostgreSQL.

The implementations cover two related but distinct structures:

- A binary heap maintains a parent-child ordering invariant in a complete binary tree.
- A priority queue uses priority ordering to determine which element should be processed next.

The implementations include insertion, deletion, heap construction, heapify, extraction, priority updates, heap sorting, and task scheduling.

The examples use infrastructure and security operations to demonstrate priority-driven execution.

## 2. Binary Heap Fundamentals

A binary heap is a complete binary tree represented efficiently using an array.

A complete binary tree fills every level except possibly the final level. Nodes in the final level are placed from left to right.

The array representation avoids explicit tree-node objects.

For a zero-indexed array, the relationships are:

| Relationship | Formula |
|---|---|
| Parent | `(i - 1) // 2` |
| Left child | `2 * i + 1` |
| Right child | `2 * i + 2` |

For a node at index `i`, its children are stored at the calculated positions.

### Min-heap

A min-heap maintains:

`parent <= children`

The root contains the smallest element.

Example:

    Input: [40, 10, 30, 5, 20, 50]

    Valid min-heap:
             5
           /   \
         10     30
        /  \    /
       40  20  50

### Max-heap

A max-heap maintains:

`parent >= children`

The root contains the largest element.

The same collection can produce a different arrangement:

             50
           /    \
         20      40
        /  \     /
       5   10   30

The internal array arrangement is not unique. Multiple arrays can represent valid heaps containing the same elements.

## 3. Heap Operations

### Insertion

Insertion places the new element at the end of the array.

The new element is then compared with its parent.

If the heap property is violated, the elements are exchanged. This process continues until the element reaches a valid position or becomes the root.

This operation is called sift-up, bubble-up, or percolate-up.

Time complexity: `O(log n)`.

### Extraction

Extraction removes the root, which contains the minimum or maximum element.

The final array element replaces the root. Sift-down then restores the heap property.

At each level, the replacement element is compared with its children. It is exchanged with the higher-priority child when necessary.

Time complexity: `O(log n)`.

### Peek

Peek returns the root without changing the heap.

Time complexity: `O(1)`.

### Deletion

Deleting an arbitrary element requires locating its position.

The selected element is replaced with the last element and removed from the array.

The replacement must move either upward or downward, depending on its relationship with its parent and children.

The implementations expose indexed deletion and value-based deletion.

| Operation | Complexity |
|---|---:|
| Indexed deletion | `O(log n)` |
| Value-based search | `O(n)` |
| Value-based deletion | `O(n)` |

An indexed heap or an auxiliary value-to-index map can improve repeated arbitrary deletion.

### Priority update

An existing element can receive a new priority.

If its new value has higher heap priority, sift-up is performed.

Otherwise, sift-down is performed.

Only one direction is necessary for a valid heap with a consistent comparator.

Time complexity: `O(log n)` when the index is already known.

## 4. Heapify and Heap Construction

Heapify transforms an unordered array into a valid binary heap.

Two approaches are commonly used.

**Repeated insertion**

Each element is inserted individually.

Time complexity: `O(n log n)`.

**Bottom-up heap construction**

The algorithm begins with the final non-leaf node and applies sift-down in reverse level order.

The final non-leaf node is:

`floor(n / 2) - 1`

Leaf nodes already satisfy the heap property because they have no children.

Bottom-up heap construction takes `O(n)` time.

The linear complexity follows from the fact that most nodes are near the leaves and require little or no movement.

The Python, JavaScript, C++17, and Java implementations use bottom-up construction.

The PostgreSQL implementation provides an explicit `heap_build` operation.

## 5. Heap Sorting

Heap sort uses heap construction followed by repeated extraction.

For ascending sorting:

1. Construct a min-heap.
2. Extract the minimum.
3. Repeat until the heap becomes empty.

For descending sorting:

1. Construct a max-heap.
2. Extract the maximum.
3. Repeat until the heap becomes empty.

The implementations use a separate heap or a copied heap so that sorting does not modify the original collection.

| Property | Heap Sort |
|---|---|
| Construction | `O(n)` |
| Extraction | `O(log n)` |
| Total time | `O(n log n)` |
| Auxiliary heap storage | `O(n)` in these implementations |
| Stable | No |
| In-place | Not in the provided extraction-based versions |

A conventional in-place heap sort can achieve `O(1)` auxiliary space by operating directly on the input array.

## 6. Priority Queue Operations

A priority queue retrieves elements according to their priority rather than their arrival order.

The task scheduling examples use higher numerical values to represent higher priority.

Example:

| Task | Description | Priority |
|---|---|---:|
| T101 | Database backup | 3 |
| T102 | Security incident | 10 |
| T103 | Infrastructure monitoring | 5 |
| T104 | Critical outage | 10 |

The processing order is:

1. T102
2. T104
3. T103
4. T101

T102 precedes T104 because it was submitted first.

### Stable priority ordering

A heap does not automatically guarantee FIFO ordering for elements with equal priorities.

The implementations use a monotonically increasing sequence number.

The ordering rule is:

1. Higher priority first.
2. Earlier sequence number first when priorities are equal.

The sequence number is part of the priority queue entry, not the business task's priority.

This distinction ensures deterministic ordering without modifying the heap comparison rules.

### Duplicate task prevention

The Python implementation uses a set of active identifiers.

The JavaScript implementation uses a `Set`.

The C++ implementation uses `std::unordered_set`.

The Java implementation uses `HashSet`.

An identifier becomes available again after the corresponding task leaves the active queue.

The database enforces uniqueness through a unique constraint on the external task key.

## 7. Python Implementation

The Python implementation uses a generic `BinaryHeap` class with an explicit `HeapType` enumeration.

Its main mechanisms include:

- Dataclasses for domain objects.
- Exceptions for empty and invalid heap operations.
- Lists for heap storage.
- Sets for active task identifiers.
- `heapq` for production-oriented priority queue management.
- Assertions and unit tests for invariant validation.
- Randomized testing against Python's sorting behavior.

The custom heap supports both min-heap and max-heap behavior.

The `TaskPriorityQueue` uses tuples containing negative priority, sequence number, and task data.

Negative priorities allow Python's min-oriented `heapq` to implement maximum-priority scheduling.

The task identifier and sequence number prevent task objects from being compared when priorities are equal.

The tests validate extraction, insertion, deletion, updates, heapify, sorting, empty states, and duplicate identifiers.

## 8. JavaScript Implementation

The JavaScript implementation uses a custom `BinaryHeap` and a separate `PriorityQueue`.

Its engineering emphasis is event-driven task processing.

### Event-driven behavior

`TaskProcessor` extends Node.js `EventEmitter`.

It emits events for:

- Task submission.
- Task processing.
- Successful completion.
- Processing failure.

The `processNext` method uses asynchronous execution and awaits a task handler.

This allows an application to integrate asynchronous work without blocking the entire event loop.

### State management

A `Map` records task completion and failure information.

A `Set` tracks active task identifiers.

The priority queue maintains its own sequence counter.

These structures separate scheduling state from execution state.

### Failure handling

Task execution errors are recorded and emitted through a failure event.

The failed task is not silently reinserted.

A production retry mechanism would require an explicit retry policy, attempt counter, and failure classification.

### Validation

The implementation rejects:

- Non-finite numeric heap values.
- Invalid heap modes.
- Missing task identifiers.
- Empty descriptions.
- Non-integer priorities.
- Duplicate active task identifiers.
- Invalid array indexes.

The implementation uses Node.js built-in modules and requires no npm dependencies.

## 9. C++17 Implementation

The C++ implementation emphasizes efficient data structures and explicit domain modeling.

The `BinaryHeap` class stores elements in `std::vector<int>`.

Its comparator behavior is controlled by `HeapMode`.

The implementation uses:

- `std::vector` for contiguous heap storage.
- `std::priority_queue` for task scheduling.
- `std::unordered_set` for active identifiers.
- `std::find` for value-based deletion.
- Exceptions for invalid operations.
- Assertions for correctness tests.

### STL priority queue

C++ `std::priority_queue` is a heap-based container adaptor.

Its default comparator produces maximum-priority behavior for ordinary numeric values.

The custom `TaskComparator` orders tasks by priority and sequence number.

This provides stable scheduling behavior.

The custom `BinaryHeap` remains useful when indexed deletion and priority updates are required, since `std::priority_queue` does not directly expose those operations.

## 10. Java 17 Implementation

The Java implementation emphasizes enterprise scheduling and policy evaluation.

Its domain model includes:

- `Task`
- `ScheduledTask`
- `TaskStatus`
- `HeapMode`
- `BinaryHeap`
- `PriorityScheduler`
- `TaskExecutionPolicy`

Java records provide immutable task and scheduling-entry representations.

The generic heap uses a supplied comparator and supports both min-heap and max-heap behavior.

### Enterprise task states

The task lifecycle is:

    QUEUED
       |
       v
    PROCESSING
       |
       +------> COMPLETED
       |
       +------> FAILED

The scheduler applies a task execution policy before completing processing.

A denied operation moves to `FAILED` and raises a security exception.

The `finally` block ensures that the active identifier is released even when policy evaluation fails.

This implementation demonstrates separation between:

- Scheduling priority.
- Task identity.
- Execution state.
- Execution authorization.

The policy interface allows different authorization rules to be supplied without changing the heap implementation.

The demonstration uses an in-memory policy and does not represent a complete authentication or authorization service.

## 11. PostgreSQL Relational Implementation

The PostgreSQL script models heap storage and priority scheduling using relational structures.

### Database entities

| Table | Purpose |
|---|---|
| `heaps` | Stores heap identity and operating mode |
| `heap_nodes` | Stores indexed heap elements |
| `scheduled_tasks` | Stores queued and processed tasks |
| `task_execution_history` | Records task state changes |

The `heap_nodes` primary key combines `heap_id` and `position`.

This permits multiple independent heaps without position collisions.

### Parent-child relationships

The parent of position `i` is:

`(i - 1) / 2`

The left child is:

`2 * i + 1`

The right child is:

`2 * i + 2`

PostgreSQL integer division produces the required parent index for non-negative positions.

### SQL heap operations

The script provides:

- `create_heap`
- `heap_insert`
- `heap_sift_up`
- `heap_sift_down`
- `heap_extract`
- `heap_delete_at`
- `heap_build`
- `validate_heap`

The functions use row locking on the heap metadata record to serialize cooperating operations against the same heap.

The heap representation is deliberately normalized into individual node records.

This provides relational inspection and integrity enforcement but has greater overhead than an in-memory array.

The database implementation is educational rather than a replacement for a specialized in-memory priority queue.

### Transactional task processing

The `process_next_task` procedure selects the highest-priority queued task.

It orders by:

1. Priority descending.
2. Sequence number ascending.

`FOR UPDATE SKIP LOCKED` allows concurrent workers to skip tasks already locked by other transactions.

The task is moved through `PROCESSING` to `COMPLETED` within the procedure's transaction.

A real distributed worker system would generally separate claiming and execution into separate transactions. This avoids holding database locks during lengthy external work.

### Audit trigger

The `trg_task_status_audit` trigger records task creation and status changes.

The history table provides an operational record of transitions.

### Indexing

The partial queue index:

`(priority DESC, sequence_number ASC) WHERE status = 'QUEUED'`

supports the common priority-selection query.

The status index supports filtering and reporting.

The heap-node value index supports value-oriented retrieval, although arbitrary deletion still requires identifying the appropriate array position.

## 12. Complexity Analysis

Let `n` represent the number of heap elements.

| Operation | Time Complexity |
|---|---:|
| Access root | `O(1)` |
| Insert | `O(log n)` |
| Extract minimum | `O(log n)` |
| Extract maximum | `O(log n)` |
| Sift-up | `O(log n)` |
| Sift-down | `O(log n)` |
| Bottom-up heapify | `O(n)` |
| Indexed deletion | `O(log n)` |
| Indexed update | `O(log n)` |
| Value search | `O(n)` |
| Value-based deletion | `O(n)` |
| Heap sort | `O(n log n)` |
| Priority queue peek | `O(1)` |
| Priority queue insertion | `O(log n)` |
| Priority queue extraction | `O(log n)` |

The array representation requires `O(n)` storage.

Heap operations have logarithmic movement because the height of a complete binary tree is logarithmic in its number of nodes.

## 13. Validation and Edge Cases

The implementations address the following conditions:

| Condition | Expected behavior |
|---|---|
| Empty heap extraction | Raise an exception |
| Empty heap peek | Raise an exception |
| Invalid index | Reject the operation |
| Duplicate active task ID | Reject submission |
| Missing task value | Return an unsuccessful deletion result |
| Single-element extraction | Empty the heap correctly |
| Duplicate numeric values | Preserve valid ordering |
| Negative numeric values | Support normal heap ordering |
| Equal task priorities | Use FIFO sequence ordering |
| Invalid priority | Reject submission |
| Failed task execution | Record failure |
| Invalid heap mode | Reject construction |

A heap invariant must be checked after structural modifications, particularly during development and testing.

## 14. Security and Production Considerations

Heap operations themselves do not provide security controls.

Priority scheduling introduces additional concerns.

### Priority manipulation

Unrestricted priority assignment can allow low-trust users to submit excessively high-priority tasks.

A production system should validate priority against an authorized range and enforce role-based submission policies.

### Starvation

A continuous stream of high-priority tasks can prevent low-priority tasks from executing.

Possible controls include:

- Priority aging.
- Weighted scheduling.
- Per-tenant quotas.
- Maximum waiting-time policies.

These mechanisms are intentionally separate from the basic binary heap.

### Concurrency

An in-memory heap generally requires synchronization when accessed by multiple threads.

The supplied Python and C++ examples are single-threaded.

The JavaScript implementation uses the event loop and does not establish cross-process coordination.

The PostgreSQL example uses transactional row locking.

A distributed scheduler requires additional controls for worker ownership, retries, leases, and idempotent task execution.

### Memory and operational limits

An unrestricted task queue can consume excessive memory.

Production systems should impose:

- Maximum queue size.
- Submission rate limits.
- Bounded task descriptions.
- Task expiration.
- Retention policies.
- Monitoring of queue depth and waiting time.

### Retry behavior

A failed task should not automatically be treated as a successful extraction.

A production retry design should distinguish transient failures from permanent failures and track attempts independently of priority.

## 15. Implementation Differences

| Feature | Python | JavaScript | C++17 | Java 17 | PostgreSQL |
|---|---|---|---|---|---|
| Custom binary heap | Yes | Yes | Yes | Yes | Yes |
| Min-heap | Yes | Yes | Yes | Yes | Yes |
| Max-heap | Yes | Yes | Yes | Yes | Yes |
| Heapify | Yes | Yes | Yes | Yes | Yes |
| Indexed deletion | Yes | Yes | Yes | Yes | Yes |
| Priority updates | Yes | Yes | Yes | Yes | Structural operations |
| Stable task ordering | Yes | Yes | Yes | Yes | Yes |
| Event-driven processing | No | Yes | No | No | Trigger and procedure |
| Async execution | No | Yes | No | No | Transactional procedure |
| Policy evaluation | No | No | No | Yes | No |
| Execution audit | No | In-memory | No | In-memory | Persistent |

The implementations share heap invariants but use different language capabilities and execution models.

## 16. Practical Application

Binary heaps are useful when an application repeatedly needs the smallest or largest item without maintaining a fully sorted collection.

Typical applications include:

- Operating system scheduling.
- Network packet prioritization.
- Incident management.
- Event simulation.
- Graph algorithms.
- Job processing.
- Resource allocation.
- Deadline management.
- Streaming data processing.

For an incident-management queue, the heap provides efficient priority selection. The surrounding application must still enforce authorization, starvation prevention, task ownership, retry behavior, and execution auditing.

The distinction between a heap and a complete scheduling system is important: the heap determines ordering, while the scheduler governs task lifecycle and operational policy.
