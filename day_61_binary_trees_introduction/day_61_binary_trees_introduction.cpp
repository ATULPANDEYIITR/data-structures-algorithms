#include <algorithm>
#include <cassert>
#include <iostream>
#include <memory>
#include <optional>
#include <queue>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <vector>

struct TreeNode {
    int value;
    std::unique_ptr<TreeNode> left;
    std::unique_ptr<TreeNode> right;

    explicit TreeNode(int value) : value(value) {}
};

enum class MergeState {
    Valid,
    Empty
};

class BinaryTree {
private:
    std::unique_ptr<TreeNode> root_;

    static int heightImpl(const TreeNode* node) {
        if (node == nullptr) {
            return -1;
        }

        return 1 + std::max(
            heightImpl(node->left.get()),
            heightImpl(node->right.get())
        );
    }

    static void preorderImpl(const TreeNode* node, std::vector<int>& result) {
        if (node == nullptr) {
            return;
        }

        result.push_back(node->value);
        preorderImpl(node->left.get(), result);
        preorderImpl(node->right.get(), result);
    }

    const TreeNode* findNode(int target) const {
        if (root_ == nullptr) {
            return nullptr;
        }

        std::queue<const TreeNode*> queue;
        queue.push(root_.get());

        while (!queue.empty()) {
            const TreeNode* node = queue.front();
            queue.pop();

            if (node->value == target) {
                return node;
            }

            if (node->left) {
                queue.push(node->left.get());
            }

            if (node->right) {
                queue.push(node->right.get());
            }
        }

        return nullptr;
    }

public:
    BinaryTree() = default;

    explicit BinaryTree(std::unique_ptr<TreeNode> root)
        : root_(std::move(root)) {}

    const TreeNode* root() const {
        return root_.get();
    }

    int height() const {
        return heightImpl(root_.get());
    }

    std::optional<int> depthOf(int target) const {
        if (!root_) {
            return std::nullopt;
        }

        std::queue<std::pair<const TreeNode*, int>> queue;
        queue.push({root_.get(), 0});

        while (!queue.empty()) {
            auto [node, depth] = queue.front();
            queue.pop();

            if (node->value == target) {
                return depth;
            }

            if (node->left) {
                queue.push({node->left.get(), depth + 1});
            }

            if (node->right) {
                queue.push({node->right.get(), depth + 1});
            }
        }

        return std::nullopt;
    }

    std::optional<int> parentOf(int target) const {
        if (!root_ || root_->value == target) {
            return std::nullopt;
        }

        std::queue<const TreeNode*> queue;
        queue.push(root_.get());

        while (!queue.empty()) {
            const TreeNode* node = queue.front();
            queue.pop();

            if (node->left && node->left->value == target) {
                return node->value;
            }

            if (node->right && node->right->value == target) {
                return node->value;
            }

            if (node->left) {
                queue.push(node->left.get());
            }

            if (node->right) {
                queue.push(node->right.get());
            }
        }

        return std::nullopt;
    }

    std::optional<std::vector<int>> childrenOf(int target) const {
        const TreeNode* node = findNode(target);

        if (!node) {
            return std::nullopt;
        }

        std::vector<int> children;

        if (node->left) {
            children.push_back(node->left->value);
        }

        if (node->right) {
            children.push_back(node->right->value);
        }

        return children;
    }

    int degreeOf(int target) const {
        const TreeNode* node = findNode(target);

        if (!node) {
            return -1;
        }

        return static_cast<int>(node->left != nullptr)
             + static_cast<int>(node->right != nullptr);
    }

    std::vector<int> preorder() const {
        std::vector<int> result;
        preorderImpl(root_.get(), result);
        return result;
    }

    std::vector<int> levelOrder() const {
        std::vector<int> result;

        if (!root_) {
            return result;
        }

        std::queue<const TreeNode*> queue;
        queue.push(root_.get());

        while (!queue.empty()) {
            const TreeNode* node = queue.front();
            queue.pop();

            result.push_back(node->value);

            if (node->left) {
                queue.push(node->left.get());
            }

            if (node->right) {
                queue.push(node->right.get());
            }
        }

        return result;
    }

    void validateAcyclic() const {
        std::unordered_set<const TreeNode*> visited;

        std::queue<const TreeNode*> queue;
        if (root_) {
            queue.push(root_.get());
        }

        while (!queue.empty()) {
            const TreeNode* node = queue.front();
            queue.pop();

            if (!visited.insert(node).second) {
                throw std::logic_error("Cycle or shared node detected.");
            }

            if (node->left) {
                queue.push(node->left.get());
            }

            if (node->right) {
                queue.push(node->right.get());
            }
        }
    }
};

std::unique_ptr<TreeNode> makeSampleTree() {
    auto root = std::make_unique<TreeNode>(40);

    root->left = std::make_unique<TreeNode>(20);
    root->right = std::make_unique<TreeNode>(60);

    root->left->left = std::make_unique<TreeNode>(10);
    root->left->right = std::make_unique<TreeNode>(30);

    root->right->left = std::make_unique<TreeNode>(50);
    root->right->right = std::make_unique<TreeNode>(70);

    root->right->right->left = std::make_unique<TreeNode>(65);

    return root;
}

void printOptional(const std::optional<int>& value) {
    if (value) {
        std::cout << *value;
    } else {
        std::cout << "none";
    }
}

int main() {
    try {
        BinaryTree tree(makeSampleTree());

        tree.validateAcyclic();

        std::cout << "Binary Tree Case Study\n";
        std::cout << "======================\n";
        std::cout << "Root: " << tree.root()->value << '\n';
        std::cout << "Height: " << tree.height() << '\n';

        std::cout << "Preorder: ";
        for (int value : tree.preorder()) {
            std::cout << value << ' ';
        }
        std::cout << '\n';

        std::cout << "Level-order: ";
        for (int value : tree.levelOrder()) {
            std::cout << value << ' ';
        }
        std::cout << "\n\n";

        const int target = 65;

        std::cout << "Node: " << target << '\n';

        std::cout << "Parent: ";
        printOptional(tree.parentOf(target));
        std::cout << '\n';

        std::cout << "Depth: ";
        printOptional(tree.depthOf(target));
        std::cout << '\n';

        std::cout << "Level: ";
        auto depth = tree.depthOf(target);
        if (depth) {
            std::cout << *depth + 1;
        } else {
            std::cout << "none";
        }
        std::cout << '\n';

        std::cout << "Degree: " << tree.degreeOf(target) << '\n';

        auto children = tree.childrenOf(target);
        std::cout << "Children: ";

        if (children) {
            for (int child : *children) {
                std::cout << child << ' ';
            }
        }

        std::cout << "\n\n";

        assert(tree.height() == 3);
        assert(tree.depthOf(65).value() == 3);
        assert(tree.parentOf(65).value() == 70);
        assert(tree.degreeOf(65) == 0);
        assert(!tree.depthOf(999).has_value());
        assert(tree.degreeOf(999) == -1);

        BinaryTree empty;
        assert(empty.height() == -1);
        assert(empty.levelOrder().empty());

        std::cout << "All validation checks passed.\n";
        std::cout << "Complexity: traversal O(n), node lookup O(n), height O(n).\n";
    }
    catch (const std::exception& error) {
        std::cerr << "Failure: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
