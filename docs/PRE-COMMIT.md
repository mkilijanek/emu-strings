# Pre-commit Hooks

Pre-commit hooks help maintain code quality by running checks before each commit.

## Installation

```bash
pip install pre-commit
pre-commit install
pre-commit install --hook-type commit-msg
```

## Hooks Included

### Python
- **black** - Code formatting
- **flake8** - Linting
- **isort** - Import sorting
- **bandit** - Security scanning

### JavaScript
- **prettier** - Code formatting

### General
- **trailing-whitespace** - Remove trailing whitespace
- **end-of-file-fixer** - Ensure files end with newline
- **check-yaml** - Validate YAML syntax
- **check-json** - Validate JSON syntax
- **check-added-large-files** - Prevent large files (>1MB)
- **detect-private-key** - Detect private keys

### Docker
- **hadolint** - Dockerfile linting

### Shell
- **shellcheck** - Shell script analysis

### Git
- **commitizen** - Commit message format checking

## Running Hooks

### Before Commit (Automatic)
Hooks run automatically on `git commit`.

### Manual Run
```bash
# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files

# Run on staged files only
pre-commit run
```

## Skip Hooks

In emergency situations:
```bash
git commit --no-verify -m "Your message"
```

**Note**: Skipping hooks should be rare and justified.

## Updating Hooks

```bash
pre-commit autoupdate
```

## Troubleshooting

### Hook fails but code looks correct
- Run `pre-commit run --all-files` to see full output
- Check the hook's specific configuration in `.pre-commit-config.yaml`

### Performance issues
- Hooks only run on changed files by default
- Use `pre-commit run --all-files` sparingly
- Consider using `pre-commit run <hook-id>` for specific hooks

## Configuration

Hook configuration is in `.pre-commit-config.yaml`.

Python tool configurations are in `pyproject.toml`.

Prettier configuration is in `.prettierrc`.
