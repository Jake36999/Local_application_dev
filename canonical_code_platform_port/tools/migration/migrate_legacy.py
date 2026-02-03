"""
Legacy File Migration Tool

Moves example/test files from root to staging/legacy/
Preserves directory structure
"""

import shutil
from pathlib import Path
import json
from datetime import datetime


class LegacyMigrator:
    """Migrates legacy test/example files to staging folder."""
    
    # Legacy files to migrate
    LEGACY_FILES = [
        "test_phase7_rules.py",
        "create_test_directives.py",
        "test_directives.py",
        "test_conflicts.py",
        "test_clean_workflow.py",
        "simple_phase7_test.py",
        "test_drift_v1.py",
        "test_drift_v2.py",
    ]
    
    def __init__(self):
        self.root = Path.cwd()
        self.staging_legacy = self.root / "staging" / "legacy"
        self.staging_legacy.mkdir(parents=True, exist_ok=True)
        self.migration_log = []
    
    def run(self):
        """Execute migration."""
        print("\n" + "="*70)
        print("LEGACY FILE MIGRATION")
        print("="*70 + "\n")
        
        moved_count = 0
        skipped_count = 0
        
        for filename in self.LEGACY_FILES:
            file_path = self.root / filename
            
            if not file_path.exists():
                print(f"⊘ {filename:40s} - not found (skip)")
                skipped_count += 1
                continue
            
            try:
                dest = self.staging_legacy / filename
                shutil.move(str(file_path), str(dest))
                
                self.migration_log.append({
                    "filename": filename,
                    "source": str(file_path),
                    "destination": str(dest),
                    "status": "SUCCESS",
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                print(f"✓ {filename:40s} → staging/legacy/")
                moved_count += 1
            
            except Exception as e:
                self.migration_log.append({
                    "filename": filename,
                    "error": str(e),
                    "status": "FAILED",
                    "timestamp": datetime.utcnow().isoformat()
                })
                print(f"✗ {filename:40s} - {e}")
        
        # Save migration log
        self._save_migration_log()
        self._print_summary(moved_count, skipped_count)
    
    def _save_migration_log(self):
        """Save migration log to file."""
        log_file = self.staging_legacy / "MIGRATION_LOG.json"
        with open(log_file, 'w') as f:
            json.dump(self.migration_log, f, indent=2)
        
        print(f"\n📋 Migration log saved: staging/legacy/MIGRATION_LOG.json")
    
    def _print_summary(self, moved_count, skipped_count):
        """Print migration summary."""
        total = moved_count + skipped_count
        
        print("\n" + "="*70)
        print("MIGRATION SUMMARY")
        print("="*70)
        print(f"\n✓ Moved:    {moved_count} files")
        print(f"⊘ Skipped:  {skipped_count} files (not found)")
        print(f"Total:      {total} files")
        print(f"\nLocation:  staging/legacy/")
        print(f"Log file:  staging/legacy/MIGRATION_LOG.json")
        print("\n" + "="*70 + "\n")


def main():
    """Entry point."""
    migrator = LegacyMigrator()
    migrator.run()


if __name__ == "__main__":
    main()
