#!/usr/bin/env python
"""
Comprehensive system test for orchestrator, settings, and UI integration.
Writes results to test_results.log for verification.
"""

import sqlite3
import json
import sys
import time
from pathlib import Path
from datetime import datetime

OUTPUT_FILE = Path('test_results.log')

def log(msg=''):
    """Log to file and print (best effort)."""
    try:
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
            f.write(msg + '\n')
    except:
        pass
    try:
        print(msg)
    except:
        pass

def section(title):
    """Add a section header."""
    log(f"\n{'='*60}")
    log(f"  {title}")
    log(f"{'='*60}")

def subsection(title):
    """Add a subsection header."""
    log(f"\n--- {title} ---")

# Clear file
OUTPUT_FILE.unlink(missing_ok=True)
log("ORCHESTRATOR SYSTEM TEST")
log(f"Started at: {datetime.now().isoformat()}")

# TEST 1: File and Directory Structure
section("TEST 1: File & Directory Structure")
subsection("Core Files")

files_to_check = [
    'orchestrator.py',
    'bus/message_bus.py',
    'bus/settings_db.py',
    'ui_app.py',
    'workflows/workflow_ingest.py',  # legacy/package ingest entrypoint
    'orchestrator_config.json',
]

optional_files = [
    ('workflow_ingest_enhanced.py', 'optional ingest entrypoint (fallback to workflows/workflow_ingest.py)'),
]

for file in files_to_check:
    exists = Path(file).exists()
    status = '[✓]' if exists else '[✗]'
    log(f"  {status} {file}")

subsection("Optional Files")
for file, description in optional_files:
    exists = Path(file).exists()
    status = '[✓]' if exists else '[~]'
    log(f"  {status} {file} ({description})")

subsection("Database Files")

dbs = {
    'canon.db': 'Main analysis DB',
    'orchestrator_bus.db': 'Message bus DB',
    'settings.db': 'Settings registry DB',
}

for db_name, description in dbs.items():
    exists = Path(db_name).exists()
    size_mb = Path(db_name).stat().st_size / (1024*1024) if exists else 0
    status = '[✓]' if exists else '[✗]'
    log(f"  {status} {db_name:20} ({description:20}) - {size_mb:.2f} MB")

subsection("Staging Folder Structure")
staging_path = Path('staging')
if staging_path.exists():
    subdirs = ['incoming', 'processed', 'failed', 'archive', 'legacy', 'metadata.json']
    for subitem in subdirs:
        path = staging_path / subitem
        if path.is_dir() or path.is_file():
            count = len(list(path.glob('*.py'))) if path.is_dir() else 'file'
            log(f"  [✓] staging/{subitem:12} - {count} items")
        else:
            log(f"  [✗] staging/{subitem:12} - MISSING")
else:
    log(f"  [✗] staging/ directory - MISSING")

# TEST 2: Orchestrator Bus Database
section("TEST 2: Message Bus Database (orchestrator_bus.db)")

try:
    db = sqlite3.connect('orchestrator_bus.db')
    db.row_factory = sqlite3.Row
    cur = db.cursor()
    
    subsection("Table Schema")
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cur.fetchall()]
    for table in tables:
        log(f"  [✓] {table}")
    
    subsection("Data Contents")
    
    # Events summary
    cur.execute("SELECT COUNT(*) as cnt, event_type FROM bus_events GROUP BY event_type")
    rows = cur.fetchall()
    log(f"  Events ({sum(r['cnt'] for r in rows)} total):")
    for row in rows:
        log(f"    - {row['event_type']:30} : {row['cnt']:3} events")
    
    # Commands summary
    cur.execute("SELECT COUNT(*) as cnt, command_type, status FROM bus_commands GROUP BY command_type, status ORDER BY command_type")
    rows = cur.fetchall()
    log(f"  Commands ({sum(r['cnt'] for r in rows)} total):")
    for row in rows:
        status_str = f"[{row['status']}]" if row['status'] else '[?]'
        log(f"    - {row['command_type']:30} {status_str:12} : {row['cnt']:3}")
    
    # State registry
    subsection("State Registry (get_state values)")
    cur.execute("SELECT state_key, state_value, data_type FROM bus_state ORDER BY state_key")
    rows = cur.fetchall()
    for row in rows:
        log(f"    {row['state_key']:30} = {str(row['state_value'])[:40]:40} [{row['data_type']}]")
    
    db.close()
    
except Exception as e:
    log(f"  [ERROR] {e}")

# TEST 3: Settings Database
section("TEST 3: Settings Database (settings.db)")

try:
    db = sqlite3.connect('settings.db')
    db.row_factory = sqlite3.Row
    cur = db.cursor()
    
    subsection("Table Schema")
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cur.fetchall()]
    for table in tables:
        log(f"  [✓] {table}")
    
    subsection("User Settings")
    cur.execute("SELECT setting_key, setting_value, setting_type FROM user_settings ORDER BY setting_key")
    rows = cur.fetchall()
    for row in rows:
        log(f"    {row['setting_key']:30} = {str(row['setting_value'])[:35]:35} [{row['setting_type']}]")
    
    subsection("Feature Flags")
    cur.execute("SELECT flag_name, enabled FROM feature_flags ORDER BY flag_name")
    rows = cur.fetchall()
    for row in rows:
        status = 'ON ' if row['enabled'] else 'OFF'
        log(f"    {row['flag_name']:30} : {status}")
    
    subsection("Workflow Configurations")
    cur.execute("SELECT COUNT(*) FROM workflow_settings")
    wf_count = cur.fetchone()[0]
    log(f"    Total workflows configured: {wf_count}")
    
    db.close()
    
except Exception as e:
    log(f"  [ERROR] {e}")

# TEST 4: Orchestrator Configuration
section("TEST 4: Orchestrator Configuration")

try:
    config_path = Path('orchestrator_config.json')
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
        
        subsection("Top-level Keys")
        for key in sorted(config.keys()):
            log(f"  [✓] {key}")
        
        subsection("Staging Configuration")
        staging_cfg = config.get('staging', {})
        for key, value in staging_cfg.items():
            log(f"    {key:30} = {value}")
        
        subsection("Workflow Configuration")
        workflow_cfg = config.get('workflows', {})
        for key, value in workflow_cfg.items():
            if isinstance(value, list):
                log(f"    {key:30} = {', '.join(value)}")
            else:
                log(f"    {key:30} = {value}")
        
    else:
        log("  [✗] orchestrator_config.json NOT FOUND")
        
except Exception as e:
    log(f"  [ERROR] {e}")

# TEST 5: Python Module Imports
section("TEST 5: Python Module Imports")

modules_to_test = [
    'bus.message_bus',
    'bus.settings_db',
    'orchestrator',
]

for module_name in modules_to_test:
    try:
        __import__(module_name)
        log(f"  [✓] {module_name}")
    except ImportError as e:
        log(f"  [✗] {module_name} - {e}")
    except Exception as e:
        log(f"  [✗] {module_name} - {e}")

# Ingest workflow import (fallbacks)
ingest_modules = ['workflow_ingest_enhanced', 'workflows.workflow_ingest']
ingest_found = False

for mod in ingest_modules:
    try:
        __import__(mod)
        log(f"  [✓] {mod}")
        ingest_found = True
        break
    except ImportError:
        continue
    except Exception as e:
        log(f"  [!] Error importing {mod}: {e}")

if not ingest_found:
    log(f"  [✗] Ingest workflow module not found (checked: {', '.join(ingest_modules)})")

# TEST 6: Message Bus Operations
section("TEST 6: Message Bus Operations")

try:
    from bus.message_bus import MessageBus
    bus = MessageBus()
    
    subsection("Read Operations")
    
    # Get events
    events = bus.get_events(limit=3)
    log(f"  [✓] get_events() returned {len(events)} events")
    if events:
        log(f"      Latest: {events[0].get('event_type', 'unknown')} @ {events[0].get('timestamp', 'unknown')[:19]}")
    
    # Get pending commands
    commands = bus.get_pending_commands()
    log(f"  [✓] get_pending_commands() returned {len(commands)} commands")
    
    # Get state
    state_dict = bus.get_all_state()
    log(f"  [✓] get_all_state() returned {len(state_dict)} state variables")
    
    # List schemas
    schemas = bus.list_schemas()
    log(f"  [✓] list_schemas() returned {len(schemas)} schemas")
    
    subsection("Write Operations Test")
    
    # Test publish event
    test_event_id = bus.publish_event(
        event_type='TEST_EVENT',
        source='test_script',
        payload={'test': 'data', 'timestamp': datetime.now().isoformat()}
    )
    log(f"  [✓] publish_event() returned ID: {test_event_id[:8]}...")
    
    # Test send command
    test_cmd_id = bus.send_command(
        command_type='TEST_COMMAND',
        target='test_target',
        payload={'test': 'command'}
    )
    log(f"  [✓] send_command() returned ID: {test_cmd_id[:8]}...")
    
    # Test set state (auto-detects type)
    bus.set_state('test_key', 'test_value')
    log(f"  [✓] set_state() completed")
    
    # Verify write
    test_val = bus.get_state('test_key')
    log(f"  [✓] Verified set_state: test_key = {test_val}")
    
except Exception as e:
    log(f"  [ERROR] {e}")
    import traceback
    log(traceback.format_exc())

# TEST 7: Settings DB Operations
section("TEST 7: Settings Database Operations")

try:
    from bus.settings_db import SettingsDB
    sdb = SettingsDB()
    
    subsection("Read Operations")
    
    # Get settings
    settings = sdb.get_all_settings()
    log(f"  [✓] get_all_settings() returned {len(settings)} settings")
    
    # Get flags
    flags = sdb.get_all_flags()
    log(f"  [✓] get_all_flags() returned {len(flags)} feature flags")
    
    subsection("Write Operations Test")
    
    # Set a test setting
    sdb.set_setting('test_user_setting', 'test_value_123', 'Test setting from script')
    log(f"  [✓] set_setting() completed")
    
    # Verify
    val = sdb.get_setting('test_user_setting')
    log(f"  [✓] Verified: test_user_setting = {val}")
    
    # Set a test flag
    sdb.set_feature_flag('test_feature', True, 'Test feature from script')
    log(f"  [✓] set_feature_flag() completed")
    
    # Verify
    enabled = sdb.is_feature_enabled('test_feature')
    log(f"  [✓] Verified: test_feature enabled = {enabled}")
    
except Exception as e:
    log(f"  [ERROR] {e}")
    import traceback
    log(traceback.format_exc())

# TEST 8: Staging Folder Files
section("TEST 8: Staging Folder Files")

try:
    incoming_dir = Path('staging/incoming')
    if incoming_dir.exists():
        py_files = list(incoming_dir.glob('*.py'))
        log(f"  Python files in staging/incoming: {len(py_files)}")
        for path_obj in py_files[:5]:
            size_kb = path_obj.stat().st_size / 1024
            log(f"    - {path_obj.name} ({size_kb:.1f} KB)")
    else:
        log(f"  [✗] staging/incoming/ does not exist")
        
except Exception as e:
    log(f"  [ERROR] {e}")

# TEST 9: Symbol Tracking (Smoke)
section("TEST 9: Symbol Tracking (Smoke)")

try:
    from analysis.symbol_resolver import SymbolResolver
    resolver = SymbolResolver()
    cur = resolver.c
    subsection("Tables Present")
    tables_to_check = ['canon_variables', 'canon_types', 'canon_globals', 'overlay_semantic']
    table_status = {}
    for table in tables_to_check:
        exists = cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table,)
        ).fetchone() is not None
        table_status[table] = exists
        status = '[✓]' if exists else '[✗]'
        log(f"  {status} {table}")

    if all(table_status.values()):
        subsection("Symbol Inventory Snapshot")
        summary = cur.execute(
            """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN scope_level='parameter' THEN 1 ELSE 0 END) as params,
                SUM(CASE WHEN scope_level='local' THEN 1 ELSE 0 END) as locals,
                SUM(CASE WHEN scope_level='global' THEN 1 ELSE 0 END) as globals,
                SUM(CASE WHEN scope_level='nonlocal' THEN 1 ELSE 0 END) as nonlocals
            FROM canon_variables
            """
        ).fetchone()

        total, params, locals_count, globals_count, nonlocals = summary
        log(f"  Total symbols : {total}")
        log(f"  Parameters    : {params or 0}")
        log(f"  Locals        : {locals_count or 0}")
        log(f"  Globals       : {globals_count or 0}")
        log(f"  Nonlocals     : {nonlocals or 0}")
    else:
        log("  [!] Skipping inventory snapshot; required tables missing.")

    resolver.conn.close()

except Exception as e:
    log(f"  [ERROR] {e}")
    import traceback
    log(traceback.format_exc())

# Final Summary
section("TEST SUMMARY")

total_tests = 9
log(f"\nCompleted {total_tests} test suites")
log(f"Results written to: {OUTPUT_FILE.absolute()}")
log(f"\nCompleted at: {datetime.now().isoformat()}")

sys.exit(0)
