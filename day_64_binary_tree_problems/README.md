# Binary Tree Problems

## Scope

This project implements six fundamental binary-tree operations across Python, JavaScript, C++17, Java 17, and PostgreSQL:

- Maximum depth
- Minimum depth
- Root-to-leaf path sum
- Tree diameter
- Balanced-tree validation
- Node counting

The implementations also include level-order construction, structural validation, complete-tree detection, optimized complete-tree counting, and combined tree analysis.

The central data structure is a binary tree. Each node contains a value and references to at most two children: a left child and a right child.

A binary tree is not necessarily a binary search tree. No ordering relationship between parent and child values is assumed.

## Binary Tree Structure

A binary tree can be represented as:

    10
   /  \
  5    15
 / \   / \
3   7 12 18

Each node has three logical fields:

| Field | Meaning |
|---|---|
| `value` | Integer stored by the node |
| `left` | Reference to the left child, or null |
| `right` | Reference to the right child, or null |

The root is the first node. A leaf is a node with neither a left nor a right child.

An empty tree has no root and contains zero nodes.

### Depth and height terminology

This project uses two explicit measurement conventions:

| Measurement | Convention |
|---|---|
| Maximum depth | Number of nodes along the longest root-to-leaf path |
| Minimum depth | Number of nodes along the shortest root-to-leaf path |
| Subtree height | Number of nodes on its longest downward path |
| Diameter | Number of edges along the longest path between any two nodes |

The root of a non-empty tree has depth one under the node-counting convention.

The diameter uses edges rather than nodes. Consequently, a one-node tree has a diameter of zero.

These conventions avoid a common source of off-by-one errors in binary-tree implementations.

## Maximum Depth

Maximum depth is the number of nodes along the longest path from the root to a leaf.

For the example tree:

    10
   /  \
  5    15
 / \   / \
3   7 12 18

The maximum depth is three.

A breadth-first search maintains a queue of nodes with their levels. Every child is added at the current level plus one. The largest recorded level is the maximum depth.

The implementation uses an iterative queue rather than recursive calls. This prevents call-stack exhaustion for very deep, unbalanced trees.

**Complexity**

- Time: `O(n)`
- Auxiliary space: `O(w)`, where `w` is the maximum tree width

Here, `n` represents the number of nodes.

## Minimum Depth

Minimum depth is the number of nodes along the shortest path from the root to an actual leaf.

A leaf must have both children absent.

A node with one missing child is not necessarily a leaf. This distinction is essential.

Consider:

    1
   /
  2

The minimum depth is two, not one. The root has no right child, but it still has a left subtree and is not a leaf.

Breadth-first search is particularly effective for this problem. The first leaf reached is guaranteed to have the minimum depth because nodes are processed level by level.

The implementation stops at that first leaf instead of visiting every remaining node.

**Complexity**

- Time: `O(n)` worst case
- Auxiliary space: `O(w)`

## Root-to-Leaf Path Sum

A path-sum problem checks whether at least one path from the root to a leaf has a specified total.

For a target of 22:

    10
   /  \
  5    15
 / \   / \
3   7 12 18

The path:

    10 -> 5 -> 7

has a sum of 22.

The path must begin at the root and terminate at a leaf. A matching sum at an intermediate node does not qualify.

The implementations use depth-first traversal and maintain the accumulated sum for each pending path.

Negative values are supported. They do not require a different algorithm because the accumulated value is calculated independently for each root-to-leaf path.

The JavaScript implementation uses `BigInt` for accumulated path sums, avoiding loss of integer precision when multiple safe-integer values are added.

The Java and C++ implementations use checked `long`-range arithmetic. An arithmetic overflow is reported instead of silently producing an incorrect result.

**Complexity**

- Time: `O(n)`
- Auxiliary space: `O(h)` for the explicit depth-first stack, where `h` is tree height

## Tree Diameter

The diameter is the longest path between any two nodes in a binary tree.

The endpoints do not have to be leaves directly connected through the root. The longest path may lie entirely inside one subtree.

For every node, the longest path passing through that node is:

\[
D_{\text{through}} =
H_{\text{left}} + H_{\text{right}}
\]

Here, each height is measured in edges from the node's child to the deepest descendant. An empty child has height zero.

The diameter of a subtree is the largest of:

- The longest path passing through its root.
- The diameter of its left subtree.
- The diameter of its right subtree.

Therefore:

\[
D =
\max(
H_{\text{left}} + H_{\text{right}},
D_{\text{left}},
D_{\text{right}}
)
\]

The implementations use postorder traversal. A parent is processed only after its children have produced their heights and diameters.

This avoids recalculating subtree heights at every node.

For the seven-node example tree, the path:

    3 -> 5 -> 10 -> 15 -> 12

contains five nodes and four edges. Its diameter is four.

**Complexity**

- Time: `O(n)`
- Auxiliary space: `O(n)` for stored subtree statistics and traversal state

## Balanced Binary Tree

A binary tree is height-balanced when every node satisfies:

\[
|H_{\text{left}} - H_{\text{right}}| \leq 1
\]

The condition must hold at every node, not only at the root.

A tree can have a balanced root while containing an unbalanced subtree.

For example:

    5
   /
  4
 /
3
/
2

This tree is not balanced. Its longest branch repeatedly extends to the left.

The efficient validation method calculates subtree heights during a postorder traversal.

Each node receives two pieces of information:

- The height of its subtree.
- Whether that subtree is balanced.

The parent combines the results from its children. If either child is unbalanced, the parent cannot be balanced. The height difference is also checked.

This produces an `O(n)` solution. Recalculating both subtree heights separately at every node can take `O(n²)` time on a skewed tree.

An empty tree is considered balanced.

**Complexity**

- Time: `O(n)`
- Auxiliary space: `O(n)`

## Node Counting

General binary-tree node counting requires visiting each reachable node exactly once.

The count is:

\[
N = 1 + N_{\text{left}} + N_{\text{right}}
\]

The empty tree has a count of zero.

The general counting implementation works for arbitrary binary trees. It does not assume that all levels are full or that nodes occupy positions from left to right.

**Complexity**

- Time: `O(n)`
- Auxiliary space: `O(n)` worst case for traversal and validation

### Complete Binary Trees

A complete binary tree has the following properties:

- Every level except possibly the final level is completely filled.
- Nodes on the final level occupy the leftmost available positions.
- There are no gaps before an existing node in level order.

A complete tree is not necessarily perfect.

A perfect binary tree has every internal node with exactly two children, and every leaf occurs at the same depth.

For a complete tree, optimized counting can use leftmost subtree heights.

Let `L` be the leftmost height of the left subtree and `R` be the leftmost height of the right subtree.

When `L == R`, the left subtree is perfect. The current node and that subtree contribute:

\[
2^L
\]

The remaining counting operation continues in the right subtree.

When the heights differ, the right subtree is perfect. The current node and that subtree contribute:

\[
2^R
\]

The remaining operation continues in the left subtree.

The counting phase takes:

\[
O(\log^2 n)
\]

The optimized method relies on the complete-tree property. Applying it to an arbitrary binary tree can produce an incorrect result.

The Python, JavaScript, C++, and Java implementations verify completeness by default before using the optimized algorithm. Python and JavaScript also expose an option to skip verification when the caller already guarantees the precondition.

The SQL implementation verifies completeness through heap-position numbering.

## Level-Order Representation

The programming-language implementations include a level-order tree builder.

For example:

`[10, 5, 15, 3, 7, 12, 18]`

represents:

    10
   /  \
  5    15
 / \   / \
3   7 12 18

A missing child is represented by `None` in Python, `null` in JavaScript, `std::nullopt` in C++, and `null` in Java.

The builder processes parents through a queue. Each parent receives up to two values: first its left child and then its right child.

Malformed input is rejected. A non-empty tree cannot have a missing root followed by non-null nodes. Non-null values remaining after all possible parents have been consumed are also invalid.

## Structural Validation

A proper binary tree has one root, no cycles, and no node shared by multiple parents.

The implementations validate these properties before running public tree operations.

A cycle occurs when a child reference eventually leads back to an ancestor.

A shared node occurs when two different parent references point to the same node.

Both structures violate the ordinary tree model. They can cause repeated traversal, incorrect counts, or infinite processing.

| Validation condition | Rejection reason |
|---|---|
| Child is not a valid node | Invalid data structure |
| A node is visited more than once | Cycle or shared child |
| Non-integer node value | Unsupported value type |
| Unreachable level-order value | Invalid input representation |
| Complete-tree operation on an incomplete tree | Invalid algorithm precondition |

The Python, C++, and Java implementations use explicit traversal state. JavaScript uses `Set` and object identity. Java uses `IdentityHashMap`, ensuring validation does not depend on application-defined equality methods.

## Python Implementation

The Python file uses a `TreeNode` dataclass with identity-based equality disabled. This makes object identity explicit when detecting repeated nodes.

The implementation includes:

- `validate_tree()` for structural validation.
- `from_level_order()` for input construction.
- `max_depth()` and `min_depth()` for depth calculations.
- `has_path_sum()` for root-to-leaf sum evaluation.
- `diameter()` for the longest path between two nodes.
- `is_balanced()` for height-balance validation.
- `count_nodes()` for general counting.
- `is_complete_tree()` and `count_complete_nodes()` for complete-tree operations.
- `analyze_tree()` for combined metrics.
- `run_tests()` for functional and edge-case validation.

The combined analysis calculates subtree height, minimum depth, diameter, balance, and node count in one postorder pass. Path-sum checking remains a separate traversal because it depends on a requested target value.

The implementation uses iterative traversals instead of recursive functions. This is useful when processing trees whose height may exceed Python's normal recursion limit.

Python integers support arbitrary-precision arithmetic, so path sums do not overflow the built-in integer representation.

## JavaScript Implementation

The JavaScript file uses classes and standard Node.js functionality.

`BinaryTree` manages tree construction, validation, traversal, and counting. `TreeNode` represents individual nodes.

The implementation uses:

- Arrays as indexed queues, avoiding the repeated cost of removing the first array element.
- `Set` to detect repeated node references.
- `Map` to associate nodes with postorder metrics.
- `BigInt` for exact path-sum arithmetic.
- `EventEmitter` for publishing completed analysis results.
- Promises and `setImmediate()` for asynchronous analysis.

`TreeAnalysisService` provides an event-driven interface. Successful analysis emits an `analysis` event and resolves its Promise. Failed analysis emits `analysisError` and rejects the Promise.

The implementation deliberately separates synchronous tree algorithms from asynchronous service orchestration. The underlying calculations remain deterministic and can be called without the event service.

`countCompleteNodes()` returns a `BigInt` because its optimized calculation uses integer powers of two.

## C++17 Implementation

The C++ file uses an ownership arena containing `std::unique_ptr<TreeNode>` objects.

The tree's child references are non-owning pointers. The arena controls node lifetime, while left and right pointers represent the actual tree relationships.

This design avoids recursive ownership and makes node addresses stable when the arena's vector reallocates. The `BinaryTree` class disables copying and supports moving.

The implementation includes:

- Level-order construction using `std::optional`.
- An explicit structural validator.
- Queue-based depth calculations.
- Checked arithmetic for root-to-leaf path sums.
- An `unordered_map` for postorder subtree statistics.
- Complete-tree validation.
- Optimized complete-tree counting using `uint64_t`.
- Assertions for functional and failure-case tests.

The postorder analysis stores the computed height, minimum depth, diameter, balance state, and node count for each node.

The complete-tree counter checks shift limits before computing powers of two. This avoids undefined shift behavior and reports counts that exceed the supported integer range.

The implementation uses standard library containers and algorithms without third-party dependencies.

## Java 17 Implementation

The Java file models a small enterprise tree-analysis service.

`TreeNode` represents the stored structure. `TreePolicy` defines operational limits, while `TreeMetrics` is an immutable record containing the calculated results.

The policy defines:

| Property | Purpose |
|---|---|
| `maximumNodes` | Limits the number of accepted nodes |
| `maximumDepth` | Limits the permitted tree height |
| `requireBalanced` | Rejects trees that fail the balance rule |

`TreeAnalyticsService` validates the tree before analysis and applies the configured policy.

Custom exceptions distinguish structural failures from resource-limit violations and policy failures:

- `InvalidTreeException`
- `TreeLimitExceededException`
- `PolicyViolationException`

The service uses `IdentityHashMap` for node-level validation and postorder statistics. This ensures the calculation operates on actual node identity rather than any future business-specific equality rules.

The service demonstrates two policies. A standard policy allows unbalanced trees within configured limits. A balanced-only policy rejects an unbalanced structure.

The separation between analysis and policy is deliberate. A tree can be structurally valid while still violating a particular operational policy.

## PostgreSQL Implementation

The SQL file models each tree as a snapshot with separately stored node records.

### Relational model

The relationship is:

    tree_snapshot
         |
         +---- tree_node
                   |
                   +---- left_child_id
                   |
                   +---- right_child_id

Each snapshot contains a root identifier. Each node contains its value and the identifiers of its two possible children.

| Database object | Responsibility |
|---|---|
| `tree_snapshot` | Stores tree identity, root, state, and creation time |
| `tree_node` | Stores node values and child references |
| `validate_tree_integrity()` | Validates the complete tree structure |
| `validate_tree_change_trigger()` | Performs deferred validation |
| `publish_tree()` | Validates and publishes a snapshot |
| `analyze_tree()` | Calculates all primary tree metrics |
| `count_tree_nodes()` | Counts nodes in any valid tree |
| `count_complete_tree_nodes()` | Verifies and counts a complete tree |
| `tree_snapshot_summary` | Provides snapshot-level reporting |

### Referential integrity

The `tree_node` primary key is `(snapshot_id, node_id)`.

Child references use composite foreign keys. As a result, a child cannot accidentally reference a node from a different snapshot.

The root also uses a composite foreign key. Child and root references are deferred so a snapshot and all its nodes can be inserted in one transaction.

Check constraints reject direct self-references and prevent the same node from being assigned as both children of one parent.

### Structural validation

Foreign keys alone cannot guarantee that a relational graph is a valid binary tree.

The validation function therefore checks additional conditions:

- A non-empty tree has a root.
- A child has no more than one parent.
- Reachable cycles do not exist.
- Every stored node is reachable from the root.

The recursive CTE maintains a path array so that an encountered cycle is identified rather than followed indefinitely.

Deferred constraint triggers validate the final transaction state. This permits related records to be inserted in an order that would temporarily violate immediate referential checks.

### Database analysis

`analyze_tree()` returns:

| Column | Meaning |
|---|---|
| `max_depth` | Maximum root-to-leaf depth in nodes |
| `min_depth` | Minimum root-to-leaf depth in nodes |
| `has_path_sum` | Whether the requested path sum exists |
| `diameter_edges` | Longest path between two nodes in edges |
| `is_balanced` | Whether every node satisfies the height-balance rule |
| `node_count` | Total number of reachable nodes |

The function first traverses the tree to calculate depth and accumulated path sum. It then processes nodes in descending depth order.

JSONB maps retain already calculated child heights and balance states, allowing each parent to calculate its own metrics.

`count_complete_tree_nodes()` assigns heap positions recursively. A complete tree must occupy every position from one through its node count. Gaps therefore cause the function to reject the snapshot.

The SQL implementation is designed as a relational learning model. Its repeated structural validation and JSONB intermediate state are suitable for small datasets, not a substitute for specialized large-scale tree-processing infrastructure.

## Algorithm Comparison

| Problem | Main technique | Time complexity | Additional space |
|---|---|---:|---:|
| Maximum depth | Breadth-first search | `O(n)` | `O(w)` |
| Minimum depth | Breadth-first search with early exit | `O(n)` worst case | `O(w)` |
| Path sum | Depth-first search | `O(n)` | `O(h)` |
| Diameter | Postorder traversal | `O(n)` | `O(n)` |
| Balanced tree | Postorder height calculation | `O(n)` | `O(n)` |
| General node count | Tree traversal | `O(n)` | `O(n)` |
| Complete-tree validation | Level-order traversal | `O(n)` | `O(w)` |
| Complete-tree counting | Repeated height calculation | `O(log² n)` after validation | `O(1)` |

Where:

- `n` is the total number of nodes.
- `h` is the tree height.
- `w` is the maximum number of nodes at a level.

A balanced tree often has height proportional to `log n`. A skewed tree can have height proportional to `n`.

The iterative implementations avoid call-stack growth, but they still require memory for traversal queues, stacks, or intermediate node statistics.

## Edge Cases and Operational Rules

| Case | Expected behavior |
|---|---|
| Empty tree | Depth and count are zero; balanced is true |
| Single node | Both depths are one; diameter is zero |
| Only left child | Minimum depth follows the left child |
| Only right child | Minimum depth follows the right child |
| Negative node values | Path sums include negative values |
| Target equals an intermediate path sum | Not accepted unless the node is a leaf |
| Repeated child reference | Rejected as an invalid tree |
| Circular references | Rejected as an invalid tree |
| Long unbalanced branch | Processed using iterative traversal |
| Incomplete tree | Rejected by verified complete-tree counting |
| Arithmetic overflow | Reported by fixed-width integer implementations |

The distinction between general and complete trees is important. General node counting is valid for all binary trees, while the optimized complete-tree method requires a stronger structural guarantee.

The implementations also distinguish structural validity from policy eligibility. A tree can be valid and processable while failing a balance requirement or a configured resource limit.

## Test Data

The primary sample tree is:

    10
   /  \
  5    15
 / \   / \
3   7 12 18

Its expected results are:

| Metric | Expected value |
|---|---:|
| Maximum depth | 3 |
| Minimum depth | 3 |
| Path sum 22 | True |
| Diameter in edges | 4 |
| Balanced | True |
| Node count | 7 |
| Complete | True |
| Complete-tree node count | 7 |

A skewed example is:

    5
   /
  4
 /
3
/
2

Its expected results are:

| Metric | Expected value |
|---|---:|
| Maximum depth | 4 |
| Minimum depth | 4 |
| Diameter in edges | 3 |
| Balanced | False |
| Node count | 4 |
| Complete | False |

The source files include executable assertions or checks for these cases, empty trees, negative values, malformed level-order input, shared references, and invalid complete-tree operations.

## Running the Implementations

| Deliverable | Runtime |
|---|---|
| Python | Python 3 |
| JavaScript | Node.js |
| C++17 | C++17-compatible compiler |
| Java | Java 17 |
| PostgreSQL | PostgreSQL 14 or later |

The C++ source can be compiled with a C++17 compiler. The Java source uses a single public class and can be compiled and executed without external libraries.

The SQL script creates its own `tree_lab` schema, inserts sample snapshots, publishes them, and executes retrieval, validation, aggregation, and analysis queries.

The SQL script drops and recreates `tree_lab` at startup. It should therefore be run in a database where replacing that dedicated schema is acceptable.
