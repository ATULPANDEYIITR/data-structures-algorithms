#include <algorithm>
#include <iomanip>
#include <iostream>
#include <map>
#include <memory>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

/*
 * Repository build scheduling is modeled as a recursion-tree case study.
 *
 * A build pipeline contains independent validation jobs. Some jobs spawn
 * additional checks. The tree records:
 *   - recursive branching,
 *   - execution depth,
 *   - local work at each node,
 *   - accumulated work,
 *   - and the difference between repeated and unique subproblems.
 *
 * The scenario is deliberately modeled as a recursive dependency evaluator
 * rather than as a generic recursion syntax exercise.
 */

struct ExecutionNode {
    string operation;
    string state;
    long long localCost;
    vector<unique_ptr<ExecutionNode>> children;

    ExecutionNode(string operation, string state, long long localCost = 1)
        : operation(move(operation)),
          state(move(state)),
          localCost(localCost) {}
};

long long nodeCount(const ExecutionNode& node) {
    long long total = 1;

    for (const auto& child : node.children) {
        total += nodeCount(*child);
    }

    return total;
}

long long leafCount(const ExecutionNode& node) {
    if (node.children.empty()) {
        return 1;
    }

    long long total = 0;

    for (const auto& child : node.children) {
        total += leafCount(*child);
    }

    return total;
}

long long treeCost(const ExecutionNode& node) {
    long long total = node.localCost;

    for (const auto& child : node.children) {
        total += treeCost(*child);
    }

    return total;
}

int treeHeight(const ExecutionNode& node) {
    if (node.children.empty()) {
        return 1;
    }

    int maximum = 0;

    for (const auto& child : node.children) {
        maximum = max(maximum, treeHeight(*child));
    }

    return maximum + 1;
}

void printTree(
    const ExecutionNode& node,
    const string& prefix = "",
    bool last = true,
    bool root = true
) {
    string connector;

    if (!root) {
        connector = last ? "└── " : "├── ";
    }

    cout << prefix
         << connector
         << node.operation
         << " ["
         << node.state
         << ", localCost="
         << node.localCost
         << "]\n";

    string childPrefix = prefix;

    if (!root) {
        childPrefix += last ? "    " : "│   ";
    }

    for (size_t i = 0; i < node.children.size(); ++i) {
        printTree(
            *node.children[i],
            childPrefix,
            i + 1 == node.children.size(),
            false
        );
    }
}


/*
 * A build stage recursively evaluates all required validation stages.
 *
 * If a stage has two independent prerequisites, its recursion tree has two
 * children. The total cost is obtained by summing local work over every node.
 */
unique_ptr<ExecutionNode> buildStageTree(
    const string& stage,
    int depth
) {
    auto node = make_unique<ExecutionNode>(
        "build-stage",
        stage,
        2
    );

    if (depth == 0) {
        return node;
    }

    node->children.push_back(
        buildStageTree(stage + ".compile", depth - 1)
    );

    node->children.push_back(
        buildStageTree(stage + ".test", depth - 1)
    );

    return node;
}


/*
 * Merge sort provides a clean recurrence:
 *
 * T(n) = 2T(n/2) + O(n)
 *
 * The recursion tree has logarithmic height, approximately n/2^level
 * elements per child, and O(n) aggregate merge work at every level.
 */
unique_ptr<ExecutionNode> mergeSortTree(
    vector<int>& values,
    int left,
    int right
) {
    auto node = make_unique<ExecutionNode>(
        "merge",
        "range=[" + to_string(left) + "," + to_string(right) + "]",
        max(1, right - left + 1)
    );

    if (left >= right) {
        return node;
    }

    int middle = left + (right - left) / 2;

    node->children.push_back(
        mergeSortTree(values, left, middle)
    );

    node->children.push_back(
        mergeSortTree(values, middle + 1, right)
    );

    inplace_merge(
        values.begin() + left,
        values.begin() + middle + 1,
        values.begin() + right + 1
    );

    return node;
}


/*
 * Fibonacci demonstrates a different recurrence:
 *
 * T(n) = T(n-1) + T(n-2) + O(1)
 *
 * It creates overlapping subproblems, so its raw tree contains many
 * repeated states. The memoized version below replaces repeated branches
 * with cached state reuse.
 */
unique_ptr<ExecutionNode> fibonacciTree(int n) {
    auto node = make_unique<ExecutionNode>(
        "fib",
        "n=" + to_string(n),
        1
    );

    if (n <= 1) {
        return node;
    }

    node->children.push_back(fibonacciTree(n - 1));
    node->children.push_back(fibonacciTree(n - 2));

    return node;
}


long long fibonacciMemoized(
    int n,
    map<int, long long>& cache,
    long long& calls
) {
    ++calls;

    auto found = cache.find(n);

    if (found != cache.end()) {
        return found->second;
    }

    if (n <= 1) {
        cache[n] = n;
        return n;
    }

    cache[n] =
        fibonacciMemoized(n - 1, cache, calls) +
        fibonacciMemoized(n - 2, cache, calls);

    return cache[n];
}


/*
 * A recursion tree does not automatically imply branching.
 * Binary search follows exactly one child per call.
 *
 * T(n) = T(n/2) + O(1)
 */
unique_ptr<ExecutionNode> binarySearchTree(
    const vector<int>& values,
    int target,
    int low,
    int high,
    bool& found
) {
    auto node = make_unique<ExecutionNode>(
        "binary-search",
        "range=[" + to_string(low) + "," + to_string(high) + "]",
        1
    );

    if (low > high) {
        found = false;
        return node;
    }

    int middle = low + (high - low) / 2;

    if (values[middle] == target) {
        found = true;
        node->state += ", index=" + to_string(middle);
        return node;
    }

    if (target < values[middle]) {
        node->children.push_back(
            binarySearchTree(
                values,
                target,
                low,
                middle - 1,
                found
            )
        );
    } else {
        node->children.push_back(
            binarySearchTree(
                values,
                target,
                middle + 1,
                high,
                found
            )
        );
    }

    return node;
}


void printRecurrenceTable() {
    cout << "\n=== Fibonacci tree growth ===\n";
    cout << left
         << setw(8) << "n"
         << setw(14) << "nodes"
         << setw(14) << "leaves"
         << setw(10) << "height"
         << "\n";

    for (int n = 0; n <= 10; ++n) {
        auto tree = fibonacciTree(n);

        cout << left
             << setw(8) << n
             << setw(14) << nodeCount(*tree)
             << setw(14) << leafCount(*tree)
             << setw(10) << treeHeight(*tree)
             << "\n";
    }
}


int main() {
    cout << "RECURSION TREES: C++ GOVERNANCE-BUILD CASE STUDY\n";
    cout << "================================================\n";

    /*
     * The first tree represents a recursively decomposed validation
     * pipeline. Every internal node owns two independent child tasks.
     */
    cout << "\n=== Recursive build validation tree ===\n";

    auto buildTree = buildStageTree("release-candidate", 3);
    printTree(*buildTree);

    cout << "\nTree height: " << treeHeight(*buildTree) << "\n";
    cout << "Tree nodes: " << nodeCount(*buildTree) << "\n";
    cout << "Leaf jobs: " << leafCount(*buildTree) << "\n";
    cout << "Accumulated local work: " << treeCost(*buildTree) << "\n";

    /*
     * Merge sort shows how local work changes with tree depth.
     * The leaves represent single-element ranges, while internal nodes
     * perform merge work proportional to their range.
     */
    cout << "\n=== Merge-sort recursion tree ===\n";

    vector<int> values{42, 17, 8, 31, 4, 29, 13, 22};
    auto original = values;

    auto sortTree = mergeSortTree(
        values,
        0,
        static_cast<int>(values.size()) - 1
    );

    cout << "Input: ";

    for (int value : original) {
        cout << value << ' ';
    }

    cout << "\nSorted: ";

    for (int value : values) {
        cout << value << ' ';
    }

    cout << "\n\n";
    printTree(*sortTree);

    cout << "\nMerge tree height: "
         << treeHeight(*sortTree) << "\n";

    cout << "Merge-tree accumulated cost: "
         << treeCost(*sortTree) << "\n";

    /*
     * Fibonacci makes the repeated-subproblem issue visible.
     */
    cout << "\n=== Overlapping Fibonacci subproblems ===\n";

    auto fibonacci = fibonacciTree(6);
    printTree(*fibonacci);

    cout << "\nRaw Fibonacci nodes: "
         << nodeCount(*fibonacci) << "\n";

    map<int, long long> cache;
    long long calls = 0;
    long long result = fibonacciMemoized(35, cache, calls);

    cout << "fib(35): " << result << "\n";
    cout << "Memoized recursive invocations: " << calls << "\n";
    cout << "Unique cached states: " << cache.size() << "\n";

    /*
     * Binary search demonstrates a one-child recursion tree. Calling this
     * a "tree" is still valid: every call is a node, but only one branch
     * survives from each internal node.
     */
    cout << "\n=== Single-path binary-search recursion ===\n";

    vector<int> sorted(32);
    iota(sorted.begin(), sorted.end(), 0);

    bool found = false;

    auto searchTree = binarySearchTree(
        sorted,
        23,
        0,
        static_cast<int>(sorted.size()) - 1,
        found
    );

    printTree(*searchTree);
    cout << "Target found: " << boolalpha << found << "\n";

    printRecurrenceTable();

    cout << "\n=== Complexity interpretation ===\n";
    cout << "Binary recursion with two half-size children often follows "
         << "T(n)=2T(n/2)+O(n), as in merge sort.\n";
    cout << "One-child halving follows T(n)=T(n/2)+O(1), as in binary search.\n";
    cout << "Fibonacci follows T(n)=T(n-1)+T(n-2)+O(1), with repeated states.\n";
    cout << "Memoization changes repeated evaluation from a large tree into "
         << "a graph-like state space where each state is computed once.\n";

    return 0;
}
