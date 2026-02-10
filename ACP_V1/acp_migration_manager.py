import csv
import os
import shutil
import re
import logging  # Added missing import
import json     # Added missing import
import hashlib  # Added for integrity verification
from pathlib import Path

class ACPMigrator:
    def __init__(self, file_map_path, source_root=None, target_root="ACP_v2"):
        self.file_map_path = file_map_path
        self.target_root = Path(target_root)
        self.source_root = Path(source_root) if source_root else None
        self.operations = []
        self.ignored_files = []
        self.missing_files = []
        self.import_map = {}  # Added missing initialization

        # Configure logging
        logging.basicConfig(
            filename='migration_log.txt',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filemode='w'
        )

        # --- DEFINING THE RULES FROM YOUR PLAN ---
        
        # 1. Exact Filename Mappings (High Priority)
        self.exact_map = {
            # --- 🧠 COGNITIVE LAYER (Brain & Logic) ---
            'stack_creator.py': 'core/brain/stack_creator.py',
            'workflow_analyzer.py': 'core/brain/workflow_analyzer.py',
            'context_manager.py': 'core/bridge/context_manager.py',

            # --- 🛡️ CONTROL SYSTEMS (Stability & Audit) ---
            'adaptive_protection.py': 'core/control/adaptive_protection.py',
            'damping_controller.py': 'core/control/damping_controller.py',
            'pmu_filter.py': 'core/control/pmu_filter.py',
            'discrepancy_check.py': 'ops/audit/discrepancy_check.py',
            'isolation_layer.py': 'ops/safe_ops/isolation_layer.py',

            # --- 🛠️ TOOLING & SCANNING ---
            'heuristics.py': 'tools/scanner/heuristics.py',
            'traversal.py': 'tools/scanner/traversal.py',
            'canon_scanner.py': 'tools/common/canon_scanner.py',
            'pdf_scanner.py': 'tools/common/pdf_scanner.py',
            'profiler.py': 'tools/common/profiler.py',

            # --- 🏗️ INFRASTRUCTURE & INTEGRATION ---
            'micro_data_center.py': 'ops/scaling/micro_data_center.py',
            'tiga_commit.py': 'ops/scaling/tiga_commit.py',
            'contract_registry.py': 'core/integration/contract_registry.py',
            'io_linker.py': 'core/integration/io_linker.py',
            'audit_logger.py': 'logs/audit_logger.py',
            
            # --- 🕵️ DEBUG & REPAIR (The "Buried Gems") ---
            'debug_db.py': 'tools/debug/debug_db.py',
            'debug_queries.py': 'tools/debug/debug_queries.py',
            'check_db.py': 'tools/debug/checks/check_db.py',
            'check_match.py': 'tools/debug/checks/check_match.py',
            
            # --- 🧬 SELF-HEALING & REBUILD ---
            'semantic_rebuilder.py': 'core/rebuild/semantic_rebuilder.py', # The advanced feature
            'manual_rebuild.py': 'tools/rebuild/manual_rebuild.py',        # The manual tool
            'trace_rebuild.py': 'tools/rebuild/trace_rebuild.py',
            
            # --- 📊 VISUALIZATION ---
            'ui_app.py': 'tools/viz/legacy_app.py', # Streamlit backup dashboard

            # --- ⚙️ CONFIGURATION & ENTRY POINTS ---
            'methodology_library.json': 'config/methodology_library.json',
            'orchestrator_config.json': 'config/orchestrator_config.json',
            'backend_startup.py': 'backend_startup.py',  # Root Entry Point

            # --- EXISTING MAPPINGS (Preserved) ---
            # Analysis Tools
            'analysis.rule_engine.py': 'tools/analysis/analysis.rule_engine.py',
            'hydrate_memory.py': 'tools/analysis/hydrate_memory.py',
            'fi_migration.py': 'tools/analysis/fi_migration.py',
            'aletheia_mcp.py': 'tools/analysis/aletheia_mcp.py',
            'main_platform.py': 'tools/analysis/main_platform.py',
            # 'orchestrator.py': HANDLED DYNAMICALLY IN DETERMINE_TARGET
            'update_mcp_setup.py': 'tools/analysis/update_mcp_setup.py',
            
            # Core & API Components
            'ws_runner.py': 'tools/api/ws_runner.py',
            'lens_manager.py': 'tools/core/lens_manager.py',
            'shared_utils.py': 'tools/core/shared_utils.py',
            'graph_transformer.py': 'tools/core/graph_transformer.py',
            
            # Bundler Support
            'workspace_packager.py': 'tools/bundler/workspace_packager.py',
            'Directory_bundler_v4.5.py': 'tools/bundler/Directory_bundler_v4.5.py',
            
            # Ingest & RAG
            'view_knowledge.py': 'tools/ingest/view_knowledge.py',
            'rag_pipeline_v4.py': 'tools/ingest/rag_pipeline_v4.py',
            'RAG_System_Bundler.py': 'tools/ingest/rag_bundler.py', # Renamed for consistency
            
            # Workflows
            'workflow_ingest.py': 'workflows/workflow_ingest.py',
            'workflow_analyze.py': 'workflows/workflow_analyze.py',
            'workflow_extract.py': 'workflows/workflow_extract.py',
            'workflow_build_stack.py': 'workflows/workflow_build_stack.py',
            'workflow_validate_schema.py': 'workflows/workflow_validate_schema.py',
            
            # Ops / Launchers
            'run_boot.bat': 'ops/launchers/run_boot.bat',
            'run_frontend.bat': 'ops/launchers/run_frontend.bat',
            'start_backend.bat': 'ops/launchers/start_backend.bat',
            'Scan_Project_Targets.bat': 'ops/launchers/Scan_Project_Targets.bat',
            'package_workspace.bat': 'ops/launchers/package_workspace.bat',
            'migrate_to_acp.ps1': 'ops/launchers/migrate_to_acp.ps1',
            'setup_frontend.bat': 'ops/launchers/setup_frontend.bat',
            'requirements.txt': 'ops/requirements.txt',
            
            # UI / Config helpers
            'package.json': 'ui/package.json',
            'package-lock.json': 'ui/package-lock.json',
            'Local_application_dev.code-workspace': 'ops/Local_application_dev.code-workspace',

            # Reference / Documentation
            'DIRECTORY_STRUCTURE.md': 'reference/legacy_directory_structure.md',
            'README.md': 'README.md',
            '.gitignore': '.gitignore',
            'RAG_GUIDE.md': 'docs/guides/RAG_GUIDE.md',
            'LLM_WORKFLOW_BUILDER_GUIDE.md': 'docs/guides/LLM_WORKFLOW_BUILDER_GUIDE.md',
            
            # Memory / State
            'GitInfo_pb2.data.json': 'memory/project/GitInfo_pb2.data.json',
            
            # Tests (Individual files if not caught by directory map)
            'test_system.py': 'tests/test_system.py',
            'test_infrastructure.py': 'tests/test_infrastructure.py',
            'conftest.py': 'tests/conftest.py',
        }

        # 2. Directory Mappings (Medium Priority)
        self.directory_map = {
            'core/canon/canonical_code_platform_port/core': 'tools/core',
            'core/canon/canonical_code_platform_port/extracted_services': 'services',
            'core/canon/canonical_code_platform_port/tests': 'tests',
            'core/canon/canonical_code_platform_port/docs/guides': 'docs/guides',
            # Granular UI subfolders
            'ui/frontend/src/components': 'ui/frontend/components',
            'ui/frontend/src/services': 'ui/frontend/services',
            'ui/frontend/src/hooks': 'ui/frontend/hooks',
            'ui/frontend': 'ui/frontend',
            'canonical_code_platform_port': 'reference/canonical_code_platform_port',
            'canonical_code_platform__v2': 'legacy/canonical_code_platform__v2',
            'directory_bundler_port': 'legacy/directory_bundler_port'
        }

        # 3. Auto-Include Extensions (Catch-All)
        self.catch_all_extensions = {
            '.py', '.tsx', '.ts', '.jsx', '.js', 
            '.html', '.css', 
            '.ps1', '.bat', '.sh', 
            '.json', '.md'
        }

        # 4. Pattern exclusions (Low Priority)
        self.ignore_patterns = [
            r'node_modules',
            r'\.git',
            r'^git/', # Ignore explicit git folder if listed
            r'__pycache__',
            r'\.mypy_cache',
            r'\.pytest_cache',
            r'dist/',
            r'build/',
            r'\.DS_Store',
            r'.*\.log$',
            r'.*\.db$',       
            r'.*\.sqlite3$',
            r'\.bin',
            r'bin/',
            r'obj/',
            r'debug/',
            # Ignore artifacts inside discovered assets
            r'.*\.meta\.json$',
            r'.*\.data\.json$'
        ]

    def load_file_map(self):
        """Reads the CSV."""
        if not os.path.exists(self.file_map_path):
            print(f"❌ File map not found at {self.file_map_path}")
            return []

        files = []
        with open(self.file_map_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            first_row = True
            for row in reader:
                if first_row and not self.source_root and row.get('root'):
                    self.source_root = Path(row['root'])
                    print(f"📍 Detected source root from CSV: {self.source_root}")
                    first_row = False
                files.append(row)
        return files

    def should_ignore(self, rel_path):
        for pattern in self.ignore_patterns:
            if re.search(pattern, rel_path, re.IGNORECASE):
                return True
        return False

    def determine_target(self, rel_path):
        """Decides where a file goes based on the plan rules, with advanced heuristics."""
        filename = os.path.basename(rel_path)
        normalized_path = rel_path.replace('\\', '/')
        _, ext = os.path.splitext(filename)
        
        target = None

        # Special Case: Orchestrator Disambiguation
        if filename == 'orchestrator.py':
            if 'Ingest' in normalized_path or 'rag' in normalized_path.lower():
                target = 'tools/ingest/rag_orchestrator.py'
            else:
                target = 'tools/analysis/orchestrator.py'

        # 1. Exact File Match (Relative Path)
        elif rel_path in self.exact_map:
            target = self.exact_map[rel_path]
        
        # 1b. Exact Filename Match (Crucial for deep source files)
        elif filename in self.exact_map:
            target = self.exact_map[filename]

        # --- 1.5 HEURISTIC / PATTERN MATCHES (Medium Priority) ---
        # Runs before Directory matches to catch specific file types anywhere
        # A. Tests: Consolidation
        elif filename.startswith('test_') or filename == 'conftest.py':
            target = f"tests/{filename}"
        # B. Scripts & Launchers
        elif ext.lower() in ['.bat', '.ps1', '.sh']:
            target = f"ops/launchers/{filename}"
        # C. Data Artifacts
        elif filename.endswith('.data.json') or filename.endswith('.meta.json'):
            target = f"memory/project/{filename}"
        # D. Common / Shared Utilities
        elif any(k in normalized_path.lower() for k in ['common', 'shared', 'utils']) and ext == '.py':
            target = f"tools/common/{filename}"
        # E. Legacy & Reference
        elif any(k in normalized_path.lower() for k in ['legacy', 'archive', 'old', 'deprecated']):
            target = f"legacy/{filename}"
        # F. UI Granularity (if not caught by explicit directory map)
        elif 'frontend' in normalized_path.lower():
            if 'components' in normalized_path.lower():
                target = f"ui/frontend/components/{filename}"
            elif 'services' in normalized_path.lower():
                target = f"ui/frontend/services/{filename}"
            elif 'hooks' in normalized_path.lower():
                target = f"ui/frontend/hooks/{filename}"
        # G. UI Static Assets
        elif ext.lower() in ['.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico'] and 'ui' in normalized_path.lower():
            target = f"ui/static/{filename}"
        # H. Documentation & Config
        elif ext.lower() == '.md' and not target:
            target = f"docs/guides/{filename}"
        elif ext.lower() == '.json' and 'config' in normalized_path.lower() and not target:
            target = f"config/{filename}"

        # 2. Directory Match
        if not target:
            sorted_dirs = sorted(self.directory_map.items(), key=lambda x: len(x[0]), reverse=True)
            for src_dir, dest_dir in sorted_dirs:
                if normalized_path.startswith(src_dir):
                    remainder = normalized_path[len(src_dir):].lstrip('/')
                    target = f"{dest_dir}/{remainder}"
                    break
        # 3. Catch-All for Code Files
        if not target:
            if ext.lower() in self.catch_all_extensions:
                clean_path = normalized_path
                legacy_prefixes = [
                    'canonical_code_platform_port/',
                    'canonical_code_platform__v2/',
                    'directory_bundler_port/',
                    'Local_application_dev/',
                    'ACP_V1/'
                ]
                for prefix in legacy_prefixes:
                    if clean_path.startswith(prefix):
                        clean_path = clean_path[len(prefix):]
                target = f"discovered_assets/{clean_path}"

        # If a target was found, register it in the import map
        if target:
            py_path = str(target).replace('/', '.').replace('\\', '.').replace('.py', '')
            original_name = Path(rel_path).stem
            self.import_map[original_name] = py_path

        return target

    def compute_hash(self, file_path):
        """Calculates SHA256 hash for verification."""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception:
            return None

    def verify_integrity(self, source, dest):
        """Verifies that the source and destination hashes match."""
        src_hash = self.compute_hash(source)
        dest_hash = self.compute_hash(dest)
        if src_hash and dest_hash and src_hash == dest_hash:
            return True
        logging.error(f"INTEGRITY FAIL: {dest} (Hash Mismatch)")
        print(f"   ⚠️ INTEGRITY FAIL: Hash mismatch for {dest.name}")
        return False

    def scan_dependencies(self):
        """Scans migrated python files to suggest dependencies."""
        imports = set()
        for root, dirs, files in os.walk(self.target_root):
            for file in files:
                if file.endswith('.py'):
                    try:
                        with open(Path(root) / file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Basic regex to catch 'import x' and 'from x import y'
                            matches = re.findall(r'^(?:from|import)\s+([a-zA-Z0-9_]+)', content, re.MULTILINE)
                            for match in matches:
                                imports.add(match)
                    except Exception:
                        pass
        
        # Filter standard lib (approximate)
        std_lib = {'os', 'sys', 're', 'json', 'csv', 'pathlib', 'logging', 'shutil', 'datetime', 'time', 'math', 'typing', 'collections'}
        external = imports - std_lib
        
        req_path = self.target_root / "ops/suggested_requirements.txt"
        os.makedirs(req_path.parent, exist_ok=True)
        with open(req_path, 'w') as f:
            f.write("# Auto-generated suggestions based on imports found\n")
            for lib in sorted(external):
                f.write(f"{lib}\n")
        print(f"ℹ️  Dependency suggestions saved to {req_path}")
    def ensure_init_files(self):
        """Ensures every directory containing .py files has an __init__.py"""
        if self.target_root.exists():
            for root, dirs, files in os.walk(self.target_root):
                if any(f.endswith('.py') for f in files) and '__init__.py' not in files:
                    init_path = Path(root) / '__init__.py'
                    with open(init_path, 'w') as f:
                        f.write(f"# Auto-generated package init for {Path(root).name}")
                    print(f"   + Created missing __init__.py in {Path(root).relative_to(self.target_root)}")

    def plan(self):
        print("🔍 Analyzing file map and building migration plan...")
        files = self.load_file_map()
        seen_targets = {}  # For collision detection

        for file_data in files:
            rel_path = file_data['rel_path']
            if self.should_ignore(rel_path):
                self.ignored_files.append(rel_path)
                continue

            target_rel = self.determine_target(rel_path)
            if target_rel:
                source_abs = Path(file_data['abs_path']) if file_data.get('abs_path') else self.source_root / rel_path
                if not source_abs.exists():
                    local_fallback = Path(os.getcwd()) / rel_path
                    if local_fallback.exists():
                        source_abs = local_fallback
                    else:
                        self.missing_files.append(rel_path)
                        continue

                target_abs = self.target_root / target_rel

                # --- COLLISION DETECTION ---
                if str(target_abs) in seen_targets:
                    existing_source = seen_targets[str(target_abs)]
                    print(f"⚠️ COLLISION DETECTED: {target_rel}")
                    print(f"   1. {existing_source}")
                    print(f"   2. {source_abs}")
                    # Append suffix to the second file
                    target_abs = target_abs.with_name(f"{target_abs.stem}_duplicate{target_abs.suffix}")
                    print(f"   -> Renaming second file to: {target_abs.name}")

                seen_targets[str(target_abs)] = source_abs
                self.operations.append((source_abs, target_abs, "COPY"))

    def create_intent_specs(self):
        """Creates the critical intent_specs.yaml configuration."""
        content = """agent_roles:
  - name: SecurityAgent
    description: Focuses on identifying and mitigating security vulnerabilities.
    cognitive_focus: security
    validation_patterns:
      - name: dangerous_calls_regex
        pattern: '(eval|exec|compile)'
        description: Detects potentially dangerous function calls.
    provenance:
      author: "ACP System"
      version: "1.0.0"

  - name: PerformanceAgent
    description: Optimizes code for efficiency and resource utilization.
    cognitive_focus: performance
    validation_patterns:
      - name: n_plus_1_query_regex
        pattern: '(for.*in.*query.*\\n.*query.*)'
        description: Detects potential N+1 query problems.
    provenance:
      author: "ACP System"
      version: "1.0.0"
metadata:
  schema_version: "1.0"
  last_updated: "2026-02-05"
"""
        target_path = self.target_root / "config/intent_specs.yaml"
        # Using a special tuple format for creating content: (None, target, "CREATE_CONTENT", content_string)
        self.operations.append((None, target_path, "CREATE_CONTENT", content))

    def create_placeholders(self):
        """Creates .keep files for all major target directories to preserve structure."""
        placeholders = [
            'ops/diagnostics/scan_assessment.md',
            'ops/diagnostics/ai_verification.md',
            'memory/project/.keep',
            'memory/task/.keep',
            'memory/schemas/.keep',
            'memory/components/.keep',
            'memory/documents/.keep',
            # New structure preservation
            'ui/static/.keep',
            'ui/frontend/components/.keep',
            'ui/frontend/services/.keep',
            'ui/frontend/hooks/.keep',
            'tools/common/.keep',
            'legacy/.keep',
            'reference/.keep',
            'docs/guides/.keep',
            'config/.keep'
        ]
        
        for p in placeholders:
            target_path = self.target_root / p
            self.operations.append((None, target_path, "CREATE"))


    def execute(self, dry_run=True):
        self.plan()
        self.create_intent_specs()
        self.create_placeholders()
        
        # --- Export Plan for Review ---
        plan_path = Path("migration_plan.csv")
        with open(plan_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Source", "Destination", "Action"])
            for op in self.operations:
                writer.writerow([str(op[0]), str(op[1]), op[2]])
        print(f"ℹ️  Migration plan exported to {plan_path.absolute()}")

        print(f"\n📋 Plan Summary:")
        print(f"   Target: {self.target_root.absolute()}")
        print(f"   Files to Copy:  {len([op for op in self.operations if op[2] == 'COPY'])}")
        print(f"   Files Ignored:  {len(self.ignored_files)}")
        print(f"   Missing Source: {len(self.missing_files)}")
        
        if dry_run:
            print("\n🚧 DRY RUN COMPLETE. No files moved.")
            print("   (Change dry_run=False in the script to execute)")
            return

        print("\n🚀 Executing Migration...")
        if not self.target_root.exists():
            os.makedirs(self.target_root)

        count = 0
        for op in self.operations:
            # Handle variable length tuple for CREATE_CONTENT
            source = op[0]
            dest = op[1]
            action = op[2]
            
            try:
                if source and source.resolve() == dest.resolve():
                    continue

                if dest.parent:
                    os.makedirs(dest.parent, exist_ok=True)
                
                if action == "COPY":
                    if source.is_file():
                        shutil.copy2(source, dest)
                        if self.verify_integrity(source, dest):
                            count += 1
                            logging.info(f"SUCCESS: {source} -> {dest}")
                    elif source.is_dir():
                        shutil.copytree(source, dest, dirs_exist_ok=True)
                        count += 1
                        logging.info(f"SUCCESS: {source} -> {dest}")
                elif action == "CREATE":
                    if not dest.exists():
                        with open(dest, 'w') as f:
                            if dest.suffix == '.md':
                                f.write(f"# {dest.stem.replace('_', ' ').title()}\n\nPlaceholder generated by ACP Migration.")
                        print(f"   + Created placeholder: {dest.name}")
                        logging.info(f"PLACEHOLDER: {dest}")
                elif action == "CREATE_CONTENT":
                    content = op[3]
                    with open(dest, 'w') as f:
                        f.write(content)
                    print(f"   + Created configuration: {dest.name}")
                    logging.info(f"CONFIG: {dest}")

            except Exception as e:
                error_msg = f"ERROR copying {source} to {dest}: {e}"
                print(f"   ❌ {error_msg}")
                logging.error(error_msg)

        # --- Import Map Output ---
        map_path = self.target_root / "migration_import_map.json"
        with open(map_path, 'w') as f:
            json.dump(self.import_map, f, indent=2)
        print(f"ℹ️  Import mapping saved to {map_path}. Use this to update imports.")
        logging.info(f"IMPORT_MAP: {map_path}")

        # --- Ensure __init__.py files ---
        self.ensure_init_files()
        
        # --- Scan Dependencies ---
        self.scan_dependencies()

        print(f"\n✅ Migration Complete. {count} files migrated.")

if __name__ == "__main__":
    csv_file = "file_map.csv"
    migrator = ACPMigrator(file_map_path=csv_file)
    migrator.execute(dry_run=False)