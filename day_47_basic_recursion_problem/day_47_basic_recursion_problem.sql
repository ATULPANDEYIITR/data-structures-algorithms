-- PostgreSQL 14+
-- Basic recursion problems modeled through recursive SQL and a repository
-- review workload. Mathematical examples and recursive change-tree
-- traversal use WITH RECURSIVE, while constraints protect stored data.

BEGIN;

DROP VIEW IF EXISTS pull_request_merge_readiness CASCADE;
DROP TABLE IF EXISTS review_comments CASCADE;
DROP TABLE IF EXISTS reviews CASCADE;
DROP TABLE IF EXISTS status_checks CASCADE;
DROP TABLE IF EXISTS pull_request_commits CASCADE;
DROP TABLE IF EXISTS pull_requests CASCADE;
DROP TABLE IF EXISTS branch_protection CASCADE;
DROP TABLE IF EXISTS branches CASCADE;
DROP TABLE IF EXISTS reviewers CASCADE;
DROP TABLE IF EXISTS repositories CASCADE;
DROP TABLE IF EXISTS change_nodes CASCADE;

CREATE TABLE repositories (
    repository_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_name TEXT NOT NULL UNIQUE,
    default_branch TEXT NOT NULL DEFAULT 'main',
    CHECK (length(trim(repository_name)) > 0)
);

CREATE TABLE branches (
    branch_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    branch_name TEXT NOT NULL,
    is_protected BOOLEAN NOT NULL DEFAULT FALSE,
    exists_now BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (repository_id, branch_name)
);

CREATE TABLE branch_protection (
    branch_id BIGINT PRIMARY KEY REFERENCES branches(branch_id)
        ON DELETE CASCADE,
    required_approvals INTEGER NOT NULL DEFAULT 1
        CHECK (required_approvals >= 0),
    require_passing_checks BOOLEAN NOT NULL DEFAULT TRUE,
    require_resolved_discussions BOOLEAN NOT NULL DEFAULT TRUE,
    restrict_direct_pushes BOOLEAN NOT NULL DEFAULT TRUE,
    allow_force_push BOOLEAN NOT NULL DEFAULT FALSE,
    allow_deletion BOOLEAN NOT NULL DEFAULT FALSE,
    require_linear_history BOOLEAN NOT NULL DEFAULT FALSE,
    require_merge_queue BOOLEAN NOT NULL DEFAULT FALSE,
    enforce_for_administrators BOOLEAN NOT NULL DEFAULT TRUE,
    bypass_roles TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[]
);

CREATE TABLE reviewers (
    reviewer_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    reviewer_name TEXT NOT NULL UNIQUE,
    can_review BOOLEAN NOT NULL DEFAULT TRUE,
    role_name TEXT NOT NULL,
    CHECK (length(trim(reviewer_name)) > 0)
);

CREATE TABLE pull_requests (
    pull_request_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id),
    source_branch_id BIGINT NOT NULL REFERENCES branches(branch_id),
    target_branch_id BIGINT NOT NULL REFERENCES branches(branch_id),
    title TEXT NOT NULL,
    lifecycle_state TEXT NOT NULL DEFAULT 'open'
        CHECK (lifecycle_state IN ('draft', 'open', 'closed', 'merged')),
    has_conflicts BOOLEAN NOT NULL DEFAULT FALSE,
    discussions_resolved BOOLEAN NOT NULL DEFAULT TRUE,
    merged_by BIGINT REFERENCES reviewers(reviewer_id),
    merged_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (source_branch_id <> target_branch_id),
    CHECK (
        (lifecycle_state = 'merged' AND merged_at IS NOT NULL)
        OR
        (lifecycle_state <> 'merged' AND merged_at IS NULL)
    ),
    CHECK (length(trim(title)) > 0)
);

CREATE INDEX pull_requests_target_state_idx
    ON pull_requests(target_branch_id, lifecycle_state);

CREATE TABLE pull_request_commits (
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    commit_hash CHAR(40) NOT NULL,
    commit_position INTEGER NOT NULL CHECK (commit_position > 0),
    PRIMARY KEY (pull_request_id, commit_hash),
    UNIQUE (pull_request_id, commit_position)
);

CREATE TABLE status_checks (
    status_check_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    result TEXT NOT NULL
        CHECK (result IN ('pending', 'success', 'failure', 'cancelled')),
    checked_commit CHAR(40) NOT NULL,
    completed_at TIMESTAMPTZ,
    UNIQUE (pull_request_id, check_name, checked_commit),
    CHECK (
        (result = 'pending' AND completed_at IS NULL)
        OR
        (result <> 'pending')
    )
);

CREATE INDEX status_checks_pr_result_idx
    ON status_checks(pull_request_id, result);

CREATE TABLE reviews (
    review_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    reviewer_id BIGINT NOT NULL REFERENCES reviewers(reviewer_id),
    review_state TEXT NOT NULL
        CHECK (
            review_state IN (
                'commented',
                'approved',
                'changes_requested',
                'dismissed'
            )
        ),
    eligible BOOLEAN NOT NULL DEFAULT TRUE,
    stale BOOLEAN NOT NULL DEFAULT FALSE,
    reviewed_commit CHAR(40) NOT NULL,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX reviews_pr_reviewer_time_idx
    ON reviews(pull_request_id, reviewer_id, submitted_at DESC);

CREATE TABLE review_comments (
    comment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    review_id BIGINT NOT NULL REFERENCES reviews(review_id)
        ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    line_number INTEGER NOT NULL CHECK (line_number > 0),
    comment_body TEXT NOT NULL,
    is_resolved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (length(trim(comment_body)) > 0)
);

CREATE INDEX review_comments_unresolved_idx
    ON review_comments(review_id, is_resolved);

-- A changed component can have nested components. parent_node_id forms a
-- forest, while the self-reference models the recursive tree.
CREATE TABLE change_nodes (
    node_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pull_request_id BIGINT NOT NULL
        REFERENCES pull_requests(pull_request_id) ON DELETE CASCADE,
    parent_node_id BIGINT REFERENCES change_nodes(node_id)
        ON DELETE CASCADE,
    path TEXT NOT NULL,
    risk_score INTEGER NOT NULL CHECK (risk_score BETWEEN 0 AND 100),
    CHECK (length(trim(path)) > 0),
    UNIQUE (pull_request_id, path)
);

CREATE INDEX change_nodes_parent_idx
    ON change_nodes(pull_request_id, parent_node_id);

INSERT INTO repositories (repository_name)
VALUES ('secure-session-service');

INSERT INTO branches (repository_id, branch_name, is_protected)
VALUES
    (1, 'main', TRUE),
    (1, 'feature/session-hardening', FALSE);

INSERT INTO branch_protection (
    branch_id,
    required_approvals,
    require_passing_checks,
    require_resolved_discussions,
    restrict_direct_pushes,
    allow_force_push,
    allow_deletion,
    require_linear_history,
    require_merge_queue,
    enforce_for_administrators
)
VALUES (1, 2, TRUE, TRUE, TRUE, FALSE, FALSE, TRUE, FALSE, TRUE);

INSERT INTO reviewers (reviewer_name, can_review, role_name)
VALUES
    ('Asha', TRUE, 'maintainer'),
    ('Dev', TRUE, 'security-reviewer'),
    ('Mira', TRUE, 'developer'),
    ('ServiceBot', FALSE, 'automation');

INSERT INTO pull_requests (
    repository_id,
    source_branch_id,
    target_branch_id,
    title,
    lifecycle_state,
    has_conflicts,
    discussions_resolved
)
VALUES (
    1, 2, 1,
    'Harden session token validation',
    'open',
    FALSE,
    FALSE
);

INSERT INTO pull_request_commits (
    pull_request_id, commit_hash, commit_position
)
VALUES
    (1, repeat('a', 40), 1),
    (1, repeat('b', 40), 2);

INSERT INTO status_checks (
    pull_request_id, check_name, result, checked_commit, completed_at
)
VALUES
    (1, 'unit-tests', 'success', repeat('b', 40), CURRENT_TIMESTAMP),
    (1, 'security-scan', 'success', repeat('b', 40), CURRENT_TIMESTAMP),
    (1, 'integration-tests', 'pending', repeat('b', 40), NULL);

INSERT INTO reviews (
    pull_request_id,
    reviewer_id,
    review_state,
    eligible,
    stale,
    reviewed_commit
)
VALUES
    (1, 1, 'approved', TRUE, FALSE, repeat('b', 40)),
    (1, 2, 'approved', TRUE, TRUE, repeat('a', 40)),
    (1, 3, 'commented', TRUE, FALSE, repeat('b', 40));

INSERT INTO review_comments (
    review_id, file_path, line_number, comment_body, is_resolved
)
VALUES
    (3, 'src/session.py', 42,
     'Validate the token audience before accepting the session.', FALSE),
    (3, 'src/session.py', 57,
     'Reject expired tokens using the configured clock tolerance.', TRUE);

-- The merge-readiness view selects the latest review decision for each
-- reviewer. Stale, dismissed, and ineligible reviews cannot count as
-- approvals. Required status checks must succeed on the latest commit.
CREATE VIEW pull_request_merge_readiness AS
WITH latest_commit AS (
    SELECT DISTINCT ON (pull_request_id)
        pull_request_id,
        commit_hash
    FROM pull_request_commits
    ORDER BY pull_request_id, commit_position DESC
),
latest_reviewer_decisions AS (
    SELECT DISTINCT ON (r.pull_request_id, r.reviewer_id)
        r.pull_request_id,
        r.reviewer_id,
        r.review_state,
        r.eligible,
        r.stale
    FROM reviews AS r
    ORDER BY
        r.pull_request_id,
        r.reviewer_id,
        r.submitted_at DESC,
        r.review_id DESC
),
approval_counts AS (
    SELECT
        pull_request_id,
        COUNT(*) FILTER (
            WHERE review_state = 'approved'
              AND eligible
              AND NOT stale
        ) AS eligible_approvals,
        COUNT(*) FILTER (
            WHERE review_state = 'changes_requested'
              AND eligible
              AND NOT stale
        ) AS active_change_requests
    FROM latest_reviewer_decisions
    GROUP BY pull_request_id
),
check_status AS (
    SELECT
        c.pull_request_id,
        BOOL_AND(c.result = 'success') AS all_checks_successful
    FROM status_checks AS c
    JOIN latest_commit AS lc
      ON lc.pull_request_id = c.pull_request_id
     AND lc.commit_hash = c.checked_commit
    GROUP BY c.pull_request_id
),
open_comments AS (
    SELECT
        r.pull_request_id,
        COUNT(*) FILTER (WHERE NOT c.is_resolved) AS unresolved_comments
    FROM reviews AS r
    JOIN review_comments AS c ON c.review_id = r.review_id
    GROUP BY r.pull_request_id
)
SELECT
    pr.pull_request_id,
    pr.title,
    pr.lifecycle_state,
    pr.has_conflicts,
    pr.discussions_resolved,
    bp.required_approvals,
    COALESCE(ac.eligible_approvals, 0) AS eligible_approvals,
    COALESCE(ac.active_change_requests, 0) AS active_change_requests,
    COALESCE(cs.all_checks_successful, FALSE) AS all_checks_successful,
    COALESCE(oc.unresolved_comments, 0) AS unresolved_comments,
    (
        pr.lifecycle_state = 'open'
        AND NOT pr.has_conflicts
        AND COALESCE(ac.eligible_approvals, 0) >= bp.required_approvals
        AND COALESCE(ac.active_change_requests, 0) = 0
        AND (
            NOT bp.require_passing_checks
            OR COALESCE(cs.all_checks_successful, FALSE)
        )
        AND (
            NOT bp.require_resolved_discussions
            OR (
                pr.discussions_resolved
                AND COALESCE(oc.unresolved_comments, 0) = 0
            )
        )
    ) AS merge_eligible
FROM pull_requests AS pr
JOIN branches AS target_branch
  ON target_branch.branch_id = pr.target_branch_id
LEFT JOIN branch_protection AS bp
  ON bp.branch_id = target_branch.branch_id
LEFT JOIN approval_counts AS ac
  ON ac.pull_request_id = pr.pull_request_id
LEFT JOIN check_status AS cs
  ON cs.pull_request_id = pr.pull_request_id
LEFT JOIN open_comments AS oc
  ON oc.pull_request_id = pr.pull_request_id;

-- Recursive factorial uses the recursive CTE's previous result as input.
WITH RECURSIVE factorial_step(n, value) AS (
    SELECT 0, 1::NUMERIC
    UNION ALL
    SELECT n + 1, value * (n + 1)
    FROM factorial_step
    WHERE n < 10
)
SELECT n, value AS factorial
FROM factorial_step
ORDER BY n;

-- Fibonacci uses two recursive state variables rather than recomputing
-- both branches. This is a linear-state recurrence.
WITH RECURSIVE fibonacci_step(n, current_value, next_value) AS (
    SELECT 0, 0::NUMERIC, 1::NUMERIC
    UNION ALL
    SELECT n + 1, next_value, current_value + next_value
    FROM fibonacci_step
    WHERE n < 20
)
SELECT n, current_value AS fibonacci
FROM fibonacci_step
ORDER BY n;

-- Recursive exponentiation by squaring can be expressed as successive
-- exponent reduction. Numeric exponentiation is bounded here to keep
-- the demonstration output manageable.
WITH RECURSIVE power_step(exponent, value, accumulated) AS (
    SELECT 13, 2::NUMERIC, 1::NUMERIC
    UNION ALL
    SELECT
        exponent / 2,
        value * value,
        CASE
            WHEN exponent % 2 = 1 THEN accumulated * value
            ELSE accumulated
        END
    FROM power_step
    WHERE exponent > 0
)
SELECT accumulated AS two_to_the_thirteenth
FROM power_step
WHERE exponent = 0;

-- Sum digits: repeatedly divide the absolute value by ten and accumulate
-- each remainder. The sign does not affect the digit sum.
WITH RECURSIVE digit_step(original_value, remaining, digit_sum) AS (
    SELECT -5821::BIGINT, ABS(-5821::BIGINT), 0::BIGINT
    UNION ALL
    SELECT
        original_value,
        remaining / 10,
        digit_sum + remaining % 10
    FROM digit_step
    WHERE remaining > 0
)
SELECT original_value, MAX(digit_sum) AS sum_of_digits
FROM digit_step
GROUP BY original_value;

-- Recursive reversal uses the accumulated prefix as state. Numeric reversal
-- naturally drops leading zeros in the reversed representation.
WITH RECURSIVE reverse_step(remaining, reversed_value) AS (
    SELECT 1200::BIGINT, 0::NUMERIC
    UNION ALL
    SELECT
        remaining / 10,
        reversed_value * 10 + remaining % 10
    FROM reverse_step
    WHERE remaining > 0
)
SELECT reversed_value AS reversed_number
FROM reverse_step
WHERE remaining = 0;

-- Recursive array traversal: each row contributes its risk score and
-- the scores of descendants. A path guard prevents infinite recursion if
-- malformed cyclic hierarchy data is introduced outside normal constraints.
WITH RECURSIVE change_tree AS (
    SELECT
        node_id,
        pull_request_id,
        parent_node_id,
        path,
        risk_score,
        ARRAY[node_id] AS visited
    FROM change_nodes
    WHERE pull_request_id = 1
      AND parent_node_id IS NULL

    UNION ALL

    SELECT
        child.node_id,
        child.pull_request_id,
        child.parent_node_id,
        child.path,
        child.risk_score,
        parent.visited || child.node_id
    FROM change_tree AS parent
    JOIN change_nodes AS child
      ON child.parent_node_id = parent.node_id
     AND child.pull_request_id = parent.pull_request_id
    WHERE NOT child.node_id = ANY(parent.visited)
)
SELECT
    pull_request_id,
    COUNT(*) AS changed_components,
    SUM(risk_score) AS total_review_risk,
    MAX(risk_score) AS highest_component_risk
FROM change_tree
GROUP BY pull_request_id;

-- Evaluate repository-level merge requirements without modifying state.
SELECT
    pull_request_id,
    title,
    eligible_approvals,
    required_approvals,
    active_change_requests,
    all_checks_successful,
    unresolved_comments,
    merge_eligible
FROM pull_request_merge_readiness;

-- Demonstrate a safe, atomic governance-state update. This block only
-- resolves an outstanding discussion and updates the check result. It does
-- not merge automatically; the readiness view remains the decision source.
BEGIN;

UPDATE review_comments
SET is_resolved = TRUE
WHERE comment_id = 1;

UPDATE pull_requests
SET discussions_resolved = TRUE
WHERE pull_request_id = 1;

UPDATE status_checks
SET result = 'success',
    completed_at = CURRENT_TIMESTAMP
WHERE pull_request_id = 1
  AND check_name = 'integration-tests'
  AND checked_commit = repeat('b', 40);

COMMIT;

SELECT
    pull_request_id,
    merge_eligible
FROM pull_request_merge_readiness;

-- Database constraints reject malformed review scores, invalid review
-- states, negative approval requirements, invalid comment line numbers,
-- and references to nonexistent repositories or reviewers.
-- These constraints are part of repository governance, not substitutes
-- for application-level authorization or atomic merge enforcement.

COMMIT;
