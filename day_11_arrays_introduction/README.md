# Arrays introduction

## Topic introduction

An array is a fundamental data structure used to store multiple values under a single collection name. Each element is associated with an index, which provides a direct way to identify its position.

A traditional array generally has these characteristics:

- Elements are stored in contiguous memory.
- Elements normally have the same data type.
- Elements are accessed through indexes.
- Random access by index is efficient.
- The logical size may be fixed or dynamically managed depending on the implementation.

Arrays form the basis for many higher-level data structures and algorithms. They are used in numerical computing, matrices, image processing, audio processing, scientific data, financial time series, buffers, lookup tables, and many other systems.

The Python script demonstrates arrays using Python lists, `array.array`, a fixed-size custom implementation, and a dynamic array implementation.

## Fundamental terminology

### Element

An element is an individual value stored in an array.

For example:

    [10, 20, 30, 40]

contains four elements.

### Index

An index identifies the position of an element.

Python uses zero-based indexing:

    Index:   0   1   2   3
    Value:  10  20  30  40

Therefore:

- index `0` refers to `10`
- index `1` refers to `20`
- index `2` refers to `30`
- index `3` refers to `40`

### Size

The size, or logical length, is the number of elements currently stored.

For:

    [10, 20, 30]

the size is `3`.

### Capacity

Capacity represents the amount of storage available before an array needs to allocate additional storage.

Size and capacity are different concepts in dynamic arrays.

For example, a dynamic array could have:

    size = 5
    capacity = 8

Five positions contain meaningful elements, while storage exists for three additional elements.

### Traversal

Traversal means visiting the elements of an array, usually from the first element to the last.

### Insertion

Insertion adds a new element at a specified position.

### Deletion

Deletion removes an element from a specified position.

### Update

Updating replaces an existing element with another value.

### Search

Searching determines whether a value exists and, when appropriate, identifies its position.

## Indexing

Python arrays represented by lists use zero-based indexing.

For an array containing `n` elements, the valid positive indexes are:

    0 through n - 1

For example:

    values = [100, 200, 300, 400, 500]

The valid indexes are:

    0, 1, 2, 3, 4

Trying to access index `5` produces an `IndexError`.

Python also supports negative indexing:

- `-1` means the last element.
- `-2` means the second-last element.
- `-3` means the third-last element.

Negative indexing is a Python language feature rather than a requirement of the traditional array data structure.

## Memory representation

Traditional arrays are commonly represented as contiguous blocks of memory.

Suppose an array begins at memory address `A`, every element requires `B` bytes, and an element has index `i`.

Conceptually, its address can be calculated as:

    address(i) = A + i × B

This calculation allows direct access to an element without scanning the elements before it.

That is the fundamental reason array indexing has constant-time complexity:

    O(1)

The calculation does not depend on how many elements are stored before the requested index.

## Python lists and memory representation

Python's built-in `list` should not be treated as an exact equivalent of a traditional C-style primitive array.

A Python list is a dynamic array containing references to Python objects. The references themselves are maintained in an internal array-like structure, while the objects they reference can exist elsewhere in memory.

This distinction explains why a Python list can contain values of different types:

    [10, 2.5, "Python", True]

A traditional typed array normally expects elements to follow a specified representation.

## Typed arrays

Python's standard library provides `array.array` for compact typed arrays.

The script demonstrates integer and floating-point typed arrays.

For example, an integer array can be created conceptually as:

    array("i", [1, 2, 3, 4])

The type code determines the representation used for the stored values.

Typed arrays can be useful when compact storage of primitive numeric values is important.

A Python list is generally more flexible, while `array.array` imposes stronger type restrictions.

## Array operations

The main operations demonstrated in the script are:

| Operation | Description | Typical complexity |
|---|---|---:|
| Access | Retrieve an element using an index | O(1) |
| Update | Replace an element using an index | O(1) |
| Traversal | Visit every element | O(n) |
| Linear search | Search sequentially | O(n) |
| Binary search | Search sorted data by repeatedly halving the range | O(log n) |
| Append | Add an element at the end | O(1) amortized |
| Insert at beginning | Add an element at the beginning | O(n) |
| Insert in middle | Add an element in the middle | O(n) |
| Delete from end | Remove the last element | O(1) amortized |
| Delete from beginning | Remove the first element | O(n) |
| Delete from middle | Remove an internal element | O(n) |

These complexities describe how the amount of work grows as the number of elements increases.

## Accessing an element

Access by index is one of the most important properties of an array.

For an array:

    values = [10, 20, 30, 40]

accessing:

    values[2]

directly identifies the element `30`.

The operation is O(1) because the location can be calculated from the index rather than discovered by scanning the collection.

## Traversal

Traversal visits each element.

A direct traversal is appropriate when only values are needed.

An index-based traversal is useful when both the position and value are required.

Python's `enumerate()` is particularly useful because it provides both:

    index
    value

without manually maintaining a separate counter.

Traversal requires O(n) time because an array containing `n` elements may require every element to be visited.

## Updating

Updating an element at a known index is generally O(1).

For example:

    values[2] = 75

does not require shifting other elements.

The operation simply replaces the value associated with that position.

## Insertion

Insertion is more expensive when it occurs before the end of an array.

Suppose an array contains:

    [10, 20, 30, 40]

Inserting `99` at index `1` produces:

    [10, 99, 20, 30, 40]

The existing elements `20`, `30`, and `40` must move to make room for the new element.

The number of moved elements can grow proportionally with the array size, giving O(n) worst-case complexity.

Appending at the end of a dynamic array is different. If free capacity exists, the new value can be placed directly into the next available position.

## Deletion

Deleting from the middle also requires shifting.

Consider:

    [10, 20, 30, 40, 50]

Deleting the element at index `1` produces:

    [10, 30, 40, 50]

The elements after the deleted element move one position to the left.

Therefore deletion from the beginning or middle is generally O(n).

Deleting the final element does not require other elements to move, so it is generally O(1), subject to the implementation's capacity-management behavior.

## Linear search

Linear search examines elements sequentially.

For:

    [7, 14, 21, 28, 35]

searching for `21` examines:

    7
    14
    21

The search can stop once the target is found.

Its complexity is:

- Best case: O(1)
- Average case: O(n)
- Worst case: O(n)

Linear search does not require the array to be sorted.

It is useful for unsorted data and small collections.

## Searching for duplicates

An array can contain repeated values.

For:

    [5, 2, 5, 8, 5]

the value `5` occurs at multiple positions.

The script implements a function that returns all matching indexes.

For large collections, a set can be used when the requirement is simply to determine whether a duplicate exists. This generally provides average O(1) membership checks and O(n) total processing, at the cost of additional memory.

## Binary search

Binary search is a substantially faster search technique for sorted arrays.

For example:

    [3, 8, 14, 21, 27, 35, 42]

Instead of examining every element, binary search checks the middle element and determines which half of the array can still contain the target.

Each step approximately halves the remaining search space.

Its complexity is:

    O(log n)

The critical requirement is that the data must already be sorted according to the comparison being used.

Applying ordinary binary search to unsorted data is not reliable.

## Linear search versus binary search

| Property | Linear search | Binary search |
|---|---|---|
| Requires sorted data | No | Yes |
| Worst-case time | O(n) | O(log n) |
| Implementation | Simple | More involved |
| Suitable for unsorted arrays | Yes | No |
| Useful for repeated searches | Depends on workload | Often useful |
| Requires maintained ordering | No | Yes |

Sorting an array only to perform one search may not be beneficial because sorting itself generally requires O(n log n) time.

Binary search becomes more attractive when many searches are performed against the same sorted data.

## First and last occurrence

A standard binary search can be modified to find the first or last occurrence when duplicate values exist.

For:

    [1, 2, 2, 2, 4, 5, 5, 9]

the first occurrence of `2` is at index `1`.

The last occurrence is at index `3`.

After finding a matching value, the modified algorithm continues searching toward the relevant side instead of stopping immediately.

Both operations remain O(log n).

## Fixed-size arrays

A traditional fixed-size array has a predetermined capacity.

If the capacity is three:

    capacity = 3

then the structure can store three elements.

Trying to insert a fourth element requires a different storage strategy.

The custom `FixedArray` implementation in the script demonstrates this concept explicitly.

Fixed-size arrays can be useful when the required size is known in advance and predictable memory usage is important.

## Dynamic arrays

A dynamic array can grow when additional elements are required.

When its capacity is exhausted, the implementation generally:

1. Allocates a larger storage area.
2. Copies existing elements.
3. Updates its internal storage reference.
4. Continues inserting new elements.

A simple growth strategy is to double the capacity:

    1 → 2 → 4 → 8 → 16 → 32

A resize operation is O(n) because existing elements have to be copied.

The important property is that resizing occurs relatively infrequently.

## Amortized O(1) append

Appending to a dynamic array is described as O(1) amortized rather than O(1) for every individual operation.

Most appends are constant time.

Occasionally, an append triggers a resize, which requires O(n) work.

Across a large sequence of appends, the total copying work is proportional to the number of inserted elements when an appropriate growth strategy is used.

Consequently, the average cost per append over the sequence is O(1) amortized.

This distinction is important:

- Individual worst-case append: O(n) when resizing occurs.
- Amortized append: O(1).

## Size versus capacity

Size and capacity should not be confused.

If a dynamic array has:

    size = 6
    capacity = 8

then six positions contain valid logical elements, while two additional positions are available without an immediate resize.

The custom dynamic array implementation explicitly tracks both values.

## Dynamic-array shrinking

Dynamic arrays can also reduce their capacity after many deletions.

Aggressive shrinking can create a performance problem known as repeated grow-shrink behavior.

For example:

    grow
    delete
    shrink
    append
    grow
    delete
    shrink

A practical implementation generally shrinks only when the storage becomes significantly underutilized.

The script demonstrates shrinking when the logical size falls to a sufficiently small fraction of capacity.

## Manual insertion

Insertion into an array can be implemented by shifting elements from right to left.

Suppose:

    [10, 20, 30, 40]

and `99` must be inserted at index `1`.

The elements are shifted in reverse order:

    40 → right
    30 → right
    20 → right

The resulting structure is:

    [10, 99, 20, 30, 40]

The reverse direction is important. Shifting from left to right can overwrite values before they have been moved.

## Manual deletion

Deletion uses the opposite direction.

If an element in the middle is removed, later elements move left to fill the empty position.

For:

    [10, 20, 30, 40, 50]

deleting index `1` results in:

    [10, 30, 40, 50]

This shifting process explains the O(n) complexity of internal deletion.

## Two-dimensional arrays

A two-dimensional array represents data using rows and columns.

For example:

    [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ]

The expression corresponding to row `1`, column `2` is:

    matrix[1][2]

and produces `6`.

Two-dimensional arrays are useful for:

- Matrices
- Tables
- Game boards
- Grids
- Images
- Spatial data
- Numerical computation

A matrix containing `r` rows and `c` columns requires traversal of O(r × c) time when every element is visited.

## A common Python two-dimensional array mistake

This construction is dangerous for mutable inner lists:

    [[0] * columns] * rows

It creates multiple references to the same inner list.

Changing one row can therefore unintentionally change other rows.

The safer construction is:

    [[0 for _ in range(columns)] for _ in range(rows)]

This creates a separate inner list for each row.

## Jagged arrays

A jagged array is an array whose rows have different lengths.

For example:

    [
        [1, 2],
        [3, 4, 5],
        [6],
        [7, 8, 9, 10]
    ]

Unlike a rectangular matrix, each row can contain a different number of elements.

Jagged structures are useful when the amount of data varies between groups.

## Array slicing

Python provides slicing syntax for creating portions of a list.

Examples include:

- `values[:4]` for the first four elements
- `values[2:6]` for a selected range
- `values[::2]` for every second element
- `values[::-1]` for a reversed copy

A normal list slice creates a new list.

This means modifying the slice does not directly replace the original list.

## References and shallow copies

Python lists store references to objects.

A shallow copy creates a new outer list but does not recursively duplicate nested mutable objects.

For example, copying:

    [[1, 2], [3, 4]]

creates a new outer list, but the inner lists can still be shared.

This distinction matters when arrays contain lists, dictionaries, objects, or other mutable structures.

## Arrays containing objects

Arrays do not have to contain only numbers.

A Python list can contain objects such as instances of a class.

The script demonstrates an array of `Employee` objects.

This allows operations such as:

- Searching by employee name
- Filtering by department
- Updating employee data
- Aggregating salaries

The complexity of searching still depends on the underlying operation. A linear scan through employee objects remains O(n).

## Array transformation

Arrays are frequently transformed into other arrays.

Examples include:

- Squaring every value
- Selecting only even values
- Filtering records
- Converting units
- Normalizing measurements
- Producing derived metrics

Python list comprehensions provide a concise way to express many such transformations.

## Prefix sum arrays

A prefix sum array stores cumulative totals.

Given:

    [2, 4, 6, 8, 10]

the prefix representation can be:

    [0, 2, 6, 12, 20, 30]

The extra leading zero simplifies range calculations.

For a range from index `left` through `right`:

    prefix[right + 1] - prefix[left]

gives the range sum.

After O(n) preprocessing, each range-sum query can be answered in O(1).

This technique is useful when many range queries must be processed against mostly unchanged data.

## Two-pointer technique

Two pointers are indexes that move through an array according to an algorithm's rules.

For sorted data, two pointers can solve the two-sum problem efficiently.

Suppose:

    [1, 3, 4, 6, 8, 11]

and the target is `10`.

Start with:

    left = 0
    right = 5

The algorithm compares the sum of both values.

- If the sum is too small, move `left` forward.
- If the sum is too large, move `right` backward.
- If the sum equals the target, the pair has been found.

For sorted data, this can be performed in O(n) time and O(1) extra space.

## Removing elements efficiently

Repeatedly calling an operation that removes an element from the middle can result in repeated shifting.

If many elements need to be removed, a filtering or compaction strategy can be more efficient.

The script implements an in-place technique using a write position.

The general pattern is:

1. Read each element.
2. Keep values that satisfy the condition.
3. Write retained values toward the beginning.
4. Remove unused trailing positions.

This approach can achieve O(n) time for a complete filtering operation.

## Moving zeroes

The script uses the same write-position concept to move all zeroes to the end while preserving the relative order of non-zero elements.

For:

    [0, 1, 0, 3, 12]

the result is:

    [1, 3, 12, 0, 0]

The algorithm requires O(n) time and O(1) additional space.

## Array-based stack

A stack follows the LIFO principle:

    Last In, First Out

An array can efficiently implement a stack when elements are added and removed from the end.

Python's:

    append()

and:

    pop()

are well suited to this use case.

Example:

    stack = []
    stack.append(10)
    stack.append(20)
    stack.append(30)

The next `pop()` returns `30`.

## Array-based queue

A queue follows FIFO:

    First In, First Out

A Python list can technically implement a queue using:

    pop(0)

but removing from the beginning requires shifting remaining elements.

Therefore, repeated front removal from a list can become inefficient.

For workloads requiring frequent insertion and removal from both ends, a deque is generally more appropriate.

The important design principle is that the best data structure depends on the operations that dominate the workload.

## Python list versus typed array

| Property | Python list | `array.array` |
|---|---|---|
| Type flexibility | High | Restricted by type code |
| Dynamic growth | Yes | Yes |
| General-purpose use | Excellent | More specialized |
| Primitive numeric storage | Less compact | More compact |
| Mixed data types | Supported | Generally not supported |
| Rich Python operations | Extensive | More limited |
| Memory representation | References to Python objects | Typed values |

For ordinary application development, Python lists are often the natural choice.

For compact typed numeric storage, `array.array` can be more appropriate.

## Arrays versus other data structures

An array is not automatically the best structure for every problem.

### Array

Useful when:

- Fast index-based access is required.
- Data is naturally sequential.
- Traversal is common.
- Appending is common.
- Memory locality matters.

### Dictionary

Useful when:

- Data is identified by keys.
- Fast average-case key lookup is required.
- Direct positional indexing is not the primary requirement.

### Set

Useful when:

- Membership testing is important.
- Duplicate elimination is required.
- Ordering by index is not the main requirement.

### Deque

Useful when:

- Elements are frequently added or removed from both ends.
- Queue-like operations are required.

The choice should be based on access patterns rather than simply choosing the most familiar structure.

## Search strategy selection

A useful decision process is:

### Use linear search when

- The array is unsorted.
- The collection is small.
- A single search is required.
- Maintaining sorted order is not worthwhile.

### Use binary search when

- The data is sorted.
- Repeated searches are required.
- Maintaining ordering is acceptable.
- O(log n) search is valuable.

### Use a hash-based structure when

- The primary requirement is fast average-case membership or key lookup.
- Positional ordering is not the central requirement.

## Edge cases

Array algorithms should explicitly consider boundary conditions.

Important cases include:

- Empty arrays
- One-element arrays
- Duplicate values
- Negative values
- Very large values
- Target not present
- Target at index `0`
- Target at the final index
- Invalid indexes
- Insertion into an empty structure
- Deletion from an empty structure
- Full fixed-size arrays
- Binary search on unsorted data

Ignoring these conditions can produce runtime errors or logically incorrect results.

## Empty arrays

An empty array has length zero.

Operations that require an element, such as finding a minimum, must define appropriate behavior.

The script raises a `ValueError` when attempting to calculate an average or minimum for an empty collection.

This is preferable to allowing an obscure error to occur later in an application.

## Invalid indexes

For an array with length `n`, an index is valid only when:

    0 <= index < n

An index equal to `n` is invalid.

The script includes safe-access logic and explicit index validation in the custom array implementation.

## Common mistakes

### Assuming indexes start at one

Traditional programming languages commonly use zero-based indexing for arrays.

The first element is normally at index `0`.

### Using `len(array)` as an index

For an array of length `5`, the last valid index is:

    4

Index `5` is invalid.

### Using binary search on unsorted data

Binary search depends on ordering.

Without a sorted array, its decisions about which half to discard are not valid.

### Inserting repeatedly at the beginning

Each insertion can require many elements to shift.

Repeated front insertion can therefore result in O(n²) total behavior.

### Repeatedly deleting from the beginning

The same shifting problem occurs with repeated front deletion.

### Modifying a list while directly iterating over it

Removing elements during iteration can cause elements to be skipped because positions change.

A filtering approach or carefully controlled index-based algorithm is safer.

### Incorrect multidimensional list construction

Using repeated references for mutable rows can cause changes to one row to appear in other rows.

### Confusing size and capacity

A dynamic array can have unused capacity.

Logical size describes valid elements; capacity describes available storage.

## Off-by-one errors

Array algorithms frequently contain boundary errors.

For an array of length `n`:

    range(n)

produces indexes:

    0 through n - 1

Using:

    range(n + 1)

would produce one additional position that is outside the normal array bounds.

Careful loop boundaries are essential when implementing insertion, deletion, searching, and traversal algorithms.

## Array invariants

An invariant is a condition that should remain true while an algorithm or data structure operates.

For the dynamic array implementation, an important invariant is:

    0 <= size <= capacity

If this relationship becomes false, the internal structure is inconsistent.

Maintaining explicit invariants makes custom data structures easier to debug and test.

## Performance considerations

Array performance should be evaluated according to the dominant operations.

Random access is highly efficient:

    O(1)

Sequential traversal is:

    O(n)

Linear search is:

    O(n)

Binary search on sorted data is:

    O(log n)

Middle insertion and deletion are generally:

    O(n)

Dynamic-array append is:

    O(1) amortized

These complexities are asymptotic descriptions. Actual performance also depends on hardware, memory hierarchy, object representation, allocation behavior, implementation details, and workload characteristics.

## Memory locality

Traditional contiguous arrays have strong spatial locality.

When neighboring elements are stored near each other in memory, sequential access can benefit from CPU cache behavior.

This is one reason arrays can perform very well for sequential numerical workloads.

Python lists have a more complicated memory model because their internal storage consists of references to Python objects rather than raw primitive values.

The underlying locality principle remains important in systems programming, numerical computing, databases, and performance-sensitive applications.

## Memory efficiency

Memory usage depends on representation.

A Python list stores references to objects. The referenced objects have their own memory requirements.

A typed array such as `array.array` can store numeric values in a more compact typed representation.

For large numerical datasets, representation can significantly affect memory consumption.

Memory should therefore be considered alongside computational complexity.

## Performance trade-offs of dynamic resizing

A larger capacity-growth factor means:

- Fewer resize operations.
- Potentially more unused memory.

A smaller growth factor means:

- Less unused capacity.
- More frequent resizing and copying.

There is no universally optimal growth factor for every workload.

The appropriate strategy depends on memory constraints, expected collection growth, allocation cost, and access patterns.

## Security and robustness

Array-related security concerns often arise from input size and boundary handling rather than from the array abstraction itself.

Production systems should:

- Validate externally supplied indexes.
- Reject negative sizes where inappropriate.
- Apply sensible maximum collection sizes.
- Avoid uncontrolled memory allocation.
- Validate numeric ranges when business rules require them.
- Avoid accidental quadratic behavior for attacker-controlled input.
- Handle empty input explicitly.
- Avoid assuming that a target value always exists.

For example, a service that accepts an externally supplied number of array elements should enforce a reasonable maximum to reduce the risk of excessive memory consumption.

## Debugging considerations

Array bugs are often caused by:

- Incorrect indexes
- Incorrect loop boundaries
- Unexpected mutations
- Incorrect shifting direction
- Incorrect capacity management
- Empty-array assumptions
- Shared references in nested structures

Useful debugging information includes:

- Current array contents
- Current index
- Current target
- Array size
- Array capacity
- Values before and after mutation

Assertions can also be used to verify invariants during development and testing.

## Testing considerations

Array implementations should be tested with both ordinary and boundary cases.

Useful test categories include:

### Normal cases

- Multiple elements
- Target present
- Target absent
- Middle insertion
- Middle deletion

### Boundary cases

- Empty array
- One element
- First index
- Last index
- Full fixed-size array

### Duplicate cases

- One duplicate
- Multiple duplicates
- All elements identical

### Algorithm-specific cases

- Sorted input for binary search
- Unsorted input for linear search
- Negative numbers
- Zero
- Large values

The Python script includes assertions for core searching, insertion, deletion, dynamic-array, filtering, and two-sum behavior.

## Real-world applications

Arrays are fundamental in many practical systems.

### Numerical data

Measurements, statistics, financial values, and scientific observations are naturally represented as sequences.

### Matrices

Two-dimensional arrays represent mathematical matrices and computational grids.

### Image processing

An image can be represented as a two-dimensional or three-dimensional collection of pixel values.

### Audio processing

Digital audio can be represented as a sequence of sampled amplitude values.

### Sensor systems

Temperature, pressure, acceleration, and other measurements are frequently stored as sequential observations.

### Financial systems

Price history, returns, transaction values, and time-series measurements can be represented using arrays.

### Machine learning

Feature vectors and numerical matrices are fundamentally array-oriented structures.

### Game development

Game boards, maps, grids, and numerical state representations frequently use arrays.

### Buffers

Systems programming commonly uses arrays as fixed-size or dynamically managed memory buffers.

## Practical implementation considerations

A production implementation should generally prefer well-tested standard-library structures when they satisfy the requirements.

A custom array implementation is valuable when:

- Specialized behavior is required.
- Educational purposes require explicit control.
- A custom memory or capacity strategy is needed.
- The application has requirements not provided by an existing structure.

Custom implementations require careful handling of:

- Capacity
- Size
- Index validation
- Resizing
- Copying
- Shifting
- Empty states
- Error handling
- Invariants
- Testing

## Complexity reference

| Concept | Complexity |
|---|---:|
| Direct index access | O(1) |
| Direct index update | O(1) |
| Complete traversal | O(n) |
| Linear search | O(n) |
| Binary search | O(log n) |
| First occurrence using binary search | O(log n) |
| Last occurrence using binary search | O(log n) |
| Insert at beginning | O(n) |
| Insert in middle | O(n) |
| Delete at beginning | O(n) |
| Delete in middle | O(n) |
| Append to dynamic array | O(1) amortized |
| Dynamic-array resize | O(n) |
| Prefix-sum construction | O(n) |
| Prefix-sum range query | O(1) |
| Two-pointer search on sorted data | O(n) |
| In-place array reversal | O(n) time, O(1) extra space |
| Move zeroes in place | O(n) time, O(1) extra space |

## Key conceptual distinctions

### Index versus value

An index identifies a position.

A value is the data stored at that position.

### Size versus capacity

Size is the number of logical elements.

Capacity is the available storage before resizing is required.

### Access versus search

Access starts with a known index.

Search starts with a value or condition and determines where it occurs.

### Fixed array versus dynamic array

A fixed array has predetermined capacity.

A dynamic array can allocate additional storage as it grows.

### Linear search versus binary search

Linear search does not require sorting.

Binary search requires sorted data.

### Python list versus typed array

A Python list is a flexible dynamic array of references.

`array.array` provides typed storage for values.

## Limitations of arrays

Arrays are highly effective for indexed access, but they have limitations.

- Internal insertion can require shifting.
- Internal deletion can require shifting.
- Fixed-size arrays cannot grow without replacement.
- Maintaining sorted order can make insertion expensive.
- Binary search depends on sorted data.
- Large collections can consume substantial memory.
- Arrays are not always appropriate for key-based access.
- Arrays are not ideal when frequent front insertion and deletion dominate the workload.

The appropriate data structure depends on the operations the application performs most frequently.
