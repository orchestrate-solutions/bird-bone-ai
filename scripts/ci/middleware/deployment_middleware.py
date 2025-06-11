"""
Deployment Middleware
====================

Middleware for deployment automation and validation.
"""
import logging
import subprocess
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class DeploymentCheck:
    """Deployment check result."""
    name: str
    passed: bool
    message: str
    details: Dict[str, Any]

class DeploymentMiddleware:
    """Middleware for deployment operations."""
    
    def __init__(self):
        """Initialize deployment middleware."""
        self.deployment_checks: List[DeploymentCheck] = []
    
    def process(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Process deployment operations."""
        logger.info("Running deployment middleware...")
        
        try:
            # Run deployment readiness checks
            self.check_build_readiness(ctx)
            self.check_deployment_config(ctx)
            self.check_environment_config(ctx)
            self.check_docker_config(ctx)
            
            ctx['deployment_middleware_completed'] = True
            ctx['deployment_checks'] = [
                {
                    'name': check.name,
                    'passed': check.passed,
                    'message': check.message,
                    'details': check.details
                }
                for check in self.deployment_checks
            ]
            
        except Exception as e:
            logger.error(f"Deployment middleware failed: {e}")
            ctx['deployment_middleware_error'] = str(e)
        
        return ctx
    
    def check_build_readiness(self, ctx: Dict[str, Any]) -> None:
        """Check if the project is ready for build."""
        try:
            project_root = Path.cwd()
            
            # Check for essential files
            essential_files = [
                'pyproject.toml',
                'requirements.txt',
                'setup.py'
            ]
            
            found_files = []
            for file_name in essential_files:
                if (project_root / file_name).exists():
                    found_files.append(file_name)
            
            if found_files:
                self.deployment_checks.append(DeploymentCheck(
                    name="build_readiness",
                    passed=True,
                    message=f"Build configuration files found: {', '.join(found_files)}",
                    details={'found_files': found_files, 'essential_files': essential_files}
                ))
            else:
                self.deployment_checks.append(DeploymentCheck(
                    name="build_readiness",
                    passed=False,
                    message="No build configuration files found",
                    details={'found_files': found_files, 'essential_files': essential_files}
                ))
                
        except Exception as e:
            self.deployment_checks.append(DeploymentCheck(
                name="build_readiness",
                passed=False,
                message=f"Could not check build readiness: {e}",
                details={'error': str(e)}
            ))
    
    def check_deployment_config(self, ctx: Dict[str, Any]) -> None:
        """Check deployment configuration."""
        try:
            project_root = Path.cwd()
            
            # Check for deployment-related files
            deployment_files = [
                'Dockerfile',
                'docker-compose.yml',
                'Procfile',
                'app.yaml',
                'serverless.yml',
                '.github/workflows'
            ]
            
            found_deployment_files = []
            for file_name in deployment_files:
                file_path = project_root / file_name
                if file_path.exists():
                    found_deployment_files.append(file_name)
            
            if found_deployment_files:
                self.deployment_checks.append(DeploymentCheck(
                    name="deployment_config",
                    passed=True,
                    message=f"Deployment configuration found: {', '.join(found_deployment_files)}",
                    details={'found_files': found_deployment_files}
                ))
            else:
                self.deployment_checks.append(DeploymentCheck(
                    name="deployment_config",
                    passed=False,
                    message="No deployment configuration files found",
                    details={'checked_files': deployment_files}
                ))
                
        except Exception as e:
            self.deployment_checks.append(DeploymentCheck(
                name="deployment_config",
                passed=False,
                message=f"Could not check deployment configuration: {e}",
                details={'error': str(e)}
            ))
    
    def check_environment_config(self, ctx: Dict[str, Any]) -> None:
        """Check environment configuration."""
        try:
            project_root = Path.cwd()
            
            # Check for environment configuration files
            env_files = [
                '.env.example',
                '.env.template',
                'config.yaml',
                'config.json'
            ]
            
            found_env_files = []
            for file_name in env_files:
                if (project_root / file_name).exists():
                    found_env_files.append(file_name)
            
            # Check for environment variables documentation
            readme_files = list(project_root.glob("README*"))
            has_env_docs = False
            
            for readme_file in readme_files:
                try:
                    with open(readme_file, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                        if any(keyword in content for keyword in ['environment', 'config', 'env', 'setup']):
                            has_env_docs = True
                            break
                except Exception:
                    continue
            
            if found_env_files or has_env_docs:
                self.deployment_checks.append(DeploymentCheck(
                    name="environment_config",
                    passed=True,
                    message="Environment configuration documentation found",
                    details={
                        'found_env_files': found_env_files,
                        'has_env_docs': has_env_docs
                    }
                ))
            else:
                self.deployment_checks.append(DeploymentCheck(
                    name="environment_config",
                    passed=False,
                    message="No environment configuration documentation found",
                    details={'checked_files': env_files}
                ))
                
        except Exception as e:
            self.deployment_checks.append(DeploymentCheck(
                name="environment_config",
                passed=False,
                message=f"Could not check environment configuration: {e}",
                details={'error': str(e)}
            ))
    
    def check_docker_config(self, ctx: Dict[str, Any]) -> None:
        """Check Docker configuration."""
        try:
            project_root = Path.cwd()
            dockerfile = project_root / "Dockerfile"
            dockercompose = project_root / "docker-compose.yml"
            
            docker_status = {
                'dockerfile_exists': dockerfile.exists(),
                'dockercompose_exists': dockercompose.exists(),
                'docker_available': False
            }
            
            # Check if Docker is available
            try:
                result = subprocess.run(
                    ['docker', '--version'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                docker_status['docker_available'] = result.returncode == 0
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
            
            if dockerfile.exists():
                # Validate Dockerfile syntax (basic check)
                try:
                    with open(dockerfile, 'r') as f:
                        dockerfile_content = f.read()
                        if dockerfile_content.strip().startswith('FROM'):
                            docker_status['dockerfile_valid'] = True
                        else:
                            docker_status['dockerfile_valid'] = False
                except Exception:
                    docker_status['dockerfile_valid'] = False
            
            if any(docker_status.values()):
                self.deployment_checks.append(DeploymentCheck(
                    name="docker_config",
                    passed=True,
                    message="Docker configuration found",
                    details=docker_status
                ))
            else:
                self.deployment_checks.append(DeploymentCheck(
                    name="docker_config",
                    passed=False,
                    message="No Docker configuration found",
                    details=docker_status
                ))
                
        except Exception as e:
            self.deployment_checks.append(DeploymentCheck(
                name="docker_config",
                passed=False,
                message=f"Could not check Docker configuration: {e}",
                details={'error': str(e)}
            ))

__all__ = ['DeploymentMiddleware', 'DeploymentCheck']
