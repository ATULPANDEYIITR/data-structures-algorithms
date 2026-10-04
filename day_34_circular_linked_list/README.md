# Circular Linked Lists

Circular linked lists extend the ordinary linked-list model by removing the terminal `null` link. The final node points back to the first node, creating a cycle.

Two important forms are covered here:

- **Circular singly linked list:** each node has one `next` reference. The tail points to the head through `tail.next`.
- **Circular doubly linked list:** each node has both `next` and `prev` references. The tail points forward to the head, while the head points backward to the tail.

The central implementation challenge is that traversal cannot rely on reaching `null`. A correct traversal must stop after returning to the starting node or after visiting the known number of nodes.

The three implementations approach the subject from different perspectives. The Python program is a broad executable learning model, the JavaScript program emphasizes object references and asynchronous event-driven behavior, and the C++ program develops a memory-managed route-management case study.

## Core Structure

### Circular singly linked lists

A circular singly linked list can be represented efficiently with a `tail` pointer.

For the logical sequence:

`A -> B -> C`

the physical relationship is:

`tail = C`

and:

`C.next = A`

The structure therefore forms:

`A -> B -> C -> A`

There is no `null` after `C`.

This representation has an important advantage. With a tail pointer, the head is available as `tail.next`. Appending a node does not require walking from the head to the final node because the final node is already known.

Appending `D` changes the relevant links from:

`C -> A`

to:

`C -> D -> A`

and then makes `D` the new tail.

Prepending is also efficient. A new node can be inserted between the tail and the current head:

`C -> A`

becomes:

`C -> D -> A`

while `C` remains the tail.

The Python and JavaScript implementations use this tail-based representation.

### Circular doubly linked lists

A circular doubly linked list gives every node two references:

- `next`, which points to the next node
- `prev`, which points to the previous node

For:

`A <-> B <-> C`

the circular invariants are:

`A.prev = C`

`C.next = A`

and the internal links satisfy:

`A.next.prev = A`

`A.prev.next = A`

This makes deletion particularly useful. If a node is already known, its predecessor and successor are available directly, so it can be removed without searching for its predecessor.

The cost is additional memory and additional pointer maintenance. Every insertion and deletion must keep both directions consistent.

## Traversal

Traversal is one of the most important differences between ordinary and circular linked lists.

A conventional singly linked list can use a loop such as `while current is not None`. That logic is incorrect for a circular list because the structure intentionally contains no terminal `None` link.

A circular traversal must use a bounded condition.

The implementations use the list's stored size and visit exactly that many nodes. This gives a deterministic traversal even when values are duplicated.

Another valid strategy is to save the starting node and stop when traversal returns to that node.

For a list containing `A`, `B`, and `C`, one complete traversal is:

`A -> B -> C -> A`

The second occurrence of `A` is the signal that the cycle has been completed.

A size-bounded traversal is especially useful when the implementation maintains an explicit node count because it also protects against accidental infinite loops if a structural invariant becomes corrupted.

## Circular Singly Linked List Operations

The Python `CircularSinglyLinkedList` and JavaScript `CircularSinglyLinkedList` maintain a tail reference and a size counter.

### Append

Appending a value creates a new node and inserts it between the old tail and the head.

With:

`A -> B -> A`

where `B` is the tail, appending `C` produces:

`A -> B -> C -> A`

The operation is `O(1)` when a tail pointer is maintained.

### Prepend

Prepending does not require moving every existing node.

For:

`A -> B -> A`

the new node `X` is linked between `B` and `A`:

`X -> A -> B -> X`

The tail remains `B`, while `tail.next` becomes `X`.

This is also `O(1)`.

### Insert after a known value

Insertion after a value requires finding the target first. Searching is `O(n)`, while the actual link insertion is `O(1)`.

If the target is the tail, the new node becomes the new tail.

This distinction matters when analyzing performance. The pointer operation itself is constant-time, but locating the target can dominate the total operation.

### Deletion

Deleting from a singly linked list requires access to the node immediately before the target because that predecessor must skip over the deleted node.

For:

`A -> B -> C -> A`

deleting `B` requires changing:

`A.next = C`

If the deleted node is the tail, the predecessor must also become the new tail.

Deleting the only node is a special case. Its self-reference must be removed and the tail must become empty.

## Circular Doubly Linked List Operations

The circular doubly linked implementation maintains a head node. The tail is obtained from `head.prev`.

For:

`A <-> B <-> C`

the boundary relationships are:

`A.prev = C`

`C.next = A`

### Insertion

To insert `X` after `B`:

Before:

`B <-> C`

After:

`B <-> X <-> C`

Four relationships must be coordinated:

- `X.prev = B`
- `X.next = C`
- `B.next = X`
- `C.prev = X`

Failing to update any one of these relationships corrupts the bidirectional structure.

### Deletion

To remove `B`:

Before:

`A <-> B <-> C`

After:

`A <-> C`

The implementation rewires:

`A.next = C`

and:

`C.prev = A`

The deleted node's own links are then cleared in the JavaScript implementation and released in the C++ implementation.

When the deleted node is the head, the successor becomes the new head.

When the list contains only one node, deletion transitions the structure from a self-referencing node to an empty list.

## Python Implementation

The Python implementation provides two reusable generic data structures:

`CircularSinglyLinkedList[T]` stores a tail node and supports append, prepend, insertion after a value, positional insertion, deletion, search, rotation, traversal, and invariant validation.

`CircularDoublyLinkedList[T]` stores a head node and maintains the bidirectional circular relationships. It supports forward and backward traversal, insertion, deletion, positional lookup, and invariant validation.

Python's `dataclass` is used for node records so the pointer structure remains explicit without unnecessary boilerplate.

The Python program also contains a `RoundRobinScheduler`. It uses the circular singly linked list to represent runnable processes. Each process receives a time quantum. An unfinished process remains in the cycle, while a completed process is removed.

This is a direct use of circular-list behavior rather than an unrelated demonstration. The scheduler repeatedly advances around a cycle until every process has completed.

The `validate_structure` methods are particularly important. They test the invariants that make circular lists different from ordinary linked lists. The checks detect broken links, inconsistent size values, missing circular references, and cycles that do not return to their expected starting point.

## JavaScript Implementation

The JavaScript implementation models nodes as ordinary objects with mutable references.

`CircularSinglyLinkedList` uses `tail` and `tail.next` to represent the boundary between the final node and the first node.

`CircularDoublyLinkedList` uses `headNode` and derives the tail through `headNode.prev`. This makes both directions available without a separate tail field.

The JavaScript implementation also demonstrates an asynchronous round-robin scheduler. The scheduler uses `async` and `await` while preserving the circular data structure itself.

The asynchronous boundary is intentionally separated from the linked-list mechanics. JavaScript's event-driven execution model can suspend between scheduling events, but the circular invariants remain the same.

The scheduler uses objects containing a job name and remaining duration. A job that has not completed causes the list to rotate. A completed job is removed from the cycle.

The implementation validates argument types and numeric constraints with `TypeError` and `RangeError`. This is important in JavaScript because the language does not enforce the intended node payload types statically at runtime.

## C++ Case Study

The C++ implementation models a transport control system.

A `ShuttleRoute` contains stations arranged on a circular route. A station can be added, inserted after another station, removed, traversed forward, or traversed in reverse.

The route is implemented using `CircularDoublyList<Station>` because the domain requires movement in both directions.

Each station contains a code and passenger capacity. Validation rejects empty codes, non-positive capacities, and duplicate station codes.

The route initially contains:

`A -> B -> C -> D -> A`

A station can be inserted between existing stations. Removing `C`, for example, changes the route to:

`A -> B -> D -> A`

The reverse traversal demonstrates the practical value of the doubly linked structure:

`D -> B -> A -> D`

The C++ program also contains a separate `CircularSinglyList` implementation. It models a service queue in which the next service is the only relationship needed. The `rotate()` operation changes the logical starting point without moving any nodes.

This distinction demonstrates an important design choice: a doubly linked list should not be selected merely because it is more capable. If backward navigation is unnecessary, the singly linked representation consumes less per-node memory and has fewer links to maintain.

## Circular Invariants

Correctness depends on maintaining structural invariants.

For a circular singly linked list with a non-empty structure:

`tail != null`

and:

`tail.next == head`

Following `next` exactly `size` times from the head must return to the head.

For a circular doubly linked list:

`head.prev == tail`

and:

`tail.next == head`

For every node:

`node.next.prev == node`

and:

`node.prev.next == node`

These relationships are stronger than simply checking whether traversal appears to produce the expected values. A list can contain the correct values while still having an incorrect reverse link.

The validation routines therefore check both connectivity and direction.

## Empty and Single-Node States

Empty and single-node lists deserve explicit handling.

An empty circular list has no node and therefore no cycle.

A one-node circular singly list has:

`node.next == node`

A one-node circular doubly list has:

`node.next == node`

and:

`node.prev == node`

This self-reference is not an error. It is the correct representation of a cycle containing exactly one element.

Deletion must recognize this state. Removing the only node changes the structure to an empty list rather than attempting to connect a predecessor and successor that do not exist.

## Rotation

Rotation is particularly natural for circular lists.

Suppose the logical order is:

`A -> B -> C -> D`

Moving the logical head forward produces:

`B -> C -> D -> A`

No node needs to be physically moved.

In a tail-based circular singly list, changing the tail reference changes which node is considered the head because the head is always `tail.next`.

This property is useful for round-robin schedulers, cyclic buffers, repeating service queues, token-passing models, and systems that repeatedly advance through a fixed set of active participants.

## Complexity

| Operation | Circular Singly | Circular Doubly |
|---|---:|---:|
| Access by position | O(n) | O(n) |
| Search by value | O(n) | O(n) |
| Append with boundary pointer | O(1) | O(1) |
| Prepend | O(1) | O(1) |
| Insert after known node | O(1) | O(1) |
| Delete known node | Requires predecessor | O(1) |
| Delete by value | O(n) | O(n) |
| Complete traversal | O(n) | O(n) |
| Rotation | O(1) | O(1) |

The doubly linked structure does not make searching faster. Its main advantage is that once a node has been identified, the predecessor is directly available.

The additional `prev` reference increases memory usage and creates additional invariants that must be preserved.

## Common Implementation Errors

### Using a null-termination loop

A loop based on `current != null` can run indefinitely because the final node points back into the list.

The traversal must instead use a node count, a saved starting node, or another explicit termination condition.

### Forgetting the one-node case

Deleting the only node is structurally different from deleting a node from a multi-node cycle. The list must transition to an empty state.

### Breaking the tail relationship

In a tail-based singly linked list, `tail.next` must always identify the head. Updating a node's `next` pointer without updating `tail` when necessary can make the logical tail incorrect.

### Updating only one direction

A circular doubly linked list requires both forward and backward links to agree. Updating `A.next` without updating the corresponding `next.prev` relationship creates a corrupted structure.

### Traversing an already-corrupted list without a bound

A broken cycle can cause an application to hang. Keeping a size counter and bounding traversal provides a defensive mechanism that can expose corruption instead of silently looping forever.

### Confusing physical order with logical head

Rotation does not require moving nodes. The same cycle can have different logical starting points depending on which node is designated as the head or tail boundary.

## Practical Applications

Circular linked lists are appropriate when the domain itself is cyclic.

A round-robin scheduler repeatedly returns to earlier participants after reaching the end of the active set.

A multiplayer turn system can advance from one participant to the next without special end-of-list handling.

A circular route can represent a transit system where the final stop connects directly back to the first stop.

A media playlist configured to repeat can maintain a logical cycle rather than repeatedly rebuilding a linear sequence.

A token-passing mechanism can represent the next participant as the next node in a circular structure.

These applications benefit from the fact that moving from the final logical element to the first requires no separate boundary transition.

## Design Trade-offs

A circular singly linked list is appropriate when forward traversal is sufficient and memory overhead should remain low.

A circular doubly linked list is appropriate when reverse traversal or constant-time deletion of a known node is important.

An array is often preferable when random positional access is a dominant requirement because linked lists require `O(n)` traversal to reach an arbitrary position.

The circular structure is most valuable when repeated progression through the same set of elements is a core part of the problem rather than an incidental implementation detail.

## Validation and Reliability

Production implementations should treat the circular invariants as explicit correctness conditions.

Tests should cover:

- an empty list
- a one-node cycle
- insertion into an empty list
- insertion at the head
- insertion at the tail
- insertion between two existing nodes
- deletion of the only node
- deletion of the head
- deletion of the tail
- deletion of an interior node
- deletion of a value that does not exist
- duplicate values
- repeated rotations
- complete forward traversal
- complete backward traversal for doubly linked structures
- structural validation after every mutation

The Python, JavaScript, and C++ programs include these boundary conditions directly rather than treating the linked-list algorithm as correct only for a multi-node happy path.

## Security and Resource Considerations

Circular references can cause accidental infinite loops, excessive CPU consumption, and unresponsive applications when traversal termination is implemented incorrectly.

Applications processing externally supplied data should validate list sizes and operation parameters before performing repeated traversal.

In C++, manual node allocation introduces ownership responsibilities. The case-study implementation therefore provides a destructor and `clear()` operation so dynamically allocated nodes are released. Copy construction and copy assignment are disabled because a shallow copy of raw node pointers would create ownership and double-free problems.

In Python and JavaScript, memory is managed by the runtime, but references can still preserve objects longer than intended. Removing obsolete links, especially in doubly linked structures, makes the intended ownership relationships clearer and reduces accidental retention through reachable references.

## Debugging Strategy

When a circular list behaves incorrectly, inspect the boundary relationships first.

For a singly linked list, verify:

`tail`

and:

`tail.next`

For a doubly linked list, verify:

`head.prev`

`tail.next`

and the reciprocal relationships between every neighboring pair.

A useful debugging technique is to print exactly `size` nodes rather than traversing until a null pointer. If the traversal does not return to the expected starting node after the expected number of steps, the structure is inconsistent.

The invariant checks included in all three implementations turn these structural assumptions into executable assertions.

## Relationship Between the Implementations

The Python implementation emphasizes reusable data structures, validation, and a round-robin scheduling simulation.

The JavaScript implementation focuses on mutable object references and demonstrates how a circular data structure can participate in asynchronous scheduling without confusing asynchronous control flow with linked-list structure.

The C++ implementation focuses on explicit memory ownership and a domain-oriented transport route. Its doubly linked route demonstrates why bidirectional links are useful when movement can occur in both directions.

All three implementations use the same fundamental circular invariant, but they intentionally express it through the strengths and constraints of their respective languages.

## Technical Takeaway

The defining property of a circular linked list is not simply that its nodes form a circle. The important engineering consequence is that there is no natural null boundary.

That changes traversal termination, insertion at the boundaries, deletion of boundary nodes, validation strategy, and the way applications model repeated progression.

A circular singly linked list minimizes per-node linkage and is well suited to forward-only cyclic workflows. A circular doubly linked list adds reverse navigation and direct predecessor access at the cost of additional memory and more complex mutation invariants.

The most reliable implementations make those invariants explicit, handle empty and one-node states separately, bound traversal, validate mutations, and select the singly or doubly linked representation according to the actual navigation requirements of the application.
