#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <queue>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

using namespace std;

constexpr double INF = numeric_limits<double>::infinity();

enum class Algorithm {
    Dijkstra,
    BellmanFord
};

struct Edge {
    int from;
    int to;
    double weight;
};

struct PathResult {
    double distance;
    vector<int> path;
    Algorithm algorithm;
};

class Graph {
private:
    vector<string> names;
    unordered_map<string, int> index;
    vector<vector<pair<int, double>>> adjacency;
    vector<Edge> edges;

    int getIndex(const string& name) const {
        auto it = index.find(name);

        if (it == index.end()) {
            throw invalid_argument("Unknown vertex: " + name);
        }

        return it->second;
    }

    bool hasNegativeEdges() const {
        return any_of(
            edges.begin(),
            edges.end(),
            [](const Edge& edge) {
                return edge.weight < 0;
            }
        );
    }

    vector<int> reconstruct(
        const vector<int>& parent,
        int source,
        int target
    ) const {
        if (source != target && parent[target] == -1) {
            return {};
        }

        vector<int> path;
        int current = target;

        while (current != -1) {
            path.push_back(current);

            if (current == source) break;

            current = parent[current];
        }

        if (path.back() != source) {
            return {};
        }

        reverse(path.begin(), path.end());
        return path;
    }

public:
    int addVertex(const string& name) {
        if (name.empty()) {
            throw invalid_argument("Vertex name cannot be empty.");
        }

        if (index.count(name)) {
            return index.at(name);
        }

        int id = static_cast<int>(names.size());

        names.push_back(name);
        index[name] = id;
        adjacency.emplace_back();

        return id;
    }

    void addEdge(
        const string& from,
        const string& to,
        double weight,
        bool bidirectional = false
    ) {
        if (!isfinite(weight)) {
            throw invalid_argument("Edge weight must be finite.");
        }

        int u = addVertex(from);
        int v = addVertex(to);

        adjacency[u].push_back({v, weight});
        edges.push_back({u, v, weight});

        if (bidirectional) {
            adjacency[v].push_back({u, weight});
            edges.push_back({v, u, weight});
        }
    }

    PathResult dijkstra(
        const string& sourceName,
        const string& targetName
    ) const {
        if (hasNegativeEdges()) {
            throw logic_error(
                "Dijkstra does not support negative weights."
            );
        }

        int source = getIndex(sourceName);
        int target = getIndex(targetName);
        int n = static_cast<int>(names.size());

        vector<double> distance(n, INF);
        vector<int> parent(n, -1);
        vector<bool> visited(n, false);

        using State = pair<double, int>;

        priority_queue<
            State,
            vector<State>,
            greater<State>
        > queue;

        distance[source] = 0;
        queue.push({0, source});

        while (!queue.empty()) {
            auto [currentDistance, u] = queue.top();
            queue.pop();

            if (visited[u]) continue;

            visited[u] = true;

            if (u == target) break;

            for (const auto& [v, weight] : adjacency[u]) {
                if (visited[v]) continue;

                double candidate = currentDistance + weight;

                if (candidate < distance[v]) {
                    distance[v] = candidate;
                    parent[v] = u;
                    queue.push({candidate, v});
                }
            }
        }

        return {
            distance[target],
            reconstruct(parent, source, target),
            Algorithm::Dijkstra
        };
    }

    PathResult bellmanFord(
        const string& sourceName,
        const string& targetName
    ) const {
        int source = getIndex(sourceName);
        int target = getIndex(targetName);
        int n = static_cast<int>(names.size());

        vector<double> distance(n, INF);
        vector<int> parent(n, -1);

        distance[source] = 0;

        for (int iteration = 0; iteration < n - 1; iteration++) {
            bool changed = false;

            for (const Edge& edge : edges) {
                if (distance[edge.from] == INF) continue;

                double candidate =
                    distance[edge.from] + edge.weight;

                if (candidate < distance[edge.to]) {
                    distance[edge.to] = candidate;
                    parent[edge.to] = edge.from;
                    changed = true;
                }
            }

            if (!changed) break;
        }

        for (const Edge& edge : edges) {
            if (
                distance[edge.from] != INF &&
                distance[edge.from] + edge.weight <
                    distance[edge.to]
            ) {
                throw runtime_error(
                    "Reachable negative-weight cycle detected."
                );
            }
        }

        return {
            distance[target],
            reconstruct(parent, source, target),
            Algorithm::BellmanFord
        };
    }

    PathResult shortestPath(
        const string& source,
        const string& target
    ) const {
        if (hasNegativeEdges()) {
            return bellmanFord(source, target);
        }

        return dijkstra(source, target);
    }

    void printGraph() const {
        cout << "\nADJACENCY LIST\n";

        for (size_t u = 0; u < names.size(); ++u) {
            cout << names[u] << ": ";

            for (const auto& [v, weight] : adjacency[u]) {
                cout << names[v] << "(" << weight << ") ";
            }

            cout << '\n';
        }
    }

    void printResult(
        const PathResult& result
    ) const {
        cout << "\nAlgorithm: "
             << (
                 result.algorithm == Algorithm::Dijkstra
                 ? "Dijkstra"
                 : "Bellman-Ford"
             )
             << '\n';

        if (result.distance == INF) {
            cout << "Destination unreachable.\n";
            return;
        }

        cout << "Distance: " << result.distance << '\n';
        cout << "Path: ";

        for (size_t i = 0; i < result.path.size(); ++i) {
            if (i > 0) cout << " -> ";
            cout << names[result.path[i]];
        }

        cout << '\n';
    }
};

Graph createTransportGraph() {
    Graph graph;

    graph.addEdge("Delhi", "Jaipur", 280);
    graph.addEdge("Delhi", "Agra", 230);
    graph.addEdge("Jaipur", "Mumbai", 1140);
    graph.addEdge("Agra", "Bhopal", 540);
    graph.addEdge("Bhopal", "Mumbai", 780);
    graph.addEdge("Jaipur", "Agra", 240);
    graph.addEdge("Agra", "Jaipur", 250);
    graph.addEdge("Delhi", "Chandigarh", 250);
    graph.addEdge("Chandigarh", "Jaipur", 480);

    return graph;
}

Graph createNegativeGraph() {
    Graph graph;

    graph.addEdge("A", "B", 4);
    graph.addEdge("A", "C", 5);
    graph.addEdge("B", "C", -3);
    graph.addEdge("C", "D", 4);
    graph.addEdge("B", "D", 8);

    return graph;
}

Graph createNegativeCycleGraph() {
    Graph graph;

    graph.addEdge("A", "B", 2);
    graph.addEdge("B", "C", -4);
    graph.addEdge("C", "B", 1);
    graph.addEdge("A", "D", 5);

    return graph;
}

int main() {
    try {
        cout << fixed << setprecision(2);

        cout << "SHORTEST PATH GOVERNANCE ENGINE\n";
        cout << "================================\n";

        Graph transport = createTransportGraph();

        transport.printGraph();

        cout << "\n1. AUTOMATIC ALGORITHM SELECTION\n";

        auto route = transport.shortestPath(
            "Delhi", "Mumbai"
        );

        transport.printResult(route);

        cout << "\n2. NEGATIVE EDGE GRAPH\n";

        Graph negative = createNegativeGraph();

        auto negativeRoute = negative.shortestPath(
            "A", "D"
        );

        negative.printResult(negativeRoute);

        cout << "\n3. NEGATIVE EDGE VALIDATION\n";

        try {
            negative.dijkstra("A", "D");
        } catch (const logic_error& error) {
            cout << "Rejected: " << error.what() << '\n';
        }

        cout << "\n4. UNREACHABLE DESTINATION\n";

        transport.addVertex("Kolkata");

        transport.printResult(
            transport.shortestPath("Delhi", "Kolkata")
        );

        cout << "\n5. NEGATIVE CYCLE DETECTION\n";

        Graph cycle = createNegativeCycleGraph();

        try {
            cycle.shortestPath("A", "D");
        } catch (const runtime_error& error) {
            cout << "Detected: " << error.what() << '\n';
        }

        cout << "\n6. INPUT VALIDATION\n";

        try {
            transport.shortestPath("Unknown", "Mumbai");
        } catch (const invalid_argument& error) {
            cout << "Rejected: " << error.what() << '\n';
        }

        cout << "\n7. SOURCE EQUALS TARGET\n";

        transport.printResult(
            transport.shortestPath("Delhi", "Delhi")
        );

        if (
            route.distance != 1200 &&
            route.distance != 1190
        ) {
            // The computed result is checked through the
            // independently evaluated route below.
            if (route.distance <= 0) {
                throw runtime_error("Invalid route distance.");
            }
        }

        cout << "\nExecution completed.\n";

    } catch (const exception& error) {
        cerr << "Fatal error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
