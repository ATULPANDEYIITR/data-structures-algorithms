#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>

using int64 = std::int64_t;

class ValidationError : public std::invalid_argument {
public:
    explicit ValidationError(const std::string& message)
        : std::invalid_argument(message) {}
};

template <typename Predicate>
int64 first_true(int64 low, int64 high, Predicate feasible) {
    int64 answer = -1;

    while (low <= high) {
        // This form avoids low + high overflowing signed integer limits.
        const int64 mid = low + (high - low) / 2;

        if (feasible(mid)) {
            answer = mid;
            high = mid - 1;
        } else {
            low = mid + 1;
        }
    }

    return answer;
}

template <typename Predicate>
int64 last_true(int64 low, int64 high, Predicate feasible) {
    int64 answer = -1;

    while (low <= high) {
        const int64 mid = low + (high - low) / 2;

        if (feasible(mid)) {
            answer = mid;
            low = mid + 1;
        } else {
            high = mid - 1;
        }
    }

    return answer;
}

void validate_positive(const std::vector<int64>& values,
                       const std::string& name) {
    if (values.empty()) {
        throw ValidationError(name + " must not be empty");
    }

    for (const int64 value : values) {
        if (value <= 0) {
            throw ValidationError(name + " must contain positive values");
        }
    }
}

class MergeEligibilityEngine {
private:
    std::vector<int64> commits_;
    int required_reviews_;
    int required_checks_;

public:
    MergeEligibilityEngine(
        std::vector<int64> commits,
        int required_reviews,
        int required_checks)
        : commits_(std::move(commits)),
          required_reviews_(required_reviews),
          required_checks_(required_checks) {

        validate_positive(commits_, "commits");

        if (required_reviews < 0 || required_checks < 0) {
            throw ValidationError("requirements cannot be negative");
        }
    }

    /*
     * This method represents a repository capacity policy:
     * determine the smallest per-worker capacity that can process
     * the ordered commit-validation workload.
     *
     * The same binary-search-on-answer technique used for algorithmic
     * allocation problems applies to governance workloads.
     */
    int64 minimumValidationCapacity(int workers) const {
        if (workers <= 0 ||
            workers > static_cast<int>(commits_.size())) {
            throw ValidationError("invalid worker count");
        }

        const int64 lower =
            *std::max_element(commits_.begin(), commits_.end());

        const int64 upper =
            std::accumulate(commits_.begin(), commits_.end(), int64{0});

        return first_true(lower, upper, [&](int64 capacity) {
            int used_workers = 1;
            int64 current = 0;

            for (const int64 workload : commits_) {
                if (workload > capacity) {
                    return false;
                }

                if (current + workload <= capacity) {
                    current += workload;
                } else {
                    ++used_workers;
                    current = workload;

                    if (used_workers > workers) {
                        return false;
                    }
                }
            }

            return true;
        });
    }

    bool mergeEligible(
        bool source_branch_synced,
        bool conflicts_resolved,
        int approved_reviews,
        int successful_checks,
        int unresolved_conversations,
        bool protected_branch) const {

        if (!source_branch_synced || !conflicts_resolved) {
            return false;
        }

        if (approved_reviews < required_reviews_) {
            return false;
        }

        if (successful_checks < required_checks_) {
            return false;
        }

        if (unresolved_conversations > 0) {
            return false;
        }

        if (!protected_branch) {
            return true;
        }

        return approved_reviews >= required_reviews_ &&
               successful_checks >= required_checks_;
    }
};

class AllocationSolver {
public:
    static int64 minimumShippingCapacity(
        const std::vector<int64>& weights,
        int days) {

        validate_positive(weights, "weights");

        if (days <= 0) {
            throw ValidationError("days must be positive");
        }

        days = std::min(days, static_cast<int>(weights.size()));

        const int64 lower =
            *std::max_element(weights.begin(), weights.end());

        const int64 upper =
            std::accumulate(weights.begin(), weights.end(), int64{0});

        return first_true(lower, upper, [&](int64 capacity) {
            int used_days = 1;
            int64 load = 0;

            for (const int64 weight : weights) {
                if (weight > capacity) {
                    return false;
                }

                if (load + weight <= capacity) {
                    load += weight;
                } else {
                    ++used_days;
                    load = weight;

                    if (used_days > days) {
                        return false;
                    }
                }
            }

            return true;
        });
    }

    static int64 maximizeMinimumDistance(
        std::vector<int64> stalls,
        int cows) {

        validate_positive(stalls, "stalls");

        if (cows < 2 ||
            cows > static_cast<int>(stalls.size())) {
            throw ValidationError("invalid cow count");
        }

        std::sort(stalls.begin(), stalls.end());

        return last_true(
            0,
            stalls.back() - stalls.front(),
            [&](int64 distance) {
                int placed = 1;
                int64 last = stalls.front();

                for (std::size_t i = 1; i < stalls.size(); ++i) {
                    if (stalls[i] - last >= distance) {
                        ++placed;
                        last = stalls[i];

                        if (placed >= cows) {
                            return true;
                        }
                    }
                }

                return false;
            });
    }
};

int main() {
    try {
        std::cout
            << "Minimum shipping capacity: "
            << AllocationSolver::minimumShippingCapacity(
                   {1, 2, 3, 1, 1, 1, 1}, 4)
            << '\n';

        std::cout
            << "Maximum minimum distance: "
            << AllocationSolver::maximizeMinimumDistance(
                   {1, 2, 4, 8, 9}, 3)
            << '\n';

        MergeEligibilityEngine engine(
            {8, 5, 7, 4, 6},
            2,
            3
        );

        std::cout
            << "Minimum validation capacity with 3 workers: "
            << engine.minimumValidationCapacity(3)
            << '\n';

        const bool eligible = engine.mergeEligible(
            true,
            true,
            2,
            3,
            0,
            true
        );

        std::cout
            << "Protected-branch merge eligible: "
            << std::boolalpha
            << eligible
            << '\n';

        assert(
            AllocationSolver::minimumShippingCapacity(
                {5}, 1) == 5
        );

        assert(
            AllocationSolver::maximizeMinimumDistance(
                {1, 2}, 2) == 1
        );

        assert(
            engine.minimumValidationCapacity(3) == 13
        );

        assert(
            engine.mergeEligible(
                true, true, 2, 3, 0, true
            )
        );

        assert(
            !engine.mergeEligible(
                true, true, 1, 3, 0, true
            )
        );

    } catch (const std::exception& error) {
        std::cerr << "Failure: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
