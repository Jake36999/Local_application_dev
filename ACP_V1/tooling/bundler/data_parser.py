import csv
import io
import json
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional


class DataParser:
    """Lightweight structured parsers for CSV, TSV, JSON, and XML."""

    MAX_SAMPLE_ROWS = 50
    MAX_SAMPLE_ELEMENTS = 50

    @staticmethod
    def _cast_value(value: str) -> Any:
        if value is None:
            return None
        text = value.strip()
        if text == "":
            return ""
        # Numeric casting
        try:
            return int(text)
        except ValueError:
            pass
        try:
            return float(text)
        except ValueError:
            pass
        # Boolean casting
        lower = text.lower()
        if lower in ("true", "false"):
            return lower == "true"
        return text

    @classmethod
    def parse_csv(cls, content: str) -> Optional[Dict[str, Any]]:
        sample = content[:4096]
        delimiter = ","
        line_terminator = "\n"
        has_header = True
        try:
            dialect = csv.Sniffer().sniff(sample)
            delimiter = dialect.delimiter
            line_terminator = getattr(dialect, "lineterminator", "\n") or "\n"
            has_header = csv.Sniffer().has_header(sample)
        except Exception:
            delimiter = "\t" if "\t" in sample else ","
            has_header = True

        # Build fieldnames
        reader_preview = csv.reader(io.StringIO(content), delimiter=delimiter)
        first_row = next(reader_preview, [])
        if has_header and first_row:
            fieldnames = [col if col else f"col_{idx+1}" for idx, col in enumerate(first_row)]
            data_stream = io.StringIO(content)
            dict_reader = csv.DictReader(data_stream, delimiter=delimiter)
        else:
            fieldnames = [f"col_{idx+1}" for idx in range(len(first_row))]
            data_stream = io.StringIO(content)
            dict_reader = csv.DictReader(data_stream, delimiter=delimiter, fieldnames=fieldnames)

        rows: List[Dict[str, Any]] = []
        row_count = 0
        for row in dict_reader:
            row_count += 1
            if len(rows) < cls.MAX_SAMPLE_ROWS:
                casted = {k: cls._cast_value(v) for k, v in row.items()}
                rows.append(casted)

        return {
            "type": "csv",
            "delimiter": delimiter,
            "lineterminator": line_terminator,
            "has_header": has_header,
            "headers": fieldnames,
            "row_count": row_count,
            "sample_rows": rows,
        }

    @classmethod
    def parse_xml(cls, content: str) -> Optional[Dict[str, Any]]:
        try:
            root = ET.fromstring(content)
        except Exception:
            return None

        samples: List[Dict[str, Any]] = []
        total = 0

        def _walk(node: ET.Element, path: str):
            nonlocal total
            if total >= cls.MAX_SAMPLE_ELEMENTS:
                return
            total += 1
            entry = {
                "path": path,
                "tag": node.tag,
                "text": (node.text or "").strip(),
                "attributes": node.attrib or {},
            }
            samples.append(entry)
            for idx, child in enumerate(list(node)):
                child_path = f"{path}/{child.tag}[{idx}]"
                _walk(child, child_path)

        _walk(root, f"/{root.tag}")

        return {
            "type": "xml",
            "root_tag": root.tag,
            "sample_elements": samples,
            "sample_count": len(samples),
        }

    @staticmethod
    def parse_json(content: str) -> Optional[Dict[str, Any]]:
        try:
            data = json.loads(content)
        except Exception:
            return None
        return {
            "type": "json",
            "preview": data,
        }

    @classmethod
    def parse_structured(cls, extension: str, content: str) -> Optional[Dict[str, Any]]:
        ext = extension.lower()
        if ext in (".csv", ".tsv"):
            return cls.parse_csv(content)
        if ext == ".xml":
            return cls.parse_xml(content)
        if ext == ".json":
            return cls.parse_json(content)
        return None
