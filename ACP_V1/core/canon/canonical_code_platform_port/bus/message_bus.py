"""
Message Bus System

Central communication hub for all orchestrator components.
Uses SQLite as backing store for persistence.

Components:
  - Events (status updates, file scans, errors)
  - Commands (to orchestrator, workflows)
  - State (current configuration, settings)
"""

import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional


class MessageBus:
    """Central message bus for orchestrator communication."""

    def __init__(self, db_path: str = "orchestrator_bus.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_database()

    def _init_database(self):
        """Initialize message bus database."""
        c = self.conn.cursor()

        # Events table (log of all events)
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS bus_events (
                event_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                source TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                processed INTEGER DEFAULT 0
            )
        """
        )

        # Commands table (queued commands for orchestrator)
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS bus_commands (
                command_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                command_type TEXT NOT NULL,
                target TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                status TEXT DEFAULT 'PENDING',
                result_json TEXT
            )
        """
        )

        # State table (configuration and runtime state)
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS bus_state (
                state_key TEXT PRIMARY KEY,
                state_value TEXT NOT NULL,
                data_type TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                locked INTEGER DEFAULT 0
            )
        """
        )

        # Schemas table (saved workflow/schema definitions)
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS bus_schemas (
                schema_id TEXT PRIMARY KEY,
                schema_name TEXT NOT NULL,
                schema_type TEXT NOT NULL,
                definition_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                is_active INTEGER DEFAULT 1
            )
        """
        )

        # Subscriptions table (event subscribers)
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS bus_subscriptions (
                subscription_id TEXT PRIMARY KEY,
                subscriber_name TEXT NOT NULL,
                event_type TEXT NOT NULL,
                handler_path TEXT NOT NULL,
                created_at TEXT NOT NULL,
                is_active INTEGER DEFAULT 1
            )
        """
        )

        self.conn.commit()

    # ========== EVENT OPERATIONS ==========

    def publish_event(self, event_type: str, source: str, payload: Dict) -> str:
        """Publish an event to the bus."""
        event_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        c = self.conn.cursor()
        c.execute(
            """
            INSERT INTO bus_events
            (event_id, timestamp, event_type, source, payload_json)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                event_id,
                timestamp,
                event_type,
                source,
                json.dumps(payload),
            ),
        )
        self.conn.commit()

        return event_id

    def get_events(
        self,
        event_type: Optional[str] = None,
        source: Optional[str] = None,
        unprocessed_only: bool = False,
        limit: int = 100,
    ) -> List[Dict]:
        """Retrieve events from the bus."""
        c = self.conn.cursor()

        query = "SELECT * FROM bus_events WHERE 1=1"
        params: List[Any] = []

        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)

        if source:
            query += " AND source = ?"
            params.append(source)

        if unprocessed_only:
            query += " AND processed = 0"

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        c.execute(query, params)
        rows = c.fetchall()

        return [dict(row) for row in rows]

    def mark_event_processed(self, event_id: str):
        """Mark event as processed."""
        c = self.conn.cursor()
        c.execute("UPDATE bus_events SET processed = 1 WHERE event_id = ?", (event_id,))
        self.conn.commit()

    # ========== COMMAND OPERATIONS ==========

    def send_command(self, command_type: str, target: str, payload: Dict) -> str:
        """Send a command via the bus."""
        command_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        c = self.conn.cursor()
        c.execute(
            """
            INSERT INTO bus_commands
            (command_id, timestamp, command_type, target, payload_json)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                command_id,
                timestamp,
                command_type,
                target,
                json.dumps(payload),
            ),
        )
        self.conn.commit()

        return command_id

    def get_pending_commands(self, target: Optional[str] = None) -> List[Dict]:
        """Get pending commands for a target."""
        c = self.conn.cursor()

        if target:
            c.execute(
                """
                SELECT * FROM bus_commands
                WHERE status = 'PENDING' AND target = ?
                ORDER BY timestamp ASC
            """,
                (target,),
            )
        else:
            c.execute(
                """
                SELECT * FROM bus_commands
                WHERE status = 'PENDING'
                ORDER BY timestamp ASC
            """
            )

        rows = c.fetchall()
        return [dict(row) for row in rows]

    def update_command_status(
        self, command_id: str, status: str, result: Optional[Dict] = None
    ):
        """Update command status and result."""
        c = self.conn.cursor()

        if result:
            c.execute(
                """
                UPDATE bus_commands
                SET status = ?, result_json = ?
                WHERE command_id = ?
            """,
                (status, json.dumps(result), command_id),
            )
        else:
            c.execute(
                """
                UPDATE bus_commands
                SET status = ?
                WHERE command_id = ?
            """,
                (status, command_id),
            )

        self.conn.commit()

    # ========== STATE OPERATIONS ==========

    def set_state(self, key: str, value: Any, data_type: Optional[str] = None):
        """Set a state variable with optional explicit type."""
        c = self.conn.cursor()

        # Preserve compatibility: allow caller to force a type (e.g., from tests)
        if data_type:
            normalized_type = data_type.lower()
        else:
            normalized_type = None

        if normalized_type == "boolean" or isinstance(value, bool):
            data_type = "boolean"
            value_str = json.dumps(bool(value))
        elif normalized_type == "integer" or isinstance(value, int):
            data_type = "integer"
            value_str = str(int(value))
        elif normalized_type == "float" or isinstance(value, float):
            data_type = "float"
            value_str = str(float(value))
        elif normalized_type == "json" or isinstance(value, (dict, list)):
            data_type = "json"
            value_str = json.dumps(value)
        else:
            data_type = "string"
            value_str = str(value)

        updated_at = datetime.utcnow().isoformat()

        c.execute(
            """
            INSERT OR REPLACE INTO bus_state
            (state_key, state_value, data_type, updated_at)
            VALUES (?, ?, ?, ?)
        """,
            (key, value_str, data_type, updated_at),
        )

        self.conn.commit()

    def get_state(self, key: str) -> Optional[Any]:
        """Get a state variable."""
        c = self.conn.cursor()
        c.execute("SELECT state_value, data_type FROM bus_state WHERE state_key = ?", (key,))
        row = c.fetchone()

        if not row:
            return None

        value_str, data_type = row

        if data_type == "boolean":
            return json.loads(value_str)
        if data_type == "integer":
            return int(value_str)
        if data_type == "float":
            return float(value_str)
        if data_type == "json":
            return json.loads(value_str)
        return value_str

    def get_all_state(self) -> Dict[str, Any]:
        """Get all state variables."""
        c = self.conn.cursor()
        c.execute("SELECT state_key, state_value, data_type FROM bus_state")
        rows = c.fetchall()

        result = {}
        for state_key, value_str, data_type in rows:
            if data_type == "boolean":
                result[state_key] = json.loads(value_str)
            elif data_type == "integer":
                result[state_key] = int(value_str)
            elif data_type == "float":
                result[state_key] = float(value_str)
            elif data_type == "json":
                result[state_key] = json.loads(value_str)
            else:
                result[state_key] = value_str

        return result

    # ========== SCHEMA OPERATIONS ==========

    def save_schema(self, schema_name: str, schema_type: str, definition: Dict) -> str:
        """Save a workflow or configuration schema."""
        schema_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()

        c = self.conn.cursor()
        c.execute(
            """
            INSERT INTO bus_schemas
            (schema_id, schema_name, schema_type, definition_json, created_at)
            VALUES (?, ?, ?, ?, ?)
        """,
            (schema_id, schema_name, schema_type, json.dumps(definition), created_at),
        )
        self.conn.commit()

        return schema_id

    def get_schema(self, schema_name: str, schema_type: str) -> Optional[Dict]:
        """Get a saved schema."""
        c = self.conn.cursor()
        c.execute(
            """
            SELECT definition_json FROM bus_schemas
            WHERE schema_name = ? AND schema_type = ? AND is_active = 1
        """,
            (schema_name, schema_type),
        )

        row = c.fetchone()
        if not row:
            return None

        return json.loads(row[0])

    def list_schemas(self, schema_type: Optional[str] = None) -> List[Dict]:
        """List all schemas."""
        c = self.conn.cursor()

        if schema_type:
            c.execute(
                """
                SELECT schema_id, schema_name, schema_type, created_at, is_active
                FROM bus_schemas
                WHERE schema_type = ?
                ORDER BY created_at DESC
            """,
                (schema_type,),
            )
        else:
            c.execute(
                """
                SELECT schema_id, schema_name, schema_type, created_at, is_active
                FROM bus_schemas
                ORDER BY created_at DESC
            """
            )

        rows = c.fetchall()
        return [dict(row) for row in rows]

    # ========== SUBSCRIPTION OPERATIONS ==========

    def subscribe(self, subscriber_name: str, event_type: str, handler_path: str) -> str:
        """Subscribe to event type."""
        subscription_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()

        c = self.conn.cursor()
        c.execute(
            """
            INSERT INTO bus_subscriptions
            (subscription_id, subscriber_name, event_type, handler_path, created_at)
            VALUES (?, ?, ?, ?, ?)
        """,
            (subscription_id, subscriber_name, event_type, handler_path, created_at),
        )
        self.conn.commit()

        return subscription_id

    def get_subscribers(self, event_type: str) -> List[Dict]:
        """Get subscribers for an event type."""
        c = self.conn.cursor()
        c.execute(
            """
            SELECT subscriber_name, handler_path
            FROM bus_subscriptions
            WHERE event_type = ? AND is_active = 1
        """,
            (event_type,),
        )

        rows = c.fetchall()
        return [dict(row) for row in rows]

    # ========== HOUSEKEEPING ==========

    def cleanup_old_events(self, days: int = 30):
        """Delete old events (retention policy)."""
        c = self.conn.cursor()

        cutoff = datetime.utcfromtimestamp(
            (datetime.utcnow().timestamp() - (days * 86400))
        ).isoformat()

        c.execute("DELETE FROM bus_events WHERE timestamp < ?", (cutoff,))
        self.conn.commit()

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

    def __del__(self):
        """Cleanup on destruction."""
        self.close()
