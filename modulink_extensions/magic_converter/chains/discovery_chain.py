"""
Discovery Chain
==============

ModuLink chain for codebase scanning and function discovery.
Composes the discovery links to provide complete codebase analysis.

This chain extracts the discovery orchestration logic from
MagicConverter.discover_functions() and related methods.

Input Context:
- source_path: Path to the codebase to analyze
- verbose: Optional boolean for verbose logging

Output Context:
- python_files: List of discovered Python files
- discovered_functions: Dict of function metadata
- scan_summary: File scanning statistics
- extraction_summary: Function extraction statistics
- discovery_success: Boolean indicating overall success
"""

import asyncio
from typing import Dict, Any

from modulink_extensions.magic_converter.links.discovery.scan_codebase_link import scan_codebase_link
from modulink_extensions.magic_converter.links.discovery.extract_functions_link import extract_functions_link

async def discovery_chain(ctx: Dict[str, Any]) -> Dict[str, Any]:
    """
    Complete codebase discovery chain.

    This chain orchestrates the discovery process by:
    1. Scanning the codebase for Python files
    2. Extracting function metadata from discovered files

    The chain preserves all original MagicConverter discovery logic
    while organizing it into composable, testable ModuLink components.

    Args:
        ctx: ModuLink context containing discovery parameters

    Returns:
        ctx: Updated context with complete discovery results

    Context Requirements:
        - source_path (str|Path): Path to codebase to analyze

    Context Outputs:
        - python_files (List[Path]): Discovered Python files
        - discovered_functions (Dict): Function metadata by qualified name
        - scan_summary (Dict): File scanning statistics
        - extraction_summary (Dict): Function extraction statistics
        - discovery_success (bool): Overall discovery success
        - discovery_summary (Dict): Combined summary statistics

    Raises:
        ValueError: If discovery fails due to invalid inputs
        OSError: If source path is inaccessible
    """

    # Validate required context
    if not ctx.get('source_path'):
        ctx.setdefault('errors', []).append({
            'type': 'missing_context',
            'chain': 'discovery_chain',
            'message': 'Missing required context key: source_path'
        })
        ctx['discovery_success'] = False
        return ctx

    try:
        # Step 1: Scan codebase for Python files
        ctx = await scan_codebase_link(ctx)

        # Check if scanning succeeded
        if not ctx.get('scan_success', False):
            ctx['discovery_success'] = False
            return ctx

        # Step 2: Extract functions from discovered files
        ctx = await extract_functions_link(ctx)

        # Check if extraction succeeded
        if not ctx.get('extraction_success', False):
            ctx['discovery_success'] = False
            return ctx

        # Create combined discovery summary
        scan_summary = ctx.get('scan_summary', {})
        extraction_summary = ctx.get('extraction_summary', {})

        discovery_summary = {
            'total_files_found': scan_summary.get('total_files_found', 0),
            'files_after_filtering': scan_summary.get('files_after_filtering', 0),
            'files_processed': extraction_summary.get('total_files_processed', 0),
            'functions_discovered': extraction_summary.get('total_functions_discovered', 0),
            'functions_per_file': extraction_summary.get('functions_per_file_avg', 0.0),
            'files_with_errors': extraction_summary.get('files_with_errors', 0),
            'discovery_success': True
        }

        ctx['discovery_summary'] = discovery_summary
        ctx['discovery_success'] = True

        # Log chain completion if verbose
        if ctx.get('verbose', False):
            try:
                from rich.console import Console
                console = Console()
                console.print(f"[green]🎉 Discovery chain completed successfully![/]")
                console.print(f"[cyan]   Files: {discovery_summary['files_after_filtering']} → Functions: {discovery_summary['functions_discovered']}[/]")
            except ImportError:
                print(f"🎉 Discovery chain completed successfully!")
                print(f"   Files: {discovery_summary['files_after_filtering']} → Functions: {discovery_summary['functions_discovered']}")

    except Exception as e:
        # Handle unexpected errors
        ctx.setdefault('errors', []).append({
            'type': 'chain_error',
            'chain': 'discovery_chain',
            'message': f'Discovery chain failed: {str(e)}'
        })
        ctx['discovery_success'] = False

    return ctx

# Utility functions for working with discovery results
def get_functions_by_domain(ctx: Dict[str, Any]) -> Dict[str, list]:
    """Group discovered functions by domain."""
    functions = ctx.get('discovered_functions', {})
    by_domain = {}

    for qualified_name, func_info in functions.items():
        domain = func_info.get('domain', 'unknown')
        if domain not in by_domain:
            by_domain[domain] = []
        by_domain[domain].append((qualified_name, func_info))

    return by_domain

def get_async_functions(ctx: Dict[str, Any]) -> Dict[str, Dict]:
    """Get only async functions from discovery results."""
    functions = ctx.get('discovered_functions', {})
    return {
        name: info for name, info in functions.items()
        if info.get('is_async', False)
    }

def get_functions_with_type_hints(ctx: Dict[str, Any]) -> Dict[str, Dict]:
    """Get functions that have type hints."""
    functions = ctx.get('discovered_functions', {})
    return {
        name: info for name, info in functions.items()
        if info.get('type_hints') and len(info['type_hints']) > 0
    }

# Chain metadata for introspection
discovery_chain._modulink_metadata = {
    'chain_type': 'discovery',
    'links_used': ['scan_codebase_link', 'extract_functions_link'],
    'input_type': 'codebase_path',
    'output_type': 'function_metadata',
    'complexity': 'medium',
    'use_cases': ['codebase_analysis', 'function_discovery', 'project_scanning'],
    'original_method': 'MagicConverter.discover_functions'
}
