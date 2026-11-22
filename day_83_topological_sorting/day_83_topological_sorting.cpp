#include <algorithm>
#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

using namespace std;

/*
 * Topological Sorting and Dependency Resolution
 *
 * C++17 implementation of a software build dependency engine.
 *
 * Features:
 * - Directed graph representation
 * - DFS topological sorting
 * - Kahn's algorithm
 * - Cycle path detection
 * - Dependency validation
 * - Deterministic scheduling
 * - Parallel execution level calculation
 * - Merge of dependency information into a build plan
 */

class GraphException : public runtime_error {
public:
    explicit GraphException(const string& message)
        : runtime_error(message) {}
};

enum class NodeState {
    UNVISITED,
    VISITING,
    VISITED
};

enum class BuildStatus {
    PENDING,
    READY,
    COMPLETED,
    FAILED,
    BLOCKED
};

string statusName(BuildStatus status) {
    switch (status) {
        case BuildStatus::PENDING:
            return "PENDING";
        case BuildStatus::READY:
            return "READY";
        case BuildStatus::COMPLETED:
            return "COMPLETED";
        case BuildStatus::FAILED:
            return "FAILED";
        case BuildStatus::BLOCKED:
            return "BLOCKED";
    }

    return "UNKNOWN";
}

struct BuildTask {
    string id;
    string description;
    BuildStatus status = BuildStatus::PENDING;
};

class DirectedGraph {
private:
    map<string, set<string>> adjacency;

    void dfs(
        const string& vertex,
        map<string, NodeState>& state,
        vector<string>& path,
        vector<string>& result
    ) const {
        state[vertex] = NodeState::VISITING;
        path.push_back(vertex);

        for (const string& neighbor : adjacency.at(vertex)) {
            if (state[neighbor] == NodeState::VISITING) {
                auto start = find(
                    path.begin(),
                    path.end(),
                    neighbor
                );

                vector<string> cycle(
                    start,
                    path.end()
                );

                cycle.push_back(neighbor);

                string message = "Cycle detected: ";

                for (size_t i = 0; i < cycle.size(); ++i) {
                    if (i > 0) {
                        message += " -> ";
                    }

                    message += cycle[i];
                }

                throw GraphException(message);
            }

            if (state[neighbor] == NodeState::UNVISITED) {
                dfs(neighbor, state, path, result);
            }
        }

        path.pop_back();
        state[vertex] = NodeState::VISITED;
        result.push_back(vertex);
    }

public:
    void addVertex(const string& id) {
        if (id.empty()) {
            throw invalid_argument("Vertex ID cannot be empty.");
        }

        adjacency.try_emplace(id);
    }

    void addEdge(
        const string& prerequisite,
        const string& dependent
    ) {
        if (!adjacency.count(prerequisite)) {
            throw GraphException(
                "Unknown prerequisite: " + prerequisite
            );
        }

        if (!adjacency.count(dependent)) {
            throw GraphException(
                "Unknown dependent: " + dependent
            );
        }

        if (prerequisite == dependent) {
            throw GraphException(
                "Self-dependency detected: " + prerequisite
            );
        }

        adjacency[prerequisite].insert(dependent);
    }

    size_t vertexCount() const {
        return adjacency.size();
    }

    size_t edgeCount() const {
        size_t count = 0;

        for (const auto& entry : adjacency) {
            count += entry.second.size();
        }

        return count;
    }

    vector<string> dfsTopologicalSort() const {
        map<string, NodeState> state;

        for (const auto& entry : adjacency) {
            state[entry.first] = NodeState::UNVISITED;
        }

        vector<string> result;
        vector<string> path;

        for (const auto& entry : adjacency) {
            if (state[entry.first] == NodeState::UNVISITED) {
                dfs(
                    entry.first,
                    state,
                    path,
                    result
                );
            }
        }

        reverse(result.begin(), result.end());

        return result;
    }

    vector<string> kahnTopologicalSort() const {
        map<string, int> indegree;

        for (const auto& entry : adjacency) {
            indegree[entry.first] = 0;
        }

        for (const auto& entry : adjacency) {
            for (const string& neighbor : entry.second) {
                ++indegree[neighbor];
            }
        }

        // A min-priority queue provides deterministic ordering.
        priority_queue<
            string,
            vector<string>,
            greater<string>
        > ready;

        for (const auto& entry : indegree) {
            if (entry.second == 0) {
                ready.push(entry.first);
            }
        }

        vector<string> result;

        while (!ready.empty()) {
            string current = ready.top();
            ready.pop();

            result.push_back(current);

            for (const string& neighbor : adjacency.at(current)) {
                --indegree[neighbor];

                if (indegree[neighbor] == 0) {
                    ready.push(neighbor);
                }
            }
        }

        if (result.size() != adjacency.size()) {
            string unresolved;

            for (const auto& entry : indegree) {
                if (entry.second > 0) {
                    if (!unresolved.empty()) {
                        unresolved += ", ";
                    }

                    unresolved += entry.first;
                }
            }

            throw GraphException(
                "Graph contains a cycle. Unresolved: " + unresolved
            );
        }

        return result;
    }

    map<string, int> calculateLevels() const {
        vector<string> order = kahnTopologicalSort();

        map<string, int> levels;

        for (const auto& entry : adjacency) {
            levels[entry.first] = 0;
        }

        for (const string& vertex : order) {
            for (const string& neighbor : adjacency.at(vertex)) {
                levels[neighbor] = max(
                    levels[neighbor],
                    levels[vertex] + 1
                );
            }
        }

        return levels;
    }

    bool validateOrdering(
        const vector<string>& order
    ) const {
        if (order.size() != adjacency.size()) {
            return false;
        }

        unordered_map<string, size_t> position;

        for (size_t i = 0; i < order.size(); ++i) {
            if (!adjacency.count(order[i])) {
                return false;
            }

            if (!position.emplace(order[i], i).second) {
                return false;
            }
        }

        for (const auto& entry : adjacency) {
            for (const string& neighbor : entry.second) {
                if (
                    position.at(entry.first) >=
                    position.at(neighbor)
                ) {
                    return false;
                }
            }
        }

        return true;
    }

    vector<string> prerequisitesOf(
        const string& vertex
    ) const {
        if (!adjacency.count(vertex)) {
            throw GraphException("Unknown vertex: " + vertex);
        }

        vector<string> result;

        for (const auto& entry : adjacency) {
            if (entry.second.count(vertex)) {
                result.push_back(entry.first);
            }
        }

        return result;
    }

    const map<string, set<string>>& getAdjacency() const {
        return adjacency;
    }
};

class BuildEngine {
private:
    DirectedGraph graph;
    map<string, BuildTask> tasks;

public:
    void registerTask(
        const string& id,
        const string& description
    ) {
        if (tasks.count(id)) {
            throw GraphException("Duplicate task: " + id);
        }

        graph.addVertex(id);

        tasks.emplace(
            id,
            BuildTask{id, description}
        );
    }

    void addDependency(
        const string& prerequisite,
        const string& dependent
    ) {
        graph.addEdge(prerequisite, dependent);
    }

    vector<string> createBuildPlan() const {
        return graph.kahnTopologicalSort();
    }

    void execute() {
        vector<string> order = createBuildPlan();

        unordered_set<string> completed;
        unordered_set<string> failed;

        for (const string& id : order) {
            BuildTask& task = tasks.at(id);

            vector<string> prerequisites =
                graph.prerequisitesOf(id);

            bool blocked = any_of(
                prerequisites.begin(),
                prerequisites.end(),
                [&](const string& prerequisite) {
                    return failed.count(prerequisite) > 0;
                }
            );

            if (blocked) {
                task.status = BuildStatus::BLOCKED;
                failed.insert(id);
                continue;
            }

            bool ready = all_of(
                prerequisites.begin(),
                prerequisites.end(),
                [&](const string& prerequisite) {
                    return completed.count(prerequisite) > 0;
                }
            );

            if (!ready) {
                throw GraphException(
                    "Execution dependency invariant violated: " + id
                );
            }

            task.status = BuildStatus::READY;

            cout << "[EXECUTING] "
                 << task.id << " - "
                 << task.description << '\n';

            // Represents a successful build operation.
            task.status = BuildStatus::COMPLETED;
            completed.insert(id);
        }

        cout << "\nBuild task states:\n";

        for (const auto& entry : tasks) {
            cout << entry.first << ": "
                 << statusName(entry.second.status) << '\n';
        }
    }

    const DirectedGraph& getGraph() const {
        return graph;
    }
};

BuildEngine createSampleBuild() {
    BuildEngine engine;

    vector<pair<string, string>> tasks = {
        {"source", "Retrieve source code"},
        {"validate", "Validate source files"},
        {"compile", "Compile application"},
        {"unit", "Execute unit tests"},
        {"security", "Run security analysis"},
        {"package", "Generate release package"},
        {"integration", "Run integration tests"},
        {"deploy", "Deploy application"}
    };

    for (const auto& task : tasks) {
        engine.registerTask(task.first, task.second);
    }

    vector<pair<string, string>> edges = {
        {"source", "validate"},
        {"validate", "compile"},
        {"compile", "unit"},
        {"compile", "security"},
        {"unit", "package"},
        {"security", "package"},
        {"package", "integration"},
        {"integration", "deploy"}
    };

    for (const auto& edge : edges) {
        engine.addDependency(edge.first, edge.second);
    }

    return engine;
}

void demonstrateCycleDetection() {
    DirectedGraph graph;

    graph.addVertex("A");
    graph.addVertex("B");
    graph.addVertex("C");

    graph.addEdge("A", "B");
    graph.addEdge("B", "C");
    graph.addEdge("C", "A");

    cout << "\nCycle detection:\n";

    try {
        graph.dfsTopologicalSort();
    } catch (const GraphException& error) {
        cout << "DFS: " << error.what() << '\n';
    }

    try {
        graph.kahnTopologicalSort();
    } catch (const GraphException& error) {
        cout << "Kahn: " << error.what() << '\n';
    }
}

void demonstrateEdgeCases() {
    DirectedGraph graph;

    graph.addVertex("isolated");

    vector<string> order = graph.kahnTopologicalSort();

    if (
        order.size() != 1 ||
        order.front() != "isolated"
    ) {
        throw GraphException("Isolated vertex test failed.");
    }

    DirectedGraph empty;

    if (!empty.kahnTopologicalSort().empty()) {
        throw GraphException("Empty graph test failed.");
    }

    try {
        graph.addEdge("isolated", "isolated");
        throw GraphException("Self-loop was not rejected.");
    } catch (const GraphException&) {
        cout << "\nSelf-loop validation passed.\n";
    }
}

int main() {
    try {
        cout << "TOPOLOGICAL SORTING AND BUILD DEPENDENCY ENGINE\n";
        cout << string(55, '=') << '\n';

        BuildEngine engine = createSampleBuild();

        const DirectedGraph& graph = engine.getGraph();

        cout << "\nVertices: " << graph.vertexCount() << '\n';
        cout << "Edges: " << graph.edgeCount() << '\n';

        vector<string> dfs = graph.dfsTopologicalSort();
        vector<string> kahn = graph.kahnTopologicalSort();

        cout << "\nDFS ordering:\n";

        for (const string& node : dfs) {
            cout << node << " ";
        }

        cout << "\n\nKahn ordering:\n";

        for (const string& node : kahn) {
            cout << node << " ";
        }

        cout << '\n';

        if (
            !graph.validateOrdering(dfs) ||
            !graph.validateOrdering(kahn)
        ) {
            throw GraphException(
                "Invalid topological ordering generated."
            );
        }

        cout << "\nBoth orderings are valid.\n";

        cout << "\nDependency execution levels:\n";

        for (const auto& entry : graph.calculateLevels()) {
            cout << entry.first
                 << ": Level "
                 << entry.second << '\n';
        }

        cout << "\nBuild execution:\n";

        engine.execute();

        demonstrateCycleDetection();
        demonstrateEdgeCases();

        cout << "\nAll validations passed.\n";

    } catch (const exception& error) {
        cerr << "Execution failed: "
             << error.what() << '\n';

        return 1;
    }

    return 0;
}
