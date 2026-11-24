#include <algorithm>
#include <cmath>
#include <cstdint>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <queue>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

using namespace std;

using Weight = int64_t;
constexpr Weight INF = numeric_limits<Weight>::max();

struct Edge {
    int destination;
    Weight weight;
};

struct PathResult {
    int source;
    vector<Weight> distance;
    vector<int> predecessor;
    vector<bool> settled;

    vector<int> getPath(int destination) const {
        if (destination < 0 ||
            destination >= static_cast<int>(distance.size())) {
            throw out_of_range("Invalid destination vertex");
        }

        if (distance[destination] == INF) {
            return {};
        }

        vector<int> path;
        int current = destination;

        while (current != -1) {
            path.push_back(current);

            if (current == source) {
                break;
            }

            current = predecessor[current];

            if (current == -1) {
                throw logic_error("Broken predecessor chain");
            }
        }

        reverse(path.begin(), path.end());

        if (path.front() != source) {
            throw logic_error("Invalid shortest path");
        }

        return path;
    }
};

class WeightedGraph {
private:
    vector<string> names;
    vector<vector<Edge>> adjacency;
    unordered_map<string, int> indices;

public:
    int addVertex(const string& name) {
        if (name.empty()) {
            throw invalid_argument("Vertex name cannot be empty");
        }

        auto found = indices.find(name);

        if (found != indices.end()) {
            return found->second;
        }

        int id = static_cast<int>(names.size());

        names.push_back(name);
        adjacency.emplace_back();
        indices.emplace(name, id);

        return id;
    }

    void addEdge(
        const string& from,
        const string& to,
        Weight weight,
        bool directed = false
    ) {
        if (weight < 0) {
            throw invalid_argument(
                "Dijkstra does not support negative weights"
            );
        }

        int u = addVertex(from);
        int v = addVertex(to);

        adjacency[u].push_back({v, weight});

        if (!directed) {
            adjacency[v].push_back({u, weight});
        }
    }

    int getVertex(const string& name) const {
        auto found = indices.find(name);

        if (found == indices.end()) {
            throw invalid_argument("Unknown vertex: " + name);
        }

        return found->second;
    }

    const string& getName(int id) const {
        return names.at(id);
    }

    int vertexCount() const {
        return static_cast<int>(names.size());
    }

    PathResult dijkstra(const string& sourceName) const {
        int n = vertexCount();
        int source = getVertex(sourceName);

        vector<Weight> distance(n, INF);
        vector<int> predecessor(n, -1);
        vector<bool> settled(n, false);

        // Min-heap entries are {distance, vertex}.
        using State = pair<Weight, int>;

        priority_queue<
            State,
            vector<State>,
            greater<State>
        > pq;

        distance[source] = 0;
        pq.push({0, source});

        while (!pq.empty()) {
            auto [currentDistance, u] = pq.top();
            pq.pop();

            // Priority queue may contain outdated distances.
            if (currentDistance != distance[u]) {
                continue;
            }

            if (settled[u]) {
                continue;
            }

            settled[u] = true;

            for (const Edge& edge : adjacency[u]) {
                int v = edge.destination;
                Weight weight = edge.weight;

                if (settled[v]) {
                    continue;
                }

                // Prevent signed integer overflow.
                if (currentDistance > INF - weight) {
                    throw overflow_error(
                        "Shortest-path distance exceeds int64 range"
                    );
                }

                Weight candidate = currentDistance + weight;

                if (candidate < distance[v]) {
                    distance[v] = candidate;
                    predecessor[v] = u;

                    pq.push({candidate, v});
                }
            }
        }

        return {
            source,
            move(distance),
            move(predecessor),
            move(settled)
        };
    }

    void printResult(const PathResult& result) const {
        cout << "\nShortest paths from "
             << getName(result.source) << "\n";

        cout << left
             << setw(18) << "Destination"
             << setw(18) << "Distance"
             << "Route\n";

        cout << string(75, '-') << "\n";

        for (int i = 0; i < vertexCount(); ++i) {
            cout << left << setw(18) << names[i];

            if (result.distance[i] == INF) {
                cout << setw(18) << "Unreachable"
                     << "-\n";
                continue;
            }

            cout << setw(18) << result.distance[i];

            vector<int> path = result.getPath(i);

            for (size_t j = 0; j < path.size(); ++j) {
                if (j > 0) {
                    cout << " -> ";
                }

                cout << names[path[j]];
            }

            cout << "\n";
        }
    }
};

WeightedGraph buildTransportNetwork() {
    WeightedGraph graph;

    vector<tuple<string, string, Weight>> edges = {
        {"Delhi", "Agra", 230},
        {"Delhi", "Jaipur", 280},
        {"Delhi", "Lucknow", 550},
        {"Agra", "Lucknow", 330},
        {"Agra", "Jaipur", 240},
        {"Jaipur", "Ahmedabad", 660},
        {"Lucknow", "Varanasi", 320},
        {"Lucknow", "Patna", 540},
        {"Varanasi", "Patna", 250},
        {"Patna", "Kolkata", 580},
        {"Ahmedabad", "Mumbai", 530},
        {"Mumbai", "Pune", 150},
        {"Kolkata", "Mumbai", 1900}
    };

    for (const auto& [u, v, weight] : edges) {
        graph.addEdge(u, v, weight);
    }

    graph.addVertex("Chennai");

    return graph;
}

void runTests() {
    WeightedGraph graph;

    graph.addEdge("A", "B", 4, true);
    graph.addEdge("A", "C", 1, true);
    graph.addEdge("C", "B", 2, true);
    graph.addEdge("B", "D", 1, true);
    graph.addEdge("C", "D", 5, true);
    graph.addVertex("ISOLATED");

    PathResult result = graph.dijkstra("A");

    int b = graph.getVertex("B");
    int d = graph.getVertex("D");
    int isolated = graph.getVertex("ISOLATED");

    if (result.distance[b] != 3 ||
        result.distance[d] != 4 ||
        result.distance[isolated] != INF) {
        throw runtime_error("Shortest-path test failed");
    }

    vector<int> expected = {
        graph.getVertex("A"),
        graph.getVertex("C"),
        graph.getVertex("B"),
        graph.getVertex("D")
    };

    if (result.getPath(d) != expected) {
        throw runtime_error("Path reconstruction test failed");
    }

    WeightedGraph zeroGraph;
    zeroGraph.addEdge("X", "Y", 0, true);

    if (zeroGraph.dijkstra("X").distance[
            zeroGraph.getVertex("Y")] != 0) {
        throw runtime_error("Zero-weight edge test failed");
    }

    WeightedGraph parallelGraph;
    parallelGraph.addEdge("P", "Q", 10, true);
    parallelGraph.addEdge("P", "Q", 3, true);

    if (parallelGraph.dijkstra("P").distance[
            parallelGraph.getVertex("Q")] != 3) {
        throw runtime_error("Parallel-edge test failed");
    }

    bool negativeRejected = false;

    try {
        graph.addEdge("A", "Z", -1);
    } catch (const invalid_argument&) {
        negativeRejected = true;
    }

    if (!negativeRejected) {
        throw runtime_error("Negative edge was accepted");
    }

    bool unknownRejected = false;

    try {
        graph.dijkstra("UNKNOWN");
    } catch (const invalid_argument&) {
        unknownRejected = true;
    }

    if (!unknownRejected) {
        throw runtime_error("Unknown source was accepted");
    }

    cout << "All C++17 tests passed.\n";
}

int main() {
    try {
        cout << "DIJKSTRA SHORTEST PATH ENGINE\n";
        cout << string(55, '=') << "\n";

        runTests();

        WeightedGraph graph = buildTransportNetwork();

        PathResult result = graph.dijkstra("Delhi");

        graph.printResult(result);

        int destination = graph.getVertex("Mumbai");

        cout << "\nSpecific route: Delhi to Mumbai\n";

        if (result.distance[destination] == INF) {
            cout << "No route available.\n";
        } else {
            vector<int> path = result.getPath(destination);

            for (size_t i = 0; i < path.size(); ++i) {
                if (i > 0) {
                    cout << " -> ";
                }

                cout << graph.getName(path[i]);
            }

            cout << "\nDistance: "
                 << result.distance[destination]
                 << " km\n";
        }

        cout << "\nPerformance characteristics\n";
        cout << "Priority queue: Binary min-heap\n";
        cout << "Time: O((V + E) log V)\n";
        cout << "Space: O(V + E)\n";
        cout << "Weight representation: int64_t\n";
        cout << "Negative weights: Rejected\n";
        cout << "Overflow: Explicitly checked\n";

    } catch (const exception& error) {
        cerr << "Execution error: " << error.what() << "\n";
        return 1;
    }

    return 0;
}
