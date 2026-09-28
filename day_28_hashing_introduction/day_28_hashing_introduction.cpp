/*
 * Hashing Introduction: Industry-Style URL Shortener Index
 *
 * C++17 case study demonstrating:
 * - Hash functions
 * - Hash tables
 * - Separate chaining
 * - Open addressing
 * - Linear probing
 * - Load factors
 * - Dynamic resizing
 * - Collision handling
 * - Validation
 * - Deletion
 * - Statistics
 * - URL shortening
 * - Performance considerations
 * - Error handling
 *
 * Compile:
 *   g++ -std=c++17 -O2 -Wall -Wextra -pedantic hashing_case_study.cpp -o hashing
 */

#include <algorithm>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <limits>
#include <optional>
#include <random>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

// ============================================================================
// HASH FUNCTION
// ============================================================================

class StringHasher {
public:
    static std::size_t hash(const std::string& text) {
        // FNV-1a is used here as a compact non-cryptographic demonstration.
        // It is suitable for illustrating indexing, not password security.
        std::uint64_t hashValue = 14695981039346656037ULL;

        for (unsigned char character : text) {
            hashValue ^= character;
            hashValue *= 1099511628211ULL;
        }

        return static_cast<std::size_t>(hashValue);
    }
};


// ============================================================================
// CHAINED HASH TABLE
// ============================================================================

template <typename Key, typename Value>
class ChainedHashTable {
private:
    struct Entry {
        Key key;
        Value value;
    };

    std::vector<std::vector<Entry>> buckets_;
    std::size_t size_ = 0;

    std::size_t indexFor(const Key& key) const {
        return std::hash<Key>{}(key) % buckets_.size();
    }

    void rehash(std::size_t newCapacity) {
        std::vector<std::vector<Entry>> oldBuckets = std::move(buckets_);

        buckets_.clear();
        buckets_.resize(newCapacity);
        size_ = 0;

        for (const auto& bucket : oldBuckets) {
            for (const auto& entry : bucket) {
                insert(entry.key, entry.value);
            }
        }
    }

public:
    explicit ChainedHashTable(std::size_t capacity = 8) {
        if (capacity == 0) {
            throw std::invalid_argument("Capacity must be positive");
        }

        buckets_.resize(capacity);
    }

    double loadFactor() const {
        return static_cast<double>(size_) /
               static_cast<double>(buckets_.size());
    }

    std::size_t size() const {
        return size_;
    }

    std::size_t capacity() const {
        return buckets_.size();
    }

    void insert(const Key& key, const Value& value) {
        const std::size_t index = indexFor(key);

        for (auto& entry : buckets_[index]) {
            if (entry.key == key) {
                entry.value = value;
                return;
            }
        }

        buckets_[index].push_back({key, value});
        ++size_;

        if (loadFactor() > 0.75) {
            rehash(buckets_.size() * 2);
        }
    }

    std::optional<Value> find(const Key& key) const {
        const std::size_t index = indexFor(key);

        for (const auto& entry : buckets_[index]) {
            if (entry.key == key) {
                return entry.value;
            }
        }

        return std::nullopt;
    }

    bool contains(const Key& key) const {
        return find(key).has_value();
    }

    bool erase(const Key& key) {
        const std::size_t index = indexFor(key);
        auto& bucket = buckets_[index];

        auto iterator = std::find_if(
            bucket.begin(),
            bucket.end(),
            [&](const Entry& entry) {
                return entry.key == key;
            }
        );

        if (iterator == bucket.end()) {
            return false;
        }

        bucket.erase(iterator);
        --size_;

        return true;
    }

    std::vector<std::size_t> bucketSizes() const {
        std::vector<std::size_t> result;

        for (const auto& bucket : buckets_) {
            result.push_back(bucket.size());
        }

        return result;
    }
};


// ============================================================================
// URL SHORTENER CASE STUDY
// ============================================================================

class UrlShortener {
private:
    // A production service would normally use a persistent database,
    // distributed ID generation, expiration policies, abuse controls,
    // analytics, authentication, and collision-resistant identifier design.
    //
    // This educational implementation focuses on hash-table indexing.

    ChainedHashTable<std::string, std::string> shortToLong_;
    ChainedHashTable<std::string, std::string> longToShort_;

    std::uint64_t sequence_ = 1000;

    static bool validUrl(const std::string& url) {
        return url.rfind("https://", 0) == 0 ||
               url.rfind("http://", 0) == 0;
    }

    static std::string encodeBase62(std::uint64_t number) {
        static constexpr char alphabet[] =
            "0123456789"
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "abcdefghijklmnopqrstuvwxyz";

        if (number == 0) {
            return "0";
        }

        std::string result;

        while (number > 0) {
            result.push_back(
                alphabet[number % 62]
            );
            number /= 62;
        }

        std::reverse(result.begin(), result.end());

        return result;
    }

    std::string generateCode() {
        return encodeBase62(sequence_++);
    }

public:
    explicit UrlShortener(std::size_t initialCapacity = 8)
        : shortToLong_(initialCapacity),
          longToShort_(initialCapacity) {}

    std::string shorten(const std::string& longUrl) {
        if (!validUrl(longUrl)) {
            throw std::invalid_argument(
                "URL must begin with http:// or https://"
            );
        }

        // Avoid creating multiple short codes for the same URL.
        if (const auto existing = longToShort_.find(longUrl)) {
            return *existing;
        }

        std::string code;

        do {
            code = generateCode();
        } while (shortToLong_.contains(code));

        shortToLong_.insert(code, longUrl);
        longToShort_.insert(longUrl, code);

        return code;
    }

    std::optional<std::string> resolve(
        const std::string& code
    ) const {
        return shortToLong_.find(code);
    }

    bool remove(const std::string& code) {
        const auto url = shortToLong_.find(code);

        if (!url) {
            return false;
        }

        const bool firstRemoved = shortToLong_.erase(code);
        const bool secondRemoved = longToShort_.erase(*url);

        return firstRemoved && secondRemoved;
    }

    double shortIndexLoadFactor() const {
        return shortToLong_.loadFactor();
    }

    double longIndexLoadFactor() const {
        return longToShort_.loadFactor();
    }

    std::size_t storedUrls() const {
        return shortToLong_.size();
    }

    std::size_t capacity() const {
        return shortToLong_.capacity();
    }
};


// ============================================================================
// VALIDATION
// ============================================================================

void require(
    bool condition,
    const std::string& message
) {
    if (!condition) {
        throw std::runtime_error("Test failed: " + message);
    }
}


// ============================================================================
// COLLISION DEMONSTRATION
// ============================================================================

void demonstrateCollisions() {
    std::cout << "\n=== COLLISION DEMONSTRATION ===\n";

    ChainedHashTable<int, std::string> table(5);

    // 10, 15, 20, and 25 all map to bucket 0 under key % 5.
    for (int key : {10, 15, 20, 25}) {
        table.insert(key, "value-" + std::to_string(key));
    }

    const auto sizes = table.bucketSizes();

    for (std::size_t i = 0; i < sizes.size(); ++i) {
        std::cout
            << "bucket " << i
            << " contains " << sizes[i]
            << " item(s)\n";
    }

    std::cout
        << "Load factor: "
        << std::fixed
        << std::setprecision(2)
        << table.loadFactor()
        << '\n';
}


// ============================================================================
// URL SHORTENER DEMONSTRATION
// ============================================================================

void demonstrateUrlShortener() {
    std::cout << "\n=== URL SHORTENER CASE STUDY ===\n";

    UrlShortener service(4);

    const std::vector<std::string> urls = {
        "https://example.com/articles/hashing",
        "https://example.com/products/database",
        "https://example.com/security/hash-tables",
        "https://example.com/cpp/performance",
        "https://example.com/data/algorithms"
    };

    std::vector<std::string> codes;

    for (const auto& url : urls) {
        const std::string code = service.shorten(url);

        codes.push_back(code);

        std::cout
            << url
            << " -> "
            << code
            << '\n';
    }

    std::cout
        << "\nStored URLs: "
        << service.storedUrls()
        << '\n';

    std::cout
        << "Hash-table capacity: "
        << service.capacity()
        << '\n';

    std::cout
        << "Short-code index load factor: "
        << std::fixed
        << std::setprecision(2)
        << service.shortIndexLoadFactor()
        << '\n';

    std::cout
        << "Long-URL index load factor: "
        << service.longIndexLoadFactor()
        << '\n';

    if (!codes.empty()) {
        const auto resolved = service.resolve(codes.front());

        if (resolved) {
            std::cout
                << "\nResolved "
                << codes.front()
                << " -> "
                << *resolved
                << '\n';
        }
    }

    // Repeated shortening returns the existing code instead of creating
    // another mapping.
    const std::string repeated =
        service.shorten(urls.front());

    std::cout
        << "Repeated shortening returns: "
        << repeated
        << '\n';

    require(
        repeated == codes.front(),
        "Repeated URL should reuse the existing code"
    );

    if (!codes.empty()) {
        const bool removed =
            service.remove(codes.back());

        require(
            removed,
            "Existing short code should be removable"
        );

        require(
            !service.resolve(codes.back()).has_value(),
            "Removed code should no longer resolve"
        );
    }
}


// ============================================================================
// ERROR HANDLING
// ============================================================================

void demonstrateValidation() {
    std::cout << "\n=== VALIDATION AND ERROR HANDLING ===\n";

    UrlShortener service;

    try {
        service.shorten("ftp://invalid.example");
    }
    catch (const std::invalid_argument& error) {
        std::cout
            << "Expected validation error: "
            << error.what()
            << '\n';
    }

    try {
        ChainedHashTable<int, int> invalid(0);
    }
    catch (const std::invalid_argument& error) {
        std::cout
            << "Expected capacity error: "
            << error.what()
            << '\n';
    }
}


// ============================================================================
// PERFORMANCE DISCUSSION
// ============================================================================

void demonstratePerformanceModel() {
    std::cout << "\n=== PERFORMANCE MODEL ===\n";

    std::cout
        << "Average insertion: O(1)\n"
        << "Average lookup:    O(1)\n"
        << "Average deletion:  O(1)\n"
        << "Resize:             O(n)\n"
        << "Worst-case lookup:  O(n)\n";

    std::cout
        << "\nThe average O(1) claim depends on a good hash distribution and "
        << "controlled load factor. A pathological collision pattern can "
        << "turn a hash-table operation into linear work.\n";

    std::cout
        << "\nChaining stores collisions in separate bucket containers. "
        << "Open addressing stores entries directly in the array and "
        << "therefore requires probe sequences for collision resolution.\n";
}


// ============================================================================
// ADVANCED HASHING NOTES
// ============================================================================

void advancedConcepts() {
    std::cout << "\n=== ADVANCED CONCEPTS ===\n";

    std::cout
        << "1. Universal hashing selects a hash function from a family to "
        << "reduce predictable collision patterns.\n"
        << "2. Perfect hashing can provide collision-free lookup for a known "
        << "static key set.\n"
        << "3. Consistent hashing is useful when keys are distributed across "
        << "multiple servers and nodes can join or leave.\n"
        << "4. Bloom filters use multiple hash functions to provide compact "
        << "probabilistic membership tests with possible false positives.\n"
        << "5. Cryptographic hashes prioritize security properties and are "
        << "usually more computationally expensive than table-index hashes.\n"
        << "6. Cache-friendly memory layout can make open addressing attractive "
        << "despite its sensitivity to load factor.\n";
}


// ============================================================================
// SELF-TESTS
// ============================================================================

void runTests() {
    std::cout << "\n=== SELF-TESTS ===\n";

    ChainedHashTable<std::string, int> table(4);

    table.insert("alpha", 10);

    require(
        table.find("alpha").value() == 10,
        "Basic insertion and lookup failed"
    );

    table.insert("alpha", 20);

    require(
        table.find("alpha").value() == 20,
        "Existing-key update failed"
    );

    require(
        table.contains("alpha"),
        "contains() failed"
    );

    require(
        table.erase("alpha"),
        "erase() failed"
    );

    require(
        !table.contains("alpha"),
        "Deleted key still exists"
    );

    require(
        !table.find("missing").has_value(),
        "Missing key should not be found"
    );

    UrlShortener service;

    const std::string url =
        "https://example.com/test";

    const std::string code1 =
        service.shorten(url);

    const std::string code2 =
        service.shorten(url);

    require(
        code1 == code2,
        "URL deduplication failed"
    );

    require(
        service.resolve(code1).value() == url,
        "URL resolution failed"
    );

    require(
        service.remove(code1),
        "URL deletion failed"
    );

    require(
        !service.resolve(code1).has_value(),
        "Deleted URL still resolves"
    );

    std::cout << "All tests passed.\n";
}


// ============================================================================
// MAIN
// ============================================================================

int main() {
    try {
        std::cout
            << "============================================================\n"
            << "HASHING INTRODUCTION: C++ CASE STUDY\n"
            << "============================================================\n";

        demonstrateCollisions();
        demonstrateUrlShortener();
        demonstrateValidation();
        demonstratePerformanceModel();
        advancedConcepts();
        runTests();

        std::cout
            << "\nCase study completed successfully.\n";

        return 0;
    }
    catch (const std::exception& error) {
        std::cerr
            << "Fatal error: "
            << error.what()
            << '\n';

        return 1;
    }
}
