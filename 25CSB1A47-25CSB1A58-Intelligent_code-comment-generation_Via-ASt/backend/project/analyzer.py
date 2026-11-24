"""Project Understanding and Architecture Intelligence Engine.

Analyzes multi-file Python projects:
- Python module and package discovery
- AST-driven import dependency graph (internal vs stdlib vs external)
- Circular import detection and unused import detection
- Cross-file symbol references and class inheritance hierarchies
- Entry-point discovery (CLI, __main__, web frameworks, pyproject scripts)
- Configuration detection (pyproject.toml, requirements.txt, setup.py, pytest.ini)
- README inspection and automated architecture report generation
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

from backend.project.workspace import ProjectWorkspace

# Standard library module names in modern Python
STDLIB_MODULES: Set[str] = set(sys.builtin_module_names).union({
    "abc", "argparse", "ast", "asyncio", "base64", "collections", "concurrent",
    "contextlib", "copy", "csv", "ctypes", "dataclasses", "datetime", "difflib",
    "dis", "email", "enum", "errno", "functools", "glob", "gzip", "hashlib",
    "hmac", "html", "http", "importlib", "inspect", "io", "ipaddress", "itertools",
    "json", "logging", "math", "multiprocessing", "operator", "os", "pathlib",
    "pickle", "platform", "pprint", "queue", "random", "re", "secrets", "select",
    "shlex", "shutil", "signal", "socket", "sqlite3", "ssl", "stat", "string",
    "subprocess", "sys", "tarfile", "tempfile", "threading", "time", "tokenize",
    "traceback", "types", "typing", "unittest", "urllib", "uuid", "warnings",
    "weakref", "xml", "zipfile", "zlib",
})


def _path_to_module_name(rel_path: str) -> str:
    """Convert a relative POSIX file path to a canonical dotted Python module name."""
    clean = rel_path.replace("\\", "/").rstrip("/")
    if clean.endswith(".py"):
        clean = clean[:-3]
    if clean.endswith("/__init__"):
        clean = clean[:-9]
    return clean.replace("/", ".")


class ProjectAnalyzer:
    """Orchestrates comprehensive AST project analysis across multiple files."""

    def __init__(self, workspace: ProjectWorkspace) -> None:
        self.workspace = workspace

    def discover_modules(self) -> Dict[str, Any]:
        """Discover all Python packages, modules, scripts, and tests in the workspace."""
        py_files = self.workspace.list_python_files()
        modules: Dict[str, Dict[str, Any]] = {}
        packages: Set[str] = set()

        for file_path in py_files:
            mod_name = _path_to_module_name(file_path)
            is_init = file_path.endswith("__init__.py")
            is_test = (
                "/test" in file_path
                or file_path.startswith("test")
                or Path(file_path).name.startswith("test_")
                or Path(file_path).name.endswith("_test.py")
            )
            if is_init:
                pkg_dir = Path(file_path).parent.as_posix()
                packages.add(pkg_dir)

            modules[mod_name] = {
                "file_path": file_path,
                "module_name": mod_name,
                "is_package_root": is_init,
                "is_test": is_test,
                "file_size": 0,
                "line_count": 0,
            }

            try:
                content = self.workspace.read_file(file_path)
                modules[mod_name]["file_size"] = len(content)
                modules[mod_name]["line_count"] = len(content.splitlines())
            except OSError:
                pass

        return {
            "total_modules": len(modules),
            "packages_count": len(packages),
            "packages": sorted(list(packages)),
            "modules": modules,
        }

    def build_dependency_graph(self) -> Dict[str, Any]:
        """Extract import dependency graph, distinguishing internal, third-party, and stdlib."""
        modules_info = self.discover_modules()["modules"]
        known_modules = set(modules_info.keys())
        known_roots = {m.split(".")[0] for m in known_modules}

        internal_deps: Dict[str, Set[str]] = {m: set() for m in known_modules}
        external_deps: Set[str] = set()
        stdlib_deps: Set[str] = set()
        unused_imports_by_file: Dict[str, List[str]] = {}

        for mod_name, meta in modules_info.items():
            file_path = meta["file_path"]
            try:
                source = self.workspace.read_file(file_path)
                tree = ast.parse(source)
            except (OSError, SyntaxError):
                continue

            imported_names: Set[str] = set()
            imported_aliases: Dict[str, ast.AST] = {}

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        base = alias.name.split(".")[0]
                        imported_names.add(alias.asname or alias.name)
                        imported_aliases[alias.asname or alias.name] = node
                        if base in STDLIB_MODULES:
                            stdlib_deps.add(base)
                        elif base in known_roots or alias.name in known_modules:
                            internal_deps[mod_name].add(alias.name)
                        else:
                            external_deps.add(base)

                elif isinstance(node, ast.ImportFrom):
                    level = node.level
                    if level > 0:
                        # Relative import
                        pkg_parts = mod_name.split(".")
                        base_parts = pkg_parts[:-level] if level <= len(pkg_parts) else []
                        target = ".".join(base_parts + ([node.module] if node.module else []))
                        if target in known_modules:
                            internal_deps[mod_name].add(target)
                        for alias in node.names:
                            imported_names.add(alias.asname or alias.name)
                    elif node.module:
                        base = node.module.split(".")[0]
                        for alias in node.names:
                            imported_names.add(alias.asname or alias.name)
                        if base in STDLIB_MODULES:
                            stdlib_deps.add(base)
                        elif base in known_roots or node.module in known_modules:
                            internal_deps[mod_name].add(node.module)
                        else:
                            external_deps.add(base)

            # Unused imports check: find imported aliases never used in Load contexts
            used_names = {
                n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)
            }
            unused = [name for name in imported_names if name not in used_names and not name.startswith("_")]
            if unused and not meta["is_package_root"]:
                unused_imports_by_file[file_path] = sorted(unused)

        # Detect circular dependencies in internal graph via Tarjan / DFS
        circular_dependencies: List[List[str]] = []
        visited: Dict[str, int] = {}  # 0=unvisited, 1=visiting, 2=visited
        path: List[str] = []

        def dfs(curr: str):
            visited[curr] = 1
            path.append(curr)
            for neighbor in internal_deps.get(curr, []):
                # Only check direct internal targets
                matching_internal = [m for m in known_modules if m == neighbor or m.startswith(neighbor + ".")]
                for target_mod in matching_internal:
                    if visited.get(target_mod) == 1:
                        # Found cycle
                        cycle_idx = path.index(target_mod)
                        circular_dependencies.append(path[cycle_idx:] + [target_mod])
                    elif visited.get(target_mod, 0) == 0:
                        dfs(target_mod)
            path.pop()
            visited[curr] = 2

        for mod in known_modules:
            if visited.get(mod, 0) == 0:
                dfs(mod)

        return {
            "internal_dependency_graph": {k: sorted(list(v)) for k, v in internal_deps.items()},
            "circular_dependencies": circular_dependencies,
            "has_circular_dependencies": bool(circular_dependencies),
            "external_dependencies": sorted(list(external_deps)),
            "stdlib_dependencies": sorted(list(stdlib_deps)),
            "unused_imports": unused_imports_by_file,
        }

    def analyze_cross_file_symbols(self) -> Dict[str, Any]:
        """Map definitions, cross-file references, and inheritance hierarchies."""
        modules_info = self.discover_modules()["modules"]
        symbol_definitions: Dict[str, List[Dict[str, Any]]] = {}
        class_hierarchy: Dict[str, Dict[str, Any]] = {}
        all_functions: List[Dict[str, Any]] = []

        for mod_name, meta in modules_info.items():
            file_path = meta["file_path"]
            try:
                tree = ast.parse(self.workspace.read_file(file_path))
            except (OSError, SyntaxError):
                continue

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    fn_info = {
                        "name": node.name,
                        "module": mod_name,
                        "file_path": file_path,
                        "line": node.lineno,
                        "params": [a.arg for a in node.args.args],
                        "has_docstring": ast.get_docstring(node) is not None,
                    }
                    all_functions.append(fn_info)
                    symbol_definitions.setdefault(node.name, []).append({
                        "kind": "function",
                        "module": mod_name,
                        "file": file_path,
                        "line": node.lineno,
                    })

                elif isinstance(node, ast.ClassDef):
                    bases = [ast.unparse(b).strip() for b in node.bases]
                    methods = [
                        item.name for item in node.body if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                    ]
                    class_hierarchy[f"{mod_name}.{node.name}"] = {
                        "name": node.name,
                        "module": mod_name,
                        "file_path": file_path,
                        "line": node.lineno,
                        "bases": bases,
                        "methods": methods,
                        "has_docstring": ast.get_docstring(node) is not None,
                    }
                    symbol_definitions.setdefault(node.name, []).append({
                        "kind": "class",
                        "module": mod_name,
                        "file": file_path,
                        "line": node.lineno,
                    })

        return {
            "total_functions_discovered": len(all_functions),
            "total_classes_discovered": len(class_hierarchy),
            "symbol_definitions": symbol_definitions,
            "class_hierarchy": class_hierarchy,
        }

    def discover_entry_points(self) -> List[Dict[str, Any]]:
        """Identify execution entry points across all files in the project."""
        entry_points: List[Dict[str, Any]] = []
        modules_info = self.discover_modules()["modules"]

        for mod_name, meta in modules_info.items():
            file_path = meta["file_path"]
            try:
                source = self.workspace.read_file(file_path)
                tree = ast.parse(source)
            except (OSError, SyntaxError):
                continue

            for node in ast.walk(tree):
                # 1. if __name__ == '__main__':
                if isinstance(node, ast.If):
                    test_str = ast.unparse(node.test).strip()
                    if '__name__' in test_str and '__main__' in test_str:
                        entry_points.append({
                            "type": "main_block",
                            "module": mod_name,
                            "file_path": file_path,
                            "line": node.lineno,
                            "title": f"Script Entry Point (__main__) in {file_path}",
                        })

                # 2. Web framework applications (Flask, FastAPI)
                elif isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                    var_name = node.targets[0].id
                    if var_name in {"app", "application"} and isinstance(node.value, ast.Call):
                        call_name = ast.unparse(node.value.func).lower()
                        if "flask" in call_name or "fastapi" in call_name or "django" in call_name:
                            entry_points.append({
                                "type": "web_application",
                                "module": mod_name,
                                "file_path": file_path,
                                "line": node.lineno,
                                "title": f"Web Application Instance '{var_name}' ({call_name}) in {file_path}",
                            })

        # 3. Check pyproject.toml / setup.py for console scripts
        for config_name in ("pyproject.toml", "setup.py", "setup.cfg"):
            try:
                cfg_content = self.workspace.read_file(config_name)
                for line in cfg_content.splitlines():
                    if "=" in line and ("scripts" in line.lower() or "console_scripts" in line.lower()):
                        entry_points.append({
                            "type": "console_script",
                            "file_path": config_name,
                            "line": 1,
                            "title": f"Configured Console Script: {line.strip()}",
                        })
            except (OSError, FileNotFoundError):
                pass

        return entry_points

    def detect_project_configurations(self) -> Dict[str, Any]:
        """Detect and parse configuration files in the project workspace."""
        configs: Dict[str, Any] = {}
        all_files = set(self.workspace.list_files())

        config_names = [
            "pyproject.toml",
            "requirements.txt",
            "setup.py",
            "setup.cfg",
            "Pipfile",
            "pytest.ini",
            "tox.ini",
            ".flake8",
            "ruff.toml",
            ".env.example",
        ]

        for name in config_names:
            if name in all_files:
                try:
                    content = self.workspace.read_file(name)
                    configs[name] = {
                        "present": True,
                        "file_path": name,
                        "size_bytes": len(content),
                        "snippet": content[:300] + ("..." if len(content) > 300 else ""),
                    }
                except OSError:
                    pass

        return {
            "configurations_found": list(configs.keys()),
            "details": configs,
        }

    def analyze_readme(self) -> Dict[str, Any]:
        """Inspect and extract structure from project README documentation."""
        for readme_candidate in ("README.md", "README.rst", "README.txt", "readme.md"):
            try:
                content = self.workspace.read_file(readme_candidate)
                lines = content.splitlines()
                title = lines[0].lstrip("#").strip() if lines else "Untitled Project"
                has_install = any("install" in line.lower() for line in lines)
                has_usage = any("usage" in line.lower() or "quickstart" in line.lower() for line in lines)
                has_testing = any("test" in line.lower() for line in lines)
                return {
                    "found": True,
                    "file_path": readme_candidate,
                    "title": title,
                    "line_count": len(lines),
                    "has_installation_instructions": has_install,
                    "has_usage_instructions": has_usage,
                    "has_testing_instructions": has_testing,
                    "excerpt": "\n".join(lines[:15]),
                }
            except (OSError, FileNotFoundError):
                continue

        return {"found": False, "title": "No README found"}

    def generate_project_architecture_report(self) -> Dict[str, Any]:
        """Consolidate project discovery, dependency graph, entry points, and configs."""
        modules_res = self.discover_modules()
        deps_res = self.build_dependency_graph()
        symbols_res = self.analyze_cross_file_symbols()
        entry_points = self.discover_entry_points()
        configs = self.detect_project_configurations()
        readme = self.analyze_readme()

        total_loc = sum(m["line_count"] for m in modules_res["modules"].values())

        # Determine architecture classification
        has_web = any(ep["type"] == "web_application" for ep in entry_points)
        is_pkg = modules_res["packages_count"] > 0
        arch_type = (
            "Web Application Service" if has_web
            else "Reusable Python Package" if is_pkg
            else "Python Script/CLI Application"
        )

        return {
            "architecture_type": arch_type,
            "total_python_files": len(modules_res["modules"]),
            "total_lines_of_code": total_loc,
            "total_packages": modules_res["packages_count"],
            "total_classes": symbols_res["total_classes_discovered"],
            "total_functions": symbols_res["total_functions_discovered"],
            "modules": modules_res["modules"],
            "entry_points": entry_points,
            "dependencies": deps_res,
            "configurations": configs,
            "readme": readme,
            "cross_file_symbols": symbols_res["symbol_definitions"],
            "class_hierarchy": symbols_res["class_hierarchy"],
        }
