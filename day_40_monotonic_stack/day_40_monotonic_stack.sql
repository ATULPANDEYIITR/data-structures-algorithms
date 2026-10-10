DROP SCHEMA IF EXISTS monotonic_stack_governance CASCADE;
CREATE SCHEMA monotonic_stack_governance;
SET search_path = monotonic_stack_governance;

CREATE TYPE pull_request_state AS ENUM (
    'draft',
    'open',
    'merged',
    'closed'
);

CREATE TYPE review_state AS ENUM (
    'commented',
    'changes_requested',
    'approved',
    'dismissed'
);

CREATE TABLE repository (
    repository_id BIGSERIAL PRIMARY KEY,
    repository_name TEXT NOT NULL UNIQUE,
    default_branch TEXT NOT NULL DEFAULT 'main',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE branch (
    branch_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repository(repository_id) ON DELETE CASCADE,
    branch_name TEXT NOT NULL,
    protected BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (repository_id, branch_name)
);

CREATE TABLE contributor (
    contributor_id BIGSERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE pull_request (
    pull_request_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repository(repository_id) ON DELETE CASCADE,
    author_id BIGINT NOT NULL REFERENCES contributor(contributor_id),
    source_branch_id BIGINT NOT NULL REFERENCES branch(branch_id),
    target_branch_id BIGINT NOT NULL REFERENCES branch(branch_id),
    title TEXT NOT NULL,
    state pull_request_state NOT NULL DEFAULT 'open',
    is_draft BOOLEAN NOT NULL DEFAULT FALSE,
    merge_conflict BOOLEAN NOT NULL DEFAULT FALSE,
    linear_history BOOLEAN NOT NULL DEFAULT TRUE,
    opened_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    merged_at TIMESTAMPTZ,
    CHECK (source_branch_id <> target_branch_id),
    CHECK (merged_at IS NULL OR state = 'merged')
);

CREATE TABLE commit_record (
    commit_id BIGSERIAL PRIMARY KEY,
    pull_request_id BIGINT NOT NULL REFERENCES pull_request(pull_request_id) ON DELETE CASCADE,
    commit_hash TEXT NOT NULL UNIQUE,
    committed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE review (
    review_id BIGSERIAL PRIMARY KEY,
    pull_request_id BIGINT NOT NULL REFERENCES pull_request(pull_request_id) ON DELETE CASCADE,
    reviewer_id BIGINT NOT NULL REFERENCES contributor(contributor_id),
    state review_state NOT NULL,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    dismissed_at TIMESTAMPTZ,
    UNIQUE (pull_request_id, reviewer_id, submitted_at)
);

CREATE TABLE review_comment (
    comment_id BIGSERIAL PRIMARY KEY,
    review_id BIGINT NOT NULL REFERENCES review(review_id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    line_number INTEGER NOT NULL CHECK (line_number > 0),
    body TEXT NOT NULL,
    resolved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE status_check (
    status_check_id BIGSERIAL PRIMARY KEY,
    pull_request_id BIGINT NOT NULL REFERENCES pull_request(pull_request_id) ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    passed BOOLEAN NOT NULL,
    duration_seconds INTEGER NOT NULL CHECK (duration_seconds >= 0),
    completed_at TIMESTAMPTZ,
    UNIQUE (pull_request_id, check_name)
);

CREATE TABLE branch_protection (
    protection_id BIGSERIAL PRIMARY KEY,
    branch_id BIGINT NOT NULL UNIQUE REFERENCES branch(branch_id) ON DELETE CASCADE,
    required_approvals INTEGER NOT NULL DEFAULT 0 CHECK (required_approvals >= 0),
    require_status_checks BOOLEAN NOT NULL DEFAULT TRUE,
    prohibit_force_push BOOLEAN NOT NULL DEFAULT TRUE,
    prohibit_deletion BOOLEAN NOT NULL DEFAULT TRUE,
    require_conversation_resolution BOOLEAN NOT NULL DEFAULT TRUE,
    require_linear_history BOOLEAN NOT NULL DEFAULT FALSE,
    restrict_direct_push BOOLEAN NOT NULL DEFAULT TRUE,
    dismiss_stale_approvals BOOLEAN NOT NULL DEFAULT TRUE,
    allow_admin_bypass BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE approval_snapshot (
    approval_snapshot_id BIGSERIAL PRIMARY KEY,
    pull_request_id BIGINT NOT NULL REFERENCES pull_request(pull_request_id) ON DELETE CASCADE,
    commit_id BIGINT REFERENCES commit_record(commit_id),
    reviewer_id BIGINT NOT NULL REFERENCES contributor(contributor_id),
    approved_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    dismissed_at TIMESTAMPTZ,
    stale BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX idx_pr_target_state
    ON pull_request(target_branch_id, state);

CREATE INDEX idx_review_pr_state
    ON review(pull_request_id, state);

CREATE INDEX idx_status_pr_passed
    ON status_check(pull_request_id, passed);

CREATE INDEX idx_commit_pr
    ON commit_record(pull_request_id);

INSERT INTO repository (repository_name)
VALUES ('monotonic-stack-governance');

INSERT INTO branch (repository_id, branch_name, protected)
SELECT repository_id, 'main', TRUE
FROM repository
WHERE repository_name = 'monotonic-stack-governance';

INSERT INTO branch (repository_id, branch_name)
SELECT repository_id, 'feature/monotonic-review-engine'
FROM repository
WHERE repository_name = 'monotonic-stack-governance';

INSERT INTO contributor (username)
VALUES
    ('alice'),
    ('bob'),
    ('carol'),
    ('david');

INSERT INTO branch_protection (
    branch_id,
    required_approvals,
    require_status_checks,
    prohibit_force_push,
    prohibit_deletion,
    require_conversation_resolution,
    require_linear_history,
    restrict_direct_push,
    dismiss_stale_approvals
)
SELECT
    branch_id,
    2,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    TRUE
FROM branch
WHERE branch_name = 'main';

INSERT INTO pull_request (
    repository_id,
    author_id,
    source_branch_id,
    target_branch_id,
    title,
    state,
    is_draft,
    merge_conflict,
    linear_history
)
SELECT
    r.repository_id,
    author.contributor_id,
    source.branch_id,
    target.branch_id,
    'Introduce monotonic-stack review metrics',
    'open',
    FALSE,
    FALSE,
    TRUE
FROM repository r
JOIN contributor author ON author.username = 'alice'
JOIN branch source
    ON source.repository_id = r.repository_id
   AND source.branch_name = 'feature/monotonic-review-engine'
JOIN branch target
    ON target.repository_id = r.repository_id
   AND target.branch_name = 'main'
WHERE r.repository_name = 'monotonic-stack-governance';

INSERT INTO commit_record (pull_request_id, commit_hash)
SELECT pull_request_id, value
FROM pull_request,
     unnest(ARRAY['a91f001', 'a91f002', 'a91f003']) AS value;

INSERT INTO review (pull_request_id, reviewer_id, state)
SELECT pr.pull_request_id, c.contributor_id, v.review_state
FROM pull_request pr
JOIN contributor c ON c.username = v.username
CROSS JOIN (
    VALUES
        ('bob', 'approved'::review_state),
        ('carol', 'approved'::review_state),
        ('david', 'commented'::review_state)
) AS v(username, review_state)
WHERE pr.title = 'Introduce monotonic-stack review metrics';

INSERT INTO review_comment (
    review_id,
    file_path,
    line_number,
    body,
    resolved
)
SELECT
    review_id,
    'src/merge_policy.cpp',
    84,
    'The conflict state must be evaluated before merge eligibility is granted.',
    TRUE
FROM review
WHERE state = 'commented'
LIMIT 1;

INSERT INTO status_check (
    pull_request_id,
    check_name,
    passed,
    duration_seconds,
    completed_at
)
SELECT
    pull_request_id,
    check_name,
    passed,
    duration_seconds,
    now()
FROM pull_request
CROSS JOIN (
    VALUES
        ('unit-tests', TRUE, 48),
        ('static-analysis', TRUE, 31),
        ('integration-tests', TRUE, 73)
) AS checks(check_name, passed, duration_seconds);

CREATE OR REPLACE FUNCTION mark_stale_approvals()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE approval_snapshot
    SET stale = TRUE
    WHERE pull_request_id = NEW.pull_request_id
      AND stale = FALSE
      AND commit_id IS DISTINCT FROM NEW.commit_id;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_commit_stales_approvals
AFTER INSERT ON commit_record
FOR EACH ROW
EXECUTE FUNCTION mark_stale_approvals();

CREATE OR REPLACE VIEW merge_eligibility AS
WITH active_approvals AS (
    SELECT
        pr.pull_request_id,
        COUNT(DISTINCT r.reviewer_id) AS approval_count
    FROM pull_request pr
    JOIN review r
      ON r.pull_request_id = pr.pull_request_id
     AND r.state = 'approved'
     AND r.dismissed_at IS NULL
    GROUP BY pr.pull_request_id
),
check_results AS (
    SELECT
        pull_request_id,
        COUNT(*) AS total_checks,
        COUNT(*) FILTER (WHERE passed) AS passed_checks
    FROM status_check
    GROUP BY pull_request_id
),
open_comments AS (
    SELECT
        r.pull_request_id,
        COUNT(*) AS unresolved_comments
    FROM review r
    JOIN review_comment rc ON rc.review_id = r.review_id
    WHERE rc.resolved = FALSE
    GROUP BY r.pull_request_id
)
SELECT
    pr.pull_request_id,
    pr.title,
    pr.state,
    pr.is_draft,
    pr.merge_conflict,
    pr.linear_history,
    bp.required_approvals,
    COALESCE(aa.approval_count, 0) AS approval_count,
    COALESCE(cr.total_checks, 0) AS total_checks,
    COALESCE(cr.passed_checks, 0) AS passed_checks,
    COALESCE(oc.unresolved_comments, 0) AS unresolved_comments,
    (
        pr.state = 'open'
        AND NOT pr.is_draft
        AND NOT pr.merge_conflict
        AND pr.linear_history = bp.require_linear_history OR
        (
            pr.state = 'open'
            AND NOT pr.is_draft
            AND NOT pr.merge_conflict
            AND (
                NOT bp.require_linear_history
                OR pr.linear_history
            )
            AND COALESCE(aa.approval_count, 0) >= bp.required_approvals
            AND (
                NOT bp.require_status_checks
                OR (
                    COALESCE(cr.total_checks, 0) > 0
                    AND COALESCE(cr.total_checks, 0) =
                        COALESCE(cr.passed_checks, 0)
                )
            )
            AND (
                NOT bp.require_conversation_resolution
                OR COALESCE(oc.unresolved_comments, 0) = 0
            )
        )
    ) AS mergeable
FROM pull_request pr
JOIN branch_protection bp
    ON bp.branch_id = pr.target_branch_id
LEFT JOIN active_approvals aa
    ON aa.pull_request_id = pr.pull_request_id
LEFT JOIN check_results cr
    ON cr.pull_request_id = pr.pull_request_id
LEFT JOIN open_comments oc
    ON oc.pull_request_id = pr.pull_request_id;

SELECT
    pull_request_id,
    title,
    approval_count,
    required_approvals,
    total_checks,
    passed_checks,
    unresolved_comments,
    mergeable
FROM merge_eligibility;

SELECT
    pr.pull_request_id,
    c.username AS reviewer,
    r.state,
    r.submitted_at
FROM pull_request pr
JOIN review r ON r.pull_request_id = pr.pull_request_id
JOIN contributor c ON c.contributor_id = r.reviewer_id
ORDER BY pr.pull_request_id, r.submitted_at;

SELECT
    pr.pull_request_id,
    sc.check_name,
    sc.passed,
    sc.duration_seconds
FROM pull_request pr
JOIN status_check sc ON sc.pull_request_id = pr.pull_request_id
WHERE sc.passed = FALSE
   OR sc.duration_seconds > 120
ORDER BY sc.duration_seconds DESC;

WITH RECURSIVE monotonic_example AS (
    SELECT
        1 AS position,
        2 AS value,
        ARRAY[2]::INTEGER[] AS stack_values
    UNION ALL
    SELECT
        position + 1,
        value,
        CASE
            WHEN stack_values[array_length(stack_values, 1)] <= value
                THEN stack_values || value
            ELSE ARRAY[value]
        END
    FROM monotonic_example
    WHERE position < 5
)
SELECT *
FROM monotonic_example;

BEGIN;

UPDATE pull_request
SET merge_conflict = TRUE
WHERE title = 'Introduce monotonic-stack review metrics';

SELECT
    pull_request_id,
    mergeable
FROM merge_eligibility
WHERE title = 'Introduce monotonic-stack review metrics';

ROLLBACK;

SELECT
    pr.pull_request_id,
    pr.title,
    bp.required_approvals,
    COALESCE(aa.approval_count, 0) AS approvals,
    CASE
        WHEN pr.is_draft THEN 'blocked: draft'
        WHEN pr.merge_conflict THEN 'blocked: conflict'
        WHEN COALESCE(aa.approval_count, 0) < bp.required_approvals
            THEN 'blocked: insufficient approvals'
        WHEN bp.require_status_checks
             AND COALESCE(cr.total_checks, 0) = 0
            THEN 'blocked: no status checks'
        WHEN bp.require_status_checks
             AND COALESCE(cr.total_checks, 0) <> COALESCE(cr.passed_checks, 0)
            THEN 'blocked: failed status checks'
        ELSE 'eligible'
    END AS governance_result
FROM pull_request pr
JOIN branch_protection bp
    ON bp.branch_id = pr.target_branch_id
LEFT JOIN (
    SELECT pull_request_id, COUNT(*) AS approval_count
    FROM review
    WHERE state = 'approved'
      AND dismissed_at IS NULL
    GROUP BY pull_request_id
) aa ON aa.pull_request_id = pr.pull_request_id
LEFT JOIN (
    SELECT
        pull_request_id,
        COUNT(*) AS total_checks,
        COUNT(*) FILTER (WHERE passed) AS passed_checks
    FROM status_check
    GROUP BY pull_request_id
) cr ON cr.pull_request_id = pr.pull_request_id;
