# AVL Trees: Self-Balancing Binary Search Trees

## 1. Technical Scope

An AVL tree is a self-balancing binary search tree (BST). It maintains the binary search tree ordering property while controlling the height of every subtree.

The structure was introduced by Georgy Adelson-Velsky and Evgenii Landis.

A conventional binary search tree can become skewed when keys are inserted in sorted order. In that situation, searching may require traversing almost every node.

An AVL tree corrects excessive height differences through rotations.

The implementations in this project demonstrate:

- Binary search tree ordering.
- Node heights and balance factors.
- LL, RR, LR, and RL rotations.
- Insertion and deletion.
- Searching and range retrieval.
- Tree traversal.
- Structural validation.
- Operation statistics.
- Relational representation and persistence.

## 2. Binary Search Tree Fundamentals

A binary search tree stores keys according to an ordering rule.

For every node:

- Keys in the left subtree are smaller than the node key.
- Keys in the right subtree are larger than the node key.
- Both subtrees independently satisfy the same ordering property.

Example:

             50
            /  \
           30   70
          / \   / \
         20 40 60 80

An in-order traversal produces:

`20, 30, 40, 50, 60, 70, 80`

The sorted output demonstrates the BST ordering property.

### 2.1 Unbalanced BST behavior

Consider inserting:

`10, 20, 30, 40, 50`

A conventional BST may become:

    10
      \
       20
         \
          30
            \
             40
               \
                50

The tree behaves similarly to a linked list.

Its height becomes proportional to the number of stored elements.

An AVL tree performs rotations to prevent this structural degradation.

## 3. Node Height and Balance Factor

### 3.1 Height

The height of a node is the number of edges on the longest downward path to a leaf.

The implementations use the following convention:

| Node state | Height |
|---|---:|
| Empty subtree | 0 |
| Leaf node | 1 |
| Parent of a leaf | 2 |

The height formula is:

\[
H(v)=1+\max(H(v_L),H(v_R))
\]

Where:

- \(v\) represents the current node.
- \(v_L\) represents its left child.
- \(v_R\) represents its right child.

### 3.2 Balance factor

The balance factor measures the difference between the heights of the left and right subtrees.

\[
BF(v)=H(v_L)-H(v_R)
\]

An AVL node must satisfy:

\[
BF(v)\in\{-1,0,1\}
\]

| Balance factor | Interpretation |
|---:|---|
| -1 | Right subtree is taller by one |
| 0 | Both subtrees have equal height |
| +1 | Left subtree is taller by one |
| Less than -1 | Right-heavy imbalance |
| Greater than +1 | Left-heavy imbalance |

The balance factor is recalculated when insertion or deletion changes subtree heights.

## 4. AVL Rotations

A rotation changes the local structure of a tree while preserving its binary search tree ordering.

Four imbalance cases are important.

### 4.1 LL Rotation: Left-Left

An LL imbalance occurs when insertion into the left subtree of the left child makes the ancestor too left-heavy.

Before:

        30
       /
      20
     /
    10

Operation: Right rotation at 30.

After:

        20
       /  \
      10   30

The rotation promotes the left child and transfers its right subtree to the former root's left position.

### 4.2 RR Rotation: Right-Right

An RR imbalance occurs when insertion into the right subtree of the right child makes the ancestor too right-heavy.

Before:

    10
      \
       20
         \
          30

Operation: Left rotation at 10.

After:

        20
       /  \
      10   30

The right child becomes the new subtree root.

### 4.3 LR Rotation: Left-Right

An LR imbalance occurs when insertion into the right subtree of the left child makes the ancestor left-heavy.

Before:

        30
       /
      10
        \
         20

Two operations are required:

1. Left rotation at 10.
2. Right rotation at 30.

After:

        20
       /  \
      10   30

This is a double rotation.

### 4.4 RL Rotation: Right-Left

An RL imbalance occurs when insertion into the left subtree of the right child makes the ancestor right-heavy.

Before:

    10
      \
       30
      /
     20

Two operations are required:

1. Right rotation at 30.
2. Left rotation at 10.

After:

        20
       /  \
      10   30

### 4.5 Rotation comparison

| Case | Imbalance direction | First rotation | Second rotation |
|---|---|---|---|
| LL | Left-left | Right | None |
| RR | Right-right | Left | None |
| LR | Left-right | Left | Right |
| RL | Right-left | Right | Left |

Single rotations are used for LL and RR cases. Double rotations are used for LR and RL cases.

## 5. AVL Insertion

Insertion follows the binary search tree ordering property.

The process is:

1. Start at the root.
2. Compare the incoming key with the current key.
3. Move left when the incoming key is smaller.
4. Move right when it is larger.
5. Insert a new leaf at the appropriate empty position.
6. Move back toward the root.
7. Recalculate node heights.
8. Calculate balance factors.
9. Perform rotations when necessary.

For example, inserting `30`, `20`, and `10` creates an LL imbalance.

The resulting right rotation restores AVL balance.

### Duplicate keys

The implementations use unique integer keys.

Duplicate insertion is rejected or ignored according to the implementation's API:

- Python returns `False`.
- JavaScript returns `false`.
- C++ returns `false`.
- Java reports a duplicate-key validation error.
- PostgreSQL rejects duplicate keys through a unique constraint.

## 6. AVL Deletion

Deletion is more involved than insertion because removing a node can reduce subtree height.

Three cases must be handled.

### 6.1 Leaf deletion

A leaf has no children.

The node can be removed directly.

### 6.2 One-child deletion

A node with one child is replaced by that child.

The child is connected to the deleted node's former parent.

### 6.3 Two-child deletion

A node with two children is replaced using its in-order successor.

The in-order successor is the smallest key in the right subtree.

After replacement:

1. Delete the successor from its original position.
2. Update affected heights.
3. Recalculate balance factors.
4. Rebalance affected ancestors.

Unlike insertion, deletion can require rebalancing at multiple ancestors.

## 7. Tree Traversal

The implementations provide multiple traversal techniques.

| Traversal | Visiting order | Primary use |
|---|---|---|
| In-order | Left, Root, Right | Sorted output |
| Pre-order | Root, Left, Right | Structural representation |
| Post-order | Left, Right, Root | Bottom-up processing |
| Level-order | Level by level | Breadth-first inspection |

### In-order traversal

In-order traversal returns keys in ascending order.

### Pre-order traversal

Pre-order traversal visits the root before its children.

It is useful for representing the tree structure.

### Post-order traversal

Post-order traversal processes children before their parent.

It is useful for bottom-up operations and tree destruction.

### Level-order traversal

Level-order traversal uses a queue.

It provides a convenient representation of the tree's levels.

## 8. Range Queries

A range query retrieves keys between two boundaries.

For example:

`range_query(25, 65)`

returns all keys satisfying:

\[
25\leq key\leq65
\]

The implementations avoid exploring subtrees that cannot contain valid results.

The expected complexity is:

\[
O(\log n+k)
\]

Where:

- \(n\) is the number of nodes.
- \(k\) is the number of returned keys.

The query includes both boundaries.

## 9. Complexity Analysis

AVL trees maintain logarithmic height.

| Operation | Average | Worst case |
|---|---:|---:|
| Search | O(log n) | O(log n) |
| Insertion | O(log n) | O(log n) |
| Deletion | O(log n) | O(log n) |
| Minimum | O(log n) | O(log n) |
| Maximum | O(log n) | O(log n) |
| Single rotation | O(1) | O(1) |
| Double rotation | O(1) | O(1) |
| Full traversal | O(n) | O(n) |
| Range query | O(log n + k) | O(log n + k) |
| Structural validation | O(n) | O(n) |

Space complexity:

- Tree storage: O(n).
- Recursive traversal stack: O(log n) for a valid AVL tree.
- Level-order traversal queue: O(n) in the widest level.
- Range results: O(k).

The AVL height remains logarithmic because every subtree is constrained by the balance-factor rule.

## 10. Python Implementation

The Python implementation is contained in the first source file.

### Main components

| Component | Responsibility |
|---|---|
| `AVLNode` | Stores key, height, and child references |
| `AVLTree` | Implements tree operations |
| `_height()` | Retrieves subtree height |
| `_balance_factor()` | Calculates node balance |
| `_rotate_left()` | Performs left rotation |
| `_rotate_right()` | Performs right rotation |
| `_rebalance()` | Selects the appropriate rotation |
| `insert()` | Inserts unique keys |
| `delete()` | Removes existing keys |
| `validate()` | Checks structural correctness |
| `range_query()` | Retrieves a bounded key range |

The implementation uses dataclasses for node representation and standard-library JSON support for persistence.

The validation method independently checks:

- BST ordering.
- Stored node heights.
- AVL balance factors.

The persistence workflow validates the serialized tree before accepting it.

A malformed file cannot silently become an accepted tree.

## 11. JavaScript Implementation

The JavaScript implementation provides an event-driven indexing perspective.

### Event-driven behavior

The AVL class extends Node.js `EventEmitter`.

It publishes events for:

- Successful insertion.
- Successful deletion.
- Duplicate keys.
- Rotation operations.

This separates tree operations from monitoring and logging.

An external service can listen for these events without modifying the balancing algorithm.

### JavaScript-specific mechanisms

| Mechanism | Purpose |
|---|---|
| `EventEmitter` | Operation notifications |
| `Set` | Detecting repeated node references |
| Generator | Lazy in-order traversal |
| `Map`-compatible statistics | Structured operational metrics |
| `async` and `await` | Asynchronous file operations |
| `JSON.stringify()` | Tree serialization |
| `fs/promises` | File persistence |

JavaScript integer keys are restricted to safe integers to prevent precision-related ordering errors.

The implementation also uses iterative traversal for selected operations to avoid unnecessary recursive call depth.

## 12. C++17 Implementation

The C++ implementation models an inventory identifier index.

### Memory management

Each node owns its children through:

`std::unique_ptr`

This provides automatic memory management.

Ownership moves during rotations using `std::move`.

The design avoids manually managing node allocation and deallocation.

### Important components

| Component | Responsibility |
|---|---|
| `AVLNode` | Node representation |
| `AVLTree` | AVL operations |
| `unique_ptr` | Exclusive node ownership |
| `optional` | Represents missing minimum or maximum |
| `vector` | Traversal results |
| `queue` | Level-order traversal |
| `enum class` | Rotation identification |
| `AVLStatistics` | Operational statistics |

The implementation also deletes copy construction and copy assignment because the tree uses exclusive ownership.

Move operations remain available.

The validation procedure verifies ordering, stored heights, and balance constraints.

## 13. Java 17 Implementation

The Java implementation models an enterprise product catalog.

The data structure is separated from the service layer.

### Domain model

The `Product` record represents an immutable product.

Its constructor validates:

- Positive product identifiers.
- Non-empty product names.
- Non-empty categories.
- Nonnegative inventory quantities.

### Service layer

`ProductCatalogService` provides operations for:

- Registering products.
- Finding products.
- Discontinuing products.
- Retrieving identifier ranges.
- Listing the catalog.
- Checking index integrity.
- Inspecting operational metrics.

### Design decisions

The generic `AVLTree<T>` separates integer indexing from the stored business object.

This allows the same tree implementation to index different types of records.

`SearchResult<T>` represents a search outcome without requiring callers to infer whether a missing value represents a failure.

`TreeMetrics` provides a compact structural report.

The implementation uses immutable returned collections and explicit validation.

The tree is not internally synchronized. A production service requiring concurrent access must introduce suitable locking or use a concurrency-aware indexing strategy.

## 14. PostgreSQL Implementation

The SQL implementation represents an AVL tree using relational tables.

It uses the `avl_catalog` schema.

### 14.1 Relational model

**avl_trees**

Stores tree-level metadata:

- Tree identifier.
- Tree name.
- Root node identifier.
- Node count.
- Tree height.
- Version.
- Creation and modification timestamps.

**avl_nodes**

Stores individual nodes:

- Node identifier.
- Tree identifier.
- Key.
- Parent identifier.
- Left child identifier.
- Right child identifier.
- Height.
- Balance factor.

### 14.2 Referential integrity

The database defines foreign keys for parent and child relationships.

Composite foreign keys ensure that related nodes belong to the same tree.

Deferred constraints allow related references to be updated within a transaction.

Unique constraints prevent duplicate keys within an individual tree.

Check constraints enforce valid stored balance factors and prevent direct self-references.

### 14.3 Rotation functions

The SQL implementation contains two direct relational rotation functions:

- `avl_rotate_left()`
- `avl_rotate_right()`

These update parent-child relationships, replace the subtree root where necessary, and recalculate affected node heights and balance factors.

The rotation demonstration constructs an LL imbalance and applies a right rotation.

### 14.4 Balanced-tree reconstruction

The SQL insertion and deletion procedures use a different strategy from the in-memory implementations.

They rebuild the relational tree using the sorted set of existing keys.

`avl_build_balanced()` recursively chooses the middle element of each sorted range.

The resulting tree has a balanced structure.

This is a valid AVL construction method, but it is not incremental AVL insertion.

Its rebuilding cost is O(n) per mutation, and repeated individual insertions can therefore be expensive.

The direct rotation functions demonstrate relational rotation mechanics independently of the rebuilding strategy.

### 14.5 Transactions

The deletion demonstration runs inside an explicit transaction.

The tree is validated after the mutation.

An exception causes the transaction to roll back rather than preserving an invalid intermediate state.

### 14.6 Reporting and validation

The SQL implementation includes:

- `avl_tree_report` for tree metadata.
- `avl_node_report` for node relationships.
- `avl_search()` for key retrieval.
- `avl_validate()` for structural checks.
- Recursive CTE traversal.
- Range retrieval.
- Aggregation queries.
- Failure-handling demonstrations.

The validation function checks reachable nodes, parent relationships, stored balance factors, and BST ordering.

## 15. Important Distinctions

### 15.1 AVL trees versus ordinary BSTs

| Property | Ordinary BST | AVL tree |
|---|---|---|
| BST ordering | Yes | Yes |
| Height balancing | No | Yes |
| Balance-factor tracking | Not required | Required |
| Rotations | Not required | Required |
| Worst-case search | O(n) | O(log n) |
| Worst-case insertion | O(n) | O(log n) |
| Maintenance overhead | Lower | Higher |

### 15.2 AVL trees versus other balanced trees

AVL trees maintain stricter height balance than some other self-balancing structures.

This can make searching particularly efficient.

The cost is additional balancing work during insertion and deletion.

The appropriate structure depends on the application's read/write workload.

## 16. Failure Conditions and Edge Cases

The implementations explicitly address the following conditions:

| Condition | Expected behavior |
|---|---|
| Empty tree search | Returns not found |
| Empty minimum lookup | Returns no value |
| Empty maximum lookup | Returns no value |
| Duplicate insertion | Rejects or ignores duplicate |
| Missing-key deletion | Returns failure |
| Invalid key type | Raises validation error |
| Invalid range | Rejects reversed boundaries |
| Single-node tree | Maintains height 1 |
| Two-child deletion | Uses in-order successor |
| Incorrect stored height | Fails structural validation |
| Invalid balance factor | Fails structural validation |
| Corrupted persistence data | Rejects invalid tree |
| Invalid rotation target | Raises an error |

## 17. Testing Strategy

The source files include automated checks for the principal AVL operations.

The four canonical rotation sequences are:

| Rotation | Insertion sequence | Expected root |
|---|---|---:|
| LL | 30, 20, 10 | 20 |
| RR | 10, 20, 30 | 20 |
| LR | 30, 10, 20 | 20 |
| RL | 10, 30, 20 | 20 |

Additional checks cover:

- Sorted in-order output.
- Search success and failure.
- Duplicate insertion.
- Minimum and maximum.
- Range boundaries.
- Leaf deletion.
- One-child deletion.
- Two-child deletion.
- Empty-tree behavior.
- Invalid ranges.
- Structural integrity after mutations.
- Persistence validation.

The validation routine should be run after significant structural changes during development.

## 18. Execution

### Python

Requirements: Python 3.10 or later.

Run the first source file using:

`python avl_tree.py`

The implementation uses only the Python standard library.

### JavaScript

Requirements: Node.js 18 or later.

Run:

`node avl_tree.js`

The implementation uses Node.js standard-library modules.

### C++17

Compile:

`g++ -std=c++17 -O2 -Wall -Wextra -pedantic avl_tree.cpp -o avl_tree`

Run:

`./avl_tree`

On Windows:

`avl_tree.exe`

### Java 17

Compile:

`javac AVLTreeDemo.java`

Run:

`java AVLTreeDemo`

### PostgreSQL

Execute the SQL script using a PostgreSQL 15 or later database.

The script creates the `avl_catalog` schema and its associated tables, functions, procedures, views, sample records, and validation queries.

The script drops and recreates its own schema, so it should be executed only in a database where replacing that schema is acceptable.

## 19. Performance and Production Considerations

### Memory overhead

AVL nodes store additional height information and child references.

This increases memory usage compared with a minimal binary search tree.

### Rotation frequency

Insertion and deletion can trigger rotations.

Rotation statistics help evaluate balancing behavior during testing.

### Concurrency

The in-memory implementations are not thread-safe.

Concurrent mutations require synchronization to prevent inconsistent parent-child relationships.

### Database performance

The PostgreSQL implementation demonstrates relational integrity and balanced-tree construction.

Its rebuild strategy is appropriate for educational demonstrations and smaller datasets, not high-frequency large-scale mutations.

A production database generally benefits from its native B-tree indexes rather than a custom relational AVL representation.

### Input validation

Keys must maintain a consistent ordering.

JavaScript uses safe integers, while the other implementations use their respective integer types.

External inputs should be validated before entering the tree.

### Persistence

Serialized data must be treated as untrusted input.

Stored heights and tree ordering must be checked rather than assumed correct.

### Operational monitoring

Rotation counts, operation counts, height, and node count provide useful diagnostics.

Unexpected height changes or failed structural validation should be investigated before accepting further mutations.

## 20. Implemented Architecture

The overall AVL operation sequence is:

    Input Key
        |
        v
    Validate Key
        |
        v
    Binary Search Tree Insertion
        |
        v
    Update Node Heights
        |
        v
    Calculate Balance Factors
        |
        v
    Identify Imbalance
        |
        +------ LL ------> Right Rotation
        |
        +------ RR ------> Left Rotation
        |
        +------ LR ------> Left + Right Rotation
        |
        +------ RL ------> Right + Left Rotation
        |
        v
    Restore AVL Properties
        |
        v
    Validate Tree
        |
        v
    Return Updated Index

The central invariant is:

\[
\boxed{|H(v_L)-H(v_R)|\leq1}
\]

Every node must satisfy this condition after a completed AVL mutation.

The combination of ordering, height maintenance, balance-factor evaluation, and rotations provides the logarithmic-height behavior that distinguishes AVL trees from ordinary binary search trees.
