# Emu-Strings Roadmap

> **Documentation-Driven Development (DDD)**
> 
> Każda faza zaczyna się od dokumentacji, implementacja następuje po akceptacji planu.

---

## Phase 0: Foundation (Q2 2026)

**Cel**: Stabilizacja istniejącej bazy kodu, poprawa bezpieczeństwa i niezawodności

### Sprint 0.1: Security Hardening
| Issue | Priorytet | Estymacja |
|-------|-----------|-----------|
| #1 Add file upload size limits | P0 | 2d |
| #2 Replace MD5 with SHA256 | P0 | 1d |
| #3 Path traversal protection | P0 | 2d |

**Definition of Done**:
- [ ] Max file size configurable via env var
- [ ] SHA256 jako jedyny hash
- [ ] UUID validation dla analysis IDs
- [ ] Security testy przechodzą

### Sprint 0.2: Reliability
| Issue | Priorytet | Estymacja |
|-------|-----------|-----------|
| #4 Health check endpoints | P1 | 2d |
| #5 Docker retry mechanism | P1 | 2d |
| #7 Graceful shutdown | P1 | 2d |

**Definition of Done**:
- [ ] /health i /ready działają
- [ ] Exponential backoff w Docker ops
- [ ] SIGTERM handling w daemonie
- [ ] Docker health checks w compose

### Sprint 0.3: Testing Infrastructure
| Issue | Priorytet | Estymacja |
|-------|-----------|-----------|
| #8 Expand test coverage | P1 | 5d |
| #9 Test fixtures | P2 | 3d |

**Definition of Done**:
- [ ] 80% coverage dla core classes
- [ ] Integration tests dla API
- [ ] Synthetic malware samples
- [ ] CI pipeline z testami

### Milestone 0: Stable Foundation
**Data**: End of Q2 2026
**Kryteria**:
- Wszystkie P0 issues zamknięte
- CI/CD działa
- Test coverage ≥ 80%
- Security audit passed

---

## Phase 1: API & Features (Q3 2026)

**Cel**: Rozszerzenie funkcjonalności API, dodanie nowych features

### Sprint 1.1: API Enhancements
| Issue | Priorytet | Estymacja |
|-------|-----------|-----------|
| #10 Bulk analysis endpoint | P1 | 3d |
| #11 Results export | P1 | 3d |
| #13 OpenAPI/Swagger docs | P1 | 2d |

**Definition of Done**:
- [ ] POST /api/submit/bulk działa
- [ ] Export do JSON, CSV, PDF
- [ ] /api/docs z Swagger UI
- [ ] Dokumentacja API zaktualizowana

### Sprint 1.2: Integrations
| Issue | Priorytet | Estymacja |
|-------|-----------|-----------|
| #12 Webhook notifications | P2 | 3d |
| #14 YARA rule matching | P2 | 5d |

**Definition of Done**:
- [ ] Webhook config w UI
- [ ] Slack/Teams/generic webhook
- [ ] YARA rules storage
- [ ] Matching w trakcie analizy

### Milestone 1: Feature Complete
**Data**: End of Q3 2026
**Kryteria**:
- Bulk upload działa
- API fully documented
- Webhook notifications
- YARA integration

---

## Phase 2: Observability (Q4 2026)

**Cel**: Pełna obserwowalność systemu

### Sprint 2.1: Logging & Tracing
| Issue | Priorytet | Estymacja |
|-------|-----------|-----------|
| #15 Structured logging | P1 | 3d |
| #17 Distributed tracing | P2 | 5d |

**Definition of Done**:
- [ ] JSON logs z correlation IDs
- [ ] Log aggregation ready
- [ ] OpenTelemetry tracing
- [ ] Trace visualization

### Sprint 2.2: Metrics & Monitoring
| Issue | Priorytet | Estymacja |
|-------|-----------|-----------|
| #16 Prometheus metrics | P1 | 3d |
| Dashboard | P2 | 3d |

**Definition of Done**:
- [ ] /metrics endpoint
- [ ] Analysis duration histogram
- [ ] Queue length gauge
- [ ] Grafana dashboard

### Milestone 2: Observable System
**Data**: End of Q4 2026
**Kryteria**:
- Structured logging
- Metrics collection
- Distributed tracing
- Alerting rules

---

## Phase 3: Scale & Performance (Q1 2027)

**Cel**: Skalowalność i wydajność

### Sprint 3.1: Performance
- Async processing dla wielu próbek
- Redis queue optimization
- Database indexing

### Sprint 3.2: Scale
- Kubernetes deployment
- Horizontal scaling emulatorów
- Auto-scaling policies

### Milestone 3: Production Ready
**Data**: End of Q1 2027
**Kryteria**:
- 100+ concurrent analyses
- Kubernetes deployment
- Auto-scaling działa

---

## Phase 4: Advanced Features (Q2-Q3 2027)

**Cel**: Zaawansowane możliwości analizy

### Future Ideas
- [ ] Machine learning classification
- [ ] Behavioral analysis
- [ ] Threat intelligence integration
- [ ] Multi-engine voting
- [ ] Sandboxing improvements
- [ ] Custom emulator plugins

---

## Appendix: Issue Quick Reference

### Security (3 issues)
- #1 File upload limits
- #2 MD5 → SHA256
- #3 Path traversal

### Reliability (3 issues)
- #4 Health checks
- #5 Docker retry
- #6 Cleanup orphaned
- #7 Graceful shutdown

### Testing (2 issues)
- #8 Test coverage
- #9 Test fixtures

### Features (5 issues)
- #10 Bulk analysis
- #11 Results export
- #12 Webhooks
- #13 OpenAPI docs
- #14 YARA rules

### Observability (3 issues)
- #15 Structured logging
- #16 Prometheus metrics
- #17 Distributed tracing

### CI/CD (3 issues)
- #18 GitHub Actions
- #19 Pre-commit hooks
- #20 Dependabot

---

*Ostatnia aktualizacja: 2026-04-23*
*Next review: End of Q2 2026*
