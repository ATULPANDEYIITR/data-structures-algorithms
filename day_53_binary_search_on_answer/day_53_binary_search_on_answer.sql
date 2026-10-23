DROP SCHEMA IF EXISTS answer_search_lab CASCADE;
CREATE SCHEMA answer_search_lab;
SET search_path TO answer_search_lab;

-- Binary search on answer treats the candidate result as the search space.
-- The database stores allocation scenarios and evaluates whether a
-- candidate capacity satisfies an operational constraint.

CREATE TABLE allocation_problem (
    problem_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    problem_name text NOT NULL UNIQUE,
    description text NOT NULL
);

CREATE TABLE workload_item (
    item_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    problem_id bigint NOT NULL REFERENCES allocation_problem(problem_id)
        ON DELETE CASCADE,
    sequence_no integer NOT NULL,
    workload bigint NOT NULL CHECK (workload > 0),
    UNIQUE (problem_id, sequence_no)
);

CREATE TABLE allocation_policy (
    policy_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    policy_name text NOT NULL UNIQUE,
    max_groups integer NOT NULL CHECK (max_groups > 0),
    objective text NOT NULL CHECK (
        objective IN ('MINIMIZE_MAX_LOAD', 'MAXIMIZE_MIN_LOAD')
    )
);

CREATE TABLE repository_workflow (
    workflow_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_name text NOT NULL UNIQUE,
    source_branch text NOT NULL,
    target_branch text NOT NULL,
    branch_synchronized boolean NOT NULL DEFAULT false,
    conflicts_resolved boolean NOT NULL DEFAULT false,
    approvals integer NOT NULL DEFAULT 0 CHECK (approvals >= 0),
    successful_checks integer NOT NULL DEFAULT 0 CHECK (successful_checks >= 0),
    unresolved_conversations integer NOT NULL DEFAULT 0
        CHECK (unresolved_conversations >= 0)
);

CREATE TABLE branch_protection (
    branch_protection_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    workflow_id bigint NOT NULL UNIQUE
        REFERENCES repository_workflow(workflow_id)
        ON DELETE CASCADE,
    required_approvals integer NOT NULL DEFAULT 0
        CHECK (required_approvals >= 0),
    required_status_checks integer NOT NULL DEFAULT 0
        CHECK (required_status_checks >= 0),
    require_sync boolean NOT NULL DEFAULT true,
    require_resolved_conversations boolean NOT NULL DEFAULT true,
    restrict_direct_push boolean NOT NULL DEFAULT true,
    restrict_force_push boolean NOT NULL DEFAULT true,
    restrict_deletion boolean NOT NULL DEFAULT true
);

CREATE INDEX workload_item_problem_sequence_idx
    ON workload_item(problem_id, sequence_no);

INSERT INTO allocation_problem (problem_name, description)
VALUES
    (
        'Package Shipping',
        'Find the smallest daily capacity that ships all packages in order.'
    ),
    (
        'Processing Capacity',
        'Find the smallest worker capacity for an ordered workload.'
    );

INSERT INTO workload_item (problem_id, sequence_no, workload)
SELECT p.problem_id, v.sequence_no, v.workload
FROM allocation_problem p
JOIN (
    VALUES
        ('Package Shipping', 1, 1::bigint),
        ('Package Shipping', 2, 2::bigint),
        ('Package Shipping', 3, 3::bigint),
        ('Package Shipping', 4, 1::bigint),
        ('Package Shipping', 5, 1::bigint),
        ('Package Shipping', 6, 1::bigint),
        ('Package Shipping', 7, 1::bigint),
        ('Processing Capacity', 1, 11::bigint),
        ('Processing Capacity', 2, 7::bigint),
        ('Processing Capacity', 3, 5::bigint),
        ('Processing Capacity', 4, 9::bigint),
        ('Processing Capacity', 5, 13::bigint),
        ('Processing Capacity', 6, 6::bigint)
) AS v(problem_name, sequence_no, workload)
    ON v.problem_name = p.problem_name;

INSERT INTO allocation_policy
    (policy_name, max_groups, objective)
VALUES
    ('Four shipping days', 4, 'MINIMIZE_MAX_LOAD'),
    ('Three processing workers', 3, 'MINIMIZE_MAX_LOAD');

INSERT INTO repository_workflow
    (
        repository_name,
        source_branch,
        target_branch,
        branch_synchronized,
        conflicts_resolved,
        approvals,
        successful_checks,
        unresolved_conversations
    )
VALUES
    (
        'platform-api',
        'feature/capacity-policy',
        'main',
        true,
        true,
        2,
        4,
        0
    ),
    (
        'analytics-service',
        'feature/allocation',
        'main',
        false,
        true,
        3,
        4,
        0
    );

INSERT INTO branch_protection
    (
        workflow_id,
        required_approvals,
        required_status_checks,
        require_sync,
        require_resolved_conversations
    )
SELECT
    workflow_id,
    2,
    3,
    true,
    true
FROM repository_workflow
WHERE repository_name = 'platform-api';

INSERT INTO branch_protection
    (
        workflow_id,
        required_approvals,
        required_status_checks,
        require_sync,
        require_resolved_conversations
    )
SELECT
    workflow_id,
    2,
    3,
    true,
    true
FROM repository_workflow
WHERE repository_name = 'analytics-service';

CREATE OR REPLACE FUNCTION can_allocate(
    p_problem_id bigint,
    p_candidate_capacity bigint,
    p_max_groups integer
)
RETURNS boolean
LANGUAGE plpgsql
AS $$
DECLARE
    current_load bigint := 0;
    groups_used integer := 1;
    item_record record;
BEGIN
    IF p_candidate_capacity <= 0 OR p_max_groups <= 0 THEN
        RETURN false;
    END IF;

    FOR item_record IN
        SELECT workload
        FROM workload_item
        WHERE problem_id = p_problem_id
        ORDER BY sequence_no
    LOOP
        IF item_record.workload > p_candidate_capacity THEN
            RETURN false;
        END IF;

        IF current_load + item_record.workload <= p_candidate_capacity THEN
            current_load := current_load + item_record.workload;
        ELSE
            groups_used := groups_used + 1;
            current_load := item_record.workload;

            IF groups_used > p_max_groups THEN
                RETURN false;
            END IF;
        END IF;
    END LOOP;

    RETURN true;
END;
$$;

CREATE OR REPLACE FUNCTION minimum_feasible_capacity(
    p_problem_id bigint,
    p_max_groups integer
)
RETURNS bigint
LANGUAGE plpgsql
AS $$
DECLARE
    low_value bigint;
    high_value bigint;
    middle_value bigint;
    answer bigint := NULL;
BEGIN
    SELECT
        max(workload),
        sum(workload)
    INTO low_value, high_value
    FROM workload_item
    WHERE problem_id = p_problem_id;

    IF low_value IS NULL THEN
        RAISE EXCEPTION 'Problem % has no workload items', p_problem_id;
    END IF;

    IF p_max_groups <= 0 THEN
        RAISE EXCEPTION 'p_max_groups must be positive';
    END IF;

    WHILE low_value <= high_value LOOP
        middle_value :=
            low_value + (high_value - low_value) / 2;

        IF can_allocate(
            p_problem_id,
            middle_value,
            p_max_groups
        ) THEN
            answer := middle_value;
            high_value := middle_value - 1;
        ELSE
            low_value := middle_value + 1;
        END IF;
    END LOOP;

    RETURN answer;
END;
$$;

CREATE OR REPLACE FUNCTION validate_branch_governance(
    p_workflow_id bigint
)
RETURNS boolean
LANGUAGE plpgsql
AS $$
DECLARE
    workflow_row repository_workflow%ROWTYPE;
    policy_row branch_protection%ROWTYPE;
BEGIN
    SELECT *
    INTO workflow_row
    FROM repository_workflow
    WHERE workflow_id = p_workflow_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Workflow % does not exist', p_workflow_id;
    END IF;

    SELECT *
    INTO policy_row
    FROM branch_protection
    WHERE workflow_id = p_workflow_id;

    IF NOT FOUND THEN
        RETURN true;
    END IF;

    IF policy_row.require_sync
       AND NOT workflow_row.branch_synchronized THEN
        RETURN false;
    END IF;

    IF NOT workflow_row.conflicts_resolved THEN
        RETURN false;
    END IF;

    IF workflow_row.approvals < policy_row.required_approvals THEN
        RETURN false;
    END IF;

    IF workflow_row.successful_checks <
       policy_row.required_status_checks THEN
        RETURN false;
    END IF;

    IF policy_row.require_resolved_conversations
       AND workflow_row.unresolved_conversations > 0 THEN
        RETURN false;
    END IF;

    RETURN true;
END;
$$;

CREATE OR REPLACE VIEW merge_eligibility AS
SELECT
    w.repository_name,
    w.source_branch,
    w.target_branch,
    w.approvals,
    p.required_approvals,
    w.successful_checks,
    p.required_status_checks,
    w.branch_synchronized,
    w.conflicts_resolved,
    w.unresolved_conversations,
    validate_branch_governance(w.workflow_id) AS merge_eligible
FROM repository_workflow w
LEFT JOIN branch_protection p
    ON p.workflow_id = w.workflow_id;

-- Basic feasibility reports.

SELECT
    p.problem_name,
    ap.max_groups,
    minimum_feasible_capacity(
        p.problem_id,
        ap.max_groups
    ) AS minimum_capacity
FROM allocation_problem p
JOIN allocation_policy ap
    ON ap.policy_name = CASE
        WHEN p.problem_name = 'Package Shipping'
            THEN 'Four shipping days'
        WHEN p.problem_name = 'Processing Capacity'
            THEN 'Three processing workers'
    END
ORDER BY p.problem_id;

-- Direct feasibility evaluation illustrates the monotonic predicate.

SELECT
    candidate_capacity,
    can_allocate(
        (
            SELECT problem_id
            FROM allocation_problem
            WHERE problem_name = 'Package Shipping'
        ),
        candidate_capacity,
        4
    ) AS feasible
FROM generate_series(3, 10) AS candidate_capacity;

-- CTE-based reporting identifies the largest workload and total workload
-- before calculating the answer-space bounds.

WITH workload_bounds AS (
    SELECT
        problem_id,
        max(workload) AS minimum_possible_capacity,
        sum(workload) AS maximum_possible_capacity,
        count(*) AS item_count
    FROM workload_item
    GROUP BY problem_id
)
SELECT
    p.problem_name,
    b.minimum_possible_capacity,
    b.maximum_possible_capacity,
    b.item_count
FROM allocation_problem p
JOIN workload_bounds b
    ON b.problem_id = p.problem_id
ORDER BY p.problem_id;

SELECT *
FROM merge_eligibility
ORDER BY repository_name;

-- Transactional policy update. The state is validated before COMMIT.

BEGIN;

UPDATE repository_workflow
SET successful_checks = successful_checks + 1
WHERE repository_name = 'platform-api';

DO $$
BEGIN
    IF NOT (
        SELECT validate_branch_governance(workflow_id)
        FROM repository_workflow
        WHERE repository_name = 'platform-api'
    ) THEN
        RAISE EXCEPTION
            'platform-api cannot satisfy branch protection';
    END IF;
END;
$$;

COMMIT;

-- A deliberately invalid state is rolled back rather than persisted.

BEGIN;

UPDATE repository_workflow
SET unresolved_conversations = 2
WHERE repository_name = 'platform-api';

DO $$
BEGIN
    IF (
        SELECT validate_branch_governance(workflow_id)
        FROM repository_workflow
        WHERE repository_name = 'platform-api'
    ) THEN
        RAISE EXCEPTION
            'Expected merge eligibility to fail';
    END IF;
END;
$$;

ROLLBACK;

SELECT
    repository_name,
    merge_eligible
FROM merge_eligibility
ORDER BY repository_name;
