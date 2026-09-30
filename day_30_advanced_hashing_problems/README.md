# Advanced Hashing Problems

This repository presents advanced hashing techniques through three deliberately different implementations.

The central idea is that hashing can convert repeated searches into constant-time expected lookups. The resulting techniques are especially powerful when a problem asks for relationships between values, frequencies, prefixes, or previously observed states.

The implementations focus on five closely related problem families:

- Prefix-sum hashing for contiguous ranges
- Longest-subarray detection
- Frequency-based analysis
- Canonical grouping
- Pair-sum matching

The Python program provides a broad algorithmic toolkit. The JavaScript program emphasizes `Map`, `Set`, canonical keys, and event-driven state. The C++ program applies the techniques to a transaction-monitoring case study.

## Hashing as a Problem-Solving Technique

A hash table maps a key to stored information so that the program can usually determine whether that key has already appeared without scanning the complete collection.

Python commonly provides this through `dict` and `set`. JavaScript provides `Map` and `Set`. C++ provides containers such as `std::unordered_map` and `std::unordered_set`.

The important design decision is not simply choosing a hash table. The key must encode the relationship the algorithm needs.

For pair sums, the useful key is the value already observed.

For frequency analysis, the key is the value being counted.

For prefix-sum problems, the key is a previously observed prefix state.

For grouping problems, the key is a canonical representation that makes equivalent objects identical from the algorithm's perspective.

This distinction is what separates useful hashing from simply storing data in a dictionary.

## Pair-Sum Hashing

A pair-sum problem asks whether two values satisfy a relationship such as:

`a + b = target`

Rearranging the equation gives:

`b = target - a`

When processing the current value `a`, the algorithm therefore needs to know whether `target - a` appeared earlier.

The Python `two_sum_indices` function stores a value and its index. The JavaScript `twoSum` function uses a `Map` for the same conceptual operation. The C++ case study applies the pattern to transaction amounts.

The important ordering rule is that the complement should be checked before the current value is inserted. This prevents a single element from being used twice when the input contains only one occurrence.

For `[4]` with target `8`, the value `4` must not match itself.

### Counting pairs is different from finding a pair

Finding one pair needs only one previously observed index.

Counting all index-pairs requires frequencies. If a complement has already occurred five times, the current value creates five new valid pairs.

For example, with values `[100, 100, 100]` and target `200`, the answer is three because the three possible index pairs are distinct.

The Python and C++ implementations demonstrate this frequency-based interpretation.

## Prefix-Sum Hashing

Prefix sums are one of the most important advanced uses of hashing.

For an array:

`[a, b, c, d]`

the prefix values can be represented as:

`0`

`a`

`a + b`

`a + b + c`

`a + b + c + d`

Suppose two prefix sums are `P[i]` and `P[j]`, with `j > i`.

The sum between them is:

`P[j] - P[i]`

Therefore, to find a subarray with target sum `T`, a current prefix `P` needs an earlier prefix equal to:

`P - T`

A hash table makes that earlier-prefix lookup expected O(1).

This transforms many apparently quadratic subarray problems into expected O(n) algorithms.

## Why Prefix Hashing Handles Negative Values

A sliding-window approach often depends on properties such as non-negative values. If all values are non-negative, expanding a window increases its sum and shrinking it decreases the sum.

Negative values destroy that monotonic behavior.

For example:

`[3, -7, 5, 4]`

can increase and decrease unpredictably as the window changes.

Prefix sums do not require monotonicity. They depend only on the algebraic relationship between two prefix states.

This is why the C++ case study deliberately contains negative transaction amounts.

## Detecting a Target-Sum Subarray

The detection problem only needs to know whether the required prefix has appeared.

The Python `has_subarray_sum` function therefore maintains a set.

The JavaScript implementation uses a `Set`.

The algorithm begins with prefix sum `0`. This is important because a valid subarray may begin at index zero.

For example, with `[5, -2, -3]` and target `5`, the initial prefix state allows the first element to form a valid range.

Forgetting the initial zero prefix is a common correctness error.

## Counting Target-Sum Subarrays

Detection and counting require different information.

A set answers:

"Has this prefix occurred?"

Counting requires:

"How many times has this prefix occurred?"

If the current prefix is `P`, every earlier occurrence of `P - T` creates one target-sum subarray ending at the current position.

The Python `count_subarrays_with_sum`, JavaScript `countSubarraysWithSum`, and C++ `countTargetWindows` functions implement this frequency-based prefix technique.

The frequency initialization with `{0: 1}` represents the empty prefix and is essential for ranges beginning at the first element.

## Longest Subarray with a Target Sum

The longest-range version has a subtle requirement.

When a prefix sum is first observed, its earliest index should be retained.

Suppose the same prefix sum occurs at positions `2` and `7`, and a later prefix needs that value. Using index `2` creates a longer subarray than using index `7`.

Therefore the Python and JavaScript implementations insert a prefix index only when the prefix has not previously been recorded.

The C++ implementation follows the same rule with `unordered_map`.

The returned range includes the start and end positions, making the result directly useful rather than returning only a length.

## Zero-Sum Subarrays

A zero-sum range satisfies:

`P[j] - P[i] = 0`

which means:

`P[j] = P[i]`

Therefore repeated prefix sums identify zero-sum subarrays.

The same prefix-hashing machinery can solve:

- whether a zero-sum subarray exists
- how many zero-sum subarrays exist
- the longest zero-sum subarray

This is an important example of one mathematical transformation supporting several different problem statements.

## Equal Numbers of Two Categories

Some longest-subarray problems do not explicitly contain a numeric sum.

Consider a binary array where the objective is to find the longest range containing equal numbers of `0` and `1`.

Map:

`0 -> -1`

`1 -> +1`

An equal number of zeroes and ones then produces a transformed sum of zero.

The problem has therefore become a zero-sum prefix problem.

The Python and JavaScript implementations demonstrate this transformation. The same idea can be generalized to two categorical events such as `success` and `failure`.

The transformation is useful because the hash table does not need to understand the original semantic meaning of the categories. It only needs the invariant represented by the transformed balance.

## Modular Prefix Hashing

Another prefix technique uses remainders.

If:

`P[j] % k = P[i] % k`

then:

`P[j] - P[i]`

is divisible by `k`.

Consequently, equal prefix remainders identify subarrays whose sums are divisible by `k`.

The Python implementation uses Python's modulo behavior directly.

The JavaScript implementation explicitly normalizes the remainder because JavaScript's `%` operator preserves the sign of the dividend. Without normalization, negative prefix sums can produce negative remainder keys and make the reasoning less transparent.

The divisor must not be zero.

## Frequency-Based Problems

Frequency hashing separates value identity from occurrence count.

The Python implementation uses both explicit dictionaries and `Counter`. The JavaScript implementation uses `Map`. The C++ implementation maintains an `unordered_map` of transaction categories.

Typical frequency questions include:

- Does a duplicate exist?
- What is the first value occurring once?
- Which values occur most frequently?
- Is there a majority value?
- How many pairs can be formed from duplicate values?
- Which categories exceed a frequency threshold?

The important distinction is that frequency analysis does not necessarily care about contiguity. A frequency table describes the entire observed collection, whereas prefix hashing describes relationships between positions in a sequence.

## Majority Elements

A majority element occurs more than half of the collection size.

The Python and JavaScript programs use explicit frequency maps to make the hashing technique visible.

For an input of length `n`, the threshold is:

`floor(n / 2)`

and the required count is strictly greater than that threshold.

The implementation also handles an empty input by returning no majority.

A different algorithm, such as Boyer-Moore voting, can reduce auxiliary space, but the hash-based version is useful when frequency information is needed for other decisions as well.

## Grouping by Canonical Keys

Grouping problems become hash problems when equivalent objects can be transformed into the same key.

Anagrams are a direct example.

Words such as:

`eat`

`tea`

`ate`

contain identical character frequencies.

The Python implementation creates a fixed 26-position frequency tuple. The JavaScript implementation serializes the same type of frequency vector into a string key.

The canonical key is independent of character order.

This is different from prefix hashing. A prefix key represents a state at a position in a sequence, while an anagram key represents an equivalence class for an entire object.

## Shifted-String Grouping

The JavaScript implementation also groups lowercase strings by their cyclic character-difference pattern.

For a word, each adjacent character contributes a modular difference:

`current - previous mod 26`

Strings that have the same sequence of differences belong to the same shift-equivalence group.

For example, `abc` and `bcd` produce the same difference pattern.

The signature therefore captures structural similarity rather than literal character equality.

This is an example of designing a hash key around the property that defines equivalence.

## C++ Transaction Case Study

The C++ implementation models a transaction-monitoring system.

Each transaction contains:

- an account identifier
- an integer amount
- an activity category

The system provides several independent hash-based analyses.

### Contiguous transaction totals

The engine can find the longest contiguous sequence whose transaction total equals a requested amount.

This uses earliest prefix-sum positions.

Negative transactions are included intentionally. They demonstrate why an algorithm cannot assume that expanding a window always increases its total.

### Counting transaction windows

The engine can count every contiguous range reaching a target total.

The implementation stores prefix frequencies rather than only prefix positions.

Repeated prefix values therefore contribute multiple valid ranges.

### Transaction category frequencies

Category frequencies answer a different question.

The order of transactions is irrelevant when determining how often `purchase`, `refund`, `deposit`, or `login` appears.

The implementation therefore uses a direct frequency map rather than prefix sums.

This distinction keeps the data structure aligned with the problem's invariant.

### Transaction pair matching

The pair-sum engine searches for two transaction amounts whose combined value equals a target.

The current amount is matched against:

`target - current`

Previously observed amounts are stored in an `unordered_map`.

The engine exposes both a single matching pair and the count of all index-pairs.

### Canonical account grouping

Accounts can be grouped by their activity-category multiset.

The implementation collects each account's categories, sorts them, and concatenates them into a canonical signature.

Sorting ensures that the same collection of categories produces the same key regardless of original ordering.

The resulting grouping uses an ordered `std::map` for deterministic output, while the internal account lookup uses `std::unordered_map`.

## Python Implementation

The Python program is designed as a reusable algorithmic toolkit rather than a translation of the C++ case study.

It demonstrates explicit dictionary construction, sets, `Counter`, `defaultdict`, tuple keys, prefix-state retention, modular arithmetic, and a reusable `PrefixHashAnalyzer` class.

The `PrefixHashAnalyzer` stores the original values as an immutable tuple and precomputes prefix sums. Its `longest_for_sum` method retains earliest prefix positions, while `count_for_sum` retains prefix frequencies.

The program also validates binary input and categorical input instead of silently accepting invalid values.

The `group_anagrams` function uses a tuple of character counts as a hashable dictionary key. This avoids sorting each word and demonstrates how a structured immutable value can serve as a canonical hash key.

## JavaScript Implementation

The JavaScript implementation emphasizes the semantics of `Map` and `Set`.

`Map` is used where keys map to indexes, counts, or structured state. `Set` is used where only membership is important.

The implementation also demonstrates a JavaScript-specific issue with modular arithmetic. `normalizedModulo` converts negative remainders into a consistent range, which is important when prefix sums can be negative.

The `EventHashAnalyzer` provides a different perspective from the Python program. It maintains event frequencies while exposing event listeners through a small subscription mechanism.

The listener collection itself is a `Map` from event type to `Set` of callback functions. This gives the example a practical event-driven data-processing structure rather than simply translating Python dictionaries into JavaScript syntax.

Private class fields such as `#events` and `#frequency` keep internal state inaccessible through ordinary property access.

## C++ Implementation

The C++ program emphasizes a system-oriented design.

`TransactionHashEngine` owns the transaction sequence and exposes operations over that data. `Transaction`, `Window`, and `PairMatch` represent meaningful domain results instead of returning loosely structured values.

`std::unordered_map` supplies expected constant-time hash lookup for prefix states, frequencies, and pair matching.

`std::map` is deliberately used for the final canonical grouping because deterministic key ordering is useful for stable output.

The program uses `std::int64_t` for monetary amounts. Narrowing transaction amounts to `int` would create unnecessary range limitations.

The case study also validates an empty transaction collection and catches exceptions at the application boundary.

## Complexity

For an input containing `n` elements, the principal hash-based algorithms have expected linear time.

| Operation | Expected Time | Auxiliary Space | Main Hash State |
| --- | ---: | ---: | --- |
| Duplicate detection | O(n) | O(n) | Seen values |
| Two-sum detection | O(n) | O(n) | Value to index |
| Pair counting | O(n) | O(n) | Value frequencies |
| Target-sum detection | O(n) | O(n) | Prefix set |
| Target-sum counting | O(n) | O(n) | Prefix frequencies |
| Longest target-sum range | O(n) | O(n) | Earliest prefix index |
| Divisibility counting | O(n) | O(n) | Prefix remainders |
| Frequency analysis | O(n) expected | O(n) | Value frequencies |
| Anagram grouping | O(total characters) | O(number of groups) | Frequency signature |
| Sorted canonical grouping | O(n log n) in relevant group sizes | O(n) | Canonical signatures |

These are expected complexities for hash-table operations. They are not unconditional worst-case guarantees.

## Collision and Hash-Table Considerations

Hashing does not mean that every lookup is mathematically guaranteed to be constant time.

Different keys can produce the same hash value. Hash-table implementations resolve such collisions internally, and excessive collisions can degrade performance.

For ordinary algorithmic workloads, Python dictionaries, JavaScript `Map`, and C++ `unordered_map` provide the expected constant-time behavior on which these solutions are based.

Security-sensitive systems should also consider adversarial input. If an attacker can deliberately influence keys and exploit weaknesses in a hash implementation, hash-table performance can become a denial-of-service concern.

The algorithmic pattern remains valid, but production systems should select appropriate containers and platform-supported hashing behavior for their threat model.

## Correctness Traps

### Storing the latest prefix index

For a longest-subarray problem, replacing an earlier prefix index with a later one is incorrect.

The earliest occurrence maximizes the distance to every future matching prefix.

### Using a set when counting

A set can answer whether a prefix exists, but it loses multiplicity.

For counting subarrays, the number of previous occurrences is part of the answer.

### Forgetting the empty prefix

The initial prefix state must represent the sequence before index zero.

Without it, valid ranges beginning at the first element can be missed.

### Assuming positive numbers

Prefix hashing works with negative, zero, and positive values.

Sliding-window reasoning that depends on monotonic sums does not automatically transfer to arbitrary integers.

### Treating value pairs as index pairs

For `[5, 5]` with target `10`, there is one index-pair.

For `[5, 5, 5]`, there are three index-pairs.

A set of distinct values answers a different question from a frequency-based index-pair counter.

### Creating ambiguous grouping keys

A canonical key must preserve the property that defines equivalence.

A poorly designed serialized key can accidentally merge distinct objects. Fixed-size frequency vectors and carefully delimited signatures reduce this risk.

## Validation and Edge Cases

The implementations explicitly handle several boundary conditions.

Empty inputs are considered where an algorithm permits them.

A divisor of zero is rejected for divisibility algorithms.

Binary transformations reject values other than `0` and `1`.

Categorical balancing rejects unexpected categories rather than silently discarding them.

The pair-sum algorithms distinguish between finding one pair and counting all pairs.

Large integer values in C++ use `std::int64_t` to reduce overflow risk compared with a 32-bit integer type.

Even with 64-bit storage, production financial or scientific applications should evaluate the maximum possible cumulative sum before choosing an integer representation.

## Debugging Hash-Based Algorithms

When debugging a prefix-sum algorithm, inspect the state after every element:

`index -> current value -> current prefix -> required prefix -> stored index/count`

This exposes the most common mistakes immediately.

For pair sums, inspect:

`current value -> required complement -> whether complement exists`

For frequency problems, inspect:

`value -> current frequency`

For grouping problems, inspect:

`original object -> canonical key`

The key is the algorithm's abstraction boundary. If two objects that should be equivalent produce different keys, the grouping logic is incorrect. If unrelated objects produce the same key, the canonical representation is insufficient.

## Practical Design Distinctions

Prefix hashing and frequency hashing both use hash tables, but their stored information has different meanings.

A frequency map answers how often a value or category occurs.

A prefix map records historical states of a cumulative transformation.

A pair-sum map records enough previous information to satisfy an algebraic complement.

A grouping map associates a canonical representation with all objects sharing that representation.

The data structure may look similar in source code, but the correctness argument comes from the meaning of the key.

That key design is the central transferable skill demonstrated throughout these implementations.
