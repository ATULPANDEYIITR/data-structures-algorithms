import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.function.Predicate;

/**
 * Queue Introduction
 *
 * Enterprise-oriented queue model for a deployment request workflow.
 *
 * Java 17+
 */
public class QueueIntroduction {

    enum DeploymentState {
        QUEUED,
        RUNNING,
        SUCCEEDED,
        FAILED
    }

    record DeploymentRequest(
            String id,
            String service,
            String environment,
            String requester,
            DeploymentState state) {

        DeploymentRequest {
            if (id == null || id.isBlank()) {
                throw new IllegalArgumentException(
                        "Deployment ID cannot be empty");
            }

            if (service == null || service.isBlank()) {
                throw new IllegalArgumentException(
                        "Service cannot be empty");
            }

            if (environment == null || environment.isBlank()) {
                throw new IllegalArgumentException(
                        "Environment cannot be empty");
            }

            if (requester == null || requester.isBlank()) {
                throw new IllegalArgumentException(
                        "Requester cannot be empty");
            }

            if (state == null) {
                throw new IllegalArgumentException(
                        "Deployment state is required");
            }
        }

        DeploymentRequest withState(DeploymentState newState) {
            return new DeploymentRequest(
                    id,
                    service,
                    environment,
                    requester,
                    newState);
        }
    }

    /**
     * A fixed-capacity circular array queue.
     *
     * This representation makes both insertion and removal O(1) and avoids
     * shifting the remaining elements after every dequeue.
     */
    static final class CircularQueue<T> {

        private final Object[] elements;
        private int front;
        private int rear;
        private int size;

        CircularQueue(int capacity) {
            if (capacity <= 0) {
                throw new IllegalArgumentException(
                        "Capacity must be positive");
            }

            elements = new Object[capacity];
        }

        void enqueue(T value) {
            if (isFull()) {
                throw new IllegalStateException("Queue is full");
            }

            elements[rear] = value;
            rear = (rear + 1) % elements.length;
            size++;
        }

        @SuppressWarnings("unchecked")
        T dequeue() {
            if (isEmpty()) {
                throw new IllegalStateException(
                        "Cannot dequeue from an empty queue");
            }

            T value = (T) elements[front];
            elements[front] = null;
            front = (front + 1) % elements.length;
            size--;

            return value;
        }

        @SuppressWarnings("unchecked")
        T peek() {
            if (isEmpty()) {
                throw new IllegalStateException(
                        "Cannot inspect an empty queue");
            }

            return (T) elements[front];
        }

        boolean isEmpty() {
            return size == 0;
        }

        boolean isFull() {
            return size == elements.length;
        }

        int size() {
            return size;
        }

        List<T> values() {
            List<T> result = new ArrayList<>(size);

            for (int offset = 0; offset < size; offset++) {
                int index = (front + offset) % elements.length;

                @SuppressWarnings("unchecked")
                T value = (T) elements[index];

                result.add(value);
            }

            return result;
        }
    }

    /**
     * Enterprise queue service.
     *
     * The domain service owns validation and lifecycle rules rather than
     * allowing callers to manipulate the underlying collection directly.
     */
    static final class DeploymentQueue {

        private final Deque<DeploymentRequest> pending =
                new ArrayDeque<>();

        private final Set<String> activeIds = new HashSet<>();

        void submit(DeploymentRequest request) {
            if (!activeIds.add(request.id())) {
                throw new IllegalArgumentException(
                        "Duplicate active deployment: " + request.id());
            }

            pending.addLast(request);
        }

        DeploymentRequest next() {
            DeploymentRequest request = pending.peekFirst();

            if (request == null) {
                throw new IllegalStateException(
                        "No deployment requests are waiting");
            }

            return request;
        }

        DeploymentRequest startNext() {
            DeploymentRequest request = pending.pollFirst();

            if (request == null) {
                throw new IllegalStateException(
                        "No deployment requests are waiting");
            }

            return request.withState(DeploymentState.RUNNING);
        }

        void complete(DeploymentRequest request,
                      boolean successful) {

            if (!activeIds.remove(request.id())) {
                throw new IllegalStateException(
                        "Deployment is not active: " + request.id());
            }

            DeploymentState state = successful
                    ? DeploymentState.SUCCEEDED
                    : DeploymentState.FAILED;

            DeploymentRequest completed =
                    request.withState(state);

            System.out.println(
                    completed.id() + " -> " + completed.state());
        }

        int pendingCount() {
            return pending.size();
        }
    }

    /**
     * A policy abstraction keeps workflow decisions separate from queue
     * mechanics. The queue determines order; this policy determines whether
     * an item may proceed once it reaches the front.
     */
    static final class DeploymentPolicy {

        private final Predicate<DeploymentRequest> eligibilityRule;

        DeploymentPolicy(
                Predicate<DeploymentRequest> eligibilityRule) {

            this.eligibilityRule = eligibilityRule;
        }

        boolean canStart(DeploymentRequest request) {
            return eligibilityRule.test(request);
        }
    }

    static void demonstrateFifo() {
        System.out.println("\n=== FIFO Behavior ===");

        CircularQueue<String> queue = new CircularQueue<>(4);

        queue.enqueue("REQUEST-A");
        queue.enqueue("REQUEST-B");
        queue.enqueue("REQUEST-C");

        System.out.println("Front: " + queue.peek());
        System.out.println("Dequeued: " + queue.dequeue());

        queue.enqueue("REQUEST-D");
        queue.enqueue("REQUEST-E");

        System.out.println("Logical order: " + queue.values());
    }

    static void demonstrateDeploymentWorkflow() {
        System.out.println("\n=== Deployment Workflow ===");

        DeploymentQueue queue = new DeploymentQueue();

        DeploymentRequest first = new DeploymentRequest(
                "DEP-100",
                "payments-api",
                "staging",
                "Asha",
                DeploymentState.QUEUED);

        DeploymentRequest second = new DeploymentRequest(
                "DEP-101",
                "audit-service",
                "production",
                "Rahul",
                DeploymentState.QUEUED);

        DeploymentRequest third = new DeploymentRequest(
                "DEP-102",
                "reporting-api",
                "staging",
                "Meera",
                DeploymentState.QUEUED);

        queue.submit(first);
        queue.submit(second);
        queue.submit(third);

        DeploymentPolicy policy = new DeploymentPolicy(
                request -> !request.environment()
                        .equalsIgnoreCase("production"));

        System.out.println("Next request: " + queue.next().id());

        while (queue.pendingCount() > 0) {
            DeploymentRequest request = queue.startNext();

            boolean allowed = policy.canStart(request);

            if (!allowed) {
                System.out.println(
                        request.id()
                                + " blocked by deployment policy");
                queue.complete(request, false);
                continue;
            }

            System.out.println(
                    request.id() + " is running for "
                            + request.service());

            queue.complete(request, true);
        }
    }

    static void demonstrateFailures() {
        System.out.println("\n=== Failure Handling ===");

        CircularQueue<String> queue = new CircularQueue<>(2);

        try {
            queue.dequeue();
        } catch (IllegalStateException error) {
            System.out.println(
                    "Expected empty-queue error: "
                            + error.getMessage());
        }

        queue.enqueue("A");
        queue.enqueue("B");

        try {
            queue.enqueue("C");
        } catch (IllegalStateException error) {
            System.out.println(
                    "Expected capacity error: "
                            + error.getMessage());
        }

        try {
            new DeploymentRequest(
                    "",
                    "service",
                    "staging",
                    "user",
                    DeploymentState.QUEUED);
        } catch (IllegalArgumentException error) {
            System.out.println(
                    "Expected validation error: "
                            + error.getMessage());
        }
    }

    static void verifyInvariants() {
        System.out.println("\n=== Invariant Verification ===");

        CircularQueue<Integer> queue = new CircularQueue<>(3);

        queue.enqueue(10);
        queue.enqueue(20);
        queue.enqueue(30);

        if (!queue.isFull()) {
            throw new IllegalStateException(
                    "Queue should be full");
        }

        if (queue.dequeue() != 10 ||
                queue.dequeue() != 20) {
            throw new IllegalStateException(
                    "FIFO order was violated");
        }

        queue.enqueue(40);

        List<Integer> expected = List.of(30, 40);

        if (!queue.values().equals(expected)) {
            throw new IllegalStateException(
                    "Circular wrap-around failed");
        }

        if (queue.dequeue() != 30 ||
                queue.dequeue() != 40 ||
                !queue.isEmpty()) {
            throw new IllegalStateException(
                    "Final queue state is invalid");
        }

        System.out.println("All queue invariants passed.");
    }

    public static void main(String[] args) {
        demonstrateFifo();
        demonstrateDeploymentWorkflow();
        demonstrateFailures();
        verifyInvariants();

        System.out.println("\nComplexity:");
        System.out.println("Circular enqueue: O(1)");
        System.out.println("Circular dequeue: O(1)");
        System.out.println("Deque addLast:    O(1) amortized");
        System.out.println("Deque pollFirst:  O(1)");
        System.out.println("Queue storage:    O(n)");
    }
}
