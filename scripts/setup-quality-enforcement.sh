#!/bin/bash

# =============================================================================
# Setup Automated Code Quality Enforcement
# =============================================================================
# This script sets up both local and CI/CD automated code quality enforcement
# Run this once to configure your development environment
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

echo -e "${BLUE}🚀 Setting up Automated Code Quality Enforcement${NC}"
echo "=============================================================="
echo -e "${BLUE}Project:${NC} Bird-Bone AI"
echo -e "${BLUE}Directory:${NC} $PROJECT_ROOT"
echo "=============================================================="

# =============================================================================
# 1. Install Required Dependencies
# =============================================================================
echo -e "\n${PURPLE}📦 Installing Code Quality Dependencies${NC}"
echo "--------------------------------------------------------------"

if command -v pip &> /dev/null; then
    echo -e "${BLUE}Installing Python code quality tools...${NC}"
    pip install black isort flake8 pytest pytest-cov
    echo -e "${GREEN}✅ Python tools installed${NC}"
else
    echo -e "${RED}❌ pip not found. Please install Python and pip first.${NC}"
    exit 1
fi

# =============================================================================
# 2. Setup Git Hooks
# =============================================================================
echo -e "\n${PURPLE}🪝 Setting up Git Hooks${NC}"
echo "--------------------------------------------------------------"

# Make sure scripts are executable
chmod +x scripts/pre-push.sh
chmod +x scripts/git-push.sh
chmod +x scripts/run.sh

# Install pre-push hook
if [ -f ".git/hooks/pre-push" ]; then
    echo -e "${YELLOW}⚠️  Existing pre-push hook found. Backing up...${NC}"
    mv .git/hooks/pre-push .git/hooks/pre-push.backup.$(date +%Y%m%d_%H%M%S)
fi

cp scripts/pre-push.sh .git/hooks/pre-push
chmod +x .git/hooks/pre-push
echo -e "${GREEN}✅ Pre-push hook installed${NC}"

# =============================================================================
# 3. Setup VS Code Integration (Optional)
# =============================================================================
echo -e "\n${PURPLE}🔧 Setting up VS Code Integration${NC}"
echo "--------------------------------------------------------------"

if [ ! -d ".vscode" ]; then
    mkdir -p .vscode
fi

# Create settings.json for VS Code
cat > .vscode/settings.json << 'EOF'
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.flake8Args": [
        "--max-line-length=88",
        "--select=E9,F63,F7,F82"
    ],
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": [
        "--line-length=88"
    ],
    "python.sortImports.args": [
        "--profile=black"
    ],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "files.trimTrailingWhitespace": true,
    "files.insertFinalNewline": true
}
EOF

# Create tasks.json for VS Code
cat > .vscode/tasks.json << 'EOF'
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Quality Check",
            "type": "shell",
            "command": "./scripts/run.sh",
            "args": ["quality"],
            "group": "test",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            },
            "problemMatcher": []
        },
        {
            "label": "Format Code",
            "type": "shell", 
            "command": "./scripts/run.sh",
            "args": ["lint:fix"],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            }
        },
        {
            "label": "Git Push with Quality Checks",
            "type": "shell",
            "command": "./scripts/git-push.sh",
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            }
        }
    ]
}
EOF

echo -e "${GREEN}✅ VS Code configuration created${NC}"

# =============================================================================
# 4. Create npm-style package.json (Optional)
# =============================================================================
echo -e "\n${PURPLE}📋 Creating npm-style Scripts Configuration${NC}"
echo "--------------------------------------------------------------"

cat > scripts.json << 'EOF'
{
  "scripts": {
    "lint": "./scripts/run.sh lint",
    "lint:fix": "./scripts/run.sh lint:fix", 
    "format": "./scripts/run.sh format",
    "format:check": "./scripts/run.sh format:check",
    "imports": "./scripts/run.sh imports",
    "imports:check": "./scripts/run.sh imports:check",
    "quality": "./scripts/run.sh quality",
    "test": "./scripts/run.sh test",
    "test:coverage": "./scripts/run.sh test:coverage",
    "push": "./scripts/git-push.sh",
    "push:force": "./scripts/git-push.sh --force",
    "push:skip": "./scripts/git-push.sh --skip-checks",
    "ci": "./scripts/run.sh ci",
    "build": "./scripts/run.sh build",
    "clean": "./scripts/run.sh clean"
  },
  "description": "NPM-style scripts for Python development workflow"
}
EOF

echo -e "${GREEN}✅ Scripts configuration created${NC}"

# =============================================================================
# 5. Test the Setup
# =============================================================================
echo -e "\n${PURPLE}🧪 Testing Code Quality Setup${NC}"
echo "--------------------------------------------------------------"

echo -e "${BLUE}Running initial quality check...${NC}"
if ./scripts/run.sh quality; then
    echo -e "${GREEN}✅ Quality check passed!${NC}"
else
    echo -e "${YELLOW}⚠️  Quality issues found (will be auto-fixed in CI/CD)${NC}"
fi

# =============================================================================
# 6. Summary and Instructions
# =============================================================================
echo -e "\n${GREEN}🎉 Setup Complete!${NC}"
echo "=============================================================="
echo -e "${BLUE}Automated Code Quality Enforcement is now active!${NC}"
echo ""
echo -e "${YELLOW}📋 What was configured:${NC}"
echo -e "   ✅ Git pre-push hooks (auto-fix on push)"
echo -e "   ✅ VS Code integration (format on save)"
echo -e "   ✅ NPM-style scripts (./scripts/run.sh)"
echo -e "   ✅ CI/CD pipeline (auto-fix and PR creation)"
echo ""
echo -e "${YELLOW}🚀 Available Commands:${NC}"
echo -e "   ${BLUE}./scripts/run.sh quality${NC}     - Run all quality checks"
echo -e "   ${BLUE}./scripts/run.sh lint:fix${NC}    - Auto-fix linting issues"
echo -e "   ${BLUE}./scripts/git-push.sh${NC}        - Git push with quality checks"
echo -e "   ${BLUE}./scripts/run.sh test${NC}        - Run tests"
echo ""
echo -e "${YELLOW}🛡️  Enforcement Levels:${NC}"
echo -e "   ${GREEN}✅ Local:${NC} Pre-push hooks catch issues before remote push"
echo -e "   ${GREEN}✅ CI/CD:${NC} GitHub Actions auto-fix and create PRs"
echo -e "   ${GREEN}✅ Blocking:${NC} Critical linting errors block the pipeline"
echo ""
echo -e "${YELLOW}💡 Pro Tips:${NC}"
echo -e "   • Use ${BLUE}./scripts/git-push.sh${NC} instead of ${BLUE}git push${NC}"
echo -e "   • Run ${BLUE}./scripts/run.sh quality${NC} before committing"
echo -e "   • CI/CD will automatically create PRs for fixes"
echo -e "   • VS Code will auto-format on save"
echo ""
echo -e "${PURPLE}🎯 Code Quality Standards Enforced:${NC}"
echo -e "   1. 🔍 Import sorting (isort) - Auto-fixed"
echo -e "   2. 🎨 Code formatting (black) - Auto-fixed"  
echo -e "   3. 🚨 Critical linting (flake8) - Blocking"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
