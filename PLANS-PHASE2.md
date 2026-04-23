# Implementation Plan - Phase 2

> Documentation-Driven Development (DDD)
> Created: 2026-04-23
> Status: In Progress

## Overview

Phase 2 implementation plan covering the next 10 high-priority issues after security hardening.

## Issues Selected

| Priority | Issue | Category | Impact | Effort | Dependencies |
|----------|-------|----------|--------|--------|--------------|
| P0 | #18 GitHub Actions | CI/CD | Critical | 2d | None |
| P1 | #8 Test coverage 80% | Quality | High | 5d | #18 |
| P1 | #19 Pre-commit hooks | Quality | High | 1d | None |
| P2 | #5 Docker retry | Reliability | Medium | 1d | None |
| P2 | #7 Graceful shutdown | Reliability | Medium | 2d | None |
| P2 | #15 Structured logging | Observability | Medium | 2d | None |
| P2 | #16 Prometheus metrics | Observability | Medium | 2d | None |
| P2 | #6 Cleanup orphaned | Maintenance | Medium | 2d | None |
| P3 | #10 Bulk analysis | Feature | Low | 3d | #8 |
| P3 | #13 OpenAPI docs | Documentation | Low | 2d | None |

## Implementation Phases

### Phase 2.1: CI/CD Foundation (Week 1)

#### Issue #18: GitHub Actions Migration

**Files**:
- `.github/workflows/ci.yml` (new)
- `.travis.yml` (delete)
- `README.md` (update)

**Workflow Steps**:
```yaml
1. Checkout code
2. Set up Python 3.11
3. Install dependencies
4. Run flake8 linting
5. Run black format check
6. Run pytest with coverage
7. Build Docker images
8. Push to registry (on main branch)
```

**Matrix Strategy**:
- Python versions: 3.9, 3.10, 3.11
- OS: ubuntu-latest

#### Issue #19: Pre-commit Hooks

**File**: `.pre-commit-config.yaml`

**Hooks**:
```yaml
- trailing-whitespace
- end-of-file-fixer
- black (Python)
- flake8 (Python)
- bandit (Security)
- prettier (JS/CSS)
```

### Phase 2.2: Testing Infrastructure (Week 2-3)

#### Issue #8: Test Coverage 80%

**Files**:
- `pytest.ini` (new)
- `tests/unit/test_sample.py` (new)
- `tests/unit/test_analysis.py` (new)
- `tests/unit/test_results.py` (new)
- `tests/integration/test_api.py` (new)

**Coverage Targets**:
| Module | Target | Current |
|--------|--------|---------|
| sample.py | 90% | 0% |
| analysis.py | 85% | 0% |
| results.py | 85% | 0% |
| validation.py | 90% | 70% |
| app.py | 80% | 0% |

**Test Structure**:
```
tests/
├── __init__.py
├── conftest.py          # Shared fixtures
├── pytest.ini           # Configuration
├── fixtures/            # Test data
│   ├── samples/
│   │   ├── hello.js
│   │   ├── test.vbs
│   │   └── encoded.jse
│   └── mocks/
│       └── emulator.json
├── unit/
│   ├── __init__.py
│   ├── test_sample.py
│   ├── test_analysis.py
│   ├── test_results.py
│   └── test_validation.py
└── integration/
    ├── __init__.py
    ├── test_api.py
    └── test_end_to_end.py
```

### Phase 2.3: Reliability (Week 4)

#### Issue #5: Docker Retry Mechanism

**File**: `src/emustrings/utils/retry.py` (new)

**Implementation**:
```python
@retry_with_backoff(max_retries=3, backoff_seconds=1)
def start_container(...):
    ...
```

**Backoff Strategy**:
- Attempt 1: immediate
- Attempt 2: 2s delay
- Attempt 3: 4s delay
- Max delay: 60s

#### Issue #7: Graceful Shutdown

**File**: `src/daemon.py`

**Implementation**:
```python
import signal

shutdown_requested = False
running_tasks = set()

def handle_sigterm(signum, frame):
    global shutdown_requested
    shutdown_requested = True
    # Stop accepting new tasks
    # Wait for running tasks with timeout
```

**Timeout**: 30 seconds before forced exit

#### Issue #6: Cleanup Orphaned Analyses

**File**: `src/emustrings/cleanup.py` (new)

**Features**:
- Delete analyses older than RETENTION_DAYS (default 30)
- Preserve failed analyses option
- Dry-run mode
- Celery beat schedule

**Schedule**: Daily at 3 AM

### Phase 2.4: Observability (Week 5)

#### Issue #15: Structured Logging

**Files**:
- `src/emustrings/logging_config.py` (new)
- Update all loggers to use structured format

**Format**:
```json
{
  "timestamp": "2026-04-23T10:00:00Z",
  "level": "INFO",
  "logger": "emustrings.analysis",
  "message": "Analysis started",
  "aid": "uuid",
  "correlation_id": "uuid"
}
```

**Middleware**: Add correlation ID to Flask requests

#### Issue #16: Prometheus Metrics

**File**: `src/emustrings/metrics.py` (new)

**Metrics**:
| Metric | Type | Description |
|--------|------|-------------|
| analysis_duration_seconds | Histogram | Analysis execution time |
| analysis_queue_length | Gauge | Number of queued analyses |
| analysis_errors_total | Counter | Total analysis failures |
| active_analyses | Gauge | Currently running analyses |
| docker_operations_total | Counter | Docker operations count |

**Endpoint**: GET /metrics

### Phase 2.5: Features (Week 6)

#### Issue #10: Bulk Analysis

**Files**:
- `src/app.py`: Add `/api/submit/bulk` endpoint
- `src/emustrings/batch.py`: Batch processing logic

**Request**:
```python
POST /api/submit/bulk
Content-Type: multipart/form-data

files: [file1.js, file2.js, ...]
options: {...}
```

**Response**:
```json
{
  "batch_id": "uuid",
  "analyses": ["aid1", "aid2", ...],
  "total": 5,
  "status": "queued"
}
```

**Limit**: Max 10 files per batch

#### Issue #13: OpenAPI Documentation

**Library**: flasgger

**File**: Update `src/app.py` with docstrings

**Endpoints Documented**:
- /health
- /ready
- /api/analysis
- /api/analysis/{aid}
- /api/submit
- /api/submit/bulk
- /api/analysis/{aid}/{key}/{identifier}

## Testing Strategy

### Unit Tests
```python
def test_docker_retry():
    # Mock Docker failure
    # Verify retry happens
    # Verify success on final attempt

def test_graceful_shutdown():
    # Start analysis
    # Send SIGTERM
    # Verify completion before exit

def test_cleanup_orphaned():
    # Create old analysis
    # Run cleanup
    # Verify deleted
```

### Integration Tests
```python
def test_github_actions():
    # Push code
    # Verify workflow triggers
    # Verify all checks pass

def test_prometheus_metrics():
    # Submit analysis
    # Check /metrics endpoint
    # Verify metrics updated
```

## Documentation Updates

### README.md Updates
- Add CI/CD badge
- Add test coverage badge
- Add pre-commit setup instructions
- Update API documentation link

### docs/ Updates
- Add TESTING.md
- Add OBSERVABILITY.md
- Update API.md with new endpoints

## Definition of Done

Each issue is complete when:
- [ ] Code implemented
- [ ] Unit tests written (coverage >= 80%)
- [ ] Integration tests written
- [ ] Documentation updated
- [ ] CI/CD pipeline passing
- [ ] Code review approved
- [ ] GitHub Issue closed with comment

## Timeline

| Week | Focus | Issues |
|------|-------|--------|
| Week 1 | CI/CD Foundation | #18, #19 |
| Week 2 | Testing Infrastructure | #8 (setup) |
| Week 3 | Testing | #8 (complete) |
| Week 4 | Reliability | #5, #7, #6 |
| Week 5 | Observability | #15, #16 |
| Week 6 | Features | #10, #13 |

Total estimated duration: **6 weeks**

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| GitHub Actions learning curve | Low | Use standard templates |
| Test coverage target | Medium | Prioritize critical paths |
| Docker retry complexity | Low | Use tenacity library |
| Prometheus setup | Low | Use flask-prometheus-exporter |

## Success Criteria

Phase 2 is successful when:
- CI/CD pipeline fully operational
- Test coverage >= 80%
- All reliability improvements deployed
- Observability stack collecting metrics
- New features documented and tested

---

*Next step: Begin Phase 2.1 - CI/CD Foundation*
