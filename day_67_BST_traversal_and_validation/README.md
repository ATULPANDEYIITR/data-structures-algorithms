# BST Traversal and Validation

## 1. Technical Scope

A Binary Search Tree (BST) is a node-based data structure that maintains an ordering relationship between its elements.

Each node contains:

- A unique key.
- A reference to its left child.
- A reference to its right child.

For a node with key `K`, the BST ordering invariant is:

- Every key in its left subtree is smaller than `K`.
- Every key in its right subtree is greater than `K`.
- Both child subtrees must independently satisfy the same invariant.

This implementation uses unique integer keys. Duplicate values are rejected rather than stored as separate nodes.

The five implementations demonstrate different approaches to maintaining, querying, validating, and reporting on BST structures.

## 2. BST Structure

A representative tree is:

        50
       /  \
      30   70
     / \   / \
    20 40 60 80

Its inorder traversal produces:

`20, 30, 40, 50, 60, 70, 80`

The ascending output is a consequence of the BST ordering invariant.

### Node relationships

| Component | Meaning |
|---|---|
| Root | Topmost node without a parent |
| Parent | Node directly above another node |
| Left child | Child containing a smaller key |
| Right child | Child containing a greater key |
| Leaf | Node without children |
| Internal node | Node with at least one child |
| Subtree | A node and all its descendants |
| Height | Number of nodes on the longest root-to-leaf path |

An empty tree has height zero.

## 3. Traversal Algorithms

Traversal determines the order in which nodes are visited.

The implementations support four traversal strategies.

### 3.1 Inorder traversal

Visit:

1. Left subtree.
2. Current node.
3. Right subtree.

For a valid BST, inorder traversal produces ascending keys.

This makes inorder traversal useful for:

- Sorted asset identifiers.
- Ordered reporting.
- Exporting unique keys.
- Verifying the BST ordering property.
- Retrieving values in ascending order.

The Python, JavaScript, C++17, and Java 17 implementations use iterative traversal with an explicit stack.

The PostgreSQL implementation uses recursive queries and relational ordering.

### 3.2 Preorder traversal

Visit:

1. Current node.
2. Left subtree.
3. Right subtree.

For the example tree:

`50, 30, 20, 40, 70, 60, 80`

Preorder traversal is useful when a tree's structure must be serialized or reconstructed.

### 3.3 Postorder traversal

Visit:

1. Left subtree.
2. Right subtree.
3. Current node.

For the example:

`20, 40, 30, 60, 80, 70, 50`

Postorder traversal is useful when processing child nodes before their parent, including recursive cleanup and hierarchical dependency processing.

### 3.4 Level-order traversal

Level-order traversal visits nodes one level at a time, from left to right.

For the example:

`50, 30, 70, 20, 40, 60, 80`

It uses a queue rather than a stack.

This traversal is useful for:

- Tree visualization.
- Level-based reporting.
- Breadth-first inspection.
- Measuring tree height.

### Traversal comparison

| Traversal | Data structure | Visit order |
|---|---|---|
| Inorder | Stack | Left, Root, Right |
| Preorder | Stack | Root, Left, Right |
| Postorder | Stack | Left, Right, Root |
| Level-order | Queue | Level by level |

All four traversals visit every reachable node once.

Their time complexity is `O(n)`.

Their auxiliary space complexity is generally `O(h)` for depth-first traversal and `O(w)` for level-order traversal, where:

- `n` is the number of nodes.
- `h` is tree height.
- `w` is maximum tree width.

## 4. BST Validation

A BST must satisfy ordering rules throughout the complete tree.

Checking only immediate parent-child relationships is insufficient.

Consider:

        50
       /  \
      30   70
        \
         60

The node `60` is greater than its immediate parent `30`, but it is located in the left subtree of `50`.

Therefore, the tree is invalid.

### 4.1 Global boundary validation

Each node is evaluated against an allowable lower and upper boundary.

For a node with key `K`:

- The lower boundary must be strictly smaller than `K`.
- The upper boundary must be strictly greater than `K`.

When visiting the left subtree, the upper boundary becomes the current key.

When visiting the right subtree, the lower boundary becomes the current key.

The algorithm uses explicit bounds rather than checking only the immediate parent.

### 4.2 Structural validation

The implementations also check structural properties:

- The number of reachable nodes matches the recorded size.
- No node is visited more than once.
- The ordering invariant holds.
- Empty trees are valid.
- Cyclic or repeated references are rejected where the implementation can represent them.

The Python, JavaScript, C++17, and Java 17 implementations use visited-node tracking.

The PostgreSQL validation function uses recursive traversal and checks reachability, ordering boundaries, root state, and parent-child consistency.

### 4.3 Duplicate-key policy

This project uses a strict BST policy:

`left < root < right`

Consequently, duplicate keys are rejected during insertion.

This avoids ambiguity in floor, ceiling, successor, predecessor, and structural validation operations.

## 5. Minimum and Maximum

The minimum key is the leftmost node.

The maximum key is the rightmost node.

For the example:

| Operation | Result |
|---|---:|
| Minimum | 20 |
| Maximum | 80 |

The search follows one path from the root.

Time complexity:

- Average: `O(log n)` in a reasonably balanced tree.
- Worst case: `O(n)` in a completely skewed tree.

An empty tree has neither a minimum nor a maximum. The application implementations report this condition through exceptions or explicit failure states.

## 6. Floor and Ceiling

Floor and ceiling are boundary-search operations.

They are particularly useful when an exact key is unavailable but the nearest valid key is required.

### 6.1 Floor

The floor of a query value is the largest stored key less than or equal to that value.

For the tree containing:

`20, 30, 40, 50, 60, 70, 80`

Examples:

| Query | Floor |
|---:|---:|
| 15 | No result |
| 20 | 20 |
| 35 | 30 |
| 45 | 40 |
| 50 | 50 |
| 85 | 80 |

The algorithm maintains a candidate whenever it encounters a node smaller than the query.

It then explores the right subtree for a potentially larger valid candidate.

### 6.2 Ceiling

The ceiling of a query value is the smallest stored key greater than or equal to that value.

| Query | Ceiling |
|---:|---:|
| 15 | 20 |
| 25 | 30 |
| 45 | 50 |
| 50 | 50 |
| 75 | 80 |
| 85 | No result |

The algorithm maintains a candidate whenever it encounters a node greater than the query.

It explores the left subtree to find a potentially smaller valid candidate.

Both operations take `O(h)` time.

## 7. Range Queries

A range query retrieves keys within an inclusive interval:

`low <= key <= high`

For the example:

`rangeQuery(30, 70)`

Returns:

`30, 40, 50, 60, 70`

The implementation prunes unnecessary branches.

If a node is smaller than the lower boundary, its left subtree cannot contain a qualifying key.

If a node is greater than the upper boundary, its right subtree cannot contain a qualifying key.

This reduces unnecessary traversal.

The expected complexity in a balanced tree is approximately `O(log n + k)`, where `k` is the number of returned values.

A highly unbalanced tree can require `O(n)` traversal.

Invalid boundaries, where `low > high`, are rejected.

## 8. Successor and Predecessor

Successor and predecessor identify neighboring values in sorted order.

### Successor

The successor is the smallest key strictly greater than the given key.

For key `50`, the successor is `60`.

### Predecessor

The predecessor is the largest key strictly smaller than the given key.

For key `50`, the predecessor is `40`.

These queries differ from ceiling and floor because they use strict comparisons.

| Operation | Comparison |
|---|---|
| Floor | `key <= query` |
| Ceiling | `key >= query` |
| Predecessor | `key < query` |
| Successor | `key > query` |

The implementations search using candidate tracking.

Their time complexity is `O(h)`.

## 9. Insertion and Deletion

### 9.1 Insertion

Insertion starts at the root and compares the new key against each visited node.

- Smaller keys move left.
- Larger keys move right.
- Equal keys cause a duplicate-key error.
- An empty child position becomes the insertion point.

For an unbalanced BST, insertion takes `O(h)` time.

### 9.2 Deletion

Deletion requires three distinct cases.

| Case | Mechanism |
|---|---|
| Leaf node | Remove the node |
| One child | Replace the node with its child |
| Two children | Replace the key with its inorder successor and remove the successor node |

The inorder successor is the smallest node in the right subtree.

It preserves the ordering invariant when used as the replacement.

The implementations update the tree size only after successful deletion.

Deleting a missing key returns a failure result without changing the tree.

## 10. Balanced Construction

Ordinary BST insertion does not guarantee a balanced structure.

Inserting sorted values in ascending order produces a right-skewed tree.

For example:

    10
      \
       20
         \
          30
            \
             40

The height becomes `n`.

A balanced construction method selects the middle element as the root and recursively builds the left and right subtrees.

For sorted values from `1` to `15`, the resulting height is `4`.

### Complexity

| Operation | Complexity |
|---|---|
| Sorted input validation | `O(n)` |
| Balanced construction | `O(n)` |
| Resulting height | `O(log n)` |
| Additional construction space | `O(log n)` recursive stack for balanced input |

The Python, JavaScript, C++17, and Java 17 implementations provide balanced construction from strictly increasing input.

A standard BST is not automatically self-balancing. AVL trees and Red-Black trees provide additional balancing mechanisms and stronger worst-case guarantees.

## 11. Python Implementation

The Python file provides a self-contained BST implementation using:

- `dataclasses` for node representation.
- Type annotations for operation contracts.
- Custom exceptions for duplicate and empty-tree conditions.
- `collections.deque` for level-order traversal.
- Iterative traversal algorithms.
- Iterative BST validation.
- Assertions for automated testing.
- `time.perf_counter()` for basic performance measurements.

### Important design decisions

The Python implementation uses iterative traversals to reduce recursion-related stack risks.

Deletion uses recursive subtree updates, which are straightforward for standard BST deletion but can encounter Python's recursion limit in extremely skewed trees.

The balanced-construction method produces a shallow tree and avoids that issue for the constructed structure.

The performance demonstration compares a randomly inserted tree against a tree constructed from sorted values.

## 12. JavaScript Implementation

The JavaScript file provides an event-driven BST.

It uses:

- Classes and objects for node management.
- `EventEmitter` for operation notifications.
- `Set` for duplicate detection and validation.
- Promises for asynchronous batch insertion.
- Frozen audit-event objects.
- Version tracking for state changes.
- Explicit error classes.

### Event-driven behavior

Every successful insertion and deletion generates an audit event.

An event contains:

| Field | Meaning |
|---|---|
| `action` | Operation performed |
| `key` | Affected key |
| `version` | State-change sequence |
| `timestamp` | Event creation time |

The batch insertion method validates the complete batch before applying changes.

This reduces the likelihood of partial updates caused by predictable validation errors.

An unexpected runtime failure triggers restoration of the original logical tree state.

The event log records the rollback.

The implementation uses safe JavaScript integers to avoid unreliable numeric ordering caused by floating-point precision limits.

## 13. C++17 Implementation

The C++17 program models an enterprise asset index.

It uses:

- `unique_ptr` for automatic node memory management.
- `struct` for node representation.
- `optional` for missing boundary-query results.
- STL containers for traversal and validation.
- `unordered_set` for visited-node tracking.
- `queue` for level-order traversal.
- `set` for batch duplicate detection.
- Exceptions for operational failures.
- Assertions for automated verification.

### Memory management

The implementation uses exclusive ownership of child nodes.

A parent owns its left and right subtrees through `unique_ptr`.

This avoids manual memory allocation and deallocation.

The recursive deletion implementation transfers ownership when replacing a node with a child.

### Batch insertion

Batch input is checked for duplicate keys and conflicts with existing nodes before insertion.

This prevents predictable validation failures from producing partially inserted batches.

The implementation does not claim full exception-safe transactional rollback for allocation failures during insertion.

## 14. Java 17 Implementation

The Java implementation represents an enterprise asset registry.

Its design includes:

- Explicit domain exceptions.
- An `Operation` enum.
- A `RegistryStatus` enum.
- Immutable audit-event records.
- Generic query-result records.
- A BST domain class.
- A registry service.
- Immutable query results.
- Validation and batch insertion.

### Service separation

The `BinarySearchTree` class owns the actual node structure and implements tree operations.

The `RegistryService` exposes business-oriented operations such as:

- Finding an asset floor.
- Finding an asset ceiling.
- Retrieving an asset interval.
- Checking registry health.

This separation keeps domain operations distinct from service-level access.

### Audit behavior

Every successful insertion and deletion creates an audit event.

Each event receives a monotonically increasing sequence number.

Audit history is exposed through an unmodifiable snapshot rather than the mutable internal list.

### Failure handling

The implementation rejects:

- Duplicate asset identifiers.
- Null batch identifiers.
- Invalid range boundaries.
- Invalid sorted input.
- Minimum or maximum requests on an empty registry.

## 15. PostgreSQL Implementation

The PostgreSQL script models the same general domain through relational tables.

The primary schema is `bst_lab`.

### 15.1 Relational structure

The main tables are:

| Table | Purpose |
|---|---|
| `registries` | Stores registry metadata |
| `bst_nodes` | Stores BST nodes and child relationships |
| `registry_roots` | Stores the root node for each registry |
| `bst_audit_log` | Records structural operations |

The node table includes:

- `node_id`
- `registry_id`
- `node_key`
- `parent_node_id`
- `left_child_id`
- `right_child_id`

### 15.2 Integrity constraints

The schema uses:

- Primary keys.
- Foreign keys.
- Composite foreign keys.
- Unique constraints.
- Check constraints.
- Deferred relationship validation.
- Registry-specific indexes.

The composite foreign keys ensure that a node cannot reference a parent or child belonging to a different registry.

The unique constraint on `(registry_id, node_key)` prevents duplicate keys within a registry.

These relational constraints enforce important structural relationships, but they do not independently enforce the complete BST ordering invariant.

The `validate_bst()` function performs the additional structural and ordering checks.

### 15.3 Database functions

The script defines operations for:

| Function | Responsibility |
|---|---|
| `bst_insert()` | Insert a key into the BST |
| `validate_bst()` | Check structural and ordering integrity |
| `bst_inorder()` | Return ascending keys |
| `bst_depth_first()` | Provide preorder or postorder traversal |
| `bst_level_order()` | Return breadth-first traversal |
| `bst_minimum()` | Retrieve the minimum key |
| `bst_maximum()` | Retrieve the maximum key |
| `bst_floor()` | Find the floor |
| `bst_ceiling()` | Find the ceiling |
| `bst_range()` | Retrieve an inclusive range |
| `bst_successor()` | Find the next larger key |
| `bst_predecessor()` | Find the next smaller key |
| `bst_delete()` | Remove a key while updating relationships |

### 15.4 Recursive CTEs

PostgreSQL recursive common table expressions provide a relational mechanism for traversing hierarchical data.

The recursive queries maintain information about:

- Current node.
- Child relationships.
- Traversal depth.
- Traversal path.

Path information is useful for detecting repeated visits and preserving traversal order.

### 15.5 Indexing

The script creates indexes on registry identifiers and node relationships.

The unique constraint on `(registry_id, node_key)` also provides a B-tree index for key lookups.

These indexes support relational filtering and reporting.

A relational database B-tree index is not the same as the manually modeled BST node hierarchy.

PostgreSQL manages its own physical indexes independently of the application-level tree.

### 15.6 Transaction management

The insertion function locks the registry row and root record before modifying the structure.

This helps serialize concurrent updates to the same registry.

Production systems should also use a consistent locking policy for deletion and validation operations.

A full validation performed while concurrent changes are occurring should use an appropriate transaction isolation strategy or acquire the relevant registry lock.

The SQL implementation is an educational relational model rather than a replacement for PostgreSQL's native indexing mechanisms.

## 16. Edge Cases and Failure Conditions

| Condition | Expected behavior |
|---|---|
| Empty tree traversal | Return an empty collection |
| Empty tree minimum | Report an error |
| Empty tree maximum | Report an error |
| Duplicate insertion | Reject the operation |
| Missing search key | Return not found |
| Missing deletion key | Return false |
| Query below minimum | Floor returns no result |
| Query above maximum | Ceiling returns no result |
| Invalid range | Reject the request |
| Single-node tree | All traversals return one key |
| Sorted insertion | May create a skewed tree |
| Invalid BST ordering | Validation fails |
| Unreachable node | Structural validation fails |
| Repeated node reference | Validation fails |
| Unsorted balanced-build input | Reject construction |

## 17. Performance Analysis

Let:

- `n` represent the number of nodes.
- `h` represent tree height.
- `k` represent the number of results returned by a range query.

| Operation | Average balanced BST | Worst-case BST |
|---|---:|---:|
| Search | `O(log n)` | `O(n)` |
| Insert | `O(log n)` | `O(n)` |
| Delete | `O(log n)` | `O(n)` |
| Minimum | `O(log n)` | `O(n)` |
| Maximum | `O(log n)` | `O(n)` |
| Floor | `O(log n)` | `O(n)` |
| Ceiling | `O(log n)` | `O(n)` |
| Successor | `O(log n)` | `O(n)` |
| Predecessor | `O(log n)` | `O(n)` |
| Inorder traversal | `O(n)` | `O(n)` |
| Preorder traversal | `O(n)` | `O(n)` |
| Postorder traversal | `O(n)` | `O(n)` |
| Level-order traversal | `O(n)` | `O(n)` |
| Validation | `O(n)` | `O(n)` |
| Balanced construction | `O(n)` | `O(n)` |

The complexity of a basic BST depends on its height.

A balanced tree has height approximately `log₂(n)`.

A skewed tree can have height `n`.

For systems requiring predictable worst-case lookup performance, an AVL tree, Red-Black tree, or database-managed B-tree may be more appropriate.

## 18. Security and Production Considerations

A production BST implementation should consider the following controls.

### Input validation

- Restrict accepted key types.
- Reject invalid numeric values.
- Enforce unique-key requirements.
- Validate range boundaries.
- Limit batch sizes when input is externally controlled.

### Structural integrity

- Validate node ordering after bulk imports.
- Prevent arbitrary child-reference updates.
- Maintain parent-child consistency.
- Protect root references.
- Use transactions for multi-row database updates.

### Concurrency

A basic in-memory BST is not automatically thread-safe.

Concurrent modifications can corrupt the logical structure unless synchronization is implemented.

Database implementations should lock the relevant registry or use a carefully defined concurrency-control strategy.

### Resource management

Extremely skewed trees can produce excessive traversal depth.

Iterative traversal reduces call-stack consumption.

Balanced construction reduces tree height but does not provide automatic rebalancing after later insertions.

### Auditability

Production systems should record:

- Operation type.
- Registry identifier.
- Affected key.
- Operation timestamp.
- Success or failure status.
- Relevant error details.

Audit records should be protected from unauthorized modification.

### Database limitations

The PostgreSQL implementation explicitly stores BST relationships in relational rows.

This provides a useful model for studying hierarchical relationships, recursive queries, constraints, and transactional updates.

For ordinary database workloads, native indexed columns and PostgreSQL's B-tree indexes are generally preferable to maintaining a manually implemented BST.

## 19. Implementation Comparison

| Feature | Python | JavaScript | C++17 | Java 17 | PostgreSQL |
|---|---|---|---|---|---|
| Node representation | Dataclass | Object | Struct | Class | Relational row |
| Inorder | Yes | Yes | Yes | Yes | Yes |
| Preorder | Yes | Yes | Yes | Yes | Yes |
| Postorder | Yes | Yes | Yes | Yes | Yes |
| Level-order | Yes | Yes | Yes | Yes | Yes |
| Validation | Yes | Yes | Yes | Yes | Yes |
| Minimum/maximum | Yes | Yes | Yes | Yes | Yes |
| Floor/ceiling | Yes | Yes | Yes | Yes | Yes |
| Range queries | Yes | Yes | Yes | Yes | Yes |
| Successor/predecessor | Yes | Yes | Yes | Yes | Yes |
| Insertion/deletion | Yes | Yes | Yes | Yes | Yes |
| Balanced construction | Yes | Yes | Yes | Yes | Not implemented |
| Audit events | No | Yes | No | Yes | Yes |
| Batch validation | Yes | Yes | Yes | Yes | Transactional insertion |

## 20. Practical Applications

BST traversal and validation techniques are applicable to:

- Ordered asset registries.
- Numeric identifier indexes.
- Hierarchical inventory systems.
- Range-based record retrieval.
- Scheduling and boundary searches.
- Ordered event processing.
- In-memory lookup structures.
- Data integrity verification.
- Hierarchical relational data processing.

The central engineering consideration is maintaining the ordering invariant while supporting efficient updates and queries.

A BST provides efficient operations when its height remains controlled. Its validation mechanism verifies correctness, while its traversal and boundary-search operations make ordered data accessible.
