DROP SCHEMA IF EXISTS circular_queue_governance CASCADE;

CREATE SCHEMA circular_queue_governance;

SET search_path TO circular_queue_governance;

CREATE TABLE repositories (
    repository_id BIGSERIAL PRIMARY KEY,
    repository_name TEXT NOT NULL UNIQUE,
    default_branch TEXT NOT NULL DEFAULT 'main',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE branches (
    branch_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    branch_name TEXT NOT NULL,
    is_protected BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (repository_id, branch_name)
);

CREATE TABLE users (
    user_id BIGSERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE pull_requests (
    pull_request_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    author_id BIGINT NOT NULL REFERENCES users(user_id),
    source_branch_id BIGINT NOT NULL REFERENCES branches(branch_id),
    target_branch_id BIGINT NOT NULL REFERENCES branches(branch_id),
    title TEXT NOT NULL,
    state TEXT NOT NULL DEFAULT 'draft',
    is_draft BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (state IN ('draft', 'open', 'closed', 'merged')),
    CHECK (title <> ''),
    CHECK (
        (is_draft = TRUE AND state = 'draft')
        OR
        (is_draft = FALSE AND state <> 'draft')
    ),
    CHECK (source_branch_id <> target_branch_id)
);

CREATE TABLE commits (
    commit_id BIGSERIAL PRIMARY KEY,
    pull_request_id BIGINT NOT NULL REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    sha CHAR(40) NOT NULL UNIQUE,
    committed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE reviews (
    review_id BIGSERIAL PRIMARY KEY,
    pull_request_id BIGINT NOT NULL REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    reviewer_id BIGINT NOT NULL REFERENCES users(user_id),
    review_state TEXT NOT NULL,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dismissed_at TIMESTAMPTZ,
    CHECK (
        review_state IN (
            'commented',
            'changes_requested',
            'approved',
            'dismissed'
        )
    ),
    CHECK (
        (review_state = 'dismissed' AND dismissed_at IS NOT NULL)
        OR
        (review_state <> 'dismissed')
    )
);

CREATE TABLE review_comments (
    comment_id BIGSERIAL PRIMARY KEY,
    review_id BIGINT NOT NULL REFERENCES reviews(review_id)
        ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    line_number INTEGER NOT NULL CHECK (line_number > 0),
    body TEXT NOT NULL,
    resolved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (body <> '')
);

CREATE TABLE status_checks (
    status_check_id BIGSERIAL PRIMARY KEY,
    pull_request_id BIGINT NOT NULL REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    check_name TEXT NOT NULL,
    required BOOLEAN NOT NULL DEFAULT FALSE,
    status TEXT NOT NULL,
    completed_at TIMESTAMPTZ,
    CHECK (status IN ('pending', 'passed', 'failed')),
    UNIQUE (pull_request_id, check_name)
);

CREATE TABLE branch_protection_policies (
    policy_id BIGSERIAL PRIMARY KEY,
    branch_id BIGINT NOT NULL UNIQUE REFERENCES branches(branch_id)
        ON DELETE CASCADE,
    required_approvals INTEGER NOT NULL DEFAULT 0,
    require_status_checks BOOLEAN NOT NULL DEFAULT FALSE,
    prohibit_direct_push BOOLEAN NOT NULL DEFAULT TRUE,
    prohibit_force_push BOOLEAN NOT NULL DEFAULT TRUE,
    prohibit_deletion BOOLEAN NOT NULL DEFAULT TRUE,
    require_conversation_resolution BOOLEAN NOT NULL DEFAULT FALSE,
    require_linear_history BOOLEAN NOT NULL DEFAULT FALSE,
    CHECK (required_approvals >= 0)
);

CREATE TABLE approval_requirements (
    requirement_id BIGSERIAL PRIMARY KEY,
    policy_id BIGINT NOT NULL REFERENCES branch_protection_policies(policy_id)
        ON DELETE CASCADE,
    reviewer_id BIGINT REFERENCES users(user_id),
    required BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (policy_id, reviewer_id)
);

CREATE TABLE queue_events (
    queue_position BIGSERIAL PRIMARY KEY,
    pull_request_id BIGINT NOT NULL REFERENCES pull_requests(pull_request_id)
        ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    queued_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMPTZ,
    CHECK (
        event_type IN (
            'opened',
            'synchronized',
            'review_submitted',
            'status_check_completed',
            'merge_requested',
            'closed'
        )
    )
);

CREATE INDEX idx_pull_requests_repository_state
    ON pull_requests(repository_id, state);

CREATE INDEX idx_pull_requests_target_branch
    ON pull_requests(target_branch_id, state);

CREATE INDEX idx_reviews_pull_request_state
    ON reviews(pull_request_id, review_state);

CREATE INDEX idx_status_checks_pull_request
    ON status_checks(pull_request_id, required, status);

CREATE INDEX idx_queue_events_unprocessed
    ON queue_events(processed_at, queued_at)
    WHERE processed_at IS NULL;

INSERT INTO repositories (repository_name)
VALUES ('payments-service');

INSERT INTO users (username)
VALUES
    ('atul'),
    ('alice'),
    ('bob'),
    ('carol'),
    ('automation');

INSERT INTO branches (repository_id, branch_name, is_protected)
SELECT repository_id, 'main', TRUE
FROM repositories
WHERE repository_name = 'payments-service';

INSERT INTO branches (repository_id, branch_name, is_protected)
SELECT repository_id, 'feature/refund-validation', FALSE
FROM repositories
WHERE repository_name = 'payments-service';

INSERT INTO branch_protection_policies (
    branch_id,
    required_approvals,
    require_status_checks,
    prohibit_direct_push,
    prohibit_force_push,
    prohibit_deletion,
    require_conversation_resolution,
    require_linear_history
)
SELECT
    branch_id,
    2,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    TRUE
FROM branches
WHERE branch_name = 'main';

INSERT INTO pull_requests (
    repository_id,
    author_id,
    source_branch_id,
    target_branch_id,
    title,
    state,
    is_draft
)
SELECT
    r.repository_id,
    author.user_id,
    source.branch_id,
    target.branch_id,
    'Validate refund requests before persistence',
    'open',
    FALSE
FROM repositories r
JOIN users author ON author.username = 'atul'
JOIN branches source
    ON source.repository_id = r.repository_id
   AND source.branch_name = 'feature/refund-validation'
JOIN branches target
    ON target.repository_id = r.repository_id
   AND target.branch_name = 'main'
WHERE r.repository_name = 'payments-service';

INSERT INTO commits (pull_request_id, sha)
SELECT
    pull_request_id,
    '1111111111111111111111111111111111111111'
FROM pull_requests
WHERE title = 'Validate refund requests before persistence';

INSERT INTO reviews (
    pull_request_id,
    reviewer_id,
    review_state
)
SELECT pr.pull_request_id, u.user_id, 'approved'
FROM pull_requests pr
JOIN users u ON u.username = 'alice'
WHERE pr.title = 'Validate refund requests before persistence';

INSERT INTO reviews (
    pull_request_id,
    reviewer_id,
    review_state
)
SELECT pr.pull_request_id, u.user_id, 'changes_requested'
FROM pull_requests pr
JOIN users u ON u.username = 'bob'
WHERE pr.title = 'Validate refund requests before persistence';

INSERT INTO reviews (
    pull_request_id,
    reviewer_id,
    review_state
)
SELECT pr.pull_request_id, u.user_id, 'approved'
FROM pull_requests pr
JOIN users u ON u.username = 'automation'
WHERE pr.title = 'Validate refund requests before persistence';

INSERT INTO review_comments (
    review_id,
    file_path,
    line_number,
    body
)
SELECT
    review_id,
    'src/refund_validator.py',
    42,
    'Validate the refund state before applying the persistence operation.'
FROM reviews
WHERE review_state = 'changes_requested';

INSERT INTO status_checks (
    pull_request_id,
    check_name,
    required,
    status,
    completed_at
)
SELECT
    pull_request_id,
    'unit-tests',
    TRUE,
    'passed',
    CURRENT_TIMESTAMP
FROM pull_requests
WHERE title = 'Validate refund requests before persistence';

INSERT INTO status_checks (
    pull_request_id,
    check_name,
    required,
    status,
    completed_at
)
SELECT
    pull_request_id,
    'security-scan',
    TRUE,
    'passed',
    CURRENT_TIMESTAMP
FROM pull_requests
WHERE title = 'Validate refund requests before persistence';

INSERT INTO queue_events (pull_request_id, event_type)
SELECT pull_request_id, 'opened'
FROM pull_requests
WHERE title = 'Validate refund requests before persistence';

INSERT INTO queue_events (pull_request_id, event_type)
SELECT pull_request_id, 'review_submitted'
FROM pull_requests
WHERE title = 'Validate refund requests before persistence';

INSERT INTO queue_events (pull_request_id, event_type)
SELECT pull_request_id, 'status_check_completed'
FROM pull_requests
WHERE title = 'Validate refund requests before persistence';

CREATE VIEW merge_eligibility AS
WITH eligible_approvals AS (
    SELECT
        r.pull_request_id,
        COUNT(*) AS approval_count
    FROM reviews r
    JOIN users u
      ON u.user_id = r.reviewer_id
    WHERE r.review_state = 'approved'
      AND r.dismissed_at IS NULL
      AND u.active = TRUE
      AND u.username <> 'automation'
    GROUP BY r.pull_request_id
),
required_checks AS (
    SELECT
        sc.pull_request_id,
        BOOL_AND(sc.status = 'passed') AS checks_pass
    FROM status_checks sc
    WHERE sc.required = TRUE
    GROUP BY sc.pull_request_id
),
open_conversations AS (
    SELECT
        r.pull_request_id,
        COUNT(*) AS unresolved_comments
    FROM review_comments rc
    JOIN reviews r
      ON r.review_id = rc.review_id
    WHERE rc.resolved = FALSE
    GROUP BY r.pull_request_id
)
SELECT
    pr.pull_request_id,
    pr.title,
    bp.required_approvals,
    COALESCE(ea.approval_count, 0) AS valid_approvals,
    bp.require_status_checks,
    COALESCE(rc.checks_pass, FALSE) AS required_checks_pass,
    COALESCE(oc.unresolved_comments, 0) AS unresolved_comments,
    CASE
        WHEN pr.state <> 'open'
            THEN FALSE
        WHEN COALESCE(ea.approval_count, 0) < bp.required_approvals
            THEN FALSE
        WHEN bp.require_status_checks
             AND NOT COALESCE(rc.checks_pass, FALSE)
            THEN FALSE
        WHEN bp.require_conversation_resolution
             AND COALESCE(oc.unresolved_comments, 0) > 0
            THEN FALSE
        ELSE TRUE
    END AS merge_eligible
FROM pull_requests pr
JOIN branch_protection_policies bp
  ON bp.branch_id = pr.target_branch_id
LEFT JOIN eligible_approvals ea
  ON ea.pull_request_id = pr.pull_request_id
LEFT JOIN required_checks rc
  ON rc.pull_request_id = pr.pull_request_id
LEFT JOIN open_conversations oc
  ON oc.pull_request_id = pr.pull_request_id;

SELECT *
FROM merge_eligibility;

SELECT
    pr.pull_request_id,
    pr.title,
    r.username AS reviewer,
    rv.review_state,
    rv.dismissed_at
FROM pull_requests pr
JOIN reviews rv
  ON rv.pull_request_id = pr.pull_request_id
JOIN users r
  ON r.user_id = rv.reviewer_id
ORDER BY pr.pull_request_id, rv.submitted_at;

SELECT
    pr.pull_request_id,
    pr.title,
    sc.check_name,
    sc.status,
    sc.required
FROM pull_requests pr
JOIN status_checks sc
  ON sc.pull_request_id = pr.pull_request_id
ORDER BY pr.pull_request_id, sc.check_name;

BEGIN;

SELECT
    pull_request_id,
    title,
    state
FROM pull_requests
WHERE pull_request_id = (
    SELECT MIN(pull_request_id)
    FROM pull_requests
)
FOR UPDATE;

UPDATE queue_events
SET processed_at = CURRENT_TIMESTAMP
WHERE queue_position = (
    SELECT MIN(queue_position)
    FROM queue_events
    WHERE processed_at IS NULL
);

COMMIT;

SELECT
    queue_position,
    pull_request_id,
    event_type,
    queued_at,
    processed_at
FROM queue_events
ORDER BY queue_position;

DO $$
DECLARE
    duplicate_sha_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO duplicate_sha_count
    FROM commits
    WHERE sha = '1111111111111111111111111111111111111111';

    IF duplicate_sha_count <> 1 THEN
        RAISE EXCEPTION 'Commit uniqueness invariant failed.';
    END IF;
END;
$$;
