# Array complexity

## Introduction

An array is an indexed collection of elements in which each element can be identified by a position. Arrays are one of the most important structures for understanding algorithmic complexity because their storage model makes some operations extremely efficient while making other operations expensive.

The central property of an array is direct indexed access. When elements occupy fixed-size positions in a contiguous storage region, the location of an element can be calculated from the starting address and its index. This makes access by index an O(1) operation.

Array performance becomes more interesting when elements are inserted or removed. Inserting at the end can be inexpensive, while inserting at the beginning or middle may require many elements to move. Dynamic arrays introduce another important concept: resizing. A resize can take O(n) time, but geometric growth makes repeated append operations O(1) amortized.

This study script develops array complexity from basic operations through dynamic-array implementation, searching, sorting, prefix sums, two-pointer algorithms, sliding windows, space complexity, cache behavior, testing, and production considerations.

## Array terminology

An array can be described using several fundamental terms.

**Element** is an individual value stored in the array.

**Index** is the position used to identify an element. Python uses zero-based indexing, so the first element has index 0.

**Length** is the number of logical elements currently stored.

**Capacity** is the amount of storage allocated for an array. Capacity is particularly important for dynamic arrays because it can be larger than the current logical size.

**Contiguous storage** means array elements occupy adjacent memory locations. Traditional low-level arrays commonly use this representation.

**Random access** means accessing an element directly using its index without scanning earlier elements.

**Traversal** means visiting array elements sequentially.

**Resizing** means allocating a different storage region and transferring existing elements into it.

## The basic array operation model

For a conventional array, the most important complexity characteristics are:

| Operation | Typical complexity |
|---|---:|
| Access by index | O(1) |
| Update by index | O(1) |
| Full traversal | O(n) |
| Linear search | O(n) |
| Binary search on sorted data | O(log n) |
| Append to dynamic array | O(1) amortized |
| Insert at beginning | O(n) |
| Insert in middle | O(n) |
| Delete from beginning | O(n) |
| Delete from middle | O(n) |
| Delete from end | O(1) |

The script implements or demonstrates each of these categories.

## Why array indexing is O(1)

Suppose an array contains:

    index:  0    1    2    3
    value: 10   20   30   40

If every element occupies the same amount of storage, the address of an element can conceptually be calculated as:

    address = base_address + index × element_size

The calculation does not require inspecting the elements before the requested position. Whether the array contains 10 elements or 10 million elements, the number of conceptual address calculations remains constant.

Therefore:

    array[index] → O(1)

This is one of the defining advantages of arrays.

## Updating an array element

Replacing an element at a known index has the same direct-access property.

    values[index] = new_value

The operation does not require shifting or searching when the index is already known.

Time complexity:

    O(1)

Auxiliary space:

    O(1)

## Traversal

Traversal processes every element.

A simple summation performs one operation for each array element:

    for value in values:
        total += value

For n elements, the loop executes n times.

Therefore:

    Time = O(n)
    Auxiliary space = O(1)

The distinction between input size and auxiliary memory is important. The array itself already occupies storage. A function that only maintains a running total does not allocate another array.

## Linear search

Linear search examines elements one at a time until the target is found.

Its cases are different:

- Best case: O(1), when the first element is the target.
- Average case: O(n).
- Worst case: O(n), when the target is last or absent.
- Auxiliary space: O(1).

Linear search does not require the array to be sorted.

The script demonstrates successful searches at different positions and an unsuccessful search.

## Binary search

Binary search is substantially faster for large sorted arrays.

At every iteration, it compares the target with the middle element. If the target cannot be in one half of the remaining array, that half is discarded.

The search space changes approximately as:

    n
    n / 2
    n / 4
    n / 8
    ...

The number of divisions required to reduce the problem to one element is proportional to log₂(n).

Therefore:

    Best case = O(1)
    Average case = O(log n)
    Worst case = O(log n)

The iterative implementation uses:

    Auxiliary space = O(1)

The recursive implementation uses:

    Auxiliary stack space = O(log n)

Binary search requires sorted data. Applying it to an unsorted array violates its fundamental assumption.

## Insertion into an array

Insertion is where array structure becomes expensive.

Suppose the array is:

    [10, 20, 30, 40]

To insert 15 at index 1, the existing elements 20, 30, and 40 must move one position to the right:

    [10, 20, 30, 40]
    [10, 20, 30, 40, empty]
    [10, 15, 20, 30, 40]

The number of shifts depends on how many elements follow the insertion point.

Insertion at the beginning is O(n).

Insertion in the middle is O(n) in the worst case.

Insertion at the end is O(1) when unused capacity is available. For a dynamic array, repeated end insertion is O(1) amortized.

## Deletion from an array

Deletion has the opposite shifting behavior.

If the first element is deleted:

    [10, 20, 30, 40]

the remaining values must shift left:

    [20, 30, 40]

Deleting the first or middle element therefore has O(n) worst-case complexity.

Deleting the final element does not require subsequent elements to move, so it can be O(1).

## Static arrays

A static array has a fixed capacity.

The script implements `StaticArray` to make this behavior explicit.

A static array has predictable storage requirements, but its capacity cannot automatically grow. Once the available slots are exhausted, another operation cannot simply increase the array's size.

Its major characteristics are:

- Fixed capacity.
- O(1) indexed access.
- O(1) update by index.
- O(n) insertion requiring shifts.
- O(n) deletion requiring shifts.
- No automatic resize.
- Capacity must be planned in advance.

Static storage is useful when the maximum size is known and predictable memory usage is important.

## Dynamic arrays

A dynamic array can grow when its capacity is exhausted.

The script implements a `DynamicArray` class to demonstrate the mechanism.

Suppose capacity is initially 2:

    capacity = 2
    size = 0

After two insertions:

    capacity = 2
    size = 2

A third insertion requires additional storage. A larger storage region is allocated and the existing elements are copied.

For example:

    old capacity = 2
    new capacity = 4

The copying operation itself is O(n).

This creates an important distinction between individual operation complexity and amortized complexity.

## Size versus capacity

Dynamic arrays normally maintain two related values:

    size
    capacity

Size describes how many elements are logically stored.

Capacity describes how many elements can fit before another resize is required.

For example:

    size = 3
    capacity = 8

There are three logical elements but eight allocated positions.

The unused capacity is intentional. It allows additional elements to be appended without immediately allocating new storage.

## Resizing

A resize generally involves:

- Allocating a new storage region.
- Copying existing elements.
- Replacing the old storage reference.
- Continuing the insertion.

If n elements must be copied, that resize costs O(n).

The important design choice is how much additional capacity to allocate.

If capacity increased by only one slot each time, repeated appends could cause:

    O(1) + O(2) + O(3) + ... + O(n)

which is O(n²) total copying.

Geometric growth avoids this problem.

## Amortized analysis

With geometric growth, capacity may follow a sequence such as:

    1
    2
    4
    8
    16
    32

The total number of copied elements across many resizes is bounded by a constant multiple of n.

For example, the copying work resembles:

    1 + 2 + 4 + 8 + ... + n

This geometric series is O(n).

Therefore, across n append operations:

    total work = O(n)

and the amortized cost of one append is:

    O(n) / n = O(1)

This does not mean every append is O(1). A particular append that triggers resizing can still be O(n).

The correct distinction is:

    Worst-case individual append = O(n)
    Amortized append = O(1)

Amortized analysis is not the same as saying that every operation takes constant time.

## Dynamic-array shrinking

Growth is only one side of dynamic storage.

If many elements are removed, an implementation may reduce capacity to avoid retaining excessive unused memory.

The script demonstrates a policy in which capacity can be reduced when the logical size becomes sufficiently small relative to capacity.

A resize-on-every-delete policy is generally undesirable because it can produce repeated allocation and copying.

A threshold-based strategy reduces the likelihood of repeated grow-shrink oscillation.

## Static versus dynamic arrays

| Property | Static array | Dynamic array |
|---|---|---|
| Capacity | Fixed | Adjustable |
| Indexed access | O(1) | O(1) |
| End append | O(1) if capacity exists | O(1) amortized |
| Resize | Not available | Occasional O(n) |
| Beginning insertion | O(n) | O(n) |
| Middle insertion | O(n) | O(n) |
| End deletion | O(1) | O(1) |
| Memory flexibility | Low | Higher |
| Capacity planning | Important | Usually handled automatically |

Dynamic arrays provide flexibility at the cost of occasional reallocation and unused capacity.

## Python lists

Python's built-in `list` behaves conceptually like a dynamic array.

Typical behavior includes:

- Indexed access: O(1).
- Assignment by index: O(1).
- `append`: O(1) amortized.
- `pop()` from the end: O(1).
- `insert(0, value)`: O(n).
- `pop(0)`: O(n).
- Searching with membership: O(n) in the general case.

The exact internal implementation details are language-runtime specific, but the dynamic-array model is useful for understanding the performance characteristics of ordinary Python list operations.

## Big-O notation

Big-O notation describes asymptotic growth.

The most important classes in this study are:

| Complexity | Growth behavior |
|---|---|
| O(1) | Constant |
| O(log n) | Logarithmic |
| O(n) | Linear |
| O(n log n) | Linearithmic |
| O(n²) | Quadratic |
| O(2ⁿ) | Exponential |

For array algorithms, O(1), O(log n), O(n), O(n log n), and O(n²) appear frequently.

## Sequential versus nested loops

Two sequential loops do not automatically produce O(n²).

For example, one O(n) loop followed by another O(n) loop gives:

    O(n) + O(n)
    = O(2n)
    = O(n)

Constant factors are ignored in asymptotic Big-O notation.

A nested loop often produces O(n²), but loop structure must be analyzed carefully.

The script includes a triangular nested loop where the number of iterations is approximately:

    n(n - 1) / 2

which is still O(n²).

The important principle is to count actual growth rather than simply counting the number of loop statements.

## Dominant terms

If an algorithm performs:

    O(n²) + O(n)

the quadratic term dominates as n grows.

Therefore:

    O(n² + n) = O(n²)

Similarly:

    O(5n + 20) = O(n)

The purpose of simplification is to describe asymptotic growth rather than exact execution time.

## Best, average, and worst cases

An algorithm can have different complexity depending on the input.

Linear search demonstrates this clearly.

For:

    [10, 20, 30, 40, 50]

searching for 10 finishes immediately.

Searching for 50 requires five comparisons.

Searching for a value that does not exist also requires checking every element.

Therefore, a single algorithm can have different best and worst cases.

This distinction is important whenever the input distribution or operation position changes performance.

## Space complexity

Time complexity measures how computational work grows.

Space complexity measures memory requirements.

For an array algorithm, distinguish between:

- Input storage.
- Output storage.
- Auxiliary space.

An in-place reversal changes the original array and uses O(1) auxiliary space.

A copied reversal creates another array and therefore uses O(n) additional storage.

Both take O(n) time, but they have different memory requirements.

## In-place algorithms

An in-place algorithm modifies the existing array instead of constructing a full replacement structure.

The two-pointer reversal demonstrates this:

    left →        ← right

The elements at the two positions are exchanged, and both pointers move toward the center.

Time:

    O(n)

Auxiliary space:

    O(1)

In-place processing can be valuable when memory is constrained.

The trade-off is that the original input is modified.

## Array slicing

A subtle Python performance issue is slicing.

An expression such as:

    values[start:end]

creates a new list.

If the slice contains k elements, creating it requires approximately:

    Time = O(k)
    Space = O(k)

This differs from direct indexing:

    values[index]

which is O(1).

For performance-sensitive code, replacing unnecessary slices with index-based traversal can reduce temporary memory usage.

## Prefix sums

Prefix sums illustrate how preprocessing can improve repeated queries.

Given:

    [5, 2, 7, 3, 9, 1]

a prefix representation can store cumulative sums.

Once constructed, a range sum can be computed using subtraction of two prefix values.

Construction:

    O(n)

Each range query:

    O(1)

Additional storage:

    O(n)

This represents a classic time-space trade-off. More memory is used to reduce repeated computation.

## Two-pointer technique

The two-pointer method is useful when array structure allows unnecessary searches to be eliminated.

For a sorted array, two pointers can begin at opposite ends.

If the current sum is too small, move the left pointer forward.

If the current sum is too large, move the right pointer backward.

Each pointer moves only forward or backward through the array, so the total number of pointer movements is O(n).

The method therefore solves the sorted two-sum problem in:

    Time = O(n)
    Auxiliary space = O(1)

A brute-force pair comparison would require O(n²) time.

## Sliding-window technique

Sliding windows optimize repeated work over contiguous sections of an array.

For a fixed window size k, a naive algorithm can recompute every window from scratch.

That approach may require:

    O(nk)

work.

The sliding-window method calculates the first window once and then updates it:

    add the new element
    subtract the element leaving the window

Each element is handled a constant number of times.

Therefore:

    Time = O(n)
    Auxiliary space = O(1)

## Maximum subarray and Kadane's algorithm

The maximum-subarray problem asks for the largest sum obtainable from a non-empty contiguous subarray.

A brute-force solution can be quadratic or worse depending on implementation.

Kadane's algorithm reduces the problem to O(n).

The key state is:

    current best subarray ending here
    best subarray found anywhere so far

For each value:

    current = max(value, current + value)

The algorithm also correctly handles arrays containing only negative numbers.

For:

    [-8, -3, -5, -2]

the answer is:

    -2

because the subarray must be non-empty.

## Two-dimensional arrays

A two-dimensional array can be modeled as rows and columns.

For an r × c matrix, visiting every cell requires:

    O(r × c)

time.

The script demonstrates nested traversal of a matrix.

Two-dimensional arrays are common in:

- Images.
- Grids.
- Tables.
- Dynamic programming.
- Numerical computing.
- Matrix algorithms.

## Rectangular versus jagged arrays

A list of lists can represent either a rectangular matrix or an irregular structure.

Rectangular:

    3 rows × 3 columns

Jagged:

    row 1 → 3 elements
    row 2 → 5 elements
    row 3 → 2 elements

Algorithms should not assume rectangular dimensions unless the representation guarantees them.

The script includes validation for rectangular matrices.

## Matrix aliasing

Python has a subtle issue when creating nested lists.

Using the same inner list reference for multiple rows means modifying one row can unexpectedly modify all rows.

The safe construction creates an independent list for each row.

This is a correctness issue rather than merely a style preference.

Understanding references is important when arrays contain mutable objects.

## Sorting and array complexity

Sorting is often used before more efficient array operations.

The script implements several algorithms.

### Selection sort

Selection sort repeatedly selects the smallest remaining value.

Its complexity is:

    Best = O(n²)
    Average = O(n²)
    Worst = O(n²)
    Auxiliary space = O(1)

Its simple structure makes it useful for studying nested-loop complexity, but it is generally inefficient for large inputs.

### Insertion sort

Insertion sort builds a sorted prefix.

Its complexity is:

    Best = O(n)
    Average = O(n²)
    Worst = O(n²)

It can perform well when the input is already or nearly sorted.

Its auxiliary space is O(1) in the implementation shown.

### Merge sort

Merge sort uses divide and conquer.

The array is repeatedly divided into smaller pieces, and sorted pieces are merged.

Its complexity is:

    Best = O(n log n)
    Average = O(n log n)
    Worst = O(n log n)

The implementation creates additional arrays, giving O(n) auxiliary storage.

### Quicksort

Quicksort partitions the array around a pivot.

Typical behavior:

    Average = O(n log n)
    Worst = O(n²)

The worst case can occur when partitioning repeatedly produces highly unbalanced subproblems.

Pivot selection is therefore important.

## Merging sorted arrays

Two already sorted arrays can be merged in linear time.

If the arrays have lengths n and m:

    Time = O(n + m)

Two pointers track the next candidate in each array.

Because each element is processed once, the algorithm does not need to repeatedly search either input.

## Duplicate detection

The script compares two approaches.

A pairwise comparison checks every possible pair:

    Time = O(n²)
    Space = O(1)

A hash-based method maintains a set of previously observed values:

    Average time = O(n)
    Space = O(n)

This is an important complexity trade-off.

The faster approach uses additional memory.

## Frequency counting

A frequency table maps each distinct value to the number of occurrences.

For n total elements and k distinct values:

    Average time = O(n)
    Space = O(k)

If every value is unique, k can approach n, giving O(n) additional space.

## Array rotation

The script implements right rotation using three reversals.

For:

    [1, 2, 3, 4, 5, 6]

a rotation by two positions produces:

    [5, 6, 1, 2, 3, 4]

The algorithm operates in:

    O(n) time
    O(1) auxiliary space

Using modulo n is important because rotating by n positions produces the original array, and rotating by more than n positions can be reduced to a smaller equivalent rotation.

## Stable movement of zeros

The zero-moving example preserves the relative order of non-zero values.

For:

    [0, 1, 0, 3, 12]

the result is:

    [1, 3, 12, 0, 0]

The implementation uses a write position to compact useful elements toward the front.

Time:

    O(n)

Auxiliary space:

    O(1)

## Common mistake: off-by-one errors

Array indexes have boundaries.

For an array of length n, valid zero-based indexes are:

    0 through n - 1

A loop intended to process the first k elements should process:

    range(k)

not an incorrectly calculated endpoint.

The script validates values such as k to prevent invalid access.

## Common mistake: modifying while iterating

Removing elements while moving through the same array can cause elements to shift into positions that have already been processed.

This can cause elements to be skipped.

The script demonstrates two approaches:

- Iterating over a copy.
- Using in-place compaction with a write index.

The copy-based approach uses O(n) temporary space.

The compaction approach uses O(1) auxiliary space.

## Empty arrays

Empty arrays require explicit consideration.

Operations such as:

- Accessing index 0.
- Finding a minimum.
- Finding a maximum.
- Calculating an average.

may not have valid results for an empty array.

The script raises explicit exceptions for operations where an empty input has no meaningful answer.

Good array algorithms define their empty-input behavior rather than allowing accidental failures.

## Duplicate values

Algorithms should specify whether uniqueness matters.

For example, "second-largest element" can mean:

- The second position after sorting.
- The second-largest value allowing duplicates.
- The second-largest distinct value.

The script explicitly implements the third interpretation.

For:

    [10, 10, 8, 7]

the second-largest distinct value is:

    8

Clear definitions prevent logically correct code from solving the wrong problem.

## Negative numbers

Negative values can expose hidden assumptions.

A maximum-subarray algorithm that initializes its answer to zero would incorrectly return zero for an all-negative array if the problem requires a non-empty subarray.

Correct initialization should account for the actual first element.

The script demonstrates this case.

## Large integers and overflow

Python integers can grow beyond conventional fixed-width integer ranges.

This behavior differs from languages that use fixed-width integer types.

An algorithm involving sums, products, indexes, or memory sizes may therefore behave differently when translated between programming languages.

Algorithmic complexity does not eliminate numerical representation issues.

## Memory allocation and external input

Array size should not blindly be accepted from untrusted input.

A request to allocate an extremely large array can cause:

- Excessive memory consumption.
- Slow allocation.
- Process termination.
- Denial-of-service conditions.

The script includes a bounded allocation example.

Production systems should establish sensible limits based on the application and available resources.

## Cache locality

Big-O notation does not describe every hardware-level performance effect.

Contiguous arrays can have good spatial locality because nearby elements are stored near one another.

Sequential traversal can therefore interact efficiently with CPU caches.

Two algorithms can have the same asymptotic complexity while exhibiting different real-world performance because of:

- Memory access patterns.
- Cache misses.
- Branch prediction.
- Allocation behavior.
- Interpreter overhead.
- CPU architecture.

This does not replace complexity analysis. It explains why asymptotically equivalent algorithms can still perform differently.

## Complexity versus measured execution time

The script includes a simple timing function based on a monotonic performance clock.

Timing can demonstrate practical differences, but a single timing result is not a complexity proof.

Measured performance can be influenced by:

- Hardware.
- Operating-system scheduling.
- Python interpreter state.
- Background processes.
- CPU frequency.
- Memory hierarchy.
- Input characteristics.

Complexity analysis describes growth behavior. Benchmarking measures behavior under specific experimental conditions.

Both perspectives are useful.

## Preallocation

When the final number of elements is known, preallocation can reduce repeated resizing in systems where allocation is explicitly controlled.

The script demonstrates the general concept with a pre-sized Python list.

The precise behavior of Python's internal list allocation is implementation-specific, so the example should not be interpreted as a public interface to Python's allocator.

## Output space versus auxiliary space

Consider an algorithm that returns a new array containing n elements.

The output itself requires O(n) storage.

If the algorithm also uses only constant temporary memory, its auxiliary space can still be described as O(1), depending on the convention being used.

Complexity discussions should clearly state whether they count:

- Input storage.
- Output storage.
- Temporary auxiliary storage.

This avoids ambiguous claims such as simply saying "space is O(n)" without explaining what that memory represents.

## Recursive versus iterative implementations

The script provides both iterative and recursive binary search.

Both have:

    Time = O(log n)

Their space requirements differ.

Iterative binary search:

    Auxiliary space = O(1)

Recursive binary search:

    Auxiliary stack space = O(log n)

The algorithmic idea is the same, but implementation strategy changes memory behavior.

## Complexity of common array patterns

Several patterns are especially important.

A single complete pass:

    O(n)

Two complete sequential passes:

    O(n) + O(n)
    = O(n)

A nested complete pass:

    O(n²)

Repeatedly halving the problem:

    O(log n)

Divide and conquer with linear work at each level:

    O(n log n)

Copying n elements:

    O(n) time
    O(n) additional storage

Accessing one indexed element:

    O(1)

These patterns form a practical basis for analyzing more complicated algorithms.

## Time-space trade-offs

Improving time complexity often requires additional memory.

Duplicate detection demonstrates:

    O(n²) time, O(1) space

versus:

    O(n) average time, O(n) space

Prefix sums demonstrate another trade-off:

    Preprocessing = O(n)
    Query = O(1)
    Storage = O(n)

The correct choice depends on the workload.

If there are many repeated queries, preprocessing may be valuable.

If memory is severely constrained and queries are rare, recomputation may be preferable.

## Choosing an array-based approach

Arrays are especially appropriate when:

- Indexed access is frequent.
- Elements are processed sequentially.
- Data has a naturally ordered structure.
- End insertion is common.
- Contiguous storage is beneficial.
- Memory overhead should be relatively small.

Arrays become less attractive when frequent operations require insertion or deletion near the beginning or middle.

The appropriate alternative depends on the broader workload and data-structure requirements.

## Real-world applications

Array structures occur throughout computing.

### Sensor data

Measurements collected over time can be represented as an ordered sequence.

### Images

An image can be represented as a two-dimensional or three-dimensional array of pixel values.

### Audio

Digital audio consists of ordered samples.

### Time-series data

Values indexed by time are naturally represented using sequential structures.

### Lookup tables

When an identifier maps naturally to a bounded integer index, direct array access can provide O(1) lookup.

### Machine-learning tensors

Numerical models commonly manipulate multidimensional arrays representing vectors, matrices, batches, and higher-dimensional data.

### Database and systems programming

Buffers and memory regions frequently use contiguous storage because predictable indexing and locality are valuable.

## Production considerations

Array complexity should be evaluated together with actual application requirements.

Important questions include:

- Is random access frequent?
- How often are insertions performed?
- Where do insertions occur?
- How frequently is data removed?
- Is the final size known?
- Is memory limited?
- Is the array frequently copied?
- Is sorting required?
- Are lookups performed on sorted data?
- Are repeated range queries required?
- Is preserving element order important?
- Can the original array be modified?
- Does the runtime use dynamic arrays internally?

An algorithm with theoretically good complexity may still be inappropriate if its memory behavior conflicts with system requirements.

## Testing strategy

The script uses several levels of testing.

Simple assertions verify expected outputs for known cases.

Randomized testing generates many small arrays and compares algorithm behavior with simpler reference implementations.

This approach can expose:

- Empty-array failures.
- Duplicate handling errors.
- Negative-number errors.
- Boundary errors.
- Search mistakes.
- Sorting errors.
- Incorrect pointer movement.

Testing complexity algorithms is particularly valuable because small indexing errors can produce correct results for ordinary examples while failing at boundaries.

## Important complexity distinctions

Several distinctions should remain clear.

### O(1) versus O(1) amortized

Direct indexed access is normally O(1) for every operation.

Dynamic-array append is O(1) amortized, but an individual resize-triggering append can be O(n).

### O(n) time versus O(n) space

These measure different resources.

An algorithm may take O(n) time while using O(1) auxiliary memory.

### Average case versus amortized case

Average-case analysis depends on assumptions about input or operation distributions.

Amortized analysis evaluates total cost over a sequence of operations according to a defined operation strategy.

### Static versus dynamic capacity

Static arrays have fixed capacity.

Dynamic arrays can reallocate as their size changes.

### Sorted versus unsorted arrays

Binary search depends on sorted ordering.

Linear search does not.

### In-place versus copied algorithms

In-place algorithms usually reduce auxiliary memory but may mutate the original data.

Copied algorithms can preserve the input but require additional storage.

## Complexity reference table

| Algorithm or operation | Best | Average | Worst | Auxiliary space |
|---|---:|---:|---:|---:|
| Index access | O(1) | O(1) | O(1) | O(1) |
| Update by index | O(1) | O(1) | O(1) | O(1) |
| Traversal | O(n) | O(n) | O(n) | O(1) |
| Linear search | O(1) | O(n) | O(n) | O(1) |
| Binary search | O(1) | O(log n) | O(log n) | O(1) iterative |
| Array insertion | O(1) at end | O(n) | O(n) | O(1) |
| Array deletion | O(1) at end | O(n) | O(n) | O(1) |
| Dynamic append | O(1) | O(1) amortized | O(n) | O(1) per operation |
| Duplicate check, pairwise | O(n²) | O(n²) | O(n²) | O(1) |
| Duplicate check, hashing | O(n) average | O(n) average | O(n²) under pathological hashing assumptions | O(n) |
| Prefix construction | O(n) | O(n) | O(n) | O(n) |
| Prefix range query | O(1) | O(1) | O(1) | O(1) per query |
| Fixed sliding window | O(n) | O(n) | O(n) | O(1) |
| Kadane's algorithm | O(n) | O(n) | O(n) | O(1) |
| Selection sort | O(n²) | O(n²) | O(n²) | O(1) |
| Insertion sort | O(n) | O(n²) | O(n²) | O(1) |
| Merge sort | O(n log n) | O(n log n) | O(n log n) | O(n) |
| Quicksort | O(n log n) typical | O(n log n) | O(n²) | O(log n) average stack |
| Merge two sorted arrays | O(n + m) | O(n + m) | O(n + m) | O(n + m) for output |

## Practical analysis checklist

When analyzing an array algorithm, determine:

- The input size.
- The number of array elements processed.
- Whether the algorithm performs one or multiple passes.
- Whether loops are nested.
- Whether the search space is repeatedly divided.
- Whether elements are shifted.
- Whether the array is copied.
- Whether slicing creates temporary storage.
- Whether sorting is required.
- Whether the array is sorted before searching.
- Whether a hash table or set changes the space-time trade-off.
- Whether the algorithm modifies the original array.
- Whether a dynamic-array resize can occur.
- Whether the stated complexity is worst-case, average-case, best-case, or amortized.
- Whether auxiliary space and output space are being distinguished.

The most important principle is to analyze how the amount of work and memory changes as the number of array elements grows, rather than focusing only on the behavior of one small example.
