/*
 * Queue Introduction
 *
 * A C++17 case study for a repository build-service queue.
 *
 * The system models jobs waiting for a build worker. Jobs enter at the rear
 * and are processed from the front, preserving FIFO behavior. The program
 * demonstrates both an array-backed circular queue and a linked queue, then
 * uses queue semantics in a small build scheduling workflow.
 */

#include <iostream>
#include <optional>
#include <stdexcept>
#include <string>
#include <vector>
#include <memory>
#include <unordered_set>
#include <functional>

// ---------------------------------------------------------------------------
// Array-backed circular queue
// ---------------------------------------------------------------------------

template <typename T>
class CircularQueue {
private:
    std::vector<std::optional<T>> storage_;
    std::size_t front_ = 0;
    std::size_t rear_ = 0;
    std::size_t size_ = 0;

public:
    explicit CircularQueue(std::size_t capacity)
        : storage_(capacity) {
        if (capacity == 0) {
            throw std::invalid_argument("Queue capacity must be positive");
        }
    }

    void enqueue(const T& value) {
        if (isFull()) {
            throw std::overflow_error("Queue is full");
        }

        storage_[rear_] = value;
        rear_ = (rear_ + 1) % storage_.size();
        ++size_;
    }

    T dequeue() {
        if (isEmpty()) {
            throw std::underflow_error("Cannot dequeue from an empty queue");
        }

        T value = *storage_[front_];
        storage_[front_].reset();
        front_ = (front_ + 1) % storage_.size();
        --size_;

        return value;
    }

    const T& peek() const {
        if (isEmpty()) {
            throw std::underflow_error("Cannot inspect an empty queue");
        }

        return *storage_[front_];
    }

    bool isEmpty() const {
        return size_ == 0;
    }

    bool isFull() const {
        return size_ == storage_.size();
    }

    std::size_t size() const {
        return size_;
    }

    std::vector<T> values() const {
        std::vector<T> result;
        result.reserve(size_);

        for (std::size_t offset = 0; offset < size_; ++offset) {
            const std::size_t index =
                (front_ + offset) % storage_.size();

            result.push_back(*storage_[index]);
        }

        return result;
    }
};

// ---------------------------------------------------------------------------
// Linked queue
// ---------------------------------------------------------------------------

template <typename T>
class LinkedQueue {
private:
    struct Node {
        T value;
        std::unique_ptr<Node> next;

        explicit Node(const T& item)
            : value(item) {}
    };

    std::unique_ptr<Node> front_;
    Node* rear_ = nullptr;
    std::size_t size_ = 0;

public:
    void enqueue(const T& value) {
        auto newNode = std::make_unique<Node>(value);
        Node* newRear = newNode.get();

        if (!rear_) {
            front_ = std::move(newNode);
        } else {
            rear_->next = std::move(newNode);
        }

        rear_ = newRear;
        ++size_;
    }

    T dequeue() {
        if (!front_) {
            throw std::underflow_error("Cannot dequeue from an empty queue");
        }

        T value = front_->value;
        front_ = std::move(front_->next);
        --size_;

        if (!front_) {
            rear_ = nullptr;
        }

        return value;
    }

    const T& peek() const {
        if (!front_) {
            throw std::underflow_error("Cannot inspect an empty queue");
        }

        return front_->value;
    }

    bool isEmpty() const {
        return front_ == nullptr;
    }

    std::size_t size() const {
        return size_;
    }
};

// ---------------------------------------------------------------------------
// Repository build domain
// ---------------------------------------------------------------------------

enum class BuildStatus {
    Queued,
    Running,
    Passed,
    Failed
};

struct BuildJob {
    std::string id;
    std::string pullRequest;
    std::string branch;
    int priority;
    BuildStatus status;
};

std::string statusName(BuildStatus status) {
    switch (status) {
        case BuildStatus::Queued:
            return "Queued";
        case BuildStatus::Running:
            return "Running";
        case BuildStatus::Passed:
            return "Passed";
        case BuildStatus::Failed:
            return "Failed";
    }

    return "Unknown";
}

// ---------------------------------------------------------------------------
// Build scheduler
// ---------------------------------------------------------------------------

class BuildScheduler {
private:
    CircularQueue<BuildJob> queue_;
    std::unordered_set<std::string> jobIds_;

public:
    explicit BuildScheduler(std::size_t capacity)
        : queue_(capacity) {}

    void submit(BuildJob job) {
        if (job.id.empty()) {
            throw std::invalid_argument("Build job ID cannot be empty");
        }

        if (job.pullRequest.empty()) {
            throw std::invalid_argument(
                "Build job must reference a Pull Request");
        }

        if (job.branch.empty()) {
            throw std::invalid_argument(
                "Build job must reference a source branch");
        }

        if (!jobIds_.insert(job.id).second) {
            throw std::invalid_argument(
                "Build job ID already exists: " + job.id);
        }

        try {
            queue_.enqueue(job);
        } catch (...) {
            // Keep the ID registry consistent if capacity validation fails.
            jobIds_.erase(job.id);
            throw;
        }
    }

    BuildJob processNext(
        const std::function<bool(const BuildJob&)>& buildFunction) {

        BuildJob job = queue_.dequeue();

        job.status = BuildStatus::Running;
        std::cout << "Running " << job.id
                  << " for " << job.pullRequest << '\n';

        const bool passed = buildFunction(job);
        job.status = passed
            ? BuildStatus::Passed
            : BuildStatus::Failed;

        jobIds_.erase(job.id);
        return job;
    }

    bool empty() const {
        return queue_.isEmpty();
    }
};

// ---------------------------------------------------------------------------
// Demonstrations
// ---------------------------------------------------------------------------

void demonstrateFifo() {
    std::cout << "\n=== FIFO Queue ===\n";

    CircularQueue<std::string> queue(4);

    queue.enqueue("build-A");
    queue.enqueue("build-B");
    queue.enqueue("build-C");

    std::cout << "Front: " << queue.peek() << '\n';
    std::cout << "Dequeued: " << queue.dequeue() << '\n';

    // The rear wraps around after the physical end of the array.
    queue.enqueue("build-D");
    queue.enqueue("build-E");

    std::cout << "Logical queue: ";

    for (const auto& value : queue.values()) {
        std::cout << value << ' ';
    }

    std::cout << '\n';
}

void demonstrateLinkedQueue() {
    std::cout << "\n=== Linked Queue ===\n";

    LinkedQueue<std::string> queue;

    queue.enqueue("compile");
    queue.enqueue("test");
    queue.enqueue("package");

    while (!queue.isEmpty()) {
        std::cout << "Processing: " << queue.dequeue() << '\n';
    }

    try {
        queue.dequeue();
    } catch (const std::underflow_error& error) {
        std::cout << "Expected failure: " << error.what() << '\n';
    }
}

void demonstrateBuildScheduler() {
    std::cout << "\n=== Repository Build Scheduler ===\n";

    BuildScheduler scheduler(5);

    scheduler.submit({
        "JOB-100",
        "PR-41",
        "feature/payment-validation",
        1,
        BuildStatus::Queued
    });

    scheduler.submit({
        "JOB-101",
        "PR-42",
        "feature/audit-log",
        1,
        BuildStatus::Queued
    });

    scheduler.submit({
        "JOB-102",
        "PR-43",
        "fix/cache-timeout",
        1,
        BuildStatus::Queued
    });

    auto buildFunction = [](const BuildJob& job) {
        // This models a deterministic build result without invoking an
        // external compiler. Real infrastructure would execute CI commands.
        return job.pullRequest != "PR-42";
    };

    while (!scheduler.empty()) {
        BuildJob result = scheduler.processNext(buildFunction);

        std::cout << result.id
                  << " completed with status "
                  << statusName(result.status)
                  << '\n';
    }
}

void verifyInvariants() {
    std::cout << "\n=== Invariant Verification ===\n";

    CircularQueue<int> queue(3);

    if (!queue.isEmpty()) {
        throw std::runtime_error("New queue must be empty");
    }

    queue.enqueue(10);
    queue.enqueue(20);
    queue.enqueue(30);

    if (!queue.isFull()) {
        throw std::runtime_error("Queue should be full");
    }

    if (queue.dequeue() != 10 || queue.dequeue() != 20) {
        throw std::runtime_error("FIFO order was violated");
    }

    queue.enqueue(40);

    const auto values = queue.values();

    if (values.size() != 2 ||
        values[0] != 30 ||
        values[1] != 40) {
        throw std::runtime_error("Circular wrap-around failed");
    }

    if (queue.dequeue() != 30 || queue.dequeue() != 40) {
        throw std::runtime_error("FIFO order failed after wrap-around");
    }

    if (!queue.isEmpty()) {
        throw std::runtime_error("Queue should be empty");
    }

    std::cout << "All invariants passed.\n";
}

int main() {
    try {
        demonstrateFifo();
        demonstrateLinkedQueue();
        demonstrateBuildScheduler();
        verifyInvariants();

        std::cout << "\nComplexity:\n";
        std::cout << "Circular enqueue: O(1)\n";
        std::cout << "Circular dequeue: O(1)\n";
        std::cout << "Linked enqueue:   O(1)\n";
        std::cout << "Linked dequeue:   O(1)\n";
        std::cout << "Array storage:    O(n) memory\n";
        std::cout << "Linked storage:   O(n) memory plus node allocation overhead\n";
    }
    catch (const std::exception& error) {
        std::cerr << "Fatal queue error: "
                  << error.what() << '\n';
        return 1;
    }

    return 0;
}
