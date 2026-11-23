# Shortest Path Algorithms: Weighted Graphs, Negative Edges, and Algorithm Selection

## Project Description

This project introduces shortest-path problems through five independent implementations in Python, JavaScript, C++17, Java 17, and PostgreSQL.

The implementations use directed weighted graphs representing transportation networks. They demonstrate how to represent graph structures, calculate minimum-cost routes, reconstruct paths, handle negative weights, identify unreachable destinations, and detect negative-weight cycles.

The central engineering problem is determining which shortest-path algorithm is appropriate for a graph's edge-weight properties and the required query workload.

## 1. Graph Fundamentals

A graph is a mathematical structure consisting of vertices and edges.

A graph is represented as:

\[
G=(V,E)
\]

Where:

- \(V\) is the set of vertices.
- \(E\) is the set of edges connecting vertices.

A transportation network can be represented as follows:

| Vertex | Meaning |
|---|---|
| Delhi | Starting city |
| Jaipur | Intermediate city |
| Agra | Intermediate city |
| Bhopal | Intermediate city |
| Mumbai | Destination |

An edge represents a connection between two vertices.

A weighted edge contains:

\[
(u,v,w)
\]

Where:

- \(u\) is the source vertex.
- \(v\) is the destination vertex.
- \(w\) is the edge weight.

The weight may represent distance, time, monetary cost, or another measurable quantity.

For example:

| Source | Destination | Weight |
|---|---|---:|
| Delhi | Jaipur | 280 |
| Delhi | Agra | 230 |
| Jaipur | Mumbai | 1140 |
| Agra | Bhopal | 540 |
| Bhopal | Mumbai | 780 |

The graph is directed because an edge from Delhi to Jaipur does not automatically imply an edge from Jaipur to Delhi.

An undirected connection must be represented by two directed edges with equal weights.

## 2. Shortest-Path Problem

The shortest-path problem determines the minimum total edge weight required to travel from a source vertex to a destination vertex.

For a path containing vertices:

\[
P=(v_0,v_1,\ldots,v_k)
\]

Its total weight is:

\[
W(P)=\sum_{i=0}^{k-1}w(v_i,v_{i+1})
\]

The shortest-path objective is:

\[
d(s,t)=\min_{P:s\rightarrow t}W(P)
\]

Where:

- \(s\) is the source.
- \(t\) is the destination.
- \(d(s,t)\) is the minimum achievable path cost.

A shortest path is not necessarily the path containing the fewest edges.

For example:

| Route | Individual weights | Total |
|---|---|---:|
| Delhi → Jaipur → Mumbai | 280 + 1140 | 1420 |
| Delhi → Agra → Bhopal → Mumbai | 230 + 540 + 780 | 1550 |
| Delhi → Agra → Jaipur → Mumbai | 230 + 240 + 1140 | 1610 |

The first route is optimal among these alternatives.

A shortest-path result contains two separate outputs:

1. The minimum distance.
2. The sequence of vertices that produces that distance.

## 3. Graph Representation

### Adjacency List

The primary implementations use adjacency lists.

Each vertex stores its outgoing connections and their weights.

Conceptually:

    Delhi
      |
      +---- Jaipur (280)
      |
      +---- Agra (230)
      |
      +---- Chandigarh (250)

An adjacency list is efficient for sparse graphs because it stores existing edges rather than every possible vertex pair.

Its storage complexity is:

\[
O(V+E)
\]

### Adjacency Matrix

An adjacency matrix stores edge weights in a two-dimensional matrix.

For vertices \(V_1,V_2,\ldots,V_n\), the entry:

\[
A[i][j]
\]

represents the weight of the edge from vertex \(i\) to vertex \(j\).

An absent edge is represented by infinity.

Storage complexity:

\[
O(V^2)
\]

Adjacency matrices are useful for dense graphs and algorithms requiring frequent access to arbitrary vertex pairs.

### Directed and Undirected Graphs

A directed graph maintains edge direction.

An undirected graph represents connections that can be traversed in both directions.

An undirected weighted edge is normally represented as:

\[
(u,v,w)
\]

and:

\[
(v,u,w)
\]

This distinction matters when calculating routes and detecting cycles.

## 4. Understanding Edge Weights

Three important weight categories determine algorithm selection.

| Weight category | Example | Algorithm implications |
|---|---|---|
| Positive | 12 | Dijkstra and Bellman-Ford |
| Zero | 0 | Dijkstra and Bellman-Ford |
| Negative | -5 | Bellman-Ford or other suitable algorithms |

### Positive Weights

A positive edge increases the accumulated path cost.

Examples include:

- Travel distance.
- Delivery time.
- Network latency.
- Transportation charges.

### Zero-Weight Edges

A zero-weight edge represents a connection with no additional cost.

Dijkstra supports zero-weight edges.

### Negative Weights

A negative edge reduces the accumulated path cost.

Negative values can represent:

- Financial credits.
- Discounts.
- Reward adjustments.
- Certain optimization transformations.

Negative weights require special attention because they invalidate Dijkstra's greedy correctness assumption.

A graph containing negative edges does not necessarily contain a negative cycle.

These are different properties.

## 5. Dijkstra's Algorithm

Dijkstra's algorithm finds shortest paths from a source vertex in a graph containing only nonnegative edge weights.

It uses a greedy strategy.

At each iteration, it selects the unsettled vertex with the smallest tentative distance.

That distance becomes final because no subsequently discovered path can reduce it when every edge weight is nonnegative.

### Processing Mechanism

1. Assign distance zero to the source.
2. Assign infinity to every other vertex.
3. Insert the source into a minimum-priority queue.
4. Extract the vertex with the smallest tentative distance.
5. Examine its outgoing edges.
6. Relax edges when a shorter route is discovered.
7. Record the predecessor of each improved vertex.
8. Continue until the queue is empty or the destination is finalized.

### Edge Relaxation

Suppose an edge connects \(u\) to \(v\).

The current candidate distance is:

\[
candidate=d(u)+w(u,v)
\]

Update the distance when:

\[
candidate<d(v)
\]

The predecessor of \(v\) becomes \(u\).

### Complexity

Using an adjacency list and binary heap:

\[
O((V+E)\log V)
\]

Space complexity:

\[
O(V+E)
\]

### Limitations

Dijkstra cannot safely process negative-weight edges.

Its greedy selection may finalize a vertex before a later negative edge produces a shorter route.

The Python, JavaScript, C++, and Java implementations explicitly reject graphs containing negative edges when Dijkstra is requested.

## 6. Bellman-Ford Algorithm

Bellman-Ford calculates shortest paths from a source vertex even when negative-weight edges exist.

It also detects negative-weight cycles reachable from the source.

Unlike Dijkstra, it does not depend on permanently finalizing the currently closest vertex.

### Processing Mechanism

For a graph containing \(V\) vertices, a shortest simple path can contain at most:

\[
V-1
\]

edges.

Bellman-Ford therefore performs up to \(V-1\) complete relaxation passes.

For every edge:

\[
(u,v,w)
\]

it evaluates:

\[
d(v)>d(u)+w
\]

If the condition is true, the distance and predecessor are updated.

An iteration can terminate early if no distance changes.

### Negative-Cycle Detection

After the relaxation passes, examine every edge again.

If an edge can still reduce a reachable vertex's distance, a reachable negative cycle exists.

The shortest distance is then undefined for destinations that can be reached from that cycle.

A negative cycle is a cycle whose total weight is less than zero.

Example:

    A --2--> B
             |
            -4
             |
             v
             C
             |
             +--1--> B

The cycle weight is:

\[
-4+1=-3
\]

Repeated traversal decreases the accumulated cost without a finite lower bound.

### Complexity

Time complexity:

\[
O(VE)
\]

Space complexity:

\[
O(V)
\]

excluding graph storage.

### Important Distinction

Bellman-Ford detects negative cycles reachable from its selected source.

An unreachable negative cycle does not invalidate shortest paths from that source.

Detecting negative cycles anywhere in a graph requires checking every connected component, typically by initializing all vertices to distance zero in a separate Bellman-Ford procedure.

## 7. Floyd-Warshall Algorithm

Floyd-Warshall calculates shortest paths between every pair of vertices.

It is an all-pairs shortest-path algorithm.

Its central operation considers whether an intermediate vertex improves a route between two other vertices.

The recurrence is:

\[
D_k(i,j)=
\min\left(
D_{k-1}(i,j),
D_{k-1}(i,k)+D_{k-1}(k,j)
\right)
\]

Where:

- \(i\) is the source.
- \(j\) is the destination.
- \(k\) is the intermediate vertex.

### Processing

1. Initialize each diagonal entry to zero.
2. Initialize direct edges with their weights.
3. Initialize missing connections to infinity.
4. Consider each vertex as an intermediate vertex.
5. Update every source-destination pair.
6. Inspect diagonal entries for negative cycles.

A negative diagonal entry indicates a negative-weight cycle.

### Complexity

Time:

\[
O(V^3)
\]

Space:

\[
O(V^2)
\]

Floyd-Warshall is appropriate for relatively small graphs when many source-destination queries are required.

It is less suitable for large sparse graphs.

The Python implementation includes this algorithm as an all-pairs extension.

## 8. Algorithm Selection

Algorithm selection depends on graph properties and the number of queries.

| Algorithm | Edge-weight support | Problem type | Time complexity |
|---|---|---|---|
| BFS | Equal, unweighted edges | Single-source | \(O(V+E)\) |
| Dijkstra | Nonnegative | Single-source | \(O((V+E)\log V)\) |
| Bellman-Ford | Positive, zero, negative | Single-source | \(O(VE)\) |
| Floyd-Warshall | Positive, zero, negative | All-pairs | \(O(V^3)\) |

BFS is suitable when every edge has equal traversal cost.

It is not a general solution for arbitrary weighted graphs.

A practical decision process is:

    Are all edges equally weighted?
              |
         Yes  |  No
          |   |
         BFS  Is every weight nonnegative?
                    |
               Yes  |  No
                |   |
            Dijkstra Bellman-Ford

    Many all-pairs queries on a small graph?
                    |
              Consider Floyd-Warshall

This selection process assumes that negative cycles are handled appropriately.

No algorithm can produce a finite minimum path cost for a destination whose route can repeatedly exploit a reachable negative cycle.

## 9. Path Reconstruction

Shortest-path algorithms typically maintain a predecessor structure.

A predecessor records the vertex from which a vertex obtained its best known distance.

For example:

| Vertex | Predecessor |
|---|---|
| Delhi | None |
| Agra | Delhi |
| Bhopal | Agra |
| Mumbai | Bhopal |

Path reconstruction starts at the destination and follows predecessors until reaching the source.

The resulting sequence is reversed to produce the forward path.

For a path containing \(k\) edges, reconstruction takes:

\[
O(k)
\]

A destination with infinite distance has no reconstructed path.

The source-to-itself path has distance zero and contains only the source vertex.

## 10. Implementation Architecture

### Python

The Python implementation provides a reusable graph model.

| Component | Responsibility |
|---|---|
| `Edge` | Immutable edge representation |
| `Algorithm` | Algorithm selection |
| `PathResult` | Distance, path, and algorithm |
| `WeightedGraph` | Graph storage and shortest-path operations |
| `NegativeCycleError` | Negative-cycle failure |
| `main()` | Executable demonstrations |

Important implementation decisions:

- Adjacency lists provide sparse-graph storage efficiency.
- `heapq` implements the Dijkstra priority queue.
- Bellman-Ford operates on a centralized edge list.
- Predecessor dictionaries support path reconstruction.
- Automatic selection considers negative-edge presence.
- Assertions verify important expected behavior.

### JavaScript

The JavaScript implementation emphasizes asynchronous application integration.

| Component | Responsibility |
|---|---|
| `WeightedGraph` | Graph representation and algorithms |
| `MinHeap` | Priority queue |
| `RoutingService` | Asynchronous route execution |
| `EventEmitter` | Route lifecycle notifications |
| `GraphValidationError` | Input validation |
| `NegativeCycleError` | Negative-cycle reporting |

The routing service emits:

- `route:requested`
- `route:completed`
- `route:failed`

This design separates graph computation from application-level event handling.

Promises provide an asynchronous service interface without requiring the graph algorithm itself to perform unnecessary network operations.

The graph revision number identifies the graph version associated with a returned result.

### C++17

The C++ implementation uses explicit integer vertex identifiers internally.

String names are mapped to integer indices.

This reduces repeated string-based graph traversal operations.

Its main components are:

- `Edge`
- `PathResult`
- `Graph`
- `Algorithm`

The Dijkstra implementation uses `std::priority_queue` with a minimum-distance comparator.

Bellman-Ford uses a contiguous edge collection, allowing sequential edge relaxation.

The design uses STL containers and avoids third-party dependencies.

### Java 17

The Java implementation adopts an enterprise-oriented service architecture.

| Component | Responsibility |
|---|---|
| `Edge` | Immutable edge record |
| `Route` | Immutable route result |
| `WeightedGraph` | Graph state and algorithm execution |
| `RoutingPolicy` | Algorithm-selection contract |
| `SafeRoutingPolicy` | Weight-based algorithm selection |
| `RoutingService` | Application-facing routing service |
| `GraphException` | Graph-related failures |
| `NegativeCycleException` | Negative-cycle failures |

Records provide immutable domain data.

The policy interface separates algorithm selection from route execution.

Synchronized graph operations protect graph state from concurrent modifications during calculations.

The graph version provides a simple way to identify the state used for a calculation.

## 11. PostgreSQL Data Model

The PostgreSQL implementation represents the graph as relational data.

Its principal relationships are:

    Graph
      |
      +---- Vertex
      |       |
      |       +---- Edge source
      |       |
      |       +---- Edge destination
      |
      +---- Algorithm Run
               |
               +---- Path Step

### Graph Table

Stores graph metadata, including its name and directedness.

### Vertex Table

Stores individual graph vertices.

The unique constraint on `(graph_id, vertex_code)` prevents duplicate vertex codes inside a graph.

### Edge Table

Stores weighted connections.

Composite foreign keys ensure that both endpoints belong to the same graph.

The edge validation trigger rejects inactive or invalid endpoints.

### Algorithm Run

Stores the execution history of shortest-path requests.

It records:

- Source and destination.
- Selected algorithm.
- Execution status.
- Computed distance.
- Computed path.
- Negative-edge information.
- Graph revision.
- Execution timestamps.

### Path Step

Stores individual vertices in a computed route, together with their cumulative distances.

### Graph Revision

Tracks changes to graph edges.

The revision number can help identify results calculated against an earlier graph state.

A production implementation would also require suitable transaction isolation and concurrency controls when graph updates and route calculations occur simultaneously.

## 12. PostgreSQL Workflow

The SQL script includes the following operations:

| Database object | Purpose |
|---|---|
| `graph` | Graph metadata |
| `vertex` | Vertex records |
| `edge` | Weighted connections |
| `algorithm_run` | Execution history |
| `path_step` | Reconstructed route |
| `graph_revision` | Graph version tracking |
| `validate_edge_graph()` | Edge integrity validation |
| `update_graph_revision()` | Revision tracking |
| `choose_algorithm()` | Algorithm selection |
| `active_graph_edges` | Active connection view |
| `graph_statistics` | Graph-level reporting |
| `enumerate_simple_paths()` | Recursive route enumeration |
| `shortest_path_report()` | Minimum simple-path report |
| `execute_path_request()` | Transactional execution workflow |

### Recursive CTE

The recursive path function begins with the source vertex.

It then extends paths through outgoing edges.

A visited-vertex array prevents a vertex from appearing twice in the same path.

This produces simple paths.

The resulting paths are ordered by total weight.

The procedure records the selected route and its path steps.

### Important Limitation

The PostgreSQL recursive path implementation is an educational enumeration method, not a scalable implementation of Dijkstra or Bellman-Ford.

The number of simple paths can grow exponentially.

The maximum depth limits the search but does not make it suitable for unrestricted large graphs.

The SQL implementation also does not perform general negative-cycle detection.

The dedicated negative-cycle query detects negative two-edge cycles only.

The Python, JavaScript, C++, and Java implementations provide general source-reachable negative-cycle detection through Bellman-Ford.

For large production graphs, an indexed iterative shortest-path engine is preferable to exhaustive recursive path enumeration.

## 13. Negative Edges and Negative Cycles

The distinction between negative edges and negative cycles is essential.

| Property | Negative edge | Negative cycle |
|---|---|---|
| Meaning | An individual edge has negative weight | A complete cycle has negative total weight |
| Dijkstra | Unsupported | Unsupported |
| Bellman-Ford | Supported | Detected when reachable |
| Finite shortest distance | Possible | Not possible for affected destinations |

Consider:

    A --4--> B
    |
    5
    |
    v
    C <-- -3 -- B
    |
    4
    |
    v
    D

The negative edge from B to C does not automatically create a negative cycle.

Bellman-Ford can calculate the shortest route from A to D.

By contrast, a reachable cycle with total weight below zero makes repeated traversal increasingly inexpensive.

## 14. Edge Cases and Failure Handling

The implementations address important graph conditions.

| Condition | Expected behavior |
|---|---|
| Unknown source | Reject the request |
| Unknown destination | Reject the request |
| Empty vertex name | Reject graph insertion |
| Infinite edge weight | Reject graph insertion |
| NaN edge weight | Reject graph insertion |
| Negative edge with Dijkstra | Reject execution |
| Negative cycle reachable from source | Raise an error |
| Unreachable destination | Return infinite distance |
| Source equals destination | Return distance zero |
| Duplicate vertex | Reuse existing vertex |
| Isolated vertex | Remain valid |
| Zero-weight edge | Process normally |

A production system must also consider:

- Numeric overflow.
- Decimal precision.
- Large graph memory requirements.
- Concurrent graph modifications.
- Stale route results.
- Input authorization.
- Request timeouts.
- Resource exhaustion.
- Graph update consistency.

## 15. Performance Considerations

| Operation | Time complexity |
|---|---|
| Add vertex | Average \(O(1)\) |
| Add edge | \(O(1)\) amortized |
| Dijkstra with binary heap | \(O((V+E)\log V)\) |
| Bellman-Ford | \(O(VE)\) |
| Floyd-Warshall | \(O(V^3)\) |
| Path reconstruction | \(O(V)\) worst case |
| Adjacency-list storage | \(O(V+E)\) |
| Floyd-Warshall storage | \(O(V^2)\) |

The actual runtime depends on graph density, edge distribution, data representation, and the number of queries.

For nonnegative sparse graphs, Dijkstra is generally the preferred single-source approach.

For negative-weight graphs without reachable negative cycles, Bellman-Ford provides a reliable solution.

For repeated all-pairs queries on smaller graphs, Floyd-Warshall may be appropriate.

For very large sparse graphs, specialized algorithms and data structures may provide better performance.

## 16. Security and Production Considerations

Shortest-path computation is not inherently an authentication or authorization mechanism.

A production routing service must protect its graph data and execution interface.

Important controls include:

- Validate all vertex identifiers.
- Reject non-finite numerical inputs.
- Restrict graph modification permissions.
- Use parameterized database operations.
- Apply transaction boundaries to graph updates.
- Limit request size and graph depth.
- Prevent unrestricted recursive path enumeration.
- Apply execution timeouts.
- Track graph versions.
- Record calculation failures.
- Validate results before downstream use.

Graph data can also contain commercially sensitive information, such as logistics routes, network topology, and transportation costs.

Access controls should apply to graph retrieval and modification independently.

## 17. Practical Applications

Shortest-path algorithms support several engineering domains.

| Domain | Graph interpretation | Edge weight |
|---|---|---|
| Transportation | Cities and roads | Distance or time |
| Logistics | Warehouses and delivery locations | Delivery cost |
| Computer networks | Routers and connections | Latency |
| Telecommunications | Network nodes | Transmission cost |
| Finance | Financial states and transitions | Cost or reward |
| Project planning | Activities and dependencies | Duration |
| Robotics | Navigation positions | Movement cost |
| Cloud infrastructure | Services and network links | Latency or resource cost |

The same mathematical model supports these different applications, but the meaning of an edge weight determines which algorithms and constraints are appropriate.

## 18. Learning Objectives

The five implementations establish the following technical distinctions:

1. A graph models relationships between vertices.
2. An edge weight represents traversal cost.
3. A shortest path minimizes accumulated edge weight.
4. Dijkstra uses greedy selection and requires nonnegative weights.
5. Bellman-Ford supports negative edges and detects reachable negative cycles.
6. Floyd-Warshall computes all-pairs shortest distances.
7. Predecessor structures reconstruct actual routes.
8. Algorithm selection depends on graph properties and query requirements.
9. Adjacency lists and matrices have different storage and performance characteristics.
10. Database integrity, graph versioning, and execution tracking support reliable routing workflows.

The essential algorithm-selection distinction is that nonnegative weighted graphs permit Dijkstra, negative-weight graphs require an algorithm that supports negative edges, and negative cycles can make shortest-path distances mathematically undefined.
