#include <algorithm>
#include <cstddef>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using namespace std;

enum class GraphType {
    Directed,
    Undirected
};

struct CycleResult {
    bool hasCycle = false;
    string algorithm;
    vector<int> cycle;
};

class DisjointSet {
private:
    vector<int> parent;
    vector<int> componentSize;
    int componentCount;

    void validate(int vertex) const {
        if (vertex < 0 ||
            vertex >= static_cast<int>(parent.size())) {
            throw out_of_range("Invalid vertex.");
        }
    }

public:
    explicit DisjointSet(int vertexCount)
        : parent(vertexCount),
          componentSize(vertexCount, 1),
          componentCount(vertexCount) {

        if (vertexCount < 0) {
            throw invalid_argument(
                "Vertex count cannot be negative."
            );
        }

        iota(parent.begin(), parent.end(), 0);
    }

    int find(int vertex) {
        validate(vertex);

        // Iterative path compression.
        int root = vertex;

        while (parent[root] != root) {
            root = parent[root];
        }

        while (parent[vertex] != vertex) {
            int next = parent[vertex];
            parent[vertex] = root;
            vertex = next;
        }

        return root;
    }

    bool unite(int first, int second) {
        int rootFirst = find(first);
        int rootSecond = find(second);

        if (rootFirst == rootSecond) {
            return false;
        }

        // Union by component size.
        if (componentSize[rootFirst] <
            componentSize[rootSecond]) {
            swap(rootFirst, rootSecond);
        }

        parent[rootSecond] = rootFirst;
        componentSize[rootFirst] +=
            componentSize[rootSecond];

        --componentCount;
        return true;
    }

    int components() const {
        return componentCount;
    }
};

class Graph {
private:
    int vertexCount;
    GraphType type;
    vector<vector<int>> adjacency;
    vector<pair<int, int>> edges;

    void validateVertex(int vertex) const {
        if (vertex < 0 || vertex >= vertexCount) {
            throw out_of_range("Vertex outside graph.");
        }
    }

    void requireType(GraphType expected) const {
        if (type != expected) {
            throw logic_error(
                "Algorithm incompatible with graph type."
            );
        }
    }

public:
    Graph(int vertices, GraphType graphType)
        : vertexCount(vertices),
          type(graphType),
          adjacency(vertices) {

        if (vertices < 0) {
            throw invalid_argument(
                "Vertex count cannot be negative."
            );
        }
    }

    void addEdge(int source, int destination) {
        validateVertex(source);
        validateVertex(destination);

        adjacency[source].push_back(destination);

        if (type == GraphType::Undirected) {
            adjacency[destination].push_back(source);
        }

        edges.emplace_back(source, destination);
    }

    CycleResult directedDFS() const {
        requireType(GraphType::Directed);

        // 0 = unvisited, 1 = active, 2 = finished.
        vector<int> state(vertexCount, 0);
        vector<int> parent(vertexCount, -1);

        vector<int> foundCycle;

        function<bool(int)> dfs = [&](int vertex) {
            state[vertex] = 1;

            for (int neighbor : adjacency[vertex]) {
                if (state[neighbor] == 0) {
                    parent[neighbor] = vertex;

                    if (dfs(neighbor)) {
                        return true;
                    }
                } else if (state[neighbor] == 1) {
                    vector<int> path;
                    path.push_back(vertex);

                    int current = vertex;

                    while (current != neighbor) {
                        current = parent[current];

                        if (current == -1) {
                            throw logic_error(
                                "Invalid DFS parent relationship."
                            );
                        }

                        path.push_back(current);
                    }

                    reverse(path.begin(), path.end());
                    path.push_back(neighbor);

                    foundCycle = move(path);
                    return true;
                }
            }

            state[vertex] = 2;
            return false;
        };

        for (int vertex = 0; vertex < vertexCount; ++vertex) {
            if (state[vertex] == 0 && dfs(vertex)) {
                return {
                    true,
                    "Directed DFS",
                    foundCycle
                };
            }
        }

        return {false, "Directed DFS", {}};
    }

    CycleResult directedBFS() const {
        requireType(GraphType::Directed);

        vector<int> indegree(vertexCount, 0);

        for (const auto& neighbors : adjacency) {
            for (int neighbor : neighbors) {
                ++indegree[neighbor];
            }
        }

        vector<int> queue;
        queue.reserve(vertexCount);

        for (int vertex = 0; vertex < vertexCount; ++vertex) {
            if (indegree[vertex] == 0) {
                queue.push_back(vertex);
            }
        }

        size_t head = 0;
        vector<int> topologicalOrder;
        topologicalOrder.reserve(vertexCount);

        while (head < queue.size()) {
            int vertex = queue[head++];
            topologicalOrder.push_back(vertex);

            for (int neighbor : adjacency[vertex]) {
                --indegree[neighbor];

                if (indegree[neighbor] == 0) {
                    queue.push_back(neighbor);
                }
            }
        }

        bool hasCycle =
            static_cast<int>(topologicalOrder.size())
            != vertexCount;

        return {
            hasCycle,
            "Kahn BFS",
            {}
        };
    }

    CycleResult undirectedDFS() const {
        requireType(GraphType::Undirected);

        vector<bool> visited(vertexCount, false);

        function<bool(int, int)> dfs =
            [&](int vertex, int parent) {
                visited[vertex] = true;

                for (int neighbor : adjacency[vertex]) {
                    if (!visited[neighbor]) {
                        if (dfs(neighbor, vertex)) {
                            return true;
                        }
                    } else if (neighbor != parent) {
                        return true;
                    }
                }

                return false;
            };

        for (int vertex = 0; vertex < vertexCount; ++vertex) {
            if (!visited[vertex] && dfs(vertex, -1)) {
                return {true, "Undirected DFS", {}};
            }
        }

        return {false, "Undirected DFS", {}};
    }

    CycleResult undirectedBFS() const {
        requireType(GraphType::Undirected);

        vector<bool> visited(vertexCount, false);
        vector<int> parent(vertexCount, -1);

        for (int start = 0; start < vertexCount; ++start) {
            if (visited[start]) {
                continue;
            }

            vector<int> queue;
            queue.push_back(start);
            visited[start] = true;

            size_t head = 0;

            while (head < queue.size()) {
                int vertex = queue[head++];

                for (int neighbor : adjacency[vertex]) {
                    if (!visited[neighbor]) {
                        visited[neighbor] = true;
                        parent[neighbor] = vertex;
                        queue.push_back(neighbor);
                    } else if (neighbor != parent[vertex]) {
                        return {
                            true,
                            "Undirected BFS",
                            {}
                        };
                    }
                }
            }
        }

        return {false, "Undirected BFS", {}};
    }

    CycleResult undirectedDSU() const {
        requireType(GraphType::Undirected);

        DisjointSet dsu(vertexCount);

        for (const auto& [source, destination] : edges) {
            if (!dsu.unite(source, destination)) {
                return {
                    true,
                    "Disjoint Set Union",
                    {}
                };
            }
        }

        return {false, "Disjoint Set Union", {}};
    }

    int vertices() const {
        return vertexCount;
    }

    size_t edgeCount() const {
        return edges.size();
    }
};

void printResult(const CycleResult& result) {
    cout << result.algorithm << ": "
         << (result.hasCycle ? "Cycle detected" : "No cycle");

    if (!result.cycle.empty()) {
        cout << " | Cycle path: ";

        for (size_t i = 0; i < result.cycle.size(); ++i) {
            if (i > 0) {
                cout << " -> ";
            }

            cout << result.cycle[i];
        }
    }

    cout << '\n';
}

void require(bool condition, const string& message) {
    if (!condition) {
        throw runtime_error("Test failed: " + message);
    }
}

void runTests() {
    Graph directed(4, GraphType::Directed);

    for (const auto& edge :
         vector<pair<int, int>>{
             {0, 1}, {1, 2}, {2, 3}, {3, 1}
         }) {
        directed.addEdge(edge.first, edge.second);
    }

    require(directed.directedDFS().hasCycle,
            "Directed DFS cycle");

    require(directed.directedBFS().hasCycle,
            "Directed BFS cycle");

    Graph dag(5, GraphType::Directed);

    for (const auto& edge :
         vector<pair<int, int>>{
             {0, 1}, {0, 2}, {1, 3}, {2, 3}, {3, 4}
         }) {
        dag.addEdge(edge.first, edge.second);
    }

    require(!dag.directedDFS().hasCycle, "Directed DAG DFS");
    require(!dag.directedBFS().hasCycle, "Directed DAG BFS");

    Graph undirected(4, GraphType::Undirected);

    for (const auto& edge :
         vector<pair<int, int>>{
             {0, 1}, {1, 2}, {2, 0}, {2, 3}
         }) {
        undirected.addEdge(edge.first, edge.second);
    }

    require(undirected.undirectedDFS().hasCycle,
            "Undirected DFS");

    require(undirected.undirectedBFS().hasCycle,
            "Undirected BFS");

    require(undirected.undirectedDSU().hasCycle,
            "Undirected DSU");

    Graph tree(5, GraphType::Undirected);

    for (const auto& edge :
         vector<pair<int, int>>{
             {0, 1}, {0, 2}, {1, 3}, {1, 4}
         }) {
        tree.addEdge(edge.first, edge.second);
    }

    require(!tree.undirectedDFS().hasCycle, "Tree DFS");
    require(!tree.undirectedBFS().hasCycle, "Tree BFS");
    require(!tree.undirectedDSU().hasCycle, "Tree DSU");

    Graph loop(1, GraphType::Undirected);
    loop.addEdge(0, 0);

    require(loop.undirectedDSU().hasCycle, "Self-loop");

    Graph parallel(2, GraphType::Undirected);
    parallel.addEdge(0, 1);
    parallel.addEdge(0, 1);

    require(parallel.undirectedDSU().hasCycle,
            "Parallel edges");

    Graph disconnected(6, GraphType::Undirected);
    disconnected.addEdge(0, 1);
    disconnected.addEdge(2, 3);
    disconnected.addEdge(4, 5);

    require(!disconnected.undirectedDSU().hasCycle,
            "Disconnected acyclic graph");

    Graph empty(0, GraphType::Directed);

    require(!empty.directedDFS().hasCycle, "Empty DFS");
    require(!empty.directedBFS().hasCycle, "Empty BFS");

    bool invalidVertexRejected = false;

    try {
        tree.addEdge(0, 10);
    } catch (const out_of_range&) {
        invalidVertexRejected = true;
    }

    require(invalidVertexRejected, "Invalid vertex");

    cout << "All C++17 tests passed.\n";
}

int main() {
    try {
        runTests();

        cout << "\nDIRECTED GRAPH\n";

        Graph directed(5, GraphType::Directed);

        for (const auto& edge :
             vector<pair<int, int>>{
                 {0, 1}, {1, 2}, {2, 3}, {3, 1}, {3, 4}
             }) {
            directed.addEdge(edge.first, edge.second);
        }

        printResult(directed.directedDFS());
        printResult(directed.directedBFS());

        cout << "\nUNDIRECTED GRAPH\n";

        Graph undirected(4, GraphType::Undirected);

        for (const auto& edge :
             vector<pair<int, int>>{
                 {0, 1}, {1, 2}, {2, 0}, {2, 3}
             }) {
            undirected.addEdge(edge.first, edge.second);
        }

        printResult(undirected.undirectedDFS());
        printResult(undirected.undirectedBFS());
        printResult(undirected.undirectedDSU());

        cout << "\nGraph vertices: "
             << undirected.vertices()
             << "\nGraph edges: "
             << undirected.edgeCount()
             << '\n';

    } catch (const exception& error) {
        cerr << "Execution error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
