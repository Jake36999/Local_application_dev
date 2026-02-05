import ast
import uuid
from typing import Dict, Any, List


class CanonScanner(ast.NodeVisitor):
    def __init__(self, db_cursor, source_code: str, file_path: str):
        self.cursor = db_cursor
        self.source = source_code
        self.file_path = file_path
        self.stack: List[Dict[str, str]] = []

    def scan(self) -> None:
        tree = ast.parse(self.source)
        self.visit(tree)

    def _register(self, node: ast.AST, kind: str, name: str) -> Dict[str, str]:
        cid = str(uuid.uuid4())
        segment = ast.get_source_segment(self.source, node) or ""
        self.cursor.execute(
            "INSERT INTO canon_components (id, file, kind, name, code_snippet) VALUES (?, ?, ?, ?, ?)",
            (cid, self.file_path, kind, name, segment),
        )
        return {"id": cid, "name": name}

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:  # type: ignore[override]
        comp = self._register(node, "function", node.name)
        self.stack.append(comp)
        self.generic_visit(node)
        self.stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> Any:  # type: ignore[override]
        comp = self._register(node, "async_function", node.name)
        self.stack.append(comp)
        self.generic_visit(node)
        self.stack.pop()

    def visit_ClassDef(self, node: ast.ClassDef) -> Any:  # type: ignore[override]
        comp = self._register(node, "class", node.name)
        self.stack.append(comp)
        self.generic_visit(node)
        self.stack.pop()


def canon_scan(path: str, db_conn) -> Dict[str, str]:
    with open(path, "r", encoding="utf-8") as handle:
        code = handle.read()

    scanner = CanonScanner(db_conn.cursor(), code, path)
    scanner.scan()
    db_conn.commit()
    return {"status": "success", "msg": f"Scanned {path}"}
