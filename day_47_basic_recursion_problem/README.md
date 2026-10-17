# Basic Recursion Problems: Mathematical Computation and Structured Traversal

## Technical scope

Recursion solves a problem by reducing it to smaller instances of the same problem. A recursive implementation has a base case that terminates the process and a recursive step that moves the input toward that case.

The implementations cover factorial, Fibonacci numbers, integer powers, digit sums, number reversal, and array traversal. They also connect recursive techniques to a practical repository-governance scenario in which changed components form a hierarchy and their review risks must be evaluated.

The six deliverables serve different purposes:

| File | Primary purpose |
|---|---|
| Python script | Executable mathematical functions, validation, performance comparison, and recursive collection algorithms |
| JavaScript file | Exact integer arithmetic, memoization, recursion events, and recursive processing of nested change records |
| C++ program | Repository change-risk analysis and a merge-eligibility policy engine |
| Java program | Typed repository domain objects, review-state management, and policy-based merge decisions |
| SQL script | Recursive common table expressions, relational integrity, change-tree traversal, and merge-readiness evaluation |
| README | Mathematical foundations, implementation decisions, complexity, and practical limitations |

## The structure of a recursive solution

A recursive function should answer three questions.

- **What is the smallest valid input?** This is the base case, such as \(0! = 1\) or the sum of an empty sequence being zero.
- **How does the current input become smaller?** Factorial reduces \(n\) to \(n-1\); digit processing removes the final decimal digit; binary search discards half the remaining interval.
- **How are partial results combined?** Factorial multiplies a number by the factorial of its predecessor. Fibonacci adds two earlier results. Recursive traversal combines the current element with the result from the remaining collection.

A function may have a correct base case but still fail if its recursive step does not make progress. For example, calling a factorial function with the original argument rather than \(n-1\) causes unbounded recursion.

The call stack stores unfinished function calls. When a recursive call returns, the caller resumes and combines its local state with the returned value. This behavior explains both the clarity of recursive definitions and their potential memory costs.

## Factorial

For a non-negative integer \(n\),

\[
0! = 1
\]

\[
n! = n(n-1)!, \quad n \geq 1
\]

The base case is essential because multiplication by the factorial of a smaller integer must eventually reach zero or one. The result for \(5!\), for example, is obtained through the chain \(5 \times 4 \times 3 \times 2 \times 1\).

The Python and JavaScript implementations validate the input before starting recursion. Negative integers are rejected because the ordinary factorial definition does not cover them. Booleans also require attention in Python because `bool` is a subclass of `int`.

The JavaScript and Java implementations use arbitrary-precision integers for exact results. Ordinary JavaScript `Number` arithmetic and Java's fixed-width primitive integers can overflow or lose integer precision for large factorials. Python integers also support arbitrary precision, though their memory use increases as the result grows.

The recursive algorithm uses \(O(n)\) multiplications and \(O(n)\) stack frames. An iterative loop produces the same mathematical result without a linearly growing recursive call stack. Recursion is useful for understanding the definition; iteration is often more appropriate for very large input values.

## Fibonacci numbers and repeated computation

The Fibonacci sequence is defined by

\[
F(0)=0,\qquad F(1)=1
\]

\[
F(n)=F(n-1)+F(n-2),\quad n\geq 2
\]

The direct recursive definition creates two subproblems at every non-base call. Those subproblems overlap. Computing \(F(6)\), for instance, repeatedly requests values such as \(F(3)\) and \(F(2)\).

The direct implementation has exponential running time, conventionally described as \(O(2^n)\) as a useful upper-bound characterization. The exact call count grows according to the Fibonacci recurrence.

Memoization changes the computation by storing previously calculated results. Each index is calculated once, producing \(O(n)\) recursive states and \(O(n)\) cache storage. The Python script uses `functools.lru_cache`; the JavaScript implementation uses a `Map`; the Java implementation uses a `HashMap`.

The SQL script uses a different approach. Its recursive CTE carries the current and next Fibonacci values as state. Each row computes the next pair without constructing a branching recursion tree. This is a linear-state recurrence rather than a direct translation of the exponential algorithm.

Memoization does not remove all limitations. A deeply recursive computation can still exhaust the call stack, and cached values consume memory. For large indices, iterative generation is generally safer.

## Integer exponentiation

For a non-negative integer exponent,

\[
a^0=1
\]

\[
a^n=a\cdot a^{n-1},\quad n>0
\]

A direct recursive implementation uses \(O(n)\) multiplications. Exponentiation by squaring reduces the work by halving the exponent at every recursive level.

For even \(n\),

\[
a^n=(a^{n/2})^2
\]

For odd \(n\),

\[
a^n=a(a^{\lfloor n/2\rfloor})^2
\]

This method uses \(O(\log n)\) recursive levels and multiplications. It is demonstrated in Python, JavaScript, Java, and SQL.

Negative exponents require special treatment:

\[
a^{-n}=\frac{1}{a^n},\quad a\neq 0
\]

Python can represent the reciprocal with ordinary numeric division. JavaScript and Java use explicit representations or errors where exact integer arithmetic cannot express a fraction. The JavaScript implementation returns a numerator and denominator using `BigInt`; the Java implementation restricts its power function to exact integer results and rejects negative exponents.

The zero-base case with a negative exponent must be rejected. Floating-point results may also be approximate even when the recursive algorithm is correct.

## Sum of decimal digits

For a non-negative integer \(n\), let \(n \bmod 10\) represent the final decimal digit and \(\lfloor n/10 \rfloor\) represent the preceding digits.

The recurrence is

\[
S(n)=
\begin{cases}
n,&0\leq n<10\\
(n\bmod 10)+S(\lfloor n/10\rfloor),&n\geq10
\end{cases}
\]

For 4729, the calculation adds 9, 2, 7, and 4 to produce 22. Each recursive call removes one decimal digit, so the number of calls is proportional to the number of digits.

The implementations treat a negative input by ignoring its sign. Thus, the digit sum of \(-4729\) is also 22. This is an explicit design decision rather than an accidental consequence of language-specific remainder rules.

The Java implementation converts the input to decimal text before processing its digits. This avoids the overflow problem associated with taking the absolute value of the minimum signed `long` value.

## Reversing an integer

Number reversal is a state-accumulation problem. Each call removes the final digit from the input and appends it to the accumulated result.

If `remaining` is the unprocessed portion and `reversed` is the accumulated prefix, the transition is:

\[
\text{reversed}'=10\cdot\text{reversed}+(\text{remaining}\bmod10)
\]

\[
\text{remaining}'=\lfloor\text{remaining}/10\rfloor
\]

The process terminates when no digits remain.

An integer representation cannot preserve leading zeros. Reversing 1200 therefore returns 21 rather than the textual value `0021`. If preserving the width of the original representation is required, the operation must work with a string or retain the desired width separately.

The Python, JavaScript, and Java implementations preserve the sign. The Java implementation accepts decimal integer text, which avoids silently overflowing a fixed-width numeric type during reversal.

## Recursive array traversal

An array can be processed by keeping an index that moves toward the end of the sequence. For a sequence \(A\) of length \(n\), the sum recurrence is:

\[
T(A,i)=
\begin{cases}
0,&i=n\\
A_i+T(A,i+1),&i<n
\end{cases}
\]

The same structure supports searches, transformations, counting, and aggregation.

The Python program includes:

- `recursive_sum`, which adds each element to the sum of the remaining sequence.
- `recursive_find`, which returns the first matching index or `-1`.
- `recursive_maximum`, which combines the current element with the maximum of the remaining elements.
- `recursive_map`, which applies a transformation without modifying the original sequence.
- `recursive_binary_search`, which searches an ordered sequence by discarding half of the remaining interval.

A linear traversal has \(O(n)\) time and \(O(n)\) recursive stack space. Binary search takes \(O(\log n)\) time and stack space, provided that its input is sorted in ascending order.

Recursive collection functions need explicit empty-input behavior. The sum of an empty sequence is zero, but a maximum cannot be defined by selecting an element from an empty sequence. The Python implementation raises a `ValueError` for that case.

Array slicing can create repeated allocations. The Python and JavaScript traversal functions use indices to avoid creating a new suffix at every call. Some transformations still allocate output elements because the transformed result is a separate collection.

## Python implementation

The Python script is an executable progression from mathematical definitions to more efficient algorithms and collection processing.

`factorial_recursive` illustrates a direct recurrence, while `factorial_iterative` supplies a version without recursive stack growth. The Fibonacci functions contrast direct recursion, memoization, and iterative computation. The script clears no cache between demonstrations, so its performance measurements explicitly reflect that earlier calls may have populated the memoization cache.

The exponentiation function uses a nested helper for exponentiation by squaring. Keeping the helper separate allows the public function to handle validation and negative exponents before the recursive calculation starts.

The array functions validate starting indices, define behavior for empty sequences, and avoid modifying the original data. The validation demonstrations catch expected errors and continue execution. Assertions verify base cases, ordinary results, negative inputs, missing search targets, and other boundary conditions.

The script is designed for the Python standard library. Its main limitation is recursion depth: Python does not optimize tail-recursive calls. Even a logically correct linear recursion can raise `RecursionError` for sufficiently deep input.

## JavaScript implementation

JavaScript introduces a distinction between ordinary numeric values and `BigInt`. The implementation uses safe integers for indices and loop-related parameters, while factorial, Fibonacci, powers, digit sums, and reversed integer values use `BigInt` where exact arithmetic is important.

The Fibonacci cache is local to each call. This makes its lifetime and memory ownership clear, but repeated independent calls do not share cached results. `fibonacciWithStatistics` exposes the number of newly calculated states and the cache size so the effect of memoization can be inspected.

The factorial trace uses a callback that receives structured events. It emits entry, base-case, and return events rather than printing directly inside the recursive function. A caller can collect those events or connect them to another event consumer.

`PullRequestRecursionLab.totalReviewRisk` recursively examines nested change records. A component contributes its own risk, the risk of its children, and the risk of its siblings. This is a tree traversal rather than a simple mathematical recurrence.

JavaScript engines do not guarantee tail-call optimization. Very deep recursion can cause a `RangeError` associated with call-stack exhaustion. BigInt also has performance and memory costs for extremely large values.

## C++ case study: repository change review

The C++ program models a pull request whose changed components are represented as a hierarchy of `ChangeNode` objects.

Each node contains a path, a risk score, and a collection of child nodes. This structure models nested areas of a change that may need independent examination. `ReviewEngine` performs three recursive operations:

- `totalRisk` traverses the hierarchy and aggregates validated risk scores.
- `fileCount` counts all nodes, including nested components.
- `findPath` locates a matching path and returns an `optional` result when no match exists.

The functions use indices to traverse sibling vectors. The nested recursive call handles descendants, while the sibling call advances through the current collection. The combined traversal is linear in the number of nodes, with call-stack usage proportional to tree depth.

The review-effort demonstration uses memoized Fibonacci values. It illustrates caching, but the Fibonacci result is not a calibrated estimate of actual engineering effort. Real estimates should use measured review time, change size, component ownership, and historical outcomes.

`MergeEligibility` represents a separate policy evaluation. It checks whether a request is open, whether drafts are allowed, whether the source branch exists, whether conflicts remain, whether required checks passed, whether discussions are resolved, and whether enough eligible approvals exist.

The evaluator does not infer that every recorded approval is valid. Its input contains the number of approvals that have already passed eligibility checks. A production service would derive this number from authoritative review records, including stale-review and reviewer-permission rules.

The case study validates risk scores and reports failures through exceptions. Its policy engine returns all blocking reasons rather than stopping at the first failed condition. This makes the output useful for identifying multiple independent reasons that prevent merging.

## Java implementation: typed governance state

The Java implementation separates mathematical operations from repository-domain behavior.

`ChangeNode`, `Review`, and `BranchPolicy` are records with constructor validation. The immutable child lists prevent external callers from modifying the hierarchy after construction. `Review.countsAsApproval` defines the conditions under which an approval counts: the reviewer must be eligible, the review must not be stale, and the state must be `APPROVED`.

`PullRequest` owns its lifecycle state, change tree, reviews, check result, conflict state, and discussion status. Its methods enforce state transitions. For example, a draft can become ready for review, but a merged request cannot be reopened through the draft transition method.

`MergeEligibilityService` evaluates the branch policy against the request state. It checks the lifecycle state, conflicts, successful checks, resolved discussions, and eligible approval count. It reports blockers before changing the request to `MERGED`.

The Java mathematical methods use `BigInteger` for factorial, Fibonacci, and exact integer powers. Memoization uses a map of previously calculated Fibonacci values. The digit-sum method processes a decimal string to avoid the minimum-value overflow problem of `Math.abs(long)`.

Java's explicit types and exceptions make invalid states visible, but the in-memory example does not provide distributed locking, durable storage, or atomic coordination with a real repository platform. A production merge service would need to recheck the policy at merge time to prevent state changes between eligibility evaluation and execution.

## SQL implementation: recursive queries and integrity

The PostgreSQL script demonstrates that recursion is not limited to procedural languages. A `WITH RECURSIVE` common table expression repeatedly applies a query to the results of its previous iteration.

The recursive factorial query stores the current index and accumulated factorial value. The Fibonacci query stores the current and next sequence values. The exponentiation query reduces the exponent by division by two while squaring the current base and updating the accumulated result. These queries use state transitions rather than creating a separate branch for every recursive subproblem.

The digit-sum query accumulates decimal remainders until no digits remain. The reversal query appends the last digit to an accumulated numeric value. The change-tree query joins parent and child nodes until the hierarchy is exhausted.

The relational schema represents repositories, branches, branch-protection policies, pull requests, commits, reviewers, reviews, status checks, inline review comments, and changed components. Foreign keys protect relationships, check constraints reject invalid states, and indexes support common joins and filtered lookups.

The `pull_request_merge_readiness` view combines the latest commit, the latest review decision per reviewer, status-check results for that commit, unresolved comments, and branch policy. A stale approval does not count, and a later review decision supersedes an earlier decision by the same reviewer.

The view is a policy-evaluation example rather than a complete repository enforcement mechanism. Database constraints cannot by themselves guarantee that an external Git server will obey the policy. A real system must coordinate repository operations with trusted review and status-check records.

The script's recursive tree query includes a visited-node path to prevent revisiting a node within a traversal. The schema's self-referencing foreign key does not independently prohibit cycles. A production system should validate parent-child relationships, enforce same-pull-request ownership, and prevent cyclic changes through suitable transactional validation or trigger logic.

The SQL script is intended for PostgreSQL. Its recursive CTEs are bounded by explicit stopping conditions, and its data-changing demonstration uses a transaction to group related state updates.

## Complexity and practical limitations

| Operation | Time complexity | Recursive stack or working-state cost |
|---|---|---|
| Factorial | \(O(n)\) multiplications | \(O(n)\) recursive frames |
| Direct Fibonacci | Exponential | \(O(n)\) maximum depth |
| Memoized Fibonacci | \(O(n)\) states | \(O(n)\) cache and stack |
| Iterative Fibonacci | \(O(n)\) additions | \(O(1)\) working variables |
| Exponentiation by squaring | \(O(\log n)\) multiplications | \(O(\log n)\) recursive frames |
| Digit sum | \(O(d)\), where \(d\) is the digit count | \(O(d)\) recursive frames |
| Number reversal | \(O(d)\) digit operations | \(O(d)\) recursive frames |
| Linear array traversal | \(O(n)\) | \(O(n)\) recursive frames |
| Binary search | \(O(\log n)\) | \(O(\log n)\) recursive frames |
| Change-tree traversal | \(O(N)\) for \(N\) nodes | \(O(H)\) for tree height \(H\) |

These bounds count basic operations and recursive state, not the full cost of arbitrary-precision arithmetic. Very large integer multiplication and storage become increasingly expensive as the result grows.

A shallow, balanced tree may be traversed comfortably with recursion. A long chain of nested nodes can produce stack depth proportional to the total number of nodes. Iterative traversal with an explicit stack is a useful alternative when input depth is not controlled.

Memoization is effective when subproblems repeat. It is less useful for a simple linear recurrence in which every state is already visited exactly once, unless the cache is needed to support repeated calls or random access to previously calculated results.

## Correctness and failure conditions

The base case and recursive transition must work together. A correct factorial function cannot accept a negative input and continue decrementing indefinitely. A correct binary search cannot use an arbitrary unsorted array because discarding half the interval depends on ordering.

Input validation should occur before expensive recursive work. In the examples, factorial rejects negative values, exponentiation rejects a zero base with a negative exponent, and maximum-value calculation rejects an empty collection. Array traversal checks its index boundaries.

Numeric representation is part of correctness. An algorithm that computes the right mathematical recurrence can still produce incorrect results if its integer type overflows. JavaScript `Number` is not suitable for all large integer results, and Java primitive integer types have fixed ranges. BigInt and BigInteger address integer precision, but neither removes resource limits.

The repository-governance examples introduce a separate correctness concern: recursively calculating a risk score does not establish merge authorization. Merge eligibility depends on policy and trusted state. Review approvals, status checks, conflict status, discussion resolution, and branch protection must remain distinct conditions.

## Repository governance as a recursive data problem

A pull request is a proposal to merge a source branch into a target branch. Code review evaluates the quality and correctness of its changes. An approval records a reviewer decision, subject to eligibility and freshness rules. Branch protection establishes repository-level conditions that must hold before the target branch accepts a change.

The recursive examples contribute to this workflow by processing structured changes. A hierarchical change tree can identify sensitive components, aggregate risk indicators, count nested components, and locate a particular path. These calculations support review planning but do not replace human judgment or automated checks.

A review system must distinguish the following conditions:

- A review can contain comments without approving the change.
- An approval can become stale when new commits modify the reviewed changes.
- A reviewer can be ineligible to approve a protected branch.
- A successful status check for an earlier commit may not establish that the latest commit passes.
- Unresolved discussions can remain a merge blocker even when the required approval count has been reached.
- Branch protection can restrict direct pushes and force pushes independently of the recursive analysis of changed files.

The implementations make these distinctions explicit because a computational result and a governance decision answer different questions. Recursive traversal computes information about the change structure; the merge policy evaluates whether the repository's requirements have been met.

## Security and production considerations

Recursive algorithms should not be trusted with arbitrary depth without a resource limit. A deeply nested JSON document, directory-like tree, or change hierarchy can consume excessive stack space. Input validation, maximum-depth rules, bounded payloads, and iterative alternatives reduce this risk.

Memoization also requires a memory policy. An unbounded cache is convenient for demonstrations, but a long-running service may need a bounded cache or request-scoped lifetime. Cached results are safe only when the function's output depends entirely on the cache key and stable inputs.

Repository policy evaluation must use authoritative records. A client-provided approval count or claimed successful check is not sufficient evidence of merge eligibility. Review permissions, current commit identifiers, policy changes, and merge state must be validated by a trusted service.

Finally, checking eligibility and executing a merge are separate operations. If a new commit arrives or an approval is dismissed between those operations, the original decision may no longer be valid. A production implementation should re-evaluate the required conditions immediately before merging and use the repository platform's supported atomic merge or concurrency controls.
