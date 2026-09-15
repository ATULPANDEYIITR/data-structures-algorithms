# Array manipulation

## Topic introduction

Array manipulation is the process of changing the contents, order, size, or arrangement of elements stored in an array. It is one of the fundamental areas of data structures and algorithmic programming because many practical systems repeatedly insert, delete, move, search, reorder, and transform collections of values.

The central operations covered in this project are insertion, deletion, rotation, reversing, shifting, swapping, and rearranging. These operations appear in applications such as order processing, scheduling, inventory management, sensor processing, data cleaning, image processing, numerical computation, and algorithmic problem solving.

The implementations use Python lists, JavaScript arrays, and C++ `std::vector`. These structures have different language-level interfaces, but their underlying dynamic-array behavior is closely related.

## Fundamental concepts

An array stores elements in an ordered sequence. Each element has a position called an index. In the three implementations, indexing begins at zero.

For an array containing five elements:

`[10, 20, 30, 40, 50]`

the indexes are:

`0 → 10`

`1 → 20`

`2 → 30`

`3 → 40`

`4 → 50`

Indexed access is normally an O(1) operation because the address of an element can be calculated from its position.

Updating an existing element is also normally O(1). The program can directly replace the value at a known index without moving other elements.

Insertion and deletion are different. When an element is inserted into the middle of a contiguous array, subsequent elements must move to create space. Deleting an element from the middle requires subsequent elements to move toward the empty position. These operations are therefore generally O(n).

## Important terminology

### Index

An index identifies the position of an element in an array.

### Element

An element is an individual value stored in the array.

### Traversal

Traversal means visiting array elements, usually from the first element to the last.

### In-place operation

An in-place operation modifies the existing array rather than creating another array of proportional size.

### Stable operation

A stable rearrangement preserves the relative ordering of elements within each resulting group.

### Shift

A shift moves elements toward one end and introduces replacement values at the newly available positions. Values that leave the array boundary are discarded.

### Rotation

A rotation moves elements toward one end while wrapping elements that leave one boundary around to the opposite boundary. Unlike a shift, a rotation preserves every element.

### Partition

Partitioning rearranges an array into groups based on a condition, such as values below and above a pivot.

### Two-pointer technique

The two-pointer technique uses two indexes that move through the array according to a defined rule. It is useful for reversing, partitioning, and stable rearrangement.

## Insertion

Insertion adds an element at a specified position.

For:

`[10, 20, 40, 50]`

inserting `30` at index `2` produces:

`[10, 20, 30, 40, 50]`

The elements originally at indexes 2 and 3 must move one position to the right.

The Python implementation contains a manual `insert_at()` function that explicitly performs this shifting. This exposes the mechanism that a higher-level list operation abstracts away.

The JavaScript implementation uses `splice()`, which provides a built-in insertion mechanism.

The C++ implementation uses `vector::insert()`.

Insertion at the end is usually cheaper than insertion at the beginning or middle. For dynamic arrays, appending is typically O(1) amortized because most appends do not require reallocating the underlying storage.

## Deletion

Deletion removes an element.

For:

`[10, 20, 30, 40, 50]`

deleting index `2` produces:

`[10, 20, 40, 50]`

The elements after the deleted element move one position to the left.

The Python implementation demonstrates manual deletion with `delete_at()`. JavaScript uses `splice()`, while C++ uses `vector::erase()`.

Deletion from the end is generally cheaper than deletion from the beginning because no subsequent elements need to move.

## Swapping

Swapping exchanges two elements.

For:

`[10, 20, 30, 40]`

swapping indexes `0` and `3` produces:

`[40, 20, 30, 10]`

A swap is O(1) because only a fixed number of elements are changed.

Swapping is a fundamental building block for reversal, partitioning, sorting, and many rearrangement algorithms.

Python uses multiple assignment:

`array[first], array[second] = array[second], array[first]`

JavaScript uses destructuring assignment.

C++ uses `std::swap()`.

## Reversing

Reversal changes the order of elements so that the first becomes the last, the second becomes the second-last, and so on.

For:

`[1, 2, 3, 4, 5]`

the reversed sequence is:

`[5, 4, 3, 2, 1]`

The Python implementation demonstrates a manual two-pointer reversal. One pointer starts at the beginning and another at the end. The elements are exchanged and the pointers move inward.

The JavaScript implementation follows the same algorithm.

The C++ implementation uses `std::reverse()`.

An in-place reversal takes O(n) time and O(1) auxiliary space.

## Shifting

A shift moves elements in one direction and fills the newly opened positions.

A left shift of two positions:

`[1, 2, 3, 4, 5]`

becomes:

`[3, 4, 5, 0, 0]`

A right shift of two positions becomes:

`[0, 0, 1, 2, 3]`

The zeroes are replacement values. The values that leave the array boundary are lost.

The direction in which elements are copied is important. For a right shift, elements must generally be processed from right to left. Copying from left to right could overwrite values before they are moved.

## Rotation

Rotation differs from shifting because values that leave one side reappear at the other side.

A left rotation by two positions:

`[1, 2, 3, 4, 5]`

becomes:

`[3, 4, 5, 1, 2]`

A right rotation by two positions becomes:

`[4, 5, 1, 2, 3]`

The implementations use the reversal algorithm for in-place rotation.

For a left rotation by `k`:

1. Reverse the first `k` elements.
2. Reverse the remaining elements.
3. Reverse the entire array.

This achieves O(n) time and O(1) auxiliary space.

Rotation counts should normally be normalized using the array length. Rotating by the array length produces the original arrangement, and rotating by a larger number can be reduced using modulo arithmetic.

The implementations also handle empty arrays safely.

## Out-of-place rotation

A simpler rotation can be implemented by creating a new array from two slices.

This approach is easy to understand but requires O(n) additional memory.

The Python `rotate_with_slice()` function and JavaScript `rotateCopy()` function demonstrate this alternative.

The distinction illustrates an important design trade-off:

| Approach | Time | Extra space | Main advantage |
|---|---:|---:|---|
| Reversal rotation | O(n) | O(1) | Memory efficient |
| Slice/copy rotation | O(n) | O(n) | Simple and readable |

The best approach depends on whether memory usage, readability, or mutation behavior is the primary concern.

## Rearranging elements

Rearrangement changes the relative positions of elements according to a condition or structural rule.

A common example is moving zeroes to the end.

Input:

`[0, 1, 0, 3, 12]`

Output:

`[1, 3, 12, 0, 0]`

The implementation uses a write pointer. Every non-zero value is written to the next available position. The remaining positions are filled with zero.

This is O(n) time and O(1) auxiliary space.

The method is stable because the non-zero values remain in their original relative order.

## Partitioning

Partitioning divides an array into logical regions.

For a pivot value of `5`, an array can be rearranged so values smaller than `5` appear before values greater than or equal to `5`.

The precise order inside the two groups does not necessarily remain unchanged.

The Python, JavaScript, and C++ implementations demonstrate partitioning techniques. C++ also distinguishes between `partition()` and `stable_partition()`.

`partition()` is appropriate when only group membership matters.

`stable_partition()` is appropriate when the original relative order inside the groups must be preserved.

## Even and odd rearrangement

An array can be rearranged so even numbers appear before odd numbers.

For example:

`[1, 2, 3, 4, 5, 6]`

may become:

`[6, 2, 4, 3, 5, 1]`

The exact order depends on the partitioning algorithm.

The two-pointer implementation demonstrates an efficient O(n) approach using swaps. It does not guarantee stability.

This illustrates an important distinction between stable and unstable rearrangement.

## Duplicate removal

Duplicate removal can be performed in several ways.

For an unsorted array:

`[3, 1, 3, 2, 1, 4]`

a set can record values already encountered.

The result can be:

`[3, 1, 2, 4]`

The set-based approach generally takes O(n) average time and O(n) additional space.

When the array is already sorted, duplicates can be removed in-place with a two-pointer technique. The Python implementation includes `remove_duplicates_sorted_in_place()` for this case.

## Searching

Linear search examines elements sequentially.

Its worst-case time complexity is O(n).

Binary search repeatedly divides a sorted search interval in half. Its time complexity is O(log n), but it requires sorted data.

The Python and JavaScript implementations contain both linear and binary search.

The C++ implementation uses `lower_bound()` for binary-search-style lookup of sorted package identifiers.

Searching and rearrangement are closely related because many systems rearrange data first to make future searches or processing more efficient.

## Advanced rearrangement

The Dutch National Flag algorithm is demonstrated for arrays containing only `0`, `1`, and `2`.

The algorithm maintains three regions:

- Values already classified as `0`
- Values currently being examined
- Values already classified as `2`

It runs in O(n) time and O(1) auxiliary space.

The implementations also demonstrate wiggle rearrangement:

`a0 <= a1 >= a2 <= a3 ...`

At every adjacent pair, the algorithm checks whether the required relationship holds and swaps the pair when necessary.

Another example is alternating positive and negative values. That implementation intentionally uses additional arrays for positive and negative groups because preserving the relative order of each group is more straightforward with separate storage.

## Python implementation

The Python script treats the built-in `list` as the primary dynamic array structure.

It contains explicit implementations of:

- Basic indexing and updates
- Manual insertion
- Manual deletion
- Swapping
- In-place reversal
- Left and right shifting
- Left and right rotation
- Zero movement
- Pivot partitioning
- Even/odd rearrangement
- Alternating-sign rearrangement
- Duplicate removal
- Linear search
- Binary search
- Dutch National Flag partitioning
- Wiggle rearrangement
- Index-mapping rearrangement
- Batch operation processing
- Edge-case validation
- Performance benchmarking
- Automated testing
- Randomized testing
- A sensor-processing case study

The Python implementation emphasizes algorithmic reasoning. Several operations are implemented manually instead of relying exclusively on built-in methods so the element movement involved in the operations is visible.

The `SensorBatch` class demonstrates how basic array operations can become part of a higher-level data-processing workflow.

A sensor batch can be cleaned, filtered, rotated for alignment, normalized, and analyzed.

## JavaScript implementation

The JavaScript file demonstrates array manipulation using native JavaScript arrays.

It includes:

- Indexing and traversal
- `splice()` insertion and deletion
- `push()` and `pop()`
- Destructuring-based swapping
- In-place reversal
- Manual shifts
- Reversal-based rotation
- Stable movement of zeroes
- Pivot partitioning
- Even/odd partitioning
- Duplicate removal using `Set`
- Linear search
- Binary search
- Three-way partitioning
- Wiggle rearrangement
- Alternating-sign rearrangement
- Copy-based versus in-place operations
- Validation and exceptions
- Automated tests
- Performance measurement
- An order-processing case study

JavaScript is particularly useful for demonstrating array manipulation because arrays are central to browser and application programming. Methods such as `splice()`, `slice()`, `push()`, `pop()`, `shift()`, and `unshift()` expose different mutation and movement behaviors.

The `OrderQueue` class models a sequence of orders that can be inserted, cancelled, promoted, rotated, and processed.

## C++ case study

The C++ program models a warehouse fulfillment system.

Each package contains:

- An identifier
- A priority
- A weight
- A processing status

The system uses `std::vector<Package>` as its dynamic contiguous sequence.

The `FulfillmentSystem` class provides operations for receiving, inserting, cancelling, prioritizing, rotating, reversing, cleaning cancelled records, removing duplicates, and processing the next package.

This case study connects low-level array manipulation with a realistic operational workflow.

### System design

The package is represented by a `struct`, which groups related attributes.

Validation is separated into `validatePackage()`. This prevents invalid records from entering the system through supported insertion paths.

The fulfillment system encapsulates the package vector. Public methods provide controlled operations instead of allowing arbitrary modification from outside the class.

This separation improves maintainability and allows business rules to be added around primitive vector operations.

### Insertion and deletion

`vector::insert()` adds an element at a selected position.

`vector::erase()` removes an element from a selected position.

Both can require movement of many elements and are therefore O(n) in the general case.

Processing the first package using `erase(begin())` also requires shifting the remaining elements. For a very large high-frequency queue, a different data structure such as `std::deque` could be more appropriate. The example intentionally uses a vector because the case study focuses on array manipulation.

### Rotation

The C++ implementation contains a generic reversal-based rotation function.

Because the function is templated, it can operate on vectors of different element types as long as the elements can be swapped.

The implementation normalizes the rotation amount using the vector length and performs three reversals.

### Stable rearrangement

Cancelled packages are moved toward the end with `stable_partition()`.

Stability is useful when the relative ordering of active packages has operational meaning.

Heavy packages are grouped with `partition()` without requiring stable ordering.

This distinction represents a real engineering trade-off: preserving order can require additional work or restrict the available algorithms, while an unstable partition can provide more flexibility when only grouping matters.

### Priority arrangement

The system uses `stable_sort()` to order packages by descending priority.

Stability means packages with equal priority retain their relative order.

This is useful in fulfillment systems where priority alone should not destroy arrival-order information.

### Searching

Linear search is appropriate for an unsorted vector and takes O(n) time.

Binary search can reduce search time to O(log n), but the data must be sorted according to the same ordering used by the search.

The C++ implementation uses `lower_bound()` to locate package identifiers in sorted data.

### Duplicate removal

Package identifiers are tracked using `unordered_set`.

The average membership check is O(1), making duplicate removal O(n) average time with O(n) additional memory.

The extra memory is a deliberate trade-off for faster lookup.

## Edge cases

Array manipulation algorithms must account for boundary conditions.

Important cases include:

- Empty arrays
- Single-element arrays
- Rotation by zero
- Rotation by the array length
- Rotation by a number larger than the array length
- Invalid indexes
- Deleting from the first position
- Deleting from the last position
- Inserting at the beginning
- Inserting at the end
- Duplicate values
- All elements satisfying a partition condition
- No elements satisfying a partition condition
- Invalid values for restricted algorithms
- Negative rotation amounts
- Invalid business records

The Python and JavaScript programs explicitly test several of these conditions. The C++ program uses exceptions and `std::optional` for failure handling.

## Exceptions and validation

Validation is important because array algorithms often assume specific input conditions.

Binary search assumes sorted input.

The Dutch National Flag implementation assumes only `0`, `1`, and `2`.

Index-based operations require valid positions.

The C++ package model requires a non-empty identifier, a priority in the permitted range, and a positive weight.

Failing early is preferable to silently producing incorrect data.

Python uses exceptions such as `IndexError` and `ValueError`.

JavaScript uses `RangeError` and `TypeError`.

C++ uses standard exceptions such as `std::out_of_range`, `std::invalid_argument`, and `std::runtime_error`.

## Mutation versus copying

Mutation changes the original array.

Examples include:

- Python list assignment
- JavaScript `splice()`
- JavaScript `reverse()`
- C++ `vector::insert()`
- C++ `vector::erase()`

Copying creates a separate collection.

Copying is often easier to reason about because the original data remains unchanged, but it requires additional memory.

In-place manipulation is useful when memory efficiency is important or when the original array is intentionally mutable.

Copy-based manipulation can be preferable when immutable-style program design or preservation of the original input is more important.

## Common mistakes

### Using an invalid index

An index equal to the array length is valid for insertion at the end but invalid for accessing or deleting an existing element.

### Copying in the wrong direction

When shifting elements to the right, copying from left to right can overwrite source values.

Right shifts should generally process elements from right to left.

### Confusing shift with rotation

A shift loses values that leave the boundary.

A rotation preserves all values.

### Forgetting modulo normalization

A rotation by `n`, `2n`, or `3n` positions produces the original sequence. Normalizing the position avoids unnecessary work.

### Rotating an empty array without checking its size

Modulo by zero is invalid, so empty arrays need a special case.

### Using binary search on unsorted data

Binary search depends on ordering. It is not a general replacement for linear search.

### Assuming partition preserves order

Ordinary partitioning can rearrange elements inside its groups. Stable partitioning is required when relative order matters.

### Modifying an array while iterating without understanding the consequences

Insertion and deletion can change indexes during traversal. Such operations should be designed carefully to avoid skipping elements or processing the same element unexpectedly.

### Ignoring allocation costs

An algorithm can be O(n) in both cases while having very different memory behavior. A copy-based rotation and an in-place rotation are both O(n) in time but differ in auxiliary memory usage.

## Performance considerations

For a contiguous dynamic array, common complexity characteristics are:

| Operation | Typical time complexity | Auxiliary space | Important detail |
|---|---:|---:|---|
| Indexed access | O(1) | O(1) | Direct position access |
| Update | O(1) | O(1) | Existing element |
| Append | O(1) amortized | O(1) | Occasional resizing |
| Insert at beginning | O(n) | O(1) | Elements shift |
| Delete at beginning | O(n) | O(1) | Elements shift |
| Linear search | O(n) | O(1) | No sorting required |
| Binary search | O(log n) | O(1) | Requires sorted data |
| Reverse | O(n) | O(1) | Two-pointer approach |
| Rotation | O(n) | O(1) | Reversal approach |
| Set-based duplicate removal | O(n) average | O(n) | Hash-based lookup |
| Sorting | O(n log n) typical | Depends on algorithm | Ordering enables later operations |

Complexity should be considered together with constant factors, memory allocation, cache locality, stability requirements, and mutation behavior.

## Security considerations

Array manipulation is not normally a security-sensitive operation by itself, but incorrect bounds handling can become a serious issue in lower-level languages.

C++ programs must validate indexes before using iterator arithmetic or direct indexing. Invalid memory access can lead to undefined behavior.

The C++ case study therefore validates insertion, deletion, swapping, and package data.

JavaScript and Python provide stronger runtime protections against many direct memory-corruption problems, but incorrect indexes and invalid application data can still cause exceptions or logical errors.

For externally supplied data, validation should occur before manipulation. Applications should also impose reasonable limits on array size when input originates from untrusted sources to reduce memory-exhaustion risks.

## Implementation considerations

The appropriate operation depends on the required behavior.

If elements must be inserted frequently at both ends, a dynamic array may not be the ideal structure.

If random indexed access dominates the workload, contiguous arrays are highly effective.

If frequent deletion from the beginning is required, repeatedly erasing the first element of a vector or JavaScript array can become expensive.

If ordering must be preserved, stable algorithms should be selected.

If only grouping matters, unstable partitioning may be sufficient.

If memory is constrained, in-place operations can be preferable.

If preserving the input is important, copy-based operations can be safer.

## Python, JavaScript, and C++ distinctions

| Concern | Python | JavaScript | C++ |
|---|---|---|---|
| Primary structure used | `list` | `Array` | `std::vector` |
| Typing | Dynamically typed | Dynamically typed | Statically typed |
| Manual memory management | No | No | Managed through RAII/library abstractions |
| Built-in insertion | `insert()` | `splice()` | `vector::insert()` |
| Built-in deletion | `pop()`, `remove()` | `splice()`, `pop()` | `erase()` |
| Reversal | `reverse()` | `reverse()` | `std::reverse()` |
| Hash-based duplicate tracking | `set` | `Set` | `unordered_set` |
| Optional result representation | `None` or exceptions | `null` or exceptions | `std::optional` |
| Generic implementation | Dynamic typing | Dynamic typing | Templates |
| Main educational strength | Clear algorithmic expression | Application and web-oriented array behavior | Explicit types, containers, algorithms, and performance |

The three languages expose similar conceptual operations while emphasizing different programming models.

Python provides concise syntax and makes algorithmic transformations easy to express.

JavaScript is particularly relevant when array manipulation occurs in browser applications and event-driven application code.

C++ provides explicit control over data structures, algorithms, types, memory characteristics, and performance-oriented design.

## Practical applications

Array manipulation is directly relevant to:

- Inventory processing
- Warehouse fulfillment
- Financial time-series processing
- Sensor data preprocessing
- Scheduling systems
- Task queues
- Batch data processing
- Search indexes
- Numerical computation
- Image and signal processing
- Game development
- Ranking systems
- Log processing
- Data cleaning
- Statistical preprocessing
- In-memory caches

The sensor example in Python demonstrates preprocessing of measurement data.

The JavaScript order queue demonstrates sequence mutation in an application-level workflow.

The C++ fulfillment system demonstrates how insertion, deletion, rotation, sorting, searching, and rearrangement can form part of a larger operational system.

## Testing approach

The Python implementation contains deterministic assertions and randomized rotation tests.

Deterministic tests verify known expected transformations.

Randomized tests generate many different arrays and rotation counts and compare the in-place implementation with a simpler reference implementation.

The JavaScript program uses a custom `assertEqual()` helper for deterministic tests.

The C++ program uses a `require()` helper and throws an exception when a condition fails.

Testing array algorithms should include both normal inputs and boundary conditions because off-by-one errors frequently occur around the first and last indexes.

## Design principles demonstrated

The implementations illustrate several general algorithmic principles.

A primitive operation can be implemented directly to expose its internal mechanics.

Multiple primitive operations can be composed into higher-level workflows.

Two-pointer methods can reduce extra memory requirements.

Stable and unstable algorithms should be selected according to application requirements.

Sorting can improve future search performance but introduces an O(n log n) preprocessing cost.

Hash-based structures can reduce average lookup time at the cost of additional memory.

In-place algorithms can improve memory efficiency but mutate their input.

Copy-based algorithms can simplify reasoning and preserve the original data but require additional storage.

Correct array manipulation is therefore not only about producing the desired final ordering. It also requires selecting an appropriate algorithm according to time complexity, memory constraints, stability requirements, input assumptions, mutation rules, and application behavior.
