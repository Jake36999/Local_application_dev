"""\n⚠️  DEPRECATED: This script is deprecated as of v2.0\n\nUse the unified verification workflow instead:\n    python workflows/workflow_verify.py\n\nSee MIGRATION_GUIDE.md for details.\nThis script will be removed in v3.0 (Q4 2026).\n"""\n\nimport sys\nimport sqlite3\n\nprint("\\n" + "="*60)\nprint("⚠️  DEPRECATION WARNING")\nprint("="*60)\nprint("This script is deprecated. Use: python workflows/workflow_verify.py")\nprint("See: MIGRATION_GUIDE.md")\nprint("="*60 + "\\n")\n\nresponse = input("Continue anyway? (y/N): ")\nif response.lower() != 'y':\n    print("Aborted. Use: python workflows/workflow_verify.py")\n    sys.exit(0)\n\nconn = sqlite3.connect('canon.db')
c = conn.cursor()

print("All component kinds:")
for row in c.execute('SELECT kind, COUNT(*) as cnt FROM canon_components GROUP BY kind ORDER BY cnt DESC'):
    print(f"  {row[0]}: {row[1]}")

print("\nAll components (top-level only):")
for row in c.execute('SELECT kind, name FROM canon_components WHERE parent_id IS NULL ORDER BY order_index'):
    print(f"  {row[0]}: {row[1][:60]}")

print("\nTotal top-level components:")
count = c.execute('SELECT COUNT(*) FROM canon_components WHERE parent_id IS NULL').fetchone()[0]
print(f"  {count}")
