#!/usr/bin/env python3
"""
Unified Extraction Workflow
Generates microservices from extraction-ready components

Usage:
    python workflow_extract.py

Prerequisites:
    - Database must exist (run workflows/workflow_ingest.py first)
    - Governance rules must pass (no blocking errors)

Output:
    - extracted_services/<service_name>/
        - interface.py
        - api.py
        - Dockerfile
        - deployment.yaml
        - requirements.txt
        - README.md
"""

import sys
from pathlib import Path
from core.canon_db import init_db
from analysis.microservice_export import MicroserviceExporter


class ExtractionWorkflow:
    """Orchestrates microservice extraction with governance gates."""
    
    def __init__(self):
        self.conn = init_db()
        self.c = self.conn.cursor()
    
    def run(self):
        """Execute microservice extraction workflow."""
        print("\n" + "="*70)
        print("CANONICAL CODE PLATFORM - EXTRACTION WORKFLOW")
        print("="*70 + "\n")
        
        # Step 1: Check governance gate
        print("[1/3] Checking governance gate status...")
        gate_status = self._check_gate()
        
        if gate_status['blocking_errors'] > 0:
            print(f"      [BLOCKED] {gate_status['blocking_errors']} blocking error(s) found")
            print("\n      Cannot proceed with extraction until errors are resolved.")
            print("      Fix blocking errors before extraction:")
            print("        - Run:  python analysis/rule_engine.py")
            print("        - View: type governance_report.txt")
            return False
        else:
            print(f"      [PASS] Gate status: CLEAR")
            print(f"      Ready components: {gate_status['ready_count']}\n")
        
        # Step 2: List candidates
        print("[2/3] Identifying extraction candidates...")
        candidates = self._get_candidates()
        
        if not candidates:
            print("      [INFO] No extraction-ready components found")
            print("\n      Components need:")
            print("        - Cut analysis score > threshold (0.5)")
            print("        - No blocking governance violations")
            print("        - @extract or @service_candidate directive (optional)")
            print("\n      To create candidates:")
            print("        1. Add extraction hints to your code:")
            print("           # @extract")
            print("           # @service_candidate")
            print("        2. Re-run: python workflows/workflow_ingest.py <file.py>")
            return False
        
        print(f"      Found {len(candidates)} candidate(s):\n")
        for qname, score, tier in candidates:
            score_val = score if score is not None else 0.0
            tier_val = tier if tier is not None else "unknown"
            print(f"        * {qname}")
            print(f"          Score: {score_val:.2f} | Tier: {tier_val}")
        print()
        
        # Step 3: Generate services
        print("[3/3] Generating microservice artifacts...")
        exporter = MicroserviceExporter()
        
        try:
            results = exporter.export_all()
            
            if results['services_generated'] > 0:
                print(f"      [OK] Generated {results['services_generated']} service(s)")
                print(f"      [OK] Total files: {results['total_files']}\n")
            else:
                print("      [INFO] No services generated (this is unexpected)")
                print("            Check cut_analysis scores and governance status\n")
        except Exception as e:
            print(f"      [FAIL] Export failed: {e}\n")
            return False
        
        # Summary
        self._print_summary(results)
        return True
    
    def _check_gate(self):
        """Check governance gate status."""
        # Count blocking errors
        blocking = self.c.execute("""
            SELECT COUNT(*) FROM overlay_best_practice 
            WHERE severity = 'ERROR'
        """).fetchone()[0]
        
        # Count components ready for extraction
        ready = self.c.execute("""
            SELECT COUNT(*) FROM canon_components c
            WHERE NOT EXISTS (
                SELECT 1 FROM overlay_best_practice bp
                WHERE bp.component_id = c.component_id
                AND bp.severity = 'ERROR'
            )
            AND c.kind IN ('function', 'class')
        """).fetchone()[0]
        
        return {
            'blocking_errors': blocking,
            'ready_count': ready
        }
    
    def _get_candidates(self):
        """Get extraction-ready components."""
        # Query components with cut analysis scores above threshold
        # and no blocking governance violations
        return self.c.execute("""
            SELECT DISTINCT 
                c.qualified_name, 
                json_extract(s.payload_json, '$.score') as score,
                json_extract(s.payload_json, '$.tier') as tier
            FROM canon_components c
            JOIN overlay_semantic s ON c.component_id = s.target_id
            WHERE s.source = 'cut_analyzer'
            AND json_extract(s.payload_json, '$.score') > 0.5
            AND NOT EXISTS (
                SELECT 1 FROM overlay_best_practice bp
                WHERE bp.component_id = c.component_id
                AND bp.severity = 'ERROR'
            )
            ORDER BY score DESC
        """).fetchall()
    
    def _print_summary(self, results):
        """Print extraction summary."""
        print("="*70)
        print("EXTRACTION SUMMARY")
        print("="*70)
        print(f"  Services generated: {results['services_generated']}")
        print(f"  Total files:        {results['total_files']}")
        print(f"  Output directory:   extracted_services/")
        
        if results['services_generated'] > 0:
            print("\n  Generated services:")
            output_dir = Path("extracted_services")
            if output_dir.exists():
                for service_dir in sorted(output_dir.iterdir()):
                    if service_dir.is_dir():
                        file_count = len(list(service_dir.iterdir()))
                        print(f"    - {service_dir.name}/ ({file_count} files)")
            
            print("\n  Next steps:")
            print("    1. Review services:  cd extracted_services/<service_name>")
            print("    2. Test locally:     docker build -t <service> .")
            print("    3. Deploy:           kubectl apply -f deployment.yaml")
        else:
            print("\n  No services generated.")
            print("  Run: python workflows/workflow_ingest.py <file.py>")
            print("  Then check: python analysis/cut_analysis.py")
        
        print("="*70 + "\n")


def main():
    """Entry point for extraction workflow."""
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        print("="*70)
        print("CANONICAL CODE PLATFORM - EXTRACTION WORKFLOW")
        print("="*70)
        print("\nUSAGE: python workflow_extract.py")
        print("\nGenerates microservices from extraction-ready components.")
        print("\nPrerequisites:")
        print("  1. Database exists (run workflows/workflow_ingest.py first)")
        print("  2. Governance rules pass (no blocking errors)")
        print("\nOutput:")
        print("  extracted_services/<service_name>/")
        print("    - interface.py      (Abstract base class)")
        print("    - api.py            (FastAPI endpoints)")
        print("    - Dockerfile        (Container definition)")
        print("    - deployment.yaml   (Kubernetes config)")
        print("    - requirements.txt  (Python dependencies)")
        print("    - README.md         (Service documentation)")
        print("\nExample:")
        print("  python workflows/workflow_ingest.py myfile.py")
        print("  python workflow_extract.py")
        print("="*70)
        sys.exit(0)
    
    try:
        workflow = ExtractionWorkflow()
        success = workflow.run()
        sys.exit(0 if success else 1)
    
    except Exception as e:
        print(f"\n[ERROR] Extraction workflow failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
