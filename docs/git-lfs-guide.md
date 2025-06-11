# Git LFS Configuration Guide

## Overview

Git Large File Storage (LFS) is configured for the Bird-Bone AI project to handle large binary files efficiently. This guide covers setup, usage, and team collaboration workflows.

## Quick Start

### For New Team Members

1. **Clone the repository:**
   ```bash
   git clone https://github.com/orchestrate-solutions/bird-bone-ai.git
   cd bird-bone-ai
   ```

2. **Install Git LFS (if not already installed):**
   ```bash
   # macOS
   brew install git-lfs
   
   # Ubuntu/Debian
   sudo apt install git-lfs
   
   # Or download from: https://git-lfs.github.io/
   ```

3. **Initialize LFS:**
   ```bash
   git lfs install
   ```

4. **Pull LFS files:**
   ```bash
   git lfs pull
   ```

### Validation

Use our automated validation script:
```bash
python scripts/setup_git_lfs.py --validate-only
```

## File Patterns Tracked by LFS

Based on Issue #2 research decisions, the following patterns are tracked:

### Model Files (Primary Use Case)
- `*.pt` - PyTorch model files
- `*.safetensors` - **Preferred format** (secure, fast)
- `*.gguf` - GGUF format models
- `*.bin` - Generic binary model files
- `*.onnx` - ONNX model files
- `*.pb` - TensorFlow SavedModel files

### Data Files
- `*.npz` - NumPy compressed arrays
- `*.npy` - NumPy arrays
- `*.h5`, `*.hdf5` - HDF5 files
- `*.parquet` - Columnar storage files

### Archives
- `*.tar.gz`, `*.tgz` - Compressed tar archives
- `*.zip` - ZIP archives
- `*.7z` - 7-Zip archives

### Bird-Bone AI Specific Patterns
- `*_compressed.*` - Compression artifacts
- `*_density_loss.*` - Density loss cycle snapshots
- `*_healing_checkpoint.*` - Healing checkpoints
- `*_bap_snapshot.*` - Biophase adaptive pruning artifacts
- `*_quantized.*` - Quantization results
- `*_factorized.*` - Low-rank factorization results

### Media Files (Large Datasets)
- Images: `*.png`, `*.jpg`, `*.jpeg`, `*.tiff`
- Audio: `*.wav`, `*.mp3`, `*.flac`
- Video: `*.mp4`, `*.avi`, `*.mov`
- Documents: `*.pdf`

## Important Exclusions

### ❌ NOT Tracked by LFS (Per Issue #2 Research)

- `*.pkl`, `*.pickle` - **Excluded for security reasons**
  - SafeTensors is preferred for serialization
  - Pickle allows arbitrary code execution
  - If legacy pickle files exist, convert to SafeTensors

### DVC vs LFS Separation

- The `/models` directory is handled by **DVC** (Issue #4)
- LFS handles large files elsewhere in the repository
- This avoids conflicts between versioning systems

## Usage Workflows

### Adding Large Files

1. **Add files normally:**
   ```bash
   git add my_model.safetensors
   git commit -m "Add compressed model checkpoint"
   ```

2. **LFS automatically handles** files matching configured patterns

3. **Verify LFS tracking:**
   ```bash
   git lfs ls-files
   ```

### Working with LFS Files

1. **Check LFS status:**
   ```bash
   git lfs status
   ```

2. **Download specific files:**
   ```bash
   git lfs pull --include="*.safetensors"
   ```

3. **Skip LFS files during clone:**
   ```bash
   GIT_LFS_SKIP_SMUDGE=1 git clone <repo>
   cd <repo>
   git lfs pull  # Download when ready
   ```

### Team Collaboration

1. **Before pushing large changes:**
   ```bash
   git lfs status
   git lfs ls-files --name-only
   ```

2. **Push LFS files:**
   ```bash
   git push origin main
   # LFS files are automatically pushed
   ```

3. **Pull teammate's LFS changes:**
   ```bash
   git pull
   git lfs pull
   ```

## Storage Considerations

### GitHub LFS Limits
- **Free accounts:** 1GB storage, 1GB bandwidth/month
- **Pro accounts:** 50GB storage, 50GB bandwidth/month
- **Organization plans:** Higher limits available

### Monitoring Usage
```bash
git lfs env
curl -H "Authorization: token <your-token>" \
  https://api.github.com/repos/orchestrate-solutions/bird-bone-ai/git/lfs
```

### Cost Optimization
1. **Use compression** for archives before committing
2. **Clean up old LFS objects** periodically
3. **Consider external storage** for very large datasets

## Advanced Usage

### Selective File Patterns
Add custom patterns to `.gitattributes`:
```
# Custom project patterns
experiments/large_datasets/** filter=lfs diff=lfs merge=lfs -text
*.custom_format filter=lfs diff=lfs merge=lfs -text
```

### Migration Existing Files
```bash
# Migrate existing large files to LFS
git lfs migrate import --include="*.pt,*.safetensors"
```

### Performance Optimization
```bash
# Configure LFS for better performance
git config lfs.concurrenttransfers 8
git config lfs.dialtimeout 60
```

## Troubleshooting

### Common Issues

1. **"File not found" errors:**
   ```bash
   git lfs pull
   git lfs checkout
   ```

2. **LFS quota exceeded:**
   - Check usage: `git lfs env`
   - Clean old files: `git lfs prune`
   - Consider external storage

3. **Files not tracked by LFS:**
   ```bash
   # Check if pattern exists in .gitattributes
   git check-attr filter path/to/file
   
   # Re-add files if needed
   git rm --cached file.pt
   git add file.pt
   ```

4. **Slow clone/pull performance:**
   ```bash
   # Use partial clone
   git clone --filter=blob:none <repo>
   git lfs pull
   ```

### Validation and Debugging

Use our comprehensive validation script:
```bash
# Full validation
python scripts/setup_git_lfs.py --validate-only

# Test mode with extra checks
python scripts/setup_git_lfs.py --test-mode

# Quiet mode for CI/CD
python scripts/setup_git_lfs.py --validate-only --quiet
```

## Integration with Bird-Bone AI Workflows

### Compression Pipeline
1. **Original models** → DVC tracking (`/models`)
2. **Compression artifacts** → LFS tracking (pattern-based)
3. **Experiment results** → LFS for large files, Git for metadata

### Density Loss Cycles
```bash
# Checkpoint before density loss
cp model.safetensors model_pre_density_loss.safetensors

# Apply compression
python compress.py --input model.safetensors --output model_compressed.safetensors

# Healing checkpoint
cp model_compressed.safetensors model_healing_checkpoint.safetensors
```

### Team Collaboration
1. **Researchers** work with local LFS files
2. **CI/CD** validates LFS configuration
3. **Production** uses optimized LFS patterns

## Security and Best Practices

### File Format Preferences (Issue #2 Alignment)
1. **SafeTensors** - Primary choice for security
2. **PyTorch native** - When SafeTensors unavailable
3. **ONNX** - For model interchange
4. **❌ Avoid pickle** - Security vulnerability

### Access Control
- Repository LFS access follows GitHub permissions
- Use organization/team controls for sensitive models
- Consider signed commits for model authenticity

### Backup Strategy
- LFS files are backed up with repository
- Consider additional backup for critical models
- Document model provenance and lineage

## References

- [Git LFS Documentation](https://git-lfs.github.io/)
- [GitHub LFS Usage](https://docs.github.com/en/repositories/working-with-files/managing-large-files)
- [Issue #2: Library Selection Research](../research/decision-logs/issue-2-library-selection.md)
- [SafeTensors Security Benefits](https://github.com/huggingface/safetensors)

---

**Last Updated:** June 11, 2025  
**Issue Reference:** #3 - Configure Git LFS for Large Binary Files  
**Maintainer:** Bird-Bone AI Development Team
