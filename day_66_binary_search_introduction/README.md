# Binary Search Tree Introduction

## 1. Concept and Structure

A Binary Search Tree (BST) is a binary tree that maintains an ordering relationship between the keys stored in its nodes.

Each node contains:

- A key.
- A reference to its left child.
- A reference to its right child.

The BST ordering invariant is:

- Every key in the left subtree is smaller than its parent key.
- Every key in the right subtree is greater than its parent key.
- Both subtrees independently satisfy the same ordering rules.

This implementation uses unique integer keys. Duplicate insertion is rejected rather than creating multiple nodes with the same key.

### Example structure

The demonstration uses the following keys:

`50, 30, 70, 20, 40, 60, 80`

The resulting tree is:

                 50
               /    \
             30      70
            /  \    /  \
           20  40  60  80

The root is `50`. Its left subtree contains smaller values, and its right subtree contains larger values.

The ordering property makes it possible to eliminate part of the search space at each visited node.

## 2. Binary Search Tree Properties

| Property | Description |
|---|---|
| Root | Topmost node |
| Parent | Node directly above another node |
| Child | Node directly connected below its parent |
| Leaf | Node without children |
| Internal node | Node with at least one child |
| Subtree | A node and all its descendants |
| Depth | Number of edges from the root to a node |
| Height | Maximum number of nodes on a root-to-leaf path |
| Minimum | Leftmost node |
| Maximum | Rightmost node |
| Predecessor | Greatest key smaller than a specified key |
| Successor | Smallest key greater than a specified key |

The root has depth zero. The implementations report height as the number of nodes on the longest root-to-leaf path. An empty tree has height zero.

## 3. Search Operation

Searching starts at the root and compares the requested key with the current node.

Three conditions determine the next action:

1. If the requested key equals the current key, the search succeeds.
2. If it is smaller, continue through the left child.
3. If it is greater, continue through the right child.

If the search reaches a missing child, the key does not exist.

For the example tree, searching for `40` follows:

`50 → 30 → 40`

Searching for `65` follows:

`50 → 70 → 60`

The number of comparisons depends on the height and shape of the tree.

## 4. Insertion Operation

Insertion preserves the BST ordering invariant.

The algorithm:

1. Checks whether the tree is empty.
2. Creates the root when no nodes exist.
3. Compares the new key against the current node.
4. Moves left or right according to the comparison.
5. Inserts the new node at the first available child position.
6. Rejects an existing key.

For example, inserting `35` into the demonstration tree follows:

`50 → 30 → 40 → left`

The resulting structure is:

                 50
               /    \
             30      70
            /  \    /  \
           20  40  60  80
              /
             35

Insertion does not automatically rebalance the tree.

## 5. Deletion Operation

Deletion has three structurally distinct cases.

### Case 1: Leaf node

A leaf has no children.

For example, deleting `20` removes the node directly.

Its parent no longer references that child.

### Case 2: Node with one child

The node is replaced by its only child.

For example:

             30
            /
           20
          /
         10

Deleting `20` connects `30` directly to `10`.

The promoted child preserves the ordering relationship.

### Case 3: Node with two children

A node with two children cannot simply be removed without reconnecting its subtrees.

The implementations use the inorder successor.

The inorder successor is the smallest key in the node's right subtree.

The deletion procedure:

1. Find the target node.
2. Enter its right subtree.
3. Follow left children until the minimum node is found.
4. Copy the successor key into the target.
5. Remove the original successor node.

The successor cannot have a left child. It therefore has at most one child, making its physical removal simpler.

An inorder predecessor, which is the maximum key in the left subtree, can also be used.

## 6. Predecessor and Successor

These operations identify neighboring keys in sorted order.

### Predecessor

The predecessor of a key is the greatest existing key strictly smaller than it.

For the ordered values:

`20, 30, 40, 50, 60, 70, 80`

The predecessor of `50` is `40`.

The predecessor of `35` is `30`.

### Successor

The successor of a key is the smallest existing key strictly greater than it.

The successor of `50` is `60`.

The successor of `65` is `70`.

### Important distinction

The implementations calculate the predecessor and successor of a search value even when that value does not exist in the tree.

For example, if the tree contains `20, 30, 40`, the predecessor of `35` is `30`, and its successor is `40`.

If no smaller or larger key exists, the corresponding result is absent.

## 7. Tree Traversal

Traversal determines the order in which nodes are visited.

| Traversal | Visiting sequence | Example |
|---|---|---|
| Inorder | Left, Root, Right | 20, 30, 40, 50, 60, 70, 80 |
| Preorder | Root, Left, Right | 50, 30, 20, 40, 70, 60, 80 |
| Postorder | Left, Right, Root | 20, 40, 30, 60, 80, 70, 50 |
| Level order | Level by level | 50, 30, 70, 20, 40, 60, 80 |

Inorder traversal of a valid BST produces keys in ascending order.

This property is useful for sorted retrieval, validation, and range reporting.

The Python implementation uses an explicit stack for inorder, preorder, and postorder traversal.

The JavaScript implementation also uses iterative traversal.

The C++ implementation demonstrates recursive depth-first traversal.

The Java implementation uses iterative traversal and Java collections.

The SQL implementation uses a recursive common table expression to follow parent-child relationships.

## 8. Complexity Analysis

Let:

- `n` represent the number of nodes.
- `h` represent the height of the tree.

| Operation | Average case | Worst case |
|---|---:|---:|
| Search | O(log n) | O(n) |
| Insertion | O(log n) | O(n) |
| Deletion | O(log n) | O(n) |
| Minimum | O(log n) | O(n) |
| Maximum | O(log n) | O(n) |
| Predecessor | O(log n) | O(n) |
| Successor | O(log n) | O(n) |
| Inorder traversal | O(n) | O(n) |
| Preorder traversal | O(n) | O(n) |
| Postorder traversal | O(n) | O(n) |
| Level-order traversal | O(n) | O(n) |
| Height calculation | O(n) | O(n) |

The logarithmic average-case behavior assumes reasonably balanced insertion patterns. An ordinary BST does not guarantee balance.

### Degenerate tree

Consider inserting sorted keys:

`10, 20, 30, 40, 50`

The resulting tree becomes:

    10
      \
       20
         \
          30
            \
             40
               \
                50

This structure behaves like a linked list.

Its height is `n`, and search, insertion, and deletion can require O(n) time.

Balanced alternatives such as AVL trees and Red-Black trees maintain stronger structural guarantees.

## 9. Python Implementation

The Python file defines:

- `Node`: A dataclass representing an individual node.
- `BinarySearchTree`: The primary tree implementation.
- `insert()`: Adds unique keys.
- `search()`: Locates a key.
- `find_minimum()` and `find_maximum()`: Identify boundary keys.
- `predecessor()` and `successor()`: Find neighboring keys.
- `delete()`: Handles all three deletion cases.
- `inorder()`, `preorder()`, and `postorder()`: Perform depth-first traversal.
- `level_order()`: Performs breadth-first traversal.
- `range_search()`: Retrieves keys within inclusive boundaries.
- `height()`: Calculates tree height.
- `validate()`: Checks ordering and node count.
- `clear()`: Resets the tree.

The implementation uses optional node references and iterative traversal to avoid unnecessary recursion in common operations.

The test suite checks duplicate insertion, missing keys, all deletion cases, predecessor and successor boundaries, invalid key types, and empty trees.

Run the script with Python 3:

`python binary_search_tree.py`

## 10. JavaScript Implementation

The JavaScript implementation uses a class-based model and Node.js event handling.

Its principal components are:

| Component | Responsibility |
|---|---|
| `BSTNode` | Stores key and child references |
| `BinarySearchTree` | Maintains the tree |
| `EventEmitter` | Publishes operation events |
| `search()` | Returns structured search information |
| `rangeSearch()` | Retrieves a bounded set of keys |
| `_record()` | Publishes an operation event |

The implementation uses `Number.isSafeInteger()` to reject unsafe numeric keys.

It also supports a configurable maximum node count.

Operation events contain:

- Operation name.
- Key.
- Current tree size.
- Operation sequence.
- Timestamp.

Consumers can subscribe to these events without modifying the tree implementation.

The event system is useful for audit logging, monitoring, and integration with other application components.

Run with:

`node binary_search_tree.js`

## 11. C++17 Implementation

The C++ implementation models a product catalogue indexed by unique product identifiers.

Its main design decisions are:

- Private node representation.
- `std::unique_ptr` for automatic memory ownership.
- Deleted copy operations to prevent accidental shallow copying.
- Move operations for ownership transfer.
- `std::optional<int>` for operations that may have no result.
- STL vectors for traversal output.
- Exceptions for invalid range requests.

### Memory management

Each node exclusively owns its left and right subtrees.

When a node is removed, `std::unique_ptr` automatically releases its memory.

The deletion implementation transfers subtree ownership instead of manually managing pointers.

This reduces the risk of memory leaks and dangling pointers.

The C++ version uses recursive traversal and deletion. A sufficiently deep, degenerate tree can exhaust the call stack.

Compile with:

`g++ -std=c++17 -O2 -Wall -Wextra -pedantic binary_search_tree.cpp -o bst`

Run with:

`./bst`

## 12. Java 17 Implementation

The Java implementation represents an enterprise employee directory indexed by unique employee identifiers.

Its design uses:

- A `Node` class for internal tree structure.
- A `TreePolicy` interface for configurable constraints.
- `EnterpriseTreePolicy` for capacity validation.
- Records for audit events, search results, and statistics.
- `Optional<Integer>` for absent predecessor, successor, minimum, and maximum results.
- `ArrayDeque` for iterative traversal.
- `Consumer<AuditEvent>` for audit subscribers.
- A custom `BSTException` for capacity failures.

### Enterprise policy

The tree policy separates capacity decisions from the data structure.

The default example allows up to 1,000 nodes.

A caller can provide a different limit without modifying the insertion algorithm.

### Audit events

Tree operations publish structured events.

Audit listener exceptions are isolated so that a logging failure does not interrupt the underlying tree operation.

This is an in-process audit demonstration. It does not provide durable audit storage, distributed synchronization, or tamper-proof logging.

Run with:

`javac --release 17 Main.java`

Then:

`java -ea Main`

Assertions must be enabled using `-ea` for the test assertions to execute.

## 13. PostgreSQL Implementation

The SQL implementation represents a BST using relational tables.

### Relational model

The database contains two primary tables.

**tree_registry**

Stores independent tree definitions.

Important attributes:

- `tree_id`: Primary key.
- `tree_name`: Unique tree name.
- `description`: Tree purpose.
- `created_at`: Creation timestamp.

**tree_nodes**

Stores the individual nodes.

Important attributes:

- `node_id`: Unique node identifier.
- `tree_id`: Reference to the owning tree.
- `node_key`: Integer value represented by the node.
- `parent_id`: Parent node reference.
- `position`: `LEFT`, `RIGHT`, or `NULL` for the root.
- `created_at`: Creation timestamp.

### Parent-child representation

A root node has:

- `parent_id = NULL`
- `position = NULL`

A left child has:

- A valid parent identifier.
- `position = LEFT`
- A smaller key than its parent.

A right child has:

- A valid parent identifier.
- `position = RIGHT`
- A greater key than its parent.

The composite foreign key ensures that a parent belongs to the same tree.

The unique constraints prevent duplicate keys within a tree and multiple children occupying the same parent position.

A partial unique index restricts each tree to one root.

### Database operations

The SQL script implements:

| Function | Purpose |
|---|---|
| `create_tree()` | Creates an independent tree |
| `bst_insert()` | Finds and inserts a node |
| `bst_search()` | Searches for a key |
| `bst_extreme()` | Finds minimum or maximum |
| `bst_predecessor()` | Finds the predecessor |
| `bst_successor()` | Finds the successor |
| `bst_delete()` | Deletes a node |
| `bst_range()` | Retrieves an inclusive key range |
| `validate_tree()` | Checks reachability and ordering |

The `validate_bst_node()` trigger checks insertion boundaries against the parent and its ancestors.

Direct structural updates are prohibited by the trigger. Structural modifications are performed through the supplied functions.

### Recursive queries

The `bst_inorder` view uses a recursive CTE to navigate the tree.

It builds a traversal path and exposes node depth.

The recursive statistics query calculates:

- Total reachable nodes.
- Maximum tree depth.
- Tree height.

### Transaction handling

The SQL script demonstrates a savepoint, successful modifications, validation, and rollback.

This allows multiple tree changes to be treated as one transaction.

The deferred unique constraint permits the temporary key exchange required by two-child deletion.

### Database concurrency

A production deployment should serialize structural modifications to the same tree.

Concurrent insertion or deletion can otherwise encounter conflicting decisions about the same child position.

A practical implementation can acquire a transaction-level advisory lock using the tree identifier before performing structural changes.

The supplied SQL demonstrates the data model and operations but does not implement that complete concurrent-write locking policy.

## 14. Technical Distinctions

### BST versus Binary Tree

A binary tree limits each node to at most two children.

A BST imposes an additional ordering invariant.

Therefore, every BST is a binary tree, but not every binary tree is a BST.

### BST versus Balanced BST

An ordinary BST preserves key ordering but does not control its height.

A balanced BST applies additional structural rules to prevent excessive height.

### Predecessor versus Parent

A predecessor is defined by key ordering.

A parent is defined by the physical tree structure.

The predecessor is not necessarily the parent or the immediate left child.

### Successor versus Right Child

The successor is the smallest key greater than the current key.

It may be the leftmost descendant of the right subtree rather than the direct right child.

### Inorder Traversal versus Search

Inorder traversal visits every node in sorted order.

Search follows one path and can avoid examining most of the tree.

Both use the same BST ordering property, but their purposes and complexity differ.

## 15. Validation and Failure Conditions

The implementations handle the following situations:

| Condition | Expected behavior |
|---|---|
| Empty tree search | Returns not found |
| Empty tree minimum | Returns no result |
| Empty tree maximum | Returns no result |
| Duplicate insertion | Rejects the insertion |
| Missing-key deletion | Returns false |
| Missing predecessor | Returns no result |
| Missing successor | Returns no result |
| Invalid range | Raises an error |
| Invalid Python key | Raises a type error |
| Unsafe JavaScript integer | Rejects the key |
| C++ empty minimum | Returns an empty optional |
| Java capacity exceeded | Raises a domain exception |
| Invalid database parent | Rejects the operation |
| Duplicate database key | Violates uniqueness |
| Invalid database ordering | Trigger rejects insertion |

The ordering validation must check complete subtree boundaries, not merely compare each node with its immediate parent.

For example, a node placed in the right subtree of `50` must remain greater than `50`, even if its immediate parent is `70`.

## 16. Practical Applications

BSTs are useful when an application needs ordered key retrieval and frequent search operations.

Examples include:

- Product identifier indexing.
- Employee identifier lookup.
- In-memory ordered collections.
- Range retrieval.
- Ordered record processing.
- Predecessor and successor queries.
- Educational models of search-tree algorithms.

The product catalogue and employee directory examples use integer identifiers as keys. A real application would normally store the associated product or employee record separately and use the BST as an index.

## 17. Security and Production Considerations

An ordinary BST is not automatically suitable for every production indexing workload.

Important considerations include:

- Validate incoming keys before modifying the structure.
- Reject duplicate identifiers consistently.
- Limit the number of stored nodes where memory usage must be controlled.
- Avoid exposing internal node references to untrusted callers.
- Protect database structural operations through controlled functions and permissions.
- Use transactions for multi-node changes.
- Serialize concurrent structural writes.
- Monitor tree height to detect degeneration.
- Consider balanced trees for unpredictable or adversarial insertion sequences.
- Use database-native indexes when persistent relational query performance is the primary requirement.

The implementations are educational BSTs, not replacements for production-grade balanced database indexes.

## 18. Implementation Comparison

| Feature | Python | JavaScript | C++17 | Java 17 | PostgreSQL |
|---|---|---|---|---|---|
| Node representation | Dataclass | Class | Struct | Class | Relational row |
| Memory management | Automatic | Garbage collection | Unique ownership | Garbage collection | Database managed |
| Duplicate handling | Reject | Reject | Reject | Reject | Unique constraint |
| Search | Iterative | Iterative | Iterative | Iterative | PL/pgSQL |
| Insertion | Iterative | Iterative | Iterative | Iterative | PL/pgSQL |
| Deletion | Successor replacement | Successor replacement | Ownership transfer | Successor replacement | Key exchange and promotion |
| Traversal | Iterative | Iterative | Recursive | Iterative | Recursive CTE |
| Validation | Ordering and count | Ordering and count | Ordering | Ordering and count | Reachability and ordering |
| Additional capability | Range search | Event emission | Ownership safety | Policy and audit events | Transactions and constraints |

Each implementation preserves the same central BST ordering invariant while using the capabilities and design conventions of its respective environment.
