# Floyd-Warshall Algorithm

## 1. Problem Definition

The Floyd-Warshall algorithm computes shortest-path distances between every ordered pair of vertices in a weighted graph.

It is an all-pairs shortest-path algorithm based on dynamic programming.

Given a directed weighted graph:

\[
G=(V,E)
\]

where:

- \(V\) is the set of vertices.
- \(E\) is the set of directed edges.
- \(w(u,v)\) is the weight of an edge from \(u\) to \(v\).

The algorithm calculates:

\[
D[i][j]
\]

where \(D[i][j]\) represents the minimum possible weight of a path from vertex \(i\) to vertex \(j\).

The algorithm supports:

- Directed graphs.
- Undirected graphs represented as pairs of directed edges.
- Positive edge weights.
- Zero-weight edges.
- Negative edge weights.
- Disconnected graphs.
- Multiple edges between the same vertices.

It does not produce well-defined finite shortest paths when a reachable negative-weight cycle exists.

## 2. Dynamic Programming Formulation

The central idea is to progressively expand the set of vertices permitted as intermediate vertices.

Let:

\[
D^{(k)}[i][j]
\]

represent the shortest distance from \(i\) to \(j\), allowing only the first \(k\) vertices as intermediate vertices.

Initially, no intermediate vertices are permitted.

### Initialisation

For every vertex:

\[
D[i][j]=
\begin{cases}
0 & i=j\\
w(i,j) & (i,j)\in E\\
\infty & \text{otherwise}
\end{cases}
\]

When multiple edges connect the same ordered pair, the minimum edge weight is selected.

### Recurrence relation

For an intermediate vertex \(k\):

\[
D^{(k)}[i][j]
=
\min
\left(
D^{(k-1)}[i][j],
D^{(k-1)}[i][k]+D^{(k-1)}[k][j]
\right)
\]

There are two possibilities:

1. The shortest path does not use vertex \(k\).
2. The shortest path passes through vertex \(k\).

The algorithm selects the smaller distance.

The in-place implementation uses:

\[
D[i][j]
=
\min(D[i][j],D[i][k]+D[k][j])
\]

The outer loop must process intermediate vertices. Reordering the loops can invalidate the dynamic programming formulation.

### Algorithm structure

The computation follows three nested loops:

- Outer loop: permitted intermediate vertex.
- Middle loop: source vertex.
- Inner loop: destination vertex.

For each combination, the algorithm evaluates whether routing through the intermediate vertex improves the existing distance.

## 3. Graph Representation

The implementations use adjacency-matrix-based shortest-path computation.

For \(V\) vertices, the distance matrix contains:

\[
V \times V
\]

entries.

An example directed graph:

| Source | Destination | Weight |
|---|---|---:|
| A | B | 4 |
| A | C | 2 |
| B | C | 1 |
| B | D | 5 |
| C | D | 8 |
| C | E | 10 |
| D | E | 2 |

A missing edge is represented by infinity rather than zero.

This distinction is important because zero is a valid edge weight.

### Parallel edges

When multiple edges connect the same vertices, only the smallest direct edge weight is needed for shortest-path computation.

### Self-loops

The initial distance from a vertex to itself is zero.

A positive self-loop does not improve that distance. A negative self-loop constitutes a negative cycle.

## 4. Path Reconstruction

Computing shortest distances does not automatically provide the actual route.

The implementations maintain an additional matrix called the next-vertex matrix.

\[
Next[i][j]
\]

stores the first vertex to visit after \(i\) when travelling towards \(j\).

### Initialisation

For a direct edge:

\[
Next[i][j]=j
\]

For a vertex travelling to itself:

\[
Next[i][i]=i
\]

For an unreachable pair:

\[
Next[i][j]=NULL
\]

### Updating the next-vertex matrix

When a shorter route through \(k\) is discovered:

\[
Next[i][j]=Next[i][k]
\]

This records the first movement towards the intermediate vertex.

### Reconstruction process

For a request from \(A\) to \(E\):

1. Begin at \(A\).
2. Read `Next[A][E]`.
3. Move to the returned vertex.
4. Continue reading the next-hop entry for the current vertex and destination.
5. Stop when \(E\) is reached.

Example:

`A -> B -> C -> D -> E`

The total path distance is obtained from the distance matrix.

Path reconstruction requires at most \(O(V)\) operations for a simple shortest path.

The implementations impose a vertex-count limit to detect invalid reconstruction states.

## 5. Negative Edge Weights and Negative Cycles

Floyd-Warshall supports negative edge weights.

For example:

| Edge | Weight |
|---|---:|
| A → B | 5 |
| B → C | -2 |
| A → C | 10 |

The shortest distance from A to C becomes:

\[
5+(-2)=3
\]

Negative weights do not independently indicate an invalid graph.

A negative cycle is different.

Consider:

| Edge | Weight |
|---|---:|
| A → B | 2 |
| B → C | -5 |
| C → A | 1 |

The total cycle weight is:

\[
2-5+1=-2
\]

Repeated traversal reduces the path cost indefinitely.

Consequently, no finite shortest distance exists for affected vertex pairs.

### Detection

After the algorithm completes, examine the diagonal:

\[
D[i][i]
\]

If:

\[
D[i][i]<0
\]

a negative cycle exists.

The implementations reject the computation rather than publishing invalid shortest-path results.

A negative cycle in one disconnected component does not affect shortest paths in another disconnected component, although a global all-pairs computation still reports that the graph contains a negative cycle.

## 6. Complexity Analysis

Let:

- \(V\) = number of vertices.
- \(E\) = number of edges.

| Operation | Time complexity |
|---|---:|
| Graph vertex initialisation | O(V) |
| Distance matrix initialisation | O(V²) |
| Edge initialisation | O(E) |
| Floyd-Warshall computation | O(V³) |
| Negative-cycle detection | O(V) |
| Single path reconstruction | O(V) |
| Complete distance matrix storage | O(V²) |
| Next-vertex matrix storage | O(V²) |

The total computational complexity is:

\[
\boxed{O(V^3)}
\]

The auxiliary matrix storage requirement is:

\[
\boxed{O(V^2)}
\]

The algorithm is suitable for relatively small and medium-sized dense graphs where distances between many pairs are required.

For very large sparse graphs, repeated single-source shortest-path algorithms may be more efficient.

## 7. Python Implementation

The Python implementation models the graph through `WeightedGraph`.

### Main components

| Component | Responsibility |
|---|---|
| `Edge` | Immutable edge representation |
| `WeightedGraph` | Vertex and edge management |
| `ShortestPathResult` | Distance and route queries |
| `GraphError` | Invalid graph operations |
| `NegativeCycleError` | Negative-cycle rejection |

### Important mechanisms

- Dictionaries provide vertex-to-index lookup.
- Lists represent distance and next-vertex matrices.
- Dataclasses provide structured edge and result models.
- Type annotations clarify the expected data structures.
- Exceptions distinguish invalid input from invalid shortest-path conditions.
- Assertions validate distance calculations and route reconstruction.

The implementation supports negative edges, parallel edges, disconnected vertices and zero-weight connections.

The result object provides separate methods for retrieving distances and reconstructing paths.

## 8. JavaScript Implementation

The JavaScript implementation uses an event-driven architecture.

### Main components

| Component | Responsibility |
|---|---|
| `GraphVertex` | Vertex identity and metadata |
| `WeightedGraph` | Graph state and version tracking |
| `FloydWarshallEngine` | Dynamic programming computation |
| `EventEmitter` | Computation lifecycle notifications |
| `computeAsync()` | Asynchronous scheduling |

### Event-driven computation

The engine emits:

- `iteration`: An intermediate vertex has been processed.
- `completed`: All shortest paths have been calculated.
- `failed`: Computation encountered an error.

The graph maintains a version number.

Every graph modification increments the version. Before returning a result, the engine checks whether its stored result corresponds to the current graph version.

If the graph has changed, the computation is repeated.

### Caching

Reconstructed paths are cached using source and destination indices.

This avoids repeated path reconstruction for identical queries.

The cache is invalidated when a new graph computation is performed.

The asynchronous wrapper yields execution before computation begins. The underlying algorithm is still synchronous and CPU-bound; it is not a parallel implementation.

## 9. C++17 Implementation

The C++ implementation models shortest-path computation as a dedicated graph-processing engine.

### Main components

| Component | Responsibility |
|---|---|
| `Edge` | Weighted edge structure |
| `WeightedGraph` | Graph storage and validation |
| `PathResult` | Structured route response |
| `FloydWarshallEngine` | Distance calculation and reconstruction |
| `GraphStatus` | Computation outcome |

### Engineering decisions

- `vector` provides efficient matrix storage.
- `unordered_map` provides average constant-time vertex lookup.
- `optional<int>` represents missing next-hop information.
- `numeric_limits<double>::infinity()` represents unreachable distances.
- Exceptions handle invalid graph operations and arithmetic failures.
- The engine refuses queries before a successful computation.

The implementation separates graph representation from shortest-path processing.

This makes the computation engine reusable across different graph instances.

## 10. Java 17 Implementation

The Java implementation uses an enterprise-oriented service architecture.

### Domain model

The principal records are:

- `Vertex`
- `Edge`
- `Route`
- `ComputationReport`
- `GraphSnapshot`

The `WeightedGraph` class manages graph state and version numbers.

The `ShortestPathService` interface defines the shortest-path computation contract.

`FloydWarshallService` implements the algorithm.

`RoutingApplication` coordinates computation, result publication and route queries.

### Snapshot-based processing

The service operates on an immutable graph snapshot.

This separates the computation input from subsequent graph modifications.

A computed result contains the graph version associated with its snapshot.

Before returning a route, the application verifies that the result corresponds to the current graph version.

### Failure management

The computation service detects negative cycles and throws a dedicated exception.

The application translates this condition into a structured computation report.

A failed candidate computation is not published as the current successful result.

The distance matrix is copied when exposed to callers to prevent external modification of internal state.

## 11. PostgreSQL Implementation

The PostgreSQL implementation models graph processing through relational tables and a stored PL/pgSQL function.

### Relational schema

| Table | Purpose |
|---|---|
| `networks` | Graph metadata |
| `vertices` | Graph vertices |
| `edges` | Directed weighted connections |
| `computations` | Execution history and status |
| `shortest_paths` | Calculated distances and reconstructed paths |

### Relationships

`networks`
  |
  +-- `vertices`
  |
  +-- `edges`
  |
  +-- `computations`
          |
          +-- `shortest_paths`

### Referential integrity

Foreign keys ensure that edges reference existing vertices and that vertices belong to the appropriate graph.

The edge-validation trigger provides an additional graph-membership check.

The database also enforces:

- Unique graph names.
- Unique vertex codes within a graph.
- Valid computation states.
- Finite numeric edge weights.
- Non-negative self-loop constraints.

Negative weights on ordinary edges remain permitted.

### Stored computation function

`graph.compute_floyd_warshall()` performs the following operations:

1. Validates the graph identifier.
2. Acquires a graph-level row lock.
3. Creates a computation record.
4. Initialises the temporary distance matrix.
5. Loads minimum direct-edge weights.
6. Processes intermediate vertices.
7. Detects negative cycles.
8. Reconstructs reachable paths.
9. Stores calculated results.
10. Updates computation status.

The temporary matrix uses SQL `NULL` to represent infinity.

The function uses a temporary relational matrix instead of persisting every intermediate dynamic programming state.

Only final shortest-path results are stored permanently.

### Reporting

The SQL script provides queries for:

- Graph and vertex retrieval.
- Direct edge inspection.
- All-pairs distance reporting.
- Path reconstruction.
- Distance aggregation.
- Unreachable vertex pairs.
- Computation status.
- Negative edge identification.

The `computation_summary` view combines graph metadata and execution information.

### Transaction management

The sample workflow uses a transaction to establish the schema and initial graph.

The graph-level row lock serializes computations for the same graph when the function is invoked within a transaction.

A graph update requires another computation to refresh its shortest-path results.

The computation history distinguishes successful calculations from negative-cycle and failed executions.

## 12. Practical Applications

Floyd-Warshall is useful when a system repeatedly needs shortest-path queries between many pairs of locations or states.

### Transportation networks

A transportation system can represent cities as vertices and direct routes as weighted edges.

The edge weight may represent distance, travel cost or a fixed travel-time estimate.

The resulting matrix supports repeated route queries without running a new shortest-path search for every request.

### Network routing

Vertices can represent network devices and edges can represent communication links.

Weights may represent latency, administrative cost or another additive routing metric.

### Dependency analysis

Vertices can represent software components or processing stages.

Directed edges can represent weighted transitions or dependency costs.

### Game development

Vertices can represent game states or map locations.

Edges can represent possible movements, with weights representing movement costs.

### Financial networks

Vertices can represent financial entities and edges can represent weighted relationships.

For exchange-rate arbitrage analysis, negative logarithms of exchange rates can be used as edge weights. A negative cycle can then indicate an arbitrage opportunity, subject to consistent exchange-rate data and transaction costs.

## 13. Correctness Considerations and Limitations

### Correctness

The algorithm relies on the optimal-substructure property of shortest paths.

For a shortest path that uses vertex \(k\), its subpaths from \(i\) to \(k\) and from \(k\) to \(j\) must also be shortest paths under the previously permitted intermediate vertices.

The recurrence considers both possible cases and retains the minimum.

After all vertices have been processed, every vertex is permitted as an intermediate vertex.

Therefore, in the absence of negative cycles, the resulting matrix contains all-pairs shortest distances.

### Important limitations

- Time complexity is cubic in the number of vertices.
- Memory consumption grows quadratically.
- A complete recomputation is required after graph changes.
- Floating-point arithmetic may introduce precision errors.
- Negative cycles prevent finite shortest-path solutions for affected pairs.
- The implementation does not automatically account for changing traffic conditions or time-dependent edge weights.
- Equal-cost alternative paths are not all retained. The next-hop matrix reconstructs one shortest path.

### Numeric precision

The Python and JavaScript implementations use floating-point numbers.

The C++ implementation uses `double`.

The Java implementation also uses `double`.

The PostgreSQL implementation uses fixed-precision `NUMERIC` values.

For applications involving financial calculations or strict decimal accuracy, an appropriate fixed-precision representation is preferable.

### Production considerations

A production implementation should consider:

- Maximum permitted vertex count.
- Input graph validation.
- Arithmetic overflow.
- Negative-cycle reporting.
- Graph versioning.
- Computation cancellation.
- Transaction boundaries.
- Concurrent graph updates.
- Result freshness.
- Memory allocation limits.
- Auditability of graph modifications.

The implementations demonstrate the same dynamic programming principle through distinct programming and database architectures.
