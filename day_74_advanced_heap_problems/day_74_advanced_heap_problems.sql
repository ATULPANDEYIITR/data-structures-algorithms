-- ============================================================
-- ADVANCED HEAP PROBLEMS
-- PostgreSQL 15+
--
-- Relational modeling of heap-based processing:
-- 1. Streaming median observations
-- 2. Priority task scheduling
-- 3. K-way sorted stream merging
-- 4. Greedy capital allocation
-- 5. Minimum refueling optimization
-- 6. Deadline-based profit optimization
--
-- The database uses transactional job claiming, indexed
-- priority selection, integrity constraints, and audit records.
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS heap_lab;

SET search_path TO heap_lab, public;


-- ============================================================
-- 1. ENUM TYPES
-- ============================================================

CREATE TYPE job_status AS ENUM (
    'queued',
    'running',
    'completed',
    'failed',
    'cancelled'
);

CREATE TYPE job_priority AS ENUM (
    'critical',
    'high',
    'normal',
    'low'
);


-- ============================================================
-- 2. REPOSITORY OF JOBS
-- ============================================================

CREATE TABLE jobs (
    job_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    job_code VARCHAR(80) NOT NULL UNIQUE,

    description TEXT NOT NULL,

    priority job_priority NOT NULL DEFAULT 'normal',

    status job_status NOT NULL DEFAULT 'queued',

    estimated_duration_seconds INTEGER NOT NULL
        CHECK (estimated_duration_seconds > 0),

    submitted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    started_at TIMESTAMPTZ,

    completed_at TIMESTAMPTZ,

    result JSONB,

    error_message TEXT,

    attempt_count INTEGER NOT NULL DEFAULT 0
        CHECK (attempt_count >= 0),

    CHECK (
        (status <> 'completed')
        OR completed_at IS NOT NULL
    ),

    CHECK (
        (status <> 'running')
        OR started_at IS NOT NULL
    )
);

CREATE INDEX idx_jobs_priority_queue
ON jobs (
    priority,
    submitted_at,
    job_id
)
WHERE status = 'queued';

CREATE INDEX idx_jobs_status_time
ON jobs(status, submitted_at DESC);

CREATE INDEX idx_jobs_completed
ON jobs(completed_at DESC)
WHERE status = 'completed';


-- ============================================================
-- 3. JOB EXECUTION HISTORY
-- ============================================================

CREATE TABLE job_execution_history (
    execution_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    job_id BIGINT NOT NULL
        REFERENCES jobs(job_id),

    previous_status job_status,

    new_status job_status NOT NULL,

    event_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    details JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX idx_execution_job_time
ON job_execution_history(job_id, event_time DESC);


-- ============================================================
-- 4. JOB STATE VALIDATION
-- ============================================================

CREATE OR REPLACE FUNCTION validate_job_transition()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN

    IF TG_OP = 'UPDATE' THEN

        IF OLD.status IN ('completed', 'cancelled') THEN
            RAISE EXCEPTION
                'Terminal job state cannot be changed: %',
                OLD.status;
        END IF;

        IF OLD.status = 'queued'
           AND NEW.status NOT IN ('queued', 'running', 'cancelled') THEN

            RAISE EXCEPTION
                'Invalid queued job transition';
        END IF;

        IF OLD.status = 'running'
           AND NEW.status NOT IN ('running', 'completed', 'failed') THEN

            RAISE EXCEPTION
                'Invalid running job transition';
        END IF;

        IF NEW.status = 'running'
           AND OLD.status <> 'running' THEN

            NEW.started_at = NOW();
            NEW.attempt_count = OLD.attempt_count + 1;
        END IF;

        IF NEW.status IN ('completed', 'failed', 'cancelled') THEN
            NEW.completed_at = NOW();
        END IF;

    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_job_transition
BEFORE UPDATE OF status
ON jobs
FOR EACH ROW
EXECUTE FUNCTION validate_job_transition();


-- ============================================================
-- 5. JOB AUDIT TRIGGER
-- ============================================================

CREATE OR REPLACE FUNCTION audit_job_transition()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN

    IF OLD.status IS DISTINCT FROM NEW.status THEN

        INSERT INTO job_execution_history (
            job_id,
            previous_status,
            new_status,
            details
        )
        VALUES (
            NEW.job_id,
            OLD.status,
            NEW.status,
            jsonb_build_object(
                'job_code', NEW.job_code,
                'attempt_count', NEW.attempt_count
            )
        );

    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_audit_job_transition
AFTER UPDATE OF status
ON jobs
FOR EACH ROW
EXECUTE FUNCTION audit_job_transition();


-- ============================================================
-- 6. TRANSACTIONAL PRIORITY QUEUE
-- ============================================================

CREATE OR REPLACE FUNCTION claim_next_job()
RETURNS SETOF jobs
LANGUAGE plpgsql
AS $$
BEGIN

    RETURN QUERY
    WITH candidate AS (
        SELECT job_id
        FROM jobs
        WHERE status = 'queued'
        ORDER BY
            CASE priority
                WHEN 'critical' THEN 1
                WHEN 'high' THEN 2
                WHEN 'normal' THEN 3
                WHEN 'low' THEN 4
            END,
            submitted_at,
            job_id
        FOR UPDATE SKIP LOCKED
        LIMIT 1
    )
    UPDATE jobs AS j
    SET status = 'running'
    FROM candidate AS c
    WHERE j.job_id = c.job_id
    RETURNING j.*;

END;
$$;


-- ============================================================
-- 7. JOB COMPLETION PROCEDURE
-- ============================================================

CREATE OR REPLACE PROCEDURE complete_job(
    p_job_id BIGINT,
    p_result JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN

    UPDATE jobs
    SET
        status = 'completed',
        result = p_result,
        error_message = NULL
    WHERE job_id = p_job_id
      AND status = 'running';

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Job % is not currently running',
            p_job_id;
    END IF;

END;
$$;


-- ============================================================
-- 8. STREAMING MEDIAN
-- ============================================================

CREATE TABLE median_streams (
    stream_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    stream_name VARCHAR(100) NOT NULL UNIQUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE median_observations (
    observation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    stream_id BIGINT NOT NULL
        REFERENCES median_streams(stream_id),

    sequence_number BIGINT NOT NULL,

    observed_value NUMERIC(18, 4) NOT NULL,

    observed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(stream_id, sequence_number)
);

CREATE INDEX idx_median_stream_sequence
ON median_observations(stream_id, sequence_number);


-- Window-function median calculation.
CREATE OR REPLACE FUNCTION calculate_stream_median(
    p_stream_id BIGINT
)
RETURNS NUMERIC
LANGUAGE sql
STABLE
AS $$
    SELECT percentile_cont(0.5)
           WITHIN GROUP (
               ORDER BY observed_value
           )
    FROM median_observations
    WHERE stream_id = p_stream_id;
$$;


-- ============================================================
-- 9. SORTED DATA STREAMS
-- ============================================================

CREATE TABLE sorted_streams (
    stream_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    stream_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE sorted_stream_values (
    stream_id BIGINT NOT NULL
        REFERENCES sorted_streams(stream_id),

    position BIGINT NOT NULL CHECK (position >= 0),

    value BIGINT NOT NULL,

    PRIMARY KEY(stream_id, position)
);

CREATE INDEX idx_sorted_values_lookup
ON sorted_stream_values(stream_id, position)
INCLUDE(value);


-- Validate monotonic insertion.
CREATE OR REPLACE FUNCTION validate_sorted_stream_value()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    previous_value BIGINT;
    next_value BIGINT;
BEGIN

    SELECT value
    INTO previous_value
    FROM sorted_stream_values
    WHERE stream_id = NEW.stream_id
      AND position < NEW.position
    ORDER BY position DESC
    LIMIT 1;

    SELECT value
    INTO next_value
    FROM sorted_stream_values
    WHERE stream_id = NEW.stream_id
      AND position > NEW.position
    ORDER BY position
    LIMIT 1;

    IF previous_value IS NOT NULL
       AND NEW.value < previous_value THEN

        RAISE EXCEPTION
            'Value violates ascending order';
    END IF;

    IF next_value IS NOT NULL
       AND NEW.value > next_value THEN

        RAISE EXCEPTION
            'Value violates ascending order';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_sorted_value
BEFORE INSERT OR UPDATE OF value, position
ON sorted_stream_values
FOR EACH ROW
EXECUTE FUNCTION validate_sorted_stream_value();


-- ============================================================
-- 10. K-WAY MERGE QUERY
-- ============================================================

CREATE OR REPLACE FUNCTION merge_sorted_streams()
RETURNS TABLE (
    stream_id BIGINT,
    position BIGINT,
    value BIGINT
)
LANGUAGE sql
STABLE
AS $$
    SELECT
        s.stream_id,
        s.position,
        s.value
    FROM sorted_stream_values AS s
    ORDER BY
        s.value,
        s.stream_id,
        s.position;
$$;


-- ============================================================
-- 11. CAPITAL ALLOCATION
-- ============================================================

CREATE TABLE investment_projects (
    project_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    project_code VARCHAR(80) NOT NULL UNIQUE,

    required_capital NUMERIC(18, 2) NOT NULL
        CHECK (required_capital >= 0),

    expected_profit NUMERIC(18, 2) NOT NULL
        CHECK (expected_profit >= 0),

    active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX idx_projects_affordable
ON investment_projects(
    required_capital,
    expected_profit DESC
)
WHERE active = TRUE;

CREATE TABLE capital_allocation_runs (
    run_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    initial_capital NUMERIC(18, 2) NOT NULL
        CHECK (initial_capital >= 0),

    final_capital NUMERIC(18, 2) NOT NULL,

    project_limit INTEGER NOT NULL
        CHECK (project_limit >= 0),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE capital_allocation_decisions (
    run_id BIGINT NOT NULL
        REFERENCES capital_allocation_runs(run_id),

    project_id BIGINT NOT NULL
        REFERENCES investment_projects(project_id),

    selection_order INTEGER NOT NULL
        CHECK (selection_order > 0),

    capital_before NUMERIC(18, 2) NOT NULL,

    capital_after NUMERIC(18, 2) NOT NULL,

    PRIMARY KEY(run_id, project_id),

    UNIQUE(run_id, selection_order),

    CHECK (capital_after >= capital_before)
);


-- Greedy allocation using repeated affordable-project selection.
CREATE OR REPLACE PROCEDURE allocate_capital(
    p_initial_capital NUMERIC,
    p_project_limit INTEGER,
    INOUT p_run_id BIGINT DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_capital NUMERIC(18, 2);
    v_project investment_projects%ROWTYPE;
    v_order INTEGER := 0;
BEGIN

    IF p_initial_capital < 0 OR p_project_limit < 0 THEN
        RAISE EXCEPTION 'Invalid allocation parameters';
    END IF;

    v_capital := p_initial_capital;

    INSERT INTO capital_allocation_runs (
        initial_capital,
        final_capital,
        project_limit
    )
    VALUES (
        p_initial_capital,
        p_initial_capital,
        p_project_limit
    )
    RETURNING run_id INTO p_run_id;

    WHILE v_order < p_project_limit LOOP

        SELECT *
        INTO v_project
        FROM investment_projects
        WHERE active = TRUE
          AND required_capital <= v_capital
          AND expected_profit > 0
          AND NOT EXISTS (
              SELECT 1
              FROM capital_allocation_decisions d
              WHERE d.run_id = p_run_id
                AND d.project_id = investment_projects.project_id
          )
        ORDER BY
            expected_profit DESC,
            project_id
        LIMIT 1
        FOR UPDATE;

        IF NOT FOUND THEN
            EXIT;
        END IF;

        v_order := v_order + 1;

        INSERT INTO capital_allocation_decisions (
            run_id,
            project_id,
            selection_order,
            capital_before,
            capital_after
        )
        VALUES (
            p_run_id,
            v_project.project_id,
            v_order,
            v_capital,
            v_capital + v_project.expected_profit
        );

        v_capital :=
            v_capital + v_project.expected_profit;

    END LOOP;

    UPDATE capital_allocation_runs
    SET final_capital = v_capital
    WHERE run_id = p_run_id;

END;
$$;


-- ============================================================
-- 12. FUEL STATION OPTIMIZATION
-- ============================================================

CREATE TABLE journeys (
    journey_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    journey_code VARCHAR(80) NOT NULL UNIQUE,

    destination NUMERIC(18, 2) NOT NULL
        CHECK (destination >= 0),

    initial_fuel NUMERIC(18, 2) NOT NULL
        CHECK (initial_fuel >= 0)
);

CREATE TABLE fuel_stations (
    station_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    journey_id BIGINT NOT NULL
        REFERENCES journeys(journey_id),

    position NUMERIC(18, 2) NOT NULL
        CHECK (position >= 0),

    available_fuel NUMERIC(18, 2) NOT NULL
        CHECK (available_fuel >= 0),

    UNIQUE(journey_id, position)
);

CREATE INDEX idx_fuel_station_position
ON fuel_stations(journey_id, position);

CREATE TABLE refueling_results (
    journey_id BIGINT PRIMARY KEY
        REFERENCES journeys(journey_id),

    minimum_stops INTEGER NOT NULL,

    reachable_distance NUMERIC(18, 2) NOT NULL,

    selected_stations BIGINT[] NOT NULL DEFAULT '{}',

    calculated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- Greedy refueling using the largest previously available fuel.
CREATE OR REPLACE PROCEDURE calculate_refueling(
    p_journey_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_target NUMERIC;
    v_reachable NUMERIC;
    v_position NUMERIC;
    v_fuel NUMERIC;

    v_heap NUMERIC[] := ARRAY[]::NUMERIC[];

    v_station_id BIGINT;
    v_best_station BIGINT;

    v_best_fuel NUMERIC;
    v_temp NUMERIC;

    v_selected BIGINT[] := ARRAY[]::BIGINT[];
    v_stops INTEGER := 0;

    station_record RECORD;
BEGIN

    SELECT destination, initial_fuel
    INTO v_target, v_reachable
    FROM journeys
    WHERE journey_id = p_journey_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Journey not found';
    END IF;

    -- Store fuel quantities in a max-heap using array indexing.
    FOR station_record IN
        SELECT station_id, position, available_fuel
        FROM fuel_stations
        WHERE journey_id = p_journey_id
        ORDER BY position, station_id
    LOOP

        v_position := station_record.position;
        v_fuel := station_record.available_fuel;
        v_station_id := station_record.station_id;

        WHILE v_reachable < v_position LOOP

            IF cardinality(v_heap) = 0 THEN
                INSERT INTO refueling_results (
                    journey_id,
                    minimum_stops,
                    reachable_distance,
                    selected_stations
                )
                VALUES (
                    p_journey_id,
                    -1,
                    v_reachable,
                    '{}'
                )
                ON CONFLICT (journey_id)
                DO UPDATE SET
                    minimum_stops = -1,
                    reachable_distance = EXCLUDED.reachable_distance,
                    selected_stations = '{}',
                    calculated_at = NOW();

                RETURN;
            END IF;

            v_best_fuel := v_heap[1];
            v_heap[1] := v_heap[cardinality(v_heap)];
            v_heap := v_heap[1:cardinality(v_heap) - 1];

            -- Restore max-heap property.
            DECLARE
                v_index INTEGER := 1;
                v_left INTEGER;
                v_right INTEGER;
                v_largest INTEGER;
            BEGIN
                LOOP
                    v_left := v_index * 2;
                    v_right := v_left + 1;
                    v_largest := v_index;

                    IF v_left <= cardinality(v_heap)
                       AND v_heap[v_left] > v_heap[v_largest] THEN
                        v_largest := v_left;
                    END IF;

                    IF v_right <= cardinality(v_heap)
                       AND v_heap[v_right] > v_heap[v_largest] THEN
                        v_largest := v_right;
                    END IF;

                    EXIT WHEN v_largest = v_index;

                    v_temp := v_heap[v_index];
                    v_heap[v_index] := v_heap[v_largest];
                    v_heap[v_largest] := v_temp;

                    v_index := v_largest;
                END LOOP;
            END;

            v_reachable := v_reachable + v_best_fuel;
            v_stops := v_stops + 1;
        END LOOP;

        -- Insert the current station fuel into the max heap.
        v_heap := array_append(v_heap, v_fuel);

        DECLARE
            v_index INTEGER := cardinality(v_heap);
            v_parent INTEGER;
        BEGIN
            WHILE v_index > 1 LOOP
                v_parent := v_index / 2;

                EXIT WHEN v_heap[v_parent] >= v_heap[v_index];

                v_temp := v_heap[v_parent];
                v_heap[v_parent] := v_heap[v_index];
                v_heap[v_index] := v_temp;

                v_index := v_parent;
            END LOOP;
        END;

        -- Track stations in a separate indexed table for reporting.
        INSERT INTO refueling_results (
            journey_id,
            minimum_stops,
            reachable_distance,
            selected_stations
        )
        VALUES (
            p_journey_id,
            0,
            v_reachable,
            '{}'
        )
        ON CONFLICT (journey_id) DO NOTHING;

    END LOOP;

    WHILE v_reachable < v_target LOOP

        IF cardinality(v_heap) = 0 THEN
            v_stops := -1;
            EXIT;
        END IF;

        v_best_fuel := v_heap[1];
        v_heap[1] := v_heap[cardinality(v_heap)];
        v_heap := v_heap[1:cardinality(v_heap) - 1];

        DECLARE
            v_index INTEGER := 1;
            v_left INTEGER;
            v_right INTEGER;
            v_largest INTEGER;
        BEGIN
            LOOP
                v_left := v_index * 2;
                v_right := v_left + 1;
                v_largest := v_index;

                IF v_left <= cardinality(v_heap)
                   AND v_heap[v_left] > v_heap[v_largest] THEN
                    v_largest := v_left;
                END IF;

                IF v_right <= cardinality(v_heap)
                   AND v_heap[v_right] > v_heap[v_largest] THEN
                    v_largest := v_right;
                END IF;

                EXIT WHEN v_largest = v_index;

                v_temp := v_heap[v_index];
                v_heap[v_index] := v_heap[v_largest];
                v_heap[v_largest] := v_temp;

                v_index := v_largest;
            END LOOP;
        END;

        v_reachable := v_reachable + v_best_fuel;
        v_stops := v_stops + 1;

    END LOOP;

    INSERT INTO refueling_results (
        journey_id,
        minimum_stops,
        reachable_distance,
        selected_stations
    )
    VALUES (
        p_journey_id,
        v_stops,
        v_reachable,
        '{}'
    )
    ON CONFLICT (journey_id)
    DO UPDATE SET
        minimum_stops = EXCLUDED.minimum_stops,
        reachable_distance = EXCLUDED.reachable_distance,
        selected_stations = EXCLUDED.selected_stations,
        calculated_at = NOW();

END;
$$;


-- ============================================================
-- 13. DEADLINE PROFIT OPTIMIZATION
-- ============================================================

CREATE TABLE deadline_tasks (
    task_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    task_code VARCHAR(80) NOT NULL UNIQUE,

    deadline INTEGER NOT NULL
        CHECK (deadline > 0),

    profit NUMERIC(18, 2) NOT NULL
        CHECK (profit >= 0)
);

CREATE INDEX idx_deadline_tasks
ON deadline_tasks(deadline, profit DESC);

CREATE TABLE deadline_optimization_results (
    optimization_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    total_profit NUMERIC(18, 2) NOT NULL,

    selected_task_ids BIGINT[] NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE OR REPLACE FUNCTION optimize_deadline_tasks()
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    task_record RECORD;

    v_selected BIGINT[] := ARRAY[]::BIGINT[];
    v_profit NUMERIC(18, 2) := 0;

    v_removed_profit NUMERIC(18, 2);
    v_removed_id BIGINT;

    v_result_id BIGINT;
BEGIN

    -- A min-heap is represented by a temporary relational table.
    CREATE TEMP TABLE IF NOT EXISTS selected_deadline_heap (
        task_id BIGINT PRIMARY KEY,
        profit NUMERIC(18, 2) NOT NULL,
        deadline INTEGER NOT NULL
    ) ON COMMIT DROP;

    TRUNCATE selected_deadline_heap;

    FOR task_record IN
        SELECT task_id, deadline, profit
        FROM deadline_tasks
        ORDER BY deadline, task_id
    LOOP

        INSERT INTO selected_deadline_heap (
            task_id,
            profit,
            deadline
        )
        VALUES (
            task_record.task_id,
            task_record.profit,
            task_record.deadline
        );

        v_profit := v_profit + task_record.profit;

        IF (
            SELECT COUNT(*)
            FROM selected_deadline_heap
        ) > task_record.deadline THEN

            SELECT task_id, profit
            INTO v_removed_id, v_removed_profit
            FROM selected_deadline_heap
            ORDER BY profit, task_id
            LIMIT 1;

            DELETE FROM selected_deadline_heap
            WHERE task_id = v_removed_id;

            v_profit := v_profit - v_removed_profit;

        END IF;

    END LOOP;

    SELECT ARRAY_AGG(task_id ORDER BY task_id)
    INTO v_selected
    FROM selected_deadline_heap;

    INSERT INTO deadline_optimization_results (
        total_profit,
        selected_task_ids
    )
    VALUES (
        v_profit,
        COALESCE(v_selected, '{}')
    )
    RETURNING optimization_id INTO v_result_id;

    DROP TABLE selected_deadline_heap;

    RETURN v_result_id;
END;
$$;


-- ============================================================
-- 14. REPORTING VIEWS
-- ============================================================

CREATE OR REPLACE VIEW job_execution_report AS
SELECT
    status,
    priority,
    COUNT(*) AS job_count,
    AVG(estimated_duration_seconds) AS average_duration,
    MAX(submitted_at) AS latest_submission
FROM jobs
GROUP BY status, priority;


CREATE OR REPLACE VIEW project_profit_report AS
SELECT
    project_id,
    project_code,
    required_capital,
    expected_profit,
    CASE
        WHEN expected_profit = 0 THEN 0
        ELSE ROUND(
            expected_profit /
            NULLIF(required_capital, 0),
            4
        )
    END AS profit_to_capital_ratio
FROM investment_projects
WHERE active = TRUE;


CREATE OR REPLACE VIEW median_stream_report AS
SELECT
    s.stream_id,
    s.stream_name,
    COUNT(o.observation_id) AS observation_count,
    percentile_cont(0.5)
        WITHIN GROUP (
            ORDER BY o.observed_value
        ) AS stream_median,
    AVG(o.observed_value) AS average_value
FROM median_streams s
LEFT JOIN median_observations o
    ON o.stream_id = s.stream_id
GROUP BY s.stream_id, s.stream_name;


-- ============================================================
-- 15. SAMPLE DATA
-- ============================================================

INSERT INTO jobs (
    job_code,
    description,
    priority,
    estimated_duration_seconds
)
VALUES
    ('BACKUP-001', 'Database backup', 'normal', 120),
    ('SECURITY-001', 'Security assessment', 'critical', 90),
    ('REPORT-001', 'Generate analytics report', 'high', 60),
    ('ARCHIVE-001', 'Archive old records', 'low', 180);


INSERT INTO median_streams(stream_name)
VALUES ('server_response_times');


INSERT INTO median_observations (
    stream_id,
    sequence_number,
    observed_value
)
SELECT
    s.stream_id,
    x.sequence_number,
    x.observed_value
FROM median_streams s
CROSS JOIN (
    VALUES
        (1, 12.0),
        (2, 4.0),
        (3, 5.0),
        (4, 3.0),
        (5, 8.0),
        (6, 7.0)
) AS x(sequence_number, observed_value)
WHERE s.stream_name = 'server_response_times';


INSERT INTO sorted_streams(stream_name)
VALUES
    ('stream_A'),
    ('stream_B'),
    ('stream_C');


INSERT INTO sorted_stream_values (
    stream_id,
    position,
    value
)
SELECT
    s.stream_id,
    x.position,
    x.value
FROM sorted_streams s
CROSS JOIN LATERAL (
    SELECT
        position,
        value
    FROM (
        VALUES
            (0::BIGINT, 1::BIGINT),
            (1::BIGINT, 4::BIGINT),
            (2::BIGINT, 7::BIGINT)
    ) a(position, value)
    WHERE s.stream_name = 'stream_A'

    UNION ALL

    SELECT position, value
    FROM (
        VALUES
            (0::BIGINT, 2::BIGINT),
            (1::BIGINT, 5::BIGINT),
            (2::BIGINT, 8::BIGINT)
    ) b(position, value)
    WHERE s.stream_name = 'stream_B'

    UNION ALL

    SELECT position, value
    FROM (
        VALUES
            (0::BIGINT, 3::BIGINT),
            (1::BIGINT, 6::BIGINT),
            (2::BIGINT, 9::BIGINT)
    ) c(position, value)
    WHERE s.stream_name = 'stream_C'
) x;


INSERT INTO investment_projects (
    project_code,
    required_capital,
    expected_profit
)
VALUES
    ('INFRASTRUCTURE', 0, 2),
    ('ANALYTICS', 1, 5),
    ('SECURITY', 2, 8),
    ('CLOUD', 5, 10);


INSERT INTO journeys (
    journey_code,
    destination,
    initial_fuel
)
VALUES
    ('ROUTE-001', 100, 10),
    ('ROUTE-002', 100, 5);


INSERT INTO fuel_stations (
    journey_id,
    position,
    available_fuel
)
SELECT
    j.journey_id,
    x.position,
    x.available_fuel
FROM journeys j
CROSS JOIN (
    VALUES
        (10::NUMERIC, 60::NUMERIC),
        (20::NUMERIC, 30::NUMERIC),
        (30::NUMERIC, 30::NUMERIC),
        (60::NUMERIC, 40::NUMERIC)
) x(position, available_fuel)
WHERE j.journey_code = 'ROUTE-001';


INSERT INTO deadline_tasks (
    task_code,
    deadline,
    profit
)
VALUES
    ('TASK-A', 2, 100),
    ('TASK-B', 1, 19),
    ('TASK-C', 2, 27),
    ('TASK-D', 1, 25),
    ('TASK-E', 3, 15);


-- ============================================================
-- 16. WORKFLOW EXECUTION
-- ============================================================

-- Claim one job atomically.
SELECT * FROM claim_next_job();

-- Display median.
SELECT
    stream_name,
    calculate_stream_median(stream_id) AS median
FROM median_streams;

-- Merge sorted streams.
SELECT * FROM merge_sorted_streams();

-- Allocate capital.
CALL allocate_capital(1, 3, NULL);

-- Calculate refueling.
CALL calculate_refueling(
    (
        SELECT journey_id
        FROM journeys
        WHERE journey_code = 'ROUTE-001'
    )
);

-- Optimize deadline tasks.
SELECT optimize_deadline_tasks();


-- ============================================================
-- 17. VALIDATION AND REPORTING
-- ============================================================

-- Job status report.
SELECT *
FROM job_execution_report
ORDER BY status, priority;

-- Median stream report.
SELECT *
FROM median_stream_report;

-- Project eligibility.
SELECT
    project_code,
    required_capital,
    expected_profit,
    CASE
        WHEN required_capital <= 3 THEN 'eligible'
        ELSE 'not eligible'
    END AS eligibility
FROM investment_projects
WHERE active = TRUE;

-- Allocation report.
SELECT
    r.run_id,
    r.initial_capital,
    r.final_capital,
    r.project_limit,
    d.selection_order,
    p.project_code,
    d.capital_before,
    d.capital_after
FROM capital_allocation_runs r
LEFT JOIN capital_allocation_decisions d
    ON d.run_id = r.run_id
LEFT JOIN investment_projects p
    ON p.project_id = d.project_id
ORDER BY r.run_id, d.selection_order;

-- Refueling report.
SELECT
    j.journey_code,
    r.minimum_stops,
    r.reachable_distance,
    r.selected_stations
FROM journeys j
LEFT JOIN refueling_results r
    ON r.journey_id = j.journey_id;

-- Deadline optimization report.
SELECT *
FROM deadline_optimization_results
ORDER BY created_at DESC;

-- Job audit history.
SELECT *
FROM job_execution_history
ORDER BY event_time DESC;


-- ============================================================
-- 18. TRANSACTIONAL FAILURE HANDLING
-- ============================================================

-- This block demonstrates savepoint-based recovery.
-- The invalid operation is isolated without losing valid work.

SAVEPOINT job_validation_checkpoint;

DO $$
BEGIN
    BEGIN
        INSERT INTO jobs (
            job_code,
            description,
            priority,
            estimated_duration_seconds
        )
        VALUES (
            'INVALID-JOB',
            'Invalid duration example',
            'normal',
            -10
        );

    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'Invalid job rejected by database constraint';
    END;
END;
$$;

RELEASE SAVEPOINT job_validation_checkpoint;


-- ============================================================
-- 19. DATABASE INTEGRITY CHECKS
-- ============================================================

-- Duplicate job identifiers are prevented by UNIQUE.
-- Negative duration and fuel are rejected by CHECK.
-- Missing parent records are rejected by FOREIGN KEY.
-- Concurrent job claims use FOR UPDATE SKIP LOCKED.
-- Terminal jobs cannot be reopened through the transition trigger.

COMMIT;
