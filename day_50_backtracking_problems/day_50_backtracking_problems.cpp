#include <algorithm>
#include <array>
#include <cstddef>
#include <iostream>
#include <limits>
#include <optional>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <utility>
#include <vector>

using namespace std;

class BacktrackingEngine {
public:
    static vector<vector<int>> subsets(const vector<int>& values) {
        vector<vector<int>> result;
        vector<int> current;

        function<void(size_t)> search = [&](size_t index) {
            if (index == values.size()) {
                result.push_back(current);
                return;
            }

            // Exclude this element.
            search(index + 1);

            // Include this element.
            current.push_back(values[index]);
            search(index + 1);
            current.pop_back();
        };

        search(0);
        return result;
    }

    static vector<vector<int>> uniqueSubsets(vector<int> values) {
        sort(values.begin(), values.end());

        vector<vector<int>> result;
        vector<int> current;

        function<void(size_t)> search = [&](size_t start) {
            result.push_back(current);

            for (size_t i = start; i < values.size(); ++i) {
                if (i > start && values[i] == values[i - 1]) {
                    continue;
                }

                current.push_back(values[i]);
                search(i + 1);
                current.pop_back();
            }
        };

        search(0);
        return result;
    }

    static vector<vector<int>> combinations(const vector<int>& values, size_t k) {
        if (k > values.size()) {
            return {};
        }

        vector<vector<int>> result;
        vector<int> current;

        function<void(size_t)> search = [&](size_t start) {
            if (current.size() == k) {
                result.push_back(current);
                return;
            }

            const size_t needed = k - current.size();
            const size_t last = values.size() - needed;

            for (size_t i = start; i <= last; ++i) {
                current.push_back(values[i]);
                search(i + 1);
                current.pop_back();
            }
        };

        if (k == 0) {
            return {{}};
        }

        search(0);
        return result;
    }

    static vector<vector<int>> permutations(vector<int> values) {
        vector<vector<int>> result;
        vector<bool> used(values.size(), false);
        vector<int> current;

        // This version deliberately treats equal input values as distinct.
        function<void()> search = [&]() {
            if (current.size() == values.size()) {
                result.push_back(current);
                return;
            }

            for (size_t i = 0; i < values.size(); ++i) {
                if (used[i]) {
                    continue;
                }

                used[i] = true;
                current.push_back(values[i]);
                search();
                current.pop_back();
                used[i] = false;
            }
        };

        search();
        return result;
    }

    static vector<vector<int>> uniquePermutations(vector<int> values) {
        sort(values.begin(), values.end());

        vector<vector<int>> result;
        vector<bool> used(values.size(), false);
        vector<int> current;

        function<void()> search = [&]() {
            if (current.size() == values.size()) {
                result.push_back(current);
                return;
            }

            for (size_t i = 0; i < values.size(); ++i) {
                if (used[i]) {
                    continue;
                }

                if (i > 0 && values[i] == values[i - 1] && !used[i - 1]) {
                    continue;
                }

                used[i] = true;
                current.push_back(values[i]);
                search();
                current.pop_back();
                used[i] = false;
            }
        };

        search();
        return result;
    }

    static vector<vector<string>> solveNQueens(int n) {
        if (n <= 0) {
            throw invalid_argument("n must be positive");
        }

        vector<vector<string>> result;
        vector<string> board(n, string(n, '.'));
        unordered_set<int> columns;
        unordered_set<int> descending;
        unordered_set<int> ascending;

        function<void(int)> search = [&](int row) {
            if (row == n) {
                result.push_back(board);
                return;
            }

            for (int column = 0; column < n; ++column) {
                if (columns.contains(column)) continue;
                if (descending.contains(row - column)) continue;
                if (ascending.contains(row + column)) continue;

                board[row][column] = 'Q';
                columns.insert(column);
                descending.insert(row - column);
                ascending.insert(row + column);

                search(row + 1);

                ascending.erase(row + column);
                descending.erase(row - column);
                columns.erase(column);
                board[row][column] = '.';
            }
        };

        search(0);
        return result;
    }

    static bool solveSudoku(array<array<int, 9>, 9>& board) {
        array<int, 9> rowMask{};
        array<int, 9> columnMask{};
        array<int, 9> boxMask{};

        for (int row = 0; row < 9; ++row) {
            for (int column = 0; column < 9; ++column) {
                const int value = board[row][column];

                if (value < 0 || value > 9) {
                    throw invalid_argument("Sudoku values must be between 0 and 9");
                }

                if (value == 0) {
                    continue;
                }

                const int bit = 1 << value;
                const int box = (row / 3) * 3 + column / 3;

                if ((rowMask[row] & bit) ||
                    (columnMask[column] & bit) ||
                    (boxMask[box] & bit)) {
                    return false;
                }

                rowMask[row] |= bit;
                columnMask[column] |= bit;
                boxMask[box] |= bit;
            }
        }

        function<bool()> search = [&]() {
            int bestRow = -1;
            int bestColumn = -1;
            int bestMask = 0;
            int bestCount = numeric_limits<int>::max();

            for (int row = 0; row < 9; ++row) {
                for (int column = 0; column < 9; ++column) {
                    if (board[row][column] != 0) {
                        continue;
                    }

                    const int box = (row / 3) * 3 + column / 3;
                    const int available =
                        ((1 << 10) - 2) &
                        ~(rowMask[row] | columnMask[column] | boxMask[box]);

                    const int count = __builtin_popcount(static_cast<unsigned>(available));

                    if (count == 0) {
                        return false;
                    }

                    if (count < bestCount) {
                        bestCount = count;
                        bestRow = row;
                        bestColumn = column;
                        bestMask = available;
                    }
                }
            }

            if (bestRow == -1) {
                return true;
            }

            const int box = (bestRow / 3) * 3 + bestColumn / 3;

            while (bestMask != 0) {
                const int bit = bestMask & -bestMask;
                bestMask -= bit;

                int value = 1;
                int temporary = bit;
                while ((temporary >>= 1) != 0) {
                    ++value;
                }

                board[bestRow][bestColumn] = value;
                rowMask[bestRow] |= bit;
                columnMask[bestColumn] |= bit;
                boxMask[box] |= bit;

                if (search()) {
                    return true;
                }

                boxMask[box] ^= bit;
                columnMask[bestColumn] ^= bit;
                rowMask[bestRow] ^= bit;
                board[bestRow][bestColumn] = 0;
            }

            return false;
        };

        return search();
    }

    struct Position {
        int row;
        int column;

        bool operator==(const Position& other) const {
            return row == other.row && column == other.column;
        }
    };

    static vector<vector<Position>> findPaths(
        const vector<vector<int>>& grid,
        Position start,
        Position target,
        size_t maxPaths = 1000
    ) {
        if (grid.empty() || grid.front().empty()) {
            return {};
        }

        const int rows = static_cast<int>(grid.size());
        const int columns = static_cast<int>(grid.front().size());

        for (const auto& row : grid) {
            if (static_cast<int>(row.size()) != columns) {
                throw invalid_argument("Grid must be rectangular");
            }
        }

        auto valid = [&](Position position) {
            return position.row >= 0 &&
                   position.row < rows &&
                   position.column >= 0 &&
                   position.column < columns;
        };

        if (!valid(start) || !valid(target)) {
            throw out_of_range("Path position is outside the grid");
        }

        if (grid[start.row][start.column] != 0 ||
            grid[target.row][target.column] != 0) {
            return {};
        }

        vector<vector<Position>> result;
        vector<Position> path{start};
        vector<vector<bool>> visited(rows, vector<bool>(columns, false));
        visited[start.row][start.column] = true;

        constexpr array<pair<int, int>, 4> directions{{
            {1, 0}, {-1, 0}, {0, 1}, {0, -1}
        }};

        function<void(Position)> search = [&](Position position) {
            if (result.size() >= maxPaths) {
                return;
            }

            if (position == target) {
                result.push_back(path);
                return;
            }

            for (const auto& [dr, dc] : directions) {
                Position next{position.row + dr, position.column + dc};

                if (!valid(next)) continue;
                if (grid[next.row][next.column] != 0) continue;
                if (visited[next.row][next.column]) continue;

                visited[next.row][next.column] = true;
                path.push_back(next);

                search(next);

                path.pop_back();
                visited[next.row][next.column] = false;
            }
        };

        search(start);
        return result;
    }
};

template <typename T>
void printVectors(const vector<vector<T>>& values) {
    cout << "[";
    for (size_t i = 0; i < values.size(); ++i) {
        cout << "[";
        for (size_t j = 0; j < values[i].size(); ++j) {
            cout << values[i][j];
            if (j + 1 < values[i].size()) cout << ", ";
        }
        cout << "]";
        if (i + 1 < values.size()) cout << ", ";
    }
    cout << "]\n";
}

void printBoard(const vector<string>& board) {
    for (const auto& row : board) {
        cout << row << '\n';
    }
    cout << '\n';
}

int main() {
    try {
        const vector<int> values{1, 2, 3};

        cout << "Subsets: ";
        printVectors(BacktrackingEngine::subsets(values));

        cout << "Combinations: ";
        printVectors(BacktrackingEngine::combinations({1, 2, 3, 4}, 2));

        cout << "Unique permutations: ";
        printVectors(BacktrackingEngine::uniquePermutations({1, 1, 2}));

        const auto queens = BacktrackingEngine::solveNQueens(4);
        cout << "4-Queens solutions: " << queens.size() << '\n';
        for (const auto& board : queens) {
            printBoard(board);
        }

        array<array<int, 9>, 9> sudoku{{
            {{5, 3, 0, 0, 7, 0, 0, 0, 0}},
            {{6, 0, 0, 1, 9, 5, 0, 0, 0}},
            {{0, 9, 8, 0, 0, 0, 0, 6, 0}},
            {{8, 0, 0, 0, 6, 0, 0, 0, 3}},
            {{4, 0, 0, 8, 0, 3, 0, 0, 1}},
            {{7, 0, 0, 0, 2, 0, 0, 0, 6}},
            {{0, 6, 0, 0, 0, 0, 2, 8, 0}},
            {{0, 0, 0, 4, 1, 9, 0, 0, 5}},
            {{0, 0, 0, 0, 8, 0, 0, 7, 9}}
        }};

        cout << "Sudoku solved: "
             << boolalpha << BacktrackingEngine::solveSudoku(sudoku) << '\n';

        for (const auto& row : sudoku) {
            for (int value : row) {
                cout << value << ' ';
            }
            cout << '\n';
        }

        const vector<vector<int>> maze{
            {0, 0, 1, 0, 0},
            {1, 0, 1, 0, 1},
            {0, 0, 0, 0, 1},
            {0, 1, 1, 0, 0},
            {0, 0, 0, 1, 0}
        };

        const auto paths = BacktrackingEngine::findPaths(
            maze,
            {0, 0},
            {4, 4},
            10
        );

        cout << "Maze paths returned: " << paths.size() << '\n';

        for (const auto& path : paths) {
            for (const auto& position : path) {
                cout << '(' << position.row << ',' << position.column << ") ";
            }
            cout << '\n';
        }
    } catch (const exception& error) {
        cerr << "Backtracking execution failed: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
