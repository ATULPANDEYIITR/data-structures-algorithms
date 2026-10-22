DROP SCHEMA IF EXISTS binary_search_variations CASCADE;
CREATE SCHEMA binary_search_variations;
SET search_path = binary_search_variations;

-- A sorted sequence is represented explicitly so that database constraints
-- can enforce the ordering required by binary-search-style range evaluation.
CREATE TABLE search_collections (
    collection_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    collection_name text NOT NULL UNIQUE,
    description text NOT NULL
);

CREATE TABLE search_values (
    collection_id bigint NOT NULL
        REFERENCES search_collections(collection_id)
        ON DELETE CASCADE,
    position integer NOT NULL CHECK (position >= 0),
    value integer NOT NULL,
    PRIMARY KEY (collection_id, position),
    UNIQUE (collection_id, position, value)
);

CREATE INDEX idx_search_values_lookup
    ON search_values (collection_id, value, position);

CREATE TABLE search_queries (
    query_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    collection_id bigint NOT NULL
        REFERENCES search_collections(collection_id)
        ON DELETE CASCADE,
    target integer NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE search_results (
    query_id bigint PRIMARY KEY
        REFERENCES search_queries(query_id)
        ON DELETE CASCADE,
    lower_bound integer NOT NULL CHECK (lower_bound >= 0),
    upper_bound integer NOT NULL CHECK (upper_bound >= lower_bound),
    first_occurrence integer,
    last_occurrence integer,
    occurrence_count integer NOT NULL CHECK (occurrence_count >= 0),
    insertion_position integer NOT NULL CHECK (insertion_position >= 0),
    CHECK (
        first_occurrence IS NULL
        OR (
            first_occurrence >= 0
            AND last_occurrence IS NOT NULL
            AND last_occurrence >= first_occurrence
        )
    )
);

-- Insert realistic sorted data containing singleton values and duplicates.
INSERT INTO search_collections (collection_name, description)
VALUES
    (
        'release_versions',
        'Sorted release identifiers containing repeated releases.'
    ),
    (
        'response_times',
        'Sorted response-time measurements containing duplicate values.'
    );

INSERT INTO search_values (collection_id, position, value)
SELECT
    c.collection_id,
    data.position,
    data.value
FROM search_collections AS c
JOIN (
    VALUES
        ('release_versions', 0, 1001),
        ('release_versions', 1, 1002),
        ('release_versions', 2, 1002),
        ('release_versions', 3, 1002),
        ('release_versions', 4, 1005),
        ('release_versions', 5, 1007),
        ('release_versions', 6, 1007),
        ('release_versions', 7, 1010),
        ('response_times', 0, 120),
        ('response_times', 1, 120),
        ('response_times', 2, 135),
        ('response_times', 3, 150),
        ('response_times', 4, 150),
        ('response_times', 5, 150),
        ('response_times', 6, 180),
        ('response_times', 7, 220)
) AS data(collection_name, position, value)
    ON data.collection_name = c.collection_name;

-- PostgreSQL array-based implementations provide compact reusable search
-- functions. The array is assumed to be sorted by the caller.
CREATE OR REPLACE FUNCTION lower_bound(values integer[], target integer)
RETURNS integer
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    left_pos integer := 1;
    right_pos integer := COALESCE(array_length(values, 1), 0) + 1;
    middle integer;
BEGIN
    -- PostgreSQL arrays are 1-based. The returned result is converted
    -- to a zero-based logical insertion position.
    WHILE left_pos < right_pos LOOP
        middle := left_pos + (right_pos - left_pos) / 2;

        IF values[middle] < target THEN
            left_pos := middle + 1;
        ELSE
            right_pos := middle;
        END IF;
    END LOOP;

    RETURN left_pos - 1;
END;
$$;

CREATE OR REPLACE FUNCTION upper_bound(values integer[], target integer)
RETURNS integer
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    left_pos integer := 1;
    right_pos integer := COALESCE(array_length(values, 1), 0) + 1;
    middle integer;
BEGIN
    WHILE left_pos < right_pos LOOP
        middle := left_pos + (right_pos - left_pos) / 2;

        IF values[middle] <= target THEN
            left_pos := middle + 1;
        ELSE
            right_pos := middle;
        END IF;
    END LOOP;

    RETURN left_pos - 1;
END;
$$;

CREATE OR REPLACE FUNCTION binary_search_report(
    values integer[],
    target integer
)
RETURNS TABLE (
    lower_bound_position integer,
    upper_bound_position integer,
    first_occurrence_position integer,
    last_occurrence_position integer,
    occurrence_count integer,
    insertion_position integer
)
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    lb integer;
    ub integer;
BEGIN
    IF values IS NULL THEN
        RAISE EXCEPTION 'Search array cannot be NULL';
    END IF;

    lb := lower_bound(values, target);
    ub := upper_bound(values, target);

    lower_bound_position := lb;
    upper_bound_position := ub;
    insertion_position := lb;
    occurrence_count := ub - lb;

    IF occurrence_count = 0 THEN
        first_occurrence_position := NULL;
        last_occurrence_position := NULL;
    ELSE
        first_occurrence_position := lb;
        last_occurrence_position := ub - 1;
    END IF;

    RETURN NEXT;
END;
$$;

-- A materialized workflow table demonstrates how search results can be
-- recorded transactionally for later reporting.
CREATE OR REPLACE FUNCTION evaluate_query(p_query_id bigint)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
    collection_values integer[];
    target_value integer;
BEGIN
    SELECT
        array_agg(sv.value ORDER BY sv.position),
        sq.target
    INTO collection_values, target_value
    FROM search_queries AS sq
    JOIN search_values AS sv
        ON sv.collection_id = sq.collection_id
    WHERE sq.query_id = p_query_id
    GROUP BY sq.query_id, sq.target;

    IF collection_values IS NULL THEN
        RAISE EXCEPTION 'Query % refers to an empty or invalid collection', p_query_id;
    END IF;

    INSERT INTO search_results (
        query_id,
        lower_bound,
        upper_bound,
        first_occurrence,
        last_occurrence,
        occurrence_count,
        insertion_position
    )
    SELECT
        p_query_id,
        lower_bound_position,
        upper_bound_position,
        first_occurrence_position,
        last_occurrence_position,
        occurrence_count,
        insertion_position
    FROM binary_search_report(collection_values, target_value)
    ON CONFLICT (query_id) DO UPDATE
    SET lower_bound = EXCLUDED.lower_bound,
        upper_bound = EXCLUDED.upper_bound,
        first_occurrence = EXCLUDED.first_occurrence,
        last_occurrence = EXCLUDED.last_occurrence,
        occurrence_count = EXCLUDED.occurrence_count,
        insertion_position = EXCLUDED.insertion_position;
END;
$$;

-- Queries are created before evaluation so the complete operation can be
-- performed inside a transaction.
INSERT INTO search_queries (collection_id, target)
SELECT collection_id, target
FROM search_collections
CROSS JOIN (
    VALUES (999), (1002), (1004), (1007), (1011)
) AS targets(target)
WHERE collection_name = 'release_versions';

INSERT INTO search_queries (collection_id, target)
SELECT collection_id, target
FROM search_collections
CROSS JOIN (
    VALUES (119), (120), (150), (151), (300)
) AS targets(target)
WHERE collection_name = 'response_times';

DO $$
DECLARE
    query_record record;
BEGIN
    FOR query_record IN
        SELECT query_id
        FROM search_queries
        ORDER BY query_id
    LOOP
        PERFORM evaluate_query(query_record.query_id);
    END LOOP;
END;
$$;

-- Reporting view exposes the relationship between a target and its
-- duplicate range without duplicating search logic in every query.
CREATE OR REPLACE VIEW search_result_report AS
SELECT
    q.query_id,
    c.collection_name,
    q.target,
    r.lower_bound,
    r.upper_bound,
    r.first_occurrence,
    r.last_occurrence,
    r.occurrence_count,
    r.insertion_position,
    CASE
        WHEN r.occurrence_count = 0 THEN 'absent'
        WHEN r.occurrence_count = 1 THEN 'singleton'
        ELSE 'duplicate'
    END AS match_class
FROM search_queries AS q
JOIN search_collections AS c
    ON c.collection_id = q.collection_id
JOIN search_results AS r
    ON r.query_id = q.query_id;

-- Transactional validation demonstrates that inconsistent search results
-- can be rejected before they become durable.
BEGIN;

WITH checks AS (
    SELECT
        q.query_id,
        q.target,
        r.lower_bound,
        r.upper_bound,
        r.first_occurrence,
        r.last_occurrence,
        r.occurrence_count
    FROM search_queries AS q
    JOIN search_results AS r
        ON r.query_id = q.query_id
)
SELECT *
FROM checks
WHERE occurrence_count <> upper_bound - lower_bound
   OR (
        occurrence_count = 0
        AND (first_occurrence IS NOT NULL OR last_occurrence IS NOT NULL)
      )
   OR (
        occurrence_count > 0
        AND (
            first_occurrence <> lower_bound
            OR last_occurrence <> upper_bound - 1
        )
      )
ORDER BY query_id;

COMMIT;

-- Core retrieval, duplicate evaluation, insertion-position reporting,
-- and aggregation queries.
SELECT *
FROM search_result_report
ORDER BY collection_name, target;

SELECT
    collection_name,
    match_class,
    count(*) AS target_count,
    sum(occurrence_count) AS matched_values
FROM search_result_report
GROUP BY collection_name, match_class
ORDER BY collection_name, match_class;

-- Direct function evaluation for an independent array.
SELECT *
FROM binary_search_report(
    ARRAY[1, 2, 2, 2, 4, 4, 7, 9, 9],
    2
);

SELECT
    lower_bound(ARRAY[1, 2, 2, 2, 4, 4, 7], 3)
        AS insertion_before_4,
    upper_bound(ARRAY[1, 2, 2, 2, 4, 4, 7], 2)
        AS first_position_after_2;

-- Integrity check: every stored position must correspond to a contiguous
-- zero-based sequence. This query identifies structural corruption.
SELECT
    collection_id,
    count(*) AS value_count,
    min(position) AS minimum_position,
    max(position) AS maximum_position
FROM search_values
GROUP BY collection_id
HAVING min(position) <> 0
    OR max(position) <> count(*) - 1
ORDER BY collection_id;
