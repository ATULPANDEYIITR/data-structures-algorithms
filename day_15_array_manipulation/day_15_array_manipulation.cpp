/*
    Array Manipulation: C++17 Technical Case Study
    =================================================

    Scenario:
    A warehouse fulfillment system receives a stream of package records.
    Packages have:
      - an identifier
      - a priority
      - a weight
      - a processing status

    The system needs to manipulate an in-memory sequence efficiently.

    Operations demonstrated:
      - insertion
      - deletion
      - swapping
      - reversal
      - shifting
      - rotation
      - stable rearrangement
      - partitioning
      - duplicate detection
      - searching
      - batch processing
      - validation
      - exception handling
      - algorithmic complexity

    Build:
        g++ -std=c++17 -O2 array_manipulation.cpp -o array_manipulation

    Run:
        ./array_manipulation
*/

#include <algorithm>
#include <chrono>
#include <exception>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <optional>
#include <random>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <utility>
#include <vector>

using namespace std;

// ---------------------------------------------------------------------------
// 1. DATA MODEL
// ---------------------------------------------------------------------------

enum class Status {
    Pending,
    Processing,
    Completed,
    Cancelled
};

string statusToString(Status status) {
    switch (status) {
        case Status::Pending:
            return "Pending";
        case Status::Processing:
            return "Processing";
        case Status::Completed:
            return "Completed";
        case Status::Cancelled:
            return "Cancelled";
    }

    return "Unknown";
}

struct Package {
    string id;
    int priority;
    double weight;
    Status status;

    bool operator==(const Package& other) const {
        return id == other.id;
    }
};

// ---------------------------------------------------------------------------
// 2. VALIDATION
// ---------------------------------------------------------------------------

void validatePackage(const Package& package) {
    if (package.id.empty()) {
        throw invalid_argument("Package ID cannot be empty");
    }

    if (package.priority < 0 || package.priority > 10) {
        throw invalid_argument("Priority must be between 0 and 10");
    }

    if (package.weight <= 0.0) {
        throw invalid_argument("Weight must be positive");
    }
}

// ---------------------------------------------------------------------------
// 3. DISPLAY
// ---------------------------------------------------------------------------

void printPackages(const vector<Package>& packages, const string& title) {
    cout << "\n" << title << "\n";

    if (packages.empty()) {
        cout << "  [empty]\n";
        return;
    }

    cout << left
         << setw(12) << "ID"
         << setw(10) << "Priority"
         << setw(10) << "Weight"
         << "Status\n";

    cout << string(48, '-') << "\n";

    for (const auto& package : packages) {
        cout << left
             << setw(12) << package.id
             << setw(10) << package.priority
             << setw(10) << fixed << setprecision(2) << package.weight
             << statusToString(package.status)
             << "\n";
    }
}

// ---------------------------------------------------------------------------
// 4. BASIC ARRAY-LIKE OPERATIONS
// ---------------------------------------------------------------------------

void insertPackage(
    vector<Package>& packages,
    size_t index,
    const Package& package
) {
    validatePackage(package);

    if (index > packages.size()) {
        throw out_of_range("Insertion index out of range");
    }

    /*
        vector::insert shifts subsequent elements to the right.
        Complexity is O(n) in the general case.
    */
    packages.insert(packages.begin() + static_cast<ptrdiff_t>(index), package);
}

Package deletePackage(vector<Package>& packages, size_t index) {
    if (index >= packages.size()) {
        throw out_of_range("Deletion index out of range");
    }

    Package deleted = packages[index];

    /*
        erase shifts later elements to fill the removed position.
        Complexity is O(n) when deleting away from the end.
    */
    packages.erase(packages.begin() + static_cast<ptrdiff_t>(index));

    return deleted;
}

void swapPackages(
    vector<Package>& packages,
    size_t first,
    size_t second
) {
    if (first >= packages.size() || second >= packages.size()) {
        throw out_of_range("Swap index out of range");
    }

    std::swap(packages[first], packages[second]);
}

// ---------------------------------------------------------------------------
// 5. REVERSAL
// ---------------------------------------------------------------------------

void reversePackages(vector<Package>& packages) {
    /*
        std::reverse uses a two-ended strategy and rearranges the existing
        vector. It requires O(n) time and O(1) auxiliary space for the
        normal vector element type.
    */
    reverse(packages.begin(), packages.end());
}

// ---------------------------------------------------------------------------
// 6. SHIFTING
// ---------------------------------------------------------------------------

template <typename T>
void shiftLeft(vector<T>& values, size_t positions, const T& fillValue) {
    if (values.empty()) {
        return;
    }

    const size_t count = min(positions, values.size());

    /*
        std::move is safe here because values are copied from left to right.
        For simple values such as integers, ordinary assignment has the same
        conceptual effect.
    */
    for (size_t index = 0; index + count < values.size(); ++index) {
        values[index] = std::move(values[index + count]);
    }

    for (size_t index = values.size() - count; index < values.size(); ++index) {
        values[index] = fillValue;
    }
}

template <typename T>
void shiftRight(vector<T>& values, size_t positions, const T& fillValue) {
    if (values.empty()) {
        return;
    }

    const size_t count = min(positions, values.size());

    /*
        The right-to-left direction is essential. Copying from left to right
        would overwrite values before they are moved.
    */
    for (size_t index = values.size(); index-- > count;) {
        values[index] = std::move(values[index - count]);
    }

    for (size_t index = 0; index < count; ++index) {
        values[index] = fillValue;
    }
}

// ---------------------------------------------------------------------------
// 7. ROTATION
// ---------------------------------------------------------------------------

template <typename T>
void reverseRange(vector<T>& values, size_t left, size_t right) {
    while (left < right) {
        swap(values[left], values[right]);
        ++left;
        --right;
    }
}

template <typename T>
void rotateLeft(vector<T>& values, size_t positions) {
    if (values.empty()) {
        return;
    }

    const size_t count = positions % values.size();

    if (count == 0) {
        return;
    }

    /*
        Reversal algorithm:
          1. reverse first k elements
          2. reverse remaining n-k elements
          3. reverse everything

        Complexity:
          Time  = O(n)
          Space = O(1) auxiliary
    */
    reverseRange(values, 0, count - 1);
    reverseRange(values, count, values.size() - 1);
    reverseRange(values, 0, values.size() - 1);
}

template <typename T>
void rotateRight(vector<T>& values, size_t positions) {
    if (values.empty()) {
        return;
    }

    const size_t count = positions % values.size();

    if (count == 0) {
        return;
    }

    rotateLeft(values, values.size() - count);
}

// ---------------------------------------------------------------------------
// 8. STABLE REARRANGEMENT
// ---------------------------------------------------------------------------

void moveCancelledToEnd(vector<Package>& packages) {
    /*
        stable_partition preserves relative order within both groups.
        It is useful when the business rule requires pending/active package
        order to remain unchanged.
    */
    stable_partition(
        packages.begin(),
        packages.end(),
        [](const Package& package) {
            return package.status != Status::Cancelled;
        }
    );
}

void moveHeavyPackagesToEnd(vector<Package>& packages, double threshold) {
    /*
        This operation deliberately does not require stability. partition()
        can rearrange elements in either group without preserving internal
        order, which is often preferable when only grouping matters.
    */
    partition(
        packages.begin(),
        packages.end(),
        [threshold](const Package& package) {
            return package.weight <= threshold;
        }
    );
}

// ---------------------------------------------------------------------------
// 9. SEARCHING
// ---------------------------------------------------------------------------

optional<size_t> linearSearch(
    const vector<Package>& packages,
    const string& packageId
) {
    for (size_t index = 0; index < packages.size(); ++index) {
        if (packages[index].id == packageId) {
            return index;
        }
    }

    return nullopt;
}

bool comparePackageId(const Package& package, const string& id) {
    return package.id < id;
}

optional<size_t> binarySearchPackage(
    const vector<Package>& sortedPackages,
    const string& packageId
) {
    /*
        Binary search is only valid because the vector is sorted by ID.
        lower_bound returns the first position that is not less than target.
    */
    auto iterator = lower_bound(
        sortedPackages.begin(),
        sortedPackages.end(),
        packageId,
        comparePackageId
    );

    if (iterator != sortedPackages.end() && iterator->id == packageId) {
        return static_cast<size_t>(
            distance(sortedPackages.begin(), iterator)
        );
    }

    return nullopt;
}

// ---------------------------------------------------------------------------
// 10. DUPLICATE DETECTION
// ---------------------------------------------------------------------------

vector<Package> removeDuplicatePackages(const vector<Package>& packages) {
    unordered_set<string> seen;
    vector<Package> uniquePackages;

    uniquePackages.reserve(packages.size());

    /*
        unordered_set gives average O(1) membership checks, so the entire
        operation is O(n) average time and O(n) additional memory.
    */
    for (const auto& package : packages) {
        if (seen.insert(package.id).second) {
            uniquePackages.push_back(package);
        }
    }

    return uniquePackages;
}

// ---------------------------------------------------------------------------
// 11. PRIORITY REARRANGEMENT
// ---------------------------------------------------------------------------

void arrangeByPriority(vector<Package>& packages) {
    /*
        stable_sort provides predictable ordering for equal priorities.
        This is useful when two packages have the same priority and the
        original arrival order should be retained.
    */
    stable_sort(
        packages.begin(),
        packages.end(),
        [](const Package& first, const Package& second) {
            return first.priority > second.priority;
        }
    );
}

// ---------------------------------------------------------------------------
// 12. BATCH PROCESSING SYSTEM
// ---------------------------------------------------------------------------

class FulfillmentSystem {
private:
    vector<Package> packages;

public:
    void receive(const Package& package) {
        validatePackage(package);

        /*
            Appending is amortized O(1). vector may occasionally allocate a
            larger memory block and move its existing elements.
        */
        packages.push_back(package);
    }

    void insertAt(size_t index, const Package& package) {
        insertPackage(packages, index, package);
    }

    bool cancel(const string& packageId) {
        auto position = linearSearch(packages, packageId);

        if (!position.has_value()) {
            return false;
        }

        packages[position.value()].status = Status::Cancelled;
        return true;
    }

    bool remove(size_t index) {
        if (index >= packages.size()) {
            return false;
        }

        deletePackage(packages, index);
        return true;
    }

    void prioritize() {
        arrangeByPriority(packages);
    }

    void rotateForNextShift(size_t offset) {
        rotateLeft(packages, offset);
    }

    void reverseForAudit() {
        reversePackages(packages);
    }

    void cleanCancelled() {
        moveCancelledToEnd(packages);
    }

    void removeDuplicates() {
        packages = removeDuplicatePackages(packages);
    }

    optional<Package> processNext() {
        if (packages.empty()) {
            return nullopt;
        }

        Package next = packages.front();
        packages.erase(packages.begin());
        return next;
    }

    const vector<Package>& getPackages() const {
        return packages;
    }
};

// ---------------------------------------------------------------------------
// 13. TEST HELPERS
// ---------------------------------------------------------------------------

void require(bool condition, const string& message) {
    if (!condition) {
        throw runtime_error("Test failed: " + message);
    }
}

bool sameIds(
    const vector<Package>& packages,
    const vector<string>& expected
) {
    if (packages.size() != expected.size()) {
        return false;
    }

    for (size_t index = 0; index < packages.size(); ++index) {
        if (packages[index].id != expected[index]) {
            return false;
        }
    }

    return true;
}

// ---------------------------------------------------------------------------
// 14. TESTS
// ---------------------------------------------------------------------------

void runTests() {
    cout << "\n=== Automated Tests ===\n";

    vector<int> values{1, 2, 3, 4, 5};
    rotateLeft(values, 2);
    require(
        values == vector<int>{3, 4, 5, 1, 2},
        "left rotation"
    );

    rotateRight(values, 2);
    require(
        values == vector<int>{1, 2, 3, 4, 5},
        "right rotation"
    );

    reverse(values.begin(), values.end());
    require(
        values == vector<int>{5, 4, 3, 2, 1},
        "reverse"
    );

    vector<int> shifted{1, 2, 3, 4, 5};
    shiftLeft(shifted, 2, 0);
    require(
        shifted == vector<int>{3, 4, 5, 0, 0},
        "left shift"
    );

    vector<int> shiftedRight{1, 2, 3, 4, 5};
    shiftRight(shiftedRight, 2, 0);
    require(
        shiftedRight == vector<int>{0, 0, 1, 2, 3},
        "right shift"
    );

    vector<Package> packages{
        {"A", 2, 2.0, Status::Pending},
        {"B", 5, 1.0, Status::Pending},
        {"C", 1, 4.0, Status::Pending}
    };

    rotateLeft(packages, 1);

    require(
        sameIds(packages, {"B", "C", "A"}),
        "package rotation"
    );

    auto position = linearSearch(packages, "C");
    require(position.has_value() && position.value() == 1,
            "linear search");

    cout << "All tests passed.\n";
}

// ---------------------------------------------------------------------------
// 15. PERFORMANCE BENCHMARK
// ---------------------------------------------------------------------------

void benchmarkRotation() {
    cout << "\n=== Performance Benchmark ===\n";

    constexpr size_t size = 500000;

    vector<int> values(size);
    iota(values.begin(), values.end(), 0);

    vector<int> inPlace = values;

    auto start = chrono::high_resolution_clock::now();

    rotateLeft(inPlace, 123456);

    auto end = chrono::high_resolution_clock::now();

    const auto inPlaceMicroseconds =
        chrono::duration_cast<chrono::microseconds>(
            end - start
        ).count();

    start = chrono::high_resolution_clock::now();

    const size_t offset = 123456 % values.size();

    /*
        This creates a second vector. It is straightforward but consumes
        additional memory proportional to n.
    */
    vector<int> copied;
    copied.reserve(values.size());

    copied.insert(
        copied.end(),
        values.begin() + static_cast<ptrdiff_t>(offset),
        values.end()
    );

    copied.insert(
        copied.end(),
        values.begin(),
        values.begin() + static_cast<ptrdiff_t>(offset)
    );

    end = chrono::high_resolution_clock::now();

    const auto copyMicroseconds =
        chrono::duration_cast<chrono::microseconds>(
            end - start
        ).count();

    cout << "In-place rotation: "
         << inPlaceMicroseconds
         << " microseconds\n";

    cout << "Copy-based rotation: "
         << copyMicroseconds
         << " microseconds\n";

    cout << "Both are O(n), but the copy-based method requires O(n) extra space.\n";

    // Keep the computed result observable.
    cout << "First values: "
         << inPlace.front()
         << ", "
         << copied.front()
         << "\n";
}

// ---------------------------------------------------------------------------
// 16. COMPLETE CASE STUDY
// ---------------------------------------------------------------------------

void runCaseStudy() {
    cout << "\n=== Warehouse Fulfillment Case Study ===\n";

    FulfillmentSystem system;

    system.receive({"PKG-100", 3, 2.5, Status::Pending});
    system.receive({"PKG-101", 7, 1.2, Status::Pending});
    system.receive({"PKG-102", 4, 8.4, Status::Processing});
    system.receive({"PKG-103", 9, 3.0, Status::Pending});

    // Inserting a high-priority package at a known location.
    system.insertAt(
        1,
        {"PKG-099", 10, 2.0, Status::Pending}
    );

    printPackages(
        system.getPackages(),
        "After receiving and inserting packages:"
    );

    system.cancel("PKG-102");

    printPackages(
        system.getPackages(),
        "After cancelling PKG-102:"
    );

    system.prioritize();

    printPackages(
        system.getPackages(),
        "After priority arrangement:"
    );

    system.rotateForNextShift(2);

    printPackages(
        system.getPackages(),
        "After rotating the processing sequence:"
    );

    system.cleanCancelled();

    printPackages(
        system.getPackages(),
        "After stable cancelled-package rearrangement:"
    );

    auto processed = system.processNext();

    if (processed.has_value()) {
        cout << "\nProcessed package: "
             << processed->id
             << "\n";
    }

    printPackages(
        system.getPackages(),
        "Remaining packages:"
    );
}

// ---------------------------------------------------------------------------
// 17. ERROR HANDLING DEMONSTRATION
// ---------------------------------------------------------------------------

void demonstrateErrors() {
    cout << "\n=== Error Handling ===\n";

    try {
        vector<Package> packages;

        insertPackage(
            packages,
            5,
            {"BAD", 2, 1.0, Status::Pending}
        );
    } catch (const exception& error) {
        cout << "Handled invalid insertion: "
             << error.what()
             << "\n";
    }

    try {
        Package invalid{"", 1, 2.0, Status::Pending};
        validatePackage(invalid);
    } catch (const exception& error) {
        cout << "Handled invalid package: "
             << error.what()
             << "\n";
    }

    try {
        vector<int> values{1, 2, 3};
        rotateLeft(values, 100);
        cout << "Rotation larger than array size handled safely.\n";
    } catch (const exception& error) {
        cout << "Unexpected error: "
             << error.what()
             << "\n";
    }
}

// ---------------------------------------------------------------------------
// 18. MAIN
// ---------------------------------------------------------------------------

int main() {
    try {
        cout << string(72, '=') << "\n";
        cout << "ARRAY MANIPULATION: C++17 TECHNICAL CASE STUDY\n";
        cout << string(72, '=') << "\n";

        vector<int> basics{10, 20, 30, 40, 50};

        cout << "\n=== Basic Operations ===\n";
        cout << "Original first element: " << basics.front() << "\n";

        basics[2] = 35;
        cout << "After updating index 2: ";

        for (int value : basics) {
            cout << value << " ";
        }

        cout << "\n";

        basics.push_back(60);
        cout << "After append: ";

        for (int value : basics) {
            cout << value << " ";
        }

        cout << "\n";

        runCaseStudy();
        demonstrateErrors();
        runTests();
        benchmarkRotation();

        cout << "\n=== Complexity Reference ===\n";
        cout << "Indexed vector access: O(1)\n";
        cout << "Update by index: O(1)\n";
        cout << "Push back: O(1) amortized\n";
        cout << "Insert near beginning: O(n)\n";
        cout << "Erase near beginning: O(n)\n";
        cout << "Linear search: O(n)\n";
        cout << "Binary search on sorted data: O(log n)\n";
        cout << "Reverse: O(n) time, O(1) auxiliary space\n";
        cout << "Reversal-based rotation: O(n) time, O(1) auxiliary space\n";
        cout << "unordered_set duplicate removal: O(n) average time, O(n) space\n";
        cout << "stable_sort: O(n log n) comparisons\n";

        cout << "\nProgram completed successfully.\n";
    } catch (const exception& error) {
        cerr << "Fatal error: " << error.what() << "\n";
        return 1;
    }

    return 0;
}
