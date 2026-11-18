"use strict";

/*
 * Graph Representation and Dynamic Graph Analysis.
 *
 * Node.js 18+
 *
 * Features:
 * - Adjacency matrix
 * - Adjacency list
 * - Edge list
 * - Weighted and directed graphs
 * - Event-driven graph modifications
 * - Graph validation
 * - BFS and DFS
 * - Dijkstra shortest paths
 * - Graph conversion
 * - Performance measurement
 * - Asynchronous graph processing
 * - JSON persistence
 */

const fs = require("node:fs/promises");
const { performance } = require("node:perf_hooks");
const EventEmitter = require("node:events");

class GraphError extends Error {}
class VertexError extends GraphError {}
class EdgeError extends GraphError {}

const Representation = Object.freeze({
    MATRIX: "matrix",
    LIST: "list",
    EDGE_LIST: "edge_list"
});

class Graph extends EventEmitter {
    constructor(vertexCount, directed = false, representation) {
        super();

        if (!Number.isSafeInteger(vertexCount) || vertexCount < 0) {
            throw new VertexError("Invalid vertex count.");
        }

        if (typeof directed !== "boolean") {
            throw new GraphError("Directed must be boolean.");
        }

        if (!Object.values(Representation).includes(representation)) {
            throw new GraphError("Unsupported representation.");
        }

        this.vertexCount = vertexCount;
        this.directed = directed;
        this.representation = representation;
    }

    validateVertex(vertex) {
        if (
            !Number.isSafeInteger(vertex) ||
            vertex < 0 ||
            vertex >= this.vertexCount
        ) {
            throw new VertexError(`Invalid vertex: ${vertex}`);
        }
    }

    validateEdge(source, target, weight) {
        this.validateVertex(source);
        this.validateVertex(target);

        if (typeof weight !== "number" || !Number.isFinite(weight)) {
            throw new EdgeError("Weight must be finite.");
        }
    }

    addEdge(source, target, weight = 1) {
        this.validateEdge(source, target, weight);

        this._add(source, target, weight);

        if (!this.directed && source !== target) {
            this._add(target, source, weight);
        }

        this.emit("edgeAdded", {
            source,
            target,
            weight
        });
    }

    removeEdge(source, target) {
        this.validateVertex(source);
        this.validateVertex(target);

        const removed = this._remove(source, target);

        if (!this.directed && source !== target) {
            this._remove(target, source);
        }

        if (removed) {
            this.emit("edgeRemoved", { source, target });
        }

        return removed;
    }

    hasEdge(source, target) {
        this.validateVertex(source);
        this.validateVertex(target);

        return this._has(source, target);
    }

    neighbors(vertex) {
        this.validateVertex(vertex);

        return this._neighbors(vertex);
    }

    toJSON() {
        return {
            vertexCount: this.vertexCount,
            directed: this.directed,
            representation: this.representation,
            edges: this.edges()
        };
    }

    static fromJSON(data, representation = Representation.LIST) {
        if (
            !data ||
            !Number.isSafeInteger(data.vertexCount) ||
            !Array.isArray(data.edges)
        ) {
            throw new GraphError("Invalid graph document.");
        }

        const graph = createGraph(
            data.vertexCount,
            Boolean(data.directed),
            representation
        );

        for (const edge of data.edges) {
            if (
                !edge ||
                !Number.isSafeInteger(edge.source) ||
                !Number.isSafeInteger(edge.target)
            ) {
                throw new EdgeError("Invalid edge document.");
            }

            graph.addEdge(
                edge.source,
                edge.target,
                edge.weight
            );
        }

        return graph;
    }

    bfs(start) {
        this.validateVertex(start);

        const visited = new Set([start]);
        const queue = [start];
        const result = [];

        let head = 0;

        while (head < queue.length) {
            const current = queue[head++];
            result.push(current);

            for (const [neighbor] of this.neighbors(current)) {
                if (!visited.has(neighbor)) {
                    visited.add(neighbor);
                    queue.push(neighbor);
                }
            }
        }

        return result;
    }

    dfs(start) {
        this.validateVertex(start);

        const visited = new Set();
        const stack = [start];
        const result = [];

        while (stack.length > 0) {
            const current = stack.pop();

            if (visited.has(current)) {
                continue;
            }

            visited.add(current);
            result.push(current);

            const adjacent = this.neighbors(current)
                .sort((a, b) => b[0] - a[0]);

            for (const [neighbor] of adjacent) {
                if (!visited.has(neighbor)) {
                    stack.push(neighbor);
                }
            }
        }

        return result;
    }

    dijkstra(start) {
        this.validateVertex(start);

        const distance = Array(this.vertexCount).fill(Infinity);
        const settled = new Set();

        for (const edge of this.edges()) {
            if (edge.weight < 0) {
                throw new GraphError(
                    "Dijkstra does not support negative weights."
                );
            }
        }

        distance[start] = 0;

        while (settled.size < this.vertexCount) {
            let current = -1;
            let best = Infinity;

            for (let vertex = 0; vertex < this.vertexCount; vertex++) {
                if (
                    !settled.has(vertex) &&
                    distance[vertex] < best
                ) {
                    best = distance[vertex];
                    current = vertex;
                }
            }

            if (current === -1) {
                break;
            }

            settled.add(current);

            for (const [neighbor, weight] of this.neighbors(current)) {
                const candidate = best + weight;

                if (candidate < distance[neighbor]) {
                    distance[neighbor] = candidate;
                }
            }
        }

        return distance;
    }

    edges() {
        return this._edges();
    }

    memoryEstimate() {
        return this._memoryEstimate();
    }

    async processInBatches(batchSize = 1000) {
        if (!Number.isSafeInteger(batchSize) || batchSize <= 0) {
            throw new GraphError("Batch size must be positive.");
        }

        const allEdges = this.edges();
        let processed = 0;

        for (let offset = 0; offset < allEdges.length; offset += batchSize) {
            const batch = allEdges.slice(offset, offset + batchSize);

            // Yield control between batches for event-loop responsiveness.
            await new Promise(resolve => setImmediate(resolve));

            processed += batch.length;

            this.emit("batchProcessed", {
                processed,
                batchSize: batch.length
            });
        }

        return processed;
    }

    _add() { throw new Error("Not implemented"); }
    _remove() { throw new Error("Not implemented"); }
    _has() { throw new Error("Not implemented"); }
    _neighbors() { throw new Error("Not implemented"); }
    _edges() { throw new Error("Not implemented"); }
    _memoryEstimate() { throw new Error("Not implemented"); }
}

class MatrixGraph extends Graph {
    constructor(vertexCount, directed = false) {
        super(vertexCount, directed, Representation.MATRIX);

        this.matrix = Array.from(
            { length: vertexCount },
            () => Array(vertexCount).fill(null)
        );
    }

    _add(source, target, weight) {
        this.matrix[source][target] = weight;
    }

    _remove(source, target) {
        const existed = this.matrix[source][target] !== null;
        this.matrix[source][target] = null;
        return existed;
    }

    _has(source, target) {
        return this.matrix[source][target] !== null;
    }

    _neighbors(vertex) {
        const result = [];

        for (let neighbor = 0; neighbor < this.vertexCount; neighbor++) {
            const weight = this.matrix[vertex][neighbor];

            if (weight !== null) {
                result.push([neighbor, weight]);
            }
        }

        return result;
    }

    _edges() {
        const result = [];

        for (let source = 0; source < this.vertexCount; source++) {
            for (let target = 0; target < this.vertexCount; target++) {
                const weight = this.matrix[source][target];

                if (
                    weight !== null &&
                    (this.directed || target >= source)
                ) {
                    result.push({ source, target, weight });
                }
            }
        }

        return result;
    }

    _memoryEstimate() {
        return this.vertexCount * this.vertexCount * 8;
    }
}

class ListGraph extends Graph {
    constructor(vertexCount, directed = false) {
        super(vertexCount, directed, Representation.LIST);

        this.adjacency = Array.from(
            { length: vertexCount },
            () => new Map()
        );
    }

    _add(source, target, weight) {
        this.adjacency[source].set(target, weight);
    }

    _remove(source, target) {
        return this.adjacency[source].delete(target);
    }

    _has(source, target) {
        return this.adjacency[source].has(target);
    }

    _neighbors(vertex) {
        return [...this.adjacency[vertex].entries()]
            .sort((a, b) => a[0] - b[0]);
    }

    _edges() {
        const result = [];

        for (let source = 0; source < this.vertexCount; source++) {
            for (const [target, weight] of this.adjacency[source]) {
                if (this.directed || target >= source) {
                    result.push({ source, target, weight });
                }
            }
        }

        return result;
    }

    _memoryEstimate() {
        let total = this.vertexCount * 8;

        for (const adjacent of this.adjacency) {
            total += adjacent.size * 40;
        }

        return total;
    }
}

class EdgeListGraph extends Graph {
    constructor(vertexCount, directed = false) {
        super(vertexCount, directed, Representation.EDGE_LIST);

        this.data = new Map();
    }

    key(source, target) {
        if (!this.directed && source > target) {
            [source, target] = [target, source];
        }

        return `${source}:${target}`;
    }

    _add(source, target, weight) {
        this.data.set(this.key(source, target), {
            source,
            target,
            weight
        });
    }

    _remove(source, target) {
        return this.data.delete(this.key(source, target));
    }

    _has(source, target) {
        return this.data.has(this.key(source, target));
    }

    _neighbors(vertex) {
        const result = [];

        for (const edge of this.data.values()) {
            if (edge.source === vertex) {
                result.push([edge.target, edge.weight]);
            }

            if (
                !this.directed &&
                edge.target === vertex &&
                edge.source !== vertex
            ) {
                result.push([edge.source, edge.weight]);
            }
        }

        return result.sort((a, b) => a[0] - b[0]);
    }

    _edges() {
        return [...this.data.values()].map(edge => ({ ...edge }));
    }

    _memoryEstimate() {
        return this.data.size * 64;
    }
}

function createGraph(vertexCount, directed, representation) {
    switch (representation) {
        case Representation.MATRIX:
            return new MatrixGraph(vertexCount, directed);

        case Representation.LIST:
            return new ListGraph(vertexCount, directed);

        case Representation.EDGE_LIST:
            return new EdgeListGraph(vertexCount, directed);

        default:
            throw new GraphError("Unknown representation.");
    }
}

function buildSampleGraph(representation) {
    const graph = createGraph(6, false, representation);

    const edges = [
        [0, 1, 4],
        [0, 2, 2],
        [1, 2, 1],
        [1, 3, 5],
        [2, 3, 8],
        [2, 4, 10],
        [3, 4, 2],
        [4, 5, 3]
    ];

    for (const [source, target, weight] of edges) {
        graph.addEdge(source, target, weight);
    }

    return graph;
}

async function benchmark(graph, repetitions = 1000) {
    if (!Number.isSafeInteger(repetitions) || repetitions <= 0) {
        throw new GraphError("Invalid repetition count.");
    }

    const source = 0;
    const target = graph.vertexCount - 1;

    let start = performance.now();

    for (let i = 0; i < repetitions; i++) {
        graph.hasEdge(source, target);
    }

    const edgeLookupMs = performance.now() - start;

    start = performance.now();

    for (let i = 0; i < repetitions; i++) {
        graph.neighbors(source);
    }

    const neighborLookupMs = performance.now() - start;

    start = performance.now();

    for (let i = 0; i < repetitions; i++) {
        graph.edges();
    }

    const enumerationMs = performance.now() - start;

    return {
        representation: graph.representation,
        vertices: graph.vertexCount,
        edges: graph.edges().length,
        estimatedMemoryBytes: graph.memoryEstimate(),
        edgeLookupMs,
        neighborLookupMs,
        enumerationMs
    };
}

async function saveGraph(graph, filename) {
    const data = JSON.stringify(graph.toJSON(), null, 2);
    await fs.writeFile(filename, data, {
        encoding: "utf8",
        mode: 0o600
    });
}

async function loadGraph(filename, representation) {
    const raw = await fs.readFile(filename, "utf8");
    const parsed = JSON.parse(raw);

    return Graph.fromJSON(parsed, representation);
}

async function runTests() {
    for (const representation of Object.values(Representation)) {
        const graph = buildSampleGraph(representation);

        if (graph.edges().length !== 8) {
            throw new Error("Edge count test failed.");
        }

        if (JSON.stringify(graph.bfs(0)) !== JSON.stringify([0, 1, 2, 3, 4, 5])) {
            throw new Error("BFS test failed.");
        }

        const distances = graph.dijkstra(0);

        const expected = [0, 3, 2, 8, 10, 13];

        if (JSON.stringify(distances) !== JSON.stringify(expected)) {
            throw new Error("Shortest path test failed.");
        }

        graph.removeEdge(0, 1);

        if (graph.hasEdge(0, 1)) {
            throw new Error("Edge removal test failed.");
        }

        graph.addEdge(0, 1, 4);
    }

    const directed = new ListGraph(3, true);
    directed.addEdge(0, 1);

    if (directed.hasEdge(1, 0)) {
        throw new Error("Directed edge test failed.");
    }

    const events = new ListGraph(2);

    let eventCount = 0;

    events.on("edgeAdded", () => eventCount++);
    events.addEdge(0, 1);

    if (eventCount !== 1) {
        throw new Error("Event handling test failed.");
    }

    const negative = new ListGraph(2, true);
    negative.addEdge(0, 1, -2);

    let rejected = false;

    try {
        negative.dijkstra(0);
    } catch (error) {
        rejected = error instanceof GraphError;
    }

    if (!rejected) {
        throw new Error("Negative weight validation failed.");
    }

    console.log("All JavaScript graph tests passed.");
}

async function main() {
    await runTests();

    for (const representation of Object.values(Representation)) {
        const graph = buildSampleGraph(representation);

        graph.on("edgeAdded", event => {
            console.log("Edge added:", event);
        });

        graph.on("batchProcessed", event => {
            console.log("Batch progress:", event);
        });

        console.log(`\nRepresentation: ${representation}`);
        console.log("Edges:", graph.edges());
        console.log("BFS:", graph.bfs(0));
        console.log("DFS:", graph.dfs(0));
        console.log("Shortest paths:", graph.dijkstra(0));

        console.log(
            "Benchmark:",
            await benchmark(graph, 1000)
        );

        await graph.processInBatches(3);
    }

    const graph = buildSampleGraph(Representation.LIST);

    try {
        await saveGraph(graph, "graph_data.json");

        const restored = await loadGraph(
            "graph_data.json",
            Representation.EDGE_LIST
        );

        if (restored.edges().length !== graph.edges().length) {
            throw new Error("Persistence verification failed.");
        }

        console.log("\nGraph persistence verified.");
    } catch (error) {
        console.error("Persistence failure:", error.message);
        process.exitCode = 1;
    }

    console.log("\nGraph analysis completed.");
}

main().catch(error => {
    console.error("Execution failed:", error.message);
    process.exitCode = 1;
});
