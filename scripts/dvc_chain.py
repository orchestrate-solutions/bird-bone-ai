"""
DVC Initialization Chain
========================

Purpose:
    Composes individual DVC links into a complete initialization chain using
    ModuLink architecture patterns for DVC model versioning setup.

Chain Flow:
    1. validate_prerequisites_link - Check DVC/Git availability
    2. initialize_dvc_subdirectory_link - Initialize DVC in models/
    3. configure_dvc_cache_link - Configure cache settings
    4. setup_dvcignore_link - Create .dvcignore file
    5. create_sample_pipeline_link - Create sample DVC pipeline
    6. test_dvc_operations_link - Test DVC functionality

Middleware Stack:
    - logging_middleware: Comprehensive operation logging
    - error_handler_middleware: Exception handling and transformation

Usage:
    from scripts.dvc_chain import dvc_init_chain
    
    result = await dvc_init_chain({
        'operation': 'dvc_initialization',
        'errors': []
    })
    
    if result.get('errors'):
        # Handle errors
    else:
        # DVC initialization successful
"""

import sys
from pathlib import Path
from modulink import chain

# Add project root to Python path for imports
project_root = str(Path(__file__).parent.parent.absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import ModuLink components
from scripts.dvc import (
    validate_prerequisites_link,
    initialize_dvc_subdirectory_link,
    configure_dvc_cache_link,
    setup_dvcignore_link,
    create_sample_pipeline_link,
    test_dvc_operations_link,
    logging_middleware,
    error_handler_middleware
)

# Create the main DVC initialization chain
dvc_init_chain = chain([
    validate_prerequisites_link,
    initialize_dvc_subdirectory_link,
    configure_dvc_cache_link,
    setup_dvcignore_link,
    create_sample_pipeline_link,
    test_dvc_operations_link
]).with_middleware([
    logging_middleware,
    error_handler_middleware
])

# Chain metadata
__chain_name__ = "DVC Initialization Chain"
__chain_version__ = "1.0.0"
__chain_description__ = "Complete DVC setup for Bird-Bone AI model versioning"
