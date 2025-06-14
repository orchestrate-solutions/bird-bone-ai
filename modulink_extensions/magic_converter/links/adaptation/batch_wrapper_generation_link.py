"""
Batch Wrapper Generation Link
============================

ModuLink link that generates ModuLink wrappers for multiple functions using
the existing basic_adaptation_chain. Extracts the core adaptation logic from
MagicConverter.adapt_functions() and _adapt_single_function().

Input Context:
- discovered_functions: Dict of function metadata from discovery chain
- function_configs: Dict of adaptation configs from domain_mapping_link
- source_path: Root source path for function extraction
- verbose: Optional boolean for verbose logging

Output Context:
- adapted_functions: Dict of successfully adapted functions
- adaptation_errors: List of adaptation error details
- adaptation_summary: Statistics about the adaptation process
- adaptation_success: Boolean indicating overall success
"""

import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, Callable

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from modulink_extensions.function_adapter.chains.basic_adaptation_chain import basic_adaptation_chain

async def batch_wrapper_generation_link(ctx: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate ModuLink wrappers for multiple functions using basic_adaptation_chain.

    This link extracts the batch adaptation logic from the original
    MagicConverter.adapt_functions() and _adapt_single_function() methods.

    Args:
        ctx: ModuLink context containing discovered functions and configs

    Returns:
        ctx: Updated context with adapted functions and adaptation results

    Context Requirements:
        - discovered_functions (Dict): Function metadata from discovery chain
        - function_configs (Dict): Adaptation configs from domain_mapping_link
        - source_path (str|Path): Root source path for function extraction

    Context Outputs:
        - adapted_functions (Dict): Successfully adapted functions
        - adaptation_errors (List): Details of adaptation failures
        - adaptation_summary (Dict): Statistics about adaptation process
        - adaptation_success (bool): Overall adaptation success
    """

    # Check for existing errors
    if ctx.get('errors'):
        return ctx

    # Extract required context
    discovered_functions = ctx.get('discovered_functions', {})
    function_configs = ctx.get('function_configs', {})
    source_path = ctx.get('source_path')

    if not discovered_functions:
        ctx.setdefault('errors', []).append({
            'type': 'missing_context',
            'link': 'batch_wrapper_generation_link',
            'message': 'Missing required context key: discovered_functions'
        })
        ctx['adaptation_success'] = False
        return ctx

    if not function_configs:
        ctx.setdefault('errors', []).append({
            'type': 'missing_context',
            'link': 'batch_wrapper_generation_link',
            'message': 'Missing required context key: function_configs'
        })
        ctx['adaptation_success'] = False
        return ctx

    if not source_path:
        ctx.setdefault('errors', []).append({
            'type': 'missing_context',
            'link': 'batch_wrapper_generation_link',
            'message': 'Missing required context key: source_path'
        })
        ctx['adaptation_success'] = False
        return ctx

    source_path = Path(source_path).resolve()
    verbose = ctx.get('verbose', False)
    console = Console() if RICH_AVAILABLE else None

    try:
        if verbose and RICH_AVAILABLE:
            console.print("[cyan]🔄 Generating ModuLink wrappers using basic_adaptation_chain...[/]")
        elif verbose:
            print("🔄 Generating ModuLink wrappers using basic_adaptation_chain...")

        adapted_functions = {}
        adaptation_errors = []
        success_count = 0
        error_count = 0

        # Process functions with progress tracking
        if RICH_AVAILABLE and len(discovered_functions) > 5:
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                         BarColumn(), TaskProgressColumn(), console=console) as progress:
                task = progress.add_task("Adapting functions...", total=len(discovered_functions))

                for qualified_name, func_info in discovered_functions.items():
                    progress.update(task, description=f"Adapting {func_info['name']}")

                    success = await _adapt_single_function(
                        qualified_name, func_info, function_configs, source_path,
                        adapted_functions, adaptation_errors, verbose
                    )

                    if success:
                        success_count += 1
                    else:
                        error_count += 1

                    progress.advance(task)
        else:
            # Process without progress bar for smaller sets
            for i, (qualified_name, func_info) in enumerate(discovered_functions.items()):
                if verbose:
                    print(f"  Adapting {func_info['name']} ({i+1}/{len(discovered_functions)})")

                success = await _adapt_single_function(
                    qualified_name, func_info, function_configs, source_path,
                    adapted_functions, adaptation_errors, verbose
                )

                if success:
                    success_count += 1
                else:
                    error_count += 1

        # Create adaptation summary
        adaptation_summary = {
            'total_functions': len(discovered_functions),
            'successful_adaptations': success_count,
            'failed_adaptations': error_count,
            'success_rate': success_count / len(discovered_functions) if discovered_functions else 0.0
        }

        # Add results to context
        ctx['adapted_functions'] = adapted_functions
        ctx['adaptation_errors'] = adaptation_errors
        ctx['adaptation_summary'] = adaptation_summary
        ctx['adaptation_success'] = True

        # Log completion
        if verbose and RICH_AVAILABLE:
            console.print(f"[green]✅ Successfully adapted {success_count} functions[/]")
            if error_count > 0:
                console.print(f"[yellow]⚠️  {error_count} functions had adaptation errors[/]")
        elif verbose:
            print(f"✅ Successfully adapted {success_count} functions")
            if error_count > 0:
                print(f"⚠️  {error_count} functions had adaptation errors")

    except Exception as e:
        ctx.setdefault('errors', []).append({
            'type': 'adaptation_error',
            'link': 'batch_wrapper_generation_link',
            'message': f'Failed to adapt functions: {str(e)}'
        })
        ctx['adaptation_success'] = False

    return ctx

async def _adapt_single_function(
    qualified_name: str,
    func_info: Dict,
    function_configs: Dict,
    source_path: Path,
    adapted_functions: Dict,
    adaptation_errors: list,
    verbose: bool = False
) -> bool:
    """
    Adapt a single function using the basic adaptation chain.
    Extracted from original MagicConverter._adapt_single_function().
    """
    try:
        # Extract the actual function from the source file
        original_function = _extract_function_object(func_info, source_path, verbose)
        if not original_function:
            adaptation_errors.append({
                'function': qualified_name,
                'error': 'Could not extract function object',
                'type': 'extraction_error'
            })
            return False

        # Get domain-specific configuration
        config = function_configs.get(qualified_name, {})

        # Adapt the function using our existing basic_adaptation_chain
        adapted_function = await basic_adaptation_chain(
            original_function,
            **config
        )

        # Store the adapted function with metadata
        adapted_functions[qualified_name] = {
            'adapted_function': adapted_function,
            'original_info': func_info,
            'config_used': config
        }

        return True

    except Exception as e:
        adaptation_errors.append({
            'function': qualified_name,
            'error': str(e),
            'type': 'adaptation_error'
        })
        return False

def _extract_function_object(func_info: Dict, source_path: Path, verbose: bool = False) -> Optional[Callable]:
    """
    Extract the actual function object from source code.
    Extracted from original MagicConverter._extract_function_object().
    """
    try:
        # Read the source file
        with open(func_info['file_path'], 'r', encoding='utf-8') as f:
            source_lines = f.readlines()

        # Extract function source
        start_line, end_line = func_info['source_lines']
        function_source = ''.join(source_lines[start_line-1:end_line])

        # Create a temporary module and execute the function
        local_namespace = {}
        exec(function_source, local_namespace)

        return local_namespace.get(func_info['name'])

    except Exception as e:
        if verbose:
            print(f"Error extracting function {func_info['name']}: {e}")
        return None

# Utility functions
def get_adapted_function(ctx: Dict[str, Any], qualified_name: str) -> Optional[Callable]:
    """Get an adapted function by qualified name."""
    adapted_functions = ctx.get('adapted_functions', {})
    adaptation_result = adapted_functions.get(qualified_name)
    return adaptation_result['adapted_function'] if adaptation_result else None

def get_adaptation_errors_by_type(ctx: Dict[str, Any], error_type: str = None) -> list:
    """Get adaptation errors, optionally filtered by type."""
    adaptation_errors = ctx.get('adaptation_errors', [])
    if error_type:
        return [error for error in adaptation_errors if error.get('type') == error_type]
    return adaptation_errors

# Link metadata for introspection
batch_wrapper_generation_link._modulink_metadata = {
    'function_type': 'adaptation_link',
    'input_requirements': ['discovered_functions', 'function_configs', 'source_path'],
    'output_keys': ['adapted_functions', 'adaptation_errors', 'adaptation_summary', 'adaptation_success'],
    'error_handling': 'graceful',
    'complexity': 'high',
    'original_method': 'MagicConverter.adapt_functions + _adapt_single_function'
}
