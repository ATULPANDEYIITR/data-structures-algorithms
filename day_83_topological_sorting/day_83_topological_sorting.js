'use strict';

/*
 * Topological Sorting and Asynchronous Dependency Scheduling
 *
 * Implements:
 * - Directed Acyclic Graphs
 * - Adjacency maps and indegree tracking
 * - Kahn's algorithm
 * - DFS cycle detection
 * - Dependency-aware asynchronous execution
 * - Concurrent execution of independent tasks
 * - Failure propagation
 * - Event-driven task lifecycle
 * - Execution cancellation after failure
 *
 * Runtime: Node.js 18+
 * External dependencies: None
 */

const { EventEmitter } = require('node:events');

class GraphError extends Error {
    constructor(message) {
        super(message);
        this.name = 'GraphError';
    }
}

class CycleError extends GraphError {
    constructor(message, cycle = []) {
        super(message);
        this.name = 'CycleError';
        this.cycle = cycle;
    }
}

class DependencyGraph {
    constructor() {
        this.adjacency = new Map();
        this.reverse = new Map();
    }

    addNode(id) {
        if (typeof id !== 'string' || id.trim() === '') {
            throw new TypeError('Node ID must be a nonempty string.');
        }

        if (!this.adjacency.has(id)) {
            this.adjacency.set(id, new Set());
            this.reverse.set(id, new Set());
        }
    }

    addDependency(prerequisite, dependent) {
        if (!this.adjacency.has(prerequisite)) {
            throw new GraphError(
                `Unknown prerequisite: ${prerequisite}`
            );
        }

        if (!this.adjacency.has(dependent)) {
            throw new GraphError(
                `Unknown dependent: ${dependent}`
            );
        }

        if (prerequisite === dependent) {
            throw new CycleError(
                `Self-dependency: ${prerequisite}`,
                [prerequisite, prerequisite]
            );
        }

        this.adjacency.get(prerequisite).add(dependent);
        this.reverse.get(dependent).add(prerequisite);
    }

    getNodeCount() {
        return this.adjacency.size;
    }

    getEdgeCount() {
        let count = 0;

        for (const neighbors of this.adjacency.values()) {
            count += neighbors.size;
        }

        return count;
    }

    getPrerequisites(id) {
        if (!this.reverse.has(id)) {
            throw new GraphError(`Unknown node: ${id}`);
        }

        return [...this.reverse.get(id)];
    }

    topologicalSort() {
        const indegree = new Map();

        for (const node of this.adjacency.keys()) {
            indegree.set(
                node,
                this.reverse.get(node).size
            );
        }

        const ready = [];

        for (const [node, degree] of indegree) {
            if (degree === 0) {
                ready.push(node);
            }
        }

        // Deterministic selection among initially ready nodes.
        ready.sort();

        const ordering = [];

        while (ready.length > 0) {
            const node = ready.shift();
            ordering.push(node);

            for (const neighbor of this.adjacency.get(node)) {
                const remaining = indegree.get(neighbor) - 1;
                indegree.set(neighbor, remaining);

                if (remaining === 0) {
                    ready.push(neighbor);
                }
            }
        }

        if (ordering.length !== this.adjacency.size) {
            const unresolved = [...indegree]
                .filter(([, degree]) => degree > 0)
                .map(([node]) => node);

            throw new CycleError(
                `Circular dependencies: ${unresolved.join(', ')}`,
                unresolved
            );
        }

        return ordering;
    }

    depthFirstSort() {
        const state = new Map();
        const result = [];
        const path = [];

        const WHITE = 0;
        const GRAY = 1;
        const BLACK = 2;

        for (const node of this.adjacency.keys()) {
            state.set(node, WHITE);
        }

        const visit = (node) => {
            state.set(node, GRAY);
            path.push(node);

            for (const neighbor of this.adjacency.get(node)) {
                if (state.get(neighbor) === GRAY) {
                    const index = path.indexOf(neighbor);
                    const cycle = [
                        ...path.slice(index),
                        neighbor
                    ];

                    throw new CycleError(
                        `Cycle: ${cycle.join(' -> ')}`,
                        cycle
                    );
                }

                if (state.get(neighbor) === WHITE) {
                    visit(neighbor);
                }
            }

            path.pop();
            state.set(node, BLACK);
            result.push(node);
        };

        for (const node of [...this.adjacency.keys()].sort()) {
            if (state.get(node) === WHITE) {
                visit(node);
            }
        }

        return result.reverse();
    }

    getLevels() {
        const order = this.topologicalSort();
        const levels = new Map();

        for (const node of this.adjacency.keys()) {
            levels.set(node, 0);
        }

        for (const node of order) {
            for (const dependent of this.adjacency.get(node)) {
                levels.set(
                    dependent,
                    Math.max(
                        levels.get(dependent),
                        levels.get(node) + 1
                    )
                );
            }
        }

        return levels;
    }
}

class Task {
    constructor(id, action, dependencies = []) {
        if (typeof id !== 'string' || !id.trim()) {
            throw new TypeError('Invalid task ID.');
        }

        if (typeof action !== 'function') {
            throw new TypeError('Task action must be a function.');
        }

        this.id = id;
        this.action = action;
        this.dependencies = [...dependencies];
        this.status = 'pending';
        this.result = undefined;
        this.error = undefined;
    }
}

class DependencyScheduler extends EventEmitter {
    constructor(maxConcurrency = 3) {
        super();

        if (
            !Number.isInteger(maxConcurrency) ||
            maxConcurrency < 1
        ) {
            throw new RangeError(
                'Concurrency must be a positive integer.'
            );
        }

        this.maxConcurrency = maxConcurrency;
        this.tasks = new Map();
        this.graph = new DependencyGraph();
    }

    register(task) {
        if (!(task instanceof Task)) {
            throw new TypeError('Expected a Task instance.');
        }

        if (this.tasks.has(task.id)) {
            throw new GraphError(
                `Duplicate task: ${task.id}`
            );
        }

        this.graph.addNode(task.id);
        this.tasks.set(task.id, task);
    }

    addDependency(prerequisite, dependent) {
        if (
            !this.tasks.has(prerequisite) ||
            !this.tasks.has(dependent)
        ) {
            throw new GraphError(
                'Both dependency tasks must be registered.'
            );
        }

        this.graph.addDependency(prerequisite, dependent);

        const task = this.tasks.get(dependent);

        if (!task.dependencies.includes(prerequisite)) {
            task.dependencies.push(prerequisite);
        }
    }

    async execute() {
        // Validate the complete graph before starting side effects.
        const ordering = this.graph.topologicalSort();

        const completed = new Set();
        const running = new Map();
        const failed = new Set();

        const executeTask = async (task) => {
            task.status = 'running';
            this.emit('taskStarted', task.id);

            try {
                const result = await task.action({
                    taskId: task.id,
                    dependencies: task.dependencies.map(
                        id => this.tasks.get(id).result
                    )
                });

                task.result = result;
                task.status = 'completed';
                completed.add(task.id);

                this.emit('taskCompleted', {
                    taskId: task.id,
                    result
                });

            } catch (error) {
                task.error = error;
                task.status = 'failed';
                failed.add(task.id);

                this.emit('taskFailed', {
                    taskId: task.id,
                    error
                });
            }
        };

        try {
            while (completed.size + failed.size < ordering.length) {
                let launched = false;

                for (const id of ordering) {
                    if (running.size >= this.maxConcurrency) {
                        break;
                    }

                    const task = this.tasks.get(id);

                    if (task.status !== 'pending') {
                        continue;
                    }

                    const prerequisites = task.dependencies;

                    if (prerequisites.some(id => failed.has(id))) {
                        task.status = 'blocked';
                        failed.add(task.id);

                        this.emit('taskBlocked', task.id);
                        launched = true;
                        continue;
                    }

                    if (
                        prerequisites.every(id => completed.has(id))
                    ) {
                        const promise = executeTask(task).then(() => {
                            running.delete(id);
                        });

                        running.set(id, promise);
                        launched = true;
                    }
                }

                if (running.size > 0) {
                    await Promise.race(running.values());
                    continue;
                }

                if (!launched) {
                    break;
                }
            }

            await Promise.all(running.values());

            const blocked = ordering.filter(
                id => this.tasks.get(id).status === 'blocked'
            );

            const successful = [...completed];

            const report = {
                ordering,
                completed: successful,
                failed: [...failed],
                blocked,
                success: failed.size === 0
            };

            this.emit('executionFinished', report);

            return report;

        } catch (error) {
            this.emit('schedulerError', error);
            throw error;
        }
    }
}

function createBuildPipeline() {
    const scheduler = new DependencyScheduler(3);

    const actions = {
        source: async () => {
            await Promise.resolve();
            return 'Source retrieved';
        },

        validate: async () => {
            return 'Source validated';
        },

        compile: async () => {
            return 'Application compiled';
        },

        unit: async () => {
            return 'Unit tests passed';
        },

        security: async () => {
            return 'Security checks passed';
        },

        package: async () => {
            return 'Package generated';
        },

        integration: async () => {
            return 'Integration tests passed';
        },

        deploy: async () => {
            return 'Application deployed';
        }
    };

    for (const [id, action] of Object.entries(actions)) {
        scheduler.register(new Task(id, action));
    }

    const edges = [
        ['source', 'validate'],
        ['validate', 'compile'],
        ['compile', 'unit'],
        ['compile', 'security'],
        ['unit', 'package'],
        ['security', 'package'],
        ['package', 'integration'],
        ['integration', 'deploy']
    ];

    for (const [prerequisite, dependent] of edges) {
        scheduler.addDependency(prerequisite, dependent);
    }

    return scheduler;
}

async function demonstrateFailureHandling() {
    const scheduler = new DependencyScheduler(2);

    scheduler.register(
        new Task('fetch', async () => 'Fetched')
    );

    scheduler.register(
        new Task('test', async () => {
            throw new Error('Test suite failed');
        })
    );

    scheduler.register(
        new Task('release', async () => 'Released')
    );

    scheduler.addDependency('fetch', 'test');
    scheduler.addDependency('test', 'release');

    const report = await scheduler.execute();

    console.log('\nFailure simulation:');
    console.log(report);

    if (
        scheduler.tasks.get('release').status !== 'blocked'
    ) {
        throw new Error('Failure propagation test failed.');
    }
}

async function main() {
    console.log('TOPOLOGICAL SORTING AND ASYNC SCHEDULING');
    console.log('='.repeat(55));

    const scheduler = createBuildPipeline();

    scheduler.on('taskStarted', id => {
        console.log(`[STARTED] ${id}`);
    });

    scheduler.on('taskCompleted', event => {
        console.log(`[COMPLETED] ${event.taskId}`);
    });

    scheduler.on('taskFailed', event => {
        console.log(
            `[FAILED] ${event.taskId}: ${event.error.message}`
        );
    });

    scheduler.on('taskBlocked', id => {
        console.log(`[BLOCKED] ${id}`);
    });

    const graph = scheduler.graph;

    console.log('\nVertices:', graph.getNodeCount());
    console.log('Edges:', graph.getEdgeCount());

    console.log(
        '\nKahn ordering:',
        graph.topologicalSort().join(' -> ')
    );

    console.log(
        '\nDFS ordering:',
        graph.depthFirstSort().join(' -> ')
    );

    console.log('\nExecution levels:');

    for (const [id, level] of graph.getLevels()) {
        console.log(`${id}: ${level}`);
    }

    const report = await scheduler.execute();

    console.log('\nExecution report:');
    console.log(JSON.stringify(report, null, 2));

    if (!report.success) {
        throw new Error('Build pipeline did not complete.');
    }

    await demonstrateFailureHandling();

    const cyclic = new DependencyGraph();

    cyclic.addNode('A');
    cyclic.addNode('B');
    cyclic.addNode('C');

    cyclic.addDependency('A', 'B');
    cyclic.addDependency('B', 'C');
    cyclic.addDependency('C', 'A');

    try {
        cyclic.topologicalSort();
    } catch (error) {
        if (!(error instanceof CycleError)) {
            throw error;
        }

        console.log('\nCycle correctly detected:', error.message);
    }

    console.log('\nAll scheduling demonstrations completed.');
}

main().catch(error => {
    console.error('Fatal execution error:', error);
    process.exitCode = 1;
});
