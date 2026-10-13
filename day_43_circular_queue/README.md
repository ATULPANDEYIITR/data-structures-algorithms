# Circular Queue: Front/Rear Pointers, Overflow Handling, and Efficient FIFO Storage

## Scope

A circular queue is a fixed-size FIFO data structure that reuses array positions after elements are removed. Instead of shifting remaining elements toward the beginning of an array, the queue treats the storage as logically connected end-to-start.

The central state consists of a `front` position, a `rear` position, and a representation of the current element count. When the rear reaches the physical end of the array, it wraps to index zero. The same wrap-around rule applies to the front pointer.

This implementation set studies the mechanism from several technical perspectives:

- Python implements a reusable fixed-capacity circular queue, a dynamic variant, a printer-spooling case study, randomized differential testing, and explicit invariant checks.
- JavaScript models the same data structure while emphasizing event-driven bounded buffering and JavaScript runtime behavior.
- C++ uses a repository-governance event stream as a realistic bounded-buffer case study and connects queue behavior to Pull Request governance processing.
- Java models a typed enterprise repository-governance domain and uses a generic circular queue for bounded event processing.
- PostgreSQL represents repository governance relationally and demonstrates how Pull Requests, reviews, approvals, status checks, protected branches, and queued events can be stored and evaluated using database constraints and queries.

The examples distinguish the queue mechanism from the application domain. The repository examples use a circular queue as an event-buffering mechanism; they do not redefine Pull Requests, reviews, approvals, or branch protection as queue concepts.

## Core FIFO Model

A queue removes elements in the same order in which they were inserted.

For a circular queue backed by an array, the physical layout can differ from the logical FIFO order. For example, a queue with five slots can contain a logical sequence such as:

`C → D → E → F → G`

while its physical array may contain:

`F → G → empty → C → D → E`

The physical positions are not the queue order. `front` identifies `C`, and iteration proceeds from that location using wrap-around arithmetic.

The fundamental transition is:

`next_index = (current_index + 1) % capacity`

The modulo operation turns the last physical position into index zero.

## Why Front and Rear Are Separate

`front` identifies the next element to be removed.

`rear` identifies the next position into which an element will be inserted.

After an enqueue:

`buffer[rear] = value`

then:

`rear = (rear + 1) % capacity`

After a dequeue:

`value = buffer[front]`

then:

`front = (front + 1) % capacity`

The queue therefore changes logical boundaries rather than physically moving the elements.

The implementations maintain an explicit `size`. This is important because `front == rear` can occur in two different logical states:

- the queue can be empty after all elements have been removed;
- the queue can become full when every slot is occupied and the rear wraps around to the front.

An explicit size removes that ambiguity.

## Fixed Capacity and Overflow

A fixed circular queue has a hard storage boundary. When `size == capacity`, an enqueue cannot proceed.

The Python implementation raises `QueueFullError`. JavaScript raises `QueueFullError`. C++ uses `QueueFullException`, while the Java implementation reports an illegal queue state.

This behavior is preferable to silently overwriting an existing element. Overwriting would violate FIFO semantics because the oldest queued value could disappear without being dequeued.

The choice between rejection, blocking, dropping, or resizing belongs to the application architecture. The basic circular queue itself should make the capacity condition explicit.

## Underflow

Underflow occurs when a dequeue is requested while the queue contains no elements.

A correct implementation must detect this condition before reading from the front position. Returning an arbitrary stale array value would violate the queue contract.

The implementations therefore distinguish an empty queue from an occupied queue through `size`.

Clearing a removed slot also matters when queue elements are objects. The slot no longer participates in the logical queue, and clearing it prevents an unnecessary reference from remaining in the backing storage.

## Efficient Reuse of Storage

A conventional array-based queue can become inefficient if every dequeue shifts all remaining elements toward index zero.

Suppose the queue contains:

`A B C D`

and `A` is removed.

A shifting implementation might physically transform the array into:

`B C D empty`

That movement is unnecessary.

A circular queue instead changes the front pointer:

`front = (front + 1) % capacity`

The existing `B`, `C`, and `D` remain where they are.

This is the principal efficiency advantage of the circular representation. Enqueue and dequeue are constant-time operations when the capacity is fixed.

## Python Implementation

The Python implementation uses a list as the physical storage and stores three pieces of state: `_front`, `_rear`, and `_size`.

`enqueue()` first checks `is_full`. It writes the value at `_rear`, advances `_rear` with modulo arithmetic, and increments `_size`.

`dequeue()` checks `is_empty`, retrieves the value at `_front`, clears that physical slot, advances `_front`, and decrements `_size`.

`__iter__()` walks only the logical queue length. This is important because the backing list can contain unused slots before, between, or after logical elements.

The `raw_storage()` method exposes the physical representation for debugging and learning. `to_list()` exposes the logical FIFO sequence.

The Python program also contains `ResizableCircularQueue`. Its growth operation first extracts logical order, allocates larger storage, writes elements from index zero, and resets the pointers. Normal fixed-capacity operations remain O(1), while resizing is O(n).

The printer-spool example demonstrates why circular buffers are useful. A printer can process completed jobs while reusing freed queue positions for later jobs without shifting all waiting jobs.

The randomized differential test compares the custom queue with `collections.deque`. This verifies FIFO behavior across many enqueue and dequeue combinations rather than relying only on a few hand-written examples.

## JavaScript Implementation

The JavaScript implementation uses a class with `buffer`, `front`, `rear`, and `size` properties.

The `values()` method reconstructs logical FIFO order without assuming that the physical array is contiguous.

JavaScript's `undefined` value is used to clear released slots. This is especially relevant for object values because retaining an obsolete object reference can keep that object reachable longer than necessary.

The `EventBuffer` class demonstrates a bounded event-processing model. Events such as login, upload, password-change, and logout operations are accepted until capacity is reached. Once the buffer is full, the producer receives a failure rather than silently overwriting an existing event.

This models back-pressure at a simple application level. A production event-processing system may choose a blocking producer, durable persistence, retry behavior, or another overflow strategy, but the bounded circular queue establishes the core capacity boundary.

`DynamicCircularQueue` demonstrates a different design decision. It doubles capacity when full. This eliminates fixed-capacity rejection but introduces an O(n) resize operation and potentially higher memory usage.

## C++ Case Study

The C++ program models a repository-governance event buffer.

A Pull Request can generate events such as opening the request, submitting a review, completing a status check, or requesting a merge. A bounded event queue can temporarily hold these events while a governance service processes them.

The `PullRequestEvent` structure contains repository and Pull Request information, including state, changed-file count, approval count, and status-check state.

The queue uses `std::vector<std::optional<PullRequestEvent>>` as its backing storage. `std::optional` makes the distinction between an occupied slot and an empty slot explicit.

The queue uses move semantics when transferring events into and out of storage. This is useful when queued objects become larger than the small scalar examples often used to demonstrate queues.

The governance portion remains separate from the queue implementation. `BranchPolicy` represents rules such as the number of required approvals and whether status checks must pass. `mergeEligible()` evaluates the modeled conditions for an open Pull Request.

This distinction is important:

- the circular queue controls event ordering and bounded storage;
- the Pull Request model represents the change-management object;
- reviews and approvals provide governance decisions;
- status checks provide automated validation;
- branch policy determines whether the Pull Request is eligible for merging.

A queue does not itself decide whether a Pull Request should merge.

## Java Enterprise Model

The Java program uses explicit domain types for repository governance.

`PullRequestState` represents lifecycle state, while `ReviewState` represents a review decision. These are deliberately different enums because Pull Request lifecycle and review lifecycle are different concerns.

The `PullRequest` class controls state transitions. A draft can become open, an open Pull Request can be closed, and reviews are accepted only while the Pull Request is open.

`Review` contains the reviewer identity, review state, and reviewer eligibility. This allows the merge service to distinguish a valid reviewer approval from an approval made by an ineligible account.

`StatusCheck` represents automated validation and records whether a check is required and whether it passed.

`BranchProtectionPolicy` models protected-branch conditions such as required approval count, required checks, force-push restrictions, and deletion restrictions.

`MergeEligibilityService` evaluates the relationship between those domain objects. It counts only approvals from eligible reviewers and evaluates required status checks before declaring the Pull Request eligible.

The generic Java `CircularQueue<T>` is independent of the repository domain. This makes it reusable for other event types while keeping the enterprise governance model strongly typed.

## SQL Data Model

The PostgreSQL implementation separates repository governance concepts into relational entities.

`repositories` represents repositories.

`branches` represents source and target branches and records whether a branch is protected.

`users` represents repository participants.

`pull_requests` records the Pull Request lifecycle, author, source branch, target branch, and draft state.

`commits` associates commits with Pull Requests.

`reviews` records review decisions separately from Pull Request state.

`review_comments` represents line-level review discussions and their resolution state.

`status_checks` stores automated validation results.

`branch_protection_policies` stores repository governance rules at the target-branch level.

`approval_requirements` provides a place to model more specific approval requirements.

`queue_events` represents events waiting to be processed. `processed_at` distinguishes pending events from events that have already been consumed.

Foreign keys prevent orphaned reviews, comments, checks, and events. Check constraints prevent invalid state values and impossible combinations such as a draft flag that disagrees with the Pull Request state.

## Approval Semantics

Approval is not equivalent to the existence of a review row.

A review can be:

`commented`

`changes_requested`

`approved`

`dismissed`

The SQL merge-eligibility view counts active approvals from active users and deliberately excludes the modeled automation account. This demonstrates that approval eligibility is a policy decision rather than a simple count of all rows whose state happens to be `approved`.

A real repository can impose more specific rules, such as required teams, code-owner approval, review dismissal after a new commit, or restrictions on self-approval.

## Stale Approvals and New Commits

A significant governance issue is whether an approval remains valid after the Pull Request changes.

A new commit can invalidate the assumptions under which a reviewer approved a previous changeset. Repository platforms can therefore use stale-review policies that require another review after relevant changes.

The relational model includes `commits` and `reviews` separately so that an application can associate approval decisions with the state of a Pull Request at a particular point in time.

The example does not pretend that a simple approval count fully models stale-approval semantics. A production policy engine would need to compare review timing or review-associated commit state with the current Pull Request revision.

## Code Review and Review Comments

Code review is broader than approval.

A reviewer can leave an inline comment without approving the Pull Request. A reviewer can request changes. A discussion can remain unresolved even after another reviewer approves.

The SQL model therefore stores review comments independently from approval state.

The `require_conversation_resolution` branch-policy setting can make unresolved comments part of merge eligibility. This illustrates the relationship between review discussions and repository governance without conflating the two.

The Java and C++ models keep the same conceptual distinction: a review decision is not simply another representation of queue state.

## Branch Protection

Branch protection governs what may happen to a protected target branch.

Relevant restrictions can include:

- required reviews before merge;
- required status checks;
- restrictions on direct pushes;
- force-push restrictions;
- branch deletion restrictions;
- required conversation resolution;
- linear-history requirements;
- limits on who can perform administrative bypasses.

The SQL policy table stores several of these conditions explicitly.

The C++ and Java examples focus on merge eligibility because that is the point at which several independent governance conditions intersect.

A protected branch is therefore not merely a special queue destination. Branch protection is a repository governance mechanism, while the queue is a data-structure mechanism.

## Relationship Between Pull Requests, Reviews, Approvals, and Protection

The concepts form a workflow with distinct responsibilities.

A Pull Request proposes a changeset from a source branch toward a target branch.

Code Review evaluates the proposed changes through comments, review states, and discussions.

An Approval represents a reviewer decision that can contribute to satisfying a repository policy.

Branch Protection determines which conditions must be satisfied before the target branch accepts the change.

A circular queue can support the infrastructure around this workflow by buffering events generated when those states change.

The separation can be represented as:

`Pull Request event → circular event buffer → governance processor → review/status/policy evaluation → merge eligibility`

The queue provides ordering and bounded storage. It does not replace the governance policy.

## Front and Rear Invariants

For a queue with capacity `C`, valid state requires:

`0 <= size <= C`

The front and rear indexes must always satisfy:

`0 <= front < C`

`0 <= rear < C`

When the queue is empty:

`size = 0`

When the queue is full:

`size = C`

The explicit size field makes both states unambiguous even when `front == rear`.

After every successful enqueue, size increases by one.

After every successful dequeue, size decreases by one.

The Python self-test suite checks these invariants through normal operations and wrap-around behavior. The JavaScript assertions test logical ordering after the rear pointer crosses the physical boundary.

## Overflow Strategies

A fixed circular queue must decide what happens when capacity is exhausted.

Rejecting the enqueue is appropriate when losing the incoming event is preferable to silently losing an existing queued event and when the producer can retry.

Blocking is useful in synchronous bounded-buffer systems where producers should wait until consumers make space.

Dropping the newest event can be acceptable for low-value telemetry but is dangerous for events that represent required business actions.

Dropping the oldest event preserves the newest information but can violate event ordering and lose important historical state.

Dynamic resizing avoids fixed-capacity rejection but introduces memory growth and occasional O(n) copying.

The correct policy depends on the semantics of the queued data. A Pull Request governance event should not normally be discarded casually because losing a review or status event can produce an incorrect governance state.

## Complexity

For a fixed-capacity circular queue:

| Operation | Complexity |
|---|---:|
| Enqueue | O(1) |
| Dequeue | O(1) |
| Peek | O(1) |
| Clear | O(n) |
| Iterate | O(n) |
| Storage | O(n) |

The constant-time enqueue and dequeue operations depend on avoiding element shifting.

A dynamic queue still provides amortized efficient insertion when it grows geometrically, but a resize itself requires O(n) copying.

## Edge Cases

An empty queue must reject dequeue and peek operations.

A full queue must reject an enqueue unless the selected design explicitly supports resizing or another overflow policy.

Capacity zero is invalid for the implementations because modulo arithmetic would otherwise attempt division by zero and no meaningful storage would exist.

A queue containing exactly one element must correctly transition between empty and non-empty states.

A full queue whose rear pointer wraps to the front must remain distinguishable from an empty queue.

Repeated enqueue and dequeue operations must preserve FIFO order even after several complete wrap-around cycles.

Object-based implementations should clear released storage slots when retaining references would unnecessarily extend object lifetimes.

## Common Implementation Errors

Using `rear == front` as the only indicator of state without reserving a slot or storing an explicit size makes full and empty states ambiguous.

Incrementing a pointer without wrap-around eventually produces an out-of-range array index.

Shifting the complete array after every dequeue defeats the primary performance advantage of a circular queue.

Checking capacity after writing into the buffer can corrupt a full queue.

Failing to clear removed object references can retain memory unnecessarily.

Iterating from index zero rather than from `front` produces incorrect logical order after wrap-around.

Treating physical array order as FIFO order is incorrect once the queue has wrapped.

## Debugging Strategy

The most useful state to inspect is:

`capacity`

`front`

`rear`

`size`

`physical storage`

`logical sequence`

A queue can appear correct when only its logical sequence is printed while its pointer arithmetic is actually wrong. Showing both physical storage and logical order makes wrap-around defects easier to locate.

A reliable test should include:

- enqueue until full;
- attempted overflow;
- dequeue until empty;
- attempted underflow;
- enqueue after partial removal;
- multiple wrap-around cycles;
- a single-element queue;
- randomized enqueue/dequeue sequences.

The Python differential test uses `collections.deque` as a reference implementation. This is useful because the reference structure can independently validate FIFO behavior across many operation sequences.

## Production Considerations

A circular queue is appropriate when storage should be bounded and operations must be efficient.

For a single-threaded application, a simple array-backed queue is often sufficient.

For concurrent producers and consumers, synchronization becomes a separate concern. A queue must not allow two producers to write the same rear slot or two consumers to remove the same front slot without coordination.

For high-throughput systems, lock-free ring buffers can use atomic operations and memory-ordering rules, but those designs are substantially more complex than the fixed queue demonstrated here.

For durable event processing, an in-memory circular queue alone is insufficient because process failure can lose queued events. Persistent storage or a durable messaging system is required when events must survive process or machine failure.

For repository governance, durability is especially important when events influence merge eligibility. A temporary in-memory buffer should not be treated as the authoritative source of Pull Request, review, approval, or branch-protection state.

## Security Considerations

A queue does not provide authorization.

The repository governance examples therefore keep authorization and reviewer eligibility separate from queue mechanics.

An approval should be associated with a known reviewer identity and evaluated against repository policy.

Automation accounts should not automatically count as human approvals unless the repository policy explicitly permits them.

Branch protection should be enforced at the authoritative repository boundary rather than only in a client-side interface.

Events should be validated before entering a governance-processing queue. An event claiming that a Pull Request was approved should not be trusted merely because its payload says `approved`.

Queue capacity itself can also be a security boundary. An attacker capable of generating unbounded events can exhaust memory if the system has no bounded buffering or rate control.

## Design Distinction

The essential relationship between the four governance concepts and the circular queue is:

`Circular Queue` handles bounded FIFO event storage.

`Pull Request` represents a proposed repository change.

`Code Review` evaluates the proposed changes.

`Approval` records a review decision that may satisfy a policy requirement.

`Branch Protection` enforces repository-level conditions governing changes to protected branches.

Keeping these responsibilities separate makes the implementation easier to test, reason about, and extend without turning the queue into an inappropriate substitute for repository governance.
