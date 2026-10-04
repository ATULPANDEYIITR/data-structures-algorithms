import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import java.util.Random;
import java.util.Set;

public class LinkedListReversalEnterprise {

    enum ReversalMode {
        ITERATIVE,
        RECURSIVE,
        GROUP_ITERATIVE,
        GROUP_RECURSIVE
    }

    enum ReviewStatus {
        OPEN,
        CHANGES_REQUESTED,
        APPROVED
    }

    record ReviewDecision(String reviewer, ReviewStatus status, String reason) {
        ReviewDecision {
            Objects.requireNonNull(reviewer, "reviewer");
            Objects.requireNonNull(status, "status");
            Objects.requireNonNull(reason, "reason");

            if (reviewer.isBlank()) {
                throw new IllegalArgumentException("Reviewer name cannot be blank");
            }
        }
    }

    static final class ChangeNode {
        private final int sequence;
        private final String change;
        private ChangeNode next;

        ChangeNode(int sequence, String change) {
            if (sequence < 0) {
                throw new IllegalArgumentException("Sequence cannot be negative");
            }

            if (change == null || change.isBlank()) {
                throw new IllegalArgumentException("Change description is required");
            }

            this.sequence = sequence;
            this.change = change;
        }
    }

    static final class ReviewChangeList {
        private ChangeNode head;
        private ChangeNode tail;
        private int size;

        void append(int sequence, String change) {
            ChangeNode node = new ChangeNode(sequence, change);

            if (head == null) {
                head = node;
                tail = node;
            } else {
                tail.next = node;
                tail = node;
            }

            size++;
        }

        List<Integer> sequences() {
            List<Integer> result = new ArrayList<>(size);
            Set<ChangeNode> visited = new HashSet<>();

            ChangeNode current = head;

            while (current != null) {
                if (!visited.add(current)) {
                    throw new IllegalStateException("Cycle detected");
                }

                result.add(current.sequence);
                current = current.next;
            }

            return result;
        }

        void validate() {
            int count = 0;
            ChangeNode current = head;
            ChangeNode last = null;
            Set<ChangeNode> visited = new HashSet<>();

            while (current != null) {
                if (!visited.add(current)) {
                    throw new IllegalStateException("List contains a cycle");
                }

                count++;
                last = current;
                current = current.next;
            }

            if (count != size) {
                throw new IllegalStateException(
                    "Stored size does not match actual node count"
                );
            }

            if (last != tail) {
                throw new IllegalStateException("Tail invariant violated");
            }

            if (tail != null && tail.next != null) {
                throw new IllegalStateException("Tail must terminate the list");
            }
        }

        void reverseIterative() {
            ChangeNode previous = null;
            ChangeNode current = head;
            ChangeNode oldHead = head;

            while (current != null) {
                ChangeNode next = current.next;
                current.next = previous;
                previous = current;
                current = next;
            }

            head = previous;
            tail = oldHead;
        }

        void reverseRecursive() {
            ChangeNode oldHead = head;
            head = reverseRecursive(head, null);
            tail = oldHead;
        }

        private ChangeNode reverseRecursive(
            ChangeNode current,
            ChangeNode previous
        ) {
            if (current == null) {
                return previous;
            }

            ChangeNode next = current.next;
            current.next = previous;

            return reverseRecursive(next, current);
        }

        void reverseInGroups(int groupSize) {
            requireValidGroupSize(groupSize);

            if (groupSize == 1 || head == null) {
                return;
            }

            ChangeNode dummy = new ChangeNode(0, "sentinel");
            dummy.next = head;

            ChangeNode groupPrevious = dummy;

            while (true) {
                ChangeNode kth = groupPrevious;

                for (int i = 0; i < groupSize; i++) {
                    kth = kth.next;

                    if (kth == null) {
                        head = dummy.next;
                        recomputeTail();
                        return;
                    }
                }

                ChangeNode groupNext = kth.next;
                ChangeNode previous = groupNext;
                ChangeNode current = groupPrevious.next;

                while (current != groupNext) {
                    ChangeNode next = current.next;
                    current.next = previous;
                    previous = current;
                    current = next;
                }

                ChangeNode oldGroupHead = groupPrevious.next;
                groupPrevious.next = kth;
                groupPrevious = oldGroupHead;
            }
        }

        void reverseInGroupsRecursively(int groupSize) {
            requireValidGroupSize(groupSize);

            if (groupSize == 1 || head == null) {
                return;
            }

            ChangeNode oldHead = head;
            head = reverseGroups(head, groupSize);
            tail = oldHead;
            recomputeTail();
        }

        private ChangeNode reverseGroups(
            ChangeNode groupHead,
            int groupSize
        ) {
            ChangeNode probe = groupHead;

            for (int i = 0; i < groupSize; i++) {
                if (probe == null) {
                    return groupHead;
                }
                probe = probe.next;
            }

            ChangeNode previous = null;
            ChangeNode current = groupHead;

            for (int i = 0; i < groupSize; i++) {
                ChangeNode next = current.next;
                current.next = previous;
                previous = current;
                current = next;
            }

            groupHead.next = reverseGroups(current, groupSize);
            return previous;
        }

        private static void requireValidGroupSize(int groupSize) {
            if (groupSize <= 0) {
                throw new IllegalArgumentException(
                    "Group size must be positive"
                );
            }
        }

        private void recomputeTail() {
            if (head == null) {
                tail = null;
                return;
            }

            ChangeNode current = head;

            while (current.next != null) {
                current = current.next;
            }

            tail = current;
        }
    }

    static final class ReviewPolicy {
        private final int requiredApprovals;
        private final Set<String> eligibleReviewers;
        private final boolean rejectChangesRequested;
        private final boolean requireCleanStatus;

        ReviewPolicy(
            int requiredApprovals,
            Set<String> eligibleReviewers,
            boolean rejectChangesRequested,
            boolean requireCleanStatus
        ) {
            if (requiredApprovals < 0) {
                throw new IllegalArgumentException(
                    "Required approvals cannot be negative"
                );
            }

            this.requiredApprovals = requiredApprovals;
            this.eligibleReviewers = Set.copyOf(eligibleReviewers);
            this.rejectChangesRequested = rejectChangesRequested;
            this.requireCleanStatus = requireCleanStatus;
        }

        boolean canMerge(
            List<ReviewDecision> decisions,
            boolean statusChecksPassed
        ) {
            if (requireCleanStatus && !statusChecksPassed) {
                return false;
            }

            if (rejectChangesRequested &&
                decisions.stream().anyMatch(
                    decision -> decision.status() == ReviewStatus.CHANGES_REQUESTED
                )) {
                return false;
            }

            long validApprovals = decisions.stream()
                .filter(decision -> decision.status() == ReviewStatus.APPROVED)
                .filter(decision -> eligibleReviewers.contains(decision.reviewer()))
                .map(ReviewDecision::reviewer)
                .distinct()
                .count();

            return validApprovals >= requiredApprovals;
        }
    }

    static final class RepositoryGovernanceService {
        private final ReviewPolicy policy;

        RepositoryGovernanceService(ReviewPolicy policy) {
            this.policy = Objects.requireNonNull(policy);
        }

        boolean evaluateMerge(
            ReviewChangeList changes,
            List<ReviewDecision> decisions,
            boolean statusChecksPassed
        ) {
            changes.validate();

            return policy.canMerge(decisions, statusChecksPassed);
        }
    }

    private static List<Integer> expectedGroups(
        List<Integer> input,
        int groupSize
    ) {
        List<Integer> expected = new ArrayList<>(input);

        for (int start = 0;
             start + groupSize <= expected.size();
             start += groupSize) {

            Collections.reverse(
                expected.subList(start, start + groupSize)
            );
        }

        return expected;
    }

    private static void assertEqual(
        List<Integer> actual,
        List<Integer> expected,
        String operation
    ) {
        if (!actual.equals(expected)) {
            throw new IllegalStateException(
                operation + " failed. Expected "
                + expected + ", actual " + actual
            );
        }
    }

    private static ReviewChangeList createChanges(int count) {
        ReviewChangeList list = new ReviewChangeList();

        for (int i = 1; i <= count; i++) {
            list.append(i, "review-change-" + i);
        }

        return list;
    }

    private static void demonstrateReversalModes() {
        System.out.println("\n=== Enterprise review changeset reversal ===");

        ReviewChangeList iterative = createChanges(6);
        iterative.reverseIterative();
        iterative.validate();

        System.out.println("Iterative: " + iterative.sequences());

        ReviewChangeList recursive = createChanges(6);
        recursive.reverseRecursive();
        recursive.validate();

        System.out.println("Recursive: " + recursive.sequences());

        assertEqual(
            iterative.sequences(),
            List.of(6, 5, 4, 3, 2, 1),
            "Iterative reversal"
        );

        assertEqual(
            recursive.sequences(),
            List.of(6, 5, 4, 3, 2, 1),
            "Recursive reversal"
        );
    }

    private static void demonstrateGroupProcessing() {
        System.out.println("\n=== Review-batch group reversal ===");

        ReviewChangeList iterative = createChanges(8);
        iterative.reverseInGroups(3);
        iterative.validate();

        System.out.println(
            "Iterative groups: " + iterative.sequences()
        );

        ReviewChangeList recursive = createChanges(8);
        recursive.reverseInGroupsRecursively(3);
        recursive.validate();

        System.out.println(
            "Recursive groups: " + recursive.sequences()
        );

        List<Integer> original =
            List.of(1, 2, 3, 4, 5, 6, 7, 8);

        List<Integer> expected = expectedGroups(original, 3);

        assertEqual(
            iterative.sequences(),
            expected,
            "Iterative group reversal"
        );

        assertEqual(
            recursive.sequences(),
            expected,
            "Recursive group reversal"
        );
    }

    private static void demonstrateGovernanceIntegration() {
        System.out.println("\n=== Review-policy integration ===");

        ReviewPolicy policy = new ReviewPolicy(
            2,
            Set.of("alice", "bob", "carol"),
            true,
            true
        );

        RepositoryGovernanceService service =
            new RepositoryGovernanceService(policy);

        ReviewChangeList changes = createChanges(5);

        List<ReviewDecision> approvedReviews = List.of(
            new ReviewDecision("alice", ReviewStatus.APPROVED, "Reviewed"),
            new ReviewDecision("bob", ReviewStatus.APPROVED, "Reviewed")
        );

        boolean eligible = service.evaluateMerge(
            changes,
            approvedReviews,
            true
        );

        System.out.println("Two eligible approvals + green checks: " + eligible);

        List<ReviewDecision> blockedByChangesRequested = List.of(
            new ReviewDecision("alice", ReviewStatus.APPROVED, "Reviewed"),
            new ReviewDecision(
                "bob",
                ReviewStatus.CHANGES_REQUESTED,
                "Fix validation"
            ),
            new ReviewDecision("carol", ReviewStatus.APPROVED, "Reviewed")
        );

        boolean blocked = service.evaluateMerge(
            changes,
            blockedByChangesRequested,
            true
        );

        System.out.println(
            "Changes requested blocks merge: " + !blocked
        );
    }

    private static void demonstrateFailureHandling() {
        System.out.println("\n=== Domain validation ===");

        ReviewChangeList changes = createChanges(4);

        try {
            changes.reverseInGroups(0);
        } catch (IllegalArgumentException error) {
            System.out.println("Invalid group size rejected: " + error.getMessage());
        }

        try {
            changes.reverseInGroupsRecursively(-2);
        } catch (IllegalArgumentException error) {
            System.out.println("Negative group size rejected: " + error.getMessage());
        }

        changes.validate();
        System.out.println("Original list remains valid: " + changes.sequences());
    }

    private static void randomizedChecks() {
        System.out.println("\n=== Randomized correctness checks ===");

        Random random = new Random(20261005);

        for (int test = 0; test < 300; test++) {
            int length = random.nextInt(31);

            ReviewChangeList iterative = createChanges(length);
            List<Integer> original = iterative.sequences();

            iterative.reverseIterative();
            iterative.validate();

            List<Integer> expectedReverse = new ArrayList<>(original);
            Collections.reverse(expectedReverse);

            assertEqual(
                iterative.sequences(),
                expectedReverse,
                "Random iterative reversal"
            );

            int groupSize = 1 + random.nextInt(10);

            ReviewChangeList grouped = createChanges(length);
            grouped.reverseInGroups(groupSize);
            grouped.validate();

            assertEqual(
                grouped.sequences(),
                expectedGroups(original, groupSize),
                "Random group reversal"
            );
        }

        System.out.println("300 randomized cases passed.");
    }

    private static void printComplexity() {
        System.out.println("\n=== Complexity ===");
        System.out.println(
            "Iterative reversal: O(n) time, O(1) auxiliary space"
        );
        System.out.println(
            "Recursive reversal: O(n) time, O(n) call-stack space"
        );
        System.out.println(
            "Iterative group reversal: O(n) time, O(1) auxiliary space"
        );
        System.out.println(
            "Recursive group reversal: O(n) time, O(n/k) call-stack space"
        );
        System.out.println(
            "Enterprise rule evaluation is O(r) for r review decisions."
        );
    }

    public static void main(String[] args) {
        demonstrateReversalModes();
        demonstrateGroupProcessing();
        demonstrateGovernanceIntegration();
        demonstrateFailureHandling();
        randomizedChecks();
        printComplexity();

        System.out.println(
            "\nAll Java 17 linked-list reversal demonstrations passed."
        );
    }
}
