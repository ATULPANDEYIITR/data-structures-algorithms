# Linked List Reversal: Iterative, Recursive, and Reverse-in-Groups

## Scope

This learning artifact focuses on three closely related linked-list operations:

- iterative reversal, where each node's `next` pointer is redirected while traversing the list once;
- recursive reversal, where the same pointer transformation is expressed through recursive stack frames;
- reverse-in-groups, where consecutive complete groups of `k` nodes are reversed while an incomplete final group remains unchanged.

The implementations deliberately distinguish the algorithmic mechanism from the language-specific implementation model. Python emphasizes executable pointer manipulation and randomized validation. JavaScript adds event-driven and asynchronous experiment patterns. C++ models a non-trivial change-list case study with explicit memory ownership. Java models a typed enterprise review-change domain and integrates reversal with policy evaluation. PostgreSQL represents linked-list adjacency relationally and uses recursive CTEs, window functions, constraints, indexes, and transactions to inspect and record reversal behavior.

## Core Linked-List Model

A singly linked list contains nodes in which each node stores a payload and a reference to the next node.

Conceptually:

`head -> A -> B -> C -> D -> null`

The important structure is the edge between nodes. Reversal does not require changing the payload values. It changes the direction of those edges:

`head -> D -> C -> B -> A -> null`

The original head becomes the new tail because its `next` pointer eventually becomes `null`.

The central invariant during iterative reversal is:

`previous -> reversed prefix`

`current -> first unprocessed node`

`next -> remaining original suffix`

Saving `next` before assigning `current.next = previous` is essential. If the old successor is not saved, the algorithm loses access to the remainder of the list.

## Iterative Reversal

The iterative algorithm uses constant auxiliary pointer storage.

The essential operation is:

`next_node = current.next`

`current.next = previous`

`previous = current`

`current = next_node`

The first assignment preserves the unprocessed suffix. The second reverses the current edge. The last two assignments advance the invariant.

For a list containing `A -> B -> C -> null`, the pointer state evolves conceptually as follows:

| Stage | Reversed prefix | Unprocessed suffix |
|---|---|---|
| Initial | `null` | `A -> B -> C` |
| After A | `A -> null` | `B -> C` |
| After B | `B -> A -> null` | `C` |
| After C | `C -> B -> A -> null` | `null` |

The Python, JavaScript, C++, and Java implementations all perform this pointer transformation directly, although their memory and type systems differ.

### Complexity

Iterative reversal requires `O(n)` time because every node is processed once.

Its auxiliary space requirement is `O(1)` because it needs only a constant number of node references.

This makes iterative reversal preferable when list size can be large or when stack depth must be tightly controlled.

## Recursive Reversal

Recursive reversal expresses the same structural transformation through function calls.

A useful formulation carries two pointers:

`reverse(current, previous)`

The base case is reached when `current` is `null`. At that point `previous` is the new head.

Before changing `current.next`, the original successor is saved. The recursive call then advances into that successor.

The Python and Java implementations demonstrate this accumulator-based formulation. The Python implementation also contains a second recursive formulation that reverses the suffix first and then attaches the current node after its original successor.

The recursive approach is algorithmically `O(n)` in time but requires `O(n)` call-stack space for a list of `n` nodes.

The call stack is not merely an implementation detail. A very large list can exceed the available recursion depth. Python and JavaScript impose runtime-specific recursion limits, while Java and C++ are constrained by available thread stack memory.

For production processing of very large lists, iterative reversal is normally safer when there is no specific requirement for recursive structure.

## Recursive Versus Iterative Pointer Semantics

The two approaches change the same links but organize control flow differently.

| Property | Iterative | Recursive |
|---|---|---|
| Pointer transformation | Explicit loop | Recursive call chain |
| Time | `O(n)` | `O(n)` |
| Auxiliary stack | `O(1)` | `O(n)` |
| Large-list behavior | Strong | Stack-depth dependent |
| State visibility | Local variables | Call frames |
| Implementation risk | Losing saved successor | Excessive recursion depth |
| Best use | Large production lists | Recursive algorithm study or naturally recursive workflows |

The distinction is important: recursion does not make the pointer reversal asymptotically faster. Its primary difference is how execution state is represented.

## Reverse-in-Groups

Reverse-in-groups divides a list into consecutive windows of size `k`.

For:

`1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7`

with `k = 3`, the complete groups are:

`1 2 3`

`4 5 6`

The final node `7` is an incomplete group.

The result is:

`3 -> 2 -> 1 -> 6 -> 5 -> 4 -> 7`

The implementations use the rule that a group must contain all `k` nodes before reversal begins. This prevents a partial final group from being accidentally reversed.

This pre-check is a major correctness condition.

### Why the Group Boundary Matters

Suppose the list is:

`1 -> 2 -> 3 -> 4 -> 5`

with `k = 3`.

The first group becomes:

`3 -> 2 -> 1`

The remaining nodes are:

`4 -> 5`

Because the remaining portion contains fewer than three nodes, it stays:

`4 -> 5`

The result is:

`3 -> 2 -> 1 -> 4 -> 5`

A common implementation error is to reverse whatever nodes remain after the final complete group. That produces a different algorithm.

## Group-Reversal Pointer Structure

The group algorithms introduce a second level of pointer management.

`groupPrevious` identifies the node immediately before the group.

`kth` identifies the final node in the group.

`groupNext` identifies the first node after the group.

During reversal, the first group's successor becomes `groupNext`, allowing the reversed group to connect directly to the untouched suffix.

A sentinel or dummy node simplifies the first-group case because the same linking logic can be used whether the group begins at the original head or later in the list.

The Python, JavaScript, C++, and Java implementations use this technique in their iterative group-reversal methods.

## Python Implementation

The Python implementation defines `Node` and `LinkedList` classes and provides:

- direct iterative reversal;
- accumulator-based recursive reversal;
- a second recursive suffix-based formulation;
- iterative reverse-in-groups;
- recursive reverse-in-groups;
- cycle detection;
- size and tail validation;
- randomized correctness tests;
- edge-case tests;
- recursion-depth considerations.

The validation logic is deliberately tied to linked-list invariants. It checks that the number of reachable nodes equals the stored size, that traversal does not encounter the same node twice, that the stored tail is actually the final reachable node, and that `tail.next` is `None`.

The randomized tests compare linked-list results against array-based reference behavior. This is useful because reversal algorithms are pointer-heavy and can appear correct for one example while failing when the list is empty, has one node, has an incomplete final group, or contains repeated payload values.

## JavaScript Implementation

The JavaScript implementation uses classes and object references for nodes.

Its `SinglyLinkedList` class performs the pointer transformations directly and adds JavaScript-specific behavior around them.

The event-driven demonstration creates a small event mechanism with `on` and `emit`. Reversal starts and completion are represented as events, illustrating how a linked-list operation could participate in a larger Node.js processing pipeline without changing the pointer algorithm itself.

The asynchronous demonstration uses `Promise.all` to run independent reversal experiments as separate promise tasks. The experiments do not share mutable list state, so their execution can be coordinated safely.

JavaScript validation uses `Set` to detect repeated node object references. This distinguishes node identity from node payload equality. Two nodes can legally contain the same value while still being different nodes.

The JavaScript implementation also validates `k` using `Number.isInteger`. This prevents values such as `1.5`, `NaN`, zero, and negative values from silently entering the group-reversal algorithm.

## C++ Case Study

The C++ implementation models a repository change list.

Each node contains a change identifier and a textual change description. The linked list therefore represents an ordered sequence of changes rather than a list of anonymous integers.

The case study demonstrates reversal as a structural operation on an actual domain object:

`change -> change -> change -> null`

The C++ class explicitly owns its dynamically allocated nodes. Its destructor releases every node, while copy construction and copy assignment are disabled to prevent accidental shallow copying of owning raw pointers.

Move construction and move assignment transfer ownership of the head, tail, and size metadata.

The class validates:

- cycle absence;
- actual node count;
- tail consistency;
- tail termination.

The reverse-in-groups operation uses a sentinel node allocated on the stack. This sentinel is not part of the stored list and exists only to make group-boundary manipulation uniform.

The C++ randomized test suite creates hundreds of different list sizes and group sizes and compares linked-list results with vector-based reference results.

This provides a useful systems-level lesson: pointer manipulation can remain `O(1)` in auxiliary space even though the program must still manage object lifetime correctly.

## Java Enterprise Model

The Java implementation treats linked-list nodes as review changes in an enterprise-oriented workflow.

`ChangeNode` models an individual change with a sequence number and description.

`ReviewChangeList` owns the linked structure and provides the reversal operations.

`ReviewDecision` is a record representing a reviewer's decision.

`ReviewStatus` defines explicit review states:

- `OPEN`
- `CHANGES_REQUESTED`
- `APPROVED`

`ReviewPolicy` models merge-related review requirements separately from the linked-list mechanics.

This separation is deliberate. Reversing a changeset is a structural algorithm, while deciding whether a changeset satisfies a review policy is domain logic. Combining both into one conditional-heavy method would make the system harder to validate and change.

The `RepositoryGovernanceService` verifies the list invariants before evaluating the review policy. This demonstrates how a data-structure operation can sit inside a larger typed service architecture without confusing structural behavior with business rules.

The Java program uses immutable `Set.copyOf` for eligible reviewers and stream operations to count distinct valid approvals.

## PostgreSQL Data Model

The SQL implementation represents a linked list through two related tables.

`linked_list` stores list-level metadata.

`list_node` stores individual nodes.

The critical adjacency field is `next_node_id`. It represents the same relationship that a pointer represents in an in-memory linked list.

The `position` field provides a stable logical ordering for demonstration and validation. It should not be confused with the pointer relationship. The pointer relationship is represented by `next_node_id`.

The schema uses:

- primary keys for node and list identity;
- foreign keys for adjacency and ownership;
- uniqueness constraints for list positions;
- check constraints for valid algorithm and group-size combinations;
- indexes on list/position and successor relationships.

## Recursive SQL Traversal

PostgreSQL recursive CTEs can follow the linked structure.

The traversal begins at a head candidate and repeatedly joins the current node to its `next_node_id`.

The recursive queries maintain a `depth` value so the resulting rows expose the traversal order.

The queries also maintain a visited-node array. This provides cycle detection during traversal and prevents a malformed pointer chain from causing unbounded recursive processing.

This is an important distinction from simply sorting by `position`: recursive traversal follows the actual adjacency relationship.

## SQL Representation of Reversal

In an in-memory linked list, iterative reversal changes each node's `next` pointer.

In a relational representation, the equivalent transformation is a reassignment of successor relationships.

For an original chain:

`A -> B -> C -> D -> null`

the reversed successor mapping becomes:

`D -> C -> B -> A -> null`

The SQL examples first inspect the predecessor relationships using `LAG`. This shows which original node becomes the successor of each node after reversal.

The SQL implementation records a reversal operation separately from the original node table. This keeps the demonstration auditable rather than silently destroying the original adjacency representation.

## SQL Reverse-in-Groups

Window functions and integer division provide a relational representation of group boundaries.

For group size `3`, positions are mapped to group numbers using:

`(position - 1) / 3`

PostgreSQL integer division assigns positions `1,2,3` to one group, `4,5,6` to the next, and so forth.

`ROW_NUMBER()` with descending position inside each group provides the reversed order within complete groups.

The incomplete final group is selected separately and retains ascending position order.

This demonstrates an important difference between pointer-oriented and relational implementations: the relational version does not need to physically mutate node pointers to calculate the result. SQL can derive the transformed ordering declaratively.

## Transactional Recording

The SQL script uses a transaction when creating a reversal operation and its result rows.

The operation is inserted into `reversal_operation`.

The calculated output ordering is inserted into `reversal_result`.

The operation is then marked successful.

The transaction ensures that the recorded operation and its results are committed together. If an error occurs before `COMMIT`, PostgreSQL can roll back the incomplete workflow.

This is different from the in-memory algorithms, where pointer mutation happens directly in application memory and persistence is not part of the operation.

## Edge Cases

Empty lists require no pointer changes.

A one-node list is already reversed.

`k = 1` produces no structural change because every group contains only one node.

`k <= 0` is invalid for reverse-in-groups and is explicitly rejected in the Python, JavaScript, C++, and Java implementations.

When `k` exceeds the list length, the iterative group implementations leave the list unchanged because no complete group exists.

When the list length is not divisible by `k`, the final incomplete group remains unchanged.

Cycle detection is important because ordinary traversal assumes termination at `null`. A cycle violates that assumption and can cause infinite traversal.

Repeated payload values are not themselves a problem. Node identity, not value equality, determines whether a cycle exists.

## Common Pointer Errors

A frequent reversal error is assigning `current.next = previous` before saving the original successor. That destroys the only reference to the remaining suffix.

Another error is forgetting to update the list head after the final reversal. The new head is the old tail.

A third error is forgetting to update the tail. After complete reversal, the old head becomes the tail and its `next` must be `null`.

Group reversal introduces another failure mode: reconnecting the reversed group to the wrong successor can disconnect the remainder of the list.

A final common mistake is reversing a short final group when the required semantics specify reversal of complete groups only.

## Validation Strategy

A reliable implementation should validate structure independently of payload values.

Useful invariants include:

`head` is either `null` or reachable.

`tail` is either `null` or the final reachable node.

`tail.next` is `null`.

The number of reachable nodes equals the stored size.

No node is visited twice during traversal.

For reverse-in-groups, every complete group preserves its members while changing only their order, and an incomplete final group preserves its order.

The Python, JavaScript, C++, and Java implementations exercise these invariants after mutations.

The randomized tests are especially useful because pointer algorithms have a large number of boundary conditions relative to their short source code.

## Performance Considerations

Complete reversal is inherently linear because every node's link must be examined or changed.

An iterative implementation performs the transformation in `O(n)` time and `O(1)` auxiliary space.

A recursive implementation performs the same logical work in `O(n)` time but consumes call-stack space.

Reverse-in-groups remains `O(n)` because each node participates in at most one local reversal.

A naive implementation that repeatedly scans ahead to determine group boundaries can accidentally increase constant factors or even produce `O(n²)` behavior if it repeatedly traverses large portions of the list. The implementations avoid this by processing each group in a controlled traversal.

## Language-Level Design Differences

Python's dynamic references make pointer manipulation concise, while explicit validation is needed to detect structural corruption.

JavaScript's object references provide similar pointer semantics, with `Set` useful for identity-based cycle detection. Its event-loop model also makes asynchronous orchestration natural, although asynchronous execution does not improve the complexity of a CPU-bound pointer reversal.

C++ provides deterministic object lifetime and low-level ownership control. The case study therefore makes memory management part of the implementation rather than treating nodes as automatically managed objects.

Java provides stronger static typing, records, enums, immutable collections, and explicit domain classes. This supports separation between linked-list mechanics and enterprise review-policy behavior.

PostgreSQL does not expose pointers as in-memory references. The adjacency relationship is modeled as a foreign key, and recursive CTEs provide a relational mechanism for traversing that graph-like structure.

## Practical Distinction Between the Three Algorithms

Iterative reversal should be understood as direct pointer redirection with an explicit traversal state.

Recursive reversal should be understood as the same pointer redirection expressed through recursive control flow and therefore backed by stack frames.

Reverse-in-groups should be understood as repeated local reversals combined with careful boundary detection and reconnection of neighboring segments.

They share the same underlying linked-list representation, but their control flow and boundary rules are different. Treating them as merely different names for "reverse the list" hides the important correctness conditions.

## Production Considerations

For large production lists, iterative reversal generally provides the most predictable memory behavior.

Recursive reversal is appropriate when recursion is specifically valuable to the surrounding design and input size is controlled.

Group reversal should define its incomplete-final-group behavior explicitly. Reversing incomplete groups and leaving them unchanged are both possible problem variants, but they are not interchangeable.

Mutable linked structures should expose invariant validation during testing even when full validation is too expensive for every production request.

When linked-list state is persisted, database constraints should enforce identity and relationship integrity. Application code should not be the only layer responsible for preventing duplicate logical positions, invalid group configuration, or broken references.

When node ordering is business-significant, preserving an auditable representation of the original and transformed order can be preferable to destructively overwriting the only representation.

## Implementation Coverage

| Deliverable | Primary technical perspective |
|---|---|
| Python | In-place algorithms, validation, edge cases, randomized testing, recursion limits |
| JavaScript | Object references, identity-based validation, events, promises, deterministic randomized tests |
| C++ | Domain-oriented changeset model, pointer ownership, RAII, move semantics, algorithmic testing |
| Java | Typed enterprise domain model, records, enums, immutable policy data, service-level validation |
| SQL | Adjacency schema, recursive CTE traversal, window-function group reversal, constraints, indexes, transactions |

The implementations therefore study the same linked-list problem from different computational perspectives without treating the language implementations as interchangeable source-code translations.
