"""
Settings Management Database

Persistent storage for:
  - User preferences
  - Workflow configuration
  - Integration settings
  - Feature flags
"""

import sqlite3
import json
from datetime import datetime
from typing import Any, Optional, Dict, List


class SettingsDB:
    """Settings persistence layer."""

    def __init__(self, db_path: str = "settings.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_database()

    def _init_database(self):
        """Initialize settings database."""
        c = self.conn.cursor()

        # User settings
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS user_settings (
                setting_key TEXT PRIMARY KEY,
                setting_value TEXT NOT NULL,
                setting_type TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                description TEXT
            )
        """
        )

        # Workflow settings
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS workflow_settings (
                workflow_id TEXT PRIMARY KEY,
                workflow_name TEXT NOT NULL,
                enabled INTEGER DEFAULT 1,
                auto_run INTEGER DEFAULT 0,
                timeout_seconds INTEGER DEFAULT 300,
                retry_count INTEGER DEFAULT 3,
                configuration_json TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """
        )

        # Integration settings
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS integration_settings (
                integration_id TEXT PRIMARY KEY,
                integration_name TEXT NOT NULL,
                enabled INTEGER DEFAULT 0,
                settings_json TEXT NOT NULL,
                credentials_encrypted BLOB,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """
        )

        # Feature flags
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS feature_flags (
                flag_name TEXT PRIMARY KEY,
                enabled INTEGER DEFAULT 0,
                description TEXT,
                updated_at TEXT NOT NULL
            )
        """
        )

        # Audit log
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS settings_audit (
                audit_id TEXT PRIMARY KEY,
                setting_key TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT,
                changed_by TEXT,
                changed_at TEXT NOT NULL
            )
        """
        )

        self.conn.commit()

        # Initialize defaults
        self._init_defaults()

    def _init_defaults(self):
        """Initialize default settings if not present."""
        defaults = {
            "staging_enabled": (True, "boolean"),
            "auto_scan": (True, "boolean"),
            "scan_interval_seconds": (5, "integer"),
            "ui_port": (8501, "integer"),
            "max_file_size_mb": (100, "integer"),
            "retention_days": (30, "integer"),
            "auto_cleanup": (True, "boolean"),
            "rag_integration_enabled": (False, "boolean"),
            "dark_mode": (False, "boolean"),
            "notifications_enabled": (True, "boolean"),
        }

        for key, (value, _vtype) in defaults.items():
            if self.get_setting(key) is None:
                self.set_setting(key, value)

    # ========== USER SETTINGS ==========

    def set_setting(self, key: str, value: Any, description: str = ""):
        """Set a user setting."""
        c = self.conn.cursor()

        if isinstance(value, bool):
            vtype = "boolean"
            vstr = json.dumps(value)
        elif isinstance(value, int):
            vtype = "integer"
            vstr = str(value)
        elif isinstance(value, float):
            vtype = "float"
            vstr = str(value)
        elif isinstance(value, (dict, list)):
            vtype = "json"
            vstr = json.dumps(value)
        else:
            vtype = "string"
            vstr = str(value)

        updated_at = datetime.utcnow().isoformat()

        c.execute(
            """
            INSERT OR REPLACE INTO user_settings
            (setting_key, setting_value, setting_type, updated_at, description)
            VALUES (?, ?, ?, ?, ?)
        """,
            (key, vstr, vtype, updated_at, description),
        )

        self.conn.commit()

    def get_setting(self, key: str) -> Optional[Any]:
        """Get a user setting."""
        c = self.conn.cursor()
        c.execute(
            "SELECT setting_value, setting_type FROM user_settings WHERE setting_key = ?",
            (key,),
        )

        row = c.fetchone()
        if not row:
            return None

        value_str, vtype = row

        if vtype == "boolean":
            return json.loads(value_str)
        if vtype == "integer":
            return int(value_str)
        if vtype == "float":
            return float(value_str)
        if vtype == "json":
            return json.loads(value_str)
        return value_str

    def get_all_settings(self) -> Dict[str, Any]:
        """Get all user settings."""
        c = self.conn.cursor()
        c.execute("SELECT setting_key, setting_value, setting_type FROM user_settings")
        rows = c.fetchall()

        result = {}
        for key, value_str, vtype in rows:
            if vtype == "boolean":
                result[key] = json.loads(value_str)
            elif vtype == "integer":
                result[key] = int(value_str)
            elif vtype == "float":
                result[key] = float(value_str)
            elif vtype == "json":
                result[key] = json.loads(value_str)
            else:
                result[key] = value_str

        return result

    # ========== WORKFLOW SETTINGS ==========

    def save_workflow_config(
        self,
        workflow_id: str,
        workflow_name: str,
        configuration: Dict,
        enabled: bool = True,
        auto_run: bool = False,
        timeout_seconds: int = 300,
    ):
        """Save workflow configuration."""
        c = self.conn.cursor()
        created_at = datetime.utcnow().isoformat()

        c.execute(
            """
            INSERT OR REPLACE INTO workflow_settings
            (workflow_id, workflow_name, enabled, auto_run, timeout_seconds,
             configuration_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                workflow_id,
                workflow_name,
                int(enabled),
                int(auto_run),
                timeout_seconds,
                json.dumps(configuration),
                created_at,
                created_at,
            ),
        )

        self.conn.commit()

    def get_workflow_config(self, workflow_id: str) -> Optional[Dict]:
        """Get workflow configuration."""
        c = self.conn.cursor()
        c.execute(
            """
            SELECT workflow_name, enabled, auto_run, timeout_seconds,
                   configuration_json FROM workflow_settings
            WHERE workflow_id = ?
        """,
            (workflow_id,),
        )

        row = c.fetchone()
        if not row:
            return None

        name, enabled, auto_run, timeout, config_json = row

        return {
            "workflow_id": workflow_id,
            "workflow_name": name,
            "enabled": bool(enabled),
            "auto_run": bool(auto_run),
            "timeout_seconds": timeout,
            "configuration": json.loads(config_json) if config_json else {},
        }

    def list_workflows(self) -> List[Dict]:
        """List all workflow configurations."""
        c = self.conn.cursor()
        c.execute(
            """
            SELECT workflow_id, workflow_name, enabled, auto_run, timeout_seconds
            FROM workflow_settings
            ORDER BY created_at DESC
        """
        )

        rows = c.fetchall()
        return [dict(row) for row in rows]

    # ========== FEATURE FLAGS ==========

    def set_feature_flag(self, flag_name: str, enabled: bool, description: str = ""):
        """Set a feature flag."""
        c = self.conn.cursor()
        updated_at = datetime.utcnow().isoformat()

        c.execute(
            """
            INSERT OR REPLACE INTO feature_flags
            (flag_name, enabled, description, updated_at)
            VALUES (?, ?, ?, ?)
        """,
            (flag_name, int(enabled), description, updated_at),
        )

        self.conn.commit()

    def is_feature_enabled(self, flag_name: str) -> bool:
        """Check if a feature is enabled."""
        c = self.conn.cursor()
        c.execute("SELECT enabled FROM feature_flags WHERE flag_name = ?", (flag_name,))

        row = c.fetchone()
        return bool(row[0]) if row else False

    def get_all_flags(self) -> Dict[str, bool]:
        """Get all feature flags."""
        c = self.conn.cursor()
        c.execute("SELECT flag_name, enabled FROM feature_flags")
        rows = c.fetchall()

        return {row[0]: bool(row[1]) for row in rows}

    # ========== AUDIT LOG ==========

    def audit_setting_change(
        self,
        setting_key: str,
        old_value: str,
        new_value: str,
        changed_by: str = "system",
    ):
        """Log a settings change."""
        import uuid

        c = self.conn.cursor()
        audit_id = str(uuid.uuid4())
        changed_at = datetime.utcnow().isoformat()

        c.execute(
            """
            INSERT INTO settings_audit
            (audit_id, setting_key, old_value, new_value, changed_by, changed_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (audit_id, setting_key, old_value, new_value, changed_by, changed_at),
        )

        self.conn.commit()

    def get_audit_log(self, limit: int = 100) -> List[Dict]:
        """Get audit log."""
        c = self.conn.cursor()
        c.execute(
            """
            SELECT audit_id, setting_key, old_value, new_value, changed_by, changed_at
            FROM settings_audit
            ORDER BY changed_at DESC
            LIMIT ?
        """,
            (limit,),
        )

        rows = c.fetchall()
        return [dict(row) for row in rows]

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

    def __del__(self):
        """Cleanup on destruction."""
        self.close()
