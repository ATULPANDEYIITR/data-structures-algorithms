-- ============================================================
-- HEAP PROBLEMS: PostgreSQL HEAP-BASED ANALYTICS WORKFLOW
-- PostgreSQL 15+
--
-- Covers:
-- 1. Kth largest and smallest
-- 2. Top-k elements
-- 3. Top-k frequent elements
-- 4. K-way merging of sorted streams
-- 5. Running median
-- 6. Streaming kth-largest calculations
--
-- SQL ORDER BY uses database sorting rather than exposing an
-- in-memory binary heap. These queries model equivalent results.
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS heap_lab;

SET search_path TO heap_lab, public;

-- ------------------------------------------------------------
-- 1. Domain tables
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS datasets (
    dataset_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dataset_name VARCHAR(120) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dataset_values (
    value_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dataset_id BIGINT NOT NULL
        REFERENCES datasets(dataset_id) ON DELETE CASCADE,
    numeric_value BIGINT NOT NULL,
    source_sequence BIGINT NOT NULL,
    inserted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_dataset_sequence
        UNIQUE (dataset_id, source_sequence)
);

CREATE TABLE IF NOT EXISTS processing_jobs (
    job_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dataset_id BIGINT NOT NULL
        REFERENCES datasets(dataset_id),
    job_type VARCHAR(30) NOT NULL CHECK (
        job_type IN (
            'KTH_LARGEST',
            'KTH_SMALLEST',
            'TOP_K',
            'TOP_K_FREQUENT',
            'RUNNING_MEDIAN',
            'STREAM_KTH'
        )
    ),
    parameter_k INTEGER NOT NULL CHECK (parameter_k >= 1),
    job_status VARCHAR(20) NOT NULL DEFAULT 'PENDING'
        CHECK (
            job_status IN (
                'PENDING',
                'RUNNING',
                'COMPLETED',
                'FAILED'
            )
        ),
    result_value NUMERIC,
    result_payload JSONB,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS stream_events (
    event_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dataset_id BIGINT NOT NULL
        REFERENCES datasets(dataset_id) ON DELETE CASCADE,
    source_name VARCHAR(100) NOT NULL,
    source_sequence BIGINT NOT NULL CHECK (source_sequence >= 1),
    numeric_value BIGINT NOT NULL,
    event_time TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_stream_source_sequence
        UNIQUE (dataset_id, source_name, source_sequence)
);

CREATE TABLE IF NOT EXISTS stream_results (
    result_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dataset_id BIGINT NOT NULL
        REFERENCES datasets(dataset_id) ON DELETE CASCADE,
    event_id BIGINT NOT NULL
        REFERENCES stream_events(event_id) ON DELETE CASCADE,
    processed_sequence BIGINT NOT NULL,
    running_median NUMERIC NOT NULL,
    kth_largest BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_processed_event UNIQUE (event_id)
);

-- ------------------------------------------------------------
-- 2. Indexes
-- ------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_values_dataset_value
    ON dataset_values(dataset_id, numeric_value DESC);

CREATE INDEX IF NOT EXISTS idx_values_dataset_sequence
    ON dataset_values(dataset_id, source_sequence);

CREATE INDEX IF NOT EXISTS idx_jobs_status_created
    ON processing_jobs(job_status, created_at);

CREATE INDEX IF NOT EXISTS idx_stream_dataset_time
    ON stream_events(dataset_id, event_time);

CREATE INDEX IF NOT EXISTS idx_stream_source_sequence
    ON stream_events(dataset_id, source_name, source_sequence);

CREATE INDEX IF NOT EXISTS idx_stream_results_dataset_sequence
    ON stream_results(dataset_id, processed_sequence);

-- ------------------------------------------------------------
-- 3. Kth largest and smallest
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION kth_largest(
    p_dataset_id BIGINT,
    p_k INTEGER
)
RETURNS BIGINT
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_result BIGINT;
    v_count BIGINT;
BEGIN
    IF p_k IS NULL OR p_k < 1 THEN
        RAISE EXCEPTION 'k must be positive';
    END IF;

    SELECT COUNT(*)
    INTO v_count
    FROM dataset_values
    WHERE dataset_id = p_dataset_id;

    IF v_count < p_k THEN
        RAISE EXCEPTION
            'Dataset contains % values; requested rank is %',
            v_count, p_k;
    END IF;

    SELECT numeric_value
    INTO STRICT v_result
    FROM dataset_values
    WHERE dataset_id = p_dataset_id
    ORDER BY numeric_value DESC, value_id
    OFFSET p_k - 1
    LIMIT 1;

    RETURN v_result;
END;
$$;

CREATE OR REPLACE FUNCTION kth_smallest(
    p_dataset_id BIGINT,
    p_k INTEGER
)
RETURNS BIGINT
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_result BIGINT;
    v_count BIGINT;
BEGIN
    IF p_k IS NULL OR p_k < 1 THEN
        RAISE EXCEPTION 'k must be positive';
    END IF;

    SELECT COUNT(*)
    INTO v_count
    FROM dataset_values
    WHERE dataset_id = p_dataset_id;

    IF v_count < p_k THEN
        RAISE EXCEPTION 'Insufficient dataset values';
    END IF;

    SELECT numeric_value
    INTO STRICT v_result
    FROM dataset_values
    WHERE dataset_id = p_dataset_id
    ORDER BY numeric_value ASC, value_id
    OFFSET p_k - 1
    LIMIT 1;

    RETURN v_result;
END;
$$;

-- ------------------------------------------------------------
-- 4. Top-k largest
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION top_k_largest(
    p_dataset_id BIGINT,
    p_k INTEGER
)
RETURNS TABLE (
    position BIGINT,
    numeric_value BIGINT
)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    IF p_k IS NULL OR p_k < 0 THEN
        RAISE EXCEPTION 'k cannot be negative';
    END IF;

    RETURN QUERY
    SELECT
        ROW_NUMBER() OVER (
            ORDER BY dv.numeric_value DESC, dv.value_id
        ),
        dv.numeric_value
    FROM dataset_values dv
    WHERE dv.dataset_id = p_dataset_id
    ORDER BY dv.numeric_value DESC, dv.value_id
    LIMIT p_k;
END;
$$;

-- ------------------------------------------------------------
-- 5. Top-k frequent values
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION top_k_frequent(
    p_dataset_id BIGINT,
    p_k INTEGER
)
RETURNS TABLE (
    numeric_value BIGINT,
    occurrence_count BIGINT,
    rank_position BIGINT
)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    IF p_k IS NULL OR p_k < 0 THEN
        RAISE EXCEPTION 'k cannot be negative';
    END IF;

    RETURN QUERY
    SELECT
        grouped.numeric_value,
        grouped.occurrence_count,
        ROW_NUMBER() OVER (
            ORDER BY
                grouped.occurrence_count DESC,
                grouped.numeric_value ASC
        )
    FROM (
        SELECT
            dv.numeric_value,
            COUNT(*) AS occurrence_count
        FROM dataset_values dv
        WHERE dv.dataset_id = p_dataset_id
        GROUP BY dv.numeric_value
    ) grouped
    ORDER BY
        grouped.occurrence_count DESC,
        grouped.numeric_value ASC
    LIMIT p_k;
END;
$$;

-- ------------------------------------------------------------
-- 6. K-way merge of sorted streams
--
-- Each stream is identified by source_name.
-- source_sequence preserves the order within that stream.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION merge_sorted_streams(
    p_dataset_id BIGINT
)
RETURNS TABLE (
    merge_position BIGINT,
    source_name VARCHAR(100),
    numeric_value BIGINT
)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM (
            SELECT
                source_name,
                source_sequence,
                numeric_value,
                LAG(numeric_value) OVER (
                    PARTITION BY source_name
                    ORDER BY source_sequence
                ) AS previous_value
            FROM stream_events
            WHERE dataset_id = p_dataset_id
        ) checked
        WHERE previous_value > numeric_value
    ) THEN
        RAISE EXCEPTION
            'At least one source stream is not sorted';
    END IF;

    RETURN QUERY
    SELECT
        ROW_NUMBER() OVER (
            ORDER BY event_time, source_name, source_sequence
        ),
        source_name,
        numeric_value
    FROM stream_events
    WHERE dataset_id = p_dataset_id
    ORDER BY numeric_value, source_name, source_sequence;
END;
$$;

-- ------------------------------------------------------------
-- 7. Running median
--
-- Two conceptual partitions:
-- lower half: values <= median boundary
-- upper half: values > median boundary
--
-- Window functions compute the exact median at each sequence.
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW running_median_view AS
WITH ordered_values AS (
    SELECT
        dataset_id,
        value_id,
        source_sequence,
        numeric_value,
        ROW_NUMBER() OVER (
            PARTITION BY dataset_id
            ORDER BY source_sequence, value_id
        ) AS running_count
    FROM dataset_values
),
ranked_values AS (
    SELECT
        dataset_id,
        value_id,
        source_sequence,
        numeric_value,
        running_count,
        COUNT(*) OVER (
            PARTITION BY dataset_id
            ORDER BY running_count
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS current_count
    FROM ordered_values
)
SELECT
    r.dataset_id,
    r.source_sequence,
    r.numeric_value,
    r.current_count,
    CASE
        WHEN r.current_count % 2 = 1 THEN
            (
                SELECT numeric_value::NUMERIC
                FROM ranked_values x
                WHERE x.dataset_id = r.dataset_id
                  AND x.running_count = (r.current_count + 1) / 2
            )
        ELSE
            (
                SELECT AVG(x.numeric_value::NUMERIC)
                FROM ranked_values x
                WHERE x.dataset_id = r.dataset_id
                  AND x.running_count IN (
                      r.current_count / 2,
                      r.current_count / 2 + 1
                  )
            )
    END AS running_median
FROM ranked_values r;

-- ------------------------------------------------------------
-- 8. Streaming kth-largest result
--
-- This view computes the kth largest value at every event.
-- Rows before k observations return NULL.
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW stream_kth_largest_view AS
SELECT
    event_id,
    dataset_id,
    source_name,
    source_sequence,
    numeric_value,
    COUNT(*) OVER (
        PARTITION BY dataset_id
        ORDER BY event_time, event_id
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS observation_count,
    (
        SELECT x.numeric_value
        FROM stream_events x
        WHERE x.dataset_id = current_event.dataset_id
          AND (
              x.event_time < current_event.event_time
              OR (
                  x.event_time = current_event.event_time
                  AND x.event_id <= current_event.event_id
              )
          )
        ORDER BY x.numeric_value DESC, x.event_id
        OFFSET (
            SELECT COUNT(*) - 1
            FROM stream_events previous
            WHERE previous.dataset_id = current_event.dataset_id
              AND (
                  previous.event_time < current_event.event_time
                  OR (
                      previous.event_time = current_event.event_time
                      AND previous.event_id <= current_event.event_id
                  )
              )
        )
        LIMIT 1
    ) AS largest_so_far
FROM stream_events current_event;

-- ------------------------------------------------------------
-- 9. Job processing procedure
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE process_heap_job(
    p_job_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_job processing_jobs%ROWTYPE;
    v_result BIGINT;
    v_payload JSONB;
BEGIN
    SELECT *
    INTO v_job
    FROM processing_jobs
    WHERE job_id = p_job_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Job % does not exist', p_job_id;
    END IF;

    IF v_job.job_status <> 'PENDING' THEN
        RAISE EXCEPTION
            'Only pending jobs can be processed';
    END IF;

    UPDATE processing_jobs
    SET job_status = 'RUNNING',
        error_message = NULL
    WHERE job_id = p_job_id;

    CASE v_job.job_type
        WHEN 'KTH_LARGEST' THEN
            v_result := kth_largest(
                v_job.dataset_id,
                v_job.parameter_k
            );

        WHEN 'KTH_SMALLEST' THEN
            v_result := kth_smallest(
                v_job.dataset_id,
                v_job.parameter_k
            );

        WHEN 'TOP_K' THEN
            SELECT jsonb_agg(
                jsonb_build_object(
                    'position', position,
                    'value', numeric_value
                )
                ORDER BY position
            )
            INTO v_payload
            FROM top_k_largest(
                v_job.dataset_id,
                v_job.parameter_k
            );

        WHEN 'TOP_K_FREQUENT' THEN
            SELECT jsonb_agg(
                jsonb_build_object(
                    'value', numeric_value,
                    'frequency', occurrence_count,
                    'rank', rank_position
                )
                ORDER BY rank_position
            )
            INTO v_payload
            FROM top_k_frequent(
                v_job.dataset_id,
                v_job.parameter_k
            );

        WHEN 'RUNNING_MEDIAN' THEN
            SELECT jsonb_agg(
                jsonb_build_object(
                    'sequence', source_sequence,
                    'value', numeric_value,
                    'median', running_median
                )
                ORDER BY source_sequence
            )
            INTO v_payload
            FROM running_median_view
            WHERE dataset_id = v_job.dataset_id;

        WHEN 'STREAM_KTH' THEN
            SELECT jsonb_agg(
                jsonb_build_object(
                    'event_id', event_id,
                    'value', numeric_value,
                    'kth_largest', largest_so_far
                )
                ORDER BY event_time, event_id
            )
            INTO v_payload
            FROM stream_kth_largest_view
            WHERE dataset_id = v_job.dataset_id;

        ELSE
            RAISE EXCEPTION 'Unsupported job type';
    END CASE;

    UPDATE processing_jobs
    SET job_status = 'COMPLETED',
        result_value = v_result,
        result_payload = v_payload,
        completed_at = CURRENT_TIMESTAMP
    WHERE job_id = p_job_id;

EXCEPTION
    WHEN OTHERS THEN
        UPDATE processing_jobs
        SET job_status = 'FAILED',
            error_message = SQLERRM,
            completed_at = CURRENT_TIMESTAMP
        WHERE job_id = p_job_id;

        RAISE;
END;
$$;

-- ------------------------------------------------------------
-- 10. Trigger for stream event validation
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_stream_event()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.source_name IS NULL
       OR BTRIM(NEW.source_name) = '' THEN
        RAISE EXCEPTION 'Source name cannot be empty';
    END IF;

    IF NEW.source_sequence < 1 THEN
        RAISE EXCEPTION 'Sequence must be positive';
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validate_stream_event
ON stream_events;

CREATE TRIGGER trg_validate_stream_event
BEFORE INSERT OR UPDATE ON stream_events
FOR EACH ROW
EXECUTE FUNCTION validate_stream_event();

-- ------------------------------------------------------------
-- 11. Sample datasets
-- ------------------------------------------------------------

INSERT INTO datasets(dataset_name, description)
VALUES
    ('heap_training', 'Heap algorithm demonstration dataset'),
    ('heap_streams', 'Multiple sorted input streams'),
    ('heap_duplicates', 'Frequency and duplicate handling'),
    ('heap_edge_cases', 'Negative and repeated values')
ON CONFLICT (dataset_name) DO NOTHING;

-- Idempotent sample loading.
INSERT INTO dataset_values(
    dataset_id, numeric_value, source_sequence
)
SELECT d.dataset_id, v.numeric_value, v.source_sequence
FROM datasets d
CROSS JOIN (
    VALUES
        (12::BIGINT, 1::BIGINT),
        (3, 2),
        (5, 3),
        (7, 4),
        (19, 5),
        (4, 6),
        (8, 7),
        (15, 8)
) AS v(numeric_value, source_sequence)
WHERE d.dataset_name = 'heap_training'
ON CONFLICT (dataset_id, source_sequence) DO NOTHING;

INSERT INTO dataset_values(
    dataset_id, numeric_value, source_sequence
)
SELECT d.dataset_id, v.numeric_value, v.source_sequence
FROM datasets d
CROSS JOIN (
    VALUES
        (5::BIGINT, 1::BIGINT),
        (5, 2),
        (4, 3),
        (4, 4),
        (4, 5),
        (2, 6),
        (2, 7),
        (1, 8)
) AS v(numeric_value, source_sequence)
WHERE d.dataset_name = 'heap_duplicates'
ON CONFLICT (dataset_id, source_sequence) DO NOTHING;

INSERT INTO dataset_values(
    dataset_id, numeric_value, source_sequence
)
SELECT d.dataset_id, v.numeric_value, v.source_sequence
FROM datasets d
CROSS JOIN (
    VALUES
        (-10::BIGINT, 1::BIGINT),
        (0, 2),
        (-5, 3),
        (0, 4),
        (100, 5),
        (-100, 6)
) AS v(numeric_value, source_sequence)
WHERE d.dataset_name = 'heap_edge_cases'
ON CONFLICT (dataset_id, source_sequence) DO NOTHING;

-- ------------------------------------------------------------
-- 12. Sorted stream sample records
-- ------------------------------------------------------------

INSERT INTO stream_events(
    dataset_id, source_name, source_sequence, numeric_value
)
SELECT
    d.dataset_id,
    v.source_name,
    v.source_sequence,
    v.numeric_value
FROM datasets d
CROSS JOIN (
    VALUES
        ('source_a'::VARCHAR(100), 1::BIGINT, 1::BIGINT),
        ('source_a', 2, 4),
        ('source_a', 3, 7),
        ('source_b', 1, 2),
        ('source_b', 2, 5),
        ('source_b', 3, 8),
        ('source_c', 1, 3),
        ('source_c', 2, 6),
        ('source_c', 3, 9)
) AS v(source_name, source_sequence, numeric_value)
WHERE d.dataset_name = 'heap_streams'
ON CONFLICT (
    dataset_id, source_name, source_sequence
) DO NOTHING;

-- ------------------------------------------------------------
-- 13. Processing job examples
-- ------------------------------------------------------------

INSERT INTO processing_jobs(
    dataset_id, job_type, parameter_k
)
SELECT dataset_id, 'KTH_LARGEST', 3
FROM datasets
WHERE dataset_name = 'heap_training'
AND NOT EXISTS (
    SELECT 1
    FROM processing_jobs j
    WHERE j.dataset_id = datasets.dataset_id
      AND j.job_type = 'KTH_LARGEST'
      AND j.parameter_k = 3
);

INSERT INTO processing_jobs(
    dataset_id, job_type, parameter_k
)
SELECT dataset_id, 'TOP_K', 4
FROM datasets
WHERE dataset_name = 'heap_training'
AND NOT EXISTS (
    SELECT 1
    FROM processing_jobs j
    WHERE j.dataset_id = datasets.dataset_id
      AND j.job_type = 'TOP_K'
      AND j.parameter_k = 4
);

INSERT INTO processing_jobs(
    dataset_id, job_type, parameter_k
)
SELECT dataset_id, 'TOP_K_FREQUENT', 3
FROM datasets
WHERE dataset_name = 'heap_duplicates'
AND NOT EXISTS (
    SELECT 1
    FROM processing_jobs j
    WHERE j.dataset_id = datasets.dataset_id
      AND j.job_type = 'TOP_K_FREQUENT'
);

INSERT INTO processing_jobs(
    dataset_id, job_type, parameter_k
)
SELECT dataset_id, 'STREAM_KTH', 3
FROM datasets
WHERE dataset_name = 'heap_streams'
AND NOT EXISTS (
    SELECT 1
    FROM processing_jobs j
    WHERE j.dataset_id = datasets.dataset_id
      AND j.job_type = 'STREAM_KTH'
);

-- ------------------------------------------------------------
-- 14. Execute example processing jobs
-- ------------------------------------------------------------

DO $$
DECLARE
    current_job RECORD;
BEGIN
    FOR current_job IN
        SELECT job_id
        FROM processing_jobs
        WHERE job_status = 'PENDING'
        ORDER BY job_id
    LOOP
        CALL process_heap_job(current_job.job_id);
    END LOOP;
END;
$$;

-- ------------------------------------------------------------
-- 15. Retrieval queries
-- ------------------------------------------------------------

-- Kth largest: expected third largest = 12.
SELECT kth_largest(
    dataset_id, 3
) AS third_largest
FROM datasets
WHERE dataset_name = 'heap_training';

-- Kth smallest.
SELECT kth_smallest(
    dataset_id, 3
) AS third_smallest
FROM datasets
WHERE dataset_name = 'heap_training';

-- Top four.
SELECT *
FROM top_k_largest(
    (
        SELECT dataset_id
        FROM datasets
        WHERE dataset_name = 'heap_training'
    ),
    4
);

-- Most frequent values.
SELECT *
FROM top_k_frequent(
    (
        SELECT dataset_id
        FROM datasets
        WHERE dataset_name = 'heap_duplicates'
    ),
    3
);

-- ------------------------------------------------------------
-- 16. K-way merge retrieval
-- ------------------------------------------------------------

SELECT *
FROM merge_sorted_streams(
    (
        SELECT dataset_id
        FROM datasets
        WHERE dataset_name = 'heap_streams'
    )
);

-- ------------------------------------------------------------
-- 17. Running median report
-- ------------------------------------------------------------

SELECT
    dataset_name,
    source_sequence,
    numeric_value,
    running_median
FROM running_median_view rm
JOIN datasets d USING (dataset_id)
WHERE d.dataset_name = 'heap_training'
ORDER BY source_sequence;

-- ------------------------------------------------------------
-- 18. Stream kth-largest report
-- ------------------------------------------------------------

SELECT
    source_name,
    source_sequence,
    numeric_value,
    observation_count,
    largest_so_far
FROM stream_kth_largest_view
WHERE dataset_id = (
    SELECT dataset_id
    FROM datasets
    WHERE dataset_name = 'heap_streams'
)
ORDER BY event_time, event_id;

-- ------------------------------------------------------------
-- 19. Job reporting
-- ------------------------------------------------------------

SELECT
    j.job_id,
    d.dataset_name,
    j.job_type,
    j.parameter_k,
    j.job_status,
    j.result_value,
    j.result_payload,
    j.error_message,
    j.created_at,
    j.completed_at
FROM processing_jobs j
JOIN datasets d USING (dataset_id)
ORDER BY j.job_id;

-- ------------------------------------------------------------
-- 20. Aggregation and validation
-- ------------------------------------------------------------

SELECT
    d.dataset_name,
    COUNT(v.value_id) AS total_values,
    MIN(v.numeric_value) AS minimum_value,
    MAX(v.numeric_value) AS maximum_value,
    AVG(v.numeric_value::NUMERIC) AS average_value,
    COUNT(DISTINCT v.numeric_value) AS distinct_values
FROM datasets d
LEFT JOIN dataset_values v USING (dataset_id)
GROUP BY d.dataset_id, d.dataset_name
ORDER BY d.dataset_name;

-- Check datasets containing fewer values than requested k.
SELECT
    j.job_id,
    j.parameter_k,
    COUNT(v.value_id) AS available_values,
    COUNT(v.value_id) >= j.parameter_k AS rank_is_valid
FROM processing_jobs j
LEFT JOIN dataset_values v USING (dataset_id)
GROUP BY j.job_id, j.parameter_k
ORDER BY j.job_id;

-- ------------------------------------------------------------
-- 21. Transaction and failure demonstration
-- ------------------------------------------------------------

SAVEPOINT heap_failure_demo;

-- A failed statement is isolated by a savepoint.
DO $$
BEGIN
    BEGIN
        PERFORM kth_largest(
            (
                SELECT dataset_id
                FROM datasets
                WHERE dataset_name = 'heap_training'
            ),
            1000
        );
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Expected validation failure: %', SQLERRM;
    END;
END;
$$;

ROLLBACK TO SAVEPOINT heap_failure_demo;

RELEASE SAVEPOINT heap_failure_demo;

-- ------------------------------------------------------------
-- 22. Query planning inspection
-- ------------------------------------------------------------

EXPLAIN
SELECT numeric_value
FROM dataset_values
WHERE dataset_id = (
    SELECT dataset_id
    FROM datasets
    WHERE dataset_name = 'heap_training'
)
ORDER BY numeric_value DESC
LIMIT 3;

-- ------------------------------------------------------------
-- 23. Operational notes
-- ------------------------------------------------------------

-- Production deployments should use:
-- 1. Restricted database roles and least-privilege grants.
-- 2. Parameterized queries in application code.
-- 3. Bounded input batches and retention policies.
-- 4. Appropriate statement timeouts.
-- 5. Monitoring of sort memory and temporary-file usage.
-- 6. Idempotent event ingestion and duplicate detection.
-- 7. Explicit transaction boundaries for job execution.
--
-- SQL ranking and window functions produce correct results but
-- do not provide the same incremental O(log k) behavior as a
-- persistent in-memory binary heap.

COMMIT;
