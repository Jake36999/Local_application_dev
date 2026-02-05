import json
import os

scan_dir = 'bundler_scans/89fa1f06/chunks'
print(f"Checking chunks in {scan_dir}...\n")

chunk_files = sorted([f for f in os.listdir(scan_dir) if f.endswith('.json')])[:5]

for chunk_file in chunk_files:
    filepath = os.path.join(scan_dir, chunk_file)
    with open(filepath, 'r', encoding='utf-8') as f:
        chunk = json.load(f)
    
    print(f"{chunk_file}:")
    print(f"  Keys: {list(chunk.keys())}")
    
    if 'ai_overview' in chunk:
        print(f"  ✓ Has ai_overview")
        print(f"    Keys: {list(chunk['ai_overview'].keys())}")
    else:
        print(f"  ✗ Missing ai_overview")
    
    if 'files' in chunk and chunk['files']:
        first_file = chunk['files'][0]
        if 'ai_analysis' in first_file:
            print(f"  ✓ Files have ai_analysis")
        else:
            print(f"  ✗ Files missing ai_analysis")
    print()

print("\n=== Checking for any Python files in chunks ===")
for chunk_file in chunk_files[:1]:  # Just first chunk
    filepath = os.path.join(scan_dir, chunk_file)
    with open(filepath, 'r', encoding='utf-8') as f:
        chunk = json.load(f)
    
    if 'files' in chunk:
        py_files = [f for f in chunk['files'] if f['path'].endswith('.py')]
        print(f"Python files in {chunk_file}: {len(py_files)}")
        if py_files:
            print(f"First Python file: {py_files[0]['path']}")
            if 'analysis' in py_files[0]:
                print(f"  analysis keys: {list(py_files[0]['analysis'].keys())}")
