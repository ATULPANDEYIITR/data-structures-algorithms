"use strict";

/*
 * Heap Sort and repository-style batch processing.
 *
 * The implementation uses a max-heap for ascending order and an event-driven
 * processing layer to show how heap operations can be integrated into a
 * larger Node.js workflow.
 */

const { performance } = require("node:perf_hooks");
const { EventEmitter } = require("node:events");

class HeapSortError extends Error {
  constructor(message) {
    super(message);
    this.name = "HeapSortError";
  }
}

class HeapSorter {
  constructor({ descending = false, maxInputSize = 1_000_000 } = {}) {
    this.descending = descending;
    this.maxInputSize = maxInputSize;
    this.comparisons = 0;
    this.swaps = 0;
  }

  validate(values) {
    if (!Array.isArray(values)) {
      throw new HeapSortError("Input must be an array.");
    }

    if (values.length > this.maxInputSize) {
      throw new HeapSortError(
        `Input exceeds ${this.maxInputSize.toLocaleString()} elements.`
      );
    }

    for (const value of values) {
      if (!Number.isSafeInteger(value)) {
        throw new HeapSortError(
          "Every element must be a JavaScript safe integer."
        );
      }
    }
  }

  compare(a, b) {
    this.comparisons++;
    return a > b ? 1 : a < b ? -1 : 0;
  }

  swap(values, i, j) {
    [values[i], values[j]] = [values[j], values[i]];
    this.swaps++;
  }

  siftDown(values, root, size, maxHeap) {
    while (true) {
      const left = root * 2 + 1;
      const right = left + 1;
      let candidate = root;

      if (
        left < size &&
        (maxHeap
          ? this.compare(values[left], values[candidate]) > 0
          : this.compare(values[left], values[candidate]) < 0)
      ) {
        candidate = left;
      }

      if (
        right < size &&
        (maxHeap
          ? this.compare(values[right], values[candidate]) > 0
          : this.compare(values[right], values[candidate]) < 0)
      ) {
        candidate = right;
      }

      if (candidate === root) {
        return;
      }

      this.swap(values, root, candidate);
      root = candidate;
    }
  }

  sort(values) {
    this.validate(values);

    this.comparisons = 0;
    this.swaps = 0;

    const result = [...values];
    const started = performance.now();

    if (result.length < 2) {
      return {
        values: result,
        comparisons: 0,
        swaps: 0,
        elapsedMs: performance.now() - started,
      };
    }

    // For ascending order, a max-heap moves the largest item to the end.
    // For descending order, a min-heap moves the smallest item to the end.
    const maxHeap = !this.descending;

    for (let root = Math.floor(result.length / 2) - 1; root >= 0; root--) {
      this.siftDown(result, root, result.length, maxHeap);
    }

    for (let end = result.length - 1; end > 0; end--) {
      this.swap(result, 0, end);
      this.siftDown(result, 0, end, maxHeap);
    }

    return {
      values: result,
      comparisons: this.comparisons,
      swaps: this.swaps,
      elapsedMs: performance.now() - started,
    };
  }
}

function mergeSort(values) {
  if (values.length <= 1) {
    return [...values];
  }

  const middle = Math.floor(values.length / 2);
  const left = mergeSort(values.slice(0, middle));
  const right = mergeSort(values.slice(middle));

  const result = [];
  let i = 0;
  let j = 0;

  while (i < left.length && j < right.length) {
    if (left[i] <= right[j]) {
      result.push(left[i++]);
    } else {
      result.push(right[j++]);
    }
  }

  return result.concat(left.slice(i), right.slice(j));
}

function quickSort(values) {
  const result = [...values];

  function sort(left, right) {
    if (left >= right) {
      return;
    }

    const pivot = result[Math.floor((left + right) / 2)];
    let i = left;
    let j = right;

    while (i <= j) {
      while (result[i] < pivot) i++;
      while (result[j] > pivot) j--;

      if (i <= j) {
        [result[i], result[j]] = [result[j], result[i]];
        i++;
        j--;
      }
    }

    if (left < j) sort(left, j);
    if (i < right) sort(i, right);
  }

  sort(0, result.length - 1);
  return result;
}

class SortJobQueue extends EventEmitter {
  constructor() {
    super();
    this.queue = [];
    this.processing = false;
  }

  enqueue(job) {
    if (!job || !Array.isArray(job.values)) {
      throw new HeapSortError("A sort job requires an array of values.");
    }

    this.queue.push(job);
    this.emit("queued", job.id);
  }

  async process() {
    if (this.processing) {
      return;
    }

    this.processing = true;

    try {
      while (this.queue.length > 0) {
        const job = this.queue.shift();

        try {
          const sorter = new HeapSorter(job.options);
          const result = sorter.sort(job.values);

          this.emit("completed", {
            id: job.id,
            result,
          });

          await Promise.resolve();
        } catch (error) {
          this.emit("failed", {
            id: job.id,
            error,
          });
        }
      }
    } finally {
      this.processing = false;
    }
  }
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function runTests() {
  const cases = [
    [],
    [1],
    [2, 1],
    [7, 7, 7],
    [-3, 9, 0, -3, 4, 2],
    [Number.MAX_SAFE_INTEGER, 0, Number.MIN_SAFE_INTEGER],
  ];

  for (const input of cases) {
    const expected = [...input].sort((a, b) => a - b);
    const result = new HeapSorter().sort(input).values;
    assert(
      JSON.stringify(result) === JSON.stringify(expected),
      `Ascending test failed: ${input}`
    );

    const descending = new HeapSorter({ descending: true }).sort(input).values;
    const expectedDescending = [...expected].reverse();

    assert(
      JSON.stringify(descending) === JSON.stringify(expectedDescending),
      `Descending test failed: ${input}`
    );
  }

  const random = [];
  let seed = 20261029;

  for (let i = 0; i < 1000; i++) {
    seed = (seed * 1664525 + 1013904223) >>> 0;
    random.push((seed % 2001) - 1000);
  }

  const heapResult = new HeapSorter().sort(random).values;
  const expected = [...random].sort((a, b) => a - b);

  assert(
    JSON.stringify(heapResult) === JSON.stringify(expected),
    "Randomized heap-sort test failed."
  );

  assert(
    JSON.stringify(mergeSort(random)) === JSON.stringify(expected),
    "Merge-sort comparison failed."
  );

  assert(
    JSON.stringify(quickSort(random)) === JSON.stringify(expected),
    "Quick-sort comparison failed."
  );

  try {
    new HeapSorter().sort([1, 2, 1.5]);
  } catch (error) {
    assert(error instanceof HeapSortError, "Wrong validation error type.");
  }

  console.log("All JavaScript heap-sort tests passed.");
}

async function main() {
  runTests();

  const sample = [12, 7, 3, 19, 4, 7, -2, 15, 0, 9];
  const heap = new HeapSorter();
  const heapResult = heap.sort(sample);

  console.log("\nHeap Sort");
  console.log("Sorted:", heapResult.values);
  console.log("Comparisons:", heapResult.comparisons);
  console.log("Swaps:", heapResult.swaps);
  console.log("Elapsed ms:", heapResult.elapsedMs.toFixed(4));

  console.log("\nComparison");
  console.log("Merge Sort:", mergeSort(sample));
  console.log("Quick Sort:", quickSort(sample));

  const queue = new SortJobQueue();

  queue.on("queued", (id) => console.log(`Job ${id} queued.`));
  queue.on("completed", ({ id, result }) => {
    console.log(`Job ${id} completed:`, result.values);
  });
  queue.on("failed", ({ id, error }) => {
    console.error(`Job ${id} failed: ${error.message}`);
  });

  queue.enqueue({
    id: "batch-001",
    values: [42, 8, 16, 4, 23, 15, 8],
    options: {},
  });

  queue.enqueue({
    id: "batch-002",
    values: [5, -1, 9, 0, -8],
    options: { descending: true },
  });

  await queue.process();
}

main().catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});
