DROP SCHEMA IF EXISTS elementary_sorting CASCADE;
CREATE SCHEMA elementary_sorting;

SET search_path = elementary_sorting, public;

CREATE TYPE sort_algorithm AS ENUM (
    'bubble',
    'selection',
    'insertion'
);

CREATE TYPE dataset_kind AS ENUM (
    'random',
    'sorted',
    'reverse',
    'duplicates',
    'nearly_sorted',
    'custom'
);

CREATE TYPE run_status AS ENUM (
    'pending',
    'running',
    'completed',
    'failed'
);

CREATE TABLE sorting_dataset (
    dataset_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dataset_name text NOT NULL,
    dataset_kind dataset_kind NOT NULL,
    values_json jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT dataset_name_nonempty
        CHECK (length(trim(dataset_name)) > 0),
    CONSTRAINT dataset_values_array
        CHECK (jsonb_typeof(values_json) = 'array')
);

CREATE TABLE sorting_run (
    run_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dataset_id bigint NOT NULL
        REFERENCES sorting_dataset(dataset_id)
        ON DELETE CASCADE,
    algorithm sort_algorithm NOT NULL,
    status run_status NOT NULL DEFAULT 'pending',
    output_json jsonb,
    comparisons bigint NOT NULL DEFAULT 0,
    swaps bigint NOT NULL DEFAULT 0,
    writes bigint NOT NULL DEFAULT 0,
    elapsed_microseconds bigint,
    failure_reason text,
    started_at timestamptz,
    completed_at timestamptz,
    CONSTRAINT nonnegative_operations
        CHECK (
            comparisons >= 0
            AND swaps >= 0
            AND writes >= 0
        ),
    CONSTRAINT successful_run_has_output
        CHECK (
            status <> 'completed'
            OR output_json IS NOT NULL
        ),
    CONSTRAINT completed_run_has_time
        CHECK (
            status <> 'completed'
            OR elapsed_microseconds IS NOT NULL
        ),
    CONSTRAINT failed_run_has_reason
        CHECK (
            status <> 'failed'
            OR length(trim(coalesce(failure_reason, ''))) > 0
        )
);

CREATE TABLE sorting_observation (
    observation_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    run_id bigint NOT NULL
        REFERENCES sorting_run(run_id)
        ON DELETE CASCADE,
    observation_type text NOT NULL,
    observation_value bigint NOT NULL,
    observed_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT observation_type_valid
        CHECK (
            observation_type IN (
                'comparisons',
                'swaps',
                'writes'
            )
        ),
    CONSTRAINT observation_value_nonnegative
        CHECK (observation_value >= 0)
);

CREATE INDEX idx_sorting_run_dataset_algorithm
    ON sorting_run(dataset_id, algorithm);

CREATE INDEX idx_sorting_run_status
    ON sorting_run(status);

CREATE INDEX idx_sorting_observation_run_type
    ON sorting_observation(run_id, observation_type);

CREATE OR REPLACE FUNCTION validate_numeric_array(input jsonb)
RETURNS boolean
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    item jsonb;
BEGIN
    IF jsonb_typeof(input) <> 'array' THEN
        RETURN false;
    END IF;

    FOR item IN
        SELECT value
        FROM jsonb_array_elements(input)
    LOOP
        IF jsonb_typeof(item) <> 'number' THEN
            RETURN false;
        END IF;
    END LOOP;

    RETURN true;
END;
$$;

ALTER TABLE sorting_dataset
ADD CONSTRAINT dataset_values_numeric
CHECK (validate_numeric_array(values_json));

CREATE OR REPLACE FUNCTION validate_run_transition()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF OLD.status = 'completed'
       AND NEW.status <> 'completed' THEN
        RAISE EXCEPTION
            'A completed sorting run cannot transition to %',
            NEW.status;
    END IF;

    IF OLD.status = 'failed'
       AND NEW.status = 'running' THEN
        RAISE EXCEPTION
            'A failed sorting run cannot directly restart as running';
    END IF;

    IF NEW.status = 'running'
       AND NEW.started_at IS NULL THEN
        NEW.started_at := now();
    END IF;

    IF NEW.status IN ('completed', 'failed')
       AND NEW.completed_at IS NULL THEN
        NEW.completed_at := now();
    END IF;

    IF NEW.status = 'completed'
       AND NEW.completed_at < coalesce(NEW.started_at, NEW.completed_at) THEN
        RAISE EXCEPTION
            'Completion time cannot precede start time';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_run_transition
BEFORE UPDATE ON sorting_run
FOR EACH ROW
EXECUTE FUNCTION validate_run_transition();

CREATE OR REPLACE FUNCTION array_is_sorted(input jsonb)
RETURNS boolean
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    previous_value numeric;
    current_value numeric;
    first_value boolean := true;
BEGIN
    IF jsonb_typeof(input) <> 'array' THEN
        RETURN false;
    END IF;

    FOR current_value IN
        SELECT value::numeric
        FROM jsonb_array_elements_text(input) AS values(value)
    LOOP
        IF first_value THEN
            previous_value := current_value;
            first_value := false;
        ELSIF previous_value > current_value THEN
            RETURN false;
        ELSE
            previous_value := current_value;
        END IF;
    END LOOP;

    RETURN true;
END;
$$;

CREATE OR REPLACE FUNCTION validate_completed_sort()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    input_values jsonb;
BEGIN
    IF NEW.status = 'completed' THEN
        SELECT values_json
        INTO input_values
        FROM sorting_dataset
        WHERE dataset_id = NEW.dataset_id;

        IF NEW.output_json IS NULL
           OR NOT array_is_sorted(NEW.output_json) THEN
            RAISE EXCEPTION
                'Completed sorting run must contain sorted output';
        END IF;

        IF jsonb_array_length(input_values)
           <> jsonb_array_length(NEW.output_json) THEN
            RAISE EXCEPTION
                'Sorted output must preserve the number of elements';
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_completed_sort
BEFORE INSERT OR UPDATE ON sorting_run
FOR EACH ROW
EXECUTE FUNCTION validate_completed_sort();

INSERT INTO sorting_dataset (
    dataset_name,
    dataset_kind,
    values_json
)
VALUES
(
    'small_random',
    'random',
    '[5, 2, 4, 1, 3]'::jsonb
),
(
    'already_sorted',
    'sorted',
    '[1, 2, 3, 4, 5]'::jsonb
),
(
    'reverse_order',
    'reverse',
    '[5, 4, 3, 2, 1]'::jsonb
),
(
    'duplicate_heavy',
    'duplicates',
    '[3, 1, 3, 2, 1, 2, 3]'::jsonb
),
(
    'nearly_sorted',
    'nearly_sorted',
    '[1, 2, 4, 3, 5, 6]'::jsonb
),
(
    'negative_values',
    'custom',
    '[-4, 7, 0, -1, 5]'::jsonb
);

INSERT INTO sorting_run (
    dataset_id,
    algorithm,
    status,
    output_json,
    comparisons,
    swaps,
    writes,
    elapsed_microseconds,
    started_at,
    completed_at
)
SELECT
    dataset_id,
    algorithm,
    'completed',
    CASE algorithm
        WHEN 'bubble' THEN
            CASE dataset_name
                WHEN 'small_random' THEN '[1,2,3,4,5]'::jsonb
                WHEN 'already_sorted' THEN '[1,2,3,4,5]'::jsonb
                WHEN 'reverse_order' THEN '[1,2,3,4,5]'::jsonb
                WHEN 'duplicate_heavy' THEN '[1,1,2,2,3,3,3]'::jsonb
                WHEN 'nearly_sorted' THEN '[1,2,3,4,5,6]'::jsonb
                WHEN 'negative_values' THEN '[-4,-1,0,5,7]'::jsonb
            END
        WHEN 'selection' THEN
            CASE dataset_name
                WHEN 'small_random' THEN '[1,2,3,4,5]'::jsonb
                WHEN 'already_sorted' THEN '[1,2,3,4,5]'::jsonb
                WHEN 'reverse_order' THEN '[1,2,3,4,5]'::jsonb
                WHEN 'duplicate_heavy' THEN '[1,1,2,2,3,3,3]'::jsonb
                WHEN 'nearly_sorted' THEN '[1,2,3,4,5,6]'::jsonb
                WHEN 'negative_values' THEN '[-4,-1,0,5,7]'::jsonb
            END
        WHEN 'insertion' THEN
            CASE dataset_name
                WHEN 'small_random' THEN '[1,2,3,4,5]'::jsonb
                WHEN 'already_sorted' THEN '[1,2,3,4,5]'::jsonb
                WHEN 'reverse_order' THEN '[1,2,3,4,5]'::jsonb
                WHEN 'duplicate_heavy' THEN '[1,1,2,2,3,3,3]'::jsonb
                WHEN 'nearly_sorted' THEN '[1,2,3,4,5,6]'::jsonb
                WHEN 'negative_values' THEN '[-4,-1,0,5,7]'::jsonb
            END
    END,
    CASE algorithm
        WHEN 'bubble' THEN 10
        WHEN 'selection' THEN 10
        WHEN 'insertion' THEN 8
    END,
    CASE algorithm
        WHEN 'bubble' THEN 4
        WHEN 'selection' THEN 3
        WHEN 'insertion' THEN 0
    END,
    CASE algorithm
        WHEN 'bubble' THEN 18
        WHEN 'selection' THEN 6
        WHEN 'insertion' THEN 14
    END,
    CASE algorithm
        WHEN 'bubble' THEN 25
        WHEN 'selection' THEN 20
        WHEN 'insertion' THEN 18
    END,
    now(),
    now() + interval '25 microseconds'
FROM sorting_dataset
CROSS JOIN (
    VALUES
        ('bubble'::sort_algorithm),
        ('selection'::sort_algorithm),
        ('insertion'::sort_algorithm)
) AS algorithms(algorithm);

-- A failed run records the operational failure without presenting it as
-- a successful sorting result.
INSERT INTO sorting_run (
    dataset_id,
    algorithm,
    status,
    failure_reason,
    started_at,
    completed_at
)
SELECT
    dataset_id,
    'insertion',
    'failed',
    'Input validation rejected a non-numeric element.',
    now(),
    now()
FROM sorting_dataset
WHERE dataset_name = 'small_random'
LIMIT 1;

INSERT INTO sorting_observation (
    run_id,
    observation_type,
    observation_value
)
SELECT
    run_id,
    'comparisons',
    comparisons
FROM sorting_run
WHERE status = 'completed';

INSERT INTO sorting_observation (
    run_id,
    observation_type,
    observation_value
)
SELECT
    run_id,
    'swaps',
    swaps
FROM sorting_run
WHERE status = 'completed';

INSERT INTO sorting_observation (
    run_id,
    observation_type,
    observation_value
)
SELECT
    run_id,
    'writes',
    writes
FROM sorting_run
WHERE status = 'completed';

CREATE OR REPLACE VIEW completed_run_report AS
SELECT
    r.run_id,
    d.dataset_name,
    d.dataset_kind,
    r.algorithm,
    r.comparisons,
    r.swaps,
    r.writes,
    r.elapsed_microseconds,
    r.output_json
FROM sorting_run AS r
JOIN sorting_dataset AS d
    ON d.dataset_id = r.dataset_id
WHERE r.status = 'completed';

CREATE OR REPLACE VIEW algorithm_performance AS
SELECT
    algorithm,
    count(*) AS completed_runs,
    avg(comparisons)::numeric(12,2) AS avg_comparisons,
    avg(swaps)::numeric(12,2) AS avg_swaps,
    avg(writes)::numeric(12,2) AS avg_writes,
    avg(elapsed_microseconds)::numeric(12,2) AS avg_microseconds
FROM completed_run_report
GROUP BY algorithm;

-- Retrieve the completed output of every algorithm.
SELECT
    dataset_name,
    algorithm,
    output_json
FROM completed_run_report
ORDER BY dataset_name, algorithm;

-- Compare operation counts by algorithm.
SELECT
    algorithm,
    completed_runs,
    avg_comparisons,
    avg_swaps,
    avg_writes,
    avg_microseconds
FROM algorithm_performance
ORDER BY avg_comparisons;

-- Identify datasets where Bubble Sort performed fewer comparisons
-- than the other elementary algorithms.
WITH comparison_rank AS (
    SELECT
        dataset_name,
        algorithm,
        comparisons,
        rank() OVER (
            PARTITION BY dataset_name
            ORDER BY comparisons
        ) AS comparison_rank
    FROM completed_run_report
)
SELECT
    dataset_name,
    algorithm,
    comparisons
FROM comparison_rank
WHERE comparison_rank = 1
ORDER BY dataset_name;

-- Validate that every completed output is sorted.
SELECT
    run_id,
    dataset_name,
    algorithm,
    array_is_sorted(output_json) AS output_is_sorted,
    jsonb_array_length(output_json) AS output_length
FROM completed_run_report
ORDER BY run_id;

-- Demonstrate transactional integrity. The transaction is rolled back,
-- so the database is unchanged after the validation example.
BEGIN;

UPDATE sorting_run
SET status = 'running',
    started_at = now()
WHERE run_id = (
    SELECT min(run_id)
    FROM sorting_run
    WHERE status = 'completed'
);

UPDATE sorting_run
SET status = 'completed',
    completed_at = now(),
    elapsed_microseconds = 30
WHERE run_id = (
    SELECT min(run_id)
    FROM sorting_run
    WHERE status = 'running'
);

ROLLBACK;

-- Operational state report.
SELECT
    status,
    count(*) AS run_count
FROM sorting_run
GROUP BY status
ORDER BY status;
