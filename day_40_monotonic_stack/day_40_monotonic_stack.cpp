#include <algorithm>
#include <iomanip>
#include <iostream>
#include <limits>
#include <optional>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

using namespace std;

struct ReviewSignal {
    string reviewer;
    int approvalWeight;
    bool approved;
};

struct PullRequest {
    int id;
    string sourceBranch;
    string targetBranch;
    vector<int> commits;
    vector<ReviewSignal> reviews;
    vector<int> statusCheckDurations;
    bool draft;
    bool mergeConflict;
};

struct BranchPolicy {
    string branch;
    int requiredApprovals;
    bool requireSuccessfulChecks;
    bool prohibitForcePush;
    bool requireLinearHistory;
    int maximumAllowedCheckDuration;
};

struct MergeDecision {
    bool eligible;
    string reason;
};

class MergeEligibilityEngine {
public:
    static bool hasRequiredApprovals(const PullRequest& pr,
                                     const BranchPolicy& policy) {
        int approvals = 0;

        for (const auto& review : pr.reviews) {
            if (review.approved) {
                approvals += review.approvalWeight;
            }
        }

        return approvals >= policy.requiredApprovals;
    }

    static bool checksPass(const PullRequest& pr,
                           const BranchPolicy& policy) {
        if (!policy.requireSuccessfulChecks) {
            return true;
        }

        if (pr.statusCheckDurations.empty()) {
            return false;
        }

        return all_of(
            pr.statusCheckDurations.begin(),
            pr.statusCheckDurations.end(),
            [&policy](int duration) {
                return duration >= 0 &&
                       duration <= policy.maximumAllowedCheckDuration;
            });
    }

    static MergeDecision evaluate(const PullRequest& pr,
                                  const BranchPolicy& policy) {
        if (pr.targetBranch != policy.branch) {
            return {false, "Pull Request targets a branch without this policy."};
        }

        if (pr.draft) {
            return {false, "Draft Pull Requests cannot be merged."};
        }

        if (pr.sourceBranch.empty() || pr.targetBranch.empty()) {
            return {false, "Source and target branches are required."};
        }

        if (pr.commits.empty()) {
            return {false, "Pull Request contains no commits."};
        }

        if (pr.mergeConflict) {
            return {false, "Pull Request has unresolved merge conflicts."};
        }

        if (!hasRequiredApprovals(pr, policy)) {
            return {false, "Required approval threshold has not been met."};
        }

        if (!checksPass(pr, policy)) {
            return {false, "Required status checks are missing or failing."};
        }

        return {true, "Pull Request satisfies the configured merge policy."};
    }
};

class NextGreaterResolver {
public:
    static vector<int> resolve(const vector<int>& values) {
        vector<int> answer(values.size(), -1);
        vector<size_t> unresolved;

        for (size_t i = 0; i < values.size(); ++i) {
            while (!unresolved.empty() &&
                   values[unresolved.back()] < values[i]) {
                answer[unresolved.back()] = values[i];
                unresolved.pop_back();
            }

            unresolved.push_back(i);
        }

        return answer;
    }
};

class HistogramRiskAnalyzer {
public:
    static pair<long long, pair<int, int>>
    largestRectangle(const vector<int>& heights) {
        if (any_of(heights.begin(), heights.end(),
                   [](int value) { return value < 0; })) {
            throw invalid_argument("Histogram heights cannot be negative.");
        }

        vector<int> extended = heights;
        extended.push_back(0);

        vector<int> stack;
        long long bestArea = 0;
        pair<int, int> bestRange{-1, -1};

        for (int i = 0; i < static_cast<int>(extended.size()); ++i) {
            while (!stack.empty() &&
                   extended[stack.back()] > extended[i]) {
                int top = stack.back();
                stack.pop_back();

                int left = stack.empty() ? 0 : stack.back() + 1;
                int right = i - 1;
                long long width = right - left + 1LL;
                long long area =
                    static_cast<long long>(extended[top]) * width;

                if (area > bestArea) {
                    bestArea = area;
                    bestRange = {left, right};
                }
            }

            stack.push_back(i);
        }

        return {bestArea, bestRange};
    }
};

static void printVector(const vector<int>& values) {
    cout << "[";
    for (size_t i = 0; i < values.size(); ++i) {
        if (i) {
            cout << ", ";
        }
        cout << values[i];
    }
    cout << "]\n";
}

static PullRequest makePullRequest() {
    PullRequest pr{
        418,
        "feature/review-policy-engine",
        "main",
        {8121, 8122, 8125},
        {
            {"reviewer-alice", 1, true},
            {"reviewer-bob", 1, true},
            {"reviewer-carol", 1, false}
        },
        {41, 58, 36},
        false,
        false
    };

    return pr;
}

int main() {
    try {
        cout << "Monotonic Stack and Repository Governance Case Study\n";
        cout << "====================================================\n\n";

        vector<int> values{2, 1, 2, 4, 3};
        cout << "Next greater values: ";
        printVector(NextGreaterResolver::resolve(values));

        /*
         * Histogram analysis demonstrates a second monotonic-stack pattern.
         * Here the bars represent consecutive status-check observations.
         * The rectangle identifies the strongest contiguous region satisfying
         * the same lower-bound metric.
         */
        vector<int> checkDurations{4, 4, 3, 3, 3, 5, 5, 2};
        auto rectangle =
            HistogramRiskAnalyzer::largestRectangle(checkDurations);

        cout << "Largest contiguous metric rectangle: "
             << rectangle.first << "\n";
        cout << "Rectangle range: ["
             << rectangle.second.first << ", "
             << rectangle.second.second << "]\n\n";

        PullRequest pr = makePullRequest();

        BranchPolicy mainPolicy{
            "main",
            2,
            true,
            true,
            true,
            120
        };

        MergeDecision decision =
            MergeEligibilityEngine::evaluate(pr, mainPolicy);

        cout << "Pull Request #" << pr.id << "\n";
        cout << "Source: " << pr.sourceBranch << "\n";
        cout << "Target: " << pr.targetBranch << "\n";
        cout << "Merge eligible: "
             << boolalpha << decision.eligible << "\n";
        cout << "Reason: " << decision.reason << "\n\n";

        /*
         * A branch policy is intentionally evaluated separately from the
         * stack algorithms. The stack answers local ordering/range questions;
         * policy evaluation answers governance questions.
         */
        pr.reviews[1].approved = false;

        decision = MergeEligibilityEngine::evaluate(pr, mainPolicy);
        cout << "After approval removal:\n";
        cout << "Merge eligible: " << decision.eligible << "\n";
        cout << "Reason: " << decision.reason << "\n";

        pr.reviews[1].approved = true;
        pr.mergeConflict = true;

        decision = MergeEligibilityEngine::evaluate(pr, mainPolicy);
        cout << "\nAfter introducing a conflict:\n";
        cout << "Merge eligible: " << decision.eligible << "\n";
        cout << "Reason: " << decision.reason << "\n";

        cout << "\nComplexity:\n";
        cout << "Next-greater stack: O(n) time and O(n) space.\n";
        cout << "Histogram rectangle: O(n) time and O(n) space.\n";
        cout << "Each input index is pushed once and popped at most once.\n";

    } catch (const exception& error) {
        cerr << "Execution error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
