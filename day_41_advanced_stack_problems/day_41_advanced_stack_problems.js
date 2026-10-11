"use strict";

/*
 * Advanced Stack Algorithms
 *
 * The examples deliberately use JavaScript-specific features such as
 * classes, Maps, generators, structured validation, BigInt where useful,
 * and an event-driven workflow model.
 */

function assertArrayOfNumbers(values, name) {
    if (!Array.isArray(values) || values.some(value => typeof value !== "number" || !Number.isFinite(value))) {
        throw new TypeError(`${name} must contain only finite numbers.`);
    }
}

function largestRectangleHistogram(heights) {
    assertArrayOfNumbers(heights, "heights");
    if (heights.some(height => height < 0)) {
        throw new RangeError("Histogram heights cannot be negative.");
    }

    const stack = [];
    let best = 0;
    const extended = [...heights, 0];

    for (let i = 0; i < extended.length; i += 1) {
        while (stack.length > 0 && extended[stack[stack.length - 1]] > extended[i]) {
            const top = stack.pop();
            const leftBoundary = stack.length > 0 ? stack[stack.length - 1] : -1;
            const width = i - leftBoundary - 1;
            best = Math.max(best, extended[top] * width);
        }
        stack.push(i);
    }

    return best;
}

function trapRainwater(heights) {
    assertArrayOfNumbers(heights, "heights");
    if (heights.some(height => height < 0)) {
        throw new RangeError("Elevation values cannot be negative.");
    }

    let left = 0;
    let right = heights.length - 1;
    let leftMax = 0;
    let rightMax = 0;
    let water = 0;

    while (left < right) {
        if (heights[left] <= heights[right]) {
            leftMax = Math.max(leftMax, heights[left]);
            water += Math.max(0, leftMax - heights[left]);
            left += 1;
        } else {
            rightMax = Math.max(rightMax, heights[right]);
            water += Math.max(0, rightMax - heights[right]);
            right -= 1;
        }
    }

    return water;
}

function stockSpan(prices) {
    assertArrayOfNumbers(prices, "prices");

    const spans = new Array(prices.length);
    const stack = [];

    for (let day = 0; day < prices.length; day += 1) {
        while (stack.length > 0 && prices[stack[stack.length - 1]] <= prices[day]) {
            stack.pop();
        }

        spans[day] = stack.length === 0
            ? day + 1
            : day - stack[stack.length - 1];

        stack.push(day);
    }

    return spans;
}

function nextGreaterCircular(values) {
    assertArrayOfNumbers(values, "values");

    const result = new Array(values.length).fill(-1);
    const stack = [];

    for (let i = 0; i < values.length * 2; i += 1) {
        const index = i % values.length;

        while (stack.length > 0 && values[stack[stack.length - 1]] < values[index]) {
            result[stack.pop()] = values[index];
        }

        if (i < values.length) {
            stack.push(index);
        }
    }

    return result;
}

const OPERATORS = new Map([
    ["+", { precedence: 1, associativity: "left" }],
    ["-", { precedence: 1, associativity: "left" }],
    ["*", { precedence: 2, associativity: "left" }],
    ["/", { precedence: 2, associativity: "left" }],
    ["%", { precedence: 2, associativity: "left" }],
    ["^", { precedence: 3, associativity: "right" }]
]);

function tokenizeExpression(expression) {
    if (typeof expression !== "string" || expression.trim() === "") {
        throw new TypeError("Expression must be a non-empty string.");
    }

    return expression
        .replace(/[()+\-*/%^]/g, " $& ")
        .trim()
        .split(/\s+/);
}

function isOperand(token) {
    return /^[A-Za-z_][A-Za-z0-9_]*$/.test(token) || /^(\d+(\.\d*)?|\.\d+)$/.test(token);
}

function infixToPostfix(expression) {
    const output = [];
    const operators = [];

    for (const token of tokenizeExpression(expression)) {
        if (isOperand(token)) {
            output.push(token);
            continue;
        }

        if (token === "(") {
            operators.push(token);
            continue;
        }

        if (token === ")") {
            while (operators.length > 0 && operators[operators.length - 1] !== "(") {
                output.push(operators.pop());
            }

            if (operators.pop() !== "(") {
                throw new SyntaxError("Mismatched parentheses.");
            }
            continue;
        }

        const current = OPERATORS.get(token);
        if (!current) {
            throw new SyntaxError(`Unsupported token: ${token}`);
        }

        while (operators.length > 0 && operators[operators.length - 1] !== "(") {
            const top = OPERATORS.get(operators[operators.length - 1]);

            const shouldPop =
                top.precedence > current.precedence ||
                (
                    top.precedence === current.precedence &&
                    current.associativity === "left"
                );

            if (!shouldPop) {
                break;
            }

            output.push(operators.pop());
        }

        operators.push(token);
    }

    while (operators.length > 0) {
        const operator = operators.pop();

        if (operator === "(") {
            throw new SyntaxError("Mismatched parentheses.");
        }

        output.push(operator);
    }

    return output.join(" ");
}

function evaluatePostfix(postfix, variables = {}) {
    const stack = [];

    for (const token of postfix.split(/\s+/).filter(Boolean)) {
        if (!OPERATORS.has(token)) {
            const value = Object.hasOwn(variables, token)
                ? variables[token]
                : Number(token);

            if (!Number.isFinite(value)) {
                throw new TypeError(`Unknown or invalid operand: ${token}`);
            }

            stack.push(value);
            continue;
        }

        if (stack.length < 2) {
            throw new SyntaxError("Invalid postfix expression.");
        }

        const right = stack.pop();
        const left = stack.pop();

        if (token === "/" && right === 0) {
            throw new RangeError("Division by zero.");
        }

        switch (token) {
            case "+": stack.push(left + right); break;
            case "-": stack.push(left - right); break;
            case "*": stack.push(left * right); break;
            case "/": stack.push(left / right); break;
            case "%": stack.push(left % right); break;
            case "^": stack.push(left ** right); break;
            default: throw new SyntaxError(`Unsupported operator: ${token}`);
        }
    }

    if (stack.length !== 1) {
        throw new SyntaxError("Invalid postfix expression.");
    }

    return stack[0];
}

function maximalRectangle(matrix) {
    if (!Array.isArray(matrix) || matrix.length === 0) {
        return 0;
    }

    const width = matrix[0].length;
    if (width === 0 || matrix.some(row => !Array.isArray(row) || row.length !== width)) {
        throw new TypeError("Matrix must be rectangular and non-empty.");
    }

    const heights = new Array(width).fill(0);
    let best = 0;

    for (const row of matrix) {
        for (let column = 0; column < width; column += 1) {
            if (row[column] !== 0 && row[column] !== 1) {
                throw new RangeError("Matrix must contain only zero and one.");
            }

            heights[column] = row[column] === 1 ? heights[column] + 1 : 0;
        }

        best = Math.max(best, largestRectangleHistogram(heights));
    }

    return best;
}

class ExpressionMachine {
    constructor(expression) {
        this.expression = expression;
        this.postfix = infixToPostfix(expression);
    }

    evaluate(variables = {}) {
        return evaluatePostfix(this.postfix, variables);
    }

    describe() {
        return {
            infix: this.expression,
            postfix: this.postfix
        };
    }
}

/*
 * This event-driven model represents a stack algorithm processing a stream.
 * A generator is useful here because callers can consume each stack decision
 * incrementally instead of constructing a large diagnostic array.
 */
function* monotonicStackTrace(values) {
    assertArrayOfNumbers(values, "values");
    const stack = [];

    for (let index = 0; index < values.length; index += 1) {
        while (stack.length > 0 && values[stack[stack.length - 1]] >= values[index]) {
            const removed = stack.pop();
            yield {
                type: "pop",
                index,
                removedIndex: removed,
                removedValue: values[removed],
                reason: `current value ${values[index]} is smaller or equal`
            };
        }

        stack.push(index);

        yield {
            type: "push",
            index,
            value: values[index],
            depth: stack.length
        };
    }
}

class AlgorithmRunner {
    constructor() {
        this.handlers = new Map();
    }

    register(name, handler) {
        if (typeof name !== "string" || name.trim() === "") {
            throw new TypeError("Algorithm name is required.");
        }

        if (typeof handler !== "function") {
            throw new TypeError("Handler must be callable.");
        }

        this.handlers.set(name, handler);
    }

    run(name, input) {
        const handler = this.handlers.get(name);

        if (!handler) {
            throw new Error(`Algorithm '${name}' is not registered.`);
        }

        return handler(input);
    }
}

function runExamples() {
    console.log("=== Largest Rectangle ===");
    console.log(largestRectangleHistogram([2, 1, 5, 6, 2, 3]));

    console.log("\n=== Trapping Rainwater ===");
    console.log(trapRainwater([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]));

    console.log("\n=== Stock Span ===");
    console.log(stockSpan([100, 80, 60, 70, 60, 75, 85]));

    console.log("\n=== Circular Next Greater ===");
    console.log(nextGreaterCircular([1, 2, 1, 3]));

    console.log("\n=== Expression Processing ===");
    const machine = new ExpressionMachine("3 + 4 * 2 / ( 1 - 5 ) ^ 2");
    console.log(machine.describe());
    console.log(machine.evaluate());

    const variableExpression = new ExpressionMachine("revenue - cost * tax");
    console.log(variableExpression.describe());
    console.log(variableExpression.evaluate({
        revenue: 1000,
        cost: 400,
        tax: 0.2
    }));

    console.log("\n=== Maximal Binary Matrix Rectangle ===");
    console.log(maximalRectangle([
        [1, 0, 1, 0, 0],
        [1, 0, 1, 1, 1],
        [1, 1, 1, 1, 1],
        [1, 0, 0, 1, 0]
    ]));

    console.log("\n=== Stack Trace ===");
    for (const event of monotonicStackTrace([5, 3, 4, 2])) {
        console.log(event);
    }

    console.log("\n=== Algorithm Registry ===");
    const runner = new AlgorithmRunner();
    runner.register("histogram", largestRectangleHistogram);
    runner.register("rainwater", trapRainwater);
    console.log(runner.run("histogram", [2, 1, 2]));
    console.log(runner.run("rainwater", [4, 2, 0, 3, 2, 5]));
}

function runValidationChecks() {
    const checks = [
        () => largestRectangleHistogram([-1]),
        () => trapRainwater([2, -3]),
        () => evaluatePostfix("2 0 /"),
        () => infixToPostfix("( 2 + 3"),
        () => maximalRectangle([[1, 0], [1]])
    ];

    for (const check of checks) {
        try {
            check();
            throw new Error("Expected validation failure did not occur.");
        } catch (error) {
            console.log("Validation check:", error.message);
        }
    }
}

runExamples();
runValidationChecks();

console.log("\nAll JavaScript advanced-stack demonstrations completed.");
