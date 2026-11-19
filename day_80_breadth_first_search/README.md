# Breadth-First Search (BFS)

## 1. Introduction

Breadth-First Search is a graph traversal algorithm that explores vertices in increasing order of their distance from a starting vertex.

BFS visits all immediately connected vertices before exploring vertices that are farther away. It uses a First-In, First-Out (FIFO) queue to maintain the order in which vertices are processed.

BFS is particularly useful for:

- Traversing graphs systematically.
- Finding shortest paths in unweighted graphs.
- Calculating minimum distances between vertices.
- Identifying connected components.
- Detecting reachability.
- Exploring networks and relationships.
- Performing level-order traversal of trees.

The implementations in this project use an undirected, unweighted graph.

## 2. Graph Fundamentals

A graph consists of two fundamental elements:

- **Vertex:** An individual entity or location.
- **Edge:** A connection between two vertices.

A graph can be represented mathematically as:

\[
G=(V,E)
\]

Where:

- \(V\) is the set of vertices.
- \(E\) is the set of edges.

Consider the following graph:

    A ----- B ----- D
    |       |
    C       E ----- F

    G ----- H

    I

Its vertices are:

\[
V=\{A,B,C,D,E,F,G,H,I\}
\]

Its undirected edges are:

\[
E=\{
(A,B),(A,C),(B,D),(B,E),
(C,F),(E,F),(G,H)
\}
\]

Vertices A through F form one connected component. G and H form another. I is an isolated vertex.

### 2.1 Directed and Undirected Graphs

An undirected graph represents connections without a specified direction.

For example:

\[
(A,B)\equiv(B,A)
\]

A directed graph represents connections with a specified direction.

For example:

\[
A\rightarrow B
\]

This implementation uses undirected graphs. Each edge is represented in both adjacency directions during traversal.

### 2.2 Weighted and Unweighted Graphs

An unweighted graph treats every edge as having equal cost.

A weighted graph associates a numerical value with each edge.

BFS guarantees a minimum-edge-count path in an unweighted graph. It does not generally guarantee the minimum total weight in a weighted graph.

Algorithms designed for weighted shortest paths include Dijkstra's algorithm and Bellman-Ford.

## 3. Breadth-First Search Mechanics

BFS explores a graph in successive distance levels.

The central data structures are:

| Data structure | Purpose |
|---|---|
| Queue | Stores vertices waiting to be processed |
| Visited set | Prevents repeated exploration |
| Adjacency list | Stores vertex connections |
| Parent map | Reconstructs shortest paths |
| Distance map | Stores minimum edge distances |

### 3.1 Queue-Based Traversal

A queue follows FIFO ordering.

The two principal operations are:

- Enqueue: Insert an element at the rear.
- Dequeue: Remove an element from the front.

For a starting vertex A, the traversal proceeds as follows:

**Initial state**

    Queue: [A]
    Visited: {A}

**Process A**

A is connected to B and C.

    Queue: [B, C]
    Visited: {A, B, C}

**Process B**

B introduces D and E.

    Queue: [C, D, E]
    Visited: {A, B, C, D, E}

**Process C**

C introduces F.

    Queue: [D, E, F]
    Visited: {A, B, C, D, E, F}

**Process D**

No new vertices are discovered.

    Queue: [E, F]

**Process E**

F has already been discovered.

    Queue: [F]

**Process F**

No new vertices are discovered.

    Queue: []

The resulting traversal is:

\[
A,B,C,D,E,F
\]

The exact traversal order can depend on adjacency-list ordering. The implementations sort neighboring vertices to produce deterministic results.

### 3.2 The Visited Set

The visited set prevents repeated processing.

This is essential because graphs can contain:

- Cycles.
- Multiple paths to the same vertex.
- Self-loops in general graph models.
- Repeated connections.

A vertex should be marked visited when it is inserted into the queue, not when it is removed.

This ensures that the same vertex is not inserted repeatedly through different neighbors.

The visited set also guarantees termination for finite graphs.

### 3.3 BFS Algorithm

The traversal follows these operations:

1. Validate the starting vertex.
2. Mark the starting vertex as visited.
3. Insert it into the queue.
4. Remove the front vertex.
5. Process its unvisited neighbors.
6. Mark newly discovered neighbors as visited.
7. Insert them into the queue.
8. Repeat until the queue becomes empty.

A completed traversal includes every vertex reachable from the starting vertex.

It does not necessarily include every vertex in a disconnected graph.

## 4. Shortest Path in an Unweighted Graph

BFS finds a shortest path in an unweighted graph because vertices are explored in increasing order of their distance from the source.

The first discovery of a vertex establishes its minimum edge distance.

For a starting vertex \(s\):

\[
d(s,s)=0
\]

For an adjacent vertex \(v\):

\[
d(s,v)=d(s,u)+1
\]

Where \(u\) is the vertex from which \(v\) is first discovered.

### 4.1 Distance Example

For the sample graph:

| Vertex | Minimum distance from A |
|---|---:|
| A | 0 |
| B | 1 |
| C | 1 |
| D | 2 |
| E | 2 |
| F | 2 |

The shortest path from A to F is:

\[
A\rightarrow C\rightarrow F
\]

Its distance is:

\[
d(A,F)=2
\]

There are two edges in this path.

Another valid shortest path is:

\[
A\rightarrow B\rightarrow E\rightarrow F
\]

This path has three edges and is therefore not optimal.

### 4.2 Parent Tracking

To reconstruct the actual shortest path, BFS stores the parent of every discovered vertex.

For example:

| Vertex | Parent |
|---|---|
| A | NULL |
| B | A |
| C | A |
| D | B |
| E | B |
| F | C |

Starting at F, following the parent relationships produces:

    F <- C <- A

Reversing the sequence produces:

    A -> C -> F

Parent tracking requires additional memory proportional to the number of discovered vertices.

### 4.3 Special Cases

| Case | Expected behavior |
|---|---|
| Source equals destination | Return the source with distance zero |
| Destination unreachable | Return no path |
| Unknown source | Reject the request |
| Unknown destination | Reject the request |
| Isolated starting vertex | Return only that vertex |
| Empty graph | Contains no reachable vertices |
| Cyclic graph | Visit each reachable vertex once |

## 5. Connected Components

A connected component is a maximal set of vertices in which every vertex is reachable from every other vertex.

A disconnected graph contains multiple connected components.

For the sample graph:

    Component 1: A, B, C, D, E, F

    Component 2: G, H

    Component 3: I

Therefore:

\[
C(G)=3
\]

A connected graph has exactly one connected component.

An isolated vertex is itself a connected component.

### 5.1 Finding Connected Components Using BFS

The algorithm uses one global visited set.

1. Examine every vertex.
2. Skip vertices already visited.
3. Start a BFS from each unvisited vertex.
4. Collect all vertices discovered by that BFS.
5. Store the collected vertices as one component.
6. Continue until every vertex has been examined.

The complexity remains:

\[
O(V+E)
\]

Each vertex is discovered once, and each undirected edge is examined at most twice using adjacency lists.

## 6. Python Implementation

**File:** `bfs.py`

The Python implementation uses a `Graph` dataclass with dictionary-based adjacency sets.

### Implemented mechanisms

| Method | Responsibility |
|---|---|
| `add_vertex()` | Creates a vertex |
| `add_edge()` | Adds an undirected connection |
| `remove_edge()` | Removes a connection |
| `remove_vertex()` | Removes a vertex and its connections |
| `bfs()` | Performs queue-based traversal |
| `bfs_levels()` | Calculates minimum distances |
| `shortest_path()` | Reconstructs a shortest path |
| `connected_components()` | Identifies disconnected groups |
| `is_connected()` | Evaluates graph connectivity |
| `display()` | Displays the adjacency representation |

Python's `collections.deque` provides efficient insertion and removal at opposite ends.

Dictionary and set membership operations provide efficient average-case lookup.

The implementation also includes:

- Input validation.
- Unknown-vertex handling.
- Deterministic neighbor ordering.
- Self-contained sample data.
- Assertions for correctness.
- Empty and single-vertex graph handling.

The use of a parent dictionary avoids storing complete candidate paths in every queue entry.

## 7. JavaScript Implementation

**File:** `bfs.js`

The JavaScript implementation uses Node.js standard-library functionality and an event-driven graph model.

### Implemented mechanisms

| Mechanism | Responsibility |
|---|---|
| `Map` | Stores adjacency relationships |
| `Set` | Tracks discovered vertices |
| Array queue | Stores pending vertices |
| Queue head index | Avoids repeated array shifting |
| `EventEmitter` | Publishes graph and traversal events |
| `Promise` and `async` | Supports asynchronous traversal |
| `AbortController` | Supports cancellation |
| `assert` | Verifies algorithm correctness |

### Event-driven traversal

The graph emits events for:

- Vertex creation.
- Edge creation.
- Edge removal.
- Traversal initiation.
- Vertex discovery.
- Vertex visitation.
- Traversal completion.

This separates traversal logic from monitoring logic.

An application can subscribe to traversal events without changing the BFS algorithm.

### Asynchronous processing

The `bfsAsync()` method supports an asynchronous callback for each visited vertex.

This is useful when processing involves asynchronous operations such as database lookups or remote service requests.

The traversal checks an optional cancellation signal between vertices.

The asynchronous method is not a parallel BFS implementation. It processes vertices sequentially while allowing asynchronous work during each visit.

### Queue optimization

JavaScript arrays support efficient indexed access.

Instead of repeatedly calling `shift()`, which moves remaining array elements, the implementation maintains a queue head index.

This preserves efficient queue processing.

## 8. C++17 Implementation

**File:** `bfs.cpp`

The C++ implementation emphasizes explicit graph modeling and STL-based data management.

### Data structures

| Structure | Purpose |
|---|---|
| `map` | Stores the adjacency list |
| `set` | Maintains unique sorted neighbors |
| `queue` | Maintains FIFO processing |
| `vector` | Stores traversal and path results |
| `map` | Stores distances and parent relationships |

### Important design decisions

The adjacency representation uses:

`map<string, set<string>>`

This provides:

- Unique vertex names.
- Unique edges.
- Deterministic neighbor ordering.
- Efficient membership checks.

The `Graph` class encapsulates graph operations.

Private validation prevents algorithms from operating on nonexistent vertices.

The implementation includes vertex and edge removal, BFS traversal, distance calculation, shortest-path reconstruction, connected-component discovery, and connectivity testing.

C++ assertions verify important expected results.

The program uses exceptions for invalid input and catches application-level failures in `main()`.

## 9. Java 17 Implementation

**File:** `BreadthFirstSearch.java`

The Java implementation uses an enterprise-oriented service structure.

### Domain types

| Type | Purpose |
|---|---|
| `Edge` record | Represents an immutable graph connection |
| `PathResult` record | Represents a shortest path and its distance |
| `GraphStatistics` record | Represents graph-level statistics |
| `GraphException` | Represents invalid graph operations |
| `Graph` | Owns graph state and traversal operations |
| `GraphService` | Provides higher-level graph operations |

### Immutable results

Traversal results use `List.copyOf()`.

Distance results are returned through unmodifiable maps.

This prevents callers from modifying internal traversal results.

### Snapshot-based processing

The graph creates an immutable adjacency snapshot before running traversal operations.

This gives each traversal a consistent view of the graph even when another operation modifies the underlying graph.

The graph's synchronized mutation and snapshot methods protect graph-state access within a single Java process.

For larger concurrent systems, additional considerations include snapshot versioning, graph partitioning, and read/write synchronization policies.

### Service layer

`GraphService` separates application-level operations from graph implementation details.

It provides route processing and connected-component reporting.

This separation allows graph algorithms to be reused by different application services.

## 10. PostgreSQL Implementation

**File:** `bfs.sql`

The PostgreSQL implementation models a persistent graph using relational tables.

### Database structure

| Database object | Responsibility |
|---|---|
| `vertices` | Stores graph vertices |
| `edges` | Stores undirected connections |
| `graph_adjacency` | Exposes both adjacency directions |
| `connected_components` | Calculates component membership |
| `graph_statistics` | Reports graph-level metrics |
| `normalize_edge()` | Validates and normalizes edges |
| `shortest_path()` | Calculates a minimum-edge path |

### Edge normalization

An undirected edge between vertices A and B is stored in one normalized form.

For example:

\[
(A,B)=(B,A)
\]

The database normalizes the endpoint identifiers into ascending order.

A unique constraint prevents duplicate undirected edges.

A check constraint rejects self-loops.

Foreign keys prevent references to nonexistent vertices.

### Adjacency view

The physical `edges` table stores each connection once.

The `graph_adjacency` view exposes each edge in both directions using `UNION ALL`.

For example, an edge between A and B produces:

| vertex | neighbor |
|---|---|
| A | B |
| B | A |

This allows recursive graph queries to process undirected connections.

### Recursive CTEs

PostgreSQL recursive common table expressions support repeated graph exploration.

The shortest-path function recursively explores candidate simple paths and selects the candidate with the smallest number of edges.

The connected-components view computes reachability from every vertex.

The minimum reachable vertex identifier is used as a stable component identifier for the current graph state.

### Database limitations

The recursive shortest-path function enumerates simple paths rather than implementing a strict queue-based BFS frontier.

This produces correct minimum-edge results for the modeled finite graph but can become expensive because the number of simple paths can grow exponentially.

The recursive distance example has the same limitation.

For large production graphs, a procedural BFS implementation using temporary frontier and visited tables, or application-side queue processing, is preferable.

The connected-components view also recalculates reachability and can be expensive on large graphs.

Materialization or incremental component maintenance may be appropriate for frequently queried, relatively stable graphs.

## 11. Complexity Analysis

Let:

- \(V\) = number of vertices.
- \(E\) = number of edges.

For adjacency-list representations:

| Operation | Time complexity |
|---|---|
| Add vertex | \(O(1)\) average in hash-based structures |
| Add edge | \(O(1)\) average with hash-based adjacency |
| BFS traversal | \(O(V+E)\) |
| BFS distance calculation | \(O(V+E)\) |
| Shortest-path search | \(O(V+E)\) |
| Path reconstruction | \(O(V)\) |
| Connected components | \(O(V+E)\) |
| Connectivity test | \(O(V+E)\) |

The implementations using sorted maps and sets have additional logarithmic insertion and lookup costs.

Their traversal complexity can be expressed more precisely as:

\[
O(V\log V+E\log V)
\]

for ordered adjacency structures.

### Space complexity

The adjacency list requires:

\[
O(V+E)
\]

BFS requires additional space for:

- Visited vertices.
- Queue entries.
- Parent relationships.
- Distances.

The total auxiliary traversal space is:

\[
O(V)
\]

Therefore, total graph storage and traversal memory are:

\[
O(V+E)
\]

## 12. Adjacency List Versus Adjacency Matrix

Two common graph representations are adjacency lists and adjacency matrices.

| Characteristic | Adjacency list | Adjacency matrix |
|---|---|---|
| Storage | \(O(V+E)\) | \(O(V^2)\) |
| Check edge | Depends on adjacency structure | \(O(1)\) |
| Find neighbors | Proportional to degree | \(O(V)\) |
| Sparse graphs | Efficient | Usually inefficient |
| Dense graphs | May have more overhead | Can be appropriate |

An adjacency list is suitable for this project because the example graph is sparse.

A graph is sparse when the number of edges is relatively small compared with the maximum possible number of edges.

For an undirected simple graph, the maximum number of edges is:

\[
\frac{V(V-1)}{2}
\]

## 13. Practical Applications

BFS is useful in several computing domains.

| Application | BFS usage |
|---|---|
| Social networks | Finding connections within a minimum number of relationships |
| Computer networks | Exploring reachable devices |
| GPS-style unweighted networks | Finding minimum-edge routes |
| Web crawling | Exploring links level by level |
| Recommendation systems | Exploring relationship neighborhoods |
| Dependency analysis | Examining reachable dependencies |
| Network security | Discovering connected network segments |
| Games | Exploring movement states with equal transition costs |
| Distributed systems | Discovering reachable services |

The algorithm is particularly suitable when every transition has equal cost.

## 14. Common Implementation Errors

| Error | Consequence | Correct approach |
|---|---|---|
| Not using a queue | Incorrect exploration order | Use FIFO processing |
| Marking visited too late | Duplicate queue entries | Mark when enqueuing |
| Ignoring disconnected vertices | Incomplete component discovery | Start BFS from every unvisited vertex |
| Forgetting parent tracking | Cannot reconstruct a path | Store each discovered vertex's parent |
| Assuming every destination is reachable | Invalid path reconstruction | Handle unreachable results |
| Using BFS for arbitrary weighted graphs | Potentially incorrect shortest path | Use an appropriate weighted shortest-path algorithm |
| Repeatedly shifting a JavaScript array | Avoidable queue-processing overhead | Maintain a queue head index |
| Storing duplicate undirected edges | Inconsistent graph representation | Normalize endpoint ordering |

## 15. Testing and Validation

The sample implementations use the same graph structure to verify comparable behavior.

| Test case | Expected result |
|---|---|
| BFS starting at A | A, B, C, D, E, F |
| Distance from A to F | 2 |
| Shortest path A to F | A, C, F |
| Shortest path A to H | Unreachable |
| Shortest path A to A | A |
| Connected components | 3 |
| Isolated vertex I | One-vertex component |
| Unknown starting vertex | Validation error |
| Single-vertex graph | One visited vertex |
| Empty graph | No components |

The graph contains a cycle through A, B, E, F, and C. This helps verify that visited-state management prevents infinite traversal.

## 16. Execution

### Python

File: `bfs.py`

Run:

`python bfs.py`

### JavaScript

File: `bfs.js`

Run:

`node bfs.js`

### C++17

File: `bfs.cpp`

Compile:

`g++ -std=c++17 -O2 -Wall -Wextra -pedantic bfs.cpp -o bfs`

Run:

`./bfs`

On Windows:

`bfs.exe`

### Java 17

File: `BreadthFirstSearch.java`

Compile:

`javac BreadthFirstSearch.java`

Run:

`java -ea BreadthFirstSearch`

The `-ea` option enables Java assertions.

### PostgreSQL

File: `bfs.sql`

Execute:

`psql -U postgres -d postgres -f bfs.sql`

The script creates the `bfs_lab` schema, populates the sample graph, defines the graph functions and views, performs queries, demonstrates transaction handling, and commits the changes.

The SQL script requires permission to create schemas and database objects.

## 17. Learning Outcomes

The five implementations demonstrate the same graph problem through different engineering approaches:

| Language | Main engineering perspective |
|---|---|
| Python | Concise graph modeling and algorithm experimentation |
| JavaScript | Event-driven traversal and asynchronous processing |
| C++17 | STL-based graph representation and efficient state management |
| Java 17 | Immutable results, domain types, and service separation |
| PostgreSQL | Relational graph modeling and recursive queries |

The central algorithmic principle remains consistent:

**BFS processes vertices in non-decreasing order of their distance from the starting vertex by using a FIFO queue.**

This property makes BFS a fundamental algorithm for graph traversal, unweighted shortest-path discovery, and connected-component identification.
