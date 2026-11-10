# Heap Introduction

## 1. Technical Scope

A heap is a specialized tree-based data structure that maintains a priority relationship between parent nodes and their children.

The implementations in this repository cover:

- Complete binary trees.
- Array-based tree representation.
- Min-heaps and max-heaps.
- Heap construction.
- Insertion and extraction.
- Sift-up and sift-down operations.
- Heap validation.
- Heap sorting.
- Priority queues.
- Event and task scheduling.
- Performance analysis.
- Input validation and failure handling.

The implementations use Python, JavaScript, C++17, Java 17, and PostgreSQL to examine the same underlying data structure from different engineering perspectives.

## 2. Complete Binary Trees

A complete binary tree is a binary tree in which:

- Every level except possibly the last is completely filled.
- Nodes in the last level occupy positions from left to right.
- No gaps occur between existing nodes at the last level.

A binary tree allows each node to have at most two children.

A complete binary tree additionally imposes a structural arrangement that makes efficient array storage possible.

Consider the following tree:

    Level 0:                  10

    Level 1:              20      30

    Level 2:            40  50  60  70

Its array representation is:

`[10, 20, 30, 40, 50, 60, 70]`

Each array position corresponds to a node in level-order traversal.

### 2.1 Index relationships

For zero-based indexing:

| Relationship | Formula |
|---|---|
| Parent | `(i - 1) // 2` |
| Left child | `2 * i + 1` |
| Right child | `2 * i + 2` |

For one-based indexing:

| Relationship | Formula |
|---|---|
| Parent | `i // 2` |
| Left child | `2 * i` |
| Right child | `2 * i + 1` |

The Python, JavaScript, C++, and Java implementations use zero-based indexing.

The PostgreSQL array implementation uses one-based indexing.

For a node at index 2 in a zero-based array:

- Parent index = 0.
- Left child index = 5.
- Right child index = 6.

The root has no parent.

A node without children is a leaf node.

A complete binary tree containing `n` nodes has height proportional to `log₂(n)`.

Its height is bounded by:

`floor(log₂(n))`

when the root is considered level zero.

## 3. Heap Properties

A binary heap satisfies two independent structural requirements.

### 3.1 Structural property

A binary heap must be a complete binary tree.

This property determines how nodes are arranged and stored.

### 3.2 Ordering property

The values of parent and child nodes must satisfy a priority relationship.

This determines whether the heap is a min-heap or a max-heap.

A heap is not necessarily a fully sorted binary tree.

Only the parent-child ordering relationship is guaranteed.

Nodes at the same level may appear in an order that does not correspond to their numerical ranking.

## 4. Min-Heaps

A min-heap maintains the following relationship:

`Parent <= Children`

The root contains the smallest element.

Example:

    Level 0:                  5

    Level 1:              10      8

    Level 2:            20  15  12  30

Array representation:

`[5, 10, 8, 20, 15, 12, 30]`

The root can be accessed in constant time.

The remaining elements are not necessarily sorted.

A min-heap is useful when the application repeatedly needs the smallest available element.

Practical applications include:

- Processing jobs in ascending priority order.
- Selecting the earliest scheduled event.
- Maintaining the smallest available distance in graph algorithms.
- Implementing task queues.
- Finding the smallest elements in a dataset.

In the scheduling examples, smaller numerical priority values represent more urgent operations.

## 5. Max-Heaps

A max-heap maintains the opposite relationship:

`Parent >= Children`

The root contains the largest element.

Example:

    Level 0:                  90

    Level 1:              70      80

    Level 2:            40  50  60  30

Array representation:

`[90, 70, 80, 40, 50, 60, 30]`

The maximum element is available at the root.

Practical applications include:

- Selecting the highest-scoring candidate.
- Maintaining the largest values in a dataset.
- Implementing descending-priority scheduling.
- Finding the maximum available resource score.
- Supporting selection and ranking algorithms.

### 5.1 Min-heap versus max-heap

| Property | Min-heap | Max-heap |
|---|---|---|
| Root | Smallest element | Largest element |
| Parent relationship | Parent <= child | Parent >= child |
| Priority direction | Ascending | Descending |
| Root extraction | Minimum | Maximum |
| Typical application | Earliest or smallest item | Highest or largest item |

Both structures have the same underlying shape and operational complexity.

The difference is the comparison rule used during heap operations.

## 6. Heap Representation

A heap can be implemented using:

- An array.
- A dynamic array.
- A vector.
- A list-backed collection.

The implementations use contiguous array-based storage.

For an array:

`[10, 20, 30, 40, 50, 60, 70]`

the tree relationships are:

    Index 0: 10
        |
        +-- Index 1: 20
        |       |
        |       +-- Index 3: 40
        |       +-- Index 4: 50
        |
        +-- Index 2: 30
                |
                +-- Index 5: 60
                +-- Index 6: 70

The complete-tree property eliminates the need for explicit left-child and right-child pointers.

This reduces memory overhead and simplifies navigation.

### 6.1 Advantages of array representation

- No separate node objects are required.
- Parent and child positions are calculated directly.
- Memory allocation is relatively efficient.
- Iteration is cache-friendly.
- Dynamic arrays support efficient insertion at the end.

### 6.2 Limitations

Array-based heaps require careful index management.

Removing arbitrary elements is not as efficient as removing the root.

The array must also be resized when its capacity is exhausted, depending on the underlying implementation.

## 7. Fundamental Heap Operations

### 7.1 Peek

Peek returns the root without removing it.

For a min-heap, it returns the minimum element.

For a max-heap, it returns the maximum element.

Time complexity: `O(1)`.

An empty heap cannot provide a root and must produce an appropriate error.

### 7.2 Insertion

Insertion adds a new element at the end of the array.

The new element is initially placed at the next available position in the complete binary tree.

It may violate the heap-order property.

The sift-up operation restores that property.

Example:

Initial min-heap:

`[10, 20, 15, 40, 30]`

Insert:

`5`

Append the new element:

`[10, 20, 15, 40, 30, 5]`

Compare 5 with its parent, 15.

Exchange the elements:

`[10, 20, 5, 40, 30, 15]`

Compare 5 with its new parent, 10.

Exchange again:

`[5, 20, 10, 40, 30, 15]`

The heap property is restored.

Time complexity: `O(log n)`.

### 7.3 Extraction

Extraction removes the root element.

The final array element is moved to the root position.

The sift-down operation then restores the ordering property.

Example:

Initial min-heap:

`[5, 20, 10, 40, 30, 15]`

Remove 5.

Move the last element, 15, to the root:

`[15, 20, 10, 40, 30]`

Compare the root with its children.

The smaller child is 10.

Exchange:

`[10, 20, 15, 40, 30]`

The heap property is restored.

Time complexity: `O(log n)`.

### 7.4 Sift-up

Sift-up compares a node with its parent.

If the node has higher priority, the elements are exchanged.

The process continues until:

- The root is reached.
- The parent-child relationship satisfies the heap property.

Sift-up is used during insertion.

### 7.5 Sift-down

Sift-down compares a parent with its available children.

It selects the child with the highest priority and exchanges the parent with that child when necessary.

The process continues until the heap property is restored.

Sift-down is used during extraction and bottom-up construction.

## 8. Building a Heap

A heap can be constructed by repeatedly inserting individual elements.

If there are `n` elements, repeated insertion takes `O(n log n)` time in the worst case.

A more efficient approach is bottom-up heap construction.

The algorithm starts from the last non-leaf node and applies sift-down toward the root.

For a zero-based array:

`Last non-leaf index = floor(n / 2) - 1`

The leaf nodes already satisfy the heap-order property because they have no children.

Bottom-up construction takes `O(n)` time.

This is asymptotically more efficient than inserting every element individually.

The Python, JavaScript, C++, Java, and PostgreSQL implementations demonstrate bottom-up construction.

## 9. Heap Sorting

Heap sort uses a heap to order an array.

The ascending-order implementation constructs a min-heap and repeatedly extracts the minimum element.

The extracted values form an ascending sequence.

The implementations use an auxiliary result collection for clarity.

A conventional in-place heap sort generally uses a max-heap, repeatedly moves the maximum element to the end of the array, and reduces the active heap boundary.

Complexity:

| Operation | Time complexity |
|---|---|
| Heap construction | `O(n)` |
| Repeated extraction | `O(n log n)` |
| Complete sorting | `O(n log n)` |

Conventional in-place heap sort uses `O(1)` auxiliary space.

The extraction-based examples use `O(n)` additional space.

Heap sort is not stable.

Equal values are not guaranteed to retain their original relative ordering.

## 10. Priority Queues

A priority queue is an abstract data type in which elements are removed according to priority rather than insertion order.

A binary heap is one common implementation of a priority queue.

The repository job scheduler demonstrates this relationship.

Example jobs:

| Repository | Operation | Priority |
|---|---|---:|
| portfolio-api | Run tests | 3 |
| security-engine | Security audit | 1 |
| market-service | Generate report | 7 |
| portfolio-api | Production incident | 1 |

The scheduler processes the security audit and production incident before the lower-priority operations.

Equal priorities are ordered using insertion sequence numbers.

This produces deterministic ordering among tasks with the same priority.

### 10.1 Heap versus priority queue

These concepts are related but are not interchangeable.

A heap is a concrete data structure.

A priority queue is an abstract behavior.

A priority queue may be implemented using:

- Binary heaps.
- Other heap variants.
- Balanced search trees.
- Unsorted arrays.
- Sorted arrays.

A binary heap provides an efficient general-purpose implementation.

## 11. Complexity Analysis

| Operation | Time complexity | Explanation |
|---|---|---|
| Access root | `O(1)` | Root is stored at index zero |
| Insert | `O(log n)` | At most one tree-height of sift-up |
| Extract root | `O(log n)` | At most one tree-height of sift-down |
| Build heap | `O(n)` | Bottom-up construction |
| Validate heap | `O(n)` | Every non-root node is checked |
| Heap sort | `O(n log n)` | Repeated extraction |
| Search arbitrary value | `O(n)` | Heap ordering does not fully sort nodes |
| Replace root | `O(log n)` | Sift-down restores ordering |

For a complete binary tree, the height is logarithmic in the number of nodes.

This is the reason insertion and extraction have logarithmic worst-case complexity.

## 12. Python Implementation

The Python implementation provides a generic `BinaryHeap` class.

Its principal components are:

| Component | Responsibility |
|---|---|
| `HeapType` | Defines min-heap and max-heap behavior |
| `BinaryHeap` | Maintains the heap structure |
| `HeapStatistics` | Records operational statistics |
| `Task` | Represents a scheduled operation |
| `TaskScheduler` | Implements priority-based execution |
| `heap_sort` | Produces an ascending sequence |

The implementation uses:

- Lists for array representation.
- Dataclasses for structured task records.
- Enums for heap type.
- Type annotations for clearer interfaces.
- Exceptions for invalid operations.
- Assertions for correctness checks.
- JSON file handling for result persistence.

The `heapq` module is used separately in the task scheduler to demonstrate the standard-library priority queue implementation.

The custom heap implementation exposes the underlying mechanics rather than hiding them behind a library abstraction.

## 13. JavaScript Implementation

The JavaScript implementation emphasizes event-driven scheduling.

Its `BinaryHeap` class implements the fundamental heap operations.

`PriorityScheduler` uses:

- `Map` for task storage.
- `EventEmitter` for scheduling notifications.
- Immutable task objects.
- Explicit validation.
- Asynchronous file persistence.

The scheduler emits two important events:

| Event | Meaning |
|---|---|
| `scheduled` | A task entered the priority queue |
| `executed` | A task was removed for execution |

This separates queue operations from the components that observe those operations.

The example uses numeric priority encoding with a sequence component.

The demonstration restricts the sequence space to fewer than one million entries so that the encoding remains unambiguous.

For an unrestricted production scheduler, a heap of structured task records with a comparator would be preferable.

The scheduler's task lookup is intentionally explicit. Its execution path can be improved to use an indexed heap or a structured-entry heap to avoid linear lookup.

## 14. C++17 Implementation

The C++ implementation demonstrates generic programming and STL integration.

Its principal components are:

| Component | Responsibility |
|---|---|
| `BinaryHeap<T>` | Generic heap implementation |
| `HeapType` | Selects min-heap or max-heap |
| `HeapStatistics` | Tracks comparisons and swaps |
| `RepositoryJob` | Models repository operations |
| `JobComparator` | Defines priority ordering |
| `RepositoryJobScheduler` | Manages operational jobs |
| `heapSort` | Performs ascending sorting |

The custom heap uses `std::vector` for contiguous storage.

The scheduler uses `std::priority_queue` with a custom comparator.

The comparator gives smaller numerical priorities precedence.

Sequence numbers ensure deterministic ordering for equal priorities.

The implementation uses exceptions to handle invalid operations and assertions to verify expected behavior.

## 15. Java 17 Implementation

The Java implementation provides an enterprise-oriented design.

It distinguishes between the heap structure and the service that uses a priority queue.

Important components include:

- `BinaryHeap<T>` for generic heap operations.
- `DeploymentTask` for immutable task data.
- `DeploymentPolicy` for execution eligibility.
- `ProductionDeploymentPolicy` for validation.
- `DeploymentService` for scheduling and processing.
- `DeploymentStatus` for domain state representation.

Java records provide immutable task data.

The service synchronizes queue operations to prevent concurrent modification of its shared state.

The priority queue orders deployment tasks by priority and sequence number.

The service separates pending, completed, and failed task collections.

The example focuses on scheduling mechanics rather than implementing an actual deployment system.

## 16. PostgreSQL Implementation

The SQL implementation demonstrates both an array-backed heap and a persistent relational priority queue.

### 16.1 Heap storage

The `heap_instances` table stores:

- Heap identifier.
- Heap name.
- Heap type.
- Array representation.
- Creation timestamp.
- Update timestamp.

The `heap_type` enum restricts the permitted values to `min` and `max`.

The `validate_heap` function checks parent-child ordering.

### 16.2 Heap functions

| Function | Responsibility |
|---|---|
| `parent_index` | Calculates parent position |
| `left_child_index` | Calculates left-child position |
| `right_child_index` | Calculates right-child position |
| `heap_has_higher_priority` | Applies min/max comparison |
| `validate_heap` | Checks heap-order integrity |
| `heap_push` | Inserts an element |
| `heap_pop` | Extracts the root |
| `build_heap` | Constructs a heap bottom-up |

The `heap_tree_view` view translates the array representation into node relationships.

### 16.3 Relational priority queue

The `repository_jobs` table models operational tasks.

Each task contains:

- Repository name.
- Operation.
- Numerical priority.
- Processing status.
- Creation timestamp.
- Processing timestamps.
- Failure information.

A partial index supports retrieval of pending tasks.

The `process_next_job` function uses:

`FOR UPDATE SKIP LOCKED`

This prevents concurrent workers from selecting the same pending task when they operate within appropriate transactions.

The completion procedure verifies the current task state before allowing a transition.

The audit trigger records status changes.

### 16.4 Array-backed heap versus relational priority queue

The two PostgreSQL approaches solve different problems.

| Characteristic | Array-backed heap | Relational queue |
|---|---|---|
| Representation | PostgreSQL array | Relational records |
| Main purpose | Heap algorithm demonstration | Persistent job management |
| Insert | Array append and sift-up | Insert a job record |
| Extract | Root replacement and sift-down | Ordered transactional selection |
| Concurrency | Requires external coordination | Row-level locking |
| Audit history | Not inherently available | Supported by audit table |
| Scaling approach | Suitable for bounded arrays | Suitable for persistent multi-worker queues |

A relational priority queue should not be described as a binary heap.

The relational implementation uses ordered database selection and transactional locking rather than maintaining a binary-tree array structure.

## 17. Failure Conditions and Edge Cases

The implementations account for several important situations.

| Condition | Expected behavior |
|---|---|
| Empty heap extraction | Raise an error |
| Empty heap peek | Raise an error |
| Single-element extraction | Return the element and empty the heap |
| Duplicate values | Preserve valid heap ordering |
| Negative numbers | Apply ordinary numerical comparisons |
| Equal priorities | Apply deterministic sequence ordering |
| Invalid priority | Reject the task |
| Invalid heap type | Reject construction |
| Invalid tree index | Raise an index-related error |
| Invalid stored heap | Reject heap operations |
| Invalid job transition | Reject the database operation |
| Concurrent queue processing | Use transactional locking |

A heap does not require distinct values.

Duplicate elements are valid.

Negative numbers are also valid.

The root remains the minimum or maximum element regardless of whether values are positive, negative, or duplicated.

## 18. Performance and Engineering Considerations

### 18.1 Array resizing

Dynamic arrays may occasionally reallocate their underlying storage.

Such reallocations can make an individual insertion more expensive.

The amortized insertion cost remains constant for the append operation itself, while heap maintenance requires `O(log n)` comparisons and swaps.

### 18.2 Cache locality

Array-based heaps generally have better memory locality than pointer-based tree structures.

Parent and child nodes occupy predictable positions.

This reduces the need for separate node allocations.

### 18.3 Comparison cost

Heap complexity assumes that comparing two elements takes constant time.

For complex objects, comparison may involve multiple fields or expensive calculations.

A comparator should therefore be deterministic and inexpensive.

### 18.4 Concurrent access

The custom Python, JavaScript, and C++ heap implementations do not automatically provide thread safety.

Shared heaps require appropriate synchronization.

The Java service synchronizes its queue operations.

The PostgreSQL relational scheduler uses database transactions and row-level locking.

### 18.5 Task failure recovery

Removing a task from a queue does not guarantee successful execution.

A production scheduler needs explicit failure management.

Useful mechanisms include:

- Retry limits.
- Idempotency keys.
- Processing timeouts.
- Dead-letter queues.
- Worker recovery.
- Persistent execution records.
- Operational monitoring.

## 19. Important Conceptual Distinctions

| Concept | Meaning |
|---|---|
| Binary tree | A tree with at most two children per node |
| Complete binary tree | A binary tree filled level by level from left to right |
| Heap | A complete binary tree satisfying a heap-order property |
| Min-heap | A heap with the minimum element at the root |
| Max-heap | A heap with the maximum element at the root |
| Heap property | The parent-child priority relationship |
| Heap representation | The storage arrangement of heap elements |
| Sift-up | Restores ordering toward the root |
| Sift-down | Restores ordering toward the leaves |
| Heapify | Constructs a heap from existing elements |
| Priority queue | An abstract collection ordered by priority |
| Heap sort | A sorting algorithm based on heap operations |

A binary heap is not a binary search tree.

A binary search tree maintains a search-order relationship between left and right subtrees.

A heap maintains a priority relationship between parents and children.

This distinction affects searching, insertion, deletion, and traversal behavior.

## 20. Learning Outcomes

After studying the implementations, the following technical competencies can be demonstrated:

- Identify complete binary tree properties.
- Calculate parent and child indexes.
- Distinguish min-heaps from max-heaps.
- Explain the heap-order property.
- Implement insertion using sift-up.
- Implement extraction using sift-down.
- Construct heaps using bottom-up heapification.
- Validate heap structures.
- Analyze heap operation complexity.
- Implement heap sorting.
- Apply heaps to priority-based scheduling.
- Distinguish a heap from a priority queue.
- Understand the role of comparators.
- Apply validation and failure handling.
- Understand the differences between in-memory heaps and persistent relational queues.
