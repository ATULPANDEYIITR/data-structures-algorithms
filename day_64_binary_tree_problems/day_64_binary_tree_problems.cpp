#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <limits>
#include <memory>
#include <optional>
#include <queue>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

struct TreeNode {
    std::int64_t value;
    TreeNode* left = nullptr;
    TreeNode* right = nullptr;

    explicit TreeNode(std::int64_t v) : value(v) {}
};

struct TreeMetrics {
    int maxDepth = 0;
    int minDepth = 0;
    bool hasPathSum = false;
    int diameterEdges = 0;
    bool balanced = true;
    std::uint64_t nodeCount = 0;
};

class BinaryTree {
private:
    std::vector<std::unique_ptr<TreeNode>> storage_;
    TreeNode* root_ = nullptr;

    TreeNode* createNode(std::int64_t value) {
        storage_.push_back(std::make_unique<TreeNode>(value));
        return storage_.back().get();
    }

    static int leftmostHeight(const TreeNode* node) {
        int height = 0;

        while (node != nullptr) {
            ++height;
            node = node->left;
        }

        return height;
    }

    static std::int64_t checkedAdd(std::int64_t a, std::int64_t b) {
        if (b > 0 && a > std::numeric_limits<std::int64_t>::max() - b) {
            throw std::overflow_error("Root-to-leaf path sum overflow.");
        }

        if (b < 0 && a < std::numeric_limits<std::int64_t>::min() - b) {
            throw std::overflow_error("Root-to-leaf path sum underflow.");
        }

        return a + b;
    }

public:
    BinaryTree() = default;

    BinaryTree(const BinaryTree&) = delete;
    BinaryTree& operator=(const BinaryTree&) = delete;

    BinaryTree(BinaryTree&&) noexcept = default;
    BinaryTree& operator=(BinaryTree&&) noexcept = default;

    static BinaryTree fromLevelOrder(
        const std::vector<std::optional<std::int64_t>>& values
    ) {
        BinaryTree tree;

        if (values.empty()) {
            return tree;
        }

        if (!values[0].has_value()) {
            for (std::size_t i = 1; i < values.size(); ++i) {
                if (values[i].has_value()) {
                    throw std::invalid_argument(
                        "A non-empty tree must have a root."
                    );
                }
            }
            return tree;
        }

        tree.root_ = tree.createNode(*values[0]);

        std::queue<TreeNode*> parents;
        parents.push(tree.root_);

        std::size_t index = 1;

        while (!parents.empty() && index < values.size()) {
            TreeNode* parent = parents.front();
            parents.pop();

            if (index < values.size()) {
                if (values[index].has_value()) {
                    parent->left = tree.createNode(*values[index]);
                    parents.push(parent->left);
                }
                ++index;
            }

            if (index < values.size()) {
                if (values[index].has_value()) {
                    parent->right = tree.createNode(*values[index]);
                    parents.push(parent->right);
                }
                ++index;
            }
        }

        for (; index < values.size(); ++index) {
            if (values[index].has_value()) {
                throw std::invalid_argument(
                    "Level-order input contains unreachable nodes."
                );
            }
        }

        tree.validate();
        return tree;
    }

    const TreeNode* root() const {
        return root_;
    }

    std::size_t validate() const {
        if (root_ == nullptr) {
            if (!storage_.empty()) {
                throw std::logic_error("Unreachable nodes exist in the tree arena.");
            }
            return 0;
        }

        std::unordered_set<const TreeNode*> visited;
        std::vector<const TreeNode*> stack{root_};

        while (!stack.empty()) {
            const TreeNode* node = stack.back();
            stack.pop_back();

            if (node == nullptr) {
                continue;
            }

            if (!visited.insert(node).second) {
                throw std::invalid_argument(
                    "Cycle or shared child detected."
                );
            }

            if (node->right != nullptr) {
                stack.push_back(node->right);
            }
            if (node->left != nullptr) {
                stack.push_back(node->left);
            }
        }

        if (visited.size() != storage_.size()) {
            throw std::logic_error("The tree contains unreachable allocated nodes.");
        }

        return visited.size();
    }

    int maxDepth() const {
        validate();

        if (root_ == nullptr) {
            return 0;
        }

        std::queue<std::pair<const TreeNode*, int>> queue;
        queue.push({root_, 1});

        int maximum = 0;

        while (!queue.empty()) {
            const auto [node, depth] = queue.front();
            queue.pop();

            maximum = std::max(maximum, depth);

            if (node->left != nullptr) {
                queue.push({node->left, depth + 1});
            }
            if (node->right != nullptr) {
                queue.push({node->right, depth + 1});
            }
        }

        return maximum;
    }

    int minDepth() const {
        validate();

        if (root_ == nullptr) {
            return 0;
        }

        std::queue<std::pair<const TreeNode*, int>> queue;
        queue.push({root_, 1});

        while (!queue.empty()) {
            const auto [node, depth] = queue.front();
            queue.pop();

            if (node->left == nullptr && node->right == nullptr) {
                return depth;
            }

            if (node->left != nullptr) {
                queue.push({node->left, depth + 1});
            }
            if (node->right != nullptr) {
                queue.push({node->right, depth + 1});
            }
        }

        return 0;
    }

    bool hasPathSum(std::int64_t target) const {
        validate();

        if (root_ == nullptr) {
            return false;
        }

        std::vector<std::pair<const TreeNode*, std::int64_t>> stack;
        stack.push_back({root_, 0});

        while (!stack.empty()) {
            const auto [node, accumulated] = stack.back();
            stack.pop_back();

            const std::int64_t current = checkedAdd(
                accumulated,
                node->value
            );

            if (node->left == nullptr && node->right == nullptr) {
                if (current == target) {
                    return true;
                }
                continue;
            }

            if (node->right != nullptr) {
                stack.push_back({node->right, current});
            }
            if (node->left != nullptr) {
                stack.push_back({node->left, current});
            }
        }

        return false;
    }

    TreeMetrics analyze(std::int64_t target) const {
        validate();

        if (root_ == nullptr) {
            return {};
        }

        struct SubtreeStats {
            int height = 0;
            int minDepth = 0;
            int diameter = 0;
            bool balanced = true;
            std::uint64_t count = 0;
        };

        std::unordered_map<const TreeNode*, SubtreeStats> stats;
        std::vector<std::pair<const TreeNode*, bool>> stack;
        stack.push_back({root_, false});

        while (!stack.empty()) {
            const auto [node, expanded] = stack.back();
            stack.pop_back();

            if (!expanded) {
                stack.push_back({node, true});

                if (node->right != nullptr) {
                    stack.push_back({node->right, false});
                }
                if (node->left != nullptr) {
                    stack.push_back({node->left, false});
                }

                continue;
            }

            const SubtreeStats left =
                node->left != nullptr ? stats.at(node->left) : SubtreeStats{};

            const SubtreeStats right =
                node->right != nullptr ? stats.at(node->right) : SubtreeStats{};

            SubtreeStats current;

            current.height = 1 + std::max(left.height, right.height);

            if (node->left == nullptr && node->right == nullptr) {
                current.minDepth = 1;
            } else if (node->left == nullptr) {
                current.minDepth = 1 + right.minDepth;
            } else if (node->right == nullptr) {
                current.minDepth = 1 + left.minDepth;
            } else {
                current.minDepth = 1 + std::min(
                    left.minDepth,
                    right.minDepth
                );
            }

            current.diameter = std::max({
                left.height + right.height,
                left.diameter,
                right.diameter
            });

            current.balanced =
                left.balanced &&
                right.balanced &&
                std::abs(left.height - right.height) <= 1;

            current.count = 1 + left.count + right.count;
            stats[node] = current;
        }

        const SubtreeStats rootStats = stats.at(root_);

        TreeMetrics result;
        result.maxDepth = rootStats.height;
        result.minDepth = rootStats.minDepth;
        result.diameterEdges = rootStats.diameter;
        result.balanced = rootStats.balanced;
        result.nodeCount = rootStats.count;
        result.hasPathSum = hasPathSum(target);

        return result;
    }

    int diameter() const {
        return analyze(0).diameterEdges;
    }

    bool isBalanced() const {
        return analyze(0).balanced;
    }

    std::uint64_t countNodes() const {
        return static_cast<std::uint64_t>(validate());
    }

    bool isComplete() const {
        validate();

        if (root_ == nullptr) {
            return true;
        }

        std::queue<const TreeNode*> queue;
        queue.push(root_);

        bool missingChildSeen = false;

        while (!queue.empty()) {
            const TreeNode* node = queue.front();
            queue.pop();

            for (const TreeNode* child : {node->left, node->right}) {
                if (child == nullptr) {
                    missingChildSeen = true;
                } else {
                    if (missingChildSeen) {
                        return false;
                    }
                    queue.push(child);
                }
            }
        }

        return true;
    }

    std::uint64_t countCompleteNodes(bool verify = true) const {
        validate();

        if (root_ == nullptr) {
            return 0;
        }

        if (verify && !isComplete()) {
            throw std::invalid_argument(
                "Optimized counting requires a complete binary tree."
            );
        }

        std::uint64_t total = 0;
        const TreeNode* current = root_;

        while (current != nullptr) {
            const int leftHeight = leftmostHeight(current->left);
            const int rightHeight = leftmostHeight(current->right);

            if (leftHeight >= 64 || rightHeight >= 64) {
                throw std::overflow_error(
                    "Complete-tree node count exceeds uint64_t capacity."
                );
            }

            if (leftHeight == rightHeight) {
                total += (std::uint64_t{1} << leftHeight);
                current = current->right;
            } else {
                total += (std::uint64_t{1} << rightHeight);
                current = current->left;
            }
        }

        return total;
    }
};

void runTests() {
    const BinaryTree balanced = BinaryTree::fromLevelOrder({
        10, 5, 15, 3, 7, 12, 18
    });

    const TreeMetrics balancedMetrics = balanced.analyze(22);

    assert(balancedMetrics.maxDepth == 3);
    assert(balancedMetrics.minDepth == 3);
    assert(balancedMetrics.hasPathSum);
    assert(balancedMetrics.diameterEdges == 4);
    assert(balancedMetrics.balanced);
    assert(balancedMetrics.nodeCount == 7);
    assert(balanced.isComplete());
    assert(balanced.countCompleteNodes() == 7);

    const BinaryTree skewed = BinaryTree::fromLevelOrder({
        5, 4, std::nullopt, 3, std::nullopt, 2
    });

    const TreeMetrics skewedMetrics = skewed.analyze(14);

    assert(skewedMetrics.maxDepth == 4);
    assert(skewedMetrics.minDepth == 4);
    assert(skewedMetrics.diameterEdges == 3);
    assert(!skewedMetrics.balanced);
    assert(skewedMetrics.nodeCount == 4);
    assert(!skewed.isComplete());

    const BinaryTree singleBranch = BinaryTree::fromLevelOrder({
        1, 2
    });
    assert(singleBranch.minDepth() == 2);

    const BinaryTree negative = BinaryTree::fromLevelOrder({
        -2, -3, -4
    });
    assert(negative.hasPathSum(-5));

    const BinaryTree empty;
    assert(empty.maxDepth() == 0);
    assert(empty.minDepth() == 0);
    assert(empty.diameter() == 0);
    assert(empty.isBalanced());
    assert(empty.countNodes() == 0);
    assert(empty.countCompleteNodes() == 0);

    bool rejectedIncomplete = false;

    try {
        skewed.countCompleteNodes();
    } catch (const std::invalid_argument&) {
        rejectedIncomplete = true;
    }

    assert(rejectedIncomplete);

    bool rejectedMalformedInput = false;

    try {
        BinaryTree::fromLevelOrder({std::nullopt, 1});
    } catch (const std::invalid_argument&) {
        rejectedMalformedInput = true;
    }

    assert(rejectedMalformedInput);

    std::cout << "All C++17 binary tree tests passed.\n";
}

int main() {
    try {
        runTests();

        const BinaryTree tree = BinaryTree::fromLevelOrder({
            10, 5, 15, 3, 7, 12, 18
        });

        const TreeMetrics result = tree.analyze(22);

        std::cout << "\nBinary Tree Analysis\n";
        std::cout << "Maximum depth: " << result.maxDepth << '\n';
        std::cout << "Minimum depth: " << result.minDepth << '\n';
        std::cout << "Path sum 22 exists: "
                  << std::boolalpha << result.hasPathSum << '\n';
        std::cout << "Diameter in edges: " << result.diameterEdges << '\n';
        std::cout << "Balanced: " << result.balanced << '\n';
        std::cout << "Node count: " << result.nodeCount << '\n';
        std::cout << "Complete tree: " << tree.isComplete() << '\n';
        std::cout << "Complete-tree node count: "
                  << tree.countCompleteNodes() << '\n';

        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Execution failed: " << error.what() << '\n';
        return 1;
    }
}
