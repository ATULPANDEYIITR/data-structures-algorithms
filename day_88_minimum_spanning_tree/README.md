# Minimum Spanning Tree: Algorithms, Network Optimization and Governance

## 1. Introduction

A Minimum Spanning Tree (MST) is a fundamental graph optimization structure used to connect all vertices of a connected, undirected, weighted graph while minimizing the sum of selected edge weights.

The problem appears in telecommunications, electrical distribution, transportation infrastructure, computer networks, water distribution, and large-scale infrastructure planning.

Consider a telecommunications organization connecting six regional network hubs. Several possible fiber-optic connections are available, each with a different installation cost. The objective is to connect every hub while minimizing total infrastructure expenditure.

An MST provides a solution without introducing unnecessary cycles.

The implementations cover two principal algorithms:

- Kruskal's algorithm.
- Prim's algorithm.

They also address disconnected graphs, network policies, validation, cost optimization, and operational planning.

## 2. Graph Fundamentals

A graph is represented as:

\[
G=(V,E)
\]

Where:

- \(V\) represents the set of vertices.
- \(E\) represents the set of edges.
- \(w(e)\) represents the weight associated with an edge.

For an infrastructure network:

| Graph concept | Infrastructure interpretation |
|---|---|
| Vertex | Regional network hub |
| Edge | Available physical connection |
| Weight | Installation or connection cost |
| Path | Sequence of connected infrastructure links |
| Cycle | A closed route through multiple connections |
| Component | A connected group of network hubs |
| Spanning tree | A connected, cycle-free network containing every hub |
| Minimum spanning tree | A spanning tree with minimum total cost |

An undirected edge permits movement in either direction.

For example, an edge connecting Lucknow and Kanpur represents a physical connection that can support communication in both directions.

### 2.1 Weighted graph representation

The sample network contains six vertices:

\[
V=\{A,B,C,D,E,F\}
\]

Its candidate connections include:

| Connection | Weight |
|---|---:|
| A-B | 4 |
| A-C | 3 |
| B-C | 1 |
| B-D | 2 |
| C-D | 4 |
| C-E | 5 |
| D-E | 2 |
| D-F | 6 |
| E-F | 3 |
| A-F | 10 |

The graph contains ten candidate edges.

The objective is to select five connections that connect all six vertices.

## 3. Spanning Trees

A spanning tree is a subgraph containing every vertex of the original connected graph.

It must satisfy three properties:

1. Every original vertex is included.
2. Every vertex is reachable from every other vertex.
3. The selected edges contain no cycles.

For a connected graph containing \(V\) vertices, every spanning tree contains:

\[
|E_{MST}|=|V|-1
\]

For six vertices:

\[
|E_{MST}|=6-1=5
\]

The minimum spanning tree is the spanning tree with the lowest aggregate edge weight.

Its objective function is:

\[
MST(G)=
\arg\min_{T\subseteq E}
\sum_{e\in T}w(e)
\]

Subject to the selected edges forming a spanning tree.

### 3.1 Why cycles are unnecessary

Suppose three network hubs A, B, and C have connections:

- A-B
- B-C
- A-C

All three edges form a cycle.

If A-B and B-C already connect all three vertices, A-C is unnecessary for the spanning-tree requirement.

Removing that edge preserves connectivity.

The same principle applies to larger graphs: an MST never contains a cycle.

### 3.2 Minimum spanning forest

A disconnected graph does not have a spanning tree because some vertices cannot be reached from others.

It can still have a Minimum Spanning Forest (MSF).

An MSF contains a minimum spanning tree for each connected component.

For a graph with \(C\) connected components:

\[
|E_{MSF}|=|V|-C
\]

For example, a network containing:

- Component 1: A, B, C
- Component 2: X, Y
- Component 3: Z

has six vertices and three components.

Its minimum spanning forest contains:

\[
6-3=3
\]

selected edges.

The Python, JavaScript, C++, and PostgreSQL implementations support disconnected-network detection and forest generation.

## 4. Disjoint Set Union

Disjoint Set Union (DSU), also called Union-Find, maintains a collection of non-overlapping sets.

It is particularly useful in Kruskal's algorithm because it determines whether connecting two vertices would introduce a cycle.

DSU supports two principal operations.

### 4.1 Find

`find(x)` identifies the representative of the component containing vertex \(x\).

Two vertices belong to the same connected component if:

\[
find(u)=find(v)
\]

### 4.2 Union

`union(u,v)` combines two previously separate components.

If both vertices already belong to the same component, the operation returns false.

This indicates that adding the corresponding edge would create a cycle.

### 4.3 Path compression

Path compression modifies parent references during the Find operation.

Instead of retaining a long parent chain, vertices are redirected toward their component representative.

This substantially reduces future traversal time.

### 4.4 Union by rank

Union by rank attaches the smaller tree beneath the root of the larger tree.

The rank is an upper-bound indicator of tree height.

Combining path compression and union by rank produces nearly constant amortized operation time:

\[
O(\alpha(V))
\]

Here, \(\alpha\) is the inverse Ackermann function.

For practical graph sizes, this operation is extremely efficient.

## 5. Kruskal's Algorithm

Kruskal's algorithm constructs an MST by considering candidate edges in ascending order of weight.

It is a greedy algorithm because each selection makes the locally cheapest valid choice.

### 5.1 Execution mechanism

The algorithm performs these operations:

1. Initialize every vertex as an independent component.
2. Sort all edges by ascending weight.
3. Examine the cheapest remaining edge.
4. Find the components containing its endpoints.
5. Select the edge if the endpoints belong to different components.
6. Merge the components.
7. Reject the edge if it would create a cycle.
8. Stop when a connected graph has \(V-1\) selected edges.

For disconnected graphs, processing continues until every available edge has been considered.

### 5.2 Sample execution

The candidate edges are sorted as follows:

| Order | Edge | Weight | Decision |
|---:|---|---:|---|
| 1 | B-C | 1 | Select |
| 2 | B-D | 2 | Select |
| 3 | D-E | 2 | Select |
| 4 | A-C | 3 | Select |
| 5 | E-F | 3 | Select |
| 6 | A-B | 4 | Reject |
| 7 | C-D | 4 | Reject |
| 8 | C-E | 5 | Reject |
| 9 | D-F | 6 | Reject |
| 10 | A-F | 10 | Reject |

The first five edges connect all six vertices.

The remaining edges are rejected because they would introduce cycles.

The resulting MST cost is:

\[
1+2+2+3+3=11
\]

### 5.3 Complexity

Sorting dominates the execution time.

\[
O(E\log E)
\]

DSU operations contribute approximately:

\[
O(E\alpha(V))
\]

The overall time complexity is:

\[
O(E\log E)
\]

The algorithm requires:

\[
O(V+E)
\]

space for graph storage, sorting, and DSU structures.

Kruskal is particularly useful for sparse graphs and scenarios where the candidate connections are naturally available as an edge list.

## 6. Prim's Algorithm

Prim's algorithm constructs an MST by expanding a connected tree from an initial vertex.

Unlike Kruskal, which considers the globally cheapest remaining edge, Prim considers the cheapest edge connecting the current tree to an unvisited vertex.

### 6.1 Execution mechanism

1. Select a starting vertex.
2. Mark it as visited.
3. Insert its outgoing candidate edges into a minimum priority queue.
4. Extract the cheapest available edge.
5. Ignore it if its destination is already visited.
6. Otherwise, add the destination and edge to the tree.
7. Insert the new vertex's eligible outgoing edges.
8. Continue until the connected component is exhausted.

For disconnected graphs, a new traversal begins from another unvisited vertex.

### 6.2 Priority queue

A minimum priority queue efficiently retrieves the cheapest candidate edge.

The Python implementation uses `heapq`.

The JavaScript implementation includes a custom binary minimum heap.

The C++ implementation uses the STL heap operations.

The Java implementation uses `PriorityQueue`.

### 6.3 Complexity

Using an adjacency list and binary heap:

\[
O((V+E)\log V)
\]

For connected sparse graphs, this is commonly expressed as:

\[
O(E\log V)
\]

Space complexity:

\[
O(V+E)
\]

Prim is particularly useful when a network is represented through adjacency relationships and the solution is expanded incrementally.

## 7. Kruskal Versus Prim

| Characteristic | Kruskal | Prim |
|---|---|---|
| Primary strategy | Global edge selection | Tree expansion |
| Main data structure | DSU | Minimum priority queue |
| Edge processing | Ascending weight | Cheapest outgoing edge |
| Cycle detection | DSU | Visited vertices |
| Typical representation | Edge list | Adjacency list |
| Time complexity | \(O(E\log E)\) | \(O(E\log V)\) |
| Sparse graphs | Effective | Effective |
| Dense graphs | Sorting may be expensive | Can use adjacency matrix |
| Disconnected graphs | Produces a forest | Produces a forest |

Both algorithms produce the same minimum total cost when applied correctly to the same weighted graph.

They do not necessarily produce identical edge sets.

## 8. Minimum Spanning Tree Properties

### 8.1 Cut property

A cut divides a graph's vertices into two non-overlapping groups.

An edge crossing the cut connects one group to the other.

A minimum-weight edge crossing a cut is safe to include in at least one MST.

This property provides a theoretical foundation for greedy MST algorithms.

### 8.2 Cycle property

For a cycle containing a uniquely heaviest edge, that edge cannot belong to an MST.

Removing the heaviest edge from the cycle preserves connectivity while reducing total cost.

### 8.3 Uniqueness

An MST is not necessarily unique.

If multiple edges have equal weights, alternative spanning trees can have the same minimum cost.

A graph with distinct edge weights has a unique MST.

The Python implementation includes an equal-weight group analysis that checks whether alternative minimum-weight component connections exist.

The other implementations focus on calculating and validating MST structures rather than performing complete uniqueness analysis.

### 8.4 Negative and zero weights

Standard MST algorithms support negative edge weights mathematically.

They also support zero-weight edges.

The implementations use nonnegative weights because the modeled domain represents infrastructure installation costs.

This is a domain validation decision rather than a mathematical restriction of MST algorithms.

Non-finite floating-point weights are rejected to prevent invalid comparisons.

## 9. Python Implementation

The Python program models the graph using dataclasses and collections.

### 9.1 Domain components

| Component | Responsibility |
|---|---|
| `Edge` | Immutable weighted connection |
| `WeightedGraph` | Vertices and candidate connections |
| `DisjointSet` | Component tracking |
| `MSTResult` | Algorithm output and statistics |
| `Algorithm` | Algorithm selection |
| `GraphError` | Graph validation failures |
| `DisconnectedGraphError` | Missing spanning-tree connectivity |

### 9.2 Kruskal implementation

The graph's edge list is sorted using:

- Connection weight.
- Normalized endpoint identifiers.

The normalized endpoint ordering makes tie-breaking deterministic.

The DSU rejects cycle-forming edges.

### 9.3 Prim implementation

The adjacency list stores each undirected connection in both directions.

The heap stores candidate edges ordered by:

1. Weight.
2. Source.
3. Destination.

Already visited destinations are ignored.

### 9.4 Result verification

The verification function checks:

- Correct vertex count.
- Correct component count.
- Expected edge count.
- Absence of cycles.
- Correct aggregate cost.

For a forest:

\[
E=V-C
\]

This invariant is used to verify the output.

### 9.5 Uniqueness analysis

Edges are processed in groups of equal weight.

Before merging a group into the main DSU, a temporary DSU identifies alternative connections between existing components.

If the temporary component graph contains a cycle, alternative equal-cost spanning choices exist.

This provides a useful uniqueness test without enumerating every possible spanning tree.

## 10. JavaScript Implementation

The JavaScript implementation emphasizes event-driven network management and policy evaluation.

### 10.1 Event-driven architecture

The `NetworkPlanner` extends Node.js `EventEmitter`.

Important events include:

| Event | Purpose |
|---|---|
| `vertexAdded` | Reports a new network vertex |
| `connectionAdded` | Reports a new candidate connection |
| `planEvaluated` | Reports the completed policy evaluation |

This separation allows monitoring, reporting, and other application services to react to network changes without coupling them to MST calculations.

### 10.2 Immutable snapshots

A network snapshot contains:

- Network version.
- Vertex collection.
- Candidate edge collection.

Both MST algorithms can operate on the same snapshot.

This prevents different algorithm executions from observing different graph states during a comparison.

### 10.3 Optimistic concurrency

Each successful network modification increments a version number.

A modification can supply the version it expects.

If the actual version differs, a `VersionConflictError` is raised.

This prevents stale updates from silently overwriting newer network state.

The mechanism is an in-memory concurrency safeguard. A production database implementation must also use appropriate transaction isolation and locking.

### 10.4 Network policy evaluation

`NetworkPolicy` evaluates a calculated MST against:

- Required connectivity.
- Maximum aggregate cost.
- Maximum individual connection cost.
- Forbidden connections.
- Mandatory connections.

The result separates the mathematical MST from its operational eligibility.

A mathematically optimal tree can still violate business requirements.

### 10.5 Asynchronous comparison

`runIndependentPlans()` executes Kruskal and Prim through independent asynchronous tasks.

Both use the same immutable snapshot.

Their total costs are compared before accepting the result.

## 11. C++17 Implementation

The C++ implementation emphasizes efficient graph processing and explicit governance evaluation.

### 11.1 Domain architecture

| Component | Responsibility |
|---|---|
| `Edge` | Connection representation |
| `DisjointSet` | Union-Find operations |
| `MSTResult` | Calculated network result |
| `NetworkPolicy` | Cost and connectivity constraints |
| `PolicyEvaluation` | Eligibility and violations |
| `NetworkGovernance` | Graph processing and validation |

### 11.2 STL usage

The implementation uses:

- `vector` for vertices and edges.
- `map` for vertex indexing.
- `set` for policy constraints.
- `sort` for Kruskal edge ordering.
- Heap operations for Prim.
- `iota` for DSU initialization.
- `tuple` for priority queue candidates.

### 11.3 Vertex indexing

The network stores vertex identifiers in a map.

String-based vertex identifiers are converted to integer indexes for DSU operations.

This separates readable domain identifiers from efficient internal graph processing.

### 11.4 Governance evaluation

The C++ policy engine checks:

- Full connectivity.
- Total network budget.
- Maximum individual connection cost.
- Forbidden connections.
- Mandatory connections.

The policy evaluator returns structured violations instead of terminating MST calculation.

This allows mathematical optimization and organizational approval to remain separate operations.

## 12. Java 17 Implementation

The Java implementation models an enterprise infrastructure planning workflow.

It uses records, immutable collections, domain-specific services, and explicit state transitions.

### 12.1 Enterprise domain types

| Type | Purpose |
|---|---|
| `Vertex` | Identifies an infrastructure location |
| `Connection` | Represents a weighted provider connection |
| `Network` | Maintains the graph |
| `NetworkPolicy` | Defines operational restrictions |
| `PlanResult` | Stores calculated MST output |
| `PolicyViolation` | Records validation failures |
| `NetworkPlan` | Controls the planning lifecycle |
| `PlanningService` | Executes MST algorithms |

Records make connection and result objects concise and immutable.

### 12.2 Planning lifecycle

The plan follows this state sequence:

DRAFT → CALCULATED → VALIDATED → APPROVED

A policy failure changes the state to:

REJECTED

The state transition prevents an uncalculated or invalid plan from receiving approval.

### 12.3 Policy severity

The implementation distinguishes:

- ERROR: prevents validation and approval.
- WARNING: identifies a concern without automatically preventing approval.

For example, a minimum provider-diversity requirement can generate a warning.

This is different from a connectivity or budget violation, which is treated as an error.

### 12.4 Stale plan protection

A plan captures the network version when it is created.

If the underlying network changes before calculation, validation, or approval, the plan is rejected.

This protects the approval workflow from relying on outdated network data.

### 12.5 Enterprise limitations

The implementation uses synchronized methods and an in-memory version counter.

A distributed enterprise deployment would require persistent versioning, database transactions, access-control policies, approval identities, and audit logging.

The current implementation demonstrates the domain and lifecycle mechanics without claiming to provide a complete distributed transaction system.

## 13. PostgreSQL Implementation

The PostgreSQL implementation provides a relational representation of infrastructure planning.

It separates graph structure, candidate connections, policy configuration, calculated plans, and approval records.

### 13.1 Database relationship

The primary relationships are:

Networks
  |
  +-- Network Vertices
  |
  +-- Candidate Connections
  |
  +-- Network Policies
  |      |
  |      +-- Policy Connection Rules
  |
  +-- Network Plans
         |
         +-- Plan Connections
         |
         +-- Plan Violations
         |
         +-- Plan Approvals

### 13.2 Main tables

| Table | Purpose |
|---|---|
| `networks` | Infrastructure network definitions |
| `network_vertices` | Network locations |
| `candidate_connections` | Available weighted edges |
| `network_policies` | Cost and connectivity rules |
| `policy_connection_rules` | Mandatory and forbidden edges |
| `network_plans` | Planning lifecycle and aggregate results |
| `plan_connections` | Selected MST edges |
| `plan_violations` | Validation findings |
| `plan_approvals` | Approval audit history |

### 13.3 Referential integrity

Primary keys uniquely identify database records.

Foreign keys enforce valid relationships between:

- Networks and vertices.
- Networks and connections.
- Plans and selected connections.
- Policies and connection rules.
- Plans and approval records.

Check constraints reject invalid values such as:

- Negative connection costs.
- Invalid geographical coordinates.
- Self-loops.
- Invalid approval decisions.
- Negative budget limits.

The connection trigger ensures that both endpoints belong to the same network.

Undirected connections are stored with ascending vertex identifiers.

This prevents storing both A-B and B-A as separate connections.

### 13.4 Kruskal in PL/pgSQL

The function `calculate_minimum_spanning_tree()` implements Kruskal's algorithm.

It:

1. Locks the plan row.
2. Checks that the plan is in DRAFT state.
3. Retrieves network vertex identifiers.
4. Initializes DSU parent and rank arrays.
5. Retrieves available connections ordered by cost.
6. Finds the component representatives.
7. Rejects cycle-forming edges.
8. Unites separate components.
9. Inserts selected connections.
10. Updates the plan's cost and connectivity information.

The arrays represent the DSU internally.

`array_position()` maps database vertex identifiers to array positions.

The function uses deterministic edge ordering through connection identifiers when costs are equal.

### 13.5 Policy validation

`validate_network_plan()` evaluates the calculated result against its assigned policy.

It checks:

- Required connectivity.
- Total cost.
- Individual connection cost.
- Forbidden connections.
- Mandatory connections.
- Provider diversity.

Findings are persisted in `plan_violations`.

The plan becomes VALIDATED when no errors exist.

A plan with errors becomes REJECTED.

Provider-diversity findings are recorded as warnings.

### 13.6 Approval procedure

`approve_network_plan()` performs the final approval operation.

It verifies:

- The plan exists.
- The current state is VALIDATED.
- No unresolved error violations exist.

It then updates the plan status and records the approving identity and remarks.

The procedure does not calculate an MST. Calculation, validation, and approval remain separate database operations.

### 13.7 Transactions and consistency

The script uses a transaction for schema creation, sample data, calculations, validation, and approval.

The calculation function locks the plan record using `FOR UPDATE`.

This protects concurrent modifications to the same plan during calculation.

For production deployments, additional concurrency controls would be required around modifications to candidate connections, vertices, and policies.

The network planning model should use a consistent source snapshot when a plan is calculated and subsequently approved.

## 14. Network Planning Workflow

A practical MST-based infrastructure planning process follows this sequence:

1. Register the network.
2. Register all infrastructure locations.
3. Record available candidate connections.
4. Assign installation costs and providers.
5. Configure network policies.
6. Create a planning record.
7. Calculate the MST.
8. Verify connectivity and aggregate cost.
9. Evaluate operational policies.
10. Record violations.
11. Approve a validated plan.
12. Preserve the final decision and selected connections.

The mathematical and governance stages have different responsibilities.

| Stage | Responsibility |
|---|---|
| Graph construction | Represent available network connections |
| Optimization | Find the minimum-cost spanning structure |
| Verification | Check connectivity, cycles, and edge count |
| Policy evaluation | Determine whether operational rules are satisfied |
| Approval | Authorize the validated plan |
| Persistence | Retain the result and decision history |

## 15. Mathematical Optimization Versus Operational Constraints

An important distinction exists between finding the mathematically cheapest MST and producing an operationally acceptable infrastructure plan.

Consider a network where the cheapest MST costs 11 units.

An organization might impose these additional conditions:

- Total expenditure must not exceed 15.
- No individual connection may cost more than 6.
- Every network location must be connected.
- A specified provider must not be used.
- A mandatory connection must appear in the selected design.

The MST algorithm minimizes the sum of edge weights.

It does not automatically satisfy arbitrary business restrictions.

### 15.1 Mandatory connections

A mandatory connection must be selected even if it is not part of an unconstrained MST.

A practical approach is to process mandatory edges first, merge their components, and then optimize the remaining graph.

Mandatory edges must be checked for cycles. A mandatory set containing a cycle cannot form part of a spanning tree without violating the tree property.

### 15.2 Forbidden connections

Forbidden connections are removed from the eligible candidate set before optimization.

The Python, JavaScript, C++, Java, and SQL policy examples evaluate prohibited selections separately from the mathematical MST calculation.

The sample implementations do not implement a complete constrained-MST solver for arbitrary combinations of mandatory and forbidden edges.

For operational deployment, constrained optimization must be performed before finalizing the selected tree rather than merely rejecting an unconstrained result.

### 15.3 Budget constraints

The MST minimizes aggregate edge cost.

A budget policy evaluates:

\[
C_{MST}\leq B
\]

Where:

- \(C_{MST}\) is the selected total cost.
- \(B\) is the authorized budget.

An MST that exceeds the budget remains mathematically optimal but is not eligible under that policy.

## 16. Edge Cases and Failure Conditions

| Condition | Expected behavior |
|---|---|
| Empty graph | Reject MST calculation |
| Single vertex | Valid tree with zero edges |
| Disconnected graph | Return forest or reject connected-tree requirement |
| Self-loop | Reject connection |
| Duplicate undirected edge | Reject duplicate |
| Negative infrastructure cost | Reject under domain validation |
| Infinite weight | Reject |
| Equal edge weights | Allow alternative MSTs |
| Cycle-forming edge | Ignore during MST construction |
| Isolated vertex | Preserve as a separate component |
| Missing endpoint | Reject connection |
| Budget exceeded | Generate policy violation |
| Mandatory edge missing | Reject policy validation |
| Forbidden edge selected | Reject policy validation |
| Stale network version | Reject outdated plan |

### 16.1 Single-vertex graph

A graph with one vertex and no edges is already connected.

Its spanning tree has zero edges and zero cost.

### 16.2 Disconnected graph

A disconnected graph can produce a minimum spanning forest.

An application requiring complete infrastructure connectivity must reject the result.

### 16.3 Equal-weight alternatives

Different valid MSTs can have the same total cost.

A system should not assume that an MST edge set is unique.

### 16.4 Numerical precision

The implementations use floating-point values in Python, JavaScript, C++, and Java.

For actual financial accounting, fixed-precision decimal representations are preferable.

The PostgreSQL implementation uses `NUMERIC(18,2)` for installation costs.

## 17. Performance Analysis

Let:

- \(V\) represent the number of vertices.
- \(E\) represent the number of candidate edges.

| Operation | Complexity |
|---|---|
| Graph vertex insertion | Expected \(O(1)\) with hash-based storage |
| Graph edge insertion | Expected \(O(1)\) with indexed storage |
| Edge sorting | \(O(E\log E)\) |
| DSU Find | Amortized \(O(\alpha(V))\) |
| DSU Union | Amortized \(O(\alpha(V))\) |
| Kruskal | \(O(E\log E)\) |
| Prim with binary heap | \(O((V+E)\log V)\) |
| Adjacency list construction | \(O(V+E)\) |
| MST result storage | \(O(V)\) for a spanning forest |

### 17.1 Sparse graphs

A sparse graph has relatively few edges compared with its maximum possible edge count.

For sparse networks, Kruskal is often effective because sorting the candidate edge list is manageable.

### 17.2 Dense graphs

Dense graphs contain many candidate connections.

The choice of algorithm and graph representation becomes important.

An adjacency-matrix implementation of Prim has:

\[
O(V^2)
\]

time complexity.

This can be competitive for dense graphs where:

\[
E\approx V^2
\]

### 17.3 Database performance

The PostgreSQL implementation creates indexes for:

- Network identification.
- Candidate edge costs.
- Edge endpoints.
- Plan status.
- Selected connections.
- Validation history.

These indexes support common retrieval and planning queries.

The PL/pgSQL implementation is intended as an executable educational and moderate-scale relational workflow.

For very large networks, graph processing should be benchmarked outside the database or implemented with more efficient database-side representations.

## 18. Security and Reliability Considerations

Infrastructure planning data can influence expensive and operationally sensitive deployment decisions.

A production implementation should consider the following controls.

### Access control

Separate permissions should exist for:

- Network configuration.
- Candidate connection management.
- Policy management.
- Plan calculation.
- Validation.
- Final approval.

A user who calculates a plan should not automatically receive approval privileges.

### Input validation

Validate:

- Vertex identifiers.
- Connection endpoints.
- Cost ranges.
- Provider identifiers.
- Policy configuration.
- Plan lifecycle transitions.

### Auditability

Record:

- Plan creation.
- Source network version.
- Selected connections.
- Calculated cost.
- Validation findings.
- Approval identity.
- Approval timestamp.

### Transaction consistency

Calculation and persistence must be consistent.

A plan should not be approved using candidate edges or policies that changed after calculation without recalculation and validation.

### Reproducibility

Retain enough information to reconstruct a calculated plan, including:

- Candidate connection versions.
- Edge weights.
- Availability states.
- Algorithm selection.
- Policy version.
- Deterministic tie-breaking rules.

## 19. Cross-Language Implementation Comparison

| Capability | Python | JavaScript | C++17 | Java 17 | PostgreSQL |
|---|---|---|---|---|---|
| Weighted graph | Yes | Yes | Yes | Yes | Yes |
| Kruskal | Yes | Yes | Yes | Yes | Yes |
| Prim | Yes | Yes | Yes | Yes | No |
| DSU | Yes | Yes | Yes | Yes | Yes |
| Minimum spanning forest | Yes | Yes | Yes | Yes | Yes |
| Policy evaluation | Partial/full sample policies | Yes | Yes | Yes | Yes |
| Mandatory connections | Evaluation | Evaluation | Evaluation | Evaluation | Evaluation |
| Forbidden connections | Evaluation | Evaluation | Evaluation | Evaluation | Evaluation |
| Event notifications | Logging | EventEmitter | No | No | Triggers |
| Version validation | No | Yes | No | Yes | Transaction locking |
| Approval lifecycle | No | No | No | Yes | Yes |
| Persistent storage | No | No | No | No | Yes |
| MST uniqueness analysis | Yes | No | No | No | No |

## 20. Verification Results

The sample network has six vertices and ten candidate connections.

The expected minimum spanning tree is:

| Selected connection | Weight |
|---|---:|
| B-C | 1 |
| B-D | 2 |
| D-E | 2 |
| A-C | 3 |
| E-F | 3 |
| **Total** | **11** |

The expected properties are:

\[
V=6
\]

\[
E_{MST}=5
\]

\[
C=1
\]

\[
Cost=11
\]

Both Kruskal and Prim should return a connected spanning tree with the same total cost.

The implementations also test invalid weights, duplicate connections, cycle detection, disconnected graphs, policy failures, and stale planning states where applicable.

## 21. Practical Applications

### Telecommunications

Connecting regional communication hubs using the lowest aggregate installation cost.

### Electrical distribution

Designing cost-efficient distribution connections between substations.

### Transportation infrastructure

Connecting transport facilities through a minimum-cost network of proposed routes.

### Water distribution

Establishing a basic connected pipeline network between distribution locations.

### Computer networks

Planning physical connections between switches, routers, and network facilities.

### Distributed infrastructure

Creating an initial connectivity backbone before applying redundancy, capacity, latency, and fault-tolerance requirements.

An MST provides a cost-efficient connectivity backbone. It does not guarantee resilience against network failures because removing one selected tree edge can disconnect the network.

Real-world designs may therefore require additional redundant connections beyond the MST.

## 22. Important Distinctions

| Concept | Meaning |
|---|---|
| Spanning tree | Any connected, cycle-free spanning subgraph |
| Minimum spanning tree | Minimum-weight spanning tree |
| Minimum spanning forest | Collection of MSTs for disconnected components |
| Shortest path tree | Tree minimizing paths from a particular source |
| Minimum spanning tree cost | Sum of selected edge weights |
| Network reliability | Ability to remain operational under failures |
| Constrained MST | MST optimization subject to additional restrictions |

A minimum spanning tree is not the same as a shortest path tree.

An MST minimizes the sum of all selected edge weights.

A shortest path tree minimizes distances from one designated source vertex.

The two structures solve different optimization problems.
