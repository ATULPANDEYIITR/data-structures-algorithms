# Backtracking Problems

This learning artifact implements backtracking as a family of constraint-search techniques rather than as a single algorithm. The source files cover subsets, permutations, combinations, N-Queens, Sudoku, and grid path-finding while keeping their state models and pruning rules distinct.

The central pattern is:

`choose -> validate constraints -> recurse -> undo choice`

A search tree is explored depth-first. Each recursive frame represents a partial solution. A branch is abandoned as soon as the partial state cannot lead to a valid result.

## Problem Models

| Problem | Search decision | State constraint | Typical output |
|---|---|---|---|
| Subsets | Include or exclude each item | Each item is considered once | `2^n` subsets |
| Permutations | Select one unused item for the next position | An item cannot be reused | `n!` permutations |
| Combinations | Select the next item after the previous index | Ordering is not significant | `C(n,k)` combinations |
| N-Queens | Place one queen in the next row | Columns and diagonals must remain unique | Valid boards |
| Sudoku | Assign a digit to an empty cell | Row, column, and 3×3 box constraints | Completed grid |
| Path finding | Move to an adjacent cell | Blocked and previously visited cells cannot be used | Valid paths |

The distinction is important. Subsets do not care about ordering, permutations do, combinations preserve selection without rearrangement, N-Queens uses geometric constraints, Sudoku uses local constraint sets, and path finding uses graph-like reachability with visited-state management.

## Search-State Design

A backtracking implementation is primarily defined by what it stores as mutable state.

For subset generation, the Python and JavaScript implementations maintain a `current` collection and an input index. The recursive decision is whether the current value participates in the subset.

For permutations, a `used` array or equivalent set records which input positions have already been selected. The next recursion level chooses one unused position.

For combinations, the recursion carries a `start` index. Every subsequent choice must have a larger index, preventing the generation of `[2, 1]` after `[1, 2]`.

For N-Queens, the state is compressed into three constraint sets:

- Occupied columns
- `row - column` diagonal identifiers
- `row + column` diagonal identifiers

This avoids scanning every previously placed queen before every candidate placement.

Sudoku maintains three groups of constraint sets for rows, columns, and 3×3 boxes. The implementations also use a minimum-remaining-values strategy: among unfilled cells, they select the cell with the fewest legal candidates first. This can dramatically reduce the search tree compared with filling cells in fixed row-major order.

Path finding maintains a visited structure because a graph search can otherwise revisit the same cells indefinitely. The current path is mutated as the recursion enters and leaves each cell.

## Python Implementation

The Python program is a self-contained executable case study using only the standard library.

It provides:

- Ordinary subset generation
- Duplicate-aware subset generation
- Permutation generation
- Duplicate-aware permutation generation
- Fixed-size combinations
- N-Queens
- Validated 9×9 Sudoku solving
- Bounded grid path enumeration
- Single-path maze solving

Python lists represent the current partial state, while sets provide efficient membership checks for constraints. The Sudoku solver uses candidate-count ordering rather than blindly selecting the next empty position.

The path finder accepts a `max_paths` limit. This is important because enumerating all simple paths can become extremely expensive even for modest grids.

Input validation is performed before recursive processing. Invalid dimensions, malformed Sudoku values, non-rectangular grids, invalid coordinates, and unsafe path limits are rejected instead of producing ambiguous failures.

## JavaScript Implementation

The JavaScript implementation emphasizes complementary runtime behavior.

Generators are used for subsets, permutations, and combinations. A generator allows the caller to consume results incrementally instead of requiring every solution to be stored simultaneously. This matters for exponential result spaces.

The Sudoku and N-Queens implementations use ordinary recursive functions because their result sets are intentionally collected for the demonstration.

The asynchronous maze wrapper uses a promise and an event-loop yield before performing the bounded search. The underlying search remains synchronous, but the public wrapper demonstrates how an application can place expensive search work behind an asynchronous interface.

JavaScript `Set` objects provide constant-average-time membership checks for constraint state. Input validation prevents malformed arrays and invalid Sudoku domains from reaching the recursive search.

## C++17 Implementation

The C++ program treats backtracking as a reusable search engine implemented through static operations and strongly typed structures.

The implementations use:

- `std::vector` for dynamic search state
- `std::array` for the fixed 9×9 Sudoku domain
- `std::unordered_set` for N-Queens constraints
- `std::vector<bool>` for compact visited state
- Recursive `std::function` closures for search operations
- Explicit validation and bounded results for safe search execution

The Sudoku solver uses bit masks. Each digit occupies one bit in a row, column, or box mask. Candidate calculation therefore becomes a small number of bit operations instead of repeated set construction.

The path model uses a typed `Position` structure. A path is represented as an ordered vector of positions, and a maximum path count prevents accidental memory growth during exhaustive enumeration.

The C++ implementation demonstrates a useful systems-level trade-off: recursive search can be computationally efficient when state is represented compactly, but result materialization can still dominate memory when the number of solutions is large.

## Java 17 Implementation

The Java implementation uses explicit domain types and immutable result boundaries.

`Position` and `RepositoryPath` are records, making coordinate and path objects value-oriented and immutable after construction. Search state remains mutable internally, while returned solutions use immutable list copies.

The Sudoku solver uses `Set<Integer>` structures for rows, columns, and boxes and selects the unfilled cell with the smallest candidate set.

The N-Queens solver explicitly models columns and both diagonal identifiers. This makes the geometric constraints visible in the domain implementation instead of hiding them behind a generic conflict check.

The program also contains a small enterprise-style workflow object that evaluates whether a search scenario satisfies basic operational gates. It illustrates the same design principle used by larger services: domain state should expose meaningful predicates rather than forcing application code to reconstruct rules from primitive fields.

## PostgreSQL Model

The SQL artifact represents backtracking workloads as persistent search records.

The relational model separates:

- Problem types
- Individual problems
- Search executions
- Solution records
- Sudoku puzzles
- N-Queens boards
- Grid maps
- Grid paths
- Validation events

`problem_types` distinguishes subsets, permutations, combinations, N-Queens, Sudoku, and path finding without collapsing their different semantics into a generic label.

`search_runs` records the algorithm, execution state, nodes explored, number of solutions, and execution timestamps.

`solution_sets` stores individual search results as `JSONB`. This is appropriate for heterogeneous result structures because a subset, a queen placement, and a path do not share the same relational shape.

The specialized tables retain stronger structure where it matters. Sudoku uses a two-dimensional integer array, N-Queens stores queen-column assignments, and grid maps store their dimensions and cells.

The database uses:

- Primary keys
- Foreign keys
- Uniqueness constraints
- Domain checks
- Indexes for repeated search-run and validation queries
- Triggers for aggregate solution counts
- PL/pgSQL validation for grid-path coordinates
- Transactional insertion
- Common table expressions
- Reporting queries
- A search eligibility view

The path trigger prevents coordinates outside the associated grid and ensures that the declared path length agrees with the number of stored coordinates. This moves an important integrity rule from application code into PostgreSQL.

## Duplicate Handling

Duplicate values change the search tree.

For example, ordinary permutations of `[1, 1, 2]` treat the two positions containing `1` as separate choices and therefore generate duplicate value sequences.

The duplicate-aware implementation sorts the values first and skips an equal value when its preceding equal value has not been used at the current recursion depth.

The same principle applies to unique subsets. Equal values are skipped when they occur at the same depth, while equal values may still be selected at deeper levels when that represents a legitimate multiplicity.

This is different from simply placing every result into a set after generation. Early duplicate pruning avoids unnecessary recursive work.

## Pruning

Pruning is the main performance mechanism in constraint-based backtracking.

A branch should be rejected as soon as its partial state violates a rule.

For N-Queens:

- `occupied column -> reject`
- `occupied row-column diagonal -> reject`
- `occupied row+column diagonal -> reject`

For Sudoku:

- `digit already in row -> reject`
- `digit already in column -> reject`
- `digit already in box -> reject`

For grid paths:

- `outside grid -> reject`
- `blocked cell -> reject`
- `already visited -> reject`

The earlier a constraint is evaluated, the smaller the remaining search tree can become.

## Complexity

Backtracking is usually exponential or factorial because it explores combinations of decisions.

| Problem | Approximate worst-case growth |
|---|---|
| All subsets | `O(2^n)` results |
| All permutations | `O(n!)` results |
| k-combinations | `O(C(n,k))` results |
| N-Queens | Exponential/factorial-style search with strong pruning |
| Sudoku | Exponential in the number of unresolved cells in the worst case |
| Simple grid paths | Potentially exponential in the number of traversable cells |

These bounds describe search growth rather than only arithmetic operations. Copying each solution also contributes output-dependent cost.

The important practical distinction is between **search complexity** and **result complexity**. A solver may find one answer quickly because it can stop after the first successful branch, while enumerating every answer can remain prohibitively expensive.

## Failure Conditions

The implementations explicitly handle several invalid states.

A subset or permutation input containing null-like values is rejected where the language representation makes that meaningful.

A permutation function that assumes distinct values rejects duplicate input when uniqueness is part of its contract. A separate unique-permutation algorithm exists when duplicates are legitimate input.

Sudoku validates dimensions and digit ranges and detects duplicate values in initial rows, columns, and boxes.

Grid algorithms validate rectangular dimensions and coordinate bounds. Blocked start or target cells immediately produce no paths.

N-Queens rejects non-positive board sizes.

Path enumeration is bounded by a caller-supplied maximum result count. This prevents a valid but extremely large result set from consuming uncontrolled memory.

## Backtracking Workflow

    Initial state
         |
         v
    Choose a candidate
         |
         v
    Does the partial state satisfy constraints?
         |                     |
        no                    yes
         |                     |
       prune                    v
                             Recurse
                                |
                                v
                         Complete solution?
                           |          |
                          no         yes
                           |          |
                        continue    record
                           |
                           v
                     Undo the choice
                           |
                           v
                    Try next candidate

The undo operation is essential. The recursive call temporarily owns a change to shared state, and the caller must restore that state before exploring a sibling branch.

## N-Queens Representation

A board can be represented visually as rows of characters, but conflict detection is better represented through sets.

For a queen at `(row, column)`:

- Column conflict is identified by `column`.
- One diagonal is identified by `row - column`.
- The other diagonal is identified by `row + column`.

Therefore a candidate position is legal only when all three identifiers are unused.

This reduces conflict checking from scanning previously placed queens to a small number of membership tests.

## Sudoku Representation

Sudoku has a fixed domain of digits from 1 through 9.

For each empty cell, legal candidates are:

`{1..9} - row_values - column_values - box_values`

The minimum-remaining-values heuristic selects the cell with the smallest candidate set. A cell with one candidate should be explored before a cell with six candidates because it introduces less branching.

The solver mutates the board during recursion and restores an unsuccessful assignment to zero during backtracking.

## Path-Finding Representation

The grid uses:

- `0` for traversable cells
- `1` for blocked cells

The search moves vertically and horizontally. Diagonal movement is intentionally excluded.

The visited matrix or set prevents cycles. A cell is marked when entered and unmarked when the recursive branch returns. This means the same cell can participate in different candidate paths while never appearing twice in one simple path.

The `max_paths` limit is an operational control rather than a mathematical constraint. It allows applications to request a bounded sample of paths without forcing complete enumeration.

## Production Considerations

Backtracking is appropriate when the search space is manageable or when strong constraints prune most branches. It becomes unsuitable when the state space grows too rapidly and no effective pruning or alternative formulation exists.

For production systems:

- Validate input before recursion.
- Establish explicit result limits.
- Avoid storing all solutions when streaming is possible.
- Use constraint propagation before branching.
- Select highly constrained variables first.
- Measure nodes explored, not only elapsed time.
- Preserve deterministic ordering when reproducibility matters.
- Protect recursive depth when inputs can be attacker-controlled.
- Avoid accepting unrestricted dimensions for computationally expensive problems.
- Distinguish “no solution” from invalid input.
- Enforce persistent data integrity in the database when the rule is structural.

A solver that returns the correct answer but allows uncontrolled input size can still be operationally unsafe.

## Learning Focus

The five implementations expose the same underlying search discipline through different technical perspectives:

| Implementation | Primary perspective |
|---|---|
| Python | Algorithmic modeling, validation, and standard-library data structures |
| JavaScript | Generator-based result consumption and asynchronous application boundaries |
| C++17 | Compact state representation, bit masks, and typed search structures |
| Java 17 | Explicit domain modeling, immutable results, and enterprise-oriented validation |
| PostgreSQL | Persistent problem state, execution auditing, integrity constraints, triggers, and reporting |

The important transferable concept is not the recursive syntax itself. It is the design of a correct search state, the definition of a valid partial solution, and the ability to undo a decision precisely before exploring the next branch.
