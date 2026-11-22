/*
===============================================================================
TOPOLOGICAL SORTING AND DEPENDENCY MANAGEMENT
PostgreSQL 15+

Relational implementation of:
- Directed Acyclic Graphs
- Dependency registration
- Recursive cycle detection
- Kahn's topological sorting algorithm
- Dependency levels
- Build execution workflow
- Task state management
- Dependency failure propagation
- Reporting and eligibility evaluation

The direction of an edge is:

    prerequisite_task -> dependent_task

A dependent task cannot execute until all its prerequisites are complete.
===============================================================================
*/

BEGIN;

CREATE SCHEMA IF NOT EXISTS dependency_engine;

SET search_path TO dependency_engine, public;

-- ============================================================================
-- 1. DOMAIN TYPES
-- ============================================================================

CREATE TYPE task_status AS ENUM (
    'PENDING',
    'READY',
    'RUNNING',
    'COMPLETED',
    'FAILED',
    'BLOCKED'
);

CREATE TYPE task_category AS ENUM (
    'SOURCE',
    'VALIDATION',
    'BUILD',
    'TEST',
    'SECURITY',
    'PACKAGE',
    'DEPLOYMENT'
);

-- ============================================================================
-- 2. REPOSITORY AND TASK TABLES
-- ============================================================================

CREATE TABLE repositories (
    repository_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_name VARCHAR(150) NOT NULL UNIQUE,
    owner_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT repository_name_not_empty
        CHECK (LENGTH(TRIM(repository_name)) > 0)
);

CREATE TABLE tasks (
    task_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id)
        ON DELETE CASCADE,

    task_code VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    category task_category NOT NULL,
    status task_status NOT NULL DEFAULT 'PENDING',

    priority INTEGER NOT NULL DEFAULT 5,
    estimated_duration_seconds INTEGER NOT NULL DEFAULT 60,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    CONSTRAINT unique_repository_task
        UNIQUE(repository_id, task_code),

    CONSTRAINT valid_priority
        CHECK (priority BETWEEN 1 AND 10),

    CONSTRAINT valid_duration
        CHECK (estimated_duration_seconds > 0),

    CONSTRAINT valid_task_description
        CHECK (LENGTH(TRIM(description)) > 0),

    CONSTRAINT valid_completion_timestamps
        CHECK (
            completed_at IS NULL
            OR (
                started_at IS NOT NULL
                AND completed_at >= started_at
            )
        )
);

-- ============================================================================
-- 3. DEPENDENCY RELATIONSHIPS
-- ============================================================================

CREATE TABLE task_dependencies (
    dependency_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id)
        ON DELETE CASCADE,

    prerequisite_task_id BIGINT NOT NULL,
    dependent_task_id BIGINT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_dependency
        UNIQUE(prerequisite_task_id, dependent_task_id),

    CONSTRAINT no_self_dependency
        CHECK (prerequisite_task_id <> dependent_task_id),

    CONSTRAINT prerequisite_task_fk
        FOREIGN KEY(prerequisite_task_id)
        REFERENCES tasks(task_id)
        ON DELETE CASCADE,

    CONSTRAINT dependent_task_fk
        FOREIGN KEY(dependent_task_id)
        REFERENCES tasks(task_id)
        ON DELETE CASCADE
);

CREATE INDEX idx_dependency_prerequisite
    ON task_dependencies(prerequisite_task_id);

CREATE INDEX idx_dependency_dependent
    ON task_dependencies(dependent_task_id);

CREATE INDEX idx_tasks_repository_status
    ON tasks(repository_id, status);

CREATE INDEX idx_tasks_category
    ON tasks(category);

-- ============================================================================
-- 4. EXECUTION HISTORY
-- ============================================================================

CREATE TABLE task_execution_history (
    execution_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    task_id BIGINT NOT NULL
        REFERENCES tasks(task_id)
        ON DELETE CASCADE,

    previous_status task_status,
    new_status task_status NOT NULL,

    message TEXT,
    executed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_execution_history_task_time
    ON task_execution_history(task_id, executed_at DESC);

-- ============================================================================
-- 5. STATE TRANSITION AUDITING
-- ============================================================================

CREATE OR REPLACE FUNCTION audit_task_status_change()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF OLD.status IS DISTINCT FROM NEW.status THEN

        INSERT INTO task_execution_history (
            task_id,
            previous_status,
            new_status,
            message
        )
        VALUES (
            NEW.task_id,
            OLD.status,
            NEW.status,
            'Task status transition'
        );

    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_task_status_audit
AFTER UPDATE OF status ON tasks
FOR EACH ROW
EXECUTE FUNCTION audit_task_status_change();

-- ============================================================================
-- 6. DEPENDENCY INTEGRITY AND CYCLE PREVENTION
-- ============================================================================

CREATE OR REPLACE FUNCTION validate_dependency()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    source_repository BIGINT;
    destination_repository BIGINT;
    cycle_exists BOOLEAN;
BEGIN
    SELECT repository_id
    INTO source_repository
    FROM tasks
    WHERE task_id = NEW.prerequisite_task_id;

    SELECT repository_id
    INTO destination_repository
    FROM tasks
    WHERE task_id = NEW.dependent_task_id;

    IF source_repository IS NULL OR destination_repository IS NULL THEN
        RAISE EXCEPTION 'Both dependency tasks must exist.';
    END IF;

    IF source_repository <> destination_repository THEN
        RAISE EXCEPTION
            'Dependencies cannot cross repository boundaries.';
    END IF;

    IF NEW.repository_id <> source_repository THEN
        RAISE EXCEPTION
            'Dependency repository does not match task repository.';
    END IF;

    /*
     * Before inserting A -> B, search for an existing path B -> A.
     * If that path exists, the proposed edge creates a cycle.
     */

    WITH RECURSIVE reachable(node_id) AS (
        SELECT NEW.dependent_task_id

        UNION

        SELECT dependency.dependent_task_id
        FROM task_dependencies dependency
        JOIN reachable current
          ON dependency.prerequisite_task_id = current.node_id

        WHERE dependency.repository_id = NEW.repository_id
    )
    SELECT EXISTS (
        SELECT 1
        FROM reachable
        WHERE node_id = NEW.prerequisite_task_id
    )
    INTO cycle_exists;

    IF cycle_exists THEN
        RAISE EXCEPTION
            'Dependency rejected: edge creates a directed cycle.';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_dependency
BEFORE INSERT OR UPDATE OF
    repository_id,
    prerequisite_task_id,
    dependent_task_id
ON task_dependencies
FOR EACH ROW
EXECUTE FUNCTION validate_dependency();

-- ============================================================================
-- 7. VALID TASK STATE TRANSITIONS
-- ============================================================================

CREATE OR REPLACE FUNCTION validate_task_transition()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF OLD.status = NEW.status THEN
        RETURN NEW;
    END IF;

    IF NOT (
        (OLD.status = 'PENDING' AND NEW.status IN ('READY', 'BLOCKED'))
        OR
        (OLD.status = 'READY' AND NEW.status IN ('RUNNING', 'BLOCKED'))
        OR
        (OLD.status = 'RUNNING' AND NEW.status IN ('COMPLETED', 'FAILED'))
    ) THEN
        RAISE EXCEPTION
            'Invalid task transition: % -> %',
            OLD.status,
            NEW.status;
    END IF;

    IF NEW.status = 'RUNNING' AND NEW.started_at IS NULL THEN
        NEW.started_at = CURRENT_TIMESTAMP;
    END IF;

    IF NEW.status = 'COMPLETED' AND NEW.completed_at IS NULL THEN
        NEW.completed_at = CURRENT_TIMESTAMP;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_task_transition
BEFORE UPDATE OF status ON tasks
FOR EACH ROW
EXECUTE FUNCTION validate_task_transition();

-- ============================================================================
-- 8. DEPENDENCY REPORTING VIEW
-- ============================================================================

CREATE OR REPLACE VIEW task_dependency_report AS
SELECT
    task.task_id,
    task.repository_id,
    task.task_code,
    task.description,
    task.status,

    COUNT(dependency.prerequisite_task_id)
        AS prerequisite_count,

    COUNT(dependency.prerequisite_task_id)
        FILTER (
            WHERE prerequisite.status = 'COMPLETED'
        ) AS completed_prerequisites,

    COUNT(dependency.prerequisite_task_id)
        FILTER (
            WHERE prerequisite.status = 'FAILED'
        ) AS failed_prerequisites

FROM tasks task

LEFT JOIN task_dependencies dependency
    ON dependency.dependent_task_id = task.task_id

LEFT JOIN tasks prerequisite
    ON prerequisite.task_id = dependency.prerequisite_task_id

GROUP BY
    task.task_id,
    task.repository_id,
    task.task_code,
    task.description,
    task.status;

-- ============================================================================
-- 9. KAHN'S TOPOLOGICAL SORTING FUNCTION
-- ============================================================================

CREATE OR REPLACE FUNCTION topological_order(
    p_repository_id BIGINT
)
RETURNS TABLE (
    task_id BIGINT,
    task_code VARCHAR(100),
    execution_position INTEGER,
    execution_level INTEGER
)
LANGUAGE plpgsql
AS $$
DECLARE
    current_task BIGINT;
    current_code VARCHAR(100);
    current_level INTEGER;
    remaining INTEGER;
    edge RECORD;
    next_level INTEGER;
    processed INTEGER := 0;
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM repositories
        WHERE repository_id = p_repository_id
    ) THEN
        RAISE EXCEPTION 'Repository % does not exist.',
            p_repository_id;
    END IF;

    /*
     * Local temporary tables isolate the calculation from the
     * persistent repository state.
     */

    CREATE TEMP TABLE IF NOT EXISTS topo_indegree (
        node_id BIGINT PRIMARY KEY,
        degree INTEGER NOT NULL,
        execution_level INTEGER NOT NULL DEFAULT 0
    ) ON COMMIT DROP;

    CREATE TEMP TABLE IF NOT EXISTS topo_ready (
        node_id BIGINT PRIMARY KEY
    ) ON COMMIT DROP;

    CREATE TEMP TABLE IF NOT EXISTS topo_processed (
        node_id BIGINT PRIMARY KEY,
        position INTEGER NOT NULL,
        execution_level INTEGER NOT NULL
    ) ON COMMIT DROP;

    TRUNCATE topo_indegree;
    TRUNCATE topo_ready;
    TRUNCATE topo_processed;

    INSERT INTO topo_indegree (
        node_id,
        degree,
        execution_level
    )
    SELECT
        task.task_id,
        COUNT(dependency.dependency_id)::INTEGER,
        0

    FROM tasks task

    LEFT JOIN task_dependencies dependency
        ON dependency.dependent_task_id = task.task_id
       AND dependency.repository_id = p_repository_id

    WHERE task.repository_id = p_repository_id

    GROUP BY task.task_id;

    INSERT INTO topo_ready(node_id)
    SELECT node_id
    FROM topo_indegree
    WHERE degree = 0;

    LOOP
        SELECT node_id
        INTO current_task
        FROM topo_ready
        ORDER BY node_id
        LIMIT 1;

        EXIT WHEN NOT FOUND;

        DELETE FROM topo_ready
        WHERE node_id = current_task;

        SELECT task_code
        INTO current_code
        FROM tasks
        WHERE tasks.task_id = current_task;

        SELECT execution_level
        INTO current_level
        FROM topo_indegree
        WHERE node_id = current_task;

        processed := processed + 1;

        INSERT INTO topo_processed (
            node_id,
            position,
            execution_level
        )
        VALUES (
            current_task,
            processed,
            current_level
        );

        /*
         * Remove outgoing dependency contributions.
         * A dependent becomes ready when its indegree reaches zero.
         */

        FOR edge IN
            SELECT dependent_task_id
            FROM task_dependencies
            WHERE prerequisite_task_id = current_task
              AND repository_id = p_repository_id
        LOOP

            SELECT execution_level
            INTO next_level
            FROM topo_indegree
            WHERE node_id = current_task;

            UPDATE topo_indegree
            SET
                degree = degree - 1,
                execution_level = GREATEST(
                    execution_level,
                    next_level + 1
                )
            WHERE node_id = edge.dependent_task_id;

            SELECT degree
            INTO remaining
            FROM topo_indegree
            WHERE node_id = edge.dependent_task_id;

            IF remaining = 0 THEN
                INSERT INTO topo_ready(node_id)
                VALUES (edge.dependent_task_id)
                ON CONFLICT DO NOTHING;
            END IF;
        END LOOP;
    END LOOP;

    IF processed <> (
        SELECT COUNT(*)
        FROM tasks
        WHERE repository_id = p_repository_id
    ) THEN
        RAISE EXCEPTION
            'Topological sorting failed: dependency cycle exists.';
    END IF;

    RETURN QUERY
    SELECT
        task.task_id,
        task.task_code,
        result.position,
        result.execution_level

    FROM topo_processed result

    JOIN tasks task
        ON task.task_id = result.node_id

    ORDER BY result.position;
END;
$$;

-- ============================================================================
-- 10. DEPENDENCY ELIGIBILITY FUNCTION
-- ============================================================================

CREATE OR REPLACE FUNCTION task_is_eligible(
    p_task_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE sql
STABLE
AS $$
    SELECT
        EXISTS (
            SELECT 1
            FROM tasks
            WHERE task_id = p_task_id
              AND status IN ('PENDING', 'READY')
        )
        AND NOT EXISTS (
            SELECT 1
            FROM task_dependencies dependency

            JOIN tasks prerequisite
                ON prerequisite.task_id =
                   dependency.prerequisite_task_id

            WHERE dependency.dependent_task_id = p_task_id
              AND prerequisite.status <> 'COMPLETED'
        );
$$;

-- ============================================================================
-- 11. WORKFLOW PROCESSING PROCEDURE
-- ============================================================================

CREATE OR REPLACE PROCEDURE process_ready_tasks(
    p_repository_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    candidate RECORD;
BEGIN
    /*
     * Lock candidate tasks to prevent concurrent workers from
     * selecting the same pending work.
     */

    FOR candidate IN
        SELECT task.task_id

        FROM tasks task

        WHERE task.repository_id = p_repository_id
          AND task.status = 'PENDING'

          AND NOT EXISTS (
              SELECT 1
              FROM task_dependencies dependency

              JOIN tasks prerequisite
                  ON prerequisite.task_id =
                     dependency.prerequisite_task_id

              WHERE dependency.dependent_task_id = task.task_id
                AND prerequisite.status <> 'COMPLETED'
          )

        ORDER BY task.priority, task.task_id

        FOR UPDATE OF task SKIP LOCKED
    LOOP
        UPDATE tasks
        SET status = 'READY'
        WHERE task_id = candidate.task_id;
    END LOOP;
END;
$$;

-- ============================================================================
-- 12. SAMPLE REPOSITORY
-- ============================================================================

INSERT INTO repositories (
    repository_name,
    owner_name
)
VALUES (
    'enterprise-build-platform',
    'engineering-team'
);

INSERT INTO tasks (
    repository_id,
    task_code,
    description,
    category,
    priority,
    estimated_duration_seconds
)
SELECT
    repository_id,
    data.task_code,
    data.description,
    data.category::task_category,
    data.priority,
    data.duration

FROM repositories repository

CROSS JOIN (
    VALUES
        ('SOURCE', 'Retrieve source code', 'SOURCE', 1, 30),
        ('VALIDATE', 'Validate source files', 'VALIDATION', 2, 20),
        ('COMPILE', 'Compile application', 'BUILD', 3, 90),
        ('UNIT', 'Run unit tests', 'TEST', 4, 120),
        ('SECURITY', 'Perform security analysis', 'SECURITY', 4, 100),
        ('PACKAGE', 'Generate release package', 'PACKAGE', 5, 40),
        ('INTEGRATION', 'Run integration tests', 'TEST', 6, 150),
        ('DEPLOY', 'Deploy application', 'DEPLOYMENT', 7, 60)
) AS data(
    task_code,
    description,
    category,
    priority,
    duration
)

WHERE repository.repository_name =
    'enterprise-build-platform';

-- ============================================================================
-- 13. SAMPLE DEPENDENCY GRAPH
-- ============================================================================

INSERT INTO task_dependencies (
    repository_id,
    prerequisite_task_id,
    dependent_task_id
)
SELECT
    repository.repository_id,
    prerequisite.task_id,
    dependent.task_id

FROM repositories repository

JOIN (
    VALUES
        ('SOURCE', 'VALIDATE'),
        ('VALIDATE', 'COMPILE'),
        ('COMPILE', 'UNIT'),
        ('COMPILE', 'SECURITY'),
        ('UNIT', 'PACKAGE'),
        ('SECURITY', 'PACKAGE'),
        ('PACKAGE', 'INTEGRATION'),
        ('INTEGRATION', 'DEPLOY')
) AS edges(prerequisite_code, dependent_code)
    ON TRUE

JOIN tasks prerequisite
    ON prerequisite.repository_id = repository.repository_id
   AND prerequisite.task_code = edges.prerequisite_code

JOIN tasks dependent
    ON dependent.repository_id = repository.repository_id
   AND dependent.task_code = edges.dependent_code

WHERE repository.repository_name =
    'enterprise-build-platform';

-- ============================================================================
-- 14. SAMPLE RETRIEVAL QUERIES
-- ============================================================================

-- Retrieve repository tasks and current states.

SELECT
    repository.repository_name,
    task.task_code,
    task.description,
    task.status,
    task.priority

FROM repositories repository

JOIN tasks task
    ON task.repository_id = repository.repository_id

ORDER BY task.priority, task.task_code;

-- Retrieve dependency relationships.

SELECT
    prerequisite.task_code AS prerequisite,
    dependent.task_code AS dependent

FROM task_dependencies dependency

JOIN tasks prerequisite
    ON prerequisite.task_id = dependency.prerequisite_task_id

JOIN tasks dependent
    ON dependent.task_id = dependency.dependent_task_id

ORDER BY prerequisite.task_code, dependent.task_code;

-- ============================================================================
-- 15. TOPOLOGICAL ORDERING REPORT
-- ============================================================================

SELECT *
FROM topological_order(
    (
        SELECT repository_id
        FROM repositories
        WHERE repository_name = 'enterprise-build-platform'
    )
);

-- ============================================================================
-- 16. DEPENDENCY LEVEL REPORT
-- ============================================================================

SELECT
    task_code,
    execution_position,
    execution_level

FROM topological_order(
    (
        SELECT repository_id
        FROM repositories
        WHERE repository_name = 'enterprise-build-platform'
    )
)

ORDER BY execution_level, execution_position;

-- ============================================================================
-- 17. DEPENDENCY ELIGIBILITY REPORT
-- ============================================================================

SELECT
    task.task_code,
    task.status,
    task_is_eligible(task.task_id) AS execution_eligible

FROM tasks task

JOIN repositories repository
    ON repository.repository_id = task.repository_id

WHERE repository.repository_name =
    'enterprise-build-platform'

ORDER BY task.task_code;

-- ============================================================================
-- 18. AGGREGATION AND GRAPH METRICS
-- ============================================================================

SELECT
    repository.repository_name,

    COUNT(DISTINCT task.task_id) AS total_tasks,

    COUNT(DISTINCT dependency.dependency_id) AS total_dependencies,

    COUNT(DISTINCT task.task_id)
        FILTER (WHERE task.status = 'COMPLETED')
        AS completed_tasks,

    COUNT(DISTINCT task.task_id)
        FILTER (WHERE task.status = 'FAILED')
        AS failed_tasks,

    COUNT(DISTINCT task.task_id)
        FILTER (WHERE task.status = 'PENDING')
        AS pending_tasks

FROM repositories repository

LEFT JOIN tasks task
    ON task.repository_id = repository.repository_id

LEFT JOIN task_dependencies dependency
    ON dependency.repository_id = repository.repository_id

WHERE repository.repository_name =
    'enterprise-build-platform'

GROUP BY repository.repository_name;

-- ============================================================================
-- 19. WORKFLOW EXECUTION
-- ============================================================================

-- Start a transaction so the scheduling operation is atomic.

BEGIN;

CALL process_ready_tasks(
    (
        SELECT repository_id
        FROM repositories
        WHERE repository_name = 'enterprise-build-platform'
    )
);

COMMIT;

-- Inspect tasks that have become ready.

SELECT
    task_code,
    status
FROM tasks
WHERE status = 'READY'
ORDER BY task_code;

-- ============================================================================
-- 20. COMPLETE A READY TASK
-- ============================================================================

BEGIN;

UPDATE tasks
SET status = 'RUNNING'
WHERE task_code = 'SOURCE'
  AND status = 'READY';

UPDATE tasks
SET status = 'COMPLETED'
WHERE task_code = 'SOURCE'
  AND status = 'RUNNING';

COMMIT;

-- Newly eligible tasks can now be identified.

SELECT
    task.task_code,
    task_is_eligible(task.task_id) AS eligible

FROM tasks task

WHERE task.repository_id = (
    SELECT repository_id
    FROM repositories
    WHERE repository_name = 'enterprise-build-platform'
)

ORDER BY task.task_code;

-- ============================================================================
-- 21. EXECUTION HISTORY
-- ============================================================================

SELECT
    task.task_code,
    history.previous_status,
    history.new_status,
    history.executed_at,
    history.message

FROM task_execution_history history

JOIN tasks task
    ON task.task_id = history.task_id

ORDER BY history.executed_at, history.execution_id;

-- ============================================================================
-- 22. CYCLE PREVENTION TEST
-- ============================================================================

/*
 * The following operation must fail because it creates:
 *
 * SOURCE -> VALIDATE -> COMPILE -> UNIT -> PACKAGE
 *         -> INTEGRATION -> DEPLOY
 *
 * Adding DEPLOY -> SOURCE creates a directed cycle.
 *
 * Execute separately when testing exception handling.
 *
 * INSERT INTO task_dependencies (
 *     repository_id,
 *     prerequisite_task_id,
 *     dependent_task_id
 * )
 * SELECT
 *     repository.repository_id,
 *     deploy.task_id,
 *     source.task_id
 * FROM repositories repository
 * JOIN tasks deploy
 *     ON deploy.repository_id = repository.repository_id
 *    AND deploy.task_code = 'DEPLOY'
 * JOIN tasks source
 *     ON source.repository_id = repository.repository_id
 *    AND source.task_code = 'SOURCE'
 * WHERE repository.repository_name = 'enterprise-build-platform';
 */

-- ============================================================================
-- 23. INVALID TRANSITION TEST
-- ============================================================================

/*
 * This operation must fail because PENDING -> COMPLETED is not allowed.
 *
 * UPDATE tasks
 * SET status = 'COMPLETED'
 * WHERE task_code = 'VALIDATE';
 */

-- ============================================================================
-- 24. FINAL REPORT
-- ============================================================================

SELECT
    repository.repository_name,
    task.task_code,
    task.status,
    task.category,
    report.prerequisite_count,
    report.completed_prerequisites,
    report.failed_prerequisites,
    task_is_eligible(task.task_id) AS eligible

FROM repositories repository

JOIN tasks task
    ON task.repository_id = repository.repository_id

JOIN task_dependency_report report
    ON report.task_id = task.task_id

WHERE repository.repository_name =
    'enterprise-build-platform'

ORDER BY task.task_code;

-- ============================================================================
-- 25. TRANSACTION COMPLETION
-- ============================================================================

COMMIT;
