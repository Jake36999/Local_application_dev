import ast
import uuid
import hashlib
import json
import re
import datetime

def uid():
    return str(uuid.uuid4())

def sha256(s: str) -> str:
    """Compute SHA256 digest."""
    return hashlib.sha256(s.encode()).hexdigest()

class CanonExtractor(ast.NodeVisitor):
    def __init__(self, source, file_id, conn, history=None):
        self.source = source
        self.file_id = file_id
        self.conn = conn
        self.history = history or {}  # Format: {qualified_name: (committed_hash, committed_at)}
        
        # Stack to track hierarchy (e.g. Class -> Method -> Inner Function)
        self.component_stack = []
        self.order_counter = 0
        
        # Track local variables to distinguish global vs local writes
        self.defined_locals = set()
        
        # Symbol tracking (Phase 2)
        self.scope_stack = []  # Track nested scopes
        self.symbols_in_component = {}  # {component_id: {name: (kind, access_type, lineno)}}
        
        # Metadata capture (Phase 4)
        self.metadata_for_component = {}  # {component_id: {indent, docstring, comments}}

    # ---------------- utilities ----------------

    def _cursor(self):
        return self.conn.cursor()

    def _parent(self):
        # Returns the ID of the component we are currently inside (or None if top-level)
        return self.component_stack[-1]["component_id"] if self.component_stack else None

    def _qualified(self, name):
        # Builds "MyClass.my_method"
        parents = [c["name"] for c in self.component_stack]
        return ".".join(parents + [name])

    def _current_component_id(self):
        """Returns the ID of the current innermost component."""
        return self.component_stack[-1]["component_id"] if self.component_stack else None
    
    def _record_variable(self, name, access_type, lineno, is_param=False, type_hint=None):
        """Track variable definitions (read/write) for symbol table."""
        cid = self._current_component_id()
        if not cid:
            return
        
        if cid not in self.symbols_in_component:
            self.symbols_in_component[cid] = {}
        
        # Track access: 'read' overwrites to 'both' if already 'write', and vice versa
        existing = self.symbols_in_component[cid].get(name, (None, None, None, False, None))
        _, existing_access, _, _, _ = existing
        
        if existing_access and existing_access != access_type:
            combined_access = "both"
        else:
            combined_access = access_type
        
        self.symbols_in_component[cid][name] = (name, combined_access, lineno, is_param, type_hint)

    def _extract_metadata(self, node, cid):
        """Extract formatting and docstring metadata for semantic rebuild (Phase 4)."""
        metadata = {
            "indent_level": len(self.component_stack),
            "has_docstring": 0,
            "docstring_type": None,
            "leading_comments": "",
            "trailing_comments": ""
        }
        
        # Check for docstring (only applicable to certain node types)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if (node.body and isinstance(node.body[0], ast.Expr) and 
                isinstance(node.body[0].value, ast.Constant) and 
                isinstance(node.body[0].value.value, str)):
                metadata["has_docstring"] = 1
                docstring = node.body[0].value.value
                if '"""' in self.source[node.lineno-1:node.end_lineno]:
                    metadata["docstring_type"] = "triple_double"
                elif "'''" in self.source[node.lineno-1:node.end_lineno]:
                    metadata["docstring_type"] = "triple_single"
                else:
                    metadata["docstring_type"] = "single_line"
        
        # Extract source to capture formatting hints
        segment = ast.get_source_segment(self.source, node)
        if segment:
            lines = segment.split('\n')
            # Leading comments (before the def/class line)
            leading = []
            for line in lines[:3]:  # Check first few lines
                stripped = line.strip()
                if stripped.startswith('#') and not stripped.startswith('# @'):
                    leading.append(stripped)
            metadata["leading_comments"] = '\n'.join(leading)
        
        self.metadata_for_component[cid] = metadata
        
        # Store in database
        hints_json = json.dumps({k: v for k, v in metadata.items() 
                                if k not in ["indent_level", "has_docstring"]})
        
        self._write("""
            INSERT INTO rebuild_metadata VALUES (?,?,?,?,?,?,?,?)
        """, (
            uid(), cid,
            metadata["indent_level"],
            metadata["has_docstring"],
            metadata["docstring_type"],
            metadata["leading_comments"],
            metadata["trailing_comments"],
            hints_json
        ))

    def _write(self, sql, params):
        c = self._cursor()
        c.execute(sql, params)
        self.conn.commit()

    # ---------------- component registration ----------------

    def _extract_comment_metadata(self, node):
        """Collect leading/trailing @-style comment tags around a node."""
        lines = self.source.splitlines()
        directives = []
        
        # Parse leading comments (lines BEFORE node.lineno)
        i = node.lineno - 2  # 0-indexed
        while i >= 0:
            line = lines[i].strip()
            
            # Stop at blank lines or non-comment lines
            if not line or not line.startswith('#'):
                break
            
            # Extract @-directives
            if line.startswith('# @'):
                # Strip "# @" prefix and split by "|" for multiple directives
                content = line[3:].strip()  # Remove "# @"
                parts = [p.strip() for p in content.split('|')]
                directives.extend(parts)
            
            i -= 1
    
        # Parse trailing comments (lines AFTER node.end_lineno)
        j = getattr(node, 'end_lineno', node.lineno)
        while j < len(lines):
            line = lines[j].strip()
            
            if not line or not line.startswith('#'):
                break
            
            if line.startswith('# @'):
                content = line[3:].strip()
                parts = [p.strip() for p in content.split('|')]
                directives.extend(parts)
            
            j += 1
        
        return {"directives": directives}
            
        j += 1
    
        return {"directives": directives}

    def _register_component(self, node, kind, name):
        """Registers a code block as a Component (for Rebuild & Source Storage)."""
        cid = uid()
        # Get exact source text for this node
        segment = ast.get_source_segment(self.source, node)
        
        # Guard against nodes having no source segment (e.g. dynamically generated)
        if segment is None:
            segment = ""

        qualified_name = self._qualified(name)
        source_hash = sha256(segment)

        # PHASE 1: Check history for committed identity
        if qualified_name in self.history:
            # ADOPT COMMITTED IDENTITY
            committed_hash, committed_at = self.history[qualified_name]
            is_new = False
            print(f"  [ADOPT] {qualified_name[:50]:50} | {committed_hash[:8]}")
        else:
            # NEW IDENTITY
            committed_hash = source_hash
            committed_at = datetime.datetime.utcnow().isoformat()
            is_new = True
            print(f"  [NEW]   {qualified_name[:50]:50} | {committed_hash[:8]}")

        rec = {
            "component_id": cid,
            "file_id": self.file_id,
            "parent_id": self._parent(),
            "kind": kind,
            "name": name,
            "qualified_name": qualified_name,
            "order_index": self.order_counter,
            "nesting_depth": len(self.component_stack),
            "start": node.lineno,
            "end": node.end_lineno,
            "hash": source_hash,
            "committed_hash": committed_hash,
            "committed_at": committed_at
        }

        self.order_counter += 1

        # 1. Write to canon_components (The Skeleton)
        self._write("""
        INSERT INTO canon_components VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            rec["component_id"], rec["file_id"], rec["parent_id"], rec["kind"],
            rec["name"], rec["qualified_name"], rec["order_index"],
            rec["nesting_depth"], rec["start"], rec["end"], rec["hash"],
            rec["committed_hash"], rec["committed_at"]
        ))

        # 2. Write to canon_source_segments (The Flesh)
        self._write("""
        INSERT INTO canon_source_segments VALUES (?,?)
        """, (rec["component_id"], segment))

        # PHASE 5: Parse and index comment directives
        try:
            comment_meta = self._extract_comment_metadata(node)
            directives = comment_meta.get("directives", [])
            
            if directives:
                # Store in overlay_semantic with source='comment_directive'
                for directive in directives:
                    payload = {
                        "directive": directive,
                        "component_name": rec["name"],
                        "qualified_name": rec["qualified_name"],
                        "kind": rec["kind"]
                    }
                    
                    self._write("""
                    INSERT INTO overlay_semantic VALUES (?,?,?,?,?,?,?)
                    """, (
                        uid(),
                        rec["component_id"],      # target_id
                        "component",              # target_type
                        "comment_directive",      # source
                        1.0,                      # confidence
                        json.dumps(payload),      # payload_json
                        datetime.datetime.utcnow().isoformat()  # created_at
                    ))
        except Exception as e:
            # Never crash extraction on comment parsing failure
            print(f"  [WARNING] Comment parsing failed for {name}: {e}")
    
        # PHASE 4: capture formatting/docstring metadata for rebuild
        try:
            self._extract_metadata(node, rec["component_id"])
        except Exception:
            pass

        return rec


    # ---------------- visitors ----------------

    def visit_Module(self, node):
        """Entry point: Treat top-level items as components to ensure Rebuild works."""
        for stmt in node.body:
            # 1. Specialized visitors: These create their own components internally
            if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                self.visit(stmt)
                continue

            # 2. Generic handling: Wrap EVERYTHING else in a component
            kind = type(stmt).__name__.lower()
            name = f"block_{kind}"

            if isinstance(stmt, (ast.Import, ast.ImportFrom)):
                kind = "import"
                # Make unique name for each import
                if isinstance(stmt, ast.Import):
                    name = f"import:{','.join(alias.name for alias in stmt.names)}"
                else:
                    name = f"import:{stmt.module or 'relative'}"
            elif isinstance(stmt, ast.Assign):
                kind = "assignment"
                try:
                    targets = [ast.unparse(t) for t in stmt.targets]
                    name = f"assign: {', '.join(targets)}"[:60]
                except:
                    name = "assignment"

            # Register as component so it exists in the rebuild
            comp = self._register_component(stmt, kind, name)
            self.component_stack.append(comp)
            
            # Visit the node to extract internal metadata (calls, symbols, etc.)
            self.visit(stmt) 
            
            self.component_stack.pop()
        
        # PHASE 2: persist collected symbols after full traversal
        try:
            self.flush_symbols()
        except Exception as e:
            print(f"Warning: Failed to flush symbols: {e}")

    def visit_FunctionDef(self, node):
        # Register function
        comp = self._register_component(node, "function", node.name)
        self.component_stack.append(comp)

        # Capture decorators as semantic overlays
        if node.decorator_list:
            cid = comp["component_id"]
            for dec in node.decorator_list:
                dec_name = ast.unparse(dec)
                self._write(
                    """
                    INSERT INTO overlay_semantic 
                    (overlay_id, target_id, target_type, source, confidence, payload_json, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        uid(),
                        cid,
                        "component",
                        "decorator",
                        1.0,
                        json.dumps({"decorator": dec_name}),
                        datetime.datetime.utcnow().isoformat(),
                    ),
                )

        # PHASE 2: Track parameters as locals with type hints
        for arg in node.args.args:
            type_hint = ast.unparse(arg.annotation) if arg.annotation else None
            self._record_variable(arg.arg, "param", node.lineno, is_param=True, type_hint=type_hint)
            self.defined_locals.add(arg.arg)
            
            # Also write to canon_symbols for legacy compatibility
            self._write("""
            INSERT INTO canon_symbols VALUES (?,?,?,?)
            """, (uid(), comp["component_id"], arg.arg, "parameter"))

        # Visit body
        self.generic_visit(node)
        
        # Cleanup
        self.defined_locals.clear()
        self.component_stack.pop()

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    def visit_ClassDef(self, node):
        comp = self._register_component(node, "class", node.name)
        self.component_stack.append(comp)
        self.generic_visit(node)
        self.component_stack.pop()

    def visit_Import(self, node):
        if not self.component_stack: 
            return
        cid = self.component_stack[-1]["component_id"]
        
        for alias in node.names:
            self._write("""
            INSERT INTO canon_imports VALUES (?,?,?,?,?)
            """, (
                uid(), cid, alias.name, None, alias.asname
            ))

    def visit_ImportFrom(self, node):
        if not self.component_stack: 
            return
        cid = self.component_stack[-1]["component_id"]

        for alias in node.names:
            self._write("""
            INSERT INTO canon_imports VALUES (?,?,?,?,?)
            """, (
                uid(), cid, node.module, alias.name, alias.asname
            ))

    def visit_Call(self, node):
        if self.component_stack:
            cid = self.component_stack[-1]["component_id"]
            try:
                target = ast.unparse(node.func)
                self._write("""
                INSERT INTO canon_calls VALUES (?,?,?,?)
                """, (
                    uid(), cid, target, node.lineno
                ))
            except:
                pass
        self.generic_visit(node)

    def visit_Assign(self, node):
        if not self.component_stack:
            return
        cid = self.component_stack[-1]["component_id"]

        for target in node.targets:
            if isinstance(target, ast.Name):
                # PHASE 2: Record variable write
                self._record_variable(target.id, "write", node.lineno)

                # If it's not a known local, it might be a global write
                if target.id not in self.defined_locals:
                    self._write(
                        """
                        INSERT INTO canon_globals VALUES (?,?,?,?)
                        """,
                        (uid(), cid, target.id, "write"),
                    )
                    self.defined_locals.add(target.id)
                else:
                    self._write(
                        """
                        INSERT INTO canon_symbols VALUES (?,?,?,?)
                        """,
                        (uid(), cid, target.id, "local"),
                    )

            elif isinstance(target, ast.Attribute):
                # Attribute assignment (e.g., self.x = 1)
                self._record_variable(target.attr, "attr_write", node.lineno)

            elif isinstance(target, ast.Subscript):
                # Subscript mutation (e.g., d['k'] = 1)
                if isinstance(target.value, ast.Name):
                    self._record_variable(target.value.id, "mutation", node.lineno)
        
        self.generic_visit(node)

    # ===== PHASE 2: SYMBOL TRACKING =====
    
    def visit_AnnAssign(self, node):
        """Capture annotated assignments with type hints."""
        if not self.component_stack:
            return
        
        if isinstance(node.target, ast.Name):
            type_hint = ast.unparse(node.annotation) if node.annotation else None
            self._record_variable(node.target.id, "write", node.lineno, type_hint=type_hint)
            
            # Store type hint in canon_types table
            if type_hint:
                cid = self._current_component_id()
                self._write("""
                INSERT INTO canon_types VALUES (?,?,?,?,?)
                """, (
                    uid(), cid, node.target.id, type_hint, "variable"
                ))
        
        self.generic_visit(node)
    
    def visit_arg(self, node):
        """Track function parameters with type annotations."""
        # Already handled in visit_FunctionDef, but can be extended here
        # if we need to capture nested function parameters
        self.generic_visit(node)
    
    def visit_Name(self, node):
        """Record variable reads/writes in context."""
        if not self.component_stack:
            return
        
        # Determine if this is a read or write based on context
        if isinstance(node.ctx, ast.Store):
            access_type = "write"
        elif isinstance(node.ctx, ast.Del):
            access_type = "delete"
        else:  # Load context
            access_type = "read"
        
        self._record_variable(node.id, access_type, node.lineno)
        self.generic_visit(node)

    def flush_symbols(self):
        """Write collected symbols to canon_variables table."""
        for cid, symbols in self.symbols_in_component.items():
            for name, (_, access_type, lineno, is_param, type_hint) in symbols.items():
                # Determine scope level
                if is_param:
                    scope_level = "parameter"
                elif name in self.defined_locals or access_type == "write":
                    scope_level = "local"
                else:
                    scope_level = "global"  # might be read from outer scope
                
                # FIX: Match 8-column schema (variable_id, component_id, name, scope_level, access_type, lineno, is_parameter, type_hint)
                self._write("""
                INSERT INTO canon_variables VALUES (?,?,?,?,?,?,?,?)
                """, (
                    uid(),                    # variable_id
                    cid,                      # component_id
                    name,                     # name
                    scope_level,              # scope_level
                    access_type,              # access_type
                    lineno,                   # lineno
                    1 if is_param else 0,     # is_parameter
                    type_hint or ""           # type_hint
                ))
        
        # Clear after flushing
        self.symbols_in_component = {}
