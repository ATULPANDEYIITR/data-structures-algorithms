-- Sorting fundamentals in PostgreSQL.
-- PostgreSQL's ORDER BY does not guarantee stability among equal sort keys.
-- A unique secondary key makes the requested order deterministic.

BEGIN;

CREATE SCHEMA IF NOT EXISTS sorting_lab;
SET LOCAL search_path = sorting_lab, public;

DROP VIEW IF EXISTS employee_sort_report;
DROP VIEW IF EXISTS algorithm_complexity;
DROP TABLE IF EXISTS sort_runs CASCADE;
DROP TABLE IF EXISTS sort_items CASCADE;
DROP TABLE IF EXISTS sorting_algorithms CASCADE;

CREATE TABLE sorting_algorithms (
    algorithm_id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    algorithm_name text NOT NULL UNIQUE,
    comparison_based boolean NOT NULL,
    stable_by_design boolean NOT NULL,
    in_place_by_design boolean NOT NULL,
    best_case text NOT NULL,
    average_case text NOT NULL,
    worst_case text NOT NULL,
    auxiliary_space text NOT NULL,
    notes text NOT NULL,
    CHECK (algorithm_name <> '')
);

INSERT INTO sorting_algorithms (
    algorithm_name, comparison_based, stable_by_design,
    in_place_by_design, best_case, average_case, worst_case,
    auxiliary_space, notes
) VALUES
(
    'Insertion sort', TRUE, TRUE, TRUE,
    'O(n)', 'O(n^2)', 'O(n^2)', 'O(1)',
    'Adaptive for nearly sorted input; shifts only strictly greater elements.'
),
(
    'Merge sort', TRUE, TRUE, FALSE,
    'O(n log n)', 'O(n log n)', 'O(n log n)', 'O(n)',
    'Predictable comparison complexity; merging requires auxiliary storage.'
),
(
    'Quicksort', TRUE, FALSE, TRUE,
    'O(n log n)', 'O(n log n)', 'O(n^2)', 'O(log n) average stack',
    'Partitioning is typically fast; pivot choices affect worst-case behavior.'
),
(
    'Heap sort', TRUE, FALSE, TRUE,
    'O(n log n)', 'O(n log n)', 'O(n log n)', 'O(1)',
    'Bounded worst-case time and constant auxiliary storage.'
),
(
    'Counting sort', FALSE, TRUE, FALSE,
    'O(n + k)', 'O(n + k)', 'O(n + k)', 'O(n + k)',
    'Applicable to bounded integer keys; k is the key range.'
);

CREATE TABLE sort_items (
    item_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    batch_name text NOT NULL,
    item_name text NOT NULL,
    sort_key integer NOT NULL,
    original_position integer NOT NULL CHECK (original_position > 0),
    payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (batch_name, original_position),
    CHECK (batch_name <> ''),
    CHECK (item_name <> '')
);

CREATE INDEX sort_items_batch_key_position_idx
    ON sort_items (batch_name, sort_key, original_position);

CREATE TABLE sort_runs (
    run_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    batch_name text NOT NULL,
    algorithm_id integer NOT NULL
        REFERENCES sorting_algorithms(algorithm_id),
    input_count integer NOT NULL CHECK (input_count >= 0),
    elapsed_microseconds bigint CHECK (elapsed_microseconds >= 0),
    result_verified boolean NOT NULL,
    input_was_modified boolean NOT NULL DEFAULT FALSE,
    executed_at timestamptz NOT NULL DEFAULT now(),
    CHECK (batch_name <> '')
);

CREATE INDEX sort_runs_batch_time_idx
    ON sort_runs (batch_name, executed_at DESC);

INSERT INTO sort_items
    (batch_name, item_name, sort_key, original_position, payload)
VALUES
    ('students', 'Asha', 90, 1, '{"department":"Computing"}'),
    ('students', 'Ravi', 75, 2, '{"department":"Security"}'),
    ('students', 'Meera', 90, 3, '{"department":"Computing"}'),
    ('students', 'Kabir', 75, 4, '{"department":"Security"}'),
    ('students', 'Isha', 90, 5, '{"department":"Research"}'),
    ('integers', 'value-1', 5, 1, '{"source":"sample"}'),
    ('integers', 'value-2', -2, 2, '{"source":"sample"}'),
    ('integers', 'value-3', 0, 3, '{"source":"sample"}'),
    ('integers', 'value-4', 5, 4, '{"source":"sample"}'),
    ('integers', 'value-5', -2, 5, '{"source":"sample"}');

INSERT INTO sort_runs (
    batch_name, algorithm_id, input_count,
    elapsed_microseconds, result_verified, input_was_modified
)
SELECT
    'students',
    algorithm_id,
    5,
    NULL,
    TRUE,
    FALSE
FROM sorting_algorithms
WHERE algorithm_name IN ('Insertion sort', 'Merge sort', 'Quicksort');

CREATE VIEW employee_sort_report AS
SELECT
    item_id,
    batch_name,
    item_name,
    sort_key,
    original_position,
    row_number() OVER (
        PARTITION BY batch_name
        ORDER BY sort_key, original_position
    ) AS deterministic_rank,
    rank() OVER (
        PARTITION BY batch_name
        ORDER BY sort_key
    ) AS score_rank,
    dense_rank() OVER (
        PARTITION BY batch_name
        ORDER BY sort_key
    ) AS score_dense_rank
FROM sort_items;

CREATE VIEW algorithm_complexity AS
SELECT
    algorithm_name,
    comparison_based,
    stable_by_design,
    in_place_by_design,
    best_case,
    average_case,
    worst_case,
    auxiliary_space,
    notes
FROM sorting_algorithms;

-- Validate that the deterministic ordering is nondecreasing.
CREATE OR REPLACE FUNCTION validate_batch_sorted(p_batch_name text)
RETURNS boolean
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    is_valid boolean;
BEGIN
    IF p_batch_name IS NULL OR btrim(p_batch_name) = '' THEN
        RAISE EXCEPTION 'Batch name must not be empty';
    END IF;

    SELECT NOT EXISTS (
        SELECT 1
        FROM (
            SELECT
                sort_key,
                lag(sort_key) OVER (
                    ORDER BY sort_key, original_position
                ) AS previous_key
            FROM sort_items
            WHERE batch_name = p_batch_name
        ) ordered_values
        WHERE previous_key > sort_key
    )
    INTO is_valid;

    RETURN COALESCE(is_valid, TRUE);
END;
$$;

-- Return rows in deterministic order. The secondary key preserves input
-- order among equal keys, which is a stable ordering policy at query level.
CREATE OR REPLACE FUNCTION sorted_batch(p_batch_name text)
RETURNS TABLE (
    item_id bigint,
    item_name text,
    sort_key integer,
    original_position integer,
    deterministic_rank bigint
)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    IF p_batch_name IS NULL OR btrim(p_batch_name) = '' THEN
        RAISE EXCEPTION 'Batch name must not be empty';
    END IF;

    RETURN QUERY
    SELECT
        s.item_id,
        s.item_name,
        s.sort_key,
        s.original_position,
        row_number() OVER (
            ORDER BY s.sort_key, s.original_position
        )
    FROM sort_items AS s
    WHERE s.batch_name = p_batch_name
    ORDER BY s.sort_key, s.original_position;
END;
$$;

-- Example: deterministic ordering and tie handling.
SELECT *
FROM sorted_batch('students');

-- Comparison ranks group equal keys, unlike deterministic row_number().
SELECT
    item_name,
    sort_key,
    original_position,
    deterministic_rank,
    score_rank,
    score_dense_rank
FROM employee_sort_report
WHERE batch_name = 'students'
ORDER BY deterministic_rank;

-- Compare algorithm properties without conflating stability and in-place use.
SELECT *
FROM algorithm_complexity
ORDER BY algorithm_name;

-- Aggregate recorded verification results.
SELECT
    a.algorithm_name,
    count(*) AS runs,
    count(*) FILTER (WHERE r.result_verified) AS verified_runs,
    avg(r.elapsed_microseconds) AS average_elapsed_microseconds,
    sum(r.input_count) AS total_items_processed
FROM sort_runs AS r
JOIN sorting_algorithms AS a USING (algorithm_id)
GROUP BY a.algorithm_name
ORDER BY a.algorithm_name;

-- A key-range query uses the batch/key/position index.
SELECT item_name, sort_key, original_position
FROM sort_items
WHERE batch_name = 'students'
  AND sort_key BETWEEN 75 AND 90
ORDER BY sort_key, original_position;

-- An empty batch is valid and has no rows.
SELECT *
FROM sorted_batch('batch-that-does-not-exist');

SELECT validate_batch_sorted('students') AS students_order_valid;

COMMIT;
