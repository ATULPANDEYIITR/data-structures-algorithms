# Recursion Trees

## Purpose

A recursion tree represents the execution structure of a recursive algorithm. Each node corresponds to one recursive call, and each child corresponds to a recursive call made by that parent.

The useful information is not simply that an algorithm is recursive. A recursion tree exposes:

- How many recursive branches each call creates.
- How quickly the input or state becomes smaller.
- How much work is performed at each node.
- How deep the recursion becomes.
- How many terminal calls exist.
- Whether different branches evaluate the same state.
- How the work accumulated across the tree relates to a recurrence.

The implementations use different technical perspectives. Python builds and analyzes explicit execution trees, JavaScript combines tree modeling with event-driven and asynchronous recursion, C++ models recursive execution as a validation-system case study, Java represents recursive execution using an enterprise-style domain model, and PostgreSQL stores recursive call relationships for database-level analysis.

---

## Core Recursion-Tree Model

A recursive call can be represented as a node:

`T(n)`

If that call invokes two smaller problems, its children might be:

`T(n - 1)` and `T(n - 2)`

The resulting structure is:

    T(n)
    ├── T(n-1)
    │   ├── ...
    │   └── ...
    └── T(n-2)
        ├── ...
        └── ...

The tree gives a concrete interpretation of a recurrence. Instead of seeing only `T(n) = T(n-1) + T(n-2) + O(1)`, the tree makes the recursive branches and their repeated descendants visible.

A useful analysis separates three properties:

| Property | What the tree reveals |
|---|---|
| Branching | How many recursive calls each node creates |
| Shrinking | How rapidly each child problem becomes smaller |
| Local work | The non-recursive work performed by a call |

The total work depends on the combination of these properties.

---

## Balanced, Single-Branch, and Overlapping Recursion

Recursion trees do not all have the same shape.

### Balanced Divide-and-Conquer

Merge sort creates two approximately equal subproblems:

`T(n) = 2T(n/2) + O(n)`

At each level, the number of nodes increases while the amount of data represented by each node decreases. The height is logarithmic because repeated halving eventually reaches single-element inputs.

The aggregate merge work at a level remains proportional to `n`. With approximately `log₂ n` levels, the total work is `O(n log n)`.

The Python and C++ implementations explicitly construct merge-sort trees and attach local costs to internal nodes. This makes it possible to calculate both tree structure and accumulated work.

### Single-Branch Recursion

Binary search follows:

`T(n) = T(n/2) + O(1)`

Only one recursive branch survives at each call. The recursion tree therefore resembles a path rather than a wide binary tree.

A recursive execution with one child per call is still a tree of calls.

The Python, C++, Java, and SQL implementations include this shape to contrast it with branching recursion.

### Overlapping Recursive Subproblems

Naive Fibonacci follows:

`T(n) = T(n-1) + T(n-2) + O(1)`

The tree contains the same states repeatedly. For example, calculating `fib(6)` reaches `fib(4)` through more than one branch.

This repetition is fundamentally different from ordinary branching. The tree shows that the algorithm is recomputing states rather than merely processing distinct subproblems.

Memoization stores the result of a state and reuses it when that state appears again. The effective computation becomes closer to a directed state graph than a fully expanded recursive tree.

---

## Python Implementation

The Python program uses the `CallNode` data class as an explicit representation of a recursive execution node.

Each node stores:

- The operation name.
- Its arguments.
- Its result.
- Local work cost.
- Child calls.

This makes recursion observable rather than leaving the call structure only on the Python call stack.

### Fibonacci

`fibonacci_tree()` recursively creates both `fib(n - 1)` and `fib(n - 2)` children. The resulting tree can be measured with `tree_height()`, `count_nodes()`, `count_leaves()`, and `sum_cost()`.

The tree exposes the source of Fibonacci's rapid growth directly: each internal call creates two branches, and many of those branches reach the same states.

### Merge Sort

`merge_sort_tree()` records the division of an input array into two ranges and assigns the size of the current range as the node's local merge cost.

This represents the recurrence more accurately than simply printing `O(n log n)`, because the program can aggregate local work over the actual tree.

### Exponentiation

The Python file compares two recursive exponentiation strategies.

`naive_power()` reduces the exponent by one:

`T(n) = T(n - 1) + O(1)`

`fast_power()` uses exponentiation by squaring. It recursively evaluates roughly half the exponent and then squares the result:

`T(n) = T(floor(n/2)) + O(1)`

This produces logarithmic recursion depth.

### Memoization

The Fibonacci memoization example demonstrates a key limitation of reading only the tree shape. A fully expanded Fibonacci tree counts every repeated computation separately. Memoization changes the execution by storing previously computed states.

The Python program records both naive recursive calls and memoized calls so the difference can be measured rather than described abstractly.

### Visualization

`tree_to_dot()` converts an execution tree into Graphviz DOT syntax. The generated representation includes node labels, results, local costs, and parent-child edges.

The visualization is produced as data without requiring an external Python package.

---

## JavaScript Implementation

The JavaScript program uses a `CallNode` class similar in purpose to the Python tree model, but the implementation emphasizes JavaScript execution patterns.

### Event-Driven Recursion Tracing

`traceRecursiveFibonacci()` accepts entry and exit callbacks.

A call-entry event represents the moment a recursive invocation begins. A call-exit event represents the point where its result has been computed.

This distinction matters for an execution visualizer because a recursion tree alone does not capture the temporal order of stack entry and return.

### Asynchronous Recursion

`asynchronousTree()` demonstrates recursive branching with Promises.

Each non-terminal node creates two asynchronous child operations. `Promise.all()` waits for both branches while allowing them to proceed independently.

This provides a useful distinction between a synchronous recursion tree and an asynchronous execution structure. The tree represents logical dependency, while event timing determines when individual branches actually complete.

### Quicksort

The JavaScript implementation uses a quicksort tree rather than reproducing the Python merge-sort example.

The final array element is selected as the pivot. Values are partitioned into two groups, and each group becomes a recursive child.

The resulting tree can be balanced or highly skewed depending on the input and pivot choices. This demonstrates why quicksort's recursion depth depends on partition quality.

### Mermaid Output

`toMermaid()` converts the tree into Mermaid graph syntax. This is useful when the recursive structure needs to be consumed by a browser-based visualization system.

---

## C++ Case Study

The C++ program models a recursive validation pipeline for a release candidate.

A validation stage can recursively create two independent child stages, such as compilation and integration validation. The `ExecutionNode` structure stores the stage, state, local cost, and child nodes.

This produces a realistic recursive workload rather than treating recursion as an isolated mathematical exercise.

### Recursive Validation Tree

`buildStageTree()` creates a binary validation tree.

At depth zero, the node is terminal. At greater depth, the stage creates two independent recursive validation branches.

The program calculates:

- Tree height.
- Total nodes.
- Terminal nodes.
- Accumulated local cost.

These metrics correspond directly to execution characteristics of the recursive validation process.

### Merge-Sort Analysis

The C++ program uses `mergeSortTree()` to show how local work varies by level.

The node covering a larger range receives a larger local cost because merging that range touches more elements. The accumulated cost therefore reflects the `O(n)` work associated with each merge level.

### Memoized State Reuse

The C++ Fibonacci implementation uses `std::map` as a cache.

The raw recursion tree contains repeated states. The memoized function stores the result associated with each integer state and avoids recomputing an already known value.

The program reports both invocation count and the number of unique cached states.

### Binary Search

`binarySearchTree()` demonstrates a one-child recursion tree. The search interval is halved at every step, but only one child is created.

This makes the implementation useful for comparing:

`T(n) = T(n/2) + O(1)`

with the two-branch merge-sort recurrence.

---

## Java Enterprise-Oriented Model

The Java program represents recursive validation as a domain model.

`ValidationState` provides explicit states such as `PENDING`, `PASSED`, and `FAILED`. `ValidationResult` is an immutable record containing the stage, state, local cost, and explanation.

`ExecutionNode` owns a validation result and its child executions.

The explicit domain types make the recursive structure easier to reason about than a collection of loosely related strings and counters.

### State Validation

The Java implementation rejects invalid validation costs and blank state identifiers through constructor and method validation.

`ExecutionNode.addChild()` also prevents a completed validation node from receiving additional recursive work.

This illustrates an important production concern: recursive state should have explicit validity rules rather than relying entirely on callers to preserve invariants.

### Recursive Analyzer Interface

`RecursiveAnalyzer` separates the concept of constructing a recursive validation tree from the specific implementation.

`ReleaseValidationAnalyzer` implements the interface and creates compilation and integration branches.

This gives the recursion mechanism a clear domain boundary and allows the execution tree to be treated as a persistent analysis structure.

### Memoization

`MemoizedFibonacci` uses a `HashMap<Integer, Long>` to associate a recursive state with its previously computed value.

The cache demonstrates that memoization changes the number of actual computations even though the mathematical recurrence remains unchanged.

---

## PostgreSQL Data Model

The SQL implementation stores recursion trees as relational data.

The main entities are:

- `algorithms`, which identifies the recurrence being studied.
- `executions`, which identifies an execution of an algorithm.
- `call_nodes`, which stores individual recursive calls.
- `recurrence_states`, which stores reusable states and computation counts.

### Parent-Child Representation

`call_nodes.parent_node_id` points back to another `call_nodes.node_id`.

A root call has no parent. Recursive children point to the node representing their parent call.

The foreign key is declared as deferrable because recursive structures can require parent-child rows to be assembled within a transaction.

### Constraints

Database constraints enforce structural validity:

- Execution identifiers must reference real executions.
- Recursion depth cannot be negative.
- Local cost cannot be negative.
- Call sequence values must be positive.
- Execution status is restricted to valid states.
- A completed execution cannot have a completion time earlier than its start time.

These rules prevent malformed recursion measurements from entering the database.

### Recursive CTE

The `call_tree` common table expression reconstructs the recursive structure from relational parent-child rows.

The recursive member joins a child node to its parent and carries the path forward.

This makes SQL capable of traversing the execution tree without requiring the entire structure to be loaded into application memory.

### Level-Based Analysis

Grouping recursive nodes by depth exposes work performed at each level.

For divide-and-conquer algorithms, this is particularly useful because the total work can often be understood by examining the cost contributed by each level.

### Branching Analysis

The child-count query measures the number of recursive children produced by each call.

A node with two children represents binary branching. A node with one child represents a single surviving recursive path. A terminal node has zero children.

### Repeated-State Analysis

`recurrence_states` records how frequently a state is computed.

A state with a computation count greater than one represents duplicated recursive work. Such states are candidates for memoization or dynamic programming.

---

## Recursion-Tree Analysis Workflow

A practical analysis starts with the recurrence's actual execution structure.

| Question | Tree interpretation |
|---|---|
| How many children does each call create? | Branching factor |
| How much smaller is each child problem? | Tree height |
| How much work occurs before recursive calls? | Node-local cost |
| Do branches reach identical states? | Overlapping subproblems |
| Does only one child continue? | Single-path recursion |
| Do child sizes remain balanced? | Divide-and-conquer balance |
| How many terminal calls occur? | Number of leaves |
| What is the sum of all node costs? | Total recursive work |

This structure connects implementation behavior with recurrence analysis.

---

## Recursion Trees and Big-O Reasoning

For a recurrence such as:

`T(n) = 2T(n/2) + cn`

the tree has approximately `2^k` nodes at level `k`, while each node handles roughly `n / 2^k` units of input.

The work at one level is therefore approximately:

`2^k × c(n / 2^k) = cn`

The number of levels is approximately `log₂ n`, producing:

`O(n log n)`

For:

`T(n) = T(n/2) + c`

there is approximately one node per level. The height is `O(log n)`, so the total work is also `O(log n)`.

For:

`T(n) = T(n-1) + c`

there is one child, but the problem shrinks by only one unit. The height becomes `O(n)`.

For:

`T(n) = T(n-1) + T(n-2) + c`

the tree branches while shrinking slowly. Repeated states create a large amount of duplicate work, producing exponential growth in the naive implementation.

---

## Tree Height Versus Total Work

Recursion depth and total execution cost are different measurements.

An algorithm can have logarithmic depth but still perform substantial work at each level.

Merge sort is a typical example:

- Recursion depth is `O(log n)`.
- Work per level is `O(n)`.
- Total work is `O(n log n)`.

Binary search has:

- Recursion depth of `O(log n)`.
- Constant work per call.
- Total work of `O(log n)`.

This distinction matters in production because stack usage is primarily related to recursion depth, while CPU time depends on the aggregate work represented by the entire tree.

---

## Common Mistakes

### Counting Only the Root

The root represents one invocation, not the complete recursive workload. Recursive children must be included when estimating total execution cost.

### Assuming Every Recursion Tree Is Binary

Some recursive algorithms create one child, many children, or a variable number of children. The tree shape must come from the actual recursive calls.

### Confusing Recursion Depth With Complexity

A recursion depth of `O(log n)` does not automatically mean `O(log n)` time. Each node can perform substantial work.

### Ignoring Overlapping States

A large Fibonacci tree contains many repeated states. Counting every repeated state as a distinct computation explains naive execution but hides the effect of memoization.

### Assuming Balanced Splitting

Divide-and-conquer analysis often depends on balanced subproblems. Quicksort can produce a much deeper tree when partitions are highly unbalanced.

### Treating Memoization as a Tree Property

A memoized algorithm no longer behaves like a fully expanded tree because repeated states share stored results. The execution is better understood as a state graph with cached transitions.

---

## Performance Considerations

A recursion tree is useful for reasoning, but explicitly constructing the entire tree can consume substantial memory.

For Fibonacci, the number of nodes in the naive tree grows rapidly. Building the complete tree can therefore be much more expensive than simply computing the final result.

Production tracing systems should often use bounded depth, sampling, streaming events, or aggregation rather than retaining every call indefinitely.

For divide-and-conquer algorithms, tree metrics can often be computed without storing every node. If only height, total cost, or a recurrence estimate is required, a compact accumulator may be preferable.

Recursive depth also matters independently of time complexity. A linear-depth recursion can exhaust the runtime call stack even when each call performs very little work.

---

## Debugging and Visualization

A recursion tree is particularly useful when debugging:

- Unexpected branching.
- Repeated work.
- Incorrect base cases.
- Missing termination conditions.
- Unexpectedly deep recursion.
- Unbalanced divide-and-conquer behavior.
- Incorrect propagation of child results.

The Python implementation produces a Graphviz-compatible representation. The JavaScript implementation produces Mermaid-compatible graph syntax and also exposes entry and exit events.

An execution visualizer can distinguish between two concerns:

**Logical structure:** recursion tree.

**Temporal behavior:** call-entry and call-exit events.

The distinction becomes especially important for asynchronous recursion, where logical parent-child relationships do not necessarily imply sequential completion.

---

## Practical Relationship Between Implementation and Recurrence

The recurrence should describe the behavior actually represented by the implementation.

If a function creates two recursive calls on half-sized inputs and performs linear work while combining their results, the implementation supports a recurrence resembling:

`T(n) = 2T(n/2) + O(n)`

If a function creates only one recursive call on half the input and performs constant local work, the implementation supports:

`T(n) = T(n/2) + O(1)`

If two calls reduce the state by one and two respectively, the structure resembles:

`T(n) = T(n-1) + T(n-2) + O(1)`

The recursion tree acts as the bridge between source-code behavior and asymptotic analysis.
