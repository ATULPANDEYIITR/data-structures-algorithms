# Graph Introduction

## 1. Graph Fundamentals

A graph is a non-linear data structure used to represent relationships between objects. It consists of a collection of vertices and edges.

A graph is commonly represented as:

\[
G = (V,E)
\]

Where:

- \(G\) represents the graph.
- \(V\) represents the set of vertices.
- \(E\) represents the set of edges connecting vertices.

For example, a transportation network can represent cities as vertices and roads as edges.

Consider the following graph:

    A ----- B
    |       |
    |       |
    C ----- D

The vertices are:

\[
V = \{A,B,C,D\}
\]

The edges are:

\[
E = \{(A,B),(A,C),(B,D),(C,D)\}
\]

This representation describes connections rather than a sequential arrangement of elements.

## 2. Vertices and Edges

### Vertices

A vertex, also called a node, represents an individual entity in a graph.

Examples include:

- A city in a transportation network.
- A person in a social network.
- A computer in a communication network.
- A service in a distributed software architecture.
- A task in a project dependency structure.

A graph can contain isolated vertices. An isolated vertex has no incident edges.

### Edges

An edge represents a relationship between two vertices.

For example:

    Delhi ----- Agra

Delhi and Agra are vertices. The road connecting them is an edge.

An edge can contain additional information, such as distance, cost, time, capacity, or connection strength.

The number of vertices is represented by:

\[
|V|
\]

The number of edges is represented by:

\[
|E|
\]

For a simple undirected graph with \(n\) vertices, the maximum number of edges is:

\[
E_{\max} = \frac{n(n-1)}{2}
\]

For a simple directed graph without self-loops:

\[
E_{\max} = n(n-1)
\]

These formulas assume that parallel edges and self-loops are not permitted.

## 3. Directed Graphs

A directed graph contains edges with a specified direction.

An edge from A to B is represented as:

\[
A \rightarrow B
\]

It does not automatically establish a connection from B to A.

Example:

    Analysis ---> Design ---> Development ---> Testing

This structure represents a project dependency workflow.

Development depends on Design, while Testing depends on Development.

Directed graphs are useful for:

- Task dependencies.
- Webpage links.
- Communication flows.
- Software package dependencies.
- Workflow systems.
- Directed information networks.

### In-degree

The in-degree of a vertex represents the number of incoming edges.

\[
d^{-}(v) = \text{Number of incoming edges}
\]

### Out-degree

The out-degree represents the number of outgoing edges.

\[
d^{+}(v) = \text{Number of outgoing edges}
\]

For example:

    A ---> C <--- B
          |
          v
          D

For vertex C:

- In-degree = 2.
- Out-degree = 1.

A directed graph may contain cycles. A directed cycle exists when a sequence of directed edges eventually returns to its starting vertex.

## 4. Undirected Graphs

An undirected graph contains edges without a specified direction.

An edge between A and B represents a bidirectional relationship:

\[
A \leftrightarrow B
\]

Example:

    Alice ----- Bob
      |          |
      |          |
    Charlie --- David

If Alice is connected to Bob, Bob is also connected to Alice.

Common applications include:

- Social friendship networks.
- Undirected road connections.
- Physical network topology.
- Mutual relationships.
- Connectivity analysis.

### Degree

The degree of an undirected vertex represents the number of edges connected to it.

\[
d(v) = \text{Number of incident edges}
\]

For example:

    A ----- B
    |
    |
    C

The degree of A is 2.

For an undirected graph, the sum of all vertex degrees is:

\[
\sum_{v \in V} d(v) = 2|E|
\]

This is known as the handshaking lemma.

## 5. Weighted Graphs

A weighted graph assigns a numerical value to each edge.

The value represents a measurable property of the connection.

Example:

    A --4-- B
    |       |
    2       5
    |       |
    C --8-- D

The weight of an edge may represent:

- Distance.
- Transportation cost.
- Network latency.
- Financial transaction cost.
- Communication capacity.
- Connection strength.

A weighted edge can be represented as:

\[
(u,v,w)
\]

Where:

- \(u\) is the source vertex.
- \(v\) is the destination vertex.
- \(w\) is the edge weight.

Weighted graphs can be directed or undirected.

A graph with no assigned edge weights is commonly treated as an unweighted graph. For traversal purposes, each edge can be assigned an implicit weight of 1.

A zero-weight edge is valid and must be distinguished from the absence of an edge.

Negative weights are permitted in some graph models, but algorithms such as Dijkstra's algorithm cannot process negative edge weights correctly.

## 6. Graph Classification

| Graph category | Edge direction | Edge weights | Main characteristic |
|---|---|---|---|
| Undirected unweighted | No | No | Mutual connections |
| Directed unweighted | Yes | No | One-way relationships |
| Undirected weighted | No | Yes | Mutual connections with costs |
| Directed weighted | Yes | Yes | One-way connections with costs |

These are independent graph properties. Direction and weighting describe different characteristics.

## 7. Graph Representations

A graph can be stored using different data structures. The two fundamental representations implemented in the source files are adjacency lists and adjacency matrices.

### 7.1 Adjacency List

An adjacency list stores the neighboring vertices associated with each vertex.

Consider:

    A ----- B
    |       |
    C ----- D

Its adjacency list is:

| Vertex | Neighbors |
|---|---|
| A | B, C |
| B | A, D |
| C | A, D |
| D | B, C |

For a weighted graph, each neighbor entry also stores its weight.

Example:

| Vertex | Neighbor and weight |
|---|---|
| A | B: 4, C: 2 |
| B | A: 4, C: 1, D: 5 |
| C | A: 2, B: 1, D: 8 |
| D | B: 5, C: 8 |

The Python implementation uses nested dictionaries, JavaScript uses Maps, C++17 uses ordered maps, and Java 17 uses nested maps.

The PostgreSQL implementation stores the same relationships in an edge table.

**Space complexity:**

\[
O(V+E)
\]

For undirected graphs, each edge is stored twice in the adjacency structure.

Advantages:

- Efficient storage for sparse graphs.
- Efficient neighbor iteration.
- Convenient edge insertion and deletion.
- Suitable for BFS and DFS.

Limitations:

- Checking whether a particular edge exists requires searching the source vertex's neighbors.
- Dense graphs can produce large neighbor collections.

### 7.2 Adjacency Matrix

An adjacency matrix uses a two-dimensional array to represent connections.

For a graph with four vertices:

\[
V = \{A,B,C,D\}
\]

An undirected unweighted example is:

| | A | B | C | D |
|---|---:|---:|---:|---:|
| A | 0 | 1 | 1 | 0 |
| B | 1 | 0 | 0 | 1 |
| C | 1 | 0 | 0 | 1 |
| D | 0 | 1 | 1 | 0 |

A value of 1 represents an edge, while 0 represents no edge in this unweighted example.

For weighted graphs, matrix cells contain edge weights.

The implementations use `None`, `null`, or an equivalent absent-edge marker instead of zero. This distinction preserves valid zero-weight edges.

**Space complexity:**

\[
O(V^2)
\]

Advantages:

- Constant-time edge existence checks.
- Convenient mathematical operations.
- Useful for dense graphs.
- Direct representation of weighted connections.

Limitations:

- Requires quadratic memory.
- Iterating through all neighbors requires scanning a complete matrix row.
- Inefficient for large sparse graphs.

### 7.3 Representation Comparison

| Operation | Adjacency list | Adjacency matrix |
|---|---|---|
| Space | O(V + E) | O(V²) |
| Edge lookup | O(degree) | O(1) |
| Neighbor iteration | O(degree) | O(V) |
| Edge insertion | O(1) average | O(1) |
| Edge removal | O(degree) | O(1) |
| Best suited for | Sparse graphs | Dense graphs |

The stated edge insertion and lookup costs assume appropriate indexing or average-case hash-map behavior. Ordered maps and database indexes have different implementation-specific costs.

## 8. Graph Traversal

Graph traversal is the process of visiting vertices by following edges.

Two fundamental traversal algorithms are Breadth-First Search and Depth-First Search.

### 8.1 Breadth-First Search

Breadth-First Search (BFS) visits vertices level by level.

It uses a queue.

Example:

    A
   / \
  B   C
  |   |
  D   E

Starting at A, a possible BFS order is:

    A -> B -> C -> D -> E

The algorithm:

1. Insert the starting vertex into a queue.
2. Mark it as visited.
3. Remove the next vertex from the queue.
4. Visit its unvisited neighbors.
5. Mark newly discovered vertices as visited.
6. Continue until the queue is empty.

**Time complexity using an adjacency list:**

\[
O(V+E)
\]

**Space complexity:**

\[
O(V)
\]

Applications include:

- Finding the minimum number of edges between vertices in an unweighted graph.
- Network exploration.
- Social network analysis.
- Level-order exploration.
- Connectivity analysis.

### 8.2 Depth-First Search

Depth-First Search (DFS) explores one path as deeply as possible before returning to earlier vertices.

It uses a stack or recursion.

Example:

    A
   / \
  B   C
  |
  D

One possible DFS traversal is:

    A -> B -> D -> C

The algorithm:

1. Select a starting vertex.
2. Mark it as visited.
3. Select an unvisited neighboring vertex.
4. Continue exploring until no unvisited neighbor remains.
5. Backtrack to explore other paths.

**Time complexity using an adjacency list:**

\[
O(V+E)
\]

**Space complexity:**

\[
O(V)
\]

Applications include:

- Cycle detection.
- Dependency exploration.
- Connected component discovery.
- Path exploration.
- Topological sorting.

Traversal order can differ depending on the order in which neighboring vertices are processed.

## 9. Shortest Paths and Dijkstra's Algorithm

A shortest path identifies a route between vertices with minimum total edge weight.

For a weighted graph:

    A --4-- B
    |       |
    2       1
    |       |
    C --8-- D

Dijkstra's algorithm calculates shortest distances from a starting vertex when all edge weights are non-negative.

Its main operations are:

- Initialize distances.
- Set the source distance to zero.
- Insert the source into a priority queue.
- Select the vertex with the smallest tentative distance.
- Relax its outgoing edges.
- Update distances when a shorter route is found.
- Continue until no useful pending vertex remains.

The relaxation operation is:

\[
d(v) = \min(d(v),d(u)+w(u,v))
\]

Where:

- \(d(u)\) is the current distance to vertex \(u\).
- \(w(u,v)\) is the edge weight.
- \(d(v)\) is the updated distance to vertex \(v\).

With an adjacency list and binary heap:

\[
O((V+E)\log V)
\]

The Python, JavaScript, C++17, and Java 17 implementations use priority-queue-based processing.

The PostgreSQL implementation uses temporary tables and iterative minimum-distance selection.

**Important limitation:** Dijkstra's algorithm is not suitable for graphs containing negative edge weights. Algorithms such as Bellman-Ford are required for general shortest-path problems with negative weights and no reachable negative cycle.

Unreachable vertices retain an infinite distance.

## 10. Connected Components

A connected component is a maximal group of vertices in an undirected graph where every vertex is reachable from every other vertex in that group.

Example:

    A ----- B ----- C

    D ----- E

    F

This graph contains three connected components:

- {A, B, C}
- {D, E}
- {F}

An isolated vertex is itself a connected component.

The implementations identify components by repeatedly starting a traversal from an unvisited vertex.

Time complexity:

\[
O(V+E)
\]

The implementation treats connected components as an undirected graph concept. Directed graphs require separate concepts such as strongly connected and weakly connected components.

## 11. Cycle Detection

A cycle is a path that returns to a previously visited vertex while respecting the graph's edge relationships.

Example:

    A ---- B
     \    /
      \  /
       C

This graph contains a cycle.

Directed and undirected graphs require different cycle-detection logic.

### Undirected graphs

DFS tracks the parent vertex. A visited neighbor other than the parent indicates a cycle.

### Directed graphs

DFS maintains:

- A visited set.
- An active recursion set.

An edge to a vertex in the active recursion set indicates a directed cycle.

Cycle detection is important in:

- Dependency management.
- Workflow validation.
- Scheduling systems.
- Network analysis.
- Circular dependency detection.

## 12. Python Implementation

The Python file defines:

- `GraphType` for graph direction.
- `Edge` as an immutable edge record.
- `Graph` as the primary graph domain object.
- Custom graph exceptions.
- Adjacency-list and adjacency-matrix generation.
- BFS and DFS.
- Degree calculations.
- Connected components.
- Dijkstra shortest paths.
- Cycle detection.
- JSON persistence.

### Implementation decisions

The adjacency list uses a dictionary containing nested dictionaries.

This provides direct access to each vertex's neighbors and supports efficient graph modifications.

The `Graph` class distinguishes directed and undirected behavior when inserting or deleting edges.

For undirected graphs, edge insertion creates reciprocal adjacency entries. Edge counting compensates for this by dividing the total adjacency-entry count by two.

JSON persistence stores the graph type, weighting property, vertices, and edges.

The loader reconstructs the graph through validated graph operations rather than directly accepting arbitrary internal adjacency structures.

The demonstration includes:

- A social network.
- A project dependency graph.
- A weighted transportation network.
- An invalid weight.
- An unknown vertex.
- A negative-weight shortest-path failure.

The graph's traversal implementations use an iterative stack or queue to avoid unnecessary recursion depth in ordinary traversals. Cycle detection remains recursive and may need an iterative alternative for extremely deep graphs.

## 13. JavaScript Implementation

The JavaScript file emphasizes event-driven graph operations and asynchronous processing.

Its principal components are:

| Component | Responsibility |
|---|---|
| `Graph` | Graph structure and operations |
| `MinHeap` | Priority queue |
| `GraphError` | General graph failures |
| `VertexNotFoundError` | Missing vertex |
| `NegativeWeightError` | Invalid Dijkstra input |

### Event-driven behavior

The implementation uses Node.js `EventEmitter`.

Graph modifications produce events such as:

- `vertexAdded`
- `vertexRemoved`
- `edgeAdded`
- `edgeRemoved`

An application can subscribe to these events to maintain audit logs, update visualizations, or initiate downstream processing.

The graph version number changes when the structure is modified.

### Asynchronous processing

The shortest-path method returns a Promise-compatible asynchronous result.

File persistence uses Node.js filesystem Promise APIs.

The application can therefore integrate graph operations into an asynchronous service without blocking its control flow during file operations.

The custom binary min-heap provides priority extraction for Dijkstra's algorithm.

## 14. C++17 Implementation

The C++17 implementation focuses on efficient domain modeling and standard-library data structures.

Its primary structures include:

- `GraphType` enumeration.
- `Edge` structure.
- `Graph` class.
- Ordered maps for deterministic vertex and neighbor iteration.
- Sets for visited vertices.
- Queues for BFS.
- Stacks for DFS.
- Priority queues for Dijkstra.

### Implementation decisions

The graph uses:

`map<string, map<string, double>>`

This representation provides deterministic iteration and direct neighbor lookup.

The priority queue uses a minimum-first ordering to support shortest-path calculations.

The implementation separates directed and undirected graph behavior through an enumeration.

It also demonstrates:

- In-degree and out-degree.
- Cycle detection.
- Connected components.
- Vertex deletion.
- Edge deletion.
- Exception handling.
- Graph integrity assertions.

Ordered maps have logarithmic lookup and insertion costs. They offer deterministic iteration at the expense of higher operation costs than average-case hash-based containers.

## 15. Java 17 Implementation

The Java implementation adopts an enterprise-oriented domain and service structure.

The principal domain types are:

| Type | Purpose |
|---|---|
| `GraphType` | Defines graph direction |
| `Edge` | Immutable edge record |
| `GraphSnapshot` | Immutable graph snapshot |
| `MatrixRepresentation` | Matrix output |
| `Graph` | Graph state and operations |
| `GraphService` | Application-level operations |

Java records provide concise immutable data structures for edges and reporting objects.

The graph uses synchronized operations to prevent concurrent modifications from interleaving within individual graph methods.

The service layer separates graph processing from application reporting.

The implementation also uses:

- Collections.
- Streams.
- Generic data structures.
- Priority queues.
- Custom runtime exceptions.
- Immutable collection views.
- Explicit validation.

A synchronized graph operation does not automatically provide an atomic multi-operation business transaction. Applications that need transactional graph updates should introduce a higher-level transaction or versioning strategy.

## 16. PostgreSQL Implementation

The PostgreSQL file models graph data using relational tables.

### Database schema

The `graph` table stores graph-level properties.

The `vertex` table stores individual vertices.

The `edge` table stores connections between vertices.

The principal relationship is:

    graph
      |
      +---- vertex
      |       |
      |       +---- source vertex
      |       |
      |       +---- destination vertex
      |
      +---- edge
              |
              +---- source_vertex_id
              |
              +---- destination_vertex_id

The edge table uses foreign keys to ensure that both endpoints belong to the same graph.

### Integrity enforcement

The schema includes:

- Primary keys.
- Foreign keys.
- Unique constraints.
- Check constraints.
- Indexes.
- Triggers.
- Views.
- Functions.
- Procedures.
- Transaction handling.

A trigger prevents non-unit edge weights from being inserted into unweighted graphs.

The endpoint constraint prevents self-loops in this particular implementation.

The unique expression index prevents duplicate endpoint pairs regardless of endpoint order. Consequently, the relational design intentionally supports simple graphs rather than multigraphs.

### Database representations

The `adjacency_list` view presents stored edges as source and destination relationships.

The `get_adjacency_matrix` function generates every ordered vertex pair and returns the corresponding edge weight where an edge exists.

Missing weights indicate absent edges. Zero remains a valid weight.

### Recursive traversal

The `graph_bfs` function uses a recursive common table expression.

It tracks:

- Current vertex.
- Traversal depth.
- Visited vertex identifiers.
- Traversal path.

This prevents revisiting vertices within a traversal path.

The implementation returns reachable vertices with their traversal depths and paths.

### Shortest-path procedure

The `calculate_shortest_paths` procedure performs Dijkstra-style processing using temporary tables.

The temporary distance table stores tentative distances, while the pending table stores vertices that remain eligible for processing.

The procedure rejects negative weights before execution.

The approach uses repeated minimum-distance selection through SQL ordering. It is useful for demonstrating relational graph processing, although it is less efficient than a dedicated binary-heap implementation for large graphs.

### Reporting

The database includes reports for:

- Graph inventory.
- Vertex and edge counts.
- Adjacency lists.
- Adjacency matrices.
- Vertex degrees.
- Connected or isolated vertices.
- Directed cycle evaluation.
- Shortest distances.
- Weight validation.
- Query execution plans.

## 17. Practical Graph Applications

| Application | Vertices | Edges | Possible weights |
|---|---|---|---|
| Transportation | Cities | Roads | Distance or travel time |
| Social networking | People | Relationships | Relationship strength |
| Computer networks | Devices | Connections | Latency or bandwidth |
| Web architecture | Webpages | Hyperlinks | Relevance |
| Project management | Tasks | Dependencies | Duration |
| Financial networks | Accounts | Transactions | Transaction amount |
| Distributed systems | Services | Communication links | Latency or cost |

The same graph structure can represent different domains by changing the meaning of vertices, edges, and weights.

## 18. Performance and Complexity Reference

Let:

- \(V\) = number of vertices.
- \(E\) = number of edges.

| Operation | Adjacency-list implementation |
|---|---|
| Add vertex | O(1) average with hash maps |
| Add edge | O(1) average |
| Remove edge | O(1) average |
| Remove vertex | O(V + E) in the general implementation |
| BFS | O(V + E) |
| DFS | O(V + E) |
| Degree lookup | O(1) average |
| Cycle detection | O(V + E) |
| Connected components | O(V + E) |
| Dijkstra with binary heap | O((V + E) log V) |

These costs depend on the underlying container. Ordered maps generally introduce logarithmic lookup and insertion costs.

### Sparse graphs

A sparse graph has relatively few edges compared with the maximum possible number of edges.

Adjacency lists are usually preferable because they require:

\[
O(V+E)
\]

storage.

### Dense graphs

A dense graph contains a large proportion of possible edges.

Adjacency matrices may be preferable when constant-time edge lookup and predictable memory access are important.

## 19. Security and Data Integrity

Graph applications can process externally supplied vertices, edges, and weights. Input validation is therefore essential.

Important controls include:

- Reject empty vertex identifiers.
- Validate numeric weights.
- Reject non-finite values.
- Enforce graph membership for edge endpoints.
- Distinguish zero weights from absent edges.
- Restrict graph modifications to authorized application operations.
- Apply database constraints and foreign keys.
- Use parameterized database queries.
- Avoid accepting arbitrary serialized graph structures without validation.
- Limit graph size and traversal depth when processing untrusted input.

For multi-user graph systems, access control should also distinguish read, insert, update, and delete permissions.

The PostgreSQL implementation uses relational constraints and triggers for structural integrity. Application-level authorization remains a separate responsibility.

## 20. Limitations and Design Trade-offs

The implementations intentionally focus on fundamental graph structures and operations.

They do not implement every graph algorithm or graph category.

Important limitations include:

- Dijkstra does not support negative edge weights.
- The examples model simple graphs rather than multigraphs.
- Self-loops are excluded in the PostgreSQL implementation.
- Recursive cycle detection can encounter recursion-depth limitations.
- The PostgreSQL shortest-path procedure prioritizes clarity over large-scale performance.
- The Java synchronization model protects individual operations, not arbitrary sequences of operations.
- Graph serialization requires validation and resource limits when used with untrusted files.
- Connected components are implemented for undirected graphs; directed connectivity requires additional algorithms.

The choice between adjacency lists and adjacency matrices should depend on graph density, query patterns, memory constraints, and expected modification frequency.

## 21. Execution and Verification

| Deliverable | Runtime | Execution |
|---|---|---|
| Python | Python 3.10+ | `python graph_introduction.py` |
| JavaScript | Node.js 18+ | `node graph_introduction.js` |
| C++17 | C++17 compiler | `g++ -std=c++17 -O2 graph_introduction.cpp -o graph_introduction` |
| Java 17 | Java 17 | `javac GraphIntroduction.java` followed by `java GraphIntroduction` |
| PostgreSQL | PostgreSQL 14+ | Execute the SQL script in a database session |

The source files use standard-language facilities without requiring third-party packages.

The demonstrations verify vertex and edge counts, traversal results, graph representations, shortest-path calculations, invalid inputs, and graph modifications.

The PostgreSQL script creates the `graph_lab` schema and its associated database objects. It should be executed in a database where the executing role has permission to create schemas, tables, functions, procedures, indexes, and triggers.
