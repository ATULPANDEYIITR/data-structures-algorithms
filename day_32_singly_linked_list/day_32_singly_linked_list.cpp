#include <algorithm>
#include <iostream>
#include <memory>
#include <optional>
#include <stdexcept>
#include <string>
#include <vector>

class RepositoryChangeList {
private:
    struct Node {
        int changeId;
        std::string description;
        std::string author;
        std::unique_ptr<Node> next;

        Node(int id, std::string text, std::string owner)
            : changeId(id),
              description(std::move(text)),
              author(std::move(owner)),
              next(nullptr) {}
    };

    std::unique_ptr<Node> head_;
    std::size_t size_ = 0;

public:
    RepositoryChangeList() = default;

    RepositoryChangeList(const RepositoryChangeList&) = delete;
    RepositoryChangeList& operator=(const RepositoryChangeList&) = delete;

    bool empty() const {
        return head_ == nullptr;
    }

    std::size_t size() const {
        return size_;
    }

    void prepend(int id, const std::string& description,
                 const std::string& author) {
        auto node = std::make_unique<Node>(id, description, author);
        node->next = std::move(head_);
        head_ = std::move(node);
        ++size_;
    }

    void append(int id, const std::string& description,
                const std::string& author) {
        auto node = std::make_unique<Node>(id, description, author);

        if (!head_) {
            head_ = std::move(node);
            ++size_;
            return;
        }

        Node* current = head_.get();

        while (current->next) {
            current = current->next.get();
        }

        current->next = std::move(node);
        ++size_;
    }

    bool insertAfterChange(
        int targetId,
        int newId,
        const std::string& description,
        const std::string& author) {

        Node* current = head_.get();

        while (current) {
            if (current->changeId == targetId) {
                auto node =
                    std::make_unique<Node>(newId, description, author);

                node->next = std::move(current->next);
                current->next = std::move(node);

                ++size_;
                return true;
            }

            current = current->next.get();
        }

        return false;
    }

    std::optional<std::size_t> searchById(int id) const {
        const Node* current = head_.get();
        std::size_t index = 0;

        while (current) {
            if (current->changeId == id) {
                return index;
            }

            current = current->next.get();
            ++index;
        }

        return std::nullopt;
    }

    bool updateDescription(
        int id,
        const std::string& newDescription) {

        Node* current = head_.get();

        while (current) {
            if (current->changeId == id) {
                current->description = newDescription;
                return true;
            }

            current = current->next.get();
        }

        return false;
    }

    bool deleteById(int id) {
        if (!head_) {
            return false;
        }

        if (head_->changeId == id) {
            head_ = std::move(head_->next);
            --size_;
            return true;
        }

        Node* previous = head_.get();

        while (previous->next) {
            if (previous->next->changeId == id) {
                /*
                 * Moving the unique_ptr out of previous->next transfers
                 * ownership of the node. Replacing previous->next with
                 * the removed node's next link deletes the removed node
                 * automatically when the local unique_ptr is destroyed.
                 */
                auto removed = std::move(previous->next);
                previous->next = std::move(removed->next);
                --size_;
                return true;
            }

            previous = previous->next.get();
        }

        return false;
    }

    void reverse() {
        /*
         * unique_ptr requires ownership to move along with the links.
         * previous owns the already-reversed prefix, while current owns
         * the remaining suffix.
         */
        std::unique_ptr<Node> previous = nullptr;
        std::unique_ptr<Node> current = std::move(head_);

        while (current) {
            std::unique_ptr<Node> next = std::move(current->next);

            current->next = std::move(previous);
            previous = std::move(current);
            current = std::move(next);
        }

        head_ = std::move(previous);
    }

    std::optional<int> valueAt(std::size_t index) const {
        const Node* current = head_.get();

        for (std::size_t position = 0; position < index && current;
             ++position) {
            current = current->next.get();
        }

        if (!current) {
            return std::nullopt;
        }

        return current->changeId;
    }

    bool validate() const {
        /*
         * Floyd's algorithm uses two raw observer pointers. They do not
         * own nodes, so ownership remains entirely controlled by unique_ptr.
         */
        const Node* slow = head_.get();
        const Node* fast = head_.get();

        while (fast && fast->next) {
            slow = slow->next.get();
            fast = fast->next->next.get();

            if (slow == fast) {
                return false;
            }
        }

        std::size_t counted = 0;
        const Node* current = head_.get();

        while (current) {
            ++counted;
            current = current->next.get();
        }

        return counted == size_;
    }

    void print() const {
        const Node* current = head_.get();

        if (!current) {
            std::cout << "[empty]\n";
            return;
        }

        while (current) {
            std::cout
                << "[change " << current->changeId
                << ", author=" << current->author
                << ", description=\"" << current->description << "\"]";

            if (current->next) {
                std::cout << " -> ";
            }

            current = current->next.get();
        }

        std::cout << '\n';
    }
};


void demonstrateRepositoryChangeHistory() {
    std::cout << "\n=== Repository change history ===\n";

    RepositoryChangeList history;

    /*
     * A commit/change history is naturally sequential for this case study:
     * each record points to the next record that follows it in the modeled
     * history. The list is not being presented as a replacement for Git's
     * actual commit graph; it is a focused data-structure model.
     */
    history.append(
        101,
        "Add validation for contributor metadata",
        "Asha");

    history.append(
        102,
        "Reject malformed change identifiers",
        "Ravi");

    history.append(
        103,
        "Add audit logging",
        "Mina");

    history.append(
        104,
        "Document deployment checks",
        "Atul");

    history.print();

    std::cout << "Records: " << history.size() << '\n';

    const auto position = history.searchById(103);

    if (position) {
        std::cout
            << "Change 103 found at position "
            << *position << '\n';
    }

    history.updateDescription(
        103,
        "Add structured audit logging");

    std::cout << "After updating change 103:\n";
    history.print();

    history.insertAfterChange(
        102,
        150,
        "Add regression test for malformed identifiers",
        "Mina");

    std::cout << "After inserting a regression change after 102:\n";
    history.print();

    history.deleteById(101);

    std::cout << "After deleting the first change:\n";
    history.print();

    history.reverse();

    std::cout << "After reversing the modeled sequence:\n";
    history.print();

    std::cout
        << "Structural validation: "
        << (history.validate() ? "valid" : "invalid")
        << '\n';
}


void demonstrateOwnershipAndMemorySafety() {
    std::cout << "\n=== Ownership and memory safety ===\n";

    RepositoryChangeList history;

    history.prepend(3, "Third event", "Mina");
    history.prepend(2, "Second event", "Ravi");
    history.prepend(1, "First event", "Asha");

    history.print();

    /*
     * Nodes are owned through unique_ptr. When a node is removed, ownership
     * is transferred to a temporary unique_ptr and its successor becomes the
     * predecessor's owned link. No manual delete is required.
     */
    history.deleteById(2);

    std::cout << "After deleting the middle node:\n";
    history.print();

    std::cout
        << "List valid after ownership transfer: "
        << std::boolalpha
        << history.validate()
        << '\n';
}


void demonstrateEdgeCases() {
    std::cout << "\n=== Edge cases ===\n";

    RepositoryChangeList history;

    std::cout
        << "Empty search: "
        << std::boolalpha
        << history.searchById(10).has_value()
        << '\n';

    std::cout
        << "Delete from empty list: "
        << history.deleteById(10)
        << '\n';

    history.append(500, "Only record", "Reviewer");

    std::cout << "Single-node list:\n";
    history.print();

    history.reverse();

    std::cout << "Single-node list after reverse:\n";
    history.print();

    history.deleteById(500);

    std::cout << "After deleting only node:\n";
    history.print();

    std::cout
        << "Index lookup beyond list: "
        << history.valueAt(5).has_value()
        << '\n';
}


void demonstrateComplexity() {
    std::cout << "\n=== Complexity ===\n";
    std::cout << "Prepend: O(1)\n";
    std::cout << "Append without tail pointer: O(n)\n";
    std::cout << "Search by identifier: O(n)\n";
    std::cout << "Update by identifier: O(n)\n";
    std::cout << "Delete by identifier: O(n)\n";
    std::cout << "Insert after located node: O(1) after traversal\n";
    std::cout << "Reverse: O(n) time, O(1) auxiliary link storage\n";
    std::cout << "Indexed access: O(n)\n";
    std::cout << "Storage: O(n)\n";

    std::cout
        << "\nA linked list avoids shifting elements during local insertion "
        << "or deletion, but it pays for this flexibility with sequential "
        << "access and per-node pointer/ownership overhead.\n";
}


void runTests() {
    std::cout << "\n=== Verification tests ===\n";

    RepositoryChangeList list;

    list.append(10, "Ten", "A");
    list.append(20, "Twenty", "B");
    list.append(30, "Thirty", "C");

    if (list.size() != 3 || !list.validate()) {
        throw std::runtime_error("Construction test failed");
    }

    list.prepend(5, "Five", "D");

    if (list.valueAt(0) != 5) {
        throw std::runtime_error("Prepend test failed");
    }

    if (!list.insertAfterChange(
            20,
            25,
            "Twenty-five",
            "E")) {
        throw std::runtime_error("Insertion test failed");
    }

    if (list.searchById(25) != std::optional<std::size_t>(3)) {
        throw std::runtime_error("Search test failed");
    }

    if (!list.updateDescription(25, "Updated twenty-five")) {
        throw std::runtime_error("Update test failed");
    }

    if (!list.deleteById(5)) {
        throw std::runtime_error("Head deletion test failed");
    }

    list.reverse();

    const std::vector<int> expected{30, 25, 20, 10};

    for (std::size_t i = 0; i < expected.size(); ++i) {
        if (list.valueAt(i) != std::optional<int>(expected[i])) {
            throw std::runtime_error("Reverse test failed");
        }
    }

    if (!list.validate()) {
        throw std::runtime_error("Integrity test failed");
    }

    std::cout << "All C++ tests passed.\n";
}


int main() {
    try {
        std::cout << "SINGLY LINKED LIST: C++ TECHNICAL CASE STUDY\n";

        demonstrateRepositoryChangeHistory();
        demonstrateOwnershipAndMemorySafety();
        demonstrateEdgeCases();
        demonstrateComplexity();
        runTests();

        std::cout << "\nProgram completed successfully.\n";
        return 0;
    }
    catch (const std::exception& error) {
        std::cerr
            << "Fatal error: "
            << error.what()
            << '\n';

        return 1;
    }
}
