# Difference arrays

## Topic introduction

A difference array is a data structure technique for efficiently processing a large number of range addition updates.

Suppose an array contains:

`[10, 10, 10, 10, 10]`

and an operation says:

`add 5 to every element from index 1 through index 3`

A direct implementation changes three elements. If there are thousands or millions of such operations, repeatedly touching every element can become expensive.

A difference array changes the representation of the update. Instead of modifying every element in the target range, it records only where the change starts and where it stops.

For an inclusive range `[left, right]` and an addition of `value`:

`difference[left] += value`

`difference[right + 1] -= value`

A later prefix sum propagates the recorded change across the required range.

The central complexity improvement is:

- Direct range update: `O(length of range)`
- Difference-array update: `O(1)`
- Reconstruction after all updates: `O(n)`
- `q` updates followed by reconstruction: `O(n + q)`

This makes difference arrays particularly useful for offline or batch range-update problems.

---

## Fundamental terminology

### Array

An array stores values at indexed positions.

For example:

`A = [4, 7, 9, 9, 12]`

The valid indices are `0` through `4`.

### Range

A range identifies a consecutive group of positions.

An inclusive range `[1, 3]` contains indices:

`1, 2, 3`

A half-open range `[1, 4)` contains the same positions:

`1, 2, 3`

The two conventions must not be mixed accidentally.

### Range update

A range update modifies every element in a contiguous interval.

Examples include:

- add 10 to indices 2 through 8
- subtract 5 from indices 10 through 20
- increase server capacity during a group of deployment slots
- count how many intervals cover each time point

### Prefix sum

A prefix sum accumulates values from the beginning of a sequence.

For:

`[2, 3, 5, 1]`

the prefix sums are:

`[2, 5, 10, 11]`

Prefix sums are the mechanism that reconstructs the values represented by a difference array.

### Difference

A difference records the change between neighboring values.

For:

`[10, 13, 13, 20, 17]`

the difference array is:

`[10, 3, 0, 7, -3]`

The first element is retained because there is no previous element from which to calculate a difference.

---

## The mathematical model

For an array `A`:

`D[0] = A[0]`

and for `i > 0`:

`D[i] = A[i] - A[i - 1]`

To reconstruct `A`:

`A[i] = D[0] + D[1] + ... + D[i]`

Therefore, the original array and the difference array are inverse representations connected by prefix summation.

For:

`A = [10, 13, 13, 20, 17]`

the difference representation is:

`D = [10, 3, 0, 7, -3]`

Reconstruction gives:

- index 0: `10`
- index 1: `10 + 3 = 13`
- index 2: `10 + 3 + 0 = 13`
- index 3: `10 + 3 + 0 + 7 = 20`
- index 4: `10 + 3 + 0 + 7 - 3 = 17`

---

## Why two boundary changes are sufficient

Suppose an array receives:

`+5` on `[2, 5]`.

The update should affect:

`2, 3, 4, 5`

It should not affect:

`0, 1, 6, 7, ...`

The difference array records:

`D[2] += 5`

This causes the prefix sum to become 5 beginning at index 2.

To stop the effect after index 5:

`D[6] -= 5`

The prefix sum therefore behaves as follows:

- before index 2: no additional change
- indices 2 through 5: additional change of 5
- beginning at index 6: the `-5` cancels the earlier `+5`

This is the key mechanism behind the technique.

---

## The sentinel position

For an array of length `n`, a practical implementation normally creates a difference array of length `n + 1`.

The extra element is a sentinel.

For an update covering the complete array `[0, n - 1]`:

`D[0] += x`

`D[n] -= x`

Index `n` does not belong to the final array. It only marks the point where the effect would stop.

This avoids special-case logic for an update whose right endpoint is the last element.

Both the Python and C++ implementations use this technique. The JavaScript implementation also allocates `n + 1` positions and discards the sentinel after reconstruction.

---

## Basic Python implementation

The Python implementation begins with `build_difference_array()`.

The function calculates the difference between each value and its predecessor.

`reconstruct_from_difference()` performs the inverse operation by accumulating the difference values.

The important relationship is:

`reconstruct(build_difference_array(A)) == A`

The script asserts this relationship so that the implementation is checked rather than merely displayed.

---

## Python range updates

The function `range_additions_difference()` accepts:

- an initial array
- a collection of updates
- an inclusive left boundary
- an inclusive right boundary
- an amount to add

Each update requires only two modifications to the difference array.

For example:

`(1, 4, 3)`

means:

`A[1] += 3`

through:

`A[4] += 3`

The function then performs one reconstruction pass.

The resulting complexity is:

`O(q + n)`

where `q` is the number of updates and `n` is the array size.

---

## Naive versus difference-array processing

The Python file contains two implementations.

`range_additions_naive()` modifies every affected element.

`range_additions_difference()` modifies only two boundaries and reconstructs the result afterward.

The naive algorithm has worst-case complexity:

`O(nq)`

if every update covers nearly the entire array.

The difference-array algorithm has:

`O(q + n)`

complexity for a batch of updates.

The Python performance demonstration measures both approaches on moderate input sizes. Exact timings depend on the computer and Python runtime, so the important result is the asymptotic difference rather than a particular measured ratio.

---

## Difference arrays starting from zero

Many algorithmic problems begin with an array containing only zeroes.

For example:

`A = [0, 0, 0, 0, 0]`

In that case, the original array does not need to be converted into a difference array. The difference array can simply be initialized with zeroes.

For every update:

`D[left] += value`

`D[right + 1] -= value`

After all updates, a prefix sum generates the final array.

This is one of the most common forms of the difference-array technique.

---

## Point values after many updates

If the updates are processed first and only the final state is required, a difference array is highly effective.

After reconstruction, a particular point can be read directly in `O(1)`.

The Python function `final_point_values()` demonstrates this pattern.

If the complete final array is not required and the coordinate space is small, constructing the entire array may still be unnecessary. For very large sparse coordinate domains, coordinate compression is more appropriate.

---

## Difference arrays and prefix sums together

A difference array handles a batch of range additions.

After the final array has been reconstructed, a second prefix-sum array can support static range-sum queries.

For a prefix array `P`:

`sum(L, R) = P[R + 1] - P[L]`

This produces the following batch workflow:

`range updates`

→ `difference array`

→ `prefix reconstruction`

→ `final array`

→ `prefix sums`

→ `static range-sum queries`

This is useful when all updates occur before the queries.

It is not equivalent to a dynamic range-query data structure.

---

## When a difference array is not sufficient

A difference array is naturally designed for range addition.

It is not automatically suitable for every range operation.

For example, consider:

`set A[2..5] = 100`

This is assignment rather than addition.

If several assignments overlap, a simple pair of addition markers cannot preserve the overwrite semantics.

The Python implementation demonstrates a separate offline assignment technique using a disjoint-set structure. Assignments are processed from right to left so that each position is assigned only when its final value is known.

For dynamic workloads involving both updates and queries, other data structures may be more appropriate.

---

## Difference arrays versus related data structures

| Technique | Typical update | Typical query | Main use |
|---|---|---|---|
| Difference array | Range addition in `O(1)` | Final state after reconstruction | Offline batch updates |
| Prefix sum | Not designed for updates | Static range sum in `O(1)` | Immutable arrays |
| Fenwick tree | Dynamic aggregate operations | Dynamic prefix/range aggregate | Online workloads |
| Segment tree | Rich range operations | Rich range queries | Dynamic range problems |
| Lazy segment tree | Range updates | Range queries | Complex online range operations |
| Sweep line | Interval events | Event-based processing | Interval geometry and coverage |
| Coordinate compression | Sparse coordinate updates | Compressed segments | Huge coordinate domains |

The correct choice depends on whether operations are offline or online, which aggregate is required, and whether updates are additions, assignments, minimums, maximums, or more complex transformations.

---

## Interval coverage

Difference arrays can count how many intervals cover every coordinate.

Suppose the intervals are:

`[1, 4]`

`[2, 6]`

`[4, 5]`

Each interval contributes:

`+1` at its start

`-1` immediately after its end

After all markers are recorded, prefix accumulation gives the number of active intervals at each coordinate.

This is closely related to event sweeping.

The Python and JavaScript implementations include interval-coverage demonstrations.

---

## Event processing

An interval can also be represented with events.

For a half-open interval `[start, end)`:

`+1` occurs at `start`

`-1` occurs at `end`

Sorting event coordinates and maintaining an active count produces the number of simultaneously active intervals.

The half-open convention is useful because an interval ending at time `t` is no longer active at `t`, while another interval beginning at `t` can become active there.

The JavaScript function `maximumConcurrentIntervals()` demonstrates this event-processing model.

---

## Two-dimensional difference arrays

The same idea extends to matrices.

Suppose an update affects the rectangle:

`top <= row <= bottom`

and:

`left <= column <= right`

Four corner changes are sufficient:

`D[top][left] += x`

`D[bottom + 1][left] -= x`

`D[top][right + 1] -= x`

`D[bottom + 1][right + 1] += x`

The signs arise from two-dimensional inclusion-exclusion.

The final matrix is reconstructed with two-dimensional prefix accumulation.

For each cell:

`result[row][column]`

is based on:

- the current difference marker
- the cell above
- the cell to the left
- subtraction of the diagonally previous cell

This produces a two-dimensional analogue of the one-dimensional difference-array technique.

---

## Two-dimensional implementation

The Python function `rectangle_updates_2d()` uses a matrix with an additional sentinel row and column.

The JavaScript function `rectangleUpdates2D()` uses the same mathematical method.

The C++ class `GridDifferenceArray` encapsulates the technique and provides `addRectangle()` and `materialize()` methods.

The implementations demonstrate that the idea is not restricted to one-dimensional arrays.

The complexity for `q` rectangle updates on an `r × c` matrix is:

`O(q + rc)`

assuming all updates are applied before the matrix is reconstructed.

---

## Coordinate compression

Direct difference arrays require storage proportional to the coordinate domain.

Suppose an interval begins at:

`10`

and ends at:

`1,000,000,000`

Allocating one array element for every integer coordinate is usually inappropriate.

Coordinate compression stores only coordinates at which the accumulated value can change.

For intervals:

`[10, 1,000,000,000)`

`[500, 700)`

`[600, 900)`

the relevant coordinates are:

`10, 500, 600, 700, 900, 1,000,000,000`

The algorithm then operates on these compressed positions.

Sorting the coordinates costs:

`O(q log q)`

and the compressed scan is linear in the number of unique coordinates.

The Python, JavaScript, and C++ implementations demonstrate this technique.

---

## Discrete derivative interpretation

A difference array can be viewed conceptually as a discrete derivative.

For an array:

`A = [2, 2, 2, 7, 7, 4]`

the first differences identify where the values change.

The prefix sum is the corresponding accumulation operation that reconstructs the original sequence.

This viewpoint explains why boundary markers are powerful.

A range addition is a constant shift over an interval. Its discrete derivative therefore changes only at the beginning and end of that interval.

The analogy with calculus is useful for intuition, but a discrete difference array should not be treated as identical to continuous differentiation or integration.

---

## Second-order differences

A first-order difference array represents changes in the values.

A second-order difference array represents changes in the first differences.

For:

`D[i] = A[i] - A[i - 1]`

the second difference is:

`DD[i] = D[i] - D[i - 1]`

Second-order techniques become useful when updates themselves have structured changes, such as arithmetic progressions.

The Python implementation includes `second_difference()` and an arithmetic-progression range-update demonstration.

This extends the boundary-marker idea beyond constant range additions.

---

## Arithmetic-progression updates

A constant update has the form:

`x, x, x, x, ...`

An arithmetic-progression update has the form:

`x, x + d, x + 2d, x + 3d, ...`

A first-order difference array represents a constant range update efficiently because the update introduces only boundary changes in the first difference.

A second-order difference array can similarly represent a linear pattern with boundary changes.

The implementation illustrates the relationship between:

- values
- first differences
- second differences
- repeated prefix reconstruction

The main lesson is that higher-order difference arrays can represent progressively more structured range transformations.

---

## Python testing strategy

The Python implementation includes randomized differential testing.

The optimized algorithm is compared with a deliberately simple naive implementation.

Random cases vary:

- array length
- number of updates
- left endpoint
- right endpoint
- positive update values
- negative update values
- zero updates
- single-position updates
- complete-array updates

This is valuable because difference-array errors are frequently caused by boundary mistakes rather than by the central mathematical idea.

Typical errors include using `right` instead of `right + 1`, allocating too little storage for the sentinel, or mixing inclusive and half-open conventions.

---

## JavaScript implementation

The JavaScript file provides the same core mathematical technique while demonstrating JavaScript-specific implementation patterns.

`buildDifferenceArray()` constructs a first-order difference array.

`reconstructFromDifference()` performs prefix accumulation.

`rangeAdditions()` performs O(1) boundary updates.

JavaScript arrays are dynamically sized, making the sentinel representation straightforward.

The implementation also uses:

- `Map` for sparse event aggregation
- classes for the server-capacity model
- destructuring for interval data
- `Array.from()` for matrix construction
- `performance.now()` for timing
- explicit `RangeError` exceptions for invalid input

The code is executable in a modern Node.js runtime without external packages.

---

## JavaScript server-capacity case study

`ServerCapacityPlanner` models capacity changes across deployment slots.

A capacity change is represented as:

`[startSlot, endSlot, capacityChange]`

For example:

`[2, 6, 50]`

means that capacity increases by 50 for every slot from 2 through 6.

The class stores only boundary changes.

`buildCapacityProfile()` reconstructs the actual capacity profile.

`minimumCapacity()` identifies the smallest resulting capacity.

This models a practical batch-processing problem where infrastructure changes are known before the final capacity plan is generated.

---

## C++ case study

The C++ program develops an infrastructure capacity planner.

The modeled system has:

- deployment slots
- a base capacity
- scheduled capacity changes
- minimum-capacity constraints
- static aggregate queries

The `CapacityPlanner` class stores a difference array rather than modifying every deployment slot for every scheduled change.

The primary methods are:

- `schedule()`
- `capacityProfile()`
- `minimumCapacity()`
- `violatesMinimum()`

The design separates the update representation from the materialized result.

This is useful because the update phase can remain extremely cheap even when many ranges are involved.

---

## C++ data structures

The C++ implementation uses:

`std::vector`

for dense arrays and matrices.

`std::map`

for coordinate-compression lookup.

`std::tuple`

for compact interval records.

`std::pair`

for simple interval endpoints.

`std::mt19937`

for deterministic randomized testing.

`std::chrono`

for performance measurement.

The program uses `long long` through the `int64` alias for cumulative values.

This is important because range updates accumulate. Even when each individual update fits in a 32-bit integer, the total may exceed the 32-bit range.

---

## C++ validation

The C++ implementation rejects invalid ranges such as:

`left > right`

or:

`right >= array size`

It also validates rectangle boundaries and compressed intervals.

Exceptions such as `std::out_of_range` and `std::invalid_argument` communicate invalid input conditions.

The `main()` function catches standard exceptions and returns a non-zero exit status when execution fails.

This is more appropriate for production-style code than silently accepting invalid ranges.

---

## C++ capacity scenario

The case study applies three changes:

- an increased workload over a group of deployment slots
- an additional event-related capacity requirement
- a temporary reduction caused by maintenance

The program generates the final capacity profile and checks it against a safety threshold.

After materialization, `StaticRangeSum` constructs a prefix-sum index so a static aggregate such as the total capacity across slots `[4, 8]` can be obtained in constant time.

This demonstrates a useful composition:

`difference array`

→ `final state`

→ `prefix-sum index`

→ `static range queries`

---

## Why 64-bit arithmetic matters

Difference arrays can accumulate many updates.

Suppose each update adds:

`1,000,000`

and 100,000 overlapping updates affect the same position.

The accumulated value can reach:

`100,000,000,000`

which exceeds a signed 32-bit integer's maximum.

The C++ implementation therefore uses 64-bit integers for capacities and differences.

Python integers automatically expand to accommodate large integers.

JavaScript's ordinary `Number` type represents integers exactly only within its safe integer range. For applications involving values beyond that range, JavaScript's `BigInt` should be considered, with the limitation that `BigInt` and `Number` arithmetic cannot be freely mixed.

---

## Edge cases

Important cases include:

### Empty array

An empty input should produce an empty output without accessing index zero.

### One-element array

A complete update becomes:

`D[0] += x`

`D[1] -= x`

The second position is only the sentinel.

### Single-position update

For `[k, k]`:

`D[k] += x`

`D[k + 1] -= x`

Only one actual value changes.

### Complete-array update

For `[0, n - 1]`:

`D[0] += x`

`D[n] -= x`

The sentinel handles the endpoint cleanly.

### Negative updates

Subtraction is simply addition of a negative value.

### Zero updates

An update amount of zero does not change the result.

### Invalid ranges

`left > right` should normally be rejected unless the application explicitly defines another meaning.

### Large coordinates

Coordinate compression may be necessary when the coordinate domain is much larger than the number of relevant boundaries.

---

## Common mistakes

### Forgetting the ending marker

Writing:

`D[left] += x`

without:

`D[right + 1] -= x`

causes the update to continue beyond the intended range.

### Allocating only n positions

If `right` can equal `n - 1`, then `right + 1` equals `n`.

A sentinel requires `n + 1` positions.

### Mixing range conventions

An inclusive range `[L, R]` stops at `R + 1`.

A half-open range `[L, R)` stops at `R`.

Confusing these conventions creates off-by-one errors.

### Forgetting reconstruction

The difference array is not normally the final data array.

A prefix accumulation is required to materialize the values.

### Using the technique for the wrong workload

If an application needs an answer immediately after every update, repeatedly reconstructing the entire array can destroy the expected performance advantage.

### Ignoring integer overflow

This is particularly important in C++ and other fixed-width integer environments.

### Assuming assignment is addition

`A[i] += x` and `A[i] = x` have different semantics.

A normal difference array naturally represents the first operation, not arbitrary overlapping assignments.

---

## Inclusive and half-open ranges

The inclusive convention:

`[L, R]`

contains `R`.

Its difference marker is placed at:

`R + 1`

The half-open convention:

`[L, R)`

does not contain `R`.

Its ending marker is placed at:

`R`

Half-open intervals are particularly convenient for event processing and coordinate compression because adjacent intervals can share boundaries without overlap ambiguity.

A robust implementation should choose one convention and apply it consistently.

---

## Complexity analysis

For a one-dimensional difference array:

| Operation | Complexity |
|---|---:|
| Construct differences | `O(n)` |
| Record one range addition | `O(1)` |
| Record `q` range additions | `O(q)` |
| Reconstruct final array | `O(n)` |
| Updates plus reconstruction | `O(n + q)` |
| Access a value after reconstruction | `O(1)` |

For a two-dimensional difference array:

| Operation | Complexity |
|---|---:|
| Record one rectangle update | `O(1)` |
| Record `q` rectangle updates | `O(q)` |
| Reconstruct an `r × c` matrix | `O(rc)` |
| Complete process | `O(q + rc)` |

For coordinate compression:

| Stage | Complexity |
|---|---:|
| Collect coordinates | `O(q)` |
| Sort unique coordinates | `O(q log q)` |
| Apply compressed updates | `O(q)` |
| Scan compressed segments | `O(q)` |

The actual memory requirement is proportional to the representation being materialized.

---

## Performance considerations

The main performance advantage comes from avoiding repeated writes.

Suppose:

`n = 1,000,000`

and:

`q = 1,000,000`

If every update covers a large part of the array, a naive algorithm can approach one trillion element modifications.

A difference-array implementation records approximately two changes per update and performs one million reconstruction operations.

The asymptotic comparison is therefore approximately:

`O(nq)` versus `O(n + q)`

The exact runtime depends on hardware, language runtime, memory locality, integer representation, and implementation details.

The C++ implementation is particularly appropriate for large numerical workloads because contiguous `std::vector` storage provides efficient memory access and the compiler can optimize the simple prefix-sum loop effectively.

---

## Memory considerations

A one-dimensional difference array normally requires:

`n + 1`

elements when a sentinel is used.

A two-dimensional version requires approximately:

`(rows + 1) × (columns + 1)`

elements.

For very large matrices, memory consumption may become the limiting factor even though update processing itself is efficient.

Coordinate compression is an important optimization when coordinates are sparse.

It is also possible to process event streams without materializing a dense array when the application only requires intervals or segments where the value changes.

---

## Security considerations

Difference arrays are not inherently a security mechanism.

They are an algorithmic representation.

Security concerns arise from the surrounding application.

Relevant engineering considerations include:

- validate array sizes supplied by users
- reject negative or excessively large dimensions
- validate every range before indexing
- prevent integer overflow where fixed-width arithmetic is used
- impose reasonable limits on the number of updates
- avoid memory allocation based on untrusted enormous dimensions
- use coordinate compression for sparse but large coordinate domains
- handle malformed input without terminating unexpectedly
- avoid assuming that external input follows the expected range convention

In a network service, input validation and resource limits are particularly important because an attacker could attempt to force excessive CPU or memory consumption.

---

## Production implementation considerations

A production implementation should explicitly define:

- whether ranges are inclusive or half-open
- whether updates are additions, assignments, or another operation
- whether updates are offline or online
- numeric limits
- overflow behavior
- maximum array dimensions
- maximum update count
- whether the final state must be materialized
- whether queries occur before or after reconstruction

The mathematical technique should be selected according to the workload rather than used automatically.

For batch additions, difference arrays are simple and efficient.

For dynamic range updates combined with dynamic queries, a Fenwick tree, segment tree, or another specialized data structure may be more appropriate.

---

## Debugging strategy

When a difference-array result is incorrect, inspect the boundaries first.

For an update `[L, R] += X`, verify:

`D[L] += X`

and:

`D[R + 1] -= X`

Then inspect the prefix-sum reconstruction.

A useful debugging sequence is:

1. Test one update.
2. Test a single-element range.
3. Test a complete-array range.
4. Test two overlapping ranges.
5. Test adjacent ranges.
6. Test negative updates.
7. Compare against a naive implementation.
8. Use randomized differential tests.

The supplied Python and C++ implementations use this final approach.

---

## Randomized differential testing

For range algorithms, randomized testing is effective because it explores many combinations of boundaries.

The reference implementation intentionally uses the simpler algorithm.

For each generated test:

`optimized result == naive result`

must hold.

This can detect:

- incorrect sentinel handling
- incorrect endpoint calculations
- negative-update errors
- overlapping-update errors
- empty-array errors
- single-element errors

The Python implementation performs 300 randomized cases.

The C++ implementation performs 500 randomized cases.

The test data is deterministic because fixed random seeds are used, making failures reproducible.

---

## Design pattern

The general one-dimensional workflow is:

`Input array`

→ `difference representation`

→ `record range boundaries`

→ `prefix accumulation`

→ `final array`

For a zero-initialized array:

`zero difference array`

→ `record updates`

→ `prefix accumulation`

→ `final state`

For static range sums:

`difference updates`

→ `reconstruct`

→ `prefix sums`

→ `range-sum queries`

For a two-dimensional matrix:

`rectangle boundary markers`

→ `two-dimensional prefix accumulation`

→ `final matrix`

For sparse coordinates:

`interval boundaries`

→ `coordinate compression`

→ `compressed difference events`

→ `segment reconstruction`

---

## Python, JavaScript, and C++ comparison

### Python

Python is concise and well suited to expressing the underlying algorithm clearly.

The Python implementation emphasizes:

- readable functions
- validation
- reference implementations
- randomized testing
- coordinate compression
- two-dimensional updates
- higher-order differences

Python's arbitrary-precision integers are useful when numerical totals may become very large.

### JavaScript

JavaScript demonstrates the technique in a runtime commonly used for application and web development.

The implementation emphasizes:

- arrays
- `Map`
- classes
- event processing
- matrix operations
- runtime validation
- performance measurement

The JavaScript case study models server capacity changes using a class.

### C++

C++ demonstrates how the same algorithm can be incorporated into a strongly typed, performance-oriented system.

The implementation emphasizes:

- encapsulation
- `std::vector`
- 64-bit integers
- exception-based validation
- deterministic randomized testing
- performance measurement
- two-dimensional structures
- coordinate compression

The C++ capacity planner is designed as a small industry-style batch-processing component rather than as an isolated algorithm demonstration.

---

## Practical applications

Difference arrays and related boundary-event techniques appear in problems involving:

- server capacity planning
- traffic load estimation
- booking counts
- resource allocation
- interval coverage
- reservation occupancy
- CPU workload windows
- deployment schedules
- inventory adjustments
- batch pricing changes
- geographic grid updates
- image or matrix region modifications
- simulation workloads
- event accumulation
- time-window analytics
- competitive programming range-update problems

The common characteristic is a large number of operations affecting contiguous ranges.

---

## Important distinction: offline versus online processing

A difference array is particularly effective when updates can be accumulated before the final result is needed.

This is an offline or batch-processing pattern.

Consider:

`update`

`update`

`update`

`update`

`build final state`

This is ideal for a difference array.

A different workload looks like:

`update`

`query`

`update`

`query`

`query`

`update`

Here, rebuilding the entire array after each update may cost too much.

A dynamic data structure such as a Fenwick tree or segment tree may be more appropriate depending on the query type.

The distinction is fundamental when selecting an algorithm.

---

## Difference arrays as boundary events

A useful conceptual interpretation is that a range update is an event with two boundaries.

For:

`[L, R] += X`

there is:

`+X` at `L`

and:

`-X` at `R + 1`

The prefix sum turns these boundary events into an active interval.

This same pattern appears in:

- interval counting
- sweep-line algorithms
- scheduling
- capacity planning
- concurrency analysis
- event aggregation
- two-dimensional inclusion-exclusion

The technique is therefore broader than a single array trick. It is an efficient way of representing piecewise-constant changes.

---

## Limitations

A difference array does not eliminate the cost of materializing the final array.

If `n` is large, reconstruction still costs `O(n)`.

It also does not automatically provide complex dynamic queries.

The technique is most effective when:

- updates are additions
- updates are contiguous
- updates can be processed in a batch
- the final state can be reconstructed once

It becomes less suitable when:

- queries are interleaved with updates
- updates require arbitrary assignments
- minimum or maximum values are needed dynamically
- sophisticated range transformations are required
- the coordinate domain is huge and dense storage is impossible

In such cases, another data structure or a hybrid approach may be necessary.

---

## Core implementation rule

For an inclusive one-dimensional range:

`[left, right]`

with update:

`+value`

the essential rule is:

`difference[left] += value`

`difference[right + 1] -= value`

Then compute a prefix sum.

Everything else in the basic technique follows from this rule.

For a zero-based array of size `n`, allocate:

`n + 1`

difference positions when using the sentinel approach.

The result consists only of positions:

`0` through `n - 1`

The sentinel position exists solely to terminate the final update.

---

## Files in this implementation set

The Python implementation is a standalone educational program covering basic difference arrays, range updates, testing, two-dimensional extensions, coordinate compression, interval processing, and higher-order differences.

The JavaScript implementation provides executable demonstrations of the same fundamental mechanism and adds JavaScript-specific classes, maps, event processing, and a server-capacity planning example.

The C++ implementation presents an infrastructure capacity case study with classes, validation, 64-bit arithmetic, static queries, two-dimensional updates, coordinate compression, randomized verification, and performance measurement.

All three implementations use complete executable logic rather than pseudocode or unfinished sections.
