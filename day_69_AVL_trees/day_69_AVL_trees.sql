/*
 * AVL TREES - POSTGRESQL RELATIONAL IMPLEMENTATION
 *
 * PostgreSQL 15+
 *
 * Models:
 * - AVL tree metadata
 * - Nodes and parent-child relationships
 * - Stored node heights
 * - Balance factors
 * - LL, RR, LR, and RL rotation mechanics
 * - Balanced-tree construction from sorted keys
 * - Transaction-safe insertions and deletions
 * - Structural integrity validation
 * - Search, range queries, and reporting
 *
 * Design decision:
 * PostgreSQL is a relational database, not an in-memory
 * pointer-based AVL implementation.
 *
 * This implementation maintains a relational tree and
 * rebuilds its balanced structure from sorted keys after
 * mutations. It preserves AVL invariants but uses O(n)
 * rebuilding rather than O(log n) incremental insertion.
 */

DROP SCHEMA IF EXISTS avl_catalog CASCADE;

CREATE SCHEMA avl_catalog;

SET search_path TO avl_catalog, public;


-- =========================================================
-- 1. DOMAIN TABLES
-- =========================================================

CREATE TABLE avl_trees (
    tree_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    tree_name VARCHAR(150) NOT NULL UNIQUE,

    root_node_id BIGINT,

    node_count INTEGER NOT NULL DEFAULT 0,

    tree_height INTEGER NOT NULL DEFAULT 0,

    version BIGINT NOT NULL DEFAULT 0,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT positive_node_count
        CHECK (node_count >= 0),

    CONSTRAINT nonnegative_tree_height
        CHECK (tree_height >= 0)
);


CREATE TABLE avl_nodes (
    node_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    tree_id BIGINT NOT NULL
        REFERENCES avl_trees(tree_id)
        ON DELETE CASCADE,

    node_key BIGINT NOT NULL,

    parent_id BIGINT,

    left_child_id BIGINT,

    right_child_id BIGINT,

    node_height INTEGER NOT NULL DEFAULT 1,

    balance_factor INTEGER NOT NULL DEFAULT 0,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_tree_key
        UNIQUE (tree_id, node_key),

    CONSTRAINT unique_tree_node
        UNIQUE (tree_id, node_id),

    CONSTRAINT positive_node_height
        CHECK (node_height >= 1),

    CONSTRAINT valid_balance_factor
        CHECK (balance_factor BETWEEN -1 AND 1),

    CONSTRAINT no_self_parent
        CHECK (parent_id IS DISTINCT FROM node_id),

    CONSTRAINT no_self_left
        CHECK (left_child_id IS DISTINCT FROM node_id),

    CONSTRAINT no_self_right
        CHECK (right_child_id IS DISTINCT FROM node_id),

    CONSTRAINT distinct_children
        CHECK (
            left_child_id IS NULL
            OR right_child_id IS NULL
            OR left_child_id <> right_child_id
        ),

    CONSTRAINT parent_fk
        FOREIGN KEY (tree_id, parent_id)
        REFERENCES avl_nodes(tree_id, node_id)
        DEFERRABLE INITIALLY DEFERRED,

    CONSTRAINT left_child_fk
        FOREIGN KEY (tree_id, left_child_id)
        REFERENCES avl_nodes(tree_id, node_id)
        DEFERRABLE INITIALLY DEFERRED,

    CONSTRAINT right_child_fk
        FOREIGN KEY (tree_id, right_child_id)
        REFERENCES avl_nodes(tree_id, node_id)
        DEFERRABLE INITIALLY DEFERRED
);


-- The root must belong to its own tree.
ALTER TABLE avl_trees
ADD CONSTRAINT root_node_fk
FOREIGN KEY (tree_id, root_node_id)
REFERENCES avl_nodes(tree_id, node_id)
DEFERRABLE INITIALLY DEFERRED;


CREATE INDEX idx_avl_nodes_parent
ON avl_nodes(tree_id, parent_id);

CREATE INDEX idx_avl_nodes_left
ON avl_nodes(tree_id, left_child_id);

CREATE INDEX idx_avl_nodes_right
ON avl_nodes(tree_id, right_child_id);

CREATE INDEX idx_avl_nodes_key
ON avl_nodes(tree_id, node_key);


-- =========================================================
-- 2. BALANCE AND HEIGHT FUNCTIONS
-- =========================================================

CREATE OR REPLACE FUNCTION avl_node_height(
    p_tree_id BIGINT,
    p_node_id BIGINT
)
RETURNS INTEGER
LANGUAGE SQL
STABLE
AS $$
    SELECT COALESCE(
        (
            SELECT node_height
            FROM avl_nodes
            WHERE tree_id = p_tree_id
              AND node_id = p_node_id
        ),
        0
    );
$$;


CREATE OR REPLACE FUNCTION avl_calculate_balance(
    p_tree_id BIGINT,
    p_node_id BIGINT
)
RETURNS INTEGER
LANGUAGE SQL
STABLE
AS $$
    SELECT
        avl_node_height(p_tree_id, left_child_id)
        -
        avl_node_height(p_tree_id, right_child_id)
    FROM avl_nodes
    WHERE tree_id = p_tree_id
      AND node_id = p_node_id;
$$;


-- =========================================================
-- 3. RELATIONAL ROTATION OPERATIONS
-- =========================================================

CREATE OR REPLACE FUNCTION avl_rotate_right(
    p_tree_id BIGINT,
    p_root_id BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_parent BIGINT;
    v_left BIGINT;
    v_middle BIGINT;
    v_height INTEGER;
BEGIN
    SELECT parent_id, left_child_id
    INTO v_parent, v_left
    FROM avl_nodes
    WHERE tree_id = p_tree_id
      AND node_id = p_root_id
    FOR UPDATE;

    IF NOT FOUND OR v_left IS NULL THEN
        RAISE EXCEPTION 'Invalid right rotation at node %',
            p_root_id;
    END IF;

    SELECT right_child_id
    INTO v_middle
    FROM avl_nodes
    WHERE tree_id = p_tree_id
      AND node_id = v_left
    FOR UPDATE;

    -- Promote the left child.
    UPDATE avl_nodes
    SET parent_id = v_parent,
        right_child_id = p_root_id
    WHERE tree_id = p_tree_id
      AND node_id = v_left;

    -- Move the middle subtree.
    UPDATE avl_nodes
    SET parent_id = v_left
    WHERE tree_id = p_tree_id
      AND node_id = p_root_id;

    UPDATE avl_nodes
    SET left_child_id = v_middle
    WHERE tree_id = p_tree_id
      AND node_id = p_root_id;

    IF v_middle IS NOT NULL THEN
        UPDATE avl_nodes
        SET parent_id = p_root_id
        WHERE tree_id = p_tree_id
          AND node_id = v_middle;
    END IF;

    -- Replace the old root in its parent.
    IF v_parent IS NOT NULL THEN
        UPDATE avl_nodes
        SET left_child_id =
            CASE
                WHEN left_child_id = p_root_id
                THEN v_left
                ELSE left_child_id
            END,
            right_child_id =
            CASE
                WHEN right_child_id = p_root_id
                THEN v_left
                ELSE right_child_id
            END
        WHERE tree_id = p_tree_id
          AND node_id = v_parent;
    ELSE
        UPDATE avl_trees
        SET root_node_id = v_left
        WHERE tree_id = p_tree_id;
    END IF;

    -- Recalculate old root height.
    SELECT 1 + GREATEST(
        avl_node_height(p_tree_id, left_child_id),
        avl_node_height(p_tree_id, right_child_id)
    )
    INTO v_height
    FROM avl_nodes
    WHERE tree_id = p_tree_id
      AND node_id = p_root_id;

    UPDATE avl_nodes
    SET node_height = v_height,
        balance_factor = avl_calculate_balance(
            p_tree_id, p_root_id
        )
    WHERE tree_id = p_tree_id
      AND node_id = p_root_id;

    -- Recalculate promoted root height.
    SELECT 1 + GREATEST(
        avl_node_height(p_tree_id, left_child_id),
        avl_node_height(p_tree_id, right_child_id)
    )
    INTO v_height
    FROM avl_nodes
    WHERE tree_id = p_tree_id
      AND node_id = v_left;

    UPDATE avl_nodes
    SET node_height = v_height,
        balance_factor = avl_calculate_balance(
            p_tree_id, v_left
        )
    WHERE tree_id = p_tree_id
      AND node_id = v_left;

    RETURN v_left;
END;
$$;


CREATE OR REPLACE FUNCTION avl_rotate_left(
    p_tree_id BIGINT,
    p_root_id BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_parent BIGINT;
    v_right BIGINT;
    v_middle BIGINT;
    v_height INTEGER;
BEGIN
    SELECT parent_id, right_child_id
    INTO v_parent, v_right
    FROM avl_nodes
    WHERE tree_id = p_tree_id
      AND node_id = p_root_id
    FOR UPDATE;

    IF NOT FOUND OR v_right IS NULL THEN
        RAISE EXCEPTION 'Invalid left rotation at node %',
            p_root_id;
    END IF;

    SELECT left_child_id
    INTO v_middle
    FROM avl_nodes
    WHERE tree_id = p_tree_id
      AND node_id = v_right
    FOR UPDATE;

    UPDATE avl_nodes
    SET parent_id = v_parent,
        left_child_id = p_root_id
    WHERE tree_id = p_tree_id
      AND node_id = v_right;

    UPDATE avl_nodes
    SET parent_id = v_right,
        right_child_id = v_middle
    WHERE tree_id = p_tree_id
      AND node_id = p_root_id;

    IF v_middle IS NOT NULL THEN
        UPDATE avl_nodes
        SET parent_id = p_root_id
        WHERE tree_id = p_tree_id
          AND node_id = v_middle;
    END IF;

    IF v_parent IS NOT NULL THEN
        UPDATE avl_nodes
        SET left_child_id =
            CASE
                WHEN left_child_id = p_root_id
                THEN v_right
                ELSE left_child_id
            END,
            right_child_id =
            CASE
                WHEN right_child_id = p_root_id
                THEN v_right
                ELSE right_child_id
            END
        WHERE tree_id = p_tree_id
          AND node_id = v_parent;
    ELSE
        UPDATE avl_trees
        SET root_node_id = v_right
        WHERE tree_id = p_tree_id;
    END IF;

    SELECT 1 + GREATEST(
        avl_node_height(p_tree_id, left_child_id),
        avl_node_height(p_tree_id, right_child_id)
    )
    INTO v_height
    FROM avl_nodes
    WHERE tree_id = p_tree_id
      AND node_id = p_root_id;

    UPDATE avl_nodes
    SET node_height = v_height,
        balance_factor = avl_calculate_balance(
            p_tree_id, p_root_id
        )
    WHERE tree_id = p_tree_id
      AND node_id = p_root_id;

    SELECT 1 + GREATEST(
        avl_node_height(p_tree_id, left_child_id),
        avl_node_height(p_tree_id, right_child_id)
    )
    INTO v_height
    FROM avl_nodes
    WHERE tree_id = p_tree_id
      AND node_id = v_right;

    UPDATE avl_nodes
    SET node_height = v_height,
        balance_factor = avl_calculate_balance(
            p_tree_id, v_right
        )
    WHERE tree_id = p_tree_id
      AND node_id = v_right;

    RETURN v_right;
END;
$$;


-- =========================================================
-- 4. TREE REBUILDING
-- =========================================================

CREATE OR REPLACE FUNCTION avl_build_balanced(
    p_tree_id BIGINT,
    p_keys BIGINT[],
    p_low INTEGER,
    p_high INTEGER,
    p_parent_id BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_middle INTEGER;
    v_key BIGINT;
    v_node_id BIGINT;
    v_left BIGINT;
    v_right BIGINT;
    v_height INTEGER;
    v_balance INTEGER;
BEGIN
    IF p_low > p_high THEN
        RETURN NULL;
    END IF;

    v_middle := (p_low + p_high) / 2;
    v_key := p_keys[v_middle];

    INSERT INTO avl_nodes (
        tree_id,
        node_key,
        parent_id,
        node_height,
        balance_factor
    )
    VALUES (
        p_tree_id,
        v_key,
        p_parent_id,
        1,
        0
    )
    RETURNING node_id INTO v_node_id;

    v_left := avl_build_balanced(
        p_tree_id,
        p_keys,
        p_low,
        v_middle - 1,
        v_node_id
    );

    v_right := avl_build_balanced(
        p_tree_id,
        p_keys,
        v_middle + 1,
        p_high,
        v_node_id
    );

    v_height := 1 + GREATEST(
        avl_node_height(p_tree_id, v_left),
        avl_node_height(p_tree_id, v_right)
    );

    v_balance :=
        avl_node_height(p_tree_id, v_left)
        -
        avl_node_height(p_tree_id, v_right);

    UPDATE avl_nodes
    SET left_child_id = v_left,
        right_child_id = v_right,
        node_height = v_height,
        balance_factor = v_balance
    WHERE tree_id = p_tree_id
      AND node_id = v_node_id;

    RETURN v_node_id;
END;
$$;


CREATE OR REPLACE PROCEDURE avl_rebuild(
    p_tree_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_keys BIGINT[];
    v_count INTEGER;
    v_root BIGINT;
    v_height INTEGER;
BEGIN
    PERFORM 1
    FROM avl_trees
    WHERE tree_id = p_tree_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Tree % does not exist', p_tree_id;
    END IF;

    SELECT COALESCE(
        array_agg(node_key ORDER BY node_key),
        ARRAY[]::BIGINT[]
    )
    INTO v_keys
    FROM avl_nodes
    WHERE tree_id = p_tree_id;

    v_count := cardinality(v_keys);

    -- Remove the previous relational topology.
    DELETE FROM avl_nodes
    WHERE tree_id = p_tree_id;

    -- Reconstruct a balanced topology from sorted keys.
    v_root := avl_build_balanced(
        p_tree_id,
        v_keys,
        1,
        v_count,
        NULL
    );

    v_height := avl_node_height(p_tree_id, v_root);

    UPDATE avl_trees
    SET root_node_id = v_root,
        node_count = v_count,
        tree_height = v_height,
        version = version + 1,
        updated_at = CURRENT_TIMESTAMP
    WHERE tree_id = p_tree_id;
END;
$$;


-- =========================================================
-- 5. TREE INSERTION AND DELETION
-- =========================================================

CREATE OR REPLACE PROCEDURE avl_insert(
    p_tree_id BIGINT,
    p_key BIGINT
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_key IS NULL THEN
        RAISE EXCEPTION 'Node key cannot be NULL';
    END IF;

    PERFORM 1
    FROM avl_trees
    WHERE tree_id = p_tree_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Tree % does not exist', p_tree_id;
    END IF;

    IF EXISTS (
        SELECT 1
        FROM avl_nodes
        WHERE tree_id = p_tree_id
          AND node_key = p_key
    ) THEN
        RAISE EXCEPTION
            'Duplicate key % in tree %',
            p_key,
            p_tree_id;
    END IF;

    -- Insert the key before rebuilding its topology.
    INSERT INTO avl_nodes (
        tree_id,
        node_key
    )
    VALUES (
        p_tree_id,
        p_key
    );

    CALL avl_rebuild(p_tree_id);
END;
$$;


CREATE OR REPLACE PROCEDURE avl_delete(
    p_tree_id BIGINT,
    p_key BIGINT
)
LANGUAGE plpgsql
AS $$
BEGIN
    PERFORM 1
    FROM avl_trees
    WHERE tree_id = p_tree_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Tree % does not exist', p_tree_id;
    END IF;

    DELETE FROM avl_nodes
    WHERE tree_id = p_tree_id
      AND node_key = p_key;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Key % does not exist', p_key;
    END IF;

    CALL avl_rebuild(p_tree_id);
END;
$$;


-- =========================================================
-- 6. TREE CREATION
-- =========================================================

INSERT INTO avl_trees (tree_name)
VALUES
    ('product_inventory'),
    ('customer_reference'),
    ('rotation_demonstration');


-- =========================================================
-- 7. ROTATION DEMONSTRATIONS
-- =========================================================

-- Directly demonstrate the relational LL rotation.
-- These nodes represent:
--
--       30
--      /
--     20
--    /
--   10
--
-- Expected result:
--
--       20
--      /  \
--     10   30

DO $$
DECLARE
    v_tree BIGINT;
    v_10 BIGINT;
    v_20 BIGINT;
    v_30 BIGINT;
    v_new_root BIGINT;
BEGIN
    SELECT tree_id
    INTO v_tree
    FROM avl_trees
    WHERE tree_name = 'rotation_demonstration';

    INSERT INTO avl_nodes(tree_id, node_key)
    VALUES (v_tree, 30)
    RETURNING node_id INTO v_30;

    INSERT INTO avl_nodes(tree_id, node_key, parent_id)
    VALUES (v_tree, 20, v_30)
    RETURNING node_id INTO v_20;

    INSERT INTO avl_nodes(tree_id, node_key, parent_id)
    VALUES (v_tree, 10, v_20)
    RETURNING node_id INTO v_10;

    UPDATE avl_nodes
    SET left_child_id = v_20,
        node_height = 3,
        balance_factor = 2
    WHERE node_id = v_30;

    UPDATE avl_nodes
    SET left_child_id = v_10,
        node_height = 2,
        balance_factor = 1
    WHERE node_id = v_20;

    UPDATE avl_trees
    SET root_node_id = v_30,
        node_count = 3,
        tree_height = 3
    WHERE tree_id = v_tree;

    v_new_root := avl_rotate_right(v_tree, v_30);

    UPDATE avl_trees
    SET tree_height = 2
    WHERE tree_id = v_tree;

    RAISE NOTICE 'LL rotation new root node ID: %',
        v_new_root;
END;
$$;


-- =========================================================
-- 8. PRODUCTION-LIKE INVENTORY WORKFLOW
-- =========================================================

DO $$
DECLARE
    v_tree BIGINT;
BEGIN
    SELECT tree_id
    INTO v_tree
    FROM avl_trees
    WHERE tree_name = 'product_inventory';

    CALL avl_insert(v_tree, 1001);
    CALL avl_insert(v_tree, 501);
    CALL avl_insert(v_tree, 1501);
    CALL avl_insert(v_tree, 251);
    CALL avl_insert(v_tree, 751);
    CALL avl_insert(v_tree, 1251);
    CALL avl_insert(v_tree, 1751);
    CALL avl_insert(v_tree, 101);
    CALL avl_insert(v_tree, 351);
    CALL avl_insert(v_tree, 651);
    CALL avl_insert(v_tree, 851);
    CALL avl_insert(v_tree, 1101);
    CALL avl_insert(v_tree, 1401);
    CALL avl_insert(v_tree, 1601);
    CALL avl_insert(v_tree, 1901);
END;
$$;


-- =========================================================
-- 9. SEARCH FUNCTIONS AND REPORTING VIEWS
-- =========================================================

CREATE OR REPLACE FUNCTION avl_search(
    p_tree_id BIGINT,
    p_key BIGINT
)
RETURNS TABLE (
    node_id BIGINT,
    node_key BIGINT,
    node_height INTEGER,
    balance_factor INTEGER
)
LANGUAGE SQL
STABLE
AS $$
    SELECT
        n.node_id,
        n.node_key,
        n.node_height,
        n.balance_factor
    FROM avl_nodes n
    WHERE n.tree_id = p_tree_id
      AND n.node_key = p_key;
$$;


CREATE OR REPLACE VIEW avl_tree_report AS
SELECT
    t.tree_id,
    t.tree_name,
    t.root_node_id,
    root.node_key AS root_key,
    t.node_count,
    t.tree_height,
    t.version,
    t.updated_at
FROM avl_trees t
LEFT JOIN avl_nodes root
    ON root.tree_id = t.tree_id
   AND root.node_id = t.root_node_id;


CREATE OR REPLACE VIEW avl_node_report AS
SELECT
    n.tree_id,
    n.node_id,
    n.node_key,
    parent.node_key AS parent_key,
    left_node.node_key AS left_key,
    right_node.node_key AS right_key,
    n.node_height,
    n.balance_factor,
    CASE
        WHEN n.balance_factor = 0 THEN 'BALANCED'
        WHEN n.balance_factor = 1 THEN 'LEFT-HEAVY'
        WHEN n.balance_factor = -1 THEN 'RIGHT-HEAVY'
        ELSE 'INVALID'
    END AS balance_status
FROM avl_nodes n
LEFT JOIN avl_nodes parent
    ON parent.tree_id = n.tree_id
   AND parent.node_id = n.parent_id
LEFT JOIN avl_nodes left_node
    ON left_node.tree_id = n.tree_id
   AND left_node.node_id = n.left_child_id
LEFT JOIN avl_nodes right_node
    ON right_node.tree_id = n.tree_id
   AND right_node.node_id = n.right_child_id;


-- =========================================================
-- 10. INTEGRITY VALIDATION
-- =========================================================

CREATE OR REPLACE FUNCTION avl_validate(
    p_tree_id BIGINT
)
RETURNS TABLE (
    is_valid BOOLEAN,
    actual_nodes BIGINT,
    actual_height INTEGER,
    invalid_balance_nodes BIGINT,
    invalid_parent_links BIGINT,
    unreachable_nodes BIGINT,
    invalid_bst_nodes BIGINT
)
LANGUAGE SQL
STABLE
AS $$
    WITH RECURSIVE reachable AS (
        SELECT
            n.node_id,
            n.node_key,
            n.left_child_id,
            n.right_child_id,
            n.node_height,
            n.balance_factor,
            1 AS depth,
            ARRAY[n.node_id]::BIGINT[] AS visited,
            NULL::BIGINT AS expected_parent
        FROM avl_trees t
        JOIN avl_nodes n
            ON n.tree_id = t.tree_id
           AND n.node_id = t.root_node_id
        WHERE t.tree_id = p_tree_id

        UNION ALL

        SELECT
            child.node_id,
            child.node_key,
            child.left_child_id,
            child.right_child_id,
            child.node_height,
            child.balance_factor,
            parent.depth + 1,
            parent.visited || child.node_id,
            parent.node_id
        FROM reachable parent
        JOIN avl_nodes child
            ON child.tree_id = p_tree_id
           AND child.node_id IN (
               parent.left_child_id,
               parent.right_child_id
           )
        WHERE NOT child.node_id = ANY(parent.visited)
    ),
    totals AS (
        SELECT
            COUNT(*)::BIGINT AS actual_nodes,
            COALESCE(MAX(depth), 0)::INTEGER AS actual_height,
            COUNT(*) FILTER (
                WHERE ABS(balance_factor) > 1
            )::BIGINT AS invalid_balance_nodes,
            COUNT(*) FILTER (
                WHERE expected_parent IS DISTINCT FROM (
                    SELECT parent_id
                    FROM avl_nodes x
                    WHERE x.node_id = reachable.node_id
                )
            )::BIGINT AS invalid_parent_links,
            COUNT(*) FILTER (
                WHERE
                    (left_child_id IS NOT NULL
                     AND node_key <= (
                        SELECT node_key
                        FROM avl_nodes x
                        WHERE x.node_id = left_child_id
                     ))
                    OR
                    (right_child_id IS NOT NULL
                     AND node_key >= (
                        SELECT node_key
                        FROM avl_nodes x
                        WHERE x.node_id = right_child_id
                     ))
            )::BIGINT AS invalid_bst_nodes
        FROM reachable
    ),
    all_nodes AS (
        SELECT COUNT(*)::BIGINT AS total
        FROM avl_nodes
        WHERE tree_id = p_tree_id
    )
    SELECT
        (
            totals.actual_nodes = all_nodes.total
            AND totals.invalid_balance_nodes = 0
            AND totals.invalid_parent_links = 0
            AND totals.invalid_bst_nodes = 0
            AND totals.actual_nodes = (
                SELECT node_count
                FROM avl_trees
                WHERE tree_id = p_tree_id
            )
        ),
        totals.actual_nodes,
        totals.actual_height,
        totals.invalid_balance_nodes,
        totals.invalid_parent_links,
        all_nodes.total - totals.actual_nodes,
        totals.invalid_bst_nodes
    FROM totals
    CROSS JOIN all_nodes;
$$;


-- =========================================================
-- 11. AGGREGATION AND TREE ANALYSIS
-- =========================================================

-- Tree-level metrics.
SELECT *
FROM avl_tree_report
ORDER BY tree_id;


-- Individual node relationships.
SELECT *
FROM avl_node_report
WHERE tree_id = (
    SELECT tree_id
    FROM avl_trees
    WHERE tree_name = 'product_inventory'
)
ORDER BY node_key;


-- Identify the root and leaf nodes.
SELECT
    tree_name,
    COUNT(*) FILTER (
        WHERE parent_id IS NULL
    ) AS root_candidates,
    COUNT(*) FILTER (
        WHERE left_child_id IS NULL
          AND right_child_id IS NULL
    ) AS leaf_nodes,
    COUNT(*) FILTER (
        WHERE left_child_id IS NOT NULL
          AND right_child_id IS NOT NULL
    ) AS two_child_nodes
FROM avl_trees t
LEFT JOIN avl_nodes n
    ON n.tree_id = t.tree_id
GROUP BY tree_name;


-- Search for a specific inventory identifier.
SELECT *
FROM avl_search(
    (
        SELECT tree_id
        FROM avl_trees
        WHERE tree_name = 'product_inventory'
    ),
    751
);


-- Retrieve a key range.
SELECT node_key
FROM avl_nodes
WHERE tree_id = (
    SELECT tree_id
    FROM avl_trees
    WHERE tree_name = 'product_inventory'
)
AND node_key BETWEEN 500 AND 1500
ORDER BY node_key;


-- =========================================================
-- 12. RECURSIVE IN-ORDER TRAVERSAL
-- =========================================================

WITH RECURSIVE traversal AS (
    SELECT
        n.node_id,
        n.node_key,
        n.left_child_id,
        n.right_child_id,
        ARRAY[]::BIGINT[] AS ancestors
    FROM avl_nodes n
    WHERE n.tree_id = (
        SELECT tree_id
        FROM avl_trees
        WHERE tree_name = 'product_inventory'
    )
    AND n.parent_id IS NULL

    UNION ALL

    SELECT
        child.node_id,
        child.node_key,
        child.left_child_id,
        child.right_child_id,
        parent.ancestors || parent.node_id
    FROM traversal parent
    JOIN avl_nodes child
        ON child.node_id IN (
            parent.left_child_id,
            parent.right_child_id
        )
    WHERE NOT child.node_id = ANY(parent.ancestors)
)
SELECT node_key
FROM traversal
ORDER BY node_key;


-- =========================================================
-- 13. VALIDATION REPORT
-- =========================================================

SELECT
    t.tree_name,
    validation.*
FROM avl_trees t
CROSS JOIN LATERAL avl_validate(t.tree_id) validation
ORDER BY t.tree_id;


-- =========================================================
-- 14. TRANSACTIONAL DELETION
-- =========================================================

BEGIN;

DO $$
DECLARE
    v_tree BIGINT;
BEGIN
    SELECT tree_id
    INTO v_tree
    FROM avl_trees
    WHERE tree_name = 'product_inventory';

    CALL avl_delete(v_tree, 1001);

    IF NOT (
        SELECT is_valid
        FROM avl_validate(v_tree)
    ) THEN
        RAISE EXCEPTION 'AVL validation failed after deletion';
    END IF;
END;
$$;

COMMIT;


-- =========================================================
-- 15. FAILURE HANDLING
-- =========================================================

-- Duplicate insertion is rejected.
-- The exception is isolated in a nested transaction block.

DO $$
DECLARE
    v_tree BIGINT;
BEGIN
    SELECT tree_id
    INTO v_tree
    FROM avl_trees
    WHERE tree_name = 'product_inventory';

    BEGIN
        CALL avl_insert(v_tree, 501);
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Duplicate insertion rejected: %',
                SQLERRM;
    END;
END;
$$;


-- Nonexistent key deletion is rejected.
DO $$
DECLARE
    v_tree BIGINT;
BEGIN
    SELECT tree_id
    INTO v_tree
    FROM avl_trees
    WHERE tree_name = 'product_inventory';

    BEGIN
        CALL avl_delete(v_tree, 999999);
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Invalid deletion rejected: %',
                SQLERRM;
    END;
END;
$$;


-- =========================================================
-- 16. FINAL VALIDATION
-- =========================================================

SELECT
    tree_name,
    node_count,
    tree_height,
    version
FROM avl_trees
ORDER BY tree_id;


SELECT
    t.tree_name,
    v.is_valid,
    v.actual_nodes,
    v.actual_height,
    v.invalid_balance_nodes,
    v.invalid_parent_links,
    v.unreachable_nodes,
    v.invalid_bst_nodes
FROM avl_trees t
CROSS JOIN LATERAL avl_validate(t.tree_id) v
ORDER BY t.tree_id;


-- End of AVL tree implementation.
