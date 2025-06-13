#!/bin/bash

# =============================================================================
# Git Push Script with Enforced Code Quality Checks
# =============================================================================
# This script runs black for formatting and ruff for linting before pushing
# =============================================================================

set -e  # Exit on any error

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

# Default values
REMOTE="origin"
BRANCH=""
FORCE_FLAG=""
SKIP_CHECKS=false

# =============================================================================
# Help function
# =============================================================================
show_help() {
    cat << EOF
${BLUE}Git Push Script with Code Quality Enforcement${NC}

${YELLOW}USAGE:${NC}
    ./scripts/git-push.sh [options] [remote] [branch]

${YELLOW}OPTIONS:${NC}
    -h, --help          Show this help message
    -f, --force         Force push (adds --force flag to git push)
    -s, --skip-checks   Skip code quality checks (not recommended)
    --set-upstream      Set upstream branch (adds -u flag to git push)

${YELLOW}EXAMPLES:${NC}
    ./scripts/git-push.sh                           # Push current branch to origin
    ./scripts/git-push.sh upstream feature-branch   # Push feature-branch to upstream
    ./scripts/git-push.sh -f origin main            # Force push main to origin
    ./scripts/git-push.sh --set-upstream origin new-feature  # Push and set upstream

${YELLOW}CODE QUALITY CHECKS:${NC}
    1. ${GREEN}black${NC}  - Code formatting (auto-fix enabled)
    2. ${GREEN}ruff${NC}   - Linting and import sorting (blocking on errors)

${PURPLE}💡 This script ensures your code meets quality standards before pushing!${NC}
EOF
}

# =============================================================================
# Parse command line arguments
# =============================================================================
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -f|--force)
            FORCE_FLAG="--force"
            shift
            ;;
        -s|--skip-checks)
            SKIP_CHECKS=true
            shift
            ;;
        --set-upstream)
            SET_UPSTREAM="-u"
            shift
            ;;
        -*)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            echo -e "${YELLOW}💡 Use --help to see available options${NC}"
            exit 1
            ;;
        *)
            if [ -z "$REMOTE" ] || [ "$REMOTE" = "origin" ]; then
                REMOTE="$1"
            elif [ -z "$BRANCH" ]; then
                BRANCH="$1"
            else
                echo -e "${RED}❌ Too many arguments${NC}"
                echo -e "${YELLOW}💡 Use --help to see usage${NC}"
                exit 1
            fi
            shift
            ;;
    esac
done

# =============================================================================
# Determine current branch if not specified
# =============================================================================
if [ -z "$BRANCH" ]; then
    BRANCH=$(git branch --show-current)
    if [ -z "$BRANCH" ]; then
        echo -e "${RED}❌ Could not determine current branch${NC}"
        exit 1
    fi
fi

# =============================================================================
# Display push information
# =============================================================================
echo -e "${BLUE}🚀 Git Push with Code Quality Checks${NC}"
echo "=================================================="
echo -e "${BLUE}Remote:${NC} $REMOTE"
echo -e "${BLUE}Branch:${NC} $BRANCH"
if [ -n "$FORCE_FLAG" ]; then
    echo -e "${YELLOW}⚠️  Force push enabled${NC}"
fi
if [ -n "$SET_UPSTREAM" ]; then
    echo -e "${BLUE}🔗 Will set upstream branch${NC}"
fi
echo "=================================================="

# =============================================================================
# Check if we're in a git repository
# =============================================================================
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}❌ Not in a git repository${NC}"
    exit 1
fi

# =============================================================================
# Code Quality Checks (unless skipped)
# =============================================================================
if [ "$SKIP_CHECKS" = false ]; then
    echo -e "\n${PURPLE}🔍 Running mandatory code quality checks...${NC}"
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

    # =============================================================================
    # 1. Code Formatting with black
    # =============================================================================
    echo -e "\n${BLUE}1/2 Code Formatting Check (black)${NC}"
    if ! black --check --diff . >/dev/null 2>&1; then
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
    else
        print_status 0 "Code formatting (black)"
    fi

    # =============================================================================
    # 2. Linting and Import Sorting with ruff
    # =============================================================================
    echo -e "\n${BLUE}2/2 Linting Check (ruff)${NC}"
    # Run ruff with --show-files to display errors with source context directly.
    if ! ruff check --show-files .; then
        echo -e "\n${RED}❌ Linting errors found (see details above). These must be fixed manually.${NC}"
        echo -e "${RED}🚫 Push aborted due to linting errors${NC}"
        exit 1
    else
        print_status 0 "Linting (ruff)"
    fi

    echo -e "\n=================================================="
    echo -e "${GREEN}🎉 All code quality checks passed!${NC}"

    # Check if there were any auto-fixes
    if ! git diff --quiet; then
        echo -e "\n${YELLOW}📝 Auto-fixes were applied:${NC}"
        git diff --name-only | sed 's/^/  - /'
        echo -e "\n${BLUE}💡 These changes are ready to be committed${NC}"
        echo -e "${YELLOW}⚠️  Consider committing these fixes before pushing${NC}"

        # Ask user if they want to commit the fixes
        echo -e "\n${BLUE}❓ Do you want to commit these auto-fixes? (y/N)${NC}"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            git add -A
            git commit -m "style: auto-fix code formatting

- Apply black code formatting
- Automated by git-push script"
            echo -e "${GREEN}✅ Auto-fixes committed${NC}"
        else
            echo -e "${YELLOW}⚠️  Proceeding without committing auto-fixes${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⚠️  Skipping code quality checks (--skip-checks enabled)${NC}"
fi

# =============================================================================
# Git Push Operation
# =============================================================================
echo -e "\n${PURPLE}🚀 Executing git push...${NC}"
echo "=================================================="

# Build the git push command
PUSH_CMD="git push $SET_UPSTREAM $FORCE_FLAG $REMOTE $BRANCH"

echo -e "${BLUE}Command:${NC} $PUSH_CMD"
echo ""

# Execute the push
if eval "$PUSH_CMD"; then
    echo -e "\n${GREEN}🎉 Successfully pushed to $REMOTE/$BRANCH!${NC}"

    # Show the commit that was pushed
    COMMIT_HASH=$(git rev-parse HEAD)
    COMMIT_MESSAGE=$(git log -1 --pretty=format:"%s" HEAD)
    echo -e "${BLUE}📝 Pushed commit:${NC} ${COMMIT_HASH:0:8} - $COMMIT_MESSAGE"

    # Show remote URL
    REMOTE_URL=$(git remote get-url "$REMOTE" 2>/dev/null || echo "unknown")
    echo -e "${BLUE}🌐 Remote URL:${NC} $REMOTE_URL"

else
    echo -e "\n${RED}❌ Push failed!${NC}"
    echo -e "${YELLOW}💡 Common issues:${NC}"
    echo -e "   - Remote branch is ahead (try: git pull first)"
    echo -e "   - No permission to push to remote"
    echo -e "   - Network connectivity issues"
    echo -e "   - Branch protection rules"
    exit 1
fi

echo -e "\n${GREEN}✅ Git push completed successfully!${NC}"
