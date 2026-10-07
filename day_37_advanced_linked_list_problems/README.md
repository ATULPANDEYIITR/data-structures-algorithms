# Advanced Linked List Problems

This project studies advanced linked-list algorithms through five executable implementations: Python, JavaScript, C++, Java, and PostgreSQL.

The central theme is **pointer topology**. Unlike arrays, linked lists do not provide constant-time random access. Their power comes from the ability to rearrange relationships between nodes by changing links. The advanced problems in this project therefore require careful reasoning about node identity, link ownership, traversal order, mutation, and structural invariants.

The implementations cover:

- intersection of two linked lists
- merging sorted linked lists
- merge sorting an unsorted linked list
- deep-copying a list with random pointers
- flattening a multilevel linked list
- stable partitioning around a pivot
- cycle detection
- reversal in groups of `k`

The implementations intentionally use different technical perspectives in each language rather than reproducing one program mechanically in four languages.

## Core Model

A singly linked list consists of nodes where each node contains a value and a reference to another node.

The essential relationship is:

`node -> next node -> next node -> null`

A node is different from its value. Two nodes may both contain `42` while remaining completely different objects.

This distinction is critical for intersection problems.

If two lists contain:

`A -> 7 -> 8`

and

`B -> 7 -> 8`

they do not necessarily intersect.

They intersect only when both traversal paths eventually reach the **same node object**.

For example:

`A -> 4 -> X -> Y`

`B -> 9 -> 2 -> X -> Y`

Here `X` and `Y` are physically shared nodes. The intersection is `X`.

This is why the implementations use identity comparisons such as Python's `is`, JavaScript's `===`, C++ pointer equality, and Java reference equality with `==`.

## Intersection

The two-pointer intersection algorithm avoids explicitly calculating both lengths.

One pointer starts at the head of the first list and another starts at the head of the second list.

When a pointer reaches the end of its list, it begins traversing the other list.

The effective paths become:

`A + B`

and

`B + A`

If the lists share a tail, the pointers eventually align at the same physical node.

If the lists do not intersect, both pointers eventually become null.

The important condition is identity rather than value equality.

The algorithm runs in `O(m + n)` time and `O(1)` auxiliary space.

A common error is to compare `node.value` instead of the node itself. Equal values are insufficient evidence of intersection.

## Merging Sorted Lists

Merging two sorted linked lists is fundamentally different from sorting an unsorted list.

Suppose the inputs are:

`1 -> 4 -> 7 -> 10`

and

`2 -> 3 -> 8 -> 9`

The merge operation repeatedly selects the smaller current node.

The implementation does not allocate a new node for every output element. Existing nodes are relinked.

The resulting structure is:

`1 -> 2 -> 3 -> 4 -> 7 -> 8 -> 9 -> 10`

The operation takes `O(m + n)` time and `O(1)` auxiliary space.

A dummy node is used as a temporary predecessor. This removes special cases around initialization of the result head.

The comparison uses `<=` when values are equal, which gives the merge a stable behavior with respect to the two input sequences.

## Merge Sort for Linked Lists

Merge sort is particularly suitable for linked lists.

Array-based sorting algorithms often benefit from random access. A linked list cannot access its middle element in constant time. Merge sort does not require random access during merging.

The linked-list implementation uses:

- slow and fast pointers to split the list
- recursive sorting of the two halves
- pointer-based merging

The splitting phase uses a slow pointer and a fast pointer. When the fast pointer reaches the end, the slow pointer is approximately at the midpoint.

The list is physically divided by setting the first half's final `next` reference to `null`.

The two halves are recursively sorted and then merged.

The time complexity is `O(n log n)`.

The recursive implementation requires `O(log n)` call-stack space. The merge itself requires `O(1)` auxiliary node storage.

The key advantage is that no array conversion is necessary.

## Stable Partitioning

Partitioning reorganizes a list around a pivot.

For pivot `3`, the input:

`1 -> 4 -> 3 -> 2 -> 5 -> 2`

becomes:

`1 -> 2 -> 2 -> 4 -> 3 -> 5`

The condition used here is:

- values `< pivot` go into the lower partition
- values `>= pivot` go into the upper partition

The implementation preserves the original relative order inside each partition.

The `2` appearing before `5` remains before the second `2` only according to its original order among nodes belonging to the same partition.

This is a **stable partition**.

Two temporary dummy heads make the operation easier to implement without special cases. The actual data nodes are reused.

The algorithm runs in `O(n)` time and uses `O(1)` auxiliary node storage.

## Random Pointers

A random-pointer list gives each node two relationships:

- `next`
- `random`

The `random` reference may point to any node in the structure, including:

- a previous node
- a later node
- the node itself
- no node

A shallow copy is not sufficient.

If the copied node's `random` reference points to an original node, the copy still depends on the original structure.

A proper deep copy must preserve the topology while ensuring that every copied node belongs to the new structure.

### Interleaving Technique

The Python, JavaScript, C++, and Java implementations use an interleaving strategy.

For:

`A -> B -> C`

the temporary structure becomes:

`A -> A' -> B -> B' -> C -> C'`

This makes the copied version of any original node immediately accessible through `original.next`.

If `B.random` points to `C`, then the copied random reference can be obtained from:

`B.random.next`

which is `C'`.

After all random references are established, the original and copied chains are separated.

The algorithm runs in `O(n)` time.

The additional working space is `O(1)` beyond the memory occupied by the newly created copy nodes.

A hash map from original nodes to copied nodes is often simpler conceptually, but it requires `O(n)` auxiliary space.

## Multilevel Linked Lists

A multilevel doubly linked list introduces a third structural relationship:

- `next`
- `prev`
- `child`

For example:

`1 - 2 - 3 - 4`

with:

`2 -> child -> 5 - 6`

and:

`6 -> child -> 7`

The flattened depth-first order is:

`1 -> 2 -> 5 -> 6 -> 7 -> 3 -> 4`

Flattening must preserve the doubly linked relationships.

When a child list is inserted:

- the parent-to-child relationship is removed
- the child becomes the immediate successor
- the child's `prev` points to the parent
- the child's tail reconnects to the parent's original `next`
- the original `next` node receives the correct `prev`

The implementations use an explicit stack to avoid recursion depth problems.

When both `next` and `child` exist, the original `next` node is saved before the child is traversed.

This is a structural traversal problem rather than a simple value transformation.

## Cycle Detection

A normal singly linked list eventually reaches `null`.

A cyclic list does not.

For example:

`1 -> 2 -> 3 -> 4 -> 5`

can become:

`5 -> 3`

which creates a cycle.

A normal traversal would never terminate.

Floyd's tortoise-and-hare algorithm uses:

- a slow pointer moving one node at a time
- a fast pointer moving two nodes at a time

If a cycle exists, the pointers eventually meet inside the cycle.

To locate the cycle entry, one pointer is moved back to the head. Both pointers then advance one step at a time. Their next meeting point is the cycle entry.

The algorithm requires `O(n)` time and `O(1)` auxiliary space.

This matters for advanced linked-list work because an algorithm that assumes an acyclic structure can otherwise enter an infinite loop.

## Reversal in Groups

The implementations also demonstrate reversing nodes in groups of `k`.

For:

`1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7`

with `k = 3`, the result is:

`3 -> 2 -> 1 -> 6 -> 5 -> 4 -> 7`

The final group is left unchanged when it contains fewer than `k` nodes.

This algorithm demonstrates a common advanced linked-list pattern: a local pointer transformation must preserve access to the rest of the list before links are modified.

The implementation first finds the end of a complete group. It then reverses only that group and reconnects it to the preceding and following portions.

The algorithm runs in `O(n)` time and `O(1)` auxiliary space.

## Python Implementation

The Python program uses `dataclass` node definitions to keep the structural model explicit.

`ListNode` represents ordinary singly linked lists.

`RandomNode` adds a `random` reference.

`MultiNode` represents a multilevel doubly linked structure with `prev`, `next`, and `child`.

The Python implementation demonstrates:

- identity-based intersection with `is`
- in-place reversal
- sorted-list merging
- linked-list merge sort
- stable partitioning
- Floyd cycle detection
- random-pointer deep copying
- multilevel flattening
- group reversal
- randomized merge-sort verification

The randomized verification generates 100 lists, sorts each through the linked-list implementation, and compares the result with Python's built-in sorted sequence.

This provides a lightweight correctness check for pointer-heavy merge-sort logic.

The Python code also protects diagnostic traversal with a limit so that a debugging function does not itself become an infinite loop when supplied with a cyclic list.

## JavaScript Implementation

The JavaScript implementation treats linked-list nodes as mutable objects.

JavaScript's reference semantics make object identity especially visible in the intersection problem.

The intersection implementation therefore compares nodes using `===`.

The random-pointer copy demonstrates a JavaScript-specific practical concern: recursive implementations can become unsafe for deeply nested structures because the JavaScript call stack has finite depth.

The multilevel flattening implementation therefore uses an explicit array as a stack.

The JavaScript program also performs randomized merge-sort verification and demonstrates cycle detection without attempting to print the entire cyclic structure.

The implementation is executable with a modern Node.js runtime and requires no npm packages.

## C++ Case Study

The C++ program presents the algorithms as part of a data-processing case study.

A service receives ordered event batches represented as linked structures. Two processing paths may converge on a shared tail, sorted batches need to be merged, unsorted recovery batches need to be sorted, and hierarchical event records can require flattening.

The C++ implementation uses explicit pointers because pointer identity and link manipulation are central to the problem.

The intersection implementation compares addresses.

The merge and partition operations reuse existing nodes rather than allocating replacement nodes.

The merge-sort implementation uses recursive divide-and-conquer with a slow/fast split.

The random-pointer copy demonstrates temporary topology modification.

The multilevel flattening implementation uses `std::vector` as an explicit stack.

The program also uses assertions and randomized testing to verify sorting behavior.

A C++ ownership decision deserves special attention. Replacing every raw pointer with `std::unique_ptr` is not automatically correct for intersecting lists because two independent heads may intentionally refer to the same shared tail. Ownership and non-owning traversal references must be modeled separately when a production system needs automatic memory management.

## Java Implementation

The Java implementation uses nested final classes for the different node models.

`ListNode` represents singly linked nodes.

`RandomNode` represents nodes with arbitrary random references.

`MultiNode` represents a multilevel doubly linked structure.

`LinkedListAlgorithms` groups pointer transformations, while `ListValidator` separates structural validation and input policy from the algorithms that mutate links.

Java reference equality is important for intersection. The expression `first == second` checks whether two references identify the same node, whereas comparing values would answer a different question.

The random-pointer copy temporarily modifies the original structure and then restores it. This demonstrates why mutation-heavy algorithms require explicit restoration logic.

The multilevel flattening operation uses `ArrayDeque` as an explicit stack, avoiding recursion for potentially deep nesting.

The Java program compiles against Java 17 or later and uses only standard-library classes.

## SQL Data Model

The PostgreSQL implementation represents linked-list topology relationally.

`linked_list` identifies logical lists.

`list_node` stores individual nodes and their structural relationships.

The node table contains:

- `next_node_id`
- `prev_node_id`
- `child_node_id`
- `random_node_id`

These foreign keys represent the pointer relationships found in the in-memory implementations.

`list_head` identifies the starting node of a logical list.

The schema includes indexes on structural foreign keys because pointer traversal and relationship inspection commonly filter or join on those columns.

The intersection example deliberately uses the same physical node identifiers for the shared tail. This is the relational equivalent of two in-memory lists containing references to the same node objects.

Recursive common table expressions are used to traverse `next` relationships.

Window functions validate the ordering of sorted batches.

A transaction demonstrates that structural modifications can be tested and rolled back without permanently altering the sample topology.

The SQL implementation does not pretend that relational tables and memory pointers are identical abstractions. Instead, it models the important structural relationships explicitly and uses database constraints and queries to inspect their integrity.

## Complexity Characteristics

| Operation | Time | Auxiliary Space | Main Technique |
|---|---:|---:|---|
| Intersection | `O(m + n)` | `O(1)` | Two-pointer alignment |
| Merge sorted lists | `O(m + n)` | `O(1)` | Link reuse |
| Merge sort | `O(n log n)` | `O(log n)` recursive stack | Slow/fast split plus merge |
| Stable partition | `O(n)` | `O(1)` | Two output chains |
| Random-pointer copy | `O(n)` | `O(1)` auxiliary | Interleaving |
| Flatten multilevel list | `O(n)` | `O(h)` stack | Depth-first traversal |
| Cycle detection | `O(n)` | `O(1)` | Floyd's algorithm |
| Reverse in groups | `O(n)` | `O(1)` | Local pointer reversal |

For merge sort, the `O(log n)` space refers to recursion depth in the recursive implementations. The merge operation itself does not require an array proportional to the input size.

For multilevel flattening, `h` represents the traversal stack depth rather than the total number of nodes.

## Important Edge Cases

An empty list must return an empty result for operations that preserve emptiness.

A single-node list is already sorted, already flattened, and requires no reversal work.

Two lists can contain identical values without intersecting. Intersection must therefore use node identity.

Two lists can intersect only once in an acyclic singly linked structure because once they share a node, their remaining `next` chain is also shared.

Merging requires both inputs to be sorted. Supplying unsorted lists violates the precondition and does not magically produce a sorted result.

Partitioning needs an explicit rule for values equal to the pivot. The implementations place them in the greater-than-or-equal partition.

A random pointer may be null or may point to the same node. Both cases must be preserved by a deep copy.

A multilevel list can contain child chains much deeper than expected. An explicit stack avoids depending on language recursion limits.

A cyclic list must not be traversed with an ordinary `while current != null` loop without cycle protection.

When reversing groups of `k`, the behavior of a final incomplete group must be defined. The implementations leave that group unchanged.

## Common Pointer Errors

Changing `current.next` before saving the old successor can permanently disconnect the remainder of the list.

Comparing values instead of object identity produces incorrect intersection results.

Forgetting to terminate a temporary partition chain can accidentally preserve stale links and introduce cycles.

During random-pointer copying, assigning `copy.random = original.random` creates a reference into the original structure instead of the copy.

During multilevel flattening, failing to clear `child` leaves a structure that is technically still multilevel even if `next` traversal appears correct.

During doubly linked flattening, updating `next` without updating `prev` produces asymmetric links.

During k-group reversal, losing the pointer to the node after the current group can disconnect the remainder of the list.

Printing a cyclic list without a traversal limit can cause the debugging program to hang even when the actual cycle-detection algorithm is correct.

## Validation and Testing

The implementations contain direct examples as well as randomized sorting verification.

The randomized tests are useful because linked-list sorting failures frequently occur only for specific combinations of:

- duplicate values
- empty input
- one-element input
- already sorted data
- reverse-sorted data
- negative values
- repeated values
- uneven list halves

Structural algorithms should also be tested for invariants.

After merge sort, the output must be nondecreasing.

After a stable partition around `p`, every node before the partition boundary must have a value below `p`, and every node after it must have a value greater than or equal to `p`.

After a random-pointer copy, the copied nodes must not be the original nodes, while the random-reference topology must be equivalent.

After flattening, every node should be reachable through `next` from the head, and the `child` relationships should have been removed.

After reversing a doubly linked list or flattening one, `next` and `prev` should remain mutually consistent.

## Performance and Design Considerations

Linked lists are advantageous when operations primarily manipulate neighboring relationships and when nodes do not need contiguous storage.

They are poor substitutes for arrays when frequent random access is required.

Finding the element at position `k` requires `O(k)` traversal rather than `O(1)` indexing.

Merge sort works well because it avoids random access during the merge phase.

The two-pointer intersection algorithm is efficient because it avoids constructing sets of visited nodes.

The interleaving random-pointer copy avoids an external hash map at the cost of temporarily modifying the original list.

The explicit-stack flattening algorithm uses additional memory proportional to traversal nesting. A recursive implementation may have similar asymptotic behavior but can fail at extreme nesting depths because of call-stack limits.

## Security and Reliability Considerations

Linked-list algorithms are vulnerable to structural corruption rather than traditional input-only errors.

Untrusted or malformed data can contain cycles, self-references, unexpectedly deep nesting, or inconsistent doubly linked relationships.

Production code that receives externally controlled structures should validate structural assumptions before performing algorithms that depend on acyclicity.

Traversal limits are useful for diagnostics and defensive inspection.

Database representations should use foreign keys and constraints where appropriate so that invalid references are rejected at the storage layer.

In concurrent systems, pointer mutation introduces a separate synchronization problem. A list being traversed while another thread modifies its links can produce inconsistent observations, lost updates, or unsafe memory access. The algorithms in these examples are single-threaded and do not claim to provide concurrent modification safety.

## Practical Distinctions

Intersection asks whether two traversal paths share a physical node.

Merging asks how two already ordered sequences can be combined without unnecessarily rebuilding their nodes.

Sorting asks how an unordered linked structure can be ordered efficiently despite the lack of random access.

Random-pointer copying asks how to reproduce arbitrary relationships while creating a completely independent structure.

Flattening asks how hierarchical links can be converted into one traversal sequence while preserving required doubly linked relationships.

Partitioning asks how nodes can be separated by a predicate while optionally preserving their original order inside each group.

These problems share pointer manipulation, but their invariants are different. Treating them as variations of the same operation is a common source of implementation errors.

## Production Considerations

A production implementation should make ownership explicit, define whether algorithms mutate their inputs, document whether cycles are allowed, and specify what happens when preconditions are violated.

For shared structures, memory ownership requires particular care. A shared tail cannot be treated as independently owned by two list objects without risking double deletion or premature reclamation.

For APIs that expose linked-list operations, immutable representations can sometimes be preferable when correctness and concurrency are more important than in-place mutation.

For very large datasets, contiguous structures can outperform linked lists because modern processors benefit from cache locality. The theoretical `O(1)` insertion or pointer manipulation advantage of a linked list does not automatically translate into better real-world performance.

The important engineering decision is therefore not simply whether an operation is theoretically efficient. The representation, memory layout, mutation model, ownership rules, access pattern, and workload all influence the practical result.
