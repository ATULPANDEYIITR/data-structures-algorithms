"use strict";

const { EventEmitter } = require("node:events");
const fs = require("node:fs/promises");

class Graph {
    constructor({ directed = false } = {}) {
        this.directed = directed;
        this.adjacency = new Map();
    }

    addVertex(vertex) {
        this.validateVertex(vertex);

        if (!this.adjacency.has(vertex)) {
            this.adjacency.set(vertex, new Set());
        }
    }

    validateVertex(vertex) {
        if (!Number.isSafeInteger(vertex)) {
            throw new TypeError("Vertices must be safe integers.");
        }
    }

    addEdge(source, destination) {
        this.validateVertex(source);
        this.validateVertex(destination);

        this.addVertex(source);
        this.addVertex(destination);

        this.adjacency.get(source).add(destination);

        if (!this.directed) {
            this.adjacency.get(destination).add(source);
        }
    }

    neighbors(vertex) {
        if (!this.adjacency.has(vertex)) {
            throw new Error(`Unknown vertex: ${vertex}`);
        }

        return this.adjacency.get(vertex);
    }

    get vertices() {
        return [...this.adjacency.keys()];
    }

    validate() {
        for (const [vertex, neighbors] of this.adjacency) {
            for (const neighbor of neighbors) {
                if (!this.adjacency.has(neighbor)) {
                    throw new Error(
                        `Invalid edge ${vertex} -> ${neighbor}`
                    );
                }

                if (
                    !this.directed &&
                    !this.adjacency.get(neighbor).has(vertex)
                ) {
                    throw new Error("Undirected edge is not symmetric.");
                }
            }
        }
    }
}


class DFSExplorer extends EventEmitter {
    constructor(graph) {
        super();

        this.graph = graph;
        this.explorationCount = 0;
    }

    recursive(start, maxDepth = Infinity) {
        this.validateStart(start);

        if (
            maxDepth !== Infinity &&
            (!Number.isInteger(maxDepth) || maxDepth < 0)
        ) {
            throw new RangeError("Invalid maximum depth.");
        }

        const visited = new Set();
        const order = [];

        const explore = (vertex, depth) => {
            visited.add(vertex);
            order.push(vertex);

            this.emit("visit", {
                vertex,
                depth,
                visitedCount: visited.size
            });

            if (depth >= maxDepth) {
                return;
            }

            for (const neighbor of this.graph.neighbors(vertex)) {
                if (!visited.has(neighbor)) {
                    explore(neighbor, depth + 1);
                }
            }
        };

        explore(start, 0);
        this.explorationCount += order.length;

        return order;
    }

    iterative(start) {
        this.validateStart(start);

        const visited = new Set([start]);
        const stack = [start];
        const order = [];

        while (stack.length > 0) {
            const vertex = stack.pop();
            order.push(vertex);

            this.emit("visit", {
                vertex,
                depth: null,
                visitedCount: visited.size
            });

            const neighbors = [...this.graph.neighbors(vertex)];

            for (let i = neighbors.length - 1; i >= 0; i--) {
                const neighbor = neighbors[i];

                if (!visited.has(neighbor)) {
                    // Mark when pushing to avoid duplicate stack entries.
                    visited.add(neighbor);
                    stack.push(neighbor);
                }
            }
        }

        this.explorationCount += order.length;
        return order;
    }

    validateStart(start) {
        if (!this.graph.adjacency.has(start)) {
            throw new Error(`Starting vertex ${start} does not exist.`);
        }
    }

    connectedComponents() {
        if (this.graph.directed) {
            throw new Error(
                "Connected components require an undirected graph."
            );
        }

        const visited = new Set();
        const components = [];

        for (const start of this.graph.vertices) {
            if (visited.has(start)) continue;

            const component = [];
            const stack = [start];
            visited.add(start);

            while (stack.length > 0) {
                const vertex = stack.pop();
                component.push(vertex);

                for (const neighbor of this.graph.neighbors(vertex)) {
                    if (!visited.has(neighbor)) {
                        visited.add(neighbor);
                        stack.push(neighbor);
                    }
                }
            }

            components.push(component);
        }

        return components;
    }

    hasPath(source, target) {
        this.validateStart(source);
        this.validateStart(target);

        const visited = new Set();
        const stack = [source];

        while (stack.length > 0) {
            const vertex = stack.pop();

            if (vertex === target) return true;
            if (visited.has(vertex)) continue;

            visited.add(vertex);

            for (const neighbor of this.graph.neighbors(vertex)) {
                if (!visited.has(neighbor)) {
                    stack.push(neighbor);
                }
            }
        }

        return false;
    }

    async exploreAsync(start, { signal } = {}) {
        this.validateStart(start);

        const visited = new Set([start]);
        const stack = [start];
        const order = [];

        while (stack.length > 0) {
            if (signal?.aborted) {
                throw new Error("Graph exploration was cancelled.");
            }

            const vertex = stack.pop();
            order.push(vertex);

            this.emit("visit", {
                vertex,
                visitedCount: visited.size
            });

            for (const neighbor of this.graph.neighbors(vertex)) {
                if (!visited.has(neighbor)) {
                    visited.add(neighbor);
                    stack.push(neighbor);
                }
            }

            // Yield control to the event loop for long-running traversals.
            await new Promise(resolve => setImmediate(resolve));
        }

        this.explorationCount += order.length;
        return order;
    }
}


class GraphRepository {
    constructor() {
        this.graph = new Graph();
        this.explorer = new DFSExplorer(this.graph);
    }

    loadEdges(edges) {
        if (!Array.isArray(edges)) {
            throw new TypeError("Edges must be an array.");
        }

        for (const edge of edges) {
            if (
                !Array.isArray(edge) ||
                edge.length !== 2
            ) {
                throw new TypeError("Each edge must contain two vertices.");
            }

            this.graph.addEdge(edge[0], edge[1]);
        }

        this.graph.validate();
    }

    async save(filename, data) {
        if (!filename.endsWith(".json")) {
            throw new Error("Only JSON output is permitted.");
        }

        const serialized = JSON.stringify(data, null, 2);
        await fs.writeFile(filename, serialized, {
            encoding: "utf8",
            mode: 0o600
        });
    }
}


async function main() {
    const repository = new GraphRepository();

    repository.loadEdges([
        [1, 2],
        [1, 3],
        [2, 4],
        [2, 5],
        [3, 6],
        [5, 6],
        [7, 8]
    ]);

    repository.graph.addVertex(9);

    const { graph, explorer } = repository;

    explorer.on("visit", event => {
        console.log(
            `Visiting ${event.vertex}; ` +
            `visited: ${event.visitedCount}`
        );
    });

    console.log("\nIterative DFS:");
    const traversal = explorer.iterative(1);
    console.log("Traversal:", traversal);

    console.log("\nRecursive DFS:");
    const recursive = explorer.recursive(1);
    console.log("Traversal:", recursive);

    console.log("\nConnected components:");
    const components = explorer.connectedComponents();
    console.log(components);

    console.log("\nPath evaluation:");
    console.log("1 -> 6:", explorer.hasPath(1, 6));
    console.log("1 -> 8:", explorer.hasPath(1, 8));

    console.log("\nAsynchronous exploration:");
    const asyncTraversal = await explorer.exploreAsync(7);

    const results = {
        graphType: graph.directed ? "directed" : "undirected",
        vertices: graph.vertices,
        traversal,
        recursive,
        components,
        asyncTraversal,
        explorationCount: explorer.explorationCount
    };

    await repository.save("dfs_results.json", results);

    console.log("\nResults saved to dfs_results.json");

    // Validate directed traversal and reject undirected-only operations.
    const directed = new Graph({ directed: true });
    directed.addEdge(10, 11);
    directed.addEdge(11, 12);

    const directedExplorer = new DFSExplorer(directed);

    console.log(
        "\nDirected traversal:",
        directedExplorer.iterative(10)
    );

    try {
        directedExplorer.connectedComponents();
    } catch (error) {
        console.log("Expected validation:", error.message);
    }

    // Self-loop and cycle handling.
    const cyclic = new Graph();
    cyclic.addEdge(20, 20);
    cyclic.addEdge(20, 21);
    cyclic.addEdge(21, 22);
    cyclic.addEdge(22, 20);

    console.log(
        "Cyclic graph traversal:",
        new DFSExplorer(cyclic).iterative(20)
    );
}


main().catch(error => {
    console.error("DFS execution failed:", error.message);
    process.exitCode = 1;
});
