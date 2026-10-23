'use strict';

/*
 * Binary Search on Answer
 *
 * The searched value is not an array index. It is a candidate answer.
 * Each feasibility function must be monotonic so that the search can
 * discard half of the remaining answer space after every evaluation.
 */

class ValidationError extends Error {
    constructor(message) {
        super(message);
        this.name = 'ValidationError';
    }
}

function validatePositiveIntegers(values, name) {
    if (!Array.isArray(values) || values.length === 0) {
        throw new ValidationError(`${name} must be a non-empty array`);
    }

    if (
        values.some(
            value =>
                !Number.isSafeInteger(value) ||
                value <= 0
        )
    ) {
        throw new ValidationError(
            `${name} must contain positive safe integers`
        );
    }

    return [...values];
}

function firstTrue(low, high, feasible) {
    let answer = null;

    while (low <= high) {
        const mid = low + Math.floor((high - low) / 2);

        if (feasible(mid)) {
            answer = mid;
            high = mid - 1;
        } else {
            low = mid + 1;
        }
    }

    return answer;
}

function lastTrue(low, high, feasible) {
    let answer = null;

    while (low <= high) {
        const mid = low + Math.floor((high - low) / 2);

        if (feasible(mid)) {
            answer = mid;
            low = mid + 1;
        } else {
            high = mid - 1;
        }
    }

    return answer;
}

function minimumShippingCapacity(weights, days) {
    weights = validatePositiveIntegers(weights, 'weights');

    if (!Number.isSafeInteger(days) || days <= 0) {
        throw new ValidationError('days must be a positive integer');
    }

    days = Math.min(days, weights.length);

    const lowerBound = Math.max(...weights);
    const upperBound = weights.reduce((a, b) => a + b, 0);

    function feasible(capacity) {
        let usedDays = 1;
        let load = 0;

        for (const weight of weights) {
            if (weight > capacity) {
                return false;
            }

            if (load + weight <= capacity) {
                load += weight;
            } else {
                usedDays++;
                load = weight;

                if (usedDays > days) {
                    return false;
                }
            }
        }

        return true;
    }

    return firstTrue(lowerBound, upperBound, feasible);
}

function minimumEatingSpeed(piles, hours) {
    piles = validatePositiveIntegers(piles, 'piles');

    if (!Number.isSafeInteger(hours) || hours <= 0) {
        throw new ValidationError('hours must be a positive integer');
    }

    const upperBound = Math.max(...piles);

    function feasible(speed) {
        let requiredHours = 0;

        for (const pile of piles) {
            requiredHours += Math.ceil(pile / speed);

            if (requiredHours > hours) {
                return false;
            }
        }

        return true;
    }

    return firstTrue(1, upperBound, feasible);
}

function maximizeMinimumDistance(stalls, cows) {
    stalls = validatePositiveIntegers(stalls, 'stalls');

    if (!Number.isSafeInteger(cows) || cows < 2 || cows > stalls.length) {
        throw new ValidationError(
            'cows must be between 2 and the number of stalls'
        );
    }

    stalls.sort((a, b) => a - b);

    function feasible(distance) {
        let placed = 1;
        let lastPosition = stalls[0];

        for (let i = 1; i < stalls.length; i++) {
            if (stalls[i] - lastPosition >= distance) {
                placed++;
                lastPosition = stalls[i];

                if (placed >= cows) {
                    return true;
                }
            }
        }

        return false;
    }

    return lastTrue(
        0,
        stalls[stalls.length - 1] - stalls[0],
        feasible
    );
}

function minimizeLargestPartition(numbers, parts) {
    numbers = validatePositiveIntegers(numbers, 'numbers');

    if (!Number.isSafeInteger(parts) || parts <= 0) {
        throw new ValidationError('parts must be positive');
    }

    parts = Math.min(parts, numbers.length);

    function feasible(limit) {
        let groups = 1;
        let current = 0;

        for (const value of numbers) {
            if (value > limit) {
                return false;
            }

            if (current + value <= limit) {
                current += value;
            } else {
                groups++;
                current = value;

                if (groups > parts) {
                    return false;
                }
            }
        }

        return true;
    }

    return firstTrue(
        Math.max(...numbers),
        numbers.reduce((a, b) => a + b, 0),
        feasible
    );
}

class RepositoryCapacityPlanner {
    constructor(jobs, workerCount) {
        this.jobs = validatePositiveIntegers(jobs, 'jobs');

        if (
            !Number.isSafeInteger(workerCount) ||
            workerCount <= 0 ||
            workerCount > jobs.length
        ) {
            throw new ValidationError(
                'workerCount must be within the number of jobs'
            );
        }

        this.workerCount = workerCount;
    }

    /*
     * Find the smallest processing capacity allowing all jobs to be
     * completed by the available workers. Jobs remain in input order.
     */
    minimumCapacity() {
        const total = this.jobs.reduce((a, b) => a + b, 0);
        const lower = Math.max(...this.jobs);

        return firstTrue(lower, total, capacity => {
            let workers = 1;
            let currentLoad = 0;

            for (const job of this.jobs) {
                if (job > capacity) {
                    return false;
                }

                if (currentLoad + job <= capacity) {
                    currentLoad += job;
                } else {
                    workers++;
                    currentLoad = job;

                    if (workers > this.workerCount) {
                        return false;
                    }
                }
            }

            return true;
        });
    }
}

function main() {
    console.log(
        'Shipping capacity:',
        minimumShippingCapacity([1, 2, 3, 1, 1, 1, 1], 4)
    );

    console.log(
        'Minimum eating speed:',
        minimumEatingSpeed([3, 6, 7, 11], 8)
    );

    console.log(
        'Maximum minimum distance:',
        maximizeMinimumDistance([1, 2, 4, 8, 9], 3)
    );

    console.log(
        'Minimum largest partition:',
        minimizeLargestPartition([7, 2, 5, 10, 8], 2)
    );

    const planner = new RepositoryCapacityPlanner(
        [11, 7, 5, 9, 13, 6],
        3
    );

    console.log('Worker capacity:', planner.minimumCapacity());

    console.assert(
        minimumShippingCapacity([5], 1) === 5
    );
    console.assert(
        minimumEatingSpeed([1], 1) === 1
    );
    console.assert(
        maximizeMinimumDistance([1, 2], 2) === 1
    );
    console.assert(
        minimizeLargestPartition([10, 20], 1) === 30
    );
    console.assert(
        planner.minimumCapacity() === 20
    );

    try {
        minimumEatingSpeed([], 3);
        throw new Error('Expected validation failure');
    } catch (error) {
        if (!(error instanceof ValidationError)) {
            throw error;
        }
    }
}

main();
