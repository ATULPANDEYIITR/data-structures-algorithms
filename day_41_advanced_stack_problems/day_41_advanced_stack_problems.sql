DROP SCHEMA IF EXISTS advanced_stack_lab CASCADE;
CREATE SCHEMA advanced_stack_lab;
SET search_path TO advanced_stack_lab;

-- The data model represents measurements and derived analyses produced by
-- monotonic-stack algorithms. PostgreSQL constraints protect the raw domain
-- from negative heights and malformed categorical values.

CREATE TABLE histogram_case (
    histogram_id BIGSERIAL PRIMARY KEY,
    case_name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL
);

CREATE TABLE histogram_bar (
    histogram_id BIGINT NOT NULL REFERENCES histogram_case(histogram_id)
        ON DELETE CASCADE,
    position INTEGER NOT NULL CHECK (position >= 0),
    height INTEGER NOT NULL CHECK (height >= 0),
    PRIMARY KEY (histogram_id, position)
);

CREATE INDEX idx_histogram_bar_height
    ON histogram_bar (histogram_id, height);

CREATE TABLE elevation_case (
    elevation_id BIGSERIAL PRIMARY KEY,
    case_name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL
);

CREATE TABLE elevation_point (
    elevation_id BIGINT NOT NULL REFERENCES elevation_case(elevation_id)
        ON DELETE CASCADE,
    position INTEGER NOT NULL CHECK (position >= 0),
    elevation INTEGER NOT NULL CHECK (elevation >= 0),
    PRIMARY KEY (elevation_id, position)
);

CREATE INDEX idx_elevation_point_elevation
    ON elevation_point (elevation_id, elevation);

CREATE TABLE stock_series (
    series_id BIGSERIAL PRIMARY KEY,
    series_name TEXT NOT NULL UNIQUE
);

CREATE TABLE stock_price (
    series_id BIGINT NOT NULL REFERENCES stock_series(series_id)
        ON DELETE CASCADE,
    trading_day INTEGER NOT NULL CHECK (trading_day >= 0),
    price NUMERIC(18, 4) NOT NULL CHECK (price >= 0),
    PRIMARY KEY (series_id, trading_day)
);

CREATE INDEX idx_stock_price_series_price
    ON stock_price (series_id, price);

CREATE TABLE expression_case (
    expression_id BIGSERIAL PRIMARY KEY,
    expression_text TEXT NOT NULL,
    expected_postfix TEXT,
    evaluation_value NUMERIC(30, 12)
);

CREATE TABLE binary_matrix_case (
    matrix_id BIGSERIAL PRIMARY KEY,
    case_name TEXT NOT NULL UNIQUE
);

CREATE TABLE binary_matrix_cell (
    matrix_id BIGINT NOT NULL REFERENCES binary_matrix_case(matrix_id)
        ON DELETE CASCADE,
    row_number INTEGER NOT NULL CHECK (row_number >= 0),
    column_number INTEGER NOT NULL CHECK (column_number >= 0),
    cell_value SMALLINT NOT NULL CHECK (cell_value IN (0, 1)),
    PRIMARY KEY (matrix_id, row_number, column_number)
);

CREATE INDEX idx_matrix_cell_coordinates
    ON binary_matrix_cell (matrix_id, row_number, column_number);

INSERT INTO histogram_case (case_name, description)
VALUES
    ('classic_histogram', 'Canonical largest-rectangle histogram'),
    ('flat_histogram', 'Equal-height bars exercise duplicate handling'),
    ('single_bar', 'Single-bar boundary case');

INSERT INTO histogram_bar (histogram_id, position, height)
SELECT histogram_id, v.position, v.height
FROM histogram_case h
JOIN (
    VALUES
        ('classic_histogram', 0, 2),
        ('classic_histogram', 1, 1),
        ('classic_histogram', 2, 5),
        ('classic_histogram', 3, 6),
        ('classic_histogram', 4, 2),
        ('classic_histogram', 5, 3),
        ('flat_histogram', 0, 4),
        ('flat_histogram', 1, 4),
        ('flat_histogram', 2, 4),
        ('single_bar', 0, 7)
) AS v(case_name, position, height)
ON h.case_name = v.case_name;

-- SQL cannot naturally reproduce the single-pass stack mutation without
-- procedural code, so the query below derives every possible contiguous
-- interval and applies the minimum-height rule. It is deliberately a
-- relational reference implementation against which a procedural monotonic
-- stack implementation can be validated.

WITH intervals AS (
    SELECT
        h.histogram_id,
        b1.position AS left_position,
        b2.position AS right_position
    FROM histogram_bar b1
    JOIN histogram_bar b2
      ON b2.histogram_id = b1.histogram_id
     AND b2.position >= b1.position
    JOIN histogram_case h
      ON h.histogram_id = b1.histogram_id
),
rectangle_candidates AS (
    SELECT
        i.histogram_id,
        i.left_position,
        i.right_position,
        MIN(b.height) AS minimum_height,
        (i.right_position - i.left_position + 1)
            * MIN(b.height) AS area
    FROM intervals i
    JOIN histogram_bar b
      ON b.histogram_id = i.histogram_id
     AND b.position BETWEEN i.left_position AND i.right_position
    GROUP BY
        i.histogram_id,
        i.left_position,
        i.right_position
),
ranked_rectangles AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY histogram_id
            ORDER BY area DESC, left_position, right_position
        ) AS ranking
    FROM rectangle_candidates
)
SELECT
    h.case_name,
    r.left_position,
    r.right_position,
    r.minimum_height,
    r.area
FROM ranked_rectangles r
JOIN histogram_case h
  ON h.histogram_id = r.histogram_id
WHERE r.ranking = 1
ORDER BY h.case_name;

INSERT INTO elevation_case (case_name, description)
VALUES
    ('classic_rainwater', 'Two-boundary trapping example'),
    ('flat_terrain', 'No water can be trapped on equal elevations');

INSERT INTO elevation_point (elevation_id, position, elevation)
SELECT elevation_id, v.position, v.elevation
FROM elevation_case e
JOIN (
    VALUES
        ('classic_rainwater', 0, 0),
        ('classic_rainwater', 1, 1),
        ('classic_rainwater', 2, 0),
        ('classic_rainwater', 3, 2),
        ('classic_rainwater', 4, 1),
        ('classic_rainwater', 5, 0),
        ('classic_rainwater', 6, 1),
        ('classic_rainwater', 7, 3),
        ('classic_rainwater', 8, 2),
        ('classic_rainwater', 9, 1),
        ('classic_rainwater', 10, 2),
        ('classic_rainwater', 11, 1),
        ('flat_terrain', 0, 3),
        ('flat_terrain', 1, 3),
        ('flat_terrain', 2, 3)
) AS v(case_name, position, elevation)
ON e.case_name = v.case_name;

-- For each position, the trapped amount is the smaller of the highest wall
-- on either side minus the current elevation. GREATEST(..., 0) prevents a
-- negative contribution at boundary or exposed positions.
WITH bounds AS (
    SELECT
        p.elevation_id,
        p.position,
        p.elevation,
        MAX(left_side.elevation) AS left_max,
        MAX(right_side.elevation) AS right_max
    FROM elevation_point p
    LEFT JOIN elevation_point left_side
      ON left_side.elevation_id = p.elevation_id
     AND left_side.position <= p.position
    LEFT JOIN elevation_point right_side
      ON right_side.elevation_id = p.elevation_id
     AND right_side.position >= p.position
    GROUP BY p.elevation_id, p.position, p.elevation
),
water AS (
    SELECT
        elevation_id,
        position,
        elevation,
        GREATEST(
            LEAST(left_max, right_max) - elevation,
            0
        ) AS trapped
    FROM bounds
)
SELECT
    e.case_name,
    SUM(w.trapped) AS trapped_units
FROM water w
JOIN elevation_case e
  ON e.elevation_id = w.elevation_id
GROUP BY e.case_name
ORDER BY e.case_name;

INSERT INTO stock_series (series_name)
VALUES ('daily_market_prices');

INSERT INTO stock_price (series_id, trading_day, price)
SELECT
    series_id,
    v.trading_day,
    v.price
FROM stock_series s
JOIN (
    VALUES
        (0, 100.0::numeric),
        (1, 80.0::numeric),
        (2, 60.0::numeric),
        (3, 70.0::numeric),
        (4, 60.0::numeric),
        (5, 75.0::numeric),
        (6, 85.0::numeric)
) AS v(trading_day, price)
ON TRUE
WHERE s.series_name = 'daily_market_prices';

-- A correlated query expresses the stock-span definition directly:
-- count consecutive earlier sessions whose price does not exceed today's
-- price until a strictly greater price is encountered.
WITH spans AS (
    SELECT
        current_day.trading_day,
        current_day.price,
        COUNT(*) FILTER (
            WHERE NOT EXISTS (
                SELECT 1
                FROM stock_price blocker
                WHERE blocker.series_id = current_day.series_id
                  AND blocker.trading_day < current_day.trading_day
                  AND blocker.trading_day > candidate.trading_day
                  AND blocker.price > current_day.price
            )
        ) AS span
    FROM stock_price current_day
    JOIN stock_price candidate
      ON candidate.series_id = current_day.series_id
     AND candidate.trading_day <= current_day.trading_day
     AND candidate.price <= current_day.price
    GROUP BY current_day.series_id,
             current_day.trading_day,
             current_day.price
)
SELECT *
FROM spans
ORDER BY trading_day;

INSERT INTO expression_case (
    expression_text,
    expected_postfix,
    evaluation_value
)
VALUES
    (
        '3 + 4 * 2 / (1 - 5) ^ 2',
        '3 4 2 * 1 5 - 2 ^ / +',
        3.5
    ),
    (
        'revenue - cost * tax',
        'revenue cost tax * -',
        920.0
    );

-- Binary matrices can be transformed row by row into histogram heights.
-- The recursive CTE calculates column heights for every row, after which
-- candidate rectangular regions can be evaluated relationally.
INSERT INTO binary_matrix_case (case_name)
VALUES ('classic_binary_matrix');

INSERT INTO binary_matrix_cell (
    matrix_id,
    row_number,
    column_number,
    cell_value
)
SELECT
    matrix_id,
    v.row_number,
    v.column_number,
    v.cell_value
FROM binary_matrix_case m
JOIN (
    VALUES
        (0, 0, 1),
        (0, 1, 0),
        (0, 2, 1),
        (0, 3, 0),
        (0, 4, 0),
        (1, 0, 1),
        (1, 1, 0),
        (1, 2, 1),
        (1, 3, 1),
        (1, 4, 1),
        (2, 0, 1),
        (2, 1, 1),
        (2, 2, 1),
        (2, 3, 1),
        (2, 4, 1),
        (3, 0, 1),
        (3, 1, 0),
        (3, 2, 0),
        (3, 3, 1),
        (3, 4, 0)
) AS v(row_number, column_number, cell_value)
ON TRUE
WHERE m.case_name = 'classic_binary_matrix';

WITH RECURSIVE matrix_heights AS (
    SELECT
        c.matrix_id,
        c.row_number,
        c.column_number,
        c.cell_value AS height
    FROM binary_matrix_cell c
    WHERE c.row_number = 0

    UNION ALL

    SELECT
        current.matrix_id,
        current.row_number,
        current.column_number,
        CASE
            WHEN current.cell_value = 1
                THEN previous.height + 1
            ELSE 0
        END AS height
    FROM (
        SELECT
            c.*,
            LAG(c.height) OVER (
                PARTITION BY c.matrix_id, c.column_number
                ORDER BY c.row_number
            ) AS previous_height
        FROM (
            SELECT
                matrix_id,
                row_number,
                column_number,
                cell_value
            FROM binary_matrix_cell
        ) c
    ) current
    JOIN matrix_heights previous
      ON previous.matrix_id = current.matrix_id
     AND previous.row_number = current.row_number - 1
     AND previous.column_number = current.column_number
    WHERE current.row_number > 0
),
row_histograms AS (
    SELECT
        matrix_id,
        row_number,
        MAX(height) AS tallest_column
    FROM matrix_heights
    GROUP BY matrix_id, row_number
)
SELECT
    m.case_name,
    r.row_number,
    r.tallest_column
FROM row_histograms r
JOIN binary_matrix_case m
  ON m.matrix_id = r.matrix_id
ORDER BY r.row_number;

-- PostgreSQL transaction behavior is useful when an application needs to
-- update related analytical data atomically.
BEGIN;

INSERT INTO histogram_case (case_name, description)
VALUES (
    'transactional_case',
    'Demonstrates atomic insertion of a histogram and its bars'
);

INSERT INTO histogram_bar (histogram_id, position, height)
SELECT histogram_id, 0, 3
FROM histogram_case
WHERE case_name = 'transactional_case';

INSERT INTO histogram_bar (histogram_id, position, height)
SELECT histogram_id, 1, 4
FROM histogram_case
WHERE case_name = 'transactional_case';

INSERT INTO histogram_bar (histogram_id, position, height)
SELECT histogram_id, 2, 2
FROM histogram_case
WHERE case_name = 'transactional_case';

COMMIT;

-- Constraint enforcement example. This statement is intentionally isolated
-- in a savepoint so the script remains executable after the expected error.
BEGIN;

SAVEPOINT invalid_height_test;

DO $$
BEGIN
    BEGIN
        INSERT INTO histogram_bar (
            histogram_id,
            position,
            height
        )
        VALUES (
            (
                SELECT histogram_id
                FROM histogram_case
                WHERE case_name = 'transactional_case'
            ),
            3,
            -10
        );
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'Negative histogram height rejected by CHECK constraint.';
    END;
END;
$$;

ROLLBACK TO SAVEPOINT invalid_height_test;
COMMIT;

-- Performance inspection for the indexed histogram lookup.
EXPLAIN
SELECT histogram_id, position, height
FROM histogram_bar
WHERE histogram_id = (
    SELECT histogram_id
    FROM histogram_case
    WHERE case_name = 'classic_histogram'
)
ORDER BY position;

-- A production-oriented view exposes the analytical input in stable order
-- without duplicating the underlying bar data.
CREATE OR REPLACE VIEW histogram_series AS
SELECT
    h.histogram_id,
    h.case_name,
    b.position,
    b.height
FROM histogram_case h
JOIN histogram_bar b
  ON b.histogram_id = h.histogram_id;

SELECT *
FROM histogram_series
ORDER BY histogram_id, position;
