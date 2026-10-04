#include <algorithm>
#include <iostream>
#include <optional>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

/*
 * Circular Linked List Case Study
 *
 * Scenario:
 * A transport control center manages a fleet of autonomous shuttle
 * services operating on a fixed circular route.
 *
 * A shuttle route is represented by a circular doubly linked list:
 *
 *     Depot A <-> Depot B <-> Depot C <-> Depot D
 *          ^                         |
 *          |_________________________|
 *
 * Dispatching can move in either direction. A shuttle can be inserted
 * into the route, removed from the route, or advanced to the next stop.
 *
 * A second circular singly linked list models a round-robin service
 * queue where only the next service is relevant.
 *
 * The program demonstrates:
 * - circular invariants
 * - insertion
 * - deletion
 * - forward and backward traversal
 * - bounded traversal
 * - validation
 * - exception-based error handling
 * - route scheduling
 * - algorithmic complexity considerations
 *
 * Compile:
 *   g++ -std=c++17 -Wall -Wextra -pedantic circular_linked_lists.cpp -o circular
 */

// ============================================================
// Circular Doubly Linked List
// ============================================================

template <typename T>
class CircularDoublyList {
private:
    struct Node {
        T value;
        Node* prev;
        Node* next;

        explicit Node(const T& value)
            : value(value), prev(this), next(this) {}
    };

    Node* head_;
    std::size_t size_;

public:
    CircularDoublyList()
        : head_(nullptr), size_(0) {}

    CircularDoublyList(const CircularDoublyList&) = delete;
    CircularDoublyList& operator=(const CircularDoublyList&) = delete;

    ~CircularDoublyList() {
        clear();
    }

    bool empty() const noexcept {
        return head_ == nullptr;
    }

    std::size_t size() const noexcept {
        return size_;
    }

    void clear() noexcept {
        if (head_ == nullptr) {
            return;
        }

        Node* current = head_->next;

        while (current != head_) {
            Node* next = current->next;
            delete current;
            current = next;
        }

        delete head_;
        head_ = nullptr;
        size_ = 0;
    }

    void push_back(const T& value) {
        Node* node = new Node(value);

        if (head_ == nullptr) {
            head_ = node;
            ++size_;
            return;
        }

        Node* tail = head_->prev;

        node->prev = tail;
        node->next = head_;

        tail->next = node;
        head_->prev = node;

        ++size_;
    }

    void push_front(const T& value) {
        push_back(value);

        // The previous tail becomes the new head.
        head_ = head_->prev;
    }

    bool insert_after(const T& target, const T& value) {
        Node* node = find(target);

        if (node == nullptr) {
            return false;
        }

        insert_after_node(node, value);
        return true;
    }

    void insert_after_node(Node* node, const T& value) {
        if (node == nullptr) {
            throw std::invalid_argument("cannot insert after a null node");
        }

        Node* successor = node->next;
        Node* inserted = new Node(value);

        inserted->prev = node;
        inserted->next = successor;

        node->next = inserted;
        successor->prev = inserted;

        ++size_;
    }

    bool remove_value(const T& value) {
        Node* node = find(value);

        if (node == nullptr) {
            return false;
        }

        remove_node(node);
        return true;
    }

    void remove_node(Node* node) {
        if (node == nullptr || head_ == nullptr) {
            throw std::invalid_argument("node does not exist");
        }

        if (size_ == 1) {
            if (node != head_) {
                throw std::invalid_argument("node is not part of this list");
            }

            delete node;
            head_ = nullptr;
            size_ = 0;
            return;
        }

        node->prev->next = node->next;
        node->next->prev = node->prev;

        if (node == head_) {
            head_ = node->next;
        }

        delete node;
        --size_;
    }

    Node* find(const T& value) const {
        if (head_ == nullptr) {
            return nullptr;
        }

        Node* current = head_;

        for (std::size_t i = 0; i < size_; ++i) {
            if (current->value == value) {
                return current;
            }

            current = current->next;
        }

        return nullptr;
    }

    std::vector<T> forward_values() const {
        std::vector<T> result;

        if (head_ == nullptr) {
            return result;
        }

        Node* current = head_;

        for (std::size_t i = 0; i < size_; ++i) {
            result.push_back(current->value);
            current = current->next;
        }

        return result;
    }

    std::vector<T> backward_values() const {
        std::vector<T> result;

        if (head_ == nullptr) {
            return result;
        }

        Node* current = head_->prev;

        for (std::size_t i = 0; i < size_; ++i) {
            result.push_back(current->value);
            current = current->prev;
        }

        return result;
    }

    /*
     * Circular structures need explicit invariant checking.
     * A null-terminated linked-list check is inappropriate because
     * the correct structure intentionally contains no null links.
     */
    void validate() const {
        if (head_ == nullptr) {
            if (size_ != 0) {
                throw std::logic_error("empty list has non-zero size");
            }
            return;
        }

        if (size_ == 0) {
            throw std::logic_error("non-empty list has zero size");
        }

        if (head_->prev == nullptr || head_->next == nullptr) {
            throw std::logic_error("head contains a null link");
        }

        Node* current = head_;

        for (std::size_t i = 0; i < size_; ++i) {
            if (current->next == nullptr || current->prev == nullptr) {
                throw std::logic_error("broken circular link");
            }

            if (current->next->prev != current) {
                throw std::logic_error("next/prev invariant broken");
            }

            if (current->prev->next != current) {
                throw std::logic_error("prev/next invariant broken");
            }

            current = current->next;
        }

        if (current != head_) {
            throw std::logic_error("forward cycle does not return to head");
        }
    }
};


// ============================================================
// Circular Singly Linked List
// ============================================================

template <typename T>
class CircularSinglyList {
private:
    struct Node {
        T value;
        Node* next;

        explicit Node(const T& value)
            : value(value), next(this) {}
    };

    Node* tail_;
    std::size_t size_;

public:
    CircularSinglyList()
        : tail_(nullptr), size_(0) {}

    CircularSinglyList(const CircularSinglyList&) = delete;
    CircularSinglyList& operator=(const CircularSinglyList&) = delete;

    ~CircularSinglyList() {
        clear();
    }

    bool empty() const noexcept {
        return tail_ == nullptr;
    }

    std::size_t size() const noexcept {
        return size_;
    }

    void clear() noexcept {
        if (tail_ == nullptr) {
            return;
        }

        Node* head = tail_->next;
        Node* current = head->next;

        while (current != head) {
            Node* next = current->next;
            delete current;
            current = next;
        }

        delete head;

        tail_ = nullptr;
        size_ = 0;
    }

    void push_back(const T& value) {
        Node* node = new Node(value);

        if (tail_ == nullptr) {
            tail_ = node;
            ++size_;
            return;
        }

        node->next = tail_->next;
        tail_->next = node;
        tail_ = node;

        ++size_;
    }

    void push_front(const T& value) {
        Node* node = new Node(value);

        if (tail_ == nullptr) {
            tail_ = node;
            ++size_;
            return;
        }

        node->next = tail_->next;
        tail_->next = node;

        ++size_;
    }

    bool remove_value(const T& value) {
        if (tail_ == nullptr) {
            return false;
        }

        Node* previous = tail_;
        Node* current = tail_->next;

        for (std::size_t i = 0; i < size_; ++i) {
            if (current->value == value) {
                if (size_ == 1) {
                    delete current;
                    tail_ = nullptr;
                    size_ = 0;
                    return true;
                }

                previous->next = current->next;

                if (current == tail_) {
                    tail_ = previous;
                }

                delete current;
                --size_;
                return true;
            }

            previous = current;
            current = current->next;
        }

        return false;
    }

    void rotate() noexcept {
        if (tail_ != nullptr) {
            tail_ = tail_->next;
        }
    }

    std::vector<T> values() const {
        std::vector<T> result;

        if (tail_ == nullptr) {
            return result;
        }

        Node* current = tail_->next;

        for (std::size_t i = 0; i < size_; ++i) {
            result.push_back(current->value);
            current = current->next;
        }

        return result;
    }

    void validate() const {
        if (tail_ == nullptr) {
            if (size_ != 0) {
                throw std::logic_error("empty list has non-zero size");
            }
            return;
        }

        if (size_ == 0) {
            throw std::logic_error("non-empty list has zero size");
        }

        if (tail_->next == nullptr) {
            throw std::logic_error("tail must point to the head");
        }

        Node* head = tail_->next;
        Node* current = head;

        for (std::size_t i = 0; i < size_; ++i) {
            if (current == nullptr) {
                throw std::logic_error("null encountered inside cycle");
            }

            current = current->next;
        }

        if (current != head) {
            throw std::logic_error("cycle length does not match size");
        }
    }
};


// ============================================================
// Transport Route Domain Model
// ============================================================

struct Station {
    std::string code;
    int passengerCapacity;

    bool operator==(const Station& other) const {
        return code == other.code;
    }
};

std::ostream& operator<<(std::ostream& out, const Station& station) {
    out << station.code << "(capacity=" << station.passengerCapacity << ")";
    return out;
}

class ShuttleRoute {
private:
    CircularDoublyList<Station> stations_;

public:
    void add_station(const Station& station) {
        if (station.code.empty()) {
            throw std::invalid_argument("station code cannot be empty");
        }

        if (station.passengerCapacity <= 0) {
            throw std::invalid_argument("station capacity must be positive");
        }

        if (stations_.find(station) != nullptr) {
            throw std::invalid_argument("station code already exists");
        }

        stations_.push_back(station);
    }

    void insert_station_after(
        const std::string& existingCode,
        const Station& station
    ) {
        if (station.code.empty()) {
            throw std::invalid_argument("station code cannot be empty");
        }

        if (station.passengerCapacity <= 0) {
            throw std::invalid_argument("station capacity must be positive");
        }

        if (stations_.find(station) != nullptr) {
            throw std::invalid_argument("station code already exists");
        }

        Station target{existingCode, 0};
        auto* targetNode = stations_.find(target);

        if (targetNode == nullptr) {
            throw std::invalid_argument("target station does not exist");
        }

        stations_.insert_after_node(targetNode, station);
    }

    void remove_station(const std::string& code) {
        Station target{code, 0};
        auto* node = stations_.find(target);

        if (node == nullptr) {
            throw std::invalid_argument("station does not exist");
        }

        stations_.remove_node(node);
    }

    void print_route() const {
        const auto route = stations_.forward_values();

        std::cout << "Forward route: ";

        for (std::size_t i = 0; i < route.size(); ++i) {
            std::cout << route[i];

            if (i + 1 < route.size()) {
                std::cout << " -> ";
            }
        }

        if (!route.empty()) {
            std::cout << " -> HEAD";
        }

        std::cout << '\n';
    }

    void print_reverse_route() const {
        const auto route = stations_.backward_values();

        std::cout << "Reverse route: ";

        for (std::size_t i = 0; i < route.size(); ++i) {
            std::cout << route[i];

            if (i + 1 < route.size()) {
                std::cout << " -> ";
            }
        }

        std::cout << '\n';
    }

    void validate() const {
        stations_.validate();
    }
};


// ============================================================
// Case Study Demonstrations
// ============================================================

void demonstrate_singly_list() {
    std::cout << "\n=== Circular Singly Linked List ===\n";

    CircularSinglyList<std::string> queue;

    queue.push_back("Service-A");
    queue.push_back("Service-B");
    queue.push_back("Service-C");

    queue.validate();

    std::cout << "Initial queue: ";

    for (const auto& service : queue.values()) {
        std::cout << service << ' ';
    }

    std::cout << '\n';

    queue.push_front("Priority-Service");

    std::cout << "After front insertion: ";

    for (const auto& service : queue.values()) {
        std::cout << service << ' ';
    }

    std::cout << '\n';

    queue.remove_value("Service-B");

    std::cout << "After deletion: ";

    for (const auto& service : queue.values()) {
        std::cout << service << ' ';
    }

    std::cout << '\n';

    queue.rotate();

    std::cout << "After rotation: ";

    for (const auto& service : queue.values()) {
        std::cout << service << ' ';
    }

    std::cout << '\n';

    queue.validate();
}


void demonstrate_route_case_study() {
    std::cout << "\n=== Circular Doubly Linked Route ===\n";

    ShuttleRoute route;

    route.add_station({"A", 60});
    route.add_station({"B", 45});
    route.add_station({"C", 80});
    route.add_station({"D", 50});

    route.validate();
    route.print_route();
    route.print_reverse_route();

    std::cout << "\nInserting a station after B...\n";

    route.insert_station_after("B", {"B2", 40});

    route.validate();
    route.print_route();

    std::cout << "\nRemoving station C...\n";

    route.remove_station("C");

    route.validate();
    route.print_route();
    route.print_reverse_route();

    std::cout << "\nRemoving the head station A...\n";

    route.remove_station("A");

    route.validate();
    route.print_route();
}


void demonstrate_failure_conditions() {
    std::cout << "\n=== Validation and Failure Conditions ===\n";

    ShuttleRoute route;

    try {
        route.add_station({"", 40});
    } catch (const std::exception& error) {
        std::cout << "Rejected invalid station: "
                  << error.what() << '\n';
    }

    try {
        route.add_station({"A", 0});
    } catch (const std::exception& error) {
        std::cout << "Rejected invalid capacity: "
                  << error.what() << '\n';
    }

    route.add_station({"A", 40});

    try {
        route.add_station({"A", 50});
    } catch (const std::exception& error) {
        std::cout << "Rejected duplicate station: "
                  << error.what() << '\n';
    }

    try {
        route.remove_station("UNKNOWN");
    } catch (const std::exception& error) {
        std::cout << "Rejected missing station deletion: "
                  << error.what() << '\n';
    }

    route.validate();
}


// ============================================================
// Complexity Reference
// ============================================================

void print_complexity_reference() {
    std::cout << "\n=== Complexity Reference ===\n";

    std::cout
        << "Circular singly list:\n"
        << "  Append with tail pointer       O(1)\n"
        << "  Prepend with tail pointer      O(1)\n"
        << "  Search                         O(n)\n"
        << "  Delete by value               O(n)\n"
        << "  Rotate                         O(1)\n"
        << '\n'
        << "Circular doubly list:\n"
        << "  Append                         O(1)\n"
        << "  Prepend                        O(1)\n"
        << "  Search                         O(n)\n"
        << "  Delete known node              O(1)\n"
        << "  Bidirectional traversal        O(n)\n"
        << '\n'
        << "Memory:\n"
        << "  Singly list stores one link per node.\n"
        << "  Doubly list stores two links per node and supports direct "
           "neighbor rewiring.\n";
}


// ============================================================
// Program Entry Point
// ============================================================

int main() {
    try {
        demonstrate_singly_list();
        demonstrate_route_case_study();
        demonstrate_failure_conditions();
        print_complexity_reference();

        std::cout << "\nAll circular-list invariants validated successfully.\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Fatal error: " << error.what() << '\n';
        return 1;
    }
}
