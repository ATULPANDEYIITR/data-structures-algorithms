/*
===============================================================================
TRIE INTRODUCTION: POSTGRESQL PREFIX TREE DATABASE
===============================================================================

Domain:
A searchable enterprise product and command catalogue.

Relational model:
dictionary
    |
    +---- trie_node
              |
              +---- parent_node_id
              |
              +---- character transition
              |
              +---- terminal word indicator
              |
              +---- word frequency

Features:
- PostgreSQL schema and relational constraints
- Root-node management
- Character-level transitions
- Unique parent-character relationships
- Word insertion
- Exact searching
- Prefix searching
- Recursive autocomplete
- Word deletion
- Frequency tracking
- Statistics and reporting
- Indexes
- Trigger-based integrity validation
- Transaction examples

PostgreSQL 14+
*/

CREATE SCHEMA IF NOT EXISTS trie_lab;

SET search_path TO trie_lab, public;

-- ============================================================================
-- 1. DICTIONARY
-- ============================================================================

CREATE TABLE IF NOT EXISTS dictionary (
    dictionary_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    dictionary_name VARCHAR(100) NOT NULL UNIQUE,

    description TEXT NOT NULL DEFAULT '',

    case_sensitive BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT dictionary_name_not_empty
        CHECK (length(trim(dictionary_name)) > 0)
);

-- ============================================================================
-- 2. TRIE NODES
-- ============================================================================

CREATE TABLE IF NOT EXISTS trie_node (
    node_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    dictionary_id BIGINT NOT NULL
        REFERENCES dictionary(dictionary_id)
        ON DELETE CASCADE,

    parent_node_id BIGINT,

    edge_character TEXT,

    is_terminal BOOLEAN NOT NULL DEFAULT FALSE,

    frequency INTEGER NOT NULL DEFAULT 0,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT node_parent_fk
        FOREIGN KEY (parent_node_id)
        REFERENCES trie_node(node_id)
        ON DELETE CASCADE,

    CONSTRAINT valid_edge_character
        CHECK (
            (parent_node_id IS NULL AND edge_character IS NULL)
            OR
            (
                parent_node_id IS NOT NULL
                AND edge_character IS NOT NULL
                AND char_length(edge_character) = 1
            )
        ),

    CONSTRAINT valid_frequency
        CHECK (frequency >= 0),

    CONSTRAINT terminal_frequency_consistency
        CHECK (
            (is_terminal = TRUE AND frequency > 0)
            OR
            (is_terminal = FALSE AND frequency = 0)
        )
);

-- A dictionary has exactly one logical root.
CREATE UNIQUE INDEX IF NOT EXISTS idx_trie_single_root
    ON trie_node(dictionary_id)
    WHERE parent_node_id IS NULL;

-- A parent can have only one outgoing transition for a character.
CREATE UNIQUE INDEX IF NOT EXISTS idx_trie_unique_transition
    ON trie_node(dictionary_id, parent_node_id, edge_character)
    WHERE parent_node_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_trie_parent_lookup
    ON trie_node(dictionary_id, parent_node_id);

CREATE INDEX IF NOT EXISTS idx_trie_terminal_nodes
    ON trie_node(dictionary_id, node_id)
    WHERE is_terminal = TRUE;

-- ============================================================================
-- 3. ROOT CREATION
-- ============================================================================

CREATE OR REPLACE FUNCTION create_dictionary_root(
    p_dictionary_id BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_root_id BIGINT;
BEGIN
    PERFORM 1
    FROM dictionary
    WHERE dictionary_id = p_dictionary_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Dictionary % does not exist',
            p_dictionary_id;
    END IF;

    INSERT INTO trie_node (
        dictionary_id,
        parent_node_id,
        edge_character
    )
    VALUES (
        p_dictionary_id,
        NULL,
        NULL
    )
    ON CONFLICT (dictionary_id)
        WHERE parent_node_id IS NULL
    DO NOTHING;

    SELECT node_id
    INTO v_root_id
    FROM trie_node
    WHERE dictionary_id = p_dictionary_id
      AND parent_node_id IS NULL;

    RETURN v_root_id;
END;
$$;

-- ============================================================================
-- 4. NODE INTEGRITY TRIGGER
-- ============================================================================

CREATE OR REPLACE FUNCTION validate_trie_node()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_parent_dictionary BIGINT;
BEGIN
    IF NEW.parent_node_id IS NULL THEN
        IF NEW.edge_character IS NOT NULL THEN
            RAISE EXCEPTION
                'Root node cannot contain a character transition';
        END IF;

        RETURN NEW;
    END IF;

    IF NEW.edge_character IS NULL
       OR char_length(NEW.edge_character) <> 1 THEN
        RAISE EXCEPTION
            'Each trie transition must contain exactly one character';
    END IF;

    SELECT dictionary_id
    INTO v_parent_dictionary
    FROM trie_node
    WHERE node_id = NEW.parent_node_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Parent node does not exist';
    END IF;

    IF v_parent_dictionary <> NEW.dictionary_id THEN
        RAISE EXCEPTION
            'Parent and child must belong to the same dictionary';
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validate_trie_node ON trie_node;

CREATE TRIGGER trg_validate_trie_node
BEFORE INSERT OR UPDATE OF
    dictionary_id,
    parent_node_id,
    edge_character
ON trie_node
FOR EACH ROW
EXECUTE FUNCTION validate_trie_node();

-- ============================================================================
-- 5. INSERT WORD
-- ============================================================================

CREATE OR REPLACE FUNCTION insert_word(
    p_dictionary_id BIGINT,
    p_word TEXT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_word TEXT;
    v_root_id BIGINT;
    v_current_id BIGINT;
    v_next_id BIGINT;
    v_character TEXT;
    v_new_word BOOLEAN;
    v_position INTEGER;
BEGIN
    IF p_word IS NULL THEN
        RAISE EXCEPTION 'Word cannot be NULL';
    END IF;

    SELECT CASE
        WHEN case_sensitive THEN
            normalize(trim(p_word), NFC)
        ELSE
            lower(normalize(trim(p_word), NFC))
        END
    INTO v_word
    FROM dictionary
    WHERE dictionary_id = p_dictionary_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Dictionary % does not exist',
            p_dictionary_id;
    END IF;

    IF v_word = '' THEN
        RAISE EXCEPTION 'Word cannot be empty';
    END IF;

    IF char_length(v_word) > 256 THEN
        RAISE EXCEPTION 'Word exceeds 256 characters';
    END IF;

    IF v_word ~ '[[:cntrl:]]' THEN
        RAISE EXCEPTION 'Control characters are prohibited';
    END IF;

    v_root_id := create_dictionary_root(p_dictionary_id);

    v_current_id := v_root_id;

    -- Traverse the word one Unicode character at a time.
    FOR v_position IN 1..char_length(v_word)
    LOOP
        v_character := substring(v_word FROM v_position FOR 1);

        INSERT INTO trie_node (
            dictionary_id,
            parent_node_id,
            edge_character
        )
        VALUES (
            p_dictionary_id,
            v_current_id,
            v_character
        )
        ON CONFLICT (
            dictionary_id,
            parent_node_id,
            edge_character
        )
        WHERE parent_node_id IS NOT NULL
        DO NOTHING;

        SELECT node_id
        INTO v_next_id
        FROM trie_node
        WHERE dictionary_id = p_dictionary_id
          AND parent_node_id = v_current_id
          AND edge_character = v_character;

        v_current_id := v_next_id;
    END LOOP;

    SELECT NOT is_terminal
    INTO v_new_word
    FROM trie_node
    WHERE node_id = v_current_id
    FOR UPDATE;

    UPDATE trie_node
    SET is_terminal = TRUE,
        frequency = frequency + 1
    WHERE node_id = v_current_id;

    RETURN v_new_word;
END;
$$;

-- ============================================================================
-- 6. EXACT WORD SEARCH
-- ============================================================================

CREATE OR REPLACE FUNCTION search_word(
    p_dictionary_id BIGINT,
    p_word TEXT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_word TEXT;
    v_current_id BIGINT;
    v_next_id BIGINT;
    v_character TEXT;
    v_position INTEGER;
BEGIN
    IF p_word IS NULL OR trim(p_word) = '' THEN
        RETURN FALSE;
    END IF;

    SELECT CASE
        WHEN case_sensitive THEN
            normalize(trim(p_word), NFC)
        ELSE
            lower(normalize(trim(p_word), NFC))
        END
    INTO v_word
    FROM dictionary
    WHERE dictionary_id = p_dictionary_id;

    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;

    SELECT node_id
    INTO v_current_id
    FROM trie_node
    WHERE dictionary_id = p_dictionary_id
      AND parent_node_id IS NULL;

    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;

    FOR v_position IN 1..char_length(v_word)
    LOOP
        v_character := substring(v_word FROM v_position FOR 1);

        SELECT node_id
        INTO v_next_id
        FROM trie_node
        WHERE dictionary_id = p_dictionary_id
          AND parent_node_id = v_current_id
          AND edge_character = v_character;

        IF NOT FOUND THEN
            RETURN FALSE;
        END IF;

        v_current_id := v_next_id;
    END LOOP;

    RETURN EXISTS (
        SELECT 1
        FROM trie_node
        WHERE node_id = v_current_id
          AND is_terminal = TRUE
    );
END;
$$;

-- ============================================================================
-- 7. PREFIX MATCHING
-- ============================================================================

CREATE OR REPLACE FUNCTION prefix_exists(
    p_dictionary_id BIGINT,
    p_prefix TEXT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_prefix TEXT;
    v_current_id BIGINT;
    v_next_id BIGINT;
    v_character TEXT;
    v_position INTEGER;
BEGIN
    IF p_prefix IS NULL OR trim(p_prefix) = '' THEN
        RETURN FALSE;
    END IF;

    SELECT CASE
        WHEN case_sensitive THEN
            normalize(trim(p_prefix), NFC)
        ELSE
            lower(normalize(trim(p_prefix), NFC))
        END
    INTO v_prefix
    FROM dictionary
    WHERE dictionary_id = p_dictionary_id;

    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;

    SELECT node_id
    INTO v_current_id
    FROM trie_node
    WHERE dictionary_id = p_dictionary_id
      AND parent_node_id IS NULL;

    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;

    FOR v_position IN 1..char_length(v_prefix)
    LOOP
        v_character := substring(v_prefix FROM v_position FOR 1);

        SELECT node_id
        INTO v_next_id
        FROM trie_node
        WHERE dictionary_id = p_dictionary_id
          AND parent_node_id = v_current_id
          AND edge_character = v_character;

        IF NOT FOUND THEN
            RETURN FALSE;
        END IF;

        v_current_id := v_next_id;
    END LOOP;

    RETURN TRUE;
END;
$$;

-- ============================================================================
-- 8. AUTOCOMPLETE USING RECURSIVE CTE
-- ============================================================================

CREATE OR REPLACE FUNCTION autocomplete(
    p_dictionary_id BIGINT,
    p_prefix TEXT,
    p_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    matched_word TEXT,
    word_frequency INTEGER
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_prefix TEXT;
    v_start_id BIGINT;
BEGIN
    IF p_prefix IS NULL OR trim(p_prefix) = '' THEN
        RAISE EXCEPTION 'Prefix cannot be empty';
    END IF;

    IF p_limit < 1 OR p_limit > 1000 THEN
        RAISE EXCEPTION 'Limit must be between 1 and 1000';
    END IF;

    SELECT CASE
        WHEN case_sensitive THEN
            normalize(trim(p_prefix), NFC)
        ELSE
            lower(normalize(trim(p_prefix), NFC))
        END
    INTO v_prefix
    FROM dictionary
    WHERE dictionary_id = p_dictionary_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Dictionary does not exist';
    END IF;

    SELECT node_id
    INTO v_start_id
    FROM trie_node
    WHERE dictionary_id = p_dictionary_id
      AND parent_node_id IS NULL;

    IF NOT FOUND THEN
        RETURN;
    END IF;

    FOR v_position IN 1..char_length(v_prefix)
    LOOP
        SELECT node_id
        INTO v_start_id
        FROM trie_node
        WHERE dictionary_id = p_dictionary_id
          AND parent_node_id = v_start_id
          AND edge_character =
              substring(v_prefix FROM v_position FOR 1);

        IF NOT FOUND THEN
            RETURN;
        END IF;
    END LOOP;

    RETURN QUERY
    WITH RECURSIVE descendants (
        node_id,
        current_word,
        is_terminal,
        frequency
    ) AS (
        SELECT
            n.node_id,
            v_prefix,
            n.is_terminal,
            n.frequency
        FROM trie_node n
        WHERE n.node_id = v_start_id

        UNION ALL

        SELECT
            child.node_id,
            parent.current_word || child.edge_character,
            child.is_terminal,
            child.frequency
        FROM descendants parent
        JOIN trie_node child
          ON child.parent_node_id = parent.node_id
         AND child.dictionary_id = p_dictionary_id
    )
    SELECT
        current_word,
        frequency
    FROM descendants
    WHERE is_terminal = TRUE
    ORDER BY current_word
    LIMIT p_limit;
END;
$$;

-- ============================================================================
-- 9. DELETE WORD AND PRUNE UNUSED NODES
-- ============================================================================

CREATE OR REPLACE FUNCTION delete_word(
    p_dictionary_id BIGINT,
    p_word TEXT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_word TEXT;
    v_current_id BIGINT;
    v_next_id BIGINT;
    v_character TEXT;
    v_position INTEGER;
    v_ids BIGINT[] := ARRAY[]::BIGINT[];
    v_nodes BIGINT[];
    v_id BIGINT;
    v_index INTEGER;
BEGIN
    IF p_word IS NULL OR trim(p_word) = '' THEN
        RETURN FALSE;
    END IF;

    SELECT CASE
        WHEN case_sensitive THEN
            normalize(trim(p_word), NFC)
        ELSE
            lower(normalize(trim(p_word), NFC))
        END
    INTO v_word
    FROM dictionary
    WHERE dictionary_id = p_dictionary_id;

    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;

    SELECT node_id
    INTO v_current_id
    FROM trie_node
    WHERE dictionary_id = p_dictionary_id
      AND parent_node_id IS NULL;

    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;

    FOR v_position IN 1..char_length(v_word)
    LOOP
        v_character := substring(v_word FROM v_position FOR 1);

        SELECT node_id
        INTO v_next_id
        FROM trie_node
        WHERE dictionary_id = p_dictionary_id
          AND parent_node_id = v_current_id
          AND edge_character = v_character;

        IF NOT FOUND THEN
            RETURN FALSE;
        END IF;

        v_current_id := v_next_id;
        v_ids := array_append(v_ids, v_current_id);
    END LOOP;

    UPDATE trie_node
    SET is_terminal = FALSE,
        frequency = 0
    WHERE node_id = v_current_id
      AND is_terminal = TRUE;

    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;

    -- Process the path from leaf to root.
    v_nodes := v_ids;

    FOR v_index IN REVERSE array_length(v_nodes, 1)..1
    LOOP
        v_id := v_nodes[v_index];

        DELETE FROM trie_node n
        WHERE n.node_id = v_id
          AND n.is_terminal = FALSE
          AND NOT EXISTS (
              SELECT 1
              FROM trie_node child
              WHERE child.parent_node_id = n.node_id
          );
    END LOOP;

    RETURN TRUE;
END;
$$;

-- ============================================================================
-- 10. DICTIONARY STATISTICS
-- ============================================================================

CREATE OR REPLACE VIEW dictionary_statistics AS
SELECT
    d.dictionary_id,
    d.dictionary_name,
    count(n.node_id) AS total_nodes,
    count(n.node_id) FILTER (
        WHERE n.is_terminal
    ) AS distinct_words,
    coalesce(sum(n.frequency), 0) AS total_insertions,
    count(n.node_id) - 1 AS total_edges,
    coalesce(
        max(char_length(
            (
                WITH RECURSIVE paths AS (
                    SELECT
                        node_id,
                        parent_node_id,
                        0 AS depth
                    FROM trie_node
                    WHERE dictionary_id = d.dictionary_id
                      AND parent_node_id IS NULL

                    UNION ALL

                    SELECT
                        child.node_id,
                        child.parent_node_id,
                        parent.depth + 1
                    FROM trie_node child
                    JOIN paths parent
                      ON child.parent_node_id = parent.node_id
                )
                SELECT string_agg('', '')
                FROM paths
            )
        )),
        0
    ) AS reserved_depth_metric
FROM dictionary d
LEFT JOIN trie_node n
    ON n.dictionary_id = d.dictionary_id
GROUP BY d.dictionary_id, d.dictionary_name;

-- ============================================================================
-- 11. SAMPLE DICTIONARIES
-- ============================================================================

INSERT INTO dictionary (
    dictionary_name,
    description,
    case_sensitive
)
VALUES
(
    'product_catalogue',
    'Enterprise product identifier dictionary',
    FALSE
),
(
    'command_catalogue',
    'Operational command dictionary',
    FALSE
),
(
    'case_sensitive_catalogue',
    'Case-sensitive identifier dictionary',
    TRUE
)
ON CONFLICT (dictionary_name) DO NOTHING;

-- ============================================================================
-- 12. SAMPLE WORD INSERTIONS
-- ============================================================================

DO $$
DECLARE
    v_product BIGINT;
    v_commands BIGINT;
    v_sensitive BIGINT;
    v_word TEXT;
BEGIN
    SELECT dictionary_id
    INTO v_product
    FROM dictionary
    WHERE dictionary_name = 'product_catalogue';

    SELECT dictionary_id
    INTO v_commands
    FROM dictionary
    WHERE dictionary_name = 'command_catalogue';

    SELECT dictionary_id
    INTO v_sensitive
    FROM dictionary
    WHERE dictionary_name = 'case_sensitive_catalogue';

    FOREACH v_word IN ARRAY ARRAY[
        'product100',
        'product101',
        'product102',
        'product200',
        'product210',
        'project100',
        'project110',
        'process100',
        'process200',
        'production',
        'prototype'
    ]
    LOOP
        PERFORM insert_word(v_product, v_word);
    END LOOP;

    FOREACH v_word IN ARRAY ARRAY[
        'deploy',
        'deployment',
        'delete',
        'describe',
        'design',
        'debug',
        'docker',
        'document',
        'download',
        'database'
    ]
    LOOP
        PERFORM insert_word(v_commands, v_word);
    END LOOP;

    PERFORM insert_word(v_sensitive, 'Trie');
    PERFORM insert_word(v_sensitive, 'trie');

    -- Duplicate insertion increases frequency, not distinct words.
    PERFORM insert_word(v_product, 'product100');
    PERFORM insert_word(v_commands, 'deploy');
END;
$$;

-- ============================================================================
-- 13. RETRIEVAL QUERIES
-- ============================================================================

SELECT
    dictionary_name,
    dictionary_id,
    case_sensitive
FROM dictionary
ORDER BY dictionary_id;

SELECT
    d.dictionary_name,
    n.node_id,
    n.parent_node_id,
    n.edge_character,
    n.is_terminal,
    n.frequency
FROM trie_node n
JOIN dictionary d
    ON d.dictionary_id = n.dictionary_id
ORDER BY d.dictionary_id, n.node_id;

-- ============================================================================
-- 14. EXACT SEARCH EVALUATION
-- ============================================================================

SELECT
    'product100' AS search_term,
    search_word(
        dictionary_id,
        'product100'
    ) AS found
FROM dictionary
WHERE dictionary_name = 'product_catalogue';

SELECT
    'product999' AS search_term,
    search_word(
        dictionary_id,
        'product999'
    ) AS found
FROM dictionary
WHERE dictionary_name = 'product_catalogue';

-- ============================================================================
-- 15. PREFIX MATCHING
-- ============================================================================

SELECT
    dictionary_name,
    prefix_exists(dictionary_id, 'prod') AS prefix_found
FROM dictionary
WHERE dictionary_name = 'product_catalogue';

SELECT
    dictionary_name,
    prefix_exists(dictionary_id, 'xyz') AS prefix_found
FROM dictionary
WHERE dictionary_name = 'product_catalogue';

-- ============================================================================
-- 16. AUTOCOMPLETE REPORTING
-- ============================================================================

SELECT *
FROM autocomplete(
    (
        SELECT dictionary_id
        FROM dictionary
        WHERE dictionary_name = 'product_catalogue'
    ),
    'prod',
    10
);

SELECT *
FROM autocomplete(
    (
        SELECT dictionary_id
        FROM dictionary
        WHERE dictionary_name = 'command_catalogue'
    ),
    'de',
    5
);

-- ============================================================================
-- 17. FREQUENCY REPORTING
-- ============================================================================

SELECT
    d.dictionary_name,
    n.edge_character,
    n.frequency,
    n.is_terminal
FROM trie_node n
JOIN dictionary d
    ON d.dictionary_id = n.dictionary_id
WHERE n.is_terminal = TRUE
ORDER BY d.dictionary_name, n.frequency DESC;

-- ============================================================================
-- 18. DICTIONARY AGGREGATION
-- ============================================================================

SELECT
    d.dictionary_name,
    count(n.node_id) AS node_count,
    count(n.node_id) FILTER (
        WHERE n.is_terminal
    ) AS word_count,
    coalesce(sum(n.frequency), 0) AS insertion_count
FROM dictionary d
LEFT JOIN trie_node n
    ON n.dictionary_id = d.dictionary_id
GROUP BY d.dictionary_name
ORDER BY d.dictionary_name;

-- ============================================================================
-- 19. VALIDATION AND FAILURE CASES
-- ============================================================================

DO $$
DECLARE
    v_dictionary BIGINT;
BEGIN
    SELECT dictionary_id
    INTO v_dictionary
    FROM dictionary
    WHERE dictionary_name = 'product_catalogue';

    -- Invalid input must fail without creating partial words.
    BEGIN
        PERFORM insert_word(v_dictionary, '');

        RAISE NOTICE 'Unexpected empty-word acceptance';

    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Empty-word validation: %', SQLERRM;
    END;

    BEGIN
        PERFORM insert_word(v_dictionary, NULL);

        RAISE NOTICE 'Unexpected NULL acceptance';

    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'NULL validation: %', SQLERRM;
    END;

    BEGIN
        PERFORM insert_word(v_dictionary, repeat('x', 257));

        RAISE NOTICE 'Unexpected oversized-word acceptance';

    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Length validation: %', SQLERRM;
    END;

    BEGIN
        INSERT INTO trie_node (
            dictionary_id,
            parent_node_id,
            edge_character
        )
        VALUES (
            v_dictionary,
            NULL,
            'x'
        );

        RAISE NOTICE 'Unexpected invalid root acceptance';

    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Root validation: %', SQLERRM;
    END;
END;
$$;

-- ============================================================================
-- 20. TRANSACTIONAL DELETION
-- ============================================================================

BEGIN;

DO $$
DECLARE
    v_dictionary BIGINT;
BEGIN
    SELECT dictionary_id
    INTO v_dictionary
    FROM dictionary
    WHERE dictionary_name = 'product_catalogue';

    PERFORM delete_word(v_dictionary, 'product102');
END;
$$;

COMMIT;

-- Confirm that deletion did not damage shared prefixes.
SELECT
    search_word(dictionary_id, 'product102') AS deleted_word_exists,
    search_word(dictionary_id, 'product101') AS shared_prefix_word_exists
FROM dictionary
WHERE dictionary_name = 'product_catalogue';

-- ============================================================================
-- 21. CASE-SENSITIVITY EVALUATION
-- ============================================================================

SELECT
    search_word(dictionary_id, 'Trie') AS uppercase_found,
    search_word(dictionary_id, 'trie') AS lowercase_found
FROM dictionary
WHERE dictionary_name = 'case_sensitive_catalogue';

-- ============================================================================
-- 22. FINAL REPORT
-- ============================================================================

SELECT
    d.dictionary_name,
    count(n.node_id) AS total_nodes,
    count(n.node_id) FILTER (
        WHERE n.is_terminal
    ) AS distinct_words,
    coalesce(sum(n.frequency), 0) AS total_insertions
FROM dictionary d
LEFT JOIN trie_node n
    ON n.dictionary_id = d.dictionary_id
GROUP BY d.dictionary_name
ORDER BY d.dictionary_name;

-- ============================================================================
-- END OF TRIE DATABASE IMPLEMENTATION
-- ============================================================================
