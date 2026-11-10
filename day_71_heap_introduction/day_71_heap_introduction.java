/*
 * HEAP INTRODUCTION
 *
 * Enterprise-oriented heap implementation using Java 17.
 *
 * Features:
 * - Complete binary tree representation
 * - Min-heap and max-heap
 * - Generic heap operations
 * - Bottom-up heap construction
 * - Priority queue for deployment operations
 * - Stable task ordering
 * - Validation and exception handling
 * - Immutable task records
 * - Heap sorting and automated tests
 *
 * Compile:
 * javac HeapIntroduction.java
 *
 * Run:
 * java HeapIntroduction
 */

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Objects;
import java.util.PriorityQueue;
import java.util.concurrent.atomic.AtomicLong;
import java.util.stream.Collectors;


public class HeapIntroduction {

    enum HeapType {
        MIN,
        MAX
    }

    record HeapStatistics(
        long insertions,
        long removals,
        long comparisons,
        long swaps
    ) {}


    static class BinaryHeap<T> {

        private final List<T> data;
        private final Comparator<? super T> comparator;
        private final HeapType type;

        private long insertions;
        private long removals;
        private long comparisons;
        private long swaps;

        BinaryHeap(
            HeapType type,
            Comparator<? super T> comparator
        ) {
            this.type = Objects.requireNonNull(type);
            this.comparator = Objects.requireNonNull(comparator);
            this.data = new ArrayList<>();
        }

        BinaryHeap(
            List<T> values,
            HeapType type,
            Comparator<? super T> comparator
        ) {
            this(type, comparator);

            for (T value : values) {
                validateValue(value);
            }

            this.data.addAll(values);

            // Bottom-up heap construction is O(n).
            for (int i = data.size() / 2 - 1; i >= 0; i--) {
                siftDown(i);
            }
        }

        private void validateValue(T value) {
            Objects.requireNonNull(value, "Heap elements cannot be null");
        }

        private boolean higherPriority(T first, T second) {
            comparisons++;

            int result = comparator.compare(first, second);

            return type == HeapType.MIN
                ? result < 0
                : result > 0;
        }

        private void swap(int first, int second) {
            T temporary = data.get(first);
            data.set(first, data.get(second));
            data.set(second, temporary);
            swaps++;
        }

        private void siftUp(int index) {
            while (index > 0) {
                int parent = (index - 1) / 2;

                if (!higherPriority(data.get(index), data.get(parent))) {
                    break;
                }

                swap(index, parent);
                index = parent;
            }
        }

        private void siftDown(int index) {
            while (true) {
                int best = index;

                int left = 2 * index + 1;
                int right = 2 * index + 2;

                if (
                    left < data.size() &&
                    higherPriority(data.get(left), data.get(best))
                ) {
                    best = left;
                }

                if (
                    right < data.size() &&
                    higherPriority(data.get(right), data.get(best))
                ) {
                    best = right;
                }

                if (best == index) {
                    break;
                }

                swap(index, best);
                index = best;
            }
        }

        public int size() {
            return data.size();
        }

        public boolean isEmpty() {
            return data.isEmpty();
        }

        public T peek() {
            if (isEmpty()) {
                throw new IllegalStateException("Heap is empty");
            }

            return data.get(0);
        }

        public void offer(T value) {
            validateValue(value);

            data.add(value);
            insertions++;

            siftUp(data.size() - 1);
        }

        public T poll() {
            if (isEmpty()) {
                throw new IllegalStateException("Cannot remove from empty heap");
            }

            T result = data.get(0);
            T last = data.remove(data.size() - 1);

            removals++;

            if (!data.isEmpty()) {
                data.set(0, last);
                siftDown(0);
            }

            return result;
        }

        public T replaceRoot(T value) {
            validateValue(value);

            if (isEmpty()) {
                throw new IllegalStateException("Cannot replace empty heap");
            }

            T previous = data.get(0);
            data.set(0, value);

            siftDown(0);

            return previous;
        }

        public boolean validate() {
            for (int i = 1; i < data.size(); i++) {
                int parent = (i - 1) / 2;

                int result = comparator.compare(
                    data.get(i),
                    data.get(parent)
                );

                if (type == HeapType.MIN && result < 0) {
                    return false;
                }

                if (type == HeapType.MAX && result > 0) {
                    return false;
                }
            }

            return true;
        }

        public List<T> arraySnapshot() {
            return List.copyOf(data);
        }

        public List<List<T>> treeLevels() {
            List<List<T>> levels = new ArrayList<>();

            int start = 0;
            int width = 1;

            while (start < data.size()) {
                int end = Math.min(start + width, data.size());

                levels.add(List.copyOf(data.subList(start, end)));

                start = end;
                width *= 2;
            }

            return List.copyOf(levels);
        }

        public HeapStatistics statistics() {
            return new HeapStatistics(
                insertions,
                removals,
                comparisons,
                swaps
            );
        }

        public void display() {
            System.out.println("\n" + type + "-HEAP");
            System.out.println("Array: " + data);

            List<List<T>> levels = treeLevels();

            for (int i = 0; i < levels.size(); i++) {
                System.out.println(
                    "Level " + i + ": " + levels.get(i)
                );
            }
        }
    }


    enum DeploymentStatus {
        PENDING,
        RUNNING,
        COMPLETED,
        FAILED
    }


    record DeploymentTask(
        long id,
        String repository,
        String operation,
        int priority,
        long sequence
    ) {
        DeploymentTask {
            if (repository == null || repository.isBlank()) {
                throw new IllegalArgumentException(
                    "Repository cannot be empty"
                );
            }

            if (operation == null || operation.isBlank()) {
                throw new IllegalArgumentException(
                    "Operation cannot be empty"
                );
            }

            if (priority < 1 || priority > 10) {
                throw new IllegalArgumentException(
                    "Priority must be between 1 and 10"
                );
            }
        }
    }


    interface DeploymentPolicy {
        boolean canExecute(DeploymentTask task);
    }


    static class ProductionDeploymentPolicy
        implements DeploymentPolicy {

        @Override
        public boolean canExecute(DeploymentTask task) {
            return task.priority() >= 1 &&
                   task.priority() <= 10 &&
                   !task.repository().isBlank();
        }
    }


    static class DeploymentService {

        private final AtomicLong idGenerator = new AtomicLong(1);
        private final AtomicLong sequenceGenerator = new AtomicLong(0);

        private final PriorityQueue<DeploymentTask> queue;
        private final DeploymentPolicy policy;

        private final List<DeploymentTask> completed =
            new ArrayList<>();

        private final List<DeploymentTask> failed =
            new ArrayList<>();

        DeploymentService(DeploymentPolicy policy) {
            this.policy = Objects.requireNonNull(policy);

            this.queue = new PriorityQueue<>(
                Comparator.comparingInt(DeploymentTask::priority)
                    .thenComparingLong(DeploymentTask::sequence)
            );
        }

        public synchronized DeploymentTask schedule(
            String repository,
            String operation,
            int priority
        ) {
            DeploymentTask task = new DeploymentTask(
                idGenerator.getAndIncrement(),
                repository,
                operation,
                priority,
                sequenceGenerator.getAndIncrement()
            );

            if (!policy.canExecute(task)) {
                throw new SecurityException(
                    "Deployment policy rejected task"
                );
            }

            queue.offer(task);

            return task;
        }

        public synchronized DeploymentTask executeNext() {
            DeploymentTask task = queue.poll();

            if (task == null) {
                throw new IllegalStateException(
                    "No pending deployments"
                );
            }

            try {
                // A real deployment adapter would perform the operation.
                completed.add(task);
                return task;
            } catch (RuntimeException error) {
                failed.add(task);
                throw error;
            }
        }

        public synchronized List<DeploymentTask> pending() {
            return queue.stream()
                .sorted(
                    Comparator.comparingInt(DeploymentTask::priority)
                        .thenComparingLong(DeploymentTask::sequence)
                )
                .collect(Collectors.toUnmodifiableList());
        }

        public synchronized List<DeploymentTask> completed() {
            return List.copyOf(completed);
        }

        public synchronized List<DeploymentTask> failed() {
            return List.copyOf(failed);
        }
    }


    static <T> List<T> heapSort(
        List<T> values,
        Comparator<? super T> comparator
    ) {
        BinaryHeap<T> heap = new BinaryHeap<>(
            values,
            HeapType.MIN,
            comparator
        );

        List<T> sorted = new ArrayList<>(values.size());

        while (!heap.isEmpty()) {
            sorted.add(heap.poll());
        }

        return List.copyOf(sorted);
    }


    static void demonstrateCompleteBinaryTree() {
        System.out.println("\nCOMPLETE BINARY TREE");

        List<Integer> values = List.of(
            10, 20, 30, 40, 50, 60, 70
        );

        for (int i = 0; i < values.size(); i++) {
            Integer parent = i == 0
                ? null
                : values.get((i - 1) / 2);

            int left = 2 * i + 1;
            int right = 2 * i + 2;

            System.out.println(
                "Node=" + values.get(i) +
                ", Parent=" + parent +
                ", Left=" + (left < values.size()
                    ? values.get(left) : null) +
                ", Right=" + (right < values.size()
                    ? values.get(right) : null)
            );
        }
    }


    static void demonstrateHeaps() {
        List<Integer> values = List.of(
            40, 10, 30, 50, 20, 60, 70
        );

        BinaryHeap<Integer> minHeap = new BinaryHeap<>(
            values,
            HeapType.MIN,
            Integer::compare
        );

        BinaryHeap<Integer> maxHeap = new BinaryHeap<>(
            values,
            HeapType.MAX,
            Integer::compare
        );

        minHeap.display();
        maxHeap.display();

        System.out.println("\nMinimum: " + minHeap.peek());
        System.out.println("Maximum: " + maxHeap.peek());

        minHeap.offer(5);

        System.out.println("After insertion:");
        minHeap.display();

        System.out.println("Removed: " + minHeap.poll());

        System.out.println("Min valid: " + minHeap.validate());
        System.out.println("Max valid: " + maxHeap.validate());

        System.out.println("Statistics: " + minHeap.statistics());
    }


    static void demonstrateDeploymentService() {
        System.out.println("\nDEPLOYMENT PRIORITY QUEUE");

        DeploymentService service =
            new DeploymentService(
                new ProductionDeploymentPolicy()
            );

        service.schedule("portfolio-api", "Run tests", 3);
        service.schedule("security-engine", "Security audit", 1);
        service.schedule("market-service", "Generate report", 7);
        service.schedule("portfolio-api", "Production incident", 1);

        System.out.println("Pending: " + service.pending());

        while (!service.pending().isEmpty()) {
            DeploymentTask task = service.executeNext();

            System.out.println(
                "Executed: " + task.repository() +
                " | " + task.operation() +
                " | Priority: " + task.priority()
            );
        }

        System.out.println("Completed: " + service.completed().size());
    }


    static void demonstrateEdgeCases() {
        System.out.println("\nEDGE CASES");

        BinaryHeap<Integer> empty = new BinaryHeap<>(
            HeapType.MIN,
            Integer::compare
        );

        try {
            empty.poll();
        } catch (IllegalStateException error) {
            System.out.println("Expected error: " + error.getMessage());
        }

        BinaryHeap<Integer> single = new BinaryHeap<>(
            List.of(42),
            HeapType.MIN,
            Integer::compare
        );

        System.out.println("Single element: " + single.poll());

        BinaryHeap<Integer> duplicates = new BinaryHeap<>(
            List.of(5, 5, 5, 2, 2),
            HeapType.MIN,
            Integer::compare
        );

        System.out.println("Duplicate extraction:");

        while (!duplicates.isEmpty()) {
            System.out.print(duplicates.poll() + " ");
        }

        System.out.println();

        try {
            new DeploymentTask(
                1, "repository", "Invalid task", 15, 0
            );
        } catch (IllegalArgumentException error) {
            System.out.println("Validation: " + error.getMessage());
        }
    }


    static void runTests() {
        BinaryHeap<Integer> min = new BinaryHeap<>(
            List.of(9, 4, 7, 1, 3),
            HeapType.MIN,
            Integer::compare
        );

        BinaryHeap<Integer> max = new BinaryHeap<>(
            List.of(9, 4, 7, 1, 3),
            HeapType.MAX,
            Integer::compare
        );

        if (min.peek() != 1 || max.peek() != 9) {
            throw new AssertionError("Incorrect heap roots");
        }

        min.offer(0);

        if (min.poll() != 0) {
            throw new AssertionError("Incorrect minimum extraction");
        }

        if (!min.validate() || !max.validate()) {
            throw new AssertionError("Heap property violated");
        }

        List<Integer> sorted = heapSort(
            List.of(5, 1, 4, 2, 3),
            Integer::compare
        );

        if (!sorted.equals(List.of(1, 2, 3, 4, 5))) {
            throw new AssertionError("Heap sort failed");
        }

        if (!heapSort(List.of(), Integer::compare).isEmpty()) {
            throw new AssertionError("Empty sort failed");
        }

        System.out.println("\nAll tests passed.");
    }


    public static void main(String[] args) {
        try {
            System.out.println("HEAP INTRODUCTION");
            System.out.println("=================");

            demonstrateCompleteBinaryTree();
            demonstrateHeaps();
            demonstrateDeploymentService();
            demonstrateEdgeCases();

            List<Integer> values = List.of(
                12, 4, 19, 1, 8, 3, 15
            );

            System.out.println("\nHEAP SORT:");

            System.out.println(
                heapSort(values, Integer::compare)
            );

            runTests();

        } catch (RuntimeException error) {
            System.err.println(
                "Application failure: " + error.getMessage()
            );

            throw error;
        }
    }
}
