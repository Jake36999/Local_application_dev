"""
    ⚠️  DEPRECATED: This script is deprecated as of v2.0
    Use the unified verification workflow instead:
        python workflows/workflow_verify.py
    See MIGRATION_GUIDE.md for details.
    This script will be removed in v3.0 (Q4 2026).
"""
import sys
import sqlite3
print("\n" + "="*60)
print("⚠️  DEPRECATION WARNING")
print("="*60)
print("This script is deprecated. Use: python workflows/workflow_verify.py")
print("See: MIGRATION_GUIDE.md")
print("="*60 + "\n")
response = input("Continue anyway? (y/N): ")
if response.lower() != 'y':
    print("Aborted. Use: python workflows/workflow_verify.py")
    sys.exit(0)
conn = sqlite3.connect('canon.db')
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
