"""
DVC ModuLink Package
===================

Purpose:
    Domain-specific links and middleware for DVC (Data Version Control) 
    initialization and management using ModuLink architecture patterns.

Package Structure:
    - Individual link functions for each DVC operation
    - Middleware for cross-cutting concerns (logging, error handling)
    - Comprehensive documentation following ModuLink best practices

Available Links:
    - validate_prerequisites_link: Validates DVC and Git availability
    - initialize_dvc_subdirectory_link: Initializes DVC in models directory
    - configure_dvc_cache_link: Configures DVC cache settings
    - setup_dvcignore_link: Creates .dvcignore file
    - create_sample_pipeline_link: Creates sample DVC pipeline
    - test_dvc_operations_link: Tests DVC functionality

Available Middleware:
    - logging_middleware: Operation logging and timing
    - error_handler_middleware: Exception handling and transformation

Usage:
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
    
    from modulink import chain
    
    dvc_chain = chain([
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
"""

# Link exports
from .validate_prerequisites import validate_prerequisites_link
from .initialize_dvc_subdirectory import initialize_dvc_subdirectory_link
from .configure_dvc_cache import configure_dvc_cache_link
from .setup_dvcignore import setup_dvcignore_link
from .create_sample_pipeline import create_sample_pipeline_link
from .test_dvc_operations import test_dvc_operations_link

__all__ = [
    # Link functions
    'validate_prerequisites_link',
    'initialize_dvc_subdirectory_link',
    'configure_dvc_cache_link',
    'setup_dvcignore_link',
    'create_sample_pipeline_link',
    'test_dvc_operations_link'
]

# Package metadata
__version__ = '1.0.0'
__author__ = 'Bird-Bone AI Development Team'
__description__ = 'ModuLink-based DVC initialization and management'
