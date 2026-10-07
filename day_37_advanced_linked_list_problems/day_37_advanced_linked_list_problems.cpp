#include <algorithm>
#include <cassert>
#include <iostream>
#include <random>
#include <sstream>
#include <string>
#include <unordered_set>
#include <utility>
#include <vector>

class RepositoryListNode {
public:
    int value;
    RepositoryListNode* next;

    explicit RepositoryListNode(int value)
        : value(value), next(nullptr) {}
};

/*
 * Case study:
 *
 * A data-processing service stores ordered event identifiers in singly
 * linked lists. Two processing streams can converge on the same physical
 * nodes after a shared event. The system also receives sorted batches,
 * unsorted recovery batches, and occasionally multilevel event structures.
 *
 * The implementation concentrates on pointer ownership and identity rather
 * than treating a linked list as an array.
 */

RepositoryListNode* buildList(const std::vector<int>& values) {
    RepositoryListNode* head = nullptr;
    RepositoryListNode* tail = nullptr;

    for (int value : values) {
        auto* node = new RepositoryListNode(value);

        if (head == nullptr) {
            head = node;
        } else {
            tail->next = node;
        }

        tail = node;
    }

    return head;
}

void printList(const std::string& label, const RepositoryListNode* head) {
    std::cout << label << ": ";

    const RepositoryListNode* current = head;
    std::size_t steps = 0;

    /*
     * The limit protects diagnostic output from an accidental cycle.
     * Normal algorithms should not silently assume that arbitrary input
     * is acyclic.
     */
    while (current != nullptr && steps < 100) {
        if (steps > 0) {
            std::cout << " -> ";
        }

        std::cout << current->value;
        current = current->next;
        ++steps;
    }

    if (current != nullptr) {
        std::cout << " -> ...";
    }

    std::cout << '\n';
}

std::size_t listLength(const RepositoryListNode* head) {
    std::size_t result = 0;

    while (head != nullptr) {
        ++result;
        head = head->next;
    }

    return result;
}

RepositoryListNode* reverseList(RepositoryListNode* head) {
    RepositoryListNode* previous = nullptr;
    RepositoryListNode* current = head;

    while (current != nullptr) {
        RepositoryListNode* next = current->next;
        current->next = previous;
        previous = current;
        current = next;
    }

    return previous;
}

/*
 * Intersection is based on address identity.
 *
 * Two nodes containing the value 42 are not necessarily the same node.
 * A physical intersection exists only when both paths eventually point
 * to the same object.
 */
RepositoryListNode* findIntersection(
    RepositoryListNode* first,
    RepositoryListNode* second) {

    RepositoryListNode* a = first;
    RepositoryListNode* b = second;

    while (a != b) {
        a = (a == nullptr) ? second : a->next;
        b = (b == nullptr) ? first : b->next;
    }

    return a;
}

RepositoryListNode* mergeSortedLists(
    RepositoryListNode* first,
    RepositoryListNode* second) {

    RepositoryListNode dummy(0);
    RepositoryListNode* tail = &dummy;

    while (first != nullptr && second != nullptr) {
        if (first->value <= second->value) {
            tail->next = first;
            first = first->next;
        } else {
            tail->next = second;
            second = second->next;
        }

        tail = tail->next;
    }

    tail->next = (first != nullptr) ? first : second;
    return dummy.next;
}

std::pair<RepositoryListNode*, RepositoryListNode*>
splitList(RepositoryListNode* head) {
    if (head == nullptr || head->next == nullptr) {
        return {head, nullptr};
    }

    RepositoryListNode* slow = head;
    RepositoryListNode* fast = head->next;

    while (fast != nullptr && fast->next != nullptr) {
        slow = slow->next;
        fast = fast->next->next;
    }

    RepositoryListNode* second = slow->next;
    slow->next = nullptr;

    return {head, second};
}

RepositoryListNode* mergeSort(RepositoryListNode* head) {
    if (head == nullptr || head->next == nullptr) {
        return head;
    }

    auto [left, right] = splitList(head);

    left = mergeSort(left);
    right = mergeSort(right);

    return mergeSortedLists(left, right);
}

/*
 * Stable partition:
 *
 * The first chain receives nodes below the pivot and the second receives
 * nodes greater than or equal to it. Existing nodes are reused, so the
 * algorithm does not allocate an auxiliary array.
 */
RepositoryListNode* stablePartition(
    RepositoryListNode* head,
    int pivot) {

    RepositoryListNode lessDummy(0);
    RepositoryListNode greaterDummy(0);

    RepositoryListNode* lessTail = &lessDummy;
    RepositoryListNode* greaterTail = &greaterDummy;

    RepositoryListNode* current = head;

    while (current != nullptr) {
        RepositoryListNode* next = current->next;
        current->next = nullptr;

        if (current->value < pivot) {
            lessTail->next = current;
            lessTail = current;
        } else {
            greaterTail->next = current;
            greaterTail = current;
        }

        current = next;
    }

    lessTail->next = greaterDummy.next;
    return lessDummy.next;
}

RepositoryListNode* detectCycleEntry(RepositoryListNode* head) {
    RepositoryListNode* slow = head;
    RepositoryListNode* fast = head;

    while (fast != nullptr && fast->next != nullptr) {
        slow = slow->next;
        fast = fast->next->next;

        if (slow == fast) {
            slow = head;

            while (slow != fast) {
                slow = slow->next;
                fast = fast->next;
            }

            return slow;
        }
    }

    return nullptr;
}

RepositoryListNode* reverseKGroup(
    RepositoryListNode* head,
    std::size_t k) {

    if (head == nullptr || k <= 1) {
        return head;
    }

    RepositoryListNode dummy(0);
    dummy.next = head;

    RepositoryListNode* groupPrevious = &dummy;

    while (true) {
        RepositoryListNode* kth = groupPrevious;

        for (std::size_t i = 0; i < k; ++i) {
            kth = kth->next;

            if (kth == nullptr) {
                return dummy.next;
            }
        }

        RepositoryListNode* groupNext = kth->next;
        RepositoryListNode* previous = groupNext;
        RepositoryListNode* current = groupPrevious->next;

        while (current != groupNext) {
            RepositoryListNode* next = current->next;
            current->next = previous;
            previous = current;
            current = next;
        }

        RepositoryListNode* oldHead = groupPrevious->next;
        groupPrevious->next = kth;
        groupPrevious = oldHead;
    }
}

class RandomNode {
public:
    int value;
    RandomNode* next;
    RandomNode* random;

    explicit RandomNode(int value)
        : value(value), next(nullptr), random(nullptr) {}
};

/*
 * Deep-copy a random-pointer list using interleaving.
 *
 * The copied node is inserted directly after its source node. Therefore,
 * if original->random points to X, original->random->next is the copied
 * version of X.
 *
 * This avoids an unordered_map and demonstrates why pointer topology can
 * sometimes be exploited to reduce auxiliary space.
 */
RandomNode* copyRandomList(RandomNode* head) {
    if (head == nullptr) {
        return nullptr;
    }

    RandomNode* current = head;

    while (current != nullptr) {
        auto* copy = new RandomNode(current->value);
        copy->next = current->next;
        current->next = copy;
        current = copy->next;
    }

    current = head;

    while (current != nullptr) {
        RandomNode* copy = current->next;

        if (current->random != nullptr) {
            copy->random = current->random->next;
        }

        current = copy->next;
    }

    RandomNode* copiedHead = head->next;
    current = head;

    while (current != nullptr) {
        RandomNode* copy = current->next;
        RandomNode* originalNext = copy->next;

        current->next = originalNext;
        copy->next =
            (originalNext == nullptr) ? nullptr : originalNext->next;

        current = originalNext;
    }

    return copiedHead;
}

class MultiNode {
public:
    int value;
    MultiNode* prev;
    MultiNode* next;
    MultiNode* child;

    explicit MultiNode(int value)
        : value(value), prev(nullptr), next(nullptr), child(nullptr) {}
};

/*
 * Flatten a multilevel doubly linked list.
 *
 * A stack gives depth-first order without recursion. When a node has both
 * next and child, next is pushed first so that child is processed first.
 */
MultiNode* flatten(MultiNode* head) {
    if (head == nullptr) {
        return nullptr;
    }

    std::vector<MultiNode*> stack;
    stack.push_back(head);

    MultiNode* previous = nullptr;

    while (!stack.empty()) {
        MultiNode* current = stack.back();
        stack.pop_back();

        if (previous != nullptr) {
            previous->next = current;
            current->prev = previous;
        }

        if (current->next != nullptr) {
            stack.push_back(current->next);
        }

        if (current->child != nullptr) {
            stack.push_back(current->child);
            current->child = nullptr;
        }

        previous = current;
    }

    if (previous != nullptr) {
        previous->next = nullptr;
    }

    return head;
}

std::vector<int> valuesOf(const RepositoryListNode* head) {
    std::vector<int> values;

    while (head != nullptr) {
        values.push_back(head->value);
        head = head->next;
    }

    return values;
}

RandomNode* buildRandomExample() {
    std::vector<RandomNode*> nodes;

    for (int value : {7, 13, 11, 10, 1}) {
        nodes.push_back(new RandomNode(value));
    }

    for (std::size_t i = 0; i + 1 < nodes.size(); ++i) {
        nodes[i]->next = nodes[i + 1];
    }

    nodes[1]->random = nodes[0];
    nodes[2]->random = nodes[4];
    nodes[3]->random = nodes[2];
    nodes[4]->random = nodes[4];

    return nodes[0];
}

void printRandomList(const RandomNode* head) {
    while (head != nullptr) {
        std::cout << "(" << head->value << ", ";

        if (head->random != nullptr) {
            std::cout << head->random->value;
        } else {
            std::cout << "null";
        }

        std::cout << ")";

        if (head->next != nullptr) {
            std::cout << " -> ";
        }

        head = head->next;
    }

    std::cout << '\n';
}

MultiNode* buildMultilevelExample() {
    std::vector<MultiNode*> nodes;

    for (int value = 1; value <= 7; ++value) {
        nodes.push_back(new MultiNode(value));
    }

    for (int i = 0; i < 3; ++i) {
        nodes[i]->next = nodes[i + 1];
        nodes[i + 1]->prev = nodes[i];
    }

    nodes[1]->child = nodes[4];

    nodes[4]->next = nodes[5];
    nodes[5]->prev = nodes[4];

    nodes[5]->child = nodes[6];

    return nodes[0];
}

void printMultiList(const MultiNode* head) {
    while (head != nullptr) {
        std::cout << head->value;

        if (head->next != nullptr) {
            std::cout << " -> ";
        }

        head = head->next;
    }

    std::cout << '\n';
}

void randomizedSortVerification() {
    std::mt19937 generator(42);
    std::uniform_int_distribution<int> sizeDistribution(0, 25);
    std::uniform_int_distribution<int> valueDistribution(-50, 50);

    for (int trial = 0; trial < 100; ++trial) {
        int size = sizeDistribution(generator);
        std::vector<int> expected;

        for (int i = 0; i < size; ++i) {
            expected.push_back(valueDistribution(generator));
        }

        std::vector<int> actual = expected;

        RepositoryListNode* list = buildList(expected);
        list = mergeSort(list);

        std::sort(expected.begin(), expected.end());
        actual = valuesOf(list);

        assert(actual == expected);
    }

    std::cout << "Randomized merge-sort verification passed.\n";
}

int main() {
    std::cout << "=== Advanced Linked List Case Study ===\n\n";

    auto* shared = buildList({8, 10, 12});

    auto* first = buildList({3, 7});
    auto* firstTail = first;

    while (firstTail->next != nullptr) {
        firstTail = firstTail->next;
    }

    firstTail->next = shared;

    auto* second = buildList({99, 1, 5});
    auto* secondTail = second;

    while (secondTail->next != nullptr) {
        secondTail = secondTail->next;
    }

    secondTail->next = shared;

    RepositoryListNode* intersection = findIntersection(first, second);

    std::cout << "Physical intersection:\n";
    std::cout << "  value = "
              << (intersection == nullptr ? -1 : intersection->value)
              << '\n';
    std::cout << "  address identity = "
              << std::boolalpha
              << (intersection == shared)
              << "\n\n";

    auto* unsorted = buildList({7, 2, 9, 1, 5, 2, 8, 3});
    printList("Unsorted event batch", unsorted);

    unsorted = mergeSort(unsorted);
    printList("Sorted event batch", unsorted);
    std::cout << '\n';

    auto* sortedA = buildList({1, 4, 7, 10});
    auto* sortedB = buildList({2, 3, 8, 9});

    auto* merged = mergeSortedLists(sortedA, sortedB);
    printList("Merged sorted streams", merged);
    std::cout << '\n';

    auto* partitioned = buildList({1, 4, 3, 2, 5, 2});
    partitioned = stablePartition(partitioned, 3);
    printList("Stable partition around 3", partitioned);
    std::cout << '\n';

    auto* grouped = buildList({1, 2, 3, 4, 5, 6, 7});
    grouped = reverseKGroup(grouped, 3);
    printList("Reverse in groups of three", grouped);
    std::cout << '\n';

    RandomNode* randomOriginal = buildRandomExample();
    RandomNode* randomCopy = copyRandomList(randomOriginal);

    std::cout << "Random-pointer original:\n";
    printRandomList(randomOriginal);

    std::cout << "Random-pointer deep copy:\n";
    printRandomList(randomCopy);

    assert(randomOriginal != randomCopy);
    std::cout << '\n';

    MultiNode* multilevel = buildMultilevelExample();
    multilevel = flatten(multilevel);

    std::cout << "Flattened multilevel list:\n";
    printMultiList(multilevel);
    std::cout << '\n';

    auto* cyclic = buildList({1, 2, 3, 4, 5});
    RepositoryListNode* cycleEntry = cyclic->next->next;

    RepositoryListNode* cyclicTail = cyclic;
    while (cyclicTail->next != nullptr) {
        cyclicTail = cyclicTail->next;
    }

    cyclicTail->next = cycleEntry;

    RepositoryListNode* detected = detectCycleEntry(cyclic);

    std::cout << "Cycle detection entry value = "
              << (detected == nullptr ? -1 : detected->value)
              << "\n\n";

    randomizedSortVerification();

    /*
     * The program deliberately uses raw pointers because pointer identity
     * and link ownership are the subject of the case study. Production
     * ownership can be made safer with smart pointers, but shared-tail
     * intersection has different ownership semantics and must be modeled
     * carefully before replacing raw links with unique ownership.
     */

    std::cout << "\nAll linked-list demonstrations completed.\n";

    return 0;
}
