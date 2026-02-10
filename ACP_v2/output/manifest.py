
import pathlib
import json
import os
import shutil
import sys
import hashlib # Added for direct hash verification in tests

# Add parent directory to path to allow importing sibling modules
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from scanner.traversal import traverse_directory
from data.provenance import generate_hashes

def generate_manifest(root_dir: pathlib.Path, output_filepath: pathlib.Path):
    """
    Generates a streaming JSONL manifest of files in the root_dir,
    including their paths and hashes, with an O(1) memory footprint per file object.
    """
    if not root_dir.is_dir():
        raise ValueError(f"Root directory not found: {root_dir}")

    print(f"Generating manifest for '{root_dir}' to '{output_filepath}'...")
    with open(output_filepath, 'w') as f_out:
        for file_path in traverse_directory(root_dir):
            try:
                hashes = generate_hashes(file_path)
                relative_path = str(file_path.relative_to(root_dir))
                absolute_path = str(file_path.resolve())

                file_entry = {
                    'relative_path': relative_path,
                    'absolute_path': absolute_path,
                    'hashes': hashes
                }
                f_out.write(json.dumps(file_entry) + '\n')
            except Exception as e:
                print(f"Warning: Could not process file '{file_path}': {e}", file=sys.stderr)

    print("Manifest generation complete.")

if __name__ == '__main__':
    # --- Test Cases ---
    test_root = pathlib.Path('./test_project_for_manifest')
    test_manifest_path = pathlib.Path('./output/test_manifest.jsonl')

    # Cleanup from previous runs
    if test_root.exists():
        shutil.rmtree(test_root)
    if test_manifest_path.exists():
        os.remove(test_manifest_path)

    # Create dummy directory structure
    test_root.mkdir(exist_ok=True)
    (test_root / 'file_a.txt').write_text('content A')
    (test_root / 'dir1').mkdir(exist_ok=True)
    (test_root / 'dir1' / 'file_b.py').write_text('import os\nprint("B")')
    (test_root / 'dir2').mkdir(exist_ok=True)
    (test_root / 'dir2' / 'file_c.md').write_text('# Markdown C')
    # Changed '.git_repo' to '.git' to ensure it's excluded by traverse_directory
    (test_root / '.git').mkdir(exist_ok=True) # Should be excluded by traversal
    (test_root / '.git' / 'config').write_text('[core]') # This file inside .git will be skipped

    # Generate the manifest
    generate_manifest(test_root, test_manifest_path)

    # Verify the generated manifest
    print(f"\nVerifying manifest at '{test_manifest_path}'...")
    expected_files = {
        'file_a.txt': 'content A',
        'dir1/file_b.py': 'import os\nprint("B")',
        'dir2/file_c.md': '# Markdown C'
    }
    found_entries = []

    assert test_manifest_path.exists(), "Manifest file was not created!"

    with open(test_manifest_path, 'r') as f_in:
        for line in f_in:
            entry = json.loads(line.strip())
            found_entries.append(entry)

    assert len(found_entries) == len(expected_files), \
        f"Expected {len(expected_files)} entries, but found {len(found_entries)}"

    for entry in found_entries:
        rel_path = entry['relative_path']
        abs_path = entry['absolute_path']
        hashes = entry['hashes']

        assert rel_path in expected_files, f"Unexpected file in manifest: {rel_path}"
        assert pathlib.Path(abs_path).is_file(), f"Absolute path does not exist: {abs_path}"
        assert 'md5' in hashes and 'sha256' in hashes, "Hashes missing from entry!"

        # Verify content hashes
        expected_content = expected_files[rel_path].encode('utf-8')
        assert hashes['md5'] == hashlib.md5(expected_content).hexdigest(), f"MD5 mismatch for {rel_path}"
        assert hashes['sha256'] == hashlib.sha256(expected_content).hexdigest(), f"SHA256 mismatch for {rel_path}"

    print("Manifest verification successful! All checks passed.")

    # --- Cleanup ---
    shutil.rmtree(test_root)
    os.remove(test_manifest_path)

