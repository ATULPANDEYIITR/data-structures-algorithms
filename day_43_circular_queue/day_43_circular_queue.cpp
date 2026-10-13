#include <algorithm>
#include <cstddef>
#include <exception>
#include <iomanip>
#include <iostream>
#include <optional>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

class QueueFullException : public std::runtime_error {
public:
    explicit QueueFullException(const std::string& message)
        : std::runtime_error(message) {}
};

class QueueEmptyException : public std::runtime_error {
public:
    explicit QueueEmptyException(const std::string& message)
        : std::runtime_error(message) {}
};

/*
 * Repository Governance Case Study
 *
 * A bounded circular queue is used here as a merge-event processing buffer.
 * Repository events arrive faster than the governance service can evaluate
 * them. The queue provides FIFO ordering while preventing unbounded memory
 * growth.
 *
 * The example deliberately connects the queue mechanism to a realistic system:
 * pull-request events are accepted, processed, and removed from reusable
 * buffer slots.
 */

enum class PullRequestState {
    Draft,
    Open,
    Closed,
    Merged
};

enum class ReviewState {
    Commented,
    ChangesRequested,
    Approved,
    Dismissed
};

struct PullRequestEvent {
    long id;
    std::string repository;
    std::string action;
    PullRequestState state;
    int changedFiles;
    int approvals;
    bool requiredChecksPassed;
};

std::string toString(PullRequestState state) {
    switch (state) {
        case PullRequestState::Draft:
            return "draft";
        case PullRequestState::Open:
            return "open";
        case PullRequestState::Closed:
            return "closed";
        case PullRequestState::Merged:
            return "merged";
    }
    return "unknown";
}

std::string toString(ReviewState state) {
    switch (state) {
        case ReviewState::Commented:
            return "commented";
        case ReviewState::ChangesRequested:
            return "changes_requested";
        case ReviewState::Approved:
            return "approved";
        case ReviewState::Dismissed:
            return "dismissed";
    }
    return "unknown";
}

class CircularQueue {
private:
    std::vector<std::optional<PullRequestEvent>> buffer_;
    std::size_t front_{0};
    std::size_t rear_{0};
    std::size_t size_{0};

    std::size_t nextIndex(std::size_t index) const {
        return (index + 1) % buffer_.size();
    }

public:
    explicit CircularQueue(std::size_t capacity)
        : buffer_(capacity) {
        if (capacity == 0) {
            throw std::invalid_argument("Queue capacity must be positive.");
        }
    }

    bool empty() const {
        return size_ == 0;
    }

    bool full() const {
        return size_ == buffer_.size();
    }

    std::size_t size() const {
        return size_;
    }

    std::size_t capacity() const {
        return buffer_.size();
    }

    std::size_t frontIndex() const {
        return front_;
    }

    std::size_t rearIndex() const {
        return rear_;
    }

    void enqueue(PullRequestEvent event) {
        if (full()) {
            throw QueueFullException(
                "Event buffer is full; producer must apply back-pressure.");
        }

        buffer_[rear_] = std::move(event);
        rear_ = nextIndex(rear_);
        ++size_;
    }

    PullRequestEvent dequeue() {
        if (empty()) {
            throw QueueEmptyException(
                "Event buffer is empty; no event can be processed.");
        }

        PullRequestEvent event = std::move(*buffer_[front_]);
        buffer_[front_].reset();

        front_ = nextIndex(front_);
        --size_;

        return event;
    }

    const PullRequestEvent& peek() const {
        if (empty()) {
            throw QueueEmptyException("Cannot inspect an empty event buffer.");
        }

        return *buffer_[front_];
    }
};

struct BranchPolicy {
    std::string branch;
    int requiredApprovals;
    bool requireChecks;
    bool prohibitForcePush;
    bool prohibitDeletion;
};

bool mergeEligible(
    const PullRequestEvent& pullRequest,
    const BranchPolicy& policy
) {
    if (pullRequest.state != PullRequestState::Open) {
        return false;
    }

    if (policy.requireChecks && !pullRequest.requiredChecksPassed) {
        return false;
    }

    if (pullRequest.approvals < policy.requiredApprovals) {
        return false;
    }

    return true;
}

void printEvent(const PullRequestEvent& event) {
    std::cout
        << "PR #" << event.id
        << " | repo=" << event.repository
        << " | action=" << event.action
        << " | state=" << toString(event.state)
        << " | files=" << event.changedFiles
        << " | approvals=" << event.approvals
        << " | checks=" << (event.requiredChecksPassed ? "pass" : "fail")
        << '\n';
}

void demonstrateCoreMechanism() {
    std::cout << "\n=== Core Circular Queue Mechanism ===\n";

    CircularQueue queue(4);

    queue.enqueue({101, "payments", "opened",
                   PullRequestState::Open, 8, 0, false});

    queue.enqueue({102, "identity", "review_submitted",
                   PullRequestState::Open, 3, 2, true});

    queue.enqueue({103, "analytics", "synchronize",
                   PullRequestState::Open, 12, 1, true});

    std::cout
        << "size=" << queue.size()
        << ", front=" << queue.frontIndex()
        << ", rear=" << queue.rearIndex()
        << '\n';

    printEvent(queue.peek());

    const auto first = queue.dequeue();
    printEvent(first);

    queue.enqueue({104, "payments", "status_check_completed",
                    PullRequestState::Open, 8, 2, true});

    std::cout
        << "After wrap-around: size=" << queue.size()
        << ", front=" << queue.frontIndex()
        << ", rear=" << queue.rearIndex()
        << '\n';

    while (!queue.empty()) {
        printEvent(queue.dequeue());
    }
}

void demonstrateGovernancePolicy() {
    std::cout << "\n=== Protected Branch Governance ===\n";

    BranchPolicy mainPolicy{
        "main",
        2,
        true,
        true,
        true
    };

    std::vector<PullRequestEvent> requests{
        {201, "payments", "review",
         PullRequestState::Open, 5, 1, true},

        {202, "payments", "checks_completed",
         PullRequestState::Open, 7, 2, false},

        {203, "payments", "approved",
         PullRequestState::Open, 4, 2, true},

        {204, "payments", "closed",
         PullRequestState::Closed, 2, 5, true}
    };

    for (const auto& request : requests) {
        const bool eligible = mergeEligible(request, mainPolicy);

        printEvent(request);

        std::cout
            << "Merge eligibility: "
            << (eligible ? "eligible" : "blocked")
            << '\n';

        if (!eligible) {
            if (request.approvals < mainPolicy.requiredApprovals) {
                std::cout << "Reason: required approvals are missing.\n";
            } else if (!request.requiredChecksPassed) {
                std::cout << "Reason: required status checks are not passing.\n";
            } else if (request.state != PullRequestState::Open) {
                std::cout << "Reason: pull request is not open.\n";
            }
        }
    }
}

void demonstrateOverflow() {
    std::cout << "\n=== Overflow Protection ===\n";

    CircularQueue queue(2);

    queue.enqueue({301, "repo-a", "opened",
                   PullRequestState::Open, 1, 0, false});

    queue.enqueue({302, "repo-a", "reviewed",
                   PullRequestState::Open, 2, 1, true});

    try {
        queue.enqueue({303, "repo-a", "synchronize",
                       PullRequestState::Open, 3, 1, true});
    } catch (const QueueFullException& exception) {
        std::cout << "Overflow handled: "
                  << exception.what() << '\n';
    }

    queue.dequeue();
    queue.enqueue({303, "repo-a", "synchronize",
                   PullRequestState::Open, 3, 1, true});

    std::cout << "A completed slot was reused successfully.\n";
}

void demonstrateUnderflow() {
    std::cout << "\n=== Underflow Protection ===\n";

    CircularQueue queue(2);

    try {
        queue.dequeue();
    } catch (const QueueEmptyException& exception) {
        std::cout << "Underflow handled: "
                  << exception.what() << '\n';
    }
}

void demonstrateComplexity() {
    std::cout << "\n=== Complexity ===\n";
    std::cout << "enqueue: O(1)\n";
    std::cout << "dequeue: O(1)\n";
    std::cout << "peek: O(1)\n";
    std::cout << "space: O(capacity)\n";
    std::cout << "Wrap-around uses modulo arithmetic instead of shifting elements.\n";
}

int main() {
    try {
        std::cout << "CIRCULAR QUEUE: REPOSITORY GOVERNANCE EVENT BUFFER\n";

        demonstrateCoreMechanism();
        demonstrateGovernancePolicy();
        demonstrateOverflow();
        demonstrateUnderflow();
        demonstrateComplexity();

        std::cout << "\nCase study completed successfully.\n";
    } catch (const std::exception& exception) {
        std::cerr << "Fatal error: " << exception.what() << '\n';
        return 1;
    }

    return 0;
}
