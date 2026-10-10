# Monotonic Stack: Increasing and Decreasing Stacks

## Scope

A monotonic stack is a stack maintained in a specific ordering while an input sequence is scanned. The ordering is not simply a sorting operation. It is an invariant that determines which earlier elements can still be useful for a future query.

For an increasing monotonic stack, values are maintained in non-decreasing order from the bottom toward the top. When a smaller value arrives, larger values that can no longer be useful are removed.

For a decreasing monotonic stack, values are maintained in non-increasing order. When a larger value arrives, smaller values that can no longer satisfy the required relationship are removed.

The key property is that an element is normally pushed once and removed at most once. This converts many apparently quadratic nearest-neighbor problems into linear-time algorithms.

This repository focuses on three closely related problem families:

- next greater elements
- next smaller elements
- largest rectangles in histograms

The same stack invariant also supports daily-temperature waits, stock spans, circular next-greater queries, subarray minimum aggregation, and two-dimensional maximal-rectangle problems.

## Core Mechanism

Consider the sequence `2, 1, 2, 4, 3` and a next-greater-to-the-right query.

The stack stores indices whose answers are still unknown. When `4` is encountered, the unresolved indices whose values are smaller than `4` can immediately receive `4` as their next greater value.

The important operation is the repeated pop:

`while stack and value_at_top < current_value: pop`

The popped element has found its first greater value. Any element below it has not necessarily found its answer, so it remains on the stack.

The stack therefore contains unresolved candidates rather than all historical input values.

For next-smaller queries the comparison is reversed:

`while stack and value_at_top > current_value: pop`

This produces an increasing stack of unresolved candidates.

The direction of traversal and the strictness of comparisons determine whether the algorithm finds a next element, previous element, strictly greater element, greater-or-equal element, strictly smaller element, or smaller-or-equal element.

## Increasing and Decreasing Stack Invariants

An increasing stack is useful when smaller values terminate the usefulness of larger candidates. Typical operations include finding nearest smaller boundaries and constructing histogram boundaries.

A decreasing stack is useful when larger values terminate the usefulness of smaller candidates. Typical operations include next-greater-element and waiting-for-a-warmer-temperature problems.

The stack may contain values when only ordering matters, but it usually contains indices when the answer needs a position, distance, width, or range.

Duplicate values require particular care. For example, a minimum-subarray contribution algorithm can use a strict comparison on one side and a non-strict comparison on the other. This gives equal values a unique ownership rule instead of counting the same subarray multiple times.

## Next Greater and Next Smaller Elements

The Python implementation contains both value-oriented and index-oriented next-greater functions. The index version is more general because the index can be converted into a distance or used to inspect additional arrays.

For `next_greater_right`, an unresolved index remains on the stack until a later value is strictly larger. The resulting stack is decreasing in value order.

For `next_smaller_right`, the unresolved stack is increasing in value order because a smaller incoming value resolves larger candidates.

The JavaScript implementation uses arrays as explicit stacks. This is idiomatic for JavaScript because `push()` and `pop()` operate efficiently at the array's end. The code also demonstrates a circular next-greater problem by scanning two logical copies of the input without physically duplicating the array.

## Histogram Algorithm

The largest-rectangle-in-a-histogram problem is a central monotonic-stack application.

Given heights such as `2, 1, 5, 6, 2, 3`, every bar can be considered the limiting height of a rectangle. The challenge is finding how far that height can extend before a smaller bar appears on either side.

An increasing index stack identifies nearest smaller boundaries.

When a smaller current height arrives, the taller bar at the top of the stack has just discovered its right boundary. The element remaining below it identifies its left boundary.

For a popped index `i`:

- the rectangle height is `heights[i]`
- the right boundary is the current index minus one
- the left boundary is one position after the new stack top, or zero if the stack is empty
- the width is the distance between those boundaries
- the area is height multiplied by width

Appending a sentinel height of zero forces every remaining candidate to be processed at the end.

The Python program implements both a direct boundary-flushing version and an explicit previous-smaller/next-smaller version. The JavaScript implementation focuses on the direct form. The C++ and Java programs use the histogram operation as part of broader technical scenarios.

## Why Histogram Complexity Is Linear

A naive approach can examine every possible left and right boundary and therefore approach quadratic or cubic behavior.

The monotonic-stack approach is linear because each histogram index enters the stack once and leaves the stack at most once. The amount of work performed by all pop operations is therefore bounded by the number of input elements.

The resulting complexity is `O(n)` time and `O(n)` auxiliary space.

The same amortized argument applies to next-greater and next-smaller algorithms.

## Maximal Rectangle in a Binary Matrix

The Python implementation extends the histogram algorithm into two dimensions.

For every matrix row, each column stores the number of consecutive `1` cells ending at that row. A row therefore becomes a histogram.

For example, after processing several rows, a column height of `4` means four consecutive rows contain `1` in that column. The largest rectangle for that histogram represents a rectangular region of ones ending at the current row.

This converts the two-dimensional maximal-rectangle problem into repeated one-dimensional histogram problems.

## Subarray Ownership

Monotonic stacks can do more than locate boundaries. They can count how many subarrays treat an element as their minimum or maximum.

For a minimum contribution, an element at index `i` can own subarrays extending between its previous smaller boundary and its next smaller-or-equal boundary.

If the number of choices on the left is `L` and the number on the right is `R`, the element participates as the selected minimum in `L * R` subarrays.

The strict/non-strict combination is deliberate. With duplicate values, choosing strict comparisons on both sides can leave ambiguity, while using non-strict comparisons on both sides can count an identical subarray multiple times.

The Python implementation applies the same ownership idea to the sum of subarray minimums and to the difference between total subarray maximums and minimums.

## Python Implementation

The Python program progresses from direct monotonic-stack construction to nearest-element queries, daily-temperature waiting periods, stock spans, histogram rectangles, maximal rectangles, subarray aggregation, and greedy digit removal.

`daily_temperatures()` stores unresolved day indices. A warmer temperature resolves one or more earlier days, and the difference between indices directly gives the waiting period.

`stock_span()` uses a decreasing price structure. Prices less than or equal to the current price are removed because they cannot be the nearest blocking price for the current span.

`largest_rectangle_histogram()` uses a sentinel zero and index boundaries to calculate rectangles without rescanning the histogram.

`remove_k_digits()` shows that monotonic stacks can also implement greedy optimization. When a smaller digit arrives, larger previously selected digits are removed while removals remain available. The resulting sequence is lexicographically smaller and therefore numerically smaller after the requested number of removals.

The script includes validation for negative histogram heights, malformed matrices, invalid digit strings, and invalid removal counts. It also contains direct invariant checks useful when debugging a stack implementation.

## JavaScript Implementation

The JavaScript program treats arrays as stack structures and uses index stacks throughout the nearest-element algorithms.

Its circular next-greater implementation demonstrates a JavaScript-specific practical pattern: the logical input is scanned twice while the physical array remains unchanged. This avoids unnecessary duplication while allowing values near the beginning of the array to find candidates near the end.

The `PullRequestMetrics` class provides a separate domain-oriented use of histogram processing. It treats a sequence of operational measurements as histogram bars and asks for the strongest contiguous region represented by a rectangle.

The class is intentionally separate from the monotonic-stack functions. The stack is an algorithmic mechanism, while the class provides a domain boundary around that mechanism.

Input validation is explicit in the histogram implementation. Invalid negative heights or non-finite numeric values are rejected before the algorithm starts.

## C++ Case Study

The C++ program uses a repository-governance scenario to demonstrate two different technical responsibilities.

`NextGreaterResolver` implements an index-based next-greater query. It uses `std::vector` as the stack container and stores positions rather than values.

`HistogramRiskAnalyzer` implements the largest rectangle algorithm over operational measurements. The rectangle identifies a contiguous region in which a metric threshold is sustained. This demonstrates how a monotonic-stack primitive can become part of a larger system without changing its mathematical invariant.

The governance model is deliberately separate from the stack algorithm. `PullRequest` contains source and target branches, commits, review signals, status-check durations, draft state, and conflict state. `BranchPolicy` represents protected-branch requirements.

`MergeEligibilityEngine` evaluates approval thresholds, draft state, missing commits, conflicts, and status-check conditions. The separation illustrates an important design principle: the monotonic stack answers a local ordering problem, while repository governance evaluates policy state.

The program also demonstrates failure transitions by removing an approval and then introducing a merge conflict.

## Java Enterprise-Oriented Model

The Java implementation uses domain types to represent repository governance rather than relying on unstructured strings.

`ReviewState` distinguishes comments, requested changes, approvals, and dismissed reviews. `PullRequestState` distinguishes draft, open, merged, and closed states.

`BranchProtection` explicitly stores the approval threshold, status-check requirement, force-push restriction, and linear-history requirement. Its `requiredConditions()` method converts those configuration values into a set of domain conditions.

`MergeEligibilityService` evaluates the current Pull Request against that policy. Eligible reviewers with an `APPROVED` state contribute to the approval count. Status checks are treated as a separate merge condition. Conflicts, draft state, missing commits, and linear-history requirements are independently evaluated.

This makes policy failures observable rather than collapsing all failures into a single Boolean.

The Java implementation also uses immutable records for reviews and protection policies. This prevents accidental mutation of policy data while a merge decision is being evaluated.

The monotonic-stack functions remain independent utilities because repository governance and nearest-element algorithms are different abstractions even when both appear in the same technical learning artifact.

## SQL Data Model

The PostgreSQL implementation models repository governance relationally.

`repository` represents the repository boundary. `branch` associates branches with repositories and identifies protected branches. `pull_request` connects an author, source branch, and target branch while storing draft, conflict, state, and history information.

`commit_record` represents commits associated with Pull Requests. `review` stores reviewer decisions, while `review_comment` records file-level and line-level review discussions. `status_check` stores individual automated validation results.

`branch_protection` contains repository governance rules such as required approvals, required checks, force-push restrictions, deletion restrictions, conversation-resolution requirements, direct-push restrictions, stale-approval behavior, and administrator bypass policy.

The relational constraints prevent invalid relationships and negative check durations. Indexes support frequent queries involving target branches, Pull Request states, review states, status checks, and commit membership.

## Database-Level Merge Evaluation

The `merge_eligibility` view combines Pull Request state with branch protection, approval counts, status-check results, and unresolved review comments.

This is intentionally different from the application implementations. SQL is particularly useful when the system needs a database-level reporting or governance view across many Pull Requests.

The view exposes the conditions used for merge eligibility instead of hiding them behind application-only logic.

The transaction near the end of the script demonstrates that a temporary conflict can be observed during a transaction and then discarded using `ROLLBACK`. This is important for governance systems because policy evaluation should operate on a consistent database state.

## Approval Semantics

An approval is a review decision, not merely the existence of a reviewer.

A reviewer can comment without approving, request changes, approve, or have an earlier approval dismissed. A policy can require a minimum number of eligible current approvals.

Stale approvals create another distinction. An approval associated with an older commit may no longer represent a review of the current changeset. The SQL model includes `approval_snapshot` and a trigger-based mechanism for marking earlier snapshots stale when a newer commit is recorded.

This reflects the difference between an approval event and an approval that is currently valid for merge eligibility.

## Branch Protection

Branch protection is a repository-level enforcement mechanism.

Required reviews specify how much review evidence is needed. Required status checks require automated validation before merging. Direct-push restrictions prevent contributors from bypassing the Pull Request workflow. Force-push and deletion restrictions protect branch history and availability.

Conversation requirements can prevent unresolved review discussions from being ignored.

Linear-history requirements constrain acceptable merge history. They are independent of the approval count because an approved change can still violate the repository's history policy.

Administrator bypass behavior is also a policy decision. A repository may permit exceptional bypasses, or it may require every actor to satisfy the same protected-branch conditions.

## Pull Request, Review, Approval, and Protection Relationship

These mechanisms should not be treated as synonyms.

A Pull Request is the change-management workflow connecting a source branch and a target branch. It identifies the proposed changeset and provides a place for review and automated checks.

Code review evaluates the changes. Reviewers can comment on specific lines, request changes, or approve the implementation.

An approval is a particular review decision. It can satisfy part of a repository policy when the reviewer is eligible and the approval remains valid.

Branch protection is the enforcement layer. It can require approvals, status checks, resolved conversations, linear history, or other conditions before the Pull Request becomes mergeable.

The relationship can therefore be expressed as:

`Pull Request → Code Review → Approval Decision → Branch Protection Evaluation → Merge Eligibility`

The arrows describe dependency rather than duplication. A Pull Request can exist without approval, a review can exist without approval, and an approval can exist without satisfying the complete branch policy.

## Comparison of Stack Variants

| Problem | Stack invariant | Typical comparison | Useful result |
|---|---|---|---|
| Next greater | Decreasing unresolved candidates | Pop while top < current | First greater element |
| Next smaller | Increasing unresolved candidates | Pop while top > current | First smaller element |
| Previous greater | Decreasing candidates | Remove values <= current | Nearest greater on left |
| Previous smaller | Increasing candidates | Remove values >= current | Nearest smaller on left |
| Histogram | Increasing indices | Pop when current height is smaller | Maximum rectangle |
| Subarray minimums | Increasing boundary candidates | Strict/non-strict pair | Element contribution |
| Subarray maximums | Decreasing boundary candidates | Strict/non-strict pair | Element contribution |

## Edge Cases

An empty sequence should return an empty result rather than attempting to access a stack top.

A single-element sequence has no next greater or next smaller element, so its answer is normally `-1` or an equivalent sentinel.

A strictly increasing sequence causes frequent pops in a decreasing next-greater stack.

A strictly decreasing sequence leaves many unresolved elements until the scan finishes.

Equal values require deliberate comparison choices. Replacing `<` with `<=`, or `>` with `>=`, can change ownership semantics and produce duplicate or missing answers.

A histogram containing zero-height bars naturally separates rectangles. Negative histogram heights are invalid for the standard rectangle interpretation and are rejected by the implementations.

## Performance Considerations

The principal advantage of a monotonic stack is amortized linear time.

Although a loop can contain another loop, an individual input index is not repeatedly pushed and popped without bound. Each index enters the stack once and can leave once. The total number of stack operations is therefore proportional to the input size.

The auxiliary stack requires `O(n)` space in the worst case.

For histogram algorithms, the input itself does not need to be sorted or copied into a second structure. A sentinel can be processed as a logical final value.

For very large numeric inputs, multiplication used in rectangle-area and contribution calculations can exceed 32-bit integer limits. The C++ implementation therefore uses `long long` for areas.

## Common Implementation Failures

Using values instead of indices can make it impossible to calculate distances and rectangle widths.

Using the wrong comparison operator changes whether equal values are retained or discarded.

Forgetting to flush the stack after the input ends leaves unresolved candidates without answers.

Forgetting the histogram sentinel leaves bars that extend to the final position unprocessed.

Treating the stack as a normal LIFO collection without maintaining its ordering invariant removes the algorithm's main performance benefit.

For subarray contribution problems, using strict comparisons on both sides or non-strict comparisons on both sides can mishandle duplicates.

## Debugging the Invariant

When debugging a monotonic-stack algorithm, inspect the stack immediately before and after each pop.

For a decreasing stack, every adjacent pair should satisfy:

`stack_value[i] >= stack_value[i + 1]`

For an increasing stack:

`stack_value[i] <= stack_value[i + 1]`

If that invariant fails, the comparison in the pop condition is usually the first place to inspect.

Index stacks should also be checked against the original array rather than assuming that the indices themselves are ordered by value.

The Python program exposes `validate_monotonic_invariant()` to make this property executable during debugging.

## Practical Boundary Between Algorithms

A useful decision rule is to identify what the current element does to earlier unresolved elements.

If the current element makes smaller earlier values obsolete, consider a decreasing stack of unresolved candidates.

If it makes larger earlier values obsolete, consider an increasing stack.

If the answer requires distance, width, or boundaries, store indices.

If duplicate values can occur, define whether equality should resolve an element before writing the pop condition.

For histogram problems, ask which smaller bar first limits the current bar on the left and right. That boundary interpretation leads directly to the increasing-stack solution.

## Files and Runtime Assumptions

The Python program requires Python 3 and uses only the standard library.

The JavaScript program is designed for a modern Node.js runtime and uses no external npm packages.

The C++ program requires C++17 or later and uses only the standard library.

The Java program requires Java 17 or later and uses only standard Java libraries.

The SQL script targets PostgreSQL and creates its own schema so that the relational demonstration can be executed without depending on an existing application schema.
