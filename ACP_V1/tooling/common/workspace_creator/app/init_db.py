import sqlite3

def init_db():
    conn = sqlite3.connect("project_meta.db")
    cursor = conn.cursor()
    
    # 1. Table for "Deep AST" (Canon Scanner)
    # Stores the actual code structure (Functions, Classes)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS canon_components (
            id TEXT PRIMARY KEY,
            file TEXT,
            kind TEXT,
            name TEXT,
            code_snippet TEXT
        )
    ''')

    # 2. Table for "Shadow Observer" (Dependency Logger)
    # Stores the graph of imports without telemetry
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dependencies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_file TEXT,
            module TEXT,
            timestamp TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized: 'project_meta.db' with tables [canon_components, dependencies]")

if __name__ == "__main__":
    init_db()