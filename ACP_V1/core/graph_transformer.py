import sqlite3
import json
from fastapi import APIRouter, HTTPException

router = APIRouter()
DB_PATH = "memory/sql/project_meta.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@router.get("/system/graph")
async def get_system_graph():
    nodes = []
    links = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            rows = cursor.execute("SELECT id, name, type, dependencies, stability_score FROM canon_components").fetchall()
        except sqlite3.OperationalError:
            return {"nodes": [], "links": []}
        for row in rows:
            nodes.append({
                "id": row["name"],
                "group": row["type"],
                "val": row["stability_score"] if row["stability_score"] else 1,
                "details": f"Type: {row['type']}"
            })
            deps = row["dependencies"]
            if deps:
                try:
                    dep_list = json.loads(deps) if deps.startswith('[') else deps.split(',')
                    for dep in dep_list:
                        links.append({
                            "source": row["name"],
                            "target": dep.strip(),
                            "value": 1
                        })
                except:
                    pass
        conn.close()
        return {"nodes": nodes, "links": links}
    except Exception as e:
        print(f"Graph Error: {e}")
        return {"nodes": [], "links": []}
