import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;
import java.util.Objects;

/**
 * Enterprise monitoring example using double-ended queues to calculate
 * sliding-window minimums and maximums.
 *
 * Compile and run:
 *   javac DequeGovernance.java
 *   java DequeGovernance
 */
public class DequeGovernance {

    public record Measurement(long sequence, double value) {
        public Measurement {
            if (!Double.isFinite(value)) {
                throw new IllegalArgumentException(
                    "Measurement must be finite."
                );
            }
        }
    }

    public record WindowResult(
        long firstSequence,
        long lastSequence,
        double minimum,
        double maximum
    ) {}

    public enum MonitorState {
        ACCEPTING,
        CLOSED
    }

    public static final class WindowPolicy {
        private final int windowSize;

        public WindowPolicy(int windowSize) {
            if (windowSize < 1) {
                throw new IllegalArgumentException(
                    "Window size must be positive."
                );
            }
            this.windowSize = windowSize;
        }

        public int windowSize() {
            return windowSize;
        }
    }

    public static final class WindowExtremaService {
        private final WindowPolicy policy;
        private final Deque<Measurement> minima = new ArrayDeque<>();
        private final Deque<Measurement> maxima = new ArrayDeque<>();

        private long nextSequence;
        private MonitorState state = MonitorState.ACCEPTING;

        public WindowExtremaService(WindowPolicy policy) {
            this.policy = Objects.requireNonNull(policy);
        }

        public synchronized WindowResult accept(double value) {
            requireAccepting();

            // Constructing the record validates the value before any state
            // is changed. Invalid input cannot partially modify the queues.
            Measurement measurement = new Measurement(nextSequence, value);
            long sequence = nextSequence;

            while (!minima.isEmpty()
                    && minima.peekFirst().sequence()
                        <= sequence - policy.windowSize()) {
                minima.removeFirst();
            }

            while (!maxima.isEmpty()
                    && maxima.peekFirst().sequence()
                        <= sequence - policy.windowSize()) {
                maxima.removeFirst();
            }

            while (!minima.isEmpty()
                    && minima.peekLast().value() >= value) {
                minima.removeLast();
            }

            while (!maxima.isEmpty()
                    && maxima.peekLast().value() <= value) {
                maxima.removeLast();
            }

            minima.addLast(measurement);
            maxima.addLast(measurement);
            nextSequence++;

            if (nextSequence < policy.windowSize()) {
                return null;
            }

            return new WindowResult(
                sequence - policy.windowSize() + 1,
                sequence,
                minima.peekFirst().value(),
                maxima.peekFirst().value()
            );
        }

        public synchronized void close() {
            state = MonitorState.CLOSED;
            minima.clear();
            maxima.clear();
        }

        public synchronized MonitorState state() {
            return state;
        }

        private void requireAccepting() {
            if (state != MonitorState.ACCEPTING) {
                throw new IllegalStateException(
                    "Measurements cannot be accepted after closure."
                );
            }
        }
    }

    public static final class MonitoringBatch {
        private final WindowExtremaService service;

        public MonitoringBatch(WindowPolicy policy) {
            service = new WindowExtremaService(policy);
        }

        public List<WindowResult> process(List<Double> readings) {
            Objects.requireNonNull(readings, "Readings cannot be null.");

            List<WindowResult> results = new ArrayList<>();

            for (Double reading : readings) {
                if (reading == null) {
                    throw new IllegalArgumentException(
                        "A measurement cannot be null."
                    );
                }

                WindowResult result = service.accept(reading);
                if (result != null) {
                    results.add(result);
                }
            }

            return List.copyOf(results);
        }
    }

    private static List<Double> bruteForceMinimum(
        List<Double> values,
        int windowSize
    ) {
        validateInput(values, windowSize);
        List<Double> result = new ArrayList<>();

        for (int start = 0; start + windowSize <= values.size(); start++) {
            double minimum = Double.POSITIVE_INFINITY;

            for (int offset = start; offset < start + windowSize; offset++) {
                minimum = Math.min(minimum, values.get(offset));
            }

            result.add(minimum);
        }

        return result;
    }

    private static List<Double> bruteForceMaximum(
        List<Double> values,
        int windowSize
    ) {
        validateInput(values, windowSize);
        List<Double> result = new ArrayList<>();

        for (int start = 0; start + windowSize <= values.size(); start++) {
            double maximum = Double.NEGATIVE_INFINITY;

            for (int offset = start; offset < start + windowSize; offset++) {
                maximum = Math.max(maximum, values.get(offset));
            }

            result.add(maximum);
        }

        return result;
    }

    private static void validateInput(List<Double> values, int windowSize) {
        Objects.requireNonNull(values, "Values cannot be null.");

        if (values.isEmpty()
                || windowSize < 1
                || windowSize > values.size()) {
            throw new IllegalArgumentException("Invalid window size.");
        }

        for (Double value : values) {
            if (value == null || !Double.isFinite(value)) {
                throw new IllegalArgumentException(
                    "Values must be non-null and finite."
                );
            }
        }
    }

    private static void runTests() {
        List<List<Double>> cases = List.of(
            List.of(1.0),
            List.of(4.0, 4.0, 4.0, 4.0),
            List.of(-8.0, -3.0, -9.0, -1.0),
            List.of(1.0, 9.0, 2.0, 8.0, 3.0, 7.0)
        );

        int comparisons = 0;

        for (List<Double> values : cases) {
            for (int k = 1; k <= values.size(); k++) {
                MonitoringBatch batch = new MonitoringBatch(
                    new WindowPolicy(k)
                );

                List<WindowResult> actual = batch.process(values);

                List<Double> actualMinimum = actual.stream()
                    .map(WindowResult::minimum)
                    .toList();

                List<Double> actualMaximum = actual.stream()
                    .map(WindowResult::maximum)
                    .toList();

                if (!actualMinimum.equals(bruteForceMinimum(values, k))
                        || !actualMaximum.equals(
                            bruteForceMaximum(values, k))) {
                    throw new AssertionError("Window comparison failed.");
                }

                comparisons++;
            }
        }

        WindowExtremaService closedService =
            new WindowExtremaService(new WindowPolicy(1));
        closedService.close();

        boolean rejected = false;

        try {
            closedService.accept(10.0);
        } catch (IllegalStateException expected) {
            rejected = true;
        }

        if (!rejected) {
            throw new AssertionError("Closed service accepted input.");
        }

        rejected = false;

        try {
            new WindowExtremaService(new WindowPolicy(2)).accept(Double.NaN);
        } catch (IllegalArgumentException expected) {
            rejected = true;
        }

        if (!rejected) {
            throw new AssertionError("Invalid measurement was accepted.");
        }

        System.out.println("Correctness comparisons passed: " + comparisons);
    }

    public static void main(String[] args) {
        List<Double> latencyReadings = List.of(
            18.2, 19.1, 17.4, 20.6, 21.3, 16.8, 18.9
        );

        MonitoringBatch batch = new MonitoringBatch(
            new WindowPolicy(3)
        );

        System.out.println("Enterprise telemetry window results:");

        for (WindowResult result : batch.process(latencyReadings)) {
            System.out.printf(
                "Window [%d, %d]: minimum=%.2f, maximum=%.2f%n",
                result.firstSequence(),
                result.lastSequence(),
                result.minimum(),
                result.maximum()
            );
        }

        System.out.println(
            "\nThe service uses explicit policy, validated measurements, "
            + "immutable result records, and synchronized state changes."
        );

        runTests();
    }
}
