-- ============================================================
-- BREADTH-FIRST SEARCH: GRAPH MANAGEMENT AND ANALYTICS
-- PostgreSQL 14+
--
-- Graph type: Undirected and unweighted.
-- Edge representation: One normalized row per undirected edge.
-- Shortest paths: Minimum number of edges.
-- Connected components: Groups of mutually reachable vertices.
-- ============================================================

BEGIN;

DROP SCHEMA IF EXISTS bfs_lab CASCADE;
CREATE SCHEMA bfs_lab;

SET search_path TO bfs_lab, public;

-- ------------------------------------------------------------
-- 1. DOMAIN TABLES
-- ------------------------------------------------------------

CREATE TABLE vertices (
    vertex_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vertex_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_vertex_name
        CHECK (length(trim(vertex_name)) > 0)
);

CREATE TABLE edges (
    edge_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    source_id BIGINT NOT NULL
        REFERENCES vertices(vertex_id) ON DELETE CASCADE,

    destination_id BIGINT NOT NULL
        REFERENCES vertices(vertex_id) ON DELETE CASCADE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT different_endpoints
        CHECK (source_id <> destination_id),

    -- Normalize endpoint order to avoid duplicate undirected edges.
    CONSTRAINT normalized_edge
        CHECK (source_id < destination_id),

    CONSTRAINT unique_undirected_edge
        UNIQUE (source_id, destination_id)
);

CREATE INDEX idx_edges_source
    ON edges(source_id);

CREATE INDEX idx_edges_destination
    ON edges(destination_id);

-- ------------------------------------------------------------
-- 2. EDGE VALIDATION AND NORMALIZATION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION normalize_edge()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    temporary_id BIGINT;
BEGIN
    IF NEW.source_id = NEW.destination_id THEN
        RAISE EXCEPTION
            'Self-loops are not allowed in this graph.';
    END IF;

    IF NEW.source_id > NEW.destination_id THEN
        temporary_id := NEW.source_id;
        NEW.source_id := NEW.destination_id;
        NEW.destination_id := temporary_id;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_normalize_edge
BEFORE INSERT OR UPDATE ON edges
FOR EACH ROW
EXECUTE FUNCTION normalize_edge();

-- ------------------------------------------------------------
-- 3. SAMPLE GRAPH
--
-- A -- B -- D
-- |    |
-- C    E -- F
--
-- G -- H
--
-- I is isolated.
-- ------------------------------------------------------------

INSERT INTO vertices (vertex_name, description)
VALUES
    ('A', 'Starting vertex'),
    ('B', 'Central vertex'),
    ('C', 'First branch'),
    ('D', 'Terminal vertex'),
    ('E', 'Intermediate vertex'),
    ('F', 'Destination vertex'),
    ('G', 'Separate component'),
    ('H', 'Neighbor of G'),
    ('I', 'Isolated vertex');

INSERT INTO edges (source_id, destination_id)
SELECT source_vertex.vertex_id,
       destination_vertex.vertex_id
FROM (
    VALUES
        ('A', 'B'),
        ('A', 'C'),
        ('B', 'D'),
        ('B', 'E'),
        ('C', 'F'),
        ('E', 'F'),
        ('G', 'H')
) AS input(source_name, destination_name)
JOIN vertices source_vertex
    ON source_vertex.vertex_name = input.source_name
JOIN vertices destination_vertex
    ON destination_vertex.vertex_name = input.destination_name;

-- ------------------------------------------------------------
-- 4. GRAPH ADJACENCY VIEW
--
-- Each undirected edge produces two directed adjacency rows.
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW graph_adjacency AS
SELECT source_id AS vertex_id,
       destination_id AS neighbor_id
FROM edges

UNION ALL

SELECT destination_id AS vertex_id,
       source_id AS neighbor_id
FROM edges;

-- ------------------------------------------------------------
-- 5. BFS SHORTEST-PATH FUNCTION
--
-- Recursive path exploration prevents revisiting vertices
-- within one candidate path.
--
-- The function returns one minimum-edge path.
-- For large graphs, a procedural BFS using temporary frontier
-- tables or application-side processing is preferable.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION shortest_path(
    p_start BIGINT,
    p_target BIGINT
)
RETURNS TABLE (
    path BIGINT[],
    distance INTEGER
)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM vertices WHERE vertex_id = p_start
    ) THEN
        RAISE EXCEPTION 'Starting vertex % does not exist.', p_start;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM vertices WHERE vertex_id = p_target
    ) THEN
        RAISE EXCEPTION 'Target vertex % does not exist.', p_target;
    END IF;

    IF p_start = p_target THEN
        RETURN QUERY
        SELECT ARRAY[p_start]::BIGINT[], 0;
        RETURN;
    END IF;

    RETURN QUERY
    WITH RECURSIVE paths(current_vertex, visited_path, depth) AS (
        SELECT
            p_start,
            ARRAY[p_start]::BIGINT[],
            0

        UNION ALL

        SELECT
            adjacency.neighbor_id,
            paths.visited_path || adjacency.neighbor_id,
            paths.depth + 1
        FROM paths
        JOIN graph_adjacency adjacency
            ON adjacency.vertex_id = paths.current_vertex
        WHERE NOT (
            adjacency.neighbor_id = ANY(paths.visited_path)
        )
    )
    SELECT
        paths.visited_path,
        paths.depth
    FROM paths
    WHERE paths.current_vertex = p_target
    ORDER BY paths.depth, paths.visited_path
    LIMIT 1;
END;
$$;

-- ------------------------------------------------------------
-- 6. CONNECTED COMPONENTS VIEW
--
-- Reachability is computed from every vertex.
-- The minimum reachable vertex ID becomes the component ID.
--
-- UNION removes duplicate (root, vertex) pairs and guarantees
-- termination on cyclic graphs.
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW connected_components AS
WITH RECURSIVE reachability(root_id, vertex_id) AS (
    SELECT vertex_id, vertex_id
    FROM vertices

    UNION

    SELECT
        reachability.root_id,
        adjacency.neighbor_id
    FROM reachability
    JOIN graph_adjacency adjacency
        ON adjacency.vertex_id = reachability.vertex_id
)
SELECT
    vertex_id,
    MIN(root_id) AS component_id
FROM reachability
GROUP BY vertex_id;

-- ------------------------------------------------------------
-- 7. GRAPH STATISTICS VIEW
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW graph_statistics AS
SELECT
    (SELECT COUNT(*) FROM vertices) AS vertex_count,
    (SELECT COUNT(*) FROM edges) AS edge_count,
    (SELECT COUNT(DISTINCT component_id)
     FROM connected_components) AS component_count;

-- ------------------------------------------------------------
-- 8. GRAPH RETRIEVAL
-- ------------------------------------------------------------

-- Display every vertex and its neighbors.
SELECT
    vertex.vertex_name,
    COALESCE(
        array_agg(neighbor.vertex_name ORDER BY neighbor.vertex_name)
            FILTER (WHERE neighbor.vertex_name IS NOT NULL),
        ARRAY[]::VARCHAR[]
    ) AS neighbors
FROM vertices vertex
LEFT JOIN graph_adjacency adjacency
    ON adjacency.vertex_id = vertex.vertex_id
LEFT JOIN vertices neighbor
    ON neighbor.vertex_id = adjacency.neighbor_id
GROUP BY vertex.vertex_id, vertex.vertex_name
ORDER BY vertex.vertex_name;

-- Retrieve graph statistics.
SELECT * FROM graph_statistics;

-- ------------------------------------------------------------
-- 9. BFS DISTANCES USING A RECURSIVE CTE
--
-- This enumerates simple paths and selects the minimum
-- distance for each reachable vertex.
-- ------------------------------------------------------------

WITH RECURSIVE paths(
    start_id,
    current_id,
    visited_path,
    depth
) AS (
    SELECT
        vertex_id,
        vertex_id,
        ARRAY[vertex_id]::BIGINT[],
        0
    FROM vertices
    WHERE vertex_name = 'A'

    UNION ALL

    SELECT
        paths.start_id,
        adjacency.neighbor_id,
        paths.visited_path || adjacency.neighbor_id,
        paths.depth + 1
    FROM paths
    JOIN graph_adjacency adjacency
        ON adjacency.vertex_id = paths.current_id
    WHERE NOT (
        adjacency.neighbor_id = ANY(paths.visited_path)
    )
)
SELECT
    vertex.vertex_name,
    MIN(paths.depth) AS minimum_distance
FROM paths
JOIN vertices vertex
    ON vertex.vertex_id = paths.current_id
GROUP BY vertex.vertex_name
ORDER BY minimum_distance, vertex.vertex_name;

-- ------------------------------------------------------------
-- 10. SHORTEST-PATH RETRIEVAL
-- ------------------------------------------------------------

SELECT
    (
        SELECT array_agg(vertex_name ORDER BY position)
        FROM unnest(result.path)
            WITH ORDINALITY AS p(vertex_id, position)
        JOIN vertices v ON v.vertex_id = p.vertex_id
    ) AS shortest_route,
    result.distance
FROM shortest_path(
    (SELECT vertex_id FROM vertices WHERE vertex_name = 'A'),
    (SELECT vertex_id FROM vertices WHERE vertex_name = 'F')
) AS result;

-- An unreachable destination produces no result row.
SELECT *
FROM shortest_path(
    (SELECT vertex_id FROM vertices WHERE vertex_name = 'A'),
    (SELECT vertex_id FROM vertices WHERE vertex_name = 'H')
);

-- Same source and target returns a zero-edge path.
SELECT *
FROM shortest_path(
    (SELECT vertex_id FROM vertices WHERE vertex_name = 'A'),
    (SELECT vertex_id FROM vertices WHERE vertex_name = 'A')
);

-- ------------------------------------------------------------
-- 11. CONNECTED COMPONENT REPORT
-- ------------------------------------------------------------

SELECT
    component_id,
    array_agg(vertex.vertex_name ORDER BY vertex.vertex_name)
        AS component_vertices,
    COUNT(*) AS component_size
FROM connected_components component
JOIN vertices vertex
    ON vertex.vertex_id = component.vertex_id
GROUP BY component_id
ORDER BY component_id;

-- ------------------------------------------------------------
-- 12. COMPONENT MEMBERSHIP VALIDATION
-- ------------------------------------------------------------

SELECT
    vertex.vertex_name,
    component.component_id,
    (
        SELECT COUNT(*)
        FROM connected_components member
        WHERE member.component_id = component.component_id
    ) AS component_size
FROM vertices vertex
JOIN connected_components component
    ON component.vertex_id = vertex.vertex_id
ORDER BY component.component_id, vertex.vertex_name;

-- ------------------------------------------------------------
-- 13. GRAPH INTEGRITY VALIDATION
-- ------------------------------------------------------------

-- Detect duplicate endpoint pairs.
SELECT source_id, destination_id, COUNT(*)
FROM edges
GROUP BY source_id, destination_id
HAVING COUNT(*) > 1;

-- Detect invalid references.
SELECT edge_id
FROM edges edge
LEFT JOIN vertices source_vertex
    ON source_vertex.vertex_id = edge.source_id
LEFT JOIN vertices destination_vertex
    ON destination_vertex.vertex_id = edge.destination_id
WHERE source_vertex.vertex_id IS NULL
   OR destination_vertex.vertex_id IS NULL;

-- Verify undirected adjacency symmetry.
SELECT
    edge.edge_id,
    edge.source_id,
    edge.destination_id
FROM edges edge
WHERE NOT EXISTS (
    SELECT 1
    FROM graph_adjacency a
    WHERE a.vertex_id = edge.source_id
      AND a.neighbor_id = edge.destination_id
)
OR NOT EXISTS (
    SELECT 1
    FROM graph_adjacency a
    WHERE a.vertex_id = edge.destination_id
      AND a.neighbor_id = edge.source_id
);

-- ------------------------------------------------------------
-- 14. WORKFLOW PROCESSING: ADDING A NEW CONNECTION
--
-- The transaction ensures the edge is either fully inserted
-- or rolled back.
-- ------------------------------------------------------------

SAVEPOINT before_new_connection;

INSERT INTO edges (source_id, destination_id)
SELECT
    source.vertex_id,
    destination.vertex_id
FROM vertices source
CROSS JOIN vertices destination
WHERE source.vertex_name = 'F'
  AND destination.vertex_name = 'G'
ON CONFLICT (source_id, destination_id) DO NOTHING;

SELECT * FROM graph_statistics;

ROLLBACK TO SAVEPOINT before_new_connection;

-- ------------------------------------------------------------
-- 15. FAILURE CASE: DUPLICATE EDGE
--
-- ON CONFLICT avoids an application-level failure.
-- ------------------------------------------------------------

INSERT INTO edges (source_id, destination_id)
SELECT source.vertex_id, destination.vertex_id
FROM vertices source
JOIN vertices destination
    ON destination.vertex_name = 'B'
WHERE source.vertex_name = 'A'
ON CONFLICT (source_id, destination_id) DO NOTHING;

-- ------------------------------------------------------------
-- 16. FAILURE CASE: SELF-LOOP
--
-- The trigger rejects this operation.
-- Run separately if testing the exception because a statement
-- error aborts the current transaction until rollback.
-- ------------------------------------------------------------

-- INSERT INTO edges (source_id, destination_id)
-- SELECT vertex_id, vertex_id
-- FROM vertices
-- WHERE vertex_name = 'A';

-- ------------------------------------------------------------
-- 17. PERFORMANCE AND EXECUTION INSPECTION
-- ------------------------------------------------------------

EXPLAIN (ANALYZE, BUFFERS)
SELECT neighbor_id
FROM graph_adjacency
WHERE vertex_id = (
    SELECT vertex_id
    FROM vertices
    WHERE vertex_name = 'A'
);

-- ------------------------------------------------------------
-- 18. FINAL REPORT
-- ------------------------------------------------------------

SELECT
    statistics.vertex_count,
    statistics.edge_count,
    statistics.component_count,
    CASE
        WHEN statistics.component_count <= 1 THEN TRUE
        ELSE FALSE
    END AS graph_is_connected
FROM graph_statistics statistics;

COMMIT;
