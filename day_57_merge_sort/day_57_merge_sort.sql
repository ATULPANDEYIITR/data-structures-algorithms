DROP SCHEMA IF EXISTS merge_sort_lab CASCADE;
CREATE SCHEMA merge_sort_lab;

SET search_path TO merge_sort_lab, public;

-- Merge sort is represented as a relational learning workflow:
-- input datasets contain values, sort runs capture executions, and
-- sorted_items preserve the original position so stability can be verified.

CREATE TABLE datasets (
    dataset_id BIGSERIAL PRIMARY KEY,
    dataset_name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE dataset_items (
    item_id BIGSERIAL PRIMARY KEY,
    dataset_id BIGINT NOT NULL REFERENCES datasets(dataset_id) ON DELETE CASCADE,
    original_position INTEGER NOT NULL,
    value INTEGER NOT NULL,
    group_key TEXT NOT NULL DEFAULT 'default',
    CONSTRAINT dataset_items_position_positive
        CHECK (original_position >= 0),
    CONSTRAINT dataset_items_group_not_blank
        CHECK (length(btrim(group_key)) > 0),
    UNIQUE (dataset_id, original_position)
);

CREATE INDEX idx_dataset_items_dataset_value
    ON dataset_items(dataset_id, value);

CREATE TABLE sort_runs (
    run_id BIGSERIAL PRIMARY KEY,
    dataset_id BIGINT NOT NULL REFERENCES datasets(dataset_id),
    algorithm TEXT NOT NULL DEFAULT 'merge_sort',
    sort_direction TEXT NOT NULL DEFAULT 'ASC',
    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'RUNNING',
    comparisons BIGINT NOT NULL DEFAULT 0,
    merge_operations BIGINT NOT NULL DEFAULT 0,
    CONSTRAINT sort_runs_algorithm_check
        CHECK (algorithm = 'merge_sort'),
    CONSTRAINT sort_runs_direction_check
        CHECK (sort_direction IN ('ASC', 'DESC')),
    CONSTRAINT sort_runs_status_check
        CHECK (status IN ('RUNNING', 'COMPLETED', 'FAILED')),
    CONSTRAINT sort_runs_comparisons_check
        CHECK (comparisons >= 0),
    CONSTRAINT sort_runs_merges_check
        CHECK (merge_operations >= 0),
    CONSTRAINT sort_runs_completion_check
        CHECK (
            (status = 'RUNNING' AND completed_at IS NULL)
            OR
            (status IN ('COMPLETED', 'FAILED') AND completed_at IS NOT NULL)
        )
);

CREATE TABLE sorted_items (
    run_id BIGINT NOT NULL REFERENCES sort_runs(run_id) ON DELETE CASCADE,
    sorted_position INTEGER NOT NULL,
    item_id BIGINT NOT NULL REFERENCES dataset_items(item_id),
    value INTEGER NOT NULL,
    PRIMARY KEY (run_id, sorted_position),
    UNIQUE (run_id, item_id),
    CONSTRAINT sorted_items_position_positive
        CHECK (sorted_position >= 0)
);

CREATE TABLE merge_operations (
    merge_id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL REFERENCES sort_runs(run_id) ON DELETE CASCADE,
    left_start INTEGER NOT NULL,
    middle_index INTEGER NOT NULL,
    right_end INTEGER NOT NULL,
    CONSTRAINT merge_range_valid
        CHECK (
            left_start >= 0
            AND middle_index >= left_start
            AND right_end > middle_index
        )
);

-- A completed run must have a completion timestamp.
CREATE OR REPLACE FUNCTION validate_sort_run_transition()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.status IN ('COMPLETED', 'FAILED')
       AND NEW.completed_at IS NULL THEN
        RAISE EXCEPTION
            'Completed or failed sort runs require completed_at';
    END IF;

    IF NEW.status = 'RUNNING'
       AND NEW.completed_at IS NOT NULL THEN
        RAISE EXCEPTION
            'Running sort runs cannot have completed_at';
    END IF;

    IF NEW.completed_at IS NOT NULL
       AND NEW.completed_at < NEW.started_at THEN
        RAISE EXCEPTION
            'completed_at cannot precede started_at';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_sort_run_transition
BEFORE INSERT OR UPDATE ON sort_runs
FOR EACH ROW
EXECUTE FUNCTION validate_sort_run_transition();

CREATE OR REPLACE FUNCTION validate_sorted_item()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    expected_dataset BIGINT;
BEGIN
    SELECT dataset_id
    INTO expected_dataset
    FROM sort_runs
    WHERE run_id = NEW.run_id;

    IF expected_dataset IS NULL THEN
        RAISE EXCEPTION 'Sort run % does not exist', NEW.run_id;
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM dataset_items di
        WHERE di.item_id = NEW.item_id
          AND di.dataset_id = expected_dataset
          AND di.value = NEW.value
    ) THEN
        RAISE EXCEPTION
            'Sorted item % does not belong to the dataset or has an invalid value',
            NEW.item_id;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_sorted_item
BEFORE INSERT OR UPDATE ON sorted_items
FOR EACH ROW
EXECUTE FUNCTION validate_sorted_item();

INSERT INTO datasets (dataset_name, description)
VALUES
    (
        'integer_mixed',
        'Mixed positive, negative, duplicate, and zero values'
    ),
    (
        'stable_priority',
        'Equal keys used to demonstrate stable ordering'
    ),
    (
        'already_sorted',
        'Ascending input used to demonstrate an already ordered dataset'
    );

INSERT INTO dataset_items (
    dataset_id,
    original_position,
    value,
    group_key
)
SELECT
    d.dataset_id,
    x.position,
    x.value,
    x.group_key
FROM datasets d
JOIN (
    VALUES
        ('integer_mixed', 0, 42, 'A'),
        ('integer_mixed', 1, -7, 'B'),
        ('integer_mixed', 2, 19, 'C'),
        ('integer_mixed', 3, 0, 'D'),
        ('integer_mixed', 4, 42, 'E'),
        ('integer_mixed', 5, 5, 'F'),
        ('integer_mixed', 6, -100, 'G'),
        ('integer_mixed', 7, 8, 'H'),
        ('stable_priority', 0, 2, 'first'),
        ('stable_priority', 1, 1, 'second'),
        ('stable_priority', 2, 2, 'third'),
        ('stable_priority', 3, 1, 'fourth'),
        ('stable_priority', 4, 2, 'fifth'),
        ('already_sorted', 0, 1, 'one'),
        ('already_sorted', 1, 2, 'two'),
        ('already_sorted', 2, 3, 'three'),
        ('already_sorted', 3, 4, 'four'),
        ('already_sorted', 4, 5, 'five')
) AS x(dataset_name, position, value, group_key)
    ON x.dataset_name = d.dataset_name;

-- A completed ascending run for the mixed dataset.
INSERT INTO sort_runs (
    dataset_id,
    sort_direction,
    status,
    completed_at,
    comparisons,
    merge_operations
)
SELECT
    dataset_id,
    'ASC',
    'COMPLETED',
    CURRENT_TIMESTAMP,
    18,
    8
FROM datasets
WHERE dataset_name = 'integer_mixed';

INSERT INTO sorted_items (run_id, sorted_position, item_id, value)
SELECT
    r.run_id,
    ROW_NUMBER() OVER (
        ORDER BY di.value, di.original_position
    ) - 1,
    di.item_id,
    di.value
FROM sort_runs r
JOIN datasets d
    ON d.dataset_id = r.dataset_id
JOIN dataset_items di
    ON di.dataset_id = d.dataset_id
WHERE d.dataset_name = 'integer_mixed'
  AND r.status = 'COMPLETED';

-- A completed run for the stable-key dataset.
INSERT INTO sort_runs (
    dataset_id,
    sort_direction,
    status,
    completed_at,
    comparisons,
    merge_operations
)
SELECT
    dataset_id,
    'ASC',
    'COMPLETED',
    CURRENT_TIMESTAMP,
    7,
    3
FROM datasets
WHERE dataset_name = 'stable_priority';

INSERT INTO sorted_items (run_id, sorted_position, item_id, value)
SELECT
    r.run_id,
    ROW_NUMBER() OVER (
        ORDER BY di.value, di.original_position
    ) - 1,
    di.item_id,
    di.value
FROM sort_runs r
JOIN datasets d
    ON d.dataset_id = r.dataset_id
JOIN dataset_items di
    ON di.dataset_id = d.dataset_id
WHERE d.dataset_name = 'stable_priority'
  AND r.status = 'COMPLETED';

-- Example merge-range records.
INSERT INTO merge_operations (
    run_id,
    left_start,
    middle_index,
    right_end
)
SELECT run_id, 0, 0, 1
FROM sort_runs
WHERE dataset_id = (
    SELECT dataset_id
    FROM datasets
    WHERE dataset_name = 'stable_priority'
);

INSERT INTO merge_operations (
    run_id,
    left_start,
    middle_index,
    right_end
)
SELECT run_id, 0, 1, 2
FROM sort_runs
WHERE dataset_id = (
    SELECT dataset_id
    FROM datasets
    WHERE dataset_name = 'stable_priority'
);

-- A report view exposes the final order without exposing internal workflow
-- details to every consumer.
CREATE VIEW v_sort_results AS
SELECT
    r.run_id,
    d.dataset_name,
    r.sort_direction,
    si.sorted_position,
    si.value,
    di.original_position,
    di.group_key,
    r.comparisons,
    r.merge_operations,
    r.status
FROM sorted_items si
JOIN sort_runs r
    ON r.run_id = si.run_id
JOIN datasets d
    ON d.dataset_id = r.dataset_id
JOIN dataset_items di
    ON di.item_id = si.item_id;

-- Retrieve a complete sorted result.
SELECT
    dataset_name,
    sorted_position,
    value,
    original_position,
    group_key
FROM v_sort_results
WHERE dataset_name = 'integer_mixed'
ORDER BY sorted_position;

-- Verify ascending order with a window function.
WITH ordered AS (
    SELECT
        dataset_name,
        sorted_position,
        value,
        LAG(value) OVER (
            PARTITION BY run_id
            ORDER BY sorted_position
        ) AS previous_value
    FROM v_sort_results
    WHERE dataset_name = 'integer_mixed'
)
SELECT
    dataset_name,
    COUNT(*) FILTER (
        WHERE previous_value IS NOT NULL
          AND value < previous_value
    ) AS ordering_violations
FROM ordered
GROUP BY dataset_name;

-- Stability validation:
-- for equal values, original_position must remain ascending.
WITH equal_key_pairs AS (
    SELECT
        a.run_id,
        a.value,
        a.sorted_position AS first_sorted_position,
        b.sorted_position AS second_sorted_position,
        a.original_position AS first_original_position,
        b.original_position AS second_original_position
    FROM v_sort_results a
    JOIN v_sort_results b
      ON a.run_id = b.run_id
     AND a.value = b.value
     AND a.sorted_position < b.sorted_position
)
SELECT
    run_id,
    COUNT(*) FILTER (
        WHERE first_original_position > second_original_position
    ) AS stability_violations
FROM equal_key_pairs
GROUP BY run_id;

-- Aggregate run statistics.
SELECT
    d.dataset_name,
    COUNT(di.item_id) AS item_count,
    r.comparisons,
    r.merge_operations,
    r.status
FROM datasets d
JOIN dataset_items di
    ON di.dataset_id = d.dataset_id
LEFT JOIN sort_runs r
    ON r.dataset_id = d.dataset_id
GROUP BY
    d.dataset_name,
    r.run_id,
    r.comparisons,
    r.merge_operations,
    r.status
ORDER BY d.dataset_name;

-- CTE identifying datasets that are already sorted.
WITH ordered AS (
    SELECT
        dataset_id,
        original_position,
        value,
        LAG(value) OVER (
            PARTITION BY dataset_id
            ORDER BY original_position
        ) AS previous_value
    FROM dataset_items
)
SELECT
    d.dataset_name,
    BOOL_AND(
        previous_value IS NULL
        OR value >= previous_value
    ) AS already_sorted
FROM ordered o
JOIN datasets d
    ON d.dataset_id = o.dataset_id
GROUP BY d.dataset_name
ORDER BY d.dataset_name;

-- Transactional example: create and complete a run atomically.
BEGIN;

INSERT INTO sort_runs (
    dataset_id,
    sort_direction,
    status
)
SELECT
    dataset_id,
    'DESC',
    'RUNNING'
FROM datasets
WHERE dataset_name = 'already_sorted'
RETURNING run_id;

-- The application would use the returned run_id to populate sorted_items
-- and merge_operations before committing. This transaction is rolled back
-- here because the sample run intentionally demonstrates an incomplete
-- workflow without leaving an inconsistent completed record.
ROLLBACK;

-- Failure-state example: a failed run has an explicit completion timestamp.
INSERT INTO sort_runs (
    dataset_id,
    sort_direction,
    status,
    completed_at,
    comparisons,
    merge_operations
)
SELECT
    dataset_id,
    'ASC',
    'FAILED',
    CURRENT_TIMESTAMP,
    0,
    0
FROM datasets
WHERE dataset_name = 'already_sorted';

SELECT
    run_id,
    dataset_id,
    status,
    started_at,
    completed_at
FROM sort_runs
WHERE status = 'FAILED';
