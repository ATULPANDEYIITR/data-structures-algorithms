import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;

/**
 * Enterprise sorting service for telemetry and event-processing workloads.
 *
 * Java 17 or later. No third-party dependencies.
 */
public class Main {

    private static final int MAX_INPUT_SIZE = 1_000_000;

    enum Algorithm {
        AUTO,
        COUNTING,
        RADIX,
        BUCKET,
        COMPARISON
    }

    enum JobState {
        QUEUED,
        RUNNING,
        COMPLETED,
        FAILED
    }

    static final class SortingException extends RuntimeException {
        SortingException(String message) {
            super(message);
        }

        SortingException(String message, Throwable cause) {
            super(message, cause);
        }
    }

    /**
     * A request contains exactly one data representation.
     * Integer requests use long values; decimal requests use double values.
     */
    record SortRequest(
        String jobId,
        Algorithm requestedAlgorithm,
        List<Long> integerValues,
        List<Double> decimalValues
    ) {
        SortRequest {
            Objects.requireNonNull(jobId, "jobId");
            Objects.requireNonNull(
                requestedAlgorithm,
                "requestedAlgorithm"
            );
            Objects.requireNonNull(integerValues, "integerValues");
            Objects.requireNonNull(decimalValues, "decimalValues");

            if (jobId.isBlank()) {
                throw new SortingException("Job ID cannot be blank.");
            }

            if (integerValues.size() > MAX_INPUT_SIZE ||
                decimalValues.size() > MAX_INPUT_SIZE) {
                throw new SortingException("Input exceeds the size limit.");
            }

            if (!integerValues.isEmpty() && !decimalValues.isEmpty()) {
                throw new SortingException(
                    "A job cannot contain both integer and decimal datasets."
                );
            }

            if (integerValues.isEmpty() && decimalValues.isEmpty()) {
                // An empty integer dataset is a valid sorting workload.
                integerValues = List.of();
            } else if (!integerValues.isEmpty()) {
                integerValues = List.copyOf(integerValues);
            } else {
                decimalValues = List.copyOf(decimalValues);
            }

            if (integerValues.stream().anyMatch(Objects::isNull) ||
                decimalValues.stream().anyMatch(Objects::isNull)) {
                throw new SortingException("Null values are not allowed.");
            }

            for (double value : decimalValues) {
                if (!Double.isFinite(value)) {
                    throw new SortingException(
                        "Decimal datasets cannot contain NaN or infinity."
                    );
                }
            }
        }

        static SortRequest integers(
            String jobId,
            Algorithm algorithm,
            List<Long> values
        ) {
            return new SortRequest(jobId, algorithm, values, List.of());
        }

        static SortRequest decimals(
            String jobId,
            Algorithm algorithm,
            List<Double> values
        ) {
            return new SortRequest(jobId, algorithm, List.of(), values);
        }

        boolean isIntegerWorkload() {
            return decimalValues.isEmpty();
        }
    }

    record SortResult(
        String jobId,
        Algorithm selectedAlgorithm,
        List<Long> sortedIntegers,
        List<Double> sortedDecimals,
        long elapsedNanos
    ) {
        SortResult {
            sortedIntegers = List.copyOf(sortedIntegers);
            sortedDecimals = List.copyOf(sortedDecimals);
        }

        double elapsedMilliseconds() {
            return elapsedNanos / 1_000_000.0;
        }
    }

    record JobSnapshot(
        String jobId,
        JobState state,
        Algorithm requestedAlgorithm
    ) {}

    /**
     * Keeps allocation policy separate from the sorting implementations.
     */
    static final class SortingPolicy {
        private final long maximumCountingRange;
        private final long countingRangeRatio;

        SortingPolicy(long maximumCountingRange, long countingRangeRatio) {
            if (maximumCountingRange < 1 || countingRangeRatio < 1) {
                throw new SortingException("Invalid sorting policy limits.");
            }

            this.maximumCountingRange = maximumCountingRange;
            this.countingRangeRatio = countingRangeRatio;
        }

        Algorithm select(SortRequest request) {
            if (request.requestedAlgorithm() != Algorithm.AUTO) {
                validateCompatibility(
                    request,
                    request.requestedAlgorithm()
                );
                return request.requestedAlgorithm();
            }

            if (!request.isIntegerWorkload()) {
                return Algorithm.BUCKET;
            }

            List<Long> values = request.integerValues();

            if (values.size() < 2) {
                return Algorithm.COUNTING;
            }

            long minimum = Collections.min(values);
            long maximum = Collections.max(values);

            // BigInteger avoids overflow for Long.MIN_VALUE and Long.MAX_VALUE.
            java.math.BigInteger span =
                java.math.BigInteger.valueOf(maximum)
                    .subtract(java.math.BigInteger.valueOf(minimum))
                    .add(java.math.BigInteger.ONE);

            long relativeLimit = Math.max(
                256L,
                (long) values.size() * countingRangeRatio
            );

            if (
                span.compareTo(
                    java.math.BigInteger.valueOf(maximumCountingRange)
                ) <= 0 &&
                span.compareTo(
                    java.math.BigInteger.valueOf(relativeLimit)
                ) <= 0
            ) {
                return Algorithm.COUNTING;
            }

            return Algorithm.RADIX;
        }

        private void validateCompatibility(
            SortRequest request,
            Algorithm algorithm
        ) {
            if (algorithm == Algorithm.AUTO) {
                throw new SortingException(
                    "AUTO must be resolved before execution."
                );
            }

            if (request.isIntegerWorkload() &&
                algorithm == Algorithm.BUCKET) {
                throw new SortingException(
                    "Bucket sorting is reserved for decimal workloads."
                );
            }

            if (!request.isIntegerWorkload() &&
                algorithm != Algorithm.BUCKET &&
                algorithm != Algorithm.COMPARISON) {
                throw new SortingException(
                    "Counting and radix sorting require integer workloads."
                );
            }
        }

        long maximumCountingRange() {
            return maximumCountingRange;
        }
    }

    /**
     * Integer sorting implementations use primitive arrays to avoid the
     * allocation overhead of boxed values during the sorting passes.
     */
    static final class IntegerSorters {

        private IntegerSorters() {}

        static long[] countingSort(long[] input, long maximumRange) {
            if (input.length < 2) {
                return input.clone();
            }

            long minimum = input[0];
            long maximum = input[0];

            for (long value : input) {
                minimum = Math.min(minimum, value);
                maximum = Math.max(maximum, value);
            }

            java.math.BigInteger span =
                java.math.BigInteger.valueOf(maximum)
                    .subtract(java.math.BigInteger.valueOf(minimum))
                    .add(java.math.BigInteger.ONE);

            if (span.compareTo(
                java.math.BigInteger.valueOf(maximumRange)
            ) > 0) {
                throw new SortingException(
                    "Counting sort range exceeds the memory policy."
                );
            }

            int range = span.intValueExact();
            long[] counts = new long[range];

            for (long value : input) {
                int offset = Math.toIntExact(value - minimum);
                counts[offset]++;
            }

            long[] output = new long[input.length];
            int destination = 0;

            for (int offset = 0; offset < range; offset++) {
                long frequency = counts[offset];

                for (long occurrence = 0; occurrence < frequency; occurrence++) {
                    output[destination++] = minimum + offset;
                }
            }

            return output;
        }

        static long[] radixSort(long[] input) {
            if (input.length < 2) {
                return input.clone();
            }

            long[] output = input.clone();
            long[] temporary = new long[input.length];

            /*
             * XOR with Long.MIN_VALUE converts signed ordering into
             * unsigned key ordering. Eight passes cover the complete long.
             */
            for (int pass = 0; pass < Long.BYTES; pass++) {
                int[] counts = new int[256];
                int shift = pass * Byte.SIZE;

                for (long value : output) {
                    long key = value ^ Long.MIN_VALUE;
                    int digit = (int) ((key >>> shift) & 0xFFL);
                    counts[digit]++;
                }

                int total = 0;

                for (int digit = 0; digit < counts.length; digit++) {
                    total += counts[digit];
                    counts[digit] = total;
                }

                for (int index = output.length - 1; index >= 0; index--) {
                    long value = output[index];
                    long key = value ^ Long.MIN_VALUE;
                    int digit = (int) ((key >>> shift) & 0xFFL);
                    int destination = --counts[digit];

                    temporary[destination] = value;
                }

                long[] swap = output;
                output = temporary;
                temporary = swap;
            }

            return output;
        }

        static long[] comparisonSort(long[] input) {
            long[] output = input.clone();
            Arrays.sort(output);
            return output;
        }
    }

    /**
     * Decimal bucket sorting normalizes extreme finite values before
     * calculating their bucket positions.
     */
    static final class DecimalSorters {

        private DecimalSorters() {}

        static double[] bucketSort(double[] input) {
            if (input.length < 2) {
                return input.clone();
            }

            double minimum = input[0];
            double maximum = input[0];

            for (double value : input) {
                if (!Double.isFinite(value)) {
                    throw new SortingException(
                        "Bucket sorting requires finite values."
                    );
                }

                minimum = Math.min(minimum, value);
                maximum = Math.max(maximum, value);
            }

            if (minimum == maximum) {
                return input.clone();
            }

            int bucketCount = Math.max(
                1,
                Math.min(10_000, (int) Math.ceil(Math.sqrt(input.length)))
            );

            /*
             * Scaling prevents overflow when maximum - minimum exceeds
             * Double.MAX_VALUE.
             */
            double scale = Math.max(
                1.0,
                Math.max(Math.abs(minimum), Math.abs(maximum))
            );

            double scaledMinimum = minimum / scale;
            double scaledMaximum = maximum / scale;
            double scaledRange = scaledMaximum - scaledMinimum;

            List<List<Double>> buckets = new ArrayList<>(bucketCount);

            for (int index = 0; index < bucketCount; index++) {
                buckets.add(new ArrayList<>());
            }

            for (double value : input) {
                double normalized = (
                    (value / scale - scaledMinimum) / scaledRange
                );

                int bucketIndex = (int) Math.floor(
                    normalized * bucketCount
                );

                bucketIndex = Math.max(
                    0,
                    Math.min(bucketCount - 1, bucketIndex)
                );

                buckets.get(bucketIndex).add(value);
            }

            double[] output = new double[input.length];
            int destination = 0;

            for (List<Double> bucket : buckets) {
                // Double.compare gives explicit handling of signed zero.
                bucket.sort(Double::compare);

                for (double value : bucket) {
                    output[destination++] = value;
                }
            }

            return output;
        }

        static double[] comparisonSort(double[] input) {
            double[] output = input.clone();
            Arrays.sort(output);
            return output;
        }
    }

    static final class JobRecord {
        private final SortRequest request;
        private final AtomicReference<JobState> state =
            new AtomicReference<>(JobState.QUEUED);
        private final CompletableFuture<SortResult> result =
            new CompletableFuture<>();

        JobRecord(SortRequest request) {
            this.request = request;
        }

        void transition(JobState expected, JobState next) {
            if (!state.compareAndSet(expected, next)) {
                throw new SortingException(
                    "Invalid job transition: " +
                    state.get() + " to " + next
                );
            }
        }

        JobSnapshot snapshot() {
            return new JobSnapshot(
                request.jobId(),
                state.get(),
                request.requestedAlgorithm()
            );
        }
    }

    /**
     * A bounded executor protects the service from unbounded queue growth.
     * Job IDs are unique, and state transitions are atomic.
     */
    static final class RepositorySortingService implements AutoCloseable {
        private final SortingPolicy policy;
        private final ThreadPoolExecutor executor;
        private final ConcurrentHashMap<String, JobRecord> jobs =
            new ConcurrentHashMap<>();

        RepositorySortingService(SortingPolicy policy) {
            this.policy = Objects.requireNonNull(policy);

            this.executor = new ThreadPoolExecutor(
                2,
                2,
                0L,
                TimeUnit.MILLISECONDS,
                new ArrayBlockingQueue<>(16),
                runnable -> {
                    Thread thread = new Thread(runnable);
                    thread.setName("repository-sort-worker");
                    thread.setDaemon(false);
                    return thread;
                },
                new ThreadPoolExecutor.AbortPolicy()
            );
        }

        CompletableFuture<SortResult> submit(SortRequest request) {
            Objects.requireNonNull(request);

            JobRecord record = new JobRecord(request);

            JobRecord existing = jobs.putIfAbsent(
                request.jobId(),
                record
            );

            if (existing != null) {
                throw new SortingException(
                    "Duplicate job ID: " + request.jobId()
                );
            }

            try {
                executor.execute(() -> process(record));
            } catch (java.util.concurrent.RejectedExecutionException error) {
                record.transition(JobState.QUEUED, JobState.FAILED);
                record.result.completeExceptionally(
                    new SortingException(
                        "Sorting service is at capacity.",
                        error
                    )
                );
            }

            return record.result;
        }

        private void process(JobRecord record) {
            try {
                record.transition(JobState.QUEUED, JobState.RUNNING);

                SortRequest request = record.request;
                Algorithm selected = policy.select(request);

                long started = System.nanoTime();

                SortResult result;

                if (request.isIntegerWorkload()) {
                    long[] input = request.integerValues()
                        .stream()
                        .mapToLong(Long::longValue)
                        .toArray();

                    long[] sorted = switch (selected) {
                        case COUNTING -> IntegerSorters.countingSort(
                            input,
                            policy.maximumCountingRange()
                        );
                        case RADIX -> IntegerSorters.radixSort(input);
                        case COMPARISON -> IntegerSorters.comparisonSort(input);
                        default -> throw new SortingException(
                            "Unsupported integer algorithm: " + selected
                        );
                    };

                    verifyIntegerResult(input, sorted);

                    List<Long> output = Arrays.stream(sorted)
                        .boxed()
                        .toList();

                    result = new SortResult(
                        request.jobId(),
                        selected,
                        output,
                        List.of(),
                        System.nanoTime() - started
                    );
                } else {
                    double[] input = request.decimalValues()
                        .stream()
                        .mapToDouble(Double::doubleValue)
                        .toArray();

                    double[] sorted = selected == Algorithm.BUCKET
                        ? DecimalSorters.bucketSort(input)
                        : DecimalSorters.comparisonSort(input);

                    verifyDecimalResult(input, sorted);

                    List<Double> output = Arrays.stream(sorted)
                        .boxed()
                        .toList();

                    result = new SortResult(
                        request.jobId(),
                        selected,
                        List.of(),
                        output,
                        System.nanoTime() - started
                    );
                }

                record.transition(JobState.RUNNING, JobState.COMPLETED);
                record.result.complete(result);
            } catch (Throwable error) {
                record.state.compareAndSet(
                    JobState.RUNNING,
                    JobState.FAILED
                );

                record.state.compareAndSet(
                    JobState.QUEUED,
                    JobState.FAILED
                );

                record.result.completeExceptionally(error);
            }
        }

        private void verifyIntegerResult(long[] original, long[] sorted) {
            if (sorted.length != original.length) {
                throw new SortingException("Integer result size mismatch.");
            }

            long[] expected = original.clone();
            Arrays.sort(expected);

            if (!Arrays.equals(expected, sorted)) {
                throw new SortingException(
                    "Integer result failed correctness verification."
                );
            }
        }

        private void verifyDecimalResult(
            double[] original,
            double[] sorted
        ) {
            if (sorted.length != original.length) {
                throw new SortingException("Decimal result size mismatch.");
            }

            double[] expected = original.clone();
            Arrays.sort(expected);

            if (!Arrays.equals(expected, sorted)) {
                throw new SortingException(
                    "Decimal result failed correctness verification."
                );
            }
        }

        JobSnapshot getJob(String jobId) {
            JobRecord record = jobs.get(jobId);
            return record == null ? null : record.snapshot();
        }

        Map<String, JobSnapshot> snapshots() {
            Map<String, JobSnapshot> result = new ConcurrentHashMap<>();

            jobs.forEach((id, record) -> {
                result.put(id, record.snapshot());
            });

            return Map.copyOf(result);
        }

        @Override
        public void close() {
            executor.shutdown();

            try {
                if (!executor.awaitTermination(10, TimeUnit.SECONDS)) {
                    executor.shutdownNow();

                    if (!executor.awaitTermination(5, TimeUnit.SECONDS)) {
                        throw new SortingException(
                            "Sorting executor did not terminate."
                        );
                    }
                }
            } catch (InterruptedException error) {
                executor.shutdownNow();
                Thread.currentThread().interrupt();

                throw new SortingException(
                    "Interrupted while stopping sorting workers.",
                    error
                );
            }
        }
    }

    private static void printResult(SortResult result) {
        System.out.println("\nJob: " + result.jobId());
        System.out.println("Algorithm: " + result.selectedAlgorithm());
        System.out.println("Elapsed: " +
            String.format("%.3f", result.elapsedMilliseconds()) + " ms");

        if (!result.sortedIntegers().isEmpty()) {
            System.out.println("Sorted integers: " + result.sortedIntegers());
        } else {
            System.out.println("Sorted decimals: " + result.sortedDecimals());
        }
    }

    public static void main(String[] args) {
        SortingPolicy policy = new SortingPolicy(
            1_000_000,
            16
        );

        try (RepositorySortingService service =
                 new RepositorySortingService(policy)) {

            SortRequest boundedTelemetry = SortRequest.integers(
                "telemetry-status-001",
                Algorithm.AUTO,
                List.of(4L, -2L, 7L, 4L, 0L, -2L, 3L, 1L)
            );

            SortRequest largeIdentifiers = SortRequest.integers(
                "event-identifiers-002",
                Algorithm.AUTO,
                List.of(
                    Long.MAX_VALUE,
                    0L,
                    Long.MIN_VALUE,
                    42L,
                    -1L,
                    9_000_000_000L
                )
            );

            SortRequest decimalMeasurements = SortRequest.decimals(
                "latency-measurements-003",
                Algorithm.AUTO,
                List.of(0.42, 0.32, 0.23, 0.52, 0.25, 0.47, 0.51)
            );

            List<CompletableFuture<SortResult>> submitted = List.of(
                service.submit(boundedTelemetry),
                service.submit(largeIdentifiers),
                service.submit(decimalMeasurements)
            );

            for (CompletableFuture<SortResult> future : submitted) {
                printResult(future.join());
            }

            System.out.println("\nJOB STATES");

            service.snapshots().forEach((id, snapshot) ->
                System.out.println(id + " -> " + snapshot.state())
            );

            System.out.println("\nVALIDATION CASES");

            try {
                service.submit(
                    SortRequest.integers(
                        "duplicate-id",
                        Algorithm.AUTO,
                        List.of(1L, 2L)
                    )
                );
                service.submit(
                    SortRequest.integers(
                        "duplicate-id",
                        Algorithm.AUTO,
                        List.of(3L, 4L)
                    )
                );
            } catch (SortingException error) {
                System.out.println("Rejected: " + error.getMessage());
            }

            try {
                SortRequest.decimals(
                    "invalid-decimals",
                    Algorithm.BUCKET,
                    List.of(1.0, Double.NaN)
                );
            } catch (SortingException error) {
                System.out.println("Rejected: " + error.getMessage());
            }
        }
    }
}
