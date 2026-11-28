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
#include <utility>
#include <vector>

using namespace std;

struct Edge {
    int source;
    int destination;
    double weight;
};

struct Candidate {
    double weight;
    int source;
    int destination;
};

struct CandidateComparator {
    bool operator()(const Candidate& a, const Candidate& b) const {
        if (a.weight != b.weight) {
            return a.weight > b.weight;
        }

        if (a.source != b.source) {
            return a.source > b.source;
        }

        return a.destination > b.destination;
    }
};

class WeightedGraph {
private:
    vector<vector<pair<int, double>>> adjacency;
    unordered_map<string, int> vertexIds;
    vector<string> vertexNames;
    size_t edgeCount = 0;

public:
    int addVertex(const string& name) {
        if (name.empty()) {
            throw invalid_argument("Vertex name cannot be empty.");
        }

        auto found = vertexIds.find(name);

        if (found != vertexIds.end()) {
            return found->second;
        }

        int id = static_cast<int>(vertexNames.size());

        vertexIds.emplace(name, id);
        vertexNames.push_back(name);
        adjacency.emplace_back();

        return id;
    }

    void addEdge(
        const string& source,
        const string& destination,
        double weight
    ) {
        if (source == destination) {
            throw invalid_argument("Self-loops are not supported.");
        }

        if (!isfinite(weight)) {
            throw invalid_argument("Weight must be finite.");
        }

        int u = addVertex(source);
        int v = addVertex(destination);

        adjacency[u].emplace_back(v, weight);
        adjacency[v].emplace_back(u, weight);

        edgeCount++;
    }

    size_t vertexCount() const {
        return adjacency.size();
    }

    size_t getEdgeCount() const {
        return edgeCount;
    }

    const vector<pair<int, double>>& neighbors(int vertex) const {
        if (vertex < 0 || vertex >= static_cast<int>(adjacency.size())) {
            throw out_of_range("Invalid vertex identifier.");
        }

        return adjacency[vertex];
    }

    const string& name(int vertex) const {
        return vertexNames.at(vertex);
    }
};

struct MSTResult {
    vector<Edge> edges;
    double totalWeight = 0.0;
    int components = 0;
    size_t examinedEdges = 0;

    bool connected(size_t vertices) const {
        return vertices == 0 || components == 1;
    }
};

class PrimEngine {
public:
    static MSTResult calculate(const WeightedGraph& graph) {
        MSTResult result;

        const int n = static_cast<int>(graph.vertexCount());

        vector<bool> visited(n, false);

        priority_queue<
            Candidate,
            vector<Candidate>,
            CandidateComparator
        > minHeap;

        for (int start = 0; start < n; start++) {
            if (visited[start]) {
                continue;
            }

            result.components++;
            visited[start] = true;

            pushNeighbors(graph, start, visited, minHeap, result);

            while (!minHeap.empty()) {
                Candidate current = minHeap.top();
                minHeap.pop();

                int destination = current.destination;

                // Lazy deletion prevents outdated heap entries
                // from introducing cycles.
                if (visited[destination]) {
                    continue;
                }

                visited[destination] = true;

                result.edges.push_back({
                    current.source,
                    destination,
                    current.weight
                });

                result.totalWeight += current.weight;

                pushNeighbors(
                    graph,
                    destination,
                    visited,
                    minHeap,
                    result
                );
            }
        }

        return result;
    }

private:
    static void pushNeighbors(
        const WeightedGraph& graph,
        int vertex,
        const vector<bool>& visited,
        priority_queue<
            Candidate,
            vector<Candidate>,
            CandidateComparator
        >& minHeap,
        MSTResult& result
    ) {
        for (const auto& [neighbor, weight] : graph.neighbors(vertex)) {
            result.examinedEdges++;

            if (!visited[neighbor]) {
                minHeap.push({
                    weight,
                    vertex,
                    neighbor
                });
            }
        }
    }
};

class DisjointSet {
private:
    vector<int> parent;
    vector<int> rank;

public:
    explicit DisjointSet(int n)
        : parent(n), rank(n, 0) {
        for (int i = 0; i < n; i++) {
            parent[i] = i;
        }
    }

    int find(int vertex) {
        if (parent[vertex] != vertex) {
            parent[vertex] = find(parent[vertex]);
        }

        return parent[vertex];
    }

    bool unite(int a, int b) {
        a = find(a);
        b = find(b);

        if (a == b) {
            return false;
        }

        if (rank[a] < rank[b]) {
            swap(a, b);
        }

        parent[b] = a;

        if (rank[a] == rank[b]) {
            rank[a]++;
        }

        return true;
    }
};

bool verifyForest(
    const WeightedGraph& graph,
    const MSTResult& result
) {
    size_t n = graph.vertexCount();

    if (result.edges.size() != n - result.components) {
        return false;
    }

    DisjointSet dsu(static_cast<int>(n));

    double total = 0.0;

    for (const Edge& edge : result.edges) {
        bool valid = false;

        for (const auto& [neighbor, weight] :
             graph.neighbors(edge.source)) {
            if (
                neighbor == edge.destination &&
                weight == edge.weight
            ) {
                valid = true;
                break;
            }
        }

        if (!valid || !dsu.unite(edge.source, edge.destination)) {
            return false;
        }

        total += edge.weight;
    }

    unordered_set<int> roots;

    for (int i = 0; i < static_cast<int>(n); i++) {
        roots.insert(dsu.find(i));
    }

    return (
        static_cast<int>(roots.size()) == result.components &&
        abs(total - result.totalWeight) < 1e-9
    );
}

void displayResult(
    const WeightedGraph& graph,
    const MSTResult& result
) {
    cout << "\nMINIMUM SPANNING FOREST\n";
    cout << "========================================\n";

    for (const Edge& edge : result.edges) {
        cout << graph.name(edge.source)
             << " -> "
             << graph.name(edge.destination)
             << " | Weight: "
             << edge.weight << '\n';
    }

    cout << "========================================\n";

    cout << "Vertices: " << graph.vertexCount() << '\n';
    cout << "Original edges: " << graph.getEdgeCount() << '\n';
    cout << "Components: " << result.components << '\n';
    cout << "Selected edges: " << result.edges.size() << '\n';

    cout << fixed << setprecision(2);
    cout << "Total weight: " << result.totalWeight << '\n';

    cout << "Connected: "
         << (result.connected(graph.vertexCount()) ? "Yes" : "No")
         << '\n';

    cout << "Examined adjacency entries: "
         << result.examinedEdges << '\n';
}

void runTests() {
    // Empty graph.
    WeightedGraph empty;
    MSTResult emptyResult = PrimEngine::calculate(empty);

    if (emptyResult.components != 0 ||
        !emptyResult.edges.empty()) {
        throw runtime_error("Empty graph test failed.");
    }

    // Negative weights and parallel edges.
    WeightedGraph negative;

    negative.addEdge("A", "B", -5);
    negative.addEdge("A", "B", 3);
    negative.addEdge("B", "C", -2);
    negative.addEdge("A", "C", 1);

    MSTResult negativeResult = PrimEngine::calculate(negative);

    if (
        abs(negativeResult.totalWeight - (-7.0)) > 1e-9 ||
        !verifyForest(negative, negativeResult)
    ) {
        throw runtime_error("Negative-weight test failed.");
    }

    // Disconnected graph.
    WeightedGraph disconnected;

    disconnected.addEdge("A", "B", 4);
    disconnected.addEdge("C", "D", 2);
    disconnected.addVertex("E");

    MSTResult disconnectedResult =
        PrimEngine::calculate(disconnected);

    if (
        disconnectedResult.components != 3 ||
        disconnectedResult.edges.size() != 2 ||
        abs(disconnectedResult.totalWeight - 6.0) > 1e-9
    ) {
        throw runtime_error("Disconnected graph test failed.");
    }

    // Invalid self-loop.
    try {
        disconnected.addEdge("A", "A", 10);
        throw runtime_error("Self-loop validation failed.");
    } catch (const invalid_argument&) {
        // Expected validation result.
    }

    // Non-finite weight.
    try {
        disconnected.addEdge(
            "A",
            "B",
            numeric_limits<double>::infinity()
        );

        throw runtime_error("Infinite-weight validation failed.");
    } catch (const invalid_argument&) {
        // Expected validation result.
    }

    cout << "\nAll C++17 tests passed.\n";
}

int main() {
    try {
        WeightedGraph graph;

        vector<Edge> input = {
            {0, 1, 4},
            {0, 2, 3},
            {1, 2, 1},
            {1, 3, 2},
            {2, 3, 4},
            {2, 4, 5},
            {3, 4, 2},
            {3, 5, 3},
            {4, 5, 1},
            {4, 6, 7},
            {5, 6, 2},
            {7, 8, 6}
        };

        vector<string> names = {
            "A", "B", "C", "D", "E",
            "F", "G", "H", "I"
        };

        for (const string& name : names) {
            graph.addVertex(name);
        }

        for (const Edge& edge : input) {
            graph.addEdge(
                names[edge.source],
                names[edge.destination],
                edge.weight
            );
        }

        graph.addVertex("ISOLATED");

        MSTResult result = PrimEngine::calculate(graph);

        displayResult(graph, result);

        if (!verifyForest(graph, result)) {
            throw runtime_error("Forest verification failed.");
        }

        cout << "\nForest verification: PASSED\n";

        runTests();

    } catch (const exception& error) {
        cerr << "Error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
