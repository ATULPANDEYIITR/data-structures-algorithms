import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.PriorityQueue;
import java.util.Set;
import java.util.concurrent.atomic.AtomicLong;
import java.util.stream.Collectors;

/*
 * Heap Operations and Enterprise Priority Scheduling
 * Java 17
 *
 * Implements:
 * - Generic binary min-heap and max-heap
 * - Heapify and bottom-up construction
 * - Insertion, deletion, extraction and update
 * - Priority queue scheduling
 * - Stable task ordering
 * - Policy-based task execution
 * - Validation and state transitions
 * - Automated tests
 */

public class HeapOperations {

    enum HeapMode {
        MIN,
        MAX
    }

    enum TaskStatus {
        QUEUED,
        PROCESSING,
        COMPLETED,
        FAILED
    }

    static class EmptyHeapException extends RuntimeException {
        EmptyHeapException(String message) {
            super(message);
        }
    }

    static class HeapValidationException extends RuntimeException {
        HeapValidationException(String message) {
            super(message);
        }
    }

    static class BinaryHeap<T> {

        private final List<T> data = new ArrayList<>();
        private final Comparator<? super T> comparator;
        private final HeapMode mode;

        BinaryHeap(
            Comparator<? super T> comparator,
            HeapMode mode
        ) {
            if (comparator == null || mode == null) {
                throw new IllegalArgumentException(
                    "Comparator and heap mode are required."
                );
            }

            this.comparator = comparator;
            this.mode = mode;
        }

        BinaryHeap(
            List<T> values,
            Comparator<? super T> comparator,
            HeapMode mode
        ) {
            this(comparator, mode);

            for (T value : values) {
                validate(value);
                data.add(value);
            }

            heapify();
        }

        private void validate(T value) {
            if (value == null) {
                throw new HeapValidationException(
                    "Null heap elements are not permitted."
                );
            }
        }

        private boolean higherPriority(T a, T b) {
            int result = comparator.compare(a, b);

            return mode == HeapMode.MIN
                ? result < 0
                : result > 0;
        }

        private void swap(int i, int j) {
            T temporary = data.get(i);
            data.set(i, data.get(j));
            data.set(j, temporary);
        }

        private void siftUp(int index) {
            while (index > 0) {
                int parent = (index - 1) / 2;

                if (!higherPriority(
                    data.get(index),
                    data.get(parent)
                )) {
                    break;
                }

                swap(index, parent);
                index = parent;
            }
        }

        private void siftDown(int index) {
            int n = data.size();

            while (true) {
                int left = 2 * index + 1;
                int right = 2 * index + 2;
                int best = index;

                if (
                    left < n &&
                    higherPriority(
                        data.get(left),
                        data.get(best)
                    )
                ) {
                    best = left;
                }

                if (
                    right < n &&
                    higherPriority(
                        data.get(right),
                        data.get(best)
                    )
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

        public void heapify() {
            for (int i = data.size() / 2 - 1; i >= 0; i--) {
                siftDown(i);
            }
        }

        public void insert(T value) {
            validate(value);
            data.add(value);
            siftUp(data.size() - 1);
        }

        public T peek() {
            if (data.isEmpty()) {
                throw new EmptyHeapException("Heap is empty.");
            }

            return data.get(0);
        }

        public T extract() {
            if (data.isEmpty()) {
                throw new EmptyHeapException("Heap is empty.");
            }

            T result = data.get(0);
            T last = data.remove(data.size() - 1);

            if (!data.isEmpty()) {
                data.set(0, last);
                siftDown(0);
            }

            return result;
        }

        public T deleteAt(int index) {
            if (index < 0 || index >= data.size()) {
                throw new IndexOutOfBoundsException(
                    "Invalid heap index."
                );
            }

            T removed = data.get(index);
            T last = data.remove(data.size() - 1);

            if (index < data.size()) {
                data.set(index, last);

                if (
                    index > 0 &&
                    higherPriority(
                        data.get(index),
                        data.get((index - 1) / 2)
                    )
                ) {
                    siftUp(index);
                } else {
                    siftDown(index);
                }
            }

            return removed;
        }

        public void update(int index, T value) {
            validate(value);

            if (index < 0 || index >= data.size()) {
                throw new IndexOutOfBoundsException(
                    "Invalid heap index."
                );
            }

            T old = data.get(index);
            data.set(index, value);

            if (higherPriority(value, old)) {
                siftUp(index);
            } else {
                siftDown(index);
            }
        }

        public boolean deleteValue(T value) {
            int index = data.indexOf(value);

            if (index < 0) {
                return false;
            }

            deleteAt(index);
            return true;
        }

        public boolean isValid() {
            for (int i = 1; i < data.size(); i++) {
                int parent = (i - 1) / 2;

                if (higherPriority(
                    data.get(i),
                    data.get(parent)
                )) {
                    return false;
                }
            }

            return true;
        }

        public List<T> sortedValues() {
            BinaryHeap<T> copy = new BinaryHeap<>(
                data,
                comparator,
                mode
            );

            List<T> result = new ArrayList<>();

            while (copy.size() > 0) {
                result.add(copy.extract());
            }

            return result;
        }

        public int size() {
            return data.size();
        }

        public boolean isEmpty() {
            return data.isEmpty();
        }
    }

    record Task(
        String id,
        String description,
        int priority
    ) {
        Task {
            if (id == null || id.isBlank()) {
                throw new IllegalArgumentException(
                    "Task ID is required."
                );
            }

            if (description == null || description.isBlank()) {
                throw new IllegalArgumentException(
                    "Description is required."
                );
            }
        }
    }

    record ScheduledTask(
        Task task,
        long sequence
    ) {}

    interface TaskExecutionPolicy {
        boolean isAllowed(Task task);
    }

    static class PriorityScheduler {

        private final PriorityQueue<ScheduledTask> queue;
        private final Set<String> activeIds = new HashSet<>();
        private final AtomicLong sequence = new AtomicLong();

        private final java.util.Map<String, TaskStatus> statuses =
            new java.util.HashMap<>();

        private final TaskExecutionPolicy policy;

        PriorityScheduler(TaskExecutionPolicy policy) {
            this.policy = policy;

            queue = new PriorityQueue<>(
                Comparator
                    .<ScheduledTask>comparingInt(
                        item -> item.task().priority()
                    )
                    .reversed()
                    .thenComparingLong(ScheduledTask::sequence)
            );
        }

        public void submit(Task task) {
            if (task == null) {
                throw new IllegalArgumentException(
                    "Task is required."
                );
            }

            if (!activeIds.add(task.id())) {
                throw new HeapValidationException(
                    "Duplicate active task ID: " + task.id()
                );
            }

            queue.add(new ScheduledTask(
                task,
                sequence.getAndIncrement()
            ));

            statuses.put(task.id(), TaskStatus.QUEUED);
        }

        public Task peek() {
            if (queue.isEmpty()) {
                throw new EmptyHeapException(
                    "No pending tasks."
                );
            }

            return queue.peek().task();
        }

        public Task processNext() {
            if (queue.isEmpty()) {
                throw new EmptyHeapException(
                    "No pending tasks."
                );
            }

            ScheduledTask scheduled = queue.poll();
            Task task = scheduled.task();

            statuses.put(task.id(), TaskStatus.PROCESSING);

            try {
                if (!policy.isAllowed(task)) {
                    throw new SecurityException(
                        "Task execution denied: " + task.id()
                    );
                }

                statuses.put(task.id(), TaskStatus.COMPLETED);
                return task;

            } catch (RuntimeException error) {
                statuses.put(task.id(), TaskStatus.FAILED);
                throw error;

            } finally {
                activeIds.remove(task.id());
            }
        }

        public TaskStatus getStatus(String taskId) {
            return statuses.get(taskId);
        }

        public int size() {
            return queue.size();
        }
    }

    static void runTests() {

        BinaryHeap<Integer> minHeap = new BinaryHeap<>(
            List.of(9, 4, 7, 1, 3),
            Comparator.naturalOrder(),
            HeapMode.MIN
        );

        assert minHeap.isValid();
        assert minHeap.extract() == 1;
        assert minHeap.isValid();

        BinaryHeap<Integer> maxHeap = new BinaryHeap<>(
            List.of(9, 4, 7, 1, 3),
            Comparator.naturalOrder(),
            HeapMode.MAX
        );

        assert maxHeap.extract() == 9;

        BinaryHeap<Integer> heap = new BinaryHeap<>(
            Comparator.naturalOrder(),
            HeapMode.MIN
        );

        heap.insert(10);
        heap.insert(5);
        heap.insert(20);

        heap.update(2, 1);

        assert heap.peek() == 1;
        assert heap.deleteValue(10);
        assert !heap.deleteValue(100);
        assert heap.isValid();

        assert heap.sortedValues().equals(List.of(1, 5));

        boolean failed = false;

        try {
            new BinaryHeap<Integer>(
                Comparator.naturalOrder(),
                HeapMode.MIN
            ).extract();
        } catch (EmptyHeapException exception) {
            failed = true;
        }

        assert failed;

        PriorityScheduler scheduler =
            new PriorityScheduler(task -> true);

        scheduler.submit(new Task("A", "Normal", 1));
        scheduler.submit(new Task("B", "Critical", 10));

        assert scheduler.processNext().id().equals("B");
        assert scheduler.getStatus("B") == TaskStatus.COMPLETED;

        PriorityScheduler restricted =
            new PriorityScheduler(task -> false);

        restricted.submit(
            new Task("C", "Restricted operation", 5)
        );

        try {
            restricted.processNext();
            throw new AssertionError("Policy should deny task.");
        } catch (SecurityException expected) {
            assert restricted.getStatus("C") == TaskStatus.FAILED;
        }

        System.out.println("All Java 17 tests passed.");
    }

    public static void main(String[] args) {

        runTests();

        BinaryHeap<Integer> minHeap = new BinaryHeap<>(
            List.of(40, 10, 30, 5, 20, 50),
            Comparator.naturalOrder(),
            HeapMode.MIN
        );

        System.out.println("\nMIN HEAP");
        System.out.println("Minimum: " + minHeap.peek());
        System.out.println("Extracted: " + minHeap.extract());

        minHeap.insert(2);
        minHeap.deleteValue(30);

        System.out.println(
            "Sorted values: " + minHeap.sortedValues()
        );

        BinaryHeap<Integer> maxHeap = new BinaryHeap<>(
            List.of(40, 10, 30, 5, 20, 50),
            Comparator.naturalOrder(),
            HeapMode.MAX
        );

        System.out.println("\nMAX HEAP");
        System.out.println("Maximum: " + maxHeap.extract());

        PriorityScheduler scheduler =
            new PriorityScheduler(task -> task.priority() <= 10);

        scheduler.submit(
            new Task("T101", "Database backup", 3)
        );

        scheduler.submit(
            new Task("T102", "Security incident", 10)
        );

        scheduler.submit(
            new Task("T103", "System monitoring", 5)
        );

        System.out.println("\nENTERPRISE TASK SCHEDULER");

        while (scheduler.size() > 0) {
            Task task = scheduler.processNext();

            System.out.println(
                task.id() + " | " +
                task.description() + " | " +
                task.priority()
            );
        }
    }
}
