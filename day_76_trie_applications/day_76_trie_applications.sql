/*
===============================================================================
TRIE APPLICATIONS - POSTGRESQL 14+
===============================================================================

Relational implementation of:
- Dictionary management
- Trie node storage
- Word insertion and deletion
- Prefix searching
- Autocomplete
- Frequency ranking
- Exact word lookup
- Wildcard dictionary search
- Word Break evaluation
- Search analytics
- Dictionary versioning and audit history

The trie is represented as an adjacency structure:
parent node -> character edge -> child node.

A separate dictionary_entry table stores complete words and frequencies.
The two structures are maintained transactionally.

Run this script in a database where the executing role can create schemas.
===============================================================================
*/

BEGIN;

CREATE SCHEMA IF NOT EXISTS trie_lab;

SET search_path TO trie_lab, public;

-- ---------------------------------------------------------------------------
-- 1. Dictionary and trie domain
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS dictionary (
    dictionary_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dictionary_name VARCHAR(120) NOT NULL UNIQUE,
    description TEXT NOT NULL DEFAULT '',
    language_code VARCHAR(10) NOT NULL DEFAULT 'en',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT dictionary_name_not_empty
        CHECK (length(trim(dictionary_name)) > 0),

    CONSTRAINT dictionary_language_valid
        CHECK (language_code ~ '^[a-z]{2}(-[A-Z]{2})?$')
);

CREATE TABLE IF NOT EXISTS trie_node (
    node_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    dictionary_id BIGINT NOT NULL
        REFERENCES dictionary(dictionary_id)
        ON DELETE CASCADE,

    parent_node_id BIGINT,

    edge_character CHAR(1),

    depth INTEGER NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT trie_node_parent_fk
        FOREIGN KEY (parent_node_id)
        REFERENCES trie_node(node_id)
        ON DELETE CASCADE,

    CONSTRAINT trie_node_depth_valid
        CHECK (depth >= 0),

    CONSTRAINT trie_node_edge_valid
        CHECK (
            (depth = 0 AND parent_node_id IS NULL
                AND edge_character IS NULL)
            OR
            (depth > 0 AND parent_node_id IS NOT NULL
                AND edge_character ~ '^[a-z]$')
        ),

    CONSTRAINT trie_node_unique_edge
        UNIQUE (dictionary_id, parent_node_id, edge_character),

    CONSTRAINT trie_node_dictionary_node_unique
        UNIQUE (dictionary_id, node_id)
);

CREATE UNIQUE INDEX IF NOT EXISTS trie_root_unique
ON trie_node(dictionary_id)
WHERE parent_node_id IS NULL;

CREATE INDEX IF NOT EXISTS trie_parent_lookup_idx
ON trie_node(dictionary_id, parent_node_id);

CREATE INDEX IF NOT EXISTS trie_edge_lookup_idx
ON trie_node(dictionary_id, edge_character);

CREATE TABLE IF NOT EXISTS dictionary_entry (
    entry_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    dictionary_id BIGINT NOT NULL
        REFERENCES dictionary(dictionary_id)
        ON DELETE CASCADE,

    word VARCHAR(128) NOT NULL,

    terminal_node_id BIGINT NOT NULL,

    frequency BIGINT NOT NULL DEFAULT 1,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT dictionary_word_valid
        CHECK (word ~ '^[a-z]{1,128}$'),

    CONSTRAINT dictionary_frequency_positive
        CHECK (frequency > 0),

    CONSTRAINT dictionary_entry_unique
        UNIQUE (dictionary_id, word),

    CONSTRAINT dictionary_terminal_node_fk
        FOREIGN KEY (dictionary_id, terminal_node_id)
        REFERENCES trie_node(dictionary_id, node_id)
);

CREATE INDEX IF NOT EXISTS dictionary_prefix_idx
ON dictionary_entry(dictionary_id, word text_pattern_ops)
WHERE is_active = TRUE;

CREATE INDEX IF NOT EXISTS dictionary_frequency_idx
ON dictionary_entry(dictionary_id, frequency DESC, word)
WHERE is_active = TRUE;

-- ---------------------------------------------------------------------------
-- 2. Search requests and search analytics
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS search_request (
    request_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    dictionary_id BIGINT NOT NULL
        REFERENCES dictionary(dictionary_id),

    search_type VARCHAR(20) NOT NULL,

    search_text VARCHAR(128) NOT NULL,

    result_count INTEGER NOT NULL DEFAULT 0,

    execution_time_ms NUMERIC(12, 3),

    requested_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT search_type_valid
        CHECK (
            search_type IN (
                'EXACT',
                'PREFIX',
                'AUTOCOMPLETE',
                'WORD_BREAK',
                'WILDCARD'
            )
        ),

    CONSTRAINT search_result_count_valid
        CHECK (result_count >= 0),

    CONSTRAINT search_execution_time_valid
        CHECK (
            execution_time_ms IS NULL
            OR execution_time_ms >= 0
        )
);

CREATE INDEX IF NOT EXISTS search_analytics_idx
ON search_request(dictionary_id, requested_at DESC);

-- ---------------------------------------------------------------------------
-- 3. Audit history
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS dictionary_audit (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    dictionary_id BIGINT NOT NULL,

    word VARCHAR(128) NOT NULL,

    operation VARCHAR(20) NOT NULL,

    old_frequency BIGINT,

    new_frequency BIGINT,

    performed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT audit_operation_valid
        CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE'))
);

CREATE INDEX IF NOT EXISTS dictionary_audit_history_idx
ON dictionary_audit(dictionary_id, performed_at DESC);

-- ---------------------------------------------------------------------------
-- 4. Audit trigger
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION audit_dictionary_entry()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO dictionary_audit (
            dictionary_id,
            word,
            operation,
            old_frequency,
            new_frequency
        )
        VALUES (
            NEW.dictionary_id,
            NEW.word,
            'INSERT',
            NULL,
            NEW.frequency
        );

        RETURN NEW;

    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO dictionary_audit (
            dictionary_id,
            word,
            operation,
            old_frequency,
            new_frequency
        )
        VALUES (
            NEW.dictionary_id,
            NEW.word,
            'UPDATE',
            OLD.frequency,
            NEW.frequency
        );

        RETURN NEW;

    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO dictionary_audit (
            dictionary_id,
            word,
            operation,
            old_frequency,
            new_frequency
        )
        VALUES (
            OLD.dictionary_id,
            OLD.word,
            'DELETE',
            OLD.frequency,
            NULL
        );

        RETURN OLD;
    END IF;

    RETURN NULL;
END;
$$;

DROP TRIGGER IF EXISTS dictionary_entry_audit_trigger
ON dictionary_entry;

CREATE TRIGGER dictionary_entry_audit_trigger
AFTER INSERT OR UPDATE OR DELETE
ON dictionary_entry
FOR EACH ROW
EXECUTE FUNCTION audit_dictionary_entry();

-- ---------------------------------------------------------------------------
-- 5. Create a dictionary and its root node
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION create_dictionary(
    p_name VARCHAR,
    p_description TEXT DEFAULT '',
    p_language VARCHAR DEFAULT 'en'
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_dictionary_id BIGINT;
BEGIN
    IF p_name IS NULL OR length(trim(p_name)) = 0 THEN
        RAISE EXCEPTION 'Dictionary name cannot be empty.';
    END IF;

    IF p_language !~ '^[a-z]{2}(-[A-Z]{2})?$' THEN
        RAISE EXCEPTION 'Invalid language code.';
    END IF;

    INSERT INTO dictionary (
        dictionary_name,
        description,
        language_code
    )
    VALUES (
        trim(p_name),
        COALESCE(p_description, ''),
        p_language
    )
    RETURNING dictionary_id INTO v_dictionary_id;

    INSERT INTO trie_node (
        dictionary_id,
        parent_node_id,
        edge_character,
        depth
    )
    VALUES (
        v_dictionary_id,
        NULL,
        NULL,
        0
    );

    RETURN v_dictionary_id;
END;
$$;

-- ---------------------------------------------------------------------------
-- 6. Insert a word into the trie
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION insert_word(
    p_dictionary_id BIGINT,
    p_word VARCHAR,
    p_frequency BIGINT DEFAULT 1
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_word VARCHAR(128);
    v_parent_id BIGINT;
    v_node_id BIGINT;
    v_character CHAR(1);
    v_position INTEGER;
    v_length INTEGER;
    v_root_count INTEGER;
    v_entry_id BIGINT;
BEGIN
    v_word := lower(trim(p_word));

    IF v_word IS NULL OR v_word !~ '^[a-z]{1,128}$' THEN
        RAISE EXCEPTION
            'Word must contain 1 to 128 lowercase alphabetic characters.';
    END IF;

    IF p_frequency IS NULL OR p_frequency <= 0 THEN
        RAISE EXCEPTION 'Frequency must be positive.';
    END IF;

    -- Serialize modifications to one dictionary.
    PERFORM 1
    FROM dictionary
    WHERE dictionary_id = p_dictionary_id
      AND is_active = TRUE
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Active dictionary does not exist.';
    END IF;

    SELECT node_id
    INTO v_parent_id
    FROM trie_node
    WHERE dictionary_id = p_dictionary_id
      AND parent_node_id IS NULL;

    IF v_parent_id IS NULL THEN
        RAISE EXCEPTION 'Dictionary root node is missing.';
    END IF;

    v_length := length(v_word);

    FOR v_position IN 1..v_length LOOP
        v_character := substring(v_word, v_position, 1);

        INSERT INTO trie_node (
            dictionary_id,
            parent_node_id,
            edge_character,
            depth
        )
        VALUES (
            p_dictionary_id,
            v_parent_id,
            v_character,
            v_position
        )
        ON CONFLICT (
            dictionary_id,
            parent_node_id,
            edge_character
        )
        DO NOTHING;

        SELECT node_id
        INTO v_node_id
        FROM trie_node
        WHERE dictionary_id = p_dictionary_id
          AND parent_node_id = v_parent_id
          AND edge_character = v_character;

        IF v_node_id IS NULL THEN
            RAISE EXCEPTION 'Unable to construct trie path.';
        END IF;

        v_parent_id := v_node_id;
    END LOOP;

    INSERT INTO dictionary_entry (
        dictionary_id,
        word,
        terminal_node_id,
        frequency,
        is_active
    )
    VALUES (
        p_dictionary_id,
        v_word,
        v_parent_id,
        p_frequency,
        TRUE
    )
    ON CONFLICT (dictionary_id, word)
    DO UPDATE SET
        frequency =
            CASE
                WHEN dictionary_entry.is_active
                THEN dictionary_entry.frequency + EXCLUDED.frequency
                ELSE EXCLUDED.frequency
            END,
        is_active = TRUE,
        terminal_node_id = EXCLUDED.terminal_node_id,
        updated_at = CURRENT_TIMESTAMP
    RETURNING entry_id INTO v_entry_id;

    RETURN v_entry_id;
END;
$$;

-- ---------------------------------------------------------------------------
-- 7. Exact dictionary lookup
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION exact_search(
    p_dictionary_id BIGINT,
    p_word VARCHAR
)
RETURNS BOOLEAN
LANGUAGE sql
STABLE
AS $$
    SELECT EXISTS (
        SELECT 1
        FROM dictionary_entry
        WHERE dictionary_id = p_dictionary_id
          AND word = lower(trim(p_word))
          AND is_active = TRUE
    );
$$;

-- ---------------------------------------------------------------------------
-- 8. Prefix lookup
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION prefix_search(
    p_dictionary_id BIGINT,
    p_prefix VARCHAR,
    p_limit INTEGER DEFAULT 20
)
RETURNS TABLE (
    matched_word VARCHAR,
    word_frequency BIGINT
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_prefix VARCHAR(128);
BEGIN
    v_prefix := lower(trim(p_prefix));

    IF v_prefix IS NULL OR v_prefix !~ '^[a-z]{1,128}$' THEN
        RAISE EXCEPTION 'Invalid prefix.';
    END IF;

    IF p_limit < 0 OR p_limit > 1000 THEN
        RAISE EXCEPTION 'Limit must be between 0 and 1000.';
    END IF;

    RETURN QUERY
    SELECT
        e.word,
        e.frequency
    FROM dictionary_entry e
    WHERE e.dictionary_id = p_dictionary_id
      AND e.is_active = TRUE
      AND left(e.word, length(v_prefix)) = v_prefix
    ORDER BY e.word
    LIMIT p_limit;
END;
$$;

-- ---------------------------------------------------------------------------
-- 9. Frequency-ranked autocomplete
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION autocomplete(
    p_dictionary_id BIGINT,
    p_prefix VARCHAR,
    p_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    suggested_word VARCHAR,
    suggestion_frequency BIGINT
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_prefix VARCHAR(128);
BEGIN
    v_prefix := lower(trim(p_prefix));

    IF v_prefix IS NULL OR v_prefix !~ '^[a-z]{1,128}$' THEN
        RAISE EXCEPTION 'Invalid autocomplete prefix.';
    END IF;

    IF p_limit < 0 OR p_limit > 100 THEN
        RAISE EXCEPTION 'Limit must be between 0 and 100.';
    END IF;

    RETURN QUERY
    SELECT
        e.word,
        e.frequency
    FROM dictionary_entry e
    WHERE e.dictionary_id = p_dictionary_id
      AND e.is_active = TRUE
      AND left(e.word, length(v_prefix)) = v_prefix
    ORDER BY e.frequency DESC, e.word
    LIMIT p_limit;
END;
$$;

-- ---------------------------------------------------------------------------
-- 10. Wildcard dictionary lookup
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION wildcard_search(
    p_dictionary_id BIGINT,
    p_pattern VARCHAR,
    p_limit INTEGER DEFAULT 100
)
RETURNS TABLE (
    matched_word VARCHAR,
    match_frequency BIGINT
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_pattern VARCHAR(128);
BEGIN
    v_pattern := lower(trim(p_pattern));

    IF v_pattern IS NULL OR v_pattern !~ '^[a-z.*]{1,128}$' THEN
        RAISE EXCEPTION 'Invalid wildcard pattern.';
    END IF;

    IF p_limit < 0 OR p_limit > 1000 THEN
        RAISE EXCEPTION 'Invalid result limit.';
    END IF;

    -- Convert the application wildcard language:
    -- "." means one character; "*" means zero or more characters.
    -- PostgreSQL regular-expression metacharacters are escaped.
    v_pattern := replace(v_pattern, '.', '[a-z]');
    v_pattern := replace(v_pattern, '*', '[a-z]*');

    RETURN QUERY
    SELECT
        e.word,
        e.frequency
    FROM dictionary_entry e
    WHERE e.dictionary_id = p_dictionary_id
      AND e.is_active = TRUE
      AND e.word ~ ('^' || v_pattern || '$')
    ORDER BY e.word
    LIMIT p_limit;
END;
$$;

-- ---------------------------------------------------------------------------
-- 11. Word Break dynamic programming
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION word_break(
    p_dictionary_id BIGINT,
    p_text VARCHAR
)
RETURNS BOOLEAN
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_text VARCHAR(128);
    v_length INTEGER;
    v_start INTEGER;
    v_end INTEGER;
    v_word VARCHAR(128);
    v_reachable BOOLEAN[];
BEGIN
    v_text := lower(trim(p_text));

    IF v_text IS NULL OR v_text !~ '^[a-z]{1,128}$' THEN
        RAISE EXCEPTION 'Word Break input must contain 1 to 128 letters.';
    END IF;

    v_length := length(v_text);

    v_reachable := array_fill(
        FALSE,
        ARRAY[v_length + 1]
    );

    v_reachable[1] := TRUE;

    FOR v_start IN 1..v_length LOOP
        IF v_reachable[v_start] THEN

            FOR v_end IN v_start..v_length LOOP
                v_word := substring(
                    v_text,
                    v_start,
                    v_end - v_start + 1
                );

                IF EXISTS (
                    SELECT 1
                    FROM dictionary_entry e
                    WHERE e.dictionary_id = p_dictionary_id
                      AND e.word = v_word
                      AND e.is_active = TRUE
                ) THEN
                    v_reachable[v_end + 1] := TRUE;
                END IF;
            END LOOP;

        END IF;
    END LOOP;

    RETURN v_reachable[v_length + 1];
END;
$$;

-- ---------------------------------------------------------------------------
-- 12. Soft deletion and terminal-node maintenance
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION delete_word(
    p_dictionary_id BIGINT,
    p_word VARCHAR
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_word VARCHAR(128);
    v_node_id BIGINT;
BEGIN
    v_word := lower(trim(p_word));

    IF v_word IS NULL OR v_word !~ '^[a-z]{1,128}$' THEN
        RAISE EXCEPTION 'Invalid word.';
    END IF;

    PERFORM 1
    FROM dictionary
    WHERE dictionary_id = p_dictionary_id
    FOR UPDATE;

    UPDATE dictionary_entry
    SET
        is_active = FALSE,
        updated_at = CURRENT_TIMESTAMP
    WHERE dictionary_id = p_dictionary_id
      AND word = v_word
      AND is_active = TRUE
    RETURNING terminal_node_id INTO v_node_id;

    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;

    -- The trie path remains available for other words sharing its prefix.
    -- Physical pruning is intentionally deferred to maintenance operations.

    RETURN TRUE;
END;
$$;

-- ---------------------------------------------------------------------------
-- 13. Search analytics recording
-- ---------------------------------------------------------------------------

CREATE OR REPLACE PROCEDURE record_search(
    p_dictionary_id BIGINT,
    p_search_type VARCHAR,
    p_search_text VARCHAR,
    p_result_count INTEGER,
    p_execution_time_ms NUMERIC DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_search_type NOT IN (
        'EXACT',
        'PREFIX',
        'AUTOCOMPLETE',
        'WORD_BREAK',
        'WILDCARD'
    ) THEN
        RAISE EXCEPTION 'Unsupported search type.';
    END IF;

    IF p_result_count < 0 THEN
        RAISE EXCEPTION 'Result count cannot be negative.';
    END IF;

    IF p_execution_time_ms < 0 THEN
        RAISE EXCEPTION 'Execution time cannot be negative.';
    END IF;

    INSERT INTO search_request (
        dictionary_id,
        search_type,
        search_text,
        result_count,
        execution_time_ms
    )
    VALUES (
        p_dictionary_id,
        p_search_type,
        lower(trim(p_search_text)),
        p_result_count,
        p_execution_time_ms
    );
END;
$$;

-- ---------------------------------------------------------------------------
-- 14. Reporting views
-- ---------------------------------------------------------------------------

CREATE OR REPLACE VIEW dictionary_statistics AS
SELECT
    d.dictionary_id,
    d.dictionary_name,
    d.language_code,
    COUNT(e.entry_id) FILTER (
        WHERE e.is_active
    ) AS active_word_count,
    COALESCE(
        SUM(e.frequency) FILTER (WHERE e.is_active),
        0
    ) AS total_search_frequency,
    COUNT(DISTINCT n.node_id) AS trie_node_count
FROM dictionary d
LEFT JOIN dictionary_entry e
    ON e.dictionary_id = d.dictionary_id
LEFT JOIN trie_node n
    ON n.dictionary_id = d.dictionary_id
GROUP BY
    d.dictionary_id,
    d.dictionary_name,
    d.language_code;

CREATE OR REPLACE VIEW popular_dictionary_words AS
SELECT
    d.dictionary_name,
    e.word,
    e.frequency,
    e.updated_at
FROM dictionary_entry e
JOIN dictionary d
    ON d.dictionary_id = e.dictionary_id
WHERE e.is_active = TRUE
ORDER BY
    d.dictionary_name,
    e.frequency DESC,
    e.word;

CREATE OR REPLACE VIEW search_activity_report AS
SELECT
    d.dictionary_name,
    s.search_type,
    COUNT(*) AS total_requests,
    AVG(s.result_count) AS average_results,
    AVG(s.execution_time_ms) AS average_execution_time_ms,
    MAX(s.requested_at) AS latest_request
FROM search_request s
JOIN dictionary d
    ON d.dictionary_id = s.dictionary_id
GROUP BY
    d.dictionary_name,
    s.search_type;

-- ---------------------------------------------------------------------------
-- 15. Sample dictionaries
-- ---------------------------------------------------------------------------

SELECT create_dictionary(
    'English Core',
    'General English dictionary for prefix and word problems.',
    'en'
);

SELECT create_dictionary(
    'Technology Terms',
    'Technical vocabulary for search and autocomplete.',
    'en'
);

-- ---------------------------------------------------------------------------
-- 16. Sample word records
-- ---------------------------------------------------------------------------

DO $$
DECLARE
    v_english BIGINT;
    v_technology BIGINT;
BEGIN
    SELECT dictionary_id INTO v_english
    FROM dictionary
    WHERE dictionary_name = 'English Core';

    SELECT dictionary_id INTO v_technology
    FROM dictionary
    WHERE dictionary_name = 'Technology Terms';

    PERFORM insert_word(v_english, 'apple', 20);
    PERFORM insert_word(v_english, 'app', 8);
    PERFORM insert_word(v_english, 'application', 15);
    PERFORM insert_word(v_english, 'apply', 12);
    PERFORM insert_word(v_english, 'apt', 4);
    PERFORM insert_word(v_english, 'banana', 10);
    PERFORM insert_word(v_english, 'band', 6);
    PERFORM insert_word(v_english, 'bandana', 3);
    PERFORM insert_word(v_english, 'bat', 7);
    PERFORM insert_word(v_english, 'ball', 9);
    PERFORM insert_word(v_english, 'cat', 10);
    PERFORM insert_word(v_english, 'cats', 7);
    PERFORM insert_word(v_english, 'and', 12);
    PERFORM insert_word(v_english, 'sand', 5);
    PERFORM insert_word(v_english, 'dog', 15);

    PERFORM insert_word(v_technology, 'algorithm', 30);
    PERFORM insert_word(v_technology, 'analytics', 25);
    PERFORM insert_word(v_technology, 'database', 35);
    PERFORM insert_word(v_technology, 'datamining', 15);
    PERFORM insert_word(v_technology, 'developer', 20);
    PERFORM insert_word(v_technology, 'development', 18);
    PERFORM insert_word(v_technology, 'network', 40);
    PERFORM insert_word(v_technology, 'neural', 28);
    PERFORM insert_word(v_technology, 'security', 50);
    PERFORM insert_word(v_technology, 'software', 45);
END;
$$;

-- ---------------------------------------------------------------------------
-- 17. Retrieval and validation queries
-- ---------------------------------------------------------------------------

-- Exact word lookup.
SELECT exact_search(
    (
        SELECT dictionary_id
        FROM dictionary
        WHERE dictionary_name = 'English Core'
    ),
    'apple'
) AS apple_exists;

-- Prefix search.
SELECT *
FROM prefix_search(
    (
        SELECT dictionary_id
        FROM dictionary
        WHERE dictionary_name = 'English Core'
    ),
    'app',
    20
);

-- Frequency-ranked autocomplete.
SELECT *
FROM autocomplete(
    (
        SELECT dictionary_id
        FROM dictionary
        WHERE dictionary_name = 'English Core'
    ),
    'app',
    10
);

-- Wildcard search: one arbitrary letter at the end.
SELECT *
FROM wildcard_search(
    (
        SELECT dictionary_id
        FROM dictionary
        WHERE dictionary_name = 'English Core'
    ),
    'app..',
    20
);

-- Word Break evaluation.
SELECT word_break(
    (
        SELECT dictionary_id
        FROM dictionary
        WHERE dictionary_name = 'English Core'
    ),
    'catsanddog'
) AS can_segment;

-- ---------------------------------------------------------------------------
-- 18. Aggregation and reporting
-- ---------------------------------------------------------------------------

SELECT *
FROM dictionary_statistics
ORDER BY dictionary_name;

SELECT *
FROM popular_dictionary_words
LIMIT 15;

SELECT
    dictionary_name,
    word,
    frequency,
    DENSE_RANK() OVER (
        PARTITION BY dictionary_name
        ORDER BY frequency DESC
    ) AS popularity_rank
FROM popular_dictionary_words;

-- ---------------------------------------------------------------------------
-- 19. Workflow and search analytics
-- ---------------------------------------------------------------------------

CALL record_search(
    (
        SELECT dictionary_id
        FROM dictionary
        WHERE dictionary_name = 'English Core'
    ),
    'AUTOCOMPLETE',
    'app',
    4,
    1.250
);

CALL record_search(
    (
        SELECT dictionary_id
        FROM dictionary
        WHERE dictionary_name = 'English Core'
    ),
    'EXACT',
    'apple',
    1,
    0.450
);

CALL record_search(
    (
        SELECT dictionary_id
        FROM dictionary
        WHERE dictionary_name = 'English Core'
    ),
    'WORD_BREAK',
    'catsanddog',
    1,
    2.150
);

SELECT *
FROM search_activity_report
ORDER BY dictionary_name, search_type;

-- ---------------------------------------------------------------------------
-- 20. CTE-based prefix analysis
-- ---------------------------------------------------------------------------

WITH prefix_candidates AS (
    SELECT
        e.word,
        e.frequency,
        length(e.word) AS word_length
    FROM dictionary_entry e
    JOIN dictionary d
        ON d.dictionary_id = e.dictionary_id
    WHERE d.dictionary_name = 'English Core'
      AND e.is_active = TRUE
      AND left(e.word, 2) = 'ba'
),
ranked_candidates AS (
    SELECT
        word,
        frequency,
        word_length,
        ROW_NUMBER() OVER (
            ORDER BY frequency DESC, word
        ) AS result_rank
    FROM prefix_candidates
)
SELECT *
FROM ranked_candidates
WHERE result_rank <= 5
ORDER BY result_rank;

-- ---------------------------------------------------------------------------
-- 21. Transactional deletion example
-- ---------------------------------------------------------------------------

BEGIN;

SELECT delete_word(
    (
        SELECT dictionary_id
        FROM dictionary
        WHERE dictionary_name = 'English Core'
    ),
    'bandana'
);

-- Verify that the word is no longer active.
SELECT exact_search(
    (
        SELECT dictionary_id
        FROM dictionary
        WHERE dictionary_name = 'English Core'
    ),
    'bandana'
) AS bandana_active;

COMMIT;

-- ---------------------------------------------------------------------------
-- 22. Audit verification
-- ---------------------------------------------------------------------------

SELECT
    dictionary_id,
    word,
    operation,
    old_frequency,
    new_frequency,
    performed_at
FROM dictionary_audit
ORDER BY audit_id DESC
LIMIT 20;

-- ---------------------------------------------------------------------------
-- 23. Failure-case validation
-- ---------------------------------------------------------------------------

DO $$
BEGIN
    BEGIN
        PERFORM insert_word(
            (
                SELECT dictionary_id
                FROM dictionary
                WHERE dictionary_name = 'English Core'
            ),
            'invalid123',
            1
        );

        RAISE EXCEPTION
            'Validation failed: invalid word was accepted.';

    EXCEPTION
        WHEN OTHERS THEN
            IF SQLERRM NOT LIKE 'Word must contain%' THEN
                RAISE;
            END IF;

            RAISE NOTICE
                'Expected invalid-word validation executed.';
    END;

    BEGIN
        PERFORM insert_word(
            (
                SELECT dictionary_id
                FROM dictionary
                WHERE dictionary_name = 'English Core'
            ),
            'validword',
            -1
        );

        RAISE EXCEPTION
            'Validation failed: negative frequency accepted.';

    EXCEPTION
        WHEN OTHERS THEN
            IF SQLERRM <> 'Frequency must be positive.' THEN
                RAISE;
            END IF;

            RAISE NOTICE
                'Expected frequency validation executed.';
    END;
END;
$$;

COMMIT;

-- ---------------------------------------------------------------------------
-- 24. Final verification
-- ---------------------------------------------------------------------------

SELECT
    dictionary_name,
    active_word_count,
    total_search_frequency,
    trie_node_count
FROM dictionary_statistics
ORDER BY dictionary_name;
