import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.Optional;

/*
 * Enterprise Repository Governance Model
 *
 * The circular queue acts as a bounded event channel for Pull Request
 * governance events. The domain model separately represents Pull Requests,
 * reviews, approvals, protected branches, and merge eligibility.
 *
 * Java's type system makes the distinction between those domain concepts
 * explicit instead of representing the workflow as loosely structured data.
 */

public class CircularQueueGovernance {

    enum PullRequestState {
        DRAFT,
        OPEN,
        CLOSED,
        MERGED
    }

    enum ReviewState {
        COMMENTED,
        CHANGES_REQUESTED,
        APPROVED,
        DISMISSED
    }

    record Review(
        String reviewer,
        ReviewState state,
        boolean eligibleReviewer
    ) {
        Review {
            Objects.requireNonNull(reviewer, "reviewer");
            Objects.requireNonNull(state, "state");

            if (reviewer.isBlank()) {
                throw new IllegalArgumentException("Reviewer cannot be blank.");
            }
        }
    }

    record StatusCheck(
        String name,
        boolean required,
        boolean passed
    ) {
        StatusCheck {
            Objects.requireNonNull(name, "name");

            if (name.isBlank()) {
                throw new IllegalArgumentException("Status check name cannot be blank.");
            }
        }
    }

    static final class PullRequest {
        private final long id;
        private final String repository;
        private final String sourceBranch;
        private final String targetBranch;
        private PullRequestState state;
        private final List<Review> reviews = new ArrayList<>();
        private final List<StatusCheck> statusChecks = new ArrayList<>();

        PullRequest(
            long id,
            String repository,
            String sourceBranch,
            String targetBranch
        ) {
            if (id <= 0) {
                throw new IllegalArgumentException("Pull Request ID must be positive.");
            }

            this.id = id;
            this.repository = requireText(repository, "repository");
            this.sourceBranch = requireText(sourceBranch, "sourceBranch");
            this.targetBranch = requireText(targetBranch, "targetBranch");
            this.state = PullRequestState.DRAFT;
        }

        void markReadyForReview() {
            if (state != PullRequestState.DRAFT) {
                throw new IllegalStateException(
                    "Only draft Pull Requests can become ready for review."
                );
            }

            state = PullRequestState.OPEN;
        }

        void close() {
            if (state != PullRequestState.OPEN) {
                throw new IllegalStateException(
                    "Only open Pull Requests can be closed."
                );
            }

            state = PullRequestState.CLOSED;
        }

        void addReview(Review review) {
            if (state != PullRequestState.OPEN) {
                throw new IllegalStateException(
                    "Reviews can only be submitted for open Pull Requests."
                );
            }

            reviews.add(Objects.requireNonNull(review));
        }

        void addStatusCheck(StatusCheck check) {
            statusChecks.add(Objects.requireNonNull(check));
        }

        long id() {
            return id;
        }

        String repository() {
            return repository;
        }

        String targetBranch() {
            return targetBranch;
        }

        PullRequestState state() {
            return state;
        }

        List<Review> reviews() {
            return List.copyOf(reviews);
        }

        List<StatusCheck> statusChecks() {
            return List.copyOf(statusChecks);
        }

        private static String requireText(String value, String field) {
            Objects.requireNonNull(value, field);

            if (value.isBlank()) {
                throw new IllegalArgumentException(field + " cannot be blank.");
            }

            return value;
        }
    }

    record BranchProtectionPolicy(
        String branch,
        int requiredApprovals,
        boolean requireStatusChecks,
        boolean prohibitForcePush,
        boolean prohibitDeletion
    ) {
        BranchProtectionPolicy {
            Objects.requireNonNull(branch, "branch");

            if (branch.isBlank()) {
                throw new IllegalArgumentException("Protected branch cannot be blank.");
            }

            if (requiredApprovals < 0) {
                throw new IllegalArgumentException(
                    "Required approval count cannot be negative."
                );
            }
        }
    }

    static final class MergeEligibilityService {

        boolean isEligible(
            PullRequest pullRequest,
            BranchProtectionPolicy policy
        ) {
            Objects.requireNonNull(pullRequest);
            Objects.requireNonNull(policy);

            if (pullRequest.state() != PullRequestState.OPEN) {
                return false;
            }

            if (!pullRequest.targetBranch().equals(policy.branch())) {
                return false;
            }

            long validApprovals = pullRequest.reviews()
                .stream()
                .filter(Review::eligibleReviewer)
                .filter(review -> review.state() == ReviewState.APPROVED)
                .count();

            if (validApprovals < policy.requiredApprovals()) {
                return false;
            }

            if (policy.requireStatusChecks()) {
                boolean allRequiredChecksPass =
                    pullRequest.statusChecks()
                        .stream()
                        .filter(StatusCheck::required)
                        .allMatch(StatusCheck::passed);

                if (!allRequiredChecksPass) {
                    return false;
                }
            }

            return true;
        }

        String explain(
            PullRequest pullRequest,
            BranchProtectionPolicy policy
        ) {
            if (pullRequest.state() != PullRequestState.OPEN) {
                return "Pull Request is not open.";
            }

            if (!pullRequest.targetBranch().equals(policy.branch())) {
                return "Pull Request does not target the protected branch.";
            }

            long approvals = pullRequest.reviews()
                .stream()
                .filter(Review::eligibleReviewer)
                .filter(review -> review.state() == ReviewState.APPROVED)
                .count();

            if (approvals < policy.requiredApprovals()) {
                return "Required approval threshold has not been reached.";
            }

            if (policy.requireStatusChecks()) {
                boolean checksPass = pullRequest.statusChecks()
                    .stream()
                    .filter(StatusCheck::required)
                    .allMatch(StatusCheck::passed);

                if (!checksPass) {
                    return "One or more required status checks are failing.";
                }
            }

            return "All modeled merge conditions are satisfied.";
        }
    }

    static final class CircularQueue<T> {
        private final Object[] buffer;
        private int front;
        private int rear;
        private int size;

        CircularQueue(int capacity) {
            if (capacity <= 0) {
                throw new IllegalArgumentException(
                    "Queue capacity must be positive."
                );
            }

            buffer = new Object[capacity];
        }

        boolean isEmpty() {
            return size == 0;
        }

        boolean isFull() {
            return size == buffer.length;
        }

        int size() {
            return size;
        }

        int capacity() {
            return buffer.length;
        }

        void enqueue(T value) {
            Objects.requireNonNull(value, "Queue values cannot be null.");

            if (isFull()) {
                throw new IllegalStateException(
                    "Circular queue overflow."
                );
            }

            buffer[rear] = value;
            rear = (rear + 1) % buffer.length;
            size++;
        }

        @SuppressWarnings("unchecked")
        T dequeue() {
            if (isEmpty()) {
                throw new IllegalStateException(
                    "Circular queue underflow."
                );
            }

            T value = (T) buffer[front];
            buffer[front] = null;

            front = (front + 1) % buffer.length;
            size--;

            return value;
        }

        @SuppressWarnings("unchecked")
        Optional<T> peek() {
            if (isEmpty()) {
                return Optional.empty();
            }

            return Optional.of((T) buffer[front]);
        }
    }

    static void demonstrateQueue() {
        System.out.println("\n=== Generic Circular Queue ===");

        CircularQueue<String> queue = new CircularQueue<>(3);

        queue.enqueue("PR_OPENED");
        queue.enqueue("REVIEW_SUBMITTED");

        System.out.println("Peek: " + queue.peek().orElseThrow());

        System.out.println("Removed: " + queue.dequeue());

        queue.enqueue("STATUS_CHECK_COMPLETED");
        queue.enqueue("MERGE_REQUESTED");

        while (!queue.isEmpty()) {
            System.out.println("Processing: " + queue.dequeue());
        }
    }

    static void demonstrateGovernance() {
        System.out.println("\n=== Enterprise Governance Workflow ===");

        PullRequest pullRequest = new PullRequest(
            7001,
            "payments-service",
            "feature/refund-validation",
            "main"
        );

        pullRequest.markReadyForReview();

        pullRequest.addReview(
            new Review("reviewer-alice", ReviewState.APPROVED, true)
        );

        pullRequest.addReview(
            new Review("reviewer-bob", ReviewState.CHANGES_REQUESTED, true)
        );

        pullRequest.addReview(
            new Review("automation-account", ReviewState.APPROVED, false)
        );

        pullRequest.addStatusCheck(
            new StatusCheck("unit-tests", true, true)
        );

        pullRequest.addStatusCheck(
            new StatusCheck("security-scan", true, true)
        );

        BranchProtectionPolicy policy = new BranchProtectionPolicy(
            "main",
            2,
            true,
            true,
            true
        );

        MergeEligibilityService service = new MergeEligibilityService();

        System.out.println("PR state: " + pullRequest.state());
        System.out.println("Merge eligible: " +
            service.isEligible(pullRequest, policy));
        System.out.println("Reason: " +
            service.explain(pullRequest, policy));

        pullRequest.addReview(
            new Review("reviewer-carol", ReviewState.APPROVED, true)
        );

        System.out.println("After second eligible approval:");
        System.out.println("Merge eligible: " +
            service.isEligible(pullRequest, policy));
        System.out.println("Reason: " +
            service.explain(pullRequest, policy));
    }

    static void demonstrateFailureState() {
        System.out.println("\n=== Invalid State Transition ===");

        PullRequest pullRequest = new PullRequest(
            7002,
            "identity-service",
            "feature/auth",
            "main"
        );

        try {
            pullRequest.addReview(
                new Review("reviewer", ReviewState.APPROVED, true)
            );
        } catch (IllegalStateException exception) {
            System.out.println("Rejected invalid workflow state: " +
                exception.getMessage());
        }
    }

    public static void main(String[] args) {
        System.out.println("CIRCULAR QUEUE AND REPOSITORY GOVERNANCE");

        demonstrateQueue();
        demonstrateGovernance();
        demonstrateFailureState();

        System.out.println("\nImplementation completed.");
    }
}
