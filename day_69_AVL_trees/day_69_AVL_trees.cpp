#include <algorithm>
#include <cassert>
#include <cmath>
#include <functional>
#include <iostream>
#include <limits>
#include <memory>
#include <optional>
#include <queue>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <vector>

using namespace std;

enum class RotationType {
    LL,
    RR,
    LR,
    RL
};

string rotationName(RotationType type) {
    switch (type) {
        case RotationType::LL: return "LL";
        case RotationType::RR: return "RR";
        case RotationType::LR: return "LR";
        case RotationType::RL: return "RL";
    }

    throw logic_error("Unknown rotation.");
}

struct AVLNode {
    int key;
    int height;
    unique_ptr<AVLNode> left;
    unique_ptr<AVLNode> right;

    explicit AVLNode(int value)
        : key(value), height(1),
          left(nullptr), right(nullptr) {}
};

struct AVLStatistics {
    size_t insertions = 0;
    size_t deletions = 0;
    size_t searches = 0;
    size_t duplicates = 0;

    size_t LL = 0;
    size_t RR = 0;
    size_t LR = 0;
    size_t RL = 0;
};

class AVLTree {
private:
    unique_ptr<AVLNode> root;
    AVLStatistics statistics;

    static int height(const unique_ptr<AVLNode>& node) {
        return node ? node->height : 0;
    }

    static int balanceFactor(const unique_ptr<AVLNode>& node) {
        if (!node) return 0;

        return height(node->left) - height(node->right);
    }

    static void updateHeight(AVLNode& node) {
        node.height = 1 + max(
            node.left ? node.left->height : 0,
            node.right ? node.right->height : 0
        );
    }

    unique_ptr<AVLNode> rotateRight(
        unique_ptr<AVLNode> y
    ) {
        if (!y || !y->left) {
            throw logic_error("Invalid right rotation.");
        }

        auto x = move(y->left);
        auto transferred = move(x->right);

        y->left = move(transferred);

        updateHeight(*y);

        x->right = move(y);

        updateHeight(*x);

        return x;
    }

    unique_ptr<AVLNode> rotateLeft(
        unique_ptr<AVLNode> x
    ) {
        if (!x || !x->right) {
            throw logic_error("Invalid left rotation.");
        }

        auto y = move(x->right);
        auto transferred = move(y->left);

        x->right = move(transferred);

        updateHeight(*x);

        y->left = move(x);

        updateHeight(*y);

        return y;
    }

    unique_ptr<AVLNode> rebalance(
        unique_ptr<AVLNode> node
    ) {
        if (!node) return nullptr;

        updateHeight(*node);

        int balance = balanceFactor(node);

        if (balance > 1) {
            if (balanceFactor(node->left) < 0) {
                statistics.LR++;
                node->left = rotateLeft(move(node->left));
            } else {
                statistics.LL++;
            }

            return rotateRight(move(node));
        }

        if (balance < -1) {
            if (balanceFactor(node->right) > 0) {
                statistics.RL++;
                node->right = rotateRight(move(node->right));
            } else {
                statistics.RR++;
            }

            return rotateLeft(move(node));
        }

        return node;
    }

    unique_ptr<AVLNode> insertNode(
        unique_ptr<AVLNode> node,
        int key
    ) {
        if (!node) {
            return make_unique<AVLNode>(key);
        }

        if (key < node->key) {
            node->left = insertNode(
                move(node->left), key
            );
        } else if (key > node->key) {
            node->right = insertNode(
                move(node->right), key
            );
        } else {
            return node;
        }

        return rebalance(move(node));
    }

    static AVLNode* minimumNode(AVLNode* node) {
        while (node && node->left) {
            node = node->left.get();
        }

        return node;
    }

    unique_ptr<AVLNode> deleteNode(
        unique_ptr<AVLNode> node,
        int key
    ) {
        if (!node) return nullptr;

        if (key < node->key) {
            node->left = deleteNode(
                move(node->left), key
            );
        } else if (key > node->key) {
            node->right = deleteNode(
                move(node->right), key
            );
        } else {
            if (!node->left) {
                return move(node->right);
            }

            if (!node->right) {
                return move(node->left);
            }

            AVLNode* successor = minimumNode(
                node->right.get()
            );

            node->key = successor->key;

            node->right = deleteNode(
                move(node->right), successor->key
            );
        }

        return rebalance(move(node));
    }

    static void inorder(
        const AVLNode* node,
        vector<int>& result
    ) {
        if (!node) return;

        inorder(node->left.get(), result);
        result.push_back(node->key);
        inorder(node->right.get(), result);
    }

    static void preorder(
        const AVLNode* node,
        vector<int>& result
    ) {
        if (!node) return;

        result.push_back(node->key);
        preorder(node->left.get(), result);
        preorder(node->right.get(), result);
    }

    static void postorder(
        const AVLNode* node,
        vector<int>& result
    ) {
        if (!node) return;

        postorder(node->left.get(), result);
        postorder(node->right.get(), result);
        result.push_back(node->key);
    }

    static void rangeQuery(
        const AVLNode* node,
        int lower,
        int upper,
        vector<int>& result
    ) {
        if (!node) return;

        if (node->key > lower) {
            rangeQuery(node->left.get(), lower, upper, result);
        }

        if (node->key >= lower && node->key <= upper) {
            result.push_back(node->key);
        }

        if (node->key < upper) {
            rangeQuery(node->right.get(), lower, upper, result);
        }
    }

    struct ValidationResult {
        bool valid;
        int height;
    };

    static ValidationResult validateNode(
        const AVLNode* node,
        optional<int> lower,
        optional<int> upper
    ) {
        if (!node) return {true, 0};

        if (
            (lower && node->key <= *lower) ||
            (upper && node->key >= *upper)
        ) {
            return {false, 0};
        }

        auto left = validateNode(
            node->left.get(), lower, node->key
        );

        auto right = validateNode(
            node->right.get(), node->key, upper
        );

        int expectedHeight = 1 + max(
            left.height,
            right.height
        );

        int balance = left.height - right.height;

        bool valid = (
            left.valid &&
            right.valid &&
            node->height == expectedHeight &&
            abs(balance) <= 1
        );

        return {valid, expectedHeight};
    }

    static void display(
        const AVLNode* node,
        const string& prefix,
        bool isLeft
    ) {
        if (!node) return;

        display(
            node->right.get(),
            prefix + (isLeft ? "│   " : "    "),
            false
        );

        cout << prefix
             << (isLeft ? "└── " : "┌── ")
             << node->key
             << " [H=" << node->height
             << ", BF="
             << (
                 (node->left ? node->left->height : 0) -
                 (node->right ? node->right->height : 0)
             )
             << "]\n";

        display(
            node->left.get(),
            prefix + (isLeft ? "    " : "│   "),
            true
        );
    }

public:
    AVLTree() = default;

    AVLTree(const AVLTree&) = delete;
    AVLTree& operator=(const AVLTree&) = delete;

    AVLTree(AVLTree&&) noexcept = default;
    AVLTree& operator=(AVLTree&&) noexcept = default;

    bool insert(int key) {
        if (search(key)) {
            statistics.duplicates++;
            return false;
        }

        root = insertNode(move(root), key);

        statistics.insertions++;

        return true;
    }

    bool search(int key) {
        statistics.searches++;

        const AVLNode* current = root.get();

        while (current) {
            if (key == current->key) {
                return true;
            }

            current = key < current->key
                ? current->left.get()
                : current->right.get();
        }

        return false;
    }

    bool erase(int key) {
        if (!search(key)) {
            return false;
        }

        root = deleteNode(move(root), key);

        statistics.deletions++;

        return true;
    }

    optional<int> minimum() const {
        if (!root) return nullopt;

        AVLNode* node = minimumNode(root.get());

        return node->key;
    }

    optional<int> maximum() const {
        if (!root) return nullopt;

        const AVLNode* current = root.get();

        while (current->right) {
            current = current->right.get();
        }

        return current->key;
    }

    int treeHeight() const {
        return height(root);
    }

    vector<int> inorder() const {
        vector<int> result;

        inorder(root.get(), result);

        return result;
    }

    vector<int> preorder() const {
        vector<int> result;

        preorder(root.get(), result);

        return result;
    }

    vector<int> postorder() const {
        vector<int> result;

        postorder(root.get(), result);

        return result;
    }

    vector<vector<int>> levelOrder() const {
        vector<vector<int>> result;

        if (!root) return result;

        queue<const AVLNode*> pending;

        pending.push(root.get());

        while (!pending.empty()) {
            size_t count = pending.size();

            vector<int> level;

            for (size_t i = 0; i < count; ++i) {
                const AVLNode* node = pending.front();

                pending.pop();

                level.push_back(node->key);

                if (node->left) {
                    pending.push(node->left.get());
                }

                if (node->right) {
                    pending.push(node->right.get());
                }
            }

            result.push_back(move(level));
        }

        return result;
    }

    vector<int> rangeQuery(int lower, int upper) const {
        if (lower > upper) {
            throw invalid_argument(
                "Lower bound cannot exceed upper bound."
            );
        }

        vector<int> result;

        rangeQuery(root.get(), lower, upper, result);

        return result;
    }

    bool validate() const {
        return validateNode(
            root.get(), nullopt, nullopt
        ).valid;
    }

    void printTree() const {
        if (!root) {
            cout << "(empty tree)\n";
            return;
        }

        display(root.get(), "", true);
    }

    const AVLStatistics& getStatistics() const {
        return statistics;
    }

    void clear() {
        root.reset();
    }
};


void printVector(const string& label, const vector<int>& values) {
    cout << label << ": ";

    for (size_t i = 0; i < values.size(); ++i) {
        if (i) cout << ", ";

        cout << values[i];
    }

    cout << '\n';
}


void demonstrateRotations() {
    cout << "\nROTATION CASES\n";

    const vector<pair<RotationType, vector<int>>> cases = {
        {RotationType::LL, {30, 20, 10}},
        {RotationType::RR, {10, 20, 30}},
        {RotationType::LR, {30, 10, 20}},
        {RotationType::RL, {10, 30, 20}}
    };

    for (const auto& test : cases) {
        AVLTree tree;

        for (int key : test.second) {
            tree.insert(key);
        }

        cout << rotationName(test.first)
             << " root = " << tree.preorder().front()
             << ", inorder = ";

        printVector("", tree.inorder());

        assert(tree.preorder().front() == 20);
        assert(tree.validate());
    }
}


void runTests() {
    AVLTree tree;

    assert(tree.inorder().empty());
    assert(tree.treeHeight() == 0);

    const vector<int> values = {
        50, 30, 70, 20, 40, 60, 80,
        10, 25, 35, 45, 65, 75, 90
    };

    for (int key : values) {
        assert(tree.insert(key));
    }

    assert(!tree.insert(50));

    assert(tree.validate());

    assert(tree.search(40));
    assert(!tree.search(999));

    assert(tree.minimum() == optional<int>(10));
    assert(tree.maximum() == optional<int>(90));

    vector<int> sorted = values;

    sort(sorted.begin(), sorted.end());

    assert(tree.inorder() == sorted);

    assert(
        tree.rangeQuery(25, 65) ==
        vector<int>({25, 30, 35, 40, 45, 50, 60, 65})
    );

    assert(tree.erase(50));
    assert(!tree.search(50));
    assert(tree.validate());

    assert(tree.erase(10));
    assert(tree.erase(20));
    assert(tree.validate());

    assert(!tree.erase(999));

    try {
        tree.rangeQuery(100, 10);
        assert(false);
    } catch (const invalid_argument&) {
        // Expected validation failure.
    }

    AVLTree empty;

    assert(!empty.minimum());
    assert(!empty.maximum());
    assert(empty.inorder().empty());
    assert(empty.validate());

    cout << "\nAll C++17 AVL tests passed.\n";
}


int main() {
    try {
        cout << "AVL TREE: INVENTORY INDEXING ENGINE\n";
        cout << "===================================\n";

        demonstrateRotations();

        AVLTree inventory;

        const vector<int> productIds = {
            1001, 500, 1500, 250, 750,
            1250, 1750, 100, 350, 650,
            850, 1100, 1400, 1600, 1900
        };

        cout << "\nINSERTING PRODUCT RECORDS\n";

        for (int id : productIds) {
            inventory.insert(id);
        }

        inventory.printTree();

        cout << "\nTREE TRAVERSALS\n";

        printVector("In-order", inventory.inorder());
        printVector("Pre-order", inventory.preorder());
        printVector("Post-order", inventory.postorder());

        cout << "\nLEVEL-ORDER\n";

        for (const auto& level : inventory.levelOrder()) {
            printVector("Level", level);
        }

        cout << "\nSEARCH OPERATIONS\n";

        cout << "Product 1250: "
             << (inventory.search(1250) ? "Found" : "Not found")
             << '\n';

        cout << "Product 9999: "
             << (inventory.search(9999) ? "Found" : "Not found")
             << '\n';

        cout << "Minimum ID: " << *inventory.minimum() << '\n';
        cout << "Maximum ID: " << *inventory.maximum() << '\n';
        cout << "Tree height: " << inventory.treeHeight() << '\n';

        printVector(
            "Products 500-1500",
            inventory.rangeQuery(500, 1500)
        );

        cout << "\nDELETION\n";

        inventory.erase(1001);

        cout << "After deleting 1001:\n";

        printVector("In-order", inventory.inorder());

        cout << "Valid AVL structure: "
             << (inventory.validate() ? "Yes" : "No")
             << '\n';

        const auto& stats = inventory.getStatistics();

        cout << "\nOPERATION STATISTICS\n";
        cout << "Insertions: " << stats.insertions << '\n';
        cout << "Deletions: " << stats.deletions << '\n';
        cout << "Searches: " << stats.searches << '\n';
        cout << "Duplicates: " << stats.duplicates << '\n';

        cout << "LL rotations: " << stats.LL << '\n';
        cout << "RR rotations: " << stats.RR << '\n';
        cout << "LR rotations: " << stats.LR << '\n';
        cout << "RL rotations: " << stats.RL << '\n';

        runTests();

    } catch (const exception& error) {
        cerr << "AVL execution error: "
             << error.what() << '\n';

        return 1;
    }

    return 0;
}
