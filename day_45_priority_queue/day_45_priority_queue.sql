-- PostgreSQL 15+
-- Priority queues, heap-backed scheduling concepts, and job processing.
--
-- The database stores the authoritative scheduling state and exposes
-- deterministic dispatch order. PostgreSQL does not expose its internal
-- index heap as an application-level priority queue. ORDER BY with indexes
-- and row locking provides the corresponding relational workflow.
--
-- Run this script in a disposable database because it recreates its schema.

BEGIN;

DROP SCHEMA IF EXISTS priority_queue_lab CASCADE;
CREATE SCHEMA priority_queue_lab;
SET search_path TO priority_queue_lab, public;

CREATE TYPE job_state AS ENUM (
    'queued',
    'running',
    'completed',
    'cancelled',
    'failed'
);

CREATE TYPE job_kind AS ENUM (
    'security_scan',
    'compile',
    'integration_test',
    'deployment',
    'report'
);

CREATE TABLE workers (
    worker_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    worker_name TEXT NOT NULL UNIQUE,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    CHECK (length(trim(worker_name)) > 0)
);

CREATE TABLE jobs (
    job_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    external_key TEXT NOT NULL UNIQUE,
    repository_name TEXT NOT NULL,
    kind job_kind NOT NULL,
    description TEXT NOT NULL,
    priority SMALLINT NOT NULL DEFAULT 50,
    estimated_seconds INTEGER NOT NULL DEFAULT 0,
    state job_state NOT NULL DEFAULT 'queued',
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    queued_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    worker_id BIGINT REFERENCES workers(worker_id),
    attempts INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL DEFAULT 3,
    CHECK (length(trim(external_key)) > 0),
    CHECK (length(trim(repository_name)) > 0),
    CHECK (length(trim(description)) > 0),
    CHECK (priority BETWEEN 0 AND 100),
    CHECK (estimated_seconds >= 0),
    CHECK (attempts >= 0),
    CHECK (max_attempts BETWEEN 1 AND 20),
    CHECK (attempts <= max_attempts),
    CHECK (finished_at IS NULL OR started_at IS NOT NULL),
    CHECK (started_at IS NULL OR started_at >= created_at),
    CHECK (finished_at IS NULL OR finished_at >= started_at),
    CHECK (
        (state = 'running' AND worker_id IS NOT NULL AND started_at IS NOT NULL)
        OR
        (state <> 'running')
    ),
    CHECK (
        state NOT IN ('completed', 'failed', 'cancelled')
        OR finished_at IS NOT NULL
    )
);

CREATE TABLE job_events (
    event_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    job_id BIGINT NOT NULL REFERENCES jobs(job_id),
    event_type TEXT NOT NULL,
    event_time TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    detail JSONB NOT NULL DEFAULT '{}'::jsonb,
    CHECK (length(trim(event_type)) > 0)
);

-- The index supports dispatch order. Partial indexing avoids scanning
-- completed jobs when finding the next eligible job.
CREATE INDEX jobs_dispatch_order_idx
    ON jobs (priority DESC, queued_at ASC, job_id ASC)
    WHERE state = 'queued';

CREATE INDEX jobs_repository_state_idx
    ON jobs (repository_name, state, created_at DESC);

CREATE INDEX job_events_job_time_idx
    ON job_events (job_id, event_time DESC);

CREATE INDEX jobs_running_worker_idx
    ON jobs (worker_id)
    WHERE state = 'running';

CREATE FUNCTION record_job_event()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO job_events (job_id, event_type, detail)
        VALUES (
            NEW.job_id,
            'created',
            jsonb_build_object(
                'priority', NEW.priority,
                'kind', NEW.kind,
                'state', NEW.state
            )
        );
        RETURN NEW;
    END IF;

    IF OLD.priority IS DISTINCT FROM NEW.priority THEN
        INSERT INTO job_events (job_id, event_type, detail)
        VALUES (
            NEW.job_id,
            'reprioritized',
            jsonb_build_object(
                'old_priority', OLD.priority,
                'new_priority', NEW.priority
            )
        );
    END IF;

    IF OLD.state IS DISTINCT FROM NEW.state THEN
        INSERT INTO job_events (job_id, event_type, detail)
        VALUES (
            NEW.job_id,
            'state_changed',
            jsonb_build_object(
                'from', OLD.state,
                'to', NEW.state
            )
        );
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER jobs_record_events
AFTER INSERT OR UPDATE OF priority, state ON jobs
FOR EACH ROW
EXECUTE FUNCTION record_job_event();

INSERT INTO workers (worker_name) VALUES
    ('build-worker-a'),
    ('build-worker-b'),
    ('security-worker');

INSERT INTO jobs (
    external_key, repository_name, kind, description,
    priority, estimated_seconds
) VALUES
    (
        'BUILD-401', 'payments-api', 'compile',
        'Compile release candidate', 50, 40
    ),
    (
        'TEST-402', 'payments-api', 'integration_test',
        'Run payment integration tests', 70, 80
    ),
    (
        'SEC-403', 'identity-service', 'security_scan',
        'Scan authentication dependencies', 95, 35
    ),
    (
        'DEPLOY-404', 'payments-api', 'deployment',
        'Deploy approved production release', 85, 25
    ),
    (
        'REPORT-405', 'analytics-service', 'report',
        'Generate weekly analytics report', 20, 15
    );

-- Increase urgency without changing the job's identity or creation history.
UPDATE jobs
SET priority = 90
WHERE external_key = 'BUILD-401'
  AND state = 'queued';

-- This view calculates queue rank at query time. It is not a stored rank:
-- a new job or priority change can alter every later row's position.
CREATE VIEW queued_job_order AS
SELECT
    job_id,
    external_key,
    repository_name,
    kind,
    priority,
    queued_at,
    row_number() OVER (
        ORDER BY priority DESC, queued_at ASC, job_id ASC
    ) AS dispatch_rank
FROM jobs
WHERE state = 'queued';

SELECT *
FROM queued_job_order
ORDER BY dispatch_rank;

-- Top-priority selection without claiming work.
SELECT external_key, priority, description
FROM jobs
WHERE state = 'queued'
ORDER BY priority DESC, queued_at ASC, job_id ASC
LIMIT 3;

-- Atomic claim operation. SKIP LOCKED allows concurrent workers to claim
-- different jobs rather than blocking on the same highest-priority row.
CREATE FUNCTION claim_next_job(p_worker_id BIGINT)
RETURNS TABLE (
    claimed_job_id BIGINT,
    claimed_external_key TEXT,
    claimed_priority SMALLINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    selected_job jobs%ROWTYPE;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM workers
        WHERE worker_id = p_worker_id AND enabled
    ) THEN
        RAISE EXCEPTION 'Worker % is missing or disabled', p_worker_id;
    END IF;

    SELECT j.*
    INTO selected_job
    FROM jobs AS j
    WHERE j.state = 'queued'
      AND j.attempts < j.max_attempts
    ORDER BY j.priority DESC, j.queued_at ASC, j.job_id ASC
    FOR UPDATE SKIP LOCKED
    LIMIT 1;

    IF NOT FOUND THEN
        RETURN;
    END IF;

    UPDATE jobs AS j
    SET state = 'running',
        worker_id = p_worker_id,
        started_at = clock_timestamp(),
        finished_at = NULL,
        attempts = j.attempts + 1
    WHERE j.job_id = selected_job.job_id;

    RETURN QUERY
    SELECT j.job_id, j.external_key, j.priority
    FROM jobs AS j
    WHERE j.job_id = selected_job.job_id;
END;
$$;

-- Claim the most urgent job. The function's update and event trigger execute
-- within the caller's transaction.
SELECT * FROM claim_next_job(
    (SELECT worker_id FROM workers WHERE worker_name = 'security-worker')
);

-- Complete the job claimed by the security worker.
UPDATE jobs
SET state = 'completed',
    finished_at = clock_timestamp()
WHERE worker_id = (
    SELECT worker_id
    FROM workers
    WHERE worker_name = 'security-worker'
)
AND state = 'running';

-- Show live workload, queue duration, and worker assignment.
SELECT
    repository_name,
    count(*) FILTER (WHERE state = 'queued') AS queued_jobs,
    count(*) FILTER (WHERE state = 'running') AS running_jobs,
    count(*) FILTER (WHERE state = 'completed') AS completed_jobs,
    max(priority) FILTER (WHERE state = 'queued') AS highest_waiting_priority
FROM jobs
GROUP BY repository_name
ORDER BY repository_name;

-- Repeated reprioritization is recorded as events, enabling an audit trail.
SELECT
    j.external_key,
    e.event_type,
    e.event_time,
    e.detail
FROM job_events AS e
JOIN jobs AS j USING (job_id)
ORDER BY e.event_time, e.event_id;

-- Demonstrate rollback of a failed admission. The savepoint keeps the main
-- sample workflow usable while exposing the constraint failure.
SAVEPOINT invalid_priority_demo;

DO $$
BEGIN
    BEGIN
        INSERT INTO jobs (
            external_key, repository_name, kind, description, priority
        ) VALUES (
            'INVALID-406', 'payments-api', 'compile',
            'Invalid priority must be rejected', 101
        );
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'Rejected invalid priority through CHECK constraint';
    END;
END;
$$;

ROLLBACK TO SAVEPOINT invalid_priority_demo;
RELEASE SAVEPOINT invalid_priority_demo;

-- A second claim demonstrates that terminal jobs are excluded from dispatch.
SELECT *
FROM claim_next_job(
    (SELECT worker_id FROM workers WHERE worker_name = 'build-worker-a')
);

SELECT
    external_key,
    priority,
    state,
    attempts,
    worker_id,
    started_at,
    finished_at
FROM jobs
ORDER BY priority DESC, queued_at, job_id;

COMMIT;
