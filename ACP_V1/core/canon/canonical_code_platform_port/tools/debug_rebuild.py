import sqlite3
import ast
import hashlib

conn = sqlite3.connect('canon.db')
c = conn.cursor()

# Get the file record
fid, raw_hash, ast_hash = c.execute('''
    SELECT file_id, raw_hash_sha256, ast_hash_sha256 FROM canon_files LIMIT 1
''').fetchone()

print(f"File ID: {fid}")
print(f"Expected raw hash: {raw_hash}")
print(f"Expected AST hash: {ast_hash}")

# Fetch top-level components
comps = c.execute('''
    SELECT component_id, kind, name FROM canon_components 
    WHERE file_id=? AND parent_id IS NULL ORDER BY order_index
''', (fid,)).fetchall()

print(f"\nTop-level components ({len(comps)}):")
for i, (cid, kind, name) in enumerate(comps):
    src = c.execute('SELECT source_text FROM canon_source_segments WHERE component_id=?', (cid,)).fetchone()
    text = src[0] if src else "(no source)"
    preview = text[:50].replace('\n', '\\n') if src else ""
    print(f"  {i+1}. [{kind}] {name}: {preview}...")

# Rebuild
rebuilt = []
for (cid,) in c.execute('''
    SELECT component_id FROM canon_components 
    WHERE file_id=? AND parent_id IS NULL ORDER BY order_index
''', (fid,)):
    src_row = c.execute(
        'SELECT source_text FROM canon_source_segments WHERE component_id=?', (cid,)
    ).fetchone()
    if src_row:
        rebuilt.append(src_row[0])
    else:
        print(f"WARNING: No source for {cid}")

rebuilt_text = '\n\n'.join(rebuilt)

def sha(s):
    return hashlib.sha256(s.encode()).hexdigest()

print(f"\nRebuilt length: {len(rebuilt_text)} bytes")
print(f"Rebuilt raw hash: {sha(rebuilt_text)}")
print(f"Raw match: {sha(rebuilt_text) == raw_hash}")

try:
    ast_obj = ast.parse(rebuilt_text)
    print(f"Rebuilt AST hash: {sha(ast.dump(ast_obj))}")
    print(f"AST match: {sha(ast.dump(ast_obj)) == ast_hash}")
except SyntaxError as e:
    print(f"SyntaxError in rebuilt: {e}")
