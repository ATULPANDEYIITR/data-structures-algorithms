#include <algorithm>
#include <functional>
#include <iostream>
#include <optional>
#include <set>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

using namespace std;

/*
 * Case study: a warehouse robot must construct a safe route through a
 * constrained grid. A route is a state-space search. Each movement is a
 * choice, blocked cells are constraints, the current route is mutable state,
 * and removing the last movement restores the state for another branch.
 *
 * The same engine also exposes how pruning changes the practical search
 * space without changing the definition of a valid solution.
 */

struct Position {
    int row{};
    int column{};

    bool operator==(const Position& other) const {
        return row == other.row && column == other.column;
    }

    bool operator<(const Position& other) const {
        return tie(row, column) < tie(other.row, other.column);
    }
};

struct PositionHash {
    size_t operator()(const Position& position) const {
        return hash<int>{}(position.row) ^
               (hash<int>{}(position.column) << 1);
    }
};

struct SearchMetrics {
    size_t statesVisited = 0;
    size_t branchesPruned = 0;
    size_t solutions = 0;
};

class WarehouseRoutePlanner {
private:
    vector<vector<int>> grid;
    int rows;
    int columns;
    vector<string> route;
    vector<vector<bool>> visited;
    vector<vector<string>> solutions;
    SearchMetrics metrics;

    const vector<tuple<char, int, int>> moves{
        {'D', 1, 0},
        {'R', 0, 1},
        {'U', -1, 0},
        {'L', 0, -1}
    };

    bool inside(int row, int column) const {
        return row >= 0 &&
               row < rows &&
               column >= 0 &&
               column < columns;
    }

    bool reachableByManhattanBound(int row, int column) const {
        const int targetRow = rows - 1;
        const int targetColumn = columns - 1;

        // This lower bound is safe: no route can use fewer moves than its
        // Manhattan distance from the current state to the destination.
        const int distance =
            abs(targetRow - row) + abs(targetColumn - column);

        return distance <= rows * columns;
    }

    void search(int row, int column) {
        ++metrics.statesVisited;

        if (!reachableByManhattanBound(row, column)) {
            ++metrics.branchesPruned;
            return;
        }

        if (row == rows - 1 && column == columns - 1) {
            solutions.push_back(route);
            ++metrics.solutions;
            return;
        }

        visited[row][column] = true;

        for (const auto& [symbol, rowDelta, columnDelta] : moves) {
            const int nextRow = row + rowDelta;
            const int nextColumn = column + columnDelta;

            if (!inside(nextRow, nextColumn) ||
                grid[nextRow][nextColumn] == 1 ||
                visited[nextRow][nextColumn]) {
                ++metrics.branchesPruned;
                continue;
            }

            route.push_back(string(1, symbol));
            search(nextRow, nextColumn);

            // Undo only the state created by this branch. This invariant is
            // what allows the parent node to try the next movement safely.
            route.pop_back();
        }

        visited[row][column] = false;
    }

public:
    explicit WarehouseRoutePlanner(vector<vector<int>> warehouse)
        : grid(std::move(warehouse)),
          rows(static_cast<int>(grid.size())),
          columns(rows == 0 ? 0 : static_cast<int>(grid[0].size())) {

        if (rows == 0 || columns == 0) {
            throw invalid_argument("warehouse grid cannot be empty");
        }

        for (const auto& row : grid) {
            if (static_cast<int>(row.size()) != columns) {
                throw invalid_argument("warehouse grid must be rectangular");
            }
        }

        if (grid.front().front() == 1 ||
            grid.back().back() == 1) {
            throw invalid_argument("start and destination must be open");
        }

        visited.assign(rows, vector<bool>(columns, false));
    }

    vector<vector<string>> findAllRoutes() {
        solutions.clear();
        route.clear();
        metrics = {};
        search(0, 0);
        return solutions;
    }

    const SearchMetrics& getMetrics() const {
        return metrics;
    }
};

struct Assignment {
    string worker;
    string station;
};

class StationScheduler {
private:
    vector<string> workers;
    vector<string> stations;
    unordered_map<string, unordered_set<string>> unavailable;
    set<pair<string, string>> conflicts;

    vector<Assignment> current;
    unordered_set<string> assignedStations;
    vector<vector<Assignment>> solutions;

    bool conflictsWithCurrent(const string& worker) const {
        for (const auto& assignment : current) {
            auto pair1 = make_pair(worker, assignment.worker);
            auto pair2 = make_pair(assignment.worker, worker);

            if (conflicts.contains(pair1) || conflicts.contains(pair2)) {
                return true;
            }
        }

        return false;
    }

    void search(size_t workerIndex) {
        if (workerIndex == workers.size()) {
            solutions.push_back(current);
            return;
        }

        const string& worker = workers[workerIndex];

        for (const string& station : stations) {
            if (assignedStations.contains(station)) {
                continue;
            }

            if (unavailable[worker].contains(station)) {
                continue;
            }

            if (conflictsWithCurrent(worker)) {
                continue;
            }

            current.push_back({worker, station});
            assignedStations.insert(station);

            search(workerIndex + 1);

            assignedStations.erase(station);
            current.pop_back();
        }
    }

public:
    StationScheduler(
        vector<string> workers,
        vector<string> stations,
        unordered_map<string, unordered_set<string>> unavailable,
        set<pair<string, string>> conflicts
    )
        : workers(std::move(workers)),
          stations(std::move(stations)),
          unavailable(std::move(unavailable)),
          conflicts(std::move(conflicts)) {}

    vector<vector<Assignment>> solve() {
        current.clear();
        assignedStations.clear();
        solutions.clear();
        search(0);
        return solutions;
    }
};

void printRoutes(const vector<vector<string>>& routes) {
    for (const auto& route : routes) {
        for (const auto& movement : route) {
            cout << movement;
        }
        cout << '\n';
    }
}

int main() {
    cout << "Backtracking repository: warehouse route case study\n\n";

    vector<vector<int>> warehouse{
        {0, 0, 1, 0, 0},
        {1, 0, 1, 0, 1},
        {0, 0, 0, 0, 0},
        {0, 1, 1, 1, 0},
        {0, 0, 0, 0, 0}
    };

    WarehouseRoutePlanner planner(warehouse);
    const auto routes = planner.findAllRoutes();

    cout << "Valid warehouse routes:\n";
    printRoutes(routes);

    const auto& metrics = planner.getMetrics();
    cout << "\nSearch states: " << metrics.statesVisited << '\n';
    cout << "Pruned branches: " << metrics.branchesPruned << '\n';
    cout << "Solutions: " << metrics.solutions << "\n\n";

    /*
     * A second domain shows that backtracking is not limited to grids.
     * Workers must be assigned unique stations while respecting individual
     * availability and pairwise incompatibilities.
     */
    vector<string> workers{"Asha", "Bharat", "Chen", "Divya"};
    vector<string> stations{"Inspection", "Packaging", "Loading", "Dispatch"};

    unordered_map<string, unordered_set<string>> unavailable{
        {"Asha", {"Dispatch"}},
        {"Bharat", {"Inspection"}},
        {"Chen", {"Loading"}},
        {"Divya", {}}
    };

    set<pair<string, string>> conflicts{
        {"Asha", "Chen"}
    };

    StationScheduler scheduler(
        workers,
        stations,
        unavailable,
        conflicts
    );

    const auto schedules = scheduler.solve();

    cout << "Valid station schedules:\n";
    for (const auto& schedule : schedules) {
        cout << "{ ";
        for (const auto& assignment : schedule) {
            cout << assignment.worker << "->"
                 << assignment.station << " ";
        }
        cout << "}\n";
    }

    /*
     * Complexity:
     *
     * Route search can be exponential in the number of reachable cells.
     * The visited matrix prevents cyclic paths from creating infinite
     * recursion. Constraint checks prune branches before deeper recursion.
     *
     * Assignment search has O(S^W) worst-case branching when W workers
     * choose among S stations, with uniqueness reducing later branching.
     * Backtracking is valuable because invalid partial assignments can be
     * rejected before a complete assignment is constructed.
     */
    return 0;
}
