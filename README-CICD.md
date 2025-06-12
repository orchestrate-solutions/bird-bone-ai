# 🚀 CI/CD Pipeline with Automated Code Quality

This repository features a comprehensive CI/CD pipeline that automatically enforces code quality standards and can auto-fix common issues.

## 🎯 Quick Start

### For New Contributors

1. **Clone the repository**
2. **Run the setup script:**
   ```bash
   ./scripts/setup-quality-enforcement.sh
   ```
3. **Start developing** - quality checks will run automatically!

### For Daily Development

Use these commands instead of regular git:

```bash
# Instead of: git push
./scripts/git-push.sh

# Check code quality anytime
./scripts/run.sh quality

# Auto-fix formatting issues
./scripts/run.sh lint:fix
```

## 🤖 What Happens Automatically

### ✅ Local Enforcement (Pre-push Hook)

When you push code, the system automatically:

1. **Sorts imports** with `isort` (auto-fixes)
2. **Formats code** with `black` (auto-fixes)
3. **Checks critical linting** with `flake8` (blocks if errors)
4. **Stages auto-fixes** and prompts for commit

### ✅ CI/CD Enforcement (GitHub Actions)

When code reaches GitHub, the pipeline:

1. **Runs the same quality checks**
2. **Auto-fixes** import and formatting issues
3. **Creates Pull Requests** with fixes (if needed)
4. **Blocks deployment** on critical linting errors
5. **Continues pipeline** only after quality passes

### ✅ VS Code Integration

With the setup script, VS Code will:

1. **Auto-format on save** with `black`
2. **Auto-sort imports** on save with `isort`
3. **Show linting errors** in real-time
4. **Provide tasks** for quality checks

## 🛡️ Quality Standards Enforced

| Check | Tool | Auto-Fix | Blocking | Purpose |
|-------|------|----------|----------|---------|
| **Import Sorting** | `isort` | ✅ Yes | ❌ No | Consistent import organization |
| **Code Formatting** | `black` | ✅ Yes | ❌ No | Consistent code style |
| **Critical Linting** | `flake8` | ❌ No | ✅ Yes | Prevent syntax/logic errors |

### Critical Errors (Pipeline Blockers)

These errors **will fail** the CI/CD pipeline and must be fixed manually:

- **E9**: Syntax errors
- **F63**: Invalid syntax in type annotations
- **F7**: Logic errors (undefined variables, etc.)
- **F82**: Undefined names

## 📋 Available Scripts

The `scripts/run.sh` provides npm-style commands:

### Code Quality
```bash
./scripts/run.sh quality      # Run all quality checks
./scripts/run.sh lint         # Run linting only
./scripts/run.sh lint:fix     # Auto-fix linting issues
./scripts/run.sh format       # Format code with black
./scripts/run.sh imports      # Sort imports with isort
```

### Git Operations
```bash
./scripts/git-push.sh                    # Push with quality checks
./scripts/git-push.sh --force            # Force push with checks
./scripts/git-push.sh --skip-checks      # Skip checks (not recommended)
```

### Testing & CI/CD
```bash
./scripts/run.sh test         # Run tests
./scripts/run.sh test:coverage # Run tests with coverage
./scripts/run.sh ci           # Run full CI/CD pipeline locally
./scripts/run.sh build        # Build Docker image
```

## 🔄 Workflow Examples

### Normal Development Flow

```bash
# 1. Write your code
vim my_module.py

# 2. Check quality (optional - will happen on push anyway)
./scripts/run.sh quality

# 3. Commit your changes
git add .
git commit -m "feat: add new feature"

# 4. Push with automatic quality checks
./scripts/git-push.sh origin feature-branch
```

### When Quality Issues Are Found

```bash
# The push script will:
# 1. Auto-fix import sorting
# 2. Auto-fix code formatting  
# 3. Stage the fixes
# 4. Ask if you want to commit them

# If you accept, it will:
# 5. Commit the fixes automatically
# 6. Continue with the push
```

### CI/CD Auto-Fix Flow

```bash
# If you push code with quality issues:
git push origin main

# The CI/CD pipeline will:
# 1. Detect quality issues
# 2. Auto-fix what it can
# 3. Create a Pull Request with fixes
# 4. Continue the pipeline with clean code
```

## 🚫 Emergency Override (Not Recommended)

For critical hotfixes only:

```bash
# Skip local pre-push checks
git push --no-verify

# Skip quality checks in our script
./scripts/git-push.sh --skip-checks

# Note: CI/CD will still enforce quality
```

## 📊 Monitoring Code Quality

### GitHub Actions Dashboard

- **Actions Tab**: View pipeline execution status
- **Pull Requests**: See automated quality reports
- **Commit Status**: See pass/fail indicators

### VS Code Integration

- **Problems Panel**: Real-time linting feedback
- **Status Bar**: Format/lint status indicators
- **Command Palette**: Run quality tasks

## 🎯 Benefits for Your Project

### For Developers
- ✅ **No more style debates** - automated formatting
- ✅ **Catch errors early** - pre-push validation
- ✅ **Save review time** - auto-fixed PRs
- ✅ **Consistent codebase** - enforced standards

### For Maintainers
- ✅ **Reduced review burden** - focus on logic, not style
- ✅ **Prevent broken builds** - critical error blocking
- ✅ **Automated compliance** - no manual enforcement needed
- ✅ **Quality metrics** - track improvements over time

## 🛠️ Configuration

### Customizing Quality Standards

Edit these files to adjust standards:

- **`.flake8`** - Linting rules and line length
- **`pyproject.toml`** - Black and isort configuration
- **`.github/workflows/ci.yml`** - CI/CD pipeline settings

### Adding New Checks

To add new quality checks:

1. **Add the tool** to `requirements.txt`
2. **Update** `scripts/run.sh` with new commands
3. **Modify** the CI/CD pipeline in `.github/workflows/ci.yml`
4. **Update** the pre-push hook in `scripts/pre-push.sh`

## 🆘 Troubleshooting

### Setup Issues

```bash
# Reinstall pre-push hook
cp scripts/pre-push.sh .git/hooks/pre-push
chmod +x .git/hooks/pre-push

# Verify script permissions
chmod +x scripts/*.sh

# Check dependencies
pip install black isort flake8
```

### VS Code Issues

1. **Install Python extension**
2. **Check settings.json** was created in `.vscode/`
3. **Restart VS Code** after setup
4. **Verify Python interpreter** is correctly set

### CI/CD Issues

1. **Check Actions tab** for detailed error logs
2. **Review auto-generated PRs** for fix suggestions
3. **Fix critical errors manually** (E9, F63, F7, F82)

## 📚 Documentation

- [Automated Code Quality Enforcement](docs/automated-code-quality-enforcement.md) - Complete guide
- [Git Push Implementation](docs/git-push-implementation-summary.md) - Technical details
- [Git Push Quality Checks](docs/git-push-quality-checks.md) - Quality check details

---

## 🚀 Ready to Contribute?

1. **Run setup:** `./scripts/setup-quality-enforcement.sh`
2. **Start coding** with automatic quality enforcement
3. **Use git-push script** instead of regular git push
4. **Let the automation handle** the rest!

The system is designed to be **helpful, not intrusive** - it catches issues early and fixes what it can automatically, so you can focus on building great features! 🎉
