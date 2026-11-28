-- ============================================================
-- PRIM'S ALGORITHM
-- PostgreSQL 15+
--
-- Relational graph model and minimum spanning forest engine.
--
-- Features:
--   1. Vertices and undirected weighted edges.
--   2. Adjacency-list representation through edge relationships.
--   3. Priority-queue equivalent using an indexed temporary table.
--   4. Lazy deletion through candidate-state tracking.
--   5. Disconnected graph handling.
--   6. Negative and zero edge weights.
--   7. Execution tracking and result verification.
--   8. Reporting and aggregation.
-- ============================================================

CREATE SCHEMA IF NOT EXISTS prim_lab;

SET search_path TO prim_lab, public;

-- ------------------------------------------------------------
-- 1. DOMAIN TABLES
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS graph (
    graph_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_name VARCHAR(150) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vertex (
    vertex_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_id BIGINT NOT NULL REFERENCES graph(graph_id)
        ON DELETE CASCADE,
    vertex_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (graph_id, vertex_name),
    UNIQUE (graph_id, vertex_id)
);

CREATE TABLE IF NOT EXISTS graph_edge (
    edge_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_id BIGINT NOT NULL,
    source_vertex_id BIGINT NOT NULL,
    destination_vertex_id BIGINT NOT NULL,
    weight NUMERIC(18, 6) NOT NULL,

    FOREIGN KEY (graph_id, source_vertex_id)
        REFERENCES vertex(graph_id, vertex_id)
        ON DELETE CASCADE,

    FOREIGN KEY (graph_id, destination_vertex_id)
        REFERENCES vertex(graph_id, vertex_id)
        ON DELETE CASCADE,

    CHECK (source_vertex_id < destination_vertex_id),

    CHECK (
        weight BETWEEN -1000000000000
        AND 1000000000000
    )
);

-- Parallel edges are allowed because multiple connections
-- between two vertices may have different weights.

CREATE INDEX IF NOT EXISTS idx_vertex_graph
    ON vertex(graph_id, vertex_id);

CREATE INDEX IF NOT EXISTS idx_edge_source
    ON graph_edge(graph_id, source_vertex_id, weight);

CREATE INDEX IF NOT EXISTS idx_edge_destination
    ON graph_edge(graph_id, destination_vertex_id, weight);

CREATE INDEX IF NOT EXISTS idx_edge_weight
    ON graph_edge(graph_id, weight, edge_id);

-- ------------------------------------------------------------
-- 2. EXECUTION AND RESULT TABLES
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS mst_execution (
    execution_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    graph_id BIGINT NOT NULL REFERENCES graph(graph_id),
    execution_status VARCHAR(20) NOT NULL DEFAULT 'RUNNING',
    total_weight NUMERIC(24, 6),
    component_count INTEGER,
    vertex_count INTEGER,
    selected_edge_count INTEGER,
    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,

    CHECK (
        execution_status IN (
            'RUNNING',
            'COMPLETED',
            'FAILED'
        )
    ),

    CHECK (
        total_weight IS NULL OR
        total_weight BETWEEN -1000000000000000000
        AND 1000000000000000000
    )
);

CREATE INDEX IF NOT EXISTS idx_execution_graph
    ON mst_execution(graph_id, started_at DESC);

CREATE TABLE IF NOT EXISTS mst_result_edge (
    execution_id BIGINT NOT NULL
        REFERENCES mst_execution(execution_id)
        ON DELETE CASCADE,

    edge_id BIGINT NOT NULL
        REFERENCES graph_edge(edge_id),

    component_root BIGINT NOT NULL,

    PRIMARY KEY (execution_id, edge_id)
);

CREATE INDEX IF NOT EXISTS idx_mst_result_component
    ON mst_result_edge(execution_id, component_root);

-- ------------------------------------------------------------
-- 3. GRAPH VALIDATION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_graph_edge()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.source_vertex_id >= NEW.destination_vertex_id THEN
        RAISE EXCEPTION
            'Undirected edge endpoints must be in canonical order.';
    END IF;

    IF NEW.source_vertex_id = NEW.destination_vertex_id THEN
        RAISE EXCEPTION
            'Self-loops are not supported.';
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validate_graph_edge
    ON graph_edge;

CREATE TRIGGER trg_validate_graph_edge
BEFORE INSERT OR UPDATE ON graph_edge
FOR EACH ROW
EXECUTE FUNCTION validate_graph_edge();

-- ------------------------------------------------------------
-- 4. GRAPH INFORMATION VIEW
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW graph_statistics AS
SELECT
    g.graph_id,
    g.graph_name,
    COUNT(DISTINCT v.vertex_id) AS vertex_count,
    COUNT(DISTINCT e.edge_id) AS edge_count,
    MIN(e.weight) AS minimum_edge_weight,
    MAX(e.weight) AS maximum_edge_weight,
    AVG(e.weight) AS average_edge_weight
FROM graph g
LEFT JOIN vertex v
    ON v.graph_id = g.graph_id
LEFT JOIN graph_edge e
    ON e.graph_id = g.graph_id
GROUP BY g.graph_id, g.graph_name;

-- ------------------------------------------------------------
-- 5. PRIM'S ALGORITHM
--
-- The priority queue is represented by a temporary table.
--
-- Candidate edges are ordered by:
--   1. Weight.
--   2. Edge identifier.
--
-- The visited array tracks vertices already incorporated
-- into the current minimum spanning forest.
--
-- Every disconnected component receives its own root.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION calculate_prim_msf(
    p_graph_id BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_execution_id BIGINT;
    v_root BIGINT;
    v_edge_id BIGINT;
    v_source BIGINT;
    v_destination BIGINT;
    v_next_vertex BIGINT;
    v_weight NUMERIC(18, 6);

    v_visited BIGINT[] := ARRAY[]::BIGINT[];

    v_total_weight NUMERIC(24, 6) := 0;
    v_component_count INTEGER := 0;
    v_vertex_count INTEGER := 0;
    v_selected_count INTEGER := 0;

BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM graph
        WHERE graph_id = p_graph_id
    ) THEN
        RAISE EXCEPTION
            'Graph % does not exist.', p_graph_id;
    END IF;

    -- Record the execution independently from graph data.
    INSERT INTO mst_execution (
        graph_id,
        execution_status
    )
    VALUES (
        p_graph_id,
        'RUNNING'
    )
    RETURNING execution_id INTO v_execution_id;

    BEGIN
        SELECT COUNT(*)::INTEGER
        INTO v_vertex_count
        FROM vertex
        WHERE graph_id = p_graph_id;

        -- Isolate the candidate queue to this database session.
        DROP TABLE IF EXISTS pg_temp.prim_candidate_queue;

        CREATE TEMP TABLE prim_candidate_queue (
            edge_id BIGINT PRIMARY KEY,
            source_vertex_id BIGINT NOT NULL,
            destination_vertex_id BIGINT NOT NULL,
            weight NUMERIC(18, 6) NOT NULL,
            processed BOOLEAN NOT NULL DEFAULT FALSE
        ) ON COMMIT DROP;

        -- Create a fast lookup index for the priority queue.
        CREATE INDEX idx_prim_candidate_priority
            ON prim_candidate_queue(weight, edge_id)
            WHERE processed = FALSE;

        -- Every unvisited vertex can become a component root.
        FOR v_root IN
            SELECT vertex_id
            FROM vertex
            WHERE graph_id = p_graph_id
            ORDER BY vertex_id
        LOOP
            IF v_root = ANY(v_visited) THEN
                CONTINUE;
            END IF;

            v_component_count := v_component_count + 1;

            v_visited := array_append(
                v_visited,
                v_root
            );

            -- Insert edges connecting the new root to
            -- vertices outside the current forest.
            INSERT INTO prim_candidate_queue (
                edge_id,
                source_vertex_id,
                destination_vertex_id,
                weight
            )
            SELECT
                e.edge_id,
                e.source_vertex_id,
                e.destination_vertex_id,
                e.weight
            FROM graph_edge e
            WHERE e.graph_id = p_graph_id
              AND (
                    (
                        e.source_vertex_id = v_root
                        AND NOT (
                            e.destination_vertex_id = ANY(v_visited)
                        )
                    )
                    OR
                    (
                        e.destination_vertex_id = v_root
                        AND NOT (
                            e.source_vertex_id = ANY(v_visited)
                        )
                    )
              )
            ON CONFLICT (edge_id) DO NOTHING;

            LOOP
                -- Extract the minimum unprocessed candidate.
                SELECT
                    edge_id,
                    source_vertex_id,
                    destination_vertex_id,
                    weight
                INTO
                    v_edge_id,
                    v_source,
                    v_destination,
                    v_weight
                FROM prim_candidate_queue
                WHERE processed = FALSE
                ORDER BY weight, edge_id
                LIMIT 1;

                EXIT WHEN NOT FOUND;

                UPDATE prim_candidate_queue
                SET processed = TRUE
                WHERE edge_id = v_edge_id;

                -- Identify the endpoint outside the visited set.
                IF v_source = ANY(v_visited)
                   AND NOT (v_destination = ANY(v_visited)) THEN

                    v_next_vertex := v_destination;

                ELSIF v_destination = ANY(v_visited)
                   AND NOT (v_source = ANY(v_visited)) THEN

                    v_next_vertex := v_source;

                ELSE
                    -- Both endpoints are already visited.
                    -- This is a stale candidate and is discarded.
                    CONTINUE;
                END IF;

                -- Accept the selected edge.
                INSERT INTO mst_result_edge (
                    execution_id,
                    edge_id,
                    component_root
                )
                VALUES (
                    v_execution_id,
                    v_edge_id,
                    v_root
                );

                v_total_weight := v_total_weight + v_weight;
                v_selected_count := v_selected_count + 1;

                v_visited := array_append(
                    v_visited,
                    v_next_vertex
                );

                -- Add newly exposed outgoing edges.
                INSERT INTO prim_candidate_queue (
                    edge_id,
                    source_vertex_id,
                    destination_vertex_id,
                    weight
                )
                SELECT
                    e.edge_id,
                    e.source_vertex_id,
                    e.destination_vertex_id,
                    e.weight
                FROM graph_edge e
                WHERE e.graph_id = p_graph_id
                  AND (
                        e.source_vertex_id = v_next_vertex
                        OR e.destination_vertex_id = v_next_vertex
                  )
                  AND NOT (
                        CASE
                            WHEN e.source_vertex_id = v_next_vertex
                            THEN e.destination_vertex_id
                            ELSE e.source_vertex_id
                        END = ANY(v_visited)
                  )
                ON CONFLICT (edge_id) DO NOTHING;

            END LOOP;
        END LOOP;

        -- The forest has exactly V - C selected edges.
        IF v_selected_count <> v_vertex_count - v_component_count THEN
            RAISE EXCEPTION
                'Forest integrity validation failed.';
        END IF;

        UPDATE mst_execution
        SET
            execution_status = 'COMPLETED',
            total_weight = v_total_weight,
            component_count = v_component_count,
            vertex_count = v_vertex_count,
            selected_edge_count = v_selected_count,
            completed_at = CURRENT_TIMESTAMP
        WHERE execution_id = v_execution_id;

        RETURN v_execution_id;

    EXCEPTION WHEN OTHERS THEN

        -- Preserve execution failure information.
        UPDATE mst_execution
        SET
            execution_status = 'FAILED',
            completed_at = CURRENT_TIMESTAMP
        WHERE execution_id = v_execution_id;

        RAISE;
    END;
END;
$$;

-- ------------------------------------------------------------
-- 6. RESULT RETRIEVAL FUNCTION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION get_prim_result(
    p_execution_id BIGINT
)
RETURNS TABLE (
    edge_id BIGINT,
    source_vertex VARCHAR(100),
    destination_vertex VARCHAR(100),
    edge_weight NUMERIC(18, 6),
    component_root VARCHAR(100)
)
LANGUAGE sql
AS $$
    SELECT
        e.edge_id,
        source.vertex_name,
        destination.vertex_name,
        e.weight,
        root.vertex_name
    FROM mst_result_edge result
    JOIN graph_edge e
        ON e.edge_id = result.edge_id
    JOIN vertex source
        ON source.vertex_id = e.source_vertex_id
    JOIN vertex destination
        ON destination.vertex_id = e.destination_vertex_id
    JOIN vertex root
        ON root.vertex_id = result.component_root
    WHERE result.execution_id = p_execution_id
    ORDER BY result.component_root, e.weight, e.edge_id;
$$;

-- ------------------------------------------------------------
-- 7. ELIGIBILITY AND INTEGRITY REPORT
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_mst_execution(
    p_execution_id BIGINT
)
RETURNS TABLE (
    execution_id BIGINT,
    expected_edge_count BIGINT,
    actual_edge_count BIGINT,
    calculated_weight NUMERIC,
    stored_weight NUMERIC,
    is_valid BOOLEAN
)
LANGUAGE sql
AS $$
    WITH execution_data AS (
        SELECT *
        FROM mst_execution
        WHERE mst_execution.execution_id = p_execution_id
    ),
    selected AS (
        SELECT
            COUNT(*) AS edge_count,
            COALESCE(SUM(e.weight), 0) AS total
        FROM mst_result_edge r
        JOIN graph_edge e
            ON e.edge_id = r.edge_id
        WHERE r.execution_id = p_execution_id
    )
    SELECT
        x.execution_id,
        x.vertex_count - x.component_count,
        s.edge_count,
        s.total,
        x.total_weight,
        (
            x.execution_status = 'COMPLETED'
            AND s.edge_count = x.vertex_count - x.component_count
            AND s.total = x.total_weight
        )
    FROM execution_data x
    CROSS JOIN selected s;
$$;

-- ------------------------------------------------------------
-- 8. SAMPLE DATA
-- ------------------------------------------------------------

BEGIN;

INSERT INTO graph (
    graph_name,
    description
)
VALUES
(
    'Infrastructure_Network',
    'Connected infrastructure network with an isolated component.'
),
(
    'Negative_Weight_Test',
    'Graph demonstrating negative and parallel edge weights.'
),
(
    'Disconnected_Test',
    'Graph with three disconnected components.'
)
ON CONFLICT (graph_name) DO NOTHING;

-- Main graph.
INSERT INTO vertex (graph_id, vertex_name)
SELECT g.graph_id, names.vertex_name
FROM graph g
CROSS JOIN (
    VALUES
        ('A'), ('B'), ('C'), ('D'), ('E'),
        ('F'), ('G'), ('H'), ('I'), ('ISOLATED')
) AS names(vertex_name)
WHERE g.graph_name = 'Infrastructure_Network'
ON CONFLICT (graph_id, vertex_name) DO NOTHING;

-- Main graph edges.
INSERT INTO graph_edge (
    graph_id,
    source_vertex_id,
    destination_vertex_id,
    weight
)
SELECT
    g.graph_id,
    LEAST(v1.vertex_id, v2.vertex_id),
    GREATEST(v1.vertex_id, v2.vertex_id),
    data.weight
FROM graph g
JOIN (
    VALUES
        ('A', 'B', 4::NUMERIC),
        ('A', 'C', 3::NUMERIC),
        ('B', 'C', 1::NUMERIC),
        ('B', 'D', 2::NUMERIC),
        ('C', 'D', 4::NUMERIC),
        ('C', 'E', 5::NUMERIC),
        ('D', 'E', 2::NUMERIC),
        ('D', 'F', 3::NUMERIC),
        ('E', 'F', 1::NUMERIC),
        ('E', 'G', 7::NUMERIC),
        ('F', 'G', 2::NUMERIC),
        ('H', 'I', 6::NUMERIC)
) AS data(source_name, destination_name, weight)
ON TRUE
JOIN vertex v1
    ON v1.graph_id = g.graph_id
   AND v1.vertex_name = data.source_name
JOIN vertex v2
    ON v2.graph_id = g.graph_id
   AND v2.vertex_name = data.destination_name
WHERE g.graph_name = 'Infrastructure_Network'
AND NOT EXISTS (
    SELECT 1
    FROM graph_edge existing
    WHERE existing.graph_id = g.graph_id
      AND existing.source_vertex_id =
          LEAST(v1.vertex_id, v2.vertex_id)
      AND existing.destination_vertex_id =
          GREATEST(v1.vertex_id, v2.vertex_id)
      AND existing.weight = data.weight
);

-- Negative and parallel-edge graph.
INSERT INTO vertex (graph_id, vertex_name)
SELECT g.graph_id, names.vertex_name
FROM graph g
CROSS JOIN (
    VALUES ('X'), ('Y'), ('Z')
) AS names(vertex_name)
WHERE g.graph_name = 'Negative_Weight_Test'
ON CONFLICT (graph_id, vertex_name) DO NOTHING;

INSERT INTO graph_edge (
    graph_id,
    source_vertex_id,
    destination_vertex_id,
    weight
)
SELECT
    g.graph_id,
    LEAST(v1.vertex_id, v2.vertex_id),
    GREATEST(v1.vertex_id, v2.vertex_id),
    data.weight
FROM graph g
JOIN (
    VALUES
        ('X', 'Y', -5::NUMERIC),
        ('X', 'Y', 2::NUMERIC),
        ('Y', 'Z', -2::NUMERIC),
        ('X', 'Z', 1::NUMERIC)
) AS data(source_name, destination_name, weight)
ON TRUE
JOIN vertex v1
    ON v1.graph_id = g.graph_id
   AND v1.vertex_name = data.source_name
JOIN vertex v2
    ON v2.graph_id = g.graph_id
   AND v2.vertex_name = data.destination_name
WHERE g.graph_name = 'Negative_Weight_Test'
AND NOT EXISTS (
    SELECT 1
    FROM graph_edge existing
    WHERE existing.graph_id = g.graph_id
      AND existing.source_vertex_id =
          LEAST(v1.vertex_id, v2.vertex_id)
      AND existing.destination_vertex_id =
          GREATEST(v1.vertex_id, v2.vertex_id)
      AND existing.weight = data.weight
);

-- Disconnected graph.
INSERT INTO vertex (graph_id, vertex_name)
SELECT g.graph_id, names.vertex_name
FROM graph g
CROSS JOIN (
    VALUES ('P'), ('Q'), ('R'), ('S'), ('T')
) AS names(vertex_name)
WHERE g.graph_name = 'Disconnected_Test'
ON CONFLICT (graph_id, vertex_name) DO NOTHING;

INSERT INTO graph_edge (
    graph_id,
    source_vertex_id,
    destination_vertex_id,
    weight
)
SELECT
    g.graph_id,
    LEAST(v1.vertex_id, v2.vertex_id),
    GREATEST(v1.vertex_id, v2.vertex_id),
    data.weight
FROM graph g
JOIN (
    VALUES
        ('P', 'Q', 4::NUMERIC),
        ('R', 'S', 2::NUMERIC)
) AS data(source_name, destination_name, weight)
ON TRUE
JOIN vertex v1
    ON v1.graph_id = g.graph_id
   AND v1.vertex_name = data.source_name
JOIN vertex v2
    ON v2.graph_id = g.graph_id
   AND v2.vertex_name = data.destination_name
WHERE g.graph_name = 'Disconnected_Test'
AND NOT EXISTS (
    SELECT 1
    FROM graph_edge existing
    WHERE existing.graph_id = g.graph_id
      AND existing.source_vertex_id =
          LEAST(v1.vertex_id, v2.vertex_id)
      AND existing.destination_vertex_id =
          GREATEST(v1.vertex_id, v2.vertex_id)
      AND existing.weight = data.weight
);

COMMIT;

-- ------------------------------------------------------------
-- 9. GRAPH RETRIEVAL
-- ------------------------------------------------------------

SELECT *
FROM graph_statistics
ORDER BY graph_id;

-- ------------------------------------------------------------
-- 10. EXECUTE PRIM'S ALGORITHM
-- ------------------------------------------------------------

SELECT calculate_prim_msf(graph_id) AS execution_id
FROM graph
ORDER BY graph_id;

-- ------------------------------------------------------------
-- 11. EXECUTION REPORT
-- ------------------------------------------------------------

SELECT
    execution_id,
    graph_id,
    execution_status,
    total_weight,
    vertex_count,
    component_count,
    selected_edge_count,
    started_at,
    completed_at
FROM mst_execution
ORDER BY execution_id;

-- ------------------------------------------------------------
-- 12. SELECTED MINIMUM SPANNING FOREST EDGES
-- ------------------------------------------------------------

SELECT
    execution_id,
    edge_id,
    source_vertex,
    destination_vertex,
    edge_weight,
    component_root
FROM mst_execution execution
CROSS JOIN LATERAL get_prim_result(
    execution.execution_id
)
ORDER BY execution_id, component_root, edge_weight;

-- ------------------------------------------------------------
-- 13. VALIDATION REPORT
-- ------------------------------------------------------------

SELECT *
FROM mst_execution execution
CROSS JOIN LATERAL validate_mst_execution(
    execution.execution_id
);

-- ------------------------------------------------------------
-- 14. AGGREGATION AND COMPONENT REPORTING
-- ------------------------------------------------------------

SELECT
    execution.execution_id,
    result.component_root,
    COUNT(*) AS selected_edges,
    SUM(edge.weight) AS component_weight,
    MIN(edge.weight) AS minimum_selected_weight,
    MAX(edge.weight) AS maximum_selected_weight
FROM mst_result_edge result
JOIN mst_execution execution
    ON execution.execution_id = result.execution_id
JOIN graph_edge edge
    ON edge.edge_id = result.edge_id
GROUP BY
    execution.execution_id,
    result.component_root
ORDER BY
    execution.execution_id,
    result.component_root;

-- ------------------------------------------------------------
-- 15. INVALID DATA TESTS
--
-- Uncomment individually to observe constraint enforcement.
-- ------------------------------------------------------------

-- Self-loop:
-- INSERT INTO graph_edge (
--     graph_id, source_vertex_id, destination_vertex_id, weight
-- )
-- SELECT graph_id, vertex_id, vertex_id, 5
-- FROM vertex
-- WHERE vertex_name = 'A'
-- LIMIT 1;

-- Invalid weight:
-- INSERT INTO graph_edge (
--     graph_id, source_vertex_id, destination_vertex_id, weight
-- )
-- VALUES (1, 1, 2, 'Infinity');

-- Invalid endpoint ordering:
-- INSERT INTO graph_edge (
--     graph_id, source_vertex_id, destination_vertex_id, weight
-- )
-- VALUES (1, 2, 1, 5);

-- ------------------------------------------------------------
-- 16. EXECUTION ELIGIBILITY
-- ------------------------------------------------------------

SELECT
    execution_id,
    graph_id,
    execution_status,
    CASE
        WHEN execution_status = 'COMPLETED'
         AND selected_edge_count = vertex_count - component_count
         AND validate.is_valid
        THEN 'VALID MINIMUM SPANNING FOREST'
        WHEN execution_status = 'FAILED'
        THEN 'FAILED EXECUTION'
        ELSE 'NOT ELIGIBLE'
    END AS eligibility
FROM mst_execution execution
CROSS JOIN LATERAL validate_mst_execution(
    execution.execution_id
) validate
ORDER BY execution_id;
