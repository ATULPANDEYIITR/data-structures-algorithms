-- PostgreSQL 14+
-- Recursion fundamentals through recursive CTEs, graph traversal,
-- hierarchical aggregation, cycle detection, and bounded dependency expansion.

BEGIN;

DROP VIEW IF EXISTS service_dependency_report;
DROP TABLE IF EXISTS service_dependencies CASCADE;
DROP TABLE IF EXISTS services CASCADE;

CREATE TABLE services (
    service_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    service_name TEXT NOT NULL UNIQUE,
    build_minutes INTEGER NOT NULL CHECK (build_minutes >= 0),
    enabled BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE service_dependencies (
    parent_service_id BIGINT NOT NULL
        REFERENCES services(service_id) ON DELETE CASCADE,
    dependency_service_id BIGINT NOT NULL
        REFERENCES services(service_id) ON DELETE CASCADE,
    PRIMARY KEY (parent_service_id, dependency_service_id),
    CHECK (parent_service_id <> dependency_service_id)
);

CREATE INDEX idx_service_dependencies_reverse
    ON service_dependencies (dependency_service_id, parent_service_id);

INSERT INTO services (service_name, build_minutes, enabled) VALUES
    ('database', 8, TRUE),
    ('cache', 3, TRUE),
    ('identity', 5, TRUE),
    ('api', 12, TRUE),
    ('web-app', 7, TRUE),
    ('reporting', 6, TRUE),
    ('legacy-worker', 4, FALSE);

INSERT INTO service_dependencies
    (parent_service_id, dependency_service_id)
SELECT parent.service_id, dependency.service_id
FROM (
    VALUES
        ('identity', 'database'),
        ('api', 'database'),
        ('api', 'cache'),
        ('web-app', 'api'),
        ('web-app', 'identity'),
        ('reporting', 'api'),
        ('legacy-worker', 'database')
) AS edge(parent_name, dependency_name)
JOIN services AS parent
    ON parent.service_name = edge.parent_name
JOIN services AS dependency
    ON dependency.service_name = edge.dependency_name;

-- Recursive descent begins with a target service and follows its dependencies.
-- UNION ALL preserves distinct paths; path tracking prevents cycles from
-- causing endless recursion if the graph is later modified.
WITH RECURSIVE dependency_walk AS (
    SELECT
        s.service_id,
        s.service_name,
        s.build_minutes,
        0 AS depth,
        ARRAY[s.service_id] AS path,
        FALSE AS cycle_detected
    FROM services AS s
    WHERE s.service_name = 'web-app'

    UNION ALL

    SELECT
        dependency.service_id,
        dependency.service_name,
        dependency.build_minutes,
        walk.depth + 1,
        walk.path || dependency.service_id,
        dependency.service_id = ANY(walk.path)
    FROM dependency_walk AS walk
    JOIN service_dependencies AS edge
        ON edge.parent_service_id = walk.service_id
    JOIN services AS dependency
        ON dependency.service_id = edge.dependency_service_id
    WHERE NOT walk.cycle_detected
      AND walk.depth < 32
)
SELECT
    service_name,
    depth,
    build_minutes,
    cycle_detected,
    path
FROM dependency_walk
ORDER BY depth, service_name;

-- A reachability query identifies every unique dependency of the release target.
WITH RECURSIVE reachable AS (
    SELECT
        edge.dependency_service_id AS service_id,
        ARRAY[target.service_id, edge.dependency_service_id] AS path,
        1 AS depth
    FROM services AS target
    JOIN service_dependencies AS edge
        ON edge.parent_service_id = target.service_id
    WHERE target.service_name = 'web-app'

    UNION ALL

    SELECT
        edge.dependency_service_id,
        reachable.path || edge.dependency_service_id,
        reachable.depth + 1
    FROM reachable
    JOIN service_dependencies AS edge
        ON edge.parent_service_id = reachable.service_id
    WHERE NOT edge.dependency_service_id = ANY(reachable.path)
      AND reachable.depth < 32
)
SELECT DISTINCT
    services.service_name,
    services.build_minutes,
    MIN(reachable.depth) AS minimum_dependency_depth
FROM reachable
JOIN services USING (service_id)
GROUP BY services.service_id, services.service_name, services.build_minutes
ORDER BY minimum_dependency_depth, services.service_name;

-- Calculate a critical-path estimate. This is the longest accumulated build
-- duration along any dependency path, not the sum of every node in the graph.
WITH RECURSIVE paths AS (
    SELECT
        target.service_id,
        target.service_name,
        target.build_minutes,
        ARRAY[target.service_id] AS path,
        target.build_minutes AS accumulated_minutes,
        0 AS depth
    FROM services AS target
    WHERE target.service_name = 'web-app'

    UNION ALL

    SELECT
        dependency.service_id,
        dependency.service_name,
        dependency.build_minutes,
        paths.path || dependency.service_id,
        paths.accumulated_minutes + dependency.build_minutes,
        paths.depth + 1
    FROM paths
    JOIN service_dependencies AS edge
        ON edge.parent_service_id = paths.service_id
    JOIN services AS dependency
        ON dependency.service_id = edge.dependency_service_id
    WHERE NOT dependency.service_id = ANY(paths.path)
      AND paths.depth < 32
)
SELECT
    MAX(accumulated_minutes) AS critical_path_minutes,
    COUNT(*) AS dependency_paths_examined
FROM paths;

CREATE VIEW service_dependency_report AS
WITH RECURSIVE reachable AS (
    SELECT
        parent_service_id AS root_id,
        dependency_service_id AS node_id,
        ARRAY[parent_service_id, dependency_service_id] AS path,
        1 AS depth
    FROM service_dependencies

    UNION ALL

    SELECT
        reachable.root_id,
        edge.dependency_service_id,
        reachable.path || edge.dependency_service_id,
        reachable.depth + 1
    FROM reachable
    JOIN service_dependencies AS edge
        ON edge.parent_service_id = reachable.node_id
    WHERE NOT edge.dependency_service_id = ANY(reachable.path)
      AND reachable.depth < 32
)
SELECT
    root.service_name AS service_name,
    dependency.service_name AS dependency_name,
    MIN(reachable.depth) AS dependency_depth
FROM reachable
JOIN services AS root ON root.service_id = reachable.root_id
JOIN services AS dependency ON dependency.service_id = reachable.node_id
GROUP BY root.service_name, dependency.service_name;

SELECT *
FROM service_dependency_report
WHERE service_name = 'web-app'
ORDER BY dependency_depth, dependency_name;

-- A direct self-reference is rejected by the CHECK constraint. This block
-- demonstrates a safe failure without aborting the surrounding transaction.
DO $$
DECLARE
    database_id BIGINT;
BEGIN
    SELECT service_id INTO database_id
    FROM services
    WHERE service_name = 'database';

    BEGIN
        INSERT INTO service_dependencies
            (parent_service_id, dependency_service_id)
        VALUES (database_id, database_id);
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'Rejected direct self-dependency as expected';
    END;
END;
$$;

-- Multi-node cycles require a recursive validation query or a trigger because
-- a row-level CHECK constraint cannot inspect arbitrary graph paths.
DO $$
DECLARE
    cyclic_path TEXT[];
BEGIN
    WITH RECURSIVE paths AS (
        SELECT
            parent_service_id AS origin,
            dependency_service_id AS current_node,
            ARRAY[parent_service_id, dependency_service_id] AS path,
            dependency_service_id = parent_service_id AS cycle_found
        FROM service_dependencies

        UNION ALL

        SELECT
            paths.origin,
            edge.dependency_service_id,
            paths.path || edge.dependency_service_id,
            edge.dependency_service_id = paths.origin
        FROM paths
        JOIN service_dependencies AS edge
            ON edge.parent_service_id = paths.current_node
        WHERE NOT paths.cycle_found
          AND NOT edge.dependency_service_id = ANY(paths.path)
          AND cardinality(paths.path) < 64
    )
    SELECT ARRAY_AGG(services.service_name ORDER BY services.service_id)
    INTO cyclic_path
    FROM (
        SELECT DISTINCT origin
        FROM paths
        WHERE cycle_found
    ) AS cycle
    JOIN services ON services.service_id = cycle.origin;

    IF cyclic_path IS NOT NULL THEN
        RAISE EXCEPTION 'Dependency cycle detected in services: %', cyclic_path;
    END IF;
END;
$$;

COMMIT;
