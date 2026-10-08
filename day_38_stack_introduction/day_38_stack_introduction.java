import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

public class StackIntroduction {

    enum OperationType {
        CREATE,
        VALIDATE,
        SAVE,
        PUBLISH,
        RETRY
    }

    record WorkflowCommand(long id, OperationType type, String resource) {
        WorkflowCommand {
            if (id <= 0) {
                throw new IllegalArgumentException("command id must be positive");
            }
            Objects.requireNonNull(type, "operation type is required");
            if (resource == null || resource.isBlank()) {
                throw new IllegalArgumentException("resource cannot be blank");
            }
        }
    }

    static final class StackService<T> {
        private final Deque<T> stack = new ArrayDeque<>();
        private final int capacity;

        StackService(int capacity) {
            if (capacity <= 0) {
                throw new IllegalArgumentException("capacity must be positive");
            }
            this.capacity = capacity;
        }

        void push(T value) {
            Objects.requireNonNull(value, "stack values cannot be null");

            if (stack.size() >= capacity) {
                throw new IllegalStateException("stack capacity exceeded");
            }

            stack.push(value);
        }

        T pop() {
            if (stack.isEmpty()) {
                throw new IllegalStateException("cannot pop from empty stack");
            }
            return stack.pop();
        }

        T peek() {
            if (stack.isEmpty()) {
                throw new IllegalStateException("cannot peek at empty stack");
            }
            return stack.peek();
        }

        boolean isEmpty() {
            return stack.isEmpty();
        }

        int size() {
            return stack.size();
        }

        List<T> topToBottom() {
            return List.copyOf(stack);
        }
    }

    static final class WorkflowProcessor {
        private final StackService<WorkflowCommand> pending;
        private final List<WorkflowCommand> processed = new ArrayList<>();
        private final Map<OperationType, Integer> operationCounts =
                new EnumMap<>(OperationType.class);

        WorkflowProcessor(int capacity) {
            pending = new StackService<>(capacity);

            for (OperationType type : OperationType.values()) {
                operationCounts.put(type, 0);
            }
        }

        void submit(WorkflowCommand command) {
            pending.push(command);
        }

        Optional<WorkflowCommand> processLatest() {
            if (pending.isEmpty()) {
                return Optional.empty();
            }

            WorkflowCommand command = pending.pop();
            processed.add(command);
            operationCounts.merge(command.type(), 1, Integer::sum);
            return Optional.of(command);
        }

        List<WorkflowCommand> pendingCommands() {
            return pending.topToBottom();
        }

        Map<OperationType, Integer> statistics() {
            return Map.copyOf(operationCounts);
        }
    }

    static boolean isBalanced(String expression) {
        Map<Character, Character> matching = Map.of(
                ')', '(',
                ']', '[',
                '}', '{'
        );

        Deque<Character> stack = new ArrayDeque<>();

        for (char character : expression.toCharArray()) {
            if (character == '(' || character == '[' || character == '{') {
                stack.push(character);
            } else if (matching.containsKey(character)) {
                if (stack.isEmpty() || stack.pop() != matching.get(character)) {
                    return false;
                }
            }
        }

        return stack.isEmpty();
    }

    static String reverse(String text) {
        Deque<Character> stack = new ArrayDeque<>();

        for (char character : text.toCharArray()) {
            stack.push(character);
        }

        StringBuilder reversed = new StringBuilder(text.length());

        while (!stack.isEmpty()) {
            reversed.append(stack.pop());
        }

        return reversed.toString();
    }

    static double evaluatePostfix(String expression) {
        Deque<Double> stack = new ArrayDeque<>();

        for (String token : expression.trim().split("\\s+")) {
            try {
                stack.push(Double.parseDouble(token));
                continue;
            } catch (NumberFormatException ignored) {
                // Non-numeric tokens are treated as operators below.
            }

            if (!List.of("+", "-", "*", "/").contains(token)) {
                throw new IllegalArgumentException("unsupported token: " + token);
            }

            if (stack.size() < 2) {
                throw new IllegalArgumentException("operator requires two operands");
            }

            double right = stack.pop();
            double left = stack.pop();

            if (token.equals("/") && right == 0.0) {
                throw new ArithmeticException("division by zero");
            }

            double result = switch (token) {
                case "+" -> left + right;
                case "-" -> left - right;
                case "*" -> left * right;
                case "/" -> left / right;
                default -> throw new IllegalStateException("unexpected operator");
            };

            stack.push(result);
        }

        if (stack.size() != 1) {
            throw new IllegalArgumentException("malformed postfix expression");
        }

        return stack.pop();
    }

    static void demonstrateWorkflow() {
        System.out.println("=== Enterprise workflow using LIFO ===");

        WorkflowProcessor processor = new WorkflowProcessor(10);

        processor.submit(new WorkflowCommand(1001, OperationType.CREATE, "invoice"));
        processor.submit(new WorkflowCommand(1002, OperationType.VALIDATE, "invoice"));
        processor.submit(new WorkflowCommand(1003, OperationType.SAVE, "invoice"));
        processor.submit(new WorkflowCommand(1004, OperationType.RETRY, "invoice"));

        while (!processor.pendingCommands().isEmpty()) {
            WorkflowCommand command = processor.processLatest().orElseThrow();
            System.out.printf(
                    "Processing command %d: %s %s%n",
                    command.id(),
                    command.type(),
                    command.resource()
            );
        }

        System.out.println("Operation statistics: " + processor.statistics());
    }

    static void demonstrateValidation() {
        System.out.println("\n=== Delimiter validation ===");

        List<String> expressions = List.of(
                "{[()]}",
                "([)]",
                "invoice[customer]",
                "((invoice)"
        );

        for (String expression : expressions) {
            System.out.printf("%s -> %s%n", expression, isBalanced(expression));
        }
    }

    static void demonstratePostfix() {
        System.out.println("\n=== Postfix evaluation ===");

        for (String expression : List.of(
                "5 2 + 3 *",
                "20 5 / 2 +",
                "9 4 - 2 *"
        )) {
            System.out.printf("%s = %.2f%n", expression, evaluatePostfix(expression));
        }

        try {
            evaluatePostfix("8 0 /");
        } catch (ArithmeticException exception) {
            System.out.println("Expected arithmetic failure: " + exception.getMessage());
        }
    }

    static void demonstrateCapacityAndUnderflow() {
        System.out.println("\n=== Stack policy enforcement ===");

        StackService<String> stack = new StackService<>(2);

        stack.push("database");
        stack.push("application");

        System.out.println("Top: " + stack.peek());

        try {
            stack.push("presentation");
        } catch (IllegalStateException exception) {
            System.out.println("Expected overflow: " + exception.getMessage());
        }

        System.out.println("Pop: " + stack.pop());
        System.out.println("Pop: " + stack.pop());

        try {
            stack.pop();
        } catch (IllegalStateException exception) {
            System.out.println("Expected underflow: " + exception.getMessage());
        }
    }

    public static void main(String[] args) {
        demonstrateWorkflow();
        demonstrateValidation();

        System.out.println("\n=== Reverse operation ===");
        System.out.println("STACK -> " + reverse("STACK"));

        demonstratePostfix();
        demonstrateCapacityAndUnderflow();

        System.out.println("\n=== Complexity ===");
        System.out.println("ArrayDeque push/pop/peek: O(1) amortized / O(1) / O(1)");
        System.out.println("Workflow processing of n commands: O(n) time");
        System.out.println("Delimiter validation: O(n) time and O(n) auxiliary space");
        System.out.println("Postfix evaluation: O(n) time and O(n) auxiliary space");
        System.out.println("ArrayDeque avoids the per-node allocation cost of a linked-list stack.");
    }
}
