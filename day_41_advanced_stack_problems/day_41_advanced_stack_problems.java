import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Deque;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;

public class AdvancedStackAlgorithms {

    enum Operator {
        ADD("+", 1, false),
        SUBTRACT("-", 1, false),
        MULTIPLY("*", 2, false),
        DIVIDE("/", 2, false),
        MODULO("%", 2, false),
        POWER("^", 3, true);

        private final String symbol;
        private final int precedence;
        private final boolean rightAssociative;

        Operator(String symbol, int precedence, boolean rightAssociative) {
            this.symbol = symbol;
            this.precedence = precedence;
            this.rightAssociative = rightAssociative;
        }

        public String symbol() {
            return symbol;
        }

        public int precedence() {
            return precedence;
        }

        public boolean rightAssociative() {
            return rightAssociative;
        }

        private static final Map<String, Operator> BY_SYMBOL = new HashMap<>();

        static {
            for (Operator operator : values()) {
                BY_SYMBOL.put(operator.symbol, operator);
            }
        }

        static Operator fromSymbol(String symbol) {
            return BY_SYMBOL.get(symbol);
        }
    }

    record RectangleResult(long area, int left, int right, int height) {
    }

    static final class HistogramAnalyzer {

        private HistogramAnalyzer() {
        }

        static RectangleResult largestRectangle(List<Integer> heights) {
            Objects.requireNonNull(heights, "heights");

            for (Integer height : heights) {
                if (height == null || height < 0) {
                    throw new IllegalArgumentException(
                        "Histogram heights must be non-negative."
                    );
                }
            }

            List<Integer> extended = new ArrayList<>(heights);
            extended.add(0);

            Deque<Integer> stack = new ArrayDeque<>();
            RectangleResult best = new RectangleResult(0, -1, -1, 0);

            for (int i = 0; i < extended.size(); i++) {
                while (!stack.isEmpty()
                        && extended.get(stack.peek()) > extended.get(i)) {

                    int top = stack.pop();
                    int left = stack.isEmpty() ? 0 : stack.peek() + 1;
                    int right = i - 1;
                    long width = right - left + 1L;
                    long area = width * extended.get(top);

                    if (area > best.area()) {
                        best = new RectangleResult(
                            area,
                            left,
                            right,
                            extended.get(top)
                        );
                    }
                }

                stack.push(i);
            }

            return best;
        }
    }

    static final class RainwaterAnalyzer {

        private RainwaterAnalyzer() {
        }

        static long trappedWater(List<Integer> heights) {
            validateHeights(heights);

            int left = 0;
            int right = heights.size() - 1;
            int leftMax = 0;
            int rightMax = 0;
            long water = 0;

            while (left < right) {
                if (heights.get(left) <= heights.get(right)) {
                    leftMax = Math.max(leftMax, heights.get(left));
                    water += leftMax - heights.get(left);
                    left++;
                } else {
                    rightMax = Math.max(rightMax, heights.get(right));
                    water += rightMax - heights.get(right);
                    right--;
                }
            }

            return water;
        }

        private static void validateHeights(List<Integer> heights) {
            Objects.requireNonNull(heights, "heights");

            if (heights.stream().anyMatch(
                value -> value == null || value < 0
            )) {
                throw new IllegalArgumentException(
                    "Elevation values must be non-negative."
                );
            }
        }
    }

    static final class StockAnalytics {

        private StockAnalytics() {
        }

        static List<Integer> stockSpan(List<Double> prices) {
            Objects.requireNonNull(prices, "prices");

            Deque<Integer> stack = new ArrayDeque<>();
            List<Integer> result = new ArrayList<>(
                Collections.nCopies(prices.size(), 0)
            );

            for (int day = 0; day < prices.size(); day++) {
                double price = prices.get(day);

                if (!Double.isFinite(price) || price < 0) {
                    throw new IllegalArgumentException(
                        "Prices must be finite and non-negative."
                    );
                }

                while (!stack.isEmpty()
                        && prices.get(stack.peek()) <= price) {
                    stack.pop();
                }

                result.set(
                    day,
                    stack.isEmpty()
                        ? day + 1
                        : day - stack.peek()
                );

                stack.push(day);
            }

            return result;
        }
    }

    static final class ExpressionEngine {

        private ExpressionEngine() {
        }

        static String toPostfix(String expression) {
            if (expression == null || expression.isBlank()) {
                throw new IllegalArgumentException(
                    "Expression cannot be blank."
                );
            }

            String[] tokens = expression
                .replace("(", " ( ")
                .replace(")", " ) ")
                .trim()
                .split("\\s+");

            Deque<String> operators = new ArrayDeque<>();
            List<String> output = new ArrayList<>();

            for (String token : tokens) {
                if (isOperand(token)) {
                    output.add(token);
                    continue;
                }

                if (token.equals("(")) {
                    operators.push(token);
                    continue;
                }

                if (token.equals(")")) {
                    while (!operators.isEmpty()
                            && !operators.peek().equals("(")) {
                        output.add(operators.pop());
                    }

                    if (operators.isEmpty()) {
                        throw new IllegalArgumentException(
                            "Mismatched parentheses."
                        );
                    }

                    operators.pop();
                    continue;
                }

                Operator current = Operator.fromSymbol(token);

                if (current == null) {
                    throw new IllegalArgumentException(
                        "Unsupported expression token: " + token
                    );
                }

                while (!operators.isEmpty()
                        && !operators.peek().equals("(")) {

                    Operator top = Operator.fromSymbol(operators.peek());

                    boolean pop =
                        top.precedence() > current.precedence()
                        || (
                            top.precedence() == current.precedence()
                            && !current.rightAssociative()
                        );

                    if (!pop) {
                        break;
                    }

                    output.add(operators.pop());
                }

                operators.push(token);
            }

            while (!operators.isEmpty()) {
                if (operators.peek().equals("(")) {
                    throw new IllegalArgumentException(
                        "Mismatched parentheses."
                    );
                }

                output.add(operators.pop());
            }

            return String.join(" ", output);
        }

        static double evaluatePostfix(
            String postfix,
            Map<String, Double> variables
        ) {
            Objects.requireNonNull(postfix, "postfix");
            Objects.requireNonNull(variables, "variables");

            Deque<Double> values = new ArrayDeque<>();

            for (String token : postfix.split("\\s+")) {
                Operator operator = Operator.fromSymbol(token);

                if (operator == null) {
                    Double value;

                    try {
                        value = Double.parseDouble(token);
                    } catch (NumberFormatException exception) {
                        value = variables.get(token);
                    }

                    if (value == null || !Double.isFinite(value)) {
                        throw new IllegalArgumentException(
                            "Unknown or invalid operand: " + token
                        );
                    }

                    values.push(value);
                    continue;
                }

                if (values.size() < 2) {
                    throw new IllegalArgumentException(
                        "Invalid postfix expression."
                    );
                }

                double right = values.pop();
                double left = values.pop();

                double result;

                switch (operator) {
                    case ADD -> result = left + right;
                    case SUBTRACT -> result = left - right;
                    case MULTIPLY -> result = left * right;
                    case DIVIDE -> {
                        if (right == 0.0) {
                            throw new ArithmeticException(
                                "Division by zero."
                            );
                        }
                        result = left / right;
                    }
                    case MODULO -> result = left % right;
                    case POWER -> result = Math.pow(left, right);
                    default -> throw new IllegalStateException(
                        "Unhandled operator."
                    );
                }

                values.push(result);
            }

            if (values.size() != 1) {
                throw new IllegalArgumentException(
                    "Invalid postfix expression."
                );
            }

            return values.pop();
        }

        private static boolean isOperand(String token) {
            return token.matches(
                "[A-Za-z_][A-Za-z0-9_]*|\\d+(\\.\\d+)?"
            );
        }
    }

    interface MergeMetric {
        long calculate(List<Integer> values);
    }

    static final class RepositoryPerformanceModel {
        private final EnumMap<MetricType, MergeMetric> metrics =
            new EnumMap<>(MetricType.class);

        void register(MetricType type, MergeMetric metric) {
            metrics.put(
                Objects.requireNonNull(type),
                Objects.requireNonNull(metric)
            );
        }

        long evaluate(MetricType type, List<Integer> values) {
            MergeMetric metric = metrics.get(type);

            if (metric == null) {
                throw new IllegalStateException(
                    "No metric registered for " + type
                );
            }

            return metric.calculate(values);
        }
    }

    enum MetricType {
        LARGEST_SUSTAINED_LOAD,
        TRAPPED_CAPACITY
    }

    static final class BinaryMatrixAnalyzer {

        static int maximalRectangle(int[][] matrix) {
            if (matrix == null || matrix.length == 0) {
                return 0;
            }

            int width = matrix[0].length;
            int[] heights = new int[width];
            int best = 0;

            for (int[] row : matrix) {
                if (row.length != width) {
                    throw new IllegalArgumentException(
                        "Matrix must be rectangular."
                    );
                }

                for (int column = 0; column < width; column++) {
                    if (row[column] != 0 && row[column] != 1) {
                        throw new IllegalArgumentException(
                            "Matrix values must be zero or one."
                        );
                    }

                    heights[column] =
                        row[column] == 1
                            ? heights[column] + 1
                            : 0;
                }

                List<Integer> currentHeights =
                    Arrays.stream(heights).boxed().toList();

                best = Math.max(
                    best,
                    (int) HistogramAnalyzer
                        .largestRectangle(currentHeights)
                        .area()
                );
            }

            return best;
        }
    }

    public static void main(String[] args) {
        System.out.println("=== Enterprise Operations Analytics ===");

        List<Integer> workload = List.of(2, 1, 5, 6, 2, 3);
        RectangleResult rectangle =
            HistogramAnalyzer.largestRectangle(workload);

        System.out.println(
            "Sustained workload area: " + rectangle.area()
        );
        System.out.println(
            "Window: " + rectangle.left()
                + " to " + rectangle.right()
        );

        List<Integer> elevation =
            List.of(4, 2, 0, 3, 2, 5);

        System.out.println(
            "Trapped capacity: "
                + RainwaterAnalyzer.trappedWater(elevation)
        );

        List<Double> prices =
            List.of(100.0, 80.0, 60.0, 70.0, 60.0, 75.0, 85.0);

        System.out.println(
            "Stock spans: "
                + StockAnalytics.stockSpan(prices)
        );

        String expression =
            "3 + 4 * 2 / ( 1 - 5 ) ^ 2";

        String postfix =
            ExpressionEngine.toPostfix(expression);

        System.out.println("Postfix: " + postfix);
        System.out.println(
            "Expression value: "
                + ExpressionEngine.evaluatePostfix(
                    postfix,
                    Map.of()
                )
        );

        String businessExpression =
            "revenue - cost * tax";

        String businessPostfix =
            ExpressionEngine.toPostfix(businessExpression);

        Map<String, Double> variables = Map.of(
            "revenue", 1000.0,
            "cost", 400.0,
            "tax", 0.20
        );

        System.out.println(
            "Business expression value: "
                + ExpressionEngine.evaluatePostfix(
                    businessPostfix,
                    variables
                )
        );

        System.out.println(
            "Maximal binary rectangle: "
                + BinaryMatrixAnalyzer.maximalRectangle(
                    new int[][] {
                        {1, 0, 1, 0, 0},
                        {1, 0, 1, 1, 1},
                        {1, 1, 1, 1, 1},
                        {1, 0, 0, 1, 0}
                    }
                )
        );

        RepositoryPerformanceModel model =
            new RepositoryPerformanceModel();

        model.register(
            MetricType.LARGEST_SUSTAINED_LOAD,
            values -> HistogramAnalyzer
                .largestRectangle(values)
                .area()
        );

        model.register(
            MetricType.TRAPPED_CAPACITY,
            RainwaterAnalyzer::trappedWater
        );

        System.out.println(
            "Registered sustained-load metric: "
                + model.evaluate(
                    MetricType.LARGEST_SUSTAINED_LOAD,
                    workload
                )
        );

        System.out.println(
            "Registered capacity metric: "
                + model.evaluate(
                    MetricType.TRAPPED_CAPACITY,
                    elevation
                )
        );

        try {
            ExpressionEngine.evaluatePostfix("10 0 /", Map.of());
        } catch (RuntimeException exception) {
            System.out.println(
                "Expected expression failure: "
                    + exception.getMessage()
            );
        }

        try {
            HistogramAnalyzer.largestRectangle(
                List.of(2, -1, 3)
            );
        } catch (RuntimeException exception) {
            System.out.println(
                "Expected histogram validation failure: "
                    + exception.getMessage()
            );
        }
    }
}
