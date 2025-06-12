# Git Push Script with Enforced Code Quality Checks

This document explains the npm-style git workflow scripts that enforce code quality checks before pushing to remote repositories.

## 🚀 Quick Start

### Git Push with Quality Checks
```bash
# Simple push with quality checks
./scripts/git-push.sh

# Push to specific remote/branch
./scripts/git-push.sh origin feature-branch

# Force push with quality checks
./scripts/git-push.sh --force origin main

# Skip quality checks (not recommended)
./scripts/git-push.sh --skip-checks
```

### NPM-Style Script Runner
```bash
# Run all quality checks
./scripts/run.sh quality

# Lint with auto-fixes
./scripts/run.sh lint:fix

# Git push with quality checks
./scripts/run.sh push origin main

# See all available scripts
./scripts/run.sh help
```

## 📋 Available Scripts

### Code Quality Scripts
- `./scripts/run.sh lint` - Run flake8 linting
- `./scripts/run.sh lint:fix` - Auto-fix imports and formatting
- `./scripts/run.sh format` - Format code with black
- `./scripts/run.sh format:check` - Check formatting without changes
- `./scripts/run.sh imports` - Sort imports with isort
- `./scripts/run.sh imports:check` - Check import sorting
- `./scripts/run.sh quality` - Run all quality checks with auto-fixes

### Git Operations
- `./scripts/run.sh push` - Git push with quality checks
- `./scripts/run.sh push:force` - Force push with quality checks
- `./scripts/run.sh push:skip` - Push without quality checks (not recommended)

### Testing Scripts
- `./scripts/run.sh test` - Run all tests with pytest
- `./scripts/run.sh test:watch` - Run tests in watch mode
- `./scripts/run.sh test:coverage` - Run tests with coverage report

### CI/CD Operations
- `./scripts/run.sh ci` - Run full CI/CD pipeline locally
- `./scripts/run.sh build` - Build Docker image
- `./scripts/run.sh deploy` - Deploy with docker-compose

## 🔧 Code Quality Enforcement

### 3 Mandatory Checks

1. **Import Sorting (isort)** ✅ Auto-fix enabled
   - Automatically sorts Python imports
   - Fixes applied and staged automatically
   - Zero configuration required

2. **Code Formatting (black)** ✅ Auto-fix enabled
   - Enforces consistent code style
   - Fixes applied and staged automatically
   - 88-character line length (black default)

3. **Critical Linting (flake8)** ❌ Manual fix required
   - Blocks push on critical errors:
     - `E9`: Syntax errors
     - `F63`: Invalid syntax in type annotations  
     - `F7`: Logic errors
     - `F82`: Undefined names
   - Style warnings are non-blocking

### What Happens During Push

```
🔍 Running mandatory code quality checks...
==================================================

1/3 Import Sorting Check (isort)
🔧 Auto-fixing import sorting...
✅ Import sorting fixed automatically
📝 Staged import sorting fixes

2/3 Code Formatting Check (black)  
🔧 Auto-fixing code formatting...
✅ Code formatting fixed automatically
📝 Staged formatting fixes

3/3 Critical Linting Check (flake8)
✅ Critical linting (flake8) passed

==================================================
🎉 All code quality checks passed!

🚀 Executing git push...
```

## 🎯 Key Features

### Automatic Fixes
- **Auto-commits available**: The script can automatically commit formatting fixes
- **Staging**: All fixes are automatically staged
- **Interactive prompts**: Option to commit auto-fixes before pushing

### Git Integration
- **Pre-push hook**: Installed in `.git/hooks/pre-push`
- **Branch detection**: Automatically detects current branch
- **Remote validation**: Checks remote repository access
- **Force push support**: `--force` flag support with safety checks

### Error Handling
- **Detailed error messages**: Clear explanations of what went wrong
- **Exit codes**: Proper exit codes for CI/CD integration  
- **Colored output**: Visual indicators for success/failure/warnings
- **Troubleshooting hints**: Helpful suggestions when pushes fail

## 🛡️ Security & Safety

### Critical Error Blocking
The following errors will **block your push**:
- Syntax errors that would break the code
- Undefined variables that would cause runtime errors
- Type annotation syntax errors
- Logic errors in code flow

### Non-Blocking Warnings
These are reported but **won't block your push**:
- Line length violations (E501)
- Unused imports (F401) 
- Missing docstrings
- Other style issues

### Override Options
```bash
# Skip all quality checks (emergency use only)
./scripts/git-push.sh --skip-checks

# Or use standard git push to bypass entirely
git push origin main
```

## 🔄 Git Hooks

### Pre-push Hook Installed
The script automatically installs a pre-push hook that:
- Runs on every `git push` command
- Applies the same quality checks
- Can be bypassed with `git push --no-verify`

### Hook Location
- **File**: `.git/hooks/pre-push`
- **Source**: `scripts/pre-push.sh` (copied during installation)
- **Permissions**: Executable

## 🎨 NPM-Style Workflow

### Familiar Commands
If you're used to npm scripts, these commands will feel natural:

```bash
# Similar to npm run lint
./scripts/run.sh lint

# Similar to npm run lint:fix  
./scripts/run.sh lint:fix

# Similar to npm run test
./scripts/run.sh test

# Similar to npm run build
./scripts/run.sh build
```

### Script Categories
- **Code Quality**: `lint`, `format`, `imports`, `quality`
- **Git Operations**: `push`, `push:force`, `push:skip`
- **Testing**: `test`, `test:watch`, `test:coverage`
- **CI/CD**: `ci`, `build`, `deploy`
- **Development**: `dev`, `install`, `clean`

## 📖 Examples

### Daily Development Workflow
```bash
# 1. Make your changes
git add .
git commit -m "feat: add new feature"

# 2. Push with automatic quality checks
./scripts/git-push.sh

# 3. Or use the npm-style runner
./scripts/run.sh push
```

### Quality Check Workflow
```bash
# Check code quality before committing
./scripts/run.sh quality

# Fix any issues automatically
./scripts/run.sh lint:fix

# Run tests to make sure everything works
./scripts/run.sh test
```

### CI/CD Workflow
```bash
# Test the full CI/CD pipeline locally
./scripts/run.sh ci

# Build and deploy locally
./scripts/run.sh build
./scripts/run.sh deploy
```

## 🚨 Troubleshooting

### Push Fails Due to Critical Errors
```bash
# See the specific errors
flake8 . --select=E9,F63,F7,F82

# Fix the errors manually
# Then try pushing again
./scripts/git-push.sh
```

### Auto-fixes Not Applied
```bash
# Run fixes manually
./scripts/run.sh lint:fix

# Check what changed
git diff

# Commit the fixes
git add .
git commit -m "style: auto-fix code formatting"
```

### Hook Not Working
```bash
# Reinstall the pre-push hook
cp scripts/pre-push.sh .git/hooks/pre-push
chmod +x .git/hooks/pre-push
```

## 💡 Best Practices

1. **Run quality checks early**: Use `./scripts/run.sh quality` before committing
2. **Let auto-fixes work**: Don't manually format what isort/black can fix
3. **Fix critical errors immediately**: Don't let E9,F63,F7,F82 errors accumulate
4. **Use the npm-style runner**: It's more convenient than remembering exact commands
5. **Test locally**: Use `./scripts/run.sh ci` to test before pushing

## 🔗 Integration

### VS Code Integration
Add to your VS Code `settings.json`:
```json
{
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.sortImports.provider": "isort",
  "editor.formatOnSave": true
}
```

### CI/CD Integration  
The same quality checks run in GitHub Actions:
- Import sorting validation
- Code formatting validation  
- Full linting with flake8
- Test execution
- Security scanning

## 📚 References

- **Black**: https://black.readthedocs.io/
- **isort**: https://pycqa.github.io/isort/
- **flake8**: https://flake8.pycqa.org/
- **pytest**: https://docs.pytest.org/

---

**🎉 Happy coding with enforced quality!** This system ensures your code meets high standards before reaching the remote repository.
