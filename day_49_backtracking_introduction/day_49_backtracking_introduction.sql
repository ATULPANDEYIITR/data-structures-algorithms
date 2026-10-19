-- PostgreSQL-compatible backtracking case study:
-- constraint-driven task assignment.
--
-- The database stores a search problem rather than implementing recursion
-- itself. Candidate states are represented relationally, constraints describe
-- legal choices, and a recursive CTE explores partial assignments.
--
-- This demonstrates an important distinction: recursive SQL can represent
-- state-space exploration, while primary keys, foreign keys, unique indexes,
-- and CHECK constraints enforce invariants around that exploration.

DROP SCHEMA IF EXISTS backtracking_lab CASCADE;
CREATE SCHEMA backtracking_lab;
SET search_path TO backtracking_lab;

CREATE TABLE workers (
    worker_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    worker_name text NOT NULL UNIQUE
);

CREATE TABLE stations (
    station_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    station_name text NOT NULL UNIQUE
);

CREATE TABLE worker_unavailability (
    worker_id bigint NOT NULL REFERENCES workers(worker_id) ON DELETE CASCADE,
    station_id bigint NOT NULL REFERENCES stations(station_id) ON DELETE CASCADE,
    PRIMARY KEY (worker_id, station_id)
);

CREATE TABLE worker_conflicts (
    worker_id bigint NOT NULL REFERENCES workers(worker_id) ON DELETE CASCADE,
    conflicting_worker_id bigint NOT NULL REFERENCES workers(worker_id) ON DELETE CASCADE,
    PRIMARY KEY (worker_id, conflicting_worker_id),
    CHECK (worker_id <> conflicting_worker_id)
);

CREATE TABLE assignments (
    assignment_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    worker_id bigint NOT NULL REFERENCES workers(worker_id),
    station_id bigint NOT NULL REFERENCES stations(station_id),
    UNIQUE (worker_id),
    UNIQUE (station_id)
);

CREATE INDEX idx_unavailability_station
    ON worker_unavailability (station_id, worker_id);

CREATE INDEX idx_conflict_reverse
    ON worker_conflicts (conflicting_worker_id, worker_id);

INSERT INTO workers (worker_name)
VALUES
    ('Asha'),
    ('Bharat'),
    ('Chen'),
    ('Divya');

INSERT INTO stations (station_name)
VALUES
    ('Inspection'),
    ('Packaging'),
    ('Loading'),
    ('Dispatch');

INSERT INTO worker_unavailability (worker_id, station_id)
SELECT w.worker_id, s.station_id
FROM workers w
JOIN stations s
    ON (w.worker_name, s.station_name) IN (
        ('Asha', 'Dispatch'),
        ('Bharat', 'Inspection'),
        ('Chen', 'Loading')
    );

INSERT INTO worker_conflicts (worker_id, conflicting_worker_id)
SELECT w1.worker_id, w2.worker_id
FROM workers w1
JOIN workers w2
    ON w1.worker_name = 'Asha'
   AND w2.worker_name = 'Chen';

-- Direct application of the constraints to a valid state.
INSERT INTO assignments (worker_id, station_id)
SELECT w.worker_id, s.station_id
FROM workers w
JOIN stations s
    ON w.worker_name = 'Asha'
   AND s.station_name = 'Inspection';

INSERT INTO assignments (worker_id, station_id)
SELECT w.worker_id, s.station_id
FROM workers w
JOIN stations s
    ON w.worker_name = 'Bharat'
   AND s.station_name = 'Packaging';

-- The UNIQUE constraints prevent the same worker or station from being
-- assigned twice. The following statement is intentionally not executed
-- because it would violate the station uniqueness constraint:
--
-- INSERT INTO assignments (worker_id, station_id)
-- SELECT w.worker_id, s.station_id
-- FROM workers w
-- CROSS JOIN stations s
-- WHERE w.worker_name = 'Chen'
--   AND s.station_name = 'Packaging';

SELECT
    w.worker_name,
    s.station_name
FROM assignments a
JOIN workers w ON w.worker_id = a.worker_id
JOIN stations s ON s.station_id = a.station_id
ORDER BY w.worker_name;

-- Reset the concrete assignment table before demonstrating recursive search.
TRUNCATE assignments RESTART IDENTITY;

-- Generate legal candidate states through a recursive CTE.
--
-- A state is encoded as a JSONB object:
-- {
--   "worker_id": station_id
-- }
--
-- The recursive term chooses an unassigned worker and an unused station.
-- It rejects unavailable stations and worker conflicts before extending the
-- state. This is the SQL equivalent of backtracking with constraint pruning.

WITH RECURSIVE search_state AS (
    SELECT
        '{}'::jsonb AS assignment,
        ARRAY[]::bigint[] AS assigned_workers,
        ARRAY[]::bigint[] AS assigned_stations,
        0 AS depth

    UNION ALL

    SELECT
        ss.assignment || jsonb_build_object(
            w.worker_id::text,
            s.station_id
        ),
        ss.assigned_workers || w.worker_id,
        ss.assigned_stations || s.station_id,
        ss.depth + 1
    FROM search_state ss
    JOIN workers w
        ON NOT (w.worker_id = ANY(ss.assigned_workers))
    JOIN stations s
        ON NOT (s.station_id = ANY(ss.assigned_stations))
    WHERE
        NOT EXISTS (
            SELECT 1
            FROM worker_unavailability wu
            WHERE wu.worker_id = w.worker_id
              AND wu.station_id = s.station_id
        )
        AND NOT EXISTS (
            SELECT 1
            FROM jsonb_each_text(ss.assignment) assigned
            JOIN worker_conflicts wc
                ON wc.worker_id = w.worker_id
               AND wc.conflicting_worker_id = assigned.key::bigint
        )
)
SELECT
    depth,
    assignment
FROM search_state
WHERE depth = (SELECT count(*) FROM workers)
ORDER BY assignment;

-- Detect which worker/station pairs are legal at the current partial state.
-- This query is useful when debugging a backtracking implementation because
-- it exposes the choices available at a particular search boundary.

WITH current_state AS (
    SELECT jsonb_build_object(
        w.worker_id::text,
        s.station_id
    ) AS assignment
    FROM workers w
    JOIN stations s
        ON w.worker_name = 'Asha'
       AND s.station_name = 'Inspection'
)
SELECT
    w.worker_name,
    s.station_name
FROM workers w
CROSS JOIN stations s
CROSS JOIN current_state cs
WHERE NOT (cs.assignment ? w.worker_id::text)
  AND NOT EXISTS (
      SELECT 1
      FROM worker_unavailability wu
      WHERE wu.worker_id = w.worker_id
        AND wu.station_id = s.station_id
  )
  AND NOT EXISTS (
      SELECT 1
      FROM jsonb_each_text(cs.assignment) assigned
      JOIN worker_conflicts wc
        ON wc.worker_id = w.worker_id
       AND wc.conflicting_worker_id = assigned.key::bigint
  )
  AND NOT (
      s.station_id IN (
          SELECT value::bigint
          FROM jsonb_each_text(cs.assignment)
      )
  )
ORDER BY w.worker_name, s.station_name;

-- A transaction provides atomicity when an application converts a discovered
-- solution into persisted assignments.

BEGIN;

INSERT INTO assignments (worker_id, station_id)
SELECT w.worker_id, s.station_id
FROM workers w
JOIN stations s
    ON (w.worker_name, s.station_name) IN (
        ('Asha', 'Inspection'),
        ('Bharat', 'Packaging'),
        ('Chen', 'Dispatch'),
        ('Divya', 'Loading')
    );

COMMIT;

-- Final integrity-oriented report.
SELECT
    w.worker_name,
    s.station_name,
    CASE
        WHEN EXISTS (
            SELECT 1
            FROM worker_unavailability wu
            WHERE wu.worker_id = w.worker_id
              AND wu.station_id = s.station_id
        )
        THEN 'INVALID: unavailable station'
        ELSE 'VALID'
    END AS availability_status
FROM assignments a
JOIN workers w ON w.worker_id = a.worker_id
JOIN stations s ON s.station_id = a.station_id
ORDER BY w.worker_name;
