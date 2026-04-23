# Implementation Plan - Top 10 Issues

> Documentation-Driven Development (DDD)
> Created: 2026-04-23
> Status: In Progress

## Overview

This document outlines the implementation plan for addressing the top 10 highest-priority issues in the emu-strings project.

## Priority Matrix

| Priority | Issue | Category | Impact | Effort | Dependencies |
|----------|-------|----------|--------|--------|--------------|
| P0 | #3 Path traversal | Security | Critical | 2d | None |
| P0 | #2 MD5→SHA256 | Security | High | 1d | None |
| P0 | #1 Upload limits | Security | Critical | 2d | None |
| P1 | #4 Health checks | Ops | High | 2d | None |
| P1 | #18 GitHub Actions | CI/CD | High | 2d | None |
| P1 | #8 Test coverage | Quality | High | 5d | #18 |
| P2 | #19 Pre-commit | Quality | Medium | 1d | #18 |
| P2 | #15 Structured logging | Observability | Medium | 2d | None |
| P2 | #5 Docker retry | Reliability | Medium | 1d | None |
| P2 | #7 Graceful shutdown | Reliability | Medium | 2d | None |

## Implementation Phases

### Phase 1: Security Hardening (Week 1)

**Goal**: Close critical security vulnerabilities

#### Issue #3: Path Traversal Protection
**File**: `src/app.py`, `src/emustrings/results.py`

```python
# Changes needed:
1. Add UUID validation decorator
2. Sanitize artifact key/identifier
3. Use werkzeug.secure_filename
4. Add path validation in ResultsStore
```

**Implementation Steps**:
1. Create `src/emustrings/validation.py` with UUID validator
2. Create path sanitization utilities
3. Update `get_artifact()` endpoint
4. Update `Sample.store()` method
5. Add security tests

**Security Tests**:
```python
def test_path_traversal_attempt():
    # Attempt ../../../etc/passwd
    # Should return 400 Bad Request

def test_uuid_validation():
    # Invalid UUID format should return 400
```

#### Issue #2: Replace MD5 with SHA256
**File**: `src/emustrings/sample.py`

```python
# Current:
self.md5 = hashlib.md5(code).hexdigest()
self.sha256 = hashlib.sha256(code).hexdigest()

# Target:
self.sha256 = hashlib.sha256(code).hexdigest()
# md5 removed entirely
```

**Changes**:
1. Remove `self.md5` from Sample class
2. Update `to_dict()` method
3. Update any references in Analysis
4. Update tests

**Backward Compatibility**:
- Existing analyses with md5 field in MongoDB can remain
- New analyses will only have sha256

#### Issue #1: File Upload Size Limits
**File**: `src/app.py`

```python
# Changes needed:
1. Add MAX_FILE_SIZE config (default 10MB)
2. Add flask-limiter for rate limiting
3. Validate before processing
4. Return HTTP 413 for oversized files
```

**Configuration**:
```python
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 10 * 1024 * 1024))  # 10MB
```

**Rate Limiting**:
```python
from flask_limiter import Limiter
limiter = Limiter(app, key_func=get_remote_address)

@app.route("/api/submit", methods=["POST"])
@limiter.limit("10 per minute")
def submit_analysis():
    ...
```

### Phase 2: Operations & CI/CD (Week 2)

#### Issue #4: Health Check Endpoints
**Files**: `src/app.py`, Dockerfiles, `docker-compose.yml`

```python
# New endpoints:
@app.route("/health")
def health():
    return {"status": "healthy"}

@app.route("/ready")
def ready():
    # Check MongoDB, Redis
    return {"status": "ready"}
```

**Docker HEALTHCHECK**:
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:80/health || exit 1
```

#### Issue #18: GitHub Actions Migration
**Files**: `.github/workflows/ci.yml`, `.travis.yml` (delete)

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install flake8 black pytest
      - name: Lint with flake8
        run: flake8 src/
      - name: Format check with black
        run: black --check src/
      - name: Test with pytest
        run: pytest tests/
```

### Phase 3: Quality & Testing (Week 3-4)

#### Issue #8: Test Coverage 80%
**Files**: `tests/`, `pytest.ini`

**Structure**:
```
tests/
├── __init__.py
├── conftest.py
├── unit/
│   ├── __init__.py
│   ├── test_sample.py
│   ├── test_analysis.py
│   └── test_results.py
└── integration/
    ├── __init__.py
    └── test_api.py
```

**Coverage Configuration**:
```ini
# pytest.ini
[pytest]
testpaths = tests
addopts = --cov=src --cov-report=term-missing --cov-fail-under=80
```

#### Issue #19: Pre-commit Hooks
**File**: `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
  
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3
  
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
  
  - repo: https://github.com/pycqa/bandit
    rev: 1.7.6
    hooks:
      - id: bandit
        args: ["-c", "pyproject.toml"]
```

### Phase 4: Observability & Reliability (Week 5)

#### Issue #15: Structured Logging
**Files**: `src/app.py`, logging configuration

```python
import logging
from pythonjsonlogger import jsonlogger

# Configure JSON logging
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    '%(timestamp)s %(level)s %(name)s %(message)s'
)
logHandler.setFormatter(formatter)
```

#### Issue #5: Docker Retry Mechanism
**File**: `src/emustrings/emulators/emulator.py`

```python
import functools
import time

def retry_with_backoff(max_retries=3, backoff_seconds=1):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    sleep_time = backoff_seconds * (2 ** attempt)
                    logging.warning(f"Attempt {attempt + 1} failed, retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
        return wrapper
    return decorator
```

#### Issue #7: Graceful Shutdown
**File**: `src/daemon.py`

```python
import signal
import sys

shutdown_requested = False

def handle_sigterm(signum, frame):
    global shutdown_requested
    logging.info("SIGTERM received, initiating graceful shutdown...")
    shutdown_requested = True

signal.signal(signal.SIGTERM, handle_sigterm)

# In main loop:
if shutdown_requested:
    # Wait for running tasks
    # Exit cleanly
```

## Testing Strategy

### Unit Tests
- Mock external dependencies (MongoDB, Redis, Docker)
- Test each component in isolation
- Focus on business logic

### Integration Tests
- Use test containers for MongoDB/Redis
- Test API endpoints
- End-to-end happy path

### Security Tests
- Path traversal attempts
- Oversized file uploads
- Malformed UUIDs
- Rate limiting verification

## Rollback Plan

Each issue is implemented in a separate branch:
- `feature/issue-3-path-traversal`
- `feature/issue-2-sha256`
- `feature/issue-1-upload-limits`
- etc.

If issues arise, revert the specific branch.

## Definition of Done

Each issue is considered complete when:
- [ ] Code implemented following DDD
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] Security review (for security issues)
- [ ] CI/CD pipeline passing
- [ ] Code review approved

## Timeline

| Week | Focus | Issues |
|------|-------|--------|
| Week 1 | Security | #3, #2, #1 |
| Week 2 | Ops & CI/CD | #4, #18 |
| Week 3 | Testing | #8 (partial) |
| Week 4 | Testing & Quality | #8 (complete), #19 |
| Week 5 | Observability & Reliability | #15, #5, #7 |

Total estimated duration: **5 weeks**

---

*Next step: Begin Phase 1 - Security Hardening*
