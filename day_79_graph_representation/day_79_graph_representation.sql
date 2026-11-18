-- ============================================================
-- GRAPH REPRESENTATION AND ANALYSIS DATABASE
-- PostgreSQL 15+
--
-- Models:
--   Graphs
--   Vertices
--   Edges
--   Representation configurations
--   Graph storage measurements
--   Traversal results
--   Shortest-path results
--   Representation performance comparisons
--
-- Supports:
--   Adjacency matrix
--   Adjacency list
--   Edge list
--   Directed and undirected graphs
--   Weighted edges
--   BFS
--   DFS
--   Dijkstra shortest paths
--   Storage and performance reporting
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS graph_lab;

SET search_path TO graph_lab, public;

-- ------------------------------------------------------------
-- 1. Domain types
-- ------------------------------------------------------------

CREATE TYPE graph_lab.representation_type AS ENUM (
    'ADJACENCY_MATRIX',
    'ADJACENCY_LIST',
    'EDGE_LIST'
);

CREATE TYPE graph_lab.graph_direction AS ENUM (
    'DIRECTED',
    'UNDIRECTED'
);

CREATE TYPE graph_lab.execution_status AS ENUM (
    'PENDING',
    'RUNNING',
    'COMPLETED',
    'FAILED'
);

-- ------------------------------------------------------------
-- 2. Graph definitions
-- ------------------------------------------------------------

CREATE TABLE graph_lab.graphs (
    graph_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    graph_name VARCHAR(150) NOT NULL UNIQUE,

    description TEXT NOT NULL DEFAULT '',

    representation graph_lab.representation_type NOT NULL,

    direction graph_lab.graph_direction NOT NULL,

    vertex_count INTEGER NOT NULL CHECK (vertex_count >= 0),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT graph_name_nonempty
        CHECK (length(trim(graph_name)) > 0)
);

-- ------------------------------------------------------------
-- 3. Vertices
-- ------------------------------------------------------------

CREATE TABLE graph_lab.vertices (
    graph_id BIGINT NOT NULL,

    vertex_id INTEGER NOT NULL CHECK (vertex_id >= 0),

    vertex_label VARCHAR(150) NOT NULL,

    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (graph_id, vertex_id),

    UNIQUE (graph_id, vertex_label),

    FOREIGN KEY (graph_id)
        REFERENCES graph_lab.graphs(graph_id)
        ON DELETE CASCADE,

    CONSTRAINT vertex_metadata_object
        CHECK (jsonb_typeof(metadata) = 'object')
);

CREATE INDEX idx_vertices_graph_label
    ON graph_lab.vertices(graph_id, vertex_label);

-- ------------------------------------------------------------
-- 4. Edge storage
--
-- A single logical edge is stored once.
-- Undirected edge endpoints are normalized so source <= target.
-- Directed edges retain their original direction.
-- ------------------------------------------------------------

CREATE TABLE graph_lab.edges (
    edge_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    graph_id BIGINT NOT NULL,

    source_vertex INTEGER NOT NULL,

    target_vertex INTEGER NOT NULL,

    weight DOUBLE PRECISION NOT NULL DEFAULT 1.0,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (graph_id, source_vertex)
        REFERENCES graph_lab.vertices(graph_id, vertex_id)
        ON DELETE CASCADE,

    FOREIGN KEY (graph_id, target_vertex)
        REFERENCES graph_lab.vertices(graph_id, vertex_id)
        ON DELETE CASCADE,

    CONSTRAINT edge_weight_finite
        CHECK (
            weight > '-Infinity'::DOUBLE PRECISION
            AND weight < 'Infinity'::DOUBLE PRECISION
        ),

    CONSTRAINT edge_unique
        UNIQUE (graph_id, source_vertex, target_vertex)
);

CREATE INDEX idx_edges_source
    ON graph_lab.edges(graph_id, source_vertex);

CREATE INDEX idx_edges_target
    ON graph_lab.edges(graph_id, target_vertex);

CREATE INDEX idx_edges_weight
    ON graph_lab.edges(graph_id, weight);

-- ------------------------------------------------------------
-- 5. Storage and benchmark records
-- ------------------------------------------------------------

CREATE TABLE graph_lab.storage_measurements (
    measurement_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    graph_id BIGINT NOT NULL
        REFERENCES graph_lab.graphs(graph_id)
        ON DELETE CASCADE,

    representation graph_lab.representation_type NOT NULL,

    estimated_bytes BIGINT NOT NULL CHECK (estimated_bytes >= 0),

    measured_bytes BIGINT CHECK (
        measured_bytes IS NULL OR measured_bytes >= 0
    ),

    measurement_method VARCHAR(100) NOT NULL,

    measured_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_storage_graph_time
    ON graph_lab.storage_measurements(graph_id, measured_at DESC);

CREATE TABLE graph_lab.benchmark_runs (
    benchmark_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    graph_id BIGINT NOT NULL
        REFERENCES graph_lab.graphs(graph_id)
        ON DELETE CASCADE,

    operation_name VARCHAR(50) NOT NULL,

    execution_status graph_lab.execution_status NOT NULL
        DEFAULT 'PENDING',

    repetitions INTEGER NOT NULL CHECK (repetitions > 0),

    execution_time_ms NUMERIC(18, 6)
        CHECK (
            execution_time_ms IS NULL OR execution_time_ms >= 0
        ),

    error_message TEXT,

    executed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT benchmark_completion_consistency
        CHECK (
            execution_status <> 'COMPLETED'
            OR execution_time_ms IS NOT NULL
        )
);

CREATE INDEX idx_benchmark_graph_operation
    ON graph_lab.benchmark_runs(
        graph_id,
        operation_name,
        executed_at DESC
    );

-- ------------------------------------------------------------
-- 6. Traversal records
-- ------------------------------------------------------------

CREATE TABLE graph_lab.traversal_runs (
    traversal_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    graph_id BIGINT NOT NULL
        REFERENCES graph_lab.graphs(graph_id)
        ON DELETE CASCADE,

    start_vertex INTEGER NOT NULL,

    algorithm VARCHAR(10) NOT NULL
        CHECK (algorithm IN ('BFS', 'DFS')),

    traversal_order INTEGER[] NOT NULL DEFAULT '{}',

    execution_time_ms NUMERIC(18, 6)
        CHECK (
            execution_time_ms IS NULL OR execution_time_ms >= 0
        ),

    executed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (graph_id, start_vertex)
        REFERENCES graph_lab.vertices(graph_id, vertex_id)
);

CREATE TABLE graph_lab.shortest_path_results (
    result_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    graph_id BIGINT NOT NULL
        REFERENCES graph_lab.graphs(graph_id)
        ON DELETE CASCADE,

    source_vertex INTEGER NOT NULL,

    target_vertex INTEGER NOT NULL,

    distance DOUBLE PRECISION NOT NULL,

    algorithm VARCHAR(30) NOT NULL DEFAULT 'DIJKSTRA',

    calculated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (graph_id, source_vertex)
        REFERENCES graph_lab.vertices(graph_id, vertex_id),

    FOREIGN KEY (graph_id, target_vertex)
        REFERENCES graph_lab.vertices(graph_id, vertex_id),

    UNIQUE (
        graph_id,
        source_vertex,
        target_vertex,
        algorithm
    ),

    CHECK (
        distance >= 0
        AND distance < 'Infinity'::DOUBLE PRECISION
    )
);

-- ------------------------------------------------------------
-- 7. Validate graph vertex capacity and edge direction
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION graph_lab.validate_edge()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    graph_direction_value graph_lab.graph_direction;
BEGIN
    SELECT direction
    INTO graph_direction_value
    FROM graph_lab.graphs
    WHERE graph_id = NEW.graph_id
    FOR SHARE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Graph % does not exist', NEW.graph_id;
    END IF;

    IF graph_direction_value = 'UNDIRECTED' THEN
        IF NEW.source_vertex > NEW.target_vertex THEN
            RAISE EXCEPTION
                'Undirected edge endpoints must be normalized: source <= target';
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_edge
BEFORE INSERT OR UPDATE ON graph_lab.edges
FOR EACH ROW
EXECUTE FUNCTION graph_lab.validate_edge();

-- ------------------------------------------------------------
-- 8. Ensure declared vertex count matches stored vertices
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION graph_lab.validate_graph_vertex_count()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    actual_count BIGINT;
BEGIN
    SELECT count(*)
    INTO actual_count
    FROM graph_lab.vertices
    WHERE graph_id = NEW.graph_id;

    IF actual_count > (
        SELECT vertex_count
        FROM graph_lab.graphs
        WHERE graph_id = NEW.graph_id
    ) THEN
        RAISE EXCEPTION
            'Graph % exceeds declared vertex count',
            NEW.graph_id;
    END IF;

    RETURN NEW;
END;
$$;

CREATE CONSTRAINT TRIGGER trg_graph_vertex_capacity
AFTER INSERT ON graph_lab.vertices
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW
EXECUTE FUNCTION graph_lab.validate_graph_vertex_count();

-- ------------------------------------------------------------
-- 9. Create graph and its vertices atomically
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE graph_lab.create_graph(
    p_graph_name VARCHAR,
    p_representation graph_lab.representation_type,
    p_direction graph_lab.graph_direction,
    p_vertex_count INTEGER
)
LANGUAGE plpgsql
AS $$
DECLARE
    new_graph_id BIGINT;
    vertex_number INTEGER;
BEGIN
    IF p_graph_name IS NULL OR length(trim(p_graph_name)) = 0 THEN
        RAISE EXCEPTION 'Graph name cannot be empty';
    END IF;

    IF p_vertex_count < 0 THEN
        RAISE EXCEPTION 'Vertex count cannot be negative';
    END IF;

    INSERT INTO graph_lab.graphs (
        graph_name,
        representation,
        direction,
        vertex_count
    )
    VALUES (
        p_graph_name,
        p_representation,
        p_direction,
        p_vertex_count
    )
    RETURNING graph_id INTO new_graph_id;

    FOR vertex_number IN 0..p_vertex_count - 1 LOOP
        INSERT INTO graph_lab.vertices (
            graph_id,
            vertex_id,
            vertex_label
        )
        VALUES (
            new_graph_id,
            vertex_number,
            'Vertex ' || vertex_number
        );
    END LOOP;

    RAISE NOTICE
        'Created graph % with ID %',
        p_graph_name,
        new_graph_id;
END;
$$;

-- ------------------------------------------------------------
-- 10. Add an edge using logical graph semantics
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION graph_lab.add_edge(
    p_graph_id BIGINT,
    p_source INTEGER,
    p_target INTEGER,
    p_weight DOUBLE PRECISION DEFAULT 1.0
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    graph_direction_value graph_lab.graph_direction;
    normalized_source INTEGER;
    normalized_target INTEGER;
    new_edge_id BIGINT;
BEGIN
    IF p_weight IS NULL
       OR p_weight <= '-Infinity'::DOUBLE PRECISION
       OR p_weight >= 'Infinity'::DOUBLE PRECISION THEN
        RAISE EXCEPTION 'Edge weight must be finite';
    END IF;

    SELECT direction
    INTO graph_direction_value
    FROM graph_lab.graphs
    WHERE graph_id = p_graph_id
    FOR SHARE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Graph does not exist';
    END IF;

    normalized_source := p_source;
    normalized_target := p_target;

    IF graph_direction_value = 'UNDIRECTED'
       AND p_source > p_target THEN
        normalized_source := p_target;
        normalized_target := p_source;
    END IF;

    INSERT INTO graph_lab.edges (
        graph_id,
        source_vertex,
        target_vertex,
        weight
    )
    VALUES (
        p_graph_id,
        normalized_source,
        normalized_target,
        p_weight
    )
    ON CONFLICT (
        graph_id,
        source_vertex,
        target_vertex
    )
    DO UPDATE SET weight = EXCLUDED.weight
    RETURNING edge_id INTO new_edge_id;

    RETURN new_edge_id;
END;
$$;

-- ------------------------------------------------------------
-- 11. Return logical neighbors
--
-- Undirected edges are interpreted in both directions.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION graph_lab.get_neighbors(
    p_graph_id BIGINT,
    p_vertex INTEGER
)
RETURNS TABLE (
    neighbor_vertex INTEGER,
    edge_weight DOUBLE PRECISION
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    graph_direction_value graph_lab.graph_direction;
BEGIN
    SELECT direction
    INTO graph_direction_value
    FROM graph_lab.graphs
    WHERE graph_id = p_graph_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Graph does not exist';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM graph_lab.vertices
        WHERE graph_id = p_graph_id
          AND vertex_id = p_vertex
    ) THEN
        RAISE EXCEPTION 'Vertex does not exist';
    END IF;

    RETURN QUERY
    SELECT
        e.target_vertex,
        e.weight
    FROM graph_lab.edges e
    WHERE e.graph_id = p_graph_id
      AND e.source_vertex = p_vertex

    UNION ALL

    SELECT
        e.source_vertex,
        e.weight
    FROM graph_lab.edges e
    WHERE e.graph_id = p_graph_id
      AND graph_direction_value = 'UNDIRECTED'
      AND e.target_vertex = p_vertex
      AND e.source_vertex <> p_vertex

    ORDER BY 1;
END;
$$;

-- ------------------------------------------------------------
-- 12. Edge existence check
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION graph_lab.edge_exists(
    p_graph_id BIGINT,
    p_source INTEGER,
    p_target INTEGER
)
RETURNS BOOLEAN
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    graph_direction_value graph_lab.graph_direction;
    result BOOLEAN;
BEGIN
    SELECT direction
    INTO graph_direction_value
    FROM graph_lab.graphs
    WHERE graph_id = p_graph_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Graph does not exist';
    END IF;

    IF graph_direction_value = 'UNDIRECTED' THEN
        SELECT EXISTS (
            SELECT 1
            FROM graph_lab.edges
            WHERE graph_id = p_graph_id
              AND (
                    (source_vertex = p_source AND target_vertex = p_target)
                    OR
                    (source_vertex = p_target AND target_vertex = p_source)
              )
        )
        INTO result;
    ELSE
        SELECT EXISTS (
            SELECT 1
            FROM graph_lab.edges
            WHERE graph_id = p_graph_id
              AND source_vertex = p_source
              AND target_vertex = p_target
        )
        INTO result;
    END IF;

    RETURN result;
END;
$$;

-- ------------------------------------------------------------
-- 13. Graph density and degree statistics
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW graph_lab.graph_statistics AS
WITH edge_counts AS (
    SELECT
        g.graph_id,
        g.graph_name,
        g.representation,
        g.direction,
        g.vertex_count,
        count(e.edge_id)::BIGINT AS stored_edge_count
    FROM graph_lab.graphs g
    LEFT JOIN graph_lab.edges e
        ON e.graph_id = g.graph_id
    GROUP BY
        g.graph_id,
        g.graph_name,
        g.representation,
        g.direction,
        g.vertex_count
)
SELECT
    graph_id,
    graph_name,
    representation,
    direction,
    vertex_count,
    stored_edge_count,
    CASE
        WHEN direction = 'DIRECTED'
            THEN vertex_count::NUMERIC *
                 GREATEST(vertex_count - 1, 0)
        ELSE vertex_count::NUMERIC *
             GREATEST(vertex_count - 1, 0) / 2
    END AS maximum_simple_edges,
    CASE
        WHEN vertex_count <= 1 THEN 0
        WHEN direction = 'DIRECTED'
            THEN stored_edge_count::NUMERIC /
                 (vertex_count::NUMERIC * (vertex_count - 1))
        ELSE stored_edge_count::NUMERIC /
             (vertex_count::NUMERIC * (vertex_count - 1) / 2)
    END AS graph_density
FROM edge_counts;

-- ------------------------------------------------------------
-- 14. Representation complexity reference
-- ------------------------------------------------------------

CREATE TABLE graph_lab.representation_characteristics (
    representation graph_lab.representation_type PRIMARY KEY,

    space_complexity VARCHAR(30) NOT NULL,

    edge_lookup_complexity VARCHAR(30) NOT NULL,

    neighbor_iteration_complexity VARCHAR(30) NOT NULL,

    insertion_complexity VARCHAR(30) NOT NULL,

    best_use_case TEXT NOT NULL
);

INSERT INTO graph_lab.representation_characteristics
VALUES
(
    'ADJACENCY_MATRIX',
    'O(V^2)',
    'O(1)',
    'O(V)',
    'O(1)',
    'Dense graphs and frequent edge-existence queries'
),
(
    'ADJACENCY_LIST',
    'O(V + E)',
    'O(degree)',
    'O(degree)',
    'O(1) average',
    'Sparse graphs and traversal-heavy applications'
),
(
    'EDGE_LIST',
    'O(E)',
    'O(E)',
    'O(E)',
    'O(1) amortized append',
    'Edge processing, storage, and sorting workflows'
)
ON CONFLICT (representation) DO UPDATE
SET
    space_complexity = EXCLUDED.space_complexity,
    edge_lookup_complexity = EXCLUDED.edge_lookup_complexity,
    neighbor_iteration_complexity =
        EXCLUDED.neighbor_iteration_complexity,
    insertion_complexity = EXCLUDED.insertion_complexity,
    best_use_case = EXCLUDED.best_use_case;

-- ------------------------------------------------------------
-- 15. Sample graph records
-- ------------------------------------------------------------

CALL graph_lab.create_graph(
    'Road Network Matrix',
    'ADJACENCY_MATRIX',
    'UNDIRECTED',
    6
);

CALL graph_lab.create_graph(
    'Road Network List',
    'ADJACENCY_LIST',
    'UNDIRECTED',
    6
);

CALL graph_lab.create_graph(
    'Road Network Edge Collection',
    'EDGE_LIST',
    'UNDIRECTED',
    6
);

CALL graph_lab.create_graph(
    'Directed Dependency Network',
    'ADJACENCY_LIST',
    'DIRECTED',
    5
);

-- Store the graph identifiers in a temporary lookup table.

CREATE TEMP TABLE sample_graph_ids AS
SELECT
    graph_id,
    graph_name
FROM graph_lab.graphs
WHERE graph_name IN (
    'Road Network Matrix',
    'Road Network List',
    'Road Network Edge Collection',
    'Directed Dependency Network'
);

-- Insert identical edges into all three representations.

DO $$
DECLARE
    graph_record RECORD;
BEGIN
    FOR graph_record IN
        SELECT graph_id
        FROM graph_lab.graphs
        WHERE graph_name IN (
            'Road Network Matrix',
            'Road Network List',
            'Road Network Edge Collection'
        )
    LOOP
        PERFORM graph_lab.add_edge(graph_record.graph_id, 0, 1, 4);
        PERFORM graph_lab.add_edge(graph_record.graph_id, 0, 2, 2);
        PERFORM graph_lab.add_edge(graph_record.graph_id, 1, 2, 1);
        PERFORM graph_lab.add_edge(graph_record.graph_id, 1, 3, 5);
        PERFORM graph_lab.add_edge(graph_record.graph_id, 2, 3, 8);
        PERFORM graph_lab.add_edge(graph_record.graph_id, 2, 4, 10);
        PERFORM graph_lab.add_edge(graph_record.graph_id, 3, 4, 2);
        PERFORM graph_lab.add_edge(graph_record.graph_id, 4, 5, 3);
    END LOOP;
END;
$$;

-- Directed dependency edges.

DO $$
DECLARE
    graph_identifier BIGINT;
BEGIN
    SELECT graph_id
    INTO graph_identifier
    FROM graph_lab.graphs
    WHERE graph_name = 'Directed Dependency Network';

    PERFORM graph_lab.add_edge(graph_identifier, 0, 1, 2);
    PERFORM graph_lab.add_edge(graph_identifier, 0, 2, 3);
    PERFORM graph_lab.add_edge(graph_identifier, 1, 3, 4);
    PERFORM graph_lab.add_edge(graph_identifier, 2, 3, 1);
    PERFORM graph_lab.add_edge(graph_identifier, 3, 4, 2);
END;
$$;

-- ------------------------------------------------------------
-- 16. Record representative storage estimates
-- These are analytical estimates, not measured server storage.
-- ------------------------------------------------------------

INSERT INTO graph_lab.storage_measurements (
    graph_id,
    representation,
    estimated_bytes,
    measurement_method
)
SELECT
    g.graph_id,
    g.representation,
    CASE g.representation
        WHEN 'ADJACENCY_MATRIX'
            THEN g.vertex_count::BIGINT *
                 g.vertex_count::BIGINT * 9
        WHEN 'ADJACENCY_LIST'
            THEN g.vertex_count::BIGINT * 48 +
                 count(e.edge_id)::BIGINT * 64 *
                 CASE
                    WHEN g.direction = 'UNDIRECTED' THEN 2
                    ELSE 1
                 END
        WHEN 'EDGE_LIST'
            THEN count(e.edge_id)::BIGINT * 40
    END,
    'Analytical estimate using representation-specific storage model'
FROM graph_lab.graphs g
LEFT JOIN graph_lab.edges e
    ON e.graph_id = g.graph_id
GROUP BY
    g.graph_id,
    g.representation,
    g.vertex_count,
    g.direction;

-- ------------------------------------------------------------
-- 17. Record example benchmark results
-- Actual execution benchmarks should be inserted by an external
-- benchmark process. The sample values below are illustrative.
-- ------------------------------------------------------------

INSERT INTO graph_lab.benchmark_runs (
    graph_id,
    operation_name,
    execution_status,
    repetitions,
    execution_time_ms
)
SELECT
    graph_id,
    'EDGE_LOOKUP',
    'COMPLETED',
    1000,
    CASE representation
        WHEN 'ADJACENCY_MATRIX' THEN 0.12
        WHEN 'ADJACENCY_LIST' THEN 0.35
        WHEN 'EDGE_LIST' THEN 2.40
    END
FROM graph_lab.graphs
WHERE graph_name IN (
    'Road Network Matrix',
    'Road Network List',
    'Road Network Edge Collection'
);

-- ------------------------------------------------------------
-- 18. BFS implementation using a recursive CTE
--
-- The recursive path prevents revisiting vertices.
-- UNION rather than UNION ALL also protects against repeated
-- identical recursive states.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION graph_lab.breadth_first(
    p_graph_id BIGINT,
    p_start INTEGER
)
RETURNS INTEGER[]
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    result INTEGER[];
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM graph_lab.vertices
        WHERE graph_id = p_graph_id
          AND vertex_id = p_start
    ) THEN
        RAISE EXCEPTION 'Invalid BFS start vertex';
    END IF;

    WITH RECURSIVE traversal AS (
        SELECT
            p_start AS vertex_id,
            ARRAY[p_start] AS visited,
            0 AS depth,
            ARRAY[p_start] AS traversal_order

        UNION ALL

        SELECT
            neighbor.neighbor_vertex,
            traversal.visited || neighbor.neighbor_vertex,
            traversal.depth + 1,
            traversal.traversal_order || neighbor.neighbor_vertex
        FROM traversal
        CROSS JOIN LATERAL graph_lab.get_neighbors(
            p_graph_id,
            traversal.vertex_id
        ) AS neighbor
        WHERE NOT (
            neighbor.neighbor_vertex = ANY(traversal.visited)
        )
    )
    SELECT traversal_order
    INTO result
    FROM traversal
    ORDER BY depth DESC
    LIMIT 1;

    RETURN result;
END;
$$;

-- ------------------------------------------------------------
-- 19. Dijkstra shortest paths
--
-- This implementation uses a temporary working table.
-- Each iteration selects the unsettled vertex with the
-- smallest tentative distance.
-- It is intended for educational and moderate-sized graphs.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION graph_lab.dijkstra(
    p_graph_id BIGINT,
    p_start INTEGER
)
RETURNS TABLE (
    target_vertex INTEGER,
    shortest_distance DOUBLE PRECISION
)
LANGUAGE plpgsql
AS $$
DECLARE
    current_vertex INTEGER;
    current_distance DOUBLE PRECISION;
    neighbor_record RECORD;
    candidate_distance DOUBLE PRECISION;
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM graph_lab.vertices
        WHERE graph_id = p_graph_id
          AND vertex_id = p_start
    ) THEN
        RAISE EXCEPTION 'Invalid Dijkstra source vertex';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM graph_lab.edges
        WHERE graph_id = p_graph_id
          AND weight < 0
    ) THEN
        RAISE EXCEPTION
            'Dijkstra does not support negative edge weights';
    END IF;

    CREATE TEMP TABLE IF NOT EXISTS pg_temp.graph_distance_work (
        vertex_id INTEGER PRIMARY KEY,
        distance DOUBLE PRECISION NOT NULL,
        settled BOOLEAN NOT NULL DEFAULT FALSE
    ) ON COMMIT DROP;

    TRUNCATE pg_temp.graph_distance_work;

    INSERT INTO pg_temp.graph_distance_work (
        vertex_id,
        distance,
        settled
    )
    SELECT
        vertex_id,
        CASE
            WHEN vertex_id = p_start THEN 0.0
            ELSE 'Infinity'::DOUBLE PRECISION
        END,
        FALSE
    FROM graph_lab.vertices
    WHERE graph_id = p_graph_id;

    LOOP
        SELECT
            vertex_id,
            distance
        INTO
            current_vertex,
            current_distance
        FROM pg_temp.graph_distance_work
        WHERE NOT settled
        ORDER BY distance, vertex_id
        LIMIT 1;

        EXIT WHEN NOT FOUND;
        EXIT WHEN current_distance = 'Infinity'::DOUBLE PRECISION;

        UPDATE pg_temp.graph_distance_work
        SET settled = TRUE
        WHERE vertex_id = current_vertex;

        FOR neighbor_record IN
            SELECT
                neighbor_vertex,
                edge_weight
            FROM graph_lab.get_neighbors(
                p_graph_id,
                current_vertex
            )
        LOOP
            candidate_distance :=
                current_distance + neighbor_record.edge_weight;

            UPDATE pg_temp.graph_distance_work
            SET distance = candidate_distance
            WHERE vertex_id = neighbor_record.neighbor_vertex
              AND NOT settled
              AND distance > candidate_distance;
        END LOOP;
    END LOOP;

    RETURN QUERY
    SELECT
        vertex_id,
        distance
    FROM pg_temp.graph_distance_work
    ORDER BY vertex_id;
END;
$$;

-- ------------------------------------------------------------
-- 20. Graph comparison report
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW graph_lab.representation_comparison AS
SELECT
    g.graph_name,
    g.representation,
    g.direction,
    g.vertex_count,
    count(e.edge_id)::BIGINT AS stored_edges,
    COALESCE(sum(sm.estimated_bytes), 0) AS estimated_storage_bytes
FROM graph_lab.graphs g
LEFT JOIN graph_lab.edges e
    ON e.graph_id = g.graph_id
LEFT JOIN graph_lab.storage_measurements sm
    ON sm.graph_id = g.graph_id
GROUP BY
    g.graph_id,
    g.graph_name,
    g.representation,
    g.direction,
    g.vertex_count;

-- ------------------------------------------------------------
-- 21. Demonstration queries
-- ------------------------------------------------------------

-- Retrieve graph definitions.
SELECT *
FROM graph_lab.graphs
ORDER BY graph_id;

-- Compare graph statistics.
SELECT *
FROM graph_lab.graph_statistics
ORDER BY graph_name;

-- Compare representation complexity.
SELECT *
FROM graph_lab.representation_characteristics
ORDER BY representation;

-- Retrieve logical neighbors of vertex 0.
SELECT
    g.graph_name,
    n.neighbor_vertex,
    n.edge_weight
FROM graph_lab.graphs g
CROSS JOIN LATERAL graph_lab.get_neighbors(
    g.graph_id,
    0
) n
WHERE g.graph_name = 'Road Network List'
ORDER BY n.neighbor_vertex;

-- Validate whether an edge exists.
SELECT
    graph_name,
    graph_lab.edge_exists(graph_id, 0, 1) AS edge_exists
FROM graph_lab.graphs
WHERE graph_name = 'Road Network List';

-- Execute BFS.
SELECT
    graph_name,
    graph_lab.breadth_first(graph_id, 0) AS bfs_order
FROM graph_lab.graphs
WHERE graph_name = 'Road Network List';

-- Execute Dijkstra.
SELECT
    g.graph_name,
    d.target_vertex,
    d.shortest_distance
FROM graph_lab.graphs g
CROSS JOIN LATERAL graph_lab.dijkstra(
    g.graph_id,
    0
) d
WHERE g.graph_name = 'Road Network List'
ORDER BY d.target_vertex;

-- Retrieve benchmark results.
SELECT
    g.graph_name,
    b.operation_name,
    b.repetitions,
    b.execution_time_ms,
    b.execution_status
FROM graph_lab.benchmark_runs b
JOIN graph_lab.graphs g
    ON g.graph_id = b.graph_id
ORDER BY b.execution_time_ms;

-- Aggregate average benchmark execution times.
SELECT
    g.representation,
    b.operation_name,
    AVG(b.execution_time_ms) AS average_execution_ms,
    MIN(b.execution_time_ms) AS minimum_execution_ms,
    MAX(b.execution_time_ms) AS maximum_execution_ms
FROM graph_lab.benchmark_runs b
JOIN graph_lab.graphs g
    ON g.graph_id = b.graph_id
WHERE b.execution_status = 'COMPLETED'
GROUP BY
    g.representation,
    b.operation_name
ORDER BY
    g.representation,
    b.operation_name;

-- Storage comparison.
SELECT
    g.graph_name,
    g.representation,
    sm.estimated_bytes,
    sm.measured_bytes,
    sm.measurement_method
FROM graph_lab.storage_measurements sm
JOIN graph_lab.graphs g
    ON g.graph_id = sm.graph_id
ORDER BY sm.estimated_bytes;

-- ------------------------------------------------------------
-- 22. Transactional edge update
-- A rollback demonstrates atomicity.
-- ------------------------------------------------------------

DO $$
DECLARE
    graph_identifier BIGINT;
BEGIN
    SELECT graph_id
    INTO graph_identifier
    FROM graph_lab.graphs
    WHERE graph_name = 'Road Network List';

    BEGIN
        INSERT INTO graph_lab.edges (
            graph_id,
            source_vertex,
            target_vertex,
            weight
        )
        VALUES (
            graph_identifier,
            0,
            5,
            99
        );

        RAISE NOTICE 'Temporary edge inserted.';

        ROLLBACK;

    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE
                'Transaction failed: %',
                SQLERRM;
    END;
END;
$$;

-- ------------------------------------------------------------
-- 23. Validate edge count against simple graph limits
-- ------------------------------------------------------------

SELECT
    g.graph_name,
    g.direction,
    g.vertex_count,
    count(e.edge_id) AS actual_edge_count,
    CASE
        WHEN g.direction = 'DIRECTED'
            THEN g.vertex_count::BIGINT *
                 GREATEST(g.vertex_count - 1, 0)
        ELSE g.vertex_count::BIGINT *
             GREATEST(g.vertex_count - 1, 0) / 2
    END AS maximum_edges,
    CASE
        WHEN count(e.edge_id) <=
            CASE
                WHEN g.direction = 'DIRECTED'
                    THEN g.vertex_count::BIGINT *
                         GREATEST(g.vertex_count - 1, 0)
                ELSE g.vertex_count::BIGINT *
                     GREATEST(g.vertex_count - 1, 0) / 2
            END
        THEN 'VALID'
        ELSE 'INVALID'
    END AS validation_result
FROM graph_lab.graphs g
LEFT JOIN graph_lab.edges e
    ON e.graph_id = g.graph_id
GROUP BY
    g.graph_id,
    g.graph_name,
    g.direction,
    g.vertex_count;

-- ------------------------------------------------------------
-- 24. Example graph density classification
-- ------------------------------------------------------------

SELECT
    graph_name,
    vertex_count,
    stored_edge_count,
    graph_density,
    CASE
        WHEN graph_density < 0.10 THEN 'SPARSE'
        WHEN graph_density < 0.50 THEN 'MODERATE'
        ELSE 'DENSE'
    END AS density_classification
FROM graph_lab.graph_statistics
ORDER BY graph_name;

COMMIT;
