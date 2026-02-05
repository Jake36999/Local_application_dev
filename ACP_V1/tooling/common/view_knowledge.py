import sqlite3
import pandas as pd  # type: ignore

def view_data():
    conn = sqlite3.connect("memory/sql/project_meta.db")
    cursor = conn.cursor()
    
    print("\n--- 🧠 CAPTURED KNOWLEDGE (Canon Components) ---")
    cursor.execute("SELECT kind, name, file FROM canon_components")
    rows = cursor.fetchall()
    
    if not rows:
        print("[Empty] No code indexed yet.")
    else:
        print(f"{'TYPE':<15} | {'NAME':<25} | {'SOURCE'}")
        print("-" * 60)
        for r in rows:
            print(f"{r[0]:<15} | {r[1]:<25} | {r[2]}")

    conn.close()

if __name__ == "__main__":
    view_data()