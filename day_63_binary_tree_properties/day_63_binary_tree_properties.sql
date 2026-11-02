DROP SCHEMA IF EXISTS binary_tree_lab CASCADE;
CREATE SCHEMA binary_tree_lab;

SET search_path TO binary_tree_lab, public;

CREATE TYPE node_kind AS ENUM ('leaf', 'internal');
CREATE TYPE tree_state AS ENUM ('active', 'archived');

CREATE TABLE trees (
    tree_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tree_name TEXT NOT NULL UNIQUE,
    state tree_state NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (length(trim(tree_name)) >= 3)
);

CREATE TABLE tree_nodes (
    node_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tree_id BIGINT NOT NULL REFERENCES trees(tree_id) ON DELETE CASCADE,
    parent_node_id BIGINT REFERENCES tree_nodes(node_id) ON DELETE CASCADE,
    node_value INTEGER NOT NULL,
    node_kind node_kind NOT NULL,
    depth INTEGER NOT NULL DEFAULT 0,
    position TEXT NOT NULL,
    CHECK (depth >= 0),
    CHECK (position IN ('root', 'left', 'right')),
    UNIQUE (tree_id, node_id),
    UNIQUE (tree_id, parent_node_id, position)
);

ALTER TABLE trees
    ADD CONSTRAINT tree_root_position_check
    CHECK (state IN ('active', 'archived'));

CREATE UNIQUE INDEX one_root_per_tree
    ON tree_nodes(tree_id)
    WHERE parent_node_id IS NULL;

CREATE INDEX tree_nodes_parent_idx
    ON tree_nodes(tree_id, parent_node_id);

CREATE INDEX tree_nodes_depth_idx
    ON tree_nodes(tree_id, depth);

CREATE TABLE tree_metrics (
    tree_id BIGINT PRIMARY KEY REFERENCES trees(tree_id) ON DELETE CASCADE,
    node_count INTEGER NOT NULL,
    leaf_count INTEGER NOT NULL,
    internal_count INTEGER NOT NULL,
    height_edges INTEGER NOT NULL,
    diameter_edges INTEGER NOT NULL,
    balanced BOOLEAN NOT NULL,
    full_tree BOOLEAN NOT NULL,
    complete_tree BOOLEAN NOT NULL,
    perfect_tree BOOLEAN NOT NULL,
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (node_count >= 0),
    CHECK (leaf_count >= 0),
    CHECK (internal_count >= 0),
    CHECK (height_edges >= -1),
    CHECK (diameter_edges >= 0),
    CHECK (leaf_count + internal_count = node_count)
);

CREATE OR REPLACE FUNCTION classify_node_kind()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    has_left BOOLEAN;
    has_right BOOLEAN;
BEGIN
    SELECT EXISTS (
        SELECT 1
        FROM tree_nodes
        WHERE tree_id = NEW.tree_id
          AND parent_node_id = NEW.node_id
          AND position = 'left'
    )
    INTO has_left;

    SELECT EXISTS (
        SELECT 1
        FROM tree_nodes
        WHERE tree_id = NEW.tree_id
          AND parent_node_id = NEW.node_id
          AND position = 'right'
    )
    INTO has_right;

    NEW.node_kind :=
        CASE
            WHEN has_left OR has_right THEN 'internal'::node_kind
            ELSE 'leaf'::node_kind
        END;

    RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION validate_node_parent()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    parent_tree_id BIGINT;
    parent_depth INTEGER;
BEGIN
    IF NEW.parent_node_id IS NULL THEN
        IF NEW.position <> 'root' THEN
            RAISE EXCEPTION
                'Root node must use position root';
        END IF;

        IF NEW.depth <> 0 THEN
            RAISE EXCEPTION
                'Root node must have depth 0';
        END IF;

        RETURN NEW;
    END IF;

    SELECT tree_id, depth
    INTO parent_tree_id, parent_depth
    FROM tree_nodes
    WHERE node_id = NEW.parent_node_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Parent node % does not exist',
            NEW.parent_node_id;
    END IF;

    IF parent_tree_id <> NEW.tree_id THEN
        RAISE EXCEPTION
            'Parent and child must belong to the same tree';
    END IF;

    IF NEW.depth <> parent_depth + 1 THEN
        RAISE EXCEPTION
            'Child depth must equal parent depth + 1';
    END IF;

    IF NEW.position NOT IN ('left', 'right') THEN
        RAISE EXCEPTION
            'Non-root node must use left or right position';
    END IF;

    IF NEW.parent_node_id = NEW.node_id THEN
        RAISE EXCEPTION
            'A node cannot be its own parent';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER tree_node_parent_validation
BEFORE INSERT OR UPDATE ON tree_nodes
FOR EACH ROW
EXECUTE FUNCTION validate_node_parent();

CREATE OR REPLACE FUNCTION recalculate_metrics(p_tree_id BIGINT)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_nodes INTEGER;
    v_leaves INTEGER;
    v_internal INTEGER;
    v_height INTEGER;
    v_diameter INTEGER;
    v_balanced BOOLEAN;
    v_full BOOLEAN;
    v_complete BOOLEAN;
    v_perfect BOOLEAN;
BEGIN
    WITH RECURSIVE hierarchy AS (
        SELECT
            n.node_id,
            n.parent_node_id,
            n.depth
        FROM tree_nodes n
        WHERE n.tree_id = p_tree_id
          AND n.parent_node_id IS NULL

        UNION ALL

        SELECT
            child.node_id,
            child.parent_node_id,
            child.depth
        FROM tree_nodes child
        JOIN hierarchy parent
          ON parent.node_id = child.parent_node_id
        WHERE child.tree_id = p_tree_id
    )
    SELECT
        COUNT(*),
        COUNT(*) FILTER (
            WHERE NOT EXISTS (
                SELECT 1
                FROM tree_nodes c
                WHERE c.tree_id = p_tree_id
                  AND c.parent_node_id = h.node_id
            )
        ),
        COALESCE(MAX(depth), -1)
    INTO v_nodes, v_leaves, v_height
    FROM hierarchy h;

    v_internal := v_nodes - v_leaves;

    /*
     * Diameter is computed by considering every pair of nodes and finding
     * their lowest common ancestor through the recursive hierarchy.
     * This is appropriate for this compact educational dataset; a production
     * system with very large trees would maintain cached subtree metrics.
     */
    WITH RECURSIVE ancestor_paths AS (
        SELECT
            n.node_id AS descendant,
            n.node_id AS ancestor,
            0 AS distance
        FROM tree_nodes n
        WHERE n.tree_id = p_tree_id

        UNION ALL

        SELECT
            ap.descendant,
            p.parent_node_id,
            ap.distance + 1
        FROM ancestor_paths ap
        JOIN tree_nodes p
          ON p.node_id = ap.ancestor
        WHERE p.parent_node_id IS NOT NULL
          AND p.tree_id = p_tree_id
    ),
    pairs AS (
        SELECT
            a.descendant AS first_node,
            b.descendant AS second_node,
            a.distance + b.distance AS distance
        FROM ancestor_paths a
        JOIN ancestor_paths b
          ON a.ancestor = b.ancestor
        WHERE a.descendant <= b.descendant
    )
    SELECT COALESCE(MAX(distance), 0)
    INTO v_diameter
    FROM pairs;

    SELECT NOT EXISTS (
        WITH RECURSIVE subtree AS (
            SELECT
                n.node_id,
                n.parent_node_id,
                0 AS relative_depth
            FROM tree_nodes n
            WHERE n.tree_id = p_tree_id

            UNION ALL

            SELECT
                child.node_id,
                child.parent_node_id,
                s.relative_depth + 1
            FROM subtree s
            JOIN tree_nodes child
              ON child.parent_node_id = s.node_id
             AND child.tree_id = p_tree_id
        ),
        child_counts AS (
            SELECT
                n.node_id,
                COUNT(c.node_id) AS child_count
            FROM tree_nodes n
            LEFT JOIN tree_nodes c
              ON c.parent_node_id = n.node_id
             AND c.tree_id = p_tree_id
            WHERE n.tree_id = p_tree_id
            GROUP BY n.node_id
        )
        SELECT 1
        FROM child_counts
        WHERE child_count = 1
    )
    INTO v_full;

    /*
     * Balance is determined bottom-up. The recursive CTE computes subtree
     * heights and rejects a tree when any node's child heights differ by > 1.
     */
    WITH RECURSIVE heights AS (
        SELECT
            n.node_id,
            n.parent_node_id,
            0 AS h
        FROM tree_nodes n
        WHERE n.tree_id = p_tree_id
          AND NOT EXISTS (
              SELECT 1
              FROM tree_nodes c
              WHERE c.parent_node_id = n.node_id
                AND c.tree_id = p_tree_id
          )

        UNION ALL

        SELECT
            p.node_id,
            p.parent_node_id,
            1 + MAX(h.h)
        FROM heights h
        JOIN tree_nodes p
          ON p.node_id = h.parent_node_id
         AND p.tree_id = p_tree_id
        GROUP BY p.node_id, p.parent_node_id
    ),
    violations AS (
        SELECT parent.node_id
        FROM tree_nodes parent
        LEFT JOIN heights left_h
          ON left_h.node_id = (
              SELECT node_id
              FROM tree_nodes
              WHERE parent_node_id = parent.node_id
                AND tree_id = p_tree_id
                AND position = 'left'
          )
        LEFT JOIN heights right_h
          ON right_h.node_id = (
              SELECT node_id
              FROM tree_nodes
              WHERE parent_node_id = parent.node_id
                AND tree_id = p_tree_id
                AND position = 'right'
          )
        WHERE parent.tree_id = p_tree_id
          AND ABS(
              COALESCE(left_h.h, -1) -
              COALESCE(right_h.h, -1)
          ) > 1
    )
    SELECT NOT EXISTS (SELECT 1 FROM violations)
    INTO v_balanced;

    /*
     * Complete-tree verification uses breadth-first positional numbering.
     * A missing child before a later occupied position makes the tree
     * incomplete.
     */
    WITH RECURSIVE numbered AS (
        SELECT
            n.node_id,
            1::BIGINT AS array_position
        FROM tree_nodes n
        WHERE n.tree_id = p_tree_id
          AND n.parent_node_id IS NULL

        UNION ALL

        SELECT
            child.node_id,
            CASE child.position
                WHEN 'left' THEN numbered.array_position * 2
                ELSE numbered.array_position * 2 + 1
            END
        FROM numbered
        JOIN tree_nodes child
          ON child.parent_node_id = numbered.node_id
         AND child.tree_id = p_tree_id
    )
    SELECT
        COALESCE(
            (SELECT MAX(array_position) FROM numbered) = COUNT(*),
            TRUE
        )
    INTO v_complete
    FROM numbered;

    /*
     * A perfect tree is both full and has all leaves at the same depth.
     */
    SELECT
        v_full
        AND (
            SELECT COUNT(DISTINCT depth) = 1
            FROM tree_nodes
            WHERE tree_id = p_tree_id
              AND node_kind = 'leaf'
        )
    INTO v_perfect;

    INSERT INTO tree_metrics (
        tree_id,
        node_count,
        leaf_count,
        internal_count,
        height_edges,
        diameter_edges,
        balanced,
        full_tree,
        complete_tree,
        perfect_tree
    )
    VALUES (
        p_tree_id,
        v_nodes,
        v_leaves,
        v_internal,
        v_height,
        v_diameter,
        v_balanced,
        v_full,
        v_complete,
        v_perfect
    )
    ON CONFLICT (tree_id)
    DO UPDATE SET
        node_count = EXCLUDED.node_count,
        leaf_count = EXCLUDED.leaf_count,
        internal_count = EXCLUDED.internal_count,
        height_edges = EXCLUDED.height_edges,
        diameter_edges = EXCLUDED.diameter_edges,
        balanced = EXCLUDED.balanced,
        full_tree = EXCLUDED.full_tree,
        complete_tree = EXCLUDED.complete_tree,
        perfect_tree = EXCLUDED.perfect_tree,
        calculated_at = CURRENT_TIMESTAMP;
END;
$$;

CREATE OR REPLACE FUNCTION prevent_invalid_tree_node()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_root_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_root_count
    FROM tree_nodes
    WHERE tree_id = NEW.tree_id
      AND parent_node_id IS NULL;

    IF NEW.parent_node_id IS NULL AND v_root_count > 1 THEN
        RAISE EXCEPTION 'A tree may contain only one root';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER tree_root_guard
BEFORE INSERT OR UPDATE ON tree_nodes
FOR EACH ROW
EXECUTE FUNCTION prevent_invalid_tree_node();

CREATE OR REPLACE VIEW tree_structural_report AS
SELECT
    t.tree_id,
    t.tree_name,
    t.state,
    m.node_count,
    m.leaf_count,
    m.internal_count,
    m.height_edges,
    m.height_edges + 1 AS height_nodes,
    m.diameter_edges,
    m.balanced,
    m.full_tree,
    m.complete_tree,
    m.perfect_tree,
    m.calculated_at
FROM trees t
LEFT JOIN tree_metrics m
    ON m.tree_id = t.tree_id;

CREATE OR REPLACE VIEW tree_leaf_report AS
SELECT
    t.tree_name,
    n.node_id,
    n.node_value,
    n.depth
FROM trees t
JOIN tree_nodes n
  ON n.tree_id = t.tree_id
WHERE n.node_kind = 'leaf';

INSERT INTO trees (tree_name)
VALUES
    ('balanced_complete'),
    ('unbalanced_chain'),
    ('perfect_tree'),
    ('full_not_perfect'),
    ('single_node');

INSERT INTO tree_nodes
(tree_id, parent_node_id, node_value, node_kind, depth, position)
VALUES
    (1, NULL, 10, 'internal', 0, 'root'),
    (1, 1, 5, 'internal', 1, 'left'),
    (1, 1, 15, 'internal', 1, 'right'),
    (1, 2, 2, 'leaf', 2, 'left'),
    (1, 2, 7, 'leaf', 2, 'right'),
    (1, 3, 12, 'leaf', 2, 'left'),
    (1, 3, 20, 'leaf', 2, 'right');

INSERT INTO tree_nodes
(tree_id, parent_node_id, node_value, node_kind, depth, position)
VALUES
    (2, NULL, 1, 'internal', 0, 'root'),
    (2, 8, 2, 'internal', 1, 'left');

UPDATE tree_nodes
SET parent_node_id = NULL
WHERE false;

INSERT INTO tree_nodes
(tree_id, parent_node_id, node_value, node_kind, depth, position)
VALUES
    (2, 8, 2, 'internal', 1, 'left');

DELETE FROM tree_nodes
WHERE tree_id = 2
  AND node_value = 2;

INSERT INTO tree_nodes
(tree_id, parent_node_id, node_value, node_kind, depth, position)
VALUES
    (2, 8, 2, 'internal', 1, 'left'),
    (2, 9, 3, 'internal', 2, 'left'),
    (2, 10, 4, 'internal', 3, 'left'),
    (2, 11, 5, 'leaf', 4, 'left');

INSERT INTO tree_nodes
(tree_id, parent_node_id, node_value, node_kind, depth, position)
VALUES
    (3, NULL, 8, 'internal', 0, 'root'),
    (3, 15, 4, 'internal', 1, 'left'),
    (3, 15, 12, 'internal', 1, 'right'),
    (3, 16, 2, 'leaf', 2, 'left'),
    (3, 16, 6, 'leaf', 2, 'right'),
    (3, 17, 10, 'leaf', 2, 'left'),
    (3, 17, 14, 'leaf', 2, 'right');

INSERT INTO tree_nodes
(tree_id, parent_node_id, node_value, node_kind, depth, position)
VALUES
    (4, NULL, 100, 'internal', 0, 'root'),
    (4, 22, 50, 'internal', 1, 'left'),
    (4, 22, 150, 'leaf', 1, 'right'),
    (4, 23, 25, 'leaf', 2, 'left'),
    (4, 23, 75, 'leaf', 2, 'right');

INSERT INTO tree_nodes
(tree_id, parent_node_id, node_value, node_kind, depth, position)
VALUES
    (5, NULL, 42, 'leaf', 0, 'root');

DO $$
DECLARE
    tree_record RECORD;
BEGIN
    FOR tree_record IN
        SELECT tree_id FROM trees ORDER BY tree_id
    LOOP
        PERFORM recalculate_metrics(tree_record.tree_id);
    END LOOP;
END;
$$;

-- Retrieval: complete structural profile.
SELECT *
FROM tree_structural_report
ORDER BY tree_id;

-- Validation: the leaf/internal identity applies to non-empty full trees.
SELECT
    tree_name,
    leaf_count,
    internal_count,
    (leaf_count = internal_count + 1) AS identity_holds
FROM tree_structural_report
WHERE node_count > 0
  AND full_tree;

-- Aggregation: compare structural classes.
SELECT
    balanced,
    complete_tree,
    COUNT(*) AS tree_count,
    AVG(height_edges)::NUMERIC(10,2) AS average_height,
    MAX(diameter_edges) AS maximum_diameter
FROM tree_structural_report
GROUP BY balanced, complete_tree
ORDER BY balanced DESC, complete_tree DESC;

-- Evaluation: trees suitable for a policy requiring height <= 3,
-- balance, and completeness.
SELECT
    tree_name,
    CASE
        WHEN height_edges <= 3
         AND balanced
         AND complete_tree
        THEN 'eligible'
        ELSE 'rejected'
    END AS eligibility
FROM tree_structural_report
ORDER BY tree_id;

-- Failure-oriented reporting.
SELECT
    tree_name,
    ARRAY_REMOVE(
        ARRAY[
            CASE WHEN NOT balanced THEN 'unbalanced' END,
            CASE WHEN NOT full_tree THEN 'not_full' END,
            CASE WHEN NOT complete_tree THEN 'not_complete' END,
            CASE WHEN NOT perfect_tree THEN 'not_perfect' END
        ],
        NULL
    ) AS structural_violations
FROM tree_structural_report
ORDER BY tree_id;

-- Leaf retrieval.
SELECT *
FROM tree_leaf_report
ORDER BY tree_name, depth, node_id;

-- Transactional metric refresh demonstrates atomic recalculation.
BEGIN;

SELECT recalculate_metrics(tree_id)
FROM trees
WHERE state = 'active';

COMMIT;

-- Final integrity check.
SELECT
    COUNT(*) AS trees,
    COUNT(*) FILTER (WHERE node_count = leaf_count + internal_count)
        AS internally_consistent_metric_rows
FROM tree_structural_report;
