#include <algorithm>
#include <cassert>
#include <cmath>
#include <iostream>
#include <memory>
#include <optional>
#include <queue>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

class BSTException : public runtime_error {
public:
    explicit BSTException(const string& message)
        : runtime_error(message) {}
};

struct Node {
    int key;
    unique_ptr<Node> left;
    unique_ptr<Node> right;

    explicit Node(int value) : key(value) {}
};

struct ListNode {
    int key;
    ListNode* prev = nullptr;
    ListNode* next = nullptr;

    explicit ListNode(int value) : key(value) {}
};

struct DoublyLinkedList {
    ListNode* head = nullptr;
    ListNode* tail = nullptr;
    size_t size = 0;

    DoublyLinkedList() = default;

    DoublyLinkedList(const DoublyLinkedList&) = delete;
    DoublyLinkedList& operator=(const DoublyLinkedList&) = delete;

    DoublyLinkedList(DoublyLinkedList&& other) noexcept {
        head = other.head;
        tail = other.tail;
        size = other.size;

        other.head = nullptr;
        other.tail = nullptr;
        other.size = 0;
    }

    DoublyLinkedList& operator=(DoublyLinkedList&& other) noexcept {
        if (this != &other) {
            clear();

            head = other.head;
            tail = other.tail;
            size = other.size;

            other.head = nullptr;
            other.tail = nullptr;
            other.size = 0;
        }

        return *this;
    }

    ~DoublyLinkedList() {
        clear();
    }

    void append(int value) {
        auto* node = new ListNode(value);

        if (!head) {
            head = node;
            tail = node;
        } else {
            tail->next = node;
            node->prev = tail;
            tail = node;
        }

        ++size;
    }

    void clear() {
        ListNode* current = head;

        while (current) {
            ListNode* next = current->next;
            delete current;
            current = next;
        }

        head = nullptr;
        tail = nullptr;
        size = 0;
    }

    vector<int> values() const {
        vector<int> result;

        for (auto* current = head; current; current = current->next) {
            result.push_back(current->key);
        }

        return result;
    }
};

class BinarySearchTree {
private:
    unique_ptr<Node> root;
    size_t nodeCount = 0;

    static unique_ptr<Node> buildBalanced(
        const vector<int>& values,
        int start,
        int end
    ) {
        if (start > end) {
            return nullptr;
        }

        int middle = start + (end - start) / 2;

        auto node = make_unique<Node>(values[middle]);

        node->left = buildBalanced(values, start, middle - 1);
        node->right = buildBalanced(values, middle + 1, end);

        return node;
    }

    static int checkHeight(const Node* node) {
        if (!node) return 0;

        int left = checkHeight(node->left.get());
        if (left == -1) return -1;

        int right = checkHeight(node->right.get());
        if (right == -1) return -1;

        if (abs(left - right) > 1) return -1;

        return 1 + max(left, right);
    }

    static size_t validateNode(
        const Node* node,
        optional<int> lower,
        optional<int> upper
    ) {
        if (!node) return 0;

        if (lower && node->key <= *lower) {
            throw BSTException("Lower-bound invariant violated.");
        }

        if (upper && node->key >= *upper) {
            throw BSTException("Upper-bound invariant violated.");
        }

        return 1
            + validateNode(node->left.get(), lower, node->key)
            + validateNode(node->right.get(), node->key, upper);
    }

    static void collectInorder(
        const Node* node,
        vector<int>& output
    ) {
        if (!node) return;

        collectInorder(node->left.get(), output);
        output.push_back(node->key);
        collectInorder(node->right.get(), output);
    }

    static void collectPreorder(
        const Node* node,
        vector<int>& output
    ) {
        if (!node) return;

        output.push_back(node->key);
        collectPreorder(node->left.get(), output);
        collectPreorder(node->right.get(), output);
    }

    static void collectPostorder(
        const Node* node,
        vector<int>& output
    ) {
        if (!node) return;

        collectPostorder(node->left.get(), output);
        collectPostorder(node->right.get(), output);
        output.push_back(node->key);
    }

    static void collectRange(
        const Node* node,
        int low,
        int high,
        vector<int>& output
    ) {
        if (!node) return;

        if (node->key > low) {
            collectRange(node->left.get(), low, high, output);
        }

        if (node->key >= low && node->key <= high) {
            output.push_back(node->key);
        }

        if (node->key < high) {
            collectRange(node->right.get(), low, high, output);
        }
    }

    static void convertToList(
        const Node* node,
        DoublyLinkedList& list
    ) {
        if (!node) return;

        convertToList(node->left.get(), list);
        list.append(node->key);
        convertToList(node->right.get(), list);
    }

public:
    BinarySearchTree() = default;

    explicit BinarySearchTree(const vector<int>& values) {
        for (int value : values) {
            insert(value);
        }
    }

    size_t size() const {
        return nodeCount;
    }

    bool empty() const {
        return root == nullptr;
    }

    bool insert(int key) {
        if (!root) {
            root = make_unique<Node>(key);
            ++nodeCount;
            return true;
        }

        Node* current = root.get();

        while (true) {
            if (key == current->key) {
                return false;
            }

            if (key < current->key) {
                if (!current->left) {
                    current->left = make_unique<Node>(key);
                    ++nodeCount;
                    return true;
                }

                current = current->left.get();
            } else {
                if (!current->right) {
                    current->right = make_unique<Node>(key);
                    ++nodeCount;
                    return true;
                }

                current = current->right.get();
            }
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

    bool erase(int key) {
        bool deleted = false;

        auto remove = [&](auto&& self,
                          unique_ptr<Node>& node,
                          int target) -> void {
            if (!node) return;

            if (target < node->key) {
                self(self, node->left, target);
            } else if (target > node->key) {
                self(self, node->right, target);
            } else {
                deleted = true;

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

                    self(self, node->right, successor->key);
                }
            }
        };

        remove(remove, root, key);

        if (deleted) --nodeCount;

        return deleted;
    }

    vector<int> inorder() const {
        vector<int> result;
        result.reserve(nodeCount);
        collectInorder(root.get(), result);
        return result;
    }

    vector<int> preorder() const {
        vector<int> result;
        result.reserve(nodeCount);
        collectPreorder(root.get(), result);
        return result;
    }

    vector<int> postorder() const {
        vector<int> result;
        result.reserve(nodeCount);
        collectPostorder(root.get(), result);
        return result;
    }

    int kthSmallest(int k) const {
        if (k < 1 || static_cast<size_t>(k) > nodeCount) {
            throw BSTException("Invalid kth-smallest position.");
        }

        vector<const Node*> stack;
        const Node* current = root.get();
        int visited = 0;

        while (current || !stack.empty()) {
            while (current) {
                stack.push_back(current);
                current = current->left.get();
            }

            current = stack.back();
            stack.pop_back();

            if (++visited == k) {
                return current->key;
            }

            current = current->right.get();
        }

        throw BSTException("Unexpected traversal failure.");
    }

    int kthLargest(int k) const {
        if (k < 1 || static_cast<size_t>(k) > nodeCount) {
            throw BSTException("Invalid kth-largest position.");
        }

        vector<const Node*> stack;
        const Node* current = root.get();
        int visited = 0;

        while (current || !stack.empty()) {
            while (current) {
                stack.push_back(current);
                current = current->right.get();
            }

            current = stack.back();
            stack.pop_back();

            if (++visited == k) {
                return current->key;
            }

            current = current->left.get();
        }

        throw BSTException("Unexpected traversal failure.");
    }

    int lowestCommonAncestor(int first, int second) const {
        if (!search(first) || !search(second)) {
            throw BSTException("Both keys must exist in the tree.");
        }

        const Node* current = root.get();

        while (current) {
            if (first < current->key && second < current->key) {
                current = current->left.get();
            } else if (first > current->key && second > current->key) {
                current = current->right.get();
            } else {
                return current->key;
            }
        }

        throw BSTException("LCA could not be determined.");
    }

    int minimum() const {
        if (!root) throw BSTException("Empty tree.");

        const Node* current = root.get();

        while (current->left) {
            current = current->left.get();
        }

        return current->key;
    }

    int maximum() const {
        if (!root) throw BSTException("Empty tree.");

        const Node* current = root.get();

        while (current->right) {
            current = current->right.get();
        }

        return current->key;
    }

    int height() const {
        if (!root) return 0;

        queue<pair<const Node*, int>> pending;
        pending.push({root.get(), 1});

        int result = 0;

        while (!pending.empty()) {
            auto [node, depth] = pending.front();
            pending.pop();

            result = max(result, depth);

            if (node->left) {
                pending.push({node->left.get(), depth + 1});
            }

            if (node->right) {
                pending.push({node->right.get(), depth + 1});
            }
        }

        return result;
    }

    bool isBalanced() const {
        return checkHeight(root.get()) != -1;
    }

    bool validate() const {
        size_t actual = validateNode(root.get(), nullopt, nullopt);

        if (actual != nodeCount) {
            throw BSTException("Node count invariant violated.");
        }

        return true;
    }

    vector<int> rangeSearch(int low, int high) const {
        if (low > high) {
            throw BSTException("Invalid range boundaries.");
        }

        vector<int> result;
        collectRange(root.get(), low, high, result);
        return result;
    }

    static BinarySearchTree fromSorted(const vector<int>& values) {
        for (size_t i = 1; i < values.size(); ++i) {
            if (values[i - 1] >= values[i]) {
                throw BSTException(
                    "Input must be strictly increasing."
                );
            }
        }

        BinarySearchTree tree;

        if (!values.empty()) {
            tree.root = buildBalanced(
                values,
                0,
                static_cast<int>(values.size()) - 1
            );
        }

        tree.nodeCount = values.size();
        return tree;
    }

    void rebalance() {
        vector<int> sorted = inorder();

        auto rebuilt = fromSorted(sorted);

        root = move(rebuilt.root);
        nodeCount = rebuilt.nodeCount;
    }

    DoublyLinkedList toDoublyLinkedList() const {
        DoublyLinkedList result;
        convertToList(root.get(), result);
        return result;
    }

    static BinarySearchTree fromPreorder(
        const vector<int>& values
    ) {
        vector<int> sorted = values;

        sort(sorted.begin(), sorted.end());

        if (adjacent_find(sorted.begin(), sorted.end()) != sorted.end()) {
            throw BSTException("Duplicate preorder keys.");
        }

        BinarySearchTree tree;
        size_t index = 0;

        auto build = [&](auto&& self,
                         optional<int> lower,
                         optional<int> upper) -> unique_ptr<Node> {
            if (index >= values.size()) return nullptr;

            int value = values[index];

            if ((lower && value <= *lower) ||
                (upper && value >= *upper)) {
                return nullptr;
            }

            ++index;

            auto node = make_unique<Node>(value);
            node->left = self(self, lower, value);
            node->right = self(self, value, upper);

            return node;
        };

        tree.root = build(build, nullopt, nullopt);

        if (index != values.size()) {
            throw BSTException("Invalid BST preorder sequence.");
        }

        tree.nodeCount = values.size();
        return tree;
    }

    void printStatistics() const {
        cout << "Size: " << nodeCount << '\n';
        cout << "Height: " << height() << '\n';
        cout << "Balanced: " << boolalpha << isBalanced() << '\n';
        cout << "Valid: " << validate() << '\n';

        if (root) {
            cout << "Minimum: " << minimum() << '\n';
            cout << "Maximum: " << maximum() << '\n';
        }
    }
};

// Domain scenario: indexed inventory records with unique numeric IDs.
class InventoryIndex {
private:
    BinarySearchTree index;

public:
    void registerAsset(int assetId) {
        if (assetId <= 0) {
            throw BSTException("Asset ID must be positive.");
        }

        if (!index.insert(assetId)) {
            throw BSTException("Asset ID already registered.");
        }
    }

    void removeAsset(int assetId) {
        if (!index.erase(assetId)) {
            throw BSTException("Asset does not exist.");
        }
    }

    bool contains(int assetId) const {
        return index.search(assetId);
    }

    int assetAtRank(int rank) const {
        return index.kthSmallest(rank);
    }

    int commonAssetGroup(int first, int second) const {
        return index.lowestCommonAncestor(first, second);
    }

    void optimizeIndex() {
        index.rebalance();
    }

    void report() const {
        index.printStatistics();
        cout << "Asset IDs: ";

        for (int id : index.inorder()) {
            cout << id << ' ';
        }

        cout << '\n';
    }
};

void runTests() {
    BinarySearchTree tree({50, 30, 70, 20, 40, 60, 80});

    assert(tree.validate());
    assert(tree.size() == 7);
    assert((tree.inorder() ==
        vector<int>{20, 30, 40, 50, 60, 70, 80}));

    assert(tree.kthSmallest(3) == 40);
    assert(tree.kthLargest(2) == 70);
    assert(tree.lowestCommonAncestor(20, 40) == 30);
    assert(tree.lowestCommonAncestor(20, 80) == 50);

    assert(tree.insert(90));
    assert(!tree.insert(50));
    assert(tree.erase(70));
    assert(!tree.search(70));
    assert(tree.validate());

    auto linked = tree.toDoublyLinkedList();
    assert(linked.values() == tree.inorder());

    auto balanced = BinarySearchTree::fromSorted(
        vector<int>{10, 20, 30, 40, 50, 60, 70}
    );

    assert(balanced.isBalanced());
    assert(balanced.kthSmallest(4) == 40);

    auto reconstructed = BinarySearchTree::fromPreorder(
        vector<int>{50, 30, 20, 40, 70, 60, 80}
    );

    assert((reconstructed.inorder() ==
        vector<int>{20, 30, 40, 50, 60, 70, 80}));

    BinarySearchTree skewed;

    for (int i = 1; i <= 100; ++i) {
        skewed.insert(i);
    }

    assert(!skewed.isBalanced());
    assert(skewed.height() == 100);

    skewed.rebalance();

    assert(skewed.isBalanced());
    assert(skewed.height() <= 7);
    assert(skewed.validate());

    BinarySearchTree empty;
    assert(empty.empty());
    assert(empty.height() == 0);

    try {
        tree.kthSmallest(0);
        assert(false);
    } catch (const BSTException&) {
    }

    try {
        BinarySearchTree::fromSorted({1, 2, 2, 3});
        assert(false);
    } catch (const BSTException&) {
    }

    try {
        BinarySearchTree::fromPreorder({10, 5, 12, 4});
        assert(false);
    } catch (const BSTException&) {
    }

    cout << "All C++17 BST tests passed.\n";
}

int main() {
    try {
        runTests();

        cout << "\nADVANCED BST DEMONSTRATION\n";

        BinarySearchTree tree({
            50, 30, 70, 20, 40, 60, 80
        });

        cout << "\nInorder: ";
        for (int value : tree.inorder()) {
            cout << value << ' ';
        }

        cout << "\nPreorder: ";
        for (int value : tree.preorder()) {
            cout << value << ' ';
        }

        cout << "\nPostorder: ";
        for (int value : tree.postorder()) {
            cout << value << ' ';
        }

        cout << "\n3rd smallest: " << tree.kthSmallest(3);
        cout << "\n2nd largest: " << tree.kthLargest(2);
        cout << "\nLCA of 20 and 40: "
             << tree.lowestCommonAncestor(20, 40);

        cout << "\nRange 30-70: ";
        for (int value : tree.rangeSearch(30, 70)) {
            cout << value << ' ';
        }

        cout << "\n\nTree statistics:\n";
        tree.printStatistics();

        auto linked = tree.toDoublyLinkedList();

        cout << "\nDoubly linked list: ";
        for (int value : linked.values()) {
            cout << value << ' ';
        }

        cout << "\n\nInventory index demonstration:\n";

        InventoryIndex inventory;

        for (int id : {1040, 1020, 1060, 1010, 1030, 1050}) {
            inventory.registerAsset(id);
        }

        inventory.report();

        cout << "Third smallest asset ID: "
             << inventory.assetAtRank(3) << '\n';

        inventory.optimizeIndex();

        cout << "\nAfter index optimization:\n";
        inventory.report();

    } catch (const exception& error) {
        cerr << "Execution failed: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
