# algorithmic-mta-framework

A production-grade Multi-Touch Attribution (MTA) framework designed to optimize ad spend. This project leverages dbt and DuckDB to compare heuristic and Markov Chain models, eliminating waste in fragmented digital marketing channels.

## Project Scaffold

The repository is structured to support end-to-end analytics engineering and ML delivery:

- `.devcontainer/`: reproducible development environment.
- `airflow/`: orchestration DAGs and scheduling logic.
- `ingestion/airbyte/`: source connector and sync strategy docs.
- `data/bronze|silver|gold/`: medallion-style data lake layers.
- `dbt/`: transformation project (staging, intermediate, marts, tests).
- `quality/great_expectations/`: data contract and quality checks.
- `observability/monte_carlo/`: observability monitors and incident definitions.
- `ml/`: training code, model artifacts, and notebooks.
- `dashboards/metabase/`: executive BI assets.
- `dashboards/streamlit/`: what-if simulator app.
- `scripts/`: bootstrap and operational scripts.
- `tests/`: unit and integration test suites.
- `doc/`: planning and execution documentation.

## Documentation

### Phase Planning & Strategy
- Implementation Plan: [doc/implementation-plan.md](doc/implementation-plan.md) — 8-phase execution roadmap with batch-level detail
- Execution-Ready Master Backlog: [doc/execution-ready-master-backlog.md](doc/execution-ready-master-backlog.md) — 40 stories, 273 points, 10 sprints with role ownership

### Phase 0 Batch Artifacts
- **Batch 0.1 (Architecture and Standards Baseline)**
	- Architecture and Domains: [doc/phase-0/batch-0-1-architecture-standards.md](doc/phase-0/batch-0-1-architecture-standards.md)
	- Standards Catalog: [doc/phase-0/standards-catalog.md](doc/phase-0/standards-catalog.md)
	- SLA/SLO Matrix: [doc/phase-0/sla-slo-matrix.md](doc/phase-0/sla-slo-matrix.md)
	- Batch Report: [doc/batches/phase-0-batch-0-1-report.md](doc/batches/phase-0-batch-0-1-report.md)
	- Command Log: [doc/batches/phase-0-batch-0-1-commands.md](doc/batches/phase-0-batch-0-1-commands.md)

- **Batch 0.2 (Environment Reproducibility)**
	- Environment Reproducibility Baseline: [doc/phase-0/batch-0-2-environment-reproducibility.md](doc/phase-0/batch-0-2-environment-reproducibility.md)
	- Cold-Start Validation Evidence: [doc/phase-0/batch-0-2-cold-start-validation.md](doc/phase-0/batch-0-2-cold-start-validation.md)
	- Batch Report: [doc/batches/phase-0-batch-0-2-report.md](doc/batches/phase-0-batch-0-2-report.md)
	- Command Log: [doc/batches/phase-0-batch-0-2-commands.md](doc/batches/phase-0-batch-0-2-commands.md)

- **Batch 0.3 (Security and Compliance Baseline)**
	- Security and Compliance Baseline: [doc/phase-0/batch-0-3-security-compliance.md](doc/phase-0/batch-0-3-security-compliance.md)
	- Secrets and Rotation Policy: [doc/phase-0/secrets-key-rotation.md](doc/phase-0/secrets-key-rotation.md)
	- PII Classification and Masking Policy: [doc/phase-0/pii-classification-masking.md](doc/phase-0/pii-classification-masking.md)
	- Access Control Matrix: [doc/phase-0/access-control-matrix.md](doc/phase-0/access-control-matrix.md)
	- Security Validation Evidence: [doc/phase-0/batch-0-3-security-validation.md](doc/phase-0/batch-0-3-security-validation.md)
	- Batch Report: [doc/batches/phase-0-batch-0-3-report.md](doc/batches/phase-0-batch-0-3-report.md)
	- Command Log: [doc/batches/phase-0-batch-0-3-commands.md](doc/batches/phase-0-batch-0-3-commands.md)

- **Batch 0.5 (Phase 0 Closure Gate Check)**
	- Gate Check Report: [doc/phase-0/phase-0-gate-check-report.md](doc/phase-0/phase-0-gate-check-report.md)
	- Closure Batch Report: [doc/batches/phase-0-batch-0-5-closure-report.md](doc/batches/phase-0-batch-0-5-closure-report.md)
	- Closure Command Log: [doc/batches/phase-0-batch-0-5-commands.md](doc/batches/phase-0-batch-0-5-commands.md)

- **Batch 0.4 (Jira Import & Operationalization)**
  - Completion Report: [doc/batches/phase-0-batch-0-4-jira-import.md](doc/batches/phase-0-batch-0-4-jira-import.md) — What was built, why decisions, issues resolved, acceptance criteria (1400+ lines)
  - Command Log: [doc/batches/phase-0-batch-0-4-commands.md](doc/batches/phase-0-batch-0-4-commands.md) — 30+ commands with expected outputs, troubleshooting guide (500+ lines)
  - Jira Import CSV: [doc/backlog/mta-framework-jira-import.csv](doc/backlog/mta-framework-jira-import.csv) — Ready-to-import (40 stories, 273 points, 10 sprints)
  - CSV Generator Script: [scripts/generate_jira_csv.py](scripts/generate_jira_csv.py) — Reusable markdown→Jira CSV automation with validation

## Quick Start

1. Install dependencies:

	```bash
	pip install -r requirements.txt
	```

2. Bootstrap local folders:

	```bash
	bash scripts/bootstrap.sh
	```

3. Start containers (optional local stack):

	```bash
	docker compose up -d
	```
