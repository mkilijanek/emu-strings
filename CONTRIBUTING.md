# Contributing to Emu-Strings

Thank you for your interest in contributing to emu-strings! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.9+
- Docker and Docker Compose
- Node.js (for frontend development)

### Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/emu-strings.git
   cd emu-strings
   ```

3. Install Python dependencies:
   ```bash
   cd src
   pip install -r requirements.txt
   pip install -r ../tests/requirements.txt
   ```

4. Install pre-commit hooks:
   ```bash
   pip install pre-commit
   pre-commit install
   pre-commit install --hook-type commit-msg
   ```

## Development Workflow

### Documentation-Driven Development (DDD)

We follow DDD principles:

1. **Document first**: Update or create documentation before implementing
2. **Test second**: Write tests that define the expected behavior
3. **Implement third**: Write the actual code
4. **Commit**: Each issue in a separate commit with proper message

### Running Tests

```bash
cd src
pytest ../tests/ -v
```

With coverage:

```bash
pytest ../tests/ --cov=emustrings --cov-report=html
```

### Code Style

We use:
- **black** for Python formatting
- **flake8** for Python linting
- **bandit** for security scanning
- **prettier** for JavaScript formatting

Check formatting:
```bash
black --check src/
```

Format code:
```bash
black src/
```

### Pre-commit Hooks

Pre-commit hooks run automatically on each commit:

```bash
pre-commit run --all-files
```

## Commit Message Format

Use conventional commits:

```
[TYPE] Brief description (#issue_number)

Detailed description of changes

- Change 1
- Change 2

Co-Authored-By: Name <email>
```

Types:
- `[SECURITY]` - Security fixes
- `[FEATURE]` - New features
- `[BUGFIX]` - Bug fixes
- `[OPS]` - Operations/Infrastructure
- `[DOCS]` - Documentation
- `[REFACTOR]` - Code refactoring
- `[TEST]` - Test changes

## Submitting Changes

1. Create a new branch:
   ```bash
   git checkout -b feature/issue-X-description
   ```

2. Make your changes following DDD

3. Commit with proper message

4. Push to your fork:
   ```bash
   git push origin feature/issue-X-description
   ```

5. Create a Pull Request

## Code Review

All submissions require review. The review process:

1. Automated checks must pass (CI/CD)
2. Code review by maintainers
3. Address feedback
4. Approval and merge

## Testing Guidelines

### Unit Tests

- Test one thing at a time
- Use descriptive test names
- Follow AAA pattern: Arrange, Act, Assert
- Mock external dependencies

```python
def test_sample_creation_with_valid_code():
    # Arrange
    code = b'var x = 1;'
    
    # Act
    sample = Sample(code, 'test.js')
    
    # Assert
    assert sample.name == 'test.js'
    assert len(sample.sha256) == 64
```

### Integration Tests

- Test complete workflows
- Use test containers for dependencies
- Clean up after tests

## Security

- Never commit secrets
- Report security vulnerabilities privately
- Follow security best practices
- Run bandit before committing

## Questions?

- Open an issue for questions
- Check existing documentation
- Review closed issues

Thank you for contributing!
