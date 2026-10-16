# Recursion Fundamentals: Problem Decomposition and Dependency Analysis

## Purpose and scope

Recursion is a method of solving a problem by expressing it in terms of smaller instances of the same problem. A recursive implementation needs a stopping condition, a rule for reducing the problem, and a return operation that combines the results of smaller calls.

The examples in this repository connect the mathematical foundations of recursion to practical computational problems. They cover factorials, Fibonacci numbers, nested data, binary search, sorting, graph traversal, dependency planning, and SQL hierarchical queries.

The central distinction is between **recursive structure** and **recursive execution**. A nested directory is recursive in structure because a directory can contain another directory. A recursive function processes that structure by calling itself on each nested directory. These ideas are related, but one describes the data and the other describes the algorithm.

## How a recursive call works

Consider factorial:

\[
n! = n(n-1)!, \qquad n > 1
\]

with the boundary definition

\[
0! = 1
\]

The implementation of `factorial(4)` creates a sequence of dependent calls:

- `factorial(4)` needs the result of `factorial(3)`.
- `factorial(3)` needs the result of `factorial(2)`.
- `factorial(2)` needs the result of `factorial(1)`.
- `factorial(1)` returns the base value `1`.

The pending multiplications are then evaluated as the calls return. Each active call has its own local state and return address. This execution history is represented by the call stack.

A base case must be reachable from every valid recursive path. A recursive case must reduce the problem according to a rule that eventually reaches that base case. If either condition is missing, execution may continue until the runtime raises a stack-overflow or recursion-depth error.

The base case is part of the mathematical definition, not an optional optimization. For factorial, returning zero at the base case would make every positive factorial zero because each earlier call multiplies by that result.

## Python implementation

The Python script uses several different forms of recursive decomposition.

### Factorial and the call stack

`factorial` uses the direct mathematical recurrence. `factorial_trace` prints each call and return so the relationship between descending calls and ascending results is observable.

The separate `factorial_iterative` function calculates the same result using a loop. Comparing the implementations demonstrates that recursion is a problem-solving technique rather than a requirement for every problem with a recurrence relation.

The functions reject negative integers and Boolean values. Python treats `bool` as a subclass of `int`, so checking only `isinstance(n, int)` would accept `True` as the integer one. Explicit validation prevents this unintended behavior.

### Repeated work and memoization

The naive Fibonacci implementation follows

\[
F(n)=F(n-1)+F(n-2)
\]

with \(F(0)=0\) and \(F(1)=1\).

The recursive tree for `fibonacci_naive(6)` contains multiple calls for the same values. Both branches eventually calculate `fibonacci_naive(4)`, `fibonacci_naive(3)`, and other overlapping subproblems. This repeated work produces exponential time complexity, approximately \(O(2^n)\).

`fibonacci_memoized` uses `functools.lru_cache` to store completed results. Each distinct input is calculated once, reducing the time complexity to \(O(n)\), with \(O(n)\) storage and recursive stack depth.

`fibonacci_bottom_up` calculates the same sequence iteratively. It retains only the two preceding values, achieving \(O(n)\) time and \(O(1)\) auxiliary space. The three implementations illustrate the trade-off between direct recursive expression, caching, and iterative state management.

### Recursive search and sorting

`binary_search_recursive` operates on an already sorted list. It compares the middle element with the target and discards half of the remaining search interval. Its time complexity is \(O(\log n)\), and its recursive stack uses \(O(\log n)\) space.

The precondition matters: binary search does not reliably locate a target in an arbitrary unsorted list. An empty list is handled by the base condition `left > right`, which returns `-1`.

`merge_sort` divides the input into two smaller lists, sorts both recursively, and merges the ordered results. Its time complexity is \(O(n\log n)\), and its auxiliary storage is \(O(n)\) for this list-based implementation. Choosing the left item when two values are equal preserves the relative order of equal elements, making the algorithm stable.

### Nested structures and graph traversal

`sum_nested` recursively processes lists that contain either integers or further lists. Each recursive call handles one nested subproblem and contributes its total to the enclosing list.

`recursive_directory_size` uses the same decomposition principle for a directory tree. File sizes are leaves; directories are branches. The returned total combines the sizes of all descendant files.

`depth_limited_search` applies recursion to a dependency graph. Its active-path set detects cycles along the current search path. It deliberately does not use a global visited set because a node that fails under one remaining-depth budget may be reachable under another path with more available depth.

The depth limit bounds traversal depth, not necessarily total work. A graph with many branching paths can still produce substantial work before the limit is reached.

### Exponentiation and greatest common divisor

`recursive_power` uses exponentiation by squaring. Rather than multiplying the base repeatedly, it calculates the power for half the exponent and squares the result. Its recursion depth is \(O(\log n)\).

`recursive_gcd` implements Euclid's algorithm:

\[
\gcd(a,b)=\gcd(b,a\bmod b)
\]

until the second argument becomes zero. The number of recursive steps is logarithmic in the magnitude of the inputs in the worst case.

The test runner verifies valid results and expected failures. The timing comparison is illustrative rather than a formal benchmark because execution time depends on the machine, runtime, and workload.

## JavaScript implementation

The JavaScript file extends the recursive model with arbitrary-precision integers, reusable memoization, immutable data, and asynchronous traversal.

### Integer precision and memoization

JavaScript's ordinary `Number` type cannot represent every integer exactly beyond `Number.MAX_SAFE_INTEGER`. The factorial implementation uses `BigInt` for its result, while `factorialBigInt` accepts a `BigInt` input so that both the input and result can be represented exactly.

The memoization helper uses a `Map` and caches results by input value. Its wrapper passes the memoized function back to the calculation, ensuring recursive calls use the cache rather than bypassing it. This is important: caching only the outermost call would not eliminate the repeated work inside the recursion.

The memoized Fibonacci implementation still uses recursion and therefore retains a stack-depth limitation. Caching improves repeated computation but does not eliminate the call stack.

### Partitioning and nested objects

`quicksort` selects a pivot and partitions the values into lower, equal, and higher groups. The equal group is excluded from further recursive calls, which is useful when the input contains many duplicate values.

Its average time complexity is \(O(n\log n)\), while unfavorable partition behavior can still produce \(O(n^2)\) time. The implementation allocates new arrays, so it is not an in-place sort.

`flattenNested` recursively visits arrays and collects finite numeric leaves. It rejects strings, non-finite numbers, and other unsupported values instead of silently coercing them.

`deepFreezeCopy` recursively creates a copy and freezes the resulting objects. It demonstrates that recursive traversal can preserve the original object while creating an immutable snapshot. This is a shallow immutability mechanism for ordinary arrays and objects, not a universal deep-freezing solution for objects with special internal state, accessors, or cyclic references.

### Asynchronous dependency traversal

`fetchDependencyTree` models a service that retrieves dependencies asynchronously. Each node is fetched through a supplied asynchronous function, and independent children are traversed with `Promise.all`.

The function distinguishes unavailable dependencies from successfully loaded nodes. It also detects a cycle along the current path and represents the maximum depth explicitly.

Because each branch receives its own copied active-path set, a dependency shared by multiple branches is not automatically treated as a cycle. This distinction is necessary for directed acyclic graphs containing shared dependencies.

In production systems, recursive asynchronous traversal also needs request timeouts, cancellation, concurrency limits, maximum node counts, and protection against hostile or unexpectedly large graphs. A depth limit alone does not guarantee bounded total resource consumption.

## C++ case study: release build planning

The C++ program models a release pipeline in which services depend on other services.

The dependency graph contains a database, cache, identity service, API, and web application. Each component has a build duration and a list of direct dependencies.

### Critical-path calculation

`BuildPlanner::durationOf` calculates the longest accumulated build duration along any dependency path.

For a service \(v\), the recurrence is

\[
T(v)=d(v)+\max_{u\in D(v)}T(u)
\]

where \(d(v)\) is the service's build duration and \(D(v)\) is the set of its dependencies. If the dependency set is empty, the maximum contribution is zero.

This calculation estimates the critical path under a simplified model in which independent dependency builds can run in parallel. It is not the sum of every service's build duration and does not account for limited build agents, queueing, deployment approvals, or network delays.

The `memoizedDuration` map stores completed estimates. The `active` set identifies nodes currently being evaluated. Revisiting an active node indicates a dependency cycle, while revisiting a completed node can reuse its calculated result.

### Dependency-first build order

The second traversal uses three states: unseen, active, and completed. A service is added to the output order only after its dependencies have been processed. The resulting order therefore places each dependency before the service that requires it.

This ordering is useful for build systems, package installation, and deployment planning. The same graph structure can represent many different domains, but the meaning of the nodes and edges must remain explicit.

### Nested configuration and fast power

The `NestedValue` type distinguishes a numeric leaf from a group of nested values. `nestedSum` recursively aggregates all leaves, while `fastPower` demonstrates logarithmic recursion depth through exponentiation by squaring.

The power function intentionally documents its integer-overflow limitation. C++ signed integer overflow is not a safe substitute for arbitrary-precision arithmetic, so production code must validate multiplication bounds or use an appropriate checked or arbitrary-precision numeric type.

The dependency planner rejects duplicate services, missing dependency registrations, negative build durations, and cycles. These validations protect the assumptions required by its recursive algorithms.

## Java implementation: enterprise release planning

The Java program models the same general problem through explicit domain types, immutable records, and a planning service.

`Service` validates the component name and build duration. `List.copyOf` prevents callers from modifying the registered dependency list through the original mutable list.

`BuildReport` represents the output of planning as an immutable dependency-first order and a critical-path estimate. The planner owns the traversal state and cache instead of exposing those internal details to callers.

### Explicit traversal states

`ComponentState` defines `UNVISITED`, `VISITING`, and `COMPLETE`.

- `UNVISITED` means the service has not been explored.
- `VISITING` means the current recursion path includes the service.
- `COMPLETE` means its dependencies and duration have been calculated.

A transition from `VISITING` back to the same service signals a cycle. A completed service returns its cached duration, preventing repeated work when multiple services share a dependency.

`Math.addExact` detects integer overflow when combining build durations. The Fibonacci implementation uses `Math.addExact` and `Math`-based integer arithmetic to detect values that exceed the supported `long` range rather than silently returning corrupted results.

### Domain validation and failure behavior

The planner rejects unknown targets and missing dependency registrations. It also reports dependency cycles through a dedicated `DependencyCycleException`, allowing callers to distinguish graph errors from other argument errors.

The recursive methods are intentionally straightforward, but their stack usage remains proportional to the longest dependency chain. Very deep or externally supplied graphs may require an explicit stack-based traversal.

The enterprise-oriented design separates domain validation, graph traversal, and reporting. This makes it easier to test the algorithm and to connect the planning service to a larger build or deployment application.

## SQL implementation: recursive queries over service dependencies

The PostgreSQL script stores the dependency graph in relational tables and uses recursive common table expressions to traverse it.

### Relational model

The `services` table assigns each service a generated primary key, a unique name, a non-negative build duration, and an enabled flag.

The `service_dependencies` table represents directed edges. Its two foreign keys ensure that both endpoints exist, and its composite primary key prevents duplicate edges. A `CHECK` constraint prevents a service from directly depending on itself.

The reverse index on `(dependency_service_id, parent_service_id)` supports queries that begin with a dependency and identify its dependents. The primary key already supports lookups that begin with the parent service.

These constraints enforce local integrity, but they cannot prevent arbitrary multi-node cycles. Detecting those cycles requires examining paths through the graph.

### Recursive common table expressions

A recursive CTE has an anchor query and a recursive query. The anchor defines the starting row; the recursive term joins the current result to the next layer of related records.

The `dependency_walk` CTE starts at `web-app` and repeatedly follows dependency edges. It carries a path array so that a node already present on the current path can be recognized as a cycle.

The `reachable` CTE identifies dependencies reachable from the target and reports their minimum depth. `DISTINCT` removes duplicate nodes that are reachable through different paths, while the minimum depth identifies the shortest dependency distance.

### Critical-path estimation

The `paths` CTE accumulates build durations along dependency paths and returns the maximum accumulated duration.

This is a useful illustration of recursive aggregation, but enumerating all possible paths can become expensive in a graph with many branching dependencies. The query also imposes a depth bound and avoids revisiting nodes on the current path. Those controls protect against unbounded recursive expansion, although they do not replace application-level validation of the complete graph.

The script's self-dependency test demonstrates constraint enforcement. Its multi-node cycle query illustrates why graph-wide validation differs from row-level validation. A production system that must guarantee acyclic dependencies should perform cycle validation whenever edges are inserted or changed, using suitable transaction isolation or locking to prevent concurrent writes from introducing a cycle between individually valid transactions.

## Complexity and implementation trade-offs

| Algorithm | Time complexity | Auxiliary space | Important limitation |
|---|---|---|---|
| Factorial recursion | \(O(n)\) | \(O(n)\) | Linear call-stack depth |
| Naive Fibonacci | \(O(2^n)\) | \(O(n)\) | Repeated subproblems |
| Memoized Fibonacci | \(O(n)\) | \(O(n)\) | Cache and stack consume memory |
| Bottom-up Fibonacci | \(O(n)\) | \(O(1)\) | Requires iterative state updates |
| Recursive binary search | \(O(\log n)\) | \(O(\log n)\) | Input must be sorted |
| Merge sort | \(O(n\log n)\) | \(O(n)\) | Additional storage for merging |
| Quicksort with three-way partitioning | Average \(O(n\log n)\) | Input-dependent | Worst-case \(O(n^2)\) |
| Exponentiation by squaring | \(O(\log n)\) | \(O(\log n)\) | Numeric overflow or precision limits |
| Graph traversal with memoization | \(O(V+E)\) for a single full traversal of a graph | \(O(V)\) | Requires cycle handling and bounded input depth |

Here, \(V\) denotes the number of graph vertices and \(E\) the number of edges. The graph complexity assumes each vertex and edge is processed a bounded number of times. Algorithms that enumerate every path can have exponential output size even when the graph itself is relatively small.

## Common failure modes

**A missing or incorrect base case.** A recursive function may never terminate, or it may terminate with a mathematically incorrect result. Test the smallest valid inputs directly.

**A recursive argument that does not progress.** If the next call receives the same problem state, the function may repeat forever. Confirm that every recursive branch reduces a well-defined measure, such as remaining input length, interval width, or remaining depth.

**Repeated subproblem evaluation.** Naive Fibonacci illustrates how a compact recurrence can create exponential runtime. Use memoization or bottom-up dynamic programming when subproblems overlap.

**Uncontrolled recursion depth.** A linked structure, directory hierarchy, or dependency chain may be deeper than expected. Python has a recursion limit, Java and C++ can exhaust the call stack, and JavaScript engines may raise a maximum call-stack error. Increasing a recursion limit does not remove the underlying memory risk.

**Incorrect cycle detection.** Graph traversal must distinguish a node on the current path from a node already completed through another path. Treating every previously seen node as a cycle incorrectly rejects valid directed acyclic graphs with shared dependencies.

**Invalid input and arithmetic overflow.** Recursive definitions do not automatically make inputs safe. Validate numeric domains, detect overflow where the language supports it, and impose limits on externally controlled structures.

**Misleading performance measurements.** A benchmark can compare different algorithms only when they calculate equivalent results under comparable conditions. Runtime measurements should not be interpreted as universal complexity guarantees.

## Practical engineering implications

Recursion is particularly effective when the problem already has a hierarchical or self-similar structure: syntax trees, directory trees, nested configuration, dependency graphs, divide-and-conquer algorithms, and mathematical recurrences.

Its suitability depends on more than whether a recursive solution is elegant. Engineers must consider the maximum input depth, the number of repeated subproblems, the amount of temporary storage, numeric bounds, and whether the input can contain cycles.

Memoization is most useful when identical subproblems recur. It offers little benefit when every call processes a unique subproblem and can increase memory usage substantially. Iteration is often preferable when the problem has a simple state transition or when stack depth is unpredictable.

For production dependency planners, recursive algorithms should be paired with graph validation, explicit resource limits, observable failure states, and tests for cycles, missing nodes, shared dependencies, empty inputs, and unusually deep graphs. These controls preserve the correctness assumptions on which recursive decomposition depends.
