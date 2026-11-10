/*
 * HEAP INTRODUCTION
 *
 * C++17 implementation of:
 * - Complete binary trees
 * - Array-based min-heaps and max-heaps
 * - Heap insertion and extraction
 * - Bottom-up heap construction
 * - Heap validation
 * - Priority-based repository job scheduling
 * - Heap sorting
 * - Performance statistics
 *
 * Compile:
 * g++ -std=c++17 -O2 -Wall -Wextra -pedantic heap.cpp -o heap
 */

#include <algorithm>
#include <cassert>
#include <cstddef>
#include <iomanip>
#include <iostream>
#include <limits>
#include <queue>
#include <stdexcept>
#include <string>
#include <vector>

enum class HeapType {
    MIN,
    MAX
};

struct HeapStatistics {
    std::size_t insertions = 0;
    std::size_t removals = 0;
    std::size_t comparisons = 0;
    std::size_t swaps = 0;
};


template <typename T>
class BinaryHeap {
private:
    std::vector<T> data;
    HeapType type;
    HeapStatistics stats;

    bool higherPriority(const T& first, const T& second) {
        ++stats.comparisons;

        if (type == HeapType::MIN) {
            return first < second;
        }

        return first > second;
    }

    void exchange(std::size_t first, std::size_t second) {
        std::swap(data[first], data[second]);
        ++stats.swaps;
    }

    void siftUp(std::size_t index) {
        while (index > 0) {
            const std::size_t parent = (index - 1) / 2;

            if (!higherPriority(data[index], data[parent])) {
                break;
            }

            exchange(index, parent);
            index = parent;
        }
    }

    void siftDown(std::size_t index) {
        const std::size_t size = data.size();

        while (true) {
            std::size_t best = index;
            const std::size_t left = 2 * index + 1;
            const std::size_t right = 2 * index + 2;

            if (
                left < size &&
                higherPriority(data[left], data[best])
            ) {
                best = left;
            }

            if (
                right < size &&
                higherPriority(data[right], data[best])
            ) {
                best = right;
            }

            if (best == index) {
                break;
            }

            exchange(index, best);
            index = best;
        }
    }

public:
    explicit BinaryHeap(HeapType heapType = HeapType::MIN)
        : type(heapType) {}

    BinaryHeap(
        const std::vector<T>& values,
        HeapType heapType = HeapType::MIN
    )
        : data(values), type(heapType) {

        // The final non-leaf node is at index n/2 - 1.
        for (
            std::size_t i = data.size() / 2;
            i > 0;
            --i
        ) {
            siftDown(i - 1);
        }
    }

    std::size_t size() const {
        return data.size();
    }

    bool empty() const {
        return data.empty();
    }

    std::size_t parent(std::size_t index) const {
        if (index == 0 || index >= data.size()) {
            throw std::out_of_range("Invalid child index");
        }

        return (index - 1) / 2;
    }

    std::size_t leftChild(std::size_t index) const {
        if (index >= data.size()) {
            throw std::out_of_range("Invalid node index");
        }

        return 2 * index + 1;
    }

    std::size_t rightChild(std::size_t index) const {
        if (index >= data.size()) {
            throw std::out_of_range("Invalid node index");
        }

        return 2 * index + 2;
    }

    const T& peek() const {
        if (empty()) {
            throw std::underflow_error("Heap is empty");
        }

        return data.front();
    }

    void push(const T& value) {
        data.push_back(value);
        ++stats.insertions;

        siftUp(data.size() - 1);
    }

    T pop() {
        if (empty()) {
            throw std::underflow_error("Cannot pop empty heap");
        }

        T result = data.front();

        if (data.size() == 1) {
            data.pop_back();
            ++stats.removals;
            return result;
        }

        data.front() = std::move(data.back());
        data.pop_back();

        ++stats.removals;
        siftDown(0);

        return result;
    }

    T replaceRoot(const T& value) {
        if (empty()) {
            throw std::underflow_error("Cannot replace empty heap");
        }

        T previous = data.front();
        data.front() = value;
        siftDown(0);

        return previous;
    }

    bool validate() const {
        for (std::size_t i = 1; i < data.size(); ++i) {
            const std::size_t p = (i - 1) / 2;

            if (type == HeapType::MIN && data[i] < data[p]) {
                return false;
            }

            if (type == HeapType::MAX && data[i] > data[p]) {
                return false;
            }
        }

        return true;
    }

    void display() const {
        std::cout
            << "\n"
            << (type == HeapType::MIN ? "MIN-HEAP" : "MAX-HEAP")
            << "\nArray: ";

        for (const auto& value : data) {
            std::cout << value << " ";
        }

        std::cout << "\n";

        std::size_t index = 0;
        std::size_t width = 1;
        std::size_t level = 0;

        while (index < data.size()) {
            std::cout << "Level " << level++ << ": ";

            const std::size_t end = std::min(
                index + width,
                data.size()
            );

            for (; index < end; ++index) {
                std::cout << data[index] << " ";
            }

            std::cout << "\n";
            width *= 2;
        }
    }

    void displayStatistics() const {
        std::cout << "\nHEAP STATISTICS\n";
        std::cout << "Size: " << data.size() << "\n";
        std::cout << "Insertions: " << stats.insertions << "\n";
        std::cout << "Removals: " << stats.removals << "\n";
        std::cout << "Comparisons: " << stats.comparisons << "\n";
        std::cout << "Swaps: " << stats.swaps << "\n";
    }

    std::vector<T> underlyingArray() const {
        return data;
    }
};


struct RepositoryJob {
    int priority;
    int sequence;
    std::string repository;
    std::string operation;
};

struct JobComparator {
    bool operator()(
        const RepositoryJob& first,
        const RepositoryJob& second
    ) const {
        if (first.priority != second.priority) {
            return first.priority > second.priority;
        }

        return first.sequence > second.sequence;
    }
};


class RepositoryJobScheduler {
private:
    std::priority_queue<
        RepositoryJob,
        std::vector<RepositoryJob>,
        JobComparator
    > jobs;

    int nextSequence = 0;

public:
    void schedule(
        const std::string& repository,
        const std::string& operation,
        int priority
    ) {
        if (repository.empty() || operation.empty()) {
            throw std::invalid_argument("Job fields cannot be empty");
        }

        if (priority < 1 || priority > 10) {
            throw std::invalid_argument("Priority must be 1 through 10");
        }

        jobs.push({
            priority,
            nextSequence++,
            repository,
            operation
        });
    }

    RepositoryJob executeNext() {
        if (jobs.empty()) {
            throw std::underflow_error("No pending repository jobs");
        }

        RepositoryJob job = jobs.top();
        jobs.pop();

        return job;
    }

    bool empty() const {
        return jobs.empty();
    }

    std::size_t size() const {
        return jobs.size();
    }
};


template <typename T>
std::vector<T> heapSort(const std::vector<T>& values) {
    BinaryHeap<T> heap(values, HeapType::MIN);

    std::vector<T> result;
    result.reserve(values.size());

    while (!heap.empty()) {
        result.push_back(heap.pop());
    }

    return result;
}


void demonstrateCompleteBinaryTree() {
    std::cout << "\nCOMPLETE BINARY TREE\n";

    const std::vector<int> tree = {
        10, 20, 30, 40, 50, 60, 70
    };

    for (std::size_t i = 0; i < tree.size(); ++i) {
        std::cout << "Node: " << tree[i];

        if (i > 0) {
            std::cout << ", Parent: " << tree[(i - 1) / 2];
        }

        const std::size_t left = 2 * i + 1;
        const std::size_t right = 2 * i + 2;

        if (left < tree.size()) {
            std::cout << ", Left: " << tree[left];
        }

        if (right < tree.size()) {
            std::cout << ", Right: " << tree[right];
        }

        std::cout << "\n";
    }
}


void demonstrateHeaps() {
    const std::vector<int> values = {
        40, 10, 30, 50, 20, 60, 70
    };

    BinaryHeap<int> minHeap(values, HeapType::MIN);
    BinaryHeap<int> maxHeap(values, HeapType::MAX);

    minHeap.display();
    maxHeap.display();

    std::cout << "\nMinimum: " << minHeap.peek() << "\n";
    std::cout << "Maximum: " << maxHeap.peek() << "\n";

    minHeap.push(5);

    std::cout << "\nAfter inserting 5:\n";
    minHeap.display();

    std::cout << "Removed minimum: " << minHeap.pop() << "\n";

    std::cout << "Min-heap valid: "
              << std::boolalpha << minHeap.validate() << "\n";

    std::cout << "Max-heap valid: "
              << maxHeap.validate() << "\n";

    minHeap.displayStatistics();
}


void demonstrateScheduler() {
    RepositoryJobScheduler scheduler;

    scheduler.schedule("portfolio-api", "Run tests", 3);
    scheduler.schedule("security-engine", "Security audit", 1);
    scheduler.schedule("market-service", "Generate report", 7);
    scheduler.schedule("portfolio-api", "Production incident", 1);

    std::cout << "\nREPOSITORY JOB EXECUTION\n";

    while (!scheduler.empty()) {
        RepositoryJob job = scheduler.executeNext();

        std::cout
            << "Repository: " << job.repository
            << " | Operation: " << job.operation
            << " | Priority: " << job.priority
            << " | Sequence: " << job.sequence
            << "\n";
    }
}


void demonstrateEdgeCases() {
    std::cout << "\nEDGE CASES\n";

    BinaryHeap<int> emptyHeap;

    try {
        emptyHeap.pop();
    } catch (const std::underflow_error& error) {
        std::cout << "Expected error: " << error.what() << "\n";
    }

    BinaryHeap<int> single({42});
    std::cout << "Single element: " << single.pop() << "\n";

    BinaryHeap<int> duplicates(
        {5, 5, 5, 2, 2},
        HeapType::MIN
    );

    std::cout << "Duplicate values: ";

    while (!duplicates.empty()) {
        std::cout << duplicates.pop() << " ";
    }

    std::cout << "\n";

    BinaryHeap<int> negatives(
        {-10, -5, -20},
        HeapType::MAX
    );

    std::cout << "Maximum negative value: "
              << negatives.pop() << "\n";

    try {
        RepositoryJobScheduler scheduler;
        scheduler.schedule("repository", "Invalid task", 20);
    } catch (const std::invalid_argument& error) {
        std::cout << "Validation error: " << error.what() << "\n";
    }
}


void runTests() {
    BinaryHeap<int> minHeap(
        {9, 4, 7, 1, 3},
        HeapType::MIN
    );

    BinaryHeap<int> maxHeap(
        {9, 4, 7, 1, 3},
        HeapType::MAX
    );

    assert(minHeap.peek() == 1);
    assert(maxHeap.peek() == 9);

    minHeap.push(0);
    assert(minHeap.pop() == 0);

    assert(minHeap.validate());
    assert(maxHeap.validate());

    const auto sorted = heapSort(
        std::vector<int>{5, 1, 4, 2, 3}
    );

    assert(
        sorted == std::vector<int>({1, 2, 3, 4, 5})
    );

    assert(heapSort(std::vector<int>{}).empty());

    std::cout << "\nAll assertions passed.\n";
}


int main() {
    try {
        std::cout << "HEAP INTRODUCTION\n";
        std::cout << "=================\n";

        demonstrateCompleteBinaryTree();
        demonstrateHeaps();
        demonstrateScheduler();
        demonstrateEdgeCases();
        runTests();

        const std::vector<int> values = {
            12, 4, 19, 1, 8, 3, 15
        };

        const auto sorted = heapSort(values);

        std::cout << "\nHEAP SORT\n";

        for (int value : sorted) {
            std::cout << value << " ";
        }

        std::cout << "\n";

    } catch (const std::exception& error) {
        std::cerr << "Application error: "
                  << error.what() << "\n";

        return 1;
    }

    return 0;
}
