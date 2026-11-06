#include <algorithm>
#include <cassert>
#include <chrono>
#include <cstdint>
#include <exception>
#include <functional>
#include <iostream>
#include <limits>
#include <memory>
#include <optional>
#include <queue>
#include <random>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <utility>
#include <vector>

using namespace std;

class BSTException : public runtime_error {
public:
    explicit BSTException(const string& message)
        : runtime_error(message) {}
};

class DuplicateKeyException : public BSTException {
public:
    explicit DuplicateKeyException(int key)
        : BSTException("Duplicate key: " + to_string(key)) {}
};

class EmptyTreeException : public BSTException {
public:
    EmptyTreeException()
        : BSTException("Operation requires a non-empty tree.") {}
};

struct Node {
    int key;
    unique_ptr<Node> left;
    unique_ptr<Node> right;

    explicit Node(int value) : key(value) {}
};

enum class TraversalOrder {
    INORDER,
    PREORDER,
    POSTORDER,
    LEVEL_ORDER
};

class BinarySearchTree {
private:
    unique_ptr<Node> root;
    size_t nodeCount = 0;

    static unique_ptr<Node> buildBalanced(
        const vector<int>& values,
        int left,
        int right
    ) {
        if (left > right) return nullptr;

        int middle = left + (right - left) / 2;

        auto node = make_unique<Node>(values[middle]);

        node->left = buildBalanced(values, left, middle - 1);
        node->right = buildBalanced(values, middle + 1, right);

        return node;
    }

public:
    BinarySearchTree() = default;

    size_t size() const {
        return nodeCount;
    }

    bool empty() const {
        return root == nullptr;
    }

    void insert(int key) {
        unique_ptr<Node>* current = &root;

        while (*current) {
            if (key == (*current)->key) {
                throw DuplicateKeyException(key);
            }

            current = key < (*current)->key
                ? &((*current)->left)
                : &((*current)->right);
        }

        *current = make_unique<Node>(key);
        nodeCount++;
    }

    void insertMany(const vector<int>& values) {
        // Prevalidate duplicate keys before mutating the tree.
        set<int> batch;

        for (int key : values) {
            if (!batch.insert(key).second || search(key)) {
                throw DuplicateKeyException(key);
            }
        }

        for (int key : values) {
            insert(key);
        }
    }

    bool search(int key) const {
        const Node* current = root.get();

        while (current) {
            if (key == current->key) return true;

            current = key < current->key
                ? current->left.get()
                : current->right.get();
        }

        return false;
    }

    vector<int> inorder() const {
        vector<int> result;
        vector<const Node*> stack;
        const Node* current = root.get();

        while (current || !stack.empty()) {
            while (current) {
                stack.push_back(current);
                current = current->left.get();
            }

            current = stack.back();
            stack.pop_back();

            result.push_back(current->key);
            current = current->right.get();
        }

        return result;
    }

    vector<int> preorder() const {
        vector<int> result;

        if (!root) return result;

        vector<const Node*> stack = {root.get()};

        while (!stack.empty()) {
            const Node* node = stack.back();
            stack.pop_back();

            result.push_back(node->key);

            if (node->right) stack.push_back(node->right.get());
            if (node->left) stack.push_back(node->left.get());
        }

        return result;
    }

    vector<int> postorder() const {
        vector<int> result;

        if (!root) return result;

        vector<pair<const Node*, bool>> stack = {
            {root.get(), false}
        };

        while (!stack.empty()) {
            auto [node, visited] = stack.back();
            stack.pop_back();

            if (visited) {
                result.push_back(node->key);
            } else {
                stack.push_back({node, true});

                if (node->right) {
                    stack.push_back({node->right.get(), false});
                }

                if (node->left) {
                    stack.push_back({node->left.get(), false});
                }
            }
        }

        return result;
    }

    vector<int> levelOrder() const {
        vector<int> result;

        if (!root) return result;

        queue<const Node*> pending;
        pending.push(root.get());

        while (!pending.empty()) {
            const Node* node = pending.front();
            pending.pop();

            result.push_back(node->key);

            if (node->left) pending.push(node->left.get());
            if (node->right) pending.push(node->right.get());
        }

        return result;
    }

    int minimum() const {
        if (!root) throw EmptyTreeException();

        const Node* current = root.get();

        while (current->left) {
            current = current->left.get();
        }

        return current->key;
    }

    int maximum() const {
        if (!root) throw EmptyTreeException();

        const Node* current = root.get();

        while (current->right) {
            current = current->right.get();
        }

        return current->key;
    }

    optional<int> floor(int key) const {
        const Node* current = root.get();
        optional<int> candidate;

        while (current) {
            if (current->key == key) return key;

            if (current->key < key) {
                candidate = current->key;
                current = current->right.get();
            } else {
                current = current->left.get();
            }
        }

        return candidate;
    }

    optional<int> ceiling(int key) const {
        const Node* current = root.get();
        optional<int> candidate;

        while (current) {
            if (current->key == key) return key;

            if (current->key > key) {
                candidate = current->key;
                current = current->left.get();
            } else {
                current = current->right.get();
            }
        }

        return candidate;
    }

    vector<int> rangeQuery(int low, int high) const {
        if (low > high) {
            throw invalid_argument("Invalid range boundaries.");
        }

        vector<int> result;
        vector<const Node*> stack;
        const Node* current = root.get();

        while (current || !stack.empty()) {
            while (current) {
                if (current->key >= low) {
                    stack.push_back(current);
                    current = current->left.get();
                } else {
                    current = current->right.get();
                }
            }

            if (stack.empty()) break;

            current = stack.back();
            stack.pop_back();

            if (current->key > high) break;

            result.push_back(current->key);
            current = current->right.get();
        }

        return result;
    }

    optional<int> successor(int key) const {
        const Node* current = root.get();
        optional<int> candidate;

        while (current) {
            if (current->key > key) {
                candidate = current->key;
                current = current->left.get();
            } else {
                current = current->right.get();
            }
        }

        return candidate;
    }

    optional<int> predecessor(int key) const {
        const Node* current = root.get();
        optional<int> candidate;

        while (current) {
            if (current->key < key) {
                candidate = current->key;
                current = current->right.get();
            } else {
                current = current->left.get();
            }
        }

        return candidate;
    }

    bool erase(int key) {
        function<bool(unique_ptr<Node>&)> remove =
            [&](unique_ptr<Node>& node) -> bool {
                if (!node) return false;

                if (key < node->key) {
                    return remove(node->left);
                }

                if (key > node->key) {
                    return remove(node->right);
                }

                if (!node->left) {
                    node = move(node->right);
                } else if (!node->right) {
                    node = move(node->left);
                } else {
                    Node* successor = node->right.get();

                    while (successor->left) {
                        successor = successor->left.get();
                    }

                    node->key = successor->key;
                    remove(node->right);
                }

                return true;
            };

        bool deleted = remove(root);

        if (deleted) nodeCount--;

        return deleted;
    }

    bool validate() const {
        struct State {
            const Node* node;
            optional<int> lower;
            optional<int> upper;
        };

        unordered_set<const Node*> visited;
        vector<State> stack = {{root.get(), nullopt, nullopt}};
        size_t count = 0;

        while (!stack.empty()) {
            State state = stack.back();
            stack.pop_back();

            const Node* node = state.node;

            if (!node) continue;

            if (!visited.insert(node).second) return false;

            count++;

            if (state.lower && node->key <= *state.lower) {
                return false;
            }

            if (state.upper && node->key >= *state.upper) {
                return false;
            }

            stack.push_back({
                node->right.get(),
                node->key,
                state.upper
            });

            stack.push_back({
                node->left.get(),
                state.lower,
                node->key
            });
        }

        return count == nodeCount;
    }

    int height() const {
        if (!root) return 0;

        queue<pair<const Node*, int>> pending;
        pending.push({root.get(), 1});

        int maximumDepth = 0;

        while (!pending.empty()) {
            auto [node, depth] = pending.front();
            pending.pop();

            maximumDepth = max(maximumDepth, depth);

            if (node->left) {
                pending.push({node->left.get(), depth + 1});
            }

            if (node->right) {
                pending.push({node->right.get(), depth + 1});
            }
        }

        return maximumDepth;
    }

    static BinarySearchTree fromSorted(
        const vector<int>& values
    ) {
        if (!is_sorted(values.begin(), values.end()) ||
            adjacent_find(values.begin(), values.end()) != values.end()) {
            throw invalid_argument(
                "Input must be strictly increasing."
            );
        }

        BinarySearchTree tree;

        tree.root = buildBalanced(
            values,
            0,
            static_cast<int>(values.size()) - 1
        );

        tree.nodeCount = values.size();

        return tree;
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

template <typename T>
void printOptional(const string& label, const optional<T>& value) {
    cout << label << ": ";

    if (value) cout << *value;
    else cout << "Not found";

    cout << '\n';
}

void runTests() {
    BinarySearchTree tree;
    tree.insertMany({50, 30, 70, 20, 40, 60, 80});

    assert(tree.validate());
    assert(tree.minimum() == 20);
    assert(tree.maximum() == 80);
    assert(tree.floor(45) == optional<int>(40));
    assert(tree.ceiling(45) == optional<int>(50));
    assert(tree.rangeQuery(30, 70) ==
           vector<int>({30, 40, 50, 60, 70}));

    assert(tree.successor(50) == optional<int>(60));
    assert(tree.predecessor(50) == optional<int>(40));

    assert(tree.erase(20));
    assert(tree.erase(30));
    assert(tree.erase(50));
    assert(tree.validate());

    assert(!tree.erase(999));

    BinarySearchTree balanced =
        BinarySearchTree::fromSorted(
            {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15}
        );

    assert(balanced.height() == 4);
    assert(balanced.validate());

    BinarySearchTree empty;
    assert(empty.validate());
    assert(empty.inorder().empty());

    try {
        empty.minimum();
        assert(false);
    } catch (const EmptyTreeException&) {
    }

    try {
        tree.insert(40);
        assert(false);
    } catch (const DuplicateKeyException&) {
    }

    try {
        BinarySearchTree::fromSorted({1, 3, 2});
        assert(false);
    } catch (const invalid_argument&) {
    }

    cout << "All C++17 tests passed.\n";
}

int main() {
    try {
        BinarySearchTree inventory;

        // Unique numeric asset identifiers are indexed in BST order.
        inventory.insertMany({
            5000, 3000, 7000, 2000, 4000, 6000, 8000
        });

        cout << "Enterprise Asset Index: BST\n";
        cout << "================================\n";

        printVector("Inorder", inventory.inorder());
        printVector("Preorder", inventory.preorder());
        printVector("Postorder", inventory.postorder());
        printVector("Level order", inventory.levelOrder());

        cout << "\nBoundary queries\n";

        cout << "Minimum asset ID: "
             << inventory.minimum() << '\n';

        cout << "Maximum asset ID: "
             << inventory.maximum() << '\n';

        printOptional("Floor of 4500", inventory.floor(4500));
        printOptional("Ceiling of 4500", inventory.ceiling(4500));

        printOptional(
            "Successor of 5000",
            inventory.successor(5000)
        );

        printOptional(
            "Predecessor of 5000",
            inventory.predecessor(5000)
        );

        printVector(
            "Assets in range 3000-7000",
            inventory.rangeQuery(3000, 7000)
        );

        cout << "\nGovernance checks\n";
        cout << "Tree valid: "
             << boolalpha << inventory.validate() << '\n';

        cout << "Tree height: " << inventory.height() << '\n';

        cout << "\nRemoving asset 5000\n";

        inventory.erase(5000);

        printVector("Updated asset index", inventory.inorder());

        cout << "Updated tree valid: "
             << inventory.validate() << '\n';

        runTests();

        cout << "\nAll operations completed successfully.\n";

    } catch (const exception& error) {
        cerr << "Execution failed: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
