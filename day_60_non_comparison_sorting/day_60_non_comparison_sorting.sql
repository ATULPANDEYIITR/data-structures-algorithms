-- PostgreSQL 14+
-- Non-comparison sorting laboratory.
--
-- Models sorting jobs, numeric input records, algorithms, execution results,
-- and result validation. Implements counting sort, signed integer radix sort,
-- and numeric bucket sort with PL/pgSQL.

DROP SCHEMA IF EXISTS noncomparison_sorting CASCADE;
CREATE SCHEMA noncomparison_sorting;

SET search_path = noncomparison_sorting, public;

-- ---------------------------------------------------------------------------
-- Algorithm catalogue and workload model
-- ---------------------------------------------------------------------------

CREATE TABLE algorithm_catalog (
    algorithm_key TEXT PRIMARY KEY,
    data_kind TEXT NOT NULL CHECK (
        data_kind IN ('integer', 'decimal', 'both')
    ),
    description TEXT NOT NULL
);

INSERT INTO algorithm_catalog (
    algorithm_key,
    data_kind,
    description
)
VALUES
    (
        'COUNTING',
        'integer',
        'Frequency-array sorting for bounded integer ranges'
    ),
    (
        'RADIX',
        'integer',
        'Stable base-10 LSD sorting for signed 64-bit integers'
    ),
    (
        'BUCKET',
        'decimal',
        'Distribution-based sorting for finite numeric values'
    ),
    (
        'COMPARISON',
        'both',
        'PostgreSQL ordered aggregation used as a reference strategy'
    );

CREATE TABLE sorting_job (
    job_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    job_name TEXT NOT NULL UNIQUE,
    data_kind TEXT NOT NULL CHECK (
        data_kind IN ('integer', 'decimal')
    ),
    requested_algorithm TEXT NOT NULL CHECK (
        requested_algorithm IN (
            'AUTO',
            'COUNTING',
            'RADIX',
            'BUCKET',
            'COMPARISON'
        )
    ),
    job_state TEXT NOT NULL DEFAULT 'queued' CHECK (
        job_state IN ('queued', 'running', 'completed', 'failed')
    ),
    failure_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CHECK (
        (job_state = 'failed' AND failure_reason IS NOT NULL)
        OR
        (job_state <> 'failed' AND failure_reason IS NULL)
    )
);

CREATE TABLE sorting_input (
    input_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    job_id BIGINT NOT NULL REFERENCES sorting_job(job_id)
        ON DELETE CASCADE,
    ordinal INTEGER NOT NULL CHECK (ordinal > 0),
    value NUMERIC NOT NULL,
    UNIQUE (job_id, ordinal),
    CHECK (
        value::TEXT NOT IN ('NaN', 'Infinity', '-Infinity')
    )
);

CREATE INDEX sorting_input_job_ordinal_idx
    ON sorting_input (job_id, ordinal);

CREATE TABLE sorting_execution (
    execution_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    job_id BIGINT NOT NULL REFERENCES sorting_job(job_id)
        ON DELETE CASCADE,
    selected_algorithm TEXT NOT NULL REFERENCES algorithm_catalog(
        algorithm_key
    ),
    sorted_values NUMERIC[] NOT NULL,
    item_count INTEGER NOT NULL CHECK (item_count >= 0),
    elapsed_microseconds NUMERIC(18, 3) NOT NULL CHECK (
        elapsed_microseconds >= 0
    ),
    executed_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

CREATE INDEX sorting_execution_job_time_idx
    ON sorting_execution (job_id, executed_at DESC);

-- ---------------------------------------------------------------------------
-- Counting sort
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION counting_sort(
    p_values BIGINT[],
    p_maximum_range INTEGER DEFAULT 1000000
)
RETURNS BIGINT[]
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    v_minimum BIGINT;
    v_maximum BIGINT;
    v_span NUMERIC;
    v_counts BIGINT[];
    v_result BIGINT[] := ARRAY[]::BIGINT[];
    v_offset INTEGER;
    v_frequency BIGINT;
    v_index INTEGER;
BEGIN
    IF p_maximum_range < 1 THEN
        RAISE EXCEPTION
            'Maximum counting range must be positive';
    END IF;

    IF cardinality(p_values) = 0 THEN
        RETURN ARRAY[]::BIGINT[];
    END IF;

    SELECT MIN(item), MAX(item)
    INTO v_minimum, v_maximum
    FROM unnest(p_values) AS source(item);

    -- Numeric arithmetic avoids BIGINT overflow at extreme endpoints.
    v_span := v_maximum::NUMERIC - v_minimum::NUMERIC + 1;

    IF v_span > p_maximum_range THEN
        RAISE EXCEPTION
            'Counting sort range % exceeds configured limit %',
            v_span,
            p_maximum_range;
    END IF;

    v_counts := array_fill(
        0::BIGINT,
        ARRAY[v_span::INTEGER]
    );

    FOREACH v_index IN ARRAY p_values
    LOOP
        v_offset := (
            v_index::NUMERIC - v_minimum::NUMERIC
        )::INTEGER + 1;

        v_counts[v_offset] := v_counts[v_offset] + 1;
    END LOOP;

    FOR v_offset IN 1..cardinality(v_counts)
    LOOP
        v_frequency := v_counts[v_offset];

        IF v_frequency > 0 THEN
            FOR v_index IN 1..v_frequency
            LOOP
                v_result := array_append(
                    v_result,
                    v_minimum + (v_offset - 1)::BIGINT
                );
            END LOOP;
        END IF;
    END LOOP;

    RETURN v_result;
END;
$$;

-- ---------------------------------------------------------------------------
-- Signed integer radix sort
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION radix_sort_bigint(
    p_values BIGINT[]
)
RETURNS BIGINT[]
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    v_result BIGINT[] := p_values;
    v_temporary BIGINT[];
    v_minimum BIGINT;
    v_maximum BIGINT;
    v_range NUMERIC;
    v_place NUMERIC := 1;
    v_digit INTEGER;
    v_counts INTEGER[];
    v_positions INTEGER[];
    v_total INTEGER;
    v_index INTEGER;
    v_output_index INTEGER;
    v_pass_count INTEGER := 0;
BEGIN
    IF cardinality(p_values) < 2 THEN
        RETURN p_values;
    END IF;

    SELECT MIN(item), MAX(item)
    INTO v_minimum, v_maximum
    FROM unnest(p_values) AS source(item);

    -- Offset keys make negative and positive values non-negative.
    -- Numeric keys avoid overflow for BIGINT_MIN to BIGINT_MAX.
    v_range := v_maximum::NUMERIC - v_minimum::NUMERIC;

    WHILE v_place <= v_range
    LOOP
        v_counts := array_fill(0, ARRAY[10]);
        v_positions := array_fill(0, ARRAY[10]);

        FOR v_index IN 1..cardinality(v_result)
        LOOP
            v_digit := (
                MOD(
                    TRUNC(
                        (v_result[v_index]::NUMERIC -
                         v_minimum::NUMERIC) / v_place
                    ),
                    10
                )
            )::INTEGER + 1;

            v_counts[v_digit] := v_counts[v_digit] + 1;
        END LOOP;

        -- Prefix totals give the final output position of each digit.
        v_total := 0;

        FOR v_index IN 1..10
        LOOP
            v_total := v_total + v_counts[v_index];
            v_positions[v_index] := v_total;
        END LOOP;

        v_temporary := array_fill(
            0::BIGINT,
            ARRAY[cardinality(v_result)]
        );

        -- Reverse traversal preserves the stability of the LSD pass.
        FOR v_index IN REVERSE cardinality(v_result)..1
        LOOP
            v_digit := (
                MOD(
                    TRUNC(
                        (v_result[v_index]::NUMERIC -
                         v_minimum::NUMERIC) / v_place
                    ),
                    10
                )
            )::INTEGER + 1;

            v_output_index := v_positions[v_digit];
            v_temporary[v_output_index] := v_result[v_index];
            v_positions[v_digit] := v_positions[v_digit] - 1;
        END LOOP;

        v_result := v_temporary;
        v_place := v_place * 10;
        v_pass_count := v_pass_count + 1;

        IF v_pass_count > 20 THEN
            RAISE EXCEPTION
                'Unexpected radix pass count for BIGINT input';
        END IF;
    END LOOP;

    RETURN v_result;
END;
$$;

-- ---------------------------------------------------------------------------
-- Bucket sort for finite numeric values
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION bucket_sort_numeric(
    p_values NUMERIC[],
    p_bucket_limit INTEGER DEFAULT 10000
)
RETURNS NUMERIC[]
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
DECLARE
    v_minimum NUMERIC;
    v_maximum NUMERIC;
    v_span NUMERIC;
    v_count INTEGER;
    v_bucket_index INTEGER;
    v_buckets JSONB := '{}'::JSONB;
    v_result NUMERIC[] := ARRAY[]::NUMERIC[];
    v_sorted_bucket NUMERIC[];
    v_value NUMERIC;
    v_bucket JSONB;
    v_index INTEGER;
BEGIN
    IF p_bucket_limit < 1 OR p_bucket_limit > 10000 THEN
        RAISE EXCEPTION
            'Bucket limit must be between 1 and 10000';
    END IF;

    v_count := cardinality(p_values);

    IF v_count = 0 THEN
        RETURN ARRAY[]::NUMERIC[];
    END IF;

    FOREACH v_value IN ARRAY p_values
    LOOP
        IF v_value::TEXT IN ('NaN', 'Infinity', '-Infinity') THEN
            RAISE EXCEPTION
                'Bucket sort accepts finite numeric values only';
        END IF;
    END LOOP;

    SELECT MIN(item), MAX(item)
    INTO v_minimum, v_maximum
    FROM unnest(p_values) AS source(item);

    v_span := v_maximum - v_minimum;

    IF v_span = 0 THEN
        RETURN p_values;
    END IF;

    v_bucket_index := LEAST(
        p_bucket_limit,
        GREATEST(
            1,
            CEIL(SQRT(v_count::NUMERIC))::INTEGER
        )
    );

    -- JSONB arrays support buckets of different lengths.
    FOR v_index IN 0..v_bucket_index - 1
    LOOP
        v_buckets := jsonb_set(
            v_buckets,
            ARRAY[v_index::TEXT],
            '[]'::JSONB,
            TRUE
        );
    END LOOP;

    FOREACH v_value IN ARRAY p_values
    LOOP
        v_index := FLOOR(
            ((v_value - v_minimum) / v_span) * v_bucket_index
        )::INTEGER;

        v_index := GREATEST(
            0,
            LEAST(v_bucket_index - 1, v_index)
        );

        v_bucket := v_buckets -> (v_index::TEXT);

        v_buckets := jsonb_set(
            v_buckets,
            ARRAY[v_index::TEXT],
            v_bucket || jsonb_build_array(v_value),
            TRUE
        );
    END LOOP;

    -- Each bucket is independently sorted before concatenation.
    FOR v_index IN 0..v_bucket_index - 1
    LOOP
        SELECT array_agg(item::NUMERIC ORDER BY item::NUMERIC)
        INTO v_sorted_bucket
        FROM jsonb_array_elements_text(
            v_buckets -> (v_index::TEXT)
        ) AS bucket_items(item);

        v_result := v_result || COALESCE(
            v_sorted_bucket,
            ARRAY[]::NUMERIC[]
        );
    END LOOP;

    RETURN v_result;
END;
$$;

-- ---------------------------------------------------------------------------
-- Database-level result validation
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_sorting_execution()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_job_kind TEXT;
    v_input_values NUMERIC[];
    v_output_values NUMERIC[];
    v_input_count INTEGER;
BEGIN
    SELECT data_kind
    INTO v_job_kind
    FROM sorting_job
    WHERE job_id = NEW.job_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Sorting job % does not exist',
            NEW.job_id;
    END IF;

    SELECT
        COALESCE(
            array_agg(value ORDER BY value, ordinal),
            ARRAY[]::NUMERIC[]
        ),
        COUNT(*)::INTEGER
    INTO v_input_values, v_input_count
    FROM sorting_input
    WHERE job_id = NEW.job_id;

    IF NEW.item_count <> v_input_count THEN
        RAISE EXCEPTION
            'Execution item count does not match input item count';
    END IF;

    IF cardinality(NEW.sorted_values) <> v_input_count THEN
        RAISE EXCEPTION
            'Output cardinality does not match input cardinality';
    END IF;

    SELECT COALESCE(
        array_agg(item ORDER BY item),
        ARRAY[]::NUMERIC[]
    )
    INTO v_output_values
    FROM unnest(NEW.sorted_values) AS result(item);

    IF v_input_values IS DISTINCT FROM v_output_values THEN
        RAISE EXCEPTION
            'Sorting output does not preserve the input multiset';
    END IF;

    IF v_job_kind = 'integer'
       AND NEW.selected_algorithm = 'BUCKET' THEN
        RAISE EXCEPTION
            'Bucket algorithm is not configured for integer jobs';
    END IF;

    IF v_job_kind = 'decimal'
       AND NEW.selected_algorithm IN ('COUNTING', 'RADIX') THEN
        RAISE EXCEPTION
            'Integer algorithm cannot process decimal jobs';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER sorting_execution_validation_trigger
BEFORE INSERT OR UPDATE ON sorting_execution
FOR EACH ROW
EXECUTE FUNCTION validate_sorting_execution();

-- ---------------------------------------------------------------------------
-- Sorting workflow
-- ---------------------------------------------------------------------------

CREATE OR REPLACE PROCEDURE execute_sorting_job(
    p_job_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_job sorting_job%ROWTYPE;
    v_input_numeric NUMERIC[];
    v_input_integer BIGINT[];
    v_output_integer BIGINT[];
    v_output_numeric NUMERIC[];
    v_algorithm TEXT;
    v_minimum NUMERIC;
    v_maximum NUMERIC;
    v_span NUMERIC;
    v_count INTEGER;
    v_started TIMESTAMPTZ;
    v_elapsed NUMERIC;
BEGIN
    SELECT *
    INTO v_job
    FROM sorting_job
    WHERE job_id = p_job_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Sorting job % does not exist',
            p_job_id;
    END IF;

    IF v_job.job_state <> 'queued' THEN
        RAISE EXCEPTION
            'Job % cannot execute from state %',
            p_job_id,
            v_job.job_state;
    END IF;

    UPDATE sorting_job
    SET job_state = 'running'
    WHERE job_id = p_job_id;

    v_started := clock_timestamp();

    SELECT
        COALESCE(
            array_agg(value ORDER BY ordinal),
            ARRAY[]::NUMERIC[]
        ),
        COUNT(*)::INTEGER,
        MIN(value),
        MAX(value)
    INTO
        v_input_numeric,
        v_count,
        v_minimum,
        v_maximum
    FROM sorting_input
    WHERE job_id = p_job_id;

    v_algorithm := v_job.requested_algorithm;

    IF v_algorithm = 'AUTO' THEN
        IF v_job.data_kind = 'decimal' THEN
            v_algorithm := 'BUCKET';
        ELSE
            v_span := COALESCE(
                v_maximum - v_minimum + 1,
                0
            );

            IF (
                v_span <= 1000000
                AND v_span <= GREATEST(256, v_count * 16)
            ) THEN
                v_algorithm := 'COUNTING';
            ELSE
                v_algorithm := 'RADIX';
            END IF;
        END IF;
    END IF;

    IF v_job.data_kind = 'integer' THEN
        IF EXISTS (
            SELECT 1
            FROM sorting_input
            WHERE job_id = p_job_id
              AND value <> TRUNC(value)
        ) THEN
            RAISE EXCEPTION
                'Integer job % contains fractional values',
                p_job_id;
        END IF;

        IF EXISTS (
            SELECT 1
            FROM sorting_input
            WHERE job_id = p_job_id
              AND (
                  value < -9223372036854775808::NUMERIC
                  OR
                  value > 9223372036854775807::NUMERIC
              )
        ) THEN
            RAISE EXCEPTION
                'Integer job % contains values outside BIGINT range',
                p_job_id;
        END IF;

        IF v_algorithm NOT IN ('COUNTING', 'RADIX', 'COMPARISON') THEN
            RAISE EXCEPTION
                'Algorithm % is incompatible with integer jobs',
                v_algorithm;
        END IF;

        SELECT COALESCE(
            array_agg(value::BIGINT ORDER BY ordinal),
            ARRAY[]::BIGINT[]
        )
        INTO v_input_integer
        FROM sorting_input
        WHERE job_id = p_job_id;

        CASE v_algorithm
            WHEN 'COUNTING' THEN
                v_output_integer := counting_sort(v_input_integer);
            WHEN 'RADIX' THEN
                v_output_integer := radix_sort_bigint(v_input_integer);
            WHEN 'COMPARISON' THEN
                SELECT COALESCE(
                    array_agg(value::BIGINT ORDER BY value),
                    ARRAY[]::BIGINT[]
                )
                INTO v_output_integer
                FROM unnest(v_input_integer) AS source(value);
            ELSE
                RAISE EXCEPTION
                    'Unsupported integer algorithm %',
                    v_algorithm;
        END CASE;

        SELECT COALESCE(
            array_agg(value::NUMERIC),
            ARRAY[]::NUMERIC[]
        )
        INTO v_output_numeric
        FROM unnest(v_output_integer) AS output(value);

    ELSE
        IF v_algorithm NOT IN ('BUCKET', 'COMPARISON') THEN
            RAISE EXCEPTION
                'Algorithm % is incompatible with decimal jobs',
                v_algorithm;
        END IF;

        IF v_algorithm = 'BUCKET' THEN
            v_output_numeric := bucket_sort_numeric(v_input_numeric);
        ELSE
            SELECT COALESCE(
                array_agg(value ORDER BY value),
                ARRAY[]::NUMERIC[]
            )
            INTO v_output_numeric
            FROM unnest(v_input_numeric) AS source(value);
        END IF;
    END IF;

    v_elapsed := GREATEST(
        0,
        EXTRACT(EPOCH FROM clock_timestamp() - v_started) * 1000000
    );

    INSERT INTO sorting_execution (
        job_id,
        selected_algorithm,
        sorted_values,
        item_count,
        elapsed_microseconds
    )
    VALUES (
        p_job_id,
        v_algorithm,
        v_output_numeric,
        v_count,
        v_elapsed
    );

    UPDATE sorting_job
    SET job_state = 'completed'
    WHERE job_id = p_job_id;
END;
$$;

-- ---------------------------------------------------------------------------
-- Reporting view
-- ---------------------------------------------------------------------------

CREATE OR REPLACE VIEW sorting_job_report AS
SELECT
    job.job_id,
    job.job_name,
    job.data_kind,
    job.requested_algorithm,
    job.job_state,
    job.failure_reason,
    job.created_at,
    COUNT(DISTINCT input.input_id)::INTEGER AS input_count,
    execution.selected_algorithm,
    execution.sorted_values,
    execution.elapsed_microseconds,
    execution.executed_at
FROM sorting_job AS job
LEFT JOIN sorting_input AS input
    ON input.job_id = job.job_id
LEFT JOIN LATERAL (
    SELECT
        selected_algorithm,
        sorted_values,
        elapsed_microseconds,
        executed_at
    FROM sorting_execution
    WHERE job_id = job.job_id
    ORDER BY executed_at DESC, execution_id DESC
    LIMIT 1
) AS execution ON TRUE
GROUP BY
    job.job_id,
    job.job_name,
    job.data_kind,
    job.requested_algorithm,
    job.job_state,
    job.failure_reason,
    job.created_at,
    execution.selected_algorithm,
    execution.sorted_values,
    execution.elapsed_microseconds,
    execution.executed_at;

-- ---------------------------------------------------------------------------
-- Sample workloads
-- ---------------------------------------------------------------------------

INSERT INTO sorting_job (
    job_name,
    data_kind,
    requested_algorithm
)
VALUES
    ('sensor-status-codes', 'integer', 'AUTO'),
    ('wide-event-identifiers', 'integer', 'RADIX'),
    ('network-latency-readings', 'decimal', 'BUCKET'),
    ('empty-integer-batch', 'integer', 'AUTO');

INSERT INTO sorting_input (job_id, ordinal, value)
SELECT
    job.job_id,
    sample.ordinal,
    sample.value
FROM sorting_job AS job
CROSS JOIN (
    VALUES
        (1, 4::NUMERIC),
        (2, -2::NUMERIC),
        (3, 7::NUMERIC),
        (4, 4::NUMERIC),
        (5, 0::NUMERIC),
        (6, -2::NUMERIC),
        (7, 3::NUMERIC),
        (8, 1::NUMERIC)
) AS sample(ordinal, value)
WHERE job.job_name = 'sensor-status-codes';

INSERT INTO sorting_input (job_id, ordinal, value)
SELECT
    job.job_id,
    sample.ordinal,
    sample.value
FROM sorting_job AS job
CROSS JOIN (
    VALUES
        (1, 9000000000::NUMERIC),
        (2, -8000000000::NUMERIC),
        (3, 0::NUMERIC),
        (4, 42::NUMERIC),
        (5, -1::NUMERIC),
        (6, 9000000000::NUMERIC)
) AS sample(ordinal, value)
WHERE job.job_name = 'wide-event-identifiers';

INSERT INTO sorting_input (job_id, ordinal, value)
SELECT
    job.job_id,
    sample.ordinal,
    sample.value
FROM sorting_job AS job
CROSS JOIN (
    VALUES
        (1, 0.42::NUMERIC),
        (2, 0.32::NUMERIC),
        (3, 0.23::NUMERIC),
        (4, 0.52::NUMERIC),
        (5, 0.25::NUMERIC),
        (6, 0.47::NUMERIC),
        (7, 0.51::NUMERIC)
) AS sample(ordinal, value)
WHERE job.job_name = 'network-latency-readings';

-- A failed job illustrates a persisted rejection state.
INSERT INTO sorting_job (
    job_name,
    data_kind,
    requested_algorithm,
    job_state,
    failure_reason
)
VALUES (
    'rejected-fractional-integer-batch',
    'integer',
    'COUNTING',
    'failed',
    'A prior validation stage rejected fractional input values.'
);

-- ---------------------------------------------------------------------------
-- Execute the valid sample jobs transactionally
-- ---------------------------------------------------------------------------

CALL execute_sorting_job(
    (
        SELECT job_id
        FROM sorting_job
        WHERE job_name = 'sensor-status-codes'
    )
);

CALL execute_sorting_job(
    (
        SELECT job_id
        FROM sorting_job
        WHERE job_name = 'wide-event-identifiers'
    )
);

CALL execute_sorting_job(
    (
        SELECT job_id
        FROM sorting_job
        WHERE job_name = 'network-latency-readings'
    )
);

CALL execute_sorting_job(
    (
        SELECT job_id
        FROM sorting_job
        WHERE job_name = 'empty-integer-batch'
    )
);

-- ---------------------------------------------------------------------------
-- Retrieval, validation, aggregation, and reporting queries
-- ---------------------------------------------------------------------------

-- 1. Job and execution details.
SELECT
    job_id,
    job_name,
    data_kind,
    requested_algorithm,
    selected_algorithm,
    job_state,
    input_count,
    sorted_values,
    elapsed_microseconds
FROM sorting_job_report
ORDER BY job_id;

-- 2. Check that every completed execution is non-decreasing.
SELECT
    execution_id,
    job_id,
    selected_algorithm,
    sorted_values,
    NOT EXISTS (
        SELECT 1
        FROM generate_subscripts(sorted_values, 1) AS positions(index)
        WHERE positions.index > 1
          AND sorted_values[positions.index] <
              sorted_values[positions.index - 1]
    ) AS is_sorted
FROM sorting_execution
ORDER BY execution_id;

-- 3. Compare average measured runtime by selected algorithm.
SELECT
    selected_algorithm,
    COUNT(*) AS executions,
    ROUND(AVG(elapsed_microseconds), 3) AS average_microseconds,
    MAX(item_count) AS largest_input
FROM sorting_execution
GROUP BY selected_algorithm
ORDER BY selected_algorithm;

-- 4. Inspect frequency distribution for an input workload.
SELECT
    input.value,
    COUNT(*) AS frequency
FROM sorting_input AS input
JOIN sorting_job AS job USING (job_id)
WHERE job.job_name = 'sensor-status-codes'
GROUP BY input.value
ORDER BY input.value;

-- 5. Inspect state counts and failed-job reasons.
SELECT
    job_state,
    COUNT(*) AS number_of_jobs
FROM sorting_job
GROUP BY job_state
ORDER BY job_state;

SELECT
    job_name,
    failure_reason
FROM sorting_job
WHERE job_state = 'failed';

-- 6. Verify that the stored input and output cardinalities match.
SELECT
    job.job_name,
    COUNT(DISTINCT input.input_id) AS input_count,
    MAX(execution.item_count) AS execution_count,
    COUNT(DISTINCT input.input_id) =
        MAX(execution.item_count) AS cardinality_matches
FROM sorting_job AS job
LEFT JOIN sorting_input AS input
    ON input.job_id = job.job_id
LEFT JOIN sorting_execution AS execution
    ON execution.job_id = job.job_id
GROUP BY job.job_id, job.job_name
ORDER BY job.job_id;

-- 7. Direct function tests for signed values and duplicates.
SELECT counting_sort(
    ARRAY[4, -2, 7, 4, 0, -2, 3, 1]::BIGINT[]
) AS counting_sort_result;

SELECT radix_sort_bigint(
    ARRAY[
        9223372036854775807,
        0,
        -9223372036854775808,
        42,
        -1
    ]::BIGINT[]
) AS radix_sort_result;

SELECT bucket_sort_numeric(
    ARRAY[0.42, 0.32, 0.23, 0.52, 0.25, 0.47, 0.51]::NUMERIC[]
) AS bucket_sort_result;

-- 8. Demonstrate a range-policy check without intentionally aborting a job.
SELECT
    10000001::NUMERIC AS requested_counting_range,
    1000000::INTEGER AS configured_maximum,
    10000001::NUMERIC <= 1000000::INTEGER AS counting_range_allowed;
