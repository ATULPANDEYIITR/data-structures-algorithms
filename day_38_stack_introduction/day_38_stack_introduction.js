/**
 * Stack Introduction
 * ===================
 * Demonstrates LIFO behavior, array-backed stacks, linked stacks,
 * event-driven stack processing, delimiter validation, postfix
 * evaluation, and undo/redo semantics.
 *
 * Run with:
 *   node stack_introduction.js
 */

"use strict";

class StackEmptyError extends Error {
    constructor(message = "Stack is empty") {
        super(message);
        this.name = "StackEmptyError";
    }
}

class StackOverflowError extends Error {
    constructor(message = "Stack capacity exceeded") {
        super(message);
        this.name = "StackOverflowError";
    }
}

class ArrayStack {
    constructor(capacity = Infinity) {
        if (!Number.isInteger(capacity) && capacity !== Infinity) {
            throw new TypeError("capacity must be an integer or Infinity");
        }
        if (capacity <= 0) {
            throw new RangeError("capacity must be positive");
        }

        this.items = [];
        this.capacity = capacity;
    }

    push(value) {
        if (this.items.length >= this.capacity) {
            throw new StackOverflowError();
        }
        this.items.push(value);
    }

    pop() {
        if (this.isEmpty()) {
            throw new StackEmptyError("Cannot pop from an empty stack");
        }
        return this.items.pop();
    }

    peek() {
        if (this.isEmpty()) {
            throw new StackEmptyError("Cannot peek at an empty stack");
        }
        return this.items[this.items.length - 1];
    }

    isEmpty() {
        return this.items.length === 0;
    }

    isFull() {
        return this.items.length === this.capacity;
    }

    get size() {
        return this.items.length;
    }

    toArray() {
        return [...this.items].reverse();
    }
}

class LinkedStackNode {
    constructor(value, next = null) {
        this.value = value;
        this.next = next;
    }
}

class LinkedStack {
    constructor() {
        this.top = null;
        this.size = 0;
    }

    push(value) {
        this.top = new LinkedStackNode(value, this.top);
        this.size += 1;
    }

    pop() {
        if (this.top === null) {
            throw new StackEmptyError("Cannot pop from an empty linked stack");
        }

        const value = this.top.value;
        this.top = this.top.next;
        this.size -= 1;
        return value;
    }

    peek() {
        if (this.top === null) {
            throw new StackEmptyError("Cannot peek at an empty linked stack");
        }
        return this.top.value;
    }

    isEmpty() {
        return this.top === null;
    }

    toArray() {
        const result = [];
        let current = this.top;

        while (current !== null) {
            result.push(current.value);
            current = current.next;
        }

        return result;
    }
}

function demonstrateLifo() {
    console.log("\n=== LIFO behavior ===");

    const stack = new ArrayStack();

    for (const action of ["open dashboard", "open report", "open chart"]) {
        stack.push(action);
    }

    console.log("Top:", stack.peek());

    while (!stack.isEmpty()) {
        console.log("Removing:", stack.pop());
    }
}

function demonstrateArrayStack() {
    console.log("\n=== Array-backed stack ===");

    const stack = new ArrayStack(3);

    stack.push("database");
    stack.push("service");
    stack.push("controller");

    console.log("Top-to-bottom:", stack.toArray());
    console.log("Full:", stack.isFull());

    try {
        stack.push("router");
    } catch (error) {
        console.log("Expected overflow:", error.message);
    }

    console.log("Pop:", stack.pop());
    console.log("Peek:", stack.peek());
}

function demonstrateLinkedStack() {
    console.log("\n=== Linked-list stack ===");

    const stack = new LinkedStack();

    for (const request of ["authenticate", "authorize", "load-profile"]) {
        stack.push(request);
    }

    console.log("Top-to-bottom:", stack.toArray());
    console.log("Pop:", stack.pop());
    console.log("Remaining:", stack.toArray());
}

function isBalanced(expression) {
    const pairs = {
        ")": "(",
        "]": "[",
        "}": "{"
    };

    const openings = new Set(Object.values(pairs));
    const stack = new ArrayStack();

    for (const character of expression) {
        if (openings.has(character)) {
            stack.push(character);
        } else if (Object.hasOwn(pairs, character)) {
            if (stack.isEmpty() || stack.pop() !== pairs[character]) {
                return false;
            }
        }
    }

    return stack.isEmpty();
}

function demonstrateDelimiterValidation() {
    console.log("\n=== Delimiter validation ===");

    const expressions = [
        "function() { return [1, 2]; }",
        "([{}])",
        "([)]",
        "{ value: [1, 2 }"
    ];

    for (const expression of expressions) {
        console.log(`${expression} -> ${isBalanced(expression)}`);
    }
}

function evaluatePostfix(expression) {
    const stack = new ArrayStack();

    for (const token of expression.trim().split(/\s+/)) {
        if (/^-?(?:\d+(?:\.\d*)?|\.\d+)$/.test(token)) {
            stack.push(Number(token));
            continue;
        }

        if (!["+", "-", "*", "/"].includes(token)) {
            throw new Error(`Unsupported postfix token: ${token}`);
        }

        if (stack.size < 2) {
            throw new Error(`Operator ${token} requires two operands`);
        }

        const right = stack.pop();
        const left = stack.pop();

        if (token === "/" && right === 0) {
            throw new RangeError("Division by zero");
        }

        let result;

        switch (token) {
            case "+":
                result = left + right;
                break;
            case "-":
                result = left - right;
                break;
            case "*":
                result = left * right;
                break;
            case "/":
                result = left / right;
                break;
            default:
                throw new Error("Unreachable operator");
        }

        stack.push(result);
    }

    if (stack.size !== 1) {
        throw new Error("Malformed postfix expression");
    }

    return stack.pop();
}

function demonstratePostfix() {
    console.log("\n=== Postfix expression evaluation ===");

    for (const expression of ["5 2 + 3 *", "20 5 / 2 +", "9 4 - 2 *"]) {
        console.log(`${expression} = ${evaluatePostfix(expression)}`);
    }
}

function createUndoRedoManager() {
    const undoStack = new ArrayStack();
    const redoStack = new ArrayStack();

    return {
        execute(command) {
            undoStack.push(command);
            redoStack.items.length = 0;
        },

        undo() {
            if (undoStack.isEmpty()) {
                return null;
            }

            const command = undoStack.pop();
            redoStack.push(command);
            return command;
        },

        redo() {
            if (redoStack.isEmpty()) {
                return null;
            }

            const command = redoStack.pop();
            undoStack.push(command);
            return command;
        },

        state() {
            return {
                undo: undoStack.toArray(),
                redo: redoStack.toArray()
            };
        }
    };
}

function demonstrateUndoRedo() {
    console.log("\n=== Undo/redo ===");

    const history = createUndoRedoManager();

    history.execute("insert customer");
    history.execute("update customer");
    history.execute("assign account");

    console.log("Undo:", history.undo());
    console.log("Undo:", history.undo());
    console.log("Redo:", history.redo());

    // A new command creates a new history branch, so redo commands are cleared.
    history.execute("delete draft");
    console.log("After new command:", history.state());
}

function createStackEventProcessor() {
    const events = [];
    const stack = new ArrayStack();

    return {
        receive(event) {
            if (!event || typeof event.type !== "string") {
                throw new TypeError("Event must contain a string type");
            }

            stack.push(event);
            events.push(`received:${event.type}`);
        },

        processLatest() {
            if (stack.isEmpty()) {
                return null;
            }

            const event = stack.pop();
            events.push(`processed:${event.type}`);
            return event;
        },

        audit() {
            return [...events];
        },

        pending() {
            return stack.toArray();
        }
    };
}

async function demonstrateEventProcessing() {
    console.log("\n=== Event-driven LIFO processing ===");

    const processor = createStackEventProcessor();

    processor.receive({ type: "save-draft", id: 101 });
    processor.receive({ type: "validate-document", id: 101 });
    processor.receive({ type: "publish-document", id: 101 });

    // setTimeout is used only to make the processing model asynchronous.
    // The stack itself still determines that the newest pending event is processed first.
    await new Promise(resolve => setTimeout(resolve, 10));

    console.log("Processed:", processor.processLatest());
    console.log("Processed:", processor.processLatest());
    console.log("Pending:", processor.pending());
    console.log("Audit:", processor.audit());
}

function demonstrateErrors() {
    console.log("\n=== Failure conditions ===");

    const stack = new ArrayStack();

    try {
        stack.pop();
    } catch (error) {
        console.log(error.name + ":", error.message);
    }

    try {
        evaluatePostfix("8 0 /");
    } catch (error) {
        console.log("Postfix error:", error.message);
    }

    try {
        new ArrayStack(0);
    } catch (error) {
        console.log("Capacity error:", error.message);
    }
}

async function main() {
    demonstrateLifo();
    demonstrateArrayStack();
    demonstrateLinkedStack();
    demonstrateDelimiterValidation();
    demonstratePostfix();
    demonstrateUndoRedo();
    await demonstrateEventProcessing();
    demonstrateErrors();

    console.log("\n=== Complexity ===");
    console.log("Array push/pop/peek: O(1) amortized / O(1) / O(1)");
    console.log("Linked push/pop/peek: O(1) / O(1) / O(1)");
    console.log("Delimiter validation: O(n) time and O(n) space");
    console.log("Postfix evaluation: O(n) time and O(n) stack space");
}

main().catch(error => {
    console.error("Unexpected failure:", error);
    process.exitCode = 1;
});
