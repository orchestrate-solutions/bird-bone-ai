"""
DVC Cache Configuration Link
===========================

Purpose:
    Configures DVC cache settings for optimal performance including cache type,
    protection settings, and other performance optimizations.

Input Context Requirements:
    - models_dir: str - Path to models directory
    - dvc_initialized: bool - Must be True to proceed
    
Output Context Additions:
    - cache_config: dict - Cache configuration settings applied
    - cache_configured: bool - Whether cache was successfully configured
    - operation: str - Set to 'configure_dvc_cache'
    
Error Conditions:
    - Previous errors exist -> skips processing and returns context unchanged
    - DVC not initialized -> context dependency error
    - DVC config command fails -> raises CalledProcessError (handled by middleware)
    - Permission errors -> raises PermissionError (handled by middleware)
    
Dependencies:
    - subprocess: For running DVC config commands
    - pathlib.Path: For directory handling
    
Side Effects:
    - Modifies DVC configuration files in models/.dvc/config
    - Sets cache type to 'reflink,copy' for optimal performance
    - Enables cache protection to prevent accidental modification
    
Example Context Flow:
    Input:  {
        'models_dir': '/project/models',
        'dvc_initialized': True
    }
    Output: {
        'models_dir': '/project/models',
        'dvc_initialized': True,
        'operation': 'configure_dvc_cache',
        'cache_configured': True,
        'cache_config': {
            'type': 'reflink,copy',
            'protected': True
        }
    }
"""

import subprocess
from pathlib import Path
from modulink import Ctx

async def configure_dvc_cache_link(ctx: Ctx) -> Ctx:
    """Configure DVC cache settings for optimal performance"""
    # Skip if there are previous errors
    if ctx.get('errors'):
        return ctx
    
    models_dir = Path(ctx['models_dir'])
    
    # Configure cache settings
    cache_config = {
        'type': 'reflink,copy',  # Use reflinks when possible, fallback to copy
        'protected': True,       # Protect cache files from accidental modification
    }
    
    # Clear any existing cache dir setting
    subprocess.run([
        'dvc', 'cache', 'dir', '--unset'
    ], cwd=models_dir, check=False)  # Allow this to fail if not set
    
    # Configure cache type
    subprocess.run([
        'dvc', 'config', 'cache.type', cache_config['type']
    ], cwd=models_dir, check=True)
    
    # Configure cache protection
    subprocess.run([
        'dvc', 'config', 'cache.protected', str(cache_config['protected']).lower()
    ], cwd=models_dir, check=True)
    
    return {
        **ctx,
        'operation': 'configure_dvc_cache',
        'cache_config': cache_config,
        'cache_configured': True
    }
