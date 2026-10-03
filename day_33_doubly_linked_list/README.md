# Doubly Linked List

A doubly linked list is a linked sequence in which every node stores a reference to both its predecessor and its successor. The two links are conventionally called `prev` and `next`.

This structure is useful when an application needs efficient movement in both directions or frequent insertion and deletion around nodes that are already known. The additional backward pointer increases memory consumption and makes mutation more error-prone than a singly linked list, but it removes the need to rediscover a predecessor during many local operations.

The three implementations in this repository deliberately approach the structure from different perspectives:

- The Python implementation develops a general-purpose mutable doubly linked list, including indexed operations, invariant validation, safe mutation, and a browser-history model.
- The JavaScript implementation emphasizes object references, generator-based traversal, the iterator protocol, event-driven navigation, and a double-ended task queue.
- The C++ implementation treats the list as a low-level systems component and builds a repository review-timeline case study around explicit node ownership, pointer manipulation, validation, and move semantics.

## Core Node Model

A singly linked node normally has the form:

`value -> next`

A doubly linked node has:

`prev <- value -> next`

For three nodes `A`, `B`, and `C`, the expected relationships are:

`A.next == B`

`B.prev == A`

`B.next == C`

`C.prev == B`

The endpoints have special conditions:

`head.prev == null`

`tail.next == null`

These endpoint rules are not optional implementation details. They are structural invariants. If `head.prev` points somewhere else, or if `B.next` points to `C` while `C.prev` does not point back to `B`, forward and backward traversal no longer describe the same sequence.

The defining property of a correct doubly linked list is therefore bidirectional consistency.

## Head, Tail, and Size

The implementations maintain references to both the first and last node.

`head` identifies the first node.

`tail` identifies the final node.

`size` or its language-specific equivalent records how many nodes exist.

Maintaining `tail` is particularly important because it makes appending constant time. Without a tail reference, appending would normally require traversing from the head until the last node is found.

An empty list has:

`head == null`

`tail == null`

and a size of zero.

A single-node list has the same node as both endpoints:

`head == tail`

That node simultaneously satisfies:

`head.prev == null`

and

`tail.next == null`

## Forward and Backward Traversal

Forward traversal begins at `head` and repeatedly follows `next`:

`head -> next -> next -> ... -> tail`

Backward traversal begins at `tail` and repeatedly follows `prev`:

`tail -> prev -> prev -> ... -> head`

This is the primary structural capability that distinguishes a doubly linked list from a singly linked list.

The Python implementation exposes `forward()` and `backward()` generators. This avoids constructing an intermediate collection when a caller only needs to consume the sequence.

The JavaScript implementation uses generator functions as well. The `forward()` generator can be returned from `[Symbol.iterator]`, allowing the list itself to participate in JavaScript's `for...of` iteration protocol.

The C++ implementation performs explicit pointer traversal and returns vectors for the case-study display. This makes the underlying pointer operations visible without introducing a generic iterator framework that would distract from the node-linking mechanics.

## Insertion

Insertion into a doubly linked list requires coordinated updates to both directions.

Suppose `A` and `B` are adjacent:

`A <-> B`

To insert `X` between them, the final structure must be:

`A <-> X <-> B`

The links must become:

`A.next = X`

`X.prev = A`

`X.next = B`

`B.prev = X`

Updating only two of these relationships produces a corrupted structure.

Insertion at the beginning is a special case because there is no predecessor. The new node becomes the head and its `next` points to the old head.

Insertion at the end is also a special case because there is no successor. The new node becomes the tail and its `prev` points to the old tail.

The Python `insert_at()` method supports insertion at an arbitrary index and treats `index == size` as an append operation.

The C++ `insertBefore()` method takes an already known node. This focuses on the fundamental linked-list operation rather than array-style indexing.

## Deletion

Deletion is the inverse of insertion.

For:

`A <-> X <-> B`

removing `X` requires:

`A.next = B`

and:

`B.prev = A`

The removed node can then be detached.

The important performance distinction is between locating a node and unlinking a node.

Searching for a value is generally O(n) because a linked list does not provide direct random access.

Once the exact node is already known, removing it is O(1), because only its immediate neighbors must be modified.

This distinction appears explicitly in all three implementations.

The Python implementation exposes `remove_node()`.

The JavaScript implementation uses `removeNode()`.

The C++ case study uses `removeNode()` with a `Node*`.

Each implementation clears the removed node's links after it has been detached. This is useful for making the node's detached state explicit and reduces the chance that later debugging will confuse an old relationship with a live list relationship.

## Indexed Access

A doubly linked list is not an array.

An array can calculate the address of an element from its index, so accessing position `i` is normally O(1).

A linked list must follow links to reach position `i`.

The Python and JavaScript implementations optimize this traversal by choosing the nearer endpoint.

For a list of size `n`, an index near zero is reached from `head`, while an index near `n - 1` is reached from `tail`.

This reduces the maximum traversal distance but does not change the asymptotic complexity: indexed access remains O(n).

For example, accessing an element near the end does not require walking from the beginning when `tail` and `prev` are available.

## Doubly Linked Versus Singly Linked Lists

A singly linked list stores only a forward link:

`value -> next`

A doubly linked list stores both:

`prev <- value -> next`

The extra pointer changes several practical properties.

| Property | Singly linked list | Doubly linked list |
|---|---|---|
| Forward traversal | Direct | Direct |
| Backward traversal | Not directly supported | Direct through `prev` |
| Per-node links | One | Two |
| Append with tail | O(1) | O(1) |
| Known-node local deletion | Requires predecessor information | O(1) using `prev` |
| Mutation bookkeeping | Simpler | More pointer relationships must remain consistent |
| Memory per node | Lower | Higher |
| Bidirectional cursor | Requires extra state or rescanning | Natural |
| Reverse traversal | Usually requires extra work | Direct |

A doubly linked list is not automatically superior. It is useful when bidirectional navigation or local node removal justifies the additional memory and mutation complexity.

If an application only needs forward traversal and simple append operations, the additional `prev` link may provide little benefit.

## Python Implementation

The Python file implements `DoublyLinkedList` as a reusable mutable data structure.

Its `Node` contains:

`value`

`prev`

`next`

The list maintains:

`head`

`tail`

`_size`

The implementation demonstrates append and prepend operations, indexed insertion, removal by node, removal by index, removal by value, removal of all matching values, searching, forward traversal, backward traversal, clearing, and structural validation.

### Efficient Endpoint Selection

The `_node_at()` method demonstrates an important doubly linked-list optimization.

When the requested index is in the first half of the list, traversal begins at `head` and follows `next`.

When the index is in the second half, traversal begins at `tail` and follows `prev`.

This does not make random access constant time, but it avoids unnecessary traversal across the entire list.

### Structural Validation

The Python `validate()` method walks in both directions.

During forward traversal it verifies that:

`current.prev` is the node previously visited.

It also verifies that:

`current.next.prev is current`

During backward traversal it performs the symmetric checks.

The method also verifies endpoint correctness, list size, and the absence of traversal cycles longer than the expected node count.

This kind of validation is particularly valuable for linked lists because pointer corruption can otherwise remain hidden until a later traversal crashes or silently produces incorrect data.

### Safe Mutation While Traversing

Removing the current node changes its `next` reference. Therefore code that wants to delete nodes during traversal must save the successor before unlinking the current node.

The Python implementation demonstrates this pattern:

`following = current.next`

followed by deletion and then:

`current = following`

This pattern is necessary because `remove_node()` intentionally clears the removed node's links.

### Browser History

The `BrowserHistory` class models a natural use case for bidirectional links.

The current page has:

- `prev` pointing to the previous page.
- `next` pointing to the next page.

A backward action follows `prev`.

A forward action follows `next`.

Visiting a new page after moving backward creates a new branch and discards the old forward path by breaking the current node's `next` relationship.

The example therefore demonstrates why a doubly linked list is useful when an application maintains a movable cursor within a sequence.

## JavaScript Implementation

The JavaScript file implements the same core data structure with JavaScript object references but focuses on mechanisms that are natural in the language.

The `Node` class represents the mutable link structure. JavaScript objects are reference-based, so assigning `node.next = anotherNode` connects the two object instances directly.

### Generator-Based Traversal

The `forward()` and `backward()` methods are generator functions.

A generator yields values lazily rather than constructing an entire array before iteration begins.

The list also implements:

`[Symbol.iterator]`

which returns the forward generator.

As a result, the list can be consumed naturally by JavaScript iteration constructs.

### Event-Driven Navigation

`NavigationHistory` extends `EventTarget`.

The structural state is still represented by `prev` and `next`, but navigation operations dispatch events after state changes.

This models a browser-oriented application more closely than a simple console-only linked list.

A listener can observe a visit or navigation event without owning the list's internal pointer-management logic.

The data structure therefore separates:

- structural navigation state,
- navigation operations,
- observers interested in state changes.

### Double-Ended Queue

The JavaScript `TaskDeque` class demonstrates another useful consequence of a doubly linked structure.

Urgent work can be inserted at the front.

Normal work can be appended at the back.

Work can be removed from either end.

With both endpoints stored, these operations can be performed without scanning the list.

This is one reason doubly linked lists are often associated with deque-like structures, although production JavaScript applications frequently use the language's built-in `Array` or specialized collections instead when their performance characteristics are sufficient.

## C++ Repository Review Timeline Case Study

The C++ implementation models a technical review timeline.

The timeline records events such as:

`commit: add authentication`

`review: security reviewer requested changes`

`commit: address review comments`

`review: changes approved`

This scenario benefits from both traversal directions.

Chronological output starts at `head`.

A newest-first review dashboard starts at `tail`.

The list can therefore provide either view without reversing a copied array.

### Explicit Node Ownership

The C++ `ChangeHistory` class owns dynamically allocated `Node` objects.

The destructor calls `clear()` so nodes are released when the list is destroyed.

Copy construction and copy assignment are disabled because a shallow copy of raw node pointers would create multiple owners of the same nodes and eventually cause double deletion.

Move construction and move assignment are implemented so ownership can be transferred safely.

After a move, the source object has null endpoints and zero size.

This is a C++-specific design concern that does not arise in the same form in the Python or JavaScript implementations because their memory-management models differ.

### Pointer-Level Deletion

The C++ implementation makes the deletion mechanism particularly explicit.

For a node with:

`previous`

and:

`next`

the predecessor is connected to the successor, and the successor is connected back to the predecessor.

If the removed node is the head, `head_` changes.

If it is the tail, `tail_` changes.

If it is the only node, both endpoints become null.

The node is then deleted.

The method returns the stored event before releasing the node.

### Review Cursor

`ReviewCursor` stores a current node and can move in either direction.

`moveNext()` follows `current_->next`.

`movePrevious()` follows `current_->prev`.

This illustrates the difference between a linked-list structure and an index-based sequence. The cursor does not need to calculate an integer position to move to an adjacent event.

## Complexity

| Operation | Typical complexity |
|---|---:|
| Prepend | O(1) |
| Append with tail | O(1) |
| Remove head | O(1) |
| Remove tail | O(1) |
| Remove known node | O(1) |
| Insert around a known node | O(1) |
| Search by value | O(n) |
| Forward traversal | O(n) |
| Backward traversal | O(n) |
| Indexed access | O(n) |
| Clear entire list | O(n) |

The O(1) deletion result depends on already having a reference to the target node.

Consider a request to remove `"logging"` from a list. Finding `"logging"` can require O(n) traversal. After the node has been located, the unlink operation itself is O(1).

This distinction is fundamental when analyzing linked-list algorithms.

## Memory Characteristics

Every node requires storage for its payload plus two links.

A conceptual node can be represented as:

`[prev | value | next]`

A singly linked node can be represented as:

`[value | next]`

Therefore a doubly linked list consumes additional memory for `prev`.

The actual memory overhead can be greater than the raw pointer size because object headers, alignment, allocator metadata, and language runtime representation also contribute to the physical memory footprint.

Doubly linked lists can therefore have poorer cache locality than contiguous arrays or vectors. Each node may reside at a different memory address, while an array or vector stores neighboring elements close together.

## Edge Cases

The empty list requires special handling because both endpoints are null.

A single-node list requires another special case because the same node is both head and tail.

Deleting the head requires updating the new head's `prev`.

Deleting the tail requires updating the new tail's `next`.

Deleting the only node requires both endpoints to become null.

Inserting into an empty list must establish both endpoints.

Removing an absent value must not alter the structure.

Removing multiple matching nodes requires careful traversal because deleting a node changes its links.

These cases are explicitly exercised by the implementations rather than being left as theoretical descriptions.

## Common Pointer Errors

A frequent insertion error is updating `A.next` to point to `X` without setting `X.prev` to `A`.

Another is setting `X.next` to `B` without setting `B.prev` to `X`.

During deletion, changing `A.next` to `B` without changing `B.prev` leaves the two traversal directions inconsistent.

Forgetting to update `head` when deleting the first node can leave the list pointing to detached memory in manual-memory-management languages.

Forgetting to update `tail` when deleting the last node creates an endpoint that no longer belongs to the active sequence.

Clearing a node's links before saving its successor can make continued traversal impossible.

The invariant:

`A.next == B` implies `B.prev == A`

is a compact way to detect many of these failures.

## Validation and Debugging

A useful linked-list validator should inspect both directions.

Forward-only validation can miss a broken `prev` pointer.

Backward-only validation can miss a broken `next` pointer.

The implementations therefore validate both directions and verify endpoint conditions.

Cycle detection is also important. An accidental assignment such as `tail.next = head` turns a linear list into a cycle. A traversal without a safety condition can then run indefinitely.

The provided validators compare traversal counts with the stored size. If traversal continues beyond the expected number of nodes, a cycle or size inconsistency is reported.

In a production implementation, debug-mode invariant checks can be enabled after complex mutations while avoiding their O(n) cost on every operation in performance-sensitive release paths.

## Mutation Safety

Linked-list mutation is local but pointer-sensitive.

When deleting the current node during traversal, save the successor first:

`nextNode = current.next`

Then unlink the current node.

Then continue with `nextNode`.

The same principle applies in all three languages, although the memory-management consequences differ.

Python and JavaScript use managed object memory.

C++ explicitly releases nodes with `delete` in this implementation.

A C++ caller must therefore treat a pointer to a removed node as invalid after `removeNode()` returns. Retaining and dereferencing such a pointer creates undefined behavior.

## Practical Applications

Doubly linked lists are appropriate when an application needs a movable position in a sequence and movement in both directions is important.

Examples include:

- Browser history, where back and forward navigation follow opposite node links.
- Text-editor structures where a cursor or local editing region needs neighboring navigation.
- Deques where insertion and removal occur at both ends.
- LRU-cache implementations, where a known cache entry can be removed from the middle in O(1) after a hash table identifies its node.
- Navigation histories, where a current item can move to an adjacent previous or next state.
- Timeline interfaces where newest-first and chronological traversal are both useful.

The choice should be based on access patterns rather than on the fact that the structure supports more operations than a singly linked list.

## Relationship Between Operations

The central relationships can be viewed as a chain of invariants:

`head -> next -> ... -> tail`

and simultaneously:

`tail -> prev -> ... -> head`

Insertion introduces a node while preserving both paths.

Deletion removes a node while reconnecting both paths.

Forward traversal uses `next`.

Backward traversal uses `prev`.

The tail pointer makes the starting point of reverse traversal immediately available.

The head pointer makes the starting point of forward traversal immediately available.

The size value provides a consistency check but is not required for pointer traversal itself.

This separation of concerns is useful when designing implementations: endpoint references provide efficient entry points, node links provide local connectivity, and validation checks whether the three components still agree.

## Limitations

A doubly linked list does not provide constant-time random access.

Its nodes usually have worse cache locality than contiguous storage.

Each node consumes extra memory for the backward pointer.

Every insertion and deletion must maintain more relationships than the corresponding singly linked-list operation.

Searching by value remains O(n).

For workloads dominated by indexed reads, a contiguous array or vector is generally a more natural structure. For workloads dominated by local insertion, deletion, and bidirectional navigation, the doubly linked representation can be useful.

## Production Considerations

A production implementation should define node ownership clearly.

In garbage-collected languages, the primary concerns are structural consistency and accidental retention of objects.

In C++, ownership must be explicit. Raw pointers can be used carefully for internal links, but ownership should be represented by an appropriate design. The C++ case study owns nodes inside `ChangeHistory` and prevents unsafe copying.

Concurrency requires additional design. A doubly linked list is not automatically thread-safe. Concurrent mutation can invalidate traversal assumptions and cause data races in languages with shared mutable memory.

Exception safety also matters in systems code. Pointer updates should be performed in an order that preserves a valid structure, and ownership should not be lost if an operation fails.

Security-sensitive applications should treat externally supplied values as data rather than trusting them as pointers, indexes, or internal node identifiers. The implementations validate indexes and reject invalid operations rather than allowing arbitrary structural manipulation.

## Implementation Map

| Concept | Python | JavaScript | C++ |
|---|---|---|---|
| Node representation | `Node` dataclass | `Node` class | Nested `Node` struct |
| Forward link | `next` | `next` | `next` |
| Backward link | `prev` | `prev` | `prev` |
| Head/tail | Explicit references | Explicit references | Private pointers |
| Forward traversal | Generator | Generator | Vector-producing traversal |
| Backward traversal | Generator | Generator | Reverse pointer traversal |
| Known-node deletion | `remove_node()` | `removeNode()` | `removeNode()` |
| Structural validation | `validate()` | `validate()` | `validate()` |
| Main realistic model | Browser history | Event-driven navigation | Repository review timeline |
| Language-specific focus | Iterables and validation | Generators and `EventTarget` | Ownership and move semantics |

The implementations share the same fundamental data-structure invariant but intentionally use different surrounding designs. This demonstrates that the doubly linked list is a structural mechanism whose usefulness depends on the application behavior built around it.
