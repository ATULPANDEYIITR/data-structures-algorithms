-- ============================================================
-- SHORTEST PATH INTRODUCTION
-- PostgreSQL weighted graph and shortest-path workflow
-- ============================================================

DROP SCHEMA IF EXISTS shortest_path CASCADE;

CREATE SCHEMA shortest_path;

SET search_path TO shortest_path, public;

-- ------------------------------------------------------------
-- 1. Domain model
-- ------------------------------------------------------------

CREATE TABLE graph (
    graph_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_name VARCHAR(150) NOT NULL UNIQUE,
    directed BOOLEAN NOT NULL DEFAULT TRUE,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE vertex (
    vertex_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_id BIGINT NOT NULL REFERENCES graph(graph_id)
        ON DELETE CASCADE,
    vertex_code VARCHAR(80) NOT NULL,
    vertex_name VARCHAR(150) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (graph_id, vertex_code),
    UNIQUE (graph_id, vertex_id)
);

CREATE TABLE edge (
    edge_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_id BIGINT NOT NULL,
    source_vertex_id BIGINT NOT NULL,
    target_vertex_id BIGINT NOT NULL,
    weight NUMERIC(14, 4) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (graph_id, source_vertex_id)
        REFERENCES vertex(graph_id, vertex_id),

    FOREIGN KEY (graph_id, target_vertex_id)
        REFERENCES vertex(graph_id, vertex_id),

    CHECK (source_vertex_id <> target_vertex_id)
);

CREATE INDEX idx_vertex_graph
    ON vertex(graph_id, active);

CREATE INDEX idx_edge_source
    ON edge(graph_id, source_vertex_id)
    WHERE active = TRUE;

CREATE INDEX idx_edge_target
    ON edge(graph_id, target_vertex_id)
    WHERE active = TRUE;

CREATE INDEX idx_edge_weight
    ON edge(graph_id, weight)
    WHERE active = TRUE;

-- ------------------------------------------------------------
-- 2. Algorithm execution records
-- ------------------------------------------------------------

CREATE TABLE algorithm_run (
    run_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_id BIGINT NOT NULL REFERENCES graph(graph_id),
    source_vertex_id BIGINT NOT NULL,
    target_vertex_id BIGINT NOT NULL,

    algorithm VARCHAR(30) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'PENDING',

    shortest_distance NUMERIC(18, 4),
    computed_path BIGINT[],

    negative_edge_present BOOLEAN NOT NULL DEFAULT FALSE,
    negative_cycle_detected BOOLEAN NOT NULL DEFAULT FALSE,

    graph_version BIGINT NOT NULL DEFAULT 0,

    execution_started_at TIMESTAMPTZ,
    execution_finished_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (graph_id, source_vertex_id)
        REFERENCES vertex(graph_id, vertex_id),

    FOREIGN KEY (graph_id, target_vertex_id)
        REFERENCES vertex(graph_id, vertex_id),

    CHECK (
        algorithm IN (
            'DIJKSTRA',
            'BELLMAN_FORD',
            'RECURSIVE_PATHS'
        )
    ),

    CHECK (
        status IN (
            'PENDING',
            'RUNNING',
            'COMPLETED',
            'UNREACHABLE',
            'FAILED',
            'NEGATIVE_CYCLE'
        )
    )
);

CREATE INDEX idx_algorithm_run_graph
    ON algorithm_run(graph_id, created_at DESC);

CREATE TABLE path_step (
    run_id BIGINT NOT NULL REFERENCES algorithm_run(run_id)
        ON DELETE CASCADE,
    step_number INTEGER NOT NULL,
    vertex_id BIGINT NOT NULL REFERENCES vertex(vertex_id),
    cumulative_distance NUMERIC(18, 4) NOT NULL,

    PRIMARY KEY (run_id, step_number),

    CHECK (step_number >= 0)
);

-- ------------------------------------------------------------
-- 3. Graph validation
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_edge_graph()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.weight IS NULL THEN
        RAISE EXCEPTION 'Edge weight cannot be NULL.';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM vertex
        WHERE graph_id = NEW.graph_id
          AND vertex_id = NEW.source_vertex_id
          AND active = TRUE
    ) THEN
        RAISE EXCEPTION 'Source vertex is missing or inactive.';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM vertex
        WHERE graph_id = NEW.graph_id
          AND vertex_id = NEW.target_vertex_id
          AND active = TRUE
    ) THEN
        RAISE EXCEPTION 'Target vertex is missing or inactive.';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_edge
BEFORE INSERT OR UPDATE ON edge
FOR EACH ROW
EXECUTE FUNCTION validate_edge_graph();

-- ------------------------------------------------------------
-- 4. Graph version tracking
-- ------------------------------------------------------------

CREATE TABLE graph_revision (
    graph_id BIGINT PRIMARY KEY REFERENCES graph(graph_id)
        ON DELETE CASCADE,
    revision BIGINT NOT NULL DEFAULT 0
);

CREATE OR REPLACE FUNCTION update_graph_revision()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    affected_graph BIGINT;
BEGIN
    IF TG_OP = 'DELETE' THEN
        affected_graph := OLD.graph_id;
    ELSE
        affected_graph := NEW.graph_id;
    END IF;

    INSERT INTO graph_revision(graph_id, revision)
    VALUES (affected_graph, 1)
    ON CONFLICT (graph_id)
    DO UPDATE SET revision =
        graph_revision.revision + 1;

    RETURN CASE
        WHEN TG_OP = 'DELETE' THEN OLD
        ELSE NEW
    END;
END;
$$;

CREATE TRIGGER trg_edge_revision
AFTER INSERT OR UPDATE OR DELETE ON edge
FOR EACH ROW
EXECUTE FUNCTION update_graph_revision();

-- ------------------------------------------------------------
-- 5. Algorithm selection
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION choose_algorithm(
    p_graph_id BIGINT
)
RETURNS VARCHAR
LANGUAGE plpgsql
AS $$
DECLARE
    negative_exists BOOLEAN;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM graph WHERE graph_id = p_graph_id
    ) THEN
        RAISE EXCEPTION 'Graph does not exist: %', p_graph_id;
    END IF;

    SELECT EXISTS (
        SELECT 1
        FROM edge
        WHERE graph_id = p_graph_id
          AND active = TRUE
          AND weight < 0
    )
    INTO negative_exists;

    IF negative_exists THEN
        RETURN 'BELLMAN_FORD';
    END IF;

    RETURN 'DIJKSTRA';
END;
$$;

-- ------------------------------------------------------------
-- 6. Graph inspection views
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW active_graph_edges AS
SELECT
    g.graph_id,
    g.graph_name,
    s.vertex_code AS source_code,
    s.vertex_name AS source_name,
    t.vertex_code AS target_code,
    t.vertex_name AS target_name,
    e.weight
FROM edge e
JOIN graph g
    ON g.graph_id = e.graph_id
JOIN vertex s
    ON s.vertex_id = e.source_vertex_id
JOIN vertex t
    ON t.vertex_id = e.target_vertex_id
WHERE e.active = TRUE
  AND s.active = TRUE
  AND t.active = TRUE;

CREATE OR REPLACE VIEW graph_statistics AS
SELECT
    g.graph_id,
    g.graph_name,
    COUNT(DISTINCT v.vertex_id) FILTER (
        WHERE v.active = TRUE
    ) AS vertex_count,
    COUNT(DISTINCT e.edge_id) FILTER (
        WHERE e.active = TRUE
    ) AS edge_count,
    COUNT(DISTINCT e.edge_id) FILTER (
        WHERE e.active = TRUE AND e.weight < 0
    ) AS negative_edge_count,
    MIN(e.weight) FILTER (
        WHERE e.active = TRUE
    ) AS minimum_weight,
    MAX(e.weight) FILTER (
        WHERE e.active = TRUE
    ) AS maximum_weight
FROM graph g
LEFT JOIN vertex v
    ON v.graph_id = g.graph_id
LEFT JOIN edge e
    ON e.graph_id = g.graph_id
GROUP BY g.graph_id, g.graph_name;

-- ------------------------------------------------------------
-- 7. Sample transportation graph
-- ------------------------------------------------------------

BEGIN;

INSERT INTO graph (
    graph_name,
    directed,
    description
)
VALUES
(
    'Indian Transport Network',
    TRUE,
    'Directed weighted transportation network.'
),
(
    'Negative Weight Demonstration',
    TRUE,
    'Graph containing a negative edge without a negative cycle.'
),
(
    'Negative Cycle Demonstration',
    TRUE,
    'Graph containing a reachable negative cycle.'
);

INSERT INTO vertex (
    graph_id,
    vertex_code,
    vertex_name
)
SELECT
    g.graph_id,
    data.vertex_code,
    data.vertex_name
FROM graph g
CROSS JOIN (
    VALUES
        ('DEL', 'Delhi'),
        ('JAI', 'Jaipur'),
        ('AGR', 'Agra'),
        ('BHO', 'Bhopal'),
        ('MUM', 'Mumbai'),
        ('CHD', 'Chandigarh'),
        ('KOL', 'Kolkata')
) AS data(vertex_code, vertex_name)
WHERE g.graph_name = 'Indian Transport Network';

INSERT INTO edge (
    graph_id,
    source_vertex_id,
    target_vertex_id,
    weight
)
SELECT
    g.graph_id,
    s.vertex_id,
    t.vertex_id,
    data.weight
FROM graph g
JOIN (
    VALUES
        ('DEL', 'JAI', 280::NUMERIC),
        ('DEL', 'AGR', 230::NUMERIC),
        ('JAI', 'MUM', 1140::NUMERIC),
        ('AGR', 'BHO', 540::NUMERIC),
        ('BHO', 'MUM', 780::NUMERIC),
        ('JAI', 'AGR', 240::NUMERIC),
        ('AGR', 'JAI', 250::NUMERIC),
        ('DEL', 'CHD', 250::NUMERIC),
        ('CHD', 'JAI', 480::NUMERIC)
) AS data(source_code, target_code, weight)
    ON TRUE
JOIN vertex s
    ON s.graph_id = g.graph_id
   AND s.vertex_code = data.source_code
JOIN vertex t
    ON t.graph_id = g.graph_id
   AND t.vertex_code = data.target_code
WHERE g.graph_name = 'Indian Transport Network';

INSERT INTO vertex (
    graph_id,
    vertex_code,
    vertex_name
)
SELECT
    g.graph_id,
    data.vertex_code,
    data.vertex_name
FROM graph g
CROSS JOIN (
    VALUES
        ('A', 'Node A'),
        ('B', 'Node B'),
        ('C', 'Node C'),
        ('D', 'Node D')
) AS data(vertex_code, vertex_name)
WHERE g.graph_name IN (
    'Negative Weight Demonstration',
    'Negative Cycle Demonstration'
);

INSERT INTO edge (
    graph_id,
    source_vertex_id,
    target_vertex_id,
    weight
)
SELECT
    g.graph_id,
    s.vertex_id,
    t.vertex_id,
    data.weight
FROM graph g
JOIN (
    VALUES
        ('A', 'B', 4::NUMERIC),
        ('A', 'C', 5::NUMERIC),
        ('B', 'C', -3::NUMERIC),
        ('C', 'D', 4::NUMERIC),
        ('B', 'D', 8::NUMERIC)
) AS data(source_code, target_code, weight)
    ON TRUE
JOIN vertex s
    ON s.graph_id = g.graph_id
   AND s.vertex_code = data.source_code
JOIN vertex t
    ON t.graph_id = g.graph_id
   AND t.vertex_code = data.target_code
WHERE g.graph_name = 'Negative Weight Demonstration';

INSERT INTO edge (
    graph_id,
    source_vertex_id,
    target_vertex_id,
    weight
)
SELECT
    g.graph_id,
    s.vertex_id,
    t.vertex_id,
    data.weight
FROM graph g
JOIN (
    VALUES
        ('A', 'B', 2::NUMERIC),
        ('B', 'C', -4::NUMERIC),
        ('C', 'B', 1::NUMERIC),
        ('A', 'D', 5::NUMERIC)
) AS data(source_code, target_code, weight)
    ON TRUE
JOIN vertex s
    ON s.graph_id = g.graph_id
   AND s.vertex_code = data.source_code
JOIN vertex t
    ON t.graph_id = g.graph_id
   AND t.vertex_code = data.target_code
WHERE g.graph_name = 'Negative Cycle Demonstration';

COMMIT;

-- ------------------------------------------------------------
-- 8. Recursive path exploration
-- ------------------------------------------------------------
-- This query enumerates simple paths. It supports negative
-- edges but excludes repeated vertices. It is intended for
-- small demonstration graphs, not large production networks.

CREATE OR REPLACE FUNCTION enumerate_simple_paths(
    p_graph_id BIGINT,
    p_source_code VARCHAR,
    p_target_code VARCHAR,
    p_max_depth INTEGER DEFAULT 10
)
RETURNS TABLE (
    vertex_path TEXT[],
    total_distance NUMERIC,
    hop_count INTEGER
)
LANGUAGE plpgsql
AS $$
DECLARE
    source_id BIGINT;
    target_id BIGINT;
BEGIN
    IF p_max_depth < 0 OR p_max_depth > 100 THEN
        RAISE EXCEPTION 'Maximum depth must be between 0 and 100.';
    END IF;

    SELECT vertex_id
    INTO source_id
    FROM vertex
    WHERE graph_id = p_graph_id
      AND vertex_code = p_source_code
      AND active = TRUE;

    IF source_id IS NULL THEN
        RAISE EXCEPTION 'Unknown source vertex: %', p_source_code;
    END IF;

    SELECT vertex_id
    INTO target_id
    FROM vertex
    WHERE graph_id = p_graph_id
      AND vertex_code = p_target_code
      AND active = TRUE;

    IF target_id IS NULL THEN
        RAISE EXCEPTION 'Unknown target vertex: %', p_target_code;
    END IF;

    RETURN QUERY
    WITH RECURSIVE paths AS (
        SELECT
            source_id AS current_vertex,
            ARRAY[source_id]::BIGINT[] AS visited,
            ARRAY[p_source_code::TEXT] AS path_codes,
            0::NUMERIC AS cost,
            0::INTEGER AS depth

        UNION ALL

        SELECT
            e.target_vertex_id,
            p.visited || e.target_vertex_id,
            p.path_codes || target.vertex_code::TEXT,
            p.cost + e.weight,
            p.depth + 1
        FROM paths p
        JOIN edge e
            ON e.graph_id = p_graph_id
           AND e.source_vertex_id = p.current_vertex
           AND e.active = TRUE
        JOIN vertex target
            ON target.vertex_id = e.target_vertex_id
           AND target.active = TRUE
        WHERE p.depth < p_max_depth
          AND NOT e.target_vertex_id = ANY(p.visited)
    )
    SELECT
        p.path_codes,
        p.cost,
        p.depth
    FROM paths p
    WHERE p.current_vertex = target_id
    ORDER BY p.cost, p.depth;
END;
$$;

-- ------------------------------------------------------------
-- 9. Shortest-path report using simple path enumeration
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION shortest_path_report(
    p_graph_id BIGINT,
    p_source_code VARCHAR,
    p_target_code VARCHAR,
    p_max_depth INTEGER DEFAULT 10
)
RETURNS TABLE (
    path TEXT[],
    distance NUMERIC,
    hops INTEGER,
    selected_algorithm VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    selected_algorithm VARCHAR;
BEGIN
    selected_algorithm := choose_algorithm(p_graph_id);

    RETURN QUERY
    SELECT
        p.vertex_path,
        p.total_distance,
        p.hop_count,
        selected_algorithm
    FROM enumerate_simple_paths(
        p_graph_id,
        p_source_code,
        p_target_code,
        p_max_depth
    ) p
    ORDER BY p.total_distance, p.hop_count
    LIMIT 1;
END;
$$;

-- ------------------------------------------------------------
-- 10. Execution workflow
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE execute_path_request(
    p_graph_id BIGINT,
    p_source_code VARCHAR,
    p_target_code VARCHAR,
    p_max_depth INTEGER DEFAULT 10
)
LANGUAGE plpgsql
AS $$
DECLARE
    source_id BIGINT;
    target_id BIGINT;
    selected_algorithm VARCHAR;
    selected_path TEXT[];
    selected_distance NUMERIC;
    selected_hops INTEGER;
    current_revision BIGINT;
    new_run_id BIGINT;
BEGIN
    SELECT vertex_id INTO source_id
    FROM vertex
    WHERE graph_id = p_graph_id
      AND vertex_code = p_source_code
      AND active = TRUE;

    SELECT vertex_id INTO target_id
    FROM vertex
    WHERE graph_id = p_graph_id
      AND vertex_code = p_target_code
      AND active = TRUE;

    IF source_id IS NULL OR target_id IS NULL THEN
        RAISE EXCEPTION 'Source or target vertex is invalid.';
    END IF;

    SELECT COALESCE(revision, 0)
    INTO current_revision
    FROM graph_revision
    WHERE graph_id = p_graph_id;

    current_revision := COALESCE(current_revision, 0);

    selected_algorithm := choose_algorithm(p_graph_id);

    INSERT INTO algorithm_run (
        graph_id,
        source_vertex_id,
        target_vertex_id,
        algorithm,
        status,
        negative_edge_present,
        graph_version,
        execution_started_at
    )
    VALUES (
        p_graph_id,
        source_id,
        target_id,
        selected_algorithm,
        'RUNNING',
        selected_algorithm = 'BELLMAN_FORD',
        current_revision,
        CURRENT_TIMESTAMP
    )
    RETURNING run_id INTO new_run_id;

    SELECT
        p.path,
        p.distance,
        p.hops
    INTO
        selected_path,
        selected_distance,
        selected_hops
    FROM shortest_path_report(
        p_graph_id,
        p_source_code,
        p_target_code,
        p_max_depth
    ) p
    LIMIT 1;

    IF selected_path IS NULL THEN
        UPDATE algorithm_run
        SET status = 'UNREACHABLE',
            execution_finished_at = CURRENT_TIMESTAMP
        WHERE run_id = new_run_id;

        RETURN;
    END IF;

    UPDATE algorithm_run
    SET status = 'COMPLETED',
        shortest_distance = selected_distance,
        computed_path = ARRAY(
            SELECT v.vertex_id
            FROM unnest(selected_path) WITH ORDINALITY
                AS p(vertex_code, position)
            JOIN vertex v
                ON v.graph_id = p_graph_id
               AND v.vertex_code = p.vertex_code
            ORDER BY p.position
        ),
        execution_finished_at = CURRENT_TIMESTAMP
    WHERE run_id = new_run_id;

    INSERT INTO path_step (
        run_id,
        step_number,
        vertex_id,
        cumulative_distance
    )
    SELECT
        new_run_id,
        p.position::INTEGER - 1,
        v.vertex_id,
        COALESCE(
            (
                SELECT SUM(e.weight)
                FROM unnest(selected_path)
                    WITH ORDINALITY AS q(vertex_code, position)
                JOIN vertex previous_vertex
                    ON previous_vertex.graph_id = p_graph_id
                   AND previous_vertex.vertex_code = q.vertex_code
                JOIN vertex next_vertex
                    ON next_vertex.graph_id = p_graph_id
                   AND next_vertex.vertex_code = p.vertex_code
                JOIN edge e
                    ON e.graph_id = p_graph_id
                   AND e.source_vertex_id = previous_vertex.vertex_id
                   AND e.target_vertex_id = next_vertex.vertex_id
                   AND e.active = TRUE
                WHERE q.position = p.position - 1
            ),
            0
        )::NUMERIC
    FROM unnest(selected_path)
        WITH ORDINALITY AS p(vertex_code, position)
    JOIN vertex v
        ON v.graph_id = p_graph_id
       AND v.vertex_code = p.vertex_code;
END;
$$;

-- ------------------------------------------------------------
-- 11. Retrieval and reporting
-- ------------------------------------------------------------

-- Graph inventory.
SELECT * FROM graph_statistics
ORDER BY graph_id;

-- Inspect the transportation network.
SELECT *
FROM active_graph_edges
WHERE graph_name = 'Indian Transport Network'
ORDER BY source_code, target_code;

-- Determine the correct algorithm.
SELECT
    graph_name,
    choose_algorithm(graph_id) AS selected_algorithm
FROM graph;

-- Shortest path: Delhi to Mumbai.
SELECT *
FROM shortest_path_report(
    (SELECT graph_id FROM graph
     WHERE graph_name = 'Indian Transport Network'),
    'DEL',
    'MUM',
    10
);

-- All simple paths in the negative-edge demonstration.
SELECT *
FROM enumerate_simple_paths(
    (SELECT graph_id FROM graph
     WHERE graph_name = 'Negative Weight Demonstration'),
    'A',
    'D',
    10
);

-- Negative-edge shortest path.
SELECT *
FROM shortest_path_report(
    (SELECT graph_id FROM graph
     WHERE graph_name = 'Negative Weight Demonstration'),
    'A',
    'D',
    10
);

-- ------------------------------------------------------------
-- 12. Transactional execution examples
-- ------------------------------------------------------------

BEGIN;

CALL execute_path_request(
    (SELECT graph_id FROM graph
     WHERE graph_name = 'Indian Transport Network'),
    'DEL',
    'MUM',
    10
);

COMMIT;

BEGIN;

CALL execute_path_request(
    (SELECT graph_id FROM graph
     WHERE graph_name = 'Negative Weight Demonstration'),
    'A',
    'D',
    10
);

COMMIT;

-- ------------------------------------------------------------
-- 13. Execution history
-- ------------------------------------------------------------

SELECT
    r.run_id,
    g.graph_name,
    source.vertex_name AS source,
    target.vertex_name AS target,
    r.algorithm,
    r.status,
    r.shortest_distance,
    r.graph_version,
    r.execution_started_at,
    r.execution_finished_at
FROM algorithm_run r
JOIN graph g
    ON g.graph_id = r.graph_id
JOIN vertex source
    ON source.vertex_id = r.source_vertex_id
JOIN vertex target
    ON target.vertex_id = r.target_vertex_id
ORDER BY r.run_id;

-- ------------------------------------------------------------
-- 14. Detailed path steps
-- ------------------------------------------------------------

SELECT
    ps.run_id,
    ps.step_number,
    v.vertex_name,
    ps.cumulative_distance
FROM path_step ps
JOIN vertex v
    ON v.vertex_id = ps.vertex_id
ORDER BY ps.run_id, ps.step_number;

-- ------------------------------------------------------------
-- 15. Negative-cycle evaluation
-- ------------------------------------------------------------
-- A negative edge alone does not imply a negative cycle.
-- The following query identifies a negative two-edge cycle.
-- General negative-cycle detection requires an algorithmic
-- relaxation process such as Bellman-Ford.

SELECT
    g.graph_name,
    source.vertex_code AS source,
    target.vertex_code AS target,
    e1.weight + e2.weight AS cycle_weight
FROM edge e1
JOIN edge e2
    ON e1.graph_id = e2.graph_id
   AND e1.source_vertex_id = e2.target_vertex_id
   AND e1.target_vertex_id = e2.source_vertex_id
JOIN graph g
    ON g.graph_id = e1.graph_id
JOIN vertex source
    ON source.vertex_id = e1.source_vertex_id
JOIN vertex target
    ON target.vertex_id = e1.target_vertex_id
WHERE e1.active = TRUE
  AND e2.active = TRUE
  AND e1.edge_id < e2.edge_id
  AND e1.weight + e2.weight < 0;

-- ------------------------------------------------------------
-- 16. Data-quality checks
-- ------------------------------------------------------------

-- Vertices without outgoing edges.
SELECT
    v.vertex_code,
    v.vertex_name
FROM vertex v
LEFT JOIN edge e
    ON e.graph_id = v.graph_id
   AND e.source_vertex_id = v.vertex_id
   AND e.active = TRUE
WHERE v.active = TRUE
  AND e.edge_id IS NULL;

-- Graphs with negative edges.
SELECT
    graph_id,
    graph_name,
    negative_edge_count
FROM graph_statistics
WHERE negative_edge_count > 0;

-- Completed and unreachable execution counts.
SELECT
    graph_id,
    status,
    COUNT(*) AS execution_count
FROM algorithm_run
GROUP BY graph_id, status
ORDER BY graph_id, status;

-- ------------------------------------------------------------
-- 17. Performance inspection
-- ------------------------------------------------------------

EXPLAIN ANALYZE
SELECT *
FROM active_graph_edges
WHERE graph_id = (
    SELECT graph_id
    FROM graph
    WHERE graph_name = 'Indian Transport Network'
);

-- Recursive path enumeration can grow exponentially.
-- For large graphs, implement indexed Dijkstra or Bellman-Ford
-- using an application service or an iterative database routine.
