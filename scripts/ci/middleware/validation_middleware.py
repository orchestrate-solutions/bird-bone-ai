"""
Validation Middleware
====================

Middleware for environment and dependency validation.
"""
import logging
import sys
import subprocess
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ValidationCheck:
    """Validation check result."""
    name: str
    passed: bool
    message: str
    details: Dict[str, Any]

class ValidationMiddleware:
    """Middleware for validation operations."""
    
    def __init__(self):
        """Initialize validation middleware."""
        self.checks_performed: List[ValidationCheck] = []
    
    def process(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Process validation checks."""
        logger.info("Running validation middleware...")
        
        try:
            # Run validation checks
            self.check_python_version(ctx)
            self.check_dependencies_installed(ctx)
            self.check_git_configuration(ctx)
            self.check_environment_variables(ctx)
            
            ctx['validation_middleware_completed'] = True
            ctx['validation_checks'] = [
                {
                    'name': check.name,
                    'passed': check.passed,
                    'message': check.message,
                    'details': check.details
                }
                for check in self.checks_performed
            ]
            
        except Exception as e:
            logger.error(f"Validation middleware failed: {e}")
            ctx['validation_middleware_error'] = str(e)
        
        return ctx
    
    def check_python_version(self, ctx: Dict[str, Any]) -> None:
        """Check Python version compatibility."""
        try:
            current_version = sys.version_info
            required_major, required_minor = 3, 8
            
            if current_version.major >= required_major and current_version.minor >= required_minor:
                self.checks_performed.append(ValidationCheck(
                    name="python_version",
                    passed=True,
                    message=f"Python {current_version.major}.{current_version.minor}.{current_version.micro} is compatible",
                    details={'version': f"{current_version.major}.{current_version.minor}.{current_version.micro}"}
                ))
            else:
                self.checks_performed.append(ValidationCheck(
                    name="python_version",
                    passed=False,
                    message=f"Python {current_version.major}.{current_version.minor} is below required version {required_major}.{required_minor}",
                    details={'version': f"{current_version.major}.{current_version.minor}.{current_version.micro}"}
                ))
                
        except Exception as e:
            self.checks_performed.append(ValidationCheck(
                name="python_version",
                passed=False,
                message=f"Could not check Python version: {e}",
                details={'error': str(e)}
            ))
    
    def check_dependencies_installed(self, ctx: Dict[str, Any]) -> None:
        """Check if required dependencies are installed."""
        try:
            project_root = Path.cwd()
            requirements_file = project_root / "requirements.txt"
            
            if not requirements_file.exists():
                self.checks_performed.append(ValidationCheck(
                    name="dependencies_installed",
                    passed=False,
                    message="No requirements.txt file found",
                    details={'file_path': str(requirements_file)}
                ))
                return
            
            # Check if pip can install from requirements.txt (dry run)
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file), '--dry-run'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.checks_performed.append(ValidationCheck(
                    name="dependencies_installed",
                    passed=True,
                    message="All dependencies can be installed successfully",
                    details={'requirements_file': str(requirements_file)}
                ))
            else:
                self.checks_performed.append(ValidationCheck(
                    name="dependencies_installed",
                    passed=False,
                    message="Some dependencies cannot be installed",
                    details={'error': result.stderr, 'requirements_file': str(requirements_file)}
                ))
                
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self.checks_performed.append(ValidationCheck(
                name="dependencies_installed",
                passed=False,
                message=f"Could not check dependencies: {e}",
                details={'error': str(e)}
            ))
    
    def check_git_configuration(self, ctx: Dict[str, Any]) -> None:
        """Check Git configuration."""
        try:
            # Check if we're in a git repository
            result = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Check git config
                config_checks = [
                    ('user.name', 'git config user.name'),
                    ('user.email', 'git config user.email')
                ]
                
                missing_configs = []
                for config_name, command in config_checks:
                    config_result = subprocess.run(
                        command.split(),
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if config_result.returncode != 0 or not config_result.stdout.strip():
                        missing_configs.append(config_name)
                
                if not missing_configs:
                    self.checks_performed.append(ValidationCheck(
                        name="git_configuration",
                        passed=True,
                        message="Git is properly configured",
                        details={'repository': True, 'user_configured': True}
                    ))
                else:
                    self.checks_performed.append(ValidationCheck(
                        name="git_configuration",
                        passed=False,
                        message=f"Missing git configuration: {', '.join(missing_configs)}",
                        details={'repository': True, 'missing_configs': missing_configs}
                    ))
            else:
                self.checks_performed.append(ValidationCheck(
                    name="git_configuration",
                    passed=False,
                    message="Not in a git repository",
                    details={'repository': False}
                ))
                
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self.checks_performed.append(ValidationCheck(
                name="git_configuration",
                passed=False,
                message=f"Could not check git configuration: {e}",
                details={'error': str(e)}
            ))
    
    def check_environment_variables(self, ctx: Dict[str, Any]) -> None:
        """Check for required environment variables."""
        try:
            # Common environment variables that might be needed
            optional_env_vars = [
                'PYTHONPATH',
                'VIRTUAL_ENV',
                'CI',
                'GITHUB_ACTIONS'
            ]
            
            env_status = {}
            for var in optional_env_vars:
                env_status[var] = os.getenv(var) is not None
            
            self.checks_performed.append(ValidationCheck(
                name="environment_variables",
                passed=True,
                message="Environment variables checked",
                details={'environment_variables': env_status}
            ))
            
        except Exception as e:
            self.checks_performed.append(ValidationCheck(
                name="environment_variables",
                passed=False,
                message=f"Could not check environment variables: {e}",
                details={'error': str(e)}
            ))

__all__ = ['ValidationMiddleware', 'ValidationCheck']
