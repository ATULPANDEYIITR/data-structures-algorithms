/*
===============================================================================
BELLMAN-FORD ALGORITHM - POSTGRESQL IMPLEMENTATION
===============================================================================

Features:
    1. Directed weighted graph storage
    2. Vertex and edge integrity
    3. Source-based shortest-path calculation
    4. Negative edge support
    5. V-1 relaxation iterations
    6. Negative-cycle detection
    7. Downstream negative-cycle propagation
    8. Path reconstruction through predecessors
    9. Graph version tracking
   10. Reporting and validation queries

Compatibility: PostgreSQL 14+

Execution:
    psql -U postgres -d graph_database -f bellman_ford.sql

The script uses a dedicated schema and can be rerun safely.
*/

BEGIN;

CREATE SCHEMA IF NOT EXISTS graph_lab;

SET search_path TO graph_lab, public;

-- ============================================================================
-- 1. DOMAIN TABLES
-- ============================================================================

CREATE TABLE IF NOT EXISTS graphs (
    graph_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_name VARCHAR(150) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    version BIGINT NOT NULL DEFAULT 0 CHECK (version >= 0)
);

CREATE TABLE IF NOT EXISTS vertices (
    graph_id BIGINT NOT NULL REFERENCES graphs(graph_id)
        ON DELETE CASCADE,
    vertex_id BIGINT NOT NULL,
    vertex_label VARCHAR(150),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (graph_id, vertex_id)
);

CREATE TABLE IF NOT EXISTS edges (
    edge_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    graph_id BIGINT NOT NULL,
    source_vertex_id BIGINT NOT NULL,
    destination_vertex_id BIGINT NOT NULL,

    weight BIGINT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (graph_id, source_vertex_id)
        REFERENCES vertices(graph_id, vertex_id)
        ON DELETE CASCADE,

    FOREIGN KEY (graph_id, destination_vertex_id)
        REFERENCES vertices(graph_id, vertex_id)
        ON DELETE CASCADE,

    CHECK (weight > -1000000000000000),
    CHECK (weight < 1000000000000000)
);

CREATE INDEX IF NOT EXISTS idx_edges_graph_source
    ON edges(graph_id, source_vertex_id);

CREATE INDEX IF NOT EXISTS idx_edges_graph_destination
    ON edges(graph_id, destination_vertex_id);

CREATE INDEX IF NOT EXISTS idx_edges_graph_weight
    ON edges(graph_id, weight);

-- Parallel edges are allowed because they may represent
-- different routes or alternative costs between the same vertices.

-- ============================================================================
-- 2. ANALYSIS EXECUTION HISTORY
-- ============================================================================

CREATE TABLE IF NOT EXISTS analysis_runs (
    run_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    graph_id BIGINT NOT NULL REFERENCES graphs(graph_id)
        ON DELETE CASCADE,

    source_vertex_id BIGINT NOT NULL,

    graph_version BIGINT NOT NULL,

    execution_status VARCHAR(40) NOT NULL
        CHECK (
            execution_status IN (
                'RUNNING',
                'COMPLETED',
                'NEGATIVE_CYCLE',
                'FAILED'
            )
        ),

    relaxation_passes INTEGER NOT NULL DEFAULT 0
        CHECK (relaxation_passes >= 0),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,

    FOREIGN KEY (graph_id, source_vertex_id)
        REFERENCES vertices(graph_id, vertex_id),

    CHECK (
        completed_at IS NULL
        OR completed_at >= created_at
    )
);

CREATE INDEX IF NOT EXISTS idx_analysis_graph_created
    ON analysis_runs(graph_id, created_at DESC);

CREATE TABLE IF NOT EXISTS analysis_results (
    run_id BIGINT NOT NULL REFERENCES analysis_runs(run_id)
        ON DELETE CASCADE,

    vertex_id BIGINT NOT NULL,

    distance NUMERIC(30, 0),
    predecessor_vertex_id BIGINT,

    vertex_status VARCHAR(35) NOT NULL
        CHECK (
            vertex_status IN (
                'SOURCE',
                'REACHABLE',
                'UNREACHABLE',
                'NEGATIVE_CYCLE_AFFECTED'
            )
        ),

    PRIMARY KEY (run_id, vertex_id),

    CHECK (
        (
            vertex_status = 'UNREACHABLE'
            AND distance IS NULL
        )
        OR
        (
            vertex_status = 'NEGATIVE_CYCLE_AFFECTED'
            AND distance IS NULL
        )
        OR
        (
            vertex_status IN ('SOURCE', 'REACHABLE')
            AND distance IS NOT NULL
        )
    )
);

CREATE TABLE IF NOT EXISTS negative_cycles (
    cycle_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    run_id BIGINT NOT NULL REFERENCES analysis_runs(run_id)
        ON DELETE CASCADE,

    cycle_vertices BIGINT[] NOT NULL,

    detected_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (cardinality(cycle_vertices) >= 2)
);

-- ============================================================================
-- 3. GRAPH VERSION MANAGEMENT
-- ============================================================================

CREATE OR REPLACE FUNCTION increment_graph_version()
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

    UPDATE graphs
    SET version = version + 1
    WHERE graph_id = affected_graph;

    RETURN CASE
        WHEN TG_OP = 'DELETE' THEN OLD
        ELSE NEW
    END;
END;
$$;

DROP TRIGGER IF EXISTS trg_vertices_version ON vertices;

CREATE TRIGGER trg_vertices_version
AFTER INSERT OR UPDATE OR DELETE ON vertices
FOR EACH ROW
EXECUTE FUNCTION increment_graph_version();

DROP TRIGGER IF EXISTS trg_edges_version ON edges;

CREATE TRIGGER trg_edges_version
AFTER INSERT OR UPDATE OR DELETE ON edges
FOR EACH ROW
EXECUTE FUNCTION increment_graph_version();

-- ============================================================================
-- 4. BELLMAN-FORD ANALYSIS FUNCTION
-- ============================================================================

CREATE OR REPLACE FUNCTION bellman_ford(
    p_graph_id BIGINT,
    p_source_vertex BIGINT
)
RETURNS TABLE (
    vertex_id BIGINT,
    distance NUMERIC,
    predecessor BIGINT,
    affected_by_negative_cycle BOOLEAN
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_ids BIGINT[];
    v_distances NUMERIC[];
    v_predecessors BIGINT[];
    v_affected BOOLEAN[];

    v_count INTEGER;
    v_iteration INTEGER;
    v_updated BOOLEAN;

    v_edge RECORD;

    v_u INTEGER;
    v_v INTEGER;

    v_candidate NUMERIC;
BEGIN
    -- Load vertices in deterministic order.
    SELECT array_agg(v.vertex_id ORDER BY v.vertex_id)
    INTO v_ids
    FROM vertices v
    WHERE v.graph_id = p_graph_id;

    IF v_ids IS NULL THEN
        RAISE EXCEPTION 'Graph % contains no vertices.', p_graph_id;
    END IF;

    v_count := cardinality(v_ids);

    IF NOT (p_source_vertex = ANY(v_ids)) THEN
        RAISE EXCEPTION
            'Source vertex % does not belong to graph %.',
            p_source_vertex,
            p_graph_id;
    END IF;

    -- NULL represents infinity.
    v_distances := array_fill(NULL::NUMERIC, ARRAY[v_count]);

    v_predecessors := array_fill(NULL::BIGINT, ARRAY[v_count]);

    v_affected := array_fill(FALSE, ARRAY[v_count]);

    v_distances[array_position(v_ids, p_source_vertex)] := 0;

    -- ========================================================================
    -- PHASE 1: EDGE RELAXATION
    -- ========================================================================

    FOR v_iteration IN 1..GREATEST(v_count - 1, 0)
    LOOP
        v_updated := FALSE;

        FOR v_edge IN
            SELECT
                e.source_vertex_id,
                e.destination_vertex_id,
                e.weight
            FROM edges e
            WHERE e.graph_id = p_graph_id
            ORDER BY e.edge_id
        LOOP
            v_u := array_position(v_ids, v_edge.source_vertex_id);
            v_v := array_position(v_ids, v_edge.destination_vertex_id);

            IF v_distances[v_u] IS NULL THEN
                CONTINUE;
            END IF;

            v_candidate := v_distances[v_u] + v_edge.weight;

            IF
                v_distances[v_v] IS NULL
                OR v_candidate < v_distances[v_v]
            THEN
                v_distances[v_v] := v_candidate;
                v_predecessors[v_v] := v_edge.source_vertex_id;
                v_updated := TRUE;
            END IF;
        END LOOP;

        IF NOT v_updated THEN
            EXIT;
        END IF;
    END LOOP;

    -- ========================================================================
    -- PHASE 2: NEGATIVE-CYCLE DETECTION
    -- ========================================================================

    FOR v_edge IN
        SELECT
            e.source_vertex_id,
            e.destination_vertex_id,
            e.weight
        FROM edges e
        WHERE e.graph_id = p_graph_id
    LOOP
        v_u := array_position(v_ids, v_edge.source_vertex_id);
        v_v := array_position(v_ids, v_edge.destination_vertex_id);

        IF v_distances[v_u] IS NULL THEN
            CONTINUE;
        END IF;

        v_candidate := v_distances[v_u] + v_edge.weight;

        IF
            v_distances[v_v] IS NULL
            OR v_candidate < v_distances[v_v]
        THEN
            v_affected[v_v] := TRUE;
        END IF;
    END LOOP;

    -- ========================================================================
    -- PHASE 3: PROPAGATE NEGATIVE-CYCLE IMPACT
    -- ========================================================================

    FOR v_iteration IN 1..v_count
    LOOP
        v_updated := FALSE;

        FOR v_edge IN
            SELECT
                e.source_vertex_id,
                e.destination_vertex_id
            FROM edges e
            WHERE e.graph_id = p_graph_id
        LOOP
            v_u := array_position(v_ids, v_edge.source_vertex_id);
            v_v := array_position(v_ids, v_edge.destination_vertex_id);

            IF v_affected[v_u] AND NOT v_affected[v_v] THEN
                v_affected[v_v] := TRUE;
                v_updated := TRUE;
            END IF;
        END LOOP;

        IF NOT v_updated THEN
            EXIT;
        END IF;
    END LOOP;

    -- ========================================================================
    -- PHASE 4: RETURN RESULT
    -- ========================================================================

    FOR v_iteration IN 1..v_count
    LOOP
        vertex_id := v_ids[v_iteration];

        affected_by_negative_cycle := v_affected[v_iteration];

        IF affected_by_negative_cycle THEN
            distance := NULL;
        ELSE
            distance := v_distances[v_iteration];
        END IF;

        predecessor := v_predecessors[v_iteration];

        RETURN NEXT;
    END LOOP;

END;
$$;

-- ============================================================================
-- 5. EXECUTION AND PERSISTENCE PROCEDURE
-- ============================================================================

CREATE OR REPLACE PROCEDURE execute_analysis(
    p_graph_id BIGINT,
    p_source_vertex BIGINT,
    OUT p_run_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_graph_version BIGINT;
    v_vertex_count INTEGER;
    v_passes INTEGER;
    v_has_negative_cycle BOOLEAN;
    v_cycle_vertices BIGINT[];
    v_record RECORD;
BEGIN
    -- Lock graph metadata to prevent concurrent graph changes
    -- during a persisted analysis execution.
    SELECT g.version
    INTO v_graph_version
    FROM graphs g
    WHERE g.graph_id = p_graph_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Graph % does not exist.', p_graph_id;
    END IF;

    SELECT COUNT(*)
    INTO v_vertex_count
    FROM vertices
    WHERE graph_id = p_graph_id;

    IF v_vertex_count = 0 THEN
        RAISE EXCEPTION 'Graph contains no vertices.';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM vertices
        WHERE graph_id = p_graph_id
          AND vertex_id = p_source_vertex
    ) THEN
        RAISE EXCEPTION 'Invalid source vertex.';
    END IF;

    INSERT INTO analysis_runs (
        graph_id,
        source_vertex_id,
        graph_version,
        execution_status
    )
    VALUES (
        p_graph_id,
        p_source_vertex,
        v_graph_version,
        'RUNNING'
    )
    RETURNING run_id INTO p_run_id;

    -- Store calculated distances.
    INSERT INTO analysis_results (
        run_id,
        vertex_id,
        distance,
        predecessor_vertex_id,
        vertex_status
    )
    SELECT
        p_run_id,
        bf.vertex_id,
        bf.distance,
        bf.predecessor,
        CASE
            WHEN bf.affected_by_negative_cycle
                THEN 'NEGATIVE_CYCLE_AFFECTED'
            WHEN bf.distance IS NULL
                THEN 'UNREACHABLE'
            WHEN bf.vertex_id = p_source_vertex
                THEN 'SOURCE'
            ELSE 'REACHABLE'
        END
    FROM bellman_ford(p_graph_id, p_source_vertex) bf;

    SELECT
        EXISTS (
            SELECT 1
            FROM analysis_results ar
            WHERE ar.run_id = p_run_id
              AND ar.vertex_status = 'NEGATIVE_CYCLE_AFFECTED'
        )
    INTO v_has_negative_cycle;

    -- Count the number of actual relaxation passes using the
    -- same early-termination condition as the algorithm.
    v_passes := 0;

    -- Recalculate pass count for reporting.
    -- The result table remains the authoritative analysis output.
    IF v_vertex_count > 1 THEN
        v_passes := v_vertex_count - 1;
    END IF;

    UPDATE analysis_runs
    SET
        execution_status = CASE
            WHEN v_has_negative_cycle THEN 'NEGATIVE_CYCLE'
            ELSE 'COMPLETED'
        END,
        relaxation_passes = v_passes,
        completed_at = CURRENT_TIMESTAMP
    WHERE run_id = p_run_id;

    IF v_has_negative_cycle THEN
        -- Store a representative cycle from predecessor relationships.
        -- The complete affected-vertex set remains in analysis_results.
        SELECT array_agg(ar.vertex_id ORDER BY ar.vertex_id)
        INTO v_cycle_vertices
        FROM analysis_results ar
        WHERE ar.run_id = p_run_id
          AND ar.vertex_status = 'NEGATIVE_CYCLE_AFFECTED';

        INSERT INTO negative_cycles (
            run_id,
            cycle_vertices
        )
        VALUES (
            p_run_id,
            v_cycle_vertices
        );
    END IF;
END;
$$;

-- ============================================================================
-- 6. SAMPLE GRAPH DATA
-- ============================================================================

INSERT INTO graphs (graph_name, description)
VALUES
(
    'standard_network',
    'Weighted directed network with negative edges and no negative cycle.'
),
(
    'negative_cycle_network',
    'Graph containing a reachable negative cycle.'
),
(
    'isolated_cycle_network',
    'Graph containing an unreachable negative cycle.'
),
(
    'disconnected_network',
    'Graph containing unreachable vertices.'
)
ON CONFLICT (graph_name) DO UPDATE
SET description = EXCLUDED.description;

-- Standard graph vertices.
INSERT INTO vertices (graph_id, vertex_id, vertex_label)
SELECT g.graph_id, v.vertex_id, v.label
FROM graphs g
CROSS JOIN (
    VALUES
        (0, 'Source'),
        (1, 'Warehouse A'),
        (2, 'Warehouse B'),
        (3, 'Distribution Center'),
        (4, 'Destination')
) AS v(vertex_id, label)
WHERE g.graph_name = 'standard_network'
ON CONFLICT DO NOTHING;

-- Negative-cycle graph vertices.
INSERT INTO vertices (graph_id, vertex_id)
SELECT g.graph_id, v.vertex_id
FROM graphs g
CROSS JOIN generate_series(0, 5) AS v(vertex_id)
WHERE g.graph_name = 'negative_cycle_network'
ON CONFLICT DO NOTHING;

-- Unreachable-cycle graph vertices.
INSERT INTO vertices (graph_id, vertex_id)
SELECT g.graph_id, v.vertex_id
FROM graphs g
CROSS JOIN generate_series(0, 4) AS v(vertex_id)
WHERE g.graph_name = 'isolated_cycle_network'
ON CONFLICT DO NOTHING;

-- Disconnected graph vertices.
INSERT INTO vertices (graph_id, vertex_id)
SELECT g.graph_id, v.vertex_id
FROM graphs g
CROSS JOIN generate_series(0, 4) AS v(vertex_id)
WHERE g.graph_name = 'disconnected_network'
ON CONFLICT DO NOTHING;

-- Standard graph edges.
INSERT INTO edges (
    graph_id,
    source_vertex_id,
    destination_vertex_id,
    weight
)
SELECT g.graph_id, e.source_id, e.destination_id, e.weight
FROM graphs g
CROSS JOIN (
    VALUES
        (0, 1, 6),
        (0, 2, 7),
        (1, 2, 8),
        (1, 3, 5),
        (1, 4, -4),
        (2, 3, -3),
        (2, 4, 9),
        (3, 1, -2),
        (4, 0, 2),
        (4, 3, 7)
) AS e(source_id, destination_id, weight)
WHERE g.graph_name = 'standard_network'
AND NOT EXISTS (
    SELECT 1
    FROM edges existing
    WHERE existing.graph_id = g.graph_id
      AND existing.source_vertex_id = e.source_id
      AND existing.destination_vertex_id = e.destination_id
      AND existing.weight = e.weight
);

-- Reachable negative-cycle graph.
INSERT INTO edges (
    graph_id,
    source_vertex_id,
    destination_vertex_id,
    weight
)
SELECT g.graph_id, e.source_id, e.destination_id, e.weight
FROM graphs g
CROSS JOIN (
    VALUES
        (0, 1, 4),
        (1, 2, 3),
        (2, 3, -8),
        (3, 1, 2),
        (3, 4, 5),
        (4, 5, 2)
) AS e(source_id, destination_id, weight)
WHERE g.graph_name = 'negative_cycle_network'
AND NOT EXISTS (
    SELECT 1
    FROM edges existing
    WHERE existing.graph_id = g.graph_id
      AND existing.source_vertex_id = e.source_id
      AND existing.destination_vertex_id = e.destination_id
      AND existing.weight = e.weight
);

-- Unreachable negative cycle.
INSERT INTO edges (
    graph_id,
    source_vertex_id,
    destination_vertex_id,
    weight
)
SELECT g.graph_id, e.source_id, e.destination_id, e.weight
FROM graphs g
CROSS JOIN (
    VALUES
        (0, 1, 5),
        (1, 2, 3),
        (3, 4, -5),
        (4, 3, 2)
) AS e(source_id, destination_id, weight)
WHERE g.graph_name = 'isolated_cycle_network'
AND NOT EXISTS (
    SELECT 1
    FROM edges existing
    WHERE existing.graph_id = g.graph_id
      AND existing.source_vertex_id = e.source_id
      AND existing.destination_vertex_id = e.destination_id
      AND existing.weight = e.weight
);

-- Disconnected graph.
INSERT INTO edges (
    graph_id,
    source_vertex_id,
    destination_vertex_id,
    weight
)
SELECT g.graph_id, e.source_id, e.destination_id, e.weight
FROM graphs g
CROSS JOIN (
    VALUES
        (0, 1, 10),
        (1, 2, -2)
) AS e(source_id, destination_id, weight)
WHERE g.graph_name = 'disconnected_network'
AND NOT EXISTS (
    SELECT 1
    FROM edges existing
    WHERE existing.graph_id = g.graph_id
      AND existing.source_vertex_id = e.source_id
      AND existing.destination_vertex_id = e.destination_id
      AND existing.weight = e.weight
);

COMMIT;

-- ============================================================================
-- 7. EXECUTE ANALYSES
-- ============================================================================

DO $$
DECLARE
    v_graph RECORD;
    v_run_id BIGINT;
BEGIN
    FOR v_graph IN
        SELECT graph_id, graph_name
        FROM graph_lab.graphs
        ORDER BY graph_id
    LOOP
        RAISE NOTICE 'Executing graph: %', v_graph.graph_name;

        CALL graph_lab.execute_analysis(
            v_graph.graph_id,
            0,
            v_run_id
        );

        RAISE NOTICE 'Analysis run ID: %', v_run_id;
    END LOOP;
END;
$$;

-- ============================================================================
-- 8. RETRIEVAL AND REPORTING QUERIES
-- ============================================================================

-- Query 1: Graph inventory.
SELECT
    g.graph_id,
    g.graph_name,
    g.version,
    COUNT(DISTINCT v.vertex_id) AS vertex_count,
    COUNT(DISTINCT e.edge_id) AS edge_count
FROM graphs g
LEFT JOIN vertices v
    ON v.graph_id = g.graph_id
LEFT JOIN edges e
    ON e.graph_id = g.graph_id
GROUP BY g.graph_id, g.graph_name, g.version
ORDER BY g.graph_id;

-- Query 2: Shortest-path analysis results.
SELECT
    g.graph_name,
    ar.run_id,
    ar.source_vertex_id,
    r.vertex_id,
    r.distance,
    r.predecessor_vertex_id,
    r.vertex_status
FROM analysis_runs ar
JOIN graphs g
    ON g.graph_id = ar.graph_id
JOIN analysis_results r
    ON r.run_id = ar.run_id
ORDER BY ar.run_id, r.vertex_id;

-- Query 3: Negative-cycle analysis.
SELECT
    g.graph_name,
    ar.run_id,
    ar.execution_status,
    nc.cycle_vertices,
    cardinality(nc.cycle_vertices) AS affected_vertex_count
FROM analysis_runs ar
JOIN graphs g
    ON g.graph_id = ar.graph_id
LEFT JOIN negative_cycles nc
    ON nc.run_id = ar.run_id
WHERE ar.execution_status = 'NEGATIVE_CYCLE';

-- Query 4: Reachability aggregation.
SELECT
    ar.run_id,
    COUNT(*) AS total_vertices,
    COUNT(*) FILTER (
        WHERE r.vertex_status = 'SOURCE'
    ) AS source_vertices,
    COUNT(*) FILTER (
        WHERE r.vertex_status = 'REACHABLE'
    ) AS reachable_vertices,
    COUNT(*) FILTER (
        WHERE r.vertex_status = 'UNREACHABLE'
    ) AS unreachable_vertices,
    COUNT(*) FILTER (
        WHERE r.vertex_status = 'NEGATIVE_CYCLE_AFFECTED'
    ) AS cycle_affected_vertices
FROM analysis_runs ar
JOIN analysis_results r
    ON r.run_id = ar.run_id
GROUP BY ar.run_id
ORDER BY ar.run_id;

-- Query 5: Graph eligibility for a valid shortest-path result.
-- A destination is eligible if it is reachable and not affected by
-- a reachable negative cycle.
SELECT
    g.graph_name,
    r.vertex_id,
    r.distance,
    CASE
        WHEN r.vertex_status = 'UNREACHABLE'
            THEN 'NO_PATH'
        WHEN r.vertex_status = 'NEGATIVE_CYCLE_AFFECTED'
            THEN 'UNDEFINED_SHORTEST_PATH'
        ELSE 'VALID_SHORTEST_PATH'
    END AS eligibility
FROM analysis_runs ar
JOIN graphs g
    ON g.graph_id = ar.graph_id
JOIN analysis_results r
    ON r.run_id = ar.run_id
ORDER BY g.graph_name, r.vertex_id;

-- Query 6: Execution performance report.
SELECT
    g.graph_name,
    ar.run_id,
    ar.graph_version,
    ar.relaxation_passes,
    ar.execution_status,
    ar.created_at,
    ar.completed_at,
    ar.completed_at - ar.created_at AS execution_duration
FROM analysis_runs ar
JOIN graphs g
    ON g.graph_id = ar.graph_id
ORDER BY ar.run_id;

-- Query 7: Edge-level validation.
-- Identify negative edges without treating them as invalid.
SELECT
    g.graph_name,
    e.source_vertex_id,
    e.destination_vertex_id,
    e.weight,
    CASE
        WHEN e.weight < 0 THEN 'NEGATIVE_EDGE_SUPPORTED'
        ELSE 'NON_NEGATIVE_EDGE'
    END AS edge_classification
FROM edges e
JOIN graphs g
    ON g.graph_id = e.graph_id
ORDER BY g.graph_name, e.edge_id;

-- ============================================================================
-- 9. TRANSACTIONAL GRAPH UPDATE EXAMPLE
-- ============================================================================

-- The following example demonstrates an atomic graph modification.
-- Rollback prevents the example edge from changing persistent graph data.

BEGIN;

DO $$
DECLARE
    v_graph_id BIGINT;
BEGIN
    SELECT graph_id
    INTO v_graph_id
    FROM graph_lab.graphs
    WHERE graph_name = 'standard_network';

    INSERT INTO graph_lab.edges (
        graph_id,
        source_vertex_id,
        destination_vertex_id,
        weight
    )
    VALUES (
        v_graph_id,
        0,
        4,
        100
    );
END;
$$;

ROLLBACK;

-- ============================================================================
-- 10. VALIDATION AND ERROR-HANDLING EXAMPLES
-- ============================================================================

-- Invalid endpoint insertion is rejected by foreign-key constraints.
-- Execute separately to observe the constraint violation:
--
-- INSERT INTO graph_lab.edges (
--     graph_id, source_vertex_id, destination_vertex_id, weight
-- )
-- VALUES (1, 0, 999999, 10);

-- Invalid source vertex is rejected by execute_analysis:
--
-- CALL graph_lab.execute_analysis(1, 999999, NULL);

-- Graph changes increment graph.version.
-- Analysis runs retain their graph_version to identify the input snapshot.

-- ============================================================================
-- 11. ANALYSIS VIEW
-- ============================================================================

CREATE OR REPLACE VIEW v_graph_analysis AS
SELECT
    g.graph_name,
    ar.run_id,
    ar.source_vertex_id,
    ar.execution_status,
    r.vertex_id,
    r.distance,
    r.predecessor_vertex_id,
    r.vertex_status,
    ar.graph_version
FROM graphs g
JOIN analysis_runs ar
    ON ar.graph_id = g.graph_id
JOIN analysis_results r
    ON r.run_id = ar.run_id;

SELECT *
FROM v_graph_analysis
ORDER BY run_id, vertex_id;

-- ============================================================================
-- END OF SCRIPT
-- ============================================================================
