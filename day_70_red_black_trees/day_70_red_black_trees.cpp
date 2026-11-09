#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstddef>
#include <iostream>
#include <limits>
#include <memory>
#include <optional>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

/*
 * Red-Black Tree: Ordered Inventory Index
 *
 * C++17 implementation featuring:
 * - Unique integer keys
 * - Parent-linked nodes
 * - Sentinel-based boundary handling
 * - Insertion and deletion
 * - Rotations and balancing
 * - Ordered and range queries
 * - Invariant validation
 * - Randomized verification
 */

enum class Color {
    RED,
    BLACK
};

class RedBlackTree {
private:

    struct Node {
        int key;
        Color color;
        Node* left;
        Node* right;
        Node* parent;

        Node(int value, Color c)
            : key(value),
              color(c),
              left(nullptr),
              right(nullptr),
              parent(nullptr) {}
    };

    Node* nil;
    Node* root;
    std::size_t nodeCount;

    void leftRotate(Node* x) {
        Node* y = x->right;

        if (y == nil) {
            throw std::logic_error("Invalid left rotation");
        }

        x->right = y->left;

        if (y->left != nil) {
            y->left->parent = x;
        }

        y->parent = x->parent;

        if (x->parent == nil) {
            root = y;
        } else if (x == x->parent->left) {
            x->parent->left = y;
        } else {
            x->parent->right = y;
        }

        y->left = x;
        x->parent = y;
    }

    void rightRotate(Node* y) {
        Node* x = y->left;

        if (x == nil) {
            throw std::logic_error("Invalid right rotation");
        }

        y->left = x->right;

        if (x->right != nil) {
            x->right->parent = y;
        }

        x->parent = y->parent;

        if (y->parent == nil) {
            root = x;
        } else if (y == y->parent->right) {
            y->parent->right = x;
        } else {
            y->parent->left = x;
        }

        x->right = y;
        y->parent = x;
    }

    void insertFixup(Node* z) {
        while (z->parent->color == Color::RED) {

            if (z->parent == z->parent->parent->left) {
                Node* uncle = z->parent->parent->right;

                if (uncle->color == Color::RED) {
                    z->parent->color = Color::BLACK;
                    uncle->color = Color::BLACK;
                    z->parent->parent->color = Color::RED;
                    z = z->parent->parent;
                } else {
                    if (z == z->parent->right) {
                        z = z->parent;
                        leftRotate(z);
                    }

                    z->parent->color = Color::BLACK;
                    z->parent->parent->color = Color::RED;
                    rightRotate(z->parent->parent);
                }
            } else {
                Node* uncle = z->parent->parent->left;

                if (uncle->color == Color::RED) {
                    z->parent->color = Color::BLACK;
                    uncle->color = Color::BLACK;
                    z->parent->parent->color = Color::RED;
                    z = z->parent->parent;
                } else {
                    if (z == z->parent->left) {
                        z = z->parent;
                        rightRotate(z);
                    }

                    z->parent->color = Color::BLACK;
                    z->parent->parent->color = Color::RED;
                    leftRotate(z->parent->parent);
                }
            }
        }

        root->color = Color::BLACK;
        root->parent = nil;
    }

    Node* findNode(int key) const {
        Node* current = root;

        while (current != nil) {
            if (key == current->key) {
                return current;
            }

            current = key < current->key
                ? current->left
                : current->right;
        }

        return nil;
    }

    Node* minimumNode(Node* node) const {
        while (node->left != nil) {
            node = node->left;
        }

        return node;
    }

    void transplant(Node* u, Node* v) {
        if (u->parent == nil) {
            root = v;
        } else if (u == u->parent->left) {
            u->parent->left = v;
        } else {
            u->parent->right = v;
        }

        v->parent = u->parent;
    }

    void deleteFixup(Node* x) {
        while (x != root && x->color == Color::BLACK) {

            if (x == x->parent->left) {
                Node* sibling = x->parent->right;

                if (sibling->color == Color::RED) {
                    sibling->color = Color::BLACK;
                    x->parent->color = Color::RED;
                    leftRotate(x->parent);
                    sibling = x->parent->right;
                }

                if (
                    sibling->left->color == Color::BLACK &&
                    sibling->right->color == Color::BLACK
                ) {
                    sibling->color = Color::RED;
                    x = x->parent;
                } else {
                    if (sibling->right->color == Color::BLACK) {
                        sibling->left->color = Color::BLACK;
                        sibling->color = Color::RED;
                        rightRotate(sibling);
                        sibling = x->parent->right;
                    }

                    sibling->color = x->parent->color;
                    x->parent->color = Color::BLACK;
                    sibling->right->color = Color::BLACK;
                    leftRotate(x->parent);
                    x = root;
                }
            } else {
                Node* sibling = x->parent->left;

                if (sibling->color == Color::RED) {
                    sibling->color = Color::BLACK;
                    x->parent->color = Color::RED;
                    rightRotate(x->parent);
                    sibling = x->parent->left;
                }

                if (
                    sibling->right->color == Color::BLACK &&
                    sibling->left->color == Color::BLACK
                ) {
                    sibling->color = Color::RED;
                    x = x->parent;
                } else {
                    if (sibling->left->color == Color::BLACK) {
                        sibling->right->color = Color::BLACK;
                        sibling->color = Color::RED;
                        leftRotate(sibling);
                        sibling = x->parent->left;
                    }

                    sibling->color = x->parent->color;
                    x->parent->color = Color::BLACK;
                    sibling->left->color = Color::BLACK;
                    rightRotate(x->parent);
                    x = root;
                }
            }
        }

        x->color = Color::BLACK;
    }

    void inorder(Node* node, std::vector<int>& result) const {
        if (node == nil) {
            return;
        }

        inorder(node->left, result);
        result.push_back(node->key);
        inorder(node->right, result);
    }

    void collectRange(
        Node* node,
        int low,
        int high,
        std::vector<int>& result
    ) const {
        if (node == nil) {
            return;
        }

        if (node->key > low) {
            collectRange(node->left, low, high, result);
        }

        if (node->key >= low && node->key <= high) {
            result.push_back(node->key);
        }

        if (node->key < high) {
            collectRange(node->right, low, high, result);
        }
    }

    int validateNode(
        Node* node,
        std::optional<int> lower,
        std::optional<int> upper,
        Node* expectedParent,
        std::size_t& count
    ) const {
        if (node == nil) {
            return 1;
        }

        ++count;

        if (node->parent != expectedParent) {
            throw std::logic_error("Parent pointer violation");
        }

        if (lower && node->key <= *lower) {
            throw std::logic_error("BST lower-bound violation");
        }

        if (upper && node->key >= *upper) {
            throw std::logic_error("BST upper-bound violation");
        }

        if (node->color == Color::RED) {
            if (
                node->left->color == Color::RED ||
                node->right->color == Color::RED
            ) {
                throw std::logic_error("Adjacent red nodes");
            }
        }

        int leftHeight = validateNode(
            node->left, lower, node->key, node, count
        );

        int rightHeight = validateNode(
            node->right, node->key, upper, node, count
        );

        if (leftHeight != rightHeight) {
            throw std::logic_error("Black-height violation");
        }

        return leftHeight +
            (node->color == Color::BLACK ? 1 : 0);
    }

    int calculateHeight(Node* node) const {
        if (node == nil) {
            return 0;
        }

        return 1 + std::max(
            calculateHeight(node->left),
            calculateHeight(node->right)
        );
    }

    void destroy(Node* node) {
        if (node == nil) {
            return;
        }

        destroy(node->left);
        destroy(node->right);
        delete node;
    }

public:

    RedBlackTree() : nodeCount(0) {
        nil = new Node(0, Color::BLACK);

        nil->left = nil;
        nil->right = nil;
        nil->parent = nil;

        root = nil;
    }

    ~RedBlackTree() {
        clear();
        delete nil;
    }

    RedBlackTree(const RedBlackTree&) = delete;
    RedBlackTree& operator=(const RedBlackTree&) = delete;

    void clear() {
        destroy(root);
        root = nil;
        nil->parent = nil;
        nodeCount = 0;
    }

    std::size_t size() const {
        return nodeCount;
    }

    bool empty() const {
        return nodeCount == 0;
    }

    bool contains(int key) const {
        return findNode(key) != nil;
    }

    bool insert(int key) {
        Node* parent = nil;
        Node* current = root;

        while (current != nil) {
            parent = current;

            if (key == current->key) {
                return false;
            }

            current = key < current->key
                ? current->left
                : current->right;
        }

        Node* node = new Node(key, Color::RED);

        node->left = nil;
        node->right = nil;
        node->parent = parent;

        if (parent == nil) {
            root = node;
        } else if (key < parent->key) {
            parent->left = node;
        } else {
            parent->right = node;
        }

        ++nodeCount;
        insertFixup(node);

        return true;
    }

    bool erase(int key) {
        Node* z = findNode(key);

        if (z == nil) {
            return false;
        }

        Node* y = z;
        Node* x;
        Color originalColor = y->color;

        if (z->left == nil) {
            x = z->right;
            transplant(z, z->right);
        } else if (z->right == nil) {
            x = z->left;
            transplant(z, z->left);
        } else {
            y = minimumNode(z->right);
            originalColor = y->color;
            x = y->right;

            if (y->parent == z) {
                x->parent = y;
            } else {
                transplant(y, y->right);
                y->right = z->right;
                y->right->parent = y;
            }

            transplant(z, y);
            y->left = z->left;
            y->left->parent = y;
            y->color = z->color;
        }

        delete z;
        --nodeCount;

        if (originalColor == Color::BLACK) {
            deleteFixup(x);
        }

        nil->color = Color::BLACK;

        if (root != nil) {
            root->parent = nil;
        }

        return true;
    }

    std::optional<int> search(int key) const {
        Node* node = findNode(key);

        if (node == nil) {
            return std::nullopt;
        }

        return node->key;
    }

    std::optional<int> minimum() const {
        if (root == nil) {
            return std::nullopt;
        }

        return minimumNode(root)->key;
    }

    std::optional<int> maximum() const {
        if (root == nil) {
            return std::nullopt;
        }

        Node* current = root;

        while (current->right != nil) {
            current = current->right;
        }

        return current->key;
    }

    std::vector<int> inorder() const {
        std::vector<int> result;
        result.reserve(nodeCount);
        inorder(root, result);
        return result;
    }

    std::vector<int> rangeQuery(int low, int high) const {
        if (low > high) {
            throw std::invalid_argument("Invalid range boundaries");
        }

        std::vector<int> result;
        collectRange(root, low, high, result);
        return result;
    }

    int height() const {
        return calculateHeight(root);
    }

    void validate() const {
        if (nil->color != Color::BLACK) {
            throw std::logic_error("Sentinel must be black");
        }

        if (root == nil) {
            if (nodeCount != 0) {
                throw std::logic_error("Invalid empty-tree size");
            }
            return;
        }

        if (root->color != Color::BLACK) {
            throw std::logic_error("Root must be black");
        }

        if (root->parent != nil) {
            throw std::logic_error("Invalid root parent");
        }

        std::size_t count = 0;

        validateNode(root, std::nullopt, std::nullopt, nil, count);

        if (count != nodeCount) {
            throw std::logic_error("Node count mismatch");
        }
    }

    void print() const {
        const auto values = inorder();

        std::cout << "[ ";

        for (int value : values) {
            std::cout << value << ' ';
        }

        std::cout << "]\n";
    }
};

void runDemonstration() {
    RedBlackTree tree;

    const std::vector<int> inventoryIds = {
        50, 30, 70, 20, 40, 60, 80,
        10, 25, 35, 45, 55, 65, 75, 90
    };

    std::cout << "RED-BLACK TREE INSERTION\n";

    for (int id : inventoryIds) {
        tree.insert(id);
        tree.validate();
        std::cout << "Inserted " << id << ": ";
        tree.print();
    }

    std::cout << "\nORDERED INVENTORY INDEX\n";
    tree.print();

    std::cout << "Size: " << tree.size() << '\n';
    std::cout << "Height: " << tree.height() << '\n';

    std::cout << "Minimum: " << *tree.minimum() << '\n';
    std::cout << "Maximum: " << *tree.maximum() << '\n';

    std::cout << "Search 45: "
              << (tree.contains(45) ? "Found" : "Not found")
              << '\n';

    std::cout << "Search 999: "
              << (tree.contains(999) ? "Found" : "Not found")
              << '\n';

    std::cout << "Range 30-65: ";

    for (int id : tree.rangeQuery(30, 65)) {
        std::cout << id << ' ';
    }

    std::cout << "\n\nDELETION\n";

    for (int id : {10, 20, 50, 70, 999}) {
        bool removed = tree.erase(id);

        std::cout << "Delete " << id << ": "
                  << (removed ? "Success" : "Not found")
                  << '\n';

        tree.validate();
        tree.print();
    }

    std::cout << "\nRANDOMIZED VERIFICATION\n";

    RedBlackTree randomized;
    std::vector<int> reference;

    std::mt19937 generator(42);
    std::uniform_int_distribution<int> distribution(-500, 500);
    std::bernoulli_distribution insertion(0.58);

    for (int i = 0; i < 5000; ++i) {
        int value = distribution(generator);

        if (insertion(generator)) {
            bool expected = std::find(
                reference.begin(), reference.end(), value
            ) == reference.end();

            bool actual = randomized.insert(value);
            assert(actual == expected);

            if (expected) {
                reference.push_back(value);
            }
        } else {
            bool expected = std::find(
                reference.begin(), reference.end(), value
            ) != reference.end();

            bool actual = randomized.erase(value);
            assert(actual == expected);

            if (expected) {
                reference.erase(
                    std::remove(
                        reference.begin(),
                        reference.end(),
                        value
                    ),
                    reference.end()
                );
            }
        }

        randomized.validate();

        std::sort(reference.begin(), reference.end());

        assert(randomized.inorder() == reference);
        assert(randomized.size() == reference.size());
    }

    std::cout << "Randomized verification passed.\n";
    std::cout << "Final size: " << randomized.size() << '\n';
    std::cout << "Final height: " << randomized.height() << '\n';
}

int main() {
    try {
        runDemonstration();
    } catch (const std::exception& error) {
        std::cerr << "Execution error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
