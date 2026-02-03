"""\n⚠️  DEPRECATED: This script is deprecated as of v2.0\n\nUse the unified verification workflow instead:\n    python workflows/workflow_verify.py\n\nSee MIGRATION_GUIDE.md for details.\nThis script will be removed in v3.0 (Q4 2026).\n"""\n\nimport sys\nimport sqlite3\n\nprint("\\n" + "="*60)\nprint("⚠️  DEPRECATION WARNING")\nprint("="*60)\nprint("This script is deprecated. Use: python workflows/workflow_verify.py")\nprint("See: MIGRATION_GUIDE.md")\nprint("="*60 + "\\n")\n\nresponse = input("Continue anyway? (y/N): ")\nif response.lower() != 'y':\n    print("Aborted. Use: python workflows/workflow_verify.py")\n    sys.exit(0)\n\nconn = sqlite3.connect('canon.db')
c = conn.cursor()

fid = c.execute('SELECT file_id FROM canon_files LIMIT 1').fetchone()[0]

# Fetch top-level components
comps = c.execute('''
    SELECT component_id FROM canon_components 
    WHERE file_id=? AND parent_id IS NULL ORDER BY order_index
''', (fid,)).fetchall()

print(f"Top-level components: {len(comps)}")
for i, (cid,) in enumerate(comps):
    src_row = c.execute(
        'SELECT source_text FROM canon_source_segments WHERE component_id=?', (cid,)
    ).fetchone()
    if src_row:
        text = src_row[0]
        preview = (text[:40] if text else "(empty)").replace('\n', '\\n')
        print(f"  {i+1}. {cid[:8]}... -> {len(text)} bytes: {preview}")
    else:
        print(f"  {i+1}. {cid[:8]}... -> NO SOURCE")

# Now actually rebuild
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
        print(f"WARNING: No source for component {cid}")

rebuilt_text = '\n\n'.join(rebuilt)
print(f"\nRebuilt: {len(rebuilt)} components, total {len(rebuilt_text)} bytes")
print(f"First 100 chars: {rebuilt_text[:100]}")
