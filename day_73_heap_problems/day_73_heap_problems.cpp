#include <algorithm>
#include <cassert>
#include <cstdint>
#include <functional>
#include <iostream>
#include <limits>
#include <queue>
#include <random>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

using namespace std;

class HeapError : public runtime_error {
public:
    explicit HeapError(const string& message)
        : runtime_error(message) {}
};

class InvalidInputError : public HeapError {
public:
    explicit InvalidInputError(const string& message)
        : HeapError(message) {}
};

class EmptyHeapError : public HeapError {
public:
    explicit EmptyHeapError(const string& message)
        : HeapError(message) {}
};

template <typename T, typename Compare = less<T>>
class BinaryHeap {
private:
    vector<T> data;
    Compare compare;

    void siftUp(size_t index) {
        while (index > 0) {
            size_t parent = (index - 1) / 2;

            if (!compare(data[index], data[parent])) {
                break;
            }

            swap(data[index], data[parent]);
            index = parent;
        }
    }

    void siftDown(size_t index) {
        const size_t n = data.size();

        while (true) {
            size_t best = index;
            size_t left = index * 2 + 1;
            size_t right = left + 1;

            if (left < n && compare(data[left], data[best])) {
                best = left;
            }

            if (right < n && compare(data[right], data[best])) {
                best = right;
            }

            if (best == index) break;

            swap(data[index], data[best]);
            index = best;
        }
    }

public:
    explicit BinaryHeap(Compare comp = Compare())
        : compare(comp) {}

    explicit BinaryHeap(
        vector<T> values,
        Compare comp = Compare()
    ) : data(move(values)), compare(comp) {
        for (int i = static_cast<int>(data.size()) / 2 - 1;
             i >= 0; --i) {
            siftDown(static_cast<size_t>(i));
        }
    }

    bool empty() const {
        return data.empty();
    }

    size_t size() const {
        return data.size();
    }

    void push(const T& value) {
        data.push_back(value);
        siftUp(data.size() - 1);
    }

    const T& top() const {
        if (empty()) {
            throw EmptyHeapError("Cannot inspect an empty heap.");
        }

        return data.front();
    }

    T pop() {
        if (empty()) {
            throw EmptyHeapError("Cannot remove from an empty heap.");
        }

        T result = data.front();

        if (data.size() == 1) {
            data.pop_back();
            return result;
        }

        data.front() = move(data.back());
        data.pop_back();
        siftDown(0);

        return result;
    }
};

void validateK(int k, size_t n, bool allowZero = false) {
    if (k < (allowZero ? 0 : 1) ||
        static_cast<size_t>(k) > n) {
        throw InvalidInputError("Invalid k value.");
    }
}

int kthLargest(const vector<int>& values, int k) {
    validateK(k, values.size());

    // A min-heap retains only the k largest elements.
    priority_queue<int, vector<int>, greater<int>> heap;

    for (int value : values) {
        if (static_cast<int>(heap.size()) < k) {
            heap.push(value);
        } else if (value > heap.top()) {
            heap.pop();
            heap.push(value);
        }
    }

    return heap.top();
}

int kthSmallest(const vector<int>& values, int k) {
    validateK(k, values.size());

    priority_queue<int> heap;

    for (int value : values) {
        if (static_cast<int>(heap.size()) < k) {
            heap.push(value);
        } else if (value < heap.top()) {
            heap.pop();
            heap.push(value);
        }
    }

    return heap.top();
}

vector<int> topKLargest(const vector<int>& values, int k) {
    validateK(k, values.size(), true);

    priority_queue<int, vector<int>, greater<int>> heap;

    for (int value : values) {
        if (static_cast<int>(heap.size()) < k) {
            heap.push(value);
        } else if (k > 0 && value > heap.top()) {
            heap.pop();
            heap.push(value);
        }
    }

    vector<int> result;

    while (!heap.empty()) {
        result.push_back(heap.top());
        heap.pop();
    }

    sort(result.rbegin(), result.rend());
    return result;
}

struct FrequencyEntry {
    int value;
    int frequency;
};

struct FrequencyCompare {
    bool operator()(
        const FrequencyEntry& a,
        const FrequencyEntry& b
    ) const {
        if (a.frequency != b.frequency) {
            return a.frequency < b.frequency;
        }

        return a.value > b.value;
    }
};

vector<FrequencyEntry> topKFrequent(
    const vector<int>& values,
    int k
) {
    if (k < 0) {
        throw InvalidInputError("k cannot be negative.");
    }

    unordered_map<int, int> frequency;

    for (int value : values) {
        ++frequency[value];
    }

    priority_queue<
        FrequencyEntry,
        vector<FrequencyEntry>,
        FrequencyCompare
    > heap;

    for (const auto& [value, count] : frequency) {
        heap.push({value, count});
    }

    vector<FrequencyEntry> result;

    while (!heap.empty() &&
           static_cast<int>(result.size()) < k) {
        result.push_back(heap.top());
        heap.pop();
    }

    return result;
}

struct MergeNode {
    int value;
    size_t arrayIndex;
    size_t elementIndex;
};

struct MergeCompare {
    bool operator()(
        const MergeNode& a,
        const MergeNode& b
    ) const {
        if (a.value != b.value) {
            return a.value > b.value;
        }

        return a.arrayIndex > b.arrayIndex;
    }
};

vector<int> mergeSortedArrays(
    const vector<vector<int>>& arrays
) {
    priority_queue<
        MergeNode,
        vector<MergeNode>,
        MergeCompare
    > heap;

    size_t total = 0;

    for (size_t i = 0; i < arrays.size(); ++i) {
        const auto& array = arrays[i];

        if (!is_sorted(array.begin(), array.end())) {
            throw InvalidInputError(
                "An input array is not sorted."
            );
        }

        total += array.size();

        if (!array.empty()) {
            heap.push({array[0], i, 0});
        }
    }

    vector<int> result;
    result.reserve(total);

    while (!heap.empty()) {
        MergeNode node = heap.top();
        heap.pop();

        result.push_back(node.value);

        size_t nextIndex = node.elementIndex + 1;
        const auto& array = arrays[node.arrayIndex];

        if (nextIndex < array.size()) {
            heap.push({
                array[nextIndex],
                node.arrayIndex,
                nextIndex
            });
        }
    }

    return result;
}

class RunningMedian {
private:
    priority_queue<int> lower;
    priority_queue<int, vector<int>, greater<int>> upper;

public:
    void add(int value) {
        if (lower.empty() || value <= lower.top()) {
            lower.push(value);
        } else {
            upper.push(value);
        }

        if (lower.size() > upper.size() + 1) {
            upper.push(lower.top());
            lower.pop();
        } else if (upper.size() > lower.size()) {
            lower.push(upper.top());
            upper.pop();
        }
    }

    double median() const {
        if (lower.empty()) {
            throw EmptyHeapError("Median is undefined.");
        }

        if (lower.size() > upper.size()) {
            return static_cast<double>(lower.top());
        }

        // Convert before addition to prevent signed integer overflow.
        return (
            static_cast<double>(lower.top()) +
            static_cast<double>(upper.top())
        ) / 2.0;
    }

    size_t size() const {
        return lower.size() + upper.size();
    }
};

class KthLargestStream {
private:
    int k;
    priority_queue<int, vector<int>, greater<int>> heap;

public:
    explicit KthLargestStream(int kValue) : k(kValue) {
        if (k < 1) {
            throw InvalidInputError("k must be positive.");
        }
    }

    bool add(int value, int& answer) {
        if (static_cast<int>(heap.size()) < k) {
            heap.push(value);
        } else if (value > heap.top()) {
            heap.pop();
            heap.push(value);
        }

        if (static_cast<int>(heap.size()) < k) {
            return false;
        }

        answer = heap.top();
        return true;
    }
};

enum class CheckState {
    Pending,
    Passed,
    Failed
};

enum class ReviewState {
    Pending,
    Approved,
    ChangesRequested,
    Dismissed
};

struct StatusCheck {
    string name;
    CheckState state;
};

struct Review {
    string reviewer;
    ReviewState state;
    bool eligible;
    bool stale;
};

struct BranchProtection {
    bool protectedBranch = true;
    bool requirePullRequest = true;
    bool requireLinearHistory = true;
    bool allowForcePush = false;
    bool allowDeletion = false;
    bool allowAdminBypass = false;
    int requiredApprovals = 2;
    vector<string> requiredChecks;
};

struct PullRequest {
    int id;
    string sourceBranch;
    string targetBranch;
    bool open = true;
    bool draft = false;
    bool conversationsResolved = true;
    bool linearHistory = true;
    bool mergeConflict = false;
    vector<Review> reviews;
    vector<StatusCheck> checks;
};

struct EligibilityResult {
    bool eligible = false;
    vector<string> reasons;
};

class GovernanceEngine {
public:
    static EligibilityResult evaluate(
        const PullRequest& pr,
        const BranchProtection& policy,
        bool actorIsAdmin = false
    ) {
        EligibilityResult result;

        auto reject = [&](const string& reason) {
            result.reasons.push_back(reason);
        };

        if (!pr.open) reject("Pull Request is not open.");
        if (pr.draft) reject("Draft Pull Request cannot be merged.");
        if (pr.sourceBranch == pr.targetBranch) {
            reject("Source and target branches must differ.");
        }

        if (pr.mergeConflict) reject("Merge conflict exists.");

        if (!pr.conversationsResolved) {
            reject("Review conversations remain unresolved.");
        }

        if (policy.requireLinearHistory && !pr.linearHistory) {
            reject("Linear history is required.");
        }

        int approvals = 0;

        for (const Review& review : pr.reviews) {
            if (
                review.state == ReviewState::ChangesRequested &&
                review.eligible &&
                !review.stale
            ) {
                reject(
                    "An eligible reviewer requested changes: " +
                    review.reviewer
                );
            }

            if (
                review.state == ReviewState::Approved &&
                review.eligible &&
                !review.stale
            ) {
                ++approvals;
            }
        }

        if (approvals < policy.requiredApprovals) {
            reject("Required approval count has not been reached.");
        }

        for (const string& required : policy.requiredChecks) {
            auto found = find_if(
                pr.checks.begin(),
                pr.checks.end(),
                [&](const StatusCheck& check) {
                    return check.name == required;
                }
            );

            if (found == pr.checks.end()) {
                reject("Missing status check: " + required);
            } else if (found->state != CheckState::Passed) {
                reject("Status check has not passed: " + required);
            }
        }

        // Administrative bypass is an explicit policy exception.
        // It does not silently change the recorded review decisions.
        if (actorIsAdmin && policy.allowAdminBypass) {
            result.reasons.clear();
            result.eligible = pr.open && !pr.draft &&
                              !pr.mergeConflict &&
                              pr.sourceBranch != pr.targetBranch;

            if (!result.eligible) {
                reject("Basic Pull Request conditions failed.");
            }

            return result;
        }

        result.eligible = result.reasons.empty();
        return result;
    }
};

void testHeapAlgorithms() {
    vector<int> values = {3, 2, 1, 5, 6, 4};

    assert(kthLargest(values, 2) == 5);
    assert(kthSmallest(values, 2) == 2);

    assert(
        topKLargest(values, 3) ==
        vector<int>({6, 5, 4})
    );

    auto merged = mergeSortedArrays({
        {1, 4, 7},
        {2, 5, 8},
        {3, 6, 9}
    });

    assert(
        merged == vector<int>({1, 2, 3, 4, 5, 6, 7, 8, 9})
    );

    RunningMedian tracker;

    for (int value : {5, 15, 1, 3}) {
        tracker.add(value);
    }

    assert(tracker.median() == 4.0);

    KthLargestStream stream(3);
    int answer = 0;

    for (int value : {4, 5, 8, 2}) {
        stream.add(value, answer);
    }

    assert(answer == 4);
    assert(stream.add(10, answer));
    assert(answer == 5);
}

void testGovernance() {
    PullRequest pr{
        101,
        "feature/heap-engine",
        "main",
        true,
        false,
        true,
        true,
        false,
        {
            {"reviewer-a", ReviewState::Approved, true, false},
            {"reviewer-b", ReviewState::Approved, true, false}
        },
        {
            {"unit-tests", CheckState::Passed},
            {"security-scan", CheckState::Passed}
        }
    };

    BranchProtection policy;
    policy.requiredApprovals = 2;
    policy.requiredChecks = {"unit-tests", "security-scan"};

    auto result = GovernanceEngine::evaluate(pr, policy);

    assert(result.eligible);

    pr.reviews[0].stale = true;

    result = GovernanceEngine::evaluate(pr, policy);
    assert(!result.eligible);
}

void demo() {
    vector<int> values = {12, 3, 5, 7, 19, 4, 8, 15};

    cout << "Kth largest: " << kthLargest(values, 3) << '\n';
    cout << "Kth smallest: " << kthSmallest(values, 3) << '\n';

    cout << "Top 4: ";
    for (int value : topKLargest(values, 4)) {
        cout << value << ' ';
    }
    cout << '\n';

    cout << "Merged arrays: ";

    for (int value : mergeSortedArrays({
        {1, 4, 7},
        {2, 5, 8},
        {3, 6, 9}
    })) {
        cout << value << ' ';
    }

    cout << '\n';

    RunningMedian median;

    for (int value : {10, 20, 5, 30, 15, 40}) {
        median.add(value);
        cout << "Inserted " << value
             << ", median = " << median.median() << '\n';
    }
}

int main() {
    try {
        testHeapAlgorithms();
        testGovernance();
        cout << "All tests passed.\n\n";

        demo();
    } catch (const exception& error) {
        cerr << "Execution error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
