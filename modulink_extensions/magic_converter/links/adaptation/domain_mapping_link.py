"""
Domain Mapping Link
==================

ModuLink link that creates domain-specific adaptation configurations.
Extracts the logic from MagicConverter._create_domain_config().

Input Context:
- discovered_functions: Dict of function metadata from discovery chain
- verbose: Optional boolean for verbose logging

Output Context:
- function_configs: Dict mapping qualified names to adaptation configs
- domain_mappings: Dict grouping functions by domain
- mapping_success: Boolean indicating successful mapping
"""

import asyncio
from typing import Dict, Any
from collections import defaultdict

try:
    from rich.console import Console
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

async def domain_mapping_link(ctx: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create domain-specific adaptation configurations for discovered functions.

    This link extracts the domain configuration logic from the original
    MagicConverter._create_domain_config() method.

    Args:
        ctx: ModuLink context containing discovered functions

    Returns:
        ctx: Updated context with adaptation configurations

    Context Requirements:
        - discovered_functions (Dict): Function metadata from discovery chain

    Context Outputs:
        - function_configs (Dict): Adaptation configs by qualified name
        - domain_mappings (Dict): Functions grouped by domain
        - mapping_success (bool): Whether mapping succeeded
        - mapping_summary (Dict): Statistics about domain mapping
    """

    # Check for existing errors
    if ctx.get('errors'):
        return ctx

    # Extract discovered functions from context
    discovered_functions = ctx.get('discovered_functions', {})
    if not discovered_functions:
        ctx.setdefault('errors', []).append({
            'type': 'missing_context',
            'link': 'domain_mapping_link',
            'message': 'Missing required context key: discovered_functions'
        })
        ctx['mapping_success'] = False
        return ctx

    verbose = ctx.get('verbose', False)
    console = Console() if RICH_AVAILABLE else None

    try:
        if verbose and RICH_AVAILABLE:
            console.print("[cyan]🔧 Creating domain-specific adaptation configurations...[/]")
        elif verbose:
            print("🔧 Creating domain-specific adaptation configurations...")

        function_configs = {}
        domain_mappings = defaultdict(list)
        domain_stats = defaultdict(int)

        # Process each discovered function
        for qualified_name, func_info in discovered_functions.items():
            domain = func_info.get('domain', 'business_logic')

            # Create domain-specific configuration
            config = _create_domain_config(domain)

            # Store configuration
            function_configs[qualified_name] = config
            domain_mappings[domain].append((qualified_name, func_info))
            domain_stats[domain] += 1

        # Create mapping summary
        mapping_summary = {
            'total_functions': len(discovered_functions),
            'domains_found': len(domain_stats),
            'domain_distribution': dict(domain_stats)
        }

        # Add results to context
        ctx['function_configs'] = function_configs
        ctx['domain_mappings'] = dict(domain_mappings)
        ctx['mapping_success'] = True
        ctx['mapping_summary'] = mapping_summary

        # Log completion
        if verbose and RICH_AVAILABLE:
            console.print(f"[green]✅ Created {len(function_configs)} configurations across {len(domain_stats)} domains[/]")
            for domain, count in domain_stats.items():
                console.print(f"[cyan]   {domain}: {count} functions[/]")
        elif verbose:
            print(f"✅ Created {len(function_configs)} configurations across {len(domain_stats)} domains")
            for domain, count in domain_stats.items():
                print(f"   {domain}: {count} functions")

    except Exception as e:
        ctx.setdefault('errors', []).append({
            'type': 'mapping_error',
            'link': 'domain_mapping_link',
            'message': f'Failed to create domain mappings: {str(e)}'
        })
        ctx['mapping_success'] = False

    return ctx

def _create_domain_config(domain: str) -> Dict:
    """
    Create domain-specific configuration for function adaptation.
    Extracted from original MagicConverter._create_domain_config().
    """
    base_config = {
        'enable_validation': True,
        'enable_tracing': True,
        'enable_metrics': True
    }

    domain_configs = {
        'ml': {
            'user_mapping': {
                'data': 'training_data',
                'model': 'ml_model',
                'X': 'features',
                'y': 'target',
                'features': 'input_features'
            },
            'result_key': 'ml_result'
        },
        'data_processing': {
            'user_mapping': {
                'data': 'input_data',
                'df': 'dataframe',
                'items': 'input_items'
            },
            'result_key': 'processed_data'
        },
        'api': {
            'user_mapping': {
                'url': 'api_endpoint',
                'endpoint': 'api_endpoint',
                'data': 'request_data'
            },
            'result_key': 'api_response'
        },
        'file_ops': {
            'user_mapping': {
                'path': 'file_path',
                'filename': 'file_path',
                'data': 'file_data'
            },
            'result_key': 'file_result'
        },
        'business_logic': {
            'user_mapping': {},
            'result_key': 'result'
        }
    }

    domain_specific = domain_configs.get(domain, domain_configs['business_logic'])
    return {**base_config, **domain_specific}

def get_config_for_function(ctx: Dict[str, Any], qualified_name: str) -> Dict:
    """Get adaptation configuration for a specific function."""
    function_configs = ctx.get('function_configs', {})
    return function_configs.get(qualified_name, _create_domain_config('business_logic'))

def get_functions_by_domain(ctx: Dict[str, Any], domain: str = None) -> Dict:
    """Get functions for a specific domain or all domain mappings."""
    domain_mappings = ctx.get('domain_mappings', {})
    if domain:
        return domain_mappings.get(domain, [])
    return domain_mappings

# Link metadata for introspection
domain_mapping_link._modulink_metadata = {
    'function_type': 'adaptation_link',
    'input_requirements': ['discovered_functions'],
    'output_keys': ['function_configs', 'domain_mappings', 'mapping_success', 'mapping_summary'],
    'error_handling': 'graceful',
    'complexity': 'low',
    'original_method': 'MagicConverter._create_domain_config'
}
