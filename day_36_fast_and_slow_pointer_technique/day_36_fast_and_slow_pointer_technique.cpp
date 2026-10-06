#include <algorithm>
#include <cassert>
#include <chrono>
#include <cstddef>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

class LinkedList {
public:
    struct Node {
        int value;
        Node* next;

        explicit Node(int value) : value(value), next(nullptr) {}
    };

private:
    std::vector<std::unique_ptr<Node>> storage_;
    Node* head_ = nullptr;

public:
    LinkedList() = default;

    explicit LinkedList(const std::vector<int>& values) {
        for (int value : values) {
            append(value);
        }
    }

    LinkedList(const LinkedList&) = delete;
    LinkedList& operator=(const LinkedList&) = delete;

    Node* head() const {
        return head_;
    }

    Node* append(int value) {
        storage_.push_back(std::make_unique<Node>(value));
        Node* newNode = storage_.back().get();

        if (head_ == nullptr) {
            head_ = newNode;
            return newNode;
        }

        Node* current = head_;

        while (current->next != nullptr) {
            current = current->next;
        }

        current->next = newNode;
        return newNode;
    }

    Node* nodeAt(std::size_t index) const {
        Node* current = head_;

        for (std::size_t i = 0; current != nullptr && i < index; ++i) {
            current = current->next;
        }

        return current;
    }

    void createCycle(std::size_t entryIndex) {
        if (head_ == nullptr) {
            throw std::logic_error("Cannot create a cycle in an empty list");
        }

        Node* entry = nodeAt(entryIndex);

        if (entry == nullptr) {
            throw std::out_of_range("Cycle entry is outside the list");
        }

        Node* tail = head_;

        while (tail->next != nullptr) {
            tail = tail->next;
        }

        tail->next = entry;
    }
};

struct CycleAnalysis {
    LinkedList::Node* meeting = nullptr;
    LinkedList::Node* entry = nullptr;
    std::size_t distanceToEntry = 0;
    std::size_t cycleLength = 0;
    bool hasCycle = false;
};

LinkedList::Node* middleNode(LinkedList::Node* head) {
    LinkedList::Node* slow = head;
    LinkedList::Node* fast = head;

    while (fast != nullptr && fast->next != nullptr) {
        slow = slow->next;
        fast = fast->next->next;
    }

    return slow;
}

LinkedList::Node* firstMiddleNode(LinkedList::Node* head) {
    if (head == nullptr) {
        return nullptr;
    }

    LinkedList::Node* slow = head;
    LinkedList::Node* fast = head->next;

    while (fast != nullptr && fast->next != nullptr) {
        slow = slow->next;
        fast = fast->next->next;
    }

    return slow;
}

LinkedList::Node* findMeetingNode(LinkedList::Node* head) {
    LinkedList::Node* slow = head;
    LinkedList::Node* fast = head;

    while (fast != nullptr && fast->next != nullptr) {
        slow = slow->next;
        fast = fast->next->next;

        if (slow == fast) {
            return slow;
        }
    }

    return nullptr;
}

LinkedList::Node* findCycleEntry(LinkedList::Node* head) {
    LinkedList::Node* meeting = findMeetingNode(head);

    if (meeting == nullptr) {
        return nullptr;
    }

    LinkedList::Node* fromHead = head;
    LinkedList::Node* fromMeeting = meeting;

    while (fromHead != fromMeeting) {
        fromHead = fromHead->next;
        fromMeeting = fromMeeting->next;
    }

    return fromHead;
}

CycleAnalysis analyzeCycle(LinkedList::Node* head) {
    CycleAnalysis analysis;
    analysis.meeting = findMeetingNode(head);

    if (analysis.meeting == nullptr) {
        return analysis;
    }

    analysis.hasCycle = true;
    analysis.entry = findCycleEntry(head);

    LinkedList::Node* current = head;

    while (current != analysis.entry) {
        ++analysis.distanceToEntry;
        current = current->next;
    }

    analysis.cycleLength = 1;
    current = analysis.entry->next;

    while (current != analysis.entry) {
        ++analysis.cycleLength;
        current = current->next;
    }

    return analysis;
}

bool removeCycle(LinkedList::Node* head) {
    LinkedList::Node* entry = findCycleEntry(head);

    if (entry == nullptr) {
        return false;
    }

    LinkedList::Node* cycleTail = entry;

    while (cycleTail->next != entry) {
        cycleTail = cycleTail->next;
    }

    cycleTail->next = nullptr;
    return true;
}

LinkedList::Node* nthFromEnd(LinkedList::Node* head, std::size_t n) {
    if (n == 0) {
        throw std::invalid_argument("n must be positive");
    }

    LinkedList::Node* fast = head;

    for (std::size_t i = 0; i < n; ++i) {
        if (fast == nullptr) {
            return nullptr;
        }

        fast = fast->next;
    }

    LinkedList::Node* slow = head;

    while (fast != nullptr) {
        slow = slow->next;
        fast = fast->next;
    }

    return slow;
}

LinkedList::Node* reverseList(LinkedList::Node* head) {
    LinkedList::Node* previous = nullptr;
    LinkedList::Node* current = head;

    while (current != nullptr) {
        LinkedList::Node* following = current->next;
        current->next = previous;
        previous = current;
        current = following;
    }

    return previous;
}

bool isPalindrome(LinkedList::Node* head) {
    if (head == nullptr || head->next == nullptr) {
        return true;
    }

    LinkedList::Node* slow = head;
    LinkedList::Node* fast = head;

    while (fast != nullptr && fast->next != nullptr) {
        slow = slow->next;
        fast = fast->next->next;
    }

    LinkedList::Node* secondHalf = reverseList(slow);
    LinkedList::Node* right = secondHalf;
    LinkedList::Node* left = head;

    bool palindrome = true;

    while (right != nullptr) {
        if (left->value != right->value) {
            palindrome = false;
            break;
        }

        left = left->next;
        right = right->next;
    }

    reverseList(secondHalf);
    return palindrome;
}

LinkedList::Node* intersectionNode(
    LinkedList::Node* headA,
    LinkedList::Node* headB
) {
    LinkedList::Node* a = headA;
    LinkedList::Node* b = headB;

    while (a != b) {
        a = (a == nullptr) ? headB : a->next;
        b = (b == nullptr) ? headA : b->next;
    }

    return a;
}

int findDuplicateFloyd(const std::vector<int>& values) {
    const std::size_t n = values.size() - 1;

    if (values.size() < 2) {
        throw std::invalid_argument("At least two values are required");
    }

    for (int value : values) {
        if (value < 1 || static_cast<std::size_t>(value) > n) {
            throw std::invalid_argument("Values must be within 1..n");
        }
    }

    /*
     * The array represents a directed functional graph:
     *     index -> values[index]
     *
     * Because n+1 values are constrained to 1..n, a duplicate forces a
     * repeated vertex and therefore a cycle.
     */
    int slow = values[0];
    int fast = values[values[0]];

    while (slow != fast) {
        slow = values[slow];
        fast = values[values[fast]];
    }

    int finder = 0;

    while (finder != slow) {
        finder = values[finder];
        slow = values[slow];
    }

    return finder;
}

std::string linearRepresentation(LinkedList::Node* head) {
    std::string result;
    LinkedList::Node* current = head;

    while (current != nullptr) {
        if (!result.empty()) {
            result += " -> ";
        }

        result += std::to_string(current->value);
        current = current->next;
    }

    return result;
}

void demonstrateRepositoryEventStream() {
    /*
     * This is a technical case study for a stream of repository events.
     *
     * A producer writes event nodes sequentially. The monitoring service does
     * not need to retain a hash set of every node just to determine whether
     * the event chain has accidentally formed a cycle. Floyd's algorithm can
     * detect the structural problem using constant auxiliary pointer state.
     */
    LinkedList eventStream({101, 102, 103, 104, 105, 106, 107});
    eventStream.createCycle(3);

    CycleAnalysis analysis = analyzeCycle(eventStream.head());

    std::cout << "\nEVENT STREAM INTEGRITY CASE STUDY\n";
    std::cout << "Cycle detected: " << std::boolalpha << analysis.hasCycle << '\n';
    std::cout << "Meeting event: "
              << analysis.meeting->value << '\n';
    std::cout << "Cycle entry event: "
              << analysis.entry->value << '\n';
    std::cout << "Prefix length: "
              << analysis.distanceToEntry << '\n';
    std::cout << "Cycle length: "
              << analysis.cycleLength << '\n';

    bool removed = removeCycle(eventStream.head());

    std::cout << "Cycle removed: " << removed << '\n';
    std::cout << "Linear stream: "
              << linearRepresentation(eventStream.head()) << '\n';
}

void demonstrateMiddleAndGapPatterns() {
    LinkedList list({10, 20, 30, 40, 50, 60});

    LinkedList::Node* secondMiddle = middleNode(list.head());
    LinkedList::Node* firstMiddle = firstMiddleNode(list.head());

    std::cout << "\nMIDDLE ELEMENT CASE STUDY\n";
    std::cout << "First middle: " << firstMiddle->value << '\n';
    std::cout << "Second middle: " << secondMiddle->value << '\n';

    LinkedList::Node* thirdFromEnd = nthFromEnd(list.head(), 3);

    std::cout << "Third from end: "
              << thirdFromEnd->value << '\n';
}

void demonstratePalindrome() {
    std::cout << "\nPALINDROME CASE STUDY\n";

    LinkedList odd({1, 2, 3, 2, 1});
    LinkedList even({4, 8, 8, 4});
    LinkedList invalid({1, 2, 3, 4});

    std::cout << "Odd palindrome: "
              << isPalindrome(odd.head()) << '\n';

    std::cout << "Even palindrome: "
              << isPalindrome(even.head()) << '\n';

    std::cout << "Non-palindrome: "
              << isPalindrome(invalid.head()) << '\n';
}

void demonstrateDuplicateDetection() {
    std::cout << "\nFUNCTIONAL GRAPH DUPLICATE DETECTION\n";

    std::vector<std::vector<int>> examples = {
        {1, 3, 4, 2, 2},
        {3, 1, 3, 4, 2},
        {1, 1},
        {2, 2, 2, 2, 2}
    };

    for (const auto& values : examples) {
        std::cout << "Duplicate in [";

        for (std::size_t i = 0; i < values.size(); ++i) {
            if (i > 0) {
                std::cout << ", ";
            }

            std::cout << values[i];
        }

        std::cout << "]: " << findDuplicateFloyd(values) << '\n';
    }
}

void runAssertions() {
    LinkedList empty;
    assert(middleNode(empty.head()) == nullptr);
    assert(!analyzeCycle(empty.head()).hasCycle);

    LinkedList list({1, 2, 3, 4});
    assert(middleNode(list.head())->value == 3);
    assert(firstMiddleNode(list.head())->value == 2);
    assert(nthFromEnd(list.head(), 1)->value == 4);
    assert(nthFromEnd(list.head(), 4)->value == 1);
    assert(nthFromEnd(list.head(), 5) == nullptr);

    LinkedList cyclic({1, 2, 3, 4, 5});
    cyclic.createCycle(2);

    CycleAnalysis analysis = analyzeCycle(cyclic.head());

    assert(analysis.hasCycle);
    assert(analysis.entry->value == 3);
    assert(analysis.distanceToEntry == 2);
    assert(analysis.cycleLength == 3);

    assert(removeCycle(cyclic.head()));
    assert(!analyzeCycle(cyclic.head()).hasCycle);

    LinkedList palindrome({1, 2, 3, 2, 1});
    assert(isPalindrome(palindrome.head()));

    LinkedList notPalindrome({1, 2, 3});
    assert(!isPalindrome(notPalindrome.head()));

    assert(findDuplicateFloyd({1, 3, 4, 2, 2}) == 2);
    assert(findDuplicateFloyd({3, 1, 3, 4, 2}) == 3);

    std::cout << "\nALL C++ ASSERTIONS PASSED\n";
}

int main() {
    try {
        std::cout << "FAST AND SLOW POINTER TECHNIQUE\n";
        std::cout << "========================================\n";

        demonstrateRepositoryEventStream();
        demonstrateMiddleAndGapPatterns();
        demonstratePalindrome();
        demonstrateDuplicateDetection();
        runAssertions();

        /*
         * Floyd's algorithm never needs a container proportional to the
         * number of nodes. That is the primary systems-level trade-off:
         * pointer state is constant, but the algorithm requires a structure
         * whose next relationship can be followed safely.
         */
        std::cout << "\nCOMPLEXITY\n";
        std::cout << "Middle node: O(n) time, O(1) auxiliary space\n";
        std::cout << "Cycle detection: O(n) time, O(1) auxiliary space\n";
        std::cout << "Cycle entry: O(n) time, O(1) auxiliary space\n";
        std::cout << "Cycle removal: O(n) time, O(1) auxiliary space\n";
        std::cout << "Nth from end: O(n) time, O(1) auxiliary space\n";
        std::cout << "Palindrome: O(n) time, O(1) auxiliary space\n";
        std::cout << "Duplicate detection: O(n) time, O(1) auxiliary space\n";

        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Execution error: " << error.what() << '\n';
        return 1;
    }
}
