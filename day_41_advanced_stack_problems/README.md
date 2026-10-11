# Advanced Stack Problems

## Scope

This module focuses on advanced applications of stacks where the stack stores unresolved relationships rather than merely acting as a last-in, first-out container.

The central technique is the **monotonic stack**. A monotonic stack maintains elements in increasing or decreasing order so that each input element is pushed and removed only a bounded number of times. This produces linear-time algorithms for problems that appear to require repeated searching.

The implementations cover:

- Largest rectangle in a histogram
- Trapping rainwater
- Stock span
- Next greater and previous smaller relationships
- Expression conversion and postfix evaluation
- Daily temperature waits
- Sum of subarray ranges
- Maximum rectangle in a binary matrix

The Python implementation emphasizes algorithmic construction, validation, testing, and diagnostics. The JavaScript implementation models stack processing with JavaScript collections, generators, maps, and an event-oriented execution model. The C++ implementation presents the algorithms as components of a capacity and analytics system. The Java implementation uses explicit domain types, records, enums, interfaces, collections, and service-style abstractions. The SQL implementation expresses the same problem domain through relational structures and analytical queries.

## Why Advanced Stack Problems Matter

A basic stack answers a structural question: which item was inserted most recently?

Advanced stack algorithms answer a different class of question: which earlier item remains relevant when a new item arrives?

For example, when processing a histogram from left to right, a bar remains on a monotonic stack while no later bar has yet established a smaller boundary. When a smaller bar appears, the stack reveals exactly which bars have just acquired their right boundary.

This is the source of the efficiency of the largest-rectangle algorithm.

A similar mechanism appears in:

- stock span, where a greater historical price becomes a boundary;
- next greater element, where a newly arriving value resolves previously unresolved elements;
- daily temperatures, where a warmer day resolves earlier temperatures;
- rainwater trapping, where a newly encountered wall closes a bounded region;
- subarray range calculations, where monotonic boundaries determine how many subarrays treat an element as a minimum or maximum.

The stack is therefore storing unresolved relationships, not simply data.

## Monotonic Stack Mechanics

A monotonic increasing stack keeps its stored values in increasing order. Before inserting a new value, elements that violate the ordering are removed.

A monotonic decreasing stack performs the opposite operation.

The important property is amortized complexity. An element can be pushed onto the stack once and popped at most once. Although an individual iteration can contain multiple pops, the total number of pops across the entire input is at most the number of pushes.

This gives an O(n) total running time for many algorithms.

The stack normally stores indices rather than values. Indices provide access to both the original value and its position. They also make width calculations possible.

## Largest Rectangle in a Histogram

A histogram contains bars with a height and an implicit width of one.

The problem is to find the largest contiguous rectangle that can be formed from those bars.

For the histogram `[2, 1, 5, 6, 2, 3]`, the optimal rectangle uses the bars with heights `5` and `6`. Its limiting height is `5`, its width is `2`, and its area is `10`.

The monotonic-stack implementation in the Python, JavaScript, C++, and Java files uses an artificial zero-height bar at the end. This sentinel forces every remaining candidate to be resolved without requiring a separate cleanup algorithm.

When a smaller height arrives, the popped bar has just discovered its first smaller bar on the right. The new stack top identifies the nearest smaller boundary on the left.

The resulting width is:

`right_boundary - left_boundary - 1`

The Python implementation also returns the coordinates and height of the selected rectangle, making the algorithm useful for diagnostics rather than returning only an area.

### Complexity

The histogram algorithm runs in O(n) time and uses O(n) auxiliary stack space.

A brute-force implementation can inspect many overlapping intervals and degrade to O(n²) or worse depending on how minimum heights are computed. The monotonic stack avoids that repeated work.

## Trapping Rainwater

The rainwater problem asks how much water remains between elevation bars after rainfall.

The key constraint is that water at a position is limited by the smaller of the highest boundary on its left and the highest boundary on its right:

`water[i] = max(0, min(left_max, right_max) - height[i])`

The Python implementation contains both a monotonic-stack solution and a two-pointer solution.

The two-pointer implementation uses the fact that when the left boundary is lower than or equal to the right boundary, the current left position can be resolved using the best left boundary seen so far. The symmetric rule applies to the right side.

This gives O(n) time and O(1) auxiliary space.

The stack version instead detects when a newly encountered elevation closes a bounded basin. The width is determined by the distance between the newly encountered right wall and the remaining left wall.

The two implementations therefore solve the same problem with different state representations.

## Stock Span

The stock-span problem asks how many consecutive previous trading sessions have prices less than or equal to the current price.

For prices:

`[100, 80, 60, 70, 60, 75, 85]`

the spans are:

`[1, 1, 1, 2, 1, 4, 6]`

The stack stores indices of prices that can still serve as boundaries.

When the current price is at least as large as the price at the stack top, that older price can no longer stop the current span and is removed.

The remaining stack top, if one exists, is the nearest previous greater price.

This makes stock span an important example of how a monotonic stack can compress a potentially long backward scan.

## Next Greater and Previous Smaller Relationships

The next-greater-element algorithm stores indices whose greater successor has not yet been found.

When a larger value arrives, it resolves all smaller unresolved values at the top of the stack.

The circular version processes the logical array twice while only inserting original indices during the first pass. This allows elements near the end of the array to find a greater value near the beginning.

The previous-smaller algorithm reverses the relationship. Values that are greater than or equal to the current value are removed because they cannot be the nearest strictly smaller boundary.

These algorithms demonstrate a general design pattern:

> Keep only candidates that can still become the answer.

Discarding dominated candidates is what produces the linear-time behavior.

## Expression Conversion

Stacks also provide the standard mechanism for converting infix expressions into postfix notation.

Infix notation places operators between operands:

`3 + 4 * 2`

Postfix notation places each operator after its operands:

`3 4 2 * +`

Operator precedence determines when an operator can leave the operator stack.

Parentheses introduce explicit boundaries. A closing parenthesis causes operators to be removed until the corresponding opening parenthesis is encountered.

Exponentiation is treated as right-associative. Addition, subtraction, multiplication, division, and modulo are left-associative.

The implementations support:

`+ - * / % ^`

and parentheses.

The postfix evaluator then uses a value stack. When an operator is encountered, its operands are popped, the operation is performed, and the result is pushed back.

Division by zero, malformed expressions, mismatched parentheses, and unknown operands are explicitly rejected.

## Expression Evaluation and Validation

A stack-based evaluator must distinguish between an operand and an operator.

The implementations accept numeric operands and named variables. For example:

`revenue - cost * tax`

can be converted to:

`revenue cost tax * -`

with values supplied through a variable map.

This separation between parsing and evaluation is important. The conversion stage establishes execution order, while the evaluation stage operates on the already ordered postfix representation.

The Java implementation represents operators as an enum, which makes precedence and associativity explicit domain properties rather than scattered conditional logic.

## Daily Temperatures

The daily-temperature problem asks how many days each temperature must wait before a warmer temperature appears.

For:

`[73, 74, 75, 71, 69, 72, 76, 73]`

the result is:

`[1, 1, 4, 2, 1, 1, 0, 0]`

The stack stores indices of temperatures that have not yet found a warmer day.

A warmer current temperature resolves every smaller temperature at the top of the stack.

The unresolved indices remain ordered so that each index is pushed and popped once.

## Sum of Subarray Ranges

The sum of subarray ranges is:

`sum(max(subarray) - min(subarray))`

Enumerating every subarray is quadratic in the number of elements, and computing its minimum and maximum independently introduces additional work.

The Python implementation uses two pairs of monotonic-stack boundary calculations.

One pair determines how many subarrays treat an element as their maximum.

The other pair determines how many subarrays treat it as their minimum.

For each element, its contribution is based on:

`value × number_of_left_choices × number_of_right_choices`

The maximum contribution is summed and the minimum contribution is subtracted.

This turns a repeated subarray calculation into a linear-time boundary-counting technique.

## Maximum Rectangle in a Binary Matrix

A binary matrix can be processed row by row by treating every row as the base of a histogram.

For every column, the current histogram height is the number of consecutive `1` values ending at the current row.

For example, after processing a row, the column heights might become:

`[3, 1, 2, 3, 0]`

The largest-rectangle histogram algorithm can then be applied to those heights.

The Python, JavaScript, and Java implementations use this reduction explicitly.

The important algorithmic relationship is:

`binary matrix → row-wise histogram → largest rectangle`

This converts a two-dimensional rectangle problem into a repeated one-dimensional monotonic-stack problem.

## Python Implementation

The Python program is organized around independent executable algorithms.

`largest_rectangle_histogram()` implements the O(n) histogram method.

`largest_rectangle_with_coordinates()` retains the winning boundaries, which is useful when the caller needs the actual rectangle rather than only its area.

`trap_rainwater_two_pointer()` demonstrates the constant-space approach, while `trap_rainwater_stack()` demonstrates basin detection with a stack.

`stock_span()` stores trading-day indices so that the nearest greater price can serve as a boundary.

`infix_to_postfix()` separates parsing from evaluation, and `evaluate_postfix()` performs stack-based execution.

`sum_of_subarray_ranges()` demonstrates contribution counting with monotonic boundaries.

`maximal_rectangle()` repeatedly transforms matrix rows into histogram heights.

The script also contains explicit validation and assertions. Negative histogram heights, negative elevations, malformed matrices, mismatched parentheses, division by zero, and invalid expressions are treated as failures rather than silently producing incorrect results.

`MonotonicStackAnalyzer` provides diagnostic events showing when indices are pushed and popped. This exposes the actual mechanism behind the amortized O(n) behavior.

## JavaScript Implementation

The JavaScript implementation emphasizes event-oriented processing.

`monotonicStackTrace()` is a generator. Instead of constructing a complete diagnostic structure before returning it, it yields each stack decision as processing occurs.

This is useful when a large input stream needs incremental observation.

`ExpressionMachine` separates expression construction, conversion, and evaluation.

`OPERATORS` is a `Map` containing precedence and associativity metadata. This keeps expression rules as data rather than duplicating precedence conditions throughout the parser.

`AlgorithmRunner` provides a small registry abstraction. Algorithms can be registered by name and executed through a common interface without changing the underlying algorithm implementations.

The JavaScript code also demonstrates the distinction between ordinary arrays used as stack containers and index-based stack state used for monotonic algorithms.

## C++ Case Study

The C++ program treats advanced stack algorithms as components of a warehouse and operational analytics system.

`WarehouseMonitoringEngine` receives a sequence representing measured workload levels. Its sustained-capacity calculation uses the histogram rectangle algorithm and reports the selected interval and limiting height.

The same system can estimate trapped capacity using the two-pointer rainwater algorithm.

`ExpressionParser` provides an operator-precedence parser and postfix evaluator. It supports numeric operands and named variables through `unordered_map`.

`MatrixRectangleAnalyzer` converts each binary matrix row into accumulated column heights and applies the histogram algorithm.

The use of `vector`, `unordered_map`, exceptions, and structured result types keeps algorithmic state separate from application-level reporting.

The `RectangleResult` structure is important because the practical system needs more information than the area alone. It preserves the interval and limiting height that produced the result.

## Java Enterprise Model

The Java implementation uses domain-oriented abstractions rather than treating every operation as a standalone function.

`Operator` is an enum containing symbol, precedence, and associativity. This gives the expression engine a controlled representation of operator policy.

`RectangleResult` is a Java record representing an immutable analytical result.

`HistogramAnalyzer`, `RainwaterAnalyzer`, and `StockAnalytics` provide focused services.

`RepositoryPerformanceModel` demonstrates a strategy-style abstraction through the `MergeMetric` interface. The model can register different analytical policies without embedding all algorithms in one conditional method.

Although the metric names are application-oriented, the calculations remain stack-specific. One metric uses the histogram stack and another uses the two-pointer rainwater calculation.

The implementation uses Java collections such as `ArrayDeque`, `ArrayList`, `HashMap`, and `EnumMap`. `ArrayDeque` is particularly appropriate for stack behavior because it provides efficient insertion and removal at one end without the overhead associated with legacy synchronized stack classes.

## SQL Data Model

The SQL script models the input structures required by advanced stack problems.

`histogram_case` and `histogram_bar` represent histogram inputs.

`elevation_case` and `elevation_point` represent elevation profiles.

`stock_series` and `stock_price` represent ordered price observations.

`expression_case` stores expressions and their expected converted form.

`binary_matrix_case` and `binary_matrix_cell` represent binary matrices.

Primary keys prevent duplicate positions within a sequence. Foreign keys preserve relationships between cases and their observations. `CHECK` constraints prevent negative heights and invalid binary values.

Indexes are provided for common filtering and ordering patterns rather than being added indiscriminately.

The SQL histogram query is deliberately relational. It generates contiguous intervals and evaluates the minimum bar height for each interval. This is useful as a database-side reference calculation even though a procedural monotonic stack is normally more efficient for large input sequences.

The rainwater query computes left and right maximum boundaries and then derives each position's trapped volume.

The stock-span query expresses the boundary definition using correlated relational logic.

The binary-matrix section uses recursive SQL to derive accumulated histogram heights from matrix rows.

A transaction demonstrates atomic creation of a histogram and its bars. The negative-height test demonstrates that invalid domain state is rejected by a database constraint rather than relying exclusively on application validation.

## Boundary and Failure Conditions

Advanced stack algorithms are particularly sensitive to equality rules.

For largest rectangles, deciding whether equal-height bars are popped immediately or retained affects which index represents the rectangle. The implementation uses explicit comparison rules rather than leaving equality behavior accidental.

Stock span uses `<=` when removing prices because an equal price belongs to the current span.

Next-greater processing uses a strict `<` comparison because an equal value is not greater.

Previous-smaller processing uses `>=` so that an equal value cannot incorrectly become a strictly smaller boundary.

Expression processing must distinguish left and right associativity. Treating exponentiation as left-associative changes the meaning of expressions such as:

`2 ^ 3 ^ 2`

Malformed parentheses must be rejected instead of producing an incomplete postfix expression.

Matrix input must be rectangular. Otherwise column-based histogram accumulation has no well-defined interpretation.

Negative histogram heights and negative elevation values are rejected because they violate the domain represented by the algorithms.

## Performance Characteristics

| Problem | Time | Auxiliary Space | Main Stack Idea |
|---|---:|---:|---|
| Largest histogram rectangle | O(n) | O(n) | Increasing unresolved bars |
| Trapping rainwater, two pointers | O(n) | O(1) | Boundary state without stack |
| Trapping rainwater, stack | O(n) | O(n) | Unresolved basin boundaries |
| Stock span | O(n) | O(n) | Previous greater boundary |
| Next greater element | O(n) | O(n) | Unresolved smaller values |
| Daily temperatures | O(n) | O(n) | Unresolved colder days |
| Expression conversion | O(n) | O(n) | Operator precedence |
| Postfix evaluation | O(n) | O(n) | Operand evaluation order |
| Maximum binary rectangle | O(rows × columns) | O(columns) | Histogram reduction |

The O(n) results rely on amortized analysis rather than the claim that every individual loop iteration performs constant work.

A single iteration may pop many stack elements. Across the entire input, each element can still be pushed and popped only a bounded number of times.

## Common Implementation Errors

A frequent error in histogram problems is calculating the width using the wrong left boundary. After popping a bar, the new stack top represents the nearest smaller bar on the left, so the usable rectangle begins one position after that index.

Another common error is forgetting to flush the remaining histogram bars. The appended zero sentinel solves this by forcing every unresolved bar to be processed.

In rainwater calculations, using the larger boundary instead of the smaller boundary overestimates trapped water.

In stock span, using a strictly smaller comparison instead of a less-than-or-equal comparison changes the treatment of equal prices.

In circular next-greater calculations, the second traversal must not push duplicate logical indices into the stack. The implementations use the second pass only to resolve previously unresolved indices.

In expression conversion, precedence and associativity must be handled independently. Parentheses are structural delimiters and should not be treated as ordinary operators.

## Security and Reliability Considerations

Expression evaluators should not execute arbitrary source-language expressions. The implementations define an explicit operator set and tokenize supported operands instead of passing input to an interpreter or shell.

Input validation should happen before algorithmic processing. Invalid negative heights, malformed matrices, unknown operands, division by zero, and malformed expressions should produce explicit failures.

For production services processing untrusted input, input sizes should also be bounded. Even an O(n) algorithm can exhaust memory when a hostile client supplies extremely large sequences.

SQL constraints provide an additional integrity boundary. Application validation can fail through programming errors or concurrent writers, while database constraints protect the stored state itself.

Numeric ranges should also be considered. Histogram areas and accumulated water can exceed a 32-bit integer even when individual heights fit within one. The C++ implementation therefore uses `long long` for aggregate quantities, while the Java and Python implementations use numeric representations suitable for their respective calculations.

## Architectural Relationship

The problems in this module share a common progression:

**Input sequence → unresolved relationships → monotonic ordering → boundary discovery → aggregate calculation**

The largest-rectangle problem uses boundaries to determine width.

Rainwater uses boundaries to determine vertical capacity.

Stock span uses a previous greater boundary to determine historical reach.

Next-greater and daily-temperature problems use future observations to resolve pending indices.

Expression conversion uses a stack for operator precedence rather than monotonic values.

Maximum binary rectangle reuses the histogram algorithm after converting two-dimensional data into row-wise heights.

The algorithms are therefore related by the use of stack state, but their stack invariants are different. Preserving those invariants is more important than simply recognizing that a stack is involved.
