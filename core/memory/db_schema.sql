-- Personal Local AI Workstation Memory & Vector Database Schema

-- 1. Conversation Logs Table
CREATE TABLE IF NOT EXISTS conversation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    model_used TEXT,
    embedding TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Code AST Nodes Table
CREATE TABLE IF NOT EXISTS code_ast_nodes (
    id TEXT PRIMARY KEY,
    file_path TEXT NOT NULL,
    node_type TEXT NOT NULL, -- 'class', 'function', 'async_function', 'method', 'component'
    node_name TEXT NOT NULL,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    docstring TEXT,
    source_code TEXT NOT NULL,
    embedding TEXT, -- JSON array of float vector embeddings
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Session State Memory Table
CREATE TABLE IF NOT EXISTS session_state_memory (
    key TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. FTS5 Virtual Tables for BM25 Keyword Search
CREATE VIRTUAL TABLE IF NOT EXISTS code_ast_fts USING fts5(
    node_id UNINDEXED,
    file_path,
    node_name,
    docstring,
    source_code
);

CREATE VIRTUAL TABLE IF NOT EXISTS conversation_fts USING fts5(
    log_id UNINDEXED,
    session_id,
    role,
    content
);

-- Indexes for fast metadata lookups
CREATE INDEX IF NOT EXISTS idx_code_ast_file ON code_ast_nodes(file_path);
CREATE INDEX IF NOT EXISTS idx_code_ast_name ON code_ast_nodes(node_name);
CREATE INDEX IF NOT EXISTS idx_conversation_session ON conversation_logs(session_id);
