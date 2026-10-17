import java.math.BigInteger;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/*
 * Basic Recursion Problems
 *
 * Enterprise-oriented case study: review effort estimation for a
 * repository pull request with a hierarchy of changed components.
 *
 * Java 17 or later:
 *     javac RecursionGovernance.java
 *     java RecursionGovernance
 *
 * BigInteger prevents integer overflow for exact factorial, Fibonacci,
 * and integer power calculations. Domain types keep repository review
 * state separate from the mathematical recursion mechanisms.
 */

public class RecursionGovernance {

    enum ReviewState {
        COMMENTED,
        APPROVED,
        CHANGES_REQUESTED,
        DISMISSED
    }

    enum PullRequestStatus {
        DRAFT,
        OPEN,
        MERGED,
        CLOSED
    }

    record Review(
        String reviewer,
        ReviewState state,
        boolean eligible,
        boolean stale
    ) {
        Review {
            if (reviewer == null || reviewer.isBlank()) {
                throw new IllegalArgumentException("Reviewer is required.");
            }
            Objects.requireNonNull(state, "Review state is required.");
        }

        boolean countsAsApproval() {
            return eligible && !stale && state == ReviewState.APPROVED;
        }
    }

    record BranchPolicy(
        int requiredApprovals,
        boolean requirePassingChecks,
        boolean requireResolvedDiscussions,
        boolean disallowDrafts
    ) {
        BranchPolicy {
            if (requiredApprovals < 0) {
                throw new IllegalArgumentException(
                    "Required approvals cannot be negative."
                );
            }
        }
    }

    record ChangeNode(
        String path,
        int risk,
        List<ChangeNode> children
    ) {
        ChangeNode {
            if (path == null || path.isBlank()) {
                throw new IllegalArgumentException("Change path is required.");
            }
            if (risk < 0 || risk > 100) {
                throw new IllegalArgumentException(
                    "Risk must be between 0 and 100."
                );
            }
            children = List.copyOf(
                Objects.requireNonNull(children, "Children are required.")
            );
        }
    }

    static final class PullRequest {
        private final int id;
        private final String sourceBranch;
        private final String targetBranch;
        private final List<ChangeNode> changes;
        private final List<Review> reviews = new ArrayList<>();

        private PullRequestStatus status;
        private boolean checksPassed;
        private boolean discussionsResolved;
        private boolean conflicts;

        PullRequest(
            int id,
            String sourceBranch,
            String targetBranch,
            List<ChangeNode> changes
        ) {
            if (id <= 0) {
                throw new IllegalArgumentException(
                    "Pull request ID must be positive."
                );
            }
            if (sourceBranch == null || sourceBranch.isBlank() ||
                targetBranch == null || targetBranch.isBlank()) {
                throw new IllegalArgumentException(
                    "Source and target branches are required."
                );
            }
            if (sourceBranch.equals(targetBranch)) {
                throw new IllegalArgumentException(
                    "Source and target branches must differ."
                );
            }

            this.id = id;
            this.sourceBranch = sourceBranch;
            this.targetBranch = targetBranch;
            this.changes = List.copyOf(changes);
            this.status = PullRequestStatus.OPEN;
        }

        void addReview(Review review) {
            if (status != PullRequestStatus.OPEN &&
                status != PullRequestStatus.DRAFT) {
                throw new IllegalStateException(
                    "Reviews cannot be added to a closed or merged request."
                );
            }
            reviews.add(Objects.requireNonNull(review));
        }

        void markDraft() {
            if (status != PullRequestStatus.OPEN) {
                throw new IllegalStateException(
                    "Only an open request can become a draft."
                );
            }
            status = PullRequestStatus.DRAFT;
        }

        void markReadyForReview() {
            if (status != PullRequestStatus.DRAFT) {
                throw new IllegalStateException(
                    "Only a draft can be marked ready for review."
                );
            }
            status = PullRequestStatus.OPEN;
        }

        void setChecksPassed(boolean value) {
            checksPassed = value;
        }

        void setDiscussionsResolved(boolean value) {
            discussionsResolved = value;
        }

        void setConflicts(boolean value) {
            conflicts = value;
        }

        long eligibleApprovalCount() {
            return reviews.stream()
                .filter(Review::countsAsApproval)
                .count();
        }

        int id() {
            return id;
        }

        PullRequestStatus status() {
            return status;
        }

        List<ChangeNode> changes() {
            return changes;
        }

        boolean checksPassed() {
            return checksPassed;
        }

        boolean discussionsResolved() {
            return discussionsResolved;
        }

        boolean conflicts() {
            return conflicts;
        }

        void merge() {
            if (status != PullRequestStatus.OPEN) {
                throw new IllegalStateException(
                    "Only an open pull request can be merged."
                );
            }
            status = PullRequestStatus.MERGED;
        }
    }

    static final class Recursion {
        private Recursion() {}

        static BigInteger factorial(int n) {
            if (n < 0) {
                throw new IllegalArgumentException(
                    "Factorial requires a non-negative integer."
                );
            }
            if (n <= 1) {
                return BigInteger.ONE;
            }
            return BigInteger.valueOf(n).multiply(factorial(n - 1));
        }

        static BigInteger fibonacci(int n) {
            if (n < 0) {
                throw new IllegalArgumentException(
                    "The Fibonacci index cannot be negative."
                );
            }
            return fibonacciMemoized(n, new HashMap<>());
        }

        private static BigInteger fibonacciMemoized(
            int n,
            Map<Integer, BigInteger> cache
        ) {
            if (n <= 1) {
                return BigInteger.valueOf(n);
            }

            BigInteger cached = cache.get(n);
            if (cached != null) {
                return cached;
            }

            BigInteger result = fibonacciMemoized(n - 1, cache)
                .add(fibonacciMemoized(n - 2, cache));

            cache.put(n, result);
            return result;
        }

        static BigInteger power(BigInteger base, int exponent) {
            Objects.requireNonNull(base, "Base is required.");

            if (base.signum() == 0 && exponent < 0) {
                throw new ArithmeticException(
                    "Zero cannot have a negative exponent."
                );
            }

            BigInteger magnitude = positivePower(
                base,
                Math.abs((long) exponent)
            );

            if (exponent >= 0) {
                return magnitude;
            }

            // BigInteger cannot represent fractional values. This method
            // therefore requires exact integer output and rejects reciprocals.
            throw new ArithmeticException(
                "Negative powers require rational-number representation."
            );
        }

        private static BigInteger positivePower(
            BigInteger base,
            long exponent
        ) {
            if (exponent == 0) {
                return BigInteger.ONE;
            }

            BigInteger half = positivePower(base, exponent / 2);
            BigInteger square = half.multiply(half);

            return exponent % 2 == 0
                ? square
                : square.multiply(base);
        }

        static int digitSum(long value) {
            // Converting to text handles Long.MIN_VALUE without overflow
            // from Math.abs(Long.MIN_VALUE).
            String digits = Long.toString(value).replace("-", "");
            return digitSumText(digits, 0);
        }

        private static int digitSumText(String digits, int index) {
            if (index == digits.length()) {
                return 0;
            }

            int digit = digits.charAt(index) - '0';
            return digit + digitSumText(digits, index + 1);
        }

        static String reverseDigits(String input) {
            if (input == null || input.isBlank()) {
                throw new IllegalArgumentException(
                    "A decimal integer string is required."
                );
            }

            boolean negative = input.charAt(0) == '-';
            int start = negative ? 1 : 0;

            if (start == input.length()) {
                throw new IllegalArgumentException("Missing digits.");
            }

            for (int i = start; i < input.length(); i++) {
                if (!Character.isDigit(input.charAt(i))) {
                    throw new IllegalArgumentException(
                        "Only decimal digits and an optional leading sign are allowed."
                    );
                }
            }

            String reversed = reverseText(input, start, input.length() - 1);
            int first = 0;

            while (first < reversed.length() - 1 &&
                   reversed.charAt(first) == '0') {
                first++;
            }

            return (negative ? "-" : "") + reversed.substring(first);
        }

        private static String reverseText(
            String input,
            int left,
            int right
        ) {
            if (left > right) {
                return "";
            }
            if (left == right) {
                return String.valueOf(input.charAt(left));
            }

            return input.charAt(right) +
                reverseText(input, left, right - 1);
        }

        static long sumArray(List<Integer> values, int index) {
            if (index < 0 || index > values.size()) {
                throw new IndexOutOfBoundsException(
                    "Invalid recursive traversal index."
                );
            }
            if (index == values.size()) {
                return 0L;
            }

            return values.get(index) + sumArray(values, index + 1);
        }

        static long totalRisk(List<ChangeNode> nodes) {
            return totalRiskAt(nodes, 0);
        }

        private static long totalRiskAt(
            List<ChangeNode> nodes,
            int index
        ) {
            if (index == nodes.size()) {
                return 0L;
            }

            ChangeNode node = nodes.get(index);

            return node.risk()
                + totalRisk(node.children())
                + totalRiskAt(nodes, index + 1);
        }

        static Optional<String> findPath(
            List<ChangeNode> nodes,
            String target
        ) {
            return findPathAt(nodes, target, 0);
        }

        private static Optional<String> findPathAt(
            List<ChangeNode> nodes,
            String target,
            int index
        ) {
            if (index == nodes.size()) {
                return Optional.empty();
            }

            ChangeNode node = nodes.get(index);

            if (node.path().equals(target)) {
                return Optional.of(node.path());
            }

            Optional<String> nested = findPath(node.children(), target);
            if (nested.isPresent()) {
                return nested;
            }

            return findPathAt(nodes, target, index + 1);
        }
    }

    static final class MergeEligibilityService {
        private final BranchPolicy policy;

        MergeEligibilityService(BranchPolicy policy) {
            this.policy = Objects.requireNonNull(policy);
        }

        List<String> blockers(PullRequest request) {
            List<String> reasons = new ArrayList<>();

            if (request.status() != PullRequestStatus.OPEN) {
                reasons.add("The pull request must be open and ready.");
            }

            if (policy.disallowDrafts() &&
                request.status() == PullRequestStatus.DRAFT) {
                reasons.add("Draft requests cannot be merged.");
            }

            if (request.conflicts()) {
                reasons.add("Merge conflicts remain.");
            }

            if (policy.requirePassingChecks() && !request.checksPassed()) {
                reasons.add("Required checks have not passed.");
            }

            if (policy.requireResolvedDiscussions() &&
                !request.discussionsResolved()) {
                reasons.add("Review discussions remain unresolved.");
            }

            if (request.eligibleApprovalCount() < policy.requiredApprovals()) {
                reasons.add("The eligible approval threshold is not met.");
            }

            return List.copyOf(reasons);
        }

        boolean mergeIfEligible(PullRequest request) {
            List<String> reasons = blockers(request);

            if (!reasons.isEmpty()) {
                System.out.println("Merge blocked for PR #" + request.id());
                reasons.forEach(reason -> System.out.println("  - " + reason));
                return false;
            }

            request.merge();
            System.out.println("PR #" + request.id() + " merged successfully.");
            return true;
        }
    }

    public static void main(String[] args) {
        System.out.println("Recursive mathematical operations");
        System.out.println("10! = " + Recursion.factorial(10));
        System.out.println("F(100) = " + Recursion.fibonacci(100));
        System.out.println("3^12 = " + Recursion.power(
            BigInteger.valueOf(3), 12
        ));
        System.out.println("Digit sum of -5821 = " + Recursion.digitSum(-5821));
        System.out.println("Reverse of 1200 = " +
            Recursion.reverseDigits("1200"));

        System.out.println("\nRepository change review");
        List<ChangeNode> changes = List.of(
            new ChangeNode(
                "src/security/session.java",
                8,
                List.of(
                    new ChangeNode("token-validation", 7, List.of()),
                    new ChangeNode("cookie-policy", 5, List.of())
                )
            ),
            new ChangeNode("tests/session-test.java", 2, List.of())
        );

        PullRequest request = new PullRequest(
            731,
            "feature/session-security",
            "main",
            changes
        );

        request.addReview(new Review(
            "reviewer-a", ReviewState.APPROVED, true, false
        ));
        request.addReview(new Review(
            "reviewer-b", ReviewState.APPROVED, true, true
        ));
        request.addReview(new Review(
            "reviewer-c", ReviewState.COMMENTED, true, false
        ));

        request.setChecksPassed(true);
        request.setDiscussionsResolved(false);
        request.setConflicts(false);

        BranchPolicy policy = new BranchPolicy(2, true, true, true);
        MergeEligibilityService service = new MergeEligibilityService(policy);

        System.out.println("Total changed-node risk: " +
            Recursion.totalRisk(request.changes()));
        System.out.println("Total array sum: " +
            Recursion.sumArray(List.of(12, 8, -3, 14), 0));
        System.out.println("Sensitive path: " +
            Recursion.findPath(request.changes(), "token-validation"));

        service.mergeIfEligible(request);

        // A stale approval does not count. Resolving discussions alone
        // therefore cannot make this request eligible.
        request.setDiscussionsResolved(true);
        service.mergeIfEligible(request);

        request.addReview(new Review(
            "reviewer-d", ReviewState.APPROVED, true, false
        ));
        service.mergeIfEligible(request);

        try {
            Recursion.factorial(-1);
        } catch (IllegalArgumentException error) {
            System.out.println("Rejected factorial input: " + error.getMessage());
        }

        try {
            request.markDraft();
        } catch (IllegalStateException error) {
            System.out.println("Rejected state transition: " + error.getMessage());
        }
    }
}
