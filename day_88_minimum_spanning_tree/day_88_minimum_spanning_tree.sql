/*
===============================================================================
MINIMUM SPANNING TREE - POSTGRESQL NETWORK PLANNING SYSTEM
===============================================================================

Implements:
1. Infrastructure network modeling.
2. Vertices and weighted undirected connections.
3. Network plans and planning states.
4. Kruskal's algorithm using PL/pgSQL.
5. Disjoint Set Union using arrays.
6. Branch-independent minimum spanning forest.
7. Mandatory and forbidden connection policies.
8. Individual and aggregate cost constraints.
9. Integrity enforcement using constraints and triggers.
10. Plan approval and audit history.
11. Reporting and validation queries.

Requirements:
PostgreSQL 14+

Execution:
Run this complete script in a PostgreSQL database.

The planning function uses a deterministic Kruskal implementation.
All monetary connection costs are represented as NUMERIC.
===============================================================================
*/

BEGIN;

CREATE SCHEMA IF NOT EXISTS mst;

SET search_path TO mst, public;


-- ============================================================================
-- 1. DOMAIN ENUMERATIONS
-- ============================================================================

CREATE TYPE network_status AS ENUM (
    'DRAFT',
    'ACTIVE',
    'ARCHIVED'
);

CREATE TYPE plan_status AS ENUM (
    'DRAFT',
    'CALCULATED',
    'VALIDATED',
    'APPROVED',
    'REJECTED'
);

CREATE TYPE algorithm_type AS ENUM (
    'KRUSKAL',
    'PRIM'
);

CREATE TYPE violation_severity AS ENUM (
    'ERROR',
    'WARNING'
);


-- ============================================================================
-- 2. NETWORKS
-- ============================================================================

CREATE TABLE networks (
    network_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    network_name VARCHAR(150) NOT NULL UNIQUE,

    description TEXT,

    status network_status NOT NULL DEFAULT 'DRAFT',

    currency_code CHAR(3) NOT NULL DEFAULT 'INR',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_network_name
        CHECK (length(trim(network_name)) > 0),

    CONSTRAINT valid_currency
        CHECK (currency_code ~ '^[A-Z]{3}$')
);


-- ============================================================================
-- 3. NETWORK VERTICES
-- ============================================================================

CREATE TABLE network_vertices (
    vertex_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    network_id BIGINT NOT NULL
        REFERENCES networks(network_id)
        ON DELETE CASCADE,

    vertex_code VARCHAR(40) NOT NULL,

    vertex_name VARCHAR(120) NOT NULL,

    region VARCHAR(100) NOT NULL,

    latitude NUMERIC(9,6),

    longitude NUMERIC(9,6),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_vertex_code
        UNIQUE(network_id, vertex_code),

    CONSTRAINT valid_coordinates
        CHECK (
            (
                latitude IS NULL
                AND longitude IS NULL
            )
            OR
            (
                latitude BETWEEN -90 AND 90
                AND longitude BETWEEN -180 AND 180
            )
        ),

    CONSTRAINT valid_vertex_name
        CHECK (
            length(trim(vertex_code)) > 0
            AND length(trim(vertex_name)) > 0
        )
);


-- ============================================================================
-- 4. CANDIDATE CONNECTIONS
-- ============================================================================

CREATE TABLE candidate_connections (
    connection_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    network_id BIGINT NOT NULL
        REFERENCES networks(network_id)
        ON DELETE CASCADE,

    source_vertex_id BIGINT NOT NULL,

    destination_vertex_id BIGINT NOT NULL,

    connection_cost NUMERIC(18,2) NOT NULL,

    provider_name VARCHAR(120) NOT NULL,

    is_available BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_connection_cost
        CHECK (connection_cost >= 0),

    CONSTRAINT different_endpoints
        CHECK (source_vertex_id <> destination_vertex_id),

    CONSTRAINT valid_provider
        CHECK (length(trim(provider_name)) > 0),

    CONSTRAINT unique_undirected_connection
        UNIQUE (
            network_id,
            source_vertex_id,
            destination_vertex_id
        ),

    CONSTRAINT source_vertex_fk
        FOREIGN KEY (network_id, source_vertex_id)
        REFERENCES network_vertices(network_id, vertex_id)
        ON DELETE CASCADE,

    CONSTRAINT destination_vertex_fk
        FOREIGN KEY (network_id, destination_vertex_id)
        REFERENCES network_vertices(network_id, vertex_id)
        ON DELETE CASCADE
);


-- ============================================================================
-- 5. NETWORK PLANNING POLICIES
-- ============================================================================

CREATE TABLE network_policies (
    policy_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    network_id BIGINT NOT NULL
        REFERENCES networks(network_id)
        ON DELETE CASCADE,

    policy_name VARCHAR(120) NOT NULL,

    require_connected BOOLEAN NOT NULL DEFAULT TRUE,

    maximum_total_cost NUMERIC(18,2),

    maximum_connection_cost NUMERIC(18,2),

    minimum_provider_count INTEGER NOT NULL DEFAULT 1,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_network_policy
        UNIQUE(network_id, policy_name),

    CONSTRAINT valid_total_limit
        CHECK (
            maximum_total_cost IS NULL
            OR maximum_total_cost >= 0
        ),

    CONSTRAINT valid_connection_limit
        CHECK (
            maximum_connection_cost IS NULL
            OR maximum_connection_cost >= 0
        ),

    CONSTRAINT valid_provider_count
        CHECK (minimum_provider_count >= 1)
);


-- ============================================================================
-- 6. MANDATORY AND FORBIDDEN CONNECTIONS
-- ============================================================================

CREATE TABLE policy_connection_rules (
    rule_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    policy_id BIGINT NOT NULL
        REFERENCES network_policies(policy_id)
        ON DELETE CASCADE,

    connection_id BIGINT NOT NULL
        REFERENCES candidate_connections(connection_id)
        ON DELETE CASCADE,

    is_mandatory BOOLEAN NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_policy_connection_rule
        UNIQUE(policy_id, connection_id)
);


-- ============================================================================
-- 7. PLANNING RECORDS
-- ============================================================================

CREATE TABLE network_plans (
    plan_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    network_id BIGINT NOT NULL
        REFERENCES networks(network_id)
        ON DELETE CASCADE,

    policy_id BIGINT
        REFERENCES network_policies(policy_id)
        ON DELETE SET NULL,

    plan_name VARCHAR(120) NOT NULL,

    algorithm algorithm_type NOT NULL DEFAULT 'KRUSKAL',

    status plan_status NOT NULL DEFAULT 'DRAFT',

    source_version TIMESTAMP WITH TIME ZONE
        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    total_cost NUMERIC(18,2),

    vertex_count INTEGER NOT NULL DEFAULT 0,

    selected_edge_count INTEGER NOT NULL DEFAULT 0,

    component_count INTEGER NOT NULL DEFAULT 0,

    connected BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    calculated_at TIMESTAMPTZ,

    approved_at TIMESTAMPTZ,

    CONSTRAINT unique_plan_name
        UNIQUE(network_id, plan_name),

    CONSTRAINT valid_plan_cost
        CHECK (total_cost IS NULL OR total_cost >= 0),

    CONSTRAINT valid_plan_counts
        CHECK (
            vertex_count >= 0
            AND selected_edge_count >= 0
            AND component_count >= 0
            AND component_count <= vertex_count
        ),

    CONSTRAINT valid_tree_edge_count
        CHECK (
            selected_edge_count =
                vertex_count - component_count
            OR status = 'DRAFT'
        )
);


-- ============================================================================
-- 8. SELECTED MST CONNECTIONS
-- ============================================================================

CREATE TABLE plan_connections (
    plan_connection_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    plan_id BIGINT NOT NULL
        REFERENCES network_plans(plan_id)
        ON DELETE CASCADE,

    connection_id BIGINT NOT NULL
        REFERENCES candidate_connections(connection_id)
        ON DELETE RESTRICT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_selected_connection
        UNIQUE(plan_id, connection_id)
);


-- ============================================================================
-- 9. POLICY VALIDATION HISTORY
-- ============================================================================

CREATE TABLE plan_violations (
    violation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    plan_id BIGINT NOT NULL
        REFERENCES network_plans(plan_id)
        ON DELETE CASCADE,

    severity violation_severity NOT NULL,

    violation_code VARCHAR(60) NOT NULL,

    description TEXT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================================
-- 10. APPROVAL AUDIT
-- ============================================================================

CREATE TABLE plan_approvals (
    approval_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    plan_id BIGINT NOT NULL
        REFERENCES network_plans(plan_id)
        ON DELETE CASCADE,

    approved_by VARCHAR(120) NOT NULL,

    decision VARCHAR(20) NOT NULL,

    remarks TEXT,

    decided_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_approval_decision
        CHECK (decision IN ('APPROVED', 'REJECTED')),

    CONSTRAINT valid_approver
        CHECK (length(trim(approved_by)) > 0)
);


-- ============================================================================
-- 11. INDEXES
-- ============================================================================

CREATE INDEX idx_vertices_network
    ON network_vertices(network_id);

CREATE INDEX idx_connections_network_cost
    ON candidate_connections(
        network_id,
        connection_cost,
        connection_id
    )
    WHERE is_available = TRUE;

CREATE INDEX idx_connections_source
    ON candidate_connections(
        network_id,
        source_vertex_id
    );

CREATE INDEX idx_connections_destination
    ON candidate_connections(
        network_id,
        destination_vertex_id
    );

CREATE INDEX idx_plans_network_status
    ON network_plans(
        network_id,
        status,
        created_at DESC
    );

CREATE INDEX idx_plan_connections_plan
    ON plan_connections(plan_id);

CREATE INDEX idx_violations_plan
    ON plan_violations(
        plan_id,
        severity
    );

CREATE INDEX idx_approval_history
    ON plan_approvals(
        plan_id,
        decided_at DESC
    );


-- ============================================================================
-- 12. UPDATED TIMESTAMP TRIGGER
-- ============================================================================

CREATE OR REPLACE FUNCTION update_modified_timestamp()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_network_updated
BEFORE UPDATE ON networks
FOR EACH ROW
EXECUTE FUNCTION update_modified_timestamp();


-- ============================================================================
-- 13. PREVENT CONNECTIONS ACROSS NETWORKS
-- ============================================================================

CREATE OR REPLACE FUNCTION validate_connection_network()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    source_network BIGINT;
    destination_network BIGINT;
BEGIN
    SELECT network_id
    INTO source_network
    FROM network_vertices
    WHERE vertex_id = NEW.source_vertex_id;

    SELECT network_id
    INTO destination_network
    FROM network_vertices
    WHERE vertex_id = NEW.destination_vertex_id;

    IF source_network IS NULL
       OR destination_network IS NULL THEN

        RAISE EXCEPTION 'Connection endpoint does not exist.';
    END IF;

    IF source_network <> NEW.network_id
       OR destination_network <> NEW.network_id THEN

        RAISE EXCEPTION
            'Connection endpoints must belong to the same network.';
    END IF;

    IF NEW.source_vertex_id > NEW.destination_vertex_id THEN
        RAISE EXCEPTION
            'Store undirected connections using ascending vertex IDs.';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_connection_network
BEFORE INSERT OR UPDATE ON candidate_connections
FOR EACH ROW
EXECUTE FUNCTION validate_connection_network();


-- ============================================================================
-- 14. PREVENT RULES FROM CROSSING NETWORK BOUNDARIES
-- ============================================================================

CREATE OR REPLACE FUNCTION validate_policy_connection()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    policy_network BIGINT;
    connection_network BIGINT;
BEGIN
    SELECT network_id
    INTO policy_network
    FROM network_policies
    WHERE policy_id = NEW.policy_id;

    SELECT network_id
    INTO connection_network
    FROM candidate_connections
    WHERE connection_id = NEW.connection_id;

    IF policy_network IS NULL
       OR connection_network IS NULL
       OR policy_network <> connection_network THEN

        RAISE EXCEPTION
            'Policy and connection must belong to the same network.';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_policy_connection
BEFORE INSERT OR UPDATE ON policy_connection_rules
FOR EACH ROW
EXECUTE FUNCTION validate_policy_connection();


-- ============================================================================
-- 15. PROTECT APPROVED PLANS FROM MODIFICATION
-- ============================================================================

CREATE OR REPLACE FUNCTION protect_finalized_plan()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    current_status plan_status;
BEGIN
    SELECT status
    INTO current_status
    FROM network_plans
    WHERE plan_id = OLD.plan_id
    FOR UPDATE;

    IF current_status IN ('APPROVED', 'REJECTED') THEN
        RAISE EXCEPTION
            'Selected connections cannot change after finalization.';
    END IF;

    RETURN COALESCE(NEW, OLD);
END;
$$;

CREATE TRIGGER trg_protect_plan_connections
BEFORE INSERT OR UPDATE OR DELETE ON plan_connections
FOR EACH ROW
EXECUTE FUNCTION protect_finalized_plan();


-- ============================================================================
-- 16. CREATE NETWORK PLAN
-- ============================================================================

CREATE OR REPLACE FUNCTION create_network_plan(
    p_network_id BIGINT,
    p_plan_name VARCHAR,
    p_policy_id BIGINT DEFAULT NULL,
    p_algorithm algorithm_type DEFAULT 'KRUSKAL'
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    new_plan_id BIGINT;
    policy_network BIGINT;
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM networks
        WHERE network_id = p_network_id
    ) THEN
        RAISE EXCEPTION 'Network does not exist.';
    END IF;

    IF p_policy_id IS NOT NULL THEN
        SELECT network_id
        INTO policy_network
        FROM network_policies
        WHERE policy_id = p_policy_id;

        IF policy_network IS DISTINCT FROM p_network_id THEN
            RAISE EXCEPTION
                'Policy does not belong to the requested network.';
        END IF;
    END IF;

    INSERT INTO network_plans (
        network_id,
        policy_id,
        plan_name,
        algorithm,
        source_version
    )
    VALUES (
        p_network_id,
        p_policy_id,
        p_plan_name,
        p_algorithm,
        CURRENT_TIMESTAMP
    )
    RETURNING plan_id INTO new_plan_id;

    RETURN new_plan_id;
END;
$$;


-- ============================================================================
-- 17. KRUSKAL MINIMUM SPANNING FOREST FUNCTION
-- ============================================================================

CREATE OR REPLACE FUNCTION calculate_minimum_spanning_tree(
    p_plan_id BIGINT
)
RETURNS TABLE (
    result_plan_id BIGINT,
    selected_edges INTEGER,
    component_count INTEGER,
    total_cost NUMERIC,
    is_connected BOOLEAN
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_network_id BIGINT;
    v_status plan_status;
    v_algorithm algorithm_type;

    vertex_ids BIGINT[];
    parent INTEGER[];
    ranks INTEGER[];

    vertex_total INTEGER;
    component_total INTEGER;

    current_edge RECORD;

    u INTEGER;
    v INTEGER;

    root_u INTEGER;
    root_v INTEGER;

    selected_total INTEGER := 0;
    cost_total NUMERIC(18,2) := 0;

BEGIN
    SELECT network_id, status, algorithm
    INTO v_network_id, v_status, v_algorithm
    FROM network_plans
    WHERE plan_id = p_plan_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Plan % does not exist.', p_plan_id;
    END IF;

    IF v_status <> 'DRAFT' THEN
        RAISE EXCEPTION
            'Only DRAFT plans can be calculated.';
    END IF;

    SELECT array_agg(vertex_id ORDER BY vertex_id)
    INTO vertex_ids
    FROM network_vertices
    WHERE network_id = v_network_id;

    vertex_total := COALESCE(
        cardinality(vertex_ids),
        0
    );

    IF vertex_total = 0 THEN
        RAISE EXCEPTION
            'Cannot calculate a spanning tree for an empty network.';
    END IF;

    parent := ARRAY(
        SELECT generate_series(1, vertex_total)
    );

    ranks := array_fill(0, ARRAY[vertex_total]);

    component_total := vertex_total;

    DELETE FROM plan_connections
    WHERE plan_id = p_plan_id;

    /*
     * Candidate edges are processed in ascending cost order.
     * Each edge is considered once.
     *
     * ARRAY_POSITION maps database vertex IDs to DSU indexes.
     */

    FOR current_edge IN
        SELECT
            connection_id,
            source_vertex_id,
            destination_vertex_id,
            connection_cost
        FROM candidate_connections
        WHERE network_id = v_network_id
          AND is_available = TRUE
        ORDER BY
            connection_cost,
            connection_id
    LOOP

        u := array_position(
            vertex_ids,
            current_edge.source_vertex_id
        );

        v := array_position(
            vertex_ids,
            current_edge.destination_vertex_id
        );

        IF u IS NULL OR v IS NULL THEN
            RAISE EXCEPTION
                'Connection references a missing vertex.';
        END IF;

        -- Find first component root.
        root_u := u;

        WHILE parent[root_u] <> root_u LOOP
            root_u := parent[root_u];
        END LOOP;

        -- Find second component root.
        root_v := v;

        WHILE parent[root_v] <> root_v LOOP
            root_v := parent[root_v];
        END LOOP;

        -- Path compression.
        WHILE parent[u] <> u LOOP
            DECLARE
                next_u INTEGER;
            BEGIN
                next_u := parent[u];
                parent[u] := root_u;
                u := next_u;
            END;
        END LOOP;

        WHILE parent[v] <> v LOOP
            DECLARE
                next_v INTEGER;
            BEGIN
                next_v := parent[v];
                parent[v] := root_v;
                v := next_v;
            END;
        END LOOP;

        -- A cycle-forming edge must be skipped.
        IF root_u <> root_v THEN

            -- Union by rank.
            IF ranks[root_u] < ranks[root_v] THEN

                parent[root_u] := root_v;

            ELSIF ranks[root_u] > ranks[root_v] THEN

                parent[root_v] := root_u;

            ELSE

                parent[root_v] := root_u;
                ranks[root_u] := ranks[root_u] + 1;

            END IF;

            component_total := component_total - 1;

            selected_total := selected_total + 1;

            cost_total :=
                cost_total + current_edge.connection_cost;

            INSERT INTO plan_connections (
                plan_id,
                connection_id
            )
            VALUES (
                p_plan_id,
                current_edge.connection_id
            );

            IF component_total = 1 THEN
                EXIT;
            END IF;

        END IF;

    END LOOP;

    /*
     * An isolated vertex remains its own component.
     * A disconnected graph therefore produces a forest.
     */

    UPDATE network_plans
    SET
        status = 'CALCULATED',
        total_cost = cost_total,
        vertex_count = vertex_total,
        selected_edge_count = selected_total,
        component_count = component_total,
        connected = (component_total <= 1),
        calculated_at = CURRENT_TIMESTAMP
    WHERE plan_id = p_plan_id;

    RETURN QUERY
    SELECT
        p_plan_id,
        selected_total,
        component_total,
        cost_total,
        component_total <= 1;

END;
$$;


-- ============================================================================
-- 18. POLICY VALIDATION FUNCTION
-- ============================================================================

CREATE OR REPLACE FUNCTION validate_network_plan(
    p_plan_id BIGINT
)
RETURNS TABLE (
    violation_type violation_severity,
    violation_description TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    plan_record RECORD;
    policy_record RECORD;

    provider_total INTEGER;
    invalid_count INTEGER;
    missing_count INTEGER;
BEGIN

    SELECT *
    INTO plan_record
    FROM network_plans
    WHERE plan_id = p_plan_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Plan does not exist.';
    END IF;

    IF plan_record.status <> 'CALCULATED' THEN
        RAISE EXCEPTION
            'Only CALCULATED plans can be validated.';
    END IF;

    DELETE FROM plan_violations
    WHERE plan_id = p_plan_id;

    IF plan_record.policy_id IS NULL THEN

        UPDATE network_plans
        SET status = 'VALIDATED'
        WHERE plan_id = p_plan_id;

        RETURN;

    END IF;

    SELECT *
    INTO policy_record
    FROM network_policies
    WHERE policy_id = plan_record.policy_id;

    IF policy_record.require_connected
       AND NOT plan_record.connected THEN

        INSERT INTO plan_violations (
            plan_id,
            severity,
            violation_code,
            description
        )
        VALUES (
            p_plan_id,
            'ERROR',
            'DISCONNECTED_NETWORK',
            'The policy requires one connected component.'
        );

    END IF;

    IF policy_record.maximum_total_cost IS NOT NULL
       AND plan_record.total_cost >
           policy_record.maximum_total_cost THEN

        INSERT INTO plan_violations (
            plan_id,
            severity,
            violation_code,
            description
        )
        VALUES (
            p_plan_id,
            'ERROR',
            'TOTAL_BUDGET_EXCEEDED',
            'Total selected connection cost exceeds the policy.'
        );

    END IF;

    IF policy_record.maximum_connection_cost IS NOT NULL THEN

        INSERT INTO plan_violations (
            plan_id,
            severity,
            violation_code,
            description
        )
        SELECT
            p_plan_id,
            'ERROR',
            'INDIVIDUAL_COST_EXCEEDED',
            'Connection ' || c.connection_id ||
            ' exceeds the individual cost limit.'
        FROM plan_connections pc
        JOIN candidate_connections c
            ON c.connection_id = pc.connection_id
        WHERE pc.plan_id = p_plan_id
          AND c.connection_cost >
              policy_record.maximum_connection_cost;

    END IF;

    -- Forbidden connections.
    INSERT INTO plan_violations (
        plan_id,
        severity,
        violation_code,
        description
    )
    SELECT
        p_plan_id,
        'ERROR',
        'FORBIDDEN_CONNECTION',
        'A prohibited connection was selected.'
    FROM plan_connections pc
    JOIN policy_connection_rules r
        ON r.connection_id = pc.connection_id
    WHERE pc.plan_id = p_plan_id
      AND r.policy_id = plan_record.policy_id
      AND r.is_mandatory = FALSE;

    -- Mandatory connections.
    INSERT INTO plan_violations (
        plan_id,
        severity,
        violation_code,
        description
    )
    SELECT
        p_plan_id,
        'ERROR',
        'MANDATORY_CONNECTION_MISSING',
        'A mandatory connection was not selected.'
    FROM policy_connection_rules r
    WHERE r.policy_id = plan_record.policy_id
      AND r.is_mandatory = TRUE
      AND NOT EXISTS (
          SELECT 1
          FROM plan_connections pc
          WHERE pc.plan_id = p_plan_id
            AND pc.connection_id = r.connection_id
      );

    -- Provider diversity.
    SELECT COUNT(DISTINCT c.provider_name)
    INTO provider_total
    FROM plan_connections pc
    JOIN candidate_connections c
        ON c.connection_id = pc.connection_id
    WHERE pc.plan_id = p_plan_id;

    IF provider_total <
       policy_record.minimum_provider_count THEN

        INSERT INTO plan_violations (
            plan_id,
            severity,
            violation_code,
            description
        )
        VALUES (
            p_plan_id,
            'WARNING',
            'PROVIDER_DIVERSITY',
            'Selected providers do not satisfy the diversity policy.'
        );

    END IF;

    SELECT COUNT(*)
    INTO invalid_count
    FROM plan_violations
    WHERE plan_id = p_plan_id
      AND severity = 'ERROR';

    UPDATE network_plans
    SET status = CASE
        WHEN invalid_count = 0 THEN 'VALIDATED'::plan_status
        ELSE 'REJECTED'::plan_status
    END
    WHERE plan_id = p_plan_id;

    RETURN QUERY
    SELECT
        pv.severity,
        pv.description
    FROM plan_violations pv
    WHERE pv.plan_id = p_plan_id
    ORDER BY pv.violation_id;

END;
$$;


-- ============================================================================
-- 19. PLAN APPROVAL PROCEDURE
-- ============================================================================

CREATE OR REPLACE PROCEDURE approve_network_plan(
    p_plan_id BIGINT,
    p_approved_by VARCHAR,
    p_remarks TEXT DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    current_status plan_status;
BEGIN

    SELECT status
    INTO current_status
    FROM network_plans
    WHERE plan_id = p_plan_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Plan does not exist.';
    END IF;

    IF current_status <> 'VALIDATED' THEN
        RAISE EXCEPTION
            'Only VALIDATED plans can be approved.';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM plan_violations
        WHERE plan_id = p_plan_id
          AND severity = 'ERROR'
    ) THEN
        RAISE EXCEPTION
            'Plan contains unresolved policy violations.';
    END IF;

    UPDATE network_plans
    SET
        status = 'APPROVED',
        approved_at = CURRENT_TIMESTAMP
    WHERE plan_id = p_plan_id;

    INSERT INTO plan_approvals (
        plan_id,
        approved_by,
        decision,
        remarks
    )
    VALUES (
        p_plan_id,
        p_approved_by,
        'APPROVED',
        p_remarks
    );

END;
$$;


-- ============================================================================
-- 20. NETWORK REPORTING VIEW
-- ============================================================================

CREATE OR REPLACE VIEW network_plan_report AS
SELECT
    n.network_id,
    n.network_name,
    p.plan_id,
    p.plan_name,
    p.algorithm,
    p.status,
    p.vertex_count,
    p.selected_edge_count,
    p.component_count,
    p.connected,
    p.total_cost,
    p.created_at,
    p.calculated_at,
    p.approved_at,
    COUNT(
        DISTINCT CASE
            WHEN v.severity = 'ERROR'
            THEN v.violation_id
        END
    ) AS error_count,
    COUNT(
        DISTINCT CASE
            WHEN v.severity = 'WARNING'
            THEN v.violation_id
        END
    ) AS warning_count
FROM networks n
JOIN network_plans p
    ON p.network_id = n.network_id
LEFT JOIN plan_violations v
    ON v.plan_id = p.plan_id
GROUP BY
    n.network_id,
    n.network_name,
    p.plan_id;


-- ============================================================================
-- 21. SAMPLE NETWORK DATA
-- ============================================================================

INSERT INTO networks (
    network_name,
    description,
    currency_code,
    status
)
VALUES (
    'National Fiber Network',
    'Regional telecommunications infrastructure planning.',
    'INR',
    'ACTIVE'
);

INSERT INTO network_vertices (
    network_id,
    vertex_code,
    vertex_name,
    region,
    latitude,
    longitude
)
SELECT
    n.network_id,
    v.vertex_code,
    v.vertex_name,
    v.region,
    v.latitude,
    v.longitude
FROM networks n
CROSS JOIN (
    VALUES
        ('A', 'Lucknow Central', 'North', 26.8467, 80.9462),
        ('B', 'Kanpur Hub', 'North', 26.4499, 80.3319),
        ('C', 'Prayagraj Hub', 'North', 25.4358, 81.8463),
        ('D', 'Varanasi Hub', 'East', 25.3176, 82.9739),
        ('E', 'Patna Hub', 'East', 25.5941, 85.1376),
        ('F', 'Gorakhpur Hub', 'East', 26.7606, 83.3732)
) AS v(
    vertex_code,
    vertex_name,
    region,
    latitude,
    longitude
)
WHERE n.network_name = 'National Fiber Network';


-- ============================================================================
-- 22. CANDIDATE CONNECTION DATA
-- ============================================================================

INSERT INTO candidate_connections (
    network_id,
    source_vertex_id,
    destination_vertex_id,
    connection_cost,
    provider_name
)
SELECT
    n.network_id,
    LEAST(a.vertex_id, b.vertex_id),
    GREATEST(a.vertex_id, b.vertex_id),
    e.cost,
    e.provider
FROM networks n
CROSS JOIN (
    VALUES
        ('A', 'B', 4.00::NUMERIC, 'Provider-1'),
        ('A', 'C', 3.00::NUMERIC, 'Provider-1'),
        ('B', 'C', 1.00::NUMERIC, 'Provider-2'),
        ('B', 'D', 2.00::NUMERIC, 'Provider-2'),
        ('C', 'D', 4.00::NUMERIC, 'Provider-1'),
        ('C', 'E', 5.00::NUMERIC, 'Provider-3'),
        ('D', 'E', 2.00::NUMERIC, 'Provider-2'),
        ('D', 'F', 6.00::NUMERIC, 'Provider-3'),
        ('E', 'F', 3.00::NUMERIC, 'Provider-3'),
        ('A', 'F', 10.00::NUMERIC, 'Provider-1')
) AS e(
    source_code,
    destination_code,
    cost,
    provider
)
JOIN network_vertices a
    ON a.network_id = n.network_id
   AND a.vertex_code = e.source_code
JOIN network_vertices b
    ON b.network_id = n.network_id
   AND b.vertex_code = e.destination_code
WHERE n.network_name = 'National Fiber Network';


-- ============================================================================
-- 23. POLICY CONFIGURATION
-- ============================================================================

INSERT INTO network_policies (
    network_id,
    policy_name,
    require_connected,
    maximum_total_cost,
    maximum_connection_cost,
    minimum_provider_count
)
SELECT
    network_id,
    'Standard Infrastructure Policy',
    TRUE,
    15.00,
    6.00,
    2
FROM networks
WHERE network_name = 'National Fiber Network';


-- ============================================================================
-- 24. SAMPLE POLICY RULES
-- ============================================================================

/*
 * The A-F connection is forbidden because its cost is high.
 * It is not a mandatory connection.
 */

INSERT INTO policy_connection_rules (
    policy_id,
    connection_id,
    is_mandatory
)
SELECT
    p.policy_id,
    c.connection_id,
    FALSE
FROM network_policies p
JOIN networks n
    ON n.network_id = p.network_id
JOIN network_vertices a
    ON a.network_id = n.network_id
   AND a.vertex_code = 'A'
JOIN network_vertices f
    ON f.network_id = n.network_id
   AND f.vertex_code = 'F'
JOIN candidate_connections c
    ON c.network_id = n.network_id
   AND c.source_vertex_id = LEAST(a.vertex_id, f.vertex_id)
   AND c.destination_vertex_id = GREATEST(a.vertex_id, f.vertex_id)
WHERE p.policy_name = 'Standard Infrastructure Policy'
  AND n.network_name = 'National Fiber Network';


-- ============================================================================
-- 25. CREATE AND CALCULATE AN MST PLAN
-- ============================================================================

DO $$
DECLARE
    v_network_id BIGINT;
    v_policy_id BIGINT;
    v_plan_id BIGINT;
BEGIN

    SELECT network_id
    INTO v_network_id
    FROM networks
    WHERE network_name = 'National Fiber Network';

    SELECT policy_id
    INTO v_policy_id
    FROM network_policies
    WHERE network_id = v_network_id
      AND policy_name = 'Standard Infrastructure Policy';

    v_plan_id := create_network_plan(
        v_network_id,
        'Minimum Cost Regional Network',
        v_policy_id,
        'KRUSKAL'
    );

    RAISE NOTICE 'Created plan ID: %', v_plan_id;

    PERFORM *
    FROM calculate_minimum_spanning_tree(v_plan_id);

    RAISE NOTICE 'MST calculated successfully.';

    PERFORM *
    FROM validate_network_plan(v_plan_id);

    RAISE NOTICE 'Policy validation completed.';

END;
$$;


-- ============================================================================
-- 26. SAMPLE QUERIES: CANDIDATE CONNECTION RETRIEVAL
-- ============================================================================

SELECT
    a.vertex_code AS source,
    b.vertex_code AS destination,
    c.connection_cost,
    c.provider_name,
    c.is_available
FROM candidate_connections c
JOIN network_vertices a
    ON a.vertex_id = c.source_vertex_id
JOIN network_vertices b
    ON b.vertex_id = c.destination_vertex_id
JOIN networks n
    ON n.network_id = c.network_id
WHERE n.network_name = 'National Fiber Network'
ORDER BY c.connection_cost, c.connection_id;


-- ============================================================================
-- 27. SELECTED MST CONNECTIONS
-- ============================================================================

SELECT
    p.plan_name,
    a.vertex_code AS source,
    b.vertex_code AS destination,
    c.connection_cost,
    c.provider_name
FROM plan_connections pc
JOIN network_plans p
    ON p.plan_id = pc.plan_id
JOIN candidate_connections c
    ON c.connection_id = pc.connection_id
JOIN network_vertices a
    ON a.vertex_id = c.source_vertex_id
JOIN network_vertices b
    ON b.vertex_id = c.destination_vertex_id
ORDER BY c.connection_cost, c.connection_id;


-- ============================================================================
-- 28. NETWORK COST AGGREGATION
-- ============================================================================

SELECT
    p.plan_id,
    p.plan_name,
    p.total_cost,
    p.vertex_count,
    p.selected_edge_count,
    p.component_count,
    p.connected,
    SUM(c.connection_cost) AS verified_selected_cost
FROM network_plans p
JOIN plan_connections pc
    ON pc.plan_id = p.plan_id
JOIN candidate_connections c
    ON c.connection_id = pc.connection_id
GROUP BY
    p.plan_id,
    p.plan_name,
    p.total_cost,
    p.vertex_count,
    p.selected_edge_count,
    p.component_count,
    p.connected;


-- ============================================================================
-- 29. POLICY VIOLATION REPORT
-- ============================================================================

SELECT
    p.plan_name,
    v.severity,
    v.violation_code,
    v.description,
    v.created_at
FROM plan_violations v
JOIN network_plans p
    ON p.plan_id = v.plan_id
ORDER BY v.created_at DESC;


-- ============================================================================
-- 30. PLAN ELIGIBILITY DETERMINATION
-- ============================================================================

SELECT
    plan_id,
    plan_name,
    status,
    connected,
    total_cost,
    CASE
        WHEN status = 'APPROVED'
            THEN 'APPROVED FOR IMPLEMENTATION'

        WHEN status = 'VALIDATED'
            THEN 'AWAITING APPROVAL'

        WHEN status = 'REJECTED'
            THEN 'POLICY REJECTION'

        WHEN status = 'CALCULATED'
            THEN 'VALIDATION REQUIRED'

        ELSE 'NOT CALCULATED'
    END AS eligibility
FROM network_plans;


-- ============================================================================
-- 31. APPROVE THE VALIDATED PLAN
-- ============================================================================

DO $$
DECLARE
    v_plan_id BIGINT;
BEGIN

    SELECT plan_id
    INTO v_plan_id
    FROM network_plans
    WHERE plan_name = 'Minimum Cost Regional Network';

    IF EXISTS (
        SELECT 1
        FROM network_plans
        WHERE plan_id = v_plan_id
          AND status = 'VALIDATED'
    ) THEN

        CALL approve_network_plan(
            v_plan_id,
            'Infrastructure Planning Officer',
            'Validated minimum-cost network plan.'
        );

    ELSE
        RAISE NOTICE
            'Plan is not eligible for approval.';
    END IF;

END;
$$;


-- ============================================================================
-- 32. FINAL NETWORK DASHBOARD
-- ============================================================================

SELECT *
FROM network_plan_report
ORDER BY created_at DESC;


-- ============================================================================
-- 33. TRANSACTIONAL VALIDATION
-- ============================================================================

/*
 * Demonstrate transaction rollback.
 * This invalid connection must not persist.
 */

SAVEPOINT before_invalid_connection;

DO $$
DECLARE
    v_network_id BIGINT;
    v_a BIGINT;
BEGIN

    SELECT network_id
    INTO v_network_id
    FROM networks
    WHERE network_name = 'National Fiber Network';

    SELECT vertex_id
    INTO v_a
    FROM network_vertices
    WHERE network_id = v_network_id
      AND vertex_code = 'A';

    BEGIN

        INSERT INTO candidate_connections (
            network_id,
            source_vertex_id,
            destination_vertex_id,
            connection_cost,
            provider_name
        )
        VALUES (
            v_network_id,
            v_a,
            v_a,
            100,
            'Invalid Provider'
        );

    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'Expected invalid self-loop rejected.';
    END;

END;
$$;

RELEASE SAVEPOINT before_invalid_connection;


-- ============================================================================
-- 34. PERFORMANCE AND INTEGRITY CHECKS
-- ============================================================================

SELECT
    n.network_name,
    COUNT(DISTINCT v.vertex_id) AS vertex_count,
    COUNT(DISTINCT c.connection_id) AS candidate_connection_count,
    COUNT(DISTINCT p.plan_id) AS plan_count
FROM networks n
LEFT JOIN network_vertices v
    ON v.network_id = n.network_id
LEFT JOIN candidate_connections c
    ON c.network_id = n.network_id
LEFT JOIN network_plans p
    ON p.network_id = n.network_id
GROUP BY n.network_id, n.network_name;


-- ============================================================================
-- 35. FINAL COMMIT
-- ============================================================================

COMMIT;
