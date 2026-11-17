#include <algorithm>
#include <cmath>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <queue>
#include <set>
#include <stdexcept>
#include <string>
#include <tuple>
#include <unordered_map>
#include <utility>
#include <vector>

using namespace std;

enum class GraphType {
    Directed,
    Undirected
};

enum class Representation {
    AdjacencyList,
    AdjacencyMatrix
};

struct Edge {
    string source;
    string destination;
    double weight;
};

class Graph {
private:
    GraphType type;
    bool weighted;

    // Adjacency list: vertex -> (neighbor -> edge weight).
    map<string, map<string, double>> adjacency;

    void validateVertex(const string& vertex) const {
        if (vertex.empty()) {
            throw invalid_argument(
                "Vertex cannot be empty."
            );
        }
    }

    void requireVertex(const string& vertex) const {
        if (adjacency.find(vertex) == adjacency.end()) {
            throw out_of_range(
                "Unknown vertex: " + vertex
            );
        }
    }

public:
    explicit Graph(
        GraphType graphType = GraphType::Undirected,
        bool isWeighted = false
    ) : type(graphType), weighted(isWeighted) {}

    void addVertex(const string& vertex) {
        validateVertex(vertex);
        adjacency.try_emplace(vertex);
    }

    void addEdge(
        const string& source,
        const string& destination,
        double weight = 1.0
    ) {
        validateVertex(source);
        validateVertex(destination);

        if (!isfinite(weight)) {
            throw invalid_argument(
                "Edge weight must be finite."
            );
        }

        if (!weighted && weight != 1.0) {
            throw invalid_argument(
                "Unweighted graph requires weight 1."
            );
        }

        addVertex(source);
        addVertex(destination);

        adjacency[source][destination] = weight;

        if (type == GraphType::Undirected) {
            adjacency[destination][source] = weight;
        }
    }

    void removeEdge(
        const string& source,
        const string& destination
    ) {
        requireVertex(source);
        requireVertex(destination);

        adjacency[source].erase(destination);

        if (type == GraphType::Undirected) {
            adjacency[destination].erase(source);
        }
    }

    void removeVertex(const string& vertex) {
        requireVertex(vertex);

        adjacency.erase(vertex);

        for (auto& [name, neighbors] : adjacency) {
            neighbors.erase(vertex);
        }
    }

    size_t vertexCount() const {
        return adjacency.size();
    }

    size_t edgeCount() const {
        size_t count = 0;

        for (const auto& [vertex, neighbors] : adjacency) {
            count += neighbors.size();
        }

        return type == GraphType::Undirected
            ? count / 2
            : count;
    }

    vector<string> vertices() const {
        vector<string> result;

        for (const auto& [vertex, neighbors] : adjacency) {
            result.push_back(vertex);
        }

        return result;
    }

    vector<Edge> edges() const {
        vector<Edge> result;

        for (const auto& [source, neighbors] : adjacency) {
            for (const auto& [destination, weight] : neighbors) {
                if (
                    type == GraphType::Undirected &&
                    source > destination
                ) {
                    continue;
                }

                result.push_back({
                    source,
                    destination,
                    weight
                });
            }
        }

        return result;
    }

    void displayAdjacencyList() const {
        cout << "\nADJACENCY LIST\n";

        for (const auto& [vertex, neighbors] : adjacency) {
            cout << vertex << " -> ";

            for (const auto& [neighbor, weight] : neighbors) {
                cout << neighbor;

                if (weighted) {
                    cout << "(" << weight << ")";
                }

                cout << " ";
            }

            cout << "\n";
        }
    }

    void displayAdjacencyMatrix() const {
        vector<string> nodes = vertices();

        cout << "\nADJACENCY MATRIX\n";
        cout << setw(8) << " ";

        for (const auto& vertex : nodes) {
            cout << setw(8) << vertex;
        }

        cout << "\n";

        for (const auto& source : nodes) {
            cout << setw(8) << source;

            for (const auto& destination : nodes) {
                auto it = adjacency.at(source).find(destination);

                if (it == adjacency.at(source).end()) {
                    cout << setw(8) << "-";
                } else {
                    cout << setw(8) << it->second;
                }
            }

            cout << "\n";
        }
    }

    vector<string> bfs(const string& start) const {
        requireVertex(start);

        queue<string> pending;
        set<string> visited;
        vector<string> result;

        pending.push(start);
        visited.insert(start);

        while (!pending.empty()) {
            string current = pending.front();
            pending.pop();

            result.push_back(current);

            for (const auto& [neighbor, weight] :
                adjacency.at(current)) {

                if (visited.insert(neighbor).second) {
                    pending.push(neighbor);
                }
            }
        }

        return result;
    }

    vector<string> dfs(const string& start) const {
        requireVertex(start);

        vector<string> stack = {start};
        set<string> visited;
        vector<string> result;

        while (!stack.empty()) {
            string current = stack.back();
            stack.pop_back();

            if (!visited.insert(current).second) {
                continue;
            }

            result.push_back(current);

            const auto& neighbors = adjacency.at(current);

            for (
                auto it = neighbors.rbegin();
                it != neighbors.rend();
                ++it
            ) {
                if (!visited.count(it->first)) {
                    stack.push_back(it->first);
                }
            }
        }

        return result;
    }

    int inDegree(const string& vertex) const {
        requireVertex(vertex);

        int count = 0;

        for (const auto& [source, neighbors] : adjacency) {
            if (neighbors.count(vertex)) {
                ++count;
            }
        }

        return count;
    }

    int outDegree(const string& vertex) const {
        requireVertex(vertex);
        return static_cast<int>(adjacency.at(vertex).size());
    }

    map<string, double> dijkstra(const string& start) const {
        requireVertex(start);

        for (const auto& edge : edges()) {
            if (edge.weight < 0) {
                throw domain_error(
                    "Dijkstra requires non-negative weights."
                );
            }
        }

        const double INF = numeric_limits<double>::infinity();

        map<string, double> distances;

        for (const auto& vertex : vertices()) {
            distances[vertex] = INF;
        }

        using State = pair<double, string>;

        priority_queue<
            State,
            vector<State>,
            greater<State>
        > pending;

        distances[start] = 0.0;
        pending.push({0.0, start});

        while (!pending.empty()) {
            auto [distance, current] = pending.top();
            pending.pop();

            if (distance != distances[current]) {
                continue;
            }

            for (
                const auto& [neighbor, weight] :
                adjacency.at(current)
            ) {
                double candidate = distance + weight;

                if (candidate < distances[neighbor]) {
                    distances[neighbor] = candidate;
                    pending.push({candidate, neighbor});
                }
            }
        }

        return distances;
    }

    bool hasCycle() const {
        if (type == GraphType::Directed) {
            set<string> visited;
            set<string> active;

            function<bool(const string&)> visit =
                [&](const string& vertex) -> bool {
                    visited.insert(vertex);
                    active.insert(vertex);

                    for (
                        const auto& [neighbor, weight] :
                        adjacency.at(vertex)
                    ) {
                        if (!visited.count(neighbor)) {
                            if (visit(neighbor)) {
                                return true;
                            }
                        } else if (active.count(neighbor)) {
                            return true;
                        }
                    }

                    active.erase(vertex);
                    return false;
                };

            for (const auto& vertex : vertices()) {
                if (
                    !visited.count(vertex) &&
                    visit(vertex)
                ) {
                    return true;
                }
            }

            return false;
        }

        set<string> visited;

        function<bool(const string&, const string&)> visit =
            [&](const string& vertex, const string& parent) {
                visited.insert(vertex);

                for (
                    const auto& [neighbor, weight] :
                    adjacency.at(vertex)
                ) {
                    if (!visited.count(neighbor)) {
                        if (visit(neighbor, vertex)) {
                            return true;
                        }
                    } else if (neighbor != parent) {
                        return true;
                    }
                }

                return false;
            };

        for (const auto& vertex : vertices()) {
            if (
                !visited.count(vertex) &&
                visit(vertex, "")
            ) {
                return true;
            }
        }

        return false;
    }

    vector<vector<string>> connectedComponents() const {
        if (type != GraphType::Undirected) {
            throw logic_error(
                "Connected components require an undirected graph."
            );
        }

        set<string> visited;
        vector<vector<string>> components;

        for (const auto& vertex : vertices()) {
            if (visited.count(vertex)) {
                continue;
            }

            vector<string> component = bfs(vertex);

            for (const auto& node : component) {
                visited.insert(node);
            }

            components.push_back(component);
        }

        return components;
    }
};

void printTraversal(const vector<string>& traversal) {
    for (size_t i = 0; i < traversal.size(); ++i) {
        if (i > 0) {
            cout << " -> ";
        }

        cout << traversal[i];
    }

    cout << "\n";
}

int main() {
    try {
        cout << "GRAPH INTRODUCTION\n";
        cout << "==============================\n";

        // Scenario 1: Road network represented as a weighted,
        // undirected graph.
        Graph roadNetwork(
            GraphType::Undirected,
            true
        );

        roadNetwork.addEdge("Delhi", "Agra", 230);
        roadNetwork.addEdge("Delhi", "Jaipur", 280);
        roadNetwork.addEdge("Agra", "Lucknow", 335);
        roadNetwork.addEdge("Jaipur", "Lucknow", 575);
        roadNetwork.addEdge("Agra", "Jaipur", 240);
        roadNetwork.addEdge("Lucknow", "Kanpur", 80);

        cout << "\n1. ROAD NETWORK\n";

        cout << "Vertices: " << roadNetwork.vertexCount() << "\n";
        cout << "Edges: " << roadNetwork.edgeCount() << "\n";

        roadNetwork.displayAdjacencyList();
        roadNetwork.displayAdjacencyMatrix();

        cout << "\n2. GRAPH TRAVERSAL\n";

        cout << "BFS from Delhi: ";
        printTraversal(roadNetwork.bfs("Delhi"));

        cout << "DFS from Delhi: ";
        printTraversal(roadNetwork.dfs("Delhi"));

        cout << "\n3. SHORTEST DISTANCES\n";

        auto distances = roadNetwork.dijkstra("Delhi");

        for (const auto& [vertex, distance] : distances) {
            cout << "Delhi to " << vertex << ": ";

            if (isinf(distance)) {
                cout << "Unreachable\n";
            } else {
                cout << distance << " km\n";
            }
        }

        cout << "\n4. DIRECTED DEPENDENCY GRAPH\n";

        Graph dependencies(GraphType::Directed);

        dependencies.addEdge("Requirements", "Design");
        dependencies.addEdge("Design", "Coding");
        dependencies.addEdge("Coding", "Testing");
        dependencies.addEdge("Testing", "Deployment");

        cout << "Dependency order traversal: ";
        printTraversal(dependencies.bfs("Requirements"));

        cout << "Outgoing degree of Design: "
             << dependencies.outDegree("Design") << "\n";

        cout << "Incoming degree of Testing: "
             << dependencies.inDegree("Testing") << "\n";

        cout << "\n5. GRAPH CYCLE DETECTION\n";

        cout << "Road network contains cycle: "
             << boolalpha << roadNetwork.hasCycle() << "\n";

        Graph cyclic(GraphType::Directed);

        cyclic.addEdge("A", "B");
        cyclic.addEdge("B", "C");
        cyclic.addEdge("C", "A");

        cout << "Directed example contains cycle: "
             << cyclic.hasCycle() << "\n";

        cout << "\n6. CONNECTED COMPONENTS\n";

        Graph disconnected(GraphType::Undirected);

        disconnected.addEdge("A", "B");
        disconnected.addEdge("B", "C");
        disconnected.addEdge("D", "E");
        disconnected.addVertex("F");

        auto components = disconnected.connectedComponents();

        for (size_t i = 0; i < components.size(); ++i) {
            cout << "Component " << i + 1 << ": ";
            printTraversal(components[i]);
        }

        cout << "\n7. GRAPH MODIFICATION\n";

        roadNetwork.removeEdge("Delhi", "Jaipur");

        cout << "Edges after removal: "
             << roadNetwork.edgeCount() << "\n";

        roadNetwork.removeVertex("Kanpur");

        cout << "Vertices after removal: "
             << roadNetwork.vertexCount() << "\n";

        cout << "\n8. VALIDATION\n";

        try {
            roadNetwork.bfs("Unknown");
        } catch (const exception& error) {
            cout << "Unknown vertex: " << error.what() << "\n";
        }

        try {
            Graph unweighted(
                GraphType::Undirected,
                false
            );

            unweighted.addEdge("A", "B", 5);
        } catch (const exception& error) {
            cout << "Invalid edge: " << error.what() << "\n";
        }

        try {
            Graph negative(
                GraphType::Directed,
                true
            );

            negative.addEdge("X", "Y", -5);
            negative.dijkstra("X");
        } catch (const exception& error) {
            cout << "Invalid shortest path input: "
                 << error.what() << "\n";
        }

        cout << "\n9. ASSERTIONS\n";

        Graph verification(GraphType::Undirected);

        verification.addEdge("A", "B");
        verification.addEdge("B", "C");

        if (verification.vertexCount() != 3 ||
            verification.edgeCount() != 2) {
            throw runtime_error(
                "Graph count verification failed."
            );
        }

        if (verification.bfs("A").size() != 3) {
            throw runtime_error(
                "BFS verification failed."
            );
        }

        cout << "All graph tests passed.\n";

    } catch (const exception& error) {
        cerr << "Application error: " << error.what() << "\n";
        return 1;
    }

    return 0;
}
