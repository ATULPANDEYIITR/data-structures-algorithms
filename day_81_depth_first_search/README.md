# Depth-First Search: Graph Traversal and Exploration

## 1. Project Overview

Depth-First Search (DFS) is a fundamental graph traversal algorithm that explores vertices by following an available path as deeply as possible before returning to previously visited vertices.

DFS is used in:

- Graph connectivity analysis.
- Network exploration.
- Dependency analysis.
- Cycle detection.
- Topological sorting.
- Maze solving.
- Connected-component identification.
- Reachability analysis.
- Dependency resolution.
- Structural analysis of large networks.

This project implements DFS through five complementary technical perspectives:

| Implementation | Engineering focus |
|---|---|
| Python | Graph modeling, recursive and iterative traversal, connectivity, path detection, testing |
| JavaScript | Event-driven exploration, asynchronous traversal, graph events, structured results |
| C++17 | Efficient graph traversal, STL containers, traversal metadata, topological sorting |
| Java 17 | Enterprise-oriented domain modeling, traversal strategies, immutable results, custom exceptions |
| PostgreSQL | Relational graph storage, recursive CTEs, traversal records, connected-component reporting |

The implementations distinguish graph structure, traversal state, traversal order, reachability, and connectivity.

## 2. Graph Fundamentals

A graph is a mathematical structure consisting of:

- **Vertices (V):** Individual entities or nodes.
- **Edges (E):** Relationships connecting vertices.
- **Adjacency:** The collection of neighboring vertices.
- **Path:** A sequence of connected vertices.
- **Cycle:** A path that returns to a previously visited vertex.
- **Degree:** The number of incident edges associated with a vertex.

A graph can be represented as:

\[
G=(V,E)
\]

For example:

    1 ----- 2 ----- 4
    |       |
    |       5 ----- 6
    |               |
    3 ---------------

    7 ----- 8

    9

The graph contains nine vertices and three disconnected components.

The isolated vertex 9 is a valid graph vertex even though it has no edges.

### 2.1 Directed and undirected graphs

| Property | Directed graph | Undirected graph |
|---|---|---|
| Edge | Ordered relationship | Symmetric relationship |
| Representation | A → B | A — B |
| Reverse traversal | Not automatic | Supported |
| Example | Service dependencies | Physical network connectivity |
| Component analysis | Strongly or weakly connected components | Connected components |

A directed edge from A to B does not establish a reverse edge from B to A.

This distinction matters when evaluating reachability and connectivity.

### 2.2 Graph representation

The implementations primarily use an adjacency list.

For the sample graph:

    1: [2, 3]
    2: [1, 4, 5]
    3: [1, 6]
    4: [2]
    5: [2, 6]
    6: [3, 5]
    7: [8]
    8: [7]
    9: []

An adjacency list stores only existing relationships.

Its storage requirement is:

\[
O(V+E)
\]

For sparse graphs, this is generally more memory-efficient than an adjacency matrix, which requires:

\[
O(V^2)
\]

An adjacency matrix may still be preferable when the graph is dense or constant-time edge-existence checks are especially important.

## 3. Depth-First Search Mechanics

DFS explores one branch before exploring alternative branches.

The central mechanism is the use of a stack.

A vertex is visited, its unvisited neighbors are explored, and traversal returns when no unexplored neighbor remains.

### 3.1 Recursive DFS

Recursive DFS uses the programming language's call stack.

Its basic process is:

1. Visit the starting vertex.
2. Mark the vertex as visited.
3. Examine its neighbors.
4. Recursively explore every unvisited neighbor.
5. Return when all available neighbors have been explored.

Conceptual execution:

    DFS(1)
      |
      +-- DFS(2)
      |     |
      |     +-- DFS(4)
      |     |
      |     +-- DFS(5)
      |           |
      |           +-- DFS(6)
      |                 |
      |                 +-- DFS(3)
      |
      +-- Return

For the sample graph, the recursive traversal order is:

    1, 2, 4, 5, 6, 3

The exact order depends on adjacency-list ordering.

Recursive DFS is compact and naturally represents backtracking.

Its primary limitation is recursion depth. A sufficiently deep graph can exceed the runtime's call-stack capacity.

### 3.2 Iterative DFS

Iterative DFS uses an explicit stack.

The algorithm:

1. Push the starting vertex.
2. Mark it as visited.
3. Remove the top vertex.
4. Process its unvisited neighbors.
5. Push those neighbors onto the stack.
6. Continue until the stack is empty.

The iterative implementation reverses neighbor insertion order before pushing when matching the recursive traversal order is required.

This distinction is important because stack operations use last-in, first-out ordering.

Iterative DFS avoids dependence on the programming language's recursive call-stack limit, although the explicit stack still requires memory proportional to the explored graph.

### 3.3 Recursive versus iterative DFS

| Characteristic | Recursive | Iterative |
|---|---|---|
| Stack | Runtime call stack | Explicit stack |
| Implementation | Compact | More control over state |
| Backtracking | Automatic | Explicit |
| Deep graphs | Recursion-limit risk | Avoids recursion-limit risk |
| Memory | O(V) worst case | O(V) worst case |
| Typical use | Trees and moderate-depth graphs | Large or unpredictable graphs |

Both approaches have the same asymptotic graph traversal complexity when implemented with adjacency lists.

\[
O(V+E)
\]

## 4. Visited State and Cycle Handling

The visited set prevents repeated exploration.

Consider:

    1 ----- 2
    |       |
    3 ----- 4

Without visited-state management, traversal could repeatedly follow:

    1 → 2 → 4 → 3 → 1

A visited set ensures each vertex is processed at most once.

The implementations use:

| Language | Visited-state structure |
|---|---|
| Python | `set` |
| JavaScript | `Set` |
| C++17 | `unordered_set` |
| Java 17 | `HashSet` |
| PostgreSQL | Recursive path tracking |

Marking a vertex when it is pushed onto an iterative stack prevents the same vertex from being added repeatedly through multiple neighboring vertices.

This is particularly important in graphs containing cycles and multiple paths to the same destination.

### 4.1 Self-loops

A self-loop is an edge from a vertex to itself.

    1 → 1

The visited-state mechanism prevents an infinite traversal.

### 4.2 Duplicate edges

Repeated edges should not create repeated neighbor entries.

The implementations use sets or explicit duplicate checks to maintain adjacency integrity.

### 4.3 Disconnected vertices

A traversal beginning at vertex 1 cannot automatically reach vertices in another disconnected component.

This is why a single DFS traversal and a complete graph exploration are different operations.

## 5. Connected Components

A connected component is a maximal set of vertices in an undirected graph in which every vertex is reachable from every other vertex.

Consider:

    Component 1:
    1 ----- 2 ----- 4
    |       |
    3 ----- 5 ----- 6

    Component 2:
    7 ----- 8

    Component 3:
    9

The graph has three connected components.

The algorithm:

1. Create an empty global visited set.
2. Examine each graph vertex.
3. If the vertex has not been visited, start a new DFS.
4. Collect all vertices reached by that DFS.
5. Continue until every vertex has been examined.

The resulting components are:

- `{1, 2, 3, 4, 5, 6}`
- `{7, 8}`
- `{9}`

The complexity is:

\[
O(V+E)
\]

Every vertex is processed once and every adjacency entry is examined a bounded number of times.

### Directed graph distinction

Ordinary connected components are defined for undirected graphs.

Directed graphs require different concepts:

- **Weakly connected components:** Ignore edge direction when evaluating connectivity.
- **Strongly connected components:** Every vertex in a component must be reachable from every other vertex following edge directions.

Algorithms such as Kosaraju's and Tarjan's algorithms are appropriate for strongly connected components.

The connected-component implementations in this project explicitly reject directed graphs rather than silently applying an incorrect definition.

## 6. Reachability and Path Detection

Reachability determines whether a destination vertex can be reached from a starting vertex.

For example:

- A network administrator may check whether one server can reach another.
- A dependency manager may inspect downstream services.
- A routing application may inspect connectivity.
- A security analysis system may examine possible access paths.

The `hasPath` operation performs DFS from the source and returns immediately when the target is found.

For a graph with V vertices and E edges:

\[
O(V+E)
\]

Worst-case traversal occurs when the target does not exist in the reachable portion of the graph.

A vertex is always reachable from itself through a path of length zero.

The implementations also validate both endpoints before beginning traversal.

## 7. DFS Discovery and Finishing Times

A more advanced DFS records when vertices are entered and when exploration is completed.

Each vertex receives:

- Discovery time.
- Finishing time.
- Parent vertex.
- Depth.

The discovery time is assigned when exploration begins.

The finishing time is assigned after all available neighbors have been examined.

For a directed graph, these timestamps support edge classification:

| Edge type | Meaning |
|---|---|
| Tree edge | Discovers an unvisited vertex |
| Back edge | Connects to an active ancestor |
| Forward edge | Connects to a previously discovered descendant |
| Cross edge | Connects vertices in separate DFS branches or subtrees |

These classifications are useful in cycle detection, dependency analysis, and graph algorithms.

The Python implementation includes a directed-graph edge-classification operation.

## 8. Cycle Detection and Topological Sorting

DFS can detect cycles using three traversal states:

| State | Meaning |
|---|---|
| Unvisited | Vertex has not been explored |
| Active | Vertex is currently being explored |
| Finished | All outgoing edges have been examined |

In a directed graph, an edge to an active vertex indicates a back edge and therefore a directed cycle.

For example:

    A → B → C
    ↑       |
    |_______|

This graph contains a cycle.

### 8.1 Topological sorting

A topological ordering is a linear ordering of vertices in a directed acyclic graph (DAG) such that every directed edge points from an earlier vertex to a later vertex.

Example:

    Authentication → API Gateway
    API Gateway → Order Service
    API Gateway → Inventory Service

A valid ordering is:

    Authentication
    API Gateway
    Order Service
    Inventory Service

Another valid ordering may exchange the last two services.

DFS-based topological sorting:

1. Visit each unvisited vertex.
2. Explore its outgoing edges.
3. Detect back edges.
4. Add the vertex to the result after finishing its neighbors.
5. Reverse the resulting finishing order.

The C++17 and Java 17 implementations include cycle-aware topological sorting.

A topological ordering does not exist when the directed graph contains a cycle.

## 9. Python Implementation

The Python script provides a graph exploration model using standard-library data structures.

### Implemented mechanisms

- `Graph` dataclass for graph state.
- `GraphType` enum for directed and undirected graphs.
- Adjacency-list representation.
- Recursive DFS.
- Iterative DFS.
- Depth-limited recursive traversal.
- Connected-component identification.
- Reachability evaluation.
- Directed DFS edge classification.
- Performance measurement.
- JSON result persistence.
- Assertions and exception handling.

### Important design decisions

The adjacency structure uses a dictionary whose values are lists.

This preserves neighbor insertion order, making traversal order reproducible.

A set is used for visited-state management because membership checks are efficient on average.

The implementation avoids unnecessary third-party dependencies.

The test suite verifies:

- Recursive and iterative traversal agreement.
- Connected-component counts.
- Reachability.
- Isolated vertices.
- Self-loops.
- Cyclic graphs.
- Directed-graph restrictions.
- Invalid starting vertices.

The benchmark measures traversal execution time without including graph construction.

Timing values are environment-dependent and should not be interpreted as a universal comparison between algorithms.

## 10. JavaScript Implementation

The JavaScript implementation emphasizes event-driven graph exploration.

### Implemented mechanisms

- `Map` for adjacency storage.
- `Set` for neighbor and visited-state management.
- `EventEmitter` for traversal notifications.
- Recursive and iterative traversal.
- Connected-component analysis.
- Reachability evaluation.
- Asynchronous DFS.
- Cancellation through `AbortSignal`.
- JSON file persistence using Node.js filesystem APIs.

### Event-driven exploration

The explorer emits a `visit` event whenever a vertex is processed.

A consumer can subscribe to this event to:

- Display traversal progress.
- Update a monitoring interface.
- Record exploration events.
- Track visited vertices.
- Collect operational metrics.

This separates traversal logic from event consumers.

### Asynchronous DFS

The asynchronous traversal uses `setImmediate` to yield control to the event loop.

This can improve responsiveness during longer traversals.

It does not make the underlying graph algorithm execute in parallel.

For CPU-intensive graph processing, worker threads or separate processes may be more appropriate.

### Failure handling

The implementation validates:

- Vertex types.
- Edge structure.
- Starting vertices.
- Graph consistency.
- Directed versus undirected operations.
- Output file extension.

The output file is written with restricted initial file permissions.

## 11. C++17 Implementation

The C++ implementation focuses on explicit state management and efficient graph processing.

### Implemented mechanisms

- `Graph` class.
- Directed and undirected graph types.
- STL adjacency containers.
- Recursive DFS using `std::function`.
- Iterative DFS using a vector-backed stack.
- Parent and depth tracking.
- Discovery and finishing timestamps.
- Connected-component identification.
- Path detection.
- Topological sorting.
- Cycle detection.
- Runtime measurement.
- Exception-based failure handling.

### Container selection

| Container | Purpose |
|---|---|
| `std::map` | Ordered adjacency representation |
| `std::vector` | Neighbor lists and traversal stacks |
| `std::unordered_set` | Visited-state management |
| `std::unordered_map` | Parent and depth metadata |
| `std::function` | Recursive traversal function |

The ordered map makes vertex iteration deterministic.

The unordered containers provide average constant-time membership and lookup operations.

### Engineering considerations

The iterative implementation avoids recursive call-stack exhaustion.

The recursive implementation is easier to understand and naturally records entry and exit times.

The program uses references to adjacency vectors to avoid unnecessary copying during traversal.

No third-party libraries are required.

## 12. Java 17 Implementation

The Java implementation models DFS through explicit domain types and an interchangeable traversal strategy.

### Domain types

| Type | Responsibility |
|---|---|
| `Graph` | Stores graph vertices and edges |
| `GraphType` | Defines directed or undirected behavior |
| `VertexState` | Tracks traversal state |
| `Edge` | Represents a graph relationship |
| `VisitEvent` | Captures a traversal event |
| `TraversalResult` | Stores immutable traversal output |
| `TraversalStrategy` | Defines the traversal contract |
| `DFSEngine` | Implements traversal and graph analysis |
| `GraphException` | Represents graph validation failures |
| `CycleDetectedException` | Represents directed cycle detection |

### Immutable traversal results

The `TraversalResult` record uses immutable copies of its collections.

This prevents external callers from modifying traversal results after they have been produced.

The graph itself maintains mutable adjacency state, while traversal results provide a stable record of completed execution.

### State transitions

The Java implementation uses:

    UNVISITED
        |
        v
      ACTIVE
        |
        v
      FINISHED

These states distinguish undiscovered vertices, currently explored vertices, and fully explored vertices.

This model is essential for directed cycle detection.

### Enterprise-oriented considerations

- Explicit validation errors.
- Immutable output records.
- Defined traversal interfaces.
- Separation of graph state from traversal results.
- Event listeners for operational monitoring.
- Custom exception types.
- Directed dependency analysis.
- Cycle-aware topological sorting.

## 13. PostgreSQL Implementation

The PostgreSQL implementation models graphs as relational data.

It demonstrates how graph relationships and traversal history can be stored, queried, and reported through SQL.

### Relational domain model

| Table | Responsibility |
|---|---|
| `graph` | Graph identity and graph type |
| `vertex` | Vertex records and metadata |
| `graph_edge` | Directed or undirected relationships |
| `traversal_run` | Traversal execution records |
| `traversal_visit` | Individual vertex visit records |
| `connected_component` | Calculated component membership |

### Relationship structure

    graph
      |
      +---- vertex
      |       |
      |       +---- graph_edge
      |
      +---- traversal_run
      |       |
      |       +---- traversal_visit
      |
      +---- connected_component

Foreign keys preserve graph ownership.

Unique constraints prevent duplicate vertex identities and duplicate directed edge records.

Check constraints enforce valid graph types, traversal methods, nonnegative depths, and valid execution states.

The edge trigger enforces canonical endpoint ordering for undirected edges.

### 13.1 Recursive CTE traversal

A recursive Common Table Expression (CTE) uses:

- An initial query.
- A recursive query.
- A termination condition.

The initial query selects the starting vertex.

The recursive query finds neighboring vertices.

A path array records vertices already present in the current path.

The condition:

\[
neighbor \notin visited\_path
\]

prevents revisiting a vertex along that particular path.

The resulting traversal identifies reachable vertices.

The SQL implementation uses `DISTINCT ON` to select a representative shortest-depth path for each reachable vertex.

Important distinction: the recursive CTE enumerates simple paths rather than implementing a global iterative DFS visited set. Consequently, it is not guaranteed to reproduce the exact DFS discovery order.

On dense graphs, simple-path enumeration can become exponentially expensive.

For large production graphs, a procedural implementation using a global visited set and an explicit stack is more appropriate.

### 13.2 Connected components in SQL

The `calculate_components` procedure uses recursive reachability.

For every vertex, it determines the vertices reachable from that vertex.

For an undirected graph, vertices in the same connected component have identical reachable sets.

The smallest vertex identifier among the reachable vertices is used as a deterministic component identifier.

This approach is easy to inspect and suitable for small datasets, but can generate substantial intermediate results.

A production implementation for large graphs should consider a procedural traversal, union-find, or a dedicated graph-processing service.

### 13.3 Traversal history

The `traversal_run` table stores:

- Graph identifier.
- Starting vertex.
- Traversal method.
- Execution status.
- Start and completion timestamps.
- Number of visited vertices.
- Error information.

The `traversal_visit` table stores:

- Visited vertex.
- Parent vertex.
- Traversal depth.
- Discovery sequence.

This supports historical analysis and operational reporting.

The SQL execution function creates a run, records traversal output, and marks successful execution.

Failures are recorded before the exception is re-raised. As with any PostgreSQL transaction, the caller must handle transaction rollback if durable failure auditing is required.

## 14. Complexity Analysis

Let:

- V represent the number of vertices.
- E represent the number of edges.

| Operation | Time complexity | Auxiliary space |
|---|---|---|
| Add vertex | O(1) average | O(1) |
| Add edge | O(1) average with set-based adjacency | O(1) |
| Recursive DFS | O(V + E) | O(V) |
| Iterative DFS | O(V + E) | O(V) |
| Connected components | O(V + E) | O(V) |
| Reachability | O(V + E) | O(V) |
| DFS cycle detection | O(V + E) | O(V) |
| Topological sorting | O(V + E) | O(V) |

These bounds assume adjacency-list graph representations and efficient visited-state membership checks.

The graph itself requires:

\[
O(V+E)
\]

storage.

Recursive DFS can additionally consume call-stack space proportional to the maximum exploration depth.

Iterative DFS stores its pending vertices explicitly.

For dense graphs, adjacency matrices may provide faster edge-existence checks at the cost of quadratic storage.

## 15. Edge Cases and Failure Conditions

| Scenario | Expected behavior |
|---|---|
| Empty graph | No traversal can begin |
| Unknown starting vertex | Validation exception |
| Isolated vertex | Traversal returns that vertex |
| Self-loop | Vertex is not explored repeatedly |
| Directed edge | Reverse traversal is not implied |
| Duplicate edge | Duplicate adjacency relationship is prevented |
| Disconnected graph | Only the starting component is explored |
| Cyclic undirected graph | Visited-state management prevents infinite traversal |
| Directed cycle | Topological sorting rejects the graph |
| Deep graph | Iterative DFS avoids recursive stack exhaustion |
| Invalid maximum depth | Validation error |
| Invalid SQL foreign key | Database rejects the relationship |
| Unsupported SQL graph type | Procedure raises an exception |

## 16. Practical Applications

### Network connectivity

DFS can inspect which infrastructure systems are reachable from a particular network node.

Connected components can reveal isolated network segments.

### Dependency exploration

A directed graph can represent software service dependencies.

DFS can identify downstream services and detect circular dependencies.

### Security analysis

Graph traversal can help examine relationships among:

- Users.
- Devices.
- Servers.
- Applications.
- Network segments.
- Access relationships.

A reachable path does not by itself establish that an access operation is authorized. Real security decisions must also evaluate permissions, authentication, network controls, and policy restrictions.

### Data organization

DFS can explore hierarchical structures, dependency trees, directory structures, and interconnected datasets.

### Research and network analysis

DFS provides a foundation for studying graph structure, reachability, connectedness, and more advanced graph algorithms.

## 17. Running the Implementations

### Python

Requirements: Python 3.10 or later.

Run the Python file directly.

The script executes its assertions, demonstrates traversal, reports connected components, and writes `dfs_results.json` in the current working directory.

### JavaScript

Requirements: Node.js with CommonJS and `EventEmitter` support.

Run the JavaScript file using Node.js.

It executes synchronous and asynchronous traversal, prints visit events, and writes `dfs_results.json`.

### C++17

Compile using a C++17-compatible compiler.

The executable runs validation tests, traversal demonstrations, connected-component analysis, and topological sorting.

### Java 17

Compile the `Main.java` source file using Java 17.

Run the `Main` class to execute the tests and graph exploration examples.

### PostgreSQL

Requirements: PostgreSQL 14 or later.

Execute the SQL script using a database account permitted to create schemas, tables, functions, triggers, and procedures.

The script creates the `graph_lab` schema and inserts two sample graphs.

The SQL uses transactions and relational integrity constraints.

## 18. Implementation Limitations

The implementations are educational graph-processing systems rather than distributed graph databases.

Their in-memory traversal algorithms assume that the graph fits within available memory.

The recursive implementations can encounter stack-depth limits.

The JavaScript asynchronous implementation yields to the event loop but does not provide parallel computation.

The SQL recursive CTE enumerates simple paths and is not suitable for unrestricted dense-graph processing.

The SQL connected-component calculation can produce large intermediate relations.

The implementations do not include concurrent graph mutation control across independent application processes.

For production deployment, graph versioning, transaction isolation, traversal cancellation, memory limits, access controls, query limits, and operational monitoring must be considered.

The central algorithmic distinction remains consistent across all five implementations: DFS explores graph structure using depth-first expansion, while visited-state management ensures that cycles and repeated relationships do not result in uncontrolled traversal.
