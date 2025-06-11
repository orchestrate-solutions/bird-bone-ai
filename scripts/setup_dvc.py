#!/usr/bin/env python3
"""
DVC Initialization Script for Bird-Bone AI
===========================================

This script implements DVC initialization using ModuLink chains following TDD principles.
It initializes DVC in the /models subdirectory for model versioning and tracking.

Issue: #4 - Initialize DVC for Model Versioning
Epic: Foundation & Infrastructure Setup

ModuLink Architecture:
    - Individual link functions for each operation
    - Middleware for logging and error handling
    - Clean composition and reusable components

Usage:
    python scripts/setup_dvc.py
    
    Or import and use programmatically:
    from scripts.setup_dvc import run_dvc_initialization
    success = await run_dvc_initialization()
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add project root to Python path for imports
project_root = str(Path(__file__).parent.parent.absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from scripts.dvc_chain import dvc_init_chain

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def run_dvc_initialization() -> bool:
    """
    Run the complete DVC initialization process using ModuLink chain
    
    Returns:
        bool: True if initialization successful, False if errors occurred
    """
    initial_ctx = {
        'operation': 'dvc_initialization',
        'started_at': str(Path.cwd()),
        'errors': []
    }
    
    logger.info("🚀 Starting DVC initialization for Bird-Bone AI")
    logger.info("=" * 60)
    
    try:
        result = await dvc_init_chain(initial_ctx)
        
        if result.get('errors'):
            logger.error("❌ DVC initialization completed with errors:")
            for error in result['errors']:
                logger.error(f"  - {error['type']}: {error['details']}")
            return False
        else:
            logger.info("✅ DVC initialization completed successfully!")
            logger.info("\nSummary:")
            logger.info(f"  - DVC Version: {result.get('dvc_version', 'Unknown')}")
            logger.info(f"  - Models Directory: {result.get('models_dir')}")
            logger.info(f"  - Cache Configured: {result.get('cache_configured', False)}")
            logger.info(f"  - Sample Pipeline: {result.get('pipeline_created', False)}")
            logger.info(f"  - All Tests Passed: {result.get('all_tests_passed', False)}")
            
            # Additional success details
            if result.get('test_results'):
                logger.info(f"  - Tests Run: {len(result['test_results'])}")
                passed_tests = sum(1 for test in result['test_results'] if test['success'])
                logger.info(f"  - Tests Passed: {passed_tests}/{len(result['test_results'])}")
            
            logger.info("\n🎉 DVC is ready for model versioning!")
            return True
            
    except Exception as e:
        logger.exception(f"💥 Unexpected error during DVC initialization: {e}")
        return False

def main():
    """Main entry point for command-line execution"""
    try:
        success = asyncio.run(run_dvc_initialization())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n⚠️  DVC initialization interrupted by user")
        exit(130)
    except Exception as e:
        logger.exception(f"💥 Fatal error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
