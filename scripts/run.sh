#!/bin/bash

# =============================================================================
# NPM-Style Script Runner for Bird-Bone AI
# =============================================================================
# Mimics npm run scripts behavior for common development tasks
# Usage: ./scripts/run.sh <script-name>
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# =============================================================================
# Available Scripts
# =============================================================================
show_help() {
    cat << EOF
${BLUE}Bird-Bone AI Script Runner${NC}

${YELLOW}USAGE:${NC}
    ./scripts/run.sh <script-name> [args...]

${YELLOW}AVAILABLE SCRIPTS:${NC}

${GREEN}Code Quality:${NC}
    ${BLUE}lint${NC}           Run flake8 linting
    ${BLUE}lint:fix${NC}       Run linting with auto-fixes (isort + black)
    ${BLUE}format${NC}         Format code with black
    ${BLUE}format:check${NC}   Check code formatting without changes
    ${BLUE}imports${NC}        Sort imports with isort
    ${BLUE}imports:check${NC}  Check import sorting without changes
    ${BLUE}quality${NC}        Run all quality checks (lint + format + imports)

${GREEN}Git Operations:${NC}
    ${BLUE}push${NC}           Git push with quality checks (./scripts/git-push.sh)
    ${BLUE}push:force${NC}     Force git push with quality checks
    ${BLUE}push:skip${NC}      Git push without quality checks

${GREEN}Testing:${NC}
    ${BLUE}test${NC}           Run all tests with pytest
    ${BLUE}test:watch${NC}     Run tests in watch mode
    ${BLUE}test:coverage${NC}  Run tests with coverage report

${GREEN}CI/CD:${NC}
    ${BLUE}ci${NC}             Run full CI/CD pipeline locally
    ${BLUE}ci:validate${NC}    Validate CI/CD configuration
    ${BLUE}build${NC}          Build Docker image
    ${BLUE}deploy${NC}         Deploy application

${GREEN}Development:${NC}
    ${BLUE}dev${NC}            Start development server
    ${BLUE}install${NC}        Install all dependencies
    ${BLUE}clean${NC}          Clean build artifacts and cache

${YELLOW}EXAMPLES:${NC}
    ./scripts/run.sh lint
    ./scripts/run.sh push origin main
    ./scripts/run.sh test:coverage
    ./scripts/run.sh quality

${PURPLE}💡 This mimics npm run scripts behavior for Python projects!${NC}
EOF
}

# =============================================================================
# Script definitions
# =============================================================================
run_script() {
    local script_name="$1"
    shift  # Remove script name from arguments
    
    echo -e "${BLUE}🚀 Running script: ${PURPLE}$script_name${NC}"
    echo "=================================================="
    
    case "$script_name" in
        # Code Quality Scripts
        "lint")
            echo -e "${YELLOW}🔍 Running flake8 linting...${NC}"
            flake8 . --count --statistics
            ;;
        "lint:fix")
            echo -e "${YELLOW}🔧 Running auto-fixes (isort + black)...${NC}"
            isort .
            black .
            echo -e "${GREEN}✅ Auto-fixes applied${NC}"
            ;;
        "format")
            echo -e "${YELLOW}🎨 Formatting code with black...${NC}"
            black .
            ;;
        "format:check")
            echo -e "${YELLOW}🎨 Checking code formatting...${NC}"
            black --check --diff .
            ;;
        "imports")
            echo -e "${YELLOW}📦 Sorting imports with isort...${NC}"
            isort .
            ;;
        "imports:check")
            echo -e "${YELLOW}📦 Checking import sorting...${NC}"
            isort --check-only --diff .
            ;;
        "quality")
            echo -e "${YELLOW}🔍 Running all quality checks...${NC}"
            echo -e "\n${BLUE}1/3 Import sorting...${NC}"
            isort --check-only --diff . || (echo -e "${YELLOW}Auto-fixing...${NC}" && isort .)
            echo -e "\n${BLUE}2/3 Code formatting...${NC}"
            black --check --diff . || (echo -e "${YELLOW}Auto-fixing...${NC}" && black .)
            echo -e "\n${BLUE}3/3 Linting...${NC}"
            flake8 . --count --statistics
            echo -e "\n${GREEN}✅ All quality checks completed${NC}"
            ;;
            
        # Git Operations
        "push")
            echo -e "${YELLOW}🚀 Git push with quality checks...${NC}"
            ./scripts/git-push.sh "$@"
            ;;
        "push:force")
            echo -e "${YELLOW}🚀 Force git push with quality checks...${NC}"
            ./scripts/git-push.sh --force "$@"
            ;;
        "push:skip")
            echo -e "${YELLOW}🚀 Git push without quality checks...${NC}"
            ./scripts/git-push.sh --skip-checks "$@"
            ;;
            
        # Testing Scripts
        "test")
            echo -e "${YELLOW}🧪 Running tests...${NC}"
            if command -v pytest &> /dev/null; then
                pytest tests/ -v
            else
                echo -e "${RED}❌ pytest not installed${NC}"
                echo -e "${YELLOW}💡 Install with: pip install pytest${NC}"
                exit 1
            fi
            ;;
        "test:watch")
            echo -e "${YELLOW}🧪 Running tests in watch mode...${NC}"
            if command -v pytest &> /dev/null; then
                pytest-watch tests/ -- -v
            else
                echo -e "${RED}❌ pytest-watch not installed${NC}"
                echo -e "${YELLOW}💡 Install with: pip install pytest-watch${NC}"
                exit 1
            fi
            ;;
        "test:coverage")
            echo -e "${YELLOW}🧪 Running tests with coverage...${NC}"
            if command -v pytest &> /dev/null; then
                pytest tests/ --cov=. --cov-report=html --cov-report=term-missing
            else
                echo -e "${RED}❌ pytest not installed${NC}"
                echo -e "${YELLOW}💡 Install with: pip install pytest pytest-cov${NC}"
                exit 1
            fi
            ;;
            
        # CI/CD Scripts
        "ci")
            echo -e "${YELLOW}🔄 Running full CI/CD pipeline...${NC}"
            if [ -f "scripts/ci/run_cicd_pipeline.py" ]; then
                python scripts/ci/run_cicd_pipeline.py
            else
                echo -e "${RED}❌ CI/CD pipeline script not found${NC}"
                exit 1
            fi
            ;;
        "ci:validate")
            echo -e "${YELLOW}🔍 Validating CI/CD configuration...${NC}"
            if [ -f "scripts/ci/validate_ci_cd_operations.py" ]; then
                python scripts/ci/validate_ci_cd_operations.py
            else
                echo -e "${RED}❌ CI/CD validation script not found${NC}"
                exit 1
            fi
            ;;
        "build")
            echo -e "${YELLOW}🏗️  Building Docker image...${NC}"
            if [ -f "Dockerfile" ]; then
                docker build -t bird-bone-ai .
            else
                echo -e "${RED}❌ Dockerfile not found${NC}"
                exit 1
            fi
            ;;
        "deploy")
            echo -e "${YELLOW}🚀 Deploying application...${NC}"
            if [ -f "docker-compose.yml" ]; then
                docker-compose up -d
            else
                echo -e "${RED}❌ docker-compose.yml not found${NC}"
                exit 1
            fi
            ;;
            
        # Development Scripts
        "dev")
            echo -e "${YELLOW}🔧 Starting development server...${NC}"
            # Add your development server command here
            echo -e "${BLUE}💡 Configure your development server in scripts/run.sh${NC}"
            ;;
        "install")
            echo -e "${YELLOW}📦 Installing dependencies...${NC}"
            if [ -f "requirements.txt" ]; then
                pip install -r requirements.txt
            fi
            if [ -f "requirements-dev.txt" ]; then
                pip install -r requirements-dev.txt
            fi
            echo -e "${GREEN}✅ Dependencies installed${NC}"
            ;;
        "clean")
            echo -e "${YELLOW}🧹 Cleaning build artifacts...${NC}"
            find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
            find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
            find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
            find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
            echo -e "${GREEN}✅ Cleaned build artifacts${NC}"
            ;;
            
        # Help
        "help"|"--help"|"-h")
            show_help
            ;;
            
        # Unknown script
        *)
            echo -e "${RED}❌ Unknown script: $script_name${NC}"
            echo -e "${YELLOW}💡 Use './scripts/run.sh help' to see available scripts${NC}"
            exit 1
            ;;
    esac
}

# =============================================================================
# Main execution
# =============================================================================
if [ $# -eq 0 ]; then
    echo -e "${RED}❌ No script specified${NC}"
    echo -e "${YELLOW}💡 Use './scripts/run.sh help' to see available scripts${NC}"
    exit 1
fi

# Run the specified script
run_script "$@"

echo -e "\n${GREEN}✅ Script completed successfully!${NC}"
