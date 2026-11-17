"use strict";

/*
 * Graph Introduction
 *
 * A graph consists of vertices and edges.
 * This implementation demonstrates:
 * - Directed and undirected graphs.
 * - Weighted and unweighted graphs.
 * - Adjacency-list and adjacency-matrix representations.
 * - BFS and DFS traversal.
 * - Dijkstra shortest paths.
 * - Event-driven graph modifications.
 * - Asynchronous graph processing.
 */

const { EventEmitter } = require("node:events");
const { writeFile, readFile, unlink } = require("node:fs/promises");

class GraphError extends Error {}

class VertexNotFoundError extends GraphError {}

class NegativeWeightError extends GraphError {}

class Graph {
    constructor({
        directed = false,
        weighted = false
    } = {}) {
        this.directed = directed;
        this.weighted = weighted;
        this.adjacency = new Map();
        this.events = new EventEmitter();
        this.version = 0;
    }

    validateVertex(vertex) {
        if (
            typeof vertex !== "string" ||
            vertex.trim().length === 0
        ) {
            throw new TypeError(
                "Vertex must be a non-empty string."
            );
        }
    }

    validateWeight(weight) {
        if (
            typeof weight !== "number" ||
            !Number.isFinite(weight)
        ) {
            throw new TypeError(
                "Edge weight must be a finite number."
            );
        }

        if (!this.weighted && weight !== 1) {
            throw new GraphError(
                "Unweighted graphs only accept weight 1."
            );
        }
    }

    addVertex(vertex) {
        this.validateVertex(vertex);

        if (this.adjacency.has(vertex)) {
            return false;
        }

        this.adjacency.set(vertex, new Map());
        this.version++;

        this.events.emit("vertexAdded", {
            vertex,
            version: this.version
        });

        return true;
    }

    addEdge(source, destination, weight = 1) {
        this.validateVertex(source);
        this.validateVertex(destination);
        this.validateWeight(weight);

        this.addVertex(source);
        this.addVertex(destination);

        const previous = this.adjacency
            .get(source)
            .get(destination);

        this.adjacency.get(source).set(destination, weight);

        if (!this.directed) {
            this.adjacency
                .get(destination)
                .set(source, weight);
        }

        this.version++;

        this.events.emit("edgeAdded", {
            source,
            destination,
            weight,
            updated: previous !== undefined,
            version: this.version
        });
    }

    removeEdge(source, destination) {
        this.requireVertex(source);
        this.requireVertex(destination);

        const removed = this.adjacency
            .get(source)
            .delete(destination);

        if (!this.directed) {
            this.adjacency
                .get(destination)
                .delete(source);
        }

        if (removed) {
            this.version++;
            this.events.emit("edgeRemoved", {
                source,
                destination,
                version: this.version
            });
        }

        return removed;
    }

    removeVertex(vertex) {
        this.requireVertex(vertex);

        this.adjacency.delete(vertex);

        for (const neighbors of this.adjacency.values()) {
            neighbors.delete(vertex);
        }

        this.version++;

        this.events.emit("vertexRemoved", {
            vertex,
            version: this.version
        });
    }

    requireVertex(vertex) {
        if (!this.adjacency.has(vertex)) {
            throw new VertexNotFoundError(
                `Vertex does not exist: ${vertex}`
            );
        }
    }

    get vertexCount() {
        return this.adjacency.size;
    }

    get edgeCount() {
        let count = 0;

        for (const neighbors of this.adjacency.values()) {
            count += neighbors.size;
        }

        return this.directed ? count : count / 2;
    }

    getVertices() {
        return [...this.adjacency.keys()].sort();
    }

    getEdges() {
        const result = [];

        for (const source of this.getVertices()) {
            const neighbors = this.adjacency.get(source);

            for (const destination of [...neighbors.keys()].sort()) {
                if (!this.directed && source > destination) {
                    continue;
                }

                result.push({
                    source,
                    destination,
                    weight: neighbors.get(destination)
                });
            }
        }

        return result;
    }

    adjacencyList() {
        return Object.fromEntries(
            this.getVertices().map(vertex => [
                vertex,
                Object.fromEntries(
                    [...this.adjacency.get(vertex).entries()]
                        .sort(([a], [b]) => a.localeCompare(b))
                )
            ])
        );
    }

    adjacencyMatrix() {
        const vertices = this.getVertices();
        const index = new Map(
            vertices.map((vertex, i) => [vertex, i])
        );

        const matrix = Array.from(
            { length: vertices.length },
            () => Array(vertices.length).fill(null)
        );

        for (const [source, neighbors] of this.adjacency) {
            for (const [destination, weight] of neighbors) {
                matrix[index.get(source)][index.get(destination)] =
                    weight;
            }
        }

        return { vertices, matrix };
    }

    bfs(start) {
        this.requireVertex(start);

        const queue = [start];
        const visited = new Set([start]);
        const result = [];

        let head = 0;

        while (head < queue.length) {
            const current = queue[head++];
            result.push(current);

            const neighbors = [
                ...this.adjacency.get(current).keys()
            ].sort();

            for (const neighbor of neighbors) {
                if (!visited.has(neighbor)) {
                    visited.add(neighbor);
                    queue.push(neighbor);
                }
            }
        }

        return result;
    }

    dfs(start) {
        this.requireVertex(start);

        const stack = [start];
        const visited = new Set();
        const result = [];

        while (stack.length > 0) {
            const current = stack.pop();

            if (visited.has(current)) {
                continue;
            }

            visited.add(current);
            result.push(current);

            const neighbors = [
                ...this.adjacency.get(current).keys()
            ].sort().reverse();

            for (const neighbor of neighbors) {
                if (!visited.has(neighbor)) {
                    stack.push(neighbor);
                }
            }
        }

        return result;
    }

    inDegree(vertex) {
        this.requireVertex(vertex);

        let count = 0;

        for (const neighbors of this.adjacency.values()) {
            if (neighbors.has(vertex)) {
                count++;
            }
        }

        return count;
    }

    outDegree(vertex) {
        this.requireVertex(vertex);
        return this.adjacency.get(vertex).size;
    }

    async dijkstra(start) {
        this.requireVertex(start);

        for (const edge of this.getEdges()) {
            if (edge.weight < 0) {
                throw new NegativeWeightError(
                    "Dijkstra requires non-negative edge weights."
                );
            }
        }

        const distances = new Map(
            this.getVertices().map(vertex => [
                vertex,
                Infinity
            ])
        );

        distances.set(start, 0);

        // A binary heap supports efficient priority extraction.
        const heap = new MinHeap();
        heap.push({ vertex: start, distance: 0 });

        while (!heap.isEmpty()) {
            const current = heap.pop();

            if (
                current.distance !==
                distances.get(current.vertex)
            ) {
                continue;
            }

            for (const [neighbor, weight] of
                this.adjacency.get(current.vertex)) {

                const candidate = current.distance + weight;

                if (candidate < distances.get(neighbor)) {
                    distances.set(neighbor, candidate);

                    heap.push({
                        vertex: neighbor,
                        distance: candidate
                    });
                }
            }
        }

        return Object.fromEntries(distances);
    }

    serialize() {
        return {
            directed: this.directed,
            weighted: this.weighted,
            vertices: this.getVertices(),
            edges: this.getEdges()
        };
    }

    static deserialize(data) {
        if (
            !data ||
            typeof data !== "object" ||
            !Array.isArray(data.vertices) ||
            !Array.isArray(data.edges) ||
            typeof data.directed !== "boolean" ||
            typeof data.weighted !== "boolean"
        ) {
            throw new GraphError("Invalid graph document.");
        }

        const graph = new Graph({
            directed: data.directed,
            weighted: data.weighted
        });

        for (const vertex of data.vertices) {
            graph.addVertex(vertex);
        }

        for (const edge of data.edges) {
            if (!edge || typeof edge !== "object") {
                throw new GraphError("Invalid edge record.");
            }

            graph.addEdge(
                edge.source,
                edge.destination,
                edge.weight
            );
        }

        return graph;
    }

    async save(filename) {
        // The filename is supplied by the application, not user input.
        await writeFile(
            filename,
            JSON.stringify(this.serialize(), null, 2),
            { encoding: "utf8", mode: 0o600 }
        );
    }

    static async load(filename) {
        const content = await readFile(filename, "utf8");
        return Graph.deserialize(JSON.parse(content));
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
            ) {
                break;
            }

            this.items[index] = this.items[parent];
            index = parent;
        }

        this.items[index] = item;
    }

    pop() {
        if (this.isEmpty()) {
            throw new GraphError("Cannot pop an empty heap.");
        }

        const minimum = this.items[0];
        const last = this.items.pop();

        if (this.items.length > 0) {
            let index = 0;

            while (true) {
                const left = index * 2 + 1;
                const right = left + 1;
                let smallest = index;

                if (
                    left < this.items.length &&
                    this.items[left].distance <
                    this.items[smallest].distance
                ) {
                    smallest = left;
                }

                if (
                    right < this.items.length &&
                    this.items[right].distance <
                    this.items[smallest].distance
                ) {
                    smallest = right;
                }

                if (smallest === index) {
                    break;
                }

                this.items[index] = this.items[smallest];
                index = smallest;
            }

            this.items[index] = last;
        }

        return minimum;
    }
}

async function main() {
    console.log("\nGRAPH INTRODUCTION");
    console.log("=".repeat(55));

    // Event-driven graph construction.
    const network = new Graph({
        directed: false,
        weighted: true
    });

    network.events.on("edgeAdded", event => {
        console.log(
            `EVENT: ${event.source} -- ${event.destination}, ` +
            `weight=${event.weight}`
        );
    });

    network.addEdge("A", "B", 4);
    network.addEdge("A", "C", 2);
    network.addEdge("B", "C", 1);
    network.addEdge("B", "D", 5);
    network.addEdge("C", "D", 8);
    network.addEdge("D", "E", 2);

    console.log("\n1. GRAPH STRUCTURE");
    console.log("Vertices:", network.getVertices());
    console.log("Edges:", network.getEdges());
    console.log("Vertex count:", network.vertexCount);
    console.log("Edge count:", network.edgeCount);

    console.log("\n2. ADJACENCY LIST");
    console.log(JSON.stringify(network.adjacencyList(), null, 2));

    console.log("\n3. ADJACENCY MATRIX");
    const representation = network.adjacencyMatrix();
    console.log("Order:", representation.vertices);
    console.log(representation.matrix);

    console.log("\n4. GRAPH TRAVERSALS");
    console.log("BFS:", network.bfs("A"));
    console.log("DFS:", network.dfs("A"));

    console.log("\n5. SHORTEST PATH DISTANCES");
    console.log(await network.dijkstra("A"));

    console.log("\n6. DIRECTED GRAPH");

    const directed = new Graph({
        directed: true
    });

    directed.addEdge("Research", "Design");
    directed.addEdge("Design", "Implementation");
    directed.addEdge("Implementation", "Testing");

    console.log("BFS:", directed.bfs("Research"));
    console.log("In-degree of Testing:", directed.inDegree("Testing"));
    console.log("Out-degree of Design:", directed.outDegree("Design"));

    console.log("\n7. GRAPH PERSISTENCE");

    const filename = "graph_example.json";

    try {
        await network.save(filename);

        const restored = await Graph.load(filename);

        console.log("Restored vertices:", restored.getVertices());
        console.log("Restored edge count:", restored.edgeCount);

        await unlink(filename);
    } catch (error) {
        console.error("Persistence error:", error.message);
        throw error;
    }

    console.log("\n8. EDGE CASES");

    try {
        network.bfs("UNKNOWN");
    } catch (error) {
        console.log("Unknown vertex:", error.message);
    }

    try {
        network.addEdge("A", "B", NaN);
    } catch (error) {
        console.log("Invalid weight:", error.message);
    }

    const negative = new Graph({
        directed: true,
        weighted: true
    });

    negative.addEdge("X", "Y", -5);

    try {
        await negative.dijkstra("X");
    } catch (error) {
        console.log("Shortest path restriction:", error.message);
    }

    // Assertions verify the expected behavior.
    if (network.vertexCount !== 5) {
        throw new Error("Unexpected vertex count.");
    }

    if (network.edgeCount !== 6) {
        throw new Error("Unexpected edge count.");
    }

    if (network.bfs("A")[0] !== "A") {
        throw new Error("BFS validation failed.");
    }

    console.log("\nAll graph demonstrations completed successfully.");
}

main().catch(error => {
    console.error("Application failure:", error);
    process.exitCode = 1;
});
