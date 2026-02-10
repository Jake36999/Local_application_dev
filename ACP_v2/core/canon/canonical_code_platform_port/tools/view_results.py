#!/usr/bin/env python3
"""Quick viewer for Phase 3 cut analysis results."""

import sqlite3
import json

conn = sqlite3.connect('canon.db')
c = conn.cursor()

# Get component names
comp_names = {}
for cid, qname in c.execute('SELECT component_id, qualified_name FROM canon_components'):
    comp_names[cid] = qname

print("\n" + "="*100)
print("PHASE 3: CUT ANALYSIS RESULTS - NORMALIZED METRICS")
print("="*100)

# Get call metrics from normalizer
print("\n[*] Call Graph Metrics (from normalizer):")
print("-"*100)
print(f"{'Component':50} | {'Fan-In':6} | {'Fan-Out':7} | {'Ext.Calls':9}")
print("-"*100)

metrics = c.execute('''
    SELECT target_id, payload_json
    FROM overlay_semantic 
    WHERE source = 'call_graph_normalizer' AND json_extract(payload_json, '$.analysis_type') = 'call_metrics'
    ORDER BY json_extract(payload_json, '$.fan_out') DESC
    LIMIT 10
''').fetchall()

for target_id, payload_json in metrics:
    payload = json.loads(payload_json)
    name = comp_names.get(target_id, 'UNKNOWN')
    fan_in = payload['fan_in']
    fan_out = payload['fan_out']
    ext = payload['external_calls']
    print(f'{name:50} | {fan_in:6} | {fan_out:7} | {ext:9}')

# Get cut scores
print("\n" + "="*100)
print("[*] Microservice Cut Scores (with improved scoring):")
print("-"*100)
print(f"{'Component':50} | {'Tier':20} | {'Score':6} | {'In':3} | {'Out':3} | {'Glob':4}")
print("-"*100)

scores = c.execute('''
    SELECT target_id, payload_json
    FROM overlay_semantic 
    WHERE source = 'cut_analyzer'
    ORDER BY confidence DESC
    LIMIT 20
''').fetchall()

for target_id, payload_json in scores:
    payload = json.loads(payload_json)
    name = comp_names.get(target_id, 'UNKNOWN')
    tier = payload['tier']
    score = payload['score']
    metrics = payload['metrics']
    fan_in = metrics['fan_in']
    fan_out = metrics['fan_out']
    globals_count = metrics['globals']
    print(f'{name:50} | {tier:20} | {score:6.2f} | {fan_in:3} | {fan_out:3} | {globals_count:4}')

# Show orchestrators
print("\n" + "="*100)
print("[!] ORCHESTRATORS DETECTED (Complex hub components):")
print("-"*100)

orchs = c.execute('''
    SELECT target_id, payload_json
    FROM overlay_semantic 
    WHERE source = 'call_graph_normalizer' AND json_extract(payload_json, '$.analysis_type') = 'orchestrator_flag'
    ORDER BY json_extract(payload_json, '$.fan_out') DESC
''').fetchall()

for target_id, payload_json in orchs:
    payload = json.loads(payload_json)
    name = comp_names.get(target_id, 'UNKNOWN')
    fan_out = payload['fan_out']
    risk = payload['risk']
    print(f'  {name:48} (fan-out: {fan_out:2}) - {risk}')

print("\n" + "="*100)
print("[+] Analysis complete. Use UI to explore detailed metrics.")
print("="*100 + "\n")
