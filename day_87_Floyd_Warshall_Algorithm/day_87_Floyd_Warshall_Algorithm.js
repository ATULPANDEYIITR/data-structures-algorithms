"use strict";

/*
 * Floyd-Warshall Algorithm
 * Event-driven all-pairs shortest-path engine.
 *
 * Runtime: Node.js 18+
 *
 * Features:
 * - Directed weighted graph
 * - Map-based vertex management
 * - Dynamic programming
 * - Next-hop path reconstruction
 * - Negative-cycle detection
 * - Event-driven computation notifications
 * - Asynchronous graph processing
 * - Query caching
 * - Input validation
 */

const { EventEmitter } = require("node:events");

class GraphValidationError extends Error {
    constructor(message) {
        super(message);
        this.name = "GraphValidationError";
    }
}

class NegativeCycleError extends Error {
    constructor(message) {
        super(message);
        this.name = "NegativeCycleError";
    }
}

class GraphVertex {
    constructor(id, metadata = {}) {
        if (typeof id !== "string" || id.trim().length === 0) {
            throw new GraphValidationError(
                "Vertex identifier must be a non-empty string"
            );
        }

        this.id = id;
        this.metadata = Object.freeze({ ...metadata });
    }
}

class WeightedGraph {
    constructor() {
        this.vertices = new Map();
        this.edges = [];
        this.version = 0;
    }

    addVertex(id, metadata = {}) {
        if (this.vertices.has(id)) {
            throw new GraphValidationError(
                `Duplicate vertex: ${id}`
            );
        }

        const vertex = new GraphVertex(id, metadata);

        this.vertices.set(id, vertex);
        this.version++;

        return vertex;
    }

    addEdge(source, destination, weight, bidirectional = false) {
        if (!this.vertices.has(source) ||
            !this.vertices.has(destination)) {
            throw new GraphValidationError(
                "An edge references an unknown vertex"
            );
        }

        if (typeof weight !== "number" ||
            !Number.isFinite(weight)) {
            throw new GraphValidationError(
                "Weight must be a finite number"
            );
        }

        this.edges.push(Object.freeze({
            source,
            destination,
            weight
        }));

        if (bidirectional) {
            this.edges.push(Object.freeze({
                source: destination,
                destination: source,
                weight
            }));
        }

        this.version++;
    }

    snapshot() {
        return Object.freeze({
            version: this.version,
            vertices: Object.freeze([...this.vertices.keys()]),
            edges: Object.freeze([...this.edges])
        });
    }
}

class FloydWarshallEngine extends EventEmitter {
    constructor(graph) {
        super();

        if (!(graph instanceof WeightedGraph)) {
            throw new GraphValidationError(
                "A WeightedGraph instance is required"
            );
        }

        this.graph = graph;
        this.result = null;
        this.cache = new Map();
        this.computing = false;
    }

    compute() {
        if (this.computing) {
            throw new Error("A computation is already running");
        }

        this.computing = true;

        try {
            const snapshot = this.graph.snapshot();

            const vertices = snapshot.vertices;
            const n = vertices.length;

            if (n === 0) {
                throw new GraphValidationError(
                    "Cannot compute an empty graph"
                );
            }

            const index = new Map(
                vertices.map((vertex, i) => [vertex, i])
            );

            const distance = Array.from(
                { length: n },
                () => Array(n).fill(Infinity)
            );

            const next = Array.from(
                { length: n },
                () => Array(n).fill(null)
            );

            for (let i = 0; i < n; i++) {
                distance[i][i] = 0;
                next[i][i] = i;
            }

            for (const edge of snapshot.edges) {
                const i = index.get(edge.source);
                const j = index.get(edge.destination);

                if (edge.weight < distance[i][j]) {
                    distance[i][j] = edge.weight;
                    next[i][j] = j;
                }
            }

            let completedIterations = 0;

            for (let k = 0; k < n; k++) {
                for (let i = 0; i < n; i++) {
                    if (distance[i][k] === Infinity) {
                        continue;
                    }

                    for (let j = 0; j < n; j++) {
                        if (distance[k][j] === Infinity) {
                            continue;
                        }

                        const candidate =
                            distance[i][k] + distance[k][j];

                        if (!Number.isFinite(candidate)) {
                            throw new RangeError(
                                "Numeric overflow during path calculation"
                            );
                        }

                        if (candidate < distance[i][j]) {
                            distance[i][j] = candidate;
                            next[i][j] = next[i][k];
                        }
                    }
                }

                completedIterations++;

                this.emit("iteration", {
                    intermediateVertex: vertices[k],
                    completedIterations,
                    totalIterations: n
                });
            }

            for (let i = 0; i < n; i++) {
                if (distance[i][i] < 0) {
                    throw new NegativeCycleError(
                        `Negative cycle detected at ${vertices[i]}`
                    );
                }
            }

            // A result is published only after successful validation.
            this.result = Object.freeze({
                vertices: Object.freeze(vertices),
                distance,
                next,
                graphVersion: snapshot.version
            });

            this.cache.clear();

            this.emit("completed", {
                vertexCount: n,
                edgeCount: snapshot.edges.length
            });

            return this.result;
        } catch (error) {
            this.emit("failed", error);
            throw error;
        } finally {
            this.computing = false;
        }
    }

    ensureComputed() {
        if (!this.result ||
            this.result.graphVersion !== this.graph.version) {
            this.compute();
        }
    }

    getDistance(source, destination) {
        this.ensureComputed();

        const i = this.result.vertices.indexOf(source);
        const j = this.result.vertices.indexOf(destination);

        if (i === -1 || j === -1) {
            throw new GraphValidationError(
                "Unknown source or destination"
            );
        }

        return this.result.distance[i][j];
    }

    getPath(source, destination) {
        this.ensureComputed();

        const vertices = this.result.vertices;

        const i = vertices.indexOf(source);
        const j = vertices.indexOf(destination);

        if (i === -1 || j === -1) {
            throw new GraphValidationError(
                "Unknown source or destination"
            );
        }

        if (this.result.distance[i][j] === Infinity) {
            return [];
        }

        const cacheKey = `${i}:${j}`;

        if (this.cache.has(cacheKey)) {
            return [...this.cache.get(cacheKey)];
        }

        const path = [source];
        let current = i;

        for (let step = 0; step < vertices.length; step++) {
            if (current === j) {
                this.cache.set(cacheKey, path);
                return [...path];
            }

            current = this.result.next[current][j];

            if (current === null) {
                return [];
            }

            path.push(vertices[current]);
        }

        throw new NegativeCycleError(
            "Path reconstruction exceeded vertex limit"
        );
    }

    getDistanceMatrix() {
        this.ensureComputed();

        return this.result.distance.map(row => [...row]);
    }
}

async function computeAsync(engine) {
    if (!(engine instanceof FloydWarshallEngine)) {
        throw new TypeError("Invalid engine");
    }

    // Yield control before starting synchronous computation.
    // The algorithm itself remains CPU-bound.
    await new Promise(resolve => setImmediate(resolve));

    return engine.compute();
}

async function main() {
    const graph = new WeightedGraph();

    const cities = [
        ["Delhi", { region: "North" }],
        ["Agra", { region: "North" }],
        ["Jaipur", { region: "West" }],
        ["Lucknow", { region: "North" }],
        ["Kanpur", { region: "North" }],
        ["Mumbai", { region: "West" }]
    ];

    for (const [id, metadata] of cities) {
        graph.addVertex(id, metadata);
    }

    const connections = [
        ["Delhi", "Agra", 2],
        ["Delhi", "Jaipur", 5],
        ["Agra", "Jaipur", 1],
        ["Agra", "Lucknow", 4],
        ["Jaipur", "Lucknow", 2],
        ["Lucknow", "Kanpur", 1],
        ["Kanpur", "Mumbai", 8],
        ["Jaipur", "Mumbai", 12],
        ["Delhi", "Kanpur", 15]
    ];

    for (const edge of connections) {
        graph.addEdge(...edge);
    }

    const engine = new FloydWarshallEngine(graph);

    engine.on("iteration", event => {
        console.log(
            `Intermediate vertex: ${event.intermediateVertex} ` +
            `(${event.completedIterations}/${event.totalIterations})`
        );
    });

    engine.on("completed", event => {
        console.log(
            `\nComputed shortest paths for ${event.vertexCount} vertices`
        );
    });

    engine.on("failed", error => {
        console.error("Computation failed:", error.message);
    });

    await computeAsync(engine);

    console.log("\nSHORTEST PATH QUERIES");

    const queries = [
        ["Delhi", "Mumbai"],
        ["Delhi", "Kanpur"],
        ["Agra", "Mumbai"],
        ["Mumbai", "Delhi"]
    ];

    for (const [source, destination] of queries) {
        const distance = engine.getDistance(source, destination);
        const path = engine.getPath(source, destination);

        console.log(
            `${source} -> ${destination}:`,
            path.length
                ? `${path.join(" -> ")} | Distance: ${distance}`
                : "Unreachable"
        );
    }

    console.log("\nDYNAMIC GRAPH UPDATE");

    graph.addEdge("Delhi", "Mumbai", 3);

    // The engine detects the changed graph version.
    console.log(
        "Updated Delhi -> Mumbai:",
        engine.getDistance("Delhi", "Mumbai")
    );

    console.log(
        "Updated path:",
        engine.getPath("Delhi", "Mumbai").join(" -> ")
    );

    console.log("\nNEGATIVE CYCLE VALIDATION");

    const negativeGraph = new WeightedGraph();

    negativeGraph.addVertex("A");
    negativeGraph.addVertex("B");
    negativeGraph.addVertex("C");

    negativeGraph.addEdge("A", "B", 2);
    negativeGraph.addEdge("B", "C", -4);
    negativeGraph.addEdge("C", "A", 1);

    const negativeEngine = new FloydWarshallEngine(negativeGraph);

    try {
        negativeEngine.compute();
    } catch (error) {
        if (error instanceof NegativeCycleError) {
            console.log("Correctly rejected:", error.message);
        } else {
            throw error;
        }
    }

    console.log("\nDISCONNECTED GRAPH");

    const disconnected = new WeightedGraph();

    disconnected.addVertex("X");
    disconnected.addVertex("Y");
    disconnected.addVertex("Z");

    disconnected.addEdge("X", "Y", 5);

    const disconnectedEngine =
        new FloydWarshallEngine(disconnected);

    disconnectedEngine.compute();

    console.log(
        "X -> Z:",
        disconnectedEngine.getDistance("X", "Z")
    );

    console.log(
        "X -> Z path:",
        disconnectedEngine.getPath("X", "Z")
    );

    console.log("\nCOMPLEXITY");
    console.log("Time: O(V^3)");
    console.log("Space: O(V^2)");
    console.log("Path reconstruction: O(V) per uncached query");
}

main().catch(error => {
    console.error("Application failure:", error);
    process.exitCode = 1;
});
