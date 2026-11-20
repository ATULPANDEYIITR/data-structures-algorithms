-- ============================================================
-- DEPTH-FIRST SEARCH: GRAPH EXPLORATION AND CONNECTIVITY
-- PostgreSQL 14+
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
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vertex (
    vertex_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_id BIGINT NOT NULL
        REFERENCES graph(graph_id) ON DELETE CASCADE,
    external_key VARCHAR(100) NOT NULL,
    vertex_label VARCHAR(200) NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (graph_id, external_key),
    UNIQUE (graph_id, vertex_id)
);

CREATE TABLE IF NOT EXISTS graph_edge (
    edge_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_id BIGINT NOT NULL,
    source_vertex_id BIGINT NOT NULL,
    destination_vertex_id BIGINT NOT NULL,
    edge_weight NUMERIC(12, 4) NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (graph_id, source_vertex_id)
        REFERENCES vertex(graph_id, vertex_id) ON DELETE CASCADE,

    FOREIGN KEY (graph_id, destination_vertex_id)
        REFERENCES vertex(graph_id, vertex_id) ON DELETE CASCADE,

    CHECK (edge_weight >= 0),
    CHECK (source_vertex_id <> destination_vertex_id),

    UNIQUE (graph_id, source_vertex_id, destination_vertex_id)
);

CREATE TABLE IF NOT EXISTS traversal_run (
    run_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_id BIGINT NOT NULL
        REFERENCES graph(graph_id) ON DELETE CASCADE,
    start_vertex_id BIGINT NOT NULL,
    traversal_method VARCHAR(15) NOT NULL
        CHECK (traversal_method IN ('RECURSIVE', 'ITERATIVE')),
    run_status VARCHAR(15) NOT NULL DEFAULT 'RUNNING'
        CHECK (run_status IN ('RUNNING', 'COMPLETED', 'FAILED')),
    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,
    vertices_visited INTEGER NOT NULL DEFAULT 0
        CHECK (vertices_visited >= 0),
    error_message TEXT,

    FOREIGN KEY (graph_id, start_vertex_id)
        REFERENCES vertex(graph_id, vertex_id),

    CHECK (
        (run_status = 'RUNNING' AND completed_at IS NULL)
        OR
        (run_status <> 'RUNNING' AND completed_at IS NOT NULL)
    )
);

CREATE TABLE IF NOT EXISTS traversal_visit (
    run_id BIGINT NOT NULL
        REFERENCES traversal_run(run_id) ON DELETE CASCADE,
    vertex_id BIGINT NOT NULL,
    parent_vertex_id BIGINT,
    depth INTEGER NOT NULL CHECK (depth >= 0),
    discovery_order INTEGER NOT NULL CHECK (discovery_order > 0),
    PRIMARY KEY (run_id, vertex_id),
    UNIQUE (run_id, discovery_order),

    FOREIGN KEY (run_id, parent_vertex_id)
        REFERENCES traversal_visit(run_id, vertex_id)
        DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE IF NOT EXISTS connected_component (
    graph_id BIGINT NOT NULL,
    vertex_id BIGINT NOT NULL,
    component_id BIGINT NOT NULL,
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (graph_id, vertex_id),

    FOREIGN KEY (graph_id, vertex_id)
        REFERENCES vertex(graph_id, vertex_id)
        ON DELETE CASCADE,

    FOREIGN KEY (graph_id, component_id)
        REFERENCES vertex(graph_id, vertex_id)
        ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- 2. INDEXES
-- ------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_vertex_graph
    ON vertex(graph_id);

CREATE INDEX IF NOT EXISTS idx_edge_source
    ON graph_edge(graph_id, source_vertex_id);

CREATE INDEX IF NOT EXISTS idx_edge_destination
    ON graph_edge(graph_id, destination_vertex_id);

CREATE INDEX IF NOT EXISTS idx_edge_graph
    ON graph_edge(graph_id);

CREATE INDEX IF NOT EXISTS idx_traversal_graph_status
    ON traversal_run(graph_id, run_status, started_at DESC);

CREATE INDEX IF NOT EXISTS idx_component_lookup
    ON connected_component(graph_id, component_id);

CREATE INDEX IF NOT EXISTS idx_vertex_metadata
    ON vertex USING GIN(metadata);

-- ------------------------------------------------------------
-- 3. EDGE INTEGRITY TRIGGER
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_graph_edge()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    current_type VARCHAR(15);
BEGIN
    SELECT graph_type
    INTO current_type
    FROM graph
    WHERE graph_id = NEW.graph_id
    FOR SHARE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Graph % does not exist', NEW.graph_id;
    END IF;

    IF current_type = 'UNDIRECTED'
       AND NEW.source_vertex_id > NEW.destination_vertex_id THEN

        RAISE EXCEPTION
            'Undirected edges must use ascending vertex identifiers';
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validate_graph_edge ON graph_edge;

CREATE TRIGGER trg_validate_graph_edge
BEFORE INSERT OR UPDATE ON graph_edge
FOR EACH ROW
EXECUTE FUNCTION validate_graph_edge();

-- ------------------------------------------------------------
-- 4. GRAPH VIEWS
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW graph_overview AS
SELECT
    g.graph_id,
    g.graph_name,
    g.graph_type,
    COUNT(DISTINCT v.vertex_id) AS vertex_count,
    COUNT(DISTINCT e.edge_id) AS edge_count,
    CASE
        WHEN COUNT(v.vertex_id) = 0 THEN 0
        WHEN g.graph_type = 'UNDIRECTED' THEN
            COUNT(DISTINCT e.edge_id) * 2
                + COUNT(DISTINCT v.vertex_id)
        ELSE COUNT(DISTINCT e.edge_id)
    END AS stored_relationship_count
FROM graph g
LEFT JOIN vertex v ON v.graph_id = g.graph_id
LEFT JOIN graph_edge e ON e.graph_id = g.graph_id
GROUP BY g.graph_id, g.graph_name, g.graph_type;

CREATE OR REPLACE VIEW traversal_report AS
SELECT
    r.run_id,
    g.graph_name,
    r.traversal_method,
    r.run_status,
    r.start_vertex_id,
    r.vertices_visited,
    r.started_at,
    r.completed_at,
    ROUND(
        EXTRACT(EPOCH FROM (r.completed_at - r.started_at))::NUMERIC,
        6
    ) AS duration_seconds
FROM traversal_run r
JOIN graph g ON g.graph_id = r.graph_id;

-- ------------------------------------------------------------
-- 5. GRAPH TRAVERSAL FUNCTION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION dfs_reachable(
    p_graph_id BIGINT,
    p_start_vertex BIGINT
)
RETURNS TABLE (
    vertex_id BIGINT,
    depth INTEGER,
    parent_vertex_id BIGINT,
    discovery_order BIGINT
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    current_type VARCHAR(15);
BEGIN
    SELECT graph_type
    INTO current_type
    FROM graph
    WHERE graph_id = p_graph_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Graph % does not exist', p_graph_id;
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM vertex
        WHERE graph_id = p_graph_id
          AND vertex_id = p_start_vertex
    ) THEN
        RAISE EXCEPTION 'Starting vertex % does not exist',
            p_start_vertex;
    END IF;

    IF current_type = 'UNDIRECTED' THEN
        RETURN QUERY
        WITH RECURSIVE traversal AS (
            SELECT
                p_start_vertex AS vertex_id,
                0 AS depth,
                NULL::BIGINT AS parent_vertex_id,
                ARRAY[p_start_vertex]::BIGINT[] AS visited_path

            UNION ALL

            SELECT
                edge.destination_vertex_id,
                traversal.depth + 1,
                traversal.vertex_id,
                traversal.visited_path
                    || edge.destination_vertex_id
            FROM traversal
            JOIN graph_edge edge
              ON edge.graph_id = p_graph_id
             AND edge.source_vertex_id = traversal.vertex_id
            WHERE NOT (
                edge.destination_vertex_id =
                    ANY(traversal.visited_path)
            )
        ),
        unique_vertices AS (
            SELECT DISTINCT ON (t.vertex_id)
                t.vertex_id,
                t.depth,
                t.parent_vertex_id
            FROM traversal t
            ORDER BY t.vertex_id, t.depth, t.visited_path
        )
        SELECT
            u.vertex_id,
            u.depth,
            u.parent_vertex_id,
            ROW_NUMBER() OVER (
                ORDER BY u.depth, u.vertex_id
            )
        FROM unique_vertices u;

    ELSE
        RETURN QUERY
        WITH RECURSIVE traversal AS (
            SELECT
                p_start_vertex AS vertex_id,
                0 AS depth,
                NULL::BIGINT AS parent_vertex_id,
                ARRAY[p_start_vertex]::BIGINT[] AS visited_path

            UNION ALL

            SELECT
                edge.destination_vertex_id,
                traversal.depth + 1,
                traversal.vertex_id,
                traversal.visited_path
                    || edge.destination_vertex_id
            FROM traversal
            JOIN graph_edge edge
              ON edge.graph_id = p_graph_id
             AND edge.source_vertex_id = traversal.vertex_id
            WHERE NOT (
                edge.destination_vertex_id =
                    ANY(traversal.visited_path)
            )
        ),
        unique_vertices AS (
            SELECT DISTINCT ON (t.vertex_id)
                t.vertex_id,
                t.depth,
                t.parent_vertex_id
            FROM traversal t
            ORDER BY t.vertex_id, t.depth, t.visited_path
        )
        SELECT
            u.vertex_id,
            u.depth,
            u.parent_vertex_id,
            ROW_NUMBER() OVER (
                ORDER BY u.depth, u.vertex_id
            )
        FROM unique_vertices u;
    END IF;
END;
$$;

-- The function enumerates simple paths to avoid cycles.
-- It is suitable for small and moderate graphs.
-- Its path enumeration can grow exponentially on dense graphs.
-- Production-scale traversal should use a queue/stack with a
-- global visited set in an application or procedural engine.

-- ------------------------------------------------------------
-- 6. CONNECTED COMPONENT CALCULATION
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE calculate_components(
    p_graph_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    current_type VARCHAR(15);
BEGIN
    SELECT graph_type
    INTO current_type
    FROM graph
    WHERE graph_id = p_graph_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Graph % does not exist', p_graph_id;
    END IF;

    IF current_type <> 'UNDIRECTED' THEN
        RAISE EXCEPTION
            'Connected components require an undirected graph';
    END IF;

    DELETE FROM connected_component
    WHERE graph_id = p_graph_id;

    INSERT INTO connected_component (
        graph_id,
        vertex_id,
        component_id,
        calculated_at
    )
    WITH RECURSIVE reachability AS (
        SELECT
            v.vertex_id AS root_id,
            v.vertex_id AS reachable_id,
            ARRAY[v.vertex_id]::BIGINT[] AS path
        FROM vertex v
        WHERE v.graph_id = p_graph_id

        UNION ALL

        SELECT
            r.root_id,
            e.destination_vertex_id,
            r.path || e.destination_vertex_id
        FROM reachability r
        JOIN graph_edge e
          ON e.graph_id = p_graph_id
         AND e.source_vertex_id = r.reachable_id
        WHERE NOT (
            e.destination_vertex_id = ANY(r.path)
        )
    ),
    labels AS (
        SELECT
            reachable_id,
            MIN(root_id) AS component_id
        FROM reachability
        GROUP BY reachable_id
    )
    SELECT
        p_graph_id,
        reachable_id,
        component_id,
        CURRENT_TIMESTAMP
    FROM labels;
END;
$$;

-- ------------------------------------------------------------
-- 7. SAMPLE GRAPHS
-- ------------------------------------------------------------

INSERT INTO graph (
    graph_name,
    graph_type,
    description
)
VALUES
(
    'infrastructure_network',
    'UNDIRECTED',
    'Infrastructure connectivity and isolated systems'
),
(
    'dependency_network',
    'DIRECTED',
    'Directed service dependency graph'
)
ON CONFLICT (graph_name) DO NOTHING;

-- Sample vertices.
INSERT INTO vertex (
    graph_id,
    external_key,
    vertex_label,
    metadata
)
SELECT
    g.graph_id,
    sample.external_key,
    sample.vertex_label,
    sample.metadata::JSONB
FROM graph g
CROSS JOIN (
    VALUES
        ('N1', 'Gateway', '{"role":"network"}'),
        ('N2', 'Router', '{"role":"network"}'),
        ('N3', 'Firewall', '{"role":"security"}'),
        ('N4', 'Application Server', '{"role":"application"}'),
        ('N5', 'Database Server', '{"role":"database"}'),
        ('N6', 'Backup Server', '{"role":"storage"}'),
        ('N7', 'Remote Gateway', '{"role":"network"}'),
        ('N8', 'Remote Router', '{"role":"network"}'),
        ('N9', 'Isolated Monitor', '{"role":"monitoring"}')
) AS sample(external_key, vertex_label, metadata)
WHERE g.graph_name = 'infrastructure_network'
ON CONFLICT (graph_id, external_key) DO NOTHING;

INSERT INTO vertex (
    graph_id,
    external_key,
    vertex_label
)
SELECT
    g.graph_id,
    sample.external_key,
    sample.vertex_label
FROM graph g
CROSS JOIN (
    VALUES
        ('S1', 'Authentication Service'),
        ('S2', 'API Gateway'),
        ('S3', 'Order Service'),
        ('S4', 'Inventory Service')
) AS sample(external_key, vertex_label)
WHERE g.graph_name = 'dependency_network'
ON CONFLICT (graph_id, external_key) DO NOTHING;

-- ------------------------------------------------------------
-- 8. SAMPLE EDGES
-- ------------------------------------------------------------

INSERT INTO graph_edge (
    graph_id,
    source_vertex_id,
    destination_vertex_id
)
SELECT
    g.graph_id,
    source.vertex_id,
    destination.vertex_id
FROM graph g
JOIN (
    VALUES
        ('N1', 'N2'),
        ('N1', 'N3'),
        ('N2', 'N4'),
        ('N2', 'N5'),
        ('N3', 'N6'),
        ('N5', 'N6'),
        ('N7', 'N8')
) AS pairs(source_key, destination_key) ON TRUE
JOIN vertex source
    ON source.graph_id = g.graph_id
   AND source.external_key = pairs.source_key
JOIN vertex destination
    ON destination.graph_id = g.graph_id
   AND destination.external_key = pairs.destination_key
WHERE g.graph_name = 'infrastructure_network'
ON CONFLICT DO NOTHING;

INSERT INTO graph_edge (
    graph_id,
    source_vertex_id,
    destination_vertex_id
)
SELECT
    g.graph_id,
    source.vertex_id,
    destination.vertex_id
FROM graph g
JOIN (
    VALUES
        ('S1', 'S2'),
        ('S2', 'S3'),
        ('S2', 'S4')
) AS pairs(source_key, destination_key) ON TRUE
JOIN vertex source
    ON source.graph_id = g.graph_id
   AND source.external_key = pairs.source_key
JOIN vertex destination
    ON destination.graph_id = g.graph_id
   AND destination.external_key = pairs.destination_key
WHERE g.graph_name = 'dependency_network'
ON CONFLICT DO NOTHING;

-- ------------------------------------------------------------
-- 9. TRAVERSAL RUN
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION execute_dfs(
    p_graph_id BIGINT,
    p_start_vertex BIGINT,
    p_method VARCHAR(15) DEFAULT 'ITERATIVE'
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    new_run_id BIGINT;
    visited_count INTEGER;
BEGIN
    IF p_method NOT IN ('ITERATIVE', 'RECURSIVE') THEN
        RAISE EXCEPTION 'Unsupported traversal method: %', p_method;
    END IF;

    INSERT INTO traversal_run (
        graph_id,
        start_vertex_id,
        traversal_method,
        run_status
    )
    VALUES (
        p_graph_id,
        p_start_vertex,
        p_method,
        'RUNNING'
    )
    RETURNING run_id INTO new_run_id;

    BEGIN
        INSERT INTO traversal_visit (
            run_id,
            vertex_id,
            parent_vertex_id,
            depth,
            discovery_order
        )
        SELECT
            new_run_id,
            result.vertex_id,
            result.parent_vertex_id,
            result.depth,
            result.discovery_order
        FROM dfs_reachable(
            p_graph_id,
            p_start_vertex
        ) result;

        GET DIAGNOSTICS visited_count = ROW_COUNT;

        UPDATE traversal_run
        SET
            run_status = 'COMPLETED',
            completed_at = CURRENT_TIMESTAMP,
            vertices_visited = visited_count
        WHERE run_id = new_run_id;

    EXCEPTION WHEN OTHERS THEN
        UPDATE traversal_run
        SET
            run_status = 'FAILED',
            completed_at = CURRENT_TIMESTAMP,
            error_message = SQLERRM
        WHERE run_id = new_run_id;

        RAISE;
    END;

    RETURN new_run_id;
END;
$$;

-- ------------------------------------------------------------
-- 10. CONNECTED COMPONENTS
-- ------------------------------------------------------------

CALL calculate_components(
    (SELECT graph_id FROM graph
     WHERE graph_name = 'infrastructure_network')
);

-- ------------------------------------------------------------
-- 11. TRANSACTIONAL TRAVERSAL EXECUTION
-- ------------------------------------------------------------

DO $$
DECLARE
    current_graph BIGINT;
    starting_vertex BIGINT;
    created_run BIGINT;
BEGIN
    SELECT g.graph_id, v.vertex_id
    INTO current_graph, starting_vertex
    FROM graph g
    JOIN vertex v ON v.graph_id = g.graph_id
    WHERE g.graph_name = 'infrastructure_network'
      AND v.external_key = 'N1';

    created_run := execute_dfs(
        current_graph,
        starting_vertex,
        'ITERATIVE'
    );

    RAISE NOTICE 'Traversal run created: %', created_run;
END;
$$;

-- ------------------------------------------------------------
-- 12. RETRIEVAL QUERIES
-- ------------------------------------------------------------

-- Graph inventory.
SELECT * FROM graph_overview;

-- Retrieve adjacency information.
SELECT
    source.external_key AS source_vertex,
    destination.external_key AS destination_vertex,
    edge.edge_weight
FROM graph_edge edge
JOIN vertex source
    ON source.graph_id = edge.graph_id
   AND source.vertex_id = edge.source_vertex_id
JOIN vertex destination
    ON destination.graph_id = edge.graph_id
   AND destination.vertex_id = edge.destination_vertex_id
JOIN graph g ON g.graph_id = edge.graph_id
WHERE g.graph_name = 'infrastructure_network'
ORDER BY source.external_key, destination.external_key;

-- Recursive DFS reachability.
SELECT
    v.external_key,
    v.vertex_label,
    traversal.depth,
    traversal.parent_vertex_id,
    traversal.discovery_order
FROM graph g
JOIN vertex start_vertex
    ON start_vertex.graph_id = g.graph_id
   AND start_vertex.external_key = 'N1'
CROSS JOIN LATERAL dfs_reachable(
    g.graph_id,
    start_vertex.vertex_id
) traversal
JOIN vertex v
    ON v.graph_id = g.graph_id
   AND v.vertex_id = traversal.vertex_id
WHERE g.graph_name = 'infrastructure_network'
ORDER BY traversal.discovery_order;

-- ------------------------------------------------------------
-- 13. CONNECTED COMPONENT REPORT
-- ------------------------------------------------------------

SELECT
    component.component_id,
    MIN(representative.vertex_label) AS representative_vertex,
    COUNT(*) AS component_size,
    STRING_AGG(v.vertex_label, ', ' ORDER BY v.vertex_label)
        AS members
FROM connected_component component
JOIN vertex v
    ON v.graph_id = component.graph_id
   AND v.vertex_id = component.vertex_id
JOIN vertex representative
    ON representative.graph_id = component.graph_id
   AND representative.vertex_id = component.component_id
JOIN graph g ON g.graph_id = component.graph_id
WHERE g.graph_name = 'infrastructure_network'
GROUP BY component.component_id
ORDER BY component.component_id;

-- ------------------------------------------------------------
-- 14. VALIDATION QUERIES
-- ------------------------------------------------------------

-- Detect invalid asymmetric undirected edges.
SELECT
    edge.graph_id,
    edge.source_vertex_id,
    edge.destination_vertex_id
FROM graph_edge edge
JOIN graph g ON g.graph_id = edge.graph_id
WHERE g.graph_type = 'UNDIRECTED'
  AND NOT EXISTS (
      SELECT 1
      FROM graph_edge reverse_edge
      WHERE reverse_edge.graph_id = edge.graph_id
        AND reverse_edge.source_vertex_id =
            edge.destination_vertex_id
        AND reverse_edge.destination_vertex_id =
            edge.source_vertex_id
  );

-- Detect vertices without any connection.
SELECT
    v.vertex_id,
    v.vertex_label
FROM vertex v
WHERE NOT EXISTS (
    SELECT 1
    FROM graph_edge e
    WHERE e.graph_id = v.graph_id
      AND (
          e.source_vertex_id = v.vertex_id
          OR e.destination_vertex_id = v.vertex_id
      )
);

-- Verify component assignments cover every vertex.
SELECT
    g.graph_name,
    COUNT(v.vertex_id) AS total_vertices,
    COUNT(c.vertex_id) AS assigned_vertices,
    COUNT(v.vertex_id) - COUNT(c.vertex_id) AS unassigned_vertices
FROM graph g
LEFT JOIN vertex v ON v.graph_id = g.graph_id
LEFT JOIN connected_component c
    ON c.graph_id = v.graph_id
   AND c.vertex_id = v.vertex_id
WHERE g.graph_type = 'UNDIRECTED'
GROUP BY g.graph_id, g.graph_name;

-- ------------------------------------------------------------
-- 15. AGGREGATION AND PERFORMANCE REPORTING
-- ------------------------------------------------------------

SELECT
    g.graph_name,
    COUNT(DISTINCT r.run_id) AS total_runs,
    COUNT(DISTINCT r.run_id)
        FILTER (WHERE r.run_status = 'COMPLETED')
        AS successful_runs,
    COUNT(DISTINCT r.run_id)
        FILTER (WHERE r.run_status = 'FAILED')
        AS failed_runs,
    COALESCE(SUM(r.vertices_visited), 0) AS total_visits,
    ROUND(
        AVG(r.vertices_visited),
        2
    ) AS average_vertices_visited
FROM graph g
LEFT JOIN traversal_run r ON r.graph_id = g.graph_id
GROUP BY g.graph_id, g.graph_name;

-- Discovery sequence for the latest successful run.
SELECT
    r.run_id,
    v.vertex_label,
    visit.depth,
    visit.discovery_order
FROM traversal_run r
JOIN traversal_visit visit ON visit.run_id = r.run_id
JOIN vertex v
    ON v.graph_id = r.graph_id
   AND v.vertex_id = visit.vertex_id
WHERE r.run_status = 'COMPLETED'
ORDER BY r.run_id DESC, visit.discovery_order;

-- ------------------------------------------------------------
-- 16. DEPTH-FIRST DEPENDENCY EXPLORATION
-- ------------------------------------------------------------

SELECT
    start_vertex.vertex_label AS start_service,
    target.vertex_label AS reachable_service,
    result.depth,
    result.parent_vertex_id
FROM graph g
JOIN vertex start_vertex
    ON start_vertex.graph_id = g.graph_id
   AND start_vertex.external_key = 'S1'
CROSS JOIN LATERAL dfs_reachable(
    g.graph_id,
    start_vertex.vertex_id
) result
JOIN vertex target
    ON target.graph_id = g.graph_id
   AND target.vertex_id = result.vertex_id
WHERE g.graph_name = 'dependency_network'
ORDER BY result.depth, result.vertex_id;

COMMIT;
