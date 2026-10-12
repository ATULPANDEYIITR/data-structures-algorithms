# Queue Introduction

## Scope

A queue is a linear data structure that processes elements according to **FIFO**, meaning **First In, First Out**. The first element inserted becomes the first element eligible for removal.

This implementation set treats queue behavior as a data-structure problem rather than as a generic collection exercise. The examples progress from direct FIFO behavior to circular array storage, linked-node storage, domain validation, asynchronous processing, and relational queue management.

The central distinction is between **queue behavior** and **queue implementation**:

- FIFO is the behavioral rule.
- An array, circular array, linked list, or language-provided deque is an implementation mechanism.
- The implementation determines memory usage, operation cost, capacity behavior, and failure conditions.
- Application code can expose queue operations through a domain service without exposing the underlying representation.

## FIFO Behavior

For a queue containing `A`, `B`, and `C` in insertion order, the logical state is:

`front -> A -> B -> C <- rear`

A dequeue removes `A`, leaving:

`front -> B -> C <- rear`

A new element `D` enters at the rear:

`front -> B -> C -> D <- rear`

The queue therefore differs from a stack. A stack follows LIFO, while a queue follows FIFO.

Queue operations normally have these meanings:

| Operation | Meaning |
|---|---|
| `enqueue` | Add an element at the rear |
| `dequeue` | Remove the element at the front |
| `peek` | Inspect the front without removing it |
| `isEmpty` | Determine whether the queue contains elements |
| `size` | Determine the number of stored elements |

The most important invariant is that an element cannot bypass an earlier element simply because it was inserted later.

## Python Implementation

The Python program begins with a direct list representation to expose the basic FIFO rule. `append()` adds elements at the end, while `pop(0)` removes the first element. This is conceptually simple but has an important performance limitation: removing index zero from a normal Python list can require shifting the remaining elements.

The program then uses `collections.deque`, which is designed for efficient insertion and removal at both ends. `append()` adds at the rear and `popleft()` removes from the front, making it a natural production-oriented queue implementation.

The `ArrayQueue` class demonstrates the data structure without relying on `deque`. It uses a fixed-size list together with:

- `_front` to identify the logical first element.
- `_rear` to identify the next physical insertion position.
- `_size` to distinguish empty, partially filled, and full states.
- Modular arithmetic to wrap positions back to the beginning of the array.

The circular representation is important because a simple array queue can waste positions after repeated dequeues if it does not reuse the freed storage.

The `LinkedQueue` class uses nodes containing a value and a reference to the next node. Both front and rear references are maintained. When the queue is empty, the first inserted node becomes both front and rear. When the final node is removed, both references must be cleared.

The support-ticket model adds domain validation. Ticket identifiers must be unique, empty identifiers are rejected, and an attempt to process an empty queue produces an explicit exception.

The Python implementation also checks queue invariants after wrap-around operations. This is important because circular queues can appear correct during simple enqueue/dequeue sequences while still containing pointer-management errors.

## JavaScript Implementation

The JavaScript program uses three different perspectives.

The initial array example exposes FIFO behavior with `push()` and `shift()`. This is useful for understanding the operation itself, but repeated `shift()` calls are not an ideal representation for a large high-throughput queue because array elements may need to be relocated.

`CircularQueue` provides an explicit fixed-capacity implementation. Its `front`, `rear`, and `size` properties represent the logical state independently of the physical array positions. The expression `(index + 1) % capacity` creates the circular movement.

The linked implementation uses `QueueNode` objects with a `next` reference. JavaScript's object references make the linked structure direct to model, while the implementation still has to maintain the special empty-state rule where both `front` and `rear` become `null`.

The `TicketQueue` implementation adds an event-driven layer. It maintains listeners for events such as `submitted` and `processed`. The queue determines processing order, while event handlers provide application behavior around those state changes. This separates the data-structure operation from notification logic.

The asynchronous example demonstrates a producer and consumer operating through a queue. The producer creates items at different times, while the consumer waits for work when the queue is temporarily empty. This shows why queue behavior becomes important in event-driven systems where production and consumption do not necessarily occur at the same rate.

## C++ Case Study

The C++ program models a repository build scheduler. A build job represents work waiting for a build worker:

`BuildJob -> Pull Request -> source branch -> build status`

The scheduler uses a circular queue for bounded build capacity. A fixed capacity is useful in this scenario because an infrastructure component may intentionally limit the number of pending jobs rather than allocating unlimited memory.

The `CircularQueue<T>` class uses `std::vector<std::optional<T>>`. `std::optional` makes an unused array position distinguishable from a stored value without requiring a special sentinel value.

The queue maintains these invariants:

- `size == 0` means the queue is empty.
- `size == capacity` means the queue is full.
- `front` identifies the oldest logical element.
- `rear` identifies the next insertion location.
- Both positions wrap using modular arithmetic.

The linked implementation uses `std::unique_ptr` for node ownership. This avoids manually managing `delete` operations and makes node lifetime follow the linked structure.

The build scheduler adds domain behavior on top of the queue. Every submitted job requires a non-empty identifier, Pull Request reference, and source branch. A set prevents duplicate active job identifiers.

The build callback changes a job from queued to running and then determines whether it passed or failed. The queue itself does not decide whether a build is successful. This separation is an important design decision: the queue controls ordering, while the build operation controls job outcome.

The C++ program therefore demonstrates that a queue is not limited to primitive values. A queue can contain domain objects while preserving the same FIFO invariant.

## Java Enterprise Model

The Java program models deployment requests moving through an enterprise deployment workflow.

A `DeploymentRequest` is represented as an immutable record containing:

- deployment identifier,
- service,
- environment,
- requester,
- lifecycle state.

The `DeploymentState` enum makes valid lifecycle states explicit:

`QUEUED -> RUNNING -> SUCCEEDED`

or:

`QUEUED -> RUNNING -> FAILED`

The queue itself uses a `Deque<DeploymentRequest>`, which exposes the appropriate FIFO operations through `addLast()` and `pollFirst()`.

The `DeploymentQueue` class owns active identifiers in a `Set`. This prevents two active requests from using the same deployment identifier. The collection therefore represents both ordering and domain-level uniqueness.

A separate `DeploymentPolicy` abstraction determines whether a deployment can proceed. The queue decides which request is next; the policy decides whether that request is eligible. These are different responsibilities and should not be merged into the data structure.

The example policy rejects production deployment requests. The purpose is to demonstrate architectural separation rather than to establish a universal deployment rule.

The Java implementation also demonstrates validation at object construction time. Invalid deployment identifiers, services, environments, requesters, and states are rejected before the object enters the queue.

## SQL Data Model

The PostgreSQL implementation represents queues and requests relationally.

The `service_queue` table defines named queues and their capacities.

The `service_request` table contains the individual queued items. Its `arrival_sequence` is essential because relational tables do not inherently guarantee an application-level FIFO ordering. Queries must explicitly define the order used to determine which request is oldest.

The relationship is:

`service_queue 1 -> many service_request`

The foreign key ensures that a request cannot reference a nonexistent queue.

The unique constraint on `(queue_id, arrival_sequence)` prevents two requests in the same queue from claiming the same arrival position.

The status check constraint restricts request states to:

`QUEUED`, `PROCESSING`, `COMPLETED`, and `FAILED`.

The partial unique index on processing requests enforces a single active worker position per queue for this particular model. It is intentionally stricter than a distributed worker system would normally require, because the example models a simple single-processing-slot queue.

## SQL FIFO Retrieval

The fundamental relational FIFO query is ordered by `arrival_sequence`:

`ORDER BY arrival_sequence LIMIT 1`

Without the explicit ordering, the database is free to return rows in an unspecified order.

The `queued_request_fifo_index` is a partial index restricted to queued requests. This allows the database to maintain an access path specifically for the operation that finds the next waiting request.

The SQL script also uses `ROW_NUMBER()` to expose the current logical queue position. This is useful when the application needs to display position information without storing a mutable position number.

A stored position is generally less desirable because every dequeue would require updating many remaining rows. The immutable arrival sequence plus a window calculation avoids that unnecessary update workload.

## Transactional Dequeue

The SQL script demonstrates transactional selection using `FOR UPDATE SKIP LOCKED`.

`FOR UPDATE` locks the selected row during the transaction. This prevents another transaction from modifying the same row while the worker is claiming it.

`SKIP LOCKED` is useful when multiple workers compete for work. Instead of waiting on a row already claimed by another worker, a worker can skip locked rows and look for another available request.

The transaction changes the request from `QUEUED` to `PROCESSING`. The state transition and row selection therefore occur as part of one database operation.

This is substantially different from an in-memory queue. An in-memory queue provides ordering within one running process, while the database can provide durable state and transactional coordination between independent processes.

## Array Queue and Linked Queue

The two primary custom implementations have different physical characteristics.

| Characteristic | Circular Array | Linked List |
|---|---|---|
| Storage | Contiguous array | Separate nodes |
| Enqueue | O(1) | O(1) with rear reference |
| Dequeue | O(1) | O(1) with front reference |
| Capacity | Usually bounded | Grows until memory is exhausted |
| Memory locality | Strong | Weaker |
| Allocation overhead | Low after allocation | Node allocation per element |
| Wrap-around | Required | Not required |
| Full condition | Explicit | Usually memory-dependent |

A circular array is often attractive when a predictable maximum capacity is known. A linked queue is useful when dynamic growth is more important than contiguous storage.

The key requirement for a linked queue is maintaining both endpoints. If only the front pointer is retained, enqueue would require traversing the entire list to find the rear, turning enqueue into an O(n) operation.

## Complexity

For a correctly implemented circular array queue:

- `enqueue` is O(1).
- `dequeue` is O(1).
- `peek` is O(1).
- `isEmpty` is O(1).
- `isFull` is O(1).

For a linked queue with front and rear references:

- `enqueue` is O(1).
- `dequeue` is O(1).
- `peek` is O(1).
- `isEmpty` is O(1).

The important contrast is not between FIFO and performance. FIFO describes ordering. Performance depends on the underlying representation and implementation strategy.

## Edge Cases

An empty queue must reject `dequeue` and normally reject `peek` because there is no front element.

A fixed-capacity queue must reject an enqueue when no storage remains. Silently overwriting the oldest item would violate ordinary FIFO queue semantics unless the data structure is explicitly defined as a circular buffer with overwrite behavior.

A queue containing exactly one element is a critical boundary case. After dequeue, both front and rear must represent the empty state.

Circular queues require careful handling when the rear index wraps from the final physical position back to index zero. Logical order must remain independent of physical position.

Duplicate domain identifiers are separate from queue ordering. The queue can contain two equal values in a pure data-structure implementation, but an application such as ticket processing may impose uniqueness rules.

## Common Implementation Errors

Using a normal array and repeatedly removing index zero is a common beginner implementation because it directly expresses FIFO behavior. The problem is that repeated front removal can become expensive as the queue grows.

Another error is confusing an empty circular queue with a full circular queue when only front and rear indexes are stored. Maintaining an explicit `size` value is one straightforward way to distinguish those states.

A linked queue can also fail when its rear reference is not cleared after the last node is removed. The next enqueue may then attach to an obsolete node instead of treating the queue as empty.

Queue code should also avoid mixing ordering responsibility with unrelated business decisions. A queue should determine which element is next. A separate policy or service can determine whether that element is eligible for processing.

## Practical Interpretation

A queue is appropriate whenever work should normally be handled in arrival order.

Examples represented by the implementations include service requests, support tickets, build jobs, deployment requests, and asynchronous producer-consumer workloads. The domain changes, but the underlying FIFO mechanism remains the same.

The implementation choice depends on the system's constraints. A small application can use a standard library deque. A teaching implementation can expose the internal array or node structure. A bounded infrastructure component can use a circular buffer. A database-backed worker system can represent queue state relationally and coordinate consumers through transactions.

The central engineering principle is to preserve the FIFO invariant while choosing a representation whose capacity, memory behavior, concurrency model, persistence requirements, and failure handling match the actual workload.
