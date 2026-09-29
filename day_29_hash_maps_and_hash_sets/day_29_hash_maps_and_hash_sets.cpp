#include <algorithm>
#include <chrono>
#include <cstddef>
#include <exception>
#include <iomanip>
#include <iostream>
#include <limits>
#include <list>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

/*
 * HASH MAPS AND HASH SETS
 * =======================
 *
 * Industry-style case study:
 * A transaction and inventory analytics engine for a retail platform.
 *
 * The system demonstrates:
 * - unordered_map as a hash map
 * - unordered_set as a hash set
 * - frequency counting
 * - duplicate detection
 * - indexing
 * - inventory management
 * - customer aggregation
 * - product lookup
 * - unique-user detection
 * - fraud-style duplicate transaction detection
 * - validation and error handling
 * - collision considerations
 * - custom hashing
 * - load-factor and bucket behavior
 * - complexity trade-offs
 * - realistic modular design
 *
 * Compile with:
 *   g++ -std=c++17 -O2 hash_maps_sets.cpp -o hash_maps_sets
 *
 * The implementation uses only the C++ standard library.
 */


// ============================================================================
// 1. DOMAIN MODEL
// ============================================================================

struct Transaction {
    std::string transactionId;
    std::string customerId;
    std::string productId;
    double amount{};
};

struct Product {
    std::string productId;
    std::string name;
    double unitPrice{};
    int stock{};
};


// ============================================================================
// 2. CUSTOM HASH FUNCTION
// ============================================================================
//
// std::unordered_map and std::unordered_set need a hash function for their
// keys. Standard strings already have std::hash<std::string>.
//
// This example demonstrates how a custom domain type can become a hash key.

struct ProductKey {
    std::string category;
    int productNumber{};

    bool operator==(const ProductKey& other) const {
        return category == other.category &&
               productNumber == other.productNumber;
    }
};

struct ProductKeyHash {
    std::size_t operator()(const ProductKey& key) const {
        const std::size_t firstHash =
            std::hash<std::string>{}(key.category);

        const std::size_t secondHash =
            std::hash<int>{}(key.productNumber);

        // A common hash-combination technique.
        return firstHash ^
               (secondHash + static_cast<std::size_t>(0x9e3779b9) +
                (firstHash << 6) +
                (firstHash >> 2));
    }
};


// ============================================================================
// 3. INVENTORY INDEX
// ============================================================================

class InventoryIndex {
private:
    // Product ID is the key because product lookup is a frequent operation.
    std::unordered_map<std::string, Product> products_;

public:
    void addProduct(const Product& product) {
        if (product.productId.empty()) {
            throw std::invalid_argument("Product ID cannot be empty.");
        }

        if (product.stock < 0) {
            throw std::invalid_argument("Stock cannot be negative.");
        }

        if (product.unitPrice < 0.0) {
            throw std::invalid_argument("Unit price cannot be negative.");
        }

        // insert_or_assign supports both insertion and replacement.
        products_.insert_or_assign(product.productId, product);
    }

    bool contains(std::string_view productId) const {
        return products_.find(std::string(productId)) != products_.end();
    }

    const Product& get(std::string_view productId) const {
        auto iterator = products_.find(std::string(productId));

        if (iterator == products_.end()) {
            throw std::out_of_range("Product not found.");
        }

        return iterator->second;
    }

    void increaseStock(std::string_view productId, int quantity) {
        if (quantity <= 0) {
            throw std::invalid_argument(
                "Stock increase must be positive."
            );
        }

        auto iterator = products_.find(std::string(productId));

        if (iterator == products_.end()) {
            throw std::out_of_range("Product not found.");
        }

        iterator->second.stock += quantity;
    }

    void decreaseStock(std::string_view productId, int quantity) {
        if (quantity <= 0) {
            throw std::invalid_argument(
                "Stock decrease must be positive."
            );
        }

        auto iterator = products_.find(std::string(productId));

        if (iterator == products_.end()) {
            throw std::out_of_range("Product not found.");
        }

        if (quantity > iterator->second.stock) {
            throw std::runtime_error("Insufficient stock.");
        }

        iterator->second.stock -= quantity;
    }

    std::size_t size() const {
        return products_.size();
    }

    void printProducts() const {
        std::cout << "\nInventory index:\n";

        for (const auto& [productId, product] : products_) {
            std::cout
                << "  " << productId
                << " | " << product.name
                << " | price=" << product.unitPrice
                << " | stock=" << product.stock
                << '\n';
        }
    }
};


// ============================================================================
// 4. CUSTOMER TRANSACTION INDEX
// ============================================================================

class TransactionAnalytics {
private:
    std::unordered_map<std::string, std::vector<Transaction>>
        transactionsByCustomer_;

    std::unordered_map<std::string, double>
        customerSpending_;

    std::unordered_set<std::string>
        knownTransactionIds_;

public:
    bool addTransaction(const Transaction& transaction) {
        if (transaction.transactionId.empty()) {
            throw std::invalid_argument(
                "Transaction ID cannot be empty."
            );
        }

        if (transaction.customerId.empty()) {
            throw std::invalid_argument(
                "Customer ID cannot be empty."
            );
        }

        if (transaction.productId.empty()) {
            throw std::invalid_argument(
                "Product ID cannot be empty."
            );
        }

        if (transaction.amount < 0.0) {
            throw std::invalid_argument(
                "Transaction amount cannot be negative."
            );
        }

        // A set gives average O(1) duplicate detection.
        if (knownTransactionIds_.contains(transaction.transactionId)) {
            return false;
        }

        knownTransactionIds_.insert(transaction.transactionId);

        transactionsByCustomer_[transaction.customerId]
            .push_back(transaction);

        customerSpending_[transaction.customerId] +=
            transaction.amount;

        return true;
    }

    double spendingForCustomer(
        const std::string& customerId
    ) const {
        auto iterator = customerSpending_.find(customerId);

        if (iterator == customerSpending_.end()) {
            return 0.0;
        }

        return iterator->second;
    }

    std::size_t transactionCountForCustomer(
        const std::string& customerId
    ) const {
        auto iterator = transactionsByCustomer_.find(customerId);

        if (iterator == transactionsByCustomer_.end()) {
            return 0;
        }

        return iterator->second.size();
    }

    void printCustomerReport() const {
        std::cout << "\nCustomer analytics:\n";

        for (const auto& [customerId, transactions] :
             transactionsByCustomer_) {
            std::cout
                << "  Customer " << customerId
                << " | transactions=" << transactions.size()
                << " | spending="
                << spendingForCustomer(customerId)
                << '\n';
        }
    }
};


// ============================================================================
// 5. PRODUCT FREQUENCY ANALYTICS
// ============================================================================

class ProductAnalytics {
private:
    std::unordered_map<std::string, std::size_t> purchaseCounts_;

public:
    void recordPurchase(const std::string& productId) {
        ++purchaseCounts_[productId];
    }

    std::size_t count(const std::string& productId) const {
        auto iterator = purchaseCounts_.find(productId);

        if (iterator == purchaseCounts_.end()) {
            return 0;
        }

        return iterator->second;
    }

    std::vector<std::pair<std::string, std::size_t>>
    topProducts(std::size_t limit) const {
        std::vector<std::pair<std::string, std::size_t>> results(
            purchaseCounts_.begin(),
            purchaseCounts_.end()
        );

        std::sort(
            results.begin(),
            results.end(),
            [](const auto& left, const auto& right) {
                if (left.second != right.second) {
                    return left.second > right.second;
                }

                return left.first < right.first;
            }
        );

        if (results.size() > limit) {
            results.resize(limit);
        }

        return results;
    }
};


// ============================================================================
// 6. UNIQUE CUSTOMER SEGMENT
// ============================================================================
//
// A hash set is appropriate when we need membership rather than a value.

class CustomerSegment {
private:
    std::unordered_set<std::string> customerIds_;

public:
    void add(const std::string& customerId) {
        if (customerId.empty()) {
            throw std::invalid_argument(
                "Customer ID cannot be empty."
            );
        }

        customerIds_.insert(customerId);
    }

    bool contains(const std::string& customerId) const {
        return customerIds_.contains(customerId);
    }

    std::size_t size() const {
        return customerIds_.size();
    }

    void remove(const std::string& customerId) {
        customerIds_.erase(customerId);
    }

    std::unordered_set<std::string>
    intersection(const CustomerSegment& other) const {
        std::unordered_set<std::string> result;

        // Iterate over the smaller set when possible.
        const auto* smaller = &customerIds_;
        const auto* larger = &other.customerIds_;

        if (smaller->size() > larger->size()) {
            std::swap(smaller, larger);
        }

        for (const auto& customerId : *smaller) {
            if (larger->contains(customerId)) {
                result.insert(customerId);
            }
        }

        return result;
    }
};


// ============================================================================
// 7. DUPLICATE TRANSACTION DETECTOR
// ============================================================================

class DuplicateTransactionDetector {
private:
    std::unordered_set<std::string> seen_;

public:
    bool isDuplicate(const std::string& transactionId) {
        auto [iterator, inserted] = seen_.insert(transactionId);

        // inserted == false means the key was already present.
        return !inserted;
    }
};


// ============================================================================
// 8. INVENTORY VALUE CALCULATION
// ============================================================================

double calculateInventoryValue(
    const InventoryIndex& inventory,
    const std::vector<std::string>& productIds
) {
    double total = 0.0;

    for (const auto& productId : productIds) {
        if (!inventory.contains(productId)) {
            continue;
        }

        const Product& product = inventory.get(productId);

        total += product.unitPrice *
                 static_cast<double>(product.stock);
    }

    return total;
}


// ============================================================================
// 9. HASH-TABLE INTERNAL METRICS
// ============================================================================

void printHashTableMetrics(
    const std::unordered_map<std::string, Product>& products
) {
    std::cout << "\nHash-table metrics:\n";
    std::cout << "  Size: " << products.size() << '\n';
    std::cout << "  Bucket count: " << products.bucket_count() << '\n';
    std::cout << "  Load factor: "
              << products.load_factor()
              << '\n';
    std::cout << "  Max load factor: "
              << products.max_load_factor()
              << '\n';

    /*
     * The load factor is approximately:
     *
     *     number_of_elements / number_of_buckets
     *
     * Higher load factors can mean more collisions.
     *
     * Implementations may rehash automatically when necessary.
     */
}


// ============================================================================
// 10. SET OPERATIONS
// ============================================================================

template <typename T>
std::unordered_set<T> setUnion(
    const std::unordered_set<T>& first,
    const std::unordered_set<T>& second
) {
    std::unordered_set<T> result = first;

    result.insert(second.begin(), second.end());

    return result;
}


template <typename T>
std::unordered_set<T> setIntersection(
    const std::unordered_set<T>& first,
    const std::unordered_set<T>& second
) {
    const auto* smaller = &first;
    const auto* larger = &second;

    if (smaller->size() > larger->size()) {
        std::swap(smaller, larger);
    }

    std::unordered_set<T> result;

    for (const auto& value : *smaller) {
        if (larger->contains(value)) {
            result.insert(value);
        }
    }

    return result;
}


template <typename T>
std::unordered_set<T> setDifference(
    const std::unordered_set<T>& first,
    const std::unordered_set<T>& second
) {
    std::unordered_set<T> result;

    for (const auto& value : first) {
        if (!second.contains(value)) {
            result.insert(value);
        }
    }

    return result;
}


// ============================================================================
// 11. PRINT HELPERS
// ============================================================================

template <typename T>
void printSet(
    const std::unordered_set<T>& values,
    const std::string& label
) {
    std::cout << label << ": {";

    bool first = true;

    for (const auto& value : values) {
        if (!first) {
            std::cout << ", ";
        }

        std::cout << value;
        first = false;
    }

    std::cout << "}\n";
}


// ============================================================================
// 12. REALISTIC DATASET
// ============================================================================

std::vector<Product> createProducts() {
    return {
        {"P100", "Laptop", 85000.0, 10},
        {"P101", "Mechanical Keyboard", 6500.0, 30},
        {"P102", "Wireless Mouse", 2500.0, 50},
        {"P103", "Monitor", 22000.0, 15},
        {"P104", "USB-C Hub", 3500.0, 40}
    };
}


std::vector<Transaction> createTransactions() {
    return {
        {"T001", "C001", "P100", 85000.0},
        {"T002", "C002", "P102", 2500.0},
        {"T003", "C001", "P101", 6500.0},
        {"T004", "C003", "P103", 22000.0},
        {"T005", "C002", "P102", 2500.0},
        {"T006", "C001", "P102", 2500.0},
        {"T006", "C001", "P102", 2500.0}
    };
}


// ============================================================================
// 13. PERFORMANCE CASE STUDY
// ============================================================================

void performanceCaseStudy(std::size_t elementCount) {
    std::cout << "\n=== Performance Case Study ===\n";

    std::vector<int> values;
    values.reserve(elementCount);

    for (std::size_t index = 0; index < elementCount; ++index) {
        values.push_back(static_cast<int>(index));
    }

    std::unordered_set<int> lookupSet;
    lookupSet.reserve(elementCount);

    for (int value : values) {
        lookupSet.insert(value);
    }

    const int target =
        static_cast<int>(elementCount - 1);

    auto listStart = std::chrono::high_resolution_clock::now();

    const bool foundInVector =
        std::find(values.begin(), values.end(), target)
        != values.end();

    auto listEnd = std::chrono::high_resolution_clock::now();

    auto setStart = std::chrono::high_resolution_clock::now();

    const bool foundInSet =
        lookupSet.contains(target);

    auto setEnd = std::chrono::high_resolution_clock::now();

    const auto vectorTime =
        std::chrono::duration<double, std::micro>(
            listEnd - listStart
        ).count();

    const auto setTime =
        std::chrono::duration<double, std::micro>(
            setEnd - setStart
        ).count();

    std::cout << "Vector found: " << std::boolalpha
              << foundInVector << '\n';

    std::cout << "Hash set found: "
              << foundInSet << '\n';

    std::cout << std::fixed << std::setprecision(3);

    std::cout << "Vector membership time: "
              << vectorTime
              << " microseconds\n";

    std::cout << "Hash-set membership time: "
              << setTime
              << " microseconds\n";

    /*
     * Vector search is O(n).
     * unordered_set membership is average O(1).
     *
     * A hash set may consume substantially more memory than a vector.
     * For small collections or cache-sensitive workloads, a vector can still
     * be preferable despite its O(n) search complexity.
     */
}


// ============================================================================
// 14. CUSTOM HASH KEY DEMONSTRATION
// ============================================================================

void demonstrateCustomHashKey() {
    std::cout << "\n=== Custom Hash Key ===\n";

    std::unordered_map<
        ProductKey,
        std::string,
        ProductKeyHash
    > catalog;

    catalog[{ "electronics", 100 }] = "Laptop";
    catalog[{ "electronics", 101 }] = "Monitor";
    catalog[{ "office", 200 }] = "Desk";

    ProductKey lookupKey{"electronics", 100};

    auto iterator = catalog.find(lookupKey);

    if (iterator != catalog.end()) {
        std::cout << "Custom-key lookup: "
                  << iterator->second
                  << '\n';
    }
}


// ============================================================================
// 15. FAILURE CONDITIONS
// ============================================================================

void demonstrateFailureConditions(InventoryIndex& inventory) {
    std::cout << "\n=== Failure Conditions ===\n";

    try {
        inventory.get("UNKNOWN");
    } catch (const std::exception& error) {
        std::cout << "Lookup error: "
                  << error.what()
                  << '\n';
    }

    try {
        inventory.decreaseStock("P100", 100000);
    } catch (const std::exception& error) {
        std::cout << "Stock error: "
                  << error.what()
                  << '\n';
    }

    try {
        inventory.addProduct(
            Product{"", "Invalid", 100.0, 1}
        );
    } catch (const std::exception& error) {
        std::cout << "Validation error: "
                  << error.what()
                  << '\n';
    }
}


// ============================================================================
// 16. COMPLETE SYSTEM DEMONSTRATION
// ============================================================================

void runCaseStudy() {
    std::cout << "HASH MAPS AND HASH SETS\n";
    std::cout << "Retail Transaction and Inventory Analytics Engine\n";

    InventoryIndex inventory;

    for (const auto& product : createProducts()) {
        inventory.addProduct(product);
    }

    inventory.printProducts();

    TransactionAnalytics analytics;
    ProductAnalytics productAnalytics;

    DuplicateTransactionDetector duplicateDetector;

    for (const auto& transaction : createTransactions()) {
        const bool duplicate =
            duplicateDetector.isDuplicate(
                transaction.transactionId
            );

        if (duplicate) {
            std::cout
                << "\nDuplicate transaction rejected: "
                << transaction.transactionId
                << '\n';

            continue;
        }

        if (!analytics.addTransaction(transaction)) {
            std::cout
                << "Transaction already exists: "
                << transaction.transactionId
                << '\n';

            continue;
        }

        productAnalytics.recordPurchase(
            transaction.productId
        );
    }

    analytics.printCustomerReport();

    std::cout << "\nProduct purchase counts:\n";

    for (const auto& [productId, count] :
         productAnalytics.topProducts(10)) {
        std::cout
            << "  " << productId
            << " -> " << count
            << '\n';
    }

    std::cout << "\nCustomer C001 spending: "
              << analytics.spendingForCustomer("C001")
              << '\n';

    std::cout << "Customer C001 transaction count: "
              << analytics.transactionCountForCustomer("C001")
              << '\n';

    const double inventoryValue =
        calculateInventoryValue(
            inventory,
            {"P100", "P101", "P102", "P103"}
        );

    std::cout << "\nSelected inventory value: "
              << inventoryValue
              << '\n';

    CustomerSegment premiumCustomers;
    premiumCustomers.add("C001");
    premiumCustomers.add("C002");
    premiumCustomers.add("C004");

    CustomerSegment activeCustomers;
    activeCustomers.add("C002");
    activeCustomers.add("C003");
    activeCustomers.add("C004");

    printSet(
        premiumCustomers.intersection(activeCustomers),
        "Premium and active customers"
    );

    demonstrateFailureConditions(inventory);
    demonstrateCustomHashKey();
    performanceCaseStudy(100000);
}


// ============================================================================
// 17. SELF-TESTS
// ============================================================================

void runTests() {
    std::cout << "\n=== Self-Tests ===\n";

    std::unordered_map<std::string, int> frequency;

    for (char character : std::string("banana")) {
        ++frequency[std::string(1, character)];
    }

    if (frequency["a"] != 3 ||
        frequency["n"] != 2 ||
        frequency["b"] != 1) {
        throw std::runtime_error(
            "Frequency-count test failed."
        );
    }

    std::unordered_set<int> values{1, 2, 3};

    if (!values.contains(2)) {
        throw std::runtime_error(
            "Set membership test failed."
        );
    }

    values.insert(2);

    if (values.size() != 3) {
        throw std::runtime_error(
            "Set uniqueness test failed."
        );
    }

    std::unordered_map<int, int> twoSumIndex;
    const std::vector<int> numbers{2, 7, 11, 15};
    const int target = 9;

    std::optional<std::pair<int, int>> result;

    for (int index = 0;
         index < static_cast<int>(numbers.size());
         ++index) {
        const int complement = target - numbers[index];

        auto iterator = twoSumIndex.find(complement);

        if (iterator != twoSumIndex.end()) {
            result = std::make_pair(
                iterator->second,
                index
            );

            break;
        }

        twoSumIndex[numbers[index]] = index;
    }

    if (!result.has_value() ||
        result->first != 0 ||
        result->second != 1) {
        throw std::runtime_error(
            "Two-sum test failed."
        );
    }

    InventoryIndex inventory;

    inventory.addProduct(
        Product{"TEST", "Test Product", 10.0, 5}
    );

    if (!inventory.contains("TEST")) {
        throw std::runtime_error(
            "Inventory insertion test failed."
        );
    }

    inventory.decreaseStock("TEST", 5);

    if (inventory.get("TEST").stock != 0) {
        throw std::runtime_error(
            "Inventory update test failed."
        );
    }

    std::cout << "All tests passed.\n";
}


// ============================================================================
// 18. MAIN
// ============================================================================

int main() {
    try {
        runCaseStudy();
        runTests();

        std::cout << "\nProgram completed successfully.\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr
            << "Fatal error: "
            << error.what()
            << '\n';

        return 1;
    }
}
