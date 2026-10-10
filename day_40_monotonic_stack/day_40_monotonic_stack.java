import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.EnumSet;
import java.util.List;
import java.util.Objects;
import java.util.Set;

public class MonotonicStackGovernance {

    enum ReviewState {
        COMMENTED,
        CHANGES_REQUESTED,
        APPROVED,
        DISMISSED
    }

    enum PullRequestState {
        DRAFT,
        OPEN,
        MERGED,
        CLOSED
    }

    enum RequiredCondition {
        APPROVAL_THRESHOLD,
        STATUS_CHECKS,
        NO_CONFLICT,
        NON_DRAFT,
        LINEAR_HISTORY
    }

    record Review(String reviewer, ReviewState state, boolean eligibleReviewer) {
        Review {
            Objects.requireNonNull(reviewer);
            Objects.requireNonNull(state);
            if (reviewer.isBlank()) {
                throw new IllegalArgumentException("Reviewer name cannot be blank.");
            }
        }
    }

    record BranchProtection(
            String branch,
            int requiredApprovals,
            boolean requiredChecks,
            boolean prohibitForcePush,
            boolean requireLinearHistory) {

        BranchProtection {
            if (branch == null || branch.isBlank()) {
                throw new IllegalArgumentException("Protected branch is required.");
            }
            if (requiredApprovals < 0) {
                throw new IllegalArgumentException("Approval threshold cannot be negative.");
            }
        }

        Set<RequiredCondition> requiredConditions() {
            EnumSet<RequiredCondition> conditions =
                    EnumSet.of(RequiredCondition.NON_DRAFT,
                               RequiredCondition.NO_CONFLICT);

            if (requiredApprovals > 0) {
                conditions.add(RequiredCondition.APPROVAL_THRESHOLD);
            }
            if (requiredChecks) {
                conditions.add(RequiredCondition.STATUS_CHECKS);
            }
            if (requireLinearHistory) {
                conditions.add(RequiredCondition.LINEAR_HISTORY);
            }

            return conditions;
        }
    }

    static final class PullRequest {
        private final int id;
        private final String sourceBranch;
        private final String targetBranch;
        private final List<String> commits;
        private final List<Review> reviews;
        private final List<Boolean> statusChecks;
        private PullRequestState state;
        private boolean mergeConflict;
        private boolean linearHistory;

        PullRequest(
                int id,
                String sourceBranch,
                String targetBranch,
                List<String> commits,
                List<Review> reviews,
                List<Boolean> statusChecks,
                PullRequestState state,
                boolean mergeConflict,
                boolean linearHistory) {

            if (id <= 0) {
                throw new IllegalArgumentException("Pull Request ID must be positive.");
            }

            if (sourceBranch == null || targetBranch == null ||
                    sourceBranch.isBlank() || targetBranch.isBlank()) {
                throw new IllegalArgumentException("Both branches are required.");
            }

            this.id = id;
            this.sourceBranch = sourceBranch;
            this.targetBranch = targetBranch;
            this.commits = List.copyOf(commits);
            this.reviews = List.copyOf(reviews);
            this.statusChecks = List.copyOf(statusChecks);
            this.state = Objects.requireNonNull(state);
            this.mergeConflict = mergeConflict;
            this.linearHistory = linearHistory;
        }

        int id() {
            return id;
        }

        String targetBranch() {
            return targetBranch;
        }

        List<Review> reviews() {
            return reviews;
        }

        List<Boolean> statusChecks() {
            return statusChecks;
        }

        boolean mergeConflict() {
            return mergeConflict;
        }

        boolean linearHistory() {
            return linearHistory;
        }

        PullRequestState state() {
            return state;
        }

        void markConflict(boolean value) {
            mergeConflict = value;
        }

        void setLinearHistory(boolean value) {
            linearHistory = value;
        }

        void transitionTo(PullRequestState next) {
            Objects.requireNonNull(next);

            if (state == PullRequestState.MERGED ||
                    state == PullRequestState.CLOSED) {
                throw new IllegalStateException(
                        "A merged or closed Pull Request cannot be reopened by this transition.");
            }

            if (next == PullRequestState.MERGED) {
                throw new IllegalStateException(
                        "Merge must pass through MergeEligibilityService.");
            }

            state = next;
        }
    }

    record MergeResult(boolean eligible, List<String> failures) {
        MergeResult {
            failures = List.copyOf(failures);
        }
    }

    static final class MergeEligibilityService {

        MergeResult evaluate(
                PullRequest pullRequest,
                BranchProtection policy) {

            List<String> failures = new ArrayList<>();

            if (!pullRequest.targetBranch().equals(policy.branch())) {
                failures.add("The Pull Request does not target the protected branch.");
            }

            if (pullRequest.state() == PullRequestState.DRAFT) {
                failures.add("Draft Pull Requests are not mergeable.");
            }

            if (pullRequest.commits.isEmpty()) {
                failures.add("The Pull Request has no commits.");
            }

            if (pullRequest.mergeConflict()) {
                failures.add("The Pull Request has unresolved conflicts.");
            }

            long approvals = pullRequest.reviews().stream()
                    .filter(review -> review.eligibleReviewer())
                    .filter(review -> review.state() == ReviewState.APPROVED)
                    .count();

            if (approvals < policy.requiredApprovals()) {
                failures.add(
                        "Approval requirement is not satisfied: " +
                        approvals + "/" + policy.requiredApprovals());
            }

            if (policy.requiredChecks() &&
                    (pullRequest.statusChecks().isEmpty() ||
                     pullRequest.statusChecks().stream().anyMatch(result -> !result))) {
                failures.add("Required status checks are not successful.");
            }

            if (policy.requireLinearHistory() && !pullRequest.linearHistory()) {
                failures.add("Protected branch requires linear history.");
            }

            return new MergeResult(failures.isEmpty(), failures);
        }
    }

    static int[] nextGreaterRight(int[] values) {
        int[] answer = new int[values.length];
        java.util.Arrays.fill(answer, -1);

        Deque<Integer> stack = new ArrayDeque<>();

        for (int i = 0; i < values.length; i++) {
            while (!stack.isEmpty() &&
                    values[stack.peek()] < values[i]) {
                answer[stack.pop()] = values[i];
            }
            stack.push(i);
        }

        return answer;
    }

    static long largestHistogramRectangle(int[] heights) {
        Deque<Integer> stack = new ArrayDeque<>();
        long best = 0;

        for (int i = 0; i <= heights.length; i++) {
            int current = i == heights.length ? 0 : heights[i];

            while (!stack.isEmpty() && heights[stack.peek()] > current) {
                int top = stack.pop();
                int left = stack.isEmpty() ? 0 : stack.peek() + 1;
                int width = i - left;
                best = Math.max(best, (long) heights[top] * width);
            }

            stack.push(i);
        }

        return best;
    }

    public static void main(String[] args) {
        int[] measurements = {2, 1, 2, 4, 3};
        System.out.println(
                "Next greater values: " +
                java.util.Arrays.toString(nextGreaterRight(measurements)));

        int[] histogram = {2, 1, 5, 6, 2, 3};
        System.out.println(
                "Largest histogram area: " +
                largestHistogramRectangle(histogram));

        PullRequest pullRequest = new PullRequest(
                418,
                "feature/repository-governance",
                "main",
                List.of("a91", "a92", "a93"),
                List.of(
                        new Review("alice", ReviewState.APPROVED, true),
                        new Review("bob", ReviewState.APPROVED, true),
                        new Review("carol", ReviewState.COMMENTED, true)
                ),
                List.of(true, true, true),
                PullRequestState.OPEN,
                false,
                true
        );

        BranchProtection protection = new BranchProtection(
                "main",
                2,
                true,
                true,
                true
        );

        MergeEligibilityService service = new MergeEligibilityService();
        MergeResult result = service.evaluate(pullRequest, protection);

        System.out.println("\nProtected branch conditions:");
        System.out.println(protection.requiredConditions());
        System.out.println("Pull Request #" + pullRequest.id());
        System.out.println("Merge eligible: " + result.eligible());

        if (!result.eligible()) {
            result.failures().forEach(failure -> System.out.println("Failure: " + failure));
        }

        pullRequest.markConflict(true);
        result = service.evaluate(pullRequest, protection);

        System.out.println("\nAfter conflict introduction:");
        System.out.println("Merge eligible: " + result.eligible());
        result.failures().forEach(failure -> System.out.println("Failure: " + failure));
    }
}
