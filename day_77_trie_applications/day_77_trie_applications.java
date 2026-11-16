import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.Predicate;
import java.util.stream.Collectors;

/**
 * Advanced Trie Engineering
 *
 * Enterprise components:
 * - Compressed radix trie.
 * - Bitwise trie.
 * - Maximum XOR analytics.
 * - Dictionary service.
 * - Policy-based validation.
 * - Enterprise query and lifecycle management.
 *
 * Java version: 17
 * External dependencies: None
 */
public class AdvancedTrieEnterprise {

    // ========================================================
    // 1. DOMAIN TYPES
    // ========================================================

    enum TrieOperation {
        INSERT,
        SEARCH,
        DELETE,
        PREFIX_SEARCH,
        AUTOCOMPLETE
    }

    enum QueryMode {
        MAXIMUM,
        MINIMUM
    }

    enum RecordStatus {
        ACTIVE,
        ARCHIVED,
        DELETED
    }

    enum MergeState {
        OPEN,
        APPROVED,
        BLOCKED,
        MERGED,
        CLOSED
    }

    record DictionaryRecord(
        String word,
        String category,
        RecordStatus status,
        long version
    ) {
        DictionaryRecord {
            if (word == null || word.isBlank()) {
                throw new IllegalArgumentException(
                    "Word cannot be empty."
                );
            }

            if (category == null || category.isBlank()) {
                throw new IllegalArgumentException(
                    "Category cannot be empty."
                );
            }

            Objects.requireNonNull(status);
        }
    }

    record XorResult(
        long xorValue,
        long matchedValue
    ) {}

    record XorPair(
        long maximumXor,
        long first,
        long second
    ) {}

    record Policy(
        int minimumApprovals,
        boolean requireStatusChecks,
        boolean requireResolvedConversations,
        boolean requireSynchronizedBranch,
        boolean requireLinearHistory,
        boolean allowDraftMerge
    ) {
        Policy {
            if (minimumApprovals < 0) {
                throw new IllegalArgumentException(
                    "Approval count cannot be negative."
                );
            }
        }
    }

    record MergeRequest(
        String id,
        String sourceBranch,
        String targetBranch,
        boolean draft,
        boolean conflict,
        boolean checksPassed,
        boolean conversationsResolved,
        boolean branchSynchronized,
        boolean linearHistory,
        int approvals,
        MergeState state
    ) {
        MergeRequest {
            Objects.requireNonNull(id);
            Objects.requireNonNull(sourceBranch);
            Objects.requireNonNull(targetBranch);
            Objects.requireNonNull(state);

            if (sourceBranch.equals(targetBranch)) {
                throw new IllegalArgumentException(
                    "Source and target branches must differ."
                );
            }

            if (approvals < 0) {
                throw new IllegalArgumentException(
                    "Approval count cannot be negative."
                );
            }
        }
    }

    record Eligibility(
        boolean eligible,
        List<String> blockers
    ) {
        Eligibility {
            blockers = List.copyOf(blockers);
        }
    }

    // ========================================================
    // 2. CUSTOM EXCEPTIONS
    // ========================================================

    static class TrieException extends RuntimeException {
        TrieException(String message) {
            super(message);
        }
    }

    static class PolicyViolationException extends RuntimeException {
        PolicyViolationException(String message) {
            super(message);
        }
    }

    // ========================================================
    // 3. COMPRESSED RADIX TRIE
    // ========================================================

    static final class RadixTrie {

        private static final class Node {
            String edge;
            boolean terminal;
            String value;
            Map<Character, Node> children = new HashMap<>();

            Node(String edge) {
                this.edge = edge;
            }
        }

        private final Node root = new Node("");
        private int size = 0;

        private static int commonPrefix(String a, String b) {
            int i = 0;

            while (
                i < a.length() &&
                i < b.length() &&
                a.charAt(i) == b.charAt(i)
            ) {
                i++;
            }

            return i;
        }

        private void validate(String word) {
            if (word == null || word.isBlank()) {
                throw new TrieException(
                    "Word must contain non-whitespace characters."
                );
            }
        }

        public synchronized boolean insert(
            String word,
            String value
        ) {
            validate(word);

            Node node = root;
            String remaining = word;

            while (!remaining.isEmpty()) {
                char first = remaining.charAt(0);
                Node child = node.children.get(first);

                if (child == null) {
                    Node fresh = new Node(remaining);
                    fresh.terminal = true;
                    fresh.value = value;

                    node.children.put(first, fresh);
                    size++;
                    return true;
                }

                int common = commonPrefix(
                    remaining,
                    child.edge
                );

                if (common == child.edge.length()) {
                    remaining = remaining.substring(common);
                    node = child;

                    if (remaining.isEmpty()) {
                        if (node.terminal) {
                            node.value = value;
                            return false;
                        }

                        node.terminal = true;
                        node.value = value;
                        size++;
                        return true;
                    }

                    continue;
                }

                Node intermediate = new Node(
                    child.edge.substring(0, common)
                );

                child.edge = child.edge.substring(common);

                intermediate.children.put(
                    child.edge.charAt(0),
                    child
                );

                node.children.put(first, intermediate);

                remaining = remaining.substring(common);

                if (remaining.isEmpty()) {
                    intermediate.terminal = true;
                    intermediate.value = value;
                } else {
                    Node fresh = new Node(remaining);
                    fresh.terminal = true;
                    fresh.value = value;

                    intermediate.children.put(
                        remaining.charAt(0),
                        fresh
                    );
                }

                size++;
                return true;
            }

            return false;
        }

        public synchronized boolean search(String word) {
            if (word == null || word.isEmpty()) return false;

            Node node = root;
            String remaining = word;

            while (!remaining.isEmpty()) {
                Node child = node.children.get(remaining.charAt(0));

                if (
                    child == null ||
                    !remaining.startsWith(child.edge)
                ) {
                    return false;
                }

                remaining = remaining.substring(child.edge.length());
                node = child;
            }

            return node.terminal;
        }

        public synchronized boolean startsWith(String prefix) {
            if (prefix == null || prefix.isEmpty()) return false;

            Node node = root;
            String remaining = prefix;

            while (!remaining.isEmpty()) {
                Node child = node.children.get(remaining.charAt(0));

                if (child == null) return false;

                int common = commonPrefix(
                    remaining,
                    child.edge
                );

                if (common == remaining.length()) return true;
                if (common != child.edge.length()) return false;

                remaining = remaining.substring(common);
                node = child;
            }

            return true;
        }

        public synchronized List<String> autocomplete(
            String prefix,
            int limit
        ) {
            if (limit < 0) {
                throw new IllegalArgumentException(
                    "Limit cannot be negative."
                );
            }

            if (prefix == null || prefix.isEmpty() || limit == 0) {
                return List.of();
            }

            Node node = root;
            String remaining = prefix;
            StringBuilder accumulated = new StringBuilder();

            while (!remaining.isEmpty()) {
                Node child = node.children.get(remaining.charAt(0));

                if (child == null) return List.of();

                int common = commonPrefix(
                    remaining,
                    child.edge
                );

                if (
                    common < remaining.length() &&
                    common < child.edge.length()
                ) {
                    return List.of();
                }

                accumulated.append(child.edge);
                remaining = remaining.substring(common);
                node = child;
            }

            List<String> result = new ArrayList<>();

            collect(
                node,
                accumulated.toString(),
                result,
                limit
            );

            return List.copyOf(result);
        }

        private void collect(
            Node node,
            String current,
            List<String> results,
            int limit
        ) {
            if (results.size() >= limit) return;

            if (node.terminal) {
                results.add(current);
            }

            node.children.entrySet()
                .stream()
                .sorted(Map.Entry.comparingByKey())
                .forEach(entry -> {
                    if (results.size() < limit) {
                        Node child = entry.getValue();

                        collect(
                            child,
                            current + child.edge,
                            results,
                            limit
                        );
                    }
                });
        }

        public synchronized boolean delete(String word) {
            if (!search(word)) return false;

            remove(root, word);
            size--;
            return true;
        }

        private void remove(Node parent, String remaining) {
            Node child = parent.children.get(remaining.charAt(0));

            String suffix = remaining.substring(child.edge.length());

            if (!suffix.isEmpty()) {
                remove(child, suffix);
            } else {
                child.terminal = false;
                child.value = null;
            }

            if (!child.terminal && child.children.isEmpty()) {
                parent.children.remove(child.edge.charAt(0));
            } else if (
                !child.terminal &&
                child.children.size() == 1
            ) {
                Node next = child.children.values()
                    .iterator()
                    .next();

                child.edge += next.edge;
                child.children = next.children;
                child.terminal = next.terminal;
                child.value = next.value;
            }
        }

        public int size() {
            return size;
        }
    }


    // ========================================================
    // 4. BINARY TRIE FOR XOR ANALYTICS
    // ========================================================

    static final class BinaryTrie {

        private static final class Node {
            Node[] children = new Node[2];
            long count;
        }

        private final int width;
        private final long maximumValue;
        private Node root = new Node();
        private long size;

        BinaryTrie(int width) {
            if (width < 1 || width > 63) {
                throw new IllegalArgumentException(
                    "Width must be between 1 and 63."
                );
            }

            this.width = width;
            this.maximumValue = (1L << width) - 1;
        }

        private void validate(long value) {
            if (value < 0 || value > maximumValue) {
                throw new IllegalArgumentException(
                    "Value exceeds configured bit width."
                );
            }
        }

        public void insert(long value) {
            validate(value);

            Node node = root;
            node.count++;

            for (int bit = width - 1; bit >= 0; bit--) {
                int direction = (int) ((value >>> bit) & 1L);

                if (node.children[direction] == null) {
                    node.children[direction] = new Node();
                }

                node = node.children[direction];
                node.count++;
            }

            size++;
        }

        public boolean contains(long value) {
            validate(value);

            Node node = root;

            for (int bit = width - 1; bit >= 0; bit--) {
                int direction = (int) ((value >>> bit) & 1L);

                node = node.children[direction];

                if (node == null || node.count == 0) {
                    return false;
                }
            }

            return true;
        }

        public boolean delete(long value) {
            validate(value);

            if (!contains(value)) return false;

            Node node = root;
            node.count--;

            for (int bit = width - 1; bit >= 0; bit--) {
                int direction = (int) ((value >>> bit) & 1L);
                Node child = node.children[direction];

                child.count--;

                if (child.count == 0) {
                    node.children[direction] = null;
                    break;
                }

                node = child;
            }

            size--;
            return true;
        }

        public XorResult query(
            long value,
            QueryMode mode
        ) {
            validate(value);

            if (size == 0) {
                throw new TrieException(
                    "Cannot query an empty binary trie."
                );
            }

            Node node = root;
            long matched = 0;
            long xor = 0;

            for (int bit = width - 1; bit >= 0; bit--) {
                int current = (int) ((value >>> bit) & 1L);

                int preferred =
                    mode == QueryMode.MAXIMUM
                    ? 1 - current
                    : current;

                int alternative = 1 - preferred;

                int selected =
                    node.children[preferred] != null &&
                    node.children[preferred].count > 0
                    ? preferred
                    : alternative;

                if (selected != current) {
                    xor |= 1L << bit;
                }

                matched |= (long) selected << bit;
                node = node.children[selected];
            }

            return new XorResult(xor, matched);
        }

        public Optional<XorPair> maximumXorPair(
            List<Long> values
        ) {
            if (values.size() < 2) return Optional.empty();

            root = new Node();
            size = 0;

            long best = -1;
            long first = 0;
            long second = 0;

            for (long value : values) {
                validate(value);

                if (size > 0) {
                    XorResult result = query(
                        value,
                        QueryMode.MAXIMUM
                    );

                    if (result.xorValue() > best) {
                        best = result.xorValue();
                        first = value;
                        second = result.matchedValue();
                    }
                }

                insert(value);
            }

            return Optional.of(
                new XorPair(best, first, second)
            );
        }

        public long size() {
            return size;
        }
    }


    // ========================================================
    // 5. ENTERPRISE DICTIONARY SERVICE
    // ========================================================

    static final class DictionaryService {

        private final RadixTrie trie = new RadixTrie();

        private final ConcurrentMap<String, DictionaryRecord> records =
            new ConcurrentHashMap<>();

        private final AtomicLong version = new AtomicLong();

        public DictionaryRecord register(
            String word,
            String category
        ) {
            long nextVersion = version.incrementAndGet();

            DictionaryRecord record = new DictionaryRecord(
                word,
                category,
                RecordStatus.ACTIVE,
                nextVersion
            );

            synchronized (trie) {
                trie.insert(word, category);
                records.put(word, record);
            }

            return record;
        }

        public Optional<DictionaryRecord> find(String word) {
            if (!trie.search(word)) {
                return Optional.empty();
            }

            return Optional.ofNullable(records.get(word));
        }

        public List<DictionaryRecord> suggest(
            String prefix,
            int limit
        ) {
            return trie.autocomplete(prefix, limit)
                .stream()
                .map(records::get)
                .filter(Objects::nonNull)
                .filter(record ->
                    record.status() == RecordStatus.ACTIVE
                )
                .collect(Collectors.toUnmodifiableList());
        }

        public boolean delete(String word) {
            synchronized (trie) {
                if (!trie.delete(word)) return false;

                records.remove(word);
                return true;
            }
        }
    }


    // ========================================================
    // 6. MERGE ELIGIBILITY POLICY SERVICE
    // ========================================================

    static final class MergePolicyService {

        public Eligibility evaluate(
            MergeRequest request,
            Policy policy
        ) {
            List<String> blockers = new ArrayList<>();

            if (request.state() == MergeState.CLOSED) {
                blockers.add("Request is closed.");
            }

            if (request.state() == MergeState.MERGED) {
                blockers.add("Request is already merged.");
            }

            if (
                request.draft() &&
                !policy.allowDraftMerge()
            ) {
                blockers.add("Draft requests cannot be merged.");
            }

            if (request.conflict()) {
                blockers.add("Merge conflict detected.");
            }

            if (
                request.approvals() <
                policy.minimumApprovals()
            ) {
                blockers.add("Insufficient approvals.");
            }

            if (
                policy.requireStatusChecks() &&
                !request.checksPassed()
            ) {
                blockers.add("Required checks failed.");
            }

            if (
                policy.requireResolvedConversations() &&
                !request.conversationsResolved()
            ) {
                blockers.add("Unresolved review conversations.");
            }

            if (
                policy.requireSynchronizedBranch() &&
                !request.branchSynchronized()
            ) {
                blockers.add("Source branch is outdated.");
            }

            if (
                policy.requireLinearHistory() &&
                !request.linearHistory()
            ) {
                blockers.add("Linear history requirement failed.");
            }

            return new Eligibility(
                blockers.isEmpty(),
                blockers
            );
        }

        public MergeRequest transition(
            MergeRequest request,
            MergeState next,
            Policy policy
        ) {
            if (request.state() == MergeState.MERGED ||
                request.state() == MergeState.CLOSED) {
                throw new PolicyViolationException(
                    "Terminal requests cannot transition."
                );
            }

            if (next == MergeState.MERGED) {
                Eligibility eligibility = evaluate(request, policy);

                if (!eligibility.eligible()) {
                    throw new PolicyViolationException(
                        String.join("; ", eligibility.blockers())
                    );
                }
            }

            return new MergeRequest(
                request.id(),
                request.sourceBranch(),
                request.targetBranch(),
                request.draft(),
                request.conflict(),
                request.checksPassed(),
                request.conversationsResolved(),
                request.branchSynchronized(),
                request.linearHistory(),
                request.approvals(),
                next
            );
        }
    }


    // ========================================================
    // 7. EXECUTABLE ENTERPRISE SCENARIO
    // ========================================================

    public static void main(String[] args) {

        System.out.println("ADVANCED TRIE ENTERPRISE SYSTEM");

        // Compressed prefix dictionary.
        System.out.println("\nCOMPRESSED RADIX TRIE");

        DictionaryService dictionary = new DictionaryService();

        dictionary.register("application", "software");
        dictionary.register("apply", "action");
        dictionary.register("apple", "product");
        dictionary.register("app", "abbreviation");
        dictionary.register("binary", "computer science");
        dictionary.register("bitwise", "algorithm");

        System.out.println(
            "Exact search: " +
            dictionary.find("application")
        );

        System.out.println(
            "Prefix suggestions: " +
            dictionary.suggest("app", 10)
        );

        dictionary.delete("apple");

        System.out.println(
            "After deletion: " +
            dictionary.find("apple")
        );

        // Maximum XOR analytics.
        System.out.println("\nBINARY TRIE");

        BinaryTrie binary = new BinaryTrie(8);

        List<Long> values = List.of(
            3L, 10L, 5L, 25L, 2L, 8L
        );

        binary.maximumXorPair(values).ifPresent(result -> {
            System.out.println("Maximum XOR: " + result.maximumXor());
            System.out.println(
                "Pair: " + result.first() + ", " + result.second()
            );
        });

        binary.insert(12);
        binary.insert(12);

        System.out.println("Contains duplicate: " + binary.contains(12));

        binary.delete(12);

        System.out.println(
            "Contains after first deletion: " + binary.contains(12)
        );

        binary.delete(12);

        System.out.println(
            "Contains after second deletion: " + binary.contains(12)
        );

        // Enterprise governance.
        System.out.println("\nMERGE POLICY ENGINE");

        Policy policy = new Policy(
            2,
            true,
            true,
            true,
            true,
            false
        );

        MergeRequest request = new MergeRequest(
            "PR-1042",
            "feature/advanced-trie",
            "main",
            false,
            false,
            true,
            true,
            true,
            true,
            2,
            MergeState.APPROVED
        );

        MergePolicyService policyService =
            new MergePolicyService();

        Eligibility eligibility =
            policyService.evaluate(request, policy);

        System.out.println(
            "Eligible: " + eligibility.eligible()
        );

        System.out.println(
            "Blockers: " + eligibility.blockers()
        );

        if (eligibility.eligible()) {
            MergeRequest merged = policyService.transition(
                request,
                MergeState.MERGED,
                policy
            );

            System.out.println(
                "New state: " + merged.state()
            );
        }

        // Blocked request.
        System.out.println("\nBLOCKED REQUEST");

        MergeRequest blocked = new MergeRequest(
            "PR-1043",
            "feature/experimental",
            "main",
            true,
            true,
            false,
            false,
            false,
            false,
            0,
            MergeState.OPEN
        );

        Eligibility blockedResult =
            policyService.evaluate(blocked, policy);

        blockedResult.blockers().forEach(
            System.out::println
        );

        // Minimum XOR.
        System.out.println("\nMINIMUM XOR");

        BinaryTrie minimumTrie = new BinaryTrie(8);
        minimumTrie.insert(10);
        minimumTrie.insert(12);

        System.out.println(
            minimumTrie.query(10, QueryMode.MINIMUM)
        );

        // Error handling.
        System.out.println("\nVALIDATION");

        try {
            binary.insert(256);
        } catch (IllegalArgumentException error) {
            System.out.println(error.getMessage());
        }

        try {
            new BinaryTrie(8).query(
                1,
                QueryMode.MAXIMUM
            );
        } catch (TrieException error) {
            System.out.println(error.getMessage());
        }

        try {
            dictionary.register("", "invalid");
        } catch (IllegalArgumentException error) {
            System.out.println(error.getMessage());
        }

        // Brute-force verification.
        System.out.println("\nRANDOMIZED VALIDATION");

        Random random = new Random(42);
        List<Long> randomValues = new ArrayList<>();

        for (int i = 0; i < 1000; i++) {
            randomValues.add((long) random.nextInt(65536));
        }

        BinaryTrie testTrie = new BinaryTrie(16);

        XorPair optimized = testTrie
            .maximumXorPair(randomValues)
            .orElseThrow();

        long bruteForce = 0;

        for (int i = 0; i < randomValues.size(); i++) {
            for (int j = i + 1; j < randomValues.size(); j++) {
                bruteForce = Math.max(
                    bruteForce,
                    randomValues.get(i) ^ randomValues.get(j)
                );
            }
        }

        if (optimized.maximumXor() != bruteForce) {
            throw new AssertionError(
                "Optimized and brute-force results differ."
            );
        }

        System.out.println("Optimized: " + optimized.maximumXor());
        System.out.println("Brute force: " + bruteForce);
        System.out.println("Validation passed.");

        System.out.println("\nEXECUTION COMPLETED");
    }
}
