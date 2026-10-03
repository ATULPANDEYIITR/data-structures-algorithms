#include <algorithm>
#include <cassert>
#include <iostream>
#include <optional>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <utility>
#include <vector>

/*
 * C++17 case study:
 * Repository-style change history implemented with a doubly linked list.
 *
 * The scenario models a review dashboard that needs:
 * - chronological forward traversal,
 * - reverse traversal for newest-first display,
 * - insertion and deletion of review events,
 * - direct removal of a known event,
 * - structural invariant checking.
 *
 * The case study uses ownership-aware C++ design:
 * the list owns its nodes, while public operations expose stable Node*
 * handles only for the duration in which callers obey the documented
 * lifetime rule. removeNode invalidates the removed handle.
 */

class ChangeHistory {
public:
    struct Node {
        std::string event;
        Node* prev;
        Node* next;

        explicit Node(std::string eventValue)
            : event(std::move(eventValue)), prev(nullptr), next(nullptr) {}
    };

    ChangeHistory() = default;

    ChangeHistory(const ChangeHistory&) = delete;
    ChangeHistory& operator=(const ChangeHistory&) = delete;

    ChangeHistory(ChangeHistory&& other) noexcept
        : head_(other.head_), tail_(other.tail_), size_(other.size_) {
        other.head_ = nullptr;
        other.tail_ = nullptr;
        other.size_ = 0;
    }

    ChangeHistory& operator=(ChangeHistory&& other) noexcept {
        if (this != &other) {
            clear();

            head_ = other.head_;
            tail_ = other.tail_;
            size_ = other.size_;

            other.head_ = nullptr;
            other.tail_ = nullptr;
            other.size_ = 0;
        }

        return *this;
    }

    ~ChangeHistory() {
        clear();
    }

    Node* append(std::string event) {
        Node* node = new Node(std::move(event));

        if (tail_ == nullptr) {
            head_ = tail_ = node;
        } else {
            node->prev = tail_;
            tail_->next = node;
            tail_ = node;
        }

        ++size_;
        return node;
    }

    Node* prepend(std::string event) {
        Node* node = new Node(std::move(event));

        if (head_ == nullptr) {
            head_ = tail_ = node;
        } else {
            node->next = head_;
            head_->prev = node;
            head_ = node;
        }

        ++size_;
        return node;
    }

    Node* insertBefore(Node* current, std::string event) {
        if (current == nullptr) {
            throw std::invalid_argument("current node cannot be null");
        }

        if (current == head_) {
            return prepend(std::move(event));
        }

        Node* previous = current->prev;

        if (previous == nullptr) {
            throw std::logic_error("current node has inconsistent links");
        }

        Node* node = new Node(std::move(event));

        node->prev = previous;
        node->next = current;

        previous->next = node;
        current->prev = node;

        ++size_;
        return node;
    }

    std::string removeNode(Node* node) {
        if (node == nullptr) {
            throw std::invalid_argument("cannot remove a null node");
        }

        Node* previous = node->prev;
        Node* next = node->next;

        if (previous == nullptr) {
            head_ = next;
        } else {
            previous->next = next;
        }

        if (next == nullptr) {
            tail_ = previous;
        } else {
            next->prev = previous;
        }

        std::string removedEvent = node->event;

        node->prev = nullptr;
        node->next = nullptr;

        delete node;
        --size_;

        if (size_ == 0) {
            head_ = nullptr;
            tail_ = nullptr;
        }

        return removedEvent;
    }

    std::optional<std::string> removeFirst(const std::string& event) {
        Node* current = head_;

        while (current != nullptr) {
            if (current->event == event) {
                return removeNode(current);
            }

            current = current->next;
        }

        return std::nullopt;
    }

    Node* find(const std::string& event) const {
        Node* current = head_;

        while (current != nullptr) {
            if (current->event == event) {
                return current;
            }

            current = current->next;
        }

        return nullptr;
    }

    std::vector<std::string> forward() const {
        std::vector<std::string> result;
        result.reserve(size_);

        Node* current = head_;

        while (current != nullptr) {
            result.push_back(current->event);
            current = current->next;
        }

        return result;
    }

    std::vector<std::string> backward() const {
        std::vector<std::string> result;
        result.reserve(size_);

        Node* current = tail_;

        while (current != nullptr) {
            result.push_back(current->event);
            current = current->prev;
        }

        return result;
    }

    void clear() noexcept {
        Node* current = head_;

        while (current != nullptr) {
            Node* next = current->next;
            delete current;
            current = next;
        }

        head_ = nullptr;
        tail_ = nullptr;
        size_ = 0;
    }

    std::size_t size() const noexcept {
        return size_;
    }

    bool empty() const noexcept {
        return size_ == 0;
    }

    Node* head() const noexcept {
        return head_;
    }

    Node* tail() const noexcept {
        return tail_;
    }

    /*
     * Structural validation is valuable in pointer-heavy C++ systems.
     * It detects corrupted links, incorrect endpoint updates, and cycles.
     */
    void validate() const {
        if (size_ == 0) {
            if (head_ != nullptr || tail_ != nullptr) {
                throw std::logic_error("empty list has non-null endpoints");
            }
            return;
        }

        if (head_ == nullptr || tail_ == nullptr) {
            throw std::logic_error("non-empty list has null endpoint");
        }

        if (head_->prev != nullptr) {
            throw std::logic_error("head.prev must be null");
        }

        if (tail_->next != nullptr) {
            throw std::logic_error("tail.next must be null");
        }

        std::size_t forwardCount = 0;
        Node* previous = nullptr;
        Node* current = head_;

        while (current != nullptr) {
            if (current->prev != previous) {
                throw std::logic_error("broken previous pointer");
            }

            if (current->next != nullptr &&
                current->next->prev != current) {
                throw std::logic_error("next/prev relationship is broken");
            }

            previous = current;
            current = current->next;
            ++forwardCount;

            if (forwardCount > size_) {
                throw std::logic_error("forward cycle detected");
            }
        }

        if (previous != tail_) {
            throw std::logic_error("forward traversal did not end at tail");
        }

        std::size_t backwardCount = 0;
        Node* next = nullptr;
        current = tail_;

        while (current != nullptr) {
            if (current->next != next) {
                throw std::logic_error("broken next pointer");
            }

            if (current->prev != nullptr &&
                current->prev->next != current) {
                throw std::logic_error("prev/next relationship is broken");
            }

            next = current;
            current = current->prev;
            ++backwardCount;

            if (backwardCount > size_) {
                throw std::logic_error("backward cycle detected");
            }
        }

        if (next != head_) {
            throw std::logic_error("backward traversal did not end at head");
        }

        if (forwardCount != size_ || backwardCount != size_) {
            throw std::logic_error("stored size does not match traversal");
        }
    }

private:
    Node* head_ = nullptr;
    Node* tail_ = nullptr;
    std::size_t size_ = 0;
};


/*
 * A repository event has enough structure to make the list useful as a
 * technical case study rather than merely storing strings.
 */
struct ReviewEvent {
    std::string actor;
    std::string action;
    std::string detail;

    std::string format() const {
        return actor + " " + action + " " + detail;
    }
};


/*
 * ReviewTimeline stores review events chronologically.
 *
 * The application frequently displays newest events first, so tail-based
 * reverse traversal avoids rebuilding the list before rendering.
 */
class ReviewTimeline {
public:
    ChangeHistory::Node* record(const ReviewEvent& event) {
        return history_.append(event.format());
    }

    void insertSystemEvent(const ReviewEvent& event) {
        history_.prepend(event.format());
    }

    bool removeEventContaining(const std::string& text) {
        ChangeHistory::Node* current = history_.head();

        while (current != nullptr) {
            ChangeHistory::Node* next = current->next;

            if (current->event.find(text) != std::string::npos) {
                history_.removeNode(current);
                return true;
            }

            current = next;
        }

        return false;
    }

    void printChronological() const {
        std::cout << "\nChronological review timeline\n";

        for (const auto& event : history_.forward()) {
            std::cout << "  " << event << '\n';
        }
    }

    void printNewestFirst() const {
        std::cout << "\nNewest-first review timeline\n";

        for (const auto& event : history_.backward()) {
            std::cout << "  " << event << '\n';
        }
    }

    void validate() const {
        history_.validate();
    }

    std::size_t size() const {
        return history_.size();
    }

private:
    ChangeHistory history_;
};


/*
 * A navigation-like cursor demonstrates why previous and next pointers are
 * useful when an application maintains a current position inside a sequence.
 */
class ReviewCursor {
public:
    explicit ReviewCursor(ChangeHistory& history)
        : history_(history), current_(history.head()) {}

    std::string current() const {
        if (current_ == nullptr) {
            return "<empty>";
        }

        return current_->event;
    }

    bool moveNext() {
        if (current_ == nullptr || current_->next == nullptr) {
            return false;
        }

        current_ = current_->next;
        return true;
    }

    bool movePrevious() {
        if (current_ == nullptr || current_->prev == nullptr) {
            return false;
        }

        current_ = current_->prev;
        return true;
    }

private:
    ChangeHistory& history_;
    ChangeHistory::Node* current_;
};


void printVector(const std::vector<std::string>& values) {
    std::cout << "  ";

    for (std::size_t i = 0; i < values.size(); ++i) {
        if (i != 0) {
            std::cout << " <-> ";
        }

        std::cout << values[i];
    }

    if (values.empty()) {
        std::cout << "<empty>";
    }

    std::cout << '\n';
}


void demonstrateCoreStructure() {
    std::cout << "=== Core doubly linked list structure ===\n";

    ChangeHistory history;

    history.append("commit: add authentication");
    history.append("review: security reviewer requested changes");
    history.append("commit: address review comments");
    history.append("review: changes approved");

    history.validate();

    std::cout << "\nForward traversal:\n";
    printVector(history.forward());

    std::cout << "\nBackward traversal:\n";
    printVector(history.backward());

    std::cout << "\nHead: " << history.head()->event << '\n';
    std::cout << "Tail: " << history.tail()->event << '\n';
}


void demonstrateKnownNodeDeletion() {
    std::cout << "\n=== Known-node O(1) deletion ===\n";

    ChangeHistory history;

    history.append("file: README.md");
    ChangeHistory::Node* target =
        history.append("file: security-policy.md");
    history.append("file: review-checklist.md");

    std::cout << "Before deletion:\n";
    printVector(history.forward());

    /*
     * Searching for the target is O(n), but once its node address is known,
     * unlinking requires only predecessor/successor pointer updates.
     */
    history.removeNode(target);

    std::cout << "After deletion:\n";
    printVector(history.forward());

    history.validate();
}


void demonstrateReviewTimeline() {
    std::cout << "\n=== Repository review timeline case study ===\n";

    ReviewTimeline timeline;

    timeline.record({
        "developer",
        "opened",
        "pull-request #42"
    });

    timeline.record({
        "reviewer",
        "commented-on",
        "authentication middleware"
    });

    timeline.record({
        "developer",
        "updated",
        "the requested changes"
    });

    timeline.record({
        "reviewer",
        "approved",
        "pull-request #42"
    });

    timeline.insertSystemEvent({
        "repository",
        "recorded",
        "branch protection status"
    });

    timeline.printChronological();
    timeline.printNewestFirst();

    std::cout << "\nRemoving one obsolete event:\n";

    const bool removed =
        timeline.removeEventContaining("branch protection status");

    std::cout << "Removed: " << std::boolalpha << removed << '\n';

    timeline.printNewestFirst();
    timeline.validate();
}


void demonstrateCursor() {
    std::cout << "\n=== Bidirectional cursor ===\n";

    ChangeHistory history;
    history.append("review opened");
    history.append("comment added");
    history.append("changes pushed");
    history.append("approval recorded");

    ReviewCursor cursor(history);

    std::cout << "Current: " << cursor.current() << '\n';

    cursor.moveNext();
    cursor.moveNext();
    std::cout << "After moving forward twice: "
              << cursor.current() << '\n';

    cursor.movePrevious();
    std::cout << "After moving backward once: "
              << cursor.current() << '\n';

    cursor.movePrevious();
    std::cout << "After moving backward again: "
              << cursor.current() << '\n';
}


void demonstrateEdgeCases() {
    std::cout << "\n=== Edge cases ===\n";

    ChangeHistory history;

    try {
        history.removeNode(nullptr);
    } catch (const std::exception& error) {
        std::cout << "Null deletion rejected: "
                  << error.what() << '\n';
    }

    history.append("only event");
    history.validate();

    ChangeHistory::Node* only = history.head();
    history.removeNode(only);

    std::cout << "After deleting only node, empty="
              << std::boolalpha << history.empty() << '\n';

    history.validate();

    const auto missing = history.removeFirst("not present");

    std::cout << "Missing event found: "
              << std::boolalpha << missing.has_value() << '\n';
}


void demonstrateMoveSemantics() {
    std::cout << "\n=== Move ownership ===\n";

    ChangeHistory original;
    original.append("event-A");
    original.append("event-B");

    ChangeHistory moved = std::move(original);

    std::cout << "Moved list:\n";
    printVector(moved.forward());

    std::cout << "Original list after move is empty: "
              << std::boolalpha << original.empty() << '\n';

    moved.validate();
    original.validate();
}


void runAssertions() {
    std::cout << "\n=== Assertions ===\n";

    ChangeHistory history;

    assert(history.empty());

    history.append("B");
    history.prepend("A");
    history.append("D");

    ChangeHistory::Node* d = history.tail();
    history.insertBefore(d, "C");

    const auto forward = history.forward();
    const auto backward = history.backward();

    assert(
        forward ==
        std::vector<std::string>{"A", "B", "C", "D"}
    );

    assert(
        backward ==
        std::vector<std::string>{"D", "C", "B", "A"}
    );

    history.validate();

    ChangeHistory::Node* b = history.find("B");
    assert(b != nullptr);

    history.removeNode(b);
    assert(
        history.forward() ==
        std::vector<std::string>{"A", "C", "D"}
    );

    history.validate();

    const auto removed = history.removeFirst("C");
    assert(removed.has_value());
    assert(removed.value() == "C");

    history.removeNode(history.head());
    history.removeNode(history.head());

    assert(history.empty());
    history.validate();

    std::cout << "All C++ assertions passed.\n";
}


int main() {
    try {
        demonstrateCoreStructure();
        demonstrateKnownNodeDeletion();
        demonstrateReviewTimeline();
        demonstrateCursor();
        demonstrateEdgeCases();
        demonstrateMoveSemantics();
        runAssertions();

        std::cout << "\n=== Complexity characteristics ===\n";
        std::cout << "Prepend: O(1)\n";
        std::cout << "Append: O(1) with a tail pointer\n";
        std::cout << "Known-node removal: O(1)\n";
        std::cout << "Search: O(n)\n";
        std::cout << "Forward traversal: O(n)\n";
        std::cout << "Backward traversal: O(n)\n";
        std::cout << "Indexed access: O(n) without an auxiliary index\n";

        std::cout
            << "\nThe doubly linked design stores two links per node. "
               "That extra memory and pointer-maintenance cost provides "
               "direct movement in both directions and local O(1) "
               "insertion or deletion when the affected node is known.\n";

        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Fatal error: " << error.what() << '\n';
        return 1;
    }
}
