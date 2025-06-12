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

from modulink import catch_errors, error_handlers

# Import ModuLink components
from scripts.dvc import (
    configure_dvc_cache_link,
    create_sample_pipeline_link,
    initialize_dvc_subdirectory_link,
    setup_dvcignore_link,
    test_dvc_operations_link,
    validate_prerequisites_link,
)

# Import custom file-based logging middleware and ModuLink error handlers
from scripts.dvc.middleware import (
    file_logging_after_middleware,
    file_logging_before_middleware,
)

# Create the main DVC initialization chain with custom file-based logging
dvc_init_chain = chain(
    validate_prerequisites_link,
    initialize_dvc_subdirectory_link,
    configure_dvc_cache_link,
    setup_dvcignore_link,
    create_sample_pipeline_link,
    test_dvc_operations_link,
)

# Add custom file-based middleware for persistent logging
dvc_init_chain.use.before(file_logging_before_middleware)
dvc_init_chain.use.after(file_logging_after_middleware)
dvc_init_chain.use.after(catch_errors(error_handlers.log_and_continue))

# Chain metadata
__chain_name__ = "DVC Initialization Chain"
__chain_version__ = "1.0.0"
__chain_description__ = "Complete DVC setup for Bird-Bone AI model versioning"

# Main execution block
if __name__ == "__main__":
    import asyncio
    import os

    print(f"🚀 Starting {__chain_name__} v{__chain_version__}")
    print(f"📝 {__chain_description__}")
    print("=" * 60)

    # Initial context for DVC initialization
    initial_context = {
        "operation": "dvc_initialization",
        "started_at": os.getcwd(),
        "errors": [],
    }

    async def run_chain():
        try:
            # Execute the chain (await the coroutine)
            result = await dvc_init_chain(initial_context)

            print("\n" + "=" * 60)
            print("🎉 DVC Chain Execution Complete!")

            # Display results
            if result.get("errors"):
                print(f"⚠️ Completed with {len(result['errors'])} errors:")
                for error in result["errors"]:
                    print(f"   - {error}")
            else:
                print("✅ All operations completed successfully!")

            # Show key results
            if result.get("dvc_initialized"):
                print(f"📁 DVC initialized in: {result.get('models_dir')}")
            if result.get("test_results"):
                test_results = result["test_results"]
                passed = sum(1 for r in test_results if r.get("passed", False))
                total = len(test_results)
                print(f"🧪 Tests: {passed}/{total} passed")

            print("📊 Operations logged to: logs/ directory")

        except Exception as e:
            print(f"💥 Chain execution failed: {str(e)}")
            import traceback

            traceback.print_exc()
            return False

        return True

    try:
        # Run the async chain
        success = asyncio.run(run_chain())

        if not success:
            sys.exit(1)

    except Exception as e:
        print(f"💥 Unexpected error running chain: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
