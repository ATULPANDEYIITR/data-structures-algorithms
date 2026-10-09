DROP SCHEMA IF EXISTS stack_applications CASCADE;
CREATE SCHEMA stack_applications;
SET search_path TO stack_applications;

-- ---------------------------------------------------------------------------
-- Stack Applications Relational Model
-- ---------------------------------------------------------------------------
-- The schema represents four distinct uses of stacks:
-- nested delimiter validation, expression evaluation, function-call frames,
-- and document history with separate undo and redo timelines.
-- PostgreSQL is used because identity columns, JSONB, arrays, constraints,
-- CTEs, and transactional behavior provide a compact executable model.

CREATE TABLE expressions (
    expression_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    expression_text TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (btrim(expression_text) <> '')
);

CREATE TABLE expression_evaluations (
    evaluation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    expression_id BIGINT NOT NULL REFERENCES expressions(expression_id),
    postfix_tokens TEXT[] NOT NULL,
    result_numeric NUMERIC,
    evaluation_status TEXT NOT NULL,
    error_message TEXT,
    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (
        evaluation_status IN ('SUCCESS', 'FAILED')
    ),
    CHECK (
        (evaluation_status = 'SUCCESS' AND error_message IS NULL)
        OR
        (evaluation_status = 'FAILED' AND error_message IS NOT NULL)
    )
);

CREATE INDEX idx_expression_evaluations_expression
    ON expression_evaluations(expression_id);

-- ---------------------------------------------------------------------------
-- Function Call Simulation
-- ---------------------------------------------------------------------------

CREATE TABLE call_sessions (
    session_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    session_name TEXT NOT NULL UNIQUE,
    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMPTZ,
    CHECK (btrim(session_name) <> ''),
    CHECK (ended_at IS NULL OR ended_at >= started_at)
);

CREATE TABLE call_frames (
    frame_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    session_id BIGINT NOT NULL REFERENCES call_sessions(session_id)
        ON DELETE CASCADE,
    parent_frame_id BIGINT REFERENCES call_frames(frame_id),
    stack_depth INTEGER NOT NULL CHECK (stack_depth >= 0),
    function_name TEXT NOT NULL,
    arguments JSONB NOT NULL DEFAULT '{}'::jsonb,
    local_variables JSONB NOT NULL DEFAULT '{}'::jsonb,
    entered_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    returned_at TIMESTAMPTZ,
    return_value JSONB,
    CHECK (btrim(function_name) <> ''),
    CHECK (returned_at IS NULL OR returned_at >= entered_at)
);

CREATE INDEX idx_call_frames_session_depth
    ON call_frames(session_id, stack_depth DESC);

CREATE INDEX idx_call_frames_active
    ON call_frames(session_id, returned_at)
    WHERE returned_at IS NULL;

-- ---------------------------------------------------------------------------
-- Document History
-- ---------------------------------------------------------------------------

CREATE TABLE documents (
    document_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    document_name TEXT NOT NULL UNIQUE,
    current_content TEXT NOT NULL DEFAULT '',
    current_version INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (current_version >= 0)
);

CREATE TABLE document_history (
    history_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    document_id BIGINT NOT NULL REFERENCES documents(document_id)
        ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    history_action TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (
        history_action IN ('EDIT', 'UNDO', 'REDO')
    ),
    UNIQUE (document_id, version_number)
);

CREATE INDEX idx_document_history_lookup
    ON document_history(document_id, version_number DESC);

-- ---------------------------------------------------------------------------
-- Delimiter Validation
-- ---------------------------------------------------------------------------

CREATE TABLE delimiter_checks (
    check_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    input_text TEXT NOT NULL,
    is_balanced BOOLEAN NOT NULL,
    error_position INTEGER,
    error_message TEXT,
    checked_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (btrim(input_text) <> ''),
    CHECK (error_position IS NULL OR error_position >= 0)
);

-- ---------------------------------------------------------------------------
-- Sample Expression Data
-- ---------------------------------------------------------------------------

INSERT INTO expressions (expression_text)
VALUES
    ('3 + 4 * 2'),
    ('(3 + 4) * 2'),
    ('20 / (2 + 3)'),
    ('10 / 0'),
    ('2 ^ 3 ^ 2');

INSERT INTO expression_evaluations
    (expression_id, postfix_tokens, result_numeric, evaluation_status, error_message)
SELECT
    expression_id,
    CASE expression_text
        WHEN '3 + 4 * 2' THEN ARRAY['3','4','2','*','+']
        WHEN '(3 + 4) * 2' THEN ARRAY['3','4','+','2','*']
        WHEN '20 / (2 + 3)' THEN ARRAY['20','2','3','+','/']
        WHEN '10 / 0' THEN ARRAY['10','0','/']
        WHEN '2 ^ 3 ^ 2' THEN ARRAY['2','3','2','^','^']
    END,
    CASE expression_text
        WHEN '3 + 4 * 2' THEN 11
        WHEN '(3 + 4) * 2' THEN 14
        WHEN '20 / (2 + 3)' THEN 4
        WHEN '2 ^ 3 ^ 2' THEN 512
        ELSE NULL
    END,
    CASE
        WHEN expression_text = '10 / 0' THEN 'FAILED'
        ELSE 'SUCCESS'
    END,
    CASE
        WHEN expression_text = '10 / 0'
        THEN 'Division by zero'
        ELSE NULL
    END
FROM expressions;

-- ---------------------------------------------------------------------------
-- Sample Function Call Stack
-- ---------------------------------------------------------------------------

INSERT INTO call_sessions (session_name)
VALUES ('request-2048');

INSERT INTO call_frames (
    session_id,
    parent_frame_id,
    stack_depth,
    function_name,
    arguments,
    local_variables
)
SELECT
    session_id,
    NULL,
    0,
    'main',
    '{"request_id":"REQ-2048"}',
    '{"authenticated":true}'
FROM call_sessions
WHERE session_name = 'request-2048';

INSERT INTO call_frames (
    session_id,
    parent_frame_id,
    stack_depth,
    function_name,
    arguments,
    local_variables
)
SELECT
    child_session.session_id,
    parent.frame_id,
    1,
    'process_request',
    '{"request_id":"REQ-2048"}',
    '{"route":"/calculate"}'
FROM call_sessions child_session
JOIN call_frames parent
    ON parent.session_id = child_session.session_id
WHERE child_session.session_name = 'request-2048'
  AND parent.function_name = 'main';

INSERT INTO call_frames (
    session_id,
    parent_frame_id,
    stack_depth,
    function_name,
    arguments,
    local_variables
)
SELECT
    child_session.session_id,
    parent.frame_id,
    2,
    'evaluate_expression',
    '{"expression":"3 * (4 + 2)"}',
    '{"operator_count":2}'
FROM call_sessions child_session
JOIN call_frames parent
    ON parent.session_id = child_session.session_id
WHERE child_session.session_name = 'request-2048'
  AND parent.function_name = 'process_request';

-- The deepest active frame represents the top of the simulated call stack.
SELECT
    session_id,
    function_name,
    stack_depth,
    arguments
FROM call_frames
WHERE returned_at IS NULL
ORDER BY stack_depth DESC
LIMIT 1;

-- ---------------------------------------------------------------------------
-- Undo / Redo History
-- ---------------------------------------------------------------------------

INSERT INTO documents (document_name, current_content, current_version)
VALUES (
    'expression-notes',
    'Stack applications',
    3
);

INSERT INTO document_history
    (document_id, version_number, content, history_action)
SELECT
    document_id,
    1,
    'Stack',
    'EDIT'
FROM documents
WHERE document_name = 'expression-notes';

INSERT INTO document_history
    (document_id, version_number, content, history_action)
SELECT
    document_id,
    2,
    'Stack applications',
    'EDIT'
FROM documents
WHERE document_name = 'expression-notes';

INSERT INTO document_history
    (document_id, version_number, content, history_action)
SELECT
    document_id,
    3,
    'Stack applications',
    'EDIT'
FROM documents
WHERE document_name = 'expression-notes';

-- The latest version is the current state. Earlier versions form the
-- recoverable undo history. A production application would normally update
-- documents and append history in one transaction.
SELECT
    d.document_name,
    d.current_version,
    d.current_content,
    h.version_number,
    h.history_action,
    h.content
FROM documents d
JOIN document_history h
    ON h.document_id = d.document_id
WHERE d.document_name = 'expression-notes'
ORDER BY h.version_number;

-- ---------------------------------------------------------------------------
-- Delimiter Validation Records
-- ---------------------------------------------------------------------------

INSERT INTO delimiter_checks (
    input_text,
    is_balanced,
    error_position,
    error_message
)
VALUES
    ('([{}])', TRUE, NULL, NULL),
    ('function(a[2], {value: 3})', TRUE, NULL, NULL),
    ('([)]', FALSE, 2, 'Closing bracket does not match the top stack entry'),
    ('{missing', FALSE, 0, 'Opening delimiter remains on the stack');

-- ---------------------------------------------------------------------------
-- Analytical Queries
-- ---------------------------------------------------------------------------

-- Successful and failed expression evaluations remain distinct from the
-- expression itself, allowing repeated evaluation attempts to be audited.
SELECT
    e.expression_text,
    ee.evaluation_status,
    ee.result_numeric,
    ee.error_message
FROM expressions e
JOIN expression_evaluations ee
    ON ee.expression_id = e.expression_id
ORDER BY e.expression_id;

-- Active call frames reveal the current stack from deepest to shallowest.
SELECT
    cs.session_name,
    cf.stack_depth,
    cf.function_name,
    cf.arguments
FROM call_sessions cs
JOIN call_frames cf
    ON cf.session_id = cs.session_id
WHERE cf.returned_at IS NULL
ORDER BY cs.session_id, cf.stack_depth DESC;

-- Find documents with a meaningful history depth.
SELECT
    d.document_name,
    COUNT(h.history_id) AS recorded_versions,
    MAX(h.version_number) AS latest_recorded_version
FROM documents d
LEFT JOIN document_history h
    ON h.document_id = d.document_id
GROUP BY d.document_id, d.document_name
HAVING COUNT(h.history_id) > 1;

-- ---------------------------------------------------------------------------
-- Transactional Undo Example
-- ---------------------------------------------------------------------------
-- The database cannot infer an application's in-memory stack, but it can
-- guarantee that a state update and its history record succeed or fail
-- together.

BEGIN;

UPDATE documents
SET
    current_content = 'Stack applications with transactional history',
    current_version = current_version + 1,
    updated_at = CURRENT_TIMESTAMP
WHERE document_name = 'expression-notes';

INSERT INTO document_history (
    document_id,
    version_number,
    content,
    history_action
)
SELECT
    document_id,
    current_version,
    current_content,
    'EDIT'
FROM documents
WHERE document_name = 'expression-notes';

COMMIT;

-- ---------------------------------------------------------------------------
-- Integrity Failure Demonstration
-- ---------------------------------------------------------------------------
-- The following statement is intentionally commented out because it would
-- violate the foreign-key relationship:
--
-- INSERT INTO call_frames (
--     session_id, stack_depth, function_name
-- )
-- VALUES (999999, 0, 'invalid_function');
--
-- The database rejects this state rather than allowing an orphan frame.
