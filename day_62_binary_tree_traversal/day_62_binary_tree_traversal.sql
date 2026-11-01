-- ============================================================
-- BINARY TREE TRAVERSAL MANAGEMENT SYSTEM
-- PostgreSQL 14+
--
-- Supports:
--   1. Preorder traversal
--   2. Inorder traversal
--   3. Postorder traversal
--   4. Level-order traversal
--   5. Recursive and iterative traversal concepts
--   6. Tree integrity and structural validation
--   7. Hierarchical reporting and analytics
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS tree_lab;

SET search_path TO tree_lab, public;

-- Remove existing demonstration objects for repeatable execution.
DROP VIEW IF EXISTS traversal_summary CASCADE;
DROP FUNCTION IF EXISTS tree_height(BIGINT) CASCADE;
DROP FUNCTION IF EXISTS tree_node_count(BIGINT) CASCADE;
DROP FUNCTION IF EXISTS validate_tree(BIGINT) CASCADE;
DROP FUNCTION IF EXISTS get_traversal(BIGINT, TEXT) CASCADE;
DROP TABLE IF EXISTS tree_traversal_log CASCADE;
DROP TABLE IF EXISTS tree_nodes CASCADE;
DROP TABLE IF EXISTS binary_trees CASCADE;

-- ------------------------------------------------------------
-- 1. Tree registry
-- ------------------------------------------------------------

CREATE TABLE binary_trees (
    tree_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    tree_name VARCHAR(120) NOT NULL UNIQUE,

    description TEXT NOT NULL DEFAULT '',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_tree_name
        CHECK (length(trim(tree_name)) BETWEEN 1 AND 120)
);

-- ------------------------------------------------------------
-- 2. Node storage
--
-- Each node has at most one parent and two possible child
-- positions. The position constraint prevents duplicate
-- left or right children.
-- ------------------------------------------------------------

CREATE TABLE tree_nodes (
    node_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    tree_id BIGINT NOT NULL
        REFERENCES binary_trees(tree_id)
        ON DELETE CASCADE,

    parent_id BIGINT,

    node_value INTEGER NOT NULL,

    child_position SMALLINT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_child_position
        CHECK (
            (parent_id IS NULL AND child_position IS NULL)
            OR
            (parent_id IS NOT NULL AND child_position IN (0, 1))
        ),

    CONSTRAINT unique_parent_position
        UNIQUE (tree_id, parent_id, child_position),

    CONSTRAINT unique_tree_node
        UNIQUE (tree_id, node_id),

    CONSTRAINT valid_parent_reference
        FOREIGN KEY (tree_id, parent_id)
        REFERENCES tree_nodes(tree_id, node_id)
        DEFERRABLE INITIALLY DEFERRED
);

COMMENT ON COLUMN tree_nodes.child_position IS
'0 represents left child; 1 represents right child.';

CREATE UNIQUE INDEX one_root_per_tree
    ON tree_nodes(tree_id)
    WHERE parent_id IS NULL;

CREATE INDEX tree_nodes_parent_idx
    ON tree_nodes(tree_id, parent_id);

CREATE INDEX tree_nodes_value_idx
    ON tree_nodes(tree_id, node_value);

-- ------------------------------------------------------------
-- 3. Traversal execution history
-- ------------------------------------------------------------

CREATE TABLE tree_traversal_log (
    log_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    tree_id BIGINT NOT NULL
        REFERENCES binary_trees(tree_id)
        ON DELETE CASCADE,

    traversal_order VARCHAR(20) NOT NULL,

    visited_nodes INTEGER NOT NULL,

    execution_status VARCHAR(20) NOT NULL,

    execution_time_ms NUMERIC(12, 4),

    executed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_traversal_order
        CHECK (
            traversal_order IN (
                'preorder',
                'inorder',
                'postorder',
                'levelorder'
            )
        ),

    CONSTRAINT valid_execution_status
        CHECK (
            execution_status IN ('completed', 'failed')
        ),

    CONSTRAINT valid_visited_nodes
        CHECK (visited_nodes >= 0),

    CONSTRAINT valid_execution_time
        CHECK (
            execution_time_ms IS NULL
            OR execution_time_ms >= 0
        )
);

CREATE INDEX traversal_log_history_idx
    ON tree_traversal_log(tree_id, executed_at DESC);

-- ------------------------------------------------------------
-- 4. Tree validation
--
-- A recursive CTE detects cycles and unreachable nodes.
-- Every valid tree must have exactly one root.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_tree(p_tree_id BIGINT)
RETURNS TABLE (
    valid BOOLEAN,
    node_count BIGINT,
    root_count BIGINT,
    reachable_count BIGINT,
    has_cycle BOOLEAN,
    message TEXT
)
LANGUAGE SQL
STABLE
AS $$
    WITH RECURSIVE
    nodes AS (
        SELECT *
        FROM tree_nodes
        WHERE tree_id = p_tree_id
    ),
    roots AS (
        SELECT node_id
        FROM nodes
        WHERE parent_id IS NULL
    ),
    walk(node_id, visited, cycle_detected) AS (
        SELECT
            node_id,
            ARRAY[node_id]::BIGINT[],
            FALSE
        FROM roots

        UNION ALL

        SELECT
            child.node_id,
            parent.visited || child.node_id,
            child.node_id = ANY(parent.visited)
        FROM walk parent
        JOIN nodes child
            ON child.parent_id = parent.node_id
        WHERE NOT parent.cycle_detected
    ),
    statistics AS (
        SELECT
            (SELECT COUNT(*) FROM nodes) AS total_nodes,
            (SELECT COUNT(*) FROM roots) AS total_roots,
            (
                SELECT COUNT(DISTINCT node_id)
                FROM walk
                WHERE NOT cycle_detected
            ) AS reachable_nodes,
            COALESCE(
                (SELECT bool_or(cycle_detected) FROM walk),
                FALSE
            ) AS cycle_found
    )
    SELECT
        (
            total_roots = 1
            AND total_nodes = reachable_nodes
            AND NOT cycle_found
        ),
        total_nodes,
        total_roots,
        reachable_nodes,
        cycle_found,
        CASE
            WHEN total_nodes = 0
                THEN 'Tree contains no nodes.'
            WHEN cycle_found
                THEN 'Cycle detected.'
            WHEN total_roots <> 1
                THEN 'Tree must contain exactly one root.'
            WHEN total_nodes <> reachable_nodes
                THEN 'Unreachable nodes detected.'
            ELSE 'Tree structure is valid.'
        END
    FROM statistics;
$$;

-- ------------------------------------------------------------
-- 5. Tree height
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION tree_height(p_tree_id BIGINT)
RETURNS INTEGER
LANGUAGE SQL
STABLE
AS $$
    WITH RECURSIVE levels AS (
        SELECT node_id, 1 AS depth
        FROM tree_nodes
        WHERE tree_id = p_tree_id
          AND parent_id IS NULL

        UNION ALL

        SELECT child.node_id, parent.depth + 1
        FROM levels parent
        JOIN tree_nodes child
          ON child.parent_id = parent.node_id
         AND child.tree_id = p_tree_id
    )
    SELECT COALESCE(MAX(depth), 0)::INTEGER
    FROM levels;
$$;

-- ------------------------------------------------------------
-- 6. Node count
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION tree_node_count(p_tree_id BIGINT)
RETURNS BIGINT
LANGUAGE SQL
STABLE
AS $$
    SELECT COUNT(*)
    FROM tree_nodes
    WHERE tree_id = p_tree_id;
$$;

-- ------------------------------------------------------------
-- 7. General traversal function
--
-- Sort keys encode traversal order:
--
-- Preorder:
--   node marker 0; left edge 1; right edge 2.
--
-- Inorder:
--   left edge 0; node marker 1; right edge 2.
--
-- Postorder:
--   left edge 0; right edge 1; node marker 2.
--
-- Level-order:
--   sort by depth and then left-to-right path.
--
-- This recursive query calculates traversal ordering without
-- relying on physical table row order.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION get_traversal(
    p_tree_id BIGINT,
    p_order TEXT
)
RETURNS TABLE (
    position BIGINT,
    node_id BIGINT,
    node_value INTEGER,
    depth INTEGER
)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    IF p_order NOT IN (
        'preorder',
        'inorder',
        'postorder',
        'levelorder'
    ) THEN
        RAISE EXCEPTION
            'Unsupported traversal order: %', p_order;
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM validate_tree(p_tree_id)
        WHERE valid
    ) THEN
        RAISE EXCEPTION
            'Cannot traverse invalid tree: %', p_tree_id;
    END IF;

    RETURN QUERY
    WITH RECURSIVE traversal AS (
        SELECT
            n.node_id,
            n.node_value,
            n.parent_id,
            n.child_position,
            1 AS depth,
            ''::TEXT AS path
        FROM tree_nodes n
        WHERE n.tree_id = p_tree_id
          AND n.parent_id IS NULL

        UNION ALL

        SELECT
            child.node_id,
            child.node_value,
            child.parent_id,
            child.child_position,
            parent.depth + 1,
            parent.path ||
                CASE child.child_position
                    WHEN 0 THEN '0'
                    WHEN 1 THEN '1'
                END
        FROM traversal parent
        JOIN tree_nodes child
            ON child.parent_id = parent.node_id
           AND child.tree_id = p_tree_id
    ),
    ordered AS (
        SELECT
            t.node_id,
            t.node_value,
            t.depth,

            CASE p_order
                WHEN 'preorder'
                    THEN t.path || '0'
                WHEN 'inorder'
                    THEN t.path || '1'
                WHEN 'postorder'
                    THEN t.path || '2'
            END AS traversal_key,

            t.path AS level_path

        FROM traversal t
    )
    SELECT
        ROW_NUMBER() OVER (
            ORDER BY
                CASE
                    WHEN p_order = 'levelorder'
                        THEN depth
                END,
                CASE
                    WHEN p_order = 'levelorder'
                        THEN level_path
                END,
                CASE
                    WHEN p_order <> 'levelorder'
                        THEN traversal_key
                END
        )::BIGINT,
        node_id,
        node_value,
        depth
    FROM ordered;
END;
$$;

-- ------------------------------------------------------------
-- 8. Reporting view
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW traversal_summary AS
SELECT
    t.tree_id,
    t.tree_name,
    COUNT(n.node_id) AS node_count,
    COALESCE(
        MAX(
            CASE
                WHEN n.parent_id IS NULL THEN 1
                ELSE 0
            END
        ),
        0
    ) AS has_root,
    tree_height(t.tree_id) AS height,
    COUNT(n.node_id) FILTER (
        WHERE n.child_position = 0
    ) AS left_children,
    COUNT(n.node_id) FILTER (
        WHERE n.child_position = 1
    ) AS right_children
FROM binary_trees t
LEFT JOIN tree_nodes n
    ON n.tree_id = t.tree_id
GROUP BY t.tree_id, t.tree_name;

-- ------------------------------------------------------------
-- 9. Sample tree
-- ------------------------------------------------------------

INSERT INTO binary_trees (
    tree_name,
    description
)
VALUES (
    'Enterprise Hierarchy',
    'Nine-node binary hierarchy for traversal analysis.'
);

-- Node values:
--
--                 50
--               /    \
--             30      70
--            /  \    /  \
--           20  40  60  80
--          /          \
--         10           65

INSERT INTO tree_nodes (
    tree_id,
    parent_id,
    node_value,
    child_position
)
SELECT
    t.tree_id,
    data.parent_id,
    data.node_value,
    data.child_position
FROM binary_trees t
CROSS JOIN (
    VALUES
        (NULL::BIGINT, 50, NULL::SMALLINT),
        (1::BIGINT, 30, 0::SMALLINT)
) AS unused(parent_id, node_value, child_position)
WHERE FALSE;

-- Insert the root first and use returned identifiers.
WITH inserted_root AS (
    INSERT INTO tree_nodes (
        tree_id,
        parent_id,
        node_value,
        child_position
    )
    SELECT tree_id, NULL, 50, NULL
    FROM binary_trees
    WHERE tree_name = 'Enterprise Hierarchy'
    RETURNING node_id, tree_id
),
inserted_children AS (
    INSERT INTO tree_nodes (
        tree_id,
        parent_id,
        node_value,
        child_position
    )
    SELECT
        root.tree_id,
        root.node_id,
        data.node_value,
        data.child_position
    FROM inserted_root root
    CROSS JOIN (
        VALUES
            (30, 0::SMALLINT),
            (70, 1::SMALLINT)
    ) AS data(node_value, child_position)
    RETURNING node_id, tree_id, node_value
),
second_level AS (
    INSERT INTO tree_nodes (
        tree_id,
        parent_id,
        node_value,
        child_position
    )
    SELECT
        child.tree_id,
        child.node_id,
        data.node_value,
        data.child_position
    FROM inserted_children child
    CROSS JOIN LATERAL (
        VALUES
            (
                CASE
                    WHEN child.node_value = 30 THEN 20
                    WHEN child.node_value = 70 THEN 60
                END,
                0::SMALLINT
            ),
            (
                CASE
                    WHEN child.node_value = 30 THEN 40
                    WHEN child.node_value = 70 THEN 80
                END,
                1::SMALLINT
            )
    ) AS data(node_value, child_position)
    RETURNING node_id, tree_id, node_value
)
INSERT INTO tree_nodes (
    tree_id,
    parent_id,
    node_value,
    child_position
)
SELECT
    parent.tree_id,
    parent.node_id,
    CASE parent.node_value
        WHEN 20 THEN 10
        WHEN 60 THEN 65
    END,
    CASE parent.node_value
        WHEN 20 THEN 0
        WHEN 60 THEN 1
    END
FROM second_level parent
WHERE parent.node_value IN (20, 60);

-- ------------------------------------------------------------
-- 10. Demonstration queries
-- ------------------------------------------------------------

-- Validate the tree.
SELECT *
FROM validate_tree(
    (SELECT tree_id
     FROM binary_trees
     WHERE tree_name = 'Enterprise Hierarchy')
);

-- Preorder.
SELECT *
FROM get_traversal(
    (SELECT tree_id
     FROM binary_trees
     WHERE tree_name = 'Enterprise Hierarchy'),
    'preorder'
);

-- Inorder.
SELECT *
FROM get_traversal(
    (SELECT tree_id
     FROM binary_trees
     WHERE tree_name = 'Enterprise Hierarchy'),
    'inorder'
);

-- Postorder.
SELECT *
FROM get_traversal(
    (SELECT tree_id
     FROM binary_trees
     WHERE tree_name = 'Enterprise Hierarchy'),
    'postorder'
);

-- Level-order.
SELECT *
FROM get_traversal(
    (SELECT tree_id
     FROM binary_trees
     WHERE tree_name = 'Enterprise Hierarchy'),
    'levelorder'
);

-- ------------------------------------------------------------
-- 11. Level-wise reporting
-- ------------------------------------------------------------

SELECT
    depth,
    ARRAY_AGG(node_value ORDER BY position) AS nodes_at_level
FROM get_traversal(
    (
        SELECT tree_id
        FROM binary_trees
        WHERE tree_name = 'Enterprise Hierarchy'
    ),
    'levelorder'
)
GROUP BY depth
ORDER BY depth;

-- ------------------------------------------------------------
-- 12. Aggregation and structural analytics
-- ------------------------------------------------------------

SELECT *
FROM traversal_summary;

-- Leaf nodes.
SELECT node_id, node_value
FROM tree_nodes n
WHERE tree_id = (
    SELECT tree_id
    FROM binary_trees
    WHERE tree_name = 'Enterprise Hierarchy'
)
AND NOT EXISTS (
    SELECT 1
    FROM tree_nodes child
    WHERE child.tree_id = n.tree_id
      AND child.parent_id = n.node_id
)
ORDER BY node_value;

-- Parent and child relationships.
SELECT
    parent.node_value AS parent_value,
    left_child.node_value AS left_value,
    right_child.node_value AS right_value
FROM tree_nodes parent
LEFT JOIN tree_nodes left_child
    ON left_child.parent_id = parent.node_id
   AND left_child.tree_id = parent.tree_id
   AND left_child.child_position = 0
LEFT JOIN tree_nodes right_child
    ON right_child.parent_id = parent.node_id
   AND right_child.tree_id = parent.tree_id
   AND right_child.child_position = 1
WHERE parent.tree_id = (
    SELECT tree_id
    FROM binary_trees
    WHERE tree_name = 'Enterprise Hierarchy'
)
ORDER BY parent.node_value;

-- ------------------------------------------------------------
-- 13. Traversal execution logging
-- ------------------------------------------------------------

INSERT INTO tree_traversal_log (
    tree_id,
    traversal_order,
    visited_nodes,
    execution_status,
    execution_time_ms
)
SELECT
    t.tree_id,
    orders.traversal_order,
    tree_node_count(t.tree_id)::INTEGER,
    'completed',
    NULL
FROM binary_trees t
CROSS JOIN (
    VALUES
        ('preorder'),
        ('inorder'),
        ('postorder'),
        ('levelorder')
) AS orders(traversal_order)
WHERE t.tree_name = 'Enterprise Hierarchy';

SELECT
    traversal_order,
    visited_nodes,
    execution_status,
    executed_at
FROM tree_traversal_log
ORDER BY log_id;

-- ------------------------------------------------------------
-- 14. Failure-condition demonstrations
-- ------------------------------------------------------------

DO $$
DECLARE
    selected_tree BIGINT;
    rejected BOOLEAN := FALSE;
BEGIN
    SELECT tree_id
    INTO selected_tree
    FROM binary_trees
    WHERE tree_name = 'Enterprise Hierarchy';

    -- Invalid traversal names must be rejected.
    BEGIN
        PERFORM *
        FROM get_traversal(selected_tree, 'diagonal');

    EXCEPTION
        WHEN OTHERS THEN
            rejected := TRUE;
            RAISE NOTICE
                'Invalid traversal correctly rejected: %',
                SQLERRM;
    END;

    IF NOT rejected THEN
        RAISE EXCEPTION
            'Invalid traversal validation failed.';
    END IF;

    -- A second root must violate the partial unique index.
    rejected := FALSE;

    BEGIN
        INSERT INTO tree_nodes (
            tree_id,
            parent_id,
            node_value,
            child_position
        )
        VALUES (
            selected_tree,
            NULL,
            999,
            NULL
        );

    EXCEPTION
        WHEN unique_violation THEN
            rejected := TRUE;
            RAISE NOTICE
                'Duplicate root correctly rejected.';
    END;

    IF NOT rejected THEN
        RAISE EXCEPTION
            'Duplicate root validation failed.';
    END IF;
END;
$$;

COMMIT;

-- ============================================================
-- END OF BINARY TREE TRAVERSAL MANAGEMENT SYSTEM
-- ============================================================
