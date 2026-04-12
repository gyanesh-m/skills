#!/usr/bin/env python3
"""
SDK API Surface Validator (AST-based)

Uses Python's ast module for accurate extraction and validation of:
- SDK source: classes, methods with full signatures, enum members
- Markdown code examples: imports, calls with kwargs, type-inferred method resolution

Usage: python3 scripts/sdk-validation/validate.py [--skip-download]
"""

import ast
import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile
import tarfile
from pathlib import Path
from dataclasses import dataclass, field

SCRIPTS_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPTS_DIR.parent.parent
SKILLS_DIR = PROJECT_DIR / "skills"
SDK_CONFIG_PATH = SCRIPTS_DIR / "sdk-config.json"
TEMP_DIR = Path(tempfile.gettempdir()) / "sdk-api-validation-ast"
SKIP_DOWNLOAD = "--skip-download" in sys.argv

exit_code = 0
error_count = 0
warn_count = 0


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------
def error(msg):
    global exit_code, error_count
    print(f"  \u274c {msg}")
    exit_code = 1
    error_count += 1


def warn(msg):
    global warn_count
    print(f"  \u26a0\ufe0f  {msg}")
    warn_count += 1


def success(msg):
    print(f"  \u2705 {msg}")


def info(msg):
    print(f"  \u2139\ufe0f  {msg}")


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------
@dataclass
class FunctionInfo:
    name: str
    params: list  # parameter names (excluding self/cls)
    defaults_count: int = 0  # number of params with defaults


@dataclass
class ClassInfo:
    name: str
    methods: dict = field(default_factory=dict)  # method name -> FunctionInfo
    attributes: set = field(default_factory=set)  # attribute names
    bases: list = field(default_factory=list)  # base class names
    is_enum: bool = False
    enum_members: set = field(default_factory=set)


@dataclass
class SDKSurface:
    exports: set = field(default_factory=set)
    classes: dict = field(default_factory=dict)  # name -> ClassInfo
    functions: dict = field(default_factory=dict)  # name -> FunctionInfo
    submodule_attrs: dict = field(default_factory=dict)  # "pkg.sub" -> set of attr names
    # For TypeScript, we only use exports + classes (regex-based)
    ts_exports: set = field(default_factory=set)


# ---------------------------------------------------------------------------
# SDK download
# ---------------------------------------------------------------------------
def ensure_dir(p):
    Path(p).mkdir(parents=True, exist_ok=True)


def download_python_sdk(package_name, version):
    tag = f"{package_name}-py-{version}"
    dest = TEMP_DIR / tag
    if SKIP_DOWNLOAD and dest.exists():
        return dest

    ensure_dir(TEMP_DIR)
    ensure_dir(dest)

    # Build version spec: "pkg", "pkg==1.0", or "pkg>=3.0,<4.0"
    if version == "latest":
        version_spec = f'"{package_name}"'
    elif version.startswith((">=", "<=", "<", ">", "~=", "!=")):
        version_spec = f'"{package_name}{version}"'
    else:
        version_spec = f'"{package_name}=={version}"'
    prefix = package_name.replace("-", "_")

    try:
        # Try with --python-version 3.12 first
        subprocess.run(
            f'pip3 download {version_spec} --no-deps --python-version 3.12 '
            f'--only-binary :all: -d "{TEMP_DIR}" 2>/dev/null || '
            f'pip3 download {version_spec} --no-deps -d "{TEMP_DIR}" 2>/dev/null',
            shell=True, check=True, capture_output=True
        )
    except subprocess.CalledProcessError:
        warn(f"Could not download {package_name}{'==' + version if version != 'latest' else ''}")
        return None

    # Find the wheel
    whl = None
    for f in TEMP_DIR.iterdir():
        if f.name.startswith(prefix) and f.suffix == ".whl":
            if version == "latest" or version in f.name:
                whl = f
                break
    if not whl:
        for f in TEMP_DIR.iterdir():
            if f.name.startswith(prefix) and f.suffix == ".whl":
                whl = f
                break

    if not whl:
        warn(f"No wheel found for {package_name}")
        return None

    with zipfile.ZipFile(whl, "r") as z:
        z.extractall(dest)

    return dest


def download_typescript_sdk(package_name, version):
    tag = f"{package_name}-ts-{version}"
    dest = TEMP_DIR / tag
    if SKIP_DOWNLOAD and dest.exists():
        return dest

    ensure_dir(TEMP_DIR)
    ensure_dir(dest)

    try:
        result = subprocess.run(
            f'cd "{TEMP_DIR}" && npm pack "{package_name}@{version}" 2>/dev/null',
            shell=True, check=True, capture_output=True, text=True
        )
    except subprocess.CalledProcessError:
        warn(f"Could not download {package_name}@{version}")
        return None

    tgz = None
    for f in TEMP_DIR.iterdir():
        if package_name in f.name and f.suffix == ".tgz":
            tgz = f
            break

    if not tgz:
        warn(f"No tarball found for {package_name}@{version}")
        return None

    with tarfile.open(tgz, "r:gz") as t:
        t.extractall(dest)

    return dest


# ---------------------------------------------------------------------------
# AST-based Python API extraction
# ---------------------------------------------------------------------------
class SDKExtractor(ast.NodeVisitor):
    """Extract API surface from a single Python source file."""

    def __init__(self):
        self.classes = {}
        self.functions = {}
        self.top_names = set()

    def visit_ClassDef(self, node):
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(base.attr)

        is_enum = any(b in ("Enum", "StrEnum", "IntEnum") for b in bases)

        ci = ClassInfo(
            name=node.name,
            bases=bases,
            is_enum=is_enum,
        )

        for item in ast.walk(node):
            if isinstance(item, ast.FunctionDef) or isinstance(item, ast.AsyncFunctionDef):
                if item is not node:
                    params = self._extract_params(item)
                    fi = FunctionInfo(
                        name=item.name,
                        params=params,
                        defaults_count=len(item.args.defaults) + len(item.args.kw_defaults),
                    )
                    ci.methods[item.name] = fi

            # Enum members: assignments at class body level
            if is_enum and isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name) and not target.id.startswith("_"):
                        ci.enum_members.add(target.id)

            # Class attributes (from __init__ self.x = ...)
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
                        if target.value.id == "self":
                            ci.attributes.add(target.attr)

        self.classes[node.name] = ci
        # Don't recurse into class body (we already walked it)

    def visit_FunctionDef(self, node):
        # Only top-level functions (not inside a class)
        params = self._extract_params(node)
        fi = FunctionInfo(
            name=node.name,
            params=params,
            defaults_count=len(node.args.defaults) + len(node.args.kw_defaults),
        )
        self.functions[node.name] = fi

    visit_AsyncFunctionDef = visit_FunctionDef

    def _extract_params(self, func_node):
        params = []
        for arg in func_node.args.args:
            if arg.arg not in ("self", "cls"):
                params.append(arg.arg)
        for arg in func_node.args.kwonlyargs:
            params.append(arg.arg)
        if func_node.args.vararg:
            params.append(func_node.args.vararg.arg)
        if func_node.args.kwarg:
            params.append(func_node.args.kwarg.arg)
        return params


def extract_python_surface(sdk_dir):
    """Extract full API surface from a Python SDK directory."""
    surface = SDKSurface()
    sdk_path = Path(sdk_dir)

    # Find all package directories (skip .dist-info)
    pkg_dirs = [
        d for d in sdk_path.iterdir()
        if d.is_dir() and not d.name.endswith(".dist-info") and not d.name.startswith(".")
    ]

    # Track submodule-level imports for nested attribute access
    # e.g., galileo/openai/__init__.py doing `import openai` makes `openai` an attribute
    submodule_attrs = {}  # "galileo.openai" -> {"openai", ...}

    for pkg_dir in pkg_dirs:
        # Parse all __init__.py files (including sub-packages) for exports
        for init_py in pkg_dir.rglob("__init__.py"):
            rel = init_py.parent.relative_to(sdk_path)
            module_path = ".".join(rel.parts)
            try:
                tree = ast.parse(init_py.read_text(encoding="utf-8", errors="replace"))
                is_top_level = init_py.parent == pkg_dir
                for node in ast.walk(tree):
                    # from X import Y, Z
                    if isinstance(node, ast.ImportFrom):
                        for alias in node.names:
                            name = alias.asname or alias.name
                            if is_top_level:
                                surface.exports.add(name)
                            else:
                                submodule_attrs.setdefault(module_path, set()).add(name)
                    # import X — makes X an attribute of this module
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            name = alias.asname or alias.name.split(".")[-1]
                            if is_top_level:
                                surface.exports.add(name)
                            else:
                                submodule_attrs.setdefault(module_path, set()).add(name)
                    # __all__ = [...]
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name) and target.id == "__all__":
                                if isinstance(node.value, (ast.List, ast.Tuple)):
                                    for elt in node.value.elts:
                                        if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                            if is_top_level:
                                                surface.exports.add(elt.value)
                                            else:
                                                submodule_attrs.setdefault(module_path, set()).add(elt.value)
            except SyntaxError:
                pass

        # Walk all .py files for class/function definitions
        for py_file in pkg_dir.rglob("*.py"):
            try:
                tree = ast.parse(py_file.read_text(encoding="utf-8", errors="replace"))
            except SyntaxError:
                continue  # Skip files with syntax incompatible with our Python version

            extractor = SDKExtractor()
            # Only visit top-level nodes (not nested)
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    extractor.visit(node)

            # Merge into surface
            for name, ci in extractor.classes.items():
                if name not in surface.classes:
                    surface.classes[name] = ci
                else:
                    # Merge methods and attributes
                    existing = surface.classes[name]
                    existing.methods.update(ci.methods)
                    existing.attributes.update(ci.attributes)
                    existing.enum_members.update(ci.enum_members)
                    if ci.is_enum:
                        existing.is_enum = True

            for name, fi in extractor.functions.items():
                if name not in surface.functions:
                    surface.functions[name] = fi

    surface.submodule_attrs = submodule_attrs
    return surface


# ---------------------------------------------------------------------------
# TypeScript API extraction (regex-based, .d.ts files)
# ---------------------------------------------------------------------------
def extract_typescript_surface(sdk_dir):
    surface = SDKSurface()
    pkg_dir = Path(sdk_dir) / "package"
    dts_path = pkg_dir / "dist" / "index.d.ts"

    if not dts_path.exists():
        warn(f"No index.d.ts found at {dts_path}")
        return surface

    content = dts_path.read_text(encoding="utf-8", errors="replace")

    # Parse export { ... } blocks
    for m in re.finditer(r"export\s*\{([^}]+)\}", content):
        for name in m.group(1).split(","):
            clean = re.sub(r"\s+as\s+\w+", "", name).replace("type ", "").strip()
            if clean:
                surface.ts_exports.add(clean)

    # Parse import statements (internal imports show available names)
    for m in re.finditer(r"import\s+(?:\{([^}]+)\}|(\w+))\s+from\s+['\"]([^'\"]+)['\"]", content):
        names = m.group(1) or m.group(2)
        if names:
            for n in names.split(","):
                clean = n.replace("type ", "").strip()
                if clean:
                    surface.ts_exports.add(clean)

    # Walk .d.ts files for class methods
    for dts_file in (pkg_dir / "dist").rglob("*.d.ts"):
        _parse_dts_classes(dts_file, surface)

    return surface


def _parse_dts_classes(filepath, surface):
    content = filepath.read_text(encoding="utf-8", errors="replace")
    current_class = None
    current_const = None  # for `export declare const X: { ... }` objects

    for line in content.split("\n"):
        # Match `export declare const X: {` — treat as enum-like const object
        const_m = re.match(r"export\s+declare\s+const\s+(\w+)\s*:\s*\{", line)
        if const_m:
            current_const = const_m.group(1)
            if current_const not in surface.classes:
                surface.classes[current_const] = ClassInfo(name=current_const, is_enum=True)
            current_class = None
            continue

        if current_const:
            # Extract `readonly key:` entries as enum members
            key_m = re.match(r"\s+readonly\s+(\w+)\s*:", line)
            if key_m:
                surface.classes[current_const].enum_members.add(key_m.group(1))
            if re.match(r"^}", line):
                current_const = None
            continue

        class_m = re.match(r"(?:export\s+)?class\s+(\w+)", line)
        if class_m:
            current_class = class_m.group(1)
            if current_class not in surface.classes:
                surface.classes[current_class] = ClassInfo(name=current_class)

        if current_class:
            method_m = re.match(r"\s+(\w+)\s*[\(<]", line)
            if method_m and not method_m.group(1).startswith("_"):
                surface.classes[current_class].methods[method_m.group(1)] = FunctionInfo(
                    name=method_m.group(1), params=[]
                )
            prop_m = re.match(r"\s+(?:readonly\s+)?(\w+)\s*[?]?\s*:", line)
            if prop_m and not prop_m.group(1).startswith("_"):
                surface.classes[current_class].attributes.add(prop_m.group(1))

            if re.match(r"^}", line):
                current_class = None


# ---------------------------------------------------------------------------
# Markdown code block extraction
# ---------------------------------------------------------------------------
def extract_code_blocks(md_content, lang):
    """Extract code blocks for a given language from markdown."""
    pattern = re.compile(rf"```{lang}\b[^\n]*\n(.*?)```", re.DOTALL)
    return [m.group(1) for m in pattern.finditer(md_content)]


# ---------------------------------------------------------------------------
# AST-based code example validator (Python)
# ---------------------------------------------------------------------------
class CodeValidator(ast.NodeVisitor):
    """Validate Python code examples against an SDK surface with type inference."""

    def __init__(self, surface, prefix, sdk_roots=None):
        self.surface = surface
        self.prefix = prefix
        self.errors = []
        self.warnings = []
        # Type inference: variable name -> class name
        self.var_types = {}
        # Track which names were imported from galileo/promptquality
        self.sdk_imports = {}  # local name -> imported name
        # Track module aliases: `import promptquality as pq` -> pq -> promptquality
        self.module_aliases = {}  # local alias -> module root name
        # SDK roots in scope for this validation pass (e.g. {"galileo", "galileo_core"})
        # Only module aliases whose root is in this set are validated.
        self.sdk_roots = sdk_roots or {"galileo", "galileo_core", "promptquality"}

    def visit_ImportFrom(self, node):
        if not node.module:
            return
        root = node.module.split(".")[0]
        if root not in ("galileo", "galileo_core", "promptquality"):
            return

        for alias in node.names:
            name = alias.name
            local = alias.asname or name
            self.sdk_imports[local] = name

            # Check if the imported name exists:
            # 1. In top-level exports
            # 2. In submodule attrs (e.g., galileo.openai has `openai` from `import openai`)
            if not self._name_exists(name):
                # Check submodule attributes
                submod_key = node.module
                submod_attrs = self.surface.submodule_attrs.get(submod_key, set())
                if name not in submod_attrs:
                    self.errors.append(
                        f"{self.prefix}: import '{name}' from '{node.module}' not found in SDK"
                    )

    def visit_Import(self, node):
        for alias in node.names:
            root = alias.name.split(".")[0]
            if root in ("galileo", "galileo_core", "promptquality"):
                local = alias.asname or alias.name.split(".")[-1]
                self.sdk_imports[local] = alias.name
                # Track module-level aliases: `import promptquality as pq`
                if alias.asname:
                    self.module_aliases[alias.asname] = root

    def visit_Assign(self, node):
        """Track variable types: x = ClassName(...) or x = module.ClassName(...)"""
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            var_name = node.targets[0].id
            class_name = self._resolve_call_class(node.value)
            if class_name:
                self.var_types[var_name] = class_name

        self.generic_visit(node)

    def visit_Call(self, node):
        """Validate function/method calls — check kwargs exist in signature."""
        # Extract keyword argument names
        kwarg_names = [kw.arg for kw in node.keywords if kw.arg is not None]

        # Case 1: standalone function call: func(k=v)
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            imported_name = self.sdk_imports.get(func_name, func_name)
            if imported_name in self.surface.functions:
                fi = self.surface.functions[imported_name]
                self._check_kwargs(func_name, kwarg_names, fi.params)

        # Case 2: attribute call: obj.method(k=v)
        elif isinstance(node.func, ast.Attribute):
            method_name = node.func.attr
            obj = node.func.value

            # Resolve object to a class
            class_name = None
            if isinstance(obj, ast.Name):
                # Direct class/enum access: ClassName.method() or var.method()
                obj_name = obj.id
                imported = self.sdk_imports.get(obj_name, obj_name)

                if imported in self.surface.classes:
                    class_name = imported
                elif obj_name in self.var_types:
                    class_name = self.var_types[obj_name]

            if class_name and class_name in self.surface.classes:
                ci = self.surface.classes[class_name]

                # Check enum member access
                if ci.is_enum and not self._class_has_enum_member(class_name, method_name):
                    pass  # Handled in visit_Attribute

                # Check method exists (with inheritance)
                if self._class_has_method(class_name, method_name):
                    params = self._get_method_params(class_name, method_name)
                    if params is not None:
                        self._check_kwargs(f"{class_name}.{method_name}", kwarg_names, params)
                elif kwarg_names and not ci.is_enum:
                    self.warnings.append(
                        f"{self.prefix}: '{class_name}.{method_name}()' — method not found on class (checked bases: {ci.bases})"
                    )
            elif isinstance(obj, ast.Name) and obj.id in self.module_aliases:
                # Module alias call: pq.something() — only validate when the aliased
                # module belongs to the SDK currently being tested. This prevents
                # false positives when a file shows legacy pq.* examples alongside
                # galileo 2.x code (or vice versa).
                alias_name = obj.id
                alias_root = self.module_aliases[alias_name]
                if alias_root in self.sdk_roots:
                    if method_name not in self.surface.exports and method_name not in self.surface.classes:
                        self.errors.append(
                            f"{self.prefix}: '{alias_name}.{method_name}()' — '{method_name}' not found in SDK exports"
                        )

        self.generic_visit(node)

    def visit_Attribute(self, node):
        """Validate attribute access: Enum.member, Class.attr"""
        if isinstance(node.value, ast.Name):
            obj_name = node.value.id
            attr_name = node.attr
            imported = self.sdk_imports.get(obj_name, obj_name)

            # Check enum member access (with inheritance)
            if imported in self.surface.classes:
                ci = self.surface.classes[imported]
                if ci.is_enum and not self._class_has_enum_member(imported, attr_name):
                    self.errors.append(
                        f"{self.prefix}: '{imported}.{attr_name}' — "
                        f"member '{attr_name}' not found in enum '{imported}'"
                    )

            # Check instance attribute/method on typed variables (with inheritance)
            elif obj_name in self.var_types:
                class_name = self.var_types[obj_name]
                if class_name in self.surface.classes:
                    if (
                        not self._class_has_method(class_name, attr_name)
                        and not attr_name.startswith("_")
                    ):
                        self.warnings.append(
                            f"{self.prefix}: '{obj_name}.{attr_name}' — "
                            f"attr/method '{attr_name}' not found on {class_name}"
                        )

        self.generic_visit(node)

    def visit_Decorator(self, node):
        pass  # Handled via FunctionDef

    def visit_FunctionDef(self, node):
        """Check decorators."""
        for deco in node.decorator_list:
            if isinstance(deco, ast.Name):
                name = self.sdk_imports.get(deco.id, deco.id)
                if name in self.sdk_imports.values() and not self._name_exists(name):
                    self.errors.append(
                        f"{self.prefix}: decorator '@{name}' not found in SDK"
                    )
            elif isinstance(deco, ast.Call) and isinstance(deco.func, ast.Name):
                name = self.sdk_imports.get(deco.func.id, deco.func.id)
                if name in self.sdk_imports.values() and not self._name_exists(name):
                    self.errors.append(
                        f"{self.prefix}: decorator '@{name}' not found in SDK"
                    )
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def _name_exists(self, name):
        return (
            name in self.surface.exports
            or name in self.surface.classes
            or name in self.surface.functions
        )

    def _class_has_method(self, class_name, method_name, visited=None):
        """Check if a class or any of its bases has the given method (MRO resolution)."""
        if visited is None:
            visited = set()
        if class_name in visited:
            return False
        visited.add(class_name)

        ci = self.surface.classes.get(class_name)
        if not ci:
            return False
        if method_name in ci.methods or method_name in ci.attributes:
            return True
        # Check base classes
        for base in ci.bases:
            if self._class_has_method(base, method_name, visited):
                return True
        return False

    def _class_has_enum_member(self, class_name, member_name, visited=None):
        """Check if an enum class or any of its bases has the given member."""
        if visited is None:
            visited = set()
        if class_name in visited:
            return False
        visited.add(class_name)

        ci = self.surface.classes.get(class_name)
        if not ci:
            return False
        if member_name in ci.enum_members:
            return True
        for base in ci.bases:
            if self._class_has_enum_member(base, member_name, visited):
                return True
        return False

    def _get_method_params(self, class_name, method_name, visited=None):
        """Get method params resolving through inheritance."""
        if visited is None:
            visited = set()
        if class_name in visited:
            return None
        visited.add(class_name)

        ci = self.surface.classes.get(class_name)
        if not ci:
            return None
        if method_name in ci.methods:
            return ci.methods[method_name].params
        for base in ci.bases:
            result = self._get_method_params(base, method_name, visited)
            if result is not None:
                return result
        return None

    def _resolve_call_class(self, node):
        """Try to resolve a Call node to a class name."""
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                name = self.sdk_imports.get(node.func.id, node.func.id)
                if name in self.surface.classes:
                    return name
            elif isinstance(node.func, ast.Attribute):
                # module.ClassName()
                return self.sdk_imports.get(node.func.attr, node.func.attr)
        return None

    def _check_kwargs(self, call_name, kwarg_names, valid_params):
        """Check that keyword arguments exist in the function signature."""
        if not kwarg_names or not valid_params:
            return
        for kw in kwarg_names:
            if kw not in valid_params:
                # Check if there's a **kwargs parameter (any param starting with nothing special)
                # If the function has **kwargs, all keyword args are valid
                has_kwargs_catch_all = any(p.startswith("kwargs") or p == "kwargs" for p in valid_params)
                if not has_kwargs_catch_all:
                    self.errors.append(
                        f"{self.prefix}: '{call_name}({kw}=...)' — "
                        f"parameter '{kw}' not found in signature (valid: {', '.join(valid_params)})"
                    )


# ---------------------------------------------------------------------------
# TypeScript code validator (regex-based since we can't ast-parse TS)
# ---------------------------------------------------------------------------
def validate_typescript_refs(blocks, surface, prefix):
    """Validate TypeScript code blocks against the SDK surface."""
    errors = []
    all_exports = surface.ts_exports | set(surface.classes.keys())

    for block in blocks:
        # import { X, Y } from "galileo"
        for m in re.finditer(r'import\s+\{([^}]+)\}\s+from\s+["\']galileo["\']', block):
            for name in m.group(1).split(","):
                clean = re.sub(r"\s+as\s+\w+", "", name).strip()
                if clean and clean not in all_exports:
                    errors.append(
                        f"{prefix}: import '{clean}' from 'galileo' not found in SDK exports"
                    )

        # String metric names in arrays: metrics: ["x", "y"]
        for m in re.finditer(r'metrics\s*:\s*\[([^\]]+)\]', block):
            inner = m.group(1)
            for sm in re.finditer(r'["\'](\w+)["\']', inner):
                metric_name = sm.group(1)
                # Check against known metric strings from GalileoMetrics enum
                if "GalileoMetrics" in surface.classes:
                    ci = surface.classes["GalileoMetrics"]
                    # TS metrics use snake_case strings matching Python enum member names
                    valid = {attr for attr in ci.attributes} | set(ci.enum_members)
                    if valid and metric_name not in valid:
                        errors.append(
                            f"{prefix}: metric string '{metric_name}' not found in GalileoMetrics"
                        )

    return errors


# ---------------------------------------------------------------------------
# Skill configuration — loaded from sdk-config.json
# ---------------------------------------------------------------------------
def load_sdk_config():
    if not SDK_CONFIG_PATH.exists():
        print(f"  Error: {SDK_CONFIG_PATH} not found")
        sys.exit(1)
    return json.loads(SDK_CONFIG_PATH.read_text())


# ---------------------------------------------------------------------------
# Frontmatter parser
# ---------------------------------------------------------------------------
def parse_frontmatter(content):
    m = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not m:
        return {}
    fm = {}
    current = fm
    for line in m.group(1).split("\n"):
        kv = re.match(r"^(\s*)([\w-]+):\s*(.*)", line)
        if not kv:
            continue
        key = kv.group(2)
        val = kv.group(3).strip().strip("\"'")
        if not val:
            fm[key] = {}
        else:
            # Handle nested (metadata.sdk-version)
            current[key] = val
    # Simple nested: parse metadata block
    metadata = {}
    in_meta = False
    for line in m.group(1).split("\n"):
        if re.match(r"^metadata:\s*$", line):
            in_meta = True
            continue
        if in_meta:
            kv = re.match(r"^\s+([\w-]+):\s*(.*)", line)
            if kv:
                metadata[kv.group(1)] = kv.group(2).strip().strip("\"'")
            else:
                in_meta = False
    fm["metadata"] = metadata
    return fm


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    global exit_code

    print("\n  SDK Validation\n")

    ensure_dir(TEMP_DIR)

    sdk_config = load_sdk_config()

    manifest_path = PROJECT_DIR / "skills.json"
    manifest = json.loads(manifest_path.read_text())

    for skill in manifest["skills"]:
        config = sdk_config.get(skill["name"])
        if not config:
            info(f"{skill['name']}: no SDK mapping — skipping")
            continue

        skill_dir = SKILLS_DIR / skill["name"]
        skill_md = (skill_dir / "SKILL.md").read_text()
        fm = parse_frontmatter(skill_md)
        sdk_version = fm.get("metadata", {}).get("sdk-version")

        if not sdk_version or sdk_version == "latest":
            warn(f"{skill['name']}: sdk-version is '{sdk_version or 'missing'}' — cannot validate")
            continue

        success(f"{skill['name']}: sdk-version = {sdk_version}")

        for pkg in config["packages"]:
            version = pkg.get("version", sdk_version)
            pkg_label = f"{pkg['name']}@{version}"

            print(f"\n  --- {skill['name']} / {pkg_label} ---\n")

            # Download
            if config["language"] == "python":
                sdk_dir = download_python_sdk(pkg["name"], version)
            else:
                sdk_dir = download_typescript_sdk(pkg["name"], version)

            if not sdk_dir:
                warn(f"Skipping {pkg_label} — download failed")
                continue

            success(f"{pkg_label}: downloaded")

            # Extract API surface
            if config["language"] == "python":
                surface = extract_python_surface(sdk_dir)

                # Merge dependencies (with version-pinned galileo-core)
                for dep in pkg.get("deps", []):
                    if isinstance(dep, str):
                        dep_name, dep_version = dep, "latest"
                    else:
                        dep_name = dep["name"]
                        dep_version = dep.get("version_range", "latest")
                    dep_dir = download_python_sdk(dep_name, dep_version)
                    if dep_dir:
                        dep_surface = extract_python_surface(dep_dir)
                        surface.exports.update(dep_surface.exports)
                        for k, v in dep_surface.classes.items():
                            if k not in surface.classes:
                                surface.classes[k] = v
                            else:
                                surface.classes[k].methods.update(v.methods)
                                surface.classes[k].attributes.update(v.attributes)
                                surface.classes[k].enum_members.update(v.enum_members)
                                if v.is_enum:
                                    surface.classes[k].is_enum = True
                        for k, v in dep_surface.functions.items():
                            if k not in surface.functions:
                                surface.functions[k] = v
                        for k, v in dep_surface.submodule_attrs.items():
                            surface.submodule_attrs.setdefault(k, set()).update(v)
                        success(f"{dep_name}: dependency merged")
            else:
                surface = extract_typescript_surface(sdk_dir)

            enum_count = sum(1 for c in surface.classes.values() if c.is_enum)
            func_count = len(surface.functions)
            cls_count = len(surface.classes)
            success(
                f"{pkg_label}: {cls_count} classes ({enum_count} enums), "
                f"{func_count} functions, {len(surface.exports or surface.ts_exports)} exports"
            )

            # Validate each markdown file
            for rel_file in pkg["files"]:
                md_path = skill_dir / rel_file
                if not md_path.exists():
                    warn(f"{skill['name']}: {rel_file} not found")
                    continue

                md_content = md_path.read_text()

                if config["language"] == "python":
                    blocks = extract_code_blocks(md_content, "python")
                    if not blocks:
                        info(f"{skill['name']} [{rel_file}]: no python code blocks")
                        continue

                    block_errors = 0
                    block_warnings = 0
                    for i, block in enumerate(blocks):
                        try:
                            tree = ast.parse(block)
                        except SyntaxError as e:
                            warn(f"{skill['name']} [{rel_file}] block {i+1}: SyntaxError — {e.msg}")
                            continue

                        # Scope alias validation to this package's module roots only.
                        # e.g. when validating against galileo@2.x, skip pq.* calls.
                        pkg_name = pkg["name"]
                        if pkg_name == "galileo":
                            sdk_roots = {"galileo", "galileo_core"}
                        elif pkg_name == "promptquality":
                            sdk_roots = {"promptquality"}
                        else:
                            sdk_roots = {pkg_name.replace("-", "_")}
                        validator = CodeValidator(surface, f"{skill['name']} [{rel_file}]", sdk_roots=sdk_roots)
                        validator.visit(tree)

                        for err in validator.errors:
                            error(err)
                            block_errors += 1
                        for w in validator.warnings:
                            warn(w)
                            block_warnings += 1

                    success(
                        f"{skill['name']} [{rel_file}]: {len(blocks)} block(s), "
                        f"{block_errors} error(s), {block_warnings} warning(s)"
                    )

                else:
                    blocks = (
                        extract_code_blocks(md_content, "typescript")
                        + extract_code_blocks(md_content, "javascript")
                        + extract_code_blocks(md_content, "ts")
                        + extract_code_blocks(md_content, "js")
                    )
                    if not blocks:
                        info(f"{skill['name']} [{rel_file}]: no TS/JS code blocks")
                        continue

                    ts_errors = validate_typescript_refs(
                        blocks, surface, f"{skill['name']} [{rel_file}]"
                    )
                    for err in ts_errors:
                        error(err)

                    success(
                        f"{skill['name']} [{rel_file}]: {len(blocks)} block(s), "
                        f"{len(ts_errors)} error(s)"
                    )

    print(f"\n  {'─' * 35}")
    if exit_code == 0:
        print(f"  All checks passed! ({warn_count} warning(s))\n")
    else:
        print(f"  {error_count} error(s), {warn_count} warning(s)\n")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
