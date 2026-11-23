"use strict";

const { EventEmitter } = require("node:events");

class GraphValidationError extends Error {}
class NegativeCycleError extends Error {}

class WeightedGraph {
    constructor() {
        this.vertices = new Set();
        this.adjacency = new Map();
        this.edges = [];
        this.revision = 0;
    }

    addVertex(vertex) {
        if (typeof vertex !== "string" || vertex.trim() === "") {
            throw new GraphValidationError(
                "Vertex must be a nonempty string."
            );
        }

        if (!this.vertices.has(vertex)) {
            this.vertices.add(vertex);
            this.adjacency.set(vertex, []);
            this.revision++;
        }

        return this;
    }

    addEdge(source, target, weight, bidirectional = false) {
        if (!Number.isFinite(weight)) {
            throw new GraphValidationError(
                "Weight must be a finite number."
            );
        }

        this.addVertex(source);
        this.addVertex(target);

        this.adjacency.get(source).push({ to: target, weight });
        this.edges.push({ from: source, to: target, weight });

        if (bidirectional) {
            this.adjacency.get(target).push({
                to: source,
                weight
            });

            this.edges.push({
                from: target,
                to: source,
                weight
            });
        }

        this.revision++;
        return this;
    }

    validate(source, target) {
        if (!this.vertices.has(source)) {
            throw new GraphValidationError(
                `Unknown source: ${source}`
            );
        }

        if (!this.vertices.has(target)) {
            throw new GraphValidationError(
                `Unknown target: ${target}`
            );
        }
    }

    get hasNegativeEdges() {
        return this.edges.some(edge => edge.weight < 0);
    }

    reconstruct(previous, source, target) {
        if (source !== target && previous.get(target) === undefined) {
            return [];
        }

        const path = [];
        const visited = new Set();
        let current = target;

        while (current !== undefined) {
            if (visited.has(current)) {
                throw new Error("Invalid predecessor cycle.");
            }

            visited.add(current);
            path.push(current);

            if (current === source) {
                return path.reverse();
            }

            current = previous.get(current);
        }

        return [];
    }

    dijkstra(source, target) {
        this.validate(source, target);

        if (this.hasNegativeEdges) {
            throw new GraphValidationError(
                "Dijkstra requires nonnegative edge weights."
            );
        }

        const distances = new Map();
        const previous = new Map();
        const visited = new Set();

        for (const vertex of this.vertices) {
            distances.set(vertex, Infinity);
        }

        distances.set(source, 0);

        // A binary heap avoids repeatedly sorting the complete queue.
        const heap = new MinHeap();
        heap.push({ vertex: source, distance: 0 });

        while (!heap.isEmpty()) {
            const current = heap.pop();
            const vertex = current.vertex;

            if (visited.has(vertex)) continue;

            visited.add(vertex);

            if (vertex === target) break;

            for (const edge of this.adjacency.get(vertex)) {
                if (visited.has(edge.to)) continue;

                const candidate = current.distance + edge.weight;

                if (candidate < distances.get(edge.to)) {
                    distances.set(edge.to, candidate);
                    previous.set(edge.to, vertex);

                    heap.push({
                        vertex: edge.to,
                        distance: candidate
                    });
                }
            }
        }

        return this.createResult(
            source, target, distances, previous, "Dijkstra"
        );
    }

    bellmanFord(source, target) {
        this.validate(source, target);

        const distances = new Map();
        const previous = new Map();

        for (const vertex of this.vertices) {
            distances.set(vertex, Infinity);
        }

        distances.set(source, 0);

        const count = this.vertices.size;

        for (let iteration = 0; iteration < count - 1; iteration++) {
            let changed = false;

            for (const edge of this.edges) {
                const sourceDistance = distances.get(edge.from);

                if (sourceDistance === Infinity) continue;

                const candidate = sourceDistance + edge.weight;

                if (candidate < distances.get(edge.to)) {
                    distances.set(edge.to, candidate);
                    previous.set(edge.to, edge.from);
                    changed = true;
                }
            }

            if (!changed) break;
        }

        for (const edge of this.edges) {
            if (
                distances.get(edge.from) !== Infinity &&
                distances.get(edge.from) + edge.weight <
                    distances.get(edge.to)
            ) {
                throw new NegativeCycleError(
                    "Reachable negative cycle detected."
                );
            }
        }

        return this.createResult(
            source, target, distances, previous, "Bellman-Ford"
        );
    }

    createResult(source, target, distances, previous, algorithm) {
        const distance = distances.get(target);

        return Object.freeze({
            source,
            target,
            distance,
            path: Object.freeze(
                distance === Infinity
                    ? []
                    : this.reconstruct(previous, source, target)
            ),
            algorithm,
            graphRevision: this.revision
        });
    }

    selectAlgorithm() {
        return this.hasNegativeEdges
            ? "bellman-ford"
            : "dijkstra";
    }

    shortestPath(source, target) {
        const algorithm = this.selectAlgorithm();

        return algorithm === "dijkstra"
            ? this.dijkstra(source, target)
            : this.bellmanFord(source, target);
    }
}

class MinHeap {
    constructor() {
        this.items = [];
    }

    isEmpty() {
        return this.items.length === 0;
    }

    push(item) {
        this.items.push(item);
        let index = this.items.length - 1;

        while (index > 0) {
            const parent = Math.floor((index - 1) / 2);

            if (
                this.items[parent].distance <= item.distance
            ) break;

            this.items[index] = this.items[parent];
            index = parent;
        }

        this.items[index] = item;
    }

    pop() {
        if (this.isEmpty()) return undefined;

        const minimum = this.items[0];
        const last = this.items.pop();

        if (this.items.length === 0) return minimum;

        let index = 0;

        while (true) {
            const left = index * 2 + 1;
            const right = left + 1;

            if (left >= this.items.length) break;

            let smaller = left;

            if (
                right < this.items.length &&
                this.items[right].distance <
                    this.items[left].distance
            ) {
                smaller = right;
            }

            if (
                this.items[smaller].distance >= last.distance
            ) break;

            this.items[index] = this.items[smaller];
            index = smaller;
        }

        this.items[index] = last;
        return minimum;
    }
}

class RoutingService extends EventEmitter {
    constructor(graph) {
        super();
        this.graph = graph;
    }

    async findRoute(source, target) {
        this.emit("route:requested", { source, target });

        try {
            // Promise-based execution permits integration with
            // asynchronous routing and application workflows.
            const result = await Promise.resolve().then(
                () => this.graph.shortestPath(source, target)
            );

            this.emit("route:completed", result);
            return result;
        } catch (error) {
            this.emit("route:failed", {
                source,
                target,
                message: error.message
            });

            throw error;
        }
    }
}

async function main() {
    const graph = new WeightedGraph();

    graph
        .addEdge("Delhi", "Jaipur", 280)
        .addEdge("Delhi", "Agra", 230)
        .addEdge("Jaipur", "Mumbai", 1140)
        .addEdge("Agra", "Bhopal", 540)
        .addEdge("Bhopal", "Mumbai", 780)
        .addEdge("Jaipur", "Agra", 240)
        .addEdge("Agra", "Jaipur", 250)
        .addEdge("Delhi", "Chandigarh", 250)
        .addEdge("Chandigarh", "Jaipur", 480);

    const service = new RoutingService(graph);

    service.on("route:requested", request => {
        console.log("Request:", request);
    });

    service.on("route:completed", result => {
        console.log("Completed:", result);
    });

    service.on("route:failed", failure => {
        console.error("Failed:", failure);
    });

    const route = await service.findRoute("Delhi", "Mumbai");

    console.log(
        `Shortest distance: ${route.distance}`
    );

    console.log(
        `Route: ${route.path.join(" -> ")}`
    );

    // Negative edges change algorithm selection.
    const negativeGraph = new WeightedGraph();

    negativeGraph
        .addEdge("A", "B", 4)
        .addEdge("A", "C", 5)
        .addEdge("B", "C", -3)
        .addEdge("C", "D", 4)
        .addEdge("B", "D", 8);

    const negativeService = new RoutingService(negativeGraph);

    const negativeRoute = await negativeService.findRoute("A", "D");

    console.log("\nNegative-edge route:", negativeRoute);

    // Unreachable vertices return Infinity and an empty path.
    graph.addVertex("Kolkata");

    const unreachable = await service.findRoute(
        "Delhi",
        "Kolkata"
    );

    console.log("\nUnreachable:", unreachable);

    // Dijkstra must reject negative weights.
    try {
        negativeGraph.dijkstra("A", "D");
    } catch (error) {
        console.log("\nDijkstra rejection:", error.message);
    }

    // Reachable negative-cycle detection.
    const cycleGraph = new WeightedGraph();

    cycleGraph
        .addEdge("A", "B", 2)
        .addEdge("B", "C", -4)
        .addEdge("C", "B", 1)
        .addEdge("A", "D", 5);

    try {
        cycleGraph.bellmanFord("A", "D");
    } catch (error) {
        console.log("\nCycle detection:", error.message);
    }

    console.log("\nAll examples executed.");
}

main().catch(error => {
    console.error("Application failure:", error.message);
    process.exitCode = 1;
});
