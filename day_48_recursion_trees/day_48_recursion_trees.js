"use strict";

/*
 * Recursion Trees
 *
 * This Node.js program models recursive calls as explicit tree nodes.
 * It focuses on branching factor, depth, repeated subproblems, per-node
 * work, memoization, and recurrence behavior.
 */

class CallNode {
    constructor(name, args, result = undefined, cost = 1) {
        this.name = name;
        this.args = args;
        this.result = result;
        this.cost = cost;
        this.children = [];
    }

    addChild(child) {
        this.children.push(child);
    }
}

function printTree(node, prefix = "", isLast = true, isRoot = true) {
    const connector = isRoot ? "" : isLast ? "└── " : "├── ";
    const result =
        node.result === undefined ? "" : ` => ${String(node.result)}`;

    console.log(
        `${prefix}${connector}${node.name}(${node.args})` +
        `${result} [cost=${node.cost}]`
    );

    const childPrefix = isRoot
        ? prefix
        : prefix + (isLast ? "    " : "│   ");

    node.children.forEach((child, index) => {
        printTree(
            child,
            childPrefix,
            index === node.children.length - 1,
            false
        );
    });
}

function countNodes(node) {
    return 1 + node.children.reduce((sum, child) => sum + countNodes(child), 0);
}

function treeHeight(node) {
    if (node.children.length === 0) {
        return 1;
    }

    return (
        1 +
        Math.max(...node.children.map((child) => treeHeight(child)))
    );
}

function totalCost(node) {
    return node.cost + node.children.reduce(
        (sum, child) => sum + totalCost(child),
        0
    );
}

function countLeaves(node) {
    if (node.children.length === 0) {
        return 1;
    }

    return node.children.reduce(
        (sum, child) => sum + countLeaves(child),
        0
    );
}


/*
 * Fibonacci intentionally creates repeated branches.
 * This makes it useful for observing exponential tree growth and
 * overlapping subproblems.
 */
function fibonacciTree(n) {
    const node = new CallNode("fib", String(n));

    if (n <= 1) {
        node.result = n;
        return node;
    }

    const left = fibonacciTree(n - 1);
    const right = fibonacciTree(n - 2);

    node.addChild(left);
    node.addChild(right);
    node.result = left.result + right.result;

    return node;
}


/*
 * Event-driven recursion tracing.
 *
 * The callbacks make the recursive lifecycle observable without changing
 * the algorithm itself. This is useful when a debugging or visualization
 * interface needs events rather than console output.
 */
function traceRecursiveFibonacci(n, onEnter, onExit) {
    function visit(value, depth) {
        onEnter({ value, depth });

        if (value <= 1) {
            onExit({ value, depth, result: value });
            return value;
        }

        const left = visit(value - 1, depth + 1);
        const right = visit(value - 2, depth + 1);
        const result = left + right;

        onExit({ value, depth, result });
        return result;
    }

    return visit(n, 0);
}


/*
 * Merge sort demonstrates a balanced divide-and-conquer tree.
 * JavaScript arrays make slicing convenient, while the explicit node
 * records the algorithm's recursive structure.
 */
function mergeSortTree(values) {
    const node = new CallNode("mergeSort", JSON.stringify(values));

    if (values.length <= 1) {
        node.result = [...values];
        return node;
    }

    const midpoint = Math.floor(values.length / 2);
    const left = mergeSortTree(values.slice(0, midpoint));
    const right = mergeSortTree(values.slice(midpoint));

    const a = left.result;
    const b = right.result;
    const merged = [];

    let i = 0;
    let j = 0;

    while (i < a.length && j < b.length) {
        if (a[i] <= b[j]) {
            merged.push(a[i++]);
        } else {
            merged.push(b[j++]);
        }
    }

    while (i < a.length) {
        merged.push(a[i++]);
    }

    while (j < b.length) {
        merged.push(b[j++]);
    }

    node.cost = values.length;
    node.addChild(left);
    node.addChild(right);
    node.result = merged;

    return node;
}


/*
 * A Promise-based recursive tree is useful when recursion controls
 * asynchronous work. Promise.all preserves both branches while allowing
 * their asynchronous operations to proceed together.
 */
function asynchronousTree(depth, branch = "root") {
    return new Promise((resolve) => {
        setTimeout(async () => {
            if (depth === 0) {
                resolve({
                    branch,
                    depth,
                    children: []
                });
                return;
            }

            const children = await Promise.all([
                asynchronousTree(depth - 1, `${branch}.L`),
                asynchronousTree(depth - 1, `${branch}.R`)
            ]);

            resolve({
                branch,
                depth,
                children
            });
        }, 2);
    });
}


/*
 * Memoization turns repeated recursive calls into cache lookups.
 * The Map stores results using the subproblem state as its key.
 */
function memoizedFibonacci(n) {
    const cache = new Map();
    let calls = 0;

    function solve(value) {
        calls++;

        if (cache.has(value)) {
            return cache.get(value);
        }

        if (value <= 1) {
            cache.set(value, value);
            return value;
        }

        const result = solve(value - 1) + solve(value - 2);
        cache.set(value, result);
        return result;
    }

    const result = solve(n);
    return { result, calls, cacheSize: cache.size };
}


/*
 * A recursion-tree-aware quicksort chooses a pivot and creates
 * differently sized subtrees. The resulting tree demonstrates why
 * balanced and highly unbalanced partitioning have different behavior.
 */
function quicksortTree(values) {
    const node = new CallNode("quickSort", JSON.stringify(values));

    if (values.length <= 1) {
        node.result = [...values];
        return node;
    }

    const pivot = values[values.length - 1];
    const lower = [];
    const greaterOrEqual = [];

    for (let i = 0; i < values.length - 1; i++) {
        if (values[i] < pivot) {
            lower.push(values[i]);
        } else {
            greaterOrEqual.push(values[i]);
        }
    }

    const left = quicksortTree(lower);
    const right = quicksortTree(greaterOrEqual);

    node.cost = values.length;
    node.addChild(left);
    node.addChild(right);
    node.result = [...left.result, pivot, ...right.result];

    return node;
}


/*
 * Converts a recursion tree into Mermaid-compatible text.
 * No Markdown fence is produced because this function is meant to
 * return raw diagram syntax for a separate renderer.
 */
function toMermaid(root) {
    const lines = ["graph TD"];
    let id = 0;

    function visit(node) {
        const current = `N${id++}`;
        const label = `${node.name}(${node.args})\\nresult=${node.result}`;
        lines.push(`${current}["${label.replaceAll('"', "'")}"]`);

        node.children.forEach((child) => {
            const childId = visit(child);
            lines.push(`${current} --> ${childId}`);
        });

        return current;
    }

    visit(root);
    return lines.join("\n");
}


async function demonstrateAsyncTree() {
    console.log("\n=== Asynchronous recursive branching ===");

    const tree = await asynchronousTree(3);

    function countAsyncNodes(node) {
        return 1 + node.children.reduce(
            (sum, child) => sum + countAsyncNodes(child),
            0
        );
    }

    console.log(`Async tree root: ${tree.branch}`);
    console.log(`Depth: ${tree.depth}`);
    console.log(`Nodes: ${countAsyncNodes(tree)}`);
    console.log(
        "Promise.all keeps the left and right recursive branches "
        + "independent while waiting for both results."
    );
}


async function main() {
    console.log("RECURSION TREES");
    console.log("================");

    console.log("\n=== Fibonacci tree ===");
    const fibRoot = fibonacciTree(5);
    printTree(fibRoot);
    console.log(`Nodes: ${countNodes(fibRoot)}`);
    console.log(`Height: ${treeHeight(fibRoot)}`);
    console.log(`Leaves: ${countLeaves(fibRoot)}`);
    console.log(`Accumulated cost: ${totalCost(fibRoot)}`);

    console.log("\n=== Merge sort tree ===");
    const mergeRoot = mergeSortTree([42, 17, 8, 31, 4, 29, 13, 22]);
    printTree(mergeRoot);
    console.log(`Sorted result: ${JSON.stringify(mergeRoot.result)}`);
    console.log(`Nodes: ${countNodes(mergeRoot)}`);

    console.log("\n=== Quicksort tree ===");
    const quickRoot = quicksortTree([9, 4, 7, 3, 10, 5, 1]);
    printTree(quickRoot);
    console.log(`Sorted result: ${JSON.stringify(quickRoot.result)}`);

    console.log("\n=== Event-driven recursive tracing ===");

    const entered = [];
    const exited = [];

    const value = traceRecursiveFibonacci(
        6,
        (event) => entered.push(event),
        (event) => exited.push(event)
    );

    console.log(`fib(6) = ${value}`);
    console.log(`Call-entry events: ${entered.length}`);
    console.log(`Call-exit events: ${exited.length}`);
    console.log(
        "The separate enter/exit streams represent call-stack entry "
        + "and return events, which are useful for execution visualizers."
    );

    console.log("\n=== Memoization ===");
    const memo = memoizedFibonacci(35);
    console.log(`fib(35) = ${memo.result}`);
    console.log(`Recursive invocations including cache hits: ${memo.calls}`);
    console.log(`Unique cached states: ${memo.cacheSize}`);

    console.log("\n=== Mermaid representation ===");
    console.log(toMermaid(fibonacciTree(3)));

    await demonstrateAsyncTree();

    console.log("\n=== Engineering observations ===");
    console.log(
        "A recursion tree exposes more than recursion depth: it reveals "
        + "branching, repeated states, local work, and the distribution of "
        + "work across recursive levels."
    );
    console.log(
        "A balanced binary tree can support logarithmic depth while a "
        + "one-child recursion has linear depth. Repeated subproblems can "
        + "inflate a tree exponentially until memoization removes redundant "
        + "evaluation."
    );
}

main().catch((error) => {
    console.error("Recursive demonstration failed:", error.message);
    process.exitCode = 1;
});
