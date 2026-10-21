DROP SCHEMA IF EXISTS binary_search_demo CASCADE;
CREATE SCHEMA binary_search_demo;
SET search_path TO binary_search_demo;

-- The indexed values represent ordered repository artifact identifiers.
-- A B-tree index is PostgreSQL's natural structure for ordered lookups
-- and supports equality, range, MIN/MAX, and ordered access efficiently.
CREATE TABLE repository_artifacts (
    artifact_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repository_name text NOT NULL,
    artifact_key integer NOT NULL,
    artifact_name text NOT NULL,
    artifact_state text NOT NULL DEFAULT 'active',
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT artifact_state_check
        CHECK (artifact_state IN ('active', 'archived', 'blocked')),
    CONSTRAINT artifact_name_not_blank
        CHECK (length(btrim(artifact_name)) > 0),
    CONSTRAINT repository_name_not_blank
        CHECK (length(btrim(repository_name)) > 0),
    CONSTRAINT repository_key_unique
        UNIQUE (repository_name, artifact_key)
);

CREATE INDEX repository_artifacts_key_idx
    ON repository_artifacts (repository_name, artifact_key);

INSERT INTO repository_artifacts
    (repository_name, artifact_key, artifact_name, artifact_state)
VALUES
    ('platform', 10, 'build-010', 'active'),
    ('platform', 20, 'build-020', 'active'),
    ('platform', 30, 'build-030', 'active'),
    ('platform', 40, 'build-040', 'active'),
    ('platform', 50, 'build-050', 'active'),
    ('platform', 50, 'build-050-retry', 'active'),
    ('platform', 70, 'build-070', 'active'),
    ('platform', 90, 'build-090', 'archived'),
    ('security', 15, 'scan-015', 'active'),
    ('security', 25, 'scan-025', 'active');

-- Recursive binary search is represented as a SQL function over an
-- ordered array. PostgreSQL arrays use one-based indexing, so midpoint
-- calculations deliberately account for that representation.
CREATE OR REPLACE FUNCTION binary_search_recursive(
    values integer[],
    target integer,
    left_bound integer DEFAULT 1,
    right_bound integer DEFAULT NULL
)
RETURNS integer
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    right_value integer;
    middle integer;
BEGIN
    IF values IS NULL THEN
        RETURN NULL;
    END IF;

    right_value := COALESCE(right_bound, COALESCE(array_length(values, 1), 0));

    IF left_bound > right_value THEN
        RETURN NULL;
    END IF;

    middle := left_bound + (right_value - left_bound) / 2;

    IF values[middle] = target THEN
        RETURN middle;
    ELSIF values[middle] < target THEN
        RETURN binary_search_recursive(
            values,
            target,
            middle + 1,
            right_value
        );
    ELSE
        RETURN binary_search_recursive(
            values,
            target,
            left_bound,
            middle - 1
        );
    END IF;
END;
$$;

-- This iterative form returns the first matching position, which is useful
-- when duplicate keys exist and deterministic selection is required.
CREATE OR REPLACE FUNCTION binary_search_first(
    values integer[],
    target integer
)
RETURNS integer
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    left_bound integer := 1;
    right_bound integer := COALESCE(array_length(values, 1), 0);
    middle integer;
    answer integer := NULL;
BEGIN
    IF values IS NULL THEN
        RETURN NULL;
    END IF;

    WHILE left_bound <= right_bound LOOP
        middle := left_bound
            + (right_bound - left_bound) / 2;

        IF values[middle] = target THEN
            answer := middle;
            right_bound := middle - 1;
        ELSIF values[middle] < target THEN
            left_bound := middle + 1;
        ELSE
            right_bound := middle - 1;
        END IF;
    END LOOP;

    RETURN answer;
END;
$$;

-- PostgreSQL's array_agg with ORDER BY creates the sorted search domain.
WITH ordered AS (
    SELECT array_agg(artifact_key ORDER BY artifact_key) AS keys
    FROM repository_artifacts
    WHERE repository_name = 'platform'
)
SELECT
    keys,
    binary_search_first(keys, 50) AS first_50_position,
    binary_search_recursive(keys, 70) AS recursive_70_position,
    binary_search_recursive(keys, 65) AS missing_65_position
FROM ordered;

-- A lower-bound query finds the first stored key greater than or equal
-- to the target. This is the SQL analogue of an insertion-point search.
WITH ordered AS (
    SELECT artifact_key
    FROM repository_artifacts
    WHERE repository_name = 'platform'
)
SELECT artifact_key
FROM ordered
WHERE artifact_key >= 65
ORDER BY artifact_key
LIMIT 1;

-- A CTE can evaluate the search domain and report its size and boundaries.
WITH search_domain AS (
    SELECT
        repository_name,
        min(artifact_key) AS minimum_key,
        max(artifact_key) AS maximum_key,
        count(*) AS item_count
    FROM repository_artifacts
    GROUP BY repository_name
)
SELECT *
FROM search_domain
ORDER BY repository_name;

-- Duplicate values are intentionally visible because ordinary binary
-- search may return any matching duplicate unless first/last semantics
-- are explicitly implemented.
SELECT
    repository_name,
    artifact_key,
    count(*) AS occurrences
FROM repository_artifacts
GROUP BY repository_name, artifact_key
HAVING count(*) > 1
ORDER BY repository_name, artifact_key;

-- Transactional validation: the constraint prevents a blank artifact name.
-- The savepoint allows the demonstration to recover without aborting the
-- surrounding transaction.
BEGIN;

SAVEPOINT before_invalid_insert;

DO $$
BEGIN
    BEGIN
        INSERT INTO repository_artifacts (
            repository_name,
            artifact_key,
            artifact_name
        )
        VALUES ('platform', 100, '');
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'Rejected invalid artifact by database constraint.';
            ROLLBACK TO SAVEPOINT before_invalid_insert;
    END;
END;
$$;

COMMIT;

-- The index can support an ordered range scan without loading the entire
-- relation into application memory.
EXPLAIN (COSTS OFF)
SELECT artifact_key, artifact_name
FROM repository_artifacts
WHERE repository_name = 'platform'
  AND artifact_key >= 40
  AND artifact_key <= 70
ORDER BY artifact_key;

-- A view exposes a stable search-oriented representation to reporting code.
CREATE OR REPLACE VIEW repository_search_summary AS
SELECT
    repository_name,
    count(*) AS artifact_count,
    min(artifact_key) AS minimum_key,
    max(artifact_key) AS maximum_key,
    count(DISTINCT artifact_key) AS distinct_key_count
FROM repository_artifacts
GROUP BY repository_name;

SELECT *
FROM repository_search_summary
ORDER BY repository_name;
