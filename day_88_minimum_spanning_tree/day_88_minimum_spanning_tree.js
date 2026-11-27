"use strict";

/**
 * Minimum Spanning Tree - Event-Driven Network Planner
 *
 * Features:
 * - Weighted undirected graph
 * - Kruskal and Prim algorithms
 * - Disjoint Set Union
 * - Dynamic network modifications
 * - Event-driven change notifications
 * - Optimistic version checking
 * - Minimum spanning forest
 * - Network policy evaluation
 * - Alternative connection analysis
 *
 * Runtime: Node.js 18+
 * Dependencies: Node.js standard library only
 */

const { EventEmitter } = require("node:events");
const assert = require("node:assert/strict");

class GraphValidationError extends Error {}
class DisconnectedGraphError extends Error {}
class VersionConflictError extends Error {}
class NetworkPolicyError extends Error {}


class DisjointSet {
    constructor(vertices) {
        this.parent = new Map();
        this.rank = new Map();
        this.components = 0;

        for (const vertex of vertices) {
            this.parent.set(vertex, vertex);
            this.rank.set(vertex, 0);
            this.components++;
        }
    }

    find(vertex) {
        if (!this.parent.has(vertex)) {
            throw new GraphValidationError(
                `Unknown vertex: ${vertex}`
            );
        }

        const parent = this.parent.get(vertex);

        if (parent !== vertex) {
            this.parent.set(vertex, this.find(parent));
        }

        return this.parent.get(vertex);
    }

    union(first, second) {
        let a = this.find(first);
        let b = this.find(second);

        if (a === b) return false;

        const rankA = this.rank.get(a);
        const rankB = this.rank.get(b);

        if (rankA < rankB) {
            [a, b] = [b, a];
        }

        this.parent.set(b, a);

        if (rankA === rankB) {
            this.rank.set(a, this.rank.get(a) + 1);
        }

        this.components--;
        return true;
    }
}


class MinHeap {
    constructor() {
        this.items = [];
    }

    get size() {
        return this.items.length;
    }

    push(item) {
        const items = this.items;
        items.push(item);

        let index = items.length - 1;

        while (index > 0) {
            const parent = Math.floor((index - 1) / 2);

            if (this.compare(items[parent], item) <= 0) break;

            items[index] = items[parent];
            index = parent;
        }

        items[index] = item;
    }

    compare(a, b) {
        return (
            a.weight - b.weight ||
            a.source.localeCompare(b.source) ||
            a.destination.localeCompare(b.destination)
        );
    }

    pop() {
        if (this.items.length === 0) return undefined;

        const root = this.items[0];
        const last = this.items.pop();

        if (this.items.length > 0) {
            let index = 0;

            while (true) {
                const left = 2 * index + 1;
                const right = left + 1;

                if (left >= this.items.length) break;

                let smallest = left;

                if (
                    right < this.items.length &&
                    this.compare(
                        this.items[right],
                        this.items[left]
                    ) < 0
                ) {
                    smallest = right;
                }

                if (
                    this.compare(
                        this.items[smallest],
                        last
                    ) >= 0
                ) break;

                this.items[index] = this.items[smallest];
                index = smallest;
            }

            this.items[index] = last;
        }

        return root;
    }
}


class NetworkPolicy {
    constructor({
        requireConnected = true,
        maximumTotalCost = Infinity,
        maximumIndividualCost = Infinity,
        forbiddenConnections = [],
        mandatoryConnections = []
    } = {}) {
        this.requireConnected = requireConnected;
        this.maximumTotalCost = maximumTotalCost;
        this.maximumIndividualCost = maximumIndividualCost;

        this.forbiddenConnections = new Set(
            forbiddenConnections.map(NetworkPolicy.key)
        );

        this.mandatoryConnections = new Set(
            mandatoryConnections.map(NetworkPolicy.key)
        );

        if (
            maximumTotalCost < 0 ||
            maximumIndividualCost < 0
        ) {
            throw new NetworkPolicyError(
                "Cost limits cannot be negative."
            );
        }
    }

    static key(source, destination) {
        if (Array.isArray(source)) {
            [source, destination] = source;
        }

        return [source, destination].sort().join("\u0000");
    }

    evaluate(result) {
        const violations = [];

        if (
            this.requireConnected &&
            !result.connected
        ) {
            violations.push("Network is disconnected.");
        }

        if (result.totalCost > this.maximumTotalCost) {
            violations.push("Total cost exceeds policy.");
        }

        for (const edge of result.edges) {
            if (edge.weight > this.maximumIndividualCost) {
                violations.push(
                    `Connection ${edge.source}-${edge.destination} ` +
                    "exceeds the individual cost limit."
                );
            }

            const key = NetworkPolicy.key(
                edge.source,
                edge.destination
            );

            if (this.forbiddenConnections.has(key)) {
                violations.push(
                    `Forbidden connection selected: ${key}`
                );
            }
        }

        for (const required of this.mandatoryConnections) {
            if (
                !result.edges.some(
                    edge =>
                        NetworkPolicy.key(
                            edge.source,
                            edge.destination
                        ) === required
                )
            ) {
                violations.push(
                    `Mandatory connection missing: ${required}`
                );
            }
        }

        return {
            eligible: violations.length === 0,
            violations
        };
    }
}


class NetworkPlanner extends EventEmitter {
    #vertices = new Set();
    #edges = new Map();
    #version = 0;

    constructor(name) {
        super();

        if (!name || !name.trim()) {
            throw new GraphValidationError(
                "Network name is required."
            );
        }

        this.name = name;
    }

    get version() {
        return this.#version;
    }

    static edgeKey(source, destination) {
        return [source, destination]
            .sort()
            .join("\u0000");
    }

    #validateWeight(weight) {
        if (
            typeof weight !== "number" ||
            !Number.isFinite(weight) ||
            weight < 0
        ) {
            throw new GraphValidationError(
                "Weight must be a finite nonnegative number."
            );
        }
    }

    addVertex(vertex, expectedVersion = this.#version) {
        this.#checkVersion(expectedVersion);

        if (
            typeof vertex !== "string" ||
            vertex.trim().length === 0
        ) {
            throw new GraphValidationError(
                "Vertex must be a nonempty string."
            );
        }

        if (this.#vertices.has(vertex)) {
            return false;
        }

        this.#vertices.add(vertex);
        this.#version++;

        this.emit("vertexAdded", {
            vertex,
            version: this.#version
        });

        return true;
    }

    addConnection(
        source,
        destination,
        weight,
        expectedVersion = this.#version
    ) {
        this.#checkVersion(expectedVersion);
        this.#validateWeight(weight);

        if (
            typeof source !== "string" ||
            typeof destination !== "string" ||
            !source.trim() ||
            !destination.trim() ||
            source === destination
        ) {
            throw new GraphValidationError(
                "Invalid connection endpoints."
            );
        }

        const key = NetworkPlanner.edgeKey(
            source,
            destination
        );

        if (this.#edges.has(key)) {
            throw new GraphValidationError(
                "Duplicate undirected connection."
            );
        }

        this.#vertices.add(source);
        this.#vertices.add(destination);

        const edge = Object.freeze({
            source,
            destination,
            weight
        });

        this.#edges.set(key, edge);
        this.#version++;

        this.emit("connectionAdded", {
            edge,
            version: this.#version
        });

        return edge;
    }

    #checkVersion(expectedVersion) {
        if (expectedVersion !== this.#version) {
            throw new VersionConflictError(
                `Expected version ${expectedVersion}, ` +
                `actual version ${this.#version}.`
            );
        }
    }

    snapshot() {
        return Object.freeze({
            version: this.#version,
            vertices: Object.freeze(
                [...this.#vertices].sort()
            ),
            edges: Object.freeze(
                [...this.#edges.values()]
            )
        });
    }

    kruskal(snapshot = this.snapshot()) {
        const dsu = new DisjointSet(snapshot.vertices);

        const sorted = [...snapshot.edges].sort(
            (a, b) =>
                a.weight - b.weight ||
                NetworkPlanner.edgeKey(
                    a.source,
                    a.destination
                ).localeCompare(
                    NetworkPlanner.edgeKey(
                        b.source,
                        b.destination
                    )
                )
        );

        const selected = [];

        for (const edge of sorted) {
            if (dsu.union(edge.source, edge.destination)) {
                selected.push(edge);
            }

            if (dsu.components <= 1) break;
        }

        return this.#result(
            "kruskal",
            snapshot,
            selected,
            dsu.components
        );
    }

    prim(snapshot = this.snapshot()) {
        const adjacency = new Map(
            snapshot.vertices.map(vertex => [vertex, []])
        );

        for (const edge of snapshot.edges) {
            adjacency.get(edge.source).push({
                vertex: edge.destination,
                weight: edge.weight
            });

            adjacency.get(edge.destination).push({
                vertex: edge.source,
                weight: edge.weight
            });
        }

        const visited = new Set();
        const selected = [];
        const heap = new MinHeap();
        let components = 0;

        for (const start of snapshot.vertices) {
            if (visited.has(start)) continue;

            components++;
            visited.add(start);

            for (const neighbor of adjacency.get(start)) {
                heap.push({
                    source: start,
                    destination: neighbor.vertex,
                    weight: neighbor.weight
                });
            }

            while (heap.size > 0) {
                const edge = heap.pop();

                if (visited.has(edge.destination)) continue;

                visited.add(edge.destination);
                selected.push(edge);

                for (
                    const neighbor of
                    adjacency.get(edge.destination)
                ) {
                    if (!visited.has(neighbor.vertex)) {
                        heap.push({
                            source: edge.destination,
                            destination: neighbor.vertex,
                            weight: neighbor.weight
                        });
                    }
                }
            }
        }

        return this.#result(
            "prim",
            snapshot,
            selected,
            components
        );
    }

    #result(algorithm, snapshot, edges, components) {
        const totalCost = edges.reduce(
            (sum, edge) => sum + edge.weight,
            0
        );

        return Object.freeze({
            network: this.name,
            algorithm,
            version: snapshot.version,
            edges: Object.freeze([...edges]),
            totalCost,
            vertexCount: snapshot.vertices.length,
            componentCount: components,
            connected: components <= 1
        });
    }

    plan({
        algorithm = "kruskal",
        policy = new NetworkPolicy()
    } = {}) {
        const snapshot = this.snapshot();

        if (snapshot.vertices.length === 0) {
            throw new GraphValidationError(
                "Cannot plan an empty network."
            );
        }

        let result;

        if (algorithm === "kruskal") {
            result = this.kruskal(snapshot);
        } else if (algorithm === "prim") {
            result = this.prim(snapshot);
        } else {
            throw new GraphValidationError(
                "Unknown algorithm."
            );
        }

        const evaluation = policy.evaluate(result);

        const finalResult = Object.freeze({
            ...result,
            eligible: evaluation.eligible,
            violations: Object.freeze(evaluation.violations)
        });

        this.emit("planEvaluated", finalResult);

        return finalResult;
    }

    static async runIndependentPlans(planner) {
        // Both algorithms operate on the same immutable snapshot.
        const snapshot = planner.snapshot();

        const [kruskal, prim] = await Promise.all([
            Promise.resolve().then(
                () => planner.kruskal(snapshot)
            ),
            Promise.resolve().then(
                () => planner.prim(snapshot)
            )
        ]);

        if (
            Math.abs(
                kruskal.totalCost - prim.totalCost
            ) > 1e-9
        ) {
            throw new Error(
                "MST implementations returned different costs."
            );
        }

        return { kruskal, prim };
    }
}


async function main() {
    const planner = new NetworkPlanner(
        "Regional Telecommunications Network"
    );

    planner.on("connectionAdded", event => {
        console.log(
            `Added ${event.edge.source}-${event.edge.destination}; ` +
            `version=${event.version}`
        );
    });

    planner.on("planEvaluated", result => {
        console.log(
            `Plan evaluated: ${result.algorithm}, ` +
            `cost=${result.totalCost}`
        );
    });

    const connections = [
        ["A", "B", 4],
        ["A", "C", 3],
        ["B", "C", 1],
        ["B", "D", 2],
        ["C", "D", 4],
        ["C", "E", 5],
        ["D", "E", 2],
        ["D", "F", 6],
        ["E", "F", 3],
        ["A", "F", 10]
    ];

    for (const [source, destination, weight] of connections) {
        planner.addConnection(source, destination, weight);
    }

    const policy = new NetworkPolicy({
        requireConnected: true,
        maximumTotalCost: 15,
        maximumIndividualCost: 6,
        forbiddenConnections: [
            ["A", "F"]
        ]
    });

    const result = planner.plan({
        algorithm: "kruskal",
        policy
    });

    console.log("\nSelected connections:");

    for (const edge of result.edges) {
        console.log(
            `${edge.source} -- ${edge.destination}: ${edge.weight}`
        );
    }

    console.log("\nNetwork report:");
    console.log({
        totalCost: result.totalCost,
        components: result.componentCount,
        connected: result.connected,
        eligible: result.eligible,
        violations: result.violations
    });

    const comparison =
        await NetworkPlanner.runIndependentPlans(planner);

    assert.equal(comparison.kruskal.totalCost, 11);
    assert.equal(comparison.prim.totalCost, 11);
    assert.equal(comparison.kruskal.edges.length, 5);

    // Optimistic concurrency prevents updates based on stale state.
    const staleVersion = planner.version;

    planner.addVertex("G");

    assert.throws(
        () => planner.addVertex("H", staleVersion),
        VersionConflictError
    );

    // Invalid connection tests.
    assert.throws(
        () => planner.addConnection("A", "A", 1),
        GraphValidationError
    );

    assert.throws(
        () => planner.addConnection("A", "Z", Infinity),
        GraphValidationError
    );

    assert.throws(
        () => planner.addConnection("A", "B", 4),
        GraphValidationError
    );

    // A mandatory edge absent from the MST causes policy rejection.
    const strictPolicy = new NetworkPolicy({
        mandatoryConnections: [["A", "F"]]
    });

    const rejected = planner.plan({
        algorithm: "prim",
        policy: strictPolicy
    });

    assert.equal(rejected.eligible, false);

    console.log("\nAll JavaScript tests passed.");
}


main().catch(error => {
    console.error("Execution failed:", error.message);
    process.exitCode = 1;
});
