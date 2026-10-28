DROP SCHEMA IF EXISTS quick_sort_lab CASCADE;
CREATE SCHEMA quick_sort_lab;

SET search_path = quick_sort_lab, public;

-- The model stores sorting jobs separately from individual input values.
-- This permits reproducible experiments comparing pivot and partition policies.

CREATE TYPE pivot_strategy AS ENUM (
    'first',
    'last',
    'middle',
    'median_of_three',
    'random'
);

CREATE TYPE partition_strategy AS ENUM (
    'lomuto',
    'hoare'
);

CREATE TYPE job_status AS ENUM (
    'created',
    'running',
    'completed',
    'failed'
);

CREATE TABLE sorting_jobs (
    job_id              BIGSERIAL PRIMARY KEY,
    job_name            TEXT NOT NULL UNIQUE,
    pivot_policy        pivot_strategy NOT NULL,
    partition_policy    partition_strategy NOT NULL,
    status              job_status NOT NULL DEFAULT 'created',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    started_at          TIMESTAMPTZ,
    completed_at        TIMESTAMPTZ,
    failure_reason      TEXT,
    CONSTRAINT valid_job_times CHECK (
        completed_at IS NULL
        OR started_at IS NULL
        OR completed_at >= started_at
    ),
    CONSTRAINT valid_failure_state CHECK (
        (status = 'failed' AND failure_reason IS NOT NULL)
        OR status <> 'failed'
    )
);

CREATE TABLE input_values (
    job_id       BIGINT NOT NULL REFERENCES sorting_jobs(job_id)
                 ON DELETE CASCADE,
    position_no  INTEGER NOT NULL,
    value        BIGINT NOT NULL,
    PRIMARY KEY (job_id, position_no),
    CONSTRAINT non_negative_position CHECK (position_no >= 0)
);

CREATE TABLE algorithm_runs (
    run_id              BIGSERIAL PRIMARY KEY,
    job_id              BIGINT NOT NULL REFERENCES sorting_jobs(job_id)
                        ON DELETE CASCADE,
    input_size          INTEGER NOT NULL,
    comparisons         BIGINT NOT NULL DEFAULT 0,
    swaps               BIGINT NOT NULL DEFAULT 0,
    partitions          BIGINT NOT NULL DEFAULT 0,
    max_stack_depth     INTEGER NOT NULL DEFAULT 0,
    elapsed_microseconds BIGINT,
    sorted_correctly    BOOLEAN,
    recorded_at         TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT non_negative_metrics CHECK (
        input_size >= 0
        AND comparisons >= 0
        AND swaps >= 0
        AND partitions >= 0
        AND max_stack_depth >= 0
        AND (
            elapsed_microseconds IS NULL
            OR elapsed_microseconds >= 0
        )
    )
);

CREATE TABLE sorted_values (
    run_id       BIGINT NOT NULL REFERENCES algorithm_runs(run_id)
                 ON DELETE CASCADE,
    position_no  INTEGER NOT NULL,
    value        BIGINT NOT NULL,
    PRIMARY KEY (run_id, position_no),
    CONSTRAINT non_negative_output_position CHECK (position_no >= 0)
);

CREATE INDEX idx_input_values_job_value
    ON input_values (job_id, value);

CREATE INDEX idx_algorithm_runs_policy
    ON algorithm_runs (job_id, recorded_at DESC);

CREATE OR REPLACE FUNCTION enforce_completed_run()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.sorted_correctly IS TRUE
       AND NOT EXISTS (
           SELECT 1
           FROM sorting_jobs
           WHERE job_id = NEW.job_id
             AND status = 'completed'
       )
    THEN
        RAISE EXCEPTION
            'A run cannot be marked correct until its job is completed';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_enforce_completed_run
BEFORE INSERT OR UPDATE ON algorithm_runs
FOR EACH ROW
EXECUTE FUNCTION enforce_completed_run();

CREATE OR REPLACE FUNCTION start_sort_job(p_job_id BIGINT)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE sorting_jobs
    SET status = 'running',
        started_at = clock_timestamp(),
        failure_reason = NULL
    WHERE job_id = p_job_id
      AND status = 'created';

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Job % is not in created state', p_job_id;
    END IF;
END;
$$;

CREATE OR REPLACE FUNCTION complete_sort_job(
    p_job_id BIGINT,
    p_failure_reason TEXT DEFAULT NULL
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_failure_reason IS NULL THEN
        UPDATE sorting_jobs
        SET status = 'completed',
            completed_at = clock_timestamp()
        WHERE job_id = p_job_id
          AND status = 'running';
    ELSE
        UPDATE sorting_jobs
        SET status = 'failed',
            completed_at = clock_timestamp(),
            failure_reason = p_failure_reason
        WHERE job_id = p_job_id
          AND status = 'running';
    END IF;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Job % is not running', p_job_id;
    END IF;
END;
$$;

CREATE VIEW job_input_statistics AS
SELECT
    j.job_id,
    j.job_name,
    j.pivot_policy,
    j.partition_policy,
    j.status,
    COUNT(i.position_no) AS input_count,
    MIN(i.value) AS minimum_value,
    MAX(i.value) AS maximum_value,
    COUNT(DISTINCT i.value) AS distinct_values
FROM sorting_jobs AS j
LEFT JOIN input_values AS i
    ON i.job_id = j.job_id
GROUP BY
    j.job_id,
    j.job_name,
    j.pivot_policy,
    j.partition_policy,
    j.status;

CREATE VIEW run_performance_report AS
SELECT
    j.job_name,
    j.pivot_policy,
    j.partition_policy,
    r.input_size,
    r.comparisons,
    r.swaps,
    r.partitions,
    r.max_stack_depth,
    r.elapsed_microseconds,
    r.sorted_correctly
FROM algorithm_runs AS r
JOIN sorting_jobs AS j
    ON j.job_id = r.job_id;

-- Reproducible experiments include balanced, ordered, reverse-ordered,
-- and duplicate-heavy inputs because pivot quality strongly affects
-- partition balance.

INSERT INTO sorting_jobs
    (job_name, pivot_policy, partition_policy)
VALUES
    ('random_median_hoare', 'median_of_three', 'hoare'),
    ('sorted_first_hoare', 'first', 'hoare'),
    ('sorted_median_hoare', 'median_of_three', 'hoare'),
    ('reverse_random_hoare', 'random', 'hoare'),
    ('duplicates_median_lomuto', 'median_of_three', 'lomuto'),
    ('small_lomuto_case', 'median_of_three', 'lomuto');

INSERT INTO input_values (job_id, position_no, value)
SELECT
    j.job_id,
    x.position_no,
    x.value
FROM sorting_jobs AS j
CROSS JOIN LATERAL (
    VALUES
        (0, 8::BIGINT),
        (1, 3::BIGINT),
        (2, 7::BIGINT),
        (3, 4::BIGINT),
        (4, 7::BIGINT),
        (5, 1::BIGINT),
        (6, 9::BIGINT),
        (7, 2::BIGINT),
        (8, 6::BIGINT),
        (9, 5::BIGINT)
) AS x(position_no, value)
WHERE j.job_name IN (
    'random_median_hoare',
    'duplicates_median_lomuto',
    'small_lomuto_case'
);

INSERT INTO input_values (job_id, position_no, value)
SELECT
    j.job_id,
    n,
    n::BIGINT
FROM sorting_jobs AS j
CROSS JOIN LATERAL generate_series(0, 99) AS g(n)
WHERE j.job_name = 'sorted_first_hoare';

INSERT INTO input_values (job_id, position_no, value)
SELECT
    j.job_id,
    n,
    (99 - n)::BIGINT
FROM sorting_jobs AS j
CROSS JOIN LATERAL generate_series(0, 99) AS g(n)
WHERE j.job_name = 'reverse_random_hoare';

INSERT INTO input_values (job_id, position_no, value)
SELECT
    j.job_id,
    n,
    7::BIGINT
FROM sorting_jobs AS j
CROSS JOIN LATERAL generate_series(0, 99) AS g(n)
WHERE j.job_name = 'duplicates_median_lomuto';

INSERT INTO input_values (job_id, position_no, value)
SELECT
    j.job_id,
    n,
    n::BIGINT
FROM sorting_jobs AS j
CROSS JOIN LATERAL generate_series(0, 99) AS g(n)
WHERE j.job_name = 'sorted_median_hoare';

-- Transactional workflow for one complete experiment.
BEGIN;

SELECT start_sort_job(job_id)
FROM sorting_jobs
WHERE job_name = 'random_median_hoare';

INSERT INTO algorithm_runs (
    job_id,
    input_size,
    comparisons,
    swaps,
    partitions,
    max_stack_depth,
    elapsed_microseconds,
    sorted_correctly
)
SELECT
    job_id,
    input_count,
    41,
    12,
    9,
    4,
    18,
    NULL
FROM job_input_statistics
WHERE job_name = 'random_median_hoare';

SELECT complete_sort_job(job_id)
FROM sorting_jobs
WHERE job_name = 'random_median_hoare';

UPDATE algorithm_runs AS r
SET sorted_correctly = TRUE
WHERE r.job_id = (
    SELECT job_id
    FROM sorting_jobs
    WHERE job_name = 'random_median_hoare'
)
AND r.run_id = (
    SELECT MAX(run_id)
    FROM algorithm_runs
    WHERE job_id = r.job_id
);

COMMIT;

-- A failed execution remains visible rather than being silently discarded.
BEGIN;

SELECT start_sort_job(job_id)
FROM sorting_jobs
WHERE job_name = 'sorted_first_hoare';

INSERT INTO algorithm_runs (
    job_id,
    input_size,
    comparisons,
    swaps,
    partitions,
    max_stack_depth,
    sorted_correctly
)
SELECT
    job_id,
    input_count,
    5050,
    99,
    99,
    99,
    FALSE
FROM job_input_statistics
WHERE job_name = 'sorted_first_hoare';

SELECT complete_sort_job(
    job_id,
    'First-element pivot produced highly unbalanced partitions for ordered input'
)
FROM sorting_jobs
WHERE job_name = 'sorted_first_hoare';

COMMIT;

-- Retrieval: inspect the input distribution before choosing an algorithm.
SELECT *
FROM job_input_statistics
ORDER BY job_id;

-- Validation: identify runs that do not have a successful sorted result.
SELECT
    j.job_name,
    r.run_id,
    r.sorted_correctly
FROM algorithm_runs AS r
JOIN sorting_jobs AS j
    ON j.job_id = r.job_id
WHERE r.sorted_correctly IS DISTINCT FROM TRUE
ORDER BY r.run_id;

-- Aggregation: compare algorithm policies by observed work.
SELECT
    j.pivot_policy,
    j.partition_policy,
    COUNT(*) AS runs,
    AVG(r.comparisons) AS avg_comparisons,
    AVG(r.swaps) AS avg_swaps,
    AVG(r.max_stack_depth) AS avg_stack_depth
FROM algorithm_runs AS r
JOIN sorting_jobs AS j
    ON j.job_id = r.job_id
GROUP BY j.pivot_policy, j.partition_policy
ORDER BY avg_comparisons;

-- CTE: calculate a normalized comparison ratio.
WITH metrics AS (
    SELECT
        j.job_name,
        r.input_size,
        r.comparisons,
        CASE
            WHEN r.input_size > 0
            THEN ROUND(
                r.comparisons::NUMERIC / r.input_size,
                2
            )
            ELSE 0
        END AS comparisons_per_item
    FROM algorithm_runs AS r
    JOIN sorting_jobs AS j
        ON j.job_id = r.job_id
)
SELECT *
FROM metrics
ORDER BY comparisons_per_item DESC;

-- Evaluation: verify that output positions, if recorded, are ordered.
WITH ordered_outputs AS (
    SELECT
        sv.run_id,
        sv.position_no,
        sv.value,
        LAG(sv.value) OVER (
            PARTITION BY sv.run_id
            ORDER BY sv.position_no
        ) AS previous_value
    FROM sorted_values AS sv
)
SELECT
    run_id,
    COUNT(*) FILTER (
        WHERE previous_value IS NOT NULL
          AND value < previous_value
    ) AS ordering_violations
FROM ordered_outputs
GROUP BY run_id
ORDER BY run_id;

-- Workflow state report.
SELECT
    job_name,
    status,
    started_at,
    completed_at,
    failure_reason
FROM sorting_jobs
ORDER BY created_at;

-- Explain the main indexed input query.
EXPLAIN
SELECT position_no, value
FROM input_values
WHERE job_id = (
    SELECT job_id
    FROM sorting_jobs
    WHERE job_name = 'random_median_hoare'
)
ORDER BY value;

-- The following query highlights the central worst-case relationship:
-- an input can produce far more comparisons when the pivot repeatedly
-- creates partitions of sizes 0 and n-1.
SELECT
    j.job_name,
    j.pivot_policy,
    j.partition_policy,
    r.input_size,
    r.comparisons,
    ROUND(
        r.comparisons::NUMERIC /
        NULLIF(r.input_size * r.input_size, 0),
        6
    ) AS normalized_quadratic_work
FROM algorithm_runs AS r
JOIN sorting_jobs AS j
    ON j.job_id = r.job_id
ORDER BY normalized_quadratic_work DESC;
