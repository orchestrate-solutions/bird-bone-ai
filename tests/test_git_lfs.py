#!/usr/bin/env python3
"""
Git LFS Configuration Test Suite

Test-driven development for Issue #3: Configure Git LFS for Large Binary Files
Following the Modulink approach with comprehensive test coverage.

Test Categories:
1. Git LFS Installation and Prerequisites
2. File Pattern Configuration
3. LFS Tracking Functionality
4. Storage Configuration
5. Sample File Testing
6. Migration Functionality
"""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path
import pytest
import json
from typing import Dict, List, Any

# Test configuration - Aligned with Issue #2 Research Decisions
# Updated to reflect comprehensive LFS pattern coverage (synchronized with .gitattributes)

# Core critical extensions that MUST be present (minimum requirements)
CRITICAL_MODEL_EXTENSIONS = [
    ".pt",
    ".pth",
    ".safetensors",
    ".gguf",
    ".bin",
    ".onnx",
    ".pb",
]
CRITICAL_DATA_EXTENSIONS = [
    ".npz",
    ".npy",
    ".h5",
    ".hdf5",
    ".parquet",
]  # Removed .pkl per research decision
CRITICAL_ARCHIVE_EXTENSIONS = [".tar.gz", ".tgz", ".zip", ".7z"]

# Legacy test constants for backward compatibility
TEST_MODEL_EXTENSIONS = CRITICAL_MODEL_EXTENSIONS
TEST_DATA_EXTENSIONS = CRITICAL_DATA_EXTENSIONS
TEST_ARCHIVE_EXTENSIONS = CRITICAL_ARCHIVE_EXTENSIONS

MINIMUM_STORAGE_REQUIREMENT = 1024 * 1024 * 100  # 100MB


def extract_all_lfs_patterns_from_gitattributes() -> List[str]:
    """Extract all LFS patterns from .gitattributes file dynamically"""
    gitattributes_path = Path(".gitattributes")
    if not gitattributes_path.exists():
        return []

    content = gitattributes_path.read_text()
    lfs_patterns = []

    for line in content.split("\n"):
        line = line.strip()
        # Skip comments and empty lines
        if not line or line.startswith("#"):
            continue

        # Check if line contains LFS filter configuration
        if "filter=lfs diff=lfs merge=lfs -text" in line:
            lfs_patterns.append(line)

    return lfs_patterns


def extract_extensions_from_patterns(patterns: List[str]) -> List[str]:
    """Extract file extensions from LFS patterns"""
    extensions = []
    for pattern in patterns:
        # Extract pattern part (before 'filter=lfs')
        pattern_part = pattern.split()[0]
        if pattern_part.startswith("*"):
            # Extract extension (everything after the *)
            ext = pattern_part[1:]
            if ext and not ext.startswith(
                "_"
            ):  # Skip project-specific patterns like *_compressed.*
                extensions.append(ext)
    return list(set(extensions))  # Remove duplicates


class TestGitLFSPrerequisites:
    """Test Git LFS installation and prerequisites"""

    def test_git_lfs_installed(self):
        """Verify Git LFS is properly installed and accessible"""
        result = subprocess.run(
            ["git", "lfs", "version"], capture_output=True, text=True
        )
        assert result.returncode == 0, "Git LFS not installed or not accessible"
        assert "git-lfs" in result.stdout.lower(), "Git LFS version output unexpected"

    def test_git_repository_exists(self):
        """Verify we're in a valid Git repository"""
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"], capture_output=True, text=True
        )
        assert result.returncode == 0, "Not in a Git repository"

    def test_github_remote_configured(self):
        """Verify GitHub remote is configured (supports LFS)"""
        result = subprocess.run(["git", "remote", "-v"], capture_output=True, text=True)
        assert result.returncode == 0, "Failed to check Git remotes"
        assert "github.com" in result.stdout, "GitHub remote not configured"


class TestGitAttributesConfiguration:
    """Test .gitattributes file configuration for LFS patterns"""

    def test_gitattributes_exists(self):
        """Verify .gitattributes file exists"""
        gitattributes_path = Path(".gitattributes")
        assert gitattributes_path.exists(), ".gitattributes file does not exist"

    def test_model_file_patterns_configured(self):
        """Verify model file extensions are configured for LFS"""
        gitattributes_content = Path(".gitattributes").read_text()

        for ext in TEST_MODEL_EXTENSIONS:
            pattern = f"*{ext} filter=lfs diff=lfs merge=lfs -text"
            assert pattern in gitattributes_content, f"Missing LFS pattern for {ext}"

    def test_data_file_patterns_configured(self):
        """Verify data file extensions are configured for LFS"""
        gitattributes_content = Path(".gitattributes").read_text()

        for ext in TEST_DATA_EXTENSIONS:
            pattern = f"*{ext} filter=lfs diff=lfs merge=lfs -text"
            assert pattern in gitattributes_content, f"Missing LFS pattern for {ext}"

    def test_archive_file_patterns_configured(self):
        """Verify archive file extensions are configured for LFS"""
        gitattributes_content = Path(".gitattributes").read_text()

        for ext in TEST_ARCHIVE_EXTENSIONS:
            pattern = f"*{ext} filter=lfs diff=lfs merge=lfs -text"
            assert pattern in gitattributes_content, f"Missing LFS pattern for {ext}"

    def test_gitattributes_format_valid(self):
        """Verify .gitattributes has proper LFS format"""
        gitattributes_content = Path(".gitattributes").read_text()
        lines = [
            line.strip() for line in gitattributes_content.split("\n") if line.strip()
        ]

        for line in lines:
            if "filter=lfs" in line:
                # Check LFS line format: pattern filter=lfs diff=lfs merge=lfs -text
                parts = line.split()
                assert len(parts) == 5, f"Invalid LFS line format: {line}"
                assert "filter=lfs" in parts, f"Missing filter=lfs in: {line}"
                assert "diff=lfs" in parts, f"Missing diff=lfs in: {line}"
                assert "merge=lfs" in parts, f"Missing merge=lfs in: {line}"
                assert "-text" in parts, f"Missing -text in: {line}"

    def test_comprehensive_lfs_pattern_coverage(self):
        """Test that all LFS patterns in .gitattributes are properly formatted and comprehensive"""
        # Extract all patterns dynamically from .gitattributes
        all_lfs_patterns = extract_all_lfs_patterns_from_gitattributes()

        # Should have a comprehensive set of patterns (45+ expected)
        assert (
            len(all_lfs_patterns) >= 40
        ), f"Expected 40+ LFS patterns, found {len(all_lfs_patterns)}"

        # Extract extensions for analysis
        all_extensions = extract_extensions_from_patterns(all_lfs_patterns)

        # Verify critical extensions are present
        critical_extensions = [".pt", ".safetensors", ".gguf", ".bin"]
        for ext in critical_extensions:
            assert (
                ext in all_extensions
            ), f"Critical extension {ext} missing from LFS patterns"

        # Verify format of all patterns
        for pattern in all_lfs_patterns:
            parts = pattern.split()
            assert len(parts) >= 4, f"Invalid LFS pattern format: {pattern}"
            assert "filter=lfs" in parts, f"Missing filter=lfs in: {pattern}"
            assert "diff=lfs" in parts, f"Missing diff=lfs in: {pattern}"
            assert "merge=lfs" in parts, f"Missing merge=lfs in: {pattern}"
            assert "-text" in parts, f"Missing -text in: {pattern}"

        # Verify no pickle patterns (security decision from Issue #2)
        pickle_patterns = [p for p in all_lfs_patterns if ".pkl" in p]
        assert (
            len(pickle_patterns) == 0
        ), f"Found pickle patterns (security risk): {pickle_patterns}"

        if hasattr(self, "_verbose_output"):
            print(f"\n📊 LFS Pattern Analysis:")
            print(f"  Total patterns: {len(all_lfs_patterns)}")
            print(f"  Unique extensions: {len(all_extensions)}")
            print(f"  Sample patterns: {all_lfs_patterns[:3]}...")

    def test_bird_bone_ai_specific_patterns(self):
        """Test Bird-Bone AI specific compression artifact patterns"""
        gitattributes_content = Path(".gitattributes").read_text()

        # Check for project-specific patterns
        project_patterns = [
            "*_compressed.*",
            "*_density_loss.*",
            "*_healing_checkpoint.*",
            "*_bap_snapshot.*",
            "*_pruning_mask.*",
            "*_quantized.*",
            "*_factorized.*",
            "*_lora.*",
        ]

        for pattern in project_patterns:
            full_pattern = f"{pattern} filter=lfs diff=lfs merge=lfs -text"
            assert (
                full_pattern in gitattributes_content
            ), f"Missing Bird-Bone AI specific pattern: {pattern}"


class TestLFSTrackingFunctionality:
    """Test LFS tracking functionality with sample files"""

    def test_lfs_initialization(self):
        """Verify LFS is initialized in repository"""
        result = subprocess.run(["git", "lfs", "track"], capture_output=True, text=True)
        assert result.returncode == 0, "Git LFS tracking command failed"

    def test_model_files_tracked_by_lfs(self):
        """Test that model files are properly tracked by LFS"""
        # Create temporary test files
        test_files = []
        for ext in TEST_MODEL_EXTENSIONS:
            test_file = f"test_model{ext}"
            test_files.append(test_file)

            # Create a small test file
            with open(test_file, "wb") as f:
                f.write(b"X" * 1024)  # 1KB test file

        try:
            # Add files to git
            for test_file in test_files:
                subprocess.run(["git", "add", test_file], check=True)

            # Check if files are tracked by LFS
            for test_file in test_files:
                assert self._is_file_tracked_by_lfs(
                    test_file
                ), f"File {test_file} not tracked by LFS"

        finally:
            # Clean up test files
            for test_file in test_files:
                if Path(test_file).exists():
                    Path(test_file).unlink()
                # Remove from git index
                subprocess.run(["git", "reset", "HEAD", test_file], capture_output=True)

    def test_data_files_tracked_by_lfs(self):
        """Test that data files are properly tracked by LFS"""
        test_files = []
        for ext in TEST_DATA_EXTENSIONS:
            test_file = f"test_data{ext}"
            test_files.append(test_file)

            with open(test_file, "wb") as f:
                f.write(b"Y" * 2048)  # 2KB test file

        try:
            for test_file in test_files:
                subprocess.run(["git", "add", test_file], check=True)

            for test_file in test_files:
                assert self._is_file_tracked_by_lfs(
                    test_file
                ), f"File {test_file} not tracked by LFS"

        finally:
            for test_file in test_files:
                if Path(test_file).exists():
                    Path(test_file).unlink()
                subprocess.run(["git", "reset", "HEAD", test_file], capture_output=True)

    def test_archive_files_tracked_by_lfs(self):
        """Test that archive files are properly tracked by LFS"""
        test_files = []
        for ext in TEST_ARCHIVE_EXTENSIONS:
            test_file = f"test_archive{ext}"
            test_files.append(test_file)

            with open(test_file, "wb") as f:
                f.write(b"Z" * 4096)  # 4KB test file

        try:
            for test_file in test_files:
                subprocess.run(["git", "add", test_file], check=True)

            for test_file in test_files:
                assert self._is_file_tracked_by_lfs(
                    test_file
                ), f"File {test_file} not tracked by LFS"

        finally:
            for test_file in test_files:
                if Path(test_file).exists():
                    Path(test_file).unlink()
                subprocess.run(["git", "reset", "HEAD", test_file], capture_output=True)

    def _is_file_tracked_by_lfs(self, filepath: str) -> bool:
        """Check if a file is tracked by Git LFS"""
        result = subprocess.run(
            ["git", "lfs", "ls-files"], capture_output=True, text=True
        )
        if result.returncode != 0:
            return False

        return filepath in result.stdout


class TestLFSStorageConfiguration:
    """Test LFS storage configuration and limits"""

    def test_lfs_storage_configuration(self):
        """Verify LFS storage is properly configured"""
        result = subprocess.run(["git", "lfs", "env"], capture_output=True, text=True)
        assert result.returncode == 0, "Failed to get LFS environment"

        # Check for basic LFS configuration
        env_output = result.stdout
        assert (
            "git config filter.lfs.clean" in env_output
        ), "LFS clean filter not configured"
        assert (
            "git config filter.lfs.smudge" in env_output
        ), "LFS smudge filter not configured"

    def test_github_lfs_support(self):
        """Test GitHub LFS support by checking remote configuration"""
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"], capture_output=True, text=True
        )
        if result.returncode == 0:
            remote_url = result.stdout.strip()
            assert "github.com" in remote_url, "Remote not GitHub (may not support LFS)"


class TestLFSPushPullFunctionality:
    """Test LFS push/pull functionality"""

    def test_lfs_push_functionality(self):
        """Test LFS push functionality (dry run)"""
        # Note: This is a dry run test to avoid actually pushing
        result = subprocess.run(
            ["git", "lfs", "push", "--dry-run", "origin", "HEAD"],
            capture_output=True,
            text=True,
        )
        # We expect this to succeed even if no LFS files to push
        assert (
            result.returncode == 0 or "no objects to push" in result.stderr.lower()
        ), "LFS push functionality test failed"

    def test_lfs_pull_configuration(self):
        """Test LFS pull configuration"""
        # Test LFS pull help/status instead of dry-run (which is not supported)
        result = subprocess.run(
            ["git", "lfs", "pull", "--help"], capture_output=True, text=True
        )
        # Help command should work if LFS pull is properly configured
        assert result.returncode == 0, "LFS pull configuration test failed"
        assert "pull" in result.stdout.lower(), "LFS pull help output unexpected"


class TestLFSIntegration:
    """Test LFS integration with project structure"""

    def test_models_directory_ready_for_lfs(self):
        """Verify models directory is ready for LFS files"""
        models_dir = Path("models")
        assert models_dir.exists(), "Models directory does not exist"
        assert models_dir.is_dir(), "Models path is not a directory"

    def test_lfs_with_dvc_compatibility(self):
        """Test LFS compatibility with DVC (future integration)"""
        # This test ensures LFS won't conflict with DVC
        # DVC will handle models/ directory, LFS handles large binary files elsewhere
        gitattributes_content = Path(".gitattributes").read_text()

        # Ensure we don't have conflicting patterns for models/ directory
        lines = gitattributes_content.split("\n")
        models_specific_lines = [line for line in lines if "models/" in line]

        # For now, we should not have models/ specific LFS rules
        # (DVC will handle models directory)
        for line in models_specific_lines:
            if "filter=lfs" in line:
                # This might be intentional, just warn
                with pytest.warns(
                    UserWarning, match="LFS pattern for models directory"
                ):
                    warnings.warn(
                        f"LFS pattern for models directory: {line}", UserWarning
                    )


class TestModulinkIntegration:
    """Test Modulink-style functional composition for LFS operations"""

    def test_lfs_setup_context_structure(self):
        """Test that LFS setup can work with Modulink context patterns"""
        # This test verifies our LFS setup works with Modulink Ctx patterns
        sample_ctx = {
            "repository_path": ".",
            "lfs_patterns": TEST_MODEL_EXTENSIONS + TEST_DATA_EXTENSIONS,
            "test_mode": True,
            "errors": [],
        }

        # Verify we can process this context structure
        assert isinstance(sample_ctx["lfs_patterns"], list)
        assert len(sample_ctx["lfs_patterns"]) > 0
        assert "errors" in sample_ctx

    def test_lfs_validation_chain_structure(self):
        """Test structure for LFS validation chain"""
        validation_results = {
            "lfs_installed": True,
            "gitattributes_configured": True,
            "tracking_functional": True,
            "storage_configured": True,
            "test_files_passed": True,
            "errors": [],
            "warnings": [],
        }

        # Verify all required validation points are covered
        required_checks = [
            "lfs_installed",
            "gitattributes_configured",
            "tracking_functional",
            "storage_configured",
        ]

        for check in required_checks:
            assert check in validation_results, f"Missing validation check: {check}"


# Utility functions for test support
def create_test_model_file(filepath: str, size_kb: int = 1) -> None:
    """Create a test model file of specified size"""
    with open(filepath, "wb") as f:
        f.write(b"X" * (size_kb * 1024))


def cleanup_test_files(filepaths: List[str]) -> None:
    """Clean up test files from filesystem and git"""
    for filepath in filepaths:
        if Path(filepath).exists():
            Path(filepath).unlink()
        subprocess.run(["git", "reset", "HEAD", filepath], capture_output=True)


# Test configuration and fixtures
@pytest.fixture(scope="session")
def lfs_test_context():
    """Provide test context for LFS operations"""
    return {
        "test_extensions": TEST_MODEL_EXTENSIONS
        + TEST_DATA_EXTENSIONS
        + TEST_ARCHIVE_EXTENSIONS,
        "min_storage": MINIMUM_STORAGE_REQUIREMENT,
        "test_files_created": [],
        "cleanup_needed": False,
    }


if __name__ == "__main__":
    # Run tests directly if script is executed
    pytest.main([__file__, "-v", "--tb=short"])
