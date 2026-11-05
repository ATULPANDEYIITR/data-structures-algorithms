#include <algorithm>
#include <cassert>
#include <cstddef>
#include <iostream>
#include <memory>
#include <optional>
#include <stdexcept>
#include <string>
#include <vector>

class BinarySearchTree {
private:
    struct Node {
        int key;
        std::unique_ptr<Node> left;
        std::unique_ptr<Node> right;

        explicit Node(int value) : key(value) {}
    };

    std::unique_ptr<Node> root;
    std::size_t node_count = 0;

    static const Node* findMinimum(const Node* node) {
        if (node == nullptr) return nullptr;

        while (node->left) {
            node = node->left.get();
        }

        return node;
    }

    static const Node* findMaximum(const Node* node) {
        if (node == nullptr) return nullptr;

        while (node->right) {
            node = node->right.get();
        }

        return node;
    }

    static bool validateNode(
        const Node* node,
        std::optional<int> lower,
        std::optional<int> upper
    ) {
        if (node == nullptr) return true;

        if (lower && node->key <= *lower) return false;
        if (upper && node->key >= *upper) return false;

        return validateNode(node->left.get(), lower, node->key)
            && validateNode(node->right.get(), node->key, upper);
    }

    static void inorderTraversal(
        const Node* node,
        std::vector<int>& result
    ) {
        if (node == nullptr) return;

        inorderTraversal(node->left.get(), result);
        result.push_back(node->key);
        inorderTraversal(node->right.get(), result);
    }

    static void preorderTraversal(
        const Node* node,
        std::vector<int>& result
    ) {
        if (node == nullptr) return;

        result.push_back(node->key);
        preorderTraversal(node->left.get(), result);
        preorderTraversal(node->right.get(), result);
    }

    static void postorderTraversal(
        const Node* node,
        std::vector<int>& result
    ) {
        if (node == nullptr) return;

        postorderTraversal(node->left.get(), result);
        postorderTraversal(node->right.get(), result);
        result.push_back(node->key);
    }

    static int calculateHeight(const Node* node) {
        if (node == nullptr) return 0;

        return 1 + std::max(
            calculateHeight(node->left.get()),
            calculateHeight(node->right.get())
        );
    }

    static bool eraseNode(std::unique_ptr<Node>& node, int key) {
        if (!node) return false;

        if (key < node->key) {
            return eraseNode(node->left, key);
        }

        if (key > node->key) {
            return eraseNode(node->right, key);
        }

        // No left child: replace with the right subtree.
        if (!node->left) {
            node = std::move(node->right);
            return true;
        }

        // No right child: replace with the left subtree.
        if (!node->right) {
            node = std::move(node->left);
            return true;
        }

        // Two children: copy the inorder successor's key,
        // then remove the successor from the right subtree.
        const Node* successor = findMinimum(node->right.get());
        node->key = successor->key;

        return eraseNode(node->right, successor->key);
    }

    static void collectRange(
        const Node* node,
        int low,
        int high,
        std::vector<int>& result
    ) {
        if (node == nullptr) return;

        if (node->key > low) {
            collectRange(node->left.get(), low, high, result);
        }

        if (node->key >= low && node->key <= high) {
            result.push_back(node->key);
        }

        if (node->key < high) {
            collectRange(node->right.get(), low, high, result);
        }
    }

public:
    BinarySearchTree() = default;

    // Prevent accidental copying of an owning tree.
    BinarySearchTree(const BinarySearchTree&) = delete;
    BinarySearchTree& operator=(const BinarySearchTree&) = delete;

    BinarySearchTree(BinarySearchTree&&) noexcept = default;
    BinarySearchTree& operator=(BinarySearchTree&&) noexcept = default;

    bool insert(int key) {
        std::unique_ptr<Node>* current = &root;

        while (*current) {
            if (key == (*current)->key) {
                return false;
            }

            current = key < (*current)->key
                ? &((*current)->left)
                : &((*current)->right);
        }

        *current = std::make_unique<Node>(key);
        ++node_count;

        return true;
    }

    bool search(int key) const {
        const Node* current = root.get();

        while (current != nullptr) {
            if (key == current->key) return true;

            current = key < current->key
                ? current->left.get()
                : current->right.get();
        }

        return false;
    }

    std::optional<int> minimum() const {
        const Node* node = findMinimum(root.get());

        if (node == nullptr) return std::nullopt;
        return node->key;
    }

    std::optional<int> maximum() const {
        const Node* node = findMaximum(root.get());

        if (node == nullptr) return std::nullopt;
        return node->key;
    }

    std::optional<int> predecessor(int key) const {
        const Node* current = root.get();
        std::optional<int> candidate;

        while (current != nullptr) {
            if (current->key < key) {
                candidate = current->key;
                current = current->right.get();
            } else {
                current = current->left.get();
            }
        }

        return candidate;
    }

    std::optional<int> successor(int key) const {
        const Node* current = root.get();
        std::optional<int> candidate;

        while (current != nullptr) {
            if (current->key > key) {
                candidate = current->key;
                current = current->left.get();
            } else {
                current = current->right.get();
            }
        }

        return candidate;
    }

    bool erase(int key) {
        if (!eraseNode(root, key)) return false;

        --node_count;
        return true;
    }

    std::vector<int> inorder() const {
        std::vector<int> result;
        result.reserve(node_count);
        inorderTraversal(root.get(), result);
        return result;
    }

    std::vector<int> preorder() const {
        std::vector<int> result;
        result.reserve(node_count);
        preorderTraversal(root.get(), result);
        return result;
    }

    std::vector<int> postorder() const {
        std::vector<int> result;
        result.reserve(node_count);
        postorderTraversal(root.get(), result);
        return result;
    }

    std::vector<int> rangeSearch(int low, int high) const {
        if (low > high) {
            throw std::invalid_argument("Invalid search range.");
        }

        std::vector<int> result;
        collectRange(root.get(), low, high, result);
        return result;
    }

    int height() const {
        return calculateHeight(root.get());
    }

    std::size_t size() const {
        return node_count;
    }

    bool empty() const {
        return node_count == 0;
    }

    bool validate() const {
        return validateNode(root.get(), std::nullopt, std::nullopt);
    }

    void clear() {
        root.reset();
        node_count = 0;
    }
};

void runTests() {
    BinarySearchTree tree;

    for (int key : {50, 30, 70, 20, 40, 60, 80}) {
        assert(tree.insert(key));
    }

    assert(!tree.insert(50));
    assert(tree.size() == 7);
    assert(tree.validate());

    assert(tree.search(40));
    assert(!tree.search(99));

    assert(tree.minimum() == 20);
    assert(tree.maximum() == 80);

    assert(tree.predecessor(50) == 40);
    assert(tree.successor(50) == 60);
    assert(!tree.predecessor(10));
    assert(!tree.successor(100));

    assert(
        tree.inorder() ==
        std::vector<int>({20, 30, 40, 50, 60, 70, 80})
    );

    assert(tree.erase(20));  // Leaf.
    assert(tree.erase(30));  // One child.
    assert(tree.erase(70));  // Two children.
    assert(tree.erase(50));  // Root.

    assert(!tree.erase(999));
    assert(tree.validate());
    assert(tree.size() == 3);

    assert(
        tree.rangeSearch(40, 80) ==
        std::vector<int>({40, 60, 80})
    );

    bool caught = false;

    try {
        tree.rangeSearch(80, 40);
    } catch (const std::invalid_argument&) {
        caught = true;
    }

    assert(caught);

    tree.clear();
    assert(tree.empty());
    assert(!tree.minimum());
    assert(tree.height() == 0);

    std::cout << "All C++17 BST tests passed.\n";
}

void demonstrate() {
    BinarySearchTree tree;

    // A product catalogue indexed by unique product identifiers.
    const std::vector<int> productIds = {
        500, 300, 700, 200, 400, 600, 800
    };

    for (int id : productIds) {
        tree.insert(id);
    }

    std::cout << "\nPRODUCT CATALOGUE INDEX\n";

    std::cout << "Inorder: ";
    for (int id : tree.inorder()) {
        std::cout << id << " ";
    }

    std::cout << "\nPreorder: ";
    for (int id : tree.preorder()) {
        std::cout << id << " ";
    }

    std::cout << "\nPostorder: ";
    for (int id : tree.postorder()) {
        std::cout << id << " ";
    }

    std::cout << "\nSearch product 400: "
              << (tree.search(400) ? "Found" : "Not found");

    std::cout << "\nMinimum product ID: "
              << *tree.minimum();

    std::cout << "\nMaximum product ID: "
              << *tree.maximum();

    std::cout << "\nPredecessor of 500: "
              << *tree.predecessor(500);

    std::cout << "\nSuccessor of 500: "
              << *tree.successor(500);

    std::cout << "\nHeight: " << tree.height();

    tree.erase(500);

    std::cout << "\nAfter deleting product 500: ";

    for (int id : tree.inorder()) {
        std::cout << id << " ";
    }

    std::cout << "\nBST valid: "
              << (tree.validate() ? "Yes" : "No")
              << "\n";
}

int main() {
    try {
        runTests();
        demonstrate();
    } catch (const std::exception& error) {
        std::cerr << "Execution error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
