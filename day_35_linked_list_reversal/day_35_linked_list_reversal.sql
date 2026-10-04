DROP SCHEMA IF EXISTS linked_list_reversal_lab CASCADE;
CREATE SCHEMA linked_list_reversal_lab;
SET search_path TO linked_list_reversal_lab;

-- PostgreSQL models a linked list naturally as an adjacency relation:
-- each node identifies its successor through next_node_id.
CREATE TABLE linked_list (
    list_id       BIGSERIAL PRIMARY KEY,
    list_name     TEXT NOT NULL UNIQUE,
    algorithm     TEXT NOT NULL CHECK (
        algorithm IN (
            'iterative',
            'recursive',
            'reverse_in_groups'
        )
    ),
    group_size    INTEGER,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (
        (algorithm = 'reverse_in_groups' AND group_size IS NOT NULL AND group_size > 0)
        OR
        (algorithm <> 'reverse_in_groups' AND group_size IS NULL)
    )
);

CREATE TABLE list_node (
    node_id         BIGSERIAL PRIMARY KEY,
    list_id         BIGINT NOT NULL REFERENCES linked_list(list_id) ON DELETE CASCADE,
    position        INTEGER NOT NULL CHECK (position > 0),
    node_value      INTEGER NOT NULL,
    next_node_id    BIGINT REFERENCES list_node(node_id) ON DELETE SET NULL,
    UNIQUE (list_id, position),
    UNIQUE (list_id, node_id)
);

CREATE INDEX idx_list_node_list_position
    ON list_node(list_id, position);

CREATE INDEX idx_list_node_next
    ON list_node(next_node_id);

-- A position describes the original logical order. next_node_id describes
-- the actual linked structure, allowing SQL to inspect both representations.
INSERT INTO linked_list (list_name, algorithm)
VALUES
    ('iterative_demo', 'iterative'),
    ('recursive_demo', 'recursive'),
    ('group_demo', 'reverse_in_groups');

UPDATE linked_list
SET group_size = 3
WHERE list_name = 'group_demo';

INSERT INTO list_node (list_id, position, node_value)
SELECT l.list_id, v.position, v.node_value
FROM linked_list l
CROSS JOIN (
    VALUES
        (1, 10),
        (2, 20),
        (3, 30),
        (4, 40),
        (5, 50)
) AS v(position, node_value)
WHERE l.list_name = 'iterative_demo';

INSERT INTO list_node (list_id, position, node_value)
SELECT l.list_id, v.position, v.node_value
FROM linked_list l
CROSS JOIN (
    VALUES
        (1, 100),
        (2, 200),
        (3, 300),
        (4, 400),
        (5, 500)
) AS v(position, node_value)
WHERE l.list_name = 'recursive_demo';

INSERT INTO list_node (list_id, position, node_value)
SELECT l.list_id, v.position, v.node_value
FROM linked_list l
CROSS JOIN (
    VALUES
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
        (7, 7),
        (8, 8)
) AS v(position, node_value)
WHERE l.list_name = 'group_demo';

-- Establish successor pointers according to the original sequence.
UPDATE list_node current_node
SET next_node_id = next_node.node_id
FROM list_node next_node
WHERE current_node.list_id = next_node.list_id
  AND next_node.position = current_node.position + 1;

CREATE TABLE reversal_operation (
    operation_id       BIGSERIAL PRIMARY KEY,
    list_id            BIGINT NOT NULL REFERENCES linked_list(list_id) ON DELETE CASCADE,
    operation_type     TEXT NOT NULL CHECK (
        operation_type IN (
            'iterative',
            'recursive',
            'group_reversal'
        )
    ),
    group_size         INTEGER,
    started_at         TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at       TIMESTAMPTZ,
    success             BOOLEAN NOT NULL DEFAULT FALSE,
    CHECK (
        (operation_type = 'group_reversal' AND group_size > 0)
        OR
        (operation_type <> 'group_reversal' AND group_size IS NULL)
    )
);

CREATE TABLE reversal_result (
    operation_id       BIGINT NOT NULL REFERENCES reversal_operation(operation_id) ON DELETE CASCADE,
    output_position    INTEGER NOT NULL CHECK (output_position > 0),
    node_id            BIGINT NOT NULL REFERENCES list_node(node_id) ON DELETE CASCADE,
    PRIMARY KEY (operation_id, output_position)
);

-- Recursive CTE traversal follows next_node_id. This is the SQL equivalent
-- of walking a pointer chain rather than merely sorting by position.
WITH RECURSIVE traversal AS (
    SELECT
        n.list_id,
        n.node_id,
        n.position,
        n.node_value,
        n.next_node_id,
        1 AS depth,
        ARRAY[n.node_id]::BIGINT[] AS visited
    FROM list_node n
    JOIN linked_list l ON l.list_id = n.list_id
    WHERE l.list_name = 'iterative_demo'
      AND n.position = 1

    UNION ALL

    SELECT
        n.list_id,
        n.node_id,
        n.position,
        n.node_value,
        n.next_node_id,
        t.depth + 1,
        t.visited || n.node_id
    FROM traversal t
    JOIN list_node n
      ON n.node_id = t.next_node_id
    WHERE NOT n.node_id = ANY(t.visited)
)
SELECT
    depth,
    node_id,
    node_value,
    position
FROM traversal
ORDER BY depth;

-- Iterative reversal can be represented relationally by mapping every
-- original position p to its predecessor's node. The final node becomes
-- the new head, and the original head terminates the reversed chain.
WITH ordered AS (
    SELECT
        node_id,
        list_id,
        position,
        LAG(node_id) OVER (
            PARTITION BY list_id
            ORDER BY position
        ) AS previous_node_id,
        COUNT(*) OVER (
            PARTITION BY list_id
        ) AS node_count
    FROM list_node
    WHERE list_id = (
        SELECT list_id
        FROM linked_list
        WHERE list_name = 'iterative_demo'
    )
)
SELECT
    position AS original_position,
    node_id,
    previous_node_id AS successor_after_reversal
FROM ordered
ORDER BY position DESC;

-- Recursive reversal can be analyzed through the same adjacency chain.
-- The recursive CTE preserves the traversal depth and therefore makes the
-- original successor relation explicit before the links are conceptually
-- inverted.
WITH RECURSIVE chain AS (
    SELECT
        n.node_id,
        n.node_value,
        n.next_node_id,
        1 AS depth
    FROM list_node n
    JOIN linked_list l ON l.list_id = n.list_id
    WHERE l.list_name = 'recursive_demo'
      AND n.position = 1

    UNION ALL

    SELECT
        n.node_id,
        n.node_value,
        n.next_node_id,
        c.depth + 1
    FROM chain c
    JOIN list_node n
      ON n.node_id = c.next_node_id
)
SELECT
    depth,
    node_id,
    node_value,
    LAG(node_id) OVER (ORDER BY depth DESC) AS successor_when_reversed
FROM chain
ORDER BY depth DESC;

-- Reverse-in-groups requires a group boundary. FLOOR arithmetic assigns
-- complete groups without reversing an incomplete final group.
WITH ordered AS (
    SELECT
        n.*,
        l.group_size,
        COUNT(*) OVER (PARTITION BY n.list_id) AS total_nodes
    FROM list_node n
    JOIN linked_list l
      ON l.list_id = n.list_id
    WHERE l.list_name = 'group_demo'
),
complete_groups AS (
    SELECT
        *,
        ((position - 1) / group_size) AS group_number
    FROM ordered
    WHERE position <= (total_nodes / group_size) * group_size
),
partial_tail AS (
    SELECT *
    FROM ordered
    WHERE position > (total_nodes / group_size) * group_size
),
group_reversed AS (
    SELECT
        node_id,
        node_value,
        position,
        group_number,
        ROW_NUMBER() OVER (
            PARTITION BY group_number
            ORDER BY position DESC
        ) AS output_position_in_group
    FROM complete_groups
)
SELECT
    group_number,
    output_position_in_group,
    node_id,
    node_value
FROM group_reversed
ORDER BY group_number, output_position_in_group;

-- The incomplete final group remains in its original order.
WITH group_metadata AS (
    SELECT
        n.*,
        l.group_size,
        COUNT(*) OVER (PARTITION BY n.list_id) AS total_nodes
    FROM list_node n
    JOIN linked_list l ON l.list_id = n.list_id
    WHERE l.list_name = 'group_demo'
)
SELECT
    position,
    node_id,
    node_value,
    CASE
        WHEN position <= (total_nodes / group_size) * group_size
            THEN 'complete_group_reversed'
        ELSE 'partial_group_unchanged'
    END AS reversal_behavior
FROM group_metadata
ORDER BY position;

-- A transaction demonstrates that a computed reversal can be recorded
-- atomically. Either all result rows are stored or none are stored.
BEGIN;

INSERT INTO reversal_operation (
    list_id,
    operation_type,
    group_size
)
SELECT
    list_id,
    'group_reversal',
    group_size
FROM linked_list
WHERE list_name = 'group_demo'
RETURNING operation_id;

-- Record a concrete result for group_demo. The generated operation_id can
-- be obtained in application code from the RETURNING result. For a fully
-- reproducible SQL demonstration, identify the newest operation directly.
WITH latest_operation AS (
    SELECT operation_id
    FROM reversal_operation
    WHERE operation_type = 'group_reversal'
    ORDER BY operation_id DESC
    LIMIT 1
),
ordered AS (
    SELECT
        n.*,
        l.group_size,
        COUNT(*) OVER (PARTITION BY n.list_id) AS total_nodes
    FROM list_node n
    JOIN linked_list l ON l.list_id = n.list_id
    WHERE l.list_name = 'group_demo'
),
reversed_complete_groups AS (
    SELECT
        node_id,
        node_value,
        position,
        ((position - 1) / group_size) AS group_number,
        ROW_NUMBER() OVER (
            PARTITION BY ((position - 1) / group_size)
            ORDER BY position DESC
        ) AS local_position
    FROM ordered
    WHERE position <= (total_nodes / group_size) * group_size
),
tail_rows AS (
    SELECT
        node_id,
        node_value,
        position,
        2147483647 AS group_number,
        position - ((total_nodes / group_size) * group_size) AS local_position
    FROM ordered
    WHERE position > (total_nodes / group_size) * group_size
),
combined AS (
    SELECT * FROM reversed_complete_groups
    UNION ALL
    SELECT * FROM tail_rows
),
numbered AS (
    SELECT
        node_id,
        ROW_NUMBER() OVER (
            ORDER BY group_number, local_position
        )::INTEGER AS output_position
    FROM combined
)
INSERT INTO reversal_result (
    operation_id,
    output_position,
    node_id
)
SELECT
    o.operation_id,
    n.output_position,
    n.node_id
FROM latest_operation o
CROSS JOIN numbered n;

UPDATE reversal_operation
SET
    completed_at = CURRENT_TIMESTAMP,
    success = TRUE
WHERE operation_id = (
    SELECT MAX(operation_id)
    FROM reversal_operation
    WHERE operation_type = 'group_reversal'
);

COMMIT;

-- Inspect the materialized group-reversal result.
SELECT
    rr.output_position,
    ln.node_id,
    ln.node_value
FROM reversal_result rr
JOIN list_node ln
  ON ln.node_id = rr.node_id
WHERE rr.operation_id = (
    SELECT MAX(operation_id)
    FROM reversal_operation
    WHERE operation_type = 'group_reversal'
)
ORDER BY rr.output_position;

-- Database constraints expose invalid group sizes before workflow execution.
DO $$
BEGIN
    BEGIN
        INSERT INTO linked_list (list_name, algorithm, group_size)
        VALUES ('invalid_group', 'reverse_in_groups', 0);
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'Invalid group size rejected by CHECK constraint.';
    END;
END
$$;

-- Detect duplicate logical positions.
SELECT
    list_id,
    position,
    COUNT(*) AS occurrences
FROM list_node
GROUP BY list_id, position
HAVING COUNT(*) > 1;

-- Detect nodes that have multiple inbound references. A singly linked list
-- should normally have at most one predecessor for each node.
SELECT
    next_node_id,
    COUNT(*) AS predecessor_count
FROM list_node
WHERE next_node_id IS NOT NULL
GROUP BY next_node_id
HAVING COUNT(*) > 1;

-- Detect an incorrect tail according to position.
SELECT
    l.list_name,
    n.node_id,
    n.position,
    n.next_node_id
FROM linked_list l
JOIN list_node n ON n.list_id = l.list_id
WHERE n.position = (
    SELECT MAX(n2.position)
    FROM list_node n2
    WHERE n2.list_id = n.list_id
)
AND n.next_node_id IS NOT NULL;

-- Query the stored operation history.
SELECT
    ro.operation_id,
    l.list_name,
    ro.operation_type,
    ro.group_size,
    ro.success,
    ro.started_at,
    ro.completed_at
FROM reversal_operation ro
JOIN linked_list l ON l.list_id = ro.list_id
ORDER BY ro.operation_id;
