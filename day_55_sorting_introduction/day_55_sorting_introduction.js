"use strict";

/*
 * Sorting laboratory:
 * - stable insertion sort
 * - stable merge sort
 * - in-place three-way quicksort
 * - operation counts and correctness checks
 */

const assert = require("node:assert/strict");

function validateArray(values, key) {
  if (!Array.isArray(values)) {
    throw new TypeError("Expected an array.");
  }
  if (typeof key !== "function") {
    throw new TypeError("Expected a key function.");
  }
  for (const value of values) {
    const result = key(value);
    if (typeof result !== "number" || !Number.isFinite(result)) {
      throw new TypeError("Every sorting key must be a finite number.");
    }
  }
}

function insertionSort(values, key = value => value) {
  validateArray(values, key);
  let comparisons = 0;
  let writes = 0;

  for (let i = 1; i < values.length; i++) {
    const current = values[i];
    const currentKey = key(current);
    let j = i - 1;

    while (j >= 0) {
      comparisons++;
      if (key(values[j]) <= currentKey) break;
      values[j + 1] = values[j];
      writes++;
      j--;
    }

    values[j + 1] = current;
    writes++;
  }

  return {
    algorithm: "insertionSort",
    values,
    stable: true,
    inPlace: true,
    comparisons,
    writes
  };
}

function mergeSort(values, key = value => value) {
  validateArray(values, key);
  let comparisons = 0;
  let writes = 0;

  function merge(left, right) {
    const output = [];
    let i = 0;
    let j = 0;

    while (i < left.length && j < right.length) {
      comparisons++;
      // Select from the left on equality to preserve input order.
      if (key(left[i]) <= key(right[j])) {
        output.push(left[i++]);
      } else {
        output.push(right[j++]);
      }
      writes++;
    }

    while (i < left.length) {
      output.push(left[i++]);
      writes++;
    }
    while (j < right.length) {
      output.push(right[j++]);
      writes++;
    }
    return output;
  }

  function sort(part) {
    if (part.length < 2) return part;
    const middle = Math.floor(part.length / 2);
    return merge(sort(part.slice(0, middle)), sort(part.slice(middle)));
  }

  return {
    algorithm: "mergeSort",
    values: sort(values.slice()),
    stable: true,
    inPlace: false,
    comparisons,
    writes
  };
}

function quickSort(values, key = value => value) {
  validateArray(values, key);
  let comparisons = 0;
  let writes = 0;

  function sort(low, high) {
    while (low < high) {
      const pivot = key(values[Math.floor((low + high) / 2)]);
      let less = low;
      let current = low;
      let greater = high;

      while (current <= greater) {
        const currentKey = key(values[current]);
        comparisons++;

        if (currentKey < pivot) {
          [values[less], values[current]] = [values[current], values[less]];
          writes += 2;
          less++;
          current++;
        } else {
          comparisons++;
          if (currentKey > pivot) {
            [values[current], values[greater]] = [values[greater], values[current]];
            writes += 2;
            greater--;
          } else {
            current++;
          }
        }
      }

      // Recurse only into the smaller partition to reduce stack usage.
      if (less - low < high - greater) {
        sort(low, less - 1);
        low = greater + 1;
      } else {
        sort(greater + 1, high);
        high = less - 1;
      }
    }
  }

  sort(0, values.length - 1);
  return {
    algorithm: "quickSort",
    values,
    stable: false,
    inPlace: true,
    comparisons,
    writes
  };
}

function isSorted(values, key = value => value) {
  for (let i = 1; i < values.length; i++) {
    if (key(values[i - 1]) > key(values[i])) return false;
  }
  return true;
}

function isStable(original, sorted, key) {
  const originalPosition = new Map(
    original.map((item, index) => [item, index])
  );

  for (let i = 1; i < sorted.length; i++) {
    if (
      key(sorted[i - 1]) === key(sorted[i]) &&
      originalPosition.get(sorted[i - 1]) > originalPosition.get(sorted[i])
    ) {
      return false;
    }
  }
  return true;
}

async function sortBatch(samples, algorithm) {
  // Promise-based orchestration allows callers to compose batches asynchronously.
  return Promise.all(samples.map(async sample => algorithm(sample.slice())));
}

async function main() {
  const samples = [
    [],
    [1],
    [5, 2, 4, 1, 3],
    [4, 4, 4, 4],
    [9, -2, 0, 7, -2]
  ];

  for (const sample of samples) {
    const expected = sample.slice().sort((a, b) => a - b);
    const results = [
      insertionSort(sample.slice()),
      mergeSort(sample),
      quickSort(sample.slice())
    ];

    for (const result of results) {
      assert.deepEqual(result.values, expected);
      assert.equal(isSorted(result.values), true);
    }

    console.log(sample, "=>", expected);
    console.table(results.map(({ algorithm, stable, inPlace, comparisons, writes }) => ({
      algorithm, stable, inPlace, comparisons, writes
    })));
  }

  const students = [
    { name: "Asha", score: 90, order: 1 },
    { name: "Ravi", score: 75, order: 2 },
    { name: "Meera", score: 90, order: 3 },
    { name: "Kabir", score: 75, order: 4 },
    { name: "Isha", score: 90, order: 5 }
  ];

  const insertion = insertionSort(students.slice(), student => student.score);
  const merged = mergeSort(students, student => student.score);
  const quick = quickSort(students.slice(), student => student.score);

  assert.equal(isStable(students, insertion.values, student => student.score), true);
  assert.equal(isStable(students, merged.values, student => student.score), true);
  assert.equal(isSorted(quick.values, student => student.score), true);

  console.log("\nStable insertion sort:", insertion.values);
  console.log("Stable merge sort:", merged.values);
  console.log("Quicksort:", quick.values);

  const generated = Array.from({ length: 200 }, (_, i) =>
    ((i * 73) % 101) - 50
  );
  const expected = generated.slice().sort((a, b) => a - b);
  const batch = await sortBatch(
    [generated, generated, generated],
    async values => mergeSort(values)
  );

  for (const result of batch) {
    assert.deepEqual(result.values, expected);
  }

  assert.throws(() => insertionSort([1, NaN, 3]), TypeError);
  assert.throws(() => mergeSort("not an array"), TypeError);

  console.log("\nAll assertions passed.");
}

main().catch(error => {
  console.error("Sorting experiment failed:", error.message);
  process.exitCode = 1;
});
