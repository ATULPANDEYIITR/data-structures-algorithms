# Priority Queues: Heap Algorithms, Scheduling, and Priority-Based Processing

## Scope

A priority queue stores pending items and selects the item with the highest precedence according to a defined ordering rule. It differs from a conventional first-in, first-out queue because insertion order does not necessarily determine removal order.

This project examines priority queues through four related areas:

- **Heap data structures:** maintaining an ordering invariant that permits efficient access to the next item.
- **Scheduling:** choosing which job, request, event, or task should execute next.
- **Priority policies:** translating urgency, severity, deadlines, and fairness requirements into a consistent ordering.
- **Operational processing:** handling cancellation, reprioritization, worker limits, concurrent consumers, and failures.

The implementations use different perspectives. Python focuses on heap operations and updateable scheduling. JavaScript develops a binary heap and asynchronous event-driven processing. C++ models a bounded build-farm scheduler. Java implements an enterprise service-desk escalation workflow. PostgreSQL represents durable job state, dispatch ordering, and concurrent job claiming.

## Heap fundamentals

A binary heap is a complete binary tree represented efficiently by an array. It does not require every element to be sorted.

For a zero-based array, the children of an element at index \(i\) occupy positions \(2i+1\) and \(2i+2\). Its parent, when one exists, occupies position \(\lfloor(i-1)/2\rfloor\).

In a min-heap, each parent is no greater than either child. In a max-heap, each parent is no smaller than either child. The root therefore identifies the minimum or maximum element without searching the entire collection.

A heap guarantees the root's ordering relationship with its descendants, not complete array sorting. Elements deeper in the heap may appear in an order that would be invalid in a sorted array.

### Complexity

| Operation | Binary heap | Explanation |
|---|---:|---|
| Inspect the highest-priority item | \(O(1)\) | The root contains the next candidate. |
| Insert an item | \(O(\log n)\) | The new element may move through the tree. |
| Remove the root | \(O(\log n)\) | The last element replaces the root and moves downward. |
| Build a heap from an array | \(O(n)\) | Bottom-up heap construction is linear. |
| Search for an arbitrary item | \(O(n)\) | Heap order does not support ordinary binary search. |
| Sort by repeated removal | \(O(n\log n)\) | Each of the \(n\) removals costs logarithmic time. |

These bounds assume a binary heap and constant-time comparisons. Expensive comparison functions or costly payload operations can change practical performance.

## Priority ordering and stable scheduling

A scheduler must define exactly what "highest priority" means.

This project uses higher numeric values for more urgent jobs, with a score ranging from 0 to 100. A score of 100 precedes a score of 50. When priorities are equal, insertion order determines precedence.

A useful ordering key is therefore:

\[
(-p,\ s)
\]

where \(p\) is the numeric priority and \(s\) is a monotonically increasing insertion sequence. A min-heap can use the negative priority to implement maximum-priority behavior.

The sequence number makes the ordering stable. Without a tie-breaker, equal-priority jobs might execute in an unexpected order. In tuple-based implementations, the tie-breaker also prevents a runtime from trying to compare payload objects that do not support ordering.

Stable ordering does not imply fairness across different priority levels. A continuous stream of urgent jobs can keep lower-priority work waiting indefinitely.

## Python implementation

The Python script uses `heapq`, which provides heap operations over ordinary lists. It does not introduce a separate heap container class.

The fundamentals demonstration contrasts minimum-priority and maximum-priority removal. The scheduling implementation then builds a higher-level `PriorityTaskQueue` around `heapq`.

### Reprioritization and lazy deletion

A standard heap does not efficiently locate an arbitrary item. Modifying a queued item's priority in place is unsafe because the heap may no longer satisfy its ordering invariant.

The Python queue instead maintains two structures:

- A heap of priority entries, version values, identifiers, and task objects.
- A dictionary mapping each live task identifier to its current version and task.

Reprioritization creates a replacement entry. The old entry remains physically present in the heap but no longer matches the authoritative dictionary entry. Removal discards such stale entries until it finds a current task.

Cancellation removes the task from the live dictionary. Its former heap entry becomes stale and is ignored later.

This strategy makes updates straightforward, but repeated changes can increase heap size beyond the number of active tasks. The `compact()` method rebuilds the heap from live dictionary entries when reclamation is needed.

The queue also validates task identifiers, priority ranges, estimated durations, and capacity. A duplicate identifier is rejected rather than silently replacing an existing task.

### Event simulation

The event simulation schedules events by timestamp and sequence number. It models systems in which the earliest scheduled event must execute next, such as retry timers and health checks.

Its ordering policy is different from the job scheduler's urgency policy. A timestamp-based event queue prioritizes earlier event times; a task scheduler prioritizes larger urgency scores.

The distinction matters because a priority queue is a data structure, not a complete scheduling policy. The comparison key determines what the queue actually means.

### Top-k operations

The script uses `heapq.nlargest()` to select the three largest measurements and `heapq.merge()` to combine sorted partitions.

These operations demonstrate that heap utilities are useful beyond dispatching jobs. Top-k selection can avoid sorting a complete collection when only a small number of extreme values are needed. Merging sorted partitions is useful when data has already been ordered in separate streams.

### Tests and limitations

The automated tests check priority ordering, stable ties, reprioritization, cancellation, capacity, invalid values, and heap compaction.

The queue is not thread-safe. A multithreaded production scheduler would need synchronization around its heap and live-task dictionary, or a durable queue service designed for concurrent workers. It also needs an explicit retry policy, observability, persistence, and a starvation-control strategy.

## JavaScript implementation

The JavaScript file implements a generic `BinaryHeap` rather than depending on a third-party priority-queue package.

The comparator determines the ordering. The heap itself is responsible for preserving that ordering during insertion and removal. Its private sift-up and sift-down methods prevent callers from directly modifying the internal array.

The `assertInvariant()` method checks that no child ranks ahead of its parent. This is particularly useful when implementing a custom heap because a small error in an index calculation can produce incorrect scheduling results without immediately causing an exception.

### Event-driven scheduling

`JobScheduler` extends `EventTarget` and emits events when jobs are submitted, reprioritized, cancelled, started, and completed.

Listeners receive structured event details rather than parsing printed output. This makes the scheduler suitable for integration with monitoring panels or other event-driven application components.

The `runOne()` method uses a promise-based timer to simulate asynchronous work. It does not block the JavaScript event loop while the timer is pending.

The example processes jobs one at a time. A production worker pool could coordinate multiple concurrent `runOne()` calls, but it would need explicit worker limits, shutdown handling, cancellation of running operations, and protection against duplicate execution.

### Stale entries and state

The scheduler uses object identity to distinguish the authoritative queued job from obsolete entries left behind by reprioritization. A cancelled job is removed from the live map, making its heap entry ineligible for execution.

The scheduler checks job state before changing the queue. It rejects duplicate identifiers, invalid priorities, negative durations, and capacity overflow.

The included assertions cover ordering, duplicate submission, capacity limits, invalid reprioritization, and empty-queue behavior.

JavaScript's single-threaded event loop does not eliminate concurrency concerns. Asynchronous operations can overlap, and a distributed deployment may have several independent processes. A shared in-memory heap cannot coordinate those processes or provide durable job ownership.

## C++ case study: build-farm scheduling

The C++ program models a build farm that processes compilation, integration-test, security-scan, and deployment requests.

Security scans and production deployment work receive high urgency scores. Routine reports receive lower scores. A fixed worker limit controls how many jobs may be marked as running simultaneously.

### Architecture and data structures

The `BuildJob` structure contains a job identifier, repository, operation, priority, estimated duration, insertion sequence, and state.

The `BuildFarm` class combines:

- `std::priority_queue` for selecting the next dispatch candidate.
- `std::unordered_map` for authoritative job state and constant-average-time identifier lookup.
- A monotonically increasing sequence value for deterministic tie-breaking.
- A worker counter for enforcing the local dispatch limit.

The `JobOrder` comparator reverses the ordinary priority comparison because `std::priority_queue` normally places the element considered greatest at the top.

### Reprioritization and cancellation

The standard C++ priority queue does not expose efficient arbitrary-element updates or removal. The implementation updates the authoritative map and inserts a replacement heap entry.

When a candidate is removed, its sequence and state are compared with the authoritative job record. An obsolete candidate is discarded.

Cancellation marks the job as cancelled. It does not require searching the heap for the old entry.

These techniques keep the code simple, although repeated updates increase physical heap size. A workload with frequent priority changes may require periodic heap rebuilding or an indexed heap that tracks each item's current position.

### Worker limits and state transitions

`start_next()` refuses to dispatch more jobs when all workers are occupied. `finish()` accepts only jobs in the running state and releases a worker after completion or failure.

The state transitions prevent a cancelled job from being completed as though it had executed. Invalid priorities, negative estimated durations, empty identity fields, duplicate identifiers, and invalid completion requests are rejected.

The simulation does not execute actual builds or track real worker processes. Its worker counter models capacity in a single process. A production build farm would also need crash recovery, durable ownership, leases or heartbeats, retry backoff, and protection against two processes executing the same job.

## Java implementation: service-desk escalation

The Java program models an enterprise service desk that must route incidents and requests to the next available agent.

Severity and escalation are distinct inputs. A critical incident begins with a higher base score than a routine request, while escalation raises the effective score of a ticket that has remained queued or requires additional attention.

The effective score is:

\[
p_{\mathrm{effective}} =
\min(100,\ p_{\mathrm{severity}} + 10e)
\]

where \(e\) is the escalation level.

This is a deliberately simple policy model. Real service-desk policies might use contractual response deadlines, service criticality, customer impact, and elapsed waiting time instead.

### Domain model and state transitions

The `Severity` and `TicketState` enums restrict values to explicitly supported states. The `Ticket` class owns its identity and current severity, escalation level, and state. `TicketSnapshot` exposes a record containing a read-only representation of ticket data.

The scheduler stores tickets in a `HashMap` and orders `QueueEntry` records through a `PriorityQueue`. Each queue entry contains the priority calculated when it was inserted, plus a version and sequence.

Escalation or a severity change produces a replacement queue entry. The version map identifies the currently valid entry. When an outdated entry reaches the root, the scheduler discards it.

Assignment changes the ticket from `QUEUED` to `ASSIGNED`. Resolution is permitted only after assignment. Cancellation is permitted only while queued.

The separation between ticket state and queue-entry state is important. The heap determines which candidate should be selected, while the domain object determines whether that candidate is still eligible for processing.

### Fairness and operational concerns

Escalation approximates aging, but it does not guarantee freedom from starvation. A high-priority arrival stream can still delay low-severity requests, especially when escalation limits are reached.

The program exposes physical queue size so that stale-entry accumulation can be observed. `compactQueue()` reconstructs the queue from authoritative queued tickets.

In a larger enterprise application, the scheduler could be integrated with a database-backed ticket repository, assignment permissions, service-level objectives, and an audit log. The in-memory implementation does not claim to provide persistence or distributed locking.

## PostgreSQL implementation: durable scheduling state

The SQL script models scheduling as a relational workflow rather than an in-memory heap.

PostgreSQL's internal index structures are not an application-level priority queue. The database instead selects eligible jobs using an explicit ordering query and provides transactional row locking for safe concurrent claims.

### Relational model

The `workers` table stores worker identity and enabled status. The `jobs` table stores the job's repository, type, priority, timestamps, retry limits, current state, and optional worker assignment.

The `job_events` table records creation, reprioritization, and state changes. Its foreign key links every event to an existing job, while JSONB captures event-specific details without requiring a separate column for every kind of event.

The database enforces unique external identifiers, valid priority ranges, non-negative durations, valid retry limits, and state-dependent timestamp and worker requirements.

The partial index `jobs_dispatch_order_idx` supports queries for queued jobs ordered by priority, queue time, and identifier. It excludes non-queued jobs, reducing the index's relevance to unrelated terminal records. The repository-state index supports workload reporting, while the event index supports retrieving a job's most recent history.

### Dispatch order

The `queued_job_order` view calculates a row number using:

`ORDER BY priority DESC, queued_at ASC, job_id ASC`

The rank is calculated when the view is queried. It is not persisted because insertion, reprioritization, and state changes can change the order of all waiting jobs.

The top-three query demonstrates limited retrieval without requiring application code to load the entire queue. The workload aggregation groups counts by repository and reports the highest waiting priority.

### Atomic job claiming

The `claim_next_job` function selects an eligible queued job using `FOR UPDATE SKIP LOCKED`.

Row locking protects the selected record while the claim is performed. `SKIP LOCKED` allows concurrent workers to move past rows that another transaction has already locked rather than waiting for those rows.

After selecting a job, the function changes its state to `running`, records the worker and start time, and increments the attempt count. The state-change trigger records the transition in the event history.

The function runs inside the caller's transaction. The caller must commit the transaction to make the claim durable. If the transaction rolls back, its claim and corresponding event insertion roll back as well.

This mechanism supports concurrent claims, but it does not by itself provide a complete distributed job-processing system. Long-running work should not hold a database transaction open for its entire duration. Production workers typically claim jobs in short transactions, execute outside the transaction, and then record completion in a separate transaction.

### Integrity and failure behavior

The invalid-priority example attempts to insert a job with a priority of 101. The database rejects the value through the `CHECK` constraint.

The event trigger maintains a history of selected changes, while the event foreign key prevents orphaned history records. The trigger does not provide a cryptographically tamper-proof audit log, and sufficiently privileged database users can still alter stored records or disable database controls.

The schema also illustrates an important distinction between integrity and operational policy. A constraint can enforce a valid priority range, but deciding whether a deployment should outrank a security incident remains a scheduling-policy decision.

## Policy design, fairness, and scheduling trade-offs

Priority queues make selection efficient, but they do not determine the right priority policy.

### Starvation and aging

Starvation occurs when lower-priority work waits indefinitely because higher-priority work keeps arriving.

Aging increases a job's effective priority as it waits. A simple policy might raise priority by a fixed amount for each elapsed interval, subject to a maximum score.

An aging policy must be implemented carefully. If an item's effective priority changes while it remains inside a heap, the heap ordering can become invalid. A scheduler can address this by periodically rebuilding the heap, inserting updated versioned entries, or using a selection method that accounts for time directly.

### Deadlines and urgency

Priority scores alone cannot guarantee that a deadline will be met. A deadline-aware scheduler needs information about due times, estimated execution durations, available workers, and the consequences of missing deadlines.

A policy based on earliest deadline first differs from a fixed-severity policy. The former chooses by deadline, while the latter chooses by assigned urgency. A combined policy must specify how these dimensions interact instead of assuming they are interchangeable.

### Bounded queues and overload

A bounded queue protects memory and limits the amount of work admitted into a system. When capacity is reached, the system needs an explicit response: reject new work, apply backpressure, persist it elsewhere, or replace eligible lower-priority work under a carefully defined policy.

The in-memory implementations reject admission when their capacity is reached. They do not silently evict a previously accepted job.

### Retry handling

A failed job should not automatically be placed back at the same priority without considering the cause of failure. Repeated immediate retries can overload a failing dependency.

A production retry policy should define maximum attempts, retryable failure categories, exponential backoff, jitter, and terminal failure behavior. Delayed retries can be represented by a time-based event queue while the primary dispatch queue orders work that is currently eligible.

### Concurrency and durability

An in-memory heap provides efficient selection inside one process. It does not coordinate separate application instances, survive a process crash, or guarantee exactly-once execution.

Distributed systems generally need durable job state, atomic claiming, ownership leases or equivalent recovery mechanisms, idempotent handlers, and explicit failure recovery. A database transaction can make state changes atomic, but external work may still be repeated if a worker crashes after performing an operation and before recording success.

## Implementation comparison

| Implementation | Primary mechanism | Distinctive concern |
|---|---|---|
| Python | `heapq` and a live-entry dictionary | Lazy deletion, compaction, and unit tests for queue invariants. |
| JavaScript | Custom binary heap and `EventTarget` | Event-driven lifecycle handling and asynchronous work. |
| C++ | `std::priority_queue` and an authoritative job map | Worker capacity and explicit state transitions. |
| Java | Typed ticket domain model and versioned queue entries | Severity escalation, assignment rules, and domain validation. |
| PostgreSQL | Ordered queries, partial indexes, and row locks | Durable state, audit history, and concurrent job claiming. |

These implementations share the concept of selecting the next eligible item, but their operational guarantees differ. An in-memory heap optimizes local selection. A database-backed queue coordinates persistent state. A complete scheduling service must combine the appropriate data structure with explicit priority rules, state validation, fairness, failure recovery, and concurrency controls.
