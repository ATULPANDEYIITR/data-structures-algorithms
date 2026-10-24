DROP SCHEMA IF EXISTS advanced_binary_search CASCADE;
CREATE SCHEMA advanced_binary_search;
SET search_path TO advanced_binary_search;

-- A search_case stores the mathematical structure known by the
-- caller. The structure determines which binary-search invariant
-- is valid.
CREATE TYPE search_structure AS ENUM (
    'SORTED_ARRAY',
    'ROTATED_ARRAY',
    'ROTATED_DUPLICATES',
    'BITONIC_ARRAY',
    'GLOBAL_MATRIX',
    'ROW_COLUMN_MATRIX'
);

CREATE TABLE search_cases (
    case_id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    case_name        TEXT NOT NULL UNIQUE,
    structure        search_structure NOT NULL,
    target           INTEGER NOT NULL,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE search_values (
    case_id          BIGINT NOT NULL
        REFERENCES search_cases(case_id)
        ON DELETE CASCADE,
    position         INTEGER NOT NULL CHECK (position >= 0),
    row_number       INTEGER,
    column_number    INTEGER,
    value             INTEGER NOT NULL,
    PRIMARY KEY (case_id, position),
    CHECK (
        (row_number IS NULL AND column_number IS NULL)
        OR
        (row_number IS NOT NULL AND row_number >= 0
         AND column_number IS NOT NULL AND column_number >= 0)
    )
);

CREATE INDEX search_values_case_value_idx
    ON search_values(case_id, value);

CREATE INDEX search_values_matrix_position_idx
    ON search_values(case_id, row_number, column_number);

-- This view reconstructs a logical sequence and exposes whether a
-- value has a valid predecessor inside its search case.
CREATE VIEW ordered_values AS
SELECT
    sv.case_id,
    sv.position,
    sv.row_number,
    sv.column_number,
    sv.value,
    lag(sv.value) OVER (
        PARTITION BY sv.case_id
        ORDER BY sv.position
    ) AS previous_value
FROM search_values AS sv;

-- Seed realistic structures.
INSERT INTO search_cases
    (case_name, structure, target)
VALUES
    ('standard_sorted', 'SORTED_ARRAY', 17),
    ('rotated_unique', 'ROTATED_ARRAY', 8),
    ('rotated_duplicates', 'ROTATED_DUPLICATES', 0),
    ('bitonic_prices', 'BITONIC_ARRAY', 11),
    ('global_matrix', 'GLOBAL_MATRIX', 22),
    ('row_column_matrix', 'ROW_COLUMN_MATRIX', 9);

INSERT INTO search_values
    (case_id, position, value)
SELECT
    sc.case_id,
    x.position,
    x.value
FROM search_cases AS sc
JOIN LATERAL (
    VALUES
        ('standard_sorted', 0, 2),
        ('standard_sorted', 1, 5),
        ('standard_sorted', 2, 8),
        ('standard_sorted', 3, 12),
        ('standard_sorted', 4, 17),
        ('standard_sorted', 5, 21),
        ('standard_sorted', 6, 29),

        ('rotated_unique', 0, 13),
        ('rotated_unique', 1, 18),
        ('rotated_unique', 2, 25),
        ('rotated_unique', 3, 2),
        ('rotated_unique', 4, 8),
        ('rotated_unique', 5, 10),

        ('rotated_duplicates', 0, 2),
        ('rotated_duplicates', 1, 5),
        ('rotated_duplicates', 2, 6),
        ('rotated_duplicates', 3, 0),
        ('rotated_duplicates', 4, 0),
        ('rotated_duplicates', 5, 1),
        ('rotated_duplicates', 6, 2),

        ('bitonic_prices', 0, 2),
        ('bitonic_prices', 1, 5),
        ('bitonic_prices', 2, 9),
        ('bitonic_prices', 3, 14),
        ('bitonic_prices', 4, 19),
        ('bitonic_prices', 5, 16),
        ('bitonic_prices', 6, 11),
        ('bitonic_prices', 7, 4),

        ('global_matrix', 0, 1),
        ('global_matrix', 1, 3),
        ('global_matrix', 2, 5),
        ('global_matrix', 3, 7),
        ('global_matrix', 4, 10),
        ('global_matrix', 5, 12),
        ('global_matrix', 6, 14),
        ('global_matrix', 7, 16),
        ('global_matrix', 8, 20),
        ('global_matrix', 9, 22),
        ('global_matrix', 10, 24),
        ('global_matrix', 11, 26)
) AS x(case_name, position, value)
    ON x.case_name = sc.case_name;

INSERT INTO search_values
    (case_id, position, row_number, column_number, value)
SELECT
    sc.case_id,
    x.position,
    x.row_number,
    x.column_number,
    x.value
FROM search_cases AS sc
JOIN LATERAL (
    VALUES
        ('row_column_matrix', 0, 0, 0, 1),
        ('row_column_matrix', 1, 0, 1, 4),
        ('row_column_matrix', 2, 0, 2, 7),
        ('row_column_matrix', 3, 0, 3, 11),
        ('row_column_matrix', 4, 1, 0, 2),
        ('row_column_matrix', 5, 1, 1, 5),
        ('row_column_matrix', 6, 1, 2, 8),
        ('row_column_matrix', 7, 1, 3, 13),
        ('row_column_matrix', 8, 2, 0, 3),
        ('row_column_matrix', 9, 2, 1, 6),
        ('row_column_matrix', 10, 2, 2, 9),
        ('row_column_matrix', 11, 2, 3, 15),
        ('row_column_matrix', 12, 3, 0, 10),
        ('row_column_matrix', 13, 3, 1, 12),
        ('row_column_matrix', 14, 3, 2, 14),
        ('row_column_matrix', 15, 3, 3, 18)
) AS x(
    case_name,
    position,
    row_number,
    column_number,
    value
)
    ON x.case_name = sc.case_name;

-- Validation function for an ordinary non-decreasing sequence.
CREATE OR REPLACE FUNCTION validate_sorted_case(
    p_case_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    invalid_count INTEGER;
BEGIN
    SELECT count(*)
    INTO invalid_count
    FROM ordered_values
    WHERE case_id = p_case_id
      AND previous_value IS NOT NULL
      AND value < previous_value;

    RETURN invalid_count = 0;
END;
$$;

-- Return all occurrences of a target. This is the relational
-- counterpart of lower_bound/upper_bound range discovery.
CREATE OR REPLACE FUNCTION find_value_range(
    p_case_id BIGINT,
    p_target INTEGER
)
RETURNS TABLE (
    first_position INTEGER,
    last_position INTEGER
)
LANGUAGE sql
AS $$
    SELECT
        min(position)::INTEGER,
        max(position)::INTEGER
    FROM search_values
    WHERE case_id = p_case_id
      AND value = p_target;
$$;

-- Evaluate a globally sorted matrix by virtual one-dimensional
-- position. The matrix has four columns in this example, but the
-- function derives the column count from the stored coordinates.
CREATE OR REPLACE FUNCTION global_matrix_match(
    p_case_id BIGINT,
    p_target INTEGER
)
RETURNS TABLE (
    row_number INTEGER,
    column_number INTEGER,
    value INTEGER
)
LANGUAGE sql
AS $$
    SELECT
        sv.row_number,
        sv.column_number,
        sv.value
    FROM search_values AS sv
    WHERE sv.case_id = p_case_id
      AND sv.value = p_target
      AND sv.row_number IS NOT NULL
      AND sv.column_number IS NOT NULL
    ORDER BY sv.row_number, sv.column_number;
$$;

-- A materialized reporting view is appropriate when the same
-- structural checks are repeatedly inspected by administrators.
CREATE MATERIALIZED VIEW case_statistics AS
SELECT
    sc.case_id,
    sc.case_name,
    sc.structure,
    sc.target,
    count(sv.position) AS element_count,
    min(sv.value) AS minimum_value,
    max(sv.value) AS maximum_value,
    count(*) FILTER (
        WHERE sv.value = sc.target
    ) AS target_occurrences
FROM search_cases AS sc
LEFT JOIN search_values AS sv
    ON sv.case_id = sc.case_id
GROUP BY
    sc.case_id,
    sc.case_name,
    sc.structure,
    sc.target;

CREATE UNIQUE INDEX case_statistics_pk_idx
    ON case_statistics(case_id);

-- The trigger prevents impossible negative matrix coordinates and
-- ensures that matrix coordinates map consistently to positions.
CREATE OR REPLACE FUNCTION validate_matrix_coordinates()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.row_number IS NULL
       AND NEW.column_number IS NULL THEN
        RETURN NEW;
    END IF;

    IF NEW.row_number < 0
       OR NEW.column_number < 0 THEN
        RAISE EXCEPTION
            'Matrix coordinates cannot be negative';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER search_values_matrix_validation
BEFORE INSERT OR UPDATE ON search_values
FOR EACH ROW
EXECUTE FUNCTION validate_matrix_coordinates();

-- Retrieval and validation examples.
SELECT
    case_name,
    structure,
    target,
    element_count,
    minimum_value,
    maximum_value,
    target_occurrences
FROM case_statistics
ORDER BY case_id;

SELECT
    case_name,
    validate_sorted_case(case_id) AS non_decreasing
FROM search_cases
WHERE structure = 'SORTED_ARRAY';

SELECT *
FROM find_value_range(
    (SELECT case_id
     FROM search_cases
     WHERE case_name = 'rotated_duplicates'),
    0
);

SELECT *
FROM global_matrix_match(
    (SELECT case_id
     FROM search_cases
     WHERE case_name = 'global_matrix'),
    22
);

-- The ordered view exposes local ordering information useful when
-- checking assumptions before selecting a binary-search strategy.
SELECT
    sc.case_name,
    ov.position,
    ov.value,
    ov.previous_value
FROM search_cases AS sc
JOIN ordered_values AS ov
    ON ov.case_id = sc.case_id
WHERE sc.case_name IN (
    'standard_sorted',
    'bitonic_prices'
)
ORDER BY sc.case_name, ov.position;

-- Demonstrate transactional integrity: an invalid structural row is
-- rejected, and the transaction is rolled back without changing data.
BEGIN;

SAVEPOINT validation_test;

DO $$
BEGIN
    INSERT INTO search_values (
        case_id,
        position,
        row_number,
        column_number,
        value
    )
    VALUES (
        (
            SELECT case_id
            FROM search_cases
            WHERE case_name = 'global_matrix'
        ),
        100,
        -1,
        2,
        999
    );

    RAISE EXCEPTION
        'Expected matrix-coordinate validation to fail';
EXCEPTION
    WHEN OTHERS THEN
        IF SQLERRM =
            'Expected matrix-coordinate validation to fail'
        THEN
            RAISE;
        END IF;
END;
$$;

ROLLBACK TO SAVEPOINT validation_test;
COMMIT;

-- Refresh reporting state after any committed changes.
REFRESH MATERIALIZED VIEW case_statistics;

SELECT
    case_name,
    target_occurrences
FROM case_statistics
ORDER BY case_name;
