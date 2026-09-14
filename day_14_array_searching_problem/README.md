# Array searching problems

## Introduction

Array searching is the process of examining a collection of values to determine whether a particular value or condition is present and, when required, identifying its position.

For an unsorted array, **linear search** is the fundamental searching technique. It examines elements sequentially until the required result is obtained or the entire array has been examined.

The accompanying Python script develops array searching from basic exact-value searches to more advanced problems involving duplicates, conditions, pairs, nested arrays, custom predicates, frequency analysis, floating-point values, object records, and reusable search utilities.

The examples use Python lists as the primary array representation, while several examples demonstrate that the same searching principles apply to tuples, ranges, strings, dictionaries, objects, and nested sequences.

## Basic terminology

### Array

An array is an ordered collection of elements that can be accessed by position.

In Python, the `list` type is commonly used for array-like programming.

For example:

    numbers = [10, 20, 30, 40]

The positions are called indexes:

    10 -> index 0
    20 -> index 1
    30 -> index 2
    40 -> index 3

Python uses zero-based indexing.

### Target

The **target** is the value being searched for.

For example, when searching `[10, 20, 30]` for `20`, the target is `20`.

### Occurrence

An occurrence is one position at which a target appears.

For:

    [5, 2, 8, 2, 9, 2]

the value `2` occurs at indexes `1`, `3`, and `5`.

### First occurrence

The first occurrence is the smallest index containing the target.

For:

    [5, 2, 8, 2, 9, 2]

the first occurrence of `2` is index `1`.

### Last occurrence

The last occurrence is the largest index containing the target.

For the same array, the last occurrence of `2` is index `5`.

### Predicate

A predicate is a condition that produces a Boolean result.

Examples include:

    x % 2 == 0
    x > 100
    len(x) >= 5

Predicates allow searching for properties rather than exact values.

## Linear search

Linear search examines elements sequentially.

Suppose the array is:

    [10, 20, 30, 40, 50]

and the target is `40`.

The algorithm compares:

    10 -> no
    20 -> no
    30 -> no
    40 -> yes

The search can terminate immediately after finding the target.

A basic implementation returns the index of the first matching element and returns `-1` when the target is absent.

The important property of linear search is that the input does not need to be sorted.

## Linear search algorithm

The basic procedure is:

1. Start at index zero.
2. Compare the current value with the target.
3. If they are equal, return the current index.
4. Otherwise continue to the next element.
5. If the end is reached without a match, return `-1`.

A typical implementation has the structure:

    for index, value in enumerate(array):
        if value == target:
            return index

    return -1

`enumerate()` is particularly useful because it supplies both the index and the value.

## Why linear search works on unsorted arrays

Linear search does not make assumptions about element ordering.

Consider:

    [40, 10, 90, 20, 70]

A search for `20` still works because every element can be examined independently.

This is one of the main differences between linear search and binary search.

Binary search relies on ordered data. Linear search does not.

## First occurrence

When searching from left to right and returning immediately when a match is found, the result is automatically the first occurrence.

For:

    [7, 4, 7, 9, 7]

the first occurrence of `7` is index `0`.

For:

    [4, 7, 9, 7, 2]

the first occurrence of `7` is index `1`.

This pattern is useful whenever the problem asks for the earliest position satisfying a requirement.

## Last occurrence

Finding the last occurrence requires continuing the search after a match.

The algorithm maintains a variable containing the most recently observed matching index.

Conceptually:

    last_index = -1

    for index, value in enumerate(array):
        if value == target:
            last_index = index

    return last_index

If no match occurs, `last_index` remains `-1`.

Another approach is to scan from right to left. The first match found during a right-to-left traversal is the last occurrence in normal left-to-right indexing.

## All occurrences

Some problems require every matching index rather than only the first or last one.

For:

    [7, 3, 7, 1, 7]

the positions of `7` are:

    [0, 2, 4]

The algorithm therefore maintains a result list and appends each matching index.

Unlike first-occurrence search, this algorithm cannot stop after the first match.

## Counting occurrences

Counting occurrences is closely related to finding all positions.

Instead of storing each index, maintain a counter:

    count = 0

    for value in array:
        if value == target:
            count += 1

This uses constant auxiliary space when only the count is required.

For an array of length `n`, the search takes O(n) time in the worst case.

## Existence search

Sometimes the problem only asks whether a value exists.

The result is therefore Boolean:

    True
    False

Once a matching element is found, the algorithm can immediately return `True`.

If the entire array is examined without finding the target, it returns `False`.

This is an example of **early termination**.

## Early termination

Early termination means stopping the search as soon as the required answer is known.

For first occurrence:

    stop at the first match

For existence:

    stop at the first match

For all occurrences:

    do not stop after the first match

For last occurrence:

    normally continue through the array

Choosing the correct termination rule is essential. Returning too early can produce a logically incorrect answer.

## Searching under conditions

Many array problems do not specify a target value.

Instead, they ask for an element satisfying a condition.

Examples:

- first even number
- first negative number
- first value greater than a threshold
- first value inside an interval
- first string with a particular length
- first record belonging to a department

The generalized pattern is:

    for index, value in enumerate(array):
        if condition(value):
            return index, value

This separates the search mechanism from the condition being tested.

## Predicate-based searching

The script provides a reusable function that accepts a predicate.

For example:

    lambda x: x % 2 == 0

means that the search should identify the first even number.

Another predicate:

    lambda x: x > 100

searches for the first value greater than `100`.

This design is useful because the same search implementation can support many different requirements.

## Index-aware predicates

Some conditions depend on both the value and its position.

For example, a problem may require the first value at an even index satisfying a numerical condition.

An index-aware predicate can receive:

    index
    value

This makes the search abstraction more flexible.

## First and last matches in one pass

If both the first and last occurrence are required, they can be determined in one traversal.

The algorithm maintains two variables:

    first = -1
    last = -1

When a target is found:

- set `first` only if it has not already been set
- always update `last`

This takes O(n) time and O(1) auxiliary space.

Performing two independent full scans is unnecessary when one traversal can produce both results.

## Duplicate detection

A duplicate exists when a value occurs more than once.

A direct pairwise solution compares every element with every later element.

Its worst-case time complexity is O(n²).

For an array of length `n`, there can be approximately n²/2 pairs to inspect.

This approach is useful for understanding the problem but is generally inefficient for large arrays.

## Duplicate detection with a set

A set can store values that have already been encountered.

For each value:

1. Check whether it is already in the set.
2. If it is, a duplicate has been found.
3. Otherwise insert it into the set.

Set membership is O(1) on average.

Therefore duplicate detection is O(n) average time with O(n) additional space.

The trade-off is straightforward:

- nested loops use less auxiliary memory but require O(n²) time
- a set uses additional memory but provides O(n) average-time detection

## First duplicate

The phrase "first duplicate" can have different meanings.

One interpretation is the first value encountered whose occurrence is a repetition during a left-to-right scan.

For:

    [5, 3, 7, 3, 9]

the second `3` causes the first duplicate detection.

The exact interpretation should always be determined from the problem statement.

## All duplicate values

If the task asks for every distinct value that occurs more than once, a frequency structure or two-set approach can be used.

The script preserves the order in which duplicate values are first detected.

This is different from simply converting a list to a set, because a set does not express the problem's required occurrence information.

## Frequency maps

A frequency map stores the number of occurrences of each value.

For:

    [4, 4, 2, 7, 4, 2]

the conceptual frequency map is:

    4 -> 3
    2 -> 2
    7 -> 1

Python dictionaries are natural for this purpose.

The `get()` method is useful for incrementing counts safely:

    frequencies[value] = frequencies.get(value, 0) + 1

Frequency maps support several search-related problems:

- duplicate detection
- first unique element
- first non-repeating element
- majority element
- exact-frequency searches
- repeated-value analysis

## First non-repeating element

A non-repeating element has frequency one.

The efficient approach is usually two-pass:

1. Build a frequency map.
2. Scan the original array from left to right.
3. Return the first element whose frequency is one.

The first pass determines global frequency information.

The second pass preserves the original order.

## Majority element

A majority element occurs more than half the length of the array.

For an array of length `n`, the required condition is:

    frequency > n / 2

The script demonstrates a frequency-map implementation.

More specialized algorithms such as Boyer-Moore can reduce auxiliary space to O(1), but the frequency-based version makes the search condition explicit and easy to understand.

## Searching for minimum and maximum

Finding a minimum or maximum can be treated as a search problem.

Instead of searching for a known target, the algorithm maintains the best candidate found so far.

For maximum:

    if current_value > current_maximum:
        update maximum

This requires one traversal and O(1) auxiliary space.

An empty array requires explicit handling because there is no valid maximum or minimum.

The script raises `ValueError` for such cases.

## Searching relative to an average

Some problems define the search target indirectly.

For example:

"Find the first value greater than the average."

The algorithm first computes the average and then performs a linear search using the derived condition.

This demonstrates an important problem-solving pattern:

1. Compute a global property.
2. Search using that property.

## Searching for a local peak

A local peak is an element that is greater than its immediate neighbors.

For an interior position `i`:

    array[i] > array[i - 1]
    array[i] > array[i + 1]

Boundary positions require special treatment because they do not have two neighbors.

The script therefore searches only interior positions.

This illustrates how neighboring elements create boundary conditions in array problems.

## Searching for a local valley

A local valley is an interior element smaller than both immediate neighbors.

The condition becomes:

    array[i] < array[i - 1]
    array[i] < array[i + 1]

The same boundary considerations apply as with local peaks.

## Searching for transitions

A transition occurs when the property of interest changes.

For:

    [False, False, False, True, True]

the first `True` can represent a transition point.

Searching for a transition is common when processing state sequences, classifications, thresholds, and status changes.

## Searching for adjacent changes

An adjacent change occurs when:

    array[i] != array[i - 1]

The script returns the first position where this happens.

This pattern is useful for detecting:

- changes in status
- boundaries between groups
- changes in categories
- breaks in repeated sequences

## Searching for plateaus

A plateau is a consecutive sequence of equal values.

For example:

    [1, 1, 2, 3, 3, 3, 4]

contains a plateau of three `3` values.

The script searches for the first plateau whose length reaches a specified minimum.

This requires maintaining the beginning of the current run and detecting when that run ends.

## Searching for order violations

A non-decreasing array must satisfy:

    array[i] >= array[i - 1]

for every valid `i`.

Therefore the first position where:

    array[i] < array[i - 1]

is a violation of non-decreasing order.

This is a useful example of searching for an invalid condition rather than searching for a desired value.

The same principle can be reversed for descending order.

## Pair searching

A common searching problem asks whether two values add up to a target.

For:

    [2, 7, 11, 15]

and target `9`, the pair is:

    2 + 7 = 9

A nested-loop implementation requires O(n²) time.

A hash-based implementation stores previously observed values and searches for the complementary value:

    required = target - current_value

This reduces the average time to O(n) with O(n) additional space.

## Two-sum trade-off

The two main approaches demonstrate the time-space trade-off.

Nested loops:

- Time: O(n²)
- Extra space: O(1)
- Simple
- Suitable for small arrays

Hash-based approach:

- Average time: O(n)
- Extra space: O(n)
- Faster for large inputs
- Requires additional memory

The appropriate approach depends on input size, memory constraints, and whether the problem permits additional data structures.

## Triplet searching

Searching for three values with a target sum can be solved directly with three nested loops.

The straightforward algorithm has O(n³) time complexity.

This demonstrates how adding another independent search dimension can significantly increase computational cost.

For larger inputs, more advanced approaches are normally required.

## Subarray searching

A subarray is a contiguous sequence of elements from an array.

For example:

    [1, 2, 3, 4]

contains:

    [1, 2]
    [2, 3]
    [3, 4]
    [2, 3, 4]

Searching for a complete pattern is different from searching for one value.

The script implements direct pattern comparison by checking each possible starting position.

## Empty pattern

The script treats an empty pattern as occurring at index zero.

This is a conventional mathematical and algorithmic interpretation for substring or subarray searching.

Problem statements may define empty-pattern behavior differently, so production implementations should document the chosen convention.

## Overlapping subarrays

Consider:

    [1, 1, 1]

with pattern:

    [1, 1]

The pattern occurs at:

    index 0
    index 1

These occurrences overlap.

The script counts both.

This distinction matters because some searching problems count only non-overlapping matches while others count every valid starting position.

## Searching strings

Strings are sequences, so linear-search principles can also be applied to characters.

A string search can identify:

- first occurrence of a character
- last occurrence
- all positions
- strings satisfying a length condition
- strings with a particular prefix
- strings with a particular suffix

Python provides higher-level string methods for many common cases, but the manual implementations demonstrate the underlying search logic.

## Case-insensitive searching

Text comparisons may need normalization.

The script uses `casefold()` for case-insensitive comparison.

For example:

    "Python".casefold()
    "python".casefold()

produce equivalent comparison keys.

This approach is preferable to assuming that uppercase and lowercase forms should be treated as different values when the application requires case-insensitive matching.

## Searching objects

Searching does not have to operate on primitive values.

The script defines a `Student` class and searches student objects by attributes such as:

    roll_number
    score

A search condition can inspect object properties.

This pattern is common in real applications where arrays contain records rather than isolated numbers.

## Key-based search

A key function transforms an object into the property used for comparison.

For example, a student object can be searched using:

    student.roll_number

This separates the identity of an object from the property used to locate it.

Key-based searching is useful for:

- database-like records
- employee collections
- products
- transactions
- customer records
- configuration objects

## Searching dictionaries and records

A list of dictionaries can represent structured records.

For example:

    {"id": 101, "name": "Asha", "department": "Finance"}

A search can examine the `id` field or another record attribute.

The `get()` method is useful when a key may be absent because it avoids raising a `KeyError` during the search.

## Nested-array searching

A two-dimensional array requires two levels of traversal.

For a matrix:

    [
        [10, 20, 30],
        [40, 50, 60],
        [70, 80, 90]
    ]

the position of `60` is:

    row 1, column 2

The script returns a tuple containing row and column indexes.

The same concept extends to higher-dimensional structures, although traversal and complexity become more involved.

## Recursive linear search

Linear search can be expressed recursively.

The recursive approach examines one element and calls itself for the next position.

Although conceptually elegant, recursion is generally not the preferred implementation in Python for large arrays.

Python has a recursion-depth limit, and each recursive call introduces function-call overhead.

An iterative loop is usually simpler, faster, and safer for production linear searches.

## Sentinel search

Sentinel search temporarily places the target at the end of a mutable sequence so that the loop can avoid an explicit boundary test on every iteration.

The script uses a copy to ensure that the original array is not modified.

Sentinel search is mainly useful for understanding algorithmic optimization techniques. In ordinary Python code, the clarity of a standard loop generally outweighs the small theoretical benefit of eliminating a boundary check.

## Floating-point searching

Exact equality is often inappropriate for calculated floating-point values.

For example:

    0.1 + 0.2

may not have exactly the same binary floating-point representation as:

    0.3

A tolerance-based comparison uses:

    abs(value - target) <= tolerance

The tolerance should be selected according to the numerical problem rather than arbitrarily.

## NaN behavior

`NaN`, or Not a Number, has unusual equality semantics.

For floating-point NaN:

    NaN != NaN

Therefore ordinary equality-based search may fail to identify a NaN value.

The correct approach is to use a NaN-aware check such as `math.isnan()` for floating-point values.

This is an important exception to ordinary equality-based search.

## Boolean and integer behavior

Python has a language-specific relationship between booleans and integers:

    True == 1
    False == 0

Consequently, a search using equality can consider `True` and `1` equal.

This can produce surprising results in mixed-type collections.

When type distinctions matter, explicit type checks may be necessary.

## Searching by type

A search can identify the first value having a particular type.

The script uses `isinstance()` for this purpose.

This is useful when a sequence contains heterogeneous data and the search requirement is type-based rather than value-based.

## Searching tuples and ranges

The same linear-search functions can work with tuples because tuples are ordered sequences.

A `range` object can also be traversed without first converting it into a list.

This demonstrates that the search algorithm depends primarily on sequential access rather than on the specific concrete container type.

## Searching from a specific index

A search can begin at a specified index.

This is useful when:

- finding subsequent occurrences
- processing an array in stages
- searching only a suffix
- implementing repeated pattern searches

The script normalizes negative start positions to zero in its custom implementation.

The exact behavior should be defined clearly when designing an API.

## Range-limited searching

Sometimes a problem restricts the search to an inclusive or exclusive range.

For example, searching only indexes:

    2 through 5

means values outside that region must not influence the result.

Boundary normalization is important to prevent invalid index access.

## Prefix and suffix searches

A prefix search examines only the beginning of an array.

A suffix search examines only the end.

These are specialized forms of linear search and are useful when a problem explicitly limits the logical search region.

## Step-based searching

A search can examine every second or third position rather than every position.

For example, indexes may be:

    0, 2, 4, 6

A negative step can traverse an array from right to left.

A step of zero is invalid because it would never advance the search.

## Searching for a missing value

If an array should contain values from `1` through `n` with exactly one missing value, the script demonstrates a set-based membership search.

The expected values are examined, and the first one not present in the array is returned.

This approach has O(n) average membership checks but uses O(n) additional memory.

There are alternative arithmetic and XOR-based approaches with O(1) auxiliary space, but they require stronger assumptions about the input.

## Searching across two arrays

Searching problems frequently involve relationships between arrays.

Examples include:

- values in the first array but not the second
- values common to both
- duplicate values across arrays
- values satisfying conditions in one array based on another

A set can provide efficient membership checks.

The original array should still be traversed when output order matters.

## Preserving order

A frequent implementation mistake is to convert data to a set and lose the required order.

Sets are excellent for membership testing, but they do not represent occurrence order as the primary concept of the problem.

If the requirement says "first", "last", or "in original order", the original sequence must remain part of the algorithm.

## Precomputed indexes

If the same array will be searched many times, repeatedly performing linear search may become expensive.

A precomputed index can map:

    value -> first index

Building the index costs O(n) average time.

After construction, lookup is O(1) average time.

The trade-off is additional memory.

This is an example of **precomputation**: spend work once to make future queries faster.

## Index of all occurrences

A more detailed index can map each value to every position where it occurs.

Conceptually:

    value -> [index1, index2, index3]

Construction takes O(n) time, while retrieving all positions for a known value is proportional to the number of stored results.

This structure is useful for workloads involving repeated occurrence queries.

## Searching multiple targets

If several targets must be searched in one array, independently running linear search for every target can require O(n × m) work for `m` targets.

A set of requested targets allows one traversal of the array.

The algorithm can record the first position of every requested target as it is encountered.

This illustrates how restructuring a problem can eliminate repeated scans.

## Prefix sums as a search condition

A search condition may depend on an accumulated value.

For example, the task may ask:

"Find the first index where the cumulative sum exceeds 100."

The algorithm maintains a running sum and checks the condition after each element.

This is still fundamentally a sequential search, but the condition depends on previous elements.

## Cumulative products

The same principle can be applied to a running product.

The search maintains:

    product *= value

and stops when the required threshold is exceeded.

Such searches require careful consideration of zero, negative values, overflow in other programming languages, and the mathematical meaning of the accumulated quantity.

## Complexity analysis

For an array of `n` elements, standard linear search has:

| Case | Time |
|---|---:|
| Best case | O(1) |
| Average case | O(n) |
| Worst case | O(n) |

The auxiliary space is normally:

    O(1)

because only a small fixed number of variables are required.

If a set, dictionary, or result list is introduced, the space complexity can increase to O(n) or O(k), depending on the problem.

## Best case

The best case occurs when the desired value is at the first position.

Only one comparison is needed.

Therefore:

    O(1)

is the best-case time complexity.

## Worst case

The worst case occurs when:

- the target is at the last position, or
- the target is absent

The entire array must be examined.

Therefore:

    O(n)

is the worst-case complexity.

## Average case

For a uniformly distributed successful search, the expected number of comparisons is approximately:

    (n + 1) / 2

This is still O(n).

The exact average depends on assumptions about where targets occur and how frequently searches succeed.

## Linear search versus binary search

| Property | Linear search | Binary search |
|---|---|---|
| Requires sorted data | No | Yes, under standard assumptions |
| Worst-case search | O(n) | O(log n) |
| Implementation | Simple | More involved |
| Works naturally on unsorted arrays | Yes | No |
| Extra space for iterative version | O(1) | O(1) |
| Best use | Small or unsorted data | Large sorted data |

Binary search can be much faster for large sorted collections, but sorting the data or maintaining sorted order also has a cost.

## When linear search is appropriate

Linear search is a reasonable choice when:

- the array is small
- the array is unsorted
- searches are infrequent
- data changes frequently
- simplicity is important
- maintaining an index is unnecessary
- the result depends on sequential conditions

The simplest correct algorithm is often preferable when performance requirements are modest.

## When linear search becomes inefficient

Repeated searches through a large collection can become expensive.

For example, performing `m` separate linear searches over `n` elements can require O(nm) work in the worst case.

Possible alternatives include:

- hash-based indexes
- dictionaries
- sets
- sorted structures
- binary search
- database indexes
- specialized indexing systems

The appropriate choice depends on data organization and workload.

## Time-space trade-offs

A central theme in searching problems is the trade-off between computation time and memory.

A plain linear search:

    Time: O(n)
    Space: O(1)

A set-based membership solution:

    Average time: O(n) construction or processing
    Lookup: O(1) average
    Space: O(n)

A precomputed dictionary index:

    Construction: O(n) average
    Repeated lookup: O(1) average
    Space: O(n)

Using additional memory can therefore make repeated searches much faster.

## Common edge cases

A robust search implementation should consider:

- empty arrays
- one-element arrays
- target at index zero
- target at the last index
- target absent
- all values equal
- multiple duplicates
- negative values
- zero
- `None`
- floating-point values
- NaN
- mixed data types
- invalid search ranges
- invalid step sizes

The script demonstrates these cases explicitly.

## Empty arrays

Searching an empty array should not attempt to access index zero.

Typical return conventions include:

    -1

for an absent index, or:

    None

for an absent object or value.

The appropriate convention should be documented by the function.

## One-element arrays

A one-element array tests both boundary behavior and equality handling.

Examples:

    [10], target=10
    [10], target=20

The first should produce index zero, while the second should indicate absence.

## Absent targets

A search must define what happens when the target does not exist.

The script commonly uses:

    -1

for an absent index.

Python's built-in `list.index()` instead raises `ValueError`.

Neither convention is universally correct. The API contract determines the appropriate behavior.

## Error handling

Some operations are undefined for empty arrays.

For example, there is no maximum value in an empty collection.

The script uses `ValueError` for such cases.

This is preferable to silently returning an arbitrary value.

Input validation is also demonstrated for parameters such as:

- tolerance
- minimum length
- frequency
- step
- search range

## Search result design

A search function may return different forms depending on the problem:

| Requirement | Suitable result |
|---|---|
| Existence | Boolean |
| First position | Integer index |
| Last position | Integer index |
| All positions | List of indexes |
| First matching object | Object or `None` |
| Pair search | Tuple of indexes |
| Matrix search | Row-column tuple |
| Failure with exceptional semantics | Exception |

Choosing the correct return representation prevents ambiguity.

## Search versus filtering

Searching normally asks for one or a limited number of results and can often terminate early.

Filtering asks for all elements satisfying a condition.

For example:

"Find the first even number"

is a search.

"Find every even number"

is a filtering-style operation.

Confusing the two can lead to unnecessary computation.

## Search versus counting

Searching for the first occurrence may stop early.

Counting all occurrences requires examining the complete collection.

Therefore:

    first occurrence -> potentially O(1) best case

while:

    count occurrences -> O(n)

even when the target occurs near the beginning.

## Search versus indexing

An index is a data structure created to make future searches faster.

A one-time linear search may be preferable to building an index.

Repeated searches can justify the additional memory and construction cost of an index.

This distinction is especially important in large applications and databases.

## Common mistakes

### Returning a value instead of an index

If the problem asks for a position, returning the matching value is incorrect even though the search itself succeeded.

### Returning the first occurrence for a last-occurrence problem

An immediate `return` is correct for first occurrence but incorrect when the last occurrence is required.

### Stopping while finding all occurrences

The all-occurrences problem requires the entire array to be examined.

### Assuming sorted data

Linear search works regardless of ordering. Other algorithms may not.

The algorithm must match the actual data assumptions.

### Ignoring empty input

Direct access such as:

    array[0]

is invalid for an empty array.

### Incorrect boundary handling

Neighbor-based problems must not access:

    array[index + 1]

when `index` is already the final position.

### Using nested loops unnecessarily

A set or dictionary can often replace an O(n²) membership problem with O(n) average processing.

### Overusing recursion

Recursive linear search is educational but is usually inferior to iteration for large Python sequences.

### Ignoring floating-point behavior

Exact equality can be unreliable for computed floating-point values.

### Ignoring NaN

NaN does not compare equal to itself.

### Losing ordering

Converting an array to a set may remove the information required to determine first or last occurrences.

## Implementation best practices

A good search implementation should:

- define the input contract
- define the result contract
- handle absence explicitly
- handle empty input where relevant
- preserve order when required
- stop early when possible
- avoid unnecessary mutation
- use appropriate data structures
- document complexity
- test boundary conditions
- validate parameters that affect correctness
- avoid premature optimization

## Security considerations

Array searching itself is not generally a security-sensitive algorithm, but search functions often process external or untrusted data in real applications.

Relevant considerations include:

- validating expected input types
- validating array sizes when input size can be attacker-controlled
- avoiding excessive repeated searches that could create performance problems
- preventing unexpected exceptions from malformed records
- avoiding assumptions about dictionary keys or object attributes
- setting reasonable limits when processing very large input

For untrusted input, computational complexity can become a security concern. An intentionally large collection combined with an O(n²) search strategy can consume substantially more CPU than an O(n) approach.

## Production performance

Performance should be evaluated according to actual workload.

A linear scan over a few dozen elements is normally inexpensive.

A linear scan over millions of elements repeated thousands of times can become expensive.

For repeated queries, a precomputed set or dictionary may provide a significant improvement.

The important design question is not simply:

"Which algorithm is theoretically fastest?"

It is:

"What combination of data structure, algorithm, memory, update cost, and query frequency fits the workload?"

## Practical problem-solving method

When solving a searching problem, identify the exact requirement first.

Ask:

1. Is the target an exact value or a condition?
2. Is the array sorted?
3. Is only one result required?
4. Is it the first occurrence?
5. Is it the last occurrence?
6. Are all occurrences required?
7. Is a count required?
8. Are duplicates important?
9. Can the search stop early?
10. Will the collection be searched repeatedly?
11. Are additional data structures permitted?
12. What should happen when no result exists?
13. What are the boundary cases?
14. What are the time and space constraints?

This sequence prevents many common implementation errors.

## Real-world applications

Array searching appears in many practical systems.

Examples include:

### User records

Searching for the first user with a particular identifier.

### Transactions

Finding transactions associated with a particular account or value.

### Logs

Locating the first event satisfying a severity or timestamp condition.

### Inventory

Searching for a product by identifier or finding the first product below a stock threshold.

### Financial analysis

Finding the first price crossing a threshold, the last occurrence of a particular value, or the first transaction meeting a condition.

### Data processing

Finding missing values, duplicate records, unique values, or records matching business rules.

### Monitoring

Finding the first metric that exceeds a threshold.

### Text processing

Finding characters, words, prefixes, suffixes, or records satisfying text conditions.

## Important distinctions

### First occurrence versus first matching condition

First occurrence searches for equality:

    value == target

First matching condition searches using a predicate:

    condition(value)

These are related but not identical problems.

### Last occurrence versus reverse search

A left-to-right last-occurrence search must usually scan the complete array.

A right-to-left search can stop at the first match.

Both can produce the last index.

### Duplicate versus consecutive duplicate

A duplicate can occur anywhere in the array.

A consecutive duplicate requires adjacent equal elements.

For:

    [1, 2, 1]

there is a duplicate but no consecutive duplicate.

For:

    [1, 2, 2]

there is a consecutive duplicate.

### Unique versus non-repeating

A unique value is often used to mean a value appearing exactly once.

A non-repeating element generally means the same thing in array-searching problems, but problem statements should define terminology precisely.

## Testing strategy

Search algorithms should be tested against representative categories.

A useful test set includes:

- empty array
- single element
- target at first position
- target at last position
- target absent
- repeated target
- all elements identical
- negative numbers
- zero
- duplicate pairs
- floating-point values
- special values such as NaN
- boundary ranges
- invalid parameters

The script includes assertion-based tests and cross-checks against Python's built-in list behavior.

## Cross-checking implementations

A useful development technique is to compare a custom implementation with a trusted built-in behavior.

For example, Python's:

    list.index()

can be used as a reference for first-occurrence searches.

The main behavioral difference is the failure convention:

    list.index() -> raises ValueError

while the custom implementation returns:

    -1

Cross-checking helps identify implementation errors while developing algorithms.

## Python-specific implementation choices

The script demonstrates several Python mechanisms for implementing searches:

- `for` loops
- `while` loops
- `enumerate()`
- `range()`
- `set`
- `dict`
- `next()`
- generator expressions
- `lambda`
- `isinstance()`
- `casefold()`
- `math.isnan()`
- exception handling
- assertions
- classes and object attributes

Each mechanism is appropriate for different forms of search logic.

## `enumerate()` versus index loops

Both approaches are valid.

An explicit index loop:

    for index in range(len(array)):
        value = array[index]

works but requires manual indexing.

Using `enumerate()`:

    for index, value in enumerate(array):

is generally clearer when both the index and value are required.

## `for` versus `while`

A `for` loop is normally the clearest option for sequential traversal.

A `while` loop can be useful when:

- traversal boundaries are dynamically controlled
- multiple pointers are involved
- the search uses a custom progression

For straightforward linear search, `for` is usually more readable.

## `next()` and generator expressions

Python's `next()` can express "return the first item satisfying a condition."

The generator produces candidates lazily, so values after the first successful match do not need to be generated.

This provides a concise alternative to an explicit loop.

For educational and production code, the choice should prioritize readability and consistency with the surrounding code.

## Data structure selection

The correct search structure depends on the problem.

| Requirement | Useful structure |
|---|---|
| Sequential scan | List or tuple |
| Membership checking | Set |
| Value-to-index lookup | Dictionary |
| Frequency counting | Dictionary |
| All positions | Dictionary of lists |
| Sorted lookup | Sorted sequence with binary search |
| Repeated record lookup | Appropriate indexed structure |

Choosing the data structure can have a greater performance impact than small changes to the loop itself.

## Algorithmic trade-offs

There is no universally best search implementation.

A simple O(n) linear search may be better than a more complicated indexed solution when:

- the collection is tiny
- searches are rare
- data changes frequently
- memory is limited
- implementation simplicity matters

An indexed solution is preferable when:

- the collection is large
- searches are frequent
- values change infrequently
- additional memory is available
- predictable lookup performance is important

## Production API design

A reusable search function should clearly define:

- accepted input types
- whether input may be empty
- target semantics
- duplicate semantics
- failure behavior
- whether indexes or values are returned
- whether the input is mutated
- complexity
- special-value behavior

Ambiguous search contracts are a common source of bugs.

## Limitations of linear search

Linear search has fundamental limitations.

For an unsorted array, an arbitrary target may require examining every element.

Its worst-case time complexity is therefore O(n).

No implementation detail can remove that fundamental limitation without additional information or preprocessing.

Faster repeated searching generally requires exploiting structure such as:

- ordering
- hashing
- indexing
- specialized data structures

## Scope of the Python script

The accompanying script progresses through:

- basic linear search
- existence checking
- first occurrence
- last occurrence
- all occurrences
- counting
- conditional searches
- duplicate detection
- frequency analysis
- unique and repeating values
- pair and triplet searches
- subarray searching
- string searching
- object searching
- nested arrays
- recursive searching
- sentinel search
- custom predicates
- floating-point and NaN handling
- range and suffix searches
- multiple-target searches
- precomputed indexes
- prefix and cumulative-condition searches
- testing
- complexity analysis
- practical implementation considerations

The examples are implemented as executable Python rather than being presented only as theoretical descriptions.
