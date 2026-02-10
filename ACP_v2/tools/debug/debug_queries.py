import sqlite3

conn = sqlite3.connect('canon.db')
c = conn.cursor()

# Get file ID
fid = c.execute('SELECT file_id FROM canon_files LIMIT 1').fetchone()[0]
print(f"File ID: {fid}\n")

# Query 1: Get top-level component IDs
print("Top-level components:")
comps = c.execute('SELECT component_id FROM canon_components WHERE file_id=? AND parent_id IS NULL ORDER BY order_index', (fid,)).fetchall()
print(f"  Found {len(comps)} components")
for i, (cid,) in enumerate(comps[:3]):
    print(f"    {i+1}. {cid[:8]}...")

# Query 2: For each, check source_text
print("\nChecking source_text for each:")
for i, (cid,) in enumerate(comps):
    result = c.execute('SELECT source_text FROM canon_source_segments WHERE component_id=?', (cid,)).fetchone()
    if result:
        src = result[0]
        preview = (src[:30] if src else "(empty)").replace('\n', '\\n')
        print(f"  {i+1}. {cid[:8]}... -> {len(src) if src else 0} bytes: {preview}")
    else:
        print(f"  {i+1}. {cid[:8]}... -> NO RESULT")
