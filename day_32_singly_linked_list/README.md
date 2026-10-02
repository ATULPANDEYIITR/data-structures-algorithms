# Singly Linked List

A singly linked list is a sequential data structure built from nodes. Each node stores a value and a reference to the next node. The final node has no successor, represented as `None`, `null`, or `nullptr` depending on the implementation language.

This project focuses on the core operations that define a singly linked list:

- traversal
- insertion
- deletion
- searching
- updating
- reversal

The three implementations approach the same data structure from different programming-language perspectives. Python emphasizes a readable, executable implementation with validation and testing. JavaScript emphasizes object references, generators, and runtime validation. C++ models a realistic sequential change-history structure while using `std::unique_ptr` to express node ownership safely.

## Structural Model

A singly linked list does not store its elements in one contiguous block. Instead, the structure begins with a `head` reference.

A typical list has this logical shape:

`head -> [value | next] -> [value | next] -> [value | next] -> null`

The `next` field is the essential structural relationship. Traversal follows that relationship repeatedly until it reaches the terminal null reference.

Unlike an array, a singly linked list does not provide constant-time indexed access. Finding the element at position `k` requires following approximately `k` links from the head.

The structure also has no inherent backward relationship. From a node, an implementation can reach its successor, but it cannot directly reach its predecessor.

## Node Representation

The Python implementation uses the `Node` dataclass:

`value` stores the payload and `next` stores either another `Node` or `None`.

The JavaScript implementation uses `ListNode`, where `next` initially contains `null`.

The C++ implementation represents each node with an internal `Node` structure containing a change identifier, description, author, and an owning `std::unique_ptr<Node>` called `next`.

The C++ design is intentionally different from the integer-only examples. It demonstrates that a linked-list node can represent a meaningful domain record rather than simply storing a primitive number.

## Traversal

Traversal means visiting nodes sequentially by following the `next` relationship.

The Python implementation supports normal iteration through `__iter__`. A loop therefore walks the structure without exposing its internal node-management details.

The JavaScript implementation provides a generator named `traverse`. The generator yields each value as the linked structure is walked. This avoids requiring an intermediate array when a caller only needs sequential access.

The C++ implementation performs explicit pointer traversal. A `Node*` observer moves from one node to the next with `current = current->next.get()`.

Traversal is fundamental because most singly linked-list operations begin with the same pattern:

`current = head`

followed by repeated movement to `current.next`.

Traversal requires O(n) time when all n nodes must potentially be inspected.

## Insertion

Insertion changes the links so that a new node becomes part of the chain.

### Insertion at the head

Head insertion is constant time.

Before insertion:

`head -> A -> B -> C`

After inserting X:

`head -> X -> A -> B -> C`

Only two references need to be established:

`X.next = old_head`

and then:

`head = X`

The Python `prepend`, JavaScript `prepend`, and C++ `prepend` methods implement this operation.

The operation takes O(1) time because it does not depend on the number of existing nodes.

### Insertion at the end

Without a tail pointer, reaching the final node requires traversal.

For:

`A -> B -> C -> null`

an append operation must find C before assigning its `next` reference.

The implementations therefore have O(n) append behavior.

A separate tail reference could make append O(1), but maintaining a tail introduces another structural invariant: whenever the list changes, the tail must still identify the final node. That additional state is useful when append performance matters, but it is deliberately not part of the basic implementations.

### Insertion at a position

To insert before an existing position, a singly linked list generally needs access to the preceding node.

For:

`A -> B -> C`

inserting X between B and C requires:

`B.next = X`

and:

`X.next = C`

The link to C must be preserved before changing B's successor.

The Python `insert_at` and JavaScript `insertAt` implementations validate the insertion position before modifying the structure.

### Insertion after a matching value

The Python and C++ implementations also demonstrate insertion after a particular existing node.

The operation combines traversal with local pointer manipulation. Traversal is O(n) in the worst case, while the actual insertion after the target is O(1) once the target has been located.

## Deletion

Deletion removes a node by changing the predecessor's `next` reference.

Suppose the structure is:

`A -> B -> C`

Removing B requires the predecessor A to bypass B:

`A -> C`

The removed node no longer belongs to the main chain.

### Deleting the head

Head deletion is a special case because there is no predecessor.

The operation is simply:

`head = head.next`

It therefore takes O(1) time.

All three implementations explicitly handle head deletion because treating it as an ordinary middle-node deletion would require a nonexistent predecessor.

### Deleting a middle or final node

For a node other than the head, the implementation must locate its predecessor.

If the structure is:

`A -> B -> C -> D`

and C is removed, B's successor becomes D.

The traversal needed to locate B makes the complete operation O(n) in the worst case.

### Deleting by value

The Python and JavaScript implementations provide deletion based on the first matching value. They traverse until a matching node is found, then reconnect the predecessor to the matching node's successor.

The Python implementation also provides `delete_all`, which removes every occurrence. This requires special treatment of consecutive matching head nodes before normal predecessor/current traversal can begin.

## Searching

Searching in a singly linked list is sequential.

The Python `search`, JavaScript `search`, and C++ `searchById` operations begin at the head and compare each node's stored value or identifier.

A successful search may terminate early. An unsuccessful search must examine the complete list.

The worst-case time complexity is O(n).

The Python and JavaScript implementations return `-1` when a value is absent. The C++ implementation returns `std::optional<std::size_t>`, which distinguishes a valid position from the absence of a match without using a special integer sentinel.

This distinction is particularly useful in C++ because `std::optional` makes the possibility of a missing result explicit in the type.

## Updating

Updating changes the payload of an existing node without changing the links.

For example:

`A -> B -> C`

can become:

`A -> X -> C`

without changing the structure itself.

The Python implementation supports `update_at` and `update_first`.

The JavaScript implementation provides equivalent position-based and value-based operations.

The C++ case study updates the description associated with a change identifier. The node remains in the same position, and its `next` relationship is unchanged.

Finding the node is O(n), while changing its stored value is O(1) once the node has been located.

## Reversal

Reversal changes the direction of every `next` link.

For:

`A -> B -> C -> D -> null`

the desired result is:

`D -> C -> B -> A -> null`

The most important implementation constraint is that changing a node's `next` reference can destroy access to the unreversed remainder unless that successor is saved first.

The standard iterative technique maintains three references:

- `previous` points to the already reversed portion.
- `current` points to the node being processed.
- `next` temporarily preserves the unreversed successor.

For each node, the algorithm saves the original successor, redirects the current node toward `previous`, advances `previous`, and then advances `current`.

The Python and JavaScript implementations use this technique directly.

The C++ implementation performs the same conceptual transformation with ownership-aware `std::unique_ptr` moves. This is important because C++ node ownership cannot safely be copied or manually discarded while still maintaining ownership invariants.

Iterative reversal takes O(n) time and O(1) auxiliary link storage.

The Python implementation also contains a recursive reversal. Although recursive reversal can be elegant, it consumes O(n) call-stack space and can therefore be unsuitable for very long lists.

## Python Implementation

The Python program provides a reusable `SinglyLinkedList` class.

The class supports:

- construction from an iterable
- iteration
- conversion to a Python list
- `prepend`
- `append`
- `insert_at`
- `insert_after`
- `delete_at`
- `delete_value`
- `delete_all`
- `search`
- `contains`
- `update_at`
- `update_first`
- `get`
- iterative `reverse`
- recursive `reverse_recursive`
- `clear`
- structural validation

The implementation maintains a `_size` field so that list length can be obtained in constant time. Every mutating operation that adds or removes a node updates this invariant.

The `validate_integrity` method combines cycle detection with node counting. Floyd's tortoise-and-hare algorithm uses two references moving at different speeds. If they meet, the structure contains a cycle. A second traversal verifies that the number of reachable nodes agrees with `_size`.

The program deliberately creates a cycle during its integrity demonstration and then restores the list. This exposes a failure condition that normal traversal assumes does not exist: a cycle would prevent ordinary traversal from reaching `None`.

The Python program also includes executable assertions covering construction, insertion, searching, updating, deletion, reversal, and structural integrity.

## JavaScript Implementation

The JavaScript program models nodes as objects and stores references through the `next` property.

Its `SinglyLinkedList` class demonstrates:

- head and size management
- head and tail insertion
- indexed insertion
- insertion after a matching value
- indexed deletion
- deletion by value
- deletion of all matching values
- sequential search
- updates
- indexed access
- iterative reversal
- generator-based traversal
- cycle detection
- structural validation

The generator implementation is a JavaScript-specific complement to the Python iterator. The `traverse` generator yields values one at a time, so a consumer can use `for...of` without first constructing an array.

The reference demonstration also shows that JavaScript objects are reference values. Holding a reference to a node and changing that node's value changes the object that remains connected to the list.

Runtime validation is performed with `RangeError` for invalid indexes. This prevents operations such as inserting at a negative position or deleting a position that does not exist.

## C++ Case Study: Sequential Repository Change History

The C++ program models a repository change history as a singly linked list.

Each node contains:

- a change identifier
- a textual description
- an author
- an owning pointer to the next change

This is a data-structure case study rather than an attempt to reproduce a real version-control system. Actual repository histories can contain branching and merging relationships that require graph structures. The case study deliberately models only a sequential history so that singly linked-list mechanics remain visible.

The `RepositoryChangeList` class provides:

`prepend` for constant-time head insertion.

`append` for sequential insertion at the end.

`insertAfterChange` for finding a change and inserting a related record immediately after it.

`searchById` for sequential identifier lookup.

`updateDescription` for modifying node payload without changing its links.

`deleteById` for unlinking a matching node.

`reverse` for reversing the entire sequence.

`valueAt` for demonstrating sequential indexed access.

`validate` for detecting cycles and checking the stored node count.

### C++ Ownership Model

The most important C++ design decision is the use of `std::unique_ptr`.

Each node owns its successor. The ownership chain therefore follows the same direction as the linked-list structure.

For example:

`head -> node A -> node B -> node C`

means that the head owns A, A owns B, and B owns C.

This gives the list a clear destruction model. When the owning pointer to a node disappears, that node and its owned successor chain can be reclaimed automatically.

Deletion transfers ownership rather than calling `delete` manually.

Reversal is also implemented through ownership transfer. The algorithm cannot simply copy raw pointers because doing so would conflict with the ownership guarantees represented by `unique_ptr`.

Raw `Node*` values are used only as non-owning observers while traversing the structure.

## Complexity

| Operation | Time complexity | Auxiliary space | Reason |
|---|---:|---:|---|
| Prepend | O(1) | O(1) | Only the head link changes |
| Append without tail | O(n) | O(1) | The final node must be located |
| Search | O(n) | O(1) | Nodes are inspected sequentially |
| Update after lookup | O(n) | O(1) | Traversal dominates the operation |
| Delete head | O(1) | O(1) | Head moves to its successor |
| Delete by value | O(n) | O(1) | A predecessor may need to be located |
| Insert after known node | O(1) | O(1) | Only local links change |
| Insert at index | O(n) | O(1) | The predecessor must be located |
| Delete at index | O(n) | O(1) | The predecessor must be located |
| Indexed access | O(n) | O(1) | There is no direct random access |
| Iterative reverse | O(n) | O(1) | Every link is changed once |
| Recursive reverse | O(n) | O(n) stack | Recursive calls accumulate |

The asymptotic complexity does not describe every practical cost. Linked-list nodes generally have additional per-node reference or pointer storage, and their memory locations can be scattered rather than contiguous. These factors can make sequential traversal less cache-friendly than traversal through a contiguous array.

## Edge Cases

An empty list has `head == None`, `head === null`, or an equivalent empty C++ ownership pointer. Operations that assume a node must explicitly handle this state.

A single-node list is important because its head is also its final node. Reversal should leave the node unchanged while its successor remains null.

Deleting the only node must leave an empty list.

Insertion at position zero is a head operation.

Insertion at the current size is a valid append position in the Python and JavaScript indexed insertion methods.

Deletion indexes must be strictly less than the current size.

Duplicate values require a precise policy. The implementations distinguish between deleting the first matching value and deleting every matching value.

A corrupted list containing a cycle is especially dangerous because ordinary traversal expects eventually to reach a null successor. The integrity checks demonstrate how Floyd's algorithm can detect such corruption with constant auxiliary space.

## Common Implementation Errors

A frequent insertion error is changing the predecessor's `next` reference before saving the successor. The original remainder of the list can become inaccessible.

A frequent deletion error is forgetting that head deletion has no predecessor.

Another common error is failing to update the list's size after insertion or deletion. This creates a structural invariant mismatch even when the links appear correct.

Reversal commonly fails when the current node's original successor is not saved before `current.next` is redirected.

Search implementations can accidentally skip the final node if the traversal condition is written incorrectly.

Recursive reversal can appear to use constant memory because the algorithm does not allocate explicit node storage, but each recursive invocation consumes stack space. Large lists can therefore make recursive reversal less robust than its iterative counterpart.

In C++, copying ownership pointers during node manipulation is another serious error. `std::unique_ptr` is intentionally non-copyable. Ownership must be transferred with moves.

## Validation and Debugging

A useful linked-list debugging strategy is to inspect the sequence of values and the successor relationship separately.

For a small structure:

`A -> B -> C -> null`

verify that:

- the head refers to A
- A points to B
- B points to C
- C points to null
- the recorded size is three

When a deletion produces incorrect output, inspect the predecessor and removed node before and after the link change.

When reversal produces a truncated list, check whether the original successor was preserved before redirecting the current node.

When traversal never terminates, suspect a cycle. Floyd's algorithm is useful because it detects cycles without requiring a separate set containing every visited node.

## Security and Reliability Considerations

A linked list does not inherently provide security. It is a data structure, so security properties depend on the surrounding application.

Untrusted indexes should be validated before traversal or modification. Negative or excessively large indexes should not be allowed to cause undefined behavior or accidental memory access.

C++ implementations require particular attention to ownership and lifetime. Manual memory management can create leaks, double deletion, or use-after-free bugs. The case study uses `std::unique_ptr` to establish explicit ownership and reduce these risks.

A corrupted pointer relationship in a low-level linked-list implementation can make traversal unsafe. Defensive validation is therefore useful in systems where the structure can be modified by multiple components.

The C++ case study also avoids using raw pointers as owners. Raw pointers are used only as temporary observers into nodes whose lifetime remains controlled by `unique_ptr`.

## Practical Trade-offs

A singly linked list is appropriate when sequential access is natural and structural insertion or deletion near a known node is important.

It is less suitable when an application frequently asks for arbitrary indexed elements. An array or vector can provide direct indexing, while a singly linked list must traverse from the head.

A linked list can be useful when elements should be connected through explicit successor relationships and when moving elements does not require shifting a contiguous block.

The absence of backward links is both a defining property and a limitation. Reverse traversal is not directly available, and finding a predecessor requires starting from the head and walking forward.

A tail pointer can improve append performance but introduces another invariant to maintain. A doubly linked list can improve predecessor access but requires additional links and more mutation rules.

## Relationship Between the Operations

Traversal is the basic mechanism from which search, indexed access, and many forms of update, insertion, and deletion are constructed.

Insertion and deletion modify topology. They change which node follows which.

Updating changes payload without changing topology.

Searching examines payload without changing topology.

Reversal changes the topology of every adjacent relationship while preserving the nodes and their values.

Understanding this distinction makes the implementation easier to reason about: operations that only inspect nodes have different failure modes from operations that modify links, and local link changes must preserve access to the rest of the structure.

## Files in This Learning Artifact

The Python implementation is a complete executable linked-list library and demonstration program. It combines the core operations with edge-case handling, integrity checks, complexity output, and executable assertions.

The JavaScript implementation presents the same fundamental data structure through JavaScript object references and a generator-based traversal interface. It also demonstrates runtime error handling and cycle detection.

The C++ implementation uses a repository-change-history scenario to show how singly linked lists can represent structured domain records. Its primary technical distinction is explicit memory ownership through `std::unique_ptr`, including ownership-safe deletion and reversal.

All three programs keep the essential singly linked-list invariant visible: each node has at most one successor, and the terminal node has no successor.
