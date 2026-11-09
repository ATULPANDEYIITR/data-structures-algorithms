/*
 * RED-BLACK TREES
 * PostgreSQL 15+
 *
 * Relational representation of a Red-Black Tree index.
 *
 * Includes:
 * - Tree metadata
 * - Node relationships
 * - Color constraints
 * - Parent-child integrity
 * - Operation history
 * - Insertion and rotation functions
 * - Structural validation
 * - Black-height validation
 * - Ordered retrieval
 * - Range queries
 * - Tree reporting
 * - Transactional demonstrations
 *
 * The database representation stores one node per row.
 * The application or database transaction must serialize
 * concurrent structural mutations of an individual tree.
 */

DROP SCHEMA IF EXISTS rb_tree CASCADE;

CREATE SCHEMA rb_tree;

SET search_path TO rb_tree, public;

/* =========================================================
   1. DOMAIN TYPES
   ========================================================= */

CREATE TYPE node_color AS ENUM (
    'RED',
    'BLACK'
);

CREATE TYPE operation_type AS ENUM (
    'INSERT',
    'DELETE',
    'LEFT_ROTATE',
    'RIGHT_ROTATE'
);

CREATE TYPE operation_status AS ENUM (
    'SUCCESS',
    'REJECTED',
    'FAILED'
);

/* =========================================================
   2. TREE METADATA
   ========================================================= */

CREATE TABLE trees (
    tree_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    tree_name VARCHAR(120) NOT NULL UNIQUE,

    root_node_id BIGINT,

    node_count INTEGER NOT NULL DEFAULT 0,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_tree_count CHECK (node_count >= 0)
);

/* =========================================================
   3. TREE NODES
   ========================================================= */

CREATE TABLE tree_nodes (
    node_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    tree_id BIGINT NOT NULL
        REFERENCES trees(tree_id) ON DELETE CASCADE,

    node_key BIGINT NOT NULL,

    color node_color NOT NULL DEFAULT 'RED',

    parent_id BIGINT,

    left_child_id BIGINT,

    right_child_id BIGINT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_tree_key UNIQUE (tree_id, node_key),

    CONSTRAINT unique_tree_node_pair UNIQUE (tree_id, node_id),

    CONSTRAINT no_self_parent
        CHECK (parent_id IS DISTINCT FROM node_id),

    CONSTRAINT no_self_left_child
        CHECK (left_child_id IS DISTINCT FROM node_id),

    CONSTRAINT no_self_right_child
        CHECK (right_child_id IS DISTINCT FROM node_id),

    CONSTRAINT distinct_children
        CHECK (
            left_child_id IS NULL
            OR right_child_id IS NULL
            OR left_child_id <> right_child_id
        ),

    CONSTRAINT parent_same_tree
        FOREIGN KEY (tree_id, parent_id)
        REFERENCES tree_nodes(tree_id, node_id)
        DEFERRABLE INITIALLY DEFERRED,

    CONSTRAINT left_child_same_tree
        FOREIGN KEY (tree_id, left_child_id)
        REFERENCES tree_nodes(tree_id, node_id)
        DEFERRABLE INITIALLY DEFERRED,

    CONSTRAINT right_child_same_tree
        FOREIGN KEY (tree_id, right_child_id)
        REFERENCES tree_nodes(tree_id, node_id)
        DEFERRABLE INITIALLY DEFERRED
);

/*
 * A node may have only one parent.
 * A partial unique index also prevents a child from being
 * attached to two different parent positions.
 */

CREATE UNIQUE INDEX unique_left_parent
    ON tree_nodes(tree_id, left_child_id)
    WHERE left_child_id IS NOT NULL;

CREATE UNIQUE INDEX unique_right_parent
    ON tree_nodes(tree_id, right_child_id)
    WHERE right_child_id IS NOT NULL;

CREATE INDEX tree_node_parent_idx
    ON tree_nodes(tree_id, parent_id);

CREATE INDEX tree_node_color_idx
    ON tree_nodes(tree_id, color);

/*
 * Ensure the designated root belongs to the same tree.
 */

ALTER TABLE trees
ADD CONSTRAINT root_belongs_to_tree
FOREIGN KEY (tree_id, root_node_id)
REFERENCES tree_nodes(tree_id, node_id)
DEFERRABLE INITIALLY DEFERRED;

/* =========================================================
   4. OPERATION AUDIT
   ========================================================= */

CREATE TABLE operation_log (
    operation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    tree_id BIGINT NOT NULL
        REFERENCES trees(tree_id) ON DELETE CASCADE,

    operation operation_type NOT NULL,

    operation_status operation_status NOT NULL,

    affected_key BIGINT,

    details JSONB NOT NULL DEFAULT '{}'::JSONB,

    executed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX operation_log_tree_time_idx
    ON operation_log(tree_id, executed_at DESC);

/* =========================================================
   5. NODE INSERTION TRIGGER
   ========================================================= */

CREATE OR REPLACE FUNCTION maintain_tree_metadata()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE trees
        SET node_count = node_count + 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE tree_id = NEW.tree_id;

        RETURN NEW;

    ELSIF TG_OP = 'DELETE' THEN
        UPDATE trees
        SET node_count = node_count - 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE tree_id = OLD.tree_id;

        RETURN OLD;
    END IF;

    RETURN NULL;
END;
$$;

CREATE TRIGGER tree_node_insert_metadata
AFTER INSERT ON tree_nodes
FOR EACH ROW
EXECUTE FUNCTION maintain_tree_metadata();

CREATE TRIGGER tree_node_delete_metadata
AFTER DELETE ON tree_nodes
FOR EACH ROW
EXECUTE FUNCTION maintain_tree_metadata();

/* =========================================================
   6. INSERT NODE FUNCTION
   ========================================================= */

CREATE OR REPLACE FUNCTION insert_tree_node(
    p_tree_id BIGINT,
    p_key BIGINT,
    p_color node_color DEFAULT 'RED'
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_node_id BIGINT;
BEGIN
    /*
     * The metadata row is the synchronization point.
     * Concurrent insertions into the same tree serialize here.
     */

    PERFORM 1
    FROM trees
    WHERE tree_id = p_tree_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Tree % does not exist', p_tree_id;
    END IF;

    INSERT INTO tree_nodes (
        tree_id,
        node_key,
        color
    )
    VALUES (
        p_tree_id,
        p_key,
        p_color
    )
    RETURNING node_id INTO v_node_id;

    INSERT INTO operation_log (
        tree_id,
        operation,
        operation_status,
        affected_key
    )
    VALUES (
        p_tree_id,
        'INSERT',
        'SUCCESS',
        p_key
    );

    RETURN v_node_id;

EXCEPTION
    WHEN unique_violation THEN
        RAISE EXCEPTION
            'Duplicate key % in tree %',
            p_key,
            p_tree_id;
END;
$$;

/* =========================================================
   7. LEFT ROTATION
   ========================================================= */

CREATE OR REPLACE FUNCTION rotate_left(
    p_tree_id BIGINT,
    p_x_id BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_x tree_nodes%ROWTYPE;
    v_y tree_nodes%ROWTYPE;
    v_parent_id BIGINT;
    v_root_id BIGINT;
BEGIN
    PERFORM 1
    FROM trees
    WHERE tree_id = p_tree_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Tree does not exist';
    END IF;

    SELECT *
    INTO v_x
    FROM tree_nodes
    WHERE tree_id = p_tree_id
      AND node_id = p_x_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Rotation node does not exist';
    END IF;

    IF v_x.right_child_id IS NULL THEN
        RAISE EXCEPTION 'Left rotation requires right child';
    END IF;

    SELECT *
    INTO v_y
    FROM tree_nodes
    WHERE tree_id = p_tree_id
      AND node_id = v_x.right_child_id
    FOR UPDATE;

    v_parent_id := v_x.parent_id;

    /*
     * Move beta from y.left to x.right.
     */

    UPDATE tree_nodes
    SET right_child_id = v_y.left_child_id
    WHERE node_id = v_x.node_id;

    IF v_y.left_child_id IS NOT NULL THEN
        UPDATE tree_nodes
        SET parent_id = v_x.node_id
        WHERE node_id = v_y.left_child_id;
    END IF;

    /*
     * Connect y to the previous parent of x.
     */

    UPDATE tree_nodes
    SET parent_id = v_parent_id
    WHERE node_id = v_y.node_id;

    IF v_parent_id IS NULL THEN
        UPDATE trees
        SET root_node_id = v_y.node_id
        WHERE tree_id = p_tree_id;
    ELSE
        UPDATE tree_nodes
        SET
            left_child_id = CASE
                WHEN left_child_id = v_x.node_id
                THEN v_y.node_id
                ELSE left_child_id
            END,
            right_child_id = CASE
                WHEN right_child_id = v_x.node_id
                THEN v_y.node_id
                ELSE right_child_id
            END
        WHERE node_id = v_parent_id;
    END IF;

    UPDATE tree_nodes
    SET
        left_child_id = v_x.node_id,
        parent_id = v_y.node_id
    WHERE node_id = v_y.node_id;

    INSERT INTO operation_log (
        tree_id,
        operation,
        operation_status,
        affected_key,
        details
    )
    VALUES (
        p_tree_id,
        'LEFT_ROTATE',
        'SUCCESS',
        v_x.node_key,
        jsonb_build_object(
            'pivot_key', v_x.node_key,
            'promoted_key', v_y.node_key
        )
    );

    RETURN v_y.node_id;
END;
$$;

/* =========================================================
   8. RIGHT ROTATION
   ========================================================= */

CREATE OR REPLACE FUNCTION rotate_right(
    p_tree_id BIGINT,
    p_y_id BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_y tree_nodes%ROWTYPE;
    v_x tree_nodes%ROWTYPE;
    v_parent_id BIGINT;
BEGIN
    PERFORM 1
    FROM trees
    WHERE tree_id = p_tree_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Tree does not exist';
    END IF;

    SELECT *
    INTO v_y
    FROM tree_nodes
    WHERE tree_id = p_tree_id
      AND node_id = p_y_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Rotation node does not exist';
    END IF;

    IF v_y.left_child_id IS NULL THEN
        RAISE EXCEPTION 'Right rotation requires left child';
    END IF;

    SELECT *
    INTO v_x
    FROM tree_nodes
    WHERE tree_id = p_tree_id
      AND node_id = v_y.left_child_id
    FOR UPDATE;

    v_parent_id := v_y.parent_id;

    UPDATE tree_nodes
    SET left_child_id = v_x.right_child_id
    WHERE node_id = v_y.node_id;

    IF v_x.right_child_id IS NOT NULL THEN
        UPDATE tree_nodes
        SET parent_id = v_y.node_id
        WHERE node_id = v_x.right_child_id;
    END IF;

    UPDATE tree_nodes
    SET parent_id = v_parent_id
    WHERE node_id = v_x.node_id;

    IF v_parent_id IS NULL THEN
        UPDATE trees
        SET root_node_id = v_x.node_id
        WHERE tree_id = p_tree_id;
    ELSE
        UPDATE tree_nodes
        SET
            left_child_id = CASE
                WHEN left_child_id = v_y.node_id
                THEN v_x.node_id
                ELSE left_child_id
            END,
            right_child_id = CASE
                WHEN right_child_id = v_y.node_id
                THEN v_x.node_id
                ELSE right_child_id
            END
        WHERE node_id = v_parent_id;
    END IF;

    UPDATE tree_nodes
    SET
        right_child_id = v_y.node_id,
        parent_id = v_x.node_id
    WHERE node_id = v_x.node_id;

    INSERT INTO operation_log (
        tree_id,
        operation,
        operation_status,
        affected_key,
        details
    )
    VALUES (
        p_tree_id,
        'RIGHT_ROTATE',
        'SUCCESS',
        v_y.node_key,
        jsonb_build_object(
            'pivot_key', v_y.node_key,
            'promoted_key', v_x.node_key
        )
    );

    RETURN v_x.node_id;
END;
$$;

/* =========================================================
   9. STRUCTURAL VALIDATION
   ========================================================= */

CREATE OR REPLACE FUNCTION validate_tree(
    p_tree_id BIGINT
)
RETURNS TABLE (
    is_valid BOOLEAN,
    reported_nodes INTEGER,
    actual_nodes INTEGER,
    black_height INTEGER,
    validation_message TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_root BIGINT;
    v_count INTEGER;
    v_actual INTEGER;
    v_black_height INTEGER;
    v_result INTEGER;
    v_cycle BOOLEAN;
BEGIN
    SELECT root_node_id, node_count
    INTO v_root, v_count
    FROM trees
    WHERE tree_id = p_tree_id;

    IF NOT FOUND THEN
        RETURN QUERY SELECT
            FALSE, 0, 0, 0, 'Tree does not exist';
        RETURN;
    END IF;

    SELECT COUNT(*)::INTEGER
    INTO v_actual
    FROM tree_nodes
    WHERE tree_id = p_tree_id;

    IF v_actual <> v_count THEN
        RETURN QUERY SELECT
            FALSE, v_count, v_actual, 0,
            'Metadata count mismatch';
        RETURN;
    END IF;

    IF v_actual = 0 THEN
        IF v_root IS NOT NULL THEN
            RETURN QUERY SELECT
                FALSE, v_count, v_actual, 0,
                'Empty tree has a root';
        ELSE
            RETURN QUERY SELECT
                TRUE, v_count, v_actual, 1,
                'Valid empty tree';
        END IF;

        RETURN;
    END IF;

    IF v_root IS NULL THEN
        RETURN QUERY SELECT
            FALSE, v_count, v_actual, 0,
            'Non-empty tree has no root';
        RETURN;
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM tree_nodes
        WHERE tree_id = p_tree_id
          AND node_id = v_root
          AND color = 'BLACK'
          AND parent_id IS NULL
    ) THEN
        RETURN QUERY SELECT
            FALSE, v_count, v_actual, 0,
            'Root must be black and have no parent';
        RETURN;
    END IF;

    /*
     * A recursive path detects cycles and verifies
     * that every reachable node has a consistent parent.
     */

    WITH RECURSIVE traversal AS (
        SELECT
            node_id,
            node_key,
            color,
            parent_id,
            left_child_id,
            right_child_id,
            ARRAY[node_id]::BIGINT[] AS path,
            FALSE AS cycle_found,
            0 AS depth
        FROM tree_nodes
        WHERE tree_id = p_tree_id
          AND node_id = v_root

        UNION ALL

        SELECT
            child.node_id,
            child.node_key,
            child.color,
            child.parent_id,
            child.left_child_id,
            child.right_child_id,
            parent.path || child.node_id,
            child.node_id = ANY(parent.path),
            parent.depth + 1
        FROM traversal parent
        CROSS JOIN LATERAL (
            SELECT *
            FROM tree_nodes
            WHERE tree_id = p_tree_id
              AND node_id IN (
                  parent.left_child_id,
                  parent.right_child_id
              )
        ) child
        WHERE NOT parent.cycle_found
          AND child.node_id <> ALL(parent.path)
    )
    SELECT
        COALESCE(BOOL_OR(cycle_found), FALSE)
    INTO v_cycle
    FROM traversal;

    IF v_cycle THEN
        RETURN QUERY SELECT
            FALSE, v_count, v_actual, 0,
            'Cycle detected';
        RETURN;
    END IF;

    /*
     * Every non-root node must have a reciprocal parent link.
     */

    IF EXISTS (
        SELECT 1
        FROM tree_nodes child
        LEFT JOIN tree_nodes parent
            ON parent.tree_id = child.tree_id
           AND parent.node_id = child.parent_id
        WHERE child.tree_id = p_tree_id
          AND child.node_id <> v_root
          AND (
              parent.node_id IS NULL
              OR (
                  parent.left_child_id <> child.node_id
                  AND parent.right_child_id <> child.node_id
              )
          )
    ) THEN
        RETURN QUERY SELECT
            FALSE, v_count, v_actual, 0,
            'Parent-child relationship violation';
        RETURN;
    END IF;

    /*
     * Verify strict BST ordering using recursive bounds.
     */

    IF EXISTS (
        WITH RECURSIVE ordered AS (
            SELECT
                node_id,
                node_key,
                left_child_id,
                right_child_id,
                NULL::BIGINT AS lower_bound,
                NULL::BIGINT AS upper_bound
            FROM tree_nodes
            WHERE tree_id = p_tree_id
              AND node_id = v_root

            UNION ALL

            SELECT
                child.node_id,
                child.node_key,
                child.left_child_id,
                child.right_child_id,
                bounds.lower_bound,
                bounds.node_key
            FROM ordered bounds
            JOIN tree_nodes child
                ON child.node_id = bounds.left_child_id
               AND child.tree_id = p_tree_id

            UNION ALL

            SELECT
                child.node_id,
                child.node_key,
                child.left_child_id,
                child.right_child_id,
                bounds.node_key,
                bounds.upper_bound
            FROM ordered bounds
            JOIN tree_nodes child
                ON child.node_id = bounds.right_child_id
               AND child.tree_id = p_tree_id
        )
        SELECT 1
        FROM ordered
        WHERE (
            lower_bound IS NOT NULL
            AND node_key <= lower_bound
        )
        OR (
            upper_bound IS NOT NULL
            AND node_key >= upper_bound
        )
    ) THEN
        RETURN QUERY SELECT
            FALSE, v_count, v_actual, 0,
            'Binary search ordering violation';
        RETURN;
    END IF;

    /*
     * Red nodes cannot have red children.
     */

    IF EXISTS (
        SELECT 1
        FROM tree_nodes parent
        JOIN tree_nodes child
          ON child.tree_id = parent.tree_id
         AND child.node_id IN (
             parent.left_child_id,
             parent.right_child_id
         )
        WHERE parent.tree_id = p_tree_id
          AND parent.color = 'RED'
          AND child.color = 'RED'
    ) THEN
        RETURN QUERY SELECT
            FALSE, v_count, v_actual, 0,
            'Adjacent red nodes detected';
        RETURN;
    END IF;

    /*
     * Calculate black height recursively.
     * A null leaf contributes one black sentinel.
     */

    WITH RECURSIVE black_paths AS (
        SELECT
            node_id,
            node_key,
            color,
            left_child_id,
            right_child_id,
            CASE WHEN color = 'BLACK' THEN 1 ELSE 0 END
                AS black_count,
            ARRAY[node_id]::BIGINT[] AS path
        FROM tree_nodes
        WHERE tree_id = p_tree_id
          AND node_id = v_root

        UNION ALL

        SELECT
            child.node_id,
            child.node_key,
            child.color,
            child.left_child_id,
            child.right_child_id,
            parent.black_count +
                CASE WHEN child.color = 'BLACK' THEN 1 ELSE 0 END,
            parent.path || child.node_id
        FROM black_paths parent
        JOIN tree_nodes child
          ON child.tree_id = p_tree_id
         AND child.node_id IN (
             parent.left_child_id,
             parent.right_child_id
         )
    ),
    leaf_heights AS (
        SELECT
            black_count + 1 AS black_height
        FROM black_paths
        WHERE left_child_id IS NULL
          AND right_child_id IS NULL
    )
    SELECT
        MIN(black_height),
        MAX(black_height)
    INTO v_black_height, v_result
    FROM leaf_heights;

    IF v_black_height IS DISTINCT FROM v_result THEN
        RETURN QUERY SELECT
            FALSE, v_count, v_actual,
            COALESCE(v_black_height, 0),
            'Black-height violation';
        RETURN;
    END IF;

    /*
     * Verify that every node is reachable from the root.
     */

    WITH RECURSIVE reachable AS (
        SELECT node_id
        FROM tree_nodes
        WHERE tree_id = p_tree_id
          AND node_id = v_root

        UNION

        SELECT child.node_id
        FROM reachable parent
        JOIN tree_nodes parent_node
          ON parent_node.node_id = parent.node_id
         AND parent_node.tree_id = p_tree_id
        JOIN tree_nodes child
          ON child.tree_id = p_tree_id
         AND child.node_id IN (
             parent_node.left_child_id,
             parent_node.right_child_id
         )
    )
    SELECT COUNT(*)::INTEGER
    INTO v_result
    FROM reachable;

    IF v_result <> v_actual THEN
        RETURN QUERY SELECT
            FALSE, v_count, v_actual, 0,
            'Unreachable or disconnected nodes detected';
        RETURN;
    END IF;

    RETURN QUERY SELECT
        TRUE,
        v_count,
        v_actual,
        COALESCE(v_black_height, 1),
        'All Red-Black properties satisfied';
END;
$$;

/* =========================================================
   10. ORDERED RETRIEVAL VIEW
   ========================================================= */

CREATE OR REPLACE VIEW ordered_tree_nodes AS
SELECT
    t.tree_id,
    t.tree_name,
    n.node_id,
    n.node_key,
    n.color,
    n.parent_id,
    n.left_child_id,
    n.right_child_id
FROM trees t
JOIN tree_nodes n
    ON n.tree_id = t.tree_id;

/* =========================================================
   11. SAMPLE TREE
   ========================================================= */

INSERT INTO trees(tree_name)
VALUES ('inventory_asset_index');

INSERT INTO trees(tree_name)
VALUES ('employee_directory_index');

/*
 * Build a valid balanced tree:
 *
 *             20(B)
 *            /     \
 *         10(R)    30(R)
 *
 * Each absent child represents a black sentinel.
 */

DO $$
DECLARE
    v_tree BIGINT;
    v_20 BIGINT;
    v_10 BIGINT;
    v_30 BIGINT;
BEGIN
    SELECT tree_id
    INTO v_tree
    FROM trees
    WHERE tree_name = 'inventory_asset_index';

    v_20 := insert_tree_node(v_tree, 20, 'BLACK');
    v_10 := insert_tree_node(v_tree, 10, 'RED');
    v_30 := insert_tree_node(v_tree, 30, 'RED');

    UPDATE tree_nodes
    SET left_child_id = v_10,
        right_child_id = v_30
    WHERE node_id = v_20;

    UPDATE tree_nodes
    SET parent_id = v_20
    WHERE node_id IN (v_10, v_30);

    UPDATE trees
    SET root_node_id = v_20
    WHERE tree_id = v_tree;
END;
$$;

/* =========================================================
   12. SECOND SAMPLE TREE
   ========================================================= */

DO $$
DECLARE
    v_tree BIGINT;
    v_root BIGINT;
    v_left BIGINT;
    v_right BIGINT;
BEGIN
    SELECT tree_id
    INTO v_tree
    FROM trees
    WHERE tree_name = 'employee_directory_index';

    v_root := insert_tree_node(v_tree, 100, 'BLACK');
    v_left := insert_tree_node(v_tree, 50, 'RED');
    v_right := insert_tree_node(v_tree, 150, 'RED');

    UPDATE tree_nodes
    SET left_child_id = v_left,
        right_child_id = v_right
    WHERE node_id = v_root;

    UPDATE tree_nodes
    SET parent_id = v_root
    WHERE node_id IN (v_left, v_right);

    UPDATE trees
    SET root_node_id = v_root
    WHERE tree_id = v_tree;
END;
$$;

/* =========================================================
   13. TRANSACTIONAL ROTATION DEMONSTRATION
   ========================================================= */

BEGIN;

DO $$
DECLARE
    v_tree BIGINT;
    v_root BIGINT;
BEGIN
    SELECT tree_id, root_node_id
    INTO v_tree, v_root
    FROM trees
    WHERE tree_name = 'inventory_asset_index'
    FOR UPDATE;

    /*
     * Left rotation:
     *
     *       20              30
     *      /  \            /
     *    10   30    ->    20
     *                    /
     *                   10
     *
     * The resulting ordering is valid, but its colors
     * require separate rebalancing for full Red-Black validity.
     */

    PERFORM rotate_left(v_tree, v_root);
END;
$$;

ROLLBACK;

/*
 * The rollback preserves the original valid sample tree.
 */

/* =========================================================
   14. RETRIEVAL
   ========================================================= */

SELECT *
FROM ordered_tree_nodes
ORDER BY tree_name, node_key;

/* Retrieve keys within an interval. */

SELECT
    tree_name,
    node_key,
    color
FROM ordered_tree_nodes
WHERE tree_name = 'inventory_asset_index'
  AND node_key BETWEEN 10 AND 25
ORDER BY node_key;

/* =========================================================
   15. VALIDATION
   ========================================================= */

SELECT
    t.tree_name,
    v.*
FROM trees t
CROSS JOIN LATERAL validate_tree(t.tree_id) v
ORDER BY t.tree_id;

/* =========================================================
   16. AGGREGATION AND REPORTING
   ========================================================= */

SELECT
    tree_id,
    tree_name,
    COUNT(*) AS total_nodes,
    COUNT(*) FILTER (
        WHERE color = 'RED'
    ) AS red_nodes,
    COUNT(*) FILTER (
        WHERE color = 'BLACK'
    ) AS black_nodes,
    MIN(node_key) AS minimum_key,
    MAX(node_key) AS maximum_key
FROM ordered_tree_nodes
GROUP BY tree_id, tree_name
ORDER BY tree_name;

/* Operation statistics. */

SELECT
    tree_id,
    operation,
    operation_status,
    COUNT(*) AS operation_count
FROM operation_log
GROUP BY tree_id, operation, operation_status
ORDER BY tree_id, operation;

/* =========================================================
   17. ELIGIBILITY AND STRUCTURAL HEALTH
   ========================================================= */

CREATE OR REPLACE VIEW tree_health_report AS
SELECT
    t.tree_id,
    t.tree_name,
    t.node_count,
    validation.is_valid,
    validation.black_height,
    validation.validation_message,
    CASE
        WHEN validation.is_valid
         AND t.node_count = validation.actual_nodes
        THEN 'HEALTHY'
        ELSE 'REQUIRES_REPAIR'
    END AS tree_status
FROM trees t
CROSS JOIN LATERAL validate_tree(t.tree_id) validation;

SELECT *
FROM tree_health_report
ORDER BY tree_name;

/* =========================================================
   18. VALIDATION FAILURE EXAMPLE
   ========================================================= */

/*
 * Duplicate insertion is rejected by the unique constraint.
 * This block catches the expected error so that the complete
 * script can continue.
 */

DO $$
DECLARE
    v_tree BIGINT;
BEGIN
    SELECT tree_id
    INTO v_tree
    FROM trees
    WHERE tree_name = 'inventory_asset_index';

    BEGIN
        PERFORM insert_tree_node(v_tree, 20, 'RED');
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Expected duplicate rejection: %', SQLERRM;
    END;
END;
$$;

/* =========================================================
   19. FINAL REPORT
   ========================================================= */

SELECT
    tree_name,
    node_count,
    root_node_id,
    created_at,
    updated_at
FROM trees
ORDER BY tree_id;

SELECT *
FROM tree_health_report
ORDER BY tree_id;
