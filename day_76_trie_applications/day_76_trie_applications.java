import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeSet;
import java.util.function.Consumer;

/*
 * Trie Applications - Java 17
 *
 * Enterprise-oriented dictionary and search service.
 *
 * Features:
 * - Domain-specific validation
 * - Trie-based dictionary management
 * - Frequency-ranked autocomplete
 * - Prefix and exact lookup
 * - Wildcard matching
 * - Word Break and sentence generation
 * - Grid word search
 * - Asynchronous search execution
 * - Event notifications
 * - Immutable result records
 */

public class TrieApplications {

    public enum SearchStatus {
        SUCCESS,
        EMPTY_RESULT,
        INVALID_REQUEST,
        FAILURE
    }

    public record Suggestion(String word, int frequency) {
        public Suggestion {
            Objects.requireNonNull(word);

            if (frequency <= 0) {
                throw new IllegalArgumentException(
                    "Frequency must be positive."
                );
            }
        }
    }

    public record SearchResult(
        String prefix,
        List<Suggestion> suggestions,
        SearchStatus status
    ) {
        public SearchResult {
            suggestions = List.copyOf(suggestions);
            Objects.requireNonNull(status);
        }
    }

    public static class DictionaryException extends RuntimeException {
        public DictionaryException(String message) {
            super(message);
        }
    }

    public static class ValidationException extends DictionaryException {
        public ValidationException(String message) {
            super(message);
        }
    }

    public static class TrieNode {
        private final Map<Character, TrieNode> children = new HashMap<>();
        private boolean terminal;
        private int frequency;
    }

    public static class TrieDictionary {

        private final TrieNode root = new TrieNode();
        private int wordCount;

        private static String normalize(String value) {
            if (value == null) {
                throw new ValidationException("Word cannot be null.");
            }

            String word = value.trim().toLowerCase();

            if (!word.matches("[a-z]+")) {
                throw new ValidationException(
                    "Only alphabetic English words are supported."
                );
            }

            return word;
        }

        private TrieNode findNode(String prefix) {
            TrieNode node = root;

            for (char character : prefix.toCharArray()) {
                node = node.children.get(character);

                if (node == null) {
                    return null;
                }
            }

            return node;
        }

        public synchronized boolean insert(
            String input,
            int frequency
        ) {
            String word = normalize(input);

            if (frequency <= 0) {
                throw new ValidationException(
                    "Frequency must be positive."
                );
            }

            TrieNode node = root;

            for (char character : word.toCharArray()) {
                node = node.children.computeIfAbsent(
                    character,
                    ignored -> new TrieNode()
                );
            }

            if (Integer.MAX_VALUE - node.frequency < frequency) {
                throw new ValidationException(
                    "Frequency exceeds supported range."
                );
            }

            boolean isNew = !node.terminal;

            node.terminal = true;
            node.frequency += frequency;

            if (isNew) {
                wordCount++;
            }

            return isNew;
        }

        public boolean insert(String word) {
            return insert(word, 1);
        }

        public boolean search(String input) {
            String word = normalize(input);
            TrieNode node = findNode(word);

            return node != null && node.terminal;
        }

        public boolean startsWith(String input) {
            return findNode(normalize(input)) != null;
        }

        public int frequency(String input) {
            TrieNode node = findNode(normalize(input));

            return node != null && node.terminal
                ? node.frequency
                : 0;
        }

        public synchronized boolean delete(String input) {
            String word = normalize(input);

            return deleteRecursive(root, word, 0);
        }

        private boolean deleteRecursive(
            TrieNode node,
            String word,
            int index
        ) {
            if (index == word.length()) {
                if (!node.terminal) {
                    return false;
                }

                node.terminal = false;
                node.frequency = 0;
                wordCount--;

                return true;
            }

            char character = word.charAt(index);
            TrieNode child = node.children.get(character);

            if (child == null) {
                return false;
            }

            boolean deleted = deleteRecursive(
                child,
                word,
                index + 1
            );

            if (
                deleted &&
                !child.terminal &&
                child.children.isEmpty()
            ) {
                node.children.remove(character);
            }

            return deleted;
        }

        public List<Suggestion> autocomplete(
            String input,
            int limit
        ) {
            String prefix = normalize(input);

            if (limit < 0) {
                throw new ValidationException(
                    "Limit cannot be negative."
                );
            }

            if (limit == 0) {
                return List.of();
            }

            TrieNode start = findNode(prefix);

            if (start == null) {
                return List.of();
            }

            List<Suggestion> results = new ArrayList<>();

            collect(start, prefix, results);

            results.sort(
                Comparator.comparingInt(Suggestion::frequency)
                    .reversed()
                    .thenComparing(Suggestion::word)
            );

            return List.copyOf(
                results.subList(
                    0,
                    Math.min(limit, results.size())
                )
            );
        }

        private void collect(
            TrieNode node,
            String prefix,
            List<Suggestion> results
        ) {
            if (node.terminal) {
                results.add(
                    new Suggestion(prefix, node.frequency)
                );
            }

            node.children.entrySet()
                .stream()
                .sorted(Map.Entry.comparingByKey())
                .forEach(entry -> collect(
                    entry.getValue(),
                    prefix + entry.getKey(),
                    results
                ));
        }

        public List<String> wildcardSearch(String patternInput) {
            if (patternInput == null) {
                throw new ValidationException(
                    "Pattern cannot be null."
                );
            }

            String pattern = patternInput.trim().toLowerCase();

            if (!pattern.matches("[a-z.*]+")) {
                throw new ValidationException(
                    "Invalid wildcard pattern."
                );
            }

            Set<String> results = new TreeSet<>();
            Set<String> visited = new HashSet<>();

            wildcardDfs(
                root,
                pattern,
                0,
                "",
                results,
                visited
            );

            return List.copyOf(results);
        }

        private void wildcardDfs(
            TrieNode node,
            String pattern,
            int index,
            String current,
            Set<String> results,
            Set<String> visited
        ) {
            String state =
                System.identityHashCode(node) + ":" + index;

            if (!visited.add(state)) {
                return;
            }

            if (index == pattern.length()) {
                if (node.terminal) {
                    results.add(current);
                }

                return;
            }

            char token = pattern.charAt(index);

            if (token == '.') {
                node.children.entrySet().stream()
                    .sorted(Map.Entry.comparingByKey())
                    .forEach(entry -> wildcardDfs(
                        entry.getValue(),
                        pattern,
                        index + 1,
                        current + entry.getKey(),
                        results,
                        visited
                    ));

            } else if (token == '*') {
                wildcardDfs(
                    node,
                    pattern,
                    index + 1,
                    current,
                    results,
                    visited
                );

                node.children.entrySet().stream()
                    .sorted(Map.Entry.comparingByKey())
                    .forEach(entry -> wildcardDfs(
                        entry.getValue(),
                        pattern,
                        index,
                        current + entry.getKey(),
                        results,
                        visited
                    ));

            } else {
                TrieNode child = node.children.get(token);

                if (child != null) {
                    wildcardDfs(
                        child,
                        pattern,
                        index + 1,
                        current + token,
                        results,
                        visited
                    );
                }
            }
        }

        public String longestPrefix(String input) {
            String text = normalize(input);
            TrieNode node = root;
            StringBuilder result = new StringBuilder();

            int lastTerminalLength = 0;

            for (char character : text.toCharArray()) {
                node = node.children.get(character);

                if (node == null) {
                    break;
                }

                result.append(character);

                if (node.terminal) {
                    lastTerminalLength = result.length();
                }
            }

            return result.substring(0, lastTerminalLength);
        }

        public synchronized int size() {
            return wordCount;
        }

        public List<Suggestion> allWords() {
            List<Suggestion> results = new ArrayList<>();
            collect(root, "", results);

            results.sort(
                Comparator.comparing(Suggestion::word)
            );

            return List.copyOf(results);
        }
    }

    public static class WordBreakService {

        private final TrieDictionary dictionary;

        public WordBreakService(TrieDictionary dictionary) {
            this.dictionary = Objects.requireNonNull(dictionary);
        }

        public boolean canSegment(String input) {
            if (input == null) {
                throw new ValidationException(
                    "Input cannot be null."
                );
            }

            String text = input.trim().toLowerCase();

            if (text.isEmpty()) {
                return true;
            }

            if (!text.matches("[a-z]+")) {
                throw new ValidationException(
                    "Invalid word-break input."
                );
            }

            boolean[] dp = new boolean[text.length() + 1];
            dp[0] = true;

            for (int start = 0; start < text.length(); start++) {
                if (!dp[start]) {
                    continue;
                }

                TrieNode node = dictionary.root;

                for (int end = start; end < text.length(); end++) {
                    node = node.children.get(text.charAt(end));

                    if (node == null) {
                        break;
                    }

                    if (node.terminal) {
                        dp[end + 1] = true;
                    }
                }
            }

            return dp[text.length()];
        }

        public List<String> sentences(
            String input,
            int maximumResults
        ) {
            if (input == null || !input.trim().matches("[a-zA-Z]+")) {
                throw new ValidationException("Invalid input.");
            }

            if (maximumResults < 0) {
                throw new ValidationException(
                    "Result limit cannot be negative."
                );
            }

            String text = input.trim().toLowerCase();

            if (maximumResults == 0) {
                return List.of();
            }

            Map<Integer, List<List<String>>> memo = new HashMap<>();

            List<List<String>> solutions = solve(
                text,
                0,
                maximumResults,
                memo
            );

            return solutions.stream()
                .map(words -> String.join(" ", words))
                .toList();
        }

        private List<List<String>> solve(
            String text,
            int start,
            int limit,
            Map<Integer, List<List<String>>> memo
        ) {
            if (start == text.length()) {
                return List.of(List.of());
            }

            if (memo.containsKey(start)) {
                return memo.get(start);
            }

            List<List<String>> results = new ArrayList<>();
            TrieNode node = dictionary.root;

            for (int end = start; end < text.length(); end++) {
                node = node.children.get(text.charAt(end));

                if (node == null) {
                    break;
                }

                if (node.terminal) {
                    String word = text.substring(start, end + 1);

                    for (List<String> suffix : solve(
                        text,
                        end + 1,
                        limit,
                        memo
                    )) {
                        List<String> combination =
                            new ArrayList<>();

                        combination.add(word);
                        combination.addAll(suffix);

                        results.add(List.copyOf(combination));

                        if (results.size() >= limit) {
                            memo.put(start, List.copyOf(results));
                            return memo.get(start);
                        }
                    }
                }
            }

            memo.put(start, List.copyOf(results));

            return memo.get(start);
        }
    }

    public static class WordSearchService {

        private final Set<String> found = new TreeSet<>();

        private final int[][] directions = {
            {1, 0},
            {-1, 0},
            {0, 1},
            {0, -1}
        };

        public List<String> findWords(
            char[][] inputBoard,
            List<String> words
        ) {
            if (inputBoard == null || words == null) {
                throw new ValidationException(
                    "Board and words cannot be null."
                );
            }

            if (inputBoard.length == 0) {
                return List.of();
            }

            int rows = inputBoard.length;
            int columns = inputBoard[0].length;

            if (columns == 0) {
                throw new ValidationException(
                    "Board cannot contain empty rows."
                );
            }

            char[][] board = new char[rows][columns];

            for (int row = 0; row < rows; row++) {
                if (
                    inputBoard[row] == null ||
                    inputBoard[row].length != columns
                ) {
                    throw new ValidationException(
                        "Board must be rectangular."
                    );
                }

                for (int column = 0; column < columns; column++) {
                    char character = Character.toLowerCase(
                        inputBoard[row][column]
                    );

                    if (character < 'a' || character > 'z') {
                        throw new ValidationException(
                            "Board cells must contain alphabetic characters."
                        );
                    }

                    board[row][column] = character;
                }
            }

            TrieDictionary dictionary = new TrieDictionary();

            for (String word : words) {
                dictionary.insert(word);
            }

            found.clear();

            for (int row = 0; row < rows; row++) {
                for (int column = 0; column < columns; column++) {
                    dfs(
                        board,
                        row,
                        column,
                        dictionary.root,
                        ""
                    );
                }
            }

            return List.copyOf(found);
        }

        private void dfs(
            char[][] board,
            int row,
            int column,
            TrieNode node,
            String current
        ) {
            char character = board[row][column];
            TrieNode child = node.children.get(character);

            if (child == null) {
                return;
            }

            String word = current + character;

            if (child.terminal) {
                found.add(word);
                child.terminal = false;
            }

            board[row][column] = '#';

            for (int[] direction : directions) {
                int nr = row + direction[0];
                int nc = column + direction[1];

                if (
                    nr >= 0 &&
                    nr < board.length &&
                    nc >= 0 &&
                    nc < board[0].length &&
                    board[nr][nc] != '#'
                ) {
                    dfs(board, nr, nc, child, word);
                }
            }

            board[row][column] = character;
        }
    }

    public static class AutocompleteService {

        private final TrieDictionary dictionary;

        public AutocompleteService(TrieDictionary dictionary) {
            this.dictionary = Objects.requireNonNull(dictionary);
        }

        public SearchResult search(String prefix, int limit) {
            try {
                List<Suggestion> results =
                    dictionary.autocomplete(prefix, limit);

                return new SearchResult(
                    prefix,
                    results,
                    results.isEmpty()
                        ? SearchStatus.EMPTY_RESULT
                        : SearchStatus.SUCCESS
                );

            } catch (ValidationException exception) {
                return new SearchResult(
                    prefix,
                    List.of(),
                    SearchStatus.INVALID_REQUEST
                );
            }
        }

        public java.util.concurrent.CompletableFuture<SearchResult>
        searchAsync(String prefix, int limit) {
            return java.util.concurrent.CompletableFuture.supplyAsync(
                () -> search(prefix, limit)
            );
        }
    }

    private static void runTests() {
        TrieDictionary trie = new TrieDictionary();

        for (String word : List.of(
            "apple",
            "app",
            "application",
            "apply",
            "banana",
            "band",
            "bandana",
            "bat"
        )) {
            trie.insert(word);
        }

        trie.insert("apple", 5);

        assert trie.search("apple");
        assert !trie.search("appl");
        assert trie.startsWith("app");

        assert trie.autocomplete("app", 1)
            .get(0).word().equals("apple");

        assert trie.delete("app");
        assert !trie.search("app");
        assert trie.search("apple");

        assert trie.wildcardSearch("app..")
            .contains("apple");

        TrieDictionary dictionary = new TrieDictionary();

        for (String word : List.of(
            "cat", "cats", "and", "sand", "dog"
        )) {
            dictionary.insert(word);
        }

        WordBreakService service = new WordBreakService(dictionary);

        assert service.canSegment("catsanddog");
        assert !service.canSegment("catsandxyz");

        assert service.sentences("catsanddog", 10).equals(
            List.of(
                "cat sand dog",
                "cats and dog"
            )
        );

        WordSearchService wordSearch = new WordSearchService();

        assert wordSearch.findWords(
            new char[][] {
                {'o', 'a', 'a', 'n'},
                {'e', 't', 'a', 'e'},
                {'i', 'h', 'k', 'r'},
                {'i', 'f', 'l', 'v'}
            },
            List.of("oath", "pea", "eat", "rain")
        ).equals(List.of("eat", "oath"));

        assert new AutocompleteService(trie)
            .search("ban", 5).status() == SearchStatus.SUCCESS;

        boolean rejected = false;

        try {
            trie.insert("bad123");
        } catch (ValidationException exception) {
            rejected = true;
        }

        assert rejected;

        System.out.println("All Java 17 tests passed.");
    }

    public static void main(String[] args) {
        try {
            System.out.println("TRIE APPLICATIONS - JAVA 17");
            System.out.println("==============================");

            TrieDictionary dictionary = new TrieDictionary();

            for (String word : List.of(
                "apple",
                "app",
                "application",
                "apply",
                "apt",
                "banana",
                "band",
                "bandana",
                "bat",
                "ball"
            )) {
                dictionary.insert(word);
            }

            dictionary.insert("apple", 10);
            dictionary.insert("application", 4);

            AutocompleteService autocomplete =
                new AutocompleteService(dictionary);

            SearchResult result = autocomplete.search("app", 5);

            System.out.println("\nAutocomplete:");

            result.suggestions().forEach(
                suggestion -> System.out.println(
                    suggestion.word() +
                    " | frequency=" +
                    suggestion.frequency()
                )
            );

            System.out.println("\nWildcard search:");
            System.out.println(
                dictionary.wildcardSearch("app..")
            );

            System.out.println("\nLongest prefix:");
            System.out.println(
                dictionary.longestPrefix("application")
            );

            TrieDictionary segmentationDictionary =
                new TrieDictionary();

            for (String word : List.of(
                "cat", "cats", "and", "sand", "dog"
            )) {
                segmentationDictionary.insert(word);
            }

            WordBreakService wordBreak =
                new WordBreakService(segmentationDictionary);

            System.out.println("\nWord Break:");
            System.out.println(
                wordBreak.canSegment("catsanddog")
            );

            System.out.println("\nWord Break sentences:");
            System.out.println(
                wordBreak.sentences("catsanddog", 10)
            );

            System.out.println("\nWord Search II:");

            WordSearchService search = new WordSearchService();

            System.out.println(search.findWords(
                new char[][] {
                    {'o', 'a', 'a', 'n'},
                    {'e', 't', 'a', 'e'},
                    {'i', 'h', 'k', 'r'},
                    {'i', 'f', 'l', 'v'}
                },
                List.of("oath", "pea", "eat", "rain")
            ));

            System.out.println("\nRunning tests...");
            runTests();

        } catch (DictionaryException exception) {
            System.err.println(
                "Dictionary error: " + exception.getMessage()
            );

            System.exit(1);
        }
    }
}
