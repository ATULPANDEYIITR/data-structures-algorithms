"use strict";

/*
 * Prim's Algorithm
 * Priority queues, adjacency maps and event-driven graph processing.
 *
 * Runtime: Node.js 18+
 *
 * Features:
 * - Undirected weighted graphs.
 * - Adjacency Map representation.
 * - Binary min-heap priority queue.
 * - Lazy deletion of outdated edges.
 * - Minimum spanning forests.
 * - Event notifications.
 * - Asynchronous execution.
 * - Validation and independent structural verification.
 */

const { EventEmitter } = require("node:events");

class GraphValidationError extends Error {
    constructor(message) {
        super(message);
        this.name = "GraphValidationError";
    }
}

class MinPriorityQueue {
    constructor() {
        this.heap = [];
    }

    get size() {
        return this.heap.length;
    }

    swap(i, j) {
        [this.heap[i], this.heap[j]] =
            [this.heap[j], this.heap[i]];
    }

    push(item) {
        this.heap.push(item);

        let index = this.heap.length - 1;

        while (index > 0) {
            const parent = Math.floor((index - 1) / 2);

            if (this.heap[parent].weight <= item.weight) {
                break;
            }

            this.swap(index, parent);
            index = parent;
        }
    }

    pop() {
        if (this.heap.length === 0) {
            return undefined;
        }

        const minimum = this.heap[0];
        const last = this.heap.pop();

        if (this.heap.length > 0) {
            this.heap[0] = last;
            this.siftDown(0);
        }

        return minimum;
    }

    siftDown(index) {
        const length = this.heap.length;

        while (true) {
            let smallest = index;
            const left = 2 * index + 1;
            const right = 2 * index + 2;

            if (
                left < length &&
                this.heap[left].weight < this.heap[smallest].weight
            ) {
                smallest = left;
            }

            if (
                right < length &&
                this.heap[right].weight < this.heap[smallest].weight
            ) {
                smallest = right;
            }

            if (smallest === index) {
                break;
            }

            this.swap(index, smallest);
            index = smallest;
        }
    }
}

class WeightedGraph {
    constructor() {
        this.adjacency = new Map();
    }

    addVertex(vertex) {
        if (
            vertex === null ||
            vertex === undefined ||
            (typeof vertex !== "string" &&
             typeof vertex !== "number")
        ) {
            throw new GraphValidationError(
                "Vertices must be non-null strings or numbers."
            );
        }

        if (!this.adjacency.has(vertex)) {
            this.adjacency.set(vertex, []);
        }
    }

    addEdge(source, destination, weight) {
        if (source === destination) {
            throw new GraphValidationError(
                "Self-loops are not supported."
            );
        }

        if (
            typeof weight !== "number" ||
            !Number.isFinite(weight)
        ) {
            throw new GraphValidationError(
                "Edge weight must be a finite number."
            );
        }

        this.addVertex(source);
        this.addVertex(destination);

        this.adjacency.get(source).push({
            destination,
            weight
        });

        this.adjacency.get(destination).push({
            destination: source,
            weight
        });
    }

    get vertexCount() {
        return this.adjacency.size;
    }

    get edgeCount() {
        let count = 0;

        for (const neighbors of this.adjacency.values()) {
            count += neighbors.length;
        }

        return count / 2;
    }
}

class PrimEngine extends EventEmitter {
    constructor(graph) {
        super();

        if (!(graph instanceof WeightedGraph)) {
            throw new GraphValidationError(
                "PrimEngine requires a WeightedGraph."
            );
        }

        this.graph = graph;
        this.running = false;
    }

    async calculate() {
        if (this.running) {
            throw new Error("This engine is already executing.");
        }

        this.running = true;

        try {
            return await this.execute();
        } finally {
            this.running = false;
        }
    }

    async execute() {
        const visited = new Set();
        const selectedEdges = [];

        let totalWeight = 0;
        let components = 0;
        let examinedEdges = 0;

        const queue = new MinPriorityQueue();

        // Insert candidate edges into the binary min-heap.
        const enqueueNeighbors = (vertex) => {
            for (const edge of this.graph.adjacency.get(vertex)) {
                examinedEdges++;

                if (!visited.has(edge.destination)) {
                    queue.push({
                        source: vertex,
                        destination: edge.destination,
                        weight: edge.weight
                    });
                }
            }
        };

        for (const start of this.graph.adjacency.keys()) {
            if (visited.has(start)) {
                continue;
            }

            components++;
            visited.add(start);

            this.emit("componentStarted", {
                root: start,
                component: components
            });

            enqueueNeighbors(start);

            while (queue.size > 0) {
                const edge = queue.pop();

                // Ignore candidates whose destination was already reached.
                if (visited.has(edge.destination)) {
                    continue;
                }

                visited.add(edge.destination);

                selectedEdges.push(Object.freeze({ ...edge }));
                totalWeight += edge.weight;

                this.emit("edgeSelected", edge);

                enqueueNeighbors(edge.destination);

                // Yield periodically to allow other event-loop work.
                if (selectedEdges.length % 1000 === 0) {
                    await new Promise(resolve => setImmediate(resolve));
                }
            }
        }

        const result = Object.freeze({
            edges: Object.freeze(selectedEdges),
            totalWeight,
            components,
            vertices: this.graph.vertexCount,
            examinedEdges,
            connected:
                this.graph.vertexCount === 0 || components === 1
        });

        this.emit("completed", result);

        return result;
    }
}

function verifyForest(graph, result) {
    if (
        result.edges.length !==
        result.vertices - result.components
    ) {
        return false;
    }

    const parent = new Map();
    const rank = new Map();

    for (const vertex of graph.adjacency.keys()) {
        parent.set(vertex, vertex);
        rank.set(vertex, 0);
    }

    function find(vertex) {
        while (parent.get(vertex) !== vertex) {
            parent.set(vertex, parent.get(parent.get(vertex)));
            vertex = parent.get(vertex);
        }

        return vertex;
    }

    function union(a, b) {
        let rootA = find(a);
        let rootB = find(b);

        if (rootA === rootB) {
            return false;
        }

        if (rank.get(rootA) < rank.get(rootB)) {
            [rootA, rootB] = [rootB, rootA];
        }

        parent.set(rootB, rootA);

        if (rank.get(rootA) === rank.get(rootB)) {
            rank.set(rootA, rank.get(rootA) + 1);
        }

        return true;
    }

    let weight = 0;

    for (const edge of result.edges) {
        const valid = graph.adjacency
            .get(edge.source)
            ?.some(
                item =>
                    item.destination === edge.destination &&
                    item.weight === edge.weight
            );

        if (
            !valid ||
            !union(edge.source, edge.destination)
        ) {
            return false;
        }

        weight += edge.weight;
    }

    const roots = new Set(
        [...graph.adjacency.keys()].map(find)
    );

    return (
        roots.size === result.components &&
        Math.abs(weight - result.totalWeight) < 1e-9
    );
}

async function main() {
    const graph = new WeightedGraph();

    const edges = [
        ["A", "B", 4],
        ["A", "C", 3],
        ["B", "C", 1],
        ["B", "D", 2],
        ["C", "D", 4],
        ["C", "E", 5],
        ["D", "E", 2],
        ["D", "F", 3],
        ["E", "F", 1],
        ["E", "G", 7],
        ["F", "G", 2],
        ["H", "I", 6]
    ];

    for (const [source, destination, weight] of edges) {
        graph.addEdge(source, destination, weight);
    }

    graph.addVertex("ISOLATED");

    const engine = new PrimEngine(graph);

    engine.on("componentStarted", event => {
        console.log(`Starting component at ${event.root}`);
    });

    engine.on("edgeSelected", edge => {
        console.log(
            `Selected ${edge.source} -> ${edge.destination}: ${edge.weight}`
        );
    });

    engine.on("completed", () => {
        console.log("Algorithm execution completed.");
    });

    const result = await engine.calculate();

    console.log("\nMinimum Spanning Forest");
    console.log("=======================");
    console.log(`Vertices: ${result.vertices}`);
    console.log(`Components: ${result.components}`);
    console.log(`Selected edges: ${result.edges.length}`);
    console.log(`Total weight: ${result.totalWeight}`);
    console.log(`Connected: ${result.connected}`);
    console.log(`Examined edges: ${result.examinedEdges}`);

    if (!verifyForest(graph, result)) {
        throw new Error("Forest verification failed.");
    }

    console.log("Verification: PASSED");

    // Negative-weight and parallel-edge test.
    const testGraph = new WeightedGraph();
    testGraph.addEdge("X", "Y", -5);
    testGraph.addEdge("X", "Y", 2);
    testGraph.addEdge("Y", "Z", -2);
    testGraph.addEdge("X", "Z", 1);

    const testEngine = new PrimEngine(testGraph);
    const testResult = await testEngine.calculate();

    if (
        testResult.totalWeight !== -7 ||
        !verifyForest(testGraph, testResult)
    ) {
        throw new Error("Negative-weight test failed.");
    }

    console.log("Negative-weight test: PASSED");

    // Invalid input test.
    try {
        graph.addEdge("A", "A", 5);
        throw new Error("Self-loop validation failed.");
    } catch (error) {
        if (!(error instanceof GraphValidationError)) {
            throw error;
        }
    }

    console.log("Input validation test: PASSED");
}

main().catch(error => {
    console.error("Execution failed:", error.message);
    process.exitCode = 1;
});
