#include <algorithm>
#include <cassert>
#include <iostream>
#include <map>
#include <queue>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

class Graph {
private:
    map<string, set<string>> adjacency;

    void validateVertex(const string& vertex) const {
        if (adjacency.find(vertex) == adjacency.end()) {
            throw invalid_argument("Unknown vertex: " + vertex);
        }
    }

public:
    void addVertex(const string& vertex) {
        if (vertex.empty()) {
            throw invalid_argument("Vertex cannot be empty.");
        }

        adjacency[vertex];
    }

    void addEdge(const string& source, const string& destination) {
        addVertex(source);
        addVertex(destination);

        adjacency[source].insert(destination);
        adjacency[destination].insert(source);
    }

    void removeEdge(
        const string& source,
        const string& destination
    ) {
        validateVertex(source);
        validateVertex(destination);

        adjacency[source].erase(destination);
        adjacency[destination].erase(source);
    }

    void removeVertex(const string& vertex) {
        validateVertex(vertex);

        for (const string& neighbor : adjacency[vertex]) {
            adjacency[neighbor].erase(vertex);
        }

        adjacency.erase(vertex);
    }

    vector<string> bfs(const string& start) const {
        validateVertex(start);

        set<string> visited;
        queue<string> frontier;
        vector<string> traversal;

        visited.insert(start);
        frontier.push(start);

        while (!frontier.empty()) {
            string current = frontier.front();
            frontier.pop();

            traversal.push_back(current);

            for (const string& neighbor : adjacency.at(current)) {
                if (visited.insert(neighbor).second) {
                    frontier.push(neighbor);
                }
            }
        }

        return traversal;
    }

    map<string, int> bfsDistances(const string& start) const {
        validateVertex(start);

        map<string, int> distances;
        queue<string> frontier;

        distances[start] = 0;
        frontier.push(start);

        while (!frontier.empty()) {
            string current = frontier.front();
            frontier.pop();

            for (const string& neighbor : adjacency.at(current)) {
                if (distances.find(neighbor) == distances.end()) {
                    distances[neighbor] = distances[current] + 1;
                    frontier.push(neighbor);
                }
            }
        }

        return distances;
    }

    vector<string> shortestPath(
        const string& start,
        const string& target
    ) const {
        validateVertex(start);
        validateVertex(target);

        if (start == target) {
            return {start};
        }

        queue<string> frontier;
        map<string, string> parent;
        set<string> visited;

        visited.insert(start);
        frontier.push(start);

        bool found = false;

        while (!frontier.empty() && !found) {
            string current = frontier.front();
            frontier.pop();

            for (const string& neighbor : adjacency.at(current)) {
                if (visited.insert(neighbor).second) {
                    parent[neighbor] = current;

                    if (neighbor == target) {
                        found = true;
                        break;
                    }

                    frontier.push(neighbor);
                }
            }
        }

        if (!found) {
            return {};
        }

        vector<string> path;
        string current = target;

        while (current != start) {
            path.push_back(current);
            current = parent.at(current);
        }

        path.push_back(start);
        reverse(path.begin(), path.end());

        return path;
    }

    vector<vector<string>> connectedComponents() const {
        set<string> visited;
        vector<vector<string>> components;

        for (const auto& [vertex, neighbors] : adjacency) {
            if (visited.count(vertex)) {
                continue;
            }

            queue<string> frontier;
            vector<string> component;

            frontier.push(vertex);
            visited.insert(vertex);

            while (!frontier.empty()) {
                string current = frontier.front();
                frontier.pop();

                component.push_back(current);

                for (const string& neighbor : adjacency.at(current)) {
                    if (visited.insert(neighbor).second) {
                        frontier.push(neighbor);
                    }
                }
            }

            components.push_back(component);
        }

        return components;
    }

    bool isConnected() const {
        return adjacency.empty() || connectedComponents().size() == 1;
    }

    void display() const {
        for (const auto& [vertex, neighbors] : adjacency) {
            cout << vertex << ": ";

            for (const auto& neighbor : neighbors) {
                cout << neighbor << " ";
            }

            cout << '\n';
        }
    }

    size_t vertexCount() const {
        return adjacency.size();
    }

    size_t edgeCount() const {
        size_t total = 0;

        for (const auto& [vertex, neighbors] : adjacency) {
            total += neighbors.size();
        }

        // Each undirected edge is stored twice.
        return total / 2;
    }
};

void printVector(const vector<string>& values) {
    if (values.empty()) {
        cout << "No path found";
    } else {
        for (size_t i = 0; i < values.size(); ++i) {
            if (i > 0) cout << " -> ";
            cout << values[i];
        }
    }

    cout << '\n';
}

Graph createSampleGraph() {
    Graph graph;

    graph.addEdge("A", "B");
    graph.addEdge("A", "C");
    graph.addEdge("B", "D");
    graph.addEdge("B", "E");
    graph.addEdge("C", "F");
    graph.addEdge("E", "F");
    graph.addEdge("G", "H");
    graph.addVertex("I");

    return graph;
}

int main() {
    try {
        Graph graph = createSampleGraph();

        cout << "BREADTH-FIRST SEARCH\n";
        cout << "====================\n";

        cout << "\n1. Graph representation\n";
        graph.display();

        cout << "\n2. Graph statistics\n";
        cout << "Vertices: " << graph.vertexCount() << '\n';
        cout << "Edges: " << graph.edgeCount() << '\n';

        cout << "\n3. BFS traversal from A\n";
        printVector(graph.bfs("A"));

        cout << "\n4. Shortest distances from A\n";

        const auto distances = graph.bfsDistances("A");

        for (const auto& [vertex, distance] : distances) {
            cout << vertex << ": " << distance << '\n';
        }

        cout << "\n5. Shortest path from A to F\n";

        vector<string> path = graph.shortestPath("A", "F");
        printVector(path);

        if (!path.empty()) {
            cout << "Minimum edge count: " << path.size() - 1 << '\n';
        }

        cout << "\n6. Unreachable destination A to H\n";
        printVector(graph.shortestPath("A", "H"));

        cout << "\n7. Connected components\n";

        auto components = graph.connectedComponents();

        for (size_t i = 0; i < components.size(); ++i) {
            cout << "Component " << i + 1 << ": ";
            printVector(components[i]);
        }

        cout << "\n8. Connectivity\n";
        cout << boolalpha << graph.isConnected() << '\n';

        cout << "\n9. Edge removal\n";
        graph.removeEdge("A", "B");
        printVector(graph.bfs("A"));

        cout << "\n10. Vertex removal\n";
        graph.removeVertex("I");
        cout << "Remaining vertices: " << graph.vertexCount() << '\n';

        cout << "\n11. Single-vertex graph\n";
        Graph single;
        single.addVertex("X");
        printVector(single.bfs("X"));

        cout << "\n12. Correctness tests\n";

        Graph test = createSampleGraph();

        assert(test.bfs("A") ==
               vector<string>({"A", "B", "C", "D", "E", "F"}));

        assert(test.bfsDistances("A").at("F") == 2);

        assert(test.shortestPath("A", "F") ==
               vector<string>({"A", "C", "F"}));

        assert(test.shortestPath("A", "H").empty());
        assert(test.shortestPath("A", "A") ==
               vector<string>({"A"}));

        assert(test.connectedComponents().size() == 3);

        cout << "All tests passed successfully.\n";

        cout << "\n13. Invalid vertex handling\n";

        try {
            test.bfs("UNKNOWN");
        } catch (const invalid_argument& error) {
            cout << "Expected error: " << error.what() << '\n';
        }

    } catch (const exception& error) {
        cerr << "Application error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
