-- ============================================================
-- BST TRAVERSAL AND VALIDATION
-- PostgreSQL implementation
--
-- Domain: Enterprise asset identifier registry
--
-- Models:
--   1. BST nodes and parent-child relationships
--   2. Unique integer keys
--   3. Structural integrity
--   4. Inorder, preorder, postorder and level-order traversal
--   5. Minimum and maximum
--   6. Floor and ceiling
--   7. Range queries
--   8. Successor and predecessor
--   9. Insert and delete operations
--  10. Audit history and validation reports
--
-- Important:
-- A relational table does not automatically maintain BST
-- ordering. The functions below explicitly enforce the
-- parent-child ordering rules.
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS bst_lab;

SET search_path TO bst_lab, public;

-- ------------------------------------------------------------
-- 1. Domain tables
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS registries (
    registry_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    registry_name VARCHAR(120) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS bst_nodes (
    node_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    registry_id BIGINT NOT NULL
        REFERENCES registries(registry_id)
        ON DELETE CASCADE,

    node_key BIGINT NOT NULL,

    parent_node_id BIGINT,

    left_child_id BIGINT,
    right_child_id BIGINT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_registry_key
        UNIQUE (registry_id, node_key),

    CONSTRAINT uq_registry_node
        UNIQUE (registry_id, node_id),

    CONSTRAINT ck_no_self_parent
        CHECK (parent_node_id IS NULL OR parent_node_id <> node_id),

    CONSTRAINT ck_no_self_left
        CHECK (left_child_id IS NULL OR left_child_id <> node_id),

    CONSTRAINT ck_no_self_right
        CHECK (right_child_id IS NULL OR right_child_id <> node_id),

    CONSTRAINT ck_distinct_children
        CHECK (
            left_child_id IS NULL
            OR right_child_id IS NULL
            OR left_child_id <> right_child_id
        ),

    CONSTRAINT fk_parent
        FOREIGN KEY (registry_id, parent_node_id)
        REFERENCES bst_nodes(registry_id, node_id)
        DEFERRABLE INITIALLY DEFERRED,

    CONSTRAINT fk_left_child
        FOREIGN KEY (registry_id, left_child_id)
        REFERENCES bst_nodes(registry_id, node_id)
        DEFERRABLE INITIALLY DEFERRED,

    CONSTRAINT fk_right_child
        FOREIGN KEY (registry_id, right_child_id)
        REFERENCES bst_nodes(registry_id, node_id)
        DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE IF NOT EXISTS registry_roots (
    registry_id BIGINT PRIMARY KEY
        REFERENCES registries(registry_id)
        ON DELETE CASCADE,

    root_node_id BIGINT,

    CONSTRAINT fk_registry_root
        FOREIGN KEY (registry_id, root_node_id)
        REFERENCES bst_nodes(registry_id, node_id)
        DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE IF NOT EXISTS bst_audit_log (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    registry_id BIGINT NOT NULL
        REFERENCES registries(registry_id)
        ON DELETE CASCADE,

    operation VARCHAR(20) NOT NULL
        CHECK (
            operation IN (
                'INSERT',
                'DELETE',
                'VALIDATE',
                'REBUILD'
            )
        ),

    node_key BIGINT,
    operation_status VARCHAR(20) NOT NULL
        CHECK (
            operation_status IN (
                'SUCCESS',
                'FAILED'
            )
        ),

    details TEXT,
    performed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------
-- 2. Indexes
-- ------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_bst_registry_parent
    ON bst_nodes(registry_id, parent_node_id);

CREATE INDEX IF NOT EXISTS idx_bst_registry_left
    ON bst_nodes(registry_id, left_child_id);

CREATE INDEX IF NOT EXISTS idx_bst_registry_right
    ON bst_nodes(registry_id, right_child_id);

CREATE INDEX IF NOT EXISTS idx_bst_registry_key
    ON bst_nodes(registry_id, node_key);

CREATE INDEX IF NOT EXISTS idx_bst_audit_time
    ON bst_audit_log(registry_id, performed_at DESC);

-- ------------------------------------------------------------
-- 3. Automatic registry root initialization
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION initialize_registry_root()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO registry_roots(registry_id, root_node_id)
    VALUES (NEW.registry_id, NULL)
    ON CONFLICT (registry_id) DO NOTHING;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_initialize_registry_root
ON registries;

CREATE TRIGGER trg_initialize_registry_root
AFTER INSERT ON registries
FOR EACH ROW
EXECUTE FUNCTION initialize_registry_root();

-- ------------------------------------------------------------
-- 4. Structural consistency trigger
--
-- Checks reciprocal parent-child relationships.
-- Full BST ordering is evaluated by validate_bst().
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION check_bst_node_relationships()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.parent_node_id IS NOT NULL THEN
        IF NOT EXISTS (
            SELECT 1
            FROM bst_nodes p
            WHERE p.registry_id = NEW.registry_id
              AND p.node_id = NEW.parent_node_id
        ) THEN
            RAISE EXCEPTION 'Parent node does not exist.';
        END IF;
    END IF;

    IF NEW.left_child_id IS NOT NULL THEN
        IF NOT EXISTS (
            SELECT 1
            FROM bst_nodes c
            WHERE c.registry_id = NEW.registry_id
              AND c.node_id = NEW.left_child_id
        ) THEN
            RAISE EXCEPTION 'Left child does not exist.';
        END IF;
    END IF;

    IF NEW.right_child_id IS NOT NULL THEN
        IF NOT EXISTS (
            SELECT 1
            FROM bst_nodes c
            WHERE c.registry_id = NEW.registry_id
              AND c.node_id = NEW.right_child_id
        ) THEN
            RAISE EXCEPTION 'Right child does not exist.';
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_check_bst_node_relationships
ON bst_nodes;

CREATE CONSTRAINT TRIGGER trg_check_bst_node_relationships
AFTER INSERT OR UPDATE ON bst_nodes
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW
EXECUTE FUNCTION check_bst_node_relationships();

-- ------------------------------------------------------------
-- 5. Insert operation
--
-- Uses row-level locking on the registry root.
-- A transaction prevents partial structural updates.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION bst_insert(
    p_registry_id BIGINT,
    p_key BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_root BIGINT;
    v_current BIGINT;
    v_parent BIGINT;
    v_new_node BIGINT;
    v_current_key BIGINT;
BEGIN
    IF p_key IS NULL THEN
        RAISE EXCEPTION 'BST key cannot be NULL.';
    END IF;

    PERFORM 1
    FROM registries
    WHERE registry_id = p_registry_id
      AND is_active = TRUE
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Registry does not exist or is inactive.';
    END IF;

    INSERT INTO registry_roots(registry_id, root_node_id)
    VALUES (p_registry_id, NULL)
    ON CONFLICT (registry_id) DO NOTHING;

    SELECT root_node_id
    INTO v_root
    FROM registry_roots
    WHERE registry_id = p_registry_id
    FOR UPDATE;

    v_current := v_root;

    WHILE v_current IS NOT NULL LOOP
        SELECT node_key
        INTO v_current_key
        FROM bst_nodes
        WHERE registry_id = p_registry_id
          AND node_id = v_current;

        IF p_key = v_current_key THEN
            RAISE EXCEPTION 'Duplicate BST key: %', p_key;
        END IF;

        v_parent := v_current;

        IF p_key < v_current_key THEN
            SELECT left_child_id
            INTO v_current
            FROM bst_nodes
            WHERE registry_id = p_registry_id
              AND node_id = v_current;
        ELSE
            SELECT right_child_id
            INTO v_current
            FROM bst_nodes
            WHERE registry_id = p_registry_id
              AND node_id = v_current;
        END IF;
    END LOOP;

    INSERT INTO bst_nodes(
        registry_id,
        node_key,
        parent_node_id
    )
    VALUES (
        p_registry_id,
        p_key,
        v_parent
    )
    RETURNING node_id INTO v_new_node;

    IF v_parent IS NULL THEN
        UPDATE registry_roots
        SET root_node_id = v_new_node
        WHERE registry_id = p_registry_id;
    ELSE
        UPDATE bst_nodes
        SET
            left_child_id = CASE
                WHEN p_key < (
                    SELECT node_key
                    FROM bst_nodes
                    WHERE node_id = v_parent
                )
                THEN v_new_node
                ELSE left_child_id
            END,

            right_child_id = CASE
                WHEN p_key > (
                    SELECT node_key
                    FROM bst_nodes
                    WHERE node_id = v_parent
                )
                THEN v_new_node
                ELSE right_child_id
            END
        WHERE registry_id = p_registry_id
          AND node_id = v_parent;
    END IF;

    INSERT INTO bst_audit_log(
        registry_id,
        operation,
        node_key,
        operation_status,
        details
    )
    VALUES (
        p_registry_id,
        'INSERT',
        p_key,
        'SUCCESS',
        'BST node inserted.'
    );

    RETURN v_new_node;
END;
$$;

-- ------------------------------------------------------------
-- 6. BST validation
--
-- Validates:
-- - Exactly one root for a non-empty tree
-- - Parent-child consistency
-- - Strict lower and upper ordering
-- - No cycles or repeated node visits
-- - Every node is reachable from the root
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_bst(
    p_registry_id BIGINT
)
RETURNS TABLE (
    is_valid BOOLEAN,
    node_count BIGINT,
    reachable_count BIGINT,
    validation_message TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_root BIGINT;
    v_total BIGINT;
    v_reachable BIGINT;
    v_root_count BIGINT;
    v_invalid BIGINT;
    v_cycle BIGINT;
BEGIN
    PERFORM 1
    FROM registries
    WHERE registry_id = p_registry_id;

    IF NOT FOUND THEN
        RETURN QUERY SELECT
            FALSE, 0::BIGINT, 0::BIGINT,
            'Registry does not exist.'::TEXT;
        RETURN;
    END IF;

    SELECT COUNT(*)
    INTO v_total
    FROM bst_nodes
    WHERE registry_id = p_registry_id;

    SELECT root_node_id
    INTO v_root
    FROM registry_roots
    WHERE registry_id = p_registry_id;

    SELECT COUNT(*)
    INTO v_root_count
    FROM bst_nodes
    WHERE registry_id = p_registry_id
      AND parent_node_id IS NULL;

    IF v_total = 0 THEN
        IF v_root IS NULL AND v_root_count = 0 THEN
            RETURN QUERY SELECT
                TRUE, 0::BIGINT, 0::BIGINT,
                'Valid empty BST.'::TEXT;
        ELSE
            RETURN QUERY SELECT
                FALSE, v_total, 0::BIGINT,
                'Invalid empty-tree root state.'::TEXT;
        END IF;
        RETURN;
    END IF;

    IF v_root IS NULL OR v_root_count <> 1 THEN
        RETURN QUERY SELECT
            FALSE, v_total, 0::BIGINT,
            'Non-empty tree must have exactly one root.'::TEXT;
        RETURN;
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM bst_nodes
        WHERE registry_id = p_registry_id
          AND node_id = v_root
          AND parent_node_id IS NULL
    ) THEN
        RETURN QUERY SELECT
            FALSE, v_total, 0::BIGINT,
            'Root reference is invalid.'::TEXT;
        RETURN;
    END IF;

    WITH RECURSIVE walk(
        node_id,
        node_key,
        lower_bound,
        upper_bound,
        path,
        cycle
    ) AS (
        SELECT
            n.node_id,
            n.node_key,
            NULL::BIGINT,
            NULL::BIGINT,
            ARRAY[n.node_id],
            FALSE
        FROM bst_nodes n
        WHERE n.registry_id = p_registry_id
          AND n.node_id = v_root

        UNION ALL

        SELECT
            c.node_id,
            c.node_key,

            CASE
                WHEN edge.side = 'LEFT'
                    THEN w.lower_bound
                ELSE w.node_key
            END,

            CASE
                WHEN edge.side = 'LEFT'
                    THEN w.node_key
                ELSE w.upper_bound
            END,

            w.path || c.node_id,
            c.node_id = ANY(w.path)

        FROM walk w

        JOIN bst_nodes p
          ON p.registry_id = p_registry_id
         AND p.node_id = w.node_id

        CROSS JOIN LATERAL (
            VALUES
                (p.left_child_id, 'LEFT'),
                (p.right_child_id, 'RIGHT')
        ) AS edge(child_id, side)

        JOIN bst_nodes c
          ON c.registry_id = p_registry_id
         AND c.node_id = edge.child_id

        WHERE edge.child_id IS NOT NULL
          AND NOT w.cycle
    )
    SELECT
        COUNT(DISTINCT node_id),
        COUNT(*) FILTER (WHERE cycle),
        COUNT(*) FILTER (
            WHERE
                (lower_bound IS NOT NULL
                    AND node_key <= lower_bound)
                OR
                (upper_bound IS NOT NULL
                    AND node_key >= upper_bound)
        )
    INTO
        v_reachable,
        v_cycle,
        v_invalid
    FROM walk;

    IF v_cycle > 0 THEN
        RETURN QUERY SELECT
            FALSE, v_total, v_reachable,
            'Cycle detected in BST.'::TEXT;
        RETURN;
    END IF;

    IF v_invalid > 0 THEN
        RETURN QUERY SELECT
            FALSE, v_total, v_reachable,
            'BST ordering invariant violated.'::TEXT;
        RETURN;
    END IF;

    IF v_reachable <> v_total THEN
        RETURN QUERY SELECT
            FALSE, v_total, v_reachable,
            'Unreachable or disconnected nodes detected.'::TEXT;
        RETURN;
    END IF;

    IF EXISTS (
        SELECT 1
        FROM bst_nodes child
        LEFT JOIN bst_nodes parent
          ON parent.registry_id = child.registry_id
         AND parent.node_id = child.parent_node_id
        WHERE child.registry_id = p_registry_id
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
            FALSE, v_total, v_reachable,
            'Parent-child relationship is inconsistent.'::TEXT;
        RETURN;
    END IF;

    RETURN QUERY SELECT
        TRUE,
        v_total,
        v_reachable,
        'BST is structurally valid.'::TEXT;
END;
$$;

-- ------------------------------------------------------------
-- 7. Inorder traversal
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION bst_inorder(
    p_registry_id BIGINT
)
RETURNS TABLE (
    node_key BIGINT,
    depth INTEGER
)
LANGUAGE sql
STABLE
AS $$
    WITH RECURSIVE walk AS (
        SELECT
            n.node_id,
            n.node_key,
            n.left_child_id,
            n.right_child_id,
            1 AS depth,
            ARRAY[n.node_id] AS path
        FROM bst_nodes n
        JOIN registry_roots r
          ON r.registry_id = n.registry_id
         AND r.root_node_id = n.node_id
        WHERE n.registry_id = p_registry_id

        UNION ALL

        SELECT
            c.node_id,
            c.node_key,
            c.left_child_id,
            c.right_child_id,
            w.depth + 1,
            w.path || c.node_id
        FROM walk w
        JOIN bst_nodes c
          ON c.node_id = w.left_child_id
        WHERE NOT c.node_id = ANY(w.path)

        UNION ALL

        SELECT
            c.node_id,
            c.node_key,
            c.left_child_id,
            c.right_child_id,
            w.depth + 1,
            w.path || c.node_id
        FROM walk w
        JOIN bst_nodes c
          ON c.node_id = w.right_child_id
        WHERE NOT c.node_id = ANY(w.path)
    ),
    ordered AS (
        SELECT
            node_key,
            depth,
            ROW_NUMBER() OVER (
                ORDER BY
                    (
                        SELECT COUNT(*)
                        FROM bst_nodes ancestor
                        WHERE ancestor.registry_id = p_registry_id
                          AND ancestor.node_key < walk.node_key
                    )
            ) AS position
        FROM walk
    )
    SELECT node_key, depth
    FROM ordered
    ORDER BY position;
$$;

-- ------------------------------------------------------------
-- 8. Preorder and postorder traversal
--
-- DFS path sorting encodes traversal order.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION bst_depth_first(
    p_registry_id BIGINT,
    p_order TEXT
)
RETURNS TABLE (
    node_key BIGINT,
    depth INTEGER
)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    IF p_order NOT IN ('PREORDER', 'POSTORDER') THEN
        RAISE EXCEPTION 'Unsupported traversal order.';
    END IF;

    RETURN QUERY
    WITH RECURSIVE walk AS (
        SELECT
            n.node_id,
            n.node_key,
            n.left_child_id,
            n.right_child_id,
            1 AS depth,
            ARRAY[0] AS path
        FROM bst_nodes n
        JOIN registry_roots r
          ON r.registry_id = n.registry_id
         AND r.root_node_id = n.node_id
        WHERE n.registry_id = p_registry_id

        UNION ALL

        SELECT
            c.node_id,
            c.node_key,
            c.left_child_id,
            c.right_child_id,
            w.depth + 1,
            w.path || edge.position
        FROM walk w
        CROSS JOIN LATERAL (
            VALUES
                (w.left_child_id, 1),
                (w.right_child_id, 2)
        ) edge(child_id, position)
        JOIN bst_nodes c
          ON c.registry_id = p_registry_id
         AND c.node_id = edge.child_id
        WHERE edge.child_id IS NOT NULL
          AND NOT edge.child_id = ANY(
              ARRAY(
                  SELECT node_id
                  FROM bst_nodes
                  WHERE registry_id = p_registry_id
                    AND node_id = edge.child_id
              )
          )
    )
    SELECT
        w.node_key,
        w.depth
    FROM walk w
    ORDER BY
        CASE WHEN p_order = 'PREORDER'
            THEN w.path
        END,
        CASE WHEN p_order = 'POSTORDER'
            THEN array_length(w.path, 1)
        END DESC,
        CASE WHEN p_order = 'POSTORDER'
            THEN w.path
        END DESC;
END;
$$;

-- ------------------------------------------------------------
-- 9. Level-order traversal
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION bst_level_order(
    p_registry_id BIGINT
)
RETURNS TABLE (
    node_key BIGINT,
    depth INTEGER
)
LANGUAGE sql
STABLE
AS $$
    WITH RECURSIVE walk AS (
        SELECT
            n.node_id,
            n.node_key,
            n.left_child_id,
            n.right_child_id,
            1 AS depth,
            ARRAY[0] AS path
        FROM bst_nodes n
        JOIN registry_roots r
          ON r.registry_id = n.registry_id
         AND r.root_node_id = n.node_id
        WHERE n.registry_id = p_registry_id

        UNION ALL

        SELECT
            c.node_id,
            c.node_key,
            c.left_child_id,
            c.right_child_id,
            w.depth + 1,
            w.path || edge.position
        FROM walk w
        CROSS JOIN LATERAL (
            VALUES
                (w.left_child_id, 1),
                (w.right_child_id, 2)
        ) edge(child_id, position)
        JOIN bst_nodes c
          ON c.registry_id = p_registry_id
         AND c.node_id = edge.child_id
    )
    SELECT node_key, depth
    FROM walk
    ORDER BY depth, path;
$$;

-- ------------------------------------------------------------
-- 10. Minimum and maximum
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION bst_minimum(
    p_registry_id BIGINT
)
RETURNS BIGINT
LANGUAGE sql
STABLE
AS $$
    SELECT node_key
    FROM bst_nodes
    WHERE registry_id = p_registry_id
    ORDER BY node_key ASC
    LIMIT 1;
$$;

CREATE OR REPLACE FUNCTION bst_maximum(
    p_registry_id BIGINT
)
RETURNS BIGINT
LANGUAGE sql
STABLE
AS $$
    SELECT node_key
    FROM bst_nodes
    WHERE registry_id = p_registry_id
    ORDER BY node_key DESC
    LIMIT 1;
$$;

-- ------------------------------------------------------------
-- 11. Floor and ceiling
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION bst_floor(
    p_registry_id BIGINT,
    p_key BIGINT
)
RETURNS BIGINT
LANGUAGE sql
STABLE
AS $$
    SELECT node_key
    FROM bst_nodes
    WHERE registry_id = p_registry_id
      AND node_key <= p_key
    ORDER BY node_key DESC
    LIMIT 1;
$$;

CREATE OR REPLACE FUNCTION bst_ceiling(
    p_registry_id BIGINT,
    p_key BIGINT
)
RETURNS BIGINT
LANGUAGE sql
STABLE
AS $$
    SELECT node_key
    FROM bst_nodes
    WHERE registry_id = p_registry_id
      AND node_key >= p_key
    ORDER BY node_key ASC
    LIMIT 1;
$$;

-- ------------------------------------------------------------
-- 12. Inclusive range query
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION bst_range(
    p_registry_id BIGINT,
    p_low BIGINT,
    p_high BIGINT
)
RETURNS TABLE(node_key BIGINT)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    IF p_low > p_high THEN
        RAISE EXCEPTION 'Invalid range boundaries.';
    END IF;

    RETURN QUERY
    SELECT n.node_key
    FROM bst_nodes n
    WHERE n.registry_id = p_registry_id
      AND n.node_key BETWEEN p_low AND p_high
    ORDER BY n.node_key;
END;
$$;

-- ------------------------------------------------------------
-- 13. Successor and predecessor
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION bst_successor(
    p_registry_id BIGINT,
    p_key BIGINT
)
RETURNS BIGINT
LANGUAGE sql
STABLE
AS $$
    SELECT node_key
    FROM bst_nodes
    WHERE registry_id = p_registry_id
      AND node_key > p_key
    ORDER BY node_key
    LIMIT 1;
$$;

CREATE OR REPLACE FUNCTION bst_predecessor(
    p_registry_id BIGINT,
    p_key BIGINT
)
RETURNS BIGINT
LANGUAGE sql
STABLE
AS $$
    SELECT node_key
    FROM bst_nodes
    WHERE registry_id = p_registry_id
      AND node_key < p_key
    ORDER BY node_key DESC
    LIMIT 1;
$$;

-- ------------------------------------------------------------
-- 14. Level-based registry report
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW bst_registry_report AS
SELECT
    r.registry_id,
    r.registry_name,
    COUNT(n.node_id) AS total_nodes,
    MIN(n.node_key) AS minimum_key,
    MAX(n.node_key) AS maximum_key,
    COUNT(n.node_id) FILTER (
        WHERE n.left_child_id IS NULL
          AND n.right_child_id IS NULL
    ) AS leaf_nodes,
    COUNT(n.node_id) FILTER (
        WHERE n.left_child_id IS NOT NULL
           OR n.right_child_id IS NOT NULL
    ) AS internal_nodes,
    r.is_active
FROM registries r
LEFT JOIN bst_nodes n
    ON n.registry_id = r.registry_id
GROUP BY
    r.registry_id,
    r.registry_name,
    r.is_active;

-- ------------------------------------------------------------
-- 15. Sample registries
-- ------------------------------------------------------------

INSERT INTO registries(
    registry_name,
    description
)
VALUES
(
    'ASSET_PRIMARY',
    'Primary enterprise asset identifier index.'
),
(
    'ASSET_SECONDARY',
    'Secondary registry for additional assets.'
)
ON CONFLICT (registry_name) DO NOTHING;

-- ------------------------------------------------------------
-- 16. Populate primary BST
-- ------------------------------------------------------------

DO $$
DECLARE
    v_registry BIGINT;
    v_key BIGINT;
BEGIN
    SELECT registry_id
    INTO v_registry
    FROM registries
    WHERE registry_name = 'ASSET_PRIMARY';

    FOREACH v_key IN ARRAY ARRAY[
        5000, 3000, 7000, 2000, 4000, 6000, 8000
    ]
    LOOP
        IF NOT EXISTS (
            SELECT 1
            FROM bst_nodes
            WHERE registry_id = v_registry
              AND node_key = v_key
        ) THEN
            PERFORM bst_insert(v_registry, v_key);
        END IF;
    END LOOP;
END;
$$;

-- ------------------------------------------------------------
-- 17. Populate secondary BST
-- ------------------------------------------------------------

DO $$
DECLARE
    v_registry BIGINT;
BEGIN
    SELECT registry_id
    INTO v_registry
    FROM registries
    WHERE registry_name = 'ASSET_SECONDARY';

    PERFORM bst_insert(v_registry, 150);
    PERFORM bst_insert(v_registry, 100);
    PERFORM bst_insert(v_registry, 200);
END;
$$;

-- ------------------------------------------------------------
-- 18. Retrieval examples
-- ------------------------------------------------------------

SELECT
    registry_name,
    total_nodes,
    minimum_key,
    maximum_key,
    leaf_nodes,
    internal_nodes
FROM bst_registry_report
ORDER BY registry_name;

SELECT bst_inorder(registry_id)
FROM registries
WHERE registry_name = 'ASSET_PRIMARY';

SELECT *
FROM bst_level_order(
    (
        SELECT registry_id
        FROM registries
        WHERE registry_name = 'ASSET_PRIMARY'
    )
);

-- ------------------------------------------------------------
-- 19. Boundary queries
-- ------------------------------------------------------------

SELECT
    bst_minimum(registry_id) AS minimum_key,
    bst_maximum(registry_id) AS maximum_key,
    bst_floor(registry_id, 4500) AS floor_value,
    bst_ceiling(registry_id, 4500) AS ceiling_value,
    bst_successor(registry_id, 5000) AS successor_value,
    bst_predecessor(registry_id, 5000) AS predecessor_value
FROM registries
WHERE registry_name = 'ASSET_PRIMARY';

-- ------------------------------------------------------------
-- 20. Range retrieval
-- ------------------------------------------------------------

SELECT *
FROM bst_range(
    (
        SELECT registry_id
        FROM registries
        WHERE registry_name = 'ASSET_PRIMARY'
    ),
    3000,
    7000
);

-- ------------------------------------------------------------
-- 21. Validation report
-- ------------------------------------------------------------

SELECT *
FROM validate_bst(
    (
        SELECT registry_id
        FROM registries
        WHERE registry_name = 'ASSET_PRIMARY'
    )
);

-- ------------------------------------------------------------
-- 22. Aggregation and evaluation
-- ------------------------------------------------------------

SELECT
    registry_id,
    COUNT(*) AS total_nodes,
    AVG(node_key) AS average_key,
    MIN(node_key) AS minimum_key,
    MAX(node_key) AS maximum_key,
    COUNT(*) FILTER (
        WHERE node_key BETWEEN 3000 AND 7000
    ) AS keys_in_operational_range
FROM bst_nodes
GROUP BY registry_id
ORDER BY registry_id;

-- ------------------------------------------------------------
-- 23. Duplicate insertion failure demonstration
--
-- The exception is caught in a subtransaction so that the
-- remainder of the script can execute.
-- ------------------------------------------------------------

DO $$
DECLARE
    v_registry BIGINT;
BEGIN
    SELECT registry_id
    INTO v_registry
    FROM registries
    WHERE registry_name = 'ASSET_PRIMARY';

    BEGIN
        PERFORM bst_insert(v_registry, 5000);
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Expected duplicate rejection: %', SQLERRM;
    END;
END;
$$;

-- ------------------------------------------------------------
-- 24. Invalid range failure demonstration
-- ------------------------------------------------------------

DO $$
DECLARE
    v_registry BIGINT;
BEGIN
    SELECT registry_id
    INTO v_registry
    FROM registries
    WHERE registry_name = 'ASSET_PRIMARY';

    BEGIN
        PERFORM *
        FROM bst_range(v_registry, 8000, 2000);
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Expected range rejection: %', SQLERRM;
    END;
END;
$$;

-- ------------------------------------------------------------
-- 25. Transactional deletion demonstration
--
-- Demonstrates a controlled structural update.
-- Deletion of a node with two children uses its inorder
-- successor as replacement.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION bst_delete(
    p_registry_id BIGINT,
    p_key BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_target BIGINT;
    v_parent BIGINT;
    v_left BIGINT;
    v_right BIGINT;
    v_replacement BIGINT;
    v_replacement_parent BIGINT;
    v_root BIGINT;
BEGIN
    PERFORM 1
    FROM registries
    WHERE registry_id = p_registry_id
      AND is_active = TRUE
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Registry is missing or inactive.';
    END IF;

    SELECT root_node_id
    INTO v_root
    FROM registry_roots
    WHERE registry_id = p_registry_id
    FOR UPDATE;

    SELECT
        node_id,
        parent_node_id,
        left_child_id,
        right_child_id
    INTO
        v_target,
        v_parent,
        v_left,
        v_right
    FROM bst_nodes
    WHERE registry_id = p_registry_id
      AND node_key = p_key
    FOR UPDATE;

    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;

    IF v_left IS NOT NULL AND v_right IS NOT NULL THEN
        v_replacement := v_right;

        LOOP
            SELECT left_child_id
            INTO v_replacement_parent
            FROM bst_nodes
            WHERE node_id = v_replacement;

            EXIT WHEN v_replacement_parent IS NULL;

            v_replacement_parent := v_replacement;

            SELECT left_child_id
            INTO v_replacement
            FROM bst_nodes
            WHERE node_id = v_replacement_parent;

            EXIT WHEN v_replacement IS NULL;
        END LOOP;

        -- Correctly locate the leftmost node of the right subtree.
        v_replacement := v_right;

        LOOP
            SELECT left_child_id
            INTO v_target
            FROM bst_nodes
            WHERE node_id = v_replacement;

            EXIT WHEN v_target IS NULL;

            v_replacement := v_target;
        END LOOP;

        SELECT parent_node_id, right_child_id
        INTO v_replacement_parent, v_target
        FROM bst_nodes
        WHERE node_id = v_replacement;

        IF v_replacement_parent <> v_left
           AND v_replacement_parent IS NOT NULL THEN
            UPDATE bst_nodes
            SET left_child_id = v_target
            WHERE node_id = v_replacement_parent;

            IF v_target IS NOT NULL THEN
                UPDATE bst_nodes
                SET parent_node_id = v_replacement_parent
                WHERE node_id = v_target;
            END IF;

            UPDATE bst_nodes
            SET right_child_id = v_right
            WHERE node_id = v_replacement;

            UPDATE bst_nodes
            SET parent_node_id = v_replacement
            WHERE node_id = v_right;
        END IF;

        UPDATE bst_nodes
        SET left_child_id = v_left
        WHERE node_id = v_replacement;

        UPDATE bst_nodes
        SET parent_node_id = v_replacement
        WHERE node_id = v_left;

        IF v_parent IS NULL THEN
            UPDATE registry_roots
            SET root_node_id = v_replacement
            WHERE registry_id = p_registry_id;
        ELSE
            UPDATE bst_nodes
            SET
                left_child_id = CASE
                    WHEN left_child_id = (
                        SELECT node_id
                        FROM bst_nodes
                        WHERE registry_id = p_registry_id
                          AND node_key = p_key
                    ) THEN v_replacement
                    ELSE left_child_id
                END,
                right_child_id = CASE
                    WHEN right_child_id = (
                        SELECT node_id
                        FROM bst_nodes
                        WHERE registry_id = p_registry_id
                          AND node_key = p_key
                    ) THEN v_replacement
                    ELSE right_child_id
                END
            WHERE node_id = v_parent;
        END IF;

        UPDATE bst_nodes
        SET parent_node_id = v_parent
        WHERE node_id = v_replacement;

    ELSE
        v_replacement := COALESCE(v_left, v_right);

        IF v_replacement IS NOT NULL THEN
            UPDATE bst_nodes
            SET parent_node_id = v_parent
            WHERE node_id = v_replacement;
        END IF;

        IF v_parent IS NULL THEN
            UPDATE registry_roots
            SET root_node_id = v_replacement
            WHERE registry_id = p_registry_id;
        ELSE
            UPDATE bst_nodes
            SET
                left_child_id = CASE
                    WHEN left_child_id = v_target
                        THEN v_replacement
                    ELSE left_child_id
                END,
                right_child_id = CASE
                    WHEN right_child_id = v_target
                        THEN v_replacement
                    ELSE right_child_id
                END
            WHERE node_id = v_parent;
        END IF;
    END IF;

    DELETE FROM bst_nodes
    WHERE node_id = v_target;

    INSERT INTO bst_audit_log(
        registry_id,
        operation,
        node_key,
        operation_status,
        details
    )
    VALUES (
        p_registry_id,
        'DELETE',
        p_key,
        'SUCCESS',
        'BST node deleted.'
    );

    RETURN TRUE;
END;
$$;

-- Use a separate transaction for the sample deletion.
SAVEPOINT before_sample_delete;

DO $$
DECLARE
    v_registry BIGINT;
BEGIN
    SELECT registry_id
    INTO v_registry
    FROM registries
    WHERE registry_name = 'ASSET_SECONDARY';

    PERFORM bst_delete(v_registry, 150);
END;
$$;

-- Validate the secondary registry after deletion.
SELECT *
FROM validate_bst(
    (
        SELECT registry_id
        FROM registries
        WHERE registry_name = 'ASSET_SECONDARY'
    )
);

-- ------------------------------------------------------------
-- 26. Final audit report
-- ------------------------------------------------------------

SELECT
    r.registry_name,
    a.operation,
    a.node_key,
    a.operation_status,
    a.details,
    a.performed_at
FROM bst_audit_log a
JOIN registries r
    ON r.registry_id = a.registry_id
ORDER BY a.performed_at, a.audit_id;

COMMIT;
