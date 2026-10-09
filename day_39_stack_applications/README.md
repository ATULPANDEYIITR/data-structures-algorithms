# Stack Applications: Balanced Parentheses, Expression Evaluation, Function Calls, and Undo/Redo

## Scope

This project studies stacks through four closely related applications:

- balanced-parentheses validation
- infix expression evaluation
- function-call simulation
- undo/redo history

A stack follows **last-in, first-out (LIFO)** behavior. The most recently inserted element is the first element removed. That rule is not merely a data-structure definition in these applications. It directly models nested syntax, operator processing, active function calls, and reversible state history.

The six deliverables approach the same technical domain from different perspectives:

| Deliverable | Primary technical perspective |
|---|---|
| Python | Executable teaching implementation with validation and simulations |
| JavaScript | Event-driven and object-oriented workflow model |
| C++ | Repository-style command-processing and stack engine case study |
| Java | Enterprise-oriented domain model with explicit value types and services |
| SQL | Relational representation of expression evaluation, call frames, and history |
| README | Conceptual and implementation-level reference for the complete project |

The implementations intentionally do not treat all stack applications as identical. Each application has a different reason for requiring LIFO behavior.

---

## Core Stack Model

A stack exposes two fundamental operations:

- **Push** places a new element at the top.
- **Pop** removes the element currently at the top.

A useful mental model is a stack of activation records:

`bottom -> main -> processRequest -> evaluateExpression -> top`

If `evaluateExpression` returns first, the top frame disappears before `processRequest`. This is exactly the behavior required by nested function calls.

The same LIFO relationship appears in other applications, but the stored object changes:

| Application | Stack element | Why LIFO is required |
|---|---|---|
| Parentheses | Opening delimiter | The newest unmatched opening delimiter must match the next closing delimiter |
| Expression conversion | Operators | Operators must be emitted according to precedence and associativity |
| Function calls | Activation record | The most recent active function returns first |
| Undo | Previous document state | The most recent edit is the first edit reversed |
| Redo | Temporarily undone state | The most recently undone state is restored first |

Stack operations are normally O(1). Algorithms using a stack are frequently O(n) when every input element is pushed and popped at most once.

---

## Balanced Parentheses

Balanced-parentheses validation is a direct stack application.

Consider:

`function(a[2], {value: (x + y)})`

When an opening delimiter is encountered, it is pushed. When a closing delimiter is encountered, the algorithm checks the top of the stack.

The sequence is conceptually:

`(` → push

`[` → push

`{` → push

`(` → push

`)` → pop `(`

`}` → pop `{`

`]` → pop `[`

`)` → pop `(`

The expression is valid because every closing delimiter matches the most recent unmatched opening delimiter.

The important failure case is:

`([)]`

The `)` cannot match the top stack entry `[`. A set of opening delimiters alone is insufficient because the algorithm must preserve ordering.

### Quoted text

The implementations also account for delimiters inside quoted strings. In:

`print("items[0]")`

the square brackets are characters in a string rather than structural delimiters. Treating them as syntax would incorrectly reject valid input.

The implementations track the active quote and escaped characters so that structural validation is separated from textual content.

### Complexity

For an input of length `n`:

- Time: O(n)
- Auxiliary space: O(n) in the worst case
- Best practical behavior: each delimiter is examined once

The maximum stack depth is determined by nesting depth rather than simply by input size.

---

## Expression Evaluation

Arithmetic expressions introduce another use for a stack because operators cannot always be evaluated immediately.

Consider:

`3 + 4 * 2`

Multiplication has higher precedence than addition, so the correct result is:

`3 + (4 * 2) = 11`

A stack-based expression processor can first convert infix notation to postfix notation.

The expression becomes:

`3 4 2 * +`

Postfix notation removes the need to retain parentheses and precedence decisions during the final evaluation.

### Operator stack

During infix-to-postfix conversion:

- numbers go directly to the output
- opening parentheses are pushed
- closing parentheses cause operators to be popped until the corresponding opening parenthesis
- operators are compared using precedence
- right-associative exponentiation is treated differently from left-associative operators

The operator precedence represented by the implementations is:

| Operator | Precedence | Associativity |
|---|---:|---|
| `+`, `-` | 1 | Left |
| `*`, `/`, `%` | 2 | Left |
| `^` | 3 | Right |

Thus:

`2 ^ 3 ^ 2`

is interpreted as:

`2 ^ (3 ^ 2)`

and produces `512`.

### Postfix evaluation

For:

`3 4 2 * +`

the evaluation stack evolves as:

`3`

`3, 4`

`3, 4, 2`

`3, 8`

`11`

When an operator is encountered, two operands are removed from the stack, the operation is applied, and the result is pushed back.

### Validation

The implementations reject conditions such as:

- unmatched parentheses
- unsupported characters
- insufficient operands
- malformed expressions
- division by zero
- non-finite numeric results

These checks are important because a stack evaluator should not assume that input is syntactically valid.

### Complexity

For `n` tokens:

- Tokenization: O(n)
- Infix-to-postfix conversion: O(n)
- Postfix evaluation: O(n)
- Auxiliary storage: O(n)

The implementation does not require a recursive evaluator, which makes the stack behavior explicit.

---

## Function Call Simulation

A function call creates an activation record containing information such as:

- function name
- arguments
- local variables
- return information
- execution context

For:

`main() -> processRequest() -> evaluateExpression()`

the call stack contains:

`main`

`main, processRequest`

`main, processRequest, evaluateExpression`

When `evaluateExpression` finishes, its activation record is removed first.

This is a precise LIFO relationship.

### Activation records

The Python implementation uses a `CallFrame`.

The C++ implementation uses `ActivationRecord`.

The Java implementation uses an immutable `ActivationRecord` record.

The JavaScript implementation stores function frames in a private class field.

The implementations differ in language-specific design, but each models the same runtime relationship without relying on the operating system's actual call stack.

### Why a call stack matters

The call stack preserves execution context across nested calls. Without it, a runtime would have no structured way to determine which caller should receive the returned value.

A stack overflow occurs when call depth grows beyond the available runtime capacity. Recursive algorithms can therefore fail even when each individual function call is small.

An explicit simulation can impose its own maximum depth when a production system needs protection against malicious or accidental excessive nesting.

---

## Undo and Redo

Undo/redo is different from parentheses and function calls because it stores **states or state transitions** rather than syntax or activation records.

A standard design uses two stacks:

`undo stack`

`redo stack`

Suppose the document changes through:

`A -> B -> C`

After editing `C`:

`undo = [A, B]`

`current = C`

`redo = []`

Undo moves `C` onto the redo stack and restores `B`:

`undo = [A]`

`current = B`

`redo = [C]`

Another undo restores `A`.

Redo reverses that operation by moving the current state back to the undo stack and taking a state from the redo stack.

### Branching history

A critical rule is that a new edit after an undo invalidates the old redo path.

For:

`A -> B -> C`

then:

`undo -> B`

then:

`edit D`

the history becomes:

`A -> B -> D`

The previous `C` branch cannot safely be replayed as a redo operation.

The implementations therefore clear the redo stack whenever a new edit is committed after an undo.

### Snapshot versus command history

The examples use complete document states because they make stack behavior easy to observe.

Large production editors often store commands, inverse operations, patches, or immutable deltas instead of duplicating complete documents.

A full snapshot has simple recovery semantics but may consume more memory.

A command-based design can use less memory, but every command must provide reliable inverse behavior. Complex commands can make undo correctness substantially harder.

---

## Python Implementation

The Python program is the most comprehensive executable teaching implementation.

`validate_balanced_parentheses()` demonstrates delimiter matching while accounting for quoted strings.

`infix_to_postfix()` separates expression conversion from evaluation. This makes the operator stack visible and allows malformed expressions to be rejected before evaluation.

`evaluate_postfix()` demonstrates the second stack involved in expression processing: the operand stack.

`CallStack` represents activation records explicitly rather than relying on Python recursion.

`UndoRedoEditor` uses two stacks of immutable `TextState` objects. The separation between current state, undo history, and redo history makes history branching explicit.

The Python implementation also exercises failure conditions such as division by zero, an empty call stack, malformed parentheses, negative factorial input, and invalid expression syntax.

---

## JavaScript Implementation

The JavaScript implementation emphasizes language-specific behavior rather than translating the Python program line by line.

`CallStack` uses private class fields to encapsulate its internal frame array.

`HistoryEditor` extends `EventTarget`. Changes to the history produce `CustomEvent` objects containing the current value and stack depths. This models how a browser or event-driven application can notify a user interface when stack-based history changes.

Expression processing uses JavaScript's `Map`, regular-expression tokenization, class methods, and runtime exceptions.

The bracket validator deliberately distinguishes structural delimiters from characters inside quoted strings.

This combination makes the implementation relevant to interactive editors, calculators, command interfaces, and browser applications.

---

## C++ Case Study

The C++ program models a command-processing service.

The `DelimiterValidator` checks nested command syntax before a command is accepted.

`ExpressionEngine` provides a complete infix-to-postfix pipeline. It separates lexical processing, operator precedence, postfix construction, and evaluation.

`CallStack` stores `ActivationRecord` objects and demonstrates explicit function-entry and function-return behavior.

`DocumentHistory` models reversible document state with two `std::vector` stacks. The use of vectors provides contiguous storage and efficient amortized push/pop behavior at the end.

The case study connects these mechanisms through command processing rather than presenting unrelated language exercises.

### C++ design decisions

`std::vector` is appropriate for stack-like storage when access is restricted to the end of the container.

`std::unordered_map` provides direct lookup for matching delimiters.

`std::optional` represents the absence of a previous token without inventing a sentinel token.

Exceptions distinguish malformed input, arithmetic failures, and invalid stack operations.

The implementation targets C++17 and does not require external libraries.

---

## Java Implementation

The Java program uses an enterprise-oriented domain model.

`ValidationResult` represents delimiter-validation outcomes as an immutable record.

`ActivationRecord` models a function execution context as a record containing function name, arguments, and local variables.

`CallStack` encapsulates its internal `ArrayDeque`. Clients cannot directly mutate the stack, which keeps stack invariants under the class's control.

`DocumentService` owns the current document state and two independent history stacks.

The expression engine uses Java collections, regular-expression tokenization, functional interfaces, and explicit arithmetic validation.

The service-oriented structure demonstrates why a stack should generally be hidden behind domain operations such as `enter()`, `exit()`, `update()`, `undo()`, and `redo()` rather than exposing raw collection operations throughout an enterprise application.

---

## SQL Data Model

The SQL implementation represents the stack-related domain relationally.

### Expressions

`expressions` stores source expressions.

`expression_evaluations` stores a particular evaluation attempt, its postfix tokens, result, status, and failure information.

A foreign key prevents an evaluation from referencing an expression that does not exist.

A check constraint restricts evaluation status to `SUCCESS` or `FAILED` and requires an error message when evaluation fails.

### Function calls

`call_sessions` represents an execution context.

`call_frames` represents activation records.

`parent_frame_id` models the caller relationship.

`stack_depth` makes the logical stack position queryable.

An active frame is identified by a null `returned_at` value.

An index on active frames supports queries that inspect the currently executing portion of a session.

The relational model does not replace an in-memory runtime call stack. It provides a durable representation useful for diagnostics, auditing, simulation, or execution tracing.

### Document history

`documents` stores the current state.

`document_history` stores historical states.

The unique constraint on `(document_id, version_number)` prevents two history records from claiming the same document version.

The SQL transaction demonstrates an important production property: the current document update and its corresponding history record should succeed or fail together.

---

## Relationship Between the Four Applications

The four applications share the same underlying LIFO rule but solve different problems.

### Syntax nesting

The delimiter stack answers:

> Which opening construct is the next closing construct required to match?

This is about structural nesting.

### Expression processing

The operator and operand stacks answer:

> Which operation or operand must be processed next while preserving precedence and associativity?

This is about evaluation order.

### Function calls

The activation stack answers:

> Which currently executing function must resume when the current function returns?

This is about execution context.

### Undo/redo

The history stacks answer:

> Which previous state should be restored, or which recently undone state should be reinstated?

This is about temporal state management.

The fact that all four use stacks does not make their algorithms interchangeable.

---

## Edge Cases and Failure Modes

### Delimiter validation

Important failures include an unexpected closing delimiter, mismatched delimiter types, an unclosed opening delimiter, and an unterminated quoted string.

Deeply nested input can consume significant memory even though the algorithm remains linear in time.

### Expression evaluation

Invalid arithmetic syntax must not reach the evaluation phase.

Division by zero must be detected explicitly.

Operator associativity must be handled correctly. Treating exponentiation as ordinary left-associative arithmetic changes the meaning of expressions such as `2 ^ 3 ^ 2`.

Numeric overflow or non-finite results should be detected where the runtime supports that distinction.

### Function calls

Returning from an empty call stack is an invalid state.

Production runtimes need limits on call depth to reduce the impact of accidental infinite recursion or deliberately malicious input.

Activation records can become expensive when they contain large local structures. A real runtime therefore manages memory carefully and may place large objects outside the frame itself.

### Undo/redo

Undoing when no history exists must be a safe no-op or a clearly reported failure.

Redoing when no redo state exists must not alter the document.

A new edit after undo must invalidate the old redo branch in a simple linear-history design.

For very large documents, storing complete snapshots can create substantial memory pressure.

---

## Common Implementation Mistakes

A delimiter validator that only counts the number of opening and closing characters can accept invalid nesting such as `([)]`. Correct validation requires stack order.

An expression evaluator that ignores operator precedence can calculate `3 + 4 * 2` as `14` rather than `11`.

An evaluator that treats every operator as left-associative can calculate exponentiation incorrectly.

A function-call simulation that removes frames from the bottom instead of the top does not represent actual call-return behavior.

An undo implementation that fails to clear redo history after a new edit allows users to navigate into an obsolete branch of document state.

An exposed stack collection can allow unrelated code to violate invariants. Encapsulating stack operations behind domain methods provides stronger control.

---

## Performance Considerations

For delimiter validation, the primary cost is proportional to input length.

For expression conversion and postfix evaluation, each token is processed a bounded number of times, producing O(n) time complexity.

Call-stack push and pop operations are normally O(1).

Undo and redo stack operations are also O(1) for the stack itself. If complete document snapshots are copied, the effective cost also depends on document size.

Memory consumption is dominated by maximum nesting depth, maximum call depth, expression token count, or retained history size depending on the application.

For large-scale systems, command compression, immutable deltas, structural sharing, or bounded history can reduce memory consumption.

---

## Security Considerations

Stack-based processing is often exposed to attacker-controlled input.

A parser should place limits on input length and nesting depth.

Expression evaluators should use explicit whitelists of permitted operators rather than evaluating arbitrary source-language code.

Function-call simulations should reject excessive depth to avoid uncontrolled memory consumption.

History systems should consider limits on stored state size and the number of retained versions.

Error messages should provide enough diagnostic information for legitimate debugging without exposing sensitive application state.

Database constraints should protect against invalid references even when application-level validation fails.

---

## Production Design Considerations

The stack should generally be encapsulated behind operations that express domain behavior.

For a parser, this may be `pushOpening()` and `matchClosing()`.

For an evaluator, it may be `pushOperand()`, `pushOperator()`, and `applyOperator()`.

For execution tracing, it may be `enterFunction()` and `returnFromFunction()`.

For an editor, it may be `edit()`, `undo()`, and `redo()`.

This approach prevents arbitrary consumers from manipulating internal stack state and makes validation rules easier to enforce.

A production implementation should also distinguish invalid input from operational failures. A malformed expression is a validation problem, while a resource-exhaustion condition is an operational problem.

---

## Technical Distinction

The central relationship can be represented as:

`Input structure -> Stack -> LIFO decision -> domain-specific behavior`

For balanced parentheses:

`opening delimiter -> delimiter stack -> most recent unmatched opening -> matching validation`

For expression evaluation:

`operator/operand -> operator or operand stack -> precedence-driven processing -> arithmetic result`

For function calls:

`function entry -> activation stack -> most recent active frame -> function return`

For undo/redo:

`state transition -> undo/redo stacks -> most recent state transition -> restored state`

The common data structure is simple. The domain rules layered on top of it are what make each application technically distinct.
