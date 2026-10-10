"use strict";

/*
 * Monotonic stacks in JavaScript.
 *
 * The examples use index stacks rather than value stacks when the answer
 * depends on distance, position, or a range. This is the common pattern
 * behind next greater/smaller problems and histogram rectangles.
 */

function buildIncreasingStack(values) {
    const stack = [];

    for (const value of values) {
        while (stack.length > 0 && stack[stack.length - 1] > value) {
            stack.pop();
        }
        stack.push(value);
    }

    return stack;
}

function buildDecreasingStack(values) {
    const stack = [];

    for (const value of values) {
        while (stack.length > 0 && stack[stack.length - 1] < value) {
            stack.pop();
        }
        stack.push(value);
    }

    return stack;
}

function nextGreaterRight(values) {
    const answer = new Array(values.length).fill(-1);
    const unresolved = [];

    for (let i = 0; i < values.length; i += 1) {
        while (
            unresolved.length > 0 &&
            values[unresolved[unresolved.length - 1]] < values[i]
        ) {
            const index = unresolved.pop();
            answer[index] = values[i];
        }

        unresolved.push(i);
    }

    return answer;
}

function nextSmallerRight(values) {
    const answer = new Array(values.length).fill(-1);
    const unresolved = [];

    for (let i = 0; i < values.length; i += 1) {
        while (
            unresolved.length > 0 &&
            values[unresolved[unresolved.length - 1]] > values[i]
        ) {
            const index = unresolved.pop();
            answer[index] = values[i];
        }

        unresolved.push(i);
    }

    return answer;
}

function dailyTemperatures(temperatures) {
    const waits = new Array(temperatures.length).fill(0);
    const unresolvedDays = [];

    for (let day = 0; day < temperatures.length; day += 1) {
        while (
            unresolvedDays.length > 0 &&
            temperatures[unresolvedDays[unresolvedDays.length - 1]] <
                temperatures[day]
        ) {
            const previousDay = unresolvedDays.pop();
            waits[previousDay] = day - previousDay;
        }

        unresolvedDays.push(day);
    }

    return waits;
}

function largestHistogramRectangle(heights) {
    if (!Array.isArray(heights) || heights.some((height) => !Number.isFinite(height) || height < 0)) {
        throw new TypeError("Histogram heights must be finite non-negative numbers.");
    }

    const stack = [];
    const extended = [...heights, 0];
    let bestArea = 0;
    let bestRange = [-1, -1];

    for (let rightBoundary = 0; rightBoundary < extended.length; rightBoundary += 1) {
        while (
            stack.length > 0 &&
            extended[stack[stack.length - 1]] > extended[rightBoundary]
        ) {
            const top = stack.pop();
            const height = extended[top];
            const leftBoundary =
                stack.length === 0 ? 0 : stack[stack.length - 1] + 1;
            const right = rightBoundary - 1;
            const width = right - leftBoundary + 1;
            const area = height * width;

            if (area > bestArea) {
                bestArea = area;
                bestRange = [leftBoundary, right];
            }
        }

        stack.push(rightBoundary);
    }

    return { area: bestArea, range: bestRange };
}

function nextGreaterCircular(values) {
    const answer = new Array(values.length).fill(-1);
    const stack = [];

    /*
     * Processing two logical copies gives elements a chance to find a
     * greater value after the physical end of the array.
     */
    for (let i = 0; i < values.length * 2; i += 1) {
        const index = i % values.length;

        while (
            stack.length > 0 &&
            values[stack[stack.length - 1]] < values[index]
        ) {
            answer[stack.pop()] = values[index];
        }

        if (i < values.length) {
            stack.push(index);
        }
    }

    return answer;
}

function sumSubarrayMinimums(values) {
    const n = values.length;
    const previousLess = new Array(n).fill(-1);
    const nextLessOrEqual = new Array(n).fill(n);
    const stack = [];

    for (let i = 0; i < n; i += 1) {
        while (stack.length > 0 && values[stack[stack.length - 1]] > values[i]) {
            stack.pop();
        }

        if (stack.length > 0) {
            previousLess[i] = stack[stack.length - 1];
        }

        stack.push(i);
    }

    stack.length = 0;

    for (let i = n - 1; i >= 0; i -= 1) {
        while (stack.length > 0 && values[stack[stack.length - 1]] >= values[i]) {
            stack.pop();
        }

        if (stack.length > 0) {
            nextLessOrEqual[i] = stack[stack.length - 1];
        }

        stack.push(i);
    }

    let total = 0;

    for (let i = 0; i < n; i += 1) {
        const leftChoices = i - previousLess[i];
        const rightChoices = nextLessOrEqual[i] - i;
        total += values[i] * leftChoices * rightChoices;
    }

    return total;
}

class PullRequestMetrics {
    constructor(latencies) {
        this.latencies = [...latencies];
    }

    largestStableWindow() {
        /*
         * This domain example treats each latency measurement as a bar.
         * A rectangle represents a contiguous period whose minimum latency
         * threshold is sustained across the entire period.
         */
        return largestHistogramRectangleForMetrics(this.latencies);
    }
}

function largestHistogramRectangleForMetrics(values) {
    if (values.length === 0) {
        return { area: 0, range: [-1, -1] };
    }

    return largestHistogramRectangle(values);
}

function run() {
    const values = [2, 1, 2, 4, 3];

    console.log("Increasing stack:", buildIncreasingStack(values));
    console.log("Decreasing stack:", buildDecreasingStack(values));

    console.log("Next greater:", nextGreaterRight(values));
    console.log("Next smaller:", nextSmallerRight(values));

    const temperatures = [73, 74, 75, 71, 69, 72, 76, 73];
    console.log("Daily temperatures:", dailyTemperatures(temperatures));

    const histogram = [2, 1, 5, 6, 2, 3];
    console.log("Histogram:", largestHistogramRectangle(histogram));

    console.log(
        "Circular next greater:",
        nextGreaterCircular([1, 2, 1])
    );

    console.log(
        "Sum of subarray minimums:",
        sumSubarrayMinimums([3, 1, 2, 4])
    );

    const metrics = new PullRequestMetrics([4, 4, 3, 3, 3, 5, 5, 2]);
    console.log("Contiguous metric window:", metrics.largestStableWindow());

    console.log("Empty histogram:", largestHistogramRectangle([]));

    try {
        largestHistogramRectangle([2, -1, 4]);
    } catch (error) {
        console.error("Validation:", error.message);
    }
}

run();
