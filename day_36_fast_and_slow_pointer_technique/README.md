# Fast and Slow Pointer Technique

## Scope

The fast and slow pointer technique is a family of algorithms that moves two references through a sequence at different rates or maintains a fixed distance between two references.

The central linked-list configuration uses:

- `slow` moving one node at a time.
- `fast` moving two nodes at a time.

This simple difference in movement speed produces several important results without storing a visited set or first calculating the complete length of the structure.

The implementations in this artifact focus on middle-element finding, Floyd's cycle detection, cycle-entry identification, cycle removal, fixed-gap searches such as nth-from-end lookup, palindrome detection, intersection detection, and Floyd's duplicate-number technique.

The implementations deliberately distinguish the mathematical idea from the data structure used to demonstrate it. Linked lists expose a `next` relationship directly, while the duplicate-number problem treats array values as transitions in a functional graph.

## Core Pointer Model

For a singly linked list, each node has a value and a reference to its successor.

A normal traversal looks like:

`current = current.next`

The fast and slow technique instead maintains two positions:

`slow = slow.next`

`fast = fast.next.next`

The pointers therefore cover different distances after the same number of loop iterations.

For an acyclic list, `fast` eventually reaches `null`.

For a cyclic list, both pointers remain inside the cycle. Because `fast` gains one node per iteration relative to `slow`, their relative positions eventually coincide.

This is the central mechanism behind Floyd's cycle detection algorithm.

## Why the Technique Saves Space

A visited-set cycle detector can store every node identity that has already been observed. That requires O(n) auxiliary memory.

Floyd's algorithm needs only a constant number of references:

- the slow pointer
- the fast pointer
- temporary references used during entry discovery or removal

Its auxiliary space is therefore O(1).

The time complexity remains O(n) for standard linked-list cycle detection because the pointers traverse a bounded number of nodes before either reaching the end or meeting inside the cycle.

The technique is especially useful when the input structure is large and modifying it to attach metadata to every node is undesirable or impossible.

## Middle Element Finding

The same speed difference solves the middle-node problem.

Consider:

`10 -> 20 -> 30 -> 40 -> 50`

Starting both pointers at the first node and moving slow by one and fast by two causes slow to reach `30` when fast reaches the end.

The Python, JavaScript, C++, and Java implementations expose `middleNode` functions that return the second middle for an even-length list.

For:

`10 -> 20 -> 30 -> 40`

the returned node is `30`.

This convention is important because an even-length sequence has two mathematically central positions. An implementation must define which one it returns.

The implementations also provide a `firstMiddleNode` variant. It initializes the fast pointer one position ahead, causing the slow pointer to stop at the first of the two middle nodes.

This small initialization difference changes the result without changing the overall O(n) time and O(1) auxiliary-space complexity.

## Floyd's Cycle Detection

Floyd's algorithm is based on the observation that two objects moving at different speeds cannot remain separated forever inside a finite cycle.

Suppose a cycle has length `L`.

After both pointers enter the cycle, their relative speed is one node per iteration because:

`fast speed - slow speed = 2 - 1 = 1`

Their positions are therefore equivalent modulo `L`. Eventually their relative displacement becomes zero modulo `L`, causing the pointers to occupy the same node.

The detection condition is therefore:

`slow == fast`

The identity comparison is important. Two different nodes may contain the same value, but a cycle detector needs to determine whether the references identify the same physical node.

The implementations use reference identity in Python, JavaScript, C++, and Java.

## Cycle Detection Versus Cycle Entry

Detecting a meeting point does not immediately identify the first node in the cycle.

For example:

`A -> B -> C -> D -> E`
`         ^         |`
`         |---------|`

The pointers may meet at `D` even though the cycle begins at `C`.

After the first meeting, one pointer is reset to the head while the other remains at the meeting node.

Both then move one node at a time.

Their next meeting point is the cycle entry.

This works because the distance from the head to the cycle entry and the distance traveled from the meeting point around the cycle have the required modular relationship.

The implementations expose this separately as `findCycleEntry`, `cycle_entry_node`, or equivalent functions rather than incorrectly treating the first meeting node as the cycle entry.

## Cycle Geometry

A useful representation of a cyclic linked list is:

`prefix + cycle`

Let:

- `μ` be the number of nodes before the cycle entry.
- `λ` be the cycle length.

The head-to-entry distance is `μ`.

The cycle contains `λ` nodes.

After detecting a meeting, resetting one pointer to the head allows the two one-step pointers to meet at the cycle entry.

The Python, C++, and Java implementations explicitly calculate:

- whether a cycle exists
- the meeting node
- the entry node
- the distance from the head to the entry
- the cycle length

These values are useful when debugging pointer algorithms because they expose the actual geometry of the structure instead of returning only a Boolean result.

## Cycle Removal

Cycle detection alone does not repair a linked list.

Once the cycle entry is known, the node immediately preceding the entry within the cycle must be located.

If the entry is `C` and the cycle is:

`C -> D -> E -> C`

then `E` is the cycle tail.

Its `next` reference is changed from `C` to `null`.

The resulting structure becomes:

`... -> B -> C -> D -> E -> null`

The removal implementation does not allocate another collection of nodes.

Its additional space remains O(1).

A critical edge case is a cycle in which the head points to itself. In that situation the entry is the head and the cycle tail is also the head. The same structural rule applies: set its `next` reference to `null`.

## Fixed-Gap Pointer Technique

Fast and slow pointers do not always need a 2:1 speed ratio.

A related pattern keeps two pointers separated by a fixed number of nodes.

For an nth-from-end query, move `fast` ahead by `n` nodes first.

Then move both pointers one node at a time.

When `fast` reaches `null`, `slow` is at the nth node from the end.

For:

`11 -> 22 -> 33 -> 44 -> 55`

a gap of three nodes means that when the fast pointer reaches the end, slow identifies `33`.

This avoids computing the list length in advance.

The same pattern is used by the remove-nth-from-end implementation. A dummy node is placed before the real head so that removing the first node does not require a separate special-case branch.

## Palindrome Detection

A singly linked list palindrome can also use the fast and slow pattern.

The process has three conceptual phases:

- Use fast and slow pointers to locate the midpoint.
- Reverse the second half in place.
- Compare the first half with the reversed second half.

For:

`1 -> 2 -> 3 -> 2 -> 1`

the second half can be reversed and compared against the beginning.

The implementations restore the reversed half before returning.

This restoration is an important production consideration. A function that merely returns the correct Boolean value but silently changes the caller's linked-list structure can introduce difficult downstream bugs.

The palindrome algorithm uses O(n) time and O(1) auxiliary space.

## Intersection of Two Linked Lists

Intersection means physical node identity, not equal values.

Two lists can contain:

`A -> B -> C`

and:

`X -> Y -> C`

where the `C` object is literally the same node.

The pointer-switching technique assigns one pointer to each head.

When a pointer reaches the end of its list, it switches to the other list's head.

Both pointers then traverse the same combined distance.

If the lists intersect, they eventually meet at the first shared node.

If they do not intersect, both become `null` at the same point.

This algorithm does not require list lengths to be calculated explicitly.

## Duplicate Detection as a Functional Graph

Floyd's technique has an important application outside linked-list objects.

Consider an array of `n + 1` integers where every value is in `1..n`.

Because there are more positions than possible values, at least one value is duplicated.

The array can be interpreted as a function:

`index -> values[index]`

Every index therefore has exactly one outgoing transition.

Following those transitions creates a functional graph.

A repeated value causes two traversal paths to merge, which creates a cycle in the resulting representation.

Floyd's algorithm can find the cycle entry, and that entry corresponds to the duplicated value.

For:

`[1, 3, 4, 2, 2]`

the transitions eventually enter a cycle whose entry identifies `2`.

The Python, JavaScript, C++, and Java implementations validate the required value range before applying the algorithm.

The advantage is O(n) time and O(1) auxiliary space, compared with a hash-set solution that uses O(n) additional memory.

The trade-off is that the algorithm depends on the exact mathematical constraints of the duplicate-number problem. It must not be blindly applied to arbitrary arrays.

## Python Implementation

The Python implementation uses a `ListNode` dataclass and explicit functions for each major fast/slow pointer pattern.

`middle_node` demonstrates midpoint discovery.

`has_cycle` performs the basic tortoise-and-hare test.

`cycle_entry_node` separates detection from entry identification.

`remove_cycle` repairs the link after the cycle entry is known.

`nth_from_end` demonstrates the fixed-gap variation.

`is_palindrome` combines midpoint discovery and in-place reversal.

`intersection_node` demonstrates pointer switching between two lists.

`find_duplicate_floyd` models an integer array as a functional graph.

The script also contains executable assertions covering empty lists, singleton lists, even and odd lengths, cyclic and acyclic structures, invalid gap sizes, palindromes, and duplicate-number examples.

The benchmark section demonstrates that the cycle detector uses constant pointer state rather than a visited set.

## JavaScript Implementation

The JavaScript implementation uses object identity for linked-list nodes and optional chaining for concise reporting.

It demonstrates the same family of algorithms but emphasizes JavaScript-specific behavior.

The `Set` in `listToString` is used only by the debugging representation so that printing a cyclic structure cannot loop forever. The actual Floyd cycle detector does not use that set.

The file also contains an asynchronous observation example using Node.js `setImmediate`.

The asynchronous example does not change Floyd's mathematical algorithm. It demonstrates how pointer-state processing can be integrated into an event-driven runtime without confusing asynchronous scheduling with algorithmic parallelism.

Error handling uses exceptions for invalid parameters and a top-level rejection handler establishes a clear process failure path.

## C++ Case Study

The C++ program models a processing event stream.

A `LinkedList` owns its nodes through `std::unique_ptr`, while the nodes themselves maintain raw `next` pointers for the linked structure.

This ownership arrangement separates lifetime management from traversal.

A deliberately corrupted event stream is created by pointing the final event back into the middle of the stream.

The `CycleAnalysis` structure records the detected state, meeting node, cycle entry, prefix length, and cycle length.

The repair operation changes only the final pointer of the cycle to `nullptr`.

The case study demonstrates why constant auxiliary memory can be valuable in systems code. A monitoring component does not need to allocate a hash table proportional to the number of events merely to determine whether a pointer chain has become cyclic.

The program compiles under C++17 or later and uses standard-library facilities only.

## Java Enterprise Model

The Java implementation models a generic linked structure using `Node<T>`.

The `CycleState` enum makes the distinction between cyclic and acyclic structures explicit.

`CycleReport<T>` is a Java record that groups the results of cycle analysis without introducing mutable reporting state.

The `LinkedList<T>` class owns node references through an internal collection while exposing linked-node behavior through the `next` reference.

The enterprise example represents an event queue such as:

`ORDER_CREATED -> PAYMENT_AUTHORIZED -> INVENTORY_RESERVED -> ...`

A routing error deliberately introduces a backward reference.

The cycle analysis service identifies the meeting point and entry point, while the repair operation removes the terminal cycle edge.

The generic implementation also demonstrates that the algorithm is based on reference relationships rather than on a specific value type.

## SQL Data Model

The PostgreSQL script models pointer structures relationally.

`pointer_list` represents a logical list.

`pointer_node` stores each node and its `next_node_id`.

The foreign key protects the local referential relationship: a `next_node_id` must identify an existing node or be null.

Indexes support queries by list and position and searches involving `next_node_id`.

`cycle_analysis` stores the result of a Floyd analysis, including:

- cycle state
- meeting node
- entry node
- distance to entry
- cycle length
- analysis timestamp

The SQL implementation deliberately does not pretend that a foreign key can enforce arbitrary graph acyclicity.

A foreign key can verify that a referenced node exists, but it cannot by itself enforce the rule that repeatedly following `next_node_id` must never return to a previously visited node.

Recursive PostgreSQL queries are therefore used to inspect graph traversal and identify repeated nodes.

The transactional repair section updates the terminal edge and changes the persisted analysis state in one transaction.

## Database Traversal Versus Floyd's Algorithm

The SQL recursive traversal and Floyd's algorithm solve related problems through different mechanisms.

A recursive SQL query can maintain a path array and use that array to identify repeated nodes. This is useful for relational inspection and reporting, but the path consumes memory proportional to the traversal depth.

Floyd's algorithm does not maintain that history.

Its central strength is precisely that it detects a cycle through relative pointer movement without explicitly remembering every visited location.

Therefore, a database query that uses a recursive path should not be described as an implementation of Floyd's constant-space algorithm. It is a database-specific method for exposing the same structural property.

## Edge Cases

An empty linked list has no middle node and no cycle.

A single-node acyclic list returns that node as its middle.

A single-node self-cycle has the same node as its cycle entry and its cycle tail.

An even-length list has two middle candidates, so an API must document whether it returns the first or second.

A gap larger than the list length produces no nth-from-end result.

A palindrome implementation that reverses the second half should restore the links when the caller expects the original structure to remain unchanged.

Cycle detection must compare node identity rather than only node values. Equal values do not imply that two nodes are the same object.

The duplicate-number formulation requires its mathematical input constraints. Arbitrary arrays do not automatically satisfy the functional-graph assumptions required by Floyd's duplicate algorithm.

## Common Implementation Errors

Starting `fast` and `slow` with incompatible initialization can change which middle node is returned.

Moving `fast` without checking both `fast` and `fast.next` can cause a null-reference error in languages where dereferencing null is invalid.

Treating the first Floyd meeting point as the cycle entry is incorrect.

Using a value comparison instead of node identity can report a false intersection or false cycle.

Removing `entry.next` instead of finding the node whose `next` points to the entry can corrupt the cycle rather than remove it.

Forgetting to restore the reversed second half of a palindrome list can silently mutate shared data.

Applying Floyd's duplicate algorithm to an array outside its required numeric range invalidates the functional-graph reasoning.

## Performance Characteristics

The standard cycle detector runs in O(n) time and O(1) auxiliary space.

Finding the cycle entry also runs in O(n) time and O(1) auxiliary space.

Removing a detected cycle remains O(n) time because the algorithm may need to traverse the cycle to find its final node.

Middle-node discovery is O(n) time and O(1) auxiliary space.

Nth-from-end lookup is O(n) time and O(1) auxiliary space.

Palindrome detection is O(n) time and O(1) auxiliary space when the second half is reversed in place.

The constant-space property refers to auxiliary algorithmic storage. It does not mean the linked list itself occupies constant memory.

## Security and Reliability Considerations

Pointer algorithms operate directly on structural references, so corrupted references can produce crashes, infinite traversal, or data corruption.

Debugging and logging functions that traverse an arbitrary linked structure should impose a traversal limit or detect repeated nodes. The JavaScript debugging representation demonstrates this principle with a `Set`.

Production systems should validate external data before constructing pointer structures.

When modifying a shared linked structure, mutation should be treated as a state-changing operation. The palindrome implementation demonstrates a safer pattern by restoring the structure after analysis.

For persistent relational data, referential integrity should be enforced by foreign keys while recursive graph invariants should be explicitly validated rather than assumed.

## Relationship Between the Techniques

Middle finding, cycle detection, nth-from-end lookup, palindrome detection, and intersection detection are not separate unrelated tricks.

They are variations of the same broader strategy:

- Use pointer movement to encode information that would otherwise require extra storage.
- Exploit relative speed or relative distance.
- Stop when the pointer relationship reveals the required structural fact.
- Preserve O(1) auxiliary space when the data structure permits it.

The exact pointer initialization and movement rules determine what information is encoded.

Cycle detection relies on relative speed.

Middle finding relies on one pointer covering approximately twice the distance of the other.

Nth-from-end lookup relies on a fixed distance between pointers.

Intersection detection relies on equalizing total traversal distance through head switching.

Palindrome detection combines midpoint discovery with structural reversal.

These mechanisms should be understood separately rather than treated as interchangeable templates.
