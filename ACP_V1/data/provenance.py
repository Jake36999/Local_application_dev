
import pathlib
import hashlib
import os
import shutil

def generate_hashes(filepath: pathlib.Path):
    """
    Generates MD5 and SHA-256 hashes for the content of a given file.
    Returns a dictionary with 'md5' and 'sha256' keys.
    """
    if not filepath.is_file():
        raise FileNotFoundError(f"File not found: {filepath}")

    md5_hash = hashlib.md5()
    sha256_hash = hashlib.sha256()

    # Read file in chunks to handle large files efficiently
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192): # Read in 8KB chunks
            md5_hash.update(chunk)
            sha256_hash.update(chunk)

    return {
        'md5': md5_hash.hexdigest(),
        'sha256': sha256_hash.hexdigest()
    }

if __name__ == '__main__':
    # --- Test Cases ---
    test_dir = pathlib.Path('./test_provenance')
    test_dir.mkdir(exist_ok=True)

    # Create a sample file
    sample_file_path = test_dir / 'sample.txt'
    sample_content = "This is some sample content for hashing.\nIt has multiple lines."
    sample_file_path.write_text(sample_content)

    # Generate hashes for the sample file
    print(f"Generating hashes for '{sample_file_path}'")
    hashes = generate_hashes(sample_file_path)
    print(f"  MD5: {hashes['md5']}")
    print(f"  SHA-256: {hashes['sha256']}")

    # Verify hashes (e.g., against known values for this specific content)
    expected_md5 = hashlib.md5(sample_content.encode('utf-8')).hexdigest()
    expected_sha256 = hashlib.sha256(sample_content.encode('utf-8')).hexdigest()

    assert hashes['md5'] == expected_md5, "MD5 hash mismatch!"
    assert hashes['sha256'] == expected_sha256, "SHA-256 hash mismatch!"
    print("  Hashes verified successfully!")

    # Test with an empty file
    empty_file_path = test_dir / 'empty.txt'
    empty_file_path.touch()
    empty_hashes = generate_hashes(empty_file_path)
    print(f"\nGenerating hashes for empty file '{empty_file_path}'")
    print(f"  MD5: {empty_hashes['md5']}")
    print(f"  SHA-256: {empty_hashes['sha256']}")
    assert empty_hashes['md5'] == hashlib.md5(b'').hexdigest(), "Empty file MD5 mismatch!"
    assert empty_hashes['sha256'] == hashlib.sha256(b'').hexdigest(), "Empty file SHA-256 mismatch!"
    print("  Empty file hashes verified successfully!")

    print("\nAll provenance hash generation tests passed successfully!")

    # --- Cleanup ---
    shutil.rmtree(test_dir)
