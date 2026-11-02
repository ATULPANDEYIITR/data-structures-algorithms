#include <algorithm>
#include <cmath>
#include <exception>
#include <fstream>
#include <functional>
#include <iomanip>
#include <iostream>
#include <memory>
#include <optional>
#include <queue>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <utility>
#include <vector>

struct TreeNode {
    int value;
    std::unique_ptr<TreeNode> left;
    std::unique_ptr<TreeNode> right;

    explicit TreeNode(int value) : value(value) {}
};

enum class NodeKind {
    Leaf,
    Internal
};

struct TreeProfile {
    std::size_t nodes{};
    std::size_t leaves{};
    std::size_t internal_nodes{};
    int height_edges{-1};
    int height_nodes{};
    int diameter_edges{};
    bool balanced{};
    bool full{};
    bool complete{};
    bool perfect{};
    std::optional<bool> leaf_internal_identity;
};

class BinaryTree {
private:
    std::unique_ptr<TreeNode> root_;

    static int heightAndDiameter(
        const TreeNode* node,
        int& diameter
    ) {
        if (!node) {
            return -1;
        }

        const int left_height = heightAndDiameter(node->left.get(), diameter);
        const int right_height = heightAndDiameter(node->right.get(), diameter);

        const int through_node = left_height + right_height + 2;
        diameter = std::max(diameter, through_node);

        return 1 + std::max(left_height, right_height);
    }

    static int balancedHeight(const TreeNode* node) {
        if (!node) {
            return 0;
        }

        const int left = balancedHeight(node->left.get());
        if (left == -1) {
            return -1;
        }

        const int right = balancedHeight(node->right.get());
        if (right == -1) {
            return -1;
        }

        if (std::abs(left - right) > 1) {
            return -1;
        }

        return 1 + std::max(left, right);
    }

public:
    explicit BinaryTree(std::unique_ptr<TreeNode> root = nullptr)
        : root_(std::move(root)) {}

    TreeNode* root() const {
        return root_.get();
    }

    static BinaryTree fromLevelOrder(
        const std::vector<std::optional<int>>& values
    ) {
        if (values.empty() || !values[0].has_value()) {
            return BinaryTree{};
        }

        auto root = std::make_unique<TreeNode>(*values[0]);
        std::queue<TreeNode*> queue;
        queue.push(root.get());

        std::size_t index = 1;

        while (!queue.empty() && index < values.size()) {
            TreeNode* current = queue.front();
            queue.pop();

            if (index < values.size() && values[index].has_value()) {
                current->left =
                    std::make_unique<TreeNode>(*values[index]);
                queue.push(current->left.get());
            }
            ++index;

            if (index < values.size() && values[index].has_value()) {
                current->right =
                    std::make_unique<TreeNode>(*values[index]);
                queue.push(current->right.get());
            }
            ++index;
        }

        if (index < values.size()) {
            throw std::invalid_argument(
                "Level-order input contains unreachable nodes"
            );
        }

        return BinaryTree(std::move(root));
    }

    std::size_t countNodes() const {
        if (!root_) {
            return 0;
        }

        std::size_t count = 0;
        std::vector<const TreeNode*> stack{root_.get()};

        while (!stack.empty()) {
            const TreeNode* node = stack.back();
            stack.pop_back();
            ++count;

            if (node->left) stack.push_back(node->left.get());
            if (node->right) stack.push_back(node->right.get());
        }

        return count;
    }

    std::size_t countLeaves() const {
        if (!root_) {
            return 0;
        }

        std::size_t count = 0;
        std::vector<const TreeNode*> stack{root_.get()};

        while (!stack.empty()) {
            const TreeNode* node = stack.back();
            stack.pop_back();

            if (!node->left && !node->right) {
                ++count;
                continue;
            }

            if (node->left) stack.push_back(node->left.get());
            if (node->right) stack.push_back(node->right.get());
        }

        return count;
    }

    int heightEdges() const {
        std::function<int(const TreeNode*)> height =
            [&](const TreeNode* node) -> int {
                if (!node) return -1;
                return 1 + std::max(
                    height(node->left.get()),
                    height(node->right.get())
                );
            };

        return height(root_.get());
    }

    int diameterEdges() const {
        if (!root_) return 0;

        int diameter = 0;
        heightAndDiameter(root_.get(), diameter);
        return diameter;
    }

    bool isBalanced() const {
        return balancedHeight(root_.get()) != -1;
    }

    bool isFull() const {
        if (!root_) return true;

        std::vector<const TreeNode*> stack{root_.get()};

        while (!stack.empty()) {
            const TreeNode* node = stack.back();
            stack.pop_back();

            const int children =
                static_cast<int>(node->left != nullptr) +
                static_cast<int>(node->right != nullptr);

            if (children == 1) {
                return false;
            }

            if (node->left) stack.push_back(node->left.get());
            if (node->right) stack.push_back(node->right.get());
        }

        return true;
    }

    bool isComplete() const {
        if (!root_) return true;

        std::queue<const TreeNode*> queue;
        queue.push(root_.get());
        bool missing_child = false;

        while (!queue.empty()) {
            const TreeNode* node = queue.front();
            queue.pop();

            if (node->left) {
                if (missing_child) return false;
                queue.push(node->left.get());
            } else {
                missing_child = true;
            }

            if (node->right) {
                if (missing_child) return false;
                queue.push(node->right.get());
            } else {
                missing_child = true;
            }
        }

        return true;
    }

    bool isPerfect() const {
        if (!root_) return true;

        std::optional<int> expected_depth;
        std::vector<std::pair<const TreeNode*, int>> stack;
        stack.push_back({root_.get(), 0});

        while (!stack.empty()) {
            auto [node, depth] = stack.back();
            stack.pop_back();

            const bool left = node->left != nullptr;
            const bool right = node->right != nullptr;

            if (!left && !right) {
                if (!expected_depth.has_value()) {
                    expected_depth = depth;
                } else if (*expected_depth != depth) {
                    return false;
                }
                continue;
            }

            if (!left || !right) {
                return false;
            }

            stack.push_back({node->left.get(), depth + 1});
            stack.push_back({node->right.get(), depth + 1});
        }

        return true;
    }

    TreeProfile profile() const {
        const auto nodes = countNodes();
        const auto leaves = countLeaves();
        const auto internal = nodes - leaves;
        const int height = heightEdges();
        const bool full = isFull();

        return TreeProfile{
            nodes,
            leaves,
            internal,
            height,
            nodes == 0 ? 0 : height + 1,
            diameterEdges(),
            isBalanced(),
            full,
            isComplete(),
            isPerfect(),
            nodes > 0 && full
                ? std::optional<bool>(leaves == internal + 1)
                : std::nullopt
        };
    }
};

enum class MergeDecision {
    Approved,
    Rejected
};

class GovernanceEngine {
private:
    int max_height_;
    bool require_balanced_;
    bool require_complete_;

public:
    GovernanceEngine(
        int max_height,
        bool require_balanced,
        bool require_complete
    )
        : max_height_(max_height),
          require_balanced_(require_balanced),
          require_complete_(require_complete) {
        if (max_height < 0) {
            throw std::invalid_argument("Maximum height cannot be negative");
        }
    }

    MergeDecision evaluate(const TreeProfile& profile) const {
        if (profile.height_edges > max_height_) {
            return MergeDecision::Rejected;
        }

        if (require_balanced_ && !profile.balanced) {
            return MergeDecision::Rejected;
        }

        if (require_complete_ && !profile.complete) {
            return MergeDecision::Rejected;
        }

        return MergeDecision::Approved;
    }
};

void printProfile(const TreeProfile& p) {
    std::cout << "{\n"
              << "  \"nodes\": " << p.nodes << ",\n"
              << "  \"leaves\": " << p.leaves << ",\n"
              << "  \"internal_nodes\": " << p.internal_nodes << ",\n"
              << "  \"height_edges\": " << p.height_edges << ",\n"
              << "  \"height_nodes\": " << p.height_nodes << ",\n"
              << "  \"diameter_edges\": " << p.diameter_edges << ",\n"
              << "  \"balanced\": " << std::boolalpha << p.balanced << ",\n"
              << "  \"full\": " << p.full << ",\n"
              << "  \"complete\": " << p.complete << ",\n"
              << "  \"perfect\": " << p.perfect << "\n"
              << "}\n";
}

void runTests() {
    const auto balanced = BinaryTree::fromLevelOrder(
        {10, 5, 15, 2, 7, 12, 20}
    );

    const auto p = balanced.profile();

    if (p.nodes != 7 ||
        p.leaves != 4 ||
        p.internal_nodes != 3 ||
        p.height_edges != 2 ||
        p.diameter_edges != 4 ||
        !p.balanced ||
        !p.full ||
        !p.complete ||
        !p.perfect) {
        throw std::runtime_error("Balanced-tree tests failed");
    }

    const auto chain = BinaryTree::fromLevelOrder(
        {1, 2, std::nullopt, 3, std::nullopt, 4}
    );

    const auto cp = chain.profile();

    if (cp.height_edges != 3 ||
        cp.diameter_edges != 3 ||
        cp.balanced ||
        cp.full) {
        throw std::runtime_error("Chain tests failed");
    }

    const auto single = BinaryTree::fromLevelOrder({42});
    const auto sp = single.profile();

    if (sp.nodes != 1 ||
        sp.leaves != 1 ||
        sp.internal_nodes != 0 ||
        sp.height_edges != 0 ||
        !sp.balanced) {
        throw std::runtime_error("Single-node tests failed");
    }

    const auto empty = BinaryTree::fromLevelOrder({});
    const auto ep = empty.profile();

    if (ep.nodes != 0 ||
        ep.height_edges != -1 ||
        ep.diameter_edges != 0 ||
        !ep.balanced) {
        throw std::runtime_error("Empty-tree tests failed");
    }
}

int main() {
    try {
        runTests();

        const auto tree = BinaryTree::fromLevelOrder(
            {50, 25, 75, 12, 37, 62, 87}
        );

        const TreeProfile profile = tree.profile();

        GovernanceEngine policy(
            4,
            true,
            true
        );

        const MergeDecision decision = policy.evaluate(profile);

        std::cout << "Binary Tree Governance Case Study\n";
        std::cout << "=================================\n";
        printProfile(profile);

        std::cout << "Governance decision: "
                  << (decision == MergeDecision::Approved
                          ? "APPROVED"
                          : "REJECTED")
                  << "\n";

        // The output file is intentionally fixed to the current directory.
        // This avoids accepting an arbitrary path from untrusted input.
        std::ofstream output("binary_tree_profile.txt");
        if (!output) {
            throw std::runtime_error("Cannot create profile output file");
        }

        output << "nodes=" << profile.nodes << '\n'
               << "leaves=" << profile.leaves << '\n'
               << "internal_nodes=" << profile.internal_nodes << '\n'
               << "height_edges=" << profile.height_edges << '\n'
               << "height_nodes=" << profile.height_nodes << '\n'
               << "diameter_edges=" << profile.diameter_edges << '\n'
               << "balanced=" << std::boolalpha << profile.balanced << '\n'
               << "full=" << profile.full << '\n'
               << "complete=" << profile.complete << '\n'
               << "perfect=" << profile.perfect << '\n';

        if (!output) {
            throw std::runtime_error("Failed while writing profile");
        }

        std::cout << "Validation: all tests passed.\n";
        std::cout << "Profile written to binary_tree_profile.txt\n";
        return 0;
    } catch (const std::exception& ex) {
        std::cerr << "Execution failed: " << ex.what() << '\n';
        return 1;
    }
}
