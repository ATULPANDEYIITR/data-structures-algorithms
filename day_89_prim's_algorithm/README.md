# Prim's Algorithm: Minimum Spanning Tree Using Priority Queues and Adjacency Lists

## 1. Project Overview

Prim's Algorithm is a greedy graph algorithm used to find a Minimum Spanning Tree (MST) of a connected, undirected, weighted graph.

A Minimum Spanning Tree connects every vertex while satisfying two conditions:

- The resulting structure contains no cycles.
- The sum of selected edge weights is minimum among all possible spanning trees.

For a connected graph containing `V` vertices, an MST contains exactly `V - 1` edges.

For a disconnected graph, Prim's algorithm can be extended to produce a Minimum Spanning Forest (MSF). Each connected component receives its own minimum spanning tree.

This project implements Prim's algorithm using adjacency lists and priority queues in five independent technical environments:

| Implementation | Main engineering approach |
|---|---|
| Python | Graph simulation, heap operations and verification |
| JavaScript | Event-driven execution and asynchronous processing |
| C++17 | Efficient graph processing with STL containers |
| Java 17 | Enterprise-oriented domain modeling and execution management |
| PostgreSQL | Relational graph storage and database-side execution |

The implementations share the same algorithmic objective but use different data structures and software engineering approaches.

## 2. Fundamental Graph Concepts

### 2.1 Graph

A graph is represented mathematically as:

`G = (V, E)`

Where:

- `V` represents the set of vertices.
- `E` represents the set of edges.

A weighted undirected graph assigns a numerical weight to every edge.

An example:

    A -------- 4 -------- B
    |                      |
    3                      2
    |                      |
    C -------- 1 -------- D

The edge connecting A and B has weight 4.

The edge connecting B and D has weight 2.

Because the graph is undirected, an edge between A and B can be traversed in either direction.

### 2.2 Weighted Edges

An edge is represented by:

`(u, v, w)`

Where:

- `u` is the source vertex.
- `v` is the destination vertex.
- `w` is the edge weight.

Edge weights may represent:

- Network installation costs.
- Transportation distances.
- Communication infrastructure costs.
- Electrical cable installation costs.
- Infrastructure connection expenses.

Prim's algorithm minimizes the sum of the selected edge weights.

### 2.3 Spanning Tree

A spanning tree is a connected, acyclic subgraph containing every vertex of the original connected graph.

For a graph with `V` vertices:

`Number of spanning-tree edges = V - 1`

For example, a connected graph containing seven vertices must have six selected edges in its spanning tree.

A spanning tree cannot contain a cycle because a cycle would introduce an unnecessary connection.

### 2.4 Minimum Spanning Tree

A Minimum Spanning Tree is a spanning tree with the lowest possible total edge weight.

Its objective is:

`Minimize Σ w(u, v)`

Subject to:

- Every vertex is included.
- The resulting graph is connected.
- No cycles are present.
- Exactly `V - 1` edges are selected.

A graph may have multiple valid MSTs when several edges have equal weights.

Different implementations can therefore produce different edge selections while still producing the same minimum total weight.

## 3. Adjacency List Representation

An adjacency list stores the neighbors of each vertex together with their edge weights.

Example:

    A: (B,4), (C,3)
    B: (A,4), (C,1), (D,2)
    C: (A,3), (B,1), (D,4)
    D: (B,2), (C,4)

The undirected edge `(A,B,4)` appears in both adjacency lists.

This representation is efficient for sparse graphs.

If the graph contains `V` vertices and `E` undirected edges, adjacency-list storage requires:

`O(V + E)` space.

The implementations use:

| Language | Adjacency representation |
|---|---|
| Python | Dictionary containing lists |
| JavaScript | Map containing arrays |
| C++17 | Vector of adjacency vectors |
| Java 17 | Map containing lists of edge records |
| PostgreSQL | Relational edge table with source and destination identifiers |

The PostgreSQL representation stores each undirected edge once. The algorithm checks both endpoints when identifying neighboring vertices.

## 4. Priority Queue

A priority queue is the central data structure in Prim's algorithm.

It maintains candidate edges ordered by their weights.

The algorithm always selects the lowest-weight edge connecting an already visited vertex to an unvisited vertex.

A minimum priority queue supports:

| Operation | Complexity |
|---|---|
| Insert | `O(log E)` |
| Extract minimum | `O(log E)` |
| Check whether empty | `O(1)` |

The implementations use:

- Python: `heapq`
- JavaScript: A custom binary min-heap
- C++17: `std::priority_queue` with a custom comparator
- Java 17: `PriorityQueue`
- PostgreSQL: An indexed temporary candidate table ordered by weight and edge identifier

A priority queue is preferable to repeatedly scanning all graph edges because it efficiently identifies the next minimum candidate.

## 5. Prim's Algorithm

### 5.1 Core Mechanism

Prim's algorithm grows a tree incrementally.

It begins with one vertex and repeatedly selects the minimum-weight edge that connects the existing tree to an unvisited vertex.

The selected edge adds exactly one new vertex to the growing tree.

### 5.2 Execution Workflow

    Input: Weighted undirected graph
                    |
                    v
          Initialize visited set
                    |
                    v
             Select start vertex
                    |
                    v
       Insert neighboring edges into heap
                    |
                    v
          Extract minimum-weight edge
                    |
                    v
       Is destination already visited?
              /             \
            Yes              No
             |                |
             v                v
         Discard       Select the edge
                              |
                              v
                     Mark destination visited
                              |
                              v
                     Insert new candidates
                              |
                              v
                       Heap empty?
                         /     \
                       No       Yes
                       |         |
                       v         v
                    Repeat   Start another
                             component or finish
                              |
                              v
                     Minimum spanning forest

### 5.3 Detailed Steps

1. Initialize an empty visited set.
2. Select an unvisited vertex as the component root.
3. Mark the root as visited.
4. Insert all edges connecting the root to unvisited vertices into the priority queue.
5. Extract the minimum-weight candidate edge.
6. Check whether its destination has already been visited.
7. Discard the candidate if it would introduce a cycle.
8. Otherwise, select the edge and mark its destination as visited.
9. Insert the newly visited vertex's eligible neighboring edges.
10. Continue until no candidate edges remain.
11. If unvisited vertices remain, begin another component.
12. Return the selected edges and their total weight.

### 5.4 Greedy Selection

Prim's algorithm uses a greedy strategy.

At each iteration, it selects the minimum-weight edge crossing the boundary between the visited and unvisited vertex sets.

Let:

- `S` represent visited vertices.
- `V - S` represent unvisited vertices.

The selected edge is:

`min{w(u,v) | u ∈ S, v ∈ V-S}`

This selection is justified by the cut property of minimum spanning trees.

For any cut dividing a connected graph into two vertex sets, a minimum-weight edge crossing that cut is safe to include in at least one MST.

This property establishes the correctness of Prim's greedy selection.

## 6. Priority Queue Management and Lazy Deletion

A candidate edge may become unnecessary after another edge reaches its destination first.

For example:

    A -- 8 -- B
    A -- 3 -- C
    C -- 2 -- B

Initially, the priority queue may contain:

| Edge | Weight |
|---|---:|
| A-B | 8 |
| A-C | 3 |

The algorithm selects A-C first.

After visiting C, it inserts C-B with weight 2.

The next selected edge is C-B.

The earlier A-B candidate remains in the queue.

When it is eventually extracted, B is already visited, so the candidate is discarded.

This technique is called lazy deletion.

It avoids requiring an expensive decrease-key operation or maintaining explicit priority-queue handles.

The visited set is therefore essential to correctness.

## 7. Disconnected Graphs and Minimum Spanning Forests

A disconnected graph contains multiple connected components.

A conventional MST cannot connect these components because no connecting paths exist in the original graph.

The extended algorithm generates one MST for each connected component.

The resulting structure is a Minimum Spanning Forest.

For a graph containing:

- `V` total vertices.
- `C` connected components.

The minimum spanning forest contains:

`V - C` edges.

Example:

    Component 1: A -- B -- C

    Component 2: D -- E

    Component 3: F

This graph contains six vertices and three components.

Its minimum spanning forest contains:

`6 - 3 = 3 edges`

An isolated vertex forms a component containing one vertex and zero selected edges.

All five implementations support disconnected graphs.

## 8. Edge Cases

| Condition | Expected behavior |
|---|---|
| Empty graph | Return an empty forest |
| Single vertex | Return zero edges |
| Connected graph | Return exactly V-1 edges |
| Disconnected graph | Return a minimum spanning forest |
| Isolated vertex | Create a component with zero edges |
| Negative edge weight | Process normally |
| Zero edge weight | Process normally |
| Equal edge weights | Accept any valid minimum forest |
| Parallel edges | Select the minimum useful candidate |
| Self-loop | Reject during graph validation |
| Infinite weight | Reject |
| Invalid vertex | Reject or report validation failure |
| Stale heap candidate | Discard when its destination is visited |

Negative edge weights are valid because Prim's algorithm does not require nonnegative weights.

Unlike Dijkstra's shortest-path algorithm, Prim's algorithm does not calculate shortest paths from a source.

## 9. Prim's Algorithm vs. Dijkstra's Algorithm

These algorithms both use priority queues, but their objectives are different.

| Property | Prim's Algorithm | Dijkstra's Algorithm |
|---|---|---|
| Objective | Minimum spanning tree | Single-source shortest paths |
| Main output | Selected graph edges | Shortest distances and paths |
| Selection criterion | Minimum crossing edge | Minimum accumulated path distance |
| Edge relaxation | Not required | Required |
| Negative weights | Supported | Not supported by standard Dijkstra |
| Connectivity | Supports minimum spanning forests | Handles reachable vertices |
| Main application | Minimum-cost network construction | Shortest-route calculation |

A particularly important distinction is the priority value.

Prim's algorithm prioritizes the weight of an individual candidate edge.

Dijkstra's algorithm prioritizes the accumulated distance from the source.

These values must not be confused.

## 10. Complexity Analysis

Let:

- `V` = Number of vertices.
- `E` = Number of undirected edges.

### 10.1 Adjacency List and Binary Heap

Each vertex is incorporated into the forest once.

Each adjacency entry is examined when its vertex is visited.

Candidate edges are inserted into the heap and extracted at logarithmic cost.

The overall complexity is:

`O((V + E) log E)`

For a connected graph with at least two vertices, this is commonly expressed as:

`O(E log V)`

The space complexity is:

`O(V + E)`

This includes:

- Adjacency lists.
- Visited-state tracking.
- Priority queue.
- Selected MST edges.

### 10.2 Alternative Implementations

| Implementation | Priority queue approach |
|---|---|
| Python | Standard-library binary heap |
| JavaScript | Explicit binary min-heap |
| C++17 | STL binary heap |
| Java 17 | Java PriorityQueue |
| PostgreSQL | Indexed temporary candidate relation |

The PostgreSQL implementation is intentionally different from the in-memory implementations.

Its candidate extraction uses an indexed ordered query. A relational database also introduces transaction, indexing, execution-plan and temporary-storage considerations.

The database version is useful for understanding how graph processing can be implemented inside a relational system, although a specialized in-memory priority queue is generally preferable for large graph workloads.

## 11. Python Implementation

### File: `prim_algorithm.py`

The Python implementation emphasizes graph simulation and algorithm verification.

Important components:

| Component | Responsibility |
|---|---|
| `WeightedGraph` | Maintains the adjacency dictionary |
| `Edge` | Represents a selected weighted connection |
| `MSTResult` | Stores the minimum spanning forest |
| `PrimAlgorithm` | Executes Prim's algorithm |
| `verify_minimum_spanning_forest` | Checks structural correctness |
| `run_tests` | Validates edge cases |

Python's `heapq` provides an efficient minimum heap.

A counter is included in each priority queue entry to prevent Python from comparing arbitrary vertex objects when candidate weights are equal.

The verification procedure uses a Disjoint Set Union structure with path compression and union by rank.

This independently checks:

- Edge existence.
- Cycle prevention.
- Component count.
- Selected edge count.
- Total edge weight.

The implementation supports hashable vertex identifiers.

## 12. JavaScript Implementation

### File: `prim_algorithm.js`

The JavaScript implementation emphasizes asynchronous processing and event-driven execution.

Its binary min-heap is implemented directly instead of relying on an external package.

Important components:

| Component | Responsibility |
|---|---|
| `WeightedGraph` | Stores graph data in a Map |
| `MinPriorityQueue` | Implements binary heap operations |
| `PrimEngine` | Executes the algorithm |
| `EventEmitter` | Publishes execution events |
| `verifyForest` | Independently checks the result |

Three important events are exposed:

- `componentStarted`
- `edgeSelected`
- `completed`

These events separate algorithm execution from reporting and monitoring.

The implementation also yields periodically using `setImmediate` during large computations.

This allows other event-loop tasks to execute between batches of selected edges.

The yielding mechanism does not make the algorithm computationally parallel. It provides cooperative scheduling within Node.js.

The engine prevents overlapping executions on the same instance.

## 13. C++17 Implementation

### File: `prim_algorithm.cpp`

The C++ implementation emphasizes efficient memory representation and STL algorithms.

Important components:

| Component | Responsibility |
|---|---|
| `WeightedGraph` | Stores adjacency vectors |
| `Candidate` | Represents a priority-queue entry |
| `CandidateComparator` | Orders candidates by weight |
| `PrimEngine` | Calculates the minimum spanning forest |
| `DisjointSet` | Verifies acyclic structure |
| `MSTResult` | Stores the calculated result |

Vertex identifiers are mapped to integer indexes.

This avoids repeatedly comparing string identifiers during the main algorithm.

The adjacency structure uses:

`vector<vector<pair<int, double>>>`

The priority queue uses:

`std::priority_queue`

A custom comparator reverses the default ordering to provide minimum-weight extraction.

This design provides efficient graph traversal without external dependencies.

## 14. Java 17 Implementation

### File: `PrimAlgorithm.java`

The Java implementation emphasizes enterprise-oriented domain modeling and controlled execution.

It uses Java 17 records to represent immutable domain values.

Important components:

| Component | Responsibility |
|---|---|
| `Vertex` | Validates vertex identifiers |
| `WeightedEdge` | Represents and validates an edge |
| `SelectedEdge` | Represents a selected connection |
| `MSTResult` | Stores an immutable result |
| `WeightedGraph` | Manages graph relationships |
| `PrimService` | Controls algorithm execution |
| `ForestVerifier` | Checks result integrity |
| `ExecutionStatus` | Tracks execution state |

The execution state follows:

`CREATED → RUNNING → COMPLETED`

A failed execution transitions to:

`FAILED`

An `AtomicBoolean` prevents simultaneous execution through the same service instance.

The graph is converted into an immutable snapshot before algorithm execution.

This prevents changes to the graph's internal adjacency lists from affecting an ongoing calculation.

The result uses immutable list copies to protect selected edges from external modification.

## 15. PostgreSQL Implementation

### File: `prim_algorithm.sql`

The SQL implementation models graph processing using relational database objects.

It creates a dedicated schema named `prim_lab`.

### 15.1 Database Architecture

| Database object | Purpose |
|---|---|
| `graph` | Stores graph metadata |
| `vertex` | Stores graph vertices |
| `graph_edge` | Stores weighted undirected edges |
| `mst_execution` | Tracks algorithm executions |
| `mst_result_edge` | Stores selected MST edges |
| `graph_statistics` | Provides graph-level reporting |
| `calculate_prim_msf` | Executes Prim's algorithm |
| `get_prim_result` | Retrieves selected edges |
| `validate_mst_execution` | Validates stored results |
| `validate_graph_edge` | Enforces edge validation |

### 15.2 Relational Graph Modeling

The database uses separate tables for vertices and edges.

Each edge references two vertices belonging to the same graph.

Composite foreign keys enforce this relationship.

The endpoint ordering constraint:

`source_vertex_id < destination_vertex_id`

provides a canonical representation of undirected edges.

An undirected edge is stored once rather than being duplicated in both directions.

Parallel edges remain permitted.

### 15.3 Database Priority Queue

The SQL implementation uses a temporary table named `prim_candidate_queue`.

Its important fields include:

- `edge_id`
- `source_vertex_id`
- `destination_vertex_id`
- `weight`
- `processed`

The minimum candidate is selected using:

`ORDER BY weight, edge_id LIMIT 1`

An index on weight and edge identifier supports ordered candidate retrieval.

The `processed` field provides lazy deletion and prevents previously extracted candidates from being selected again.

### 15.4 Transaction and Execution Management

Each algorithm execution receives an execution identifier.

The execution table records:

- Graph identifier.
- Execution status.
- Total weight.
- Component count.
- Vertex count.
- Selected edge count.
- Start timestamp.
- Completion timestamp.

The algorithm records successful execution as `COMPLETED`.

An exception marks the execution as `FAILED` before propagating the error.

The selected edges and execution metadata are persisted transactionally.

### 15.5 Database Reporting

The SQL script includes queries for:

- Graph statistics.
- Execution history.
- Selected minimum spanning forest edges.
- Component-level aggregation.
- Minimum and maximum selected weights.
- Total spanning forest weight.
- Execution validation.
- Eligibility reporting.

The result-validation function verifies the fundamental forest relationship:

`Selected edges = Vertices - Components`

It also compares the calculated edge-weight sum with the stored execution total.

## 16. Implementation Comparison

| Feature | Python | JavaScript | C++17 | Java 17 | PostgreSQL |
|---|---|---|---|---|---|
| Adjacency lists | Yes | Yes | Yes | Yes | Relational |
| Priority queue | heapq | Custom heap | STL heap | PriorityQueue | Indexed table |
| Negative weights | Yes | Yes | Yes | Yes | Yes |
| Parallel edges | Yes | Yes | Yes | Yes | Yes |
| Disconnected graphs | Yes | Yes | Yes | Yes | Yes |
| Forest verification | DSU | DSU | DSU | DSU | Relational checks |
| Event-driven execution | No | Yes | No | No | No |
| Explicit execution state | Result | Engine | Result | Service | Database |
| External dependencies | None | None | None | None | None |

## 17. Practical Applications

### 17.1 Telecommunications Infrastructure

A telecommunications organization may need to connect several network locations while minimizing cable installation costs.

Vertices represent network locations.

Edges represent possible cable connections.

Weights represent estimated installation expenses.

Prim's algorithm identifies a minimum-cost connection structure.

### 17.2 Electrical Distribution Networks

Vertices can represent substations.

Edges can represent possible transmission connections.

Weights can represent construction or installation costs.

A minimum spanning tree provides a minimum-cost connection structure under the simplified assumption that every selected connection is feasible and all costs are additive.

Actual electrical network planning must also consider capacity, redundancy, voltage constraints and operational safety.

### 17.3 Transportation Infrastructure

Vertices can represent cities or transport stations.

Edges represent possible direct connections.

Weights represent construction costs or distances.

A minimum spanning tree identifies a low-cost connected network.

It does not necessarily minimize the travel distance between every pair of locations.

### 17.4 Cloud Infrastructure

Vertices can represent data centers or infrastructure regions.

Edges represent possible network connections.

Weights can represent estimated connectivity costs.

The resulting minimum spanning tree provides a basic cost-minimization model.

Real cloud network design must also account for latency, bandwidth, availability and redundancy.

## 18. Limitations and Engineering Considerations

### 18.1 Minimum Cost Does Not Guarantee Reliability

An MST minimizes total selected edge weight.

It does not automatically provide:

- Fault tolerance.
- Redundant communication paths.
- High availability.
- Maximum bandwidth.
- Minimum latency.

An MST contains no cycles, so removing a selected edge can disconnect its component.

### 18.2 Static Graph Assumption

The implementations calculate a forest using a snapshot of the graph.

When edge weights or connections change, the MST may no longer be optimal.

A new calculation may be required.

### 18.3 Floating-Point Precision

Python, JavaScript, C++ and Java implementations use floating-point weights.

Floating-point arithmetic can introduce rounding errors.

The verification routines therefore use a tolerance when comparing accumulated totals.

PostgreSQL uses `NUMERIC` to provide decimal arithmetic for stored weights and totals.

### 18.4 Memory Consumption

Adjacency lists and priority queues require additional memory.

For extremely large graphs, candidate queues can contain many entries.

Lazy deletion simplifies implementation but may increase temporary queue size.

### 18.5 Concurrency

Graph modification during execution can invalidate algorithm assumptions.

The Java implementation uses a graph snapshot.

The JavaScript implementation prevents concurrent execution through the same engine instance.

The Python and C++ examples assume that graph data remains unchanged during calculation.

The PostgreSQL implementation uses database transactions and session-specific temporary tables. Concurrent modifications still require an appropriate transaction-isolation policy when the algorithm must operate on a consistent graph snapshot.

### 18.6 Verification Limitations

The included verification routines check structural properties and selected-edge validity.

They do not independently prove that the selected forest has globally minimum weight.

The mathematical correctness of Prim's algorithm follows from the cut property.

An independent optimality check would require comparing against another MST algorithm, such as Kruskal's algorithm, or verifying the relevant cycle and cut optimality conditions.

## 19. Execution Commands

| Implementation | Execution |
|---|---|
| Python | `python prim_algorithm.py` |
| JavaScript | `node prim_algorithm.js` |
| C++17 | `g++ -std=c++17 -O2 -Wall -Wextra -pedantic prim_algorithm.cpp -o prim_algorithm` |
| C++17 execution | `./prim_algorithm` |
| Java 17 compilation | `javac PrimAlgorithm.java` |
| Java 17 execution | `java PrimAlgorithm` |
| PostgreSQL | Execute `prim_algorithm.sql` using a PostgreSQL SQL client |

The PostgreSQL implementation requires PostgreSQL 15 or later.

The other four implementations use their respective language standard libraries without third-party dependencies.

## 20. Expected Results

For the main sample graph, the vertices are:

`A, B, C, D, E, F, G, H, I, ISOLATED`

The graph contains:

- 10 vertices.
- 12 edges.
- 3 connected components.

The minimum spanning forest selects seven edges.

One valid result is:

| Selected edge | Weight |
|---|---:|
| A-C | 3 |
| C-B | 1 |
| B-D | 2 |
| D-E | 2 |
| E-F | 1 |
| F-G | 2 |
| H-I | 6 |
| **Total** | **17** |

The isolated vertex forms the third component.

The resulting forest has:

`10 - 3 = 7 edges`

Expected validation conditions:

| Validation | Expected result |
|---|---|
| Selected edge count | 7 |
| Total weight | 17 |
| Connected components | 3 |
| Forest structure | Valid |
| Cycle detection | No cycles |
| Isolated vertex | Preserved |
| Negative-weight test | Passed |
| Parallel-edge test | Passed |
| Invalid self-loop | Rejected |

The exact selected edges may differ when multiple minimum-weight alternatives exist. The minimum total weight and structural requirements must remain valid. 
