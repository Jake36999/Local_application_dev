"""FastAPI bridge exposing canon graph data for the React frontend.

Endpoints:
- GET /api/graph/nodes: Return canon_components enriched with params/types/drift overlays.
- GET /api/graph/edges: Return call_graph_edges with call_kind styling info.
- POST /api/action/connect: Create a new connection (canon_calls + call_graph_edges).
- GET /api/analysis/dag: Build a DAG from current call graph for live animation.
"""
from __future__ import annotations

import sqlite3
import uuid
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.canon_db import init_db
from ACP_V1.brain.workflow_analyzer import WorkflowAnalyzer

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "canon.db"

app = FastAPI(title="Canonical Graph API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure tables exist for this database path
init_db(str(DB_PATH))
_analyzer = WorkflowAnalyzer()


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


class ConnectPayload(BaseModel):
    source_id: str
    target_id: str
    call_kind: Optional[str] = "direct"
    lineno: Optional[int] = None


@app.get("/api/graph/nodes")
def get_nodes():
    conn = get_connection()
    try:
        components = conn.execute("SELECT * FROM canon_components").fetchall()
        params = conn.execute("SELECT * FROM canon_variables WHERE is_param = 1").fetchall()
        types = conn.execute(
            """
            SELECT ct.*, cv.name AS variable_name
            FROM canon_types ct
            LEFT JOIN canon_variables cv ON cv.variable_id = ct.variable_id
            """
        ).fetchall()
        drifts = conn.execute("SELECT * FROM drift_events").fetchall()
        best_practices = conn.execute("SELECT * FROM overlay_best_practice").fetchall()

        params_by_component: Dict[str, List[dict]] = defaultdict(list)
        for row in params:
            params_by_component[row["component_id"]].append(
                {
                    "variable_id": row["variable_id"],
                    "name": row["name"],
                    "type_hint": row["type_hint"],
                    "lineno": row["lineno"],
                }
            )

        outputs_by_component: Dict[str, List[dict]] = defaultdict(list)
        for row in types:
            outputs_by_component[row["component_id"]].append(
                {
                    "variable_id": row["variable_id"],
                    "name": row["variable_name"],
                    "type_annotation": row["type_annotation"],
                    "inferred_type": row["inferred_type"],
                }
            )

        drift_by_component = {row["component_id"]: row for row in drifts}
        practices_by_component: Dict[str, List[dict]] = defaultdict(list)
        for row in best_practices:
            practices_by_component[row["component_id"]].append(
                {
                    "practice_id": row["practice_id"],
                    "severity": row["severity"],
                    "message": row["message"],
                    "rule_id": row["rule_id"],
                }
            )

        nodes = []
        for component in components:
            component_id = component["component_id"]
            nodes.append(
                {
                    "id": component_id,
                    "type": component["kind"] or "service",
                    "position": {"x": 0, "y": 0},
                    "data": {
                        "label": component["qualified_name"] or component["name"],
                        "parent_id": component["parent_id"],
                        "parameters": params_by_component.get(component_id, []),
                        "outputs": outputs_by_component.get(component_id, []),
                        "drift": drift_by_component.get(component_id),
                        "best_practices": practices_by_component.get(component_id, []),
                        "order_index": component["order_index"],
                        "kind": component["kind"],
                    },
                }
            )

        return nodes
    finally:
        conn.close()


@app.get("/api/graph/edges")
def get_edges():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM call_graph_edges").fetchall()
        edges = []
        for row in rows:
            edge_id = row["edge_id"] or f"{row['caller_id']}->{row['callee_id']}"
            call_kind = row["call_kind"] or "direct"
            edges.append(
                {
                    "id": edge_id,
                    "source": row["caller_id"],
                    "target": row["callee_id"],
                    "data": {
                        "call_kind": call_kind,
                        "resolved_name": row["resolved_name"],
                    },
                    "style": "dashed" if call_kind == "event" else "solid",
                }
            )
        return edges
    finally:
        conn.close()


@app.post("/api/action/connect")
def connect_components(payload: ConnectPayload):
    conn = get_connection()
    cur = conn.cursor()
    try:
        source_exists = cur.execute(
            "SELECT 1 FROM canon_components WHERE component_id = ?",
            (payload.source_id,),
        ).fetchone()
        target_exists = cur.execute(
            "SELECT 1 FROM canon_components WHERE component_id = ?",
            (payload.target_id,),
        ).fetchone()

        if not source_exists or not target_exists:
            raise HTTPException(status_code=404, detail="source_id or target_id not found")

        call_id = str(uuid.uuid4())
        edge_id = str(uuid.uuid4())
        call_kind = payload.call_kind or "direct"

        cur.execute(
            "INSERT INTO canon_calls (call_id, component_id, call_target, lineno) VALUES (?, ?, ?, ?)",
            (call_id, payload.source_id, payload.target_id, payload.lineno),
        )
        cur.execute(
            """
            INSERT INTO call_graph_edges (
                edge_id, caller_id, callee_id, call_kind, is_internal, is_external, is_builtin, line_number, resolved_name
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                edge_id,
                payload.source_id,
                payload.target_id,
                call_kind,
                1,
                0,
                0,
                payload.lineno,
                payload.target_id,
            ),
        )
        conn.commit()

        return {"status": "ok", "edge_id": edge_id, "call_id": call_id}
    finally:
        conn.close()


@app.get("/api/analysis/dag")
def get_dag():
    conn = get_connection()
    try:
        edges = conn.execute("SELECT caller_id, callee_id FROM call_graph_edges").fetchall()
        dependencies: Dict[str, set] = defaultdict(set)
        nodes = set()
        for edge in edges:
            caller = edge["caller_id"]
            callee = edge["callee_id"]
            nodes.add(caller)
            nodes.add(callee)
            dependencies[callee].add(caller)

        telemetry = []
        for node in nodes:
            telemetry.append({"id": node, "dependencies": list(dependencies.get(node, []))})

        dag = _analyzer.build_dag(telemetry)
        return dag
    finally:
        conn.close()
