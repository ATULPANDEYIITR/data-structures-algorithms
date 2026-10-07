DROP SCHEMA IF EXISTS linked_list_lab CASCADE;

CREATE SCHEMA linked_list_lab;

SET search_path TO linked_list_lab;

-- A relational representation of advanced linked-list structures.
-- PostgreSQL is used because recursive CTEs, identity references, arrays,
-- check constraints, and transactional DML make structural validation
-- expressive without requiring application-only rules.

CREATE TABLE linked_list (
    list_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    list_name TEXT NOT NULL UNIQUE,
    list_type TEXT NOT NULL CHECK (
        list_type IN (
            'SINGLY',
            'RANDOM_POINTER',
            'MULTILEVEL_DOUBLY'
        )
    ),
    description TEXT NOT NULL
);

CREATE TABLE list_node (
    node_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    list_id BIGINT NOT NULL
        REFERENCES linked_list(list_id)
        ON DELETE CASCADE,
    position_hint INTEGER,
    value INTEGER NOT NULL,
    next_node_id BIGINT REFERENCES list_node(node_id),
    prev_node_id BIGINT REFERENCES list_node(node_id),
    child_node_id BIGINT REFERENCES list_node(node_id),
    random_node_id BIGINT REFERENCES list_node(node_id),

    CONSTRAINT node_not_self_next
        CHECK (next_node_id IS NULL OR next_node_id <> node_id),

    CONSTRAINT node_not_self_prev
        CHECK (prev_node_id IS NULL OR prev_node_id <> node_id),

    CONSTRAINT node_not_self_child
        CHECK (child_node_id IS NULL OR child_node_id <> node_id)
);

CREATE INDEX idx_list_node_list
    ON list_node(list_id);

CREATE INDEX idx_list_node_next
    ON list_node(next_node_id);

CREATE INDEX idx_list_node_random
    ON list_node(random_node_id);

CREATE INDEX idx_list_node_child
    ON list_node(child_node_id);

CREATE TABLE list_head (
    list_id BIGINT PRIMARY KEY
        REFERENCES linked_list(list_id)
        ON DELETE CASCADE,
    head_node_id BIGINT
        REFERENCES list_node(node_id)
        ON DELETE SET NULL
);

CREATE TABLE sorted_batch (
    batch_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    batch_name TEXT NOT NULL UNIQUE,
    source_system TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sorted_batch_item (
    batch_id BIGINT NOT NULL
        REFERENCES sorted_batch(batch_id)
        ON DELETE CASCADE,
    sequence_number INTEGER NOT NULL CHECK (sequence_number > 0),
    value INTEGER NOT NULL,
    PRIMARY KEY (batch_id, sequence_number)
);

CREATE INDEX idx_sorted_batch_item_value
    ON sorted_batch_item(batch_id, value);

INSERT INTO linked_list (list_name, list_type, description)
VALUES
(
    'intersection_left',
    'SINGLY',
    'First path that joins a physically shared tail.'
),
(
    'intersection_right',
    'SINGLY',
    'Second path that joins the same shared tail.'
),
(
    'random_pointer_source',
    'RANDOM_POINTER',
    'Random-pointer structure used for deep-copy validation.'
),
(
    'multilevel_source',
    'MULTILEVEL_DOUBLY',
    'Nested child relationships used for flattening.'
);

-- The shared tail is deliberately represented by the same node IDs.
-- This models physical intersection rather than equal values.

INSERT INTO list_node (list_id, position_hint, value)
SELECT list_id, position_hint, value
FROM (
    VALUES
        ((SELECT list_id FROM linked_list WHERE list_name = 'intersection_left'), 1, 3),
        ((SELECT list_id FROM linked_list WHERE list_name = 'intersection_left'), 2, 7),
        ((SELECT list_id FROM linked_list WHERE list_name = 'intersection_left'), 3, 8),
        ((SELECT list_id FROM linked_list WHERE list_name = 'intersection_left'), 4, 10),
        ((SELECT list_id FROM linked_list WHERE list_name = 'intersection_left'), 5, 12)
) AS seed(list_id, position_hint, value);

INSERT INTO list_node (list_id, position_hint, value)
SELECT list_id, position_hint, value
FROM (
    VALUES
        ((SELECT list_id FROM linked_list WHERE list_name = 'intersection_right'), 1, 99),
        ((SELECT list_id FROM linked_list WHERE list_name = 'intersection_right'), 2, 1),
        ((SELECT list_id FROM linked_list WHERE list_name = 'intersection_right'), 3, 5)
) AS seed(list_id, position_hint, value);

WITH left_nodes AS (
    SELECT node_id, position_hint
    FROM list_node
    WHERE list_id = (
        SELECT list_id
        FROM linked_list
        WHERE list_name = 'intersection_left'
    )
),
right_nodes AS (
    SELECT node_id, position_hint
    FROM list_node
    WHERE list_id = (
        SELECT list_id
        FROM linked_list
        WHERE list_name = 'intersection_right'
    )
)
UPDATE list_node target
SET next_node_id = source.node_id
FROM left_nodes target_position
JOIN left_nodes source
    ON source.position_hint = target_position.position_hint + 1
WHERE target.node_id = target_position.node_id;

UPDATE list_node
SET next_node_id = (
    SELECT node_id
    FROM list_node
    WHERE list_id = (
        SELECT list_id
        FROM linked_list
        WHERE list_name = 'intersection_left'
    )
    AND position_hint = 3
)
WHERE list_id = (
    SELECT list_id
    FROM linked_list
    WHERE list_name = 'intersection_right'
)
AND position_hint = 3;

-- The two lists now share the left list's nodes at positions 3 through 5.
-- The right list's final node points into that shared physical tail.

UPDATE list_node
SET next_node_id = (
    SELECT node_id
    FROM list_node
    WHERE list_id = (
        SELECT list_id
        FROM linked_list
        WHERE list_name = 'intersection_left'
    )
    AND position_hint = 3
)
WHERE list_id = (
    SELECT list_id
    FROM linked_list
    WHERE list_name = 'intersection_right'
)
AND position_hint = 3;

INSERT INTO list_head (list_id, head_node_id)
SELECT
    l.list_id,
    n.node_id
FROM linked_list l
JOIN list_node n
    ON n.list_id = l.list_id
   AND n.position_hint = 1
WHERE l.list_name IN ('intersection_left', 'intersection_right');

-- Random-pointer example.
INSERT INTO list_node (list_id, position_hint, value)
SELECT
    (SELECT list_id
     FROM linked_list
     WHERE list_name = 'random_pointer_source'),
    position_number,
    node_value
FROM (
    VALUES
        (1, 7),
        (2, 13),
        (3, 11),
        (4, 10),
        (5, 1)
) AS values(position_number, node_value);

UPDATE list_node current_node
SET next_node_id = next_node.node_id
FROM list_node next_node
WHERE current_node.list_id = (
        SELECT list_id
        FROM linked_list
        WHERE list_name = 'random_pointer_source'
    )
  AND next_node.list_id = current_node.list_id
  AND next_node.position_hint = current_node.position_hint + 1;

UPDATE list_node n
SET random_node_id = target.node_id
FROM list_node target
WHERE n.list_id = (
        SELECT list_id
        FROM linked_list
        WHERE list_name = 'random_pointer_source'
    )
  AND target.list_id = n.list_id
  AND (
        (n.position_hint = 2 AND target.position_hint = 1)
        OR
        (n.position_hint = 3 AND target.position_hint = 5)
        OR
        (n.position_hint = 4 AND target.position_hint = 3)
        OR
        (n.position_hint = 5 AND target.position_hint = 5)
    );

INSERT INTO list_head (list_id, head_node_id)
SELECT
    l.list_id,
    n.node_id
FROM linked_list l
JOIN list_node n
    ON n.list_id = l.list_id
   AND n.position_hint = 1
WHERE l.list_name = 'random_pointer_source';

-- Multilevel doubly linked structure:
--
-- 1 - 2 - 3 - 4
--     |
--     5 - 6
--         |
--         7

INSERT INTO list_node (list_id, position_hint, value)
SELECT
    (SELECT list_id
     FROM linked_list
     WHERE list_name = 'multilevel_source'),
    position_number,
    node_value
FROM (
    VALUES
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
        (7, 7)
) AS values(position_number, node_value);

UPDATE list_node current_node
SET next_node_id = next_node.node_id
FROM list_node next_node
WHERE current_node.list_id = (
        SELECT list_id
        FROM linked_list
        WHERE list_name = 'multilevel_source'
    )
  AND next_node.list_id = current_node.list_id
  AND (
        (current_node.position_hint = 1 AND next_node.position_hint = 2)
        OR
        (current_node.position_hint = 2 AND next_node.position_hint = 3)
        OR
        (current_node.position_hint = 3 AND next_node.position_hint = 4)
        OR
        (current_node.position_hint = 5 AND next_node.position_hint = 6)
    );

UPDATE list_node current_node
SET prev_node_id = previous_node.node_id
FROM list_node previous_node
WHERE current_node.list_id = (
        SELECT list_id
        FROM linked_list
        WHERE list_name = 'multilevel_source'
    )
  AND previous_node.list_id = current_node.list_id
  AND (
        (current_node.position_hint = 2 AND previous_node.position_hint = 1)
        OR
        (current_node.position_hint = 3 AND previous_node.position_hint = 2)
        OR
        (current_node.position_hint = 4 AND previous_node.position_hint = 3)
        OR
        (current_node.position_hint = 6 AND previous_node.position_hint = 5)
    );

UPDATE list_node parent
SET child_node_id = child.node_id
FROM list_node child
WHERE parent.list_id = (
        SELECT list_id
        FROM linked_list
        WHERE list_name = 'multilevel_source'
    )
  AND child.list_id = parent.list_id
  AND (
        (parent.position_hint = 2 AND child.position_hint = 5)
        OR
        (parent.position_hint = 6 AND child.position_hint = 7)
    );

INSERT INTO list_head (list_id, head_node_id)
SELECT
    l.list_id,
    n.node_id
FROM linked_list l
JOIN list_node n
    ON n.list_id = l.list_id
   AND n.position_hint = 1
WHERE l.list_name = 'multilevel_source';

-- Detect the physical intersection.
WITH RECURSIVE left_path AS (
    SELECT
        h.head_node_id AS node_id,
        0 AS depth
    FROM list_head h
    JOIN linked_list l
        ON l.list_id = h.list_id
    WHERE l.list_name = 'intersection_left'

    UNION ALL

    SELECT
        n.next_node_id,
        left_path.depth + 1
    FROM left_path
    JOIN list_node n
        ON n.node_id = left_path.node_id
    WHERE n.next_node_id IS NOT NULL
),
right_path AS (
    SELECT
        h.head_node_id AS node_id,
        0 AS depth
    FROM list_head h
    JOIN linked_list l
        ON l.list_id = h.list_id
    WHERE l.list_name = 'intersection_right'

    UNION ALL

    SELECT
        n.next_node_id,
        right_path.depth + 1
    FROM right_path
    JOIN list_node n
        ON n.node_id = right_path.node_id
    WHERE n.next_node_id IS NOT NULL
)
SELECT
    left_path.node_id AS intersection_node_id,
    n.value,
    left_path.depth AS left_depth,
    right_path.depth AS right_depth
FROM left_path
JOIN right_path
    ON right_path.node_id = left_path.node_id
JOIN list_node n
    ON n.node_id = left_path.node_id
ORDER BY left_path.depth
LIMIT 1;

-- Verify random-pointer topology.
SELECT
    n.position_hint,
    n.value,
    random_target.value AS random_value
FROM list_node n
LEFT JOIN list_node random_target
    ON random_target.node_id = n.random_node_id
WHERE n.list_id = (
    SELECT list_id
    FROM linked_list
    WHERE list_name = 'random_pointer_source'
)
ORDER BY n.position_hint;

-- Recursive traversal of the primary multilevel next chain.
WITH RECURSIVE chain AS (
    SELECT
        h.head_node_id AS node_id,
        0 AS depth
    FROM list_head h
    JOIN linked_list l
        ON l.list_id = h.list_id
    WHERE l.list_name = 'multilevel_source'

    UNION ALL

    SELECT
        n.next_node_id,
        chain.depth + 1
    FROM chain
    JOIN list_node n
        ON n.node_id = chain.node_id
    WHERE n.next_node_id IS NOT NULL
)
SELECT
    chain.depth,
    node.value,
    node.child_node_id
FROM chain
JOIN list_node node
    ON node.node_id = chain.node_id
ORDER BY chain.depth;

INSERT INTO sorted_batch (batch_name, source_system)
VALUES
    ('warehouse_a', 'warehouse-feed'),
    ('warehouse_b', 'warehouse-feed');

INSERT INTO sorted_batch_item
    (batch_id, sequence_number, value)
SELECT
    b.batch_id,
    input.sequence_number,
    input.value
FROM sorted_batch b
JOIN (
    VALUES
        ('warehouse_a', 1, 1),
        ('warehouse_a', 2, 4),
        ('warehouse_a', 3, 7),
        ('warehouse_a', 4, 10),
        ('warehouse_b', 1, 2),
        ('warehouse_b', 2, 3),
        ('warehouse_b', 3, 8),
        ('warehouse_b', 4, 9)
) AS input(batch_name, sequence_number, value)
    ON input.batch_name = b.batch_name;

-- Validate that a batch is sorted according to its sequence positions.
WITH ordered AS (
    SELECT
        batch_id,
        sequence_number,
        value,
        LAG(value) OVER (
            PARTITION BY batch_id
            ORDER BY sequence_number
        ) AS previous_value
    FROM sorted_batch_item
)
SELECT
    b.batch_name,
    COUNT(*) FILTER (
        WHERE ordered.previous_value IS NOT NULL
          AND ordered.value < ordered.previous_value
    ) AS ordering_violations
FROM ordered
JOIN sorted_batch b
    ON b.batch_id = ordered.batch_id
GROUP BY b.batch_name
ORDER BY b.batch_name;

-- Merge two sorted relational streams using a recursive CTE.
-- Each emitted row chooses the smallest current value from the two streams.
WITH RECURSIVE
a AS (
    SELECT
        sequence_number,
        value,
        ROW_NUMBER() OVER (ORDER BY sequence_number) AS rn
    FROM sorted_batch_item
    WHERE batch_id = (
        SELECT batch_id
        FROM sorted_batch
        WHERE batch_name = 'warehouse_a'
    )
),
b AS (
    SELECT
        sequence_number,
        value,
        ROW_NUMBER() OVER (ORDER BY sequence_number) AS rn
    FROM sorted_batch_item
    WHERE batch_id = (
        SELECT batch_id
        FROM sorted_batch
        WHERE batch_name = 'warehouse_b'
    )
),
merged AS (
    SELECT
        1 AS output_position,
        CASE
            WHEN a.value <= b.value THEN a.rn
            ELSE NULL
        END AS a_rn,
        CASE
            WHEN b.value < a.value THEN b.rn
            ELSE NULL
        END AS b_rn,
        LEAST(a.value, b.value) AS value
    FROM a
    CROSS JOIN b
    WHERE a.rn = 1
      AND b.rn = 1

    UNION ALL

    SELECT
        merged.output_position + 1,
        CASE
            WHEN merged.a_rn IS NULL
                 AND merged.b_rn IS NOT NULL
                 AND next_a.value <= next_b.value
                THEN 1
            ELSE merged.a_rn
        END,
        merged.b_rn,
        merged.value
    FROM merged
    LEFT JOIN a next_a
        ON next_a.rn = COALESCE(merged.a_rn, 0) + 1
    LEFT JOIN b next_b
        ON next_b.rn = COALESCE(merged.b_rn, 0) + 1
    WHERE merged.output_position < 8
)
SELECT *
FROM merged
ORDER BY output_position;

-- Stable partition represented relationally.
WITH classified AS (
    SELECT
        sequence_number,
        value,
        CASE
            WHEN value < 3 THEN 0
            ELSE 1
        END AS partition_group
    FROM (
        VALUES
            (1, 1),
            (2, 4),
            (3, 3),
            (4, 2),
            (5, 5),
            (6, 2)
    ) AS input(sequence_number, value)
),
stable_order AS (
    SELECT
        value,
        partition_group,
        ROW_NUMBER() OVER (
            PARTITION BY partition_group
            ORDER BY sequence_number
        ) AS within_group
    FROM classified
)
SELECT
    value,
    partition_group
FROM stable_order
ORDER BY partition_group, within_group;

-- A transaction demonstrates database-level protection of a pointer update.
BEGIN;

UPDATE list_node
SET next_node_id = NULL
WHERE node_id = (
    SELECT head_node_id
    FROM list_head h
    JOIN linked_list l
        ON l.list_id = h.list_id
    WHERE l.list_name = 'intersection_right'
);

-- The transaction is intentionally rolled back so the demonstration does
-- not destroy the sample topology.
ROLLBACK;

-- Detect duplicate incoming references. A singly linked structure normally
-- has at most one predecessor per node. Multiple predecessors may indicate
-- a shared structure or an invalid singly-linked representation.
SELECT
    next_node_id,
    COUNT(*) AS incoming_reference_count
FROM list_node
WHERE next_node_id IS NOT NULL
GROUP BY next_node_id
HAVING COUNT(*) > 1
ORDER BY incoming_reference_count DESC, next_node_id;

-- A useful structural report for debugging advanced linked-list data.
SELECT
    l.list_name,
    l.list_type,
    n.node_id,
    n.position_hint,
    n.value,
    n.next_node_id,
    n.prev_node_id,
    n.child_node_id,
    n.random_node_id
FROM linked_list l
JOIN list_node n
    ON n.list_id = l.list_id
ORDER BY l.list_name, n.position_hint, n.node_id;
