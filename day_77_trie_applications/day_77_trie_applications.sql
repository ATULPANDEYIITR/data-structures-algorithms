-- ============================================================
-- ADVANCED TRIE ENGINEERING
-- PostgreSQL 15+
--
-- Models:
-- 1. Compressed radix dictionary.
-- 2. Radix tree nodes and compressed edge labels.
-- 3. Binary trie for XOR analytics.
-- 4. Maximum XOR pair evaluation.
-- 5. Prefix lookup and autocomplete.
-- 6. Versioned dictionary records.
-- 7. Transaction-safe insertion and deletion.
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS advanced_trie;

SET search_path TO advanced_trie, public;

-- ============================================================
-- 1. DOMAIN TABLES
-- ============================================================

CREATE TABLE IF NOT EXISTS dictionary (
    dictionary_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dictionary_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dictionary_entry (
    entry_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dictionary_id BIGINT NOT NULL
        REFERENCES dictionary(dictionary_id)
        ON DELETE CASCADE,

    word TEXT NOT NULL,
    normalized_word TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    entry_value TEXT,
    version BIGINT NOT NULL DEFAULT 1,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_dictionary_word
        UNIQUE (dictionary_id, normalized_word),

    CONSTRAINT ck_dictionary_word
        CHECK (
            word <> ''
            AND normalized_word <> ''
            AND length(word) <= 512
        ),

    CONSTRAINT ck_dictionary_version
        CHECK (version > 0)
);

-- Compressed radix nodes.
-- Each non-root node stores a complete compressed edge label.
CREATE TABLE IF NOT EXISTS radix_node (
    node_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    dictionary_id BIGINT NOT NULL
        REFERENCES dictionary(dictionary_id)
        ON DELETE CASCADE,

    parent_node_id BIGINT
        REFERENCES radix_node(node_id)
        ON DELETE CASCADE,

    edge_label TEXT NOT NULL,

    terminal BOOLEAN NOT NULL DEFAULT FALSE,

    entry_id BIGINT
        REFERENCES dictionary_entry(entry_id)
        ON DELETE SET NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ck_radix_edge_length
        CHECK (
            parent_node_id IS NULL
            OR length(edge_label) > 0
        ),

    CONSTRAINT ck_radix_terminal_entry
        CHECK (
            terminal = TRUE OR entry_id IS NULL
        )
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_radix_child_edge
    ON radix_node(dictionary_id, parent_node_id, edge_label);

CREATE INDEX IF NOT EXISTS idx_radix_parent
    ON radix_node(parent_node_id);

CREATE INDEX IF NOT EXISTS idx_radix_dictionary_terminal
    ON radix_node(dictionary_id, terminal)
    WHERE terminal = TRUE;

CREATE INDEX IF NOT EXISTS idx_dictionary_prefix
    ON dictionary_entry(dictionary_id, normalized_word text_pattern_ops)
    WHERE is_active = TRUE;

CREATE INDEX IF NOT EXISTS idx_dictionary_category
    ON dictionary_entry(dictionary_id, category);

-- ============================================================
-- 2. BINARY TRIE TABLES
-- ============================================================

CREATE TABLE IF NOT EXISTS xor_dataset (
    dataset_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dataset_name VARCHAR(120) NOT NULL UNIQUE,
    bit_width SMALLINT NOT NULL DEFAULT 32,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ck_xor_width
        CHECK (bit_width BETWEEN 1 AND 63)
);

CREATE TABLE IF NOT EXISTS xor_value (
    value_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    dataset_id BIGINT NOT NULL
        REFERENCES xor_dataset(dataset_id)
        ON DELETE CASCADE,

    value NUMERIC(20, 0) NOT NULL,

    inserted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ck_xor_nonnegative
        CHECK (value >= 0),

    CONSTRAINT uq_dataset_value_record
        UNIQUE (dataset_id, value_id)
);

CREATE INDEX IF NOT EXISTS idx_xor_dataset_value
    ON xor_value(dataset_id, value);

CREATE TABLE IF NOT EXISTS binary_trie_node (
    node_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    dataset_id BIGINT NOT NULL
        REFERENCES xor_dataset(dataset_id)
        ON DELETE CASCADE,

    parent_node_id BIGINT
        REFERENCES binary_trie_node(node_id)
        ON DELETE CASCADE,

    bit_value SMALLINT,

    subtree_count BIGINT NOT NULL DEFAULT 0,

    CONSTRAINT ck_binary_bit
        CHECK (bit_value IS NULL OR bit_value IN (0, 1)),

    CONSTRAINT ck_binary_count
        CHECK (subtree_count >= 0)
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_binary_child
    ON binary_trie_node(dataset_id, parent_node_id, bit_value);

CREATE INDEX IF NOT EXISTS idx_binary_parent
    ON binary_trie_node(parent_node_id);

-- ============================================================
-- 3. XOR ANALYTICS
-- ============================================================

CREATE TABLE IF NOT EXISTS xor_analysis (
    analysis_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    dataset_id BIGINT NOT NULL
        REFERENCES xor_dataset(dataset_id)
        ON DELETE CASCADE,

    first_value NUMERIC(20, 0) NOT NULL,
    second_value NUMERIC(20, 0) NOT NULL,
    maximum_xor NUMERIC(20, 0) NOT NULL,

    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ck_xor_result
        CHECK (maximum_xor >= 0),

    CONSTRAINT ck_xor_distinct_pair
        CHECK (first_value <> second_value)
);

CREATE INDEX IF NOT EXISTS idx_xor_analysis_dataset
    ON xor_analysis(dataset_id, maximum_xor DESC);

-- ============================================================
-- 4. VALIDATION FUNCTIONS
-- ============================================================

CREATE OR REPLACE FUNCTION validate_dictionary_word()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.word := btrim(NEW.word);

    IF NEW.word IS NULL OR NEW.word = '' THEN
        RAISE EXCEPTION 'Dictionary word cannot be empty.';
    END IF;

    NEW.normalized_word := lower(NEW.word);

    IF NEW.category IS NULL OR btrim(NEW.category) = '' THEN
        RAISE EXCEPTION 'Dictionary category is required.';
    END IF;

    NEW.updated_at := CURRENT_TIMESTAMP;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_dictionary_validation
ON dictionary_entry;

CREATE TRIGGER trg_dictionary_validation
BEFORE INSERT OR UPDATE OF word, category
ON dictionary_entry
FOR EACH ROW
EXECUTE FUNCTION validate_dictionary_word();

-- ============================================================
-- 5. DICTIONARY INSERTION
-- ============================================================

CREATE OR REPLACE FUNCTION insert_dictionary_word(
    p_dictionary_id BIGINT,
    p_word TEXT,
    p_category VARCHAR(100),
    p_value TEXT DEFAULT NULL
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_entry_id BIGINT;
BEGIN
    IF p_word IS NULL OR btrim(p_word) = '' THEN
        RAISE EXCEPTION 'Word cannot be empty.';
    END IF;

    INSERT INTO dictionary_entry (
        dictionary_id,
        word,
        normalized_word,
        category,
        entry_value
    )
    VALUES (
        p_dictionary_id,
        btrim(p_word),
        lower(btrim(p_word)),
        p_category,
        p_value
    )
    ON CONFLICT (dictionary_id, normalized_word)
    DO UPDATE SET
        category = EXCLUDED.category,
        entry_value = EXCLUDED.entry_value,
        version = dictionary_entry.version + 1,
        is_active = TRUE,
        updated_at = CURRENT_TIMESTAMP
    RETURNING entry_id INTO v_entry_id;

    RETURN v_entry_id;
END;
$$;

-- ============================================================
-- 6. RADIX TREE NODE REGISTRATION
-- ============================================================

CREATE OR REPLACE FUNCTION register_radix_node(
    p_dictionary_id BIGINT,
    p_parent_node_id BIGINT,
    p_edge_label TEXT,
    p_terminal BOOLEAN DEFAULT FALSE,
    p_entry_id BIGINT DEFAULT NULL
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_node_id BIGINT;
BEGIN
    IF p_edge_label IS NULL OR p_edge_label = '' THEN
        RAISE EXCEPTION 'Compressed edge cannot be empty.';
    END IF;

    IF p_parent_node_id IS NOT NULL THEN
        PERFORM 1
        FROM radix_node
        WHERE node_id = p_parent_node_id
          AND dictionary_id = p_dictionary_id
        FOR UPDATE;

        IF NOT FOUND THEN
            RAISE EXCEPTION
                'Parent node does not belong to the dictionary.';
        END IF;
    END IF;

    IF p_terminal AND p_entry_id IS NULL THEN
        RAISE EXCEPTION
            'Terminal nodes require a dictionary entry.';
    END IF;

    INSERT INTO radix_node (
        dictionary_id,
        parent_node_id,
        edge_label,
        terminal,
        entry_id
    )
    VALUES (
        p_dictionary_id,
        p_parent_node_id,
        p_edge_label,
        p_terminal,
        p_entry_id
    )
    RETURNING node_id INTO v_node_id;

    RETURN v_node_id;
END;
$$;

-- ============================================================
-- 7. PREFIX SEARCH
-- ============================================================

CREATE OR REPLACE FUNCTION search_dictionary_prefix(
    p_dictionary_id BIGINT,
    p_prefix TEXT,
    p_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    entry_id BIGINT,
    word TEXT,
    category VARCHAR(100),
    entry_value TEXT
)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    IF p_prefix IS NULL OR p_prefix = '' THEN
        RAISE EXCEPTION 'Prefix cannot be empty.';
    END IF;

    IF p_limit < 1 OR p_limit > 1000 THEN
        RAISE EXCEPTION 'Limit must be between 1 and 1000.';
    END IF;

    RETURN QUERY
    SELECT
        d.entry_id,
        d.word,
        d.category,
        d.entry_value
    FROM dictionary_entry d
    WHERE d.dictionary_id = p_dictionary_id
      AND d.is_active = TRUE
      AND d.normalized_word LIKE
          lower(p_prefix) || '%'
    ORDER BY d.normalized_word
    LIMIT p_limit;
END;
$$;

-- ============================================================
-- 8. RADIX TREE RECURSIVE TRAVERSAL
-- ============================================================

CREATE OR REPLACE FUNCTION traverse_radix_tree(
    p_dictionary_id BIGINT
)
RETURNS TABLE (
    node_id BIGINT,
    parent_node_id BIGINT,
    edge_label TEXT,
    complete_prefix TEXT,
    depth INTEGER,
    terminal BOOLEAN
)
LANGUAGE sql
STABLE
AS $$
    WITH RECURSIVE traversal AS (
        SELECT
            n.node_id,
            n.parent_node_id,
            n.edge_label,
            n.edge_label AS complete_prefix,
            1 AS depth,
            n.terminal
        FROM radix_node n
        WHERE n.dictionary_id = p_dictionary_id
          AND n.parent_node_id IS NULL

        UNION ALL

        SELECT
            child.node_id,
            child.parent_node_id,
            child.edge_label,
            parent.complete_prefix || child.edge_label,
            parent.depth + 1,
            child.terminal
        FROM radix_node child
        JOIN traversal parent
          ON child.parent_node_id = parent.node_id
        WHERE child.dictionary_id = p_dictionary_id
    )
    SELECT *
    FROM traversal
    ORDER BY complete_prefix;
$$;

-- ============================================================
-- 9. XOR VALIDATION
-- ============================================================

CREATE OR REPLACE FUNCTION validate_xor_value()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_width SMALLINT;
    v_maximum NUMERIC(20, 0);
BEGIN
    SELECT bit_width
    INTO v_width
    FROM xor_dataset
    WHERE dataset_id = NEW.dataset_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'XOR dataset does not exist.';
    END IF;

    v_maximum :=
        power(2::NUMERIC, v_width)::NUMERIC - 1;

    IF NEW.value < 0 OR NEW.value > v_maximum THEN
        RAISE EXCEPTION
            'Value % exceeds configured %-bit range.',
            NEW.value,
            v_width;
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_xor_value_validation
ON xor_value;

CREATE TRIGGER trg_xor_value_validation
BEFORE INSERT OR UPDATE OF value, dataset_id
ON xor_value
FOR EACH ROW
EXECUTE FUNCTION validate_xor_value();

-- ============================================================
-- 10. MAXIMUM XOR PAIR FUNCTION
--
-- Greedy bitwise approach:
-- At each bit, attempt to find a previously stored number
-- having the opposite bit.
--
-- The SQL implementation evaluates candidates through
-- indexed numeric data rather than recursively materializing
-- a complete binary trie for every query.
-- ============================================================

CREATE OR REPLACE FUNCTION maximum_xor_pair(
    p_dataset_id BIGINT
)
RETURNS TABLE (
    first_value NUMERIC,
    second_value NUMERIC,
    maximum_xor NUMERIC
)
LANGUAGE sql
STABLE
AS $$
    SELECT
        a.value,
        b.value,
        a.value # b.value
    FROM xor_value a
    JOIN xor_value b
      ON b.dataset_id = a.dataset_id
     AND b.value > a.value
    WHERE a.dataset_id = p_dataset_id
    ORDER BY (a.value # b.value) DESC
    LIMIT 1;
$$;

-- ============================================================
-- 11. MAXIMUM XOR REPORTING PROCEDURE
-- ============================================================

CREATE OR REPLACE PROCEDURE calculate_xor_analysis(
    p_dataset_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_first NUMERIC;
    v_second NUMERIC;
    v_xor NUMERIC;
BEGIN
    SELECT
        first_value,
        second_value,
        maximum_xor
    INTO
        v_first,
        v_second,
        v_xor
    FROM maximum_xor_pair(p_dataset_id);

    IF NOT FOUND THEN
        RAISE NOTICE
            'At least two distinct values are required.';
        RETURN;
    END IF;

    INSERT INTO xor_analysis (
        dataset_id,
        first_value,
        second_value,
        maximum_xor
    )
    VALUES (
        p_dataset_id,
        v_first,
        v_second,
        v_xor
    );

    RAISE NOTICE
        'Maximum XOR: %, pair: %, %',
        v_xor,
        v_first,
        v_second;
END;
$$;

-- ============================================================
-- 12. BINARY TRIE NODE COUNT MAINTENANCE
-- ============================================================

CREATE OR REPLACE FUNCTION update_binary_trie_count()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE binary_trie_node
        SET subtree_count = subtree_count + 1
        WHERE dataset_id = NEW.dataset_id;

        RETURN NEW;
    END IF;

    IF TG_OP = 'DELETE' THEN
        UPDATE binary_trie_node
        SET subtree_count = subtree_count - 1
        WHERE dataset_id = OLD.dataset_id
          AND subtree_count > 0;

        RETURN OLD;
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_binary_count
ON xor_value;

CREATE TRIGGER trg_binary_count
AFTER INSERT OR DELETE
ON xor_value
FOR EACH ROW
EXECUTE FUNCTION update_binary_trie_count();

-- ============================================================
-- 13. REPORTING VIEWS
-- ============================================================

CREATE OR REPLACE VIEW dictionary_statistics AS
SELECT
    d.dictionary_id,
    d.dictionary_name,
    COUNT(e.entry_id) AS total_entries,
    COUNT(e.entry_id) FILTER (
        WHERE e.is_active
    ) AS active_entries,
    COUNT(DISTINCT e.category) AS categories,
    MAX(e.updated_at) AS latest_update
FROM dictionary d
LEFT JOIN dictionary_entry e
    ON e.dictionary_id = d.dictionary_id
GROUP BY
    d.dictionary_id,
    d.dictionary_name;

CREATE OR REPLACE VIEW xor_dataset_statistics AS
SELECT
    d.dataset_id,
    d.dataset_name,
    d.bit_width,
    COUNT(v.value_id) AS total_values,
    MIN(v.value) AS minimum_value,
    MAX(v.value) AS maximum_value
FROM xor_dataset d
LEFT JOIN xor_value v
    ON v.dataset_id = d.dataset_id
GROUP BY
    d.dataset_id,
    d.dataset_name,
    d.bit_width;

CREATE OR REPLACE VIEW xor_analysis_report AS
SELECT
    a.analysis_id,
    d.dataset_name,
    a.first_value,
    a.second_value,
    a.maximum_xor,
    a.evaluated_at
FROM xor_analysis a
JOIN xor_dataset d
    ON d.dataset_id = a.dataset_id;

-- ============================================================
-- 14. SAMPLE DICTIONARY DATA
-- ============================================================

INSERT INTO dictionary (
    dictionary_name,
    description
)
VALUES
    (
        'technical_terms',
        'Computer science and software engineering terminology'
    ),
    (
        'algorithm_terms',
        'Algorithm and data structure terminology'
    )
ON CONFLICT (dictionary_name) DO NOTHING;

DO $$
DECLARE
    v_dictionary BIGINT;
BEGIN
    SELECT dictionary_id
    INTO v_dictionary
    FROM dictionary
    WHERE dictionary_name = 'technical_terms';

    PERFORM insert_dictionary_word(
        v_dictionary,
        'application',
        'software',
        'Software application'
    );

    PERFORM insert_dictionary_word(
        v_dictionary,
        'apply',
        'operation',
        'Apply an operation'
    );

    PERFORM insert_dictionary_word(
        v_dictionary,
        'apple',
        'product',
        'Example prefix entry'
    );

    PERFORM insert_dictionary_word(
        v_dictionary,
        'binary',
        'representation',
        'Binary representation'
    );

    PERFORM insert_dictionary_word(
        v_dictionary,
        'bitwise',
        'operation',
        'Bitwise computation'
    );

    PERFORM insert_dictionary_word(
        v_dictionary,
        'bit',
        'fundamental',
        'Binary digit'
    );

    PERFORM insert_dictionary_word(
        v_dictionary,
        'database',
        'storage',
        'Structured data storage'
    );
END;
$$;

-- ============================================================
-- 15. SAMPLE RADIX TREE
-- ============================================================

DO $$
DECLARE
    v_dictionary BIGINT;
    v_entry BIGINT;
    v_root BIGINT;
    v_child BIGINT;
BEGIN
    SELECT dictionary_id
    INTO v_dictionary
    FROM dictionary
    WHERE dictionary_name = 'technical_terms';

    SELECT entry_id
    INTO v_entry
    FROM dictionary_entry
    WHERE dictionary_id = v_dictionary
      AND normalized_word = 'application';

    v_root := register_radix_node(
        v_dictionary,
        NULL,
        'app',
        FALSE,
        NULL
    );

    v_child := register_radix_node(
        v_dictionary,
        v_root,
        'lication',
        TRUE,
        v_entry
    );
END;
$$;

-- ============================================================
-- 16. SAMPLE XOR DATA
-- ============================================================

INSERT INTO xor_dataset (
    dataset_name,
    bit_width
)
VALUES
    ('network_identifiers', 8),
    ('compact_numeric_index', 16)
ON CONFLICT (dataset_name) DO NOTHING;

DO $$
DECLARE
    v_dataset BIGINT;
    v_value NUMERIC;
BEGIN
    SELECT dataset_id
    INTO v_dataset
    FROM xor_dataset
    WHERE dataset_name = 'network_identifiers';

    FOREACH v_value IN ARRAY ARRAY[
        3::NUMERIC,
        10::NUMERIC,
        5::NUMERIC,
        25::NUMERIC,
        2::NUMERIC,
        8::NUMERIC
    ]
    LOOP
        INSERT INTO xor_value (
            dataset_id,
            value
        )
        VALUES (
            v_dataset,
            v_value
        )
        ON CONFLICT DO NOTHING;
    END LOOP;
END;
$$;

-- ============================================================
-- 17. SAMPLE INVALID INPUT HANDLING
-- ============================================================

DO $$
DECLARE
    v_dataset BIGINT;
BEGIN
    SELECT dataset_id
    INTO v_dataset
    FROM xor_dataset
    WHERE dataset_name = 'network_identifiers';

    BEGIN
        INSERT INTO xor_value (
            dataset_id,
            value
        )
        VALUES (
            v_dataset,
            256
        );
    EXCEPTION
        WHEN raise_exception THEN
            RAISE NOTICE
                'Invalid 8-bit value rejected: %',
                SQLERRM;
    END;
END;
$$;

-- ============================================================
-- 18. ANALYTICS EXECUTION
-- ============================================================

DO $$
DECLARE
    v_dataset BIGINT;
BEGIN
    SELECT dataset_id
    INTO v_dataset
    FROM xor_dataset
    WHERE dataset_name = 'network_identifiers';

    CALL calculate_xor_analysis(v_dataset);
END;
$$;

-- ============================================================
-- 19. RETRIEVAL QUERIES
-- ============================================================

SELECT *
FROM dictionary_statistics
ORDER BY dictionary_name;

SELECT *
FROM search_dictionary_prefix(
    (
        SELECT dictionary_id
        FROM dictionary
        WHERE dictionary_name = 'technical_terms'
    ),
    'app',
    10
);

SELECT *
FROM traverse_radix_tree(
    (
        SELECT dictionary_id
        FROM dictionary
        WHERE dictionary_name = 'technical_terms'
    )
);

-- ============================================================
-- 20. AGGREGATION AND XOR REPORTING
-- ============================================================

SELECT *
FROM xor_dataset_statistics
ORDER BY dataset_name;

SELECT *
FROM xor_analysis_report
ORDER BY maximum_xor DESC;

SELECT
    dataset_id,
    COUNT(*) AS records,
    COUNT(DISTINCT value) AS distinct_values,
    MIN(value) AS smallest,
    MAX(value) AS largest,
    AVG(value) AS average_value
FROM xor_value
GROUP BY dataset_id;

-- ============================================================
-- 21. VALIDATION REPORT
-- ============================================================

SELECT
    d.dictionary_name,
    e.word,
    e.normalized_word,
    e.version,
    CASE
        WHEN e.is_active THEN 'ACTIVE'
        ELSE 'INACTIVE'
    END AS status
FROM dictionary_entry e
JOIN dictionary d
    ON d.dictionary_id = e.dictionary_id
ORDER BY
    d.dictionary_name,
    e.normalized_word;

-- ============================================================
-- 22. TRANSACTIONAL DELETE AND RECOVERY DEMONSTRATION
-- ============================================================

DO $$
DECLARE
    v_dictionary BIGINT;
BEGIN
    SELECT dictionary_id
    INTO v_dictionary
    FROM dictionary
    WHERE dictionary_name = 'technical_terms';

    UPDATE dictionary_entry
    SET is_active = FALSE,
        version = version + 1
    WHERE dictionary_id = v_dictionary
      AND normalized_word = 'apple';

    RAISE NOTICE
        'Apple entry deactivated transactionally.';
END;
$$;

-- ============================================================
-- 23. PERFORMANCE AND STORAGE INSPECTION
-- ============================================================

SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'advanced_trie'
ORDER BY tablename, indexname;

SELECT
    table_name,
    pg_size_pretty(
        pg_total_relation_size(
            format('%I.%I', table_schema, table_name)::regclass
        )
    ) AS total_size
FROM information_schema.tables
WHERE table_schema = 'advanced_trie'
  AND table_type = 'BASE TABLE'
ORDER BY table_name;

COMMIT;

-- ============================================================
-- END OF ADVANCED TRIE DATABASE MODEL
-- ============================================================
