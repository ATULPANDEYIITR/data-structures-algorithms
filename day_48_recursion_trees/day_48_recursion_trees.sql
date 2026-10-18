-- Recursion Trees: PostgreSQL data model and analytical workflow
--
-- The database stores observed recursive calls as a tree. Each call has a
-- parent, local work, recursive state, and result. This supports analysis
-- of branching factor, depth, leaves, repeated states, and total cost.
--
-- PostgreSQL features used:
--   - generated identity keys
--   - foreign keys
--   - CHECK constraints
--   - partial and composite indexes
--   - recursive CTEs
--   - views
--   - transactions
--   - window functions

DROP SCHEMA IF EXISTS recursion_trees CASCADE;
CREATE SCHEMA recursion_trees;

SET search_path TO recursion_trees;

CREATE TABLE algorithms (
    algorithm_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name text NOT NULL UNIQUE,
    recurrence text NOT NULL,
    description text NOT NULL
);

CREATE TABLE executions (
    execution_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    algorithm_id bigint NOT NULL
        REFERENCES algorithms(algorithm_id),
    input_size integer NOT NULL CHECK (input_size >= 0),
    started_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    completed_at timestamptz,
    status text NOT NULL
        CHECK (status IN ('RUNNING', 'COMPLETED', 'FAILED')),
    CHECK (
        completed_at IS NULL
        OR completed_at >= started_at
    )
);

CREATE TABLE call_nodes (
    node_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    execution_id bigint NOT NULL
        REFERENCES executions(execution_id)
        ON DELETE CASCADE,
    parent_node_id bigint,
    call_sequence integer NOT NULL CHECK (call_sequence > 0),
    depth integer NOT NULL CHECK (depth >= 0),
    operation text NOT NULL,
    state_key text NOT NULL,
    result_value bigint,
    local_cost integer NOT NULL CHECK (local_cost >= 0),
    is_terminal boolean NOT NULL DEFAULT false,

    CONSTRAINT call_nodes_parent_fk
        FOREIGN KEY (parent_node_id)
        REFERENCES call_nodes(node_id)
        DEFERRABLE INITIALLY DEFERRED,

    CONSTRAINT call_nodes_sequence_unique
        UNIQUE (execution_id, call_sequence)
);

CREATE TABLE recurrence_states (
    algorithm_id bigint NOT NULL
        REFERENCES algorithms(algorithm_id)
        ON DELETE CASCADE,
    state_key text NOT NULL,
    first_seen_execution bigint
        REFERENCES executions(execution_id),
    computed_value bigint,
    computation_count integer NOT NULL DEFAULT 1
        CHECK (computation_count > 0),
    PRIMARY KEY (algorithm_id, state_key)
);

CREATE INDEX idx_call_nodes_execution_parent
    ON call_nodes (execution_id, parent_node_id);

CREATE INDEX idx_call_nodes_execution_depth
    ON call_nodes (execution_id, depth);

CREATE INDEX idx_call_nodes_state
    ON call_nodes (execution_id, state_key);

CREATE INDEX idx_call_nodes_terminal
    ON call_nodes (execution_id)
    WHERE is_terminal = true;


INSERT INTO algorithms (name, recurrence, description)
VALUES
(
    'Fibonacci',
    'T(n) = T(n-1) + T(n-2) + O(1)',
    'Binary recursive branching with overlapping subproblems.'
),
(
    'Merge Sort',
    'T(n) = 2T(n/2) + O(n)',
    'Balanced divide-and-conquer recursion with linear work per level.'
),
(
    'Binary Search',
    'T(n) = T(n/2) + O(1)',
    'One recursive child survives at each internal call.'
);


INSERT INTO executions (
    algorithm_id,
    input_size,
    status
)
SELECT
    algorithm_id,
    6,
    'COMPLETED'
FROM algorithms
WHERE name = 'Fibonacci';

INSERT INTO executions (
    algorithm_id,
    input_size,
    status
)
SELECT
    algorithm_id,
    8,
    'COMPLETED'
FROM algorithms
WHERE name = 'Merge Sort';

INSERT INTO executions (
    algorithm_id,
    input_size,
    status
)
SELECT
    algorithm_id,
    64,
    'COMPLETED'
FROM algorithms
WHERE name = 'Binary Search';


-- Fibonacci call tree.
-- The parent-child structure preserves the actual recursive expansion.
WITH fib_nodes (
    execution_id,
    parent_node_id,
    call_sequence,
    depth,
    operation,
    state_key,
    result_value,
    local_cost,
    is_terminal
) AS (
    SELECT
        e.execution_id,
        NULL::bigint,
        1,
        0,
        'fib',
        '6',
        NULL::bigint,
        1,
        false
    FROM executions e
    JOIN algorithms a
        ON a.algorithm_id = e.algorithm_id
    WHERE a.name = 'Fibonacci'
    ORDER BY e.execution_id
    LIMIT 1
)
INSERT INTO call_nodes (
    execution_id,
    parent_node_id,
    call_sequence,
    depth,
    operation,
    state_key,
    result_value,
    local_cost,
    is_terminal
)
SELECT *
FROM fib_nodes;


-- Add a representative set of Fibonacci states as a normalized state table.
INSERT INTO recurrence_states (
    algorithm_id,
    state_key,
    computed_value,
    computation_count
)
SELECT
    algorithm_id,
    n::text,
    CASE
        WHEN n = 0 THEN 0
        WHEN n = 1 THEN 1
        WHEN n = 2 THEN 1
        WHEN n = 3 THEN 2
        WHEN n = 4 THEN 3
        WHEN n = 5 THEN 5
        WHEN n = 6 THEN 8
    END,
    CASE
        WHEN n = 6 THEN 1
        WHEN n = 5 THEN 2
        WHEN n = 4 THEN 3
        WHEN n = 3 THEN 5
        WHEN n = 2 THEN 8
        WHEN n = 1 THEN 5
        ELSE 3
    END
FROM algorithms
CROSS JOIN generate_series(0, 6) AS n
WHERE name = 'Fibonacci';


-- A completed merge-sort execution receives an explicit balanced tree.
WITH execution AS (
    SELECT e.execution_id
    FROM executions e
    JOIN algorithms a
        ON a.algorithm_id = e.algorithm_id
    WHERE a.name = 'Merge Sort'
    ORDER BY e.execution_id
    LIMIT 1
)
INSERT INTO call_nodes (
    execution_id,
    parent_node_id,
    call_sequence,
    depth,
    operation,
    state_key,
    result_value,
    local_cost,
    is_terminal
)
SELECT
    execution_id,
    NULL,
    1,
    0,
    'merge_sort',
    '[0,7]',
    NULL,
    8,
    false
FROM execution;


-- Binary-search root demonstrates a one-child recursive path.
WITH execution AS (
    SELECT e.execution_id
    FROM executions e
    JOIN algorithms a
        ON a.algorithm_id = e.algorithm_id
    WHERE a.name = 'Binary Search'
    ORDER BY e.execution_id
    LIMIT 1
)
INSERT INTO call_nodes (
    execution_id,
    parent_node_id,
    call_sequence,
    depth,
    operation,
    state_key,
    result_value,
    local_cost,
    is_terminal
)
SELECT
    execution_id,
    NULL,
    1,
    0,
    'binary_search',
    '[0,63]',
    NULL,
    1,
    false
FROM execution;


-- Add deeper binary-search calls while preserving a single branch.
WITH execution AS (
    SELECT e.execution_id
    FROM executions e
    JOIN algorithms a
        ON a.algorithm_id = e.algorithm_id
    WHERE a.name = 'Binary Search'
    ORDER BY e.execution_id
    LIMIT 1
),
root AS (
    SELECT node_id, execution_id
    FROM call_nodes
    WHERE execution_id = (SELECT execution_id FROM execution)
      AND call_sequence = 1
)
INSERT INTO call_nodes (
    execution_id,
    parent_node_id,
    call_sequence,
    depth,
    operation,
    state_key,
    result_value,
    local_cost,
    is_terminal
)
SELECT
    execution_id,
    node_id,
    2,
    1,
    'binary_search',
    '[32,63]',
    NULL,
    1,
    false
FROM root;


WITH execution AS (
    SELECT e.execution_id
    FROM executions e
    JOIN algorithms a
        ON a.algorithm_id = e.algorithm_id
    WHERE a.name = 'Binary Search'
    ORDER BY e.execution_id
    LIMIT 1
),
parent AS (
    SELECT node_id, execution_id
    FROM call_nodes
    WHERE execution_id = (SELECT execution_id FROM execution)
      AND call_sequence = 2
)
INSERT INTO call_nodes (
    execution_id,
    parent_node_id,
    call_sequence,
    depth,
    operation,
    state_key,
    result_value,
    local_cost,
    is_terminal
)
SELECT
    execution_id,
    node_id,
    3,
    2,
    'binary_search',
    '[48,63]',
    NULL,
    1,
    false
FROM parent;


-- Mark a successful leaf and provide its result.
WITH execution AS (
    SELECT e.execution_id
    FROM executions e
    JOIN algorithms a
        ON a.algorithm_id = e.algorithm_id
    WHERE a.name = 'Binary Search'
    ORDER BY e.execution_id
    LIMIT 1
)
UPDATE call_nodes
SET
    result_value = 50,
    is_terminal = true,
    operation = 'binary_search_match'
WHERE execution_id = (SELECT execution_id FROM execution)
  AND call_sequence = 3;


-- Recursive CTE: reconstruct a call tree from parent-child relationships.
WITH RECURSIVE call_tree AS (
    SELECT
        node_id,
        execution_id,
        parent_node_id,
        depth,
        operation,
        state_key,
        local_cost,
        ARRAY[node_id] AS path
    FROM call_nodes
    WHERE parent_node_id IS NULL

    UNION ALL

    SELECT
        child.node_id,
        child.execution_id,
        child.parent_node_id,
        child.depth,
        child.operation,
        child.state_key,
        child.local_cost,
        parent.path || child.node_id
    FROM call_nodes child
    JOIN call_tree parent
        ON child.parent_node_id = parent.node_id
       AND child.execution_id = parent.execution_id
)
SELECT
    execution_id,
    depth,
    operation,
    state_key,
    local_cost,
    path
FROM call_tree
ORDER BY execution_id, path;


-- Aggregate the tree by level. This exposes the amount of work performed
-- at each recursion depth rather than only the final total.
WITH RECURSIVE call_tree AS (
    SELECT
        node_id,
        execution_id,
        depth,
        local_cost
    FROM call_nodes
    WHERE parent_node_id IS NULL

    UNION ALL

    SELECT
        child.node_id,
        child.execution_id,
        child.depth,
        child.local_cost
    FROM call_nodes child
    JOIN call_tree parent
        ON child.parent_node_id = parent.node_id
       AND child.execution_id = parent.execution_id
)
SELECT
    execution_id,
    depth,
    count(*) AS calls_at_depth,
    sum(local_cost) AS work_at_depth
FROM call_tree
GROUP BY execution_id, depth
ORDER BY execution_id, depth;


-- Measure branching factor for every internal node.
SELECT
    parent.node_id,
    parent.operation,
    parent.state_key,
    count(child.node_id) AS child_count
FROM call_nodes parent
LEFT JOIN call_nodes child
    ON child.parent_node_id = parent.node_id
GROUP BY
    parent.node_id,
    parent.operation,
    parent.state_key
ORDER BY parent.node_id;


-- Find repeated recursive states. These are candidates for memoization.
SELECT
    algorithm_id,
    state_key,
    computation_count,
    computed_value
FROM recurrence_states
WHERE computation_count > 1
ORDER BY computation_count DESC, state_key;


-- A view exposes execution-level recursion metrics for repeated analysis.
CREATE VIEW execution_tree_metrics AS
WITH RECURSIVE tree AS (
    SELECT
        node_id,
        execution_id,
        parent_node_id,
        depth,
        local_cost,
        is_terminal
    FROM call_nodes
    WHERE parent_node_id IS NULL

    UNION ALL

    SELECT
        child.node_id,
        child.execution_id,
        child.parent_node_id,
        child.depth,
        child.local_cost,
        child.is_terminal
    FROM call_nodes child
    JOIN tree parent
        ON child.parent_node_id = parent.node_id
       AND child.execution_id = parent.execution_id
)
SELECT
    execution_id,
    count(*) AS node_count,
    max(depth) AS maximum_depth,
    sum(local_cost) AS total_cost,
    count(*) FILTER (WHERE is_terminal) AS terminal_nodes
FROM tree
GROUP BY execution_id;


SELECT *
FROM execution_tree_metrics
ORDER BY execution_id;


-- Demonstrate transactional integrity for a recursive state.
BEGIN;

INSERT INTO recurrence_states (
    algorithm_id,
    state_key,
    first_seen_execution,
    computed_value,
    computation_count
)
SELECT
    algorithm_id,
    '7',
    min(execution_id),
    13,
    1
FROM executions
WHERE algorithm_id = (
    SELECT algorithm_id
    FROM algorithms
    WHERE name = 'Fibonacci'
)
GROUP BY algorithm_id
ON CONFLICT (algorithm_id, state_key)
DO UPDATE
SET
    computed_value = EXCLUDED.computed_value,
    computation_count =
        recurrence_states.computation_count + 1;

COMMIT;


-- This query identifies states that have been evaluated more than once.
-- A high count indicates duplicated recursive work.
SELECT
    a.name AS algorithm,
    rs.state_key,
    rs.computation_count,
    rs.computed_value
FROM recurrence_states rs
JOIN algorithms a
    ON a.algorithm_id = rs.algorithm_id
WHERE rs.computation_count > 1
ORDER BY rs.computation_count DESC;


-- Database-level validation example:
-- negative local_cost cannot be inserted because of the CHECK constraint.
-- The following statement is intentionally omitted as executable DML
-- because it would abort the script transaction with a constraint error.
--
-- INSERT INTO call_nodes (
--     execution_id, call_sequence, depth, operation,
--     state_key, local_cost
-- )
-- VALUES (
--     1, 999, 0, 'invalid', 'negative-cost', -1
-- );
