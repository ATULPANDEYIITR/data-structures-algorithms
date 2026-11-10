/*
 * HEAP INTRODUCTION
 *
 * PostgreSQL implementation of an array-based binary heap,
 * heap operations, priority queues, tree representation,
 * validation, sorting, and operational reporting.
 *
 * Target: PostgreSQL 14+
 *
 * The implementation uses:
 * - PostgreSQL arrays for heap storage
 * - PL/pgSQL for heap algorithms
 * - Relational tables for persistent priority queues
 * - Constraints and indexes for data integrity
 * - Transactions for safe task processing
 */

BEGIN;

CREATE SCHEMA IF NOT EXISTS heap_lab;

SET search_path TO heap_lab, public;


-- =========================================================
-- 1. DOMAIN TYPES
-- =========================================================

CREATE TYPE heap_type AS ENUM (
    'min',
    'max'
);

CREATE TYPE task_status AS ENUM (
    'pending',
    'processing',
    'completed',
    'failed',
    'cancelled'
);


-- =========================================================
-- 2. HEAP ARRAY IMPLEMENTATION
-- =========================================================

CREATE TABLE heap_instances (
    heap_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    heap_name VARCHAR(100) NOT NULL UNIQUE,

    heap_kind heap_type NOT NULL,

    elements INTEGER[] NOT NULL DEFAULT '{}',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_heap_name
        CHECK (length(trim(heap_name)) > 0),

    CONSTRAINT valid_heap_elements
        CHECK (array_ndims(elements) IS NULL OR array_ndims(elements) = 1),

    CONSTRAINT one_based_heap_array
        CHECK (
            cardinality(elements) = 0
            OR array_lower(elements, 1) = 1
        )
);


-- =========================================================
-- 3. COMPLETE BINARY TREE INDEX CALCULATIONS
-- =========================================================

CREATE FUNCTION parent_index(node_index INTEGER)
RETURNS INTEGER
LANGUAGE SQL
IMMUTABLE
STRICT
AS $$
    SELECT CASE
        WHEN node_index <= 1 THEN NULL
        ELSE (node_index - 1) / 2
    END;
$$;


CREATE FUNCTION left_child_index(node_index INTEGER)
RETURNS INTEGER
LANGUAGE SQL
IMMUTABLE
STRICT
AS $$
    SELECT 2 * node_index;
$$;


CREATE FUNCTION right_child_index(node_index INTEGER)
RETURNS INTEGER
LANGUAGE SQL
IMMUTABLE
STRICT
AS $$
    SELECT 2 * node_index + 1;
$$;


CREATE FUNCTION heap_has_higher_priority(
    first_value INTEGER,
    second_value INTEGER,
    kind heap_type
)
RETURNS BOOLEAN
LANGUAGE SQL
IMMUTABLE
STRICT
AS $$
    SELECT CASE
        WHEN kind = 'min' THEN first_value < second_value
        ELSE first_value > second_value
    END;
$$;


-- =========================================================
-- 4. HEAP VALIDATION
-- =========================================================

CREATE FUNCTION validate_heap(
    input_elements INTEGER[],
    kind heap_type
)
RETURNS BOOLEAN
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    i INTEGER;
    n INTEGER;
BEGIN
    IF input_elements IS NULL OR kind IS NULL THEN
        RETURN FALSE;
    END IF;

    IF array_ndims(input_elements) IS NOT NULL
       AND array_ndims(input_elements) <> 1 THEN
        RETURN FALSE;
    END IF;

    IF cardinality(input_elements) = 0 THEN
        RETURN TRUE;
    END IF;

    IF array_lower(input_elements, 1) <> 1 THEN
        RETURN FALSE;
    END IF;

    n := cardinality(input_elements);

    FOR i IN 2..n LOOP
        IF heap_has_higher_priority(
            input_elements[i],
            input_elements[parent_index(i)],
            kind
        ) THEN
            RETURN FALSE;
        END IF;
    END LOOP;

    RETURN TRUE;
END;
$$;


-- =========================================================
-- 5. INSERTION OPERATION
-- =========================================================

CREATE FUNCTION heap_push(
    input_elements INTEGER[],
    new_value INTEGER,
    kind heap_type
)
RETURNS INTEGER[]
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    result INTEGER[];
    current_index INTEGER;
    parent_position INTEGER;
    temporary INTEGER;
BEGIN
    IF input_elements IS NULL OR kind IS NULL THEN
        RAISE EXCEPTION 'Heap and heap type cannot be NULL';
    END IF;

    IF array_ndims(input_elements) IS NOT NULL
       AND array_ndims(input_elements) <> 1 THEN
        RAISE EXCEPTION 'Heap must be a one-dimensional array';
    END IF;

    IF cardinality(input_elements) > 0
       AND array_lower(input_elements, 1) <> 1 THEN
        RAISE EXCEPTION 'Heap array must use a one-based index';
    END IF;

    IF NOT validate_heap(input_elements, kind) THEN
        RAISE EXCEPTION 'Input does not satisfy heap property';
    END IF;

    result := input_elements || ARRAY[new_value];

    current_index := cardinality(result);

    WHILE current_index > 1 LOOP
        parent_position := parent_index(current_index);

        IF NOT heap_has_higher_priority(
            result[current_index],
            result[parent_position],
            kind
        ) THEN
            EXIT;
        END IF;

        temporary := result[current_index];
        result[current_index] := result[parent_position];
        result[parent_position] := temporary;

        current_index := parent_position;
    END LOOP;

    RETURN result;
END;
$$;


-- =========================================================
-- 6. ROOT EXTRACTION
-- =========================================================

CREATE FUNCTION heap_pop(
    input_elements INTEGER[],
    kind heap_type
)
RETURNS TABLE (
    removed_value INTEGER,
    remaining_elements INTEGER[]
)
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    result INTEGER[];
    n INTEGER;
    current_index INTEGER := 1;
    best_index INTEGER;
    left_position INTEGER;
    right_position INTEGER;
    temporary INTEGER;
BEGIN
    IF input_elements IS NULL OR kind IS NULL THEN
        RAISE EXCEPTION 'Heap and heap type cannot be NULL';
    END IF;

    IF NOT validate_heap(input_elements, kind) THEN
        RAISE EXCEPTION 'Input heap is invalid';
    END IF;

    n := cardinality(input_elements);

    IF n = 0 THEN
        RAISE EXCEPTION 'Cannot extract from an empty heap';
    END IF;

    removed_value := input_elements[1];

    IF n = 1 THEN
        remaining_elements := ARRAY[]::INTEGER[];
        RETURN NEXT;
        RETURN;
    END IF;

    result := input_elements;
    result[1] := result[n];
    result := result[1:n - 1];

    n := cardinality(result);

    LOOP
        best_index := current_index;

        left_position := left_child_index(current_index);
        right_position := right_child_index(current_index);

        IF left_position <= n THEN
            IF heap_has_higher_priority(
                result[left_position],
                result[best_index],
                kind
            ) THEN
                best_index := left_position;
            END IF;
        END IF;

        IF right_position <= n THEN
            IF heap_has_higher_priority(
                result[right_position],
                result[best_index],
                kind
            ) THEN
                best_index := right_position;
            END IF;
        END IF;

        IF best_index = current_index THEN
            EXIT;
        END IF;

        temporary := result[current_index];
        result[current_index] := result[best_index];
        result[best_index] := temporary;

        current_index := best_index;
    END LOOP;

    remaining_elements := result;

    RETURN NEXT;
END;
$$;


-- =========================================================
-- 7. BOTTOM-UP HEAP CONSTRUCTION
-- =========================================================

CREATE FUNCTION build_heap(
    input_values INTEGER[],
    kind heap_type
)
RETURNS INTEGER[]
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    result INTEGER[];
    n INTEGER;
    current_index INTEGER;
    best_index INTEGER;
    left_position INTEGER;
    right_position INTEGER;
    temporary INTEGER;
BEGIN
    IF input_values IS NULL OR kind IS NULL THEN
        RAISE EXCEPTION 'Input and heap type cannot be NULL';
    END IF;

    IF array_ndims(input_values) IS NOT NULL
       AND array_ndims(input_values) <> 1 THEN
        RAISE EXCEPTION 'Input must be one-dimensional';
    END IF;

    IF cardinality(input_values) > 0
       AND array_lower(input_values, 1) <> 1 THEN
        RAISE EXCEPTION 'Input array must be one-based';
    END IF;

    result := input_values;
    n := cardinality(result);

    FOR current_index IN REVERSE (n / 2)..1 LOOP

        DECLARE
            position INTEGER := current_index;
        BEGIN
            LOOP
                best_index := position;

                left_position := left_child_index(position);
                right_position := right_child_index(position);

                IF left_position <= n THEN
                    IF heap_has_higher_priority(
                        result[left_position],
                        result[best_index],
                        kind
                    ) THEN
                        best_index := left_position;
                    END IF;
                END IF;

                IF right_position <= n THEN
                    IF heap_has_higher_priority(
                        result[right_position],
                        result[best_index],
                        kind
                    ) THEN
                        best_index := right_position;
                    END IF;
                END IF;

                IF best_index = position THEN
                    EXIT;
                END IF;

                temporary := result[position];
                result[position] := result[best_index];
                result[best_index] := temporary;

                position := best_index;
            END LOOP;
        END;
    END LOOP;

    RETURN result;
END;
$$;


-- =========================================================
-- 8. TREE REPRESENTATION VIEW
-- =========================================================

CREATE VIEW heap_tree_view AS
SELECT
    h.heap_id,
    h.heap_name,
    h.heap_kind,
    i.node_index,
    h.elements[i.node_index] AS node_value,

    CASE
        WHEN i.node_index = 1 THEN NULL
        ELSE parent_index(i.node_index)
    END AS parent_index,

    CASE
        WHEN left_child_index(i.node_index)
            <= cardinality(h.elements)
        THEN left_child_index(i.node_index)
        ELSE NULL
    END AS left_child_index,

    CASE
        WHEN right_child_index(i.node_index)
            <= cardinality(h.elements)
        THEN right_child_index(i.node_index)
        ELSE NULL
    END AS right_child_index,

    floor(log(2, i.node_index))::INTEGER AS tree_level

FROM heap_instances h
CROSS JOIN LATERAL generate_series(
    1,
    cardinality(h.elements)
) AS i(node_index);


-- =========================================================
-- 9. REPOSITORY JOB MANAGEMENT
-- =========================================================

CREATE TABLE repository_jobs (
    job_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    repository_name VARCHAR(150) NOT NULL,

    operation VARCHAR(100) NOT NULL,

    priority SMALLINT NOT NULL,

    status task_status NOT NULL DEFAULT 'pending',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    started_at TIMESTAMPTZ,

    completed_at TIMESTAMPTZ,

    failure_reason TEXT,

    CONSTRAINT valid_repository_name
        CHECK (length(trim(repository_name)) > 0),

    CONSTRAINT valid_operation
        CHECK (length(trim(operation)) > 0),

    CONSTRAINT valid_priority
        CHECK (priority BETWEEN 1 AND 10),

    CONSTRAINT valid_job_timestamps
        CHECK (
            (started_at IS NULL OR started_at >= created_at)
            AND
            (completed_at IS NULL OR started_at IS NOT NULL)
            AND
            (completed_at IS NULL OR completed_at >= started_at)
        ),

    CONSTRAINT valid_failure_reason
        CHECK (
            status <> 'failed'
            OR failure_reason IS NOT NULL
        )
);


-- Pending jobs are retrieved by priority and insertion order.
CREATE INDEX idx_pending_repository_jobs
ON repository_jobs (
    priority ASC,
    created_at ASC,
    job_id ASC
)
WHERE status = 'pending';


CREATE INDEX idx_repository_job_history
ON repository_jobs (
    repository_name,
    created_at DESC
);


-- =========================================================
-- 10. JOB PROCESSING FUNCTION
-- =========================================================

CREATE FUNCTION process_next_job()
RETURNS TABLE (
    processed_job_id BIGINT,
    processed_repository VARCHAR(150),
    processed_operation VARCHAR(100),
    processed_priority SMALLINT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    WITH selected_job AS (
        SELECT j.job_id
        FROM repository_jobs j
        WHERE j.status = 'pending'
        ORDER BY
            j.priority ASC,
            j.created_at ASC,
            j.job_id ASC
        LIMIT 1
        FOR UPDATE SKIP LOCKED
    ),
    updated_job AS (
        UPDATE repository_jobs j
        SET
            status = 'processing',
            started_at = CURRENT_TIMESTAMP
        FROM selected_job s
        WHERE j.job_id = s.job_id
        RETURNING
            j.job_id,
            j.repository_name,
            j.operation,
            j.priority
    )
    SELECT
        u.job_id,
        u.repository_name,
        u.operation,
        u.priority
    FROM updated_job u;
END;
$$;


-- =========================================================
-- 11. JOB COMPLETION PROCEDURE
-- =========================================================

CREATE PROCEDURE complete_repository_job(
    input_job_id BIGINT,
    success BOOLEAN,
    error_message TEXT DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    current_status task_status;
BEGIN
    SELECT status
    INTO current_status
    FROM repository_jobs
    WHERE job_id = input_job_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Job % does not exist', input_job_id;
    END IF;

    IF current_status <> 'processing' THEN
        RAISE EXCEPTION
            'Job % is not processing; current status is %',
            input_job_id,
            current_status;
    END IF;

    IF success THEN
        UPDATE repository_jobs
        SET
            status = 'completed',
            completed_at = CURRENT_TIMESTAMP,
            failure_reason = NULL
        WHERE job_id = input_job_id;
    ELSE
        IF error_message IS NULL OR length(trim(error_message)) = 0 THEN
            RAISE EXCEPTION 'Failure reason is required';
        END IF;

        UPDATE repository_jobs
        SET
            status = 'failed',
            completed_at = CURRENT_TIMESTAMP,
            failure_reason = error_message
        WHERE job_id = input_job_id;
    END IF;
END;
$$;


-- =========================================================
-- 12. AUDIT TRIGGER
-- =========================================================

CREATE TABLE repository_job_audit (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    job_id BIGINT NOT NULL,

    old_status task_status,

    new_status task_status NOT NULL,

    changed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE FUNCTION audit_repository_job_status()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        INSERT INTO repository_job_audit (
            job_id,
            old_status,
            new_status
        )
        VALUES (
            NEW.job_id,
            OLD.status,
            NEW.status
        );
    END IF;

    RETURN NEW;
END;
$$;


CREATE TRIGGER trg_repository_job_audit
AFTER UPDATE ON repository_jobs
FOR EACH ROW
EXECUTE FUNCTION audit_repository_job_status();


-- =========================================================
-- 13. REPORTING VIEWS
-- =========================================================

CREATE VIEW repository_job_summary AS
SELECT
    repository_name,
    COUNT(*) AS total_jobs,

    COUNT(*) FILTER (
        WHERE status = 'pending'
    ) AS pending_jobs,

    COUNT(*) FILTER (
        WHERE status = 'processing'
    ) AS processing_jobs,

    COUNT(*) FILTER (
        WHERE status = 'completed'
    ) AS completed_jobs,

    COUNT(*) FILTER (
        WHERE status = 'failed'
    ) AS failed_jobs,

    ROUND(AVG(priority), 2) AS average_priority

FROM repository_jobs
GROUP BY repository_name;


-- =========================================================
-- 14. SAMPLE HEAPS
-- =========================================================

INSERT INTO heap_instances (
    heap_name,
    heap_kind,
    elements
)
VALUES
(
    'development_min_heap',
    'min',
    build_heap(ARRAY[40, 10, 30, 50, 20, 60, 70], 'min')
),
(
    'development_max_heap',
    'max',
    build_heap(ARRAY[40, 10, 30, 50, 20, 60, 70], 'max')
),
(
    'empty_min_heap',
    'min',
    ARRAY[]::INTEGER[]
);


-- =========================================================
-- 15. SAMPLE REPOSITORY JOBS
-- =========================================================

INSERT INTO repository_jobs (
    repository_name,
    operation,
    priority,
    status
)
VALUES
(
    'portfolio-api',
    'Run automated tests',
    3,
    'pending'
),
(
    'security-engine',
    'Execute security audit',
    1,
    'pending'
),
(
    'market-service',
    'Generate analytics report',
    7,
    'pending'
),
(
    'portfolio-api',
    'Investigate production incident',
    1,
    'pending'
),
(
    'log-service',
    'Completed database backup',
    5,
    'completed'
),
(
    'security-engine',
    'Previous failed deployment',
    2,
    'failed'
);


-- =========================================================
-- 16. TREE RETRIEVAL
-- =========================================================

SELECT *
FROM heap_tree_view
ORDER BY heap_id, node_index;


-- =========================================================
-- 17. HEAP VALIDATION REPORT
-- =========================================================

SELECT
    heap_name,
    heap_kind,
    elements,
    validate_heap(elements, heap_kind) AS is_valid,
    cardinality(elements) AS element_count
FROM heap_instances
ORDER BY heap_id;


-- =========================================================
-- 18. INSERTION AND EXTRACTION
-- =========================================================

UPDATE heap_instances
SET
    elements = heap_push(
        elements,
        5,
        heap_kind
    ),
    updated_at = CURRENT_TIMESTAMP
WHERE heap_name = 'development_min_heap';


SELECT
    heap_name,
    elements,
    validate_heap(elements, heap_kind) AS is_valid
FROM heap_instances
WHERE heap_name = 'development_min_heap';


-- Extract the minimum from a copied heap without modifying
-- the persistent heap record.
SELECT *
FROM heap_pop(
    ARRAY[1, 10, 5, 20, 30]::INTEGER[],
    'min'
);


-- =========================================================
-- 19. PRIORITY QUEUE RETRIEVAL
-- =========================================================

SELECT
    job_id,
    repository_name,
    operation,
    priority,
    status,
    created_at
FROM repository_jobs
WHERE status = 'pending'
ORDER BY
    priority ASC,
    created_at ASC,
    job_id ASC;


-- =========================================================
-- 20. AGGREGATION AND REPORTING
-- =========================================================

SELECT *
FROM repository_job_summary
ORDER BY repository_name;


SELECT
    priority,
    COUNT(*) AS total_jobs,
    COUNT(*) FILTER (
        WHERE status = 'pending'
    ) AS pending_jobs
FROM repository_jobs
GROUP BY priority
ORDER BY priority;


-- =========================================================
-- 21. TRANSACTIONAL JOB PROCESSING
-- =========================================================

BEGIN;

SELECT *
FROM process_next_job();

-- The returned job is marked processing.
-- The caller can complete it using its returned job_id.

COMMIT;


-- =========================================================
-- 22. COMPLETE A SAMPLE PROCESSING JOB
-- =========================================================

-- Complete the oldest job that is currently processing.
DO $$
DECLARE
    selected_id BIGINT;
BEGIN
    SELECT job_id
    INTO selected_id
    FROM repository_jobs
    WHERE status = 'processing'
    ORDER BY started_at, job_id
    LIMIT 1;

    IF selected_id IS NOT NULL THEN
        CALL complete_repository_job(
            selected_id,
            TRUE,
            NULL
        );
    END IF;
END;
$$;


-- =========================================================
-- 23. FAILURE HANDLING DEMONSTRATION
-- =========================================================

-- A failed task must have a failure reason.
DO $$
BEGIN
    BEGIN
        INSERT INTO repository_jobs (
            repository_name,
            operation,
            priority,
            status
        )
        VALUES (
            'security-engine',
            'Invalid priority demonstration',
            20,
            'pending'
        );

    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'Expected validation failure: invalid priority';
    END;
END;
$$;


-- =========================================================
-- 24. AUDIT REPORT
-- =========================================================

SELECT
    audit_id,
    job_id,
    old_status,
    new_status,
    changed_at
FROM repository_job_audit
ORDER BY audit_id;


-- =========================================================
-- 25. PRIORITY QUEUE ELIGIBILITY REPORT
-- =========================================================

SELECT
    job_id,
    repository_name,
    operation,
    priority,

    CASE
        WHEN status = 'pending' THEN TRUE
        ELSE FALSE
    END AS eligible_for_execution,

    CASE
        WHEN status = 'pending' THEN
            'Ready for priority queue'
        WHEN status = 'processing' THEN
            'Already being processed'
        WHEN status = 'completed' THEN
            'Already completed'
        WHEN status = 'failed' THEN
            'Requires failure investigation'
        ELSE
            'Cancelled'
    END AS eligibility_reason

FROM repository_jobs
ORDER BY priority, created_at, job_id;


-- =========================================================
-- 26. FINAL INTEGRITY CHECKS
-- =========================================================

DO $$
DECLARE
    invalid_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO invalid_count
    FROM heap_instances
    WHERE NOT validate_heap(elements, heap_kind);

    IF invalid_count > 0 THEN
        RAISE EXCEPTION
            'Heap integrity check failed for % records',
            invalid_count;
    END IF;

    RAISE NOTICE 'All stored heaps satisfy their heap properties';
END;
$$;


COMMIT;

-- Production considerations:
-- 1. Use FOR UPDATE SKIP LOCKED for concurrent workers.
-- 2. Keep task processing idempotent.
-- 3. Add retry limits and dead-letter handling for failures.
-- 4. Restrict function execution privileges by role.
-- 5. Monitor queue depth and processing duration.
-- 6. The array-backed heap is suitable for educational and
--    bounded datasets. Large concurrent queues should use
--    relational priority ordering and transactional locking.
