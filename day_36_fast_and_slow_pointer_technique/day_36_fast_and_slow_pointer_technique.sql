DROP SCHEMA IF EXISTS fast_slow_pointer_lab CASCADE;
CREATE SCHEMA fast_slow_pointer_lab;
SET search_path TO fast_slow_pointer_lab;

-- The relational model stores a directed "next node" relationship.
-- A cycle exists when following next_node_id eventually returns to an
-- already-reached node. PostgreSQL recursive queries can expose such
-- structures, while the application implementations use Floyd's algorithm
-- to detect them with O(1) auxiliary pointer state.

CREATE TABLE pointer_list (
    list_id BIGSERIAL PRIMARY KEY,
    list_name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL
);

CREATE TABLE pointer_node (
    node_id BIGSERIAL PRIMARY KEY,
    list_id BIGINT NOT NULL REFERENCES pointer_list(list_id) ON DELETE CASCADE,
    position_hint INTEGER NOT NULL CHECK (position_hint >= 0),
    node_value TEXT NOT NULL,
    next_node_id BIGINT REFERENCES pointer_node(node_id),
    UNIQUE (list_id, position_hint),
    UNIQUE (list_id, node_id)
);

CREATE INDEX idx_pointer_node_list_position
    ON pointer_node (list_id, position_hint);

CREATE INDEX idx_pointer_node_next
    ON pointer_node (next_node_id);

CREATE TABLE cycle_analysis (
    analysis_id BIGSERIAL PRIMARY KEY,
    list_id BIGINT NOT NULL REFERENCES pointer_list(list_id) ON DELETE CASCADE,
    algorithm_name TEXT NOT NULL
        CHECK (algorithm_name = 'Floyd'),
    cycle_state TEXT NOT NULL
        CHECK (cycle_state IN ('ACYCLIC', 'CYCLIC')),
    meeting_node_id BIGINT REFERENCES pointer_node(node_id),
    entry_node_id BIGINT REFERENCES pointer_node(node_id),
    distance_to_entry INTEGER NOT NULL CHECK (distance_to_entry >= -1),
    cycle_length INTEGER NOT NULL CHECK (cycle_length >= 0),
    analyzed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- A list can have only one current analysis record in this demonstration.
CREATE UNIQUE INDEX uq_cycle_analysis_current_list
    ON cycle_analysis(list_id);

INSERT INTO pointer_list (list_name, description)
VALUES
    (
        'middle_search_even',
        'Even-length list used to demonstrate first and second middle positions'
    ),
    (
        'acyclic_processing_chain',
        'Linear event chain with no cycle'
    ),
    (
        'cyclic_processing_chain',
        'Processing chain whose tail points back into the middle'
    ),
    (
        'palindrome_history',
        'Symmetric node sequence used for palindrome analysis'
    ),
    (
        'duplicate_functional_graph',
        'Integer transition graph representing duplicate detection'
    );

-- Populate the even-length list.
INSERT INTO pointer_node (list_id, position_hint, node_value)
SELECT
    list_id,
    position_hint,
    node_value
FROM pointer_list p
CROSS JOIN (
    VALUES
        (0, '10'),
        (1, '20'),
        (2, '30'),
        (3, '40'),
        (4, '50'),
        (5, '60')
) AS values(position_hint, node_value)
WHERE p.list_name = 'middle_search_even';

-- The ordinary linear chain.
INSERT INTO pointer_node (list_id, position_hint, node_value)
SELECT
    list_id,
    position_hint,
    node_value
FROM pointer_list p
CROSS JOIN (
    VALUES
        (0, 'REQUESTED'),
        (1, 'VALIDATED'),
        (2, 'AUTHORIZED'),
        (3, 'PROCESSED'),
        (4, 'ARCHIVED')
) AS values(position_hint, node_value)
WHERE p.list_name = 'acyclic_processing_chain';

-- The cyclic chain.
INSERT INTO pointer_node (list_id, position_hint, node_value)
SELECT
    list_id,
    position_hint,
    node_value
FROM pointer_list p
CROSS JOIN (
    VALUES
        (0, 'EVENT_A'),
        (1, 'EVENT_B'),
        (2, 'EVENT_C'),
        (3, 'EVENT_D'),
        (4, 'EVENT_E'),
        (5, 'EVENT_F')
) AS values(position_hint, node_value)
WHERE p.list_name = 'cyclic_processing_chain';

-- A palindrome-like history.
INSERT INTO pointer_node (list_id, position_hint, node_value)
SELECT
    list_id,
    position_hint,
    node_value
FROM pointer_list p
CROSS JOIN (
    VALUES
        (0, 'OPEN'),
        (1, 'REVIEW'),
        (2, 'APPROVED'),
        (3, 'REVIEW'),
        (4, 'OPEN')
) AS values(position_hint, node_value)
WHERE p.list_name = 'palindrome_history';

-- The values correspond to a functional graph:
-- index 0 -> 1
-- index 1 -> 3
-- index 2 -> 4
-- index 3 -> 2
-- index 4 -> 2
--
-- The repeated destination 2 creates the cycle used by Floyd's duplicate
-- detection formulation.
INSERT INTO pointer_node (list_id, position_hint, node_value)
SELECT
    list_id,
    position_hint,
    node_value
FROM pointer_list p
CROSS JOIN (
    VALUES
        (0, '1'),
        (1, '3'),
        (2, '4'),
        (3, '2'),
        (4, '2')
) AS values(position_hint, node_value)
WHERE p.list_name = 'duplicate_functional_graph';

-- Establish next-node relationships for every list except the functional
-- graph where the value itself is the transition destination.
UPDATE pointer_node current_node
SET next_node_id = next_node.node_id
FROM pointer_node next_node
WHERE current_node.list_id = next_node.list_id
  AND next_node.position_hint = current_node.position_hint + 1
  AND current_node.position_hint < (
      SELECT MAX(position_hint)
      FROM pointer_node tail
      WHERE tail.list_id = current_node.list_id
  )
  AND current_node.list_id IN (
      SELECT list_id
      FROM pointer_list
      WHERE list_name IN (
          'middle_search_even',
          'acyclic_processing_chain',
          'cyclic_processing_chain',
          'palindrome_history'
      )
  );

-- Create the cycle:
-- EVENT_F -> EVENT_C
UPDATE pointer_node tail
SET next_node_id = entry.node_id
FROM pointer_list p
JOIN pointer_node entry
    ON entry.list_id = p.list_id
   AND entry.position_hint = 2
WHERE tail.list_id = p.list_id
  AND tail.position_hint = 5
  AND p.list_name = 'cyclic_processing_chain';

-- For the functional graph, node position i points to the position encoded
-- by node_value. This represents the array-as-function transformation used by
-- Floyd's duplicate algorithm.
UPDATE pointer_node source
SET next_node_id = target.node_id
FROM pointer_list p
JOIN pointer_node target
    ON target.list_id = p.list_id
   AND target.position_hint = CAST(source.node_value AS INTEGER)
WHERE source.list_id = p.list_id
  AND p.list_name = 'duplicate_functional_graph';

-- Inspect the physical graph.
SELECT
    p.list_name,
    n.position_hint,
    n.node_value,
    n.next_node_id
FROM pointer_list p
JOIN pointer_node n
    ON n.list_id = p.list_id
ORDER BY p.list_name, n.position_hint;

-- Recursive traversal is useful at the database layer for exposing cycles.
-- The path array prevents the recursive query from continuing indefinitely.
WITH RECURSIVE traversal AS (
    SELECT
        p.list_id,
        p.list_name,
        n.node_id,
        n.node_value,
        n.next_node_id,
        ARRAY[n.node_id]::BIGINT[] AS path,
        false AS cycle_detected,
        0 AS depth
    FROM pointer_list p
    JOIN pointer_node n
        ON n.list_id = p.list_id
    WHERE n.position_hint = 0

    UNION ALL

    SELECT
        t.list_id,
        t.list_name,
        next_node.node_id,
        next_node.node_value,
        next_node.next_node_id,
        t.path || next_node.node_id,
        next_node.node_id = ANY(t.path),
        t.depth + 1
    FROM traversal t
    JOIN pointer_node next_node
        ON next_node.node_id = t.next_node_id
    WHERE NOT t.cycle_detected
      AND t.depth < 1000
)
SELECT
    list_name,
    depth,
    node_value,
    cycle_detected,
    path
FROM traversal
ORDER BY list_name, depth;

-- Find the second middle of the even-length list by position.
-- SQL can calculate it directly because relational storage exposes positions.
-- The Python, C++, and Java implementations instead demonstrate why
-- fast/slow pointers are useful when positions or lengths are not available.
WITH ordered_nodes AS (
    SELECT
        n.*,
        COUNT(*) OVER (PARTITION BY list_id) AS list_length
    FROM pointer_node n
    WHERE list_id = (
        SELECT list_id
        FROM pointer_list
        WHERE list_name = 'middle_search_even'
    )
)
SELECT
    node_value AS second_middle
FROM ordered_nodes
WHERE position_hint = list_length / 2;

-- Find the first middle for the same even-length list.
WITH ordered_nodes AS (
    SELECT
        n.*,
        COUNT(*) OVER (PARTITION BY list_id) AS list_length
    FROM pointer_node n
    WHERE list_id = (
        SELECT list_id
        FROM pointer_list
        WHERE list_name = 'middle_search_even'
    )
)
SELECT
    node_value AS first_middle
FROM ordered_nodes
WHERE position_hint = (list_length - 1) / 2;

-- Detect a cyclic list using a recursive path.
WITH RECURSIVE walk AS (
    SELECT
        n.list_id,
        n.node_id,
        n.next_node_id,
        ARRAY[n.node_id]::BIGINT[] AS path,
        false AS repeated
    FROM pointer_node n
    WHERE n.position_hint = 0
      AND n.list_id = (
          SELECT list_id
          FROM pointer_list
          WHERE list_name = 'cyclic_processing_chain'
      )

    UNION ALL

    SELECT
        w.list_id,
        n.node_id,
        n.next_node_id,
        w.path || n.node_id,
        n.node_id = ANY(w.path)
    FROM walk w
    JOIN pointer_node n
        ON n.node_id = w.next_node_id
    WHERE NOT w.repeated
      AND cardinality(w.path) < 1000
)
SELECT
    CASE
        WHEN BOOL_OR(repeated) THEN 'CYCLIC'
        ELSE 'ACYCLIC'
    END AS cycle_state
FROM walk;

-- Identify the first repeated node in the cyclic processing chain.
WITH RECURSIVE walk AS (
    SELECT
        n.node_id,
        n.next_node_id,
        ARRAY[n.node_id]::BIGINT[] AS path,
        false AS repeated
    FROM pointer_node n
    WHERE n.position_hint = 0
      AND n.list_id = (
          SELECT list_id
          FROM pointer_list
          WHERE list_name = 'cyclic_processing_chain'
      )

    UNION ALL

    SELECT
        n.node_id,
        n.next_node_id,
        w.path || n.node_id,
        n.node_id = ANY(w.path)
    FROM walk w
    JOIN pointer_node n
        ON n.node_id = w.next_node_id
    WHERE NOT w.repeated
      AND cardinality(w.path) < 1000
)
SELECT
    n.node_value AS repeated_node
FROM walk w
JOIN pointer_node n
    ON n.node_id = w.node_id
WHERE w.repeated
LIMIT 1;

-- Validate that a graph does not contain a node pointing to itself.
SELECT
    p.list_name,
    n.node_id,
    n.node_value
FROM pointer_list p
JOIN pointer_node n
    ON n.list_id = p.list_id
WHERE n.node_id = n.next_node_id;

-- A database-level constraint cannot by itself express arbitrary graph
-- acyclicity with a normal CHECK constraint because CHECK expressions cannot
-- safely perform recursive graph traversal. This distinction is important:
-- relational integrity constraints protect local relationships, while a
-- graph-cycle invariant requires recursive analysis or application logic.

-- Store a completed Floyd analysis for the cyclic list.
INSERT INTO cycle_analysis (
    list_id,
    algorithm_name,
    cycle_state,
    meeting_node_id,
    entry_node_id,
    distance_to_entry,
    cycle_length
)
SELECT
    p.list_id,
    'Floyd',
    'CYCLIC',
    meeting.node_id,
    entry.node_id,
    2,
    3
FROM pointer_list p
JOIN pointer_node meeting
    ON meeting.list_id = p.list_id
   AND meeting.position_hint = 5
JOIN pointer_node entry
    ON entry.list_id = p.list_id
   AND entry.position_hint = 2
WHERE p.list_name = 'cyclic_processing_chain';

-- Demonstrate the recorded analysis.
SELECT
    p.list_name,
    c.algorithm_name,
    c.cycle_state,
    meeting.node_value AS meeting_value,
    entry.node_value AS entry_value,
    c.distance_to_entry,
    c.cycle_length,
    c.analyzed_at
FROM cycle_analysis c
JOIN pointer_list p
    ON p.list_id = c.list_id
LEFT JOIN pointer_node meeting
    ON meeting.node_id = c.meeting_node_id
LEFT JOIN pointer_node entry
    ON entry.node_id = c.entry_node_id;

-- Transactional repair of the cycle.
-- The update changes only the final edge of the cyclic chain, making the
-- formerly cyclic sequence linear.
BEGIN;

UPDATE pointer_node tail
SET next_node_id = NULL
FROM pointer_list p
WHERE tail.list_id = p.list_id
  AND p.list_name = 'cyclic_processing_chain'
  AND tail.position_hint = 5;

UPDATE cycle_analysis
SET cycle_state = 'ACYCLIC',
    meeting_node_id = NULL,
    entry_node_id = NULL,
    distance_to_entry = -1,
    cycle_length = 0,
    analyzed_at = CURRENT_TIMESTAMP
WHERE list_id = (
    SELECT list_id
    FROM pointer_list
    WHERE list_name = 'cyclic_processing_chain'
);

COMMIT;

-- Verify the repaired chain.
WITH RECURSIVE walk AS (
    SELECT
        n.node_id,
        n.node_value,
        n.next_node_id,
        ARRAY[n.node_id]::BIGINT[] AS path
    FROM pointer_node n
    WHERE n.position_hint = 0
      AND n.list_id = (
          SELECT list_id
          FROM pointer_list
          WHERE list_name = 'cyclic_processing_chain'
      )

    UNION ALL

    SELECT
        n.node_id,
        n.node_value,
        n.next_node_id,
        w.path || n.node_id
    FROM walk w
    JOIN pointer_node n
        ON n.node_id = w.next_node_id
    WHERE NOT n.node_id = ANY(w.path)
)
SELECT
    node_value,
    next_node_id
FROM walk
ORDER BY cardinality(path);

-- The SQL model intentionally distinguishes:
--   * next_node_id: the structural relationship
--   * recursive traversal: database-level graph inspection
--   * cycle_analysis: persisted algorithm results
--   * application-level Floyd detection: O(1) auxiliary memory
--
-- This separation prevents the relational model from pretending that a
-- recursive graph invariant is equivalent to an ordinary foreign-key rule.
