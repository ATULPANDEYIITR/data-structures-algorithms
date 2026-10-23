import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Objects;
import java.util.function.LongPredicate;

public class BinarySearchOnAnswer {

    static class ValidationException extends IllegalArgumentException {
        ValidationException(String message) {
            super(message);
        }
    }

    enum ReviewState {
        DRAFT,
        OPEN,
        CHANGES_REQUESTED,
        APPROVED,
        MERGED,
        CLOSED
    }

    record ReviewPolicy(
            int requiredApprovals,
            int requiredStatusChecks,
            boolean requireSyncedBranch,
            boolean requireResolvedConversations) {

        ReviewPolicy {
            if (requiredApprovals < 0 ||
                requiredStatusChecks < 0) {
                throw new ValidationException(
                    "review requirements cannot be negative"
                );
            }
        }
    }

    record PullRequest(
            String sourceBranch,
            String targetBranch,
            ReviewState state,
            boolean conflictsResolved,
            boolean branchSynchronized,
            int approvals,
            int successfulChecks,
            int unresolvedConversations) {

        PullRequest {
            Objects.requireNonNull(sourceBranch);
            Objects.requireNonNull(targetBranch);
            Objects.requireNonNull(state);

            if (sourceBranch.isBlank() || targetBranch.isBlank()) {
                throw new ValidationException(
                    "branch names cannot be blank"
                );
            }

            if (approvals < 0 ||
                successfulChecks < 0 ||
                unresolvedConversations < 0) {
                throw new ValidationException(
                    "counts cannot be negative"
                );
            }
        }
    }

    static final class MergeEligibilityService {
        private final ReviewPolicy policy;

        MergeEligibilityService(ReviewPolicy policy) {
            this.policy = Objects.requireNonNull(policy);
        }

        boolean canMerge(PullRequest pullRequest) {
            if (pullRequest.state() != ReviewState.OPEN &&
                pullRequest.state() != ReviewState.APPROVED) {
                return false;
            }

            if (policy.requireSyncedBranch() &&
                !pullRequest.branchSynchronized()) {
                return false;
            }

            if (!pullRequest.conflictsResolved()) {
                return false;
            }

            if (pullRequest.approvals() <
                policy.requiredApprovals()) {
                return false;
            }

            if (pullRequest.successfulChecks() <
                policy.requiredStatusChecks()) {
                return false;
            }

            if (policy.requireResolvedConversations() &&
                pullRequest.unresolvedConversations() > 0) {
                return false;
            }

            return true;
        }
    }

    static long firstTrue(
            long low,
            long high,
            LongPredicate predicate) {

        long answer = -1;

        while (low <= high) {
            long middle = low + (high - low) / 2;

            if (predicate.test(middle)) {
                answer = middle;
                high = middle - 1;
            } else {
                low = middle + 1;
            }
        }

        return answer;
    }

    static long lastTrue(
            long low,
            long high,
            LongPredicate predicate) {

        long answer = -1;

        while (low <= high) {
            long middle = low + (high - low) / 2;

            if (predicate.test(middle)) {
                answer = middle;
                low = middle + 1;
            } else {
                high = middle - 1;
            }
        }

        return answer;
    }

    static List<Long> requirePositive(List<Long> values, String name) {
        if (values == null || values.isEmpty()) {
            throw new ValidationException(
                name + " cannot be empty"
            );
        }

        for (Long value : values) {
            if (value == null || value <= 0) {
                throw new ValidationException(
                    name + " must contain positive values"
                );
            }
        }

        return new ArrayList<>(values);
    }

    static long minimumShippingCapacity(
            List<Long> weights,
            int days) {

        List<Long> values =
            requirePositive(weights, "weights");

        if (days <= 0) {
            throw new ValidationException(
                "days must be positive"
            );
        }

        days = Math.min(days, values.size());

        long lower =
            values.stream().max(Comparator.naturalOrder()).orElseThrow();

        long upper =
            values.stream().mapToLong(Long::longValue).sum();

        final int allowedDays = days;

        return firstTrue(lower, upper, capacity -> {
            int usedDays = 1;
            long currentLoad = 0;

            for (long weight : values) {
                if (weight > capacity) {
                    return false;
                }

                if (currentLoad + weight <= capacity) {
                    currentLoad += weight;
                } else {
                    usedDays++;
                    currentLoad = weight;

                    if (usedDays > allowedDays) {
                        return false;
                    }
                }
            }

            return true;
        });
    }

    static long minimumProcessingCapacity(
            List<Long> workloads,
            int workers) {

        List<Long> values =
            requirePositive(workloads, "workloads");

        if (workers <= 0 || workers > values.size()) {
            throw new ValidationException(
                "workers must be within workload count"
            );
        }

        long lower =
            values.stream().max(Comparator.naturalOrder()).orElseThrow();

        long upper =
            values.stream().mapToLong(Long::longValue).sum();

        return firstTrue(lower, upper, capacity -> {
            int usedWorkers = 1;
            long current = 0;

            for (long workload : values) {
                if (workload > capacity) {
                    return false;
                }

                if (current + workload <= capacity) {
                    current += workload;
                } else {
                    usedWorkers++;
                    current = workload;

                    if (usedWorkers > workers) {
                        return false;
                    }
                }
            }

            return true;
        });
    }

    static long maximizeMinimumDistance(
            List<Long> positions,
            int reviewers) {

        List<Long> values =
            requirePositive(positions, "positions");

        if (reviewers < 2 || reviewers > values.size()) {
            throw new ValidationException(
                "reviewer count is invalid"
            );
        }

        values.sort(Comparator.naturalOrder());

        long lower = 0;
        long upper =
            values.get(values.size() - 1) - values.get(0);

        return lastTrue(lower, upper, distance -> {
            int placed = 1;
            long last = values.get(0);

            for (int i = 1; i < values.size(); i++) {
                long position = values.get(i);

                if (position - last >= distance) {
                    placed++;
                    last = position;

                    if (placed >= reviewers) {
                        return true;
                    }
                }
            }

            return false;
        });
    }

    public static void main(String[] args) {
        long shipping =
            minimumShippingCapacity(
                List.of(1L, 2L, 3L, 1L, 1L, 1L, 1L),
                4
            );

        long capacity =
            minimumProcessingCapacity(
                List.of(11L, 7L, 5L, 9L, 13L, 6L),
                3
            );

        long spacing =
            maximizeMinimumDistance(
                List.of(1L, 2L, 4L, 8L, 9L),
                3
            );

        System.out.println(
            "Minimum shipping capacity: " + shipping
        );

        System.out.println(
            "Minimum processing capacity: " + capacity
        );

        System.out.println(
            "Maximum minimum distance: " + spacing
        );

        ReviewPolicy policy = new ReviewPolicy(
            2,
            3,
            true,
            true
        );

        PullRequest pullRequest = new PullRequest(
            "feature/merge-policy",
            "main",
            ReviewState.APPROVED,
            true,
            true,
            2,
            3,
            0
        );

        MergeEligibilityService service =
            new MergeEligibilityService(policy);

        System.out.println(
            "Merge eligible: " + service.canMerge(pullRequest)
        );

        if (shipping != 3) {
            throw new AssertionError("Unexpected shipping result");
        }

        if (capacity != 20) {
            throw new AssertionError("Unexpected capacity result");
        }

        if (spacing != 3) {
            throw new AssertionError("Unexpected spacing result");
        }

        if (!service.canMerge(pullRequest)) {
            throw new AssertionError(
                "Expected pull request to be merge eligible"
            );
        }
    }
}
