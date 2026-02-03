#!/usr/bin/env python3
"""
Unified Ingestion Workflow
Runs Phases 1-7 in correct order with progress tracking

Usage:
    python workflows/workflow_ingest.py <python_file>

Phases:
    1. File ingestion (canon_extractor + ingest)
    2. Symbol resolution (symbol_resolver)
    3. Cut analysis (cut_analysis)
    4. Governance checks (rule_engine)
    5. Report generation (governance_report)
"""

import sys
import os
from pathlib import Path


class IngestionWorkflow:
    """Orchestrates the complete ingestion and analysis pipeline."""
    
    def __init__(self, target_path):
        self.target_path = Path(target_path)
        self.results = {}
        
        if not self.target_path.exists():
            raise FileNotFoundError(f"Path not found: {target_path}")
        
        if self.target_path.is_file():
            self.targets = [self.target_path]
        else:
            # Accept a directory; ingest all Python files beneath it
            self.targets = sorted(p for p in self.target_path.rglob("*.py"))
            if not self.targets:
                raise ValueError(f"No Python files found under directory: {target_path}")
    
    def run(self):
        """Execute full ingestion pipeline."""
        print("\n" + "="*70)
        print("CANONICAL CODE PLATFORM - INGESTION WORKFLOW")
        print("="*70 + "\n")
        print(f"Target: {self.target_path}")
        print()
        
        for index, py_file in enumerate(self.targets, start=1):
            print(f"--- [{index}/{len(self.targets)}] Processing {py_file} ---")
            self.file_path = py_file
            # Phase 1-6: Ingest file
            self._run_phase(1, f"Ingesting {py_file.name} and detecting drift", self._phase_ingest)
            # Phase 2: Resolve symbols
            self._run_phase(2, "Resolving symbols and scopes", self._phase_symbols)
            # Phase 3: Cut analysis
            self._run_phase(3, "Analyzing microservice candidates", self._phase_cut_analysis)
            # Phase 7: Governance checks
            self._run_phase(4, "Running governance rules", self._phase_governance)
            # Report generation
            self._run_phase(5, "Generating governance report", self._phase_report)
            print()
        
        # Summary
        self._print_summary()
        return self.results
    
    def _run_phase(self, phase_num, description, phase_func):
        """Run a single phase with error handling."""
        print(f"[{phase_num}/5] {description}...")
        try:
            phase_func()
            self.results[description] = 'SUCCESS'
            print(f"        [OK] Phase {phase_num} complete\n")
        except Exception as e:
            self.results[description] = f'FAILED: {str(e)}'
            print(f"        [FAIL] {str(e)}\n")
            # Continue to next phase even if this one fails (for reporting)
    
    def _phase_ingest(self):
        """Phase 1-6: Ingest file with canonical extraction."""
        from core.ingest import main as ingest_main
        
        # Save original argv
        original_argv = sys.argv
        try:
            # Set argv for ingest script
            sys.argv = ['core/ingest.py', str(self.file_path)]
            ingest_main()
        finally:
            # Restore original argv
            sys.argv = original_argv
    
    def _phase_symbols(self):
        """Phase 2: Resolve symbols and scopes."""
        try:
            from analysis.symbol_resolver import main as resolve_symbols
            resolve_symbols()
        except (ImportError, AttributeError):
            # symbol_resolver might not have a main() function
            from analysis import symbol_resolver  # noqa: F401
            # If no main, assume module execution is sufficient
            pass
    
    def _phase_cut_analysis(self):
        """Phase 3: Analyze microservice extraction candidates."""
        from analysis.cut_analysis import CutAnalyzer
        analyzer = CutAnalyzer()
        analyzer.analyze()
    
    def _phase_governance(self):
        """Phase 7: Run governance rule checks."""
        from analysis.rule_engine import RuleEngine
        engine = RuleEngine()
        engine.run()
    
    def _phase_report(self):
        """Generate governance report."""
        from analysis.governance_report import GovernanceReport
        report = GovernanceReport()
        report.write_report("governance_report.txt")
        report.write_json("governance_report.json")
    
    def _print_summary(self):
        """Print workflow execution summary."""
        print("="*70)
        print("WORKFLOW SUMMARY")
        print("="*70)
        
        success_count = sum(1 for r in self.results.values() if r == 'SUCCESS')
        total_count = len(self.results)
        
        for phase, result in self.results.items():
            status = "[OK]  " if result == "SUCCESS" else "[FAIL]"
            display_result = result if result != "SUCCESS" else "Completed successfully"
            print(f"  {status} {phase}")
            if result != "SUCCESS":
                print(f"         {result}")
        
        print(f"\nOverall: {success_count}/{total_count} phases completed")
        
        if success_count == total_count:
            print("\n[SUCCESS] All phases completed successfully!")
            print("\nNext steps:")
            print("  - View UI:          streamlit run ui_app.py")
            print("  - Extract services: python workflows/workflow_extract.py")
            print("  - Verify suite:     python workflows/workflow_verify.py")
            print("  - View report:      type governance_report.txt")
        else:
            print("\n[PARTIAL] Some phases failed. Review errors above.")
            print("  - Verify suite:     python workflows/workflow_verify.py")
            print("  - Debug errors:     python debug_queries.py")
        
        print("="*70 + "\n")


def main():
    """Entry point for workflow execution."""
    if len(sys.argv) != 2:
        print("="*70)
        print("CANONICAL CODE PLATFORM - INGESTION WORKFLOW")
        print("="*70)
        print("\nUSAGE: python workflows/workflow_ingest.py <python_file>")
        print("\nRuns complete ingestion pipeline:")
        print("  1. File ingestion (Phases 1-6: canonical extraction + drift)")
        print("  2. Symbol resolution (Phase 2: variables + scopes)")
        print("  3. Cut analysis (Phase 3: microservice candidates)")
        print("  4. Governance checks (Phase 7: rule validation)")
        print("  5. Report generation (governance_report.txt)")
        print("\nExample:")
        print("  python workflows/workflow_ingest.py myfile.py")
        print("\nOutput:")
        print("  - canon.db (updated)")
        print("  - governance_report.txt")
        print("  - governance_report.json")
        print("="*70)
        sys.exit(1)
    
    try:
        workflow = IngestionWorkflow(sys.argv[1])
        results = workflow.run()
        
        # Exit with error if any phase failed
        failed = [r for r in results.values() if r != 'SUCCESS']
        if failed:
            sys.exit(1)
        else:
            sys.exit(0)
    
    except Exception as e:
        print(f"\n[ERROR] Workflow failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
