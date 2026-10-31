DROP SCHEMA IF EXISTS binary_tree_intro CASCADE;
CREATE SCHEMA binary_tree_intro;

SET search_path TO binary_tree_intro;

-- A binary tree node has at most two children.
-- The parent relationship is represented by parent_id.
CREATE TABLE tree_nodes (
    node_id       BIGSERIAL PRIMARY KEY,
    tree_id       BIGINT NOT NULL,
    value         INTEGER NOT NULL,
    parent_id     BIGINT NULL,
    left_child_id BIGINT NULL,
    right_child_id BIGINT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_tree_node_value UNIQUE (tree_id, node_id),
    CONSTRAINT fk_left_child
        FOREIGN KEY (tree_id, left_child_id)
        REFERENCES tree_nodes (tree_id, node_id)
        DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_right_child
        FOREIGN KEY (tree_id, right_child_id)
        REFERENCES tree_nodes (tree_id, node_id)
        DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT fk_parent
        FOREIGN KEY (tree_id, parent_id)
        REFERENCES tree_nodes (tree_id, node_id)
        DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT chk_not_self_parent
        CHECK (parent_id IS NULL OR parent_id <> node_id),
    CONSTRAINT chk_not_self_left
        CHECK (left_child_id IS NULL OR left_child_id <> node_id),
    CONSTRAINT chk_not_self_right
        CHECK (right_child_id IS NULL OR right_child_id <> node_id)
);

CREATE TABLE trees (
    tree_id      BIGSERIAL PRIMARY KEY,
    tree_name    TEXT NOT NULL UNIQUE,
    description  TEXT NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE tree_nodes
    ADD CONSTRAINT fk_tree
    FOREIGN KEY (tree_id)
    REFERENCES trees(tree_id)
    ON DELETE CASCADE;

CREATE INDEX idx_tree_nodes_parent
    ON tree_nodes (tree_id, parent_id);

CREATE INDEX idx_tree_nodes_value
    ON tree_nodes (tree_id, value);

CREATE OR REPLACE FUNCTION validate_binary_tree_node()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    child_count INTEGER;
BEGIN
    child_count :=
        (CASE WHEN NEW.left_child_id IS NOT NULL THEN 1 ELSE 0 END) +
        (CASE WHEN NEW.right_child_id IS NOT NULL THEN 1 ELSE 0 END);

    IF child_count > 2 THEN
        RAISE EXCEPTION 'A binary tree node cannot have more than two children';
    END IF;

    IF NEW.left_child_id IS NOT NULL
       AND NEW.left_child_id = NEW.right_child_id THEN
        RAISE EXCEPTION 'Left and right child cannot reference the same node';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_binary_tree_node
BEFORE INSERT OR UPDATE ON tree_nodes
FOR EACH ROW
EXECUTE FUNCTION validate_binary_tree_node();

CREATE OR REPLACE FUNCTION tree_node_metrics(
    p_tree_id BIGINT,
    p_node_id BIGINT
)
RETURNS TABLE (
    node_id BIGINT,
    value INTEGER,
    parent_id BIGINT,
    degree INTEGER,
    depth INTEGER,
    level INTEGER,
    is_leaf BOOLEAN
)
LANGUAGE sql
AS $$
WITH RECURSIVE ancestors AS (
    SELECT
        n.node_id,
        n.value,
        n.parent_id,
        0 AS depth
    FROM tree_nodes n
    WHERE n.tree_id = p_tree_id
      AND n.node_id = p_node_id

    UNION ALL

    SELECT
        parent.node_id,
        parent.value,
        parent.parent_id,
        child.depth + 1
    FROM tree_nodes parent
    JOIN ancestors child
      ON parent.tree_id = p_tree_id
     AND parent.node_id = child.parent_id
)
SELECT
    n.node_id,
    n.value,
    n.parent_id,
    (CASE WHEN n.left_child_id IS NOT NULL THEN 1 ELSE 0 END +
     CASE WHEN n.right_child_id IS NOT NULL THEN 1 ELSE 0 END)::INTEGER
        AS degree,
    COALESCE(
        (
            SELECT MAX(a.depth)
            FROM ancestors a
        ),
        0
    ) AS depth,
    COALESCE(
        (
            SELECT MAX(a.depth)
            FROM ancestors a
        ),
        0
    ) + 1 AS level,
    n.left_child_id IS NULL
        AND n.right_child_id IS NULL AS is_leaf
FROM tree_nodes n
WHERE n.tree_id = p_tree_id
  AND n.node_id = p_node_id;
$$;

CREATE OR REPLACE FUNCTION tree_height(p_tree_id BIGINT)
RETURNS INTEGER
LANGUAGE sql
AS $$
WITH RECURSIVE descendants AS (
    SELECT
        n.node_id,
        0 AS depth
    FROM tree_nodes n
    WHERE n.tree_id = p_tree_id
      AND n.parent_id IS NULL

    UNION ALL

    SELECT
        child.node_id,
        d.depth + 1
    FROM descendants d
    JOIN tree_nodes parent
      ON parent.tree_id = p_tree_id
     AND parent.node_id = d.node_id
    JOIN tree_nodes child
      ON child.tree_id = p_tree_id
     AND child.node_id IN (parent.left_child_id, parent.right_child_id)
)
SELECT COALESCE(MAX(depth), -1)
FROM descendants;
$$;

CREATE OR REPLACE VIEW node_classification AS
SELECT
    n.tree_id,
    n.node_id,
    n.value,
    n.parent_id,
    CASE
        WHEN n.parent_id IS NULL THEN 'ROOT'
        WHEN n.left_child_id IS NULL
         AND n.right_child_id IS NULL THEN 'LEAF'
        ELSE 'INTERNAL'
    END AS node_role,
    (
        CASE WHEN n.left_child_id IS NOT NULL THEN 1 ELSE 0 END +
        CASE WHEN n.right_child_id IS NOT NULL THEN 1 ELSE 0 END
    ) AS degree
FROM tree_nodes n;

CREATE OR REPLACE VIEW tree_statistics AS
SELECT
    t.tree_id,
    t.tree_name,
    COUNT(n.node_id) AS node_count,
    COUNT(*) FILTER (
        WHERE n.parent_id IS NULL
    ) AS root_count,
    COUNT(*) FILTER (
        WHERE n.left_child_id IS NULL
          AND n.right_child_id IS NULL
    ) AS leaf_count,
    COUNT(*) FILTER (
        WHERE n.left_child_id IS NOT NULL
           OR n.right_child_id IS NOT NULL
    ) AS internal_node_count,
    tree_height(t.tree_id) AS height
FROM trees t
LEFT JOIN tree_nodes n
    ON n.tree_id = t.tree_id
GROUP BY t.tree_id, t.tree_name;

INSERT INTO trees (tree_name, description)
VALUES
    (
        'engineering-hierarchy',
        'Binary tree used to study parent-child relationships and structural terminology'
    ),
    (
        'edge-case-tree',
        'Small tree used to represent a single-child branch'
    );

-- The deferred foreign keys permit construction of linked nodes
-- inside one transaction without relying on insertion order.
BEGIN;

INSERT INTO tree_nodes
    (tree_id, node_id, value, parent_id, left_child_id, right_child_id)
VALUES
    (1, 1, 50, NULL, 2, 5),
    (1, 2, 25, 1, 3, 4),
    (1, 3, 10, 2, NULL, NULL),
    (1, 4, 35, 2, NULL, NULL),
    (1, 5, 75, 1, 6, 7),
    (1, 6, 60, 5, NULL, NULL),
    (1, 7, 90, 5, 8, NULL),
    (1, 8, 80, 7, NULL, NULL);

INSERT INTO tree_nodes
    (tree_id, node_id, value, parent_id, left_child_id, right_child_id)
VALUES
    (2, 9, 100, NULL, 10, NULL),
    (2, 10, 80, 9, NULL, NULL);

COMMIT;

-- Root, internal node, and leaf distinctions.
SELECT *
FROM node_classification
WHERE tree_id = 1
ORDER BY node_id;

-- Parent, degree, depth, level, and leaf status for node 80.
SELECT *
FROM tree_node_metrics(1, 8);

-- Height measured in edges.
SELECT tree_id, tree_name, tree_height(tree_id) AS height
FROM trees
ORDER BY tree_id;

-- Aggregate structural report.
SELECT *
FROM tree_statistics
ORDER BY tree_id;

-- Nodes having exactly one child.
SELECT
    tree_id,
    node_id,
    value,
    degree
FROM node_classification
WHERE degree = 1
ORDER BY tree_id, node_id;

-- Leaves grouped by tree.
SELECT
    tree_id,
    COUNT(*) AS leaf_count
FROM node_classification
WHERE node_role = 'LEAF'
GROUP BY tree_id
ORDER BY tree_id;

-- Breadth-first traversal with depth.
WITH RECURSIVE traversal AS (
    SELECT
        n.tree_id,
        n.node_id,
        n.value,
        n.left_child_id,
        n.right_child_id,
        0 AS depth
    FROM tree_nodes n
    WHERE n.tree_id = 1
      AND n.parent_id IS NULL

    UNION ALL

    SELECT
        child.tree_id,
        child.node_id,
        child.value,
        child.left_child_id,
        child.right_child_id,
        traversal.depth + 1
    FROM traversal
    JOIN tree_nodes child
      ON child.tree_id = traversal.tree_id
     AND child.node_id IN (
         traversal.left_child_id,
         traversal.right_child_id
     )
)
SELECT
    tree_id,
    node_id,
    value,
    depth,
    depth + 1 AS level
FROM traversal
ORDER BY depth, node_id;

-- Transactional validation example.
BEGIN;

SELECT
    tree_id,
    tree_name,
    node_count,
    leaf_count,
    height
FROM tree_statistics
WHERE tree_id = 1
FOR SHARE;

COMMIT;
