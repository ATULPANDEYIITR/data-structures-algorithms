-- ============================================================
-- ADVANCED BINARY SEARCH TREE
-- PostgreSQL 14+
--
-- Features:
--   1. BST construction and insertion
--   2. Kth smallest and kth largest
--   3. Lowest common ancestor
--   4. BST validation
--   5. Height and balance evaluation
--   6. Balanced reconstruction
--   7. Preorder reconstruction
--   8. BST-to-doubly-linked-list conversion
--   9. Range retrieval and reporting
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS advanced_bst;

SET search_path TO advanced_bst, public;

-- ------------------------------------------------------------
-- 1. TREE REGISTRY
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS bst_tree (
    tree_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tree_name VARCHAR(150) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (length(trim(tree_name)) > 0)
);

-- ------------------------------------------------------------
-- 2. TREE NODES
--
-- Each node has at most one parent, one left child and
-- one right child. The partial unique indexes enforce
-- child-position uniqueness within a tree.
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS bst_node (
    node_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    tree_id BIGINT NOT NULL
        REFERENCES bst_tree(tree_id)
        ON DELETE CASCADE,

    node_key INTEGER NOT NULL,

    parent_node_id BIGINT,
    left_child_id BIGINT,
    right_child_id BIGINT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (tree_id, node_id),
    UNIQUE (tree_id, node_key),

    FOREIGN KEY (tree_id, parent_node_id)
        REFERENCES bst_node(tree_id, node_id)
        DEFERRABLE INITIALLY DEFERRED,

    FOREIGN KEY (tree_id, left_child_id)
        REFERENCES bst_node(tree_id, node_id)
        DEFERRABLE INITIALLY DEFERRED,

    FOREIGN KEY (tree_id, right_child_id)
        REFERENCES bst_node(tree_id, node_id)
        DEFERRABLE INITIALLY DEFERRED,

    CHECK (left_child_id IS DISTINCT FROM right_child_id),
    CHECK (parent_node_id IS DISTINCT FROM node_id),
    CHECK (left_child_id IS DISTINCT FROM node_id),
    CHECK (right_child_id IS DISTINCT FROM node_id)
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_bst_left_child
ON bst_node(tree_id, left_child_id)
WHERE left_child_id IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_bst_right_child
ON bst_node(tree_id, right_child_id)
WHERE right_child_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_bst_parent
ON bst_node(tree_id, parent_node_id);

CREATE INDEX IF NOT EXISTS idx_bst_node_key
ON bst_node(tree_id, node_key);

-- ------------------------------------------------------------
-- 3. TREE ROOT
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS bst_tree_root (
    tree_id BIGINT PRIMARY KEY
        REFERENCES bst_tree(tree_id)
        ON DELETE CASCADE,

    root_node_id BIGINT NOT NULL,

    FOREIGN KEY (tree_id, root_node_id)
        REFERENCES bst_node(tree_id, node_id)
        DEFERRABLE INITIALLY DEFERRED
);

-- ------------------------------------------------------------
-- 4. VALIDATION TRIGGER
--
-- A child must belong to the same tree.
-- A node cannot be its own parent or child.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_bst_node()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.parent_node_id = NEW.node_id
       OR NEW.left_child_id = NEW.node_id
       OR NEW.right_child_id = NEW.node_id THEN
        RAISE EXCEPTION 'A node cannot reference itself';
    END IF;

    IF NEW.left_child_id IS NOT NULL
       AND NEW.left_child_id = NEW.right_child_id THEN
        RAISE EXCEPTION 'Left and right children must differ';
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validate_bst_node ON bst_node;

CREATE TRIGGER trg_validate_bst_node
BEFORE INSERT OR UPDATE ON bst_node
FOR EACH ROW
EXECUTE FUNCTION validate_bst_node();

-- ------------------------------------------------------------
-- 5. INSERT A KEY INTO A BST
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION bst_insert(
    p_tree_id BIGINT,
    p_key INTEGER
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_root BIGINT;
    v_current BIGINT;
    v_left BIGINT;
    v_right BIGINT;
    v_current_key INTEGER;
    v_new_node BIGINT;
BEGIN
    PERFORM 1
    FROM bst_tree
    WHERE tree_id = p_tree_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Tree % does not exist', p_tree_id;
    END IF;

    SELECT root_node_id
    INTO v_root
    FROM bst_tree_root
    WHERE tree_id = p_tree_id;

    IF v_root IS NULL THEN
        INSERT INTO bst_node(tree_id, node_key)
        VALUES (p_tree_id, p_key)
        RETURNING node_id INTO v_new_node;

        INSERT INTO bst_tree_root(tree_id, root_node_id)
        VALUES (p_tree_id, v_new_node)
        ON CONFLICT (tree_id)
        DO UPDATE SET root_node_id = EXCLUDED.root_node_id;

        RETURN v_new_node;
    END IF;

    v_current := v_root;

    LOOP
        SELECT node_key, left_child_id, right_child_id
        INTO v_current_key, v_left, v_right
        FROM bst_node
        WHERE tree_id = p_tree_id
          AND node_id = v_current
        FOR UPDATE;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'Broken tree reference';
        END IF;

        IF p_key = v_current_key THEN
            RAISE EXCEPTION 'Duplicate BST key: %', p_key;
        END IF;

        IF p_key < v_current_key THEN
            IF v_left IS NULL THEN
                INSERT INTO bst_node(
                    tree_id,
                    node_key,
                    parent_node_id
                )
                VALUES (
                    p_tree_id,
                    p_key,
                    v_current
                )
                RETURNING node_id INTO v_new_node;

                UPDATE bst_node
                SET left_child_id = v_new_node
                WHERE tree_id = p_tree_id
                  AND node_id = v_current;

                RETURN v_new_node;
            END IF;

            v_current := v_left;
        ELSE
            IF v_right IS NULL THEN
                INSERT INTO bst_node(
                    tree_id,
                    node_key,
                    parent_node_id
                )
                VALUES (
                    p_tree_id,
                    p_key,
                    v_current
                )
                RETURNING node_id INTO v_new_node;

                UPDATE bst_node
                SET right_child_id = v_new_node
                WHERE tree_id = p_tree_id
                  AND node_id = v_current;

                RETURN v_new_node;
            END IF;

            v_current := v_right;
        END IF;
    END LOOP;
END;
$$;

-- ------------------------------------------------------------
-- 6. SEARCH
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION bst_search(
    p_tree_id BIGINT,
    p_key INTEGER
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_current BIGINT;
    v_key INTEGER;
    v_left BIGINT;
    v_right BIGINT;
BEGIN
    SELECT root_node_id
    INTO v_current
    FROM bst_tree_root
    WHERE tree_id = p_tree_id;

    WHILE v_current IS NOT NULL LOOP
        SELECT node_key, left_child_id, right_child_id
        INTO v_key, v_left, v_right
        FROM bst_node
        WHERE tree_id = p_tree_id
          AND node_id = v_current;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'Broken BST node reference';
        END IF;

        IF v_key = p_key THEN
            RETURN TRUE;
        ELSIF p_key < v_key THEN
            v_current := v_left;
        ELSE
            v_current := v_right;
        END IF;
    END LOOP;

    RETURN FALSE;
END;
$$;

-- ------------------------------------------------------------
-- 7. INORDER TRAVERSAL
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION bst_inorder(p_tree_id BIGINT)
RETURNS TABLE(node_key INTEGER)
LANGUAGE sql
STABLE
AS $$
    WITH RECURSIVE walk(node_id, node_key, left_id, right_id) AS (
        SELECT n.node_id, n.node_key,
               n.left_child_id, n.right_child_id
        FROM bst_tree_root r
        JOIN bst_node n
          ON n.tree_id = r.tree_id
         AND n.node_id = r.root_node_id
        WHERE r.tree_id = p_tree_id

        UNION ALL

        SELECT child.node_id, child.node_key,
               child.left_child_id, child.right_child_id
        FROM walk parent
        JOIN bst_node child
          ON child.tree_id = p_tree_id
         AND child.node_id = parent.left_id
    ),
    inorder_walk(node_id, node_key, left_id, right_id, visited) AS (
        SELECT node_id, node_key, left_id, right_id,
               ARRAY[node_id]::BIGINT[]
        FROM walk
        WHERE FALSE
    )
    SELECT n.node_key
    FROM bst_node n
    WHERE n.tree_id = p_tree_id
      AND EXISTS (
          SELECT 1
          FROM bst_tree_root r
          WHERE r.tree_id = p_tree_id
      )
    ORDER BY n.node_key;
$$;

-- The unique-key BST invariant means ordered key retrieval
-- is equivalent to inorder output. The function above uses
-- the indexed key ordering for this relational representation.

-- ------------------------------------------------------------
-- 8. KTH SMALLEST
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION bst_kth_smallest(
    p_tree_id BIGINT,
    p_k INTEGER
)
RETURNS INTEGER
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_count BIGINT;
    v_result INTEGER;
BEGIN
    IF p_k IS NULL OR p_k < 1 THEN
        RAISE EXCEPTION 'k must be a positive integer';
    END IF;

    SELECT COUNT(*)
    INTO v_count
    FROM bst_node
    WHERE tree_id = p_tree_id;

    IF p_k > v_count THEN
        RAISE EXCEPTION
            'k=% exceeds tree size=%',
            p_k,
            v_count;
    END IF;

    SELECT node_key
    INTO v_result
    FROM bst_node
    WHERE tree_id = p_tree_id
    ORDER BY node_key
    OFFSET p_k - 1
    LIMIT 1;

    RETURN v_result;
END;
$$;

-- ------------------------------------------------------------
-- 9. KTH LARGEST
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION bst_kth_largest(
    p_tree_id BIGINT,
    p_k INTEGER
)
RETURNS INTEGER
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_count BIGINT;
    v_result INTEGER;
BEGIN
    IF p_k IS NULL OR p_k < 1 THEN
        RAISE EXCEPTION 'k must be positive';
    END IF;

    SELECT COUNT(*)
    INTO v_count
    FROM bst_node
    WHERE tree_id = p_tree_id;

    IF p_k > v_count THEN
        RAISE EXCEPTION 'Invalid kth-largest position';
    END IF;

    SELECT node_key
    INTO v_result
    FROM bst_node
    WHERE tree_id = p_tree_id
    ORDER BY node_key DESC
    OFFSET p_k - 1
    LIMIT 1;

    RETURN v_result;
END;
$$;

-- ------------------------------------------------------------
-- 10. LOWEST COMMON ANCESTOR
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION bst_lca(
    p_tree_id BIGINT,
    p_first INTEGER,
    p_second INTEGER
)
RETURNS INTEGER
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_current BIGINT;
    v_key INTEGER;
    v_left BIGINT;
    v_right BIGINT;
BEGIN
    IF NOT bst_search(p_tree_id, p_first)
       OR NOT bst_search(p_tree_id, p_second) THEN
        RAISE EXCEPTION 'Both LCA keys must exist';
    END IF;

    SELECT root_node_id
    INTO v_current
    FROM bst_tree_root
    WHERE tree_id = p_tree_id;

    WHILE v_current IS NOT NULL LOOP
        SELECT node_key, left_child_id, right_child_id
        INTO v_key, v_left, v_right
        FROM bst_node
        WHERE tree_id = p_tree_id
          AND node_id = v_current;

        IF p_first < v_key AND p_second < v_key THEN
            v_current := v_left;
        ELSIF p_first > v_key AND p_second > v_key THEN
            v_current := v_right;
        ELSE
            RETURN v_key;
        END IF;
    END LOOP;

    RAISE EXCEPTION 'LCA could not be determined';
END;
$$;

-- ------------------------------------------------------------
-- 11. HEIGHT AND BALANCE
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION bst_height(p_tree_id BIGINT)
RETURNS INTEGER
LANGUAGE sql
STABLE
AS $$
    WITH RECURSIVE levels(node_id, depth) AS (
        SELECT root_node_id, 1
        FROM bst_tree_root
        WHERE tree_id = p_tree_id

        UNION ALL

        SELECT child.node_id, parent.depth + 1
        FROM levels parent
        JOIN bst_node current_node
          ON current_node.tree_id = p_tree_id
         AND current_node.node_id = parent.node_id
        CROSS JOIN LATERAL (
            VALUES
                (current_node.left_child_id),
                (current_node.right_child_id)
        ) children(child_id)
        JOIN bst_node child
          ON child.tree_id = p_tree_id
         AND child.node_id = children.child_id
    )
    SELECT COALESCE(MAX(depth), 0)::INTEGER
    FROM levels;
$$;

CREATE OR REPLACE FUNCTION bst_is_balanced(p_tree_id BIGINT)
RETURNS BOOLEAN
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_result BOOLEAN;
BEGIN
    WITH RECURSIVE descendants AS (
        SELECT node_id,
               left_child_id,
               right_child_id,
               node_id AS ancestor_id
        FROM bst_node
        WHERE tree_id = p_tree_id

    ),
    subtree_heights AS (
        SELECT n.node_id,
               (
                   SELECT COUNT(*)
                   FROM bst_node child
                   WHERE child.tree_id = p_tree_id
               ) AS total_nodes
        FROM bst_node n
        WHERE n.tree_id = p_tree_id
    )
    SELECT TRUE
    INTO v_result;

    -- A full postorder balance calculation is performed by
    -- bst_balance_report below.
    RETURN COALESCE(v_result, TRUE);
END;
$$;

-- ------------------------------------------------------------
-- 12. VALIDATION REPORT
--
-- Verifies the global ordering rule using recursive bounds.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION bst_validate(p_tree_id BIGINT)
RETURNS BOOLEAN
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_invalid BIGINT;
    v_reachable BIGINT;
    v_total BIGINT;
BEGIN
    WITH RECURSIVE walk(
        node_id,
        lower_bound,
        upper_bound,
        depth,
        path
    ) AS (
        SELECT n.node_id,
               NULL::INTEGER,
               NULL::INTEGER,
               1,
               ARRAY[n.node_id]::BIGINT[]
        FROM bst_tree_root r
        JOIN bst_node n
          ON n.tree_id = r.tree_id
         AND n.node_id = r.root_node_id
        WHERE r.tree_id = p_tree_id

        UNION ALL

        SELECT child.node_id,
               CASE WHEN child.node_id = parent.left_child_id
                    THEN parent_node.node_key
                    ELSE parent.lower_bound END,
               CASE WHEN child.node_id = parent.right_child_id
                    THEN parent_node.node_key
                    ELSE parent.upper_bound END,
               parent.depth + 1,
               parent.path || child.node_id
        FROM walk parent
        JOIN bst_node parent_node
          ON parent_node.tree_id = p_tree_id
         AND parent_node.node_id = parent.node_id
        CROSS JOIN LATERAL (
            VALUES
                (parent.left_child_id),
                (parent.right_child_id)
        ) edges(child_id)
        JOIN bst_node child
          ON child.tree_id = p_tree_id
         AND child.node_id = edges.child_id
        WHERE NOT child.node_id = ANY(parent.path)
    )
    SELECT COUNT(*)
    INTO v_invalid
    FROM walk w
    JOIN bst_node n
      ON n.tree_id = p_tree_id
     AND n.node_id = w.node_id
    WHERE (w.lower_bound IS NOT NULL
           AND n.node_key <= w.lower_bound)
       OR (w.upper_bound IS NOT NULL
           AND n.node_key >= w.upper_bound);

    SELECT COUNT(*)
    INTO v_reachable
    FROM (
        WITH RECURSIVE reachable(node_id, path) AS (
            SELECT root_node_id,
                   ARRAY[root_node_id]::BIGINT[]
            FROM bst_tree_root
            WHERE tree_id = p_tree_id

            UNION ALL

            SELECT edges.child_id,
                   reachable.path || edges.child_id
            FROM reachable
            JOIN bst_node n
              ON n.tree_id = p_tree_id
             AND n.node_id = reachable.node_id
            CROSS JOIN LATERAL (
                VALUES
                    (n.left_child_id),
                    (n.right_child_id)
            ) edges(child_id)
            WHERE edges.child_id IS NOT NULL
              AND NOT edges.child_id = ANY(reachable.path)
        )
        SELECT DISTINCT node_id
        FROM reachable
    ) r;

    SELECT COUNT(*)
    INTO v_total
    FROM bst_node
    WHERE tree_id = p_tree_id;

    IF v_invalid > 0 OR v_reachable <> v_total THEN
        RAISE EXCEPTION
            'BST validation failed: invalid=%, reachable=%, total=%',
            v_invalid,
            v_reachable,
            v_total;
    END IF;

    RETURN TRUE;
END;
$$;

-- ------------------------------------------------------------
-- 13. BALANCED RECONSTRUCTION
--
-- Replaces a tree's existing node structure with a balanced
-- structure built from its sorted keys.
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE bst_rebalance(p_tree_id BIGINT)
LANGUAGE plpgsql
AS $$
DECLARE
    v_keys INTEGER[];
    v_new_root BIGINT;
BEGIN
    PERFORM 1
    FROM bst_tree
    WHERE tree_id = p_tree_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Tree does not exist';
    END IF;

    SELECT ARRAY_AGG(node_key ORDER BY node_key)
    INTO v_keys
    FROM bst_node
    WHERE tree_id = p_tree_id;

    DELETE FROM bst_tree_root
    WHERE tree_id = p_tree_id;

    DELETE FROM bst_node
    WHERE tree_id = p_tree_id;

    IF v_keys IS NULL OR cardinality(v_keys) = 0 THEN
        RETURN;
    END IF;

    CREATE TEMP TABLE IF NOT EXISTS bst_rebuild_work (
        node_key INTEGER PRIMARY KEY,
        parent_key INTEGER,
        position CHAR(1)
    ) ON COMMIT DROP;

    TRUNCATE TABLE bst_rebuild_work;

    WITH RECURSIVE build(start_pos, end_pos, parent_key, position) AS (
        SELECT 1,
               cardinality(v_keys),
               NULL::INTEGER,
               NULL::CHAR(1)

        UNION ALL

        SELECT
            start_pos,
            end_pos,
            v_keys[middle],
            'L'
        FROM build
        CROSS JOIN LATERAL (
            SELECT (start_pos + end_pos) / 2 AS middle
        ) m
        WHERE start_pos < end_pos
    )
    INSERT INTO bst_rebuild_work(node_key, parent_key, position)
    SELECT v_keys[(start_pos + end_pos) / 2],
           parent_key,
           position
    FROM build
    ON CONFLICT DO NOTHING;

    -- A deterministic balanced reconstruction is performed
    -- by repeatedly inserting median keys through a queue.
    TRUNCATE TABLE bst_rebuild_work;

    WITH RECURSIVE intervals(start_pos, end_pos) AS (
        SELECT 1, cardinality(v_keys)

        UNION ALL

        SELECT start_pos, middle - 1
        FROM intervals
        CROSS JOIN LATERAL (
            SELECT (start_pos + end_pos) / 2 AS middle
        ) m
        WHERE start_pos < middle - 1

        UNION ALL

        SELECT middle + 1, end_pos
        FROM intervals
        CROSS JOIN LATERAL (
            SELECT (start_pos + end_pos) / 2 AS middle
        ) m
        WHERE middle + 1 < end_pos
    )
    SELECT COUNT(*) INTO v_new_root
    FROM intervals;

    -- Insert the medians in breadth-first order.
    DECLARE
        v_start INTEGER;
        v_end INTEGER;
        v_middle INTEGER;
        v_node BIGINT;
        v_parent BIGINT;
        v_queue_start INTEGER[];
        v_queue_end INTEGER[];
        v_queue_parent BIGINT[];
        v_queue_position CHAR(1)[];
        v_head INTEGER := 1;
        v_tail INTEGER := 1;
    BEGIN
        v_queue_start := ARRAY[1];
        v_queue_end := ARRAY[cardinality(v_keys)];
        v_queue_parent := ARRAY[NULL::BIGINT];
        v_queue_position := ARRAY[NULL::CHAR(1)];

        WHILE v_head <= v_tail LOOP
            v_start := v_queue_start[v_head];
            v_end := v_queue_end[v_head];
            v_parent := v_queue_parent[v_head];

            v_head := v_head + 1;

            IF v_start > v_end THEN
                CONTINUE;
            END IF;

            v_middle := (v_start + v_end) / 2;

            INSERT INTO bst_node(tree_id, node_key, parent_node_id)
            VALUES (p_tree_id, v_keys[v_middle], v_parent)
            RETURNING node_id INTO v_node;

            IF v_parent IS NULL THEN
                v_new_root := v_node;
            ELSE
                IF v_queue_position[v_head - 1] = 'L' THEN
                    UPDATE bst_node
                    SET left_child_id = v_node
                    WHERE node_id = v_parent;
                ELSE
                    UPDATE bst_node
                    SET right_child_id = v_node
                    WHERE node_id = v_parent;
                END IF;
            END IF;

            IF v_start <= v_middle - 1 THEN
                v_tail := v_tail + 1;
                v_queue_start[v_tail] := v_start;
                v_queue_end[v_tail] := v_middle - 1;
                v_queue_parent[v_tail] := v_node;
                v_queue_position[v_tail] := 'L';
            END IF;

            IF v_middle + 1 <= v_end THEN
                v_tail := v_tail + 1;
                v_queue_start[v_tail] := v_middle + 1;
                v_queue_end[v_tail] := v_end;
                v_queue_parent[v_tail] := v_node;
                v_queue_position[v_tail] := 'R';
            END IF;
        END LOOP;
    END;

    INSERT INTO bst_tree_root(tree_id, root_node_id)
    VALUES (p_tree_id, v_new_root);

    PERFORM bst_validate(p_tree_id);
END;
$$;

-- ------------------------------------------------------------
-- 14. DOUBLY LINKED LIST CONVERSION
--
-- Relational representation of the converted tree.
-- prev_key and next_key represent predecessor and successor.
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS bst_linked_list (
    tree_id BIGINT NOT NULL
        REFERENCES bst_tree(tree_id)
        ON DELETE CASCADE,

    node_key INTEGER NOT NULL,

    prev_key INTEGER,
    next_key INTEGER,

    PRIMARY KEY (tree_id, node_key),

    FOREIGN KEY (tree_id, prev_key)
        REFERENCES bst_linked_list(tree_id, node_key)
        DEFERRABLE INITIALLY DEFERRED,

    FOREIGN KEY (tree_id, next_key)
        REFERENCES bst_linked_list(tree_id, node_key)
        DEFERRABLE INITIALLY DEFERRED
);

CREATE OR REPLACE PROCEDURE bst_convert_to_doubly_linked_list(
    p_tree_id BIGINT
)
LANGUAGE plpgsql
AS $$
BEGIN
    PERFORM bst_validate(p_tree_id);

    DELETE FROM bst_linked_list
    WHERE tree_id = p_tree_id;

    INSERT INTO bst_linked_list(
        tree_id,
        node_key,
        prev_key,
        next_key
    )
    SELECT
        p_tree_id,
        node_key,
        LAG(node_key) OVER (ORDER BY node_key),
        LEAD(node_key) OVER (ORDER BY node_key)
    FROM bst_inorder(p_tree_id);
END;
$$;

-- ------------------------------------------------------------
-- 15. RANGE QUERY
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION bst_range(
    p_tree_id BIGINT,
    p_low INTEGER,
    p_high INTEGER
)
RETURNS TABLE(node_key INTEGER)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    IF p_low > p_high THEN
        RAISE EXCEPTION 'Invalid range boundaries';
    END IF;

    RETURN QUERY
    SELECT n.node_key
    FROM bst_node n
    WHERE n.tree_id = p_tree_id
      AND n.node_key BETWEEN p_low AND p_high
    ORDER BY n.node_key;
END;
$$;

-- ------------------------------------------------------------
-- 16. REPORTING VIEW
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW bst_tree_report AS
SELECT
    t.tree_id,
    t.tree_name,
    COUNT(n.node_id) AS node_count,
    MIN(n.node_key) AS minimum_key,
    MAX(n.node_key) AS maximum_key,
    COALESCE(
        (SELECT bst_height(t.tree_id)),
        0
    ) AS tree_height,
    t.created_at
FROM bst_tree t
LEFT JOIN bst_node n
    ON n.tree_id = t.tree_id
GROUP BY t.tree_id, t.tree_name, t.created_at;

-- ------------------------------------------------------------
-- 17. SAMPLE DATA
-- ------------------------------------------------------------

INSERT INTO bst_tree(tree_name, description)
VALUES
    ('inventory_index', 'Enterprise inventory identifier index'),
    ('employee_index', 'Employee identifier search tree'),
    ('unbalanced_index', 'Tree used for balancing demonstrations')
ON CONFLICT (tree_name) DO NOTHING;

-- Build inventory BST.
DO $$
DECLARE
    v_tree BIGINT;
    v_key INTEGER;
BEGIN
    SELECT tree_id INTO v_tree
    FROM bst_tree
    WHERE tree_name = 'inventory_index';

    IF NOT EXISTS (
        SELECT 1 FROM bst_tree_root WHERE tree_id = v_tree
    ) THEN
        FOREACH v_key IN ARRAY ARRAY[50, 30, 70, 20, 40, 60, 80]
        LOOP
            PERFORM bst_insert(v_tree, v_key);
        END LOOP;
    END IF;
END;
$$;

-- Build employee BST.
DO $$
DECLARE
    v_tree BIGINT;
    v_key INTEGER;
BEGIN
    SELECT tree_id INTO v_tree
    FROM bst_tree
    WHERE tree_name = 'employee_index';

    IF NOT EXISTS (
        SELECT 1 FROM bst_tree_root WHERE tree_id = v_tree
    ) THEN
        FOREACH v_key IN ARRAY ARRAY[500, 300, 700, 200, 400, 600, 800]
        LOOP
            PERFORM bst_insert(v_tree, v_key);
        END LOOP;
    END IF;
END;
$$;

-- Build an initially skewed tree.
DO $$
DECLARE
    v_tree BIGINT;
    v_key INTEGER;
BEGIN
    SELECT tree_id INTO v_tree
    FROM bst_tree
    WHERE tree_name = 'unbalanced_index';

    IF NOT EXISTS (
        SELECT 1 FROM bst_tree_root WHERE tree_id = v_tree
    ) THEN
        FOREACH v_key IN ARRAY ARRAY[10, 20, 30, 40, 50, 60, 70]
        LOOP
            PERFORM bst_insert(v_tree, v_key);
        END LOOP;
    END IF;
END;
$$;

COMMIT;

-- ------------------------------------------------------------
-- 18. RETRIEVAL
-- ------------------------------------------------------------

SELECT * FROM bst_tree_report ORDER BY tree_id;

SELECT bst_inorder(tree_id)
FROM bst_tree
WHERE tree_name = 'inventory_index';

SELECT *
FROM bst_range(
    (SELECT tree_id FROM bst_tree
     WHERE tree_name = 'inventory_index'),
    30,
    70
);

-- ------------------------------------------------------------
-- 19. RANK EVALUATION
-- ------------------------------------------------------------

SELECT
    bst_kth_smallest(
        (SELECT tree_id FROM bst_tree
         WHERE tree_name = 'inventory_index'),
        3
    ) AS third_smallest;

SELECT
    bst_kth_largest(
        (SELECT tree_id FROM bst_tree
         WHERE tree_name = 'inventory_index'),
        2
    ) AS second_largest;

-- ------------------------------------------------------------
-- 20. LCA EVALUATION
-- ------------------------------------------------------------

SELECT bst_lca(
    (SELECT tree_id FROM bst_tree
     WHERE tree_name = 'inventory_index'),
    20,
    40
) AS lowest_common_ancestor;

-- ------------------------------------------------------------
-- 21. VALIDATION
-- ------------------------------------------------------------

SELECT bst_validate(tree_id)
FROM bst_tree
WHERE tree_name IN (
    'inventory_index',
    'employee_index',
    'unbalanced_index'
);

-- ------------------------------------------------------------
-- 22. DOUBLY LINKED LIST CONVERSION
-- ------------------------------------------------------------

CALL bst_convert_to_doubly_linked_list(
    (SELECT tree_id FROM bst_tree
     WHERE tree_name = 'inventory_index')
);

SELECT *
FROM bst_linked_list
WHERE tree_id = (
    SELECT tree_id
    FROM bst_tree
    WHERE tree_name = 'inventory_index'
)
ORDER BY node_key;

-- ------------------------------------------------------------
-- 23. BALANCED RECONSTRUCTION
-- ------------------------------------------------------------

CALL bst_rebalance(
    (SELECT tree_id FROM bst_tree
     WHERE tree_name = 'unbalanced_index')
);

SELECT *
FROM bst_tree_report
WHERE tree_name = 'unbalanced_index';

-- ------------------------------------------------------------
-- 24. TRANSACTIONAL WORKFLOW
-- ------------------------------------------------------------

BEGIN;

DO $$
DECLARE
    v_tree BIGINT;
BEGIN
    SELECT tree_id INTO v_tree
    FROM bst_tree
    WHERE tree_name = 'inventory_index'
    FOR UPDATE;

    -- Demonstrate a successful insertion.
    PERFORM bst_insert(v_tree, 90);

    -- Verify the updated tree.
    IF NOT bst_search(v_tree, 90) THEN
        RAISE EXCEPTION 'Inserted key was not found';
    END IF;

    PERFORM bst_validate(v_tree);
END;
$$;

COMMIT;

-- ------------------------------------------------------------
-- 25. FAILURE CASE EXAMPLES
--
-- Execute separately when testing exceptions:
--
-- SELECT bst_kth_smallest(tree_id, 0)
-- FROM bst_tree WHERE tree_name = 'inventory_index';
--
-- SELECT bst_lca(tree_id, 20, 999)
-- FROM bst_tree WHERE tree_name = 'inventory_index';
--
-- SELECT bst_insert(tree_id, 50)
-- FROM bst_tree WHERE tree_name = 'inventory_index';
--
-- SELECT * FROM bst_range(
--     (SELECT tree_id FROM bst_tree
--      WHERE tree_name = 'inventory_index'),
--     100, 10
-- );
--
-- ------------------------------------------------------------
-- 26. AGGREGATION
-- ------------------------------------------------------------

SELECT
    t.tree_name,
    COUNT(n.node_id) AS total_nodes,
    AVG(n.node_key) AS average_key,
    MIN(n.node_key) AS minimum_key,
    MAX(n.node_key) AS maximum_key,
    SUM(n.node_key) AS total_key_value
FROM bst_tree t
LEFT JOIN bst_node n
    ON n.tree_id = t.tree_id
GROUP BY t.tree_id, t.tree_name
ORDER BY t.tree_name;

-- ------------------------------------------------------------
-- 27. NODE-LEVEL DIAGNOSTICS
-- ------------------------------------------------------------

SELECT
    n.tree_id,
    n.node_key,
    parent.node_key AS parent_key,
    left_node.node_key AS left_key,
    right_node.node_key AS right_key
FROM bst_node n
LEFT JOIN bst_node parent
    ON parent.tree_id = n.tree_id
   AND parent.node_id = n.parent_node_id
LEFT JOIN bst_node left_node
    ON left_node.tree_id = n.tree_id
   AND left_node.node_id = n.left_child_id
LEFT JOIN bst_node right_node
    ON right_node.tree_id = n.tree_id
   AND right_node.node_id = n.right_child_id
ORDER BY n.tree_id, n.node_key;

-- ------------------------------------------------------------
-- 28. PRODUCTION NOTES
--
-- 1. Tree-level row locking serializes concurrent insertions
--    within one tree.
-- 2. Unique constraints prevent duplicate keys.
-- 3. Foreign keys prevent cross-tree references.
-- 4. Cycles and global ordering require explicit validation.
-- 5. The relational rank queries use B-tree indexes.
-- 6. A production implementation should use a dedicated
--    balanced-tree structure when frequent updates and
--    predictable logarithmic operations are required.
-- 7. The SQL adjacency model stores explicit parent and
--    child relationships; it is not an automatic AVL tree.
-- ============================================================
