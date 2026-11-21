"use strict";

/*
 * Graph Cycle Detection Engine
 *
 * Supports:
 * 1. Directed DFS using recursion-stack state.
 * 2. Directed BFS using Kahn's algorithm.
 * 3. Undirected DFS using parent tracking.
 * 4. Undirected BFS using parent tracking.
 * 5. Undirected DSU using path compression and union by size.
 *
 * The engine also exposes an event-driven interface for
 * incremental edge registration and cycle evaluation.
 */

const GraphType = Object.freeze({
    DIRECTED: "directed",
    UNDIRECTED: "undirected"
});

class GraphValidationError extends Error {
    constructor(message) {
        super(message);
        this.name = "GraphValidationError";
    }
}

class DisjointSet {
    constructor(vertexCount) {
        if (!Number.isSafeInteger(vertexCount) || vertexCount < 0) {
            throw new GraphValidationError(
                "Vertex count must be a non-negative safe integer."
            );
        }

        this.parent = Array.from(
            { length: vertexCount },
            (_, index) => index
        );

        this.size = Array(vertexCount).fill(1);
        this.components = vertexCount;
    }

    validate(vertex) {
        if (
            !Number.isSafeInteger(vertex) ||
            vertex < 0 ||
            vertex >= this.parent.length
        ) {
            throw new GraphValidationError(
                `Invalid vertex: ${vertex}`
            );
        }
    }

    find(vertex) {
        this.validate(vertex);

        let root = vertex;

        while (root !== this.parent[root]) {
            root = this.parent[root];
        }

        // Iterative path compression avoids recursion overhead.
        while (vertex !== root) {
            const next = this.parent[vertex];
            this.parent[vertex] = root;
            vertex = next;
        }

        return root;
    }

    union(first, second) {
        let rootFirst = this.find(first);
        let rootSecond = this.find(second);

        if (rootFirst === rootSecond) {
            return false;
        }

        if (this.size[rootFirst] < this.size[rootSecond]) {
            [rootFirst, rootSecond] = [rootSecond, rootFirst];
        }

        this.parent[rootSecond] = rootFirst;
        this.size[rootFirst] += this.size[rootSecond];
        this.components--;

        return true;
    }
}

class Graph {
    constructor(vertexCount, type = GraphType.DIRECTED) {
        if (!Number.isSafeInteger(vertexCount) || vertexCount < 0) {
            throw new GraphValidationError(
                "Vertex count must be a non-negative safe integer."
            );
        }

        if (!Object.values(GraphType).includes(type)) {
            throw new GraphValidationError("Unsupported graph type.");
        }

        this.vertexCount = vertexCount;
        this.type = type;

        this.adjacency = Array.from(
            { length: vertexCount },
            () => []
        );

        this.edges = [];
        this.edgeCount = 0;
    }

    validateVertex(vertex) {
        if (
            !Number.isSafeInteger(vertex) ||
            vertex < 0 ||
            vertex >= this.vertexCount
        ) {
            throw new GraphValidationError(
                `Vertex ${vertex} is outside the graph.`
            );
        }
    }

    addEdge(source, destination) {
        this.validateVertex(source);
        this.validateVertex(destination);

        this.adjacency[source].push(destination);

        if (this.type === GraphType.UNDIRECTED) {
            this.adjacency[destination].push(source);
        }

        this.edges.push([source, destination]);
        this.edgeCount++;
    }

    detectDirectedDFS() {
        this.requireType(GraphType.DIRECTED);

        // 0 = white, 1 = gray, 2 = black.
        const state = new Uint8Array(this.vertexCount);
        const parent = new Int32Array(this.vertexCount);
        parent.fill(-1);

        const buildCycle = (vertex, ancestor) => {
            const path = [vertex];

            while (path[path.length - 1] !== ancestor) {
                const previous = parent[path[path.length - 1]];

                if (previous === -1) {
                    throw new Error("Invalid DFS parent state.");
                }

                path.push(previous);
            }

            path.reverse();
            path.push(ancestor);

            return path;
        };

        const dfs = (vertex) => {
            state[vertex] = 1;

            for (const neighbor of this.adjacency[vertex]) {
                if (state[neighbor] === 0) {
                    parent[neighbor] = vertex;

                    const cycle = dfs(neighbor);

                    if (cycle !== null) {
                        return cycle;
                    }
                } else if (state[neighbor] === 1) {
                    return buildCycle(vertex, neighbor);
                }
            }

            state[vertex] = 2;
            return null;
        };

        for (let vertex = 0; vertex < this.vertexCount; vertex++) {
            if (state[vertex] === 0) {
                const cycle = dfs(vertex);

                if (cycle !== null) {
                    return {
                        hasCycle: true,
                        algorithm: "Directed DFS",
                        cycle
                    };
                }
            }
        }

        return {
            hasCycle: false,
            algorithm: "Directed DFS",
            cycle: []
        };
    }

    detectDirectedBFS() {
        this.requireType(GraphType.DIRECTED);

        const indegree = new Int32Array(this.vertexCount);

        for (const neighbors of this.adjacency) {
            for (const neighbor of neighbors) {
                indegree[neighbor]++;
            }
        }

        const queue = new Int32Array(this.vertexCount);
        let head = 0;
        let tail = 0;

        for (let vertex = 0; vertex < this.vertexCount; vertex++) {
            if (indegree[vertex] === 0) {
                queue[tail++] = vertex;
            }
        }

        const order = [];

        while (head < tail) {
            const vertex = queue[head++];
            order.push(vertex);

            for (const neighbor of this.adjacency[vertex]) {
                indegree[neighbor]--;

                if (indegree[neighbor] === 0) {
                    queue[tail++] = neighbor;
                }
            }
        }

        return {
            hasCycle: order.length !== this.vertexCount,
            algorithm: "Kahn BFS",
            topologicalOrder: order
        };
    }

    detectUndirectedDFS() {
        this.requireType(GraphType.UNDIRECTED);

        const visited = new Uint8Array(this.vertexCount);

        const dfs = (vertex, parent) => {
            visited[vertex] = 1;

            for (const neighbor of this.adjacency[vertex]) {
                if (!visited[neighbor]) {
                    if (dfs(neighbor, vertex)) {
                        return true;
                    }
                } else if (neighbor !== parent) {
                    return true;
                }
            }

            return false;
        };

        for (let vertex = 0; vertex < this.vertexCount; vertex++) {
            if (!visited[vertex] && dfs(vertex, -1)) {
                return {
                    hasCycle: true,
                    algorithm: "Undirected DFS"
                };
            }
        }

        return {
            hasCycle: false,
            algorithm: "Undirected DFS"
        };
    }

    detectUndirectedBFS() {
        this.requireType(GraphType.UNDIRECTED);

        const visited = new Uint8Array(this.vertexCount);
        const parent = new Int32Array(this.vertexCount);
        parent.fill(-1);

        for (let start = 0; start < this.vertexCount; start++) {
            if (visited[start]) {
                continue;
            }

            const queue = [start];
            let head = 0;

            visited[start] = 1;

            while (head < queue.length) {
                const vertex = queue[head++];

                for (const neighbor of this.adjacency[vertex]) {
                    if (!visited[neighbor]) {
                        visited[neighbor] = 1;
                        parent[neighbor] = vertex;
                        queue.push(neighbor);
                    } else if (neighbor !== parent[vertex]) {
                        return {
                            hasCycle: true,
                            algorithm: "Undirected BFS"
                        };
                    }
                }
            }
        }

        return {
            hasCycle: false,
            algorithm: "Undirected BFS"
        };
    }

    detectUndirectedDSU() {
        this.requireType(GraphType.UNDIRECTED);

        const dsu = new DisjointSet(this.vertexCount);

        for (const [source, destination] of this.edges) {
            if (!dsu.union(source, destination)) {
                return {
                    hasCycle: true,
                    algorithm: "Disjoint Set Union",
                    components: dsu.components
                };
            }
        }

        return {
            hasCycle: false,
            algorithm: "Disjoint Set Union",
            components: dsu.components
        };
    }

    requireType(expected) {
        if (this.type !== expected) {
            throw new GraphValidationError(
                `Expected ${expected} graph, received ${this.type}.`
            );
        }
    }
}

/*
 * Event-driven graph monitor.
 *
 * Events are emitted after successful edge insertion.
 * Cycle evaluation is performed explicitly because directed
 * cycle detection cannot generally be maintained using DSU.
 */

class GraphMonitor {
    constructor(graph) {
        if (!(graph instanceof Graph)) {
            throw new TypeError("GraphMonitor requires a Graph.");
        }

        this.graph = graph;
        this.listeners = new Map();
        this.revision = 0;
    }

    on(eventName, listener) {
        if (typeof listener !== "function") {
            throw new TypeError("Listener must be a function.");
        }

        if (!this.listeners.has(eventName)) {
            this.listeners.set(eventName, new Set());
        }

        this.listeners.get(eventName).add(listener);

        return () => {
            this.listeners.get(eventName)?.delete(listener);
        };
    }

    emit(eventName, payload) {
        const listeners = this.listeners.get(eventName);

        if (!listeners) {
            return;
        }

        // Snapshot protects iteration from listener removal.
        for (const listener of [...listeners]) {
            try {
                listener(Object.freeze({ ...payload }));
            } catch (error) {
                // One listener must not prevent other listeners.
                process.stderr.write(
                    `Listener failure: ${error.message}\n`
                );
            }
        }
    }

    addEdge(source, destination) {
        this.graph.addEdge(source, destination);
        this.revision++;

        this.emit("edgeAdded", {
            source,
            destination,
            revision: this.revision
        });
    }

    async evaluate() {
        // A Promise provides an asynchronous service boundary.
        await Promise.resolve();

        const result = this.graph.type === GraphType.DIRECTED
            ? this.graph.detectDirectedDFS()
            : this.graph.detectUndirectedDSU();

        this.emit("evaluated", {
            revision: this.revision,
            result
        });

        return result;
    }
}

function assert(condition, message) {
    if (!condition) {
        throw new Error(`Test failed: ${message}`);
    }
}

async function runTests() {
    const directed = new Graph(4, GraphType.DIRECTED);

    for (const edge of [
        [0, 1],
        [1, 2],
        [2, 3],
        [3, 1]
    ]) {
        directed.addEdge(...edge);
    }

    assert(directed.detectDirectedDFS().hasCycle, "Directed DFS");
    assert(directed.detectDirectedBFS().hasCycle, "Directed BFS");

    const dag = new Graph(4, GraphType.DIRECTED);

    for (const edge of [[0, 1], [0, 2], [1, 3], [2, 3]]) {
        dag.addEdge(...edge);
    }

    assert(!dag.detectDirectedDFS().hasCycle, "Directed DAG DFS");
    assert(!dag.detectDirectedBFS().hasCycle, "Directed DAG BFS");

    const undirected = new Graph(4, GraphType.UNDIRECTED);

    for (const edge of [[0, 1], [1, 2], [2, 0], [2, 3]]) {
        undirected.addEdge(...edge);
    }

    assert(undirected.detectUndirectedDFS().hasCycle, "Undirected DFS");
    assert(undirected.detectUndirectedBFS().hasCycle, "Undirected BFS");
    assert(undirected.detectUndirectedDSU().hasCycle, "Undirected DSU");

    const tree = new Graph(5, GraphType.UNDIRECTED);

    for (const edge of [[0, 1], [0, 2], [1, 3], [1, 4]]) {
        tree.addEdge(...edge);
    }

    assert(!tree.detectUndirectedDFS().hasCycle, "Tree DFS");
    assert(!tree.detectUndirectedBFS().hasCycle, "Tree BFS");
    assert(!tree.detectUndirectedDSU().hasCycle, "Tree DSU");

    assert(
        new Graph(1, GraphType.DIRECTED)
            .detectDirectedDFS().hasCycle === false,
        "Empty edge graph"
    );

    const loop = new Graph(1, GraphType.UNDIRECTED);
    loop.addEdge(0, 0);
    assert(loop.detectUndirectedDSU().hasCycle, "Self-loop");

    const parallel = new Graph(2, GraphType.UNDIRECTED);
    parallel.addEdge(0, 1);
    parallel.addEdge(0, 1);
    assert(parallel.detectUndirectedDSU().hasCycle, "Parallel edges");

    const monitorGraph = new Graph(3, GraphType.DIRECTED);
    const monitor = new GraphMonitor(monitorGraph);

    let edgeEvents = 0;
    monitor.on("edgeAdded", () => edgeEvents++);

    monitor.addEdge(0, 1);
    monitor.addEdge(1, 2);
    monitor.addEdge(2, 0);

    assert(edgeEvents === 3, "Event delivery");

    const monitoredResult = await monitor.evaluate();
    assert(monitoredResult.hasCycle, "Asynchronous evaluation");

    const unsubscribe = monitor.on("edgeAdded", () => {
        throw new Error("Intentional listener error");
    });

    unsubscribe();

    let invalidRejected = false;

    try {
        directed.addEdge(0, 10);
    } catch (error) {
        invalidRejected = error instanceof GraphValidationError;
    }

    assert(invalidRejected, "Invalid vertex validation");

    console.log("All JavaScript tests passed.");
}

async function demonstrate() {
    console.log("\nDIRECTED GRAPH");

    const directed = new Graph(5, GraphType.DIRECTED);

    for (const edge of [
        [0, 1],
        [1, 2],
        [2, 3],
        [3, 1],
        [3, 4]
    ]) {
        directed.addEdge(...edge);
    }

    console.log(directed.detectDirectedDFS());
    console.log(directed.detectDirectedBFS());

    console.log("\nUNDIRECTED GRAPH");

    const undirected = new Graph(4, GraphType.UNDIRECTED);

    for (const edge of [[0, 1], [1, 2], [2, 0], [2, 3]]) {
        undirected.addEdge(...edge);
    }

    console.log(undirected.detectUndirectedDFS());
    console.log(undirected.detectUndirectedBFS());
    console.log(undirected.detectUndirectedDSU());
}

async function main() {
    await runTests();
    await demonstrate();
}

main().catch(error => {
    process.stderr.write(`${error.stack || error.message}\n`);
    process.exitCode = 1;
});
