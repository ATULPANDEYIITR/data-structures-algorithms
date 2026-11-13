#include <algorithm>
#include <cassert>
#include <cmath>
#include <functional>
#include <iostream>
#include <limits>
#include <queue>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <utility>
#include <vector>

using namespace std;

/*
 * Advanced Heap Problems - C++17
 *
 * Implementations:
 * 1. Streaming median
 * 2. CPU scheduling
 * 3. Merge K sorted arrays
 * 4. Maximum capital optimization
 * 5. Minimum refueling stops
 * 6. Deadline profit scheduling
 *
 * All implementations use standard C++17.
 */

// ============================================================
// 1. STREAMING MEDIAN
// ============================================================

class MedianFinder {
private:
    priority_queue<int> lower;
    priority_queue<int, vector<int>, greater<int>> upper;

public:
    void addNumber(int value) {

        lower.push(value);

        if (!upper.empty() && lower.top() > upper.top()) {
            upper.push(lower.top());
            lower.pop();
        }

        if (lower.size() > upper.size() + 1) {
            upper.push(lower.top());
            lower.pop();
        } else if (upper.size() > lower.size()) {
            lower.push(upper.top());
            upper.pop();
        }
    }

    double findMedian() const {

        if (lower.empty()) {
            throw runtime_error("Median of empty stream");
        }

        if (lower.size() > upper.size()) {
            return static_cast<double>(lower.top());
        }

        // Convert before addition to avoid integer overflow.
        return (
            static_cast<double>(lower.top()) +
            static_cast<double>(upper.top())
        ) / 2.0;
    }

    size_t size() const {
        return lower.size() + upper.size();
    }
};


// ============================================================
// 2. CPU TASK SCHEDULING
// ============================================================

enum class TaskState {
    WAITING,
    RUNNING,
    COMPLETED
};

struct Task {
    string id;
    int priority;
    int duration;
    int sequence;
    TaskState state;
};

struct TaskComparator {
    bool operator()(const Task& a, const Task& b) const {
        if (a.priority != b.priority) {
            return a.priority > b.priority;
        }

        return a.sequence > b.sequence;
    }
};

class CPUScheduler {
private:
    priority_queue<
        Task,
        vector<Task>,
        TaskComparator
    > queue;

    unordered_set<string> identifiers;
    int sequence = 0;

public:
    void submit(
        const string& id,
        int priority,
        int duration
    ) {
        if (id.empty()) {
            throw invalid_argument("Task ID cannot be empty");
        }

        if (priority < 0 || duration <= 0) {
            throw invalid_argument("Invalid task properties");
        }

        if (!identifiers.insert(id).second) {
            throw invalid_argument("Duplicate task ID");
        }

        queue.push({
            id,
            priority,
            duration,
            sequence++,
            TaskState::WAITING
        });
    }

    vector<string> executeAll() {
        vector<string> result;

        while (!queue.empty()) {
            Task task = queue.top();
            queue.pop();

            task.state = TaskState::RUNNING;

            // Simulated non-preemptive task execution.
            task.state = TaskState::COMPLETED;

            result.push_back(task.id);
        }

        return result;
    }
};


// ============================================================
// 3. MERGE K SORTED ARRAYS
// ============================================================

struct HeapNode {
    int value;
    size_t listIndex;
    size_t elementIndex;
};

struct NodeComparator {
    bool operator()(
        const HeapNode& a,
        const HeapNode& b
    ) const {
        if (a.value != b.value) {
            return a.value > b.value;
        }

        return a.listIndex > b.listIndex;
    }
};

vector<int> mergeKSortedArrays(
    const vector<vector<int>>& lists
) {
    priority_queue<
        HeapNode,
        vector<HeapNode>,
        NodeComparator
    > minHeap;

    size_t totalSize = 0;

    for (size_t i = 0; i < lists.size(); i++) {

        if (!is_sorted(lists[i].begin(), lists[i].end())) {
            throw invalid_argument("Input list is not sorted");
        }

        totalSize += lists[i].size();

        if (!lists[i].empty()) {
            minHeap.push({
                lists[i][0],
                i,
                0
            });
        }
    }

    vector<int> result;
    result.reserve(totalSize);

    while (!minHeap.empty()) {

        HeapNode current = minHeap.top();
        minHeap.pop();

        result.push_back(current.value);

        size_t nextIndex = current.elementIndex + 1;

        if (nextIndex < lists[current.listIndex].size()) {
            minHeap.push({
                lists[current.listIndex][nextIndex],
                current.listIndex,
                nextIndex
            });
        }
    }

    return result;
}


// ============================================================
// 4. MAXIMUM CAPITAL
// ============================================================

struct Project {
    string id;
    long long requiredCapital;
    long long profit;
};

struct ProjectComparator {
    bool operator()(
        const Project& a,
        const Project& b
    ) const {
        if (a.profit != b.profit) {
            return a.profit < b.profit;
        }

        return a.id > b.id;
    }
};

struct CapitalResult {
    long long finalCapital;
    vector<string> selectedProjects;
};

CapitalResult maximizeCapital(
    long long initialCapital,
    vector<Project> projects,
    int maximumProjects
) {
    if (initialCapital < 0 || maximumProjects < 0) {
        throw invalid_argument("Invalid capital parameters");
    }

    unordered_set<string> ids;

    for (const auto& project : projects) {
        if (
            project.id.empty() ||
            project.requiredCapital < 0 ||
            project.profit < 0 ||
            !ids.insert(project.id).second
        ) {
            throw invalid_argument("Invalid project");
        }
    }

    sort(
        projects.begin(),
        projects.end(),
        [](const Project& a, const Project& b) {
            if (a.requiredCapital != b.requiredCapital) {
                return a.requiredCapital < b.requiredCapital;
            }

            return a.id < b.id;
        }
    );

    priority_queue<
        Project,
        vector<Project>,
        ProjectComparator
    > affordable;

    long long capital = initialCapital;
    size_t index = 0;

    CapitalResult result{
        initialCapital,
        {}
    };

    for (
        int count = 0;
        count < maximumProjects;
        count++
    ) {

        while (
            index < projects.size() &&
            projects[index].requiredCapital <= capital
        ) {
            affordable.push(projects[index]);
            index++;
        }

        if (affordable.empty() || affordable.top().profit == 0) {
            break;
        }

        Project selected = affordable.top();
        affordable.pop();

        if (
            capital >
            numeric_limits<long long>::max() - selected.profit
        ) {
            throw overflow_error("Capital overflow");
        }

        capital += selected.profit;
        result.selectedProjects.push_back(selected.id);
    }

    result.finalCapital = capital;

    return result;
}


// ============================================================
// 5. MINIMUM REFUELING STOPS
// ============================================================

struct FuelStation {
    long long position;
    long long fuel;
};

struct RefuelingResult {
    int stops;
    vector<size_t> selectedStations;
};

RefuelingResult minimumRefuelingStops(
    long long target,
    long long initialFuel,
    vector<FuelStation> stations
) {
    if (target < 0 || initialFuel < 0) {
        throw invalid_argument("Invalid target or fuel");
    }

    for (const auto& station : stations) {
        if (
            station.position < 0 ||
            station.position > target ||
            station.fuel < 0
        ) {
            throw invalid_argument("Invalid station");
        }
    }

    sort(
        stations.begin(),
        stations.end(),
        [](const FuelStation& a, const FuelStation& b) {
            return a.position < b.position;
        }
    );

    for (size_t i = 1; i < stations.size(); i++) {
        if (stations[i - 1].position == stations[i].position) {
            throw invalid_argument("Duplicate station position");
        }
    }

    // Store fuel and original station index.
    priority_queue<
        pair<long long, size_t>
    > available;

    long long reachable = initialFuel;

    RefuelingResult result{
        0,
        {}
    };

    for (size_t i = 0; i < stations.size(); i++) {

        while (reachable < stations[i].position) {

            if (available.empty()) {
                return {-1, {}};
            }

            auto best = available.top();
            available.pop();

            if (
                reachable >
                numeric_limits<long long>::max() - best.first
            ) {
                throw overflow_error("Fuel overflow");
            }

            reachable += best.first;
            result.selectedStations.push_back(best.second);
        }

        available.push({
            stations[i].fuel,
            i
        });
    }

    while (reachable < target) {

        if (available.empty()) {
            return {-1, {}};
        }

        auto best = available.top();
        available.pop();

        if (
            reachable >
            numeric_limits<long long>::max() - best.first
        ) {
            throw overflow_error("Fuel overflow");
        }

        reachable += best.first;
        result.selectedStations.push_back(best.second);
    }

    result.stops = static_cast<int>(
        result.selectedStations.size()
    );

    return result;
}


// ============================================================
// 6. DEADLINE PROFIT SCHEDULING
// ============================================================

struct DeadlineTask {
    string id;
    int deadline;
    long long profit;
};

struct DeadlineResult {
    long long totalProfit;
    vector<string> selected;
};

DeadlineResult maximizeDeadlineProfit(
    const vector<DeadlineTask>& tasks
) {
    unordered_set<string> ids;

    vector<DeadlineTask> sorted = tasks;

    for (const auto& task : sorted) {
        if (
            task.id.empty() ||
            task.deadline <= 0 ||
            task.profit < 0 ||
            !ids.insert(task.id).second
        ) {
            throw invalid_argument("Invalid deadline task");
        }
    }

    sort(
        sorted.begin(),
        sorted.end(),
        [](const DeadlineTask& a, const DeadlineTask& b) {
            if (a.deadline != b.deadline) {
                return a.deadline < b.deadline;
            }

            return a.id < b.id;
        }
    );

    // Min heap removes the lowest-profit selected job.
    priority_queue<
        pair<long long, string>,
        vector<pair<long long, string>>,
        greater<pair<long long, string>>
    > selected;

    long long totalProfit = 0;

    for (const auto& task : sorted) {

        if (
            totalProfit >
            numeric_limits<long long>::max() - task.profit
        ) {
            throw overflow_error("Profit overflow");
        }

        selected.push({
            task.profit,
            task.id
        });

        totalProfit += task.profit;

        if (
            selected.size() >
            static_cast<size_t>(task.deadline)
        ) {
            totalProfit -= selected.top().first;
            selected.pop();
        }
    }

    DeadlineResult result{
        totalProfit,
        {}
    };

    while (!selected.empty()) {
        result.selected.push_back(selected.top().second);
        selected.pop();
    }

    sort(
        result.selected.begin(),
        result.selected.end()
    );

    return result;
}


// ============================================================
// 7. MAIN AND VALIDATION
// ============================================================

int main() {
    try {

        cout << "\nADVANCED HEAP PROBLEMS\n";
        cout << string(55, '=') << "\n";

        // Median
        cout << "\n1. Streaming Median\n";

        MedianFinder median;

        for (int value : {12, 4, 5, 3, 8, 7}) {
            median.addNumber(value);

            cout << "Inserted " << value
                 << " | Median: "
                 << median.findMedian()
                 << '\n';
        }

        assert(median.findMedian() == 6.0);

        // CPU scheduling
        cout << "\n2. CPU Scheduling\n";

        CPUScheduler scheduler;

        scheduler.submit("Backup", 3, 20);
        scheduler.submit("Security", 1, 10);
        scheduler.submit("Analytics", 2, 15);

        for (const string& id : scheduler.executeAll()) {
            cout << id << '\n';
        }

        // K-way merge
        cout << "\n3. Merge K Sorted Arrays\n";

        auto merged = mergeKSortedArrays({
            {1, 4, 7},
            {2, 5, 8},
            {3, 6, 9}
        });

        for (int value : merged) {
            cout << value << ' ';
        }

        cout << '\n';

        assert(
            merged == vector<int>({
                1, 2, 3, 4, 5, 6, 7, 8, 9
            })
        );

        // Maximum capital
        cout << "\n4. Maximum Capital\n";

        auto capital = maximizeCapital(
            1,
            {
                {"Infrastructure", 0, 2},
                {"Analytics", 1, 5},
                {"Security", 2, 8},
                {"Cloud", 5, 10}
            },
            3
        );

        cout << "Final capital: "
             << capital.finalCapital << '\n';

        for (const auto& id : capital.selectedProjects) {
            cout << id << '\n';
        }

        assert(capital.finalCapital == 16);

        // Refueling
        cout << "\n5. Minimum Refueling Stops\n";

        auto refuel = minimumRefuelingStops(
            100,
            10,
            {
                {10, 60},
                {20, 30},
                {30, 30},
                {60, 40}
            }
        );

        cout << "Minimum stops: " << refuel.stops << '\n';

        assert(refuel.stops == 2);

        // Deadline scheduling
        cout << "\n6. Deadline Profit Scheduling\n";

        auto deadline = maximizeDeadlineProfit({
            {"A", 2, 100},
            {"B", 1, 19},
            {"C", 2, 27},
            {"D", 1, 25},
            {"E", 3, 15}
        });

        cout << "Maximum profit: "
             << deadline.totalProfit << '\n';

        assert(deadline.totalProfit == 142);

        // Edge cases
        cout << "\n7. Edge Case Validation\n";

        bool emptyMedianRejected = false;

        try {
            MedianFinder empty;
            empty.findMedian();
        } catch (const runtime_error&) {
            emptyMedianRejected = true;
        }

        assert(emptyMedianRejected);

        auto unreachable = minimumRefuelingStops(
            100,
            10,
            {}
        );

        assert(unreachable.stops == -1);

        cout << "All assertions passed.\n";

    } catch (const exception& error) {
        cerr << "Application error: "
             << error.what() << '\n';

        return 1;
    }

    return 0;
}
