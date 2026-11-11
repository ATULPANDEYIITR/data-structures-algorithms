-- ============================================================
-- HEAP OPERATIONS AND PRIORITY QUEUE MANAGEMENT
-- PostgreSQL 15+
--
-- Models:
--   Binary heaps
--   Min-heap and max-heap operations
--   Heapify and extraction
--   Indexed deletion and priority updates
--   Priority scheduling
--   Stable task ordering
--   Transactional queue processing
--   Execution history and reporting
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS heap_lab;

SET search_path TO heap_lab, public;

-- ------------------------------------------------------------
-- 1. Domain types
-- ------------------------------------------------------------

CREATE TYPE heap_mode AS ENUM ('MIN', 'MAX');

CREATE TYPE task_status AS ENUM (
    'QUEUED',
    'PROCESSING',
    'COMPLETED',
    'FAILED'
);

-- ------------------------------------------------------------
-- 2. Binary heap storage
-- ------------------------------------------------------------

CREATE TABLE heaps (
    heap_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    heap_name VARCHAR(100) NOT NULL UNIQUE,
    mode heap_mode NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE heap_nodes (
    heap_id BIGINT NOT NULL
        REFERENCES heaps(heap_id) ON DELETE CASCADE,
    position INTEGER NOT NULL CHECK (position >= 0),
    value BIGINT NOT NULL,
    PRIMARY KEY (heap_id, position)
);

CREATE INDEX idx_heap_nodes_value
ON heap_nodes(heap_id, value);

-- ------------------------------------------------------------
-- 3. Priority queue tables
-- ------------------------------------------------------------

CREATE TABLE scheduled_tasks (
    task_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    external_key VARCHAR(100) NOT NULL UNIQUE,
    description TEXT NOT NULL CHECK (
        length(trim(description)) > 0
    ),
    priority INTEGER NOT NULL,
    status task_status NOT NULL DEFAULT 'QUEUED',
    sequence_number BIGINT GENERATED ALWAYS AS IDENTITY UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    failure_reason TEXT,

    CHECK (
        completed_at IS NULL OR started_at IS NOT NULL
    ),

    CHECK (
        status <> 'COMPLETED' OR completed_at IS NOT NULL
    ),

    CHECK (
        status <> 'FAILED' OR failure_reason IS NOT NULL
    )
);

CREATE INDEX idx_scheduled_tasks_queue
ON scheduled_tasks (
    priority DESC,
    sequence_number ASC
)
WHERE status = 'QUEUED';

CREATE INDEX idx_scheduled_tasks_status
ON scheduled_tasks(status, created_at);

CREATE TABLE task_execution_history (
    history_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    task_id BIGINT NOT NULL
        REFERENCES scheduled_tasks(task_id),
    previous_status task_status,
    new_status task_status NOT NULL,
    event_time TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    details TEXT
);

-- ------------------------------------------------------------
-- 4. Heap comparison function
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION has_higher_priority(
    p_mode heap_mode,
    p_candidate BIGINT,
    p_current BIGINT
)
RETURNS BOOLEAN
LANGUAGE SQL
IMMUTABLE
STRICT
AS $$
    SELECT CASE p_mode
        WHEN 'MIN' THEN p_candidate < p_current
        WHEN 'MAX' THEN p_candidate > p_current
    END;
$$;

-- ------------------------------------------------------------
-- 5. Heap invariant validation
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_heap(
    p_heap_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_mode heap_mode;
    v_valid BOOLEAN;
BEGIN
    SELECT mode
    INTO v_mode
    FROM heaps
    WHERE heap_id = p_heap_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Heap % does not exist', p_heap_id;
    END IF;

    SELECT NOT EXISTS (
        SELECT 1
        FROM heap_nodes child
        JOIN heap_nodes parent
          ON parent.heap_id = child.heap_id
         AND parent.position = (child.position - 1) / 2
        WHERE child.heap_id = p_heap_id
          AND has_higher_priority(
              v_mode,
              child.value,
              parent.value
          )
    )
    INTO v_valid;

    RETURN v_valid;
END;
$$;

-- ------------------------------------------------------------
-- 6. Heap creation
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION create_heap(
    p_name VARCHAR,
    p_mode heap_mode
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_heap_id BIGINT;
BEGIN
    IF p_name IS NULL OR length(trim(p_name)) = 0 THEN
        RAISE EXCEPTION 'Heap name is required';
    END IF;

    INSERT INTO heaps(heap_name, mode)
    VALUES (p_name, p_mode)
    RETURNING heap_id INTO v_heap_id;

    RETURN v_heap_id;
END;
$$;

-- ------------------------------------------------------------
-- 7. Sift-up operation
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION heap_sift_up(
    p_heap_id BIGINT,
    p_position INTEGER
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_mode heap_mode;
    v_parent INTEGER;
    v_child_value BIGINT;
    v_parent_value BIGINT;
BEGIN
    SELECT mode INTO v_mode
    FROM heaps
    WHERE heap_id = p_heap_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Heap does not exist';
    END IF;

    WHILE p_position > 0 LOOP
        v_parent := (p_position - 1) / 2;

        SELECT value INTO v_child_value
        FROM heap_nodes
        WHERE heap_id = p_heap_id
          AND position = p_position;

        SELECT value INTO v_parent_value
        FROM heap_nodes
        WHERE heap_id = p_heap_id
          AND position = v_parent;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'Parent node is missing';
        END IF;

        IF NOT has_higher_priority(
            v_mode,
            v_child_value,
            v_parent_value
        ) THEN
            EXIT;
        END IF;

        UPDATE heap_nodes
        SET value = CASE position
            WHEN p_position THEN v_parent_value
            WHEN v_parent THEN v_child_value
        END
        WHERE heap_id = p_heap_id
          AND position IN (p_position, v_parent);

        p_position := v_parent;
    END LOOP;
END;
$$;

-- ------------------------------------------------------------
-- 8. Sift-down operation
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION heap_sift_down(
    p_heap_id BIGINT,
    p_position INTEGER,
    p_size INTEGER
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_mode heap_mode;
    v_left INTEGER;
    v_right INTEGER;
    v_best INTEGER;
    v_current BIGINT;
    v_candidate BIGINT;
    v_best_value BIGINT;
BEGIN
    SELECT mode INTO v_mode
    FROM heaps
    WHERE heap_id = p_heap_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Heap does not exist';
    END IF;

    LOOP
        v_left := 2 * p_position + 1;
        v_right := 2 * p_position + 2;
        v_best := p_position;

        SELECT value INTO v_current
        FROM heap_nodes
        WHERE heap_id = p_heap_id
          AND position = p_position;

        IF NOT FOUND THEN
            EXIT;
        END IF;

        IF v_left < p_size THEN
            SELECT value INTO v_candidate
            FROM heap_nodes
            WHERE heap_id = p_heap_id
              AND position = v_left;

            IF has_higher_priority(
                v_mode,
                v_candidate,
                v_current
            ) THEN
                v_best := v_left;
            END IF;
        END IF;

        IF v_right < p_size THEN
            SELECT value INTO v_candidate
            FROM heap_nodes
            WHERE heap_id = p_heap_id
              AND position = v_right;

            SELECT value INTO v_best_value
            FROM heap_nodes
            WHERE heap_id = p_heap_id
              AND position = v_best;

            IF has_higher_priority(
                v_mode,
                v_candidate,
                v_best_value
            ) THEN
                v_best := v_right;
            END IF;
        END IF;

        IF v_best = p_position THEN
            EXIT;
        END IF;

        UPDATE heap_nodes
        SET value = CASE position
            WHEN p_position THEN (
                SELECT value
                FROM heap_nodes
                WHERE heap_id = p_heap_id
                  AND position = v_best
            )
            WHEN v_best THEN v_current
        END
        WHERE heap_id = p_heap_id
          AND position IN (p_position, v_best);

        p_position := v_best;
    END LOOP;
END;
$$;

-- ------------------------------------------------------------
-- 9. Insertion
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION heap_insert(
    p_heap_id BIGINT,
    p_value BIGINT
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_position INTEGER;
BEGIN
    PERFORM 1
    FROM heaps
    WHERE heap_id = p_heap_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Heap does not exist';
    END IF;

    SELECT COALESCE(MAX(position) + 1, 0)
    INTO v_position
    FROM heap_nodes
    WHERE heap_id = p_heap_id;

    INSERT INTO heap_nodes(heap_id, position, value)
    VALUES (p_heap_id, v_position, p_value);

    PERFORM heap_sift_up(p_heap_id, v_position);
END;
$$;

-- ------------------------------------------------------------
-- 10. Extract root
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION heap_extract(
    p_heap_id BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_root BIGINT;
    v_last BIGINT;
    v_size INTEGER;
BEGIN
    PERFORM 1
    FROM heaps
    WHERE heap_id = p_heap_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Heap does not exist';
    END IF;

    SELECT COUNT(*) INTO v_size
    FROM heap_nodes
    WHERE heap_id = p_heap_id;

    IF v_size = 0 THEN
        RAISE EXCEPTION 'Cannot extract from empty heap';
    END IF;

    SELECT value INTO v_root
    FROM heap_nodes
    WHERE heap_id = p_heap_id
      AND position = 0;

    SELECT value INTO v_last
    FROM heap_nodes
    WHERE heap_id = p_heap_id
      AND position = v_size - 1;

    DELETE FROM heap_nodes
    WHERE heap_id = p_heap_id
      AND position = v_size - 1;

    IF v_size > 1 THEN
        UPDATE heap_nodes
        SET value = v_last
        WHERE heap_id = p_heap_id
          AND position = 0;

        PERFORM heap_sift_down(
            p_heap_id,
            0,
            v_size - 1
        );
    END IF;

    RETURN v_root;
END;
$$;

-- ------------------------------------------------------------
-- 11. Arbitrary indexed deletion
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION heap_delete_at(
    p_heap_id BIGINT,
    p_position INTEGER
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_removed BIGINT;
    v_last BIGINT;
    v_size INTEGER;
    v_parent_value BIGINT;
    v_mode heap_mode;
BEGIN
    PERFORM 1
    FROM heaps
    WHERE heap_id = p_heap_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Heap does not exist';
    END IF;

    SELECT COUNT(*) INTO v_size
    FROM heap_nodes
    WHERE heap_id = p_heap_id;

    IF p_position < 0 OR p_position >= v_size THEN
        RAISE EXCEPTION 'Invalid heap position';
    END IF;

    SELECT value INTO v_removed
    FROM heap_nodes
    WHERE heap_id = p_heap_id
      AND position = p_position;

    SELECT value INTO v_last
    FROM heap_nodes
    WHERE heap_id = p_heap_id
      AND position = v_size - 1;

    DELETE FROM heap_nodes
    WHERE heap_id = p_heap_id
      AND position = v_size - 1;

    IF p_position < v_size - 1 THEN
        UPDATE heap_nodes
        SET value = v_last
        WHERE heap_id = p_heap_id
          AND position = p_position;

        SELECT mode INTO v_mode
        FROM heaps
        WHERE heap_id = p_heap_id;

        IF p_position > 0 THEN
            SELECT value INTO v_parent_value
            FROM heap_nodes
            WHERE heap_id = p_heap_id
              AND position = (p_position - 1) / 2;
        END IF;

        IF p_position > 0 AND has_higher_priority(
            v_mode,
            v_last,
            v_parent_value
        ) THEN
            PERFORM heap_sift_up(p_heap_id, p_position);
        ELSE
            PERFORM heap_sift_down(
                p_heap_id,
                p_position,
                v_size - 1
            );
        END IF;
    END IF;

    RETURN v_removed;
END;
$$;

-- ------------------------------------------------------------
-- 12. Heapify existing nodes
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION heap_build(
    p_heap_id BIGINT
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_size INTEGER;
    v_position INTEGER;
BEGIN
    PERFORM 1
    FROM heaps
    WHERE heap_id = p_heap_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Heap does not exist';
    END IF;

    SELECT COUNT(*) INTO v_size
    FROM heap_nodes
    WHERE heap_id = p_heap_id;

    FOR v_position IN REVERSE
        (v_size / 2 - 1)..0
    LOOP
        PERFORM heap_sift_down(
            p_heap_id,
            v_position,
            v_size
        );
    END LOOP;
END;
$$;

-- ------------------------------------------------------------
-- 13. Task status audit trigger
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION audit_task_status()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO task_execution_history(
            task_id,
            previous_status,
            new_status,
            details
        )
        VALUES (
            NEW.task_id,
            NULL,
            NEW.status,
            'Task created'
        );

    ELSIF OLD.status IS DISTINCT FROM NEW.status THEN
        INSERT INTO task_execution_history(
            task_id,
            previous_status,
            new_status,
            details
        )
        VALUES (
            NEW.task_id,
            OLD.status,
            NEW.status,
            'Task status changed'
        );
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_task_status_audit
AFTER INSERT OR UPDATE OF status
ON scheduled_tasks
FOR EACH ROW
EXECUTE FUNCTION audit_task_status();

-- ------------------------------------------------------------
-- 14. Task submission
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION submit_task(
    p_key VARCHAR,
    p_description TEXT,
    p_priority INTEGER
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_task_id BIGINT;
BEGIN
    IF p_key IS NULL OR length(trim(p_key)) = 0 THEN
        RAISE EXCEPTION 'Task key is required';
    END IF;

    IF p_priority < 0 THEN
        RAISE EXCEPTION 'Priority cannot be negative';
    END IF;

    INSERT INTO scheduled_tasks(
        external_key,
        description,
        priority
    )
    VALUES (
        p_key,
        p_description,
        p_priority
    )
    RETURNING task_id INTO v_task_id;

    RETURN v_task_id;
END;
$$;

-- ------------------------------------------------------------
-- 15. Transaction-safe task processing
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE process_next_task()
LANGUAGE plpgsql
AS $$
DECLARE
    v_task_id BIGINT;
BEGIN
    SELECT task_id
    INTO v_task_id
    FROM scheduled_tasks
    WHERE status = 'QUEUED'
    ORDER BY priority DESC, sequence_number ASC
    LIMIT 1
    FOR UPDATE SKIP LOCKED;

    IF v_task_id IS NULL THEN
        RAISE NOTICE 'No queued task available';
        RETURN;
    END IF;

    UPDATE scheduled_tasks
    SET status = 'PROCESSING',
        started_at = CURRENT_TIMESTAMP
    WHERE task_id = v_task_id;

    -- The example workload completes synchronously.
    UPDATE scheduled_tasks
    SET status = 'COMPLETED',
        completed_at = CURRENT_TIMESTAMP
    WHERE task_id = v_task_id;
END;
$$;

-- ------------------------------------------------------------
-- 16. Reporting views
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW heap_inspection AS
SELECT
    h.heap_id,
    h.heap_name,
    h.mode,
    n.position,
    n.value,
    CASE
        WHEN n.position = 0 THEN NULL
        ELSE (n.position - 1) / 2
    END AS parent_position,
    2 * n.position + 1 AS left_child_position,
    2 * n.position + 2 AS right_child_position
FROM heaps h
LEFT JOIN heap_nodes n
    ON n.heap_id = h.heap_id;

CREATE OR REPLACE VIEW task_queue_report AS
SELECT
    task_id,
    external_key,
    description,
    priority,
    status,
    sequence_number,
    created_at,
    started_at,
    completed_at,
    failure_reason
FROM scheduled_tasks;

CREATE OR REPLACE VIEW task_status_summary AS
SELECT
    status,
    COUNT(*) AS task_count,
    AVG(priority)::NUMERIC(10, 2) AS average_priority
FROM scheduled_tasks
GROUP BY status;

COMMIT;

-- ============================================================
-- 17. Sample data and demonstrations
-- ============================================================

-- Create independent min and max heaps.

SELECT create_heap('minimum_heap', 'MIN');
SELECT create_heap('maximum_heap', 'MAX');

-- Populate min heap.

DO $$
DECLARE
    v_heap_id BIGINT;
    v_value BIGINT;
BEGIN
    SELECT heap_id INTO v_heap_id
    FROM heaps
    WHERE heap_name = 'minimum_heap';

    FOREACH v_value IN ARRAY ARRAY[40, 10, 30, 5, 20, 50]
    LOOP
        PERFORM heap_insert(v_heap_id, v_value);
    END LOOP;
END;
$$;

-- Populate max heap.

DO $$
DECLARE
    v_heap_id BIGINT;
    v_value BIGINT;
BEGIN
    SELECT heap_id INTO v_heap_id
    FROM heaps
    WHERE heap_name = 'maximum_heap';

    FOREACH v_value IN ARRAY ARRAY[40, 10, 30, 5, 20, 50]
    LOOP
        PERFORM heap_insert(v_heap_id, v_value);
    END LOOP;
END;
$$;

-- Inspect both heaps.

SELECT *
FROM heap_inspection
ORDER BY heap_id, position;

-- Validate heap invariants.

SELECT
    heap_name,
    validate_heap(heap_id) AS is_valid
FROM heaps;

-- Extract minimum.

SELECT heap_extract(
    (SELECT heap_id FROM heaps
     WHERE heap_name = 'minimum_heap')
) AS extracted_minimum;

-- Extract maximum.

SELECT heap_extract(
    (SELECT heap_id FROM heaps
     WHERE heap_name = 'maximum_heap')
) AS extracted_maximum;

-- Delete a specific heap position.

SELECT heap_delete_at(
    (SELECT heap_id FROM heaps
     WHERE heap_name = 'minimum_heap'),
    2
) AS deleted_value;

-- Insert additional value.

SELECT heap_insert(
    (SELECT heap_id FROM heaps
     WHERE heap_name = 'minimum_heap'),
    2
);

-- Verify modified heap.

SELECT
    heap_name,
    validate_heap(heap_id) AS is_valid
FROM heaps;

SELECT *
FROM heap_inspection
WHERE heap_name = 'minimum_heap'
ORDER BY position;

-- ============================================================
-- 18. Priority queue sample records
-- ============================================================

SELECT submit_task(
    'TASK-101',
    'Database backup',
    3
);

SELECT submit_task(
    'TASK-102',
    'Security incident investigation',
    10
);

SELECT submit_task(
    'TASK-103',
    'Infrastructure monitoring',
    5
);

SELECT submit_task(
    'TASK-104',
    'Critical service outage',
    10
);

-- Priority descending, FIFO for equal priorities.

SELECT
    task_id,
    external_key,
    description,
    priority,
    sequence_number,
    status
FROM scheduled_tasks
WHERE status = 'QUEUED'
ORDER BY priority DESC, sequence_number ASC;

-- Process one task transactionally.

BEGIN;

CALL process_next_task();

COMMIT;

-- ============================================================
-- 19. Retrieval and aggregation
-- ============================================================

SELECT *
FROM task_queue_report
ORDER BY priority DESC, sequence_number;

SELECT *
FROM task_status_summary
ORDER BY status;

-- CTE-based priority ranking.

WITH ranked_tasks AS (
    SELECT
        external_key,
        description,
        priority,
        status,
        ROW_NUMBER() OVER (
            PARTITION BY status
            ORDER BY priority DESC, sequence_number ASC
        ) AS priority_rank
    FROM scheduled_tasks
)
SELECT *
FROM ranked_tasks
ORDER BY status, priority_rank;

-- Execution history.

SELECT
    t.external_key,
    h.previous_status,
    h.new_status,
    h.event_time,
    h.details
FROM task_execution_history h
JOIN scheduled_tasks t
    ON t.task_id = h.task_id
ORDER BY h.event_time;

-- ============================================================
-- 20. Validation and failure demonstrations
-- ============================================================

-- Negative priority is rejected by submit_task.

-- Uncomment separately to test:
-- SELECT submit_task('TASK-INVALID', 'Invalid priority', -1);

-- Duplicate external keys are rejected by the unique constraint.

-- Uncomment separately to test:
-- SELECT submit_task('TASK-101', 'Duplicate task', 2);

-- Extraction from an empty heap raises an exception.

-- Uncomment separately to test:
-- SELECT heap_extract(
--     (SELECT heap_id FROM heaps WHERE heap_name = 'empty_heap')
-- );

-- Heap validation for every stored heap.

SELECT
    h.heap_name,
    h.mode,
    COUNT(n.position) AS node_count,
    validate_heap(h.heap_id) AS invariant_holds
FROM heaps h
LEFT JOIN heap_nodes n
    ON n.heap_id = h.heap_id
GROUP BY h.heap_id, h.heap_name, h.mode
ORDER BY h.heap_name;
