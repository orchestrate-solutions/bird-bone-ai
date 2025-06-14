"""
Magic Converter ModuLink Migration
=================================

The magic converter has been refactored from a monolithic class into
proper ModuLink chains and links for better maintainability.

This package contains:
- discovery_chain: Codebase scanning and function discovery
- adaptation_chain: Function adaptation orchestration
- test_generation_chain: Intelligent test generation
- output_generation_chain: File writing and packaging
- magic_converter_chain: Main orchestration chain

The refactoring preserves all original functionality while making
the code more modular, testable, and maintainable.
"""

__version__ = "1.0.0"

# Main exports will be added as chains are implemented
__all__ = []
