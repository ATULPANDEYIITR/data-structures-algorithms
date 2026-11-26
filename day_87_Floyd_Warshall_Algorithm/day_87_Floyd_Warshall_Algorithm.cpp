#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <optional>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

using namespace std;

constexpr double INF = numeric_limits<double>::infinity();

enum class GraphStatus {
    Valid,
    NegativeCycle,
    InvalidInput
};

struct Edge {
    int source;
    int destination;
    double weight;
};

struct PathResult {
    bool reachable;
    double distance;
    vector<string> path;
};

class WeightedGraph {
private:
    vector<string> vertices;
    unordered_map<string, int> vertexIndex;
    vector<Edge> edges;

public:
    void addVertex(const string& name) {
        if (name.empty()) {
            throw invalid_argument("Vertex name cannot be empty");
        }

        if (vertexIndex.count(name)) {
            throw invalid_argument("Duplicate vertex: " + name);
        }

        int index = static_cast<int>(vertices.size());

        vertexIndex[name] = index;
        vertices.push_back(name);
    }

    void addEdge(
        const string& source,
        const string& destination,
        double weight,
        bool bidirectional = false
    ) {
        if (!isfinite(weight)) {
            throw invalid_argument("Edge weight must be finite");
        }

        auto sourceIt = vertexIndex.find(source);
        auto destinationIt = vertexIndex.find(destination);

        if (sourceIt == vertexIndex.end() ||
            destinationIt == vertexIndex.end()) {
            throw invalid_argument("Unknown vertex in edge");
        }

        edges.push_back({
            sourceIt->second,
            destinationIt->second,
            weight
        });

        if (bidirectional) {
            edges.push_back({
                destinationIt->second,
                sourceIt->second,
                weight
            });
        }
    }

    const vector<string>& getVertices() const {
        return vertices;
    }

    const vector<Edge>& getEdges() const {
        return edges;
    }

    int getIndex(const string& name) const {
        auto it = vertexIndex.find(name);

        if (it == vertexIndex.end()) {
            throw invalid_argument("Unknown vertex: " + name);
        }

        return it->second;
    }

    int size() const {
        return static_cast<int>(vertices.size());
    }
};

class FloydWarshallEngine {
private:
    const WeightedGraph& graph;

    vector<vector<double>> distance;
    vector<vector<optional<int>>> nextVertex;

    bool computed = false;

    void initialize() {
        int n = graph.size();

        distance.assign(n, vector<double>(n, INF));

        nextVertex.assign(
            n,
            vector<optional<int>>(n, nullopt)
        );

        for (int i = 0; i < n; ++i) {
            distance[i][i] = 0.0;
            nextVertex[i][i] = i;
        }

        for (const Edge& edge : graph.getEdges()) {
            int u = edge.source;
            int v = edge.destination;

            if (edge.weight < distance[u][v]) {
                distance[u][v] = edge.weight;
                nextVertex[u][v] = v;
            }
        }
    }

public:
    explicit FloydWarshallEngine(const WeightedGraph& inputGraph)
        : graph(inputGraph) {
        if (graph.size() == 0) {
            throw invalid_argument("Graph cannot be empty");
        }
    }

    GraphStatus compute() {
        initialize();

        const int n = graph.size();

        /*
         * Dynamic programming:
         *
         * D[i][j] = minimum distance from i to j.
         *
         * At iteration k, paths may use vertices
         * 0 through k as intermediate vertices.
         *
         * Recurrence:
         *
         * D(i,j) = min(D(i,j), D(i,k) + D(k,j))
         */

        for (int k = 0; k < n; ++k) {
            for (int i = 0; i < n; ++i) {

                if (isinf(distance[i][k])) {
                    continue;
                }

                for (int j = 0; j < n; ++j) {

                    if (isinf(distance[k][j])) {
                        continue;
                    }

                    double candidate =
                        distance[i][k] + distance[k][j];

                    if (!isfinite(candidate)) {
                        throw overflow_error(
                            "Distance arithmetic overflow"
                        );
                    }

                    if (candidate < distance[i][j]) {
                        distance[i][j] = candidate;

                        // Preserve the first hop for path reconstruction.
                        nextVertex[i][j] = nextVertex[i][k];
                    }
                }
            }
        }

        for (int i = 0; i < n; ++i) {
            if (distance[i][i] < 0.0) {
                computed = false;
                return GraphStatus::NegativeCycle;
            }
        }

        computed = true;
        return GraphStatus::Valid;
    }

    double getDistance(
        const string& source,
        const string& destination
    ) const {
        if (!computed) {
            throw logic_error("Run successful computation first");
        }

        int i = graph.getIndex(source);
        int j = graph.getIndex(destination);

        return distance[i][j];
    }

    PathResult getPath(
        const string& source,
        const string& destination
    ) const {
        if (!computed) {
            throw logic_error("Run successful computation first");
        }

        int i = graph.getIndex(source);
        int j = graph.getIndex(destination);

        if (isinf(distance[i][j])) {
            return {false, INF, {}};
        }

        vector<string> path;

        int current = i;
        const int n = graph.size();

        path.push_back(graph.getVertices()[current]);

        for (int step = 0; step < n; ++step) {

            if (current == j) {
                return {
                    true,
                    distance[i][j],
                    path
                };
            }

            if (!nextVertex[current][j].has_value()) {
                return {false, INF, {}};
            }

            current = nextVertex[current][j].value();

            path.push_back(graph.getVertices()[current]);
        }

        throw logic_error(
            "Path reconstruction exceeded vertex limit"
        );
    }

    void printMatrix() const {
        if (!computed) {
            throw logic_error("No valid shortest-path matrix");
        }

        const auto& vertices = graph.getVertices();

        cout << "\nALL-PAIRS SHORTEST DISTANCES\n";

        cout << left << setw(12) << "From/To";

        for (const string& vertex : vertices) {
            cout << right << setw(12) << vertex;
        }

        cout << '\n';

        for (int i = 0; i < graph.size(); ++i) {
            cout << left << setw(12) << vertices[i];

            for (int j = 0; j < graph.size(); ++j) {
                if (isinf(distance[i][j])) {
                    cout << right << setw(12) << "INF";
                } else {
                    cout << right << setw(12)
                         << distance[i][j];
                }
            }

            cout << '\n';
        }
    }
};

void displayPath(
    const FloydWarshallEngine& engine,
    const string& source,
    const string& destination
) {
    PathResult result = engine.getPath(source, destination);

    cout << source << " -> " << destination << ": ";

    if (!result.reachable) {
        cout << "Unreachable\n";
        return;
    }

    for (size_t i = 0; i < result.path.size(); ++i) {
        if (i > 0) {
            cout << " -> ";
        }

        cout << result.path[i];
    }

    cout << " | Distance: " << result.distance << '\n';
}

void testCorrectness() {
    WeightedGraph graph;

    for (const string& name : {"A", "B", "C", "D"}) {
        graph.addVertex(name);
    }

    graph.addEdge("A", "B", 3);
    graph.addEdge("B", "C", 2);
    graph.addEdge("A", "C", 10);
    graph.addEdge("C", "D", 1);

    FloydWarshallEngine engine(graph);

    if (engine.compute() != GraphStatus::Valid) {
        throw runtime_error("Unexpected computation failure");
    }

    if (engine.getDistance("A", "C") != 5 ||
        engine.getDistance("A", "D") != 6) {
        throw runtime_error("Shortest-distance test failed");
    }

    PathResult path = engine.getPath("A", "D");

    vector<string> expected = {"A", "B", "C", "D"};

    if (path.path != expected) {
        throw runtime_error("Path reconstruction test failed");
    }

    if (!isinf(engine.getDistance("D", "A"))) {
        throw runtime_error("Unreachable-path test failed");
    }

    WeightedGraph negative;

    negative.addVertex("X");
    negative.addVertex("Y");
    negative.addVertex("Z");

    negative.addEdge("X", "Y", 5);
    negative.addEdge("Y", "Z", -2);

    FloydWarshallEngine negativeEngine(negative);

    if (negativeEngine.compute() != GraphStatus::Valid ||
        negativeEngine.getDistance("X", "Z") != 3) {
        throw runtime_error("Negative-edge test failed");
    }

    WeightedGraph cycle;

    cycle.addVertex("P");
    cycle.addVertex("Q");

    cycle.addEdge("P", "Q", -2);
    cycle.addEdge("Q", "P", 1);

    FloydWarshallEngine cycleEngine(cycle);

    if (cycleEngine.compute() != GraphStatus::NegativeCycle) {
        throw runtime_error("Negative-cycle test failed");
    }

    cout << "\nALL C++ TESTS PASSED\n";
}

int main() {
    try {
        WeightedGraph graph;

        vector<string> locations = {
            "Delhi",
            "Agra",
            "Jaipur",
            "Lucknow",
            "Kanpur",
            "Mumbai"
        };

        for (const string& location : locations) {
            graph.addVertex(location);
        }

        vector<Edge> routes = {
            {0, 1, 2},
            {0, 2, 5},
            {1, 2, 1},
            {1, 3, 4},
            {2, 3, 2},
            {3, 4, 1},
            {4, 5, 8},
            {2, 5, 12},
            {0, 4, 15}
        };

        for (const Edge& route : routes) {
            graph.addEdge(
                locations[route.source],
                locations[route.destination],
                route.weight
            );
        }

        FloydWarshallEngine engine(graph);

        cout << "FLOYD-WARSHALL SHORTEST-PATH ENGINE\n";

        GraphStatus status = engine.compute();

        if (status == GraphStatus::NegativeCycle) {
            cerr << "Graph contains a negative cycle\n";
            return 1;
        }

        engine.printMatrix();

        cout << "\nROUTE QUERIES\n";

        displayPath(engine, "Delhi", "Mumbai");
        displayPath(engine, "Delhi", "Kanpur");
        displayPath(engine, "Agra", "Mumbai");
        displayPath(engine, "Mumbai", "Delhi");

        testCorrectness();

        cout << "\nCOMPLEXITY\n";
        cout << "Time: O(V^3)\n";
        cout << "Space: O(V^2)\n";
        cout << "Path reconstruction: O(V)\n";

        return 0;

    } catch (const exception& error) {
        cerr << "Application error: "
             << error.what() << '\n';

        return 1;
    }
}
