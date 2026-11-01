#include <algorithm>
#include <cassert>
#include <chrono>
#include <cstddef>
#include <iostream>
#include <queue>
#include <stack>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <utility>
#include <vector>

using namespace std;

struct TreeNode {
    int value;
    TreeNode* left;
    TreeNode* right;

    explicit TreeNode(int v)
        : value(v), left(nullptr), right(nullptr) {}
};

enum class TraversalOrder {
    Preorder,
    Inorder,
    Postorder,
    LevelOrder
};

class BinaryTree {
private:
    TreeNode* root;

    static void destroy(TreeNode* node) {
        if (!node) return;

        destroy(node->left);
        destroy(node->right);
        delete node;
    }

    static void preorderRecursive(
        TreeNode* node,
        vector<int>& result
    ) {
        if (!node) return;

        result.push_back(node->value);
        preorderRecursive(node->left, result);
        preorderRecursive(node->right, result);
    }

    static void inorderRecursive(
        TreeNode* node,
        vector<int>& result
    ) {
        if (!node) return;

        inorderRecursive(node->left, result);
        result.push_back(node->value);
        inorderRecursive(node->right, result);
    }

    static void postorderRecursive(
        TreeNode* node,
        vector<int>& result
    ) {
        if (!node) return;

        postorderRecursive(node->left, result);
        postorderRecursive(node->right, result);
        result.push_back(node->value);
    }

public:
    explicit BinaryTree(int value) : root(new TreeNode(value)) {}

    BinaryTree(const BinaryTree&) = delete;
    BinaryTree& operator=(const BinaryTree&) = delete;

    ~BinaryTree() {
        destroy(root);
    }

    TreeNode* getRoot() const {
        return root;
    }

    // Ownership of the supplied child remains with the tree.
    void attachLeft(TreeNode* parent, int value) {
        if (!parent || parent->left) {
            throw invalid_argument("Invalid parent or occupied left child.");
        }

        parent->left = new TreeNode(value);
    }

    void attachRight(TreeNode* parent, int value) {
        if (!parent || parent->right) {
            throw invalid_argument("Invalid parent or occupied right child.");
        }

        parent->right = new TreeNode(value);
    }

    vector<int> preorderRecursive() const {
        vector<int> result;
        preorderRecursive(root, result);
        return result;
    }

    vector<int> inorderRecursive() const {
        vector<int> result;
        inorderRecursive(root, result);
        return result;
    }

    vector<int> postorderRecursive() const {
        vector<int> result;
        postorderRecursive(root, result);
        return result;
    }

    vector<int> preorderIterative() const {
        vector<int> result;
        if (!root) return result;

        stack<TreeNode*> nodes;
        nodes.push(root);

        while (!nodes.empty()) {
            TreeNode* current = nodes.top();
            nodes.pop();

            result.push_back(current->value);

            if (current->right) nodes.push(current->right);
            if (current->left) nodes.push(current->left);
        }

        return result;
    }

    vector<int> inorderIterative() const {
        vector<int> result;
        stack<TreeNode*> nodes;

        TreeNode* current = root;

        while (current || !nodes.empty()) {
            while (current) {
                nodes.push(current);
                current = current->left;
            }

            current = nodes.top();
            nodes.pop();

            result.push_back(current->value);
            current = current->right;
        }

        return result;
    }

    vector<int> postorderIterative() const {
        vector<int> result;
        if (!root) return result;

        stack<pair<TreeNode*, bool>> nodes;
        nodes.push({root, false});

        while (!nodes.empty()) {
            auto [current, visited] = nodes.top();
            nodes.pop();

            if (visited) {
                result.push_back(current->value);
                continue;
            }

            nodes.push({current, true});

            if (current->right) {
                nodes.push({current->right, false});
            }

            if (current->left) {
                nodes.push({current->left, false});
            }
        }

        return result;
    }

    // Breadth-first traversal uses a FIFO queue.
    vector<int> levelOrder() const {
        vector<int> result;
        if (!root) return result;

        queue<TreeNode*> nodes;
        nodes.push(root);

        while (!nodes.empty()) {
            TreeNode* current = nodes.front();
            nodes.pop();

            result.push_back(current->value);

            if (current->left) nodes.push(current->left);
            if (current->right) nodes.push(current->right);
        }

        return result;
    }

    vector<vector<int>> levelOrderByLevel() const {
        vector<vector<int>> levels;
        if (!root) return levels;

        queue<TreeNode*> nodes;
        nodes.push(root);

        while (!nodes.empty()) {
            size_t levelSize = nodes.size();
            vector<int> level;

            for (size_t i = 0; i < levelSize; ++i) {
                TreeNode* current = nodes.front();
                nodes.pop();

                level.push_back(current->value);

                if (current->left) nodes.push(current->left);
                if (current->right) nodes.push(current->right);
            }

            levels.push_back(move(level));
        }

        return levels;
    }

    size_t countNodes() const {
        if (!root) return 0;

        size_t count = 0;
        stack<TreeNode*> nodes;
        nodes.push(root);

        while (!nodes.empty()) {
            TreeNode* current = nodes.top();
            nodes.pop();
            ++count;

            if (current->left) nodes.push(current->left);
            if (current->right) nodes.push(current->right);
        }

        return count;
    }

    size_t height() const {
        if (!root) return 0;

        queue<pair<TreeNode*, size_t>> nodes;
        nodes.push({root, 1});

        size_t maximum = 0;

        while (!nodes.empty()) {
            auto [current, depth] = nodes.front();
            nodes.pop();

            maximum = max(maximum, depth);

            if (current->left) {
                nodes.push({current->left, depth + 1});
            }

            if (current->right) {
                nodes.push({current->right, depth + 1});
            }
        }

        return maximum;
    }

    TreeNode* find(int target) const {
        if (!root) return nullptr;

        queue<TreeNode*> nodes;
        nodes.push(root);

        while (!nodes.empty()) {
            TreeNode* current = nodes.front();
            nodes.pop();

            if (current->value == target) return current;

            if (current->left) nodes.push(current->left);
            if (current->right) nodes.push(current->right);
        }

        return nullptr;
    }

    static string toString(
        const vector<int>& values
    ) {
        string output = "[";

        for (size_t i = 0; i < values.size(); ++i) {
            if (i > 0) output += ", ";
            output += to_string(values[i]);
        }

        output += "]";
        return output;
    }
};

void printLevels(const vector<vector<int>>& levels) {
    for (size_t i = 0; i < levels.size(); ++i) {
        cout << "Level " << i << ": "
             << BinaryTree::toString(levels[i]) << '\n';
    }
}

void runTests(const BinaryTree& tree) {
    assert(
        tree.preorderRecursive() ==
        vector<int>({50, 30, 20, 10, 40, 70, 60, 65, 80})
    );

    assert(
        tree.inorderRecursive() ==
        vector<int>({10, 20, 30, 40, 50, 60, 65, 70, 80})
    );

    assert(
        tree.postorderRecursive() ==
        vector<int>({10, 20, 40, 30, 65, 60, 80, 70, 50})
    );

    assert(
        tree.levelOrder() ==
        vector<int>({50, 30, 70, 20, 40, 60, 80, 10, 65})
    );

    assert(tree.preorderRecursive() == tree.preorderIterative());
    assert(tree.inorderRecursive() == tree.inorderIterative());
    assert(tree.postorderRecursive() == tree.postorderIterative());

    assert(tree.countNodes() == 9);
    assert(tree.height() == 4);
    assert(tree.find(65) != nullptr);
    assert(tree.find(999) == nullptr);

    BinaryTree single(42);
    assert(single.inorderIterative() == vector<int>({42}));

    bool rejected = false;

    try {
        single.attachLeft(nullptr, 10);
    } catch (const invalid_argument&) {
        rejected = true;
    }

    assert(rejected);

    cout << "All C++17 traversal tests passed.\n";
}

int main() {
    try {
        /*
         * Repository-style hierarchical data:
         * each node represents an entity and its children
         * represent subordinate entities.
         */

        BinaryTree tree(50);
        TreeNode* root = tree.getRoot();

        tree.attachLeft(root, 30);
        tree.attachRight(root, 70);

        tree.attachLeft(root->left, 20);
        tree.attachRight(root->left, 40);

        tree.attachLeft(root->right, 60);
        tree.attachRight(root->right, 80);

        tree.attachLeft(root->left->left, 10);
        tree.attachRight(root->right->left, 65);

        cout << "BINARY TREE TRAVERSAL ENGINE\n";
        cout << "============================\n";

        const auto start = chrono::steady_clock::now();

        cout << "Preorder recursive : "
             << BinaryTree::toString(tree.preorderRecursive()) << '\n';

        cout << "Preorder iterative : "
             << BinaryTree::toString(tree.preorderIterative()) << '\n';

        cout << "Inorder recursive  : "
             << BinaryTree::toString(tree.inorderRecursive()) << '\n';

        cout << "Inorder iterative  : "
             << BinaryTree::toString(tree.inorderIterative()) << '\n';

        cout << "Postorder recursive: "
             << BinaryTree::toString(tree.postorderRecursive()) << '\n';

        cout << "Postorder iterative: "
             << BinaryTree::toString(tree.postorderIterative()) << '\n';

        cout << "Level-order        : "
             << BinaryTree::toString(tree.levelOrder()) << '\n';

        cout << "\nLEVEL-WISE OUTPUT\n";
        printLevels(tree.levelOrderByLevel());

        cout << "\nTREE METRICS\n";
        cout << "Node count: " << tree.countNodes() << '\n';
        cout << "Height: " << tree.height() << '\n';
        cout << "Find 65: "
             << (tree.find(65) ? "Found" : "Not found") << '\n';

        const auto end = chrono::steady_clock::now();

        const auto elapsed =
            chrono::duration_cast<chrono::nanoseconds>(
                end - start
            ).count();

        cout << "Execution time: " << elapsed << " ns\n\n";

        runTests(tree);

    } catch (const exception& error) {
        cerr << "Error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
