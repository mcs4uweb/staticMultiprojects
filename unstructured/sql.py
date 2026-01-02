import sqlite3

conn = sqlite3.connect("chroma_db/chroma.sqlite3")
cursor = conn.cursor()

# Query the Chroma FTS content table (schema uses id + c0)
cursor.execute("""
    SELECT id, c0
    FROM embedding_fulltext_search_content
    ORDER BY id
""")

rows = cursor.fetchall()
print(f"? Found {len(rows)} document chunks\n")

for doc_id, content in rows:
    cursor.execute("""
        SELECT key, string_value, int_value, float_value, bool_value
        FROM embedding_metadata
        WHERE id = ?
        ORDER BY key
    """, (doc_id,))
    meta_rows = cursor.fetchall()

    metadata = {}
    for key, s_val, i_val, f_val, b_val in meta_rows:
        if s_val is not None:
            metadata[key] = s_val
        elif i_val is not None:
            metadata[key] = i_val
        elif f_val is not None:
            metadata[key] = f_val
        elif b_val is not None:
            metadata[key] = bool(b_val)

    source = metadata.get("source", "unknown")

    print(f"--- Chunk ID: {doc_id} ---")
    print(f"?? Source: {source}")
    print(f"?? Content (first 200 chars): {content[:200]}...\n")

conn.close()
