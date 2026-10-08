DROP SCHEMA IF EXISTS stack_learning CASCADE;
CREATE SCHEMA stack_learning;

SET search_path TO stack_learning;

-- PostgreSQL's identity columns provide database-generated identifiers.
-- The model separates a stack container from its individual elements so
-- insertion order and LIFO removal order can be queried explicitly.

CREATE TABLE stacks (
    stack_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    stack_name TEXT NOT NULL UNIQUE,
    implementation_type TEXT NOT NULL
        CHECK (implementation_type IN ('ARRAY', 'LINKED_LIST')),
    capacity INTEGER
        CHECK (capacity IS NULL OR capacity > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE stack_items (
    item_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    stack_id BIGINT NOT NULL REFERENCES stacks(stack_id) ON DELETE CASCADE,
    item_value TEXT NOT NULL,
    push_sequence BIGINT NOT NULL,
    pushed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    popped_at TIMESTAMPTZ,
    CHECK (push_sequence > 0),
    CHECK (popped_at IS NULL OR popped_at >= pushed_at),
    UNIQUE (stack_id, push_sequence)
);

CREATE INDEX idx_stack_items_lifo
    ON stack_items (stack_id, push_sequence DESC);

CREATE INDEX idx_stack_items_active
    ON stack_items (stack_id, popped_at)
    WHERE popped_at IS NULL;

-- A stack cannot contain more active items than its declared capacity.
-- This trigger makes the capacity rule enforceable even when data is inserted
-- outside an application service.

CREATE OR REPLACE FUNCTION enforce_stack_capacity()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    stack_capacity INTEGER;
    active_count INTEGER;
BEGIN
    SELECT capacity
    INTO stack_capacity
    FROM stacks
    WHERE stack_id = NEW.stack_id
    FOR UPDATE;

    IF stack_capacity IS NULL THEN
        RETURN NEW;
    END IF;

    SELECT COUNT(*)
    INTO active_count
    FROM stack_items
    WHERE stack_id = NEW.stack_id
      AND popped_at IS NULL;

    IF active_count >= stack_capacity THEN
        RAISE EXCEPTION
            'Stack % has reached capacity %',
            NEW.stack_id,
            stack_capacity;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_enforce_stack_capacity
BEFORE INSERT ON stack_items
FOR EACH ROW
EXECUTE FUNCTION enforce_stack_capacity();

CREATE OR REPLACE VIEW active_stack_items AS
SELECT
    s.stack_id,
    s.stack_name,
    s.implementation_type,
    s.capacity,
    i.item_id,
    i.item_value,
    i.push_sequence,
    i.pushed_at
FROM stacks s
JOIN stack_items i
  ON i.stack_id = s.stack_id
WHERE i.popped_at IS NULL;

INSERT INTO stacks (stack_name, implementation_type, capacity)
VALUES
    ('browser-history', 'ARRAY', 10),
    ('job-retry-stack', 'LINKED_LIST', 4),
    ('expression-stack', 'ARRAY', NULL);

INSERT INTO stack_items (stack_id, item_value, push_sequence)
SELECT stack_id, item_value, push_sequence
FROM (
    VALUES
        ((SELECT stack_id FROM stacks WHERE stack_name = 'browser-history'),
         'home', 1),
        ((SELECT stack_id FROM stacks WHERE stack_name = 'browser-history'),
         'products', 2),
        ((SELECT stack_id FROM stacks WHERE stack_name = 'browser-history'),
         'checkout', 3),
        ((SELECT stack_id FROM stacks WHERE stack_name = 'job-retry-stack'),
         'retry-payment', 1),
        ((SELECT stack_id FROM stacks WHERE stack_name = 'job-retry-stack'),
         'retry-invoice', 2),
        ((SELECT stack_id FROM stacks WHERE stack_name = 'job-retry-stack'),
         'retry-notification', 3),
        ((SELECT stack_id FROM stacks WHERE stack_name = 'expression-stack'),
         '(', 1),
        ((SELECT stack_id FROM stacks WHERE stack_name = 'expression-stack'),
         '[', 2),
        ((SELECT stack_id FROM stacks WHERE stack_name = 'expression-stack'),
         '{', 3)
) AS seed(stack_id, item_value, push_sequence);

-- The newest active element is the LIFO top.
SELECT
    stack_name,
    item_value AS top_item,
    push_sequence
FROM active_stack_items
WHERE push_sequence = (
    SELECT MAX(i2.push_sequence)
    FROM stack_items i2
    WHERE i2.stack_id = active_stack_items.stack_id
      AND i2.popped_at IS NULL
)
ORDER BY stack_name;

-- The same ordering exposes the complete stack from top to bottom.
SELECT
    stack_name,
    item_value,
    push_sequence
FROM active_stack_items
ORDER BY stack_name, push_sequence DESC;

-- Simulate a pop operation inside a transaction. The UPDATE selects the
-- current maximum push sequence, which represents the top of the stack.
BEGIN;

WITH top_item AS (
    SELECT item_id
    FROM stack_items
    WHERE stack_id = (
        SELECT stack_id
        FROM stacks
        WHERE stack_name = 'browser-history'
    )
      AND popped_at IS NULL
    ORDER BY push_sequence DESC
    LIMIT 1
    FOR UPDATE
)
UPDATE stack_items
SET popped_at = CURRENT_TIMESTAMP
WHERE item_id IN (SELECT item_id FROM top_item);

COMMIT;

-- Confirm that checkout has been removed and products is now the top.
SELECT
    stack_name,
    item_value,
    push_sequence
FROM active_stack_items
WHERE stack_name = 'browser-history'
ORDER BY push_sequence DESC;

-- Capacity enforcement demonstration.
-- The job-retry-stack has capacity four and already contains three items.
INSERT INTO stack_items (
    stack_id,
    item_value,
    push_sequence
)
VALUES (
    (SELECT stack_id FROM stacks WHERE stack_name = 'job-retry-stack'),
    'retry-webhook',
    4
);

-- This statement intentionally demonstrates a rejected database operation.
-- PostgreSQL raises an exception because the stack is now at capacity.
-- It is kept commented so the complete script remains executable.
--
-- INSERT INTO stack_items (
--     stack_id, item_value, push_sequence
-- )
-- VALUES (
--     (SELECT stack_id FROM stacks WHERE stack_name = 'job-retry-stack'),
--     'retry-cache',
--     5
-- );

-- Aggregate query showing active depth for every stack.
SELECT
    s.stack_name,
    s.implementation_type,
    s.capacity,
    COUNT(i.item_id) AS active_depth,
    MAX(i.push_sequence) AS top_sequence
FROM stacks s
LEFT JOIN stack_items i
  ON i.stack_id = s.stack_id
 AND i.popped_at IS NULL
GROUP BY
    s.stack_id,
    s.stack_name,
    s.implementation_type,
    s.capacity
ORDER BY s.stack_name;

-- Historical query: every item records whether and when it was popped.
SELECT
    s.stack_name,
    i.item_value,
    i.push_sequence,
    i.pushed_at,
    i.popped_at,
    CASE
        WHEN i.popped_at IS NULL THEN 'ACTIVE'
        ELSE 'POPPED'
    END AS state
FROM stacks s
JOIN stack_items i ON i.stack_id = s.stack_id
ORDER BY s.stack_name, i.push_sequence;

-- Integrity examples:
-- * stack_id foreign keys prevent orphaned stack elements.
-- * push_sequence must be positive.
-- * duplicate sequence numbers within one stack are rejected.
-- * capacity is enforced by the trigger.
-- * the partial index accelerates queries for currently active elements.
