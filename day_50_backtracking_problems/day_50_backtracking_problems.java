import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import java.util.Set;
import java.util.function.Consumer;
import java.util.stream.Collectors;

public class BacktrackingProblems {

    public static List<List<Integer>> subsets(List<Integer> values) {
        Objects.requireNonNull(values, "values");
        List<List<Integer>> result = new ArrayList<>();
        backtrackSubsets(values, 0, new ArrayList<>(), result);
        return result;
    }

    private static void backtrackSubsets(
            List<Integer> values,
            int index,
            List<Integer> current,
            List<List<Integer>> result) {

        if (index == values.size()) {
            result.add(List.copyOf(current));
            return;
        }

        backtrackSubsets(values, index + 1, current, result);

        current.add(values.get(index));
        backtrackSubsets(values, index + 1, current, result);
        current.remove(current.size() - 1);
    }

    public static List<List<Integer>> combinations(List<Integer> values, int k) {
        Objects.requireNonNull(values, "values");

        if (k < 0 || k > values.size()) {
            return List.of();
        }

        List<List<Integer>> result = new ArrayList<>();
        backtrackCombinations(values, k, 0, new ArrayList<>(), result);
        return result;
    }

    private static void backtrackCombinations(
            List<Integer> values,
            int k,
            int start,
            List<Integer> current,
            List<List<Integer>> result) {

        if (current.size() == k) {
            result.add(List.copyOf(current));
            return;
        }

        int needed = k - current.size();
        int last = values.size() - needed;

        for (int index = start; index <= last; index++) {
            current.add(values.get(index));
            backtrackCombinations(values, k, index + 1, current, result);
            current.remove(current.size() - 1);
        }
    }

    public static List<List<Integer>> uniquePermutations(List<Integer> values) {
        Objects.requireNonNull(values, "values");

        List<Integer> sorted = new ArrayList<>(values);
        Collections.sort(sorted);

        List<List<Integer>> result = new ArrayList<>();
        boolean[] used = new boolean[sorted.size()];

        backtrackUniquePermutations(sorted, used, new ArrayList<>(), result);
        return result;
    }

    private static void backtrackUniquePermutations(
            List<Integer> values,
            boolean[] used,
            List<Integer> current,
            List<List<Integer>> result) {

        if (current.size() == values.size()) {
            result.add(List.copyOf(current));
            return;
        }

        for (int index = 0; index < values.size(); index++) {
            if (used[index]) {
                continue;
            }

            if (index > 0
                    && values.get(index).equals(values.get(index - 1))
                    && !used[index - 1]) {
                continue;
            }

            used[index] = true;
            current.add(values.get(index));

            backtrackUniquePermutations(values, used, current, result);

            current.remove(current.size() - 1);
            used[index] = false;
        }
    }

    public static List<List<String>> solveNQueens(int n) {
        if (n < 1) {
            throw new IllegalArgumentException("n must be positive");
        }

        char[][] board = new char[n][n];
        for (char[] row : board) {
            Arrays.fill(row, '.');
        }

        Set<Integer> columns = new HashSet<>();
        Set<Integer> descending = new HashSet<>();
        Set<Integer> ascending = new HashSet<>();
        List<List<String>> result = new ArrayList<>();

        backtrackQueens(
                0,
                n,
                board,
                columns,
                descending,
                ascending,
                result
        );

        return result;
    }

    private static void backtrackQueens(
            int row,
            int n,
            char[][] board,
            Set<Integer> columns,
            Set<Integer> descending,
            Set<Integer> ascending,
            List<List<String>> result) {

        if (row == n) {
            List<String> solution = new ArrayList<>();
            for (char[] boardRow : board) {
                solution.add(new String(boardRow));
            }
            result.add(List.copyOf(solution));
            return;
        }

        for (int column = 0; column < n; column++) {
            if (columns.contains(column)
                    || descending.contains(row - column)
                    || ascending.contains(row + column)) {
                continue;
            }

            board[row][column] = 'Q';
            columns.add(column);
            descending.add(row - column);
            ascending.add(row + column);

            backtrackQueens(
                    row + 1,
                    n,
                    board,
                    columns,
                    descending,
                    ascending,
                    result
            );

            ascending.remove(row + column);
            descending.remove(row - column);
            columns.remove(column);
            board[row][column] = '.';
        }
    }

    public static boolean solveSudoku(int[][] board) {
        validateSudoku(board);

        Set<Integer>[] rows = createSets();
        Set<Integer>[] columns = createSets();
        Set<Integer>[] boxes = createSets();

        for (int row = 0; row < 9; row++) {
            for (int column = 0; column < 9; column++) {
                int value = board[row][column];

                if (value == 0) {
                    continue;
                }

                int box = (row / 3) * 3 + column / 3;

                if (!rows[row].add(value)
                        || !columns[column].add(value)
                        || !boxes[box].add(value)) {
                    return false;
                }
            }
        }

        return backtrackSudoku(board, rows, columns, boxes);
    }

    @SuppressWarnings("unchecked")
    private static Set<Integer>[] createSets() {
        Set<Integer>[] sets = new Set[9];
        for (int index = 0; index < 9; index++) {
            sets[index] = new HashSet<>();
        }
        return sets;
    }

    private static void validateSudoku(int[][] board) {
        if (board == null || board.length != 9) {
            throw new IllegalArgumentException("Sudoku board must be 9x9");
        }

        for (int[] row : board) {
            if (row == null || row.length != 9) {
                throw new IllegalArgumentException("Sudoku board must be 9x9");
            }

            for (int value : row) {
                if (value < 0 || value > 9) {
                    throw new IllegalArgumentException("Sudoku values must be 0 through 9");
                }
            }
        }
    }

    private static boolean backtrackSudoku(
            int[][] board,
            Set<Integer>[] rows,
            Set<Integer>[] columns,
            Set<Integer>[] boxes) {

        int bestRow = -1;
        int bestColumn = -1;
        List<Integer> bestCandidates = null;

        for (int row = 0; row < 9; row++) {
            for (int column = 0; column < 9; column++) {
                if (board[row][column] != 0) {
                    continue;
                }

                int box = (row / 3) * 3 + column / 3;
                List<Integer> candidates = new ArrayList<>();

                for (int value = 1; value <= 9; value++) {
                    if (!rows[row].contains(value)
                            && !columns[column].contains(value)
                            && !boxes[box].contains(value)) {
                        candidates.add(value);
                    }
                }

                if (candidates.isEmpty()) {
                    return false;
                }

                if (bestCandidates == null
                        || candidates.size() < bestCandidates.size()) {
                    bestCandidates = candidates;
                    bestRow = row;
                    bestColumn = column;
                }
            }
        }

        if (bestRow == -1) {
            return true;
        }

        int box = (bestRow / 3) * 3 + bestColumn / 3;

        for (int value : bestCandidates) {
            board[bestRow][bestColumn] = value;
            rows[bestRow].add(value);
            columns[bestColumn].add(value);
            boxes[box].add(value);

            if (backtrackSudoku(board, rows, columns, boxes)) {
                return true;
            }

            boxes[box].remove(value);
            columns[bestColumn].remove(value);
            rows[bestRow].remove(value);
            board[bestRow][bestColumn] = 0;
        }

        return false;
    }

    public record Position(int row, int column) {
        public Position {
            if (row < 0 || column < 0) {
                throw new IllegalArgumentException("Coordinates cannot be negative");
            }
        }
    }

    public record RepositoryPath(List<Position> positions) {
        public RepositoryPath {
            positions = List.copyOf(positions);
        }
    }

    public static List<RepositoryPath> findPaths(
            int[][] grid,
            Position start,
            Position target,
            int maxPaths) {

        validateGrid(grid);

        if (maxPaths <= 0) {
            return List.of();
        }

        ensureInside(grid, start);
        ensureInside(grid, target);

        if (grid[start.row()][start.column()] != 0
                || grid[target.row()][target.column()] != 0) {
            return List.of();
        }

        List<RepositoryPath> result = new ArrayList<>();
        boolean[][] visited = new boolean[grid.length][grid[0].length];
        List<Position> current = new ArrayList<>();
        current.add(start);
        visited[start.row()][start.column()] = true;

        backtrackPaths(grid, target, maxPaths, visited, current, result);
        return List.copyOf(result);
    }

    private static void backtrackPaths(
            int[][] grid,
            Position target,
            int maxPaths,
            boolean[][] visited,
            List<Position> current,
            List<RepositoryPath> result) {

        if (result.size() >= maxPaths) {
            return;
        }

        Position currentPosition = current.get(current.size() - 1);

        if (currentPosition.equals(target)) {
            result.add(new RepositoryPath(current));
            return;
        }

        int[][] directions = {
                {1, 0},
                {-1, 0},
                {0, 1},
                {0, -1}
        };

        for (int[] direction : directions) {
            Position next = new Position(
                    currentPosition.row() + direction[0],
                    currentPosition.column() + direction[1]
            );

            if (next.row() < 0
                    || next.row() >= grid.length
                    || next.column() < 0
                    || next.column() >= grid[0].length) {
                continue;
            }

            if (grid[next.row()][next.column()] != 0
                    || visited[next.row()][next.column()]) {
                continue;
            }

            visited[next.row()][next.column()] = true;
            current.add(next);

            backtrackPaths(
                    grid,
                    target,
                    maxPaths,
                    visited,
                    current,
                    result
            );

            current.remove(current.size() - 1);
            visited[next.row()][next.column()] = false;
        }
    }

    private static void validateGrid(int[][] grid) {
        if (grid == null || grid.length == 0 || grid[0] == null || grid[0].length == 0) {
            throw new IllegalArgumentException("Grid must be non-empty");
        }

        int columns = grid[0].length;

        for (int[] row : grid) {
            if (row == null || row.length != columns) {
                throw new IllegalArgumentException("Grid must be rectangular");
            }
        }
    }

    private static void ensureInside(int[][] grid, Position position) {
        if (position == null
                || position.row() >= grid.length
                || position.column() >= grid[0].length) {
            throw new IllegalArgumentException("Position is outside the grid");
        }
    }

    private record RepositoryReviewScenario(
            String repository,
            List<Integer> changedFiles,
            boolean testsPassing,
            boolean hasConflicts,
            List<String> reviewers
    ) {
        boolean mergeEligible() {
            return !changedFiles.isEmpty()
                    && testsPassing
                    && !hasConflicts
                    && reviewers.stream().anyMatch(name -> !name.isBlank());
        }
    }

    public static void main(String[] args) {
        System.out.println("Subsets: " + subsets(List.of(1, 2, 3)));
        System.out.println("Combinations: " + combinations(List.of(1, 2, 3, 4), 2));
        System.out.println(
                "Unique permutations: "
                        + uniquePermutations(List.of(1, 1, 2))
        );

        List<List<String>> queens = solveNQueens(4);
        System.out.println("4-Queens solutions: " + queens.size());
        queens.forEach(solution -> {
            solution.forEach(System.out::println);
            System.out.println();
        });

        int[][] sudoku = {
                {5, 3, 0, 0, 7, 0, 0, 0, 0},
                {6, 0, 0, 1, 9, 5, 0, 0, 0},
                {0, 9, 8, 0, 0, 0, 0, 6, 0},
                {8, 0, 0, 0, 6, 0, 0, 0, 3},
                {4, 0, 0, 8, 0, 3, 0, 0, 1},
                {7, 0, 0, 0, 2, 0, 0, 0, 6},
                {0, 6, 0, 0, 0, 0, 2, 8, 0},
                {0, 0, 0, 4, 1, 9, 0, 0, 5},
                {0, 0, 0, 0, 8, 0, 0, 7, 9}
        };

        System.out.println("Sudoku solved: " + solveSudoku(sudoku));

        for (int[] row : sudoku) {
            System.out.println(
                    Arrays.stream(row)
                            .mapToObj(Integer::toString)
                            .collect(Collectors.joining(" "))
            );
        }

        int[][] maze = {
                {0, 0, 1, 0, 0},
                {1, 0, 1, 0, 1},
                {0, 0, 0, 0, 1},
                {0, 1, 1, 0, 0},
                {0, 0, 0, 1, 0}
        };

        Position start = new Position(0, 0);
        Position target = new Position(4, 4);

        List<RepositoryPath> paths = findPaths(maze, start, target, 10);
        System.out.println("Paths returned: " + paths.size());

        RepositoryReviewScenario scenario = new RepositoryReviewScenario(
                "payment-service",
                List.of(12, 18, 25),
                true,
                false,
                List.of("reviewer-a", "reviewer-b")
        );

        System.out.println("Enterprise workflow gate: " + scenario.mergeEligible());
    }
}
