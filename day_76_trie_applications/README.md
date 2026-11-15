# Trie Applications: Autocomplete, Prefix Searching, Dictionary Problems and Word Search

## 1. Project Overview

A Trie, also called a prefix tree, is a tree-based data structure that stores strings by sharing their common prefixes.

Unlike a conventional dictionary implemented using a hash table, a Trie exposes the internal structure of words. Each edge represents a character, and each path from the root represents a prefix. A node marked as terminal represents a complete dictionary word.

For example, the words `app`, `apple`, `apply`, and `application` share the prefix `app`.

A Trie stores their shared characters once rather than maintaining four independent character sequences.

This project implements practical Trie applications across Python, JavaScript, C++17, Java 17, and PostgreSQL.

## 2. Core Trie Structure

The logical structure is:

    Root
     |
     a
     |
     p
     |
     p [terminal]
     |
     +---- l
           |
           e [terminal]
           |
           i
           |
           c
           |
           a
           |
           t
           |
           i
           |
           o
           |
           n [terminal]

The terminal marker is important.

The path `app` represents a valid word, but it is also a prefix of `apple`, `apply`, and `application`.

A Trie must distinguish between a node that merely represents a prefix and a node that represents a complete word.

### 2.1 Trie node components

| Component | Purpose |
|---|---|
| Children | Stores outgoing character edges |
| Terminal marker | Identifies a complete dictionary word |
| Frequency | Tracks word popularity |
| Root | Starting point of every word |
| Depth | Represents the number of characters from the root |

The implementations use lowercase English letters to provide consistent validation and indexing.

This restriction keeps the examples focused on Trie algorithms. Production systems supporting multilingual text require Unicode normalization, appropriate character segmentation, and a defined case-folding policy.

## 3. Fundamental Operations

### 3.1 Insertion

Insertion processes a word character by character.

For each character:

- Check whether the corresponding child exists.
- Create the child if it does not exist.
- Move to the child.
- Continue until the word is exhausted.
- Mark the final node as terminal.

Example:

- Insert `apple`.
- Insert `application`.
- Insert `apply`.

The prefix `appl` is shared by all three words.

Insertion takes \(O(L)\) time, where \(L\) is the word length.

Frequency-based insertion also supports repeated observations of an existing word without creating duplicate dictionary entries.

### 3.2 Exact searching

Exact searching follows the character sequence from the root.

Two conditions must hold:

1. Every character must have a corresponding child.
2. The final node must be terminal.

For example:

| Query | Result |
|---|---|
| `apple` | Found |
| `appl` | Not found |
| `app` | Found |
| `application` | Found |

A valid prefix is not necessarily a valid dictionary word.

Time complexity: \(O(L)\).

### 3.3 Prefix searching

Prefix searching determines whether a path exists for the requested character sequence.

It does not require the final node to be terminal.

For example, the prefix `app` exists if the dictionary contains `apple`, even if `app` itself is not a complete dictionary entry.

Time complexity: \(O(P)\), where \(P\) is the prefix length.

### 3.4 Deletion

Deletion must preserve shared prefixes.

Suppose the dictionary contains:

- `app`
- `apple`
- `application`

Deleting `app` must not remove the shared nodes required by the other words.

The deletion algorithm:

1. Locates the complete word.
2. Checks whether its terminal marker exists.
3. Removes the terminal marker.
4. Moves backward through the path.
5. Removes nodes that are neither terminal nor connected to children.

This operation is known as path pruning.

Time complexity: \(O(L)\).

## 4. Autocomplete

Autocomplete retrieves dictionary entries beginning with a supplied prefix.

For example, the prefix `app` can produce:

- `apple`
- `application`
- `apply`

The implementation supports frequency-based ranking.

An application can maintain frequencies using:

- Search activity
- Selection counts
- User interactions
- Popularity measurements

The ranking rule is:

1. Higher frequency first.
2. Alphabetical order when frequencies are equal.

Example:

| Word | Frequency |
|---|---:|
| apple | 20 |
| application | 15 |
| apply | 12 |
| app | 8 |

The prefix search first locates the prefix node. A traversal then collects terminal descendants.

The result is sorted by frequency and limited to the requested number of suggestions.

If \(K\) words are found below a prefix, collecting them takes time proportional to the visited subtree. Sorting the results takes \(O(K \log K)\).

The Python and JavaScript versions use explicit traversal stacks for autocomplete. The C++ and Java versions use recursive traversal.

For very large dictionaries, sorting every matching word can be expensive. A production autocomplete service can maintain bounded top-K candidates or use a priority queue.

## 5. Longest Prefix Matching

Longest prefix matching finds the longest dictionary word that is also a prefix of an input string.

Consider a dictionary containing:

- `a`
- `app`
- `apple`
- `application`

For the input `application`, the longest dictionary word that is also a prefix is `app`, because the example implementations use the configured dictionary and return the last terminal node encountered during traversal.

The algorithm:

1. Start at the root.
2. Follow the input characters.
3. Record every terminal node encountered.
4. Return the longest recorded word.

Time complexity: \(O(L)\).

This operation is useful in:

- URL routing
- Command interpretation
- Network prefix matching
- Lexical analysis
- Search indexing

## 6. Wildcard Dictionary Searching

Wildcard searching supports patterns that represent multiple possible strings.

The project defines two wildcard symbols:

| Symbol | Meaning |
|---|---|
| `.` | Exactly one alphabetic character |
| `*` | Zero or more alphabetic characters |

Examples:

| Pattern | Interpretation |
|---|---|
| `app..` | Five-character words beginning with `app` |
| `ba.` | Three-character words beginning with `ba` |
| `a*` | Words beginning with `a` |
| `*dog` | Words ending with `dog` |

The search uses recursive depth-first traversal.

For `.` the algorithm explores every child and advances the pattern position.

For `*` it considers two alternatives:

- Match zero characters and advance the pattern.
- Consume a character and remain at the same pattern position.

Memoization of visited node-position states prevents repeated exploration of equivalent search states.

Wildcard matching can have substantially higher complexity than exact searching because a pattern can branch into many possible paths.

Production systems should limit pattern length, result count, execution time, and available wildcard operations.

## 7. Word Break Problem

Word Break determines whether an input string can be divided into valid dictionary words.

Example:

    Input: catsanddog

    Dictionary:
    cat
    cats
    and
    sand
    dog

Valid segmentation:

    cat + sand + dog

Another valid segmentation:

    cats + and + dog

The project uses dynamic programming combined with Trie traversal.

### 7.1 Dynamic programming state

Let:

\[
dp[i] =
\begin{cases}
true & \text{if the first } i \text{ characters can be segmented}\\
false & \text{otherwise}
\end{cases}
\]

Initialization:

\[
dp[0] = true
\]

For every reachable starting position, the algorithm traverses the Trie using subsequent characters.

Whenever it reaches a terminal node, the corresponding ending position becomes reachable.

The final answer is:

\[
dp[n]
\]

where \(n\) is the length of the input.

The implementation avoids repeatedly constructing every possible substring and searching for it independently.

The complexity depends on the input length and the number of Trie transitions explored.

### 7.2 Generating all valid segmentations

The implementations also provide sentence generation.

A memoization map stores previously computed suffix results.

This prevents repeated computation of the same suffix.

The output limit controls memory consumption and execution time.

The number of valid segmentations can grow exponentially. A result limit is therefore an important operational safeguard.

## 8. Word Search II

Word Search II finds multiple dictionary words inside a two-dimensional character grid.

Example:

    o a a n
    e t a e
    i h k r
    i f l v

Dictionary:

- oath
- pea
- eat
- rain

Expected results:

- eat
- oath

### 8.1 Movement rules

The algorithm permits:

- Moving upward
- Moving downward
- Moving left
- Moving right

Diagonal movement is not allowed.

A grid cell cannot be reused within the same word.

### 8.2 Trie-guided depth-first search

A conventional approach independently searches the grid for each dictionary word.

This repeats substantial work when words share prefixes.

Trie-guided DFS improves this process.

The algorithm:

1. Inserts every dictionary word into a Trie.
2. Starts DFS from each grid cell.
3. Follows the corresponding Trie edge.
4. Stops when no matching Trie edge exists.
5. Records a word when a terminal node is reached.
6. Temporarily marks the visited grid cell.
7. Explores neighboring cells.
8. Restores the original cell after returning.

The Trie allows unsuccessful search paths to terminate early.

After finding a word, its terminal marker is removed from the search structure to prevent duplicate discoveries.

This optimization does not remove the shared prefix nodes required by other words.

The grid is restored after every DFS operation.

### 8.3 Complexity

Let:

- \(R\) represent the number of rows.
- \(C\) represent the number of columns.
- \(L\) represent the maximum dictionary word length.
- \(D\) represent the dictionary size.

Trie construction requires time proportional to the total number of dictionary characters.

The DFS worst case can grow exponentially with the maximum word length because each cell can have up to four directional choices.

Trie pruning substantially reduces unnecessary exploration when dictionary words share prefixes.

## 9. Python Implementation

The Python implementation provides a reusable Trie class with dataclass-based nodes.

### Implemented components

| Component | Responsibility |
|---|---|
| `TrieNode` | Stores children, terminal state, and frequency |
| `Trie` | Implements dictionary operations |
| `WordDictionary` | Provides wildcard dictionary queries |
| `word_break` | Evaluates string segmentation |
| `word_break_sentences` | Generates valid segmentations |
| `word_search_ii` | Finds dictionary words in a grid |
| `load_dictionary` | Imports newline-separated words |
| `save_dictionary` | Exports words and frequencies |
| `TrieTests` | Validates core behavior |

The implementation uses:

- Dictionaries for child references
- Lists for traversal and dynamic programming
- Sets for duplicate elimination
- Dataclasses for node modeling
- Exceptions for invalid input
- JSON for dictionary persistence
- Logging for invalid dictionary records
- Unit testing for verification

### Execution

Save the source as `trie_applications.py`.

Run:

`python trie_applications.py`

The script executes the demonstrations and unit tests.

## 10. JavaScript Implementation

The JavaScript implementation emphasizes event-driven and asynchronous search services.

### Main components

| Component | Responsibility |
|---|---|
| `TrieNode` | Stores child nodes and terminal information |
| `Trie` | Manages dictionary state |
| `WordBreakService` | Performs dynamic programming |
| `AutocompleteService` | Provides asynchronous autocomplete |
| `EventEmitter` | Publishes search results and errors |
| `wordSearchII` | Implements grid searching |
| `loadDictionary` | Loads a dictionary from a file |
| `saveDictionary` | Persists dictionary data |

### Event-driven autocomplete

The autocomplete service emits a `results` event when a search completes.

Consumers can subscribe to this event without coupling their application logic to the internal Trie implementation.

The service also emits `searchError` events for unsuccessful requests.

The asynchronous interface uses Node.js event-loop scheduling.

The implementation does not provide request cancellation or network-level debouncing. These would be additional service-layer responsibilities in a production application.

### Persistence

Dictionary data is serialized into JSON.

The saved representation contains complete words and their frequencies rather than internal Trie node references.

This makes persistence independent of the in-memory node structure.

### Execution

Save the source as `trie_applications.js`.

Run:

`node trie_applications.js`

The application uses Node.js built-in modules and requires no third-party npm packages.

## 11. C++17 Implementation

The C++ implementation emphasizes memory ownership, efficient node access, and algorithmic control.

### Design decisions

| Component | Design |
|---|---|
| Trie node | Struct containing a fixed child array |
| Child ownership | `std::unique_ptr` |
| Word lookup | Direct indexed child access |
| Word collection | DFS |
| Search results | STL vectors |
| Duplicate elimination | `std::unordered_set` |
| Word Break | `std::vector<bool>` |
| Word Search | Recursive DFS |
| Validation | Standard exceptions |

### Fixed-array representation

The C++ implementation uses an array of 26 child pointers.

For lowercase English text, each character maps to an integer:

\[
index = character - 'a'
\]

This provides constant-time child access.

The design uses more predictable per-node storage than a hash-map representation, at the cost of reserving space for all 26 possible children.

### Memory management

`std::unique_ptr` provides exclusive ownership of child nodes.

When a word is deleted, unnecessary nodes are automatically released through recursive pruning.

Copying is disabled to prevent accidental duplication of the Trie ownership structure.

### Execution

Save the source as `trie_applications.cpp`.

Compile:

`g++ -std=c++17 -O2 -Wall -Wextra -pedantic trie_applications.cpp -o trie_applications`

Run:

`./trie_applications`

On Windows:

`trie_applications.exe`

No external libraries are required.

## 12. Java 17 Implementation

The Java implementation uses domain-oriented service classes and immutable search results.

### Domain model

| Component | Responsibility |
|---|---|
| `TrieNode` | Represents an individual Trie node |
| `TrieDictionary` | Manages dictionary operations |
| `Suggestion` | Immutable autocomplete result |
| `SearchResult` | Search response with status |
| `SearchStatus` | Represents the search outcome |
| `WordBreakService` | Handles segmentation |
| `WordSearchService` | Handles grid searching |
| `AutocompleteService` | Provides synchronous and asynchronous lookup |
| `DictionaryException` | Represents dictionary failures |
| `ValidationException` | Represents invalid requests |

### Enterprise-oriented design

The dictionary is separated from the application services.

The autocomplete service returns a structured result rather than exposing internal nodes.

The result record contains:

- Requested prefix
- Immutable suggestion list
- Search status

This provides a clear boundary between internal data structures and application consumers.

### Concurrency considerations

Dictionary insertion and deletion are synchronized.

This provides basic protection for structural mutations, but does not make the entire dictionary implementation a fully concurrent data structure.

A high-throughput service would require a more comprehensive concurrency strategy, such as immutable snapshots, read-write locking, or concurrent Trie structures.

### Execution

Save the source as `TrieApplications.java`.

Compile:

`javac TrieApplications.java`

Run:

`java -ea TrieApplications`

The `-ea` option enables Java assertions.

Java 17 is required.

## 13. PostgreSQL Implementation

The PostgreSQL implementation provides a persistent relational representation of Trie data.

It separates dictionary metadata, Trie nodes, complete dictionary entries, search requests, and audit history.

### 13.1 Database relationships

    Dictionary
       |
       +---- Trie Nodes
       |       |
       |       +---- Parent Node
       |       |
       |       +---- Child Node
       |
       +---- Dictionary Entries
       |       |
       |       +---- Complete Word
       |       |
       |       +---- Terminal Node
       |       |
       |       +---- Frequency
       |
       +---- Search Requests
       |
       +---- Dictionary Audit

### 13.2 Main tables

| Table | Purpose |
|---|---|
| `dictionary` | Stores dictionary metadata |
| `trie_node` | Stores parent-child character relationships |
| `dictionary_entry` | Stores complete words and frequencies |
| `search_request` | Records search activity |
| `dictionary_audit` | Records dictionary modifications |

### 13.3 Trie node representation

Each Trie node contains:

- Unique node identifier
- Dictionary identifier
- Parent node identifier
- Character represented by the edge
- Node depth

The root node has no parent and no edge character.

Each non-root node has a parent and one alphabetic character.

The unique constraint on dictionary, parent, and edge character prevents duplicate child edges.

### 13.4 Dictionary entry representation

The dictionary entry table stores complete words independently of their individual character nodes.

Each entry references the terminal node representing its final character.

The unique constraint on dictionary and word prevents duplicate dictionary entries.

Repeated insertion increases the frequency instead of creating a duplicate entry.

### 13.5 Transactional insertion

The `insert_word` function:

1. Validates the word.
2. Validates its frequency.
3. Locks the relevant dictionary record.
4. Locates the root.
5. Creates missing Trie nodes.
6. Reuses existing edges.
7. Locates the terminal node.
8. Inserts or updates the dictionary entry.

The transaction ensures that partial insertions do not leave an incomplete dictionary entry.

The dictionary-level lock serializes modifications to one dictionary. This simplifies correctness but can restrict write throughput when many sessions modify the same dictionary.

### 13.6 Prefix searching

The `prefix_search` function retrieves all active words beginning with the requested prefix.

The database also includes a B-tree index using `text_pattern_ops` to support prefix-oriented text queries.

The implementation uses a separate complete-word table for efficient retrieval and frequency ranking.

The normalized relational representation preserves the Trie hierarchy, while the entry table provides a practical search-oriented access path.

### 13.7 Search analytics

Search requests record:

- Dictionary
- Search type
- Search text
- Result count
- Execution time
- Request timestamp

The reporting views aggregate dictionary statistics and search activity.

These records can support analysis of popular prefixes, dictionary utilization, and search performance.

### 13.8 Audit controls

A database trigger records dictionary-entry insertion, modification, and deletion.

The audit table maintains historical frequency information.

Dictionary deletion uses soft deletion. The corresponding Trie path remains available for other words that share its prefixes.

Physical Trie-node pruning is deferred because shared nodes must not be removed while other active words depend on them.

### 13.9 Execution

Save the SQL source as `trie_applications.sql`.

Execute it using:

`psql -U postgres -d your_database -f trie_applications.sql`

The script creates its own schema, sample dictionaries, Trie nodes, functions, procedures, triggers, views, indexes, and test records.

## 14. Cross-Language Implementation Comparison

| Capability | Python | JavaScript | C++17 | Java 17 | PostgreSQL |
|---|---|---|---|---|---|
| Trie insertion | Yes | Yes | Yes | Yes | Yes |
| Exact search | Yes | Yes | Yes | Yes | Yes |
| Prefix search | Yes | Yes | Yes | Yes | Yes |
| Deletion | Yes | Yes | Yes | Yes | Soft deletion |
| Frequency ranking | Yes | Yes | Yes | Yes | Yes |
| Wildcard search | Yes | Yes | Yes | Yes | Yes |
| Word Break | Yes | Yes | Yes | Yes | Yes |
| Sentence generation | Yes | Yes | Yes | Yes | Not implemented |
| Word Search II | Yes | Yes | Yes | Yes | Not implemented |
| Persistence | JSON | JSON | In-memory | In-memory | Relational |
| Asynchronous interface | No | Yes | No | Yes | Database transactions |

The implementations share the same underlying Trie concepts but use different engineering approaches.

Python emphasizes concise data modeling and testing.

JavaScript demonstrates event-driven application integration.

C++ emphasizes memory ownership and direct indexed access.

Java emphasizes domain separation and structured service responses.

PostgreSQL emphasizes persistent storage, referential integrity, transactional updates, and reporting.

## 15. Complexity Analysis

Let:

- \(L\) = length of the input word.
- \(P\) = length of a prefix.
- \(N\) = number of Trie nodes.
- \(K\) = number of words matching a prefix.
- \(D\) = total number of characters across dictionary words.
- \(R\) = number of grid rows.
- \(C\) = number of grid columns.

| Operation | Time Complexity |
|---|---|
| Trie insertion | \(O(L)\) |
| Exact search | \(O(L)\) |
| Prefix search | \(O(P)\) |
| Deletion | \(O(L)\) |
| Autocomplete traversal | Proportional to visited subtree |
| Autocomplete sorting | \(O(K \log K)\) |
| Longest prefix matching | \(O(L)\) |
| Trie construction | \(O(D)\) |
| Word Break | \(O(nL)\) upper bound |
| Word Search II | Exponential worst case in maximum word length |

Trie memory consumption is proportional to the number of distinct prefix nodes.

For a fixed lowercase alphabet, a fixed-array implementation reserves 26 child references per node.

A map-based implementation stores only existing child edges, reducing unused child storage at the cost of map overhead.

## 16. Edge Cases and Failure Handling

The implementations explicitly address several important cases.

| Condition | Expected behavior |
|---|---|
| Empty dictionary | Search returns no match |
| Missing prefix | Autocomplete returns an empty result |
| Prefix is not a complete word | Exact search returns false |
| Duplicate insertion | Frequency increases |
| Delete missing word | No dictionary change |
| Delete shared-prefix word | Other words remain available |
| Zero autocomplete limit | Empty result |
| Negative frequency | Validation error |
| Invalid alphabetic input | Validation error |
| Invalid grid dimensions | Grid validation error |
| Repeated grid discoveries | Duplicate results removed |
| Excessive sentence combinations | Result limit applied |
| Missing dictionary file | File-access error |
| Invalid persisted data | Import failure |

A production service should also enforce request-size limits, rate limits, memory limits, authorization, and execution deadlines.

## 17. Security and Operational Considerations

Trie-based applications can process user-controlled input at high frequency.

Important controls include:

- Validate all dictionary entries.
- Restrict accepted character sets.
- Limit word length.
- Limit autocomplete result counts.
- Limit wildcard pattern complexity.
- Bound Word Break sentence generation.
- Bound grid dimensions.
- Avoid untrusted SQL string construction.
- Use parameterized database queries.
- Apply database permissions according to application roles.
- Protect dictionary files from unauthorized modification.
- Monitor search latency and resource consumption.

The PostgreSQL implementation uses database functions and constraints to enforce important integrity rules.

In a deployed application, application roles should receive only the database privileges necessary for their operations. Database functions should also be reviewed for their execution privileges and security context before exposure to untrusted callers.

## 18. Practical Applications

### Search engines

A Trie can efficiently identify words beginning with a user's input and provide immediate suggestions.

### Text editors

Autocomplete can suggest identifiers, commands, and previously used terms.

### Contact directories

Prefix searching can locate names and identifiers without scanning every complete record.

### Dictionary applications

Exact lookup, prefix search, wildcard matching, and word segmentation support lexical search.

### Spell-checking

A dictionary Trie can support prefix-based candidate generation and dictionary membership checks. More advanced spelling correction requires edit-distance calculations or additional ranking algorithms.

### Search query processing

Word Break can identify valid token sequences in concatenated text.

### Grid-based puzzles

Trie-guided DFS efficiently searches for multiple words within a character board.

### Network and routing systems

Longest prefix matching provides a conceptual foundation for routing-table lookup, although production IP routing generally requires bitwise prefix structures rather than alphabetic string Tries.

## 19. Testing Coverage

The source implementations include executable tests for:

- Exact word lookup
- Prefix lookup
- Frequency ranking
- Deletion
- Shared-prefix preservation
- Wildcard matching
- Word Break
- Sentence generation
- Word Search II
- Invalid input
- Search result validation

The PostgreSQL script includes sample records, constraint checks, transactional operations, audit verification, and reporting queries.

Testing should also cover high-volume dictionaries, repeated insertion, concurrent modifications, memory consumption, and pathological wildcard patterns before production deployment.

## 20. Final Technical Distinction

The Trie is the shared data structure, but its applications solve different problems.

| Application | Main objective |
|---|---|
| Exact search | Determine whether a complete word exists |
| Prefix search | Determine whether a character sequence exists as a prefix |
| Autocomplete | Retrieve and rank words below a prefix |
| Longest prefix matching | Find the longest complete word matching the beginning of an input |
| Wildcard search | Match dictionary entries against flexible patterns |
| Word Break | Determine whether a string can be segmented into dictionary words |
| Word Search II | Find multiple dictionary words inside a two-dimensional grid |

These problems share Trie traversal but differ in their state management, search constraints, result generation, and complexity.

The five implementations demonstrate how the same prefix-tree model can support algorithmic problem solving, application services, memory-efficient data structures, enterprise domain models, and persistent relational workflows.
