#include <algorithm>
#include <cassert>
#include <cstddef>
#include <iostream>
#include <limits>
#include <queue>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <utility>
#include <vector>

using namespace std;

enum class HeapMode {
    Min,
    Max
};

class BinaryHeap {
private:
    vector<int> data;
    HeapMode mode;

    bool higherPriority(int a, int b) const {
        return mode == HeapMode::Min ? a < b : a > b;
    }

    void siftUp(size_t index) {
        while (index > 0) {
            size_t parent = (index - 1) / 2;

            if (!higherPriority(data[index], data[parent])) {
                break;
            }

            swap(data[index], data[parent]);
            index = parent;
        }
    }

    void siftDown(size_t index) {
        const size_t n = data.size();

        while (true) {
            size_t left = 2 * index + 1;
            size_t right = 2 * index + 2;
            size_t best = index;

            if (
                left < n &&
                higherPriority(data[left], data[best])
            ) {
                best = left;
            }

            if (
                right < n &&
                higherPriority(data[right], data[best])
            ) {
                best = right;
            }

            if (best == index) {
                break;
            }

            swap(data[index], data[best]);
            index = best;
        }
    }

public:
    explicit BinaryHeap(HeapMode heapMode = HeapMode::Min)
        : mode(heapMode) {}

    BinaryHeap(
        const vector<int>& values,
        HeapMode heapMode = HeapMode::Min
    ) : data(values), mode(heapMode) {
        heapify();
    }

    void heapify() {
        for (int i = static_cast<int>(data.size()) / 2 - 1;
             i >= 0; --i) {
            siftDown(static_cast<size_t>(i));
        }
    }

    void insert(int value) {
        data.push_back(value);
        siftUp(data.size() - 1);
    }

    int peek() const {
        if (data.empty()) {
            throw underflow_error("Cannot peek into empty heap.");
        }

        return data.front();
    }

    int extract() {
        if (data.empty()) {
            throw underflow_error("Cannot extract from empty heap.");
        }

        int result = data.front();
        data.front() = data.back();
        data.pop_back();

        if (!data.empty()) {
            siftDown(0);
        }

        return result;
    }

    int deleteAt(size_t index) {
        if (index >= data.size()) {
            throw out_of_range("Heap index out of range.");
        }

        int removed = data[index];
        data[index] = data.back();
        data.pop_back();

        if (index < data.size()) {
            if (
                index > 0 &&
                higherPriority(
                    data[index],
                    data[(index - 1) / 2]
                )
            ) {
                siftUp(index);
            } else {
                siftDown(index);
            }
        }

        return removed;
    }

    bool deleteValue(int value) {
        auto it = find(data.begin(), data.end(), value);

        if (it == data.end()) {
            return false;
        }

        deleteAt(static_cast<size_t>(
            distance(data.begin(), it)
        ));

        return true;
    }

    void update(size_t index, int value) {
        if (index >= data.size()) {
            throw out_of_range("Heap index out of range.");
        }

        int oldValue = data[index];
        data[index] = value;

        if (higherPriority(value, oldValue)) {
            siftUp(index);
        } else {
            siftDown(index);
        }
    }

    bool isValid() const {
        for (size_t i = 1; i < data.size(); ++i) {
            size_t parent = (i - 1) / 2;

            if (higherPriority(data[i], data[parent])) {
                return false;
            }
        }

        return true;
    }

    vector<int> sortedValues() const {
        BinaryHeap copy = *this;
        vector<int> result;

        while (!copy.empty()) {
            result.push_back(copy.extract());
        }

        return result;
    }

    bool empty() const {
        return data.empty();
    }

    size_t size() const {
        return data.size();
    }

    const vector<int>& values() const {
        return data;
    }
};

struct Task {
    string id;
    string description;
    int priority;
    unsigned long long sequence;
};

struct TaskComparator {
    bool operator()(const Task& a, const Task& b) const {
        if (a.priority != b.priority) {
            return a.priority < b.priority;
        }

        // Earlier sequence numbers have higher priority.
        return a.sequence > b.sequence;
    }
};

class TaskScheduler {
private:
    priority_queue<
        Task,
        vector<Task>,
        TaskComparator
    > tasks;

    unordered_set<string> activeIds;
    unsigned long long nextSequence = 0;

public:
    void submit(
        const string& id,
        const string& description,
        int priority
    ) {
        if (id.empty() || description.empty()) {
            throw invalid_argument(
                "Task ID and description are required."
            );
        }

        if (!activeIds.insert(id).second) {
            throw invalid_argument(
                "Duplicate active task ID."
            );
        }

        tasks.push({
            id,
            description,
            priority,
            nextSequence++
        });
    }

    Task next() const {
        if (tasks.empty()) {
            throw underflow_error("No scheduled tasks.");
        }

        return tasks.top();
    }

    Task process() {
        if (tasks.empty()) {
            throw underflow_error("No tasks to process.");
        }

        Task result = tasks.top();
        tasks.pop();

        activeIds.erase(result.id);

        return result;
    }

    bool empty() const {
        return tasks.empty();
    }

    size_t size() const {
        return tasks.size();
    }
};

vector<int> heapSort(
    const vector<int>& values,
    bool descending = false
) {
    BinaryHeap heap(
        values,
        descending ? HeapMode::Max : HeapMode::Min
    );

    return heap.sortedValues();
}

void printVector(const vector<int>& values) {
    for (int value : values) {
        cout << value << " ";
    }

    cout << '\n';
}

void demonstrate() {
    cout << "MIN HEAP\n";

    BinaryHeap minHeap(
        {40, 10, 30, 5, 20, 50},
        HeapMode::Min
    );

    cout << "Initial heap: ";
    printVector(minHeap.values());

    cout << "Minimum: " << minHeap.peek() << '\n';
    cout << "Extracted: " << minHeap.extract() << '\n';

    minHeap.insert(2);
    minHeap.deleteValue(30);

    cout << "After modifications: ";
    printVector(minHeap.values());

    cout << "Valid: " << boolalpha
         << minHeap.isValid() << '\n';

    cout << "\nMAX HEAP\n";

    BinaryHeap maxHeap(
        {40, 10, 30, 5, 20, 50},
        HeapMode::Max
    );

    cout << "Maximum: " << maxHeap.extract() << '\n';

    cout << "\nHEAP SORT\n";

    vector<int> values = {12, 4, 19, 1, 8, 15, 3};

    cout << "Ascending: ";
    printVector(heapSort(values));

    cout << "Descending: ";
    printVector(heapSort(values, true));

    cout << "\nTASK SCHEDULER\n";

    TaskScheduler scheduler;

    scheduler.submit("T101", "Database backup", 3);
    scheduler.submit("T102", "Security incident", 10);
    scheduler.submit("T103", "System monitoring", 5);
    scheduler.submit("T104", "Critical outage", 10);

    while (!scheduler.empty()) {
        Task task = scheduler.process();

        cout << "Processing " << task.id
             << " | " << task.description
             << " | Priority " << task.priority
             << '\n';
    }
}

void runTests() {
    BinaryHeap minHeap(
        {9, 4, 7, 1, 3},
        HeapMode::Min
    );

    assert(minHeap.isValid());
    assert(minHeap.extract() == 1);
    assert(minHeap.isValid());

    BinaryHeap maxHeap(
        {9, 4, 7, 1, 3},
        HeapMode::Max
    );

    assert(maxHeap.extract() == 9);

    BinaryHeap heap({5, 10, 15});
    heap.update(2, 1);
    assert(heap.peek() == 1);

    assert(heap.deleteValue(10));
    assert(!heap.deleteValue(100));
    assert(heap.isValid());

    assert(
        heapSort({8, 3, 5, 1}) ==
        vector<int>({1, 3, 5, 8})
    );

    BinaryHeap emptyHeap;

    bool exceptionRaised = false;

    try {
        emptyHeap.extract();
    } catch (const underflow_error&) {
        exceptionRaised = true;
    }

    assert(exceptionRaised);

    TaskScheduler scheduler;

    scheduler.submit("A", "Normal", 1);
    scheduler.submit("B", "Critical", 10);

    assert(scheduler.process().id == "B");

    cout << "\nAll C++17 tests passed.\n";
}

int main() {
    try {
        runTests();
        demonstrate();
    } catch (const exception& error) {
        cerr << "Error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
