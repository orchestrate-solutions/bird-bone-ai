"""
DVC Ignore File Setup Link
==========================

Purpose:
    Creates a .dvcignore file in the models directory with appropriate exclusions
    to prevent tracking of temporary files, system files, and other artifacts.

Input Context Requirements:
    - models_dir: str - Path to models directory

Output Context Additions:
    - dvcignore_path: str - Path to created .dvcignore file
    - dvcignore_created: bool - Whether .dvcignore was successfully created
    - operation: str - Set to 'setup_dvcignore'

Error Conditions:
    - Previous errors exist -> skips processing and returns context unchanged
    - File write permission errors -> raises PermissionError (handled by middleware)
    - Path/directory errors -> raises OSError (handled by middleware)

Dependencies:
    - pathlib.Path: For file path handling

Side Effects:
    - Creates .dvcignore file in models directory
    - Overwrites existing .dvcignore if it exists

Example Context Flow:
    Input:  {
        'models_dir': '/project/models'
    }
    Output: {
        'models_dir': '/project/models',
        'operation': 'setup_dvcignore',
        'dvcignore_path': '/project/models/.dvcignore',
        'dvcignore_created': True
    }
"""

from pathlib import Path

from modulink import Ctx


async def setup_dvcignore_link(ctx: Ctx) -> Ctx:
    """Create .dvcignore file with appropriate exclusions"""
    # Skip if there are previous errors
    if ctx.get("errors"):
        return ctx

    models_dir = Path(ctx["models_dir"])
    dvcignore_path = models_dir / ".dvcignore"

    # Default .dvcignore patterns for models directory
    dvcignore_content = """# DVC ignore file for models directory
# Ignore temporary files and directories
*.tmp
*.temp
.DS_Store
Thumbs.db

# Ignore Python cache
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# Ignore Jupyter notebook checkpoints
.ipynb_checkpoints/

# Ignore IDE files
.vscode/
.idea/
*.swp
*.swo

# Ignore logs
*.log
logs/

# Ignore model artifacts that should not be tracked by DVC
# (Add specific patterns as needed for your use case)

# Ignore compression intermediates
*.partial
*.incomplete

# Ignore system files
.directory
desktop.ini
"""

    # Write the .dvcignore file
    with open(dvcignore_path, "w") as f:
        f.write(dvcignore_content)

    return {
        **ctx,
        "operation": "setup_dvcignore",
        "dvcignore_path": str(dvcignore_path),
        "dvcignore_created": True,
    }
