-- ============================================================
-- DIJKSTRA'S SHORTEST PATH ALGORITHM
-- PostgreSQL 15+
--
-- Models:
--   Weighted directed and undirected graphs
--   Vertices and weighted edges
--   Dijkstra shortest-path execution
--   Path reconstruction
--   Route queries and graph validation
--
-- SQL implementation uses an array-based minimum selection.
-- Time complexity: O(V^2 + E) for the SQL implementation.
-- ============================================================

DROP SCHEMA IF EXISTS shortest_path CASCADE;

CREATE SCHEMA shortest_path;

SET search_path TO shortest_path, public;

-- ------------------------------------------------------------
-- 1. DOMAIN TABLES
-- ------------------------------------------------------------

CREATE TABLE graph (
    graph_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_name VARCHAR(120) NOT NULL UNIQUE,
    graph_type VARCHAR(20) NOT NULL
        CHECK (graph_type IN ('DIRECTED', 'UNDIRECTED')),
    description TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE vertex (
    vertex_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_id BIGINT NOT NULL REFERENCES graph(graph_id)
        ON DELETE CASCADE,
    vertex_name VARCHAR(120) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (graph_id, vertex_name),
    UNIQUE (graph_id, vertex_id)
);

CREATE TABLE edge (
    edge_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_id BIGINT NOT NULL,
    source_vertex_id BIGINT NOT NULL,
    destination_vertex_id BIGINT NOT NULL,
    weight BIGINT NOT NULL CHECK (weight >= 0),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    FOREIGN KEY (graph_id, source_vertex_id)
        REFERENCES vertex(graph_id, vertex_id)
        ON DELETE CASCADE,

    FOREIGN KEY (graph_id, destination_vertex_id)
        REFERENCES vertex(graph_id, vertex_id)
        ON DELETE CASCADE,

    CHECK (source_vertex_id <> destination_vertex_id),

    UNIQUE (
        graph_id,
        source_vertex_id,
        destination_vertex_id
    )
);

CREATE INDEX idx_vertex_graph_active
    ON vertex(graph_id, is_active, vertex_id);

CREATE INDEX idx_edge_source
    ON edge(graph_id, source_vertex_id)
    WHERE is_active = TRUE;

CREATE INDEX idx_edge_destination
    ON edge(graph_id, destination_vertex_id)
    WHERE is_active = TRUE;

CREATE INDEX idx_edge_weight
    ON edge(graph_id, weight)
    WHERE is_active = TRUE;

-- ------------------------------------------------------------
-- 2. ROUTE EXECUTION AUDIT
-- ------------------------------------------------------------

CREATE TABLE route_execution (
    execution_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_id BIGINT NOT NULL REFERENCES graph(graph_id),
    source_vertex_id BIGINT NOT NULL,
    destination_vertex_id BIGINT,
    execution_status VARCHAR(20) NOT NULL
        CHECK (
            execution_status IN (
                'RUNNING',
                'COMPLETED',
                'UNREACHABLE',
                'FAILED'
            )
        ),
    total_distance BIGINT CHECK (total_distance >= 0),
    route_vertex_ids BIGINT[] NOT NULL DEFAULT '{}',
    executed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    execution_duration_ms NUMERIC(12, 3),

    FOREIGN KEY (graph_id, source_vertex_id)
        REFERENCES vertex(graph_id, vertex_id),

    FOREIGN KEY (graph_id, destination_vertex_id)
        REFERENCES vertex(graph_id, vertex_id),

    CHECK (
        (execution_status = 'COMPLETED'
            AND destination_vertex_id IS NOT NULL
            AND total_distance IS NOT NULL)
        OR
        (execution_status = 'UNREACHABLE'
            AND destination_vertex_id IS NOT NULL
            AND total_distance IS NULL)
        OR
        (execution_status IN ('RUNNING', 'FAILED'))
    )
);

CREATE INDEX idx_execution_graph_time
    ON route_execution(graph_id, executed_at DESC);

-- ------------------------------------------------------------
-- 3. EDGE VALIDATION TRIGGER
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_edge_graph()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM vertex
        WHERE graph_id = NEW.graph_id
          AND vertex_id = NEW.source_vertex_id
          AND is_active = TRUE
    ) THEN
        RAISE EXCEPTION
            'Source vertex is missing or inactive';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM vertex
        WHERE graph_id = NEW.graph_id
          AND vertex_id = NEW.destination_vertex_id
          AND is_active = TRUE
    ) THEN
        RAISE EXCEPTION
            'Destination vertex is missing or inactive';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_edge
BEFORE INSERT OR UPDATE ON edge
FOR EACH ROW
EXECUTE FUNCTION validate_edge_graph();

-- ------------------------------------------------------------
-- 4. EDGE INSERTION PROCEDURE
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE add_edge(
    p_graph_id BIGINT,
    p_source_name VARCHAR,
    p_destination_name VARCHAR,
    p_weight BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_source BIGINT;
    v_destination BIGINT;
    v_graph_type VARCHAR(20);
BEGIN
    IF p_weight IS NULL OR p_weight < 0 THEN
        RAISE EXCEPTION
            'Edge weight must be non-negative';
    END IF;

    SELECT graph_type
    INTO v_graph_type
    FROM graph
    WHERE graph_id = p_graph_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Graph does not exist';
    END IF;

    SELECT vertex_id
    INTO v_source
    FROM vertex
    WHERE graph_id = p_graph_id
      AND vertex_name = p_source_name
      AND is_active = TRUE;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Source vertex % does not exist',
            p_source_name;
    END IF;

    SELECT vertex_id
    INTO v_destination
    FROM vertex
    WHERE graph_id = p_graph_id
      AND vertex_name = p_destination_name
      AND is_active = TRUE;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Destination vertex % does not exist',
            p_destination_name;
    END IF;

    IF v_source = v_destination THEN
        RAISE EXCEPTION
            'Self-loops are not supported';
    END IF;

    INSERT INTO edge (
        graph_id,
        source_vertex_id,
        destination_vertex_id,
        weight
    )
    VALUES (
        p_graph_id,
        v_source,
        v_destination,
        p_weight
    )
    ON CONFLICT (
        graph_id,
        source_vertex_id,
        destination_vertex_id
    )
    DO UPDATE SET
        weight = EXCLUDED.weight,
        is_active = TRUE;

    IF v_graph_type = 'UNDIRECTED' THEN
        INSERT INTO edge (
            graph_id,
            source_vertex_id,
            destination_vertex_id,
            weight
        )
        VALUES (
            p_graph_id,
            v_destination,
            v_source,
            p_weight
        )
        ON CONFLICT (
            graph_id,
            source_vertex_id,
            destination_vertex_id
        )
        DO UPDATE SET
            weight = EXCLUDED.weight,
            is_active = TRUE;
    END IF;
END;
$$;

-- ------------------------------------------------------------
-- 5. DIJKSTRA FUNCTION
--
-- The implementation maintains:
--   vertex_ids: Ordered vertex identifiers
--   distances: Best known distances
--   predecessors: Previous vertex on shortest path
--   visited: Settled vertex state
--
-- NULL distance means unreachable.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION dijkstra(
    p_graph_id BIGINT,
    p_source_name VARCHAR
)
RETURNS TABLE (
    vertex_id BIGINT,
    vertex_name VARCHAR,
    shortest_distance BIGINT,
    predecessor_id BIGINT,
    predecessor_name VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    vertex_ids BIGINT[];
    distances BIGINT[];
    predecessors BIGINT[];
    visited BOOLEAN[];

    n INTEGER;
    source_index INTEGER;
    current_index INTEGER;
    neighbor_index INTEGER;

    current_vertex BIGINT;
    neighbor_vertex BIGINT;
    current_distance BIGINT;
    edge_weight BIGINT;
    candidate BIGINT;

    i INTEGER;
    j INTEGER;
    found_vertex BOOLEAN;
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM graph
        WHERE graph_id = p_graph_id
    ) THEN
        RAISE EXCEPTION 'Graph does not exist';
    END IF;

    SELECT COALESCE(
        array_agg(v.vertex_id ORDER BY v.vertex_id),
        ARRAY[]::BIGINT[]
    )
    INTO vertex_ids
    FROM vertex v
    WHERE v.graph_id = p_graph_id
      AND v.is_active = TRUE;

    n := COALESCE(array_length(vertex_ids, 1), 0);

    IF n = 0 THEN
        RAISE EXCEPTION 'Graph has no active vertices';
    END IF;

    SELECT v.vertex_id
    INTO current_vertex
    FROM vertex v
    WHERE v.graph_id = p_graph_id
      AND v.vertex_name = p_source_name
      AND v.is_active = TRUE;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Source vertex % does not exist',
            p_source_name;
    END IF;

    source_index := array_position(
        vertex_ids,
        current_vertex
    );

    distances := array_fill(NULL::BIGINT, ARRAY[n]);
    predecessors := array_fill(NULL::BIGINT, ARRAY[n]);
    visited := array_fill(FALSE, ARRAY[n]);

    distances[source_index] := 0;

    LOOP
        current_index := NULL;
        current_distance := NULL;

        -- Find the unvisited vertex with the minimum known distance.
        FOR i IN 1..n LOOP
            IF NOT visited[i]
               AND distances[i] IS NOT NULL THEN

                IF current_index IS NULL
                   OR distances[i] < current_distance THEN
                    current_index := i;
                    current_distance := distances[i];
                END IF;
            END IF;
        END LOOP;

        -- No reachable unvisited vertex remains.
        EXIT WHEN current_index IS NULL;

        visited[current_index] := TRUE;
        current_vertex := vertex_ids[current_index];

        -- Relax all outgoing edges from the selected vertex.
        FOR neighbor_vertex, edge_weight IN
            SELECT
                e.destination_vertex_id,
                e.weight
            FROM edge e
            WHERE e.graph_id = p_graph_id
              AND e.source_vertex_id = current_vertex
              AND e.is_active = TRUE
        LOOP
            neighbor_index := array_position(
                vertex_ids,
                neighbor_vertex
            );

            IF neighbor_index IS NULL THEN
                CONTINUE;
            END IF;

            IF visited[neighbor_index] THEN
                CONTINUE;
            END IF;

            -- Prevent bigint overflow.
            IF current_distance >
               9223372036854775807 - edge_weight THEN
                RAISE EXCEPTION
                    'Distance overflow while processing edge % -> %',
                    current_vertex,
                    neighbor_vertex;
            END IF;

            candidate := current_distance + edge_weight;

            IF distances[neighbor_index] IS NULL
               OR candidate < distances[neighbor_index] THEN

                distances[neighbor_index] := candidate;
                predecessors[neighbor_index] := current_vertex;
            END IF;
        END LOOP;
    END LOOP;

    RETURN QUERY
    SELECT
        v.vertex_id,
        v.vertex_name,
        distances[i],
        predecessors[i],
        pv.vertex_name
    FROM generate_subscripts(vertex_ids, 1) AS s(i)
    JOIN vertex v
      ON v.vertex_id = vertex_ids[s.i]
     AND v.graph_id = p_graph_id
    LEFT JOIN vertex pv
      ON pv.vertex_id = predecessors[s.i]
     AND pv.graph_id = p_graph_id
    ORDER BY v.vertex_name;
END;
$$;

-- ------------------------------------------------------------
-- 6. SHORTEST PATH RECONSTRUCTION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION shortest_path(
    p_graph_id BIGINT,
    p_source_name VARCHAR,
    p_destination_name VARCHAR
)
RETURNS TABLE (
    step_number INTEGER,
    vertex_name VARCHAR,
    cumulative_distance BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    result_data RECORD;
    destination_id BIGINT;
    current_id BIGINT;
    previous_id BIGINT;
    current_distance BIGINT;

    route_ids BIGINT[] := ARRAY[]::BIGINT[];
    route_distances BIGINT[] := ARRAY[]::BIGINT[];

    source_id BIGINT;
    step_count INTEGER := 0;
    i INTEGER;
BEGIN
    SELECT vertex_id
    INTO source_id
    FROM vertex
    WHERE graph_id = p_graph_id
      AND vertex_name = p_source_name
      AND is_active = TRUE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown source vertex';
    END IF;

    SELECT vertex_id
    INTO destination_id
    FROM vertex
    WHERE graph_id = p_graph_id
      AND vertex_name = p_destination_name
      AND is_active = TRUE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown destination vertex';
    END IF;

    FOR result_data IN
        SELECT *
        FROM dijkstra(p_graph_id, p_source_name)
    LOOP
        IF result_data.vertex_id = destination_id THEN
            current_distance := result_data.shortest_distance;
            EXIT;
        END IF;
    END LOOP;

    IF current_distance IS NULL THEN
        RETURN;
    END IF;

    current_id := destination_id;

    LOOP
        step_count := step_count + 1;

        IF step_count > (
            SELECT COUNT(*)
            FROM vertex
            WHERE graph_id = p_graph_id
              AND is_active = TRUE
        ) THEN
            RAISE EXCEPTION
                'Cycle detected in predecessor chain';
        END IF;

        route_ids := array_append(route_ids, current_id);

        SELECT d.shortest_distance, d.predecessor_id
        INTO current_distance, previous_id
        FROM dijkstra(p_graph_id, p_source_name) d
        WHERE d.vertex_id = current_id;

        route_distances := array_append(
            route_distances,
            current_distance
        );

        EXIT WHEN current_id = source_id;

        IF previous_id IS NULL THEN
            RAISE EXCEPTION
                'Invalid predecessor chain';
        END IF;

        current_id := previous_id;
    END LOOP;

    FOR i IN REVERSE step_count..1 LOOP
        RETURN QUERY
        SELECT
            step_count - i + 1,
            v.vertex_name,
            route_distances[i]
        FROM vertex v
        WHERE v.graph_id = p_graph_id
          AND v.vertex_id = route_ids[i];
    END LOOP;
END;
$$;

-- ------------------------------------------------------------
-- 7. SAMPLE GRAPH
-- ------------------------------------------------------------

INSERT INTO graph (
    graph_name,
    graph_type,
    description
)
VALUES (
    'Indian Transport Network',
    'UNDIRECTED',
    'Weighted transport connections between Indian cities'
);

INSERT INTO vertex (
    graph_id,
    vertex_name
)
SELECT
    1,
    city
FROM unnest(ARRAY[
    'Delhi',
    'Agra',
    'Jaipur',
    'Lucknow',
    'Varanasi',
    'Patna',
    'Kolkata',
    'Ahmedabad',
    'Mumbai',
    'Pune',
    'Chennai'
]) AS city;

-- ------------------------------------------------------------
-- 8. TRANSACTIONAL EDGE INSERTION
-- ------------------------------------------------------------

BEGIN;

CALL add_edge(1, 'Delhi', 'Agra', 230);
CALL add_edge(1, 'Delhi', 'Jaipur', 280);
CALL add_edge(1, 'Delhi', 'Lucknow', 550);
CALL add_edge(1, 'Agra', 'Lucknow', 330);
CALL add_edge(1, 'Agra', 'Jaipur', 240);
CALL add_edge(1, 'Jaipur', 'Ahmedabad', 660);
CALL add_edge(1, 'Lucknow', 'Varanasi', 320);
CALL add_edge(1, 'Lucknow', 'Patna', 540);
CALL add_edge(1, 'Varanasi', 'Patna', 250);
CALL add_edge(1, 'Patna', 'Kolkata', 580);
CALL add_edge(1, 'Ahmedabad', 'Mumbai', 530);
CALL add_edge(1, 'Mumbai', 'Pune', 150);
CALL add_edge(1, 'Kolkata', 'Mumbai', 1900);

COMMIT;

-- ------------------------------------------------------------
-- 9. GRAPH VALIDATION VIEW
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW graph_statistics AS
SELECT
    g.graph_id,
    g.graph_name,
    g.graph_type,
    COUNT(DISTINCT v.vertex_id) FILTER (
        WHERE v.is_active
    ) AS active_vertices,
    COUNT(DISTINCT e.edge_id) FILTER (
        WHERE e.is_active
    ) AS active_edges,
    MIN(e.weight) FILTER (
        WHERE e.is_active
    ) AS minimum_weight,
    MAX(e.weight) FILTER (
        WHERE e.is_active
    ) AS maximum_weight,
    AVG(e.weight) FILTER (
        WHERE e.is_active
    ) AS average_weight
FROM graph g
LEFT JOIN vertex v
    ON v.graph_id = g.graph_id
LEFT JOIN edge e
    ON e.graph_id = g.graph_id
GROUP BY
    g.graph_id,
    g.graph_name,
    g.graph_type;

-- ------------------------------------------------------------
-- 10. ROUTE EXECUTION PROCEDURE
-- ------------------------------------------------------------

CREATE OR REPLACE PROCEDURE execute_route(
    p_graph_id BIGINT,
    p_source_name VARCHAR,
    p_destination_name VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_source BIGINT;
    v_destination BIGINT;
    v_distance BIGINT;
    v_route BIGINT[];
    v_started TIMESTAMPTZ;
    v_status VARCHAR(20);
BEGIN
    v_started := clock_timestamp();

    SELECT vertex_id
    INTO v_source
    FROM vertex
    WHERE graph_id = p_graph_id
      AND vertex_name = p_source_name
      AND is_active = TRUE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Invalid source vertex';
    END IF;

    SELECT vertex_id
    INTO v_destination
    FROM vertex
    WHERE graph_id = p_graph_id
      AND vertex_name = p_destination_name
      AND is_active = TRUE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Invalid destination vertex';
    END IF;

    CREATE TEMP TABLE IF NOT EXISTS route_result_buffer (
        step_number INTEGER,
        vertex_name VARCHAR(120),
        cumulative_distance BIGINT
    ) ON COMMIT DROP;

    TRUNCATE route_result_buffer;

    INSERT INTO route_result_buffer
    SELECT *
    FROM shortest_path(
        p_graph_id,
        p_source_name,
        p_destination_name
    );

    IF NOT EXISTS (
        SELECT 1
        FROM route_result_buffer
    ) THEN
        v_status := 'UNREACHABLE';
        v_distance := NULL;
        v_route := ARRAY[]::BIGINT[];
    ELSE
        v_status := 'COMPLETED';

        SELECT cumulative_distance
        INTO v_distance
        FROM route_result_buffer
        ORDER BY step_number DESC
        LIMIT 1;

        SELECT array_agg(v.vertex_id ORDER BY b.step_number)
        INTO v_route
        FROM route_result_buffer b
        JOIN vertex v
          ON v.graph_id = p_graph_id
         AND v.vertex_name = b.vertex_name;
    END IF;

    INSERT INTO route_execution (
        graph_id,
        source_vertex_id,
        destination_vertex_id,
        execution_status,
        total_distance,
        route_vertex_ids,
        execution_duration_ms
    )
    VALUES (
        p_graph_id,
        v_source,
        v_destination,
        v_status,
        v_distance,
        COALESCE(v_route, ARRAY[]::BIGINT[]),
        EXTRACT(
            EPOCH FROM clock_timestamp() - v_started
        ) * 1000
    );
END;
$$;

-- ------------------------------------------------------------
-- 11. EXECUTION EXAMPLES
-- ------------------------------------------------------------

-- Retrieve all shortest distances from Delhi.
SELECT
    vertex_name,
    shortest_distance,
    predecessor_name
FROM dijkstra(1, 'Delhi');

-- Retrieve the exact Delhi-to-Mumbai route.
SELECT *
FROM shortest_path(1, 'Delhi', 'Mumbai');

-- Execute and record a route calculation.
CALL execute_route(1, 'Delhi', 'Mumbai');

-- Retrieve execution history.
SELECT
    execution_id,
    execution_status,
    total_distance,
    executed_at,
    execution_duration_ms
FROM route_execution
ORDER BY executed_at DESC;

-- Graph-level statistics.
SELECT *
FROM graph_statistics;

-- Detect vertices without active connections.
SELECT
    v.vertex_name
FROM vertex v
WHERE v.graph_id = 1
  AND v.is_active = TRUE
  AND NOT EXISTS (
      SELECT 1
      FROM edge e
      WHERE e.graph_id = v.graph_id
        AND e.is_active = TRUE
        AND (
            e.source_vertex_id = v.vertex_id
            OR e.destination_vertex_id = v.vertex_id
        )
  );

-- Verify that no active edge contains a negative weight.
SELECT COUNT(*) AS invalid_negative_edges
FROM edge
WHERE graph_id = 1
  AND is_active = TRUE
  AND weight < 0;

-- ------------------------------------------------------------
-- 12. FAILURE CASE VALIDATION
-- ------------------------------------------------------------

-- This statement must fail and is intentionally isolated.
DO $$
BEGIN
    BEGIN
        CALL add_edge(1, 'Delhi', 'Agra', -10);

        RAISE EXCEPTION
            'Negative weight validation did not execute';
    EXCEPTION
        WHEN OTHERS THEN
            IF SQLERRM =
                'Negative weight validation did not execute' THEN
                RAISE;
            END IF;

            RAISE NOTICE
                'Expected invalid-weight rejection: %',
                SQLERRM;
    END;
END;
$$;

-- Unknown source validation.
DO $$
BEGIN
    BEGIN
        PERFORM *
        FROM dijkstra(1, 'Unknown City');

        RAISE EXCEPTION
            'Unknown vertex validation did not execute';
    EXCEPTION
        WHEN OTHERS THEN
            IF SQLERRM =
                'Unknown vertex validation did not execute' THEN
                RAISE;
            END IF;

            RAISE NOTICE
                'Expected unknown-source rejection: %',
                SQLERRM;
    END;
END;
$$;

-- Unreachable destination test.
CALL execute_route(1, 'Delhi', 'Chennai');

SELECT
    execution_status,
    total_distance
FROM route_execution
WHERE destination_vertex_id = (
    SELECT vertex_id
    FROM vertex
    WHERE graph_id = 1
      AND vertex_name = 'Chennai'
);

-- ------------------------------------------------------------
-- 13. PERFORMANCE AND QUERY PLAN
-- ------------------------------------------------------------

EXPLAIN ANALYZE
SELECT *
FROM edge
WHERE graph_id = 1
  AND source_vertex_id = (
      SELECT vertex_id
      FROM vertex
      WHERE graph_id = 1
        AND vertex_name = 'Delhi'
  )
  AND is_active = TRUE;

-- The SQL array implementation is intended for learning,
-- moderate graph sizes, and database-resident route analysis.
--
-- Its minimum-selection loop is O(V^2), with edge relaxation
-- contributing O(E). A binary heap implementation is preferable
-- for large sparse graphs.
--
-- The database constraints prevent negative weights, cross-graph
-- edges, duplicate directed edges, and invalid vertex references.
-- ============================================================
