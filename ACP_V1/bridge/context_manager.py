
import math
import json
import pathlib
import sys

# Attempt to load default LLM context length from config, fallback if not available
DEFAULT_LLM_CONTEXT_LENGTH = 262144 # Fallback default
config_file = pathlib.Path('tooling/lms_config.json')
if config_file.exists():
    try:
        with open(config_file, 'r') as f:
            lms_config = json.load(f)
            DEFAULT_LLM_CONTEXT_LENGTH = lms_config.get('context_length', DEFAULT_LLM_CONTEXT_LENGTH)
    except json.JSONDecodeError:
        print(f"Warning: Could not parse {config_file}, using default LLM context length.", file=sys.stderr)

def chunk_text_with_overlap(text: str, chunk_size: int = 12000, overlap_size: int = 500, llm_context_length: int = DEFAULT_LLM_CONTEXT_LENGTH) -> list[str]:
    """
    Segments a given text into chunks with a specified chunk size and overlap.
    Ensures semantic continuity across chunks for local LLMs.
    The chunk_size will be capped by llm_context_length if it exceeds it.
    """
    if not text:
        return []
    if chunk_size <= overlap_size:
        raise ValueError("Chunk size must be greater than overlap size.")

    # Enforce LLM context length constraint
    if chunk_size > llm_context_length:
        print(f"Warning: Requested chunk_size ({chunk_size}) exceeds LLM's context length ({llm_context_length}). Capping chunk_size to {llm_context_length}.", file=sys.stderr)
        chunk_size = llm_context_length

    chunks = []
    start_index = 0
    text_length = len(text)

    while start_index < text_length:
        end_index = min(start_index + chunk_size, text_length)
        chunk = text[start_index:end_index]
        chunks.append(chunk)

        if end_index == text_length:
            break # Reached the end of the text

        # For the next chunk, move back by the overlap size
        start_index += chunk_size - overlap_size

    return chunks

if __name__ == '__main__':
    # --- Test Cases ---
    print(f"\n--- Testing chunk_text_with_overlap (LLM context length: {DEFAULT_LLM_CONTEXT_LENGTH}) ---")

    # Test 1: Simple text, expected 3 chunks
    print("\nTest Case 1: Simple text, expected 3 chunks")
    text1 = "A" * 10000
    chunks1 = chunk_text_with_overlap(text1, chunk_size=5000, overlap_size=1000)
    print(f"Original length: {len(text1)}, Number of chunks: {len(chunks1)}")
    assert len(chunks1) == 3, f"Expected 3 chunks, got {len(chunks1)}"
    assert len(chunks1[0]) == 5000, f"Chunk 0 length mismatch: {len(chunks1[0])}"
    assert len(chunks1[1]) == 5000, f"Chunk 1 length mismatch: {len(chunks1[1])}"
    assert len(chunks1[2]) == 2000, f"Chunk 2 length mismatch: {len(chunks1[2])}"
    assert chunks1[0][-1000:] == chunks1[1][:1000], "Overlap content mismatch for Test 1 (0-1)!"
    assert chunks1[1][-1000:] == chunks1[2][:1000], "Overlap content mismatch for Test 1 (1-2)!"
    print("Test 1 Passed.")

    # Test 2: Text that requires a partial last chunk
    print("\nTest Case 2: Text that requires a partial last chunk")
    text2 = "B" * 12345
    chunks2 = chunk_text_with_overlap(text2, chunk_size=5000, overlap_size=500)
    print(f"Original length: {len(text2)}, Number of chunks: {len(chunks2)}")
    assert len(chunks2) == 3, f"Expected 3 chunks, got {len(chunks2)}"
    assert len(chunks2[0]) == 5000
    assert len(chunks2[1]) == 5000
    assert len(chunks2[2]) == 3345
    assert chunks2[0][-500:] == chunks2[1][:500], "Overlap content mismatch for Test 2 (1-2)!"
    assert chunks2[1][-500:] == chunks2[2][:500], "Overlap content mismatch for Test 2 (2-3)!"
    print("Test 2 Passed.")

    # Test 3: Short text (less than chunk_size)
    print("\nTest Case 3: Short text")
    text3 = "C" * 500
    chunks3 = chunk_text_with_overlap(text3, chunk_size=1000, overlap_size=100)
    print(f"Original length: {len(text3)}, Number of chunks: {len(chunks3)}")
    assert len(chunks3) == 1, f"Expected 1 chunk, got {len(chunks3)}"
    assert len(chunks3[0]) == 500, f"Chunk length mismatch: {len(chunks3[0])}"
    print("Test 3 Passed.")

    # Test 4: Empty text
    print("\nTest Case 4: Empty text")
    text4 = ""
    chunks4 = chunk_text_with_overlap(text4)
    print(f"Original length: {len(text4)}, Number of chunks: {len(chunks4)}")
    assert len(chunks4) == 0, f"Expected 0 chunks, got {len(chunks4)}"
    print("Test 4 Passed.")

    # Test 5: Chunk size equal to overlap size (should raise ValueError)
    print("\nTest Case 5: Chunk size <= overlap size")
    try:
        chunk_text_with_overlap("Some text", chunk_size=500, overlap_size=500)
        assert False, "ValueError was not raised!"
    except ValueError as e:
        assert "Chunk size must be greater than overlap size." in str(e)
        print("Test 5 Passed: ValueError caught as expected.")

    # Test 6: Chunk size exceeds LLM context length (should be capped)
    print("\nTest Case 6: Chunk size exceeds LLM context length (should be capped)")
    # Assuming default LLM context length is 262144
    large_chunk_size = DEFAULT_LLM_CONTEXT_LENGTH + 1000
    text5 = "D" * (DEFAULT_LLM_CONTEXT_LENGTH + 5000) # Text larger than LLM context
    chunks5 = chunk_text_with_overlap(text5, chunk_size=large_chunk_size, overlap_size=500)
    print(f"Original length: {len(text5)}, Number of chunks: {len(chunks5)}")
    assert chunks5[0] == "D" * DEFAULT_LLM_CONTEXT_LENGTH, "Test 6 Failed: Chunk not capped correctly!"
    assert len(chunks5[0]) == DEFAULT_LLM_CONTEXT_LENGTH, "Test 6 Failed: First chunk length not LLM context length!"
    print("Test 6 Passed.")

    print("\nAll chunking tests completed successfully!")
