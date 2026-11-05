-- ============================================================
-- BINARY SEARCH TREE: POSTGRESQL IMPLEMENTATION
-- ============================================================
-- Model:
--   tree_registry
--       |
--       +---- tree_nodes
--                |
--                +---- parent_id
--                +---- position (LEFT / RIGHT)
--
-- Unique integer keys per tree.
-- Duplicate keys are rejected.
-- Parent-child relationships are explicitly stored.
--
-- Execute using PostgreSQL 14 or later.
-- ============================================================

BEGIN;

DROP SCHEMA IF EXISTS bst_lab CASCADE;

CREATE SCHEMA bst_lab;

SET search_path TO bst_lab, public;

-- ------------------------------------------------------------
-- 1. TREE REGISTRY
-- ------------------------------------------------------------

CREATE TABLE tree_registry (
    tree_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tree_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------
-- 2. TREE NODES
-- ------------------------------------------------------------

CREATE TABLE tree_nodes (
    node_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    tree_id BIGINT NOT NULL
        REFERENCES tree_registry(tree_id)
        ON DELETE CASCADE,

    node_key BIGINT NOT NULL,

    parent_id BIGINT,

    position VARCHAR(5)
        CHECK (position IN ('LEFT', 'RIGHT')),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_tree_node_key
        UNIQUE (tree_id, node_key)
        DEFERRABLE INITIALLY IMMEDIATE,

    CONSTRAINT uq_tree_parent_position
        UNIQUE (tree_id, parent_id, position),

    CONSTRAINT uq_tree_node_reference
        UNIQUE (tree_id, node_id),

    CONSTRAINT fk_tree_parent
        FOREIGN KEY (tree_id, parent_id)
        REFERENCES tree_nodes(tree_id, node_id)
        DEFERRABLE INITIALLY IMMEDIATE,

    CONSTRAINT ck_root_position
        CHECK (
            (parent_id IS NULL AND position IS NULL)
            OR
            (parent_id IS NOT NULL AND position IS NOT NULL)
        ),

    CONSTRAINT ck_not_self_parent
        CHECK (parent_id IS DISTINCT FROM node_id)
);

-- A tree can have only one root.
CREATE UNIQUE INDEX uq_tree_single_root
    ON tree_nodes(tree_id)
    WHERE parent_id IS NULL;

CREATE INDEX idx_tree_parent
    ON tree_nodes(tree_id, parent_id);

CREATE INDEX idx_tree_key
    ON tree_nodes(tree_id, node_key);

-- ------------------------------------------------------------
-- 3. VALIDATE TREE STRUCTURE ON INSERT
-- ------------------------------------------------------------
-- This trigger verifies:
--   * A root is the first node in its tree.
--   * A left child is smaller than its parent.
--   * A right child is greater than its parent.
--   * Every ancestor's ordering boundary is respected.
--   * A node cannot be attached to an unrelated tree.
--
-- Operational writes should use the supplied functions.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_bst_node()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    parent_key BIGINT;
    current_parent BIGINT;
    current_key BIGINT;
    current_position VARCHAR(5);
    lower_bound BIGINT;
    upper_bound BIGINT;
    steps INTEGER := 0;
BEGIN
    IF TG_OP = 'UPDATE' THEN
        IF NEW.tree_id IS DISTINCT FROM OLD.tree_id
           OR NEW.node_key IS DISTINCT FROM OLD.node_key
           OR NEW.parent_id IS DISTINCT FROM OLD.parent_id
           OR NEW.position IS DISTINCT FROM OLD.position
        THEN
            RAISE EXCEPTION
                'Direct structural updates are prohibited. Use BST functions.';
        END IF;

        RETURN NEW;
    END IF;

    IF NEW.parent_id IS NULL THEN
        IF EXISTS (
            SELECT 1
            FROM tree_nodes
            WHERE tree_id = NEW.tree_id
        ) THEN
            RAISE EXCEPTION
                'A tree can have only one root.';
        END IF;

        RETURN NEW;
    END IF;

    SELECT node_key
    INTO parent_key
    FROM tree_nodes
    WHERE tree_id = NEW.tree_id
      AND node_id = NEW.parent_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Parent node does not exist.';
    END IF;

    IF NEW.position = 'LEFT' AND NEW.node_key >= parent_key THEN
        RAISE EXCEPTION
            'Left child key must be smaller than parent key.';
    END IF;

    IF NEW.position = 'RIGHT' AND NEW.node_key <= parent_key THEN
        RAISE EXCEPTION
            'Right child key must be greater than parent key.';
    END IF;

    -- Walk upward to verify every ancestor boundary.
    current_parent := NEW.parent_id;

    WHILE current_parent IS NOT NULL LOOP
        steps := steps + 1;

        IF steps > 100000 THEN
            RAISE EXCEPTION 'Invalid cyclic parent structure.';
        END IF;

        SELECT node_key, parent_id, position
        INTO current_key, current_parent, current_position
        FROM tree_nodes
        WHERE tree_id = NEW.tree_id
          AND node_id = current_parent;

        IF current_position = 'LEFT' THEN
            IF NEW.node_key >= current_key THEN
                RAISE EXCEPTION
                    'Node violates an ancestor left-subtree boundary.';
            END IF;
        ELSIF current_position = 'RIGHT' THEN
            IF NEW.node_key <= current_key THEN
                RAISE EXCEPTION
                    'Node violates an ancestor right-subtree boundary.';
            END IF;
        END IF;
    END LOOP;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_bst_node
BEFORE INSERT OR UPDATE ON tree_nodes
FOR EACH ROW
EXECUTE FUNCTION validate_bst_node();

-- ------------------------------------------------------------
-- 4. CREATE A TREE
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION create_tree(
    p_name VARCHAR,
    p_description TEXT DEFAULT NULL
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    result_id BIGINT;
BEGIN
    IF p_name IS NULL OR length(trim(p_name)) = 0 THEN
        RAISE EXCEPTION 'Tree name cannot be empty.';
    END IF;

    INSERT INTO tree_registry(tree_name, description)
    VALUES (trim(p_name), p_description)
    RETURNING tree_id INTO result_id;

    RETURN result_id;
END;
$$;

-- ------------------------------------------------------------
-- 5. INSERT A NODE
-- ------------------------------------------------------------
-- Finds the correct insertion position by following
-- the BST ordering rules.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION bst_insert(
    p_tree_id BIGINT,
    p_key BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    current_node tree_nodes%ROWTYPE;
    new_position VARCHAR(5);
    new_parent BIGINT;
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM tree_registry
        WHERE tree_id = p_tree_id
    ) THEN
        RAISE EXCEPTION 'Tree % does not exist.', p_tree_id;
    END IF;

    IF EXISTS (
        SELECT 1
        FROM tree_nodes
        WHERE tree_id = p_tree_id
          AND node_key = p_key
    ) THEN
        RETURN FALSE;
    END IF;

    SELECT *
    INTO current_node
    FROM tree_nodes
    WHERE tree_id = p_tree_id
      AND parent_id IS NULL;

    IF NOT FOUND THEN
        INSERT INTO tree_nodes(tree_id, node_key)
        VALUES (p_tree_id, p_key);

        RETURN TRUE;
    END IF;

    LOOP
        IF p_key < current_node.node_key THEN
            new_position := 'LEFT';

            IF NOT EXISTS (
                SELECT 1
                FROM tree_nodes
                WHERE tree_id = p_tree_id
                  AND parent_id = current_node.node_id
                  AND position = 'LEFT'
            ) THEN
                new_parent := current_node.node_id;
                EXIT;
            END IF;

            SELECT *
            INTO current_node
            FROM tree_nodes
            WHERE tree_id = p_tree_id
              AND parent_id = current_node.node_id
              AND position = 'LEFT';

        ELSE
            new_position := 'RIGHT';

            IF NOT EXISTS (
                SELECT 1
                FROM tree_nodes
                WHERE tree_id = p_tree_id
                  AND parent_id = current_node.node_id
                  AND position = 'RIGHT'
            ) THEN
                new_parent := current_node.node_id;
                EXIT;
            END IF;

            SELECT *
            INTO current_node
            FROM tree_nodes
            WHERE tree_id = p_tree_id
              AND parent_id = current_node.node_id
              AND position = 'RIGHT';
        END IF;
    END LOOP;

    INSERT INTO tree_nodes(
        tree_id,
        node_key,
        parent_id,
        position
    )
    VALUES (
        p_tree_id,
        p_key,
        new_parent,
        new_position
    );

    RETURN TRUE;
END;
$$;

-- ------------------------------------------------------------
-- 6. SEARCH
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION bst_search(
    p_tree_id BIGINT,
    p_key BIGINT
)
RETURNS TABLE (
    found_node_id BIGINT,
    found_key BIGINT,
    comparisons INTEGER
)
LANGUAGE plpgsql
AS $$
DECLARE
    current_node tree_nodes%ROWTYPE;
    total_comparisons INTEGER := 0;
BEGIN
    SELECT *
    INTO current_node
    FROM tree_nodes
    WHERE tree_id = p_tree_id
      AND parent_id IS NULL;

    WHILE FOUND LOOP
        total_comparisons := total_comparisons + 1;

        IF current_node.node_key = p_key THEN
            RETURN QUERY
            SELECT current_node.node_id,
                   current_node.node_key,
                   total_comparisons;

            RETURN;
        END IF;

        IF p_key < current_node.node_key THEN
            SELECT *
            INTO current_node
            FROM tree_nodes
            WHERE tree_id = p_tree_id
              AND parent_id = current_node.node_id
              AND position = 'LEFT';
        ELSE
            SELECT *
            INTO current_node
            FROM tree_nodes
            WHERE tree_id = p_tree_id
              AND parent_id = current_node.node_id
              AND position = 'RIGHT';
        END IF;
    END LOOP;

    RETURN QUERY
    SELECT NULL::BIGINT, NULL::BIGINT, total_comparisons;
END;
$$;

-- ------------------------------------------------------------
-- 7. MINIMUM AND MAXIMUM
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION bst_extreme(
    p_tree_id BIGINT,
    p_find_minimum BOOLEAN
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    current_node tree_nodes%ROWTYPE;
    next_position VARCHAR(5);
BEGIN
    SELECT *
    INTO current_node
    FROM tree_nodes
    WHERE tree_id = p_tree_id
      AND parent_id IS NULL;

    IF NOT FOUND THEN
        RETURN NULL;
    END IF;

    next_position := CASE
        WHEN p_find_minimum THEN 'LEFT'
        ELSE 'RIGHT'
    END;

    LOOP
        SELECT *
        INTO current_node
        FROM tree_nodes
        WHERE tree_id = p_tree_id
          AND parent_id = current_node.node_id
          AND position = next_position;

        EXIT WHEN NOT FOUND;
    END LOOP;

    RETURN current_node.node_key;
END;
$$;

-- ------------------------------------------------------------
-- 8. PREDECESSOR
-- ------------------------------------------------------------
-- Greatest key strictly smaller than the supplied key.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION bst_predecessor(
    p_tree_id BIGINT,
    p_key BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    current_node tree_nodes%ROWTYPE;
    candidate BIGINT;
BEGIN
    SELECT *
    INTO current_node
    FROM tree_nodes
    WHERE tree_id = p_tree_id
      AND parent_id IS NULL;

    WHILE FOUND LOOP
        IF current_node.node_key < p_key THEN
            candidate := current_node.node_key;

            SELECT *
            INTO current_node
            FROM tree_nodes
            WHERE tree_id = p_tree_id
              AND parent_id = current_node.node_id
              AND position = 'RIGHT';
        ELSE
            SELECT *
            INTO current_node
            FROM tree_nodes
            WHERE tree_id = p_tree_id
              AND parent_id = current_node.node_id
              AND position = 'LEFT';
        END IF;
    END LOOP;

    RETURN candidate;
END;
$$;

-- ------------------------------------------------------------
-- 9. SUCCESSOR
-- ------------------------------------------------------------
-- Smallest key strictly greater than the supplied key.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION bst_successor(
    p_tree_id BIGINT,
    p_key BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    current_node tree_nodes%ROWTYPE;
    candidate BIGINT;
BEGIN
    SELECT *
    INTO current_node
    FROM tree_nodes
    WHERE tree_id = p_tree_id
      AND parent_id IS NULL;

    WHILE FOUND LOOP
        IF current_node.node_key > p_key THEN
            candidate := current_node.node_key;

            SELECT *
            INTO current_node
            FROM tree_nodes
            WHERE tree_id = p_tree_id
              AND parent_id = current_node.node_id
              AND position = 'LEFT';
        ELSE
            SELECT *
            INTO current_node
            FROM tree_nodes
            WHERE tree_id = p_tree_id
              AND parent_id = current_node.node_id
              AND position = 'RIGHT';
        END IF;
    END LOOP;

    RETURN candidate;
END;
$$;

-- ------------------------------------------------------------
-- 10. DELETE A NODE
-- ------------------------------------------------------------
-- Cases:
--   Leaf: remove the node.
--   One child: promote its child.
--   Two children: exchange its key with its inorder successor,
--                 then remove the successor.
--
-- The unique key constraint is deferred during the two-key
-- exchange. Parent and position relationships are maintained.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION bst_delete(
    p_tree_id BIGINT,
    p_key BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    target tree_nodes%ROWTYPE;
    successor_node tree_nodes%ROWTYPE;
    replacement tree_nodes%ROWTYPE;
    parent_node tree_nodes%ROWTYPE;
    old_key BIGINT;
BEGIN
    SELECT *
    INTO target
    FROM tree_nodes
    WHERE tree_id = p_tree_id
      AND node_key = p_key
    FOR UPDATE;

    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;

    SET CONSTRAINTS uq_tree_node_key DEFERRED;

    IF EXISTS (
        SELECT 1 FROM tree_nodes
        WHERE tree_id = p_tree_id
          AND parent_id = target.node_id
          AND position = 'LEFT'
    )
    AND EXISTS (
        SELECT 1 FROM tree_nodes
        WHERE tree_id = p_tree_id
          AND parent_id = target.node_id
          AND position = 'RIGHT'
    ) THEN

        SELECT *
        INTO successor_node
        FROM tree_nodes
        WHERE tree_id = p_tree_id
          AND parent_id = target.node_id
          AND position = 'RIGHT';

        LOOP
            SELECT *
            INTO replacement
            FROM tree_nodes
            WHERE tree_id = p_tree_id
              AND parent_id = successor_node.node_id
              AND position = 'LEFT';

            EXIT WHEN NOT FOUND;
            successor_node := replacement;
        END LOOP;

        old_key := target.node_key;

        UPDATE tree_nodes
        SET node_key = CASE
            WHEN node_id = target.node_id THEN successor_node.node_key
            WHEN node_id = successor_node.node_id THEN old_key
        END
        WHERE node_id IN (
            target.node_id,
            successor_node.node_id
        );

        -- The successor has no left child.
        target := successor_node;
    END IF;

    SELECT *
    INTO parent_node
    FROM tree_nodes
    WHERE tree_id = p_tree_id
      AND node_id = target.parent_id;

    SELECT *
    INTO replacement
    FROM tree_nodes
    WHERE tree_id = p_tree_id
      AND parent_id = target.node_id;

    IF NOT FOUND THEN
        -- Target is a leaf.
        DELETE FROM tree_nodes
        WHERE node_id = target.node_id;

        RETURN TRUE;
    END IF;

    -- A node with one child.
    IF target.parent_id IS NULL THEN
        UPDATE tree_nodes
        SET parent_id = NULL,
            position = NULL
        WHERE node_id = replacement.node_id;

    ELSE
        UPDATE tree_nodes
        SET parent_id = target.parent_id,
            position = target.position
        WHERE node_id = replacement.node_id;
    END IF;

    DELETE FROM tree_nodes
    WHERE node_id = target.node_id;

    RETURN TRUE;
END;
$$;

-- ------------------------------------------------------------
-- 11. INORDER TRAVERSAL VIEW
-- ------------------------------------------------------------
-- Recursive CTE follows parent relationships and generates
-- the ordering through a sortable traversal path.
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW bst_inorder AS
WITH RECURSIVE traversal AS (
    SELECT
        n.tree_id,
        n.node_id,
        n.node_key,
        n.parent_id,
        n.position,
        ARRAY[
            LPAD(n.node_key::TEXT, 20, '0')
        ]::TEXT[] AS path,
        1 AS depth
    FROM tree_nodes n
    WHERE n.parent_id IS NULL

    UNION ALL

    SELECT
        child.tree_id,
        child.node_id,
        child.node_key,
        child.parent_id,
        child.position,
        CASE
            WHEN child.position = 'LEFT'
                THEN parent.path || ARRAY['0' || LPAD(
                    child.node_key::TEXT, 20, '0'
                )]
            ELSE parent.path || ARRAY['1' || LPAD(
                    child.node_key::TEXT, 20, '0'
                )]
        END,
        parent.depth + 1
    FROM traversal parent
    JOIN tree_nodes child
      ON child.tree_id = parent.tree_id
     AND child.parent_id = parent.node_id
)
SELECT
    tree_id,
    node_id,
    node_key,
    depth
FROM traversal;

-- ------------------------------------------------------------
-- 12. TREE VALIDATION REPORT
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_tree(p_tree_id BIGINT)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    actual_count BIGINT;
    visited_count BIGINT;
    root_count BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO actual_count
    FROM tree_nodes
    WHERE tree_id = p_tree_id;

    SELECT COUNT(*)
    INTO root_count
    FROM tree_nodes
    WHERE tree_id = p_tree_id
      AND parent_id IS NULL;

    IF actual_count = 0 THEN
        RETURN root_count = 0;
    END IF;

    IF root_count <> 1 THEN
        RETURN FALSE;
    END IF;

    WITH RECURSIVE reachable AS (
        SELECT node_id, node_key
        FROM tree_nodes
        WHERE tree_id = p_tree_id
          AND parent_id IS NULL

        UNION ALL

        SELECT child.node_id, child.node_key
        FROM tree_nodes child
        JOIN reachable parent
          ON child.parent_id = parent.node_id
        WHERE child.tree_id = p_tree_id
    )
    SELECT COUNT(*)
    INTO visited_count
    FROM reachable;

    RETURN actual_count = visited_count
       AND NOT EXISTS (
           SELECT 1
           FROM tree_nodes child
           JOIN tree_nodes parent
             ON parent.tree_id = child.tree_id
            AND parent.node_id = child.parent_id
           WHERE child.tree_id = p_tree_id
             AND (
                 (child.position = 'LEFT'
                  AND child.node_key >= parent.node_key)
                 OR
                 (child.position = 'RIGHT'
                  AND child.node_key <= parent.node_key)
             )
       );
END;
$$;

-- ------------------------------------------------------------
-- 13. RANGE RETRIEVAL
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION bst_range(
    p_tree_id BIGINT,
    p_low BIGINT,
    p_high BIGINT
)
RETURNS TABLE (
    result_key BIGINT
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_low > p_high THEN
        RAISE EXCEPTION 'Invalid range boundaries.';
    END IF;

    RETURN QUERY
    SELECT n.node_key
    FROM bst_inorder n
    WHERE n.tree_id = p_tree_id
      AND n.node_key BETWEEN p_low AND p_high
    ORDER BY n.node_key;
END;
$$;

-- ------------------------------------------------------------
-- 14. SAMPLE TREE
-- ------------------------------------------------------------

INSERT INTO tree_registry(tree_name, description)
VALUES (
    'Product Identifier Index',
    'BST index for unique product identifiers.'
);

SELECT bst_insert(1, value)
FROM unnest(
    ARRAY[50, 30, 70, 20, 40, 60, 80, 35, 45, 65]::BIGINT[]
) AS value;

-- ------------------------------------------------------------
-- 15. RETRIEVAL QUERIES
-- ------------------------------------------------------------

-- All nodes in inorder.
SELECT tree_id, node_key, depth
FROM bst_inorder
WHERE tree_id = 1
ORDER BY node_key;

-- Search for an identifier.
SELECT *
FROM bst_search(1, 40);

-- Minimum and maximum.
SELECT
    bst_extreme(1, TRUE) AS minimum_key,
    bst_extreme(1, FALSE) AS maximum_key;

-- Predecessor and successor.
SELECT
    bst_predecessor(1, 50) AS predecessor,
    bst_successor(1, 50) AS successor;

-- Range retrieval.
SELECT * FROM bst_range(1, 35, 65);

-- ------------------------------------------------------------
-- 16. VALIDATION AND AGGREGATION
-- ------------------------------------------------------------

SELECT
    tree_id,
    COUNT(*) AS total_nodes,
    MIN(node_key) AS smallest_key,
    MAX(node_key) AS largest_key,
    AVG(node_key) AS average_key
FROM tree_nodes
GROUP BY tree_id;

SELECT
    tree_id,
    validate_tree(tree_id) AS ordering_valid
FROM tree_registry;

-- ------------------------------------------------------------
-- 17. FAILURE CASES
-- ------------------------------------------------------------

-- Duplicate insertion returns FALSE.
SELECT bst_insert(1, 50) AS duplicate_inserted;

-- Missing search returns null node identifiers.
SELECT * FROM bst_search(1, 999);

-- Missing predecessor and successor return NULL.
SELECT
    bst_predecessor(1, 10) AS no_predecessor,
    bst_successor(1, 100) AS no_successor;

-- ------------------------------------------------------------
-- 18. DELETE OPERATIONS
-- ------------------------------------------------------------

-- Delete a leaf.
SELECT bst_delete(1, 20);

-- Delete a node with one child.
SELECT bst_delete(1, 30);

-- Delete a node with two children.
SELECT bst_delete(1, 70);

-- Delete the root.
SELECT bst_delete(1, 50);

-- Missing-key deletion returns FALSE.
SELECT bst_delete(1, 999);

-- Confirm the resulting ordering.
SELECT node_key
FROM bst_inorder
WHERE tree_id = 1
ORDER BY node_key;

SELECT validate_tree(1) AS valid_after_deletion;

-- ------------------------------------------------------------
-- 19. TREE STATISTICS
-- ------------------------------------------------------------

WITH RECURSIVE levels AS (
    SELECT
        node_id,
        tree_id,
        1 AS depth
    FROM tree_nodes
    WHERE parent_id IS NULL

    UNION ALL

    SELECT
        child.node_id,
        child.tree_id,
        parent.depth + 1
    FROM tree_nodes child
    JOIN levels parent
      ON child.parent_id = parent.node_id
     AND child.tree_id = parent.tree_id
)
SELECT
    tree_id,
    COUNT(*) AS node_count,
    MAX(depth) AS tree_height
FROM levels
GROUP BY tree_id;

-- ------------------------------------------------------------
-- 20. TRANSACTION DEMONSTRATION
-- ------------------------------------------------------------
-- A failed operation rolls back the complete transaction.
-- ------------------------------------------------------------

SAVEPOINT before_transaction_demo;

DO $$
BEGIN
    PERFORM bst_insert(1, 90);
    PERFORM bst_insert(1, 85);

    IF NOT validate_tree(1) THEN
        RAISE EXCEPTION 'Tree validation failed.';
    END IF;
END;
$$;

ROLLBACK TO SAVEPOINT before_transaction_demo;

-- Confirm rollback.
SELECT *
FROM bst_search(1, 90);

-- ------------------------------------------------------------
-- 21. CREATE A SECOND INDEPENDENT TREE
-- ------------------------------------------------------------

SELECT create_tree(
    'Employee Identifier Index',
    'Independent BST for employee identifiers.'
);

SELECT bst_insert(2, value)
FROM unnest(
    ARRAY[5000, 3000, 7000, 2000, 4000, 6000, 8000]::BIGINT[]
) AS value;

SELECT
    tree_id,
    node_key
FROM bst_inorder
ORDER BY tree_id, node_key;

SELECT
    tree_id,
    validate_tree(tree_id)
FROM tree_registry;

COMMIT;
