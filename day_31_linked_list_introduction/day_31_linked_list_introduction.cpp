/*
 * Linked List Introduction
 *
 * C++17 case study:
 * A repository work-item queue uses a singly linked list to model pending
 * operations. The implementation deliberately exposes memory ownership,
 * pointer manipulation, validation, exception handling, and complexity.
 *
 * Compile:
 *   g++ -std=c++17 -Wall -Wextra -pedantic linked_list_introduction.cpp -o linked_list
 */

#include <algorithm>
#include <cstddef>
#include <exception>
#include <iostream>
#include <memory>
#include <optional>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

struct WorkItem {
    int id;
    std::string title;
    std::string owner;
    int priority;
};

class WorkQueue {
private:
    /*
     * Each node owns the next node through unique_ptr. This makes ownership
     * explicit: deleting a node automatically releases the remainder of its
     * owned chain. Raw pointers are still useful as non-owning traversal
     * references, but ownership stays with unique_ptr.
     */
    struct Node {
        WorkItem item;
        std::unique_ptr<Node> next;

        explicit Node(WorkItem work)
            : item(std::move(work)), next(nullptr) {}
    };

    std::unique_ptr<Node> head_;
    Node* tail_ = nullptr;
    std::size_t size_ = 0;

public:
    WorkQueue() = default;

    WorkQueue(const WorkQueue&) = delete;
    WorkQueue& operator=(const WorkQueue&) = delete;

    WorkQueue(WorkQueue&&) noexcept = default;
    WorkQueue& operator=(WorkQueue&&) noexcept = default;

    ~WorkQueue() = default;

    bool empty() const noexcept {
        return size_ == 0;
    }

    std::size_t size() const noexcept {
        return size_;
    }

    void enqueue(WorkItem item) {
        auto node = std::make_unique<Node>(std::move(item));

        if (!head_) {
            tail_ = node.get();
            head_ = std::move(node);
        } else {
            tail_->next = std::move(node);
            tail_ = tail_->next.get();
        }

        ++size_;
    }

    WorkItem dequeue() {
        if (!head_) {
            throw std::underflow_error(
                "cannot dequeue from an empty work queue"
            );
        }

        WorkItem result = std::move(head_->item);
        head_ = std::move(head_->next);

        --size_;

        if (!head_) {
            tail_ = nullptr;
        }

        return result;
    }

    const WorkItem* findById(int id) const noexcept {
        const Node* current = head_.get();

        while (current != nullptr) {
            if (current->item.id == id) {
                return &current->item;
            }

            current = current->next.get();
        }

        return nullptr;
    }

    bool removeById(int id) {
        if (!head_) {
            return false;
        }

        if (head_->item.id == id) {
            head_ = std::move(head_->next);
            --size_;

            if (!head_) {
                tail_ = nullptr;
            }

            return true;
        }

        Node* previous = head_.get();

        while (previous->next) {
            if (previous->next->item.id == id) {
                const bool removedTail = previous->next.get() == tail_;

                previous->next = std::move(previous->next->next);
                --size_;

                if (removedTail) {
                    tail_ = previous;
                }

                return true;
            }

            previous = previous->next.get();
        }

        return false;
    }

    void print() const {
        const Node* current = head_.get();

        if (!current) {
            std::cout << "EMPTY\n";
            return;
        }

        while (current != nullptr) {
            std::cout
                << "[" << current->item.id << "] "
                << current->item.title
                << " | owner=" << current->item.owner
                << " | priority=" << current->item.priority
                << '\n';

            current = current->next.get();
        }
    }

    /*
     * This operation demonstrates an invariant check without relying on the
     * stored size alone. It detects accidental metadata corruption in the
     * queue implementation.
     */
    bool invariantHolds() const noexcept {
        std::size_t counted = 0;
        const Node* current = head_.get();
        const Node* last = nullptr;

        while (current != nullptr) {
            ++counted;
            last = current;
            current = current->next.get();
        }

        if (counted != size_) {
            return false;
        }

        if (size_ == 0) {
            return tail_ == nullptr;
        }

        return last == tail_;
    }
};

class WorkItemValidator {
public:
    static void validate(const WorkItem& item) {
        if (item.id <= 0) {
            throw std::invalid_argument("work-item ID must be positive");
        }

        if (item.title.empty()) {
            throw std::invalid_argument("work-item title cannot be empty");
        }

        if (item.owner.empty()) {
            throw std::invalid_argument("work-item owner cannot be empty");
        }

        if (item.priority < 1 || item.priority > 5) {
            throw std::invalid_argument(
                "priority must be between 1 and 5"
            );
        }
    }
};

class ValidatedWorkQueue {
private:
    WorkQueue queue_;

public:
    void enqueue(WorkItem item) {
        WorkItemValidator::validate(item);
        queue_.enqueue(std::move(item));
    }

    WorkItem dequeue() {
        return queue_.dequeue();
    }

    bool removeById(int id) {
        return queue_.removeById(id);
    }

    const WorkItem* findById(int id) const noexcept {
        return queue_.findById(id);
    }

    void print() const {
        queue_.print();
    }

    std::size_t size() const noexcept {
        return queue_.size();
    }

    bool invariantHolds() const noexcept {
        return queue_.invariantHolds();
    }
};

void demonstrateNodeMemory() {
    std::cout << "\n=== C++ Node Memory Model ===\n";

    struct DemoNode {
        int value;
        DemoNode* next;
    };

    DemoNode first{10, nullptr};
    DemoNode second{20, nullptr};

    first.next = &second;

    std::cout << "first.value: " << first.value << '\n';
    std::cout << "first.next->value: " << first.next->value << '\n';
    std::cout << "Address stored in first.next: "
              << static_cast<const void*>(first.next) << '\n';

    /*
     * The addresses are printed only to make the pointer relationship
     * visible. Code should not depend on particular addresses because memory
     * allocation is controlled by the runtime and operating system.
     */
}

void demonstrateArrayComparison() {
    std::cout << "\n=== Array and Linked-List Access ===\n";

    const std::vector<int> values{10, 20, 30, 40, 50};

    std::cout << "Vector index 3: " << values[3] << '\n';

    auto head = std::make_unique<struct SimpleNode>();
    head->value = 10;
    head->next = nullptr;

    auto second = std::make_unique<struct SimpleNode>();
    second->value = 20;
    second->next = nullptr;

    auto third = std::make_unique<struct SimpleNode>();
    third->value = 30;
    third->next = nullptr;

    /*
     * The standalone demonstration nodes use raw next pointers but remain
     * owned by unique_ptr variables. This separates ownership from the
     * pointer used for traversal.
     */
    head->next = second.get();
    second->next = third.get();

    SimpleNode* current = head.get();

    for (int step = 0; step < 2; ++step) {
        current = current->next;
    }

    std::cout << "Linked-list index 2 after traversal: "
              << current->value << '\n';
    std::cout << "Array/vector random access: O(1)\n";
    std::cout << "Singly linked-list indexed access: O(n)\n";
}

struct SimpleNode {
    int value{};
    SimpleNode* next{nullptr};
};

class AuditChain {
private:
    struct Node {
        std::string event;
        std::unique_ptr<Node> next;

        explicit Node(std::string eventName)
            : event(std::move(eventName)), next(nullptr) {}
    };

    std::unique_ptr<Node> head_;
    Node* tail_ = nullptr;

public:
    void append(std::string event) {
        auto node = std::make_unique<Node>(std::move(event));

        if (!head_) {
            tail_ = node.get();
            head_ = std::move(node);
            return;
        }

        tail_->next = std::move(node);
        tail_ = tail_->next.get();
    }

    void print() const {
        const Node* current = head_.get();

        while (current) {
            std::cout << "  " << current->event << '\n';
            current = current->next.get();
        }
    }
};

void demonstrateRepositoryScenario() {
    std::cout << "\n=== Repository Work Queue Case Study ===\n";

    ValidatedWorkQueue queue;

    queue.enqueue({
        1001,
        "Validate incoming change",
        "reviewer-a",
        5
    });

    queue.enqueue({
        1002,
        "Execute automated checks",
        "ci-system",
        4
    });

    queue.enqueue({
        1003,
        "Update technical documentation",
        "maintainer",
        2
    });

    std::cout << "Initial queue:\n";
    queue.print();

    std::cout << "Queue size: " << queue.size() << '\n';
    std::cout << "Invariant valid: "
              << std::boolalpha
              << queue.invariantHolds()
              << '\n';

    const WorkItem* found = queue.findById(1002);

    if (found) {
        std::cout << "Found item 1002: "
                  << found->title << '\n';
    }

    std::cout << "Removing item 1002: "
              << queue.removeById(1002)
              << '\n';

    std::cout << "Queue after removal:\n";
    queue.print();

    WorkItem next = queue.dequeue();

    std::cout << "Dequeued item: "
              << next.id << " - "
              << next.title << '\n';

    std::cout << "Remaining queue:\n";
    queue.print();
}

void demonstrateValidation() {
    std::cout << "\n=== Validation and Failure Handling ===\n";

    ValidatedWorkQueue queue;

    const std::vector<WorkItem> invalidItems{
        {0, "Invalid identifier", "developer", 3},
        {2001, "", "developer", 3},
        {2002, "Missing owner", "", 3},
        {2003, "Invalid priority", "developer", 8}
    };

    for (const auto& item : invalidItems) {
        try {
            queue.enqueue(item);
            std::cout << "Unexpectedly accepted invalid item\n";
        } catch (const std::invalid_argument& error) {
            std::cout << "Rejected invalid item: "
                      << error.what() << '\n';
        }
    }

    try {
        queue.dequeue();
    } catch (const std::underflow_error& error) {
        std::cout << "Empty-queue failure handled: "
                  << error.what() << '\n';
    }
}

void demonstratePointerTradeoffs() {
    std::cout << "\n=== Pointer and Allocation Trade-offs ===\n";

    std::cout
        << "A linked list allocates nodes independently, so each node "
        << "contains both data and link metadata.\n";

    std::cout
        << "Independent allocation can increase allocation overhead and "
        << "reduce cache locality compared with contiguous arrays.\n";

    std::cout
        << "The benefit is that inserting or removing a node after a known "
        << "position can change links without shifting later elements.\n";

    std::cout
        << "This case study uses unique_ptr ownership to avoid manual "
        << "delete operations and reduce memory-leak risk.\n";
}

void runAssertions() {
    std::cout << "\n=== Executable Invariant Checks ===\n";

    ValidatedWorkQueue queue;

    queue.enqueue({1, "First", "alice", 1});
    queue.enqueue({2, "Second", "bob", 2});
    queue.enqueue({3, "Third", "carol", 3});

    if (!queue.invariantHolds()) {
        throw std::logic_error("queue invariant failed after insertion");
    }

    if (queue.findById(2) == nullptr) {
        throw std::logic_error("expected work item was not found");
    }

    if (!queue.removeById(2)) {
        throw std::logic_error("expected work item was not removed");
    }

    if (queue.findById(2) != nullptr) {
        throw std::logic_error("removed item is still present");
    }

    if (!queue.invariantHolds()) {
        throw std::logic_error("queue invariant failed after removal");
    }

    WorkItem first = queue.dequeue();

    if (first.id != 1) {
        throw std::logic_error("FIFO ordering was violated");
    }

    if (!queue.invariantHolds()) {
        throw std::logic_error("queue invariant failed after dequeue");
    }

    std::cout << "All C++ assertions passed.\n";
}

int main() {
    try {
        std::cout << std::string(72, '=') << '\n';
        std::cout << "LINKED LIST INTRODUCTION\n";
        std::cout << std::string(72, '=') << '\n';

        demonstrateNodeMemory();
        demonstrateArrayComparison();
        demonstrateRepositoryScenario();
        demonstrateValidation();
        demonstratePointerTradeoffs();

        AuditChain history;
        history.append("Work item accepted");
        history.append("Validation completed");
        history.append("Processing started");

        std::cout << "\n=== Linked Audit Chain ===\n";
        history.print();

        runAssertions();

        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Fatal error: " << error.what() << '\n';
        return 1;
    }
}
