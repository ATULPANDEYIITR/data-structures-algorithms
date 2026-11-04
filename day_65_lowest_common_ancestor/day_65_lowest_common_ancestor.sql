-- ============================================================
-- LOWEST COMMON ANCESTOR
-- PostgreSQL implementation
--
-- Features:
-- 1. Binary-tree relational model
-- 2. Parent-pointer LCA
-- 3. Recursive CTE LCA
-- 4. Binary-lifting preprocessing
-- 5. Multiple-query processing
-- 6. Kth ancestor and tree distance
-- 7. Ancestor validation and reporting
-- ============================================================

DROP SCHEMA IF EXISTS lca_lab CASCADE;

CREATE SCHEMA lca_lab;

SET search_path TO lca_lab, public;

-- ------------------------------------------------------------
-- 1. Tree management
-- ------------------------------------------------------------

CREATE TABLE binary_tree (
    tree_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tree_name VARCHAR(150) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tree_node (
    node_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tree_id BIGINT NOT NULL
        REFERENCES binary_tree(tree_id) ON DELETE CASCADE,

    node_value INTEGER NOT NULL,

    parent_node_id BIGINT,
    child_side CHAR(1),

    CONSTRAINT uq_tree_node_value
        UNIQUE (tree_id, node_value),

    CONSTRAINT uq_tree_node_reference
        UNIQUE (tree_id, node_id),

    CONSTRAINT fk_parent_same_tree
        FOREIGN KEY (tree_id, parent_node_id)
        REFERENCES tree_node(tree_id, node_id)
        DEFERRABLE INITIALLY DEFERRED,

    CONSTRAINT ck_not_own_parent
        CHECK (parent_node_id IS NULL OR parent_node_id <> node_id),

    CONSTRAINT ck_child_side
        CHECK (
            (parent_node_id IS NULL AND child_side IS NULL)
            OR
            (parent_node_id IS NOT NULL AND child_side IN ('L', 'R'))
        )
);

CREATE UNIQUE INDEX uq_tree_root
    ON tree_node(tree_id)
    WHERE parent_node_id IS NULL;

CREATE UNIQUE INDEX uq_tree_child_position
    ON tree_node(tree_id, parent_node_id, child_side)
    WHERE parent_node_id IS NOT NULL;

CREATE INDEX idx_tree_parent
    ON tree_node(tree_id, parent_node_id);

CREATE INDEX idx_tree_node_lookup
    ON tree_node(tree_id, node_value);

-- ------------------------------------------------------------
-- 2. Tree integrity validation
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_tree_structure()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_cycle BOOLEAN;
BEGIN
    IF NEW.parent_node_id IS NULL THEN
        RETURN NEW;
    END IF;

    IF NEW.parent_node_id = NEW.node_id THEN
        RAISE EXCEPTION 'A node cannot be its own parent.';
    END IF;

    -- Detect whether the proposed parent is already a
    -- descendant of the node being inserted or updated.
    WITH RECURSIVE descendants(node_id) AS (
        SELECT NEW.node_id
        WHERE NEW.node_id IS NOT NULL

        UNION ALL

        SELECT child.node_id
        FROM tree_node child
        JOIN descendants d
          ON child.parent_node_id = d.node_id
        WHERE child.tree_id = NEW.tree_id
    )
    SELECT EXISTS (
        SELECT 1
        FROM descendants
        WHERE node_id = NEW.parent_node_id
    )
    INTO v_cycle;

    IF v_cycle THEN
        RAISE EXCEPTION 'Tree cycle detected.';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_tree_structure
BEFORE INSERT OR UPDATE OF parent_node_id, tree_id
ON tree_node
FOR EACH ROW
EXECUTE FUNCTION validate_tree_structure();

-- ------------------------------------------------------------
-- 3. Tree registration and sample data
-- ------------------------------------------------------------

INSERT INTO binary_tree(tree_name)
VALUES ('Engineering Organization Tree');

INSERT INTO tree_node(tree_id, node_value, parent_node_id, child_side)
SELECT tree_id, 1, NULL, NULL
FROM binary_tree
WHERE tree_name = 'Engineering Organization Tree';

-- Sample tree:
--
--                 1
--              /     \
--             2       3
--           /   \   /   \
--          4     5 6     7
--         / \   /
--        8   9 10

WITH sample_nodes(node_value, parent_value, child_side) AS (
    VALUES
        (2, 1, 'L'),
        (3, 1, 'R'),
        (4, 2, 'L'),
        (5, 2, 'R'),
        (6, 3, 'L'),
        (7, 3, 'R'),
        (8, 4, 'L'),
        (9, 4, 'R'),
        (10, 5, 'L')
)
INSERT INTO tree_node(
    tree_id,
    node_value,
    parent_node_id,
    child_side
)
SELECT
    t.tree_id,
    s.node_value,
    p.node_id,
    s.child_side
FROM sample_nodes s
CROSS JOIN binary_tree t
JOIN tree_node p
    ON p.tree_id = t.tree_id
   AND p.node_value = s.parent_value
WHERE t.tree_name = 'Engineering Organization Tree';

-- ------------------------------------------------------------
-- 4. Tree information view
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW v_tree_nodes AS
SELECT
    t.tree_id,
    t.tree_name,
    n.node_id,
    n.node_value,
    n.parent_node_id,
    parent.node_value AS parent_value,
    n.child_side
FROM binary_tree t
JOIN tree_node n
    ON n.tree_id = t.tree_id
LEFT JOIN tree_node parent
    ON parent.tree_id = n.tree_id
   AND parent.node_id = n.parent_node_id;

-- ------------------------------------------------------------
-- 5. Recursive CTE: LCA
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION recursive_lca(
    p_tree_id BIGINT,
    p_first_value INTEGER,
    p_second_value INTEGER
)
RETURNS INTEGER
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_result INTEGER;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM tree_node
        WHERE tree_id = p_tree_id
          AND node_value = p_first_value
    ) OR NOT EXISTS (
        SELECT 1 FROM tree_node
        WHERE tree_id = p_tree_id
          AND node_value = p_second_value
    ) THEN
        RAISE EXCEPTION 'Both nodes must exist in the specified tree.';
    END IF;

    WITH RECURSIVE
    first_ancestors(node_id, parent_node_id, distance) AS (
        SELECT node_id, parent_node_id, 0
        FROM tree_node
        WHERE tree_id = p_tree_id
          AND node_value = p_first_value

        UNION ALL

        SELECT parent.node_id,
               parent.parent_node_id,
               child.distance + 1
        FROM tree_node parent
        JOIN first_ancestors child
          ON parent.node_id = child.parent_node_id
         AND parent.tree_id = p_tree_id
    ),
    second_ancestors(node_id, parent_node_id, distance) AS (
        SELECT node_id, parent_node_id, 0
        FROM tree_node
        WHERE tree_id = p_tree_id
          AND node_value = p_second_value

        UNION ALL

        SELECT parent.node_id,
               parent.parent_node_id,
               child.distance + 1
        FROM tree_node parent
        JOIN second_ancestors child
          ON parent.node_id = child.parent_node_id
         AND parent.tree_id = p_tree_id
    )
    SELECT a.node_value
    INTO v_result
    FROM first_ancestors fa
    JOIN second_ancestors sa
      ON sa.node_id = fa.node_id
    JOIN tree_node a
      ON a.node_id = fa.node_id
     AND a.tree_id = p_tree_id
    ORDER BY
        fa.distance + sa.distance,
        fa.distance
    LIMIT 1;

    RETURN v_result;
END;
$$;

-- ------------------------------------------------------------
-- 6. Parent-pointer LCA
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION parent_lca(
    p_tree_id BIGINT,
    p_first_value INTEGER,
    p_second_value INTEGER
)
RETURNS INTEGER
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_first BIGINT;
    v_second BIGINT;
    v_result INTEGER;
BEGIN
    SELECT node_id
    INTO v_first
    FROM tree_node
    WHERE tree_id = p_tree_id
      AND node_value = p_first_value;

    SELECT node_id
    INTO v_second
    FROM tree_node
    WHERE tree_id = p_tree_id
      AND node_value = p_second_value;

    IF v_first IS NULL OR v_second IS NULL THEN
        RAISE EXCEPTION 'Unknown node.';
    END IF;

    WITH RECURSIVE
    first_chain(node_id, parent_node_id, depth) AS (
        SELECT node_id, parent_node_id, 0
        FROM tree_node
        WHERE node_id = v_first

        UNION ALL

        SELECT p.node_id, p.parent_node_id, c.depth + 1
        FROM tree_node p
        JOIN first_chain c
          ON p.node_id = c.parent_node_id
    ),
    second_chain(node_id, parent_node_id, depth) AS (
        SELECT node_id, parent_node_id, 0
        FROM tree_node
        WHERE node_id = v_second

        UNION ALL

        SELECT p.node_id, p.parent_node_id, c.depth + 1
        FROM tree_node p
        JOIN second_chain c
          ON p.node_id = c.parent_node_id
    )
    SELECT n.node_value
    INTO v_result
    FROM first_chain f
    JOIN second_chain s
      ON s.node_id = f.node_id
    JOIN tree_node n
      ON n.node_id = f.node_id
    ORDER BY
        f.depth + s.depth,
        f.depth
    LIMIT 1;

    RETURN v_result;
END;
$$;

-- ------------------------------------------------------------
-- 7. Tree depth and distance
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION node_depth(
    p_tree_id BIGINT,
    p_node_value INTEGER
)
RETURNS INTEGER
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_depth INTEGER;
BEGIN
    WITH RECURSIVE chain(node_id, parent_node_id, depth) AS (
        SELECT node_id, parent_node_id, 0
        FROM tree_node
        WHERE tree_id = p_tree_id
          AND node_value = p_node_value

        UNION ALL

        SELECT p.node_id, p.parent_node_id, c.depth + 1
        FROM tree_node p
        JOIN chain c
          ON p.node_id = c.parent_node_id
         AND p.tree_id = p_tree_id
    )
    SELECT MAX(depth)
    INTO v_depth
    FROM chain;

    IF v_depth IS NULL THEN
        RAISE EXCEPTION 'Unknown node.';
    END IF;

    RETURN v_depth;
END;
$$;

CREATE OR REPLACE FUNCTION tree_distance(
    p_tree_id BIGINT,
    p_first_value INTEGER,
    p_second_value INTEGER
)
RETURNS INTEGER
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_lca INTEGER;
BEGIN
    v_lca := parent_lca(
        p_tree_id,
        p_first_value,
        p_second_value
    );

    RETURN node_depth(p_tree_id, p_first_value)
         + node_depth(p_tree_id, p_second_value)
         - 2 * node_depth(p_tree_id, v_lca);
END;
$$;

-- ------------------------------------------------------------
-- 8. Ancestor relationship evaluation
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION is_ancestor(
    p_tree_id BIGINT,
    p_ancestor_value INTEGER,
    p_descendant_value INTEGER
)
RETURNS BOOLEAN
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_found BOOLEAN;
BEGIN
    WITH RECURSIVE chain(node_id, parent_node_id) AS (
        SELECT node_id, parent_node_id
        FROM tree_node
        WHERE tree_id = p_tree_id
          AND node_value = p_descendant_value

        UNION ALL

        SELECT p.node_id, p.parent_node_id
        FROM tree_node p
        JOIN chain c
          ON p.node_id = c.parent_node_id
         AND p.tree_id = p_tree_id
    )
    SELECT EXISTS (
        SELECT 1
        FROM chain c
        JOIN tree_node n
          ON n.node_id = c.node_id
        WHERE n.node_value = p_ancestor_value
    )
    INTO v_found;

    RETURN v_found;
END;
$$;

-- ------------------------------------------------------------
-- 9. Binary-lifting storage
-- ------------------------------------------------------------

CREATE TABLE ancestor_index (
    tree_id BIGINT NOT NULL,
    node_id BIGINT NOT NULL,
    level INTEGER NOT NULL,
    ancestor_node_id BIGINT,

    PRIMARY KEY(tree_id, node_id, level),

    FOREIGN KEY(tree_id, node_id)
        REFERENCES tree_node(tree_id, node_id)
        ON DELETE CASCADE,

    FOREIGN KEY(tree_id, ancestor_node_id)
        REFERENCES tree_node(tree_id, node_id)
        ON DELETE CASCADE,

    CHECK(level >= 0)
);

CREATE INDEX idx_ancestor_lookup
    ON ancestor_index(tree_id, node_id, level);

-- ------------------------------------------------------------
-- 10. Build binary-lifting index
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE build_ancestor_index(
    p_tree_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_count INTEGER;
    v_levels INTEGER;
    v_level INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_count
    FROM tree_node
    WHERE tree_id = p_tree_id;

    IF v_count = 0 THEN
        RAISE EXCEPTION 'Tree is empty.';
    END IF;

    v_levels := CEIL(LOG(2, v_count + 1));

    DELETE FROM ancestor_index
    WHERE tree_id = p_tree_id;

    -- Level zero contains the direct parent.
    INSERT INTO ancestor_index(
        tree_id,
        node_id,
        level,
        ancestor_node_id
    )
    SELECT
        tree_id,
        node_id,
        0,
        parent_node_id
    FROM tree_node
    WHERE tree_id = p_tree_id;

    -- Level j contains the 2^j-th ancestor.
    FOR v_level IN 1..GREATEST(v_levels, 1) - 1 LOOP
        INSERT INTO ancestor_index(
            tree_id,
            node_id,
            level,
            ancestor_node_id
        )
        SELECT
            current.tree_id,
            current.node_id,
            v_level,
            previous.ancestor_node_id
        FROM ancestor_index current
        LEFT JOIN ancestor_index previous
          ON previous.tree_id = current.tree_id
         AND previous.node_id = current.ancestor_node_id
         AND previous.level = v_level - 1
        WHERE current.tree_id = p_tree_id
          AND current.level = v_level - 1;
    END LOOP;
END;
$$;

-- ------------------------------------------------------------
-- 11. Binary-lifting kth ancestor
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION kth_ancestor(
    p_tree_id BIGINT,
    p_node_value INTEGER,
    p_k INTEGER
)
RETURNS INTEGER
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_node_id BIGINT;
    v_ancestor BIGINT;
    v_bit INTEGER := 0;
    v_k INTEGER := p_k;
    v_result INTEGER;
BEGIN
    IF p_k < 0 THEN
        RAISE EXCEPTION 'k cannot be negative.';
    END IF;

    SELECT node_id
    INTO v_node_id
    FROM tree_node
    WHERE tree_id = p_tree_id
      AND node_value = p_node_value;

    IF v_node_id IS NULL THEN
        RAISE EXCEPTION 'Unknown node.';
    END IF;

    WHILE v_k > 0 AND v_node_id IS NOT NULL LOOP
        IF MOD(v_k, 2) = 1 THEN
            SELECT ancestor_node_id
            INTO v_ancestor
            FROM ancestor_index
            WHERE tree_id = p_tree_id
              AND node_id = v_node_id
              AND level = v_bit;

            v_node_id := v_ancestor;
        END IF;

        v_k := v_k / 2;
        v_bit := v_bit + 1;
    END LOOP;

    IF v_node_id IS NULL THEN
        RETURN NULL;
    END IF;

    SELECT node_value
    INTO v_result
    FROM tree_node
    WHERE tree_id = p_tree_id
      AND node_id = v_node_id;

    RETURN v_result;
END;
$$;

-- ------------------------------------------------------------
-- 12. Binary-lifting LCA
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION binary_lifting_lca(
    p_tree_id BIGINT,
    p_first_value INTEGER,
    p_second_value INTEGER
)
RETURNS INTEGER
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_first BIGINT;
    v_second BIGINT;
    v_depth_first INTEGER;
    v_depth_second INTEGER;
    v_difference INTEGER;
    v_levels INTEGER;
    v_level INTEGER;
    v_a BIGINT;
    v_b BIGINT;
    v_result INTEGER;
BEGIN
    SELECT node_id
    INTO v_first
    FROM tree_node
    WHERE tree_id = p_tree_id
      AND node_value = p_first_value;

    SELECT node_id
    INTO v_second
    FROM tree_node
    WHERE tree_id = p_tree_id
      AND node_value = p_second_value;

    IF v_first IS NULL OR v_second IS NULL THEN
        RAISE EXCEPTION 'Both nodes must exist.';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM ancestor_index
        WHERE tree_id = p_tree_id
          AND node_id = v_first
    ) THEN
        RAISE EXCEPTION 'Binary-lifting index is missing.';
    END IF;

    WITH RECURSIVE
    a(node_id, parent_node_id, depth) AS (
        SELECT node_id, parent_node_id, 0
        FROM tree_node
        WHERE node_id = v_first

        UNION ALL

        SELECT p.node_id, p.parent_node_id, c.depth + 1
        FROM tree_node p
        JOIN a c ON p.node_id = c.parent_node_id
    ),
    b(node_id, parent_node_id, depth) AS (
        SELECT node_id, parent_node_id, 0
        FROM tree_node
        WHERE node_id = v_second

        UNION ALL

        SELECT p.node_id, p.parent_node_id, c.depth + 1
        FROM tree_node p
        JOIN b c ON p.node_id = c.parent_node_id
    )
    SELECT
        (SELECT MAX(depth) FROM a),
        (SELECT MAX(depth) FROM b)
    INTO v_depth_first, v_depth_second;

    IF v_depth_first < v_depth_second THEN
        v_a := v_first;
        v_first := v_second;
        v_second := v_a;

        v_difference := v_depth_second - v_depth_first;

        v_depth_first := v_depth_second;
    ELSE
        v_difference := v_depth_first - v_depth_second;
    END IF;

    v_levels := CEIL(LOG(2, (
        SELECT COUNT(*) + 1
        FROM tree_node
        WHERE tree_id = p_tree_id
    )));

    -- Lift the deeper node.
    v_level := 0;

    WHILE v_difference > 0 LOOP
        IF MOD(v_difference, 2) = 1 THEN
            SELECT ancestor_node_id
            INTO v_first
            FROM ancestor_index
            WHERE tree_id = p_tree_id
              AND node_id = v_first
              AND level = v_level;
        END IF;

        v_difference := v_difference / 2;
        v_level := v_level + 1;
    END LOOP;

    IF v_first = v_second THEN
        SELECT node_value
        INTO v_result
        FROM tree_node
        WHERE node_id = v_first;

        RETURN v_result;
    END IF;

    FOR v_level IN REVERSE v_levels - 1..0 LOOP
        SELECT ancestor_node_id
        INTO v_a
        FROM ancestor_index
        WHERE tree_id = p_tree_id
          AND node_id = v_first
          AND level = v_level;

        SELECT ancestor_node_id
        INTO v_b
        FROM ancestor_index
        WHERE tree_id = p_tree_id
          AND node_id = v_second
          AND level = v_level;

        IF v_a IS DISTINCT FROM v_b THEN
            v_first := v_a;
            v_second := v_b;
        END IF;
    END LOOP;

    SELECT node_value
    INTO v_result
    FROM tree_node
    WHERE tree_id = p_tree_id
      AND node_id = (
          SELECT ancestor_node_id
          FROM ancestor_index
          WHERE tree_id = p_tree_id
            AND node_id = v_first
            AND level = 0
      );

    RETURN v_result;
END;
$$;

-- ------------------------------------------------------------
-- 13. Multiple-query workload
-- ------------------------------------------------------------

CREATE TABLE lca_query_log (
    query_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tree_id BIGINT NOT NULL
        REFERENCES binary_tree(tree_id) ON DELETE CASCADE,

    first_node INTEGER NOT NULL,
    second_node INTEGER NOT NULL,

    submitted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ck_distinct_query_values
        CHECK (first_node >= 0 AND second_node >= 0)
);

CREATE INDEX idx_lca_query_tree_time
    ON lca_query_log(tree_id, submitted_at DESC);

CREATE OR REPLACE VIEW v_lca_query_results AS
SELECT
    q.query_id,
    q.tree_id,
    q.first_node,
    q.second_node,
    parent_lca(
        q.tree_id,
        q.first_node,
        q.second_node
    ) AS lowest_common_ancestor,
    tree_distance(
        q.tree_id,
        q.first_node,
        q.second_node
    ) AS distance
FROM lca_query_log q;

-- ------------------------------------------------------------
-- 14. Sample query workload
-- ------------------------------------------------------------

INSERT INTO lca_query_log(
    tree_id,
    first_node,
    second_node
)
SELECT
    tree_id,
    first_node,
    second_node
FROM binary_tree
CROSS JOIN (
    VALUES
        (8, 9),
        (8, 10),
        (8, 6),
        (5, 10),
        (2, 8)
) AS queries(first_node, second_node)
WHERE tree_name = 'Engineering Organization Tree';

-- ------------------------------------------------------------
-- 15. Execute binary-lifting preprocessing transactionally
-- ------------------------------------------------------------

BEGIN;

CALL build_ancestor_index(
    (SELECT tree_id
     FROM binary_tree
     WHERE tree_name = 'Engineering Organization Tree')
);

COMMIT;

-- ------------------------------------------------------------
-- 16. Retrieval and evaluation queries
-- ------------------------------------------------------------

-- Tree structure.
SELECT *
FROM v_tree_nodes
ORDER BY node_value;

-- Recursive LCA.
SELECT recursive_lca(
    tree_id, 8, 10
) AS recursive_lca
FROM binary_tree
WHERE tree_name = 'Engineering Organization Tree';

-- Parent-pointer LCA.
SELECT parent_lca(
    tree_id, 8, 10
) AS parent_lca
FROM binary_tree
WHERE tree_name = 'Engineering Organization Tree';

-- Binary-lifting LCA.
SELECT binary_lifting_lca(
    tree_id, 8, 10
) AS binary_lifting_lca
FROM binary_tree
WHERE tree_name = 'Engineering Organization Tree';

-- Kth ancestor.
SELECT kth_ancestor(
    tree_id, 8, 3
) AS third_ancestor
FROM binary_tree
WHERE tree_name = 'Engineering Organization Tree';

-- Distance between nodes.
SELECT tree_distance(
    tree_id, 8, 10
) AS distance
FROM binary_tree
WHERE tree_name = 'Engineering Organization Tree';

-- Ancestor relationship.
SELECT is_ancestor(
    tree_id, 2, 8
) AS is_ancestor
FROM binary_tree
WHERE tree_name = 'Engineering Organization Tree';

-- Process multiple queries.
SELECT
    first_node,
    second_node,
    parent_lca(tree_id, first_node, second_node) AS lca,
    tree_distance(tree_id, first_node, second_node) AS distance
FROM lca_query_log
ORDER BY query_id;

-- ------------------------------------------------------------
-- 17. Ancestor index reporting
-- ------------------------------------------------------------

SELECT
    n.node_value,
    i.level,
    a.node_value AS ancestor_value
FROM ancestor_index i
JOIN tree_node n
    ON n.tree_id = i.tree_id
   AND n.node_id = i.node_id
LEFT JOIN tree_node a
    ON a.tree_id = i.tree_id
   AND a.node_id = i.ancestor_node_id
ORDER BY n.node_value, i.level;

-- ------------------------------------------------------------
-- 18. Aggregation
-- ------------------------------------------------------------

SELECT
    tree_id,
    COUNT(*) AS total_queries,
    COUNT(DISTINCT first_node) AS distinct_first_nodes,
    COUNT(DISTINCT second_node) AS distinct_second_nodes,
    AVG(tree_distance(
        tree_id,
        first_node,
        second_node
    )) AS average_distance
FROM lca_query_log
GROUP BY tree_id;

-- ------------------------------------------------------------
-- 19. Validation checks
-- ------------------------------------------------------------

DO $$
DECLARE
    v_tree_id BIGINT;
BEGIN
    SELECT tree_id
    INTO v_tree_id
    FROM binary_tree
    WHERE tree_name = 'Engineering Organization Tree';

    IF recursive_lca(v_tree_id, 8, 9) <> 4 THEN
        RAISE EXCEPTION 'Recursive LCA test failed.';
    END IF;

    IF parent_lca(v_tree_id, 8, 10) <> 2 THEN
        RAISE EXCEPTION 'Parent-pointer LCA test failed.';
    END IF;

    IF binary_lifting_lca(v_tree_id, 8, 6) <> 1 THEN
        RAISE EXCEPTION 'Binary-lifting LCA test failed.';
    END IF;

    IF tree_distance(v_tree_id, 8, 10) <> 4 THEN
        RAISE EXCEPTION 'Distance test failed.';
    END IF;

    IF kth_ancestor(v_tree_id, 8, 3) <> 1 THEN
        RAISE EXCEPTION 'Kth ancestor test failed.';
    END IF;

    IF NOT is_ancestor(v_tree_id, 2, 8) THEN
        RAISE EXCEPTION 'Ancestor relationship test failed.';
    END IF;

    IF is_ancestor(v_tree_id, 3, 8) THEN
        RAISE EXCEPTION 'Negative ancestor test failed.';
    END IF;

    RAISE NOTICE 'All PostgreSQL LCA tests passed.';
END;
$$;

-- ------------------------------------------------------------
-- 20. Failure handling example
-- ------------------------------------------------------------

DO $$
DECLARE
    v_tree_id BIGINT;
BEGIN
    SELECT tree_id
    INTO v_tree_id
    FROM binary_tree
    WHERE tree_name = 'Engineering Organization Tree';

    BEGIN
        PERFORM parent_lca(v_tree_id, 8, 999);
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Expected invalid-node failure: %', SQLERRM;
    END;
END;
$$;

-- ------------------------------------------------------------
-- 21. Operational considerations
-- ------------------------------------------------------------
--
-- Recursive CTE:
--   Suitable for occasional queries and readable traversal.
--
-- Parent-pointer LCA:
--   O(h) time and O(h) recursive-chain storage.
--
-- Binary lifting:
--   O(N log N) preprocessing and storage.
--   O(log N) LCA and kth-ancestor queries.
--
-- Integrity:
--   Composite foreign keys prevent cross-tree parent references.
--   Unique indexes enforce one root and one child per side.
--   Trigger rejects cycles.
--
-- Production:
--   Restrict DML permissions on tree_node.
--   Serialize concurrent structural modifications per tree.
--   Rebuild ancestor_index after structural changes.
--   Use a version column or immutable tree snapshots to prevent
--   queries from reading an index built for an older tree state.
