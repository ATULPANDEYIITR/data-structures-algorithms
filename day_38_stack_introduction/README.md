# Stack Introduction

## Scope

This learning artifact develops the stack data structure from its defining LIFO behavior through two concrete implementations: an array-backed stack and a linked-list stack. It also shows why stacks are useful in delimiter validation, postfix expression evaluation, history management, event processing, and other situations where the most recently created or received item must be handled first.

The five implementations deliberately use different perspectives. Python emphasizes reusable data structures and algorithmic applications. JavaScript models event-driven processing and history state. C++ presents a memory-oriented workflow case study. Java models an enterprise service boundary with explicit domain types. PostgreSQL represents stack state relationally and enforces capacity and integrity rules at the database layer.

## Core Concept: LIFO

LIFO means **Last In, First Out**. The most recently pushed element becomes the first element removed.

A stack exposes a restricted access pattern. New elements enter through the top, and removals also occur through the top. An implementation may use an array, dynamic array, linked nodes, or another storage mechanism, but the LIFO rule remains the defining abstraction.

For a stack containing `A`, `B`, and `C`, where `C` was pushed last, the removal order is `C`, `B`, `A`.

The principal operations are:

| Operation | Meaning | Typical complexity |
|---|---|---:|
| `push` | Add an element to the top | O(1) |
| `pop` | Remove and return the top element | O(1) |
| `peek` | Inspect the top without removing it | O(1) |
| `isEmpty` | Determine whether the stack has no elements | O(1) |
| `size` | Return the number of elements | O(1) |

The data structure does not normally support arbitrary removal from the middle. That restriction is useful because it makes the intended access policy explicit.

## Stack State and Invariants

A valid stack maintains a clear relationship between its storage and its top element.

For an array-backed stack, the top is represented by the final occupied array position. In the Python implementation, `self._items[-1]` is the top and `append` and `pop` operate on that same end.

For a linked-list stack, the top is represented by the head node. A push creates a new node whose `next` pointer references the previous top. A pop moves the head reference to the next node.

A stack should also protect its boundary conditions. Calling `pop` or `peek` on an empty stack is an underflow condition. A fixed-capacity stack can also experience overflow when another element would exceed its declared capacity.

## Array-Based Stacks

The Python implementation uses a Python list as the backing storage. The JavaScript implementation uses a JavaScript array, and the C++ case study uses `std::vector`.

The array representation is compact and cache-friendly because elements are stored in contiguous storage. Dynamic arrays can occasionally resize, so `push` is generally described as amortized O(1) rather than unconditionally O(1).

A fixed-capacity stack adds a deliberate capacity check before insertion. This is useful when the maximum amount of stack storage is known or when an application must reject additional work rather than silently consume more memory.

The Python `ArrayStack` exposes `capacity`, `is_full`, `push`, `pop`, and `peek`, making the capacity rule part of the abstraction rather than an informal application convention.

## Linked-List Stacks

A linked-list stack stores each element in a node. Each node contains a value and a reference to the next node.

The top is the head node. Pushing creates one node and places it before the existing head. Popping removes the head and advances the top reference.

Both operations remain O(1), but linked storage has different engineering characteristics from an array. Each node requires separate allocation and contains link metadata. This increases allocation and pointer-management overhead and can reduce cache locality.

The linked representation is valuable when demonstrating dynamic node-based storage or when the surrounding design naturally works with linked structures. It is not automatically faster than an array-backed implementation.

## Python Implementation

The Python program defines `ArrayStack`, `LinkedStack`, and `MinStack`.

`ArrayStack` demonstrates a conventional list-backed LIFO structure, optional fixed capacity, underflow handling, iteration from top to bottom, and explicit stack state.

`LinkedStack` uses the `_Node` dataclass. The node at `_top` represents the current top, so insertion and removal never require shifting existing elements.

`MinStack` demonstrates an augmented stack. It maintains a second stack containing minimum values observed at each relevant depth. As a result, `min_value()` remains O(1) while ordinary push and pop operations remain O(1).

The program then applies stacks to concrete algorithms. `validate_parentheses` pushes opening delimiters and requires each closing delimiter to match the most recently opened delimiter. This is a direct LIFO relationship rather than a superficial use of a stack.

`evaluate_postfix` processes operands by pushing them and processes operators by popping the two most recent operands. The implementation validates malformed expressions and division by zero.

The undo/redo example uses two stacks. Undo transfers an operation from the undo stack to the redo stack. A new operation clears redo history because it creates a new editing history branch.

## JavaScript Implementation

The JavaScript program uses `ArrayStack` for array-backed storage and `LinkedStack` for explicit node-based storage.

The event-processing example demonstrates an important distinction between JavaScript's asynchronous runtime and the stack itself. `setTimeout` introduces an asynchronous scheduling boundary, but once events are stored in the stack, the newest pending event is selected through LIFO semantics.

The undo/redo manager uses two independent stacks. A newly executed command clears the redo stack, while `undo()` moves the most recent command from undo history to redo history.

The JavaScript implementation also validates delimiters and evaluates postfix expressions. It uses JavaScript-specific features such as `Set`, object property checks, promises, and asynchronous functions without turning the program into a generic JavaScript syntax tutorial.

## C++ Case Study

The C++ program models a workflow engine in which operations are submitted as `WorkflowEvent` objects.

The `WorkflowEngine` stores pending events in a `std::vector`. Submission appends an event to the end, while `processLatest()` removes the last event. This models a workload where the most recently submitted pending operation receives priority.

The event structure contains an identifier, operation type, and payload. This makes the stack example represent a meaningful system workload instead of isolated integer manipulation.

The program also implements delimiter validation using the stack and reverses text by pushing each character and removing characters in reverse insertion order.

C++ exception handling is used for underflow and fixed-capacity overflow. The program uses move semantics when transferring stack elements from the vector, avoiding unnecessary string copies in the workflow path.

The vector-backed design provides O(1) amortized insertion and O(1) removal from the end. A linked implementation could avoid vector resizing but would introduce node allocation and pointer overhead.

## Java Implementation

The Java implementation treats the stack as a service boundary through the generic `StackService<T>` class. It uses `ArrayDeque`, which is an appropriate standard-library implementation for stack semantics.

`WorkflowCommand` is a Java record containing an identifier, operation type, and resource. Its compact constructor validates the domain state before the command enters the stack.

`OperationType` is an enum rather than a collection of strings. This prevents arbitrary operation names from silently entering the workflow model.

`WorkflowProcessor` separates pending work from processed work and maintains operation statistics with an `EnumMap`. `processLatest()` explicitly models LIFO workflow behavior through the stack service.

The Java implementation also demonstrates delimiter validation and postfix evaluation. Exceptions distinguish invalid capacity, empty-stack access, malformed expressions, and arithmetic failure.

This design demonstrates how a stack can sit behind an enterprise-oriented service abstraction rather than being exposed as raw collection manipulation throughout an application.

## PostgreSQL Data Model

The SQL script creates a `stack_learning` schema with two central tables: `stacks` and `stack_items`.

`stacks` records the stack identity, implementation type, and optional capacity. `stack_items` records the value, push sequence, push timestamp, and optional pop timestamp.

The foreign key from `stack_items.stack_id` to `stacks.stack_id` prevents orphaned elements. The unique constraint on `(stack_id, push_sequence)` prevents two elements from occupying the same logical insertion position within a stack.

The `active_stack_items` view exposes only elements that have not been popped.

The LIFO top is identified by the largest active `push_sequence`. Ordering active elements by `push_sequence DESC` therefore presents the stack from top to bottom.

## Database-Level Capacity Enforcement

The SQL implementation does not rely solely on application code to enforce fixed capacity. The `enforce_stack_capacity()` PostgreSQL trigger function locks the relevant stack row, counts active items, and rejects an insertion when the configured capacity has already been reached.

This demonstrates an important database design principle: an invariant that must remain true regardless of which client performs an insertion can be enforced at the database layer.

The trigger is deliberately concerned with active elements rather than historical elements. Popped items remain in the table for history, but they no longer consume stack capacity.

## Transactional Pop

The SQL pop example runs inside a transaction. A common table expression identifies the active element with the greatest `push_sequence`, locks it for update, and marks it as popped.

The operation therefore preserves history rather than physically deleting the element.

The transaction boundary is important if multiple database clients can manipulate the same stack. Locking the selected top element reduces the risk of concurrent sessions attempting to process the same logical stack element.

## Applications of Stacks

### Delimiter Matching

Delimiter matching requires the most recently opened delimiter to be closed first.

For `({[]})`, the opening sequence creates a stack containing `(`, `{`, and `[`. The `]` must match `[`, the `}` must match `{`, and the `)` must match `(`.

An expression such as `([)]` fails because `)` attempts to close `(` while `[` is still the most recent unmatched opening delimiter.

This algorithm requires O(n) time and O(n) worst-case auxiliary space.

### Postfix Expression Evaluation

Postfix notation places operators after their operands.

For `5 2 + 3 *`, the stack first receives `5` and `2`. The `+` operator removes those values and pushes `7`. The `3` is then pushed, and `*` removes `3` and `7`, producing `21`.

The stack naturally provides the operand ordering required by postfix evaluation.

### Undo and Redo

An undo stack records operations in the order they occur. The newest operation is the first candidate for reversal.

A separate redo stack stores operations that have been undone. Executing a new operation after an undo normally clears redo history because the new action creates a different sequence of application state changes.

### Event and Work Processing

A stack can model workloads where the latest pending item should be processed first. This differs from a queue, where the oldest pending item normally receives priority.

The C++ and Java examples use domain objects rather than primitive values to show how the same LIFO rule can govern meaningful workflow records.

## Array Stack Versus Linked Stack

| Property | Array-backed stack | Linked-list stack |
|---|---|---|
| Top representation | Array end | Head node |
| Push | O(1) amortized | O(1) |
| Pop | O(1) | O(1) |
| Memory layout | Compact contiguous storage | Separate nodes |
| Resizing | May be required for dynamic arrays | Not required |
| Allocation overhead | Lower in typical dynamic-array implementations | Higher because nodes require allocation |
| Cache locality | Usually favorable | Usually weaker |
| Capacity | Natural fixed boundary or dynamic growth | Naturally dynamic unless explicitly bounded |

The LIFO abstraction is the same in both designs. The storage trade-offs are different.

## Edge Cases and Failure Conditions

An empty stack cannot provide a meaningful `pop` or `peek` result. The implementations explicitly reject those operations instead of returning arbitrary sentinel values.

Fixed-capacity stacks must reject insertion at capacity. Silent acceptance would violate the declared memory boundary.

Delimiter validation must reject a closing delimiter when there is no corresponding opening delimiter and must reject a mismatched delimiter.

Postfix evaluation must reject unsupported tokens, insufficient operands, malformed final stack state, and division by zero.

For history management, a new operation after an undo must invalidate the redo path if the model represents a linear editing history.

## Performance Considerations

Stack operations should normally be designed so that the top can be accessed without scanning the structure.

Appending and removing from the end of an array-backed structure avoids the O(n) shifting that would occur if the implementation inserted and removed from the front of an ordinary array.

A linked stack maintains O(1) push and pop because only the head node changes. Its practical cost includes allocations, pointer dereferencing, and additional memory per element.

Algorithms such as delimiter validation and postfix evaluation are linear in the number of input tokens or characters because each item is pushed and popped a bounded number of times.

## Common Mistakes

Treating a stack as a general-purpose indexed collection weakens the abstraction because arbitrary middle-element access is not part of the intended LIFO interface.

Removing from the beginning of a dynamic array can turn an intended O(1) stack operation into O(n) work because remaining elements may need to be shifted.

For linked stacks, forgetting to update the top pointer during `pop` can cause lost elements or invalid traversal.

For fixed-capacity stacks, checking capacity after insertion is incorrect because the invalid state has already been created.

In postfix evaluation, popping operands in the wrong order changes subtraction and division. For `left right -`, the result must be `left - right`, not `right - left`.

## Practical Design Principles

A stack abstraction should expose the operations required by the application while hiding storage details.

The implementation should define explicit behavior for empty-stack access and, where relevant, capacity overflow.

The top should have a direct representation so that `push`, `pop`, and `peek` remain constant-time operations.

An application should choose array-backed or linked storage based on workload and memory behavior rather than assuming that one representation is universally superior.

When a stack is used to implement an algorithm, the reason for the LIFO ordering should be identifiable in the problem itself. Delimiter nesting, operand processing, history reversal, and latest-event handling all have a direct relationship with the most-recent-first rule.

## Security and Reliability Considerations

Stacks can grow without an explicit limit when they are backed by dynamically expanding storage. Applications processing untrusted input should consider maximum depth to prevent excessive memory consumption.

Recursive algorithms use the call stack implicitly. Deeply nested untrusted input can therefore cause stack exhaustion even when the application does not explicitly create a stack object.

Expression evaluators must validate tokens rather than interpreting arbitrary input as executable code. The examples perform explicit token recognition and arithmetic operations.

For concurrent applications, an ordinary stack object is not automatically thread-safe. Shared stacks require appropriate synchronization or a concurrency-aware design when multiple workers can push and pop simultaneously.

The SQL implementation demonstrates database-side capacity enforcement and transactional access because application-level checks alone can be insufficient when multiple database clients operate concurrently.

## Implementation Relationship

The same abstract operation appears through different implementation mechanisms:

`push` adds an element to the top.

`pop` removes the most recently pushed element.

`peek` observes the most recently pushed element without changing stack state.

Python demonstrates both list and node storage directly. JavaScript demonstrates object-oriented and asynchronous workflow usage. C++ emphasizes a realistic event-processing system and explicit resource behavior. Java emphasizes typed domain modeling and service-oriented encapsulation. PostgreSQL models persistence, constraints, indexes, transactions, and historical state.

The central data-structure rule remains unchanged across all five implementations: the top element is the next element eligible for removal.
