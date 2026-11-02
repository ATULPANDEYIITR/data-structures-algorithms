# Binary Tree Properties

## Scope

This project models and analyzes the structural properties of binary trees through five complementary implementations:

| File | Technical perspective | Main purpose |
|---|---|---|
| Python | Object-oriented structural analysis | Build trees, calculate properties, validate invariants, and persist a profile |
| JavaScript | Event-driven policy model | Emit traversal events, evaluate structural policies, and persist results asynchronously |
| C++17 | Governance engine | Evaluate tree structure through explicit ownership, STL algorithms, and policy decisions |
| Java 17 | Enterprise domain model | Separate domain types, services, policies, validation, and reporting |
| PostgreSQL | Relational structural model | Store trees and nodes, enforce structural constraints, calculate metrics, and report eligibility |

The central domain is the structural analysis of a binary tree. The implementations distinguish height, diameter, balanced structure, leaves, internal nodes, full trees, complete trees, and perfect trees rather than treating these properties as interchangeable.

## Structural Model

A binary tree contains nodes where each node has at most two children.

The domain relationship is:

`Binary Tree → Root → Internal Nodes → Child Nodes → Leaf Nodes`

A node is classified as a leaf when it has no children. A node is internal when it has at least one child.

For a non-empty full binary tree:

`number of leaves = number of internal nodes + 1`

That identity is not true for every binary tree. The implementations therefore evaluate it only when the tree satisfies the full-tree condition.

## Height

Height is represented in edges.

- Empty tree: `-1`
- Single-node tree: `0`
- A root-to-leaf path containing three edges has height `3`

A second node-based representation is reported as `heightEdges + 1` for non-empty trees.

This distinction avoids ambiguity between common edge-based and node-based definitions.

The height calculation follows:

`height(node) = 1 + max(height(left), height(right))`

The empty subtree contributes `-1` in edge-based calculations.

## Diameter

The diameter is the maximum number of edges on a path between two nodes.

The efficient implementations calculate height and diameter together during a post-order traversal. For a node, a path passing through that node can have length:

`leftHeight + rightHeight + 2`

The final diameter is the maximum of:

- the left-subtree diameter
- the right-subtree diameter
- the path passing through the current node

This gives `O(n)` time for a tree with `n` nodes.

## Balanced Trees

A tree is balanced when the heights of the left and right subtrees of every node differ by no more than one.

The implementations avoid repeatedly recalculating subtree heights. Each subtree returns its height while propagating an invalid marker when an imbalance is detected.

This makes balance checking `O(n)` rather than repeatedly traversing subtrees.

A long one-sided chain is deliberately included as a failure case. Its height and diameter increase linearly with the number of nodes, while the balance condition eventually fails.

## Leaf and Internal Nodes

The implementations explicitly count both categories.

For each node:

- Leaf: zero children
- Internal: one or two children

The number of internal nodes is derived as:

`internal = total nodes - leaves`

This relationship is useful because a binary tree may be sparse, full, complete, perfect, or merely balanced. These classifications describe different structural properties.

## Full, Complete, and Perfect Trees

### Full

A full binary tree requires every node to have either:

- zero children, or
- two children

A node with exactly one child violates the condition.

### Complete

A complete binary tree has every level filled except possibly the last, and nodes on the last level occur from left to right without gaps.

The implementations use breadth-first traversal and mark the first missing child. Once a missing child has been observed, a later child makes the tree incomplete.

### Perfect

A perfect binary tree is both structurally full and level-uniform:

- every internal node has two children
- every leaf occurs at the same depth

The implementation records the first leaf depth and requires all later leaves to have that same depth.

A perfect tree is therefore more restrictive than a full or balanced tree.

## Relationship Between Properties

The project intentionally keeps the properties separate.

| Property | Requirement |
|---|---|
| Height | Longest root-to-leaf path |
| Diameter | Longest path between any two nodes |
| Balanced | Local subtree heights differ by at most one |
| Leaf | Zero children |
| Internal | At least one child |
| Full | Every node has zero or two children |
| Complete | Last level is left-filled |
| Perfect | Full and all leaves have equal depth |

A tree can be balanced without being perfect. A tree can be full without being complete. A complete tree can have a different diameter from another complete tree with the same number of nodes.

## Python Implementation

The Python implementation uses `TreeNode` and `BinaryTree` classes with `dataclass` support for compact domain objects.

`from_level_order()` constructs trees from level-order input while rejecting unreachable non-null values.

The implementation provides:

- node counting
- leaf counting
- internal-node counting
- edge-based height
- diameter
- balance checking
- full-tree checking
- complete-tree checking
- perfect-tree checking
- preorder, inorder, postorder, and level-order traversal
- structural validation
- JSON profile persistence
- executable assertions

The `structural_profile()` method provides one consolidated representation of the calculated properties.

Validation also detects repeated node references and self-references. This is important because a malformed object graph can otherwise cause recursive algorithms to loop indefinitely.

The output file is restricted to the current working directory rather than accepting an arbitrary filesystem path.

## JavaScript Implementation

The JavaScript implementation uses Node.js standard-library facilities and introduces an event-driven perspective.

`BinaryTree` extends `EventEmitter`.

Traversal emits `visit` events containing:

- node value
- traversal phase

Profile calculation emits a `profile` event after structural analysis.

This separates structural computation from consumers that may want to observe traversal activity.

The implementation also defines `GovernancePolicy`, which evaluates a structural profile against:

- maximum permitted height
- required balance
- required completeness

The policy returns an explicit eligibility result and a list of violations.

Asynchronous file persistence uses `fs.promises.writeFile()`. The output file is created with restrictive permissions and is constrained to the current working directory.

## C++17 Implementation

The C++ implementation emphasizes ownership and explicit governance.

`TreeNode` owns its children through `std::unique_ptr`. This makes node lifetime deterministic and avoids manual memory management.

The `BinaryTree` class provides:

- level-order construction
- node and leaf counting
- height
- diameter
- balance checking
- full-tree checking
- complete-tree checking
- perfect-tree checking
- structural profiling

The diameter calculation returns height and diameter together through a recursive helper.

The governance layer is represented separately by `GovernanceEngine`. It applies structural requirements such as maximum height, balance, and completeness and returns an explicit `MergeDecision`.

This separates structural measurement from policy evaluation.

The program also writes a compact profile to a fixed local output file and validates failures through C++ exceptions.

## Java 17 Implementation

The Java implementation separates domain modeling from policy and reporting.

The main domain types are:

- `TreeNode`
- `TreeProfile`
- `Policy`
- `PolicyDecision`
- `TreePolicy`
- `StructuralPolicy`
- `TreeService`
- `ReportService`

Records are used for immutable value-oriented results such as `TreeProfile`, `Policy`, and `PolicyDecision`.

The `TreePolicy` interface makes structural policy evaluation independent from the tree traversal service.

`TreeService` owns the tree and performs validation and structural calculations.

`ReportService` converts a calculated profile into a persistent textual representation.

The implementation explicitly models failure conditions, including invalid parent relationships, repeated node references, self-references, unreachable level-order nodes, and policy violations.

This organization resembles an enterprise service design in which domain state, policy evaluation, and reporting have separate responsibilities.

## PostgreSQL Model

The PostgreSQL implementation represents the tree as relational data.

The principal tables are:

- `trees`
- `tree_nodes`
- `tree_metrics`

`tree_nodes` stores:

- parent relationship
- node value
- node classification
- depth
- left/right/root position

The database uses foreign keys, unique constraints, check constraints, partial indexes, triggers, functions, views, recursive CTEs, and transactions.

The `one_root_per_tree` partial unique index ensures that each tree has at most one root.

The `(tree_id, parent_node_id, position)` uniqueness rule prevents a parent from receiving two nodes in the same left or right position.

The parent-validation trigger verifies:

- parent existence
- same-tree membership
- correct depth
- valid position
- absence of self-reference

## Recursive SQL Analysis

Recursive CTEs represent the hierarchical relationship between parents and descendants.

They are used to derive:

- node counts
- leaf counts
- maximum depth
- internal-node counts
- diameter
- balance conditions
- full-tree conditions
- complete-tree conditions
- perfect-tree conditions

The database stores calculated metrics in `tree_metrics` so reporting queries do not need to recompute every property repeatedly.

For a large production tree workload, the same design could be extended with incremental subtree metrics. The supplied model favors transparent relational analysis over premature optimization.

## Sample Structural Cases

The dataset includes five structurally distinct cases.

| Tree | Intended structure |
|---|---|
| `balanced_complete` | Balanced, full, complete, and perfect |
| `unbalanced_chain` | Deep one-sided structure |
| `perfect_tree` | Perfect binary tree |
| `full_not_perfect` | Full but not perfect |
| `single_node` | One-node edge case |

These cases make structural distinctions observable rather than theoretical.

## Validation and Failure Handling

The implementations validate important malformed inputs.

Examples include:

- empty trees
- single-node trees
- unreachable level-order nodes
- one-child structures
- long chains
- self-references
- repeated node references
- invalid parent relationships
- cross-tree parent relationships
- incorrect depth values
- invalid left/right positions
- policy violations

The goal is to make structural properties dependent on valid tree state rather than silently accepting malformed data.

## Complexity

For a tree containing `n` nodes:

| Operation | Typical complexity |
|---|---:|
| Node count | `O(n)` |
| Leaf count | `O(n)` |
| Internal count | `O(n)` or derived from counts |
| Height | `O(n)` |
| Diameter | `O(n)` |
| Balance check | `O(n)` |
| Full-tree check | `O(n)` |
| Complete-tree check | `O(n)` |
| Perfect-tree check | `O(n)` |
| Standard traversals | `O(n)` |

Recursive implementations use call-stack space proportional to tree height. Iterative implementations use explicit stacks or queues and therefore make memory usage more visible.

For highly skewed trees, recursion depth can become a practical limitation in languages with constrained call stacks. The Python and JavaScript implementations therefore use iterative traversals for several structural checks.

## Security and Data Integrity

Tree analysis is computational rather than network-facing, but malformed structures still create reliability risks.

Important controls include:

- rejecting self-references
- detecting repeated node references
- validating parent relationships
- enforcing same-tree membership
- enforcing one root
- restricting generated output paths
- using database constraints for structural invariants
- separating policy decisions from measurement
- avoiding unbounded external input processing

The PostgreSQL implementation places critical structural rules close to the data, reducing dependence on application-side validation alone.

## Execution Model

The Python program can be run directly with a Python 3 interpreter.

The JavaScript program requires a Node.js runtime.

The C++ program requires a C++17-compatible compiler.

The Java program requires Java 17 or later.

The SQL script is designed for PostgreSQL and creates its own `binary_tree_lab` schema after removing any prior copy of that schema.

Each implementation performs executable validation against balanced, unbalanced, single-node, and empty-tree cases.

## Practical Interpretation

A binary tree's structure cannot be described by height alone.

Two trees can have the same number of nodes but different heights, diameters, balance characteristics, leaf counts, and completeness properties. The project therefore treats structural analysis as a collection of related measurements and predicates.

The most important distinction is between measurement and classification:

`nodes → measurements → structural predicates → policy decision`

Measurements such as height and diameter describe the tree. Predicates such as balanced, full, complete, and perfect classify it. A policy can then consume those classifications to determine whether a particular structural requirement is satisfied.
