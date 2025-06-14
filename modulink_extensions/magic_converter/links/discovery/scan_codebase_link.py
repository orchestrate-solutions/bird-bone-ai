"""
Scan Codebase Link
=================

ModuLink link that recursively scans a codebase to discover Python files.
Extracts the file discovery logic from MagicConverter.discover_functions().

Input Context:
- source_path: Path to the codebase to scan
- verbose: Optional boolean for verbose logging

Output Context:
- python_files: List of discovered Python file paths
- scan_summary: Statistics about the scan
- scan_success: Boolean indicating successful scan
"""

import asyncio
from pathlib import Path
from typing import Dict, Any, List

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


async def scan_codebase_link(ctx: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively scan a codebase to discover Python files.

    This link extracts the file discovery logic from the original
    MagicConverter.discover_functions() method.

    Args:
        ctx: ModuLink context containing scan parameters

    Returns:
        ctx: Updated context with discovered files and scan results

    Context Requirements:
        - source_path (str|Path): Path to the codebase to scan

    Context Outputs:
        - python_files (List[Path]): List of discovered Python file paths
        - scan_summary (Dict): Statistics about the scan
        - scan_success (bool): Whether scan succeeded
    """

    # Check for existing errors
    if ctx.get('errors'):
        return ctx

    # Extract source path from context
    source_path = ctx.get('source_path')
    if not source_path:
        ctx.setdefault('errors', []).append({
            'type': 'missing_context',
            'link': 'scan_codebase_link',
            'message': 'Missing required context key: source_path'
        })
        ctx['scan_success'] = False
        return ctx

    # Convert to Path object and validate
    try:
        source_path = Path(source_path).resolve()
        if not source_path.exists():
            ctx.setdefault('errors', []).append({
                'type': 'invalid_path',
                'link': 'scan_codebase_link',
                'message': f'Source path does not exist: {source_path}'
            })
            ctx['scan_success'] = False
            return ctx
    except Exception as e:
        ctx.setdefault('errors', []).append({
            'type': 'path_error',
            'link': 'scan_codebase_link',
            'message': f'Invalid source path: {str(e)}'
        })
        ctx['scan_success'] = False
        return ctx

    verbose = ctx.get('verbose', False)
    console = Console() if RICH_AVAILABLE else None

    try:
        # Log scanning start
        if verbose and RICH_AVAILABLE:
            console.print(f"[cyan]🔍 Scanning codebase: {source_path}[/]")
        elif verbose:
            print(f"🔍 Scanning codebase: {source_path}")

        # Discover Python files using the original logic
        python_files = list(source_path.rglob("*.py"))

        # Filter out unwanted files (original logic)
        filtered_files = []
        for py_file in python_files:
            if _should_include_file(py_file):
                filtered_files.append(py_file)

        # Create scan summary
        scan_summary = {
            'total_files_found': len(python_files),
            'files_after_filtering': len(filtered_files),
            'filtered_out': len(python_files) - len(filtered_files),
            'source_path': str(source_path)
        }

        # Add results to context
        ctx['python_files'] = filtered_files
        ctx['scan_summary'] = scan_summary
        ctx['scan_success'] = True

        # Log completion
        if verbose and RICH_AVAILABLE:
            console.print(f"[green]✅ Found {len(filtered_files)} Python files ({len(python_files)} total, {scan_summary['filtered_out']} filtered)[/]")
        elif verbose:
            print(f"✅ Found {len(filtered_files)} Python files ({len(python_files)} total, {scan_summary['filtered_out']} filtered)")

    except Exception as e:
        ctx.setdefault('errors', []).append({
            'type': 'scan_error',
            'link': 'scan_codebase_link',
            'message': f'Failed to scan codebase: {str(e)}'
        })
        ctx['scan_success'] = False

    return ctx


def _should_include_file(file_path: Path) -> bool:
    """
    Determine if a Python file should be included in scanning.
    Extracted from original MagicConverter logic.
    """
    # Skip if in __pycache__ or similar
    if '__pycache__' in str(file_path):
        return False

    # Skip test files (they'll be regenerated)
    if 'test_' in file_path.name or file_path.name.startswith('test'):
        return False

    # Skip if in typical ignore directories
    ignore_dirs = {'.git', '.venv', 'venv', 'env', '__pycache__', '.pytest_cache', 'node_modules'}
    if any(ignore_dir in file_path.parts for ignore_dir in ignore_dirs):
        return False

    return True


# Link metadata for introspection
scan_codebase_link._modulink_metadata = {
    'function_type': 'discovery_link',
    'input_requirements': ['source_path'],
    'output_keys': ['python_files', 'scan_summary', 'scan_success'],
    'error_handling': 'graceful',
    'complexity': 'low',
    'original_method': 'MagicConverter.discover_functions (file discovery part)'
}
