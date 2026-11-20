#include <algorithm>
#include <chrono>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <set>
#include <stack>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

using namespace std;

enum class GraphType {
    Directed,
    Undirected
};

class Graph {
private:
    GraphType type;
    map<int, vector<int>> adjacency;

public:
    explicit Graph(GraphType graphType = GraphType::Undirected)
        : type(graphType) {}

    void addVertex(int vertex) {
        adjacency.try_emplace(vertex);
    }

    void addEdge(int source, int destination) {
        addVertex(source);
        addVertex(destination);

        auto& neighbors = adjacency.at(source);

        if (find(neighbors.begin(), neighbors.end(), destination)
            == neighbors.end()) {
            neighbors.push_back(destination);
        }

        if (type == GraphType::Undirected) {
            auto& reverseNeighbors = adjacency.at(destination);

            if (find(
                    reverseNeighbors.begin(),
                    reverseNeighbors.end(),
                    source
                ) == reverseNeighbors.end()) {
                reverseNeighbors.push_back(source);
            }
        }
    }

    bool contains(int vertex) const {
        return adjacency.find(vertex) != adjacency.end();
    }

    const vector<int>& neighbors(int vertex) const {
        auto it = adjacency.find(vertex);

        if (it == adjacency.end()) {
            throw invalid_argument("Unknown vertex.");
        }

        return it->second;
    }

    const map<int, vector<int>>& getAdjacency() const {
        return adjacency;
    }

    GraphType getType() const {
        return type;
    }

    size_t vertexCount() const {
        return adjacency.size();
    }
};


struct DFSResult {
    vector<int> traversal;
    unordered_map<int, int> parent;
    unordered_map<int, int> depth;
    unordered_map<int, int> discoveryTime;
    unordered_map<int, int> finishTime;
};


class DFSEngine {
private:
    const Graph& graph;

public:
    explicit DFSEngine(const Graph& graphReference)
        : graph(graphReference) {}

    DFSResult recursive(int start, int maxDepth = -1) const {
        if (!graph.contains(start)) {
            throw invalid_argument("Starting vertex does not exist.");
        }

        if (maxDepth < -1) {
            throw invalid_argument("Invalid maximum depth.");
        }

        DFSResult result;
        unordered_set<int> visited;
        int clock = 0;

        function<void(int, int)> explore =
            [&](int vertex, int depth) {
                visited.insert(vertex);
                result.traversal.push_back(vertex);
                result.depth[vertex] = depth;
                result.discoveryTime[vertex] = ++clock;

                if (maxDepth == -1 || depth < maxDepth) {
                    for (int neighbor : graph.neighbors(vertex)) {
                        if (!visited.count(neighbor)) {
                            result.parent[neighbor] = vertex;
                            explore(neighbor, depth + 1);
                        }
                    }
                }

                result.finishTime[vertex] = ++clock;
            };

        explore(start, 0);
        return result;
    }

    DFSResult iterative(int start) const {
        if (!graph.contains(start)) {
            throw invalid_argument("Starting vertex does not exist.");
        }

        DFSResult result;

        unordered_set<int> visited;
        vector<int> stack;

        visited.insert(start);
        stack.push_back(start);
        result.depth[start] = 0;

        while (!stack.empty()) {
            int vertex = stack.back();
            stack.pop_back();

            result.traversal.push_back(vertex);

            const auto& neighbors = graph.neighbors(vertex);

            for (auto it = neighbors.rbegin();
                 it != neighbors.rend(); ++it) {

                int neighbor = *it;

                if (!visited.count(neighbor)) {
                    visited.insert(neighbor);
                    result.parent[neighbor] = vertex;
                    result.depth[neighbor] =
                        result.depth[vertex] + 1;
                    stack.push_back(neighbor);
                }
            }
        }

        return result;
    }

    vector<vector<int>> connectedComponents() const {
        if (graph.getType() != GraphType::Undirected) {
            throw logic_error(
                "Connected components require an undirected graph."
            );
        }

        unordered_set<int> visited;
        vector<vector<int>> components;

        for (const auto& [vertex, neighbors] : graph.getAdjacency()) {
            if (visited.count(vertex)) {
                continue;
            }

            vector<int> component;
            vector<int> stack = {vertex};
            visited.insert(vertex);

            while (!stack.empty()) {
                int current = stack.back();
                stack.pop_back();

                component.push_back(current);

                for (int neighbor : graph.neighbors(current)) {
                    if (!visited.count(neighbor)) {
                        visited.insert(neighbor);
                        stack.push_back(neighbor);
                    }
                }
            }

            components.push_back(move(component));
        }

        return components;
    }

    bool hasPath(int source, int target) const {
        if (!graph.contains(source) || !graph.contains(target)) {
            throw invalid_argument("Invalid path endpoint.");
        }

        unordered_set<int> visited;
        vector<int> stack = {source};

        while (!stack.empty()) {
            int vertex = stack.back();
            stack.pop_back();

            if (vertex == target) {
                return true;
            }

            if (!visited.insert(vertex).second) {
                continue;
            }

            for (int neighbor : graph.neighbors(vertex)) {
                if (!visited.count(neighbor)) {
                    stack.push_back(neighbor);
                }
            }
        }

        return false;
    }

    vector<int> topologicalSort() const {
        if (graph.getType() != GraphType::Directed) {
            throw logic_error(
                "Topological sorting requires a directed graph."
            );
        }

        unordered_map<int, int> state;
        vector<int> order;

        // 0 = unvisited, 1 = active, 2 = finished.
        function<void(int)> explore = [&](int vertex) {
            state[vertex] = 1;

            for (int neighbor : graph.neighbors(vertex)) {
                if (state[neighbor] == 1) {
                    throw logic_error("Directed cycle detected.");
                }

                if (state[neighbor] == 0) {
                    explore(neighbor);
                }
            }

            state[vertex] = 2;
            order.push_back(vertex);
        };

        for (const auto& [vertex, neighbors] : graph.getAdjacency()) {
            if (state[vertex] == 0) {
                explore(vertex);
            }
        }

        reverse(order.begin(), order.end());
        return order;
    }
};


void printTraversal(const string& label, const vector<int>& values) {
    cout << label;

    for (int value : values) {
        cout << value << " ";
    }

    cout << '\n';
}

void runTests() {
    Graph graph;

    graph.addEdge(1, 2);
    graph.addEdge(1, 3);
    graph.addEdge(2, 4);
    graph.addEdge(2, 5);
    graph.addEdge(3, 6);
    graph.addEdge(5, 6);
    graph.addEdge(7, 8);
    graph.addVertex(9);

    DFSEngine engine(graph);

    auto recursive = engine.recursive(1);
    auto iterative = engine.iterative(1);

    if (recursive.traversal != iterative.traversal) {
        throw runtime_error("DFS traversal mismatch.");
    }

    auto components = engine.connectedComponents();

    if (components.size() != 3) {
        throw runtime_error("Connected component test failed.");
    }

    if (!engine.hasPath(1, 6)) {
        throw runtime_error("Path existence test failed.");
    }

    if (engine.hasPath(1, 8)) {
        throw runtime_error("Disconnected path test failed.");
    }

    if (engine.hasPath(9, 9) != true) {
        throw runtime_error("Self-path test failed.");
    }

    Graph directed(GraphType::Directed);
    directed.addEdge(10, 11);
    directed.addEdge(11, 12);
    directed.addEdge(10, 13);

    DFSEngine directedEngine(directed);

    auto order = directedEngine.topologicalSort();

    if (order.size() != 4) {
        throw runtime_error("Topological sort test failed.");
    }

    Graph cyclic(GraphType::Directed);
    cyclic.addEdge(20, 21);
    cyclic.addEdge(21, 22);
    cyclic.addEdge(22, 20);

    try {
        DFSEngine cyclicEngine(cyclic);
        cyclicEngine.topologicalSort();
        throw runtime_error("Cycle detection test failed.");
    } catch (const logic_error&) {
        // Expected cycle detection.
    }

    try {
        engine.iterative(100);
        throw runtime_error("Invalid vertex test failed.");
    } catch (const invalid_argument&) {
        // Expected validation.
    }

    cout << "All C++17 DFS tests passed.\n";
}


int main() {
    try {
        runTests();

        Graph graph;

        graph.addEdge(1, 2);
        graph.addEdge(1, 3);
        graph.addEdge(2, 4);
        graph.addEdge(2, 5);
        graph.addEdge(3, 6);
        graph.addEdge(5, 6);
        graph.addEdge(7, 8);
        graph.addVertex(9);

        DFSEngine engine(graph);

        auto recursive = engine.recursive(1);
        auto iterative = engine.iterative(1);

        cout << "\nRecursive DFS:\n";
        printTraversal("Traversal: ", recursive.traversal);

        cout << "\nIterative DFS:\n";
        printTraversal("Traversal: ", iterative.traversal);

        cout << "\nDFS parent relationships:\n";

        for (const auto& [vertex, parent] : recursive.parent) {
            cout << parent << " -> " << vertex << '\n';
        }

        cout << "\nConnected components:\n";

        auto components = engine.connectedComponents();

        for (size_t i = 0; i < components.size(); ++i) {
            cout << "Component " << i + 1 << ": ";

            for (int vertex : components[i]) {
                cout << vertex << " ";
            }

            cout << '\n';
        }

        cout << "\nPath 1 -> 6: "
             << (engine.hasPath(1, 6) ? "Yes" : "No") << '\n';

        cout << "Path 1 -> 8: "
             << (engine.hasPath(1, 8) ? "Yes" : "No") << '\n';

        Graph directed(GraphType::Directed);

        directed.addEdge(1, 2);
        directed.addEdge(1, 3);
        directed.addEdge(2, 4);
        directed.addEdge(3, 4);

        DFSEngine directedEngine(directed);

        cout << "\nTopological ordering:\n";
        printTraversal("Order: ", directedEngine.topologicalSort());

        cout << "\nDepth-limited recursive DFS:\n";
        auto limited = engine.recursive(1, 1);
        printTraversal("Traversal: ", limited.traversal);

        // Benchmark traversal without including graph construction.
        auto beginning = chrono::steady_clock::now();
        auto benchmarkResult = engine.iterative(1);
        auto ending = chrono::steady_clock::now();

        auto elapsed =
            chrono::duration_cast<chrono::microseconds>(
                ending - beginning
            ).count();

        cout << "\nIterative DFS visited "
             << benchmarkResult.traversal.size()
             << " vertices in " << elapsed << " microseconds.\n";

    } catch (const exception& error) {
        cerr << "Execution error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
