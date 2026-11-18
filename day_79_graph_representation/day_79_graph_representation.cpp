#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstddef>
#include <iomanip>
#include <iostream>
#include <limits>
#include <queue>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

using namespace std;

enum class Representation {
    AdjacencyMatrix,
    AdjacencyList,
    EdgeList
};

struct Edge {
    int source;
    int target;
    double weight;

    bool operator==(const Edge& other) const {
        return source == other.source &&
               target == other.target &&
               weight == other.weight;
    }
};

class Graph {
protected:
    int vertexCount;
    bool directed;

    void validateVertex(int vertex) const {
        if (vertex < 0 || vertex >= vertexCount) {
            throw out_of_range("Invalid vertex index.");
        }
    }

    void validateEdge(int source, int target, double weight) const {
        validateVertex(source);
        validateVertex(target);

        if (!isfinite(weight)) {
            throw invalid_argument("Edge weight must be finite.");
        }
    }

public:
    Graph(int vertices, bool isDirected = false)
        : vertexCount(vertices), directed(isDirected) {

        if (vertices < 0) {
            throw invalid_argument("Negative vertex count.");
        }
    }

    virtual ~Graph() = default;

    int vertices() const {
        return vertexCount;
    }

    bool isDirected() const {
        return directed;
    }

    virtual void addEdge(int source, int target, double weight = 1.0) = 0;
    virtual bool removeEdge(int source, int target) = 0;
    virtual bool hasEdge(int source, int target) const = 0;

    virtual vector<pair<int, double>>
    neighbors(int vertex) const = 0;

    virtual vector<Edge> edges() const = 0;

    virtual size_t memoryEstimate() const = 0;

    vector<int> bfs(int start) const {
        validateVertex(start);

        vector<bool> visited(vertexCount, false);
        vector<int> result;
        queue<int> pending;

        visited[start] = true;
        pending.push(start);

        while (!pending.empty()) {
            int current = pending.front();
            pending.pop();

            result.push_back(current);

            for (const auto& [neighbor, weight] : neighbors(current)) {
                (void)weight;

                if (!visited[neighbor]) {
                    visited[neighbor] = true;
                    pending.push(neighbor);
                }
            }
        }

        return result;
    }

    vector<int> dfs(int start) const {
        validateVertex(start);

        vector<bool> visited(vertexCount, false);
        vector<int> result;
        vector<int> stack = {start};

        while (!stack.empty()) {
            int current = stack.back();
            stack.pop_back();

            if (visited[current]) {
                continue;
            }

            visited[current] = true;
            result.push_back(current);

            auto adjacent = neighbors(current);

            sort(
                adjacent.begin(),
                adjacent.end(),
                [](const auto& first, const auto& second) {
                    return first.first > second.first;
                }
            );

            for (const auto& [neighbor, weight] : adjacent) {
                (void)weight;

                if (!visited[neighbor]) {
                    stack.push_back(neighbor);
                }
            }
        }

        return result;
    }

    vector<double> dijkstra(int start) const {
        validateVertex(start);

        for (const auto& edge : edges()) {
            if (edge.weight < 0) {
                throw invalid_argument(
                    "Dijkstra requires non-negative weights."
                );
            }
        }

        const double INF = numeric_limits<double>::infinity();

        vector<double> distance(vertexCount, INF);

        using State = pair<double, int>;

        priority_queue<
            State,
            vector<State>,
            greater<State>
        > pending;

        distance[start] = 0.0;
        pending.push({0.0, start});

        while (!pending.empty()) {
            auto [currentDistance, current] = pending.top();
            pending.pop();

            if (currentDistance != distance[current]) {
                continue;
            }

            for (const auto& [neighbor, weight] : neighbors(current)) {
                double candidate = currentDistance + weight;

                if (candidate < distance[neighbor]) {
                    distance[neighbor] = candidate;
                    pending.push({candidate, neighbor});
                }
            }
        }

        return distance;
    }
};

class AdjacencyMatrixGraph : public Graph {
private:
    vector<vector<double>> matrix;

    static constexpr double ABSENT =
        numeric_limits<double>::infinity();

public:
    AdjacencyMatrixGraph(int vertices, bool isDirected = false)
        : Graph(vertices, isDirected),
          matrix(
              vertices,
              vector<double>(vertices, ABSENT)
          ) {}

    void addEdge(int source, int target, double weight = 1.0) override {
        validateEdge(source, target, weight);

        matrix[source][target] = weight;

        if (!directed) {
            matrix[target][source] = weight;
        }
    }

    bool removeEdge(int source, int target) override {
        validateVertex(source);
        validateVertex(target);

        bool existed = isfinite(matrix[source][target]);

        matrix[source][target] = ABSENT;

        if (!directed) {
            matrix[target][source] = ABSENT;
        }

        return existed;
    }

    bool hasEdge(int source, int target) const override {
        validateVertex(source);
        validateVertex(target);

        return isfinite(matrix[source][target]);
    }

    vector<pair<int, double>>
    neighbors(int vertex) const override {
        validateVertex(vertex);

        vector<pair<int, double>> result;

        for (int target = 0; target < vertexCount; target++) {
            if (isfinite(matrix[vertex][target])) {
                result.push_back({target, matrix[vertex][target]});
            }
        }

        return result;
    }

    vector<Edge> edges() const override {
        vector<Edge> result;

        for (int source = 0; source < vertexCount; source++) {
            for (int target = 0; target < vertexCount; target++) {
                if (
                    isfinite(matrix[source][target]) &&
                    (directed || target >= source)
                ) {
                    result.push_back({
                        source,
                        target,
                        matrix[source][target]
                    });
                }
            }
        }

        return result;
    }

    size_t memoryEstimate() const override {
        return sizeof(double) *
               static_cast<size_t>(vertexCount) *
               static_cast<size_t>(vertexCount);
    }
};

class AdjacencyListGraph : public Graph {
private:
    vector<unordered_map<int, double>> adjacency;

public:
    AdjacencyListGraph(int vertices, bool isDirected = false)
        : Graph(vertices, isDirected),
          adjacency(vertices) {}

    void addEdge(int source, int target, double weight = 1.0) override {
        validateEdge(source, target, weight);

        adjacency[source][target] = weight;

        if (!directed) {
            adjacency[target][source] = weight;
        }
    }

    bool removeEdge(int source, int target) override {
        validateVertex(source);
        validateVertex(target);

        bool existed = adjacency[source].erase(target) > 0;

        if (!directed) {
            adjacency[target].erase(source);
        }

        return existed;
    }

    bool hasEdge(int source, int target) const override {
        validateVertex(source);
        validateVertex(target);

        return adjacency[source].find(target) !=
               adjacency[source].end();
    }

    vector<pair<int, double>>
    neighbors(int vertex) const override {
        validateVertex(vertex);

        vector<pair<int, double>> result(
            adjacency[vertex].begin(),
            adjacency[vertex].end()
        );

        sort(result.begin(), result.end());

        return result;
    }

    vector<Edge> edges() const override {
        vector<Edge> result;

        for (int source = 0; source < vertexCount; source++) {
            for (const auto& [target, weight] : adjacency[source]) {
                if (directed || target >= source) {
                    result.push_back({source, target, weight});
                }
            }
        }

        sort(
            result.begin(),
            result.end(),
            [](const Edge& a, const Edge& b) {
                return make_pair(a.source, a.target) <
                       make_pair(b.source, b.target);
            }
        );

        return result;
    }

    size_t memoryEstimate() const override {
        size_t total =
            sizeof(unordered_map<int, double>) * adjacency.size();

        for (const auto& neighborsMap : adjacency) {
            total += neighborsMap.size() *
                     (sizeof(pair<const int, double>) + 2 * sizeof(void*));
        }

        return total;
    }
};

class EdgeListGraph : public Graph {
private:
    vector<Edge> data;

    pair<int, int> normalize(int source, int target) const {
        if (!directed && source > target) {
            swap(source, target);
        }

        return {source, target};
    }

public:
    EdgeListGraph(int vertices, bool isDirected = false)
        : Graph(vertices, isDirected) {}

    void addEdge(int source, int target, double weight = 1.0) override {
        validateEdge(source, target, weight);

        auto [normalizedSource, normalizedTarget] =
            normalize(source, target);

        for (auto& edge : data) {
            if (
                edge.source == normalizedSource &&
                edge.target == normalizedTarget
            ) {
                edge.weight = weight;
                return;
            }
        }

        data.push_back({
            normalizedSource,
            normalizedTarget,
            weight
        });
    }

    bool removeEdge(int source, int target) override {
        validateVertex(source);
        validateVertex(target);

        auto [normalizedSource, normalizedTarget] =
            normalize(source, target);

        auto position = find_if(
            data.begin(),
            data.end(),
            [&](const Edge& edge) {
                return edge.source == normalizedSource &&
                       edge.target == normalizedTarget;
            }
        );

        if (position == data.end()) {
            return false;
        }

        data.erase(position);
        return true;
    }

    bool hasEdge(int source, int target) const override {
        validateVertex(source);
        validateVertex(target);

        auto [normalizedSource, normalizedTarget] =
            normalize(source, target);

        return any_of(
            data.begin(),
            data.end(),
            [&](const Edge& edge) {
                return edge.source == normalizedSource &&
                       edge.target == normalizedTarget;
            }
        );
    }

    vector<pair<int, double>>
    neighbors(int vertex) const override {
        validateVertex(vertex);

        vector<pair<int, double>> result;

        for (const auto& edge : data) {
            if (edge.source == vertex) {
                result.push_back({edge.target, edge.weight});
            }

            if (
                !directed &&
                edge.target == vertex &&
                edge.source != vertex
            ) {
                result.push_back({edge.source, edge.weight});
            }
        }

        sort(result.begin(), result.end());

        return result;
    }

    vector<Edge> edges() const override {
        return data;
    }

    size_t memoryEstimate() const override {
        return data.capacity() * sizeof(Edge);
    }
};

unique_ptr<Graph> createGraph(
    Representation representation,
    int vertices,
    bool directed = false
) {
    switch (representation) {
        case Representation::AdjacencyMatrix:
            return make_unique<AdjacencyMatrixGraph>(
                vertices, directed
            );

        case Representation::AdjacencyList:
            return make_unique<AdjacencyListGraph>(
                vertices, directed
            );

        case Representation::EdgeList:
            return make_unique<EdgeListGraph>(
                vertices, directed
            );
    }

    throw invalid_argument("Unknown graph representation.");
}

vector<Edge> sampleEdges() {
    return {
        {0, 1, 4},
        {0, 2, 2},
        {1, 2, 1},
        {1, 3, 5},
        {2, 3, 8},
        {2, 4, 10},
        {3, 4, 2},
        {4, 5, 3}
    };
}

void populate(Graph& graph) {
    for (const auto& edge : sampleEdges()) {
        graph.addEdge(
            edge.source,
            edge.target,
            edge.weight
        );
    }
}

void printVector(const vector<int>& values) {
    cout << "[";

    for (size_t i = 0; i < values.size(); i++) {
        if (i) cout << ", ";
        cout << values[i];
    }

    cout << "]";
}

void printDistances(const vector<double>& distances) {
    cout << "[";

    for (size_t i = 0; i < distances.size(); i++) {
        if (i) cout << ", ";

        if (isinf(distances[i])) {
            cout << "INF";
        } else {
            cout << distances[i];
        }
    }

    cout << "]";
}

void runTests() {
    vector<Representation> types = {
        Representation::AdjacencyMatrix,
        Representation::AdjacencyList,
        Representation::EdgeList
    };

    for (auto type : types) {
        auto graph = createGraph(type, 6);
        populate(*graph);

        if (graph->edges().size() != 8) {
            throw runtime_error("Edge count test failed.");
        }

        if (graph->bfs(0) != vector<int>({0, 1, 2, 3, 4, 5})) {
            throw runtime_error("BFS test failed.");
        }

        auto distances = graph->dijkstra(0);

        vector<double> expected = {
            0, 3, 2, 8, 10, 13
        };

        if (distances != expected) {
            throw runtime_error("Dijkstra test failed.");
        }

        if (!graph->removeEdge(0, 1)) {
            throw runtime_error("Edge removal test failed.");
        }

        if (graph->hasEdge(0, 1)) {
            throw runtime_error("Edge still exists.");
        }

        graph->addEdge(0, 1, 4);
    }

    AdjacencyListGraph directed(3, true);

    directed.addEdge(0, 1);

    if (directed.hasEdge(1, 0)) {
        throw runtime_error("Directed edge test failed.");
    }

    AdjacencyListGraph negative(2, true);
    negative.addEdge(0, 1, -1);

    bool rejected = false;

    try {
        negative.dijkstra(0);
    } catch (const invalid_argument&) {
        rejected = true;
    }

    if (!rejected) {
        throw runtime_error("Negative weight was accepted.");
    }

    AdjacencyListGraph empty(0);

    if (!empty.edges().empty()) {
        throw runtime_error("Empty graph test failed.");
    }

    cout << "All C++17 graph tests passed.\n";
}

void benchmark(const Graph& graph, int repetitions = 10000) {
    using Clock = chrono::steady_clock;

    if (repetitions <= 0 || graph.vertices() == 0) {
        return;
    }

    volatile size_t sink = 0;

    auto start = Clock::now();

    for (int i = 0; i < repetitions; i++) {
        sink += graph.hasEdge(0, graph.vertices() - 1);
    }

    auto lookupTime = chrono::duration<double, milli>(
        Clock::now() - start
    ).count();

    start = Clock::now();

    for (int i = 0; i < repetitions; i++) {
        sink += graph.neighbors(0).size();
    }

    auto neighborTime = chrono::duration<double, milli>(
        Clock::now() - start
    ).count();

    start = Clock::now();

    for (int i = 0; i < repetitions; i++) {
        sink += graph.edges().size();
    }

    auto enumerationTime = chrono::duration<double, milli>(
        Clock::now() - start
    ).count();

    cout << fixed << setprecision(4);
    cout << "Edge lookup: " << lookupTime << " ms\n";
    cout << "Neighbor lookup: " << neighborTime << " ms\n";
    cout << "Edge enumeration: " << enumerationTime << " ms\n";
    cout << "Estimated storage: "
         << graph.memoryEstimate() << " bytes\n";

    (void)sink;
}

int main() {
    try {
        cout << "GRAPH REPRESENTATION ENGINE\n";
        cout << "===========================\n\n";

        runTests();

        vector<pair<Representation, string>> types = {
            {
                Representation::AdjacencyMatrix,
                "Adjacency Matrix"
            },
            {
                Representation::AdjacencyList,
                "Adjacency List"
            },
            {
                Representation::EdgeList,
                "Edge List"
            }
        };

        for (const auto& [type, name] : types) {
            auto graph = createGraph(type, 6);
            populate(*graph);

            cout << "\n" << name << "\n";
            cout << "---------------------------\n";

            cout << "Vertices: " << graph->vertices() << "\n";
            cout << "Edges: " << graph->edges().size() << "\n";

            cout << "BFS: ";
            printVector(graph->bfs(0));
            cout << "\n";

            cout << "DFS: ";
            printVector(graph->dfs(0));
            cout << "\n";

            cout << "Shortest distances: ";
            printDistances(graph->dijkstra(0));
            cout << "\n";

            benchmark(*graph);
        }

        cout << "\nRepresentation trade-offs\n";
        cout << "---------------------------\n";
        cout << "Matrix: O(V^2) space, O(1) edge lookup.\n";
        cout << "List: O(V + E) space, efficient neighbor iteration.\n";
        cout << "Edge list: O(E) space, O(E) edge lookup.\n";

        cout << "\nExecution completed successfully.\n";

    } catch (const exception& error) {
        cerr << "Error: " << error.what() << "\n";
        return 1;
    }

    return 0;
}
