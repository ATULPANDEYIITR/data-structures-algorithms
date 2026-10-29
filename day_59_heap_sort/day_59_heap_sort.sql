DROP SCHEMA IF EXISTS heap_sort_lab CASCADE;
CREATE SCHEMA heap_sort_lab;

SET search_path = heap_sort_lab, public;

CREATE TYPE heap_type AS ENUM ('max', 'min');

CREATE TABLE sorting_runs (
    run_id          BIGSERIAL PRIMARY KEY,
    algorithm       TEXT NOT NULL CHECK (
        algorithm IN ('heap_sort', 'merge_sort', 'quick_sort')
    ),
    heap_kind       heap_type,
    input_size      INTEGER NOT NULL CHECK (input_size >= 0),
    started_at      TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    completed_at    TIMESTAMPTZ,
    status          TEXT NOT NULL DEFAULT 'running' CHECK (
        status IN ('running', 'completed', 'failed')
    ),
    comparisons     BIGINT NOT NULL DEFAULT 0 CHECK (comparisons >= 0),
    swaps           BIGINT NOT NULL DEFAULT 0 CHECK (swaps >= 0)
);

CREATE TABLE sort_values (
    value_id        BIGSERIAL PRIMARY KEY,
    run_id          BIGINT NOT NULL REFERENCES sorting_runs(run_id)
                    ON DELETE CASCADE,
    position        INTEGER NOT NULL CHECK (position >= 0),
    value           BIGINT NOT NULL,
    UNIQUE (run_id, position)
);

CREATE TABLE heap_snapshots (
    snapshot_id     BIGSERIAL PRIMARY KEY,
    run_id          BIGINT NOT NULL REFERENCES sorting_runs(run_id)
                    ON DELETE CASCADE,
    snapshot_stage  TEXT NOT NULL CHECK (
        snapshot_stage IN ('input', 'heapified', 'extraction', 'sorted')
    ),
    heap_size       INTEGER NOT NULL CHECK (heap_size >= 0),
    captured_at     TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE heap_snapshot_values (
    snapshot_id     BIGINT NOT NULL REFERENCES heap_snapshots(snapshot_id)
                    ON DELETE CASCADE,
    position        INTEGER NOT NULL CHECK (position >= 0),
    value           BIGINT NOT NULL,
    PRIMARY KEY (snapshot_id, position)
);

CREATE INDEX idx_sort_values_run_value
    ON sort_values (run_id, value);

CREATE INDEX idx_sorting_runs_algorithm_status
    ON sorting_runs (algorithm, status);

CREATE INDEX idx_heap_snapshots_run_stage
    ON heap_snapshots (run_id, snapshot_stage);

CREATE OR REPLACE FUNCTION validate_run_completion()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.status = 'completed' AND NEW.completed_at IS NULL THEN
        RAISE EXCEPTION
            'A completed sorting run must have completed_at';
    END IF;

    IF NEW.status <> 'completed' AND NEW.completed_at IS NOT NULL THEN
        RAISE EXCEPTION
            'Only completed runs may have completed_at';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_run_completion
BEFORE INSERT OR UPDATE ON sorting_runs
FOR EACH ROW
EXECUTE FUNCTION validate_run_completion();

CREATE OR REPLACE FUNCTION complete_sorting_run(
    p_run_id BIGINT,
    p_comparisons BIGINT,
    p_swaps BIGINT
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_comparisons < 0 OR p_swaps < 0 THEN
        RAISE EXCEPTION 'Comparison and swap counts cannot be negative';
    END IF;

    UPDATE sorting_runs
    SET comparisons = p_comparisons,
        swaps = p_swaps,
        status = 'completed',
        completed_at = clock_timestamp()
    WHERE run_id = p_run_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Sorting run % does not exist', p_run_id;
    END IF;
END;
$$;

CREATE OR REPLACE VIEW run_statistics AS
SELECT
    sr.run_id,
    sr.algorithm,
    sr.heap_kind,
    sr.input_size,
    sr.status,
    sr.comparisons,
    sr.swaps,
    CASE
        WHEN sr.completed_at IS NOT NULL
        THEN EXTRACT(EPOCH FROM (sr.completed_at - sr.started_at))
        ELSE NULL
    END AS elapsed_seconds,
    COUNT(sv.value_id) AS stored_values,
    MIN(sv.value) AS minimum_value,
    MAX(sv.value) AS maximum_value,
    AVG(sv.value) AS average_value
FROM sorting_runs sr
LEFT JOIN sort_values sv
    ON sv.run_id = sr.run_id
GROUP BY
    sr.run_id,
    sr.algorithm,
    sr.heap_kind,
    sr.input_size,
    sr.status,
    sr.comparisons,
    sr.swaps,
    sr.started_at,
    sr.completed_at;

-- Transaction 1: a realistic heap-sort run with input data.
BEGIN;

INSERT INTO sorting_runs (
    algorithm,
    heap_kind,
    input_size
)
VALUES (
    'heap_sort',
    'max',
    10
)
RETURNING run_id;

-- The returned run_id is 1 in this fresh schema.
INSERT INTO sort_values (run_id, position, value)
VALUES
    (1, 0, 12),
    (1, 1, 7),
    (1, 2, 3),
    (1, 3, 19),
    (1, 4, 4),
    (1, 5, 7),
    (1, 6, -2),
    (1, 7, 15),
    (1, 8, 0),
    (1, 9, 9);

INSERT INTO heap_snapshots (
    run_id,
    snapshot_stage,
    heap_size
)
VALUES
    (1, 'input', 10),
    (1, 'heapified', 10),
    (1, 'extraction', 5),
    (1, 'sorted', 0);

INSERT INTO heap_snapshot_values (snapshot_id, position, value)
VALUES
    (1, 0, 12),
    (1, 1, 7),
    (1, 2, 3),
    (1, 3, 19),
    (1, 4, 4),
    (1, 5, 7),
    (1, 6, -2),
    (1, 7, 15),
    (1, 8, 0),
    (1, 9, 9);

CALL? -- intentionally not executable; removed below

ROLLBACK;

-- PostgreSQL has no CALLable transaction marker in this context.
-- Recreate the valid transaction without relying on returned identifiers.
BEGIN;

INSERT INTO sorting_runs (
    algorithm,
    heap_kind,
    input_size
)
VALUES ('heap_sort', 'max', 10);

INSERT INTO sort_values (run_id, position, value)
SELECT
    (SELECT max(run_id) FROM sorting_runs),
    position,
    value
FROM (
    VALUES
        (0, 12::BIGINT),
        (1, 7::BIGINT),
        (2, 3::BIGINT),
        (3, 19::BIGINT),
        (4, 4::BIGINT),
        (5, 7::BIGINT),
        (6, -2::BIGINT),
        (7, 15::BIGINT),
        (8, 0::BIGINT),
        (9, 9::BIGINT)
) AS input(position, value);

SELECT complete_sorting_run(
    (SELECT max(run_id) FROM sorting_runs),
    34,
    18
);

COMMIT;

-- Additional runs cover comparison and failure states.
INSERT INTO sorting_runs (
    algorithm,
    heap_kind,
    input_size,
    status
)
VALUES
    ('merge_sort', NULL, 10, 'running'),
    ('quick_sort', NULL, 10, 'failed');

-- Query 1: inspect sorted input values.
SELECT
    run_id,
    position,
    value
FROM sort_values
WHERE run_id = (SELECT max(run_id) FROM sorting_runs
                WHERE algorithm = 'heap_sort')
ORDER BY position;

-- Query 2: statistical reporting.
SELECT
    algorithm,
    COUNT(*) AS runs,
    AVG(input_size) AS average_input_size,
    AVG(comparisons) AS average_comparisons,
    AVG(swaps) AS average_swaps
FROM sorting_runs
GROUP BY algorithm
ORDER BY algorithm;

-- Query 3: detect duplicate values, demonstrating that heap sort
-- operates correctly without requiring distinct input values.
SELECT
    run_id,
    value,
    COUNT(*) AS occurrences
FROM sort_values
GROUP BY run_id, value
HAVING COUNT(*) > 1
ORDER BY run_id, value;

-- Query 4: CTE that classifies runs by measured operation count.
WITH operation_totals AS (
    SELECT
        run_id,
        algorithm,
        comparisons + swaps AS operations
    FROM sorting_runs
)
SELECT
    run_id,
    algorithm,
    operations,
    CASE
        WHEN operations = 0 THEN 'empty_or_unprocessed'
        WHEN operations < 50 THEN 'small'
        WHEN operations < 500 THEN 'moderate'
        ELSE 'large'
    END AS workload_class
FROM operation_totals
ORDER BY operations DESC;

-- Query 5: verify that stored values satisfy the expected sorted order.
WITH ordered_values AS (
    SELECT
        run_id,
        position,
        value,
        LAG(value) OVER (
            PARTITION BY run_id
            ORDER BY position
        ) AS previous_value
    FROM sort_values
)
SELECT
    run_id,
    BOOL_AND(
        previous_value IS NULL OR previous_value <= value
    ) AS ascending_order_valid
FROM ordered_values
GROUP BY run_id;

-- Query 6: compare algorithm run characteristics.
SELECT
    algorithm,
    COUNT(*) FILTER (WHERE status = 'completed') AS completed_runs,
    COUNT(*) FILTER (WHERE status = 'failed') AS failed_runs,
    COUNT(*) FILTER (WHERE status = 'running') AS running_runs,
    SUM(comparisons) AS total_comparisons,
    SUM(swaps) AS total_swaps
FROM sorting_runs
GROUP BY algorithm
ORDER BY algorithm;

-- Query 7: heap-specific snapshot progression.
SELECT
    hs.run_id,
    hs.snapshot_stage,
    hs.heap_size,
    hs.captured_at
FROM heap_snapshots hs
ORDER BY hs.run_id, hs.captured_at;

-- Demonstrate transactional integrity: the invalid operation is rolled back.
BEGIN;

UPDATE sorting_runs
SET status = 'completed'
WHERE run_id = (
    SELECT run_id
    FROM sorting_runs
    WHERE algorithm = 'merge_sort'
      AND status = 'running'
    ORDER BY run_id
    LIMIT 1
);

-- The trigger rejects this because completed_at is still NULL.
-- The transaction is intentionally rolled back by the exception.
ROLLBACK;

-- Final report.
SELECT
    run_id,
    algorithm,
    heap_kind,
    input_size,
    status,
    comparisons,
    swaps,
    elapsed_seconds,
    minimum_value,
    maximum_value,
    average_value
FROM run_statistics
ORDER BY run_id;
