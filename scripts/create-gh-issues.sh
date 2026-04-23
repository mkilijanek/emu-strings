#!/bin/bash
# Skrypt do tworzenia GitHub Issues dla projektu emu-strings
# Użycie: ./scripts/create-gh-issues.sh
# Wymaga: gh CLI zautoryzowane (gh auth login)

set -e

echo "Creating GitHub Issues for emu-strings..."
echo "=========================================="

# Security Issues
echo "Creating Security Issues..."

gH issue create --title "[SECURITY] Add file upload size limits and validation" \
  --body "## Description
Currently, there is no limit on uploaded file sizes, which could lead to resource exhaustion attacks.

## Requirements
- Add configurable max file size limit (default: 10MB)
- Validate file type before processing
- Add rate limiting for API endpoints to prevent abuse
- Return appropriate HTTP 413 for oversized files

## Acceptance Criteria
- [ ] MAX_FILE_SIZE env var (default 10MB)
- [ ] File type validation (magic numbers)
- [ ] Rate limiting (flask-limiter)
- [ ] Tests for oversized files
- [ ] Documentation updated

## References
- src/app.py: submit_analysis() endpoint
- Flask-Limiter: https://flask-limiter.readthedocs.io/

## Labels: security, enhancement" \
  --label "security" --label "enhancement" || echo "Issue #1 skipped/already exists"

gH issue create --title "[SECURITY] Replace MD5 with SHA256 for sample identification" \
  --body "## Description
MD5 is cryptographically broken and should not be used for file identification. The Sample class currently uses MD5 alongside SHA256.

## Requirements
- Remove MD5 hashing from Sample class
- Use SHA256 as primary identifier
- Consider migration strategy for existing analyses

## Acceptance Criteria
- [ ] MD5 removed from Sample class
- [ ] SHA256 used for all identification
- [ ] Backward compatibility handled
- [ ] Tests updated
- [ ] Documentation updated

## References
- src/emustrings/sample.py:14
- src/emustrings/analysis.py:98 (find_analysis by sha256)

## Labels: security, refactoring" \
  --label "security" --label "refactoring" || echo "Issue #2 skipped/already exists"

gH issue create --title "[SECURITY] Add path traversal protection" \
  --body "## Description
User-provided file paths and identifiers are not fully sanitized, potentially allowing path traversal attacks.

## Requirements
- Sanitize file paths in all user inputs
- Validate analysis IDs format (must be valid UUID)
- Add validation for artifact keys and identifiers
- Use werkzeug.secure_filename or equivalent

## Acceptance Criteria
- [ ] UUID validation for aid parameter
- [ ] Path sanitization in get_artifact
- [ ] Filename sanitization in Sample.store
- [ ] Security tests for path traversal
- [ ] Code review completed

## References
- src/app.py: get_artifact() endpoint
- src/emustrings/results.py
- werkzeug.utils.secure_filename

## Labels: security, bug" \
  --label "security" --label "bug" || echo "Issue #3 skipped/already exists"

# Reliability Issues
echo "Creating Reliability Issues..."

gH issue create --title "[OPS] Implement health check endpoints" \
  --body "## Description
No health check endpoints exist for monitoring service health or Docker orchestration.

## Requirements
- Add /health endpoint for Flask app (liveness)
- Add /ready endpoint (readiness)
- Add Docker health checks for all services
- Check dependency health (MongoDB, Redis, Docker daemon)

## Acceptance Criteria
- [ ] GET /health returns 200 when app is running
- [ ] GET /ready checks MongoDB, Redis connectivity
- [ ] Docker HEALTHCHECK in all Dockerfiles
- [ ] docker-compose health checks configured
- [ ] Kubernetes probes compatibility

## References
- src/app.py
- docker-compose.yml
- Flask healthcheck pattern

## Labels: enhancement, ops" \
  --label "enhancement" --label "ops" || echo "Issue #4 skipped/already exists"

gH issue create --title "[RELIABILITY] Add retry mechanism for Docker operations" \
  --body "## Description
Docker operations can fail transiently but no retry mechanism exists.

## Requirements
- Implement exponential backoff for container operations
- Handle transient Docker daemon errors
- Add maximum retry count to prevent infinite loops
- Log retry attempts

## Acceptance Criteria
- [ ] Retry decorator/function created
- [ ] Exponential backoff (1s, 2s, 4s, 8s... max 60s)
- [ ] Max 3 retries for container operations
- [ ] Retry logging with warning level
- [ ] Tests for retry logic

## References
- src/emustrings/emulators/emulator.py: start() method
- tenacity library or custom implementation

## Labels: enhancement, reliability" \
  --label "enhancement" --label "reliability" || echo "Issue #5 skipped/already exists"

gH issue create --title "[RELIABILITY] Implement cleanup mechanism for orphaned analyses" \
  --body "## Description
Old analyses accumulate in storage without cleanup mechanism.

## Requirements
- Cron job to clean old analyses (>30 days)
- Configurable retention policy
- Preserve failed analyses for debugging

## Acceptance Criteria
- [ ] Cleanup daemon task created
- [ ] RETENTION_DAYS env var (default 30)
- [ ] Preserve orphaned/failed analyses option
- [ ] Logging of cleaned analyses
- [ ] Dry-run mode for testing

## References
- src/daemon.py
- Celery beat for scheduling

## Labels: enhancement, maintenance" \
  --label "enhancement" --label "maintenance" || echo "Issue #6 skipped/already exists"

gH issue create --title "[RELIABILITY] Add graceful shutdown handling" \
  --body "## Description
Daemon doesn't handle SIGTERM properly, potentially interrupting running analyses.

## Requirements
- Handle SIGTERM properly in daemon
- Complete running analyses before shutdown
- Set timeout for forced shutdown

## Acceptance Criteria
- [ ] SIGTERM handler in daemon.py
- [ ] Wait for running analyses with timeout
- [ ] Prevent new analyses during shutdown
- [ ] Exit code 0 on graceful shutdown
- [ ] Exit code 1 on forced shutdown

## References
- src/daemon.py
- Python signal module
- Celery worker shutdown

## Labels: enhancement, reliability" \
  --label "enhancement" --label "reliability" || echo "Issue #7 skipped/already exists"

# Testing Issues
echo "Creating Testing Issues..."

gH issue create --title "[TESTING] Expand test coverage to 80%" \
  --body "## Description
Current test coverage is minimal (only tests/test.py).

## Requirements
- Unit tests for Sample, Analysis, ResultsStore
- Integration tests for API endpoints
- Emulator mock tests
- Target: 80% coverage

## Acceptance Criteria
- [ ] pytest configured with coverage
- [ ] Unit tests for Sample class
- [ ] Unit tests for Analysis class
- [ ] Unit tests for ResultsStore
- [ ] API integration tests
- [ ] Emulator mock tests
- [ ] CI pipeline with coverage report
- [ ] Coverage badge in README

## References
- tests/test.py
- pytest, pytest-cov
- Flask testing docs

## Labels: testing, enhancement" \
  --label "testing" --label "enhancement" || echo "Issue #8 skipped/already exists"

gH issue create --title "[TESTING] Add test fixtures and sample malware corpus" \
  --body "## Description
No synthetic malware samples exist for testing.

## Requirements
- Create synthetic JScript/VBScript samples
- Mock emulator responses
- Test data generators

## Acceptance Criteria
- [ ] Synthetic JScript samples (obfuscated)
- [ ] Synthetic VBScript samples
- [ ] Encoded JScript/VBScript samples
- [ ] Mock emulator responses (JSON)
- [ ] Factory fixtures for tests
- [ ] Documentation of test corpus

## References
- tests/
- Factory Boy or custom fixtures

## Labels: testing" \
  --label "testing" || echo "Issue #9 skipped/already exists"

# Feature Issues
echo "Creating Feature Issues..."

gH issue create --title "[FEATURE] Add bulk/batch analysis endpoint" \
  --body "## Description
Currently only single file upload is supported.

## Requirements
- Allow submitting multiple samples at once
- Return job IDs for tracking
- Progress tracking for batch

## Acceptance Criteria
- [ ] POST /api/submit/bulk endpoint
- [ ] Accept multipart/form-data with multiple files
- [ ] Return batch_id for tracking
- [ ] Individual analysis IDs in response
- [ ] Batch status endpoint
- [ ] Frontend batch upload UI
- [ ] Documentation updated

## References
- src/app.py: submit_analysis
- Frontend upload form

## Labels: feature, api" \
  --label "feature" --label "api" || echo "Issue #10 skipped/already exists"

gH issue create --title "[FEATURE] Implement results export (JSON, CSV, PDF)" \
  --body "## Description
No export functionality exists for analysis results.

## Requirements
- Export analysis results in multiple formats
- Download as archive
- Bulk export support

## Acceptance Criteria
- [ ] GET /api/analysis/{aid}/export?format=json
- [ ] GET /api/analysis/{aid}/export?format=csv
- [ ] GET /api/analysis/{aid}/export?format=pdf
- [ ] Bulk export endpoint
- [ ] Download link in UI
- [ ] Format selection in UI
- [ ] Tests for exports

## References
- src/emustrings/results.py
- ReportLab for PDF
- csv module

## Labels: feature, api" \
  --label "feature" --label "api" || echo "Issue #11 skipped/already exists"

gH issue create --title "[FEATURE] Add webhook notifications" \
  --body "## Description
No notification mechanism exists for analysis completion.

## Requirements
- Notify on analysis completion
- Support Slack, Teams, generic webhook
- Configurable per-analysis

## Acceptance Criteria
- [ ] Webhook configuration model
- [ ] POST webhook on analysis complete/fail
- [ ] Slack webhook format
- [ ] Teams webhook format
- [ ] Generic webhook (custom payload)
- [ ] Retry on failure
- [ ] Webhook UI configuration
- [ ] Tests for webhooks

## References
- src/emustrings/analysis.py: set_status
- Celery tasks for async webhook

## Labels: feature, integration" \
  --label "feature" --label "integration" || echo "Issue #12 skipped/already exists"

gH issue create --title "[FEATURE] Add REST API documentation (OpenAPI/Swagger)" \
  --body "## Description
API is not documented, making integration difficult.

## Requirements
- Document all endpoints
- Provide example requests/responses
- Interactive Swagger UI

## Acceptance Criteria
- [ ] OpenAPI 3.0 spec created
- [ ] All endpoints documented
- [ ] Request/response schemas
- [ ] Authentication documented (if added)
- [ ] Swagger UI at /api/docs
- [ ] ReDoc alternative
- [ ] Postman collection export

## References
- src/app.py
- flasgger or flask-restx
- OpenAPI specification

## Labels: documentation, api" \
  --label "documentation" --label "api" || echo "Issue #13 skipped/already exists"

gH issue create --title "[FEATURE] Implement YARA rule matching" \
  --body "## Description
No YARA rule integration exists for pattern matching.

## Requirements
- Run YARA rules on extracted strings
- Add YARA rule management
- Match reporting

## Acceptance Criteria
- [ ] YARA rules storage (MongoDB)
- [ ] Rule management API (CRUD)
- [ ] YARA matching in analysis pipeline
- [ ] Match results in output
- [ ] Default rule set (IoC patterns)
- [ ] Custom rules upload
- [ ] Documentation

## References
- src/emustrings/analysis.py
- yara-python library

## Labels: feature, security" \
  --label "feature" --label "security" || echo "Issue #14 skipped/already exists"

# Observability Issues
echo "Creating Observability Issues..."

gH issue create --title "[OBSERVABILITY] Add structured logging (JSON)" \
  --body "## Description
Logs are in plain text format, difficult to parse and analyze.

## Requirements
- Replace plain text logs with structured format
- Add correlation IDs for tracing
- Log levels configuration

## Acceptance Criteria
- [ ] python-json-logger configured
- [ ] All loggers output JSON
- [ ] Correlation ID middleware
- [ ] Request ID propagation
- [ ] Log level via env var
- [ ] Centralized logging ready

## References
- Python logging module
- python-json-logger

## Labels: enhancement, observability" \
  --label "enhancement" --label "observability" || echo "Issue #15 skipped/already exists"

gH issue create --title "[OBSERVABILITY] Add Prometheus metrics" \
  --body "## Description
No metrics collection exists for monitoring.

## Requirements
- Analysis duration histogram
- Queue length gauge
- Error rate counter

## Acceptance Criteria
- [ ] prometheus-flask-exporter configured
- [ ] /metrics endpoint
- [ ] analysis_duration_seconds histogram
- [ ] analysis_queue_length gauge
- [ ] analysis_errors_total counter
- [ ] emulator-specific metrics
- [ ] Grafana dashboard JSON

## References
- prometheus-flask-exporter
- Prometheus metrics types

## Labels: enhancement, monitoring" \
  --label "enhancement" --label "monitoring" || echo "Issue #16 skipped/already exists"

gH issue create --title "[OBSERVABILITY] Implement distributed tracing" \
  --body "## Description
No distributed tracing across services.

## Requirements
- Trace requests across services
- OpenTelemetry integration
- Jaeger/Zipkin export

## Acceptance Criteria
- [ ] OpenTelemetry SDK configured
- [ ] Flask instrumentation
- [ ] Celery instrumentation
- [ ] Docker client instrumentation
- [ ] Trace context propagation
- [ ] Jaeger exporter
- [ ] Sampling configuration

## References
- OpenTelemetry Python
- opentelemetry-instrumentation-flask

## Labels: enhancement, observability" \
  --label "enhancement" --label "observability" || echo "Issue #17 skipped/already exists"

# CI/CD Issues
echo "Creating CI/CD Issues..."

gH issue create --title "[CI/CD] Migrate from Travis CI to GitHub Actions" \
  --body "## Description
Travis CI is deprecated and builds may stop working.

## Requirements
- Migrate to GitHub Actions
- Add automated testing
- Add Docker image building

## Acceptance Criteria
- [ ] .github/workflows/ci.yml created
- [ ] Python linting (flake8)
- [ ] Python formatting (black)
- [ ] Test execution
- [ ] Coverage reporting
- [ ] Docker build and push
- [ ] Multi-arch support (amd64, arm64)
- [ ] Remove .travis.yml

## References
- .travis.yml (current)
- GitHub Actions docs

## Labels: ci-cd, ops" \
  --label "ci-cd" --label "ops" || echo "Issue #18 skipped/already exists"

gH issue create --title "[CI/CD] Add pre-commit hooks" \
  --body "## Description
No code quality checks before commit.

## Requirements
- Code formatting (black, prettier)
- Linting (flake8, eslint)
- Security scanning (bandit)

## Acceptance Criteria
- [ ] .pre-commit-config.yaml created
- [ ] black for Python
- [ ] flake8 for Python
- [ ] bandit for security
- [ ] prettier for JS/CSS
- [ ] eslint for JS
- [ ] trailing-whitespace fixer
- [ ] end-of-file-fixer
- [ ] Documentation in CONTRIBUTING.md

## References
- pre-commit framework
- pre-commit-hooks

## Labels: ci-cd, quality" \
  --label "ci-cd" --label "quality" || echo "Issue #19 skipped/already exists"

gH issue create --title "[CI/CD] Implement automated dependency updates" \
  --body "## Description
Dependencies may have security vulnerabilities.

## Requirements
- Dependabot configuration
- Security vulnerability scanning
- Automated PR creation

## Acceptance Criteria
- [ ] .github/dependabot.yml created
- [ ] Python dependencies monitored
- [ ] JavaScript dependencies monitored
- [ ] Docker base images monitored
- [ ] GitHub Actions monitored
- [ ] Security alerts enabled
- [ ] CODEOWNERS for review assignment
- [ ] Auto-merge for patch updates

## References
- Dependabot docs
- GitHub Security Advisories

## Labels: ci-cd, security" \
  --label "ci-cd" --label "security" || echo "Issue #20 skipped/already exists"

echo "=========================================="
echo "Done! Check GitHub Issues at:"
echo "https://github.com/$(gh repo view --json nameWithOwner -q .nameWithOwner)/issues"
