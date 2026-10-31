# Binary Trees Introduction

## Scope

This project implements the fundamental structure and terminology of binary trees through five independent technical implementations.

The central model is a binary tree in which every node has at most two children:

```text
                 50
               /    \
             25      75
            /  \    /  \
          10   35  60   90
                         /
                        80
```

The implementations focus on the structural relationships that make binary trees distinct from linear data structures.

The four major concepts represented in the implementation are:

| Concept | Meaning |
|---|---|
| Root | The unique starting node of a non-empty tree |
| Parent | A node directly above another node |
| Child | A node directly below another node |
| Leaf | A node with no children |
| Internal node | A non-root node with at least one child |
| Degree | Number of children belonging to a node |
| Depth | Number of edges from the root to a node |
| Level | Depth plus one when the root is assigned level 1 |
| Height | Maximum depth of any node, measured here in edges |
| Subtree | A node together with all of its descendants |

## Binary Tree Structure

A binary tree restricts each node to zero, one, or two children.

A node can therefore have:

- degree `0`: leaf
- degree `1`: one-child internal node
- degree `2`: two-child internal node

For the sample structure:

| Node | Parent | Children | Degree | Depth | Level | Classification |
|---|---|---|---|---|---|---|
| 50 | none | 25, 75 | 2 | 0 | 1 | Root |
| 25 | 50 | 10, 35 | 2 | 1 | 2 | Internal |
| 75 | 50 | 60, 90 | 2 | 1 | 2 | Internal |
| 10 | 25 | none | 0 | 2 | 3 | Leaf |
| 35 | 25 | none | 0 | 2 | 3 | Leaf |
| 60 | 75 | none | 0 | 2 | 3 | Leaf |
| 90 | 75 | 80 | 1 | 2 | 3 | Internal |
| 80 | 90 | none | 0 | 3 | 4 | Leaf |

The root is not defined by its value. It is defined by having no parent.

A leaf is not defined by its position in the diagram. It is defined by having no children.

## Depth, Level, and Height

Depth and level describe an individual node relative to the root.

The root has depth `0`. If the root is considered level `1`, then:

`level = depth + 1`

For example, node `80` has three edges between itself and the root:

```text
50
 |
75
 |
90
 |
80
```

Therefore:

- depth of `80` = `3`
- level of `80` = `4`

Height describes the entire tree or the height of a particular subtree.

For this project, height is measured in edges. An empty tree has height `-1`, a single-node tree has height `0`, and a tree whose deepest node is three edges below the root has height `3`.

This convention is important because other textbooks sometimes define height using the number of nodes on the longest path instead.

## Subtrees

Every node can be treated as the root of a smaller tree.

For node `75`, its subtree is:

```text
       75
      /  \
    60    90
          /
         80
```

The subtree includes node `75` and every descendant reachable through its child relationships.

The implementations expose subtree-oriented behavior through node lookup and descendant traversal where appropriate.

## Python Implementation

The Python implementation uses a `TreeNode` dataclass and a `BinaryTree` service class.

The implementation provides:

- node creation
- root detection
- parent lookup
- child lookup
- degree calculation
- depth calculation
- level calculation
- tree height
- subtree traversal
- preorder traversal
- inorder traversal
- postorder traversal
- level-order traversal
- duplicate-value validation
- empty-tree handling
- single-node handling
- skewed-tree handling
- executable assertions

Breadth-first traversal uses `collections.deque`, which provides efficient queue operations.

Recursive traversal is used for height and depth-independent preorder, inorder, and postorder operations. Level-order operations use an explicit queue.

The validation routine detects duplicate values because the sample API uses node values as convenient identifiers. A production tree implementation could instead assign a separate immutable node identifier and permit duplicate values.

## JavaScript Implementation

The JavaScript implementation uses classes, `Map`, `Set`, asynchronous methods, and event-driven inspection.

`TreeNode` represents the structural node. `BinaryTree` manages traversal and validation.

The implementation validates:

- node types
- cycles
- shared node references
- missing nodes
- calculated depth and level
- empty trees

The `nodeInspected` event allows callers to observe node inspection without coupling the traversal algorithm to the reporting logic.

The asynchronous inspection API demonstrates how tree operations can fit into an event-driven Node.js workflow even when the current computation itself does not require external I/O.

The JavaScript model intentionally does not mechanically reproduce the Python API. Its emphasis is event notification, asynchronous service boundaries, and structural validation.

## C++17 Implementation

The C++ implementation models ownership explicitly with `std::unique_ptr`.

This makes the parent-to-child ownership relationship clear: each tree node owns its left and right descendants.

The program provides:

- strongly typed node storage
- explicit tree ownership
- breadth-first lookup
- depth calculation
- parent lookup
- child lookup
- degree calculation
- preorder traversal
- level-order traversal
- structural validation
- exception handling
- assertions for edge cases

`std::optional` distinguishes a missing node or missing parent from an integer value.

The implementation also checks for repeated node addresses during validation. This protects the structural assumption that a tree should not contain cycles or shared child nodes.

The use of `unique_ptr` avoids manual memory-management code and makes destruction of the complete tree automatic.

## Java 17 Implementation

The Java implementation models tree behavior as an enterprise-style service.

The domain includes:

- `TreeNode`
- `NodeInfo`
- `NodeRole`
- `TreePolicy`
- `LeafPolicy`
- `BinaryTreeService`
- `InvalidTreeException`

`NodeInfo` is a Java record that provides an immutable description of a node after inspection.

`NodeRole` explicitly distinguishes:

- `ROOT`
- `INTERNAL`
- `LEAF`

The service performs structural validation before exposing tree operations.

A policy object is used for leaf classification rather than embedding every business rule directly inside traversal code. This separates structural discovery from domain decisions.

Java collections provide the queues and sets needed for traversal and structural validation. The implementation also uses immutable lists when returning node information so callers cannot modify service-owned results.

## PostgreSQL Implementation

The PostgreSQL implementation represents a binary tree relationally.

The main entities are:

- `trees`
- `tree_nodes`

Each node stores:

- tree identifier
- node identifier
- value
- parent identifier
- left-child identifier
- right-child identifier
- creation timestamp

Foreign keys represent the parent-child relationships.

The child columns are nullable because a node may have zero or one child on either side.

The database includes:

- primary keys
- foreign keys
- unique constraints
- check constraints
- indexes
- triggers
- recursive common table expressions
- SQL functions
- views
- transactional examples
- sample records
- structural reports

The `node_classification` view identifies roots, internal nodes, and leaves.

The `tree_node_metrics` function calculates:

- parent
- degree
- depth
- level
- leaf status

The `tree_height` function calculates maximum depth using a recursive query.

The recursive traversal query follows child references from the root and produces node depth and level values.

## Relational Representation

The database representation separates the tree entity from its nodes:

```text
trees
  |
  +-- tree_nodes
        |
        +-- parent_id
        |
        +-- left_child_id
        |
        +-- right_child_id
```

This design permits multiple independent trees to exist in the same database.

The `tree_id` component in relationship constraints prevents a node from accidentally becoming a parent or child of a node belonging to another tree.

Deferred foreign keys permit a complete tree to be inserted within a transaction without requiring the rows to be inserted in strict parent-first order.

## Traversal Operations

The five implementations use several standard traversal strategies.

| Traversal | Order | Primary use |
|---|---|---|
| Preorder | Root, left, right | Processing a node before descendants |
| Inorder | Left, root, right | Ordered processing in a binary search tree |
| Postorder | Left, right, root | Processing descendants before a node |
| Level-order | Level by level | Breadth-first structural inspection |

For a binary tree with `n` nodes, a complete traversal requires `O(n)` time because every reachable node must be inspected.

Recursive depth-first traversal requires `O(h)` auxiliary stack space, where `h` is tree height.

Level-order traversal requires `O(w)` queue space, where `w` is the maximum width of the tree.

## Edge Cases

The implementations explicitly account for several boundary conditions.

### Empty Tree

An empty tree has:

- no root
- no nodes
- height `-1` under the selected edge-based convention
- no valid parent or child lookup

### Single-Node Tree

A single node is simultaneously:

- the root
- a leaf
- degree `0`
- depth `0`
- level `1`
- height `0`

### One-Child Node

A binary tree does not require every internal node to have two children.

For example:

```text
90
/
80
```

Node `90` has degree `1`. Node `80` is a leaf.

### Missing Node

A lookup for a value that is not present must not be interpreted as a root, leaf, or valid node.

The implementations return an explicit absence representation such as `None`, `null`, `Optional.empty()`, or `std::nullopt`.

### Deep or Skewed Tree

A tree can degenerate into a structure resembling a linked list:

```text
1
 \
  2
   \
    3
     \
      4
```

Its height approaches the number of nodes, making operations that depend on height potentially more expensive in recursive implementations.

## Complexity

For a tree containing `n` nodes and height `h`:

| Operation | Time | Typical auxiliary space |
|---|---|---|
| Height | `O(n)` | `O(h)` recursive or `O(w)` iterative |
| Node lookup | `O(n)` worst case | `O(w)` for breadth-first lookup |
| Parent lookup | `O(n)` worst case | `O(w)` |
| Degree lookup after node discovery | `O(1)` | `O(w)` including lookup |
| Child lookup after node discovery | `O(1)` | `O(w)` including lookup |
| Preorder traversal | `O(n)` | `O(h)` |
| Inorder traversal | `O(n)` | `O(h)` |
| Postorder traversal | `O(n)` | `O(h)` |
| Level-order traversal | `O(n)` | `O(w)` |

The exact auxiliary-space behavior depends on whether traversal is recursive or iterative.

## Validation and Structural Safety

A valid binary tree has a single root and a directed parent-to-child structure without cycles.

The implementations therefore validate structural assumptions rather than treating the diagram alone as authoritative.

Important failure conditions include:

- a node referring to itself
- cyclic child references
- a node appearing under multiple parents
- more than two children
- invalid child references
- invalid parent references
- missing nodes
- inconsistent depth calculations

Database foreign keys enforce referential integrity, while application implementations validate object relationships directly.

## Practical Distinctions

The terminology should remain precise.

A parent-child relationship is a direct relationship. A node is not the parent of a grandchild.

Depth is a node property measured from the root.

Height is a property of a tree or subtree measured downward toward its deepest descendant.

Level is a presentation convention derived from depth in this project.

Degree counts immediate children only.

A subtree includes descendants, not merely immediate children.

These distinctions are essential when implementing traversal, searching, tree metrics, and recursive algorithms.

## Relationship Between the Implementations

The five implementations use the same underlying domain but emphasize different engineering mechanisms.

| Implementation | Primary perspective |
|---|---|
| Python | Direct structural modeling, traversal, validation, and testing |
| JavaScript | Event-driven inspection and asynchronous service behavior |
| C++17 | Explicit ownership, STL traversal, and structural safety |
| Java 17 | Immutable domain objects, policy abstraction, and service-oriented modeling |
| PostgreSQL | Relational integrity, recursive queries, functions, views, and transactions |

The terminology remains consistent across all implementations while the engineering approach changes.

## Security and Reliability Considerations

Binary-tree data can be supplied from external systems, so structural validation is important before traversal.

Potential reliability problems include malformed references, cycles, extremely deep trees, unexpectedly large input, and inconsistent parent-child relationships.

For untrusted input:

- impose maximum node counts where appropriate
- impose maximum permitted depth when recursion could exhaust the call stack
- validate node references before traversal
- reject cycles
- avoid trusting client-supplied structural metrics
- use database constraints for persistent relationships
- use transactions for multi-row tree construction
- separate node identifiers from display values when duplicate values are valid

The PostgreSQL model uses foreign keys and constraints as database-level enforcement rather than relying entirely on application code.

## Terminology Reference

| Term | Precise interpretation used here |
|---|---|
| Binary tree | A tree in which each node has at most two children |
| Root | Node with no parent |
| Parent | Immediate predecessor of a node |
| Child | Immediate successor below a node |
| Leaf | Node with zero children |
| Internal node | Node with at least one child |
| Degree | Number of immediate children |
| Depth | Number of edges from root to node |
| Level | Depth plus one |
| Height | Maximum node depth in the tree |
| Subtree | A node and all descendants below it |

## File Responsibilities

The source files are deliberately independent.

The Python file is a complete executable exploration of tree terminology and traversal.

The JavaScript file provides a service-oriented and event-driven representation.

The C++17 file focuses on ownership, traversal, validation, and explicit resource management.

The Java 17 file uses enterprise-style domain types, policies, immutable result objects, and a tree service.

The PostgreSQL file provides persistent relational modeling, database constraints, recursive analysis, structural views, and transactional operations.
