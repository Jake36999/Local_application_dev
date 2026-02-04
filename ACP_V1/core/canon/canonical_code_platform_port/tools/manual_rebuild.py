import sqlite3
import ast
import hashlib

conn = sqlite3.connect('canon.db')
c = conn.cursor()

def sha(s):
    return hashlib.sha256(s.encode()).hexdigest()

# Get file record
fid, raw_hash, ast_hash = c.execute('SELECT file_id, raw_hash_sha256, ast_hash_sha256 FROM canon_files LIMIT 1').fetchone()

print(f"Expected raw hash: {raw_hash}")
print(f"Expected AST hash: {ast_hash}\n")

# Reconstruct
rebuilt_parts = []
query_result = c.execute('SELECT component_id FROM canon_components WHERE file_id=? AND parent_id IS NULL ORDER BY order_index', (fid,)).fetchall()
print(f"Query returned {len(query_result)} rows")

for i, (cid,) in enumerate(query_result):
    src_row = c.execute('SELECT source_text FROM canon_source_segments WHERE component_id=?', (cid,)).fetchone()
    if src_row and src_row[0]:
        rebuilt_parts.append(src_row[0])
        print(f"  {i+1}. Added: {len(src_row[0])} bytes")
    else:
        print(f"  {i+1}. MISSING or EMPTY segment for {cid[:8]}...")

rebuilt_src = '\n\n'.join(rebuilt_parts)

print(f"\nTotal rebuilt: {len(rebuilt_parts)} parts = {len(rebuilt_src)} bytes")
print(f"Rebuilt raw hash: {sha(rebuilt_src)}")
print(f"Raw match: {sha(rebuilt_src) == raw_hash}\n")

try:
    tree = ast.parse(rebuilt_src)
    ast_dump = ast.dump(tree)
    rebuilt_ast_hash = sha(ast_dump)
    print(f"Rebuilt AST hash: {rebuilt_ast_hash}")
    print(f"AST match: {rebuilt_ast_hash == ast_hash}")
except SyntaxError as e:
    print(f"SyntaxError: {e}")
