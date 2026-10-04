#include <algorithm>
#include <cassert>
#include <cstddef>
#include <iostream>
#include <optional>
#include <random>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <utility>
#include <vector>

class RepositoryChangeList {
private:
    struct Node {
        int changeId;
        std::string description;
        Node* next;

        Node(int id, std::string text)
            : changeId(id), description(std::move(text)), next(nullptr) {}
    };

    Node* head_ = nullptr;
    Node* tail_ = nullptr;
    std::size_t size_ = 0;

public:
    RepositoryChangeList() = default;

    RepositoryChangeList(const std::vector<std::pair<int, std::string>>& changes) {
        for (const auto& [id, description] : changes) {
            append(id, description);
        }
    }

    RepositoryChangeList(const RepositoryChangeList&) = delete;
    RepositoryChangeList& operator=(const RepositoryChangeList&) = delete;

    RepositoryChangeList(RepositoryChangeList&& other) noexcept
        : head_(other.head_), tail_(other.tail_), size_(other.size_) {
        other.head_ = nullptr;
        other.tail_ = nullptr;
        other.size_ = 0;
    }

    RepositoryChangeList& operator=(RepositoryChangeList&& other) noexcept {
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

    ~RepositoryChangeList() {
        clear();
    }

    void append(int id, const std::string& description) {
        Node* node = new Node(id, description);

        if (head_ == nullptr) {
            head_ = tail_ = node;
        } else {
            tail_->next = node;
            tail_ = node;
        }

        ++size_;
    }

    std::vector<int> ids() const {
        std::vector<int> result;
        result.reserve(size_);

        std::unordered_set<const Node*> visited;

        const Node* current = head_;

        while (current != nullptr) {
            if (!visited.insert(current).second) {
                throw std::logic_error("Cycle detected in change list");
            }

            result.push_back(current->changeId);
            current = current->next;
        }

        return result;
    }

    void print(const std::string& title) const {
        std::cout << title << ": ";

        const Node* current = head_;

        while (current != nullptr) {
            std::cout << "[" << current->changeId << ": "
                      << current->description << "]";

            if (current->next != nullptr) {
                std::cout << " -> ";
            }

            current = current->next;
        }

        std::cout << " -> null\n";
    }

    void validate() const {
        std::size_t count = 0;
        const Node* current = head_;
        const Node* last = nullptr;
        std::unordered_set<const Node*> visited;

        while (current != nullptr) {
            if (!visited.insert(current).second) {
                throw std::logic_error("Linked-list cycle detected");
            }

            ++count;
            last = current;
            current = current->next;
        }

        if (count != size_) {
            throw std::logic_error("Node count does not match stored size");
        }

        if (last != tail_) {
            throw std::logic_error("Tail pointer is inconsistent");
        }

        if (tail_ != nullptr && tail_->next != nullptr) {
            throw std::logic_error("Tail must terminate the list");
        }
    }

    void reverseIterative() {
        /*
         * A three-pointer traversal is sufficient:
         * previous is the reversed prefix,
         * current is the node being processed,
         * next preserves the unprocessed suffix.
         *
         * No nodes are allocated and no payload values are copied.
         */
        Node* previous = nullptr;
        Node* current = head_;
        Node* oldHead = head_;

        while (current != nullptr) {
            Node* next = current->next;
            current->next = previous;
            previous = current;
            current = next;
        }

        head_ = previous;
        tail_ = oldHead;
    }

private:
    static Node* reverseRecursive(Node* current, Node* previous) {
        if (current == nullptr) {
            return previous;
        }

        Node* next = current->next;
        current->next = previous;

        return reverseRecursive(next, current);
    }

public:
    void reverseRecursive() {
        Node* oldHead = head_;
        head_ = reverseRecursive(head_, nullptr);
        tail_ = oldHead;
    }

    void reverseInGroups(std::size_t k) {
        if (k == 0) {
            throw std::invalid_argument("Group size must be greater than zero");
        }

        if (k <= 1 || head_ == nullptr) {
            return;
        }

        Node dummy(0, "sentinel");
        dummy.next = head_;

        Node* groupPrevious = &dummy;

        while (true) {
            Node* kth = groupPrevious;

            for (std::size_t i = 0; i < k; ++i) {
                kth = kth->next;

                if (kth == nullptr) {
                    head_ = dummy.next;
                    recomputeTail();
                    return;
                }
            }

            Node* groupNext = kth->next;

            Node* previous = groupNext;
            Node* current = groupPrevious->next;

            while (current != groupNext) {
                Node* next = current->next;
                current->next = previous;
                previous = current;
                current = next;
            }

            Node* oldGroupHead = groupPrevious->next;
            groupPrevious->next = kth;
            groupPrevious = oldGroupHead;
        }
    }

    void reverseInGroupsRecursive(std::size_t k) {
        if (k == 0) {
            throw std::invalid_argument("Group size must be greater than zero");
        }

        if (k <= 1 || head_ == nullptr) {
            return;
        }

        Node* oldHead = head_;

        std::function<Node*(Node*)> reverseGroups =
            [&](Node* head) -> Node* {
                Node* probe = head;

                for (std::size_t i = 0; i < k; ++i) {
                    if (probe == nullptr) {
                        return head;
                    }
                    probe = probe->next;
                }

                Node* previous = nullptr;
                Node* current = head;

                for (std::size_t i = 0; i < k; ++i) {
                    Node* next = current->next;
                    current->next = previous;
                    previous = current;
                    current = next;
                }

                head->next = reverseGroups(current);
                return previous;
            };

        head_ = reverseGroups(head_);
        tail_ = oldHead;
        recomputeTail();
    }

private:
    void recomputeTail() {
        if (head_ == nullptr) {
            tail_ = nullptr;
            return;
        }

        Node* current = head_;

        while (current->next != nullptr) {
            current = current->next;
        }

        tail_ = current;
    }

public:
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
};

std::vector<int> expectedReverse(const std::vector<int>& input) {
    std::vector<int> result = input;
    std::reverse(result.begin(), result.end());
    return result;
}

std::vector<int> expectedGroupReverse(
    const std::vector<int>& input,
    std::size_t k
) {
    std::vector<int> result = input;

    if (k <= 1) {
        return result;
    }

    for (std::size_t start = 0; start + k <= result.size(); start += k) {
        std::reverse(
            result.begin() + static_cast<std::ptrdiff_t>(start),
            result.begin() + static_cast<std::ptrdiff_t>(start + k)
        );
    }

    return result;
}

void verifyEqual(
    const std::vector<int>& actual,
    const std::vector<int>& expected,
    const std::string& operation
) {
    if (actual != expected) {
        throw std::runtime_error(operation + " produced an unexpected sequence");
    }
}

void runBasicScenario() {
    std::cout << "\n=== Pull-request changeset scenario ===\n";

    RepositoryChangeList changes({
        {101, "Add validation"},
        {102, "Add audit event"},
        {103, "Add policy test"},
        {104, "Fix merge condition"}
    });

    changes.print("Original changeset");
    changes.reverseIterative();
    changes.validate();
    changes.print("Iteratively reversed");
}

void runRecursiveScenario() {
    std::cout << "\n=== Recursive pointer reversal ===\n";

    RepositoryChangeList changes({
        {201, "Parser update"},
        {202, "Review comment fix"},
        {203, "Status check update"},
        {204, "Documentation change"}
    });

    changes.print("Original");
    changes.reverseRecursive();
    changes.validate();
    changes.print("Recursively reversed");
}

void runGroupScenario() {
    std::cout << "\n=== Commit-window grouping scenario ===\n";

    std::vector<std::pair<int, std::string>> data = {
        {301, "schema"},
        {302, "index"},
        {303, "constraint"},
        {304, "query"},
        {305, "test"},
        {306, "cleanup"},
        {307, "audit"}
    };

    const std::size_t k = 3;

    RepositoryChangeList changes(data);
    changes.print("Original");

    changes.reverseInGroups(k);
    changes.validate();
    changes.print("Groups of three reversed");

    std::vector<int> ids;
    for (const auto& [id, unused] : data) {
        ids.push_back(id);
    }

    verifyEqual(
        changes.ids(),
        expectedGroupReverse(ids, k),
        "Iterative group reversal"
    );
}

void runRandomizedTests() {
    std::cout << "\n=== Randomized pointer tests ===\n";

    std::mt19937 generator(20261005);
    std::uniform_int_distribution<int> lengthDistribution(0, 40);
    std::uniform_int_distribution<int> valueDistribution(-500, 500);
    std::uniform_int_distribution<int> groupDistribution(1, 10);

    for (int test = 0; test < 500; ++test) {
        const int length = lengthDistribution(generator);

        std::vector<std::pair<int, std::string>> data;

        for (int i = 0; i < length; ++i) {
            data.emplace_back(
                i,
                "change-" + std::to_string(valueDistribution(generator))
            );
        }

        std::vector<int> original;
        for (const auto& [id, unused] : data) {
            original.push_back(id);
        }

        RepositoryChangeList iterative(data);
        iterative.reverseIterative();
        iterative.validate();

        verifyEqual(
            iterative.ids(),
            expectedReverse(original),
            "Random iterative reversal"
        );

        RepositoryChangeList recursive(data);
        recursive.reverseRecursive();
        recursive.validate();

        verifyEqual(
            recursive.ids(),
            expectedReverse(original),
            "Random recursive reversal"
        );

        const std::size_t k =
            static_cast<std::size_t>(groupDistribution(generator));

        RepositoryChangeList grouped(data);
        grouped.reverseInGroups(k);
        grouped.validate();

        verifyEqual(
            grouped.ids(),
            expectedGroupReverse(original, k),
            "Random group reversal"
        );
    }

    std::cout << "500 randomized cases passed.\n";
}

void explainAlgorithmicTradeoffs() {
    std::cout << "\n=== Algorithmic trade-offs ===\n";
    std::cout << "Iterative reversal: O(n) time, O(1) auxiliary space.\n";
    std::cout << "Recursive reversal: O(n) time, O(n) stack space.\n";
    std::cout << "Iterative k-groups: O(n) time, O(1) auxiliary space.\n";
    std::cout << "Recursive k-groups: O(n) time, O(n/k) stack frames.\n";
    std::cout
        << "Pointer reversal changes links rather than copying payload objects.\n";
}

int main() {
    try {
        runBasicScenario();
        runRecursiveScenario();
        runGroupScenario();
        runRandomizedTests();
        explainAlgorithmicTradeoffs();

        std::cout << "\nAll C++17 linked-list reversal checks passed.\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Failure: " << error.what() << '\n';
        return 1;
    }
}
