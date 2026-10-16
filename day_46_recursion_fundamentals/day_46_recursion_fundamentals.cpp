#include <algorithm>
#include <functional>
#include <iostream>
#include <map>
#include <optional>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

using namespace std;

// A release pipeline is modeled as a dependency graph. Recursive traversal
// detects cycles, computes dependency depth, and identifies build order.

struct Component {
    string name;
    vector<string> dependencies;
    int buildMinutes;
};

class BuildPlanner {
private:
    unordered_map<string, Component> components;
    unordered_map<string, int> memoizedDuration;
    set<string> active;

    int durationOf(const string& name) {
        auto cached = memoizedDuration.find(name);
        if (cached != memoizedDuration.end()) {
            return cached->second;
        }

        auto found = components.find(name);
        if (found == components.end()) {
            throw invalid_argument("Unknown component: " + name);
        }

        // An active node is already on the current recursion path.
        // Encountering it again means the dependency graph contains a cycle.
        if (active.count(name)) {
            throw logic_error("Dependency cycle detected at: " + name);
        }

        active.insert(name);
        int longestDependencyPath = 0;

        for (const string& dependency : found->second.dependencies) {
            longestDependencyPath =
                max(longestDependencyPath, durationOf(dependency));
        }

        active.erase(name);
        const int total = found->second.buildMinutes + longestDependencyPath;
        memoizedDuration[name] = total;
        return total;
    }

    bool visit(
        const string& name,
        unordered_map<string, int>& state,
        vector<string>& order
    ) const {
        // 0 means unseen, 1 means active, and 2 means completely processed.
        if (state[name] == 1) {
            throw logic_error("Cycle encountered while producing build order");
        }
        if (state[name] == 2) return false;

        auto found = components.find(name);
        if (found == components.end()) {
            throw invalid_argument("Unknown component: " + name);
        }

        state[name] = 1;
        for (const auto& dependency : found->second.dependencies) {
            visit(dependency, state, order);
        }
        state[name] = 2;
        order.push_back(name);
        return true;
    }

public:
    void addComponent(Component component) {
        if (component.name.empty()) {
            throw invalid_argument("Component name cannot be empty");
        }
        if (component.buildMinutes < 0) {
            throw invalid_argument("Build duration cannot be negative");
        }
        if (components.count(component.name)) {
            throw invalid_argument("Duplicate component: " + component.name);
        }
        components.emplace(component.name, move(component));
        memoizedDuration.clear();
    }

    int estimatedCriticalPath(const string& target) {
        return durationOf(target);
    }

    vector<string> buildOrder(const string& target) const {
        unordered_map<string, int> state;
        vector<string> order;
        visit(target, state, order);
        return order;
    }

    vector<string> dependenciesOf(const string& target) const {
        auto found = components.find(target);
        if (found == components.end()) {
            throw invalid_argument("Unknown component: " + target);
        }
        return found->second.dependencies;
    }

    void validateAllDependencies() {
        for (const auto& entry : components) {
            for (const auto& dependency : entry.second.dependencies) {
                if (!components.count(dependency)) {
                    throw invalid_argument(
                        entry.first + " depends on unknown component " + dependency
                    );
                }
            }
        }
    }
};

struct NestedValue {
    optional<int> value;
    vector<NestedValue> children;

    static NestedValue number(int n) {
        NestedValue node;
        node.value = n;
        return node;
    }

    static NestedValue group(vector<NestedValue> nodes) {
        NestedValue node;
        node.children = move(nodes);
        return node;
    }
};

long long nestedSum(const NestedValue& node) {
    long long total = node.value.value_or(0);
    for (const auto& child : node.children) {
        total += nestedSum(child);
    }
    return total;
}

long long fastPower(long long base, unsigned int exponent) {
    if (exponent == 0) return 1;

    const long long half = fastPower(base, exponent / 2);
    const long long square = half * half;

    // This educational implementation assumes intermediate products fit
    // in long long; production code should check multiplication overflow.
    return exponent % 2 == 0 ? square : base * square;
}

int main() {
    try {
        BuildPlanner planner;
        planner.addComponent({"database", {}, 8});
        planner.addComponent({"cache", {}, 3});
        planner.addComponent({"identity", {"database"}, 5});
        planner.addComponent({"api", {"database", "cache"}, 12});
        planner.addComponent({"web-app", {"api", "identity"}, 7});
        planner.validateAllDependencies();

        cout << "Release pipeline dependency analysis\n";
        cout << "Critical-path estimate: "
             << planner.estimatedCriticalPath("web-app") << " minutes\n";

        cout << "Dependency-first build order:";
        for (const auto& component : planner.buildOrder("web-app")) {
            cout << ' ' << component;
        }
        cout << '\n';

        const auto nested = NestedValue::group({
            NestedValue::number(120),
            NestedValue::group({
                NestedValue::number(55),
                NestedValue::number(13)
            }),
            NestedValue::number(8)
        });
        cout << "Nested configuration total: " << nestedSum(nested) << '\n';
        cout << "3^13: " << fastPower(3, 13) << '\n';

        BuildPlanner broken;
        broken.addComponent({"service-a", {"service-b"}, 2});
        broken.addComponent({"service-b", {"service-a"}, 4});

        try {
            broken.estimatedCriticalPath("service-a");
            throw logic_error("Cycle should have been rejected");
        } catch (const logic_error& error) {
            cout << "Expected graph failure: " << error.what() << '\n';
        }

        try {
            planner.estimatedCriticalPath("missing-service");
            throw logic_error("Unknown component should have been rejected");
        } catch (const invalid_argument& error) {
            cout << "Expected validation failure: " << error.what() << '\n';
        }

        if (nestedSum(nested) != 196) {
            throw runtime_error("Nested sum verification failed");
        }
        if (fastPower(2, 10) != 1024) {
            throw runtime_error("Power verification failed");
        }

        cout << "Case-study checks passed.\n";
    } catch (const exception& error) {
        cerr << "Build planner failed: " << error.what() << '\n';
        return 1;
    }
    return 0;
}
