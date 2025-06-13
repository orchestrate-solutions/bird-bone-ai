"""
Tests for Scan Codebase Link
============================

Test suite for the scan_codebase_link ModuLink link.
Tests the file discovery logic extracted from MagicConverter.
"""

import pytest
import asyncio
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, Any

from modulink_extensions.magic_converter.links.discovery.scan_codebase_link import (
    scan_codebase_link,
    _should_include_file
)

class TestScanCodebaseLink:
    """Test suite for scan_codebase_link."""

    @pytest.mark.asyncio
    async def test_scan_empty_directory(self):
        """Test scanning an empty directory."""
        with TemporaryDirectory() as temp_dir:
            ctx = {'source_path': temp_dir}

            result_ctx = await scan_codebase_link(ctx)

            assert result_ctx['scan_success'] is True
            assert result_ctx['python_files'] == []
            assert result_ctx['scan_summary']['total_files_found'] == 0
            assert result_ctx['scan_summary']['files_after_filtering'] == 0

    @pytest.mark.asyncio
    async def test_scan_with_python_files(self):
        """Test scanning directory with Python files."""
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create some Python files
            (temp_path / "main.py").write_text("def main(): pass")
            (temp_path / "utils.py").write_text("def helper(): pass")
            (temp_path / "subdir").mkdir()
            (temp_path / "subdir" / "module.py").write_text("class Module: pass")

            ctx = {'source_path': temp_dir}

            result_ctx = await scan_codebase_link(ctx)

            assert result_ctx['scan_success'] is True
            assert len(result_ctx['python_files']) == 3
            assert result_ctx['scan_summary']['total_files_found'] == 3
            assert result_ctx['scan_summary']['files_after_filtering'] == 3

    @pytest.mark.asyncio
    async def test_scan_filters_test_files(self):
        """Test that test files are filtered out."""
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create Python files including test files
            (temp_path / "main.py").write_text("def main(): pass")
            (temp_path / "test_main.py").write_text("def test_main(): pass")
            (temp_path / "test_utils.py").write_text("def test_utils(): pass")

            ctx = {'source_path': temp_dir}

            result_ctx = await scan_codebase_link(ctx)

            assert result_ctx['scan_success'] is True
            assert len(result_ctx['python_files']) == 1  # Only main.py
            assert result_ctx['scan_summary']['total_files_found'] == 3
            assert result_ctx['scan_summary']['files_after_filtering'] == 1
            assert result_ctx['scan_summary']['filtered_out'] == 2

    @pytest.mark.asyncio
    async def test_scan_filters_pycache(self):
        """Test that __pycache__ files are filtered out."""
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create Python files including __pycache__
            (temp_path / "main.py").write_text("def main(): pass")
            (temp_path / "__pycache__").mkdir()
            (temp_path / "__pycache__" / "main.cpython-39.pyc").write_text("bytecode")

            ctx = {'source_path': temp_dir}

            result_ctx = await scan_codebase_link(ctx)

            assert result_ctx['scan_success'] is True
            assert len(result_ctx['python_files']) == 1  # Only main.py
            # Note: .pyc files aren't matched by *.py glob, so total found is still 1

    @pytest.mark.asyncio
    async def test_scan_missing_source_path(self):
        """Test error handling when source_path is missing."""
        ctx = {}  # No source_path

        result_ctx = await scan_codebase_link(ctx)

        assert result_ctx['scan_success'] is False
        assert len(result_ctx['errors']) == 1
        assert result_ctx['errors'][0]['type'] == 'missing_context'
        assert 'source_path' in result_ctx['errors'][0]['message']

    @pytest.mark.asyncio
    async def test_scan_invalid_source_path(self):
        """Test error handling when source_path doesn't exist."""
        ctx = {'source_path': '/nonexistent/path'}

        result_ctx = await scan_codebase_link(ctx)

        assert result_ctx['scan_success'] is False
        assert len(result_ctx['errors']) == 1
        assert result_ctx['errors'][0]['type'] == 'invalid_path'

    @pytest.mark.asyncio
    async def test_scan_preserves_existing_errors(self):
        """Test that existing errors are preserved."""
        with TemporaryDirectory() as temp_dir:
            ctx = {
                'source_path': temp_dir,
                'errors': [{'type': 'previous_error', 'message': 'Previous error'}]
            }

            result_ctx = await scan_codebase_link(ctx)

            # Should return early without processing
            assert 'scan_success' not in result_ctx
            assert len(result_ctx['errors']) == 1
            assert result_ctx['errors'][0]['type'] == 'previous_error'

    @pytest.mark.asyncio
    async def test_scan_with_verbose_logging(self):
        """Test verbose logging doesn't break functionality."""
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            (temp_path / "test.py").write_text("def test(): pass")

            ctx = {'source_path': temp_dir, 'verbose': True}

            result_ctx = await scan_codebase_link(ctx)

            assert result_ctx['scan_success'] is True
            assert len(result_ctx['python_files']) == 1

class TestShouldIncludeFile:
    """Test suite for _should_include_file helper function."""

    def test_include_regular_python_file(self):
        """Test that regular Python files are included."""
        file_path = Path("src/main.py")
        assert _should_include_file(file_path) is True

    def test_exclude_test_files(self):
        """Test that test files are excluded."""
        test_files = [
            Path("test_main.py"),
            Path("tests/test_utils.py"),
            Path("src/test_module.py")
        ]

        for test_file in test_files:
            assert _should_include_file(test_file) is False

    def test_exclude_pycache_files(self):
        """Test that __pycache__ files are excluded."""
        pycache_file = Path("src/__pycache__/main.cpython-39.pyc")
        assert _should_include_file(pycache_file) is False

    def test_exclude_venv_files(self):
        """Test that virtual environment files are excluded."""
        venv_files = [
            Path("venv/lib/python3.9/site-packages/module.py"),
            Path(".venv/scripts/activate.py"),
            Path("env/bin/python")
        ]

        for venv_file in venv_files:
            assert _should_include_file(venv_file) is False

    def test_exclude_git_files(self):
        """Test that .git files are excluded."""
        git_file = Path(".git/hooks/pre-commit.py")
        assert _should_include_file(git_file) is False

    def test_include_nested_python_files(self):
        """Test that nested Python files are included."""
        nested_files = [
            Path("src/utils/helper.py"),
            Path("modules/core/processor.py"),
            Path("deep/nested/path/module.py")
        ]

        for nested_file in nested_files:
            assert _should_include_file(nested_file) is True

if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__])
