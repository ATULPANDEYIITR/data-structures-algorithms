# Bellman-Ford Algorithm: Shortest Paths and Negative Cycle Detection

## 1. Technical Scope

The Bellman-Ford algorithm calculates shortest paths from one source vertex to all reachable vertices in a weighted directed graph.

Unlike Dijkstra's algorithm, Bellman-Ford supports negative edge weights. It can also detect negative-weight cycles reachable from the selected source.

The implementations demonstrate the algorithm through five engineering perspectives:

| Implementation | Primary engineering focus |
|---|---|
| Python | Graph simulation, algorithm mechanics, validation and testing |
| JavaScript | Event-driven execution, asynchronous processing and immutable snapshots |
| C++17 | Efficient graph representation and mergeable algorithm components |
| Java 17 | Enterprise domain modeling, service separation and immutable results |
| PostgreSQL | Relational graph storage, procedural computation and persistent analysis |

The implementations use directed graphs. An edge from vertex `u` to vertex `v` does not imply an edge from `v` to `u`.

## 2. Graph Terminology

A weighted directed graph is represented as:

\[
G=(V,E)
\]

Where:

- \(V\) is the set of vertices.
- \(E\) is the set of directed edges.
- \(w(u,v)\) represents the weight of the edge from \(u\) to \(v\).
- \(s\) is the source vertex.
- \(d[v]\) is the currently known distance from the source to vertex \(v\).

An edge contains three attributes:

| Attribute | Meaning |
|---|---|
| Source | Starting vertex |
| Destination | Ending vertex |
| Weight | Cost of traversing the edge |

Weights can be positive, zero or negative.

A negative edge does not necessarily indicate a negative cycle. It simply means that traversing that edge decreases the accumulated path cost.

## 3. Edge Relaxation

Relaxation is the central operation of Bellman-Ford.

For an edge \((u,v)\) with weight \(w\), the algorithm evaluates:

\[
d[v] > d[u]+w
\]

If this condition is true, the current distance to \(v\) is improved:

\[
d[v]=d[u]+w
\]

The predecessor of \(v\) is updated:

\[
pred[v]=u
\]

The predecessor relationship makes it possible to reconstruct the shortest path after computation.

### Initialization

All vertices initially have infinite distance except the source.

\[
d[s]=0
\]

\[
d[v]=\infty \quad \forall v\neq s
\]

All predecessor values initially remain undefined.

An implementation must distinguish an unreachable vertex from a vertex whose shortest-path distance is zero.

### Relaxation passes

The algorithm performs at most:

\[
V-1
\]

complete passes over the edge collection.

A shortest path without a negative cycle can be represented by a simple path containing at most \(V-1\) edges.

Each pass attempts to improve distances by examining every edge.

The algorithm can terminate early when an entire pass produces no updates. At that point, another pass cannot improve any distance in the current graph.

## 4. Negative Edge Weights

Consider the following directed graph:

| Source | Destination | Weight |
|---|---|---:|
| 0 | 1 | 4 |
| 0 | 2 | 5 |
| 1 | 2 | -2 |
| 2 | 3 | 3 |

Starting at vertex 0:

- Distance to vertex 0 is 0.
- Distance to vertex 1 becomes 4.
- Distance to vertex 2 improves from 5 to 2.
- Distance to vertex 3 becomes 5.

The shortest path to vertex 3 is:

\[
0\rightarrow1\rightarrow2\rightarrow3
\]

Its cost is:

\[
4+(-2)+3=5
\]

A negative edge can improve an existing path. This is why algorithms that assume non-negative weights cannot be applied without checking their assumptions.

Bellman-Ford does not reject negative edges.

## 5. Negative Cycle Detection

A negative-weight cycle is a directed cycle whose total weight is negative.

For example:

\[
1\rightarrow2\rightarrow3\rightarrow1
\]

With edge weights:

\[
-4,\quad 2,\quad 1
\]

The total cycle weight is:

\[
-4+2+1=-1
\]

Repeated traversal decreases the path cost indefinitely.

Consequently, there is no finite shortest-path distance for vertices that can be reached from this cycle.

### Detection procedure

After the normal \(V-1\) relaxation passes, Bellman-Ford examines every edge once more.

If an edge can still improve a distance:

\[
d[v]>d[u]+w(u,v)
\]

a reachable negative cycle exists.

The detection must ignore edges whose source has infinite distance. Otherwise, an unreachable negative cycle could incorrectly invalidate a source-specific analysis.

### Cycle reconstruction

The implementations maintain predecessor information.

When an additional relaxation is possible, the destination's predecessor is updated.

To identify a vertex inside the cycle:

1. Start at a vertex whose distance can still improve.
2. Follow predecessor links \(V\) times.
3. This enters the cycle when the predecessor chain is valid.
4. Continue following predecessors until the starting cycle vertex is reached.
5. Reverse the collected sequence to display the directed cycle.

The cycle is represented as a closed sequence, with the first vertex repeated at the end.

## 6. Negative-Cycle Impact Propagation

Detecting a negative cycle and identifying all affected vertices are separate operations.

A reachable negative cycle makes the shortest-path distance undefined for:

- Vertices belonging to the cycle.
- Vertices reachable from the cycle.

It does not invalidate vertices that are reachable from the source but cannot be reached from the negative cycle.

The implementations use breadth-first traversal after identifying relaxable edge destinations.

The propagation process is:

1. Identify destinations of edges that can still be relaxed.
2. Add those destinations to a queue.
3. Traverse their outgoing edges.
4. Mark each newly discovered vertex as affected.
5. Continue until no new vertices remain.

The resulting classification is:

| Vertex state | Meaning |
|---|---|
| Source | Selected starting vertex |
| Reachable | Finite shortest-path distance exists |
| Unreachable | No path exists from the source |
| Negative-cycle affected | No finite shortest-path distance exists |

This distinction prevents a common implementation error: treating every vertex in a graph as affected merely because a negative cycle exists somewhere in the graph.

## 7. Shortest-Path Reconstruction

The predecessor array or map stores the previous vertex in the best-known route.

For a destination \(t\), reconstruction begins at \(t\) and repeatedly follows:

\[
t\rightarrow pred[t]\rightarrow pred[pred[t]]
\]

The process stops at the source.

The collected vertices are reversed to produce the source-to-destination path.

Three outcomes must be handled separately:

- A valid path exists and has a finite cost.
- The destination is unreachable.
- The destination is affected by a reachable negative cycle.

The third outcome must not be reported as an ordinary unreachable destination. The shortest-path problem is undefined rather than merely disconnected.

## 8. Python Implementation

**File:** `bellman_ford.py`

The Python implementation emphasizes graph simulation and algorithm verification.

### Domain model

The `Edge` dataclass represents an immutable weighted edge.

`Graph` maintains:

- A vertex count.
- An edge list.
- An adjacency dictionary.

The edge list supports repeated full-edge relaxation passes. The adjacency dictionary supports efficient propagation of negative-cycle effects.

### Algorithm execution

The `bellman_ford()` method performs:

1. Distance initialization.
2. Repeated relaxation.
3. Early termination.
4. Additional negative-cycle detection.
5. Negative-cycle reconstruction.
6. Downstream impact propagation.

The `BellmanFordResult` dataclass stores distances, predecessors, cycle information and execution statistics.

### Validation and reliability

The implementation checks:

- Positive graph size.
- Valid vertex identifiers.
- Integer edge weights.
- Valid source and destination vertices.
- Consistent predecessor chains.

Python integers support arbitrary-precision arithmetic, avoiding fixed-width integer overflow in distance calculations.

The automated tests cover negative edges, reachable negative cycles, unreachable negative cycles, disconnected vertices, negative self-loops and zero-weight self-loops.

## 9. JavaScript Implementation

**File:** `bellman_ford.js`

The JavaScript implementation introduces asynchronous execution and event-driven observability.

### Graph management

`WeightedGraph` uses:

- `Set` for vertex membership.
- Arrays for edge storage.
- `Map` for adjacency relationships.
- `EventEmitter` for graph-change notifications.

The graph version increases whenever a vertex or edge is added.

A snapshot captures the graph state at the beginning of an analysis.

This prevents subsequent graph modifications from changing the input of an already-running calculation.

### Event-driven execution

`BellmanFordEngine` emits events for:

| Event | Purpose |
|---|---|
| `relaxed` | Reports a successful distance improvement |
| `passCompleted` | Reports the completion of a relaxation pass |
| `completed` | Reports the final analysis result |

The asynchronous execution periodically yields control using `setImmediate()`.

An optional `AbortSignal` supports cancellation.

### Numeric precision

JavaScript numbers use IEEE 754 floating-point representation.

Exact integer calculations are therefore restricted to the safe integer range.

The implementation validates weights and intermediate distances using `Number.isSafeInteger()`.

This is important because an apparently valid graph can produce path sums outside JavaScript's exact integer range.

For larger integer domains, a `BigInt`-based distance representation would be necessary.

## 10. C++17 Implementation

**File:** `bellman_ford.cpp`

The C++ implementation focuses on explicit data structures, predictable execution and efficient memory usage.

### Graph representation

The `WeightedGraph` class maintains:

- `vector<Edge>` for directed edges.
- `vector<vector<int>>` for adjacency.
- Fixed vertex indexing.
- Validation of edge endpoints.

The `BellmanFordResult` structure stores distances, predecessors, affected vertices and negative-cycle information.

### Integer safety

The implementation uses `long long` for path costs.

A finite infinity sentinel is used rather than relying on an arbitrary maximum value for ordinary arithmetic.

The `safeAdd()` function checks for overflow before calculating a candidate distance.

This avoids undefined behavior from signed integer overflow.

### Complexity considerations

The edge list is scanned directly during each relaxation pass.

Adjacency lists are used only when propagating negative-cycle effects.

This separates the algorithm's principal computational workload from graph traversal after cycle detection.

The implementation uses standard C++17 libraries without external dependencies.

## 11. Java 17 Implementation

**File:** `BellmanFordEnterprise.java`

The Java implementation separates graph management, algorithm execution, policy evaluation and result representation.

### Enterprise domain types

The implementation defines records for:

- `Edge`
- `VertexDistance`
- `GraphSnapshot`
- `AnalysisResult`

The records represent structured domain information and provide immutable result boundaries.

Enums describe vertex states and execution statuses.

### Service separation

`WeightedGraph` manages graph state and versioning.

`BellmanFordService` performs the algorithm.

`DistancePolicy` defines the relaxation decision.

`StandardDistancePolicy` implements the normal minimum-distance comparison.

This separation makes the algorithm's relaxation rule explicit without coupling graph storage to the analysis service.

### Snapshot consistency

Graph snapshots preserve the edge list and adjacency relationships for an individual execution.

The graph version is included in the analysis result.

This allows an application to identify which graph state produced a result.

### Failure handling

The implementation distinguishes:

- Invalid graph input.
- Invalid source vertices.
- Arithmetic overflow.
- Unreachable destinations.
- Negative-cycle-affected destinations.

A custom `NegativeCycleException` prevents callers from accidentally treating an undefined shortest path as a valid result.

## 12. PostgreSQL Implementation

**File:** `bellman_ford.sql`

The PostgreSQL implementation demonstrates how a graph algorithm can be integrated into a relational database.

### Relational model

The database uses the following relationships:

| Table | Responsibility |
|---|---|
| `graphs` | Stores graph definitions and versions |
| `vertices` | Stores graph vertices |
| `edges` | Stores directed weighted edges |
| `analysis_runs` | Stores individual algorithm executions |
| `analysis_results` | Stores per-vertex distances and states |
| `negative_cycles` | Stores negative-cycle analysis information |

The composite foreign keys ensure that both endpoints of an edge belong to the same graph.

Parallel edges are permitted.

This is important for networks in which multiple routes connect the same pair of vertices.

### Graph versioning

Triggers increment the graph version when vertices or edges change.

Each analysis run stores the graph version associated with its execution.

This supports historical identification of the input graph state.

### Procedural relaxation

The `bellman_ford()` PostgreSQL function uses PL/pgSQL arrays to maintain:

- Vertex identifiers.
- Distances.
- Predecessors.
- Negative-cycle impact flags.

An SQL `NULL` distance represents infinity.

The function executes the \(V-1\) relaxation passes, performs an additional negative-cycle detection scan and propagates affected status through outgoing edges.

### Persistent analysis

The `execute_analysis()` procedure:

1. Locks the graph metadata row.
2. Validates the source vertex.
3. Creates an analysis run.
4. Executes the Bellman-Ford function.
5. Stores per-vertex results.
6. Determines execution status.
7. Records negative-cycle impact information.

The procedure uses database transaction handling to ensure that persistent analysis records are not partially committed.

### Database reporting

The SQL script includes queries for:

- Graph inventory.
- Shortest-path results.
- Negative-cycle reporting.
- Reachability aggregation.
- Destination eligibility.
- Execution history.
- Negative-edge identification.

The `v_graph_analysis` view provides a combined reporting interface.

The persisted cycle array represents the affected vertex set, not an ordered reconstruction of the exact cycle. The Python, JavaScript, C++17 and Java 17 implementations provide explicit cycle reconstruction.

## 13. Algorithmic Complexity

Let:

- \(V\) = number of vertices.
- \(E\) = number of directed edges.

### Time complexity

The main relaxation phase performs at most \(V-1\) passes over all edges.

\[
O(VE)
\]

The additional negative-cycle detection pass requires:

\[
O(E)
\]

Negative-cycle impact propagation using adjacency lists requires:

\[
O(V+E)
\]

Therefore, the complete algorithm has worst-case complexity:

\[
\boxed{O(VE)}
\]

### Space complexity

The algorithm stores:

- Distances: \(O(V)\)
- Predecessors: \(O(V)\)
- Adjacency lists: \(O(V+E)\)
- Edge collection: \(O(E)\)
- Queue and cycle information: \(O(V)\)

The complete graph representation and algorithm state require:

\[
\boxed{O(V+E)}
\]

The SQL implementation additionally uses relational indexes, persistent analysis records and procedural arrays.

### Comparison with Dijkstra's algorithm

| Characteristic | Bellman-Ford | Dijkstra |
|---|---|---|
| Negative edges | Supported | Not supported by standard implementation |
| Negative-cycle detection | Yes, for cycles reachable from source | No |
| Typical complexity | \(O(VE)\) | \(O((V+E)\log V)\) with a binary heap |
| Relaxation approach | Repeated full-edge scans | Priority-based selection |
| Main advantage | Handles negative weights | More efficient for non-negative weights |
| Main limitation | Higher computational cost | Requires non-negative edge weights |

Bellman-Ford is appropriate when negative edge weights are possible or negative-cycle detection is required.

## 14. Edge Cases and Failure Conditions

| Scenario | Expected behavior |
|---|---|
| Single vertex without edges | Source distance is zero |
| Positive edge weights | Normal shortest-path calculation |
| Negative edge without a cycle | Negative edge contributes to a shorter path |
| Zero-weight edge | Valid relaxation candidate |
| Negative self-loop | Reachable negative cycle |
| Zero-weight self-loop | No negative cycle |
| Unreachable vertex | Distance remains infinite |
| Unreachable negative cycle | Does not invalidate source-specific distances |
| Reachable negative cycle | Cycle is detected |
| Downstream vertex of a negative cycle | Distance becomes undefined |
| Parallel edges | Each edge is evaluated independently |
| Invalid source | Input validation fails |
| Invalid endpoint | Graph integrity validation fails |
| Excessive numeric value | Implementation-specific numeric safety checks apply |

A graph containing a negative cycle does not necessarily have undefined shortest distances for every vertex.

Only vertices reachable from a negative cycle that is itself reachable from the selected source are affected.

## 15. Practical Applications

Bellman-Ford is useful in several graph-analysis scenarios:

- Network routing with negative link costs.
- Currency exchange arbitrage detection.
- Financial transaction networks.
- Dependency and constraint analysis.
- Transportation networks with rebates or credits.
- Directed cost optimization.
- Graph-based anomaly detection.

### Currency arbitrage interpretation

Currency conversion can be represented using logarithmic edge weights.

For an exchange rate \(r\):

\[
w=-\log(r)
\]

A cycle with a negative total weight indicates that the product of the exchange rates around that cycle exceeds one.

This can indicate an arbitrage opportunity before transaction fees, liquidity limitations and execution constraints are considered.

The algorithm detects the mathematical opportunity; it does not establish that the opportunity can be executed profitably in a real market.

## 16. Implementation Limitations

The implementations make several deliberate engineering tradeoffs.

- The graph is directed; undirected edges require adding both directions.
- The standard algorithm calculates shortest paths from one source at a time.
- Repeated analyses for multiple sources increase total computational cost.
- Floating-point edge weights require numerical tolerance policies that are not part of these integer-based examples.
- The JavaScript implementation is restricted to safe integer calculations.
- C++17 and Java 17 use bounded integer representations with explicit overflow checks.
- The PostgreSQL procedure persists analysis results but does not reconstruct the exact ordered negative cycle.
- The PostgreSQL reporting model records graph versions, but a graph version alone is not a complete historical copy of every edge and vertex.
- Early termination improves favorable cases but does not change worst-case complexity.

For large sparse graphs with non-negative weights, Dijkstra's algorithm is generally more efficient. When negative edges exist, Bellman-Ford provides the necessary relaxation and negative-cycle analysis mechanisms.
