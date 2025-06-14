"""
Extract Functions Link
=====================

ModuLink link that extracts function metadata from Python files.
Extracts the function parsing logic from MagicConverter._scan_python_file().

Input Context:
- python_files: List of Python file paths to analyze
- source_path: Root source path for relative path calculation
- verbose: Optional boolean for verbose logging

Output Context:
- discovered_functions: Dict of function metadata keyed by qualified name
- extraction_summary: Statistics about function extraction
- extraction_success: Boolean indicating successful extraction
"""

import ast
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

async def extract_functions_link(ctx: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract function metadata from Python files using AST parsing.

    This link extracts the function parsing logic from the original
    MagicConverter._scan_python_file() method.

    Args:
        ctx: ModuLink context containing Python files to analyze

    Returns:
        ctx: Updated context with discovered functions and extraction results

    Context Requirements:
        - python_files (List[Path]): Python files to analyze
        - source_path (str|Path): Root source path for relative paths

    Context Outputs:
        - discovered_functions (Dict): Function metadata by qualified name
        - extraction_summary (Dict): Statistics about extraction
        - extraction_success (bool): Whether extraction succeeded
    """

    # Check for existing errors
    if ctx.get('errors'):
        return ctx

    # Extract required context
    python_files = ctx.get('python_files', [])
    source_path = ctx.get('source_path')
    if not source_path:
        ctx.setdefault('errors', []).append({
            'type': 'missing_context',
            'link': 'extract_functions_link',
            'message': 'Missing required context key: source_path'
        })
        ctx['extraction_success'] = False
        return ctx

    source_path = Path(source_path).resolve()
    verbose = ctx.get('verbose', False)
    console = Console() if RICH_AVAILABLE else None

    try:
        discovered_functions = {}
        total_functions = 0
        files_processed = 0
        files_with_errors = 0

        if verbose and RICH_AVAILABLE:
            console.print(f"[cyan]🔍 Extracting functions from {len(python_files)} files...[/]")
        elif verbose:
            print(f"🔍 Extracting functions from {len(python_files)} files...")

        # Process files with progress tracking
        if RICH_AVAILABLE and len(python_files) > 5:
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                         BarColumn(), TaskProgressColumn(), console=console) as progress:
                task = progress.add_task("Extracting functions...", total=len(python_files))

                for py_file in python_files:
                    progress.update(task, description=f"Processing {py_file.name}")
                    file_functions = await _extract_functions_from_file(py_file, source_path, verbose)

                    if file_functions is not None:
                        discovered_functions.update(file_functions)
                        total_functions += len(file_functions)
                        files_processed += 1
                    else:
                        files_with_errors += 1

                    progress.advance(task)
        else:
            # Process without progress bar for smaller sets
            for i, py_file in enumerate(python_files):
                if verbose:
                    print(f"  Processing {py_file.name} ({i+1}/{len(python_files)})")

                file_functions = await _extract_functions_from_file(py_file, source_path, verbose)

                if file_functions is not None:
                    discovered_functions.update(file_functions)
                    total_functions += len(file_functions)
                    files_processed += 1
                else:
                    files_with_errors += 1

        # Create extraction summary
        extraction_summary = {
            'total_files_processed': files_processed,
            'files_with_errors': files_with_errors,
            'total_functions_discovered': total_functions,
            'functions_per_file_avg': total_functions / max(files_processed, 1)
        }

        # Add results to context
        ctx['discovered_functions'] = discovered_functions
        ctx['extraction_summary'] = extraction_summary
        ctx['extraction_success'] = True

        # Log completion
        if verbose and RICH_AVAILABLE:
            console.print(f"[green]✅ Extracted {total_functions} functions from {files_processed} files[/]")
            if files_with_errors > 0:
                console.print(f"[yellow]⚠️  {files_with_errors} files had parsing errors[/]")
        elif verbose:
            print(f"✅ Extracted {total_functions} functions from {files_processed} files")
            if files_with_errors > 0:
                print(f"⚠️  {files_with_errors} files had parsing errors")

    except Exception as e:
        ctx.setdefault('errors', []).append({
            'type': 'extraction_error',
            'link': 'extract_functions_link',
            'message': f'Failed to extract functions: {str(e)}'
        })
        ctx['extraction_success'] = False

    return ctx

async def _extract_functions_from_file(file_path: Path, source_path: Path, verbose: bool = False) -> Optional[Dict[str, Dict]]:
    """
    Extract function metadata from a single Python file.
    Extracted from original MagicConverter._scan_python_file().
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            source = f.read()

        tree = ast.parse(source)
        file_functions = {}

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if _should_include_function(node, file_path):
                    func_info = _extract_function_info(node, file_path, source_path, source)
                    file_functions[func_info['qualified_name']] = func_info

        return file_functions

    except Exception as e:
        if verbose:
            print(f"⚠️  Error parsing {file_path}: {e}")
        return None

def _should_include_function(node: ast.FunctionDef, file_path: Path) -> bool:
    """
    Determine if a function should be included in extraction.
    Extracted from original MagicConverter._should_include_function().
    """
    # Skip private functions (unless specifically important)
    if node.name.startswith('_') and not node.name.startswith('__'):
        return False

    # Skip if in __pycache__ or similar (should already be filtered at file level)
    if '__pycache__' in str(file_path):
        return False

    # Skip setup/config functions
    config_names = {'setup', 'configure', 'main', '__main__'}
    if node.name in config_names and len(node.args.args) == 0:
        return False

    return True

def _extract_function_info(node: ast.FunctionDef, file_path: Path, source_path: Path, source: str) -> Dict:
    """
    Extract comprehensive function information.
    Extracted from original MagicConverter._extract_function_info().
    """
    relative_path = file_path.relative_to(source_path)
    module_path = str(relative_path).replace('/', '.').replace('\\', '.').replace('.py', '')
    qualified_name = f"{module_path}.{node.name}"

    return {
        'name': node.name,
        'qualified_name': qualified_name,
        'file_path': file_path,
        'module_path': module_path,
        'is_async': isinstance(node, ast.AsyncFunctionDef),
        'args': [arg.arg for arg in node.args.args],
        'defaults': len(node.args.defaults),
        'docstring': ast.get_docstring(node) or "",
        'returns': _extract_return_type(node),
        'type_hints': _extract_type_hints(node),
        'complexity': _analyze_complexity(node),
        'domain': _detect_domain(node),
        'dependencies': _extract_dependencies(node),
        'source_lines': (node.lineno, node.end_lineno) if hasattr(node, 'end_lineno') else (node.lineno, node.lineno + 10)
    }

def _extract_return_type(node: ast.FunctionDef) -> Optional[str]:
    """Extract return type annotation if present."""
    if node.returns:
        try:
            return ast.unparse(node.returns)
        except:
            return None
    return None

def _extract_type_hints(node: ast.FunctionDef) -> Dict[str, str]:
    """Extract type hints for function parameters."""
    hints = {}
    for arg in node.args.args:
        if arg.annotation:
            try:
                hints[arg.arg] = ast.unparse(arg.annotation)
            except:
                hints[arg.arg] = "Any"
    return hints

def _analyze_complexity(node: ast.FunctionDef) -> Dict[str, int]:
    """Analyze function complexity for test generation."""
    complexity = {
        'conditions': 0,
        'loops': 0,
        'try_except': 0,
        'function_calls': 0,
        'returns': 0
    }

    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.IfExp)):
            complexity['conditions'] += 1
        elif isinstance(child, (ast.For, ast.While, ast.ListComp, ast.DictComp)):
            complexity['loops'] += 1
        elif isinstance(child, (ast.Try, ast.ExceptHandler)):
            complexity['try_except'] += 1
        elif isinstance(child, ast.Call):
            complexity['function_calls'] += 1
        elif isinstance(child, ast.Return):
            complexity['returns'] += 1

    return complexity

def _detect_domain(node: ast.FunctionDef) -> str:
    """Detect the domain/category of the function."""
    name = node.name.lower()
    docstring = (ast.get_docstring(node) or "").lower()
    combined = f"{name} {docstring}"

    # ML/Data Science patterns
    if any(term in combined for term in ['train', 'model', 'predict', 'accuracy', 'dataset', 'feature']):
        return 'ml'

    # Data processing patterns
    if any(term in combined for term in ['process', 'transform', 'filter', 'clean', 'parse', 'data']):
        return 'data_processing'

    # API/Web patterns
    if any(term in combined for term in ['api', 'request', 'response', 'http', 'url', 'endpoint']):
        return 'api'

    # File operations
    if any(term in combined for term in ['file', 'read', 'write', 'save', 'load', 'path']):
        return 'file_ops'

    # Business logic (default)
    return 'business_logic'

def _extract_dependencies(node: ast.FunctionDef) -> List[str]:
    """Extract external dependencies used by the function."""
    dependencies = []
    for child in ast.walk(node):
        if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
            if isinstance(child.func.value, ast.Name):
                dependencies.append(child.func.value.id)
    return list(set(dependencies))

# Link metadata for introspection
extract_functions_link._modulink_metadata = {
    'function_type': 'discovery_link',
    'input_requirements': ['python_files', 'source_path'],
    'output_keys': ['discovered_functions', 'extraction_summary', 'extraction_success'],
    'error_handling': 'graceful',
    'complexity': 'high',
    'original_method': 'MagicConverter._scan_python_file + _extract_function_info'
}
