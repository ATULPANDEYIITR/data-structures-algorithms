"use strict";

/*
 * Basic Recursion Problems
 *
 * This implementation emphasizes JavaScript-specific concerns:
 * BigInt arithmetic for exact large integers, immutable input handling,
 * recursive closures, explicit validation, and event-driven tracing.
 *
 * Run with Node.js:
 *     node recursion_problems.js
 *
 * No npm dependencies are required.
 */

function requireInteger(value, name) {
    if (typeof value !== "number" || !Number.isSafeInteger(value)) {
        throw new TypeError(`${name} must be a safe JavaScript integer.`);
    }
}

function requireBigInt(value, name) {
    if (typeof value !== "bigint") {
        throw new TypeError(`${name} must be a BigInt.`);
    }
}

function factorial(n) {
    requireInteger(n, "n");

    if (n < 0) {
        throw new RangeError("Factorial requires a non-negative integer.");
    }

    if (n <= 1) {
        return 1n;
    }

    return BigInt(n) * factorial(n - 1);
}

function fibonacci(n) {
    requireInteger(n, "n");

    if (n < 0) {
        throw new RangeError("The Fibonacci index cannot be negative.");
    }

    // A Map stores computed states so each index is calculated once.
    const cache = new Map([
        [0, 0n],
        [1, 1n]
    ]);

    function calculate(index) {
        if (cache.has(index)) {
            return cache.get(index);
        }

        const result = calculate(index - 1) + calculate(index - 2);
        cache.set(index, result);
        return result;
    }

    return calculate(n);
}

function fibonacciWithStatistics(n) {
    requireInteger(n, "n");

    if (n < 0) {
        throw new RangeError("The Fibonacci index cannot be negative.");
    }

    const cache = new Map([
        [0, 0n],
        [1, 1n]
    ]);

    let evaluations = 0;

    function calculate(index) {
        if (cache.has(index)) {
            return cache.get(index);
        }

        evaluations += 1;
        const value = calculate(index - 1) + calculate(index - 2);
        cache.set(index, value);
        return value;
    }

    return {
        value: calculate(n),
        computedStates: evaluations,
        cachedStates: cache.size
    };
}

function power(base, exponent) {
    requireBigInt(base, "base");
    requireInteger(exponent, "exponent");

    if (base === 0n && exponent < 0) {
        throw new RangeError("Zero cannot have a negative exponent.");
    }

    function positivePower(value, exp) {
        if (exp === 0) {
            return 1n;
        }

        const half = positivePower(value, Math.floor(exp / 2));
        const squared = half * half;

        return exp % 2 === 0 ? squared : squared * value;
    }

    if (exponent < 0) {
        // BigInt has no fractional representation. Return an exact rational
        // description rather than silently converting to an imprecise Number.
        return {
            numerator: 1n,
            denominator: positivePower(base, -exponent)
        };
    }

    return positivePower(base, exponent);
}

function sumDigits(n) {
    requireBigInt(n, "n");

    const magnitude = n < 0n ? -n : n;

    function calculate(value) {
        if (value < 10n) {
            return value;
        }

        return value % 10n + calculate(value / 10n);
    }

    return calculate(magnitude);
}

function reverseNumber(n) {
    requireBigInt(n, "n");

    const negative = n < 0n;
    const magnitude = negative ? -n : n;

    function reverse(value, accumulated = 0n) {
        if (value === 0n) {
            return accumulated;
        }

        return reverse(
            value / 10n,
            accumulated * 10n + value % 10n
        );
    }

    const result = reverse(magnitude);
    return negative ? -result : result;
}

function sumArray(values, index = 0) {
    if (!Array.isArray(values)) {
        throw new TypeError("values must be an array.");
    }

    if (!Number.isInteger(index) || index < 0 || index > values.length) {
        throw new RangeError("The traversal index is invalid.");
    }

    if (index === values.length) {
        return 0;
    }

    if (typeof values[index] !== "number" || !Number.isFinite(values[index])) {
        throw new TypeError(`Invalid numeric element at index ${index}.`);
    }

    return values[index] + sumArray(values, index + 1);
}

function findIndex(values, target, index = 0) {
    if (!Array.isArray(values)) {
        throw new TypeError("values must be an array.");
    }

    if (!Number.isInteger(index) || index < 0 || index > values.length) {
        throw new RangeError("The traversal index is invalid.");
    }

    if (index === values.length) {
        return -1;
    }

    if (Object.is(values[index], target)) {
        return index;
    }

    return findIndex(values, target, index + 1);
}

function mapRecursively(values, transform, index = 0) {
    if (!Array.isArray(values)) {
        throw new TypeError("values must be an array.");
    }

    if (typeof transform !== "function") {
        throw new TypeError("transform must be a function.");
    }

    if (!Number.isInteger(index) || index < 0 || index > values.length) {
        throw new RangeError("The traversal index is invalid.");
    }

    if (index === values.length) {
        return [];
    }

    // The spread operation returns a new array without modifying the input.
    return [
        transform(values[index]),
        ...mapRecursively(values, transform, index + 1)
    ];
}

function binarySearch(sortedValues, target, low = 0, high = sortedValues.length - 1) {
    if (!Array.isArray(sortedValues)) {
        throw new TypeError("sortedValues must be an array.");
    }

    if (!Number.isInteger(low) || !Number.isInteger(high)) {
        throw new TypeError("Search bounds must be integers.");
    }

    if (low < 0 || high >= sortedValues.length) {
        if (!(sortedValues.length === 0 && low === 0 && high === -1)) {
            throw new RangeError("Search bounds are outside the array.");
        }
    }

    if (low > high) {
        return -1;
    }

    const middle = low + Math.floor((high - low) / 2);
    const current = sortedValues[middle];

    if (current === target) {
        return middle;
    }

    return target < current
        ? binarySearch(sortedValues, target, low, middle - 1)
        : binarySearch(sortedValues, target, middle + 1, high);
}

/*
 * A trace is emitted as events rather than hard-coded console messages.
 * This permits callers to collect, filter, or display recursion steps.
 */
function factorialWithTrace(n, emit) {
    requireInteger(n, "n");

    if (typeof emit !== "function") {
        throw new TypeError("emit must be a function.");
    }

    if (n < 0) {
        throw new RangeError("Factorial requires a non-negative integer.");
    }

    function calculate(value) {
        emit({ type: "enter", value });

        if (value <= 1) {
            emit({ type: "base", value, result: 1n });
            return 1n;
        }

        const result = BigInt(value) * calculate(value - 1);
        emit({ type: "return", value, result });
        return result;
    }

    return calculate(n);
}

class PullRequestRecursionLab {
    /*
     * A realistic repository example uses recursion to inspect a nested
     * tree of changed files and sum their review-risk scores.
     */
    static totalReviewRisk(nodes, index = 0) {
        if (!Array.isArray(nodes)) {
            throw new TypeError("nodes must be an array.");
        }

        if (!Number.isInteger(index) || index < 0 || index > nodes.length) {
            throw new RangeError("The node index is invalid.");
        }

        if (index === nodes.length) {
            return 0;
        }

        const node = nodes[index];

        if (!node || typeof node !== "object") {
            throw new TypeError(`Invalid change node at index ${index}.`);
        }

        if (typeof node.risk !== "number" || node.risk < 0 ||
            !Number.isFinite(node.risk)) {
            throw new RangeError(`Invalid risk score at index ${index}.`);
        }

        const nestedRisk = PullRequestRecursionLab.totalReviewRisk(
            node.children ?? []
        );

        return node.risk + nestedRisk +
            PullRequestRecursionLab.totalReviewRisk(nodes, index + 1);
    }
}

function assert(condition, message) {
    if (!condition) {
        throw new Error(`Assertion failed: ${message}`);
    }
}

function expectError(operation, expectedType) {
    let caught = false;

    try {
        operation();
    } catch (error) {
        if (!(error instanceof expectedType)) {
            throw error;
        }
        caught = true;
    }

    assert(caught, `Expected ${expectedType.name}.`);
}

function main() {
    console.log("Factorial");
    console.log(Array.from({ length: 8 }, (_, n) => ({
        n,
        factorial: factorial(n).toString()
    })));

    console.log("\nFibonacci with memoization");
    console.log(Array.from({ length: 12 }, (_, n) =>
        fibonacci(n).toString()
    ));
    console.log("F(100):", fibonacci(100).toString());
    console.log("Statistics:", fibonacciWithStatistics(40));

    console.log("\nPower calculation");
    console.log("2^100:", power(2n, 100).toString());
    const reciprocal = power(2n, -5);
    console.log(
        "2^-5:",
        `${reciprocal.numerator}/${reciprocal.denominator}`
    );

    console.log("\nDigit operations");
    console.log("Digit sum:", sumDigits(-4729n).toString());
    console.log("Reversed number:", reverseNumber(-1200n).toString());

    console.log("\nRecursive array operations");
    const measurements = [14, 7, 22, 7, -3];
    console.log("Measurements:", measurements);
    console.log("Sum:", sumArray(measurements));
    console.log("First 7:", findIndex(measurements, 7));
    console.log("Doubled:", mapRecursively(measurements, value => value * 2));
    console.log("Binary search:", binarySearch([-3, 7, 14, 22], 14));

    console.log("\nRecursion trace");
    const trace = [];
    const tracedResult = factorialWithTrace(4, event => trace.push(event));
    console.log("Result:", tracedResult.toString());
    console.log("Events:", trace.map(event =>
        `${event.type}:${event.value}`
    ));

    console.log("\nNested repository review risk");
    const changedFiles = [
        {
            path: "src/auth/session.js",
            risk: 5,
            children: [
                { path: "token-validation", risk: 3, children: [] },
                { path: "cookie-policy", risk: 2, children: [] }
            ]
        },
        {
            path: "tests/auth/session.test.js",
            risk: 1,
            children: []
        }
    ];
    console.log(
        "Total risk:",
        PullRequestRecursionLab.totalReviewRisk(changedFiles)
    );

    expectError(() => factorial(-1), RangeError);
    expectError(() => fibonacci(2.5), TypeError);
    expectError(() => power(0n, -1), RangeError);
    expectError(() => sumDigits(12), TypeError);
    expectError(() => sumArray([1, NaN]), TypeError);

    assert(factorial(0) === 1n, "factorial base case");
    assert(fibonacci(10) === 55n, "Fibonacci recurrence");
    assert(power(3n, 4) === 81n, "power calculation");
    assert(sumDigits(0n) === 0n, "zero digit sum");
    assert(reverseNumber(1200n) === 21n, "reverse with leading zeros");
    assert(sumArray([]) === 0, "empty array sum");
    assert(findIndex([3, 5], 8) === -1, "missing element");
    assert(binarySearch([], 8) === -1, "empty binary search");

    console.log("\nAll JavaScript assertions passed.");
    console.log(
        "Use iterative loops for very deep traversals: JavaScript engines " +
        "do not guarantee tail-call optimization."
    );
}

main();
