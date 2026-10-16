"use strict";

/*
 * Recursion fundamentals with JavaScript-specific execution patterns:
 * immutable problem decomposition, asynchronous recursion, and memoization.
 */

const assert = require("node:assert/strict");
const { performance } = require("node:perf_hooks");

function factorial(n) {
  if (!Number.isSafeInteger(n)) {
    throw new TypeError("n must be a safe integer");
  }
  if (n < 0) {
    throw new RangeError("n must be non-negative");
  }
  if (n <= 1) return 1n;
  return BigInt(n) * factorial(n - 1);
}

// BigInt prevents factorial results from losing integer precision.
function factorialBigInt(n) {
  if (typeof n !== "bigint") {
    throw new TypeError("n must be a BigInt");
  }
  if (n < 0n) throw new RangeError("n must be non-negative");
  if (n <= 1n) return 1n;
  return n * factorialBigInt(n - 1n);
}

function fibonacciNaive(n) {
  if (!Number.isSafeInteger(n) || n < 0) {
    throw new RangeError("n must be a non-negative safe integer");
  }
  if (n <= 1) return n;
  return fibonacciNaive(n - 1) + fibonacciNaive(n - 2);
}

function memoizeUnary(fn) {
  const cache = new Map();

  function memoized(value) {
    if (cache.has(value)) return cache.get(value);
    const result = fn(value, memoized);
    cache.set(value, result);
    return result;
  }

  memoized.clear = () => cache.clear();
  memoized.cacheSize = () => cache.size;
  return memoized;
}

const fibonacciMemoized = memoizeUnary((n, self) => {
  if (!Number.isSafeInteger(n) || n < 0) {
    throw new RangeError("n must be a non-negative safe integer");
  }
  if (n <= 1) return n;
  return self(n - 1) + self(n - 2);
});

function quicksort(values) {
  if (values.length <= 1) return values.slice();

  // Three-way partitioning avoids repeatedly recursing through duplicates.
  const pivot = values[Math.floor(values.length / 2)];
  const lower = [];
  const equal = [];
  const higher = [];

  for (const value of values) {
    if (value < pivot) lower.push(value);
    else if (value > pivot) higher.push(value);
    else equal.push(value);
  }

  return [...quicksort(lower), ...equal, ...quicksort(higher)];
}

function flattenNested(values, output = []) {
  if (!Array.isArray(values)) {
    throw new TypeError("The root must be an array");
  }

  for (const value of values) {
    if (Array.isArray(value)) {
      flattenNested(value, output);
    } else if (typeof value === "number" && Number.isFinite(value)) {
      output.push(value);
    } else {
      throw new TypeError("Nested values must be finite numbers or arrays");
    }
  }

  return output;
}

function deepFreezeCopy(value) {
  if (value === null || typeof value !== "object") return value;

  const copy = Array.isArray(value)
    ? value.map(deepFreezeCopy)
    : Object.fromEntries(
        Object.entries(value).map(([key, child]) => [key, deepFreezeCopy(child)])
      );

  return Object.freeze(copy);
}

function countTreeNodes(node) {
  if (node === null) return 0;
  if (typeof node !== "object" || Array.isArray(node)) {
    throw new TypeError("Tree nodes must be objects or null");
  }
  return 1 + countTreeNodes(node.left ?? null) + countTreeNodes(node.right ?? null);
}

// Explicit traversal state makes depth-limited graph search easy to inspect.
function depthLimitedPath(graph, start, goal, maxDepth) {
  if (!Number.isInteger(maxDepth) || maxDepth < 0) {
    throw new RangeError("maxDepth must be a non-negative integer");
  }

  function visit(node, remaining, path, active) {
    if (node === goal) return path.slice();
    if (remaining === 0) return null;

    for (const neighbor of graph[node] ?? []) {
      if (active.has(neighbor)) continue;
      active.add(neighbor);
      path.push(neighbor);

      const result = visit(neighbor, remaining - 1, path, active);
      if (result !== null) return result;

      path.pop();
      active.delete(neighbor);
    }
    return null;
  }

  return visit(start, maxDepth, [start], new Set([start]));
}

// Promise resolution adopts the returned promise, allowing recursive async work.
async function fetchDependencyTree(root, fetchNode, maxDepth = 4) {
  if (!Number.isInteger(maxDepth) || maxDepth < 0) {
    throw new RangeError("maxDepth must be non-negative");
  }

  async function visit(name, depth, active) {
    if (active.has(name)) {
      return { name, status: "cycle", dependencies: [] };
    }

    let dependencies;
    try {
      dependencies = await fetchNode(name);
    } catch (error) {
      return {
        name,
        status: "unavailable",
        error: error.message,
        dependencies: []
      };
    }

    if (!Array.isArray(dependencies) ||
        !dependencies.every(item => typeof item === "string")) {
      throw new TypeError(`Invalid dependency response for ${name}`);
    }

    if (depth === maxDepth) {
      return { name, status: "depth-limit", dependencies: [] };
    }

    const nextActive = new Set(active);
    nextActive.add(name);

    const children = await Promise.all(
      dependencies.map(child => visit(child, depth + 1, nextActive))
    );

    return { name, status: "loaded", dependencies: children };
  }

  return visit(root, 0, new Set());
}

function printTree(node, indentation = "") {
  console.log(`${indentation}${node.name} [${node.status}]`);
  for (const child of node.dependencies) {
    printTree(child, `${indentation}  `);
  }
}

function runTests() {
  assert.equal(factorial(0), 1n);
  assert.equal(factorial(5), 120n);
  assert.equal(factorialBigInt(30n), 265252859812191058636308480000000n);
  assert.equal(fibonacciMemoized(100), 354224848179261915075);
  assert.deepEqual(quicksort([5, 2, 5, 1, 3]), [1, 2, 3, 5, 5]);
  assert.deepEqual(flattenNested([1, [2, [3]], 4]), [1, 2, 3, 4]);
  assert.equal(countTreeNodes({ left: { left: null, right: null }, right: null }), 2);
  assert.equal(depthLimitedPath({ a: ["b"], b: ["c"], c: [] }, "a", "c", 2)
    .join("->"), "a->b->c");
  assert.throws(() => factorial(-1), RangeError);
  assert.throws(() => flattenNested([1, "invalid"]), TypeError);
  console.log("Synchronous tests passed.");
}

async function main() {
  runTests();

  console.log("\nMemoized computation");
  fibonacciMemoized.clear();
  const start = performance.now();
  const result = fibonacciMemoized(100);
  console.log(`F(100) = ${result}`);
  console.log(`Cached subproblems = ${fibonacciMemoized.cacheSize()}`);
  console.log(`Elapsed milliseconds = ${(performance.now() - start).toFixed(3)}`);

  console.log("\nImmutable nested-data decomposition");
  const original = { name: "release", children: [{ name: "api", children: [] }] };
  const snapshot = deepFreezeCopy(original);
  console.log("Original preserved:", original.children.length === 1);
  console.log("Snapshot frozen:", Object.isFrozen(snapshot.children));

  console.log("\nAsynchronous dependency traversal");
  const dependencyMap = {
    "web-app": ["api", "auth"],
    api: ["database", "cache"],
    auth: ["identity"],
    database: [],
    cache: [],
    identity: []
  };

  const tree = await fetchDependencyTree(
    "web-app",
    async name => {
      await Promise.resolve();
      if (!(name in dependencyMap)) throw new Error("Dependency not found");
      return dependencyMap[name];
    },
    3
  );
  printTree(tree);
}

main().catch(error => {
  console.error("Execution failed:", error.message);
  process.exitCode = 1;
});
