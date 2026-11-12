import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.PriorityQueue;
import java.util.concurrent.atomic.AtomicLong;
import java.util.stream.Collectors;

public class HeapProblems {

    public static class HeapException extends RuntimeException {
        public HeapException(String message) {
            super(message);
        }
    }

    public static class InvalidInputException extends HeapException {
        public InvalidInputException(String message) {
            super(message);
        }
    }

    public static class EmptyHeapException extends HeapException {
        public EmptyHeapException(String message) {
            super(message);
        }
    }

    /*
     * Generic heap implementation.
     * The comparator determines which element has highest priority.
     */
    public static final class BinaryHeap<T> {
        private final List<T> data = new ArrayList<>();
        private final Comparator<? super T> comparator;

        public BinaryHeap(Comparator<? super T> comparator) {
            this.comparator = Objects.requireNonNull(comparator);
        }

        public BinaryHeap(
            Comparator<? super T> comparator,
            List<T> values
        ) {
            this(comparator);
            data.addAll(values);

            for (int i = data.size() / 2 - 1; i >= 0; i--) {
                siftDown(i);
            }
        }

        public int size() {
            return data.size();
        }

        public boolean isEmpty() {
            return data.isEmpty();
        }

        private void siftUp(int index) {
            while (index > 0) {
                int parent = (index - 1) / 2;

                if (
                    comparator.compare(
                        data.get(index),
                        data.get(parent)
                    ) >= 0
                ) {
                    break;
                }

                Collections.swap(data, index, parent);
                index = parent;
            }
        }

        private void siftDown(int index) {
            int size = data.size();

            while (true) {
                int best = index;
                int left = index * 2 + 1;
                int right = left + 1;

                if (
                    left < size &&
                    comparator.compare(
                        data.get(left),
                        data.get(best)
                    ) < 0
                ) {
                    best = left;
                }

                if (
                    right < size &&
                    comparator.compare(
                        data.get(right),
                        data.get(best)
                    ) < 0
                ) {
                    best = right;
                }

                if (best == index) {
                    break;
                }

                Collections.swap(data, index, best);
                index = best;
            }
        }

        public void offer(T value) {
            data.add(value);
            siftUp(data.size() - 1);
        }

        public T peek() {
            if (isEmpty()) {
                throw new EmptyHeapException("Heap is empty.");
            }

            return data.get(0);
        }

        public T poll() {
            if (isEmpty()) {
                throw new EmptyHeapException("Cannot remove from empty heap.");
            }

            T result = data.get(0);
            T last = data.remove(data.size() - 1);

            if (!isEmpty()) {
                data.set(0, last);
                siftDown(0);
            }

            return result;
        }
    }

    private static void validateK(int k, int size, boolean allowZero) {
        if (k < (allowZero ? 0 : 1) || k > size) {
            throw new InvalidInputException("Invalid k: " + k);
        }
    }

    public static int kthLargest(List<Integer> values, int k) {
        validateK(k, values.size(), false);

        PriorityQueue<Integer> heap = new PriorityQueue<>();

        for (int value : values) {
            if (heap.size() < k) {
                heap.offer(value);
            } else if (value > heap.peek()) {
                heap.poll();
                heap.offer(value);
            }
        }

        return heap.peek();
    }

    public static int kthSmallest(List<Integer> values, int k) {
        validateK(k, values.size(), false);

        PriorityQueue<Integer> heap =
            new PriorityQueue<>(Comparator.reverseOrder());

        for (int value : values) {
            if (heap.size() < k) {
                heap.offer(value);
            } else if (value < heap.peek()) {
                heap.poll();
                heap.offer(value);
            }
        }

        return heap.peek();
    }

    public static List<Integer> topKLargest(
        List<Integer> values,
        int k
    ) {
        validateK(k, values.size(), true);

        PriorityQueue<Integer> heap = new PriorityQueue<>();

        for (int value : values) {
            if (heap.size() < k) {
                heap.offer(value);
            } else if (k > 0 && value > heap.peek()) {
                heap.poll();
                heap.offer(value);
            }
        }

        List<Integer> result = new ArrayList<>(heap);
        result.sort(Comparator.reverseOrder());

        return result;
    }

    public record FrequencyEntry(int value, int frequency) {}

    public static List<FrequencyEntry> topKFrequent(
        List<Integer> values,
        int k
    ) {
        if (k < 0) {
            throw new InvalidInputException("k cannot be negative.");
        }

        Map<Integer, Integer> frequencies = new HashMap<>();

        for (int value : values) {
            frequencies.merge(value, 1, Integer::sum);
        }

        Comparator<FrequencyEntry> comparator =
            Comparator.comparingInt(FrequencyEntry::frequency)
                .thenComparing(
                    Comparator.comparingInt(
                        FrequencyEntry::value
                    ).reversed()
                );

        PriorityQueue<FrequencyEntry> heap =
            new PriorityQueue<>(comparator);

        for (var entry : frequencies.entrySet()) {
            FrequencyEntry candidate =
                new FrequencyEntry(entry.getKey(), entry.getValue());

            if (heap.size() < k) {
                heap.offer(candidate);
            } else if (k > 0 && comparator.compare(
                candidate, heap.peek()
            ) > 0) {
                heap.poll();
                heap.offer(candidate);
            }
        }

        List<FrequencyEntry> result = new ArrayList<>(heap);

        result.sort(
            Comparator.comparingInt(FrequencyEntry::frequency)
                .reversed()
                .thenComparingInt(FrequencyEntry::value)
        );

        return result;
    }

    private record MergeNode(
        int value,
        int arrayIndex,
        int elementIndex
    ) {}

    public static List<Integer> mergeSortedArrays(
        List<List<Integer>> arrays
    ) {
        PriorityQueue<MergeNode> heap = new PriorityQueue<>(
            Comparator.comparingInt(MergeNode::value)
                .thenComparingInt(MergeNode::arrayIndex)
        );

        int total = 0;

        for (int i = 0; i < arrays.size(); i++) {
            List<Integer> array = arrays.get(i);

            for (int j = 1; j < array.size(); j++) {
                if (array.get(j) < array.get(j - 1)) {
                    throw new InvalidInputException(
                        "Input array " + i + " is not sorted."
                    );
                }
            }

            total = Math.addExact(total, array.size());

            if (!array.isEmpty()) {
                heap.offer(new MergeNode(array.get(0), i, 0));
            }
        }

        List<Integer> result = new ArrayList<>(total);

        while (!heap.isEmpty()) {
            MergeNode current = heap.poll();
            result.add(current.value());

            int nextIndex = current.elementIndex() + 1;
            List<Integer> array = arrays.get(current.arrayIndex());

            if (nextIndex < array.size()) {
                heap.offer(new MergeNode(
                    array.get(nextIndex),
                    current.arrayIndex(),
                    nextIndex
                ));
            }
        }

        return result;
    }

    public static final class RunningMedian {
        private final PriorityQueue<Integer> lower =
            new PriorityQueue<>(Comparator.reverseOrder());

        private final PriorityQueue<Integer> upper =
            new PriorityQueue<>();

        public void add(int value) {
            if (lower.isEmpty() || value <= lower.peek()) {
                lower.offer(value);
            } else {
                upper.offer(value);
            }

            if (lower.size() > upper.size() + 1) {
                upper.offer(lower.poll());
            } else if (upper.size() > lower.size()) {
                lower.offer(upper.poll());
            }
        }

        public double median() {
            if (lower.isEmpty()) {
                throw new EmptyHeapException("Median is undefined.");
            }

            if (lower.size() > upper.size()) {
                return lower.peek();
            }

            return (
                (double) lower.peek() + (double) upper.peek()
            ) / 2.0;
        }

        public int size() {
            return lower.size() + upper.size();
        }
    }

    public static final class KthLargestStream {
        private final int k;
        private final PriorityQueue<Integer> heap = new PriorityQueue<>();

        public KthLargestStream(int k) {
            if (k < 1) {
                throw new InvalidInputException("k must be positive.");
            }

            this.k = k;
        }

        public Integer add(int value) {
            if (heap.size() < k) {
                heap.offer(value);
            } else if (value > heap.peek()) {
                heap.poll();
                heap.offer(value);
            }

            return heap.size() == k ? heap.peek() : null;
        }
    }

    public record StreamEvent(
        long sequence,
        int value,
        double median,
        Integer kthLargest
    ) {}

    /*
     * Enterprise stream service.
     * Each accepted event receives a monotonic sequence number.
     */
    public static final class StreamAnalyticsService {
        private final RunningMedian median = new RunningMedian();
        private final KthLargestStream kth;
        private final AtomicLong sequence = new AtomicLong();

        public StreamAnalyticsService(int k) {
            this.kth = new KthLargestStream(k);
        }

        public synchronized StreamEvent process(int value) {
            median.add(value);
            Integer kthValue = kth.add(value);

            return new StreamEvent(
                sequence.incrementAndGet(),
                value,
                median.median(),
                kthValue
            );
        }

        public synchronized List<StreamEvent> processBatch(
            List<Integer> values
        ) {
            return values.stream()
                .map(this::process)
                .collect(Collectors.toUnmodifiableList());
        }
    }

    private static void testAlgorithms() {
        List<Integer> values = List.of(3, 2, 1, 5, 6, 4);

        assert kthLargest(values, 2) == 5;
        assert kthSmallest(values, 2) == 2;

        assert topKLargest(values, 3)
            .equals(List.of(6, 5, 4));

        assert mergeSortedArrays(List.of(
            List.of(1, 4, 7),
            List.of(2, 5, 8),
            List.of(3, 6, 9)
        )).equals(List.of(1, 2, 3, 4, 5, 6, 7, 8, 9));

        RunningMedian median = new RunningMedian();

        for (int value : List.of(5, 15, 1, 3)) {
            median.add(value);
        }

        assert median.median() == 4.0;

        KthLargestStream stream = new KthLargestStream(3);

        for (int value : List.of(4, 5, 8, 2)) {
            stream.add(value);
        }

        assert stream.add(3) == 4;
        assert stream.add(10) == 5;

        assert topKFrequent(
            List.of(1, 1, 2, 2, 2, 3), 2
        ).equals(List.of(
            new FrequencyEntry(2, 3),
            new FrequencyEntry(1, 2)
        ));

        try {
            kthLargest(List.of(1, 2), 3);
            throw new AssertionError("Expected validation failure.");
        } catch (InvalidInputException expected) {
            // Expected invalid input.
        }

        try {
            new BinaryHeap<Integer>(Comparator.naturalOrder()).poll();
            throw new AssertionError("Expected empty heap failure.");
        } catch (EmptyHeapException expected) {
            // Expected empty heap.
        }
    }

    private static void demonstrateStreamProcessing() {
        StreamAnalyticsService service =
            new StreamAnalyticsService(3);

        List<StreamEvent> events = service.processBatch(
            List.of(10, 20, 5, 30, 15, 40)
        );

        events.forEach(System.out::println);
    }

    public static void main(String[] args) {
        testAlgorithms();

        System.out.println("All heap tests passed.");

        List<Integer> values =
            List.of(12, 3, 5, 7, 19, 4, 8, 15);

        System.out.println(
            "Kth largest: " + kthLargest(values, 3)
        );

        System.out.println(
            "Kth smallest: " + kthSmallest(values, 3)
        );

        System.out.println(
            "Top four: " + topKLargest(values, 4)
        );

        demonstrateStreamProcessing();
    }
}
