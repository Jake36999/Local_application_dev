import argparse
import importlib
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, cast

try:
    PDFProcessor = cast(Any, importlib.import_module("core.pdf_processor").PDFProcessor)
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    PDFProcessor = cast(Any, importlib.import_module("core.pdf_processor").PDFProcessor)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("LibraryBuilder")


DEFAULT_OUTPUT_BASE = Path(__file__).resolve().parents[2] / "cli_scans" / "knowledge_bundle"

def build_library(input_dir: str, output_name: str = str(DEFAULT_OUTPUT_BASE)) -> None:
    """Build a Markdown bundle + JSON index from PDFs using PDFProcessor (OCR-aware)."""
    input_path = Path(input_dir).resolve()
    if not input_path.exists():
        logger.error(f"Directory not found: {input_dir}")
        return

    output_base = Path(output_name)
    if not output_base.is_absolute():
        output_base = input_path / output_base

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    bundle_dir = output_base.parent / f"{output_base.stem}_bundle_{timestamp}"
    bundle_dir.mkdir(parents=True, exist_ok=True)

    processor = PDFProcessor()
    files: List[Path] = sorted([f for f in input_path.iterdir() if f.suffix.lower() == ".pdf"])
    if not files:
        logger.warning(f"No PDFs found in {input_dir}")
        return

    markdown_content: List[str] = []
    documents_index: List[Dict[str, Any]] = []
    json_index: Dict[str, Any] = {
        "bundle_name": output_base.stem,
        "generated_at": datetime.now().isoformat(),
        "total_documents": len(files),
        "documents": documents_index,
        "source_dir": str(input_path),
        "bundle_dir": str(bundle_dir),
    }

    chunk_jsonl_path = bundle_dir / f"{output_base.stem}_chunks.jsonl"
    json_index["chunk_file"] = chunk_jsonl_path.name

    markdown_content.append(f"# Knowledge Library: {output_base.stem}\n")
    markdown_content.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    markdown_content.append(f"**Source Directory:** {input_path}\n")
    markdown_content.append(f"**Document Count:** {len(files)}\n")
    markdown_content.append("---\n")

    logger.info(f"Starting ingestion of {len(files)} documents...")
    total_chunks = 0

    md_filename = bundle_dir / f"{output_base.stem}.md"
    json_filename = bundle_dir / f"{output_base.stem}_index.json"

    with open(chunk_jsonl_path, "w", encoding="utf-8") as chunk_stream:
        for order, file_path in enumerate(files, 1):
            logger.info(f"Processing ({order}/{len(files)}): {file_path.name}")
            try:
                chunks = processor.process_file(file_path)
                full_text = "\n".join(chunk["content"] for chunk in chunks)

                documents_index.append(
                    {
                        "order": order,
                        "filename": file_path.name,
                        "char_count": len(full_text),
                        "chunk_count": len(chunks),
                        "processed_successfully": True,
                    }
                )

                for chunk in chunks:
                    meta = chunk["metadata"]
                    record = {
                        "id": meta["chunk_id"],
                        "text": chunk["content"],
                        "metadata": {
                            "source": meta["file_name"],
                            "page": meta["page_number"],
                            "ocr": meta["ocr_applied"],
                            "global_idx": meta["chunk_index_global"],
                            "chunk_group": meta["chunk_index_global"] // 20,
                            "page_char_start": meta["page_char_start"],
                            "page_char_end": meta["page_char_end"],
                            "char_count": meta["char_count"],
                        },
                    }
                    chunk_stream.write(json.dumps(record) + "\n")
                total_chunks += len(chunks)

                markdown_content.append(f"# DOC {order}: {file_path.name}")
                markdown_content.append("## Metadata")
                markdown_content.append(f"- **Filename:** `{file_path.name}`")
                markdown_content.append(f"- **Size:** {len(full_text)} chars")
                markdown_content.append(f"- **Chunks:** {len(chunks)}")
                markdown_content.append(
                    f"- **OCR Used:** {'Yes' if any(c['metadata']['ocr_applied'] for c in chunks) else 'No'}"
                )
                markdown_content.append("\n## Content\n")
                markdown_content.append(full_text)
                markdown_content.append("\n---\n")
            except Exception as e:  # pylint: disable=broad-except
                logger.error(f"Failed to process {file_path.name}: {e}")
                documents_index.append(
                    {
                        "order": order,
                        "filename": file_path.name,
                        "error": str(e),
                        "processed_successfully": False,
                    }
                )

    json_index["total_chunks"] = total_chunks

    with open(md_filename, "w", encoding="utf-8") as f:
        f.write("\n".join(markdown_content))
    logger.info(f"Saved text bundle to: {md_filename}")

    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(json_index, f, indent=4)
    logger.info(f"Saved structure index to: {json_filename}")
    logger.info(f"Saved chunk database to: {chunk_jsonl_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aletheia Library Builder (PDF -> MD+JSON)")
    parser.add_argument("input_dir", help="Folder containing PDFs")
    parser.add_argument(
        "-o",
        "--output",
        default=str(DEFAULT_OUTPUT_BASE),
        help="Output filename base (absolute or relative; default: cli_scans/knowledge_bundle)",
    )
    args = parser.parse_args()
    build_library(args.input_dir, args.output)
