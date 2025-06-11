#!/usr/bin/env bash

# Bird-Bone AI Environment Setup Script
# Comprehensive environment creation and validation for Issue #2
# Optimized for H100/A100 cloud GPUs with data collection focus

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_NAME="bird-bone-ai"
PYTHON_VERSION="3.11"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if conda is installed
check_conda() {
    print_status "Checking conda installation..."
    if ! command -v conda &> /dev/null; then
        print_error "Conda not found. Please install Anaconda or Miniconda first."
        echo "Download from: https://docs.conda.io/en/latest/miniconda.html"
        exit 1
    fi
    
    local conda_version=$(conda --version | cut -d' ' -f2)
    print_success "Found conda version: $conda_version"
}

# Function to check CUDA availability
check_cuda() {
    print_status "Checking CUDA availability..."
    
    if command -v nvidia-smi &> /dev/null; then
        local cuda_version=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader,nounits | head -n1)
        print_success "NVIDIA GPU detected with driver version: $cuda_version"
        
        # Check for H100/A100
        local gpu_names=$(nvidia-smi --query-gpu=name --format=csv,noheader)
        if echo "$gpu_names" | grep -E "(H100|A100)" &> /dev/null; then
            print_success "H100/A100 GPU detected - optimal for bird-bone AI development"
        else
            print_warning "GPU detected but not H100/A100. Performance may be suboptimal."
            echo "Detected GPUs: $gpu_names"
        fi
    else
        print_warning "NVIDIA GPU not detected. Running in CPU-only mode."
        print_warning "For optimal performance, use H100/A100 cloud instances."
    fi
}

# Function to create conda environment
create_environment() {
    print_status "Creating conda environment '$ENV_NAME'..."
    
    # Check if environment already exists
    if conda env list | grep -q "^$ENV_NAME "; then
        print_warning "Environment '$ENV_NAME' already exists."
        read -p "Do you want to recreate it? [y/N]: " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Removing existing environment..."
            conda env remove -n "$ENV_NAME" -y
        else
            print_status "Using existing environment."
            return 0
        fi
    fi
    
    # Create environment from environment.yml
    print_status "Creating environment from environment.yml..."
    cd "$PROJECT_ROOT"
    conda env create -f environment.yml
    
    print_success "Environment '$ENV_NAME' created successfully"
}

# Function to activate environment and install pip dependencies
install_pip_dependencies() {
    print_status "Installing pip dependencies..."
    
    # Activate environment and install requirements
    eval "$(conda shell.bash hook)"
    conda activate "$ENV_NAME"
    
    # Upgrade pip first
    python -m pip install --upgrade pip
    
    # Install requirements with retries for network issues
    local max_retries=3
    local retry_count=0
    
    while [ $retry_count -lt $max_retries ]; do
        if pip install -r "$PROJECT_ROOT/requirements.txt"; then
            print_success "All pip dependencies installed successfully"
            break
        else
            retry_count=$((retry_count + 1))
            if [ $retry_count -lt $max_retries ]; then
                print_warning "Installation failed. Retrying ($retry_count/$max_retries)..."
                sleep 5
            else
                print_error "Failed to install pip dependencies after $max_retries attempts"
                exit 1
            fi
        fi
    done
}

# Function to validate critical imports
validate_imports() {
    print_status "Validating critical package imports..."
    
    eval "$(conda shell.bash hook)"
    conda activate "$ENV_NAME"
    
    # Test critical imports
    python << 'EOF'
import sys
import traceback

def test_import(module_name, description=""):
    try:
        exec(f"import {module_name}")
        print(f"✓ {module_name} {description}")
        return True
    except ImportError as e:
        print(f"✗ {module_name} - FAILED: {e}")
        return False
    except Exception as e:
        print(f"✗ {module_name} - ERROR: {e}")
        return False

print("Testing critical imports:")
success_count = 0
total_tests = 0

# Core ML libraries
tests = [
    ("torch", "- PyTorch core"),
    ("transformers", "- HuggingFace transformers"),
    ("accelerate", "- Model acceleration"),
    ("safetensors", "- Secure tensor serialization"),
    ("bitsandbytes", "- Quantization library"),
    ("peft", "- Parameter-efficient fine-tuning"),
    ("modulink_py", "- ModuLink architecture"),
    ("kedro", "- Pipeline orchestration"),
    ("dvc", "- Data version control"),
    ("wandb", "- Experiment tracking"),
    ("nbdime", "- Notebook diffing"),
    ("pytest", "- Testing framework"),
    ("black", "- Code formatting"),
    ("ruff", "- Fast linting"),
    ("jupyter", "- Notebook environment"),
    ("matplotlib", "- Plotting"),
    ("numpy", "- Numerical computing"),
    ("pandas", "- Data manipulation"),
]

for module, desc in tests:
    if test_import(module, desc):
        success_count += 1
    total_tests += 1

print(f"\nImport validation: {success_count}/{total_tests} successful")

if success_count == total_tests:
    print("✅ All critical imports successful!")
    sys.exit(0)
else:
    print("❌ Some imports failed. Check installation.")
    sys.exit(1)
EOF

    if [ $? -eq 0 ]; then
        print_success "All critical imports validated successfully"
    else
        print_error "Import validation failed. Some packages may not be installed correctly."
        exit 1
    fi
}

# Function to test GPU functionality
test_gpu_functionality() {
    print_status "Testing GPU functionality..."
    
    eval "$(conda shell.bash hook)"
    conda activate "$ENV_NAME"
    
    python << 'EOF'
import torch
import sys

print("PyTorch GPU Test:")
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"CUDA version: {torch.version.cuda}")
    print(f"cuDNN version: {torch.backends.cudnn.version()}")
    print(f"GPU count: {torch.cuda.device_count()}")
    
    for i in range(torch.cuda.device_count()):
        gpu_name = torch.cuda.get_device_name(i)
        gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1e9
        print(f"GPU {i}: {gpu_name} ({gpu_memory:.1f} GB)")
        
        # Test tensor operations
        try:
            x = torch.randn(1000, 1000, device=f'cuda:{i}')
            y = torch.randn(1000, 1000, device=f'cuda:{i}')
            z = torch.matmul(x, y)
            print(f"  ✓ Matrix multiplication test passed")
        except Exception as e:
            print(f"  ✗ GPU test failed: {e}")
            sys.exit(1)
    
    print("✅ GPU functionality verified!")
else:
    print("⚠️  Running in CPU-only mode")
    print("   For optimal performance, use CUDA-enabled GPU")

# Test bitsandbytes if available
try:
    import bitsandbytes as bnb
    print(f"\n✓ bitsandbytes {bnb.__version__} available")
    if torch.cuda.is_available():
        print("  Ready for 4-bit/8-bit quantization")
except ImportError:
    print("\n⚠️  bitsandbytes not available - quantization features limited")
EOF

    print_success "GPU functionality test completed"
}

# Function to setup development tools
setup_dev_tools() {
    print_status "Setting up development tools..."
    
    eval "$(conda shell.bash hook)"
    conda activate "$ENV_NAME"
    
    # Install pre-commit hooks if .pre-commit-config.yaml exists
    if [ -f "$PROJECT_ROOT/.pre-commit-config.yaml" ]; then
        print_status "Installing pre-commit hooks..."
        pre-commit install
        print_success "Pre-commit hooks installed"
    else
        print_warning ".pre-commit-config.yaml not found - skipping pre-commit setup"
    fi
    
    # Initialize DVC if not already done
    if [ ! -d "$PROJECT_ROOT/.dvc" ]; then
        print_status "Initializing DVC..."
        cd "$PROJECT_ROOT"
        dvc init --no-scm
        print_success "DVC initialized"
    else
        print_status "DVC already initialized"
    fi
    
    # Initialize Git LFS if not already done
    if ! git lfs env &> /dev/null; then
        print_status "Initializing Git LFS..."
        git lfs install
        print_success "Git LFS initialized"
    else
        print_status "Git LFS already initialized"
    fi
}

# Function to generate environment report
generate_report() {
    print_status "Generating environment health report..."
    
    eval "$(conda shell.bash hook)"
    conda activate "$ENV_NAME"
    
    local report_file="$PROJECT_ROOT/environment_health_report.txt"
    
    cat > "$report_file" << EOF
Bird-Bone AI Environment Health Report
=====================================
Generated: $(date)
Script: $0

System Information:
------------------
OS: $(uname -s) $(uname -r)
Python: $(python --version)
Conda: $(conda --version)
Git: $(git --version)

Environment Details:
-------------------
Name: $ENV_NAME
Location: $(conda info --envs | grep "^$ENV_NAME " | awk '{print $2}')

GPU Information:
---------------
EOF

    # Add GPU info to report
    if command -v nvidia-smi &> /dev/null; then
        echo "NVIDIA Driver: $(nvidia-smi --query-gpu=driver_version --format=csv,noheader,nounits | head -n1)" >> "$report_file"
        echo "GPUs:" >> "$report_file"
        nvidia-smi --query-gpu=name,memory.total --format=csv,noheader | sed 's/^/  /' >> "$report_file"
    else
        echo "No NVIDIA GPU detected" >> "$report_file"
    fi
    
    echo "" >> "$report_file"
    echo "PyTorch Configuration:" >> "$report_file"
    python -c "
import torch
print(f'PyTorch: {torch.__version__}')
print(f'CUDA Available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA Version: {torch.version.cuda}')
    print(f'GPU Count: {torch.cuda.device_count()}')
" >> "$report_file"
    
    echo "" >> "$report_file"
    echo "Package Versions (Key Dependencies):" >> "$report_file"
    pip list | grep -E "(torch|transformers|accelerate|bitsandbytes|peft|modulink|kedro|dvc|wandb)" >> "$report_file"
    
    print_success "Environment report saved to: $report_file"
}

# Function to provide next steps
show_next_steps() {
    print_success "Environment setup completed successfully! 🎉"
    echo ""
    print_status "Next steps:"
    echo "1. Activate environment: conda activate $ENV_NAME"
    echo "2. Review environment report: cat environment_health_report.txt"
    echo "3. Test the setup: python -c 'import torch; print(f\"CUDA: {torch.cuda.is_available()}\")'"
    echo "4. Start development: jupyter lab"
    echo ""
    print_status "For bird-bone AI development:"
    echo "• Use git lfs for large model files"
    echo "• Use dvc for data/model versioning"
    echo "• Run pre-commit hooks before commits"
    echo "• Monitor with wandb for experiment tracking"
    echo ""
    print_status "GPU optimization:"
    echo "• Ensure CUDA 12.4+ for optimal H100/A100 performance"
    echo "• Use bitsandbytes for 4-bit/8-bit quantization"
    echo "• Consider DeepSpeed for models >7B parameters"
    echo ""
    echo "Happy coding! 🦆💪"
}

# Main execution
main() {
    echo "Bird-Bone AI Environment Setup"
    echo "=============================="
    echo "Setting up biologically-inspired neural compression environment"
    echo "Optimized for: H100/A100 GPUs, data collection, quality development"
    echo ""
    
    # Pre-flight checks
    check_conda
    check_cuda
    
    # Environment setup
    create_environment
    install_pip_dependencies
    
    # Validation
    validate_imports
    test_gpu_functionality
    
    # Development tools
    setup_dev_tools
    
    # Reporting
    generate_report
    show_next_steps
}

# Run main function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
