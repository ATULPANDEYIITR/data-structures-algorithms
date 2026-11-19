"use strict";

const { EventEmitter } = require("node:events");

class Graph extends EventEmitter {
    constructor() {
        super();
        this.adjacency = new Map();
    }

    addVertex(vertex) {
        if (typeof vertex !== "string" || vertex.trim().length === 0) {
            throw new TypeError("Vertex must be a non-empty string.");
        }

        if (!this.adjacency.has(vertex)) {
            this.adjacency.set(vertex, new Set());
            this.emit("vertexAdded", { vertex });
        }
    }

    addEdge(source, destination) {
        this.addVertex(source);
        this.addVertex(destination);

        this.adjacency.get(source).add(destination);
        this.adjacency.get(destination).add(source);

        this.emit("edgeAdded", { source, destination });
    }

    removeEdge(source, destination) {
        this.validateVertex(source);
        this.validateVertex(destination);

        this.adjacency.get(source).delete(destination);
        this.adjacency.get(destination).delete(source);

        this.emit("edgeRemoved", { source, destination });
    }

    validateVertex(vertex) {
        if (!this.adjacency.has(vertex)) {
            throw new Error(`Unknown vertex: ${vertex}`);
        }
    }

    sortedNeighbors(vertex) {
        return [...this.adjacency.get(vertex)].sort();
    }

    bfs(start) {
        this.validateVertex(start);

        const visited = new Set([start]);
        const queue = [start];
        const traversal = [];

        // A head index avoids the O(n) cost of repeated Array.shift().
        let head = 0;

        this.emit("traversalStarted", { start });

        while (head < queue.length) {
            const current = queue[head++];

            traversal.push(current);
            this.emit("vertexVisited", { vertex: current });

            for (const neighbor of this.sortedNeighbors(current)) {
                if (!visited.has(neighbor)) {
                    visited.add(neighbor);
                    queue.push(neighbor);

                    this.emit("vertexDiscovered", {
                        vertex: neighbor,
                        parent: current
                    });
                }
            }
        }

        this.emit("traversalCompleted", {
            start,
            traversal
        });

        return traversal;
    }

    bfsLevels(start) {
        this.validateVertex(start);

        const distance = new Map([[start, 0]]);
        const queue = [start];
        let head = 0;

        while (head < queue.length) {
            const current = queue[head++];

            for (const neighbor of this.sortedNeighbors(current)) {
                if (!distance.has(neighbor)) {
                    distance.set(
                        neighbor,
                        distance.get(current) + 1
                    );

                    queue.push(neighbor);
                }
            }
        }

        return distance;
    }

    shortestPath(start, target) {
        this.validateVertex(start);
        this.validateVertex(target);

        if (start === target) {
            return [start];
        }

        const queue = [start];
        const parent = new Map([[start, null]]);
        let head = 0;

        while (head < queue.length) {
            const current = queue[head++];

            for (const neighbor of this.sortedNeighbors(current)) {
                if (parent.has(neighbor)) {
                    continue;
                }

                parent.set(neighbor, current);

                if (neighbor === target) {
                    const path = [];
                    let currentNode = target;

                    while (currentNode !== null) {
                        path.push(currentNode);
                        currentNode = parent.get(currentNode);
                    }

                    return path.reverse();
                }

                queue.push(neighbor);
            }
        }

        return null;
    }

    connectedComponents() {
        const visited = new Set();
        const components = [];

        const vertices = [...this.adjacency.keys()].sort();

        for (const vertex of vertices) {
            if (visited.has(vertex)) {
                continue;
            }

            const component = [];
            const queue = [vertex];
            let head = 0;

            visited.add(vertex);

            while (head < queue.length) {
                const current = queue[head++];
                component.push(current);

                for (const neighbor of this.sortedNeighbors(current)) {
                    if (!visited.has(neighbor)) {
                        visited.add(neighbor);
                        queue.push(neighbor);
                    }
                }
            }

            components.push(component);
        }

        return components;
    }

    isConnected() {
        return this.adjacency.size === 0 ||
            this.connectedComponents().length === 1;
    }

    async bfsAsync(start, options = {}) {
        this.validateVertex(start);

        const {
            signal,
            onVisit = async () => {}
        } = options;

        if (typeof onVisit !== "function") {
            throw new TypeError("onVisit must be a function.");
        }

        const visited = new Set([start]);
        const queue = [start];
        const traversal = [];
        let head = 0;

        while (head < queue.length) {
            if (signal?.aborted) {
                throw new Error("BFS traversal was cancelled.");
            }

            const current = queue[head++];

            traversal.push(current);
            await onVisit(current);

            for (const neighbor of this.sortedNeighbors(current)) {
                if (!visited.has(neighbor)) {
                    visited.add(neighbor);
                    queue.push(neighbor);
                }
            }
        }

        return traversal;
    }

    printGraph() {
        for (const vertex of [...this.adjacency.keys()].sort()) {
            console.log(
                `${vertex}: ${JSON.stringify(this.sortedNeighbors(vertex))}`
            );
        }
    }
}

function createSampleGraph() {
    const graph = new Graph();

    const edges = [
        ["A", "B"],
        ["A", "C"],
        ["B", "D"],
        ["B", "E"],
        ["C", "F"],
        ["E", "F"],
        ["G", "H"]
    ];

    for (const [source, destination] of edges) {
        graph.addEdge(source, destination);
    }

    graph.addVertex("I");

    return graph;
}

async function main() {
    const graph = createSampleGraph();

    console.log("BREADTH-FIRST SEARCH");
    console.log("====================");

    // Event-driven monitoring of traversal.
    graph.on("traversalStarted", ({ start }) => {
        console.log(`\nTraversal started at ${start}`);
    });

    graph.on("vertexVisited", ({ vertex }) => {
        console.log(`Visited: ${vertex}`);
    });

    graph.on("traversalCompleted", ({ traversal }) => {
        console.log("Traversal completed:", traversal);
    });

    console.log("\n1. Adjacency list");
    graph.printGraph();

    console.log("\n2. BFS traversal");
    console.log(graph.bfs("A"));

    console.log("\n3. Shortest-distance map");
    console.log(Object.fromEntries(graph.bfsLevels("A")));

    console.log("\n4. Shortest path");
    console.log(graph.shortestPath("A", "F"));

    console.log("\n5. Unreachable destination");
    console.log(graph.shortestPath("A", "H"));

    console.log("\n6. Connected components");
    console.log(graph.connectedComponents());

    console.log("\n7. Connectivity");
    console.log(graph.isConnected());

    console.log("\n8. Asynchronous traversal");
    const asyncResult = await graph.bfsAsync("A", {
        onVisit: async vertex => {
            await Promise.resolve();
            console.log(`Async processing: ${vertex}`);
        }
    });

    console.log("Async result:", asyncResult);

    console.log("\n9. Validation");
    try {
        graph.bfs("UNKNOWN");
    } catch (error) {
        console.log("Expected error:", error.message);
    }

    console.log("\n10. Cancellation");
    const controller = new AbortController();
    controller.abort();

    try {
        await graph.bfsAsync("A", {
            signal: controller.signal
        });
    } catch (error) {
        console.log("Expected cancellation:", error.message);
    }

    console.log("\n11. Correctness assertions");

    const testGraph = createSampleGraph();

    const assert = require("node:assert/strict");

    assert.deepEqual(
        testGraph.bfs("A"),
        ["A", "B", "C", "D", "E", "F"]
    );

    assert.deepEqual(
        testGraph.shortestPath("A", "F"),
        ["A", "C", "F"]
    );

    assert.equal(testGraph.bfsLevels("A").get("F"), 2);
    assert.equal(testGraph.shortestPath("A", "H"), null);
    assert.equal(testGraph.connectedComponents().length, 3);

    console.log("All tests passed.");
}

main().catch(error => {
    console.error("Application failure:", error.message);
    process.exitCode = 1;
});
