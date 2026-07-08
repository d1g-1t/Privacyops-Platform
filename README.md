# Privacyops-Platform 🏗️

> Enterprise privacy governance platform for Russian Federal Law 152-FZ compliance.
> Clean Architecture · DDD · Hexagonal Ports & Adapters · FastAPI · SQLAlchemy 2 async

---

## What is this?

A production-ready backend that lets your DPO and compliance team:

- **Register & evaluate** personal data processing activities (Article 18.1, 22)
- **Track legal bases** — consent, contract, legal obligation, etc.
- **Manage consent** — templates + captures with expiry and withdrawal audit trail
- **Handle DSR** (Data Subject Requests) with 30-day SLA enforcement
- **Vet processors/vendors** — questionnaire → risk score → DPA attestation → approve/reject
- **Respond to incidents** — severity classification, RKN notification helper, full lifecycle
- **Check localization** 152-FZ Article 18(5) — Roskomnadzor compliance assertion
- **Generate compliance score** — real-time dashboard aggregate across all domains
- **Full audit log** — append-only, tamper-evident event stream
- **Rule engine** — 15 deterministic rules across 5 domains, evaluated on demand
- **LLM assistance** — risk explanations and DSR draft responses via Ollama (assistive only, never primary truth)

Everything is async, multi-tenant, PASETO v4-protected, and fully observable via Prometheus + Grafana + Tempo.

---

## Quick start (the only thing you actually need to remember)

```bash
make setup   # copy .env, build images
make up      # spin everything up
make test    # run the test suite
make down    # shut it all down
```

After `make up`, the API is at **http://localhost:8700/docs** (Swagger UI, only in DEBUG mode).

---

## Port map (all non-standard to avoid conflicts with your other projects)

| Service          | Port  |
|------------------|-------|
| FastAPI API      | 8700  |
| PostgreSQL 16    | 5700  |
| Redis 7          | 6700  |
| Grafana          | 3702  |
| Prometheus       | 9700  |
| Tempo (OTLP)     | 4700  |
| Tempo (HTTP)     | 3700  |
| Loki             | 3701  |
| Celery Flower    | 5701  |
| Ollama           | 11700 |

---

## Makefile reference

```
make setup      — prep environment (.env, pull images, build)
make up         — docker compose up -d (all services)
make down       — docker compose down
make test       — run pytest inside the api container
make lint       — ruff + mypy
make migrate    — alembic upgrade head
make shell      — bash into the api container
make logs       — tail api + worker logs
make clean      — remove volumes and images (nuclear option)
```

---

## Architecture

```
src/
├── core/           — config, logging, telemetry, security (PASETO), DI container
├── domain/         — pure Python: entities, value objects, repositories (ports), services
│   ├── entities/       — 13 dataclass entities with business methods
│   ├── value_objects/  — 8 StrEnum types (Python 3.12 style)
│   ├── repositories/   — ABC interfaces (hexagonal ports)
│   ├── services/       — pure domain logic (Consent, DSR, Localization)
│   └── exceptions/     — typed error hierarchy
├── infrastructure/ — adapters: SQLAlchemy, Redis, Celery, rules engine, LLM, observability
│   ├── database/       — SQLAlchemy 2.0 async models + 8 repo implementations
│   ├── rules/          — deterministic rule engine with 5 rule sets (15 rules)
│   ├── llm/            — LangChain + Ollama explainer (assistive only)
│   ├── queue/          — Celery 5.3 with 5 named queues + beat schedule
│   ├── cache/          — Redis cache with namespace invalidation
│   ├── observability/  — 12 Prometheus metrics
│   └── security/       — PASETO handler + RBAC FastAPI deps
├── application/    — use cases + DTOs (orchestration only, no business logic)
│   ├── dto/            — Pydantic v2 request/response types
│   └── use_cases/      — 7 use-case classes (Activity, Auth, Consent, DSR, Processor, Incident, Analytics)
└── presentation/   — FastAPI routers, middleware, SSE
    ├── api/v1/         — 9 routers (health, auth, activities, consents, dsr, processors, incidents, analytics, audit)
    └── middleware/     — error handler, audit log, tenant extraction
```

---

## Auth

PASETO v4 (not JWT). Long story short: it's like JWT but cryptographically better, no alg confusion attacks.

```bash
# Get a token
curl -X POST http://localhost:8700/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email": "admin@example.com", "password": "changeme"}'

# Use it
curl http://localhost:8700/api/v1/activities \
  -H "Authorization: Bearer <token>" \
  -H "X-Tenant-Id: <your-tenant-uuid>"
```

### Roles

| Role                | Activities | Consents | DSR | Processors | Incidents | Analytics | Audit |
|---------------------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `admin`             | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `dpo`               | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| `compliance_officer`| ✅ | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ |
| `legal`             | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ |
| `viewer`            | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |

---

## Rule engine

15 deterministic rules across 5 domains. They return structured violations — no blocking side effects.

```
R-LB-001  Active activity must have at least one legal basis
R-LB-002  Consent-based processing must have a consent template
R-LB-003  Legal obligation basis must reference an article
R-LOC-001 Active activity must have a localization assessment
R-LOC-002 Primary DB location must be in Russia (RU-*)
R-LOC-003 Cross-border transfers require documented mechanism
R-LOC-004 Non-compliant localization must have an action plan
R-CON-001 Active consent must not be expired
R-CON-002 Consent template must be active to capture
R-PROC-001 Processor with PD must have a DPA
R-PROC-002 High-risk processors must have a signed questionnaire
R-PROC-003 Processors with subprocessors must document them
R-DSR-001 DSR must be resolved within SLA (30 days)
R-DSR-002 Completed DSR must have a response text
R-DSR-003 Rejected DSR must have a stated reason
```

---

## LLM integration

Ollama runs locally on port 11700. The `LLMExplainerService` generates:

- **Activity risk explanation** — plain-language risk summary for activities
- **DSR response draft** — suggested response text for common DSR types
- **Processor review summary** — consolidated vendor assessment narrative
- **Incident remediation plan** — step-by-step corrective actions

All prompts are loaded from `src/infrastructure/llm/prompts/`, SHA-256 hashed for auditability. LLM output is always advisory — never used as primary compliance evidence.

Default model: `llama3.1:8b` (change via `LLM_MODEL` in `.env`).

---

## Observability

- **Prometheus** → http://localhost:9700
- **Grafana** → http://localhost:3702 (auto-provisioned datasources + privacy dashboard)
- **Tempo** → traces via OTLP on port 4700
- **Loki** → structured JSON logs from all containers

Metrics exported at `http://localhost:8700/metrics`.

---

## Database

PostgreSQL 16 on port 5700. Automatic migrations via Alembic:

```bash
make migrate            # apply all pending migrations
make shell              # python -m alembic revision --autogenerate -m "your message"
```

Schema highlights:
- All PKs are UUID v4 generated by `pgcrypto`
- Multi-tenant isolation via `tenant_id` on every table with cascade deletes
- JSONB columns for flexible metadata and evidence payloads
- All timestamps with timezone

---

## Background jobs (Celery)

Worker queues:

| Queue        | Tasks                                      |
|--------------|--------------------------------------------|
| `activities` | Risk re-evaluation, rule engine runs       |
| `consents`   | Expiry scan (daily), bulk withdrawal       |
| `dsr`        | SLA deadline scan (every 30 min)           |
| `processors` | Review reminders, questionnaire dispatch   |
| `incidents`  | RKN notification dispatch                  |
| `analytics`  | Score recalculation (every 15 min)         |

Flower monitoring → http://localhost:5701

---

## Running tests locally (without Docker)

```bash
pip install -e ".[dev]"
pytest tests/unit -v                    # pure unit tests, no infra needed
pytest tests/integration -v             # needs running app (or just httpx mocks)
pytest --cov=src --cov-report=term-missing
```

---

## Environment variables

Copy `.env.example` to `.env` and tweak what you need:

```bash
cp .env.example .env
```

Key variables:

```
SECRET_KEY          — PASETO symmetric key (min 32 bytes, generate with: openssl rand -hex 32)
DATABASE_URL        — async postgres URL
REDIS_URL           — Redis connection string
LLM_MODEL           — Ollama model name
OTLP_ENDPOINT       — leave empty to disable traces
DEBUG               — set to false in production
```

---

## Development workflow

```bash
# lint + type check
make lint

# add a new migration after model changes
docker compose exec api alembic revision --autogenerate -m "add_field_X"

# rebuild the image after dependency changes
docker compose build api

# tail all logs
docker compose logs -f api worker
```

---

## What 152-FZ requires (quick cheat sheet)

| Requirement | Where implemented |
|---|---|
| Art. 18(1) — maintain register of processing activities | `data_processing_activities` + `legal_basis_records` |
| Art. 18(5) — localization of PD in Russia | `localization_assessments` + R-LOC rules |
| Art. 7 — consent must be informed, specific, freely given | `consent_templates` + `consent_captures` |
| Art. 14-17 — respond to DSR within 30 days | `data_subject_requests` + SLA tracking |
| Art. 22 — notify Roskomnadzor of processing | operator registration metadata |
| Art. 22.1 — appoint DPO | `users` with `dpo` role |
| Art. 19 — take security measures, document incidents | `privacy_incidents` + evidence |
| Art. 6 — legal basis for every processing activity | `legal_basis_records` + R-LB rules |

---

## License

MIT. Use it, fork it, file issues.
