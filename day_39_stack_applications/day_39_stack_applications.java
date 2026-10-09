import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;
import java.util.Map;
import java.util.function.DoubleBinaryOperator;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/*
 * Stack Applications
 *
 * Enterprise-oriented model covering:
 * - nested input validation
 * - expression evaluation
 * - explicit activation records
 * - undo/redo state management
 *
 * Java records provide immutable value objects while ArrayDeque provides
 * efficient stack operations without exposing implementation details.
 */
public class StackApplications {

    // -------------------------------------------------------------------------
    // Balanced Parentheses
    // -------------------------------------------------------------------------

    private static final Map<Character, Character> CLOSING_TO_OPENING = Map.of(
        ')', '(',
        ']', '[',
        '}', '{'
    );

    private static final Map<Character, Character> OPENING_TO_CLOSING = Map.of(
        '(', ')',
        '[', ']',
        '{', '}'
    );

    public static ValidationResult validateBrackets(String input) {
        Deque<Character> stack = new ArrayDeque<>();
        Character quote = null;
        boolean escaped = false;

        for (int index = 0; index < input.length(); index++) {
            char character = input.charAt(index);

            if (quote != null) {
                if (escaped) {
                    escaped = false;
                } else if (character == '\\') {
                    escaped = true;
                } else if (character == quote) {
                    quote = null;
                }
                continue;
            }

            if (character == '\'' || character == '"') {
                quote = character;
            } else if (OPENING_TO_CLOSING.containsKey(character)) {
                stack.push(character);
            } else if (CLOSING_TO_OPENING.containsKey(character)) {
                if (stack.isEmpty()) {
                    return new ValidationResult(
                        false,
                        "Unexpected closing delimiter at index " + index
                    );
                }

                char opening = stack.pop();
                if (opening != CLOSING_TO_OPENING.get(character)) {
                    return new ValidationResult(
                        false,
                        "Mismatched delimiter at index " + index
                    );
                }
            }
        }

        if (quote != null) {
            return new ValidationResult(false, "Unterminated quoted string");
        }

        if (!stack.isEmpty()) {
            return new ValidationResult(
                false,
                "Unclosed opening delimiter " + stack.peek()
            );
        }

        return new ValidationResult(true, "Balanced");
    }

    public record ValidationResult(boolean valid, String message) {}

    // -------------------------------------------------------------------------
    // Expression Evaluation
    // -------------------------------------------------------------------------

    private static final Pattern TOKEN_PATTERN =
        Pattern.compile("\\s*(?:(\\d+(?:\\.\\d*)?|\\.\\d+)|([+\\-*/%^()]))");

    private static final Map<String, Integer> PRECEDENCE = Map.of(
        "+", 1,
        "-", 1,
        "*", 2,
        "/", 2,
        "%", 2,
        "^", 3
    );

    private static final Map<String, DoubleBinaryOperator> OPERATIONS = Map.of(
        "+", (a, b) -> a + b,
        "-", (a, b) -> a - b,
        "*", (a, b) -> a * b,
        "/", (a, b) -> {
            if (b == 0.0) {
                throw new ArithmeticException("Division by zero");
            }
            return a / b;
        },
        "%", (a, b) -> {
            if (b == 0.0) {
                throw new ArithmeticException("Remainder by zero");
            }
            return a % b;
        },
        "^", Math::pow
    );

    private static List<String> tokenize(String expression) {
        List<String> tokens = new ArrayList<>();
        Matcher matcher = TOKEN_PATTERN.matcher(expression);
        int position = 0;

        while (position < expression.length()) {
            matcher.region(position, expression.length());

            if (!matcher.lookingAt()) {
                throw new IllegalArgumentException(
                    "Invalid expression near index " + position
                );
            }

            if (matcher.group(1) != null) {
                tokens.add(matcher.group(1));
            } else {
                tokens.add(matcher.group(2));
            }

            position = matcher.end();
        }

        if (tokens.isEmpty()) {
            throw new IllegalArgumentException("Expression cannot be empty");
        }

        return tokens;
    }

    private static boolean isNumber(String token) {
        return token.matches("(?:\\d+(?:\\.\\d*)?|\\.\\d+)");
    }

    private static boolean isOperator(String token) {
        return PRECEDENCE.containsKey(token);
    }

    private static List<String> toPostfix(String expression) {
        List<String> tokens = tokenize(expression);
        List<String> output = new ArrayList<>();
        Deque<String> operators = new ArrayDeque<>();
        String previous = null;

        for (String token : tokens) {
            if (isNumber(token)) {
                output.add(token);
                previous = "number";
                continue;
            }

            if (token.equals("(")) {
                operators.push(token);
                previous = "left";
                continue;
            }

            if (token.equals(")")) {
                boolean matched = false;

                while (!operators.isEmpty()) {
                    String top = operators.pop();

                    if (top.equals("(")) {
                        matched = true;
                        break;
                    }

                    output.add(top);
                }

                if (!matched) {
                    throw new IllegalArgumentException(
                        "Unmatched closing parenthesis"
                    );
                }

                previous = "right";
                continue;
            }

            if (isOperator(token)) {
                if (
                    token.equals("-") &&
                    (previous == null ||
                     previous.equals("operator") ||
                     previous.equals("left"))
                ) {
                    output.add("0");
                }

                while (!operators.isEmpty() &&
                       !operators.peek().equals("(")) {

                    String top = operators.peek();

                    boolean higher = PRECEDENCE.get(top) >
                                     PRECEDENCE.get(token);

                    boolean equalLeftAssociative =
                        PRECEDENCE.get(top).equals(PRECEDENCE.get(token)) &&
                        !token.equals("^");

                    if (!higher && !equalLeftAssociative) {
                        break;
                    }

                    output.add(operators.pop());
                }

                operators.push(token);
                previous = "operator";
            }
        }

        while (!operators.isEmpty()) {
            String operator = operators.pop();

            if (operator.equals("(")) {
                throw new IllegalArgumentException(
                    "Unmatched opening parenthesis"
                );
            }

            output.add(operator);
        }

        return output;
    }

    private static double evaluate(String expression) {
        Deque<Double> values = new ArrayDeque<>();

        for (String token : toPostfix(expression)) {
            if (isNumber(token)) {
                values.push(Double.parseDouble(token));
                continue;
            }

            if (values.size() < 2) {
                throw new IllegalArgumentException("Insufficient operands");
            }

            double right = values.pop();
            double left = values.pop();

            DoubleBinaryOperator operation = OPERATIONS.get(token);
            if (operation == null) {
                throw new IllegalArgumentException(
                    "Unsupported operator " + token
                );
            }

            double result = operation.applyAsDouble(left, right);

            if (!Double.isFinite(result)) {
                throw new ArithmeticException(
                    "Expression produced a non-finite result"
                );
            }

            values.push(result);
        }

        if (values.size() != 1) {
            throw new IllegalArgumentException("Malformed expression");
        }

        return values.pop();
    }

    // -------------------------------------------------------------------------
    // Enterprise Function Call Model
    // -------------------------------------------------------------------------

    public record ActivationRecord(
        String functionName,
        List<String> arguments,
        Map<String, Object> localVariables
    ) {}

    public static final class CallStack {
        private final Deque<ActivationRecord> frames = new ArrayDeque<>();

        public void enter(
            String functionName,
            List<String> arguments,
            Map<String, Object> localVariables
        ) {
            if (functionName == null || functionName.isBlank()) {
                throw new IllegalArgumentException(
                    "Function name is required"
                );
            }

            frames.push(
                new ActivationRecord(
                    functionName,
                    List.copyOf(arguments),
                    Map.copyOf(localVariables)
                )
            );
        }

        public ActivationRecord exit() {
            if (frames.isEmpty()) {
                throw new IllegalStateException(
                    "Cannot exit an empty call stack"
                );
            }

            return frames.pop();
        }

        public int depth() {
            return frames.size();
        }

        public List<String> activeFunctions() {
            return frames.stream()
                .map(ActivationRecord::functionName)
                .toList();
        }
    }

    // -------------------------------------------------------------------------
    // Undo / Redo Domain
    // -------------------------------------------------------------------------

    public record DocumentState(String content) {}

    public static final class DocumentService {
        private DocumentState current;
        private final Deque<DocumentState> undoHistory = new ArrayDeque<>();
        private final Deque<DocumentState> redoHistory = new ArrayDeque<>();

        public DocumentService(String initialContent) {
            current = new DocumentState(initialContent);
        }

        public void update(String content) {
            if (content == null) {
                throw new IllegalArgumentException(
                    "Document content cannot be null"
                );
            }

            if (content.equals(current.content())) {
                return;
            }

            undoHistory.push(current);
            current = new DocumentState(content);

            // A new state after undo creates a new branch of history.
            redoHistory.clear();
        }

        public boolean undo() {
            if (undoHistory.isEmpty()) {
                return false;
            }

            redoHistory.push(current);
            current = undoHistory.pop();
            return true;
        }

        public boolean redo() {
            if (redoHistory.isEmpty()) {
                return false;
            }

            undoHistory.push(current);
            current = redoHistory.pop();
            return true;
        }

        public String content() {
            return current.content();
        }

        public int undoDepth() {
            return undoHistory.size();
        }

        public int redoDepth() {
            return redoHistory.size();
        }
    }

    // -------------------------------------------------------------------------
    // Demonstration
    // -------------------------------------------------------------------------

    public static void main(String[] args) {
        System.out.println("=== Nested Delimiter Validation ===");

        for (String input : List.of(
            "service([10, 20], {active: true})",
            "service([10, 20}, {active: true})",
            "print(\"items[0]\")"
        )) {
            ValidationResult result = validateBrackets(input);
            System.out.printf(
                "%s -> %s (%s)%n",
                input,
                result.valid() ? "VALID" : "INVALID",
                result.message()
            );
        }

        System.out.println("\n=== Expression Evaluation ===");

        for (String expression : List.of(
            "3 + 4 * 2",
            "(3 + 4) * 2",
            "2 ^ 3 ^ 2",
            "-5 + 3 * 4"
        )) {
            try {
                System.out.printf(
                    "%s = %s%n",
                    expression,
                    evaluate(expression)
                );
            } catch (RuntimeException error) {
                System.out.printf(
                    "%s rejected: %s%n",
                    expression,
                    error.getMessage()
                );
            }
        }

        System.out.println("\n=== Function Call Simulation ===");

        CallStack calls = new CallStack();

        calls.enter(
            "main",
            List.of(),
            Map.of("requestId", "REQ-1001")
        );

        calls.enter(
            "processRequest",
            List.of("REQ-1001"),
            Map.of("authenticated", true)
        );

        calls.enter(
            "evaluateExpression",
            List.of("3 * (4 + 2)"),
            Map.of()
        );

        System.out.println("Active functions: " + calls.activeFunctions());

        ActivationRecord completed = calls.exit();
        System.out.println("Returned from: " + completed.functionName());

        calls.exit();
        calls.exit();

        System.out.println("Call depth: " + calls.depth());

        System.out.println("\n=== Undo / Redo ===");

        DocumentService document =
            new DocumentService("Initial command");

        document.update("Initial command with validation");
        document.update("Initial command with validation and logging");

        System.out.println("Current: " + document.content());

        document.undo();
        System.out.println("Undo: " + document.content());

        document.redo();
        System.out.println("Redo: " + document.content());

        document.undo();
        document.update("New command branch");

        System.out.println("New branch: " + document.content());
        System.out.println(
            "Redo depth after branching: " + document.redoDepth()
        );

        try {
            evaluate("10 / 0");
        } catch (RuntimeException error) {
            System.out.println(
                "Expected evaluation failure: " + error.getMessage()
            );
        }
    }
}
