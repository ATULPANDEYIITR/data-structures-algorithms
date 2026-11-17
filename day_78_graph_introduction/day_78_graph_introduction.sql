-- ============================================================
-- GRAPH INTRODUCTION
-- PostgreSQL relational graph implementation
-- ============================================================
--
-- Demonstrates:
-- 1. Vertices and edges.
-- 2. Directed and undirected graphs.
-- 3. Weighted and unweighted graphs.
-- 4. Adjacency-list representation.
-- 5. Adjacency-matrix representation.
-- 6. Graph integrity constraints.
-- 7. BFS traversal using recursive CTEs.
-- 8. Connected component exploration.
-- 9. Degree calculations.
-- 10. Shortest-path processing for non-negative weights.
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS graph_lab;

SET search_path TO graph_lab, public;

-- ------------------------------------------------------------
-- 1. DOMAIN TABLES
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS graph (
    graph_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_name VARCHAR(150) NOT NULL UNIQUE,
    graph_type VARCHAR(15) NOT NULL
        CHECK (graph_type IN ('DIRECTED', 'UNDIRECTED')),
    is_weighted BOOLEAN NOT NULL DEFAULT FALSE,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vertex (
    vertex_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_id BIGINT NOT NULL
        REFERENCES graph(graph_id) ON DELETE CASCADE,
    vertex_key VARCHAR(100) NOT NULL,
    vertex_label VARCHAR(150) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_graph_vertex
        UNIQUE (graph_id, vertex_key),

    CONSTRAINT ck_vertex_key
        CHECK (length(trim(vertex_key)) > 0),

    CONSTRAINT ck_vertex_label
        CHECK (length(trim(vertex_label)) > 0)
);

CREATE TABLE IF NOT EXISTS edge (
    edge_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    graph_id BIGINT NOT NULL
        REFERENCES graph(graph_id) ON DELETE CASCADE,

    source_vertex_id BIGINT NOT NULL,
    destination_vertex_id BIGINT NOT NULL,

    weight NUMERIC(14, 4) NOT NULL DEFAULT 1.0,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_edge_source
        FOREIGN KEY (graph_id, source_vertex_id)
        REFERENCES vertex(graph_id, vertex_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_edge_destination
        FOREIGN KEY (graph_id, destination_vertex_id)
        REFERENCES vertex(graph_id, vertex_id)
        ON DELETE CASCADE,

    CONSTRAINT ck_edge_weight_finite
        CHECK (
            weight > '-Infinity'::NUMERIC
            AND weight < 'Infinity'::NUMERIC
            AND weight <> 'NaN'::NUMERIC
        ),

    CONSTRAINT ck_edge_distinct_vertices
        CHECK (source_vertex_id <> destination_vertex_id)
);

-- A directed graph has one ordered source-destination pair.
-- An undirected graph is canonicalized by its endpoint order.
CREATE UNIQUE INDEX IF NOT EXISTS uq_edge_pair
ON edge (
    graph_id,
    LEAST(source_vertex_id, destination_vertex_id),
    GREATEST(source_vertex_id, destination_vertex_id)
);

CREATE INDEX IF NOT EXISTS idx_vertex_graph
ON vertex(graph_id, vertex_id);

CREATE INDEX IF NOT EXISTS idx_edge_source
ON edge(graph_id, source_vertex_id);

CREATE INDEX IF NOT EXISTS idx_edge_destination
ON edge(graph_id, destination_vertex_id);

CREATE INDEX IF NOT EXISTS idx_edge_weight
ON edge(graph_id, weight);

-- ------------------------------------------------------------
-- 2. GRAPH INTEGRITY TRIGGERS
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_graph_edge()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_weighted BOOLEAN;
    v_type VARCHAR(15);
BEGIN
    SELECT is_weighted, graph_type
    INTO v_weighted, v_type
    FROM graph
    WHERE graph_id = NEW.graph_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Graph % does not exist', NEW.graph_id;
    END IF;

    IF NOT v_weighted AND NEW.weight <> 1 THEN
        RAISE EXCEPTION
            'Unweighted graph % only permits weight 1',
            NEW.graph_id;
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validate_graph_edge ON edge;

CREATE TRIGGER trg_validate_graph_edge
BEFORE INSERT OR UPDATE OF graph_id, weight
ON edge
FOR EACH ROW
EXECUTE FUNCTION validate_graph_edge();

-- Prevent graph-type changes when stored edges would violate
-- the uniqueness semantics of the new representation.
CREATE OR REPLACE FUNCTION validate_graph_type_change()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    duplicate_count BIGINT;
BEGIN
    IF NEW.graph_type = OLD.graph_type THEN
        RETURN NEW;
    END IF;

    IF NEW.graph_type = 'UNDIRECTED' THEN
        SELECT COUNT(*)
        INTO duplicate_count
        FROM (
            SELECT
                LEAST(source_vertex_id, destination_vertex_id) AS a,
                GREATEST(source_vertex_id, destination_vertex_id) AS b
            FROM edge
            WHERE graph_id = OLD.graph_id
            GROUP BY 1, 2
            HAVING COUNT(*) > 1
        ) duplicates;

        IF duplicate_count > 0 THEN
            RAISE EXCEPTION
                'Cannot convert graph: reciprocal edges exist';
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validate_graph_type
ON graph;

CREATE TRIGGER trg_validate_graph_type
BEFORE UPDATE OF graph_type
ON graph
FOR EACH ROW
EXECUTE FUNCTION validate_graph_type_change();

-- ------------------------------------------------------------
-- 3. SAMPLE GRAPH DEFINITIONS
-- ------------------------------------------------------------

INSERT INTO graph (
    graph_name,
    graph_type,
    is_weighted,
    description
)
VALUES
(
    'social_network',
    'UNDIRECTED',
    FALSE,
    'Unweighted social relationship graph'
),
(
    'road_network',
    'UNDIRECTED',
    TRUE,
    'Road distances between Indian cities'
),
(
    'project_dependencies',
    'DIRECTED',
    FALSE,
    'Directed software development dependencies'
)
ON CONFLICT (graph_name) DO NOTHING;

-- ------------------------------------------------------------
-- 4. VERTEX DATA
-- ------------------------------------------------------------

INSERT INTO vertex (
    graph_id,
    vertex_key,
    vertex_label
)
SELECT g.graph_id, v.vertex_key, v.vertex_label
FROM graph g
CROSS JOIN (
    VALUES
        ('social_network', 'ALICE', 'Alice'),
        ('social_network', 'BOB', 'Bob'),
        ('social_network', 'CHARLIE', 'Charlie'),
        ('social_network', 'DAVID', 'David'),
        ('social_network', 'EVE', 'Eve'),

        ('road_network', 'DELHI', 'Delhi'),
        ('road_network', 'AGRA', 'Agra'),
        ('road_network', 'JAIPUR', 'Jaipur'),
        ('road_network', 'LUCKNOW', 'Lucknow'),
        ('road_network', 'KANPUR', 'Kanpur'),

        ('project_dependencies', 'ANALYSIS', 'Analysis'),
        ('project_dependencies', 'DESIGN', 'Design'),
        ('project_dependencies', 'DEVELOPMENT', 'Development'),
        ('project_dependencies', 'TESTING', 'Testing'),
        ('project_dependencies', 'DEPLOYMENT', 'Deployment')
) AS v(graph_name, vertex_key, vertex_label)
WHERE g.graph_name = v.graph_name
ON CONFLICT (graph_id, vertex_key) DO NOTHING;

-- ------------------------------------------------------------
-- 5. EDGE DATA
-- ------------------------------------------------------------

-- Undirected social connections.
INSERT INTO edge (
    graph_id,
    source_vertex_id,
    destination_vertex_id,
    weight
)
SELECT
    g.graph_id,
    source.vertex_id,
    destination.vertex_id,
    1
FROM graph g
JOIN (
    VALUES
        ('ALICE', 'BOB'),
        ('ALICE', 'CHARLIE'),
        ('BOB', 'DAVID'),
        ('CHARLIE', 'DAVID')
) AS e(source_key, destination_key)
ON TRUE
JOIN vertex source
    ON source.graph_id = g.graph_id
    AND source.vertex_key = e.source_key
JOIN vertex destination
    ON destination.graph_id = g.graph_id
    AND destination.vertex_key = e.destination_key
WHERE g.graph_name = 'social_network'
ON CONFLICT DO NOTHING;

-- Weighted road network.
INSERT INTO edge (
    graph_id,
    source_vertex_id,
    destination_vertex_id,
    weight
)
SELECT
    g.graph_id,
    source.vertex_id,
    destination.vertex_id,
    e.weight
FROM graph g
JOIN (
    VALUES
        ('DELHI', 'AGRA', 230::NUMERIC),
        ('DELHI', 'JAIPUR', 280::NUMERIC),
        ('AGRA', 'LUCKNOW', 335::NUMERIC),
        ('AGRA', 'JAIPUR', 240::NUMERIC),
        ('LUCKNOW', 'KANPUR', 80::NUMERIC)
) AS e(source_key, destination_key, weight)
ON TRUE
JOIN vertex source
    ON source.graph_id = g.graph_id
    AND source.vertex_key = e.source_key
JOIN vertex destination
    ON destination.graph_id = g.graph_id
    AND destination.vertex_key = e.destination_key
WHERE g.graph_name = 'road_network'
ON CONFLICT DO NOTHING;

-- Directed project dependencies.
INSERT INTO edge (
    graph_id,
    source_vertex_id,
    destination_vertex_id,
    weight
)
SELECT
    g.graph_id,
    source.vertex_id,
    destination.vertex_id,
    1
FROM graph g
JOIN (
    VALUES
        ('ANALYSIS', 'DESIGN'),
        ('DESIGN', 'DEVELOPMENT'),
        ('DEVELOPMENT', 'TESTING'),
        ('TESTING', 'DEPLOYMENT')
) AS e(source_key, destination_key)
ON TRUE
JOIN vertex source
    ON source.graph_id = g.graph_id
    AND source.vertex_key = e.source_key
JOIN vertex destination
    ON destination.graph_id = g.graph_id
    AND destination.vertex_key = e.destination_key
WHERE g.graph_name = 'project_dependencies'
ON CONFLICT DO NOTHING;

-- ------------------------------------------------------------
-- 6. GRAPH INFORMATION VIEW
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW graph_summary AS
SELECT
    g.graph_id,
    g.graph_name,
    g.graph_type,
    g.is_weighted,
    COUNT(DISTINCT v.vertex_id) AS vertex_count,
    COUNT(DISTINCT e.edge_id) AS edge_count,
    g.created_at
FROM graph g
LEFT JOIN vertex v
    ON v.graph_id = g.graph_id
LEFT JOIN edge e
    ON e.graph_id = g.graph_id
GROUP BY
    g.graph_id,
    g.graph_name,
    g.graph_type,
    g.is_weighted,
    g.created_at;

-- ------------------------------------------------------------
-- 7. ADJACENCY LIST VIEW
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW adjacency_list AS
SELECT
    g.graph_name,
    source.vertex_key AS source_vertex,
    destination.vertex_key AS destination_vertex,
    e.weight
FROM edge e
JOIN graph g
    ON g.graph_id = e.graph_id
JOIN vertex source
    ON source.vertex_id = e.source_vertex_id
JOIN vertex destination
    ON destination.vertex_id = e.destination_vertex_id;

-- ------------------------------------------------------------
-- 8. GRAPH DEGREE REPORT
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW vertex_degree_report AS
SELECT
    g.graph_name,
    v.vertex_key,
    v.vertex_label,

    CASE
        WHEN g.graph_type = 'UNDIRECTED' THEN
            COUNT(e.edge_id)
        ELSE
            COUNT(e.edge_id) FILTER (
                WHERE e.source_vertex_id = v.vertex_id
            )
    END AS out_degree,

    CASE
        WHEN g.graph_type = 'UNDIRECTED' THEN
            COUNT(e.edge_id)
        ELSE
            COUNT(e.edge_id) FILTER (
                WHERE e.destination_vertex_id = v.vertex_id
            )
    END AS in_degree

FROM graph g
JOIN vertex v
    ON v.graph_id = g.graph_id
LEFT JOIN edge e
    ON e.graph_id = g.graph_id
    AND (
        e.source_vertex_id = v.vertex_id
        OR (
            g.graph_type = 'UNDIRECTED'
            AND e.destination_vertex_id = v.vertex_id
        )
    )
GROUP BY
    g.graph_name,
    g.graph_type,
    v.vertex_id,
    v.vertex_key,
    v.vertex_label;

-- ------------------------------------------------------------
-- 9. ADJACENCY MATRIX FUNCTION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION get_adjacency_matrix(
    p_graph_name VARCHAR
)
RETURNS TABLE (
    source_vertex TEXT,
    destination_vertex TEXT,
    edge_weight NUMERIC
)
LANGUAGE sql
STABLE
AS $$
    SELECT
        source.vertex_key::TEXT,
        destination.vertex_key::TEXT,
        e.weight
    FROM graph g
    CROSS JOIN vertex source
    CROSS JOIN vertex destination
    LEFT JOIN edge e
        ON e.graph_id = g.graph_id
        AND e.source_vertex_id = source.vertex_id
        AND e.destination_vertex_id = destination.vertex_id
    WHERE g.graph_name = p_graph_name
      AND source.graph_id = g.graph_id
      AND destination.graph_id = g.graph_id
    ORDER BY
        source.vertex_key,
        destination.vertex_key;
$$;

-- Missing edge_weight represents no connection.
-- A value of zero would represent a valid zero-weight edge.

-- ------------------------------------------------------------
-- 10. BREADTH-FIRST SEARCH USING RECURSIVE CTE
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION graph_bfs(
    p_graph_name VARCHAR,
    p_start_vertex VARCHAR
)
RETURNS TABLE (
    vertex_key VARCHAR,
    depth INTEGER,
    traversal_path VARCHAR[]
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_graph_id BIGINT;
    v_start_id BIGINT;
    v_type VARCHAR(15);
BEGIN
    SELECT graph_id, graph_type
    INTO v_graph_id, v_type
    FROM graph
    WHERE graph_name = p_graph_name;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Graph not found: %', p_graph_name;
    END IF;

    SELECT vertex_id
    INTO v_start_id
    FROM vertex
    WHERE graph_id = v_graph_id
      AND vertex_key = p_start_vertex;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Starting vertex not found: %',
            p_start_vertex;
    END IF;

    RETURN QUERY
    WITH RECURSIVE traversal AS (
        SELECT
            v.vertex_id,
            v.vertex_key,
            0 AS depth,
            ARRAY[v.vertex_id] AS visited_ids,
            ARRAY[v.vertex_key] AS path
        FROM vertex v
        WHERE v.vertex_id = v_start_id

        UNION ALL

        SELECT
            destination.vertex_id,
            destination.vertex_key,
            t.depth + 1,
            t.visited_ids || destination.vertex_id,
            t.path || destination.vertex_key
        FROM traversal t
        JOIN edge e
            ON e.graph_id = v_graph_id
            AND e.source_vertex_id = t.vertex_id
        JOIN vertex destination
            ON destination.vertex_id = e.destination_vertex_id
        WHERE NOT destination.vertex_id = ANY(t.visited_ids)
           OR (
                v_type = 'UNDIRECTED'
                AND e.destination_vertex_id <> ALL(t.visited_ids)
           )
    )
    SELECT
        t.vertex_key,
        t.depth,
        t.path
    FROM traversal t
    ORDER BY
        t.depth,
        t.path;
END;
$$;

-- ------------------------------------------------------------
-- 11. DIRECTED GRAPH CYCLE DETECTION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION graph_has_directed_cycle(
    p_graph_name VARCHAR
)
RETURNS BOOLEAN
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_graph_id BIGINT;
    v_type VARCHAR(15);
    v_has_cycle BOOLEAN;
BEGIN
    SELECT graph_id, graph_type
    INTO v_graph_id, v_type
    FROM graph
    WHERE graph_name = p_graph_name;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Graph not found: %', p_graph_name;
    END IF;

    IF v_type <> 'DIRECTED' THEN
        RAISE EXCEPTION
            'Directed cycle detection requires a directed graph';
    END IF;

    WITH RECURSIVE paths AS (
        SELECT
            e.source_vertex_id AS start_id,
            e.destination_vertex_id AS current_id,
            ARRAY[
                e.source_vertex_id,
                e.destination_vertex_id
            ] AS visited
        FROM edge e
        WHERE e.graph_id = v_graph_id

        UNION ALL

        SELECT
            p.start_id,
            e.destination_vertex_id,
            p.visited || e.destination_vertex_id
        FROM paths p
        JOIN edge e
            ON e.graph_id = v_graph_id
            AND e.source_vertex_id = p.current_id
        WHERE e.destination_vertex_id = p.start_id
           OR NOT e.destination_vertex_id = ANY(p.visited)
    )
    SELECT EXISTS (
        SELECT 1
        FROM paths
        WHERE current_id = start_id
    )
    INTO v_has_cycle;

    RETURN v_has_cycle;
END;
$$;

-- ------------------------------------------------------------
-- 12. NON-NEGATIVE WEIGHT SHORTEST PATH FUNCTION
-- ------------------------------------------------------------

-- This procedure performs a Dijkstra-style iterative search.
-- It stores tentative distances in a temporary table.
-- Negative weights are rejected.

CREATE OR REPLACE PROCEDURE calculate_shortest_paths(
    p_graph_name VARCHAR,
    p_start_vertex VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_graph_id BIGINT;
    v_start_id BIGINT;
    v_type VARCHAR(15);
    v_current_id BIGINT;
    v_current_distance NUMERIC;
    v_edge RECORD;
    v_candidate NUMERIC;
BEGIN
    SELECT graph_id, graph_type
    INTO v_graph_id, v_type
    FROM graph
    WHERE graph_name = p_graph_name;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Graph not found: %', p_graph_name;
    END IF;

    SELECT vertex_id
    INTO v_start_id
    FROM vertex
    WHERE graph_id = v_graph_id
      AND vertex_key = p_start_vertex;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Starting vertex not found: %',
            p_start_vertex;
    END IF;

    IF EXISTS (
        SELECT 1
        FROM edge
        WHERE graph_id = v_graph_id
          AND weight < 0
    ) THEN
        RAISE EXCEPTION
            'Dijkstra cannot process negative weights';
    END IF;

    DROP TABLE IF EXISTS pg_temp.graph_distances;
    DROP TABLE IF EXISTS pg_temp.graph_pending;

    CREATE TEMP TABLE graph_distances (
        vertex_id BIGINT PRIMARY KEY,
        distance NUMERIC
    ) ON COMMIT DROP;

    CREATE TEMP TABLE graph_pending (
        vertex_id BIGINT PRIMARY KEY
    ) ON COMMIT DROP;

    INSERT INTO graph_distances(vertex_id, distance)
    SELECT
        vertex_id,
        CASE
            WHEN vertex_id = v_start_id THEN 0
            ELSE 'Infinity'::NUMERIC
        END
    FROM vertex
    WHERE graph_id = v_graph_id;

    INSERT INTO graph_pending(vertex_id)
    SELECT vertex_id
    FROM vertex
    WHERE graph_id = v_graph_id;

    LOOP
        SELECT
            d.vertex_id,
            d.distance
        INTO v_current_id, v_current_distance
        FROM graph_distances d
        JOIN graph_pending p
            ON p.vertex_id = d.vertex_id
        ORDER BY d.distance, d.vertex_id
        LIMIT 1;

        EXIT WHEN NOT FOUND;

        IF v_current_distance = 'Infinity'::NUMERIC THEN
            EXIT;
        END IF;

        DELETE FROM graph_pending
        WHERE vertex_id = v_current_id;

        FOR v_edge IN
            SELECT
                e.destination_vertex_id AS neighbor_id,
                e.weight
            FROM edge e
            WHERE e.graph_id = v_graph_id
              AND e.source_vertex_id = v_current_id

            UNION ALL

            SELECT
                e.source_vertex_id,
                e.weight
            FROM edge e
            WHERE e.graph_id = v_graph_id
              AND v_type = 'UNDIRECTED'
              AND e.destination_vertex_id = v_current_id
        LOOP
            IF EXISTS (
                SELECT 1
                FROM graph_pending
                WHERE vertex_id = v_edge.neighbor_id
            ) THEN
                v_candidate := v_current_distance + v_edge.weight;

                UPDATE graph_distances
                SET distance = v_candidate
                WHERE vertex_id = v_edge.neighbor_id
                  AND distance > v_candidate;
            END IF;
        END LOOP;
    END LOOP;

    RAISE NOTICE 'Shortest path calculation completed for %',
        p_graph_name;
END;
$$;

-- ------------------------------------------------------------
-- 13. TRANSACTIONAL GRAPH UPDATE
-- ------------------------------------------------------------

SAVEPOINT before_graph_update;

-- Demonstration: add a zero-weight connection to a weighted graph.
INSERT INTO edge (
    graph_id,
    source_vertex_id,
    destination_vertex_id,
    weight
)
SELECT
    g.graph_id,
    source.vertex_id,
    destination.vertex_id,
    0
FROM graph g
JOIN vertex source
    ON source.graph_id = g.graph_id
    AND source.vertex_key = 'DELHI'
JOIN vertex destination
    ON destination.graph_id = g.graph_id
    AND destination.vertex_key = 'KANPUR'
WHERE g.graph_name = 'road_network'
ON CONFLICT DO NOTHING;

-- The demonstration change is rolled back to preserve sample data.
ROLLBACK TO SAVEPOINT before_graph_update;

-- ------------------------------------------------------------
-- 14. RETRIEVAL QUERIES
-- ------------------------------------------------------------

-- Graph inventory.
SELECT *
FROM graph_summary
ORDER BY graph_name;

-- All edges.
SELECT *
FROM adjacency_list
ORDER BY graph_name, source_vertex, destination_vertex;

-- Degree report.
SELECT *
FROM vertex_degree_report
ORDER BY graph_name, vertex_key;

-- ------------------------------------------------------------
-- 15. ADJACENCY MATRIX REPORT
-- ------------------------------------------------------------

SELECT *
FROM get_adjacency_matrix('road_network');

-- ------------------------------------------------------------
-- 16. BFS REPORT
-- ------------------------------------------------------------

SELECT *
FROM graph_bfs('social_network', 'ALICE');

-- ------------------------------------------------------------
-- 17. CYCLE EVALUATION
-- ------------------------------------------------------------

SELECT
    graph_name,
    graph_has_directed_cycle(graph_name) AS contains_cycle
FROM graph
WHERE graph_type = 'DIRECTED';

-- ------------------------------------------------------------
-- 18. SHORTEST PATH EVALUATION
-- ------------------------------------------------------------

CALL calculate_shortest_paths(
    'road_network',
    'DELHI'
);

SELECT
    v.vertex_key,
    d.distance
FROM graph_distances d
JOIN vertex v
    ON v.vertex_id = d.vertex_id
ORDER BY d.distance, v.vertex_key;

-- ------------------------------------------------------------
-- 19. VALIDATION REPORTS
-- ------------------------------------------------------------

-- Check for orphaned references.
SELECT
    e.edge_id
FROM edge e
LEFT JOIN vertex source
    ON source.vertex_id = e.source_vertex_id
LEFT JOIN vertex destination
    ON destination.vertex_id = e.destination_vertex_id
WHERE source.vertex_id IS NULL
   OR destination.vertex_id IS NULL;

-- Check whether an unweighted graph contains invalid weights.
SELECT
    g.graph_name,
    e.edge_id,
    e.weight
FROM edge e
JOIN graph g
    ON g.graph_id = e.graph_id
WHERE NOT g.is_weighted
  AND e.weight <> 1;

-- Check isolated vertices.
SELECT
    g.graph_name,
    v.vertex_key
FROM vertex v
JOIN graph g
    ON g.graph_id = v.graph_id
WHERE NOT EXISTS (
    SELECT 1
    FROM edge e
    WHERE e.graph_id = v.graph_id
      AND (
          e.source_vertex_id = v.vertex_id
          OR e.destination_vertex_id = v.vertex_id
      )
);

-- ------------------------------------------------------------
-- 20. AGGREGATION
-- ------------------------------------------------------------

SELECT
    g.graph_name,
    g.graph_type,
    COUNT(DISTINCT v.vertex_id) AS vertices,
    COUNT(DISTINCT e.edge_id) AS edges,
    ROUND(AVG(e.weight), 2) AS average_edge_weight,
    MIN(e.weight) AS minimum_weight,
    MAX(e.weight) AS maximum_weight
FROM graph g
LEFT JOIN vertex v
    ON v.graph_id = g.graph_id
LEFT JOIN edge e
    ON e.graph_id = g.graph_id
GROUP BY
    g.graph_id,
    g.graph_name,
    g.graph_type
ORDER BY g.graph_name;

-- ------------------------------------------------------------
-- 21. QUERY PERFORMANCE INSPECTION
-- ------------------------------------------------------------

EXPLAIN
SELECT destination_vertex_id
FROM edge
WHERE graph_id = (
    SELECT graph_id
    FROM graph
    WHERE graph_name = 'road_network'
)
AND source_vertex_id = (
    SELECT vertex_id
    FROM vertex
    WHERE graph_id = (
        SELECT graph_id
        FROM graph
        WHERE graph_name = 'road_network'
    )
    AND vertex_key = 'DELHI'
);

COMMIT;
