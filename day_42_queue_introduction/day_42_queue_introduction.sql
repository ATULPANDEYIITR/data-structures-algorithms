-- Queue Introduction
-- PostgreSQL-compatible relational model.
--
-- The database represents a service-request queue. Arrival order is preserved
-- through an explicit sequence number, while constraints prevent invalid
-- states such as duplicate active requests or illegal queue positions.

DROP SCHEMA IF EXISTS queue_learning CASCADE;

CREATE SCHEMA queue_learning;

SET search_path TO queue_learning;

-- ---------------------------------------------------------------------------
-- Core entities
-- ---------------------------------------------------------------------------

CREATE TABLE service_queue (
    queue_id BIGSERIAL PRIMARY KEY,
    queue_name VARCHAR(100) NOT NULL UNIQUE,
    capacity INTEGER NOT NULL CHECK (capacity > 0)
);

CREATE TABLE service_request (
    request_id BIGSERIAL PRIMARY KEY,
    queue_id BIGINT NOT NULL
        REFERENCES service_queue(queue_id),
    request_code VARCHAR(40) NOT NULL UNIQUE,
    requester VARCHAR(120) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(20) NOT NULL
        CHECK (status IN ('QUEUED', 'PROCESSING', 'COMPLETED', 'FAILED')),
    arrival_sequence BIGINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMPTZ,
    CONSTRAINT request_arrival_sequence_positive
        CHECK (arrival_sequence > 0),
    CONSTRAINT request_completion_time_valid
        CHECK (
            processed_at IS NULL
            OR processed_at >= created_at
        ),
    CONSTRAINT unique_queue_arrival_sequence
        UNIQUE (queue_id, arrival_sequence)
);

-- Only one request should normally be actively processed by a simple FIFO
-- worker for a given queue.
CREATE UNIQUE INDEX one_processing_request_per_queue
ON service_request(queue_id)
WHERE status = 'PROCESSING';

-- This index supports the fundamental FIFO operation: find the oldest
-- queued request for a specific queue.
CREATE INDEX queued_request_fifo_index
ON service_request(queue_id, arrival_sequence)
WHERE status = 'QUEUED';

-- ---------------------------------------------------------------------------
-- Sample queues
-- ---------------------------------------------------------------------------

INSERT INTO service_queue (queue_name, capacity)
VALUES
    ('Customer Support', 100),
    ('Internal Operations', 50);

-- ---------------------------------------------------------------------------
-- Sample FIFO requests
-- ---------------------------------------------------------------------------

INSERT INTO service_request (
    queue_id,
    request_code,
    requester,
    description,
    status,
    arrival_sequence
)
VALUES
    (
        1,
        'SUP-1001',
        'Asha',
        'Payroll access is unavailable',
        'QUEUED',
        1
    ),
    (
        1,
        'SUP-1002',
        'Rahul',
        'Monthly report export fails',
        'QUEUED',
        2
    ),
    (
        1,
        'SUP-1003',
        'Meera',
        'Password reset request',
        'QUEUED',
        3
    ),
    (
        2,
        'OPS-2001',
        'Finance',
        'Daily reconciliation file is delayed',
        'QUEUED',
        1
    ),
    (
        2,
        'OPS-2002',
        'HR',
        'Employee data synchronization failed',
        'QUEUED',
        2
    );

-- ---------------------------------------------------------------------------
-- Inspect queue state
-- ---------------------------------------------------------------------------

SELECT
    q.queue_name,
    r.request_code,
    r.requester,
    r.status,
    r.arrival_sequence
FROM service_request AS r
JOIN service_queue AS q
    ON q.queue_id = r.queue_id
WHERE r.status = 'QUEUED'
ORDER BY q.queue_id, r.arrival_sequence;

-- The oldest queued request is the FIFO front.
SELECT
    r.request_id,
    r.request_code,
    r.requester,
    r.description,
    r.arrival_sequence
FROM service_request AS r
WHERE r.queue_id = 1
  AND r.status = 'QUEUED'
ORDER BY r.arrival_sequence
LIMIT 1;

-- ---------------------------------------------------------------------------
-- Queue position calculation
-- ---------------------------------------------------------------------------

SELECT
    r.request_code,
    r.arrival_sequence,
    ROW_NUMBER() OVER (
        PARTITION BY r.queue_id
        ORDER BY r.arrival_sequence
    ) AS current_queue_position
FROM service_request AS r
WHERE r.queue_id = 1
  AND r.status = 'QUEUED'
ORDER BY r.arrival_sequence;

-- ---------------------------------------------------------------------------
-- Transactional dequeue/start operation
-- ---------------------------------------------------------------------------
--
-- FOR UPDATE locks the selected row during the transaction. This matters when
-- multiple workers might attempt to take the same FIFO item concurrently.

BEGIN;

WITH next_request AS (
    SELECT request_id
    FROM service_request
    WHERE queue_id = 1
      AND status = 'QUEUED'
    ORDER BY arrival_sequence
    LIMIT 1
    FOR UPDATE SKIP LOCKED
)
UPDATE service_request AS r
SET
    status = 'PROCESSING'
FROM next_request
WHERE r.request_id = next_request.request_id
RETURNING
    r.request_id,
    r.request_code,
    r.status,
    r.arrival_sequence;

COMMIT;

-- ---------------------------------------------------------------------------
-- Complete the currently processing request
-- ---------------------------------------------------------------------------

UPDATE service_request
SET
    status = 'COMPLETED',
    processed_at = CURRENT_TIMESTAMP
WHERE queue_id = 1
  AND status = 'PROCESSING'
RETURNING
    request_code,
    status,
    processed_at;

-- ---------------------------------------------------------------------------
-- Queue capacity inspection
-- ---------------------------------------------------------------------------

SELECT
    q.queue_name,
    q.capacity,
    COUNT(r.request_id) FILTER (
        WHERE r.status IN ('QUEUED', 'PROCESSING')
    ) AS active_requests,
    q.capacity - COUNT(r.request_id) FILTER (
        WHERE r.status IN ('QUEUED', 'PROCESSING')
    ) AS remaining_capacity
FROM service_queue AS q
LEFT JOIN service_request AS r
    ON r.queue_id = q.queue_id
GROUP BY q.queue_id, q.queue_name, q.capacity
ORDER BY q.queue_id;

-- ---------------------------------------------------------------------------
-- Invalid-state demonstrations
-- ---------------------------------------------------------------------------
--
-- These statements are intentionally disabled. They illustrate constraints
-- without causing the complete script to fail.
--
-- Duplicate arrival sequence in the same queue:
-- INSERT INTO service_request (
--     queue_id, request_code, requester, description, status, arrival_sequence
-- )
-- VALUES (1, 'SUP-BAD-1', 'Test', 'Invalid duplicate sequence',
--         'QUEUED', 3);
--
-- Invalid status:
-- INSERT INTO service_request (
--     queue_id, request_code, requester, description, status, arrival_sequence
-- )
-- VALUES (1, 'SUP-BAD-2', 'Test', 'Invalid status',
--         'WAITING', 4);
--
-- Invalid negative sequence:
-- INSERT INTO service_request (
--     queue_id, request_code, requester, description, status, arrival_sequence
-- )
-- VALUES (1, 'SUP-BAD-3', 'Test', 'Invalid sequence',
--         'QUEUED', -1);

-- ---------------------------------------------------------------------------
-- Queue view
-- ---------------------------------------------------------------------------

CREATE OR REPLACE VIEW active_queue AS
SELECT
    q.queue_name,
    r.request_code,
    r.requester,
    r.description,
    r.status,
    r.arrival_sequence,
    ROW_NUMBER() OVER (
        PARTITION BY r.queue_id
        ORDER BY r.arrival_sequence
    ) AS queue_position
FROM service_request AS r
JOIN service_queue AS q
    ON q.queue_id = r.queue_id
WHERE r.status IN ('QUEUED', 'PROCESSING');

SELECT *
FROM active_queue
ORDER BY queue_name, queue_position;

-- ---------------------------------------------------------------------------
-- Queue statistics
-- ---------------------------------------------------------------------------

SELECT
    q.queue_name,
    COUNT(*) FILTER (WHERE r.status = 'QUEUED') AS waiting,
    COUNT(*) FILTER (WHERE r.status = 'PROCESSING') AS processing,
    COUNT(*) FILTER (WHERE r.status = 'COMPLETED') AS completed,
    COUNT(*) FILTER (WHERE r.status = 'FAILED') AS failed
FROM service_queue AS q
LEFT JOIN service_request AS r
    ON r.queue_id = q.queue_id
GROUP BY q.queue_id, q.queue_name
ORDER BY q.queue_id;
