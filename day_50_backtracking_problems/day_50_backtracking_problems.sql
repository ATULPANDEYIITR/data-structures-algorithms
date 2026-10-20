DROP SCHEMA IF EXISTS backtracking_lab CASCADE;
CREATE SCHEMA backtracking_lab;
SET search_path = backtracking_lab, public;

-- A relational model for solving and auditing backtracking workloads.
-- PostgreSQL arrays are used for compact representation of ordered states,
-- while normalized tables represent the reusable problem and search metadata.

CREATE TABLE problem_types (
    problem_type_id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL
);

CREATE TABLE problems (
    problem_id BIGSERIAL PRIMARY KEY,
    problem_type_id BIGINT NOT NULL REFERENCES problem_types(problem_type_id),
    name TEXT NOT NULL,
    difficulty TEXT NOT NULL CHECK (difficulty IN ('easy', 'medium', 'hard')),
    input_size INTEGER NOT NULL CHECK (input_size >= 0),
    max_solutions INTEGER CHECK (max_solutions IS NULL OR max_solutions > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (problem_type_id, name)
);

CREATE TABLE search_runs (
    search_run_id BIGSERIAL PRIMARY KEY,
    problem_id BIGINT NOT NULL REFERENCES problems(problem_id),
    algorithm TEXT NOT NULL,
    status TEXT NOT NULL CHECK (
        status IN ('running', 'completed', 'no_solution', 'failed')
    ),
    nodes_explored BIGINT NOT NULL DEFAULT 0 CHECK (nodes_explored >= 0),
    solutions_found INTEGER NOT NULL DEFAULT 0 CHECK (solutions_found >= 0),
    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,
    CHECK (
        completed_at IS NULL
        OR completed_at >= started_at
    )
);

CREATE TABLE solution_sets (
    solution_set_id BIGSERIAL PRIMARY KEY,
    search_run_id BIGINT NOT NULL REFERENCES search_runs(search_run_id) ON DELETE CASCADE,
    solution_index INTEGER NOT NULL CHECK (solution_index > 0),
    solution_state JSONB NOT NULL,
    UNIQUE (search_run_id, solution_index)
);

CREATE TABLE sudoku_puzzles (
    puzzle_id BIGSERIAL PRIMARY KEY,
    problem_id BIGINT NOT NULL UNIQUE REFERENCES problems(problem_id),
    grid INTEGER[][] NOT NULL,
    CHECK (array_ndims(grid) = 2),
    CHECK (array_length(grid, 1) = 9),
    CHECK (array_length(grid, 2) = 9)
);

CREATE TABLE queens_boards (
    board_id BIGSERIAL PRIMARY KEY,
    problem_id BIGINT NOT NULL REFERENCES problems(problem_id),
    board_size INTEGER NOT NULL CHECK (board_size BETWEEN 1 AND 20),
    queen_columns INTEGER[] NOT NULL,
    UNIQUE (problem_id, queen_columns)
);

CREATE TABLE grid_maps (
    grid_id BIGSERIAL PRIMARY KEY,
    problem_id BIGINT NOT NULL UNIQUE REFERENCES problems(problem_id),
    rows_count INTEGER NOT NULL CHECK (rows_count > 0),
    columns_count INTEGER NOT NULL CHECK (columns_count > 0),
    cells INTEGER[][] NOT NULL,
    CHECK (array_ndims(cells) = 2)
);

CREATE TABLE grid_paths (
    path_id BIGSERIAL PRIMARY KEY,
    grid_id BIGINT NOT NULL REFERENCES grid_maps(grid_id) ON DELETE CASCADE,
    search_run_id BIGINT REFERENCES search_runs(search_run_id) ON DELETE SET NULL,
    path_number INTEGER NOT NULL CHECK (path_number > 0),
    coordinates JSONB NOT NULL,
    path_length INTEGER NOT NULL CHECK (path_length > 0),
    UNIQUE (grid_id, path_number)
);

CREATE TABLE validation_events (
    validation_event_id BIGSERIAL PRIMARY KEY,
    problem_id BIGINT NOT NULL REFERENCES problems(problem_id),
    event_type TEXT NOT NULL,
    passed BOOLEAN NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_search_runs_problem_status
    ON search_runs(problem_id, status);

CREATE INDEX idx_solution_sets_run
    ON solution_sets(search_run_id);

CREATE INDEX idx_validation_events_problem
    ON validation_events(problem_id, created_at DESC);

INSERT INTO problem_types (name, description) VALUES
    ('subsets', 'Include-or-exclude search over a collection.'),
    ('permutations', 'Position-selection search over unused elements.'),
    ('combinations', 'Ordered-index search for fixed-size selections.'),
    ('n_queens', 'Constraint search placing one queen per row.'),
    ('sudoku', 'Constraint search assigning legal digits to empty cells.'),
    ('path_finding', 'Grid search using visited-state constraints.');

INSERT INTO problems (
    problem_type_id, name, difficulty, input_size, max_solutions
)
SELECT problem_type_id, 'Feature Flag Subsets', 'easy', 4, 16
FROM problem_types WHERE name = 'subsets';

INSERT INTO problems (
    problem_type_id, name, difficulty, input_size, max_solutions
)
SELECT problem_type_id, 'Deployment Permutations', 'medium', 4, 24
FROM problem_types WHERE name = 'permutations';

INSERT INTO problems (
    problem_type_id, name, difficulty, input_size, max_solutions
)
SELECT problem_type_id, 'Release Team Combinations', 'easy', 6, 20
FROM problem_types WHERE name = 'combinations';

INSERT INTO problems (
    problem_type_id, name, difficulty, input_size, max_solutions
)
SELECT problem_type_id, 'Four Queens', 'medium', 4, 2
FROM problem_types WHERE name = 'n_queens';

INSERT INTO problems (
    problem_type_id, name, difficulty, input_size, max_solutions
)
SELECT problem_type_id, 'Classic Sudoku', 'hard', 81, 1
FROM problem_types WHERE name = 'sudoku';

INSERT INTO problems (
    problem_type_id, name, difficulty, input_size, max_solutions
)
SELECT problem_type_id, 'Warehouse Grid Route', 'medium', 25, 10
FROM problem_types WHERE name = 'path_finding';

INSERT INTO search_runs (
    problem_id, algorithm, status, nodes_explored, solutions_found, completed_at
)
SELECT problem_id, 'include-exclude', 'completed', 31, 16, CURRENT_TIMESTAMP
FROM problems WHERE name = 'Feature Flag Subsets';

INSERT INTO search_runs (
    problem_id, algorithm, status, nodes_explored, solutions_found, completed_at
)
SELECT problem_id, 'used-element permutation', 'completed', 65, 24, CURRENT_TIMESTAMP
FROM problems WHERE name = 'Deployment Permutations';

INSERT INTO search_runs (
    problem_id, algorithm, status, nodes_explored, solutions_found, completed_at
)
SELECT problem_id, 'index combination', 'completed', 42, 15, CURRENT_TIMESTAMP
FROM problems WHERE name = 'Release Team Combinations';

INSERT INTO search_runs (
    problem_id, algorithm, status, nodes_explored, solutions_found, completed_at
)
SELECT problem_id, 'column-diagonal constraints', 'completed', 17, 2, CURRENT_TIMESTAMP
FROM problems WHERE name = 'Four Queens';

INSERT INTO search_runs (
    problem_id, algorithm, status, nodes_explored, solutions_found, completed_at
)
SELECT problem_id, 'minimum-remaining-values sudoku', 'completed', 4208, 1, CURRENT_TIMESTAMP
FROM problems WHERE name = 'Classic Sudoku';

INSERT INTO search_runs (
    problem_id, algorithm, status, nodes_explored, solutions_found, completed_at
)
SELECT problem_id, 'visited-cell depth-first search', 'completed', 47, 3, CURRENT_TIMESTAMP
FROM problems WHERE name = 'Warehouse Grid Route';

INSERT INTO solution_sets (search_run_id, solution_index, solution_state)
SELECT
    search_run_id,
    value,
    jsonb_build_object(
        'selected_features',
        CASE value
            WHEN 1 THEN '[]'::jsonb
            WHEN 2 THEN '["audit_logging"]'::jsonb
            WHEN 3 THEN '["metrics"]'::jsonb
            WHEN 4 THEN '["audit_logging","metrics"]'::jsonb
            ELSE '["sample"]'::jsonb
        END
    )
FROM search_runs
WHERE algorithm = 'include-exclude'
  AND value IN (
      SELECT generate_series(1, LEAST(solutions_found, 4))
  );

INSERT INTO sudoku_puzzles (problem_id, grid)
SELECT
    problem_id,
    ARRAY[
        ARRAY[5,3,0,0,7,0,0,0,0],
        ARRAY[6,0,0,1,9,5,0,0,0],
        ARRAY[0,9,8,0,0,0,0,6,0],
        ARRAY[8,0,0,0,6,0,0,0,3],
        ARRAY[4,0,0,8,0,3,0,0,1],
        ARRAY[7,0,0,0,2,0,0,0,6],
        ARRAY[0,6,0,0,0,0,2,8,0],
        ARRAY[0,0,0,4,1,9,0,0,5],
        ARRAY[0,0,0,0,8,0,0,7,9]
    ]::INTEGER[][]
FROM problems
WHERE name = 'Classic Sudoku';

INSERT INTO queens_boards (problem_id, board_size, queen_columns)
SELECT
    problem_id,
    4,
    ARRAY[1,3,0,2]
FROM problems
WHERE name = 'Four Queens';

INSERT INTO queens_boards (problem_id, board_size, queen_columns)
SELECT
    problem_id,
    4,
    ARRAY[2,0,3,1]
FROM problems
WHERE name = 'Four Queens';

INSERT INTO grid_maps (
    problem_id,
    rows_count,
    columns_count,
    cells
)
SELECT
    problem_id,
    5,
    5,
    ARRAY[
        ARRAY[0,0,1,0,0],
        ARRAY[1,0,1,0,1],
        ARRAY[0,0,0,0,1],
        ARRAY[0,1,1,0,0],
        ARRAY[0,0,0,1,0]
    ]::INTEGER[][]
FROM problems
WHERE name = 'Warehouse Grid Route';

INSERT INTO grid_paths (
    grid_id,
    search_run_id,
    path_number,
    coordinates,
    path_length
)
SELECT
    g.grid_id,
    r.search_run_id,
    1,
    '[
        {"row":0,"column":0},
        {"row":0,"column":1},
        {"row":1,"column":1},
        {"row":2,"column":1},
        {"row":2,"column":2},
        {"row":2,"column":3},
        {"row":3,"column":3},
        {"row":3,"column":4},
        {"row":4,"column":4}
    ]'::jsonb,
    9
FROM grid_maps g
JOIN problems p ON p.problem_id = g.problem_id
JOIN search_runs r ON r.problem_id = p.problem_id
WHERE p.name = 'Warehouse Grid Route'
  AND r.algorithm = 'visited-cell depth-first search';

INSERT INTO validation_events (problem_id, event_type, passed, message)
SELECT
    problem_id,
    'sudoku-domain',
    TRUE,
    'All supplied Sudoku values are within the legal 0..9 domain.'
FROM problems
WHERE name = 'Classic Sudoku';

INSERT INTO validation_events (problem_id, event_type, passed, message)
SELECT
    problem_id,
    'n-queens-solution',
    TRUE,
    'Stored queen placements contain one queen per row and distinct columns.'
FROM problems
WHERE name = 'Four Queens';

-- A trigger maintains the aggregate solution count so that the run metadata
-- remains consistent when solution rows are inserted independently.
CREATE OR REPLACE FUNCTION refresh_solution_count()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE search_runs
    SET solutions_found = (
        SELECT COUNT(*)
        FROM solution_sets
        WHERE search_run_id = COALESCE(NEW.search_run_id, OLD.search_run_id)
    )
    WHERE search_run_id = COALESCE(NEW.search_run_id, OLD.search_run_id);

    RETURN COALESCE(NEW, OLD);
END;
$$;

CREATE TRIGGER trg_refresh_solution_count
AFTER INSERT OR DELETE ON solution_sets
FOR EACH ROW
EXECUTE FUNCTION refresh_solution_count();

-- Reject malformed path coordinates at the database boundary.
CREATE OR REPLACE FUNCTION validate_grid_path()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    grid_rows INTEGER;
    grid_columns INTEGER;
    coordinate JSONB;
BEGIN
    SELECT rows_count, columns_count
    INTO grid_rows, grid_columns
    FROM grid_maps
    WHERE grid_id = NEW.grid_id;

    IF grid_rows IS NULL THEN
        RAISE EXCEPTION 'Unknown grid_id %', NEW.grid_id;
    END IF;

    IF jsonb_typeof(NEW.coordinates) <> 'array' THEN
        RAISE EXCEPTION 'Path coordinates must be a JSON array';
    END IF;

    FOR coordinate IN
        SELECT value FROM jsonb_array_elements(NEW.coordinates)
    LOOP
        IF (coordinate->>'row')::INTEGER < 0
           OR (coordinate->>'row')::INTEGER >= grid_rows
           OR (coordinate->>'column')::INTEGER < 0
           OR (coordinate->>'column')::INTEGER >= grid_columns THEN
            RAISE EXCEPTION 'Path coordinate is outside grid %', NEW.grid_id;
        END IF;
    END LOOP;

    IF NEW.path_length <> jsonb_array_length(NEW.coordinates) THEN
        RAISE EXCEPTION 'path_length must match coordinate count';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_grid_path
BEFORE INSERT OR UPDATE ON grid_paths
FOR EACH ROW
EXECUTE FUNCTION validate_grid_path();

-- The following transaction demonstrates atomic recording of a search run
-- and its first solution.
BEGIN;

WITH selected_run AS (
    SELECT search_run_id
    FROM search_runs
    WHERE algorithm = 'include-exclude'
    ORDER BY search_run_id
    LIMIT 1
)
INSERT INTO solution_sets (search_run_id, solution_index, solution_state)
SELECT
    selected_run.search_run_id,
    100,
    '{"selected_features":["rate_limit","security_headers"]}'::jsonb
FROM selected_run
ON CONFLICT (search_run_id, solution_index) DO NOTHING;

UPDATE search_runs
SET status = 'completed',
    completed_at = CURRENT_TIMESTAMP
WHERE algorithm = 'include-exclude'
  AND status = 'completed';

COMMIT;

-- Evaluate which search runs have reached their configured solution cap.
WITH run_limits AS (
    SELECT
        r.search_run_id,
        p.name,
        p.max_solutions,
        r.solutions_found,
        r.nodes_explored,
        CASE
            WHEN p.max_solutions IS NULL THEN FALSE
            ELSE r.solutions_found >= p.max_solutions
        END AS reached_limit
    FROM search_runs r
    JOIN problems p ON p.problem_id = r.problem_id
)
SELECT *
FROM run_limits
ORDER BY search_run_id;

-- Identify runs with unusually high search effort per discovered solution.
SELECT
    p.name,
    r.algorithm,
    r.nodes_explored,
    r.solutions_found,
    ROUND(
        r.nodes_explored::NUMERIC /
        NULLIF(r.solutions_found, 0),
        2
    ) AS nodes_per_solution
FROM search_runs r
JOIN problems p ON p.problem_id = r.problem_id
ORDER BY nodes_per_solution DESC NULLS LAST;

-- Verify that stored N-Queens solutions have no repeated columns.
SELECT
    qb.board_id,
    p.name,
    qb.queen_columns,
    cardinality(qb.queen_columns) = qb.board_size AS one_per_row,
    cardinality(
        ARRAY(
            SELECT DISTINCT value
            FROM unnest(qb.queen_columns) AS value
        )
    ) = qb.board_size AS unique_columns
FROM queens_boards qb
JOIN problems p ON p.problem_id = qb.problem_id;

-- Report grid path quality and search metadata.
SELECT
    p.name AS problem,
    gp.path_number,
    gp.path_length,
    r.nodes_explored,
    jsonb_array_length(gp.coordinates) AS stored_coordinates
FROM grid_paths gp
JOIN grid_maps gm ON gm.grid_id = gp.grid_id
JOIN problems p ON p.problem_id = gm.problem_id
LEFT JOIN search_runs r ON r.search_run_id = gp.search_run_id
ORDER BY p.name, gp.path_number;

-- A view gives applications a stable merge-style eligibility equivalent:
-- a search run is complete, has at least one solution, and has not failed.
CREATE OR REPLACE VIEW v_search_eligibility AS
SELECT
    r.search_run_id,
    p.name AS problem,
    r.algorithm,
    r.status,
    r.solutions_found,
    r.nodes_explored,
    (
        r.status = 'completed'
        AND r.solutions_found > 0
        AND r.completed_at IS NOT NULL
    ) AS eligible
FROM search_runs r
JOIN problems p ON p.problem_id = r.problem_id;

SELECT *
FROM v_search_eligibility
ORDER BY search_run_id;
