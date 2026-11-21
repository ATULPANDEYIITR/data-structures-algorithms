# Graph Cycle Detection

## 1. Introduction

Graph cycle detection determines whether a graph contains a path that returns to a previously visited vertex.

A cycle is a closed path in which the starting and ending vertices are identical, with at least one edge connecting them.

Cycle detection is important in:

- Software dependency management.
- Build-system dependency validation.
- Network topology analysis.
- Deadlock detection.
- Scheduling and task dependency validation.
- Database relationship analysis.
- Resource allocation.
- Circuit and infrastructure analysis.

A graph can be directed or undirected. The distinction changes how a cycle must be identified.

The implementations in this project cover Depth-First Search (DFS), Breadth-First Search (BFS), Kahn's topological sorting algorithm, and Disjoint Set Union (DSU).

## 2. Graph Fundamentals

A graph is represented as:

\[
G=(V,E)
\]

Where:

- \(V\) represents the set of vertices.
- \(E\) represents the set of edges.
- An edge represents a relationship between two vertices.

For example:

\[
V=\{0,1,2,3\}
\]

\[
E=\{(0,1),(1,2),(2,3)\}
\]

This graph contains four vertices and three edges.

### Directed graph

A directed edge has a defined direction.

An edge:

\[
(u,v)
\]

means that traversal is possible from \(u\) to \(v\).

It does not automatically imply that traversal is possible from \(v\) to \(u\).

Example:

\[
0\rightarrow1\rightarrow2\rightarrow3
\]

A directed cycle exists when a sequence of directed edges returns to its starting vertex.

Example:

\[
0\rightarrow1\rightarrow2\rightarrow0
\]

### Undirected graph

An undirected edge has no direction.

An edge between \(u\) and \(v\) allows traversal in both directions.

Example:

\[
0-1-2-0
\]

The graph contains a cycle because the vertices form a closed path.

### Simple graphs and multigraphs

A simple graph does not contain self-loops or parallel edges.

A multigraph may contain multiple edges connecting the same pair of vertices.

A self-loop is an edge connecting a vertex to itself.

\[
(u,u)
\]

A self-loop represents a cycle.

Parallel edges also require special consideration. Two parallel undirected edges between the same vertices form a cycle of length two under the multigraph convention used by the DSU implementation.

## 3. Graph Representation

The implementations use adjacency lists.

An adjacency list stores the neighbors of each vertex.

Example:

| Vertex | Neighbors |
|---|---|
| 0 | 1, 2 |
| 1 | 2 |
| 2 | 3 |
| 3 | 0 |

For a directed graph, only outgoing neighbors are stored.

For an undirected graph, both directions are stored.

If an undirected edge connects vertices 0 and 1, the adjacency lists contain:

- Vertex 0: neighbor 1.
- Vertex 1: neighbor 0.

The adjacency-list representation requires:

\[
O(V+E)
\]

space.

For undirected graphs, each edge normally contributes two adjacency entries.

The implementations also maintain an edge list where required. This is particularly useful for DSU because each undirected edge can be processed exactly once.

## 4. Directed Cycle Detection Using DFS

### 4.1 Core mechanism

Depth-First Search explores a graph by following one path as deeply as possible before backtracking.

Directed cycle detection requires distinguishing between three vertex states.

| State | Meaning |
|---|---|
| WHITE | Not visited |
| GRAY | Currently being explored |
| BLACK | Fully processed |

The states represent the following progression:

`WHITE → GRAY → BLACK`

A directed cycle exists when DFS encounters an edge from the current vertex to a GRAY vertex.

Such an edge is called a back edge.

A GRAY vertex belongs to the active DFS path. Returning to it establishes a directed cycle.

### 4.2 Example

Consider:

\[
0\rightarrow1\rightarrow2\rightarrow3
\]

and:

\[
3\rightarrow1
\]

DFS follows:

`0 → 1 → 2 → 3`

At vertex 3, the edge to vertex 1 is examined.

Vertex 1 is still GRAY.

Therefore, the graph contains:

\[
1\rightarrow2\rightarrow3\rightarrow1
\]

### 4.3 Cycle reconstruction

The DFS implementations maintain a parent array.

When a back edge is discovered, parent relationships are followed to reconstruct the cycle.

For the example above:

`1 → 2 → 3 → 1`

The reconstructed sequence includes the starting vertex at both ends.

### 4.4 Complexity

| Operation | Complexity |
|---|---|
| Initialization | \(O(V)\) |
| DFS traversal | \(O(V+E)\) |
| Cycle reconstruction | \(O(V)\) |
| Total time | \(O(V+E)\) |
| Auxiliary space | \(O(V)\) |

The adjacency list requires another \(O(V+E)\) space.

### 4.5 Important distinction

An edge to any previously visited vertex does not necessarily indicate a directed cycle.

The target must be in the current recursion path.

An edge to a BLACK vertex does not establish a cycle.

This distinction prevents incorrect cycle detection in graphs containing cross edges.

## 5. Directed Cycle Detection Using BFS

### 5.1 Kahn's algorithm

Kahn's algorithm detects directed cycles through topological sorting.

A topological ordering is a linear arrangement of vertices in which every directed edge points from an earlier vertex to a later vertex.

A directed graph has a topological ordering if and only if it is a Directed Acyclic Graph (DAG).

The algorithm uses indegree.

Indegree represents the number of incoming edges to a vertex.

For vertex \(v\):

\[
indegree(v)=|\{(u,v)\in E\}|
\]

### 5.2 Processing procedure

1. Calculate the indegree of every vertex.
2. Insert all zero-indegree vertices into a queue.
3. Remove a vertex from the queue.
4. Process its outgoing edges.
5. Decrease the indegree of each destination.
6. Insert destinations whose indegree becomes zero.
7. Continue until the queue is empty.

The number of processed vertices determines whether a cycle exists.

\[
\text{Cycle exists}
\iff
\text{Processed vertices}<V
\]

### 5.3 Example

Consider:

\[
0\rightarrow1
\]

\[
1\rightarrow2
\]

\[
2\rightarrow3
\]

\[
3\rightarrow1
\]

The indegrees are:

| Vertex | Indegree |
|---|---:|
| 0 | 0 |
| 1 | 2 |
| 2 | 1 |
| 3 | 1 |

Only vertex 0 enters the initial queue.

After processing vertex 0, the remaining vertices cannot become zero-indegree because the cycle maintains their incoming dependencies.

The processed count is smaller than the total vertex count.

Therefore, a cycle exists.

### 5.4 Complexity

| Operation | Complexity |
|---|---|
| Calculate indegrees | \(O(V+E)\) |
| Queue processing | \(O(V+E)\) |
| Total time | \(O(V+E)\) |
| Auxiliary space | \(O(V)\) |

### 5.5 DFS versus Kahn's algorithm

Both algorithms detect directed cycles in linear time.

Their operational differences are:

| Characteristic | DFS | Kahn's BFS |
|---|---|---|
| Main structure | Stack or recursion | Queue |
| Main tracking | Three vertex states | Indegree |
| Cycle evidence | Back edge | Unprocessed vertices |
| Topological ordering | Requires postorder processing | Produced directly |
| Cycle path | Can reconstruct a path | Does not directly reconstruct one |
| Main application | Structural cycle analysis | Dependency scheduling |

Kahn's algorithm is particularly useful for build systems and task scheduling.

DFS is useful when an actual cycle path is required.

## 6. Undirected Cycle Detection Using DFS

### 6.1 Parent tracking

In an undirected graph, every edge appears in both adjacency lists.

Suppose DFS traverses:

\[
0-1
\]

When vertex 1 examines vertex 0, it encounters an already visited vertex.

This is not a cycle. Vertex 0 is simply the parent of vertex 1.

Therefore, the algorithm maintains the parent of each vertex.

A cycle is detected when an already visited neighbor is not the current vertex's parent.

### 6.2 Example

Consider:

\[
0-1,\quad1-2,\quad2-0
\]

DFS traverses:

`0 → 1 → 2`

Vertex 2 encounters vertex 0.

Vertex 0 is not the parent of vertex 2.

The graph therefore contains a cycle.

### 6.3 Complexity

\[
Time=O(V+E)
\]

\[
Auxiliary\ Space=O(V)
\]

The algorithm also examines disconnected components by initiating DFS from every unvisited vertex.

### 6.4 Parallel-edge consideration

A basic parent-vertex implementation assumes a simple graph.

In a multigraph, two parallel edges between a parent and child must be distinguished by edge identity.

The implementations use this simplified parent rule for DFS and BFS. Their DSU implementation correctly identifies parallel edges as a cycle because it processes each edge independently.

For multigraph-safe traversal, parent edge IDs should be tracked instead of only parent vertices.

## 7. Undirected Cycle Detection Using BFS

BFS explores vertices level by level.

The undirected cycle detection procedure maintains:

- A visited array.
- A queue.
- Parent information.

For each unvisited component:

1. Insert its starting vertex into the queue.
2. Mark the starting vertex visited.
3. Remove vertices from the queue.
4. Examine their neighbors.
5. Insert unvisited neighbors and record their parents.
6. Report a cycle if an already visited neighbor is not the current vertex's parent.

The algorithm must process every connected component.

### Complexity

\[
Time=O(V+E)
\]

\[
Auxiliary\ Space=O(V)
\]

BFS is useful when level-based exploration is already part of the application.

## 8. Disjoint Set Union

### 8.1 Definition

Disjoint Set Union is a data structure that maintains a collection of non-overlapping sets.

It supports two principal operations.

**Find**

Determines the representative of the set containing a vertex.

**Union**

Combines the sets containing two vertices.

The structure is also called Union-Find.

### 8.2 Parent representation

Each vertex initially represents its own component.

For five vertices:

`0, 1, 2, 3, 4`

The initial parent relationships are:

| Vertex | Parent |
|---|---|
| 0 | 0 |
| 1 | 1 |
| 2 | 2 |
| 3 | 3 |
| 4 | 4 |

Every vertex initially belongs to a separate component.

### 8.3 Cycle detection procedure

For each undirected edge \((u,v)\):

1. Find the representative of \(u\).
2. Find the representative of \(v\).
3. If both representatives are identical, a cycle exists.
4. Otherwise, merge the two components.

The fundamental condition is:

\[
Find(u)=Find(v)
\Rightarrow
Cycle
\]

If the representatives differ, the edge joins two previously disconnected components.

### 8.4 Example

Consider:

\[
E=\{(0,1),(1,2),(2,0)\}
\]

Processing the first edge combines components 0 and 1.

Processing the second edge combines the component containing 1 with the component containing 2.

When the third edge is processed, vertices 2 and 0 already have the same representative.

The edge closes a cycle.

### 8.5 Path compression

Path compression reduces the height of the parent structure.

During a Find operation, intermediate vertices are redirected toward the root.

This improves subsequent operations.

### 8.6 Union by rank or size

Union by rank attaches a shallower tree beneath a deeper tree.

Union by size attaches the smaller component beneath the larger component.

Both techniques prevent unnecessarily tall trees.

### 8.7 Complexity

With path compression and union by rank or size:

\[
O(\alpha(V))
\]

is the amortized complexity of an individual operation.

Here, \(\alpha\) is the inverse Ackermann function, which grows extremely slowly.

Processing all edges requires:

\[
O(V+E\alpha(V))
\]

including initialization.

Auxiliary space is:

\[
O(V)
\]

### 8.8 DSU limitations

DSU is designed for undirected connectivity.

It does not directly identify directed cycles.

A directed graph can contain a cycle even when an edge connects vertices belonging to different undirected components.

Applying ordinary DSU cycle detection to directed edges therefore produces incorrect results.

## 9. Mathematical Relationship Between Cycles and Forests

An undirected forest is an undirected graph without cycles.

For a graph with:

- \(V\) vertices,
- \(E\) edges,
- \(C\) connected components,

the forest condition is:

\[
E=V-C
\]

The graph contains a cycle when:

\[
E>V-C
\]

This relationship applies to undirected multigraphs when self-loops and parallel edges are counted individually.

It also handles disconnected graphs and isolated vertices.

For a connected undirected tree:

\[
E=V-1
\]

For a disconnected forest, each connected component is a tree or an isolated vertex.

This mathematical property is used in the PostgreSQL implementation to evaluate undirected cycle existence through connected-component analysis.

## 10. Implementation Architecture

The five source files provide different engineering perspectives.

| File | Main responsibility |
|---|---|
| Python | Algorithm simulation and validation |
| JavaScript | Event-driven graph monitoring |
| C++17 | Efficient graph traversal and DSU |
| Java 17 | Enterprise graph validation service |
| PostgreSQL | Relational graph storage and evaluation |

### 10.1 Python implementation

The Python implementation uses:

- `GraphType` enum for graph classification.
- `Graph` class for adjacency-list management.
- `CycleResult` dataclass for structured results.
- `deque` for BFS.
- Lists for vertex states and parent tracking.
- `DisjointSet` for undirected connectivity.

The directed DFS implementation reconstructs an actual cycle path.

Kahn's algorithm identifies cyclic graphs by comparing processed and total vertices.

The test suite covers:

- Directed cycles.
- Directed acyclic graphs.
- Undirected trees.
- Undirected cycles.
- Self-loops.
- Parallel edges.
- Disconnected graphs.
- Empty graphs.
- Invalid vertices.
- Invalid algorithm and graph-type combinations.

Python's recursive DFS is straightforward but can exceed the interpreter recursion limit on very deep graphs. An iterative DFS is preferable for large production graphs.

### 10.2 JavaScript implementation

The JavaScript implementation introduces an event-driven architecture.

`GraphMonitor` manages graph changes and exposes events.

The main events are:

| Event | Meaning |
|---|---|
| `edgeAdded` | A new edge has been registered |
| `evaluated` | A cycle evaluation has completed |

Listeners can subscribe to events and unsubscribe when they no longer need notifications.

A listener failure is isolated so that other listeners can continue receiving events.

The evaluation method returns a Promise, establishing an asynchronous service boundary.

The DSU implementation uses iterative path compression and union by size.

The JavaScript implementation is particularly relevant to systems that monitor changing dependency structures or expose graph evaluation through asynchronous services.

Event-driven monitoring does not automatically maintain a correct cycle result after every edge insertion. Evaluation is explicitly requested because the appropriate algorithm depends on the graph type.

### 10.3 C++17 implementation

The C++ program uses:

- `vector` for adjacency lists.
- `vector<bool>` for visited states.
- `vector<int>` for parent and indegree tracking.
- `function` for recursive DFS.
- `pair<int,int>` for edge representation.
- STL algorithms for array initialization and reversal.
- Exceptions for invalid inputs.

The implementation uses iterative DSU path compression and union by size.

Its main emphasis is efficient data structures, explicit memory management through STL containers, and predictable graph-processing behavior.

For very large or deeply nested graphs, iterative DFS is preferable to recursive DFS because recursion consumes call-stack memory.

### 10.4 Java 17 implementation

The Java implementation uses explicit domain types and a service-oriented architecture.

Its domain model includes:

- `GraphType`
- `DetectionStatus`
- `Edge`
- `CycleResult`
- `RepositoryPolicy`
- `Graph`

The `GraphGovernanceService` applies graph submission rules before accepting a graph.

Its responsibilities include:

1. Checking vertex-count limits.
2. Checking edge-count limits.
3. Enforcing self-loop restrictions.
4. Enforcing parallel-edge restrictions.
5. Applying the required acyclic-graph policy.
6. Rejecting invalid submissions with specific exceptions.

`GraphCycleException` preserves the detection result, allowing calling services to inspect the failure.

The design separates graph algorithms from business validation.

This distinction is important in enterprise applications where graph correctness is one part of a larger submission or processing workflow.

## 11. PostgreSQL Relational Model

The SQL implementation models graphs as relational entities.

The primary relationships are:

`Graphs → Vertices → Edges → Detection Runs`

### 11.1 Graph registry

The `graphs` table stores graph-level metadata.

Important attributes include:

- `graph_id`
- `graph_name`
- `graph_kind`
- `vertex_count`
- `status`
- `created_at`

The graph type determines which detection algorithms are valid.

### 11.2 Vertex storage

The `vertices` table identifies vertices within a graph.

The composite primary key is:

\[
(graph\_id,vertex\_id)
\]

This prevents duplicate vertex identifiers within the same graph while allowing different graphs to use the same vertex identifiers.

### 11.3 Edge storage

The `edges` table records connections between vertices.

Each edge references both endpoint vertices through composite foreign keys.

The independent `edge_id` allows parallel edges to be represented.

For an undirected graph, an edge is stored once. Its interpretation is bidirectional.

### 11.4 Detection records

The `detection_runs` table stores the results of algorithm executions.

It records:

- Graph identifier.
- Algorithm.
- Cycle status.
- Reconstructed cycle where available.
- Processed vertex count.
- Execution time.
- Execution timestamp.
- Additional JSON metadata.

This separates graph data from evaluation history.

A graph can therefore be evaluated multiple times without replacing its original edge records.

### 11.5 Constraints and triggers

The database enforces:

- Non-negative vertex counts.
- Unique graph names.
- Valid vertex references.
- Valid edge endpoints.
- Graph-specific vertex ranges.
- Controlled graph mutation after validation.

The vertex trigger checks whether a vertex identifier is within the configured graph range.

The edge trigger prevents changes to graphs that have already entered a terminal validation state.

Foreign keys provide referential integrity independently of application-level validation.

### 11.6 Database functions

The SQL file provides functions for:

| Function | Responsibility |
|---|---|
| `create_graph` | Creates a graph and its vertices |
| `add_graph_edge` | Registers an edge |
| `detect_directed_cycle_dfs` | Evaluates directed cycles using recursive paths |
| `detect_directed_cycle_kahn` | Performs indegree-based evaluation |
| `detect_undirected_cycle_dsu` | Evaluates the undirected forest condition |
| `evaluate_graph` | Executes an algorithm and records its result |

The directed DFS function uses recursive SQL path enumeration.

The Kahn implementation maintains a temporary indegree table and processes zero-indegree vertices.

The undirected DSU-equivalent function computes connected components through recursive reachability and applies the forest condition:

\[
E=V-C
\]

These relational implementations demonstrate the underlying properties of the algorithms rather than providing the same execution characteristics as in-memory DSU.

## 12. Example Workflows

### 12.1 Software dependency validation

Suppose a build system has these dependencies:

\[
A\rightarrow B
\]

\[
A\rightarrow C
\]

\[
B\rightarrow D
\]

\[
C\rightarrow D
\]

\[
D\rightarrow E
\]

This is a DAG.

Kahn's algorithm can generate a valid build order.

If a dependency is added:

\[
E\rightarrow A
\]

a directed cycle is created.

The build system cannot establish a valid topological order.

Directed cycle detection identifies the dependency problem before execution.

### 12.2 Network infrastructure

Suppose network devices are represented as vertices and physical connections as undirected edges.

A network containing:

\[
0-1,\quad1-2,\quad2-0
\]

has a cycle.

DSU identifies this condition when the final edge connects vertices already belonging to the same component.

This is useful for connectivity and topology validation.

The presence of a cycle is not automatically an error in network design. Redundant network paths can be intentional.

The required policy depends on the application.

### 12.3 Task scheduling

Tasks can be represented as vertices.

A directed edge indicates that one task must be completed before another.

A cycle such as:

\[
Task_A\rightarrow Task_B
\]

\[
Task_B\rightarrow Task_C
\]

\[
Task_C\rightarrow Task_A
\]

creates mutually dependent tasks.

No valid topological schedule exists.

Kahn's algorithm provides a practical validation mechanism.

### 12.4 Disconnected graph validation

Consider:

\[
V=\{0,1,2,3,4,5\}
\]

\[
E=\{(0,1),(2,3),(4,5)\}
\]

The graph contains three disconnected components.

It has:

\[
V=6,\quad E=3,\quad C=3
\]

Therefore:

\[
E=V-C
\]

The graph is a forest.

Cycle detection must inspect all components rather than assuming that every vertex is reachable from vertex zero.

## 13. Edge Cases and Failure Handling

| Case | Expected behavior |
|---|---|
| Empty graph | No cycle |
| Single isolated vertex | No cycle |
| Directed self-loop | Cycle |
| Undirected self-loop | Cycle |
| Directed back edge | Cycle |
| Undirected tree | No cycle |
| Disconnected forest | No cycle |
| Undirected triangle | Cycle |
| Parallel undirected edges | Cycle under multigraph convention |
| Invalid vertex | Reject input |
| Negative vertex count | Reject graph creation |
| Directed algorithm on undirected graph | Reject operation |
| Undirected DSU on directed graph | Reject operation |

### Self-loops

A self-loop immediately establishes a cycle.

DFS detects it as an edge to the current GRAY vertex in a directed graph.

DSU detects it because both endpoints have the same representative.

### Disconnected components

Every DFS and BFS implementation starts a new traversal for each unvisited vertex.

DSU naturally supports multiple components.

### Parallel edges

DSU processes each edge independently.

The first edge joins the components.

A second edge between the same vertices finds identical representatives and reports a cycle.

Parent-vertex DFS and BFS require additional edge-ID handling if parallel edges must be treated correctly.

### Invalid input

All implementations validate vertex identifiers and graph dimensions.

Invalid graph-type and algorithm combinations are rejected rather than silently producing results.

## 14. Complexity Comparison

Let:

- \(V\) represent the number of vertices.
- \(E\) represent the number of edges.
- \(\alpha(V)\) represent the inverse Ackermann function.

| Algorithm | Graph type | Time complexity | Auxiliary space |
|---|---|---|---|
| DFS | Directed | \(O(V+E)\) | \(O(V)\) |
| Kahn BFS | Directed | \(O(V+E)\) | \(O(V)\) |
| DFS | Undirected | \(O(V+E)\) | \(O(V)\) |
| BFS | Undirected | \(O(V+E)\) | \(O(V)\) |
| DSU | Undirected | \(O(V+E\alpha(V))\) | \(O(V)\) |

All adjacency-list graph implementations require \(O(V+E)\) storage.

DSU is especially efficient when edges arrive incrementally and only undirected connectivity needs to be maintained.

DFS and BFS provide broader traversal capabilities.

## 15. Algorithm Selection

| Requirement | Suitable algorithm |
|---|---|
| Find a directed cycle path | Directed DFS |
| Check whether a directed graph is cyclic | DFS or Kahn BFS |
| Generate a topological order | Kahn BFS |
| Detect cycles in an undirected tree-like structure | DFS or BFS |
| Process undirected edges incrementally | DSU |
| Maintain connected components | DSU |
| Validate dependency scheduling | Kahn BFS |
| Inspect disconnected graph components | DFS or BFS |
| Detect parallel-edge cycles | DSU or edge-ID-aware traversal |

The correct algorithm depends on graph direction, required output, graph size, and whether the graph changes over time.

## 16. Performance and Security Considerations

### Memory management

Adjacency lists are generally preferable to adjacency matrices for sparse graphs.

An adjacency matrix requires:

\[
O(V^2)
\]

space.

An adjacency list requires:

\[
O(V+E)
\]

space.

For large sparse graphs, the difference can be substantial.

### Recursive traversal

Recursive DFS can exhaust the call stack when a graph contains a very long path.

An iterative DFS using an explicit stack avoids dependence on the language's recursion limit.

### Input validation

External graph input must be validated before allocation or traversal.

Important checks include:

- Non-negative vertex count.
- Valid endpoint identifiers.
- Maximum vertex count.
- Maximum edge count.
- Valid graph type.
- Duplicate-edge policy.
- Self-loop policy.

### Integer limits

Large graph identifiers and edge counts require suitable integer types.

The PostgreSQL implementation uses `BIGINT` for database identifiers and `INTEGER` for vertex identifiers.

The C++ implementation uses integer vertex identifiers, so applications with larger identifier ranges should adopt suitable wider integer types.

### Database integrity

Foreign keys prevent edges from referencing nonexistent vertices.

Transactions ensure that graph creation and edge registration can be rolled back when validation fails.

Indexes on graph identifiers and edge endpoints support graph retrieval.

### Concurrency

When multiple processes modify a graph simultaneously, cycle evaluation must consider the graph state consistently.

A cycle result is only valid for the graph version that was evaluated.

Production systems should use transaction isolation, locking, or immutable graph versions to prevent concurrent modifications from invalidating an evaluation result.

### Access control

Applications that accept externally submitted graphs should enforce authorization and resource limits before processing.

Database permissions should restrict direct modifications to graph tables where stored procedures are intended to control state transitions.

## 17. Practical Distinctions

The four major algorithmic approaches solve related but different problems.

**Directed DFS** identifies a back edge in the active traversal path.

**Kahn's BFS** identifies whether all vertices can be removed through zero-indegree processing.

**Undirected DFS and BFS** identify connections to previously visited vertices other than the traversal parent.

**Disjoint Set Union** detects whether an undirected edge connects vertices that are already connected.

These mechanisms should not be treated as interchangeable.

The choice between them should be based on graph direction, required output, update frequency, and operational constraints.

The implementations establish a common graph model while demonstrating different algorithmic and software-engineering approaches.
