# Graph Representation: Adjacency Matrix, Adjacency List and Edge List

## 1. Introduction

A graph is a non-linear data structure consisting of vertices and edges.

A vertex represents an entity. An edge represents a connection between two entities.

Graphs are used to model:

- Road networks and transportation systems.
- Computer networks.
- Social relationships.
- Dependency management.
- Recommendation systems.
- Communication networks.
- Supply chains.
- Knowledge networks.
- Scheduling and routing problems.

The same logical graph can be stored in different ways. The choice of representation affects memory consumption, insertion speed, edge lookup, neighbor retrieval, and graph traversal performance.

The three principal representations implemented in this project are:

1. Adjacency Matrix.
2. Adjacency List.
3. Edge List.

## 2. Fundamental Graph Concepts

### 2.1 Vertex

A vertex is an individual element in a graph.

For example, a transportation network may represent cities as vertices.

For a graph containing six vertices:

`V = {0, 1, 2, 3, 4, 5}`

### 2.2 Edge

An edge connects two vertices.

An edge between vertices 0 and 1 can be represented as:

`(0, 1)`

A graph can contain multiple edges with different weights, depending on its graph model. The implementations in this project use a simple graph model in which a particular ordered or unordered vertex pair has at most one edge.

### 2.3 Directed Graph

A directed graph contains edges with a specific direction.

For example:

`0 → 1`

This does not automatically establish:

`1 → 0`

Directed graphs are useful for representing:

- Website links.
- Task dependencies.
- One-way transportation routes.
- Communication flows.
- Following relationships.

### 2.4 Undirected Graph

An undirected graph contains edges without a specified direction.

An edge between vertices 0 and 1 establishes a connection in both directions:

`0 — 1`

The connection is stored as one logical edge in the edge-list implementations. Adjacency matrices and adjacency lists maintain the corresponding reverse access.

### 2.5 Weighted Graph

A weighted graph assigns a numerical value to each edge.

For example:

| Source | Target | Weight |
|---|---|---:|
| 0 | 1 | 4 |
| 0 | 2 | 2 |
| 1 | 2 | 1 |
| 1 | 3 | 5 |
| 3 | 4 | 2 |

Weights can represent:

- Distance.
- Travel time.
- Financial cost.
- Network latency.
- Connection strength.
- Resource consumption.

An unweighted graph can be represented by assigning every edge a weight of 1.

### 2.6 Degree

The degree of a vertex is the number of edges connected to it in an undirected graph.

For directed graphs, two separate measurements are used:

- In-degree: number of incoming edges.
- Out-degree: number of outgoing edges.

The degree of a vertex is useful for understanding its connectivity.

### 2.7 Graph Density

Graph density measures how many edges exist compared with the maximum possible number of edges.

For a simple undirected graph:

\[
D = \frac{2E}{V(V-1)}
\]

For a simple directed graph without self-loops:

\[
D = \frac{E}{V(V-1)}
\]

Where:

- \(V\) represents the number of vertices.
- \(E\) represents the number of edges.
- \(D\) represents graph density.

A density near zero indicates a sparse graph.

A density closer to one indicates a dense graph.

## 3. Adjacency Matrix

An adjacency matrix represents a graph using a two-dimensional array.

If a graph contains \(V\) vertices, its matrix contains:

\[
V \times V
\]

positions.

Each row represents a source vertex, and each column represents a target vertex.

For an unweighted graph:

- `1` indicates an existing edge.
- `0` indicates an absent edge.

For a weighted graph, the corresponding position stores the edge weight.

The Python, JavaScript, C++17 and Java implementations use a separate presence indicator or `None` to distinguish a missing edge from an existing edge with weight zero.

### 3.1 Example

Consider the undirected graph:

- 0 connected to 1.
- 0 connected to 2.
- 1 connected to 2.
- 1 connected to 3.

Its unweighted adjacency matrix is:

| Vertex | 0 | 1 | 2 | 3 |
|---|---:|---:|---:|---:|
| 0 | 0 | 1 | 1 | 0 |
| 1 | 1 | 0 | 1 | 1 |
| 2 | 1 | 1 | 0 | 0 |
| 3 | 0 | 1 | 0 | 0 |

The matrix is symmetric because the graph is undirected.

For a directed graph, the matrix does not need to be symmetric.

### 3.2 Implementation Mechanism

The matrix implementation maintains:

- A two-dimensional array.
- An edge-presence indicator.
- A vertex-count property.
- A directed or undirected configuration.

An edge insertion updates the corresponding matrix position.

For an undirected graph, both symmetric positions are updated.

An edge lookup directly checks one matrix position.

### 3.3 Advantages

- Constant-time edge existence lookup.
- Straightforward implementation.
- Efficient for dense graphs.
- Convenient for mathematical graph operations.
- Simple representation of weighted edges.

### 3.4 Limitations

- Requires quadratic memory.
- Neighbor retrieval examines an entire row.
- Inefficient for graphs containing many vertices but relatively few edges.
- Adding vertices can require resizing the matrix.

## 4. Adjacency List

An adjacency list stores the neighbors of each vertex.

Each vertex maintains a collection of its connected vertices.

For weighted graphs, each neighbor is stored together with its edge weight.

### 4.1 Example

Consider:

`0 — 1`

`0 — 2`

`1 — 2`

`1 — 3`

The adjacency list is:

| Vertex | Neighbors |
|---|---|
| 0 | 1, 2 |
| 1 | 0, 2, 3 |
| 2 | 0, 1 |
| 3 | 1 |

For a weighted graph, the entries also contain their respective weights.

### 4.2 Implementation Mechanism

The Python implementation uses a list of dictionaries.

The JavaScript implementation uses an array of `Map` objects.

The C++ implementation uses a vector of unordered maps.

The Java implementation uses a list of hash maps.

Each vertex has a separate collection of neighbors.

For example:

`adjacency[0] = {1: 4, 2: 2}`

This means vertex 0 connects to vertex 1 with weight 4 and vertex 2 with weight 2.

### 4.3 Advantages

- Efficient memory usage for sparse graphs.
- Direct access to a vertex's neighbors.
- Convenient graph traversal.
- Efficient edge insertion.
- Suitable for large networks with relatively few connections.

### 4.4 Limitations

- Edge existence lookup depends on the neighbor collection.
- Memory overhead depends on the underlying collection.
- Less convenient than matrices for operations requiring every possible vertex pair.
- Hash-based collections introduce additional storage overhead.

## 5. Edge List

An edge list stores the graph as a collection of edges.

Each edge contains:

- Source vertex.
- Target vertex.
- Weight.

### 5.1 Example

| Edge | Source | Target | Weight |
|---|---:|---:|---:|
| E1 | 0 | 1 | 4 |
| E2 | 0 | 2 | 2 |
| E3 | 1 | 2 | 1 |
| E4 | 1 | 3 | 5 |

The representation stores the connections directly instead of maintaining a separate neighbor collection for every vertex.

### 5.2 Implementation Mechanism

The Python implementation uses a dictionary keyed by normalized vertex pairs.

The JavaScript implementation uses a `Map` keyed by vertex identifiers.

The C++ implementation stores edge records in a vector.

The Java implementation uses a hash map of edge records.

For undirected graphs, endpoint normalization ensures that `(0, 1)` and `(1, 0)` refer to the same logical edge.

For directed graphs, the order of the endpoints remains significant.

### 5.3 Advantages

- Compact representation when the number of edges is small.
- Simple edge enumeration.
- Convenient for sorting and processing edges.
- Suitable for algorithms that primarily operate on edges.
- Straightforward serialization and storage.

### 5.4 Limitations

- Finding a particular edge may require scanning the collection.
- Finding all neighbors of a vertex requires examining stored edges unless an additional index is maintained.
- Repeated neighborhood queries can be expensive.

## 6. Comparison of the Three Representations

The following comparison assumes simple graphs without duplicate edges. Complexity depends on the underlying implementation and data structures.

| Operation | Adjacency Matrix | Adjacency List | Edge List |
|---|---|---|---|
| Space | O(V²) | O(V + E) | O(E) |
| Edge existence | O(1) | O(degree) average with a hash map | O(E) in a sequential list |
| Neighbor retrieval | O(V) | O(degree) | O(E) |
| Edge insertion | O(1) | O(1) average | O(1) amortized append |
| Edge deletion | O(1) | O(1) average | O(E) in a sequential list |
| Edge enumeration | O(V²) | O(V + E) | O(E) |

The hash-based edge-list implementations in Python, JavaScript and Java improve edge lookup to average O(1), at the cost of additional indexing memory.

The C++ edge-list implementation uses a vector and therefore performs sequential edge searches.

### 6.1 Memory Comparison

For a graph with \(V\) vertices and \(E\) edges:

**Adjacency Matrix**

\[
O(V^2)
\]

The matrix allocates space for every possible vertex pair, including absent edges.

**Adjacency List**

\[
O(V+E)
\]

An undirected graph typically stores each connection twice in its neighbor collections.

**Edge List**

\[
O(E)
\]

Each logical edge is represented once.

The actual memory consumption also depends on:

- Programming language.
- Object overhead.
- Collection implementation.
- Numeric data types.
- Allocator behavior.
- Hash-table capacity.
- Memory alignment.

The memory measurements in the source programs are estimates, not exact operating-system memory measurements.

## 7. Graph Traversal

Graph traversal means visiting vertices according to a defined exploration strategy.

The implementations contain Breadth-First Search and Depth-First Search.

### 7.1 Breadth-First Search

Breadth-First Search, or BFS, visits neighboring vertices before exploring vertices farther away.

It uses a queue.

Workflow:

1. Select a starting vertex.
2. Mark it as visited.
3. Insert it into the queue.
4. Remove the first vertex from the queue.
5. Examine its unvisited neighbors.
6. Mark those neighbors as visited and insert them into the queue.
7. Continue until the queue becomes empty.

For an adjacency-list graph, its complexity is:

\[
O(V+E)
\]

For an adjacency matrix, it is:

\[
O(V^2)
\]

BFS is useful for finding the minimum number of edges between vertices in an unweighted graph.

### 7.2 Depth-First Search

Depth-First Search, or DFS, explores one path as far as possible before returning to another available path.

The implementations use an explicit stack instead of recursive function calls.

Workflow:

1. Select a starting vertex.
2. Insert it into the stack.
3. Remove the top vertex.
4. Ignore it if already visited.
5. Mark it as visited.
6. Insert its unvisited neighbors.
7. Continue until the stack becomes empty.

For adjacency-list graphs, DFS takes:

\[
O(V+E)
\]

For adjacency matrices, it takes:

\[
O(V^2)
\]

The iterative approach avoids excessive call-stack usage on very deep graphs.

## 8. Shortest Paths Using Dijkstra's Algorithm

Dijkstra's algorithm calculates the shortest distance from one starting vertex to every reachable vertex.

It requires non-negative edge weights.

The implementations reject negative weights before processing.

### 8.1 Working Mechanism

1. Assign a distance of zero to the starting vertex.
2. Assign infinity to all other vertices.
3. Select the unsettled vertex with the smallest known distance.
4. Examine its neighbors.
5. Calculate possible improved distances.
6. Update the distances when a shorter route is found.
7. Repeat until no reachable unsettled vertex remains.

The Python implementation uses a priority queue.

The C++ implementation uses `std::priority_queue`.

The Java implementation uses `PriorityQueue`.

The JavaScript implementation uses a straightforward minimum-distance selection process, providing a simpler implementation with different performance characteristics.

For adjacency-list implementations using a priority queue, the typical complexity is:

\[
O((V+E)\log V)
\]

For the JavaScript implementation:

\[
O(V^2+E)
\]

### 8.2 Example

Using the sample weighted network:

| Source | Target | Weight |
|---|---|---:|
| 0 | 1 | 4 |
| 0 | 2 | 2 |
| 1 | 2 | 1 |
| 1 | 3 | 5 |
| 2 | 3 | 8 |
| 2 | 4 | 10 |
| 3 | 4 | 2 |
| 4 | 5 | 3 |

The shortest distances from vertex 0 are:

| Vertex | Shortest Distance |
|---|---:|
| 0 | 0 |
| 1 | 3 |
| 2 | 2 |
| 3 | 8 |
| 4 | 10 |
| 5 | 13 |

For vertex 1, the shortest route is:

`0 → 2 → 1`

Its total weight is:

\[
2+1=3
\]

For vertex 5, the shortest route is:

`0 → 2 → 1 → 3 → 4 → 5`

Its total weight is:

\[
2+1+5+2+3=13
\]

## 9. Python Implementation

The Python implementation provides an extensible graph interface using an abstract base class.

Its main components are:

| Component | Responsibility |
|---|---|
| `Graph` | Common graph operations |
| `AdjacencyMatrix` | Matrix storage |
| `AdjacencyList` | Neighbor dictionary storage |
| `EdgeList` | Edge collection storage |
| `Edge` | Immutable edge record |
| `Representation` | Representation selection |
| `benchmark()` | Performance measurements |
| `generate_random_graph()` | Random graph construction |
| `save_graph()` | JSON persistence |
| `load_graph()` | Graph reconstruction |
| `run_tests()` | Correctness validation |

### Important design decisions

**Abstract interface**

The common interface allows traversal and shortest-path algorithms to work with all three representations.

**Dictionaries**

The adjacency-list implementation uses dictionaries to provide efficient neighbor lookup and edge updates.

**Immutable edge records**

The `Edge` dataclass prevents accidental modification of individual edge records.

**Input validation**

Invalid vertices, non-finite weights, and invalid graph sizes are rejected.

**Persistence**

Graph structures are serialized into JSON and reconstructed using the selected representation.

The JSON document stores the logical graph rather than a language-specific memory layout.

## 10. JavaScript Implementation

The JavaScript implementation focuses on dynamic graph management and event-driven processing.

Its principal components are:

| Component | Responsibility |
|---|---|
| `Graph` | Common graph contract |
| `MatrixGraph` | Matrix implementation |
| `ListGraph` | Map-based adjacency lists |
| `EdgeListGraph` | Map-based edge storage |
| `EventEmitter` | Graph modification notifications |
| `processInBatches()` | Asynchronous batch processing |
| `benchmark()` | Runtime measurements |
| `saveGraph()` | JSON persistence |
| `loadGraph()` | Graph reconstruction |

### Event-driven behavior

The graph class emits events when edges are added or removed.

For example, an application can subscribe to `edgeAdded` and update a monitoring interface whenever the graph changes.

This separates graph modification from the components that respond to it.

### Asynchronous processing

The `processInBatches()` method processes edge records in batches.

It yields control between batches using the Node.js event loop.

This helps prevent large processing loops from monopolizing the event loop.

It does not make the underlying graph operations computationally parallel.

### Data structure decisions

JavaScript `Map` objects provide efficient average-case key lookup and preserve insertion order.

`Set` objects provide efficient visited-vertex tracking.

The implementation uses a moving queue index for BFS rather than repeatedly removing the first array element.

## 11. C++17 Implementation

The C++ implementation focuses on memory-conscious data structures and explicit ownership.

Its principal components are:

| Component | Responsibility |
|---|---|
| `Graph` | Abstract graph interface |
| `AdjacencyMatrixGraph` | Matrix storage |
| `AdjacencyListGraph` | Vector of hash maps |
| `EdgeListGraph` | Vector of edge records |
| `Edge` | Graph edge structure |
| `Representation` | Representation selection |
| `createGraph()` | Factory function |
| `benchmark()` | Operation measurements |
| `runTests()` | Correctness verification |

### Memory management

The graph factory returns `std::unique_ptr<Graph>`.

This provides automatic resource management and prevents manual deletion of dynamically allocated graph objects.

### STL usage

- `vector` stores vertices and edge collections.
- `unordered_map` stores adjacency relationships.
- `queue` implements BFS.
- `priority_queue` implements Dijkstra's algorithm.
- `sort` provides deterministic neighbor ordering.
- `find_if` searches the edge-list implementation.

### Trade-offs

The matrix uses contiguous rows of numeric values and a separate presence matrix.

The adjacency list uses hash maps for average constant-time edge lookup.

The edge list uses a vector to minimize per-edge storage overhead, although edge lookup and removal require linear searches.

## 12. Java 17 Implementation

The Java implementation focuses on enterprise-oriented separation of responsibilities.

Its principal components are:

| Component | Responsibility |
|---|---|
| `GraphStore` | Common graph interface |
| `AbstractGraph` | Shared validation |
| `MatrixGraph` | Matrix implementation |
| `ListGraph` | Hash-map adjacency implementation |
| `EdgeListGraph` | Edge collection implementation |
| `GraphFactory` | Object construction |
| `GraphTraversalService` | BFS and DFS |
| `ShortestPathService` | Dijkstra processing |
| `GraphBenchmarkService` | Performance measurements |
| `GraphProcessingService` | Asynchronous execution |

### Records

Java records represent immutable domain values:

- `Edge`
- `GraphMetrics`
- `PathResult`

This makes graph data easier to pass between services without exposing mutable internal objects.

### Service separation

Graph storage is separated from traversal, shortest-path processing, and benchmarking.

This makes the implementation easier to extend and test.

### Asynchronous execution

`CompletableFuture` and `ExecutorService` are used to execute graph traversal through a managed thread pool.

The executor is shut down after processing.

This demonstrates asynchronous service execution without changing the underlying graph representation.

## 13. PostgreSQL Implementation

The PostgreSQL implementation models graph data using relational tables.

It separates graph definitions, vertices, edges, storage measurements, benchmark results, traversal records, and shortest-path results.

### 13.1 Database Structure

The principal relationships are:

`Graphs → Vertices → Edges`

Additional analytical relationships are:

`Graphs → Storage Measurements`

`Graphs → Benchmark Runs`

`Graphs → Traversal Runs`

`Graphs → Shortest Path Results`

### 13.2 Graph Table

The `graphs` table records:

- Graph name.
- Representation.
- Direction.
- Vertex count.
- Description.
- Creation timestamp.

The representation is stored using a PostgreSQL enum.

### 13.3 Vertex Table

The `vertices` table stores each vertex separately.

The composite primary key is:

`(graph_id, vertex_id)`

This ensures that a vertex identifier is unique within its graph.

A vertex can have JSONB metadata for additional application-specific properties.

### 13.4 Edge Table

The `edges` table stores logical connections.

Each edge contains:

- Edge identifier.
- Graph identifier.
- Source vertex.
- Target vertex.
- Weight.

Composite foreign keys ensure that both endpoints belong to the same graph.

The unique constraint prevents duplicate logical edges.

For undirected graphs, endpoint normalization establishes a consistent ordering.

For example:

`(0, 1)` is the canonical representation of the connection between vertices 0 and 1.

This prevents `(1, 0)` from being inserted as a second logical edge.

The `get_neighbors()` function restores the two-way behavior of undirected connections.

### 13.5 Functions and Procedures

The database includes the following mechanisms:

| Database object | Purpose |
|---|---|
| `create_graph()` | Creates a graph and its vertices |
| `add_edge()` | Inserts or updates an edge |
| `get_neighbors()` | Returns logical neighbors |
| `edge_exists()` | Checks edge existence |
| `breadth_first()` | Executes BFS |
| `dijkstra()` | Calculates shortest distances |
| `validate_edge()` | Enforces direction rules |
| `validate_graph_vertex_count()` | Checks declared vertex capacity |

### 13.6 Constraints and Indexes

The database uses:

- Primary keys for entity identification.
- Foreign keys for graph integrity.
- Unique constraints for duplicate prevention.
- Check constraints for valid values.
- Triggers for graph-specific validation.
- Indexes for source and target vertex searches.
- Composite indexes for benchmark reporting.

The indexes improve relevant retrieval operations but consume additional storage and increase the cost of data modifications.

### 13.7 Analytical Reporting

The `graph_statistics` view calculates:

- Number of vertices.
- Number of stored edges.
- Maximum possible edge count.
- Graph density.

The `representation_characteristics` table stores the theoretical complexity characteristics of each representation.

The `representation_comparison` view provides an analytical comparison of graph storage.

The benchmark table records execution measurements independently of the graph's structural data.

### 13.8 SQL Transaction Handling

The graph creation procedure inserts a graph and its vertices within the calling transaction.

The edge insertion function uses an upsert operation to update an existing logical edge rather than create a duplicate.

The transactional demonstration illustrates rollback behavior.

The SQL script is intended to be executed as a complete database setup. It creates the `graph_lab` schema and its associated objects.

## 14. Real-World Applications

### Transportation Networks

Vertices represent locations, while edges represent roads.

Edge weights can represent distance, fuel consumption, or travel time.

Adjacency lists are useful when each location connects to a relatively small number of other locations.

### Computer Networks

Vertices represent network devices.

Edges represent communication links.

Weights can represent latency or connection cost.

An adjacency matrix can be useful when the network is relatively dense and edge-existence checks are frequent.

### Social Networks

Vertices represent users.

Edges represent relationships such as following or friendship.

A directed adjacency list can represent follower relationships.

### Dependency Management

Vertices represent software components or tasks.

Directed edges represent dependencies.

An edge from A to B can indicate that B depends on A, provided the application consistently follows that convention.

### Financial Networks

Vertices represent accounts or financial institutions.

Edges represent relationships or transactions.

Weights can represent transaction amounts or risk measures.

A transaction network may require a multigraph model when multiple transactions between the same pair of entities must be retained separately.

## 15. Important Edge Cases and Limitations

### Empty Graph

A graph can contain zero vertices.

Traversal and shortest-path operations require a valid starting vertex and therefore cannot run on an empty graph.

### Isolated Vertices

A vertex can exist without any edges.

It must still appear in the graph's vertex collection.

### Self-Loops

A self-loop connects a vertex to itself.

The implementations support self-loops.

For an undirected graph, a self-loop is stored once.

### Duplicate Edges

The implementations use simple graph semantics.

Adding an existing edge updates its weight.

Applications that require multiple independent edges between the same vertices need a multigraph representation.

### Zero-Weight Edges

A zero-weight edge is valid.

A separate edge-presence indicator is required in matrix implementations to distinguish a zero-weight edge from an absent edge.

### Negative Weights

Negative weights are rejected by Dijkstra's algorithm.

Graphs containing negative weights require an alternative such as Bellman-Ford.

### Disconnected Graphs

A traversal visits only the vertices reachable from its starting vertex.

Unreachable vertices remain unvisited.

Dijkstra returns infinity for unreachable vertices.

### Very Large Graphs

An adjacency matrix becomes expensive as the number of vertices increases.

An adjacency list or edge list may be more appropriate depending on the operations required.

For large-scale production graphs, memory layout, external storage, indexing, partitioning, and parallel processing become important design considerations.

### Floating-Point Precision

Weighted graph calculations use floating-point numbers.

Repeated arithmetic can introduce small precision differences.

Applications requiring exact financial calculations should use appropriate decimal arithmetic or scaled integer weights.

## 16. Performance Considerations

The theoretical complexity of a graph representation does not fully determine its actual runtime.

Practical performance also depends on:

- CPU cache behavior.
- Memory allocation.
- Data structure overhead.
- Graph density.
- Number of repeated queries.
- Distribution of vertex degrees.
- Programming language runtime.
- Dataset size.

For example, an adjacency matrix has a high theoretical memory requirement but can perform well on dense graphs because its elements are stored in a predictable layout.

An adjacency list can be more memory-efficient for sparse graphs, although hash-map overhead can be significant.

An edge list is compact and convenient for edge-oriented algorithms, but neighborhood retrieval may require repeated scanning.

The benchmark programs measure edge lookup, neighbor retrieval, edge enumeration, and approximate memory consumption.

Benchmark results should be interpreted as measurements of the particular runtime and hardware, not universal performance guarantees.

## 17. Security and Data Integrity

Graph implementations should validate input before changing internal state.

Important controls include:

- Rejecting invalid vertex identifiers.
- Rejecting non-finite edge weights.
- Validating graph direction.
- Preventing accidental duplicate logical edges.
- Checking foreign-key relationships.
- Avoiding untrusted object deserialization.
- Restricting database modification privileges.
- Using parameterized database operations.
- Protecting graph files through appropriate filesystem permissions.

For networked graph applications, additional controls may be required for authentication, authorization, input-size limits, resource quotas, and protection against expensive traversal requests.

The database implementation provides relational integrity, but production deployments should also apply suitable database roles and access policies.

## 18. Implementation Scope and Trade-offs

| Deliverable | Primary engineering perspective |
|---|---|
| Python | Extensible graph interface, validation, algorithms, persistence and testing |
| JavaScript | Event-driven graph changes, Maps, Sets and asynchronous processing |
| C++17 | STL containers, memory estimation and explicit resource ownership |
| Java 17 | Immutable records, interfaces, service separation and asynchronous execution |
| PostgreSQL | Relational graph storage, integrity constraints, functions and analytical reporting |

The source implementations use different internal storage choices to demonstrate that a graph's logical structure is independent of its physical representation.

The SQL implementation stores the logical graph in relational tables. It does not claim that the relational storage engine physically allocates an adjacency matrix or in-memory adjacency list.

The memory figures are estimates. Actual storage measurements depend on the runtime, database engine, indexes, object overhead, and storage configuration.

## 19. Core Technical Distinctions

| Concept | Meaning |
|---|---|
| Graph | A collection of vertices and edges |
| Vertex | An individual graph element |
| Edge | A connection between vertices |
| Directed graph | A graph with directional connections |
| Undirected graph | A graph with bidirectional connections |
| Weighted graph | A graph whose edges carry numerical values |
| Adjacency matrix | A two-dimensional representation of connections |
| Adjacency list | A collection of neighbors for each vertex |
| Edge list | A collection of individual edge records |
| Degree | Number of connections associated with a vertex |
| Graph density | Ratio of existing edges to possible edges |
| BFS | Traversal using a queue |
| DFS | Traversal using a stack or recursion |
| Dijkstra | Shortest-path algorithm for non-negative weights |
| Sparse graph | A graph with relatively few edges |
| Dense graph | A graph with many edges relative to its possible maximum |

The central design decision is to select a graph representation according to the operations performed most frequently, the expected graph density, and the available memory.

A representation that is efficient for edge lookup may be less efficient for neighborhood retrieval. A representation that minimizes storage may require more computation when searching for connections. These trade-offs determine the suitability of adjacency matrices, adjacency lists, and edge lists for different graph-processing applications.
