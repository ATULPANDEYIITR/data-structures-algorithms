-- ============================================================
-- GRAPH CYCLE DETECTION
-- PostgreSQL relational graph model and cycle detection engine
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS graph_lab;

SET search_path TO graph_lab, public;

-- ------------------------------------------------------------
-- 1. Domain types
-- ------------------------------------------------------------

CREATE TYPE graph_type AS ENUM (
    'DIRECTED',
    'UNDIRECTED'
);

CREATE TYPE graph_status AS ENUM (
    'DRAFT',
    'VALIDATED',
    'REJECTED'
);

CREATE TYPE detection_algorithm AS ENUM (
    'DIRECTED_DFS',
    'DIRECTED_KAHN',
    'UNDIRECTED_DSU',
    'UNDIRECTED_DFS',
    'UNDIRECTED_BFS'
);

CREATE TYPE cycle_status AS ENUM (
    'CYCLE_FOUND',
    'ACYCLIC',
    'INVALID'
);

-- ------------------------------------------------------------
-- 2. Graph registry
-- ------------------------------------------------------------

CREATE TABLE graphs (
    graph_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    graph_name VARCHAR(150) NOT NULL UNIQUE,

    graph_kind graph_type NOT NULL,

    vertex_count INTEGER NOT NULL
        CHECK (vertex_count >= 0),

    status graph_status NOT NULL DEFAULT 'DRAFT',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (length(trim(graph_name)) > 0)
);

-- ------------------------------------------------------------
-- 3. Vertices
-- ------------------------------------------------------------

CREATE TABLE vertices (
    graph_id BIGINT NOT NULL
        REFERENCES graphs(graph_id)
        ON DELETE CASCADE,

    vertex_id INTEGER NOT NULL
        CHECK (vertex_id >= 0),

    vertex_label VARCHAR(150),

    PRIMARY KEY (graph_id, vertex_id)
);

-- ------------------------------------------------------------
-- 4. Edges
--
-- For directed graphs, source and destination are ordered.
-- For undirected graphs, both endpoints represent one edge.
--
-- edge_id is retained because parallel edges are permitted.
-- ------------------------------------------------------------

CREATE TABLE edges (
    edge_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    graph_id BIGINT NOT NULL,

    source_vertex INTEGER NOT NULL,

    destination_vertex INTEGER NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (graph_id, source_vertex)
        REFERENCES vertices(graph_id, vertex_id),

    FOREIGN KEY (graph_id, destination_vertex)
        REFERENCES vertices(graph_id, vertex_id)
);

CREATE INDEX idx_edges_graph_source
    ON edges(graph_id, source_vertex);

CREATE INDEX idx_edges_graph_destination
    ON edges(graph_id, destination_vertex);

CREATE INDEX idx_edges_graph_pair
    ON edges(graph_id, source_vertex, destination_vertex);

-- ------------------------------------------------------------
-- 5. Cycle detection execution records
-- ------------------------------------------------------------

CREATE TABLE detection_runs (
    run_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    graph_id BIGINT NOT NULL
        REFERENCES graphs(graph_id)
        ON DELETE CASCADE,

    algorithm detection_algorithm NOT NULL,

    result cycle_status NOT NULL,

    detected_cycle INTEGER[] NOT NULL DEFAULT '{}',

    processed_vertices INTEGER NOT NULL DEFAULT 0
        CHECK (processed_vertices >= 0),

    execution_time_ms NUMERIC(14, 4)
        CHECK (
            execution_time_ms IS NULL
            OR execution_time_ms >= 0
        ),

    executed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    details JSONB NOT NULL DEFAULT '{}'::JSONB
);

CREATE INDEX idx_detection_runs_graph_time
    ON detection_runs(graph_id, executed_at DESC);

CREATE INDEX idx_detection_runs_result
    ON detection_runs(result, executed_at DESC);

-- ------------------------------------------------------------
-- 6. Vertex registration trigger
--
-- Vertices must belong to the configured graph range.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_vertex_range()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    configured_count INTEGER;
BEGIN
    SELECT vertex_count
    INTO configured_count
    FROM graphs
    WHERE graph_id = NEW.graph_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Graph % does not exist', NEW.graph_id;
    END IF;

    IF NEW.vertex_id >= configured_count THEN
        RAISE EXCEPTION
            'Vertex % outside graph range [0, %)',
            NEW.vertex_id,
            configured_count;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_vertex_range
BEFORE INSERT OR UPDATE ON vertices
FOR EACH ROW
EXECUTE FUNCTION validate_vertex_range();

-- ------------------------------------------------------------
-- 7. Edge registration trigger
--
-- Prevents changes to validated or rejected graphs.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_graph_edge()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    current_status graph_status;
BEGIN
    SELECT status
    INTO current_status
    FROM graphs
    WHERE graph_id = NEW.graph_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Graph does not exist.';
    END IF;

    IF current_status <> 'DRAFT' THEN
        RAISE EXCEPTION
            'Edges can only be changed while graph is in DRAFT state.';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_graph_edge
BEFORE INSERT OR UPDATE ON edges
FOR EACH ROW
EXECUTE FUNCTION validate_graph_edge();

-- ------------------------------------------------------------
-- 8. Register a complete graph
--
-- Vertices are generated from zero to vertex_count - 1.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION create_graph(
    p_name VARCHAR,
    p_type graph_type,
    p_vertex_count INTEGER
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    new_graph_id BIGINT;
BEGIN
    IF p_name IS NULL OR length(trim(p_name)) = 0 THEN
        RAISE EXCEPTION 'Graph name is required.';
    END IF;

    IF p_vertex_count IS NULL OR p_vertex_count < 0 THEN
        RAISE EXCEPTION 'Invalid vertex count.';
    END IF;

    INSERT INTO graphs(
        graph_name,
        graph_kind,
        vertex_count
    )
    VALUES (
        p_name,
        p_type,
        p_vertex_count
    )
    RETURNING graph_id INTO new_graph_id;

    IF p_vertex_count > 0 THEN
        INSERT INTO vertices(graph_id, vertex_id)
        SELECT
            new_graph_id,
            generate_series(0, p_vertex_count - 1);
    END IF;

    RETURN new_graph_id;
END;
$$;

-- ------------------------------------------------------------
-- 9. Register an edge
--
-- Duplicate edges are intentionally supported.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION add_graph_edge(
    p_graph_id BIGINT,
    p_source INTEGER,
    p_destination INTEGER
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    new_edge_id BIGINT;
BEGIN
    IF p_source IS NULL OR p_destination IS NULL THEN
        RAISE EXCEPTION 'Both endpoints are required.';
    END IF;

    INSERT INTO edges(
        graph_id,
        source_vertex,
        destination_vertex
    )
    VALUES (
        p_graph_id,
        p_source,
        p_destination
    )
    RETURNING edge_id INTO new_edge_id;

    RETURN new_edge_id;
END;
$$;

-- ------------------------------------------------------------
-- 10. Directed cycle detection using recursive DFS
--
-- Uses path arrays and an active recursion path.
-- A destination already present in the active path
-- indicates a directed cycle.
--
-- The query is intended for learning and moderate graphs.
-- Recursive path enumeration can become expensive when
-- many alternative paths exist.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION detect_directed_cycle_dfs(
    p_graph_id BIGINT
)
RETURNS TABLE (
    has_cycle BOOLEAN,
    detected_cycle INTEGER[]
)
LANGUAGE plpgsql
AS $$
DECLARE
    configured_type graph_type;
    configured_count INTEGER;
    found_path INTEGER[];
BEGIN
    SELECT graph_kind, vertex_count
    INTO configured_type, configured_count
    FROM graphs
    WHERE graph_id = p_graph_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown graph ID: %', p_graph_id;
    END IF;

    IF configured_type <> 'DIRECTED' THEN
        RAISE EXCEPTION
            'Directed DFS requires a directed graph.';
    END IF;

    WITH RECURSIVE paths(
        start_vertex,
        current_vertex,
        path,
        active_path,
        has_cycle
    ) AS (
        SELECT
            vertex_id,
            vertex_id,
            ARRAY[vertex_id]::INTEGER[],
            ARRAY[vertex_id]::INTEGER[],
            FALSE
        FROM vertices
        WHERE graph_id = p_graph_id

        UNION ALL

        SELECT
            p.start_vertex,
            e.destination_vertex,

            CASE
                WHEN e.destination_vertex = ANY(p.active_path)
                THEN p.path || e.destination_vertex
                ELSE p.path || e.destination_vertex
            END,

            CASE
                WHEN e.destination_vertex = ANY(p.active_path)
                THEN p.active_path
                ELSE p.active_path || e.destination_vertex
            END,

            e.destination_vertex = ANY(p.active_path)

        FROM paths p
        JOIN edges e
          ON e.graph_id = p_graph_id
         AND e.source_vertex = p.current_vertex

        WHERE NOT p.has_cycle
    )
    SELECT path
    INTO found_path
    FROM paths
    WHERE has_cycle
    LIMIT 1;

    RETURN QUERY
    SELECT
        found_path IS NOT NULL,
        COALESCE(found_path, ARRAY[]::INTEGER[]);
END;
$$;

-- ------------------------------------------------------------
-- 11. Directed cycle detection using Kahn's algorithm
--
-- Repeatedly removes indegree-zero vertices.
-- If processed vertex count is smaller than V, a cycle exists.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION detect_directed_cycle_kahn(
    p_graph_id BIGINT
)
RETURNS TABLE (
    has_cycle BOOLEAN,
    processed_vertices INTEGER
)
LANGUAGE plpgsql
AS $$
DECLARE
    configured_type graph_type;
    configured_count INTEGER;
    current_vertex INTEGER;
    current_indegree INTEGER;
    processed INTEGER := 0;
    queue_vertices INTEGER[];
BEGIN
    SELECT graph_kind, vertex_count
    INTO configured_type, configured_count
    FROM graphs
    WHERE graph_id = p_graph_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown graph ID: %', p_graph_id;
    END IF;

    IF configured_type <> 'DIRECTED' THEN
        RAISE EXCEPTION
            'Kahn algorithm requires a directed graph.';
    END IF;

    CREATE TEMP TABLE IF NOT EXISTS kahn_indegree (
        vertex_id INTEGER PRIMARY KEY,
        indegree INTEGER NOT NULL
    ) ON COMMIT DROP;

    TRUNCATE TABLE kahn_indegree;

    INSERT INTO kahn_indegree(vertex_id, indegree)
    SELECT
        v.vertex_id,
        COUNT(e.edge_id)::INTEGER
    FROM vertices v
    LEFT JOIN edges e
      ON e.graph_id = v.graph_id
     AND e.destination_vertex = v.vertex_id
    WHERE v.graph_id = p_graph_id
    GROUP BY v.vertex_id;

    SELECT ARRAY_AGG(vertex_id ORDER BY vertex_id)
    INTO queue_vertices
    FROM kahn_indegree
    WHERE indegree = 0;

    IF queue_vertices IS NULL THEN
        queue_vertices := ARRAY[]::INTEGER[];
    END IF;

    WHILE cardinality(queue_vertices) > 0 LOOP
        current_vertex := queue_vertices[1];

        queue_vertices :=
            queue_vertices[2:cardinality(queue_vertices)];

        processed := processed + 1;

        FOR current_vertex IN
            SELECT destination_vertex
            FROM edges
            WHERE graph_id = p_graph_id
              AND source_vertex = current_vertex
        LOOP
            UPDATE kahn_indegree
            SET indegree = indegree - 1
            WHERE vertex_id = current_vertex
            RETURNING indegree INTO current_indegree;

            IF current_indegree = 0 THEN
                queue_vertices :=
                    array_append(queue_vertices, current_vertex);
            END IF;
        END LOOP;
    END LOOP;

    RETURN QUERY
    SELECT
        processed <> configured_count,
        processed;
END;
$$;

-- ------------------------------------------------------------
-- 12. Undirected cycle detection using recursive connectivity
--
-- A component is built using recursive reachability.
-- DSU is generally more efficient for incremental edge
-- processing. This SQL implementation evaluates whether
-- an undirected graph satisfies the forest edge condition.
--
-- For a multigraph:
-- E > V - C indicates at least one cycle.
-- Self-loops and parallel edges are counted separately.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION detect_undirected_cycle_dsu(
    p_graph_id BIGINT
)
RETURNS TABLE (
    has_cycle BOOLEAN,
    component_count INTEGER,
    edge_count BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    configured_type graph_type;
    configured_count INTEGER;
    total_edges BIGINT;
    total_components INTEGER;
BEGIN
    SELECT graph_kind, vertex_count
    INTO configured_type, configured_count
    FROM graphs
    WHERE graph_id = p_graph_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown graph ID: %', p_graph_id;
    END IF;

    IF configured_type <> 'UNDIRECTED' THEN
        RAISE EXCEPTION
            'DSU cycle detection requires an undirected graph.';
    END IF;

    SELECT COUNT(*)
    INTO total_edges
    FROM edges
    WHERE graph_id = p_graph_id;

    WITH RECURSIVE reachability(root, vertex_id) AS (
        SELECT vertex_id, vertex_id
        FROM vertices
        WHERE graph_id = p_graph_id

        UNION

        SELECT
            r.root,
            CASE
                WHEN e.source_vertex = r.vertex_id
                THEN e.destination_vertex
                ELSE e.source_vertex
            END
        FROM reachability r
        JOIN edges e
          ON e.graph_id = p_graph_id
         AND (
             e.source_vertex = r.vertex_id
             OR e.destination_vertex = r.vertex_id
         )
    ),
    components AS (
        SELECT vertex_id, MIN(root) AS component_root
        FROM reachability
        GROUP BY vertex_id
    )
    SELECT COUNT(DISTINCT component_root)::INTEGER
    INTO total_components
    FROM components;

    RETURN QUERY
    SELECT
        total_edges::NUMERIC >
            configured_count::NUMERIC - total_components::NUMERIC,
        total_components,
        total_edges;
END;
$$;

-- ------------------------------------------------------------
-- 13. General cycle detection service
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION evaluate_graph(
    p_graph_id BIGINT,
    p_algorithm detection_algorithm
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    configured_type graph_type;
    current_result BOOLEAN;
    processed INTEGER := 0;
    cycle_path INTEGER[] := ARRAY[]::INTEGER[];
    new_run_id BIGINT;
BEGIN
    SELECT graph_kind
    INTO configured_type
    FROM graphs
    WHERE graph_id = p_graph_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown graph ID.';
    END IF;

    IF p_algorithm IN ('DIRECTED_DFS', 'DIRECTED_KAHN')
       AND configured_type <> 'DIRECTED' THEN
        RAISE EXCEPTION
            'Directed algorithm cannot evaluate an undirected graph.';
    END IF;

    IF p_algorithm IN (
        'UNDIRECTED_DSU',
        'UNDIRECTED_DFS',
        'UNDIRECTED_BFS'
    )
    AND configured_type <> 'UNDIRECTED' THEN
        RAISE EXCEPTION
            'Undirected algorithm cannot evaluate a directed graph.';
    END IF;

    IF p_algorithm = 'DIRECTED_DFS' THEN
        SELECT has_cycle, detected_cycle
        INTO current_result, cycle_path
        FROM detect_directed_cycle_dfs(p_graph_id);

    ELSIF p_algorithm = 'DIRECTED_KAHN' THEN
        SELECT has_cycle, processed_vertices
        INTO current_result, processed
        FROM detect_directed_cycle_kahn(p_graph_id);

    ELSIF p_algorithm = 'UNDIRECTED_DSU' THEN
        SELECT has_cycle
        INTO current_result
        FROM detect_undirected_cycle_dsu(p_graph_id);

    ELSE
        RAISE EXCEPTION
            'Use DIRECTED_DFS, DIRECTED_KAHN or UNDIRECTED_DSU.';
    END IF;

    INSERT INTO detection_runs(
        graph_id,
        algorithm,
        result,
        detected_cycle,
        processed_vertices,
        details
    )
    VALUES (
        p_graph_id,
        p_algorithm,
        CASE
            WHEN current_result THEN 'CYCLE_FOUND'::cycle_status
            ELSE 'ACYCLIC'::cycle_status
        END,
        cycle_path,
        processed,
        jsonb_build_object(
            'graph_type', configured_type,
            'algorithm', p_algorithm
        )
    )
    RETURNING run_id INTO new_run_id;

    UPDATE graphs
    SET status = CASE
        WHEN current_result THEN 'REJECTED'::graph_status
        ELSE 'VALIDATED'::graph_status
    END
    WHERE graph_id = p_graph_id;

    RETURN new_run_id;
END;
$$;

-- ------------------------------------------------------------
-- 14. Graph reporting view
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW graph_statistics AS
SELECT
    g.graph_id,
    g.graph_name,
    g.graph_kind,
    g.status,
    g.vertex_count,
    COUNT(DISTINCT e.edge_id) AS edge_count,
    COUNT(DISTINCT r.run_id) AS detection_run_count,
    COUNT(DISTINCT r.run_id)
        FILTER (WHERE r.result = 'CYCLE_FOUND')
        AS cycle_detection_count,
    COUNT(DISTINCT r.run_id)
        FILTER (WHERE r.result = 'ACYCLIC')
        AS acyclic_detection_count
FROM graphs g
LEFT JOIN edges e
    ON e.graph_id = g.graph_id
LEFT JOIN detection_runs r
    ON r.graph_id = g.graph_id
GROUP BY
    g.graph_id,
    g.graph_name,
    g.graph_kind,
    g.status,
    g.vertex_count;

-- ------------------------------------------------------------
-- 15. Sample graph records
-- ------------------------------------------------------------

DO $$
DECLARE
    dag_id BIGINT;
    cyclic_id BIGINT;
    undirected_tree_id BIGINT;
    undirected_cycle_id BIGINT;
    self_loop_id BIGINT;
    disconnected_id BIGINT;
BEGIN
    dag_id := create_graph(
        'Project Dependency DAG',
        'DIRECTED',
        6
    );

    PERFORM add_graph_edge(dag_id, 0, 1);
    PERFORM add_graph_edge(dag_id, 0, 2);
    PERFORM add_graph_edge(dag_id, 1, 3);
    PERFORM add_graph_edge(dag_id, 2, 3);
    PERFORM add_graph_edge(dag_id, 3, 4);
    PERFORM add_graph_edge(dag_id, 4, 5);

    cyclic_id := create_graph(
        'Circular Dependency Graph',
        'DIRECTED',
        5
    );

    PERFORM add_graph_edge(cyclic_id, 0, 1);
    PERFORM add_graph_edge(cyclic_id, 1, 2);
    PERFORM add_graph_edge(cyclic_id, 2, 3);
    PERFORM add_graph_edge(cyclic_id, 3, 1);
    PERFORM add_graph_edge(cyclic_id, 3, 4);

    undirected_tree_id := create_graph(
        'Infrastructure Tree',
        'UNDIRECTED',
        5
    );

    PERFORM add_graph_edge(undirected_tree_id, 0, 1);
    PERFORM add_graph_edge(undirected_tree_id, 0, 2);
    PERFORM add_graph_edge(undirected_tree_id, 1, 3);
    PERFORM add_graph_edge(undirected_tree_id, 1, 4);

    undirected_cycle_id := create_graph(
        'Infrastructure Ring',
        'UNDIRECTED',
        4
    );

    PERFORM add_graph_edge(undirected_cycle_id, 0, 1);
    PERFORM add_graph_edge(undirected_cycle_id, 1, 2);
    PERFORM add_graph_edge(undirected_cycle_id, 2, 0);
    PERFORM add_graph_edge(undirected_cycle_id, 2, 3);

    self_loop_id := create_graph(
        'Self Loop Example',
        'DIRECTED',
        2
    );

    PERFORM add_graph_edge(self_loop_id, 1, 1);

    disconnected_id := create_graph(
        'Disconnected Forest',
        'UNDIRECTED',
        6
    );

    PERFORM add_graph_edge(disconnected_id, 0, 1);
    PERFORM add_graph_edge(disconnected_id, 2, 3);
    PERFORM add_graph_edge(disconnected_id, 4, 5);

    -- Sample IDs remain available through graph_name lookups.
END;
$$;

-- ------------------------------------------------------------
-- 16. Execute graph evaluations
-- ------------------------------------------------------------

DO $$
DECLARE
    current_id BIGINT;
BEGIN
    SELECT graph_id INTO current_id
    FROM graphs
    WHERE graph_name = 'Project Dependency DAG';

    PERFORM evaluate_graph(current_id, 'DIRECTED_DFS');
    PERFORM evaluate_graph(current_id, 'DIRECTED_KAHN');

    SELECT graph_id INTO current_id
    FROM graphs
    WHERE graph_name = 'Circular Dependency Graph';

    PERFORM evaluate_graph(current_id, 'DIRECTED_DFS');
    PERFORM evaluate_graph(current_id, 'DIRECTED_KAHN');

    SELECT graph_id INTO current_id
    FROM graphs
    WHERE graph_name = 'Infrastructure Tree';

    PERFORM evaluate_graph(current_id, 'UNDIRECTED_DSU');

    SELECT graph_id INTO current_id
    FROM graphs
    WHERE graph_name = 'Infrastructure Ring';

    PERFORM evaluate_graph(current_id, 'UNDIRECTED_DSU');

    SELECT graph_id INTO current_id
    FROM graphs
    WHERE graph_name = 'Self Loop Example';

    PERFORM evaluate_graph(current_id, 'DIRECTED_DFS');

    SELECT graph_id INTO current_id
    FROM graphs
    WHERE graph_name = 'Disconnected Forest';

    PERFORM evaluate_graph(current_id, 'UNDIRECTED_DSU');
END;
$$;

-- ------------------------------------------------------------
-- 17. Retrieval query
-- ------------------------------------------------------------

SELECT
    g.graph_name,
    g.graph_kind,
    v.vertex_id,
    v.vertex_label
FROM graphs g
JOIN vertices v
    ON v.graph_id = g.graph_id
ORDER BY g.graph_name, v.vertex_id;

-- ------------------------------------------------------------
-- 18. Edge retrieval
-- ------------------------------------------------------------

SELECT
    g.graph_name,
    e.source_vertex,
    e.destination_vertex
FROM graphs g
JOIN edges e
    ON e.graph_id = g.graph_id
ORDER BY g.graph_name, e.edge_id;

-- ------------------------------------------------------------
-- 19. Cycle evaluation report
-- ------------------------------------------------------------

SELECT
    g.graph_name,
    r.algorithm,
    r.result,
    r.detected_cycle,
    r.processed_vertices,
    r.executed_at
FROM detection_runs r
JOIN graphs g
    ON g.graph_id = r.graph_id
ORDER BY g.graph_name, r.executed_at;

-- ------------------------------------------------------------
-- 20. Aggregate graph statistics
-- ------------------------------------------------------------

SELECT *
FROM graph_statistics
ORDER BY graph_name;

-- ------------------------------------------------------------
-- 21. Detect directed edges participating in a self-loop
-- ------------------------------------------------------------

SELECT
    g.graph_name,
    e.source_vertex
FROM graphs g
JOIN edges e
    ON e.graph_id = g.graph_id
WHERE g.graph_kind = 'DIRECTED'
  AND e.source_vertex = e.destination_vertex;

-- ------------------------------------------------------------
-- 22. Forest validation
--
-- An undirected graph is a forest if E = V - C.
-- This includes disconnected graphs and isolated vertices.
-- ------------------------------------------------------------

SELECT
    g.graph_name,
    g.vertex_count,
    COUNT(DISTINCT e.edge_id) AS edge_count,
    s.component_count,
    (
        COUNT(DISTINCT e.edge_id)
        = g.vertex_count - s.component_count
    ) AS is_forest
FROM graphs g
JOIN LATERAL detect_undirected_cycle_dsu(g.graph_id)
    AS s(has_cycle, component_count, edge_count)
    ON g.graph_kind = 'UNDIRECTED'
LEFT JOIN edges e
    ON e.graph_id = g.graph_id
GROUP BY
    g.graph_id,
    g.graph_name,
    g.vertex_count,
    s.component_count
ORDER BY g.graph_name;

-- ------------------------------------------------------------
-- 23. Demonstrate transaction rollback
--
-- An invalid edge must not remain in the database.
-- ------------------------------------------------------------

DO $$
DECLARE
    test_graph_id BIGINT;
    rollback_verified BOOLEAN := FALSE;
BEGIN
    SELECT graph_id
    INTO test_graph_id
    FROM graphs
    WHERE graph_name = 'Project Dependency DAG';

    BEGIN
        PERFORM add_graph_edge(test_graph_id, 0, 999);
    EXCEPTION
        WHEN foreign_key_violation THEN
            rollback_verified := TRUE;
    END;

    IF NOT rollback_verified THEN
        RAISE EXCEPTION
            'Invalid edge validation failed.';
    END IF;

    RAISE NOTICE
        'Invalid edge correctly rejected and rolled back.';
END;
$$;

-- ------------------------------------------------------------
-- 24. Failure-case demonstration
--
-- Invalid graph type and invalid identifiers are rejected.
-- ------------------------------------------------------------

DO $$
DECLARE
    test_graph_id BIGINT;
    rejection_confirmed BOOLEAN := FALSE;
BEGIN
    SELECT graph_id
    INTO test_graph_id
    FROM graphs
    WHERE graph_name = 'Project Dependency DAG';

    BEGIN
        PERFORM evaluate_graph(
            test_graph_id,
            'UNDIRECTED_DSU'
        );
    EXCEPTION
        WHEN raise_exception THEN
            rejection_confirmed := TRUE;
    END;

    IF NOT rejection_confirmed THEN
        RAISE EXCEPTION
            'Graph type mismatch was not rejected.';
    END IF;
END;
$$;

-- ------------------------------------------------------------
-- 25. Database integrity checks
-- ------------------------------------------------------------

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM edges e
        LEFT JOIN vertices s
          ON s.graph_id = e.graph_id
         AND s.vertex_id = e.source_vertex
        LEFT JOIN vertices d
          ON d.graph_id = e.graph_id
         AND d.vertex_id = e.destination_vertex
        WHERE s.vertex_id IS NULL
           OR d.vertex_id IS NULL
    ) THEN
        RAISE EXCEPTION 'Orphan edge detected.';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM graphs g
        WHERE (
            SELECT COUNT(*)
            FROM vertices v
            WHERE v.graph_id = g.graph_id
        ) <> g.vertex_count
    ) THEN
        RAISE EXCEPTION 'Vertex registry is incomplete.';
    END IF;
END;
$$;

COMMIT;

-- ============================================================
-- IMPORTANT IMPLEMENTATION LIMITATIONS
--
-- 1. Recursive DFS uses recursive SQL path enumeration rather
--    than an iterative adjacency-list traversal.
--
-- 2. Kahn's algorithm uses a temporary relational queue.
--
-- 3. The undirected DSU function uses the equivalent forest
--    condition E > V - C rather than materializing DSU parents.
--
-- 4. Recursive reachability can be expensive on large graphs.
--
-- 5. For high-volume graph processing, use an application-level
--    iterative DFS or DSU implementation.
--
-- 6. Graph mutation and evaluation are transactionally
--    protected through row-level locking in evaluate_graph.
-- ============================================================
