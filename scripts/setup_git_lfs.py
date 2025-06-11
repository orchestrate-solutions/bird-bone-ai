#!/usr/bin/env python3
"""
Git LFS Setup Script - Modulink Chain Implementation

Following the Modulink approach for Issue #3: Configure Git LFS for Large Binary Files
This script implements the LFS setup as a functional composition chain.

Usage:
    python scripts/setup_git_lfs.py
    python scripts/setup_git_lfs.py --validate-only
    python scripts/setup_git_lfs.py --test-mode
"""

import subprocess
import sys
from pathlib import Path
import argparse
import json
from typing import Dict, List, Any
from dataclasses import dataclass

# Modulink-style context type
Ctx = Dict[str, Any]

@dataclass
class LFSSetupConfig:
    """Configuration for Git LFS setup"""
    repository_path: str = "."
    test_mode: bool = False
    validate_only: bool = False
    verbose: bool = True

def create_context(config: LFSSetupConfig) -> Ctx:
    """Create initial context for LFS setup chain"""
    return {
        'config': config,
        'repository_path': config.repository_path,
        'test_mode': config.test_mode,
        'validate_only': config.validate_only,
        'verbose': config.verbose,
        'errors': [],
        'warnings': [],
        'setup_complete': False,
        'validation_results': {},
        'lfs_patterns': [],
        'test_files_created': []
    }

# Modulink-style chain functions
async def check_prerequisites(ctx: Ctx) -> Ctx:
    """Check Git LFS prerequisites"""
    if ctx['verbose']:
        print("🔍 Checking Git LFS prerequisites...")
    
    # Check Git LFS installation
    try:
        result = subprocess.run(['git', 'lfs', 'version'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            ctx['errors'].append("Git LFS not installed or not accessible")
            return ctx
        
        ctx['validation_results']['lfs_installed'] = True
        if ctx['verbose']:
            print(f"✅ Git LFS version: {result.stdout.strip()}")
    except Exception as e:
        ctx['errors'].append(f"Failed to check Git LFS: {e}")
        return ctx
    
    # Check Git repository
    try:
        result = subprocess.run(['git', 'rev-parse', '--git-dir'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            ctx['errors'].append("Not in a Git repository")
            return ctx
        
        ctx['validation_results']['git_repository'] = True
        if ctx['verbose']:
            print("✅ Valid Git repository detected")
    except Exception as e:
        ctx['errors'].append(f"Failed to check Git repository: {e}")
        return ctx
    
    # Check GitHub remote
    try:
        result = subprocess.run(['git', 'remote', '-v'], 
                              capture_output=True, text=True)
        if result.returncode == 0 and 'github.com' in result.stdout:
            ctx['validation_results']['github_remote'] = True
            if ctx['verbose']:
                print("✅ GitHub remote configured (LFS supported)")
        else:
            ctx['warnings'].append("GitHub remote not configured - LFS may not be available")
    except Exception as e:
        ctx['warnings'].append(f"Could not check remote: {e}")
    
    return ctx

async def initialize_git_lfs(ctx: Ctx) -> Ctx:
    """Initialize Git LFS in repository"""
    if ctx['validate_only'] or ctx['errors']:
        return ctx
    
    if ctx['verbose']:
        print("🚀 Initializing Git LFS...")
    
    try:
        result = subprocess.run(['git', 'lfs', 'install'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            ctx['validation_results']['lfs_initialized'] = True
            if ctx['verbose']:
                print("✅ Git LFS initialized successfully")
        else:
            ctx['errors'].append(f"Failed to initialize Git LFS: {result.stderr}")
    except Exception as e:
        ctx['errors'].append(f"Error initializing Git LFS: {e}")
    
    return ctx

async def validate_gitattributes(ctx: Ctx) -> Ctx:
    """Validate .gitattributes configuration"""
    if ctx['verbose']:
        print("📝 Validating .gitattributes configuration...")
    
    gitattributes_path = Path(ctx['repository_path']) / '.gitattributes'
    
    if not gitattributes_path.exists():
        ctx['errors'].append(".gitattributes file does not exist")
        return ctx
    
    try:
        content = gitattributes_path.read_text()
        
        # Check for required patterns (aligned with research decisions)
        required_patterns = [
            '*.pt filter=lfs diff=lfs merge=lfs -text',
            '*.safetensors filter=lfs diff=lfs merge=lfs -text',
            '*.gguf filter=lfs diff=lfs merge=lfs -text',
            '*.bin filter=lfs diff=lfs merge=lfs -text',
            '*.npz filter=lfs diff=lfs merge=lfs -text',
            '*.h5 filter=lfs diff=lfs merge=lfs -text',
            '*.tar.gz filter=lfs diff=lfs merge=lfs -text',
            '*.zip filter=lfs diff=lfs merge=lfs -text'
        ]
        
        missing_patterns = []
        for pattern in required_patterns:
            if pattern not in content:
                missing_patterns.append(pattern)
        
        if missing_patterns:
            ctx['errors'].append(f"Missing LFS patterns: {missing_patterns}")
        else:
            ctx['validation_results']['gitattributes_configured'] = True
            if ctx['verbose']:
                print("✅ .gitattributes properly configured")
        
        # Check that pickle patterns are NOT present (research decision)
        pickle_patterns = ['*.pkl filter=lfs', '*.pickle filter=lfs']
        found_pickle = []
        for pattern in pickle_patterns:
            if pattern in content:
                found_pickle.append(pattern)
        
        if found_pickle:
            ctx['warnings'].append(f"Pickle patterns found (should be removed per Issue #2): {found_pickle}")
        
        ctx['lfs_patterns'] = required_patterns
        
    except Exception as e:
        ctx['errors'].append(f"Error reading .gitattributes: {e}")
    
    return ctx

async def test_lfs_functionality(ctx: Ctx) -> Ctx:
    """Test LFS functionality with sample files"""
    if ctx['validate_only'] or ctx['errors']:
        return ctx
    
    if ctx['verbose']:
        print("🧪 Testing LFS functionality...")
    
    test_extensions = ['.pt', '.safetensors', '.npz']
    test_files = []
    
    try:
        # Create test files
        for ext in test_extensions:
            test_file = f"test_lfs_sample{ext}"
            test_files.append(test_file)
            
            with open(test_file, 'wb') as f:
                f.write(b'LFS_TEST_DATA' * 100)  # Create small test file
        
        # Add to git and check LFS tracking
        for test_file in test_files:
            subprocess.run(['git', 'add', test_file], check=True)
            
            # Check if tracked by LFS
            result = subprocess.run(['git', 'lfs', 'ls-files'], 
                                  capture_output=True, text=True)
            if test_file not in result.stdout:
                ctx['errors'].append(f"File {test_file} not tracked by LFS")
        
        if not ctx['errors']:
            ctx['validation_results']['lfs_tracking'] = True
            if ctx['verbose']:
                print("✅ LFS file tracking working correctly")
        
        ctx['test_files_created'] = test_files
        
    except Exception as e:
        ctx['errors'].append(f"Error testing LFS functionality: {e}")
    finally:
        # Clean up test files
        for test_file in test_files:
            if Path(test_file).exists():
                Path(test_file).unlink()
            subprocess.run(['git', 'reset', 'HEAD', test_file], 
                         capture_output=True)
    
    return ctx

async def validate_lfs_environment(ctx: Ctx) -> Ctx:
    """Validate LFS environment configuration"""
    if ctx['verbose']:
        print("⚙️  Validating LFS environment...")
    
    try:
        result = subprocess.run(['git', 'lfs', 'env'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            env_output = result.stdout
            
            required_configs = [
                'git config filter.lfs.clean',
                'git config filter.lfs.smudge'
            ]
            
            missing_configs = []
            for config in required_configs:
                if config not in env_output:
                    missing_configs.append(config)
            
            if missing_configs:
                ctx['errors'].append(f"Missing LFS configurations: {missing_configs}")
            else:
                ctx['validation_results']['lfs_environment'] = True
                if ctx['verbose']:
                    print("✅ LFS environment properly configured")
        else:
            ctx['errors'].append("Failed to get LFS environment")
    except Exception as e:
        ctx['errors'].append(f"Error validating LFS environment: {e}")
    
    return ctx

async def generate_report(ctx: Ctx) -> Ctx:
    """Generate setup/validation report"""
    if ctx['verbose']:
        print("\n📊 Git LFS Setup Report")
        print("=" * 50)
    
    # Summary
    total_checks = len(ctx['validation_results'])
    passed_checks = sum(1 for v in ctx['validation_results'].values() if v)
    
    if ctx['verbose']:
        print(f"Validation Results: {passed_checks}/{total_checks} checks passed")
        
        for check, status in ctx['validation_results'].items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {check}")
        
        if ctx['warnings']:
            print(f"\n⚠️  Warnings ({len(ctx['warnings'])}):")
            for warning in ctx['warnings']:
                print(f"  • {warning}")
        
        if ctx['errors']:
            print(f"\n❌ Errors ({len(ctx['errors'])}):")
            for error in ctx['errors']:
                print(f"  • {error}")
        
        # Success determination
        critical_checks = ['lfs_installed', 'git_repository', 'gitattributes_configured']
        setup_successful = all(
            ctx['validation_results'].get(check, False) for check in critical_checks
        ) and not ctx['errors']
        
        if setup_successful:
            print("\n🎉 Git LFS setup completed successfully!")
            ctx['setup_complete'] = True
        else:
            print("\n🚫 Git LFS setup incomplete or failed")
    
    return ctx

# Modulink-style chain composition
async def git_lfs_setup_chain(ctx: Ctx) -> Ctx:
    """Complete Git LFS setup chain"""
    # Sequential chain execution
    ctx = await check_prerequisites(ctx)
    if not ctx['validate_only']:
        ctx = await initialize_git_lfs(ctx)
    ctx = await validate_gitattributes(ctx)
    if not ctx['validate_only']:
        ctx = await test_lfs_functionality(ctx)
    ctx = await validate_lfs_environment(ctx)
    ctx = await generate_report(ctx)
    
    return ctx

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Git LFS Setup Script')
    parser.add_argument('--validate-only', action='store_true',
                       help='Only validate existing setup, do not modify')
    parser.add_argument('--test-mode', action='store_true',
                       help='Run in test mode with additional validation')
    parser.add_argument('--quiet', action='store_true',
                       help='Suppress verbose output')
    
    args = parser.parse_args()
    
    config = LFSSetupConfig(
        validate_only=args.validate_only,
        test_mode=args.test_mode,
        verbose=not args.quiet
    )
    
    # Create initial context
    ctx = create_context(config)
    
    # Run the setup chain
    import asyncio
    result_ctx = asyncio.run(git_lfs_setup_chain(ctx))
    
    # Exit with appropriate code
    if result_ctx['errors']:
        sys.exit(1)
    elif not result_ctx.get('setup_complete', False) and not args.validate_only:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
