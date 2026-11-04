# Lowest Common Ancestor (LCA)

## 1. Topic Overview

The Lowest Common Ancestor (LCA) of two nodes in a rooted tree is the deepest node that is an ancestor of both nodes.

An ancestor of a node includes the node itself. Consequently, the LCA of a node with itself is that node.

Consider the following binary tree:

                1
              /   \
             2     3
            / \   / \
           4   5 6   7
          / \ /
         8  9 10

Examples:

| Query | LCA | Explanation |
|---|---:|---|
| LCA(8, 9) | 4 | Both nodes belong to node 4's subtree. |
| LCA(8, 10) | 2 | Their paths first meet at node 2. |
| LCA(8, 6) | 1 | Their paths meet at the root. |
| LCA(5, 10) | 5 | One queried node is an ancestor of the other. |
| LCA(2, 8) | 2 | An ancestor queried with its descendant. |
| LCA(7, 7) | 7 | A node is its own ancestor. |

The implementations use integer node identifiers and reject duplicate identifiers within a tree.

## 2. Fundamental Terminology

### 2.1 Root

The root is the node without a parent. Every node in a rooted tree has exactly one path from the root.

### 2.2 Parent

The immediate predecessor of a node on its path from the root.

### 2.3 Child

A node directly connected below another node. In a binary tree, a parent can have at most two children:

- Left child
- Right child

### 2.4 Ancestor

A node on the path from the root to a given node.

A node is also considered its own ancestor for LCA purposes.

### 2.5 Descendant

A node whose path to the root passes through another specified node.

### 2.6 Depth

The number of edges between a node and the root.

The root has depth zero.

### 2.7 Height

The maximum number of edges from a node to a leaf in its subtree.

### 2.8 Subtree

A node together with all its descendants.

### 2.9 Lowest Common Ancestor

The common ancestor with the greatest depth.

For two nodes p and q, the LCA is the deepest node appearing in both root-to-node paths.

## 3. Core LCA Mechanism

There are several ways to solve LCA queries. Their differences concern how much information is stored before queries and how much work each query requires.

The five implementations cover the following approaches:

| Approach | Preprocessing | Query time | Additional storage |
|---|---:|---:|---:|
| Recursive binary-tree LCA | None | O(N) | O(H) stack |
| Parent-pointer LCA | Parent references already available | O(H) | O(H) |
| Depth-alignment LCA | None | O(H) | O(1) |
| Binary lifting | O(N log N) | O(log N) | O(N log N) |
| Relational recursive CTE | Database-dependent | O(H) traversal | Recursive working data |

N represents the number of nodes and H represents tree height.

For a balanced binary tree, H is approximately log N. For a completely skewed tree, H can approach N.

## 4. Recursive Binary-Tree LCA

### 4.1 Principle

The recursive approach examines both subtrees.

For a node x:

1. If x is null, return null.
2. If x is either requested node, return x.
3. Search the left subtree.
4. Search the right subtree.
5. If both searches return non-null nodes, x is their LCA.
6. Otherwise, propagate the non-null result upward.

The central relationship is:

- Both targets found in separate subtrees: current node is the LCA.
- Both targets found in one subtree: propagate that subtree's result.
- One target is the current node: current node is the LCA if the other target exists below it.

### 4.2 Complexity

| Measure | Complexity |
|---|---|
| Time | O(N) |
| Recursive stack | O(H) |
| Preprocessing | None |

Every node may need to be visited.

A recursive implementation can encounter stack-depth limitations for highly skewed trees.

The Python implementation also checks that both requested nodes exist. This prevents returning an apparently valid candidate when only one requested node is present.

### 4.3 Appropriate usage

Recursive LCA is appropriate when:

- The tree is relatively small.
- Queries are infrequent.
- The tree structure is already available.
- Simplicity is more important than repeated-query performance.

## 5. Parent-Pointer Approach

### 5.1 Principle

Each node stores a reference to its parent.

The algorithm uses two phases.

**Phase 1: Record the first node's ancestors**

Start at the first node and move toward the root. Store every encountered node in a set.

**Phase 2: Search the second node's ancestors**

Start at the second node and move toward the root. The first node found in the stored set is the LCA.

For the sample tree:

- Ancestors of 8: 8, 4, 2, 1
- Ancestors of 10: 10, 5, 2, 1
- First shared ancestor encountered from node 10: 2

Therefore, LCA(8, 10) = 2.

### 5.2 Complexity

| Measure | Complexity |
|---|---|
| Time | O(H) |
| Auxiliary storage | O(H) |
| Preprocessing | None when parent references already exist |

This approach is useful when parent relationships are frequently needed for navigation.

### 5.3 Parent-pointer alternative: Depth alignment

Instead of storing ancestors in a set, calculate both node depths.

Move the deeper node upward until both nodes have equal depth.

Then move both nodes upward simultaneously until they meet.

This approach requires O(1) auxiliary storage and O(H) time.

The Python, JavaScript, C++17, and Java implementations include this method.

## 6. Binary Lifting

Binary lifting is an efficient method for answering many LCA and ancestor queries.

It stores information about ancestors at exponentially increasing distances.

### 6.1 Basic idea

For every node v, define:

`up[v][j]` = the ancestor of v located 2^j edges above it.

The first levels are:

| Level | Ancestor distance |
|---|---:|
| 0 | 1 edge |
| 1 | 2 edges |
| 2 | 4 edges |
| 3 | 8 edges |
| 4 | 16 edges |

If an ancestor does not exist at a particular distance, the entry is null or -1, depending on the implementation.

### 6.2 Preprocessing recurrence

The direct parent is:

`up[v][0] = parent[v]`

For higher levels:

`up[v][j] = up[up[v][j-1]][j-1]`

This recurrence works because moving 2^j edges upward is equivalent to performing two consecutive jumps of 2^(j-1) edges.

The preprocessing process uses a traversal to establish node depths and immediate parents. It then fills the ancestor table.

### 6.3 Finding the LCA

For two nodes u and v:

1. Compare their depths.
2. Lift the deeper node until both have equal depth.
3. If the nodes are equal, return that node.
4. Otherwise, inspect ancestor-table levels from largest to smallest.
5. Whenever the two nodes have different ancestors at a level, move both nodes upward.
6. Their immediate parent is the LCA.

Descending through the levels prevents skipping over the lowest common ancestor.

### 6.4 Complexity

Let L = ceil(log2(N + 1)).

| Operation | Complexity |
|---|---|
| Preprocessing | O(N log N) |
| Storage | O(N log N) |
| LCA query | O(log N) |
| Kth ancestor | O(log N) |
| Distance query after LCA | O(log N) |

Binary lifting is particularly effective when the tree remains unchanged while many queries are processed.

### 6.5 Limitations

Binary lifting requires additional memory.

When the tree changes, the ancestor table may become outdated. The index must be rebuilt or updated using an appropriate dynamic-tree technique.

It is not automatically a solution for arbitrary dynamic tree modifications.

## 7. Kth Ancestor Queries

The kth ancestor of node v is the node located k edges above v.

Examples:

| Node | k | Result |
|---|---:|---|
| 8 | 0 | 8 |
| 8 | 1 | 4 |
| 8 | 2 | 2 |
| 8 | 3 | 1 |
| 8 | 4 | Not available |

Binary representation allows a query to be decomposed into powers of two.

For example:

`5 = 4 + 1`

Therefore, finding the fifth ancestor requires one four-edge jump and one one-edge jump.

This is the same mechanism used by binary lifting.

The implementations return null, an empty optional, or -1 when the requested ancestor does not exist.

Negative k values are rejected.

## 8. Distance Between Two Nodes

The shortest path between two nodes in a tree always passes through their LCA.

Let:

- depth(u) represent the depth of u.
- depth(v) represent the depth of v.
- w represent LCA(u, v).

Then:

`distance(u, v) = depth(u) + depth(v) - 2 × depth(w)`

For nodes 8 and 10:

- depth(8) = 3
- depth(10) = 3
- LCA(8, 10) = 2
- depth(2) = 1

Therefore:

`distance(8, 10) = 3 + 3 - 2 × 1 = 4`

This operation is useful in hierarchical navigation, network routing, tree-based indexing, and organizational structures.

## 9. Ancestor Relationship Queries

An ancestor query determines whether node a is an ancestor of node b.

Starting at b, repeatedly follow parent pointers until either:

- Node a is encountered.
- The root is reached.

If a is encountered, the relationship exists.

The implementations treat a node as its own ancestor.

The query takes O(H) time with parent pointers.

Binary lifting can also support faster ancestor checks when combined with additional interval information from a DFS traversal.

## 10. Python Implementation

The Python program models a binary tree through a `TreeNode` dataclass and a `BinaryTree` class.

### Implemented mechanisms

| Component | Responsibility |
|---|---|
| `TreeNode` | Stores node value, children, and parent |
| `BinaryTree` | Manages tree construction and operations |
| `recursive_lca()` | Recursive LCA calculation |
| `parent_pointer_lca()` | Ancestor-set approach |
| `depth_lca()` | Depth-alignment approach |
| `BinaryLifting` | Precomputed ancestor index |
| `kth_ancestor()` | Finds a specified ancestor |
| `distance()` | Calculates shortest path length |
| `is_ancestor()` | Evaluates ancestor relationships |

### Design decisions

- Dictionaries provide direct node lookup.
- Sets support efficient ancestor membership checks.
- Deques support iterative level-order preprocessing.
- Dataclasses provide compact node definitions.
- Exceptions distinguish invalid operations from missing results.
- Assertions verify the expected behavior.

The recursive implementation explicitly checks the existence of both requested nodes.

The binary-lifting implementation uses iterative preprocessing to avoid recursive traversal stack limitations.

## 11. JavaScript Implementation

The JavaScript implementation emphasizes event-driven query processing and cached results.

### Implemented mechanisms

| Component | Responsibility |
|---|---|
| `TreeNode` | Stores binary-tree relationships |
| `BinaryTree` | Constructs and validates the hierarchy |
| `AncestorIndex` | Maintains the binary-lifting table |
| `QueryService` | Handles repeated queries |
| `batchLCA()` | Processes multiple queries |
| `clearCache()` | Invalidates cached query results |

### Query caching

A query between nodes 8 and 10 is equivalent to a query between nodes 10 and 8.

The service normalizes the node order before constructing a cache key.

Consequently:

- First query: calculate and cache the result.
- Repeated query: retrieve the cached result.
- Cache clearing: remove stored results.

The cache is suitable for an immutable tree index.

If structural modifications are introduced, cached results must be invalidated and the ancestor index rebuilt.

### Runtime characteristics

The implementation uses:

- `Map` for node and ancestor lookup.
- `Set` for ancestor membership.
- Arrays for binary-lifting levels.
- Promises for asynchronous execution compatibility.
- Structured objects for query results.
- Exceptions for invalid inputs.

No third-party dependencies are required.

## 12. C++17 Implementation

The C++ implementation models a binary tree using explicit pointers and standard library containers.

### Domain structure

`TreeNode` stores:

- Integer identifier.
- Left-child pointer.
- Right-child pointer.
- Parent pointer.

`BinaryTree` manages node allocation and prevents duplicate identifiers and occupied child positions.

Copy operations are disabled because the tree owns dynamically allocated nodes.

The destructor releases allocated nodes.

### Binary-lifting engine

`BinaryLifting` separates preprocessing from query execution.

It stores:

- Node depths.
- Ancestor tables.
- Number of binary-lifting levels.

The implementation uses:

- `unordered_map` for node-indexed storage.
- `queue` for iterative preprocessing.
- `unordered_set` for ancestor tracking.
- `vector` for ancestor levels and batch results.
- Exceptions for invalid queries.

### Batch processing

The `batchLCA()` method processes a vector of node pairs against the same precomputed index.

This avoids repeating preprocessing for each query.

The tree is non-copyable to protect pointer ownership and avoid accidental double deletion.

## 13. Java 17 Implementation

The Java implementation represents an enterprise-oriented hierarchical query service.

### Domain components

| Component | Responsibility |
|---|---|
| `TreeNode` | Encapsulates node relationships |
| `BinaryTree` | Manages hierarchy and structural state |
| `AncestorIndex` | Provides optimized ancestor queries |
| `LcaQuery` | Immutable query request |
| `QueryResult` | Immutable query response |
| `QueryPolicy` | Defines query authorization rules |
| `SameTreePolicy` | Validates permitted identifier values |
| `LcaQueryService` | Applies policy and caching |

### Structural state

The tree has two states:

- `ACTIVE`: structural changes are permitted.
- `REGISTERED`: structural changes are rejected.

The `freeze()` method transitions the tree into the registered state.

This ensures that the hierarchy cannot silently change after it has been finalized for indexing.

### Policy-based execution

The query service separates authorization from algorithm execution.

The `QueryPolicy` interface provides a policy boundary.

The current `SameTreePolicy` validates non-negative identifiers. The binary-tree index then verifies actual node existence.

This distinction separates query policy from structural validation.

### Immutable query objects

Java records represent query requests and results.

They provide compact data structures with immutable component references.

The service normalizes query keys so that reversed node pairs can share cached results.

### Production considerations

A production service would also require:

- User and tenant authorization.
- Resource-level access control.
- Tree-version validation.
- Cache invalidation.
- Query-size limits.
- Audit logging.
- Concurrency controls.
- Immutable or versioned hierarchy snapshots.

The sample policy demonstrates the separation of responsibilities but does not implement a complete identity-management system.

## 14. PostgreSQL Implementation

The SQL implementation represents binary-tree relationships through relational records.

### 14.1 Relational model

The primary tables are:

| Table | Purpose |
|---|---|
| `binary_tree` | Stores tree metadata |
| `tree_node` | Stores node identifiers and parent relationships |
| `ancestor_index` | Stores binary-lifting information |
| `lca_query_log` | Records query workload |

### 14.2 Tree representation

The `tree_node` table contains:

- `node_id`: unique node identifier.
- `tree_id`: owning tree.
- `node_value`: business-level node value.
- `parent_node_id`: parent reference.
- `child_side`: left or right position.

The composite foreign key ensures that a parent belongs to the same tree.

The unique root index permits only one root per tree.

The unique child-position index prevents multiple left children or multiple right children for the same parent.

The trigger rejects cycles during structural modifications.

### 14.3 Recursive CTE

A recursive common table expression repeatedly follows parent relationships.

The `recursive_lca()` function builds ancestor chains for both requested nodes.

It identifies their shared ancestors and selects the nearest common ancestor.

The parent-pointer function uses a similar relational traversal but provides a separate implementation of the ancestor-chain method.

### 14.4 Binary-lifting storage

The `ancestor_index` table stores:

- Tree identifier.
- Node identifier.
- Jump level.
- Ancestor node identifier.

For example, level zero stores the immediate parent and level one stores the second ancestor.

The `build_ancestor_index()` procedure generates these records.

The `kth_ancestor()` and `binary_lifting_lca()` functions use the precomputed information.

### 14.5 Transaction handling

The sample script builds the ancestor index inside an explicit transaction.

This ensures that index construction is committed as a unit or rolled back if an error occurs.

The index must be rebuilt after structural modifications.

For production use, index versions should be associated with tree versions so that queries cannot use stale preprocessing data.

### 14.6 Reporting

The SQL workflow supports:

- Tree-node retrieval.
- Recursive LCA evaluation.
- Parent-pointer LCA evaluation.
- Binary-lifting LCA evaluation.
- Kth ancestor retrieval.
- Distance calculation.
- Ancestor relationship evaluation.
- Batch query reporting.
- Query aggregation.
- Index inspection.
- Validation and failure handling.

## 15. Important Edge Cases

| Case | Expected behavior |
|---|---|
| Both query nodes are identical | Return that node |
| First node is an ancestor of second | Return first node |
| Second node is an ancestor of first | Return second node |
| Nodes are in separate root branches | Return root |
| One node does not exist | Reject or return no result according to the interface |
| Both nodes are absent | Reject the query |
| Empty tree | Reject preprocessing |
| Single-node tree | Root is its own LCA |
| Negative kth-ancestor distance | Reject input |
| kth ancestor exceeds node depth | Return no ancestor |
| Duplicate node identifiers | Reject insertion |
| Occupied child position | Reject insertion |
| Invalid child side | Reject insertion |
| Structural cycle | Reject insertion or update |
| Modified tree with stale index | Rebuild the index before querying |

## 16. Algorithm Selection

The appropriate LCA algorithm depends on the number of queries, tree size, structural stability, and available memory.

| Situation | Preferred approach |
|---|---|
| Small tree, occasional queries | Recursive LCA |
| Parent pointers already available | Parent-pointer LCA |
| Limited auxiliary memory | Depth alignment |
| Large number of repeated queries | Binary lifting |
| Relational hierarchical data | Recursive CTE |
| Database workload with repeated queries | Persisted ancestor index |
| Immutable enterprise hierarchy | Precomputed binary-lifting index |

Binary lifting is not always the best choice.

For one or two queries, preprocessing can cost more than it saves. For a large static tree with thousands of queries, its logarithmic query complexity can provide a substantial performance advantage.

## 17. Practical Applications

### Organizational hierarchies

Given two employees, the LCA identifies their lowest shared reporting manager.

### File systems

Given two directory nodes, the LCA identifies the closest common parent directory.

### Version-control structures

An ancestor relationship can identify shared historical points in a rooted commit graph represented as a tree.

A general version-control commit graph can contain multiple parents, so ordinary binary-tree LCA assumptions do not automatically apply.

### Network hierarchies

The LCA can identify the nearest shared aggregation point in a hierarchical network.

### XML and document structures

The LCA identifies the closest common enclosing element of two nodes.

### Database hierarchy queries

Parent relationships can be queried through recursive CTEs or stored ancestor indexes.

## 18. Limitations and Engineering Considerations

### Binary-tree assumptions

These implementations assume a rooted tree in which each node has at most two children.

A general tree may have an arbitrary number of children. The LCA principles remain applicable, but the node representation and traversal logic must be adapted.

### Multiple roots

Each tree is represented independently. Queries across different trees are invalid.

### Dynamic updates

Adding or removing nodes after binary-lifting preprocessing can invalidate ancestor information.

The index must be rebuilt unless a dynamic-tree algorithm is introduced.

### Recursive stack limitations

Recursive traversal has stack usage proportional to tree height.

An extremely skewed tree can cause stack exhaustion in languages with limited recursion stacks.

Iterative traversal avoids this preprocessing limitation.

### Database concurrency

Concurrent tree updates can invalidate ancestor-index assumptions.

A production implementation should serialize structural changes, maintain a tree version, and ensure that each query uses an index matching the same version.

### Memory consumption

Binary lifting requires O(N log N) ancestor entries.

For very large trees with few queries, parent-pointer methods may be more economical.

### Security and integrity

Tree identifiers should be validated at application boundaries.

Database permissions should prevent unauthorized structural modifications.

Cross-tree references, duplicate child positions, and cycles must be rejected.

Cached results must not be shared across incompatible tree versions or authorization contexts.

## 19. Validation Scenarios

The five implementations use the same sample hierarchy to test the principal LCA mechanisms.

| Test | Expected result |
|---|---:|
| Recursive LCA(8, 9) | 4 |
| Recursive LCA(8, 10) | 2 |
| Recursive LCA(8, 6) | 1 |
| Parent LCA(8, 10) | 2 |
| Depth LCA(8, 6) | 1 |
| Binary lifting LCA(5, 10) | 5 |
| Kth ancestor(8, 1) | 4 |
| Kth ancestor(8, 2) | 2 |
| Kth ancestor(8, 3) | 1 |
| Kth ancestor(8, 4) | Not available |
| Distance(8, 10) | 4 |
| Distance(8, 6) | 5 |
| Is ancestor(2, 8) | True |
| Is ancestor(3, 8) | False |

These cases verify ordinary queries, ancestor-descendant queries, cross-subtree queries, boundary conditions, and invalid-node handling.

## 20. Cross-Language Implementation Comparison

| Capability | Python | JavaScript | C++17 | Java 17 | PostgreSQL |
|---|---|---|---|---|---|
| Tree representation | Dataclass | Class | Struct and pointers | Classes | Relational tables |
| Parent pointers | Yes | Yes | Yes | Yes | Foreign keys |
| Recursive LCA | Yes | Yes | Yes | Yes | Recursive CTE |
| Parent-pointer LCA | Yes | Yes | Yes | Yes | Recursive function |
| Depth alignment | Yes | Yes | Yes | Yes | Depth function |
| Binary lifting | Yes | Yes | Yes | Yes | Ancestor table |
| Kth ancestor | Yes | Yes | Yes | Yes | SQL function |
| Batch queries | Loop | Array | Vector | List | Query log |
| Query caching | No | Yes | No | Yes | Query logging |
| Validation | Exceptions | Exceptions | Exceptions | Custom exceptions | Constraints and triggers |

## 21. Learning Objectives

The central technical distinction is between computing an LCA directly and preprocessing a tree to accelerate repeated queries.

The recursive method demonstrates how subtree information propagates toward the root.

The parent-pointer method demonstrates how ancestor chains intersect.

Depth alignment demonstrates how equal-depth traversal simplifies comparisons.

Binary lifting demonstrates how powers of two reduce ancestor-navigation time.

The database implementation demonstrates how hierarchical relationships can be represented, validated, indexed, and queried using relational structures.

Together, these mechanisms establish the foundation for efficient ancestor-related operations on rooted trees.
