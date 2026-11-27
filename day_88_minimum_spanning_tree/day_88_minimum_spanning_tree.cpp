#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <set>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>

using namespace std;

/*
 * Minimum Spanning Tree: Repository-independent Network
 * Governance and Merge-Style Eligibility Engine
 *
 * Domain: Enterprise infrastructure connection planning.
 *
 * Implements:
 * - Weighted undirected graph
 * - Kruskal's algorithm
 * - Prim's algorithm
 * - Union-Find with path compression and union by rank
 * - Mandatory and forbidden connection policies
 * - Individual and aggregate budget constraints
 * - Disconnected network handling
 * - Minimum spanning forest
 * - Independent algorithm verification
 *
 * Compile: g++ -std=c++17 -O2 -Wall -Wextra -pedantic mst.cpp -o mst
 */

enum class Algorithm {
    Kruskal,
    Prim
};

struct Edge {
    string source;
    string destination;
    double weight;

    Edge(
        string s,
        string d,
        double w
    ) : source(move(s)),
        destination(move(d)),
        weight(w) {

        if (source.empty() || destination.empty()) {
            throw invalid_argument("Empty vertex identifier.");
        }

        if (source == destination) {
            throw invalid_argument("Self-loop not permitted.");
        }

        if (!isfinite(weight) || weight < 0) {
            throw invalid_argument(
                "Weight must be finite and nonnegative."
            );
        }
    }

    auto normalized() const {
        return minmax(source, destination);
    }
};

class DisjointSet {
private:
    vector<int> parent;
    vector<int> rank;

public:
    explicit DisjointSet(int size)
        : parent(size), rank(size, 0) {
        iota(parent.begin(), parent.end(), 0);
    }

    int find(int vertex) {
        if (parent[vertex] != vertex) {
            parent[vertex] = find(parent[vertex]);
        }

        return parent[vertex];
    }

    bool unite(int first, int second) {
        int a = find(first);
        int b = find(second);

        if (a == b) return false;

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

struct MSTResult {
    Algorithm algorithm;
    vector<Edge> selected;
    double totalCost = 0;
    int vertexCount = 0;
    int componentCount = 0;

    bool connected() const {
        return componentCount <= 1;
    }

    int expectedEdgeCount() const {
        return vertexCount - componentCount;
    }
};

struct NetworkPolicy {
    bool requireConnected = true;
    double maximumTotalCost =
        numeric_limits<double>::infinity();

    double maximumIndividualCost =
        numeric_limits<double>::infinity();

    set<pair<string, string>> forbidden;
    set<pair<string, string>> mandatory;

    static pair<string, string> key(
        const string& first,
        const string& second
    ) {
        return minmax(first, second);
    }
};

struct PolicyEvaluation {
    bool eligible = true;
    vector<string> violations;
};

class NetworkGovernance {
private:
    string networkName;
    vector<string> vertices;
    vector<Edge> edges;
    map<string, int> index;

    int ensureVertex(const string& vertex) {
        if (vertex.empty()) {
            throw invalid_argument("Empty vertex.");
        }

        auto found = index.find(vertex);

        if (found != index.end()) {
            return found->second;
        }

        int id = static_cast<int>(vertices.size());

        vertices.push_back(vertex);
        index[vertex] = id;

        return id;
    }

    void validate() const {
        if (vertices.empty()) {
            throw runtime_error("Network has no vertices.");
        }

        for (const auto& edge : edges) {
            if (
                index.find(edge.source) == index.end() ||
                index.find(edge.destination) == index.end()
            ) {
                throw runtime_error(
                    "Edge references an unknown vertex."
                );
            }
        }
    }

public:
    explicit NetworkGovernance(string name)
        : networkName(move(name)) {

        if (networkName.empty()) {
            throw invalid_argument("Network name is required.");
        }
    }

    void addVertex(const string& vertex) {
        ensureVertex(vertex);
    }

    void addConnection(
        const string& source,
        const string& destination,
        double weight
    ) {
        Edge candidate(source, destination, weight);

        auto key = candidate.normalized();

        for (const auto& existing : edges) {
            if (existing.normalized() == key) {
                throw invalid_argument(
                    "Duplicate undirected connection."
                );
            }
        }

        ensureVertex(source);
        ensureVertex(destination);

        edges.push_back(move(candidate));
    }

    MSTResult kruskal() const {
        validate();

        vector<Edge> ordered = edges;

        sort(
            ordered.begin(),
            ordered.end(),
            [](const Edge& a, const Edge& b) {
                if (a.weight != b.weight) {
                    return a.weight < b.weight;
                }

                return a.normalized() < b.normalized();
            }
        );

        DisjointSet dsu(
            static_cast<int>(vertices.size())
        );

        MSTResult result{
            Algorithm::Kruskal,
            {},
            0,
            static_cast<int>(vertices.size()),
            static_cast<int>(vertices.size())
        };

        for (const auto& edge : ordered) {
            int u = index.at(edge.source);
            int v = index.at(edge.destination);

            if (dsu.unite(u, v)) {
                result.selected.push_back(edge);
                result.totalCost += edge.weight;
                result.componentCount--;

                if (result.componentCount == 1) break;
            }
        }

        return result;
    }

    MSTResult prim() const {
        validate();

        const int n = static_cast<int>(vertices.size());

        vector<vector<pair<int, double>>> adjacency(n);

        for (const auto& edge : edges) {
            int u = index.at(edge.source);
            int v = index.at(edge.destination);

            adjacency[u].push_back({v, edge.weight});
            adjacency[v].push_back({u, edge.weight});
        }

        using Candidate = tuple<
            double,
            int,
            int
        >;

        MSTResult result{
            Algorithm::Prim,
            {},
            0,
            n,
            0
        };

        vector<bool> visited(n, false);

        for (int start = 0; start < n; ++start) {
            if (visited[start]) continue;

            result.componentCount++;
            visited[start] = true;

            vector<Candidate> candidates;

            auto pushNeighbors = [&](int vertex) {
                for (auto [neighbor, weight] : adjacency[vertex]) {
                    if (!visited[neighbor]) {
                        candidates.emplace_back(
                            weight,
                            vertex,
                            neighbor
                        );
                    }
                }

                push_heap(
                    candidates.begin(),
                    candidates.end(),
                    greater<Candidate>()
                );
            };

            pushNeighbors(start);

            while (!candidates.empty()) {
                pop_heap(
                    candidates.begin(),
                    candidates.end(),
                    greater<Candidate>()
                );

                auto [weight, source, destination] =
                    candidates.back();

                candidates.pop_back();

                if (visited[destination]) continue;

                visited[destination] = true;

                result.selected.emplace_back(
                    vertices[source],
                    vertices[destination],
                    weight
                );

                result.totalCost += weight;

                pushNeighbors(destination);
            }
        }

        return result;
    }

    PolicyEvaluation evaluate(
        const MSTResult& result,
        const NetworkPolicy& policy
    ) const {
        PolicyEvaluation evaluation;

        auto reject = [&](const string& reason) {
            evaluation.eligible = false;
            evaluation.violations.push_back(reason);
        };

        if (policy.requireConnected && !result.connected()) {
            reject("Network must be fully connected.");
        }

        if (result.totalCost > policy.maximumTotalCost) {
            reject("Aggregate connection budget exceeded.");
        }

        set<pair<string, string>> selected;

        for (const auto& edge : result.selected) {
            auto key = NetworkPolicy::key(
                edge.source,
                edge.destination
            );

            selected.insert(key);

            if (edge.weight > policy.maximumIndividualCost) {
                reject(
                    "Individual connection exceeds cost limit: " +
                    edge.source + "-" + edge.destination
                );
            }

            if (policy.forbidden.count(key)) {
                reject(
                    "Forbidden connection selected: " +
                    edge.source + "-" + edge.destination
                );
            }
        }

        for (const auto& required : policy.mandatory) {
            if (!selected.count(required)) {
                reject(
                    "Mandatory connection missing: " +
                    required.first + "-" + required.second
                );
            }
        }

        return evaluation;
    }

    bool verify(const MSTResult& result) const {
        if (
            result.vertexCount !=
            static_cast<int>(vertices.size())
        ) {
            return false;
        }

        DisjointSet dsu(
            static_cast<int>(vertices.size())
        );

        double total = 0;

        for (const auto& edge : result.selected) {
            auto u = index.find(edge.source);
            auto v = index.find(edge.destination);

            if (
                u == index.end() ||
                v == index.end()
            ) {
                return false;
            }

            if (!dsu.unite(u->second, v->second)) {
                return false;
            }

            total += edge.weight;
        }

        return (
            static_cast<int>(result.selected.size()) ==
                result.expectedEdgeCount() &&
            dsu.components == result.componentCount &&
            abs(total - result.totalCost) < 1e-9
        );
    }

    void report(const MSTResult& result) const {
        cout << "\nNetwork: " << networkName << "\n";
        cout << "Algorithm: "
             << (
                 result.algorithm == Algorithm::Kruskal
                 ? "Kruskal"
                 : "Prim"
             )
             << "\n";

        cout << string(55, '-') << "\n";

        for (const auto& edge : result.selected) {
            cout << left << setw(12) << edge.source
                 << " -> "
                 << setw(12) << edge.destination
                 << " Cost: "
                 << edge.weight << "\n";
        }

        cout << string(55, '-') << "\n";

        cout << "Vertices: " << result.vertexCount << "\n";
        cout << "Edges: " << result.selected.size() << "\n";
        cout << "Components: " << result.componentCount << "\n";
        cout << "Total cost: " << result.totalCost << "\n";
        cout << "Connected: "
             << boolalpha << result.connected() << "\n";
    }
};

void runTests() {
    NetworkGovernance graph("Test Network");

    graph.addConnection("A", "B", 1);
    graph.addConnection("B", "C", 2);
    graph.addConnection("A", "C", 5);

    auto kruskal = graph.kruskal();
    auto prim = graph.prim();

    if (!graph.verify(kruskal) || !graph.verify(prim)) {
        throw runtime_error("MST verification failed.");
    }

    if (
        abs(kruskal.totalCost - 3.0) > 1e-9 ||
        abs(prim.totalCost - 3.0) > 1e-9
    ) {
        throw runtime_error("Incorrect MST cost.");
    }

    NetworkPolicy validPolicy;
    validPolicy.maximumTotalCost = 4;

    auto valid = graph.evaluate(
        kruskal,
        validPolicy
    );

    if (!valid.eligible) {
        throw runtime_error("Valid policy was rejected.");
    }

    NetworkPolicy invalidPolicy;
    invalidPolicy.maximumTotalCost = 2;

    auto invalid = graph.evaluate(
        kruskal,
        invalidPolicy
    );

    if (invalid.eligible) {
        throw runtime_error("Budget violation was accepted.");
    }

    NetworkGovernance disconnected("Disconnected Test");
    disconnected.addConnection("A", "B", 2);
    disconnected.addVertex("ISOLATED");

    auto forest = disconnected.kruskal();

    if (
        forest.connected() ||
        forest.componentCount != 2 ||
        forest.selected.size() != 1
    ) {
        throw runtime_error(
            "Disconnected forest calculation failed."
        );
    }

    bool duplicateRejected = false;

    try {
        graph.addConnection("B", "A", 1);
    } catch (const invalid_argument&) {
        duplicateRejected = true;
    }

    if (!duplicateRejected) {
        throw runtime_error(
            "Duplicate edge was not rejected."
        );
    }

    cout << "\nAll C++17 tests passed.\n";
}

int main() {
    try {
        cout << fixed << setprecision(2);

        NetworkGovernance network(
            "National Fiber Optic Infrastructure"
        );

        vector<Edge> connections = {
            Edge("A", "B", 4),
            Edge("A", "C", 3),
            Edge("B", "C", 1),
            Edge("B", "D", 2),
            Edge("C", "D", 4),
            Edge("C", "E", 5),
            Edge("D", "E", 2),
            Edge("D", "F", 6),
            Edge("E", "F", 3),
            Edge("A", "F", 10)
        };

        for (const auto& edge : connections) {
            network.addConnection(
                edge.source,
                edge.destination,
                edge.weight
            );
        }

        auto kruskal = network.kruskal();
        auto prim = network.prim();

        network.report(kruskal);

        if (
            abs(
                kruskal.totalCost -
                prim.totalCost
            ) > 1e-9
        ) {
            throw runtime_error(
                "Kruskal and Prim disagree."
            );
        }

        if (
            kruskal.selected.size() != 5 ||
            abs(kruskal.totalCost - 11.0) > 1e-9
        ) {
            throw runtime_error(
                "Unexpected MST result."
            );
        }

        NetworkPolicy policy;
        policy.requireConnected = true;
        policy.maximumTotalCost = 15;
        policy.maximumIndividualCost = 6;

        policy.forbidden.insert(
            NetworkPolicy::key("A", "F")
        );

        auto evaluation = network.evaluate(
            kruskal,
            policy
        );

        cout << "\nGovernance evaluation\n";
        cout << "Eligible: "
             << evaluation.eligible << "\n";

        for (const auto& violation : evaluation.violations) {
            cout << "Violation: " << violation << "\n";
        }

        if (!network.verify(kruskal)) {
            throw runtime_error(
                "Spanning tree integrity verification failed."
            );
        }

        runTests();

    } catch (const exception& error) {
        cerr << "Execution error: "
             << error.what() << "\n";

        return 1;
    }

    return 0;
}
