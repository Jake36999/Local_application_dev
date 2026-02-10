import os
from pathlib import Path

# Base path for the port
base = Path("canonical_code_platform_port/analysis")
base.mkdir(parents=True, exist_ok=True)

# 1. __init__.py
(base / "__init__.py").touch()

# 2. call_graph_normalizer.py
(base / "call_graph_normalizer.py").write_text("""
class CallGraphNormalizer:
    def normalize_calls(self): print("    [Stub] Normalizing calls...")
    def compute_metrics(self): pass
    def detect_orchestrators(self): pass
    def build_dependency_dag(self): pass
""", encoding='utf-8')

# 3. semantic_rebuilder.py
(base / "semantic_rebuilder.py").write_text("""
class SemanticRebuilder:
    def rebuild(self): pass
""", encoding='utf-8')

# 4. drift_detector.py
(base / "drift_detector.py").write_text("""
class DriftDetector:
    def __init__(self, conn): self.conn = conn
    def detect_drift(self, fid, ver): 
        return {'added': 0, 'removed': 0, 'modified': 0}
""", encoding='utf-8')

# 5. symbol_resolver.py
(base / "symbol_resolver.py").write_text("""
def main(): print("    [Stub] Resolving symbols...")
""", encoding='utf-8')

# 6. cut_analysis.py
(base / "cut_analysis.py").write_text("""
class CutAnalyzer:
    def analyze(self): print("    [Stub] Analyzing cuts...")
""", encoding='utf-8')

# 7. rule_engine.py
(base / "rule_engine.py").write_text("""
class RuleEngine:
    def run(self): print("    [Stub] Running rules...")
""", encoding='utf-8')

# 8. governance_report.py
(base / "governance_report.py").write_text("""
class GovernanceReport:
    def write_report(self, path): 
        with open(path, 'w') as f: f.write("Governance Report (Stub)")
    def write_json(self, path):
        with open(path, 'w') as f: f.write("{}")
""", encoding='utf-8')

print("✅ 'analysis' package created successfully. You can now rerun the workflow.")