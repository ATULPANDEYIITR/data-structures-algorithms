# Hashing Introduction

## Topic

This study covers the fundamental and practical concepts behind hashing and hash tables, including hash functions, table indexing, collisions, separate chaining, open addressing, probing strategies, load factors, resizing, deletion, complexity, applications, implementation details, and security considerations.

The three implementations approach the subject from different perspectives:

- Python develops the concepts incrementally and provides several reusable implementations and algorithmic examples.
- JavaScript demonstrates hashing through custom data structures as well as native `Map` and `Set`, including object-key behavior and asynchronous application-level caching.
- C++ develops an industry-style URL-shortener indexing system using a dynamically resizing chained hash table.

---

## 1. What Is Hashing?

Hashing is a technique for transforming a key into a value that can be used to locate information efficiently.

A hash function accepts an input key and produces a hash value. When the hash value is mapped into the range of a table, it determines a bucket or slot where the associated data can be stored.

A simplified model is:

`index = hash(key) mod table_capacity`

For example, with a table containing 10 slots:

`hash(42) mod 10 = 2`

The key can therefore initially be associated with slot 2.

Hashing is useful because it can reduce the amount of searching required for common operations. Under favorable conditions, hash-table insertion, lookup, and deletion have average-case constant-time complexity, written as O(1).

This does not mean that every hash-table operation is guaranteed to take exactly one operation. Collisions, poor hash functions, high load factors, resizing, and adversarial inputs can increase the actual work.

---

## 2. Important Terminology

### Key

A key identifies an item.

Examples include:

- user ID
- username
- product code
- URL
- database record identifier
- word
- IP address

### Value

A value is the data associated with a key.

For example:

`"user:1001" -> "Atul"`

The first part is the key and the second part is the value.

### Hash Function

A hash function maps a key to a numeric hash value.

A table then converts that hash value into a valid array index.

### Bucket

A bucket is a logical storage location associated with a particular hash-table index.

A bucket may contain:

- one item,
- several colliding items,
- or no items.

### Slot

In open addressing, a slot is a position directly inside the table array.

### Collision

A collision occurs when two different keys map to the same table position.

For example, with capacity 5:

`10 mod 5 = 0`

`15 mod 5 = 0`

Therefore, 10 and 15 collide.

Collisions are normal and must be handled by the data structure.

### Load Factor

The load factor is:

`α = number of stored elements / table capacity`

For example:

`7 / 10 = 0.70`

A higher load factor generally means a more crowded table.

### Rehashing

Rehashing means creating a new table, usually with a larger capacity, and inserting existing elements into the new table using the new capacity.

The indexes can change because:

`hash(key) mod old_capacity`

and

`hash(key) mod new_capacity`

can produce different results.

---

## 3. Properties of a Useful Hash Function

A hash function used by a hash table should generally have the following properties.

### Determinism

The same key should produce the same hash value under the same hashing rules.

### Efficiency

The function should be fast enough that calculating the hash does not dominate the cost of the operation.

### Good Distribution

Keys should be spread reasonably evenly throughout the table.

A poor distribution can create large collision groups.

### Bounded Indexing

A hash table needs a valid table position. A common technique is:

`index = hash_value mod capacity`

### Low Clustering

Related keys should not systematically map to nearby positions when that behavior would create excessive collisions.

---

## 4. Hashing Is Not the Same as Encryption

Hashing and encryption solve different problems.

Encryption is designed to transform information into ciphertext that can be reversed using the appropriate key.

Hashing normally produces a fixed-size representation of input data.

A hash-table hash is optimized primarily for efficient indexing and distribution.

A cryptographic hash such as SHA-256 is designed around security properties such as resistance to practical collision and preimage attacks.

The Python implementation demonstrates SHA-256 to make this distinction explicit.

A hash-table implementation should not be described as secure merely because it uses the word "hash."

---

## 5. Collisions

A collision is unavoidable when a large or unlimited key space is mapped into a finite number of table positions.

For example, suppose a table has five positions:

`0, 1, 2, 3, 4`

The keys 10, 15, 20, and 25 all produce index 0 under `key mod 5`.

A hash table therefore requires a collision-resolution strategy.

The two major approaches implemented here are:

1. Separate chaining
2. Open addressing

---

## 6. Separate Chaining

Separate chaining stores multiple entries in a bucket.

Conceptually:

`bucket[0] -> [10, 15, 20, 25]`

If a collision occurs, the new item is added to the bucket associated with that index.

### Advantages

- Collision handling is conceptually straightforward.
- Deletion is relatively simple.
- The table can contain more entries than the number of buckets.
- Very high load factors are possible, although performance eventually degrades.

### Disadvantages

- Additional memory is needed for bucket containers and entries.
- Pointer or container overhead can reduce memory locality.
- Long collision chains can produce linear lookup behavior.

The Python `ChainedHashTable`, JavaScript `ChainedHashTable`, and C++ `ChainedHashTable` all demonstrate this approach.

---

## 7. Open Addressing

Open addressing stores entries directly in the table array.

When the preferred slot is occupied, the implementation searches another slot according to a probing rule.

For example:

`h(key)`

then:

`h(key) + 1`

then:

`h(key) + 2`

and so on, wrapping around the table.

This is called linear probing.

### Advantages

- Entries remain inside one array.
- Memory locality can be excellent.
- There is no separate linked bucket structure.
- Implementations can be memory-efficient.

### Disadvantages

- Performance becomes sensitive to load factor.
- Deletion requires careful handling.
- Probe sequences become longer as the table becomes crowded.
- Resizing and probing logic are more delicate.

---

## 8. Linear Probing

The Python and JavaScript implementations use linear probing.

The general formula is:

`index = (initial_index + attempt) mod capacity`

For attempts 0, 1, 2, and 3:

`h`

`h + 1`

`h + 2`

`h + 3`

with wraparound.

### Primary Clustering

Linear probing can create primary clusters.

A group of occupied adjacent slots can cause later collisions to extend the same group.

This increases probe lengths.

Linear probing is nevertheless attractive because it is simple and often cache-friendly.

---

## 9. Quadratic Probing

Quadratic probing changes the probe distance.

A common demonstration is:

`index = (h + i²) mod capacity`

where `i` is the probe attempt.

The sequence grows approximately quadratically rather than linearly.

This can reduce primary clustering, but correct behavior depends on table size and the exact probing formula.

The Python and JavaScript examples demonstrate the mathematical probe sequence without implementing a complete production quadratic-probing table.

---

## 10. Double Hashing

Double hashing uses two hash calculations.

A conceptual formula is:

`index = (h1(key) + i * h2(key)) mod capacity`

The second hash determines the probe step.

This can produce better probe distribution than simple linear probing when the functions and table dimensions are chosen appropriately.

The examples use a prime-based second step for demonstration.

---

## 11. Tombstones and Deletion

Deletion is particularly important in open addressing.

Suppose three keys form a probe sequence:

`A -> B -> C`

If B is simply changed to an empty slot, a later search for C might stop at B and incorrectly conclude that C does not exist.

A tombstone solves this problem.

The states become:

- EMPTY: never occupied
- OCCUPIED: currently contains an entry
- TOMBSTONE: previously contained an entry

A lookup continues through tombstones.

A later insertion can reuse a tombstone.

The Python and JavaScript open-addressing implementations explicitly demonstrate this mechanism.

---

## 12. Load Factor

The load factor is:

`α = n / m`

where:

- `n` is the number of stored entries.
- `m` is the table capacity.

Examples:

`3 / 10 = 0.30`

`5 / 10 = 0.50`

`7 / 10 = 0.70`

`9 / 10 = 0.90`

The practical threshold depends on the collision strategy.

Open addressing generally requires a lower maximum load factor than chaining because the table itself must provide unused positions for probing.

The implementations use thresholds around 0.70 to 0.75 as practical demonstrations.

These values are not universal requirements.

---

## 13. Resizing

When a table becomes too full, it can be resized.

A typical process is:

1. Allocate a larger table.
2. Iterate through the old entries.
3. Recalculate their positions using the new capacity.
4. Insert them into the new table.
5. Replace the old table.

Resizing is an O(n) operation because all active entries may need to be processed.

Nevertheless, geometric growth such as doubling capacity produces amortized O(1) insertion under ordinary assumptions.

For example:

`8 -> 16 -> 32 -> 64 -> 128`

rather than increasing the table by only one slot each time.

---

## 14. Python Implementation

The Python script starts with simple mathematical hashing:

`key % table_size`

It then demonstrates a polynomial-style string hash.

The script explains important properties of hash functions and contrasts ordinary hash-table hashing with SHA-256.

### ChainedHashTable

The Python `ChainedHashTable` class implements:

- insertion
- updating an existing key
- lookup
- membership testing
- deletion
- iteration
- load-factor calculation
- resizing

The table represents each bucket as a Python list.

### OpenAddressingHashTable

The Python open-addressing implementation demonstrates:

- direct table storage
- linear probing
- tombstones
- deletion
- lookup after deletion
- automatic resizing
- load-factor control

### Algorithmic Applications

The Python script also demonstrates practical hash-based algorithms.

#### Frequency Counting

A dictionary maps an item to the number of times it has appeared.

For example:

`a -> 3`

`b -> 1`

`n -> 2`

This gives average O(1) updates and lookups.

#### Deduplication

A set can track whether a value has already appeared.

This makes it possible to remove duplicates efficiently while preserving insertion order when explicitly implemented that way.

#### Two-Sum

The two-sum implementation stores previously observed values in a dictionary.

For each current value `x`, it searches for:

`target - x`

This changes the common brute-force O(n²) approach into an average-case O(n) approach using O(n) additional memory.

---

## 15. Python Custom Objects and Hashing

Python dictionary keys must satisfy hashing and equality requirements.

The `CorrectKey` class demonstrates the relationship between `__hash__()` and `__eq__()`.

The essential rule is:

If `a == b` is true, then `hash(a) == hash(b)` must also be true.

The reverse is not required.

Two different objects can have the same hash value because collisions are permitted.

Immutable objects are generally safer as dictionary keys because changing fields that affect equality or hashing after insertion can make a key effectively unreachable.

The `UserKey` example uses a frozen dataclass to demonstrate an immutable compound key.

---

## 16. JavaScript Implementation

JavaScript provides native hash-oriented collections through:

- `Map`
- `Set`

### Map

`Map` stores key-value pairs.

Conceptually:

`key -> value`

The implementation demonstrates:

- insertion with `set`
- lookup with `get`
- membership with `has`
- deletion with `delete`

### Set

`Set` stores unique values.

It is useful for:

- deduplication
- membership tests
- tracking visited items
- maintaining collections of unique identifiers

---

## 17. JavaScript Object Identity

A particularly important JavaScript behavior is object-key identity.

Two objects can contain identical properties but still be different keys.

For example:

`{ id: 1 }`

and

`{ id: 1 }`

are distinct objects.

A `Map` distinguishes them by object identity.

The JavaScript implementation explicitly demonstrates this behavior.

This differs from a custom value-based hashing system in which object contents may define equality.

---

## 18. JavaScript Asynchronous Cache

The JavaScript implementation includes a simulated asynchronous user lookup.

The cache is a `Map`.

The flow is:

1. Check whether the user ID is already cached.
2. Return the cached value if present.
3. Otherwise simulate asynchronous I/O.
4. Create the result.
5. Store it in the map.
6. Return the result.

This demonstrates that hash-based lookup can be embedded inside event-driven and asynchronous application logic.

The hash table itself does not make the operation asynchronous. JavaScript's Promise and event-loop mechanisms provide the asynchronous behavior.

---

## 19. C++ Industry-Style Case Study

The C++ program models a simplified URL-shortening service.

A URL shortener accepts a long URL such as:

`https://example.com/articles/hashing`

and generates a shorter identifier such as:

`G8`

The service must support two important lookup directions:

`short code -> long URL`

and:

`long URL -> short code`

The case study therefore maintains two hash-table indexes.

---

## 20. C++ Architecture

The main components are:

### StringHasher

This demonstrates a compact non-cryptographic FNV-1a-style hash calculation.

It is intentionally not presented as a password hash or cryptographic security mechanism.

### ChainedHashTable

The generic C++ table supports:

- key-value storage
- insertion
- update
- lookup
- membership testing
- deletion
- load-factor calculation
- automatic resizing
- bucket statistics

The implementation uses:

`std::vector<std::vector<Entry>>`

for separate chaining.

### UrlShortener

The service maintains:

`ChainedHashTable<string, string> shortToLong`

and:

`ChainedHashTable<string, string> longToShort`

The first index resolves short codes.

The second index prevents duplicate short codes from being created for the same long URL.

---

## 21. URL Identifier Generation

The case study uses sequential numeric identifiers encoded using Base62.

The alphabet contains:

- digits
- uppercase letters
- lowercase letters

A numeric sequence can therefore be represented more compactly.

This is an application-level identifier strategy, not a cryptographic identifier.

A production service would need to consider:

- distributed ID generation
- persistence
- concurrency
- abuse prevention
- expiration
- authorization
- analytics
- namespace management
- operational availability
- collision policies

The educational program intentionally keeps the storage system in memory.

---

## 22. URL Validation

The case study accepts URLs beginning with:

`http://`

or:

`https://`

Invalid input produces an exception.

This illustrates a general design principle: validation should occur at the system boundary before invalid data enters internal structures.

The validation is intentionally basic. A production URL validation policy may need substantially more rules.

---

## 23. Duplicate URL Handling

If the same long URL is shortened twice, the C++ service returns the existing short code.

This is implemented through the reverse index:

`long URL -> short code`

The approach demonstrates how a hash table can serve not only as a storage structure but also as an indexing mechanism.

---

## 24. Collision Handling in the Case Study

The C++ `ChainedHashTable` uses separate chaining.

If two keys produce the same bucket index, both entries remain accessible through that bucket.

For example:

`10 mod 5 = 0`

`15 mod 5 = 0`

The table does not overwrite one entry with the other.

The bucket becomes a collection of entries.

---

## 25. Complexity

Under ordinary assumptions:

| Operation | Average Case | Worst Case |
|---|---:|---:|
| Hash-table lookup | O(1) | O(n) |
| Hash-table insertion | O(1) | O(n) |
| Hash-table deletion | O(1) | O(n) |
| Resize | O(n) | O(n) |
| Two-sum with hashing | O(n) | O(n²) in pathological hash behavior |
| Frequency counting | O(n) | Potentially higher under severe collisions |

The O(1) figures are average-case expectations.

A hash table is not automatically constant-time in every situation.

---

## 26. Why Worst-Case Lookup Can Become O(n)

Suppose every key is mapped into the same bucket.

With separate chaining, the bucket could contain:

`k1 -> k2 -> k3 -> k4 -> ... -> kn`

Searching for the final item may require checking all n entries.

Thus the operation becomes O(n).

The quality of the hash function and the distribution of keys are therefore important.

---

## 27. Chaining and Open Addressing Comparison

| Property | Separate Chaining | Open Addressing |
|---|---|---|
| Collision storage | Separate bucket | Another table slot |
| Deletion | Usually straightforward | Requires tombstones or reorganization |
| Memory layout | Bucket containers | Single primary array |
| Cache locality | Often lower | Often higher |
| High load factor | More tolerant | More sensitive |
| Implementation complexity | Relatively simple | More delicate |
| Table can exceed capacity | Yes, conceptually | No active entries beyond slots |
| Probe sequences | Not required | Required |

Neither strategy is universally correct for every workload.

The choice depends on memory constraints, expected load factor, deletion behavior, cache locality, implementation requirements, and workload characteristics.

---

## 28. Common Mistakes

### Assuming Hashing Eliminates Collisions

It does not.

Collisions are a fundamental consequence of mapping a large key space to a finite number of locations.

### Assuming Hash Tables Are Always O(1)

Average-case O(1) is the usual model.

Poor distribution and excessive collisions can cause slower behavior.

### Using a Mutable Key

If the state used for equality or hashing changes after insertion, lookup behavior can become incorrect.

### Forgetting to Resize

As a table becomes crowded, collisions or probe lengths increase.

### Mishandling Deletion in Open Addressing

Simply marking a deleted slot as permanently empty can break future searches.

Tombstones or a correct cluster-reorganization strategy are required.

### Using a Cryptographic Hash Everywhere

Cryptographic hashes have different goals and computational characteristics.

A hash table normally needs fast distribution rather than password-security properties.

### Ignoring Input Attacks

If an attacker can deliberately influence keys, pathological collision behavior can become a denial-of-service concern.

---

## 29. Performance Considerations

Hash-table performance depends on more than asymptotic complexity.

Important factors include:

- hash-function cost
- collision frequency
- load factor
- memory allocation
- cache locality
- key size
- value size
- table capacity
- resizing frequency
- runtime implementation
- CPU architecture

Open addressing can have excellent locality because entries occupy a contiguous array.

Chaining can be easier to manage under deletion and variable bucket populations.

The best choice depends on the workload.

---

## 30. Memory Considerations

Separate chaining usually requires additional memory for bucket containers and their entries.

Open addressing can store entries directly in the table array, potentially reducing structural overhead.

Open addressing also needs unused slots to maintain efficient probe sequences.

Therefore, a lower load factor can require more allocated memory while improving lookup performance.

Memory efficiency and lookup performance must be considered together.

---

## 31. Resizing Trade-Offs

A larger table reduces the probability of collisions but consumes more memory.

A smaller table uses less memory but can increase collision frequency.

Common resizing strategies use geometric growth.

For example:

`16 -> 32 -> 64 -> 128`

This avoids performing a full resize for every additional element.

A resize is expensive individually, but geometric growth allows insertion to remain amortized O(1) under typical assumptions.

---

## 32. Security Considerations

Hashing has several security implications.

### Password Storage

Passwords should not be stored as plaintext.

A normal fast hash such as SHA-256 should not be treated as a password-storage algorithm.

Password storage should use an appropriate salted, deliberately slow password KDF.

### Hash-Table Collision Attacks

If an attacker can construct many keys that collide, a hash table may experience excessive lookup and insertion work.

Systems exposed to untrusted input should use mature implementations and appropriate defensive mechanisms.

### Cryptographic Hashing

Cryptographic hash functions are designed for security-sensitive applications such as integrity verification and digital fingerprinting.

They should not be confused with ordinary hash-table indexing functions.

---

## 33. Advanced Hashing Concepts

### Universal Hashing

Universal hashing uses a family of hash functions and selects functions in a way intended to reduce predictable collision patterns.

It is useful in theoretical and adversarial settings.

### Perfect Hashing

Perfect hashing can provide collision-free lookup for a known static set of keys.

It is particularly useful when the key set does not change frequently.

### Consistent Hashing

Consistent hashing is commonly associated with distributed systems.

Instead of mapping all keys directly to a fixed local array, keys can be mapped to a logical hash space and then assigned to nodes.

When nodes join or leave, consistent hashing can reduce the number of keys that must move.

### Bloom Filters

A Bloom filter uses multiple hash functions and compact bit storage to answer membership questions probabilistically.

A Bloom filter can produce false positives but, in its standard form, does not produce false negatives for correctly managed inserted items.

It is useful when memory efficiency is more important than exact membership representation.

---

## 34. Python, JavaScript, and C++ Roles

### Python

Python is effective for studying hashing because dictionaries and sets are built into the language and custom classes can be implemented concisely.

The Python implementation focuses on:

- fundamentals
- custom hash-table mechanics
- algorithmic applications
- testing
- custom keys
- complexity
- security concepts

### JavaScript

JavaScript provides a useful application-oriented perspective.

The implementation demonstrates:

- custom hash tables
- `Map`
- `Set`
- object identity
- asynchronous cache usage
- application-level lookup
- JavaScript runtime behavior

### C++

C++ is useful for examining lower-level implementation decisions.

The case study demonstrates:

- generic data structures
- explicit memory-oriented design
- templates
- exception handling
- resizing
- type-safe interfaces
- system-style architecture
- an application built around hash-table indexes

---

## 35. Native Hash Tables in Real Programming

Most production applications should normally use well-tested standard-library or runtime hash-table implementations rather than writing a custom table without a specific reason.

Examples include:

Python:

`dict` and `set`

JavaScript:

`Map` and `Set`

C++:

`std::unordered_map` and `std::unordered_set`

Custom implementations are valuable when learning algorithms, controlling specialized behavior, studying performance, or implementing systems where particular storage and collision strategies are required.

---

## 36. Real-World Applications

Hashing appears in many systems.

### Databases and Indexing

Hash-based indexes can provide efficient equality lookups.

### Caches

A key can identify a cached result:

`request -> response`

### Compilers

Symbol tables can map names to information about variables, functions, and types.

### Networking

Hashing can support lookup tables, routing structures, connection tracking, and distributed allocation schemes.

### Deduplication

A hash can provide a compact fingerprint for identifying previously observed content.

### Data Processing

Frequency counting and grouping are common hash-based operations.

### Security

Cryptographic hashes support integrity checking and other security mechanisms.

### Distributed Systems

Consistent hashing can help distribute keys across nodes.

---

## 37. Important Distinctions

### Hash Value vs Table Index

A hash function can produce a large integer.

The table index is usually derived from that value:

`index = hash(key) mod capacity`

These are conceptually different quantities.

### Collision vs Duplicate Key

A duplicate key means the same logical key is inserted again.

A collision means different keys map to the same table location.

Two different keys can collide.

### Hashing vs Sorting

Hash-table lookup is typically average O(1).

Sorted-array lookup through binary search is O(log n).

Hash tables generally provide faster average equality lookup but do not naturally provide sorted order.

### Hashing vs Encryption

Hashing normally produces a digest or index value.

Encryption is designed for reversible transformation using cryptographic keys.

### General Hash vs Cryptographic Hash

A general-purpose hash prioritizes speed and distribution.

A cryptographic hash additionally targets security properties.

---

## 38. Edge Cases Demonstrated

The implementations account for or discuss:

- empty strings
- zero values
- negative integers
- large integer keys
- duplicate keys
- missing keys
- deletion
- collisions
- tombstones
- high load factors
- resizing
- invalid capacities
- invalid URLs
- repeated URL shortening
- object identity
- missing lookups
- extreme collision patterns

Correct hash-table implementations must treat these cases deliberately.

---

## 39. Testing Strategy

The three implementations include executable checks.

The Python tests verify:

- insertion
- updating
- lookup
- deletion
- collision handling
- open-addressing lookup after deletion
- two-sum
- deduplication
- frequency counting

The JavaScript tests verify:

- chained insertion
- updates
- deletion
- open-addressing collisions
- tombstone behavior
- two-sum
- deduplication

The C++ tests verify:

- generic table insertion
- lookup
- update
- membership
- deletion
- missing-key behavior
- URL deduplication
- URL resolution
- URL deletion

Testing collision cases is particularly important because collision logic is where many hash-table implementation errors occur.

---

## 40. Production Implementation Considerations

A production hash-table-based service should consider:

- persistence
- concurrency
- thread safety
- process boundaries
- memory limits
- monitoring
- logging
- input validation
- abuse prevention
- capacity planning
- serialization
- data durability
- failure recovery
- security
- performance measurement

The C++ URL-shortener case study intentionally models only the in-memory indexing layer.

A real URL-shortening service would require additional components for storage, networking, authentication, operations, and reliability.

---

## 41. Core Formulas

Hash-table indexing:

`index = hash(key) mod capacity`

Load factor:

`α = n / m`

Linear probing:

`index = (h(key) + i) mod m`

Quadratic probing:

`index = (h(key) + i²) mod m`

Double hashing:

`index = (h1(key) + i × h2(key)) mod m`

These formulas describe the central mathematical mechanisms demonstrated by the implementations.

---

## 42. Key Implementation Lessons

A functional hash table requires more than a hash function.

The complete design must account for:

1. Key hashing.
2. Index calculation.
3. Collision resolution.
4. Key equality.
5. Insertion.
6. Lookup.
7. Deletion.
8. Load-factor monitoring.
9. Resizing.
10. Rehashing.
11. Edge cases.
12. Performance.
13. Security considerations.

The interaction between these mechanisms determines the practical behavior of the data structure.
