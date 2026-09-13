# Array traversal problems

## Topic introduction

Array traversal is the process of visiting the elements of an array or list systematically, usually from the first element to the last. Traversal is one of the most fundamental operations in programming because many array problems are solved by examining each element and maintaining some form of state.

In Python, the built-in `list` type is commonly used to represent an array in algorithmic problems. A list provides indexed access, sequential iteration, dynamic sizing, and support for many built-in operations.

The accompanying Python script develops array traversal from basic iteration to more advanced techniques such as single-pass statistics, prefix sums, sliding windows, two-array traversal, conditional aggregation, matrix traversal, and state-based algorithms.

## What an array represents

An array is a sequence of elements stored in an ordered structure. Each element has a position called an index.

For example:

    numbers = [10, 20, 30, 40, 50]

The indices are:

    10 -> index 0
    20 -> index 1
    30 -> index 2
    40 -> index 3
    50 -> index 4

Python uses zero-based indexing, meaning the first element has index `0`.

Negative indexing is also supported:

    numbers[-1]

refers to the final element.

The number of elements is obtained with `len(numbers)`.

## Fundamental traversal

The simplest traversal is:

    for value in numbers:
        process(value)

This form is appropriate when the position of the element is not required.

When the index is important, an index-based traversal can be used:

    for index in range(len(numbers)):
        value = numbers[index]

Python's `enumerate()` is generally clearer when both the index and value are required:

    for index, value in enumerate(numbers):
        process(index, value)

The script demonstrates all three forms.

## Traversal direction

A traversal does not have to move from the first element toward the last.

Forward traversal visits elements in their natural order.

Reverse traversal visits elements from the last element toward the first. Python provides `reversed()` for this purpose, while explicit index traversal can use a decreasing range.

The direction matters in some algorithms. For example, an algorithm that depends on previously processed elements can produce different results when the traversal direction changes.

## Maximum element

Finding the maximum element is a classic traversal problem.

The basic algorithm is:

1. Treat the first element as the current maximum.
2. Visit each remaining element.
3. If the current element is larger, replace the stored maximum.
4. Return the final maximum.

For an array containing `n` elements, every element may need to be inspected. Therefore the time complexity is `O(n)`.

Only the current maximum needs to be stored, so the auxiliary space complexity is `O(1)`.

Python provides the built-in `max()` function, but manually implementing the algorithm is important for understanding traversal-based problem solving.

## Minimum element

Minimum traversal uses exactly the same principle as maximum traversal.

The first element becomes the initial minimum. Each subsequent element is compared with it. Whenever a smaller value is encountered, the stored minimum is updated.

The time complexity is `O(n)` and auxiliary space complexity is `O(1)`.

## Sum

A sum traversal maintains a running total.

For an array:

    [10, 20, 30]

the running states are:

    10
    30
    60

The final state is the sum.

The algorithm requires one visit to each element, giving `O(n)` time and `O(1)` auxiliary space.

Python's `sum()` performs this standard operation directly.

## Average

The arithmetic mean is calculated as:

    average = sum / number_of_elements

An empty array does not have a defined arithmetic mean. The script therefore raises `ValueError` rather than returning an arbitrary value.

This distinction is important because an algorithm must define its behavior for invalid or undefined inputs.

## Frequency counting

Frequency means the number of times a value appears.

For:

    [2, 4, 2, 7, 4, 2]

the frequencies are:

    2 -> 3
    4 -> 2
    7 -> 1

A dictionary can maintain these counts while traversing the array.

The general operation is:

    frequencies[value] = frequencies.get(value, 0) + 1

Average-case dictionary insertion and lookup are approximately `O(1)`, making the complete traversal `O(n)` on average.

The space requirement is `O(k)`, where `k` is the number of distinct values.

The script also demonstrates `collections.Counter`, which is designed specifically for frequency counting.

## Conditional traversal

Many array problems do not require processing every element in the same way.

A condition determines whether an element should be selected or counted.

Examples include:

    value % 2 == 0

for even numbers,

    value > threshold

for threshold filtering,

and:

    lower <= value <= upper

for range-based selection.

The general pattern is:

    for value in values:
        if condition(value):
            process(value)

This pattern is the foundation of filtering and conditional aggregation.

## Even and odd elements

An integer is even when its remainder after division by two is zero:

    value % 2 == 0

An integer is odd when:

    value % 2 != 0

The traversal can either count matching values or place them into a new result list.

The time complexity remains `O(n)` because each element is inspected once.

## Positive, negative, and zero elements

Conditional traversal can classify numeric values into groups.

Positive values satisfy:

    value > 0

Negative values satisfy:

    value < 0

Zero satisfies:

    value == 0

These categories are mutually exclusive for ordinary numeric values.

Classification problems are useful because they demonstrate how a single traversal can transform raw data into meaningful categories.

## Counting conditional elements

Sometimes the required result is only the number of elements satisfying a condition.

Instead of creating a result list, the algorithm maintains a counter:

    count = 0

    for value in values:
        if condition(value):
            count += 1

This reduces additional memory usage because only the count is stored.

For example, counting values greater than `10` requires `O(n)` time and `O(1)` auxiliary space.

## First matching element

The first matching element can be found by stopping traversal as soon as a condition succeeds.

The important operation is:

    return value

inside the condition.

This is an example of early termination.

If a matching value occurs near the beginning, the algorithm can finish much earlier than `n` iterations. Its worst-case time complexity is still `O(n)`.

If no value matches, the script returns `None`.

## Last matching element

To find the last matching element, traversal continues through the complete array while replacing the stored result whenever a match is found.

This normally requires `O(n)` time.

Unlike first-match searching, it cannot stop at the first match because a later element may also satisfy the condition.

## Matching indices

Sometimes the actual values are insufficient and the positions of matching elements are required.

Using `enumerate()` makes this straightforward:

    for index, value in enumerate(values):
        if condition(value):
            indices.append(index)

The result is an array of indices rather than values.

## Linear search

Linear search checks elements sequentially until the target is found.

For:

    [15, 8, 23, 42, 9]

searching for `42` checks:

    15
    8
    23
    42

The algorithm can stop immediately after finding the target.

Best-case time complexity is `O(1)`.
Worst-case time complexity is `O(n)`.
Auxiliary space complexity is `O(1)`.

If the target does not exist, every element must be examined.

## Single-pass statistics

A straightforward implementation can use:

    min(values)
    max(values)
    sum(values)

This is readable and appropriate for many applications.

A custom single-pass algorithm can maintain minimum, maximum, and sum simultaneously.

The algorithm has:

    Time: O(n)
    Auxiliary space: O(1)

This illustrates an important algorithm-design principle: several related statistics can sometimes be collected during one traversal instead of performing separate logical traversals.

The trade-off is that the single-pass implementation is more complex than using standard built-ins.

## Running values

A running value represents information accumulated from the beginning of the array through the current position.

For running sums:

    [2, 5, 3]

produces:

    [2, 7, 10]

Running maximum produces the greatest value observed so far.

For:

    [4, 2, 7, 3]

the running maximum is:

    [4, 4, 7, 7]

Running minimum works analogously.

These techniques are useful in financial analysis, monitoring systems, statistics, performance tracking, and time-series processing.

## Prefix sums

A prefix-sum array stores cumulative totals.

For:

    [10, 20, 30]

a convenient prefix representation is:

    [0, 10, 30, 60]

The leading zero allows range sums to be calculated using:

    prefix[right + 1] - prefix[left]

For example, the sum from index `1` through index `2` is:

    prefix[3] - prefix[1]
    = 60 - 10
    = 50

Building the prefix array requires `O(n)` time.

After construction, each range-sum query requires `O(1)` time.

This represents a common algorithmic trade-off: use additional memory and preprocessing to make repeated queries faster.

## Two-array traversal

Some problems require simultaneous traversal of two arrays.

For equal-length arrays:

    [1, 2, 3]
    [4, 5, 6]

the elementwise sum is:

    [5, 7, 9]

The dot product is:

    1 × 4 + 2 × 5 + 3 × 6
    = 32

Python's `zip()` is useful for synchronized traversal.

If two arrays are expected to correspond element-for-element, unequal lengths should usually be treated as an error rather than silently ignored.

## Reverse traversal

Reverse traversal is useful when processing must begin at the end of an array.

The script demonstrates both:

    reversed(values)

and explicit decreasing index traversal.

A reversed copy requires additional storage when a new list is created.

Simply iterating through `reversed(values)` does not require constructing a second complete list.

## Adjacent-element traversal

Some problems compare neighboring elements.

For an array of length `n`, there are `n - 1` adjacent pairs:

    values[0], values[1]
    values[1], values[2]
    ...
    values[n - 2], values[n - 1]

This pattern is useful for detecting increases, decreases, transitions, duplicate runs, changes in state, and local patterns.

Care must be taken with arrays containing fewer than two elements because there are no adjacent pairs in such arrays.

## Sliding-window traversal

A sliding window processes contiguous sections of an array.

Suppose the array is:

    [2, 1, 5, 1, 3, 2]

and the window size is `3`.

The windows are:

    [2, 1, 5]
    [1, 5, 1]
    [5, 1, 3]
    [1, 3, 2]

A naive algorithm recalculates every window's sum from scratch.

The sliding-window technique reuses the previous result:

    new_sum = old_sum - outgoing_value + incoming_value

This changes the typical complexity from `O(n × k)` to `O(n)` for a fixed window size `k`.

The technique is widely used in moving averages, monitoring systems, signal processing, time-series analysis, and contiguous-subarray problems.

## Matrix traversal

A matrix is an array containing arrays.

For example:

    [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ]

A row-major traversal processes the first row, then the second, then the third.

The nested traversal pattern is:

    for row in matrix:
        for value in row:
            process(value)

For an `r × c` matrix, visiting every element takes `O(r × c)` time.

The script calculates row sums, column sums, and flattened row-major traversal.

Column operations require care because the rows must have consistent lengths. A matrix with rows of different lengths is a ragged structure rather than a conventional rectangular matrix.

## Conditional statistics

A powerful traversal pattern combines filtering and aggregation.

For example, instead of first creating a list of all even numbers and then calculating its statistics, a single traversal can calculate:

- count
- sum
- minimum
- maximum
- average

only for matching values.

This demonstrates state aggregation.

The general design is:

    initialize state

    for value in values:
        if condition(value):
            update state

    return state

This pattern is particularly useful when processing large data sets because unnecessary intermediate lists can be avoided.

## Duplicate detection

A set can record values already encountered.

The basic idea is:

    if value in seen:
        duplicate
    else:
        add value to seen

This provides average-case `O(1)` membership checking.

The complete traversal is therefore approximately `O(n)` average time.

The script preserves the order in which values are first recognized as duplicates.

## Second-largest distinct element

Finding the second-largest distinct value is an example of state-based traversal.

Two pieces of state are maintained:

- largest value seen
- second-largest distinct value seen

When a new value exceeds the current maximum, the old maximum becomes the second-largest value.

Sorting could solve the problem, but sorting requires `O(n log n)` time. A correctly designed traversal can solve it in `O(n)` time with `O(1)` auxiliary state.

The word `distinct` is important. An array such as:

    [10, 10, 8]

has only one distinct maximum value, so it does not contain a second-largest distinct value.

## State tracking and maximum profit

The stock-price example demonstrates a more advanced traversal pattern.

Given:

    [7, 1, 5, 3, 6, 4]

the algorithm must choose a buying price before the selling price.

The traversal maintains:

- the minimum price seen so far
- the best profit found so far

For each later price, the possible profit is calculated against the minimum price already observed.

This is a general example of converting a potentially quadratic comparison problem into a linear state-tracking algorithm.

## Stable conditional partitioning

Partitioning separates elements according to a condition.

The script demonstrates placing even values before odd values while preserving the relative order inside each group.

For example:

    [5, 2, 7, 4, 1, 6]

becomes:

    [2, 4, 6, 5, 7, 1]

This implementation uses additional lists and therefore requires `O(n)` auxiliary space.

The stability requirement is important. A partition that merely separates the groups does not necessarily preserve their original ordering.

## In-place traversal

An in-place operation modifies the original array rather than constructing a separate result.

The script replaces negative values with zero by modifying elements through their indices.

In-place algorithms can reduce memory usage, but they have an important side effect: the original data is changed.

This can be undesirable when the original array must remain available for later processing.

## Generators and lazy traversal

A generator can yield values one at a time instead of constructing a complete result list.

For example, a function can yield only values above a threshold.

This is useful when:

- the input is large
- only a few matching values are needed
- results can be consumed incrementally
- memory usage matters

A list creates all results immediately. A generator produces results lazily.

The trade-off is that a generator is generally consumed sequentially and does not provide the same random-access behavior as a list.

## Traversing structured records

Arrays are not limited to numbers.

An array can contain dictionaries representing records:

    {
        "name": "Asha",
        "salary": 65000
    }

Traversal can calculate the average salary or identify the highest-paid employee.

This illustrates how the same traversal principles apply to structured application data.

The important difference is that the comparison or aggregation operation now uses fields inside each record.

## Traversing text arrays

String arrays can be traversed using the same techniques.

Examples include:

- counting words above a certain length
- finding the longest word
- filtering words
- checking prefixes
- calculating character-based properties

The traversal mechanism does not fundamentally change. Only the condition or aggregation logic changes.

## Edge cases

A robust traversal algorithm must define its behavior for unusual inputs.

Important cases include:

### Empty array

An empty array contains no elements.

Operations such as sum naturally produce `0`, but minimum, maximum, and average are undefined without an explicit convention.

The script raises an exception for undefined minimum, maximum, and average operations.

### Single-element array

For:

    [42]

the minimum, maximum, and average are all `42`.

A second-largest distinct value does not exist.

There are also no adjacent pairs.

### All elements equal

For:

    [7, 7, 7, 7]

the minimum and maximum are both `7`.

There is only one distinct value, so a second-largest distinct element cannot be found.

### Negative values

Algorithms should not assume that values are positive.

Initializing a maximum or minimum to `0` is a common mistake because an all-negative array would produce an incorrect maximum if `0` were not actually present.

The safer strategy is to initialize the state from the first element.

### Zero

Zero is neither positive nor negative.

Conditional classification must account for this explicitly when the distinction matters.

### Duplicates

Duplicates affect frequency counts, distinct-value algorithms, searching, and ranking problems.

An algorithm that requires distinct values must explicitly enforce that requirement.

### Invalid input types

Numeric traversal functions should not silently accept strings or unrelated objects.

The validation function checks numeric inputs and rejects boolean values even though Python technically treats `bool` as a subclass of `int`.

## Common mistakes

### Initializing maximum to zero

Incorrect approach:

    maximum = 0

This fails for:

    [-10, -5, -20]

because the actual maximum is `-5`, not `0`.

Initializing from the first element is safer.

### Starting an index loop at the wrong position

When comparing adjacent elements, the first comparison often begins at index `1`:

    for index in range(1, len(values)):
        compare(values[index], values[index - 1])

Starting at index `0` would attempt to access an invalid previous position unless the algorithm deliberately uses negative indexing.

### Forgetting empty input

Operations that access `values[0]` immediately will fail on empty arrays.

The algorithm should either reject empty input explicitly or define a valid result for it.

### Dividing by zero

Average calculation on an empty array causes division by zero if the input is not checked.

### Ignoring unequal array lengths

When two arrays represent corresponding data, silently truncating one array with `zip()` can hide a data-quality problem.

Explicit length validation is preferable when equal lengths are required.

### Modifying an array unintentionally

In-place traversal changes the original list.

When the original data is needed later, construct a separate result or work on a copy.

### Building unnecessary intermediate lists

A list comprehension is concise, but constructing a large filtered list may use substantial memory.

A generator can be more appropriate when the results only need to be processed sequentially.

### Repeating expensive traversal

Calling multiple functions over the same very large data set can create unnecessary work.

When performance is critical, related statistics can sometimes be calculated in one pass.

## Built-ins versus manual traversal

Manual traversal is valuable for understanding algorithms and implementing custom logic.

Built-in operations such as:

    min()
    max()
    sum()
    reversed()

are generally preferable for standard operations because they are concise, tested, and implemented efficiently.

Manual traversal becomes more appropriate when the operation involves custom state, multiple conditions, early termination, domain-specific rules, or an algorithm not directly provided by a built-in.

The best choice is therefore not simply "loops are faster" or "built-ins are always better." The appropriate approach depends on the problem, readability requirements, input size, and algorithmic complexity.

## Time complexity

For an array containing `n` elements:

| Operation | Typical complexity |
|---|---:|
| Full traversal | O(n) |
| Maximum | O(n) |
| Minimum | O(n) |
| Sum | O(n) |
| Average | O(n) |
| Linear search | O(n) worst case |
| Frequency counting | O(n) average |
| Filtering | O(n) |
| Counting a condition | O(n) |
| Running statistics | O(n) |
| Prefix-sum construction | O(n) |
| Prefix-sum range query | O(1) |
| Fixed-size sliding window | O(n) |
| Matrix traversal | O(rows × columns) |
| Sorting-based ranking | O(n log n) |
| Single-pass second maximum | O(n) |

The number of passes is important, but it is not the only performance consideration. Constant factors, Python implementation details, memory allocation, and the cost of individual operations also matter.

## Space complexity

A simple traversal can often use `O(1)` auxiliary space.

For example:

    total = 0

    for value in values:
        total += value

Only the running total is required.

Filtering into a new list requires additional space proportional to the number of selected elements.

Frequency counting requires space proportional to the number of distinct values.

Prefix sums require `O(n)` additional storage.

Generators can reduce the memory cost of producing filtered results because values are produced lazily.

## Single pass versus multiple passes

A single-pass implementation can combine related calculations:

    minimum
    maximum
    sum
    count

This can reduce traversal overhead.

There is a readability trade-off. A highly compact multi-purpose loop can become difficult to understand when it contains many unrelated conditions.

For ordinary-sized inputs, clear built-in operations may be preferable.

For very large inputs or streaming systems, reducing unnecessary passes can become more significant.

## Streaming data considerations

Some data does not exist as a complete array in memory.

Examples include:

- log records
- sensor measurements
- transaction streams
- network data
- large files

The same traversal concepts can operate on iterables and generators.

A streaming algorithm should avoid assumptions such as:

    len(data)

or:

    data[0]

when the input may not support random access.

The generator example in the script demonstrates how filtering can be performed lazily.

## Numerical considerations

Floating-point arithmetic can introduce small representation errors.

For example, calculations involving decimal fractions may not produce exact binary representations.

The script uses `math.isclose()` in a test instead of requiring exact equality for a floating-point calculation.

For financial applications where exact decimal arithmetic is required, Python's `decimal.Decimal` type can be more appropriate than binary floating-point values.

The correct numerical representation depends on the domain.

## Validation considerations

Input validation prevents ambiguous or invalid data from reaching algorithmic logic.

Useful checks include:

- whether the array exists
- whether the array is empty
- whether values have the expected type
- whether numeric bounds are valid
- whether two arrays have equal lengths
- whether a window size is positive
- whether a matrix is rectangular

Validation is particularly important at application boundaries where data originates from users, files, APIs, or external systems.

## Error handling

The script uses explicit exceptions for invalid states.

Examples include:

    ValueError

when an operation is mathematically undefined or an argument is invalid, and:

    TypeError

when an element has an inappropriate type.

Exceptions are preferable to silently returning misleading results.

For example, returning `0` for the maximum of an empty array would confuse "no maximum exists" with "the maximum is zero."

## Debugging traversal algorithms

Traversal bugs frequently arise from incorrect indices or incorrect state updates.

A useful debugging technique is to display:

- current index
- current value
- state before or after the update

The script includes a running-sum debugging function that prints the current index, value, and cumulative total.

For production systems, direct printing is usually replaced with structured logging or proper diagnostics.

## Testing traversal algorithms

The script contains assertion-based tests covering:

- maximum
- minimum
- sum
- average
- frequency
- filtering
- searching
- running statistics
- prefix sums
- paired traversal
- sliding windows
- matrices
- duplicates
- ranking
- conditional partitioning
- mutation
- generators
- text traversal
- floating-point comparison

Good traversal tests should include normal cases as well as boundary cases.

A useful test set often includes:

    empty input
    one element
    repeated values
    all-negative values
    mixed values
    sorted input
    reverse-sorted input
    target absent
    target present at first position
    target present at last position

## Production considerations

In production code, traversal algorithms should be selected according to actual data characteristics.

For small collections, readability usually has greater practical value than micro-optimizing the number of passes.

For large collections, important questions include:

- How many elements exist?
- Can the data fit in memory?
- Is random access required?
- Can the data be streamed?
- Are repeated queries performed?
- Is preprocessing worthwhile?
- Is additional memory acceptable?
- Are values numeric and precision-sensitive?
- Can early termination be used?
- Can intermediate lists be avoided?

A prefix-sum structure is appropriate when many range queries are required. A generator is useful when results can be processed incrementally. A single-pass algorithm is valuable when several statistics must be collected from a very large data set.

## Practical applications

Array traversal appears in many real systems.

### Financial analysis

Daily prices or returns can be traversed to calculate:

- minimum price
- maximum price
- average price
- cumulative returns
- threshold events
- moving averages
- transaction statistics

### Business analytics

Sales arrays can be analyzed for:

- total revenue
- average revenue
- highest-performing day
- lowest-performing day
- days above a target
- zero-sales periods

The script includes a complete sales-analysis example.

### Monitoring

A sequence of measurements can be traversed to detect:

- values above a threshold
- sudden changes
- minimum readings
- maximum readings
- cumulative measurements
- moving averages

### Data processing

Large collections of records can be traversed to:

- filter records
- count categories
- calculate statistics
- identify exceptional values
- find the highest or lowest record

### Machine learning and numerical computing

Traversal principles appear in:

- feature preprocessing
- aggregation
- normalization
- metric calculation
- vector operations
- batch processing

Although specialized numerical libraries may provide faster vectorized implementations, the underlying concepts are still based on systematic element processing.

## Important distinctions

### Traversal versus searching

Traversal means systematically visiting elements.

Searching is a particular task performed during traversal to locate a target or condition.

### Filtering versus counting

Filtering creates or identifies the matching elements.

Counting only records how many elements satisfy the condition.

Counting normally requires less additional memory.

### Maximum versus second-largest distinct value

The maximum is the greatest element.

The second-largest distinct value must be strictly smaller than the maximum and must exist as a separate distinct value.

### Full traversal versus early termination

Some problems require examining every element.

Others can stop as soon as the required information is found.

Early termination can improve practical performance without changing the worst-case complexity.

### In-place versus out-of-place

In-place traversal modifies the original structure.

Out-of-place traversal creates a new result.

The choice affects memory usage, side effects, and data preservation.

### List versus generator

A list stores all produced values.

A generator produces values lazily.

Lists are convenient for repeated access. Generators are useful for sequential processing and memory-efficient pipelines.

## Security considerations

Array traversal itself is generally not a security-sensitive operation, but applications processing external data should validate inputs.

Potential issues include:

- unexpectedly large arrays causing excessive memory use
- extremely large nested structures causing excessive processing
- invalid numeric values
- malformed records
- unexpected types
- resource exhaustion through repeated expensive operations

For untrusted input, application-level limits should be considered.

Examples include maximum record counts, maximum nested dimensions, maximum string lengths, and bounded processing time.

Validation should occur before expensive processing whenever practical.

## Algorithmic design principles demonstrated

The script illustrates several reusable algorithmic patterns.

### Accumulator

Maintain a running result:

    total += value

### Extremum tracking

Maintain a current minimum or maximum:

    if value > maximum:
        maximum = value

### Counter

Count matching elements:

    if condition:
        count += 1

### State tracking

Maintain multiple pieces of information that describe the portion of the array already processed.

### Early termination

Return as soon as a required result is known.

### Prefix preprocessing

Perform preprocessing once to make later queries faster.

### Sliding window

Reuse information from a previous contiguous range.

### Synchronized traversal

Process corresponding positions from multiple arrays.

### Nested traversal

Visit every element of a multidimensional structure.

These patterns recur across data structures, competitive programming, analytics, and production software.

## Complexity trade-offs

Algorithm design often involves trading time against memory.

A direct range-sum calculation may require `O(k)` time for a range containing `k` elements.

A prefix-sum structure requires `O(n)` preprocessing and `O(n)` additional memory, after which each range query is `O(1)`.

Similarly, constructing a filtered list requires memory proportional to the result size, while a generator can process matching elements lazily.

The correct trade-off depends on workload characteristics rather than on a universal preference for either speed or memory efficiency.

## Code organization

The Python script separates concepts into small functions.

This makes individual traversal algorithms easier to:

- understand
- test
- reuse
- debug
- compare
- benchmark

The `main()` function executes the educational demonstrations in a logical progression.

The assertion test function provides an independent correctness check for the major algorithms.

## File usage

The Python file is self-contained and uses only Python's standard library.

It can be executed directly with a Python interpreter.

The program prints demonstrations of the traversal techniques and finishes by running assertion-based tests. A successful test run indicates that the implemented examples satisfy their expected results.

The central principle throughout the script is simple: identify what information must be maintained while visiting each element, update that information correctly, and define precise behavior for boundary conditions and invalid input.
