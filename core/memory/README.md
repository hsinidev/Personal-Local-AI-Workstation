# Core Memory Engine

SQLite + Local Vector Embeddings Engine providing long-term semantic memory storage, document chunking, and similarity indexing for the Personal Local AI Workstation.

## Components
- `schema.sql`: Database schema definition for memory chunks and conversation logs.
- `db.py`: SQLite connection manager and CRUD interfaces.
- `embeddings.py`: Cosine similarity calculation & vector index search logic.
