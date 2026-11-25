"use strict";

/*
 * Bellman-Ford Algorithm
 *
 * Event-driven graph analysis with:
 * - Map-based graph storage
 * - Negative edge support
 * - Relaxation events
 * - Asynchronous execution
 * - Negative-cycle detection
 * - Cycle-impact propagation
 * - Shortest-path reconstruction
 * - Immutable result snapshots
 * - Cancellation and validation
 *
 * Runtime: Node.js 18+
 */

const { EventEmitter } = require("node:events");

class GraphError extends Error {
    constructor(message) {
        super(message);
        this.name = "GraphError";
    }
}

class NegativeCycleError extends Error {
    constructor(cycle) {
        super("Shortest path is undefined because of a reachable negative cycle.");
        this.name = "NegativeCycleError";
        this.cycle = Object.freeze([...cycle]);
    }
}

class WeightedGraph extends EventEmitter {
    #vertices = new Set();
    #edges = [];
    #adjacency = new Map();
    #version = 0;

    get version() {
        return this.#version;
    }

    get vertexCount() {
        return this.#vertices.size;
    }

    addVertex(vertex) {
        if (!Number.isSafeInteger(vertex)) {
            throw new GraphError("Vertex must be a safe integer.");
        }

        if (this.#vertices.has(vertex)) {
            return false;
        }

        this.#vertices.add(vertex);
        this.#adjacency.set(vertex, []);
        this.#version++;

        this.emit("vertexAdded", { vertex, version: this.#version });
        return true;
    }

    addEdge(source, destination, weight) {
        if (!this.#vertices.has(source) || !this.#vertices.has(destination)) {
            throw new GraphError("Both edge endpoints must exist.");
        }

        if (!Number.isSafeInteger(weight)) {
            throw new GraphError("Weight must be a safe integer.");
        }

        const edge = Object.freeze({ source, destination, weight });

        this.#edges.push(edge);
        this.#adjacency.get(source).push(destination);
        this.#version++;

        this.emit("edgeAdded", { ...edge, version: this.#version });
    }

    snapshot() {
        return Object.freeze({
            version: this.#version,
            vertices: Object.freeze([...this.#vertices]),
            edges: Object.freeze([...this.#edges]),
            adjacency: new Map(
                [...this.#adjacency].map(([vertex, neighbors]) => [
                    vertex,
                    Object.freeze([...neighbors])
                ])
            )
        });
    }
}

class BellmanFordEngine extends EventEmitter {
    #graph;
    #snapshot = null;

    constructor(graph) {
        super();

        if (!(graph instanceof WeightedGraph)) {
            throw new TypeError("A WeightedGraph instance is required.");
        }

        this.#graph = graph;
    }

    async execute(source, options = {}) {
        const {
            signal,
            yieldEvery = 4
        } = options;

        if (!Number.isSafeInteger(source)) {
            throw new GraphError("Source must be a safe integer.");
        }

        if (!Number.isInteger(yieldEvery) || yieldEvery <= 0) {
            throw new GraphError("yieldEvery must be a positive integer.");
        }

        const snapshot = this.#graph.snapshot();

        if (!snapshot.vertices.includes(source)) {
            throw new GraphError("Source vertex does not exist.");
        }

        const vertices = snapshot.vertices;
        const edges = snapshot.edges;
        const adjacency = snapshot.adjacency;

        const distance = new Map();
        const predecessor = new Map();

        for (const vertex of vertices) {
            distance.set(vertex, Infinity);
            predecessor.set(vertex, null);
        }

        distance.set(source, 0);

        let passes = 0;
        let operations = 0;

        // Every execution works on one immutable graph snapshot.
        // Later graph modifications cannot corrupt the current calculation.
        const checkCancellation = () => {
            if (signal?.aborted) {
                throw signal.reason ?? new Error("Execution cancelled.");
            }
        };

        for (let iteration = 0; iteration < vertices.length - 1; iteration++) {
            checkCancellation();

            let updated = false;

            for (const edge of edges) {
                checkCancellation();

                const { source: u, destination: v, weight } = edge;
                const current = distance.get(u);

                if (current === Infinity) {
                    continue;
                }

                const candidate = current + weight;

                if (!Number.isSafeInteger(candidate)) {
                    throw new RangeError(
                        "Distance exceeds JavaScript safe integer precision."
                    );
                }

                if (candidate < distance.get(v)) {
                    distance.set(v, candidate);
                    predecessor.set(v, u);
                    updated = true;

                    this.emit("relaxed", {
                        edge,
                        distance: candidate,
                        iteration: iteration + 1
                    });
                }

                operations++;
            }

            passes++;

            this.emit("passCompleted", {
                pass: passes,
                updated,
                operations
            });

            if (!updated) {
                break;
            }

            if (passes % yieldEvery === 0) {
                await new Promise(resolve => setImmediate(resolve));
                checkCancellation();
            }
        }

        // Find every vertex that can be improved by another relaxation.
        const affected = new Set();

        for (const edge of edges) {
            const current = distance.get(edge.source);

            if (
                current !== Infinity &&
                current + edge.weight < distance.get(edge.destination)
            ) {
                affected.add(edge.destination);
            }
        }

        // Propagate negative-cycle influence to all downstream vertices.
        const queue = [...affected];
        let head = 0;

        while (head < queue.length) {
            const current = queue[head++];

            for (const neighbor of adjacency.get(current)) {
                if (!affected.has(neighbor)) {
                    affected.add(neighbor);
                    queue.push(neighbor);
                }
            }
        }

        const negativeCycle = this.#findCycle(
            affected,
            predecessor,
            vertices.length
        );

        const result = Object.freeze({
            source,
            graphVersion: snapshot.version,
            distances: new Map(distance),
            predecessors: new Map(predecessor),
            negativeCycle: Object.freeze(negativeCycle),
            affectedVertices: Object.freeze([...affected]),
            passes,
            operations,
            hasNegativeCycle: negativeCycle.length > 0
        });

        this.#snapshot = result;

        this.emit("completed", result);

        return result;
    }

    #findCycle(affected, predecessor, vertexCount) {
        if (affected.size === 0) {
            return [];
        }

        // Use a vertex inside a relaxable cycle.
        const candidates = [...affected];

        for (const candidate of candidates) {
            let current = candidate;
            let valid = true;

            for (let i = 0; i < vertexCount; i++) {
                current = predecessor.get(current);

                if (current === null || current === undefined) {
                    valid = false;
                    break;
                }
            }

            if (!valid) {
                continue;
            }

            const start = current;
            const cycle = [start];

            current = predecessor.get(start);

            while (current !== start && current !== null) {
                if (cycle.length > vertexCount) {
                    break;
                }

                cycle.push(current);
                current = predecessor.get(current);
            }

            if (current === start) {
                cycle.push(start);
                return cycle.reverse();
            }
        }

        return [];
    }

    getPath(destination) {
        if (!this.#snapshot) {
            throw new GraphError("Execute the algorithm first.");
        }

        const result = this.#snapshot;

        if (result.affectedVertices.includes(destination)) {
            throw new NegativeCycleError(result.negativeCycle);
        }

        const distance = result.distances.get(destination);

        if (distance === undefined) {
            throw new GraphError("Unknown destination.");
        }

        if (distance === Infinity) {
            return null;
        }

        const path = [];
        let current = destination;

        while (current !== null) {
            path.push(current);

            if (current === result.source) {
                return Object.freeze(path.reverse());
            }

            current = result.predecessors.get(current);
        }

        return null;
    }
}

async function demonstrateNormalGraph() {
    console.log("\n========== NORMAL GRAPH ==========");

    const graph = new WeightedGraph();

    for (let vertex = 0; vertex < 6; vertex++) {
        graph.addVertex(vertex);
    }

    graph.on("edgeAdded", event => {
        console.log("Edge added:", event);
    });

    graph.addEdge(0, 1, 6);
    graph.addEdge(0, 2, 7);
    graph.addEdge(1, 3, 5);
    graph.addEdge(1, 4, -4);
    graph.addEdge(2, 3, -3);
    graph.addEdge(3, 1, -2);
    graph.addEdge(4, 5, 2);

    const engine = new BellmanFordEngine(graph);

    engine.on("relaxed", event => {
        console.log(
            `Relaxed ${event.edge.source}->${event.edge.destination}:`,
            event.distance
        );
    });

    const result = await engine.execute(0);

    console.log("\nDistances:");

    for (const [vertex, distance] of result.distances) {
        console.log(
            vertex,
            result.affectedVertices.includes(vertex)
                ? "UNDEFINED"
                : distance
        );
    }

    console.log("Negative cycle:", result.negativeCycle);
    console.log("Path to 5:", engine.getPath(5));
    console.log("Passes:", result.passes);
}

async function demonstrateNegativeCycle() {
    console.log("\n========== NEGATIVE CYCLE ==========");

    const graph = new WeightedGraph();

    for (let vertex = 0; vertex < 5; vertex++) {
        graph.addVertex(vertex);
    }

    graph.addEdge(0, 1, 2);
    graph.addEdge(1, 2, -4);
    graph.addEdge(2, 1, 1);
    graph.addEdge(2, 3, 5);
    graph.addEdge(3, 4, 2);

    const engine = new BellmanFordEngine(graph);
    const result = await engine.execute(0);

    console.log("Cycle:", result.negativeCycle);
    console.log("Affected:", result.affectedVertices);

    try {
        engine.getPath(4);
    } catch (error) {
        console.log(error.name + ":", error.message);
    }
}

async function demonstrateUnreachableCycle() {
    console.log("\n========== UNREACHABLE CYCLE ==========");

    const graph = new WeightedGraph();

    for (let vertex = 0; vertex < 4; vertex++) {
        graph.addVertex(vertex);
    }

    graph.addEdge(0, 1, 5);
    graph.addEdge(2, 3, -3);
    graph.addEdge(3, 2, 1);

    const engine = new BellmanFordEngine(graph);
    const result = await engine.execute(0);

    console.log("Negative cycle reachable from source:", result.hasNegativeCycle);
    console.log("Distance to 1:", result.distances.get(1));
    console.log("Distance to 2:", result.distances.get(2));
}

async function runTests() {
    const graph = new WeightedGraph();

    [0, 1, 2, 3].forEach(vertex => graph.addVertex(vertex));

    graph.addEdge(0, 1, 4);
    graph.addEdge(1, 2, -2);
    graph.addEdge(2, 3, 3);

    const engine = new BellmanFordEngine(graph);
    const result = await engine.execute(0);

    if (result.distances.get(3) !== 5) {
        throw new Error("Shortest-distance test failed.");
    }

    if (engine.getPath(3).join(",") !== "0,1,2,3") {
        throw new Error("Path reconstruction test failed.");
    }

    const cycleGraph = new WeightedGraph();

    [0, 1, 2].forEach(vertex => cycleGraph.addVertex(vertex));

    cycleGraph.addEdge(0, 1, 1);
    cycleGraph.addEdge(1, 2, -3);
    cycleGraph.addEdge(2, 1, 1);

    const cycleResult = await new BellmanFordEngine(cycleGraph).execute(0);

    if (!cycleResult.hasNegativeCycle) {
        throw new Error("Negative-cycle test failed.");
    }

    const disconnectedGraph = new WeightedGraph();

    [0, 1, 2].forEach(vertex => disconnectedGraph.addVertex(vertex));

    disconnectedGraph.addEdge(0, 1, 10);

    const disconnectedResult =
        await new BellmanFordEngine(disconnectedGraph).execute(0);

    if (disconnectedResult.distances.get(2) !== Infinity) {
        throw new Error("Unreachable vertex test failed.");
    }

    // Validate safe handling of malformed graph operations.
    let rejected = false;

    try {
        graph.addEdge(0, 9, 1);
    } catch (error) {
        rejected = error instanceof GraphError;
    }

    if (!rejected) {
        throw new Error("Invalid endpoint test failed.");
    }

    console.log("\nAll JavaScript tests passed.");
}

async function main() {
    try {
        await demonstrateNormalGraph();
        await demonstrateNegativeCycle();
        await demonstrateUnreachableCycle();
        await runTests();
    } catch (error) {
        console.error("Execution failed:", error);
        process.exitCode = 1;
    }
}

main();
