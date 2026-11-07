# Advanced Binary Search Tree Problems

## Technical Scope

This project implements advanced Binary Search Tree (BST) operations using Python, JavaScript, C++17, Java 17, and PostgreSQL.

The implementations cover:

- Kth smallest and kth largest element retrieval.
- BST construction from sorted values.
- BST construction from preorder traversal.
- Lowest Common Ancestor (LCA).
- Tree height and balance evaluation.
- Reconstruction and rebalancing.
- Conversion of a BST into a sorted doubly linked list.
- Range-based retrieval.
- Structural validation.
- Duplicate handling and invalid-input detection.

The five implementations use different engineering approaches while preserving the same fundamental BST ordering rules.

## 1. Binary Search Tree Fundamentals

A Binary Search Tree is a binary tree in which each node follows an ordering invariant.

For a node with key `x`:

- Every key in its left subtree is smaller than `x`.
- Every key in its right subtree is greater than `x`.
- The same rule applies recursively to both subtrees.

The implementations use unique integer keys. Duplicate keys are rejected rather than inserted as separate nodes.

### Example structure

A BST containing `50, 30, 70, 20, 40, 60, 80` has the following structure:

                    50
               /        \
             30          70
            /  \        /  \
          20    40    60    80

The ordering invariant makes it possible to eliminate irrelevant subtrees during searching.

### Complexity

Let `h` represent tree height and `n` represent the number of nodes.

| Operation | Average case | Worst case |
|---|---:|---:|
| Search | O(log n) | O(n) |
| Insert | O(log n) | O(n) |
| Delete | O(log n) | O(n) |
| Minimum | O(log n) | O(n) |
| Maximum | O(log n) | O(n) |
| Kth smallest | O(h + k) in general | O(n) |
| LCA | O(h) | O(n) |
| Inorder traversal | O(n) | O(n) |
| Height calculation | O(n) | O(n) |
| Balance evaluation | O(n) | O(n) |
| Balanced reconstruction | O(n) | O(n) |
| Doubly linked list conversion | O(n) | O(n) |

The average-case search complexity assumes reasonably distributed insertion patterns. An ordinary BST does not automatically maintain balance.

## 2. Kth Smallest and Kth Largest

### Kth smallest

The kth smallest problem identifies the element occupying position `k` in ascending order.

The key observation is that inorder traversal of a valid BST produces sorted keys.

For the example tree:

| Position | Key |
|---:|---:|
| 1 | 20 |
| 2 | 30 |
| 3 | 40 |
| 4 | 50 |
| 5 | 60 |
| 6 | 70 |
| 7 | 80 |

The third smallest key is `40`.

The implementation uses an explicit stack:

1. Traverse left until the current node has no left child.
2. Remove the next node from the stack.
3. Increment the visited-node counter.
4. Return the key when the counter reaches `k`.
5. Continue through the right subtree.

The traversal stops immediately after finding the required element.

### Kth largest

Kth largest uses reverse inorder traversal.

The traversal order becomes:

`80, 70, 60, 50, 40, 30, 20`

The second largest key is `70`.

### Validation

The implementation rejects:

- `k = 0`.
- Negative positions.
- Positions greater than the number of nodes.
- Non-integer rank values where the language supports such distinctions.

The operation must also handle an empty tree.

### Performance consideration

A standard inorder traversal may examine only the nodes required to reach the requested position. Its auxiliary stack requires O(h) memory.

For systems that perform frequent rank queries, subtree-size metadata can be stored in every node.

A node can maintain:

`subtree_size = 1 + left_subtree_size + right_subtree_size`

This enables kth-element retrieval in O(h) time without visiting all preceding elements.

The supplied implementations use traversal-based rank retrieval to keep structural maintenance simple.

## 3. BST Construction

Construction determines the initial arrangement of nodes while preserving the BST invariant.

### Construction from arbitrary insertion sequences

Inserting keys individually produces a valid BST.

For example:

`50, 30, 70, 20, 40, 60, 80`

produces a balanced-looking structure.

The insertion order matters.

Inserting:

`10, 20, 30, 40, 50, 60, 70`

produces a right-skewed tree:

    10
      \
       20
         \
          30
            \
             40
               \
                50
                  \
                   60
                     \
                      70

The tree remains a valid BST, but its height becomes proportional to its node count.

### Construction from sorted values

When values are already sorted, balanced construction can be achieved by selecting the middle element as the root.

For an interval from `start` to `end`:

1. Calculate the middle position.
2. Create a node containing the middle value.
3. Construct the left subtree using the preceding interval.
4. Construct the right subtree using the following interval.

The process continues recursively.

This produces a tree with height O(log n) when the input contains distinct sorted values.

The construction requires O(n) time because every input value becomes exactly one node.

The implementations reject duplicate or unsorted input.

### Construction from preorder traversal

Preorder traversal follows:

`Root → Left → Right`

A valid preorder sequence contains enough ordering information to reconstruct a unique-key BST.

The reconstruction algorithm maintains lower and upper bounds for every subtree.

A value can become a node only when it belongs to the current permitted interval.

For example:

`50, 30, 20, 40, 70, 60, 80`

is a valid preorder sequence.

The implementation rejects sequences that cannot represent a BST preorder traversal.

This approach constructs the tree in O(n) time when each value is processed once.

## 4. Lowest Common Ancestor in a BST

The Lowest Common Ancestor of two nodes is the deepest node that is an ancestor of both.

For keys `20` and `40`, the LCA is `30`.

For keys `20` and `80`, the LCA is `50`.

### BST-specific algorithm

The BST ordering property allows the search to follow a single path.

Given keys `a` and `b`:

- If both keys are smaller than the current node, move left.
- If both keys are larger than the current node, move right.
- Otherwise, the current node is the split point and therefore the LCA.

The algorithm requires O(h) time.

### Important distinction

An LCA operation on a general binary tree normally requires a different algorithm because a general binary tree does not enforce key ordering.

The supplied implementations also verify that both requested keys exist before returning an LCA.

This prevents an absent key from producing a misleading result.

## 5. Tree Height and Balance

Tree height measures the longest root-to-leaf path.

The implementations count height using the number of nodes along the path.

Therefore:

- An empty tree has height `0`.
- A tree containing only a root has height `1`.
- A chain of seven nodes has height `7`.

### Balance evaluation

A binary tree is height-balanced when the height difference between its left and right subtrees is no greater than one at every node.

The condition is:

`abs(left_height - right_height) <= 1`

A correct balance evaluation must examine every relevant subtree.

Checking only the root's immediate children is insufficient.

The Python, JavaScript, and Java implementations use recursive height evaluation with early failure.

The C++ implementation applies the same approach through a height-checking function.

The SQL implementation models the tree using relational records and includes tree-height and structural-validation operations. Its relational representation does not automatically maintain AVL or Red-Black balancing.

### Balanced versus self-balancing trees

An ordinary BST and a self-balancing BST are different data structures.

| Feature | Ordinary BST | AVL tree | Red-Black tree |
|---|---|---|---|
| BST ordering | Yes | Yes | Yes |
| Automatic balancing | No | Yes | Yes |
| Rotations | Not required | Used | Used |
| Height guarantee | O(n) worst case | O(log n) | O(log n) |
| Implementation complexity | Lower | Higher | Higher |

The implementations demonstrate rebuilding an ordinary BST into a balanced structure. They do not claim to implement AVL or Red-Black rotation-based maintenance.

## 6. Rebalancing

Rebalancing reconstructs a tree using its existing keys.

The procedure is:

1. Perform inorder traversal.
2. Store the sorted keys.
3. Select the middle key as the new root.
4. Recursively construct the left and right subtrees.
5. Replace the original root.

Example:

An initially skewed tree containing:

`10, 20, 30, 40, 50, 60, 70`

can be rebuilt into:

                    40
                  /    \
                20      60
               /  \    /  \
             10   30  50   70

The sorted key sequence remains unchanged.

### Complexity

| Stage | Time |
|---|---:|
| Inorder traversal | O(n) |
| Construct balanced tree | O(n) |
| Total | O(n) |
| Additional storage | O(n) |

Rebuilding is suitable for occasional optimization of an ordinary BST.

It is less suitable when the application requires continuous insertion and deletion with guaranteed logarithmic complexity.

## 7. BST to Doubly Linked List Conversion

A BST can be converted into a doubly linked list while preserving ascending key order.

A doubly linked list contains two references:

- `prev`: previous node.
- `next`: next node.

The conversion uses inorder traversal.

For every visited BST node:

1. Create a new list node containing the key.
2. Connect the previous list node through `next`.
3. Connect the new node through `prev`.
4. Update the tail pointer.

For the example BST, the result is:

`20 ⇄ 30 ⇄ 40 ⇄ 50 ⇄ 60 ⇄ 70 ⇄ 80`

The resulting list supports traversal in both directions.

### Implementation decision

The Python, JavaScript, and Java versions create independent list nodes.

The C++ version uses explicitly managed list-node memory and move-only ownership for the converted list.

The conversion does not modify the original BST.

This avoids losing the tree structure and makes both representations available simultaneously.

### Complexity

- Conversion time: O(n).
- Additional memory: O(n).
- Forward traversal: O(n).
- Reverse traversal: O(n).

An alternative in-place conversion can reuse the original BST node pointers. That approach saves additional node allocations but destroys the original tree structure and requires careful pointer management.

## 8. Range Search

Range search retrieves every key between a lower and upper boundary.

For the interval `[30, 70]`, the result is:

`30, 40, 50, 60, 70`

The algorithm uses BST ordering to avoid unnecessary traversal.

- If the current key exceeds the lower bound, the left subtree may contain qualifying keys.
- If the current key falls inside the interval, it is included.
- If the current key is smaller than the upper bound, the right subtree may contain qualifying keys.

The implementation returns values in ascending order.

The worst-case complexity is O(n), while balanced trees generally reduce the traversal work substantially.

## 9. Implementation Architecture

### Python

The Python implementation uses:

- `dataclasses` for node and conversion-result structures.
- Classes for BST state and operations.
- Iterative inorder and reverse-inorder traversal.
- Recursive construction and validation.
- Explicit exceptions for invalid rank and tree operations.
- Assertions for automated testing.

The tree maintains a separate node count, which is checked against the actual structure during validation.

The script also includes examples of empty trees, duplicate insertion, invalid preorder sequences, and skewed-tree reconstruction.

### JavaScript

The JavaScript implementation emphasizes event-driven behavior.

Its main components include:

- ES classes for tree and node structures.
- `EventEmitter` for insertion, deletion, and rebalancing events.
- `Set` for duplicate detection during preorder reconstruction.
- Promises and asynchronous operation processing.
- Structured operation objects.
- Explicit error classes.

The `processTreeOperations` function demonstrates processing a sequence of operations asynchronously while retaining a single tree state.

The implementation uses safe-integer validation to avoid precision problems associated with JavaScript's numeric representation.

### C++17

The C++ implementation emphasizes ownership and memory management.

It uses:

- `unique_ptr` for exclusive BST node ownership.
- STL vectors for traversal results.
- STL queues for level-based height calculation.
- Optional bounds for validation.
- Exceptions for invalid operations.
- Move-only ownership for the converted doubly linked list.

The `InventoryIndex` class demonstrates how a BST can support numeric asset identifiers.

The index supports registration, deletion, membership checking, rank-based retrieval, and optimization.

### Java 17

The Java implementation uses an enterprise-oriented domain model.

It includes:

- Immutable records for assets and operation results.
- Enums for asset states and operation outcomes.
- Dedicated exception types.
- A tree service implementation.
- An asset registry maintaining both a BST and a hash-based asset lookup.
- Immutable traversal results.

The asset registry distinguishes between successful registration, duplicate records, missing records, and internal index inconsistencies.

The BST is used for ordered identifier retrieval, while the hash map provides direct asset lookup.

These two structures serve different performance requirements.

### PostgreSQL

The SQL implementation uses a relational representation of a BST.

Its principal entities are:

| Database object | Purpose |
|---|---|
| `bst_tree` | Stores tree metadata |
| `bst_node` | Stores individual tree nodes |
| `bst_tree_root` | Identifies each tree root |
| `bst_linked_list` | Stores converted predecessor and successor relationships |

The `bst_node` table represents the structure using:

- `parent_node_id`
- `left_child_id`
- `right_child_id`
- `node_key`

Composite foreign keys prevent references across different trees.

Unique constraints enforce unique keys within a tree.

Partial indexes prevent a node from occupying multiple left-child or right-child positions in the same tree.

The SQL functions implement insertion, search, rank retrieval, LCA, validation, height calculation, range retrieval, and reporting.

The reconstruction procedure rebuilds a tree from sorted keys.

The linked-list conversion uses PostgreSQL window functions:

- `LAG()` identifies the preceding key.
- `LEAD()` identifies the succeeding key.

These relationships represent a doubly linked list in relational form.

## 10. Important Database Integrity Rules

The relational representation requires more than ordinary foreign keys.

A valid BST must satisfy several conditions:

- Every node belongs to an existing tree.
- Every key is unique within its tree.
- A child belongs to the same tree as its parent.
- A node cannot reference itself.
- Each node has at most one parent.
- A node cannot be both the left and right child of the same parent.
- The root has no parent.
- Every node must satisfy the ordering constraints inherited from its ancestors.
- The structure must not contain cycles.

Some of these conditions are enforced by constraints and triggers.

Global ordering and cycle validation require additional logic because ordinary foreign keys cannot enforce arbitrary recursive tree rules.

For concurrent modifications, the SQL insertion function locks the tree registry row. This serializes insertions into the same tree and protects the search-then-insert workflow.

## 11. Testing and Failure Handling

The implementations test valid operations as well as invalid states.

| Test case | Expected behavior |
|---|---|
| Insert a new key | Successful insertion |
| Insert an existing key | Reject duplicate |
| Search for existing key | Return true |
| Search for absent key | Return false |
| Delete a leaf | Remove leaf |
| Delete a node with one child | Replace with child |
| Delete a node with two children | Use inorder successor |
| Find first smallest element | Return minimum |
| Find last largest element | Return minimum |
| Request rank zero | Reject operation |
| Request rank above tree size | Reject operation |
| Find LCA with absent key | Reject operation |
| Construct from sorted unique values | Build balanced BST |
| Construct from duplicate values | Reject input |
| Construct from invalid preorder | Reject input |
| Rebalance a skewed tree | Preserve keys and reduce height |
| Convert an empty tree | Return empty list |
| Convert a nonempty tree | Preserve sorted order |

The JavaScript implementation additionally tests event notifications and asynchronous operation processing.

The Java implementation tests enterprise registry consistency.

The C++ implementation exercises memory ownership through the converted list.

The PostgreSQL script demonstrates transactional insertion and validation.

## 12. Practical Design Considerations

### Duplicate-key policy

These implementations use unique keys.

This simplifies:

- Searching.
- Rank calculation.
- LCA evaluation.
- Structural validation.
- Balanced reconstruction.

Applications requiring duplicate values can store a frequency counter or a collection of records within each node.

### Recursion depth

Recursive operations are convenient for balanced trees.

A highly skewed BST can create recursion depths proportional to the number of nodes.

For very large or untrusted trees, iterative traversal and explicit stacks reduce the risk of stack exhaustion.

### Concurrent modifications

The in-memory implementations are designed for single-process operation and do not provide thread-safe mutation.

A production service must coordinate concurrent updates through synchronization, immutable snapshots, or transactional storage.

The PostgreSQL implementation uses tree-level locking during insertion, but a production system must also enforce suitable permissions and transaction isolation.

### Security and input validation

BST operations must validate external inputs before modifying tree state.

Relevant controls include:

- Rejecting invalid identifiers.
- Rejecting duplicate keys.
- Validating rank boundaries.
- Preventing cross-tree references.
- Checking structural integrity.
- Restricting database permissions.
- Using parameterized SQL in application integrations.
- Controlling transaction boundaries.

A valid BST structure is not, by itself, a security boundary.

### Performance tradeoffs

An ordinary BST is appropriate when its simplicity is useful and insertion order is reasonably distributed.

For workloads requiring predictable lookup and update performance, self-balancing structures are more suitable.

The choice depends on:

- Dataset size.
- Insertion frequency.
- Deletion frequency.
- Rank-query frequency.
- Required latency.
- Memory constraints.
- Concurrency requirements.
- Whether structural rebuilding is acceptable.

## 13. Final Technical Comparison

| Capability | Python | JavaScript | C++17 | Java 17 | PostgreSQL |
|---|---|---|---|---|---|
| BST insertion | Yes | Yes | Yes | Yes | Yes |
| Deletion | Yes | Yes | Yes | Yes | Not implemented as a public operation |
| Search | Yes | Yes | Yes | Yes | Yes |
| Kth smallest | Yes | Yes | Yes | Yes | Yes |
| Kth largest | Yes | Yes | Yes | Yes | Yes |
| LCA | Yes | Yes | Yes | Yes | Yes |
| Sorted construction | Yes | Yes | Yes | Yes | Through reconstruction |
| Preorder construction | Yes | Yes | Yes | Yes | Not implemented |
| Balance evaluation | Yes | Yes | Yes | Yes | Structural height reporting |
| Rebalancing | Yes | Yes | Yes | Yes | Yes |
| Doubly linked conversion | Yes | Yes | Yes | Yes | Relational representation |
| Range search | Yes | Yes | Yes | Yes | Yes |
| Structural validation | Yes | Yes | Yes | Yes | Yes |
| Automated tests | Yes | Yes | Yes | Yes | Executable SQL examples |

The central distinction across these implementations is between preserving the BST ordering invariant and maintaining an efficient tree shape. A tree can remain logically valid while becoming inefficient. Rank retrieval, LCA, reconstruction, balance evaluation, and representation conversion address different aspects of that problem.
