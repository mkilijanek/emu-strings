# Emu-Strings: Agent Development Guide

> **Documentation-Driven Development (DDD)** - Zasada projektowa: dokumentacja pierwsza, implementacja druga.

## Przeznaczenie repozytorium

**Emu-Strings** to platforma do analizy malware JScript/VBScript oparta na natywnym silniku Windows Script Host (WSH) uruchamianym w środowisku Wine w kontenerach Docker.

### Główne cele projektu
1. **Dekodowanie stringów** - Wykrywanie zobfuskowanych stringów wykonywanych w runtime
2. **Ekstrakcja IoC** - URL-e, OLE Automation object identifiers, eval'owane code snippety
3. **Sandbox emulation** - Bezpieczne wykonywanie podejrzanych skryptów w izolowanych kontenerach
4. **Network simulation** - FakeNet z HTTP/DNS do wykrywania prób komunikacji C2

## Architektura systemu

```
┌─────────────────────────────────────────────────────────────────┐
│                         Web UI (React)                          │
│              src/web/src/ - Interfejs użytkownika              │
└─────────────────────────────┬───────────────────────────────────┘
                              │ HTTP
┌─────────────────────────────▼───────────────────────────────────┐
│                    Flask API (app.py)                         │
│   /api/analysis - listowanie analiz                            │
│   /api/submit   - upload próbki                                │
│   /api/analysis/<aid> - pobieranie wyników                      │
└─────────────────────────────┬───────────────────────────────────┘
                              │ Celery Tasks
┌─────────────────────────────▼───────────────────────────────────┐
│                  Analysis Daemon (daemon.py)                   │
│   Zarządzanie kolejką analiz, koordynacja emulatorów           │
└─────────────────────────────┬───────────────────────────────────┘
                              │ Docker API
┌─────────────────────────────▼───────────────────────────────────┐
│                     Emulator Engines                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   Winedrop   │  │    Box-js    │  │   Future...  │        │
│  │  (JScript/   │  │  (JScript    │  │              │        │
│  │   VBScript)  │  │   only)      │  │              │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│         Wine + Docker-in-Docker                               │
└─────────────────────────────────────────────────────────────────┘
```

### Komponenty systemu

#### 1. Warstwa prezentacji (React)
- **UploadForm.js** - Formularz uploadu z advanced settings
- **AnalysisList.js** - Lista analiz z paginacją
- **AnalysisView.js** - Szczegóły analizy z prezenterami wyników
- **presenters/** - Komponenty wyświetlania wyników (Strings, URLs, Snippets, Logs)

#### 2. API Layer (Flask)
- **app.py** - REST API endpoints
- MongoDB dla metadanych analiz
- Redis dla kolejki Celery

#### 3. Core Engine (Python)
- **analysis.py** - Klasa Analysis zarządzająca cyklem życia analizy
- **sample.py** - Klasa Sample reprezentująca próbkę z autodetekcją języka
- **results.py** - ResultsStore dla agregacji wyników z emulatorów
- **language.py** - System rozpoznawania języka (JScript, VBScript, Encoded)

#### 4. Emulatory
- **emulator.py** - Bazowa klasa Emulator
- **winedrop/** - Emulator oparty na Wine + patchowanym WSH
- **boxjs/** - Integracja z zewnętrznym narzędziem box-js

#### 5. Infrastructure
- **docker-compose.yml** - Orkiestracja wielu serwisów
- **dind** - Docker-in-Docker dla izolacji

## Proces analizy (flow)

```
1. Upload próbki (POST /api/submit)
   ↓
2. Tworzenie Analysis (UUID) + Sample (hash, lang detection)
   ↓
3. Zapis do MongoDB + filesystem (workdir)
   ↓
4. Celery task → analyze_sample
   ↓
5. Daemon wybiera emulatory na podstawie języka
   ↓
6. Dla każdego emulatora:
   - start() → Docker container
   - join() → czekaj na zakończenie
   - store_results() → zapisz do ResultsStore
   ↓
7. Finalizacja → status success/failed
```

## Development Guidelines (DDD)

### Zasada 1: Dokumentacja przed kodem
- Każdy feature zaczyna się od aktualizacji dokumentacji
- API changes → aktualizuj AGENTS.md
- Nowe endpointy → dokumentacja w kodzie + OpenAPI

### Zasła 2: Test-driven dla core logic
- Unit testy dla Sample, Analysis, ResultsStore
- Mock testy dla emulatorów
- Integration testy dla API

### Zasada 3: Security-first
- Wszystkie inputy są walidowane
- Path traversal protection
- File size limits
- Rate limiting

### Zasada 4: Observability
- Structured logging (JSON)
- Correlation IDs
- Prometheus metrics
- Distributed tracing

## Utworzenie GitHub Issues

Aby utworzyć wszystkie zidentyfikowane enhancements, uruchom:

```bash
# Autoryzacja (jeśli potrzebna)
gh auth login

# Security
gh issue create --title "[SECURITY] Add file upload size limits" --body "Add configurable max file size limit (default: 10MB) and rate limiting" --label "security,enhancement"
gh issue create --title "[SECURITY] Replace MD5 with SHA256" --body "Remove MD5 from Sample class, use only SHA256" --label "security,refactoring"
gh issue create --title "[SECURITY] Add path traversal protection" --body "Sanitize file paths and validate UUID format" --label "security,bug"

# Reliability
gh issue create --title "[OPS] Implement health check endpoints" --body "Add /health, /ready, and Docker health checks" --label "enhancement,ops"
gh issue create --title "[RELIABILITY] Add retry mechanism for Docker" --body "Exponential backoff for container operations" --label "enhancement,reliability"
gh issue create --title "[RELIABILITY] Cleanup orphaned analyses" --body "Cron job for cleaning old analyses >30 days" --label "enhancement,maintenance"
gh issue create --title "[RELIABILITY] Graceful shutdown" --body "Handle SIGTERM, complete running analyses" --label "enhancement,reliability"

# Testing
gh issue create --title "[TESTING] Expand test coverage to 80%" --body "Unit tests for core classes, integration tests for API" --label "testing,enhancement"
gh issue create --title "[TESTING] Add test fixtures" --body "Synthetic JScript/VBScript samples, mock emulator responses" --label "testing"

# Features
gh issue create --title "[FEATURE] Bulk analysis endpoint" --body "Submit multiple samples at once" --label "feature,api"
gh issue create --title "[FEATURE] Results export (JSON, CSV, PDF)" --body "Download analysis results in multiple formats" --label "feature,api"
gh issue create --title "[FEATURE] Webhook notifications" --body "Notify on analysis completion (Slack, Teams, webhook)" --label "feature,integration"
gh issue create --title "[FEATURE] OpenAPI/Swagger docs" --body "Document all API endpoints" --label "documentation,api"
gh issue create --title "[FEATURE] YARA rule matching" --body "Run YARA rules on extracted strings" --label "feature,security"

# Observability
gh issue create --title "[OBS] Structured logging (JSON)" --body "Replace plain text with JSON logs, add correlation IDs" --label "enhancement,observability"
gh issue create --title "[OBS] Prometheus metrics" --body "Analysis duration, queue length, error rates" --label "enhancement,monitoring"
gh issue create --title "[OBS] Distributed tracing" --body "OpenTelemetry integration" --label "enhancement,observability"

# CI/CD
gh issue create --title "[CI/CD] Migrate to GitHub Actions" --body "Travis CI deprecated, add automated testing" --label "ci-cd,ops"
gh issue create --title "[CI/CD] Pre-commit hooks" --body "black, flake8, eslint, bandit" --label "ci-cd,quality"
gh issue create --title "[CI/CD] Dependabot" --body "Automated dependency updates and security scanning" --label "ci-cd,security"
```

## Konwencje kodu

### Python
- **Formatter**: black
- **Linter**: flake8
- **Security**: bandit
- **Docstrings**: Google style

### JavaScript/React
- **Formatter**: prettier
- **Linter**: eslint
- **Style**: Functional components with hooks

## Workflow developmentu

### Dodawanie nowego emulatora

1. **Dokumentacja** - Opisz w AGENTS.md nowy emulator
2. **Implementacja** - Stwórz klasę dziedziczącą z Emulator
3. **SUPPORTED_LANGUAGES** - Zdefiniuj języki
4. **IMAGE_NAME** - Nazwa obrazu Docker
5. **Implementuj metody**:
   - `connections()` → lista URL-i
   - `strings()` → lista stringów
   - `snippets()` → lista snippetów
   - `logfiles()` → lista logów
6. **Testy** - Mock testy + integration test
7. **Dokumentacja** - Update README.md

### Dodawanie nowego endpointu API

1. **Dokumentacja** - Opis endpointu w AGENTS.md
2. **OpenAPI spec** - Dodaj do specyfikacji
3. **Implementacja** - Dodaj do app.py
4. **Testy** - Unit + integration tests
5. **Frontend** - Update jeśli potrzebny

## Rozwój lokalny

```bash
# 1. Klonowanie z submodules
git clone --recurse-submodules https://github.com/psrok1/emu-strings.git

# 2. Build emulator images (długie!)
cd emulators && ./build.sh

# 3. Uruchomienie
cd .. && docker-compose up --build

# 4. Testy
cd src && python -m pytest ../tests/
```

## Debugging

### Logi
```bash
# Web app
docker-compose logs -f emu-app

# Daemon
docker-compose logs -f emu-daemon

# DIND (Docker in Docker)
docker-compose logs -f dind
```

### Debug mode
```bash
FLASK_ENV=development docker-compose up
```

## Troubleshooting

### Issue: Analysis timeout
- Zwiększ `soft_timeout` w opcjach
- Sprawdź logi w workdir

### Issue: Container fails to start
- Sprawdź Docker daemon (DIND)
- Zweryfikuj uprawnienia privileged

### Issue: MongoDB connection
- Sprawdź czy mongo kontener działa
- Zweryfikuj MONGODB_URL

## Kontakt

- **Autor**: psrok1
- **Email**: kontakt przez GitHub issues
- **Thesis**: https://0xcc.pl/static/msc/psrok1-msc.pdf (polish only)

---

*Ostatnia aktualizacja: 2026-04-23*
