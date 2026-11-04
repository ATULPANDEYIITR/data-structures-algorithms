#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <limits>
#include <queue>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

using namespace std;

struct TreeNode {
    int value;
    TreeNode* left = nullptr;
    TreeNode* right = nullptr;
    TreeNode* parent = nullptr;

    explicit TreeNode(int v) : value(v) {}
};

class BinaryTree {
private:
    vector<TreeNode*> allocated;
    unordered_map<int, TreeNode*> nodes;
    TreeNode* root = nullptr;

public:
    BinaryTree() = default;

    BinaryTree(const BinaryTree&) = delete;
    BinaryTree& operator=(const BinaryTree&) = delete;

    ~BinaryTree() {
        for (TreeNode* node : allocated) {
            delete node;
        }
    }

    TreeNode* addRoot(int value) {
        if (root != nullptr) {
            throw invalid_argument("Root already exists.");
        }

        if (nodes.count(value)) {
            throw invalid_argument("Duplicate node value.");
        }

        root = new TreeNode(value);
        allocated.push_back(root);
        nodes[value] = root;

        return root;
    }

    TreeNode* addChild(int parentValue, int childValue, char side) {
        TreeNode* parent = getNode(parentValue);

        if (nodes.count(childValue)) {
            throw invalid_argument("Duplicate node value.");
        }

        TreeNode** position = nullptr;

        if (side == 'L') {
            position = &parent->left;
        } else if (side == 'R') {
            position = &parent->right;
        } else {
            throw invalid_argument("Side must be L or R.");
        }

        if (*position != nullptr) {
            throw invalid_argument("Child position is occupied.");
        }

        TreeNode* child = new TreeNode(childValue);
        child->parent = parent;

        *position = child;
        allocated.push_back(child);
        nodes[childValue] = child;

        return child;
    }

    TreeNode* getNode(int value) const {
        auto it = nodes.find(value);

        if (it == nodes.end()) {
            throw out_of_range("Unknown node value.");
        }

        return it->second;
    }

    TreeNode* getRoot() const {
        return root;
    }

    size_t size() const {
        return nodes.size();
    }

    int recursiveLCA(int p, int q) const {
        TreeNode* first = getNode(p);
        TreeNode* second = getNode(q);

        function<TreeNode*(TreeNode*)> solve =
            [&](TreeNode* node) -> TreeNode* {
                if (node == nullptr || node == first || node == second) {
                    return node;
                }

                TreeNode* left = solve(node->left);
                TreeNode* right = solve(node->right);

                if (left != nullptr && right != nullptr) {
                    return node;
                }

                return left != nullptr ? left : right;
            };

        TreeNode* answer = solve(root);

        if (answer == nullptr) {
            throw runtime_error("No common ancestor.");
        }

        return answer->value;
    }

    int parentLCA(int p, int q) const {
        TreeNode* first = getNode(p);
        TreeNode* second = getNode(q);

        unordered_set<int> ancestors;

        while (first != nullptr) {
            ancestors.insert(first->value);
            first = first->parent;
        }

        while (second != nullptr) {
            if (ancestors.count(second->value)) {
                return second->value;
            }

            second = second->parent;
        }

        throw runtime_error("No common ancestor.");
    }

    int depth(int value) const {
        TreeNode* node = getNode(value);
        int result = 0;

        while (node->parent != nullptr) {
            result++;
            node = node->parent;
        }

        return result;
    }

    int depthLCA(int p, int q) const {
        TreeNode* first = getNode(p);
        TreeNode* second = getNode(q);

        int firstDepth = depth(p);
        int secondDepth = depth(q);

        while (firstDepth > secondDepth) {
            first = first->parent;
            firstDepth--;
        }

        while (secondDepth > firstDepth) {
            second = second->parent;
            secondDepth--;
        }

        while (first != second) {
            first = first->parent;
            second = second->parent;
        }

        if (first == nullptr) {
            throw runtime_error("No common ancestor.");
        }

        return first->value;
    }

    bool isAncestor(int ancestor, int descendant) const {
        TreeNode* target = getNode(ancestor);
        TreeNode* current = getNode(descendant);

        while (current != nullptr) {
            if (current == target) {
                return true;
            }

            current = current->parent;
        }

        return false;
    }

    int distance(int p, int q) const {
        int ancestorValue = parentLCA(p, q);
        TreeNode* ancestor = getNode(ancestorValue);

        auto count = [&](TreeNode* node) {
            int result = 0;

            while (node != ancestor) {
                node = node->parent;
                result++;
            }

            return result;
        };

        return count(getNode(p)) + count(getNode(q));
    }
};

class BinaryLifting {
private:
    const BinaryTree& tree;
    int levels;

    unordered_map<int, int> depth;
    unordered_map<int, vector<int>> up;

public:
    explicit BinaryLifting(const BinaryTree& input)
        : tree(input) {

        if (tree.size() == 0) {
            throw invalid_argument("Cannot index an empty tree.");
        }

        levels = 1;

        while ((1ULL << levels) <= tree.size()) {
            levels++;
        }

        queue<pair<TreeNode*, int>> pending;
        pending.push({tree.getRoot(), -1});

        while (!pending.empty()) {
            auto [node, parent] = pending.front();
            pending.pop();

            int d = parent == -1 ? 0 : depth[parent] + 1;

            depth[node->value] = d;

            vector<int> ancestors(levels, -1);
            ancestors[0] = parent;

            up[node->value] = ancestors;

            if (node->left) {
                pending.push({node->left, node->value});
            }

            if (node->right) {
                pending.push({node->right, node->value});
            }
        }

        for (int j = 1; j < levels; j++) {
            for (auto& entry : up) {
                int value = entry.first;
                int previous = entry.second[j - 1];

                if (previous != -1) {
                    entry.second[j] = up.at(previous)[j - 1];
                }
            }
        }
    }

    int kthAncestor(int value, int k) const {
        if (!up.count(value)) {
            throw out_of_range("Unknown node.");
        }

        if (k < 0) {
            throw invalid_argument("k cannot be negative.");
        }

        if (k > depth.at(value)) {
            return -1;
        }

        int bit = 0;

        while (k > 0) {
            if (k & 1) {
                value = up.at(value)[bit];

                if (value == -1) {
                    return -1;
                }
            }

            k >>= 1;
            bit++;
        }

        return value;
    }

    int lca(int p, int q) const {
        if (!up.count(p) || !up.count(q)) {
            throw out_of_range("Both nodes must exist.");
        }

        if (depth.at(p) < depth.at(q)) {
            swap(p, q);
        }

        p = kthAncestor(p, depth.at(p) - depth.at(q));

        if (p == q) {
            return p;
        }

        for (int j = levels - 1; j >= 0; j--) {
            int a = up.at(p)[j];
            int b = up.at(q)[j];

            if (a != b) {
                p = a;
                q = b;
            }
        }

        return up.at(p)[0];
    }

    int distance(int p, int q) const {
        int ancestor = lca(p, q);

        return depth.at(p) + depth.at(q) - 2 * depth.at(ancestor);
    }

    vector<int> batchLCA(
        const vector<pair<int, int>>& queries
    ) const {
        vector<int> results;
        results.reserve(queries.size());

        for (const auto& [p, q] : queries) {
            results.push_back(lca(p, q));
        }

        return results;
    }
};

BinaryTree createSampleTree() {
    BinaryTree tree;

    tree.addRoot(1);

    tree.addChild(1, 2, 'L');
    tree.addChild(1, 3, 'R');

    tree.addChild(2, 4, 'L');
    tree.addChild(2, 5, 'R');

    tree.addChild(3, 6, 'L');
    tree.addChild(3, 7, 'R');

    tree.addChild(4, 8, 'L');
    tree.addChild(4, 9, 'R');

    tree.addChild(5, 10, 'L');

    return tree;
}

void runTests() {
    BinaryTree tree = createSampleTree();
    BinaryLifting index(tree);

    assert(tree.recursiveLCA(8, 9) == 4);
    assert(tree.recursiveLCA(8, 10) == 2);
    assert(tree.recursiveLCA(8, 6) == 1);
    assert(tree.recursiveLCA(5, 10) == 5);

    assert(tree.parentLCA(8, 10) == 2);
    assert(tree.depthLCA(8, 6) == 1);

    assert(index.lca(8, 10) == 2);
    assert(index.lca(8, 6) == 1);
    assert(index.kthAncestor(8, 3) == 1);
    assert(index.kthAncestor(8, 4) == -1);

    assert(index.distance(8, 10) == 4);
    assert(tree.distance(8, 6) == 5);

    assert(tree.isAncestor(2, 8));
    assert(!tree.isAncestor(3, 8));

    bool failed = false;

    try {
        index.lca(8, 999);
    } catch (const out_of_range&) {
        failed = true;
    }

    assert(failed);

    cout << "All C++17 LCA tests passed.\n";
}

int main() {
    try {
        BinaryTree tree = createSampleTree();
        BinaryLifting index(tree);

        cout << "LOWEST COMMON ANCESTOR\n\n";

        vector<pair<int, int>> queries = {
            {8, 9},
            {8, 10},
            {8, 6},
            {5, 10},
            {2, 8}
        };

        for (const auto& [p, q] : queries) {
            cout
                << "Nodes " << p << ", " << q
                << " | Recursive: " << tree.recursiveLCA(p, q)
                << " | Parent: " << tree.parentLCA(p, q)
                << " | Binary lifting: " << index.lca(p, q)
                << '\n';
        }

        cout << "\nDistance 8 to 10: "
             << index.distance(8, 10) << '\n';

        cout << "3rd ancestor of 8: "
             << index.kthAncestor(8, 3) << '\n';

        cout << "Is 2 an ancestor of 8: "
             << boolalpha << tree.isAncestor(2, 8) << '\n';

        cout << "\nBatch queries:\n";

        for (int answer : index.batchLCA(queries)) {
            cout << answer << '\n';
        }

        runTests();

    } catch (const exception& error) {
        cerr << "Error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
