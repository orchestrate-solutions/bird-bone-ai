"""
DVC Sample Pipeline Creation Link
================================

Purpose:
    Creates a sample DVC pipeline configuration and .gitignore file to demonstrate
    model tracking workflow and establish best practices for DVC usage.

Input Context Requirements:
    - models_dir: str - Path to models directory

Output Context Additions:
    - dvc_yaml_path: str - Path to created dvc.yaml file
    - pipeline_created: bool - Whether pipeline was successfully created
    - sample_pipeline: dict - The pipeline configuration created
    - gitignore_path: str - Path to models/.gitignore file
    - operation: str - Set to 'create_sample_pipeline'

Error Conditions:
    - Previous errors exist -> skips processing and returns context unchanged
    - File write permission errors -> raises PermissionError (handled by middleware)
    - YAML serialization errors -> raises yaml.YAMLError (handled by middleware)

Dependencies:
    - pathlib.Path: For file path handling
    - yaml: For YAML file generation

Side Effects:
    - Creates dvc.yaml file in models directory
    - Creates .gitignore file in models directory
    - Overwrites existing files if they exist

Example Context Flow:
    Input:  {
        'models_dir': '/project/models'
    }
    Output: {
        'models_dir': '/project/models',
        'operation': 'create_sample_pipeline',
        'dvc_yaml_path': '/project/models/dvc.yaml',
        'pipeline_created': True,
        'sample_pipeline': {...},
        'gitignore_path': '/project/models/.gitignore'
    }
"""

import yaml
from pathlib import Path
from modulink import Ctx


async def create_sample_pipeline_link(ctx: Ctx) -> Ctx:
    """Create a sample DVC pipeline for model tracking demonstration"""
    # Skip if there are previous errors
    if ctx.get("errors"):
        return ctx

    models_dir = Path(ctx["models_dir"])

    # Create sample DVC pipeline configuration
    sample_pipeline = {
        "stages": {
            "prepare_sample_model": {
                "cmd": "python scripts/create_sample_model.py",
                "deps": ["scripts/create_sample_model.py"],
                "outs": ["models/sample_model.pt"],
            },
            "validate_model": {
                "cmd": "python scripts/validate_model.py models/sample_model.pt",
                "deps": ["scripts/validate_model.py", "models/sample_model.pt"],
                "metrics": ["models/validation_metrics.json"],
            },
            "compress_model": {
                "cmd": "python scripts/compress_model.py models/sample_model.pt models/compressed_model.pt",
                "deps": ["scripts/compress_model.py", "models/sample_model.pt"],
                "outs": ["models/compressed_model.pt"],
                "metrics": ["models/compression_metrics.json"],
            },
        },
        "plots": [
            {"models/validation_metrics.json": {"x": "epoch", "y": "accuracy"}},
            {
                "models/compression_metrics.json": {
                    "x": "compression_ratio",
                    "y": "performance_retained",
                }
            },
        ],
    }

    # Create dvc.yaml file
    dvc_yaml_path = models_dir / "dvc.yaml"
    with open(dvc_yaml_path, "w") as f:
        yaml.dump(sample_pipeline, f, default_flow_style=False, indent=2)

    # Create .gitignore for DVC outputs in models directory
    gitignore_path = models_dir / ".gitignore"
    gitignore_content = """# DVC tracked outputs - these should not be committed to Git
/sample_model.pt
/compressed_model.pt
/validation_metrics.json
/compression_metrics.json

# DVC cache files
/.dvc/cache/

# Temporary model files
*.tmp.pt
*.partial.pt

# Model checkpoints (example - adjust as needed)
/checkpoints/

# Experiment artifacts
/experiments/
/logs/
"""

    with open(gitignore_path, "w") as f:
        f.write(gitignore_content)

    return {
        **ctx,
        "operation": "create_sample_pipeline",
        "dvc_yaml_path": str(dvc_yaml_path),
        "pipeline_created": True,
        "sample_pipeline": sample_pipeline,
        "gitignore_path": str(gitignore_path),
    }
