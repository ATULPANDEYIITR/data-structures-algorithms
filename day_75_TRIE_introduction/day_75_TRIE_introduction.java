/*
 * TRIE INTRODUCTION: JAVA 17 ENTERPRISE PREFIX INDEX
 *
 * Scenario:
 * An enterprise service maintains a searchable catalogue of
 * product identifiers, service names, and operational commands.
 *
 * Features:
 * - Explicit domain types
 * - Character transition maps
 * - Unicode code-point traversal
 * - Exact lookup
 * - Prefix lookup
 * - Autocomplete
 * - Reviewable frequency statistics
 * - Safe deletion
 * - Longest-prefix matching
 * - Immutable result records
 * - Validation exceptions
 * - Service-layer separation
 * - Automated tests
 *
 * Compile:
 * javac TrieEnterprise.java
 *
 * Run:
 * java TrieEnterprise
 */

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.Deque;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.TreeMap;

public class TrieEnterprise {

    enum OperationStatus {
        CREATED,
        FREQUENCY_UPDATED,
        DELETED,
        NOT_FOUND
    }

    record OperationResult(
        OperationStatus status,
        String value,
        int frequency
    ) {}

    record TrieStatistics(
        int distinctWords,
        long totalInsertions,
        int nodes,
        int edges,
        int maximumDepth
    ) {}

    record Suggestion(
        String value,
        int frequency
    ) {}

    static class TrieException extends RuntimeException {
        TrieException(String message) {
            super(message);
        }
    }

    static class InvalidInputException extends TrieException {
        InvalidInputException(String message) {
            super(message);
        }
    }

    static class TrieNode {
        private final Map<Integer, TrieNode> children =
            new TreeMap<>();

        private boolean terminal;
        private int frequency;

        public boolean isTerminal() {
            return terminal;
        }

        public int frequency() {
            return frequency;
        }

        public int childCount() {
            return children.size();
        }
    }

    static final class Trie {
        private final TrieNode root = new TrieNode();

        private final boolean caseSensitive;

        private int distinctWords;
        private long totalInsertions;

        Trie(boolean caseSensitive) {
            this.caseSensitive = caseSensitive;
        }

        private String normalize(String input) {
            if (input == null) {
                throw new InvalidInputException(
                    "Input cannot be null."
                );
            }

            String word = java.text.Normalizer.normalize(
                input.strip(),
                java.text.Normalizer.Form.NFC
            );

            if (word.isEmpty()) {
                throw new InvalidInputException(
                    "Input cannot be empty."
                );
            }

            if (word.codePointCount(0, word.length()) > 256) {
                throw new InvalidInputException(
                    "Input exceeds 256 code points."
                );
            }

            if (word.codePoints().anyMatch(Character::isISOControl)) {
                throw new InvalidInputException(
                    "Control characters are prohibited."
                );
            }

            return caseSensitive
                ? word
                : word.toLowerCase(java.util.Locale.ROOT);
        }

        private int[] codePoints(String word) {
            return word.codePoints().toArray();
        }

        public OperationResult insert(String input) {
            String word = normalize(input);

            TrieNode current = root;

            for (int character : codePoints(word)) {
                current = current.children.computeIfAbsent(
                    character,
                    ignored -> new TrieNode()
                );
            }

            boolean created = !current.terminal;

            current.terminal = true;
            current.frequency++;

            totalInsertions++;

            if (created) {
                distinctWords++;

                return new OperationResult(
                    OperationStatus.CREATED,
                    word,
                    current.frequency
                );
            }

            return new OperationResult(
                OperationStatus.FREQUENCY_UPDATED,
                word,
                current.frequency
            );
        }

        private TrieNode findNode(String input) {
            String word = normalize(input);

            TrieNode current = root;

            for (int character : codePoints(word)) {
                current = current.children.get(character);

                if (current == null) {
                    return null;
                }
            }

            return current;
        }

        public boolean search(String input) {
            TrieNode node = findNode(input);

            return node != null && node.terminal;
        }

        public boolean startsWith(String prefix) {
            return findNode(prefix) != null;
        }

        public int frequency(String input) {
            TrieNode node = findNode(input);

            return node != null && node.terminal
                ? node.frequency
                : 0;
        }

        public List<Suggestion> autocomplete(
            String input,
            int limit
        ) {
            String prefix = normalize(input);

            if (limit < 1 || limit > 1000) {
                throw new InvalidInputException(
                    "Suggestion limit must be between 1 and 1000."
                );
            }

            TrieNode start = findNode(prefix);

            if (start == null) {
                return List.of();
            }

            List<Suggestion> results = new ArrayList<>();

            record SearchState(
                TrieNode node,
                String word
            ) {}

            Deque<SearchState> stack = new ArrayDeque<>();

            stack.push(new SearchState(start, prefix));

            while (!stack.isEmpty() && results.size() < limit) {
                SearchState state = stack.pop();

                if (state.node().terminal) {
                    results.add(
                        new Suggestion(
                            state.word(),
                            state.node().frequency
                        )
                    );
                }

                // Reverse order is required because the stack is LIFO.
                List<Integer> keys = new ArrayList<>(
                    state.node().children.keySet()
                );

                keys.sort(Comparator.reverseOrder());

                for (int character : keys) {
                    stack.push(
                        new SearchState(
                            state.node().children.get(character),
                            state.word() + new String(
                                Character.toChars(character)
                            )
                        )
                    );
                }
            }

            return List.copyOf(results);
        }

        public OperationResult delete(String input) {
            String word = normalize(input);

            if (!search(word)) {
                return new OperationResult(
                    OperationStatus.NOT_FOUND,
                    word,
                    0
                );
            }

            int[] characters = codePoints(word);

            TrieNode[] path = new TrieNode[characters.length + 1];

            path[0] = root;

            TrieNode current = root;

            for (int i = 0; i < characters.length; i++) {
                current = current.children.get(characters[i]);
                path[i + 1] = current;
            }

            current.terminal = false;
            current.frequency = 0;

            distinctWords--;

            // Preserve nodes that are still used by other words.
            for (int i = characters.length; i > 0; i--) {
                TrieNode child = path[i];

                if (!child.terminal && child.children.isEmpty()) {
                    path[i - 1].children.remove(characters[i - 1]);
                } else {
                    break;
                }
            }

            return new OperationResult(
                OperationStatus.DELETED,
                word,
                0
            );
        }

        public String longestPrefix(String input) {
            String text = normalize(input);

            TrieNode current = root;

            StringBuilder candidate = new StringBuilder();
            String longest = "";

            for (int character : codePoints(text)) {
                current = current.children.get(character);

                if (current == null) {
                    break;
                }

                candidate.appendCodePoint(character);

                if (current.terminal) {
                    longest = candidate.toString();
                }
            }

            return longest;
        }

        public TrieStatistics statistics() {
            record NodeDepth(TrieNode node, int depth) {}

            Deque<NodeDepth> queue = new ArrayDeque<>();

            queue.add(new NodeDepth(root, 0));

            int nodes = 0;
            int edges = 0;
            int maximumDepth = 0;

            while (!queue.isEmpty()) {
                NodeDepth entry = queue.remove();

                nodes++;

                maximumDepth = Math.max(
                    maximumDepth,
                    entry.depth()
                );

                for (TrieNode child : entry.node().children.values()) {
                    edges++;

                    queue.add(
                        new NodeDepth(
                            child,
                            entry.depth() + 1
                        )
                    );
                }
            }

            return new TrieStatistics(
                distinctWords,
                totalInsertions,
                nodes,
                edges,
                maximumDepth
            );
        }
    }

    interface DictionaryPolicy {
        boolean isEligible(String identifier);
    }

    static final class ProductIdentifierPolicy
        implements DictionaryPolicy {

        @Override
        public boolean isEligible(String identifier) {
            return identifier != null
                && identifier.matches("[A-Za-z][A-Za-z0-9_-]{1,63}");
        }
    }

    static final class CatalogueService {
        private final Trie trie;
        private final DictionaryPolicy policy;

        CatalogueService(
            Trie trie,
            DictionaryPolicy policy
        ) {
            this.trie = Objects.requireNonNull(trie);
            this.policy = Objects.requireNonNull(policy);
        }

        public OperationResult register(String identifier) {
            if (!policy.isEligible(identifier)) {
                throw new InvalidInputException(
                    "Identifier violates catalogue policy."
                );
            }

            return trie.insert(identifier);
        }

        public List<Suggestion> suggest(String prefix, int limit) {
            return trie.autocomplete(prefix, limit);
        }

        public boolean exists(String identifier) {
            return trie.search(identifier);
        }

        public OperationResult remove(String identifier) {
            return trie.delete(identifier);
        }

        public TrieStatistics report() {
            return trie.statistics();
        }
    }

    private static void runTests() {
        Trie trie = new Trie(false);

        assert trie.insert("car").status()
            == OperationStatus.CREATED;

        assert trie.insert("cart").status()
            == OperationStatus.CREATED;

        assert trie.insert("cat").status()
            == OperationStatus.CREATED;

        assert trie.insert("car").status()
            == OperationStatus.FREQUENCY_UPDATED;

        assert trie.search("car");
        assert !trie.search("ca");

        assert trie.startsWith("ca");
        assert !trie.startsWith("xyz");

        assert trie.frequency("car") == 2;

        assert trie.autocomplete("car", 10)
            .stream()
            .map(Suggestion::value)
            .toList()
            .equals(List.of("car", "cart"));

        assert trie.delete("car").status()
            == OperationStatus.DELETED;

        assert !trie.search("car");
        assert trie.search("cart");

        assert trie.delete("cart").status()
            == OperationStatus.DELETED;

        assert !trie.startsWith("car");
        assert trie.search("cat");

        Trie unicode = new Trie(false);

        unicode.insert("café");

        assert unicode.search("café");

        boolean rejected = false;

        try {
            trie.insert("");
        } catch (InvalidInputException exception) {
            rejected = true;
        }

        assert rejected;

        System.out.println("All Java assertions passed.");
    }

    public static void main(String[] args) {
        try {
            System.out.println(
                "========================================"
            );

            System.out.println(
                "ENTERPRISE PRODUCT CATALOGUE TRIE"
            );

            System.out.println(
                "========================================"
            );

            Trie trie = new Trie(false);

            CatalogueService service = new CatalogueService(
                trie,
                new ProductIdentifierPolicy()
            );

            List<String> identifiers = List.of(
                "Product100",
                "Product101",
                "Product102",
                "Product200",
                "Product210",
                "Product220",
                "Project100",
                "Project110",
                "Process100",
                "Process200"
            );

            System.out.println("\n1. IDENTIFIER REGISTRATION");

            for (String identifier : identifiers) {
                System.out.println(
                    service.register(identifier)
                );
            }

            System.out.println("\n2. EXACT LOOKUP");

            for (String identifier : List.of(
                "Product100",
                "Product",
                "Project110",
                "Unknown100"
            )) {
                System.out.println(
                    identifier + " -> " + service.exists(identifier)
                );
            }

            System.out.println("\n3. PREFIX SUGGESTIONS");

            for (String prefix : List.of(
                "Product",
                "Project",
                "Process"
            )) {
                System.out.println(
                    prefix + " -> " +
                    service.suggest(prefix, 5)
                );
            }

            System.out.println("\n4. DELETION");

            System.out.println(
                service.remove("Product100")
            );

            System.out.println(
                "Product100 exists: " +
                service.exists("Product100")
            );

            System.out.println(
                "Product101 exists: " +
                service.exists("Product101")
            );

            System.out.println("\n5. LONGEST PREFIX");

            System.out.println(
                trie.longestPrefix("Product101Archive")
            );

            System.out.println("\n6. GOVERNANCE VALIDATION");

            try {
                service.register("Invalid Identifier!");
            } catch (InvalidInputException exception) {
                System.out.println(
                    "Rejected: " + exception.getMessage()
                );
            }

            System.out.println("\n7. DICTIONARY STATISTICS");

            System.out.println(service.report());

            System.out.println("\n8. AUTOMATED TESTS");

            runTests();

            System.out.println("\n9. PERFORMANCE CHARACTERISTICS");

            System.out.println("Insertion: O(L) expected");
            System.out.println("Search: O(L) expected");
            System.out.println("Prefix lookup: O(P) expected");
            System.out.println("Autocomplete: O(P + V + K log K)");
            System.out.println("Deletion: O(L)");
            System.out.println("Memory: O(N) trie nodes");

            System.out.println("\nExecution completed.");

        } catch (TrieException exception) {
            System.err.println(
                "Application failure: " + exception.getMessage()
            );

            System.exit(1);
        }
    }
}
