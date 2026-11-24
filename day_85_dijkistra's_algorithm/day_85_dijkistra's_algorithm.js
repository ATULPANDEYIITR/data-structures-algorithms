'use strict';

/*
 * Dijkstra's Algorithm
 * Event-driven transport routing and shortest-path evaluation.
 *
 * Runtime: Node.js 18+
 * Dependencies: None
 */

const assert = require('node:assert/strict');
const { EventEmitter } = require('node:events');

class MinPriorityQueue {
    constructor() {
        this.heap = [];
        this.sequence = 0;
    }

    get size() {
        return this.heap.length;
    }

    less(a, b) {
        if (a.priority !== b.priority) {
            return a.priority < b.priority;
        }
        return a.sequence < b.sequence;
    }

    push(value, priority) {
        if (!Number.isFinite(priority) || priority < 0) {
            throw new RangeError('Priority must be finite and non-negative');
        }

        const entry = {
            value,
            priority,
            sequence: this.sequence++
        };

        this.heap.push(entry);
        this.bubbleUp(this.heap.length - 1);
    }

    bubbleUp(index) {
        while (index > 0) {
            const parent = Math.floor((index - 1) / 2);

            if (!this.less(this.heap[index], this.heap[parent])) {
                break;
            }

            [this.heap[index], this.heap[parent]] =
                [this.heap[parent], this.heap[index]];

            index = parent;
        }
    }

    pop() {
        if (this.heap.length === 0) {
            return null;
        }

        const minimum = this.heap[0];
        const last = this.heap.pop();

        if (this.heap.length > 0) {
            this.heap[0] = last;
            this.bubbleDown(0);
        }

        return minimum;
    }

    bubbleDown(index) {
        const length = this.heap.length;

        while (true) {
            const left = 2 * index + 1;
            const right = 2 * index + 2;
            let smallest = index;

            if (
                left < length &&
                this.less(this.heap[left], this.heap[smallest])
            ) {
                smallest = left;
            }

            if (
                right < length &&
                this.less(this.heap[right], this.heap[smallest])
            ) {
                smallest = right;
            }

            if (smallest === index) {
                break;
            }

            [this.heap[index], this.heap[smallest]] =
                [this.heap[smallest], this.heap[index]];

            index = smallest;
        }
    }
}

class RouteGraph extends EventEmitter {
    constructor() {
        super();
        this.adjacency = new Map();
        this.version = 0;
    }

    addVertex(name) {
        if (typeof name !== 'string' || name.trim().length === 0) {
            throw new TypeError('Vertex name must be a non-empty string');
        }

        if (!this.adjacency.has(name)) {
            this.adjacency.set(name, []);
            this.version++;
            this.emit('vertexAdded', { name, version: this.version });
        }
    }

    addEdge(from, to, weight, directed = false) {
        if (
            typeof weight !== 'number' ||
            !Number.isFinite(weight) ||
            weight < 0
        ) {
            throw new RangeError(
                'Edge weight must be finite and non-negative'
            );
        }

        this.addVertex(from);
        this.addVertex(to);

        this.adjacency.get(from).push({ to, weight });

        if (!directed) {
            this.adjacency.get(to).push({ to: from, weight });
        }

        this.version++;

        this.emit('edgeAdded', {
            from,
            to,
            weight,
            directed,
            version: this.version
        });
    }

    dijkstra(source, options = {}) {
        if (!this.adjacency.has(source)) {
            throw new Error(`Unknown source vertex: ${source}`);
        }

        const {
            destination = null,
            onSettle = null
        } = options;

        if (
            destination !== null &&
            !this.adjacency.has(destination)
        ) {
            throw new Error(`Unknown destination: ${destination}`);
        }

        const versionAtStart = this.version;
        const distances = new Map();
        const predecessors = new Map();
        const settled = new Set();

        for (const vertex of this.adjacency.keys()) {
            distances.set(vertex, Infinity);
            predecessors.set(vertex, null);
        }

        distances.set(source, 0);

        const queue = new MinPriorityQueue();
        queue.push(source, 0);

        while (queue.size > 0) {
            const current = queue.pop();

            const vertex = current.value;
            const distance = current.priority;

            // Discard entries superseded by a better relaxation.
            if (distance !== distances.get(vertex)) {
                continue;
            }

            if (settled.has(vertex)) {
                continue;
            }

            settled.add(vertex);

            if (typeof onSettle === 'function') {
                onSettle({
                    vertex,
                    distance,
                    settledCount: settled.size
                });
            }

            if (vertex === destination) {
                break;
            }

            for (const edge of this.adjacency.get(vertex)) {
                if (settled.has(edge.to)) {
                    continue;
                }

                const candidate = distance + edge.weight;

                if (!Number.isFinite(candidate)) {
                    throw new RangeError(
                        'Distance exceeds JavaScript numeric range'
                    );
                }

                if (candidate < distances.get(edge.to)) {
                    distances.set(edge.to, candidate);
                    predecessors.set(edge.to, vertex);

                    queue.push(edge.to, candidate);
                }
            }
        }

        if (this.version !== versionAtStart) {
            throw new Error(
                'Graph changed during shortest-path evaluation'
            );
        }

        return new RouteResult(
            source,
            distances,
            predecessors,
            settled
        );
    }
}

class RouteResult {
    constructor(source, distances, predecessors, settled) {
        this.source = source;
        this.distances = distances;
        this.predecessors = predecessors;
        this.settled = settled;
    }

    distanceTo(destination) {
        if (!this.distances.has(destination)) {
            throw new Error(`Unknown destination: ${destination}`);
        }

        return this.distances.get(destination);
    }

    pathTo(destination) {
        if (!this.distances.has(destination)) {
            throw new Error(`Unknown destination: ${destination}`);
        }

        if (!Number.isFinite(this.distanceTo(destination))) {
            return null;
        }

        const path = [];
        const visited = new Set();

        let current = destination;

        while (current !== null) {
            if (visited.has(current)) {
                throw new Error('Predecessor cycle detected');
            }

            visited.add(current);
            path.push(current);
            current = this.predecessors.get(current);
        }

        path.reverse();

        if (path[0] !== this.source) {
            throw new Error('Invalid predecessor chain');
        }

        return path;
    }
}

class RoutingService {
    constructor(graph) {
        this.graph = graph;
    }

    async calculateRoute(source, destination) {
        // Yield control so a large route calculation does not
        // execute as part of the caller's synchronous setup.
        await new Promise(resolve => setImmediate(resolve));

        const result = this.graph.dijkstra(source, { destination });

        return {
            source,
            destination,
            distance: result.distanceTo(destination),
            path: result.pathTo(destination)
        };
    }
}

function createTransportGraph() {
    const graph = new RouteGraph();

    const connections = [
        ['Delhi', 'Agra', 230],
        ['Delhi', 'Jaipur', 280],
        ['Delhi', 'Lucknow', 550],
        ['Agra', 'Lucknow', 330],
        ['Agra', 'Jaipur', 240],
        ['Jaipur', 'Ahmedabad', 660],
        ['Lucknow', 'Varanasi', 320],
        ['Lucknow', 'Patna', 540],
        ['Varanasi', 'Patna', 250],
        ['Patna', 'Kolkata', 580],
        ['Ahmedabad', 'Mumbai', 530],
        ['Mumbai', 'Pune', 150],
        ['Kolkata', 'Mumbai', 1900]
    ];

    for (const [from, to, weight] of connections) {
        graph.addEdge(from, to, weight);
    }

    graph.addVertex('Chennai');

    return graph;
}

function runTests() {
    const graph = new RouteGraph();

    graph.addEdge('A', 'B', 4, true);
    graph.addEdge('A', 'C', 1, true);
    graph.addEdge('C', 'B', 2, true);
    graph.addEdge('B', 'D', 1, true);
    graph.addEdge('C', 'D', 5, true);
    graph.addVertex('ISOLATED');

    const result = graph.dijkstra('A');

    assert.equal(result.distanceTo('A'), 0);
    assert.equal(result.distanceTo('B'), 3);
    assert.equal(result.distanceTo('D'), 4);

    assert.deepEqual(
        result.pathTo('D'),
        ['A', 'C', 'B', 'D']
    );

    assert.equal(result.pathTo('ISOLATED'), null);

    const zeroGraph = new RouteGraph();
    zeroGraph.addEdge('X', 'Y', 0, true);

    assert.equal(zeroGraph.dijkstra('X').distanceTo('Y'), 0);

    const queue = new MinPriorityQueue();
    queue.push('high', 10);
    queue.push('low', 1);
    queue.push('medium', 5);

    assert.equal(queue.pop().value, 'low');
    assert.equal(queue.pop().value, 'medium');

    assert.throws(
        () => graph.addEdge('A', 'Z', -1),
        RangeError
    );

    assert.throws(
        () => graph.dijkstra('UNKNOWN'),
        Error
    );

    assert.throws(
        () => graph.dijkstra('A', { destination: 'UNKNOWN' }),
        Error
    );

    assert.throws(
        () => queue.push('invalid', Infinity),
        RangeError
    );

    console.log('All JavaScript tests passed.');
}

async function main() {
    runTests();

    const graph = createTransportGraph();

    graph.on('edgeAdded', event => {
        if (event.from === 'Delhi') {
            console.log(
                `Network update: ${event.from} -> ${event.to}`
            );
        }
    });

    const service = new RoutingService(graph);

    console.log('\nTransport network shortest paths');

    const result = graph.dijkstra('Delhi');

    for (const [destination, distance] of result.distances) {
        const path = result.pathTo(destination);

        console.log({
            destination,
            distance: Number.isFinite(distance)
                ? distance
                : 'Unreachable',
            path
        });
    }

    console.log('\nAsynchronous route request');

    const route = await service.calculateRoute(
        'Delhi',
        'Mumbai'
    );

    console.log(route);

    console.log('\nAlgorithm characteristics');
    console.log('Priority queue: Binary min-heap');
    console.log('Relaxation: Greedy distance minimization');
    console.log('Complexity: O((V + E) log V)');
    console.log('Space: O(V + E)');
    console.log('Weights: Non-negative finite numbers only');
}

main().catch(error => {
    console.error('Routing failure:', error.message);
    process.exitCode = 1;
});
