# Dijkstra's Algorithm: Shortest Path Computing with Priority Queues

## 1. Technical Scope

Dijkstra's algorithm computes shortest paths from a selected source vertex to other reachable vertices in a weighted graph.

It is a greedy algorithm that repeatedly selects the unprocessed vertex with the smallest known distance. It then examines the outgoing edges and updates neighboring distances whenever a shorter route is discovered.

The algorithm is applicable when every edge has a non-negative weight.

Typical applications include:

- Road and transport navigation.
- Network packet routing.
- Telecommunications infrastructure.
- Supply-chain transportation.
- Geographic information systems.
- Infrastructure cost optimization.
- Network topology analysis.

The implementations use a transport network connecting Indian cities. Edge weights represent travel distances in kilometres.

## 2. Graph Fundamentals

A weighted graph is represented as:

\[
G=(V,E)
\]

Where:

- \(V\) represents the set of vertices.
- \(E\) represents the set of edges.
- Each edge has a numerical weight.
- A vertex represents a location or network node.
- An edge represents a connection between two vertices.

For example:

    Delhi --230-- Agra
    Delhi --280-- Jaipur
    Delhi --550-- Lucknow

The graph can be directed or undirected.

| Property | Directed graph | Undirected graph |
|---|---|---|
| Connection | One-way | Two-way |
| Edge representation | u → v | u ↔ v |
| Reverse edge | Not automatic | Automatically represented |
| Example | One-way road | Two-way road |

An adjacency list stores the connections of each vertex.

For a graph with \(V\) vertices and \(E\) edges, an adjacency list generally requires \(O(V+E)\) space.

This representation is particularly suitable for sparse graphs.

## 3. Dijkstra's Algorithm

### 3.1 Core principle

The algorithm maintains three important pieces of information:

| Structure | Purpose |
|---|---|
| Distance | Best known distance from the source |
| Predecessor | Previous vertex on the currently best route |
| Visited or settled | Whether the shortest distance has been finalized |

Initially:

\[
dist[source]=0
\]

For every other vertex:

\[
dist[v]=\infty
\]

The priority queue initially contains the source vertex with priority zero.

### 3.2 Edge relaxation

Suppose the algorithm processes vertex \(u\), and an edge connects \(u\) to \(v\) with weight \(w(u,v)\).

The candidate distance is:

\[
candidate=dist[u]+w(u,v)
\]

If:

\[
candidate<dist[v]
\]

the algorithm updates:

\[
dist[v]=candidate
\]

and:

\[
predecessor[v]=u
\]

This operation is called edge relaxation.

It improves the best known distance whenever a shorter route is discovered.

### 3.3 Algorithm workflow

    Initialize all distances to infinity
                |
                v
    Set source distance to zero
                |
                v
    Insert source into min-priority queue
                |
                v
    Extract vertex with minimum distance
                |
                v
    Ignore stale or already settled entries
                |
                v
    Examine outgoing edges
                |
                v
    Calculate candidate distances
                |
                v
    Update improved distances and predecessors
                |
                v
    Insert updated entries into priority queue
                |
                v
    Repeat until queue becomes empty
                |
                v
    Reconstruct shortest paths

### 3.4 Why the greedy approach works

Dijkstra's algorithm relies on the non-negative edge-weight condition.

When the vertex with the smallest tentative distance is selected, no alternative path through an unprocessed vertex can subsequently produce a smaller distance.

This property allows its distance to be finalized.

Negative edge weights invalidate this guarantee.

A negative-weight graph requires a different algorithm, such as Bellman-Ford, when negative cycles and reachability conditions are handled appropriately.

## 4. Priority Queue Implementation

A priority queue selects the next vertex according to its current tentative distance.

A binary min-heap is a suitable implementation.

Its important operations are:

| Operation | Time complexity |
|---|---:|
| Insert | \(O(\log V)\) |
| Extract minimum | \(O(\log V)\) |
| Read minimum | \(O(1)\) |

The priority queue does not need to contain only one entry for each vertex.

When a shorter distance is discovered, a new entry is inserted. The older entry remains in the queue until extracted.

This approach is called lazy deletion.

When an entry is extracted, the algorithm checks whether its distance still matches the best known distance.

If not, it is stale and is ignored.

This avoids implementing a specialized decrease-key operation.

For an adjacency-list graph with a binary heap, the commonly stated complexity is:

\[
O((V+E)\log V)
\]

The additional storage requirement is:

\[
O(V+E)
\]

The exact heap operation count can depend on the number of successful relaxations and parallel edges.

## 5. Shortest-Path Reconstruction

Calculating distances and reconstructing routes are separate operations.

The distance array or map identifies the minimum cost from the source.

The predecessor structure identifies the route used to obtain that cost.

Consider the directed graph:

    A --4--> B
    A --1--> C
    C --2--> B
    B --1--> D
    C --5--> D

The direct route from A to B costs 4.

The alternative route is:

    A -> C -> B

Its cost is:

\[
1+2=3
\]

Therefore, the algorithm replaces the earlier distance of 4 with 3.

The shortest route to D becomes:

    A -> C -> B -> D

Its total distance is:

\[
1+2+1=4
\]

Predecessor traversal starts at the destination and continues until reaching the source.

The resulting sequence is reversed to obtain the forward route.

An unreachable destination has an infinite distance and no valid path.

## 6. Pulling the Concepts Together Through the Transport Network

The example network contains:

- Delhi
- Agra
- Jaipur
- Lucknow
- Varanasi
- Patna
- Kolkata
- Ahmedabad
- Mumbai
- Pune
- Chennai

The connections represent undirected transport links.

A calculation beginning at Delhi produces the shortest known distance to every reachable city.

The shortest distance to a destination is not necessarily the weight of the direct edge from the source.

The algorithm can discover a more economical route through intermediate vertices.

This distinction is important in transport systems because a geographically direct connection is not always the lowest-cost route.

## 7. Python Implementation

**File:** `dijkstra.py`

The Python implementation uses:

- `dataclass` for edge and result structures.
- Dictionaries for adjacency lists and distances.
- `heapq` for the binary min-heap.
- A predecessor dictionary for path reconstruction.
- A settled set to avoid repeated processing.
- Assertions for executable test cases.

### Important implementation decisions

The priority queue stores distance, sequence number, and vertex.

The sequence number prevents comparison problems when two vertices have equal priorities.

Stale entries are discarded during extraction.

The graph validates weights before adding edges. Negative, infinite, and invalid numerical weights are rejected.

The result object separates route reconstruction from distance computation.

The implementation also handles:

- Zero-weight edges.
- Parallel edges.
- Disconnected vertices.
- Unknown source vertices.
- Unknown destinations.
- Equal-distance priority queue entries.

Python's floating-point representation permits fractional weights, but floating-point precision should be considered when working with exact financial or measurement values.

For exact integer distances, an integer-based implementation is preferable.

## 8. JavaScript Implementation

**File:** `dijkstra.js`

The JavaScript implementation provides an independent event-driven routing model.

Its main components are:

| Component | Responsibility |
|---|---|
| `MinPriorityQueue` | Implements binary min-heap operations |
| `RouteGraph` | Maintains the network and graph version |
| `RouteResult` | Stores distances and reconstructs paths |
| `RoutingService` | Provides asynchronous route requests |

### JavaScript-specific decisions

`Map` stores adjacency lists and calculated distances.

`Set` tracks settled vertices.

`EventEmitter` exposes graph modification events.

The graph maintains a version counter. A calculation verifies that the graph was not modified during execution.

The routing service uses a Promise-based interface and schedules calculation through the Node.js event loop.

The underlying calculation remains synchronous. The asynchronous interface provides a convenient integration point but does not make CPU-intensive Dijkstra execution non-blocking.

For large production workloads, worker threads or a dedicated routing service may be appropriate.

JavaScript uses IEEE 754 floating-point numbers. `Number.MAX_SAFE_INTEGER` is the largest integer that can be represented exactly. Production systems requiring larger exact integer weights should use `BigInt` with an appropriately adapted priority queue.

## 9. C++17 Implementation

**File:** `dijkstra.cpp`

The C++ implementation uses:

- `vector` for adjacency lists.
- `unordered_map` for vertex identification.
- `priority_queue` for minimum-distance extraction.
- `pair` for queue entries.
- `int64_t` for edge weights and distances.
- Structures for edges and calculated results.

The standard C++ priority queue is a max-heap by default.

The implementation uses `greater` to reverse its ordering and obtain minimum-distance extraction.

### Integer overflow protection

An integer addition can exceed the maximum representable value.

Before calculating:

\[
candidate=distance+weight
\]

the implementation checks:

\[
distance\leq INT64\_MAX-weight
\]

This prevents signed integer overflow.

The program also rejects negative weights before inserting edges.

The implementation separates vertex indexing from vertex names. This provides efficient access to adjacency lists without using strings throughout the shortest-path calculation.

## 10. Java 17 Implementation

**File:** `DijkstraEnterprise.java`

The Java implementation models shortest-path calculation as an enterprise routing service.

Its domain structures include:

- `Edge` record.
- `QueueEntry` record.
- `Route` record.
- `NetworkType` enumeration.
- `WeightedGraph` class.
- `ShortestPathResult` class.
- `ShortestPathService` class.
- `RoutingException` exception.

### Enterprise-oriented design

The graph maintains its own network state.

The service obtains an immutable graph snapshot before calculation. This prevents the calculation from observing partially modified adjacency lists.

The result object exposes immutable distance maps and path lists.

The route record distinguishes reachable and unreachable destinations.

A dedicated service separates graph storage from shortest-path computation.

This design supports future integration with network management systems, routing APIs, and enterprise applications.

The Java implementation also checks integer overflow before distance addition.

## 11. PostgreSQL Implementation

**File:** `dijkstra.sql`

The PostgreSQL implementation stores graph information relationally.

### Relational data model

| Table | Purpose |
|---|---|
| `graph` | Stores graph definitions and graph types |
| `vertex` | Stores graph vertices |
| `edge` | Stores weighted connections |
| `route_execution` | Stores calculated route results |

The relationship is:

    Graph
      |
      +---- Vertices
      |
      +---- Edges
      |
      +---- Route Executions

Each edge references its source and destination vertices.

Composite foreign keys ensure that both vertices belong to the same graph.

The edge weight constraint prevents negative values.

The uniqueness constraint prevents duplicate directed connections between the same pair of vertices.

For undirected graphs, the insertion procedure creates both directions.

### SQL Dijkstra implementation

The `dijkstra` function maintains four arrays:

- `vertex_ids`
- `distances`
- `predecessors`
- `visited`

The function selects the unvisited vertex having the smallest non-null distance.

It then relaxes its outgoing edges.

Unlike the Python, C++, Java, and JavaScript implementations, this SQL version uses linear minimum selection rather than a binary heap.

Consequently, its time complexity is:

\[
O(V^2+E)
\]

This is a deliberate implementation trade-off. It keeps the database algorithm self-contained without requiring a custom heap structure in PL/pgSQL.

The `shortest_path` function reconstructs a destination route using predecessor identifiers.

The `execute_route` procedure records the route, total distance, execution status, and execution duration.

### Database integrity

The database uses:

- Primary keys.
- Composite foreign keys.
- Unique constraints.
- Non-negative weight constraints.
- Active-state validation.
- Insertion triggers.
- Transactional edge insertion.
- Execution history.
- Performance-oriented indexes.

The SQL implementation is suitable for learning and moderate database-resident graphs.

For large sparse graphs, an application-level binary heap or a specialized graph-processing system is more appropriate.

## 12. Distinguishing the Implementations

| Feature | Python | JavaScript | C++17 | Java 17 | PostgreSQL |
|---|---|---|---|---|---|
| Graph storage | Dictionary | Map | Vector | Map | Relational tables |
| Priority queue | `heapq` | Custom binary heap | STL priority queue | PriorityQueue | Linear selection |
| Distance type | Float | Number | int64 | long | BIGINT |
| Path reconstruction | Predecessor map | Predecessor map | Predecessor vector | Predecessor map | Predecessor array |
| Disconnected graph | Supported | Supported | Supported | Supported | Supported |
| Negative weights | Rejected | Rejected | Rejected | Rejected | Rejected |
| Overflow protection | Floating-point checks | Finite-number checks | Explicit | Explicit | Explicit |

The implementations use the same algorithmic principle while adopting data structures appropriate to their respective environments.

## 13. Edge Cases and Failure Conditions

| Scenario | Expected behavior |
|---|---|
| Source equals destination | Distance is zero |
| Zero-weight edge | Accepted |
| Negative edge | Rejected |
| Infinite weight | Rejected where supported |
| Unreachable destination | No route returned |
| Unknown source | Validation error |
| Unknown destination | Validation error |
| Parallel edges | Minimum available edge determines the better relaxation |
| Equal candidate distances | Existing predecessor is retained |
| Large distance | Overflow or numeric-range protection |
| Isolated vertex | Remains unreachable from other components |

### Negative-weight limitation

Dijkstra's algorithm cannot guarantee correct results for graphs containing negative-weight edges.

A negative edge can provide a shorter route after a vertex has already been settled.

The algorithm's greedy selection property depends on non-negative edge weights.

### Zero-weight edges

Zero-weight edges are valid.

They do not violate the greedy property and can represent free transitions, logical network links, or connections with no additional cost.

### Disconnected graphs

A disconnected graph contains vertices that cannot be reached from the selected source.

Their distances remain infinite or null, depending on the implementation.

The algorithm does not treat unreachable vertices as calculation failures.

## 14. Performance Analysis

Let:

- \(V\) = number of vertices.
- \(E\) = number of edges.

| Implementation | Shortest-path time | Auxiliary storage |
|---|---:|---:|
| Python | \(O((V+E)\log V)\) | \(O(V+E)\) |
| JavaScript | \(O((V+E)\log V)\) | \(O(V+E)\) |
| C++17 | \(O((V+E)\log V)\) | \(O(V+E)\) |
| Java 17 | \(O((V+E)\log V)\) | \(O(V+E)\) |
| PostgreSQL | \(O(V^2+E)\) | \(O(V)\) |

The priority-queue implementations are particularly effective for sparse graphs.

A dense graph may justify alternative representations and algorithmic approaches.

An adjacency matrix with linear minimum selection can be appropriate for dense graphs.

A binary heap is not always the optimal data structure for every graph size and density.

## 15. Practical Engineering Considerations

Production routing systems must account for more than the shortest-path algorithm.

### Weight definition

A weight can represent:

- Physical distance.
- Travel duration.
- Monetary transportation cost.
- Network latency.
- Energy consumption.
- Operational penalties.

The meaning of the weight must remain consistent throughout a graph.

### Dynamic networks

Road conditions, network failures, and changing transportation costs can modify edge weights.

A calculated route is valid for the graph state used during computation.

Dynamic systems should associate route calculations with graph versions or timestamps.

### Security and validation

External graph data should be validated before insertion.

Important controls include:

- Input validation.
- Non-negative weight enforcement.
- Vertex ownership validation.
- Database transaction boundaries.
- Protection against integer overflow.
- Controlled access to graph modification.
- Auditable route execution records.

### Concurrency

When graph updates occur during route computation, the system should use a consistent snapshot or versioning strategy.

The Java implementation uses an immutable calculation snapshot.

The JavaScript implementation detects graph version changes.

Database transactions provide consistency for relational graph modifications.

### Operational monitoring

Useful metrics include:

- Number of vertices.
- Number of edges.
- Number of reachable destinations.
- Route computation duration.
- Graph modification frequency.
- Failed route requests.
- Unreachable destination frequency.

These measurements help identify data-quality problems and performance bottlenecks.

## 16. Execution Instructions

### Python

Save the source as `dijkstra.py`.

Run:

`python dijkstra.py`

### JavaScript

Save the source as `dijkstra.js`.

Run:

`node dijkstra.js`

### C++17

Save the source as `dijkstra.cpp`.

Compile:

`g++ -std=c++17 -O2 -Wall -Wextra -pedantic dijkstra.cpp -o dijkstra`

Run:

`./dijkstra`

On Windows:

`dijkstra.exe`

### Java 17

Save the source as `DijkstraEnterprise.java`.

Compile:

`javac DijkstraEnterprise.java`

Run:

`java DijkstraEnterprise`

### PostgreSQL

Save the SQL source as `dijkstra.sql`.

Execute using:

`psql -U postgres -d postgres -f dijkstra.sql`

The script creates the `shortest_path` schema and its database objects.

Run it in a development database because it drops and recreates that schema.

## 17. Learning Outcomes

The implementations demonstrate the relationship between graph representation, greedy optimization, priority queues, edge relaxation, predecessor tracking, and shortest-path reconstruction.

They also illustrate how the same algorithmic problem can be approached using different engineering models:

- Python emphasizes concise data structures and executable validation.
- JavaScript emphasizes event-driven graph management and asynchronous service interfaces.
- C++17 emphasizes efficient memory structures and explicit numerical safety.
- Java 17 emphasizes domain modeling, immutable results, and service separation.
- PostgreSQL emphasizes relational integrity, database-resident computation, and execution auditing.

The central correctness requirement remains unchanged across all five implementations: every edge must have a non-negative weight, and every relaxation must preserve the best known distance from the selected source.
