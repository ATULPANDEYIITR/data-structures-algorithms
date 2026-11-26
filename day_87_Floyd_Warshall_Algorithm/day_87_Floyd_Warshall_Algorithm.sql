-- ============================================================
-- FLOYD-WARSHALL ALGORITHM
-- PostgreSQL All-Pairs Shortest-Path Database
-- ============================================================
--
-- Models:
--   Graphs
--   Vertices
--   Weighted directed edges
--   Shortest-path computations
--   All-pairs distances
--   Path reconstruction
--   Negative-cycle detection
--   Computation history
--
-- PostgreSQL 15+
--
-- Edge weights may be negative.
-- Negative cycles invalidate shortest-path results.
-- Parallel edges are supported.
--
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS graph;

CREATE TABLE IF NOT EXISTS graph.networks (
    graph_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_name VARCHAR(150) NOT NULL UNIQUE,
    description TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (length(trim(graph_name)) > 0)
);

CREATE TABLE IF NOT EXISTS graph.vertices (
    vertex_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_id BIGINT NOT NULL
        REFERENCES graph.networks(graph_id) ON DELETE CASCADE,
    vertex_code VARCHAR(80) NOT NULL,
    vertex_name VARCHAR(150) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (graph_id, vertex_code),
    CHECK (length(trim(vertex_code)) > 0),
    CHECK (length(trim(vertex_name)) > 0)
);

CREATE TABLE IF NOT EXISTS graph.edges (
    edge_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_id BIGINT NOT NULL,
    source_vertex_id BIGINT NOT NULL,
    destination_vertex_id BIGINT NOT NULL,
    weight NUMERIC(18,4) NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (graph_id)
        REFERENCES graph.networks(graph_id) ON DELETE CASCADE,

    FOREIGN KEY (graph_id, source_vertex_id)
        REFERENCES graph.vertices(graph_id, vertex_id),

    FOREIGN KEY (graph_id, destination_vertex_id)
        REFERENCES graph.vertices(graph_id, vertex_id),

    CHECK (
        source_vertex_id <> destination_vertex_id
        OR weight >= 0
    )
);

CREATE TABLE IF NOT EXISTS graph.computations (
    computation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_id BIGINT NOT NULL
        REFERENCES graph.networks(graph_id) ON DELETE CASCADE,

    algorithm VARCHAR(50) NOT NULL DEFAULT 'FLOYD_WARSHALL',

    status VARCHAR(30) NOT NULL DEFAULT 'PENDING',

    vertex_count INTEGER NOT NULL DEFAULT 0,
    edge_count INTEGER NOT NULL DEFAULT 0,

    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,

    error_message TEXT,

    CHECK (algorithm = 'FLOYD_WARSHALL'),

    CHECK (
        status IN (
            'PENDING',
            'RUNNING',
            'COMPLETED',
            'NEGATIVE_CYCLE',
            'FAILED'
        )
    ),

    CHECK (vertex_count >= 0),
    CHECK (edge_count >= 0),

    CHECK (
        completed_at IS NULL
        OR completed_at >= started_at
    )
);

CREATE TABLE IF NOT EXISTS graph.shortest_paths (
    computation_id BIGINT NOT NULL
        REFERENCES graph.computations(computation_id)
        ON DELETE CASCADE,

    source_vertex_id BIGINT NOT NULL
        REFERENCES graph.vertices(vertex_id),

    destination_vertex_id BIGINT NOT NULL
        REFERENCES graph.vertices(vertex_id),

    distance NUMERIC(30,4) NOT NULL,

    path_vertex_ids BIGINT[] NOT NULL DEFAULT '{}',

    PRIMARY KEY (
        computation_id,
        source_vertex_id,
        destination_vertex_id
    ),

    CHECK (distance >= 0 OR array_length(path_vertex_ids, 1) >= 1)
);

-- Indexes for graph traversal and reporting.
CREATE INDEX IF NOT EXISTS idx_vertices_graph
    ON graph.vertices(graph_id);

CREATE INDEX IF NOT EXISTS idx_edges_source
    ON graph.edges(graph_id, source_vertex_id)
    WHERE enabled = TRUE;

CREATE INDEX IF NOT EXISTS idx_edges_destination
    ON graph.edges(graph_id, destination_vertex_id)
    WHERE enabled = TRUE;

CREATE INDEX IF NOT EXISTS idx_edges_weight
    ON graph.edges(graph_id, weight);

CREATE INDEX IF NOT EXISTS idx_computations_graph_status
    ON graph.computations(graph_id, status, started_at DESC);

CREATE INDEX IF NOT EXISTS idx_shortest_paths_destination
    ON graph.shortest_paths(
        computation_id,
        destination_vertex_id
    );

-- ============================================================
-- INTEGRITY TRIGGER
-- ============================================================

CREATE OR REPLACE FUNCTION graph.validate_edge_graph()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM graph.vertices v
        WHERE v.vertex_id = NEW.source_vertex_id
          AND v.graph_id = NEW.graph_id
    ) THEN
        RAISE EXCEPTION
            'Source vertex does not belong to graph %',
            NEW.graph_id;
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM graph.vertices v
        WHERE v.vertex_id = NEW.destination_vertex_id
          AND v.graph_id = NEW.graph_id
    ) THEN
        RAISE EXCEPTION
            'Destination vertex does not belong to graph %',
            NEW.graph_id;
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validate_edge_graph
ON graph.edges;

CREATE TRIGGER trg_validate_edge_graph
BEFORE INSERT OR UPDATE ON graph.edges
FOR EACH ROW
EXECUTE FUNCTION graph.validate_edge_graph();

-- ============================================================
-- SAMPLE NETWORK
-- ============================================================

INSERT INTO graph.networks (
    graph_name,
    description
)
VALUES (
    'Indian_City_Routing',
    'Directed weighted network for all-pairs shortest-path analysis'
)
ON CONFLICT (graph_name) DO NOTHING;

INSERT INTO graph.vertices (
    graph_id,
    vertex_code,
    vertex_name
)
SELECT
    n.graph_id,
    v.vertex_code,
    v.vertex_name
FROM graph.networks n
CROSS JOIN (
    VALUES
        ('DEL', 'Delhi'),
        ('AGR', 'Agra'),
        ('JAI', 'Jaipur'),
        ('LKO', 'Lucknow'),
        ('KNP', 'Kanpur'),
        ('MUM', 'Mumbai')
) AS v(vertex_code, vertex_name)
WHERE n.graph_name = 'Indian_City_Routing'
ON CONFLICT (graph_id, vertex_code) DO NOTHING;

-- Direct edge distances.
INSERT INTO graph.edges (
    graph_id,
    source_vertex_id,
    destination_vertex_id,
    weight
)
SELECT
    n.graph_id,
    source.vertex_id,
    destination.vertex_id,
    route.weight
FROM graph.networks n
JOIN (
    VALUES
        ('DEL', 'AGR', 2.0::NUMERIC),
        ('DEL', 'JAI', 5.0::NUMERIC),
        ('AGR', 'JAI', 1.0::NUMERIC),
        ('AGR', 'LKO', 4.0::NUMERIC),
        ('JAI', 'LKO', 2.0::NUMERIC),
        ('LKO', 'KNP', 1.0::NUMERIC),
        ('KNP', 'MUM', 8.0::NUMERIC),
        ('JAI', 'MUM', 12.0::NUMERIC),
        ('DEL', 'KNP', 15.0::NUMERIC)
) AS route(source_code, destination_code, weight)
    ON TRUE
JOIN graph.vertices source
    ON source.graph_id = n.graph_id
   AND source.vertex_code = route.source_code
JOIN graph.vertices destination
    ON destination.graph_id = n.graph_id
   AND destination.vertex_code = route.destination_code
WHERE n.graph_name = 'Indian_City_Routing'
AND NOT EXISTS (
    SELECT 1
    FROM graph.edges existing
    WHERE existing.graph_id = n.graph_id
      AND existing.source_vertex_id = source.vertex_id
      AND existing.destination_vertex_id = destination.vertex_id
      AND existing.weight = route.weight
);

-- ============================================================
-- ALL-PAIRS SHORTEST-PATH COMPUTATION
-- ============================================================

CREATE OR REPLACE FUNCTION graph.compute_floyd_warshall(
    p_graph_id BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_computation_id BIGINT;
    v_vertex_count INTEGER;
    v_edge_count INTEGER;
    v_k BIGINT;
    v_negative_cycle BOOLEAN;
BEGIN
    -- Validate the requested graph.
    IF NOT EXISTS (
        SELECT 1
        FROM graph.networks
        WHERE graph_id = p_graph_id
    ) THEN
        RAISE EXCEPTION 'Graph % does not exist', p_graph_id;
    END IF;

    SELECT COUNT(*)
    INTO v_vertex_count
    FROM graph.vertices
    WHERE graph_id = p_graph_id;

    SELECT COUNT(*)
    INTO v_edge_count
    FROM graph.edges
    WHERE graph_id = p_graph_id
      AND enabled = TRUE;

    IF v_vertex_count = 0 THEN
        RAISE EXCEPTION 'Cannot process an empty graph';
    END IF;

    -- Serialize computations on the same graph.
    PERFORM 1
    FROM graph.networks
    WHERE graph_id = p_graph_id
    FOR UPDATE;

    INSERT INTO graph.computations (
        graph_id,
        status,
        vertex_count,
        edge_count
    )
    VALUES (
        p_graph_id,
        'RUNNING',
        v_vertex_count,
        v_edge_count
    )
    RETURNING computation_id
    INTO v_computation_id;

    /*
     * Temporary matrix:
     *
     * distance(i,j) = current shortest known distance.
     * next_hop(i,j) = first vertex after i on the path to j.
     *
     * NULL represents infinity.
     */

    DROP TABLE IF EXISTS pg_temp.fw_matrix;

    CREATE TEMP TABLE fw_matrix (
        source_id BIGINT NOT NULL,
        destination_id BIGINT NOT NULL,
        distance NUMERIC(30,4),
        next_hop BIGINT,
        PRIMARY KEY (source_id, destination_id)
    ) ON COMMIT DROP;

    -- Initialize all vertex pairs.
    INSERT INTO fw_matrix (
        source_id,
        destination_id,
        distance,
        next_hop
    )
    SELECT
        source.vertex_id,
        destination.vertex_id,
        CASE
            WHEN source.vertex_id = destination.vertex_id
                THEN 0
            ELSE NULL
        END,
        CASE
            WHEN source.vertex_id = destination.vertex_id
                THEN source.vertex_id
            ELSE NULL
        END
    FROM graph.vertices source
    CROSS JOIN graph.vertices destination
    WHERE source.graph_id = p_graph_id
      AND destination.graph_id = p_graph_id;

    -- Initialize direct edges.
    -- Parallel edges are reduced to their minimum weight.
    WITH minimum_edges AS (
        SELECT
            source_vertex_id,
            destination_vertex_id,
            MIN(weight) AS weight
        FROM graph.edges
        WHERE graph_id = p_graph_id
          AND enabled = TRUE
        GROUP BY
            source_vertex_id,
            destination_vertex_id
    )
    UPDATE fw_matrix matrix
    SET
        distance = edges.weight,
        next_hop = edges.destination_vertex_id
    FROM minimum_edges edges
    WHERE matrix.source_id = edges.source_vertex_id
      AND matrix.destination_id = edges.destination_vertex_id
      AND edges.weight < COALESCE(
          matrix.distance,
          'Infinity'::NUMERIC
      );

    /*
     * Floyd-Warshall recurrence:
     *
     * D(i,j) = MIN(
     *     D(i,j),
     *     D(i,k) + D(k,j)
     * )
     *
     * The intermediate vertex k is processed sequentially.
     */

    FOR v_k IN
        SELECT vertex_id
        FROM graph.vertices
        WHERE graph_id = p_graph_id
        ORDER BY vertex_id
    LOOP

        UPDATE fw_matrix AS current
        SET
            distance = left_path.distance + right_path.distance,
            next_hop = left_path.next_hop

        FROM fw_matrix AS left_path,
             fw_matrix AS right_path

        WHERE left_path.source_id = current.source_id
          AND left_path.destination_id = v_k

          AND right_path.source_id = v_k
          AND right_path.destination_id = current.destination_id

          AND left_path.distance IS NOT NULL
          AND right_path.distance IS NOT NULL

          AND (
              current.distance IS NULL
              OR left_path.distance + right_path.distance
                 < current.distance
          );

    END LOOP;

    -- Negative diagonal means the graph has a negative cycle.
    SELECT EXISTS (
        SELECT 1
        FROM fw_matrix
        WHERE source_id = destination_id
          AND distance < 0
    )
    INTO v_negative_cycle;

    IF v_negative_cycle THEN

        UPDATE graph.computations
        SET
            status = 'NEGATIVE_CYCLE',
            completed_at = CURRENT_TIMESTAMP,
            error_message = 'Negative-weight cycle detected'
        WHERE computation_id = v_computation_id;

        RETURN v_computation_id;
    END IF;

    /*
     * Reconstruct paths using next_hop.
     * A simple shortest path contains at most V vertices.
     */

    INSERT INTO graph.shortest_paths (
        computation_id,
        source_vertex_id,
        destination_vertex_id,
        distance,
        path_vertex_ids
    )
    SELECT
        v_computation_id,
        source_id,
        destination_id,
        distance,
        ARRAY[source_id]::BIGINT[]
    FROM fw_matrix
    WHERE source_id = destination_id
      AND distance IS NOT NULL;

    -- Store reachable non-self paths.
    DECLARE
        v_source BIGINT;
        v_destination BIGINT;
        v_current BIGINT;
        v_next BIGINT;
        v_path BIGINT[];
        v_step INTEGER;
        v_distance NUMERIC(30,4);
    BEGIN
        FOR v_source, v_destination, v_distance IN
            SELECT source_id, destination_id, distance
            FROM fw_matrix
            WHERE source_id <> destination_id
              AND distance IS NOT NULL
        LOOP

            v_current := v_source;
            v_path := ARRAY[v_source]::BIGINT[];
            v_step := 0;

            WHILE v_current <> v_destination LOOP

                SELECT next_hop
                INTO v_next
                FROM fw_matrix
                WHERE source_id = v_current
                  AND destination_id = v_destination;

                IF v_next IS NULL THEN
                    RAISE EXCEPTION
                        'Path reconstruction failed for % -> %',
                        v_source,
                        v_destination;
                END IF;

                v_current := v_next;
                v_path := array_append(v_path, v_current);

                v_step := v_step + 1;

                IF v_step > v_vertex_count THEN
                    RAISE EXCEPTION
                        'Path reconstruction exceeded vertex count';
                END IF;

            END LOOP;

            INSERT INTO graph.shortest_paths (
                computation_id,
                source_vertex_id,
                destination_vertex_id,
                distance,
                path_vertex_ids
            )
            VALUES (
                v_computation_id,
                v_source,
                v_destination,
                v_distance,
                v_path
            );

        END LOOP;
    END;

    UPDATE graph.computations
    SET
        status = 'COMPLETED',
        completed_at = CURRENT_TIMESTAMP
    WHERE computation_id = v_computation_id;

    RETURN v_computation_id;

EXCEPTION
    WHEN OTHERS THEN

        IF v_computation_id IS NOT NULL THEN
            UPDATE graph.computations
            SET
                status = 'FAILED',
                completed_at = CURRENT_TIMESTAMP,
                error_message = SQLERRM
            WHERE computation_id = v_computation_id;
        END IF;

        RAISE;
END;
$$;

-- ============================================================
-- EXECUTE COMPUTATION
-- ============================================================

DO $$
DECLARE
    v_graph_id BIGINT;
    v_computation_id BIGINT;
BEGIN
    SELECT graph_id
    INTO v_graph_id
    FROM graph.networks
    WHERE graph_name = 'Indian_City_Routing';

    v_computation_id :=
        graph.compute_floyd_warshall(v_graph_id);

    RAISE NOTICE 'Computation ID: %', v_computation_id;
END;
$$;

-- ============================================================
-- REPORTING VIEWS
-- ============================================================

CREATE OR REPLACE VIEW graph.computation_summary AS
SELECT
    c.computation_id,
    n.graph_name,
    c.algorithm,
    c.status,
    c.vertex_count,
    c.edge_count,
    c.started_at,
    c.completed_at,
    c.error_message
FROM graph.computations c
JOIN graph.networks n
    ON n.graph_id = c.graph_id;

CREATE OR REPLACE VIEW graph.latest_completed_computations AS
SELECT DISTINCT ON (graph_id)
    computation_id,
    graph_id,
    status,
    vertex_count,
    edge_count,
    completed_at
FROM graph.computations
WHERE status = 'COMPLETED'
ORDER BY graph_id, completed_at DESC, computation_id DESC;

-- ============================================================
-- QUERY 1: GRAPH RETRIEVAL
-- ============================================================

SELECT
    n.graph_name,
    v.vertex_code,
    v.vertex_name
FROM graph.networks n
JOIN graph.vertices v
    ON v.graph_id = n.graph_id
WHERE n.graph_name = 'Indian_City_Routing'
ORDER BY v.vertex_code;

-- ============================================================
-- QUERY 2: DIRECT EDGE RETRIEVAL
-- ============================================================

SELECT
    source.vertex_name AS source,
    destination.vertex_name AS destination,
    e.weight
FROM graph.edges e
JOIN graph.vertices source
    ON source.vertex_id = e.source_vertex_id
JOIN graph.vertices destination
    ON destination.vertex_id = e.destination_vertex_id
WHERE e.enabled = TRUE
ORDER BY source.vertex_name, destination.vertex_name;

-- ============================================================
-- QUERY 3: ALL-PAIRS SHORTEST-DISTANCE REPORT
-- ============================================================

SELECT
    c.computation_id,
    source.vertex_name AS source,
    destination.vertex_name AS destination,
    sp.distance
FROM graph.shortest_paths sp
JOIN graph.computations c
    ON c.computation_id = sp.computation_id
JOIN graph.vertices source
    ON source.vertex_id = sp.source_vertex_id
JOIN graph.vertices destination
    ON destination.vertex_id = sp.destination_vertex_id
WHERE c.status = 'COMPLETED'
ORDER BY
    c.computation_id,
    source.vertex_name,
    destination.vertex_name;

-- ============================================================
-- QUERY 4: PATH RECONSTRUCTION
-- ============================================================

SELECT
    source.vertex_name AS source,
    destination.vertex_name AS destination,
    sp.distance,
    array_to_string(
        ARRAY(
            SELECT v.vertex_name
            FROM unnest(sp.path_vertex_ids)
                 WITH ORDINALITY AS p(vertex_id, position)
            JOIN graph.vertices v
                ON v.vertex_id = p.vertex_id
            ORDER BY p.position
        ),
        ' -> '
    ) AS reconstructed_path
FROM graph.shortest_paths sp
JOIN graph.vertices source
    ON source.vertex_id = sp.source_vertex_id
JOIN graph.vertices destination
    ON destination.vertex_id = sp.destination_vertex_id
WHERE sp.computation_id = (
    SELECT computation_id
    FROM graph.computations
    WHERE graph_id = (
        SELECT graph_id
        FROM graph.networks
        WHERE graph_name = 'Indian_City_Routing'
    )
    AND status = 'COMPLETED'
    ORDER BY computation_id DESC
    LIMIT 1
)
ORDER BY source.vertex_name, destination.vertex_name;

-- ============================================================
-- QUERY 5: AGGREGATION
-- ============================================================

SELECT
    c.computation_id,
    COUNT(*) AS reachable_pairs,
    MIN(sp.distance) AS minimum_distance,
    MAX(sp.distance) AS maximum_distance,
    AVG(sp.distance) AS average_distance
FROM graph.shortest_paths sp
JOIN graph.computations c
    ON c.computation_id = sp.computation_id
WHERE c.status = 'COMPLETED'
GROUP BY c.computation_id
ORDER BY c.computation_id;

-- ============================================================
-- QUERY 6: UNREACHABLE PAIRS
-- ============================================================

SELECT
    source.vertex_name AS source,
    destination.vertex_name AS destination
FROM graph.vertices source
CROSS JOIN graph.vertices destination
WHERE source.graph_id = (
    SELECT graph_id
    FROM graph.networks
    WHERE graph_name = 'Indian_City_Routing'
)
AND destination.graph_id = source.graph_id
AND NOT EXISTS (
    SELECT 1
    FROM graph.shortest_paths sp
    JOIN graph.computations c
        ON c.computation_id = sp.computation_id
    WHERE sp.source_vertex_id = source.vertex_id
      AND sp.destination_vertex_id = destination.vertex_id
      AND c.status = 'COMPLETED'
      AND c.computation_id = (
          SELECT MAX(computation_id)
          FROM graph.computations
          WHERE graph_id = source.graph_id
            AND status = 'COMPLETED'
      )
)
ORDER BY source.vertex_name, destination.vertex_name;

-- ============================================================
-- QUERY 7: COMPUTATION PERFORMANCE REPORT
-- ============================================================

SELECT
    graph_name,
    computation_id,
    status,
    vertex_count,
    edge_count,
    completed_at - started_at AS execution_duration,
    error_message
FROM graph.computation_summary
ORDER BY computation_id DESC;

-- ============================================================
-- QUERY 8: NEGATIVE EDGE VALIDATION
-- ============================================================

SELECT
    source.vertex_name AS source,
    destination.vertex_name AS destination,
    e.weight
FROM graph.edges e
JOIN graph.vertices source
    ON source.vertex_id = e.source_vertex_id
JOIN graph.vertices destination
    ON destination.vertex_id = e.destination_vertex_id
WHERE e.weight < 0
  AND e.enabled = TRUE;

-- ============================================================
-- QUERY 9: TRANSACTIONAL EDGE UPDATE
-- ============================================================

-- This example updates an existing direct connection.
-- A new computation must be performed after graph changes.

DO $$
DECLARE
    v_graph_id BIGINT;
    v_source BIGINT;
    v_destination BIGINT;
BEGIN
    SELECT graph_id
    INTO v_graph_id
    FROM graph.networks
    WHERE graph_name = 'Indian_City_Routing';

    SELECT vertex_id
    INTO v_source
    FROM graph.vertices
    WHERE graph_id = v_graph_id
      AND vertex_code = 'DEL';

    SELECT vertex_id
    INTO v_destination
    FROM graph.vertices
    WHERE graph_id = v_graph_id
      AND vertex_code = 'MUM';

    INSERT INTO graph.edges (
        graph_id,
        source_vertex_id,
        destination_vertex_id,
        weight
    )
    VALUES (
        v_graph_id,
        v_source,
        v_destination,
        3
    );

END;
$$;

COMMIT;
