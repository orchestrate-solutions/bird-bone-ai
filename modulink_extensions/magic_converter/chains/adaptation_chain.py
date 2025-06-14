"""
Adaptation Chain
===============

ModuLink chain for function adaptation using the existing basic_adaptation_chain.
Composes the adaptation links to provide complete function adaptation pipeline.

This chain extracts the adaptation orchestration logic from
MagicConverter.adapt_functions() and related methods.

Input Context:
- discovered_functions: Dict of function metadata from discovery chain
- source_path: Path to the codebase being adapted
- verbose: Optional boolean for verbose logging

Output Context:
- adapted_functions: Dict of successfully adapted ModuLink functions
- adaptation_errors: List of adaptation error details
- function_configs: Dict of adaptation configurations used
- domain_mappings: Dict grouping functions by domain
- adaptation_summary: Statistics about the adaptation process
- adaptation_success: Boolean indicating overall success
"""

import asyncio
from typing import Dict, Any

from modulink_extensions.magic_converter.links.adaptation.domain_mapping_link import domain_mapping_link
from modulink_extensions.magic_converter.links.adaptation.batch_wrapper_generation_link import batch_wrapper_generation_link

async def adaptation_chain(ctx: Dict[str, Any]) -> Dict[str, Any]:
    """
    Complete function adaptation chain using existing basic_adaptation_chain.

    This chain orchestrates the adaptation process by:
    1. Creating domain-specific adaptation configurations
    2. Generating ModuLink wrappers using basic_adaptation_chain

    The chain leverages our existing function adapter system while organizing
    the logic into composable, testable ModuLink components.

    Args:
        ctx: ModuLink context containing discovered functions

    Returns:
        ctx: Updated context with adapted functions and results

    Context Requirements:
        - discovered_functions (Dict): Function metadata from discovery chain
        - source_path (str|Path): Path to codebase being adapted

    Context Outputs:
        - adapted_functions (Dict): Successfully adapted ModuLink functions
        - adaptation_errors (List): Details of adaptation failures
        - function_configs (Dict): Adaptation configurations used
        - domain_mappings (Dict): Functions grouped by domain
        - adaptation_summary (Dict): Combined adaptation statistics
        - adaptation_success (bool): Overall adaptation success

    Raises:
        ValueError: If adaptation fails due to invalid inputs
        OSError: If source files are inaccessible
    """

    # Validate required context
    if not ctx.get('discovered_functions'):
        ctx.setdefault('errors', []).append({
            'type': 'missing_context',
            'chain': 'adaptation_chain',
            'message': 'Missing required context key: discovered_functions'
        })
        ctx['adaptation_success'] = False
        return ctx

    if not ctx.get('source_path'):
        ctx.setdefault('errors', []).append({
            'type': 'missing_context',
            'chain': 'adaptation_chain',
            'message': 'Missing required context key: source_path'
        })
        ctx['adaptation_success'] = False
        return ctx

    try:
        # Step 1: Create domain-specific adaptation configurations
        ctx = await domain_mapping_link(ctx)

        # Check if mapping succeeded
        if not ctx.get('mapping_success', False):
            ctx['adaptation_success'] = False
            return ctx

        # Step 2: Generate ModuLink wrappers using basic_adaptation_chain
        ctx = await batch_wrapper_generation_link(ctx)

        # Check if adaptation succeeded
        if not ctx.get('adaptation_success', False):
            return ctx

        # Create combined adaptation summary
        mapping_summary = ctx.get('mapping_summary', {})
        adaptation_summary = ctx.get('adaptation_summary', {})

        combined_summary = {
            'total_functions': mapping_summary.get('total_functions', 0),
            'domains_found': mapping_summary.get('domains_found', 0),
            'domain_distribution': mapping_summary.get('domain_distribution', {}),
            'successful_adaptations': adaptation_summary.get('successful_adaptations', 0),
            'failed_adaptations': adaptation_summary.get('failed_adaptations', 0),
            'success_rate': adaptation_summary.get('success_rate', 0.0),
            'adaptation_complete': True
        }

        ctx['adaptation_summary'] = combined_summary
        ctx['adaptation_success'] = True

        # Log chain completion if verbose
        if ctx.get('verbose', False):
            try:
                from rich.console import Console
                console = Console()
                console.print(f"[green]🎉 Adaptation chain completed successfully![/]")
                console.print(f"[cyan]   Functions: {combined_summary['total_functions']} → Adapted: {combined_summary['successful_adaptations']}[/]")
                console.print(f"[cyan]   Success rate: {combined_summary['success_rate']:.1%}[/]")
            except ImportError:
                print(f"🎉 Adaptation chain completed successfully!")
                print(f"   Functions: {combined_summary['total_functions']} → Adapted: {combined_summary['successful_adaptations']}")
                print(f"   Success rate: {combined_summary['success_rate']:.1%}")

    except Exception as e:
        # Handle unexpected errors
        ctx.setdefault('errors', []).append({
            'type': 'chain_error',
            'chain': 'adaptation_chain',
            'message': f'Adaptation chain failed: {str(e)}'
        })
        ctx['adaptation_success'] = False

    return ctx

# Utility functions for working with adaptation results
def get_adapted_functions_by_domain(ctx: Dict[str, Any]) -> Dict[str, list]:
    """Group adapted functions by domain."""
    adapted_functions = ctx.get('adapted_functions', {})
    domain_mappings = ctx.get('domain_mappings', {})

    adapted_by_domain = {}
    for domain, functions_list in domain_mappings.items():
        adapted_domain_functions = []
        for qualified_name, func_info in functions_list:
            if qualified_name in adapted_functions:
                adapted_domain_functions.append((qualified_name, adapted_functions[qualified_name]))
        adapted_by_domain[domain] = adapted_domain_functions

    return adapted_by_domain

def get_adaptation_success_rate(ctx: Dict[str, Any]) -> float:
    """Get the overall adaptation success rate."""
    adaptation_summary = ctx.get('adaptation_summary', {})
    return adaptation_summary.get('success_rate', 0.0)

def get_failed_adaptations(ctx: Dict[str, Any]) -> list:
    """Get list of functions that failed adaptation."""
    adaptation_errors = ctx.get('adaptation_errors', [])
    return [error['function'] for error in adaptation_errors]

def get_successful_adaptations(ctx: Dict[str, Any]) -> list:
    """Get list of successfully adapted function names."""
    adapted_functions = ctx.get('adapted_functions', {})
    return list(adapted_functions.keys())

# Chain metadata for introspection
adaptation_chain._modulink_metadata = {
    'chain_type': 'adaptation',
    'links_used': ['domain_mapping_link', 'batch_wrapper_generation_link'],
    'input_type': 'discovered_functions',
    'output_type': 'adapted_functions',
    'complexity': 'high',
    'use_cases': ['function_adaptation', 'modulink_conversion', 'batch_processing'],
    'original_method': 'MagicConverter.adapt_functions'
}
