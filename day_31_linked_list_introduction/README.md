# Linked List Introduction

## Scope

A linked list is a dynamic data structure in which elements are stored in separate nodes connected by references or pointers. Unlike a contiguous array, a linked list does not require its logical elements to occupy adjacent memory locations.

This project focuses on the foundations required to understand linked lists:

- node structure
- pointers and references
- dynamic memory allocation
- the `head` and `tail` concepts
- traversal
- searching
- insertion and deletion
- reversing links
- cycle detection
- comparison with arrays
- practical queue usage
- memory ownership
- edge cases and invariants
- algorithmic complexity

The three implementations approach the topic differently. Python emphasizes an executable progression through linked-list algorithms. JavaScript emphasizes object references and an event-history use case. C++ uses explicit pointer and ownership semantics in a practical work-queue system.

## Linked List Structure

A singly linked list consists of nodes. Each node normally contains two logical components:

- a data value
- a link to the next node

A simple conceptual chain is:

`head -> [10 | next] -> [20 | next] -> [30 | null]`

The first node is identified by `head`. Each node knows how to reach the next node, but a singly linked-list node does not normally contain a reference to its previous node.

The final node points to `null` or `None`, depending on the programming language. That terminal value represents the end of the chain.

A linked list therefore describes a sequence through relationships between objects rather than through element positions in contiguous storage.

## Nodes, References, and Pointers

### Python

The Python implementation defines `Node` with a `value` attribute and a `next` attribute.

`next` stores a reference to another `Node` object. Python does not expose a normal application-level raw memory address for this operation. Memory allocation and object lifetime are managed by the Python runtime.

The important structural relationship is still explicit:

`first.next = second`

After this assignment, the first node can reach the second node.

The Python program also demonstrates that removing the reference with `first.next = None` changes the logical structure of the list. If no other references keep an object alive, Python can eventually reclaim that object's memory.

### JavaScript

JavaScript uses object references in a similar conceptual manner.

A `Node` contains `value` and `next`. The expression `first.next = second` connects two objects.

JavaScript developers normally do not manipulate raw memory addresses. The JavaScript engine manages allocation and garbage collection.

The implementation uses strict equality, such as `first.next === second`, to demonstrate that both variables can refer to the same object.

### C++

C++ exposes pointers directly. A pointer can contain the address of another object.

The C++ demonstration uses expressions such as `first.next->value` to follow a pointer and access the target node.

The practical case study goes further by separating ownership from traversal. `std::unique_ptr<Node>` owns the next node, while a raw `Node*` is used as a non-owning traversal or tail reference.

This distinction is important in modern C++ because linked-list implementations can otherwise become vulnerable to memory leaks, double deletion, dangling pointers, and unclear ownership.

## Dynamic Memory Allocation

Linked lists are useful partly because nodes can be allocated independently.

An array normally represents elements in a contiguous logical storage region. A linked list can create a new node without requiring every existing node to move.

This property is useful when insertion and deletion are frequent and the application already has a reference to the relevant position.

The trade-off is that every linked-list node needs link metadata in addition to its stored value. Independently allocated nodes can also have worse cache locality than contiguous arrays.

### Python allocation

Python's `Node` instances are dynamically allocated objects. The programmer creates a node with `Node(value)` and Python manages its lifetime.

### JavaScript allocation

JavaScript's `new Node(value)` creates an object. The JavaScript runtime determines where the object is stored and manages its lifetime through garbage collection.

### C++ allocation

The C++ case study uses `std::make_unique<Node>()`. This performs dynamic allocation while giving ownership to a `std::unique_ptr`.

When a `unique_ptr` is destroyed or reassigned, the object it owns is automatically released. This makes the ownership model substantially safer than manually pairing every `new` operation with a `delete`.

## Head and Tail

`head` identifies the first node.

A `tail` reference identifies the final node when the implementation maintains one.

A tail reference changes the complexity of append operations. If only `head` exists, appending normally requires traversal to the final node, which is O(n). With a valid `tail` reference, appending can link the new node directly after the current tail in O(1) time.

The implementations maintain the invariant that an empty list has no valid tail.

For a non-empty list, the tail is the node whose `next` reference is null.

The C++ implementation explicitly checks this relationship through `invariantHolds()`.

## Traversal

Traversal is the fundamental operation used to work with a singly linked list.

A typical traversal starts with the head:

`current = head`

The algorithm processes the current node and then advances:

`current = current.next`

The traversal ends when `current` becomes null.

This is fundamentally different from array indexing. An array can generally calculate the location of an indexed element directly because the elements have a positional relationship with the storage layout. A singly linked list must follow the chain from the head.

Consequently, accessing an arbitrary linked-list position is O(n).

## Searching

Searching for a value in a singly linked list requires traversal until the value is found or the end of the list is reached.

The Python `find()` method returns the matching node itself, which is useful when a later operation needs the node reference.

The JavaScript `find()` method follows the same structural principle but works with JavaScript object references.

The C++ `findById()` method searches a practical queue by work-item identifier and returns a non-owning pointer to the matching record.

Searching remains O(n) because the algorithm may need to inspect every node.

## Insertion

Insertion demonstrates one of the principal structural benefits of linked lists.

Suppose the chain is:

`A -> B -> C`

To insert `X` after `B`, the links become:

`A -> B -> X -> C`

The operation requires changing references rather than shifting all later elements.

If the target node is already known, inserting after it is O(1).

If the program first needs to search for the target by value, the complete operation becomes O(n), because finding the target dominates the cost.

The Python implementation exposes `insert_after()`. The JavaScript implementation performs the same structural operation as part of its independent workflow model.

## Deletion

Deletion changes the relationship between neighboring nodes.

For:

`A -> B -> C`

removing `B` changes the link from `A -> B` to `A -> C`.

A singly linked list usually needs the previous node to perform this operation efficiently.

The Python `delete_first()` method handles this by maintaining both `previous` and `current` during traversal.

The C++ queue performs removal by changing the owning `unique_ptr` that points to the removed node. This is an important ownership-aware implementation detail because releasing the owning pointer also releases the removed node safely.

Deleting the head is a special case because there is no previous node. The head itself must be advanced.

Deleting the tail is another important case because the tail reference must be updated to the new final node.

## Reverse Operation

Reversing a singly linked list demonstrates why pointer or reference manipulation requires careful ordering.

For:

`A -> B -> C -> null`

the desired result is:

`C -> B -> A -> null`

At each node, the implementation must preserve the original next reference before replacing it.

The essential state consists of:

- the previous node
- the current node
- the original next node

The Python and JavaScript implementations perform this in-place reversal without allocating another complete list.

The operation is O(n) because every node must be visited once.

## Finding the Middle Node

The Python and JavaScript implementations use two traversal references.

The slow reference advances by one node while the fast reference advances by two nodes.

When the fast reference reaches the end, the slow reference is positioned around the middle.

This technique finds the middle in O(n) time while using O(1) additional space.

For an even-sized list, the implementations return the second middle node.

## Cycle Detection

A normal singly linked list eventually reaches null.

A malformed or intentionally cyclic structure may instead contain a chain such as:

`A -> B -> C -> D -> B`

There is no terminal null in this structure.

The Python and JavaScript implementations use Floyd's tortoise-and-hare algorithm. One reference advances one node at a time and another advances two nodes at a time.

If a cycle exists, the two references eventually meet.

The algorithm uses O(n) time and O(1) additional space.

Cycle detection is particularly important for debugging because ordinary traversal assumes termination. A traversal over an unexpected cycle can otherwise continue indefinitely.

## Array Comparison

| Operation | Typical array behavior | Singly linked-list behavior |
|---|---|---|
| Access by index | O(1) | O(n) |
| Search by value | O(n) | O(n) |
| Insert at beginning | O(n) for typical contiguous arrays | O(1) with head |
| Delete at beginning | O(n) for typical contiguous arrays | O(1) with head |
| Append | Usually amortized O(1) for dynamic arrays | O(1) with tail |
| Insert after known node | Requires positional movement | O(1) |
| Reverse | O(n) | O(n) |
| Extra link metadata | No per-element next pointer | Required |

The table describes common implementations rather than a universal rule for every array or vector implementation.

The main structural distinction is that arrays provide efficient positional access while linked lists provide efficient link manipulation when the relevant node or predecessor is already known.

## Python Implementation

The Python file begins with direct node construction and reference relationships before introducing a reusable `SinglyLinkedList`.

The implementation maintains:

- `head`
- `tail`
- `size`

The list supports append, prepend, search, insertion after a target, deletion by value, deletion by index, reversal, middle-node detection, cycle detection, and duplicate removal.

The `remove_duplicates()` implementation uses a Python `set` to record values already encountered. This changes duplicate detection from repeated nested scans to average O(n) time with additional O(n) storage.

The script also contains a `TaskQueue` example. It demonstrates why a linked structure can naturally model FIFO processing when insertion occurs at the tail and removal occurs at the head.

The benchmark compares direct Python-list indexing with explicit linked-list traversal. The measured times are machine-dependent; the purpose of the benchmark is to make the different access mechanisms observable rather than to establish a hardware-independent timing ratio.

The Python program includes executable assertions covering insertion, deletion, reversal, cycle invariants, and duplicate removal.

## JavaScript Implementation

The JavaScript implementation uses ES classes to represent nodes and the linked-list container.

Its linked-list class supports:

- append
- prepend
- search
- insertion after a target
- deletion of the first matching value
- reversal
- middle-node detection
- cycle detection
- safe serialization

The `toArray()` method includes a defensive traversal limit. This is useful because converting a cyclic linked structure to an ordinary array would otherwise never terminate.

The JavaScript-specific practical example is an event history. `EventHistory` stores event records in a linked list while maintaining listener functions in a `Map`.

This separates two responsibilities: listeners receive events immediately, while the linked list retains an ordered history of emitted events.

The implementation therefore demonstrates a realistic use of object references without simply translating the Python examples line by line.

## C++ Case Study

The C++ implementation models a work-processing queue.

A `WorkItem` contains:

- an identifier
- a title
- an owner
- a priority

Each work item is stored in a linked node.

The queue uses a `head_` owning pointer and a `tail_` non-owning pointer. `head_` owns the complete node chain through `unique_ptr` links.

Appending creates a new node and attaches it to the current tail. The tail pointer is then updated using `get()` without transferring ownership.

This provides O(1) enqueue behavior while preserving clear ownership.

Dequeuing moves the next owning pointer into `head_`. If the queue becomes empty, the tail is reset to null.

The case study also implements removal by identifier. When a node is removed from the middle, the predecessor's owning `unique_ptr` is replaced with the removed node's next owning pointer. The removed node then becomes automatically destructible.

## C++ Validation

`WorkItemValidator` rejects invalid records before they enter the queue.

The validation rules require:

- a positive identifier
- a non-empty title
- a non-empty owner
- a priority between 1 and 5

The queue separately handles an empty dequeue operation with `std::underflow_error`.

This distinction is important because validation failure and invalid queue state represent different categories of failure.

The program also checks a structural invariant. The counted number of nodes must equal the stored size, and the final reachable node must match the stored tail pointer.

## Memory Ownership in the C++ Case Study

The C++ implementation deliberately avoids a raw owning pointer.

A raw pointer is appropriate as a non-owning traversal reference when its lifetime is guaranteed by another owner. The `tail_` pointer has this role.

The `unique_ptr` chain is responsible for ownership.

This design prevents several common linked-list errors:

- forgetting to delete dynamically allocated nodes
- deleting the same node twice
- retaining ownership of an object that has already been deleted
- losing the remainder of a list during reassignment

Ownership remains a central difference between a conceptual linked-list diagram and a production-quality C++ implementation.

## Edge Cases

An empty linked list has no head and no tail.

A one-node list has the same node as both head and tail.

Deleting the only node must therefore clear both references.

Inserting after the current tail must update the tail.

Deleting the current tail must move the tail to its predecessor.

Searching an empty list must terminate immediately.

Invalid index operations should be rejected rather than silently accessing nonexistent nodes.

Cycle creation must be treated separately from ordinary linked-list traversal because a cycle violates the assumption that traversal eventually reaches null.

## Common Implementation Errors

A linked-list implementation can fail even when the individual node type is correct.

A frequent error during insertion is overwriting `current.next` before saving the old next node. That loses access to the remainder of the chain.

During reversal, the same mistake can disconnect the list. The original next reference must be saved before the current link is redirected.

Another error is updating the head without updating the tail when the last node is deleted.

A further error is maintaining a `size` field but failing to update it on every insertion and deletion. The C++ invariant check illustrates how metadata and structural state can be validated together.

In C++, manually managing node ownership without a clear ownership model can introduce memory-safety defects. The case study uses `unique_ptr` specifically to make ownership explicit.

## Performance Considerations

A linked list is not automatically faster than an array.

Its performance advantages appear in operations where link manipulation is more important than indexed access.

A singly linked list provides O(1) insertion at the head and O(1) append when a tail reference is maintained.

It does not provide O(1) random access. Reaching the element at position `k` requires following up to `k` links, making indexed access O(n).

Independent node allocation can also reduce cache locality. A contiguous array often allows the processor to access neighboring elements efficiently because they are physically close in memory.

The practical choice therefore depends on the workload rather than on the data structure being universally superior.

## Security and Reliability Considerations

Linked lists can contribute to reliability problems when malformed links are possible.

An unexpected cycle can cause an unbounded traversal.

A dangling pointer in C++ can cause undefined behavior if a pointer is used after the object it referenced has been destroyed.

Incorrect ownership can cause memory leaks or double deletion.

The C++ case study reduces these risks with RAII and `unique_ptr`. The Python and JavaScript versions rely on managed memory but still require correct logical references.

Validation is also important in application-level linked structures. The C++ work queue rejects malformed work items before storing them, preventing invalid records from propagating through the system.

## Complexity Model

For the implementations in this project, the principal costs are:

| Operation | Complexity |
|---|---|
| Access by index | O(n) |
| Search | O(n) |
| Insert at head | O(1) |
| Delete at head | O(1) |
| Append with tail | O(1) |
| Append without tail | O(n) |
| Insert after known node | O(1) |
| Reverse | O(n) |
| Middle-node detection | O(n) time, O(1) extra space |
| Cycle detection | O(n) time, O(1) extra space |

These complexities describe the algorithms used here and assume that the list itself is a standard singly linked structure.

## Practical Interpretation

A linked list should be understood as a chain of relationships between nodes.

The essential mental model is not an array with slower indexing. It is a structure in which each node provides the information required to reach the next node.

Python and JavaScript hide physical memory management while retaining the reference-based structure.

C++ makes the pointer and ownership model explicit, which exposes both the power and the risks of manual data-structure design.

The central trade-off is therefore between efficient positional access and efficient link manipulation. Understanding that trade-off is more important than memorizing a particular linked-list implementation.
