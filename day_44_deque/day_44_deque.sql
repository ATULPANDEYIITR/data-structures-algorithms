-- PostgreSQL 15+
-- Sliding-window analytics for operational telemetry.
--
-- The relational model stores incoming measurements and materializes
-- rolling minimum/maximum results. The SQL window functions provide a
-- transparent reference implementation; the indexes support time-series
-- filtering and partitioned analysis.

BEGIN;

CREATE SCHEMA IF NOT EXISTS deque_lab;
SET LOCAL search_path TO deque_lab, public;

CREATE TABLE IF NOT EXISTS monitored_streams (
    stream_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    stream_name TEXT NOT NULL UNIQUE,
    measurement_unit TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT stream_name_not_blank
        CHECK (length(trim(stream_name)) > 0),
    CONSTRAINT stream_unit_not_blank
        CHECK (length(trim(measurement_unit)) > 0)
);

CREATE TABLE IF NOT EXISTS measurements (
    measurement_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    stream_id BIGINT NOT NULL
        REFERENCES monitored_streams(stream_id) ON DELETE CASCADE,
    observed_at TIMESTAMPTZ NOT NULL,
    sequence_number BIGINT NOT NULL CHECK (sequence_number >= 0),
    measured_value DOUBLE PRECISION NOT NULL,
    CONSTRAINT measurement_finite_value
        CHECK (
            measured_value > '-Infinity'::DOUBLE PRECISION
            AND measured_value < 'Infinity'::DOUBLE PRECISION
        ),
    CONSTRAINT unique_stream_sequence
        UNIQUE (stream_id, sequence_number)
);

-- The leading stream_id supports per-stream analysis; observed_at supports
-- time-range queries. Sequence numbers disambiguate equal timestamps.
CREATE INDEX IF NOT EXISTS idx_measurements_stream_time
    ON measurements (stream_id, observed_at, sequence_number);

CREATE TABLE IF NOT EXISTS window_policies (
    policy_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    stream_id BIGINT NOT NULL
        REFERENCES monitored_streams(stream_id) ON DELETE CASCADE,
    window_size INTEGER NOT NULL CHECK (window_size > 0),
    policy_name TEXT NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT unique_stream_policy_name UNIQUE (stream_id, policy_name),
    CONSTRAINT policy_name_not_blank CHECK (length(trim(policy_name)) > 0)
);

CREATE TABLE IF NOT EXISTS window_results (
    result_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    policy_id BIGINT NOT NULL
        REFERENCES window_policies(policy_id) ON DELETE CASCADE,
    first_sequence BIGINT NOT NULL,
    last_sequence BIGINT NOT NULL,
    minimum_value DOUBLE PRECISION NOT NULL,
    maximum_value DOUBLE PRECISION NOT NULL,
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_window_bounds
        CHECK (first_sequence >= 0 AND last_sequence >= first_sequence),
    CONSTRAINT valid_window_extrema
        CHECK (
            minimum_value <= maximum_value
            AND minimum_value > '-Infinity'::DOUBLE PRECISION
            AND maximum_value < 'Infinity'::DOUBLE PRECISION
        ),
    CONSTRAINT unique_policy_window
        UNIQUE (policy_id, first_sequence, last_sequence)
);

CREATE INDEX IF NOT EXISTS idx_window_results_policy_end
    ON window_results (policy_id, last_sequence DESC);

INSERT INTO monitored_streams (
    stream_name,
    measurement_unit
)
VALUES
    ('api_latency', 'milliseconds'),
    ('memory_usage', 'percent'),
    ('queue_depth', 'requests')
ON CONFLICT (stream_name) DO NOTHING;

INSERT INTO window_policies (
    stream_id,
    window_size,
    policy_name
)
SELECT stream_id, 3, 'three_sample_extrema'
FROM monitored_streams
WHERE stream_name IN ('api_latency', 'memory_usage', 'queue_depth')
ON CONFLICT (stream_id, policy_name) DO NOTHING;

-- Deterministic sample data allows the result of every window to be checked.
INSERT INTO measurements (
    stream_id,
    observed_at,
    sequence_number,
    measured_value
)
SELECT
    stream.stream_id,
    TIMESTAMPTZ '2026-10-14 08:00:00+05:30'
        + sample.sequence_number * INTERVAL '1 minute',
    sample.sequence_number,
    sample.measured_value
FROM (
    VALUES
        ('api_latency', 0::BIGINT, 18.2::DOUBLE PRECISION),
        ('api_latency', 1::BIGINT, 19.1::DOUBLE PRECISION),
        ('api_latency', 2::BIGINT, 17.4::DOUBLE PRECISION),
        ('api_latency', 3::BIGINT, 20.6::DOUBLE PRECISION),
        ('api_latency', 4::BIGINT, 21.3::DOUBLE PRECISION),
        ('api_latency', 5::BIGINT, 16.8::DOUBLE PRECISION),
        ('api_latency', 6::BIGINT, 18.9::DOUBLE PRECISION),
        ('memory_usage', 0::BIGINT, 61.0::DOUBLE PRECISION),
        ('memory_usage', 1::BIGINT, 63.0::DOUBLE PRECISION),
        ('memory_usage', 2::BIGINT, 62.0::DOUBLE PRECISION),
        ('memory_usage', 3::BIGINT, 71.0::DOUBLE PRECISION),
        ('memory_usage', 4::BIGINT, 69.0::DOUBLE PRECISION),
        ('queue_depth', 0::BIGINT, 4.0::DOUBLE PRECISION),
        ('queue_depth', 1::BIGINT, 8.0::DOUBLE PRECISION),
        ('queue_depth', 2::BIGINT, 3.0::DOUBLE PRECISION),
        ('queue_depth', 3::BIGINT, 11.0::DOUBLE PRECISION)
) AS sample(stream_name, sequence_number, measured_value)
JOIN monitored_streams AS stream
    ON stream.stream_name = sample.stream_name
ON CONFLICT (stream_id, sequence_number) DO NOTHING;

-- ROWS BETWEEN uses the current row and preceding rows in the ordering.
-- The full window is emitted only when the requested count is available.
WITH ordered_measurements AS (
    SELECT
        m.stream_id,
        m.sequence_number,
        m.observed_at,
        m.measured_value,
        p.policy_id,
        p.window_size,
        COUNT(*) OVER window_frame AS samples_in_frame,
        MIN(m.measured_value) OVER window_frame AS minimum_value,
        MAX(m.measured_value) OVER window_frame AS maximum_value,
        FIRST_VALUE(m.sequence_number) OVER window_frame AS first_sequence
    FROM measurements AS m
    JOIN window_policies AS p
        ON p.stream_id = m.stream_id
       AND p.enabled
    WINDOW window_frame AS (
        PARTITION BY m.stream_id, p.policy_id
        ORDER BY m.sequence_number
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    )
)
SELECT
    stream_id,
    policy_id,
    first_sequence,
    sequence_number AS last_sequence,
    minimum_value,
    maximum_value
FROM ordered_measurements
WHERE samples_in_frame = window_size
ORDER BY stream_id, sequence_number;

-- PostgreSQL frame bounds are static SQL syntax. For a configurable window
-- size, generate the frame in trusted application code or use a correlated
-- query. The following query supports each policy's actual window_size.
SELECT
    stream.stream_name,
    policy.policy_name,
    current_measurement.sequence_number AS last_sequence,
    current_measurement.sequence_number - policy.window_size + 1
        AS first_sequence,
    extrema.minimum_value,
    extrema.maximum_value
FROM window_policies AS policy
JOIN monitored_streams AS stream
    ON stream.stream_id = policy.stream_id
JOIN measurements AS current_measurement
    ON current_measurement.stream_id = policy.stream_id
CROSS JOIN LATERAL (
    SELECT
        MIN(prior.measured_value) AS minimum_value,
        MAX(prior.measured_value) AS maximum_value,
        COUNT(*) AS sample_count
    FROM measurements AS prior
    WHERE prior.stream_id = policy.stream_id
      AND prior.sequence_number BETWEEN
          current_measurement.sequence_number - policy.window_size + 1
          AND current_measurement.sequence_number
) AS extrema
WHERE policy.enabled
  AND extrema.sample_count = policy.window_size
ORDER BY stream.stream_name, last_sequence;

-- Persist calculated results atomically. Re-running the statement is safe
-- because the policy/window uniqueness constraint prevents duplicates.
WITH computed AS (
    SELECT
        policy.policy_id,
        current_measurement.sequence_number - policy.window_size + 1
            AS first_sequence,
        current_measurement.sequence_number AS last_sequence,
        extrema.minimum_value,
        extrema.maximum_value,
        extrema.sample_count,
        policy.window_size
    FROM window_policies AS policy
    JOIN measurements AS current_measurement
        ON current_measurement.stream_id = policy.stream_id
    CROSS JOIN LATERAL (
        SELECT
            MIN(prior.measured_value) AS minimum_value,
            MAX(prior.measured_value) AS maximum_value,
            COUNT(*) AS sample_count
        FROM measurements AS prior
        WHERE prior.stream_id = policy.stream_id
          AND prior.sequence_number BETWEEN
              current_measurement.sequence_number - policy.window_size + 1
              AND current_measurement.sequence_number
    ) AS extrema
    WHERE policy.enabled
)
INSERT INTO window_results (
    policy_id,
    first_sequence,
    last_sequence,
    minimum_value,
    maximum_value
)
SELECT
    policy_id,
    first_sequence,
    last_sequence,
    minimum_value,
    maximum_value
FROM computed
WHERE sample_count = window_size
ON CONFLICT (policy_id, first_sequence, last_sequence)
DO UPDATE SET
    minimum_value = EXCLUDED.minimum_value,
    maximum_value = EXCLUDED.maximum_value,
    calculated_at = CURRENT_TIMESTAMP;

CREATE OR REPLACE VIEW latest_window_extrema AS
SELECT
    stream.stream_name,
    policy.policy_name,
    result.first_sequence,
    result.last_sequence,
    result.minimum_value,
    result.maximum_value,
    result.calculated_at
FROM window_results AS result
JOIN window_policies AS policy
    ON policy.policy_id = result.policy_id
JOIN monitored_streams AS stream
    ON stream.stream_id = policy.stream_id;

SELECT *
FROM latest_window_extrema
ORDER BY stream_name, last_sequence;

-- Integrity checks: this query returns no rows if every stored window
-- contains the true minimum and maximum of its referenced interval.
SELECT
    result.result_id,
    result.first_sequence,
    result.last_sequence,
    result.minimum_value AS stored_minimum,
    actual.minimum_value AS recomputed_minimum,
    result.maximum_value AS stored_maximum,
    actual.maximum_value AS recomputed_maximum
FROM window_results AS result
JOIN window_policies AS policy
    ON policy.policy_id = result.policy_id
CROSS JOIN LATERAL (
    SELECT
        MIN(measurement.measured_value) AS minimum_value,
        MAX(measurement.measured_value) AS maximum_value,
        COUNT(*) AS sample_count
    FROM measurements AS measurement
    WHERE measurement.stream_id = policy.stream_id
      AND measurement.sequence_number BETWEEN
          result.first_sequence AND result.last_sequence
) AS actual
WHERE actual.sample_count <> policy.window_size
   OR actual.minimum_value <> result.minimum_value
   OR actual.maximum_value <> result.maximum_value;

COMMIT;
