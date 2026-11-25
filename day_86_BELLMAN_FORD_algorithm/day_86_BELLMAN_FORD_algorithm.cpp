#include <algorithm>
#include <iostream>
#include <limits>
#include <queue>
#include <stdexcept>
#include <string>
#include <vector>
#include <unordered_set>

using namespace std;

/*
 * Bellman-Ford Repository-Independent Graph Engine
 *
 * Engineering perspective:
 * - Explicit graph and edge models
 * - Integer distance arithmetic with overflow protection
 * - Negative-cycle detection
 * - Cycle reconstruction
 * - Downstream impact propagation
 * - Shortest-path reconstruction
 * - Input validation
 * - Automated verification
 *
 * Compile:
 * g++ -std=c++17 -O2 -Wall -Wextra -pedantic bellman_ford.cpp -o bellman_ford
 */

using Distance = long long;

constexpr Distance INF = numeric_limits<Distance>::max() / 4;

struct Edge {
    int source;
    int destination;
    Distance weight;
};

struct BellmanFordResult {
    vector<Distance> distances;
    vector<int> predecessor;
    vector<int> negativeCycle;
    vector<bool> affected;
    int relaxationPasses = 0;

    bool hasNegativeCycle() const {
        return !negativeCycle.empty();
    }
};

class WeightedGraph {
private:
    int vertexCount;
    vector<Edge> edges;
    vector<vector<int>> adjacency;

    void validateVertex(int vertex) const {
        if (vertex < 0 || vertex >= vertexCount) {
            throw out_of_range("Invalid vertex identifier.");
        }
    }

    static Distance safeAdd(Distance a, Distance b) {
        if (b > 0 && a > INF - b) {
            throw overflow_error("Positive distance overflow.");
        }

        if (b < 0 && a < -INF - b) {
            throw overflow_error("Negative distance overflow.");
        }

        return a + b;
    }

    vector<int> reconstructCycle(
        int vertex,
        const vector<int>& predecessor
    ) const {
        for (int i = 0; i < vertexCount; ++i) {
            if (vertex == -1) {
                return {};
            }

            vertex = predecessor[vertex];
        }

        if (vertex == -1) {
            return {};
        }

        int start = vertex;
        vector<int> cycle{start};

        vertex = predecessor[start];

        while (vertex != start) {
            if (vertex == -1 || cycle.size() > static_cast<size_t>(vertexCount)) {
                return {};
            }

            cycle.push_back(vertex);
            vertex = predecessor[vertex];
        }

        cycle.push_back(start);
        reverse(cycle.begin(), cycle.end());

        return cycle;
    }

public:
    explicit WeightedGraph(int vertices)
        : vertexCount(vertices), adjacency(vertices) {

        if (vertices <= 0) {
            throw invalid_argument("Graph must contain at least one vertex.");
        }
    }

    int size() const {
        return vertexCount;
    }

    void addEdge(int source, int destination, Distance weight) {
        validateVertex(source);
        validateVertex(destination);

        if (weight >= INF || weight <= -INF) {
            throw invalid_argument("Weight exceeds supported range.");
        }

        edges.push_back({source, destination, weight});
        adjacency[source].push_back(destination);
    }

    BellmanFordResult solve(int source) const {
        validateVertex(source);

        BellmanFordResult result;

        result.distances.assign(vertexCount, INF);
        result.predecessor.assign(vertexCount, -1);
        result.affected.assign(vertexCount, false);

        result.distances[source] = 0;

        // Phase 1: relax all edges at most V-1 times.
        for (int iteration = 0; iteration < vertexCount - 1; ++iteration) {
            bool updated = false;

            for (const Edge& edge : edges) {
                int u = edge.source;
                int v = edge.destination;

                if (result.distances[u] == INF) {
                    continue;
                }

                Distance candidate = safeAdd(
                    result.distances[u],
                    edge.weight
                );

                if (candidate < result.distances[v]) {
                    result.distances[v] = candidate;
                    result.predecessor[v] = u;
                    updated = true;
                }
            }

            result.relaxationPasses++;

            if (!updated) {
                break;
            }
        }

        // Phase 2: detect reachable negative cycles.
        int cycleVertex = -1;

        for (const Edge& edge : edges) {
            int u = edge.source;
            int v = edge.destination;

            if (result.distances[u] == INF) {
                continue;
            }

            Distance candidate = safeAdd(
                result.distances[u],
                edge.weight
            );

            if (candidate < result.distances[v]) {
                result.predecessor[v] = u;

                if (cycleVertex == -1) {
                    cycleVertex = v;
                }
            }
        }

        if (cycleVertex != -1) {
            result.negativeCycle = reconstructCycle(
                cycleVertex,
                result.predecessor
            );
        }

        // Every relaxable destination is affected by a reachable cycle.
        queue<int> pending;

        for (const Edge& edge : edges) {
            int u = edge.source;
            int v = edge.destination;

            if (result.distances[u] == INF) {
                continue;
            }

            if (
                safeAdd(result.distances[u], edge.weight)
                < result.distances[v]
            ) {
                if (!result.affected[v]) {
                    result.affected[v] = true;
                    pending.push(v);
                }
            }
        }

        // Propagate undefined shortest-distance status downstream.
        while (!pending.empty()) {
            int current = pending.front();
            pending.pop();

            for (int neighbor : adjacency[current]) {
                if (!result.affected[neighbor]) {
                    result.affected[neighbor] = true;
                    pending.push(neighbor);
                }
            }
        }

        return result;
    }

    vector<int> shortestPath(
        int source,
        int destination,
        const BellmanFordResult& result
    ) const {
        validateVertex(source);
        validateVertex(destination);

        if (result.affected[destination]) {
            throw domain_error(
                "Shortest path is undefined because of a negative cycle."
            );
        }

        if (result.distances[destination] == INF) {
            return {};
        }

        vector<int> path;
        int current = destination;

        while (current != -1) {
            path.push_back(current);

            if (current == source) {
                break;
            }

            current = result.predecessor[current];
        }

        if (path.back() != source) {
            return {};
        }

        reverse(path.begin(), path.end());
        return path;
    }

    void printResult(
        int source,
        const BellmanFordResult& result
    ) const {
        cout << "\nSource vertex: " << source << "\n\n";

        cout << "Vertex\tDistance\tPredecessor\tState\n";

        for (int vertex = 0; vertex < vertexCount; ++vertex) {
            cout << vertex << "\t";

            if (result.affected[vertex]) {
                cout << "UNDEFINED\t";
            } else if (result.distances[vertex] == INF) {
                cout << "INF\t\t";
            } else {
                cout << result.distances[vertex] << "\t\t";
            }

            cout << result.predecessor[vertex] << "\t\t";

            if (result.affected[vertex]) {
                cout << "NEGATIVE-CYCLE-AFFECTED";
            } else if (result.distances[vertex] == INF) {
                cout << "UNREACHABLE";
            } else {
                cout << "DEFINED";
            }

            cout << '\n';
        }

        cout << "\nRelaxation passes: "
             << result.relaxationPasses << '\n';

        if (result.hasNegativeCycle()) {
            cout << "Negative cycle: ";

            for (int vertex : result.negativeCycle) {
                cout << vertex << ' ';
            }

            cout << '\n';
        } else {
            cout << "No reachable negative cycle.\n";
        }

        cout << "\nShortest paths:\n";

        for (int destination = 0; destination < vertexCount; ++destination) {
            cout << source << " -> " << destination << ": ";

            if (result.affected[destination]) {
                cout << "UNDEFINED\n";
                continue;
            }

            vector<int> path = shortestPath(
                source,
                destination,
                result
            );

            if (path.empty()) {
                cout << "UNREACHABLE\n";
                continue;
            }

            for (size_t i = 0; i < path.size(); ++i) {
                if (i > 0) cout << " -> ";
                cout << path[i];
            }

            cout << " (cost: " << result.distances[destination] << ")\n";
        }
    }
};

void demonstrateNormalGraph() {
    cout << "\n========== NORMAL GRAPH ==========\n";

    WeightedGraph graph(5);

    graph.addEdge(0, 1, 6);
    graph.addEdge(0, 2, 7);
    graph.addEdge(1, 2, 8);
    graph.addEdge(1, 3, 5);
    graph.addEdge(1, 4, -4);
    graph.addEdge(2, 3, -3);
    graph.addEdge(2, 4, 9);
    graph.addEdge(3, 1, -2);
    graph.addEdge(4, 0, 2);
    graph.addEdge(4, 3, 7);

    BellmanFordResult result = graph.solve(0);

    graph.printResult(0, result);
}

void demonstrateNegativeCycle() {
    cout << "\n========== NEGATIVE CYCLE ==========\n";

    WeightedGraph graph(6);

    graph.addEdge(0, 1, 4);
    graph.addEdge(1, 2, 3);
    graph.addEdge(2, 3, -8);
    graph.addEdge(3, 1, 2);
    graph.addEdge(3, 4, 5);
    graph.addEdge(4, 5, 2);

    BellmanFordResult result = graph.solve(0);

    graph.printResult(0, result);
}

void demonstrateUnreachableCycle() {
    cout << "\n========== UNREACHABLE CYCLE ==========\n";

    WeightedGraph graph(5);

    graph.addEdge(0, 1, 5);
    graph.addEdge(1, 2, 3);
    graph.addEdge(3, 4, -5);
    graph.addEdge(4, 3, 2);

    BellmanFordResult result = graph.solve(0);

    graph.printResult(0, result);
}

void demonstrateDisconnectedGraph() {
    cout << "\n========== DISCONNECTED GRAPH ==========\n";

    WeightedGraph graph(5);

    graph.addEdge(0, 1, 10);
    graph.addEdge(1, 2, -2);

    BellmanFordResult result = graph.solve(0);

    graph.printResult(0, result);
}

void runTests() {
    // Shortest-path correctness.
    WeightedGraph graph(4);

    graph.addEdge(0, 1, 4);
    graph.addEdge(1, 2, -2);
    graph.addEdge(2, 3, 3);

    BellmanFordResult result = graph.solve(0);

    if (
        result.distances[0] != 0 ||
        result.distances[1] != 4 ||
        result.distances[2] != 2 ||
        result.distances[3] != 5
    ) {
        throw runtime_error("Distance verification failed.");
    }

    vector<int> path = graph.shortestPath(0, 3, result);

    if (path != vector<int>({0, 1, 2, 3})) {
        throw runtime_error("Path reconstruction failed.");
    }

    // Reachable negative cycle.
    WeightedGraph cycleGraph(3);

    cycleGraph.addEdge(0, 1, 1);
    cycleGraph.addEdge(1, 2, -3);
    cycleGraph.addEdge(2, 1, 1);

    BellmanFordResult cycleResult = cycleGraph.solve(0);

    if (!cycleResult.hasNegativeCycle()) {
        throw runtime_error("Negative-cycle detection failed.");
    }

    // Unreachable negative cycle.
    WeightedGraph isolatedGraph(4);

    isolatedGraph.addEdge(0, 1, 2);
    isolatedGraph.addEdge(2, 3, -4);
    isolatedGraph.addEdge(3, 2, 1);

    BellmanFordResult isolatedResult = isolatedGraph.solve(0);

    if (isolatedResult.hasNegativeCycle()) {
        throw runtime_error("Unreachable-cycle handling failed.");
    }

    // Negative self-loop.
    WeightedGraph selfLoopGraph(1);
    selfLoopGraph.addEdge(0, 0, -1);

    if (!selfLoopGraph.solve(0).hasNegativeCycle()) {
        throw runtime_error("Negative self-loop detection failed.");
    }

    // Invalid vertex.
    bool rejected = false;

    try {
        graph.addEdge(0, 9, 1);
    } catch (const out_of_range&) {
        rejected = true;
    }

    if (!rejected) {
        throw runtime_error("Vertex validation failed.");
    }

    cout << "\nAll C++17 tests passed.\n";
}

int main() {
    try {
        demonstrateNormalGraph();
        demonstrateNegativeCycle();
        demonstrateUnreachableCycle();
        demonstrateDisconnectedGraph();
        runTests();
    } catch (const exception& error) {
        cerr << "Execution error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
