# Topological Sorting and Dependency Resolution

## 1. Introduction

Topological sorting is an algorithm for arranging the vertices of a directed graph into a linear sequence that respects all directed edges.

It is applicable to problems in which certain operations must occur before other operations.

Examples include:

- Software compilation and build pipelines.
- Package installation and dependency management.
- Database migration execution.
- Project scheduling.
- Course prerequisite planning.
- Data processing pipelines.
- Deployment orchestration.
- Workflow automation.

The fundamental data structure is a Directed Acyclic Graph (DAG).

A DAG represents dependencies without permitting circular relationships.

If task A must finish before task B starts, the graph contains:

`A -> B`

A valid topological ordering must place A before B.

The graph can have several valid topological orderings. The algorithm determines a valid ordering, not necessarily a unique ordering.

## 2. Directed Graph Fundamentals

A directed graph is represented mathematically as:

\[
G = (V,E)
\]

Where:

- \(V\) is the set of vertices.
- \(E\) is the set of directed edges.

For a dependency graph:

- Vertices represent tasks.
- Edges represent prerequisite relationships.
- An incoming edge represents a prerequisite.
- An outgoing edge represents a dependent task.

Consider:

    A ----> C ----> E
     \      ^
      \     |
       ---> D

    B ----> D

The edges express:

- A must execute before C.
- A must execute before D.
- B must execute before D.
- C must execute before E.
- D must execute before E.

A valid ordering is:

`A, B, C, D, E`

Another valid ordering is:

`B, A, D, C, E`

Both satisfy every dependency.

The ordering is not unique because A and B are independent, and C and D can be processed in different valid sequences.

### 2.1 Directed Acyclic Graphs

A Directed Acyclic Graph contains no directed cycle.

A directed cycle exists when following directed edges eventually returns to an already visited vertex.

For example:

    A -> B -> C -> A

This graph is cyclic.

It represents contradictory prerequisites:

- A requires C.
- C requires B.
- B requires A.

No vertex can be placed first without violating a dependency.

Therefore, a topological ordering does not exist.

A directed graph has a topological ordering if and only if it is acyclic.

### 2.2 Adjacency List Representation

An adjacency list stores the outgoing neighbors of each vertex.

For example:

| Vertex | Outgoing neighbors |
|---|---|
| A | B, C |
| B | D |
| C | D |
| D | None |

Representation:

- Python: dictionaries containing sets.
- JavaScript: `Map` containing `Set` objects.
- C++: ordered maps containing sets.
- Java: maps containing sets.
- PostgreSQL: relational dependency records.

The adjacency-list representation requires:

\[
O(V+E)
\]

Space.

It is particularly suitable for sparse dependency graphs.

An adjacency matrix requires:

\[
O(V^2)
\]

Space, regardless of the number of actual edges.

## 3. Topological Sorting

Topological sorting produces a linear ordering of vertices that satisfies all directed edges.

For every edge:

\[
u \rightarrow v
\]

The resulting sequence must satisfy:

\[
position(u) < position(v)
\]

Two principal algorithms are implemented in these deliverables:

1. Depth-First Search (DFS).
2. Kahn's Algorithm.

They solve the same ordering problem through different mechanisms.

## 4. DFS-Based Topological Sorting

Depth-First Search explores a vertex and recursively visits its unvisited outgoing neighbors.

A vertex is added to the resulting ordering only after all its outgoing neighbors have been processed.

This is called postorder processing.

The resulting list is reversed to obtain a valid topological ordering.

### 4.1 Vertex States

Three states are required:

| State | Meaning |
|---|---|
| WHITE | Not visited |
| GRAY | Currently being explored |
| BLACK | Completely processed |

The states identify whether an edge indicates a cycle.

**WHITE vertex**

The vertex has not been visited. DFS can safely explore it.

**GRAY vertex**

The vertex belongs to the active recursion path.

An edge to a GRAY vertex indicates a directed cycle.

**BLACK vertex**

The vertex has already been completely processed.

Revisiting a BLACK vertex does not indicate a cycle.

### 4.2 Algorithm

1. Initialize all vertices as WHITE.
2. Select an unvisited vertex.
3. Mark it GRAY.
4. Explore its outgoing neighbors.
5. Detect a cycle if a neighbor is GRAY.
6. Recursively explore WHITE neighbors.
7. Mark the current vertex BLACK.
8. Append the vertex to the result.
9. Reverse the result after processing all vertices.

### 4.3 Complexity

| Measurement | Complexity |
|---|---|
| Time | \(O(V+E)\) |
| Auxiliary space | \(O(V)\) |
| Graph storage | \(O(V+E)\) |

Every vertex is visited once and every edge is examined once.

The recursion stack can become large for deeply connected dependency chains. Iterative DFS is preferable when recursion depth is a practical concern.

### 4.4 Implementation Details

The Python implementation maintains a recursion path and reports the actual cycle.

The JavaScript implementation uses a state map and an active path.

The C++17 implementation uses strongly typed vertex states and recursive traversal.

The Java implementation uses explicit domain-level exceptions to distinguish dependency failures from ordinary validation errors.

DFS is useful when traversal and cycle-path information are important.

## 5. Kahn's Algorithm

Kahn's algorithm uses vertex indegrees rather than recursive traversal.

The indegree of a vertex is the number of incoming edges.

\[
indegree(v) =
|\{u : (u,v)\in E\}|
\]

A vertex with indegree zero has no remaining prerequisites.

It can therefore be placed in the next position of a valid topological ordering.

### 5.1 Algorithm

1. Calculate the indegree of every vertex.
2. Identify all vertices having indegree zero.
3. Insert those vertices into a queue or priority queue.
4. Remove one available vertex.
5. Append it to the ordering.
6. Decrease the indegree of each outgoing neighbor.
7. Insert a neighbor when its indegree becomes zero.
8. Repeat until no available vertices remain.
9. Compare the number of processed vertices with the total vertex count.

If every vertex is processed, the graph is acyclic.

If some vertices remain unresolved, the graph contains a directed cycle.

### 5.2 Example

Consider:

    SOURCE -> VALIDATE -> COMPILE
                              |
                         +----+----+
                         |         |
                        UNIT    SECURITY
                         |         |
                         +----+----+
                              |
                           PACKAGE
                              |
                         INTEGRATION
                              |
                            DEPLOY

Initially:

| Task | Indegree |
|---|---:|
| SOURCE | 0 |
| VALIDATE | 1 |
| COMPILE | 1 |
| UNIT | 1 |
| SECURITY | 1 |
| PACKAGE | 2 |
| INTEGRATION | 1 |
| DEPLOY | 1 |

SOURCE is initially available.

After processing SOURCE, VALIDATE becomes available.

After processing VALIDATE, COMPILE becomes available.

After processing COMPILE, both UNIT and SECURITY become available.

PACKAGE becomes available only after both have been processed.

This illustrates how indegrees enforce prerequisite completion.

### 5.3 Complexity

| Measurement | Complexity |
|---|---|
| Time using a FIFO queue | \(O(V+E)\) |
| Auxiliary space | \(O(V)\) |
| Graph storage | \(O(V+E)\) |

The implementation uses a queue for the standard linear-time algorithm.

The C++17, Java, and JavaScript implementations also demonstrate deterministic selection through ordered structures or priority queues. This changes the worst-case scheduling overhead to:

\[
O((V+E)\log V)
\]

when priority-queue operations are used.

The Python implementation uses a deque and sorted neighbor traversal.

### 5.4 Why Kahn's Algorithm Detects Cycles

Suppose a graph contains a directed cycle.

Every vertex in that cycle has at least one incoming edge from another vertex in the cycle.

Consequently, none of those vertices can become available while the cycle remains intact.

Kahn's algorithm eventually stops with unresolved vertices.

Therefore:

\[
processed\_vertices < |V|
\]

indicates that no complete topological ordering exists.

An important distinction is that unresolved vertices can include vertices downstream of a cycle, not only vertices directly participating in it.

DFS is useful for identifying an actual cycle path, while Kahn's algorithm provides a straightforward completion test.

## 6. Comparing DFS and Kahn's Algorithm

| Property | DFS | Kahn |
|---|---|---|
| Primary mechanism | Recursive traversal | Indegree reduction |
| Cycle detection | GRAY vertex | Unprocessed vertices |
| Ordering construction | Reverse postorder | Repeated zero-indegree selection |
| Standard time complexity | \(O(V+E)\) | \(O(V+E)\) |
| Main auxiliary structure | Recursion stack | Queue and indegree map |
| Natural parallel scheduling | Requires additional analysis | Exposes available tasks |
| Cycle-path reporting | Straightforward | Requires additional traversal |

Neither algorithm is universally superior.

DFS provides a natural way to reconstruct a cycle.

Kahn's algorithm naturally supports dependency scheduling because each newly available vertex becomes eligible for processing.

## 7. Dependency Resolution

Dependency resolution identifies which operations must complete before another operation can execute.

A software build system is a practical example.

Consider the following tasks:

| Task | Prerequisite |
|---|---|
| Retrieve source | None |
| Validate source | Retrieve source |
| Compile application | Validate source |
| Unit testing | Compile application |
| Security analysis | Compile application |
| Package generation | Unit testing and security analysis |
| Integration testing | Package generation |
| Deployment | Integration testing |

The dependency graph is a DAG.

The build system must not execute a task before all its prerequisites are satisfied.

This distinction is important:

- Topological sorting establishes a valid ordering.
- Dependency resolution identifies prerequisite relationships.
- Scheduling determines when eligible tasks execute.
- Execution performs the actual operations.

A topological ordering does not automatically execute tasks.

## 8. Independent Tasks and Parallel Execution

Tasks with no unresolved dependencies can potentially execute concurrently.

In the build pipeline:

    COMPILE
       |
       +----------+
       |          |
      UNIT     SECURITY
       |          |
       +----------+
            |
         PACKAGE

UNIT and SECURITY are independent after COMPILE finishes.

They can therefore execute in parallel if the execution environment supports concurrency.

### 8.1 Dependency Levels

The earliest execution level of a vertex is:

\[
level(v) =
\begin{cases}
0 & \text{if } indegree(v)=0\\
1+\max(level(u)) & \text{for all } u\rightarrow v
\end{cases}
\]

For the build example:

| Task | Level |
|---|---:|
| SOURCE | 0 |
| VALIDATE | 1 |
| COMPILE | 2 |
| UNIT | 3 |
| SECURITY | 3 |
| PACKAGE | 4 |
| INTEGRATION | 5 |
| DEPLOY | 6 |

Tasks at the same level are dependency-independent.

This does not guarantee that they can execute concurrently in practice.

Additional restrictions may include:

- Available CPU capacity.
- Memory limitations.
- Shared database access.
- File-system locks.
- External API rate limits.
- Resource ownership.
- Deployment environment restrictions.

### 8.2 Critical Path

The critical path is the longest-duration dependency path through a DAG.

It determines the minimum possible completion time under unlimited resources and assuming task durations and dependencies are fixed.

For task durations \(d(v)\), the earliest finish time is:

\[
EF(v)=d(v)+\max EF(u)
\]

over all prerequisites \(u\) of \(v\), with the maximum for an empty prerequisite set treated as zero.

The Python, JavaScript, C++17, and Java implementations calculate dependency levels rather than full critical-path durations.

The PostgreSQL model stores estimated task durations, which can be used to extend the scheduling analysis.

Dependency levels and critical paths are different concepts. Equal levels do not necessarily imply equal task durations or equal completion times.

## 9. Cycle Detection and Failure Handling

Circular dependencies make complete topological sorting impossible.

Example:

    BUILD_A -> BUILD_B
       ^          |
       |          v
       +------- BUILD_C

A useful dependency engine should identify invalid graphs before starting operations with external side effects.

The implementations provide:

- Immediate self-loop rejection.
- DFS cycle detection.
- Kahn's unresolved-vertex detection.
- Invalid dependency rejection.
- Duplicate task validation.
- Duplicate edge handling.
- Failure propagation.
- Blocked-task identification.

A failed prerequisite must prevent its dependent tasks from executing.

For example:

    FETCH -> TEST -> RELEASE

If TEST fails:

- FETCH remains completed.
- TEST becomes failed.
- RELEASE becomes blocked.

The JavaScript scheduler models this behavior with asynchronous task execution and events.

The Java implementation explicitly models state transitions.

The C++17 implementation models build execution and blocked states.

The Python implementation validates prerequisite completion during execution.

## 10. Python Implementation

**File:** `topological_sorting.py`

The Python script provides a reusable graph and dependency-resolution model.

### Main components

| Component | Responsibility |
|---|---|
| `DirectedGraph` | Maintains vertices and directed edges |
| `Task` | Represents a build task |
| `TaskStatus` | Defines task lifecycle states |
| `DependencyResolver` | Resolves and executes dependencies |
| `CycleDetectedError` | Reports cyclic dependencies |
| `TaskNotFoundError` | Reports missing task identifiers |

### Important mechanisms

The graph uses:

- `defaultdict` for adjacency management.
- `set` for duplicate-edge prevention.
- `deque` for Kahn's algorithm.
- Dictionaries for indegree and vertex states.
- Dataclasses for structured task information.
- Enums for execution states.

The implementation includes both sorting algorithms, dependency-level calculation, ordering validation, cycle detection, and a sequential build simulation.

The ordering-validation method verifies:

1. Every graph vertex occurs exactly once.
2. No unknown vertex is present.
3. Every prerequisite appears before its dependent.

The implementation is intentionally self-contained and uses only Python's standard library.

## 11. JavaScript Implementation

**File:** `topological_scheduler.js`

The JavaScript implementation provides an asynchronous scheduling perspective.

Its graph representation uses:

- `Map` for vertex storage.
- `Set` for outgoing dependencies.
- Reverse adjacency sets for prerequisite lookup.

The `DependencyScheduler` extends Node.js `EventEmitter`.

### Event-driven task lifecycle

| Event | Meaning |
|---|---|
| `taskStarted` | Task execution begins |
| `taskCompleted` | Task finishes successfully |
| `taskFailed` | Task execution fails |
| `taskBlocked` | A prerequisite has failed |
| `executionFinished` | Scheduler produces its final report |
| `schedulerError` | Scheduling encounters an error |

The scheduler uses Promises and asynchronous functions to execute independent tasks.

The concurrency limit prevents unlimited simultaneous execution.

Before execution begins, Kahn's algorithm validates the dependency graph.

### Failure propagation

A task becomes eligible only when every prerequisite is completed.

A failed prerequisite causes downstream tasks to become blocked.

The final report separates:

- Completed tasks.
- Failed tasks.
- Blocked tasks.
- Overall execution success.

The implementation demonstrates why dependency ordering and asynchronous execution are separate responsibilities.

The scheduler is an in-memory demonstration. Production distributed schedulers would require persistent state, retries, timeouts, cancellation, idempotency, and coordination between workers.

## 12. C++17 Implementation

**File:** `topological_sorting.cpp`

The C++ implementation focuses on a strongly structured build dependency engine.

### Main components

| Component | Responsibility |
|---|---|
| `DirectedGraph` | Graph representation and traversal |
| `BuildTask` | Build-task domain structure |
| `BuildEngine` | Dependency-aware execution |
| `NodeState` | DFS traversal states |
| `BuildStatus` | Task execution states |
| `GraphException` | Graph and dependency failures |

The implementation uses:

- `std::map` for deterministic graph representation.
- `std::set` for unique neighbors.
- `std::priority_queue` for deterministic Kahn scheduling.
- `std::unordered_map` for vertex positions.
- `std::unordered_set` for completed tasks.
- STL algorithms for ordering validation.

### Engineering considerations

Ordered containers provide deterministic traversal but introduce logarithmic lookup and insertion costs.

The implementation validates generated orderings independently rather than assuming that successful algorithm completion guarantees correctness.

The execution engine checks prerequisite completion before marking a task completed.

This separation supports extension into more complex build systems where execution failures and resource management must be handled independently.

## 13. Java 17 Implementation

**File:** `Main.java`

The Java implementation uses an enterprise-oriented domain model.

### Main domain types

| Type | Responsibility |
|---|---|
| `TaskDefinition` | Immutable task definition |
| `DependencyType` | Task classification |
| `TaskStatus` | Task lifecycle |
| `DependencyPolicy` | Graph-size restrictions |
| `DirectedAcyclicGraph` | Graph algorithms |
| `TaskExecutionService` | Scheduling and state transitions |
| `ExecutionResult` | Immutable execution result |
| `CycleException` | Cycle-specific failure |

The implementation uses Java 17 records for immutable task definitions and execution results.

The `DependencyPolicy` enforces maximum task and dependency counts.

### State transitions

The allowed execution transitions are:

    PENDING -> READY -> RUNNING -> COMPLETED
                                  |
                                  +-> FAILED

A pending task can also become BLOCKED when a prerequisite fails.

Invalid state transitions are rejected.

This is important in enterprise applications because an execution engine should not silently permit inconsistent lifecycle states.

The service validates the complete graph before starting execution.

The immutable result records provide structured execution reporting without exposing mutable internal collections.

The current execution service models sequential execution. A production implementation could use an executor service to process independent tasks concurrently while preserving dependency constraints.

## 14. PostgreSQL Implementation

**File:** `topological_sorting.sql`

The PostgreSQL implementation models dependency management as a relational workflow.

### 14.1 Database Structure

The schema contains the following principal tables:

| Table | Purpose |
|---|---|
| `repositories` | Repository ownership and identity |
| `tasks` | Task definitions and execution states |
| `task_dependencies` | Directed prerequisite relationships |
| `task_execution_history` | Task lifecycle audit records |

The relationship is:

    REPOSITORIES
         |
         v
       TASKS
         |
         v
    TASK_DEPENDENCIES
         |
         v
    TASK_EXECUTION_HISTORY

The dependency table represents a directed edge using:

- `prerequisite_task_id`
- `dependent_task_id`

A foreign key ensures that both tasks exist.

A unique constraint prevents duplicate dependency relationships.

A check constraint prevents direct self-dependencies.

### 14.2 Cycle Prevention Trigger

The `validate_dependency()` trigger function prevents cycles during dependency insertion or modification.

Before accepting a proposed edge:

\[
A\rightarrow B
\]

The function searches for an existing path:

\[
B\leadsto A
\]

If such a path exists, the proposed edge would create a directed cycle.

The database rejects the operation.

The recursive CTE performs reachability analysis using `UNION`, which prevents repeated vertices from causing unbounded recursion.

The trigger also prevents dependencies across different repositories.

**Concurrency limitation:** A trigger-based reachability check alone does not provide complete protection against concurrent transactions inserting different edges that jointly create a cycle. Production systems requiring strict DAG integrity must serialize graph mutations, for example by acquiring a repository-level transaction advisory lock before inserting or modifying dependency relationships.

### 14.3 Kahn's Algorithm in PostgreSQL

The `topological_order()` function implements Kahn's algorithm using temporary tables.

Its working structures are:

- `topo_indegree`: stores the current indegree and execution level.
- `topo_ready`: stores vertices available for processing.
- `topo_processed`: records the resulting order.

The function:

1. Calculates indegrees.
2. Identifies zero-indegree tasks.
3. Processes one available task.
4. Decreases dependent-task indegrees.
5. Makes newly available tasks eligible.
6. Detects cycles when not all vertices are processed.

The returned data includes:

- Task identifier.
- Task code.
- Execution position.
- Dependency execution level.

Temporary tables isolate intermediate calculations from persistent task records.

The function is designed for sequential calls within a transaction. Its temporary-table names are session-local and reused by truncation.

### 14.4 State Transition Enforcement

The `validate_task_transition()` trigger prevents invalid task-state changes.

For example:

`PENDING -> COMPLETED`

is rejected.

A task must pass through the appropriate intermediate states.

The audit trigger records status changes in `task_execution_history`.

This provides an execution trail for operational reporting and debugging.

### 14.5 Eligibility Determination

The `task_is_eligible()` function determines whether a task can be executed.

A task is eligible when:

1. It exists.
2. It is pending or ready.
3. Every prerequisite has completed successfully.

The `task_dependency_report` view aggregates prerequisite counts and completion states.

The `process_ready_tasks()` procedure identifies tasks whose prerequisites have completed.

It uses `FOR UPDATE SKIP LOCKED` to reduce contention between concurrent workers selecting tasks.

The procedure only marks tasks READY. Actual task execution remains an application responsibility.

## 15. Practical Applications

### Software build systems

A compiler must process source dependencies before dependent modules.

Topological sorting provides a valid compilation order.

### Package managers

A package may depend on multiple other packages.

The installation process must resolve these prerequisites before installing the dependent package.

### Database migrations

A migration that creates a foreign key may require the referenced table to exist first.

A DAG can represent the required migration order.

### Project scheduling

Project activities often have predecessor relationships.

A DAG helps identify valid task sequences and supports critical-path analysis.

### Data engineering

A data pipeline can represent transformations as vertices and data dependencies as directed edges.

Independent transformations can execute concurrently.

### Cloud deployment

Infrastructure resources may depend on other resources.

A deployment engine can use topological sorting to determine a valid creation sequence.

## 16. Important Edge Cases

| Case | Expected behavior |
|---|---|
| Empty graph | Return an empty ordering |
| Single vertex | Return that vertex |
| Isolated vertices | Include every vertex |
| Duplicate edge | Do not increase indegree twice |
| Self-loop | Reject immediately |
| Two-node cycle | Reject the graph |
| Longer cycle | Reject the graph |
| Multiple valid orderings | Return any valid ordering |
| Missing dependency | Reject the relationship |
| Failed prerequisite | Block dependent tasks |
| Disconnected components | Process each component |
| Deep dependency chain | Consider iterative DFS to avoid stack exhaustion |

A disconnected graph can still be a DAG.

Each independent component can be topologically sorted and combined into one valid ordering.

## 17. Security and Production Considerations

A dependency engine operating in a real environment should enforce several additional controls.

**Input validation**

Task identifiers and dependency relationships must be validated before they enter the graph.

**Resource limits**

Large graphs can consume significant memory and processing time. Limits should be enforced on task counts, edge counts, and traversal depth.

**Concurrency control**

Concurrent graph modifications can invalidate previously computed orderings. Graph changes and scheduling should be coordinated through transactions or versioned graph snapshots.

**Execution isolation**

A failed task should not automatically trigger unrelated downstream operations.

**Idempotency**

Retried tasks should not duplicate external side effects.

**Timeouts**

Long-running operations should have execution deadlines.

**Auditability**

State transitions and execution results should be retained for investigation and operational reporting.

**Persistence**

An in-memory graph is unsuitable as the only source of truth for a distributed production scheduler.

**Cycle prevention**

Cycle detection should occur both during graph modification and before execution. Database-level integrity must also account for concurrent transactions.

## 18. Complexity Comparison

Let:

- \(V\) = number of vertices.
- \(E\) = number of directed edges.

| Operation | Complexity |
|---|---|
| Add vertex | \(O(1)\) average with hash-based storage |
| Add edge | \(O(1)\) average with hash-based adjacency sets |
| DFS topological sort | \(O(V+E)\) |
| Kahn topological sort | \(O(V+E)\) with a FIFO queue |
| Priority-queue Kahn | \(O((V+E)\log V)\) |
| Dependency-level calculation | \(O(V+E)\) after ordering |
| Ordering validation | \(O(V+E)\) |
| Full graph storage | \(O(V+E)\) |

These complexities assume suitable adjacency-list representations and efficient vertex lookup.

The PostgreSQL implementation also incurs relational lookup, indexing, temporary-table, and transaction overhead that is not captured by the abstract graph complexity.

## 19. Learning Outcomes

The implementations establish the relationship between graph theory and practical dependency management:

1. A directed edge represents a prerequisite relationship.
2. A DAG guarantees the existence of a topological ordering.
3. DFS uses recursion states and reverse postorder.
4. Kahn's algorithm uses indegrees and a queue.
5. Cycle detection identifies invalid dependency structures.
6. Dependency levels expose groups of potentially parallel tasks.
7. Topological sorting establishes order but does not execute operations.
8. Scheduling manages task eligibility and execution.
9. Failure propagation prevents invalid downstream execution.
10. Persistent relational models can enforce and report dependency relationships.

The central distinction is between a valid dependency ordering and a successfully executed workflow. A correct topological ordering satisfies graph constraints, while a production dependency-management system must also enforce execution states, resource limits, failure handling, persistence, and concurrency controls.
