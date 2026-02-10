from pathlib import Path
import re

files = [
    Path("WORKFLOWS.md"),
    Path("QUICKSTART.md"),
    Path("DIRECTORY_STRUCTURE.md"),
    Path("ARCHITECTURE.md"),
    Path("MIGRATION_GUIDE.md"),
    Path("CLEANUP_SUMMARY.md"),
    Path("VERIFICATION_PLAN.md"),
    Path("tools/README.md"),
    Path("staging/README.md"),
    Path("PART6_COMPLETION_SUMMARY.md"),
    Path("MIGRATION_GUIDE_PART6.md"),
    Path("README.md"),
    Path("start.bat"),
    Path("rebuild_verifier.py"),
    Path("core/rebuild_verifier.py"),
    Path("tools/trace_rebuild.py"),
    Path("tools/debug_db.py"),
    Path("workflow_ingest_enhanced.py"),
    Path("workflows/ingest_workflow.py"),
]

# Ordered replacements to avoid duplicate prefixes.
simple_replacements = [
    ("workflows/workflows/workflow_ingest.py", "workflows/workflow_ingest.py"),
    ("workflows/workflows/workflow_extract.py", "workflows/workflow_extract.py"),
    ("python workflow_ingest.py", "python workflows/workflow_ingest.py"),
    ("python workflow_extract.py", "python workflows/workflow_extract.py"),
    ("python workflow_verify.py", "python workflows/workflow_verify.py"),
]

regex_replacements = [
    (re.compile(r"(?<!workflows/)workflow_ingest\.py"), "workflows/workflow_ingest.py"),
    (re.compile(r"(?<!workflows/)workflow_extract\.py"), "workflows/workflow_extract.py"),
    (re.compile(r"(?<!workflows/)workflow_verify\.py"), "workflows/workflow_verify.py"),
]

for file in files:
    if not file.exists():
        continue

    text = file.read_text(encoding="utf-8")
    new_text = text

    for old, new in simple_replacements:
        new_text = new_text.replace(old, new)

    for pattern, repl in regex_replacements:
        new_text = pattern.sub(repl, new_text)

    if new_text != text:
        file.write_text(new_text, encoding="utf-8")
        print(f"updated {file}")
