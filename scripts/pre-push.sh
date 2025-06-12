#!/bin/bash

# =============================================================================
# Git Pre-Push Hook Script for Bird-Bone AI
# =============================================================================
# This script runs code quality checks before pushing to ensure CI/CD success
# Similar to npm's pre-commit hooks, but for git push operations
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}🔍 Running pre-push code quality checks...${NC}"
echo "=================================================="

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2 passed${NC}"
    else
        echo -e "${RED}❌ $2 failed${NC}"
        return 1
    fi
}

# Function to run a command with error handling
run_check() {
    local check_name="$1"
    local command="$2"
    local auto_fix="$3"

    echo -e "\n${YELLOW}🔧 Running $check_name...${NC}"

    if eval "$command"; then
        print_status 0 "$check_name"
        return 0
    else
        if [ "$auto_fix" = "true" ]; then
            echo -e "${YELLOW}⚠️  $check_name failed, attempting auto-fix...${NC}"
            return 1
        else
            print_status 1 "$check_name"
            return 1
        fi
    fi
}

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}❌ Not in a git repository${NC}"
    exit 1
fi

# Check if there are staged changes
if git diff --cached --quiet; then
    echo -e "${YELLOW}⚠️  No staged changes found. Checking working directory...${NC}"
    if git diff --quiet; then
        echo -e "${YELLOW}ℹ️  No changes to check. Proceeding with push...${NC}"
        exit 0
    fi
fi

echo -e "${BLUE}📁 Working directory: $PROJECT_ROOT${NC}"

# =============================================================================
# 1. Import Sorting with isort (SKIPPED)
# =============================================================================
echo -e "\n${BLUE}1/4 Import Sorting Check${NC}"
echo -e "${YELLOW}⚠️  Import sorting check skipped: isort is no longer used in this project${NC}"
# SKIP isort: isort is no longer used in this project
# if ! run_check "isort" "isort --check-only --diff ."; then
#     echo -e "${YELLOW}🔧 Auto-fixing import sorting...${NC}"
#     if isort .; then
#         echo -e "${GREEN}✅ Import sorting fixed automatically${NC}"
#         # Stage the changes
#         git add -A
#         echo -e "${BLUE}📝 Staged import sorting fixes${NC}"
#     else
#         echo -e "${RED}❌ Failed to auto-fix import sorting${NC}"
#         exit 1
#     fi
# fi

# =============================================================================
# 2. Code Formatting with black
# =============================================================================
echo -e "\n${BLUE}2/4 Code Formatting Check${NC}"
if ! run_check "black" "black --check --diff ."; then
    echo -e "${YELLOW}🔧 Auto-fixing code formatting...${NC}"
    if black .; then
        echo -e "${GREEN}✅ Code formatting fixed automatically${NC}"
        # Stage the changes
        git add -A
        echo -e "${BLUE}📝 Staged formatting fixes${NC}"
    else
        echo -e "${RED}❌ Failed to auto-fix code formatting${NC}"
        exit 1
    fi
fi

# =============================================================================
# 3. Linting with flake8 (Critical Errors Only)
# =============================================================================
echo -e "\n${BLUE}3/4 Critical Linting Check${NC}"
if ! run_check "flake8 (critical)" "flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics"; then
    echo -e "${RED}❌ Critical linting errors found. These must be fixed manually:${NC}"
    echo -e "${RED}   - E9: Syntax errors${NC}"
    echo -e "${RED}   - F63: Invalid syntax in type annotations${NC}"
    echo -e "${RED}   - F7: Logic errors${NC}"
    echo -e "${RED}   - F82: Undefined names${NC}"
    echo -e "\n${YELLOW}💡 Run 'flake8 . --select=E9,F63,F7,F82' to see details${NC}"
    exit 1
fi

# =============================================================================
# 4. Full Linting Report (Non-blocking)
# =============================================================================
echo -e "\n${BLUE}4/4 Full Linting Report${NC}"
echo -e "${YELLOW}📊 Running full linting check (warnings only)...${NC}"
if flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics; then
    echo -e "${GREEN}✅ Full linting check completed${NC}"
else
    echo -e "${YELLOW}⚠️  Style warnings found (non-blocking)${NC}"
fi

# =============================================================================
# 5. Optional: Run tests (uncomment to enable)
# =============================================================================
# echo -e "\n${BLUE}5/5 Quick Test Check${NC}"
# if command -v pytest &> /dev/null; then
#     if ! run_check "pytest" "pytest tests/ -v --tb=short"; then
#         echo -e "${RED}❌ Tests failed. Push aborted.${NC}"
#         exit 1
#     fi
# else
#     echo -e "${YELLOW}⚠️  pytest not found, skipping tests${NC}"
# fi

# =============================================================================
# Final Status
# =============================================================================
echo -e "\n=================================================="
echo -e "${GREEN}🎉 All pre-push checks passed!${NC}"
echo -e "${BLUE}🚀 Ready to push to remote repository${NC}"

# Check if there were any auto-fixes
if ! git diff --cached --quiet; then
    echo -e "\n${YELLOW}📝 Auto-fixes were applied and staged:${NC}"
    git diff --cached --name-only | sed 's/^/  - /'
    echo -e "\n${BLUE}💡 These changes will be included in your next commit${NC}"
    echo -e "${YELLOW}⚠️  Consider committing these fixes before pushing${NC}"
fi

echo -e "\n${GREEN}✅ Pre-push validation completed successfully!${NC}"
exit 0
